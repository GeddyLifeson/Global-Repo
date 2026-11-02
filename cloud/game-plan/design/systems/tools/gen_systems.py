#!/usr/bin/env python3
"""Generates every CSV in design/systems/. Values are Shardfall design choices (3 Oct 2026)
unless a column names a data/ source. Run: python3 design/systems/tools/gen_systems.py"""
import csv, os, collections, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
DATA = os.path.join(OUT, '..', '..', 'data')

def rd(p):
    with open(os.path.join(DATA, p), newline='') as f:
        return list(csv.DictReader(f))

def wr(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print(f'{name}: {len(rows)} rows')

# ------------------------------------------------------------------ STEALTH
# Detection meter per AI per target, 0..100. Gain/s while target is in a sight cone:
#   gain = 55 x Dist x Light x Stance x Motion x Load x Cone x Faction x (1 - Infil) x Perks
wr('stealth_states.csv',
   ['state_id', 'state', 'enter_rule', 'exit_rule', 'ai_behaviour', 'hud_icon', 'icon_colour', 'sfx_hook', 'music_layer', 'data_ids'],
   [
    ['STL_UNAWARE', 'Unaware', 'Meter 0-34; spawn default', 'Meter >= 35 or a heard noise', 'Runs patrol or idle package', 'none', '-', '-', 'Explore', 'AIP_* Sight m / Sight FOV deg / Hearing m'],
    ['STL_SUSPICIOUS', 'Suspicious', 'Meter 35-69, or noise heard with meter < 35 (meter set to 35)', 'Meter decays below 20 (back to Unaware), or reaches 70', 'Stops, turns head to stimulus at 90 deg/s, walks 3 m toward it after 1.5 s; bark VO_BARK_SUSPECT', 'Hollow eye with ? fill arc', '#E8C547', 'SFX_STL_SUSPECT', 'Explore + tension stinger', 'STR_STL_SUSPICIOUS'],
    ['STL_SEARCHING', 'Searching', 'Meter 70-99; gunshot or body found within hearing range; ally alert while the target is unseen', 'Meter 100 (Alerted); or 20 s search without sight (Lost)', 'Moves to last known position at run speed, then sweeps 3 search points within 12 m, 4 s each; flashlight/lantern raised (light x1.4 on target)', 'Eye with ? solid', '#E89A3C', 'SFX_STL_SEARCH', 'Tension', 'STR_STL_SEARCHING'],
    ['STL_ALERTED', 'Alerted (combat)', 'Meter 100, any damage taken from the target, or sneak attack fails', 'Target unseen for 8 s (Lost)', 'Enters combat AI (utility scoring); shouts alert to allies (propagation table)', 'Eye with ! red', '#D8483A', 'SFX_STL_ALERT', 'Combat layer 2', 'STR_STL_ALERTED'],
    ['STL_LOST', 'Lost target', 'Alerted or Searching with no sight for 8 s', 'After 20 s search -> Wary; sight regained -> Alerted (meter jumps to 100)', 'Search pattern of 5 points in 20 m, grenade/cast into last cover 30% chance (Remnant 60%)', 'Eye with ? red outline', '#D8483A', 'SFX_STL_LOST', 'Tension', 'STR_STL_LOST'],
    ['STL_WARY', 'Wary', 'After Lost or after a body was found', 'Timer ends: 120 s (300 s after a body)', 'Back to patrol at walk; thresholds -15 (Suspicious at 20, Searching at 55); gain x1.25', 'Small eye, grey', '#9A9A9A', '-', 'Explore', 'STR_STL_WARY'],
   ])

wr('stealth_detection_factors.csv',
   ['factor_id', 'factor', 'band_or_case', 'multiplier', 'rule', 'source_or_note'],
   [
    ['DET_BASE', 'Base gain', 'Target fully visible at 0 m', '55 per s', 'Unaware to Alerted in 1.8 s at point blank in light', 'Shardfall choice'],
    ['DET_DIST_NEAR', 'Distance', '0 to 4 m', '1.0', 'Inside 4 m', 'Shardfall choice'],
    ['DET_DIST_MID', 'Distance', '4 m to 50% of Sight m', 'lerp 1.0 -> 0.5', 'Linear', 'AIP_* Sight m'],
    ['DET_DIST_FAR', 'Distance', '50% to 100% of Sight m', 'lerp 0.5 -> 0.1', 'Beyond Sight m: 0', 'AIP_* Sight m'],
    ['DET_CONE_CENTER', 'Vision cone', 'Within 30 deg of facing', '1.0', 'Foveal', 'Shardfall choice'],
    ['DET_CONE_PERIPH', 'Vision cone', '30 deg to half of Sight FOV', '0.4', 'Peripheral', 'AIP_* Sight FOV deg'],
    ['DET_CONE_REAR', 'Vision cone', 'Outside FOV', '0', 'Only noise or Choirborn Shard-sense', ''],
    ['DET_CONE_VERT', 'Vision cone', 'More than 35 deg above or 50 deg below eye line', '0.5', 'Ledges and pits help', ''],
    ['DET_LIGHT_DARK', 'Light on target', 'Luminance < 0.08 (moonless night, unlit interior)', '0.2', 'Light sampled at target chest from probe grid every 0.25 s', 'Shardfall choice'],
    ['DET_LIGHT_DIM', 'Light on target', '0.08 - 0.25 (night, shade, dusk)', '0.45', '', ''],
    ['DET_LIGHT_LIT', 'Light on target', '0.25 - 0.6 (overcast day, lit room)', '0.8', '', ''],
    ['DET_LIGHT_BRIGHT', 'Light on target', '0.6 - 0.9 (full sun)', '1.0', '', ''],
    ['DET_LIGHT_SPOT', 'Light on target', '> 0.9 (spotlight, campfire within 3 m, searcher lantern)', '1.5', '', ''],
    ['DET_LIGHT_SCAR', 'Shard scar glow', 'Casting, Surge, or Resonance', '+0.3 luminance for 3 s', 'Weave use shows you', 'Character creator scar glow does not change this'],
    ['DET_LIGHT_TORCH', 'Carried light', 'Player torch or lamp lit', 'luminance floor 0.7', '', ''],
    ['DET_STANCE_STAND', 'Stance', 'Standing', '1.0', '', 'STAT_MOVESPEED'],
    ['DET_STANCE_CROUCH', 'Stance', 'Crouched', '0.6', 'Crouch move 2.5 m/s', 'STAT_MOVESPEED'],
    ['DET_STANCE_COVER', 'Stance', 'Crouched in tall grass, foliage volume or smoke', '0.3', 'Smoke blocks sight fully past 2 m inside it', ''],
    ['DET_MOTION_STILL', 'Motion', 'Speed < 0.3 m/s', '0.5', '', ''],
    ['DET_MOTION_WALK', 'Motion', 'Walk or crouch-walk', '1.0', '', ''],
    ['DET_MOTION_RUN', 'Motion', 'Run 5 m/s', '1.5', '', ''],
    ['DET_MOTION_SPRINT', 'Motion', 'Sprint, roll, jump', '2.0', '', ''],
    ['DET_LOAD_LIGHT', 'Equip load', 'Light (<30%)', '1.0', 'Applies to sight gain and footstep noise', 'ITM_F_EQUIP_LOAD'],
    ['DET_LOAD_MEDIUM', 'Equip load', 'Medium (<70%)', '1.1', '', ''],
    ['DET_LOAD_HEAVY', 'Equip load', 'Heavy (>=70%)', '1.3', '', ''],
    ['DET_INFIL', 'Infiltration skill', 'Rank 1-100', 'x (1 - 0.0025 x rank)', '-25% at rank 100', 'SKL_INFILTRATION'],
    ['DET_PERK_LIGHTSTEP', 'Perk', 'Light Step ranks 1-3', 'Sight m and noise radius -10% per rank', '', 'PRK_INFILTRATION_01'],
    ['DET_PERK_VANISH', 'Perk', 'Vanish', 'Lost timer 8 s -> 6 s', '', 'PRK_INFILTRATION_08'],
    ['DET_PERK_DISGUISE', 'Perk', 'Disguise with 3+ faction armor pieces', 'Fodder gain 0 beyond 4 m', 'Leaders and heavies see through at x0.5', 'PRK_INFILTRATION_10'],
    ['DET_DECAY', 'Decay', 'Target not in sight', '-12 per s after 2.0 s grace', 'Never below the state floor of Wary (0)', ''],
    ['DET_TICK', 'Update rate', 'Per AI', '0.1 s (10 Hz) near, 0.25 s beyond 40 m', 'Max 40 line traces per frame', 'design/tech/03-save-ai-world.md'],
    ['DET_COOP', 'Co-op', 'Each player has its own meter per AI', '-', 'Alerted on one player puts AI in combat; others keep their meter', ''],
    ['DET_DIFF_ASSIST', 'Assist option', 'On', 'none', 'Assist never changes stealth', 'DIF_ASSIST'],
   ])

FAC = [
 ['FAC_HOLLOWED', 'Hollowed', '0.7', '1.3', '15', '1.0', 'none', 'Shuffle-scream wakes Hollowed within 15 m after 1.5 s', 'Weak eyes, keen ears. Bodies of Hollowed do not raise alarm.'],
 ['FAC_REMNANT', 'Remnant', '1.2', '0.8', '35', '0.6 (thermal: light factor never below 0.6)', 'none', 'Drone link: every Remnant in the encounter zone goes Alerted 2.0 s after the first; killing the relay unit (Leader) first stops the link', 'Thermal optics ignore darkness; smoke still blocks.'],
 ['FAC_THORN', 'Thorn Clans', '1.0', '1.0', '25', '1.0', 'none', 'War horn: Leader blows horn 3 s after Alerted, pulls camp within 60 m; kill Leader before 3 s to stop it', 'Morale rules apply (FRM_MORALE).'],
 ['FAC_CHOIRBORN', 'Choirborn of the Quiet', '1.1', '1.0', '25', '1.0', 'Shard-sense: 360 deg detection inside 8 m at gain x0.5, ignores light', 'Choir chorus: allies within 40 m share the meter value (highest wins) every 1 s', 'Hardest to sneak; teleporting searchers.'],
 ['CREATURE', 'Creatures (Hostile/Territorial)', '0.9', '1.4', '0', '1.0', 'Scent: downwind of player inside 20 m adds +8 per s', 'Pack call within 30 m', 'Wind direction from world weather system'],
 ['FAC_TOWN', 'Town guards (crime)', '1.0', '1.0', '20', '1.0', 'none', 'Crime witness: any civilian who sees a crime reports to nearest guard in 10 s', 'Detection here feeds the crime system (world/campaign own penalties)'],
]
wr('stealth_faction_rules.csv',
   ['fac_id', 'faction', 'sight_gain_mult', 'hearing_radius_mult', 'shout_alert_radius_m', 'light_factor_rule', 'special_sense', 'alert_propagation', 'notes'], FAC)

NOISE = [
 ['NOI_STEP_CROUCH', 'Footsteps, crouch-walk', 2, 'continuous', '+6/s', 'Silent Roll does not apply'],
 ['NOI_STEP_WALK', 'Footsteps, walk', 4, 'continuous', '+8/s', ''],
 ['NOI_STEP_RUN', 'Footsteps, run', 9, 'continuous', '+12/s', ''],
 ['NOI_STEP_SPRINT', 'Footsteps, sprint', 15, 'continuous', '+18/s', ''],
 ['NOI_ROLL', 'Roll or backstep', 6, 'event', '+20', 'PRK_INFILTRATION_05 makes it 0'],
 ['NOI_LAND', 'Landing from > 3 m', 12, 'event', '+30', ''],
 ['NOI_SURFACE_METAL', 'Surface: hull plate, grating', 'x1.5', 'modifier', '-', 'Physical material tag'],
 ['NOI_SURFACE_SOFT', 'Surface: moss, sand, snow, carpet', 'x0.6', 'modifier', '-', ''],
 ['NOI_SURFACE_WATER', 'Surface: shallow water', 'x1.3', 'modifier', '-', ''],
 ['NOI_MELEE_HIT', 'Melee hit on enemy', 12, 'event', '+35', 'Sneak kill with Quiet Hand: 0 within 8 m'],
 ['NOI_MELEE_BLOCK', 'Blocked hit / parry', 18, 'event', '+45', ''],
 ['NOI_BODY_FALL', 'Body falls', 8, 'event', '+25', 'Investigate; body found -> Searching'],
 ['NOI_CAST', 'Weave Cast or Strike', 20, 'event', '+40', ''],
 ['NOI_SURGE', 'Surge', 50, 'event', 'Alerted', ''],
 ['NOI_RESONANCE', 'Resonance', 70, 'event', 'Alerted', ''],
 ['NOI_GUN_PST', 'Pistol shot', 55, 'event', 'Searching', 'ITM_CLS_PST'],
 ['NOI_GUN_ARF', 'Auto Rifle shot', 75, 'event', 'Searching', 'ITM_CLS_ARF'],
 ['NOI_GUN_SCT', 'Scout Rifle shot', 85, 'event', 'Searching', 'ITM_CLS_SCT'],
 ['NOI_GUN_SMG', 'SMG shot', 55, 'event', 'Searching', 'ITM_CLS_SMG'],
 ['NOI_GUN_SHG', 'Shotgun shot', 85, 'event', 'Searching', 'ITM_CLS_SHG'],
 ['NOI_GUN_SNP', 'Sniper shot', 130, 'event', 'Searching', 'ITM_CLS_SNP; shooter position not revealed beyond 80 m'],
 ['NOI_GUN_LCH', 'Launcher blast', 110, 'event', 'Alerted', 'ITM_CLS_LCH'],
 ['NOI_GUN_LNC', 'Shard Lance', 65, 'event', 'Searching', 'ITM_CLS_LNC'],
 ['NOI_GUN_SUPP', 'Suppressor perk on firearm', 'x0.35', 'modifier', '-', 'Needs new weapon perk, see DR-SYS-003'],
 ['NOI_DOOR', 'Door or hatch', 6, 'event', '+15', ''],
 ['NOI_LOCK_BREAK', 'Lockpick breaks', 5, 'event', '+15', ''],
 ['NOI_THROW', 'Thrown distraction (pebble, bottle)', 12, 'event at impact', '+35 and Investigate', 'Draws AI to impact point; does not raise above Suspicious'],
 ['NOI_STRIDER', 'Strider gallop', 25, 'continuous', '+25/s', 'Walk gait 8 m'],
 ['NOI_VEH_SKIM', 'Skimmer engine', 45, 'continuous', '+35/s', 'Idle 15 m'],
 ['NOI_VEH_HAUL', 'Hauler engine', 60, 'continuous', '+45/s', 'Idle 20 m'],
 ['NOI_VEH_FLY', 'Flyer engine', 80, 'continuous', '+45/s', 'Idle 25 m'],
 ['NOI_EXPLOSION', 'Explosion', 90, 'event', 'Alerted', 'Vehicle death, barrels'],
 ['NOI_RAIN', 'Weather: rain or storm', 'x0.7 all radii', 'modifier', '-', 'From weather system'],
]
wr('stealth_noise.csv', ['noise_id', 'source', 'radius_m', 'kind', 'meter_effect_if_heard', 'notes'], NOISE)

wr('stealth_actions.csv',
   ['act_id', 'action', 'condition', 'numbers', 'xp', 'data_ids'],
   [
    ['STA_SNEAK_ATTACK', 'Sneak attack', 'Target Unaware or Suspicious, attacker in rear 120 deg arc or unseen; not bosses', 'Melee x3.0 (Backstab perk x4/x5); daggers +1.0 on top; firearms precision x1.5 extra; Heavy and Leader capped at 60% max HP per sneak hit', 'SKL_INFILTRATION_XP4', 'PRK_INFILTRATION_03, ITM_CLS_DGR'],
    ['STA_TAKEDOWN', 'Silent takedown (melee button while crouched behind)', 'Fodder, Skirmisher, Artillery only; Unaware; 1.4 m rear', 'Instant kill, 2.2 s animation, noise 4 m (NOI_BODY_FALL 0)', 'SKL_INFILTRATION_XP4 x1.2', 'ANIM_STL_TAKEDOWN_*'],
    ['STA_CARRY', 'Carry body', 'Body of a takedown or sneak kill', 'Move 2.0 m/s, drop 0.5 s; hidden in tall grass or container = never found', '-', 'PRM_CARRY_BODY'],
    ['STA_DISTRACT', 'Throw distraction', 'Holding a pebble (infinite, 4 s cooldown)', 'Range 15 m arc; NOI_THROW', '-', 'TUT_SNEAK'],
    ['STA_LOCKPICK', 'Pick a lock', 'Lock tier 1-5; tier needs Infiltration 0/15/35/60/85 (Lockpick perk +1 tier per rank)', 'Sweet spot 30/22/15/10/6 deg; pick break chance per failed turn 20% (x0.75 with perk); picks are ITM_CON_UTL_PICK (Salvager Picks)', 'SKL_INFILTRATION_XP2 x tier', 'PRK_INFILTRATION_02, TUT_LOCKPICK'],
    ['STA_PICKPOCKET', 'Pickpocket', 'Behind or crouched, target not Alerted, 1.5 m', 'Chance = clamp(0.30 + rank/200 - item_kg x 0.06 - item_value/4000, 0.05, 0.95); equipped items need PRK_INFILTRATION_04 and < 2 kg; fail = crime + Alerted', 'SKL_INFILTRATION_XP3', 'PRK_INFILTRATION_04'],
    ['STA_HIDE', 'Break contact', 'Out of sight of every Alerted AI for 8 s (6 with Vanish)', 'AI goes Lost; crouching in cover halves its search point accuracy', 'SKL_INFILTRATION_XP1', 'PRK_INFILTRATION_08, PRK_INFILTRATION_12'],
    ['STA_MARK', 'Mark enemies', 'Aim at enemy 1 s (or Ostra ping in Explorer mode)', 'Max 8 marks; marks show state icon through walls 40 m; co-op marks shared', '-', 'UI_HUD_MARK'],
   ])

# ------------------------------------------------------------------ VEHICLES
VEH = [
 # id, name, role, regions, seats, mass_kg, top_kmh, rev_kmh, accel_0_100_s, brake_100_0_m, turn_deg_s, boost, susp_travel_m, flip_deg, self_right_s, ground_clear_m, ram_coef, weapons, hijack_rule, armor_kin, armor_weave, armor_expl, fuel
 ['VEH_SKIMMER', 'Skimmer', 'Fast scout, 2 seats (driver + passenger who can shoot)', 'REG_01 REG_02 REG_03 REG_04 REG_05', '2', 650, 118, 30, 4.2, 34, 95, 'Boost +40% top speed for 3 s, recharge 6 s', 0.45, 70, 2.5, 0.35, 0.9, 'None (passenger uses own firearm, 180 deg arc)', 'Hijack rule HJK_GROUND', 0.1, 1.0, 1.5, 'none'],
 ['VEH_HAULER', 'Hauler', 'Armored transport, 6 seats with turret', 'REG_02 REG_03 REG_04 REG_05 REG_06 REG_U', '6 (driver, gunner, 4 passengers)', 6200, 82, 24, 11.0, 42, 48, 'none', 0.6, 55, 4.0, 0.5, 2.6, 'Turret VWP_HAULER_TURRET', 'Hijack rule HJK_GROUND (gunner seat can be taken at any speed)', 0.05, 0.8, 1.2, 'none'],
 ['VEH_FLYER', 'Remnant Flyer', 'Enemy gunship, hijackable, 2 seats', 'REG_02 REG_03 REG_04 REG_05 REG_06 REG_Q', '2 (pilot, rear gunner)', 2400, 160, 0, 6.5, 0, 70, 'Afterburn +30% for 4 s, recharge 10 s', 0, 0, 0, 0, 1.4, 'Nose cannon VWP_FLYER_CANNON; rear gun VWP_FLYER_REAR', 'Hijack rule HJK_AIR', 0.25, 1.0, 1.5, 'none'],
]
wr('vehicles.csv',
   ['veh_id', 'name', 'role', 'regions', 'seats', 'mass_kg', 'top_speed_kmh', 'reverse_kmh', 'accel_0_100_s', 'brake_100_0_m', 'turn_rate_deg_s', 'boost', 'suspension_travel_m', 'flip_angle_deg', 'self_right_s', 'ground_clearance_m', 'ram_coef', 'weapons', 'hijack', 'dmg_mult_kinetic', 'dmg_mult_weave', 'dmg_mult_explosive', 'fuel'], VEH)

wr('vehicle_handling.csv',
   ['veh_id', 'param', 'value', 'unit', 'note'],
   [[v, p, val, u, n] for v, p, val, u, n in [
    ('VEH_SKIMMER', 'Steering lock', 32, 'deg', 'Halved above 90 km/h'),
    ('VEH_SKIMMER', 'Hover height', 0.35, 'm', 'Hover sled; crosses shallow water at full speed'),
    ('VEH_SKIMMER', 'Slope limit', 38, 'deg', 'Slides back above this'),
    ('VEH_SKIMMER', 'Drift grip', 0.55, 'ratio', 'Handbrake lateral grip'),
    ('VEH_SKIMMER', 'Air control', 25, 'deg/s pitch and roll', ''),
    ('VEH_SKIMMER', 'Jump (hop)', 2.2, 'm', 'Boost + jump button, 4 s cooldown'),
    ('VEH_SKIMMER', 'Camera', '3P chase 5.5 m back, 1.8 m up, FOV 70 -> 82 at top speed', '-', ''),
    ('VEH_HAULER', 'Steering lock', 28, 'deg', 'Six-wheel, all-wheel drive'),
    ('VEH_HAULER', 'Slope limit', 42, 'deg', ''),
    ('VEH_HAULER', 'Water depth', 1.4, 'm', 'Engine stalls deeper'),
    ('VEH_HAULER', 'Turret traverse', 70, 'deg/s', '360 deg, -10 to +45 elevation'),
    ('VEH_HAULER', 'Camera', '3P chase 8 m back, 3 m up, FOV 70', '-', 'Gunner uses 1P sight'),
    ('VEH_FLYER', 'Hover ceiling', 120, 'm above terrain', 'Hard ceiling per region map volume'),
    ('VEH_FLYER', 'Climb rate', 9, 'm/s', ''),
    ('VEH_FLYER', 'Strafe speed', 40, 'km/h', 'Hover mode'),
    ('VEH_FLYER', 'Roll / pitch rate', '90 / 60', 'deg/s', ''),
    ('VEH_FLYER', 'Stall', 'none (VTOL)', '-', 'Both engines lost = 6 m/s glide descent'),
    ('VEH_FLYER', 'Camera', '3P chase 9 m back, 2.5 m up, FOV 75', '-', ''),
    ('ALL', 'Enter / exit time', '0.8 / 0.6', 's', 'Exit at speed > 40 km/h = roll-out, 15% max HP'),
    ('ALL', 'Ram damage to actors', 'ram_coef x speed_kmh x (mass_kg/1000)^0.5, min speed 15 km/h', 'damage', 'Skimmer at 100 km/h = 72; Hauler at 80 km/h = 515'),
    ('ALL', 'Ram self-damage', '20% of dealt to hull', '-', ''),
    ('ALL', 'Collision damage to vehicle', '(delta_v_kmh - 25) x mass_kg/500 to hull when delta_v > 25 km/h', 'damage', ''),
    ('ALL', 'Despawn', 'Unoccupied and 300 m from all players for 120 s', '-', 'Player-called vehicles return to the last Anchor'),
    ('ALL', 'Call vehicle', 'At a lit Anchor or retaken outpost; 1 owned skimmer per player after MQ_A1_06', '-', 'Hauler from outposts; Flyer only by hijack'),
    ('ALL', 'Co-op', 'Host-authoritative physics; passengers predicted', '-', 'design/tech/02-online.md'),
    ('ALL', 'Not allowed', 'Citadels, sites, raid, Arena, The Quiet interior', '-', 'Hard blocker volumes'),
   ]])

PARTS = [
 # plan Part 1b values are exact for health
 ['VEH_SKIMMER', 'HULL', 600, 'All damage not on a part; 30% of part damage spills here', 'Hull 0: burning for 5 s (passengers warned), then explodes 6 m radius, 150 damage', 'Smoke at 50%, fire at 25%'],
 ['VEH_SKIMMER', 'ENGINE', 150, 'Rear housing', '0: no thrust, coasts; boost disabled at 50%', 'Top speed -30% under 50%'],
 ['VEH_SKIMMER', 'WHEEL_FL', 120, 'Hover pod front left', '0: pod drags, top speed -25%, pulls left 6 deg/s', ''],
 ['VEH_SKIMMER', 'WHEEL_FR', 120, 'Hover pod front right', '0: as above, pulls right', ''],
 ['VEH_SKIMMER', 'WHEEL_RL', 120, 'Hover pod rear left', '0: top speed -25%', ''],
 ['VEH_SKIMMER', 'WHEEL_RR', 120, 'Hover pod rear right', '0: top speed -25%', ''],
 ['VEH_HAULER', 'HULL', 1800, 'Body; 30% spill', 'Hull 0: burns 8 s then explodes 8 m, 400 damage', 'Smoke 50%, fire 25%'],
 ['VEH_HAULER', 'ENGINE', 450, 'Front grille', '0: immobile; turret still works', 'Under 50%: accel time x1.6'],
 ['VEH_HAULER', 'TURRET', 400, 'Roof turret', '0: turret dead, gunner exposed (takes full damage)', 'Under 50%: traverse -40%'],
 ['VEH_HAULER', 'WHEEL_1..6', 300, 'Each of six wheels', '0: wheel locks, top speed -12% each, 3+ lost = 20 km/h max', ''],
 ['VEH_FLYER', 'HULL', 900, 'Fuselage; 30% spill', 'Hull 0: spins down, explodes on impact 8 m, 300 damage', ''],
 ['VEH_FLYER', 'ENGINE_L', 200, 'Left nacelle', '0: thrust -50%, yaw drift; both lost = forced 6 m/s descent (hijack window)', ''],
 ['VEH_FLYER', 'ENGINE_R', 200, 'Right nacelle', 'as left', ''],
 ['VEH_FLYER', 'WING_L', 250, 'Left wing; takes 3x explosive (plan 1b)', '0: roll pull 20 deg/s, top speed -35%', ''],
 ['VEH_FLYER', 'WING_R', 250, 'Right wing; takes 3x explosive', 'as left', ''],
]
wr('vehicle_parts.csv', ['veh_id', 'part', 'health', 'hit_zone', 'destroyed_effect', 'damaged_effect'], PARTS)

wr('vehicle_weapons.csv',
   ['vwp_id', 'vehicle', 'damage_type', 'damage_per_shot', 'rpm', 'heat_per_shot', 'overheat_s', 'cooldown_s', 'range_m', 'blast_m', 'note'],
   [
    ['VWP_HAULER_TURRET', 'VEH_HAULER', 'Kinetic', 42, 450, 0.033, 4, 3, 150, 0, 'Overheat after 4 s of fire (STR_TIP_041); scales with enemy level band: x(1 + 0.04 x (band mid level - 10))'],
    ['VWP_FLYER_CANNON', 'VEH_FLYER', 'Weave (Iron)', 120, 120, 0.1, 5, 4, 200, 2.5, 'Same level scaling'],
    ['VWP_FLYER_REAR', 'VEH_FLYER', 'Kinetic', 28, 600, 0.025, 4, 3, 120, 0, ''],
   ])

wr('vehicle_hijack.csv',
   ['hjk_id', 'case', 'conditions', 'input', 'duration_s', 'result', 'counterplay', 'data_ids'],
   [
    ['HJK_GROUND', 'Ground vehicle (skimmer, hauler driver seat)', 'Within 2.5 m of a door; vehicle < 25 km/h, or engine destroyed, or driver staggered', 'Hold interact 0.5 s', 1.4, 'Driver thrown 3 m, staggered 2 s, takes 10% max HP; player takes seat', 'Enemy drivers accelerate away when player within 8 m (50% chance)', 'PRM_HIJACK, ANIM_VEH_HIJACK_GROUND'],
    ['HJK_GUNNER', 'Hauler turret seat', 'Climb the rear ladder at any speed', 'Interact', 1.0, 'Gunner pulled off; fall damage applies', '-', 'ANIM_VEH_HIJACK_TURRET'],
    ['HJK_AIR', 'Remnant Flyer', 'Player within 3 m of a landing skid; Flyer below 8 m altitude, or both engines destroyed (forced descent), or pilot stunned by Shock', 'Hold interact 0.6 s (from Strider double jump/glide or high ground)', 2.0, 'Pilot thrown off (fall damage), player pilots; rear gunner stays hostile until shot or thrown (melee 1 hit)', 'Flyer climbs to 20 m when a player is within 15 m under it (cooldown 12 s)', 'PRM_HIJACK, ANIM_VEH_HIJACK_AIR, STR_ACH_56'],
    ['HJK_PVP', 'Invasions', 'Players can hijack other players vehicles with the same rules; protection 3 s after entering', '-', '-', '-', '-', ''],
   ])

wr('vehicle_repair.csv',
   ['rep_id', 'method', 'rule', 'cost', 'data_ids'],
   [
    ['REP_TOOL', 'Field repair', 'Hold interact at a damaged part, 1 part at a time, 25 health per s (x(1 + Engineering rank/100))', 'ITM_CON_UTL_REPAIR, 1 per part (new item, DR-SYS-001)', 'SKL_ENGINEERING'],
    ['REP_ANCHOR', 'Anchor or outpost', 'Calling the vehicle again respawns it at full health', '60 s cooldown after a destroyed vehicle', ''],
    ['REP_AUTO', 'Self-repair', 'None for parts; hull regenerates 0', '-', ''],
   ])

# ------------------------------------------------------------------ ONBOARDING (first 120 minutes)
# (from, to, location, beat, mechanic, popup/tut, method, gate, failsafe, expected state)
SEG = [
 (0, 1, 'Title, settings first boot', 'Language, subtitles size, brightness, colorblind, Assist toggle offered on one screen', 'Accessibility first', 'CNF_FIRSTBOOT', 'Menu', 'Confirm', 'Defaults kept after 60 s idle', 'Lvl 1'),
 (1, 5, 'Cold open CIN_OPEN', 'Meridian falls; Ires says "Accept."', 'None (skippable on 2nd play)', '-', 'Cinematic', 'Ends', 'Skip hold 1.5 s', 'Lvl 1'),
 (5, 6, 'Bay 9 cryo pod', 'Pod opens; Old Tomas pulls the player out', 'Look (camera) only', 'TUT_MOVE (look half)', 'Do', 'Look at Tomas 1 s', 'Tomas calls out after 10 s', 'Lvl 1'),
 (6, 11, 'Bay 9 cryo scanner', 'Scanner reads the player: character creator and Origin pick', 'Character creator', '-', 'Menu (diegetic scanner)', 'Begin pressed', 'None; creator has no timer', 'Origin set'),
 (11, 12, 'Cryo ward', 'Walk to Tomas through the ward', 'Move, sprint', 'TUT_MOVE, TUT_SPRINT', 'Do', 'Reach Tomas (25 m)', 'Re-prompt after 15 s idle', ''),
 (12, 13, 'Cryo ward debris', 'Crawl under a beam, hop a gap', 'Crouch, jump', 'TUT_SNEAK (crouch half)', 'Do', 'Pass beam', 'Context prompt glows', ''),
 (13, 14, 'Dead sleeper', 'Pick up Bay 9 tag; Ostra speaks: "Bay 9. You were not scheduled to wake."', 'Interact, loot', 'TUT_LOOT', 'Do', 'Pick tag', 'Tag pulses after 10 s', 'Ostra online'),
 (14, 15, 'Locker', 'Take starter weapon from Origin kit', 'Equip', 'TUT_INV', 'Do', 'Weapon drawn', 'Auto-equip after 30 s', 'Kit equipped'),
 (15, 17, 'Ward hallway', 'First fight: 1 Hollowed shambler (ACT_VAR_R1_01) at level 1', 'Light attack, lock-on', 'TUT_LIGHT, TUT_LOCK', 'Do', 'Kill', 'Enemy deals 50% damage in prologue; cannot kill player before minute 20 (min 1 HP)', ''),
 (17, 18, 'Ward hallway', 'Second shambler telegraphs a lunge (ATK_HOLLOWED_FODDER_2)', 'Roll', 'TUT_ROLL', 'Slow-mo 0.3x for 0.5 s at telegraph, first time only', 'Roll through 1 attack', 'Repeat telegraph until rolled (max 3, then continue)', ''),
 (18, 20, 'Ward hallway', 'Two more shamblers', 'Heavy attack, Breath bar', 'TUT_HEAVY, TUT_BREATH', 'Do', 'Kill both', 'Prompt reappears if Breath empties', 'Blades/Heavy skill rank +1'),
 (20, 21, 'Med bay', 'Take a hit on purpose (scripted fall), drink Tonic', 'Tonic', 'TUT_TONIC', 'Do', 'Drink', 'Tomas hands a spare if wasted', '4 Tonics'),
 (21, 23, 'Med bay to Spine lift', 'Ostra and Tomas talk; lore walk; first lore item', 'Lore pickup, reading', 'NTF_LORE_NEW', 'See', 'Walk to lift', '-', ''),
 (23, 24, 'Spine lift (load hide)', 'Lift ride; MQ_P_01 complete; MQ_P_02 starts', 'Quest toast', 'NTF_QUEST_DONE', 'See', 'Lift arrives', '-', 'Ember ~120'),
 (24, 26, 'Spine base', 'Thorn scout with a shield (ACT_VAR_R1_05) blocks the path', 'Block, guard break', 'TUT_BLOCK', 'Do', 'Block 2 hits', 'Repeat; after 3 fails, the scout drops his guard', ''),
 (26, 28, 'Spine base', 'Same scout, parry window shown', 'Parry and riposte', 'TUT_PARRY', 'Do, optional', 'Parry 1 or kill', 'Skippable: kill any way', 'Guard skill +1'),
 (28, 30, 'Spine armory', 'Salvaged pistol (ITM_WPN_PST_01) given by Tomas', 'Aim (1P switch), fire, reload', 'TUT_AIM, TUT_RELOAD', 'Do', 'Hit 3 targets on a shooting wall (10 m)', 'Targets enlarge after 20 s', 'Firearms rank +1'),
 (30, 32, 'Spine gantry', 'Remnant drone (Iron Ward) at 20 m', 'Ward: Weave hits Ward, Kinetic hits flesh; weapon swap', 'TUT_WARD, TUT_SWAP', 'Do', 'Break Ward then kill', 'Ostra repeats the tip after 30 s', ''),
 (32, 34, 'Spine gantry', 'Ostra unlocks Cast slot (Origin element)', 'Cast ability', 'TUT_CAST', 'Do', 'Hit a group of 3 Hollowed', 'Cooldown shortened to 5 s in tutorial', 'Rite skill +1'),
 (34, 36, 'Spine climb', 'Climb with ledges, 2 shortcut doors opened from one side', 'Shortcut rule (doors open from one side)', 'PRM_DOOR_ONEWAY', 'See', 'Open shortcut', 'Door handle glows', ''),
 (36, 38, 'First Anchor', 'Light the Anchor; rest; enemies respawn; Tonics refill', 'Anchor, rest, respawn', 'TUT_ANCHOR', 'Do', 'Kindle Anchor', '-', 'STR_ACH_01 unlocks'),
 (38, 40, 'First Anchor', 'Spend Ember: kindle level 2; Vigor point', 'Level up, Vigor', 'TUT_LEVEL', 'Do (menu)', 'Spend or close', 'Ember shown with arrow', 'Lvl 2'),
 (40, 42, 'Upper Spine', 'Bridge collapse forces a death drop in a pit of Hollowed (scripted, cannot be avoided once)', 'Death, Shard-ghost', 'TUT_DEATH', 'Do', 'Respawn at Anchor', 'Only scripted death in the game', 'Ember on ghost'),
 (42, 44, 'Upper Spine', 'Run back, recover the Shard-ghost', 'Recover Ember', 'PRM_GHOST_NEAR, NTF_EMBER_RECOVER', 'Do', 'Touch ghost', 'Ghost beam visible 60 m', ''),
 (44, 46, 'Upper Spine', 'Mixed group: 2 fodder, 1 artillery', 'Free practice, combine tools', '-', 'Do', 'Clear', '-', ''),
 (46, 48, 'Officer deck', 'Shard scar flares: Strike unlocked', 'Strike ability', 'TUT_STRIKE', 'Do', 'Use Strike once', '-', ''),
 (48, 52, 'Officer deck arena', 'Mini-boss: Hollowed crew officer (2 phases, stance 60)', 'Poise and stance break, crit', 'TUT_POISE', 'Do', 'Kill', 'After 2 deaths: Tomas joins as summon (Echo preview)', 'Lvl 3'),
 (52, 54, 'Officer deck', 'Ostra calls the Shard "mine"; silence beat', 'Story', '-', 'Cinematic (in-engine, 60 s)', 'Ends', '-', ''),
 (54, 56, 'Spinegate lower door', 'Exit into Cinderreach; vista; act title card', 'Horizon promise, map dark', 'TUT_MAP', 'See', 'Walk out', '-', 'MQ_P_02 done'),
 (56, 60, 'Cinderreach road', 'Road to Emberwatch; Relay Tower visible; 1 patrol (ENC_PATROL_REG_01)', 'Open-world travel, marker', 'TUT_EXPLORER (offer), NTF_QUEST_NEW', 'Do', 'Reach waypoint', 'Explorer mode prompt once', ''),
 (60, 63, 'Cinderreach road', 'Optional: Relay Tower climb (fills map)', 'Relay Tower', 'TUT_TOWER', 'Do, optional', 'Climb or skip', 'Tomas mentions it again at Kiln', ''),
 (63, 66, 'Hamlet edge', 'MQ_A1_01 choice: save people (3 waves) or save Anchor', 'Choice with consequence', 'CNF_CHOICE', 'Do', 'Pick', '-', ''),
 (66, 74, 'Hamlet', 'Waves branch (8 min) or Anchor branch (4 min + 4 min free roam)', 'Encounter loop, Surge', 'TUT_SURGE', 'Do', 'Branch done', 'Surge meter forced full once', 'Lvl 4'),
 (74, 76, 'Emberwatch', 'Arrive; Reeve Annik; survivors count', 'Town, NPC talk', 'TUT_DIALOGUE', 'Do', 'Talk', '-', ''),
 (76, 78, 'Emberwatch forge', 'Smith: upgrade weapon to +1', 'Smithing', 'TUT_SMITH', 'Do', 'Upgrade +1', 'Smith gives 2 Hull Scrap if short', ''),
 (78, 80, 'Emberwatch', 'Vendor; skills menu; first skill rank-up toast earlier now explained', 'Skills and XP from use', 'TUT_SKILLS', 'Do (menu)', 'Open skills', '-', ''),
 (80, 82, 'Emberwatch', 'Perk point spent', 'Perks', 'TUT_PERKS', 'Do (menu)', 'Spend or close', '-', ''),
 (82, 86, 'Kilns', 'MQ_A1_02 Kessa Vane found hiding', 'Speech check preview', '-', 'Do', 'Talk', '-', ''),
 (86, 92, 'Kilns yard', 'Kessa squad arrives: fight or talk (Speech 25 / Hull Knight Friendly)', 'Skill checks in dialogue', 'TUT_DIALOGUE', 'Do', 'Resolve', '-', ''),
 (92, 94, 'Emberwatch', 'Kessa joins', 'Companion commands', 'TUT_COMPANION', 'Do', 'Issue 1 command', '-', 'STR_ACH_23'),
 (94, 98, 'Kiln outskirts', 'Optional ruin with a locked chest and a sleeping Thorn camp', 'Stealth, lockpick, sneak attack', 'TUT_SNEAK, TUT_LOCKPICK', 'Do, optional', 'Leave area', 'Kessa says "Low and quiet." on approach', 'Infiltration +1'),
 (98, 102, 'Road east', 'Skimmer at a wrecked outpost; drive to the next Anchor', 'Vehicle', 'TUT_VEHICLE', 'Do', 'Drive 300 m', 'Walk is allowed', ''),
 (102, 106, 'Ember field', 'Status effects: Burn on enemies near Ember vents', 'Status buildup', 'TUT_STATUS', 'See and do', 'Proc 1 status', '-', ''),
 (106, 110, 'Site entrance: wreck section', 'First site (10-25 min loop starts)', 'Site loop, shortcut back', '-', 'Do', 'Enter', '-', 'Lvl 5'),
 (110, 116, 'Site interior', 'Clear half the site, open the shortcut', 'Shortcut, lore item', 'PRM_DOOR_ONEWAY', 'Do', 'Shortcut open', '-', ''),
 (116, 118, 'Site', 'First Step ability unlocked from Origin skill rank', 'Step ability', 'TUT_STEP', 'Do', 'Use Step', '-', ''),
 (118, 120, 'Site rest point', 'Anchor; save; end of onboarding window. Remaining tutorials (Echo, co-op, notes, faction, Resonance, Quiet) fire in context later', 'Handoff to open play', 'TUT_ECHO (on first boss death), TUT_COOP, TUT_NOTES', 'Contextual', '-', '-', 'Lvl 5, ~1.3k Ember spent'),
]
rows = []
for a, b, loc, beat, mech, tut, meth, gate, fs, state in SEG:
    for m in range(a, b):
        rows.append([m, m + 1, loc, beat if m == a else '(continues) ' + beat, mech, tut if m == a else '', meth, gate if m == b - 1 else '', fs if m == a else '', state if m == b - 1 else ''])
assert len(rows) == 120 and rows[-1][1] == 120
wr('onboarding_first2h.csv', ['minute_from', 'minute_to', 'location', 'beat', 'mechanic_taught', 'popup_ids', 'teaching_method', 'gate_to_continue', 'failsafe', 'expected_state'], rows)

wr('onboarding_rules.csv',
   ['rule_id', 'rule', 'value'],
   [
    ['ONB_ONE_AT_A_TIME', 'New mechanics per minute', 'Max 1 new verb per 2 minutes in the first 60 minutes'],
    ['ONB_PRACTICE', 'Practice before test', 'Each new verb used 3 times in a safe space before a fight needs it'],
    ['ONB_TEXT', 'Tutorial text length', 'Title <= 20 chars, body <= 90 chars English (popups.csv max_chars)'],
    ['ONB_REPROMPT', 'Re-prompt', 'Unused verb re-prompts after 15 s of being needed, then every 30 s, max 3'],
    ['ONB_SKIP', 'Skip', 'Options > Tutorials: Off skips all TUT_* popups (still in Codex); New Game+ defaults Off'],
    ['ONB_CODEX', 'Codex', 'Every TUT_* seen is saved to the Codex Tutorials tab with an animated loop'],
    ['ONB_DEATH_SAFE', 'Prologue safety', 'Minutes 0-20: player cannot die (min 1 HP); enemies x0.5 damage until minute 40'],
    ['ONB_SCRIPTED_DEATH', 'Teach death', 'Exactly one scripted death (minute 40) so the Shard-ghost rule is learned at low stakes'],
    ['ONB_TELEMETRY', 'Funnel metrics', 'Log time per segment; flag any segment where median > 1.5x planned or quit rate > 3%'],
    ['ONB_TARGETS', 'Targets (plan 3.3, 6.4)', '95% reach minute 54 exit; 85% reach Emberwatch; 70% finish the first site inside 2 h; no confusion point hit by > 20%'],
    ['ONB_PACE_CHECK', 'Level check', 'Level 5 at minute 120 vs design/loops/progression_pacing.csv (level 4 at 1.8 h on the region rate); prologue XP bonus covers the gap'],
   ])

# ------------------------------------------------------------------ BALANCE (computed from data/)
lvl = {int(r['Level']): r for r in rd('actors/level_curve.csv')}
grades = {r['grade']: float(r['coef_at_plus0']) for r in rd('items/scaling_grades.csv')}
curve = [(float(r['attribute_value']), float(r['stat_factor'])) for r in rd('items/stat_curve.csv')]
def sf(v):
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        if v <= x1: return y0 + (y1 - y0) * (v - x0) / (x1 - x0)
    return curve[-1][1]
bands = {r['region_id']: r for r in rd('items/drop_rarity_by_region.csv')}
stats = {}
for r in rd('actors/enemy_stats_by_level.csv'):
    stats[(r['ACT_ID'], int(r['Level']))] = r
enemies = {r['ACT_ID']: r for r in rd('actors/enemies.csv')}
def _regs(e):  # data has used both REG_01 and short R1 / RQ / RU forms; accept either
    out = set()
    for t in e['Regions'].split():
        out.add(t)
        if len(t) == 2 and t[0] == 'R': out.add('REG_0' + t[1] if t[1].isdigit() else 'REG_' + t[1])
    return out
frames = rd('items/melee_frame_data.csv')
mcls = rd('items/melee_classes.csv'); fcls = rd('items/firearm_classes.csv')

def build(L):
    """On-curve build: primary attribute 16 at start + 70% of attribute points; secondary 10 + 30%."""
    pts = int(lvl[min(L, 100)]['Attribute points total'])
    return min(60, 16 + 0.7 * pts), min(60, 10 + 0.3 * pts)

def melee_dps(c, L, u):
    prim, sec = build(L)
    g = c['default_grades_MFLG']; gs = sorted([grades[x] for x in g], reverse=True)
    coef_u = 1 + 0.025 * u
    ar = float(c['base_ar']) * (1 + 0.075 * u) + float(c['base_ar']) * coef_u * (gs[0] * sf(prim) + gs[1] * sf(sec))
    lights = [f for f in frames if f['weapon_class'] == c['name'] and f['attack'].startswith('Light')]
    mv = st.mean(float(f['motion_value']) for f in lights)
    cyc = st.mean((int(f['startup_frames']) + int(f['active_frames']) + int(f['recovery_frames'])) for f in lights) / 60
    # Breath limits a string: lights from a 100+Vigor bar, regen 40/s after 1.2 s; uptime factor 0.6 (dodging, spacing)
    wmax = float(c['weight_max']); up = 0.65 if wmax <= 5 else (0.6 if wmax <= 10 else 0.5)  # heavier = longer commits, more Breath
    return ar * mv / cyc * up, ar, ar * mv

def gun_dps(c, L, u):
    prim, _ = build(L)
    imp = float(c['impact']) * float(c['pellets'])
    dmg = imp * (1 + 0.075 * u) * (1 + grades[c['scaling_grade']] * (1 + 0.025 * u) * sf(prim))
    rps = float(c['rpm']) / 60; mag = float(c['mag'])
    sustained = dmg * mag / (mag / rps + float(c['reload_s']))
    return sustained * 0.75, dmg  # 0.75 accuracy x uptime on body shots

BANDREG = ['REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06', 'REG_Q']
dps_rows = []; dps_by = {}
for reg in BANDREG:
    b = bands[reg]; L = (int(b['level_min']) + int(b['level_max'])) // 2
    u = (int(b['drop_upg_min']) + int(b['drop_upg_max'])) // 2
    vals = []
    for c in mcls:
        d, ar, _ = melee_dps(c, L, u); vals.append(('Melee', c['name'], c['class_id'], d, ar))
    for c in fcls:
        d, dm = gun_dps(c, L, u); vals.append(('Firearm', c['name'], c['class_id'], d, dm))
    med = st.median(v[3] for v in vals)
    dps_by[reg] = (L, u, med, {v[2]: v[3] for v in vals})
    for kind, name, cid, d, per in vals:
        dev = d / med - 1
        flag = 'OK' if abs(dev) <= 0.25 else ('HIGH' if dev > 0 else 'LOW')
        if cid in ('ITM_CLS_SHD',): flag += ' (shield: utility, exempt)'
        if cid in ('ITM_CLS_LCH', 'ITM_CLS_SNP'): flag += ' (burst class: judged on TTK, ammo-limited)'
        dps_rows.append([reg, L, u, kind, cid, name, round(per, 1), round(d, 1), round(med * 0.8, 1), round(med * 1.2, 1), f'{dev:+.0%}', flag])
wr('balance_dps_bands.csv',
   ['region', 'band_mid_level', 'upgrade', 'kind', 'class_id', 'class', 'damage_per_hit_or_shot', 'effective_dps', 'target_dps_min', 'target_dps_max', 'vs_band_median', 'status'], dps_rows)

TTK = {  # seconds solo; derived from loops 01-combat.md light-hit counts x ~0.9 s per landed light
 'Fodder': (1.5, 3.5), 'Skirmisher': (2.5, 5), 'Artillery': (2.5, 5), 'Shield-bearer': (6, 10), 'Heavy': (12, 18), 'Leader': (9, 14)}
LIGHTS = {'Fodder': (2, 3), 'Skirmisher': (3, 4), 'Artillery': (3, 4), 'Shield-bearer': (6, 8), 'Heavy': (14, 18), 'Leader': (10, 14)}
sts = next(c for c in mcls if c['class_id'] == 'ITM_CLS_STS')
ttk_rows = []; hpfix = collections.defaultdict(list); dmgfix = collections.defaultdict(list)
for reg in BANDREG:
    L, u, med, by = dps_by[reg]
    for eid, e in enemies.items():
        if e['Tier'] not in ('Base', 'Leader') or reg not in _regs(e): continue
        s = stats.get((eid, L)) or stats.get((eid, min(max(L, int(e['Level band'].split('-')[0])), int(e['Level band'].split('-')[1]))))
        if not s: continue
        hp, ward, de = float(s['HP']), float(s['Ward']), float(s['Defense'])
        defk = 100 / (100 + de)
        mel = by['ITM_CLS_STS'] * defk * (0.7 if e['Role'] == 'Shield-bearer' else 1.0); gun = by['ITM_CLS_ARF'] * defk  # shield-bearers block 30% of melee uptime
        hitdmg = melee_dps(sts, L, u)[2] * defk
        lights = (ward / 1.5 + hp) / hitdmg
        t_m = (ward / 1.5 + hp) / mel + (2.0 if ward else 0)  # melee Weave-infused assumption on Ward: x1.5; 2 s swap/stance allowance
        t_g = (ward / 0.5 + hp) / gun if ward else hp / gun  # pure kinetic gun into Ward x0.5 (worst case)
        t_g_mix = (ward / 1.5) / (by['ITM_CLS_LNC'] * defk) + hp / gun + 0.66 if ward else t_g  # Lance pops Ward, swap, rifle
        lo, hi = TTK[e['Role']]
        def fl(t): return 'OK' if lo * 0.8 <= t <= hi * 1.25 else ('SLOW' if t > hi else 'FAST')
        llo, lhi = LIGHTS[e['Role']]
        ttk_rows.append([reg, L, eid, e['Role'], int(hp), int(ward), int(de), lo, hi, round(lights, 1), f'{llo}-{lhi}', round(t_m, 1), fl(t_m), round(t_g_mix, 1), fl(t_g_mix), round(t_g, 1),
                         f'{abs(t_m - t_g_mix) / max(t_m, t_g_mix):.0%}', round((llo + lhi) / 2 / lights, 2)])
        hpfix[reg].append((llo + lhi) / 2 / lights)
wr('balance_ttk.csv',
   ['region', 'level', 'act_id', 'role', 'hp', 'ward', 'defense', 'target_ttk_min_s', 'target_ttk_max_s', 'sword_lights_to_kill', 'loops_target_lights', 'ttk_straight_sword_s', 'melee_status', 'ttk_lance_then_auto_rifle_s', 'gun_status', 'ttk_kinetic_only_s', 'melee_vs_gun_gap', 'enemy_hp_mult_to_hit_loops_target'], ttk_rows)

# Incoming damage: share of on-curve player HP per hit
amult = collections.defaultdict(list)
for r in rd('actors/enemy_attacks.csv'):
    if float(r['Damage mult']) > 0: amult[r['ACT_ID']].append(float(r['Damage mult']))
inc = []
TARGET_IN = {'Fodder': (6, 12), 'Skirmisher': (8, 14), 'Artillery': (8, 14), 'Shield-bearer': (8, 14), 'Heavy': (15, 25), 'Leader': (10, 18)}  # typical hit
for reg in BANDREG:
    L = dps_by[reg][0]
    vig = int(lvl[L]['Vigor points total']); _, grit = build(L)
    php = 400 + 8 * (vig * 0.5) + 4 * (grit - 10)  # half of Vigor in Health; Grit as secondary
    absorb = 0.10 + 0.004 * L  # medium armor on curve: 10% at L0 to ~42% at L80 (armor_pieces median trend, choice)
    for role, (lo, hi) in TARGET_IN.items():
        eid = next((k for k, e in enemies.items() if e['Role'] == role and e['Tier'] in ('Base', 'Leader') and reg in _regs(e)), None)
        if not eid: continue
        s = stats.get((eid, L))
        if not s: continue
        base = float(s['Damage per 1.0 mult']) * (1 - absorb)
        typ = base * st.mean(amult[eid]); big = base * max(amult[eid])
        pct = typ / php * 100; pbig = big / php * 100
        inc.append([reg, L, int(php), f'{absorb:.0%}', role, eid, round(typ, 1), round(pct, 1), round(pbig, 1), lo, hi, 'OK' if lo * 0.85 <= pct <= hi * 1.15 else ('HIGH' if pct > hi else 'LOW'), max(1, int(php // max(typ, 1))), round((lo + hi) / 2 / pct, 2)])
        dmgfix[reg].append((lo + hi) / 2 / pct)
wr('balance_incoming.csv',
   ['region', 'level', 'player_hp_on_curve', 'player_absorb', 'role', 'act_id', 'typical_hit', 'typical_pct_of_hp', 'biggest_hit_pct', 'target_pct_min', 'target_pct_max', 'status', 'hits_to_kill_player', 'enemy_dmg_mult_to_hit_target'], inc)
wr('balance_curve_fix.csv', ['region', 'band_mid_level', 'median_enemy_hp_mult_needed', 'min', 'max', 'median_enemy_damage_mult_needed', 'proposal'],
   [[r, dps_by[r][0], round(st.median(hpfix[r]), 2), round(min(hpfix[r]), 2), round(max(hpfix[r]), 2), round(st.median(dmgfix[r]), 2),
     'Scale enemy_stats_by_level HP and damage by these factors at band mid (lerp between bands), then rerun this script; SUPERSEDED by enemy_curve_target.csv (DR-SYS-010 rev 2)'] for r in BANDREG])

wr('balance_targets.csv',
   ['bal_id', 'metric', 'target', 'measured_by', 'source'],
   [
    ['BAL_TTK_TIER', 'TTK per enemy tier (solo, level-matched)', 'Fodder 2-4 s; Skirmisher/Artillery 4-7 s; Shield-bearer 8-14 s; Heavy 18-30 s; Leader 14-22 s', 'balance_ttk.csv', 'Shardfall choice; hit counts in design/loops/01-combat.md'],
    ['BAL_TTK_BOSS', 'Boss TTK', 'Site boss 90-140 s; field 120-180 s; Citadel 180-300 s; Shard-bearer 240-420 s solo; raid boss 6-10 min at 6 players', 'Boss sim from bosses.csv HP vs band median DPS', 'loops 01-combat.md (site, Shard-bearer); others Shardfall choice'],
    ['BAL_DPS_BAND', 'Class DPS spread', 'Every non-burst, non-shield class within +/-20% of band median effective DPS', 'balance_dps_bands.csv', 'Pillar 4'],
    ['BAL_PARITY', 'Melee vs gun parity', 'Clear time gap <= 15% per encounter template', 'balance_ttk.csv melee_vs_gun_gap; Gate 2 playtests', 'Plan 2.2'],
    ['BAL_INCOMING', 'Damage taken per hit', 'Fodder 6-12% HP; Heavy 25-38%; boss heavy 35-55%; no single non-grab hit over 70% at on-curve HP', 'balance_incoming.csv', 'Shardfall choice'],
    ['BAL_DEATHS', 'Deaths per hour (main path)', 'Region 1: 1-3; Region 6: 3-6; Shard-bearer median first kill 3-12 attempts', 'Telemetry', 'Plan 5.4'],
    ['BAL_KNEW', 'I knew why I died', '>= 80% yes', 'Post-death prompt in playtests', 'Plan 2.1'],
    ['BAL_LEVEL_TIME', 'Time to level', 'As design/loops/progression_pacing.csv (owned by loops); campaign 35-45 h main path, 60-90 h full', 'Progression sim', 'Loops thread, plan 3.3'],
    ['BAL_SESSION', 'Session pacing', 'As design/loops/session_30min.csv; a level-up or gear upgrade every 30-45 min', 'Telemetry', 'Loops thread'],
    ['BAL_ENC_LEN', 'Encounter length', '30-60 s (plan 3.3); camp 90-150 s', 'Telemetry', 'Plan 3.3'],
    ['BAL_SURGE', 'Surge cadence', 'One per 2-3 encounters (120-180 s combat)', 'Telemetry', 'loops 01-combat.md'],
    ['BAL_TONIC', 'Tonic use', '0-1 per encounter, 1-3 per boss attempt', 'Telemetry', 'loops 01-combat.md'],
    ['BAL_UNDERLEVEL', 'Under-level penalty', '5 levels under band mid: TTK x1.4, damage taken x1.3; 10 under: x2.0 / x1.7', 'Sim', 'Shardfall choice'],
    ['BAL_COOP', 'Co-op TTK', 'Boss TTK at 2/3/4 players = 0.95/0.90/0.85 of solo (scaling 1.7/2.3/2.9)', 'Sim with coop_scaling.csv', 'Plan 1b gap values'],
    ['BAL_PVP_TTK', 'Arena TTK (normalized L80)', 'Primary weapons 0.9-1.6 s optimal; melee 3-4 hits; Shard Lance 2 hits', 'Arena sim', 'Shardfall choice, Halo/Destiny range'],
    ['BAL_STEALTH', 'Stealth viability', 'A full camp (ENC_CAMP) can be cleared unseen by an Infiltration 40 build in 3-5 min', 'Playtest', 'Shardfall choice'],
    ['BAL_VEH', 'Vehicle TTK', 'Skimmer killed by 1 launcher hit + 4 s of Weave fire; Hauler needs 3 launcher hits or 2 engine-focused Lance shots + wheels; Flyer: 2 wing hits with explosives', 'vehicle_parts.csv', 'Shardfall choice'],
   ])

# ------------------------------------------------------------------ ACHIEVEMENTS
ACH = {  # n: (condition, stat, threshold, grade, hidden, missable, coop_credit, data_ids)
 1: ('Kindle any Anchor', 'anchors_kindled', 1, 'B', 0, 0, 1, 'TUT_ANCHOR'),
 2: ('MQ_A1_05 complete (Vael defeated, Heart Shard taken or spared)', 'shard_REG_01', 1, 'S', 0, 0, 1, 'ACT_BOSS_VAEL'),
 3: ('MQ_A1_08 complete (Corsa)', 'shard_REG_02', 1, 'S', 0, 0, 1, 'ACT_BOSS_CORSA'),
 4: ('Thornwood Shard-bearer defeated', 'shard_REG_03', 1, 'S', 0, 0, 1, 'ACT_BOSS_SORREL'),
 5: ('Glasswaste Shard-bearer defeated', 'shard_REG_04', 1, 'S', 0, 0, 1, 'ACT_BOSS_BRANNOCH'),
 6: ('Rimefall Shard-bearer defeated', 'shard_REG_05', 1, 'S', 0, 0, 1, 'ACT_BOSS_RIME'),
 7: ('Hollowdeep Shard-bearer defeated', 'shard_REG_06', 1, 'S', 0, 0, 1, 'ACT_BOSS_HOLLOWTWINS'),
 8: ('Ending: Restore the Meridian', 'ending_restore', 1, 'G', 1, 0, 0, 'design/campaign/04-choices-and-endings.md'),
 9: ('Ending: Bind the Shards', 'ending_bind', 1, 'G', 1, 0, 0, ''),
 10: ('Ending: Take the Quiet', 'ending_take', 1, 'G', 1, 0, 0, ''),
 11: ('Climb all Relay Towers (6 surface regions)', 'relay_towers', 6, 'S', 0, 0, 0, 'TUT_TOWER'),
 12: ('Discover 100% of map cells in REG_01..06', 'map_pct_all', 100, 'G', 0, 0, 0, 'world/locations.csv'),
 13: ('Enter REG_U', 'reg_u_entered', 1, 'B', 0, 0, 1, 'REG_U'),
 14: ('Reach Act 3 (enter REG_Q)', 'reg_q_entered', 1, 'S', 0, 0, 1, 'REG_Q'),
 15: ('Defeat 12 field bosses', 'bosses_field', 12, 'S', 0, 0, 1, 'ACT_BOSS (Field)'),
 16: ('Defeat 12 site bosses', 'bosses_site', 12, 'S', 0, 0, 1, 'ACT_BOSS (Site)'),
 17: ('Defeat 6 Citadel bosses', 'bosses_citadel', 6, 'G', 0, 0, 1, 'ACT_BOSS (Citadel)'),
 18: ('Hull Knights reputation Exalted', 'rep_FAC_HULLKNIGHTS', 'REP_EXALTED', 'S', 0, 1, 0, 'reputation_tiers.csv'),
 19: ('Lantern Church Exalted', 'rep_FAC_LANTERN', 'REP_EXALTED', 'S', 0, 1, 0, ''),
 20: ('Salvagers Guild Exalted', 'rep_FAC_SALVAGERS', 'REP_EXALTED', 'S', 0, 1, 0, ''),
 21: ('Quiet Hand Exalted', 'rep_FAC_QUIETHAND', 'REP_EXALTED', 'S', 0, 1, 0, ''),
 22: ('Choir Exalted', 'rep_FAC_CHOIR', 'REP_EXALTED', 'S', 0, 1, 0, ''),
 23: ('Recruit any companion', 'companions', 1, 'B', 0, 0, 0, 'ACT_CMP_C1'),
 24: ('Recruit all 8 companions in one save', 'companions', 8, 'G', 0, 1, 0, 'ACT_CMP_C1..C8'),
 25: ('Any companion approval >= 75 (loyal)', 'cmp_approval_max', 75, 'S', 0, 0, 0, '04-choices-and-endings.md'),
 26: ('Finish any companion questline', 'cmp_lines_done', 1, 'S', 0, 0, 0, 'quests.csv'),
 27: ('Any skill rank 100', 'skill_max', 100, 'S', 0, 0, 0, 'skills.csv'),
 28: ('Make a skill Legendary (reset at 100)', 'skill_legendary', 1, 'S', 0, 0, 0, 'DR-SYS-004'),
 29: ('All 14 skills rank 50+', 'skills_at_50', 14, 'G', 0, 0, 0, ''),
 30: ('All nodes in one perk tree', 'perk_tree_full', 1, 'S', 0, 0, 0, 'perks.csv'),
 31: ('Level 25', 'level', 25, 'B', 0, 0, 0, 'level_curve.csv'),
 32: ('Level 50', 'level', 50, 'S', 0, 0, 0, ''),
 33: ('Level 70', 'level', 70, 'S', 0, 0, 0, ''),
 34: ('Own any Shardborn', 'shardborn_owned', 1, 'B', 0, 0, 1, 'shardborn.csv'),
 35: ('Own 20 different Shardborn', 'shardborn_owned', 20, 'G', 0, 0, 1, ''),
 36: ('Any weapon at +20 (Shardborn +10)', 'weapon_max_upg', 1, 'S', 0, 0, 0, 'upgrade_costs.csv'),
 37: ('Craft 1 Rite', 'rites_crafted', 1, 'B', 0, 0, 0, 'rite_crafting.csv'),
 38: ('Learn all Brewing recipes', 'brew_recipes', 'all RCP brewing', 'S', 0, 0, 0, 'crafting_recipes.csv'),
 39: ('100 successful parries (lifetime)', 'parries', 100, 'B', 0, 0, 1, 'STAT_PARRY'),
 40: ('500 enemy Wards broken', 'wards_broken', 500, 'B', 0, 0, 1, 'FRM_WARDHIT'),
 41: ('Burn, Shock, Drain, Slow, Root, Shatter on enemies in one combat', 'status_set_combat', 6, 'S', 0, 0, 1, 'STS_*'),
 42: ('50 pickpockets without being caught (lifetime, fail does not reset)', 'pickpockets', 50, 'B', 0, 0, 0, 'STA_PICKPOCKET'),
 43: ('50 Speech checks passed', 'speech_checks', 50, 'B', 0, 0, 0, 'SKL_SPEECH'),
 44: ('Recover Shard-ghost 25 times', 'ghosts_recovered', 25, 'B', 0, 0, 0, 'NTF_EMBER_RECOVER'),
 45: ('From entering a region to its Shard-bearer kill with 0 deaths in that region', 'deathless_region', 1, 'G', 0, 0, 0, ''),
 46: ('As a summoned guest, host defeats a boss', 'boss_helped', 1, 'B', 0, 0, 1, 'MM_COOP_SIGN'),
 47: ('Kill a host as invader', 'invader_kills', 1, 'B', 0, 0, 0, 'FAC_QUIETHAND'),
 48: ('Kill 10 invaders as host or guest', 'invaders_killed', 10, 'B', 0, 0, 1, ''),
 49: ('Complete any Strike', 'strikes', 1, 'B', 0, 0, 1, 'EG_STRIKE'),
 50: ('Strike completions in 4 distinct weekly resets', 'strike_weeks', 4, 'S', 0, 0, 1, 'season_calendar.csv'),
 51: ('Kill all 4 raid bosses (any weeks)', 'raid_clear', 1, 'G', 0, 0, 1, 'EG_RAID'),
 52: ('Full raid clear in one lockout with 0 deaths for all 6 players', 'raid_flawless', 1, 'G', 1, 0, 1, ''),
 53: ('Win any Arena match', 'arena_wins', 1, 'B', 0, 0, 0, 'EG_ARENA'),
 54: ('3 kills with one power weapon pickup', 'pwr_kills_one', 3, 'B', 0, 0, 0, 'ITM_PWR_*'),
 55: ('Continuous glide of 500 m on a Strider', 'glide_m', 500, 'B', 0, 0, 0, 'Strider'),
 56: ('Complete HJK_AIR', 'flyers_hijacked', 1, 'B', 0, 0, 0, 'HJK_AIR'),
 57: ('100 helpful ratings on Shard-notes', 'notes_rated', 100, 'S', 0, 0, 0, 'TUT_NOTES'),
 58: ("All Ostra memory fragments", 'ostra_fragments', 'all', 'G', 1, 0, 0, '03-main-story.md'),
 59: ('All ship logs (lore_items kind Ship log)', 'ship_logs', 'all', 'G', 0, 0, 0, 'lore_items.csv'),
 60: ('Earn ACH_01..59', 'ach_count', 59, 'P', 0, 0, 0, ''),
}
GS = {'B': 10, 'S': 15, 'G': 25, 'P': 0}
total = sum(GS[v[3]] for v in ACH.values())
# Xbox base game 1000 G: put the remainder on the platinum-equivalent (Shardfall)
plat = 1000 - total
assert 0 <= plat <= 150, plat
ach_rows = []
for n, (cond, stat, thr, g, hid, miss, coop, ids) in ACH.items():
    gs = plat if g == 'P' else GS[g]
    ach_rows.append([f'ACH_{n:02d}', f'STR_ACH_{n:02d}', f'STR_ACH_{n:02d}_DESC', cond, stat, thr, {'B': 'Bronze', 'S': 'Silver', 'G': 'Gold', 'P': 'Platinum'}[g], gs, hid, miss, coop, 'Yes' if n not in (47, 48, 53, 54) else 'No (PvP)', f'UI_ACH_{n:02d}', ids])
assert sum(r[7] for r in ach_rows) == 1000, sum(r[7] for r in ach_rows)
wr('achievements.csv', ['ach_id', 'name_str', 'desc_str', 'unlock_condition', 'tracked_stat', 'threshold', 'ps_trophy', 'xbox_gamerscore', 'hidden', 'missable_in_one_save', 'coop_guest_credit', 'offline_possible', 'icon', 'data_ids'], ach_rows)

# ------------------------------------------------------------------ CHARACTER CREATOR
CC = []
def s(step, oid, label, ctrl, rng, default, inc, drives, note=''):
    CC.append([oid, step, label, ctrl, rng, default, inc, drives, note])
s('Origin', 'CC_ORIGIN', 'STR_CC_STEP_ORIGIN', 'Card list (6)', 'ORG_CRASHKNIGHT..ORG_UNBOUND', 'ORG_CRASHKNIGHT', '-', 'origins.csv stats and kit', 'Locked after Begin (STR_CC_REVIEW_TEXT)')
s('Body', 'CC_BODY_TYPE', 'STR_CC_BODY_TYPE', 'Toggle', 'Frame A / Frame B', 'Frame A', '-', 'Base skeleton and mesh (two rigs, shared anim set)', 'Not tied to voice or pronouns')
s('Body', 'CC_PRONOUN', 'STR_CC_PRONOUN', 'List', 'they / she / he', 'they', '-', 'NPC text tokens {VAR_pronoun}', 'Independent of frame; new string DR-SYS-006')
for oid, lab, lo, hi, d in [('CC_HEIGHT', 'STR_CC_HEIGHT', 160, 200, 178), ('CC_BUILD', 'STR_CC_BUILD', 0, 100, 50), ('CC_MUSCLE', 'STR_CC_MUSCLE', 0, 100, 40), ('CC_AGE', 'STR_CC_AGE', 18, 70, 32)]:
    s('Body', oid, lab, 'Slider', f'{lo}-{hi}' + (' cm' if oid == 'CC_HEIGHT' else (' years' if oid == 'CC_AGE' else '')), d, 1, {'CC_HEIGHT': 'Root scale 0.9-1.12 (hitbox fixed; camera height follows)', 'CC_BUILD': 'Blend thin<->heavy morph', 'CC_MUSCLE': 'Muscle definition morph + normal blend', 'CC_AGE': 'Skin wrinkle maps, hair grey bias, posture blend'}[oid])
s('Body', 'CC_SKIN', 'STR_CC_SKIN', 'Swatch grid + slider', '36 swatches (Fitzpatrick I-VI x 6 undertones) + fine slider 0-100', 'swatch 14', 1, 'Skin albedo LUT')
s('Body', 'CC_SKIN_WEAR', 'STR_CC_SKIN_WEAR', 'Slider', '0-100', 30, 1, 'Grime, sunburn, cryo-frost burn mask')
s('Body', 'CC_PROSTHETIC', 'STR_CC_PROSTHETIC', 'List per limb', 'None / salvage arm L / R / leg L / R (cosmetic)', 'None', '-', 'Mesh swap, no stat change', 'Fits the salvage setting; DR-SYS-006 strings')
s('Face', 'CC_FACE_PRESET', 'STR_CC_FACE_PRESET', 'Grid (24 per frame)', 'CCP_A01..A24, CCP_B01..B24', 'CCP_A01 / CCP_B01', '-', 'Loads all face sliders', 'See cc_presets.csv')
for oid, lab, subs in [
    ('CC_FACE_SHAPE', 'STR_CC_FACE_SHAPE', ['Width', 'Length', 'Roundness', 'Forehead height', 'Forehead slope', 'Temple width']),
    ('CC_BROW', 'STR_CC_BROW', ['Brow height', 'Brow depth', 'Brow angle', 'Brow ridge', 'Brow shape (12 styles)', 'Brow thickness', 'Brow colour (follows hair, override)']),
    ('CC_EYES', 'STR_CC_EYES', ['Eye size', 'Eye spacing', 'Eye height', 'Eye depth', 'Eye tilt', 'Eyelid fold', 'Lash length', 'Eye shape (10 presets)']),
    ('CC_NOSE', 'STR_CC_NOSE', ['Nose length', 'Bridge height', 'Bridge width', 'Tip height', 'Tip width', 'Nostril width', 'Nose tilt', 'Broken-nose offset']),
    ('CC_CHEEKS', 'STR_CC_CHEEKS', ['Cheekbone height', 'Cheekbone width', 'Cheek fullness', 'Hollow depth']),
    ('CC_MOUTH', 'STR_CC_MOUTH', ['Mouth width', 'Mouth height', 'Upper lip', 'Lower lip', 'Lip corner tilt', 'Mouth depth', 'Lip colour']),
    ('CC_JAW', 'STR_CC_JAW', ['Jaw width', 'Jaw angle', 'Jaw length', 'Chin height', 'Chin width', 'Chin depth', 'Chin cleft']),
    ('CC_EARS', 'STR_CC_EARS', ['Ear size', 'Ear angle', 'Ear lobe', 'Ear point (0 = round)']),
]:
    for i, sub in enumerate(subs, 1):
        style = '(' in sub and 'styles' in sub or 'presets' in sub
        s('Face', f'{oid}_{i:02d}', f'{lab}_{i:02d}', 'List' if style else ('Colour wheel' if 'colour' in sub.lower() else 'Slider'), 'list' if style else ('HSV' if 'colour' in sub.lower() else '-100..100'), 0, 1 if not style else '-', f'Morph target {oid[3:].lower()}_{i:02d}', sub)
s('Face', 'CC_EYE_COLOR', 'STR_CC_EYE_COLOR', 'Swatch (24) + colour wheel', 'HSV; heterochromia toggle', 'swatch 5', '-', 'Iris material')
s('Face', 'CC_EYE_SHARD', 'STR_CC_EYE_SHARD', 'Toggle', 'Off / Left / Right / Both', 'Off', '-', 'Shard fleck in iris glows with scar colour')
s('Face', 'CC_HAIR', 'STR_CC_HAIR', 'Grid', '48 styles (incl. bald, shaved, braids, locs, coils, undercuts)', 'style 01', '-', 'Hair groom asset HAIR_01..48', 'Helmets: hair hidden or compressed per style flag')
s('Face', 'CC_HAIR_COLOR', 'STR_CC_HAIR_COLOR', 'Swatch (32) + colour wheel + tip colour + grey 0-100', 'HSV', 'swatch 3', '-', 'Hair material')
s('Face', 'CC_FACIAL_HAIR', 'STR_CC_FACIAL_HAIR', 'Grid + length slider', '24 styles + none; stubble 0-100', 'none', 1, 'Groom asset BEARD_01..24', 'Available on both frames')
s('Face', 'CC_PAINT', 'STR_CC_PAINT', 'Grid + colour + opacity', '30 designs (faction marks unlock later)', 'none', 1, 'Decal layer', 'Faction designs unlock at Friendly rep')
s('Face', 'CC_MAKEUP', 'STR_CC_MAKEUP', 'Eye / lip / blush each: list + colour + opacity', '12 each', 'none', 1, 'Decal layers', '')
s('Face', 'CC_TATTOO', 'STR_CC_TATTOO', 'Grid, 4 body zones, colour, opacity', '40 designs', 'none', 1, 'Decal layers', '')
s('Face', 'CC_SCARS', 'STR_CC_SCARS', 'Grid (multi-select max 3)', '20 scars', 'none', '-', 'Decal + normal', 'Separate from the Shard scar')
s('Shard Scar', 'CC_SCAR_PLACE', 'STR_CC_SCAR_PLACE', 'List', 'Chest centre / left / right, neck, face left / right, left arm, right arm, back', 'Chest centre', '-', 'Scar decal location (story: the Shard grew in the chest; it spreads along the chosen path)', 'STR_CC_SCAR_HINT')
s('Shard Scar', 'CC_SCAR_SIZE', 'STR_CC_SCAR_SIZE', 'Slider', '0-100', 50, 1, 'Vein spread radius')
s('Shard Scar', 'CC_SCAR_GLOW', 'STR_CC_SCAR_GLOW', 'Slider', '0-100 (idle glow)', 40, 1, 'Emissive; Weave use flares to 100 for 3 s', 'Pure cosmetic; detection uses DET_LIGHT_SCAR regardless')
s('Shard Scar', 'CC_SCAR_COLOR', 'STR_CC_SCAR_COLOR', 'Swatch (8) + colour wheel', 'Default amber #E8B23A', '#E8B23A', '-', 'Emissive colour', 'Element VFX tint stays element-coloured (VB readability rule)')
s('Voice', 'CC_VOICE_PICK', 'STR_CC_VOICE_PICK', 'List', 'VO_PLAYER_1..4', 'VO_PLAYER_1', '-', 'Effort and callout VO set', 'Any voice with any frame')
s('Voice', 'CC_VOICE_PITCH', 'STR_CC_VOICE_PITCH', 'Slider', '-100..100 (+/-3 semitones)', 0, 1, 'Real-time pitch shift on VO bus')
s('Voice', 'CC_VOICE_PREVIEW', 'STR_CC_VOICE_PREVIEW', 'Button', 'Plays 1 of 6 preview lines', '-', '-', 'VO preview')
s('Name', 'CC_NAME', 'STR_CC_STEP_NAME', 'Text field', '2-16 chars; letters, space, apostrophe, hyphen; profanity + reserved-name filter', 'Origin default name', '-', 'Save name; NPCs never speak it', 'STR_CC_ERR_NAME_*; platform text filter API on console')
s('Review', 'CC_REVIEW', 'STR_CC_STEP_REVIEW', 'Turntable + lighting presets', 'Lights: Cryo bay, Daylight, Night, Ember glow; armor preview: Origin kit / none', 'Cryo bay', '-', 'Preview only', 'STR_CC_REVIEW_TEXT; STR_CC_BEGIN')
s('All', 'CC_RANDOM', 'STR_CC_RANDOM', 'Button', 'Randomizes current step within 70% of slider range', '-', '-', '', '')
s('All', 'CC_UNDO', 'STR_CC_UNDO', 'Button', '20-step undo per step', '-', '-', '', '')
s('All', 'CC_SAVE_PRESET', 'STR_CC_SAVE_PRESET', 'Button', '10 local preset slots; share code (16 chars) cross-platform', '-', '-', 'Appearance blob 512 bytes', 'DR-SYS-006 strings')
s('All', 'CC_CAMERA', '-', 'Stick / mouse', 'Zoom 3 levels (body, bust, face), rotate 360, light rotate', '-', '-', '', 'Auto-zoom per step')
s('Post-creation', 'CC_MIRROR', 'STR_CC_MIRROR', 'Mirror in Lantern Hold', 'All steps except Origin', 'Free', '-', 'Same screen', 'Costs 0 Ember; appearance changes are always free')
wr('character_creator.csv', ['option_id', 'step', 'label_str', 'control', 'range_or_options', 'default', 'increment', 'drives', 'notes'], CC)

PRE = []
moods = ['Veteran', 'Scholar', 'Scavenger', 'Pilgrim', 'Ranger', 'Drifter', 'Noble', 'Dockhand', 'Mystic', 'Smith', 'Medic', 'Sentinel']
for fr in 'AB':
    for i in range(1, 25):
        PRE.append([f'CCP_{fr}{i:02d}', f'Frame {fr}', moods[(i - 1) % 12] + (' (older)' if i > 12 else ''), 18 + ((i * 7) % 50), f'swatch {(i * 5) % 36 + 1}', f'style {(i * 3) % 48 + 1}', f'swatch {(i * 7) % 32 + 1}', f'STR_CCP_{fr}{i:02d}', 'Face slider set authored by character art; values in the preset asset'])
wr('cc_presets.csv', ['preset_id', 'frame', 'look', 'age', 'skin', 'hair', 'hair_colour', 'name_str', 'note'], PRE)

# ------------------------------------------------------------------ TARGET ENEMY CURVES (DR-SYS-010 rev 2)
# Rev 1 gave per-band multipliers taken from mixed-faction medians; applied on top of the old curve they made
# HP fall after level 62. Rev 2 gives absolute targets per level, derived from the on-curve player hit, so every
# enemy needs the loops light-hit count at every level and HP rises monotonically.
mids = [(dps_by[r][0], (int(bands[r]['drop_upg_min']) + int(bands[r]['drop_upg_max'])) / 2) for r in BANDREG]
def upg_at(L):  # continuous upgrade level, lerp between band mids, clamped 0..20
    if L <= mids[0][0]: return max(0.0, mids[0][1] * L / mids[0][0])
    for (l0, u0), (l1, u1) in zip(mids, mids[1:]):
        if L <= l1: return u0 + (u1 - u0) * (L - l0) / (l1 - l0)
    return min(20.0, mids[-1][1] + (L - mids[-1][0]) * 0.25)
WARD_SHARE = {'FAC_HOLLOWED': 0, 'FAC_THORN': 0, 'FAC_REMNANT': 0.5, 'FAC_CHOIRBORN': 0.4}
TOUGH = {'FAC_HOLLOWED': 1.0, 'FAC_THORN': 1.1, 'FAC_REMNANT': 1.0, 'FAC_CHOIRBORN': 1.15}  # Thorn sturdier, Choirborn late elites
curve_rows = []; sim = {}
for eid, e in enemies.items():
    if e['Tier'] not in ('Base', 'Leader'): continue
    lo_l, hi_l = map(int, e['Level band'].split('-'))
    llo, lhi = LIGHTS[e['Role']]; tlo, thi = TARGET_IN[e['Role']]
    prev = 0
    for L in range(lo_l, hi_l + 1):
        de = float(stats[(eid, L)]['Defense'])
        hit = melee_dps(sts, L, upg_at(L))[2] * 100 / (100 + de)
        eff = (llo + lhi) / 2 * hit * TOUGH[e['FAC_ID']]
        w = WARD_SHARE[e['FAC_ID']]
        hp = eff / (1 + w / 1.5); ward = hp * w
        vig = int(lvl[L]['Vigor points total']); _, grit = build(L)
        php = 400 + 8 * (vig * 0.5) + 4 * (grit - 10); absorb = 0.10 + 0.004 * L
        d1 = (tlo + thi) / 2 / 100 * php / st.mean(amult[eid]) / (1 - absorb)
        hp, ward, d1 = round(hp), round(ward), round(d1)
        hp = max(hp, prev + 1 if L > lo_l else hp); ward = round(hp * w); prev = hp  # strictly rising
        curve_rows.append([eid, L, hp, ward, int(de), d1, stats[(eid, L)]['HP'], stats[(eid, L)]['Damage per 1.0 mult']])
        sim[(eid, L)] = (hp, ward, de, d1)
wr('enemy_curve_target.csv', ['ACT_ID', 'Level', 'HP_target', 'Ward_target', 'Defense (unchanged)', 'Damage_per_1x_target', 'HP_current_data', 'Damage_current_data'], curve_rows)

# Re-check targets against the proposed curve
chk = []
for reg in BANDREG:
    L, u, med, by = dps_by[reg]
    for eid, e in enemies.items():
        if (eid, L) not in sim or reg not in _regs(e): continue
        hp, ward, de, d1 = sim[(eid, L)]
        defk = 100 / (100 + de); hit = melee_dps(sts, L, u)[2] * defk
        lights = (ward / 1.5 + hp) / hit; llo, lhi = LIGHTS[e['Role']]
        mel = by['ITM_CLS_STS'] * defk * (0.7 if e['Role'] == 'Shield-bearer' else 1.0)
        t_m = (ward / 1.5 + hp) / mel + (2.0 if ward else 0)
        gun = by['ITM_CLS_ARF'] * defk * 1.35  # with DR-SYS-011 applied
        t_g = (ward / 1.5) / (by['ITM_CLS_LNC'] * defk) + hp / gun + 0.66 if ward else hp / gun
        lo, hi = TTK[e['Role']]
        ok = lambda t: 'OK' if lo * 0.8 <= t <= hi * 1.25 else ('SLOW' if t > hi else 'FAST')
        chk.append([reg, L, eid, e['Role'], hp, ward, round(lights, 1), f'{llo}-{lhi}', 'OK' if llo * 0.9 <= lights <= lhi * 1.1 * TOUGH[e['FAC_ID']] else 'OFF',
                    round(t_m, 1), ok(t_m), round(t_g, 1), ok(t_g), f'{abs(t_m - t_g) / max(t_m, t_g):.0%}'])
wr('balance_check_proposed.csv', ['region', 'level', 'act_id', 'role', 'hp', 'ward', 'sword_lights', 'loops_target', 'lights_status', 'ttk_sword_s', 'sword_status', 'ttk_lance_rifle_s', 'gun_status', 'melee_vs_gun_gap'], chk)
