# Magic vs tech balance and NPC innate abilities (2026-11-04)

Sources: plans/AGE_BALANCE_MATRIX.csv (11-03), plans/progression/graph.json (199 nodes), codex-store/library.sqlite (realm field; keyword counts over name+summary, so upper bounds), quests-panscriptum/quests.sqlite. No Haiku batch was needed; everything came from existing tables.

## 1. Pack: magic vs tech
| Measure | Magic | Tech |
|---|---|---|
| Progression nodes (graph) | 12 (6%) | 31 (16%), plus 11 upgrade and 25 gear/munition nodes that lean tech |
| Mod items by function | 2,778 | 7,158 machines + 2,558 storage |
| Peak Ages | III 856, IV 1,720 (93% of all) | V 2,183, VI 3,844 (84% of machines) |
| Age V / VI | 8 / 8 magic items, 0 nodes at V | strongest |
| Age I / II | 120 / 1 | 10 / 142 |
| Age VIII | 0 nodes, 20 items | 2 nodes, 50 items |
Magic is front-loaded (III-IV), tech back-loaded (V-VI). Magic has a hole at II, V, VIII; tech has a hole at I and VII (66 machines).
Library lean is the opposite: Arcane 375k entries vs Stellar 80k, so lore is magic-heavy while built content is tech-heavy.
Bridges exist (Tobardealain mana to grid, Lochrandraoidheachd grid to dust, arcane_motor), so the two sides do talk.

## 2. Panscriptum NPCs and innate abilities
225,383 beings. Realm split: Arcane 121k, Mythic 28k, Stellar 27k, Grounded 25k, Ki 9.9k, Martial 9.4k, Outer 4.9k.
Only 1,062 beings carry a pack_id (all Arcane; mobs). No Ki, Mythic, Martial or Stellar being is bound to anything in the pack.
Text mentions (upper bounds): flight 7,768; ki/chi/aura 6,133 (6,064 in the Ki realm); shapeshift 1,019; regeneration 128; invisibility 56; telepathy 17; teleport 15.
Pack side: graph.json has no flight, ki, or innate-power node. NeoOrigins 2.2.30 is in the pack (picker plus Pre-kill patch), the natural host for data-driven powers, but I found no power data for these beings. Verdict: needed by roughly 6k Ki beings and several thousand flyers, not provided today.

## 3. Fixes (MOD-FIRST, no new jars)
V1 (data only):
1. Merge the 19 nodes in AGE_BALANCE_NODES.json (adds magic.alchemy V, glyphs VI, paracausal VIII). Owner: Age balance lane.
2. Add a small `innate` tag (flight, ki, shapeshift, regen) to the quest givers and shrine NPCs that actually spawn in V1, derived from the Library text plus realm, not invented. Flight for NPCs uses vanilla flying-mob AI; ki for NPCs is a flag on the entity.
3. Define ki as an energy: fold into the existing magic rate (100 J per unit), so it feeds the units layer and Codex with no new system.
4. Fill Age II magic: re-gate existing merged mods (Druidry #35, Roots) with tech_ages entries; no new content.
Post-V1:
5. NeoOrigins power data for flight, ki, shapeshift per culture or realm (player side too).
6. Ki techniques as a Pufferfish skill tree (CC0 data) tied to the Ki realm.
7. Tech Age I-II hand machines and VII machine items; magic Age V items.
8. Bind Ki, Mythic, Martial, Stellar beings to pack entities as the fauna lane matures.
