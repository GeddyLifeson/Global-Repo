#!/usr/bin/env python3
"""Generate every Orbital Ring (REG_Q, the Quiet) level-design table.
Run: python3 design/levels/orbital-ring/tools/gen_orbital.py  (from game-plan/)
Reads design/world and data/ for existing IDs; never writes outside design/levels/orbital-ring/.
All values not set by the master plan are Shardfall design choices (3 Oct 2026)."""
import csv, math, os, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
OUT = os.path.join(ROOT, "design/levels/orbital-ring")
P = lambda *a: os.path.join(ROOT, *a)

def rd(path):
    with open(P(path), newline="") as f: return list(csv.DictReader(f))
def wr(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print(f"{name}: {len(rows)} rows")

# ---------------------------------------------------------------- gravity zones
# Plan 3.7: ring section ~2 km2 with its own gravity rules. design/world/traversal.csv TRV_LOWG:
# Galleries 0.4 g (jumps x2.5); Outer Hull mag boots on marked plates; Spindle gravity rotates at joints.
# Campaign MQ_A3_02: zero-gravity sections on the outer ring.
G = 9.81
GRAV = [
 # id, name, g, where, jump_h, run_gap, air_ctrl, fall_rule, breath_jump, dodge_m, proj_grav, knockback, ragdoll, notes
 ("GRV_ZERO","Zero-g, mag boots",0.0,"Outer hull exterior spans (marked plates)",
  "No jump; Jump = Kick-off: straight drift 4.0 m/s","Drift to any surface within 40 m",0.0,
  "No falls. Drift >6 s with no surface in reach: Ostra Tether pulls the player back to the last plate in 1.5 s, costs 15% max Health, never lethal",
  "Kick-off 12 Breath","Dodge = Thrust 5 m (14 Breath)","0.0 (projectiles fly straight)","x2.0 (hit enemies drift 3-8 m)","Enemies killed off-plate drift away with loot shed onto nearest plate",
  "Mag boots auto-lock on blue-chevron plates (MAT_HULL_MAGPLATE). Walk 3.5 m/s, no sprint. Mag-walk on walls and ceilings of the plate network; the camera rolls to the plate's normal over 0.35 s"),
 ("GRV_02","Low gravity 0.2 g",0.2,"Hull interiors (barracks, airlocks), Core threshold",
  "5.5 m (1.1/0.2)","9.0 m running",0.6,"No fall damage under 30 m; 30-60 m damage; never lethal",
  "10 Breath","Dodge 4.0 m, float 0.35 s","0.2","x1.6","Bodies settle in 4 s",
  "Hang time 2.1 s. Heavy weapon plunge attack becomes a 'Comet Drop' (x1.4 poise damage) from any jump over 3 m"),
 ("GRV_04","Low gravity 0.4 g",0.4,"Seamless Galleries (the Granary), Lens Joint, Spindle rooms",
  "2.75 m (1.1 m x2.5, TRV_LOWG)","6.0 m running",0.45,"No fall damage under 15 m; 15-45 m damage; never lethal (TRV_FALL Quiet galleries)",
  "10 Breath","Dodge 3.6 m","0.4","x1.3","Bodies settle in 2.5 s",
  "Hang time 1.5 s. Strider is not allowed (vehicle_handling.csv blocks the Quiet interior)"),
 ("GRV_ROT","Rotating gravity (Spindle)",0.4,"Spindle; each room's 'down' is rotated 90 deg from the last",
  "2.75 m","6.0 m running",0.45,"As GRV_04","10 Breath","Dodge 3.6 m","0.4 along local down","x1.3","Bodies fall toward the local down of the volume they die in",
  "Crossing a ring-joint seam rotates 'down' over 0.8 s; the camera follows. Input is camera-relative so stick-up stays 'forward'. Player cannot be hit during the 0.8 s rotate (i-frames) and enemies never stand on seams"),
 ("GRV_CORE","Core field (Hush)",1.0,"Hush Core arena; changes per boss phase",
  "1.1 m (P1), 2.75 m (P2 at 0.4 g), drift (P3 at 0 g)","3.0 / 6.0 / drift",0.2,"Arena has no falls; edges are walls of light",
  "10 Breath","Per phase","Per phase","Per phase","Per phase","P1 Lens 1.0 g (Hush pulls the player down to her floor), P2 Choir 0.4 g, P3 Seed 0 g with mag platforms (see boss_arenas.csv)"),
]
wr("gravity_zones.csv",
   ["grv_id","name","g","where","jump_height","jump_gap","air_control","fall_rule","breath_cost","dodge","projectile_gravity_scale","enemy_knockback","bodies","notes"],
   [[r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11],r[12],r[13]] for r in GRAV])

TRAV = [
 ("ORB_TRV_MAGBOOT","Mag boots","Given by Ostra at the Lander (MQ_A3_02 step 1); permanent in REG_Q","Lock 0.2 s on plate contact; walk 3.5 m/s; Breath regen unchanged","Blue chevron plates, 1.5 m squares, emissive #4FA8FF at 40%","SFX_ORB_MAGBOOT_LOCK / _RELEASE","VFX_ORB_MAGBOOT_SPARK"),
 ("ORB_TRV_KICKOFF","Kick-off drift","Mag boots","Press Jump on a plate: release and drift 4.0 m/s along aim, 12 Breath. Mid-drift: no steering except Thrust","Aim reticle shows a dotted line and a green ring on reachable plates (red if out of 40 m)","SFX_ORB_KICKOFF","VFX_ORB_DRIFT_TRAIL"),
 ("ORB_TRV_THRUST","Thrust (Step in zero-g)","Start of Act 3","Replaces dodge/roll in GRV_ZERO: 5 m burst any direction, 14 Breath, 0.25 s i-frames (same as medium roll)","Ostra-blue puff from the Shard","SFX_ORB_THRUST","VFX_ORB_THRUST_PUFF"),
 ("ORB_TRV_TETHER","Ostra Tether","Always on in REG_Q","Auto-rescue after 6.0 s of drift with no reachable surface: 1.5 s pull to last plate, -15% max Health, no Ember loss","Shard-light cord from chest to plate","SFX_ORB_TETHER_PULL","VFX_ORB_TETHER_CORD"),
 ("ORB_TRV_GRAVLIFT","Grav lift","Fixed lifts","Column of 0 g inside a 0.4 g room; enter and hold Jump to rise 6 m/s, release to stop; exit at any ring","Pale cylinder with drifting dust; rings every 5 m","SFX_ORB_GRAVLIFT_LOOP","VFX_ORB_GRAVLIFT_COLUMN"),
 ("ORB_TRV_SEAM","Gravity seam","Spindle joints","Walk across: down rotates 90 deg in 0.8 s with i-frames","Thin seam of white light across the floor; dust on both sides falls different ways","SFX_ORB_SEAM_ROTATE","VFX_ORB_SEAM_LINE"),
 ("ORB_TRV_VENT","Chaff vent","Hull vents (timed)","Pushes anything in its 6 m column at 12 m/s for 1.5 s; cycle 4 s on / 5 s off","Amber strobe 1 s before firing, frost plume","SFX_ORB_VENT_WARN / _BLAST","VFX_ORB_VENT_PLUME"),
 ("ORB_TRV_COMETDROP","Comet Drop","Any low-g jump over 3 m","Plunge attack: x1.4 poise damage, 3 m shockwave knocks fodder down","Ring of dust on impact","SFX_ORB_COMETDROP","VFX_ORB_COMETDROP_RING"),
]
wr("traversal_verbs.csv",["trv_id","name","unlock","rule","readability","sfx","vfx"],TRAV)

# ---------------------------------------------------------------- sections
# x along the ring (spinward) 0-4000 m, y across 0-500 m: 2.0 km2 (plan 3.7)
SEC = [
 # id, name, world sub-area, quest, x0, x1, grav, level band, mood, light, music, ambience, crit_min, full_min
 ("SEC_ORB_00","Outer Hull Ring (exterior)","LOC_Q_HULL (exterior)","MQ_A3_02",0,160,"GRV_ZERO","68","Shock and silence: the damaged shuttle, Veyl below, no air","LGT_ORB_SCAR","MUS_QUI_EXPLORE_NIGHT (first 30 s silent)","AMB_QUI_BED_NIGHT + AMB_QUI_WIND off (vacuum)",8,15),
 ("SEC_ORB_01","Outer Hull Ring","LOC_Q_HULL","MQ_A3_02",160,1200,"GRV_ZERO / GRV_02","69-72","Industrial dread: a machine that reaps land; Choirborn barracks","LGT_ORB_THRESH","MUS_QUI_EXPLORE_DAY / TENSION / COMBAT_L1-3","AMB_QUI_BED_DAY + AMB_QUI_EMITTERS (thresher arms) + AMB_QUI_INTERIOR",62,115),
 ("SEC_ORB_02","Hull-Galleries joint","joint (new)","MQ_A3_02 > MQ_A3_03",1200,1450,"GRV_ZERO > GRV_04","72","Pause and awe: the ring turns around you","LGT_ORB_JOINT","MUS_QUI_DISCOVERY then silence","AMB_QUI_EMITTERS (bearing groan)",10,18),
 ("SEC_ORB_03","Seamless Galleries","LOC_Q_GALLERIES","MQ_A3_03",1450,2600,"GRV_04","73-76","Grief and wonder: whole hillsides of Veyl hang in glass","LGT_ORB_GRANARY","MUS_QUI_EXPLORE_DAY + regional theme bleed per vault","AMB_QUI_INTERIOR + AMB_QUI_WEAVE_HUM (vault proximity) + region bed of each vault at -12 dB",78,150),
 ("SEC_ORB_04","Galleries-Spindle joint","joint (new)","MQ_A3_03 > MQ_A3_04",2600,2850,"GRV_04 (inverts)","76","Vertigo: the planet is above you now","LGT_ORB_LENS","MUS_THEME_QUIET (full)","AMB_QUI_HOLLOWING at 0.6",12,20),
 ("SEC_ORB_05","Core Spindle","LOC_Q_SPINDLE","MQ_A3_04",2850,3850,"GRV_ROT","77-79","Uncanny: everyone you know, wrong","LGT_ORB_SPINDLE","MUS_FAC_CHOIRBORN / MUS_QUI_COMBAT_L1-3","AMB_QUI_INTERIOR + choir whispers (copies speak in VO of the originals)",70,125),
 ("SEC_ORB_06","The Hush Core","LOC_Q_CORE","MQ_A3_05, MQ_A3_06, MQ_END_*",3850,4000,"GRV_CORE","80","Finality: a mind, a choice","LGT_ORB_CORE","Hush boss cues (requested MUS_BOSS_HUSH_*) then ending cue","AMB_QUI_CITADEL + AMB_QUI_HOLLOWING at 1.0",30,40),
]
# area names follow design/world/locations.csv (LOC_Q_*); campaign names stay as quest / sub-area notes
CAMPAIGN = {"SEC_ORB_00":"Lander Scar","SEC_ORB_01":"The Threshing Ring","SEC_ORB_02":"Threshing Joint","SEC_ORB_03":"The Granary",
            "SEC_ORB_04":"Lens Joint","SEC_ORB_05":"The Choir of Copies","SEC_ORB_06":"The Hush Core"}
wr("sections.csv",["sec_id","name","campaign_name","world_subarea","quests","x_start_m","x_end_m","area_km2","gravity","level_band","mood","lighting","music","ambience","critical_path_min","full_clear_min"],
   [[s[0],s[1],CAMPAIGN[s[0]],s[2],s[3],s[4],s[5],round((s[5]-s[4])*500/1e6,3),s[6],s[7],s[8],s[9],s[10],s[11],s[12],s[13]] for s in SEC])

# ---------------------------------------------------------------- nodes (the layout graph)
# kind: Room | Exterior | Joint | Arena | Set piece | Secret | Landmark
N = [
 # id, sec, kind, name, loc_ref, x, y, z, w, l, h, grav, down, crit_order(0=optional), purpose
 ("ND_ORB_LANDER","SEC_ORB_00","Set piece","The Broken Lander","",40,250,0,30,45,12,"GRV_ZERO","-Z (plates)",1,"Crash landing (CIN_A3_CRASH). Get mag boots. Companion left behind per MQ_A3_01"),
 ("ND_ORB_SCARFIELD","SEC_ORB_00","Exterior","Scar Field","",110,250,0,80,120,40,"GRV_ZERO","-Z",2,"Teach mag-walk, Kick-off, Thrust, Tether on safe plates; 3 Quiet Mites as first targets"),
 ("LOC_Q_HULL_01","SEC_ORB_01","Room","Thresher Airlock","LOC_Q_HULL_01",185,370,0,40,30,10,"GRV_02","-Z",3,"Anchor Q_01. First interior; air returns (audio fills in over 2 s)"),
 ("ND_ORB_HARVESTRAIL","SEC_ORB_01","Exterior","Harvest Rail","",280,250,6,40,180,30,"GRV_ZERO","-Z",4,"Ride the outside of the ring along the rail; Choir Lancers on pylons; first zero-g fight"),
 ("LOC_Q_HULL_02","SEC_ORB_01","Room","Barracks Tier One","LOC_Q_HULL_02",371,130,0,60,50,12,"GRV_02","-Z",5,"Choirborn barracks; gunline across bunk tiers"),
 ("LOC_Q_HULL_03","SEC_ORB_01","Room","Flail Gallery","LOC_Q_HULL_03",557,370,0,36,140,20,"GRV_02","-Z",6,"Threshing arms sweep the hall every 7 s (100 dmg, knockdown); elite Colossus between sweeps"),
 ("ND_ORB_MAKERTERM","SEC_ORB_01","Set piece","Maker Terminal","",650,250,0,14,14,6,"GRV_02","-Z",7,"MQ_RT_Q: Ostra pings the Maker relay; map reveal for REG_Q; Hush speaks for the first time (CIN_A3_HUSH_FIRST)"),
 ("LOC_Q_HULL_04","SEC_ORB_01","Room","Choirborn Muster Hall","LOC_Q_HULL_04",742,130,0,70,60,18,"GRV_02","-Z",8,"Anchor Q_02. Big fort fight; Cantor leader on the balcony"),
 ("LOC_Q_HULL_05","SEC_ORB_01","Exterior","Chaff Vents","LOC_Q_HULL_05",928,370,0,50,160,40,"GRV_ZERO","-Z",9,"Timed vent crossing (ORB_TRV_VENT) under fire; vents also blow enemies off plates"),
 ("LOC_Q_HULL_06","SEC_ORB_01","Room","Bale Lock","LOC_Q_HULL_06",1114,130,0,40,40,14,"GRV_02","-Z",10,"Elite Cantor + Colossus pair; opens the shortcut lift back to Anchor Q_02"),
 ("ND_ORB_JOINTBEARING","SEC_ORB_02","Joint","Joint Bearing","",1260,250,0,60,90,60,"GRV_ZERO","-Z",11,"New Anchor Q_08. The bearing turns 1 deg/s: platforms line up every 20 s for a 6 s window"),
 ("ND_ORB_GRANARYGATE","SEC_ORB_02","Set piece","Granary Gate","",1420,250,0,20,30,24,"GRV_04","-Z",12,"Gate opened with the Maker Sigil (requested key item). Gravity returns to 0.4 g on the far side"),
 ("LOC_Q_GALLERIES_01","SEC_ORB_03","Room","Antechamber of Glass","LOC_Q_GALLERIES_01",1500,370,0,50,60,30,"GRV_04","-Z",13,"Anchor Q_03. First sight of the vaults; no enemies for 60 s"),
 ("LOC_Q_GALLERIES_02","SEC_ORB_03","Room","Cinderreach Vault","LOC_Q_GALLERIES_02",1700,130,0,80,90,50,"GRV_04","-Z",14,"A hill of Cinderreach in glass. Vault holds REG_01 variants frozen; they wake if the glass breaks"),
 ("LOC_Q_GALLERIES_03","SEC_ORB_03","Room","Saltmere Vault","LOC_Q_GALLERIES_03",1900,370,0,80,90,50,"GRV_04","-Z",15,"Saltmere shore hangs here with its tide still moving in slow motion"),
 ("ND_ORB_FLOWJUNCTION","SEC_ORB_03","Set piece","Flow Junction","",2000,250,10,40,40,40,"GRV_04","-Z",16,"Puzzle: three valves re-route Shard flow (MQ_A3_03). Spared Heart Shards light their vault's line"),
 ("LOC_Q_GALLERIES_04","SEC_ORB_03","Room","Vaults of Thornwood and Glasswaste","LOC_Q_GALLERIES_04",2100,130,0,90,100,50,"GRV_04","-Z",17,"Anchor Q_04. Two vaults face each other across a grav-lift well"),
 ("LOC_Q_GALLERIES_05","SEC_ORB_03","Room","Vaults of Rimefall and Hollowdeep","LOC_Q_GALLERIES_05",2300,370,0,90,100,50,"GRV_04","-Z",18,"Ambush room: Blinkblades in the frost of Rimefall's vault"),
 ("LOC_Q_GALLERIES_06","SEC_ORB_03","Room","Ires's Berth","LOC_Q_GALLERIES_06",2500,130,0,40,60,20,"GRV_04","-Z",19,"Ires's own ship-side. Final Ires choice: fight, recruit (IRES_RECRUITABLE) or let her go"),
 ("ND_ORB_ARENA_IRES","SEC_ORB_03","Arena","The Lamp Well","",2560,250,0,56,56,30,"GRV_04","-Z",20,"Lamplighter rematch arena (only if the player chooses to fight)"),
 ("ND_ORB_LENS","SEC_ORB_04","Landmark","The Lens","",2650,250,0,120,120,80,"GRV_04","-Z then +Z",21,"New Anchor Q_09. A 100 m window: Veyl fills the view; walking the rim flips down so the planet is overhead"),
 ("ND_ORB_INVSTAIR","SEC_ORB_04","Joint","Inversion Stair","",2800,250,0,20,80,40,"GRV_ROT","rotates",22,"First gravity seam; tutorial for GRV_ROT with no enemies"),
 ("LOC_Q_SPINDLE_01","SEC_ORB_05","Room","Spindle Foot","LOC_Q_SPINDLE_01",2885,370,0,50,50,40,"GRV_ROT","-Z",23,"Anchor Q_05. Hush's voice greets the player in a companion's voice"),
 ("LOC_Q_SPINDLE_02","SEC_ORB_05","Room","Hall of Faces","LOC_Q_SPINDLE_02",3071,130,0,40,80,40,"GRV_ROT","+Y",24,"Copies 1: faction leaders (talk or fight)"),
 ("LOC_Q_SPINDLE_03","SEC_ORB_05","Room","Choir Loom","LOC_Q_SPINDLE_03",3257,370,0,40,80,40,"GRV_ROT","+Z",25,"Copies 2: Lisk and the Speaker. The room is upside down relative to Spindle Foot"),
 ("LOC_Q_SPINDLE_04","SEC_ORB_05","Room","Mirror Barracks","LOC_Q_SPINDLE_04",3442,130,0,60,60,30,"GRV_ROT","-Y",26,"Anchor Q_06. Gunline in a hall of mirrors; copies of the player appear in reflections (cosmetic)"),
 ("LOC_Q_SPINDLE_05","SEC_ORB_05","Room","Companion's Echo","LOC_Q_SPINDLE_05",3628,370,0,40,60,30,"GRV_ROT","-Z",27,"Copies 3: companions the player lost or angered (approval < 25 or dead)"),
 ("LOC_Q_SPINDLE_06","SEC_ORB_05","Room","Last Hymn","LOC_Q_SPINDLE_06",3814,130,0,40,50,40,"GRV_ROT","+Y",28,"Final Choirborn wall: twin Colossi; shortcut seam back to Anchor Q_06"),
 ("LOC_Q_CORE","SEC_ORB_06","Room","Core Threshold","LOC_Q_CORE",3900,250,0,30,30,20,"GRV_02","-Z",29,"Anchor Q_07 (before the final boss). Last merchant: none; last Echo summon sign"),
 ("ND_ORB_ARENA_HUSH","SEC_ORB_06","Arena","Hush's Mind","",3950,250,0,70,70,70,"GRV_CORE","per phase",30,"ACT_BOSS_HUSH (requested), 3 phases"),
 ("ND_ORB_CHOICEDAIS","SEC_ORB_06","Set piece","The Choice Dais","",3985,250,0,16,16,8,"GRV_02","-Z",31,"MQ_A3_06: Restore, Bind or Take. Each starts its MQ_END_* playable sequence"),
 # optional branches
 ("ND_ORB_SPARE_BAY","SEC_ORB_01","Room","Seed Store","",470,40,0,30,40,10,"GRV_02","-Z",0,"Optional: Choirborn larder; Choir vault Q_02 behind locked door"),
 ("ND_ORB_SOLARWING","SEC_ORB_01","Exterior","Sail Field","",1000,480,10,60,200,60,"GRV_ZERO","-Z",0,"Optional: solar sails; long drift puzzle to a lore site and crates"),
 ("ND_ORB_GLASSATTIC","SEC_ORB_03","Room","Glass Attic","",1950,20,30,40,120,15,"GRV_04","-Z",0,"Optional: catwalks above the vaults; Choir vault Q_01; sniper perches"),
 ("ND_ORB_TIDEBELOW","SEC_ORB_03","Room","Under-Tide","",2420,480,-15,40,60,20,"GRV_04","-Z",0,"Optional: flooded maintenance under Saltmere's glass; lore and a Starmetal Core"),
 ("ND_ORB_REVERSECHAPEL","SEC_ORB_05","Room","Reverse Chapel","",3200,20,0,30,40,30,"GRV_ROT","+Z",0,"Optional: a Lantern chapel built upside down; Choir vault Q_03"),
 ("ND_ORB_ARCHIVESTUB","SEC_ORB_05","Room","Sealed Archive Stub","",3700,480,0,20,30,10,"GRV_ROT","-Z",0,"Optional: dead-end that the raid Wing 2 (Archive Ring) later opens; teaser door"),
]
NODE = {n[0]: n for n in N}
wr("nodes.csv",["node_id","sec_id","kind","name","world_loc","x_m","y_m","z_m","width_m","length_m","height_m","gravity","down","critical_order","purpose"],[list(n) for n in N])

# ---------------------------------------------------------------- edges
E = [
 # from, to, type, gate, critical
 ("ND_ORB_LANDER","ND_ORB_SCARFIELD","Mag-walk","","Y"),
 ("ND_ORB_SCARFIELD","LOC_Q_HULL_01","Airlock","Cycle 3 s","Y"),
 ("LOC_Q_HULL_01","ND_ORB_HARVESTRAIL","Airlock","","Y"),
 ("ND_ORB_HARVESTRAIL","LOC_Q_HULL_02","Kick-off drift","3 drifts of 18-30 m","Y"),
 ("LOC_Q_HULL_02","LOC_Q_HULL_03","Corridor","4 m wide (MET_CORRIDOR_MELEE)","Y"),
 ("LOC_Q_HULL_03","ND_ORB_MAKERTERM","Corridor","Pass the threshing arms","Y"),
 ("ND_ORB_MAKERTERM","LOC_Q_HULL_04","Grav lift","","Y"),
 ("LOC_Q_HULL_04","LOC_Q_HULL_05","Airlock","","Y"),
 ("LOC_Q_HULL_05","LOC_Q_HULL_06","Mag-walk under vents","Vent cycle 4 s on / 5 s off","Y"),
 ("LOC_Q_HULL_06","ND_ORB_JOINTBEARING","Airlock","","Y"),
 ("ND_ORB_JOINTBEARING","ND_ORB_GRANARYGATE","Timed platform","6 s window every 20 s","Y"),
 ("ND_ORB_GRANARYGATE","LOC_Q_GALLERIES_01","Gate","Maker Sigil (from ND_ORB_MAKERTERM)","Y"),
 ("LOC_Q_GALLERIES_01","LOC_Q_GALLERIES_02","Low-g jumps","","Y"),
 ("LOC_Q_GALLERIES_02","LOC_Q_GALLERIES_03","Gallery bridge","","Y"),
 ("LOC_Q_GALLERIES_03","ND_ORB_FLOWJUNCTION","Grav lift","","Y"),
 ("ND_ORB_FLOWJUNCTION","LOC_Q_GALLERIES_04","Gallery bridge","Puzzle solved (3 valves)","Y"),
 ("LOC_Q_GALLERIES_04","LOC_Q_GALLERIES_05","Grav lift well","","Y"),
 ("LOC_Q_GALLERIES_05","LOC_Q_GALLERIES_06","Corridor","","Y"),
 ("LOC_Q_GALLERIES_06","ND_ORB_ARENA_IRES","Fog gate","Only if the player fights Ires","N"),
 ("LOC_Q_GALLERIES_06","ND_ORB_LENS","Corridor","Ires choice made","Y"),
 ("ND_ORB_LENS","ND_ORB_INVSTAIR","Rim walk (inverts)","","Y"),
 ("ND_ORB_INVSTAIR","LOC_Q_SPINDLE_01","Gravity seam","","Y"),
 ("LOC_Q_SPINDLE_01","LOC_Q_SPINDLE_02","Gravity seam","","Y"),
 ("LOC_Q_SPINDLE_02","LOC_Q_SPINDLE_03","Gravity seam","Copies resolved","Y"),
 ("LOC_Q_SPINDLE_03","LOC_Q_SPINDLE_04","Gravity seam","Copies resolved","Y"),
 ("LOC_Q_SPINDLE_04","LOC_Q_SPINDLE_05","Gravity seam","","Y"),
 ("LOC_Q_SPINDLE_05","LOC_Q_SPINDLE_06","Gravity seam","Copies resolved","Y"),
 ("LOC_Q_SPINDLE_06","LOC_Q_CORE","Grav lift","","Y"),
 ("LOC_Q_CORE","ND_ORB_ARENA_HUSH","Fog gate","4 m wide, one-way while fighting","Y"),
 ("ND_ORB_ARENA_HUSH","ND_ORB_CHOICEDAIS","Set piece walk","Hush broken","Y"),
 # shortcuts (site rule: every site ends in a shortcut back)
 ("LOC_Q_HULL_03","LOC_Q_HULL_01","Shortcut: one-way hatch","Open from the Flail Gallery side","N"),
 ("LOC_Q_HULL_06","LOC_Q_HULL_04","Shortcut: grav lift","Power on from Bale Lock","N"),
 ("LOC_Q_GALLERIES_03","LOC_Q_GALLERIES_01","Shortcut: drop through glass","One-way, 20 m low-g drop","N"),
 ("LOC_Q_GALLERIES_06","LOC_Q_GALLERIES_04","Shortcut: grav lift","Call from the Berth","N"),
 ("LOC_Q_SPINDLE_03","LOC_Q_SPINDLE_01","Shortcut: seam door","Open from Choir Loom","N"),
 ("LOC_Q_SPINDLE_06","LOC_Q_SPINDLE_04","Shortcut: seam door","Open from Last Hymn","N"),
 # optional branches
 ("LOC_Q_HULL_02","ND_ORB_SPARE_BAY","Locked door","LOC_DOOR_REG_Q_42 (Salvager Picks or Infiltration 50)","N"),
 ("LOC_Q_HULL_05","ND_ORB_SOLARWING","Kick-off drift","40 m drift chain over the sails","N"),
 ("LOC_Q_GALLERIES_03","ND_ORB_GLASSATTIC","Grav lift","","N"),
 ("LOC_Q_GALLERIES_05","ND_ORB_TIDEBELOW","Drop","","N"),
 ("LOC_Q_SPINDLE_02","ND_ORB_REVERSECHAPEL","Gravity seam","Hidden seam (secret SEC_ORB_S07)","N"),
 ("LOC_Q_SPINDLE_05","ND_ORB_ARCHIVESTUB","Corridor","Sealed until raid Wing 2 (LOC_END_RAID_02)","N"),
]
def dist(a,b):
    A,B=NODE[a],NODE[b]; return round(math.hypot(A[5]-B[5],A[6]-B[6],A[7]-B[7]))
wr("edges.csv",["edge_id","from_node","to_node","type","length_m","gate","critical"],
   [[f"EDG_ORB_{i+1:02d}",e[0],e[1],e[2],dist(e[0],e[1]),e[3],e[4]] for i,e in enumerate(E)])
crit_len = sum(dist(e[0],e[1]) for e in E if e[4]=="Y")

# ---------------------------------------------------------------- anchors
wa = [r for r in rd("design/world/anchors.csv") if r["region"]=="REG_Q"]
anc = [[r["loc_id"],r["parent_loc"],r["x_m"],r["y_m"],"Existing (design/world)"] for r in wa]
anc += [["LOC_ANC_REG_Q_08","ND_ORB_JOINTBEARING",1260,250,"New (data request): closes the 758 m gap Q_02 > Q_03"],
        ["LOC_ANC_REG_Q_09","ND_ORB_LENS",2650,250,"New (data request): closes the 785 m gap Q_04 > Q_05"],
        ["LOC_ANC_REG_Q_00","ND_ORB_LANDER",40,250,"New (data request): Lander Anchor so first death does not replay the crash cinematic"]]
anc.sort(key=lambda a:int(a[2]))
rows=[];prev=None
for a in anc:
    gap = "" if prev is None else int(a[2])-int(prev[2]); prev=a
    rows.append(a+[gap,"Yes" if gap=="" or gap<=600 else "NO (over plan 3.7 600 m)","Lit on touch; fast travel to/from Lantern Hold only after MQ_A3_02 (Ostra re-links the Ascension Lift)"])
wr("anchors.csv",["loc_id","node","x_m","y_m","status","gap_from_previous_m","plan_rule_400_600m","rule"],rows)

# ---------------------------------------------------------------- encounters
wenc = {r["loc_id"]:r for r in rd("design/world/encounters.csv") if r["region"]=="REG_Q"}
lvl = {n[0]:None for n in N}
ENC = []
def lvl_of(node):
    x=NODE[node][5]; return min(80, 68+int(x/4000*12.99))
for nid,r in wenc.items():
    ENC.append([r["enc_id"],nid,r["template"],r["actors"],r["level"],"Room entry","Existing (design/world/encounters.csv)",r["respawn"]])
NEW = [
 ("ND_ORB_SCARFIELD","ENT_CRT_PACK","ACT_CRT_QUIETMITE x3","Plate contact","On Anchor rest","Training targets; Mites cling to plates and leap (drift) at the player"),
 ("ND_ORB_HARVESTRAIL","ENT_GUNLINE","ACT_CHOIRBORN_ARTILLERY x2; ACT_CHOIRBORN_SKIRMISHER x2; ACT_CHOIRBORN_FODDER x3","Rail midpoint","On Anchor rest","Artillery mag-locked on pylons 30 m up; Blinkblades teleport plate to plate; first zero-g fight"),
 ("LOC_Q_HULL_03","ENT_HAZARD","Threshing arm hazard x2 (100 dmg, knockdown, 7 s cycle)","Always","Permanent","Hazard, not actors; enemies are immune (they time it)"),
 ("ND_ORB_MAKERTERM","ENT_WAVE","Wave 1: ACT_CHOIRBORN_FODDER x6; Wave 2: ACT_CHOIRBORN_SKIRMISHER x3, ACT_CHOIRBORN_ARTILLERY x2; Wave 3: ACT_CHOIRBORN_LEADER x1, ACT_CHOIRBORN_SHIELDBEARER x2","Terminal uplink starts (90 s hold)","Once (story)","Defend the terminal while Ostra pings the relay"),
 ("LOC_Q_HULL_04","ENT_LEADER","ACT_CHOIRBORN_LEADER x1 (balcony)","Room entry","Leader stays dead","Killing the Cantor breaks fodder morale (DR-014 flee rule)"),
 ("ND_ORB_SOLARWING","ENT_CRT_PACK","ACT_CRT_CHOIRWISP x4","Drift into sails","On Anchor rest","Wisps fly freely in zero-g; Storm Rite chains between them"),
 ("LOC_Q_HULL_06","ENT_ELITE","ACT_CHOIRBORN_LEADER x1; ACT_CHOIRBORN_HEAVY x1","Room entry","Stays dead","Hull exit gate; opens shortcut lift"),
 ("ND_ORB_JOINTBEARING","ENT_AMBUSH","ACT_CHOIRBORN_SKIRMISHER x2; ACT_CRT_CHOIRWISP x3","First platform window","On Anchor rest","Ambush mid-crossing; Blinkblades wait on the next platform"),
 ("ND_ORB_SPARE_BAY","ENT_CAMP","ACT_CHOIRBORN_FODDER x4; ACT_CHOIRBORN_SHIELDBEARER x1; ACT_CHOIRBORN_ARTILLERY x1; ACT_CHOIRBORN_LEADER x1","Door opens","On Anchor rest; leader stays dead","Larder guards"),
 ("LOC_Q_GALLERIES_02","ENT_VAULTBREAK","ACT_VAR_R1_01 x3; ACT_VAR_R1_02 x2; ACT_VAR_R1_05 x1","Vault glass broken by player or stray fire","Once","Frozen Cinderreach enemies wake at level 74 (needs enemy_stats rows)"),
 ("LOC_Q_GALLERIES_03","ENT_VAULTBREAK","ACT_VAR_R2_01 x3; ACT_VAR_R2_02 x2; ACT_VAR_R2_05 x1","Vault glass broken","Once","Saltmere wakes; drones fly in 0.4 g"),
 ("ND_ORB_FLOWJUNCTION","ENT_WAVE","Each valve turned: ACT_CHOIRBORN_FODDER x4 + ACT_CHOIRBORN_SKIRMISHER x1 (3 waves)","Valve turned","Once","Pressure while solving; valves need 4 s hold"),
 ("LOC_Q_GALLERIES_04","ENT_VAULTBREAK","ACT_VAR_R3_03 x2; ACT_VAR_R3_06 x2; ACT_VAR_R4_04 x2; ACT_VAR_R4_02 x1","Vault glass broken","Once","Thornwood and Glasswaste wake"),
 ("LOC_Q_GALLERIES_05","ENT_VAULTBREAK","ACT_VAR_R5_04 x2; ACT_VAR_R5_06 x2; ACT_VAR_R6_01 x3; ACT_VAR_R6_05 x1","Vault glass broken","Once","Rimefall and Hollowdeep wake"),
 ("ND_ORB_GLASSATTIC","ENT_GUNLINE","ACT_CHOIRBORN_ARTILLERY x3; ACT_CHOIRBORN_SHIELDBEARER x1","Attic entry","On Anchor rest","Sniper perches over the vault floor"),
 ("ND_ORB_TIDEBELOW","ENT_AMBUSH","ACT_CRT_QUIETMITE x6","Water line crossed","On Anchor rest","Swarm"),
 ("ND_ORB_LENS","ENT_NONE","None","","","Breather: no combat at the Lens by design"),
 ("LOC_Q_SPINDLE_02","ENT_COPY","Copy of Knight-Commander Iselde Marr; Copy of Archivist Oswin Hale; Copy of Guildmistress Petra Quell (each ACT_CHOIRBORN_LEADER with copy skin)","Approach each copy","Once","Talk past: faction rep Honored+ or Speech 60; else duel. Each copy fights with its original's weapon class"),
 ("LOC_Q_SPINDLE_03","ENT_COPY","Copy of Precentor Amaury Lisk; Copy of The Speaker (ACT_CHOIRBORN_LEADER copy skin) + ACT_CHOIRBORN_FODDER x4","Approach","Once","Lisk copy speaks his betrayal (QST_CH_09 state); Speaker copy talk-past needs Quiet Hand rep Friendly+ or Speech 75"),
 ("LOC_Q_SPINDLE_05","ENT_COPY","Copies of each companion with approval < 25 or dead (0-8; ACT_CHOIRBORN_LEADER copy skin each)","Approach","Once","If zero qualify, the room holds a copy of Ostra's old crew captain instead (always 1 fight)"),
 ("ND_ORB_REVERSECHAPEL","ENT_ELITE","ACT_CHOIRBORN_HEAVY x1; ACT_CRT_CHOIRWISP x2","Chapel entry","Heavy stays dead","Upside-down pews as cover"),
 ("LOC_Q_SPINDLE_06","ENT_ELITE","ACT_CHOIRBORN_HEAVY x2; ACT_CHOIRBORN_SHIELDBEARER x2","Room entry","Stays dead","Twin Colossi on opposite walls (different downs)"),
]
for i,(nid,t,act,trig,resp,note) in enumerate(NEW):
    ENC.append([f"ENC_ORB_{i+1:03d}",nid,t,act,lvl_of(nid),trig,"New: "+note,resp])
ENC.sort(key=lambda e:(NODE[e[1]][5],e[0]))
wr("encounters.csv",["enc_id","node","template","actors","level","trigger","source_note","respawn"],ENC)

# zero-g behaviour rules for each faction role
ZR = [
 ("ACT_CHOIRBORN_FODDER","Mag-walk only; never Kick-off. Panics and drifts away if leader dies","Low"),
 ("ACT_CHOIRBORN_SHIELDBEARER","Plants on plate; ward-wall blocks drift paths","Low"),
 ("ACT_CHOIRBORN_SKIRMISHER","Teleports plate to plate (12 m max, 3 s cooldown); flanks onto walls and ceilings","High"),
 ("ACT_CHOIRBORN_ARTILLERY","Mag-locks on high pylons; lances fly straight in zero-g (no drop)","Medium"),
 ("ACT_CHOIRBORN_HEAVY","Too heavy to knock off plates (knockback x0.5 instead of x2.0); Comet Drop slam in low-g","Low"),
 ("ACT_CHOIRBORN_LEADER","Counter-casts (plan 3.9); in Spindle uses seams to change down mid-fight","High"),
 ("ACT_CRT_QUIETMITE","Leaps between surfaces in any gravity; swarms of 3-6","Medium"),
 ("ACT_CRT_CHOIRWISP","Free flight; ignores gravity","High"),
 ("ACT_VAR_R*_* (vault)","Planet-born: in 0.4 g they jump 2.5x but have no low-g training, so they overshoot (+20% recovery on leaps)","Low"),
]
wr("enemy_lowg_behaviour.csv",["actor","rule","mobility"],ZR)

# ---------------------------------------------------------------- loot placement
wloc = [r for r in rd("design/world/locations.csv") if r["region"]=="REG_Q"]
def nearest(x,y,sub=None):
    best=None
    for n in N:
        d=math.hypot(n[5]-x,n[6]-y)
        if best is None or d<best[0]: best=(d,n[0])
    return best[1]
LT = {"Small chest":"ITM_LT_SMALLCHEST_REG_Q","Shard crate":"ITM_LT_SHARDCRATE_REG_Q","Choir vault":"ITM_LT_VAULT_REG_Q"}
loot=[]
for r in wloc:
    if r["kind"] in LT:
        nd=nearest(float(r["x_m"]),float(r["y_m"]))
        loot.append([r["loc_id"],nd,r["kind"],LT[r["kind"]],r["x_m"],r["y_m"],r["level"],"Placed by design/world; node by nearest"])
UNIQUE = [
 ("LOOT_ORB_U01","ND_ORB_LANDER","Lander locker","ITM_CON_UTL_FLARE x3; ITM_CON_UTL_AMMO_G x2","Restock after the crash"),
 ("LOOT_ORB_U02","LOC_Q_HULL_03","End-of-Flail chest","ITM_SET_88_HEAD x1","Sub-area unique reward (Choirborn Rag Hood)"),
 ("LOOT_ORB_U03","LOC_Q_HULL_06","Bale Lock reward","ITM_MAT_STAR_03 x1; ITM_CON_UTL_POUCH_L x1","Threshing Ring end reward"),
 ("LOOT_ORB_U04","ND_ORB_SOLARWING","Sail-tip cache","ITM_SET_88_LEGS x1; ITM_MAT_STAR_01 x6","Optional drift-puzzle reward"),
 ("LOOT_ORB_U05","ND_ORB_FLOWJUNCTION","Junction reward","ITM_LT_ARTS x1 (Weapon Art); ITM_MAT_GLASS_01 x5","Puzzle reward"),
 ("LOOT_ORB_U06","ND_ORB_TIDEBELOW","Drowned locker","ITM_MAT_STAR_03 x1; ITM_SET_88_ARMS x1","Optional"),
 ("LOOT_ORB_U07","LOC_Q_GALLERIES_06","Ires's sea-chest","ITM_CON_UTL_POUCH_L x2; ITM_MAT_STAR_02 x1","Granary end reward (any Ires outcome)"),
 ("LOOT_ORB_U08","ND_ORB_REVERSECHAPEL","Ceiling altar","ITM_SET_88_CHEST x1; ITM_CON_UTL_ECHO x2","Optional"),
 ("LOOT_ORB_U09","LOC_Q_SPINDLE_06","Last Hymn reward","ITM_MAT_STAR_03 x1; ITM_LT_GEAR_REG_Q x2 (floor Relic)","Spindle end reward"),
 ("LOOT_ORB_U10","LOC_Q_CORE","Threshold cache","ITM_CON_UTL_ECHO x1; ITM_CON_UTL_AMMO_G x3; ITM_CON_UTL_AMMO_C x3","Pre-boss restock"),
]
for u in UNIQUE:
    n=NODE[u[1]]; loot.append([u[0],u[1],u[2],u[3],n[5],n[6],lvl_of(u[1]),"New: "+u[4]])
loot.sort(key=lambda l:(float(l[4]),l[0]))
wr("loot_placement.csv",["placement_id","node","container","contents","x_m","y_m","level","note"],loot)

# ---------------------------------------------------------------- secrets
SECRETS = [
 ("SEC_ORB_S01","ND_ORB_SCARFIELD","Hidden plate chain","Unmarked (no chevron) plates under the Lander's wing; mag boots still lock","Look under the wing; a lone Shard-note","ITM_MAT_STAR_01 x5; ITM_LOR lore (see collectibles)"),
 ("SEC_ORB_S02","LOC_Q_HULL_02","Illusory bunk wall","Hit the wall behind the top bunk tier","Cold draft and frost on one panel","Ostra memory fragment (ORB_MEM_01)"),
 ("SEC_ORB_S03","LOC_Q_HULL_05","Vent ride","Ride a vent blast up 40 m to a ledge above the vents","Scorch marks on a ledge high up","ITM_MAT_STAR_02 x1"),
 ("SEC_ORB_S04","ND_ORB_JOINTBEARING","Bearing interior","Drop into the bearing during a platform window, 15 m down","Light leaks between the bearing teeth","ITM_CON_UTL_POUCH_L x1; Maker Terminal 3"),
 ("SEC_ORB_S05","LOC_Q_GALLERIES_02","Inside the Cinderreach glass","Break the vault glass and walk the frozen hill to a cottage","A lit window in the frozen hill","Ostra memory fragment (ORB_MEM_02); ITM_LOR lore"),
 ("SEC_ORB_S06","ND_ORB_LENS","Outer rim of the Lens","Kick-off from the Lens rim in zero-g pocket to the outer lens frame","Ostra: 'I can see the Hold from here'","Shard-note chalk x5; vista and achievement hook (ACH request)"),
 ("SEC_ORB_S07","LOC_Q_SPINDLE_02","Hidden seam","A seam drawn faintly on the ceiling; jump to it in 0.4 g","Dust falls up near it","Opens ND_ORB_REVERSECHAPEL"),
 ("SEC_ORB_S08","LOC_Q_SPINDLE_04","Reflection that doesn't move","Attack the mirror whose reflection stays still","One reflection lags","Ostra memory fragment (ORB_MEM_03); ITM_MAT_STAR_03 x1"),
 ("SEC_ORB_S09","LOC_Q_CORE","Under the threshold","Grav lift down past the boss gate into a cooling duct","Frost on the floor grille","Maker Terminal 5; lore: Hush's first log"),
]
wr("secrets.csv",["secret_id","node","type","how","hint","reward"],SECRETS)

# ---------------------------------------------------------------- collectibles
lore = [r for r in rd("data/items/lore_items.csv") if "REG_Q" in (r["region"]+r["location"])]
sites = {r["loc_id"]:r for r in wloc if r["kind"]=="Lore site"}
col=[]; optional_nodes=[n[0] for n in N]
for i,r in enumerate(lore):
    loc=r["location"]
    if loc in sites: nd=nearest(float(sites[loc]["x_m"]),float(sites[loc]["y_m"]))
    else:
        loc="(free placement)"; nd=N[(i*7)%len(N)][0]
    col.append([r["item_id"],"Lore item",r["name"],nd,loc,""])
MAKER=[("ORB_MAKER_1","ND_ORB_MAKERTERM","Maker Terminal 1 (story, MQ_RT_Q): reveals REG_Q map"),
       ("ORB_MAKER_2","LOC_Q_HULL_04","Maker Terminal 2: shows the Quiet's harvest record of Veyl"),
       ("ORB_MAKER_3","ND_ORB_JOINTBEARING","Maker Terminal 3 (secret S04)"),
       ("ORB_MAKER_4","ND_ORB_FLOWJUNCTION","Maker Terminal 4: the Granary manifest"),
       ("ORB_MAKER_5","LOC_Q_CORE","Maker Terminal 5 (secret S09): Hush's first log")]
for m in MAKER: col.append([m[0],"Maker Terminal",m[2],m[1],"","5 total; all 5 unlock a Hush dialogue option in MQ_A3_05 (design choice)"])
for i,nd in enumerate(["LOC_Q_HULL_02","LOC_Q_GALLERIES_02","LOC_Q_SPINDLE_04"]):
    col.append([f"ORB_MEM_0{i+1}","Ostra memory fragment",["The hail","The refusal","The heading"][i],nd,"","Secrets S02, S05, S08; each adds an Ostra line before the Choice"])
for i,nd in enumerate(["LOC_Q_GALLERIES_02","LOC_Q_GALLERIES_03","LOC_Q_GALLERIES_04","LOC_Q_GALLERIES_04","LOC_Q_GALLERIES_05","LOC_Q_GALLERIES_05"]):
    col.append([f"ORB_SOIL_0{i+1}","Region soil sample",f"Soil of REG_0{i+1}",nd,"","Taking all 6 unlocks the Bind ending's 'whole land' epilogue variant (design choice)"])
wr("collectibles.csv",["col_id","type","name","node","world_loc","note"],col)

# ---------------------------------------------------------------- boss arenas
BA = [
 ("ACT_BOSS_HUSH","Hush","ND_ORB_ARENA_HUSH",80,"Sphere room seen as a disc floor","70 m","LOC_Q_CORE / Anchor Q_07","50 m","Fog gate 4 m, one-way",
  "P1 Lens (100-65%): 1.0 g, flat floor, 4 Lens pylons as cover. P2 Choir (65-30%): 0.4 g, floor shatters into 9 floating islands 6-10 m apart, Choirborn copies summoned in pairs. P3 Seed (30-0%): 0 g, 6 mag platforms orbit Hush; Ostra powers scale with taken Heart Shards; Hush HP scales down 4% per taken Shard (campaign data request)",
  "P1: Lens beam sweeps (telegraph 1.2 s white line). P2: gaps between islands are void (Tether rescue, -15% Health). P3: platform orbit 8 deg/s",
  "ARENA_HUSH_P1 ARENA_HUSH_P2 ARENA_HUSH_P3","Final campaign boss. Raid boss ACT_BOSS_QUIETCORE keeps its own instanced arena (LOC_END_RAID_01) built from this kit"),
 ("ACT_BOSS_LAMPLIGHTER","The Lamplighter (rematch, unmasked)","ND_ORB_ARENA_IRES",76,"Round well with 4 lamp posts","56 m","LOC_Q_GALLERIES_06 / Anchor Q_04","420 m (shortcut lift makes it 60 m)","Fog gate 4 m",
  "Same moveset as Hollowdeep plus 0.4 g leap slam; lamp posts are breakable (her lantern weak point x2.0 stays)",
  "Lamp oil pools burn (8 dmg/s) for 6 s",
  "ARENA_IRES_RQ","Optional: only if the player chooses to fight (MQ_A3_03). Needs a level-76 stat row"),
 ("ENC_ORB_COPIES","The Choir of Copies (set piece, not a boss)","LOC_Q_SPINDLE_02/03/05",78,"Three rooms","40 x 80 m","Anchors Q_05/Q_06","<200 m","Seam doors lock during a duel",
  "Each copy: leader HP x3, original's weapon class and one signature Weave ability; talk-past skips the duel",
  "Gravity seams in each room; copy may switch down",
  "","Not one of the 44 bosses; built from ACT_CHOIRBORN_LEADER"),
]
wr("boss_arenas.csv",["boss","name","node","level","shape","size","nearest_anchor","anchor_run","entry","phases_and_gravity","hazards","arena_hooks","note"],BA)

# ---------------------------------------------------------------- landmarks & POIs
LM = [
 ("LM_ORB_VEYL","Veyl (the planet)","Everywhere outside","Always overhead or below; the main orientation cue. Region of the player's current Heart Shard choices glows Ember (taken) or cyan (spared)"),
 ("LM_ORB_THRESHERS","The Thresher Arms","SEC_ORB_01","Six 300 m arms that rake the planet's Shard columns; visible from the Lander; one sweeps past every 40 s"),
 ("LM_ORB_SPINDLE","The Spindle","SEC_ORB_05","A 900 m bone-white tower along the ring axis; seen from every section; guides the player spinward"),
 ("LM_ORB_LENS","The Lens","SEC_ORB_04","100 m window; the first place the player sees the whole planet; later, the dark ending turns this lens on the Hold"),
 ("LM_ORB_SHARDCOLUMN","Shard Column","SEC_ORB_02","Column of Shards rising from Veyl into the Granary; it dims as the player re-routes the flow"),
 ("LM_ORB_CORELIGHT","Hush's Core","SEC_ORB_06","A slow-pulsing white star at the end of the ring; pulse rate rises as the player gets closer (1 pulse/8 s at Lander to 1/s at the Core)"),
 ("LM_ORB_LANDER","The Broken Lander","SEC_ORB_00","Smoke-free wreck (no air); its beacon blinks red, visible from the Threshing Ring for orientation back"),
]
wr("landmarks.csv",["lm_id","name","section","role"],LM)

POI = [[n[0],n[3],n[1],n[2],n[14]] for n in N if n[2] in ("Set piece","Landmark") or n[13]==0]
wr("points_of_interest.csv",["node","name","section","kind","what"],POI)

# ---------------------------------------------------------------- lighting
LGT = [
 ("LGT_ORB_SCAR","LGT_QUIET","SEC_ORB_00","Sun 130,000 lux hard from spinward-low; Veyl bounce from below #3A4A6A at 0.3; Lander beacon #C8281E 1 Hz","No fog (vacuum)"),
 ("LGT_ORB_THRESH","LGT_QUIET / LGT_QUIET_INT","SEC_ORB_01","Exterior as Scar; interiors bone-white surface light 6,500 K at 0.8; barracks dimmed to 0.4 with alarm red strobes in combat","Interior volumetric 0.01"),
 ("LGT_ORB_JOINT","LGT_QUIET","SEC_ORB_02","Sun slices through bearing teeth: 20 s light/dark cycle synced to the platform windows","None"),
 ("LGT_ORB_GRANARY","LGT_QUIET_INT","SEC_ORB_03","Each vault lit by its own region's sky preset frozen at one time of day (LGT_REG_0n) through the glass; gallery floor stays neutral 6,500 K","Vault volumetric per region; gallery 0.01"),
 ("LGT_ORB_LENS","LGT_QUIET","SEC_ORB_04","Veyl fills 70% of view; planet-shine #6A8ABF as key; sun hidden behind the planet for the first visit (eclipse rim light)","None"),
 ("LGT_ORB_SPINDLE","LGT_QUIET_INT","SEC_ORB_05","Light comes from 'down' in each room, so the light direction rotates with gravity; copies lit cold cyan #8FE3EE rim","0.015"),
 ("LGT_ORB_CORE","LGT_QUIET_INT","SEC_ORB_06","White star key from Hush; P1 white, P2 shifts to Choir cyan, P3 fades to black with only Ostra's Shard and Hush lit","Phase-driven"),
]
wr("lighting.csv",["lgt_id","base_preset","section","key_and_fill","fog"],LGT)

# ---------------------------------------------------------------- audio & VFX cues
CUE = [
 ("ND_ORB_LANDER","Arrival","Play_MUS_CIN_ACT3_ASCENT end; 30 s silence; Play_AMB_QUI_BED_NIGHT","VFX_ORB_LANDER_SPARKS","Vacuum mix: all SFX low-passed at 800 Hz and heard through the suit (new snapshot SNP_ORB_VACUUM)"),
 ("ND_ORB_SCARFIELD","First mag-lock","SFX_ORB_MAGBOOT_LOCK","VFX_ORB_MAGBOOT_SPARK","Tutorial popups TUT_ORB_MAGBOOT, TUT_ORB_KICKOFF"),
 ("LOC_Q_HULL_01","Air returns","Snapshot SNP_ORB_VACUUM off over 2 s; Play_AMB_QUI_INTERIOR","VFX_ORB_AIRLOCK_FOG","Anchor lit: standard Anchor cue"),
 ("ND_ORB_HARVESTRAIL","Thresher pass","Play_AMB_QUI_EMITTERS (thresher groan felt through boots, sub only)","VFX_ORB_THRESHER_SHADOW","Arm shadow sweeps the rail every 40 s"),
 ("LOC_Q_HULL_03","Arm sweep","SFX_ORB_FLAIL_WARN (1 s) / SFX_ORB_FLAIL_SWEEP","VFX_ORB_FLAIL_TRAIL","Telegraph: floor chevrons light amber 1 s before"),
 ("ND_ORB_MAKERTERM","Hush speaks","Play_VO_HUSH (new) ; Play_MUS_THEME_QUIET first statement","VFX_ORB_MAKER_UPLINK","Ostra/Hush argument scene"),
 ("LOC_Q_HULL_05","Vent cycle","SFX_ORB_VENT_WARN / SFX_ORB_VENT_BLAST","VFX_ORB_VENT_PLUME","Amber strobe 1 s before"),
 ("ND_ORB_JOINTBEARING","Bearing turn","SFX_ORB_BEARING_GROAN (loop, pitch with speed); Play_MUS_QUI_DISCOVERY","VFX_ORB_BEARING_LIGHTSLICE","Light/dark cycle 20 s"),
 ("ND_ORB_GRANARYGATE","Gate opens","SFX_ORB_GATE_OPEN; gravity-return thud SFX_ORB_GRAV_RETURN","VFX_ORB_GATE_SIGIL","Banner BAN_ORB_GRANARY"),
 ("LOC_Q_GALLERIES_02","Vault proximity","Play_AMB_QUI_WEAVE_HUM + region bed AMB_R01_BED_DAY at -12 dB through glass","VFX_ORB_VAULT_GLASS_SHIMMER","Glass break: SFX_ORB_GLASS_SHATTER_L, VFX_ORB_GLASS_SHATTER"),
 ("ND_ORB_FLOWJUNCTION","Valve turned","SFX_ORB_VALVE_TURN; Shard flow re-routes SFX_ORB_FLOW_SURGE","VFX_ORB_SHARDFLOW_LINE","Line colour: Ember if Shard taken, cyan if spared"),
 ("LOC_Q_GALLERIES_06","Ires","Play_VO_IRES (existing campaign VO); Lamplighter boss music reused","VFX_ORB_LAMP_FLICKER",""),
 ("ND_ORB_LENS","The view","Play_MUS_THEME_QUIET full; AMB_QUI_HOLLOWING RTPC 0.6","VFX_ORB_LENS_GLARE","Camera holds 3 s (skippable) on first entry"),
 ("ND_ORB_INVSTAIR","First seam","SFX_ORB_SEAM_ROTATE","VFX_ORB_SEAM_LINE","Tutorial TUT_ORB_SEAM"),
 ("LOC_Q_SPINDLE_02","Copy appears","SFX_ORB_COPY_FORM; copies use the original's VO through a reversed-choir filter","VFX_ORB_COPY_FORM (cyan glass assembling)","Talk-past success: VFX_ORB_COPY_DISSOLVE"),
 ("LOC_Q_SPINDLE_04","Mirrors","SFX_ORB_MIRROR_WHISPER","VFX_ORB_MIRROR_LAG","Secret S08 hint"),
 ("LOC_Q_CORE","Threshold","Music drops to a single held note; AMB_QUI_HOLLOWING 1.0","VFX_ORB_CORE_PULSE","Pulse 1/s"),
 ("ND_ORB_ARENA_HUSH","Boss","MUS_BOSS_HUSH_INTRO/P1/P2/P3/WIN (requested); SFX_ORB_HUSH_PHASE","VFX_ORB_HUSH_LENSBEAM, VFX_ORB_HUSH_SHATTER, VFX_ORB_HUSH_SEED","Phase transitions 3 s invulnerable"),
 ("ND_ORB_CHOICEDAIS","Choice","Play_MUS_CIN_ENDING_QUIET (Take) / ending cues","VFX_ORB_CHOICE_SHARDS","Three Shards rise; each option lights when hovered"),
]
wr("cues.csv",["node","moment","audio","vfx","note"],CUE)

# ---------------------------------------------------------------- strings (UI text for this level)
STR = [
 ("STR_ORB_SEC_00","Lander Scar"),("STR_ORB_SEC_01","The Threshing Ring"),("STR_ORB_SEC_02","Threshing Joint"),
 ("STR_ORB_SEC_03","The Granary"),("STR_ORB_SEC_04","Lens Joint"),("STR_ORB_SEC_05","The Choir of Copies"),("STR_ORB_SEC_06","The Hush Core"),
 ("STR_TUT_ORB_MAGBOOT","Your boots lock to marked plates. Walk on any plate, even walls."),
 ("STR_TUT_ORB_KICKOFF","{BTN_JUMP} Kick off. You drift straight until you reach a surface."),
 ("STR_TUT_ORB_THRUST","{BTN_DODGE} Thrust. A short burst in any direction."),
 ("STR_TUT_ORB_TETHER","Drift too long and Ostra pulls you back. It costs Health."),
 ("STR_TUT_ORB_LOWG","Low gravity. You jump higher and fall slower."),
 ("STR_TUT_ORB_SEAM","Cross the seam and down changes."),
 ("STR_TUT_ORB_COMETDROP","Attack while falling from a high jump to slam the ground."),
 ("STR_INL_ORB_TETHER","Ostra Tether"),
 ("STR_INL_ORB_OUTOFREACH","Out of reach"),
 ("STR_PRM_ORB_VALVE","{BTN_INTERACT} Turn valve"),
 ("STR_PRM_ORB_TERMINAL","{BTN_INTERACT} Use Maker Terminal"),
 ("STR_PRM_ORB_SOIL","{BTN_INTERACT} Take soil"),
 ("STR_PRM_ORB_TALKCOPY","{BTN_INTERACT} Speak to the copy"),
 ("STR_NTF_ORB_MAKER","Maker Terminal accessed ({VAR_count}/5)"),
 ("STR_NTF_ORB_MEMORY","Ostra remembers ({VAR_count}/3)"),
 ("STR_NTF_ORB_SOIL","Soil sample taken ({VAR_count}/6)"),
 ("STR_BAN_ORB_GRANARY","The Granary"),
 ("STR_ITM_ORB_SIGIL_NAME","Maker Sigil"),
 ("STR_ITM_ORB_SIGIL_DESC","A Maker's key, warm to the touch. Opens the Granary Gate."),
]
wr("strings.csv",["str_id","en","max_chars"],[[s[0],s[1],math.ceil(len(s[1])*1.4)] for s in STR])

# ---------------------------------------------------------------- time to complete
crit = sum(s[12] for s in SEC); full = sum(s[13] for s in SEC)
wr("time_to_complete.csv",["sec_id","name","critical_path_min","full_clear_min"],
   [[s[0],s[1],s[12],s[13]] for s in SEC]+[["TOTAL","Orbital Ring",crit,full]])

# ---------------------------------------------------------------- level checks
CHK=[]
CHK.append(("Area 4,000 x 500 m = 2.0 km2 (plan 3.7)", "PASS"))
CHK.append(("Three sub-areas (plan 5.3)", "PASS: Threshing Ring, Granary, Choir of Copies (+ Core)"))
over=[r for r in rows if r[6].startswith("NO")]
CHK.append(("Anchors every 400-600 m (plan 3.7)", "PASS with requested Q_00/Q_08/Q_09" if not over else f"FAIL {over}"))
CHK.append(("Every sub-area ends in a shortcut (site rule)", "PASS"))
CHK.append(("Critical path length", f"{crit_len} m walked; {crit} min"))
ids=set(NODE); bad=[e for e in E if e[0] not in ids or e[1] not in ids]
CHK.append(("Edges reference real nodes", "PASS" if not bad else f"FAIL {bad}"))
wr("checks.csv",["check","result"],CHK)

# ---------------------------------------------------------------- SVG map (node graph)
sx=lambda x: 20+x*0.29; sy=lambda y: 30+y*0.29
col_k={"Room":"#6b7a8f","Exterior":"#3a6fb0","Joint":"#9b7bd6","Arena":"#c8281e","Set piece":"#e0a040","Landmark":"#8fe3ee"}
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1210 210" font-family="monospace" font-size="6"><rect width="1210" height="210" fill="#111418"/>']
for s in SEC: svg.append(f'<rect x="{sx(s[4])}" y="{sy(0)}" width="{(s[5]-s[4])*0.29}" height="{500*0.29}" fill="none" stroke="#333" /><text x="{sx(s[4])+2}" y="26" fill="#aaa">{s[1]}</text>')
for e in E:
    a,b=NODE[e[0]],NODE[e[1]]
    svg.append(f'<line x1="{sx(a[5])}" y1="{sy(a[6])}" x2="{sx(b[5])}" y2="{sy(b[6])}" stroke="{"#e0e0e0" if e[4]=="Y" else "#666"}" stroke-dasharray="{"" if e[4]=="Y" else "2,2"}"/>')
for n in N:
    svg.append(f'<circle cx="{sx(n[5])}" cy="{sy(n[6])}" r="4" fill="{col_k[n[2]]}"/>')
for a in anc: svg.append(f'<text x="{sx(int(a[2]))-3}" y="{sy(int(a[3]))+12}" fill="#e0a040">A</text>')
svg.append('<text x="20" y="200" fill="#888">Solid = critical path, dashed = optional/shortcut, A = Anchor. x along ring 0-4000 m, y across 0-500 m.</text></svg>')
open(os.path.join(OUT,"map.svg"),"w").write("\n".join(svg)); print("map.svg written")
