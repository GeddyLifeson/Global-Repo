# Handoff: Run judging one shard per worker (12), GR branch claude/project-thread-qpjd6w (canonical), 11-05 ~21:50Z
Recipe as in handoff 11 (plans/handoffs/run-judging-one-shard-per-worker-11.md). Work dir plans/powers/judge. Brief: tools/worker_brief.txt -> /tmp/wb.txt; Agent prompt "Read /tmp/wb.txt and follow it. SHARD=N LO=a HI=b." Max 6 parallel.
## Passed and pushed this thread
123, 124, 125, 126, 127, 128 (out/ written, problems 0). Fix pattern for "W bad kind/mag/quote/name" = stripped-name gear: drop idx from W and b1 in all part files, rerun autofix then merge. Wrong page vs lead (123 row 5): blank url in batches/shard_N.src.jsonl row, add u0 to parts/shard_N_fix.json AFTER autofix.
## In flight when handed off (their part files may land after this; check parts/ and ls before relaunching)
- 129: parts 0 (rows 0-32 only), 209 done; worker running for LO=33 HI=209 (writes shard_129_33.json).
- 130: part 152 done; worker running LO=0 HI=152 (may hand off partial: relaunch from its last row).
- 131: part 191 done; worker running LO=0 HI=191.
- 132: worker running LO=0 HI=209; 209-250 not started.
## Not started
132 (209-250), 133-136 (ranges via `python3 tools/split.py ranges N`), then 2 (needs PC recut of row 119), 4, 80, then rest of READY_SHARDS.txt on 8lxbuh.
Workers that hand off partial: relaunch with LO=their last covered row; parts glob merges all shard_N_[0-9]*.json.
- UPDATE 21:55Z: parts for 129 (0,33,209), 130 (0,152), 131 (0,191) are all on the branch; merge 129, 130, 131 (autofix then merge). Only 132 (0-209 worker may still be running) remains in flight.
