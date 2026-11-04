# MEGAMACHINES: mega construction and extraction vehicles, and megastructures (D1139, 2026-11-03)

Marlon 11-03: "there should be mega construction and extraction vehicles and mega structures." Own names, own art (64 px Industrial Factory look). Real machines are the basis; numbers are SI per UNITS.md. Optional systems reach players as Codex quests, no switches. Catalogue: `plans/megamachines/catalog.json|tsv`, made and checked by S6899 (`cloud/megamachines/gen_megamachines.py`).

## 1. Vehicles (12, Age gated)
Age I-II has none (hand tools). III treadwheel crane. V steam navvy and walking dragline. VI bucket-wheel excavator, tunnel boring machine, haul truck, crawler crane, crawler transporter. VII autonomous excavator and haul truck. VIII mountain strip miner. RODOS terraform builder. Each row carries mass (t), power (MW), medium dug, efficiency, dig rate (m3/s), crew, walkable deck (m2) and its real-world basis.

Dig rate is not typed in by hand: it must equal power x efficiency / specific energy of the medium (soil 2, overburden 6, ore 25, rock 40, regolith 60 MJ/m3). The generator rejects a row off by more than 25%. So a bigger drive digs faster by physics, and hard rock is slow.

## 2. Megastructures (7)
Aqueduct arcade (III), ship lock flight (V), great dam (VI, 500 MW out), arcology tower (VII, settlement hub), space elevator (VIII), orbital ring and Dyson collector swarm (RODOS, feed the Shardfall Gate launch bank). Each is a multiblock built from a blueprint by builder vehicles plus bulk material in pallets; stages show progress, the finished structure turns on its function (power, water level, transit, housing). Block estimate stays under 100k so a server holds it; sky-scale ones (elevator, ring, swarm) build as a column plus a data-driven remote part, not literal blocks to orbit.

## 3. How they work in the world
- **Digging and building.** A vehicle works a swept volume (bucket arc, wheel face, bore cylinder) at its rate. Blocks removed go into the output hopper; builders do the reverse from a blueprint. Work is tick-sliced (rate x tick) so no chunk-wide stall.
- **Walkable.** Every vehicle is an assembled Valkyrien Skies 2 ship (diaithir-ships, ported) with an interior deck and ladders; the player walks on and rides it while it moves. Seats and cabs are real blocks. Archimedes' Ships (#128) is the fallback if VS2 is unavailable.
- **Physics standard.** Follow the vehicle bot thread's tests: mount by empty-hand use works, engine and fuel present on spawn, mass from the part table, no clip through terrain, deck stays stable at rest and at full speed. The checklist in section 6 is what the bot runs.
- **Assay and magnitude.** Dug material goes through the assay roll for the deposit it came from; deposit magnitude scales yield and depletes with volume removed, so a strip miner empties a field and shows it in the Atlas.
- **Containers and pallets.** Output leaves as pallets and bulk containers (same ids and tags as MUNITIONS_CONTAINERS.md: `c:` container tags plus a data component with count/capacity), loaded by conveyor or haul truck. Nothing spills into the world.
- **Crews, wages, autonomy.** Every vehicle keeps its crew seats. Hired NPC operators (fed rations per PROGRESSION) are paid from the employer's treasury; unpaid crews strike, then revolt (NPC wages thread). A machine runs crewless only when its type is marked `autonomy_capable` (the four Age VII+ machines) AND an autonomy module (a crafted item) is installed; the Age alone grants nothing. The check hooks the autonomy thread's per-entity API (#220), not an Age test. Without the module the machine needs its crew, whatever its Age.
- **Power, fuel, upgrades.** Each vehicle lists its engine classes (diaithir-units ids: draft_animal, steam_piston, diesel_engine, electric_motor, fuel_cell, arcane_motor). Fuel comes from the shared fuel table, so magic is a fuel like diesel; arcane_motor is allowed from Age VI only (checked). Power draw in W through diaithir-units. Factorio-style modules and quality apply (UPGRADES.md): drive, bucket and efficiency modules.
- **Stations, not the grid.** Vehicles are made at the Heavy Yard (Age evolving: timber yard, foundry slip, assembly hall, autonomous yard). Parts are cast and pressed, then a few major parts are joined (hull, drive, boom, cab). No crafting-grid recipe.

## 4. Reuse (mod-first)
Immersive Vehicles (ours, ARR) stays the small-vehicle path and gives the seat, controls and engine parts for the Age V-VI trucks and crawlers. Valkyrien Skies 2 and Eureka supply assembly and mass. Create (diaithir.8) rotation drives the cranes and wheels. Keelwright (SHIPBUILDING.md) shares the part catalog, power grid and crew logic; megamachines is a second catalog in the same generator, not a new jar. Host: diaithir-ships/keelwright (vehicles) and diaithir-worldsystems (structures). No new jar.

## 5. Build order (cheapest first)
1. Catalogue and validator (this PR, no Java).
2. Generator: catalogue to block and item defs, lang (English then the 130-culture names), Age data, Heavy Yard recipes.
3. Walkable chassis plus crawler drive on VS2; the tank test (IV) mounts first.
4. Dig and build engine (swept volume, hopper, pallets); wire assay and magnitude.
5. Crew seats, wages, autonomy-capable flag plus autonomy module check (#220).
6. Structures: blueprint staging, then function hooks (power, water, transit).
7. Codex pages, Panscriptum entries and quests; bot tests.

## 6. Bot test checklist (real world at spawn, one thing per test)
Mount the machine; walk its deck while it moves; dig 1 m3 of soil and check the hopper count equals the rate x time; assay result appears; pallet fills and empties onto a conveyor; unpaid crew strikes; Age VII machine with the autonomy module runs crewless, and without the module refuses to run; finished dam produces W.

## 7. Open points
Block art, sounds and Panscriptum text are not started. All names and numbers are ours; real machines are only a basis. Gaps need Java in diaithir-ports (not attached to this thread).
