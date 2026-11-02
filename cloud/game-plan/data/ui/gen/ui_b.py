# Part B: Ledger screens and tooltips.
from ui_a import R, blk

blk('INV', 'Inventory', '''
title|Inventory
cat_all|All
cat_weapons|Weapons
cat_firearms|Firearms
cat_armor|Armor
cat_tonics|Tonics and Brews
cat_throw|Throwables
cat_ammo|Ammo
cat_mats|Materials
cat_res|Resonances
cat_keys|Key Items
cat_notes|Notes and Logs
cat_misc|Miscellaneous
cat_junk|Junk
sort_new|Newest
sort_name|Name
sort_rarity|Rarity
sort_dmg|Damage
sort_armor|Armor
sort_weight|Weight
sort_value|Value
sort_vw|Value per Weight
filter_equippable|Can Equip
filter_upgradable|Can Upgrade
filter_stolen|Stolen
filter_fav|Favorites
load|Equip Load {VAR_cur} / {VAR_max}
load_light|Light
load_medium|Medium
load_heavy|Heavy
load_over|Overloaded
load_light_d|Under 30%: fast roll, full Breath regen.
load_medium_d|30 to 70%: normal roll.
load_heavy_d|70 to 100%: slow roll, Breath regen 25% slower.
load_over_d|Over 100%: cannot roll or sprint.
carry|Carry {VAR_cur} / {VAR_max}
carry_over|You are carrying too much to run.
compare_title|Compare to Equipped
compare_up|+{VAR_n}
compare_down|-{VAR_n}
stolen_tag|Stolen
quest_tag|Quest Item
no_items|Nothing here yet.
drop_confirm|Drop {ITM_name}?
drop_qty|Drop how many?
''')

blk('EQ', 'Equipment and loadout', '''
title|Equipment
main1|Primary
main2|Secondary
sidearm|Sidearm
offhand|Off Hand
head|Head
chest|Chest
arms|Arms
legs|Legs
charm1|Charm 1
charm2|Charm 2
tonic_slot|Tonic Slot {VAR_n}
throw_slot|Throwable
shardborn_lock|Shardborn: only one equipped
shardborn_lock_d|You can equip one Shardborn weapon and one Shardborn armor piece at a time.
loadouts|Loadouts
loadout_n|Loadout {VAR_n}
loadout_save|Save Current
loadout_equip|Equip Loadout
loadout_missing|{VAR_n} items missing
armor_total|Armor {VAR_n}
ward_total|Ward {VAR_n}
poise_total|Poise {VAR_n}
''')

# Stat labels used by tooltips and detail views
STATS = [('DMG','Damage'),('WARD_DMG','Ward Damage'),('POISE_DMG','Poise Damage'),('CRIT','Critical Chance'),('CRIT_DMG','Critical Damage'),
         ('SPEED','Attack Speed'),('RANGE','Range'),('RPM','Rate of Fire'),('MAG','Magazine'),('RELOAD','Reload Time'),('STAB','Stability'),
         ('HANDLE','Handling'),('AIM','Aim Assist'),('ZOOM','Zoom'),('WEIGHT','Weight'),('VALUE','Value'),('ARMOR','Armor'),('POISE','Poise'),
         ('WARD','Ward'),('RES_ELEM','Elemental Resistance'),('BREATH_COST','Breath Cost'),('COOLDOWN','Cooldown'),('DURATION','Duration'),
         ('RADIUS','Radius'),('BUILDUP','Status Buildup'),('SCALING','Scaling'),('INFUSE','Infusion'),('UPGRADE','Upgrade'),('ART','Weapon Art')]
for k, n in STATS:
    R.append((f'STR_STAT_{k}', 'Shared', n, ''))
for g in 'SABCDE':
    R.append((f'STR_GRADE_{g}', 'Shared', g, {'S':'Scaling over 140%','A':'110-139%','B':'85-109%','C':'60-84%','D':'25-59%','E':'1-24%'}[g]))
ATTR = [('MIGHT','Might','Heavy weapon scaling, carry weight +5 per point, poise damage +1%.'),
        ('FINESSE','Finesse','Light weapon and firearm scaling, reload speed +0.5% per point, crit chance +0.2%.'),
        ('LORE','Lore','Weave damage scaling, ability cooldown -0.5% per point, Resonance strength +1%.'),
        ('GRIT','Grit','Poise +1 per point, status resistance +1.5%, equip load +1.')]
for k, n, d in ATTR:
    R += [(f'STR_ATTR_{k}', 'Level up', n, ''), (f'STR_ATTR_{k}_DESC', 'Level up', d, ''), (f'STR_ATTR_{k}_ABBR', 'Shared', n[:3].upper(), '')]
for k, n, d in [('HEALTH','Health','+8 Health per point.'),('WARD','Ward','+8 Ward per point. Ward fully recharges 4.5 s after the last hit.'),
                ('BREATH','Breath','+8 Breath per point. Breath starts refilling 1.2 s after you stop using it.')]:
    R += [(f'STR_VIGOR_{k}', 'Level up', n, ''), (f'STR_VIGOR_{k}_DESC', 'Level up', d, '')]

# Tooltip templates. Tokens point at data/items (ITM_) and data/actors (ACT_, PRK_).
blk('TT', 'Tooltip', '''
wpn_head|{ITM_name}
wpn_sub|{ITM_rarity} {ITM_family}  +{ITM_upgrade}
wpn_dmg|Damage {ITM_damage} ({ITM_damage_type})
wpn_ward|Ward Damage {ITM_ward_damage}
wpn_poise|Poise Damage {ITM_poise_damage}
wpn_crit|Critical {ITM_crit_chance}% x{ITM_crit_mult}
wpn_speed|Speed {ITM_attack_speed}
wpn_scale|Scaling  MIG {ITM_scale_might}  FIN {ITM_scale_finesse}  LOR {ITM_scale_lore}
wpn_req|Requires  MIG {ITM_req_might}  FIN {ITM_req_finesse}  LOR {ITM_req_lore}
wpn_req_fail|You lack the {ATTR_name} to wield this well. Damage -40%.
wpn_infuse|Infused: {ITM_infusion}
wpn_art|Weapon Art: {ITM_art_name}
wpn_art_desc|{ITM_art_desc}
wpn_weight|Weight {ITM_weight}
wpn_value|Value {ITM_value} Ember
gun_head|{ITM_name}
gun_sub|{ITM_rarity} {ITM_family}  +{ITM_upgrade}
gun_dmg|Damage {ITM_damage} per shot
gun_rpm|Rate of Fire {ITM_rpm} rpm
gun_mag|Magazine {ITM_mag}
gun_reload|Reload {ITM_reload}s
gun_range|Range {ITM_range} m
gun_stab|Stability {ITM_stability}
gun_handle|Handling {ITM_handling}
gun_ammo|Ammo: {ITM_ammo_type}
gun_perks|Perks
gun_perk_line|{ITM_perk_name}: {ITM_perk_desc}
gun_roll|Roll {VAR_n} of {VAR_total} possible
arm_head|{ITM_name}
arm_sub|{ITM_rarity} {ITM_slot}  +{ITM_upgrade}
arm_armor|Armor {ITM_armor}
arm_ward|Ward +{ITM_ward}
arm_poise|Poise {ITM_poise}
arm_res|Resist  {ELEM_icon} {ITM_res_value}%
arm_set|Set: {ITM_set_name} ({VAR_have}/{VAR_need})
arm_set_bonus|{VAR_need} pieces: {ITM_set_bonus}
tonic_head|{ITM_name}
tonic_eff|Restores {ITM_heal} Health over {ITM_heal_time}s
tonic_count|{VAR_n} of {VAR_max}. Refills at Anchors.
brew_eff|{ITM_effect} for {ITM_duration}s
throw_eff|{ITM_damage} {ITM_element} damage in {ITM_radius} m
mat_head|{ITM_name}
mat_use|Used in: {ITM_used_in}
mat_owned|Owned {VAR_n}
res_head|{ITM_name}
res_desc|{ITM_res_desc}
res_cd|Cooldown {ITM_cooldown}s
key_head|{ITM_name}
key_desc|{ITM_desc}
lore_flavor|{ITM_lore}
abil_head|{ACT_ability_name}
abil_desc|{ACT_ability_desc}
abil_cd|Cooldown {ACT_cooldown}s
abil_dmg|{ACT_damage} {ACT_element} damage
perk_head|{PRK_name}
perk_rank|Rank {VAR_rank} / {PRK_max_rank}
perk_desc|{PRK_desc}
perk_next|Next rank: {PRK_next_desc}
perk_req|Requires {PRK_skill} {PRK_req_level}
perk_req_node|Requires {PRK_parent_name}
perk_cost|Costs 1 perk point
skill_head|{SKL_name}
skill_level|Level {VAR_level} / 100
skill_xp|{VAR_xp} / {VAR_xp_next} to next level
skill_how|{SKL_desc}
status_head|{STATUS_name}
status_desc|{STATUS_desc}
status_build|Buildup {VAR_n}%
elem_head|{ELEM_name}
elem_desc|{ELEM_desc}
vendor_price|Price {VAR_price} Ember
vendor_sell|Sells for {VAR_price} Ember
stolen|Stolen from {ACT_owner_name}. Guild fences only.
cant_sell|Cannot be sold.
cant_drop|Quest item. Cannot be dropped.
''')

blk('SKL', 'Skills', '''
title|Skills
level|{VAR_level}
progress|{VAR_pct}%
perks_free|Perk points: {VAR_n}
legend|Legend
legend_d|Reset this skill to 15 and refund its perks. Raises it to Legendary rank {VAR_n}.
legend_confirm|Make {SKL_name} Legendary? It returns to level 15 and all {VAR_n} perks are refunded.
cap|Max level reached
''')
blk('PRK', 'Perk trees', '''
title|{SKL_name} Perks
gate|Rank Gate {VAR_level}
gate_d|Nodes past this line need {SKL_name} {VAR_level}.
unlock|Unlock
unlocked|Unlocked
cant_points|No perk points. You gain 1 per character level.
cant_level|Requires {SKL_name} {VAR_level}.
cant_parent|Unlock {PRK_parent_name} first.
respec|Reset Tree
respec_d|Refund all perks in this tree for {VAR_cost} Ember. Only at Anchors.
''')
for g in (25, 50, 75, 100):
    R.append((f'STR_PRK_GATE_{g}', 'Perk trees', f'Rank {g}', 'Gate line label'))

blk('LVL', 'Level up', '''
title|Level Up
cur|Level {VAR_level}
cost|Cost {VAR_cost} Ember
held|Held {VAR_ember} Ember
vigor_pt|Vigor point
attr_pt|Attribute point
vigor_hint|Each level gives 1 Vigor point and 1 attribute point.
preview|After
confirm|Confirm Level
not_enough|You need {VAR_short} more Ember.
done|Level {VAR_level} reached.
''')

blk('ABL', 'Abilities and Resonances', '''
title|Abilities
cast|Cast
cast_d|A thrown Weave. Grenade-class damage on a cooldown.
strike|Strike
strike_d|An empowered melee blow.
step|Step
step_d|A movement Weave: dash, blink or leap.
surge|Surge
surge_d|Your super. Charges from damage dealt and taken.
element|Element
pick_elem|Choose an element. All four slots use it.
res_title|Resonances
res_d|Found powers with long cooldowns. Equip one.
res_none|No Resonance equipped
counter|Counter: deals triple Ward damage to {ELEM_counter} Wards.
''')

blk('MAP', 'World map', '''
title|Map
local|Local Map
world|World Map
layer_surface|Surface
layer_under|Undervault
layer_quiet|The Quiet
unrevealed|Climb this region's Relay Tower to reveal the map.
legend|Legend
marker_place|Place Marker
marker_remove|Remove Marker
travel|Fast Travel
travel_to|Travel to {VAR_anchor_name}?
travel_cost|Travel costs nothing. Enemies in this region will not respawn.
travel_combat|Cannot travel in combat.
travel_unlit|Kindle this Anchor first.
travel_quiet|You cannot fast travel out of the Quiet.
zoom_in|Zoom In
zoom_out|Zoom Out
center|Center on Me
filters|Filters
explored|Explored {VAR_pct}%
level_band|Recommended level {VAR_band}
''')
for k, n in [('ANCHOR','Anchor'),('ANCHOR_UNLIT','Unlit Anchor'),('TOWER','Relay Tower'),('TOWN','Town'),('SITE','Site'),('SITE_DONE','Cleared Site'),
             ('VENDOR','Vendor'),('SMITH','Smith'),('BENCH','Workbench'),('QUEST_MAIN','Main Quest'),('QUEST_SIDE','Side Quest'),('QUEST_FAC','Faction Quest'),
             ('QUEST_CMP','Companion Quest'),('FIELD_BOSS','Field Boss'),('BOSS_DEAD','Defeated'),('GHOST','Shard-ghost'),('ALLY','Ally'),('CMP','Companion'),
             ('CITADEL','Hollowed Citadel'),('STRIKE','Strike'),('RAID','Raid Gate'),('MIRROR','Mirror'),('VEHICLE','Vehicle'),('PLAYER','You'),
             ('CUSTOM','Marker'),('SHORTCUT','Shortcut'),('LOCKED_DOOR','Locked Door')]:
    R.append((f'STR_MARK_{k}', 'World map', n, 'Map legend and marker name'))

blk('JRN', 'Journal', '''
title|Journal
main|Main
faction|Factions
companion|Companions
radiant|Contracts
misc|Miscellaneous
done|Completed
failed|Failed
active|Active
tracked|Tracked
obj_done|[x] {VAR_objective}
obj_open|[ ] {VAR_objective}
obj_opt|(Optional) {VAR_objective}
reward|Reward: {VAR_reward}
giver|From {ACT_giver_name}
explorer|Explorer Mode
explorer_d|Hides quest markers. The journal gives written directions instead.
explorer_on|Explorer Mode on. Markers hidden.
explorer_off|Explorer Mode off. Markers shown.
no_quests|No quests in this tab.
''')

blk('CDX', 'Lore codex', '''
title|Codex
items|Items
places|Places
logs|Ship Logs
bestiary|Bestiary
people|People
found|{VAR_found} of {VAR_total} found
locked|Undiscovered
beast_kills|Defeated {VAR_n}
beast_weak|Weak to {ELEM_name}
beast_resist|Resists {ELEM_name}
beast_drops|Drops {ITM_name}
log_title|Log {VAR_n}: {VAR_log_title}
''')

blk('FAC', 'Factions screen', '''
title|Factions
standing|Standing {VAR_standing}
rank|Rank: {VAR_rank}
next|{VAR_n} to {VAR_next_rank}
conflict|Conflict
conflict_d|Joining {FAC_name} closes the {FAC_rival} questline for good.
joined|Member
not_joined|Not a member
''')
blk('CMPS', 'Companions screen', '''
title|Companions
loyalty|Loyalty {VAR_n}
active|With you
waiting|Waiting at {VAR_location}
not_met|Not yet met
quest_step|Quest: {VAR_step}
gear|Gear
dismiss|Part Ways
dismiss_confirm|Send {CMP_name} back to {VAR_location}?
max|You can travel with one companion at a time.
''')

blk('SMITH', 'Crafting: Smithing', '''
title|Smithing
upgrade_to|Upgrade to +{VAR_n}
cost|Cost
have|Have {VAR_have} / Need {VAR_need}
max|Fully upgraded
cap_meter|Skill bonus {VAR_pct}% of 15%
cap_d|Engineering perks add up to 15% on top of upgrade level.
infuse|Infuse
infuse_d|Turn {ITM_scale_might} scaling into {ELEM_name} damage.
missing|Missing materials.
level_low|Engineering {VAR_req} needed for this upgrade.
done|{ITM_name} upgraded to +{VAR_n}.
''')
blk('RITE', 'Crafting: Rites', '''
title|Rites
effects|Effects
add|Add Effect
slot|Effect {VAR_n} of 3
mag|Magnitude
dur|Duration
area|Area
cost|Cooldown {VAR_s}s
formula|Cooldown = base {VAR_base}s x (1 + 0.4 x effects) x (1 - Shaping/250)
name|Name your Rite
known|Only effects you have learned appear here.
done|{VAR_rite_name} written.
''')
blk('TINK', 'Crafting: Tinkering', '''
title|Tinkering
gadgets|Gadgets
ammo|Ammo
mods|Weapon Mods
make|Build x{VAR_n}
max|Make Max
done|Built {ITM_name} x{VAR_n}.
''')
blk('BREW', 'Crafting: Brewing', '''
title|Brewing
tonics|Tonic Upgrades
brews|Brews
unknown|Unknown Recipe
discover|You learned a new recipe: {ITM_name}.
done|Brewed {ITM_name} x{VAR_n}.
tonic_up|Tonic potency +{VAR_n}
tonic_add|Tonic capacity +1
''')

blk('VEND', 'Vendor', '''
title|{ACT_vendor_name}
buy|Buy
sell|Sell
buyback|Buy Back
ember|Your Ember {VAR_ember}
vendor_ember|Vendor Ember {VAR_ember}
restock|Restocks in {VAR_time}
no_mats|This vendor does not buy materials.
no_stolen|This vendor will not touch stolen goods.
too_poor|You cannot afford that.
vendor_poor|The vendor cannot afford that.
qty|How many? {VAR_n}
total|Total {VAR_price} Ember
''')

blk('ANCH', 'Anchor rest menu', '''
title|{VAR_anchor_name}
rest|Rest
level|Level Up
travel|Travel
refill|Refill Tonics
echoes|Summon Echoes
craft|Workbench
storage|Storage
wait|Wait
wait_hours|Wait {VAR_n} hours
leave|Leave
rest_d|Restores Health, Ward, Breath and Tonics. Normal enemies return.
kindled|ANCHOR KINDLED
''')

blk('DEATH', 'Death screen', '''
title|YOU FELL
ghost|Your Shard-ghost waits at {VAR_location}.
ember|It holds {VAR_ember} Ember.
rule|You dropped half your Ember. Reach your ghost to take it back. Fall again first and it is gone.
lost|Your Shard-ghost faded. {VAR_ember} Ember lost.
respawn|Return to {VAR_anchor_name}
echo|Your Echo fell.
coop_fallen|{VAR_player} fell.
coop_wipe|Your fireteam fell.
''')

blk('DLG', 'Dialogue', '''
check_speech|[Speech {VAR_req}]
check_attr|[{ATTR_name} {VAR_req}]
check_fac|[{FAC_name}]
check_pass|Success
check_fail|Failed
leave|Goodbye.
trade|Let me see your goods.
bribe|[Bribe {VAR_n} Ember]
intimidate|[Intimidate]
lie|[Lie]
said|(Already asked)
log|Dialogue Log
''')

blk('LOAD', 'Loading screens', '''
title|{REGION_name}
press|Press {BTN_confirm} to Continue
progress|{VAR_pct}%
''')

blk('OPT', 'Options', '''
title|Options
tab_game|Gameplay
tab_ctrl|Controls
tab_remap|Remap
tab_display|Display
tab_gfx|Graphics
tab_audio|Audio
tab_ui|Interface
tab_access|Accessibility
tab_acct|Account
diff_note|Shardfall has no difficulty menu. Use Echoes, co-op, levels or Assist Mode to change the challenge.
assist|Assist Mode
assist_d|Adds aim help and widens parry windows by 4 frames. Achievements stay on.
defeat|Defeat Mode
defeat_d|When you fall you keep all Ember. For players who want to explore.
autosave|Autosave Interval
autosave_d|Every 5, 10 or 15 minutes, plus at every Anchor.
camera_dist|Camera Distance
camera_shake|Camera Shake
fov|Field of View
fov_d|70 to 110 degrees.
lock_switch|Lock-on Target Switch
lock_switch_flick|Flick
lock_switch_button|Button
auto_lock|Auto Lock-on
crosshair|Crosshair Style
hitmark|Hit Markers
dmg_numbers|Damage Numbers
dmg_numbers_d|Off, Hits only, or All.
tutorials|Tutorials
tut_reset|Reset Tutorials
lang_text|Text Language
lang_voice|Voice Language
sens_x|Look Sensitivity (Horizontal)
sens_y|Look Sensitivity (Vertical)
sens_aim|Aim Sensitivity
invert_y|Invert Y
invert_x|Invert X
deadzone_l|Left Stick Deadzone
deadzone_r|Right Stick Deadzone
vibration|Vibration
triggers|Adaptive Triggers
aim_assist|Aim Assist
aim_assist_d|Applies to controllers only. Off in PvP Arena.
toggle_sprint|Sprint
toggle_aim|Aim
toggle_block|Block
toggle_crouch|Crouch
hold|Hold
toggle|Toggle
remap_press|Press a button for {VAR_action}...
remap_conflict|{VAR_key} is already bound to {VAR_action}. Swap them?
remap_reset|Reset All Bindings
res|Resolution
window|Window Mode
window_full|Fullscreen
window_border|Borderless
window_win|Windowed
vsync|V-Sync
fps_cap|Frame Rate Limit
fps_unl|Unlimited
hdr|HDR
brightness|Brightness
brightness_d|Adjust until the left symbol is barely visible.
upscale|Upscaling
upscale_q|Quality
upscale_b|Balanced
upscale_p|Performance
preset|Graphics Preset
textures|Texture Quality
shadows|Shadow Quality
gi|Global Illumination
reflections|Reflections
foliage|Foliage Density
draw|View Distance
motion_blur|Motion Blur
dof|Depth of Field
grain|Film Grain
vol_master|Master Volume
vol_music|Music
vol_sfx|Effects
vol_voice|Dialogue
vol_ui|Interface
vol_ostra|Ostra Voice
dyn_range|Dynamic Range
dyn_wide|Home Theater
dyn_mid|Headphones
dyn_night|Night Mode
subtitles|Subtitles
sub_size|Subtitle Size
sub_bg|Subtitle Background
sub_speaker|Show Speaker Names
hud_opacity|HUD Opacity
hud_scale|UI Scale
hud_scale_d|80% to 150%.
hud_mode|HUD
hud_full|Full
hud_min|Minimal (fades out of combat)
hud_off|Off
compass|Compass
markers|Quest Markers
ostra_subs|Ostra Subtitles
unsaved|You have unsaved changes. Apply them?
reset_confirm|Reset all settings on this tab to default?
restart|This change applies after a restart.
revert|Keep these display settings? Reverting in {VAR_s}s.
''')
blk('ACC', 'Accessibility suite', '''
colorblind|Colorblind Mode
cb_off|Off
cb_prot|Protanopia
cb_deut|Deuteranopia
cb_trit|Tritanopia
cb_d|Changes element, status and rarity colors. Shapes stay the same.
motion|Reduce Motion
motion_d|Cuts screen shake, flashes and menu motion.
flash|Reduce Flashing
contrast|High Contrast HUD
text_size|Menu Text Size
screen_reader|Menu Narration
audio_cues|Visual Sound Cues
audio_cues_d|Shows arrows for footsteps, gunfire and telegraphs.
hold_tap|Replace Holds with Taps
qte_auto|Auto-complete Button Mashing
mono|Mono Audio
dyslexic|Dyslexia-friendly Font
cursor|Cursor Size
slow_mo|Slow Combat (Single Player)
slow_mo_d|Runs combat at 75% speed. Single player only.
''')

blk('MP', 'Co-op and multiplayer lobby', '''
title|Co-op
invite|Invite Friend
join|Join Friend
quick|Quick Match
sign|Place Summon Sign
sign_d|Others can summon you into their world.
sign_placed|Summon sign placed.
summon|Summon
summoned|You were summoned to {VAR_host}'s world.
host|Host
guest|Guest
invasions|Allow Invasions
invasions_d|When on, other players can invade your world while you are online.
password|Group Password
level_sync|Level Sync
level_sync_d|Guests are scaled to the host's region band.
kick|Remove Player
kick_confirm|Remove {VAR_player} from your world?
leave|Leave Session
leave_confirm|Return to your own world? Progress from this session is kept.
party|Fireteam {VAR_n}/{VAR_max}
mm_search|Searching for players... {VAR_time}
mm_found|Match found
mm_cancel|Cancel Search
ready|Ready
not_ready|Not Ready
voice|Voice Chat
voice_push|Push to Talk
text_chat|Text Chat
mute|Mute
report|Report Player
block|Block Player
''')

blk('NOTE', 'Shard-notes composer', '''
title|Write a Shard-note
template|Template
word|Word
conj|Conjunction
add_line|Add Second Line
preview|Preview
place|Place Note
cost|Uses 1 Shard-note chalk
rate_good|Helpful
rate_bad|Unhelpful
rated|Rated
rating|Your notes were rated helpful {VAR_n} times.
limit|You can place 10 notes. The oldest will fade.
''')
TEMPLATES = ['{W} ahead','No {W} ahead','{W} required ahead','Be wary of {W}','Try {W}','Could this be a {W}?','If only I had a {W}...',
             'Visions of {W}...','Time for {W}','{W}','{W}!','{W}?','Didn\'t expect {W}...','Look carefully','Listen carefully','Ahh, {W}...',
             'Seek {W}','Still no {W}...','Why is it always {W}?','Praise the {W}!']
WORDS = ['enemy','Hollowed','Remnant','Thorn raider','Choirborn','ambush','sniper','turret','boss','strong foe','weak foe','pack',
         'Anchor','shortcut','hidden path','ladder','door','lever','chest','trap','ledge','drop','bridge','dead end','loot','Shard',
         'Relic','Shardborn','Ember','Starmetal','Choir Glass','Hull Scrap','tonic','ammo','Ward','Breath','parry','roll','jump',
         'sneak','fire','lightning','void','frost','growth','iron','Burn','Shock','Drain','Slow','Root','Shatter','headshot','weak point',
         'back','legs','head','tail','left','right','up','down','behind','under','above','light','dark','water','height','close-range',
         'long-range','Strider','skimmer','hauler','friend','co-op','Echo','patience','courage','despair','hope','Ostra','the ship','home']
CONJ = ['and then','but','therefore','in short','or','by the way','so to speak','all the more',', ']
for i, t in enumerate(TEMPLATES):
    R.append((f'STR_NOTE_T{i+1:02d}', 'Shard-notes composer', t.replace('{W}', '{VAR_word}'), 'Template'))
for i, w in enumerate(WORDS):
    R.append((f'STR_NOTE_W{i+1:03d}', 'Shard-notes composer', w, 'Word'))
for i, c in enumerate(CONJ):
    R.append((f'STR_NOTE_C{i+1:02d}', 'Shard-notes composer', c, 'Conjunction'))

blk('END', 'Endgame hub', '''
title|The Quiet
strikes|Weekly Strikes
strike_name|{ACT_strike_name}
strike_d|3 players. Matchmade. Resets Tuesday 17:00 UTC.
raid|Raid Gate
raid_d|6 players. No matchmaking. Bring a fireteam.
arena|Arena
arena_d|3v3. Matchmade. Power weapons spawn on timers.
citadels|Hollowed Citadels
citadel_d|A remixed dungeon. New modifiers each week.
modifiers|This week
seals|Seals {VAR_n}
seal_cap|Weekly Seals {VAR_n} / 100
seal_vendor|Seal Warden
power|Gear Power {VAR_n}
rec_power|Recommended Power {VAR_n}
launch|Launch
reset_in|Resets in {VAR_time}
first_clear|First clear this week: bonus Shardborn drop
''')
for i, (n, d) in enumerate([('Blazing','Ember damage +50% for everyone.'),('Overcharged Storm','Storm abilities recharge 2x faster.'),
        ('Brittle Wards','Wards break in half the damage.'),('Iron Skin','Enemies take 50% less precision damage.'),('Famine','No ammo drops from fodder.'),
        ('Blackout','Radar disabled. Enemies hit 2x harder in melee.'),('Grounded','Airborne players take 25% more damage.'),
        ('Champion\'s Return','Leaders appear in every encounter.'),('Equinox','Bloom and Hollow damage +50%.'),('Quiet Mind','Surge charges 30% slower.')]):
    R += [(f'STR_MOD_{i+1:02d}', 'Endgame hub', n, 'Weekly modifier'), (f'STR_MOD_{i+1:02d}_DESC', 'Endgame hub', d, '')]

blk('SHOP', 'Cosmetics shop', '''
title|Wardrobe Shop
dyes|Dyes
striders|Strider Skins
emotes|Emotes
frames|Photo Frames
bundles|Bundles
owned|Owned
price|{VAR_price}
no_power|Cosmetic only. Nothing here changes your stats.
buy_confirm|Buy {VAR_item} for {VAR_price}?
rotates|Rotates in {VAR_time}
''')
blk('PHOTO', 'Photo mode', '''
title|Photo Mode
camera|Camera
fov|Field of View
roll|Roll
focus|Focus Distance
aperture|Aperture
exposure|Exposure
filters|Filters
filter_n|Filter {VAR_n}
strength|Strength
frames|Frames
pose|Pose
expression|Expression
hide_player|Hide Player
hide_allies|Hide Allies
take|Take Photo
saved|Photo saved.
''')
blk('FFE', 'Forgeframe editor UI', '''
title|Forgeframe
records|Records
place|Place
select|Select
move|Move
rotate|Rotate
scale|Scale
script|Script
test|Test in Sandbox
test_stop|Stop Test
publish|Publish Mod
publish_d|Shares your mod. Mods disable achievements in that save.
unsaved|Unsaved changes. Save before closing?
err_missing|Missing reference: {VAR_record}
err_compile|Script error at line {VAR_line}: {VAR_msg}
mods|Mods
mod_on|Enabled
mod_off|Disabled
load_order|Load Order
ach_off|Mods are active. Achievements are off for this save.
''')
blk('SEASON', 'Season pass and events', '''
title|Season {VAR_n}: {VAR_season_name}
rank|Rank {VAR_rank}
xp|{VAR_xp} / 10000 XP
free|Free Track
premium|Premium Track
claim|Claim
claim_all|Claim All
ends|Season ends in {VAR_time}
event|{VAR_event_name}
event_ends|Event ends in {VAR_time}
challenges|Challenges
weekly|Weekly
daily|Daily
''')
blk('PLAT', 'Platform overlays', '''
saving|Saving. Do not turn off the system.
saved|Saved
net_lost|Connection lost. Trying to reconnect...
net_back|Connection restored.
net_offline|Playing offline. Co-op and Shard-notes are unavailable.
ctrl_lost|Controller disconnected. Reconnect it to continue.
ctrl_back|Controller connected.
user_change|Signed-in profile changed. Returning to the title screen.
storage_full|Not enough storage space. {VAR_mb} MB more is needed.
psplus|An online subscription is required for co-op.
xbl|Xbox network access is required for co-op.
age|Online interactions are not rated.
''')
