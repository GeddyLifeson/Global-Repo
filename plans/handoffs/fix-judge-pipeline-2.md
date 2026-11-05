# Handoff: Fix judge pipeline (2) (Global-Repo branch claude/project-thread-8lxbuh, from yq7x8t e2060461 + bc5d482)
Read plans/handoffs/fix-judge-pipeline.md first (pipeline, paths, rules). This adds what changed.

## Marlon's orders (11-05)
- "Just do them 5 at a time here", no API. 5 shards per fresh worker, workers read only a short brief and hand off at 60k tokens. Prove one 5-shard worker (shards 0-4), check its rows and real token cost, then fan out; open the next worker as each finishes and resolve finished ones.
- "Just have a script download it all": step one is bulk page download, then judge from the local cache. Context watch: hand off at 125k (this thread hit 155k).
- Math: derive the method sd and canon weights ourselves (not wait for Marlon): run through c3m.zip (measure.py, inference.py; combat.py not yet read), justify a baseline, test on feats from the passing shards (160,161,162,167,177; note none has a real SI feat), write plans/powers/judge/BASELINE_CANON_METHOD.md marked "refinable baseline". NOT STARTED. Facts found: inference.Feat has sd (calc uncertainty), w (canon weight in (0,1], divides variance: s^2/w), SOURCE_BIAS = primary (0,0), author (0,.2), anime (.3,.3), game (.5,.5), scaled (0,0). feats.py METHOD_SD (stated .2, measured .3, scaled .4, estimated .6) and CANON_W (main 1, extended .5, games .5, noncanon .2) are guesses. Game sources already get bias via SOURCE_BIAS, so CANON_W games .5 may double count: consider games 1.0 w/ bias doing the work.

## State
- Pushed on branch: tools/shard.sh (prep N / done N), tools/bulk.py (A B workers: copy old shard, resolve, fetch pages -> cache/shard_N.pages.json.gz; pages.text reads cache first), pages.py: wikitext batch fallback for wikis w/o TextExtracts (fandom), throttle, 429 pause, wiki2txt.
- BLOCKER: fandom serves this cloud IP a Cloudflare challenge (HTTP 429); about 430 pages were fetched before it started. Fandom XML dumps on S3 are DEEP_ARCHIVE (403), dead end. Non-fandom wikis work from the cloud.
- The PC download thread (started by coordinator, cmsg_01EpyoqYuwV3X4z3b4zk5pEKBcubfnHUrTWMiGNqvQDDaz) runs `bulk.py 0 160 2` and pushes cache/ + batches/ to this branch; it messages when shards 0-4 land. Caveat: pages.py intro() batched wikitext path was only unit-tested before the block; first real run may need fixes (check resolved counts: `grep -c NO-SOURCE`).
- Old inputs for shards 0-159: /mnt/project-files/plans/powers/judge/inthread/shard_NN.jsonl (bulk.py copies them to batches/).

## Next
1. Wait for PC message; `git pull` the branch; `tools/shard.sh prep 0` (judge view from cache), write config JSON per PLAYBOOK, `judge.py write N`, `tools/shard.sh done N`.
2. Prove with a 5-shard worker (0-4): read its rows, measure tokens via get_session usage delta.
3. Write the canon/method baseline file (above), then wire into feats.py if justified.
4. Fan out 5-shard workers (coordinator or Agent), 60k limit each.
