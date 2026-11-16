# J7 Ages F1-F9 data side (11-09): BLOCKED on source files

Source of truth (kubejs/data/diaithir_tech/tech_tree.json, tech_items.json 7,601 items, content/tech_ages.json, content/ages.json) is not in any cloud repo or /mnt/project-files. It lives in the pack / on the PC (canon/eras.csv is PC-only too). So the per-Age anchor-tech check against tech_items.json cannot run here. No F item ticked.

## What could be checked (stale snapshot, builds/ancient-crops/tech_ages_v3.json, not authoritative)
Items per Age: I 1153, II 4824, III 4255, IV 1800, V 372, VI 718, VII 102, RODOS 41, **VIII 0**.
- F9 Rodos: 41 gated items matches the spec (41). OK in snapshot.
- F8 Future (VIII): spec says 70 gated items, snapshot has 0 and no VIII in its order list. Matches the checklist note that VIII rows are not yet added (eras.csv has only I-VII; spec in /mnt/project-files/ages/FUTURE_RODOS_ROWS.md).
- F1: canon eras.csv (copy in project files) has I-VII only; no Age content files found, as F1 already says.

## Needed to finish (PC lane)
Run on the PC repo with the real files: for each Age, anchor tech exists in tech_tree.json, count of gated items in tech_items.json equals spec (VIII 70, RODOS 41), civics present. Then tick F2-F9 data side; in-game ticks stay UNTESTED.
