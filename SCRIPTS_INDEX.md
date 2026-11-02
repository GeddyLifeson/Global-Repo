# Global script catalogue

Every script, one stable ID. Borrow by ID; copies live in this repo under `<device>/<path>` when marked yes. Source of truth for IDs: `ids.tsv`. Rebuild with S0002 (`python3 build_index.py <repo>`).

Devices: `cloud` = /mnt/project-files (shared folder), `pc` = Fountain-of-Lateralus-Rex, `laptop` = MSI.

Run hints: .py `python3 <file>` (PC `py`), .ps1 via a hidden launcher (never a visible window), .sh `bash`, .js/.mjs `node`. Norton deletes .bat, so avoid it.

| ID | Device | Path | What | Copy |
|---|---|---|---|---|
| S0001 | global | `scan_cloud.py` | S0001 scans /mnt/project-files, copies scripts scrubbed, writes cloud_inventory.tsv: python3 -I scan_cloud.py <repo> | yes |
| S0002 | global | `build_index.py` | S0002 assigns stable IDs and renders SCRIPTS_INDEX.md: python3 -I build_index.py <repo> | yes |
| S0003 | cloud | `IF_reassemble.py` | Rejoins the Industrial Factory resource pack zips from their 8 MB parts and checks every sha256. | yes |
| S0004 | cloud | `animals-art/ao_bake.py` | Bake ambient occlusion onto an Untamed Wilds model's own UV layout (headless Blender, bpy 5.2). | yes |
| S0005 | cloud | `animals-art/build_animals.py` | 16x sources (final UV layout) -> shared Factorio style -> realistic eyes -> 32x textures.""" | yes |
| S0006 | cloud | `animals-art/build_fresh.py` | All 35 skins: Blender AO bake + fresh Factorio-style paint.  python3 build_fresh.py BLENDER_PYTHON ENTITIES_DIR OUT [SCALE]""" | yes |
| S0007 | cloud | `animals-art/build_page.py` | R = '/home/user/geddylifeson/diaithir-ports/src/main/resources' | yes |
| S0008 | cloud | `animals-art/eye_alloc.py` | Enlarge each model's eye planes for PureBD cartoon eyes and give them free UV space.""" | yes |
| S0009 | cloud | `animals-art/eyes.py` | Paint eyes into each eye plane's UV faces (32x texture): 'cartoon' (PureBD) or 'real' (small dark eye, rest clear).""" | yes |
| S0010 | cloud | `animals-art/paint.py` | Paint an Untamed Wilds animal skin fresh, Factorio style, at SCALE x its texture size. | yes |
| S0011 | cloud | `animals-art/parse.py` | Parse Untamed Wilds code-built models into JSON for a three.js viewer.""" | yes |
| S0012 | cloud | `animals-art/rebake.py` | Re-lay a model texture after its boxes moved or changed size: every face of the | yes |
| S0013 | cloud | `animals-art/shot.mjs` | const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-u | yes |
| S0014 | cloud | `animals-art/vanilla/auto.py` | The long tail of mod mobs: each skin is matched to its model automatically, the locked creature method paints it. | yes |
| S0015 | cloud | `animals-art/vanilla/batch3.py` | Preview table for the Bestiary and Wyrmlore page (build_page.py --table=batch3).""" | yes |
| S0016 | cloud | `animals-art/vanilla/build_page.py` | Preview page for a batch of vanilla mobs: python3 build_page.py LAYERS_JSON VANILLA_TEX PAINTED_DIR OUT.html TITLE GROUP mob ...""" | yes |
| S0017 | cloud | `animals-art/vanilla/convert.py` | Turn other model formats into the same posed-polygon layers ExportLayers.java writes, so vanilla.py paints them. | yes |
| S0018 | cloud | `animals-art/vanilla/fixups.py` | Skins auto.py could not match by coverage, given their real models: MCA profession outfits (the player body layout, | yes |
| S0019 | cloud | `animals-art/vanilla/geo.py` | GeckoLib creatures (Occultism spirits, Neovitae daemons): convert.py geo layers, each painted on its own same-named skin. | yes |
| S0020 | cloud | `animals-art/vanilla/lane6.py` | Creature variants left over after the main batches (the entity lane's list): baby, tame and angry skins, villager biome and | yes |
| S0021 | cloud | `animals-art/vanilla/lane6_page.py` | Preview page for lane6.py: python3 lane6_page.py LAYERS_JSON TEX_ROOT PAINTED LIST_JSON SIBLINGS_JSON OUT.html""" | yes |
| S0022 | cloud | `animals-art/vanilla/mods.py` | Mod mobs exported by ExportLayers.java from the mod's own jar (Twilight Forest, Aether II), the locked creature method. | yes |
| S0023 | cloud | `animals-art/vanilla/poly_ao.py` | Bake ambient occlusion onto a vanilla model layer's own UV layout (headless Blender, bpy 5.2). | yes |
| S0024 | cloud | `animals-art/vanilla/tail_page.py` | Preview page for the long tail (auto.py, geo.py, the Wyrmlore dread): python3 tail_page.py S_DIR OUT.html""" | yes |
| S0025 | cloud | `animals-art/vanilla/vanilla.py` | Paint vanilla mob skins fresh at 64x (4x), the locked Diaithir creature method, from ExportLayers.java polygons. | yes |
| S0026 | cloud | `animals-art/vanilla/wyrm.py` | Wyrmlore (Ice and Fire CE port) creatures, the locked Diaithir creature method. | yes |
| S0027 | cloud | `animals-fossils/validate.py` | python3 validate.py catalogue/<file>.psv [more]  -> prints errors, exit 1 if any.""" | yes |
| S0028 | cloud | `animals-fossils/validate_coat.py` | python3 validate_coat.py <group>  (checks catalogue/coat_<group>.psv against <group>.psv ids)""" | yes |
| S0029 | cloud | `audit/pc/start_server.ps1` | Start the Diaithir production server detached, then its watchdog. | yes |
| S0030 | cloud | `audit_ages_bridge.js` | Mirrors the engine state KubeJS needs (current Age, story flags) and keeps it across restarts. | yes |
| S0031 | cloud | `audit_tech_ages_data_head2k.js` | Written by tools/age1/install.py from content/tech_ages.json; edit that file. | yes |
| S0032 | cloud | `audits/consolidation-2026-10-21/delete_branches.sh` | Branch cleanup from the 2026-10-21 consolidation. Run from a DiaithirRPG clone after Marlon approves. | yes |
| S0033 | cloud | `brewing-drop/bridge/a_data.js` | GENERATED by tools/drinks/gen_data.py from content/drinks/drinks.json. Do not edit; rerun it. | yes |
| S0034 | cloud | `brewing-drop/bridge/brewing.js` | Brewing: six stations turn farm goods into drinks over game time. Data comes from data.js (tools/drinks/gen_data.py). | yes |
| S0035 | cloud | `brewing-drop/bridge/drinks_scripts/a_data.js` | GENERATED by tools/drinks/gen_data.py from content/drinks/drinks.json. Do not edit; rerun it. | yes |
| S0036 | cloud | `brewing-drop/bridge/drinks_scripts/brewing.js` | Brewing: six stations turn farm goods into drinks over game time. Data comes from data.js (tools/drinks/gen_data.py). | yes |
| S0037 | cloud | `brewing-drop/bridge/drinks_scripts/effects.js` | Drinking: each drink gives a small gift of its kind, and strength builds a drunkenness that wears off with time. | yes |
| S0038 | cloud | `brewing-drop/bridge/effects.js` | Drinking: each drink gives a small gift of its kind, and strength builds a drunkenness that wears off with time. | yes |
| S0039 | cloud | `brewing-drop/bridge/gen_create_bridge.py` | Make Create mixing recipes (heated basin) from diaithirbrewing recipe JSON. | yes |
| S0040 | cloud | `brewing-drop/bridge/gen_create_bridge_kubejs.mjs` | Make Create mixing recipes (heated basin) from the drinks KubeJS scripts, running their real code. | yes |
| S0041 | cloud | `builds/food-server-drop/jar_reassemble.py` | Rejoins a jar from its 8 MB parts and checks every sha256. | yes |
| S0042 | cloud | `builds/pack-sweep-3/kubejs/server_scripts/speuran/age_gate.js` | Age gate for the far worlds of na Speuran (datapack diaithir_worlds). Stellaris has no per-planet rocket | yes |
| S0043 | cloud | `builds/pack-sweep/client-test/client.sh` | client.sh CLIENTDIR OUTDIR [maxsec]: boot the client under Xvfb, quick-play into saves/world, screenshots + jstack on stall | yes |
| S0044 | cloud | `builds/pack-sweep/client-test/qboot.sh` | qboot.sh SRV LOG: boot to Done, wait 20 s, stop | yes |
| S0045 | cloud | `builds/pack-sweep/client-test/testall.sh` | per batch: fresh server (boot = new world), client boot + quick-play join on that world; bench for 3 and 4 | yes |
| S0046 | cloud | `builds/pack-update-1/tests/harness/client.sh` | client.sh CLIENTDIR OUTDIR [maxsec]: boot the client under Xvfb, quick-play into saves/world, screenshots + jstack on stall | yes |
| S0047 | cloud | `builds/pack-update-1/tests/harness/client2.sh` | client.sh CLIENTDIR OUTDIR [maxsec]: boot the client under Xvfb, quick-play into saves/world, screenshots + jstack on stall | yes |
| S0048 | cloud | `builds/pack-update-1/tests/harness/client3.sh` | client.sh CLIENTDIR OUTDIR [maxsec]: boot the client under Xvfb, quick-play into saves/world, screenshots + jstack on stall | yes |
| S0049 | cloud | `builds/pack-update-1/tests/harness/hold.sh` | hold.sh CLIENTDIR: start the client under Xvfb :91 and leave it running (killed by hand) | yes |
| S0050 | cloud | `builds/pack-update-1/tests/harness/qboot.sh` | qboot.sh SRV LOG: boot to Done, wait 20 s, stop | yes |
| S0051 | cloud | `builds/pack-update-2/tests/harness/cl.sh` | cl.sh CLIENTDIR OUTDIR PORT : start the client (multiplayer quick play) under Xvfb in the background; returns at once | yes |
| S0052 | cloud | `builds/pack-update-2/tests/harness/cl_sp.sh` | cl_sp.sh CLIENTDIR OUTDIR : singleplayer quick play into saves/world | yes |
| S0053 | cloud | `builds/pack-update-2/tests/harness/cmd.sh` | cmd.sh LOG "command" | yes |
| S0054 | cloud | `builds/pack-update-2/tests/harness/qboot.sh` | qboot.sh SRV LOG: boot to Done, wait 20 s, stop | yes |
| S0055 | cloud | `builds/pack-update-2/tests/harness/shot.sh` | shot.sh FILE.png | yes |
| S0056 | cloud | `builds/pack-update-2/tests/harness/srvup.sh` | srvup.sh SRV LOG : boot the server and leave it running; commands go to LOG.in | yes |
| S0057 | cloud | `builds/pack-update-2/tests/harness/stboot.sh` | stboot.sh SRV LOG "cmd1;cmd2" WAITPATTERN: boot, run console commands, wait for pattern, stop | yes |
| S0058 | cloud | `builds/pack-update-3/tests/harness/cl_sp.sh` | cl_srv.sh CLIENTDIR OUTDIR: headless client joins 127.0.0.1:25565 | yes |
| S0059 | cloud | `builds/pack-update-3/tests/harness/cmd.sh` | cmd.sh LOG "command" | yes |
| S0060 | cloud | `builds/pack-update-3/tests/harness/shot.sh` | shot.sh FILE.png | yes |
| S0061 | cloud | `builds/pack-update-3/tests/harness/srvup.sh` | srvup.sh SRV LOG : boot the server and leave it running; commands go to LOG.in | yes |
| S0062 | cloud | `builds/pack-update-4/tests/harness/cl_sp.sh` | cl_srv.sh CLIENTDIR OUTDIR: headless client joins 127.0.0.1:25565 | yes |
| S0063 | cloud | `builds/pack-update-4/tests/harness/cmd.sh` | cmd.sh LOG "command" | yes |
| S0064 | cloud | `builds/pack-update-4/tests/harness/shot.sh` | shot.sh FILE.png | yes |
| S0065 | cloud | `builds/pack-update-4/tests/harness/srvup.sh` | srvup.sh SRV LOG : boot the server and leave it running; commands go to LOG.in | yes |
| S0066 | cloud | `builds/perf-pass/apply_perf.ps1` | Diaithir perf pass 1: run once with the server STOPPED (or it applies at next restart). Backs up every file it edits to *.bak-perf. | yes |
| S0067 | cloud | `builds/perf-pass/apply_perf2.ps1` | Diaithir perf pass 2 (includes pass 1; safe to rerun). Stops the server, applies, STARTS it, verifies the port. Backs up every file it edits | yes |
| S0068 | cloud | `builds/reset-overnight/Reset Diaithir Server v2.bat` | rem Reset Diaithir Server: backup, fresh Age I world, spawn at Creag Ruadh (on land), boot, check. One double-click. | yes |
| S0069 | cloud | `builds/reset-overnight/fixspawn/Fix Spawn.bat` | rem Sets world spawn at Creag Ruadh on the running server. Needs the server up. | yes |
| S0070 | cloud | `builds/reset-overnight/fixspawn/fix_spawn.py` | Set the world spawn and border centre at Creag Ruadh on the running server (reads rcon settings from server.properties).""" | yes |
| S0071 | cloud | `builds/reset-overnight/fixspawn/rcon.py` | Minimal Minecraft RCON client (stdlib only) plus parsing of the fork's PROBE/SCAN lines.""" | yes |
| S0072 | cloud | `builds/reset-overnight/livefix/Live Fix.bat` | rem Fixes the world-generation crash (stale ore modifiers), restarts the server and sets spawn. Keeps the current world. | yes |
| S0073 | cloud | `builds/reset-overnight/livefix/live_fix.py` | Live fix for the running Diaithir server: remove the 7 stale per-coal biome modifiers (they duplicate deep_mod_ores and cause | yes |
| S0074 | cloud | `builds/reset-overnight/livefix/rcon.py` | Minimal Minecraft RCON client (stdlib only) plus parsing of the fork's PROBE/SCAN lines.""" | yes |
| S0075 | cloud | `builds/reset-overnight/livefix/spawn_once.js` | One-shot: players who joined before the spawn fix (old Tellus default) are moved to Creag Ruadh on their next login. | yes |
| S0076 | cloud | `builds/reset-overnight/livefix/start_server.ps1` | Start the Diaithir production server detached, then its watchdog. | yes |
| S0077 | cloud | `builds/reset-overnight/rescue/Rescue.bat` | python -I "%~dp0rescue.py" | yes |
| S0078 | cloud | `builds/reset-overnight/rescue/rcon.py` | Minimal Minecraft RCON client (stdlib only) plus parsing of the fork's PROBE/SCAN lines.""" | yes |
| S0079 | cloud | `builds/reset-overnight/rescue/rescue.py` | Rescue players who fell out of the world: build a stone platform at the Creag Ruadh spawn, move everyone online onto it, set world spawn, | yes |
| S0080 | cloud | `builds/spawn-fix/safety.js` | ﻿// Server rules (/rules, shown once on first join) and the first-boot claim that keeps the land round spawn | yes |
| S0081 | cloud | `compute/jobs/caves_biomes/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0082 | cloud | `compute/jobs/caves_mobs/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0083 | cloud | `compute/jobs/caves_structures/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0084 | cloud | `compute/jobs/classes_library/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0085 | cloud | `compute/jobs/classes_lore/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0086 | cloud | `compute/jobs/combat_lore/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0087 | cloud | `compute/jobs/combat_lore_retry/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0088 | cloud | `compute/jobs/combat_lore_retry2/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0089 | cloud | `compute/jobs/diaithir-bosses_lore/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0090 | cloud | `compute/jobs/diaithir-bosses_lore_retry/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0091 | cloud | `compute/jobs/diaithir-bosses_lore_retry2/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0092 | cloud | `compute/jobs/diaithir-tanning_library/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0093 | cloud | `compute/jobs/gear_crossmod_names-retry/merge.py` | d = pathlib.Path(__file__).parent | yes |
| S0094 | cloud | `compute/jobs/gear_crossmod_names/merge.py` | d = pathlib.Path(__file__).parent | yes |
| S0095 | cloud | `compute/jobs/gear_lore/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0096 | cloud | `compute/jobs/gear_lore_retry/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0097 | cloud | `compute/jobs/gear_lore_retry2/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0098 | cloud | `compute/jobs/relics_lore/merge.py` | d = pathlib.Path(__file__).parent | yes |
| S0099 | cloud | `compute/jobs/relics_lore_retry/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0100 | cloud | `compute/jobs/relics_lore_retry2/merge.py` | d=pathlib.Path(__file__).parent | yes |
| S0101 | cloud | `diaithiris-archaic/tools/archaic.py` | Diaithiris archaic layer: regular sound-change rules run backwards from modern Goidelic spelling. | yes |
| S0102 | cloud | `diaithiris-archaic/tools/build.py` | sys.path.insert(0,'/tmp/claude-0/w') | yes |
| S0103 | cloud | `diaithiris-archaic/tools/check_unique.py` | python3 -I check_unique.py DIR : every tech name in TECH_NAMES_CORE.json + TECH_NAMES_MODS.json must be unique.""" | yes |
| S0104 | cloud | `diaithiris-archaic/tools/g2p.py` | Reconstructed pronunciation for archaic Diaithiris spelling (rules documented in GRAMMAR_ARCHAIC.md).""" | yes |
| S0105 | cloud | `diaithiris-archaic/tools/render.py` | def line(x): | yes |
| S0106 | cloud | `earth_maps/biomes_by_age/build.py` | Renders the per-slice class grids for the Biomes By Age page. Run: python3 -I build.py  (needs numpy, Pillow) | yes |
| S0107 | cloud | `earth_maps/biomes_by_age/page.py` | sys.path.insert(0, '/tmp/claude-0/bm') | yes |
| S0108 | cloud | `earth_maps/biomes_by_age/pal.py` | 0: ("Ocean", "#bcd6e2"), | yes |
| S0109 | cloud | `earth_maps/biomes_by_age/stage2/build2.py` | Stage 2 of the Biomes By Age page: HYDE slices for Ages IV-VII, dated lakes, crust rebound, a Koppen-Geiger Future. | yes |
| S0110 | cloud | `earth_maps/biomes_by_age/stage2/page2.py` | sys.path.insert(0, '/tmp/claude-0/bm2') | yes |
| S0111 | cloud | `earth_maps/biomes_by_age/stage2/pal.py` | 0: ("Ocean", "#bcd6e2"), | yes |
| S0112 | cloud | `earth_maps/biomes_by_age/stage2/patch.py` | t = open('/tmp/claude-0/bm2/template.html').read() | yes |
| S0113 | cloud | `earth_maps/biomes_by_age/stage3/build3.py` | B2 = '/tmp/claude-0/bm2/'; B3 = '/tmp/claude-0/bm3/' | yes |
| S0114 | cloud | `earth_maps/biomes_by_age/stage3/page3.py` | sys.path.insert(0, '/tmp/claude-0/bm2') | yes |
| S0115 | cloud | `earth_maps/biomes_by_age/stage3/patch3.py` | t = open('/tmp/claude-0/bm2/template2.html').read() | yes |
| S0116 | cloud | `earth_maps/biomes_by_age/stage3/run_future.py` | Palette run for the modelled Future: BIOME4 class and climate come from the 0.5 degree climate-analog rasters (build2.analog), sea +0.6 m."" | yes |
| S0117 | cloud | `earth_maps/biomes_by_age/stage3/run_slices.py` | Runs the Age I pack-biome palette engine (world/earth/biome/palette, the Python mirror of EraPalette) once per dated slice. | yes |
| S0118 | cloud | `enable_factory_pack.ps1` | Enables the Industrial Factory resource pack zips in the Diaithir client's options.txt. | yes |
| S0119 | cloud | `export_age_palettes.py` | Writes docs/ui/age_palettes.json: each Age's colours as hex, for every screen that draws its own colours in code | yes |
| S0120 | cloud | `game-plan/antislop/skills/antislop-human/contrast-check.py` | WCAG 2.x contrast checker, home of the antislop-human contrast checker. | yes |
| S0121 | cloud | `game-plan/antislop/skills/antislop-human/contrast-mcp.py` | Minimal MCP stdio server exposing the antislop contrast checker as a tool. | yes |
| S0122 | cloud | `game-plan/bible/check.py` | Check finished work against the Shardfall Bible (bible/BIBLE.md). | yes |
| S0123 | cloud | `game-plan/data/actors/tools/common.py` | OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') | yes |
| S0124 | cloud | `game-plan/data/actors/tools/gen_bosses.py` | CLS={'Shard-bearer':(3.0,120,1.0,'A031'),'Citadel':(2.4,100,0.6,'A032'),'Field':(1.6,90,0.4,'A033'),'Site':(1.3,80,0.1,'A034'),'Raid':(30.0, | yes |
| S0125 | cloud | `game-plan/data/actors/tools/gen_enemies.py` | ROLE={ # role: hp mult, def mult, stance, ember mult, speed m/s, height m | yes |
| S0126 | cloud | `game-plan/data/actors/tools/gen_perks.py` | GATE=[0,10,25,25,25,50,50,50,75,75,90,100] | yes |
| S0127 | cloud | `game-plan/data/actors/tools/gen_player.py` | ---------- Base player resources ---------- | yes |
| S0128 | cloud | `game-plan/data/actors/tools/gen_world.py` | ---------- Resonances ---------- | yes |
| S0129 | cloud | `game-plan/data/actors/tools/run_all.py` | os.chdir(os.path.dirname(os.path.abspath(__file__))) | yes |
| S0130 | cloud | `game-plan/data/items/gen_items.py` | Generates every Shardfall item table in this folder. Re-run to rebuild: python3 gen_items.py | yes |
| S0131 | cloud | `game-plan/data/tools/build.py` | Rebuild all Shardfall data: folder generators, then the link pass, then the validator. Usage: python3 data/tools/build.py""" | yes |
| S0132 | cloud | `game-plan/data/tools/link.py` | Integration pass for Shardfall data. Run after the three folder generators (tools/build.py does it). | yes |
| S0133 | cloud | `game-plan/data/tools/merge/__init__.py` | Design-request merge layer. link.py calls run(T, D) after the core link pass and before the asset-hook registry is built. | yes |
| S0134 | cloud | `game-plan/data/tools/merge/m_0world.py` | World and level design requests (design/world, design/levels/*). Runs first (the zero sorts it first) because it rebuilds | yes |
| S0135 | cloud | `game-plan/data/tools/merge/m_antislop.py` | antislop copy pass (game-plan/antislop/). Runs after every other merge module. | yes |
| S0136 | cloud | `game-plan/data/tools/merge/m_campaign.py` | Campaign data requests (design/campaign/data-requests.csv): new actors, quests and locations, plus a few changes. | yes |
| S0137 | cloud | `game-plan/data/tools/merge/m_cinematics.py` | Merge module for design/cinematics/data-requests.csv (cinematics thread). | yes |
| S0138 | cloud | `game-plan/data/tools/merge/m_frontstrings.py` | Front-end and string requests: accessibility, companion, forgeframe, frontend, platform, social, research, liveops, art, licensing. | yes |
| S0139 | cloud | `game-plan/data/tools/merge/m_numeric.py` | Numeric columns import as numbers (B04 row structs). Runs last. | yes |
| S0140 | cloud | `game-plan/data/tools/merge/m_systems.py` | Merge module m_systems: design/loops, design/systems, design/simulation and design/controls data requests. | yes |
| S0141 | cloud | `game-plan/data/tools/merge/m_writing.py` | Merge module for design/writing/data-requests.csv (writing thread). | yes |
| S0142 | cloud | `game-plan/data/tools/validate.py` | Checks that every ID reference in data/*/*.csv resolves, shared names agree and game text fits (B09: max_chars, tokens, STR_ keys). Exit cod | yes |
| S0143 | cloud | `game-plan/data/ui/gen/ui_a.py` | Shardfall UI text, part A: shared names, common, title, creation, HUD, menus. | yes |
| S0144 | cloud | `game-plan/data/ui/gen/ui_b.py` | Part B: Ledger screens and tooltips. | yes |
| S0145 | cloud | `game-plan/data/ui/gen/ui_c.py` | Part C: popups, notifications, tutorials, confirms, errors, tips, achievements. Writes both CSVs. | yes |
| S0146 | cloud | `game-plan/design/accessibility/tools/gen_accessibility.py` | Builds design/accessibility/*.csv from opts.txt, features.txt and gag.txt. Run from anywhere.""" | yes |
| S0147 | cloud | `game-plan/design/art/tools/gen_art.py` | Generates every CSV in design/art/. Run: python3 tools/gen_art.py (from design/art/). | yes |
| S0148 | cloud | `game-plan/design/audio/samples/freesound/build.py` | B='/mnt/project-files/game-plan/design/audio/samples/freesound' | yes |
| S0149 | cloud | `game-plan/design/audio/samples/freesound/fetch.py` | OUT='/mnt/project-files/game-plan/design/audio/samples/freesound/src' | yes |
| S0150 | cloud | `game-plan/design/audio/tools/gen_audio.py` | Generate every Shardfall audio-direction table into design/audio/. | yes |
| S0151 | cloud | `game-plan/design/audio/tools/gen_sound_design.py` | Shardfall sound design: sonic identity, layered recipes, readability rules, | yes |
| S0152 | cloud | `game-plan/design/audio/tools/synth_samples.py` | Synthesised reference sounds for Shardfall's key signatures. | yes |
| S0153 | cloud | `game-plan/design/audit/tools/map_genre.py` | Map genre roles, cert areas and GDC talks (genre_sources.csv) to owning design folders. | yes |
| S0154 | cloud | `game-plan/design/campaign/tools/gen_campaign.py` | Builds the campaign tables from seeds/*.json. Never hand-edit the CSVs it writes. | yes |
| S0155 | cloud | `game-plan/design/campaign/tools/gen_endings.py` | Writes endings.csv (epilogue slides) and vo_budget.csv (whole-campaign voice plan). Run after gen_campaign.py.""" | yes |
| S0156 | cloud | `game-plan/design/cinematics/tools/gen_cinematics.py` | Generates every Shardfall cinematics table from the beat lists below. | yes |
| S0157 | cloud | `game-plan/design/cinematics/tools/gen_requests.py` | Builds design/cinematics/data-requests.csv from cinematics.csv and shots.csv. Run after gen_cinematics.py.""" | yes |
| S0158 | cloud | `game-plan/design/companion/tools/gen_companion.py` | Builds every table in design/companion/. Run from game-plan/: | yes |
| S0159 | cloud | `game-plan/design/companion/tools/requests_src.py` | data-requests.csv for the companion folder. exec'd by gen_companion.py. | yes |
| S0160 | cloud | `game-plan/design/companion/tools/strings_src.py` | Screen strings and popups for the companion app. exec'd by gen_companion.py. | yes |
| S0161 | cloud | `game-plan/design/continuity/tools/idscan.py` | Scan every data/ and design/ file: definitions = first column of each CSV; refs = ID tokens anywhere. Print undefined refs by prefix and fol | yes |
| S0162 | cloud | `game-plan/design/continuity/tools/namecheck.py` | Compare names given next to IDs in every CSV with the canonical name (world locations, data actors/npcs/quests/items).""" | yes |
| S0163 | cloud | `game-plan/design/continuity/tools/report_rows.py` | Continuity pass 2026-10-03: the issue list behind report.csv (rerun: python3 tools/report_rows.py).""" | yes |
| S0164 | cloud | `game-plan/design/controls/tools/gen_controls.py` | Generate design/controls/*.csv: input map, remap rules, timing, aim assist, | yes |
| S0165 | cloud | `game-plan/design/forgeframe/tools/gen_forgeframe.py` | Generates the Forgeframe (shipped player editor) design tables. | yes |
| S0166 | cloud | `game-plan/design/frontend/tools/gen_frontend.py` | Shardfall front end: boot flow, main menu, saves, photo mode, credits. | yes |
| S0167 | cloud | `game-plan/design/levels/cinderreach/tools/authored.py` | Hand-authored Cinderreach levels: prologue, Spine Keep, towns, Relay Tower, Choir site. | yes |
| S0168 | cloud | `game-plan/design/levels/cinderreach/tools/gen_levels.py` | Builds every Cinderreach (REG_01) level table, map and level sheet. | yes |
| S0169 | cloud | `game-plan/design/levels/glasswaste/tools/check.py` | Checks every ID the Glasswaste level tables use against data/, design/world, design/audio, design/art and the asset sheet.""" | yes |
| S0170 | cloud | `game-plan/design/levels/glasswaste/tools/gen_levels.py` | Glasswaste (REG_04) level design generator. | yes |
| S0171 | cloud | `game-plan/design/levels/hollowdeep/tools/gen_levels.py` | Hollowdeep (REG_06) level design generator. | yes |
| S0172 | cloud | `game-plan/design/levels/multiplayer/tools/gen_mp.py` | Shardfall multiplayer level design generator. | yes |
| S0173 | cloud | `game-plan/design/levels/orbital-ring/tools/gen_orbital.py` | Generate every Orbital Ring (REG_Q, the Quiet) level-design table. | yes |
| S0174 | cloud | `game-plan/design/levels/rimefall/tools/gen_levels.py` | Rimefall (REG_05) level design generator. | yes |
| S0175 | cloud | `game-plan/design/levels/saltmere/tools/gen_saltmere.py` | Saltmere (REG_02) level design generator. | yes |
| S0176 | cloud | `game-plan/design/levels/thornwood/tools/gen_levels.py` | Thornwood (REG_03) level design generator. | yes |
| S0177 | cloud | `game-plan/design/levels/undervault/tools/gen_undervault.py` | Generate every Undervault level table, level sheet and map. | yes |
| S0178 | cloud | `game-plan/design/licensing/tools/gen_licensing.py` | Generate every CSV in design/licensing/. Run from game-plan/: python3 design/licensing/tools/gen_licensing.py | yes |
| S0179 | cloud | `game-plan/design/liveops/tools/gen_liveops.py` | Generate every live ops and launch table in design/liveops/. | yes |
| S0180 | cloud | `game-plan/design/loops/tools/gen_loops.py` | Generates the numeric loop tables in design/loops/ from data/. Run: python3 tools/gen_loops.py (from design/loops/). | yes |
| S0181 | cloud | `game-plan/design/platform/tools/gen_platform.py` | Generate Shardfall platform integration tables into design/platform/. | yes |
| S0182 | cloud | `game-plan/design/production/tools/gen_production.py` | Generates the Shardfall production tables. Run: python3 tools/gen_production.py (from design/production). | yes |
| S0183 | cloud | `game-plan/design/production/tools/gen_roadmap.py` | Generates build-roadmap.csv. Run: python3 tools/gen_roadmap.py (from design/production). | yes |
| S0184 | cloud | `game-plan/design/research/tools/gen_research.py` | Generate design/research/*.csv. Run: python3 design/research/tools/gen_research.py | yes |
| S0185 | cloud | `game-plan/design/simulation/sim/report.py` | Builds report.html (inline SVG charts) from the CSVs sim.py wrote. Run: python3 report.py""" | yes |
| S0186 | cloud | `game-plan/design/simulation/sim/sim.py` | B08 loot and economy simulator (stdlib only). | yes |
| S0187 | cloud | `game-plan/design/simulation/tools/gen_sim.py` | Shardfall open-world simulation tables: crime/bounty/guards, town life/schedules, physics/destruction. | yes |
| S0188 | cloud | `game-plan/design/social/tools/gen_social.py` | Writes every table in design/social/. Run from anywhere: python3 gen_social.py | yes |
| S0189 | cloud | `game-plan/design/systems/tools/gen_systems.py` | Generates every CSV in design/systems/. Values are Shardfall design choices (3 Oct 2026) | yes |
| S0190 | cloud | `game-plan/design/tech/tools/gen_datatable_map.py` | Builds datatable_map.csv: how every CSV in game-plan/data maps into Unreal. Rerun after data changes.""" | yes |
| S0191 | cloud | `game-plan/design/ui-mockups/src/app.js` | Screens: each entry paints a region backdrop, optional canvas extras, then an HTML overlay at 1920x1080. | yes |
| S0192 | cloud | `game-plan/design/ui-mockups/src/build.py` | Build the Shardfall screen gallery: pull real values from data/ into DATA, inline src/ into ../index.html.""" | yes |
| S0193 | cloud | `game-plan/design/ui-mockups/src/data.js` | const DATA={"rarities": [{"name": "Common", "frame_color_hex": "#8A857A"}, {"name": "Forged", "frame_color_hex": "#A87A4A"}, {"name": "Rare" | yes |
| S0194 | cloud | `game-plan/design/ui-mockups/src/icons.py` | game-icons.net (CC BY 3.0) symbols for the gallery. Source: github.com/game-icons/icons.""" | yes |
| S0195 | cloud | `game-plan/design/ui-mockups/src/paint.js` | Shardfall procedural painter: layered landscapes, region features, figures, particles, grade. | yes |
| S0196 | cloud | `game-plan/design/world/future-earth/tools/build_map.mjs` | Generate the future Earth map in Azgaar's FMG (vite dev server on :5173) and export .map, SVG and PNG. | yes |
| S0197 | cloud | `game-plan/design/world/future-earth/tools/calib.py` | Fit FMG's world.png to Natural Earth land as Web Mercator; prints (IoU, x0, k, y0, projection) for make_heightmap.py | yes |
| S0198 | cloud | `game-plan/design/world/future-earth/tools/make_heightmap.py` | Future Earth heightmap: reproject Azgaar's world.png (Web Mercator, fitted to Natural Earth) to | yes |
| S0199 | cloud | `game-plan/design/world/future-earth/tools/run.sh` | Rebuild the future Earth map after editing future_earth.json. | yes |
| S0200 | cloud | `game-plan/design/world/future-earth/tools/verify_load.mjs` | Check the .map loads in FMG: open the page, upload the file, print a few names back | yes |
| S0201 | cloud | `game-plan/design/world/tools/append_locations.py` | Append-only pass over the frozen design/world/locations.csv (3 Oct 2026). | yes |
| S0202 | cloud | `game-plan/design/world/tools/gen_world_design.py` | Shardfall world and level design generator. | yes |
| S0203 | cloud | `game-plan/design/world/tools/unique_names.py` | Continuity CP-11 (decided 2026-10-06): every place in design/world/locations.csv gets a unique name. | yes |
| S0204 | cloud | `game-plan/design/writing/tools/build.py` | Rebuild every writing table, merge data requests, then run the text checker. | yes |
| S0205 | cloud | `game-plan/design/writing/tools/canon_names.py` | World place names for writing generators. | yes |
| S0206 | cloud | `game-plan/design/writing/tools/check_text.py` | Loc pre-check for every text table in design/writing/ (style guide section 9, step 4). | yes |
| S0207 | cloud | `game-plan/design/writing/tools/gen_codex.py` | Codex entries and localization glossary for Shardfall (writing thread, part "codex"). | no |
| S0208 | cloud | `game-plan/design/writing/tools/gen_dialogue.py` | Shardfall writing: dialogue scene outline, cinematics outline, bark sheet, scene summary. | yes |
| S0209 | cloud | `game-plan/design/writing/tools/gen_item_text.py` | Shardfall item text generator (writing thread, part "items"). | no |
| S0210 | cloud | `game-plan/design/writing/tools/gen_quest_text.py` | Shardfall writing: quest text, radiant notices, tutorials, Ostra hints, loading tips. | yes |
| S0211 | cloud | `game-plan/design/writing/tools/gen_scripts.py` | Parse the screenplay scripts in design/writing/scripts/**/*.md into dialogue_lines.csv. | yes |
| S0212 | cloud | `game-plan/design/writing/tools/gen_world_text.py` | Writing pass for world text: place names, site terminals, Choir stones, books, name banks. | yes |
| S0213 | cloud | `game-plan/design/writing/tools/lore_requested.py` | Lore text for lore items that level threads placed and asked data to add (design/merge-report.csv: | yes |
| S0214 | cloud | `game-plan/minecraft/shardfall-weapons/gen.py` | Shardfall weapons -> Minecraft item models (cuboid, Blockbench-compatible), 32x textures, mapping CSV, contact sheets. | yes |
| S0215 | cloud | `game-plan/unreal/Content/Python/sf_blockout.py` | B24: whiteboxes the Cinderreach vertical slice from sf_blockout_spec.json (tools/gen_blockout.py). | yes |
| S0216 | cloud | `game-plan/unreal/Content/Python/sf_build_input.py` | B07: builds the Enhanced Input actions and mapping contexts from sf_input_spec.json (tools/gen_input.py). | yes |
| S0217 | cloud | `game-plan/unreal/Content/Python/sf_build_ui.py` | B19: imports design/frontend screens.csv and widgets.csv into DT_Screens and DT_Widgets, then creates the | yes |
| S0218 | cloud | `game-plan/unreal/Content/Python/sf_import_audio.py` | B27: imports the sample library into /Game/Audio from sf_audio_spec.json (tools/gen_audio_spec.py). | yes |
| S0219 | cloud | `game-plan/unreal/Content/Python/sf_import_data.py` | B05: imports the game-plan/data CSVs into DataTables, CurveTables and StringTables. | yes |
| S0220 | cloud | `game-plan/unreal/assets/cinderreach/env/fetch.py` | Download the Cinderreach environment set listed in spec.csv; write manifest.csv and CREDITS.csv. | yes |
| S0221 | cloud | `game-plan/unreal/tools/GenRowStructs.py` | B04: writes C++ row structs for every table in design/tech/datatable_map.csv, plus the manifest sf_import_data.py reads. | yes |
| S0222 | cloud | `game-plan/unreal/tools/check_formulas.py` | B06: checks the formula library's math against the data CSVs, then writes the C++ test cases. | yes |
| S0223 | cloud | `game-plan/unreal/tools/gen_audio_spec.py` | B27: turns design/audio/*.csv and the sample manifests into Content/Python/sf_audio_spec.json for sf_import_audio.py. | yes |
| S0224 | cloud | `game-plan/unreal/tools/gen_blockout.py` | B24: turns the Cinderreach level design CSVs into Content/Python/sf_blockout_spec.json for sf_blockout.py. | yes |
| S0225 | cloud | `game-plan/unreal/tools/gen_input.py` | B07: turns data/input/*.csv into Content/Python/sf_input_spec.json for sf_build_input.py. | yes |
| S0226 | cloud | `game-plan/unreal/tools/gen_telemetry_schema.py` | B29: turns the event tables in design/tech/06-telemetry-crash-liveops.md into the SfTelemetry schema. | yes |
| S0227 | cloud | `gcp/pack_server.py` | r"""Packs the test server (E:\MCTest\diaithir_server, else E:\MCTest\server) for the Google Cloud VM. | yes |
| S0228 | cloud | `jar_reassemble.py` | Rejoins a jar from its 8 MB parts and checks every sha256. | yes |
| S0229 | cloud | `jobs/bandcheck/check.py` | python3 check.py out-keyed.jsonl: magnitude on the ladder and within the row's ceiling, short basis, no em/en dashes.""" | yes |
| S0230 | cloud | `jobs/nemesis/check_names.py` | python check_names.py <outputs.jsonl>: each line {"id", "output": {...}} for the nemesis_age_* jobs. Exit 1 on any problem.""" | yes |
| S0231 | cloud | `make_core.py` | Make a 'v1 core' copy of a packwiz pack tree: drop the mods in v1_core_cutlist.json (mods with no Age I content). | yes |
| S0232 | cloud | `marketplace/build_data.py` | V = {  # name (lowercase, exact listing name) -> (verdict, note) | yes |
| S0233 | cloud | `marketplace/mcp_registry.py` | out, cur, rows = sys.argv[1], None, {} | yes |
| S0234 | cloud | `marketplace/score.py` | AREAS = { | yes |
| S0235 | cloud | `migrate_to_c.ps1` | Moves E:\Prism and E:\DiaithirServer to the C: NVMe SSD (E: is a USB spinning disk). | yes |
| S0236 | cloud | `migrate_to_c2.ps1` | Moves E:\Prism and E:\DiaithirServer to C: (E: is a USB spinning disk, exFAT, so no junctions) and rewrites E:\Prism / E:\DiaithirServer | yes |
| S0237 | cloud | `mod-categories/worldgen/end-datapack/gen.py` | R='/home/user/endpack/diaithir_end_dp' | yes |
| S0238 | cloud | `mod-ports/patch_range.py` | Relax one dependency versionRange in a NeoForge jar's mods.toml (open-licence mods only). | yes |
| S0239 | cloud | `mythology/build.py` | Build mythology data from src/pantheons.txt. Run: python3 -I build.py | yes |
| S0240 | cloud | `mythology/gen_age1.py` | Per-culture Age I hearth courts (3 gods, 2 creatures each) for every Age I culture in MASTER_CULTURES.csv. | yes |
| S0241 | cloud | `mythology/later_units.py` | Map the later-era culture units (cultures/LATER_AGE_UNITS.csv) to the invented V-to-Rodos courts. Run: python3 -I later_units.py""" | yes |
| S0242 | cloud | `mythology/placement.py` | Join the fantasy-biome sites (DiaithirRPG PR #146 sites.csv) to courts. Run: python3 -I placement.py""" | yes |
| S0243 | cloud | `panscriptum/archive-import/assemble.py` | Agent research (aib/*.json) -> kit record + the kit index edits for The Archive In Between.""" | yes |
| S0244 | cloud | `panscriptum/archive-import/crawl.py` | Pull the free public text of The Archive In Between into raw/ (research only, never committed). | yes |
| S0245 | cloud | `panscriptum/archive-import/marks.py` | Add The Archive In Between to TIERS.json and append its worlds' shelfmarks to SHELFMARKS.json. | yes |
| S0246 | cloud | `panscriptum/archive-import/merge.py` | Merge one new source from a build run without the two LFS records (dc, marvel) into the committed outputs. | yes |
| S0247 | cloud | `panscriptum/archive-import/merge2.py` | Replace one source's worlds, slots and shelf in the committed omniverse outputs with a build run's (run made without dc/marvel). | yes |
| S0248 | cloud | `panscriptum/coverage/crawl.py` | Panscriptum coverage crawl: wiki titles -> missing-entry queues with lead text. | yes |
| S0249 | cloud | `panscriptum/lol-import/assemble.py` | Append the research-json batches to the kit's League of Legends record (append-only, so existing indices hold). | yes |
| S0250 | cloud | `panscriptum/lol-import/pass2/select.py` | Pick catalogue candidates from the raw LoL crawl that the kit record lacks. python3 select.py RAW_DIR RECORD OUT""" | yes |
| S0251 | cloud | `panscriptum/scp-backrooms-import/age_split.py` | Per-entry Age sort for one source with staging/age_sort.py's rule (PR #11). | yes |
| S0252 | cloud | `panscriptum/scp-backrooms-import/assemble.py` | research-json -> kit records + index edits for the SCP Foundation and the Backrooms. | yes |
| S0253 | cloud | `panscriptum/scp-backrooms-import/backrooms_crawl.py` | Crawl backrooms-wiki.wikidot.com tag listings and page text into JSONL (stdlib only). | yes |
| S0254 | cloud | `panscriptum/scp-backrooms-import/marks.py` | Add SCP Foundation and The Backrooms to TIERS.json and append their worlds' shelfmarks to SHELFMARKS.json. | yes |
| S0255 | cloud | `panscriptum/wh-scifi-import/assemble.py` | research-json -> kit records + index edits for all of Warhammer, Star Wars and Star Trek. | yes |
| S0256 | cloud | `panscriptum/wh-scifi-import/gap/gap.py` | Crawled wiki titles minus kit entries -> per-franchise write-job lists. | yes |
| S0257 | cloud | `pc-update/out/merge-all-prs.ps1` | Merge all PRs: marks every open draft PR ready and merges all open PRs, stacked PRs in order, | yes |
| S0258 | cloud | `pc-update/out/update-diaithir.ps1` | Update Diaithir: pulls the latest test pack into the Prism instance. | yes |
| S0259 | cloud | `pc-update/update-diaithir.ps1` | Update Diaithir: pulls the latest test pack into the Prism instance. | yes |
| S0260 | cloud | `perf/boot/boot.sh` | cd /home/user/boot/srv | yes |
| S0261 | cloud | `perf/boot/client.sh` | export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe | yes |
| S0262 | cloud | `plans/v1-test-logs/cmd_shim.py` | Linux shim for tools/testrig/cmd.py: writes commands to the server console (cmd.txt read by boot.sh) and prints the new log.""" | yes |
| S0263 | cloud | `plans/v1-test-logs/zz_v1test.js` | TEST ONLY (v1 cloud test, not for the repo): probes for the Age Turn reload and the cities year listener. | yes |
| S0264 | cloud | `reassemble.py` | Rejoins the Industrial Factory resource pack zips from their 8 MB parts and checks every sha256. | yes |
| S0265 | cloud | `texture-pack/gaps-src/apply.py` | sys.path.insert(0,"/home/user/work/pix") | yes |
| S0266 | cloud | `texture-pack/gaps-src/apply2.py` | sys.path.insert(0,"/home/user/work/pix") | yes |
| S0267 | cloud | `texture-pack/gaps-src/blocks.py` | V="/home/user/diaithirrpg/tools/art/blender/baked/vanilla/assets/minecraft/textures/block/" | yes |
| S0268 | cloud | `texture-pack/gaps-src/blocks_real.py` | S0268 Real-material storage blocks: stacked ingots for metals, faceted mosaics for gems, rock-and-vein masses for raw ore. | yes |
| S0269 | cloud | `texture-pack/gaps-src/build_list.py` | sys.path.insert(0,"/home/user/diaithirrpg/tools/art/blender") | yes |
| S0270 | cloud | `texture-pack/gaps-src/build_page.py` | Progress page: finished photo icons (64 px) next to their source photo, with credits.""" | yes |
| S0271 | cloud | `texture-pack/gaps-src/classify.py` | B="/home/user/diaithirrpg/tools/art/blender/baked/" | yes |
| S0272 | cloud | `texture-pack/gaps-src/cutout.py` | Download picked photos, cut the background out (rembg, cloud only), crop tight, colour-correct, 64 px with a slight sharpen. | yes |
| S0273 | cloud | `texture-pack/gaps-src/dish_run.py` | Photoreal-ish dish renderer for the Diaithir kit. A dish is a JSON scene (vessel, base mounds, sauce pools, pieces, garnish) built | yes |
| S0274 | cloud | `texture-pack/gaps-src/fetch_candidates.py` | Find openly licensed Wikimedia Commons photos for each dish. | yes |
| S0275 | cloud | `texture-pack/gaps-src/fetch_more.py` | Add Openverse (Flickr CC and others; by/by-sa/cc0/pdm only) and more Commons queries to each dish's candidate list. | yes |
| S0276 | cloud | `texture-pack/gaps-src/fetch_unified.py` | Resumable candidate search: for each dish, Haiku's queries against Commons and Openverse (cc0/pdm/by/by-sa). Appends one line per dish to CA | yes |
| S0277 | cloud | `texture-pack/gaps-src/finish.py` | sys.path.insert(0,"/home/user/work/gaps") | yes |
| S0278 | cloud | `texture-pack/gaps-src/make_cakes.py` | Placed-cake block textures (top, side, bottom, cut inner) for the 15 cake dishes, in the vanilla cake layout, rendered through the kit.""" | yes |
| S0279 | cloud | `texture-pack/gaps-src/make_crops.py` | 8 drink crops x 4 growth stages (+seeds) and 12 drink-ingredient/instrument items for the Diaithir kit.""" | yes |
| S0280 | cloud | `texture-pack/gaps-src/make_cw.py` | Cookware and station icon specs for the Diaithir kit: 76 stations, each a 3D model of the real vessel or machine.""" | yes |
| S0281 | cloud | `texture-pack/gaps-src/make_cw2.py` | 31 additional cookware icons (cookware_new.json) for the Diaithir kit; reuses helpers from make_cw.""" | yes |
| S0282 | cloud | `texture-pack/gaps-src/make_dish_scenes.py` | Builds the API job that asks Claude for a per-dish Blender scene spec, and wraps returned scenes for dish_run.py.""" | yes |
| S0283 | cloud | `texture-pack/gaps-src/make_dish_specs.py` | Per-dish kit specs: archetype from the dish name, food colours from the dish's own 16 px icon, 3D vessel and food parts.""" | yes |
| S0284 | cloud | `texture-pack/gaps-src/make_dish_v2.py` | Dish icon specs v2: vessel from the catalogue's shape, food built from the dish's own recipe ingredients.""" | yes |
| S0285 | cloud | `texture-pack/gaps-src/make_drinks.py` | 527 drink icon specs for the Diaithir kit: a 3D vessel per drink, liquid tinted by its colour, accents by category.""" | yes |
| S0286 | cloud | `texture-pack/gaps-src/make_pick_job.py` | Download candidate thumbs, build montages (up to 8 photos, 4 per row) and the API vision job. | yes |
| S0287 | cloud | `texture-pack/gaps-src/materials.py` | Real-world reference table for the gem / nugget / raw / dust / ingot icons. | yes |
| S0288 | cloud | `texture-pack/gaps-src/matlib.py` | sys.path.insert(0,"/home/user/work/pix") | yes |
| S0289 | cloud | `texture-pack/gaps-src/mkspecs.py` | sys.path.insert(0,"/home/user/diaithirrpg/tools/art/blender"); sys.path.insert(0,"/home/user/work/gaps") | yes |
| S0290 | cloud | `texture-pack/gaps-src/model3d.py` | 3D item models (held, dropped, in frames) that match the 64 px icons: faceted gems, bevelled ingots, lumpy nuggets, | yes |
| S0291 | cloud | `texture-pack/gaps-src/ore_proc.py` | Pixel-art ore faces and nugget sheets from the real-material colours (ores_all.json).""" | yes |
| S0292 | cloud | `texture-pack/gaps-src/ore_rebake.py` | sys.path.insert(0,"/home/user/work/pix"); sys.path.insert(0,"/home/user/diaithirrpg/tools/art/blender") | yes |
| S0293 | cloud | `texture-pack/gaps-src/picks_from_jobs.py` | Merge cand_all.jsonl with vision outputs of dish_photo_pick_* into picks.json (id -> chosen photo with credit).""" | yes |
| S0294 | cloud | `texture-pack/gaps-src/pixel_icons.py` | S0294 Hand-drawn style 32 px sprites (shown at 64 px, nearest) for gems, shards, nuggets, raw ore, dust and ingots. | yes |
| S0295 | cloud | `texture-pack/gaps-src/render_dishes.py` | out.jsonl (scene specs from the API) -> kit specs -> sharded Blender renders -> 64 px PNGs + review images. | yes |
| S0296 | cloud | `texture-pack/gaps-src/restyle_newmods.py` | Factory-look filter for textures of mods added after the first coverage pass. Size and UV layout are kept.""" | yes |
| S0297 | cloud | `texture-pack/gaps-src/tanning_make_specs.py` | Specs and map images for the tanning set, rendered through the Diaithir Blender kit (run_kit.py).""" | yes |
| S0298 | cloud | `ug_underground_fix.py` | Turns the Age I underground on in the live world: caves, aquifers, lava, geodes and stone patches (all off in world_gen_settings.dat). | yes |
| S0299 | cloud | `ui_ages.py` | One GUI skin per Age (docs/ui/UI_SCHEMA.md). A screen is drawn in the skin of the Age its block or mod is unlocked in | yes |
| S0300 | cloud | `vshang_start_server.ps1` | Start the Diaithir production server detached, then its watchdog. | yes |
| S0301 | cloud | `world-checks/build_page.py` | snow = [json.loads(l) for l in open("snow_all.jsonl")] | yes |
| S0302 | cloud | `world-checks/ores.py` | Ore Y histogram per site: actual Y bands, and Y mapped back to the vanilla profile (Tellus shell mapping).""" | yes |
| S0303 | cloud | `world-checks/pregen.py` | for name in sys.argv[1:]: | yes |
| S0304 | cloud | `world-checks/pregen_t.py` | for name in sys.argv[1:]: | yes |
| S0305 | cloud | `world-checks/rcon.py` | def rcon(cmds, host="127.0.0.1", port=25575, pw="x"): | yes |
| S0306 | cloud | `world-checks/render.py` | Top-down PNG per site: snow white, water blue, land shaded by elevation, ice-sheet columns tinted; 1 px = 4x4 blocks.""" | yes |
| S0307 | cloud | `world-checks/scan.py` | Scan Tellus region files: per-column ground Y, snow cover, bedrock floor, and every *_ore block position.""" | yes |
| S0308 | cloud | `world-checks/sites.py` | R = 111319.49166666667 * 180 / math.pi | yes |
| S0309 | cloud | `world-checks/snow.py` | Snowline check: snow cover fraction by elevation band vs the Age I line (EraMath.age1SnowlineMeters).""" | yes |
| S0310 | cloud | `tools/get_jdk25.sh` | Installs Temurin JDK 25 into /tmp/claude-0/jdk25 (cloud container, via the proxy) and prints how to use it. | yes |
| S0311 | cloud | `tools/compile_fix_loop.py` | S0311 (v2: prompt caching on the stable prefix, 6 parallel direct calls, optional gradle mirror init) Compile-fix loop: gradle compileJava p | yes |
| S0316 | cloud | `names/linguistics/audit_names.py` | S0316 Audits every culture name in names/*.json against names/linguistics/rules/<slug>.json (graphemes, forbidden patterns, word length); wr | yes |
| S0317 | cloud | `names/linguistics/research_rules.py` | S0317 One direct cached Claude call per culture language: researches how a linguist builds words there, writes names/linguistics/rules/<slug | yes |
| S0322 | global | `claim_id.py` | S0322 atomically claims the next free script ID(s) via next_id (pull --rebase, bump, push, retry): python3 -I claim_id.py [count] | yes |
| S0331 | cloud | `tools/harness/srvup.sh` | S0331 srvup.sh SRV LOG : boot a NeoForge server and leave it running; commands go to LOG.in (use cmd.sh). Prints Done/failed line. | yes |
| S0332 | cloud | `tools/harness/cmd.sh` | S0332 cmd.sh LOG "command" : send a console command to a server started by srvup.sh (rcon alternative: S0071 rcon.py) | yes |
| S0333 | cloud | `tools/harness/shot.sh` | S0333 shot.sh FILE.png : screenshot of the Xvfb display (env DISPLAY_NUM, default 96) | yes |
| S0334 | cloud | `tools/harness/cl_join.sh` | S0334 cl_join.sh CLIENTDIR OUTDIR : headless client (Xvfb + portablemc) joins a world or server; returns at once. | yes |
| S0335 | cloud | `names/linguistics/regen_names.py` | S0312 Regenerates every culture name that fails its language rules (Haiku, rules file cached per language, up to 3 repair rounds); writes na | yes |
| S0335 | global | `crawl_all.py` | S0335 crawls /mnt/project-files into catalog/{D,F,M,A,J}.tsv with stable IDs: python3 -I crawl_all.py <repo> | yes |
| S0336 | global | `add_rows.py` | S0336 registers hand-fed types T (threads) and P (PRs/branches): python3 -I add_rows.py <repo> T < tsv | yes |
