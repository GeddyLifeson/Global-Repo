# Judge playbook (in-session, no API). Read only this page.
Batches: plans/powers/judge/batches/shard_160..927.jsonl (250 pages each, beings first).. Test shard 106 cost about 12k tokens of reading.

## Loop
1. Your batch number N is given by the coordinator (no claiming). `python3 plans/powers/judge/tools/judge.py show N` resolves each row to its wiki page (title + URL, committed as batches/shard_N.src.jsonl), fetches the FULL page text live, and prints `idx|page title|lead start ## evidence sentences from the whole page`. Needs network (wikis in tools/wikis.tsv). Use `show N 0 80` for parts. `@@Heading:` shows the page's whole Abilities/Powers/Spells/etc. sections (subsections included, up to 1500 chars). Evidence is a keyword hint only: read the page text (tools/pages.py text(url)) before deciding a being has no powers.
2. Decide per row, then ONE `judge.py write N '<json>'`; it validates and writes shard_NN.out.jsonl and lists problems by idx. Fix and re-run (it overwrites).
3. Commit + push plans/powers/judge/out/shard_N.out.jsonl to your own branch (Global-Repo). Resolve the thread.

## Rules (unchanged)
- Page by page, exact source page = the row id (`wiki|lead_idx`). Quote must be verbatim from the text; no quote, no power.
- Beings (b1): named individuals only. Plurals, types, species, groups, titles, concepts, disciplines, episodes, missions, camos, perks, attachments and junk fragments ("Dr.") are b0.
- Non-beings are linked but NOT assayed (b0), EXCEPT weapon, armor, vehicle: b2 with kind, one overall magnitude m 1-10, quote, confidence. Plain firearms/cars = 1.
- Powers p only from pool ids in plans/powers/POWER_POOL.tsv, magnitude on the C3M scale: 1 peak human, 2 city block, 3 building, 4 city, 5 mountain, 6 island, 7 ocean/continent, 8 moon, 9 planet, 10 star/universe. Rare; most lead texts state none. Non-pool abilities go in x (short tag).
- No Anthropic API. Do not hand-claim shards; never write another thread's shard.

## Output per row (spec: plans/powers/JUDGE_PAGES.md S6975 + POWER_POOL README + c3m scale)
`id, b, n, p[{id,m,q,c}], x` as in JUDGE_PAGES.md; plus `u` source page URL (auto from src, write refuses rows with none), `s` short summary (default first sentence of the lead; pass `"s":{idx:"..."}` to override), `t` page title. Quotes are checked against the FULL page text.

## write JSON
`{"d":0, "b1":[idx..], "n":{idx:"name"}, "p":{idx:[["flight",5,"verbatim quote","h"]]}, "W":{idx:["weapon|armor|vehicle","name",m,"quote","h|m|l"]}, "x":{idx:["tag"]}, "auto":1}`
- d=0: unlisted rows are b0; use `"d":1,"b0":[idx..]` when most rows are beings (list the non-beings instead).
- Name is auto-taken from the first words before ` is/was/(/,`; if the helper reports "name not in text", add it to `n` (use "" when the name is stripped).
- `auto":1` adds x vampirism/possession by regex (WoD shards; check for false positives like "vampire hunter").

## c3m (c3m.zip, assay-c3m/SYSTEM_PROMPT.txt)
Optional `f` per being: [[AP|Dur|v, verbatim quote]] for a stated physical number with unit (energy, mass/speed, size, distance/time). Game damage numbers (e.g. 13875 Shadow damage) are not SI feats: leave `f` empty. `st` = source type from c3m SOURCE_BIAS (`game` for game wikis). c3m itself (inference.py/measure.py) does all arithmetic later; judges never compute tiers.

## Validator (S6985): mandatory
`python3 plans/powers/judge/tools/validate.py N` runs automatically at the end of `judge.py write`. Push ONLY shards that print PASS (rejected shard = fix and re-write, never push). It re-fetches the pages and checks: source URL/title resolve and match the batch lead; every power/feat/gear quote verbatim in the page; required fields, pool ids, m 1-10, c h/m/l; non-beings carry no powers/gear; gear is weapon/armor/vehicle only; Abilities pages have a power, feat, x or `z:"none stated: reason"`; feat maths recomputed with c3m (measure.py/inference.py copies in tools/c3m_lib) plus a plain-math cross-check, input number present in quote; shard totals (out/shard_N.meta.json) recounted. `python3 tools/selftest.py` shows it rejecting 11 deliberately broken variants. Fold: `validate.py all`; cloud/tools/powers/merge_judged.py refuses any judge/out shard that fails.

## Worker notes (from the first 5 workers)
- One shard per worker (250 rows ~ 45-55k tokens). Rows with no source page need config key `"u0":{"idx":"reason"}`; the validator allows at most 2%.
- Script section extraction (Powers/Abilities/Skills/Battle/Attacks headings) from the cache; the pool keyword regexes are in POWER_POOL.tsv column index 6 and are noisy and miss tabletop Discipline/Gift names.
- Name not found (e.g. \xa0 in the lead): set it in `n`. Gear name case must match the page.
- Discipline/Gift to pool-id mappings (Celerity -> super_speed etc.) are judgement calls: m=1, c=l.

## Resolver causes and ABSENT rule (pages.py, held-shard fix)
Rows left without a source page had these causes, all fixed in `pages.py resolve`:
1. Request errors (429) were swallowed, so whole batches silently stayed unresolved. `lookup` now retries 4 times and counts failures.
2. Page title is a shorter form of the lead name (Su-37, ATC Tango, singular): candidates are word spans of the name, parentheticals unwrapped, plus singular.
3. Template rows (`{{... Template | ...}}`): candidates come from Image stem (with `(Earth-616)` qualifier), Name/nam/MainPage/CurrentAlias/LegacyNumber/Title, rom/dub, and the subject of Overview.
4. Name stripped from the row (wikilink removed): search several windows of the text, quoted and unquoted, and accept the page that contains >=40% of the row's 4-word shingles.
5. An empty page on the first host no longer wins over a matching page on the second host.
ABSENT RULE: if every lookup and search ran with no request error and still nothing matched, the page is gone from the wiki. The resolver writes `batches/shard_N.absent.json` (row ids) and `validate.py` does not count those rows toward the 2% cap. Judges still mark them `b0` with `z="no source page: <reason>"`. Any request error removes the file, so a flaky run can never excuse rows.
