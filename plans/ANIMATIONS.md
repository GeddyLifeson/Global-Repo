# ANIMATIONS (V1 scope, Marlon 11-03 18:45-18:46: "animations for literally everything and anything")

Home: client module `diaithir-entity-animation` (already in the consolidation plan, 5 mods in, 24 effort days). No new jar. Coverage is tracked in `ANIMATIONS_COVERAGE.csv` (one row per thing, status todo/route/done).

## Routes (mod-first rule), from PACK_CONSOLIDATION_AUDIT.csv
| Piece | Mod | Licence | Route |
|---|---|---|---|
| Player anim engine | Player Animation Library 1.2.8 | MIT | keep, our animations build on it |
| Model anim engine | GeckoLib 5.5.2 | MIT | keep, used for mobs, bosses, machines, vehicles |
| Emotes | Emotecraft 3.3.0 b164 | GPL3 | merge_port into module |
| Entity models / textures | Entity Model Features, Entity Texture Features | LGPL-3.0 | merge_port |
| Vanilla-body anims (eating, bow draw, climbing, sneaking, riding, held items) | Not Enough Animations | tr7zw Protective (ARR) | clean-room rewrite; EMF Compat (GPL-3.0) is open but only a shim |
| First-person body | firstperson | tr7zw Protective (ARR) | clean-room rewrite (lives in diaithir-client-view-input, shares the pose layer) |
| 3D skin layers | skinlayers3d | tr7zw Protective (ARR) | clean-room rewrite |
| Weapon swing anims | Better Combat | ARR | clean-room, already in diaithir-combat-arms; reuse the same pose layer |
| Gun handling | Vic's Point Blank | ARR | clean-room, ties to firearms #158 |
| Candidates still to check on 26.1 + licence | Custom Player Animations (NeoForge 26.1.2 listed), Player Animation Core (26.1 unconfirmed), Eating Animation (NeoForge fork), Punchy (26.1.x), ParCool + Epic Fight (26.1 not confirmed) | unknown | verify licence on the page; fold if open, else our own |

## Own content to animate (all on the Player Animation Library layer, one stack, no conflicts)
Firearms and tanks (#158), combat-classes skills, Ascendant boss attacks and rites, Celtic rite casting, Keelwright piloting, Foundry operator seat, Immersive Vehicles seats and controls.

## Inventory (coverage rows, generated per category)
1. Player actions: walk/run/sprint/sneak/crawl/swim/climb/ladder/glide/fall/land/ride/sit/sleep/emote, use item, eat/drink, bow/crossbow/trident, block, mine, place, interact, open container, fish, brew.
2. Weapon and tool swings per class (sword, axe, spear, mace, hammer, staff, dagger, pick, shovel, hoe, shears), gun hold/aim/fire/reload/inspect, class skills.
3. Mobs and animals, bosses (idle/walk/attack/hurt/death/rite), NPCs by profession (work, talk, trade, sit).
4. Machines and blocks: every working block (idle/working/done), doors, chests, levers, tanks, turrets, Foundry belts.
5. Vehicles: ground, boat, aircraft, ship, seats, driver hands, wheels, propellers, hatches.
6. Rites and magic casting, ship piloting, operator seat.

## Order
1. Pose layer (Player Animation Library) + vanilla body anims clean-room (fold of NEA and firstperson ideas).
2. Combat swings, then guns.
3. Own-content animations, category by category, driven by the coverage CSV.
Tests: headless server boot plus single-mod client join in the cloud; no full-pack PC join until consolidation finishes.

## Open
Coverage CSV is generated from the live content lists (mobs, NPCs, blocks, items, vehicles) by a script to be registered in Global-Repo; helper threads per category are requested from the coordinator.
