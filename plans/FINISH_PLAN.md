# V1.0 finish plan (written 2026-11-03 22:40Z, scope frozen by Marlon)

No new features. Everything already planned ships in V1.0; this plan only sequences and sizes it.
Sources: Global-Repo `throughput/MERGE_ORDER.csv`, `merge-safe/LAST_RUN.json` and `runs/`, GitHub PR counts for all four repos, the thread list, `plans/DRIVER.md`, `plans/V1_PUNCHLIST.md`, `plans/PACK_CONSOLIDATION_AUDIT.md`, `compute/ledger.csv`, `headless-bot/reports/2026-11-03/`.

## 1. Where things stand (numbers as of 22:30Z)

| Item | Count |
|---|---|
| Open PRs | 90 (ports 60, Global-Repo 20, DiaithirRPG 9, shardfall-game 1) |
| Of those, drafts | 87 |
| Open PRs created 11-02 or 11-03 | about 85 of 90 |
| MERGE_ORDER.csv rows | 130 (after the 22:40 restore and the 22:45 unskips) |
| Merged since 10-27 (ports + RPG + Global-Repo) | 320 |
| Pack size now | client about 180, server about 165 (wave 6 was 192/176, wave 7 takes 12 hosted jars off). Target 20 to 40. |
| Threads working now | rites, headless bot, megastructures, Age V/VI magic, Age V canning, code review, this one |

## 2. Observed throughput

PRs merged per day, summed over ports, DiaithirRPG and Global-Repo:

| Day | 10-27 | 10-28 | 10-29 | 10-30 | 10-31 | 11-01 | 11-02 | 11-03 |
|---|---|---|---|---|---|---|---|---|
| Merged | 11 | 5 | 0 | 78 | 0 | 57 | 35 | 134 |

PRs created per day (ports + RPG): 10-30: 1, 10-31: 0, 11-01: 22, 11-02: 51, 11-03: 149.

What this says:
- Merging comes in bursts, one burst per Marlon click. Three zero days in eight. Average 40 a day, but 65 to 135 on a day with clicks.
- Creation outran merging on 11-03 (about 170 opened, 134 merged), which is why the open count looks like a wall.
- The three Merge Safe runs on 11-03 merged 15, 5 and 4 PRs and skipped 45, 48 and 49. Skip reasons in the 21:09 run: 37 drafts missing from MERGE_ORDER.csv, 5 storage duplicates, 2 BuildCraft duplicates, 2 meteor duplicates, plus conflicts and a held migration. So the click rate was fine; the order file and duplicate decisions were the limit. The 22:45 unskips fix the duplicates.
- Lane turnaround, measured: a clean-room module thread takes 18 to 24 hours (storage: 11-02 22:41 to 11-03 20:31). Stacked PRs need a rebase every wave (conflict-fix A/B ran twice today).
- The pack shrank from 243 to about 180 jars in about 8 hours today. That was the easy part: open-licence folds. The audit says 20 to 40 is not reachable by folds alone.

## 3. Why it is slow

1. **Nothing is merged until a wave runs.** 87 of 90 open PRs are drafts. The Merge Safe tool only takes rows listed in MERGE_ORDER.csv, and the file lost 16 rows in a rebuild at 20:41. Every missing row is a skipped PR.
2. **Duplicates were never decided.** Storage (#107 #112 #114 #121 #123), BuildCraft (#108 vs #119) and meteors (#111 vs #113) blocked 10 PRs for hours. Decided 22:45.
3. **Work is tested headless only.** Bot findings today that code review did not catch: vehicles had no click boxes (216 aimed attempts, 0 mounts), default parts never spawned, tank icon magenta, router GUI opens nothing, portable storage menus had no slots, connected textures did nothing at first. The tank still cannot be mounted. The full pack does not fit the cloud container, so light per-module packs stand in, and the first full-pack client join (11-03) crashed 13 s in on the ships jar. Each module has one hidden defect round waiting for its first real client run.
4. **Scope grew faster than it finished.** ports PR numbers went from #164 to #249 in two days. About 35 lanes started on 11-02 and 11-03. Every new port or module counts against the 20 to 40 jar target and adds a rebase and a retest.
5. **The 20 to 40 jar target is a rewrite project.** Audit: 546 mods, 375 open, 138 all-rights-reserved, 29 unknown. ARR and unknown mods can only be clean-room rewritten (119 planned routes). Open-licence folds are mostly done.
6. **The API and compute queue stalled.** The watcher wrote nothing between 21:51Z and about 22:30Z (23 jobs pending, planet text partial). It is writing again at 22:32Z with 15 jobs pending. Note: the 30-day API key expires about 11-26, so bulk API work has a hard stop.
7. **Blocked threads.** On 11-03 14:50, 10 lanes sat blocked on questions to Marlon (economy, belts, mobs, picker, worldgen audit). Told to decide themselves at 22:30; resumption not yet verified.
8. **Client testing is held on purpose.** Marlon's rule (11-03 18:55): no PC client until the pack is 20 to 40 jars. That puts every real-client defect after consolidation.

## 4. Lanes: what is left, what blocks it, size

Size scale: S under 0.5 day, M 0.5 to 1.5 days, L 2 to 4 days, XL 5 or more days. Days are calendar days at today's parallelism.

| Lane | Open PRs / threads | Left | Blocked by | Size |
|---|---|---|---|---|
| Gate and merge hygiene | Global-Repo #18-37, Merge Safe | Add every draft to MERGE_ORDER.csv, run Merge Safe 2 to 3 times, clear conflicts | Marlon click per run | S, repeating |
| Storage and logistics | ports #107 #112 #114 #121 #123 #119 #108, thread 3cD9 | Merge winners, close losers, router GUI fix (bot FAIL) | Unskips done 22:45; click | S |
| Meteors and events | ports #111 #113 #134 | #113 wins; #134 follows | Click | S |
| Consolidation to 20-40 jars | ports #219 #247 #240 #238 #243 #239 #232 #233 #236 #237 #230 #205 #204 #201 #177, RPG #260 #249, thread V5AQ | Wave 7 merge, then clean-room rewrite of the remaining ARR and unknown mods (7 groups, 5 delivered), then fold libraries | Rewrite throughput; each rewrite needs rebase | XL (critical path) |
| Vehicles, aircraft, trains, freight | ports #206 #210 #216 #220 #221 #225 #228 #229 #235 #249 #203 #208, Global #27 | Tank seat/mount fix, narrow-car payload and crew rules (found unenforced), client drive and fire test, ships jar swap to .7 or .8 | Seat fix (CoBS); client test | L |
| Animation | ports #207 #209 #212 #222 #227, RPG #256 | Merge, client check of fauna, gun, sword and arrow clips (screens exist) | Merge order | M |
| Planets, flora, colony picker, culture start | ports #217 #241, RPG #255 #262 | Merge, `/colony` check, culture start picker (Great Zimbabwe added) | Click | M |
| Progression, economy, wages, magnitude, stations | ports #244 #242 #202, RPG #257 #258 #259 #261, Global #30 #34 | Merge, stations layer, trade-screen client test (bot not run yet) | Conflicts with wave 7 | M |
| Gear, munitions, building materials, everyday objects | ports #211 #245 #213 #234 #215 #226, thread 3yVW | Merge, recipe and Codex check | Click | M |
| Wiretech circuit network | ports #214 | Merge; non-draft, ready | Click | S |
| Bosses and Ascendant | #242 #202, boss rush PASS on client | Rite chains, wardens | Click | S |
| Rites, NPCs, quests, Library to content | thread 5Nob (working), others done | Rites build, client Library tab, named chests in the Library dimension | Rites thread | M |
| Magic Age V/VI, canning and farm machines, megastructures | 3 working threads | Finish, PR, merge | Their own work | M each |
| Realms (Undergarden, Backwoods, Bumblezone, Aether II, Aerial Hell) | #240 #205 | Boss rituals, creature models, portal activation (listed open) | Consolidation | M to L |
| OpenComputers port | #223 (work in progress, not in order) | Steps 2 onward | Compile and boot | L, highest risk |
| Compile of everything merged | COMPILE_STATUS.csv (110 OK, 2 FAIL, 14 N/A) | Fix the 2 fails | None | S |
| Pack rebuild, clean install, headless boot | Pack thread KKe5 | Rebuild after consolidation, swap ships jar, id migrations | Consolidation | M |
| PC client join and V1 test pass | V1_PUNCHLIST items 3 to 5 | Picker, safe landing, 60 s alive, spawn at Creag Ruadh, ore bands, Offgrid inspect, ships | Pack at 20-40 jars; PC rule | L (2 to 4 fix cycles) |
| Production restart, tunnel | V1_PUNCHLIST items 6 and 7 | Updater run, server.properties, restart, open the tunnel | Join passes | S |
| Assay tail | 118 ids (library thread) | Finish | None | S |
| Compute queue | 15 jobs pending | Keep watcher alive, finish before 11-26 key expiry | Watcher restarts | M |
| shardfall-game | #1 local job queue (data only, do not merge) | Nothing for V1 | None | n/a |

Held until Marlon: wave 6 and 7 world migration (`migrate_world.py` with the server stopped). Memory says there is no world save to keep (fresh world up 11-03), so this hold may be droppable. The coordinator should confirm.

## 5. Critical path

1. **Merge backlog and gate fixes** (now to 11-05). Add drafts to MERGE_ORDER.csv, run Merge Safe until skips are only real conflicts.
2. **Consolidation to 20-40 jars** (11-04 to about 11-11). Long pole: clean-room rewrites of the remaining ARR and unknown mods, with wave merges between.
3. **Pack rebuild, clean install, headless boot** (1 day after 2).
4. **First full-pack PC client join** (starts about 11-12). Expect 2 to 4 crash-and-fix cycles of about a day each, since the one join so far crashed.
5. **V1 test pass, production restart, tunnel open** (1 to 2 days after the join passes).

Everything else runs beside this path and only slips the date if it arrives after step 3, because a late jar means a rebuild and another install test.

## 6. Date range

| Case | V1.0 live | Assumes |
|---|---|---|
| Best | 11-10 | Consolidation done by 11-07, first join clean |
| Realistic | 11-14 to 11-22 | Consolidation done 11-09 to 11-12, two to three join cycles |
| Bad | 11-28 or later | OpenComputers or a big rewrite group slips, join needs five or more cycles, or the API key lapses on 11-26 with bulk work unfinished |

Estimate basis: 134 merged on the best day, lane turnaround about one day, jar count falling about 60 a day on folds but needing about 1 rewrite module per thread per day for the rest. These are a range, not a promise. The widest uncertainty is step 4, which has no history to measure.

## 7. What moves the date

- Freeze holds: any new port or feature adds a jar, a rebase and a retest. Each one costs about a day at the tail.
- Run Merge Safe after every wave of new rows, not once a day.
- Decide duplicates as they appear (the unskips of 22:45 are the model).
- Drop OpenComputers (#223) from V1.0 if it is not booting by 11-07. It is the largest single risk. Dropping it is a scope call, so it is listed here only as an option, not done.
- Allow one early PC join of a light but real pack to flush client crashes before the final one. That would break the 11-03 18:55 rule, so it is Marlon's call.
- Keep the compute watcher alive and finish bulk text before the key expires on 11-26.
