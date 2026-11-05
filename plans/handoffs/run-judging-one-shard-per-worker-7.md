# Handoff: Run judging one shard per worker (7), GR branch claude/project-thread-qpjd6w, 11-05 ~21:00Z
Context reached ~115k (cap 125k). Stopped launching.
## Done and pushed
- pages.match fix (tools/pages.py): nested parentheticals stripped on both sides (tried raw first, then stripped), lead may follow a stub/quote banner (within 400 chars). validate.py unchanged. PASS now: 82, 86, 92, 5 (5 was skimmed: still needs full-read redo).
## Parts written (uncommitted-before-this-handoff, now pushed), NOT merged-clean
- 105: parts/shard_105_{0,54,95,174}.json. `python3 tools/split.py merge 105 parts/shard_105_{0,54,95,174}.json` gives 10 problems, see below. Fix with a small fixer writing parts/shard_105_fix.json, then re-merge with all parts.
  - rows 26 32 36 55 72 (+1 more): need z "none stated: reason" (or p/x) because pages have an Abilities/Powers section.
  - row 134: set n ("Kick-Off"); row 237: W bad kind/mag/quote/name.
  - row 87 unresolved source (must be b0 with u0 / z "no source page: ..."); rows 95, 157, 205 lead-match fail (resolver/page mismatch, check pages.srcs vs lead; may need PC re-cut).
- 87: parts/shard_87_{0,53,134}.json done and check OK; part [196,250] NOT started. Then `split.py merge 87 parts/shard_87_{0,53,134,196}.json` (row 54 is u0 no-source).
## Next steps
1. Fix + merge 105; launch 87 [196,250]; merge 87.
2. Redo under full reads: 1 [[0,77],[77,141],[141,223],[223,250]], 2 [[0,86],[86,139],[139,218],[218,250]], 81 [[0,76],[76,155],[155,216],[216,250]], 65, 5 and everything in SKIMMED.txt. Worker brief used: recreate from HANDOFF 6 text (read PLAYBOOK, `split.py dump N lo hi`, read ALL, write parts/shard_N_LO.json with b1,n,p,W,x,z,f,u0; run `split.py check`; no commit; one-line reply). Max 6 workers.
3. Ready shards not yet judged: 106-113 115 116 118-120 122-136 (use split.py ranges N).
4. Over-2% no-source shards per coordinator 20:59Z: 0 3 51 88 99 101 102 103 152; look at 99, 103, 102 (diag/ on 8lxbuh), push pages.py fix.
5. Open a draft PR for the branch (none yet).
