# Handoff: Retry DC and Marvel Panscriptum gaps

Written 2026-11-09 ~19:10Z at 146k context. Branch GR claude/project-thread-yzyymm (draft PR #128).

## Method (works, ~89% of replies pass the validator)
- Tools in plans/panscriptum_gap/work/: prep.py (builds sys.txt + 50-row shards in scratchpad dc/in, marvel/in), process.py (validates replies with gap_batch.accept, assigns ids from /mnt/project-files/compute/id_counters/gap_<host>, appends to <tag>/accepted.jsonl, state in <tag>/state.json), spec/ (gap_batch.py + originate_prompt.txt from GR 28p9u0, unchanged).
- Set up in a fresh container: copy work/ to a scratchpad dir S, run `python3 -I S/prep.py S` (edit paths if needed), copy work/dc_out/* to S/dc/out/ and work/dc_state.json to S/dc/state.json, put accepted entries back from plans/panscriptum_gap/retry-dc/out.jsonl into S/dc/accepted.jsonl. Then `python3 -I S/process.py S dc` is idempotent.
- Workers: Agent (model sonnet, background, general-purpose), one per TWO shards, prompt: read S/sys.txt, follow it for every row; for each shard read S/<tag>/in/SH.jsonl, write ONE Write call S/<tag>/out/SH.jsonl, lines {"id","reply":{summary,feats,realm,ceiling_T,powers}}; skip only rows with no character; final answer only counts. Up to ~17 in flight (hard cap 20). Nested Agent spawning is NOT available to subagents. A worker costs ~140k of its own tokens; each launch+result costs me ~3k context, so hand off about every 40 launches.
- Marvel universe is Losaustanum, host marvel.fandom.com, counter currently 972827 (read before use).

## State
- DC: 201 shards (s000-s200), 10,016 rows. Outputs done: s000-s035, s037-s041, s043, s045-s047, s049-s050 (plus any landed since). 2,067 accepted, 236 rejected as of the last process.py run, counter file now 926032 (dc backup of the old value: 923965).
- Still in flight when this was written (outputs may land in the old scratchpad): s036, s042, s044, s048, s051-s070. If the scratchpad is gone, redo those.
- NEXT DC shard to launch: s071 onward, through s200.
- Marvel: not started (667 shards, s000-s666, 33,341 rows).
- Real people (dictators etc.) were skipped by workers on purpose; fine.
- Pushed: retry-dc/out.jsonl (1,938 rows at the first push). Re-copy accepted.jsonl to plans/panscriptum_gap/retry-dc/out.jsonl and push after each wave. Never edit dc/out.jsonl; never delete PANSCRIPTUM_MASTER entries; no merge; no Actions.
- At the end: copy out.jsonl to /mnt/project-files/compute/jobs/panscriptum-gap/retry-<tag>/out.jsonl if space allows, tick P1 in plans/V1_CHECKLIST.md with counts.
