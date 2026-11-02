#!/usr/bin/env python3
"""Shardfall open-world simulation tables: crime/bounty/guards, town life/schedules, physics/destruction.
Reads data/ read-only. Every value not cited to the plan or data/ is a SIM design choice (3 Oct 2026).
Run from anywhere: python3 design/simulation/tools/gen_sim.py"""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
DATA = os.path.join(OUT, '..', '..', 'data')

def rd(p):
    with open(os.path.join(DATA, p), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def T(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print(f'{name}: {len(rows)} rows')

REG = {r['reg_id']: r for r in rd('world/regions.csv')}
STR = []  # (str_id, english, context, max_chars)
def S(sid, en, ctx):
    STR.append((sid, en, ctx, int(len(en) * 1.4) + 1)); return sid

# ---------------------------------------------------------------- time
T('sim_time.csv', ['key', 'value', 'unit', 'source', 'notes'], [
    ['TIMESCALE', 20, 'game s per real s', 'SIM choice', '1 game day = 72 real minutes; matches Skyrim default so schedules read at walking pace'],
    ['DAY_LENGTH_REAL_MIN', 72, 'real min', 'derived', ''],
    ['DAWN_START', '05:00', 'game time', 'SIM choice', 'Street lamps go out 05:30'],
    ['DAY_START', '07:00', 'game time', 'SIM choice', 'Shops open'],
    ['DUSK_START', '19:00', 'game time', 'SIM choice', 'Street lamps lit 19:30, shops close 20:00'],
    ['NIGHT_START', '21:00', 'game time', 'SIM choice', 'Curfew in Lantern Hold upper decks; night guard shift'],
    ['WAIT_MAX_H', 24, 'game h', 'SIM choice', 'Wait/rest at an Anchor or bed, 1 h steps; blocked in combat, Searching or with a guard within 20 m while bounty > 0'],
    ['WAIT_SPEED', 'one game h per 0.5 real s', '', 'SIM choice', 'Schedules fast-forward via catch-up rules (sim_lod.csv)'],
    ['VENDOR_RESTOCK_H', 72, 'game h', 'plan 3.10', ''],
    ['GAME_WEEK_DAYS', 7, 'game days', 'SIM choice', 'Used by reputation_actions weekly caps (RPA_DONATE) and guard leniency'],
    ['TIME_IN_COOP', 'host clock', '', 'SIM choice', 'Guests adopt host time on join; their own world time is restored on leave'],
])

# ---------------------------------------------------------------- jurisdictions
JUR = []
for rid in ['REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06', 'REG_HUB']:
    r = REG[rid]
    lvl = int(r['level_max']) + 5 if rid != 'REG_HUB' else 75
    law = {'REG_01': 'Cinder Wardens', 'REG_02': 'Saltmere Tidewatch', 'REG_03': 'Thornwood Rangers', 'REG_04': 'Glass Compact', 'REG_05': 'Rimefall Hearthguard', 'REG_06': 'Hollowdeep Lampmen', 'REG_HUB': 'Hull Knights (Lantern Hold Watch)'}[rid]
    JUR.append([f'JUR_{rid[4:]}', rid, r['name'], law, lvl, 1.5 if rid == 'REG_HUB' else 1.0,
                'FAC_HULLKNIGHTS' if rid == 'REG_HUB' else '', S(f'STR_JUR_{rid[4:]}_NAME', law, 'Jurisdiction / guard force name')])
JUR.append(['JUR_NONE', 'REG_Q; REG_U; wilderness outside town bounds', 'No law', '-', '-', 0, '', ''])
T('crime_jurisdictions.csv', ['jur_id', 'reg_id', 'region', 'guard_force', 'guard_level', 'bounty_mult', 'faction_link', 'str_id'], JUR + [])

# ---------------------------------------------------------------- crimes
# bounty in Ember; violent crimes never decay
CR = [
 # id, crime, trigger, bounty, violent, rep, response floor, notes
 ['CRM_TRESPASS', 'Trespassing', 'In a private or restricted volume (TRIGGER_PRIVATE) after one warning bark and 10 s grace', 25, 0, '', 'WARN', 'Doors marked Private show a red lock tint; inns, shops after hours, faction back rooms'],
 ['CRM_LOCKPICK', 'Lockpicking', 'Seen starting or finishing a lock on owned property (STA_LOCKPICK)', 50, 0, '', 'APPROACH', 'Failed attempt seen counts the same'],
 ['CRM_PICKPOCKET', 'Pickpocketing', 'STA_PICKPOCKET fails, or success is seen by a third party', 50, 0, '', 'APPROACH', 'Plus the theft bounty of the item if it was taken'],
 ['CRM_THEFT', 'Theft', 'Taking an owned item (red-marked prompt) while seen', 'max(10, 0.5 x item value)', 0, '', 'APPROACH', 'Item tagged Stolen whether seen or not'],
 ['CRM_THEFT_VEHICLE', 'Vehicle or Strider theft', 'Mounting an owned skimmer, hauler or Strider', 200, 0, '', 'APPROACH', 'Owned mounts show the owner name on the prompt'],
 ['CRM_VANDAL', 'Vandalism', 'Destroying an owned destructible (DST_* with owner)', 'repair cost x 1.0 (DST row)', 0, '', 'APPROACH', 'Barrels, stalls, fences, windows'],
 ['CRM_ARSON', 'Arson', 'Owned building prop set Burning by the player (Ember spread counts)', 500, 1, '', 'ARREST', 'Fire caused by an enemy you lured does not count'],
 ['CRM_WEAVE_TOWN', 'Reckless casting', 'Cast or Surge that deals damage to an owned object or civilian in a town', 100, 1, '', 'APPROACH', 'Healing and buffs are legal'],
 ['CRM_ASSAULT', 'Assault', 'Damaging a civilian or guard who did not attack first', 300, 1, '', 'ARREST', 'Brawls started by dialogue do not count'],
 ['CRM_ASSAULT_GUARD', 'Assaulting a guard', 'Damaging a guard', 600, 1, '', 'ARREST', 'Stacks with CRM_ASSAULT'],
 ['CRM_MURDER', 'Murder', 'Killing a civilian or faction member', 1000, 1, 'RPA_KILL_MEMBER (faction members only)', 'HUNT', 'Opens the Quiet Hand join path (FAC_QUIETHAND requirement)'],
 ['CRM_MURDER_GUARD', 'Killing a guard', 'Killing a guard', 1500, 1, '', 'HUNT', ''],
 ['CRM_ANIMAL', 'Killing livestock', 'Killing an owned animal or Strider', 100, 1, '', 'APPROACH', ''],
 ['CRM_RESIST', 'Resisting arrest', 'Choosing Resist, fleeing during ARREST, or attacking the arresting guard', 500, 1, '', 'HUNT', ''],
 ['CRM_ESCAPE', 'Jailbreak', 'Leaving a cell before the sentence ends', 500, 0, '', 'ARREST', 'Confiscated items stay in the evidence chest'],
 ['CRM_HALL_CRIME', 'Crime in a faction hall', 'Any crime above inside a faction hall volume', 'base crime', 0, 'RPA_CRIME_SEEN', 'as base', 'Extra reputation penalty for the hall owner'],
]
T('crime_types.csv', ['crime_id', 'crime', 'trigger', 'bounty_ember', 'violent (no decay)', 'rep_action', 'min_response', 'notes', 'str_id'],
  [c + [S(f'STR_{c[0]}_NAME', c[1], 'Crime name in bounty log')] for c in CR])

T('bounty_tiers.csv', ['tier_id', 'tier', 'bounty_min', 'bounty_max', 'guard_response', 'civilian_reaction', 'vendors', 'map_icon', 'bounty_hunters'], [
 ['BTY_CLEAN', 'Clean', 0, 0, 'Greet / ignore', 'Normal', 'Normal', 'none', 'no'],
 ['BTY_FINE', 'Wanted (fine)', 1, 499, 'APPROACH on sight; offers pay, jail, persuade', 'Normal', 'Normal', 'UI_ICON_BOUNTY_1', 'no'],
 ['BTY_ARREST', 'Wanted (arrest)', 500, 1999, 'ARREST on sight; weapons drawn', 'Avoid player, close doors', 'Refuse trade in that jurisdiction (fences excepted)', 'UI_ICON_BOUNTY_2', 'no'],
 ['BTY_HUNTED', 'Hunted', 2000, 4999, 'Attack on sight; offers surrender once at Ward 0', 'Flee and report', 'Refuse', 'UI_ICON_BOUNTY_3', '1 hunter squad per 2 game days in that region'],
 ['BTY_OUTLAW', 'Outlaw', 5000, 999999, 'Attack on sight; no surrender; town gates closed', 'Flee', 'Refuse', 'UI_ICON_BOUNTY_4', '1 squad per game day, +1 elite at 10000'],
])

T('bounty_rules.csv', ['rule_id', 'rule', 'value', 'source', 'notes'], [
 ['BR_PER_JUR', 'Bounty is tracked per jurisdiction', 'crime_jurisdictions.csv', 'plan 4.4; Skyrim hold model', 'Crimes in Lantern Hold x1.5'],
 ['BR_WITNESS', 'A crime gives bounty only once reported', 'report delay 10 s (FAC_TOWN in systems/stealth_faction_rules.csv)', 'systems', 'Guard witness reports instantly'],
 ['BR_UNSEEN', 'Unseen crimes', 'no bounty; theft still tags items Stolen', 'SIM choice', 'Owners notice missing high-value items (>500) after 24 game h: +1 town suspicion'],
 ['BR_KILL_WITNESS', 'Killing every witness before the report clears the pending crime', 'pending crime cleared; the kill is its own crime if seen', 'SIM choice', 'Witness flees at 6 m/s toward nearest guard'],
 ['BR_DECAY', 'Non-violent bounty decays', '-5% per game day with no new crime in that jurisdiction, floor 0', 'SIM choice', 'Violent bounty never decays'],
 ['BR_PAY', 'Pay at any guard or Bounty Board', 'cost = bounty in Ember; clears all; stolen items on you confiscated', 'SIM choice', 'Ember is the only currency (plan 3.10)'],
 ['BR_PAY_REMOTE', 'Pay through a Salvagers fence', 'bounty x 1.25, max bounty 1999', 'SIM choice', 'Needs Salvagers Friendly'],
 ['BR_JAIL', 'Serve time', '1 game h per 50 bounty, min 6 h, max 72 h', 'SIM choice', 'Bounty cleared; stolen items confiscated; other gear kept'],
 ['BR_JAIL_PENALTY', 'Jail penalty', 'lose 25% of current XP progress toward next rank in the 2 highest skills per 24 h served (never a rank)', 'SIM choice; softened from Oblivion skill loss', 'Shown in the sentence popup before accepting'],
 ['BR_JAIL_SKIP', 'Skip remaining sentence', 'pay remaining h x 50 Ember', 'SIM choice', 'Offered by the cell door'],
 ['BR_ESCAPE', 'Escape jail', 'cell lock tier 3; evidence chest tier 4; adds CRM_ESCAPE', 'SIM choice', 'Every jail has one authored escape tunnel'],
 ['BR_PERSUADE', 'Talk your way out', 'Speech check: rank >= bounty / 20 (max 1000 bounty); success clears, fail +10%', 'SIM choice', 'Once per guard per game day'],
 ['BR_BRIBE', 'Bribe', '0.5 x bounty, needs Speech 40, bounty < 1000', 'SIM choice', 'Fails silently if a second guard is within 15 m'],
 ['BR_FACTION', 'Faction favour', 'Hull Knights Honored+: clear a bounty under 1000 once per game week', 'SIM choice', 'Dialogue line on any guard'],
 ['BR_DEATH', 'Dying with a bounty', 'bounty kept; you respawn at your Anchor as normal', 'plan 3.4 death rules', 'Guards do not camp Anchors'],
 ['BR_MASK', 'Masked crimes', 'with a Quiet Hand mask on, bounty goes to the mask identity; removing the mask while unseen for 30 s drops it', 'SIM choice', 'Mask identity bounty is cleared on mask unequip at a Still Room'],
 ['BR_COOP', 'Co-op', 'bounty and jail belong to the offending player only; guards target that player; a jailed guest watches a timer and may skip it', 'SIM choice', 'Helping a wanted player fight guards = CRM_ASSAULT_GUARD'],
 ['BR_PVP', 'Invasion', 'invaders commit no crimes; town guards ignore invasion combat', 'SIM choice', 'Towns block invasions inside walls (plan 3.11 opt-in)'],
 ['BR_QUEST_SAFE', 'Quest exemptions', 'quest-flagged thefts and kills do not raise bounty', 'SIM choice', 'Flag on the quest step'],
 ['BR_HUNTER', 'Bounty hunters', 'squad of 3 guards of the jurisdiction at guard_level; spawn on roads 150-300 m from player, out of sight', 'SIM choice', 'Not in sites, Citadels or co-op guest worlds'],
])

T('stolen_goods.csv', ['rule_id', 'rule', 'value', 'notes'], [
 ['SG_TAG', 'Stolen tag', 'item flag Stolen + owner id', 'Tooltip red hand icon UI_ICON_STOLEN'],
 ['SG_SELL', 'Normal vendors refuse Stolen items', '-', ''],
 ['SG_FENCE', 'Fence buy price', '0.35 x value, +0.05 per Salvagers tier above Neutral (max 0.55)', 'RPA_FENCE: +50 rep per 5000 fenced'],
 ['SG_FENCE_CAP', 'Fence cash per restock', '4000 Ember x region number (Hub 25000)', 'Plan says no vendor gold caps; fences are the one exception (SIM choice)'],
 ['SG_CLEAR', 'Stolen tag clears', 'after selling, or after 30 game days owned', ''],
 ['SG_OWNER', 'Owner sees you holding their item', '+theft bounty, owner asks for it back (return = bounty cleared)', ''],
 ['SG_CONFISCATE', 'Arrest or pay', 'all Stolen items moved to the jail evidence chest', ''],
])

# guard response state machine
GS = [
 ['GRD_IDLE', 'Idle / patrol', 'Default', 'Runs schedule (SCH_GUARD_*)', '-', ''],
 ['GRD_WARN', 'Warn', 'CRM_TRESPASS grace or weapon drawn within 5 m for 3 s', 'Walks to 3 m, bark; 10 s to comply', 'BARK_GUARD_WARN', 'Comply = IDLE'],
 ['GRD_APPROACH', 'Approach', 'Bounty tier FINE seen, or a min_response APPROACH crime reported', 'Walks to player at 3.5 m/s, opens dialogue at 2.5 m', 'BARK_GUARD_STOP', 'Dialogue: Pay / Jail / Persuade / Bribe / Faction / Resist'],
 ['GRD_ARREST', 'Arrest', 'Tier ARREST, or crime with min_response ARREST', 'Runs at 5.5 m/s, weapon drawn; dialogue Pay / Jail / Resist only', 'BARK_GUARD_ARREST', 'Moving away > 8 m during dialogue = Resist'],
 ['GRD_COMBAT', 'Combat', 'Resist, tier HUNTED+, or attacked', 'Encounter AI with AIP_GUARD_*; calls other guards within 40 m', 'BARK_GUARD_COMBAT', 'Leaving the jurisdiction by 100 m and unseen 30 s = SEARCH'],
 ['GRD_SURRENDER', 'Surrender offer', 'HUNTED and player Ward 0, once per fight', 'Guard stops for 3 s and shouts Yield; player sheaths to accept (goes to Jail)', 'BARK_GUARD_YIELD', ''],
 ['GRD_SEARCH', 'Search', 'Lost sight of a wanted player', 'Uses STL_SEARCHING / STL_LOST from systems', '', 'Returns to IDLE after 60 s'],
 ['GRD_ESCORT', 'Escort to jail', 'Player chose Jail', 'Fade to black 1.0 s, teleport to cell, sentence popup', '', ''],
 ['GRD_FLEE_NONE', 'Guards never flee', '-', 'Morale ignored', '', 'Exception to FRM_MORALE'],
]
T('guard_states.csv', ['state_id', 'state', 'enter', 'behaviour', 'bark', 'exit/notes'], GS)

T('guard_profiles.csv', ['guard_id', 'role', 'level', 'count_per_town', 'weapon_kit', 'sight_m', 'fov_deg', 'hearing_m', 'reaction_ms', 'notes'], [
 ['GRD_WATCH', 'Watch (sword and shield)', 'guard_level', '60%', 'Straight sword + kite shield', 30, 110, 18, 400, 'Patrols and posts'],
 ['GRD_ARCHER', 'Watch rifle', 'guard_level', '25%', 'Rifle (common ammo)', 45, 90, 18, 450, 'Walls and towers'],
 ['GRD_CAPTAIN', 'Captain', 'guard_level + 3', '1 per town', 'Greatsword or polearm', 30, 120, 20, 350, 'Leader role; heavy stance'],
 ['GRD_WARDEN', 'Weave warden', 'guard_level', '15%', 'Catalyst, Warding', 30, 110, 20, 400, 'Counter-casts in REG_04+'],
 ['GRD_HUNTER', 'Bounty hunter', 'guard_level', 'squads of 3', 'Mixed', 40, 120, 22, 350, 'Spawned by BR_HUNTER'],
])

# ---------------------------------------------------------------- town life
T('town_tiers.csv', ['tier_id', 'tier', 'examples', 'population', 'guards', 'vendors', 'inn', 'jail', 'smart_objects', 'full_sim_npcs_max', 'notes'], [
 ['TWN_HAMLET', 'Hamlet', 'Roadside camps, farms', '6-12', '0-2', '1', 'no', 'no', '20-40', 12, 'Crimes reported to nearest town'],
 ['TWN_TOWN', 'Town', 'LOC_TOWN_REG_* (2-3 per region, plan 3.7)', '25-45', '8-12', '4-6 incl. 1 fence', 'yes', 'yes', '120-200', 40, 'Has a Bounty Board'],
 ['TWN_CITY', 'City', 'Lantern Hold (REG_HUB)', '160 placed, 60 full-sim at once', '40', 'all hub vendors + 2 fences', '3', 'yes (Brig)', '900', 60, 'District-based streaming; curfew upper decks 21:00-05:00'],
])

ARCH = [  # schedule id, archetype, blocks: (start,end,activity,smart object)
 ('SCH_GUARD_DAY', 'Guard (day shift)', [(6, 7, 'Barracks: eat', 'SO_TABLE'), (7, 19, 'Patrol route or post (swap every 2 h)', 'SO_PATROL_ROUTE / SO_GUARD_POST'), (19, 20, 'Tavern', 'SO_BAR'), (20, 6, 'Sleep in barracks', 'SO_BED')]),
 ('SCH_GUARD_NIGHT', 'Guard (night shift)', [(18, 19, 'Barracks: eat', 'SO_TABLE'), (19, 7, 'Patrol with lantern; light street lamps 19:30', 'SO_PATROL_ROUTE / SO_LAMP'), (7, 8, 'Tavern', 'SO_BAR'), (8, 18, 'Sleep', 'SO_BED')]),
 ('SCH_SMITH', 'Smith', [(5, 6, 'Wake, eat at home', 'SO_TABLE'), (6, 12, 'Forge work (shop open 7-20)', 'SO_ANVIL / SO_FORGE'), (12, 13, 'Lunch at tavern', 'SO_BAR'), (13, 20, 'Forge / grindstone', 'SO_GRINDSTONE'), (20, 22, 'Tavern', 'SO_CHAIR_TAVERN'), (22, 5, 'Sleep', 'SO_BED')]),
 ('SCH_MERCHANT', 'Merchant / vendor', [(6, 7, 'Eat at home', 'SO_TABLE'), (7, 20, 'Stall or counter (vendor open)', 'SO_COUNTER'), (20, 22, 'Walk to tavern, drink', 'SO_CHAIR_TAVERN'), (22, 6, 'Sleep', 'SO_BED')]),
 ('SCH_INNKEEP', 'Innkeeper', [(6, 2, 'Behind bar; sweep 10:00 and 16:00', 'SO_BAR_BEHIND / SO_BROOM'), (2, 6, 'Sleep upstairs', 'SO_BED')]),
 ('SCH_FARMER', 'Farmer', [(5, 6, 'Eat', 'SO_TABLE'), (6, 12, 'Fields', 'SO_FARM_PLOT'), (12, 13, 'Eat outside', 'SO_BENCH'), (13, 18, 'Fields / feed animals', 'SO_FARM_PLOT / SO_TROUGH'), (18, 21, 'Home, sit by fire', 'SO_HEARTH'), (21, 5, 'Sleep', 'SO_BED')]),
 ('SCH_SALVAGER', 'Salvager / laborer', [(6, 7, 'Eat', 'SO_TABLE'), (7, 17, 'Salvage yard: carry, cut, sort', 'SO_SCRAP_PILE / SO_WORKBENCH'), (17, 23, 'Tavern, dice game', 'SO_DICE_TABLE'), (23, 6, 'Sleep', 'SO_BED')]),
 ('SCH_PRIEST', 'Lantern Church priest', [(5, 6, 'Lantern rite at shrine', 'SO_SHRINE'), (6, 12, 'Read logs, preach 9:00 and 11:00', 'SO_LECTERN'), (12, 13, 'Eat', 'SO_TABLE'), (13, 19, 'Visit sick / graveyard', 'SO_GRAVE / SO_BEDSIDE'), (19, 20, 'Evening rite', 'SO_SHRINE'), (20, 5, 'Sleep', 'SO_BED')]),
 ('SCH_SCHOLAR', 'Choir scholar', [(8, 12, 'Study shard glass', 'SO_DESK'), (12, 13, 'Eat', 'SO_TABLE'), (13, 2, 'Study / listen at Shard focus', 'SO_DESK / SO_SHARD_FOCUS'), (2, 8, 'Sleep', 'SO_BED')]),
 ('SCH_BEGGAR', 'Beggar / drifter', [(7, 20, 'Sit near market; ask passers', 'SO_BEG_SPOT'), (20, 7, 'Sleep on bedroll near hearth or under bridge', 'SO_BEDROLL')]),
 ('SCH_BARD', 'Bard', [(10, 18, 'Wander market, sit', 'SO_BENCH'), (18, 1, 'Perform in tavern (song every 6 game min)', 'SO_STAGE'), (1, 10, 'Sleep at inn', 'SO_BED')]),
 ('SCH_FENCE', 'Fence', [(10, 18, 'Legit cover job', 'SO_COUNTER'), (18, 4, 'Back room (fence trade open)', 'SO_BACKROOM'), (4, 10, 'Sleep', 'SO_BED')]),
 ('SCH_COURIER', 'Traveling vendor / courier', [(0, 24, 'Route between towns, 1 stop per 6 game h (world/npcs.csv routes)', 'SO_ROAD_WAYPOINT / SO_COUNTER')]),
 ('SCH_NOBLE', 'Hold official', [(8, 9, 'Eat', 'SO_TABLE'), (9, 17, 'Audience hall (petitions)', 'SO_THRONE / SO_DESK'), (17, 20, 'Walk gardens', 'SO_BENCH'), (20, 23, 'Dine', 'SO_TABLE'), (23, 8, 'Sleep', 'SO_BED')]),
]
rows = []
for sid, name, blocks in ARCH:
    for i, (a, b, act, so) in enumerate(blocks):
        rows.append([f'{sid}_{i+1:02d}', sid, name, f'{a:02d}:00', f'{b:02d}:00', act, so, 'Shelter SO if raining (WTH rain/storm)' if 'Fields' in act or 'Wander' in act or 'Patrol' in act and 'GUARD' not in sid else 'none'])
T('schedule_blocks.csv', ['block_id', 'schedule_id', 'archetype', 'start', 'end', 'activity', 'smart_object', 'weather_override'], rows)

T('schedule_rules.csv', ['rule_id', 'rule', 'value', 'notes'], [
 ['SR_JITTER', 'Block start jitter', '+/- 0-20 game min per NPC per day (seeded by NPC id)', 'Crowds do not move in lockstep'],
 ['SR_TRAVEL', 'Travel time', 'NPC leaves early so it arrives on time; walk 1.4 m/s, hurry 3.0 m/s if late', ''],
 ['SR_SO_BUSY', 'Smart object taken', 'pick nearest free SO of same type within 30 m; else idle-wander 60 s and retry', ''],
 ['SR_INTERRUPT', 'Interrupt priority', 'Combat > Flee > Crime report > Quest > Player dialogue > Weather > Schedule', ''],
 ['SR_RESUME', 'Resume after interrupt', 'go to block active at current time; skip anything missed', ''],
 ['SR_DIALOGUE', 'Player talks to NPC mid-task', 'NPC finishes animation loop (max 2 s), turns, talks; vendor trade works anywhere during open hours', ''],
 ['SR_CLOSED', 'Shop closed', 'door lock tier 2, trespass volume active; vendor at home trades only at Speech 50', ''],
 ['SR_DEATH', 'Unique NPC killed', 'role filled by a generic replacement after 7 game days (vendors, innkeepers, guards)', 'Quest-givers are Essential until their quests end'],
 ['SR_ESSENTIAL', 'Essential NPCs', 'knocked down at 0 HP for 15 s instead of dying', 'Quest-critical and companions only'],
 ['SR_HOLLOWING', 'Hollowing pressure', 'when a region Shard-bearer is alive past Act 2 midpoint, night population -30%, doors locked at 21:00', 'Ties world state to the story'],
 ['SR_MEMORY', 'NPC memory of the player', 'remembers last 3 notable acts for 3 game days (theft seen, helped, fought nearby) and comments', 'Feeds greeting barks'],
])

T('npc_reactions.csv', ['react_id', 'stimulus', 'radius_m', 'civilian_reaction', 'guard_reaction', 'bark_category', 'cooldown_s'], [
 ['RCT_WEAPON_DRAWN', 'Player weapon drawn in town', 5, 'Step back, nervous idle', 'GRD_WARN after 3 s', 'civ_weapon_out', 30],
 ['RCT_AIM', 'Player aims a firearm at NPC', 15, 'Hands up, cower 3 s; then flee', 'GRD_WARN immediately', 'civ_aimed_at', 20],
 ['RCT_CAST', 'Player casts damaging Weave in town', 15, 'Flinch, move away 6 m', 'GRD_WARN', 'civ_magic', 20],
 ['RCT_BUMP', 'Player runs into NPC', 1, 'Stumble anim, complaint', 'Complaint', 'civ_bump', 10],
 ['RCT_SPRINT', 'Player sprints past within 2 m', 2, 'Glance', '-', 'none', 15],
 ['RCT_COMBAT_NEAR', 'Combat within 30 m', 30, 'Flee indoors (nearest SO_SHELTER)', 'Join if enemy faction', 'civ_panic', 10],
 ['RCT_CORPSE', 'Body found', 20, 'Scream, report to guard', 'GRD_SEARCH', 'civ_body', 30],
 ['RCT_FIRE', 'Building prop burning', 25, 'Flee; 30% chance to carry water bucket (put out in 20 s)', 'Fight fire', 'civ_fire', 20],
 ['RCT_HOLLOW_RAID', 'Town raid event', 60, 'Flee to inn / chapel', 'Combat', 'civ_raid', 0],
 ['RCT_GIFT', 'Player gives Ember/item to beggar', 2, 'Thank, +disposition', '-', 'civ_thanks', 60],
 ['RCT_NAKED', 'Player has no chest armor', 4, 'Comment', 'Comment', 'civ_comment_outfit', 120],
 ['RCT_SHARD_GLOW', 'Player uses a Resonance', 40, 'Awe idle 2 s, then whisper', 'Same', 'civ_awe', 60],
 ['RCT_RAIN', 'Rain or storm starts', 0, 'Walk to shelter SO, hood up', 'Hood up, stays', 'civ_weather', 300],
 ['RCT_NIGHT', '19:30 lamp lighting', 0, 'Lamplighter route', 'Night shift swap', 'none', 0],
 ['RCT_GREET', 'Player within 3 m, NPC Unaware', 3, 'Greeting by faction rank and memory', 'Greeting', 'civ_greet', 45],
])

T('sim_lod.csv', ['lod_id', 'band', 'distance_m', 'npc_update', 'physics', 'schedule', 'notes'], [
 ['SIM_FULL', 'Full', '0-60', 'Every frame; full anim and perception', 'Full collision', 'Live', 'Max per town tier in town_tiers.csv'],
 ['SIM_NEAR', 'Reduced', '60-200', '10 Hz AI, anim URO', 'Capsule only', 'Live', ''],
 ['SIM_FAR', 'Virtual', '200 to stream-out', 'No actor; schedule ticks every 1 game min', 'none', 'Virtual position along route', 'Spawned at virtual position when streamed in, out of view if possible'],
 ['SIM_OFF', 'Unloaded', 'cell unloaded', 'none', 'none', 'Catch-up on load: place every NPC in block for current time', 'Dead NPCs and moved props persist (save rules in tech/03)'],
])

T('town_events.csv', ['event_id', 'event', 'where', 'frequency', 'duration', 'effect', 'notes'], [
 ['TEV_MARKET', 'Market day', 'Towns', 'Every 7th game day', '07:00-18:00', 'Extra 3 stalls, vendor prices -10%, +8 NPCs', ''],
 ['TEV_LANTERN', 'Lantern procession', 'Towns with a chapel', 'Every 7th game day at 20:00', '30 game min', 'Priests walk route; Lantern Church +10 rep if player walks along', 'Rep via RPA side'],
 ['TEV_RAID_HOLLOW', 'Hollowed raid', 'Towns in REG_03+', '10% per game night, not within 3 game days of last', 'Until 12 attackers dead', 'Encounter template spawns at gate; guards fight; reward 2 x region Ember drop + town disposition', 'Off while player is under level band min'],
 ['TEV_RAID_THORN', 'Thorn Clan shakedown', 'Hamlets', '15% per game day', '1 game h', 'Thorns demand tribute; player may pay, persuade or fight', 'Neutral if Salvagers Honored (FAC_THORN rule)'],
 ['TEV_FIRE', 'House fire', 'Towns', 'Only from player/enemy fire', 'Until out', 'Townsfolk bucket chain', ''],
 ['TEV_EXECUTION', 'Public trial', 'Lantern Hold', 'After main quest beats (flag)', '20 game min', 'Story set piece', 'Authored by campaign'],
 ['TEV_FESTIVAL', 'Crashfall festival', 'All towns', 'Live-season event (loops season calendar)', '7 real days', 'Decorations, fireworks, cosmetics', 'Owned by loops/live'],
])

# ---------------------------------------------------------------- physics
T('physics_materials.csv', ['pm_id', 'material', 'density_kg_m3', 'friction', 'restitution', 'flammable', 'conducts_storm', 'footstep_sfx', 'impact_vfx', 'impact_sfx'],
  [[f'PM_{m.upper()}', m, d, f, r, fl, c, f'SFX_FOOT_{m.upper()}', f'VFX_IMPACT_{m.upper()}', f'SFX_IMPACT_{m.upper()}'] for m, d, f, r, fl, c in [
   ('wood', 600, 0.6, 0.30, 'yes', 'no'), ('stone', 2500, 0.7, 0.15, 'no', 'no'), ('metal', 7800, 0.4, 0.25, 'no', 'yes'),
   ('hull', 4500, 0.4, 0.20, 'no', 'yes'), ('glass', 2500, 0.3, 0.10, 'no', 'no'), ('cloth', 300, 0.8, 0.05, 'yes', 'no'),
   ('flesh', 1000, 0.7, 0.05, 'no', 'yes'), ('ice', 900, 0.05, 0.10, 'no', 'no'), ('dirt', 1500, 0.8, 0.05, 'no', 'no'),
   ('water', 1000, 0.1, 0.0, 'no', 'yes'), ('shard', 2600, 0.3, 0.40, 'no', 'yes'), ('foliage', 400, 0.6, 0.10, 'yes', 'no')]])

T('physics_props.csv', ['pc_id', 'class', 'mass_kg', 'examples', 'player_interaction', 'throw_speed_m_s', 'impact_damage', 'npc_reaction', 'persist', 'net_authority'], [
 ['PC_CLUTTER', 'Clutter', '0.1-2', 'Cups, books, bottles, scrap bits', 'Push on contact; pick up and drop (Interact hold 0.3 s)', 8, '0 (stagger-free)', 'Owner complains if knocked off counter', 'Positions saved in towns and sites; reset on cell reset (tech/03)', 'Local cosmetic in co-op'],
 ['PC_SMALL', 'Small prop', '2-15', 'Buckets, chairs, small crates', 'Kick on sprint; carry one-handed (no attacks)', 6, '0.5 x mass x v^2 / 100, max 30, no damage to player', 'Glance', 'Saved', 'Host'],
 ['PC_MEDIUM', 'Medium prop', '15-60', 'Barrels, crates, carts wheels', 'Push only (walk speed 1.2 m/s); explosions and Strike knock it', 0, 'max 80 when knocked into NPC above 6 m/s', 'Stagger on hit', 'Saved', 'Host'],
 ['PC_HEAVY', 'Heavy prop', '60-600', 'Carts, boulders on slopes, beams', 'Not movable by hand; Iron Pull, explosions, vehicles', 0, '0.5 x mass x v^2 / 100, max 400; crush at > 300 kg and > 4 m/s = kill fodder', 'Knockdown', 'Saved', 'Host'],
 ['PC_STATIC', 'Static', 'infinite', 'Buildings, cliffs, Citadel walls', 'None', 0, '-', '-', '-', '-'],
])

T('physics_rules.csv', ['rule_id', 'rule', 'value', 'source', 'notes'], [
 ['PH_FALL_SAFE', 'Fall damage threshold', 'no damage under 6 m', 'SIM choice', 'Roll on landing (Breath 15) halves damage above'],
 ['PH_FALL_DMG', 'Fall damage', '(h - 6) x 6% max HP per m; death at 20 m', 'SIM choice', 'Glide (Strider) cancels; water deeper than 1.5 m cancels'],
 ['PH_KNOCK_THRESH', 'Impulse to stagger / knockdown', 'stagger at 1500 N.s, knockdown at 4000 N.s, ragdoll at 9000 N.s', 'SIM choice', 'Scaled by poise: heavy enemies x2'],
 ['PH_RAGDOLL_TIME', 'Ragdoll get-up', '1.2 s blend after velocity < 0.5 m/s, max 3 s', 'SIM choice', ''],
 ['PH_CORPSE_CAP', 'Corpse limit', '24 ragdoll corpses; oldest out of view fades after 300 s', 'SIM choice', 'Bosses persist until area reload'],
 ['PH_DEBRIS_CAP', 'Debris pieces', 'max 150 active, sleep after 5 s, fade after 30 s out of view', 'SIM choice', 'tech/perf_budgets owns frame cost'],
 ['PH_ACTIVE_BODIES', 'Simulated rigid bodies', 'max 200 awake (PS5/XSX), 300 PC', 'SIM choice', ''],
 ['PH_COOP', 'Physics in co-op', 'gameplay props host-authoritative and replicated; debris and clutter local only', 'SIM choice', 'Destruction state replicated as a bit per DST instance'],
 ['PH_LOW_G', 'The Quiet gravity', '0.38 g on outer ring, 1.0 g inner decks; fall threshold 15 m in 0.38 g', 'plan 3.7 own gravity rules; values SIM choice', 'Thrown props fly 2.6x farther'],
 ['PH_WATER', 'Swimming', 'heavy Equip Load sinks: swim speed -50%, cannot dive', 'SIM choice', 'Firearms cannot fire underwater'],
 ['PH_GRAB', 'Telekinetic grab (Iron Pull Shaping)', 'pull props up to 120 kg within 15 m; launch at 18 m/s', 'SIM choice', 'Links Iron element to physics'],
])

DST = [
 # id, name, pm, hp, kin, weave, explosive, fire, destroyed_by_melee, drops, respawn, repair_cost, owner
 ['DST_CRATE', 'Wooden crate', 'PM_WOOD', 40, 1.0, 1.0, 3.0, 1.5, 'yes', 'ITM_LT_BREAKABLE_REG_* (requested, DR-SIM-07)', 'cell reset', 15],
 ['DST_BARREL', 'Barrel', 'PM_WOOD', 60, 1.0, 1.0, 3.0, 1.5, 'yes', 'ITM_LT_BREAKABLE_REG_* (requested, DR-SIM-07)', 'cell reset', 20],
 ['DST_SHARD_CANISTER', 'Shard canister (explosive)', 'PM_SHARD', 25, 1.0, 1.0, 2.0, 2.0, 'yes', 'Explodes 5 m radius, 180 dmg at band min, element by tint, 0.4 s fuse', 'cell reset', 80],
 ['DST_DOOR_WOOD', 'Wooden door (barred)', 'PM_WOOD', 400, 0.5, 1.0, 4.0, 1.0, 'heavy only', '-', 'never (stays open)', 120],
 ['DST_BARRICADE', 'Thorn barricade', 'PM_WOOD', 600, 0.5, 1.0, 4.0, 2.0, 'yes', '-', 'never', 0],
 ['DST_FENCE', 'Fence section', 'PM_WOOD', 80, 1.0, 1.0, 3.0, 1.5, 'yes', '-', '3 game days', 30],
 ['DST_STALL', 'Market stall', 'PM_CLOTH', 150, 1.0, 1.0, 3.0, 2.0, 'yes', 'scatter goods (owned)', '1 game day', 200],
 ['DST_GLASS', 'Window / glass panel', 'PM_GLASS', 10, 1.0, 1.0, 5.0, 1.0, 'yes', '-', '1 game day', 50],
 ['DST_CHOIRGLASS', 'Choir glass pane', 'PM_SHARD', 300, 0.25, 1.5, 2.0, 0.5, 'yes', 'Shard Dust 1-2', 'never', 0],
 ['DST_HULL_PANEL', 'Weak hull panel (secret)', 'PM_HULL', 800, 0.25, 0.5, 4.0, 0.0, 'heavy only', 'reveals passage', 'never', 0],
 ['DST_ICE_WALL', 'Frost ice wall', 'PM_ICE', 300, 1.0, 1.0, 2.0, 3.0, 'yes', '-', 'never', 0],
 ['DST_ROOTS', 'Bloom root mass', 'PM_FOLIAGE', 250, 0.5, 1.0, 2.0, 4.0, 'yes', '-', 'regrows 1 game day', 0],
 ['DST_HOLLOW_GROWTH', 'Hollowing crust', 'PM_SHARD', 500, 0.5, 1.0, 1.0, 1.0, 'yes', 'Shard Dust 1', 'never (cleansed)', 0],
 ['DST_REMNANT_TURRET', 'Remnant wall turret', 'PM_METAL', 900, 0.5, 1.5, 2.0, 0.5, 'yes', 'Hull Scrap 2-4', 'cell reset', 0],
 ['DST_BRIDGE_ROPE', 'Rope bridge (scripted)', 'PM_WOOD', 200, 0.0, 1.0, 1.0, 3.0, 'no (ropes only)', 'collapses, ragdolls riders', 'never', 0],
 ['DST_PILLAR', 'Cracked pillar (scripted)', 'PM_STONE', 1500, 0.0, 0.5, 1.0, 0.0, 'no', 'falls along authored path, crush 400', 'never', 0],
]
T('destructibles.csv', ['dst_id', 'object', 'pm_id', 'hp', 'mult_kinetic', 'mult_weave', 'mult_explosive', 'mult_fire', 'melee_can_break', 'on_destroy', 'respawn', 'repair_cost_ember', 'states', 'vfx', 'sfx', 'mesh', 'str_id'],
  [d + ['Intact > Damaged (50%) > Destroyed', f'VFX_{d[0]}_BREAK', f'SFX_{d[0]}_BREAK', f'MESH_{d[0]}', S(f'STR_{d[0]}_NAME', d[1], 'Destructible name (inspect)')] for d in DST])

T('element_world.csv', ['ew_id', 'element', 'world_effect', 'radius_m', 'duration_s', 'spread', 'notes'], [
 ['EW_EMBER_GRASS', 'Ember', 'Ignites dry grass and PM_WOOD/PM_CLOTH/PM_FOLIAGE', 1.5, 'grass 8, wood 30', 'Spreads 1 m/s in grass, stops at water, stone or rain', 'Burn status to anyone standing in it (status_effects)'],
 ['EW_EMBER_WATER', 'Ember', 'Fire put out by water, rain, Frost', '-', '-', '-', 'Rain halves burn duration'],
 ['EW_STORM_WATER', 'Storm', 'Electrifies water and wet targets', 6, 3, 'Through connected water body up to 6 m', 'Shock to all in radius incl. caster'],
 ['EW_STORM_METAL', 'Storm', 'Arcs between PM_METAL/PM_HULL props within 4 m', 4, 0.5, 'Chain 3 jumps', ''],
 ['EW_FROST_WATER', 'Frost', 'Freezes water surface into walkable ice', 4, 20, '-', 'Ice friction 0.05: sprint slides'],
 ['EW_FROST_FIRE', 'Frost', 'Extinguishes fire', 4, '-', '-', ''],
 ['EW_BLOOM_ROOT', 'Bloom', 'Grows climbable root mass on soil (DST_ROOTS)', 3, 60, '-', 'Ember on roots spreads Burn (element combos)'],
 ['EW_HOLLOW_LIGHT', 'Hollow', 'Snuffs light sources in radius (stealth aid)', 8, 30, '-', 'Feeds systems light factor'],
 ['EW_IRON_PULL', 'Iron', 'Pulls PM_METAL/PM_HULL props and opens metal shutters', 15, '-', '-', 'See PH_GRAB'],
 ['EW_EXPLOSIVE', 'Kinetic (explosive)', 'Impulse 6000 N.s at centre, linear falloff to radius', 'weapon blast radius', '-', '-', 'Knocks PC_MEDIUM, breaks DST'],
])

# ---------------------------------------------------------------- strings (UI and popups)
S('STR_SIM_BOUNTY_HUD', 'Bounty: {VAR_bounty} Ember', 'HUD under compass when bounty > 0 in current jurisdiction')
S('STR_SIM_CRIME_REPORTED', 'Crime reported: {VAR_crime}', 'Toast 3 s')
S('STR_SIM_WITNESS', 'Witness fleeing', 'Toast while a witness runs to report')
S('STR_SIM_STOLEN', 'Stolen', 'Item tooltip tag')
S('STR_SIM_TAKE_OWNED', 'Steal {VAR_item}', 'Interact prompt for owned item (red)')
S('STR_SIM_PRIVATE', 'Private: {VAR_owner}', 'Door prompt')
S('STR_SIM_GUARD_STOP', 'Stop right there. You have a bounty of {VAR_bounty} Ember.', 'Guard dialogue opener')
S('STR_SIM_OPT_PAY', 'Pay the fine ({VAR_bounty} Ember)', 'Dialogue option')
S('STR_SIM_OPT_JAIL', 'Go to jail ({VAR_hours} hours)', 'Dialogue option')
S('STR_SIM_OPT_PERSUADE', '[Speech {VAR_req}] This is a misunderstanding.', 'Dialogue option')
S('STR_SIM_OPT_BRIBE', '[Speech 40] Maybe {VAR_cost} Ember clears this up?', 'Dialogue option')
S('STR_SIM_OPT_FACTION', '[Hull Knights] I serve the Knight-Commander.', 'Dialogue option')
S('STR_SIM_OPT_RESIST', 'Resist arrest', 'Dialogue option')
S('STR_SIM_SENTENCE', 'Sentence: {VAR_hours} hours. Stolen goods are confiscated. Lose 25% of rank progress in your two highest skills for each day served.', 'Jail popup body')
S('STR_SIM_SKIP_SENTENCE', 'Pay {VAR_cost} Ember to leave now', 'Cell door prompt')
S('STR_SIM_RELEASED', 'Sentence served. Bounty cleared.', 'Toast')
S('STR_SIM_YIELD', 'Yield!', 'Guard shout subtitle')
S('STR_SIM_HUNTED', 'You are hunted in {VAR_jur}', 'Toast on reaching tier HUNTED')
S('STR_SIM_TIER_FINE', 'Wanted', 'Bounty tier')
S('STR_SIM_TIER_ARREST', 'Wanted for arrest', 'Bounty tier')
S('STR_SIM_TIER_HUNTED', 'Hunted', 'Bounty tier')
S('STR_SIM_TIER_OUTLAW', 'Outlaw', 'Bounty tier')
S('STR_SIM_SHOP_CLOSED', 'Closed. Opens at {VAR_time}.', 'Shop door prompt')
S('STR_SIM_WAIT', 'Wait {VAR_hours} hours', 'Wait menu')
S('STR_SIM_WAIT_BLOCKED', 'You cannot wait with guards nearby.', 'Wait menu error')
S('STR_SIM_FALL', 'Too high to fall safely', 'Unused by default; Assist hint near 20 m drops')
S('STR_SIM_BOUNTY_BOARD', 'Bounty Board', 'Interactable name')
import re
T('strings_simulation.csv', ['str_id', 'screen', 'text_en', 'max_chars', 'tokens', 'notes'],
  [[i, 'SIMULATION', en, mc, ';'.join(re.findall(r'\{(VAR_[a-z]+)\}', en)), ctx] for i, en, ctx, mc in STR])
print('strings', len(STR))
