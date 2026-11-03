# MUNITIONS: ordnance manufacturing as evolution chains (draft 1, 2026-11-03)

Answer to "shouldn't there be weapons manufacturing for the missiles and bombs on boats, planes and trains": yes. Same pattern as BUILDING_MATERIALS.md: each line is one chain that changes form through the Ages, every stage a PROGRESSION node (`needs`, `makes`, `age`, `module`, `q.<id>`), gated by `gate.<Age>`, SI units (UNITS.md), upgrade slots (UPGRADES.md). Game content only: crafting machines, recipes and item stats. No real-world process detail goes in any recipe, Codex text or Panscriptum entry. No new jar: stages fold into existing modules (Foundry/tech machines, Keelwright mounts, diaithir-arms vehicle packs).

Age names: I Ancient, II Ailean, III Holy, IV Sundering, V Strangers, VI Kingdom, VII Dubhan, VIII Future, RODOS. Placement is a first proposal; tech-by-age.md wins on conflict.

## 1. Chains (output is a shared `c:` tag so mounts and vehicles accept it)
| Line | I | II | III | IV | V | VI | VII | VIII / RODOS |
|---|---|---|---|---|---|---|---|---|
| Propellant | charcoal mix | saltpetre pits, black powder | corned powder | nitrated cellulose | cordite-type stick | stabilised double-base | composite grain | shard-fuel cells |
| Shot and shell (ships, tanks, field guns) | stone shot | cast iron ball | grape and chain shot | explosive shell (fuse) | steel shell, armour-piercing | high-explosive and smoke | guided and proximity shell | shard shell |
| Incendiary | pitch arrows | Greek fire siphon | fire pots | incendiary shell | napalm-style gel | cluster incendiary | thermobaric-style | plasma |
| Rockets | fire arrows | war rockets | rocket frames | stick rockets | spin-stabilised rockets | rocket pods | guided rockets | shard rockets |
| Bombs (aircraft, airships, siege) | thrown pots | powder kegs | fused bombards | contact bombs | aerial bombs | cluster and guided bombs | smart bombs | orbital rods |
| Torpedoes and mines | log mines | powder kegs on floats | spar torpedo | self-propelled torpedo | magnetic and acoustic torpedo | wire-guided | homing torpedo | shard torpedo |
| Missiles | none | none | none | early guided rocket | wire/radio guided | heat-seeking | radar-guided, fire-and-forget | shard missile |
| Railway ordnance | none | none | none | rail-gun carriages (shell) | armoured-train mounts | rail-mounted rocket batteries | rail missile car | rail shard cannon |

Early rows (I-III) double as the player's first ordnance; later stages never delete earlier ones (same evolution rule as BUILDING_MATERIALS: old stages stay craftable at lower speed and quality, refit raises throughput and lowers W per kg).

## 2. Production machines (Foundry/tech module; one machine family per step)
1. **Powder works** (propellant), **filler station** (explosive/incendiary fill), **casting and forging bay** (shot, casings), **fuze bench** (fuzes, seekers), **guidance bench** (VI+ electronics from the tech chain), **assembly line / munitions yard** (final round, bomb, torpedo or missile on a pallet). Each step is a recipe with items in and out; no real process shown.
2. Intermediate items by stage: casing, propellant charge, filler, fuze, guidance pack, motor. The final **round** item has stats: mass kg, blast energy J, range m, guidance tier, Age.
3. **Magazines and storage**: armoury block with a capacity in kg; ammo hoppers feed Keelwright magazines and vehicle racks. Crew jobs (SHIPBUILDING Crew) haul rounds when no belt feeds them.
4. **Safety rule in game**: filled rounds are volatile; stored in an unarmoured chest they can chain-detonate when the block breaks. Armoured magazines and spacing counter it. Quest teaches it.

## 3. Consumers and tags
- Tags: `c:ammo/shot`, `c:ammo/shell`, `c:ammo/rocket`, `c:ammo/bomb`, `c:ammo/torpedo`, `c:ammo/missile`, each with `/<age>` subtags; `c:propellant`, `c:fuze`, `c:guidance`.
- **Ships**: Keelwright weapon mounts (SHIPBUILDING step 7: Weapons + ammo + Ward Emitters) accept `c:ammo/shell|torpedo|rocket|missile`. OldCannons logic feeds the Weapons part set (licence check at wiring).
- **Aircraft** (#188), **trucks** (#189), **tanks** (diaithir-arms Immersive Vehicles packs): racks and bomb bays accept the matching tags; the yard API (#186) lets an assembly yard load rounds onto a vehicle.
- **Trains**: rail ordnance cars from the transport module consume the same tags.
- Economy: every round is a tradable good; selling needs a licensed company recipe (Bethesda-quest style, no switches). Settlements and Hostile Encounters (Enhanced Celestials port) use the same items so NPC fights match player gear.
- Panscriptum: names and descriptions only from real page text; Library entry and Codex quest per stage; names via the 130-culture pipeline.

## 4. Mod sources (mod-first rule; unverified, check before building)
| Need | Plan |
|---|---|
| Cannons, shot, ship ammo | OldCannons (in pack) first; Davinci has none (checked 11-02); VS Tournament port #140 for VS2 weapons |
| Rockets, bombs, missiles on vehicles | diaithir-arms Immersive Vehicles packs and Immersive Aircraft; check latest 26.1 builds, then ports |
| Production machines | existing Foundry and Create nodes; clean-room otherwise |
| Anything ARR | clean-room in the owning module |
Next step is a licence and 26.1 check per row (Modrinth dump), logged to CSV, then node entries in `graph.json` and `check_progression.py`.

## 5. Build order
1. Item and tag catalog plus round stats validator (data only, no Java). 2. Machines and recipes for Ages I-IV. 3. Ages V-VIII and guidance. 4. Hook mounts and vehicle racks. 5. Quests, Codex, names.

## 6. Open items for the coordinator
- Owner module for the machines (suggest Foundry/tech); Keelwright, aircraft, trucks and transport threads should read section 3 for tag names.
- Dropped for now: any realistic recipe detail, and WMD-class content beyond game-balance "shard" tiers.

## 7. Containers, feeding and animation (added 11-03 after Marlon's question)
Gap list, not yet built. Catalog so far covers rounds and their parts only.
- **Containers as manufactured items:** magazine (per weapon family, capacity in rounds), ammo box (bulk, kg capacity), belt and link (belt segments of N rounds), clip/speedloader, bomb rack and torpedo cradle. Made at the same stations: casing-style part (cast), link or spring part, one-step assembly. Each has a loaded and empty form; loading a container from rounds is a station recipe or an inventory action.
- **Tags:** `c:ammo_container/magazine|box|belt|clip`, with the weapon family as subtag, so guns and vehicle mounts accept the right ones.
- **Animation on firing:** per weapon the animation set needs fire, eject, reload, magazine swap, belt feed/advance, and cycle. This belongs to the animation renderer threads (ports #207, #209); this lane supplies the container items, their states (full, partial, empty) and the weapon-to-container tag map so animations can key off them. Vehicle mounts (ship, aircraft, tank, train) reuse the same states.
- Order: container catalog (data) first, then recipes, then animation hooks with the renderer threads.
