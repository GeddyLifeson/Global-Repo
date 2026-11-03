# MOD_SURVEY: existing mods for every project feature (2026-11-03)

Requested by Marlon 11-03 ("every feature, no matter how old"). Six search passes (vehicles/transport, combat/gear, logistics/tech, society/progression, world/nature/food, client/QoL/perf), about 240 features, any MC version or loader. Parts are in /mnt/project-files/mod-survey/; this file is their concatenation.

## How to read
- Target MC 26.1.2 NeoForge. Old-version mods are code or asset ports; the no-new-jars rule holds (port or fold into an existing diaithir-* module).
- Recommendation verbs: PORT, FOLD (into a named module), ADOPT (already usable on 26.1.2), CLEAN-ROOM (nothing usable or licence forbids).
- Licence: ARR, NC, ND, custom and source-available = no code port. Assets can differ from code (Ars Nouveau and Nature's Spirit: code open, assets ARR, so port code and redraw art).
- Method limits, stated honestly: Modrinth API was the main source. The GitHub API and CurseForge API were blocked, so CurseForge-only mods and some licences are marked unverified and were read from WebSearch/WebFetch pages where possible. Coverage percentages are estimates. Per-feature recall cross-check queued as compute job `mod_survey_recall` (230 rows, unverified recall, Sonnet).
- Ports PRs #107-#199 were not readable; features are matched from plans/*.md and MERGE_ORDER.csv titles.

## Headline changes to earlier verdicts
- Firearms, ammo/mags/boxes and gun animations are NOT clean-room: TaCZ and Superb Warfare (both GPL-3.0) are portable engines. Decision for Marlon: two gun engines (TaCZ plus diaithir-firearms) is one too many; fold the catalogue into one.
- Lane belts, splitters and inserters DO exist: Conveyors & Automation (MIT per Modrinth; NeoForge 1.21.1 to 26.3, no 26.1 build; repo licence unverified). Overturns the 11-02 "no lane belts" line.
- Ars Nouveau, Botania, Nature's Spirit: code is portable (LGPL-3.0 / Botania License copyleft / MIT); assets ARR for Ars and Nature's Spirit. Biomes O' Plenty, Productive Bees, Macaw's ARR families stay clean-room.
- Narrow and wide gauge trains: Create: Steam 'n' Rails (LGPL-3). Road vehicles, fuel, trailers: MrCrayfish's Vehicle Unofficial (GPL-3). Transport-Fever-style lines: Minecraft Transit Railway (MIT).
- Real gaps (clean-room confirmed): mega vehicles and megastructures (only IE's bucket-wheel excavator exists, redistribution banned), shared fuel API, assembly yards/cranes/containers/harbours, Age-evolving stations, NPC wages/strikes/revolts, civ tech-tree calendar, signal wires/combinators, quality/recycling, 3D skin layers (ARR/protective), headless real-network test client (use Mineflayer plus a small clean-room lane).
- Licence flags to confirm in jar files: First-person Model (Modrinth MIT vs audit "protective"), Building Gadgets 2, Millenaire, True Ending, Nerospace.



---

<!-- part1_vehicles_transport.md -->
# Mod survey part 1: vehicles and transport (2026-11-03)
Sources: Modrinth API (versions/licences/source URLs read from the API), cfwidget (CurseForge), raw GitHub LICENSE files, WebSearch. In-pack facts from plans/PACK_CONSOLIDATION_AUDIT.csv, SHIPBUILDING.md, FACTORIO_TECH.md, EXCLUSIONS.md. Not redone: Archimedes/Davinci/VS Tournament/Clockwork/Sable checks in SHIPBUILDING.md.
Limits: GitHub API (gh) is blocked here, so PRs #186-#194,#199 bodies were NOT read (titles unverified; plans mention only #186 = assembly yard API / diaithir-yards, #188 aircraft, #189 trucks, #187 Create addons age gate, #197 ships gate). Mods not on Modrinth (MCHeli, Flan's old, MTS legacy) checked by CurseForge/WebSearch only. "MC" = newest..oldest build; NeoForge target is 26.1.2.
In pack already (26.1.2): Create 6.0.9 diaithir.8 (MIT code, trains/signals/schedules/contraptions), diaithir-ships (VS2 + Eureka + VS Tournament ports), Immersive Vehicles (diaithir clean-room), Immersive Aircraft (GPL-3), Railcraft Reborn (keep), Minecart Trains Fork, Cargo Boats, Better Boat Movement, Horseman, Iron Jetpacks, Hang Glider, Yori3o Grappling Hooks, Modular Drones, OpenBlocks Elevator, Simple Teleporters Reforged, Waystones, Abridged.

## Road vehicles + vehicle physics (diaithir-vehicles)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Immersive Vehicles / MTS (Mr_Mulle) https://modrinth.com/mod/immersive-vehicles | 26.1.2..1.12.2 Forge/Neo | ARR | no | ~80% (cars, planes, parts, fuel, damage) | Already rebuilt clean-room as diaithir-vehicles. Dozens of content packs (OCP, UNU, IAV CC-BY-4.0 1.12.2-1.20.1, VEB CC-BY-4.0) are packs for it; CC-BY ones are pure data/models usable if our format reads MTS packs (unverified). |
| MrCrayfish's Vehicle Unofficial (bay4lly) https://modrinth.com/mod/mrcrayfishs-vehicle-unofficial | 1.21.1..1.20.1 Forge/Neo | GPL-3.0-only (original reported GPL-3 per ModDex; art stays MrCrayfish's) | code yes; assets no | ~50% (drivable cars, fuel pump/gas station, crates, trailers, damage) | Best code base for fuel pumps + trailers; retexture needed. |
| Automobility (FoundationGames) https://modrinth.com/mod/automobility | 1.21.1..1.18.2 Fabric/Forge/Neo/Quilt | MIT | yes | ~35% customizable cars, auto-engines, fuel-less | Small clean code; last build 2025-04. |
| Kuruma (jdmmc) | 1.21.1..1.20.1 Forge/Neo | GPL-3.0-only | yes | grip/suspension/drift physics only | Active 10-31. Physics model reference. |
| Limitless Vehicle (YWZJ) | 1.21.1..1.20.1 Forge/Neo | GPL-3.0-or-later | yes | datapack-defined vehicles | Active; data-driven vehicle format. |
| Flan's Mod Reloaded (jamioflan) | 1.20.1 Forge | MIT | yes | vehicles + guns toolbox | Large; relevant to tanks. |
| Fex's Vehicle & Transportation Mod, Plain Cars | 26.1.2..1.12.2 Fabric/Forge | custom (Fexcraft Common) | no | cars, trains, planes | Has 26.1.2 build but licence custom. |
| Ultimate Car/Plane Mod (henkelmax) | 26.3..1.10.2 | ARR | no | cars, roads, biodiesel | Already on EXCLUSIONS clean-room list. |
| Create Aeronautics (Simulated) https://modrinth.com/mod/create-aeronautics | 1.21.1 Neo | code MIT, assets ARR (verified LICENSE.md); depends on Sable (PolyForm Shield) | code only | cars, trucks, planes via physics | Sable API differs from VS2; rewrite onto VS2. |
Recommendation: PORT MrCrayfish's Vehicle Unofficial (GPL-3 code: fuel pump, trailers, vehicle crates) into diaithir-vehicles with our own art; keep Immersive Vehicles clean-room base. Kuruma physics as reference only.

## Walkable vehicle decks / moving structures (diaithir-ships, Create)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Valkyrien Skies 2 unofficial port (LumixTeam) | 26.2..1.21.1 Neo/Fabric | LGPL-3.0-only | yes (already ported) | ~90% walkable physics ships | Already diaithir-ships jar. |
| Create contraptions (in pack) | 26.1.2 | MIT | in pack | assemble blocks, ride them | Create Interactive (rubydesic, ARR, 1.20.1) gives walking inside; ARR so not usable. |
| Sable (ryanhcode) | 1.21.1 Fabric/Neo | PolyForm Shield 1.0.0 (verified) | no (source-available, non-compete) | sub-levels | Idea only. |
| Archimedes' Ships port (#128) | in progress | MIT | in pack branch | walking inside missing | Gap listed in EXCLUSIONS. |
| aleki's Nifty Ships | 1.20.1 Forge/Neo | MIT | yes | in-world built boats, walkable decks | Gitlab. Candidate for non-VS walkable boats. |
Recommendation: ADOPT VS2+Eureka (already ported); close the Archimedes walk-inside gap by FOLD of aleki's Nifty Ships deck logic into diaithir-ships if VS-free ships are wanted.

## Aircraft (diaithir-aircraft)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Immersive Aircraft (in pack) | 26.1.2 Neo | GPL-3.0-only | yes | gliders, biplane, airship, gyrodyne | Core. |
| Aviator Dreams Reloaded (in pack) | 26.1.2 | GPL-3.0-only | yes | real aircraft data | |
| Man of Many Planes | 26.2..1.19.2 | CC-BY-NC-SA-4.0 | no | extra aircraft | In pack list clean-room. |
| Simple Planes (SappyInsane) | 1.21.1..1.19.2 Forge/Neo | LGPL-3.0-only | yes | upgradeable planes + helicopters | Best port candidate for helicopter. |
| Ultimate Plane Mod | 26.3 | ARR | no | planes | |
| MCHeli (EMB4) | 1.12.2 | ARR (source obfuscated) | no; MCHeli Community Edition / Overdrive reported GPL-3 (unverified) | helis, planes, weapons | |
| Create Aeronautics | see above | MIT code | partial | propellers, balloons | |
Recommendation: FOLD Simple Planes (LGPL) helicopter/upgrade logic into diaithir-aircraft.

## Mega vehicles and megastructures (diaithir-ships)
None found as a dedicated mod. VS2 ships + Create Big Contraptions (MIT, 1.21.1) raise size limits; Huge Structure Blocks (LGPL-3, 26.3) is a build aid.
Recommendation: CLEAN-ROOM on VS2: Keelwright hull classes cover size; nothing to port.

## Semi trucks, trailers, construction vehicles
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Trin Civil Pack, RDNTrucks, UNU packs | 26.1.2..1.12.2 | ARR | no | truck models for IV | Content for IV only. |
| MrCrayfish Vehicle Unofficial | see above | GPL-3 | yes | trailers (hitch) | |
| Create: Tow & Haul | 1.21.1 Neo | ARR | no | towing | |
| Little Tractor (DragN0007) | 1.20.1 Forge | ARR | no | tractor | |
| Excavators (Pepsied, MIT 26.2) | | MIT | | actually tools, not vehicles | not relevant. |
Nothing found for excavators/bulldozers/dump trucks as vehicles (Pushdozer, Fabric MIT, is a push tool).
Recommendation: CLEAN-ROOM trucks/construction as IV-format content (#189 trucks in progress) with trailer hitch FOLDed from MrCrayfish Vehicle.

## Shared fuel API
None found as a standalone API. Fuel exists inside MrCrayfish Vehicle (GPL-3, fuel pump/tank), Immersive Vehicles (ARR), Create Liquid Fuel (ARR, 1.21.1), GasStation (1.7.10 custom). FuelInfo (Apache-2.0, 26.2) is only a tooltip.
Recommendation: CLEAN-ROOM a fluid-tag-based fuel capability in diaithir-vehicles (NeoForge fluid handler + `diaithir:fuel` tag) shared by vehicles, ships, aircraft; copy the pump/tank design from MrCrayfish Vehicle.

## Trains on two gauges + signal-block trains + Railway Empire/Transport Fever line management (diaithir-ground-water-transport)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Create trains (in pack, 6.0.9) | 26.1.2 | MIT | in pack | tracks, block signals, schedules, stations | Signals native. |
| Create: Steam 'n' Rails (Layers of Railways) | 1.20.1..1.18.2; unofficial 1.21.1 Neo (PoppyBlossom), 26.2..26.1 Fabric (chaevsfe) | LGPL-3.0 | yes | narrow + wide gauge tracks (verified in 1.5.0 changelog), semaphores, couplers, monorail | Best "two gauges" source. |
| Immersive Railroading (cam72cam) + Track API | IR 1.21.4..1.7.10 Forge/Neo; Track API 26.1.2 | IR LGPL-2.1; models CC-BY-NC-SA; Track API MIT | code yes, models no | life-size multi-gauge trains | Track API already at 26.1.2. |
| Minecraft Transit Railway (jonafanho) | 1.21.4..1.16 Fabric/Forge/Neo | MIT | yes | lines, stations, depots, timetables, passengers (closest to Transport Fever) | Own rail engine. |
| Create Railways Navigator (MrJulsen) | 1.21.1 | LGPL-3.0+ | yes | route planning, timetables UI | |
| Create: Threaded Trains | 1.21.1 | GPL-3.0+ | yes | async train sim performance | |
| Create: Routes (MIT 1.21.1), Create Dispatcher (MIT 1.20.1, tiny) | | MIT | yes | named routes / dispatch | Dispatch-board idea. |
| Railcraft Reborn (in pack) | 26.1.2 | custom (CovertJaguar permission) | no | signalling, locomotives, loaders | |
| Open Signals, Train Signals | 1.18.2..1.12.2 / 1.19.4 | Apache-2.0 / MIT | yes | German signals / manual signals | |
Recommendation: PORT Steam 'n' Rails (gauges, semaphores, couplers) from the 1.21.1 Neo port into diaithir-ground-water-transport; FOLD Navigator + Routes ideas for the Dispatch board; MTR is the line-management reference (PORT only its station/line UI if wanted).

## Carts (one-way/destination rails, cart loaders)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Steve's Carts 2 (CreeperHost) | 1.21.7..1.16.5 Forge/Neo (26.1 branch per tech-transport/PLAN) | MIT | yes | modular carts, manager/loaders | Original Vswe permission cited. |
| Railcraft Reborn (in pack) | 26.1.2 | custom | no | Loader/Unloader, dispenser, elevator track | One-way/routing tracks: unverified. |
| Minecart Trains Fork (in pack) | 26.3..1.17 | GPL-3.0 | yes | linked trains | |
| CartLoader (guicale) | 1.20.4 Fabric | GPL-3.0+ | yes | tiny loader | |
| Sophisticated Storage in Motion | 26.1.2 | ARR | no | chests in carts | |
| Astikor/Nifty Carts | 1.21.1 | BSD-2 / MIT | yes | animal carts | |
Recommendation: ADOPT-by-build Steve's Carts 2 (MIT) into diaithir-ground-water-transport; destination/one-way rails CLEAN-ROOM small blocks (none found).

## Boats / cargo boats / mounts
| Candidate | MC/loader | Licence | Port? | Notes |
|---|---|---|---|---|
| Cargo Boats (in pack) | 26.1.2..1.21.1 Neo | Apache-2.0 | yes | automated cargo |
| Better Boat Movement (in pack) | 26.3..1.19.3 | GPL-3.0 | yes | |
| aleki's Nifty Ships | 1.20.1 | MIT | yes | placeable containers on ships |
| Small Ships (talhanation) | 1.21.4 | ARR | no | cannons |
| Horseman (in pack, MIT), Horse Expert (MPL-2.0 26.3) | | | yes | mounts |
Recommendation: ADOPT in-pack set; FOLD aleki's container-on-ship into diaithir-ground-water-transport.

## Personal mobility (diaithir-personal-mobility)
| Candidate | MC/loader | Licence | Port? | Notes |
|---|---|---|---|---|
| Iron Jetpacks (in pack) | 26.1.2..1.12 | MIT | yes | |
| Hang Glider (Fuzs, in pack) | 26.3..1.18.2 | MIT | yes | |
| Gliders (Suff99) | 1.21.1..1.19.2 | GPL-3.0+ | yes | |
| Grappling Hook Mod (yyon) / Yori3o hooks (in pack) | 1.21.1..1.12.2 / 26.3 | GPL-3 / MIT | yes | |
| Modular Drones (in pack CC-BY-4.0), Buddy Drones (CC-BY-4.0) | | | yes with credit | |
| Create Jetpack | 1.21.1 | custom | no | |
Recommendation: ADOPT as already routed; nothing missing.

## Elevators, bridges, teleporter blocks (diaithir-travel-structures)
| Candidate | MC/loader | Licence | Port? | Notes |
|---|---|---|---|---|
| OpenBlocks Elevator (in pack) / ElevatorMod (VsnGamer) | 26.3..1.12.2 Fabric/Forge/Neo | MIT | yes | |
| Moving Elevators | 26.3 | ARR | no | clean-room (listed) |
| Laser Bridges & Doors | 26.3 | MIT | yes | bridges |
| Simple Teleporters Reforged (in pack) | 26.1.2 | MIT | yes | |
| Teleporters By Juix | 26.3 | CC0 | yes | |
Recommendation: ADOPT in-pack; FOLD Laser Bridges for drawbridge/light bridge.

## Physics ships + Cosmoteer-style modular ship building (diaithir-ships, Keelwright)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Valkyrien Skies 2 port, Eureka port | 26.2 Neo | LGPL-3 / Apache-2 | yes | in pack | |
| VS Tournament | 1.20.6 | Apache-2.0 | yes | merging (jar .3) | |
| Create: Propulsion (DeltaSF) | 1.20.6..1.20.1 Forge/Neo | MIT | yes | thrusters, magnets, VS2 | New: fold into Drive parts. |
| Create: Linked Thrusters (VS2 ed. 1.20.1), Fluxnautics (Sable+Mekanism, force fields, ion thrusters) | | MIT | yes (Sable API) | idea source for Ward/field drives | |
| Valkyrien Sails, Valkyrien Pirates | 1.20.x | LGPL-3 / MIT | yes | sails, boarding | |
| Sails and Airships | 26.3 Fabric | ARR | no | |
| Cosmoteer-like mods | none found | | | |
Recommendation: FOLD Create: Propulsion thruster/magnet logic into diaithir-ships Drive parts; rest CLEAN-ROOM Keelwright (per SHIPBUILDING.md).

## Assembly yards (rail, ship, space yards, cranes) (diaithir-yards, #186)
None found as a yard system. Cranes: Create Extended Gantries (GPL-3, 1.21.1, small); Create Aeronautics Physics Gantry (MIT, 1.21.1, Sable). Nothing for forklifts/drydocks.
Recommendation: CLEAN-ROOM on the #186 assembly API; FOLD Gantry arm movement idea if wanted.

## Spaceships and space travel between planets
| Candidate | MC/loader | Licence | Port? | Notes |
|---|---|---|---|---|
| Create: Northstar Redux | 1.21.1..1.20.1 | MIT | yes | planets, rockets via Create; best open source |
| Ad Astra | 1.21.1 | Terrarium Licence (custom) | no | |
| Galacticraft Legacy | 1.12.2 | MIT | yes | oxygen, planets; old |
| Advanced Rocketry 3 | 1.21.1 | ARR | no | |
| Gregicality Rocketry | 1.21.1 | LGPL-3 | yes | needs GT |
Recommendation: FOLD Northstar Redux planet/oxygen data into Foundry body profiles; ships stay Keelwright.

## Shipping containers and pallets loaded physically (cranes, forklifts, container ships)
Create Sable Pallets (MIT, 1.21.1, tiny), SDM Shipping Box (ARR). No container ship/forklift mod found.
Recommendation: CLEAN-ROOM container + pallet blocks (item-component inventory) in diaithir-yards.

## Interdimensional logistics / cargo drops
| Candidate | MC | Licence | Port? | Notes |
|---|---|---|---|---|
| Interdimensional Wireless Transmitter | 26.1.2 Fabric/Forge/Neo | MIT | yes | cross-dim item/fluid |
| Ad Astra Cargo Rocket (unofficial) | 1.20.1 | LGPL-3 | yes | cargo pods |
Recommendation: FOLD IWT (adopt if pack-eligible) + Ad Astra cargo rocket concept into diaithir-routing-networks / Launch pad.

## Ports / harbours / stations (diaithir_stations = crafting-station framework; Foundry stations)
No harbour/port mod found. Station-block examples: Create Station Decor (MIT 1.20.1), Create Track Map (MIT). Crafting stations: diaithir_stations framework (ports #163).
Recommendation: CLEAN-ROOM (dock/harbour blocks as yard types).

## Age-evolving stations
None found. Tinkers' Construct smeltery is the model (MIT, on port list).
Recommendation: CLEAN-ROOM (per PROGRESSION 7c).

## Fuel / refuelling
See Shared fuel API. Create Railways Refuelled (ARR), Create Liquid Fuel (ARR). Recommendation: as above.

## Vehicle crash / damage
Nothing standalone. Damage exists in IV (ARR) and MrCrayfish Vehicle (GPL). Recommendation: FOLD MrCrayfish crash/health logic into diaithir-vehicles.

## Vehicle animations
Nothing found; IV animated parts are ARR. Recommendation: CLEAN-ROOM (animation threads, ANIMATIONS.md).

---
# Megamachines deeper pass (2026-11-03, for plans/MEGAMACHINES.md, PR #27)
Catalogue read: 12 vehicles (treadwheel crane, steam navvy, walking dragline, bucket-wheel excavator, TBM, haul truck, crawler crane, crawler transporter, autonomous excavator/haul truck, strip miner, terraform builder), 7 structures (aqueduct, lock flight, dam, arcology, space elevator, orbital ring, Dyson swarm). Method: Modrinth API searches for each term (bucket wheel, dragline, tunnel boring, crane, gantry, quarry, drill, bore, excavator, builder, colonies, space elevator, dyson, orbital ring, dam, terraform, megastructure) plus the named mods. Licences read from API / LICENSE files.
Headline: no mod implements bucket-wheel excavators, draglines, TBMs, giant crawlers, tower/container cranes, forklifts, straddle carriers, ports, dams, space elevators or orbital rings as drivable/animated machines. Searches for "bucket wheel", "dragline", "tunnel boring machine", "space elevator", "orbital ring", "crane", "forklift", "container ship", "port" returned nothing relevant. Only fragments exist.

## Per-candidate table
| Candidate | Newest MC / loader | Licence | Covers (for megamachines) | Port plausibility |
|---|---|---|---|---|
| Immersive Engineering (BluSunrize) | 1.21.1 Neo (oldest 1.12.2) | Custom "Blu's License of Common Sense" (read): may copy bits with credit, fork, write addons; may NOT redistribute project without permission; derived code must be visible source | The excavator + bucket wheel multiblock (rotating wheel digs a swept area, output to hopper/crusher) is the only real bucket-wheel in any mod; also cranes? (none) | CLEAN-ROOM from the observed behaviour, or ask BluSunrize for redistribution permission. Copying small credited snippets is allowed. Not a drop-in port. |
| Create (in pack 6.0.9, MIT) + contraptions (drills, harvesters, saws, deployers) | 26.1.2 | MIT | Drill/harvester heads on moving contraptions: the digging mechanism for a swept-volume vehicle | Already in pack; use as the dig actor. |
| Create: More Drill Heads | 1.21.1 Neo | MIT | extra drill heads | Port easy, trivial. |
| Create Deployers / Create Crafts & Additions (mrh0) | 1.21.1 Neo | MIT | deployer = placement actor for builder vehicles; CCA adds electricity<->kinetic, cranes? no | Port plausible (MIT). |
| Create: Connected | 1.21.1 Neo | AGPL-3.0+ | QoL (inverted gearboxes, linked sequencers) | Copyleft AGPL; reuse ideas, avoid code. |
| Create Interactive (rubydesic) | 1.20.1 | ARR | walk on contraptions | No. VS2 gives this. |
| Create Big Cannons | 1.21.1 | custom CBC licence (read from API link) | big gun/cannon builds | Not megamachines; check licence only if used for ship guns. |
| Clockwork (ValkyrienSkies/rubydesic) | 1.20.1 Fabric/Forge | Apache-2.0 | VS2 + Create physics contraptions (propellers, flaps) | Port OK licence-wise; 1.20.1 only, needs VS2 API shifts; ideas for crawler/walker physics. Already judged in SHIPBUILDING. |
| VS Tournament | 1.20.6 | Apache-2.0 | utilities/thrusters | already merging. |
| "Takeoff" VS addon | not found on Modrinth (search "takeoff" only gives elytra mods) | unverified | | none found |
| RFTools Builder (McJty) | 26.3 Fabric/Forge/Neo (neo newest 1.21.1 in API) | MIT | Builder machine: copies/places/removes volumes with a moving "builder"; shield system | PORT-friendly (MIT, already on list C). Best open base for the terraform/structure builder logic. |
| Intelligence: Quarry | 26.1.2 Neo | MIT | vanilla-style quarry frame digging a volume | In batchA; fold quarry swept-volume logic for dragline/bucket-wheel work engine. |
| Industrial Foregoing (MIT, 1.21.1) | 1.21.1 Neo | MIT | Laser drill + miners (planet-scale drill) | Port plausible; list C. Laser drill is the nearest "quarry/planet-scale" machine. |
| Mekanism Digital Miner (MIT) | 26.1 branch building | MIT | volume miner with filters | Building from source per tech-transport plan; reference for filtered dig. |
| Simple Drills, Bores, Tunnel & Trench | 26.1.2 / 26.3 | MIT | hand tools | not machines. |
| Quarry Reborn, Simple Quarry, Create: Quarry, RetroRig: Quarry | various | CC-BY-NC / ARR | quarries | No (NC/ARR). |
| MineColonies (Raycoms) + builder hut | 1.21.1 Neo (CF), GPL-3.0+ (Modrinth shows old 1.18.2 page) | GPL-3.0-or-later | NPC builder places blueprints stage by stage | Core staged-build AI: GPL, large; reference/FOLD ideas for blueprint staging, not a port. |
| RFTools Builder + Structure blocks, Huge Structure Blocks | 26.3 | LGPL-3.0 | big blueprint place | Aid only. |
| Ad Astra / Galacticraft / Advanced Rocketry (stations) | see above | Terrarium (custom) / MIT (Galacticraft Legacy 1.12.2) / ARR | space stations, rockets | Galacticraft Legacy (MIT) is the only open station model; 1.12.2. |
| Nerospace (Neroland) | 26.3 (26.1.2 oldest) Fabric/Forge/Neo | custom | rockets, alien ore, terraform to rain | Custom licence: read https://github.com/Neroland/nerospace LICENSE before using; terraform idea matches RODOS builder. unverified licence terms. |
| Create: Northstar Redux | 1.21.1 | MIT | rockets, planets, oxygen | planet side; no elevator. |
| Dyson Sphere Project (Bax12) | 1.20.1 Forge | GPL-3.0 | Dyson-themed production/factory mod | Check content; port possible (GPL). Collector-swarm idea only. unverified depth. |
| Megastructure block (itsjustnil) | 1.21.11 Neo | GPL-3.0 | unclear, 261 downloads | unverified, tiny. |
| Extra Utilities family (Reborn Again 1.20.1 MIT; Angel Extra Utilities 1.21.1 MIT; Reutilized NC-SA) | | | machines, no vehicles | no megamachine content. |
| Flan's Mod Reloaded (MIT 1.20.1 Forge) | 1.20.1 | MIT | heavy vehicles with seats, turret, tank tracks; data-driven | Port plausible for crawler chassis/tank tracks (MIT); old Flan's 1.12.2 custom. |
| MrCrayfish Vehicle Unofficial (GPL-3) | 1.21.1 | GPL-3.0 | haulers/trailers, fuel | already recommended. |
| Create Aeronautics Physics Gantry | 1.21.1 | MIT | gantry arms on Sable | Sable-dependent, rewrite on VS2. |
| Create Extended Gantries | 1.21.1 | GPL-3.0 | gantry extension | small; GPL ok to port. |
| Create Sable Pallets | 1.21.1 | MIT | pallet blocks | tiny. |
| Minecraft Transit Railway | 1.21.4 | MIT | rail/station infrastructure, cable cars | ports/stations reference. |
| Aleki's Nifty Ships (MIT) | 1.20.1 | MIT | ships carrying container blocks | harbour cargo basis. |

## Per megamachine feature
- Bucket-wheel excavator, strip miner, dragline, steam navvy: IE excavator (custom licence, clean-room) for the wheel/hopper idea; dig actor from Create drill heads; swept-volume work engine from Intelligence: Quarry + RFTools Builder (MIT). Recommendation: CLEAN-ROOM vehicle on VS2; FOLD quarry/builder volume logic (MIT) into the dig engine.
- Tunnel borer: nothing; Create drill head rotating cylinder + Bores (MIT, hand tool). CLEAN-ROOM.
- Giant crawlers/crawler transporter/haul truck: Flan's Reloaded (MIT) tracks + MrCrayfish Vehicle trailers; on VS2 chassis. FOLD tank-track chassis from Flan's Reloaded if wanted.
- Tower/gantry/crawler crane, container crane, forklift, straddle carrier, ports: none; Create Aeronautics Physics Gantry (MIT) + Extended Gantries (GPL) for arm motion only. CLEAN-ROOM on assembly-yard API (#186).
- Quarry/planet-scale harvesters: Industrial Foregoing laser drill (MIT), Intelligence: Quarry (MIT, 26.1.2). PORT/ADOPT Quarry; PORT Industrial Foregoing laser drill.
- Dams, aqueducts, lock flights: no mod; MineColonies/RFTools Builder as staged-build mechanic only. CLEAN-ROOM structures with blueprint stages.
- Space elevator, orbital ring, Dyson swarm: no mod. Northstar Redux / Nerospace / Galacticraft Legacy for planets; elevator and ring CLEAN-ROOM (tie to Foundry Sky ladder).
- Builder/terraform vehicle: RFTools Builder (MIT) PORT logic; Nerospace terraform idea (licence unverified).
- "Modular Powersuits-scale": not searched at depth; Modular Powersuits is a 1.12/1.20 power-armour mod (licence unchecked) and out of megamachine scope: unverified.
- Tinkers' Construct: no vehicle content; only the Age-evolving station model.


---

<!-- part2_combat_gear.md -->
# Mod survey part 2: combat and gear (2026-11-03)
Data: Modrinth API (project + version endpoints, verified 11-03). CurseForge/GitHub were not reachable from this session (GitHub 403 "not enabled", CF not tried), so CF-only mods are "unverified" and taken from PACK_CONSOLIDATION_AUDIT.csv. Ports PRs #167-#198 could not be read (no repo access); in-pack state comes from plans/PACK_CONSOLIDATION_AUDIT.csv, mod-ports/PLAN.md, CLEAN_ROOM_COMBAT_GROUP.md.
Already in pack/done (not redone): own diaithir-firearms (clean-room of Vic's Point Blank, v1, 80/0 selftest), musketmod-diaithir.1 (MIT), Player Animation Library 1.2.8 (MIT), GeckoLib 5.5.2 (MIT), Emotecraft, EMF/ETF, Artifacts (MIT), Silent Gear (MIT), Apotheosis (MIT), Relics & Artifacts (Apache-2.0), Combat Roll (GPL-3), Critical Strike (GPL-3), Jungdab's Turrets (MIT), Better Caravans (MIT), Gateways to Eternity (MIT), Illager Invasion (MIT), Mutant Monsters (AGPL), Millager (MIT), Tool Belt (BSD-3, CF), Baubley Heart Canisters (MIT), Mining Gadgets (MIT, CF; pack has 1.19.3 build).
Note: Modrinth lists tr7zw "First-person Model" as MIT (1.16.5..26.3), contradicting the audit's "firstperson = Protective/ARR". Needs a check of the actual licence file before the clean-room is relied on.

## Firearms, historical designs 1288-2019 (diaithir-firearms)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| TaCZ (Timeless and Classics Zero), MCModderAnchor | 1.20.1 Forge..1.18.2 | GPL-3.0-only | yes (GPL, own module) | data-driven gun framework: guns, attachments, ammo, animations, gun-pack format | no 26.1; unofficial 1.21.1 NeoForge port tacz-1.21.1 (MUKSC, GPL-3.0) exists |
| Musket Mod, ewewukek | 1.21.1 NeoForge..1.16.5 | MIT | yes | flintlock musket/pistol/blunderbuss | already ours as musketmod diaithir.1 |
| Pillager's Gun (Unofficial Port) | 26.2 neoforge/fabric..1.20.1 | GPL-3.0-only | yes | pillager gun, small | 26.1+ build exists |
| One in the Chamber [MTS/IV] | 26.1.2 forge,neoforge..1.12.2 | GPL-3.0-only | yes | guns as Immersive Vehicles content pack | 26.1.2 NeoForge build, fits our IV |
| Custom Gun Continued | 26.3 neoforge..1.20.1 | GPL-3.0-only | yes | gun framework | 26.x build, unverified depth |
| Firearms (firearms_re4) | 26.2 all loaders..1.21.11 | MIT | yes | RE4-style guns, small | |
| Scorched Guns Neoforged / Scorched Guns 2 Flintlocks | 1.21.1 / 1.20.1 | GPL-3.0-or-later | yes | sci-fi + flintlocks | no 26.1 |
| Balkon's WeaponMod: Legacy, HyperSpeeed | 26.3 fabric,forge,neoforge..1.7.10 | MIT | yes | musket, crossbow, cannon, dynamite, halberd etc., 15 years of versions | 26.x build exists, loader neoforge |
| Flan's Mod: Reloaded | 1.20.1 Forge | MIT | yes | guns, vehicles, content-pack format | no 26.1 |
| Techguns-CE | 1.12.2 | custom (Techguns Mod License) | unverified terms | guns, ammo, ammo press | read licence before any use |
| Modern Warfare Cubed | 1.12.2 | Apache-2.0 | yes | modern guns | old |
| Vic's Point Blank | 26.1.2 | ARR | no | guns | already clean-roomed |
| Mo' Than Enough Guns, Shots Fired, Old West Weaponry, Bren | 1.20.1..1.21.10 | GPL-2+/Apache/MIT/MIT | yes | small gun sets | |
| MrCrayfish Gun Mod (CF) | unverified | unverified | unverified | | |
Historical coverage (handgonne to 2019 designs): no mod covers it as a catalogue; Balkon's + TaCZ packs cover ~15%.
Recommendation: CLEAN-ROOM (continue diaithir-firearms; data-driven weapon list). Optional FOLD of MIT assets/code from Balkon's WeaponMod Legacy and Musket Mod for pre-1700 firearms; TaCZ's pack format is a design reference only (GPL, own module if used).

## Ammo: magazines, boxes, belts, ammo containers (MUNITIONS_CONTAINERS)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| TaCZ Applied Ammo Box / Curios For Ammo Box (nanaios) | 1.21.1 neoforge..1.20.1 | GPL-3.0-only | yes | ammo box items, curios slot | needs TaCZ |
| TaCZ Magazines (Raiiiden) | 1.20.1 | ARR | no | magazine items | |
| Call to Battle Ammo Boxes Addon | 1.12.2 | ARR | no | | |
| ModularShootAmmo (Yanbwe) | 1.21.1 neoforge | MIT | yes | ammo-type API | tiny, 114 dl |
| Techguns-CE | 1.12.2 | custom | unverified | ammo, ammo press | |
Coverage: boxes ~40%; belts/links/clips/loaded-empty states: none found.
Recommendation: CLEAN-ROOM inside diaithir-firearms (container items per plans/MUNITIONS_CONTAINERS.md); read MIT ModularShootAmmo for tag design.

## Munitions catalogue: rounds, parts, stations (MUNITIONS.md)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Create Big Cannons (realRobotix) | 1.21.1 neoforge..1.18.2 | custom (Create-Big-Cannons-License) | read licence | cannon shells, powder, casting, fuzes, assembly | closest to catalogue; no 26.1 |
| CBC: Advanced Technologies / Going Ballistic | 1.21.1 | MIT | yes | extra CBC munitions | depends on CBC |
| CBC Modern Warfare | 1.20.1 | MIT | yes | modern shells | |
| ICBM-Classic | 1.12.2 | MIT | yes | missiles, explosives, launchers | old |
| Ballistix | 1.21.1 | custom (AURILISDEV 1.02) | unverified | missiles, explosives | |
| Flan's Mod Reloaded | 1.20.1 | MIT | yes | bombs, shells | |
| Create Arms Race Reborn | 1.20.6 | MIT | yes | ammo recipes | |
| OldCannons (in pack) | - | - | - | cannon logic | per MUNITIONS.md |
Coverage: ~25% of the eight-line age chains (cannon and bombs only); no tech-age chain exists anywhere.
Recommendation: CLEAN-ROOM (data catalogue + machines in Foundry/tech); FOLD MIT bits (ICBM-Classic, CBC addons) if recipes/models help; CBC after licence read.

## Gun animations (fire/dry/reload)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| TaCZ | 1.20.1 | GPL-3.0-only | yes | full fire/reload/inspect animation set via Blockbench | best reference |
| Immersive Guns (lukeon) | 1.20.1 fabric | GPL-3.0-only | yes | animated guns | |
| Old Guns | 1.21.1 | ARR | no | | |
| TaCZ - First-person Model compat | 1.21.1 neoforge | MIT | yes | tiny glue | |
| Vic's Point Blank | 26.1.2 | ARR | no | | already rewritten |
Recommendation: CLEAN-ROOM on Player Animation Library + GeckoLib (as ANIMATIONS.md); use TaCZ animation file structure as a GPL reference only.

## Melee/tool/bow player animations
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Player Animation Library (ZigyTheBird) | 26.3 fabric,neoforge..1.21.1 | MIT | in pack | engine | |
| Better Animations Collection (Fuzs) | 26.3..1.18.2 | MPL-2.0 | yes | vanilla-body anim tweaks (eating, swing etc.) | 26.x NeoForge; unexpectedly fits NEA gap |
| Emotecraft | 26.3..1.16.5 | GPL-3.0-or-later | in pack | emotes | |
| Better Combat | 26.3..1.18.2 | ARR | no | swing anims | clean-room in combat-arms |
| Epic Fight | 1.21.1..1.12.2 | GPL-3.0-or-later | yes | swing/skill animations | no 26.1 |
| Not Enough Animations | 26.3 | tr7zw Protective | no | | |
| Custom Player Animations (RazorPlay01) | 26.3 neoforge | CC-BY-NC-SA-4.0 | no (NC) | | |
Recommendation: FOLD Better Animations Collection (MPL-2.0, file-level) into diaithir-entity-animation for vanilla-body anims; CLEAN-ROOM swings; Epic Fight as GPL reference.

## First-person pose layer
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| First-person Model (tr7zw) | 26.3..1.16.5 | MIT per Modrinth (audit says Protective; recheck) | yes if MIT confirmed | first-person body | |
| Punchy! | 26.4-snap..1.20.1 | ARR | no | fp animations | |
| Fancy View Model | 26.3 fabric | ARR | no | | |
| SkyHands / MCInspects | 26.2 / 1.21.7 fabric | MIT | yes | fp hand/inspect | small |
Recommendation: PORT/FOLD First-person Model into diaithir-client-view-input if the MIT licence file is confirmed, else CLEAN-ROOM.

## Machine/block/vehicle/entity animations (core, rules, coverage)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| GeckoLib | 26.1.2 | MIT | in pack | block/entity/item/armor anims | |
| Entity Model Features / Entity Texture Features | 26.1 | LGPL-3.0 | in pack | custom models | |
| PulseLib | 26.2 neoforge | custom ALoCS | unverified | animation lib | |
Coverage tooling (CSV of every thing to animate): none found.
Recommendation: ADOPT GeckoLib as-is (in pack); animation content CLEAN-ROOM from ANIMATIONS_COVERAGE.csv.

## Boss/bestiary animations
GeckoLib (in pack) is the only engine; bosses in Bosses of Mass Destruction Forge (LGPL-3.0, 1.21.1 neoforge..1.20.1), Alex's Caves Continued (LGPL, in pack), Mutant Monsters (AGPL) ship GeckoLib-style animation assets.
Recommendation: CLEAN-ROOM (own animations on GeckoLib); BoMD Forge as a port source for mechanics if wanted.

## Historical melee weapons (spartan-weaponry style)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Spartan Weaponry Unofficial (Mai_xiyu) | newest 1.21.1 neoforge (project range lists 26.1) | Apache-2.0 | yes | ~40 weapons, 18 types | 26.1 build seen in range, confirm file |
| Spartan Weaponry / Spartan Shields (ObliviousSpartan) | 1.20.1..1.12.2 | Apache-2.0 | yes | | original |
| Balkon's WeaponMod: Legacy | 26.3..1.7.10 | MIT | yes | | |
| Immersive Weapons | 26.3 neoforge..1.20.1 | MIT | yes | | |
| Epic Knights | 26.1.2 | ARR | no | | |
| Fantasy Weapons (Medieval Series) | 26.x | ARR | no | | |
| Epic Fight x Spartan Weaponry | 1.20.1 | CC-BY-4.0 | yes | anim data | |
Coverage vs the 246-weapon roster (weapons/WEAPONS_ROSTER.csv): ~20%.
Recommendation: PORT Spartan Weaponry Unofficial (Apache-2.0) as the base (mod-ports lane A), then data-add the roster.

## Armor
| Candidate | MC/loader | Licence | Port? | Notes |
|---|---|---|---|---|
| Immersive Armors (Luke100000) | 26.1.2 neoforge..1.16.5 | GPL-3.0-only | yes (own module) | many historical sets |
| Armor Model API | 26.3 | MIT | in pack | |
| Epic Knights, Fantasy Armor | 26.x | ARR | no | |
| Armourer's Workshop | 26.1.2 | CC-BY-NC-SA-3.0 | no | |
| Knight Quest | 1.21.1 | GPL-3.0 | yes | |
Recommendation: ADOPT Immersive Armors 26.1.2 as-is only if pack-eligible (GPL stays separate); else FOLD into diaithir-combat-arms. Per-Age data CLEAN-ROOM.

## Relics and magical gear
Artifacts (MIT, 26.1.2), Relics & Artifacts (Apache-2.0, 26.3), Yori3o's Relics 'n Jewelry (MIT, 26.3 neoforge..1.21.1), Arcane Relics (LGPL, fabric), Relics RPG (ARR), Reliquary/Forbidden Arcanus (ARR). 
Recommendation: ADOPT Artifacts and Relics & Artifacts (in pack); FOLD Yori3o's Relics (MIT) into diaithir-arcane-relics.

## Accessories (tool belt, jewelry, magnets)
| Candidate | Licence | Notes |
|---|---|---|
| Curios API (26.3, LGPL-3.0+) | in pack | slot layer |
| Tool Belt (gigaherz, CF) | BSD-3 | unverified on Modrinth, in pack per audit; port |
| Traveler Tool Belt | ARR | no |
| Beans' Toolbelt / ToolBelt Unlimited | MIT, 1.21.1 | alt sources |
| Jewelry (RPG), Iron's Jewelry | ARR | clean-room |
| Yori3o's Relics 'n Jewelry, Additional Jewelry (MIT, 1.21.1) | MIT | jewelry source |
| Simple Magnets | ARR | clean-room |
| Magnets by Juix (CC0, 26.x), Simple Magnet (azeolii, MIT), Magnetic Enchantment (AGPL) | | open magnet sources |
Recommendation: PORT Tool Belt (BSD) and Baubley Heart Canisters (MIT) into diaithir-accessories; FOLD Yori3o jewelry (MIT) and Magnets by Juix (CC0) for jewelry and magnets.

## Parts stations (smithy, workshop bench, gunsmith bench)
| Candidate | MC/loader | Licence | Notes |
|---|---|---|---|
| Silent Gear | 26.1.2 | MIT | part-based tools, in pack |
| Create: Gunsmithing (jetug) | 1.21.1 | GPL-2.0-or-later | gun part crafting |
| Tetra | 1.20.1 | ARR | no |
| Tinkers' Construct | in pack | | |
| Techguns-CE | 1.12.2 | custom | gun workbench, ammo press |
Recommendation: FOLD Silent Gear station pattern (in pack) plus CLEAN-ROOM gunsmith bench/ammo press; Create: Gunsmithing as GPL reference.

## Combat classes, skill trees, crits
| Candidate | MC/loader | Licence | Notes |
|---|---|---|---|
| Skill Tree (RPG Series) | 26.3 | ARR | clean-room (done route) |
| Pufferfish's Skills framework + Default Skill Trees (CC0) | 26.3 | CC0 (trees); framework licence unverified | data-driven, candidate for diaithir-quests-skills |
| Stronger/RPG skill tree (PanCaKe) | 26.x | MIT | Pufferfish datapacks |
| Critical Strike (Zsolt) | 26.3 | GPL-3.0-only | port, in pack |
| Epic Fight: Skill Tree | 1.21.1 | GPL-3.0 | reference |
| LevelZ | 1.21.1 fabric | GPL-3.0 | |
Recommendation: PORT Critical Strike (GPL, own module); CLEAN-ROOM class trees on the Pufferfish-style data format (verify framework licence).

## Mounted combat and rolls
Combat Roll (GPL-3.0, 26.1.2) in pack: PORT as planned. Jousting (ARR, 26.1.2): CLEAN-ROOM data. Mobbility combat roll addon (MIT, 1.20.1). Recommendation: PORT Combat Roll into diaithir-combat-arms; CLEAN-ROOM lances/mounted.

## 3D skin layers
3D Skin Layers (tr7zw Protective, 26.2 neoforge): not portable. Recommendation: CLEAN-ROOM (diaithir-entity-animation); none other found.

## Player model / skin
Show Me Your Skin (MIT, fabric), Skin Restorer (MIT, 26.x), SkinsRestorer (GPL), First-person Model, Armourer's Workshop (NC-SA). Recommendation: CLEAN-ROOM (small); FOLD Skin Restorer (MIT) only if server skin handling needed.

## Boss system, Calamity-style bosses via Celtic rituals (ASCENDANT.md)
| Candidate | MC/loader | Licence | Notes |
|---|---|---|---|
| MC Calamity (NotGleam) | 1.21.4..1.20.2 | CC-BY-4.0 on Modrinth (ASCENDANT.md said unconfirmed) | recreation of Terraria mod: still excluded by project rule |
| Devourer of Gods, Minecraft Calamity | 1.21.1 | ARR | no |
| Lethality (Terramity addon) | 1.20.1 | CC0 | depends on Terramity ARR |
| Bosses of Mass Destruction Forge | 1.21.1 neoforge | LGPL-3.0 | boss mechanics reference |
| Progressive Bosses | 1.20.1 | MIT | scaling |
| Boss Rush (BSD-3), Boss Checklist (MIT, 26.3), Roots Classic rituals (MIT, in pack), Gateways to Eternity (MIT, 26.1.2) | | | rush/checklist/ritual/wave pieces |
Recommendation: CLEAN-ROOM in diaithir-bosses (as ASCENDANT.md); FOLD Boss Checklist (MIT) and ritual pattern of Roots Classic.

## Win ceremony / gate block
none found (no mod models an end-of-game ceremony gate). Recommendation: CLEAN-ROOM.

## Hostile encounters (caravans, hordes, lunar, blood moon, raiders, mutants)
| Candidate | MC/loader | Licence | Port? |
|---|---|---|---|
| Better Caravans | 26.3 neoforge | MIT | in pack |
| Enhanced Celestials 1 | 1.21.1..1.19.2 | LGPL-3.0-only | yes (planned port); EC2 is ARR |
| Lunar (Mrbysco) | 26.1 neoforge | MIT | yes |
| Blood Moon (nugrevan) | 26.2 all | MIT | yes |
| Better Blood Moon | 26.2 neoforge | MIT | yes |
| Zombie Hordes (hooneybAdgers) | 26.2 | MIT | yes |
| The Hordes (Smileycorp) | 1.21.1..1.12.2 | LGPL-2.1 | yes |
| Undead Nights | 26.3 | ARR | no (clean-room, per audit) |
| Raided (Mrbysco) | 26.3 | MIT | yes |
| Illager Invasion, Mutant Monsters, Gateways to Eternity, Immersive Pillagers | 26.x | MIT/AGPL/MIT/GPL | in pack |
| Global Events | fabric | MIT | reference |
Recommendation: FOLD Lunar + Blood Moon + Zombie Hordes + Raided (all MIT, 26.x) and Enhanced Celestials 1 (LGPL) into diaithir-hostile-encounters; Undead Nights replaced by those.

## Turrets and mining laser gadgets
Jungdab's Turrets (MIT, 26.3), Mining Gadgets (MIT, CF, unverified on 26.1; pack has 1.19.3), Mekanism Turrets (MIT, 26.x), Patched/Tails. Recommendation: PORT Jungdab's Turrets (26.x exists, so adopt) and Mining Gadgets into diaithir-tools-gadgets.

## Shields/ranged
Spartan Shields (Apache-2.0, 1.20.1), Ranged Weapon API (MIT, 26.x, in pack), Archers (ARR), Sword Blocking Mechanics (MPL-2.0, 26.x), Passive Shield (ARR). Recommendation: FOLD Spartan Shields (Apache) + Sword Blocking Mechanics (MPL) into diaithir-combat-arms; ADOPT Ranged Weapon API.

## Damage types
Nothing dedicated found. Silent Gear/Apotheosis (MIT, in pack) carry attributes; Spell Power Attributes (LGPL, in pack) is the spell side. Recommendation: CLEAN-ROOM (datapack damage types).

## Armour/weapon repair
Searches returned only SyncRepair (GPL, fabric) and Unbreakable Items (LGPL). Recommendation: CLEAN-ROOM (station recipes via Silent Gear repair).

## Age-gated combat recipes
none found; Age gating lives in content/tech_ages.json. Recommendation: CLEAN-ROOM data (no mod).

---
# DEEP PASS (coordinator request 11-03): supersedes the earlier verdicts for these features
Newest MC = newest build listed on Modrinth (verified via API) unless marked. Clean-room inspiration = behaviour to copy, no code/assets. Not found / unverified is stated.

## Firearms catalogue (historical designs, mass-produced) [deep]
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| TaCZ (MCModderAnchor) | 1.20.1 forge..1.18.2 | GPL-3.0-only | yes | data-driven guns/attachments/ammo/animation; gun-pack format; huge pack ecosystem | unofficial 1.21.1 NeoForge port (MUKSC, GPL-3.0); 26.1 port plausible = bump 1.21.1 port |
| Superb Warfare (Mercurows) | 1.21.1 neoforge, 1.20.1 forge | GPL-3.0-only | yes | guns, ammo types, vehicles, Superb Warfare-style mags/ammo box, many addons (CC0 Block Expansion, GPL/LGPL packs) | no 26.1 |
| Vic's Point Blank | 26.1.2 | ARR | clean-room (done) | named behaviour: ADS, attachments, ammo/mag swap, recoil, jam | covered by diaithir-firearms |
| MrCrayfish Gun Mod (GitHub mrcrayfish/mrcrayfishgunmod) | newest I could confirm 1.19.2; repo licence "other" (LICENSE-new.txt, not opened) | custom, unverified | assume clean-room | classic gun/ammo/workbench (weapon workbench station) | not on Modrinth |
| Scorched Guns Neoforged / Scorched Guns 2: Flintlocks | 1.21.1 neoforge / 1.20.1 | GPL-3.0-or-later | yes | flintlocks, custom guns, mobs | |
| Pillager's Gun port, One in the Chamber (26.1.2 neoforge, GPL-3.0), Custom Gun Continued (26.3, GPL-3.0), Firearms RE4 (26.2, MIT), Stabx Modern Guns (1.21.1, GPL-3.0) | | | yes | 26.x-capable gun content | |
| Balkon's WeaponMod Legacy | 26.3..1.7.10 | MIT | yes | musket, crossbow, cannon | |
| Ballistix (aurilisdev) | 1.21.1..1.16.5 | custom AURILISDEV 1.02 | unverified | explosives/missiles | |
| Flan's Mod Reloaded | 1.20.1 | MIT | yes | gun/vehicle content-pack format | |
| ModularWarfare | 1.12.2 | CC-BY-NC-SA-4.0 | no (NC) | gun-pack format | |
| Techguns-CE | 1.12.2 | custom | unverified | |
Revised view: a GPL gun framework (TaCZ 1.21.1 NeoForge port or Superb Warfare) exists and is portable. Plausible ~70% of firearm behaviour for modern-era guns; the missing part is the 1288-2019 historical roster (which would be data in TaCZ-style packs).
Recommendation: PORT TaCZ (1.21.1 NeoForge port -> 26.1.2) as its own GPL module for the gun engine, add our historical roster as data packs; keep diaithir-firearms (clean-room Point Blank) only for ids already migrated. Decision for coordinator: two gun engines is one too many.

## Ammo, mags, belts, containers [deep]
| Candidate | MC/loader | Licence | Port? | Covers |
|---|---|---|---|---|
| TaCZ ammo + magazine/extended-mag attachment system | 1.20.1 | GPL-3.0 | yes | magazines, ammo types, reload states |
| Superb Warfare ammo boxes/ammo types | 1.21.1 neoforge | GPL-3.0 | yes | ammo box, ammo types |
| [TaCZ] Applied Ammo Box, Curios For Ammo Box (nanaios) | 1.21.1 neoforge | GPL-3.0-only | yes | bulk ammo box, curios slot, AE2 link |
| Create Big Cannons | 1.21.1 | custom CBC | read licence | cartridge, shell, powder charge, cannon ammo containers (munitions parts and stations) |
| ModularShootAmmo | 1.21.1 neoforge | MIT | yes | ammo types API |
| TaCZ Magazines (ARR), Torch Bandolier (MIT, 1.21.1, bandolier pattern) | | | clean-room / yes | |
Belts/links: no mod found with belt feed advance; CBC and Superb Warfare cover boxes/magazines only.
Recommendation: FOLD TaCZ ammo/mag system + Ammo Box addons (GPL, in the TaCZ module); belts/links CLEAN-ROOM; CBC for artillery munitions after licence read.

## Gun animations [deep]
TaCZ (GPL-3.0, 1.20.1; 1.21.1 port), Superb Warfare (GPL-3.0, 1.21.1), Immersive Guns (GPL-3.0, 1.20.1 fabric), Vic's Point Blank (ARR; named behaviour: smooth ADS, inspect, per-state reload), Old Guns (ARR). TaCZ ships fire/dry-fire/reload-empty/reload-tactical/inspect/bolt animations as GeckoLib-like animation files, authored in Blockbench.
Recommendation: PORT TaCZ animation system with the gun engine (GPL); CLEAN-ROOM only the belt-feed additions.

## 3D skin layers [deep]
3D Skin Layers (tr7zw): newest 26.2 neoforge build (26.3 listed), licence tr7zw Protective (ARR-class), source github.com/tr7zw/3d-skin-layers (public but licence forbids reuse). Others: Legacy 3D Skin Layers (Wyvest, 1.8.9, GPL-3.0, tiny, old renderer); DragonMine Z Layers+ (GPL-3.0, 1.20.1); SkinLayers3D CustomSkinLoader Bridge (MIT, 1.21.4-1.21.5, bridge only).
Behaviour to copy clean-room: extrude the second skin layer into voxel boxes per pixel, skip hidden faces, LOD by distance, toggle for first-person hands.
Recommendation: CLEAN-ROOM (small, ~300 lines), may read the GPL Legacy mod for mesh approach as a GPL-module reference only.

## Damage types [deep]
Overhauled Damage (TheRedBrain, MIT, 26.1.2 fabric..1.20.1): typed damage framework, closest match. Improved Damage Framework (MIT, 1.19.2). Spell Power Attributes (LGPL, in pack), Apotheosis (MIT), Alembic (LGPL, 1.20.3), Abloom API (GPL, 26.3). In vanilla 26.1 damage types are data (datapack damage_type).
Recommendation: FOLD Overhauled Damage ideas/code (MIT) into diaithir-combat-progression (loader fabric -> NeoForge port); datapack damage types for content.

## Armour/weapon repair [deep]
Anvil Repairing (Darkhax, LGPL-2.1, 26.3 neoforge) - repair at anvil with materials; Repair Anvil (MIT, 26.1.2 datapack/loaders); SF's Anvil Repair (MIT, 1.21.11); Iron Repair Kits (MIT, 1.20.6 neoforge) - kit items; Smart Durability & Repair (MIT, 1.21.1 neoforge); Create Repair (MIT, 1.20.1); Anvil Repair (CC-BY-NC-SA, no); Silent Gear repair kits (MIT, in pack).
Recommendation: FOLD Anvil Repairing (LGPL, fold with notices) + Iron Repair Kits (MIT) into diaithir-tools-gadgets; repair-kit tiers per Age as data.

## Boss/ritual summoning (Celtic rituals) [deep]
| Candidate | MC/loader | Licence | Port? | Covers |
|---|---|---|---|---|
| Summoning Rituals (Relentless) | 1.21.1 fabric,forge,neoforge..1.18.2 | ARR | clean-room | altar + item offerings summon mobs (behaviour to copy: item list at altar, spawn on completion) |
| Occultism (klikli-dev) | 26.3 neoforge..1.18.2 | MIT | in pack | multi-step chalk-circle rituals with sacrificial bowls, spirits (not bosses) |
| Roots Classic rituals | 26.1.2 | MIT | in pack | druidic rituals, item/ingredient altar |
| Ritual Magic (zickit) | 26.2 | MIT | yes | ritual framework |
| rituals (strixun) | 26.3 | MIT | yes | totem rituals |
| Abyssal Corrupter | 1.21.1 neoforge | MIT | yes | boss summoned at altar |
| Blood Magic | 1.20.1 | CC-BY-4.0 | yes | altar tiers, sacrificial rituals, demon summons; Neo Vitae (MIT) is its 26.1.2 successor, in pack |
| Twilight Forest | 26.1.2 (LGPL-2.1, in pack) | | in pack | boss altar/trophy/summon-by-item pattern; advancement-gated progress |
| Ice and Fire | 1.20.1 (ours ported) | LGPL-3.0 | in pack | summon via item/pit, dragon bosses |
| Cataclysm (L_Ender) | 1.21.5 | CC-BY-NC-ND | no | boss summon by item at altar block; clean-room inspiration only |
| Goety / Mowzie's Cataclysm | 1.21.x | ARR | no | summoning |
| Ars Nouveau | 1.21.1 | ARR | no | rituals at Ritual Brazier (clean-room inspiration: brazier + item set) |
| UltraRituals Free (Modrinth, newer than 26.1 per search; page not API-verified) | unverified | unverified | unverified | rituals that spawn any boss |
| Terraria Calamity-type | none for MC 26.1 | ARR/CC-BY (MC Calamity, excluded by rule) | | |
Recommendation: FOLD Occultism/Roots/Neo Vitae ritual step primitives (MIT, in pack) + Twilight Forest altar pattern into diaithir-bosses; boss contents CLEAN-ROOM. Changes earlier "clean-room only" to "ritual engine reuse from in-pack MIT mods".

## Epic Fight, Better Combat [deep]
Epic Fight (Yesssssman): newest 1.21.1 neoforge (1.12.2..1.21.1), GPL-3.0-or-later, big addon ecosystem incl. Epic Fight x Spartan Weaponry (CC-BY-4.0, 1.20.1), Skill Tree (GPL-3.0), Sword Soaring (LGPL). No 26.1 build. Port plausible: GPL, own module, large (animation + combat engine); would conflict with Better Combat/clean-room swings, choose one.
Better Combat (ZsoltMolnarrr): 26.3, ARR, behaviour to copy: attack-hitbox arcs, per-weapon combos, swing animations via PlayerAnimation (Player Animation Library), weapon_attributes JSON.
Recommendation: CLEAN-ROOM swings (as planned) with Epic Fight as GPL reference; or PORT Epic Fight if the team wants a full combat overhaul (decision for coordinator).

## Create armorer / station mods [deep]
Create: Immersive Armorer Integration and Create: Immersive TaCZ Integration (MarcosJoestar, MIT, 1.21.1 neoforge): Create-machine crafting of armour and TaCZ guns (fits parts stations/gunsmith bench). Create: Gunsmithing (GPL-2+, 1.21.1). Recommendation: FOLD both MIT integrations as recipe/station references for the gunsmith bench; assembled by Create nodes in Foundry module.


---

<!-- part3_logistics_tech.md -->
# Mod-first survey, part 3: logistics and tech (2026-11-03)
Method: Modrinth API (search + project/version endpoints, queried 11-03) on about 130 queries; pack state from plans/PACK_CONSOLIDATION_AUDIT.csv; earlier work reused, not redone (FACTORIO_MODS_SURVEY.md sections 1 and 4, tech-transport/PLAN.md, FACTORIO_TECH.md module map). Version ranges are Modrinth tags (oldest..newest), loader for newest. "In pack" = audit CSV row. Not searched: CurseForge-only mods beyond the 19 IDs already pulled on 11-02 (CF API 403); GitHub-only repos not on Modrinth (unverified). Port rule: open licence = port; ARR/NC-ND/custom = clean-room. PRs #107..#199 could not be read (gh GraphQL 403 in this session); module owners below come from FACTORIO_TECH.md and the audit CSV.

New finds since the 11-02 survey (change earlier verdicts):
- **Conveyors & Automation** (Zetakron, MIT, NeoForge 1.21.1/1.21.4/26.2/26.3, 2026-10-30): two-lane belts, 3 tiers, undergrounds, splitters, filter splitters with lane priority, burner/standard/fast/long/stack inserters with filter and lane select. This contradicts the 11-02 line "no Minecraft mod has lane belts, splitters, inserters". No 26.1 build. Source repo per Modrinth issues link: github.com/Zetakron/Conveyors-Automation (not readable from this session: GitHub access not enabled, raw LICENSE URL 404 on main; repo licence file unverified, Modrinth says MIT). Best port base for the Factorio belt set.
- **Satiscraftory** (StainlessStasis, GPL-3.0-or-later, NeoForge 26.1.2, early alpha): Satisfactory-style world-spanning factory simulation that runs with chunks unloaded. Idea source for chunk-free simulation and autonomy; its design is closed (no pipes/cables/other mods), so port only the sim idea.
- **Research Tree** (Wolfieboy09, Apache-2.0, NeoForge 1.21.1, github.com/wolfieboy09/ResearchTree): data-driven research GUI. Second source next to Researcher.
- **Ol' Foundry** (MIT, Fabric 26.1.2): single smelter block with slag byproduct; small ore-chain piece.

## Circuit network, signal wires, combinators, redstone computing (diaithir-routing-networks)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| More Red (Commoble) | 1.20.1 Forge/Neo (in pack, keep) | MIT | yes | ~35%: bundled cables, gates, relays | In pack already; signal bundling is the nearest to wires. No numeric signals. |
| Project Red Core/Integration/Transmission | 1.19.2..1.21.1 Forge/Neo (2026-07) | MIT | yes | ~30%: bundled cable, gates | Redstone gates only, no arithmetic. Redpower lineage. |
| Integrated Dynamics + Integrated Scripting | 1.18.2..26.3 Forge/Neo (in pack, keep) | MIT | n/a | ~50%: variables, operators, readers, display; scripting addon | Closest to deciders/arithmetic combinators; item/entity logic not wire-and-signal. |
| Redstone Logic Gates (ISC), LogicGates (MIT) | 1.16..1.21.8 / Fabric 26.3 | ISC / MIT | yes | ~10%: gate blocks | Tiny. |
| Create: Circuits | 1.21.1 Neo (2026-05) | MIT | yes | ~15%: Create logic circuits | Needs Create (not in pack). |
| Create: Programmable Logic | 1.20.1 Forge | ARR | no | programmable controller | Skip. |
| Wireless Redstone | 1.12.2..1.20.4 Fabric/Forge/Neo (2026-10) | GPL-3.0 | yes | wireless signal link | Covers wireless leg only. |
Recommendation: CLEAN-ROOM numeric signal wires, constant/arithmetic/decider combinators (nothing gives integer signals on a shared wire); borrow bundled-cable UX from More Red (in pack, MIT) and FOLD Integrated Dynamics operators as the expression engine into diaithir-routing-networks.

## Autonomy (AAI-style self-running factories, robots, full autonomy removing crews)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Satiscraftory | 26.1.2 Neo | GPL-3.0+ | yes | ~30%: chunk-free self-running factory sim | Alpha; closed from other mods. |
| Create: Buzzy Bees (Construction Robots) | 1.20.1/1.21.1 Forge/Neo (2026-11-03) | MIT | yes | ~40%: worker bees, item moves, schematic build | Needs Create. Strong robot prior art. |
| BuildCraft Robotics (original) | b1.4..1.12.2 Forge | depends on version (MMPL/CC-BY) | check | robots with boards | BuildCraft CE (see Pipes) supersedes. |
| Create: Steam Robots | 1.20.1 Forge | MIT | yes | small robot | Minor. |
| TurtleMatic | 1.18.2..1.21.1 (2026-08) | MIT | yes | turtle upgrades | CC:Tweaked addon. |
| MineColonies | 1.18.2 on Modrinth (current builds elsewhere) | GPL-3.0+ | yes (heavy) | NPC workers run buildings | Colony workers = crews; replacing them with machines at Age VII+ is Foundry design. |
Recommendation: CLEAN-ROOM crew-to-autonomy rule (crew slots that machines fill from Age VII); PORT Buzzy Bees for the bee/robot behaviour inside diaithir-logistics-utilities.

## Computers and programming (OpenComputers, ComputerCraft)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| CC: Tweaked (in pack, keep) | 1.15.2..26.3 Fab/Forge/Neo (2026-11-03) | CCPL (custom) | no (adopt as is) | ~80%: computers, turtles, peripherals | In pack at 26.1.2 forge build. Add-ons: NeoPeripherals (MIT), Secure Boot PKI (GPL). |
| OpenComputers | 1.7.10..1.12.2 Forge | MIT | yes (huge) | ~90% but 1.12 | Port is a rewrite. |
| OpenComputers II | 1.21.1 Fab/Neo (2026-10-21) | MIT | yes | RISC-V VM computers | Newest OC lineage; 3.7k dl, early. |
| OC2: Reimagined (+ addons Create/Components/Library/VS) | 1.20.1 Forge | MIT | yes | VM computers, robots | 22.7k dl. |
| *NEW* VM computers | 1.20.1..1.21.1 | GPL-3.0+ | yes | RISC-V VM | Alt VM base. |
| ComputerCraft Greg Flavored / CC Create / Create: Avionics | 1.19..1.21.1 | MIT / CC-BY-SA / MIT | yes | integrations | Reference only. |
Recommendation: ADOPT CC: Tweaked as it is (keep separate); skip OC port (cost high, CCPL-in-pack covers it).

## Belts, lanes, splitters, inserters, balancers, assemblers (diaithir-routing-networks)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Conveyors & Automation (Zetakron) | 1.21.1..26.3 Fab/Neo | MIT | yes | ~75%: 2-lane belts, undergrounds, splitters, filter splitters, 5 inserter kinds, funnels, auto crafter | No 26.1 build; source repo not found. Balancers and assembler recipe lock missing. |
| Simple Conveyor Belts (Rearth) | 1.21.1..26.1.2 Fab/Neo | CC-BY-4.0 | yes (credit) | ~25%: spline belts, no lanes | Verify no lanes. Fits curved/long haul. |
| Simple Conveyors | 26.1.x datapack | MIT | yes | entity conveyors via terracotta | Trivial. |
| Create Chain/Vertical Conveyors, More Conveyor | 1.20.1..1.21.1 | MIT | yes | Create-based | Needs Create. |
| Conveyor Belts (BillBodkin) | 1.18.2..1.21.1 Fabric | MIT | yes | basic belts | Minor. |
| Satiscraftory | 26.1.2 Neo | GPL-3.0+ | yes | belts/splitters/assemblers in own sim | Not interoperable. |
| Factorization | 1.2.5..1.8.9 Forge | MIT | yes | sorter/router machines, barrels | Idea only. |
| Modular Routers / LaserIO / BBL Routers (in pack) | 26.x | MIT | n/a | inserter/router logic | Already in. |
| Assembler-style: none found | n/a | n/a | n/a | 0% | AE2 molecular assembler addons are AE2-bound. |
Recommendation: PORT Conveyors & Automation into diaithir-routing-networks (belts, splitters, inserters); CLEAN-ROOM balancers and recipe-locked assembler.

## Modules and beacons / upgrades on all working blocks (diaithir-automation-crafting, diaithir-upgrades)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Mekanism upgrades (in pack) | 26.1.2 Neo | MIT | n/a | speed/energy/muffling cards on Mek machines only | Pack-internal. |
| Modern Industrialization (in pack) | 26.1.2 | MIT | n/a | overclocks, hatches | MI Parallel Control Hatch / hatch stack addons (MIT/ARR) 1.21.1. |
| AE2 Overclocked, AEInfinityBooster | 1.20.1..1.21.1 / 26.1.2 | LGPL-3.0 | yes | per-block boosters in AE2 | AE2 only. |
| Tech Reborn New Upgrades | Fabric 26.1..26.3 | MIT | yes | Tech Reborn upgrade slots | Fabric. |
| Energized Power, Ender IO, Oritech (in pack) | 26.1.2 | MIT/Unlicense/CC-BY | n/a | per-mod upgrade items | Each mod its own. |
Recommendation: CLEAN-ROOM global module/beacon system (already specced in UPGRADES.md; no mod does cross-mod modules); keep per-mod upgrades as is.

## Research tree, operator seat, science packs (diaithir-automation-crafting)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Researcher (Tr100000) | 1.21.11..26.3 Fabric | MIT | yes | data-driven research and science items | Fabric to Neo port. |
| Research Tree (Wolfieboy09) | 1.21.1 Neo | Apache-2.0 | yes | data-driven tree GUI (G key) | Second source. |
| Researchd | 1.21.1 Neo | custom (Common Sense) | no | Factorio-ish research | Inspiration. |
| The Package Mod | 1.12.2 | LGPL-3.0 | yes | research and bulk crafting | Old. |
| Research Station (MarvinEckhardt) | 1.21.1 Neo | ARR | no | station | Skip. |
| Galactic Research (igentuman) | 1.12.2 | MIT | yes | research sci-fi | Old, idea. |
| Game Stages / Item Stages / Recipe Stages | 1.11..1.20.3 Forge | LGPL-2.1 / MIT | yes | progress gating | Gate backend; not a tree. |
Recommendation: PORT Researcher (MIT) + Research Tree (Apache) merged into diaithir-automation-crafting; operator seat and packs CLEAN-ROOM.

## Machine power in W, SI units, energy/fluid conversion (diaithir-units)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Mekanism (in pack) | 26.1.2 homebaked | MIT | n/a | ~30%: selectable energy unit display (J/FE/EU/T) per mod | Display setting inside Mekanism only; no cross-mod conversion. |
| Dynamic Electricity | 1.21.1..1.16.5 Forge/Neo | MIT | yes | ~15%: volts/amps grid | Idea for V/A model; no SI conversion layer. |
| Flux Networks, Applied Flux (in pack) | 26.1.2 | MIT / LGPL-3.0 | n/a | ~10%: FE bridging to other buses | Bridges transport, not units. |
| Mekanism Matter | 1.18.2..1.16.5 Forge | MIT | yes | tiny: unit-converting blocks | Dead (2024). |
Recommendation: CLEAN-ROOM diaithir-units (no mod unifies units across mods; UNITS.md spec stands).

## Courier depots, construction robots, ghost placement (diaithir-logistics-utilities)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Create: Buzzy Bees (StaticFX) | 1.21.1..1.20.1 Forge/Neo (2026-11-03) | MIT | yes | ~40%: construction bees, schematic place/destroy, item moves | Needs Create (not in pack); source github.com/StaticFX/Create-Construction-Robots. |
| Create More: Package Couriers (Krei) | 1.21.1..1.20.1 | Lambda License (custom) | no | package couriers | Licence blocks; Create only. |
| Drone Logistics | 1.21.4..1.20.1 | ARR | no | drone item moves | Skip. |
| Not Logistics Pipes / Logistics Pipes | 1.20.2..1.20.1 / 1.12.2 | LGPL-3.0 / MMPL | NLP yes | request/provider routing | See Pipes section. |
| Portable Blueprints (Nimblonia) | 1.21.1..1.19.2 Forge/Neo | MIT | yes | ~20%: save and place builds | Ghost-like placement UX. |
| Effortless Building (Requios) | 26.3..1.19.2 Fab/Forge/Neo (NeoForge 26.3 build checked 11-03) | LGPL-3.0-only | yes | ~20%: build modes, mirror, replace | 26.1.2 build exists per tech-transport csv (not re-checked). |
| Building Gadgets 2 (Direwolf20) | 1.21.1 Neo per memory | unverified (memory: MIT) | unverified | ~25%: copy/paste gadget, template | Not on Modrinth under any slug I tried; CurseForge-only, so licence and newest MC are unverified. Addons on Modrinth: BG2 AE2 Addon (MIT), BG RS Bridge (MIT, 26.1). |
| MineColonies | 1.18.2 on Modrinth (current builds elsewhere) | GPL-3.0+ | yes (heavy) | NPC builders | Too big; reference. |
Recommendation: PORT Buzzy Bees into diaithir-logistics-utilities; FOLD Effortless Building (LGPL) build modes as the ghost/plan table UI; Not Logistics Pipes for requests.

## Pipes: items, fluids, energy (diaithir-pipes)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Tiny Pipes (in pack) | 26.3..1.20 Forge/Neo | GPL-3.0+ | yes | ~50%: item/fluid/energy pipes | Keeper. |
| Pipe Connector (in pack) | 26.x | MIT | yes | ~15%: pipe linking | |
| Pipez (in pack) | 26.3..1.19 | ARR | no | ~60%: item/fluid/energy/gas pipes | Clean-room per audit. |
| Classic Pipes (in pack) | 26.2..1.20.1 | CC-BY-NC-SA-4.0 | no | ~40%: BuildCraft style pipes | Clean-room. |
| BuildCraft Community Edition | 26.3 Neo..1.12.2 (per 11-02 survey, unverified here) | MPL-2.0 | yes | ~60%: pipes, engines, quarry, robots | Port PR #108. |
| Copper Item Pipes | 26.2..1.21.2 | MIT | yes | ~10%: simple item pipe | |
| Fluid Pipes / Mini (pinter.gabor) | 26.2..1.21.4 Fab/Neo | MIT | yes | ~15%: fluid pipe | |
| XNet (McJty) | 26.3..1.10.2 Fab/Forge/Neo | MIT | yes | ~50%: item/fluid/energy channels | Needs McJtyLib (MIT). |
| Refined Pipes | 1.18.2..1.15.2 Forge | MIT | yes | ~20%: item pipes | Dead (2023). |
| Curvy Pipes | 26.1.2..1.7.10 | ARR | no | spline visuals | Inspiration. |
| Unflavoured Pipes | 1.21.11..1.20.1 Fab/Forge | AGPL-3.0 | yes | ~20%: item/fluid pipes | AGPL. |
Recommendation: FOLD Tiny Pipes + Pipe Connector + BuildCraft CE pipes (+ XNet channels) into diaithir-pipes; CLEAN-ROOM only the Pipez and Classic Pipes parts.

## Routers, wireless and linked networks
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Modular Routers, BBL Routers, LaserIO (in pack) | 26.2..1.16.5 | MIT | yes | ~70%: routers with modules | Folded in routing-networks. |
| Flux Networks (in pack) | 26.1.2 | MIT | yes | wireless energy | |
| Quick Link (Wireless Logistics) | 26.3..1.20.1 Forge/Neo | MIT | yes | ~20%: wireless link to storage | |
| Refined Wireless Upgrades (Ultramega) | 26.1.2..1.20.1 | MIT | yes | RS wireless | RS only. |
| Tesseract (SuperMartijn642) | 26.3..1.12 | ARR | no | linked tunnels | Clean-room. |
| Linked Chests (Fuzs), DimStorage | 26.x | MPL-2.0 / AGPL-3.0 | yes | linked inventories | In pack. |
Recommendation: FOLD (already) routers into diaithir-routing-networks; Tesseract-like clean-room.

## AE2 and addons, Integrated Dynamics, Logistics Pipes, BuildCraft, Factorization
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Applied Energistics 2 (in pack) | 26.3..1.18 | multiple | keep | ~100% storage network | Addons in diaithir-ae2-extensions: ExtendedAE, AdvancedAE, wireless terminals, import/export card, ME Requester, AEInfinityBooster. |
| Applied Mekanistics | 1.21.1..1.18.2 | LGPL-3.0 | yes | Mek chemicals in AE2 | No 26.1 build. |
| Refined Storage | 26.1.2..1.9 Fab/Forge/Neo | MIT | yes | alternative storage | Duplicate of AE2; not in pack. |
| Integrated Dynamics/Tunnels/Terminals/Crafting/Scripting | 26.3..1.18.2 | MIT | n/a | logic cable network | In pack. |
| Logistics Pipes (Bernasss12) | 1.12.2 | MMPL | check | request/provider routing | 4.1k dl on Modrinth; 13.8M on CF. |
| Not Logistics Pipes | 1.20.2..1.20.1 Fab/Forge/Neo | LGPL-3.0 | yes | clean routing | Port base. |
| Logistic Pipes 2 | 1.20.1 Forge/Neo | custom | no | revival | |
| BuildCraft (original) | 1.12.2..b1.4 | depends on version | check | pipes/builders/robots | CE supersedes. |
| Factorization | 1.8.9..1.2.5 | MIT | yes | sorter/router machines | Design reference. |
Recommendation: ADOPT AE2 + addons (in pack); PORT Not Logistics Pipes into diaithir-pipes as the request network.

## Storage: drawers, backpacks, linked chests, quick stack/restock/sort
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Storage Drawers, Functional Storage, Colossal Chests, Tom's Storage | 26.1.x | MIT | n/a | drawers, big chests, terminals | In pack. |
| Echo Chest, Nether Chested, Linked Chests (Fuzs) | 26.1 Neo | MPL-2.0 | yes | special chests, linked | In pack. |
| Sophisticated Backpacks/Storage (in pack) | 26.3..1.16.5 | ARR | no | ~95% backpacks | Clean-room route in audit. |
| Traveler's Backpack | 26.3..1.12.2 Fab/Forge/Neo (2026-11-02) | LGPL-3.0 | yes | ~60%: backpacks, upgrades | Open alternative. |
| Inventory Profiles Next | 26.3..1.14.1 | AGPL-3.0+ | yes | ~90%: sort, move matching, restock | AGPL. |
| Client Sort (in pack) | 26.1.2 | Apache-2.0 | yes | sort | |
| Terrastorage (TimVinci) | 26.3..1.20 Fabric/Quilt (26.1.2 build exists) | MIT (verified 11-03) | yes | ~60%: quick stack to nearby chests, restock | Fabric only; port to NeoForge. |
| Inventory Sort, Serverside Chest + Inventory sort | 1.20.1 Forge / 26.3 Fabric | Apache-2.0 / AGPL-3.0+ | yes | sort | |
Recommendation: FOLD Traveler's Backpack into diaithir-sophisticated-portable (replaces clean-room); PORT Terrastorage quick stack into diaithir-inventory-ui.

## Filter system
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Item Filters (Lat) | 1.20.1..1.19.2 Fabric/Forge | GPL-3.0 | yes | ~60%: filter items by tag/NBT/mod | Dead since 2023. |
| Item Filter (ThBTT) | 1.21.1 Fabric | MIT | yes | ~20%: simple filter | |
| Conveyors & Automation filter splitters | 26.3 Neo | MIT | yes | ~30%: per-lane item filter | |
| Mekanism / AE2 / Modular Routers filters (in pack) | 26.x | MIT / LGPL | n/a | per-mod | |
Recommendation: FOLD Item Filters (GPL) as the shared filter item into diaithir-routing-networks.

## Miners and quarries (diaithir-miners)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Intelligence: Quarry (in pack) | 26.1.2..1.19.2 | MIT | n/a | ~60%: quarry | In. |
| Additional Enchanted Miner (in pack) | 26.1.2 | LGPL-3.0 | n/a | ~40%: miner | In. |
| Immersive Machinery (in pack) | 26.1.2 | GPL-3.0+ | n/a | ~30%: excavators, drills | In. |
| BuildCraft CE | 26.3 | MPL-2.0 | yes | ~60%: quarry with frame | Unverified here. |
| Quarry Reborn / Simple Quarry / RetroRig: Quarry | 1.20.4 / 1.21.4 / 26.1.2 | CC-BY-NC-4.0 / ARR / ARR | no | quarry | Skip. |
| Advanced Ore Deposits | 1.21.1 Neo | MIT | yes | ~50%: depletable ore patches | |
| FactoriOres | 1.16.5 Forge | MIT | yes | ~50%: ore patches + miners | |
Recommendation: FOLD (already) quarries into diaithir-miners; PORT Advanced Ore Deposits for patches.

## Power generation and storage (diaithir-power-storage)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Powah, Mekanism Generators, Energized Power, Ender IO Endergy, Oritech (in pack) | 26.1.2 | LGPL-3.0 / MIT / Unlicense / CC-BY-4.0 | n/a | ~85%: generators, storage tiers | In pack. |
| Extreme Reactors | 1.21.1..1.9.4 | MIT | yes | ~15%: big fission/turbine | Fills large-reactor gap. |
| Just A Battery, Battery Box | 1.21.8..1.18.1 | LGPL-3.0 | yes | ~10%: batteries | |
| Create Diesel Generators | 1.21.1..1.18.2 | MIT | yes | Create generator | Needs Create. |
| Solar Panel v2 | 1.21.1..1.20.1 | MPL-2.0 | yes | solar | |
Recommendation: ADOPT (in pack); PORT Extreme Reactors if a large reactor is wanted.

## Mekanism and addons
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Mekanism + Generators/Tools/Additions | 26.1.2 homebaked (in pack); Modrinth 1.21.1 | MIT | n/a | 100% | |
| Mekanism Extra, More Mekanism Processing | 1.21.1 | MIT | yes | extra tiers, ore chains | |
| Better Fusion Reactor for Mekanism, JEMM | 1.21.1 | MIT | yes | addons | |
| Applied Mekanistics | 1.21.1 | LGPL-3.0 | yes | AE2 bridge | |
Recommendation: ADOPT 26.1.2 build as-is (pack-eligible); fold addons selectively.

## Thermal / IE / GregTech / Modern Industrialization / PneumaticCraft
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Thermal Expansion/Foundation, CoFH Core | 1.20.1 Forge/Neo..1.16.5 | ARR | no | full Thermal | Clean-room. |
| Thermal: Extra | 1.21.5..1.16.5 | MIT | yes | addon | |
| Immersive Engineering | 1.21.1..1.12.2 | custom (Blu) | no | multiblocks, wires | Reference. |
| GregTech CEu Modern | 1.21.1..1.19.2 (26.1 branch per tech-transport, unverified) | LGPL-3.0+ | yes | deep GT | |
| Modern Industrialization (in pack) | 1.21.1..1.16.2 (26.1.2 build) | MIT | n/a | ~100% | |
| PneumaticCraft: Repressurized (in pack) | 1.21.1..1.16.5 | LGPL-2.1 | n/a | ~100% | |
Recommendation: ADOPT MI + PNC (in pack); PORT GregTech Modern from its 26.1 branch; CLEAN-ROOM Thermal.

## Metal processing foundry, ore chains (diaithir-metal-processing)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| JAOPCA (in pack) | 26.1.2..1.7.10 | MIT | yes | ~40%: auto ore/ingot variants | |
| Silent's Gems (in pack) | 26.1.x | MIT | yes | gems/metals | |
| Productive Metalworks (in pack) | 26.1.x | ARR | no | ~60%: foundry/alloy | Clean-room. |
| Tinkers' Construct (+ unofficial 1.21.1 port) | 1.20.1..1.6.4 / 1.21.1 Neo | MIT | yes | ~70%: smeltery, casting | |
| Alloy Forgery | 26.1.2..1.17 Fab/Neo/Quilt | MIT | yes | ~40%: alloying | |
| Ol' Foundry | 26.1.2 Fabric | MIT | yes | ~15%: foundry block, slag | |
| Immersive Geology | 1.20.1..1.16.5 | LGPL-3.0 | yes | ~50%: multi-step ore chain | |
| Create: Ore Processing, More Mek Processing | 1.20.1 / 1.21.1 | MIT | yes | ~30%: ore multipliers | |
Recommendation: FOLD Alloy Forgery + Ol' Foundry + Tinkers smeltery logic into diaithir-metal-processing; Immersive Geology chain as design; Productive Metalworks clean-room.

## Farm equipment and farming automation
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Agritech: Evolved (in pack) | 26.1.2 | MIT | yes | ~40%: farming machines | |
| Hydrofarm | 26.3..26.1 Fab/Neo | MIT | yes | ~30%: sprinklers, hydroponic beds, tanks | |
| RightClickHarvest (in pack) | 26.x | MIT | yes | hand harvest | |
| Farming for Blockheads (in pack) | 26.1.2 | ARR | no | market/field | Clean-room. |
| Little Tractor | 1.20.1..1.18.2 | ARR | no | tractor | Skip. |
| AutoFarm-Mod | 26.3 Fabric | CC-BY-NC-4.0 | no | auto farm | Skip. |
| Create: Buzzy Bees | 1.21.1 | MIT | yes | bees move items | See robots. |
Recommendation: none found for digging stick to combine harvester ladder; CLEAN-ROOM tool/machine ladder, FOLD Hydrofarm and Agritech.

## Pollution / Unrest / nests
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Pollution of the Realms | 26.3..1.20.1 | CC-BY-ND-4.0 | no | ~50%: chunk pollution | No-derivatives. |
| Pollution Plus | 1.20.1..1.12.2 | MIT | yes | ~30%: pollution | |
| Compressed Pollution | 1.20.1 | LGPL-2.1 | yes | pollution API | |
| Luki and Pollution | 1.14.4..1.12.2 | CC-BY-NC-4.0 | no | pollution | |
| Create: Smog | 1.21.1 | MIT | yes | Create-only | |
Recommendation: CLEAN-ROOM Unrest and nests (no nest-spawn-on-pollution mod found); Pollution Plus (MIT) as reference.

## Quality and recycling
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Quality Food | 26.1.2 Neo..1.18.2 | MIT | yes | ~20%: tiered food | Food only. |
| Tierify | 1.20.4 Fabric | MIT code, ARR assets | partial | gear tiers | Fabric. |
| Recycler Block (quarkesh), Mace Recycler | 1.20.1 / 1.21.1 | MIT | yes | ~10%: recycle one item | |
| Scrap / other recyclers | various | ARR | no | | |
Recommendation: CLEAN-ROOM quality grades and Reclaimer; reuse Quality Food component design.

## Items-per-minute meters
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Mekanism / Powah / AE2 readouts (in pack) | 26.x | MIT / LGPL | n/a | per-mod stats | |
| Conveyors & Automation | 26.3 | MIT | yes | counts only if unverified | Unverified. |
| Modrinth queries "items per minute", "production statistics" | | | | none | No dedicated mod found. |
Recommendation: CLEAN-ROOM.

## Interdimensional logistics
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Interdimensional Wireless Transmitter (Ultramega) | 26.1.2..1.16.2 Fab/Forge/Neo | MIT | yes | ~40%: cross-dimension RS link | RS-bound. |
| DimStorage (in pack) | 26.1.2 | AGPL-3.0 | yes | ~50%: dimension-wide storage | |
| Interdimensional (genau6502) | 1.18.1 Fabric | LGPL-3.0 | yes | dimension travel, not logistics | |
| Ender Logistics Network | 1.21.1 | MIT | yes | ~30%: ender item network | 286 dl. |
Recommendation: FOLD DimStorage + Interdimensional Wireless Transmitter into diaithir-linked-storage.

## Age-evolving crafting stations / station ladder
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Crafting Station: J/EMI Edition Updated | 26.3..1.19.2 | MIT | yes | ~15%: bigger crafting table | |
| Sprawl Crafting | 26.2..1.12.2 Fab/Forge/Neo | MIT | yes | ~25%: hand-craft queue | |
| Extended Crafting (in pack) | 26.1.2 | MIT | n/a | ~40%: tiered tables | |
| Portable Crafting | 1.21.1..1.18.2 | LGPL-3.0 | yes | portable bench | |
| Primum Opus, Flint Required | 1.19.4 / 1.21.1 | MIT / ARR | partial | primitive start | |
| Game Stages / Recipe Stages | 1.20.3 Forge | LGPL / MIT | yes | gating | |
Recommendation: FOLD Extended Crafting + Sprawl Crafting into diaithir-automation-crafting; the Age ladder (minimal grid, things made at stations) CLEAN-ROOM.

## Chunk loaders, force fields (MFFS), elevators
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Chunk Loader (2mal3) | 1.21.1..1.19 all loaders | LGPL-3.0 | yes | ~80%: chunk loader | |
| Chunk Loaders (SuperMartijn642) | 26.3..1.12 | ARR | no | | |
| Copper Chunk Loader | 26.3..1.21.2 | CC-BY-NC-SA-4.0 | no | | |
| MFFS (QueenOfMissiles) | 26.1.2..1.20.1 | ARR | no | ~70%: force fields | |
| Modular Force Field Systems (aurilisdev) | 1.21.1..1.18.2 | custom | no | | |
| ElevatorMod (VsnGamer) | 26.3..1.12.2 | MIT | yes | ~80%: elevators | |
| OpenBlocks Elevator (in pack) | 26.1 | MIT | n/a | elevator | |
| Moving Elevators | 26.3..1.12 | ARR | no | | |
Recommendation: PORT Chunk Loader (2mal3), FOLD ElevatorMod; CLEAN-ROOM MFFS.

## Power poles / grids, fluid tanks, sieves / cobble gens
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Flux Pylons | 1.21.1..1.20.1 | custom | no | ~30%: pole-like wireless | |
| Large Fluid Tank | 26.3..1.12.2 | MIT | yes | ~60%: multiblock tank | |
| Tank Storage | 1.21.1..1.20.1 | MIT | yes | tanks | |
| Hydrofarm tanks | 26.3 | MIT | yes | merging tanks | |
| Cobblestone Generator (ChinaEX123) | 26.3..1.21.1 Neo | CC-BY-4.0 | yes | ~70%: cobble gen | |
| Create cobble/deepslate generators | 1.21.1..1.20.1 | CC0-1.0 | yes | | Create only. |
| Cobblegen Galore (in pack) | 26.1.2 | ARR | no | | Clean-room. |
| Fabricae Ex Nihilo | 1.20.6..1.18.2 Fabric | MIT | yes | ~60%: sieves, crooks | Port base for sieve. |
| Ex Nihilo: Sequentia | 1.21.4..1.19.2 | CC-BY-NC-SA-4.0 | no | | |
Recommendation: CLEAN-ROOM power poles (supply-area; none found); FOLD Large Fluid Tank; PORT Fabricae Ex Nihilo sieves and Cobblestone Generator.


---

<!-- part4_society_progression.md -->
# Part 4: society, progression, knowledge, world events (survey 2026-11-03, tidy pass)
Method: Modrinth API (all versions) + in-pack audit (plans/PACK_CONSOLIDATION_AUDIT.csv, COMPAT_MATRIX.csv, EXCLUSIONS.md). GitHub API blocked in session (add_repo not enabled); GitHub/CurseForge pages read via WebFetch. Version ranges are newest..oldest of builds seen (Modrinth uploads unless noted; older CF builds not seen). Licence verified on the primary page where marked; else "unverified". "In pack" = 26.1.2 jar already in audit.
Primary-page licence checks (11-03): MineColonies github.com/ldtteam/minecolonies = GPL-3.0 (LICENSE file; no separate asset licence stated). FTB Quests CurseForge = All Rights Reserved (GitHub repo shows no licence, so no grant either). FTB Chunks CurseForge = All Rights Reserved. FTB Ranks CurseForge = All Rights Reserved. Millenaire CurseForge = "Custom License" (terms page not read, port allowed = unverified). True Ending Modrinth = Custom (terms at github.com/SpluoSplatus/Vanilla-Refresh/wiki/License, not read, unverified). FTB Essentials/Teams/Library: ARR per pack audit only (CF page not fetched, unverified).
Pack facts: MineColonies main jar not in pack (COMPAT_MATRIX: "MineColonies port (already queued)"); Structurize, BlockUI, Domum Ornamentum are diaithir builds (GPL-3.0).

## NPC wages and employer treasuries (economy / diaithir-villager-trade)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Lightman's Currency (Lightman) modrinth.com/mod/lightmans-currency | 26.1.2..1.16.4 all loaders | Apache-2.0 | yes | ~40%: wallets, traders, bank accounts, trader taxes | in pack (our fork); no NPC payroll |
| Minecolonies: War N Taxes Addon (Machiavellian) modrinth.com/mod/minecolony-tax-addon | 1.20.6..1.20 forge | MIT | yes | ~25%: colony taxes | needs MineColonies; abandoned |
| Workers Plus (nivthefox) modrinth.com/mod/workersplus | 1.20.1 forge | BSD-3-Clause | yes | ~10%: hired workers | depth unverified |
| Villager Workers (talhanation) modrinth.com/mod/villager-workers | 1.20.1..1.18.2 forge | ARR | no | ~20%: hired villagers | abandoned |
Strikes/revolts: none found.
Recommendation: FOLD Lightman's Currency treasury/tax code into diaithir-villager-trade; wages, strikes, revolts CLEAN-ROOM (nothing usable).

## NPC jobs/professions (diaithir-villagers-npcs)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| MineColonies (ldtteam) github.com/ldtteam/minecolonies | CF/GitHub newer; Modrinth 1.18.2 only | GPL-3.0 (verified GitHub) | yes | ~85%: ~20 worker huts, citizen skills, happiness | port queued; assets licence not stated |
| Millager (LZYZL6) modrinth.com/mod/millager | 26.2..1.20.1 | MIT | yes | ~25%: military/summoner roles | in pack |
| More Professions (Pepsied) modrinth.com/mod/more-professions | 26.2..1.21 | MIT | yes | ~15% extra POI jobs | |
| Villager Professions Plus (Rhonan) | 1.20.6..1.20.1 fabric | CC0-1.0 | yes | ~10% | |
| Custom Villager Professions (SpaceCat97) | 1.20.1..1.19.2 | ARR | no | POI jobs | |
| Millenaire (Kinniken) curseforge.com/minecraft/mc-mods/millenaire | 1.12.2 and older (Modrinth only has addons) | Custom License (verified CF; terms unread) | unverified | ~60% culture villages with jobs/trade/construction | closest ancestor of culture villages |
Recommendation: PORT MineColonies into diaithir-villagers-npcs; FOLD More Professions POI list. Millenaire stays CLEAN-ROOM reference until its custom terms are read.

## Villager trading (diaithir-villager-trade)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Trading Post (Fuzs) modrinth.com/mod/trading-post | 26.3..1.19 all loaders | MPL-2.0 | yes | ~70% mass-trade UI | in pack |
| Villager Trading Plus (Cassian) modrinth.com/mod/trading-plus | 26.3..1.20 | MIT | yes | ~60% | in pack |
| Your Reputation (Aton-Kish) + Port (FR13NDS_Krypton) | 26.3..1.19 fabric | MIT | yes | villager rep pricing | |
| Mercantile - Villager Overhaul (rfizzle) | 1.21.1 fabric | MIT | yes | trade UI/economy | |
| Bulk Villager Trading (bradcarnage) | 1.20.6..1.20.1 forge | MIT | yes | ~30% | dup |
Recommendation: ADOPT in-pack Trading Post + Villager Trading Plus merge into diaithir-villager-trade; FOLD Your Reputation.

## Trading posts, merchants, caravans (diaithir-villager-trade)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Better Caravans (Nikrecs) modrinth.com/mod/better-caravans | 26.3..1.19.2 | MIT | yes | ~50% roaming caravans | audit keeper over Pillager Caravans (ARR) |
| Wandering Trader Plus (Semi) | 1.21.8..1.16.5 | MIT | yes | trader stock | |
| Better Wandering Traders (DrexHD) | 26.3..1.21.5 | MIT | yes | | |
| Villager Caravan (ctkrocks) | 1.21.1..1.21 | MIT | yes | ~40% | |
| Minecolonies Caravans (Derunation) | 1.21.1 neoforge | MIT | yes | colony caravans | needs MineColonies |
| Wandering Trader Maps (lullaby) | 26.3..1.21 | LGPL-3.0-or-later | yes | map sales | |
Recommendation: FOLD Better Caravans + Wandering Trader Plus into diaithir-villager-trade; culture stock is ours.

## Economy, currency, markets, banks, taxes (diaithir-villager-trade)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Lightman's Currency | 26.1.2..1.16.4 | Apache-2.0 | yes | ~75%: coins, shops, auctions, banks, taxes | in pack, ours; LC Tech add-on Apache-2.0 1.21.1..1.16.5 |
| Spud's Shops | 1.21.11..1.20.1 | MIT | yes | shop blocks | |
| Banking System (Splinter) / Diamond Banking | 1.21.5..1.16 / 26.1 | MIT | yes | simple banks | |
| EconomyMc | 26.2..1.21.4 | GPL-3.0-only | yes | balances | |
| Create: Stock Market (Deokma) | 1.21.1 | AGPL-3.0-only | yes (copyleft) | stock market | |
| FSMM (Fexcraft) | 26.1.2..1.12.2 | custom | unverified | money/ATM | |
Recommendation: ADOPT Lightman's Currency as-is (pack-eligible); price/tax rules per culture CLEAN-ROOM.

## MCA-style social NPCs and relationships (diaithir-villagers-npcs)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| MCA Reborn (Luke100000) modrinth.com/mod/minecraft-comes-alive-reborn | 26.2..1.16.5 all loaders | GPL-3.0-only | yes | ~90%: marriage, children genetics, gifts, moods | in pack 8.1.11 |
| MCA Quests / Conversations (otectus) | 1.21.1..1.20.1 | GPL-3.0+ / LGPL-3.0+ | yes | dialogue + quest add-ons | |
| MCA Romantic Expansion | 26.2..1.20.1 | GPL-3.0-only | yes | | |
| MCA Expanded (diacritics-owo) | 1.20.4..1.20.1 fabric | MIT | yes | | |
| Easy NPC (Kaworru) | 26.3..1.18.2 | MIT | yes | dialogue NPCs | in pack |
Recommendation: PORT MCA Reborn into diaithir-villagers-npcs; FOLD MCA Quests/Conversations ideas.

## Factions, kingdoms/polities, diplomacy, war (diaithir-villagers-npcs)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Tale of Kingdoms: New Conquest (SamB440) | 1.21.1..1.16.5 fabric | LGPL-3.0-only | yes | ~40% kingdoms, taxes | |
| MCA Capitals (MajesttyX) | 1.21.1..1.20.1 | GPL-3.0 | yes | ~35% monarchy on MCA | |
| Easy Factions and Claims (OverWatter) | 1.21.1..1.20.1 | MPL-2.0 | yes | ~35% | |
| Factions (ickerio) | 26.3..1.17 fabric | MIT | yes | ~30% | |
| OPAC: Warfare (svinpepe) | 26.3..1.20 | MIT | yes | claim war | |
| Siege of Settlements | 1.20.1 | LGPL-3.0-only | yes | sieges | |
| Villager Recruits (talhanation); Village Diplomacy; Diplomacy | 1.20.1.. | ARR | no | armies/diplomacy | |
Recommendation: FOLD Tale of Kingdoms + MCA Capitals + Warfare into diaithir-villagers-npcs; diplomacy/war rules CLEAN-ROOM.

## Claims / chunk claims (social)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Open Parties and Claims (thexaero) | 26.3..1.18.2 | LGPL-3.0-only | yes | ~95% | dropped for FTB Chunks |
| FTB Chunks | 26.1.2 (pack) | ARR (verified CF) | no | claims+map | in pack |
| OPAC Essentials (swzo) | 1.21.1 neoforge | Apache-2.0 | yes | extras | |
Recommendation: PORT Open Parties and Claims into diaithir-admin-core, retiring the ARR FTB chain; reason: only open 26.x-maintained claims mod.

## Village defenders / guards (diaithir-villagers-npcs)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Millager (LZYZL6) | 26.2..1.20.1 | MIT | yes | ~70% | in pack |
| Guard Villagers Fabric/Quilt (mrsterner) | 26.2..1.18.2 | MIT | yes | ~80% guard behaviour | replaces clean-room |
| Guard Villagers (seymourimadeit) | 26.3..1.16.5 | custom | no | guards | in pack |
| Villager Guards (lullaby) | 26.3..1.21 | AGPL-3.0+ | yes (copyleft) | | |
Recommendation: PORT Millager, FOLD mrsterner's MIT Guard Villagers.

## Settlements / colony building (MineColonies, Structurize)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| MineColonies | see jobs | GPL-3.0 (verified) | yes | ~90% | |
| Structurize / BlockUI / Domum Ornamentum | pack | GPL-3.0 | yes | schematics, UI, blocks | ours |
| Better With Minecolonies (kreezxil) | 1.21.1..1.14.4 | MIT | yes | tweaks | |
| Pathfinding Edition for MineColonies | 1.21.1..1.20.1 | GPL-3.0-only | yes | | |
| Settlement Roads (Countered) | 1.21.10..1.20.1 | MIT | yes | roads | |
Recommendation: PORT MineColonies atop our Structurize/BlockUI/Domum.

## Quests / questbooks / Bethesda-style quests (diaithir-quests-skills)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| FTB Quests | 26.1.2 (pack) | ARR (verified CF; GitHub no licence) | no | questbook | clean-room |
| Hardcore Questing Mode (lorddusk) | 1.21.1..1.20.4 (orig 1.7.10) | LGPL-3.0-only | yes | ~70% | |
| Not Quests (Alessio) | 26.3..1.17 neoforge | GPL-3.0-only | yes | ~60% | |
| JustQuests (ErikEdits) | 26.3..1.18.2 | GPL-3.0+ | yes | | |
| Odyssey Quests | 1.21.1..1.20 | MIT | yes | | |
| Chapters (gabinx) | 26.1.2..1.21.1 | MIT | yes | chapter gating | |
| Village Quest (topasmusic) | 26.3..1.21.11 | LGPL-3.0+ | yes | NPC quests | |
Recommendation: PORT Not Quests (or HQM) as base for diaithir-quests-skills; quest content CLEAN-ROOM.

## Skill trees (diaithir-quests-skills)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Puffish Skills | 26.1 (pack) | ARR (audit) | no | engine | |
| Default Skill Trees (Pufferfish) | 26.3..1.18.2 | CC0-1.0 | yes | tree data | |
| Stronger Skill Tree | 26.3..1.18.2 | MIT | yes | data | |
| Iron's Spells Dynamic Skill Trees | 1.21.1..1.19.2 | MIT | yes | | |
| Skill Tree Fabric (JammingDino) | 1.20 | Apache-2.0 | yes | tiny | |
Recommendation: CLEAN-ROOM engine; FOLD CC0/MIT tree data.

## Ages as tech tree on shared server year, age gates (diaithir-progression)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Chapters (gabinx) | 26.1.2..1.21.1 | MIT | yes | ~30% stage gating | |
| SDM GameStages (Sixik) | 1.20.1..1.19.2 | MIT | yes | ~40% | |
| Hexstages / Mob Stages (Darkhax) | 1.20.1 / 1.12.2 | MIT / LGPL-2.1 | yes | | |
| Hex Research; Old Research | 1.19.2 / 1.12.2 | MIT | yes | research UI | |
Civilization-style tree with calendar year: none found.
Recommendation: CLEAN-ROOM (graph.json is source); FOLD Chapters stage checks.

## Codex / Civilopedia replacing JEI (diaithir-codex)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Modonomicon | 26.1.2 (pack) | MIT AND CC-BY-4.0 | yes | book engine | in pack |
| GuideME | pack | multiple OSS | partly | | in pack |
| Minepedia (Minehendrix) | 26.3..1.20.4 fabric | MIT | yes | in-game wiki | |
| Biology Dictionary | 26.3..1.20.1 | LGPL-3.0-only | yes | creature dictionary | |
| Guide-API VP (maxanier) | 26.1.2..1.16.4 | MIT | yes | | |
| Patchouli (Vazkii) | 26.1.2..1.12.2 | CC-BY-NC-SA-3.0 | no | | |
Recommendation: FOLD Modonomicon as Codex renderer; CodexService stays CLEAN-ROOM.

## Panscriptum/Library books, lore books, in-game libraries
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| RPG Lore (otectus) | 1.21.1..1.20.1 | MIT | yes | ~10% lore books | |
| Ancient Library (MissileMann) | 1.20.1 | MIT | yes | library structure | |
| Loremaster | 1.21.1..1.20.1 | MIT | yes | | |
| Babel - Lore Books Loot (JiFish) | 1.21.11..1.21 | ARR | no | | |
Recommendation: CLEAN-ROOM (699k real entries via sqlite store); no mod does this.

## Assaying and magnitude (ore assay, geology survey)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Precision Prospecting (Notenoughmail) | 1.21.1..1.18.2 | EUPL-1.2 | yes (copyleft) | ~60% readouts | |
| Ore Detector (pinter.gabor) | 26.2..1.20.2 | MIT | yes | ~40% | |
| Ore Scanner (dqwertyc.dev) | 26.3..1.21.11 | MIT | yes | | |
| Prospecting Picks / Tools | 1.21.1..1.20.1 | MIT | yes | ~40% | |
| Immersive Geology | 1.20.1..1.16.5 | LGPL-3.0-only | yes | strata | |
| Project Rankine | 1.18.2..1.16.5 | MIT | yes | | |
Recommendation: FOLD Ore Detector/Precision Prospecting readouts into diaithir-worldgen-structures; magnitude numbers CLEAN-ROOM.

## Atlas, maps, waypoints (diaithir-map-utility)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Antique Atlas 3.1.2 (pack) / AA4 | 26.1.2 / 1.21.1..1.19.2 | LGPL-3.0+ code, CC BY-NC-SA textures | code yes | ~90% | textures need replacing |
| Surveyor | 26.1.2..1.20.1 | LGPL-3.0+ | yes | map data | in pack |
| Surveyor Atlases (settingdust) | 1.21.11..1.20.1 | Apache-2.0 | yes | | |
| Server Waypoint | 26.3..1.20 | MIT | yes | waypoints | |
| Xaero's Minimap/World Map | 26.3..1.7.10 | ARR | no | | |
Recommendation: ADOPT in-pack Antique Atlas + Surveyor (port route); FOLD Server Waypoint.

## Culture start picker, 130 cultures, native-language naming (diaithir-culture-start)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Origins (Apace) | 1.21.1..1.16.5 | MIT | yes | ~40% picker | |
| Medieval Origins Revival | 1.21.1..1.19.2 | MIT | yes | | |
| RPG Origins | 1.20.6..1.16.5 | Apache-2.0 | yes | | |
| Villager Names (OverlordsIII) | 1.21..1.16.4 | MIT | yes | name lists | |
Recommendation: FOLD Origins picker UI; cultures and native+English names CLEAN-ROOM (Library data).

## Constructed languages / translation
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| AstraGlossa (AquaAdAstra) | 26.1.2..1.21.1 | EUPL | yes (copyleft) | conlang chat | |
| Language Reload (Jerozgen) | 26.3..1.17.1 fabric | MIT | yes | lang loading | |
Recommendation: CLEAN-ROOM; AstraGlossa reference only.

## Global Events (meteors, blood moon, golden hour)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Global Events (MD22) | 26.3..1.21 fabric | MIT | yes | ~50% | ports #111/#113 |
| Enhanced Celestials (CorgiTaco) | 1.21.1..1.19.2 | LGPL-3.0-only | yes | moons | |
| Oh My, Meteors! (Emafire003) | 26.2..1.19.2 | MIT | yes | meteors | |
| Blood Moon (nugrevan) | 26.2..26.1 | MIT | yes | blood moon | |
| Skyfall: Meteorites | 1.20.1..1.19.2 | Apache-2.0 | yes | | |
Recommendation: PORT Global Events + Oh My Meteors (existing #111/#113 route).

## Calendar / seasons / day-night
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Homeostatic Seasons | pack | MIT | yes | seasons | in pack |
| Chronicle: World Calendar | 1.20.1 fabric | MIT | yes | calendar | |
| Timekeeper (Lunakibby) | 1.21.8..1.20.1 | CC-BY-SA-4.0 | yes (share-alike) | | |
| Serene Seasons; Ecliptic Seasons | 26.3.. | ARR | no | | |
Recommendation: FOLD Homeostatic Seasons + Chronicle; shared server year CLEAN-ROOM.

## Death recovery / graves (diaithir-death-recovery)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Epitaphs | pack | LGPL-3.0 | yes | ~90% | in pack |
| Gravestones (Pneumono) | 26.2..1.20 | MIT | yes | | |
| YIGD (b1n-ry) | 1.21.1..1.16.5 | MIT | yes | | |
| Graves (lullaby) | 26.3..1.21 | AGPL-3.0+ | yes (copyleft) | | |
| Corpse / GraveStone (henkelmax) | 26.3..1.19 | ARR | no | | pack has gravestone ARR |
Recommendation: PORT Epitaphs.

## Admin tools, ranks, permissions, backups (diaithir-admin-core)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Simple Backups (MelanX) | 26.3..1.18.1 | Apache-2.0 | yes | backups | in pack |
| FastBack (pcal43) | 26.3..1.19.2 | GPL-2.0-only | yes | backups | |
| GriefLogger | pack | Apache-2.0 | yes | logging | in pack |
| PermissionGate (ngoclinh_) | 26.2 | MIT | yes | ~20% permissions | tiny |
| FTB Ranks | 26.1.2 (pack) | ARR (verified CF) | no | ranks | |
| FTB Essentials | 26.1.2 (pack) | ARR (audit; CF unverified) | no | homes/warps | |
Recommendation: FOLD Simple Backups, GriefLogger, PermissionGate; ranks/essentials CLEAN-ROOM (no open ranks mod found).

## Voice chat and chat
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Simple Voice Chat (henkelmax) | 26.3..1.8.8 | ARR | no | voice | in pack, keep |
| diaithir-voice | 26.1.2 | MIT | yes | ours | |
| No Chat Reports | 26.3..1.19 | WTFPL | yes | | |
| Chat Heads | 26.3..1.16 | MPL-2.0 | yes | | |
| Chat Patches | 26.3..1.18 | LGPL-3.0-only | yes | | |
Recommendation: ADOPT Voice Chat as-is; FOLD open chat mods into diaithir-chat-client.

## Building materials, structural integrity, construction stages
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Structural Safety (MrStilu2k6) | 26.2..1.20.1 | MIT | yes | ~50% collapse | |
| Simple Block Physics | 1.21.1..1.20.1 | MIT | yes | ~40% | |
| MineCollapse (zerodind) | 1.21.1..1.20.1 | EUPL-1.2 | yes (copyleft) | | |
| Domum Ornamentum | pack | GPL-3.0 | yes | material variants | ours |
| Create-style Scaffolding | 26.3..26.1 fabric | MIT | yes | scaffolding | |
Recommendation: FOLD Structural Safety into diaithir-decor-furnishings; construction-stage chains CLEAN-ROOM.

## Win condition / ceremony
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| True Ending (limesplatus) | 26.1.2..1.19.4 | Custom (verified Modrinth; terms at github.com/SpluoSplatus/Vanilla-Refresh/wiki/License unread) | unverified | ~15% ending trigger | |
| Ending Library (MegaDarkness) | 1.20.1 | MIT | yes | ending screens | |
Recommendation: CLEAN-ROOM Shardfall Gate ceremony; FOLD Ending Library idea.

## Achievements
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Convenient Achievements (SayNooty) | 1.21.8..1.19 | MIT | yes | UI | |
| Achievements Optimizer (bigenergy) | 26.1.2..1.18.2 | MIT | yes | perf only | |
| Achievements (FallingUser) | 26.3..26.1 fabric | AGPL-3.0-only | yes (copyleft) | | |
Recommendation: CLEAN-ROOM on vanilla advancements (Better Advancements is "Don't Be a Jerk", clean-room per audit).

## Tutorial / onboarding
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Create Tutorial Books (vr_d0ge) | 1.20.1..1.19.2 | MIT | yes | ~10% tutorial books | |
| Tutorial Worlds Legacy Console (SmartStreamLabs) | 26.2..1.20.1 | GPL-3.0-only | yes | tutorial worlds | |
Others found only disable the vanilla tutorial.
Recommendation: CLEAN-ROOM via Codex quests that introduce systems.

## Diet / nutrition (diaithir-food-diet)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Nutritional Balance | 26.1 (pack) | GPL-3.0+ | yes | ~80% | in pack keeper |
| Spice of Life Onion (creativemd) | 26.3..1.20.1 | LGPL-3.0-only | yes | variety | in pack |
| Diet (TheIllusiveC4) | 1.20.1..1.16.5 | LGPL-3.0+ | yes | groups | |
| A Balanced Diet (pawjwp) | 1.20.6..1.20 | LGPL-3.0+ | yes | | |
Recommendation: PORT Nutritional Balance.

## Religion / gods / rites
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Divine Gifts (confect1on) | 1.20.1 | MIT | yes | ~20% deity gifts | |
| Gods of Olympus (GalievDev) | 1.20.4 fabric | MIT | yes | ~10% | |
| Gods of the Cosmos (leret) | 1.19.2 | CC-BY-4.0 | yes | ~10% | |
| Medieval Religions; Gods and Heroes | 1.20.x | ARR | no | | |
Recommendation: CLEAN-ROOM (Library gods and per-culture rites); Occultism/Theurgy in pack cover rites.

## Law / crime (diaithir-villagers-npcs)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Cuffed (ported, Xylos_Official) | 1.21.1 neoforge | GPL-3.0-only | yes | ~15% restraint | |
| Bountycraft (Tyler_) | 1.20.1 | MIT | yes | ~15% bounties | |
| Bounty System | 1.21.1 | ARR | no | | |
| Police and Prisoners | 1.20.1 | ARR | no | | |
Recommendation: CLEAN-ROOM law system; FOLD Cuffed + Bountycraft items.


---

<!-- part5_world_nature_food.md -->
# Part 5: world, nature, food, decor, magic (mod-first survey, 2026-11-03)

Method: Modrinth API (search + project/version endpoints, run 11-03), GitHub repo search (RTG only), in-pack/prior work read first (PACK_CONSOLIDATION_AUDIT.csv/.md, EXCLUSIONS.md, ASCENDANT.md, mod-ports/PLAN.md, planets/PLANETS.md). CurseForge-only mods (Twilight Forest, Croptopia, Thaumcraft, Mo' Creatures originals) not re-queried via CF here: marked "unverified" where I relied on the audit/memory.
Reading the tables: version column is newest..oldest builds Modrinth lists for that loader (NeoForge unless stated). Modrinth now lists "26.3" builds; a mod showing 26.3 may or may not have a 26.1.2 file (only "26.1.2" shown means a 26.1.2 build exists). Licences are the Modrinth `license.id` unless noted. "In pack" = in PACK_CONSOLIDATION_AUDIT.csv. Oldest-era mods (1.7 to 1.12) are code/asset ports only.

## Realistic earth-scale worldgen, Tellus-like, 1:5 (diaithir-overworld-biomes / our Tellus fork)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Tellus (Yucareux) https://modrinth.com/mod/tellus | NeoForge 26.3..1.21.1; Forge 1.20.1; Fabric 26.3..1.20.1 | LicenseRef-LGPL-3.0-license (src github.com/Yucareux/Tellus) | Yes (LGPL) | Real-Earth terrain, buildings, roads: ~90% of the feature | Our fork `Tellus-neoforge-26.1.2-0.8.3-diaithir.16` already in /mnt/project-files. Maintained (updated 11-02). 1:5 scale setting: unverified upstream, we patch it ourselves |
| TellusCN | Fabric 26.1.2..1.20.1 | LGPL-3.0-only | Yes | Chinese-localised fork, Fabric | Nothing new |
| Tellus: Real Earth Survival | NeoForge 1.21.1 | MIT | Yes | Modpack/config layer | Data only |
| Tellus: Atlas and Wildlife | NeoForge 1.21.1 | ARR | No | Atlas + wildlife on Tellus | clean-room only |
| The Earth: Tellus, A Roving Journey to Tellus | Fabric 1.21.11 / NF 1.21.8 | CC-BY-NC-SA-4.0 / MIT | NC-SA no; MIT yes | Packs on Tellus | Little code |
| Realistic Terrain Generation (Team-RTG) https://github.com/Team-RTG/Realistic-Terrain-Generation | Forge 1.12.x (pushed 2024-07) | GPL-3.0 (GitHub API) | Yes (GPL) | Procedural realistic terrain, not real-earth | Only useful as ideas; Tectonic/Terralith cover it today |
Recommendation: ADOPT our own Tellus fork (already shipped); upstream is LGPL so keep rebasing on upstream 26.3. Nothing else does real-earth.

## Overworld biomes, terrain, climate (diaithir-overworld-biomes)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Regions Unexplored (Apollounknowndev) | NF 26.1.2..1.21; Forge 1.21.1..1.18.2; Fabric 26.1.2 | MIT | Yes | ~60%: biomes, wood, blocks, nether biomes | In pack, "keep"; 26.1.2 build exists |
| Tectonic | NF 26.3..1.19.3 | MIT | Yes | Terrain shaping (mountains, rivers) | In pack, port route. Conflicts with Tellus terrain, use only for non-Earth planets |
| Biolith | NF 26.3..1.20.4 | LGPL-3.0-only | Yes | Biome API lib | In pack, keep |
| Terralith | NF 26.3..1.20 | LicenseRef-Stardust-Labs-License | Data only per audit | Biomes + terrain | Audit route: data |
| Biomes O' Plenty | NF 26.3..1.7.10 | ARR | No | Biomes/wood/blocks | Audit: clean-room rewrite |
| Nature's Spirit | NF 26.1.2..1.21 | LicenseRef-Natures-Spirit-License (custom) | Check licence text (unverified) | Biomes/trees/mobs | Audit: clean-room |
| Worlium | NF 26.1.2..1.21.11 | GPL-3.0-only | Yes (GPL, separate module) | Cave/world overhaul | Unverified depth |
| Oh The Biomes We've Gone / Oh The Trees You'll Grow | NF 26.3..1.20.1 | LGPL-3.0-only | Yes | Trees (in pack) | keep |
Recommendation: ADOPT Regions Unexplored 26.1.2 (MIT) as the base; FOLD Tectonic into diaithir-overworld-biomes for non-Earth planets; BoP stays CLEAN-ROOM (LICENSE verified ARR, see Corrections); Nature's Spirit CODE is MIT so FOLD its code and redraw its assets (see Corrections).

## Caves (diaithir-overworld-biomes)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| YUNG's Better Caves | NF 26.1.2..1.21; Forge/Fabric 1.20.1 | LGPL-3.0-only | Yes | Cave carving, 90% | In pack (ug_YungsBetterCaves jar present) |
| YUNG's Cave Biomes | NF 26.1.2 build exists | ARR | No | Cave biomes | Audit: clean-room |
| Profundis (firenh) | Fabric 1.21.4..1.18.1 | LGPL-3.0-only | Yes (Fabric->NeoForge port) | 9 cave biomes | Unmaintained since 2024-12; best open cave-biome source |
| Less Predictable Cave Biomes | 26.2..26.1.2 all loaders | MIT | Yes | Cave-biome placement tweak | unverified depth |
| Alex's Caves Continued | NF 26.3..1.20.4 | LGPL-3.0-only | Yes | Themed cave dimensions | In pack, keep |
Recommendation: ADOPT YUNG's Better Caves 26.1.2; FOLD Profundis biomes (LGPL) into diaithir-overworld-biomes to replace the ARR Cave Biomes.

## Seasons and climate (diaithir-overworld-biomes; PR #164)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Homeostatic Seasons | NF 26.3..1.21.1; Fabric | MIT | Yes | Seasons + crop growth | In pack (port route) |
| Serene Seasons | NF 26.3..1.7.10 | ARR | No | Reference seasons | clean-room only |
| Fabric Seasons (+Extras, compat packs) | Fabric 1.21.1..1.16.5 | MPL-2.0 | Yes (MPL file-level) | Seasons, Fabric only | Port source for compat data |
| Natural Temperature | NF 26.3..1.20.1 | custom "Limited Rights Granted" | No | Player temperature | clean-room; unread licence detail |
| Solstice Dynamic Seasons | 1.21.11..1.20.1 | ARR | No | | |
Recommendation: ADOPT Homeostatic Seasons (MIT) via the module; temperature from our climate PR #164 stays own. No open player-temperature mod found.

## Villages and settlements (diaithir-villages-settlements)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| ChoiceTheorem's Overhauled Village | NF 26.2..1.18.2 | CC-BY-NC-ND-4.0 | No | Village overhaul | clean-room |
| Villages&Pillages | NF 26.3..1.19.2 | CC-BY-NC-ND-4.0 | No | | clean-room |
| MMV Moog's Missing Villages | NF 26.3..1.20 | AGPL-3.0-only | Code yes (AGPL, own module); audit says clean-room because assets unclear | Missing biome villages | |
| Castle Shift | NF 26.3..1.21.1 | LGPL-3.0-only | Yes | Castle-style villages | In pack, port |
| Underground Villages | in pack | MIT | Yes | | port |
| Better Villages, Lios Overhauled Villages | 26.2 / 26.3 | ARR | No | | |
Recommendation: FOLD Castle Shift + Underground Villages (+ MMV code if AGPL module accepted) into diaithir-villages-settlements; the ND/ARR ones are CLEAN-ROOM.

## Ruins, dungeons, castles, monuments, landmarks (diaithir-ruins-landmarks / diaithir-dungeons-underground / diaithir-adventure-structures)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Battle Castles | NF 1.21.1..1.16.5 | Apache-2.0 | Yes | Castles | unverified size |
| Little Structures (datapack) | all loaders 1.21.8..1.19.4 | LGPL-3.0-only | Yes (data) | Small structures | |
| Ancient Ruins | Fabric 26.3..26.2 | MIT | Yes | Small ruins | tiny, 853 dl |
| Dungeon Crawl, Better Archeology, Need More Structures, Thun's, Trek, WITS, Useful Structures, MBS/MES/MMR/MSS/MNS | in pack | GPL/MIT/LGPL | Yes | Dungeons/structures | Audit routes already data/port |
| Ember's Castles and Keeps, Philips Ruins, Epic Structures, Integrated Dungeons, Explorify, Abu Simbel/Petra/etc. | 1.20..26.3 | ARR | No | Ruins/landmarks | clean-room list in audit |
| Knights And Castles | NF 1.20.6..1.20.1 | LicenseRef-Amethyst | unverified | Castles | |
Recommendation: FOLD Battle Castles + Little Structures + Ancient Ruins into diaithir-ruins-landmarks/-adventure-structures; the 40 ARR packs stay CLEAN-ROOM (ports #133 already). Landmarks of the real Earth come from Tellus buildings.

## YUNG's-style structure redesigns (diaithir-yungs-structures)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| YUNG's API + Better Dungeons/Mineshafts/Strongholds/Desert & Jungle Temples/Witch Huts/Nether Fortresses/Ocean Monuments/Bridges/Extras | NF 26.1.2 (Dungeons/Monuments from 1.19.2; API from 1.18.2) | LGPL-3.0-only | Yes | 100% of the set | All have 26.1.2 builds, updated 2026-09 |
| Hopo Better Underwater Ruins, Buried Wrecks | in pack | LGPL / MIT | Yes | Ocean ruins | |
Recommendation: ADOPT the 26.1.2 builds as they are (LGPL) inside diaithir-yungs-structures; nothing missing.

## Nether overhaul (diaithir-nether)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| BetterNether New Dawn, Eternal Nether | in pack | MIT | Yes | Biomes/blocks | port |
| Gardens of the Dead | NF 1.21.1..1.21; Forge 1.20.1 | MIT | Yes | Nether forest biomes (Mojang-style) | Not yet in pack, best open add |
| Charred Horizons | NF 1.20.1 | MIT | Yes | Nether biomes | small |
| Incendium | NF 26.3..1.18.2 | Stardust license | audit: clean-room | Structures/biomes | |
| NetherEx, Nether Descent | in pack | custom/ARR | No | | clean-room |
| Even Better Nether, Hearths | | ARR | No | | |
Recommendation: FOLD Gardens of the Dead (MIT) into diaithir-nether next to BetterNether/Eternal Nether; rest as audit.

## End overhaul (diaithir-end)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| End Remastered (+Lost Castle) | NF 26.3..1.21; Forge 1.20.4..1.16.3 | LGPL-3.0-only | Yes | Structures/loot, 70% | In pack, port |
| End Caves | all loaders 26.1..1.19 | MIT | Yes | End cave carving | 26.1 build; add |
| Nullscape | NF 26.3..1.18.2 | Stardust | clean-room | End terrain | in pack as clean-room |
| Enderscape | 26.3..1.17 | custom Enderscape licence | unverified | End biomes/mobs | |
| Hardcore Ender Expansion | Forge 1.7.10 (2023-08) | custom | unverified | Old End overhaul | idea source only |
| Fancy End, Yanza's End City Overhaul | 26.2 / 1.21.3 | CC-BY-NC-ND / MIT | no / yes | Visual / city | |
Recommendation: ADOPT End Remastered (LGPL) + End Caves (MIT) in diaithir-end; End terrain stays CLEAN-ROOM (Nullscape).

## Dimension: Undergarden
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| The Undergarden (quek) | NF 26.1.2..1.20.1 | ARR (src github.com/quek04/The-Undergarden) | No | 100% | In pack "keep"; updated 2026-08 |
Recommendation: ADOPT 26.1.2 build as-is (already pack-eligible, kept separate).

## Dimension: Aether / Paradise Lost
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| The Aether (Aether Team) | NF 1.21.1..1.20.1; Fabric 1.21.1 | LicenseRef-Custom | check text | Aether | No 26.1 build on Modrinth |
| The Aether II | in pack | custom | | | Kept; this is the Aether in pack |
| Paradise Lost (devs-immortal) | NF 1.21.1; Fabric 1.21.1..1.16.4 | MIT | Yes | Aether-like dim, ~80% | In module diaithir-dimensions-world |
| Deep Aether | NF 1.21.1..1.20 | LGPL-3.0-only | Yes | Aether addon | needs Aether |
Recommendation: PORT Paradise Lost (MIT) in diaithir-dimensions-world; keep Aether II as shipped.

## Dimension: Twilight Forest
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| The Twilight Forest (official) | 26.1.2 (per pack.json, EXCLUSIONS) | LGPL (audit) with ARR sounds/structures | n/a | 100% | Not on Modrinth; unverified here |
| Twilight Forest Cave Fix, The Lost Blocks | 1.20.1 / 1.21.1 | MIT | Yes | Addons | |
Recommendation: ADOPT official 26.1.2 build (already decided).

## Dimension: Bumblezone
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| The Bumblezone (TelepathicGrunt) | NF 26.1.2..1.20.1 | ARR | No | 100% | In pack keep, updated 2026-10-29 |
Recommendation: ADOPT 26.1.2 build as-is.

## Dimension: Aurorian
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| The Aurorian (shiroroku) | Forge 1.12.2 | MIT | Yes | Original, 100% | src github.com/shiroroku/TheAurorian |
| The Aurorian Reborn | Forge 1.20.1 | MIT | Yes | Rewrite | updated 2026-09 |
| The Aurorian Unofficial Port | NF 1.21.1..1.19.2 | MIT | Yes | Port, 421 dl | Closest to our target |
Recommendation: PORT Unofficial Port (MIT) into diaithir-dimensions-world; ports #130 already did the dimension, still missing the items in EXCLUSIONS B2.

## Dimension: Eternal Starlight
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Eternal Starlight (LeoLezury) | NF 1.21.1..1.21; Fabric | MIT | Yes | 100% | In module; updated 2026-09 |
Recommendation: PORT (MIT) to 26.1.2 in diaithir-dimensions-world.

## Dimension: Dimdoors
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Dimensional Doors | NF 1.21.1; Forge 1.20.1..1.12.2; Fabric 1.21.1..1.19.2 | GPL-3.0-only | Yes (GPL) | 100%, maintained | src github.com/DimensionalDevelopment/DimDoors |
Recommendation: PORT into diaithir-dimensions-world (keep GPL file headers; GPL module boundary).

## Dimension: Backrooms
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| The Backrooms (v-fast) | Fabric 26.2..1.19; Quilt | MIT | Yes (Fabric->NF) | Levels | In pack as legacy keep |
| Found Footage | Fabric 1.20.1 | LGPL-3.0-only | Yes | Horror | |
Recommendation: FOLD The Backrooms (MIT) into diaithir-dimensions-world; we also have backrooms_levels.json.

## Planets, one real planet per universe, Stellaris-style (planets/PLANETS.md; Keelwright)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Stellaris (st0x0ef) | NF/Fabric 26.1.2..1.20.6 | CC-BY-NC-SA-4.0 | NC-SA only | Rockets, planets, 40% | In pack keep |
| Ad Astra (Terrarium) | NF 1.21.1..1.20.4 | custom Terrarium Licence | no (custom) | Rockets, planets | |
| Ad Astra: Planets+ | Forge/NF/Fabric 1.20.4..1.20.1 | MIT | Yes | Extra planets | data |
| Create: Northstar / Redux | Forge 1.20.1 (2024) / 1.21.1 | MIT | Yes | Create-style rockets | |
| Creating Space, Space Explore | NF 1.21.1 | MIT | Yes | Space travel | |
| Star Wars Planets | 1.21..1.19.2 | GPL-3.0-or-later | Yes | Planet dims | |
Recommendation: CLEAN-ROOM (data): 216 planet dimensions are already generated (planets/datapack) and travel is Keelwright ships. No mod maps a Panscriptum universe to a planet. FOLD Planets+/Stellaris sky textures only as references (Stellaris NC-SA: redraw).

## Hidden rite sites and ascendant biomes (ASCENDANT.md)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| rituals (totem-rituals) | NF/Forge/Fabric 26.3..1.21 | MIT | Yes | Ritual crafting | src Underwood-Inc/rituals; unverified fit |
| Summoning Rituals | 1.21.1..1.18.2 | ARR | No | Altar summon | |
| Trials of the Wild | Fabric 1.21.11 | ARR | No | | |
Recommendation: CLEAN-ROOM (ogham stones, tree riddles, altar chain are our design); none found for hidden sites/biomes with riddle steps.

## Ores, geodes, mineral deposits, depletion (diaithir-resource-gathering / worldgen)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Geolosys | NF/Forge 1.21.1..1.12 | GPL-3.0-only | Yes | Ore deposits, prospecting, 70% | maintained 2026-10; best match |
| GeOre | in pack | MIT | Yes | Geode-style ores | data |
| Create: Rock & Stone | NF 1.21.1 | LGPL-3.0-or-later | Yes | Rock/stone deposits | |
| More Geodes (Reforged) | Forge 1.20.1 | LGPL-3.0-only | Yes | Geodes | |
| Geodesy | Fabric 26.3..1.17 | MIT | Yes | Geodes | |
| Minerally, Rare Rich Veins, Universal Ores | | ARR / ARR / Polyform | No | | |
Recommendation: FOLD Geolosys (GPL module) into diaithir-resource-gathering for deposits and prospecting; depletion: none found as a mod, add as own rule.

## Fauna and animals: Alex's Mobs, Untamed Wilds, prehistoric (diaithir-creatures)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Alex's Mobs Continued | NF 26.3..1.20.4; Forge 26.2..1.20.1; Fabric | GPL-3.0-only | Yes (GPL module) | 100% of Alex's Mobs, maintained | src github.com/Codx-org/AlexsMobsContinued; Alex's Mobs original 1.20.1..1.16.5 GPL |
| Untamed Wilds (Unofficial Port) | NF 1.21.1 | GPL-3.0-only | Yes | Our port is in pack | |
| Prehistoric Kingdom | NF 26.3..1.21.1 | MIT | Yes | Prehistoric animals | 535 dl |
| More Fossils | NF 26.1.2..1.19 | MIT | Yes | Fossils | |
| Fossils & Archaeology Revival / Legacy | Forge 1.20.1..1.7.10 / NF 1.21.1 | custom FA-License / MIT | Legacy yes | Fossil dinos | project-files/animals-fossils exists |
| Jurassic Reborn | NF 1.21.1..1.12.2 | ARR | No | | |
| Naturalist | NF 26.3..1.18.2 | custom | no | Wildlife | |
Recommendation: FOLD Alex's Mobs Continued (GPL, own module) + Prehistoric Kingdom (MIT) into diaithir-creatures; port Untamed Wilds (done).

## Dragons, Ice and Fire, mythical creatures
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Ice and Fire (AlexModGuy) | NF/Forge 1.20.1..1.10.2 | LGPL-3.0-only | Yes | 100% | Our port in pack; upstream stale (2024-08) |
| Saint's Dragons | Forge/Fabric 1.20.1 | dual-licence (unverified) | ? | Dragons | |
| Mythical Creatures Reborn | Forge 1.20.1 | MIT | Yes | Mythic mobs | 631 dl |
| Dragons: Book of Dragons, Tiny Dragons | | ARR | No | | |
Recommendation: ADOPT our Ice and Fire port; FOLD Mythical Creatures Reborn (MIT) for extras.

## Morphing and shapeshifting (diaithir-creatures)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| ReMorphed (ToCraft) | NF 26.3..1.20.2; Fabric/Forge/Quilt | LGPL-3.0-or-later | Yes | Identity-style morph, 90% | In pack with Walkers; updated 2026-10 |
| Walkers | NF/Forge 1.20.4..1.20.1 | ARR | No | Morph | clean-room only |
| Origins / Origins (Forge) | Fabric 1.21.1; Forge 1.20.1 | MIT | Yes | Origins (race powers) | |
| Medieval Origins Revival | NF 1.21.1 | MIT | Yes | Origins pack | |
| Morphling | Fabric 26.1.2 | MIT | Yes (Fabric->NF) | Simple morph | |
Recommendation: ADOPT ReMorphed 26.x build (LGPL); drop Walkers; Origins race powers FOLD as data if wanted.

## Mob habitats and planet spawns
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| (none found as a mod) | | | | | Spawn rules are biome JSON; Alex's Mobs/Naturalist ship their own |
Recommendation: CLEAN-ROOM: spawn JSON per planet from the Panscriptum creature entries (planets/PLANETS.md placement rule), data only.

## Taming and pets (diaithir-creature-utilities)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Petting - Tame any mob | NF 26.3..1.20.6 | LGPL-3.0-only | Yes | Tame any mob | |
| Optimal Taming | Fabric 26.1.2 | CC0-1.0 | Yes | Taming tweaks | |
| Mob Lassos, Animal Feeding Trough, Call Your Horse | in pack | MPL / MIT | Yes | Capture/feed/call | |
| Saddlebag | NF 26.3..1.21 | ARR | No | Pet pack | |
Recommendation: FOLD Petting (LGPL) into diaithir-creature-utilities.

## Fishing (diaithir-creature-utilities)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Fishing Real | NF 26.1.2..1.20.4; Forge/Fabric | MIT | Yes | Real fish, lengths, 80% | 26.1.2 build, 3.5M dl |
| Stardew Fishing | NF 26.2..1.20.1 | MIT | Yes | Minigame | |
| Lava Fishing | NF 26.1.2..1.20.1 | AGPL-3.0-only | Yes (AGPL) | Lava | |
| Aquaculture 2 | in pack | ARR | No | Fishing gear | audit clean-room |
Recommendation: FOLD Fishing Real (MIT) + Stardew Fishing (MIT) into diaithir-creature-utilities; replaces Aquaculture 2 clean-room.

## Butchery (PR #186; project-files/butchery)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Butchery | NF 26.1.2..1.20.1 | ARR | No | Carcasses | 1.2M dl |
| Butcher's Delight (+Foods) | Forge 1.20.1..1.16.5 | MIT | Yes | Meat foods | |
| flaying | NF 1.21.1 | MIT | Yes | Skinning | tiny |
| Butchercraft | NF 1.21.3..1.19.2 | CC-BY-NC-SA-4.0 | No | | |
| Carcass | Fabric 1.20.1 | ARR | No | | |
Recommendation: CLEAN-ROOM (our #186) borrowing food data from Butcher's Delight (MIT) and flaying (MIT).

## Farming: crops, trees, Mystical Agriculture, Croptopia (diaithir-crops-and-trees / diaithir-mystical-agriculture)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Mystical Agriculture | NF 26.1.2..1.21; Forge 1.20.1..1.10 | MIT | Yes | 100% | In pack; 26.1.2 build |
| MA Tiered Crystals | NF 26.1.2 | MIT | Yes | | In pack |
| Croptopia | in pack, MIT (Modrinth slug not found; CF) | MIT (audit) | Yes | Crops/foods | unverified here |
| Farmer's Delight | NF 1.21.1..1.20 | MIT | Yes | Cooking, crops | newest 1.21.1 (no 26.1) |
| Dynamic Trees (+Plus) | NF 26.1.2..1.16.4 | MIT | Yes | Growing trees | not in pack |
| Pam's HarvestCraft (1.12.2, 2) | Forge | ARR | No | Crops/trees | |
| Productive Farming/Trees, Saro's Fruit Trees | | ARR | No | | |
| Fruit Trees | Fabric/Forge 1.20.1 | CC-BY-4.0 | Yes | Fruit trees | small |
Recommendation: ADOPT Mystical Agriculture 26.1.2; PORT Croptopia; FOLD Dynamic Trees (MIT, 26.1.2) only if Marlon wants growing trees; productive farming/trees CLEAN-ROOM.

## Cooking and kitchens (diaithir-kitchen-farmtech)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Cooking for Blockheads | NF 26.3..1.20.2 | ARR | No | Kitchen multiblock | audit clean-room |
| Farmer's Delight | NF 1.21.1 | MIT | Yes | Cooking pot | data+code source |
| Baker's Oven | Forge 1.16.5 (2025-03) | CC0-1.0 | Yes | Oven | tiny |
| Magave Kitchen Core | Forge 1.20.1 | MIT | Yes | Kitchen | 222 dl |
| Chef's Workbench, [Let's Do] Candlelight/Bakery | | ARR / custom | No | | |
Recommendation: CLEAN-ROOM kitchen multiblock; FOLD Farmer's Delight recipes/pot logic (MIT) into diaithir-kitchen-farmtech.

## Drinks, brewing, kegs (diaithir-kitchen-brewing)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Brewin' And Chewin' | NF 1.21.1 | ARR | No | Kegs | 3.8M dl |
| Alcohol Only | Fabric 1.21 | GPL-3.0 plus "Chaotic Hell" clause | unclear | | |
| TFC Aged Alcohol | NF 1.21.1 | LGPL-3.0-only | Yes | Aging | needs TFC |
| Create: Alcohol Industry | NF 1.21.1 | custom | check | | |
| Trank-O-Mat | 1.20.4 | MIT | Yes | Potion machine | |
| Simply Alcohol | NF 26.1.2 | ARR | No | | |
Recommendation: CLEAN-ROOM (already built: brewing_keg_barrel_client.png, PR #165); nothing open worth folding.

## Dish icons
No mod found (Modrinth searches empty). Recommendation: CLEAN-ROOM; /mnt/project-files/dishes is our own set.

## Food spoilage (diaithir-food-diet)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Spoiled | in pack | MIT | Yes | Rot, 90% | port |
| SpoiledZ, Rot Timer | Fabric 1.21.1 / Fabric+Forge | MIT | Yes | Rot | dropped by rule |
| FFFoodSpoilageAndPreservation | NF 26.3 | ARR | No | | |
| Food Spoiling | Forge 1.12.2 | MIT | Yes | Old | |
Recommendation: ADOPT Spoiled port (already).

## Diet (diaithir-food-diet)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Spice of Life Onion | in pack | LGPL-3.0-only | Yes | Variety | |
| Nutritional Balance | in pack | GPL-3.0-or-later | Yes | Nutrients | |
| Nourished | NF 1.21.1 | MIT | Yes | Nutrition | |
| Diet / A Balanced Diet | Fabric+Forge 1.20.1 / 1.20.6 | LGPL-3.0-or-later | Yes | Food groups | |
| NutritionZ | Fabric 1.21.1 | MIT | Yes | | |
Recommendation: FOLD (already in module); no new candidates needed.

## Everyday objects, 460 tools/kitchen/household items
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| MrCrayfish's Furniture Refurbished | in pack | MIT | Yes | Kitchen/household blocks | keep |
| Supplementaries | NF 1.21.1 | Supplementaries Team License (custom) | No | Misc | |
| Handcrafted | NF 1.21.1 | Terrarium Licence | No | Furnishing | |
| Another Furniture | NF 1.21.1 | custom | check | | |
| Paladin's Furniture | 1.21.11 | LGPL code, Polyform-Shield assets | Code only | Furniture | |
Recommendation: CLEAN-ROOM data items (our 460-item list); FOLD MrCrayfish (MIT) blocks. No mod covers a hand-tool/household list that size.

## Decoration, furnishing, building blocks, connected textures (diaithir-macaw-blocks / decor-furnishings / diagonal-blocks)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Macaw's Doors, Fences&Walls, Paths, Trapdoors | NF 26.3..1.16.5 | MIT | Yes | | Audit: data |
| Macaw's Windows/Roofs/Stairs/Bridges/Furniture/Lights | NF 26.3 | ARR | No | | clean-room (#119 slice 1) |
| Diagonal Fences/Walls/Windows | 26.3..1.18.2 | MPL-2.0 | Yes | | merge |
| Chisel Reborn | NF 26.3..1.20.3 | custom | check | Chisel blocks | |
| Reintegrated: Chipped, Chipped Express | NF 1.21.1 | MIT | Yes | Chipped-style variants | Chipped itself ARR |
| Fusion (Connected Textures) | 26.3..1.12 | ARR | No | CTM | |
| CTM Overhaul | resource pack 1.21.11..1.19 | CC0-1.0 | Yes | Pack-side CTM | |
| Bibliocraft Legacy, Domum Ornamentum, FramedBlocks, ArmorStatues | in pack | MIT/GPL/LGPL/MPL | Yes | | merge |
Recommendation: FOLD Chipped Express/Reintegrated (MIT) and Macaw MIT mods into diaithir-macaw-blocks; CLEAN-ROOM the ARR Macaw families; connected textures via CTM Overhaul (CC0) pack data.

## Building tools (diaithir-building-tools)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Building Gadgets | in pack | MIT | Yes | Gadgets | |
| Effortless Building | NF 26.3..1.19.2 | LGPL-3.0-only | Yes | Build modes, mirror | in pack |
| Construction Wand KOTS | NF 26.1.2..1.21.1 | MIT | Yes | Wands | maintained 11-01 |
| ConstructionSticks | in pack | MIT | Yes | Sticks | |
Recommendation: FOLD all four into diaithir-building-tools (as audit).

## Magic: Botania-style (diaithir-arcane-relics / ritual-enchant)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Botania (Vazkii) | Forge/Fabric 1.20.1..1.6.4 | LicenseRef-Botania-License | check text (unverified) | Flower magic | no NF / 26.1 build |
| AIOT Botania, Botania Seeds | 1.20.1 | MIT | Yes | Addons | need Botania |
Recommendation (REVISED): PORT Botania code/assets under the Botania License (Use/Share/Adapt, with attribution + copyleft + non-monetary clauses); verified. See Corrections.

## Magic: Ars Nouveau-style
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Ars Nouveau | NF 1.21.1..1.20.1 | ARR | No | Glyph spells | 4.1M dl |
| Spell Engine | NF 26.3..1.20.1 | GPL-3.0-only | Yes | Spell framework | in pack |
| Hex Casting | NF/Forge/Fabric 1.20.1 | MIT | Yes | Pattern casting | |
Recommendation (REVISED): PORT Ars Nouveau CODE (LGPL-3.0, verified) into a GPL-free module, REDRAW all assets (assets ARR); build against NF 1.21.1 -> 26.1.2. See Corrections.

## Magic: Thaumcraft-style
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Thaumcraft 4/6 (Azanor) | Forge 1.7.10/1.12.2 | ARR (unverified) | No | | not on Modrinth |
| Thaumcraft 4 Tweaks | Forge 1.7.10 | AGPL-3.0-only | tweaks only | | |
| Thaumon | NF/Fabric/Forge 1.21.1 | MIT | Yes | Decoration/magic mix; not true Thaumcraft | verify |
| Forbidden and Arcanus, Occultism, Theurgy | in pack | ARR / MIT / MIT | | Occult/alchemy | |
Recommendation (REVISED): FOLD/PORT Thaumic Augmentation (LGPL-3.0, 1.12.2) ideas/code for research+aspects; original Thaumcraft stays clean-room. See Corrections.

## Magic: rituals, druidic, alchemy, evil (diaithir-ritual-enchant)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Roots Classic | in pack | MIT | Yes | Druidic rituals | |
| Theurgy | NF 26.3..1.20 | MIT | Yes | Alchemy (classical) | |
| Occultism | NF 26.3..1.20 | MIT | Yes | Rituals/spirits | in pack |
| EvilCraft | NF 26.3..1.20.4 | MIT | Yes | Blood magic | |
| Apothic Enchanting | NF 26.1.2..1.21.1 | MIT | Yes | Enchanting | 26.1.2 build |
| Druids (RPG Series Plus) | 1.21.1 | MIT | Yes | Druid class | |
| rituals (totem-rituals) | 26.3..1.21 | MIT | Yes | Rituals | |
Recommendation: FOLD (as audit): ADOPT 26.1.2 builds of Apothic Enchanting; port the rest.

## Magic: Spell Engine classes (diaithir-arcane-classes)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Spell Engine, Spell Power Attributes | NF 26.3..1.20.1 | GPL / LGPL | Yes | Core | keep |
| Wizards, Paladins & Priests, Runes | NF 26.3 | ARR | No | Classes | audit: data bundles |
| Druids (RPG Series Plus), Elemental Wizards | 1.21.1 | MIT / ARR | Druids yes | | |
Recommendation: CLEAN-ROOM class data on Spell Engine; FOLD Druids (MIT).

## Sky and space visuals
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Enhanced Celestials | NF 1.21.1..1.19.2 | LGPL-3.0-only | Yes | Moons, events | ports #113 |
| Aurora Astral | 26.3..1.19 | LGPL-3.0-or-later | Yes | Sky/aurora | unverified type |
| Stellaris StellarView compat | NF 1.21.1 | MIT | Yes | Planets in sky | |
| End Planet | 26.1.2 | CC-BY-SA-4.0 | SA | | |
| Aurora Sky, Nebula Dust Sky Pack | 26.x | ARR | No | | |
Recommendation: FOLD Enhanced Celestials (done), plus Aurora Astral textures if licence fits.

## Weather
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Raindance | 1.21.11..1.19 | MIT | Yes | Rain control | |
| Expanded Weather2 Dynamics | Forge/NF 1.21.1 | MIT | Yes | Weather2 add-on | needs Weather2 |
| Weather2 (Corosus) | Forge | unverified | | Storms, tornados | |
Recommendation: CLEAN-ROOM storms on climate PR #164; FOLD Raindance if rain control wanted.

## Wood and stone variants
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Every Compat (Wood Good) | 1.21.1..1.18.1 | ARR | No | | |
| More Compatibility Variants | 1.21.1..1.20.1 | MIT | Yes | Wood variants | |
| Woodworks | NF 1.21.1 | Abnormals licence | No | | |
| Carved Wood | 26.1.2..1.20.1 | Makers Mods Licence | check | | |
| Stoneworks | in pack | MPL-2.0 | Yes | | |
Recommendation: FOLD More Compatibility Variants (MIT) approach; generate variants by data (diaithir-content-data wood variants).

## Rewrite-jar equivalents: BoP, Nature's Spirit, Productive Bees, Blockheads
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| BoP | NF 26.3 | ARR | No | | clean-room (audit) |
| Nature's Spirit | NF 26.1.2 | custom | check | | clean-room |
| Productive Bees | NF 1.21.1..1.20 | ARR | No | | keep (ARR, no 26.1) |
| Mystian Apiary | NF 26.1.2 | ARR | No | Bees | |
| Cooking/Farming for Blockheads | NF 26.3 | ARR | No | | clean-room |
Recommendation (REVISED): BoP, Productive Bees, Macaw's ARR families and Blockheads stay CLEAN-ROOM (ARR verified); Nature's Spirit is code-MIT/assets-ARR so PORT code, redraw assets. See Corrections.

## Corrections (coordinator query 11-03: licences read from LICENSE files / Modrinth API)
| Mod | Verified licence (source) | Verdict |
|---|---|---|
| Ars Nouveau | Code LGPL-3.0; assets (textures, models) "All Rights Reserved" (https://raw.githubusercontent.com/baileyholl/Ars-Nouveau/HEAD/license.txt; Modrinth tag says ARR) | PORT code (LGPL), redraw assets. Newest NF 1.21.1 |
| Botania | Botania License: free to Use, Share, Adapt with attribution, copyleft (derivative must be open source with a similar clause), non-monetary; API dir verbatim only (https://raw.githubusercontent.com/VazkiiMods/Botania/HEAD/LICENSE.txt). Newest Forge/Fabric 1.20.1, no NF | PORT allowed; our module must be open source with the same clause, credit Vazkii; assets redrawn anyway |
| Biomes O' Plenty | LICENSE is "All rights reserved" (https://raw.githubusercontent.com/Glitchfiend/BiomesOPlenty/HEAD/LICENSE). Your memory of LGPL applies to old builds only (unverified for them) | CLEAN-ROOM stands (current 26.x builds) |
| Nature's Spirit | Assets and model packages All Rights Reserved; all other files MIT (https://raw.githubusercontent.com/Team-Hibiscus/NatureSpirit/master/LICENSE) | PORT code (MIT), redraw assets; clean-room only for assets |
| Productive Bees | All Rights Reserved (https://raw.githubusercontent.com/JDKDigital/productive-bees/HEAD/LICENSE) | CLEAN-ROOM stands |
| Macaw's Roofs/Windows/Furniture/Stairs/Bridges/Lights | ARR per Modrinth API; no public source repo (https://modrinth.com/mod/macaws-roofs). MIT only for Doors, Fences&Walls, Paths, Trapdoors | CLEAN-ROOM for the ARR set, as before |
| Thaumic Augmentation (TheCodex6824) | LGPL-3.0 per GitHub API (https://github.com/TheCodex6824/ThaumicAugmentation, 1.12.2, pushed 2026-06); needs Thaumcraft 6 itself | Port its own code; Thaumcraft assets/code not covered |
| Thaumcraft Continuous | Not found on Modrinth or GitHub search | Unverified; none found |
Cooking/Farming for Blockheads: ARR on Modrinth; repo license not re-read (unverified).

## Added prior art (coordinator request)
### Butchery
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Butchery | NF 26.1.2..1.20.1 | ARR (Modrinth) | No | Carcass/knife butchering | |
| Butchery: Alex's Mobs Addon | Forge 1.20.1 | ARR | No | | |
| Butcher's Delight, Butcher's Delight Foods | Forge 1.20.1..1.16.5 | MIT | Yes | Meat foods, cuts | |
| Butchercraft | NF 1.21.3..1.19.2 | CC-BY-NC-SA-4.0 | No | | |
| Carcass | Fabric 1.20.1 | ARR | No | | |
| flaying | NF 1.21.1 | MIT | Yes | Skinning | |
Recommendation: CLEAN-ROOM (#186) with MIT data from Butcher's Delight/flaying.
### Brewing, kegs (Brewin' And Chewin', Let's Do Brewery, Vinery)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Brewin' And Chewin' (Monad-Modding) | NF 1.21.1..1.20.1; Fabric 1.21.1 | ARR (Modrinth; repo LICENSE file not retrievable, unverified) | No | Keg, ferments | 3.8M dl |
| [Let's Do] Brewery | NF/Forge/Fabric 1.20.1 (Farm&Charm compat 1.21.1) | LicenseRef-Custom (text unread, unverified) | Check | Brewing station, drinks | src github.com/satisfyu/Brewery |
| [Let's Do] Vinery | NF/Fabric 1.21.1..1.19.2 | LicenseRef-custom (unread) | Check | Grapes, wine | 13M dl |
| Patbox's Brewery | Fabric 26.3..1.19.2 | LGPL-3.0-only | Yes | Brewing, fabric-only | github.com/Patbox/brewery |
| BreweryX | Bukkit plugin 26.2..1.9 | GPL-3.0-only | idea only | Server brewing | |
| TFC Aged Alcohol | NF 1.21.1 | LGPL-3.0-only | Yes | Aging barrels | |
Recommendation: CLEAN-ROOM keg/barrel (done, #165); FOLD Patbox's Brewery logic (LGPL) if more recipes wanted; check Let's Do licence text before borrowing.
### Dish icons
Modrinth queries "dish icons", "food icons" returned nothing relevant; none found. CLEAN-ROOM (own dishes set).
### Ore depletion and deposits
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Geolosys | NF 1.21.1; Forge 1.20.1..1.12 | GPL-3.0-only (src git.oitsjustjose.com/me/Geolosys) | Yes | Deposits, prospecting; depletion not confirmed | |
| Advanced Ore Deposits | NF 1.21.1 | MIT (github.com/samllea/AdvancedOreDeposits) | Yes | Finite deposits (depletion unverified, 444 dl) | |
| Ore Deposits | all loaders 1.21.1..1.16.5 | Apache-2.0 | Yes | Deposits | |
| Create Ore Excavation Deposits | 1.21.1..1.20.1 | MIT | Yes | Drilling deposits | |
| Large Ore Deposits | 26.3..1.20.1 | CC-BY-ND-4.0 | No | | |
Recommendation: FOLD Advanced Ore Deposits (MIT) + Geolosys (GPL module) into diaithir-resource-gathering; confirm depletion in their source before relying on it.


---

<!-- part6_client_qol_perf.md -->
# Mod survey part 6: client, QoL, performance, distribution (2026-11-03)

Method: Modrinth API (search + project/version endpoints, queried for neoforge + 26.1.2 builds; licence = Modrinth SPDX/LicenseRef field), plus the audit CSV (plans/PACK_CONSOLIDATION_AUDIT.csv), QOL_MODS.md and CLEAN_ROOM_R2_QOL_CLIENT_LICENCES.md. GitHub API was blocked in this session (repo not enabled), so repo-level licence files, CurseForge-only and pre-2020 forum mods were not checked; "unverified" marks anything not seen on a Modrinth page. MC range "newest..oldest" is the Modrinth game-version span of listed builds (may include snapshots such as 26.3). "NF26.1.2 build" means a NeoForge file tagged 26.1.2 exists on Modrinth. Port rule: open licence = port/fold allowed; ARR, NC, ND, Polyform, "protective" = clean-room only. Licences in the pack audit are quoted as the audit has them.

## Keybinds with no same-context conflicts (diaithir-client-view-input)
| Candidate | MC/loader (newest..oldest) | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Controlling (jaredlll08) https://modrinth.com/mod/controlling | 26.3..1.7.10 fabric/forge/neoforge; NF26.1.2 build 26.1.2.7 | MIT | yes | Search/filter keybind screen, conflict highlighting, "show conflicts" filter. ~70% | Already in audit as port into diaithir-client-view-input. Does not add contexts, only displays vanilla/NeoForge KeyConflictContext clashes |
| NeoForge KeyConflictContext / IKeyConflictContext (loader built-in) | 26.1.2 neoforge | LGPL-2.1 (NeoForge) | n/a (API) | The actual "same-context only" conflict rule: UNIVERSAL/GUI/IN_GAME, custom contexts | Use this for our own binds; no jar needed. Source: NeoForge repo, unverified in this session |
| Amecs (Siphalor) https://modrinth.com/mod/amecs | 26.2..1.14.4 fabric only | Apache-2.0 | yes (code) | Ctrl/Shift/Alt modifier keys on any bind, so far fewer clashes | Fabric API-based; port the modifier-key matching idea only |
| Amecs Reborn | 1.21.6..1.21.1 fabric | Apache-2.0 | yes | Same, abandoned-fork | Superseded by Amecs |
| KeyBind Bundles (Matyrobbrt) | 26.1.2..1.20.1 forge/neoforge | MIT | yes | Collapses many binds into one radial/bundle; fewer top-level keys | In audit: port to diaithir-world-interaction |
| Omni Wheel (seniorendi) https://modrinth.com/mod/omni-wheel | 26.3..1.16.5; NF26.1.2 2.0.0 | MIT | yes | Radial menu of keybinds | Alternative to KeyBind Bundles |
| Modern Controlling (fdym) | 1.12.2 forge | GPL-2.0-or-later | yes (GPL ok only if module GPL-compatible) | Controlling back-port for 1.12.2 | Old, no value over Controlling |
Recommendation: PORT Controlling (MIT) into diaithir-client-view-input; build our own binds on NeoForge KeyConflictContext with a custom Diaithir context so conflicts are only same-context; FOLD KeyBind Bundles for radial.

## HUD overlays (diaithir-hud-overlays)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Leave My Bars Alone (Fuzs) | 26.3..1.18.2 all loaders | MPL-2.0 | yes | Food/xp bar while mounted | In audit: port |
| Measurements (Mrbysco) | 26.3..1.16.5 all | MIT | yes | Distance/size readouts | In audit: port |
| AutoHUD (Crendgrim) https://modrinth.com/mod/autohud | 26.3..1.18.2; NF 9.3+26.1 | LGPL-3.0-only | yes | Auto-hide/show HUD elements by context | Good fold candidate, ~40% of HUD tweaks |
| AppleSkin | audit: Unlicense | Unlicense | yes | Food/saturation HUD + tooltip | Kept separate in audit; could fold (public domain) |
| Better Mount HUD (Lortseam) | 26.3..1.17 fabric | GPL-3.0-only | code only if module GPL | Mount health/jump bar | Fabric only |
| uku's Armor HUD | 26.3..1.20.1 fabric/neoforge/quilt | MIT | yes | Armor HUD | Optional |
| MiniHUD (masa) | 26.3..1.8 fabric/forge | LGPL-3.0-only | yes (code) | Info lines, overlays (light level, chunk borders) | Fabric/Forge only; NeoForge port needed |
| Jade (Snownee) | 26.3..1.16.4; NF 26.1.12 | CC-BY-NC-SA-4.0 | NO | Look-at HUD | Per R2 verdict: keep jar or write own look-at HUD |
Recommendation: FOLD Leave My Bars Alone + Measurements + AutoHUD (+ AppleSkin) into diaithir-hud-overlays; CLEAN-ROOM look-at HUD later (Jade is NC-SA).

## Toasts (diaithir-hud-overlays)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Toast Control (Shadows-of-Fire) | 26.1.2..1.20.1 forge/neoforge; NF 26.1.2-10.0.0 | MIT | yes | Hide/filter toast types | In audit: port |
| Toast Remover (Azz_9) | 26.3..26.1 | MIT | yes | Remove toasts | Redundant |
| Fancy Toasts / Better Advancements (Bivrik) | 26.3..1.20; NF 1.4.7 | MIT | yes | Restyled advancement toasts | Optional |
| Advancement Plaques (Grend) | 26.3..1.12.2 | CC-BY-NC-ND-4.0 | NO | Plaque instead of toast | Clean-room if wanted |
| Disable Insecure Chat Toast | 26.3..1.19.1 | CC0-1.0 | yes | One toast | Trivial |
| The Open Sauce Toast Killer | 1.21.1..1.14.4 fabric | Apache-2.0 | yes | Toast removal | Old |
Recommendation: FOLD Toast Control into diaithir-hud-overlays (fancy styling via Fancy Toasts MIT if wanted).

## Pickup notices (diaithir-hud-overlays)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Pick Up Notifier (Fuzs) https://modrinth.com/mod/pick-up-notifier | 26.3..1.19 all | MPL-2.0 | yes | Item pickup log on HUD, ~100% | In audit: port |
| Vintage Pick Up Notifier (le_jack) | 1.7.10 forge | LGPL-3.0-only | yes | Same, legacy | Not needed |
| ItemPickupNotifier (AshKiano) | 26.3..1.21.10 fabric | MIT | yes | Same | Fabric |
| Loot Journal: Pickup Notifier (Obscuria) | 26.1.2..1.20.1 all | Obscuria Ecosystem | NO | Pickup + journal | Custom licence |
Recommendation: FOLD Pick Up Notifier (MPL-2.0) into diaithir-hud-overlays.

## Pings (diaithir-hud-overlays)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Ping Wheel (Luken) https://modrinth.com/mod/ping-wheel | 26.3..1.18; NF 1.12.1 | MIT | yes | Wheel + world ping markers, server-aware. ~100% | In audit: port. Very high downloads (15M) |
| Ping (Girafi) | 26.3..1.7.2 | ARR | NO | Ping markers | |
| Ping Wheel-Plugin / Click Ping Wheel | various | Apache-2.0 / MIT | yes | Addons | Optional |
Recommendation: FOLD Ping Wheel into diaithir-hud-overlays.

## Speech balloons (diaithir-hud-overlays)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Talk Balloons (CerbonXD) https://modrinth.com/mod/talk-balloons | 26.3..1.18 fabric/forge/neoforge | LGPL-3.0-only | yes | Chat bubbles above players. ~100% | In audit: port |
| TalkingClouds (KostarSf) | 1.20.4..1.18.2 fabric | MIT | yes | Same | Fabric |
| Proximity Chat Bubble (mybios) | 26.1.2 | MIT | yes | Same + proximity | 44 downloads, unverified quality |
| COH Chat Over Heads (Earu) | 1.21.11..1.20.1 | AGPL-3.0-only | licence-incompatible | Same | |
Recommendation: FOLD Talk Balloons into diaithir-hud-overlays.

## Tooltips (diaithir-tooltips)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| ShulkerBoxTooltip (MisterPeModder) | 26.3..1.16.5; NF 5.4.3 | MIT | yes | Container contents tooltip | Added per QOL_MODS (as jar) |
| Enchantment Descriptions (Darkhax) | 26.3..1.9.4 | LGPL-2.1-only | yes | Enchant text | In audit: port |
| Food Effect Tooltips (DaFuqs) | 26.3..1.17.1 | LGPL-3.0-only | yes | Food effects | In audit: port |
| Better Advanced Tooltips | audit | MIT | yes | F3+H tags/components | In audit: port |
| Held Item Tooltips (Fuzs) | 26.3..1.19.2 | MPL-2.0 | yes | Held-item name popup | Optional |
| Item Tooltips (Rebel459) | 26.3..1.21; NF 26.1-r2.4 | LGPL-3.0-only | yes | Tooltip styling/info | Optional |
| Effect Insights (Fuzs) | 26.3..1.18.2 | MPL-2.0 | yes | Effect descriptions | Optional |
| Durability Tooltip (SuperMartijn642) | 26.3..1.12 | ARR | NO | Durability line | Audit: clean-room (trivial) |
| Legendary Tooltips (Grend) | 26.3..1.12.2 | CC-BY-NC-ND-4.0 | NO | Frames/borders | Skip |
| Scrollable Item Tooltips | 26.1.2 fabric | MIT | yes | Scroll long tooltips | Fabric only |
Recommendation: FOLD Enchantment Descriptions, Food Effect Tooltips, Better Advanced Tooltips, ShulkerBoxTooltip into diaithir-tooltips; CLEAN-ROOM durability line.

## Inventory sorting (diaithir-inventory-tools / diaithir-inventory-ui)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Inventory Profiles Next (blackd) https://modrinth.com/mod/inventory-profiles-next | 26.3..1.14.1; NF 2.3.8 | AGPL-3.0-or-later | AGPL only if module also AGPL | Sort, auto-refill, profiles, lock slots. ~100% | In audit: port (AGPL; needs libIPN AGPL as well). Licence decision needed |
| Inventory Sorting / Inventory-Sorter (meza) | 26.3..1.19; NF 3.0.1 | MIT | yes | Sort player+containers, sorting buttons. ~80% | MIT alternative to IPN |
| Client Sort | audit | Apache-2.0 | yes | Client sort | In audit: merge |
| Lightweight Inventory Sorting (borknbeans) | 26.3..1.20.6 fabric | MIT | yes | Sort | Fabric |
| Nemo's Inventory Sorting | 26.3..1.19.2 | ARR | NO | Sort | |
| Sorted (L4stIdi0t) | 26.3..1.21 | ARR | NO | | |
| Inventory Essentials | audit | ARR | NO | | audit: clean-room |
| Smooth Swapping | per QOL_MODS | LGPL-3.0 | yes | Animation | Added |
Recommendation: FOLD Inventory Sorting (MIT) + Client Sort (Apache) into diaithir-inventory-tools; avoid IPN unless Marlon accepts AGPL for that module.

## Inventory search (diaithir-inventory-tools)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Searchables (jaredlll08) | NF 1.0.2 (26.1.2) | MIT | yes | Search-box library for creative/inventory | In audit: port |
| Persistent Inventory Search (Serilum) | 26.3..1.18.2 | ARR | NO | Keeps search text | |
| Item Searchbar (Dev-Sebi) | 26.3..26.2 fabric | MIT | yes | | Fabric |
| CreativeTabSearch (src_resources) | 1.20.4..1.20 | LGPL-3.0-only | yes | Creative search | Old |
| Search Item In Box (xzhao4545) | 1.20.1 forge | MIT | yes | Search containers | Idea source |
Recommendation: FOLD Searchables into diaithir-inventory-tools.

## Trash slot (diaithir-inventory-ui)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Simple Trash Slot (pajic) | NF 1.0.6+26.1.2 | MIT | yes | Trash slot. ~100% | Updated 2026-11-02 |
| TrashSlot (BlayTheNinth) | 26.3..1.18 | ARR | NO | | Audit: clean-room |
| Trash Slot (Capple) | 26.2..1.12.2 fabric/forge | OUFL-1.0 (custom) | unverified | | No NF 26.1.2 build |
Recommendation: FOLD Simple Trash Slot into diaithir-inventory-ui (replaces clean-room plan).

## Mouse tweaks (diaithir-inventory-tools)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Mouse Tweaks (YaLTeR) | 26.3..b1.7.3; NF 26.1-2.31 | BSD-3-Clause | yes | Drag-split, scroll-move, RMB drag. 100% | Audit: port |
| More Mouse Tweaks (NotRyken) | 26.3..1.21 fabric/neoforge | Apache-2.0 | yes | Extra | Optional |
| Legacy/Old Mouse Tweaks | 1.8.9 / 1.20.1 | MIT | yes | Legacy | |
Recommendation: FOLD Mouse Tweaks into diaithir-inventory-tools.

## JEI-replacement Codex (recipe viewer; own Codex store per CODEX_LIBRARY_STORE.md)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Just Enough Items (mezz) | 26.3..1.8; NF 29.53.0.115 | MIT | yes | Item/recipe lists, uses/recipes, bookmarks, plugin API. 100% | Plans say item-list clones forbidden by pack rule; licence permits port |
| Roughly Enough Items (shedaniel) | 26.3..1.13; NF 26.1.819 | MIT | yes | Same | |
| EMI (Emi) | 1.21.1..1.18.2; no NF 26.1.2 build | MIT | yes | Same | Stale for 26.1 |
| EMI Loot / Enchanting / Ores addons | 1.21.1 | MIT/LGPL | yes | Loot, enchant, ore tabs | Idea source for Codex pages |
| Not Enough Items (NEI), HowManyItems, JFMUY, retroEMI | 1.7.10..b1.5 | MIT/GPL | yes | Historic | Not useful |
| Distraction Free Recipes | 1.21.1 | custom (Tonis) | NO | | |
Recommendation: CLEAN-ROOM/FOLD Codex: base on REI or JEI (MIT) code only as a reference for recipe-category rendering; viewer itself is the Codex lane, not a new jar.

## Minimap / Atlas / waypoints (diaithir-map-utility, diaithir-waypoints)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Antique Atlas 4 (sisby / sleepingdragoninn) | 1.21.1..1.19.2 NF; no NF26.1.2 build; pack has 3.1.2 neoforge-26.1.2 | LGPL-3.0-or-later | yes | Atlas item, painted map | In audit: port; Surveyor (LGPL) as data source |
| Antique Atlas (tyra314) | 1.18.2..1.16.2 | GPL-3.0-only | yes | Original | Old |
| Xaero's Minimap/World Map | NF 26.6.2 for 26.1.2 | ARR | NO | Full minimap | Jar only |
| JourneyMap (mysticdrew) | NF 26.1.2-6.0.10 | ARR | NO | Minimap + web map | Jar only; JourneyMap Teams Apache-2.0 |
| FTB Chunks | audit | ARR | NO | Claims + map | Keep |
| VoxelMap-Updated | 26.3..1.17.1 | ARR | NO | | |
| Waystones (BlayTheNinth) | 26.3..1.16.5 | ARR | NO | | Clean-room diaithir-waypoints already done |
| Wraith Waystones (LordDeatHunter) | 26.1.2..1.17.1 fabric | MIT | yes | Waystones | Fabric; not needed |
| Waypoints (md5lukas), Server Waypoint (2676959) | 26.2..1.17 / 26.3..1.20 | MIT | yes | Server waypoints | Idea source |
| AxolotlClient Waypoints | 26.2..1.8.9 fabric | LGPL-3.0-or-later | yes | Client waypoints | |
Recommendation: PORT Antique Atlas 3/4 + Surveyor (LGPL) into diaithir-map-utility; waypoints stay on diaithir-waypoints (done); no free minimap exists -> CLEAN-ROOM minimap later only if needed.

## Structure navigation (diaithir-structure-navigation)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Structure Compass (Mrbysco) https://modrinth.com/mod/structure-compass | 26.3..1.15.2 forge/neoforge; NF 6.1.0 | MIT | yes | Compass that finds chosen structure. ~90% | Better than clean-room; fold |
| Structure Memory (xsoras) | 26.3..1.7.10 | Apache-2.0 | yes | Records discovered structures | In audit: port |
| Explorer's Compass (Chaosyr) | 26.3..1.18.2 | CC-BY-NC-SA-4.0 | NO | | Audit: clean-room, now moot |
| Luna's Structure Compass | 1.21.8..1.21.5 | MIT | yes | | |
| OmniCompass (MeVerdo) | 26.1.2..1.21.1 fabric/neoforge | MIT | yes | | |
| Advanced Locate (Kolala) | 26.2..1.20.1 fabric | MIT | yes | /locate improvements | |
Recommendation: FOLD Structure Compass + Structure Memory into diaithir-structure-navigation (replaces the clean-room plan).

## Zoom / first person / view tweaks (diaithir-client-view-input)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Zoomify (isxander) | 26.4-snap..1.18; NF 2.17.0 | LGPL-3.0-only | yes | Zoom | Audit: port |
| Just Zoom (Keksuccino), Ok Zoomer | 26.3 | DSMSL / ARR | NO | Zoom | |
| Zoom (AnECanSaiTin) | 1.21.3..1.21.1 neoforge | GPL-3.0-or-later | GPL | | |
| First-person Model (tr7zw) | 26.3..1.16.5 | MIT (Modrinth page says MIT; audit says tr7zw Protective for firstperson-neoforge) | mismatch: verify | Show body in first person | Licence conflict between audit and Modrinth; treat as clean-room unless jar licence file confirms MIT |
| Camera Overhaul (Mirsario) | 26.3..1.14 | GPL-3.0-or-later | GPL | View sway/lean | Optional |
| Real Camera (xTracr) | 26.3..1.18.2 | MIT | yes | 3rd-person camera | Optional |
| Cubes Without Borders, IMBlocker | audit | MIT / GPL-3 | yes | Borderless window, IME | Audit: port |
Recommendation: FOLD Zoomify + Cubes Without Borders + IMBlocker; CLEAN-ROOM first-person body (or fold FPM after licence file check).

## Menus (FancyMenu/Drippy) (diaithir-client)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| FancyMenu (Keksuccino) | 26.3..1.12; NF 3.9.14 | DSMSL v3.1 (custom) | NO (custom) | Full menu editor. 100% | Source-available custom licence, unverified terms |
| Drippy Loading Screen (+ Early Loading Module) | 26.3..1.16.2; NF 3.1.5 | DSMSLv3 | NO | Loading screen styling | |
| Main Menu Credits (isxander) | 26.3..1.18.2 | LGPL-3.0-only | yes | Credits button | No NF 26.1.2 build |
| Better Main Menu (Mitzingdash) | 1.21.1..1.20.1 fabric | MIT | yes | Main menu layout | |
| Clean Main Menu | | ARR | NO | | |
Recommendation: CLEAN-ROOM menu/branding in diaithir-client (we already own diaithir-branding); fold Main Menu Credits for credits screen. Keep FancyMenu out (no-new-jars).

## Loading screens (diaithir-client)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Drippy Loading Screen | see above | DSMSLv3 | NO | | |
| Mod Loading Screen (TakiSpl) | 26.4-snap..rd-132211 fabric/quilt | MIT | yes | Mod-load splash progress | Fabric only |
| Early Loading Screen (ishland) | 1.21.4..1.19.2 fabric | MIT | yes | | |
| Dark Loading Screen (A5b84) | 26.3..1.14 fabric/quilt | LGPL-3.0-only | yes | Dark bg | Fabric; trivial |
| Seamless Loading Screen (Minenash) | 1.21.1..1.16.2 | MIT | yes | | |
| diaithir-earlywindow-neoforge | audit | (ours) | yes | Early window | Already ours |
Recommendation: CLEAN-ROOM/extend diaithir-earlywindow (our own); borrow ideas from Dark Loading Screen (LGPL).

## Branding (diaithir-client)
| Candidate | Licence | Notes |
|---|---|---|
| diaithir-branding-neoforge (ours, MIT; Pixelify Sans font) | MIT | Already merged in audit |
| Main Menu Credits | LGPL-3.0-only | credits |
Recommendation: ADOPT own diaithir-branding (merge into diaithir-client); no external mod needed.

## F3 screen (keep separate or fold)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| BetterF3 (TreyRuffy) | 26.3..1.16; NF 18.0.2 | MIT | yes | Reformatted F3, modules, colours. ~100% | Audit: keep separate |
| BetterF3 Spark Module | 1.21.11..1.21 | MIT | yes | MSPT/spark line | |
| MiniHUD MSPT Provider | 26.1..26.1.2 fabric | CC0-1.0 | yes | | |
Recommendation: FOLD BetterF3 (MIT) into diaithir-hud-overlays rather than keep a jar (pack target is fewer jars).

## Accessibility (diaithir-client)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Disable Accessibility Screen (DaFuqs) | 26.3..23w03a fabric/neoforge/quilt | MIT | yes | Removes first-launch screen | Trivial |
| Speech To Text Accessibility (Orion_Moonclaw) | 1.21.11..1.21 fabric | GPL-3.0-only | GPL | Subtitles of speech | |
| Ari's Accessibility Tweaks | 1.20.1..1.19.4 | CC0-1.0 | yes | Options | |
| lands-visual-accessibility | 26.3..1.21.11 | MIT | yes | Visual options | 342 downloads |
| Vanilla accessibility (subtitles, high contrast, narrator) | built in | n/a | n/a | | |
| Extreme Sound Muffler | 26.3..1.18 | LGPL-3.0-only | yes | Per-sound muting | In audit: merge into diaithir-audio |
Recommendation: FOLD Disable Accessibility Screen + Extreme Sound Muffler; otherwise rely on vanilla options.

## Dynamic lights (diaithir-world-visuals)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| LambDynamicLights (LambdAurora) | 26.3..1.16.2; NF 4.11.2 | Lambda License (custom) | NO | Held-item/entity light. 100% | Audit: clean-room |
| Dynamic Lights (Tschipcraft) | 26.2..1.17; NF 1.9.3 | custom | NO | Resource-pack based | |
| Dynamic Lights (CreepermeYT) | 26.3..1.17 | MIT | yes | Dynamic lights. ~90% | Verified via Modrinth only |
| RyoamicLights (TexTrue) | 1.21.1..1.16.4 forge/neoforge | MIT | yes | Lamb port for Forge | Older base |
| Radiant Gear (TheIllusiveC4) | 1.20.6..1.18.2 | LGPL-3.0-or-later | yes | | |
| Dynamic Torches / Dynamic Lights Reforged (older) | 1.12-1.16 | various | unverified | | |
Recommendation: FOLD Dynamic Lights (CreepermeYT, MIT) or RyoamicLights (MIT) into diaithir-world-visuals instead of clean-room.

## Shaders / visual polish
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Iris | not on this search; pack: dropped, crashes with Mekanism | LGPL-3.0 (unverified here) | yes | Shader loader | Pack rule |
| Oculus | 1.20.1 forge | LGPL-3.0-only | yes | Iris for Forge | Dead for 26.1 |
| Better Clouds (qendolin) | 26.3..1.17; NF 1.13.6 | MPL-2.0 | yes | Volumetric clouds | Good fold |
| Enhanced Block Entities Reloaded | 26.3..1.16.5; NF 0.13.3 | LGPL-3.0-only | yes | Chest/bed baked models, perf | Fold candidate |
| Sodium Extra | 26.3..1.16.2; NF 0.9.5 | LGPL-3.0-only | yes | Fog, cloud, animation toggles | Audit: keep |
| Visuality (audit) | MIT | yes | Particles | Audit: clean-room |
Recommendation: FOLD Better Clouds + Sodium Extra settings into diaithir-world-visuals; skip shader packs (no new jars).

## Skybox (diaithir-world-visuals)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Sky Aesthetics | audit | MIT | yes | Skybox replace | Audit: merge |
| Skyboxify (omo50) | 26.3..1.21 fabric | GPL-3.0-only | GPL | Custom skybox | |
| Better End Sky | 26.3..1.18.2 | MIT | yes | End sky | |
| Dramatic Skys | | ARR | NO | | |
Recommendation: FOLD Sky Aesthetics into diaithir-world-visuals.

## Falling leaves (diaithir-world-visuals)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Falling Leaves (Fourmisain) | 26.3..1.16 fabric | MIT | yes | Particles. 100% | Fabric original |
| Falling Leaves NeoForge (cheaterpaul) | 26.3..1.16.3; NF 26.1.2-3.1.0 | LGPL-3.0-only | yes | Same | In pack (audit: merge) |
| Falling Leaves Plus (Fuzs) | NF 26.1.2 | MPL-2.0 | yes | More leaves | |
Recommendation: FOLD Falling Leaves NeoForge into diaithir-world-visuals (already routed).

## Ambient soundscapes (diaithir-audio)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| AmbientSounds (Dr. Lillith/Creative) | audit | LGPL-3.0-only | yes | Biome ambience | In audit: merge; 84 MB assets (QOL_MODS says excluded for size) |
| Dynamic Surroundings Rebirth (uawyiegrfv) | NF 1.4.2 on 26.1.2 | MIT | yes | Biome/weather/footstep ambience. ~80% | Fresh candidate; modern |
| Dynamic Surroundings (OreCruncher) | 1.21.1..1.17.1 fabric/NF | MIT | yes | Original design | |
| Dynamic Surroundings Unofficial 1.7.10 / Remastered | 1.7.10 / 1.19.2 | MIT | yes | Legacy | Idea source |
| MAtmos (tc.gaming108) | 26.3..1.12.2 | ARR | NO | Ambience | |
| Presence Footsteps | 26.3..1.7.10 fabric | Polyform Shield | NO | Footsteps | NF port MIT (1.21.8) only |
| Ambient Caves | 1.19.4..1.16.5 | MIT | yes | Cave sound pack | Assets |
Recommendation: FOLD Dynamic Surroundings Rebirth (MIT, NF 26.1.2) + AmbientSounds (LGPL, trimmed assets) into diaithir-audio.

## Sound propagation / physics (diaithir-audio)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Sound Physics Remastered (henkelmax) | 26.3..1.19; NF 1.5.2 | GPL-3.0-only | GPL only | Reverb, occlusion. 100% | Audit: merge (GPL taint on module) |
| Sound Physics Perfected (RedLifedev) | 26.3..1.20 | MIT | yes | Same family | Alternative MIT base |
| Sound Acoustic Physics (Macaroon3145) | 26.2..1.21.11 | MIT | yes | | |
| Sound Physics (thedocruby) | 1.18.1..1.17 fabric | LGPL-2.1-only | yes | Original | |
| Dynamic Sound Filters (andre111) | 1.21.1..1.19.3 fabric | Apache-2.0 | yes | Muffle underwater/walls | |
Recommendation: FOLD Sound Physics Perfected (MIT) instead of GPL Remastered, if GPL cannot be accepted in diaithir-audio.

## Instruments (diaithir-audio)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Immersive Melodies (Luke100000) | 26.2..1.18.2; NF 0.8.3 | GPL-3.0-only | GPL | Playable instruments + MIDI. ~100% | Audit: merge |
| Immersive Melodies in Backpacks | 1.21.1 | MIT | yes | Compat only | |
| Gain Friendship From Melodies | 1.21.1..1.20.1 | MIT | yes | | |
Recommendation: FOLD Immersive Melodies into diaithir-audio (GPL: confirm module licence).

## Entity model / texture customization (diaithir-entity-animation)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Entity Model Features (Traben) | 26.3..1.18.2; NF 3.3.12 | LGPL-3.0-only | yes | CEM models/animation | Audit: merge |
| Entity Texture Features (Traben) | 26.3..1.16.5; NF 7.2.7 | LGPL-3.0-only | yes | Random/emissive entity textures | Audit: merge |
| Not Enough Animations (tr7zw) | audit | tr7zw Protective | NO | Player anims | Audit: clean-room |
| Enhanced Block Entities Reloaded | see above | LGPL | yes | BE models | |
Recommendation: FOLD EMF + ETF into diaithir-entity-animation.

## Emotes (diaithir-entity-animation)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Emotecraft (KosmX) | 26.3..1.16.5; NF 3.3.0-b164 | GPL-3.0-or-later | GPL | Player emotes + server sync | Audit: merge |
| Emote Tweaks | 1.21.1 | MIT | yes | | |
| Player Animation Library | audit | MIT | yes | Lib | Kept |
| Emotecraft: Borrow Their Emote | | CC-BY-ND-4.0 | NO | | |
Recommendation: FOLD Emotecraft (GPL) into diaithir-entity-animation.

## Connected textures (keep Fusion)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Fusion (Lilly) | audit | ARR | NO | CTM models | R2: keep jar |
| Continuity (PepperCode1) | 26.3..1.17.1; no NF 26.1.2 build (continuity-neoforged 1.21.1..26.3) | LGPL-3.0-only | yes | OptiFine-format CTM. ~90% | Fabric base; Continuity: NeoForged (aspctt) is a port |
| CTM Optifine - Fabric (Aeldit) | 26.2..1.17 | GPL-2.0-only | GPL | | |
| CTMLib (in pack, audit) | LGPL-3.0-only | yes | Lib | |
| Chisel / ConnectedTexturesMod (tterrag, 1.7-1.12) | unverified | unverified | unverified | Original CTM | Not seen on Modrinth |
Recommendation: PORT Continuity (LGPL) into diaithir-world-visuals if Fusion jar is to go; else ADOPT Fusion as-is (already pack).

## 3D skin layers (diaithir-entity-animation)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| 3D Skin Layers (tr7zw) | 26.3..1.8.8; NF 1.11.4 | tr7zw Protective | NO | | Audit: clean-room |
| 3D Skins (AlphaLeoli) | | ARR | NO | | |
| Legacy 3D Skin Layers (Wyvest) | 1.8.9 | GPL-3.0-only | GPL | Concept | |
Recommendation: CLEAN-ROOM (small: extruded overlay voxel mesh in player renderer).

## Client performance, Sodium-class
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Sodium (CaffeineMC) | NF 0.9.2 (26.1.2) | Polyform Shield 1.0.0 | NO | Renderer. 100% | Keep jar |
| Embeddium (FiniteReality) | 1.21.4..1.16.5 | LGPL-3.0-only | yes | Sodium fork for Forge | No 26.1 build, last update 2025-01 |
| Sodium Extra, Reese's Sodium Options | NF builds | LGPL-3.0-only / MIT | yes | Options | |
| ImmediatelyFast (RaphiMC) | NF 1.15.3 | LGPL-3.0-or-later | yes | GUI immediate renderer | Audit: merge to diaithir-client-render-culling |
| Dynamic FPS (juliand665) | NF 3.11.7 | MIT | yes | Throttle unfocused | Audit: keep |
| More Culling (FX) | NF 1.7.4 | GPL-3.0-only | GPL | Face culling | |
| ModernFix | NF 5.27.25 | LGPL-3.0-only | yes | Load time, RAM | Audit: keep |
| Noisium(Forked) | 26.2..1.21 | LGPL-3.0-only | yes | Noise gen | No NF 26.1.2 build |
| Ksyxis | NF 1.4.6 | MIT | yes | Spawn chunk skip | Audit: merge |
Recommendation: ADOPT Sodium jar; FOLD ImmediatelyFast, Dynamic FPS, Ksyxis into diaithir-client-render-culling / worldgen-chunk-opts.

## Lithium
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Lithium (CaffeineMC) | NF 0.24.7 (26.1.2); 26.3..1.16.2 | LGPL-3.0-only | yes | Game-logic opts | Audit: keep |
| Lithium Modpack, Raycast Fix | | MIT / CC-BY-4.0 | yes | Variants | |
| Alternate Current | audit | MIT | yes | Redstone | Audit: merge |
Recommendation: ADOPT Lithium jar as-is (already pack-eligible); fold Alternate Current into diaithir-server-logic-tweaks.

## C2ME / chunk threading
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| C2ME NeoForge (ishland) | NF 0.4.0-alpha.0.100 (26.1.2) | MIT | yes | Parallel chunk IO/gen | In pack (audit: keep) |
| C2ME OpenCL module | | ARR | NO | | |
| Connectored C2ME / C2ME Forge | 1.20.1 | MIT | yes | | |
| Starlight (spottedleaf) | 1.20.4..1.17 | LGPL-3.0-only | yes | Lighting engine (superseded) | |
Recommendation: ADOPT C2ME NeoForge as-is (alpha status; watch crashes).

## FerriteCore
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| FerriteCore (malte0811) | NF 9.0.0 (26.1.2); 26.3..1.16.5 | MIT | yes | Memory use. 100% | In pack (audit: keep); last NF update 2026-03 |
Recommendation: ADOPT FerriteCore as-is.

## Entity culling
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Entity Culling (tr7zw) | 26.3..b1.7.3; NF 1.11.3 | tr7zw Protective | NO | Async path-tracing culling | Audit: clean-room |
| Entity Culling (Meldexun) | 1.16.5..1.12.2 | ARR | NO | | |
| Entity Culling Unofficial (TCLProject) | 1.7.10 forge | MIT | yes | Old entity cull | Algorithm basic |
| Entity culling backport (piesilhouette) | 1.6.4 | MIT | yes | | |
| More Culling (FX) | GPL-3.0 | GPL | Block/entity face cull | |
| PartiCull | 1.21.1..1.20 | PolyForm Shield | NO | | |
Recommendation: CLEAN-ROOM (diaithir-client-render-culling), starting from Entity Culling Unofficial MIT code for the occlusion test.

## Async / scalable lighting
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| ScalableLux (ishland) | NF 0.3.0-alpha.0.18 (26.1.2) | LGPL-3.0-only | yes | Light engine rewrite | Audit: port into diaithir-worldgen-chunk-opts |
| Starlight (spottedleaf) | 1.20.4..1.17 | LGPL-3.0-only | yes | Original engine | |
Recommendation: FOLD ScalableLux (alpha; keep jar until stable).

## Server tick optimisations (diaithir-server-logic-tweaks)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| BadOptimizations (thosea) | NF 2.4.1 | MIT | yes | Various | Audit: port |
| ServerCore (Wesley) | audit | MIT | yes | Entity/chunk tick | Keep |
| Alternate Current, FastFurnace, EfficientHashing, RailOptimization | audit | MIT / LGPL / GPL | yes | | merges in audit |
| FastSuite, FastWorkbench | audit | MIT | yes | Crafting | |
| AI Improvements | audit | ARR | NO | AI tuning | Clean-room |
| spark (lucko) | NF 1.10.187 | GPL-3.0-only | profiler | Profiling | Keep separate |
| Observable | 1.21.4..1.16.5 | MPL-2.0 | yes | Profiler | |
Recommendation: FOLD as already routed; keep spark as the single profiler jar.

## Crash reporting (diaithir-crash-tools)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Crash Assistant (KostromDan) | NF 1.11.12; 26.3..1.6.4 | KostromDan MML-1.1.3 (custom) | NO | Crash GUI + log analysis | Audit: clean-room |
| Crash Utilities (Darkere) | 1.20.1 forge | MIT | yes | Crash tools | In audit as port |
| spark | GPL | profiler | | |
| Mixin Conflict Helper | 1.21.5..1.19 fabric | LGPL-3.0-only | yes | Mixin conflict hints | |
Recommendation: FOLD Crash Utilities; CLEAN-ROOM a crash window (diaithir-earlywindow).

## Network compatibility / version checks (diaithir-network-compat)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Better Compatibility Checker (nanite) | NF 26.1.2.1 | ARR (Modrinth) | NO | Modpack-version handshake | Audit: clean-room |
| Packet Fixer | audit | MIT | yes | Packet limits | Port |
| Modpack Update Checker (omo50) | 1.21.6..1.16.5 | CC-BY-NC-ND-4.0 | NO | | |
| Simple Update Checker (Patbox) | fabric/quilt | LGPL-3.0-only | yes | | |
| Simple Modpack Update Checker | 26.3..1.21 fabric | MIT | yes | | |
| NeoForge handshake / `acceptedVersions` | built in | n/a | | Mod-list check | Use in clean-room |
Recommendation: FOLD Packet Fixer; CLEAN-ROOM version handshake (small).

## Multiloader abstraction libs and config GUIs (diaithir-multiloader-compat)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Architectury API (shedaniel) | NF 20.1.17 (builds up to 26.1.2); 26.3..1.16.5 | LGPL-3.0-only | yes | Cross-loader API | Audit: port into multiloader-compat |
| YACL (isxander) | NF 3.9.7 | LGPL-3.0-or-later | yes | Config GUI lib | Audit: keep |
| Cloth Config (shedaniel) | NF 26.1.154 | LGPL-3.0-only | yes | Config GUI | Audit: keep |
| JamLib | 26.3..1.18 | MIT | yes | Multiloader | audit keep |
| Resourceful Config / Lib, Configured, Forge Config API Port | audit | MIT / LGPL / MPL | yes | | keep |
| Platform (ItsBlackgear), The Mighty Architectury | | LGPL / MIT | | | |
| Mod Menu (Prospector) | fabric/quilt; NeoForge Edition 1.21.11 | MIT | yes | Config entry screen | No NF 26.1.2 build |
Recommendation: FOLD Architectury API into diaithir-multiloader-compat; ADOPT YACL and Cloth Config as the two config GUI libs (drop the others where possible).

## Library dependencies (consolidation)
Libraries (open) kept per audit: Geckolib MIT, Curios LGPL-3.0, Puzzles Lib MPL-2.0, Titanium MIT, Cucumber MIT, Placebo MIT, Mantle MIT, Silent Lib MIT, Cyclops Core MIT, L2 Library LGPL-2.1, Resourceful Lib MIT, Lithostitched MIT, TerraBlender LGPL-3.0, Yung's API LGPL-3.0, GuideME (multi-OSS), Modonomicon MIT+CC-BY-4.0. ARR libs needing clean-room or removal: Balm, Shogi, Cupboard, GlitchCore, Iron's Lib, FTB Library/Teams/XMod, SuperMartijn642 Core/Config Lib, Sophisticated Core. Custom/NC: CodxLib, Cristel Lib (CC-BY-NC-ND), Fragmentum, Valhelsia Core.
Recommendation: ADOPT open libs as-is; CLEAN-ROOM or drop the ARR libs only when their last dependent leaves (rule in R2 file).

## Launcher, packwiz, our own distribution/updater
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| packwiz / packwiz-installer (packwiz org) | n/a (CLI) | MIT (unverified) | yes | Pack format + installer | Not checked via GitHub |
| Packwiz Modpack Loader (EvieTheOwl) | 1.21.10..1.19 fabric/quilt | MIT | yes | In-game packwiz sync | Fabric |
| PackWiz-ard (Adammatthiesen) | 1.21.1 fabric/neoforge | MIT | yes | | |
| Prism Launcher | n/a | GPL-3.0 (unverified) | | Instance format | Distribution only |
| Astro Sync | 1.21.11..1.20 | ARR | NO | | |
| Resourcify (DeDiamondPro) | NF 1.8.7 | LGPL-3.0-only | yes | In-game pack browser | |
Recommendation: CLEAN-ROOM our own updater in diaithir-client using packwiz-style manifest (no CurseForge/Modrinth publishing rule), borrowing PackWiz-ard (MIT).

## Headless test bot / fake client
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| NeoForge FakePlayerFactory / GameTest framework (loader built-in) | 26.1.2 | LGPL-2.1/MIT | n/a | Server-side fake players, gametests, `/test` | Server-only; no network client |
| Minecraft GameTest (vanilla `/test`, test instances) | 26.1.2 | Mojang | n/a | In-world assertions | Needs structure NBT; vanilla |
| Carpet (gnembon) /player spawn | 26.3..1.14.4 fabric only; no NF build | MIT | yes (code) | Fake players with actions | Fabric only |
| Fake Players (duzos) | 26.2..1.19.2 all; no NF 26.1.2 build | LGPL-3.0-or-later | yes | Server fake players | |
| Advanced Fake Player (Theus452) | 1.21.1..1.20.1 | MIT | yes | | |
| StressTestBots (ShaneBee) | 26.2..1.21.3 | MIT | yes | Bot load testing (Paper plugin?) unverified | |
| simpleAFKBot | 26.3..26.1 fabric | MIT | yes | | |
| Mineflayer (PrismarineJS) | Node bot, 1.8..latest | MIT (unverified) | yes (external) | Real protocol client | Not a mod; best fit for headless client |
| HeadlessMC (3arthqu4ke) | runs real client headless | MIT (unverified) | external tool | Real client in CI | Not verified in session |
Recommendation: CLEAN-ROOM a small test-bot lane (diaithir test mod using FakePlayerFactory + GameTest) and use Mineflayer externally for protocol-level joins; Carpet is Fabric-only reference.

## Server watchdog / backup tools (diaithir-admin-core)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Simple Backups (ChaoticTrials/MelanX) | NF 26.1.6; 26.3..1.18.1 | Apache-2.0 | yes | Scheduled backups | Audit: merge |
| FastBack (pcal43) | NF 0.33.1; 26.3..1.19.2 | GPL-2.0-only | GPL | Git-based snapshots | |
| Advanced Backups (HeatherWhite) | 1.21.4..1.7.10 | BSD-3-Clause | yes | | |
| Backup Manager | 1.21.5..1.18.2 | BSD-4-Clause | yes | | |
| Fast Async Backups | 1.21.11 NF | MIT | yes | | |
| Chunky (pregen) | audit | GPL-3.0 | keep | | |
| ServerCore, Watchdog Essentials (OMS addon) | 1.20.1 forge/neoforge | MIT | yes | Watchdog-style monitoring | tiny |
| Vanilla server watchdog (max-tick-time) | built in | | | | |
Recommendation: FOLD Simple Backups into diaithir-admin-core; use vanilla watchdog plus a clean-room tick-stall reporter.

## Chat features (diaithir-chat-client)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| No Chat Reports (Aizistral) | NF 2.19.0 | WTFPL | yes | Unsigned chat | Audit: merge |
| Chat Heads (dzwdz) | NF 1.3.2 | MPL-2.0 | yes | Heads beside chat | Audit: merge |
| More Chat History (JackFred) | fabric 26.3..1.16.5 | CC0-1.0 | yes | Longer history | Replaces ARR LongerChatHistory |
| Emojiful (Buuz135) | NF 26.1.2-5.3.2 | MIT | yes | Emojis in chat | Optional |
| Emoji Type, Chat Heads (SyddersLMAO) | | GPL / AGPL | | | |
Recommendation: FOLD No Chat Reports, Chat Heads, More Chat History (CC0, replace ARR mod).

## Player heads (diaithir-chat-client / items)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Player Heads (tnjs) | 26.3..1.20 | MIT | yes | Head drops | Datapack |
| Just Player Heads (Serilum) | 26.3..1.16.5 | ARR | NO | | |
| Simple Player Heads (fliplus) | 1.21.8..1.20 fabric | MIT | yes | | |
| Custom Player Heads | 1.21..1.19.2 fabric | MIT | yes | | |
| Chat Heads | covered above | | | | |
Recommendation: FOLD Player Heads (MIT datapack-style) if head drops needed; otherwise none.

## Voice chat (diaithir-voice)
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| Simple Voice Chat (henkelmax) | NF 2.6.27 (26.1.2); 26.w14a..1.12 | ARR | NO | Proximity voice | Clean-room diaithir-voice (ports #73) |
| Voice Chat Interaction, Enhanced Groups | | ARR | NO | | |
| Replay Voice Chat | MIT | yes | Replay integration | fabric |
| Simple Voice Chat Discord Bridge (amsam0) | NF 26.3..1.16.5 | MIT | yes | Bridge | |
Recommendation: CLEAN-ROOM diaithir-voice (already underway).

## Dish-icon photos (food photo icons)
Searched "dish photo", "food photo", "screenshot": no mod renders food icons from photographs. Nearest: Camerapture (chrrs, MIT, NF 1.10.14, camera item taking in-world pictures), Screenshot Viewer (MIT), Photo Mode (ARR, b1.7.3). Recommendation: CLEAN-ROOM (dish icons are a resource/data job: AI-generated or rendered photos as item textures; no code needed); optionally FOLD Camerapture's render-to-texture code.

## Mod menus
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| NeoForge built-in Mods screen + config button | 26.1.2 | LGPL | n/a | Mod list, config | Sufficient |
| Mod Menu (Prospector) | fabric/quilt | MIT | yes | | NeoForge Edition (Raguto) 1.21.11 only |
| Game Menu Mod Option | 1.20.4..1.16.4 | LGPL-3.0-only | yes | Button | |
Recommendation: ADOPT NeoForge built-in; no mod.

## Recipe viewers (separate from Codex)
Same table as the Codex section. Recommendation: use REI (MIT, NF 26.1.819) or JEI (MIT, NF 29.53) as code reference only for Codex; if Marlon relaxes "no item list", ADOPT JEI jar as-is (84 NF 26.1.2 builds, updated 2026-11-02).

## Item-render / GUI scaling
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| GUI Scaler (netleak) | NF 26.1.2-1.4.5 | LGPL-3.0-only | yes | Auto GUI scale | Fold |
| Precise-gui-scale | 26.3..1.21 | MIT | yes | Fractional scale | Fold |
| GUI Scale Splitter | 1.21.10..1.20.1 | GPL-3.0-only | GPL | | |
| ImmediatelyFast | above | | | GUI batching | |
| OptiGUI | audit | LGPL-3.0-or-later | yes | Custom GUIs | Audit: port |
Recommendation: FOLD GUI Scaler (or Precise-gui-scale) into diaithir-client-view-input.

## Controller support
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| MidnightControls (TeamMidnightDust) | NF 1.12.1+26.1 | MIT | yes | Gamepad support. ~100% | Controllable (MrCrayfish) not found on Modrinth search |
| MidnightControlsExtra | 1.21.10..1.18 | MIT | yes | | |
| Controllable (MrCrayfish) | CurseForge, unverified | CC (unverified) | unverified | | |
Recommendation: FOLD MidnightControls (MIT) into diaithir-client-view-input.

## Mobile / touch
| Candidate | MC/loader | Licence | Port? | Covers | Notes |
|---|---|---|---|---|---|
| TouchController (fifth_light) | NF 0.3.1-alpha16; 26.4-snap..1.12.2 | LGPL-3.0-or-later | yes | Touch controls on Java | Alpha |
Recommendation: ADOPT/FOLD TouchController only if mobile is in scope; else none (low priority).

## Existing test-bot / fake-player mods (for the headless client bot)
| Tool | Kind | Licence | Notes |
|---|---|---|---|
| Carpet /player (gnembon) | server mod, fabric only | MIT | Spawn fake player, run actions; no NF 26.1.2 build |
| Carpet Extra, Carpet TIS Addition, Carpet PVP | fabric | MIT / LGPL | Extend fake player |
| Fake Players (duzos) | all loaders, 26.2 max | LGPL-3.0-or-later | No NF 26.1.2 build |
| Advanced Fake Player (Theus452) | 1.21.1 | MIT | |
| FakePlayerFactory (NeoForge API) | in-loader | | Use for server-side bots |
| GameTest framework (vanilla / NeoForge) | in-loader | | `/test run`; structure-based asserts |
| StressTestBots (ShaneBee) | 26.2..1.21.3 | MIT | Load-testing bots (platform unverified) |
| Mineflayer (PrismarineJS) | Node library | MIT (unverified) | Real protocol client |
| HeadlessMC (3arthqu4ke) | launcher | MIT (unverified) | Real vanilla/NeoForge client without display |
Recommendation: see Headless test bot section.
