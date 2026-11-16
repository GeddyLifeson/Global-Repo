# Parallel batch 11-09: V1_CHECKLIST items with no client or full-pack boot needed

Source: plans/V1_CHECKLIST.md (this branch, GR claude/project-thread-wx17x3). Every job: read the checklist lines for its ids, work only those, tick with the Evidence the item names, push after each change, quiet thread, hand off at 125k. Items that already say PARTIAL 11-09 have a running lane (B3, B5, B13): do not start a second thread on them. Excluded as owned: N1/N3 shard judging, A7-A9 merge-safe lane, E*/C3-C9/G-FULL/F10/H-test items (need PC boot).
Where a code fix (D items) normally needs an in-game check, the job does the code fix plus a headless or unit check and leaves the in-game tick UNTESTED for the PC lane.

## J1 Merge and PR hygiene (A2, A4, A5, A6, A9, A10, A11)
Files: GR PRs #115 #116 #117 #65 #66, merge-safe/merge-order.csv (branch zuc996), merge-safe-config.json. Done: each PR has Bible check output, no dirty PRs in ports/RPG/GR, #223 on skip list, superseded PRs closed. Merges themselves are Marlon's Merge Safe click.

## J2 Compile (C1)
Files: plans/COMPILE_STATUS.csv. Done: 0 FAIL on cloud JDK 25 (2 FAIL, diaithir-claims). Then C2 pack rebuild into a throwaway dir with refresh_index.py.

## J3 Pack licences and packaging (B2, B7, B9, B10, B11, B12, B14, B15)
Files: pack.json, MOD_REMOVALS.json, LICENSES.md. Done per item as written in the checklist.

## J4 Code fixes A (D1, D2, D3, D4, D5, D6)
Superman grant, gate rite, tank Space fire, Tool Belt ItemDisplayContext, narrow-gauge payload, /diaithircargo. Done: fix merged, headless/unit check output; in-game left UNTESTED.

## J5 Code fixes B (D7, D8, D9, D10, D11, D12, D13, D16, D17)
Trade screens, capitalised fauna ids, Better Animations hook, animation crash, keybinds/options override files, NeoOrigins, Occlusion NPE, Offgrid, wave head failures.

## J6 Ages data (F11, F12, F13, G67)
Files: tech_items.json, AGE_BALANCE.md, ITEM_ROLES.csv. Done: Age tables agree, depth within band, 0 strict orphans, boss items have roles. Needs A8 for F11 only if tables are on unmerged PRs; start from the branch.

## J7 Ages F1-F9 data side
Per-Age anchor tech and gated items checked by script against tech_items.json; in-game tick left UNTESTED.

## J8 Megamachines code (H23, H11-H16, H19-H22 code side)
Merge #224 #265 #286 and Global #27, run MegaSelfTest headless. Done: C1 clean, MegaSelfTest PASS. H item in-game ticks stay UNTESTED.

## J9 Progression and encounters (I0, I16, I19, G64)
check_progression.py exits 0 on the pack data (188 nodes, 15 systems, 225 resources); station recipe audit; Global Events hooks for bosses.

## J10 Panscriptum and Codex (J2, J7, J8, J10, J11, J12, J16)
Files: plans/PANSCRIPTUM_MASTER.tsv, parity checker. No invented entries; source page text only. J8 needs A5/A6 merged first.

## J11 Economy, rites, drinks, misc (L1, L2, L7, L11, L12, M2, M7, P1, P3, Z5)
Economy retest data side, real-economics port (BskW #151), rites list, drinks recipes, textures with lang key but no model, antislop gate, compute ledger, stallcheck S-id, Bible check on deliveries.

Marlon-only: A8 merge click, A12 storage clear-out, E0 already lifted (11-05 18:09Z), Z6 acceptance.
