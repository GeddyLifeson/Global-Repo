# MEGASTRUCTURES: blueprints and staged construction (D1140, 2026-11-03)

Split from MEGAMACHINES.md (section 2 and the structure steps of its build order). Marlon: build big things up in stages over the Ages, at Age-evolving stations, minimal crafting grid, materials and labour from storage networks and containers. Data is made and checked by S6917 (`cloud/megamachines/gen_megastructures.py`) from the S6899 catalogue; output is `plans/megamachines/blueprints.json`, `stages.tsv`, `codex_megastructures.tsv`. All numbers are SI (UNITS.md). Stage splits and fleet sizes are our design values; the real structure is only the basis and every stage cites its real phase.

## 1. Mod-first (MOD_SURVEY.md, Global-Repo #28)
No mod builds dams, aqueducts, lock flights, towers, elevators or rings. Calls:
- **Staged-build mechanic:** FOLD ideas from RFTools Builder (MIT, volume copy/place/remove with a moving builder) and the placement UX of Portable Blueprints (MIT); MineColonies builder-hut staging (GPL-3, ours via Structurize) is reference only. Each is a different MC version; RFTools Builder newest is 1.21.1, so it is a port, not a drop-in. Per the survey, the engine that places a stage is clean-room in diaithir-worldsystems, borrowing the RFTools volume walker under MIT.
- **Placement actors:** the builder vehicles in the catalogue (cranes, excavators, TBM, terraform builder) are the actors; Create deployers (MIT) stay the small-scale actor.
- **Arm motion:** Create Aeronautics Physics Gantry (MIT) and Extended Gantries (GPL-3) for crane booms only, rewritten on VS2.
- **Sky parts:** no mod. Clean-room, tied to the Foundry Sky ladder.
- **Licence rule:** GPL code (MineColonies ideas, Extended Gantries) lives in its own module inside an existing jar. No new jars.

## 2. Blueprint
A blueprint is an item carrying data component `megamachines:blueprint` = {structure id, stage index, origin (x,y,z), facing, culture id}. It is made, not crafted in a grid:
1. **Survey.** The Atlas/Surveyor marks a site; sites need flat ground, water or rock per structure kind (a dam needs a valley, a lock flight a slope with water).
2. **Site office.** The only crafting surface. It evolves with the Age: drafting floor (III), drawing office (V), engineering office (VI), design studio (VII), planning hall (VIII), shard plotter (RODOS). One block per site, upgraded in place by modules (UPGRADES.md). It prints the blueprint and keeps the stage ledger. A structure cannot be started at an office older than its Age.
3. **Ghost.** The placed blueprint shows the next stage as a ghost volume; finished stages are solid and stay valid across Age changes (ids never change).

## 3. Stages
Each structure has 4 to 6 stages from its real build phases (table in `stages.tsv`). A stage is one of:
- `dig`: a builder digger removes a swept volume at its catalogue rate (m3/s). No materials.
- `place`: a crane or navvy places blocks from delivered material, rate = P x eta / (g x h), with eta 0.4 for hoists whose vehicle row has none and h half the build height (literal blocks stop at 500 m).
- `remote`: sky-scale data-driven part for elevator, ring and swarm. Mass is lifted by a launch/beam budget at P x 0.5 / (MJ per tonne to orbit: 33 LEO, 57 GEO, 62.5 escape). No literal blocks; the Atlas and Codex show it as a progress arc.

Rules the generator enforces: builder exists and is not from a later Age; builders can dig if they dig; material tags exist and are not earlier than their Age; mass fractions and block fractions each sum to 1; a stage finishes in at most 168 h of fleet work with at most 64 builders (remote stages: 1 launch bank); total blocks under 100k; function share never falls and ends at 1.

Result today (hours are fleet work, not wall time): aqueduct 153 h, lock flight 652 h, dam 771 h, arcology 864 h, elevator 444 h, ring 413 h, swarm 347 h.

## 4. Materials and labour flow
- **Materials** are `c:` tags per BUILDING_MATERIALS.md and INTEGRATION.md: `c:stone/cut`, `c:timber/beam`, `c:mortar/lime`, `c:brick/fired`, `c:beams/steel`, `c:rebar`, `c:concrete/precast`, `c:cement/bulk`, `c:glass_blocks`, `c:plate/steel`, `c:composite/panel`, `c:tether/ultrahigh`, `c:feedstock/shard`. Tags marked `proposed` in the generator (`c:stone/cut`, `c:timber/beam`, `c:tether/ultrahigh`) are not yet in a plan and need a row in BUILDING_MATERIALS before ids are made.
- **Delivery.** Packaged goods move on pallets (1 t), bulk goods in bulk containers (20 t payload), the same ids and `c:` container tags as MUNITIONS_CONTAINERS.md. A **site depot** block next to the structure exposes the standard item handler; it has no GUI of its own and no storage. It pulls from adjacent containers and from any storage network that reaches it (containers thread), and each stage shows its pallet and container count.
- **Labour.** Builders keep their crew seats (MEGAMACHINES section 3). A stage's crew-hours (`stages.tsv`) are paid by the employer through the NPC wages API; unpaid crews strike and the stage pauses. Autonomy-capable builders run crewless only with an autonomy module fitted, as in MEGAMACHINES.
- **Pause and resume.** Work is tick-sliced; a stage keeps its progress in the site office, so a server restart or an empty depot only pauses it.

## 5. Function hooks
`function_share` per stage is the fraction of the finished function that is live, so a dam makes power as turbines come online, a lock opens when its gates are fitted, an arcology houses residents as floors finish, a ring and swarm raise transit and W as segments close.
- Power: dam 500 MW out, swarm 50 GW out, to the grid in W through diaithir-units. Draws: arcology 20 MW, elevator 50 MW, ring 2 GW.
- Water: aqueduct carries a water level link; lock flight lets VS2 ships transit.
- Habitat: arcology is a settlement hub node (population from the settlement system).
- Transit: elevator and ring register as Foundry Sky ladder rungs.

## 6. Codex and Panscriptum
`codex_megastructures.tsv` gives one Codex entry per structure with its stage chain and real basis. Panscriptum text and assays are **pending real page text only**; nothing is invented here, the column says so. Names go through the 130-culture pipeline; the English names are the catalogue's.

## 7. Bot tests (real world at spawn, one thing each; bot lanes in memory)
Print a blueprint at a site office of the right Age and refuse at an older one. Deliver 1 pallet to the depot and see the stage ledger count it. Dig stage removes 1 m3 per catalogue rate x time. A place stage with an empty depot pauses and resumes. Aqueduct final stage connects water; dam turbine stage produces W in step with function share; an unpaid crew stops the stage. Server restart mid-stage keeps progress.

## 8. Status and open points
Done: this design, the generator with `--selftest` (five injected faults all caught), the data files. Not done: all Java (site office, depot, stage engine, ghost renderer, function hooks) lives in diaithir-worldsystems and diaithir-ships in diaithir-ports, which is not attached to this thread; no game test has run. Per-stage block art and the Panscriptum text are not started. Next: hand `blueprints.json` to the diaithir-ports thread as the data contract.
