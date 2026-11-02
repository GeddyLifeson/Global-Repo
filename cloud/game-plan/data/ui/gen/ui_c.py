# Part C: popups, notifications, tutorials, confirms, errors, tips, achievements. Writes both CSVs.
import csv, re, os
from ui_a import R, REGIONS, SKILLS, FACTIONS
import ui_b  # noqa: registers part B strings

P = []  # popup rows
KIND = {  # kind: (screen layer, default duration, dismiss rule, queue rule)
 'toast': ('HUD notification feed, top right', '4.0', 'Auto', 'Queue max 4 visible; newer push older up; same ID within 2 s merges count'),
 'banner': ('HUD centre banner', '5.0', 'Auto; any input after 1.5 s skips', 'Exclusive; waits for previous banner'),
 'prompt': ('HUD bottom centre', 'Until condition', 'Condition met', 'One at a time; highest priority wins'),
 'tutorial': ('HUD left card', '8.0 or until action', 'Action done or 8 s; repeat once after 60 s if not done', 'One at a time; suppressed in combat and dialogue'),
 'modal': ('Modal dialog over current screen', 'Until input', 'Button press', 'Blocks input; pauses game in single player'),
 'error': ('Modal dialog, red rule', 'Until input', 'Button press', 'Blocks input; replaces any modal of lower priority'),
 'inline': ('Inline on current screen', '3.0', 'Auto', 'Replaces previous inline message'),
}
def pop(pid, kind, screen, trigger, title, body, buttons='', dur=None, prio=2, sfx=''):
    ids = []
    for part, txt in (('T', title), ('B', body)):
        if txt:
            sid = f'STR_{pid}_{part}'
            R.append((sid, screen, txt, f'{kind} {part=="T" and "title" or "body"}'))
            ids.append(sid)
        else:
            ids.append('')
    layer, d, dis, q = KIND[kind]
    P.append(dict(popup_id=pid, kind=kind, screen=screen, layer=layer, trigger=trigger, title_str=ids[0], body_str=ids[1],
                  buttons=buttons, duration_s=dur or d, dismiss=dis, priority=prio, queue_rule=q, sfx_hook=sfx))

def rows(kind, screen, block, prio=2, buttons=''):
    for ln in block.strip().split('\n'):
        p = [x.strip() for x in ln.split('|')]
        pid, trig, title, body = p[:4]
        dur = p[4] if len(p) > 4 and p[4] else None
        b = p[5] if len(p) > 5 else buttons
        pop(pid, kind, screen, trig, title, body, b, dur, prio, p[6] if len(p) > 6 else f'SFX_UI_{kind.upper()}')

# --- HUD toasts (notification feed) ---
rows('toast', 'HUD', '''
NTF_SKILL_UP|A skill gains a level|{SKL_name} {VAR_level}||3.0
NTF_SKILL_MILESTONE|Skill reaches 25, 50, 75 or 100|{SKL_name} {VAR_level}|New perks can be unlocked in this tree.|5.0
NTF_PERK_READY|Character level up grants a perk point|Perk point earned|Open Perks to spend it.|4.0
NTF_QUEST_NEW|Quest added to journal|New Quest|{VAR_quest_name}|5.0
NTF_QUEST_UPDATE|Objective changes|Quest Updated|{VAR_objective}|4.0
NTF_QUEST_DONE|Quest completed|Quest Complete|{VAR_quest_name}|5.0
NTF_QUEST_FAIL|Quest failed|Quest Failed|{VAR_quest_name}|5.0
NTF_DISCOVER|Player enters a new site trigger volume|Discovered|{VAR_location}|4.0
NTF_SITE_CLEAR|Site boss dead and all enemies in site cleared|Site Cleared|{VAR_location}|4.0
NTF_ITEM_RARE|Pick up Rare or higher item|{ITM_rarity}|{ITM_name}|4.0
NTF_SHARDBORN|Pick up Shardborn item|SHARDBORN|{ITM_name}|6.0||SFX_UI_SHARDBORN
NTF_RECIPE|Learn recipe|Recipe Learned|{ITM_name}|3.0
NTF_CODEX|New codex entry unlocked|Codex Entry|{VAR_entry}|3.0
NTF_LOG|Ship log found|Ship Log Found|Log {VAR_n}: {VAR_log_title}|4.0
NTF_STANDING|Faction standing changes by 50 or more|{FAC_name}|Standing {VAR_sign}{VAR_n}|3.0
NTF_RANK|Faction rank up|{FAC_name}|You are now {VAR_rank}.|5.0
NTF_LOYALTY|Companion loyalty tier changes|{CMP_name}|{CMP_name} is now {VAR_loyalty}.|4.0
NTF_CMP_LIKE|Companion approves of a choice (+5 loyalty or more)|{CMP_name} approves.||2.5
NTF_CMP_DISLIKE|Companion disapproves (-5 loyalty or more)|{CMP_name} disapproves.||2.5
NTF_BOUNTY|Crime witnessed|Bounty +{VAR_n}|{VAR_hold_name} guards want you.|4.0
NTF_BOUNTY_CLEAR|Bounty paid or cleared|Bounty Cleared||3.0
NTF_STOLEN|Item taken while owned and unseen|Stolen|{ITM_name}|2.5
NTF_ENCUMBERED|Carry weight over max|Overloaded|You cannot run. Drop something.|4.0
NTF_TONIC_UP|Tonic capacity increased|Tonic +1|You now carry {VAR_n} Tonics.|4.0
NTF_RES_FOUND|New Resonance acquired|Resonance Found|{ITM_name}|5.0
NTF_ABIL_UNLOCK|New ability unlocked|Ability Unlocked|{ACT_ability_name}|5.0
NTF_EMBER_RECOVER|Shard-ghost touched|Ember Recovered|+{VAR_n} Ember|4.0
NTF_EMBER_LOST|Died with ghost still out|Ember Lost|{VAR_n} Ember faded with your old ghost.|5.0
NTF_AUTOSAVE|Autosave completes|Saved||1.5
NTF_ACH|Platform achievement unlocked (if platform shows none)|Achievement|{VAR_ach_name}|5.0
NTF_PLAYER_JOIN|Co-op player joins|{VAR_player} joined.||3.0
NTF_PLAYER_LEAVE|Co-op player leaves|{VAR_player} left.||3.0
NTF_INVADED|Invader enters world|Invaded|{VAR_player} has invaded your world!|5.0
NTF_INVADER_DEAD|Invader defeated|Invader Defeated|+{VAR_n} Ember|4.0
NTF_SIGN_USED|Your summon sign is used|Summoned||3.0
NTF_NOTE_RATED|Your Shard-note rated helpful|Note Rated|A player found your note helpful. Health restored.|3.0
NTF_SEAL|Seals earned|+{VAR_n} Seals||3.0
NTF_SEAL_CAP|Weekly Seal cap reached|Seal Cap Reached|More Seals next reset.|4.0
NTF_SEASON_RANK|Season rank up|Season Rank {VAR_rank}|Reward ready to claim.|4.0
NTF_EVENT|Live event starts while playing|{VAR_event_name}|Event is live. See the Quiet.|6.0
NTF_WEATHER|Ostra weather warning before storm|Shardstorm|Seek cover. Storm in {VAR_s}s.|5.0
NTF_MAIL|Item sent to Lantern Hold storage (inventory full)|Sent to Storage|{ITM_name}|3.0
''')
# --- banners ---
rows('banner', 'HUD', '''
BAN_LEVEL_UP|Character level increases at Anchor|LEVEL {VAR_level}|Perk point earned.|4.0
BAN_REGION|First entry into a region|{REGION_name}|Level {VAR_band}|5.0
BAN_ANCHOR|Anchor kindled for the first time|ANCHOR KINDLED|{VAR_anchor_name}|3.5
BAN_TOWER|Relay Tower climbed|MAP REVEALED|{REGION_name}|4.0
BAN_BOSS_DEAD|Boss health reaches 0|{ACT_boss_name} FELLED||6.0||SFX_UI_BOSS_DEAD
BAN_SHARD|Shard-bearer killed|SHARD CLAIMED|{ACT_shard_name}|7.0||SFX_UI_SHARD
BAN_PHASE|Boss enters next phase|{ACT_phase_line}||2.5
BAN_SITE_BOSS|Enter site boss arena|{ACT_boss_name}|{ACT_boss_title}|3.0
BAN_ACT|Main quest act complete|ACT {VAR_n} COMPLETE|{VAR_act_name}|6.0
BAN_STRIKE_DONE|Strike final boss dead|STRIKE COMPLETE|{VAR_time} cleared|6.0
BAN_RAID_DONE|Raid final encounter cleared|RAID COMPLETE|{VAR_raid_name}|8.0
BAN_PVP_START|Arena match starts|ROUND {VAR_n}|First to {VAR_score}|3.0
BAN_PVP_END|Arena match ends|{VAR_result}|{VAR_team_a} - {VAR_team_b}|5.0
BAN_SURGE|Surge meter reaches 100%|SURGE READY||1.5
''', prio=3)
# --- prompts (persistent) ---
rows('prompt', 'HUD', '''
PRM_GHOST_NEAR|Within 30 m of own Shard-ghost|Your Shard-ghost is near.||Until out of range
PRM_LOW_TONIC|Health under 25% and Tonics at 0|No Tonics left. Rest at an Anchor.||6.0
PRM_RELOAD|Magazine empty and reserve > 0|{BTN_reload} Reload||Until reload
PRM_NO_AMMO|Magazine and reserve empty|No ammo. Switch weapons with {BTN_swap}.||5.0
PRM_SURGE|Surge ready and in combat 10 s without use|{BTN_surge} Surge||Until used or combat ends
PRM_REVIVE|Ally downed within 3 m|Hold {BTN_interact} to Revive {VAR_player}||Until revived or bled out
PRM_DOWNED|Player downed in co-op|DOWNED. Wait for an ally. {VAR_s}s||30.0
PRM_SPECTATE|Player dead in co-op while allies live|Spectating {VAR_player}. {BTN_next} Next||Until respawn
PRM_FOG|At boss fog wall|{BTN_interact} Enter the Fog||Until moved away
PRM_FOG_COOP|Guest at fog wall|Waiting for host to enter...||Until host enters
PRM_LEAVE_AREA|Player leaves arena or mission bounds|Return to the area. {VAR_s}s||10.0
PRM_STEALTH_HIDDEN|Crouched and undetected|[HIDDEN]||While true
PRM_STEALTH_SEEN|Detection meter 100%|[DETECTED]||2.0
PRM_STEALTH_CAUTION|Detection meter 1-99%|[CAUTION]||While true
PRM_SWIM_BREATH|Underwater|Air {VAR_s}s||While underwater
PRM_FALL|Fall height over 12 m and no glide|{BTN_glide} Glide||Until landing
PRM_VEHICLE_EXIT|In vehicle|Hold {BTN_interact} Exit||While in vehicle
''', prio=4)
# --- tutorials ---
TUT = [('MOVE','Game start, first 3 s','Move','{BTN_move} Move. {BTN_look} Look.','Move 5 m'),
 ('SPRINT','After TUT_MOVE','Sprint','Hold {BTN_sprint} to sprint. It uses Breath.','Sprint 2 s'),
 ('ROLL','First enemy in view','Roll','{BTN_roll} Roll. You are untouchable for a moment at the start of a roll.','Roll once'),
 ('LIGHT','Weapon drawn','Light Attack','{BTN_light} Light attack.','Hit once'),
 ('HEAVY','After 3 light hits','Heavy Attack','{BTN_heavy} Heavy attack. Hold to charge.','Heavy once'),
 ('BLOCK','First enemy wind-up','Block','Hold {BTN_block} to block. Blocking drains Breath.','Block one hit'),
 ('PARRY','Third blocked hit','Parry','Tap {BTN_parry} just before a hit lands to parry. Then {BTN_light} for a critical.','Parry once'),
 ('LOCK','Enemy within 15 m','Lock On','{BTN_lock} Lock on. Flick {BTN_look} to switch target.','Lock once'),
 ('AIM','Firearm equipped','Aim and Fire','Hold {BTN_aim} to aim. {BTN_fire} Fire.','Fire 3 shots'),
 ('SWAP','Second weapon picked up','Switch Weapon','{BTN_swap} Switch between primary and secondary. Hold for sidearm.','Swap once'),
 ('RELOAD','Magazine below 30%','Reload','{BTN_reload} Reload.','Reload once'),
 ('WARD','First Ward hit taken','Ward','Your Ward (blue) soaks damage first. It refills 4.5 s after the last hit.','Ward recharges'),
 ('WARD_BREAK','Enemy Ward first broken','Breaking Wards','Elemental damage breaks enemy Wards faster. Match the counter element for triple damage.','6 s'),
 ('BREATH','Breath hits 0','Breath','Breath (green) powers rolls, sprints, blocks and attacks. Stop to let it refill.','6 s'),
 ('TONIC','Health under 50% first time','Tonics','{BTN_tonic} Drink a Tonic. You have {VAR_n}. Anchors refill them.','Drink once'),
 ('CAST','Cast unlocked','Cast','{BTN_cast} Cast your Weave. It recharges on its own.','Cast once'),
 ('STRIKE','Strike unlocked','Strike','{BTN_strike} Strike. A charged melee Weave.','Strike once'),
 ('STEP','Step unlocked','Step','{BTN_step} Step. A Weave that moves you fast.','Step once'),
 ('SURGE','Surge first full','Surge','{BTN_surge} Release your Surge. It charges as you fight.','Surge once'),
 ('STATUS','First status buildup on player','Status Effects','The bar under your Health fills as an effect builds. When full, it takes hold.','6 s'),
 ('POISE','First enemy staggered','Stagger','Heavy hits break poise. A staggered enemy can take a critical: {BTN_light}.','Crit once'),
 ('LOOT','First item drop','Loot','{BTN_interact} Pick up. Rarer items glow brighter.','Pick up once'),
 ('ANCHOR','First Anchor in 10 m','Anchors','{BTN_interact} Kindle the Anchor. Resting refills you, but normal enemies return.','Kindle'),
 ('LEVEL','First rest with enough Ember to level','Level Up','You have enough Ember to level. Choose Level Up at the Anchor.','Open Level Up'),
 ('DEATH','First death','Shard-ghost','You dropped half your Ember. Reach your ghost to take it back.','Respawn'),
 ('SKILLS','First skill level up','Skills','Skills rise as you use them. Every level in any skill counts toward your character level.','8 s'),
 ('PERKS','First perk point','Perks','Spend perk points in any skill tree. Gates at 25, 50, 75 and 100 unlock deeper nodes.','Open Perks'),
 ('INV','Inventory first opened','Inventory','{BTN_compare} Compare. {BTN_junk} Mark as junk. Weight over 70% slows your roll.','8 s'),
 ('MAP','Map first opened','Map','Climb a region\'s Relay Tower to reveal its map. Lit Anchors are fast travel points.','8 s'),
 ('TOWER','Relay Tower first seen','Relay Towers','Climb this tower to reveal the region on your map.','Reach top'),
 ('SNEAK','First crouch near enemy','Sneaking','{BTN_crouch} Crouch. The eye shows how close you are to being seen. Sneak attacks deal triple damage.','Sneak attack'),
 ('LOCKPICK','First lock','Lockpicking','Turn {BTN_look} to find the sweet spot. {BTN_confirm} Turn the lock. Picks can break.','Open or leave'),
 ('SMITH','First smithing bench','Smithing','Spend materials to raise a weapon\'s level. Engineering adds up to 15% more.','Upgrade once'),
 ('DIALOGUE','First dialogue','Dialogue','Options in brackets need a skill or faction. Your chance is shown when you hover them.','8 s'),
 ('COMPANION','First companion recruited','Companions','{CMP_name} now follows you. Their loyalty changes with your choices.','8 s'),
 ('VEHICLE','First Strider or skimmer','Vehicles','{BTN_interact} Mount. {BTN_boost} Boost. {BTN_glide} Glide (Strider).','Mount'),
 ('ECHO','First boss fog with Echo item','Echoes','Use an Echo at an Anchor to summon a spirit ally for the next boss.','8 s'),
 ('COOP','Co-op menu first opened','Co-op','Place a summon sign to help others, or invite a friend. Enemies get tougher with more players.','8 s'),
 ('NOTES','First Shard-note seen','Shard-notes','Messages from other players. Rate the helpful ones; it heals the writer.','8 s'),
 ('EXPLORER','Journal first opened','Explorer Mode','Prefer no markers? Turn on Explorer Mode for written directions.','8 s'),
 ('RESONANCE','First Resonance','Resonances','Equip a Resonance in Abilities. It is strong but has a long cooldown.','Equip'),
 ('FACTION','First faction invitation','Factions','Some factions are rivals. Joining one can lock another out for good.','8 s'),
 ('QUIET','Enter the Quiet first time','The Quiet','Weekly Strikes, Citadels and the Raid live here. They reset every Tuesday.','8 s')]
for k, trig, t, b, done in TUT:
    pop(f'TUT_{k}', 'tutorial', 'HUD', f'{trig}; once per profile; completes on: {done}', t, b, '', None, 3, 'SFX_UI_TUTORIAL')

# --- confirmations ---
rows('modal', 'Various', '''
CNF_NEW_GAME|Select New Game with existing saves|New Game|Start a new character? Your other saves are kept.|Until input|Confirm / Cancel
CNF_OVERWRITE|Save over an existing slot|Overwrite Save|Replace this save with your current game?|Until input|Overwrite / Cancel
CNF_DELETE_SAVE|Delete save in Load menu|Delete Save|Delete {VAR_char_name}, Level {VAR_level}? This cannot be undone.|Until input|Delete / Cancel
CNF_LOAD|Load while playing|Load Game|Load this save? Unsaved progress will be lost.|Until input|Load / Cancel
CNF_QUIT_TITLE|Quit to Title|Quit to Title|Quit to the title screen? Unsaved progress since {VAR_time} will be lost.|Until input|Quit / Cancel
CNF_QUIT_DESK|Quit to Desktop|Quit Game|Quit to desktop? Unsaved progress since {VAR_time} will be lost.|Until input|Quit / Cancel
CNF_SELL_RARE|Sell item Relic or higher|Sell {ITM_rarity}|Sell {ITM_name} for {VAR_price} Ember?|Until input|Sell / Cancel
CNF_DISMANTLE|Dismantle upgraded or Rare+ item|Dismantle|Break down {ITM_name}? You get {VAR_mats}.|Until input|Dismantle / Cancel
CNF_DROP_RARE|Drop Rare or higher item|Drop Item|Drop {ITM_name}? It stays here until you leave the region.|Until input|Drop / Cancel
CNF_LEVEL|Confirm level up allocation|Confirm Level|Spend {VAR_cost} Ember to reach Level {VAR_level}?|Until input|Confirm / Cancel
CNF_PERK|Unlock perk node|Unlock Perk|Unlock {PRK_name}? Perks can only be reset at Anchors.|Until input|Unlock / Cancel
CNF_RESPEC|Reset perk tree|Reset {SKL_name} Perks|Refund {VAR_n} perks for {VAR_cost} Ember?|Until input|Reset / Cancel
CNF_LEGEND|Make skill Legendary|Make Legendary|{SKL_name} returns to 15 and {VAR_n} perks are refunded. Continue?|Until input|Confirm / Cancel
CNF_FACTION_JOIN|Join a faction with a rival|Join {FAC_name}|Joining will close the {FAC_rival} questline for good. Join anyway?|Until input|Join / Not Yet
CNF_FAST_TRAVEL|Select fast travel point|Fast Travel|Travel to {VAR_anchor_name}?|Until input|Travel / Cancel
CNF_TRAVEL_GHOST|Fast travel with Shard-ghost out in another region|Leave Your Ghost?|Your Shard-ghost holds {VAR_n} Ember. It stays where it is.|Until input|Travel / Cancel
CNF_REST_COOP|Host rests at Anchor in co-op|Rest|Resting ends this co-op session. Continue?|Until input|Rest / Cancel
CNF_LEAVE_COOP|Guest leaves session|Leave Session|Return to your world?|Until input|Leave / Stay
CNF_KICK|Host removes player|Remove Player|Remove {VAR_player}?|Until input|Remove / Cancel
CNF_INVASIONS_ON|Turn invasions on|Allow Invasions|Other players will be able to invade your world. Turn on?|Until input|Turn On / Cancel
CNF_LEAVE_ACTIVITY|Leave Strike, Raid or Arena early|Leave Activity|Leave now? You will not get rewards. Arena leavers get a 10 minute matchmaking lock.|Until input|Leave / Stay
CNF_BUY|Buy cosmetic|Confirm Purchase|Buy {VAR_item} for {VAR_price}? Charged through your platform store.|Until input|Buy / Cancel
CNF_SKIP_CINE|Press skip during cutscene|Skip Scene|Skip this scene?|Until input|Skip / Watch
CNF_DISMISS_CMP|Part ways with companion|Part Ways|Send {CMP_name} back to {VAR_location}?|Until input|Confirm / Cancel
CNF_PICKPOCKET|Pickpocket with chance under 25%|Low Chance|Your chance is {VAR_pct}%. Getting caught adds a bounty. Try anyway?|Until input|Try / Cancel
CNF_ATTACK_NEUTRAL|First attack on non-hostile NPC|Attack {ACT_name}?|This will make {FAC_name} hostile.|Until input|Attack / Cancel
CNF_DEFEAT_MODE|Toggle Defeat Mode on|Defeat Mode|You will keep all Ember when you fall. You can turn this off at any time.|Until input|Turn On / Cancel
CNF_MODS|Load save with mods enabled|Mods Active|Achievements are off for saves with mods. Continue?|Until input|Continue / Cancel
CNF_RESET_BINDS|Reset all bindings|Reset Bindings|Reset every binding to default?|Until input|Reset / Cancel
CNF_DISPLAY|Display mode changed|Keep Settings?|Reverting in {VAR_s}s.|15.0|Keep / Revert
CNF_ENDING|Choose an ending at final Shard|Final Choice|This choice ends the story. You can keep playing afterward. Your save will be backed up first.|Until input|Choose / Not Yet
''', prio=5)

# --- errors ---
rows('error', 'Various', '''
ERR_SAVE_FAIL|Save write fails|Save Failed|Your game could not be saved. Check free space and try again.|Until input|Retry / Cancel
ERR_SAVE_CORRUPT|Save fails checksum on load|Damaged Save|This save is damaged. Load the backup from {VAR_time}?|Until input|Load Backup / Cancel
ERR_LOAD_FAIL|Load fails|Load Failed|This save could not be loaded.|Until input|OK
ERR_VERSION|Save from newer build|Newer Save|This save was made with a newer version. Update the game to load it.|Until input|OK
ERR_DLC_MISSING|Save needs expansion not installed|Content Missing|This save uses {VAR_dlc}. Install it to continue.|Until input|OK
ERR_NET_LOST|Server connection drops in online activity|Connection Lost|You were disconnected. Error {VAR_code}.|Until input|OK
ERR_HOST_LEFT|Host leaves co-op|Host Left|The host left. Returning to your world.|5.0|OK
ERR_SESSION_FULL|Join a full session|Session Full|That world is full.|Until input|OK
ERR_JOIN_FAIL|Join fails|Could Not Join|Could not join {VAR_player}. Error {VAR_code}.|Until input|OK
ERR_VERSION_MISMATCH|Peers on different builds|Version Mismatch|You and {VAR_player} are on different versions.|Until input|OK
ERR_NAT|Strict NAT detected|Network Limited|Your network type is strict. You may not be able to join some players.|Until input|OK
ERR_MM_TIMEOUT|Matchmaking passes 5 minutes|No Match Found|No players found. Keep searching?|Until input|Keep Searching / Stop
ERR_SERVERS_DOWN|Service health check fails|Servers Unavailable|Online services are down. You can keep playing offline.|Until input|OK
ERR_KICKED|Removed by host|Removed|You were removed from {VAR_player}'s world.|Until input|OK
ERR_BANNED|Account restricted|Account Restricted|Your account cannot use online play until {VAR_date}.|Until input|OK
ERR_ACTIVITY_LOCK|Activity needs more players|Need a Fireteam|{VAR_activity} needs {VAR_n} players.|Until input|OK
ERR_POWER_LOW|Launch activity under recommended power by 20+|Power Too Low|Recommended Power is {VAR_n}. You can still launch.|Until input|Launch / Cancel
ERR_PURCHASE|Store purchase fails|Purchase Failed|Nothing was charged. Error {VAR_code}.|Until input|OK
ERR_STORAGE|Not enough disk space|Storage Full|{VAR_mb} MB more is needed to save.|Until input|OK
ERR_CTRL|Controller disconnects|Controller Disconnected|Reconnect your controller to continue.|Until input|OK
ERR_GPU|Unsupported GPU or driver at launch|Graphics Driver|Your graphics driver is out of date. Update to {VAR_version} or newer for best results.|Until input|Continue / Quit
ERR_SHADERS|Shader compile on first launch|Preparing Shaders|Building shaders for your system. {VAR_pct}%|Until done|
ERR_MOD|Mod fails to load|Mod Error|{VAR_mod} failed to load and was turned off.|Until input|OK
''', prio=6)

# --- inline denials (short, on the current screen) ---
rows('inline', 'Various', '''
INL_CANT_COMBAT|Menu action blocked while enemies are aware|You cannot do that in combat.|
INL_CANT_REST_ENEMY|Rest pressed with enemy within 30 m|Enemies are near.|
INL_NOT_ENOUGH_EMBER|Buy or level without Ember|Not enough Ember.|
INL_NOT_ENOUGH_MATS|Upgrade without materials|Not enough materials.|
INL_INV_FULL|Pickup when weight cap of storage reached|Inventory full.|
INL_REQ_ATTR|Equip below requirements|Requirements not met. Damage -40%.|
INL_LOCKED|Use locked door without key|Locked.|
INL_LOCKED_KEY|Locked door needing key|Requires {ITM_name}.|
INL_LOCKED_OTHER|Door opens from the other side|It opens from the other side.|
INL_NO_PICKS|Lock with no lockpicks|You have no lockpicks.|
INL_PICK_BROKE|Lockpick breaks|Lockpick broke.|
INL_CANT_SLEEP|Sleep in owned bed|This bed belongs to someone.|
INL_CANT_SAVE|Manual save during boss or combat|You cannot save right now.|
INL_ON_COOLDOWN|Ability pressed while cooling down|Not ready.|
INL_NO_BREATH|Action needing Breath at 0|Out of Breath.|
INL_SHARDBORN_ONE|Equip second Shardborn of same type|Only one Shardborn {VAR_type} at a time.|
INL_NO_TARGET|Lock-on with no target|No target.|
INL_TRAVEL_BLOCK|Fast travel in combat or over weight|You cannot travel right now.|
INL_QUEST_ITEM|Drop or sell quest item|Quest items cannot be removed.|
INL_STOLEN_SELL|Sell stolen item to non-fence|They will not buy stolen goods.|
''', prio=1)

# --- loading tips (rotate every 8 s; region tips weighted 2x in that region) ---
TIPS = ['Rolling makes you untouchable for the first 12 frames. Light loads roll faster.',
 'Your Ward refills fully 4.5 seconds after the last hit you take.',
 'Breath starts refilling 1.2 seconds after you stop using it.',
 'Parry windows are 7 frames. Bucklers give 8.',
 'Every Vigor point adds 8 to Health, Ward or Breath.',
 'Each counter element deals triple damage to its opposite Ward. Ember beats Frost. Storm beats Iron. Hollow beats Bloom.',
 'Resting at an Anchor refills Tonics, but normal enemies come back.',
 'When you fall you drop all carried Ember as a Shard-ghost. Die again before you reach it and half of it burns.',
 'Defeat Mode lets you keep all Ember when you fall. Find it in Options.',
 'You start with 4 Tonics and can carry up to 12.',
 'Climb a region\'s Relay Tower to reveal its map.',
 'Every skill level you gain counts toward your character level.',
 'Perk tree gates open at skill levels 25, 50, 75 and 100.',
 'Smithing upgrades get up to 15% more from Engineering perks.',
 'Only one Shardborn weapon and one Shardborn armor piece can be equipped at a time.',
 'Sneak attacks deal triple damage. Daggers deal more.',
 'Heavy hits break poise. Staggered enemies take criticals.',
 'Firearm headshots deal double damage once the target\'s Ward is down.',
 'Shock stops Ward recharge. Use it before you burst a shielded foe.',
 'Shatter makes targets take 25% more poise and physical damage.',
 'Root holds a target in place for 2.5 seconds, but they can still swing.',
 'Burn deals 2% of max Health every second for 6 seconds.',
 'Co-op enemies get 50 to 85% more health for each extra player.',
 'Echoes are spirit allies you summon at an Anchor before a boss.',
 'Rate a helpful Shard-note and its writer gets healed.',
 'Explorer Mode hides markers and writes out directions in the journal.',
 'The Salvagers\' Guild fences stolen goods. Nobody else will.',
 'Joining some factions closes others. Check the Factions screen before you swear in.',
 'Companions change loyalty based on your choices. At Devoted they unlock a final quest.',
 'Ostra remembers more as you claim Shards.',
 'Remnant drones share targets. Kill the relay unit first.',
 'Thorn raiders rush when they outnumber you. Use doorways.',
 'Choirborn teleport after taking a heavy hit. Watch for the shimmer.',
 'Hollowed leaders buff every Hollowed within 20 m.',
 'Boss health bars show notches where phases change.',
 'Weekly Strikes and Citadels reset every Tuesday at 17:00 UTC.',
 'You can earn up to 100 Seals a week.',
 'The Wardrobe Shop sells cosmetics only. Nothing in it changes stats.',
 'Strider glide drains Breath. Land before it runs dry.',
 'Skimmers boost for 3 seconds and recharge in 6.',
 'Hauler turrets overheat after 4 seconds of fire.',
 'Lantern Hold storage holds what your pack cannot.',
 'Mirrors in Lantern Hold let you change your look for free.',
 'Assist Mode adds aim help and widens parry windows. Achievements stay on.',
 'Shardstorms drain Ward. Get under a roof.',
 'Hold to toggle options are in Accessibility.',
 'Infused weapons trade attribute scaling for elemental damage.',
 'Legendary skills reset to 15 so you can keep leveling.',
 'Speech checks show your chance before you pick them.',
 'Bribes cost Ember but always work if you can pay.',
 'Status buildup decays after 3 seconds without new hits.',
 'Enemies return to their posts if you break line of sight for 20 seconds.']
LORE = ['The Meridian fell for nine days. The logs say no one aboard slept.',
 'Lantern priests read the logs aloud at dusk. Nobody knows who wrote log zero.',
 'Hull Knights still salute the bridge, though no bridge remains.',
 'Choir scholars say the Shards sing. The ones who agree tend to vanish.',
 'Cinderreach was farmland before the ship came down.',
 'The Hollowed were people once. Some still carry their names stitched inside their coats.',
 'Ostra speaks in fragments. Some of them contradict each other.',
 'Something second is waking in orbit. The Choir calls it the Hollowing.']
for i, t in enumerate(TIPS):
    R.append((f'STR_TIP_{i+1:03d}', 'Loading screens', t, 'Gameplay tip; rotates every 8 s, min 1 shown'))
for i, t in enumerate(LORE):
    R.append((f'STR_LORE_{i+1:02d}', 'Loading screens', t, 'Lore line, shown above tip'))
for k, n, b in REGIONS:
    R.append((f'STR_TIP_REG_{k}', 'Loading screens', f'{n} is meant for level {b}.' if b[0].isdigit() else f'{n}.', 'Region tip'))
pop('LDG_TIP', 'banner', 'Loading screens', 'Any load over 2 s; pick 1 lore line + 1 tip, no repeat within 10 loads',
    '', '{VAR_lore}\n{VAR_tip}', '', '8.0 per tip; holds until load ends', 1, '')

# --- achievements (60, matching UV-080) ---
ACH = [('First Light','Kindle your first Anchor.'),('Ashes to Ashes','Claim the Shard of Cinderreach.'),
 ('Salt of the Earth','Claim the Shard of Saltmere.'),('Through the Thorns','Claim the Shard of Thornwood.'),
 ('Glass Heart','Claim the Shard of Glasswaste.'),('Cold Comfort','Claim the Shard of Rimefall.'),
 ('Into the Deep','Claim the Shard of Hollowdeep.'),('Homeward','See the ending where the ship is restored.'),
 ('Binding Oath','See the ending where the Shards are bound.'),('Captain Now','See the ending where you take the ship.'),
 ('All Six','Climb every Relay Tower.'),('Cartographer','Explore 100% of every surface region.'),
 ('Down Below','Reach the Undervault.'),('Into the Quiet','Enter the Quiet.'),('Field Notes','Defeat all 12 field bosses.'),
 ('Site Unseen','Defeat all 12 site bosses.'),('Citadel Sweep','Defeat all 6 Citadel bosses.'),('Sworn Knight','Reach Exalted with the Hull Knights.'),
 ('Keeper of Logs','Reach Exalted with the Lantern Church.'),('Everything Has a Price','Reach Exalted with the Salvagers\' Guild.'),
 ('Never Twice','Reach Exalted with the Quiet Hand.'),('Heard the Song','Reach Exalted with the Choir.'),
 ('Not Alone','Recruit your first companion.'),('Full Crew','Recruit all 8 companions.'),('Devoted','Bring a companion to Devoted loyalty.'),
 ('Their Story','Finish a companion questline.'),('Master of One','Raise any skill to 100.'),('Legend','Make a skill Legendary.'),
 ('Jack of All','Raise every skill to 50.'),('Full Tree','Unlock every perk in one tree.'),('Level 25','Reach character level 25.'),
 ('Level 50','Reach character level 50.'),('Level 70','Reach character level 70.'),('First Shardborn','Find a Shardborn item.'),
 ('Collector','Own 20 Shardborn items.'),('Plus Ten','Upgrade a weapon to its maximum level.'),('Rite Writer','Craft your first Rite.'),
 ('Brewmaster','Learn every brewing recipe.'),('Perfect Timing','Parry 100 attacks.'),('Ward Breaker','Break 500 enemy Wards.'),
 ('Six Elements','Apply all six status effects in one fight.'),('Clean Hands','Pickpocket 50 items without being caught.'),
 ('Silver Tongue','Pass 50 Speech checks.'),('Ghost Runner','Recover your Shard-ghost 25 times.'),('No Ghosts','Claim any Shard without falling in that region.'),
 ('Friend in Need','Help another player defeat a boss.'),('Invader','Defeat a host as an invader.'),('Defender','Defeat 10 invaders.'),
 ('Fireteam','Complete a Strike.'),('Weekly Regular','Complete Strikes in 4 different weeks.'),('Raid Day','Complete the Raid.'),
 ('Flawless Raid','Complete the Raid with no fireteam deaths.'),('Arena Debut','Win an Arena match.'),('Power Play','Get 3 kills with one power weapon pickup.'),
 ('Strider Flight','Glide 500 m in one go.'),('Hijacker','Hijack an enemy flyer.'),('Kind Words','Have your Shard-notes rated helpful 100 times.'),
 ('Ostra Remembers','Recover all of Ostra\'s memory fragments.'),('Scripture','Find every ship log.'),('Shardfall','Earn every other achievement.')]
for i, (n, d) in enumerate(ACH):
    R += [(f'STR_ACH_{i+1:02d}', 'Platform overlays', n, 'Achievement name'), (f'STR_ACH_{i+1:02d}_DESC', 'Platform overlays', d, 'Achievement description')]

# --- write ---
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # data/ui (was an absolute shared path; broke sandbox builds)
os.makedirs(out, exist_ok=True)
seen = set()
with open(f'{out}/strings.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['str_id', 'screen', 'text_en', 'max_chars', 'tokens', 'notes'])
    for sid, scr, txt, note in R:
        assert sid not in seen, sid
        seen.add(sid)
        toks = ' '.join(sorted(set(re.findall(r'\{([A-Z]+_[A-Za-z0-9_]+)\}', txt))))
        w.writerow([sid, scr, txt, max(8, int(len(txt) * 1.4 + 0.5)), toks, note])
with open(f'{out}/popups.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(P[0].keys()))
    w.writeheader()
    w.writerows(P)
print(len(R), 'strings', len(P), 'popups')
