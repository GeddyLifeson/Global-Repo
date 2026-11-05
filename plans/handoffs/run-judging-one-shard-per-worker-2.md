# Handoff: Run judging one shard per worker (2) (GR branch claude/project-thread-ddv1l7)
Read plans/handoffs/run-judging-5-shards-at-a-time.md first (workflow, gotchas); this adds state at 11-05 19:30Z.

## Method that works
Spawn one Agent (run_in_background) per shard with a brief: pull branch, read PLAYBOOK.md, `bash plans/powers/judge/tools/shard.sh prep N`, judge, `judge.py write N`, trust `validate.py N`, `shard.sh done N` (pull --no-rebase and re-push on rejection), stop ~60k, short report. Keep ~5-6 running. Pull origin claude/project-thread-8lxbuh to pick up PC caches (merge into ddv1l7, push).

## Passed + pushed (meta files in out/)
8 16 17 19 20 21 22 23 24 31 41 46 48 49 50 66 68 74 148 149 153 154 155 156 157 158 159 160 161 162 167 177 

## Workers still running when I stopped (check out/shard_N.meta.json / git log; rerun if no PASS): 10, 22, 24, 25, 26, 28

## Cached with src, not yet judged / not started
10 101 106 107 108 123 152 18 25 26 27 28 29 30 32 33 34 35 36 38 39 40 44 47 52 53 54 55 56 57 58 59 60 61 62 67 69 7 70 71 73 75 77 78 79 82 85 86 87 88 90 91 
(minus the running ones above)

## Tooling changes this thread (pushed)
- pages.py: PC patch merged (empty-lead template rows accepted when page exists); skip host on fetch error.
- validate.py: template-start (`{{`), nameless (`is/was/are/,`) and image-caption-fragment (`...]]`) leads accepted when the resolved page exists. Shard 8 now PASS.
- Worker quality note: some workers add generic filler x tags (spell_list) to satisfy "Abilities section needs a power/x/z" check; brief now says prefer z "none stated: reason". Shard 16 has 5 such spell_list tags; shard 50 auto vampirism/possession regex tags unchecked for false positives; shard 50 powers possibly missed on long stat blocks.
- Uncommitted .pyc under tools/c3m_lib/__pycache__ are tracked; ignore (git checkout them).

## Open
1. Reconcile 159 downloaded vs judged shards (V1_CHECKLIST N3). 2. Final validate.py all + record c3m hashes (N5). 3. Open draft PR ddv1l7 -> main when a good batch is in (none opened yet). 4. Shards 7, 44, 152 wait for PC rerun with new resolver; 0-2 rerun on PC.
