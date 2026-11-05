# Handoff: Run judging one shard per worker (10), GR branch claude/project-thread-qpjd6w (canonical), 11-05 ~21:35Z
Recipe as in handoff 8/9. Work dir plans/powers/judge. NEW helpers committed: tools/worker_brief.txt (worker brief; copy to /tmp and tell Agent "Read <path> and follow it. SHARD=N LO=a HI=b."), tools/autofix.py N parts... (writes parts/shard_N_fix.json: z "none stated" for Abilities rejects, n for odd names; then run `split.py merge N parts... parts/shard_N_fix.json`).
## Passed and pushed this thread
107, 110, 111, 112, 113 (plus earlier 1 5 65 81 82 86 87 92 105 106 108 109).
## Manual fixes seen
Stripped-name gear ("The  is a"): drop its W and b1 from the part file and, if the resolver page is wrong, blank the src row in batches/shard_N.src.jsonl + add u0 in the fix file. Beings with stripped lead names: n "".
## Shard 115 (ranges [0,49][49,86][86,117][117,150][150,176][176,213][213,250])
Launched ranges 0..213; 213-250 NOT launched. If parts/shard_115_*.json exist on the branch, merge; else relaunch.
## Remaining ready, not started
116 118 119 120 122-136, then 2 (needs PC recut of row 119), 4, 80. Then rest of READY_SHARDS.txt on 8lxbuh.
Max 6 workers in parallel. Workers take ~70-110s each. Stop launching at ~100k own context.
