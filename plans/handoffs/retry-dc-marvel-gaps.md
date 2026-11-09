# Handoff: Retry DC and Marvel Panscriptum gaps (part 2)

Branch GR claude/project-thread-yzyymm (draft PR #128). Written 2026-11-09 ~19:50Z.

## Method (unchanged, see work/ in plans/panscriptum_gap/)
- Tools in plans/panscriptum_gap/work/: prep.py, process.py, spec/ (gap_batch.py). Set up in a fresh scratchpad S: copy work/ to S, `python3 -I S/prep.py S` (builds sys.txt and 50-row shards dc/in, marvel/in), `mkdir S/dc/out`.
- Dedupe: S/dc/state.json is NOT needed in a fresh container if you only run shards >= s139 (no overlap). For Marvel use tag marvel (fresh state). Put accepted entries in S/<tag>/accepted.jsonl; process.py appends there and bumps /mnt/project-files/compute/id_counters/gap_<host>.
- Workers: Agent (sonnet, background, general-purpose), one per two shards. Prompt: "S=<path>. Read $S/sys.txt and follow it for every row. For each shard SH in [sNNN,sMMM]: read $S/<tag>/in/SH.jsonl, ONE Write call to $S/<tag>/out/SH.jsonl, lines {id,reply:{summary,feats,realm,ceiling_T,powers}}. Skip only rows with no character. Do not spawn agents. Final answer: done." Up to ~17 in flight. Each worker ~140k own tokens; ~4 min.
- Push: take origin out.jsonl (retry-dc/out.jsonl, or retry-marvel/out.jsonl), append only new ids from S/<tag>/accepted.jsonl, commit, push (rebase conflicts on out.jsonl: take upstream and re-append).
- Yield ~50-55% accepted rows after validator.

## State
- DC: shards s000-s138 DONE (s000-s070 by the old lane, s071-s138 by this thread). Accepted entries pushed in retry-dc/out.jsonl (see final count below). NEXT DC shard: s139 through s200.
- Marvel: not started (667 shards s000-s666, host marvel.fandom.com, universe Losaustanum, counter file gap_marvel.fandom.com).
- At the end: copy out.jsonl to /mnt/project-files/compute/jobs/panscriptum-gap/retry-<tag>/out.jsonl if space allows, tick P1 in plans/V1_CHECKLIST.md with counts.
- Rules: never delete PANSCRIPTUM_MASTER entries; never merge; no Actions. Marlon approved full-speed tokens; stop at 90% weekly usage.
- Final DC accepted count in out.jsonl at this handoff: 6137

## Update 2026-11-09 ~20:00Z (part 3)
- DC s139-s200 DONE, pushed (retry-dc/out.jsonl, 8815 lines). DC finished.
- Marvel: shards s000-s008 done and pushed (retry-marvel/out.jsonl, 276 entries; s003 and s009+ not yet processed unless in later commits). NEXT: s003 (check marvel/out), s009 onward to s666.
- Marlon 11-09 19:29Z: slow down, shards eat weekly usage. Run only 1-2 agents at a time.
- Setup in fresh container: copy work/ to S, python3 -I prep.py S, then S/marvel/out; process.py dedupes by id only within S state, so skip shards already pushed.
