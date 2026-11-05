# Handoff: Run judging one shard per worker (9), GR branch claude/project-thread-qpjd6w (canonical), 11-05 ~21:25Z
Recipe unchanged from handoff 8 (plans/handoffs/run-judging-one-shard-per-worker-8.md). Work dir plans/powers/judge.
## Passed and pushed this thread
65 (removed from SKIMMED.txt, now empty), 106, 108, 109. Earlier: 1 5 81 82 86 87 92 105.
## In flight when this thread stopped (workers write parts/ files; no commit by them)
- Shard 107: ranges [0,57] [57,124] [124,187] [187,250] -> parts/shard_107_{0,57,124,187}.json
- Shard 110: ranges [0,92] [92,182] [182,250]; 182-250 NOT launched -> parts/shard_110_{0,92}.json exist when workers finish; need a worker for 182-250
Check which parts files exist and pass `split.py check`, then `split.py merge N parts...`, fix rejects in parts/shard_N_fix.json (z "none stated: ..." for Abilities sections; n for \xa0/odd names; drop gear whose name is stripped ("The  is a")), commit, push to qpjd6w.
## Remaining ready, not started
111 112 113 115 116 118 119 120 122-136, plus 2 (needs PC recut of row 119), 4, 80.
## Lessons
- Workers must be told: no truncation of lines, no keyword scanning, read chunks of ~20 rows; skimmers (65 rows 87-195, 108 rows 0-84) had to be redone. Tell them not to share /tmp dump files (one collided).
- Worker brief template is in this thread's /tmp/brief.txt (gone later); contents: read PLAYBOOK.md, split.py dump N LO HI, write parts/shard_N_LO.json, split.py check, one-line reply.
