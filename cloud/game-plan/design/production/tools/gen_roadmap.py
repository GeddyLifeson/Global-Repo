"""Generates build-roadmap.csv. Run: python3 tools/gen_roadmap.py (from design/production).
Phases and gates come from schedule_phases.csv (plan Part 4); order and splits are Shardfall choices (4 Oct 2026).
where: cloud = a cloud thread can do it end to end; cloud+pc = cloud writes code/scripts, Marlon's PC compiles, imports or runs them in Unreal;
pc = Unreal editor work on his PC; people = needs testers or players; paid = needs paid people, tools or services."""
import csv, os
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (id, phase, package, produces, depends_on, where, sessions, status, inputs)
R = [
 # P2 pre-production: Gate 2 prototypes (combat, first/third-person switch, Strider, co-op)
 ('B01','P2','Prototype pass 2','Full sound library, real character, better rifle sound, simplify pass','','pc',1,'in progress','Unreal prototype thread'),
 ('B02','P2','Code repo','Private GitHub repo holding the Unreal Source/, Config/ and data CSVs, so cloud threads can commit code the PC pulls','','pc',1,'done: private repo GeddyLifeson/shardfall-game, prototype on main','tech/05-pipeline-tools.md'),
 ('B03','P2','Module skeleton','17 Sf* modules with Build.cs files, Forgeframe plugin and 11 Game Feature plugins (game-plan/unreal/)','B02','cloud',1,'done: compiles on the PC, 104 tables imported (shardfall-game main)','tech/01-code-architecture.md'),
 ('B04','P2','Row structs','GenRowStructs.py plus generated C++ row structs for every table in datatable_map.csv','B03','cloud',1,'done: compiles on the PC, 104 tables imported (shardfall-game main)','tech/datatable_map.csv'),
 ('B05','P2','Data import','Editor Python script that imports all CSVs into DataTables, CurveTables and StringTables','B04','cloud+pc',1,'done: compiles on the PC, 104 tables imported (shardfall-game main)','tech/datatable_map.csv, data/'),
 ('B06','P2','Formula library','SfCore C++ formulas with automation tests checked against the CSV formula tables','B03','cloud',1,'compiles on the PC (shardfall-game main); editor steps and tests pending','actors/derived_formulas.csv, economy_formulas.csv, items/formulas.csv'),
 ('B07','P2','Input assets','Script that builds Enhanced Input actions, contexts and presets from data/input','B03','cloud+pc',1,'compiles on the PC (shardfall-game main); editor steps and tests pending','data/input/'),
 ('B08','P2','Loot and economy simulator','Python simulator: rolls loot tables and runs progression 10,000 times, charts drop rates, Ember and level vs region band','','cloud',1,'done','simulation/sim/ (sim.py, report.html); open items in simulation/sim/findings.csv'),
 ('B09','P2','Localization checker','Python check for text over max_chars, missing STR_ keys and broken tokens','','cloud',1,'done','data/ui/; checks in data/tools/validate.py and writing/tools/check_text.py; open items in b09-text-findings.csv'),
 ('B10','P2','Slice asset sourcing','CC0 or commercially licensed meshes, materials, characters and animations for the Cinderreach slice, logged in CREDITS.csv','','cloud',2,'in progress: chars done in repo main (Quaternius UBC, outfits, UAL1/UAL2; clip map art/anim_ual_map.csv), placeholder meshes for Strider, 3 Hollowed, 2 bosses, 6 props in shardfall-game PR #3 to run on the PC; done once PR #2 is reviewed; env done: 92 CC0 assets, 2.1 GB, downloaded with manifest and CREDITS (unreal/assets/cinderreach/env/)','shardfall-assets.xlsx, art/, levels/cinderreach/'),
 ('B11','P2','GAS core','Attribute sets, status effects and damage execution from the actor tables','B04,B06','cloud+pc',2,'compiles on the PC (shardfall-game main); editor steps and tests pending','actors/attributes.csv, status_effects.csv, player_base_stats.csv'),
 ('B12','P2','Melee prototype','Hit detection, stance and poise, frame data driven by melee_frame_data.csv','B11','cloud+pc',2,'in PR #6 on shardfall-game, awaiting PC compile','items/melee_frame_data.csv, feel/'),
 ('B13','P2','Firearm classes','All 8 firearm classes on the prototype rifle code, with feel presets','B11','cloud+pc',1,'in PR #7 on shardfall-game, awaiting PC compile','items/firearm_classes.csv, feel/'),
 ('B14','P2','Camera switch prototype','First/third-person switch per camera_modes.csv (risk R02)','B01','cloud+pc',1,'later','data/camera/'),
 ('B15','P2','Strider prototype','Rideable Strider mount with placeholder model','B11','cloud+pc',1,'in PR #4 on shardfall-game, awaiting PC compile','tech/01, world/traversal_verbs.csv'),
 ('B16','P2','Co-op prototype','2 to 4 player listen-server co-op with replicated combat','B12,B13','cloud+pc',2,'later','tech/02-online.md, actors/coop_scaling.csv'),
 ('B17','P2','Enemy AI','StateTree AI for 3 archetypes from ai_profiles.csv','B11','cloud+pc',2,'in PR #8 on shardfall-game, awaiting PC compile','actors/ai_profiles.csv, enemies.csv'),
 ('B18','P2','Gate 2 playtest','Feel scores for combat, camera switch, Strider and co-op; melee vs gun parity check (R01)','B12,B13,B14,B15,B16','people',1,'later','playtest_research_plan.md'),
 # P3 vertical slice (Cinderreach)
 ('B19','P3','UI framework','CommonUI screens, HUD and popups from frontend/ and the Screen Gallery, with string tables','B05','cloud+pc',3,'compiles on the PC (shardfall-game main); editor steps and tests pending','frontend/, ui-mockups/, data/ui/'),
 ('B20','P3','Save system','SfSave serialization, versioning and save rules','B03','cloud+pc',1,'compiles on the PC (shardfall-game main); editor steps and tests pending','tech/03, frontend/save_rules.csv'),
 ('B21','P3','Inventory and loot','Items, equipment, loadouts and loot rolls','B05,B11','cloud+pc',2,'in PR #10 on shardfall-game, awaiting PC compile','data/items/'),
 ('B22','P3','Progression','Levels, use-based skill XP, perks and Origins','B11','cloud+pc',2,'in PR #5 on shardfall-game, awaiting PC compile','actors/level_curve.csv, skills.csv, perks.csv'),
 ('B23','P3','Quests and dialogue runtime','Quest state, dialogue playback and world flags','B20','cloud+pc',2,'in PR #9 on shardfall-game, awaiting PC compile','world/quests.csv, writing/, campaign/'),
 ('B24','P3','Cinderreach slice blockout','Editor script that whiteboxes the slice from level nodes and placements','B05','cloud+pc',2,'compiles on the PC (shardfall-game main); editor steps and tests pending','levels/cinderreach/, world/level_nodes.csv, level_placements.csv'),
 ('B25','P3','Spine Keep blockout','Region 1 Citadel whitebox and encounters','B24','cloud+pc',1,'later','levels/cinderreach/02-spine-keep.md'),
 ('B26','P3','Slice boss','First boss with phases and moves from the boss tables','B12,B17','cloud+pc',2,'later','actors/bosses.csv, boss_phases.csv, boss_moves.csv'),
 ('B27','P3','Audio hookup','MetaSounds, music state machine and SFX hook resolver using the 5,709-file library','B05','cloud+pc',2,'compiles on the PC (shardfall-game main); editor steps and tests pending','audio/, audio/samples/full/'),
 ('B28','P3','Slice art and lighting','Kitbash, lighting and VFX pass on the slice with sourced assets','B10,B24','pc',3,'later','art/02-lighting-guide.md, Visual Bible'),
 ('B29','P3','Telemetry and crash reports','Event schema, batching and crash reporting','B03','cloud+pc',1,'compiles on the PC (shardfall-game main); editor steps and tests pending','tech/06'),
 ('B30','P3','Gate 3 slice test','Slice test against its three targets plus cost re-estimate','B19,B21,B22,B23,B25,B26,B27,B28','people',1,'later','playtest_research_plan.md, budget_by_phase.csv'),
 # P4 systems
 ('B31','P4','Weave, Resonances, elements','All Weave abilities, Resonances and element combos','B11','cloud+pc',3,'later','actors/weave_abilities.csv, resonances.csv, element_*'),
 ('B32','P4','Full weapon roster','12 melee and 8 firearm classes, weapon arts, perks, infusions','B12,B13','cloud+pc',3,'later','data/items/'),
 ('B33','P4','Crafting, vendors, economy','Crafting, upgrades, vendors and currencies','B21','cloud+pc',2,'later','items/crafting_recipes.csv, vendors.csv, loops/05-economy.md'),
 ('B34','P4','Factions and world simulation','Reputation, crime and bounty, NPC schedules','B23','cloud+pc',3,'later','actors/factions.csv, simulation/'),
 ('B35','P4','Stealth','Detection, noise and faction stealth rules','B17','cloud+pc',2,'later','systems/stealth_*'),
 ('B36','P4','Vehicles','Vehicles, parts, weapons, handling and hijack','B15','cloud+pc',2,'later','systems/vehicle_*'),
 ('B37','P4','World systems','World Partition, day/night, weather, fast travel, Anchors, Shard-ghost','B20','cloud+pc',3,'later','tech/03'),
 ('B38','P4','Online services','EOS sessions, matchmaking, invasions, 3-player strikes, raids and 3v3 PvP on dedicated servers, backend','B16','cloud+pc',6,'later','tech/02-online.md'),
 ('B39','P4','Server hosting','GameLift fleets and backend hosting','B38','paid',1,'later','tech/02, budget_by_phase.csv'),
 ('B40','P4','Accessibility','Every feature in accessibility_features.csv','B19','cloud+pc',2,'later','accessibility/'),
 ('B41','P4','Character creator','Creator and presets','B19','cloud+pc',2,'later','systems/character_creator.csv, cc_presets.csv'),
 ('B42','P4','Codex, achievements, photo mode','Codex, achievements and photo mode','B19','cloud+pc',1,'later','data/ui/, frontend/photo_mode.csv'),
 ('B43','P4','Companion app','Web companion app against a mock backend, later the real one','B38','cloud',2,'later','companion/'),
 # P5 content (region order from region_schedule.csv)
 ('B44','P5','Region 1 Cinderreach','Full region build, the template for the rest','B30','pc+paid',6,'later','levels/cinderreach/, region_schedule.csv'),
 ('B45','P5','Regions 2 and 3','Saltmere and Thornwood','B44','pc+paid',8,'later','levels/saltmere/, thornwood/'),
 ('B46','P5','Regions 4 to 6','Glasswaste, Rimefall, Hollowdeep','B44','pc+paid',10,'later','levels/glasswaste/, rimefall/, hollowdeep/'),
 ('B47','P5','The Quiet and the Undervault','Orbital act and the Undervault','B44','pc+paid',6,'later','levels/orbital-ring/, undervault/'),
 ('B48','P5','Encounters and quest content','Placed encounters and every quest from quests.csv','B23,B44','cloud+pc',8,'later','world/quests.csv, levels/*/encounters.csv'),
 ('B49','P5','Enemies and bosses','69 enemy types and 44 bosses plus Hush: logic in code, models and animation outsourced','B26','cloud+pc+paid',10,'later','actors/, art/outsource_packages.csv'),
 ('B50','P5','Characters, armor, weapons art','88 characters, 91 armor sets, 289 weapon models to final quality','B10','paid',1,'later','asset_throughput.csv, art/04-outsourcing-spec-pack.md'),
 ('B51','P5','Mocap and animation','Mocap shoot and cleanup for 858 gameplay clips','B12','paid',1,'later','art/mocap_shotlist.csv, anim_sets.csv'),
 ('B52','P5','Cinematics','About 45 minutes of cinematics','B51','paid',1,'later','cinematics/'),
 ('B53','P5','Multiplayer maps','Strikes, PvP maps and raid wings','B38','cloud+pc',4,'later','levels/multiplayer/, world/strikes.csv, pvp_maps.csv'),
 ('B54','P5','Final audio and music','Replace placeholder SFX, music and ambience','B27','paid',1,'later','audio/'),
 ('B55','P5','Voice in 5 languages','VO casting and recording (deferred by Marlon)','B23','paid',1,'later','localization.csv, writing/'),
 ('B56','P5','Text localization','11 more text languages','B09','paid',1,'later','localization.md'),
 # P6 to P9
 ('B57','P6','Alpha','Bug bash to under 200 majors, performance to perf_budgets.csv, 200-tester outside playtest','B44,B45,B46,B47,B48,B49','pc+people',4,'later','qa_cert.md, tech/perf_budgets.csv'),
 ('B58','P7','Beta and certification','Platform devkits, TRC/XR/Steam passes, age ratings, 50,000-player closed beta','B57','paid',1,'later','qa_cert.md, ratings_legal.md'),
 ('B59','P8','Launch','Store pages, marketing beats, day-one patch','B58','paid',1,'later','marketing_launch.md'),
 ('B60','P9','Live service','Seasons every 3 months, Forgeframe, yearly expansion','B59','cloud+pc+paid',1,'later','liveops_calendar.csv, forgeframe/'),
]
with open(os.path.join(OUT, 'build-roadmap.csv'), 'w', newline='') as f:
    c = csv.writer(f)
    c.writerow(['id','phase','package','produces','depends_on','where','sessions','status','inputs'])
    c.writerows(R)
