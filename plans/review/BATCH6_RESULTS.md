# Review Batch 6: names, loot, data hygiene (2026-11-19)

Status: decision pack plus paper fixes. Nothing here was run in game: UNTESTED. Work on repos outside this thread's scope (DiaithirRPG #289/#290, palette branch) needs a thread with that repo.

## Marlon decisions (recommendations taken as defaults)
| Item | Recommendation | Done here |
|---|---|---|
| C3/E15 names #289 | Do NOT merge as "repaired". Treat coined words as placeholders. Add checks: per-culture uniqueness, English passthrough, Goidelic wordlist, coined share per culture, 200-row human sample per language. | Plan only; needs RPG repo thread. Mount `names/` drops are a small subset (about 3.5k entries) and cannot give the 1.27M count. |
| C9 | Snapshot `/mnt/project-files/names/` before any in-place run; move `audit_names.py` next to `fix_names.py`. | Plan only. |
| C7/E17 palette | Not approved. Keep `--no-palettes` the default until Marlon views the preview and one in-game screenshot. Commit a fixed palette table; skip tint-index, entity and `_n/_s/_e` textures. | Plan only (RPG branch 3izkf0). |
| E13 bosses | Overnight PC lane lists the diaithirbosses jar loot tables (45 items per PC lane). Marlon states if source is jar-only. | Open question stays with Marlon. |
| E14/E12/C17 | One owner for Ages and item roles (F11-F13). Close or fold GR #123 and #131 before #133 and RPG #290. Do not merge #133/#290 until a sample is checked in game and the Age I fallback list is reviewed. Boss count: 45 (PC lane, newest). 1,072 orphan loot sources and 601 assumed role rows are labelled UNTESTED fallbacks. | Labelled here. |
| A9 | Keep caches out of public repo; attribution added. | `ATTRIBUTION.md` |
| A23 | Low risk, keep. | Noted in `ATTRIBUTION.md` |
| A10 | Judging and retries stay parked (budget pause). | Already paused |

## D items
- D10 API spend: ledger shows about $72-163, incomplete. If the API returns: Batch for Sonnet, cached prefix, log every caller. No action now.
- D11 open compute jobs (owner, decision): assay-retry-019/027-031/033/034/037/038, item_roles-retry3, libmob_classify-retry3/5 = DROP unless API returns (wait for credit); dish_comp_pick_1b, worldsys-code = DROP (never produced output); relink-things = WAIT (on hold); panscriptum-gap/retry-dc and retry-marvel = PARKED by budget; transport_names s07-s12 = DROP (poller off, nothing syncs).
- D15 handoffs: about 40 of 69 are dead. Archive candidates (all Judge-*, Build/Run headless bot, Port OpenComputers, shard P/Q/A/B/C series, judge-inflight-*): list only; deleting shared-folder files needs Marlon's go. Live ones: judge-160-927-part6, retry-dc-marvel-gaps, get-all-wiki-pages-bulk, driver, economy-rites-misc-j10.
- D16 MEMORY.md: should become an index with a `v1-current-state.md`; prune about 25 files; 11 dangling links; email in `modal-compute.md` line 8 should be removed. Not applied: team memory edits left to Marlon's approval.
- D19 token-costly rules: suspend ID claims, Bible check.py on pack work, and "check API jobs folder" until V1 ships; context check every fifth turn. Needs a master CLAUDE.md edit, which the PC permission check blocks for Claude: Marlon applies.
- D20: `plans/COMPILE_STATUS.csv` marked HISTORICAL. Dead MERGE_ORDER copies to delete (Marlon's go): mount `plans/MERGE_ORDER.csv`, GR `plans/MERGE_ORDER.csv`, GR `throughput/MERGE_ORDER.csv`. Live: `merge-safe/merge-order.csv` on branch zuc996.
