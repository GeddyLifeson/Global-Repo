# Handoff: Run judging one shard per worker (11), GR branch claude/project-thread-qpjd6w (canonical), 11-05 ~21:45Z
Recipe as in handoff 10 (read plans/handoffs/run-judging-one-shard-per-worker-10.md). Work dir plans/powers/judge. Worker brief: tools/worker_brief.txt (copy to /tmp/wb.txt; Agent prompt "Read /tmp/wb.txt and follow it. SHARD=N LO=a HI=b."). Ranges: `python3 tools/split.py ranges N`. Merge: `python3 tools/autofix.py N parts... ; python3 tools/split.py merge N parts/shard_N_[0-9]*.json parts/shard_N_fix.json` (merge can take >100s, use timeout 110).
## Passed this thread (merged, out/ written)
115, 116, 118, 120, 119, 122. Earlier: 107 110-113, 1 5 65 81 82 86 87 92 105 106 108 109.
115, 116, 118, 120 pushed. 119 and 122 merged and PASS locally; the final commit/push is in this thread's last step (check git log for "Judge shards 119 and 122").
## Fix patterns used
- "name not in text" (n): set fix n {idx:""}.
- wrong page vs lead: blank url in batches/shard_N.src.jsonl row, fix u0 {idx:reason}, remove idx from part b1/W etc.
- Gear with stripped name ("The  is a", W bad / gear name missing): drop its W and b1 from part files.
## Next
123-136 in order, then 2 (needs PC recut of row 119), 4, 80, then rest of READY_SHARDS.txt on 8lxbuh. Max 6 workers in parallel.
