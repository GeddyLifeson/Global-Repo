# J7 Ages F1-F9 data check on the PC (2026-11-09)
Source: pack branch `claude/pack-v1-3-wave17` of diaithir-ports: `kubejs/data/diaithir_tech/tech_tree.json` (851 techs) and `tech_items.json` (7,601 items, 180 namespaces). Not found on the PC: `content/tech_ages.json` (only its generated copy `kubejs/server_scripts/diaithir/tech_ages_data.js`, order I-VII + RODOS, no VIII), `content/ages.json`, `canon/eras.csv`.

| Age | techs in tree | items gated explicitly | pop |
|---|---|---|---|
| I | 114 | 1149 | 1 |
| II | 115 | 575 | 4 |
| III | 154 | 2769 | 10 |
| IV | 134 | 1844 | 25 |
| V | 94 | 386 | 60 |
| VI | 127 | 721 | 150 |
| VII | 82 | 38 | 300 |
| VIII | 15 | 73 | 400 |
| RODOS | 16 | 46 | 500 |

Plus namespace-default gating (31 II, 30 III, 24 IV, 20 V, 40 VI, 32 VII, 1 VIII, 1 RODOS, 1 I).

## F8 Future (VIII)
- Anchor tech `fusion_power`: PRESENT, era VIII. Civics `star_concord`, `synthetic_accord`, `paracausal_ethics`: PRESENT, era VIII. `eraNames` has VIII Future, popByEra VIII = 400 (spec 400).
- Gated items: 73 explicit in tech_items.json vs spec 70 (3 more). Not equal, so F8 data side is NOT ticked.
- `tech_ages_data.js` order has no VIII (stale generated copy); `content/tech_ages.json` and `canon/eras.csv` are not on this PC.
## F9 Rodos
- Gated items: 46 explicit vs spec 41 (5 more). Civics rodos_accord, keepers_of_the_shard, second_dawn present. Not equal, NOT ticked.
## Defects found
- Duplicate tech ids in the tree: `nanofabrication` (x2), `allthemodium.RODOS` (x2), `productivebees.RODOS` (x2).
- Namespaces VIII/RODOS carry only 1 namespace default each.
## Evidence command
`git show claude/pack-v1-3-wave17:kubejs/data/diaithir_tech/tech_tree.json` then count techs by `era`; items by `techs[v].era` or the `.ERA` suffix of the tech id in `tech_items.json`.

## Addendum: files found in the repos (2026-11-09)
Found: DiaithirRPG `content/tech_ages.json` (16,604 items, 335 namespaces, order has VIII), `content/ages.json`, and diaithir-laptop `canon/eras.csv`.
- `eras.csv`: rows I-VII only; no VIII row and no RODOS row (spec in FUTURE_RODOS_ROWS.md is not applied). F8 and F9 canon rows: MISSING.
- `content/ages.json`: ages TELLING and I-VII only; no VIII or RODOS entry.
- `content/tech_ages.json` items per Age: I 2012, II 5046, III 4985, IV 2753, V 623, VI 897, VII 136, VIII 88, RODOS 64; namespace defaults VIII 2, RODOS 1.
- Three sources disagree on gated items: pack `tech_items.json` VIII 73 / RODOS 46; content `tech_ages.json` VIII 88 / RODOS 64; spec VIII 70 / RODOS 41. None equals the spec, so F8 and F9 data stay UNTICKED. The content file is the input and the pack file is its older output, so the pack needs a rebuild once the spec number is settled.
