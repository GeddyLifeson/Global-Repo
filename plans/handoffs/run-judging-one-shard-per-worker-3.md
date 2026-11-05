# Handoff: Run judging one shard per worker (3) (GR branch claude/project-thread-ddv1l7), 11-05 ~19:45Z
Read plans/handoffs/run-judging-one-shard-per-worker-2.md and run-judging-5-shards-at-a-time.md first (method, gotchas). Method unchanged: one Agent (run_in_background) per shard, brief = /tmp/brief.txt (recreate: pull, read PLAYBOOK.md, shard.sh prep N, read FULL source page sections, judge.py write, validate.py N, shard.sh done N, ~60k stop, one-line report). Keep ~6 running. Pull origin claude/project-thread-8lxbuh for new PC caches.

## Passed shards with meta in out/ (at handoff, before in-flight finish)
8 10 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 46 47 48 49 50 52 53 54 57 59 66 67 68 69 71 74 148 149 153 154 155 156 157 158 159 160 161 162 167 177 
## Cached with src, no meta yet (includes in-flight)
3 4 7 42 44 51 55 56 58 60 61 62 70 73 75 76 77 78 79 80 82 83 85 86 87 88 90 91 99 101 102 103 106 107 108 109 113 115 116 118 119 123 152 
## In flight when I stopped: 59 18 51 55 42 56, and 47 REDO
47: first worker skimmed lead/evidence only (violates full-page rule); redo overwrites its output. Check origin for PASS on these; rerun any without.
## Notes
- Brief must say read FULL page sections; do not change the brief mid-run (42's first worker aborted because of that).
- Shards 7, 44, 152 wait for PC resolver rerun; 0-2 on PC.
- Open: reconcile downloaded vs judged (N3), validate.py all + c3m hashes (N5), open draft PR ddv1l7 -> main (none yet; a big batch is in).
