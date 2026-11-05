# Handoff: Run judging one shard per worker (8), GR branch claude/project-thread-qpjd6w (CANONICAL), 11-05 ~21:45Z
ddv1l7 and 8lxbuh are merged into qpjd6w. Work only on qpjd6w; pull 8lxbuh again for new READY_SHARDS/diag.
## Pass and pushed (out/shard_N.out.jsonl)
1, 5, 81, 82, 86, 92 (full-read redos for 1, 5, 81), 87, 105.
## Shard 2: all 4 parts done (parts/shard_2_{0,86,139,218,fix}.json), merge REJECTS only on "6 no-source rows > 2%" (row 119 resolves to the wrong page; its src was blanked). Needs the PC resolver recut of row 119 (Hero (class)), then `split.py merge 2 parts/shard_2_{0,86,139,218,fix}.json`; remove the blank of row 119 in batches/shard_2.src.jsonl and drop its u0 from shard_2_fix.json if the recut fixes it.
## Notes
- tools/pages.py: match() strips "[url label]" in leads; resolve() has 8lxbuh's article-strip fallback. Wiki API returns 429 from the cloud container, so resolver reruns (over-2% shards 0 3 51 88 99 101-103 152, diag/*.unresolved.jsonl) must run on the PC. Most of those unresolved rows have clear names (e.g. M3 Gun Motor Carriage, T-34, Spitfire, Fleetfoot Ken); spot check showed Spitfire/T-34 now resolve with current pages.py, so the diag files may be stale: PC should rerun resolve on those shards first.
- Rows with stripped template names (e.g. "The is a ...") cannot be named for gear, so they went to b0.
- Not done: 65 and the rest of SKIMMED.txt (full-read redo), ready shards 106-113 115 116 118-120 122-136 and rest of READY_SHARDS.txt, validate-all.
## Worker recipe (works)
Brief at /tmp is gone; recreate: read PLAYBOOK.md; `python3 tools/split.py dump N LO HI` read ALL; write parts/shard_N_LO.json (d=0,b1,n,p,W,x,z,f,u0); `split.py check N LO HI part`; no commit; one-line reply. Ranges: `split.py ranges N`. Max 6 workers (sonnet). Then `split.py merge N parts...` and fix with parts/shard_N_fix.json. Typical fixes: z "none stated: ..." for Abilities sections, n for names with \xa0, disambig/template rows to b0, blank a src row + u0 when the resolver page is wrong.
