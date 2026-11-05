# Handoff: Run judging one shard per worker (13), GR branch claude/project-thread-qpjd6w (canonical)
Recipe: see handoff 12 and 11. Work dir plans/powers/judge. Brief tools/worker_brief.txt -> /tmp/wb.txt; Agent prompt "Read /tmp/wb.txt and follow it. SHARD=N LO=a HI=b." Max 6 parallel. Merge: `python3 tools/autofix.py N parts/shard_N_[0-9]*.json; timeout 110 python3 tools/split.py merge N parts/shard_N_[0-9]*.json parts/shard_N_fix.json`. "W bad kind/mag/quote/name" fix: drop idx from W and b1 in the part files, rerun.
## Passed and pushed
129-136 (out/ written, problems 0).
## Parts in flight when this thread stopped launching (workers write parts/ locally; check git for "Judge parts" commits and ls parts/)
- 4: parts 0, 46, 113, 157 done (157 covers rows 157-188 only). Still to judge: LO=189 HI=212 and LO=212 HI=250. Merge 4 when all five parts exist.
## Not started
- 80: ranges [[0,45],[45,95],[95,152],[152,200],[200,250]].
- 2 (needs PC recut of row 119), then rest of READY_SHARDS.txt on 8lxbuh.
