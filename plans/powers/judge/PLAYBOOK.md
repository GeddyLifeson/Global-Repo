# Judge playbook (in-session, no API). Read only this page.
Helper: `python3 /mnt/project-files/plans/powers/judge/tools/judge.py` (3 commands). Test shard 106 cost about 12k tokens of reading.

## Loop
1. `judge.py claim <your-tag> 80 159` prints shard N (atomic; skips claimed/judged). "none" = stop and resolve. Judge only N.
2. `judge.py show N` prints `idx|first sentence ## power/scale sentences only` for 250 pages (about 8k tokens). Needs no other reading. Use `show N 0 80` for halves.
3. Decide per row, then ONE `judge.py write N '<json>'`; it validates and writes shard_NN.out.jsonl and lists problems by idx. Fix and re-run (it overwrites).
4. Commit + push shard_NN.out.jsonl to your branch (Global-Repo plans/powers/judge/inthread/). Claim next.

## Rules (unchanged)
- Page by page, exact source page = the row id (`wiki|lead_idx`). Quote must be verbatim from the text; no quote, no power.
- Beings (b1): named individuals only. Plurals, types, species, groups, titles, concepts, disciplines, episodes, missions, camos, perks, attachments and junk fragments ("Dr.") are b0.
- Non-beings are linked but NOT assayed (b0), EXCEPT weapon, armor, vehicle: b2 with kind, one overall magnitude m 1-10, quote, confidence. Plain firearms/cars = 1.
- Powers p only from pool ids in plans/powers/POWER_POOL.tsv, magnitude on the C3M scale: 1 peak human, 2 city block, 3 building, 4 city, 5 mountain, 6 island, 7 ocean/continent, 8 moon, 9 planet, 10 star/universe. Rare; most lead texts state none. Non-pool abilities go in x (short tag).
- No Anthropic API. Do not hand-claim shards; never write another thread's shard.

## write JSON
`{"d":0, "b1":[idx..], "n":{idx:"name"}, "p":{idx:[["flight",5,"verbatim quote","h"]]}, "W":{idx:["weapon|armor|vehicle","name",m,"quote","h|m|l"]}, "x":{idx:["tag"]}, "auto":1}`
- d=0: unlisted rows are b0; use `"d":1,"b0":[idx..]` when most rows are beings (list the non-beings instead).
- Name is auto-taken from the first words before ` is/was/(/,`; if the helper reports "name not in text", add it to `n` (use "" when the name is stripped).
- `auto":1` adds x vampirism/possession by regex (WoD shards; check for false positives like "vampire hunter").
