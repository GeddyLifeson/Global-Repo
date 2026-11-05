# Handoff: Run judging 5 shards at a time (judge lane, GR branch claude/project-thread-ddv1l7; PC cache also lands on claude/project-thread-8lxbuh)

## Marlon's decisions
- No API. 1 shard per worker (card answered 11-05 18:47; 5 per worker does not fit 60k). Workers hand off at 30%/60k, you at 60%/125k. Quiet threads: post only on finish/block/ask.
- Pipeline mode: PC download thread pushes caches (plans/powers/judge/cache/shard_N.pages.json.gz + batches/shard_N.src.jsonl); coordinator relays "batch pushed"; give each ready shard to one fresh worker.

## How to run a worker (Agent tool, run_in_background)
Brief is /tmp/brief.txt (may be gone; recreate from this): worker pulls branch, reads plans/powers/judge/PLAYBOOK.md (has Worker notes), `bash tools/shard.sh prep N`, scripts section extraction (Powers/Abilities/Skills/Battle/Attacks/Strategy), judge.py write N '<json>' (u0 key for no-source rows), `shard.sh done N` (needs validator PASS, commits, pushes). Stop at ~60k; report rows/powers/unresolved/PASS. Measured: 25-55k tokens per shard.

## State (11-05 19:10Z)
- Judged + validator PASS and pushed: 46 49 148 149 (redone, 5 powers) 153 154 155 156 157 158 159 (plus older 160 161 162 167 177). Destiny shards (153-159) are gear-only, 0 powers is correct.
- Workers still running when I stopped: 21, 31, 41, 48 (check git log / out/shard_N.meta.json; if no PASS after a while, rerun).
- Ready (cached, src, <=5 unresolved), not started: 50, 68.
- Not ready: 7 (6 unresolved), 41 (4, fine), 44 (16), 152 (35), 8 (20): need PC resolver rerun with commit 58d1954+ (tools/pages.py: template-start rows accepted when named page exists, second fragment key). 26, 34 cached but no src yet. Shard 0 rerun unfinished on PC. All others 1-159 not yet downloaded.
- Coordinator relays PC status; message_thread to the PC thread is refused (person's own session), ask the coordinator to relay.

## Pipeline fixes made (all pushed)
pages.py: template-name lookup, full-text fragment match, mid-text search, template rows with empty lead accepted, match() compares up to shorter text. judge.py show: Battle/Strategy/Gifts/Disciplines sections and unspaced headings. PLAYBOOK worker notes; .gitignore pyc. Baseline math: PR #117 merged into branch (BASELINE_CANON_METHOD.md).

## Known gotchas
Wrong-page rows (lead != page): blank url+title in batches/shard_N.src.jsonl then u0. `judge.py show` prints rows in chunks (`show N 80 250`). Don't pipe `prep` into head. `judge.py write` says PASS even with problems: trust `validate.py N`. WoD Discipline/Gift to pool mappings are low-confidence judgement (shard 49).

## Open items
1. Reconcile 159 downloaded vs 147 judged shards (V1_CHECKLIST N3): list the shards not judged and why.
2. Final: `python3 plans/powers/judge/tools/validate.py all` and per-shard validator outputs as evidence; record c3m file hashes (N5).
3. Open a draft PR from claude/project-thread-ddv1l7 to main when a meaningful batch is done (none opened yet).
