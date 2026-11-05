# Handoff: Run judging one shard per worker (13), GR branch claude/project-thread-qpjd6w (canonical)
Recipe: see handoff 12 and 11. Work dir plans/powers/judge. Brief tools/worker_brief.txt -> /tmp/wb.txt; Agent prompt "Read /tmp/wb.txt and follow it. SHARD=N LO=a HI=b." Max 6 parallel. Merge: `python3 tools/autofix.py N parts/shard_N_[0-9]*.json; timeout 110 python3 tools/split.py merge N parts/shard_N_[0-9]*.json parts/shard_N_fix.json`. "W bad kind/mag/quote/name" fix: drop idx from W and b1 in the part files, rerun.
## Passed and pushed
129-135.
## Parts in flight when this thread stopped launching (workers write parts/ locally; check git for "Judge parts" commits and ls parts/)
- 136: parts 0 (rows 0-107 only), 108 (108-202), 203 (203-249). Merge 136 once all three are on the branch.
- 4: ranges 0-46, 46-113, 113-157, 157-212 in flight; 212-250 NOT started. Merge 4 when all five parts exist.
## Not started
- 80: ranges [[0,45],[45,95],[95,152],[152,200],[200,250]].
- 2 (needs PC recut of row 119), then rest of READY_SHARDS.txt on 8lxbuh.
