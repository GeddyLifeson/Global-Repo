# F11-F13 status (2026-11-09)

## F11 Ages
- CMD: `noage.py` patched to read `namespaces` from EXTRA_AGE_JSON too, run on ports `claude/pack-v1-3-wave17` kubejs + DiaithirRPG `content/tech_ages.json` @851ef02: `no-age ids: 0 of 47200` (was 5,871 without the namespace patch, 5,989 at the audit).
- The audit's "324 conflicts" compares an Age letter in `tech_ages_data.js` with a tech name in `tech_items.json` (steel, alchemy, copper). Real Age-vs-Age conflicts between those two tables: 3 (musketmod:cartridge, casinodeco:glass_table, casinodeco:glass_coffee_table); the engine table already holds the `tech_ages_data.js` value for all 3. The engine table has 79 deliberate overrides of either source (e.g. energizedpower upgrade modules VII to VIII). Engine `content/tech_ages.json` is the single source; 0 invalid Age values.
- NOT DONE, UNTESTED: removing the 273 table ids that name no item. The universe is the wave15 jar snapshot; 934 to 1,274 table ids per table are absent from it inside known namespaces, many are generated variants, so absence here does not prove nonexistence.

## F12 Balance
- `AGE_BALANCE_MATRIX.csv` regenerated from the current progression graph (287 nodes: I 30, II 22, III 30, IV 31, V 32, VI 44, VII 52, VIII 24, RODOS 22; all within 50% of the I-VII median 31).
- Recipe counts per Age are not measured by `age_balance.py`. Thin cells (under half the row median, decor excluded): I 3, II 9, III 1, IV 1, V 8, VI 4, VII 7, VIII 13, RODOS 14. VIII and RODOS items, structures, textures and Library are still thin. Not at the band: F12 stays open.

## F13 Item roles
- CMD reproduces the audit: 17,850 items in no recipe, loot or trade; 2,164 strict orphans.
- 617 of them already had an ITEM_ROLES row. Added 601 rows (579 spawn eggs, 22 technical/UI items) under the assumed default that spawn eggs and technical items are admin/UI items, not survival items (UNTESTED, Marlon can reverse).
- 946 strict orphans remain with no role (`ITEM_ROLES_ORPHANS_OPEN.csv`): aerialhell 156, diaithirworldsys 79, eternal_starlight 65, the_backwoods 64, undergarden 63, morered 59, untamedwilds 49, alexscaves 46, 46 boss items. Each needs a real role from the mod's own source or a Java-drop LOG line. No invented rows. F13 and G67 stay open.
