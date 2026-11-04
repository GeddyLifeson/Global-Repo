# Diaithir / Shardfall V1 feature audit (read-only), 2026-11-04

Pack audited: /home/user/geddylifeson/diaithir-ports @ da34c034 "Wave15" (37 jars + 52 packwiz downloads = 89 files in mods/; FINISH_PLAN had ~180 at 11-03 22:30).
Status words: CLIENT = a real game client ran it (see caveat), HEADLESS = server/cloud/unit tests only, UNTESTED = code exists (in pack or in a PR), never run, DESIGN = plan/data/catalogue only, MISSING = nothing found.
Caveats that apply to every CLIENT row: the only client runs are the cloud bot (Xvfb, light per-module packs, PR-head jars). NO full-pack client join has ever passed. The first one (11-03) crashed 13 s in on the ships jar (FINISH_PLAN s3). pack-v1 (408 jars, 10-28) did join, but is not this pack.
I could not query GitHub (gh returned nothing), so "merged or open" comes from MERGE_ORDER.csv (237 rows, no status column), FINISH_PLAN (90 open PRs, 87 drafts, 11-03) and jar contents. "In pack" below means I found the class/asset in a jar here.
The master plan artifact (57d08605...) is the Unreal Engine Shardfall production plan (6-game teardown, 54-month phases). It never mentions Diaithir, Ages, Panscriptum or the pack. The V1 feature list therefore comes from the plans/ files, not from that artifact. /home/user/shardfall-game was not audited.

## Table

| Feature | Status | Evidence | Blocker |
|---|---|---|---|
| Age I (content, tech gate, Age Turn) | HEADLESS | V1_TEST_CHECKLIST s2,s9: acceptance paths A/B PASS and gate reload at Age Turn PASS (cloud, 10-22); pack-v1 client join PASS 10-28 (V1_STATUS). Pack has diaithir-ages .7 but kubejs/data/diaithir_ages/ages holds only _global/culture_starts.json; Age content files not found in the repo tree | Gates for a real player (10c) never tested; content delivery path unverified |
| Ages II-VII | HEADLESS | kubejs/data/diaithir_tech/tech_tree.json (9 eras I..VIII+RODOS), tech_items.json 7601 items; gate to Age II verified cloud 10-22 | No client run; balance audit Global #30 unmerged |
| Age VIII (Future) + Rodos | UNTESTED | ui_ages viii/rodos .pw.toml; V1_STATUS: "need the PC's canon/eras.csv"; icons RPG #263 unmerged; Ascendant tiers sit at VII/Rodos | eras.csv import; no test |
| Culture picker screen | UNTESTED | CreatorScreen in diaithir-ages .7 + platform suite; V1_STATUS "picker screen NOT verified (PC must test)"; no bot report covers it | PC rule (no client until pack small); Great Zimbabwe start RPG #262 unmerged |
| Culture start spawn (131 starts) | HEADLESS | culture_start.js, culture_spawns.json, culture_starts.json; spawn_guard.js; cloud only | Real spawn at Creag Ruadh never confirmed (join timed out on chunk gen) |
| Safe landing | CLIENT | V1_STATUS: fresh survival join at y=231 ended on surface (pack-v1, 10-28); safe_landing.js in pack | Not re-run on this pack |
| Spawn and ore bands on production | UNTESTED | V1_PUNCHLIST: "UNVERIFIED", RPG #79 open, not checked since 10-20 | PC job |
| Planets (216) data | UNTESTED | worldgen suite: 216 dimension_type, planet_stems, tags, colony icons, 3037 biomes; kubejs/data/diaithir_worlds/planets has only 8 files | No client/server proof the 216 dims load together; bot rite test needed a test jar because no delivered jar had the #diaithir_planets biome tags (bosses #202) |
| Colony picker (/colony list,info,found,where) | CLIENT | bot 11-03 colony_run.txt: 216 planets listed, found + where PASS (chat in client) | The restart-persistence run failed (server did not start); GUI picker screen not tested |
| Panscriptum == modpack parity | DESIGN | PANSCRIPTUM_INTEGRATION s1: pack to Library 118 ids left; "Library to pack: not yet" (699,649 entries). Pack folded 546 mods to 89 files with no parity check | Mapping job and per-entry forms not built |
| Codex (Ages/boss/tech screens) | UNTESTED | CodexScreen, TechTreeScreen, codex/bosses.json in diaithir-ages .7 | No bot or PC test |
| Codex Library tab (700k entries) | UNTESTED | LibraryStore class in ages jar; sqlite store built (CODEX_LIBRARY_STORE s1); RPG #269 (wave 8) unmerged | Merge, ship 70 MB zip, client check |
| Civilopedia | MISSING | grep of all jars, plans and PR titles: no hit | Not planned in any PR |
| Atlas map | UNTESTED | Antique Atlas + Surveyor jarred in worldgen suite (third party); Diathiris "Atlas" repo is separate | Never opened in a client |
| Claims, Look-At box, claims map, waypoints | CLIENT | bot 11-03: /claim map, Look-At block/waypoint/"Claimed by"/mob health PASS | Light pack |
| Connected textures | CLIENT | bot retest 11-03: ports #184 jar PASS | Light pack |
| Economy core (Lightman's Currency, prices, company) | HEADLESS | V1_STATUS: market chain, /company found/fund/line cloud-tested; LC jar in pack; config/prices.json etc. | borrow/repay retest queued; no client |
| Trade screens | UNTESTED | lane3 report: NOT TESTABLE, 3 bugs: village_guard has no renderer (NPE), PackVersionCheck kicks unversioned clients, TradeScreens sends empty ItemStack (disconnect). #226 claims some fixes | Full pack needed; fixes unverified |
| NPC wages, payroll, strikes | UNTESTED | RPG #259 (wave 3) unmerged; bot wages/wt_run.txt hit KubeJS errors and was inconclusive | Merge; no result |
| Vendors Age I-II fill, stations layer | UNTESTED | ports #244, Global #34, RPG #257-#261 unmerged | Conflicts with wave 7 |
| Upgrades core (modules, slots, planner, quality) | HEADLESS | platform suite: net/diaithir/upgrades (Resolver, Planner, UpgradeMenu, UpgradeScreen, Quality); PR #166 fake-player selftest | Menu/screen never opened in client; "every working block takes modules" unproven |
| Upgrade beacon (animated render) | CLIENT | lane3 #209: 3 beacons render and sway, no errors | Light pack |
| Wiretech circuit network | UNTESTED | net/diaithir/wiretech (46 classes) + assets in platform suite; PR #214 "ready" | No test of any kind in reports |
| Foundry / stations / research packs | UNTESTED | diaithirfoundry classes in rewrites jar; bot: "Foundry is not formed" only | Machines never built in a client |
| Units (SI display) | HEADLESS | diaithir-units jarjar'd in rewrites jar; PR #257 22 tests | No in-game text audit |
| Storage and logistics (portable, router) | CLIENT | bot: portable slots PASS after #123; router GUI PASS (11-03 20:45) | Linked/foundry screens not reached |
| Combat ports (sentry, laser, relics, classes, Tool Belt) | CLIENT | bot 11-04: #313, #316, #309 PASS; #302 PASS at 9cb22b2a66 after 2 crashes | #317 Better Animations has no renderer; PR heads, merge state unknown |
| Armour models, boss looks | CLIENT | bot: 9 armour sets, 26 bosses textured | Light pack |
| Bosses, boss rush, 9 Ascendant | CLIENT | bossrush_real_client.png, no disconnect; ShardfallGateBlock/AscendantAltarBlock in pack | Needs 3 required kills before rush |
| Rites (Spell Engine + druidry) | CLIENT | rite_report.json: Venaerys rite plays end to end | One rite only; needs overworld-biomes jar for tags |
| Age Wardens (7 mini-bosses, rite chains, evolving altar) | UNTESTED | PRs #242 #250 #253; no AgeWarden class in pack | Unmerged |
| Shardfall Gate win ceremony | UNTESTED | Gate, GateTest in bosses jar (unit tests); #167, #254 pipeline unmerged | No client run |
| Ascendant biomes + rite sites | UNTESTED | PRs #164 #264 unmerged | Merge |
| NPCs (Easy NPC, guards, villager care) | UNTESTED | easy_npc_bundle pw.toml; worldsys villageguards/villagercare classes | Guard renderer crash (see trade screens) |
| Quests (clean-room questbook engine) | UNTESTED | worldsys/questbook classes (9); #279, #246 | Codex Quests tab never opened |
| Library dimension, named chests, Library to content | UNTESTED | FINISH_PLAN: "client Library tab, named chests" left; RPG #250 #254; thread 5Nob working | Rites thread unfinished |
| Realms (Undergarden, Backwoods, Bumblezone, Aether II, Aerial Hell) | UNTESTED | wave15 puts them in worldgen suite (aether_ii, aerialhell data); FINISH_PLAN: boss rituals, creature models, portal activation "listed open" | Consolidation, no client |
| Magic Age V/VI (alchemy, glyph school, Theurgy, Roots) | UNTESTED | Theurgy in ritual-enchant jar; PRs #239 #266 RPG #264 unmerged; thread still working | Not finished |
| Farm and canning (Age V canning, reaper, Fordson, farm equipment 35 machines) | UNTESTED | farmkitchen classes in realms suite; PRs #275 #195 #338 unmerged; canning not in pack | Thread working |
| Munitions (Ages I-VIII chains, ammo containers) | DESIGN | MUNITIONS.md "draft 1"; #193 "data only", #211 items PR open; no munitions classes in pack | Items/stations unmerged |
| Gear catalogs (everyday objects 460, building materials, historical weapons) | UNTESTED | PRs #185 #213 #245 #182 #203 #328 #331 | Merge |
| Hostile encounters, Global Events (meteors, blood moon) | UNTESTED | PRs #111 #113 #134 #327 | Duplicate decisions made 22:45; merge |
| Vehicles: mount and drive (cars, tank) | CLIENT | bot 11-04: tank mount/drive/fuel PASS; ford_f1 mount/drive/steer PASS on PR jars #225 #345 #221 | Fixes are in unmerged PRs; pack jar still has defects found 11-03 (no click boxes, no engine, magenta icons) unless those PRs are in; IV panel/engine start via GUI not possible in bot |
| Tank gun fire | CLIENT | tank_fire26: `/diaithirvehicle fire 8` kills villagers (log). Space-key fire FAIL (no shot), no visible muzzle/impact | Fire bind; visuals |
| Vehicle cargo bays (#340) | UNTESTED | bot cargo2-6: load/status work, tank deck load hidden inside hull, clear bug fixed later; n345 build: /diaithircargo "Incorrect argument", no VehicleCarriers class | Regression in latest jar; ships cargo #341 never tested |
| Rail wagon cargo (#339) | CLIENT | CARGO.md: container draws on flatcar after 643c29b8b7 | Curves, moving wagons unchecked |
| Trains: gauges, rails, signals | HEADLESS | TRAINS.md: speeds match GAUGES.md in server run; pack has steel/bronze/fast/station rails, signal, coupling chain but no narrow rail (so #228 not in pack) | Payload and crew rules unenforced (Gauge.payload unused, crew never read); wrong-gauge placement refusal needs a client |
| Locomotives, yards, cranes, timetables | UNTESTED | PRs #206 #220 #235 #251 #336 | Merge, client |
| Ships (Archimedes + VS2 + Eureka) | HEADLESS | VS 2.5.0-diaithir.11 soak (10-27, no VS errors); VS/Archimedes/Eureka in extras suite | First full-pack join crashed on ships jar; swap to .7/.8 pending (FINISH_PLAN) |
| Keelwright (part-driven ships, yards) | DESIGN | SHIPBUILDING.md; yard PRs #186 #191 #194 #216 #249 #293; no keelwright/vs_yard class in pack | Heartcore/Conduit/ship power grid, HP and mass table marked GAP in the plan |
| Aircraft | UNTESTED | PRs #188 #248; aircraft tuning class in worldsys | Never flown |
| Megamachines and megastructures | DESIGN | MEGAMACHINES.md, Global #27 #33 catalogue/validator; PRs #224 #265 #286 open; nothing in pack | Code unmerged, nothing run |
| Autonomy (crewed/autopilot vehicles) | DESIGN | INTEGRATION_MATRIX bridge S/W; TRAINS.md: Autonomy.status counts any rider as CREWED, wages never charged; no Autonomy class in pack | No implementation to test |
| Entity animation (HUD, skin layers, NEA) | CLIENT | entity-animation 1.0.2 boots and joins with 10 client jars (11-03 21:05) | Light pack |
| Fauna animation and textures | UNTESTED | lane3 #207: animations PASS only with textures; capitals in species id crash client; plan fallback textures missing (magenta) | Fix in #226 unverified |
| Gun, sword, vehicle, machine animation (diaithir-animation) | UNTESTED | #165 #171 #187 #222 #337; lane3 #222: hold/aim PASS, fire/reload/sword NOT CONFIRMED; no module in pack | Merge; clip check |
| Keybinds (no conflicts) | MISSING | No keybinds.txt or options.txt in the repo tree although the master CLAUDE.md says they ship as overrides; #218 and #322 unmerged; Tool Belt R collides | Merge + updater test |
| OpenComputers | MISSING | Decided out of V1 (FINISH_PLAN s8.6); #169 step 1 compile only, #223 WIP. Pack has own diaithir-computing (cable, disk drive, reckoner, turtle) untested | Out of V1 by decision |
| World migration (migrate_world.py, id migrations) | UNTESTED | diaithir-migrate source in repo; wave 6/7 held "until Marlon"; may be moot (fresh world) | Coordinator to confirm |
| Full-pack client join and V1 test pass | MISSING | FINISH_PLAN: first join crashed; punchlist items 3-5 open; rule "no PC client until 20-40 jars" (11-03 18:55) | Pack still 89 files; PC rule |
| Clean-room compile of all merged code | HEADLESS | COMPILE_STATUS.csv: 110 OK, 2 FAIL, 14 N/A (per FINISH_PLAN) | Fix 2 fails |

## Counts
61 rows: CLIENT 14, HEADLESS 9, UNTESTED 29, DESIGN 5, MISSING 4. (No row is 'built and fully tested in the full pack': CLIENT = light-pack bot only.)

## Planned items with no PR or code found anywhere
1. Civilopedia (no PR, no class, no plan file).
2. Autonomy controller: only a stub status method in the carts PR; no PR for crews, wages for crew, autopilot.
3. Enforcement of narrow-gauge payload (0.4) and steam crew (2): found unenforced (TRAINS.md), no fix PR named.
4. Keelwright power layer (Heartcore, Conduit, Cells) and per-block HP and mass table: SHIPBUILDING.md status GAP.
5. Panscriptum "Library to pack" forms for the ~699k entries beyond the Codex tab (PANSCRIPTUM_INTEGRATION s1: "not yet") and any parity check tool.
6. Future (VIII) and Rodos era rows from the PC's canon/eras.csv (V1_STATUS).
7. Off Grid compat test (DiaithirRPG #232 repo never attached) and Offgrid inspect.
8. OpenComputers beyond loader compile (explicitly out of V1).
Not checked: whether Munitions, Megastructure and canning have code beyond the PR titles; I read no PR diffs.

## Biggest risks, in order
1. No full-pack client join has ever passed; every CLIENT row above is a light pack. Defects found in light packs so far: vehicles unmountable, default parts never spawned, magenta icons, router GUI empty, entity-animation boot crash x2, Tool Belt enum crash, cargo regression, trade-screen disconnects. Expect the same density on the rest.
2. 87 of 90 open PRs were drafts; features marked UNTESTED/PR-only are not in the pack until merged.
3. Defects fixed only in unmerged PR jars (vehicles #225/#345/#221) may still exist in the pack's own vehicle jars.
