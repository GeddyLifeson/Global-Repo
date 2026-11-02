# PROGRESSION: one dependency web, finished only by touching every system (Marlon 11-02 23:16)

Goal: a solo player, like in Factorio, cannot finish the modpack without using every part of it. Every system makes things another system needs, the Ages tree gates the order, and the run ends at one win: **Open the Shardfall Gate** (the pack's rocket launch). The server still has everything. No on/off switches; each step reaches the player as a Codex quest (Bethesda style). Sources: INTEGRATION.md, UNITS.md, UPGRADES.md, FACTORIO_TECH.md, SHIPBUILDING.md, ASCENDANT.md.

Machine-readable source of truth: `graph.json` (182 nodes, 15 systems, 225 resources). Checker: `check_progression.py` (S-ID in Global-Repo). Cross-mod recipes: `datapack/`.

## 1. How the web works
- A **node** is one thing a player does or builds. It has `needs` (resources), `makes` (resources), an `age`, a `system`, a `module` (which jar owns it), a quest id `q.<node id>`, and optional `item`, `W` (watts drawn) and `s` (job seconds), in SI per UNITS.md.
- A **resource** is anything passed between nodes: an item tag (`c:ingots/steel`, `c:plates/iron`, following INTEGRATION.md section 1), a service the player has built (`power.grid`, `ward.field`, `depot.network`), or a state (`settle.town`). Two nodes making the same resource are **alternatives**; one is enough.
- **Age gate.** Every node of Age II or later also needs `gate.<Age>`, made by a chain of `research.gate_*` nodes. Each gate needs the previous gate and the newest research pack. The packs come from other systems (below), so research cannot be skipped either.
- **The win** needs the apex product of every system. The checker proves that removing any one system makes the win unreachable.

## 2. The chain, by system
| System | Nodes | First Age | Feeds N systems | Fed by N systems | Owner thread |
|---|---|---|---|---|---|
| Tech (Foundry) | 30 | I | 14 | 7 | foundry |
| Research (#127) | 16 | I | 3 | 9 | foundry |
| Upgrades (#117) | 9 | III | 5 | 7 | upgrades |
| Magic (Celtic) | 12 | I | 11 | 8 | consolidation |
| Food and cooking | 10 | I | 9 | 5 | consolidation |
| Farming | 12 | I | 11 | 5 | rewrite-blocks-decor-farming |
| Creatures and animals | 8 | I | 9 | 6 | mobs |
| Combat and bosses (Ascendant #125) | 13 | I | 8 | 6 | rewrite-combat-classes |
| Storage and logistics | 9 | I | 6 | 5 | rewrite-storage-logistics |
| Transport and rail | 11 | II | 4 | 6 | transport |
| Ships (Keelwright) | 13 | II | 6 | 11 | keelwright |
| Economy and companies | 11 | I | 4 | 10 | economy |
| Settlements | 9 | I | 4 | 12 | settlements |
| Cultures | 8 | I | 5 | 8 | culture-start |
| Exploration and worldgen | 10 | I | 13 | 7 | rewrite-worldgen-structures |

| Age | Nodes |
|---|---|
| I | 18 |
| II | 15 |
| III | 26 |
| IV | 19 |
| V | 17 |
| VI | 27 |
| VII | 33 |
| VIII | 10 |
| RODOS | 17 |

Apex product each system must deliver to the Gate:

| System | Apex resource | Made by |
|---|---|---|
| Tech (Foundry) | `resonator.shard` | tech.shard_resonator (Age RODOS) |
| Research (#127) | `research.pack_7` | research.pack_7 (Age RODOS) |
| Magic (Celtic) | `focus.shard` | magic.shard_focus (Age RODOS) |
| Food and cooking | `feast.ages` | food.feast (Age VIII) |
| Farming | `farm.living_seed` | farm.living_seed (Age RODOS) |
| Creatures and animals | `creature.menagerie` | creature.menagerie (Age VIII) |
| Combat and bosses (Ascendant #125) | `rush.cleared` | combat.rush (Age RODOS) |
| Storage and logistics | `depot.global` | store.global (Age VIII) |
| Transport and rail | `trans.orbital_link` | trans.orbital (Age RODOS) |
| Ships (Keelwright) | `ship.shard_ark` | ship.ark (Age RODOS) |
| Economy and companies | `treasury.shard` | econ.treasury (Age RODOS) |
| Settlements | `settle.capital` | settle.capital (Age RODOS) |
| Cultures | `accord.rodos` | culture.accord (Age RODOS) |
| Upgrades (#117) | `module.legendary` | upgrade.legendary (Age RODOS) |
| Exploration and worldgen | `shard_land.access` | explore.shard_land (Age RODOS) |

## 3. The interlocks Marlon named, and where they sit
- **Magic needs foundry alloys.** `magic.circle` (altar) takes silver, `magic.altar_adv` takes steel, wax and an ogham module; `magic.field_ward` needs circuits and the grid; `magic.dust_rite` needs lamp dust from `tech.lochrand` (the real Lochrandraoidheachd bridge).
- **Tech needs magic.** `tobardealain` feeds mana to the grid at 100 J per quantum (UNITS.md); the fusion core needs `module.t3`, and the Rodos resonator needs slagiron from the Cinderfen.
- **Machines need food-fed workers.** `tech.operator` (the Operator seat) needs `ration.worker` and a settlement population. Advanced circuits need a seated operator, so no advanced tech without the kitchen and a town. Ships take hired crew fed by the same rations.
- **Bosses drop catalysts the factory needs.** `boss.catalyst` gates research pack 5 and tier 3 modules; `boss.hollow_core` gates the fusion core and pack 6; `boss.ageshard` (Last Wheel) gates the shard resonator, pack 7, shard focus, the shard land and legendary modules. Summons are ritual: `magic.summon` needs an altar, a rite focus and an **offering feast** from the kitchen (`food.offering`, which needs cold store from the tech tree).
- **The factory attracts the hive.** `creature.burrowkin` needs an assembler running (Unrest) and turrets; its chitin goes into hollowsteel armour and its jelly into quality grading (`upgrade.quality`).
- **Ships need everything.** Keelwright hulls need wood, fibre, pitch, plates, circuits, the grid, mana wards, rations, crew, aircraft engines, nanoalloy, a fold drive and the shard resonator.
- **Economy closes the loop.** A company (`econ.company`) needs a bank, a civic hall, a warehouse and research pack 3 (the quest-founding rule from memory). Company lines run trains (`trans.company`), and the exchange needs bulk farm output, sea and rail trade, and a depot network.
- **Cultures and settlements.** Your culture gives script (magic, pack 1), currency (coin), dishes (cuisine), architecture (town) and envoys (civics, accord). Settlements need irrigation, roads, walls, a port, a hall, cities need depots, dispatch and wards, the capital needs cold store, the exchange and the Rodos accord.
- **Upgrades touch every theme.** Ogham and spice modules at Age III, circuit modules at Age VI, tier 2 and 3 after circuits and a boss catalyst, quality after the Reclaimer and Burrowkin jelly, legendary after the boss rush.

## 4. Solo rule
- Every step is completable alone. Co-op nodes are flagged `coop` and must have a solo alternative making the same resource. Today: `econ.player_market` (co-op) beside `econ.npc_market` (solo), both making `market.liquid`.
- Other cultures are NPC envoys (`culture.envoys`), crew is hired NPC crew, settlement population is NPC. Boss HP scaling by player count (ASCENDANT.md) stays; solo is the base case.
- The checker fails the build if any resource has only co-op makers.

## 5. The checks (`python3 -I check_progression.py graph.json --report [--datapack DIR]`)
1. Every need has a maker; nothing is made that nothing uses (a node may list `terminal` resources on purpose).
2. Solo fixpoint: starting from nothing, every non-co-op node becomes reachable, so there are no cycles or dead branches.
3. Age order: no node needs a resource first made in a later Age.
4. Every system is required: remove it and the Gate is unreachable.
5. Every system feeds at least 3 others and is fed by at least 3.
6. Units: `W` and `s` are positive numbers; data pack recipes match the graph item and map to real resources.
Threads run it before delivering any change that touches a node, and update `graph.json` in the same PR. A fold or rewrite that renames an id must keep ids (INTEGRATION.md) or migrate the graph row.

## 6. Cross-mod recipes (`datapack/`, generated by `gen_progression_recipes.py`)
- 41 shapeless recipes, one per node with an `item`. Inputs are `c:` tags where the convention has one, else the tag `diaithir:progression/<resource>` (40 tags, empty, for the owner threads to fill with their items). Vanilla world sources map to vanilla tags. Services (power, wards, settlements, maps) are not ingredients; they are quest or placement conditions.
- Every recipe carries `neoforge:conditions`: the result item must exist and every progression tag must be non-empty. Until a module ships the item and fills its tag, the recipe is silently off, so the pack loads clean today.
- The 30 `item` ids marked `item_proposed` are suggestions in the module's own prefix (`foundry_` for tech, research, upgrade, storage). The owning thread keeps or renames them in `graph.json` before the item exists; after that ids never change.
- Quantities are 1 per input in this first pass. Owners balance counts, and give working blocks `W`/`s` in watts and seconds.

## 7. Deviations and open items (stated so nothing is claimed that is not there)
1. **Module ages.** UPGRADES.md puts tier 1 modules at Age III for every theme. Ogham and spice modules are at III here. Circuit modules and beacons are at VI because circuits and the grid do not exist earlier. Upgrade thread confirms or moves the grid earlier.
2. **Rodos is Age 9.** The ASCENDANT.md text says "Rodos (Age 8)"; the eras spec says VIII Future and RODOS 9. This plan uses VIII and RODOS.
3. **Not built:** Operator seat, Unrest, Gate rite, the quest files, the research-bench Age nodes, and all Java glue. This PR is the plan, graph, checker and dormant recipes.
4. **Quantities and balance** (item counts, W, J, L per node), Age years on the shared calendar, and the 130-culture names are owner work.
5. **Win ceremony** (what the Gate does, the credits scene) is a design task for the Codex and campaign threads.
6. No in-game test has been run. The checker proves graph shape only; the PC lane tests recipes once items exist.

## 8. What each thread does next
- **Foundry:** tech and research nodes: Operator seat, research bench Age nodes (`research.gate_*`, packs 1 to 7), `foundry_` ids, W and s per machine.
- **Upgrades:** theme modules, quality, beacon and planner rules against the Ages above; confirm the VI deviation.
- **Consolidation:** magic and food nodes live in the merged modules; fill progression tags for them; add the matrix columns "progression node".
- **Rewrite threads:** farming (greenhouse, auto harvest, living seed), combat (arms ladder, turret, bosses), storage and logistics (depot, plan table, global depot), worldgen (ores by Age, Thornwake, Cinderfen, the Unwound, shard land).
- **Ascendant:** drops `boss.catalyst`, `boss.hollow_core`, `boss.ageshard`; summon needs `ritual.summon_ready`.
- **Keelwright:** the ship parts per Age; space hull needs the nanoalloy, crew and anyseason crops.
- **Economy, settlements, cultures, transport, mobs:** their rows in `graph.json` are the quest chain order.
- **Kept-mod integration:** shim rules and tags for third-party mods that fill the same resources (c: tags), plus rules that no kept mod gives a shortcut around a node. If one does, add it as an alternative maker or remove it.
