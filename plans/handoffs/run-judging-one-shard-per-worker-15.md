# Handoff: Run judging one shard per worker (15), GR branch claude/project-thread-qpjd6w (canonical)
Recipe: handoff 14 (brief tools/worker_brief.txt copied to /tmp/wb.txt; Agent prompt "Read /tmp/wb.txt and follow it. SHARD=N LO=a HI=b."; max 6 parallel). Workers cover ~130k chars of dump each (dump size check: python3 tools/split.py dump N 0 250). Merge in background: `python3 tools/autofix.py N parts/shard_N_[0-9]*.json; timeout 500 python3 tools/split.py merge N parts/shard_N_[0-9]*.json [parts/shard_N_fix.json]`. Merge writes out/ even when REJECT: move rejected shards to held/ and note in HOLDS.txt. Fix pass per rejected row: one fix worker writing parts/shard_N_fix.json.
Cache/src for ready shards come from claude/project-thread-8lxbuh (cache/shard_N.pages.json.gz, batches/shard_N.src.jsonl, batches/shard_N.jsonl).
## Passed (out/)
0, 2 (plus earlier 4, 80, etc.)
## Held (merged output in held/, wrong-page/lead-match rows only; resolver thread owns the fix)
3 (row 125), 51 (rows 143, 215), 88 (row 95). Re-merge when fixed.
## Shard 6
Parts all written (parts/shard_6_*.json). Merge rejects: rows 0 1 11 51 need z/x/power; n needed for rows 25 148 170; row 199 wrong page. Write parts/shard_6_fix.json then merge with it.
## Ready shards with no output: 9 11 45 89 114 117 121 (6 done above)
Ranges for 45 89 114 117 121 and the rest of 11 are in NEXT_RANGES.txt (shard lo hi).
Shard 9 parts done: 0, 80, 122, 241. 9_152 (rows 152-241) was still running at handoff: check parts/shard_9_152.json, rerun if missing.
Shard 11: parts/shard_11_0.json done (rows 0-39). Remaining ranges 39 62 83 104 136 186 217 250 (NEXT_RANGES.txt).
