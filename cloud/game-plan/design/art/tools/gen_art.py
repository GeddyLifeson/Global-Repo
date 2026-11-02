"""Generates every CSV in design/art/. Run: python3 tools/gen_art.py (from design/art/).
All values are Shardfall art-production choices made 2026-10-03 unless a column says otherwise.
Per-asset budgets stay inside design/tech/04-performance-platforms.md (tech owns engine-wide budgets)."""
import csv, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

def w(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)
    print(name, len(rows))

# ---------------------------------------------------------------- asset budgets
# texel density in px per metre at LOD0. tris: LOD0 triangles (skinned/rigid) or Nanite source tris.
w('asset_budgets.csv',
  ['class_id','asset_class','xlsx_rows','geometry','lod0_tris_min','lod0_tris_max','nanite_fallback_tris','lods','materials_max','tex_default','tex_max','tex_sets_max','texel_px_per_m','uv_channels','collision','tech_04_rule','notes'],
  [
  ['ART_CHR_PLAYER_BASE','Player body + head (per body type)','A001 A019','Skinned',35000,45000,'',4,3,'4K','4K',2,'2048 (face 4096)','UV0 unique, UV1 none','Physics asset 18 bodies','Hero 100-150k total, 4K max 3 sets','Head 25k of the total; body under armor is cut away per set. Whole equipped player (base + 5 armor slots) stays at max 3 4K sets and 3 materials, eyes and hair not counted'],
  ['ART_CHR_PLAYER_ARMOR','Player armor set (5 slots: helm, chest, arms, legs, boots)','A002 A020 A043','Skinned',60000,100000,'',4,2,'2K per slot','4K chest only (counts toward the 3-set cap)',2,1024,'UV0 unique; UV1 dye mask shared','Cloth sim on capes/tabards only (Chaos Cloth, max 1 per set)','Hero 100-150k total with base','Full outfit + base must stay under 150k. Per slot: helm 12k, chest 40k, arms 14k, legs 22k, boots 10k (max). Dye via _M mask, no unique dye textures'],
  ['ART_CHR_COSMETIC','Cosmetic ornaments and dyes','A021','Skinned attach / MI only',0,8000,'',4,1,'1K','2K',1,1024,'UV0','None','Inside the 150k hero cap','Dyes are material instance parameter sets, zero new textures'],
  ['ART_CHR_COMPANION','Companions (8)','A022','Skinned',100000,150000,'',4,3,'4K','4K',3,'2048 (face 4096)','UV0','Physics asset','Hero 100-150k','Full facial rig (see 03-animation-direction.md)'],
  ['ART_CHR_NAMED_NPC','Named NPCs, faction leaders, vendors (80)','A023','Skinned',60000,90000,'',4,3,'2K','4K head',3,'1024 (face 2048)','UV0','Physics asset','Below hero cap','Shares generic body kits; unique head + 1 unique outfit piece'],
  ['ART_CHR_OSTRA','Ostra hologram form','A023','Skinned, translucent',30000,45000,'',3,2,'2K','2K',1,1024,'UV0','None','Translucent material 120 instr max','Uses M_Master_Translucent hologram switch; must read at 50% opacity over any region grade'],
  ['ART_CHR_GENERIC_NPC','Generic townsfolk (modular kits)','A024','Skinned modular',25000,45000,'',4,2,'2K','2K',2,1024,'UV0','Physics asset (shared)','Below enemy cap','Body, head, 3 outfit layers, 1 prop. Mesh merge at runtime (Skeletal Mesh Merge) for crowds'],
  ['ART_CHR_ENEMY','Enemy archetype (fodder, shield, skirmisher, artillery)','A025-A028','Skinned',40000,60000,'',4,2,'2K','2K',2,1024,'UV0','Physics asset + hit zones','Enemies 40-70k, 2K','Weak point and breakable parts as separate mesh sections (see bosses.csv weak points)'],
  ['ART_CHR_ENEMY_HEAVY','Enemy heavy and group leader','A025-A028','Skinned',55000,70000,'',4,2,'2K','2K',3,1024,'UV0','Physics asset + hit zones','Enemies 40-70k, 2K','Leader carries one tall element (banner, antenna, halo) per Visual Bible'],
  ['ART_CHR_ENEMY_VARIANT','Regional variant (1 reskin per region cap)','A029','MI + attach',0,10000,'',4,1,'2K','2K',1,1024,'UV0','Shared','Inside base enemy cap','Element tint and gear swap only; max 10k added tris'],
  ['ART_CHR_CREATURE_S','Creature small (rat swarm, mite, moth, fox)','A030','Skinned',6000,15000,'',3,1,'1K','2K',1,1024,'UV0','Capsule','Below enemy cap','Swarms use Niagara mesh/VAT instancing, 1.5k tris per member'],
  ['ART_CHR_CREATURE_M','Creature medium (hound, wolf, deer, boar)','A030','Skinned',25000,45000,'',4,2,'2K','2K',2,1024,'UV0','Physics asset','Enemies 40-70k','Fur via cards, no strand grooms'],
  ['ART_CHR_CREATURE_L','Creature large (drake, golem, serpent, roc, wild Strider)','A030','Skinned',50000,70000,'',4,2,'2K','4K',2,512,'UV0','Physics asset','Enemies 40-70k','4K only for flying creatures seen against sky at close range'],
  ['ART_CHR_CREATURE_XL','Creature huge (Shard Wyrm juvenile)','A030','Skinned',90000,140000,'',5,3,'4K','4K',3,512,'UV0','Physics asset + parts','Bosses up to 200k, 4K','Treated as a mini-boss budget'],
  ['ART_CHR_BOSS','Boss (Shard-bearer, Citadel, field, site)','A031-A034','Skinned',120000,200000,'',5,4,'4K','4K',4,'512-1024 by height','UV0','Physics asset + breakable parts','Bosses up to 200k, 4K','Every breakable part (bosses.csv weak points) is a separate section with intact and broken states; phase change states via MI params or mesh swap'],
  ['ART_CHR_BOSS_RAID','Raid boss','A035','Skinned + Nanite set pieces',150000,200000,'2% or 20k',5,5,'4K','4K',5,512,'UV0','Physics asset + parts','Bosses up to 200k, 4K','Static arena-attached parts may be Nanite and outside the skinned count'],
  ['ART_CHR_MOUNT','Strider mount base','A036','Skinned',70000,90000,'',4,3,'4K','4K',2,1024,'UV0','Physics asset','Hero cap','Saddle and tack separate; glide membrane uses cloth or morph targets, not sim'],
  ['ART_CHR_MOUNT_SKIN','Strider skin','A037','MI + attach',0,15000,'',4,1,'2K','4K',1,1024,'UV0','Shared','Inside mount cap','Most skins are material-only'],
  ['ART_WPN_MELEE','Melee weapon (incl. shields, catalysts, Shardborn)','A009 A038 A039 A043 A044','Skinned or static (rigid)',15000,30000,'',4,2,'2K','2K',1,2048,'UV0 unique, UV1 trail mask','Simple box/capsule for drops; trace sockets for hits','Weapons 15-30k, 2K','Sockets: Trace_Base, Trace_Tip, VFX_Trail_A/B, Grip_R, Grip_L. Shardborn may use 2 sets (body + Shard emissive) at 2K'],
  ['ART_WPN_FIREARM','Firearm 1P and 3P (incl. arena power weapons)','A010 A040 A041 A046','Skinned',20000,30000,'',4,2,'2K','2K',2,2048,'UV0','Box','Weapons 15-30k, 2K','1P and 3P share the mesh; LOD0 only in 1P. Sockets: Muzzle, Eject, Mag, Optic, Grip_L, Sight_ADS'],
  ['ART_WPN_ATTACH','Firearm attachment (barrel, mag, scope, grip)','A042','Static',2000,6000,'',3,1,'1K','1K',1,2048,'UV0','None','Inside weapon cap','Attach to firearm sockets; scopes use a render-target-free reticle material'],
  ['ART_ITEM_PICKUP','World pickup model (consumable, material, lore item)','A047 A048 A049','Nanite static',2000,20000,'',0,1,'1K','2K',1,1024,'UV0','Simple sphere','Props Nanite 2K','Lore items 2K; glow by rarity from shared Niagara, not unique textures'],
  ['ART_ENV_LANDSCAPE','Region landscape','A060 A061 A062','World Partition landscape',0,0,'',0,1,'RVT 256 px/m','',0,'256 (RVT)','N/A','Landscape collision','Landscape uses RVT','1 m quad spacing, components 127x127 quads (2x2 sections of 63). Max 4 painted layers per component, 12 layers per region material'],
  ['ART_ENV_KIT','Modular architecture kit piece (14 kits)','A016 A064 A065-A069','Nanite static',5000,300000,'2% or 3k',0,2,'2K (trim/tiling)','4K hero only',2,512,'UV0 unique or trim, UV1 tiling','Simple collision authored (UCX_), never complex-as-simple','Props Nanite, 2K default','Trim sheets 4K x 1 per kit allowed (counts as kit-shared). 1 m grid snapping, 4 m wall module, pivot at bottom-left-back'],
  ['ART_ENV_LANDMARK','Hero landmark (Meridian spine, Relay Tower, Citadel exterior, Anchor shrine)','A063 A065 A070 A071','Nanite static',300000,3000000,'1% or 20k',0,3,'4K','4K',3,512,'UV0 + UV1','UCX_ per piece','Hero props 4K','Must have HLOD1 and HLOD2 proxy (see lod_rules.csv). Silhouette readable from 2 km'],
  ['ART_ENV_PROP_S','Small prop (clutter, candles, tools)','A076','Nanite static',500,20000,'2% or 500',0,1,'512-1K','1K',1,1024,'UV0','None or simple','Props Nanite 2K','Atlas 4-8 small props per 2K set where possible'],
  ['ART_ENV_PROP_M','Medium prop (furniture, crates, consoles)','A076','Nanite static',20000,80000,'2% or 2k',0,2,'1K-2K','2K',1,1024,'UV0','UCX_','Props Nanite 2K',''],
  ['ART_ENV_PROP_L','Large prop (wreck sections, carts, statues)','A076','Nanite static',80000,500000,'2% or 5k',0,2,'2K','4K hero only',2,512,'UV0 + UV1 tiling','UCX_','Hero props 4K',''],
  ['ART_ENV_ROCK_CLIFF','Rocks and cliffs','A077','Nanite static',50000,1500000,'1% or 5k',0,1,'2K + tiling detail','4K',1,512,'UV0 + UV1 tiling','UCX_ or simplified hull','Props Nanite','World-aligned blend with landscape via RVT'],
  ['ART_ENV_TREE','Tree','A077','Nanite foliage (WPO wind)',100000,400000,'1% or 4k',0,2,'2K bark + 2K leaf atlas','2K',2,512,'UV0','Trunk capsule only','Props Nanite','WPO disabled beyond 80 m (WPO Disable Distance). Leaves masked, no translucency'],
  ['ART_ENV_GRASS','Grass, flowers, small plants','A077','Instanced non-Nanite (PCG)',50,600,'',3,1,'1K atlas','1K',1,'n/a','UV0','None','Overdraw checked in VFX review map','Cull 60 m (PS5/XSX), 40 m (Series S/Deck)'],
  ['ART_ENV_DECAL','Decal (grime, blood, scorch, graffiti, signage)','A076','DBuffer decal',0,0,'',0,1,'1K','2K',1,1024,'n/a','None','Material 120 instr (decal counts as translucent)','Max 40 overlapping decals per screen region; fade at 50 m'],
  ['ART_ENV_SKY','Sky, clouds, time of day, the Quiet in orbit','A078','Sky Atmosphere + Volumetric Clouds + mesh',0,50000,'',0,2,'2K','4K (Quiet orbital mesh)',1,'n/a','n/a','None','Lumen budget 4.0 ms','No baked skyboxes; Quiet orbital mesh is an unlit emissive card set'],
  ['ART_VEH_GROUND','Ground vehicle (skimmer, hauler)','A080 A081 A083','Skinned (Chaos Vehicle)',60000,100000,'',4,3,'2K','4K hull',2,1024,'UV0','Physics asset; per-part damage shapes','Hero cap','Parts per plan Part 1b: hull, engine, wheels, turret. Each part has intact, damaged, destroyed state'],
  ['ART_VEH_AIR','Flyer (hijackable)','A082 A083','Skinned',70000,110000,'',4,3,'2K','4K hull',2,1024,'UV0','Physics asset; per-part damage shapes','Hero cap','Parts: hull, 2 engines, 2 wings (wings take 3x explosive damage, so they need the clearest damage art)'],
  ['ART_VFX_SPRITE','VFX sprite / flipbook texture','A013 A084-A088','Niagara GPU sprites',0,0,'',0,1,'512 (8x8 flipbook in 2K)','2K',1,'n/a','n/a','None','2,000 GPU particles per system on screen; translucent 120 instr','Flipbooks 8x8 max; use motion vectors for slow flipbooks'],
  ['ART_VFX_MESH','VFX mesh (shards, debris, rings)','A084-A088','Niagara mesh particles',100,5000,'',2,1,'512','1K',1,'n/a','UV0','None','Inside VFX GPU 2.0 ms','Ward break shards: 300 tris each, max 60 per burst'],
  ['ART_UI_ICON','UI icon (weapon, armor, perk, glyph, map marker)','UV-068 to UV-080','Texture 2D',0,0,'',0,0,'512 source, 256 cooked','512',0,'n/a','n/a','n/a','UI 0.3 GB memory','Authored 512x512, cooked as 256 in atlases; HUD authored at 3840x2160 per Visual Bible'],
  ['ART_UI_KEYART','Key art, store capsules, loading screens','UV-057 UV-112 A106','Texture 2D',0,0,'',0,0,'4K','8K source',0,'n/a','n/a','n/a','Streamed, not resident','Loading screens 4K, stream in, unload on exit'],
  ])

# ---------------------------------------------------------------- LOD and HLOD
w('lod_rules.csv',
  ['class','method','lod0_screen','lod1_screen','lod2_screen','lod3_screen','lod4_screen','lod1_tris_pct','lod2_tris_pct','lod3_tris_pct','lod4_tris_pct','bones_dropped_at','min_lod_series_s_deck','notes'],
  [
  ['Hero character / companion / player','Authored LOD0, auto LOD1-3 then cleaned',1.0,0.5,0.25,0.12,'',50,25,10,'','LOD2: fingers, face bones; LOD3: twist bones',1,'Player never below LOD1 in co-op at 10 m'],
  ['Named and generic NPC','Auto (Skeletal Mesh Reduction)',1.0,0.45,0.22,0.1,'',50,25,10,'','LOD2 fingers, LOD3 face',1,'Crowds beyond 40 m use Animation Sharing + LOD3'],
  ['Enemy and creature','Auto',1.0,0.4,0.2,0.08,'',50,25,10,'','LOD2 fingers and cloth bones',1,'Hit zones stay valid on every LOD'],
  ['Boss and huge creature','Authored LOD0-1, auto LOD2-4',1.0,0.6,0.35,0.18,0.08,60,35,15,6,'LOD3 secondary bones',0,'Bosses fill the screen; LOD1 is the normal combat LOD'],
  ['Weapon','Auto',1.0,0.3,0.12,0.05,'',50,20,8,'','n/a',1,'1P always LOD0'],
  ['Vehicle and mount','Authored LOD0, auto LOD1-3',1.0,0.45,0.2,0.08,'',50,25,10,'','LOD2 suspension detail',1,''],
  ['Grass and small foliage (non-Nanite)','Auto + cull',1.0,0.3,0.1,'','',40,15,'','','n/a',1,'Cull 60 m / 40 m'],
  ['Nanite static (props, kits, rocks, trees, landmarks)','Nanite cluster LOD (automatic)','','','','','','','','','','n/a','n/a','Fallback mesh per asset_budgets.csv nanite_fallback_tris for Lumen surface cache, ray tracing and min-spec PC'],
  ])
w('hlod_rules.csv',
  ['layer','used_for','built_from','distance_m_ps5_xsx','distance_m_series_s_deck','material','tex','notes'],
  [
  ['Streaming range (no HLOD)','All World Partition actors','Source actors','0-384','0-256','Source','Source','tech 03: 128 m cells, loading range 384 m / 256 m'],
  ['HLOD1 Merged','Towns, sites, Citadel exteriors, wreck fields, forests','Merged + simplified mesh per cell, Nanite on','384-1500','256-1000','Baked 1 material per cell','2K per cell (BaseColor, Normal, ORM)','Instanced HLOD for foliage (keep instancing, drop to impostor cards past 1000 m)'],
  ['HLOD2 Simplified','Landmarks and skyline only (Meridian spine, Relay Towers, Citadels, Choir towers, the Quiet)','Approximated mesh, 1-5% tris','1500-world edge','1000-world edge','Baked + emissive mask kept','1K per landmark','Shard emissive glow must survive into HLOD2: the horizon is a promise'],
  ['Landscape LOD','Terrain','Landscape LOD + HLOD landscape proxy','by screen size','by screen size','RVT','RVT','Virtual Heightfield Mesh not used'],
  ])

# ---------------------------------------------------------------- textures and materials
w('texture_rules.csv',
  ['suffix','map','channels','compression','srgb','texture_group','max_res','authoring_rule'],
  [
  ['_D','Base color','RGB (+A opacity if masked)','BC1 (BC3/BC7 with alpha)','Yes','World / Character / Weapon','4K','No lighting baked in. Dielectric albedo 50-240 sRGB, metals 180-255. Charcoal floor 30'],
  ['_N','Normal','RG (B rebuilt)','BC5','No','WorldNormalMap / CharacterNormalMap','4K','DirectX convention (Y-), tangent space MikkTSpace, bake cage from high poly'],
  ['_ORM','Packed masks','R AO, G Roughness, B Metallic','BC1 (BC7 for hero)','No','Masks','4K','Roughness 0.04-1.0; avoid pure 0 and pure 1 metallic gradients'],
  ['_E','Emissive','RGB','BC1','Yes','World','2K','Only Shard light, ship panels, Lens UI and element effects glow. Lens cyan #8FE3EE reserved for Shard-powered objects'],
  ['_M','Dye and feature masks','R dye primary, G dye secondary, B metal trim, A Shard glow','BC7','No','Masks','2K','Every player armor and Strider skin ships one _M; cosmetic dyes only change MI parameters'],
  ['_H','Height','R','BC4','No','World','2K','Landscape and tessellation-free POM only; no Nanite displacement on consoles'],
  ['_SSS','Subsurface / thickness','R','BC4','No','Character / Foliage','2K','Skin, leaves, wax, Choir glass'],
  ['_F','VFX flipbook','RGBA','BC7 (BC3 fallback)','Yes (color) / No (data)','Effects','2K','8x8 max; frames power of two'],
  ['_MV','VFX motion vector','RG','BC5','No','Effects','2K','For flipbooks under 30 fps playback'],
  ['_LUT','Color grading LUT','RGB','Uncompressed','Yes','ColorLookupTable','256x16','One per region and time-of-day key in lighting_tod.csv'],
  ['_UI','UI texture','RGBA','BC7 / UserInterface2D','Yes','UI','512 icons, 4K screens','Authored at 3840x2160; no mips for UI'],
  ['_HDR','HDR sky / cubemap','RGB','BC6H','No','Skybox','2K','Only the Quiet orbital view and menu backdrops; world sky is Sky Atmosphere'],
  ])
w('master_materials.csv',
  ['master','domain_shading','instruction_cap','used_by','key_switches'],
  [
  ['M_Master_Env_Opaque','Surface / Default Lit','200','Kits, props, landmarks, rocks','Trim vs unique, tiling detail, vertex color blend (moss, ash, salt, rime, glass dust by region), Shard emissive, Hollowing desaturation param'],
  ['M_Master_Char_Skin','Surface / Subsurface Profile','200','All skin, creature hide','Shard scar emissive, wetness, Hollowed crystal growth mask'],
  ['M_Master_Char_Gear','Surface / Default Lit','200','Armor, clothing, weapons, vehicles, mount tack','Dye mask (_M), damage state, Shard emissive, element tint (enemy Ward color), cloth sheen'],
  ['M_Master_Hair','Surface / Hair','200','Hair cards, fur cards, beards','Color root/tip, dye'],
  ['M_Master_Eye','Surface / Eye','200','All eyes','Iris color, Shard-touched eye glow'],
  ['M_Master_Foliage','Surface / Two Sided Foliage (masked)','200','Trees, grass, vines, Thornwood red bark','Wind WPO with disable distance, seasonal tint, Hollowing drain, Bloom element vines'],
  ['M_Master_Landscape','Surface / Default Lit (RVT)','200','Region landscapes','Up to 12 layers, RVT output, distance tiling blend, puddles/snow/ash accumulation by weather param'],
  ['M_Master_Decal','Deferred decal (DBuffer)','120','Grime, blood, scorch, signage, telegraph ground decals','Fill-over-time param for AoE telegraphs'],
  ['M_Master_Translucent','Translucent / Default Lit or Unlit','120','Glass, Choir glass, holograms, Ostra, Remnant light walls, Ward shells','Hologram scanline, flicker (off in reduced motion), element tint'],
  ['M_Master_Water','Single Layer Water','200','Rivers, Saltmere flats, lakes, Undervault pools','Salt crust edge, caustics, Hollowing still-water'],
  ['M_Master_VFX','Translucent / Unlit (Niagara)','120','All particles','Erosion, flipbook, soft particle, element color from palette param'],
  ['M_Master_UI','User Interface','n/a','HUD and menus','Lens line sweep, rarity notch, colorblind remap'],
  ])

# ---------------------------------------------------------------- naming
N = []
def n(kind, prefix, pattern, example, folder, notes=''):
    N.append([kind, prefix, pattern, example, folder, notes])
n('Static mesh','SM_','SM_<HookBody>[_Var]','SM_WPN_STS_01 (hook MESH_WPN_STS_01)','/Game/Shardfall/Weapons/Melee/STS/','Hook body = hook ID minus its kind prefix (MESH_, VFX_, ANIM_). SfAssetAudit checks the match')
n('Skeletal mesh','SK_','SK_<HookBody>','SK_ACT_BOSS_VAEL','/Game/Shardfall/Characters/Bosses/VAEL/')
n('Skeleton','SKEL_','SKEL_<Family>','SKEL_Humanoid, SKEL_Strider, SKEL_Quadruped_M','/Game/Shardfall/Characters/_Shared/Skeletons/','Shared skeletons: Humanoid (player, NPC, humanoid enemies), Quadruped S/M/L, Avian, Serpent, Strider, plus one per unique boss body')
n('Physics asset','PHYS_','PHYS_<MeshName>','PHYS_ACT_BOSS_VAEL','beside mesh')
n('Material (master)','M_','M_Master_<Domain>','M_Master_Char_Gear','/Game/Shardfall/Materials/Masters/','Max 12 (master_materials.csv)')
n('Material instance','MI_','MI_<AssetName>[_Var]','MI_WPN_STS_01_Frost','beside mesh')
n('Material function','MF_','MF_<Purpose>','MF_HollowingDesat','/Game/Shardfall/Materials/Functions/')
n('Material parameter collection','MPC_','MPC_<Purpose>','MPC_WeatherState','/Game/Shardfall/Materials/')
n('Texture','T_','T_<AssetName>_<Suffix>','T_WPN_STS_01_ORM','beside mesh','Suffixes from texture_rules.csv')
n('Runtime virtual texture','RVT_','RVT_<Region>_<Use>','RVT_REG_01_Color','/Game/Shardfall/World/REG_01/Landscape/')
n('Animation sequence','A_','A_<Skeleton>_<Set>_<Action>[_Dir][_Var]','A_Humanoid_STS_Light_1, A_Humanoid_Loco_Jog_F','/Game/Shardfall/Animation/<Skeleton>/<Set>/','Set = weapon class code (STS, GRS, ARF...) or Loco, Trav, Hit, Abil, Social, Emote')
n('Animation montage','AM_','AM_<Skeleton>_<Set>_<Action>','AM_Humanoid_STS_Light_1','same as sequence','Montage name matches the melee_frame_data.csv attack_id body: ITM_ATK_STS_LIGHT_1 maps to AM_Humanoid_STS_Light_1')
n('Blend space','BS_','BS_<Skeleton>_<Set>_<Purpose>','BS_Humanoid_Loco_Strafe','same')
n('Aim offset','AO_','AO_<Skeleton>_<Set>','AO_Humanoid_ARF','same')
n('Animation blueprint','ABP_','ABP_<Skeleton>[_Layer_<Set>]','ABP_Humanoid, ABP_Humanoid_Layer_GRS','/Game/Shardfall/Animation/<Skeleton>/','One base ABP plus linked layers per weapon class (tech 01)')
n('Pose search database','PSD_','PSD_<Skeleton>_<Set>','PSD_Humanoid_Loco','same','Motion Matching databases')
n('Control rig','CR_','CR_<Skeleton>_<Purpose>','CR_Humanoid_FootIK','same')
n('IK rig / retargeter','IK_ / RTG_','IK_<Skeleton>, RTG_<From>_To_<To>','RTG_Mocap_To_Humanoid','/Game/Shardfall/Animation/_Retarget/')
n('Niagara system','NS_','NS_<HookBody>','NS_ART_01 (hook VFX_ART_01)','/Game/Shardfall/VFX/<Group>/')
n('Niagara emitter','NE_','NE_<Purpose>','NE_WardShatter_Shards','/Game/Shardfall/VFX/_Emitters/')
n('Sound (MetaSound / wave)','MS_ / SW_','MS_<HookBody>, SW_<HookBody>_<NN>','MS_ART_01','/Game/Shardfall/Audio/','Audio thread owns detail; listed here so the folder tree is complete')
n('Widget blueprint','WBP_','WBP_<Screen>_<Part>','WBP_HUD_Vitals','/Game/Shardfall/UI/<Screen>/')
n('UI texture','T_UI_','T_UI_<HookBody>','T_UI_ICON_DYE_01 (hook UI_ICON_DYE_01)','/Game/Shardfall/UI/Icons/<Group>/')
n('Level / map','L_','L_<Area>[_<Sub>]','L_REG_01_Persistent, L_SITE_REG_01_04, L_ARENA_VAEL','/Game/Shardfall/Maps/<Area>/','Instanced levels for sites, Citadels, raids (tech 03)')
n('Level instance / packed level actor','LI_ / PLA_','LI_<Kit>_<Name>','PLA_KIT_HULL_Corridor_A','/Game/Shardfall/World/Kits/<Kit>/Assemblies/')
n('Data layer','DL_','DL_<Purpose>','DL_Night, DL_Hollowing_Stage2, DL_Season_01','/Game/Shardfall/World/DataLayers/')
n('Post process material','PPM_','PPM_<Purpose>','PPM_HollowingDesat','/Game/Shardfall/Lighting/PostProcess/')
n('Color grading LUT','T_LUT_','T_LUT_<Region>_<TOD>','T_LUT_REG_01_Dusk','/Game/Shardfall/Lighting/LUTs/')
n('Lighting preset (data asset)','DA_Light_','DA_Light_<Region>_<TOD>','DA_Light_REG_01_Day','/Game/Shardfall/Lighting/Presets/','One per lighting_tod.csv row; rows are imported by script')
n('PCG graph','PCG_','PCG_<Region>_<Purpose>','PCG_REG_03_Undergrowth','/Game/Shardfall/World/<Region>/PCG/')
n('Data table (imported)','DT_','DT_<CsvName>','DT_AssetHooks','/Game/Shardfall/Data/','Owned by tech datatable_map.csv')
n('Blueprint class','BP_','BP_<Purpose>','BP_Anchor, BP_RelayTower','/Game/Shardfall/Gameplay/<Area>/')
n('Chaos vehicle / cloth / destruction','VH_ / CLO_ / GC_','VH_<Name>, CLO_<Mesh>, GC_<Mesh>','VH_Skimmer, GC_PRP_Crate_Wood','beside mesh')
n('Source files (DCC, not in Content)','SRC_','SRC_<AssetName>.<ext>','SRC_ACT_BOSS_VAEL.ma, SRC_ACT_BOSS_VAEL.spp','//shardfall/art/source/<same path as Content>/','Maya .ma, Blender .blend, ZBrush .ztl, Substance .spp/.sbsar, Houdini .hip. Exports as FBX next to source')
w('naming_conventions.csv', ['asset_type','prefix','pattern','example','folder','notes'], N)

FOLDERS = [
 ['/Game/Shardfall/Characters/Player/','Base bodies, heads, character creator parts (A001, A019)'],
 ['/Game/Shardfall/Characters/Armor/<ArmorSetID>/','One folder per armor set (A020)'],
 ['/Game/Shardfall/Characters/Cosmetics/','Ornaments; dye presets are data only (A021)'],
 ['/Game/Shardfall/Characters/Companions/<NPC_ID>/','A022'],
 ['/Game/Shardfall/Characters/NPCs/Named/<NPC_ID>/ and /NPCs/Generic/<Culture>/','A023, A024'],
 ['/Game/Shardfall/Characters/Enemies/<FAC_ID>/<ACT_ID>/','A025-A029; one folder per enemies.csv row'],
 ['/Game/Shardfall/Characters/Creatures/<ACT_ID>/','A030'],
 ['/Game/Shardfall/Characters/Bosses/<ACT_ID>/','A031-A035 (mesh, MIs, textures, arena-only props)'],
 ['/Game/Shardfall/Characters/Mount/','A036, A037'],
 ['/Game/Shardfall/Characters/_Shared/','Skeletons, shared materials, eye/hair libraries'],
 ['/Game/Shardfall/Weapons/Melee/<ClassCode>/','A038, A039 (STS, CRV, GRS, AXE, HMR, POL, FST, DGR, SHD, TWB, GAX, GHM)'],
 ['/Game/Shardfall/Weapons/Firearm/<ClassCode>/','A040, A041 (PST, ARF, SCT, SMG, SHG, SNP, LCH, LNC)'],
 ['/Game/Shardfall/Weapons/Attachments/<Type>/','A042'],
 ['/Game/Shardfall/Weapons/Catalysts/ and /Shardborn/ and /Arena/','A043, A044, A046'],
 ['/Game/Shardfall/Items/Pickups/<Group>/','A047-A049 world models'],
 ['/Game/Shardfall/World/<REGION>/','Landscape, PCG, region-unique meshes, region MIs (A060-A062)'],
 ['/Game/Shardfall/World/Kits/<KitCode>/','A064 kits: KIT_CASTLE, KIT_HULL, KIT_CHURCH, KIT_VILLAGE, KIT_RUIN, KIT_REMNANT, KIT_QUIET, KIT_CAVE, KIT_STILT, KIT_THORN, KIT_CHOIR, KIT_MONASTERY, KIT_LIFTED, KIT_UNDERVAULT'],
 ['/Game/Shardfall/World/Props/<Group>/','A076 (Furniture, Containers, Debris, Clutter, ShipParts, Religious, Lighting)'],
 ['/Game/Shardfall/World/Foliage/<Biome>/','A077'],
 ['/Game/Shardfall/World/Landmarks/','Meridian spine, Relay Towers, Anchor shrine (A070, A071)'],
 ['/Game/Shardfall/Vehicles/<Name>/','A080-A083'],
 ['/Game/Shardfall/Animation/<Skeleton>/<Set>/','All animation (A003-A008, A050-A059)'],
 ['/Game/Shardfall/Cinematics/<SceneID>/','Level sequences, cine cameras, cine-only assets'],
 ['/Game/Shardfall/VFX/<Group>/','Matches xlsx VFX sheet groups'],
 ['/Game/Shardfall/Lighting/','Presets, LUTs, post process materials, IES profiles'],
 ['/Game/Shardfall/Materials/','Masters, functions, MPCs'],
 ['/Game/Shardfall/UI/','Widgets and UI textures'],
 ['/Game/Shardfall/Audio/','Owned by audio thread'],
 ['/Game/Shardfall/Maps/','All levels'],
 ['/Game/Shardfall/Data/','Imported DataTables (tech)'],
 ['/Game/Shardfall/Gameplay/','Blueprint classes'],
 ['/Game/Shardfall/_Dev/<user>/','Personal sandboxes; never referenced by shipping content; excluded from cook'],
 ['/Game/Shardfall/_Placeholder/','Pink cube, beep and grey mannequin fallbacks used by DT_AssetHooks'],
]
w('folder_structure.csv', ['content_path','holds'], FOLDERS)

# ---------------------------------------------------------------- lighting
# Physical units: sun in lux, sky in cd/m2 equivalent left to Sky Atmosphere. Exposure in EV100.
REG = [
 # id, name, base sun lux, color temp day K, fog density, fog color, palette note, signature, weather set
 ('REG_01','Cinderreach',100000,5600,0.035,'#7A4A2E','Warm ash haze, low contrast distance','Ash fall','Clear, Ash fall, Shard-storm'),
 ('REG_02','Saltmere',110000,6200,0.045,'#A9CFC6','High-key reflective flats, bright sky in water','Salt spray, mist','Clear, Fog, Rain light, Storm (Lightning)'),
 ('REG_03','Thornwood',80000,5200,0.06,'#6A2A20','Dappled light under red canopy, strong god rays','Pollen, fireflies','Clear, Rain heavy, Fog'),
 ('REG_04','Glasswaste',120000,6500,0.02,'#C7A8E0','Harsh noon, specular glass glints, violet shadows','Glass dust, heat shimmer','Clear, Sandstorm, Shard-storm'),
 ('REG_05','Rimefall',90000,7500,0.05,'#9AB8D0','Cold blue ambient, snow bounce lifts shadows','Snow, breath fog','Snow, Blizzard, Aurora (Weave)'),
 ('REG_06','Hollowdeep',60000,6800,0.07,'#7C7888','Drained, low saturation, floating debris rim-lit','Upward Shard drift','Fog, Shard-storm'),
]
TOD = [  # tod, sun elevation deg, sun lux mult, temp offset K, exposure EV100 min,max, fog mult, sat, contrast, bloom, notes
 ('Dawn',8,0.25,-1800,9,12,1.6,0.95,1.0,0.8,'Long shadows, low fog banks, landmarks backlit'),
 ('Day',55,1.0,0,12,15,1.0,1.0,1.05,0.6,'Reference key; all art reviewed here first'),
 ('Dusk',6,0.2,-2300,8,11,1.3,1.05,1.0,0.9,'Warm rim, Shard glow starts to read'),
 ('Night',-20,0.0,0,3,7,0.8,0.8,1.1,1.2,'Moonlight 0.3 lux at 4100 K plus Weave aurora; Shard light becomes the main navigation cue'),
 ('Storm',35,0.15,800,9,12,2.2,0.85,0.95,0.7,'Weather override: region weather set; lightning flashes capped at 3 per 10 s (photosensitivity)'),
]
L = []
for rid, name, lux, temp, fog, fogc, pal, sig, wx in REG:
    for tod, el, m, toff, emin, emax, fm, sat, con, bl, note in TOD:
        sat_r = round(sat * (0.55 if rid == 'REG_06' else 1.0), 2)
        L.append([f'LGT_{rid}_{tod.upper()}', rid, name, tod, el, round(lux*m) if m else 0, max(1800, temp+toff) if m else 4100,
                  emin, emax, round(fog*fm, 3), fogc, sat_r, con, bl, 0.25 if tod in ('Night','Storm') else 0.15,
                  f'T_LUT_{rid}_{tod}', sig, wx if tod == 'Storm' else '', f'{pal}. {note}'])
SPECIAL = [
 ('LGT_HUB_DAY','REG_HUB','Lantern Hold','Interior day',0,20000,3200,8,11,0.02,'#5A4632',1.0,1.0,0.8,0.2,'T_LUT_REG_HUB_Day','Dust motes, candle haze','','Candlelit consoles; warm practicals 2700 K against cyan console glow; sky through bridge glass'),
 ('LGT_HUB_NIGHT','REG_HUB','Lantern Hold','Interior night',0,0,2700,5,8,0.025,'#3A2A1A',0.95,1.05,1.1,0.25,'T_LUT_REG_HUB_Night','Dust motes','','Practicals only; market stalls lit by lanterns'),
 ('LGT_UND','REG_U','The Undervault','Underground (no TOD)',0,0,0,2,6,0.04,'#173A38',0.9,1.1,1.2,0.3,'T_LUT_REG_U','Shard vein glow','','Lit only by Shard veins (cyan-teal) and player torch; Lumen GI from emissive veins'),
 ('LGT_QUIET','REG_Q','The Quiet','Orbital (no TOD)',10,130000,5900,10,14,0.0,'#000000',0.35,1.25,0.5,0.35,'T_LUT_REG_Q','Low-g dust','','Hard unfiltered starlight, no atmosphere, black shadows, one alarm red #C8281E; planet below as fill (bounce 0.1)'),
 ('LGT_QUIET_INT','REG_Q','The Quiet','Orbital interior',0,0,6500,6,10,0.01,'#22252A',0.3,1.15,0.6,0.3,'T_LUT_REG_Q_Int','None','','Seamless bone-white panels with no visible fixtures; light comes from surfaces'),
 ('LGT_CAVE','ANY','Sites: caves and mines','Interior',0,0,0,3,7,0.03,'#202020',0.9,1.05,1.0,0.3,'T_LUT_Cave','Dust','','Entrance spill + torches 1800 K; shortcut doors always get a light so they read'),
 ('LGT_WRECK','ANY','Sites: wreck sections','Interior',0,0,0,4,8,0.02,'#1C2226',0.9,1.1,1.0,0.3,'T_LUT_Wreck','Sparks, steam','','Emergency strips and sparking panels; cold 6500 K with warm candle offerings'),
 ('LGT_CITADEL','ANY','Citadel interiors','Interior',0,0,0,5,10,0.025,'region fog','region','1.05',0.9,0.25,'T_LUT_<REG>_Citadel','Region signature','','Uses the region palette; boss arenas get a dedicated rig (below)'),
 ('LGT_BOSS_ARENA','ANY','Boss arenas','Boss fight',0,0,0,'locked','locked',0.02,'region fog','region',1.1,0.8,0.3,'T_LUT_<ARENA>','Boss element particles','','Exposure locked for the fight so telegraphs never wash out; key light from behind the player toward the boss; telegraph glints and signal red must keep 3:1 contrast against the arena'),
 ('LGT_MENU','UI','Title and menus','Menu',0,0,0,8,8,0.0,'#000000',1.0,1.0,0.6,0.2,'T_LUT_Menu','','','Live Meridian wreck backdrop per Visual Bible'),
]
w('lighting_tod.csv', ['light_id','region','name','time_of_day','sun_elev_deg','sun_lux','sun_temp_k','ev100_min','ev100_max','fog_density','fog_color','saturation','contrast','bloom','vignette','lut','ambient_particles','weather_set','look_notes'], L + [list(s) for s in SPECIAL])

w('post_process_volumes.csv',
  ['ppv_id','scope','priority','blend_radius_m','unbound','settings_from','notes'],
  [
  ['PPV_Global','World default',0,0,'Yes','LGT_<REG>_DAY of current region via region manager','Exposure method Manual-to-Auto Histogram, metering mask center-weighted; TSR; no chromatic aberration; film grain 0.1 (off in accessibility)'],
  ['PPV_REG_01','Cinderreach',1,200,'No','lighting_tod.csv rows LGT_REG_01_*','Blended by time-of-day manager'],
  ['PPV_REG_02','Saltmere',1,200,'No','LGT_REG_02_*',''],
  ['PPV_REG_03','Thornwood',1,200,'No','LGT_REG_03_*',''],
  ['PPV_REG_04','Glasswaste',1,200,'No','LGT_REG_04_*',''],
  ['PPV_REG_05','Rimefall',1,200,'No','LGT_REG_05_*',''],
  ['PPV_REG_06','Hollowdeep',1,200,'No','LGT_REG_06_*','PPM_HollowingDesat strength 0.7'],
  ['PPV_HUB','Lantern Hold',2,10,'No','LGT_HUB_*',''],
  ['PPV_UND','The Undervault',2,20,'No','LGT_UND',''],
  ['PPV_QUIET','The Quiet',2,0,'Yes (level)','LGT_QUIET / LGT_QUIET_INT',''],
  ['PPV_INTERIOR','Every site and Citadel interior',3,4,'No','LGT_CAVE / LGT_WRECK / LGT_CITADEL','Entrance blends over 4 m so the exposure shift is felt, not popped'],
  ['PPV_BOSS','Every boss arena',4,2,'No','LGT_BOSS_ARENA','Enabled on fog-gate entry'],
  ['PPM_HollowingDesat','Post material, global','n/a','n/a','n/a','MPC_Hollowing.Stage 0-3','Saturation drop 0, 25, 50, 70% by stage; spreads to earlier regions through Act 2 (Visual Bible)'],
  ['PPM_LowHealth','Post material, player','n/a','n/a','n/a','Health < 25%','Blood red #D4483F edge vignette; disabled by reduced-motion only for the pulse'],
  ['PPM_WardBreak','Post material, player','n/a','n/a','n/a','Player Ward breaks','Screen-edge crack 0.4 s'],
  ['PPM_DeathFade','Post material, player','n/a','n/a','n/a','Death','Fade to Lens cyan per Visual Bible'],
  ])

# ---------------------------------------------------------------- animation timing
# All frame counts at 60 fps, matching melee_frame_data.csv and boss_moves.csv.
w('anim_timing_standards.csv',
  ['action','category','startup_f','active_f','recovery_f','total_f_range','commit_frame','root_motion','blend_in_s','blend_out_s','cancel_rule','source'],
  [
  ['Light attack 1 (light weapons: dagger, fist, curved)','Player melee','8-12','4','20-24','32-40',6,'Yes (Motion Warping to target within 1.5 m)',0.05,0.15,'Roll cancel after recovery-8','melee_frame_data.csv'],
  ['Light attack 1 (medium: straight sword, axe, twinblade, polearm, shield)','Player melee','11-14','4','22-26','37-44',6,'Yes',0.05,0.15,'Roll cancel after recovery-8','melee_frame_data.csv'],
  ['Light attack 1 (heavy: greatsword, hammer)','Player melee','18-23','4-5','26-28','48-56',6,'Yes',0.08,0.2,'Roll cancel after recovery-8','melee_frame_data.csv'],
  ['Light chain 2 and 3','Player melee','startup of L1 +1 to +2','4','22-28','',6,'Yes',0.03,0.15,'Chains on input in last 12 f of recovery','melee_frame_data.csv'],
  ['Heavy attack','Player melee','16-28','5','28-32','49-65',6,'Yes',0.08,0.2,'No cancel before recovery end-6',''],
  ['Charged heavy (release)','Player melee','30-42','6','32-36','68-84',6,'Yes',0.1,0.25,'Charge loop 30 f can be released early',''],
  ['Running attack','Player melee','12-24','5','26-30','','6','Yes (keeps momentum 0.6)',0.05,0.2,'',''],
  ['Jump attack','Player melee','14-26','5','28-32','','6','Yes',0.05,0.2,'Lands into recovery',''],
  ['Guard counter','Player melee','13-25','5','24-28','','6','Yes',0.03,0.15,'Window 30 f after a block',''],
  ['Roll (light load)','Player defense','0','i-frames 13 (f2-14)','20','33',0,'Yes, 3.2 m','0.02','0.1','Plan Part 1b: light <30%','plan 3.6 / Elden Ring 13 i-frames'],
  ['Roll (medium load)','Player defense','0','i-frames 13','24','37',0,'Yes, 2.8 m',0.02,0.1,'',''],
  ['Roll (heavy load)','Player defense','0','i-frames 12','34','46',0,'Yes, 2.2 m',0.02,0.12,'Heavy doubles recovery vs light (plan Part 1b)',''],
  ['Backstep','Player defense','0','i-frames 8','14','22',0,'Yes, 1.4 m',0.02,0.1,'',''],
  ['Parry','Player defense','3','7 (8 bucklers; Assist +4)','28','38',0,'No',0.02,0.1,'Riposte window 60 f','Dark Souls 7-frame parry'],
  ['Block raise / hold / break','Player defense','4','hold','guard-break stagger 50','',0,'No',0.08,0.15,'',''],
  ['Flinch (light hit)','Hit reaction','','','14-20','14-20','','No (additive upper body)',0.02,0.1,'Super-armor attacks ignore',''],
  ['Stagger (heavy hit)','Hit reaction','','','30-40','30-40','','Yes, 0.5-1 m push',0.02,0.15,'',''],
  ['Knockdown + get-up','Hit reaction','','','60 down + 40 get-up (i-frames on get-up 20)','100','','Yes',0.03,0.2,'3 staggers in 8 s cause knockdown, then 2 s immunity (plan Part 1b Outward)',''],
  ['Death','Hit reaction','','','90-150','90-150','','Yes',0.05,0,'Ragdoll blend at end',''],
  ['Tonic drink','Player item','20 (heal at f20)','','24','44',0,'No (walk at 30% speed)',0.1,0.15,'Interruptible before f20',''],
  ['Cast (grenade slot)','Player ability','14-20','','18-24','32-44',8,'No',0.05,0.15,'',''],
  ['Strike (melee ability)','Player ability','12-18','4-8','24-30','40-56',6,'Yes',0.05,0.15,'',''],
  ['Step (class movement)','Player ability','2','i-frames 10','12','24',0,'Yes',0.02,0.1,'Capstone: blink roll',''],
  ['Surge (super) activation','Player ability','40-60 (invulnerable)','','20','60-80',0,'Yes',0.1,0.2,'Camera cut allowed; 3P only',''],
  ['Resonance','Player ability','30-50','','20-30','50-80',0,'Yes',0.1,0.2,'',''],
  ['Firearm: ADS in','Player firearm','','','','11-23 (ads_ms 180-380)','','No',0,0,'Must equal firearm_classes.csv ads_ms','firearm_classes.csv'],
  ['Firearm: reload','Player firearm','','','','33-168 (reload_s 0.55-2.8)','','No',0.1,0.1,'Mag-out at 40%, mag-in at 75% of clip; must equal reload_s','firearm_classes.csv'],
  ['Firearm: swap','Player firearm','','','','24 out + 24 in','','No',0.05,0.05,'',''],
  ['Firearm: fire (recoil)','Player firearm','','','','6-12 additive','','No',0,0.05,'Procedural recoil from data on top',''],
  ['Locomotion (walk 1.6, jog 4.2, sprint 6.4 m/s)','Locomotion','','','','loops 30-60','','Motion Matching (root motion in DB)',0.2,0.2,'Starts 12-20 f, stops 14-24 f, pivots 20-30 f',''],
  ['Mantle / climb / ledge','Traversal','','','','40-90','','Yes (Motion Warping to ledge)',0.1,0.15,'',''],
  ['Mount / dismount Strider','Traversal','','','','45 / 35','','Yes (warped)',0.1,0.15,'',''],
  ['Interact (door, chest, lever)','Social','','','','45-90','','Yes (warped to interact point)',0.15,0.2,'',''],
  ['Enemy attack: first hit of a string','Enemy','>=12 wind-up pose','2-8','>=18','','','Yes',0.05,0.15,'Visual Bible: every enemy attack wind-up >=12 f','enemy_attacks.csv'],
  ['Enemy attack: combo follow-up','Enemy','>=12','2-8','>=14','','','Yes',0.03,0.15,'Same 12 f minimum as openers (Visual Bible: every enemy attack)','enemy_attacks.csv'],
  ['Boss attack','Boss','12-180 (telegraph lead 0.13-3 s)','up to 600 (beams)','>=10','','','Yes',0.05,0.2,'Every move has a unique wind-up pose; delayed attacks hold a readable pose, never a blend','boss_moves.csv'],
  ['Boss phase transition','Boss','','','','120-300','','Yes (invulnerable)',0.1,0.3,'Readable transition per plan (60-65% HP)','bosses.csv'],
  ['Critical / riposte / backstab (pair)','Paired','','','','90-150','','Yes, synced pair',0.05,0.2,'Victim and attacker authored together in the same take',''],
  ])

# per-set clip counts. 12 melee classes per plan 4.1 and items/melee_classes.csv.
MEL = ['STS Straight Sword','CRV Curved Sword','GRS Greatsword','AXE Axe','HMR Hammer','POL Polearm','FST Fist','DGR Dagger','SHD Shield','TWB Twinblade','GAX Greataxe','GHM Greathammer']
SETS = []
for m in MEL:
    code, name = m.split(' ', 1)
    SETS.append([f'ANM_MEL_{code}', name, 'Player melee', 24, 'Light x3, heavy x2, charged (start, loop, release), running, jump, guard counter, 2 weapon-specific (e.g. thrust), idle, guard, sheathe/draw, crit + riposte (attacker), 2-hand variants of light/heavy; dual-wield and power-stance for 1-hand classes', 'Mocap + keyframe polish', 'plan 4.1 (18-24 each)'])
for f in ['PST Pistol','ARF Auto Rifle','SCT Scout Rifle','SMG Submachine Gun','SHG Shotgun','SNP Sniper Rifle','LCH Launcher','LNC Shard Lance']:
    code, name = f.split(' ', 1)
    SETS.append([f'ANM_FIR_{code}', name, 'Player firearm', 20, '1P: idle, ADS in/out, fire, reload, reload empty, swap in/out, sprint, inspect (9). 3P: idle, aim, fire, reload, reload empty, swap, sprint, hip-fire walk, cover lean, melee bash, crouch (11)', 'Keyframe 1P, mocap 3P', 'A051 (160 total)'])
SETS += [
 ['ANM_LOCO','Locomotion (2 body types)','Player locomotion',60,'Motion Matching DB: walk, jog, sprint, starts, stops, pivots, strafe 8-way locked-on, crouch, slopes, stairs','Mocap (dance card)','A003 (40) expanded for Motion Matching'],
 ['ANM_DEF','Defense','Player defense',22,'Roll x3 loads x4 directions folded to 3 + backstep, block, block hit, block break, parry x2, guard counter shared','Mocap','A004'],
 ['ANM_HIT','Hit reactions','Player hit',24,'Flinch 4 dir, stagger 4 dir, knockdown front/back, get-up x2, launch, fall damage, death x4, respawn at Anchor, crit victim x3','Mocap + stunt','A006'],
 ['ANM_ABIL','Abilities by element','Player ability',60,'Cast, Strike, Step, Surge x 6 elements, plus 12 Resonances, plus 3 subclass variants each for Surge','Mocap + keyframe','A052; weave_abilities.csv, resonances.csv'],
 ['ANM_ART','Weapon Arts','Player ability',40,'One per weapon_arts.csv row','Mocap + keyframe','A045; ANIM_ART_01..40 hooks'],
 ['ANM_TRAV','Traversal','Player traversal',60,'Climb, mantle (3 heights), ledge, swim, ladder, fall/land (3), mount/dismount, ride gaits, glide, vehicle enter/exit per seat, low-gravity set for the Quiet','Mocap + keyframe (Strider)','A053'],
 ['ANM_SOCIAL','Interactions and emotes','Player social',80,'Doors, chests, levers, crafting stations x4, Anchor rest, pickups, 40 emotes','Mocap','A054'],
 ['ANM_STRIDER','Strider mount','Mount',45,'Gaits, double jump, glide, turns, idle, combat stomp, hurt, death','Keyframe (quadruped)','A036'],
 ['ANM_ENEMY','Enemy archetypes (24 sets: 4 factions x 5 roles + 4 leaders)','Enemy',30,'Per set: locomotion 8, attacks 6-10, block/shield 2, hit/stagger/stance-break 4, crit victim 2, death 3, panic/flee 2 (fodder), barks 3','Mocap (humanoid) / keyframe (drones, giants)','A055; enemy_attacks.csv 120 attacks'],
 ['ANM_CREATURE','Creatures (24)','Creature',22,'Per creature: locomotion 6, attacks 3-5, hit 2, death 2, idle/ambient 4, flee 1','Keyframe (some animal reference shoots)','A030; creatures.csv'],
 ['ANM_BOSS','Bosses (40 sets)','Boss',40,'Per boss avg 11 moves (boss_moves.csv 440) + locomotion 6 + phase transitions 2 + stance break/crit 3 + death 1 + intro 1 + part-break reactions 2-4','Mocap (humanoid bosses) + keyframe','A056; boss_moves.csv'],
 ['ANM_NPC','Ambient NPC behaviours','NPC',120,'Work (smith, farm, scribe, trade), sit, talk, eat, sleep, pray, idle variants, crowd reactions','Mocap','A057'],
 ['ANM_CINE','Cinematics and conversations','Cinematic','180 min','Full performance capture (body + face + voice)','Performance capture','A058, plan 5.7'],
 ['ANM_FACE','Facial and lip-sync','Facial','60,000 lines','Hero characters: performance capture; all other lines: audio-driven lip-sync (MetaHuman Animator / Audio2Face class tool), polished for camera close-ups','Pipeline','A059'],
]
MULT = {'ANM_ENEMY': 24, 'ANM_CREATURE': 24, 'ANM_BOSS': 40}
for r in SETS:
    k = MULT.get(r[0], 1); r.insert(4, k); r.insert(5, r[3] * k if isinstance(r[3], int) else r[3])
w('anim_sets.csv', ['set_id','name','category','clips_per_set','set_count','total_clips','contents','method','source'], SETS)
print('gameplay clips total', sum(r[5] for r in SETS if isinstance(r[5], int)))

# ---------------------------------------------------------------- mocap shot list
# est_moves = usable clips; takes = moves x avg takes; minutes = processed; days at ~60 usable moves per day (body) / 6 min per day (performance)
SH = [
 ['MC01','Locomotion dance cards (2 body types)','ANM_LOCO','Body 2 performers',60,4,'Phase 2',2,'Treadmill-free; 30 m volume; slopes and stair rig'],
 ['MC02','Defense, rolls, hit reactions','ANM_DEF ANM_HIT','Body + stunt',46,4,'Phase 2',2,'Pads, crash mats, stunt coordinator; deaths and knockdowns'],
 ['MC03','Prototype melee (straight sword) + prototype enemy','ANM_MEL_STS ANM_ENEMY','Body',44,5,'Phase 2',1,'Prop swords weighted to class weight_min-max'],
 ['MC04','Melee classes, light (dagger, fist, curved, twinblade)','ANM_MEL_DGR FST CRV TWB','Body (martial arts)',96,5,'Phase 4',3,''],
 ['MC05','Melee classes, medium (axe, polearm, shield)','ANM_MEL_AXE POL SHD','Body (HEMA)',72,5,'Phase 4',2,''],
 ['MC06','Melee classes, heavy (greatsword, hammer, greataxe, greathammer)','ANM_MEL_GRS HMR GAX GHM','Body (HEMA, strength)',96,5,'Phase 4',4,'Weighted props so momentum reads'],
 ['MC07','Dual wield, power stance, crit/riposte/backstab pairs','ANM_MEL_*','Body 2 performers',60,5,'Phase 4',2,'Paired takes, victim and attacker together'],
 ['MC08','Firearms 3P (8 classes)','ANM_FIR_*','Body (tactical)',88,4,'Phase 4',2,'1P sets are keyframed; 3P captured with replica weights'],
 ['MC09','Abilities, Surges, Resonances, Weapon Arts','ANM_ABIL ANM_ART','Body (dance/acrobatics)',100,5,'Phase 4',3,'Element-specific pose language from Visual Bible shape rules'],
 ['MC10','Traversal (human side)','ANM_TRAV','Body + stunt',48,4,'Phase 4',2,'Climb rig, ledge rig, low-gravity on wires for the Quiet'],
 ['MC11','Interactions and emotes','ANM_SOCIAL','Body',80,3,'Phase 5',2,''],
 ['MC12','Humanoid enemies: Hollowed (shamble, crawl, swarm)','ANM_ENEMY','Body (movement artist)',60,4,'Phase 4',2,'Crawlers on all fours; panic/flee'],
 ['MC13','Humanoid enemies: Thorn Clans','ANM_ENEMY','Body (martial arts)',60,4,'Phase 4',2,'Berserker chief, twin-axe runner, bone-bow sniper'],
 ['MC14','Humanoid enemies: Choirborn','ANM_ENEMY','Body (dance)',60,4,'Phase 5',2,'Phase duelists, chanting casters, blink starts/ends'],
 ['MC15','Humanoid bosses (Shard-bearers, Citadel, raid humanoids)','ANM_BOSS','Body (stunt + martial arts)',220,5,'Phase 5',6,'About 20 humanoid bosses x 11 moves; the rest keyframed (creatures, machines, colossi)'],
 ['MC16','Ambient NPC behaviours','ANM_NPC','Body 2-4 performers',120,3,'Phase 5',3,'Work props built per region culture'],
 ['MC17','Cinematics: opening, act transitions, 3 endings (45 min)','ANM_CINE','Performance capture (body, face, voice)','45 min',3,'Phase 5',10,'plan 5.7; full cast; virtual camera'],
 ['MC18','Conversations and quest scenes (135 min)','ANM_CINE','Performance capture','135 min',2,'Phase 5',18,'A058 total 180 min; 8 companions and faction leaders prioritized'],
 ['MC19','Facial ROM and hero face capture (Ostra, 8 companions, 5 faction leaders, main villain)','ANM_FACE','Head-mounted camera','15 actors',1,'Phase 4',3,'FACS range-of-motion per actor for the rig'],
 ['MC20','Pickups and retakes (reserve 15%)','ALL','Mixed','15%','','Phase 5-6',8,'Fixes from playtests and Gate 6 balance pass'],
]
w('mocap_shotlist.csv', ['shoot_id','session','sets','capture_type','est_usable_moves','avg_takes_per_move','phase','stage_days','notes'], SH)
print('stage days total', sum(s[7] for s in SH))

# ---------------------------------------------------------------- outsourcing packages
w('outsource_packages.csv',
  ['pkg_id','package','xlsx_rows','vendor_type','units','deliverables','acceptance_check','review_rounds','first_needed','in_house_owner'],
  [
  ['OS01','Environment props (non-hero)','A076','Environment art outsourcer','1,500 props in batches of 100','SRC + FBX, T_ set, UCX_ collision, Nanite enabled, MI from M_Master_Env_Opaque','SfAssetAudit pass; texel density +-15%; turntable in neutral and region lighting','2 (blockout, final)','Phase 4','Lead environment artist'],
  ['OS02','Foliage and rocks per biome','A077','Environment art outsourcer','300 meshes','Photogrammetry-cleaned or sculpted; Nanite; wind setup; PCG-ready pivots','WPO disable distance set; overdraw check in review map','2','Phase 4','Lead environment artist'],
  ['OS03','Weapon models','A039 A041 A042 A044','Hard-surface outsourcer','120 melee + 80 firearm + 60 attachments + 20 catalysts','SK/SM, sockets per asset_budgets.csv, T_ set with _M, 1P LOD0 check','Sockets named exactly; 1P close-up review at 90 FOV; tris within 15-30k','3 (concept fit, high poly, final)','Phase 4','Lead weapons artist'],
  ['OS04','Armor sets','A020 A021','Character outsourcer','90 sets (450 slot meshes) + 120 cosmetics','Skinned to SKEL_Humanoid both body types, cut-away body masks, _M dye mask','Deformation test anim pass (ROM clip), clipping test with all 10 melee + 8 firearm idles','3','Phase 5','Lead character artist'],
  ['OS05','Generic NPC kits','A024','Character outsourcer','300 parts','Modular, shared physics asset, culture by region','Mesh merge test, 40-NPC crowd perf test','2','Phase 5','Lead character artist'],
  ['OS06','Creatures','A030','Creature outsourcer','24 creatures','Mesh + rig + keyframe set (ANM_CREATURE)','Locomotion reads at 30 m; hit zones match weak points','3','Phase 5','Lead creature artist'],
  ['OS07','Animation cleanup (mocap)','A050-A057','Mocap cleanup house','All body shoots MC01-MC16','Solved, retargeted to SKEL_Humanoid, root motion extracted, frame counts per anim_timing_standards.csv','Frame counts match melee_frame_data / enemy_attacks / boss_moves within 1 f; foot sliding < 2 cm','2','Phase 2 onward','Lead animator'],
  ['OS08','Facial and lip-sync','A059','Facial animation vendor','60,000 lines (5 VO languages)','Audio-driven lip-sync for all lines; hand polish for close-ups','Phoneme sync within 2 frames on sample of 2%','1 + spot checks','Phase 5','Cinematic lead'],
  ['OS09','UI icons','UV-068 to UV-080','2D art outsourcer','1,180 icons','512 source PSD/Figma, T_UI_ exports, consistent light direction (top-left 45 deg)','Reads at 64 px; colorblind check; rarity notch rules','2','Phase 4','UI art lead'],
  ['OS10','Boss-specific VFX','A088','VFX outsourcer','200 effects','Niagara systems with scalability per platform, NS_ naming','2,000 GPU particle cap; telegraph colors only from reserved palette','2','Phase 5','Lead VFX artist'],
  ['OS11','Marketing renders and key art','UV-112 A105 A106','Marketing art agency','12 key art + 60 store images','8K source, platform crops','Brand and color rules, no reserved gameplay colors misused','2','Phase 6','Art director'],
  ['OS12','Kit dressing for towns and sites (art pass on gray-box)','A065-A069','Co-development studio','Region-by-region (regions 4-6 parallel)','Final art pass on designer gray-box using in-house kits only','Blind traversal test re-run after art pass (plan 5.1)','3','Phase 5','Region art lead'],
  ])
w('outsource_acceptance_checklist.csv', ['check_id','area','check','tool_or_method','fail_action'], [
  ['QC01','Naming','Asset name follows naming_conventions.csv and matches its hook ID','SfAssetAudit','Reject batch'],
  ['QC02','Folders','Asset sits in folder_structure.csv path','SfAssetAudit','Reject batch'],
  ['QC03','Budget','Tris, LOD count, material count, texture size within asset_budgets.csv','SfAssetAudit','Return asset'],
  ['QC04','Texel density','Within +-15% of class target','Texel density view mode','Return asset'],
  ['QC05','Textures','Suffix, compression, sRGB per texture_rules.csv; albedo range valid','Texture audit commandlet + PBR validation view','Return asset'],
  ['QC06','Materials','Uses an instance of an approved master; no new masters','SfAssetAudit','Return asset'],
  ['QC07','Collision','Simple collision present; complex-as-simple not used','SfAssetAudit','Return asset'],
  ['QC08','Pivot and scale','1 uu = 1 cm, pivot per class rule, +X forward','Import check','Return asset'],
  ['QC09','Color rules','No reserved gameplay color (Visual Bible) at full saturation on environment, armor or cosmetics','Palette checker on _D and _E','Return asset'],
  ['QC10','Style','Salvage-and-worship rule visible; shape language per faction; reviewed in day key light','Art director review','Feedback round'],
  ['QC11','Animation','Frame counts match data within 1 f; root motion and notifies (hit windows, footsteps, VFX) present','Combat frame viewer','Return clip'],
  ['QC12','Legal','No reference traced from source games; source register entry for every photo/scan','Clean-room rule (plan 0.1)','Reject and escalate'],
  ['QC13','Performance','Asset passes in region perf map on base PS5 and Series S','Nightly perf capture','Return asset'],
  ])

# ---------------------------------------------------------------- fonts (all 12 text locales)
# Visual Bible stand-ins: Spectral SC (Ledger headings), IBM Plex Sans (interface), IBM Plex Mono (numerals).
FONT = [
 # role, locale, family, weights (VB weight -> face), license, fallback chain, min px at 4K, line height, notes
 ['Ledger headings','Latin + Cyrillic (en fr de es pt-BR it pl ru)','Spectral SC','500 Medium, 700 Bold','SIL OFL 1.1','Spectral SC > IBM Plex Sans > Source Han Sans','36','1.25','Visual Bible stand-in confirmed as the shipping face'],
 ['Interface text','Latin + Cyrillic','IBM Plex Sans','400 Regular, 500 Medium, 600 SemiBold','SIL OFL 1.1','IBM Plex Sans > Source Han Sans','28 (subtitles 36)','1.35',''],
 ['Numerals','All 12 locales','IBM Plex Mono','400 Regular, 500 Medium','SIL OFL 1.1','IBM Plex Mono > IBM Plex Sans','28','1.2','Digits stay Latin tabular in every locale; CJK unit words fall to the locale body face'],
 ['Ledger headings','ja-JP','Source Han Serif JP','500 -> Medium, 700 -> Bold','SIL OFL 1.1','Source Han Serif JP > IBM Plex Sans JP > Source Han Sans (all regions)','40','1.4','Serif matches Spectral SC; no small caps in CJK, so headings get +2% tracking and 1.1x size instead'],
 ['Interface text','ja-JP','IBM Plex Sans JP','400 Regular, 500 Medium, 600 SemiBold','SIL OFL 1.1','IBM Plex Sans JP > Source Han Sans JP > Source Han Sans KR/SC/TC','32 (subtitles 40)','1.5','Same design family as IBM Plex Sans, so mixed JA/Latin lines match'],
 ['Ledger headings','ko-KR','Source Han Serif KR','500 -> Medium, 700 -> Bold','SIL OFL 1.1','Source Han Serif KR > IBM Plex Sans KR > Source Han Sans (all regions)','40','1.4',''],
 ['Interface text','ko-KR','IBM Plex Sans KR','400 Regular, 500 Medium, 600 SemiBold','SIL OFL 1.1','IBM Plex Sans KR > Source Han Sans KR > Source Han Sans JP/SC/TC','32 (subtitles 40)','1.5','Full 11,172 Hangul syllables kept (player names)'],
 ['Ledger headings','zh-Hans','Source Han Serif SC','500 -> Medium, 700 -> Bold','SIL OFL 1.1','Source Han Serif SC > Source Han Sans SC > Source Han Sans TC/JP/KR','40','1.4',''],
 ['Interface text','zh-Hans','Source Han Sans SC','400 -> Regular, 500 -> Medium, 600 -> Bold','SIL OFL 1.1','Source Han Sans SC > Source Han Sans TC/JP/KR','32 (subtitles 40)','1.5','Source Han Sans has no SemiBold; 600 maps to Bold'],
 ['Ledger headings','zh-Hant','Source Han Serif TC','500 -> Medium, 700 -> Bold','SIL OFL 1.1','Source Han Serif TC > Source Han Sans TC > Source Han Sans SC/JP/KR','40','1.4',''],
 ['Interface text','zh-Hant','Source Han Sans TC','400 -> Regular, 500 -> Medium, 600 -> Bold','SIL OFL 1.1','Source Han Sans TC > Source Han Sans SC/JP/KR','32 (subtitles 40)','1.5',''],
 ['Last-resort fallback','All 12 locales','Source Han Sans (all four regional sets)','Regular','SIL OFL 1.1','End of every chain','n/a','n/a','Covers other players\' names and Shard-note text from players in other regions; lazy-loaded, never resident unless a missing glyph is hit'],
]
w('fonts.csv', ['role','locale','family','weights','license','fallback_chain','min_px_at_4k','line_height','notes'], FONT)
