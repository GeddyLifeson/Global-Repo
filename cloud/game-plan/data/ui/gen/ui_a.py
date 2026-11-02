# Shardfall UI text, part A: shared names, common, title, creation, HUD, menus.
# Each block: key|text[|note]. IDs become STR_<PFX>_<KEY>.
R = []  # (id, screen, text, note)

def blk(pfx, screen, body):
    for ln in body.strip('\n').split('\n'):
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        p = ln.split('|')
        R.append((f"STR_{pfx}_{p[0].upper()}", screen, p[1], p[2] if len(p) > 2 else ''))

# ---------- Shared names (Shardfall choices where the plan left gaps) ----------
ELEMENTS = [('EMBER','Ember','Burn','Fire and heat. Sets targets alight.'),
            ('STORM','Storm','Shock','Lightning. Chains between close targets and stalls Ward recharge.'),
            ('HOLLOW','Hollow','Drain','Void from the Shards. Steals Ward and heals you a little.'),
            ('FROST','Frost','Slow','Cold. Slows movement and attack speed.'),
            ('BLOOM','Bloom','Root','Living growth. Roots targets in place.'),
            ('IRON','Iron','Shatter','Kinetic force. Breaks poise and armor.')]
COUNTER = {'EMBER':'Frost','FROST':'Ember','STORM':'Iron','IRON':'Storm','HOLLOW':'Bloom','BLOOM':'Hollow'}
STATUS = [('BURN','Burn','Takes 2% max Health per second for 6 seconds.'),
          ('SHOCK','Shock','Ward recharge stops for 4 seconds. The next hit chains 30% damage to 2 targets within 6 m.'),
          ('DRAIN','Drain','Loses 20 Ward per second for 4 seconds. The attacker gains half.'),
          ('SLOW','Slow','Moves and attacks 30% slower for 6 seconds.'),
          ('ROOT','Root','Cannot move for 2.5 seconds. Can still attack and block.'),
          ('SHATTER','Shatter','Takes 25% more poise and physical damage for 8 seconds.')]
SKILLS = [('STEEL','BLADES','Blades','Daggers, swords and curved swords. Raised by landing hits with them.'),
          ('STEEL','HEAVY','Heavy Arms','Greatswords, greataxes and hammers. Raised by landing hits with them.'),
          ('STEEL','POLEARMS','Polearms','Spears and halberds. Raised by landing hits with them.'),
          ('STEEL','GUARD','Guard','Blocking, parrying and shields. Raised by blocking and parrying damage.'),
          ('STEEL','UNARMED','Unarmed','Fists and fist weapons. Raised by landing unarmed hits.'),
          ('WEAVE','EMBER_RITE','Ember Rite','Ember and Frost Weaves. Raised by dealing damage with them.'),
          ('WEAVE','STORM_RITE','Storm Rite','Storm and Iron Weaves. Raised by dealing damage with them.'),
          ('WEAVE','HOLLOW_RITE','Hollow Rite','Hollow and Bloom Weaves. Raised by dealing damage with them.'),
          ('WEAVE','WARDING','Warding','Ward strength and recharge. Raised when your Ward absorbs damage.'),
          ('WEAVE','SHAPING','Shaping','Rites crafting and Resonances. Raised by crafting Rites and using Resonances.'),
          ('SALVAGE','FIREARMS','Firearms','Rifles, shotguns, pistols and launchers. Raised by hitting targets with them.'),
          ('SALVAGE','ENGINEERING','Engineering','Smithing and Tinkering. Raised by upgrading gear and building gadgets.'),
          ('SALVAGE','INFILTRATION','Infiltration','Sneaking, lockpicks and pickpocketing. Raised by staying unseen and opening locks.'),
          ('SALVAGE','SPEECH','Speech','Persuasion, prices and faction standing. Raised by passing checks and trading.')]
GROUPS = [('STEEL','Steel','Close combat and defense.'),('WEAVE','Weave','The Shard arts.'),('SALVAGE','Salvage','Guns, tools and guile.')]
REGIONS = [('R1','Cinderreach','1 to 12'),('R2','Saltmere','10 to 24'),('R3','Thornwood','22 to 36'),
           ('R4','Glasswaste','32 to 46'),('R5','Rimefall','42 to 58'),('R6','Hollowdeep','55 to 70'),
           ('HUB','Lantern Hold','Hub'),('UNDER','The Undervault','Varies'),('QUIET','The Quiet','Endgame')]
FACTIONS = [('KNIGHTS','Hull Knights','Sworn soldiers of the old ship. Honor, war and the chain of command.'),
            ('CHURCH','Lantern Church','Keepers of the ship logs, read as scripture.'),
            ('GUILD','Salvagers\' Guild','Traders, fences and thieves. Everything has a price.'),
            ('HAND','Quiet Hand','Contract killers who never take a job twice.'),
            ('CHOIR','Choir','Scholars of the Shards. Some of them listen too closely.')]
FACTION_ENEMY = [('HOLLOWED','Hollowed'),('REMNANT','Remnant'),('THORN','Thorn Clans'),('CHOIRBORN','Choirborn')]
STANDING = ['Hostile','Distrusted','Unknown','Known','Trusted','Sworn','Exalted']
COMPANIONS = [('C1','Kessa Vane','Hull Knight deserter'),('C2','Brother Odo','Lantern Church archivist'),
              ('C3','Tamsin Rook','Guild smuggler'),('C4','Vey','Quiet Hand initiate'),('C5','Hal Merrow','Choir defector'),
              ('C6','Sister Calla','Field medic'),('C7','Dren','Thorn Clan exile'),('C8','Unit 9','Rebuilt Remnant drone')]
LOYALTY = ['Wary','Steady','Loyal','Devoted']
ORIGINS = [('CRASH','Crash-Knight','A soldier who woke in the wreck with a rifle and a sword.','Blades 20, Firearms 15, Guard 15','Straight Sword, Hull Rifle, Medium armor'),
           ('HULLWITCH','Hullwitch','Born near a Shard. The Weave came before words did.','Ember Rite 20, Warding 15, Shaping 15','Catalyst, Ember Cast, Light armor'),
           ('SCAV','Scavenger','You picked the wreck clean before anyone else got there.','Engineering 20, Firearms 15, Infiltration 15','Pump Shotgun, Dagger, Light armor'),
           ('PRIEST','Lantern Priest','You read the ship logs aloud to the faithful.','Speech 20, Warding 15, Hollow Rite 15','Mace, Lantern Shield, Medium armor'),
           ('RANGER','Ranger','You walked the Reach alone and lived.','Firearms 20, Infiltration 15, Polearms 15','Marksman Rifle, Spear, Light armor'),
           ('UNBOUND','Unbound','No past. No starting bonuses. Ten points to spend as you like.','10 free skill points','Club, rags')]
MELEE = ['Dagger','Straight Sword','Curved Sword','Spear','Axe','Greatsword','Greataxe','Hammer','Greathammer','Halberd','Fist Weapon','Twinblade']
GUNS = ['Hull Rifle','Scout Rifle','Marksman Rifle','Auto Shotgun','Pump Shotgun','Sidearm','Hand Cannon','Launcher']
RARITY = [('COMMON','Common'),('FORGED','Forged'),('RARE','Rare'),('RELIC','Relic'),('SHARDBORN','Shardborn')]
MATERIALS = [('SCRAP','Hull Scrap','Common salvage. Used in most upgrades.'),('DUST','Shard Dust','Ground from small Shards. Used in Forged and Rare upgrades.'),
             ('GLASS','Choir Glass','Glass grown by Shards. Used in Relic upgrades and Rites.'),('STARMETAL','Starmetal','Metal from the ship core. Used for Shardborn gear.'),
             ('SEAL','Seal','Earned in weekly endgame activities. Spent at the Seal Warden.')]

for k, n, s, d in ELEMENTS:
    R += [(f'STR_ELEM_{k}', 'Shared', n, ''), (f'STR_ELEM_{k}_DESC', 'Shared', f'{d} Applies {s}. Deals triple buildup to {COUNTER[k]} Wards.', '')]
for k, n, d in STATUS:
    R += [(f'STR_STATUS_{k}', 'Shared', n, ''), (f'STR_STATUS_{k}_DESC', 'Shared', d, ''),
          (f'STR_STATUS_{k}_APPLIED', 'HUD', f'{n}!', 'Floating text over target')]
for g, n, d in GROUPS:
    R += [(f'STR_SKGRP_{g}', 'Skills', n, ''), (f'STR_SKGRP_{g}_DESC', 'Skills', d, '')]
for g, k, n, d in SKILLS:
    R += [(f'STR_SKILL_{k}', 'Skills', n, f'Group {g}'), (f'STR_SKILL_{k}_DESC', 'Skills', d, '')]
for k, n, b in REGIONS:
    R += [(f'STR_REGION_{k}', 'Shared', n, f'Level band {b}'), (f'STR_REGION_{k}_ENTER', 'HUD', n.upper(), 'Region entry banner')]
for k, n, d in FACTIONS:
    R += [(f'STR_FAC_{k}', 'Factions', n, ''), (f'STR_FAC_{k}_DESC', 'Factions', d, '')]
for k, n in FACTION_ENEMY:
    R.append((f'STR_EFAC_{k}', 'Shared', n, 'Enemy faction'))
for i, s in enumerate(STANDING):
    R.append((f'STR_STANDING_{i}', 'Factions', s, f'Standing tier {i}, thresholds -1000/-500/0/250/1000/2500/5000'))
for k, n, d in COMPANIONS:
    R += [(f'STR_CMP_{k}', 'Companions', n, 'Shardfall name; data/actors wins if it differs'), (f'STR_CMP_{k}_TAG', 'Companions', d, '')]
for i, s in enumerate(LOYALTY):
    R.append((f'STR_LOYALTY_{i}', 'Companions', s, 'Loyalty 0-24/25-49/50-74/75-100'))
for k, n, d, sk, kit in ORIGINS:
    R += [(f'STR_ORIGIN_{k}', 'Character creation', n, ''), (f'STR_ORIGIN_{k}_DESC', 'Character creation', d, ''),
          (f'STR_ORIGIN_{k}_SKILLS', 'Character creation', f'Starting skills: {sk}', ''),
          (f'STR_ORIGIN_{k}_KIT', 'Character creation', f'Starting gear: {kit}', '')]
for i, n in enumerate(MELEE):
    R.append((f'STR_WFAM_M{i+1:02d}', 'Shared', n, 'Melee family'))
for i, n in enumerate(GUNS):
    R.append((f'STR_WFAM_G{i+1:02d}', 'Shared', n, 'Firearm family'))
for k, n in RARITY:
    R.append((f'STR_RARITY_{k}', 'Shared', n, ''))
for k, n, d in MATERIALS:
    R += [(f'STR_MAT_{k}', 'Shared', n, ''), (f'STR_MAT_{k}_DESC', 'Shared', d, '')]

blk('CMN', 'All', '''
confirm|Confirm
cancel|Cancel
back|Back
yes|Yes
no|No
ok|OK
continue|Continue
apply|Apply
default|Reset to Default
close|Close
select|Select
equip|Equip
unequip|Unequip
drop|Drop
use|Use
inspect|Inspect
compare|Compare
sort|Sort
filter|Filter
junk|Mark as Junk
unjunk|Unmark Junk
favorite|Favorite
unfavorite|Remove Favorite
split|Split Stack
buy|Buy
sell|Sell
buyback|Buy Back
upgrade|Upgrade
craft|Craft
dismantle|Dismantle
rest|Rest
travel|Travel
accept|Accept
decline|Decline
track|Track
untrack|Stop Tracking
rename|Rename
delete|Delete
save|Save
load|Load
skip|Skip
hold_skip|Hold to Skip
next|Next
prev|Previous
page|Page {VAR_page} of {VAR_pages}
tab_prev|Previous Tab
tab_next|Next Tab
none|None
empty|Empty
locked|Locked
new|New
equipped|Equipped
loading|Loading...
saving|Saving...
searching|Searching...
connecting|Connecting...
seconds|{VAR_n}s
minutes|{VAR_n}m
hours|{VAR_n}h
days|{VAR_n}d
time_left|{VAR_time} left
x_of_y|{VAR_a} / {VAR_b}
count|x{VAR_n}
percent|{VAR_n}%
on|On
off|Off
low|Low
medium|Medium
high|High
ultra|Ultra
custom|Custom
auto|Auto
''')

blk('TITLE', 'Title and main menu', '''
press|Press {BTN_confirm} to Begin|Pulses 1.5 s cycle
continue|Continue
continue_sub|{VAR_char_name}, Level {VAR_level}, {VAR_location}
new|New Game
load|Load Game
coop|Co-op
options|Options
credits|Credits
quit|Quit to Desktop
version|Version {VAR_build}
copyright|(c) {VAR_year} Shardfall Team. All rights reserved.
online|Online
offline|Offline Play
slot|{VAR_char_name}  Level {VAR_level}  {VAR_location}  {VAR_playtime}
slot_empty|Empty Slot
slot_auto|Autosave
slot_quick|Quicksave
slot_manual|Manual Save
''')

blk('CC', 'Character creation', '''
title|Who survived the fall?
step_origin|Origin
step_body|Body
step_face|Face
step_scar|Shard Scar
step_voice|Voice
step_name|Name
step_review|Review
body_type|Body Type
body_a|Frame A
body_b|Frame B
height|Height
build|Build
muscle|Muscle
age|Age
skin|Skin Tone
skin_wear|Weathering
face_preset|Face Preset
face_shape|Face Shape
brow|Brow
eyes|Eyes
eye_color|Eye Color
nose|Nose
cheeks|Cheeks
mouth|Mouth
jaw|Jaw
ears|Ears
hair|Hair
hair_color|Hair Color
facial_hair|Facial Hair
paint|Face Paint
scars|Scars
scar_place|Placement
scar_size|Size
scar_glow|Glow
scar_color|Shard Color
scar_hint|Your Shard scar glows when you use the Weave. Pick where it sits.
voice_pick|Voice {VAR_n}
voice_pitch|Pitch
voice_preview|Preview Voice
name_prompt|Enter a name
name_hint|Ostra will call you this. 2 to 16 characters.
random|Randomize
undo|Undo
review_text|You can change your look at any Mirror in Lantern Hold. Your Origin cannot be changed.
begin|Begin
err_name_short|Names need at least 2 characters.
err_name_long|Names can be 16 characters at most.
err_name_bad|That name is not allowed. Try another.
''')

blk('HUD', 'HUD', '''
health|Health
ward|Ward
breath|Breath
tonic|Tonic
tonic_count|{VAR_n}
ward_broken|WARD BROKEN|Flash 0.6 s over vitals
ward_restored|Ward Restored|0.8 s
low_health|Low Health|Edge vignette label, accessibility text only
cast|Cast
strike|Strike
step|Step
surge|Surge
surge_ready|SURGE READY|1.2 s pulse
resonance|Resonance
resonance_ready|{VAR_res_name} ready
ammo_common|Common
ammo_charged|Charged
ammo_heavy|Heavy
ammo_mag|{VAR_mag}
ammo_reserve|{VAR_reserve}
ammo_low|LOW AMMO
ammo_empty|NO AMMO
reload|RELOAD
ember|{VAR_ember}
ember_gain|+{VAR_n}
ember_risk|At risk: {VAR_n}
lock_on|Locked On
poise_break|STAGGERED
crit|CRITICAL
headshot|Headshot
weak|Weak Point
resist|Resisted
immune|Immune
elite|Elite
leader|Leader
boss_title|{ACT_boss_name}, {ACT_boss_title}
boss_phase|Phase {VAR_n}
compass_n|N
compass_ne|NE
compass_e|E
compass_se|SE
compass_s|S
compass_sw|SW
compass_w|W
compass_nw|NW
distance|{VAR_m} m
distance_km|{VAR_km} km
ghost_marker|Your Shard-ghost
grenade|Grenade
incoming|Incoming fire
sub_ostra|OSTRA
sub_speaker|{ACT_speaker_name}
loot_line|{ITM_name} x{VAR_n}
loot_ember|{VAR_n} Ember
loot_full|Inventory full
loot_more|+{VAR_n} more
roster_downed|DOWNED {VAR_s}
roster_revive|Hold {BTN_interact} to Revive
roster_dead|Fallen
roster_disc|Disconnected
glide|Glide
speed|{VAR_kmh} km/h
boost|Boost
heat|Heat
overheat|OVERHEATED
seat_driver|Driver
seat_gunner|Gunner
seat_passenger|Passenger
explorer_dir|{VAR_direction}
pvp_score|{VAR_team_a} - {VAR_team_b}
pvp_power|Power weapon in {VAR_s}
pvp_power_up|Power weapon available
pvp_killfeed|{VAR_killer} [{ITM_icon}] {VAR_victim}
pvp_obj_a|Zone A
pvp_obj_b|Zone B
pvp_obj_c|Zone C
pvp_capturing|Capturing {VAR_zone}
pvp_contested|Contested
pvp_win|VICTORY
pvp_loss|DEFEAT
pvp_draw|DRAW
raid_wipe|Wipe in {VAR_s}
raid_mech|{VAR_mechanic}
raid_team|Fireteam
''')

# Interaction prompt verbs: [{BTN_interact}] Verb Target
for k, v in [('open','Open'),('loot','Loot'),('talk','Talk'),('pick','Pick Lock'),('steal','Steal'),('pickpocket','Pickpocket'),
             ('take','Take'),('take_all','Take All'),('read','Read'),('use','Use'),('rest','Rest at Anchor'),('light','Kindle Anchor'),
             ('climb','Climb'),('climb_tower','Climb Relay Tower'),('mount','Mount'),('dismount','Dismount'),('drive','Drive'),
             ('enter','Enter'),('exit','Exit'),('pull','Pull'),('push','Push'),('lever','Pull Lever'),('door','Open Door'),
             ('shortcut','Unbar Shortcut'),('search','Search'),('gather','Gather'),('mine','Mine'),('harvest','Harvest'),
             ('sit','Sit'),('sleep','Sleep'),('wait','Wait'),('craft','Use Bench'),('mirror','Use Mirror'),('ghost','Recover Ember'),
             ('note_read','Read Shard-note'),('note_write','Write Shard-note'),('sign','Summon {VAR_player}'),
             ('revive','Revive'),('carry','Carry'),('drop_body','Drop'),('hijack','Hijack'),('pray','Pray'),('donate','Offer')]:
    R.append((f'STR_PROMPT_{k.upper()}', 'HUD', f'{{BTN_interact}} {v}', 'Hold ring 0.8 s for steal, pickpocket, revive, hijack; tap otherwise'))
R.append(('STR_PROMPT_TARGET', 'HUD', '{VAR_verb} {VAR_target}', 'Composed prompt'))
R.append(('STR_PROMPT_OWNED', 'HUD', 'Owned by {ACT_owner_name}', 'Red text under steal prompts'))
R.append(('STR_PROMPT_LOCK', 'HUD', 'Lock: {VAR_lock_tier} (Infiltration {VAR_req})', ''))
for i, t in enumerate(['Novice','Apprentice','Adept','Expert','Master']):
    R.append((f'STR_LOCK_T{i+1}', 'HUD', t, f'Lock tier, Infiltration {[0,25,50,75,100][i]}'))

blk('PAUSE', 'Pause menu', '''
title|Ledger
resume|Resume
inventory|Inventory
equipment|Equipment
skills|Skills
perks|Perks
abilities|Abilities
map|Map
journal|Journal
codex|Codex
factions|Factions
companions|Companions
coop|Co-op
notes|Shard-notes
photo|Photo Mode
options|Options
save|Save Game
load|Load Game
help|Help
quit_menu|Quit to Title
quit_desk|Quit to Desktop
playtime|Play time {VAR_playtime}
level|Level {VAR_level}
ember_held|Ember {VAR_ember}
next_level|Next level {VAR_cost}
''')
