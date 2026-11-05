# Handoff: fix-judge-pipeline (Global-Repo branch claude/project-thread-yq7x8t, mirrored on claude/project-thread-nn7sho)

## State (2026-11-05)
- Judge pipeline rebuilt: each batch row is resolved to its wiki page (title + URL), judges see the FULL page text including Abilities sections, every row records its source page, a short summary, powers with verbatim quotes, c3m feats, and a `z` "none stated: reason" for Abilities pages with no pool power.
- Shards judged and validator-PASSED: 160, 161, 167, 177 (redo), 162 (cost measurement run). Latest commit cc26ff55.
- Old shards 0-159 (147 files under /mnt/project-files/plans/powers/judge/inthread/ and the s4t1m3 branch): 36,550 rows, 1,367 with powers, 0 with source URL. They fail the validator and need redoing. Their inputs are old-format (text<=700, same ids `wiki|idx`); copy shard_NN.jsonl into plans/powers/judge/batches/ to judge them.
- Waiting on Marlon: "go" for the 0-159 redo and the full 163-927 fan-out. Marlon said "ok" to the batch-160 format only. Marlon wants context watched (125k handoff limit); run one fresh thread per 4-6 shards.

## Key paths (plans/powers/judge/)
- PLAYBOOK.md: rules and the loop. tools/judge.py (show N / write N), tools/pages.py (S6984, resolve + full text), tools/validate.py (S6985, runs automatically at the end of write), tools/feats.py + tools/c3m_lib (c3m measure.py/inference.py copies), tools/selftest.py (rejects 11 broken variants), tools/wikis.tsv.
- batches/shard_N.jsonl + shard_N.src.jsonl (resolved titles/URLs); out/shard_N.out.jsonl + shard_N.meta.json.
- Fold gate: cloud/tools/powers/merge_judged.py refuses judge/out shards that fail validate.py. `validate.py all` re-validates everything.
- Spec sources: plans/powers/JUDGE_PAGES.md (S6975), POWER_POOL.tsv + plans/powers README, assay-c3m/SYSTEM_PROMPT.txt, c3m.zip (file_01NCEmfvJ655n36WbeZnk3AV).

## Per-shard procedure (about 9 tool calls)
1. `python3 tools/pages.py resolve N` (about 45 s; shows unresolved count). 2. Read titles + leads, and the evidence (`@@` sections / strong keyword hits). 3. Write config JSON (d=1, b0 non-beings, W gear, p powers, z reasons, u0 for unresolvable junk fragments, max 2%). 4. `python3 tools/judge.py write N '<json>'` must print PASS. 5. Commit + push both branches.
- Resolver tips: titles with a leading rank ("Commander X") are found via name-search; "(no extract)" template pages accepted only if the page has no text at all.

## Open issues
- Magnitudes are my reading of scale words; fireball id used for fire breath; non-beings flagged by eye (regex helper then lead review).
- Method sd (stated .2, measured .3, scaled .4, estimated .6) and canon weights (main 1, extended .5, games .5, noncanon .2) in feats.py are my assumptions; no zip document defines them. Ask Marlon to confirm. No real feat exists in shards 160-177 (no page states physical units); c3m maths were verified only on a synthetic test.
- 7 junk fragment rows (BWL, T2, T3, ZG ...) have no source page and are marked `z: no source page`.

## Cost
- Session so far (all work incl. tooling): $6.28; 23.5M cache-read, 0.77M cache-write, 83k output tokens.
- Shard 162 measured as a usage delta at 313k context: +3.55M cache-read, +20.7k cache-write, +7.4k output, +$0.51 (includes one small status post). 
- 147 shards in this fat context would cost about $75. In fresh threads (30-50k context) cache reads fall about 7x: estimate $0.10-0.15 per shard, about $15-22 for 147 shards (estimate, not measured). Haiku batch would be cheaper but API has no credit. Validator, resolver and fold checks cost 0 tokens.
