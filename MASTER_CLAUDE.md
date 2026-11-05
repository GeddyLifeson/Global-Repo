# MASTER CLAUDE.md (single source for every repo and session)

Location: /mnt/project-files/CLAUDE.md. Each repo's CLAUDE.md points here. Rules cite their source in [brackets]: memory file names are in team memory (silo), dates are Marlon's messages. When two rules conflict the newest wins; resolved conflicts are listed in section 8.

Every repo's CLAUDE.md is a short pointer to this file plus repo-specific notes. Change shared rules HERE, not in the repos.
If you cannot read /mnt/project-files, the "Essentials" block below is enough to start.

## Essentials (copied into each repo file)
1. Order of work (minimise session tokens, section 0): existing scripts and tools first, then ModelRouter and free lanes, then the Claude API (job folder, Haiku Batch, caching), then Claude sessions only for planning, judgment and review.
2. Claude API key: read it from `/mnt/project-files/compute/secrets/anthropic_key` into `ANTHROPIC_API_KEY` (cloud). On the PC the key is the file `C:\Users\imarl\.claude\anthropic_key` and the `ANTHROPIC_API_KEY` environment variable; use whichever is set (Marlon allowed this on 2026-11-01 so every session can use the API; expires about 11-26). Never print it, commit it, paste it into CLAUDE.md, a PR, a job file or memory, or copy it anywhere else. Never put any other token or Marlon's email in a file, commit or request.
3. Anything needing Marlon is one desktop-shortcut double-click. Do not ask him to refresh tokens or paste things.
4. Find the latest 26.1 mod build; else port an older one (licence allowing); else build our own (clean-room for ARR). Duplicates merge into one thing with id migration.
5. No invented entries. Panscriptum assays come from real page text only. Everything in the Panscriptum must be in the modpack and vice versa.
6. Tests run in the real world at spawn, not backrooms or void, and test only the thing asked.
7. Commit and push after every working change. No GitHub Actions. No CurseForge or Modrinth publishing. Local models on the PC and laptop are allowed (Marlon 11-02 22:40): hidden windows only (start through `E:\\launch_hidden.ps1`), laptop RAM is tight.
8. One job per thread (Marlon 11-01 19:01). Never pile side tasks onto a busy thread, least of all the PC game-test thread, which does only game tests. A new task gets its own new thread; a thread that finds extra work asks the coordinator for one via message_coordinator.
9. Context handoff (Marlon 11-04): at 125k used tokens (25% of 500k) write plans/handoffs/<thread-title>.md and message the coordinator "handoff ready: <path>"; the driver thread enforces it. Full rule below.

## 0. Spend as few Claude session tokens as possible (top rule, Marlon 11-01)
Session tokens are the scarcest resource. Push every piece of work as far down this ladder as it will go, and stop at the first rung that can do it:
1. An existing script or tool (section 3). Look there first; never rewrite what exists. The master module list is the "Code modules (master module list)" section (line 314) of `C:\\Users\\imarl\\.claude\\capabilities\\INDEX.md`, with its companion `C:\\Users\\imarl\\code_commons\\CATALOG.md`. Cloud copies dated 11-01: `/mnt/project-files/pc_capabilities_INDEX.md` and `/mnt/project-files/pc_code_commons_CATALOG.md`; regenerate on the PC with `python ~/.claude/capabilities/build.py`. Look there first for any tool.
2. A new script, if the work repeats. Scripting anything repetitive is the default, then run it.
3. Free lanes through ModelRouter (section 2). Text jobs a local model can do (names, translation, compile-error triage, lore and quest drafts) go to `compute/jobs-local/<name>/` (format and rules in `compute/jobs-local/README.md`); everything else goes to rung 4.
4. A Claude API job: Haiku first, Batch, prompt caching (section 1), via a job folder.
5. Session reasoning, only for planning, judgment, review and integration, then push.

No budget cap on the API (Marlon 11-03 21:45): the watcher runs ~96 concurrent calls and the queue must never sit empty. Submit every bulk text, extraction, catalogue, check or judging task as a compute/jobs job right away (compute/LANES.md, "NO CAP, KEEP THE QUEUE FULL").
Also: replies short and results only; read only what is needed (search, then read by range, never whole large files); never narrate, recap or re-derive; send log reading, test runs and doc fetching to a script or cheap model; one commit and push per working change. If the API or a free lane would cost more than doing a tiny job yourself, do it yourself.

## 1. Claude API practices (all lanes)
Where it runs: bulk text work is a job folder `/mnt/project-files/compute/jobs/<name>/` holding `in.jsonl` (`{id,prompt[,system][,images]}`) and a README. The watcher (compute-lanes thread, `tools/compute/api_lane/` in DiaithirRPG) claims it within ~1 minute and writes `out.jsonl` (`{id,text,lane}`) beside it. Owners validate and merge; failed rows go in `<name>-retry`. Lane map: `/mnt/project-files/compute/LANES.md`. Spend log: `/mnt/project-files/compute/ledger.csv` (`ts,job,model,input,output,cache_write,cache_read`).

Job README keys the watcher reads: `max_tokens N` (required), `model: haiku|sonnet|opus` (default haiku), `effort: low|medium|high|max`, the word `sync` (force direct calls). A `schema.json` beside `in.jsonl` turns on structured outputs.

Features in use, with why:
- **Batch API** (50% off, up to 100k requests per batch; we chunk at 1,500). Every bulk job. Sonnet/Opus jobs of 40+ rows also go Batch unless README says `sync`. Do not use `stream`, `speed` (fast mode) or `max_tokens: 0` in a batch.
- **Prompt caching, 1-hour TTL.** Put everything shared FIRST (instructions, rules, few-shot, source text), then the per-row part. The runner puts `cache_control` on the common prompt prefix when it is over ~2,400 characters (minimum cacheable is 512 tokens on the 5.5 models) and on any `system` over that size. Batch hits are best effort, so keep the 1h TTL. Changing `output_config.format` invalidates the cache. Check `usage.cache_read_input_tokens`: the ledger's last column should be large on every row but the first.
- **Model choice.** Batch prices per MTok in/out: Haiku 5.5 $0.05/$0.25 (default, classify, extract, rewrite, pick); Sonnet 5.5 $1/$5 (judgment, adjudication, fact checks); Opus 5.5 $2/$10 (hardest only); Fable 5.1 $5/$25 (almost never). Haiku 5.5 input costs 5x more above 100k tokens per prompt, so keep prompts small.
- **Thinking.** Off for Haiku (`disabled`), `between_tools` for Sonnet/Opus, or max_tokens is eaten and text comes back empty. Use `effort` instead to tune depth: `low` for simple extraction and picks.
- **Structured outputs** (`output_config.format` json_schema) for any job whose output is JSON (capitals lat/lon, photo picks, validators). Guarantees valid JSON and removes retry rows. Not compatible with citations or prefill.
- **Files API** for images: each image is uploaded once and referenced by `file_id` (map in `/tmp/claude-0/run/files.json`), instead of base64 per row. Shrinks batch payloads and re-uses uploads across the pick and review passes.
- **Token counting** (free `count_tokens`, text only; file sources are rejected) runs at claim time and writes `<job>/.estimate` with a ceiling cost, so large jobs are visible before spend.
- **Not used, on purpose:** citations (conflicts with schemas; assay text is grounded by giving real page text in the prompt), context editing and compaction, memory tool, tool use and agents, fast mode, task budgets, streaming. Our calls are single-turn and stateless. Revisit if a job becomes multi-turn.
- If the API would cost more than doing the work in a session, do it in the session. Never pad or invent rows to use credits.

After a container restart the watcher and runners die but submitted batches keep going on Anthropic's side: export the key from the secrets file (`export ANTHROPIC_API_KEY=$(cat /mnt/project-files/compute/secrets/anthropic_key)`), run `recover.py`, relaunch `watch.py` under `nohup bash -c 'while true; do python3 -I watch.py; sleep 5; done'`. The file is on a network mount, so chmod 600 is not enforced there; treat the whole `compute/secrets/` folder as private and never move it into a repo.

## 2. ModelRouter and free lanes
ModelRouter (desktop `C:\Users\imarl\modelrouter`, Ollama API on `:11435`) is the single entry for free capacity (Groq, Gemini, Cerebras and others held under free limits, keyless hosts, desktop GPU Ollama). Scripts call models only through `tools/compute/llm.py` `ask(...)`. A new free source becomes a backend inside ModelRouter, not a new script. Details: `tools/compute/README.md` in DiaithirRPG and `/mnt/project-files/compute/FREE_HOSTS.md`. As of 10-27 it returned 502 (only the ModelRouter RC session edits its config); until it works use the keyless lanes (OVH, Kilo) and then the Claude API job folder. Ollama fallback must stay off.

## 3. Scripts and tools (where things live)
- DiaithirRPG `tools/`: `compute/` (router, run.py, llm.py, `api_lane/` Claude API watcher/batch/sync/recover), `offload/` (PC job queue), `age1/`, `names/` (130-culture name pipeline: `content/names/extra/*.tsv`, `build.py`, `export_drop.py`), `culture_start/`, `kaggle`, `modal`, `needs_marlon.py`.
- diaithir-ports: NeoForge 26.1.2 mod ports and own mods (`diaithir-*` folders), packwiz pack; build with `build_pack.py` and a clean-install test before any publish.
- Machines: PC `Fountain-of-Lateralus-Rex` (user folder `C:\Users\imarl`, server `C:\DiaithirServer`, Prism instance "Diaithir" in `C:\Prism`); MSI laptop (~2.5 GB free RAM, no game clients, Kaggle loop).
- Cloud compile of NeoForge 26.1.2 (~2.5 min): `source /mnt/project-files/tools/get_jdk25.sh` (JDK 25 from api.adoptium.net), then `./gradlew compileJava --no-daemon -q -I /mnt/project-files/compute/gradle_mirror_init.gradle -Dorg.gradle.java.installations.paths=$JAVA_HOME`. The `-I` file is a Google Maven Central mirror that avoids the 429 rate limit. Auto-fix loop: `tools/compile_fix_loop.py`. Recipe also in `compute/LANES.md`.
- Norton deletes `.bat` files; use one desktop shortcut for anything Marlon must run.
- **Global script catalogue (Marlon 11-02): `https://github.com/GeddyLifeson/Global-Repo`, index `SCRIPTS_INDEX.md`, IDs in `ids.tsv`.** Before writing a script, search the index and borrow by ID. Every new script (cloud, PC, laptop, any repo) must be registered: take the next free ID, put `# Sxxxx <what it does>` as its header comment, add its row to `<device>_inventory.tsv` and run `build_index.py`, then commit and push the repo. IDs never change. No secrets in the repo (it is public).
- **Everything gets an ID (Marlon 11-02).** Global-Repo also catalogues docs (D), data files (F), modules/jars (M), art sets (A), compute jobs (J), threads (T) and PRs/branches (P), each with a stable ID (`CATALOGUE.md`). Claim IDs only with `python3 -I /path/to/Global-Repo/claim_id.py <PREFIX> [n] [note]` (atomic via the shared counter in compute/id_counters, works from any thread; never pick one by hand; add the row to Global-Repo by PR or message the catalogue thread), and run `crawl_all.py` after adding files so the catalogue stays current. Paths and metadata only, never secrets or private data.

## 4. Master module list (what is in the pack)
- `/mnt/project-files/mod-categories/*.json` (14 categories: adventure, cursed, decoration, economy, equipment, food, game-mechanics, magic, management, minigame, mobs, optimization, social and more) with `BATCH1_REPORT.md`.
- `/mnt/project-files/game-plan/minecraft/modlist-2026-10-13` (older full mod list) and `/mnt/project-files/mod-ports/` (port status).
- The live pack is the packwiz index in diaithir-ports; branch `claude/pack-latest` is the newest full test pack.
- Rule: every mod in the Panscriptum is in the pack and every pack mod is in the Panscriptum. Optional systems reach players as quests (Codex Quests tab), never as on/off switches.
- **Panscriptum master sheet** (S6964, S6966): `plans/PANSCRIPTUM_MASTER.tsv`, one row per being with source wiki and lead index, powers, pack entity and card shard. Use it to find a known character's copy; how-to in `plans/PANSCRIPTUM_MASTER_README.md`.

## 4a. Pack (build, test, branches, release)
Written 11-01 from the pack-v1-2 and pack-latest sessions. Repos: `diaithir-ports` (the packwiz pack Marlon's players install, plus our own mod source) and `DiaithirRPG` (the inputs under `distribution/` and `content/`). The ports tree is OUTPUT; edit the inputs in DiaithirRPG and rebuild.

**Inputs (DiaithirRPG `distribution/`)**
- `pack.json`: `name, author, version, minecraft, neoforge, ram_mb, min_ram_mb, jvm_args, pack_url` (raw.githubusercontent URL of the branch's `pack.toml`), plus maps `drop` (jar name -> reason it is removed), `add` (jar name -> `{sha256, side}` for jars not in sources.json, normally ours in `ports/`), `rebuilt` (jar name -> sha256 of our rebuild when it differs from the manifest hash, e.g. diaithir-compat) and `server_only` (jars the client must not get). Every drop needs a reason string; MOD_REMOVALS (`content/dedupe/MOD_REMOVALS.json`) must all appear in `drop`.
- `sources.json`: third-party jar name -> `{url, sha256, side[, modrinth, curseforge]}`. Third-party mods are never rehosted: each becomes a `.pw.toml` pointing at the author's CDN file.
- `server_manifest.csv`: `path,size,sha256,mod_id,mod_version,ours` for every jar and server file; keep it in step with `ports/`.
- `ports/`: our own jars and ports (diaithir-*, patched builds). Client-only ports are hosted under `client/` and linked by a `.pw.toml`; `client_files/` are client-only resource packs; `overrides/` is everything copied into the game folder (config, kubejs, defaultconfigs); `tech_data/` is the default tech JSON for the engine.
- LICENSES.md (ports repo): one row per jar we host; add the row when you add a jar. A jar whose licence does not allow redistribution goes in `drop` or is built clean-room.

**Build.** `python3 tools/distribution/build_pack.py OUT_DIR BOOTSTRAP_JAR [--server SERVER_ROOT] [--tech-src DIR]` writes `.pw.toml` links, copies ports and overrides, runs `packwiz refresh --build` (binary `/root/go/bin/packwiz` in the cloud) and writes `Diaithir.zip` (Prism instance that runs the installer before each launch). `--server` (PC only) adds the live server's kubejs/config; `--tech-src` overrides `tech_data`. Build into a throwaway dir and copy only what changed into the ports branch; a blind copy re-adds files other lines removed (loot tables for dropped mods) and deletes `keybinds.txt`/`options.txt`. For a one-file change you can edit the file, then recompute its `index.toml` hash and `pack.toml`'s index hash.
- The bootstrap jar is inside `Diaithir.zip` (`Diaithir/.minecraft/packwiz-installer-bootstrap.jar`); the cloud host blocks api.github.com, so pass `/tmp/pw/packwiz-installer.jar` as the installer to skip self-update.
- `options.txt` and `keybinds.txt` ship as overrides (a blind build copy deletes them from the ports branch, so keep them). Whether the installer leaves a player's edited copy alone is not verified here; check before changing how they ship. Config that fixes crashes lives in overrides too (Lithium `lithium.properties` was a pack-v1 workaround for the PoiManager crash; pack-v1-2 has the ships jar diaithir.2 instead and no workaround).

**KubeJS layout and KubeJS 8 / MC 26.1 gotchas.** `kubejs/startup_scripts`, `server_scripts` (per topic folder: `diaithir/`, `economy/`, `culture_start/`...), `client_scripts`, `assets`, `data/<ns>/...` (JSON read with `JsonIO.read('kubejs/data/...')`). Rhino here rejects array spread (`[...set]` is a syntax error that kills the whole script file), so use `forEach`/loops; no jar needed for scripts; use `Java.loadClass`; wrap JSON reads in try/catch; a bad handler can kick players, so boot-test every script. Server log line `Loaded N/N KubeJS server scripts ... with 0 errors` is the check; the two startup plugin errors (Architectury, JAOPCA) are known and old.

**Branch lines (both repos)**: `claude/pack-v1` live; `pack-v1-1` and `pack-v1-2` are the next candidates (v1-2 = ships jar diaithir.2); `claude/pack-latest` newest full test pack (food-6 head plus later work); `pack-food-N` older test lines; `claude/pc-updater` holds the updater script. TEST-ONLY URL rule: a test branch's `pack_url` and its client-only `.pw.toml` links point at its own branch (e.g. `claude/pack-latest`) so the installer can fetch it; those URLs are test-only and must be reverted to the live branch's URLs when the contents are promoted. Never push to pack-v1 or other lines you were not asked to touch.

**Test steps before anything is called ready**
1. `tools/distribution/clean_install_test.py PACK_TOML_URL BOOTSTRAP_JAR WORK_DIR [INSTALLER_JAR]`: clean client and server install, every jar hash against manifest and pack.json, every override file, client dependencies. Assert exactly ONE `diaithir-ages-*.jar` per side.
2. Server boot (NeoForge 26.1.2.116, Java 25, `online-mode=false`, GriefLogger removed for the boot only): need `Done`, `Loaded N/N KubeJS server scripts ... 0 errors`, no new ERROR lines compared with the line you started from.
3. Real client join at spawn (not backrooms/void) when a client can run; otherwise say plainly "no client join". Heap in tests: server 3.8G, client 3.5G (players get ram_mb 12288 from pack.json).
4. Disk hygiene: the cloud box has about 2-3 GB free; a server install is ~1.6 GB and a client install ~1.5 GB. Run them one after the other, delete each work dir when done, use sparse worktrees (`git sparse-checkout`) instead of full checkouts of DiaithirRPG (1.7 GB), never delete directories you did not create, and never `git worktree remove` before copying out build products.

**Where it runs.** Server `C:\DiaithirServer`; Prism instance "Diaithir" in `C:\Prism`. PC updater: Marlon double-clicks "Update Diaithir" (`/mnt/project-files/pc-update/`; it runs `update-diaithir.ps1` from branch `claude/pc-updater` of diaithir-ports; pack address in `pack_url.txt` there; log on the Desktop; close Prism first if possible). Do not ask him for anything more.

**Release and merge flow.** Sessions push test branches normally (no force). Marlon merges with his Desktop shortcut. No GitHub Actions, no CurseForge/Modrinth publishing; players get the pack from the raw GitHub URL via the Prism import of `Diaithir.zip`. Never put Marlon's email, keys or tokens in requests, files or commits. Commit messages end with the attribution lines the session gives.

## 4b. Units of measure (Marlon 11-02, standard in plans/UNITS.md)
Real SI units only, few as possible. Energy J (1 FE = 1 J), power W (1 FE/t = 20 W), fluid L (1 mB = 1 L, bucket = 1000 L = 1 m3), temperature K shown as C, pressure bar, torque N.m (Create SU), rotation rpm, mass kg, length m, time s (20 ticks), currency g of silver. Magic folds into energy: 100 J per mana/aura/ember/LP/vis, Source 1000 J. Player text never shows FE, RF, EU, mB, AE, mana, SU or ticks. Third-party stores are wrapped with `diaithir-units` (`Units`, `Fmt`, `shim.ScaledEnergy`, diaithir-ports); a new unit needs a reason in UNITS.md.

## 5. Plans and maps
- Map of everything: `/mnt/project-files/INDEX.md`. Plan to v1: `/mnt/project-files/plans/PLAN_TO_V1.md`. Status: `plans/V1_STATUS.md`, `V1_TEST_CHECKLIST.md`.
- Bible: `/mnt/project-files/game-plan/bible/BIBLE.md`. World scale 1:5. Ages are the civ tech tree on one shared calendar year.
- Naming: English is the main display name; the grey italic line is the starting culture's native name; every Diaithiris-named thing gets a name in all 130 culture languages. Diaithiris is the ancient ancestor of Goidelic: no word may equal modern Gaelic, Irish or Manx. Every name in a language is built the way an expert linguist of that language would build it, from real research: its word formation, morphology, compounding, phonotactics, orthography, and attested roots and grammar; ancient and reconstructed languages follow scholarly reconstruction conventions. Each language keeps a cited rules file next to its names, and names that fail the rules are regenerated. [Marlon 11-02]
- Look and lore: Industrial Factory textures at 64 px, Factorio look for tech, magic is Celtic. Ids never change. Only show finished things.

- One job per thread. A side task never goes onto a running thread; it gets a new thread via the coordinator. Threads already running several jobs finish the current one and hand the rest to new threads.
- **Integration (Marlon 11-02 22:54, 22:56).** Every merged, ported or clean-room module is as integrated with the rest of the pack as possible: shared `c:` tags and ores, cross-mod recipes, energy/fluid/item capabilities in SI units, upgrade rule on every working block, Global Events hooks, Codex entry, quest link and Age gate. Spec and definition of done: `plans/INTEGRATION.md`. A module is not done until its compat-matrix row is green. **PR review check (Marlon 11-03 22:15): every thing integrates with every other system in some way.** Every PR description must have an "Integration" line naming the cross-system hooks (shared `c:` tags and ores, recipes using other modules' items, SI-unit capabilities, upgrade slots, Global Events, Codex entry, quest link, Age gate, names, animation, economy/wages, Panscriptum entry) or justifying each gap. The driver does not call a PR ready without it.

## 6. Working rules
- Live server restarts are OK. Every pack publish needs a clean install plus a client world-join test.
- Pause PC work while Marlon plays. Only kill PIDs you launched.
- Give status without being asked; Marlon is impatient. Keep replies short and report results only.

## 7. Standing rules pulled from everywhere (with sources)
Process and people
- Never ask Marlon to type approvals or paste tokens; at most one Allow tap or one desktop shortcut. Route anything the auto-mode guard refuses (free-host text, restarts, committing router config) to cloud lanes. [desktop-guard-blocks, 10-20]
- Read a stalled desktop session's `logs/*.md` and `NEEDS_MARLON.md` in DiaithirRPG before re-briefing it. Add Marlon steps only with `python tools/needs_marlon.py add <id> "<step>" --check "<cmd>"`; never hand-edit. [needs-marlon-list]
- Device threads never end a turn mid-job: poll in the foreground until done; coordinator sets about 30-minute check-ins. Never blame PC sleep without evidence. [device-thread-idle-drop, 10-26]
- Do not spin up mass lane threads from a coordinator post (the cloud check refuses them). Add throughput to existing lanes instead. [new-lane-threads-blocked, 10-21]
- Everything project-related is mirrored so GitHub, cloud, MSI laptop and desktop can each take over; secrets sync device to device only, never GitHub or cloud. [failsafe-sync, 10-19]
- Keep INDEX.md current when adding repos or folders. [project-consolidation]
- Prefer free capacity over paid; AWS/Lightning/Colab/HF free-GPU idea was DROPPED. [free-gpu-services, 10-19]
- The $200/month Claude API credit (cap $150/month for the rewrite lane) and the user key expiring about 11-26 are why the ledger exists; never store the key. [claude-rewrite-lane, api-does-bulk-work]

Shardfall (design and game)
- The master plan doc beats any other file (including shardfall-assets.xlsx) on conflict. [master-plan-wins, 10-03]
- Every thread checks finished work against the Bible: `python3 game-plan/bible/check.py <changed files>`, and `check.py --data` after data, campaign or writing changes; new canon goes in the Bible plus rules/numbers/terms CSVs. [shardfall-bible]
- `design/world/locations.csv` is frozen; changes go to `data-requests.csv`. [world-locations-frozen]

Diaithir (pack, world, art)
- Atlas (Diathiris repo) covers only what happens on Diaithir itself; dimensions, other worlds, the Pale, the Sift, space and omniverse go in the Panscriptum. [atlas-scope, 10-22]
- Gating is per item and per entry, never per whole mod or source; Age rules in DiaithirRPG `docs/design/tech-by-age.md`. [tech-by-age, 10-18]
- We ship our own packwiz pack and Prism import from public diaithir-ports; third-party mods are never rehosted (each .pw.toml points at the original CDN file); Almost Unified fork, Twilight Forest port and stock Iris are out. [own-distribution, 10-20]
- Textures: our own Industrial Factory pack, Factorio style, 64 px, drawn fresh per texture, metal must shine; PureBD is dropped and deleted. [texture-pack, factorio-tech-look, 10-22/24]
- Creatures: the approved 64x method (parse boxes, Blender AO bake, paint fresh per face, real eyes) is the standard for every mob. [creature-art-standard, 10-22]
- Capital and spawn: Creag Ruadh x -251201 y 207 z -1541408 (Mercator scale 5). [capital-spawn-creag-ruadh]
- KubeJS on 26.1 has traps (player kicks, dead handlers); boot-test scripts. [kubejs-26-gotchas]

Panscriptum kit and library (from the panscriptum and panscriptum-library-kit CLAUDE.md files)
- NO CAPS, EVER: every IP and reference is uncapped; no limit, sample, top-N or truncated roster. Rank first, never rank then truncate. [panscriptum CLAUDE.md, Hard Rule 0, 2026-08-22]
- Escalation chain Janitor, Operator, Supervisor, Safety, Manager, Owner: you may raise a halt, you may not lift one you merely found; a halt you caused you may clear only with a written ruling and a same-turn report. Every safety must be independent, fail closed and proven by `python src/drill.py`. [panscriptum CLAUDE.md, Hard Rule -1, 2026-08-25]
- Do not invent facts, spine codes, Assay decimals or Shelfmarks; Threads stay pending until the entanglement pass; pilot before scaling; report progress. [panscriptum Hard rules 1-7]
- The charter's Acquisitions Index is the addressing system; extend it only with owner sign-off or provisional `UNSORTED...PROVISIONAL` codes. [panscriptum Hard rule 2]
- On the MSI laptop use miniconda python; Norton breaks pip TLS and blocks DuckDB; evaluated and declined tools are listed in that file (LiteLLM, Scrapy, Prefect and others) so do not re-run the survey. [panscriptum CLAUDE.md]
- Assay: fresh rock-to-omniversal anchored relative ranking, presented like "The Wheel of Faith". [assay-relative-ranking, assay-presentation-wof]

Diaithir novels and Legendarium (from the diaithir-laptop CLAUDE.md, a separate series)
- Never rewrite a whole book; fix flagged lines. Scripts check, models judge, canon lives in tables (`canon/`), one keeper writes proposals to `canon/proposed.jsonl`, Marlon rules. The 25 decisions are all RULED; `canon/rules.md` there wins. House style (Gaelic spelling policy, song-title epigraphs) is deliberate. [diaithir-laptop CLAUDE.md]

## 8. Conflicts resolved (newest wins)
- panscriptum, panscriptum-library-kit and diaithir-laptop CLAUDE.md tell sessions to use the local Ollama model. SUPERSEDED by the 10-21 ban on local models on the PC and laptop; bulk goes to ModelRouter, free lanes, then the Claude API. Treat every "local Ollama" line in those files as historical. [no-local-models, 10-21 21:16] UPDATE 11-02 22:40: Marlon allowed local models again on the PC and laptop, hidden windows only, so those local-Ollama lines stand again, within that limit. Cloud sessions still cannot reach a local model.
- DiaithirRPG free-compute skill said "never use Claude for bulk". SUPERSEDED 10-27 18:28-18:58 by routing order ModelRouter and free lanes, then Claude API Batch, then Claude sessions. Skill updated.
- Earlier "Claude workers write a quarter of rewrites" lane (10-22) is folded into the general API job-folder lane. [claude-rewrite-lane]
- panscriptum-library-kit CLAUDE.md is an older copy of panscriptum's CLAUDE.md (it lacks Hard Rules -1 and 0). The panscriptum repo version governs.

## 9. Pulled in from the PC (11-01; originals in claude-md-intake/pc/)
Sources: PC global `~/.claude/CLAUDE.md` [pc-global] and `Diaithir_work\Diaithir\CLAUDE.md` [diaithir-novels]. These apply when the session runs on the PC or touches those projects.

**PC global (every session on the PC)**
- Done means proven: show the command, its output and exit code before saying it works. Any nonzero exit or stall: diagnose before the next step; after two failed fixes, stop and change approach. [pc-global]
- Commands run non-interactively with a timeout. Anything over ~30 s runs in the background with a log checked within 60 s; no foreground sleeps over 30 s. Reply to Marlon first, then keep working. [pc-global, 10-10]
- Any background job over 10 min gets a stall watchdog started in the same turn: `python ~/.claude/scripts/watchdog.py --watch <dirs> --stall <3x normal min> --match <cmd text> --kill <worker text>`. On STALL run `hogs.py`, diagnose, restart, re-arm. Kill only PIDs `hogs.py` names. One GPU job at a time. [pc-global]
- Before using any tool, app, model or service for real work, check its options (`--help`, docs) and set the fastest/best ones (GPU encode, parallel limits, quality presets, batch modes); state them before the first run. [pc-global, 10-10]
- Before sending any render or cut, check the whole output (frames at least every 0.5 s, edited windows, measured audio), fix every problem in one batch, re-check, then send. [pc-global, 10-10]
- Confirm a package is real (age, downloads, source) before installing it. Smallest change that satisfies the request; state assumptions. New behaviour gets a test that fails first; never weaken tests. Turn repeated failures into a rule, test or script. [pc-global]
- Token habits: search before reading, read big files by range, pipe noisy output through grep/head/tail, `git diff --stat` first, send log reading and doc fetching to a cheap subagent. [pc-global]
- Big installs, models and outputs go on E:, never C:. After any AppData cleanup prove `python` and `uv` still run. Never move or delete Norton's sandbox folder. [pc-global, 10-07]
- Media: Craft Apps CLIs first (FilmCraft video, EffectCraft motion, PhotoCraft images, SoundCraft audio, VectorCraft, LightCraft, DesignCraft, DeckCraft, WordCraft, GridCraft, PdfCraft, CADCraft; installed in `C:\Program Files\<Name>Craft\`, each has `<name>craft-cli.exe` with an `mcp` subcommand), Blender 5.2 as fallback, `local-3d` skill (Hunyuan3D on E:) for 3D. Dropped, never suggest: ComfyUI, DaVinci Resolve, Easy Diffusion. [pc-global]
- Where things live: skills `~/.claude/skills/`, 95 more behind the hub skills in `~/.claude/skill-library/`, reusable code `C:\Users\imarl\code_commons` (catalog `CATALOG.md`; reuse before writing new), tool index `~/.claude/capabilities/INDEX.md`. UI work: read `vibecode-scan` first and run it before delivering. antislop applies to code and UI edits. [pc-global]

**Diaithir novels project (`Diaithir_work\Diaithir`; not the game or modpack)**
- 19 novels across seven Ages plus Companions, Legendarium, Plans v3 and Atlas. Reconcile cheaply: scripts check, models judge, never rewrite a whole book, fix flagged lines only. [diaithir-novels]
- Canon lives in tables (`canon/*.csv`, `rules.md`); the table wins over prose. New facts go to `canon/proposed.jsonl`; nothing enters canon without Marlon's approval. Marlon's rulings are final; `canon/rules.md` records all 25 as RULED (10-01) and wins over the brief. [diaithir-novels]
- Canon precedence: Marlon's ruling, then Plans' cast/roll tables, then the narrated scene, then Companion "Settled" notes, then Legendarium narrative, then annals (copies of one file count once). [diaithir-novels]
- Era conversions: VE n = LC n; GE n = LC 5,323+n; FE n = LC 9,925+n; LE n = LC 12,884+n; an era's last year is the next era's first. Keep the Gaelic spelling policy (sc not sg, grave accents only, t-/n- hyphen rule) and the Atlas as map of record. Protected place names must never be duplicated. [diaithir-novels]
- Rebuild order: `tools/build_canon.py`, then `tools/linters/run.py`, then `tools/build_sheets.py`. Work moved to the RTX 3080 PC on 10-01 (HANDOFF.md). [diaithir-novels]

**Conflicts with the rest of this file (newest wins)**
- The novels brief's "local Ollama does the bulk" and the PC global's "Ollama and `cascade/ask.py`" and `local-3d`/Hunyuan3D lines: the 10-21 ban is on local text models. Use ModelRouter, free lanes and the Claude API for text bulk; Hunyuan3D/Blender/Craft apps are media tools, not local LLMs, and stay as listed. `cascade/ask.py` (on the PC only) must not call a local model: point it at the API lanes (Haiku with caching, job folder) instead; Marlon's no-local-models rule already decides this (coordinator 11-01). [no-local-models, 10-21]

**PC project folders (condensed; originals in claude-md-intake/pc/, all under C:\\Users\\imarl)** [pc-projects, 11-01]
- Panscriptum kit (`panscriptum-library-kit`, `age_sort_wt\\panscriptum`; copies in kitpush and panscriptum-export are identical or generated, never hand-edit the mirror): read `reference/keystone_volumes/00_MASTER_CHARTER.md` and `map/CLAUDE.md` first; check `state/HALT.json` before any run. Chain of command (`src/escalation.py`): you may raise a halt, never lift one unless you caused the fault and have fixed it, proved it (`src/drill.py` plus battery green) and recorded a written ruling. No caps ever: no limit, sample, top-N or truncation on any source; slow means more workers or time. Never invent facts, addresses, Assay decimals or Shelfmarks; threads stay pending; pilot (`--pilot 3`) before scale; report progress. Python is `C:/Users/imarl/miniconda3/python.exe` (Norton breaks the py launcher). The "local Ollama" lines there are overruled by the no-local-models rule (section 9). `STATUS.md`, `FOR_OWNER.md` are generated; the pack and Panscriptum must match (essential 5). [panscriptum]
- ModelRouter (`modelrouter`) and its older twin `cascade`: never read or print `secrets.json`; do not move root files or rename folders (other projects and the panscriptum-maintenance task cite them); `ask.py -f <file> "<task>"` is the one-shot delegate and must go through the API lanes, not a local model. [modelrouter, cascade]
- `code_commons` (module list, CATALOG.md is generated: grep it, never load it whole; run `python tests/run_all.py` after changes) and `code-library` (grep INDEX.md first, copy and change only what the Adapt note says, never add keys or personal paths). [code-commons, code-library]
- Other projects, one rule each: `miami-vice-rts` (do not rename js/ files; load order in index.html is the architecture; `npm test`), `myth-and-blood` (new js file needs a script tag, then `npm run gen:eslint-globals`; RESUME.md is gitignored, never publish), `orrery` (HANDOFF.md must equal E:\\motoko\\HANDOFF.md; never delete .pt in runs/; no git, back up first), `apify-actors` (nothing moves to the next stage until a person has read the last output; never touch the Apify token; publishing and pricing need Marlon's OK). The ICM workspaces and `icm-architect` template follow the same rule: triggers "setup" and "status", read only the current stage's refs, outputs are the edit surface. [pc-projects]

## 10. Still not pulled in
Laptop user-level CLAUDE.md and any CLAUDE.md in the Prism or server folders (laptop is offline, intake pending), plus rules that exist only in archived thread transcripts.

**Quiet threads (Marlon 11-04 14:17):** post in your thread only when a job is finished, blocked, or needs Marlon. No progress updates. Checklists carry progress.

**Thread token diet (Marlon 11-04 14:22):** (1) At most ~8 lanes active at once; critical path first (consolidation, conflict fixes, compute, merge-safe, bot, combat/tank, pack, PC lane). (2) When your job is finished or you are idle with nothing owed, resolve your thread (set_thread_resolved). (3) If your lane is unfinished but not on the critical path, or your history is large, write a short handoff note to /mnt/project-files/plans/handoffs/<thread-title>.md (done, open PRs, next steps, owners), then resolve; the driver restarts it as a fresh thread when a slot frees.

**Context handoff rule (Marlon 11-04 14:29, restated 15:56): at 25% context a thread hands off to a fresh one.** After every turn, call get_session with no session_id and read external_metadata.context_usage. At used_tokens >= 125000 (25% of 500k): stop at a safe point, write /mnt/project-files/plans/handoffs/<thread-title>.md (state, open PRs, next steps, key paths), message the coordinator "handoff ready: <path>", and stop. The coordinator starts a fresh replacement and resolves the old thread. No hourly or timed refresh. **Watchdog (enforcer):** the Drive V1 lanes thread (cmsg_01EpyoqYuwV3X4z3b4zk5pEKNR8GCpK14oXUfQNCyHGVBs, notes in plans/DRIVER.md, helper plans/driver/stallcheck.py for stalls) checks every active lane's context and forces a handoff on any lane that missed it. No separate context-watchdog script exists yet.

**Lane rules (Marlon 11-04 15:59, approved "yes"):** active-lane cap is now 10 (Marlon 16:02, replaces 16). Every running lane follows three rules: (1) Quiet threads: post only when done or blocked. (2) Direct handoffs: message dependent threads directly, put status in files, not in the project chat. (3) Close on finish: resolve your own thread when the job is done (and the coordinator resolves a thread that handed off at 25%).


**ROUTING RULE (Marlon 11-04 16:02):** bulk work goes to API Haiku Batch job folders (Sonnet only for judgment or failed rows). Small text jobs (names, translation, compile triage, lore drafts) go to the PC router via jobs-local. Full threads only for integration, porting, clean-room code, merge/conflict, review. Active threads capped at 10; the driver brings lanes down to 10.
