# Pack consolidation audit (pack-v1-3, 546 mods)

Generated 2026-11-02 by Haiku 5.5 Batch (per-mod classification) + Sonnet 5.5 Batch (per-family merge plan), both with prompt caching. Data: Modrinth API, cfwidget, and the jars themselves (class, recipe and data counts). Full per-mod table: `PACK_CONSOLIDATION_AUDIT.csv`.

## Headline

- **546 mods fold to about 238**: 80 real Diaithir modules plus 158 kept separate (74 of those are libraries/APIs). As dependents merge, many kept libraries drop away, so the final count would be lower (not estimated).
- A realistic 'few dozen' target needs the 158 kept mods cut further; the planner kept big standalones (Mekanism, AE2, Create-class, BoP) and libraries. The 20 to 40 figure holds only if those big content mods are also rebuilt, which is the most expensive part.
- Licence mix: 375 open, 138 ARR, 29 unknown. ARR/unknown mods can only be clean-room rewritten, not merged as code.
- Content type: 269 code-heavy, 85 mixed, 104 data-only, 84 library.
- Planned routes inside modules: 141 portable, 119 clean-room, 44 to datapack/KubeJS data.
- Effort (rough, planner's estimate, one focused engineer-day each): 1553 days across 80 modules. Treat as order of magnitude.

## Modules by family

| Family | Modules | Effort days | Members | Clean-room | Portable | As data |
|---|---|---|---|---|---|---|
| biomes-terrain-structures | 8 | 247 | 88 | 51 | 22 | 15 |
| diaithir-own | 9 | 129 | 46 | 3 | 25 | 5 |
| storage-inventory | 4 | 123 | 14 | 5 | 0 | 0 |
| logistics-networks-automation | 5 | 123 | 24 | 4 | 15 | 2 |
| food-farming-cooking | 4 | 111 | 15 | 4 | 9 | 2 |
| mobs-fauna-bosses | 3 | 92 | 20 | 5 | 12 | 1 |
| magic-enchanting | 3 | 90 | 11 | 7 | 4 | 3 |
| transport-vehicles | 4 | 72 | 16 | 3 | 0 | 2 |
| ui-hud-maps-tooltips | 5 | 70 | 23 | 4 | 19 | 0 |
| equipment-weapons-armor | 3 | 66 | 13 | 8 | 5 | 3 |
| game-mechanics-qol | 4 | 57 | 17 | 6 | 9 | 1 |
| visuals-shaders-animations-sound | 3 | 52 | 16 | 4 | 0 | 1 |
| performance-optimisation | 3 | 47 | 15 | 2 | 8 | 0 |
| economy-trade-quests-progression | 2 | 46 | 5 | 2 | 0 | 0 |
| tech-machines-energy | 4 | 45 | 14 | 0 | 2 | 1 |
| ores-resources-worldgen-minerals | 3 | 44 | 8 | 2 | 4 | 2 |
| decoration-building | 4 | 42 | 23 | 7 | 0 | 5 |
| admin-server-tools | 3 | 37 | 7 | 4 | 2 | 0 |
| unclassified | 2 | 30 | 3 | 3 | 0 | 1 |
| library-dependency | 3 | 24 | 7 | 1 | 6 | 0 |
| social-chat-voice-claims | 1 | 6 | 3 | 1 | 0 | 0 |

## Module list

| Module | Family | Purpose | Mods | Days | Risk |
|---|---|---|---|---|---|
| diaithir-admin-core | admin-server-tools | Server admin suite: essential commands, rank and permission system, and scheduled world backups in one codebase. | 3 | 14 | med |
| diaithir-crash-tools | admin-server-tools | Crash reporting and analysis: post-crash log GUI plus server-admin crash utilities in one module. | 2 | 18 | high |
| diaithir-network-compat | admin-server-tools | Connection layer fixes: modpack-version-based server compatibility check plus packet, NBT and timeout fixes. | 2 | 5 | med |
| diaithir-adventure-structures | biomes-terrain-structures | General structure packs, Formations library and structure-name tool folded into one worldgen-structure module. | 25 | 40 | med |
| diaithir-dungeons-underground | biomes-terrain-structures | Dungeons, taverns, underground rooms, archaeology and ocean dungeons merged into one underground-exploration module. | 6 | 22 | med |
| diaithir-end | biomes-terrain-structures | Merged End content: End Remastered with its Lost Castle, Nullscape terrain, and extra End structures. | 5 | 15 | med |
| diaithir-nether | biomes-terrain-structures | Merged Nether overhaul: biomes, structures, mobs and loot from five Nether mods plus Moog's Nether data. | 6 | 45 | high |
| diaithir-overworld-biomes | biomes-terrain-structures | Unified overworld biome, terrain, cave-biome, seasons and biome-locator module replacing overlapping worldgen overhauls. | 11 | 60 | high |
| diaithir-ruins-landmarks | biomes-terrain-structures | Ruins, monuments, giant landmarks and lost cities as one data-driven landmark pack. | 15 | 18 | low |
| diaithir-villages-settlements | biomes-terrain-structures | One village, outpost, castle and medieval-settlement overhaul combining the village mods. | 8 | 25 | med |
| diaithir-yungs-structures | biomes-terrain-structures | All YUNG's vanilla-structure redesigns, bridges and extras, plus Buried Wrecks and ocean ruins, in one module. | 12 | 22 | low |
| diaithir-building-tools | decoration-building | Unified building aids: construction sticks, building gadgets, mirrors, arrays and build modes under one codebase. | 3 | 9 | med |
| diaithir-decor-furnishings | decoration-building | Decorative statues, signposts, glass, camouflage, bookcases and ornamental blocks consolidated into one decoration module. | 6 | 14 | med |
| diaithir-diagonal-blocks | decoration-building | Diagonal fences, walls and windows folded into one mod sharing a single copy of the bundled library. | 3 | 3 | low |
| diaithir-macaw-blocks | decoration-building | Macaw's building-block family plus Stoneworks as one data-driven module, with furniture and lights rebuilt clean-room. | 11 | 16 | high |
| diaithir-client | diaithir-own | Client-side branding, early-window and tooltip polish merged into one client module with shared fonts and textures. | 3 | 4 | low |
| diaithir-content-data | diaithir-own | Data-heavy content: compat assets, elevators, wood variants, musket weapons, and the Ages progression mod. | 5 | 8 | med |
| diaithir-core-systems | diaithir-own | Small first-party utility mods: chunkloading, forcefield, storage network, voice, perf, bridges, wiretech and similar. | 14 | 12 | med |
| diaithir-creatures | diaithir-own | Creature and mob content: Ice and Fire, Untamed Wilds, Ribbits, Bestiary, plus the Walkers and Remorphed morphing mods. | 6 | 22 | high |
| diaithir-dimensions-world | diaithir-own | World-expansion content: Dimdoors, Eternal Starlight, Paradise Lost and Graveyard biomes and dimensions. | 5 | 25 | high |
| diaithir-kitchen-brewing | diaithir-own | Food, farming, cooking, brewing, potions and tavern content in one module. | 4 | 9 | med |
| diaithir-map-utility | diaithir-own | World-mapping and structure utilities: Antique Atlas, Surveyor, Structurize, Jupiter. | 4 | 9 | med |
| diaithir-tech-automation | diaithir-own | Tech and automation: Actually Additions, MEGA Cells, RFTools builder and power. | 4 | 10 | med |
| diaithir-vehicles | diaithir-own | Clean-room vehicle system rebuilt from observed Immersive Vehicles behaviour, with no code or assets copied. | 1 | 30 | high |
| diaithir-quests-skills | economy-trade-quests-progression | Clean-room quest book and skill-tree progression system, with quest rewards able to grant skill points and XP. | 2 | 40 | high |
| diaithir-villager-trade | economy-trade-quests-progression | Unified villager trading: mass-trade Trading Post plus Villager Trading Plus enhancements, one codebase and one config. | 3 | 6 | low |
| diaithir-accessories | equipment-weapons-armor | Wearable and carried utility: tool belt, heart canisters, jewelry and item magnets, sharing one accessory-slot integration. | 4 | 20 | med |
| diaithir-combat-arms | equipment-weapons-armor | Unified melee, ranged, roll and mounted combat: weapons, attributes, enchantments and animations from the RPG-series family. | 5 | 30 | high |
| diaithir-tools-gadgets | equipment-weapons-armor | Craftable station-sticks, mining laser gadgets, configurable turrets, and Silent Gear metalworking compat recipes. | 4 | 16 | med |
| diaithir-crops-and-trees | food-farming-cooking | Croptopia foods, breedable crops and trees, plus right-click harvesting in one farming content module. | 4 | 48 | high |
| diaithir-food-diet | food-farming-cooking | Unified diet variety, nutrition buffs/debuffs and food spoilage system. | 3 | 10 | med |
| diaithir-kitchen-farmtech | food-farming-cooking | Kitchen multiblock, market and sprinklers, farming automation machines, and upgraded furnaces. | 4 | 41 | high |
| diaithir-mystical-agriculture | food-farming-cooking | Single Mystical Agriculture core with Agradditions tier 6 crops, tiered crystals and crop customization folded in. | 4 | 12 | med |
| diaithir-attribute-fixes | game-mechanics-qol | Vanilla bug and limit fixes: attribute caps, max health, nether portal destinations, transparent-block hits, experimental settings. | 5 | 8 | med |
| diaithir-combat-progression | game-mechanics-qol | Chance-based critical hits plus a class skill-tree progression system. | 2 | 14 | high |
| diaithir-death-recovery | game-mechanics-qol | Single grave system that stores player items on death, with migration from the duplicate mod. | 2 | 4 | med |
| diaithir-world-interaction | game-mechanics-qol | Player interaction QoL: carrying, patting, multi-block mining, hammers, crafting grid tweaks, keybind bundles, drop merging, utility modules. | 8 | 31 | high |
| diaithir-filter-system | library-dependency | Clean-room item filtering system with GUI editing, replacing the All-Rights-Reserved FTB Filter System. | 1 | 10 | high |
| diaithir-mcjty-core | library-dependency | Merge McJty shared utility library and RFTools base library, ported from 1.21 to 26.1. | 2 | 5 | low |
| diaithir-multiloader-compat | library-dependency | Port and fold older-version multiloader abstraction, connection and config-GUI libraries (20.x builds) into one 26.1 compat core. | 4 | 9 | med |
| diaithir-ae2-extensions | logistics-networks-automation | Single AE2 addon module: wireless terminals, cards, autocrafting QoL, requester, analyser and construction-stick integration. | 8 | 28 | med |
| diaithir-integrated-addons | logistics-networks-automation | Fold Integrated Crafting, Terminals and Tunnels into one addon module depending on Integrated Dynamics. | 3 | 14 | med |
| diaithir-logistics-utilities | logistics-networks-automation | Hopper variants, item collectors and laser bridges as one small utility module. | 4 | 9 | low |
| diaithir-pipes | logistics-networks-automation | One pipe system for items, fluids and energy, with a connector tool. | 4 | 30 | high |
| diaithir-routing-networks | logistics-networks-automation | Unified wireless and router-based item, fluid and energy routing: routers, LaserIO, Flux Networks and Logistics Network. | 5 | 42 | high |
| diaithir-arcane-classes | magic-enchanting | Wizard, Paladin and Priest class content and rune ammo, rebuilt as data on top of Spell Engine. | 3 | 10 | med |
| diaithir-arcane-relics | magic-enchanting | Clean-room magical relics, Arcanus-style building and ritual content, aura items and utility magic blocks. | 4 | 45 | high |
| diaithir-ritual-enchant | magic-enchanting | Ported open-licence magic: extended enchanting, druidic rituals, evil blood content and classical alchemy. | 4 | 35 | med |
| diaithir-creature-utilities | mobs-fauna-bosses | Fishing, mob capture, feeding, horse calling and spawner manipulation utilities for animals and mobs. | 5 | 22 | med |
| diaithir-hostile-encounters | mobs-fauna-bosses | Hostile mobs, mutants, raiders, golem dungeons, gateway wave events, horde nights and boss-related tweaks in one combat-content module. | 10 | 32 | high |
| diaithir-villagers-npcs | mobs-fauna-bosses | Villager and piglin interaction, village defenders and guards, and MCA social systems, with id migration. | 5 | 38 | high |
| diaithir-metal-processing | ores-resources-worldgen-minerals | Metal and gem processing: foundry multiblock, auto-generated ore processing chains, and gem tools and blocks. | 3 | 28 | high |
| diaithir-resource-gathering | ores-resources-worldgen-minerals | Unified passive and active resource gathering: geode-style ores, cobble generators and water-strainer finds. | 3 | 11 | med |
| diaithir-worldgen-structures | ores-resources-worldgen-minerals | Underground stone blob worldgen tweaks and handcrafted and procedural dungeons with tiered loot. | 2 | 5 | low |
| diaithir-client-render-culling | performance-optimisation | Client rendering helpers: immediate-mode batching plus clean-room async entity and block-entity culling. | 2 | 11 | high |
| diaithir-server-logic-tweaks | performance-optimisation | Unified server-side logic optimisations: AI, XP orbs, recipes, crafting, furnaces, redstone, rails, hashing. | 9 | 20 | med |
| diaithir-worldgen-chunk-opts | performance-optimisation | Worldgen, lighting and chunk-load optimisations: ScalableLux, Fast Noise, Structure Layout Optimizer, Ksyxis. | 4 | 16 | high |
| diaithir-chat-client | social-chat-voice-claims | Unified chat module: unreportable chat, player heads beside messages, and extended chat history length. | 3 | 6 | med |
| diaithir-chests-drawers | storage-inventory | Chest variants and drawer storage: echo, 8x nether, multiblock colossal chests, plus merged drawers. | 5 | 22 | med |
| diaithir-inventory-ui | storage-inventory | Inventory quality-of-life: sorting, essential inventory tweaks and a draggable trash slot. | 3 | 12 | low |
| diaithir-linked-storage | storage-inventory | Unified frequency/owner-based linked inventories: ender-style chests, linked chests and entangled blocks. | 3 | 14 | med |
| diaithir-sophisticated-portable | storage-inventory | Tiered upgradeable storage, placeable backpacks and DankNull-style portable inventory in one module. | 3 | 75 | high |
| diaithir-automation-crafting | tech-machines-energy | Automation blocks, early-game animal-powered machines, Mystical Agriculture automation and extended crafting tables. | 4 | 16 | med |
| diaithir-mekanism-addons | tech-machines-energy | Fold Mekanism Additions, Generators and Tools into one add-on module, with Mekanism itself kept separate. | 3 | 8 | low |
| diaithir-miners | tech-machines-energy | Merged quarry and mining machines under one set of ids, keeping the best features of each. | 3 | 12 | med |
| diaithir-power-storage | tech-machines-energy | Unified energy generation, storage and transfer: Powah, ME-network flux, charging gadgets and EnderIO Endergy data. | 4 | 9 | med |
| diaithir-aircraft | transport-vehicles | Immersive Aircraft core plus its aircraft addons folded into one aircraft system with shared ids | 3 | 14 | med |
| diaithir-ground-water-transport | transport-vehicles | Boats, minecarts and mounts: boat movement, cargo boats, minecart trains, storage minecarts, horse improvements | 6 | 30 | high |
| diaithir-personal-mobility | transport-vehicles | Personal movement and helpers: jetpacks, hang glider, grappling hooks, follower drones | 4 | 18 | med |
| diaithir-travel-structures | transport-vehicles | Fixed travel infrastructure: elevators, bridges and simple teleporter blocks | 3 | 10 | low |
| diaithir-client-view-input | ui-hud-maps-tooltips | Client view, input and settings: zoom, first-person, borderless window, IME blocking, keybinds, GUI and Sodium options. | 7 | 24 | high |
| diaithir-hud-overlays | ui-hud-maps-tooltips | In-world and HUD feedback: advancements UI, pickup notices, toasts, bars, measurements, pings, speech balloons. | 7 | 16 | med |
| diaithir-inventory-tools | ui-hud-maps-tooltips | Inventory sorting, mouse-drag tweaks and search, merged into one inventory interaction layer. | 3 | 15 | med |
| diaithir-structure-navigation | ui-hud-maps-tooltips | Locate structures and automatically remember discovered structure waypoints. | 2 | 9 | med |
| diaithir-tooltips | ui-hud-maps-tooltips | Unified item tooltips: enchantment descriptions, food effects, advanced F3+H data and durability. | 4 | 6 | low |
| diaithir-trials-overhaul | unclassified | Clean-room rebuild of overhauled trial chamber structures, loot and recipes as datapack/KubeJS data for 26.1.2. | 1 | 8 | med |
| diaithir-utility-visuals | unclassified | Clean-room utility machines and ambient visual effects, replacing RFTools Utility and Visuality. | 2 | 22 | high |
| diaithir-audio | visuals-shaders-animations-sound | Unified client audio: ambient soundscapes, selective muffling, physical sound propagation and playable instruments/melodies. | 4 | 8 | med |
| diaithir-entity-animation | visuals-shaders-animations-sound | Entity model/texture customisation, player animations, emotes and 3D skin layers in one client rendering module. | 5 | 24 | high |
| diaithir-world-visuals | visuals-shaders-animations-sound | World and client visual polish: dynamic lights, falling leaves, skybox, flicker fix, glowing blocks, titles, inventory movement. | 7 | 20 | med |

## Recommended order

1. Data-only and datapack folds first (cheap, safe, no code): see `as_data` rows in the CSV.
2. Open-licence code merges in families with obvious duplicates (storage, QoL, UI, performance).
3. Clean-room rewrites last, highest-value first; each needs id migration and a client world-join test before publish.
4. Libraries come off only after every dependent is merged.

## Caveats

- Classification is from names, descriptions, licence fields and jar contents, not source reading. CurseForge licences are often blank (cfwidget), so those show `unknown` until checked on the page.
- The count depends on how much of the big standalone content is rebuilt. Marlon should decide whether Mekanism-class mods are folded or stay.
- 4 mods failed JSON parse in pass 1 and were placed by the family pass; verify them in the CSV (`family` blank).
- Unverified: effort days, risk, and duplicate groups are model estimates.

## V1 pack size (11-09)

The V1 pack is the wave17 packwiz branch (diaithir-ports claude/pack-v1-3-wave17 plus the 11-09 fixes): 176 `.pw.toml` links (149 both, 23 client, 4 server) and 38 local jars in `mods/`. Counting both sides that is about 191 server and 210 client entries before library dependencies, against 76 server and 87 client recorded at 11-05 (that count was jars only).

The 20 to 40 mod target above is superseded by the licence rule (Marlon 11-05): ARR and unknown-licence mods stay as their original jars, only open-licence mods are folded. No number is promised. Source: `python3 -I tools/integrity/check_licenses.py .` and the `pw.toml` side counts.
