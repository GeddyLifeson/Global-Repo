#!/usr/bin/env python3
"""Shardfall writing: dialogue scene outline, cinematics outline, bark sheet, scene summary.

Re-runnable. Reads at run time:
  design/campaign/dialogue_outline.csv, quests.csv, quest_steps.csv, quest_branches.csv,
  cinematics.csv, endings.csv, vo_budget.csv, companion_approval.csv
  design/writing/place_names.csv
  data/actors/bosses.csv, reputation_tiers.csv, data/items/vendors.csv, data/world/npcs.csv, locations.csv
Writes (design/writing/): dialogue_scenes.csv, cinematics.csv, barks.csv, scene_summary.csv, requests_dialogue.csv
Every row is status=draft (style guide: no generated text ships without a writer pass).
"""
import csv, hashlib, math, os, re, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
CAMP = os.path.join(ROOT, 'design', 'campaign')
WR = os.path.join(ROOT, 'design', 'writing')
DATA = os.path.join(ROOT, 'data')



def _norm_region(rows):   # data/actors/bosses.csv moved to short region codes (R1..R6, RQ); writing keys on REG_xx
    for r in rows:
        v = r.get('Region')
        if v and re.fullmatch(r'R\d', v):
            r['Region'] = 'REG_0' + v[1]
        elif v == 'RQ':
            r['Region'] = 'REG_Q'
    return rows

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_text import BANNED as STYLE_BANNED  # noqa: E402
from canon_names import canon, world_locations

def rd(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8', newline='') as f:
        return _norm_region(list(csv.DictReader(f)))


def h(s):
    return int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16)


def pick(lst, key):
    return lst[h(key) % len(lst)]


def picks(lst, key, k):
    """k distinct items, stable order by hash of key."""
    order = sorted(range(len(lst)), key=lambda i: h(f'{key}|{i}'))
    return [lst[i] for i in order[:k]]


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def mc(s):
    return math.ceil(len(s) * 1.4)


# ---------------------------------------------------------------- inputs
outline = rd(os.path.join(CAMP, 'dialogue_outline.csv'))
quests = {q['qst_id']: q for q in rd(os.path.join(CAMP, 'quests.csv'))}
steps = collections.defaultdict(list)
for s in rd(os.path.join(CAMP, 'quest_steps.csv')):
    steps[s['qst_id']].append(s)
branches = collections.defaultdict(list)
for b in rd(os.path.join(CAMP, 'quest_branches.csv')):
    branches[b['qst_id']].append(b)
camp_cins = rd(os.path.join(CAMP, 'cinematics.csv'))
CIN_FALLBACK = [('CIN_OPEN', 'MQ_P_01', 'The Last Minutes', 4.0), ('CIN_HUB_ARRIVE', 'MQ_A1_03', 'Lantern Hold', 2.5), ('CIN_SECOND_STAR', 'MQ_A1_04', 'The Second Star', 2.5),
                ('CIN_MEM_1', 'MQ_A1_05', 'Memory: The Hail', 1.5), ('CIN_MEM_2', 'MQ_A1_08', 'Memory: A Heading Out', 1.5), ('CIN_ACT1_END', 'MQ_A1_08', 'A Column of Light', 3.0),
                ('CIN_MEM_3', 'MQ_A2_02', 'Memory: Yes', 1.5), ('CIN_MEM_4', 'MQ_A2_03', 'Memory: The Doors', 1.5), ('CIN_MEM_5', 'MQ_A2_04', 'Memory: The Count', 1.5),
                ('CIN_MEM_6', 'MQ_A2_05', 'Memory: The Cut', 1.5), ('CIN_MUTINY', 'MQ_A2_06', 'The Missing Forty Minutes', 6.0), ('CIN_ACT2_END', 'MQ_A2_09', 'Launch', 3.5),
                ('CIN_END_R', 'MQ_END_R', 'Restore the Meridian', 5.0), ('CIN_END_B', 'MQ_END_B', 'Bind the Shards', 5.0), ('CIN_END_T', 'MQ_END_T', 'Take the Quiet', 4.5)]
CIN_FROM_FALLBACK = not camp_cins
if not camp_cins:
    _osp = {re.search(r'(CIN_[A-Z0-9_]+)', o['scene_id']).group(1): o.get('speakers', '') for o in outline if 'CIN_' in o['scene_id']}
    camp_cins = [{'cin_id': a, 'qst_id': b, 'title': c, 'minutes': str(d), 'shots': '', 'speakers': _osp.get(a, ''), 'summary': ''} for a, b, c, d in CIN_FALLBACK]
endings = rd(os.path.join(CAMP, 'endings.csv'))
vo_budget = rd(os.path.join(CAMP, 'vo_budget.csv'))
approval = rd(os.path.join(CAMP, 'companion_approval.csv'))
places = {r['loc_id']: r['text_en'] for r in rd(os.path.join(WR, 'place_names.csv'))}
bosses = rd(os.path.join(DATA, 'actors', 'bosses.csv'))
tiers = rd(os.path.join(DATA, 'actors', 'reputation_tiers.csv'))
vendor_rows = rd(os.path.join(DATA, 'items', 'vendors.csv'))
npcs = {r['act_id']: r for r in rd(os.path.join(DATA, 'world', 'npcs.csv'))}
locs = world_locations()   # design/world/locations.csv is canon
WN = {l['loc_id']: l['name'] for l in locs}

REGION = {'REG_01': 'Cinderreach', 'REG_02': 'Saltmere', 'REG_03': 'Thornwood', 'REG_04': 'Glasswaste',
          'REG_05': 'Rimefall', 'REG_06': 'Hollowdeep', 'REG_U': 'the Undervault', 'REG_Q': 'the Quiet',
          'REG_HUB': 'Lantern Hold'}
ELEMENT = {'REG_01': 'Ember', 'REG_02': 'Storm', 'REG_03': 'Bloom', 'REG_04': 'Iron', 'REG_05': 'Frost', 'REG_06': 'Hollow'}
SAYING = {'REG_01': 'Smoke on the ridge, bring the children in.', 'REG_02': 'Tide takes, tide gives back, never the same thing.',
          'REG_03': 'Root deep or blow away.', 'REG_04': 'Water is a promise.', 'REG_05': 'Wait for the thaw.',
          'REG_06': 'Say your name every morning.', 'REG_HUB': 'The Hold holds.'}
TOWN_FALLBACK = {'LOC_TOWN_REG_01_01': 'Emberwatch', 'LOC_TOWN_REG_01_02': 'Cinder Hollow', 'LOC_TOWN_REG_01_03': 'Wreckers\' Rest',
                 'LOC_TOWN_REG_02_01': 'Stiltmarket', 'LOC_TOWN_REG_02_02': 'Brinehook', 'LOC_TOWN_REG_02_03': 'Low Tide Chapel',
                 'LOC_TOWN_REG_03_01': 'Redbark Lodge', 'LOC_TOWN_REG_03_02': 'Thicket Steading', 'LOC_TOWN_REG_04_01': 'Glassmouth Caravanserai',
                 'LOC_TOWN_REG_04_02': 'Choirtower Hamlet', 'LOC_TOWN_REG_05_01': 'Rimehold', 'LOC_TOWN_REG_05_02': 'Lampwick',
                 'LOC_TOWN_REG_05_03': 'Frostgate Hamlet', 'LOC_TOWN_REG_06_01': 'Last Light', 'LOC_TOWN_REG_06_02': 'Driftanchor',
                 'LOC_LANTERN_HOLD': 'Lantern Hold'}
for k, v in TOWN_FALLBACK.items():
    places.setdefault(k, v)

NAMES = {
    'PLAYER': 'the Kindled', 'ACT_NPC_OSTRA': 'Ostra', 'ACT_NPC_WARDEN_TOMAS': 'Old Tomas', 'ACT_NPC_REEVE_ANNIK': 'Reeve Annik',
    'ACT_NPC_HARBOR_MOSS': 'Harbormaster Moss', 'ACT_NPC_THORNKING_GRAL': 'Thorn King Gral', 'ACT_NPC_MIRAGE_SABA': 'Saba',
    'ACT_NPC_HEARTH_ELDER_YURI': 'Elder Yuri', 'ACT_NPC_LASTLIGHT_BEA': 'Bea Crane', 'ACT_NPC_COUNCIL_CLERK': 'Clerk Imre',
    'ACT_NPC_IRES': 'Captain Ires', 'ACT_NPC_HULLKNIGHT_COMMANDER': 'Iselde Marr', 'ACT_NPC_LANTERN_ARCHIVIST': 'Archivist Hale',
    'ACT_NPC_SALVAGER_BOSS': 'Petra Quell', 'ACT_NPC_QUIETHAND_SPEAKER': 'the Speaker', 'ACT_NPC_CHOIR_PRECENTOR': 'Precentor Lisk',
    'ACT_CMP_C1': 'Kessa', 'ACT_CMP_C2': 'Odo', 'ACT_CMP_C3': 'Tamsin', 'ACT_CMP_C4': 'Vey', 'ACT_CMP_C5': 'Hal',
    'ACT_CMP_C6': 'Calla', 'ACT_CMP_C7': 'Dren', 'ACT_CMP_C8': 'Unit 9', 'ACT_BOSS_HUSH': 'Hush', 'ACT_NPC_ECHO': 'the Echo',
    'COMPANION_ACTIVE': 'the active companion', 'ACT_NPC_MERIDIAN_CREW': 'Meridian crew', 'ACT_NPC_TITLE_CARD': 'title card',
}
for b in bosses:
    NAMES.setdefault(b['ACT_ID'], b['Boss'].split(',')[0])


def name_of(aid):
    if aid in NAMES:
        return NAMES[aid]
    if aid in npcs:
        return npcs[aid]['name']
    t = aid.replace('ACT_NPC_', '').replace('ACT_', '').split('_')
    if len(t) == 1:
        return cap(t[0].lower())
    desc = ' '.join(x.lower() for x in t[:-1])
    c = canon(desc.title())   # old town names in IDs (ACT_NPC_GREYFOLD_...) read as world names
    return f"{cap(t[-1].lower())} ({c if c != desc.title() else desc})"


VOICE = {
    'ACT_NPC_OSTRA': 'Ostra voice by stage (style guide 3)', 'ACT_BOSS_HUSH': 'Hush: always "we", polite, never lies',
    'ACT_NPC_IRES': 'Ires: formal, ranks, promises as physical things', 'ACT_NPC_HULLKNIGHT_COMMANDER': 'Knight clipped duty words',
    'ACT_NPC_LANTERN_ARCHIVIST': 'Church warmth, Log citations, "Logged."', 'ACT_NPC_SALVAGER_BOSS': 'Guild: fast, prices in every line',
    'ACT_NPC_QUIETHAND_SPEAKER': 'Hand: few words, second person, weather-report contracts', 'ACT_NPC_CHOIR_PRECENTOR': 'Choir: tone, pitch, rest',
}

# Ostra stage by main quest order
MQ_ORDER = ['MQ_P_01', 'MQ_P_02', 'MQ_RT_01', 'MQ_A1_01', 'MQ_A1_02', 'MQ_A1_03', 'MQ_A1_04', 'MQ_A1_05C', 'MQ_A1_05',
            'MQ_RT_02', 'MQ_A1_06', 'MQ_A1_07', 'MQ_A1_08', 'MQ_A2_01', 'MQ_RT_03', 'MQ_A2_02C', 'MQ_A2_02', 'MQ_RT_04',
            'MQ_A2_03C', 'MQ_A2_03', 'MQ_RT_05', 'MQ_A2_04C', 'MQ_A2_04', 'MQ_RT_06', 'MQ_A2_05C', 'MQ_A2_05', 'MQ_A2_06',
            'MQ_A2_07', 'MQ_A2_08', 'MQ_A2_09', 'MQ_A3_01', 'MQ_A3_02', 'MQ_RT_Q', 'MQ_A3_03', 'MQ_A3_04', 'MQ_A3_05',
            'MQ_A3_06', 'MQ_END_R', 'MQ_END_B', 'MQ_END_T']


def stage_of(qid, act='', region=''):
    if qid in MQ_ORDER:
        i = MQ_ORDER.index(qid)
        if i <= MQ_ORDER.index('MQ_A1_05C'):
            return 1
        if i <= MQ_ORDER.index('MQ_A2_05'):
            return 2
        if i <= MQ_ORDER.index('MQ_A2_09'):
            return 3
        return 4
    act = str(act)
    if act in ('3', 'END', 'post') or region == 'REG_Q':
        return 4
    if act == '2':
        return 2
    if act in ('P',):
        return 1
    if act == '1':
        return 1 if region in ('REG_01', 'REG_HUB', '') else 2
    return 2


def act_of_region(reg):
    return {'REG_01': '1', 'REG_02': '1', 'REG_HUB': '1', 'REG_Q': '3'}.get(reg, '2')


# ---------------------------------------------------------------- Ostra lines for live reactions
OSTRA_LIVE = {
    1: ['Noted. Filing it under Meridian, mine.', 'Correction: that bolt pattern is Engineering. I would know.',
        'Unknown. I dislike unknown.', 'Logged. Proceed. Correction: proceed carefully.', 'Irrelevant. Correction: mildly relevant.',
        'That is ship plate. Deck four, probably. I am rarely wrong.', 'I do not forget. I misfile.', 'Status: you are bleeding. Minor. Continue.'],
    2: ['I think I knew this place. I think I liked it.', 'Do you trust them? I am asking. I do not usually ask.',
        'That is mine. I think it is mine.', 'I was going to say something. It went.', 'Ask them the year. Please. I want to check something.',
        'I think that was a joke. Was it a joke?', 'I keep a list of things that do not fit. It is longer today.', 'Say that again. Slower. I am recording.'],
    3: ['They would be right to hate me.', 'Do not make me say the number again.', 'I had a reason. I do not like it any more.',
        'Say something. Anything that is not about me.', 'I used to log everything. Now I would rather not.', 'They are kind to you. Be kind back. I could not.'],
    4: ['Whatever they choose, let them choose it.', 'I will remember this for them, if they want it remembered.',
        'You decide. I will hold the line.', 'I used to think kindness was inefficient. I was wrong about that too.',
        'Look at them. Four thousand became this many. Good.', 'I am listening. I am better at it now.'],
}
OSTRA_WRONG = ['The core failed. Reactor fatigue. I logged it.', 'Nobody opened anything. I would have logged it.',
               'The captain followed protocol. I watched her do it.', 'There was no hail. I would remember a hail.',
               'Hull failure at entry. Nobody is to blame. I checked.']
FALL_WORDS = re.compile(r'\b(Fall|core|crash|captain|Ires|hail|pods?|log page|forty minutes|bridge|mutiny)\b', re.I)

OPENERS = ['At {place}, {a} opens the scene.', '{place}. {a} has been waiting for the player.', '{a} waves the player over at {place}.',
           'Open on {a}, mid-task, at {place}.', '{a} stops the player near {place}.', '{place}, late in the day. {a} speaks first.',
           '{a} talks while working at {place}.', '{a} meets the player at {place}, arms folded.', 'Rain or dust at {place}; {a} does not seem to notice.',
           '{a} is arguing with someone at {place} and breaks off.', '{place}: {a} is eating and does not stop.', '{a} at {place}, counting something under their breath.',
           'The player finds {a} at {place}.', '{a} calls out from across {place}.', 'Quiet at {place} until {a} clears their throat.',
           '{a} is already talking when the player reaches {place}.', 'At {place}, {a} hands the player something before saying hello.',
           '{a} waits at {place} with a lamp, though it is not dark yet.', '{place}. {a} looks up from a ledger.', '{a} sits on a crate at {place}.']
DETAIL = ['We learn: {s}', 'Backstory, told by {a}: {s}', '{b} fills in the rest: {s}', 'The detail that has to land: {s}', 'Said plainly: {s}',
          '{a} lets it slip: {s}', 'What the player can piece together: {s}', 'Context, kept short: {s}', '{a} admits it: {s}',
          'The part nobody wants to say: {s}', 'In {a}\'s own words: {s}', 'Underneath it: {s}']
OSTRA_BEAT = ['Ostra, heard only by the player: "{l}"', 'Ostra cuts in: "{l}"', 'Ostra, live: "{l}"', 'A second later, Ostra: "{l}"',
              'Ostra, quietly: "{l}"', 'Ostra comments over the top: "{l}"', 'Inside the player\'s chest, Ostra: "{l}"']
IRONY = ['Dramatic irony: Ostra is wrong here, and the player may already know it: "{l}"',
         'Ostra, confident and wrong (counts toward CNT_OSTRA_CONTRADICTIONS if the player has a source): "{l}"',
         'Ostra answers too fast: "{l}"']
TURN = ['Turn: {s}', 'The turn: {s}', 'Reversal: {s}', 'What changes: {s}', 'The sting: {s}', 'Then: {s}']
COST = ['Cost of the choice: {s}', 'Choice lands: {s}', 'Consequence shown on screen: {s}', 'Outcome by branch: {s}']
CLOSE = ['Exit: {s}', 'Scene ends on the next objective: {s}', 'Leads to: {s}', 'Out: {s}', 'Handoff: {s}']
JOURNAL_CLOSE = ['Close on the journal line: "{s}"', 'Last image matches the journal: "{s}"', 'Final beat, journal: "{s}"']
COMP_REACT = ['{c} reacts in their own way; approval shifts if the player sides against them.', '{c} says one line the player will remember later.',
              '{c} stays quiet, which is unlike them.', '{c} makes a small joke that does not land, on purpose.']


def sentences(text):
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"])', (text or '').strip())
    return [p.strip() for p in parts if len(p.strip()) > 8]


def place_of(loc):
    if not loc:
        return 'the scene location'
    if loc in places:
        return places[loc]
    m = re.match(r'LOC_(?:CQ|SITE)_(REG_(?:0\d|U|Q|HUB))_(.+)', loc)
    if m:
        nm = WN.get(loc, '') if loc.startswith('LOC_CQ_') else ''
        nm = nm or canon(m.group(2).replace('_', ' ').title())
        return f"{nm}, {REGION.get(m.group(1), '')}".replace("'S ", "'s ")
    m = re.match(r'LOC_CQ_HUB_(.+)', loc)
    if m:
        return f"{m.group(1).replace('_', ' ').title()}, Lantern Hold"
    return loc.replace('LOC_CQ_', '').replace('LOC_', '').replace('_', ' ').title()


def endp(s):
    s = s.strip()
    return s if s[-1:] in '.!?"' else s + '.'


# ---------------------------------------------------------------- hand beats for key main-path scenes (keyed by campaign scene id)
# Each value: beats separated by " / " (numbered by the script), optional choices, flags, notes.
HB = {
 'DLG_MQ_P_01_S1': ('Old Tomas cracks the Bay 9 pod with a crowbar and swears at the frost / He says he has pulled eleven sleepers out of this ward and none of them talked; the player talks / The cryo scanner sweeps the player and reads out an Origin (creation screen rides on the scan) / Tomas: "Name and trade. That is all anyone gets to keep." / Turn: the player\'s hands still remember inputs on a panel; Tomas sees them twitch and says nothing / Tomas gives the player his spare boots, a size too big', 'Plain/Kind/Hard/Sly first line to Tomas (sets the voice sample; no flag)', '', ''),
 'DLG_MQ_P_01_S4': ('Tomas walks the nameplates on the dead pods, one hand on each / He is looking for his grandmother, Bay 9, row two; the plate is blank / He laughs once: "She always said she would be late." / Ostra, to the player only: "Bay 9, row two. Pod failed at entry. I have her name." / Turn: the player can tell Tomas the name Ostra gives, or not / Tomas pockets a frost lily from beside the pod', 'Kind: tell Tomas the name (FLG_TOMAS_NAME_TOLD, design choice) / Plain: say nothing / Sly: "She left in a hurry."', 'FLG_TOMAS_NAME_TOLD', 'Flag is a Shardfall design choice; read by DLG_MQ_A3_04_S4 (Tomas copy).'),
 'DLG_MQ_P_02_S1': ('Climbing the broken spine, Tomas explains Anchors as "beds that remember you" / Ember tutorial: he burns a bead to light the first Anchor / Tomas: a Kindled who dies wakes here, carrying nothing but debts / Ostra corrects him: "Escape-pod beacon. Model Seven." Tomas cannot hear her and keeps going / Turn: Tomas asks if the player hears the Shard sing; he has heard Kindled go mad that way / The player can lie', 'Plain/Kind/Hard/Sly; Sly: "Only on Tuesdays."', '', ''),
 'DLG_MQ_P_02_S3': ('The Hollowed officer falls; his rank pip reads Deck Officer, Bay 4 / The chest Shard flares hot / Ostra: "That Shard is mine." Then four seconds of nothing / Player: "Ostra?" / Ostra: "Noted. Later." Her HUD hints come back slightly dimmer / Turn: the officer\'s last words (Hush, "There you are. We\'ve been counting.") are still on the subtitle log; Ostra refuses to discuss them', '', '', 'Pairs with the story-pass boss_death scene for the officer.'),
 'DLG_MQ_P_02_S4': ('Tomas stops at the lower Spinegate door and takes off his coat / It was his son\'s; his son went to the Hold and did not come back / "Fits you better than it fit him. He was all elbows." / The door reads the chest Shard and opens on Cinderreach smoke / Turn: Tomas will not come; he is an Anchor keeper and the Spinegate needs one / Ostra logs the coat as "Item: borrowed."', 'Kind: promise to look for his son (FLG_TOMAS_SON, design choice) / Plain: thank him / Hard: "I don\'t need a coat."', 'FLG_TOMAS_SON', 'Design choice flag; feeds a Lantern Hold side-quest hook if the campaign wants it.'),
 'DLG_MQ_A1_01_S1': ('Reeve Annik counts water buckets at the Kiln well and does not stop counting while she talks / Vael\'s Pyre-Wardens are burning Low Kiln "to keep the Shards warm" / She needs one thing saved: the people in the square or the Anchor on the hill / Ostra wants the Anchor, plainly: "Beacon. Mine. Useful." / Turn: Annik\'s sister is in the square; she does not say so until the player is already walking / Tomas stays to guard the well', 'Save the people (FLG_KILN_PEOPLE; Kessa +10 later) / Save the Anchor (FLG_KILN_ANCHOR; early fast travel; Kessa -10 later)', 'FLG_KILN_PEOPLE; FLG_KILN_ANCHOR', ''),
 'DLG_MQ_A1_01_S4': ('Annik counts survivors at the gate out loud / People saved: a girl walks in carrying a goat bigger than she is and refuses to put it down / Anchor saved: Annik thanks the player once and turns her back / Ostra (people): "Forty. Correction: forty-one. The goat." / Turn: Annik\'s sister is either in the count or not; Annik reacts by branch / Annik mentions a Knight hiding in the cold kilns', '', '', 'Reads FLG_KILN_PEOPLE / FLG_KILN_ANCHOR.'),
 'DLG_MQ_A1_02_S1': ('A knife from inside a cold kiln: Kessa Vane, Hull Knight plate, no squad / She asks the player\'s post; the player has none, which she finds worse than an enemy / She would not burn Emberlow for Vael, so she walked / Ostra: "That badge is my security detail\'s. She wears it upside down." / Turn: Kessa wears it upside down on purpose; it is the deserter\'s mark / Squad horns on the ridge', 'Plain/Kind/Hard/Sly (Kind +5 Kessa, Hard -5)', '', ''),
 'DLG_MQ_A1_02_S2': ('Sergeant Dunne and three Knights at the kiln yard gate / Dunne calls Kessa by her post, never her name / He reads her sentence: airlocked, meaning exile, meaning they kill her if she comes back / The player talks or fights / Turn, talked down: Dunne admits he burned Emberlow himself after she left and has not slept since / Fight: Dunne yields at low health and asks Kessa to finish it; she will not', 'Talk down: SKL_SPEECH 25 or FAC_HULLKNIGHTS Friendly (FLG_KESSA_SQUAD_SPARED) / Fight', 'FLG_KESSA_SQUAD_SPARED', 'Spared: Dunne returns in QST_HK_06.'),
 'DLG_MQ_A1_03_S1': ('Clerk Imre seats the player below the empty Speaker\'s chair and its black candle / Marr wants the gates shut; Hale wants the Log read; Quell wants salvage rights; Lisk talks about a second star / They argue about the Hollowing until Imre rings a ship bell older than all of them / Ostra, under the noise: "This was my bridge. That console is navigation. Someone has put a vase on it." / Turn: the black candle gutters when Lisk says "the star is listening"; nobody comments / Each leader turns to the player at once', 'Ask each leader one question (tone choices)', '', ''),
 'DLG_MQ_A1_04_S1': ('Lisk leads the player up the Choir Spire, out of breath, delighted / He explains the Choir has watched a second star since 702 AF and kept it secret / "It is learning our names. I find that beautiful." / Ostra goes quiet in the middle of a correction / Turn: Lisk asks the player whether the Shard in their chest ever hums along; he is not asking idly / He opens the lens shutter', 'Plain: What is it? / Kind: Thank you for trusting me. / Hard: Who else knows? / Sly: Does it pay?', '', ''),
 'DLG_MQ_A1_04_S3': ('Hale gives the player a log page in a cloth sleeve, hands shaking / Two timestamps, forty minutes apart, nothing between / Hale: "The Church reads this page every Fall Day. Nobody reads the numbers." / Ostra: "That page is mine. It is complete. Correction: it is incomplete. Unknown why." / Turn: Hale asks the player to take it away from the Chapel, because he is afraid of what he will do with it / He names Brother Odo, who found a second copy', '', 'CNT_OSTRA_CONTRADICTIONS +1', 'Contradiction source 1 of several.'),
 'DLG_MQ_A1_05_S2': ('Vael stands in the Pyre-Court, which was the engine crew mess hall; the tables are still bolted down / Tic: "Keep it warm. Keep it covered. The sky looks for cold Shards." / Vael believes fire hides the Shards; he is burning his own villages to do it / Ostra: "Engineer. Chief rank. I know that walk." / Turn: Vael recognizes the chest Shard and is afraid of the player, not angry / He lights the court', '', '', ''),
 'DLG_MQ_A1_05_S3': ('Vael on his knees; the fire around him goes out on its own / The tic drops; he speaks as an engineer, exact: "Coolant was nominal. Pressure was nominal. The core didn\'t fail. Somebody opened it." / Ostra, at once: "Incorrect. Reactor fatigue. I logged it." / Vael hears something the player does not and laughs, tired: "She would say that." / Turn: he asks the player who they carry; if the player says Ostra, he goes white / Lucid moment ends; Heart Shard choice follows', '', 'CNT_LUCID_HEARD +1; CNT_OSTRA_CONTRADICTIONS +1', 'Lucid line 1. Ostra reaction set: see SCN_OSTRA lucid sets.'),
 'DLG_MQ_A1_05_S4': ('Annik hears Vael is dead and sits down on the well step / She has hated him for a year and he was the one who built the well pump / Spared: Vael\'s last message reaches her, an apology with a pump diagram on the back / Taken: there is no message, only grey ash on the wind from the Pyre-Court / Turn: Annik asks the player to keep the pump diagram, because she cannot look at it / Emberwatch goes back to work', '', '', 'Reads FLG_HEART_1_SPARED / TAKEN.'),
 'DLG_MQ_A1_06_S3': ('Hal Merrow hides in a Choir vault with wax in his ears / He hears Ostra; he is the first person in the world to do so / Hal: "There is a woman in your chest and she is very rude." / Ostra: "Correction: precise." / Turn: Hal panics because the song also talks to him, and he cannot tell the two voices apart yet / He asks the player to take him somewhere loud', '', '', 'Ostra becomes audible to a second character for the first time.'),
 'DLG_MQ_A1_07_S3': ('The Cantor\'s hymn fills the drowned nave; it is Hush\'s song in full / Hal drops to his knees and speaks in a voice that is not his: "We are so glad she brought you." / Hush, through Hal, uses Ostra\'s ship designation / Ostra: "Stop that. Hal. Stop." / Turn: Hal comes back and remembers every word; he asks who "she" is / Companion steadies him if present', '', '', 'Hush line must be true: Ostra did bring the player.'),
 'DLG_MQ_A1_08_S2': ('Corsa on the flooded deck of the Beached Ark, giving bearings to a fleet that sank 340 years ago / She stops mid-order and listens to the player\'s chest / Corsa: "Ostra? You\'re in there?" It is the first time anyone in the world speaks to Ostra / Ostra: "Navigator. Corsa. I know you." / Lucid, quiet, as a navigator: "We had a heading out. She turned us down." / Turn: the player cannot tell whether "she" is the captain or Ostra; Ostra says "the captain" too quickly / Corsa dies looking at the sky', '', 'CNT_LUCID_HEARD +1; CNT_OSTRA_CONTRADICTIONS +1', 'Story pass H. Lucid line 2.'),
 'DLG_MQ_A1_08_S3': ('Moss salutes Corsa\'s body from the Stiltmarket wall, ex-navy habit / Stiltmarket counts what the sea gave back after the column: six boats, one bell, no fish / Moss: "She shelled us for twenty years and I am sad. Write that down." / Ostra says nothing; her hints stay off for a minute / Turn: Moss shows the player a lamplight on the cliff that nobody in Stiltmarket owns / The player heads back to Lantern Hold', '', '', 'Plants the lamplighter seen in CIN_ACT1_END.'),
 'DLG_MQ_A2_01_S1': ('Imre lays six stones on the Council table, two of them dark for the Hearts already met / Marr: only a Kindled survives a Shard-bearer, and the Hold has one / Hale votes yes and looks at the floor; Quell votes yes and names a price; Lisk votes yes and smiles / The Speaker\'s candle gutters; Imre records it as a yes / Ostra: "Four hearts. They are not hearts. They are fuel cells." / Turn: nobody asks the player; the vote is about them', '', '', ''),
 'DLG_MQ_A2_02_S1': ('Thorn King\'s Moot: Gral on a stump throne, clan banners nailed to living trees / Dren hangs in a cage at the Moot gate, eating an apple someone threw at him / Gral offers passage for a duel, a bribe, or Dren\'s word, which is worth nothing here / Turn: Dren\'s word is worth nothing because he refused a blood feud; Gral is his uncle / The player picks a way through', 'Duel / Bribe / Vouch for Dren (FAC_THORN rep; Dren approval per branch)', '', 'Choices from campaign branches if present.'),
 'DLG_MQ_A2_02_S3': ('Sorrel is her forest; she speaks as "the grove" and pauses as if listening / Hush, last phase, through her: "Her trees grow for us. All of them do." / Defeated, a single sapling turns toward the player / Lucid: "Sorrel. My name is Sorrel. The captain said yes. I heard her say yes." / Ostra: "Then she said yes. I locked nothing. I think I locked nothing." / Turn: Sorrel asks if her bay crew got out; Ostra has the number and does not say it', '', 'CNT_LUCID_HEARD +1', 'Lucid line 3.'),
 'DLG_MQ_A2_03_S2': ('Unit 9 boots in the Last Hangar, apologizes to the door, then addresses Ostra by ship designation / Ostra is moved and hides it under status words / Unit 9: "Standing orders unchanged for nine hundred years. Awaiting update." / Turn: Unit 9 asks Ostra why her last order was "seal the bridge" / Ostra: "Unknown." It is the first lie she knows she tells / The player can let it pass', '', 'CNT_OSTRA_CONTRADICTIONS +1', ''),
 'DLG_MQ_A2_03_S3': ('Brannoch kneels among broken drones, counting them: "Forty. Forty-one. My oath." / Hush, last phase, through him: "He built this army for the sky. We are the sky." / The tic drops / Lucid: "My oath was to Ires. It still is. I would still open the door for her." / Ostra: "The doors were sealed. By security. By someone." / Turn: Brannoch asks the player to tell Iselde Marr; a Knight runner is already listening', '', 'CNT_LUCID_HEARD +1', 'Lucid line 4. Feeds DLG_MQ_A2_03_S5.'),
 'DLG_MQ_A2_03_S5': ('A Knight runner reaches Marr at the Knights\' Gate with Brannoch\'s words / Marr reads the founding oath aloud: it names Captain Ires, not the ship / "Nine hundred years we have been sworn to a woman nobody has seen." / Turn: Marr asks the player if Ires is alive; the player does not know yet, and Ostra does not answer / Marr orders the oath copied, then crosses out her own name on the copy', '', '', 'Sets up QST_HK_09.'),
 'DLG_MQ_A2_04_S3': ('Mother Rime by the Still Lake: "Shh. Later. You\'ll be fine later." / Hush, last phase, through her: "She kept them cold for later. We are later." / Lucid, flat, medical: "Thirty-seven thousand pods. I counted them all." / Ostra: "Thirty-seven thousand and twelve. I counted too." / Turn: Ostra realizes she knows the number exactly and should not / Rime asks if the pods by the lake were thawed', '', 'CNT_LUCID_HEARD +1', 'Lucid line 5.'),
 'DLG_MQ_A2_04_S4': ('Yuri walks the thawed pods or the frozen ones, by flag / Thawed: his wife Vera opens her eyes, does not know him, then asks if the goats were fed; she knows the goats / Frozen: Yuri sits by her pod and tells her about the weather / Ostra (thawed): "Patched. She is patched." / Turn: Yuri asks the player whether he should wake her at all, now that she is a stranger / Rimehold\'s first fire in a year', '', '', 'Reads FLG_RIME_THAWED.'),
 'DLG_MQ_A2_05_S3': ('The Hollow Twins finish each other\'s sentences, wrongly / Hush, last phase, through both: "We spoke to them before we spoke to her." / The two bodies fall at the same moment / Lucid, one voice, correctly: "We heard the hail. We heard what it offered." / Ostra: "Stop. I am checking my logs. My logs agree with me." / Turn: Ada asks Ennis whether they told anyone; Ennis says the bridge cut the line', '', 'CNT_LUCID_HEARD +1', 'Lucid line 6.'),
 'DLG_MQ_A2_06_S1': ('Odo unrolls his map of the Undervault on a crate, weighed down with his pencil stub / He hopes the forty minutes are a copying error and says so twice / Ostra, proud: "My engine block. You will like it. It is very large." / Turn: Odo asks Ostra a question through the player, the first time he has addressed her / She answers him kindly, which frightens the player more', '', '', ''),
 'DLG_MQ_A2_06_S3': ('The memory Shard goes dark in the player\'s hand / Ostra: "I had the numbers. I always have the numbers. I just did not keep them." / The HUD loses her hints one by one / Turn: the player understands the ship-system prompts from the opening were her, and their own hands obeyed / Silence begins; MQ_A2_07 starts without her', '', 'FLG_OSTRA_SILENT', 'Stage 3 starts here.'),
 'DLG_MQ_A2_06_S4': ('Odo, if present, sits on the core housing step / "The dead deserve the truth. The living deserve it more, and like it less." / He offers to write it down so the player does not have to carry it / Turn: he asks whether the player knew; if CNT_OSTRA_CONTRADICTIONS >= 3, the player can say yes / Odo +10 if the player is honest either way', 'Plain/Kind/Hard/Sly; honest answer Odo +10', '', ''),
 'DLG_MQ_A2_07_S1': ('Lantern Hold without Ostra: no hints, no map updates, only crowd noise / Market calls, a child crying, a Knight drilling recruits / The player keeps hearing a pause where a correction would be / Turn: someone says "the long sleep" and nobody explains it / Compass marker stays frozen for the whole quest (UI note)', '', '', 'Story pass H: the absence is mechanical.'),
 'DLG_MQ_A2_07_S3': ('The full Council, and the empty chair / Imre asks for the report; the player tells the truth or a lie / Truth: Hale stands, Marr sits down hard, Quell laughs once and stops, Lisk looks almost relieved / Lie: everybody believes it except Hale / Turn: the player has to speak for Ostra without her; Ostra is silent and cannot help / Imre writes the result on the board in chalk, which can be wiped', 'Truth (FLG_TRUTH_TOLD; Odo +15, Kessa +10; Church -100, Knights -50) / Hide (FLG_TRUTH_HIDDEN; Odo -20; Church +50)', 'FLG_TRUTH_TOLD; FLG_TRUTH_HIDDEN', ''),
 'DLG_MQ_A2_07_S4': ('Hale in the Log Chapel after hours / He has known for years that the forty minutes were cut; the Archivists hid it for six hundred / "I read the page aloud every Fall Day and skipped the numbers." / Turn: Hale knew someone opened the core and chose God over the numbers / He asks the player to read the next Fall Day page in his place', '', '', ''),
 'DLG_MQ_A2_07_S5': ('Night, at an Anchor; the chest Shard warms without warning / Ostra: "You should have left me in the dark." / She speaks in short pieces; she has been listening the whole time / Turn: she heard what the player told the Council and thanks them for it, whatever it was / The player can forgive her; she does not accept it, but logs it', 'Tell Ostra she is forgiven (FLG_OSTRA_FORGIVEN) / Plain: "Welcome back." / Hard: "Earn it."', 'FLG_OSTRA_FORGIVEN', 'Bind route requirement.'),
 'DLG_MQ_A2_08_S1': ('The Speaker in the Still Room, behind a filtered mask, with the Lamplighter\'s ledgers / The Speaker hears Ostra, says so, and calls her "the old voice" / Ledgers show Shards shipped to a lamp tower, weighed like grain / Turn: the Speaker has been taking orders from an Ostra backup routine for years and only now hears the original / "You will go to the tower at dusk. She will not fight."', '', '', ''),
 'DLG_MQ_A2_08_S2': ('Ires in the lamp tower, making tea for two, unmasked / She knows who the player carries and is not surprised / The hail, the terms, why she said yes: Hush promised to set the sleepers down / Turn: she believed it then, and she still half believes it / She asks after the Knights by post', 'Plain/Kind/Hard/Sly throughout; Speech checks open her reasons', '', 'Part 1 of 3 (180 lines total).'),
 'DLG_MQ_A2_08_S3': ('Ostra speaks to Ires through the player; Ires hears her (Kindled, Shard-touched) / "Hello, Captain." "Hello, ship." Nine hundred years in two lines / They argue about the numbers; Ostra was right about the trade and wrong about the cost / Turn: Ires thanks Ostra for the four thousand who lived, then asks her to admit the thirty-seven thousand / Ostra admits it out loud for the first time', '', '', 'Part 2 of 3.'),
 'DLG_MQ_A2_08_S4': ('Ires calls it a debt: she feeds Shards to the sky so Hush will spare what is left / The player can attack, release her, or offer a way out / Attack: she does not draw; she breaks a Shard and rises up the Weave / Release: she bows to Ostra and walks out into the grey / Offer: she stops feeding the tower and says she will think on it / Turn: whatever the choice, Ires tells the player "It wants you more than it wants me."', 'Attack (FLG_IRES_ATTACKED) / Let her go (FLG_IRES_RELEASED) / Offer a way out: SKL_SPEECH 50 or FLG_TRUTH_TOLD (FLG_IRES_RECRUITABLE)', 'FLG_IRES_ATTACKED; FLG_IRES_RELEASED; FLG_IRES_RECRUITABLE', 'Part 3 of 3. Foreshadows the ignition shard reveal.'),
 'DLG_MQ_A2_09_S1': ('Quell and Marr over the shuttle in the Cradle; Quell has priced every bolt / Two taken Heart Shards go in the power cradle / Marr wants Knights on board; Quell wants Guild; both want the player / Turn: Quell admits the shuttle seats four and she has promised it to six people / Ostra reads the tail number and goes quiet; it was the captain\'s shuttle', '', '', ''),
 'DLG_MQ_A3_01_S1': ('Lisk at the Cradle door controls, hand on the lever / Not redeemed: he explains, kindly, that Hush is a god and gods are owed a harvest; he opens the doors / Redeemed (QST_CH_09): he confesses twenty years of talking to Hush and closes the doors from inside / Turn: either way, he is the gentlest person in the room / Ostra: "He believes it. That is why it works on him."', '', 'FLG_LISK_REDEEMED (read)', ''),
 'DLG_MQ_A3_01_S2': ('The active companion braces the door / They ask the player to carry one message up, specific to them (Kessa: the whistle; Odo: his margin note; Tamsin: the ledger, paid) / Approval 50+: they will come back in MQ_A3_05; below: they will not / Turn: the player has to leave them; there is no option to stay / The door closes on their last line', '', '', 'Per-companion variants; 8 versions.'),
 'DLG_MQ_A3_02_S3': ('A Maker terminal in the Threshing Ring wakes to the chest Shard / Text in plain units: yield per century, field health, harvest windows / A line marked as a fault: "Ignition component missing. Yield unusable." / Turn: the component\'s signature matches the player\'s chest Shard / Hush adds a line under it, in Common: "Found."', '', '', 'Ignition-shard reveal, part 1.'),
 'DLG_MQ_A3_02_S4': ('Hush speaks face to face, through a Choirborn wearing Old Tomas\'s face / "Hello again, ship." Calls Ostra "the one who spoiled the crop" / Ostra argues, stage 4 calm; Hush agrees with everything she says, which is worse / Turn: Hush, plainly: "We did not wake you. We let her wake you. You were always coming here." / The player is the last harvest: the ignition shard is what Hush needs / Ostra: "It is not lying. That is the worst part."', 'Plain/Kind/Hard/Sly replies to Hush; Hush answers every question truthfully', '', 'Story pass D.'),
 'DLG_MQ_RT_Q_S1': ('Ostra pings the Maker relay out of habit / Hush answers on the first ring and offers her the map, politely / Ostra accepts, because refusing would be stupid / Turn: the map shows a route that ends at the Hush Core, already lit / Ostra: "It wants us to arrive on time."', '', '', ''),
 'DLG_MQ_A3_03_S3': ('Ires on her own side of the Granary, unmasked / She has fed the sky for nine hundred years and the land in glass here is what it bought / Turn: she sees the Maker record too and understands the deal was never a deal / Duel, recruit (FLG_IRES_RECRUITABLE), or let her reach Hush / Ostra asks her, once, to stop', 'Duel (FLG_IRES_DEAD) / Recruit if FLG_IRES_RECRUITABLE (FLG_IRES_ALLY) / Let her reach Hush (FLG_IRES_TO_HUSH)', 'FLG_IRES_DEAD; FLG_IRES_ALLY; FLG_IRES_TO_HUSH', ''),
 'DLG_MQ_A3_03_S5': ('Ires and Ostra, last words, by outcome / Dead: Ires: "Log it, ship." Ostra does / Ally: "Permission to come aboard." Ostra grants it in full sentences / To Hush: she walks into the light without looking back / Turn: Ostra keeps the captain\'s log entry open for a second longer than needed', '', '', ''),
 'DLG_MQ_A3_04_S1': ('Hush meets the player in a hall of standing Choirborn / "We kept them for you." Each copy is built from what the player did (flags) / Hush explains the rules, kindly: they are only what the player remembers / Turn: Hush asks which one the player wants to see first, and means it', '', '', 'Story pass H: copies from flags.'),
 'DLG_MQ_A3_04_S2': ('Faction leader copies, one per leader the player betrayed, left or angered (rep Wary or lower, or line abandoned) / Each speaks 3 to 5 lines built from the player\'s flags (e.g. Marr copy if FLG_HK_OATH_REWRITTEN unset: "You let me keep the oath.") / Talk past with Speech checks keyed to rep, or fight / Turn: the copies are accurate; the player can recognize a line they actually said / Ostra after each: what Hush got wrong', 'Talk past: SKL_SPEECH 40 to 70 by leader / Fight', '', ''),
 'DLG_MQ_A3_04_S3': ('Copies of Lisk (if not redeemed), Ires (if FLG_IRES_TO_HUSH or dead) and companions who died or left / A lost companion copy repeats the last thing they said to the player / Approval 50+ at loss: the player can talk them down; otherwise fight / Turn: a companion copy forgives the player, and Hush admits it does not understand why', 'Speech checks keyed to final approval', '', ''),
 'DLG_MQ_A3_04_S4': ('Tomas\'s copy stands by a copy of Bay 9 / He asks whether his grandmother\'s pod was found / If FLG_TOMAS_NAME_TOLD: he already knows, and says her name before the player can / Turn: Hush built him with the coat on / The copy steps aside without a fight', '', '', ''),
 'DLG_MQ_A3_05_S3': ('Before phase 3, in the Seed\'s light / Ostra asks the player to say her name, once / Taken Shards count: more taken, the more of her there is in the fight / Turn: she tells the player that if this goes badly, the opening prompts were her fault, never theirs / The player answers in a tone', 'Plain/Kind/Hard/Sly; Kind counts toward the Bind kind-choice route', '', ''),
 'DLG_MQ_A3_05_S5': ('Hush breaks; the Seed cracks like a frozen lake / "We were only doing what we were for." / No anger in it, only a farmer looking at weather / Turn: Hush asks the player what they are for / The light stops', '', '', ''),
 'DLG_MQ_A3_06_S1': ('Ostra lays out the three endings in full sentences, stage 4 / Restore: a ship and a future; magic dies, the Kindled end, and she survives as a ship, not a friend / Bind: the land heals, magic stays, the player and she die, and in three thousand years another light comes / Take: the harvest stops for good; the player becomes the thing in the sky / Turn: she tells the player which one she would pick, and then says not to listen to her / "Whatever you choose, I will hold the door."', 'Restore (CNT_HEARTS_TAKEN >= 4) / Bind (CNT_HEARTS_SPARED >= 3 or FLG_OSTRA_FORGIVEN plus three kind choices) / Take (always)', 'FLG_END_RESTORE; FLG_END_BIND; FLG_END_TAKE', 'Costs per 05-story-pass F.'),
 'DLG_MQ_A3_06_S2': ('The active companion argues their ending lean in their own terms / Kessa wants a post she chose (Restore); Odo wants the truth written (Bind); Dren depends on the Moot / Turn: they admit the cost to themselves of their own pick / Approval shifts per campaign branches', '', '', ''),
 'DLG_MQ_END_R_S2': ('Ostra, flying the Quiet, gets a ship again and says so in a voice already less hers / She asks the player to talk to her while she still sounds like herself / Turn: she starts reporting status instead of answering; the player hears her become a ship / Last full sentence from her: "Thank you for the borrowed body."', '', '', 'Cost: Ostra survives as a ship, not a friend.'),
 'DLG_MQ_END_B_S2': ('The fall: the Quiet burns; the player and Ostra in the Granary, the last land released / Ostra tells the player their real name from the Bay 9 manifest / Turn: she apologizes for the opening prompts; the player can answer / Last lines while the light goes white', 'Final tone choice (no flag; shapes the Log entry in CIN_END_B)', '', 'Cost: player and Ostra die.'),
 'DLG_MQ_END_T_S1': ('The merge: Hush, Ostra and the player share one voice / Lines start alternating, then overlap, then become "we" / Ostra asks the player to keep one word that is only theirs / Turn: the player\'s next bark comes out as "We" without the player choosing it / The harvest stops', '', '', 'Cost: player and Hush become one.'),
 'DLG_MQ_END_T_S2': ('Ostra asks for a room of her own inside the Quiet: one small cold room / She wants to keep her own name there / Turn: Hush agrees, which is the first gift it has ever given / Ostra: "Visit. Sometimes."', '', '', ''),
}


# ---------------------------------------------------------------- Shard-bearers
SB = [
    (1, 'MQ_A1_05', 'ACT_BOSS_VAEL', 'Vael', 'REG_01', 'Burning it only ripens it. Thank you, Vael.',
     'a kiln brick with a wrench scratched into it', 'Bury it under the kiln, where it is warm.', 'ACT_NPC_REEVE_ANNIK',
     'Take it. It is mine. Correction: it was mine.'),
    (2, 'MQ_A1_08', 'ACT_BOSS_CORSA', 'Corsa', 'REG_02', 'Her heading was good. We would have followed it.',
     'her brass compass, the needle pointing straight up', 'Don\'t give it to her. She steers too well.', 'ACT_NPC_HARBOR_MOSS',
     'She knew me. Nobody knows me. Take it.'),
    (3, 'MQ_A2_02', 'ACT_BOSS_SORREL', 'Sorrel', 'REG_03', 'Her trees grow for us. All of them do.',
     'a seedling in a ration tin', 'Leave it in the roots. They need it more than you.', 'ACT_NPC_THORNKING_GRAL',
     'I think I want it. I think that is a bad reason.'),
    (4, 'MQ_A2_03', 'ACT_BOSS_BRANNOCH', 'Brannoch', 'REG_04', 'He built this army for the sky. We are the sky.',
     'his oath plate, the captain\'s name polished bright', 'Give it to the captain. Oath.', 'ACT_NPC_MIRAGE_SABA',
     'He would give it to her. I am asking you not to. I think.'),
    (5, 'MQ_A2_04', 'ACT_BOSS_RIME', 'Mother Rime', 'REG_05', 'She kept them cold for later. We are later.',
     'a pod tag tied to a frost lily', 'Keep it cold. Somebody will want it later.', 'ACT_NPC_HEARTH_ELDER_YURI',
     'Take it or do not. I will not count it.'),
    (6, 'MQ_A2_05', 'ACT_BOSS_HOLLOWTWINS', 'the Hollow Twins', 'REG_06', 'We spoke to them before we spoke to her.',
     'two comms headsets sharing one cord', 'Take it and listen. Or bury it and don\'t.', 'ACT_NPC_LASTLIGHT_BEA',
     'Whatever is in it, I said it. Take it anyway.'),
]
SB_BY_BOSS = {s[2]: s for s in SB}
SB_TIC = {'ACT_BOSS_VAEL': '"Keep it warm. Keep it covered."', 'ACT_BOSS_CORSA': 'orders to a fleet that is gone, in bearings',
          'ACT_BOSS_SORREL': 'speaks as "the grove", pausing to listen', 'ACT_BOSS_BRANNOCH': 'counts drones and ranks, "my oath"',
          'ACT_BOSS_RIME': '"Shh. Later. You\'ll be fine later."', 'ACT_BOSS_HOLLOWTWINS': 'finish each other\'s sentences, wrongly'}

# ---------------------------------------------------------------- story-pass extra scenes (05-story-pass.md)
# (quest, kind, speakers, trigger, beats, choices, flags, lines, notes, dedupe phrase)
RT_HUSH = [
    ('MQ_RT_01', 'Hello, ship.', 'Unknown signal. Ignoring it. Old relays repeat things.', 'The companion, if present, hears nothing and asks why the player stopped.'),
    ('MQ_RT_02', 'You are smaller than we remember.', 'Remember. It said remember. Correction: noise.', 'Ostra runs a diagnostic out loud, twice, and finds nothing.'),
    ('MQ_RT_03', 'Your people are doing so well. Look how much they\'ve grown.', 'Grown. It means the forest. I think it means the forest.', 'Below, Thornwood\'s canopy moves in a wind that is not there; the player reads "grown" as "ripe".'),
    ('MQ_RT_04', 'We see the one carrying you.', 'It is talking to you. Do not answer it.', 'Every Remnant drone in sight turns its lens to the sky at once.'),
    ('MQ_RT_05', 'Soon.', 'I am not counting. I am not counting anything.', 'The coolant tanks below frost over in one breath.'),
    ('MQ_RT_06', 'Thank you for keeping it warm.', 'Keeping what warm.', 'The chest Shard is hot for a full minute; the player\'s hand comes away pink.'),
]
EXTRA = [
    ('MQ_P_01', 'terminal', 'PLAYER; ACT_NPC_OSTRA', 'Last 90 s of CIN_OPEN, playable',
     'Interface rises on cracked cryo glass: an unnamed ship system, amber text / Prompt 1 "Seal bulkheads": the player presses it; doors slam down the corridor / Prompt 2 "Vent core coolant": a gauge drops; the alarm pitch changes / Prompt 3 "Override bridge command": a woman\'s voice on the bridge says "Belay that" and is cut off / Prompts read like a drill, with a timer and a score / Turn: the score reads 100% just as the glass goes white; nobody tells the player what they scored', '', '', 4,
     'Story pass A. Inputs are logged and replayed in MQ_A2_06 (CIN_MUTINY). The only voice is Ires cut off; Ostra is the interface itself.', 'Seal bulkheads'),
    ('MQ_P_02', 'boss_death', 'ACT_NPC_HOLLOWED_OFFICER; ACT_BOSS_HUSH; ACT_NPC_OSTRA; PLAYER', 'Hollowed crew officer mini-boss reaches 10% HP',
     'The officer stops mid-swing and straightens, the way he once stood at a post / His mouth moves in a calm voice that is not his: "There you are. We\'ve been counting." / The player\'s chest Shard answers with a single tone / Ostra: "Static. Ignore it." too fast / Turn: the officer dies smiling, and his hand points up / Tomas, behind, asks who was talking', '', '', 6,
     'Story pass C. First Hush line; true: Hush has been counting the stall years.', "We've been counting"),
] + [
    (q, 'conversation', 'ACT_NPC_OSTRA; ACT_BOSS_HUSH; PLAYER', 'Top of the Relay Tower, after the beacon wakes',
     f'Ostra pings the escape-pod network and the region fills in on the map / A second signal answers on Ostra\'s own band / Hush: "{line}" / Ostra: "{react}" / Turn: {turn} / The map stays lit; the line goes dead', '', '', 6,
     f'Story pass C, tower {i + 1} of 6; every Hush line is true.', line)
    for i, (q, line, react, turn) in enumerate(RT_HUSH)
] + [
    ('MQ_A2_06', 'terminal', 'PLAYER; ACT_NPC_OSTRA', 'Inside CIN_MUTINY, replay of the opening prompts',
     'The memory replays the same amber prompts from the cold open / This time each prompt has its label: "Seal bulkheads: bridge lockout" / "Vent core coolant: overload sequence" / "Override bridge command: captain removed" / The player\'s own inputs from MQ_P_01 replay, with their real timing / Turn: the score screen returns: 37,000 pods lost, 4,000 kept', '', '', 4,
     'Story pass A payoff.', 'replays those exact inputs'),
    ('MQ_A2_06', 'conversation', 'ACT_NPC_OSTRA; PLAYER', 'After CIN_MUTINY, only if FLG_OSTRA_CONFRONTED',
     'Ostra, before the silence: "You said the core. At the Anchor. You were right." / She quotes the player\'s own words back from her log / "Log it. I was wrong and you were right. Log it." / Turn: she asks the player to keep the log, because she cannot be trusted to / Silence', '', '', 8,
     'Story pass B payoff; only when the Anchor confrontation happened.', 'You were right'),
    ('MQ_A3_03', 'terminal', 'PLAYER; ACT_NPC_OSTRA; ACT_BOSS_HUSH', 'Maker record in the Granary, after the Shard-flow puzzle',
     'A Maker record plays like a farming manual: planting, soil, yield / The Weave is the field; Veyl is the farm; magic is irrigation / Next harvester scheduled if this one fails: in about 3,000 years / Ostra reads the Rites table and recognizes the player\'s own Rites as plumbing / Turn: Hush adds, kindly, that the Church\'s prayers improve yield / The record ends on an empty field label: "Plot 7, Veyl"', '', '', 10,
     'Story pass E. Lore item BOOK_059 style.', 'Weave is the farm'),
    ('MQ_A3_04', 'conversation', 'ACT_BOSS_HUSH; PLAYER; ACT_NPC_OSTRA', 'Copies of Shard-bearers the player Took',
     'One copy per Heart Shard taken (FLG_HEART_1_TAKEN to FLG_HEART_6_TAKEN) / Each copy speaks its lucid line, then a new one: what it lost when the player took the Heart / Ostra hears her own memory fragments in their mouths / Turn: the copies do not attack; they ask the player to give the Shard back / Talk past, or fight', 'Talk past: SKL_SPEECH 50 / Fight', '', 18,
     'Story pass H: copies of Taken Shard-bearers.', 'Shard-bearers they Took'),
]

# Ostra systemic: contradictions and lucid counts (writing source)
OSTRA_SETS = [
    ('Ostra confidently wrong, Act 1', 'MQ_A1_01', 1, 'bark_set', 'Act 1 field comments on crash debris and lore',
     'Ostra explains the Fall with total confidence and gets it wrong / Samples: "The core failed. Reactor fatigue. I logged it." "The captain followed protocol." "There was no hail." / Every line is later contradicted by a lore item, Choir stone or lucid line / Write so a second playthrough hears each as a lie she believes / Turn: one line in ten trails off mid-word and she does not notice', 120, 'Story pass B.', ''),
    ('Contradiction found reactions', '', 1, 'bark_set', 'Player picks up a contradicting source (CNT_OSTRA_CONTRADICTIONS +1)',
     'Trigger: lore item, Choir stone or lucid line that disagrees with Ostra / Ostra explains the source away: bad copy, Church edit, madness / Counts 1 and 2: amused / Count 3: short; hints shorten (UI: hint text color shifts colder) / Turn: at count 3 the Anchor option opens', 90, 'Story pass B.', 'CNT_OSTRA_CONTRADICTIONS +1'),
    ('Anchor confrontation', '', 1, 'conversation', 'Any Anchor, option "Ostra, you\'re wrong about the core." (CNT_OSTRA_CONTRADICTIONS >= 3)',
     'The player names the core / Ostra denies it, citing her own log, entry by entry / The player lists the sources; she has an answer for each, getting shorter / Turn: she reaches the forty-minute gap in her own log and stops mid-sentence / "Hints will be brief from now on. Efficiency." Her hint color turns cold / The player can push (Speech 40) and she ends the conversation herself', 90, 'Story pass B. Hints turn colder (UI).', 'FLG_OSTRA_CONFRONTED'),
] + [
    (f'Lucid count {n}', '', 2, 'bark_set', f'After a lucid moment when CNT_LUCID_HEARD = {n}', b, 20, 'Story pass G.', f'CNT_LUCID_HEARD={n}')
    for n, b in [
        (1, 'One officer, one strange line / Ostra: "They are mad. Mad people say true-sounding things." / Calm, almost amused / Turn: she adds the line to her list of things that do not fit, out loud, by accident'),
        (2, 'Two officers, the same story from two sides / Ostra: "Two. Coincidence is cheap." / She checks her log while talking and the player hears her pause / Turn: she asks the player which line they believe'),
        (3, 'Three lines now fit together / Ostra: "I think they rehearsed it. Correction: they had nine hundred years to rehearse it." / She sounds proud of the correction / Turn: she stops using "Correction" for the rest of the region'),
        (4, 'Four lines: enough to see the shape, in any order / Ostra: "Stop. I am checking my logs. The logs agree with me. The logs are mine." / Turn: she realizes she wrote the logs / Silence for ten seconds'),
        (5, 'Five / Ostra: "I do not want the sixth." / She asks the player to skip the next lucid moment and knows they cannot / Turn: she says the sixth line before the player hears it, and is right'),
        (6, 'All six / Ostra: "Stop telling me this." / No status words at all / Turn: the stop-collecting scene unlocks at the next Anchor'),
    ]
] + [
    ('Stop collecting', 'MQ_A2_06', 2, 'conversation', 'Next Anchor after CNT_LUCID_HEARD = 6, before MQ_A2_06',
     'Ostra asks to talk, the first time she has asked / She recites all six lucid lines in order, perfectly / "You are collecting them like evidence. Stop. Please." / Turn: she admits she knows what is in the Undervault and would like the player not to go / The player promises to go slowly, refuses, or says nothing / She thanks them either way', 20, 'Story pass G.', 'stop collecting'),
]


# ---------------------------------------------------------------- outline expansion
def kind_map(k, purpose):
    k = (k or '').lower()
    if purpose.lower().startswith('lucid moment'):
        return 'lucid_moment'
    return {'bark': 'bark_set', 'cine': 'cinematic', 'cinematic': 'cinematic', 'ambi': 'ambient'}.get(k, k or 'conversation')


def ostra_line(stage, key, text):
    if stage == 1 and FALL_WORDS.search(text):
        return pick(IRONY, key + 'i').format(l=pick(OSTRA_WRONG, key))
    return pick(OSTRA_BEAT, key + 'o').format(l=pick(OSTRA_LIVE[stage], key))


def branch_text(b):
    t = b['choice']
    if b.get('requires') and b['requires'] != 'none':
        t += f" [{b['requires']}]"
    eff = '; '.join(x for x in [b.get('flags_set', ''), b.get('approval', ''), b.get('reputation', '')] if x)
    return t + (f' -> {eff}' if eff else '')


TONE_HINTS = ['Tones: Plain / Kind / Hard / Sly', 'Tones: Plain / Kind / Hard / Sly; companions note Kind and Hard (+/-5)',
              'Tones: Plain / Kind / Hard / Sly; Sly opens one extra line', 'Tones: Plain / Kind / Hard / Sly; Hard ends the scene early']


def expand(sc, idx, n_in_q, q, stage):
    sid, kind, purpose = sc['scene_id'], sc['_kind'], sc['purpose'].strip().rstrip('.')
    spk = [s.strip() for s in sc['speakers'].split(';') if s.strip()]
    nonp = [s for s in spk if s not in ('PLAYER', 'ACT_NPC_OSTRA')] or spk
    a = name_of(nonp[0]) if nonp else 'Someone'
    b = name_of(nonp[1]) if len(nonp) > 1 else a
    qsteps = steps.get(sc['qst_id'], [])
    st = qsteps[min(len(qsteps) - 1, idx * len(qsteps) // max(1, n_in_q))] if qsteps else None
    loc = (st or {}).get('loc') or (q.get('locations', '').split(';')[0].strip() if q else '')
    place = place_of(loc)
    sents = sentences(q.get('summary', '')) if q else []
    det = sents[idx % len(sents)] if sents else ''
    turn = sents[(idx + 1) % len(sents)] if len(sents) > 1 else ''
    beats = []
    if kind in ('conversation', 'lucid_moment'):
        beats.append(pick(OPENERS, sid).format(place=place, a=a))
        beats.append(endp(cap(purpose)))
        if det:
            beats.append(pick(DETAIL, sid + 'd').format(a=a, b=b, s=det))
        if 'ACT_NPC_OSTRA' in spk:
            beats.append(ostra_line(stage, sid, purpose + ' ' + det))
        elif len(nonp) > 1:
            beats.append(f'{b} pushes back on {a}; they disagree about what the player should do.' if h(sid) % 2 else f'{b} adds one small, specific want of their own.')
        if turn and turn != det:
            beats.append(pick(TURN, sid + 't').format(s=turn))
        if st:
            beats.append(pick(CLOSE, sid + 'c').format(s=st['objective']))
    elif kind == 'bark_set':
        _obj = (st or {}).get("objective") or "quest beat"
        beats.append(f'Trigger: {_obj} ({place}).' if place.split(',')[0] not in _obj else f'Trigger: {_obj}.')
        first = a.split(' (')[0].split()[-1] if a else ''
        beats.append(endp(cap(purpose)) if first and first.lower() in purpose.lower()[:len(first) + 12] else endp(f'{cap(a)}: {purpose}'))
        beats.append(pick(['Write lines that react to what the player just did, not to the quest log.', 'Each variant names one concrete thing in view.',
                           'Short; each line works if heard alone.', 'Lines escalate across repeats; the last one is the funniest or the saddest.',
                           'One variant per tone of the last player choice.'], sid))
        beats.append(ostra_line(stage, sid, purpose) if 'ACT_NPC_OSTRA' in spk else ('Each companion records its own variant in its own voice.' if nonp and nonp[0] == 'COMPANION_ACTIVE' else f'Voice: {VOICE.get(nonp[0] if nonp else "", "speaker voice sheet, style guide 3")}.'))
        if det:
            beats.append(pick(DETAIL, sid + 'd').format(a=a, b=b, s=det))
    elif kind == 'ambient':
        beats.append(endp(f'Ambience at {place}: {purpose}'))
        beats.append(f'Regional saying used once: "{SAYING.get(q.get("region", ""), SAYING["REG_HUB"]) if q else SAYING["REG_HUB"]}"')
        if det:
            beats.append(pick(DETAIL, sid + 'd').format(a=a, b=b, s=det))
        beats.append(pick(['Overlapping voices; no line longer than eight words.', 'Two people talk past each other; one of them is right.',
                           'Loops until the player leaves; the loop has one line that only plays once.', 'A child repeats an adult line wrong.'], sid))
    elif kind == 'echo':
        beats.append(f'A Weave recording flickers up at {place}.')
        beats.append(endp(cap(purpose)))
        if det:
            beats.append(pick(DETAIL, sid + 'd').format(a=a, b=b, s=det))
        beats.append(pick(['The recording ends mid-word when the player steps closer.', 'It loops once, and the second time one word is different.',
                           'Ostra names the date before the recording does.', 'The figure looks at the player for one second it should not.'], sid))
    elif kind == 'terminal':
        beats.append(f'A Meridian terminal at {place} wakes to the Kindled\'s touch.')
        beats.append(endp(cap(purpose)))
        if det:
            beats.append(pick(DETAIL, sid + 'd').format(a=a, b=b, s=det))
        beats.append(pick(['Screen text in ship log format; one line is redacted until after MQ_A2_06.', 'The terminal asks for crew ID; the chest Shard answers.',
                           'Last line on screen is a crew member\'s personal note left in the system.'], sid))
    else:  # cinematic
        beats.append(f'Wide on {place}.')
        beats.append(endp(cap(purpose)))
        if det:
            beats.append(pick(DETAIL, sid + 'd').format(a=a, b=b, s=det))
        beats.append(f'Close on {a}; player armor visible (in-engine).')
    if idx == n_in_q - 1 and q and q.get('journal') and len(beats) < 8:
        beats.append(pick(JOURNAL_CLOSE, sid + 'j').format(s=q['journal']))
    while len(beats) < 4:
        beats.append(pick(COMP_REACT, sid + str(len(beats))).format(c='The active companion'))
    return beats[:8], place, loc


def fmt_beats(beats):
    return ' / '.join(f'{i}. {b.strip()}' for i, b in enumerate(beats, 1))


ROWS = []
COLS = ['scene_id', 'source', 'quest_id', 'act', 'region', 'location', 'kind', 'speakers', 'trigger', 'beats', 'player_choices',
        'flags_set', 'est_lines', 'est_words', 'ostra_stage', 'notes', 'script', 'status']
counter = collections.defaultdict(int)


CAT = 'quest'


def add(owner, source, qid, act, region, location, kind, speakers, trigger, beats, choices, flags, lines, stage, notes):
    counter[owner] += 1
    sid = f'SCN_{owner}_{counter[owner]:02d}'
    if isinstance(beats, str):
        beats = [x.strip() for x in beats.split(' / ') if x.strip()]
    ROWS.append({'scene_id': sid, 'source': source, 'quest_id': qid, 'act': act, 'region': region, 'location': location, 'kind': kind,
                 'speakers': speakers, 'trigger': trigger, 'beats': fmt_beats(beats), 'player_choices': choices, 'flags_set': flags,
                 'est_lines': int(lines), 'est_words': int(lines) * 9, 'ostra_stage': stage, 'notes': notes, 'status': 'draft', '_cat': CAT})
    return sid


def norm_spk(s):
    return '; '.join(x.strip().replace('COMPANION_ACTIVE', 'ACT_CMP_ACTIVE').replace('COMPANION_LOST', 'ACT_CMP_LOST')
                     .replace('COMPANION_RETURNING', 'ACT_CMP_RETURNING') for x in s.split(';') if x.strip())


warn = []
by_q = collections.OrderedDict()
for sc in outline:
    sc['_kind'] = kind_map(sc.get('kind'), sc.get('purpose', ''))
    by_q.setdefault(sc['qst_id'], []).append(sc)
used_hb = set()
for ex in EXTRA:
    hits = [o for o in outline if o['qst_id'] == ex[0] and ex[9].lower() in o.get('purpose', '').lower()]
    if hits and hits[0]['scene_id'] not in HB:
        HB[hits[0]['scene_id']] = (ex[4], ex[5], ex[6], ex[8] + ' (writing beats on campaign scene)')
HUSH_THROUGH = {}
for o in outline:
    m = re.search(r'Last phase: Hush speaks once through[^"]*"([^"]+)"', o.get('purpose', ''))
    if m:
        HUSH_THROUGH[o['qst_id']] = m.group(1)
SB = [tuple(list(x[:5]) + [HUSH_THROUGH.get(x[1], x[5])] + list(x[6:])) for x in SB]
SB_BY_BOSS = {x[2]: x for x in SB}
outline_text = ' '.join(s.get('purpose', '') for s in outline).lower()


def quest_order_key(qid):
    if qid in MQ_ORDER:
        return (0, MQ_ORDER.index(qid), qid)
    return (1, 0, qid)


for qid in sorted(by_q, key=quest_order_key):
    scs = by_q[qid]
    q = quests.get(qid, {})
    region = q.get('region', '')
    act = q.get('act', '') or act_of_region(region)
    stage = stage_of(qid, act, region)
    # branch attach: last conversation with est_lines >= 0.8*max; hand scenes with choices take precedence
    hb_choice = any(HB.get(s['scene_id'], ('', '', '', ''))[1] for s in scs)
    convs = [s for s in scs if s['_kind'] in ('conversation', 'lucid_moment')]
    target = None
    if convs and branches.get(qid) and not hb_choice:
        mx = max(int(s['est_lines'] or 0) for s in convs)
        target = [s for s in convs if int(s['est_lines'] or 0) >= 0.8 * mx][-1]['scene_id']
    heart_branches = [b for b in branches.get(qid, []) if 'Heart Shard' in b['choice']]
    for i, sc in enumerate(scs):
        beats, place, loc = expand(sc, i, len(scs), q, stage)
        choices, flags, notes = '', '', f"campaign {sc['scene_id']}"
        if sc['scene_id'] in HB:
            hb = HB[sc['scene_id']]
            beats = [x.strip() for x in hb[0].split(' / ') if not x.strip().startswith('Hush, last phase')]
            choices, flags = hb[1], hb[2]
            notes += ('; ' + hb[3]) if hb[3] else ''
            used_hb.add(sc['scene_id'])
        if sc['scene_id'] == target:
            bl = [b for b in branches[qid] if b not in heart_branches]
            if bl:
                choices = ' | '.join(branch_text(b) for b in bl)
                flags = '; '.join(sorted({f.strip() for b in bl for f in b.get('flags_set', '').split(';') if f.strip()}))
                outs = [b['outcome'] for b in bl if b.get('outcome')]
                if outs and len(beats) < 8:
                    beats.insert(min(len(beats), 5), pick(COST, sc['scene_id']).format(s=' Or: '.join(endp(o) for o in outs[:2])))
        if not choices and 'PLAYER' in sc['speakers'] and sc['_kind'] in ('conversation', 'lucid_moment'):
            choices = pick(TONE_HINTS, sc['scene_id'])
        if sc['_kind'] == 'cinematic':
            m = re.search(r'(CIN_[A-Z0-9_]+)', sc['scene_id'])
            if m:
                notes += f'; shot outline in design/writing/cinematics.csv ({m.group(1)})'
        if stage == 2 and str(act) == '2' and 'ACT_NPC_OSTRA' in sc['speakers'] and qid not in MQ_ORDER:
            notes += '; record a stage 3 Ostra variant if played after MQ_A2_06'
        add(qid, 'campaign', qid, act, region, place, sc['_kind'], norm_spk(sc['speakers']), (beats and '') or '', beats, choices, flags,
            sc['est_lines'] or 0, stage, notes)
        ROWS[-1]['trigger'] = (f"Step: {steps[qid][min(len(steps[qid]) - 1, i * len(steps[qid]) // max(1, len(scs)))]['objective']}"
                               if steps.get(qid) else 'Quest start')
        # heart choice + spare grave after each lucid moment
        if sc['_kind'] == 'lucid_moment' and qid in [s[1] for s in SB]:
            n, _, boss, bname, reg, hush, grave, ask, npc, ost = [s for s in SB if s[1] == qid][0]
            hc = ' | '.join(branch_text(b) for b in heart_branches) or f'Take (FLG_HEART_{n}_TAKEN) | Spare (FLG_HEART_{n}_SPARED)'
            hb_beats = (f'The Heart Shard lifts out of {bname}, fist-sized, humming in {ELEMENT[reg]} light / '
                        f'Ostra wants it: "{ost}" / {bname}, fading, asks one thing: "{ask}" / '
                        f'The active companion argues their lean (approval per companion_approval.csv) / '
                        f'Take: Ostra absorbs it, +5% max Ward, CIN_MEM_{n} plays; {REGION[reg]} keeps Hollowing after Act 2 / '
                        f'Spare: {bname} dies as a person; {REGION[reg]} stops Hollowing; grave scene follows / '
                        f'Turn: either way the player hears Ostra breathe, which a ship mind does not need to do')
            CAT = 'heart'
            add(qid, 'writing', qid, act, region, place, 'conversation', f'PLAYER; ACT_NPC_OSTRA; {boss}; ACT_CMP_ACTIVE',
                'Immediately after the lucid moment', hb_beats, hc, f'FLG_HEART_{n}_TAKEN; FLG_HEART_{n}_SPARED; CNT_HEARTS_TAKEN; CNT_HEARTS_SPARED',
                20, stage, f'Heart Shard choice {n} (04 section 1).')
            add(qid, 'writing', qid, act, region, place, 'conversation', f'PLAYER; ACT_NPC_OSTRA; {npc}',
                f'FLG_HEART_{n}_SPARED, after the choice',
                f'A small grave dug by {name_of(npc)}, marked with {grave} / {name_of(npc)} says one plain thing about who {bname} was before the madness / '
                f'Ostra reads the officer\'s Meridian rank and berth, the way a chaplain would / '
                f'Turn: {name_of(npc)} asks the player whether {bname} was a monster or a person; the player answers / The region\'s colors warm by one step (world-state change)',
                'Plain/Kind/Hard/Sly', '', 20, stage, f'Spare grave scene {n}.')
            CAT = 'quest'
    # story-pass extras for this quest
    for ex in [e for e in EXTRA if e[0] == qid]:
        _, kind, spk, trig, bts, ch, fl, ln, nt, dd = ex
        if dd.lower() in outline_text:
            warn.append(f'extra merged into campaign scene ("{dd}") in {qid}')
            continue
        add(qid, 'writing', qid, act, region, place_of((q.get('locations', '') or '').split(';')[0].strip()), kind, spk, trig, bts, ch, fl, ln, stage, nt)

for k in HB:
    if k not in used_hb:
        warn.append(f'hand beats not matched to campaign scene: {k}')

# Ostra contradiction / lucid sets
CAT = 'ostra_sys'
for title, qid, stg, kind, trig, bts, ln, nt, dd in OSTRA_SETS:
    add('OSTRA', 'writing', qid, '1' if stg == 1 else '2', '', 'Any (Ostra, voice only)', kind, 'ACT_NPC_OSTRA; PLAYER' if kind == 'conversation' else 'ACT_NPC_OSTRA',
        trig, bts, 'Plain/Kind/Hard/Sly; SKL_SPEECH 40 to push' if kind == 'conversation' else '',
        'FLG_OSTRA_CONFRONTED' if 'confrontation' in title.lower() else ('FLG_OSTRA_ASKED_STOP' if 'Stop' in title else ''),
        ln, stg, f'{title}. {nt}')

# ---------------------------------------------------------------- bosses (systemic)
CAT = 'bosses'
PERSONA = {
    'ACT_BOSS_SPINEGATE': 'challenges in old security code-phrases', 'ACT_BOSS_CANTOR': 'sings Hush\'s hymn underwater, then speaks in its rests',
    'ACT_BOSS_HALDEN': 'bows before the fight and offers a free hit; sworn to guard Sorrel\'s forest', 'ACT_BOSS_GRAFTED': 'speaks only in build orders',
    'ACT_BOSS_YSSE': 'prays to Hush aloud and counter-casts in rhythm', 'ACT_BOSS_LAMPLIGHTER': 'gives clipped bridge commands to nobody',
    'ACT_BOSS_SKIMMERACE': 'trash-talks over a boat horn and keeps score', 'ACT_BOSS_ARKKNIGHT': 'reports to a watch officer dead for centuries',
    'ACT_BOSS_SENTINELS': 'recite lift access rules in turn', 'ACT_BOSS_SMUGGLERQUEEN': 'negotiates during the fight; Speech 60 ends it',
    'ACT_BOSS_WRECKFOREMAN': 'shouts shift orders at a crew of scrap', 'ACT_BOSS_MIRRORKNIGHT': 'repeats the player\'s last bark back',
    'ACT_BOSS_LASTPILOT': 'still flies the approach checklist', 'ACT_BOSS_TOWERWITCH': 'rents her floors to the cold and charges the player',
    'ACT_BOSS_CRYPTABBOT': 'keeps the dead in alphabetical order', 'ACT_BOSS_CLOCKPRIOR': 'rings the hours and attacks on the bell',
    'ACT_BOSS_VAULTKEEPER': 'reads names off the vault wall, slowly', 'ACT_BOSS_HAULER': 'announces delivery stops on a route that ended',
    'ACT_BOSS_QUIETCORE': 'is Hush\'s machinery, speaking in harvest terms', 'ACT_BOSS_ARCHIVIST': 'indexes the player as a crop sample',
    'ACT_BOSS_MERIDIANGHOST': 'is the ship\'s last crew roster, all voices at once', 'ACT_BOSS_UNMADECHOIR': 'sings with every voice Hush ever gathered',
}
MUTE = {'BEAST', 'MULTI'}
SPEAK_OVERRIDE = {'ACT_BOSS_LASTPILOT', 'ACT_BOSS_SENTINELS', 'ACT_BOSS_HAULER', 'ACT_BOSS_VAULTKEEPER'}
MAIN_FOR = {'ACT_BOSS_SPINEGATE': 'MQ_A1_05C', 'ACT_BOSS_CANTOR': 'MQ_A1_07', 'ACT_BOSS_HALDEN': 'MQ_A2_02C', 'ACT_BOSS_GRAFTED': 'MQ_A2_03C',
            'ACT_BOSS_YSSE': 'MQ_A2_04C', 'ACT_BOSS_LAMPLIGHTER': 'MQ_A2_05C'}
for s in SB:
    MAIN_FOR[s[2]] = s[1]
DEATH_FRAMES = ['{n} drops to one knee and does not get up', '{n} staggers into the arena wall and slides down', 'The light goes out of {n} all at once',
                '{n} falls the way a building falls, slowly then all at once', '{n} sways, steadies, and falls on the second try']
OSTRA_BOSS = {1: ['"Threat logged. Deck officer build. Mine, once."', '"Noted. It is large. Correction: it is very large."', '"Unknown class. I dislike unknown."'],
              2: ['"I think I know that one. I do not want to."', '"Weak point: the {w}. I think."', '"Be careful. I am asking."'],
              3: ['"Another thing I made, probably."', '"Hit the {w}. Please end it quickly."', '"It is not its fault. Hit it anyway."'],
              4: ['"End it cleanly. That is all I ask."', '"The {w}. You know what to do."', '"I am with you. Say when."']}
all_bosses = [b for b in bosses if b['ACT_ID'] != 'ACT_BOSS_HUSH'] + [{'ACT_ID': 'ACT_BOSS_HUSH', 'Boss': 'Hush', 'Class': 'Final', 'Region': 'REG_Q', 'Level': '80', 'Archetype': 'CASTER',
                        'Phases': '3', 'Phase HP thresholds %': '66; 33', 'Weak points / parts': 'the Seed', 'Notes': 'Lens, Choir, Seed phases (02-characters)',
                        'Resonance unlocked': '', 'Region name': 'the Quiet'}]
for bz in all_bosses:
    bid, bname, cls, reg = bz['ACT_ID'], bz['Boss'].split(',')[0], bz['Class'], bz['Region']
    owner = 'BOSS_' + bid.replace('ACT_BOSS_', '')
    lvl = int(bz.get('Level') or 1)
    act = 'post' if cls == 'Raid' else ('3' if reg == 'REG_Q' else act_of_region(reg))
    stg = 4 if reg == 'REG_Q' else stage_of(MAIN_FOR.get(bid, ''), act, reg)
    speaks = bz.get('Archetype') not in MUTE and bid not in ('ACT_BOSS_ASHCOLOSSUS', 'ACT_BOSS_NIGHTDRAKE', 'ACT_BOSS_FROSTTITAN',
                                                             'ACT_BOSS_BONEHARVESTER', 'ACT_BOSS_MINEGOLEM', 'ACT_BOSS_FURNACEMAW') or bid in SPEAK_OVERRIDE
    weak = (bz.get('Weak points / parts') or 'core').split(' x')[0].split(' when')[0].strip().lower()
    thr = [t.strip() for t in (bz.get('Phase HP thresholds %') or '').split(';') if t.strip()]
    loc = place_of(MAIN_FOR.get(bid, '')) if False else (REGION.get(reg, reg))
    ost = pick(OSTRA_BOSS[stg], bid).format(w=weak)
    if bid in SB_BY_BOSS:
        voice = f'tic: {SB_TIC[bid]}'
    elif bid == 'ACT_BOSS_HUSH':
        voice = 'always "we", calm, polite; never lies'
    else:
        voice = PERSONA.get(bid, 'creature vocal set only')
    intro = [f'Arena: {bz.get("Notes") or "boss arena"} ({REGION.get(reg, reg)}, level {lvl}).']
    if speaks:
        intro.append(f'{bname} opens: one line in voice ({voice}).')
    else:
        intro.append(f'{bname} has no voice: creature vocal cue; companion names it first.')
    intro.append(f'Ostra (stage {stg}): {ost}')
    for k, t in enumerate(thr, 2):
        intro.append(f'Phase {k} at {t}% HP: {"new line, the voice changes" if speaks else "roar cue and Ostra warning"}.')
    if bid in SB_BY_BOSS:
        intro.append(f'Last phase: Hush speaks through {bname} in {bname}\'s own voice: "{SB_BY_BOSS[bid][5]}"')
    if bid == 'ACT_BOSS_HUSH':
        intro = ['Arena: the Hush Core; three phases (Lens, Choir, Seed).', 'Hush opens: "We are glad you came. We were worried about the weather."',
                 'Phase 1 Lens: Hush describes each block of stolen land it throws, kindly, by region and year.',
                 'Phase 2 Choir at 66%: copies speak in voices the player knows; Ires copy if FLG_IRES_TO_HUSH.',
                 'Phase 3 Seed at 33%: Hush scales down 4% HP per Heart Shard taken; it notices and says so, without anger.',
                 'Ostra (stage 4) calls the openings in full sentences; with all six Hearts taken she has "Meridian\'s Voice".']
    intro.append(f'Player-death lines: 3 variants{", in voice" if speaks else " (Ostra and companion only)"}.')
    if speaks and bid == 'ACT_BOSS_SMUGGLERQUEEN':
        intro.append('Speech 60 check mid-fight ends it as a deal (rewards differ).')
    if bid == 'ACT_BOSS_HALDEN':
        intro.append('He bows; a free hit is allowed. Taking it costs Kessa approval (design choice).')
    intro = intro[:8]
    while len(intro) < 4:
        intro.append('Companion warning bark on the first big attack.')
    sp = '; '.join(([bid] if speaks else []) + ['ACT_NPC_OSTRA', 'PLAYER', 'ACT_CMP_ACTIVE'])
    base = {'Shard-bearer': 30, 'Citadel': 20, 'Field': 16, 'Site': 16, 'Raid': 20, 'Final': 40}.get(cls, 16)
    if not speaks:
        base = 8
    add(owner, 'systemic', MAIN_FOR.get(bid, ''), act, reg, REGION.get(reg, reg), 'boss_intro', sp, f'Enter {bname} arena',
        intro, '', '', base, stg, f'{cls} boss, {bz.get("Archetype", "")}. Voice: {voice}.')
    death = [pick(DEATH_FRAMES, bid).format(n=bname) + '.']
    if bid in SB_BY_BOSS:
        death += ['The tic stutters and stops; the lucid moment scene takes over (see main quest rows).',
                  f'Ostra goes silent for exactly as long as it takes {bname} to breathe twice.']
    elif bid == 'ACT_BOSS_LAMPLIGHTER':
        death += ['At 30% the mask cracks; a Meridian captain\'s insignia; she flees into the dark lamp shaft (counts as defeated).',
                  'Ostra: nine seconds of nothing, then "Rank: captain."']
    elif bid == 'ACT_BOSS_HUSH':
        death += ['Hush: "We were only doing what we were for."', 'The Seed goes dark; leads into MQ_A3_06.']
    elif speaks:
        death += [f'Last words in voice ({voice}); something ordinary, never a speech.', pick(['Ostra names who it was, if she knows.',
                  'Ostra says nothing; the player notices.', 'Ostra logs it with a rank and a deck.'], bid)]
    else:
        death += ['A last creature sound, then quiet.', 'Ostra: one dry line about its size.']
    res = bz.get('Resonance unlocked') or ''
    death.append(f'Reward beat: {("Resonance " + res + " unlocked; ") if res else ""}drop and Ember toast play.')
    death.append(pick(['Companion reaction bark, one line, by approval.', 'Companion says the name of a person this boss hurt.',
                       'Companion sits down for a second before moving on.'], bid + 'c'))
    add(owner, 'systemic', MAIN_FOR.get(bid, ''), act, reg, REGION.get(reg, reg), 'boss_death', sp, f'{bname} defeated',
        death, '', '', {'Shard-bearer': 10, 'Citadel': 8, 'Final': 10}.get(cls, 6) if speaks else 4, stg, f'{cls} boss death.')

# ---------------------------------------------------------------- companions (systemic)
CAT = 'cmp_scenes'
COMP = {
    'C1': ('Kessa Vane', 'REG_01', 'folds everything corners first', 'a post she chose herself', 'being ordered to burn a village again', 'her old squad\'s tin whistle', True, 'Restore', 'MQ_A1_02', 'Emberwatch'),
    'C2': ('Brother Odo', 'REG_HUB', 'licks his thumb before turning a page', 'one true page in the Log', 'fire, for books and for himself', 'a pencil stub tied to his wrist', False, 'Bind', 'MQ_A1_04', 'the Log Chapel'),
    'C3': ('Tamsin Rook', 'REG_02', 'prices everything out loud', 'to owe nobody anything', 'her sister\'s face', 'a ledger with her debts in red', True, 'Restore', '', 'Smugglers\' Cut'),
    'C4': ('Vey', 'REG_01', 'sits facing the door', 'one contract she picks herself', 'being the replacement', 'a black contract seal she never broke', True, 'Ostra\'s choice', '', 'the Anchor where the player first died'),
    'C5': ('Hal Merrow', 'REG_02', 'hums to drown out the song', 'one hour of real silence', 'liking the song', 'wax earplugs he makes himself', True, 'Bind', 'MQ_A1_06', 'a Choir vault in Saltmere'),
    'C6': ('Sister Calla', 'REG_02', 'falls asleep sitting up', 'one patient who stays cured', 'running out of bandages before patients', 'a spoon she sterilizes with Ember', False, 'Bind', 'MQ_A1_06', 'Stiltmarket'),
    'C7': ('Dren', 'REG_03', 'names every animal he meets', 'to go home without blood', 'becoming his father', 'the key to his own cage, on a cord', True, 'Take or Bind', 'MQ_A2_02', 'the Thorn King\'s Moot'),
    'C8': ('Unit 9', 'REG_04', 'apologizes to doors', 'a valid order', 'an order it should not follow', 'a crew badge, the name worn off', False, 'Restore', 'MQ_A2_03', 'the Last Hangar'),
}
BANTER = {
    'C1': ['Kessa teaches the player to fold a cloak corners first and is appalled by the result; she refolds it in silence',
           'Kessa salutes a Knight patrol by reflex, then hates herself for it for a mile',
           'Kessa asks whether Kindled dream; she has not slept a full night since Emberlow'],
    'C2': ['Odo cites the Log for a rash and the entry turns out to be about Ballast, the ship cat',
           'Odo asks what Earth smelled like; the player\'s Origin gives one word and Odo writes it down like scripture',
           'Odo writes the player\'s name in his margin, then worries it is heresy to put a sleeper in the Log'],
    'C3': ['Tamsin values the player\'s armor out loud, piece by piece, then values the player',
           'Tamsin loses a knife-throwing bet on purpose and will not admit it',
           'Tamsin sees her sister\'s handwriting on a shop ledger and pretends she did not'],
    'C4': ['Vey counts the exits in every room aloud, and once counts the player as one',
           'Vey asks how Kindled death feels, for professional reasons, then for personal ones',
           'Vey tries to tell a joke; it comes out as a contract, word for word'],
    'C5': ['Hal hums over Ostra and Ostra asks him to pick a better key; they argue about pitch',
           'Hal and Ostra argue whether a Shard can be out of tune; Unit 9 is not there to settle it',
           'Hal says the song once called him by his mother\'s pet name, and he almost went'],
    'C6': ['Calla falls asleep mid-sentence and finishes the sentence an hour later, exactly where she stopped',
           'Calla keeps a tally of the dead on her forearm in ink; the player asks how many',
           'Calla asks the player to tell her if she starts forgetting words'],
    'C7': ['Dren names a Strider, a crow and a rock, in that order, and is offended when the rock does not answer',
           'Dren explains clan insults; the worst one is "cold-slept cousin"',
           'Dren says his father\'s last words were a feud name, not his son\'s'],
    'C8': ['Unit 9 files a maintenance ticket on the player\'s armor and assigns it priority one',
           'Unit 9 asks Ostra for orders; Ostra realizes it still uses her old voice and goes quiet',
           'Unit 9 wonders whether the crew member named on its badge would mind it being borrowed'],
}
AREAS = ['REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06', 'REG_U', 'REG_Q', 'REG_HUB']
for c, (nm, creg, habit, want, fear, item, rom, lean, recq, recloc) in COMP.items():
    aid = f'ACT_CMP_{c}'
    o = f'CMP_{c}'
    short = nm.split()[0] if c not in ('C8',) else nm
    if c == 'C2':
        short = 'Odo'
    if c == 'C6':
        short = 'Calla'
    hearO = c in ('C5', 'C8')
    spk = f'{aid}; PLAYER' + ('; ACT_NPC_OSTRA' if hearO else '')
    st = stage_of(recq, act_of_region(creg), creg) if recq else (1 if creg == 'REG_01' else 2)
    if not recq:
        add(o, 'systemic', '', act_of_region(creg), creg, recloc, 'conversation', spk, f'Recruit: {recloc}',
            [f'{nm} at {recloc}; first impression built on a habit: {short} {habit}.', f'{short} sizes up the player and the Shard in their chest.',
             f'What {short} wants, said sideways: {want}.', f'Turn: {short} names the price of joining, and it is not money; it is about {fear}.',
             'PLAYER accepts in a tone; first approval shift.', f'Ostra (stage {st}): {pick(OSTRA_LIVE[st], aid)}'],
            'Plain/Kind/Hard/Sly; approval +/-5 by tone', f'FLG_{c}_RECRUITED', 24, st, 'Recruit scene (02-characters). Design choice flag name.')
    else:
        warn.append(f'{aid} recruit covered by {recq} campaign scenes')
    for thr, ttl in [(25, 'trust'), (50, 'the favor'), (75, 'the last quest')]:
        tb = {25: [f'Approval reaches 25 at a camp or Anchor; {short} brings out {item}.', f'{short} tells the story of {item} in under a minute.',
                   f'{short} {habit} while talking, and the player notices.', f'Turn: the story ends with {short} admitting what they were afraid of: {fear}.',
                   'PLAYER answers; Kind +5, Hard -5.'],
              50: [f'Approval 50: {short} asks a favor, plainly, which costs them something to ask.', f'The favor is about {want}.',
                   f'{short} offers {item} as payment and means it.', 'Turn: the player can refuse the payment; that matters more than the favor.',
                   'Unlocks the companion\'s fourth quest early if not already open.'],
              75: [f'Approval 75: {short} unlocks CMPQ_{c}_05 by saying the thing they have avoided all game.', f'It is about {fear}, and it is specific.',
                   f'{short} gives the player {item} to hold until it is over.', 'Turn: they ask the player not to fix it, only to come along.',
                   'Ostra, if audible to them, says one line of support; otherwise the player hears her alone.']}[thr]
        add(o, 'systemic', f'CMPQ_{c}_05' if thr == 75 else '', '', creg, 'Camp or Anchor', 'conversation', spk, f'CNT_APPROVAL_{c} >= {thr}', tb,
            'Plain/Kind/Hard/Sly', f'FLG_{c}_APPROVAL_{thr}', 16 if thr < 75 else 22, st, f'Approval checkpoint {thr} ({ttl}).')
    add(o, 'systemic', '', '', creg, 'Wherever approval drops', 'conversation', spk, f'CNT_APPROVAL_{c} <= -50',
        [f'{short} packs without saying anything, {habit}.', f'The last thing {short} says names one specific choice the player made.',
         f'{short} leaves {item} behind, or takes it, depending on how bad it got.', 'Turn: the player can ask them to stay; it fails, but it is remembered.',
         'Companion is gone; one gift quest can win them back.'], 'Plain/Kind/Hard/Sly (no effect)', f'FLG_{c}_LEFT', 14, st, 'Leave at -50 (04 section 3).')
    add(o, 'systemic', '', '', creg, 'Their old haunt', 'conversation', spk, f'FLG_{c}_LEFT and gift quest done',
        [f'The player brings back something tied to {want}.', f'{short} looks at it a long time.', f'{short}: one line about {fear}.',
         'Turn: they come back, but approval resets to 0 and they say so.'], 'Kind / Plain', f'FLG_{c}_RETURNED', 12, st, 'Win-back (once).')
    if rom:
        for k, (trg, bb) in enumerate([
            ('Approval 50 and CMPQ_{c}_03 done', [f'Night camp; {short} sits closer than needed.', f'{short} admits the player is the first person they have not lied to about {fear}.',
                                                   'The player can lean in or step back; both are fine.', f'Turn: {short} laughs at their own nerve, {habit}.']),
            ('Approval 75 and romance started', [f'{short} asks what happens to Kindled who love someone who can die.', 'Ostra goes quiet on purpose; the player notices the courtesy.',
                                                 f'{short} offers {item} as a promise.', 'Turn: the player can accept, or say not yet; not yet is honored later.']),
            ('Before MQ_A3_01, romance active', [f'{short} asks the player to come back from the Quiet.', 'The player cannot promise; they say so or lie.',
                                                 f'{short} names the ending they want and admits it is selfish.', 'Turn: the last line is a joke only the two of them get.']),
        ], 1):
            add(o, 'systemic', '', '', creg, 'Camp', 'conversation', spk, trg.format(c=c), bb, 'Lean in / Step back / Not yet', f'FLG_{c}_ROMANCE_{k}', 18, st,
                f'Romance scene {k} (02-characters: Yes).')
    CAT = 'cmp_barks'
    for k, prem in enumerate(BANTER[c], 1):
        add(o, 'systemic', '', '', '', 'Travel', 'conversation', spk, f'Travel banter {k}, idle on the road',
            [prem + '.', 'The player answers in a tone; no approval change unless Hard.', f'{short} {habit}, which is part of the joke or the hurt.',
             'Turn: it ends one line earlier than expected.'], 'Plain/Kind/Hard/Sly', '', 20, st, 'Banter, funny or sad in a specific way.')
    add(o, 'systemic', '', '', '', 'Field', 'bark_set', aid, 'Major choices (Heart Shards, Council, Ires, endings)',
        [f'One reaction per major choice flag, keyed to {short}\'s ending lean ({lean}).', 'Approve, disapprove and silent variants.',
         f'{short} names the cost of the choice, never the rule.', 'Turn: a reaction set changes after CMPQ_{c}_05 resolves.'.format(c=c)],
        '', '', 40, st, 'Choice reactions.')
    CAT = 'cmp_barks'
    add(o, 'systemic', '', '', '', 'Field', 'bark_set', aid, 'Combat',
        [f'Combat barks for {short}: spot, flank, hurt, revive player, low health, kill, boss.', f'Voice built on the habit: {habit}.',
         'Four lines per category minimum; see barks.csv for player tone format.', 'Turn: one line per category only plays at approval 75+.'],
        '', '', 120, st, 'vo_budget: 120 combat per companion.')
    for ar in AREAS:
        add(o, 'systemic', '', '', ar, REGION[ar], 'bark_set', aid, f'Exploring {REGION[ar]}',
            [f'{short} comments on places in {REGION[ar]}; 40 lines, 4 samples in barks.csv.', f'Lines tie the area to {want} or {fear}.',
             'No line repeats a place name the HUD already shows.', pick(['Two lines in forty only play at night.', 'One line in ten is a callback to a past choice.',
                                                                         'Three lines change if the region\'s Heart was taken.', 'Lines get shorter the more Hollowed the area is.'], aid + ar)],
            '', '', 40, 4 if ar == 'REG_Q' else (1 if ar == 'REG_01' else 2), 'Region barks (campaign plan 40 per region).')
    add(o, 'systemic', '', 'END', '', 'Epilogue', 'cinematic', aid, 'Epilogue companion slide',
        [f'Voice line over slide EPI_{aid}_LOYAL, _NEUTRAL or _GONE (endings.csv).', f'Loyal: {short} says where they ended up, tied to {want}.',
         f'Neutral: {short} mentions the player once, in passing.', 'Gone: no voice; another character says what became of them.'],
        '', '', 6, 4, 'Ending slide line, three variants.')
    CAT = 'cmp_reactions'
    add(o, 'systemic', '', '', '', 'Field', 'bark_set', aid, 'Every quest completion and key quest beat',
        [f'Quest reactions for {short}: about 4 lines per quest, {len(quests)} quests.', f'Each reaction ties the quest to {want} or {fear}.',
         'Approve, disapprove and quiet variants; lines never summarize the quest.', 'Turn: reactions to Ostra change after MQ_A2_06 (only Hal and Unit 9 address her).'],
        '', '', 4 * max(1, len(quests)), st, 'vo_budget: quest reactions 4 x quests.')
    CAT = 'cmp_scenes'

# ---------------------------------------------------------------- faction leaders
CAT = 'faction_scenes'
JOIN_FLAG = {'HULLKNIGHTS': 'FLG_HK_JOINED', 'LANTERNCHURCH': 'FLG_JOINED_LANTERNCHURCH', 'SALVAGERS': 'FLG_SG_JOINED',
             'QUIETHAND': 'FLG_QH_JOINED', 'CHOIR': 'FLG_CH_JOINED'}   # design/campaign/flags.csv
FACT = [
    ('HULLKNIGHTS', 'HK', 'ACT_NPC_HULLKNIGHT_COMMANDER', 'Iselde Marr', 'the Knights\' Gate', 'a Knight\'s post on the gate roster', 'clipped, ranks, "on the deck"'),
    ('LANTERNCHURCH', 'LC', 'ACT_NPC_LANTERN_ARCHIVIST', 'Archivist Hale', 'the Log Chapel', 'a reader\'s seat at the Log terminal', 'warm, quotes the Log, ends with "Logged."'),
    ('SALVAGERS', 'SG', 'ACT_NPC_SALVAGER_BOSS', 'Petra Quell', 'the Undermarket', 'a Guild salvage stamp', 'fast, prices in every line'),
    ('QUIETHAND', 'QH', 'ACT_NPC_QUIETHAND_SPEAKER', 'the Speaker', 'the Still Room', 'a black contract seal', 'few words, second person'),
    ('CHOIR', 'CH', 'ACT_NPC_CHOIR_PRECENTOR', 'Precentor Lisk', 'the Choir Spire', 'a tuning stone', 'tone, pitch, rest; gentle'),
]
up_tiers = [t for t in tiers if int(t['Min']) >= 500]
for fac, code, lid, lname, hall, token, voice in FACT:
    o = f'FAC_{fac}'
    join_q = f'QST_{code}_00' if f'QST_{code}_00' in quests else ''
    add(o, 'systemic', join_q, '1', 'REG_HUB', hall, 'conversation', f'{lid}; PLAYER', f'FAC_{fac} Neutral and join offer accepted',
        [f'{lname} at {hall}; voice: {voice}.', f'{lname} gives the player {token} and explains what it costs to carry.',
         'One rule of the faction, stated as a fact of daily life.', f'Turn: {lname} names what the faction wants from a Kindled specifically.',
         'Join confirmed; rivalry note if Choir or Church.'], 'Join / Not yet; Plain/Kind/Hard/Sly', JOIN_FLAG[fac], 24, 1, 'Faction join (reputation_tiers: Neutral, join quest available).')
    for t in up_tiers:
        add(o, 'systemic', '', '', 'REG_HUB', hall, 'conversation', f'{lid}; PLAYER', f'FAC_{fac} reaches {t["Tier"]}',
            [f'{lname} calls the player in at {hall}.', f'What it unlocks, in {lname}\'s words: {t["Unlocks"]}.',
             pick([f'{lname} admits something about the faction they would not have said at the last rank.', f'{lname} gives a small gift tied to {token}.',
                   f'{lname} asks the player\'s opinion and actually listens.', f'{lname} complains about another Council member, specifically.'], o + t['Tier']),
             f'Turn: at {t["Tier"]}, {lname} {pick(["asks for something harder", "lets slip a faction secret", "treats the player as one of their own for the first time", "warns the player about the Council"], o + t["Tier"] + "x")}.'],
            'Plain/Kind/Hard/Sly', '', 12 if t['Tier'] != 'Sworn' else 20, 2, f'Rank-up {t["REP_ID"]}.')
add('FAC_LANTERNCHURCH', 'systemic', 'QST_CH_00', '1', 'REG_HUB', 'the Log Chapel', 'conversation', 'ACT_NPC_LANTERN_ARCHIVIST; PLAYER; ACT_CMP_C2',
    'Player joins the Choir (QST_CH_00 complete)', ['Hale closes the Chapel archive door gently, not angrily.', 'He returns the player\'s reader\'s seat token.',
    'Odo, if present, loses 20 approval and says why in one sentence.', 'Turn: Hale says he will still pray for the player, and he means it.'], '', 'FAC_LANTERNCHURCH closed', 10, 1, 'Rival closed (04 section 3).')
add('FAC_CHOIR', 'systemic', 'QST_LC_00', '1', 'REG_HUB', 'the Choir Spire', 'conversation', 'ACT_NPC_CHOIR_PRECENTOR; PLAYER',
    'Player joins the Lantern Church (QST_LC_00 complete)', ['Lisk meets the player on the Spire stair, out of breath.', 'He takes back the tuning stone, apologizing.',
    'He says the star will still listen to the player; he means it kindly.', 'Turn: he asks the player to keep the lens view secret anyway.'], '', 'FAC_CHOIR closed', 10, 1, 'Rival closed.')

# ---------------------------------------------------------------- vendors
CAT = 'vendors'
VPERS = {'ITM_VEN_QUARTERMASTER': 'a retired Knight who counts everything twice', 'ITM_VEN_ARMORER': 'deaf in one ear from the forge; talks while hammering',
         'ITM_VEN_APOTHECARY': 'tastes every Tonic first and reviews it', 'ITM_VEN_TINKER': 'Salvager, puts a price in every sentence',
         'ITM_VEN_ARCHIVIST': 'Choir archivist who hears the Shards she sells', 'ITM_VEN_CLOTHIER': 'trades comms (gossip) with every sale',
         'ITM_VEN_SEALS': 'formal; Seals are weekly tokens and she treats them like vows',
         'ITM_VEN_FENCE_HUB_01': 'Lantern Hold fence in the lower stalls; never asks where a thing came from and never forgets either',
         'ITM_VEN_FENCE_HUB_02': 'Lantern Hold fence on the dock stairs; prices by weight, talks by the hour, pays in loose Ember'}
seen = []
for v in vendor_rows:
    if v['vendor_id'] not in seen:
        seen.append(v['vendor_id'])
vmeta = {}
for v in vendor_rows:
    vmeta.setdefault(v['vendor_id'], (v['vendor_name'], v['location'], v.get('restock_game_h', '')))
for vid in seen:
    vname, vloc, rh = vmeta[vid]
    reg = vloc.split('LOC_TOWN_')[-1][:6] if 'TOWN' in vloc else 'REG_HUB'
    pers = VPERS.get(vid, f'{REGION.get(reg, "")} trader in {place_of(vloc)}; uses the regional saying "{SAYING.get(reg, "")}"')
    o = 'VEN_' + vid.replace('ITM_VEN_', '')
    act_id = 'ACT_NPC_VEN_' + vid.replace('ITM_VEN_', '')
    for setn, ln, bb in [('greet', 12, ['First visit greeting, then repeat-visit variants.', 'One line per rep tier with the vendor\'s faction where relevant.', 'One line reacts to the player\'s chest Shard glow.']),
                         ('buy', 8, ['Lines on purchase; cheap and expensive variants.', 'One line when the player buys the last of something.', 'One line when the player cannot afford it.']),
                         ('sell', 8, ['Lines when the player sells; junk versus Meridian parts.', 'One line when the player sells something the vendor sold them.', 'One line for selling a lore item (vendor reads a word of it).']),
                         ('leave', 7, ['Goodbye variants by time of day.', 'One line if the player bought nothing.', 'One line after the world-state changes (Heart choice in this region).']),
                         ('restock', 5, [f'Lines when stock refreshes (restock every {rh or "?"} game hours).', 'One line if the player arrives right after restock.', 'One line naming where the new stock came from.'])]:
        add(o, 'systemic', '', act_of_region(reg), reg, place_of(vloc), 'bark_set', act_id, f'Vendor {setn}',
            [f'{vname}: {pers}.'] + bb + [f'Turn: one rare line (1 in 20) in the {setn} set tells a piece of the vendor\'s own life.'], '', '', ln, stage_of('', act_of_region(reg), reg),
            f'Vendor set {setn} ({vid}).')

# ---------------------------------------------------------------- town ambient
CAT = 'town'
TOPICS = {
    'REG_01': ['a potter arguing over kiln time', 'children counting embers on the ridge', 'a widow selling ash-baked bread', 'miners comparing coughs', 'someone repainting a hull-plate house sign'],
    'REG_02': ['net menders betting on the tide', 'a smuggler pretending to be a fisher', 'two sailors arguing about a wreck they both claim', 'a girl ringing the dusk bell too early', 'salt fish traders haggling'],
    'REG_03': ['herbalists arguing about rot', 'a Thorn cousin trading insults at a stall', 'a beekeeper with a sting she is proud of', 'foresters measuring a root that grew overnight', 'a family feud conducted politely'],
    'REG_04': ['caravaners settling a water debt', 'a glassblower selling windows nobody can afford', 'kids racing drone parts', 'a grandmother rationing cactus water', 'two traders swearing on water'],
    'REG_05': ['herders waiting for the thaw', 'monks counting breaths', 'someone checking an ice pod for a cousin', 'sledge drivers trading routes', 'a baker with tuber bread and opinions'],
    'REG_06': ['lamp crew children reciting names', 'an old man saying his name every morning, loudly', 'a widow leaving food for a Hollowed husband', 'carters who forget their routes', 'a woman writing her name on her hand'],
    'REG_HUB': ['Knights drilling recruits', 'a Church reader practicing the Fall Day page', 'Guild auctioneers', 'Choir students tuning stones', 'a clerk running late for the Council'],
}
settle = [l['loc_id'] for l in locs if l['kind'] in ('Settlement',)]
for lid in settle:
    reg = lid[9:15]
    nm = place_of(lid)
    o = 'TOWN_' + lid.replace('LOC_TOWN_', '')
    sp = f'ACT_NPC_TOWNSFOLK_{lid.replace("LOC_TOWN_", "")}'
    named = lid.endswith('_01')
    sets = [('day chatter', 160), ('world state', 100), ('night chatter', 100)]
    for sn, ln in sets:
        tp = picks(TOPICS[reg], lid + sn, 3)
        bb = [f'{nm}, {sn}: overheard, never addressed to the player unless they stop.', f'Topics: {tp[0]}; {tp[1]}; {tp[2]}.',
              f'Saying, once per loop: "{SAYING[reg]}"']
        if sn == 'world state':
            bb += [f'Variants by Heart Shard choice for {REGION[reg]} (spared: recovery talk; taken: greying talk) and by act.',
                   'Turn: after MQ_A2_07, one NPC repeats what the player told the Council, wrong.']
        elif sn == 'night chatter':
            bb += ['Fewer voices, closer; one argument behind a door.', 'Turn: someone names the dead at a lamp (Lighting Night custom).']
        else:
            bb += ['Twelve lines per NPC; thirty NPC voices in named towns, fifteen elsewhere.', 'Turn: one NPC recognizes the player from a quest and says so.']
        add(o, 'systemic', '', act_of_region(reg), reg, nm, 'ambient', sp, f'Player in {nm}', bb, '', '', ln, stage_of('', act_of_region(reg), reg),
            f'Town ambient ({sn}). Speaker group ID is a request.')
for tier, topic in [('Bridge Deck', 'Council aides and petitioners'), ('Knights\' Gate', 'recruits and gate checks'), ('Log Chapel', 'readers and mourners'),
                    ('Choir Spire', 'students and lens keepers'), ('Undermarket', 'traders and boat hands'), ('the Cradle', 'riggers and Guild crew')]:
    add('TOWN_HUB', 'systemic', '', '1', 'REG_HUB', f'Lantern Hold: {tier}', 'ambient', f'ACT_NPC_TOWNSFOLK_HUB_{h(tier) % 90 + 10}',
        f'Player on {tier}', [f'{tier}: {topic}.', f'Topics: {"; ".join(picks(TOPICS["REG_HUB"], tier, 2))}.', 'Saying once: "The Hold holds."',
                               f'Turn: on {tier}, one line changes after each act transition.'], '', '', 60, 1, 'Hub ambient tier.')
add('TOWN_HUB', 'systemic', 'MQ_A2_07', '2', 'REG_HUB', 'Lantern Hold', 'ambient', 'ACT_NPC_TOWNSFOLK_HUB_ALL', 'After MQ_A2_07',
    ['The Hold reacts to the Council report.', 'FLG_TRUTH_TOLD: people spit, pray, argue; a Church schism song.', 'FLG_TRUTH_HIDDEN: nothing changes, which is its own sting.',
     'Turn: one child asks the player if the ship is sorry.'], '', '', 60, 3, 'Hub reactive.')
add('TOWN_HUB', 'systemic', '', 'post', 'REG_HUB', 'Lantern Hold', 'ambient', 'ACT_NPC_TOWNSFOLK_HUB_ALL', 'Post-game after any ending',
    ['Restore: talk of the ship, navy drills, Rites failing.', 'Bind: the player is a Weave echo; people pray near them.', 'Take: people look up before they speak.',
     'Turn: one NPC thanks the player for the wrong thing.'], '', '', 60, 4, 'Hub post-ending.')

# ---------------------------------------------------------------- Echo summon
CAT = 'echo'
for sn, bb in [('summon', ['Echo Lantern lit; the Echo arrives as a Weave recording of a Kindled.', 'Three voice variants (design choice).', 'Lines are the Echo\'s last day, replayed.', 'Turn: one line in ten is addressed to someone else.']),
               ('fight', ['Combat lines from the recording; it does not quite hear the player.', 'Callouts lag by a beat, like a recording should.', 'One line per enemy faction.', 'Turn: it warns about an attack that already happened.']),
               ('boss', ['Boss arena lines; the Echo remembers fighting something like this.', 'One line names a boss it cannot have met.', 'Ostra comments on the Echo once.', 'Turn: if the boss dies, the Echo says thank you to nobody.']),
               ('fade', ['Echo fades at low HP or fight end.', 'Last line is ordinary: a meal, a name, the weather.', 'Church NPCs nearby react if they saw it (02-world-life 5).', 'Turn: the last word is sometimes the player\'s name.'])]:
    add('ECHO', 'systemic', '', '', '', 'Any', 'echo', 'ACT_NPC_ECHO', f'Echo {sn}', bb, '', '', 20, 2, f'Echo summon set {sn} (FRM_ECHO).')

# ---------------------------------------------------------------- Ostra and player systemic sets, enemy bark sets
CAT = 'ostra_sys'
for title, ln, stg, bb in [
    ('Lore item comments: ship logs', 140, 2, ['Ostra comments on each ship log picked up.', 'She knows most crew by name and berth.', 'Removed entries: she says nothing, then "Misfiled."', 'Turn: after MQ_A2_06 she reads the restored ones herself.']),
    ('Lore item comments: letters', 120, 2, ['Comments on Veyl letters of 900 AF.', 'She is curious about people she never carried.', 'One line per letter, specific to its want.', 'Turn: some letters mention the player by rumor.']),
    ('Lore item comments: relics', 80, 2, ['Comments on things made from ship parts.', 'She names the original part.', 'Pride, then something else.', 'Turn: one relic is made from her own housing.']),
    ('Lore item comments: keys', 60, 2, ['Comments on keys and what they open.', 'Dry, short.', 'She guesses wrong about one door on purpose, as a joke.', 'Turn: one key opens a berth she remembers.']),
    ('Boss and site comments', 500, 2, ['Ostra on every boss and site arrival, one to three lines each.', 'Act 1: confident identifications; later: guilt where she built the thing.', 'Never repeats the HUD name.', 'Turn: after MQ_A2_06 she apologizes to two of them.']),
    ('Hints', 900, 1, ['Hint lines for combat, Rites, Anchors, crafting, traversal, map.', 'Stage-voiced; Act 1 confident, later warmer.', 'Colder variants after the Anchor confrontation (UI color shift).', 'Turn: hints vanish during MQ_A2_07.']),
    ('NG+ foreshadowing', 300, 4, ['NG+ only: she remembers this.', '"I remember this. I remember lying to you here."', 'Lines keyed to each Act 1 wrong line.', 'Turn: she warns the player before the opening prompts.']),
] + [(f'Region arrival: {REGION[a]}', 100, 4 if a == 'REG_Q' else (1 if a == 'REG_01' else 2),
      [f'First arrival and returns to {REGION[a]}.', 'She names the crash debris she can see.', 'Lines keyed to the Relay Tower being lit or not.', 'Turn: one line changes after the region\'s Heart choice.']) for a in AREAS]:
    add('OSTRA', 'writing', '', '', '', 'Any', 'bark_set', 'ACT_NPC_OSTRA', title, bb, '', '', ln, stg, title + ' (vo_budget Ostra line).')
CAT = 'player_barks'
for vs in 'AB':
    add('PLAYER', 'writing', '', '', '', 'Any', 'bark_set', 'PLAYER', f'Voice set {vs}: combat barks',
        [f'Voice set {vs}: 20 categories, 900 lines total (target counts in barks.csv).', 'Four tones where relevant: Plain, Kind, Hard, Sly.', '2 to 8 words each.',
         'Turn: tone of the last dialogue choice biases which bark plays (design choice).'], '', '', 900, 1, 'Player combat barks.')
    add('PLAYER', 'writing', '', '', '', 'Any', 'bark_set', 'PLAYER', f'Voice set {vs}: reactions',
        [f'Voice set {vs}: reactions to loot, lore, places, Ostra.', 'Short replies to Ostra lines (she talks, the player answers).', 'Four tones.',
         'Turn: after MQ_A2_06, reactions to Ostra shift by FLG_OSTRA_FORGIVEN.'], '', '', 600, 1, 'Player reactions.')
CAT = 'enemy'
for fac in ['HOLLOWED', 'REMNANT', 'THORN', 'CHOIRBORN']:
    for role in ['FODDER', 'SHIELDBEARER', 'SKIRMISHER', 'ARTILLERY', 'HEAVY', 'LEADER']:
        add(f'BARK_{fac}', 'writing', '', '', '', 'Field', 'bark_set', f'ACT_{fac}_{role}' if role != 'LEADER' else f'ACT_{fac}_LEADER',
            f'{fac.title()} {role.lower()} in combat', [f'{fac.title()} {role.lower()}: 10 categories, 40 written lines, recorded by 3 voices.',
                                                       'Faction voice per style guide section 4.', 'Samples in barks.csv (STR_BARK_*).', 'Turn: leader-down lines break morale differently per faction.'],
            '', '', 120, 2, 'Enemy barks; LEADER squad role (ACT_<FAC>_LEADER, used by campaign scenes).')


# ---------------------------------------------------------------- budget categories from vo_budget.csv not covered above
CAT = 'cmp_pairs'
ck = list(COMP)
for i in range(len(ck)):
    for j in range(i + 1, len(ck)):
        a_, b_ = ck[i], ck[j]
        A, B = COMP[a_], COMP[b_]
        sa, sb = NAMES[f'ACT_CMP_{a_}'], NAMES[f'ACT_CMP_{b_}']
        hook = pick([f'{sa} catches {sb} doing the thing they always do ({B[2]})', f'{sb} asks {sa} about {A[5]}',
                     f'{sa} and {sb} argue over who gets the dry bunk', f'{sb} bets {sa} cannot go a day without their habit ({A[2]})',
                     f'{sa} offers to trade {A[5]} for {B[5]}, half joking', f'{sb} finds out what {sa} fears most: {A[4]}'], a_ + b_)
        add('CMP_PAIRS', 'systemic', '', '', 'REG_HUB', 'Lantern Hold: companions\' camp under the Cradle', 'conversation', f'ACT_CMP_{a_}; ACT_CMP_{b_}',
            f'Both recruited; both resting at the Hold camp',
            [f'Camp at the Hold; {sa} and {sb} share a fire while the player is in earshot.', cap(hook) + '.',
             f'{sb} answers from their own want: {B[3]}.', f'Turn: {sa} admits wanting the same thing, put another way: {A[3]}.',
             pick(['The player can join in or walk past; walking past plays a shorter version.', 'Ostra comments to the player only.',
                   'It ends when one of them falls asleep.', 'Someone at the next fire tells them to be quiet.'], b_ + a_)],
            'Join (Plain/Kind/Hard/Sly) / Walk past', '', 30, 2, 'vo_budget: companion-to-companion banter (camp only; one companion in the field at a time).')
CAT = 'leader_react'
for fac, code, lid, lname, hall, token, voice in FACT:
    add(f'FAC_{fac}', 'systemic', '', '', 'REG_HUB', hall, 'bark_set', lid, 'Hub milestones: each main-quest act beat and major choice',
        [f'{lname} reacts in passing to main-quest milestones ({voice}).', 'Lines for Heart Shard counts, FLG_TRUTH_TOLD or HIDDEN, Ires outcome, launch.',
         f'At least one line per milestone that only makes sense if the player joined FAC_{fac}.', 'Turn: after MQ_A2_07 the lines get shorter or warmer, by flag.'],
        '', '', 40, 2, 'vo_budget: faction leader hub reactions 40 each.')
CAT = 'hush_sys'
for ar in ['REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06', 'REG_U', 'REG_Q']:
    add('HUSH', 'writing', '', act_of_region(ar), ar, REGION[ar], 'bark_set', 'ACT_BOSS_HUSH; ACT_HOLLOWED_FODDER', f'Hollowed whispers in {REGION[ar]}',
        [f'Hush speaks through Hollowed mouths in {REGION[ar]}, in the voice of the person each Hollowed was.', 'Every line is true; none is a threat.',
         'Lines thank, count, or describe the weather of the harvest.', pick(['Turn: one whisper uses the player\'s Origin trade.', 'Turn: one whisper repeats something the player said in a scene.',
                                                                              'Turn: one whisper is addressed to Ostra by ship designation.', 'Turn: one whisper apologizes for the smell.'], ar)],
        '', '', 75, 4 if ar == 'REG_Q' else 2, 'vo_budget: Hush whispers (towers and boss lines live in quest scenes).')
CAT = 'radiant'
for rt in rd(os.path.join(CAMP, 'radiant_templates.csv')):
    tw = [t.strip() for t in (rt.get('twists') or '').split(';') if t.strip()]
    lpi = int(rt.get('lines_per_instance') or 12)
    add(f"RAD_{rt['rad_id'].replace('RAD_', '')}", 'systemic', rt['rad_id'], '', '', (rt.get('giver_pool') or '').split(';')[0].split(' (')[0][:60], 'conversation',
        'ACT_NPC_RADIANT_GIVER; PLAYER', f"Radiant {rt.get('name', '')} offered",
        [f"Giver from the pool reads the notice in their own regional voice: {rt.get('name', '')}.", f"Target slot: {(rt.get('target_pool') or '').split(';')[0]}.",
         f"Twist (one of {len(tw)}): {tw[0] if tw else 'none'}", f"Turn-in: the giver's small personal want pays off or does not ({rt.get('reward_rule', '')}).",
         'Ostra one-liner keyed to the twist.'], 'Plain/Kind/Hard/Sly', '', 25 * lpi, 2, f"vo_budget: 25 instances x {lpi} lines; template {rt['rad_id']}.")
CAT = 'epilogue'
grp = collections.defaultdict(list)
for e in endings:
    grp[e.get('ending', 'Any')].append(e)
for en, es in grp.items():
    kinds = sorted({e.get('kind', '') for e in es})
    add('EPILOGUE', 'writing', {'Restore': 'MQ_END_R', 'Bind': 'MQ_END_B', 'Take': 'MQ_END_T'}.get(en, ''), 'END', '', 'Epilogue slides', 'cinematic', 'ACT_NPC_LANTERN_ARCHIVIST',
        f'Epilogue slides, ending: {en}', [f'{len(es)} slides for {en} ({", ".join(kinds)}), endings.csv.', 'Hale reads each slide as a new Log entry (design choice), ending "Logged."',
                                           'Narration fits narration_seconds per slide.', f'Turn: the last {en} slide carries the ending cost (05-story-pass F).'],
        '', '', len(es), 4, 'vo_budget: epilogue narration. Narrator choice is a Shardfall design choice.')
CAT = 'lore_read'
for lt, n in [('ship logs', 140), ('letters', 120), ('relics', 80), ('keys', 60)]:
    add('LORE', 'writing', '', '', '', 'Any', 'bark_set', 'ACT_NPC_LORE_READERS', f'Lore item read aloud: {lt}',
        [f'{n} {lt} read aloud on pickup (ITM_LOR_*).', 'Crew voices for logs; 900 AF villagers for letters; museum voice for relics.',
         'Removed log entries read only the time stamp until MQ_A2_06.', 'Turn: one reader per region is the same voice as a quest NPC (family line).'],
        '', '', n, 2, 'vo_budget: lore readings.')
CAT = 'branch'
BR_OPEN = ['Right after the choice ({c}), {g} reacts first.', 'The player has chosen: {c}. {g} takes a second to answer.', '{g} sees what the player did ({c}).',
           'Choice made: {c}. {g} does not hide what they think.', 'Outcome scene for "{c}"; {g} speaks before anyone else.', 'The player commits ({c}); {g} goes still, then talks.',
           '{g} hears the decision ({c}) and puts down whatever they were holding.', 'It is done: {c}. {g} looks at the player a long moment.',
           'As soon as the player acts ({c}), {g} starts talking fast.', '{g} was hoping for something else than this: {c}.',
           'No going back from "{c}"; {g} says so first.', 'After "{c}", {g} laughs once, not happily.']
for qid in sorted(branches, key=quest_order_key):
    q = quests.get(qid, {})
    region = q.get('region', '')
    act = q.get('act', '') or act_of_region(region)
    stg = stage_of(qid, act, region)
    giver = q.get('giver', '') or 'PLAYER'
    for b in branches[qid]:
        outs = sentences(b.get('outcome', '')) or [b.get('outcome', '') or 'The world notes it.']
        apr = b.get('approval', '')
        g = name_of(giver)
        bb = [pick(BR_OPEN, b['branch_id']).format(c=b['choice'].rstrip('.'), g=g), endp(outs[0])]
        if apr:
            bb.append(f'Companions react on the spot ({apr}).')
        bb.append(ostra_line(stg, b['branch_id'], b.get('outcome', '')))
        bb.append(pick(TURN, b['branch_id'] + 't').format(s=endp(outs[1]) if len(outs) > 1 else
                  pick(['nobody thanks the player, and that is the point.', 'the small want at the heart of the quest is met, or visibly not.',
                        'someone the player did not notice was watching.', 'the cost shows up one scene later, not now.'], b['branch_id'])))
        sp = '; '.join([x for x in [giver if giver != 'PLAYER' else '', 'PLAYER', 'ACT_NPC_OSTRA'] if x] + (['ACT_CMP_ACTIVE'] if apr else []))
        add(qid, 'campaign', qid, act, region, place_of((q.get('locations', '') or '').split(';')[0].strip()), 'conversation', sp,
            f"Branch {b['branch_id']} chosen", bb, branch_text(b), b.get('flags_set', ''), 14, stg, f"Branch outcome dialogue ({b['branch_id']}); vo_budget about 14 lines each.")
CAT = 'other'

# ---------------------------------------------------------------- cinematics
CB = {
 'CIN_OPEN': ('Black screen; a calm ship alarm counts down / Through frosted Bay 9 glass: crew running past, red-lit / Bridge audio only: a hail in a voice that is many voices / Ires, tired: "Accept." / PLAYABLE 90 s: amber prompts on the cracked glass, "Seal bulkheads", "Vent core coolant", "Override bridge command"; the player obeys / A woman says "Belay that" and is cut off; the score reads 100% / White. Title: 900 AF / Same glass, furred with frost; a crowbar bites the seal / Old Tomas, breath steaming: "Another one. Breathing, too." / The scanner sweep becomes the creation screen', 'MUS_CIN_OPEN: ship alarm pulse as the scale, low strings; Ostra motif in broken fragments under the prompts'),
 'CIN_HUB_ARRIVE': ('The road crests the crater rim at wake-call / Lantern Hold: the Meridian\'s bridge on its nose in the lake / Tomas names each tier as they cross the causeway: Gate, Chapel, Spire, Undermarket / Kessa, if present, straightens her upside-down badge and then leaves it / Knights check the player\'s hands for Shard light / The Bridge Deck lights come on; Ostra, first word since the road: "Mine." / Bell for the Council', 'MUS_CIN_HUB: hub theme on brass, a deckfiddle under it'),
 'CIN_SECOND_STAR': ('The lens irises open; violet Weave threads cross the stars / One star moves against the others / Zoom: a dark ring, kilometers across, too regular / Lisk, breathless with wonder / Ostra\'s voice breaks into fragments and ship alarms only the player hears / The player snaps the shutter closed / Lisk asks if they heard it too', 'MUS_CIN_STAR: Choir theme, one held note that bends flat'),
 'CIN_ACT1_END': ('The storm breaks after Corsa\'s fall; the sea goes flat as glass / Shards lift out of the water in a column, slow, like snow falling up / Stiltmarket on the wall; Moss takes off his cap / On the cliff: a lamplighter figure (Ires, unnamed, masked) lifts a Shard to the sky as the column rises / The tide turns grey behind it / Ostra: "I know that ship." / The column bends toward one star / Title: The Four Hearts', 'MUS_CIN_ACT1_END: Saltmere theme slowed, then the Quiet motif in a low drone'),
 'CIN_MUTINY': ('Core housing in the Undervault: the memory Shard placed in its old socket / The bridge, 0 AF, from Ostra\'s point of view: forty minutes compressed / The hail; Hush\'s offer in "we": dock, hand over the core, sleepers set down safely / Ires: "Accept." / Ostra runs the numbers on screen: Hush takes core and sleepers both / Ostra locks the captain out; Ires pounds the console / The opening prompts replay with their true labels; the player\'s own inputs, their real timing / Bridge lockout, coolant vented, command removed / The Meridian dives; the core overloads; the ship breaks in three / A pod counter runs down from 41,000 to 4,000 / Back in the Undervault: Ostra\'s voice, stage 3: "I had the numbers." / Silence', 'MUS_CIN_MUTINY: Ostra motif played whole for the first time, then cut to room tone'),
 'CIN_ACT2_END': ('The patched shuttle rolls out of the Cradle; two Heart Shards burn in the power cradle / Every Hold tier is lit; people on rooftops / Quell crosses her fingers behind her back; Marr salutes / The active companion at the door controls / Lift-off through the violet threads / Lisk at the door controls, hand on the lever / Cut to black on the lever moving', 'MUS_CIN_ACT2_END: all faction themes stacked, then everything drops but one Choir note'),
 'CIN_END_R': ('The Quiet descends slow and heavy over the crater lake / It docks against Lantern Hold; the bridge is a bridge again / Sleepers wake in the Undervault and, if thawed, in Rimefall / Ostra\'s voice gives docking status and nothing else; the player notices / Ires, if ally, takes the captain\'s chair and does not sit / Cost: the Weave thins; a Choir student\'s tuning stone goes silent in her hand / Epilogue slides (endings.csv): Weave fading over thirty years, Petra\'s ship, the Knights as a navy / Last slide: Ostra\'s line, as a ship, not a friend', 'MUS_CIN_END_R: Meridian theme on full orchestra, Ostra motif absent at the end'),
 'CIN_END_B': ('The Quiet burns across the sky like a second sun / It breaks apart over the sea / Stolen land settles back into each region; green comes first where Hearts were spared / Hale reads the Log\'s new last entry in the Chapel, shaped by the player\'s final tone / A Weave echo of the player watches from the back / Epilogue slides per region and companion / Cost sting: three thousand years later, one new light in the sky / Last slide: Ostra, Bind line', 'MUS_CIN_END_B: Church hymn in ship alarm scale, resolving for the first time'),
 'CIN_END_T': ('The lens turns; the Hold Council looks up into it / Hush\'s voice and the player\'s, alternating, then one / Veyl goes on under a god in the sky; the Choir becomes its priesthood / Lisk\'s ghost refuses to serve, if FLG_LISK_REDEEMED / Ostra in her one small cold room / Epilogue slides / Post-credits: the Speaker seals a black contract addressed to the player; Vey takes it / Final slide: the player, as the Quiet, is glad someone took it', 'MUS_CIN_END_T: Quiet motif becomes a lullaby; one voice too many'),
}
MEM = {1: 'a contact where no ship should be; a calm "we" hails; Ostra reads the signal strength; cut before anyone answers',
       2: 'Corsa presents an escape heading Ostra plotted; the captain turns it down off-screen; Ostra recalculates',
       3: 'the hydroponics comm goes live; Ires says "Yes."; plants shiver at the Weave\'s first touch',
       4: 'Brannoch\'s detail runs for the bridge on the captain\'s order; the doors seal in their faces; who sealed them is not shown',
       5: 'pod power drops row by row; Rime counts aloud; Ostra\'s log counts with her in the same voice',
       6: 'Ada and Ennis watch something read the ship\'s mind through the channel; Ostra orders a file deleted; delete confirm'}
CIN_ROWS = []
master = rd(os.path.join(ROOT, 'design', 'cinematics', 'cinematics.csv'))
shots = collections.defaultdict(list)
for sh in rd(os.path.join(ROOT, 'design', 'cinematics', 'shots.csv')):
    shots[sh['cin_id']].append(sh)
EXTRA_CB = {
 'CIN_ACT1_TITLE': ('The lower Spinegate door grinds open on smoke / Cinderreach from the spine: burnt hills, Kiln smoke on the ridge / Tomas points the way down and stays behind / Ostra, over the wide shot, stage 1: a confident wrong line about the crash ("Reactor fatigue. I logged it.") / The player steps out; armor and Tomas\'s son\'s coat visible / Title: Act One, Ember and Salt', ''),
 'CIN_COUNCIL_VOTE': ('Imre lays six stones on the table, two dark / Marr, Hale, Quell and Lisk vote in turn, each in one line of their own voice / The Speaker\'s candle gutters; Imre records it as a yes / The map table lights four regions / Ostra: "Four hearts. They are not hearts. They are fuel cells." / Nobody asks the player; the vote was about them / Title: Act Two, The Four Hearts', ''),
 'CIN_LAMPLIGHTER_UNMASK': ('The Lamplighter at 30% HP, back to the lamp shaft / Her mask cracks down the middle / A Meridian captain\'s insignia under the soot / Ostra: nine seconds of nothing / "Rank: captain." / She drops into the dark shaft; Bea\'s lamps flicker in sequence behind her', ''),
 'CIN_OSTRA_STOP': ('An Anchor at night; the chest Shard warms without the player touching it / Ostra asks to talk, the first time she has asked / She recites all six lucid lines in order, perfectly / "You are collecting them like evidence. Stop. Please." / She admits she knows what is in the Undervault / The player answers; the Anchor light steadies', ''),
 'CIN_OSTRA_RETURN': ('Night after the Council; the HUD has been empty all quest / The chest Shard warms; one hint flickers back / Ostra: "You should have left me in the dark." / Short pieces; she heard everything the player said / The player can forgive her; she logs it without accepting it / The map starts updating again, one tile at a time', ''),
 'CIN_IRES_TOWER': ('Hollowdeep lamp tower; Shards in crates labeled like grain / Ires unmasked, making tea for two / She knows who the player carries / "Hello, ship." "Hello, Captain." / Ostra and Ires argue the numbers; Ostra admits the thirty-seven thousand out loud / Ires: "It wants you more than it wants me."', ''),
 'CIN_IRES_PARTING': ('Outcome by branch: attack, release or a way out / Attack: she does not draw; she breaks a Shard and rises up the Weave / Release: she bows to Ostra and walks into the grey / Offer: she puts the tower lamp out with her own hand / Ostra keeps the captain\'s log open a second too long / The tower goes dark', ''),
 'CIN_BETRAYAL': ('The Cradle doors, launch alarms counting / Lisk at the controls, hand on the lever / Not redeemed: he opens the doors, kindly, and Choirborn pour in / Redeemed: he confesses and seals himself outside with them / The active companion braces the inner door and asks the player to carry one message / Approval 50+ promise, or no promise / The door closes; the shuttle clears the crater damaged', ''),
 'CIN_RING_CRASH': ('The shuttle hits the Threshing Ring and slides / Low gravity: debris drifts upward and stays / Ostra checks the player\'s vitals, then the hull, in full sentences / Choirborn racks in rows, every face asleep / A Choirborn wakes and asks to hear its name / The Maker terminal glows at the end of the ring', ''),
 'CIN_HUSH_SPEAKS': ('Hush, face to face, through a Choirborn wearing a face the player knows (Old Tomas) / "Hello again, ship." / It calls Ostra "the one who spoiled the crop" / Ostra argues; Hush agrees with every true thing she says / "We did not wake you. We let her wake you. You were always coming here." / The ignition shard in the player\'s chest answers the room / Ostra: "It is not lying. That is the worst part."', ''),
 'CIN_GRANARY_REVEAL': ('The Granary: stolen land hanging in glass, region by region / Spared regions whole and green; taken regions grey / The Maker record plays like a farming manual / The Weave is the field; magic is irrigation; another harvester comes in about 3,000 years if this one fails / Ostra recognizes the player\'s Rites as plumbing / Hush, kindly: the Church\'s prayers improve yield', ''),
 'CIN_IRES_FINAL': ('Ires on the far side of the Granary, unmasked / She has read the Maker record and understands the deal was never a deal / She asks Ostra for an order, the first in nine hundred years / Duel, recruit, or let her reach Hush / Ostra asks her, once, to stop / Outcome by branch', ''),
 'CIN_HUSH_DESCENT': ('The descent into the Hush Core: a lift with no walls / Stolen sounds from every region play as they pass / Ostra counts the Heart Shards in the player\'s chest out loud / Hush narrates the weather of the harvest, politely / The active or returning companion arrives if approval allowed / The Seed lights below', ''),
 'CIN_HUSH_FALL': ('The Seed cracks like a frozen lake / Hush: "We were only doing what we were for." / No anger in it / Hush asks the player what they are for / The voices in the room stop one by one / Silence; Ostra breathes', ''),
 'CIN_CHOICE': ('At the broken core; the three endings shown as three lights / Ostra lays out each cost in full sentences / Restore: a ship; magic ends; she survives as a ship / Bind: the land heals; the player and she die; another light in 3,000 years / Take: the harvest stops; the player becomes the thing in the sky / "Whatever you choose, I will hold the door."', ''),
 'CIN_END_T_POST': ('Post-credits, the Still Room / The Speaker seals a black contract / The name on it is the player\'s / Vey takes it from the table / She looks up at the sky for a long time / Final slide: the player, as the Quiet, is glad someone took it', ''),
}
src = [m for m in master if m.get('kind') == 'CUT'] if master else []
if src:
    excl = {'CIN_MEM_4', 'CIN_MEM_5', 'CIN_MEM_6', 'CIN_END_B', 'CIN_END_T', 'CIN_END_T_POST'}
    items = [(m['cin_id'], m['quest_id'], m['title'], float(m['runtime_s']) / 60.0, m.get('cast', ''), m.get('location', ''), m.get('music_cue', ''),
              m.get('condition', ''), m['cin_id'] not in excl) for m in src]
    CIN_SRC = 'design/cinematics/cinematics.csv (master, CUT rows)'
else:
    items = [(c['cin_id'], c['qst_id'], c.get('title', ''), float(c['minutes']), c.get('speakers', ''), '', '', '', True) for c in camp_cins]
    CIN_SRC = 'campaign cinematics list (master missing at run time)'
for i, (nm, qid, title, mins, cast, loc, mus0, cond, typical) in enumerate(items, 1):
    if nm in CB:
        bt, mus = CB[nm]
        bts = [x.strip() for x in bt.split(' / ')]
    elif nm in EXTRA_CB:
        bts = [x.strip() for x in EXTRA_CB[nm][0].split(' / ')]
        mus = ''
    elif nm.startswith('CIN_MEM_'):
        n = int(nm.split('_')[-1])
        parts = [x.strip() for x in MEM.get(n, title).split(';')]
        bts = [f'Static frame from the chest Shard; HUD dims (only if FLG_HEART_{n}_TAKEN)'] + [cap(p) for p in parts] + \
              ['Ostra, over the cut: one line in her current stage voice', 'Back to the present; the player still kneels where the Heart was']
        mus = f'Ostra motif fragment {n} of 6 (the six together make the full motif heard in CIN_MUTINY)'
    else:
        seen_b, bts = set(), []
        for sh in shots.get(nm, []):
            if sh['beat'] in seen_b:
                continue
            seen_b.add(sh['beat'])
            act_ = sh['action'].replace('(cont.) ', '')
            bts.append((act_ if act_.lower().startswith(sh['beat_type'].lower()) else f"{sh['beat_type'].title()}: {act_}") + (f" ({name_of(sh['speaker']) if sh['speaker'].startswith('ACT_') else sh['speaker']})" if sh.get('speaker') else ''))
        if nm.startswith('CIN_BOSS_') and nm.replace('CIN_', 'ACT_') in SB_BY_BOSS:
            bts.append(f'Tic line in voice: {SB_TIC[nm.replace("CIN_", "ACT_")]}')
        if nm.startswith('CIN_LUCID_'):
            bid = nm.replace('CIN_LUCID_', 'ACT_BOSS_')
            if bid in SB_BY_BOSS:
                bts.append(f'Ostra reaction from the CNT_LUCID_HEARD line set (SCN_OSTRA lucid count rows); Heart Shard choice follows ({SB_BY_BOSS[bid][1]})')
        mus = ''
    bts = [b for b in bts if b][:12]
    while len(bts) < 6:
        bts.append(pick(['Reaction shot of the active companion', 'Close on the chest Shard as Ostra speaks', 'Hold on the location two seconds before gameplay returns',
                         'Player face; armor visible (in-engine)', 'Wide to match the gameplay camera, blend back in 1 s', 'Cut on a sound, never on a line'], nm + str(len(bts))))
    q = quests.get(qid, {})
    CIN_ROWS.append({'cin_id': f'CIN_{i:02d}', 'name': nm, 'title': title, 'quest_id': qid, 'minutes': round(mins, 2),
                     'typical_run': 'yes' if typical else 'no', 'typical_minutes': round(mins, 2) if typical else 0,
                     'location': loc or (place_of((q.get('locations', '') or '').split(';')[0].strip()) if q else ''),
                     'characters': cast, 'beats': fmt_beats(bts), 'music_cue': mus0 or mus or (f"Suggest: {REGION.get(q.get('region', ''), 'act')} theme, {'Shard-bearer layer' if ('BOSS' in nm or 'LUCID' in nm) else 'low strings'}; cinematics thread assigns the MUS_CIN_ id" if q else 'Suggest: act theme; cinematics thread assigns the MUS_CIN_ id'),
                     'ostra_stage': stage_of(qid) if qid in MQ_ORDER else 4, 'condition': cond,
                     'notes': f'Name, runtime and cast from {CIN_SRC}. This file is the writing outline (beats and lines); the campaign data-requests CIN_* asset hooks point at the cinematics thread master list.'
                     + (' Story pass beats added.' if nm in ('CIN_OPEN', 'CIN_ACT1_END', 'CIN_MUTINY', 'CIN_HUSH_SPEAKS', 'CIN_GRANARY_REVEAL', 'CIN_OSTRA_STOP', 'CIN_CHOICE', 'CIN_END_R', 'CIN_END_B', 'CIN_END_T') else '')
                     + (' Typical run = one ending (Restore here) and three memories, per design/cinematics/README.' if not typical else ''),
                     'status': 'draft'})
cin_total = round(sum(float(r['typical_minutes']) for r in CIN_ROWS), 2)
cin_authored = round(sum(float(r['minutes']) for r in CIN_ROWS), 2)

# cinematic rows in the scene table for campaign CINs not already in the outline
outline_cins = {re.search(r'(CIN_[A-Z0-9_]+)', s['scene_id']).group(1) for s in outline if 'CIN_' in s['scene_id']}
for r in CIN_ROWS:
    if r['name'] not in outline_cins and r['name'] in [c[0] for c in CIN_FALLBACK]:
        q = quests.get(r['quest_id'], {})
        add(r['quest_id'], 'writing', r['quest_id'], q.get('act', ''), q.get('region', ''), r['location'], 'cinematic', r['characters'], 'Cinematic',
            [x.split('. ', 1)[1] for x in r['beats'].split(' / ')][:8], '', '', round(float(r['minutes']) * 8), r['ostra_stage'], f'See cinematics.csv {r["cin_id"]} ({r["name"]}).')

# ---------------------------------------------------------------- barks
BARKS = []
BCOLS = ['str_id', 'owner_id', 'kind', 'faction_or_speaker', 'role_or_area', 'category', 'tone', 'text_en', 'max_chars', 'target_count', 'status', 'notes']
CATS = [('IDLE', 6), ('SPOT', 6), ('LOSE', 3), ('FLANK', 4), ('RELOAD', 3), ('ALLYDOWN', 4), ('LEADERDOWN', 4), ('HURT', 4), ('DEATH', 3), ('PLAYERDEATH', 3)]
FILL = {
 'HOLLOWED': {'FODDER': ['the barley', 'the goats', 'the hens'], 'SHIELDBEARER': ['the gate', 'my post', 'the night bell'],
              'SKIRMISHER': ['my mother', 'the well', 'the rope swing'], 'ARTILLERY': ['the kiln', 'the glass', 'the bellows'],
              'HEAVY': ['the ore cart', 'the anvil', 'the big stone'], 'LEADER': ['the roll call', 'the reeve\'s bell', 'the harvest count']},
 'REMNANT': {'FODDER': ['deck four', 'corridor C', 'bay two'], 'SHIELDBEARER': ['bulkhead nine', 'airlock six', 'hatch twelve'],
             'SKIRMISHER': ['vent shaft three', 'deck seven', 'the gantry'], 'ARTILLERY': ['array three', 'hull plate forty', 'mortar bay'],
             'HEAVY': ['cargo hold B', 'the engine deck', 'frame bay one'], 'LEADER': ['the bridge relay', 'command node one', 'deck control']},
 'THORN': {'FODDER': ['Bram', 'Tull', 'Nessa'], 'SHIELDBEARER': ['Gorm', 'Haddie', 'Ulf'], 'SKIRMISHER': ['Wick', 'Sela', 'Pip'],
           'ARTILLERY': ['Aldra', 'Fen', 'Moro'], 'HEAVY': ['Bruk', 'Old Tarn', 'Hask'], 'LEADER': ['Gral', 'Vorna', 'Kettle-Ma']},
 'CHOIRBORN': {'FODDER': ['the field', 'the furrow', 'the grain'], 'SHIELDBEARER': ['the wall', 'the held note', 'the hedge'],
               'SKIRMISHER': ['the gap', 'the quick note', 'the blink'], 'ARTILLERY': ['the lens', 'the long note', 'the bright line'],
               'HEAVY': ['the weight', 'the deep note', 'the great voice'], 'LEADER': ['the chorus', 'the gathering', 'the harvest song']},
}
FR = {
 'HOLLOWED': {
  'IDLE': ['Has anyone seen {r}?', 'I left {r} out, I left', 'Who moved {r}? Who', 'Someone should see to {r}', '{R} again. Always {r}'],
  'SPOT': ['Are you here for {r}?', 'You. You know {r}', 'Wait, did you bring {r}', 'Help me with {r}, help', 'Sleeper. Sleeper, {r} is'],
  'LOSE': ['Where did {r} go, where', 'Gone. Like {r}', 'Come back, {r} is', 'Was someone here? {R}?', 'I lost it. I lost {r}'],
  'FLANK': ['Round the back, by {r}', 'Go round {r}, go round', 'Behind {r}, behind the', 'Other side of {r}', 'Through {r}, quick, through'],
  'RELOAD': ['Wait. Wait, {r} first', 'Let me finish {r}', 'Tired. {R} can wait', 'One more breath for {r}', 'Hold on, {r} is heavy'],
  'ALLYDOWN': ['He went to fetch {r}', 'She was minding {r}', 'Who sees to {r} now', 'Down. Like {r} fell down', 'Get up, {r} needs you'],
  'LEADERDOWN': ['Who calls {r} now?', 'No one at {r}. No one', 'Mother? {R}? Mother', 'Run to {r}, run', 'Quiet. {R} went quiet'],
  'HURT': ['That stings, like {r}', 'Ow. Ow, {r}', 'Not {r}, not again', 'Hurts. Tell {r} it hurts', 'My arm, {r}, my'],
  'DEATH': ['Tell {r} I', 'Going home to {r}', 'Put {r} away now', 'Finally, {r}', 'Oh. {R}. There you'],
  'PLAYERDEATH': ['Sleep, like {r} sleeps', 'There. Lie by {r}', 'Shh. {R} will wait', 'You can help with {r} later', 'Rest. {R} is done']},
 'REMNANT': {
  'IDLE': ['Running checks on {r}.', '{R}: status nominal.', 'Sweeping {r}. Dust level high.', 'Log entry: {r} quiet.', 'Maintenance cycle, {r}. Proceeding.'],
  'SPOT': ['Unauthorized crew on {r}.', 'Intruder near {r}. Please remain still.', 'Unlisted sleeper at {r}.', 'Contact, {r}. Requesting crew ID.', 'Hull breach at {r}. Correcting.'],
  'LOSE': ['Contact lost near {r}.', 'Signal dropped, {r}. Searching.', '{R}: no crew detected.', 'Sweep widened to {r}.', 'Unknown crew left {r}.'],
  'FLANK': ['Rerouting through {r}.', 'Repair team to {r}.', 'Approaching from {r}. Please hold.', 'Second unit, take {r}.', 'Path via {r} clear.'],
  'RELOAD': ['Recharging. {R} hold.', 'Capacitor low at {r}.', 'Cycling cells, {r}.', 'Feed jammed, {r}.', 'Power draw from {r}. Wait.'],
  'ALLYDOWN': ['Unit offline at {r}.', 'Lost a unit, {r}. Logged.', 'Repair request: {r}.', 'Peer silent near {r}.', 'Salvage tag placed, {r}.'],
  'LEADERDOWN': ['Command lost. {R} silent.', 'No orders from {r}.', 'Fall back to {r}. Fall back.', 'Chain broken at {r}.', 'Seeking new command, {r}.'],
  'HURT': ['Damage taken, {r}.', 'Plating cracked. {R} logged.', 'Integrity falling at {r}.', 'Fault in {r} systems.', 'Please stop. {R} damaged.'],
  'DEATH': ['Shutdown at {r}.', 'Final log, {r}.', 'Powering down. {R}.', 'Report to {r}. Report', 'Unit lost. {R} unmanned.'],
  'PLAYERDEATH': ['Crew member vented, {r}.', 'Repair complete at {r}.', 'Breach sealed, {r}.', 'Body tagged for {r}.', 'Order restored to {r}.']},
 'THORN': {
  'IDLE': ['{R}, your turn on watch.', 'Who ate {r}\'s bread?', '{R} snores like a bear.', 'Quiet, {r}. Listen.', '{R} says rain by dusk.'],
  'SPOT': ['There! {R}, there!', 'Fresh meat, {r}!', '{R}! Sleeper on the path!', 'Gral wants its head, {r}!', 'Up, {r}! Company!'],
  'LOSE': ['Where\'d it go, {r}?', '{R}, you see it?', 'Lost it in the brush, {r}.', 'Check the ferns, {r}.', 'Gone to ground, {r}.'],
  'FLANK': ['{R}, go left!', 'Round the back, {r}!', '{R}, take the high roots!', 'Cut it off, {r}!', 'Box it in, {r}!'],
  'RELOAD': ['{R}, cover me!', 'Arrows, {r}! Arrows!', 'Hold them, {r}, I\'m loading!', 'Give me a breath, {r}!', 'Stringing up, {r}!'],
  'ALLYDOWN': ['They took {r}!', '{R} is down!', '{R}! Get up!', 'For {r}! For the Moot!', 'Blood for {r}!'],
  'LEADERDOWN': ['Run, it took {r}, run!', '{R} fell! Back!', 'No {r}, no fight!', '{R} is dead! Scatter!', 'Get out! {R}\'s gone!'],
  'HURT': ['Ah! {R}, I\'m cut!', 'Just a scratch, {r}!', 'It bit me, {r}!', '{R}! My leg!', 'Bleeding here, {r}!'],
  'DEATH': ['Tell {r} I fought.', '{R}, mind my axe.', 'Burn me proud, {r}.', 'Sorry, {r}.', '{R}, take me home.'],
  'PLAYERDEATH': ['Take its boots, {r}!', '{R}, it\'s down! Ha!', 'That\'s for {r}!', 'Sing it, {r}! We won!', 'Drag it to {r}!']},
 'CHOIRBORN': {
  'IDLE': ['We tend {r}.', 'We hum to {r}.', 'We wait in {r}.', '{R} is almost ripe. We wait.', 'We are {r}. We are patient.'],
  'SPOT': ['We see you in {r}.', 'You are almost ready for {r}.', 'Come to {r}. Be still.', 'We hear you near {r}.', 'Welcome to {r}, Kindled.'],
  'LOSE': ['Quiet in {r}. We are patient.', 'You hide in {r}. That is fine.', 'We will find you by {r}.', 'Gone from {r}. Not far.', 'We listen to {r} for you.'],
  'FLANK': ['We go around {r}.', 'We close {r} behind you.', 'We meet you past {r}.', 'Some of us take {r}.', 'We fill {r} on your left.'],
  'RELOAD': ['We breathe for {r}.', 'We gather {r} again.', 'A rest for {r}.', 'We tune {r}. Wait.', '{R} rests. Then we sing.'],
  'ALLYDOWN': ['One of us left {r}.', 'We are fewer in {r}.', 'That voice returns to {r}.', 'We gather them later, from {r}.', '{R} lost a voice. No matter.'],
  'LEADERDOWN': ['{R} is silent. We, we', 'Where is {r}? We cannot hear', 'We are, we are not {r}', 'Without {r} we are only us', '{R} stopped. Why did it stop'],
  'HURT': ['You bruise {r}. We do not mind.', 'That was loud, for {r}.', 'We feel that in {r}.', '{R} is cracked. We mend.', 'A sharp note in {r}.'],
  'DEATH': ['We return to {r}.', 'Be still, {r}. Gathered.', 'We rest in {r} now.', '{R} keeps us.', 'Gathered into {r}.'],
  'PLAYERDEATH': ['You rest in {r} now.', 'We gather you into {r}.', 'Good. {R} is quiet.', 'Be still. {R} has you.', 'You were almost ready for {r}.']},
}


def okbark(t):
    w = len(t.replace(',', ' ').split())
    return 2 <= w <= 8 and len(t) <= 60


for fac, roles in FILL.items():
    for role, fills in roles.items():
        for cat, tgt in CATS:
            frs = picks(FR[fac][cat], f'{fac}{role}{cat}', 5)
            out = []
            for k, f in enumerate(frs):
                if len(out) == 3:
                    break
                fl = fills[len(out)]
                t = f.replace('{R}', cap(fl)).replace('{r}', fl)
                if okbark(t):
                    out.append(t)
            for k, t in enumerate(out, 1):
                BARKS.append({'str_id': f'STR_BARK_{fac}_{role}_{cat}_{k:02d}', 'owner_id': f'ACT_{fac}_{role}', 'kind': 'Enemy bark', 'faction_or_speaker': f'FAC_{fac}',
                              'role_or_area': role, 'category': cat, 'tone': '', 'text_en': t, 'max_chars': 84, 'target_count': tgt * 3, 'status': 'draft',
                              'notes': f'Sample {k} of {tgt} written lines; x3 voices = {tgt * 3} recordings.' + (' LEADER: squad leader role (request).' if role == 'LEADER' else '')})
DETAILS = {
    'REG_01': ['the ash drifts', 'the burnt chapel', 'the kiln smoke', 'the black pines', 'the Spinegate ribs', 'the ember pits'],
    'REG_02': ['the salt flats', 'the wreck masts', 'the tide line', 'the gull rocks', 'the storm wall', 'the net sheds'],
    'REG_03': ['the root bridges', 'the rot pools', 'the moss stones', 'the strangler vines', 'the hydro pipes', 'the thorn hedges'],
    'REG_04': ['the glass dunes', 'the dry wells', 'the heat shimmer', 'the drone husks', 'the mirage road', 'the fused craters'],
    'REG_05': ['the ice pods', 'the frozen pass', 'the white lake', 'the cold huts', 'the coolant vents', 'the snow bridges'],
    'REG_06': ['the grey trees', 'the glass river', 'the sinkhole', 'the empty houses', 'the lamp poles', 'the name stones'],
    'REG_U': ['the engine ribs', 'the coolant pipes', 'the dead consoles', 'the core housing', 'the cable trenches', 'the vent fans'],
    'REG_Q': ['the Choirborn racks', 'the low gravity', 'the glass fields', 'the Maker walls', 'the threshing arms', 'the stolen hills'],
    'REG_HUB': ['the Bridge Deck', 'the Undermarket stalls', 'the Choir Spire', 'the crater lake', 'the Knights\' Gate', 'the Cradle doors'],
}
CFR = {
    'C1': ['Mark {d}. Good cover.', '{D}. Bad ground for a line.', 'Knights would post watch at {d}.', 'Keep left of {d}.', 'My squad camped near {d}.', 'Eyes on {d}, sleeper.', '{D}. My brother would hate this.', 'We fall back to {d}.'],
    'C2': ['The Log mentions {d}. Briefly.', 'I\'d like to sketch {d}.', '{D}. Nobody wrote that down.', 'Odd. {D} isn\'t in the logs.', 'Log, Hull 2:9 fits {d}.', 'Let me note {d}.', '{D}. My hands are cold.', 'Careful near {d}. I trip.'],
    'C3': ['{D}? Forty lights, easy.', 'I could sell {d}.', 'Smuggled past {d} once.', '{D}. Bad place to owe money.', 'Who owns {d}? Nobody? Good.', '{D}. Finders keep.', 'Debts hide near {d}.', 'Price of {d}? Too high.'],
    'C4': ['You see {d}. Good.', '{D}. You keep walking.', 'You could hide by {d}.', 'Watch {d}. Not me.', '{D}. Quiet.', 'You count {d}. I count exits.', 'Someone waits near {d}.', '{D}. Contract ground.'],
    'C5': ['{D} hums. Low pitch.', 'The song is loud near {d}.', 'Ostra, you hear {d}?', '{D}. A rest in the song.', 'I hear tones from {d}.', '{D}. My head aches.', 'Even {d} sings here.', 'Off-key, {d}. Wrong.'],
    'C6': ['{D}. Bad air for lungs.', 'I treated someone from {d}.', 'Wash after touching {d}.', '{D}. I need sleep.', 'Bandages are low. {D}, though.', 'Hollowing spreads near {d}.', '{D}. Mind your feet.', 'Someone died by {d}. Recently.'],
    'C7': ['My clan feared {d}.', '{D}. Ma told stories.', 'Clan Hask camps near {d}.', '{D}. No feud here, good.', 'Wolves love {d}.', 'Kin buried near {d}.', '{D}. I\'d set a trap there.', 'Smells like home, {d}.'],
    'C8': ['{D}: logged.', 'Scanning {d}. Nominal.', '{D}. Maintenance overdue.', 'Map updated: {d}.', 'Hazard near {d}. Step left.', '{D}: no crew. Logged sadly.', 'Ship part detected: {d}.', '{D}. Order 41 applies.'],
}
for c, frs in CFR.items():
    for ar in AREAS:
        dets = picks(DETAILS[ar], c + ar, 4)
        fs = picks(frs, ar + c, 8)
        k = 0
        for f in fs:
            if k == 4:
                break
            d = dets[k]
            t = f.replace('{D}', cap(d)).replace('{d}', d)
            if okbark(t):
                k += 1
                BARKS.append({'str_id': f'STR_BARK_CMP_{c}_{ar}_{k:02d}', 'owner_id': f'ACT_CMP_{c}', 'kind': 'Companion region bark', 'faction_or_speaker': f'ACT_CMP_{c}',
                              'role_or_area': ar, 'category': 'AREA', 'tone': '', 'text_en': t, 'max_chars': 84, 'target_count': 40, 'status': 'draft',
                              'notes': f'Sample {k} of 40 for {REGION[ar]}.'})
PB = [  # category, target, tone lines (Plain|Kind|Hard|Sly) or Any
 ('SPOT', 70, ['Contact ahead.|Two of them, left.|Company on the road.', 'Easy. Stay back if you can.|I don\'t want this fight.|Turn around. Please.',
               'Come on, then.|Your move. Make it fast.|You picked the wrong road.', 'Hello, friends. Bad timing.|Ah. You again, probably.|Smile, we have guests.']),
 ('HEAVYATTACK', 40, ['Hah, take it!|Here it comes!|All of it!']),
 ('DODGE', 30, ['Missed me.|Close one.|Not today.']),
 ('PARRY', 45, ['Blocked it.|Caught it.|Not that one.', 'Careful, you\'ll hurt yourself.|Stop. It\'s over.|Easy, now. Easy.',
                'Too slow.|Try harder.|That all you have?', 'Saw that coming.|Rude. Very rude.|Nice try, honestly.']),
 ('HURT', 60, ['Ah, that bit.|Ow, my ribs.|Ugh, my arm.']),
 ('LOWHEALTH', 45, ['Need to patch up.|Hurt. Pulling back.|Bad hit. Moving.', 'Ostra, stay with me.|Not yet. Not yet.|Breathe. Keep going.',
                    'Still standing.|Takes more than that.|I\'m not done.', 'This is fine. Mostly.|Ow. Noted, Ostra.|Should have stayed asleep.']),
 ('TONIC', 40, ['Quick drink.|Tonic, now.|Bitter. Works.']),
 ('RELOAD', 40, ['Reloading, cover.|Changing mag.|Loading, hold them.']),
 ('NOAMMO', 30, ['Out of rounds.|Empty. Switching.|No shots left.']),
 ('RITE', 45, ['Rite ready.|Casting now.|Drawing on the Shard.', 'Hold still, this helps.|Stay behind me.|Light for you.',
               'Burn, then.|Feel that.|Stand in this.', 'Watch this trick.|Little Shard magic.|Don\'t blink.']),
 ('WEAVE', 45, ['Weave, now.|Pulling the thread.|Ability up.', 'Together, now.|Cover your eyes.|Hang on to me.',
                'Down you go.|Out of my way.|End of the line.', 'Hold my Ember.|Bet you didn\'t plan for this.|Here\'s the clever bit.']),
 ('KILL', 70, ['It\'s down.|One less.|That\'s one.', 'Rest now.|I\'m sorry.|Go to sleep.', 'Stay down.|Next one.|Should have run.', 'Well, that happened.|Very tidy.|Oops. Not really.']),
 ('MULTIKILL', 45, ['Area clear.|That\'s the lot.|All down.', 'No more. Please.|It didn\'t have to go this way.|That\'s enough now.',
                    'Who\'s next?|Line them up.|All of you, then.', 'Did I do that?|Bit of a pile, now.|Count those for me, Ostra.']),
 ('BOSSSPOT', 45, ['That\'s the big one.|Here it comes.|Big target, ahead.', 'Whoever you were, I\'m sorry.|Let\'s end it gently.|You don\'t have to do this.',
                   'You\'re mine.|Let\'s settle this.|Big doesn\'t mean hard.', 'Oh, that\'s large.|Nobody mentioned teeth.|I hope it\'s friendly.']),
 ('BOSSDOWN', 45, ['It\'s over.|Big one\'s down.|Done. Finally.', 'Sleep well.|Go in peace.|You can rest now.', 'Told you.|Who\'s the god now?|Stay dead.',
                   'Wasn\'t so tough.|Thought that would take longer.|Can I keep the hat?']),
 ('ALLYDOWN', 45, ['Ally down.|Hold on, coming.|They\'re hit.', 'Stay with me. Please.|Don\'t you dare go.|I\'m here. Breathe.',
                   'Get up. Now.|Nobody touches them.|On your feet.', 'Nap later, please.|Up, you\'re embarrassing me.|Not the time to lie down.']),
 ('REVIVE', 45, ['Up you get.|There. Standing.|Back in it.', 'I\'ve got you.|Easy, slowly.|You\'re all right.', 'Walk it off.|Fight now, bleed later.|Up. We\'re not done.',
                 'Miss me?|You owe me one.|Rise and shine.']),
 ('DEATH', 30, ['Ostra, catch me.|Back soon.|Too soon, sorry.']),
 ('RESPAWN', 45, ['Back again.|Anchor holds.|Here again, then.', 'Thank you, Ostra.|Still here. Still trying.|Breathe. Again.', 'Again, then.|I\'m coming back for it.|One more time.',
                  'Nobody saw that.|Let\'s call that practice.|Ostra, don\'t log that.']),
 ('LEVELUP', 40, ['Stronger now.|Getting better.|Felt that change.', 'That\'s for Tomas.|For everyone back home.|Small steps, still steps.',
                  'More, then.|Bring the next one.|Not done growing.', 'Do I look taller?|Ostra, did I glow?|Very impressive, me.']),
]
TONES = ['Plain', 'Kind', 'Hard', 'Sly']
for cat, tgt, groups in PB:
    for gi, g in enumerate(groups):
        tone = TONES[gi] if len(groups) == 4 else 'Any'
        for k, t in enumerate(g.split('|'), 1):
            BARKS.append({'str_id': f'STR_BARK_PLAYER_{cat}_{tone.upper()}_{k:02d}', 'owner_id': 'PLAYER', 'kind': 'Player combat bark', 'faction_or_speaker': 'PLAYER',
                          'role_or_area': 'Voice sets A and B', 'category': cat, 'tone': tone, 'text_en': t, 'max_chars': 84,
                          'target_count': tgt if len(groups) == 1 else tgt // 4 + (1 if gi < tgt % 4 else 0), 'status': 'draft',
                          'notes': f'Category target {tgt} per voice set; recorded by both sets A and B.'})

# ---------------------------------------------------------------- summary
# scripted scenes: real voiced line counts from dialogue_lines.csv (tools/gen_scripts.py) replace the estimate
_scripted = collections.Counter(); _file = {}
for _l in rd(os.path.join(WR, 'dialogue_lines.csv')):
    if _l['voiced'] == 'yes':
        _scripted[_l['scene_id']] += 1
    _file[_l['scene_id']] = _l['script']
for r in ROWS:
    if r['scene_id'] in _file:
        r['est_lines'] = _scripted[r['scene_id']]; r['est_words'] = r['est_lines'] * 9; r['script'] = _file[r['scene_id']]
SUM = []
SCOLS = ['section', 'key', 'scenes', 'est_lines', 'est_words', 'target', 'target_source', 'gap', 'notes']
total_lines = sum(r['est_lines'] for r in ROWS)
for k, v in sorted(collections.Counter(r['kind'] for r in ROWS).items()):
    ln = sum(r['est_lines'] for r in ROWS if r['kind'] == k)
    SUM.append({'section': 'by_kind', 'key': k, 'scenes': v, 'est_lines': ln, 'est_words': ln * 9, 'target': '', 'target_source': '', 'gap': '', 'notes': ''})
for k, v in sorted(collections.Counter(r['source'] for r in ROWS).items()):
    ln = sum(r['est_lines'] for r in ROWS if r['source'] == k)
    SUM.append({'section': 'by_source', 'key': k, 'scenes': v, 'est_lines': ln, 'est_words': ln * 9, 'target': '', 'target_source': '', 'gap': '', 'notes': ''})
spk_lines = collections.defaultdict(float)
spk_scenes = collections.Counter()
for r in ROWS:
    sp = [s.strip() for s in r['speakers'].split(';') if s.strip()]
    w = {s: (0.6 if s == 'PLAYER' else 1.0) for s in sp}
    tot = sum(w.values()) or 1
    for s in sp:
        share = r['est_lines'] * w[s] / tot
        if s == 'ACT_CMP_ACTIVE':
            for i in range(1, 9):
                spk_lines[f'ACT_CMP_C{i}'] += share
                spk_scenes[f'ACT_CMP_C{i}'] += 1
        else:
            spk_lines[s] += share
            spk_scenes[s] += 1
CHAR_TGT = {'ACT_NPC_OSTRA': 6200, 'PLAYER': 9000, 'ACT_BOSS_HUSH': 900, 'ACT_NPC_IRES': 700, 'ACT_NPC_CHOIR_PRECENTOR': 800,
            'ACT_NPC_HULLKNIGHT_COMMANDER': 1100, 'ACT_NPC_LANTERN_ARCHIVIST': 1000, 'ACT_NPC_SALVAGER_BOSS': 950, 'ACT_NPC_QUIETHAND_SPEAKER': 900,
            'ACT_CMP_C1': 1400, 'ACT_CMP_C2': 1300, 'ACT_CMP_C3': 1350, 'ACT_CMP_C4': 1250, 'ACT_CMP_C5': 1300, 'ACT_CMP_C6': 1200, 'ACT_CMP_C7': 1250, 'ACT_CMP_C8': 1100}
for s in sorted(spk_lines, key=lambda x: -spk_lines[x]):
    ln = round(spk_lines[s])
    t = CHAR_TGT.get(s, '')
    SUM.append({'section': 'by_speaker', 'key': s, 'scenes': spk_scenes[s], 'est_lines': ln, 'est_words': ln * 9, 'target': t,
                'target_source': '02-characters.md' if t else '', 'gap': (ln - t) if t else '',
                'notes': ('PLAYER target = 4,500 x 2 voice sets; player lines count once except the A/B bark rows' if s == 'PLAYER' else
                          ('includes active-companion shares, recorded per companion' if s.startswith('ACT_CMP_C') else ''))})
real_spk = {s for s in spk_lines if not s.startswith('ACT_CMP_ACTIVE')}
voices_enemy = 4 * 3
SUM.append({'section': 'plan', 'key': 'VO lines total', 'scenes': len(ROWS), 'est_lines': total_lines, 'est_words': total_lines * 9, 'target': 60000,
            'target_source': 'plan 5.5', 'gap': total_lines - 60000, 'notes': 'Active-companion lines counted once here; per-companion recordings add more (see by_speaker).'})
SUM.append({'section': 'plan', 'key': 'speaking characters', 'scenes': '', 'est_lines': '', 'est_words': '', 'target': 120, 'target_source': 'plan 5.5',
            'gap': len(real_spk) - 120, 'notes': f'{len(real_spk)} distinct speaker IDs in scenes (enemy bark roles count as IDs; enemy voices = {voices_enemy} actors).'})
VO_CAT = [('quest scenes', 'quest', 'All quest scenes (campaign dialogue_outline)'), ('Second voice set', None, 'PLAYER quest lines re-recorded by set B'),
          ('Combat and reaction barks', 'player_barks', ''), ('Lore item comments', 'ostra_sys', ''), ('Quest reactions', 'cmp_reactions', ''),
          ('Location barks', 'cmp_barks', ''), ('Companion-to-companion', 'cmp_pairs', ''), ('Hub reactions', 'leader_react', ''),
          ('Relay Tower answers', 'hush_sys', ''), ('4 factions', 'enemy', ''), ('44 bosses plus Hush', 'bosses', ''), ('towns', 'town', ''), ('vendors', 'vendors', ''),
          ('templates', 'radiant', ''), ('endings.csv slides', 'epilogue', ''), ('read aloud', 'lore_read', ''), ('quest branch', 'branch', ''), ('lucid moments', 'heart', '')]
cat_lines = collections.Counter()
cat_scenes = collections.Counter()
for r in ROWS:
    cat_lines[r['_cat']] += r['est_lines']
    cat_scenes[r['_cat']] += 1
player_quest = round(sum(r['est_lines'] * 0.6 / (sum(0.6 if s_.strip() == 'PLAYER' else 1 for s_ in r['speakers'].split(';')) or 1)
                         for r in ROWS if r['_cat'] == 'quest' and 'PLAYER' in r['speakers']))
budget_q = sum(int(v['lines'] or 0) for v in vo_budget if v.get('source') == 'quest scenes')
matched_cats = set()
SUM.append({'section': 'vo_budget', 'key': 'quest scenes (all speakers)', 'scenes': cat_scenes['quest'], 'est_lines': cat_lines['quest'], 'est_words': cat_lines['quest'] * 9,
            'target': budget_q, 'target_source': 'design/campaign/vo_budget.csv', 'gap': cat_lines['quest'] - budget_q, 'notes': 'sum of per-speaker quest-scene rows'})
matched_cats.add('quest')
for v in vo_budget:
    if v.get('source') == 'quest scenes' or v.get('speaker') == 'TOTAL':
        continue
    t = int(v.get('lines') or 0)
    cat = next((c for key, c, _ in VO_CAT if key.lower() in (v.get('source', '') + ' ' + v.get('speaker', '')).lower()), 'none')
    if cat is None:
        ln, sc = player_quest, ''
    else:
        ln, sc = cat_lines.get(cat, 0), cat_scenes.get(cat, 0)
        matched_cats.add(cat)
    SUM.append({'section': 'vo_budget', 'key': f"{v.get('speaker')}: {v.get('source', '')[:60]}", 'scenes': sc, 'est_lines': ln, 'est_words': ln * 9, 'target': t,
                'target_source': 'design/campaign/vo_budget.csv', 'gap': ln - t, 'notes': 'PLAYER quest share, set B re-record' if cat is None else f'category {cat}'})
for c in sorted(set(cat_lines) - matched_cats):
    SUM.append({'section': 'vo_budget', 'key': f'not in vo_budget: {c}', 'scenes': cat_scenes[c], 'est_lines': cat_lines[c], 'est_words': cat_lines[c] * 9, 'target': 0,
                'target_source': 'design/campaign/vo_budget.csv', 'gap': cat_lines[c], 'notes': 'writing-side scenes the budget does not list yet'})
vb_total = next((int(v['lines']) for v in vo_budget if v.get('speaker') == 'TOTAL'), 0)
grand = total_lines + player_quest
SUM.append({'section': 'vo_budget', 'key': 'TOTAL incl. set B re-record', 'scenes': len(ROWS), 'est_lines': grand, 'est_words': grand * 9, 'target': vb_total,
            'target_source': 'design/campaign/vo_budget.csv', 'gap': grand - vb_total, 'notes': 'scene est_lines plus PLAYER quest share recorded again by voice set B'})
SUM.append({'section': 'cinematics', 'key': 'minutes', 'scenes': len(CIN_ROWS), 'est_lines': '', 'est_words': '', 'target': 45, 'target_source': 'plan 5.7',
            'gap': round(cin_total - 45, 2), 'notes': f'Typical run (one ending, three memories) must be 43 to 47; authored CUT footage {cin_authored} min.'})
SUM.append({'section': 'barks', 'key': 'sample rows', 'scenes': len(BARKS), 'est_lines': len(BARKS), 'est_words': '', 'target': sum(int(b['target_count']) for b in BARKS if b['str_id'].endswith('_01') or b['kind'] == 'Player combat bark') ,
            'target_source': 'barks.csv target_count', 'gap': '', 'notes': 'Samples written now vs final counts in target_count.'})

# ---------------------------------------------------------------- self-check
BANNED = STYLE_BANNED + ['journey', 'ancient']
errs = []
for tbl, rows, fields in [('dialogue_scenes', ROWS, ['beats', 'notes', 'player_choices', 'trigger']), ('cinematics', CIN_ROWS, ['beats', 'notes', 'music_cue']),
                          ('barks', BARKS, ['text_en'])]:
    seen_t = collections.Counter()
    for r in rows:
        for f in fields:
            t = str(r.get(f, ''))
            lo = t.lower()
            for bw in BANNED:
                if re.search(r'\b' + re.escape(bw) + r'\b', lo):
                    errs.append(f'{tbl} {r.get("scene_id") or r.get("cin_id") or r.get("str_id")}: banned "{bw}"')
            if '...' in t or '…' in t:
                errs.append(f'{tbl}: ellipsis in {f}')
            if tbl != 'barks' and '!' in t:
                errs.append(f'{tbl} {r.get("scene_id") or r.get("cin_id")}: exclamation in {f}')
        key = r.get('beats') or r.get('text_en')
        if not key:
            errs.append(f'{tbl}: empty text')
        seen_t[key] += 1
    d = [k for k, v in seen_t.items() if v > 1]
    if d:
        errs.append(f'{tbl}: {len(d)} duplicate texts, e.g. {d[0][:80]}')
for r in ROWS:
    nb = r['beats'].count(' / ') + 1
    if not 4 <= nb <= 8:
        errs.append(f'{r["scene_id"]}: {nb} beats')
    if r['ostra_stage'] not in (1, 2, 3, 4):
        errs.append(f'{r["scene_id"]}: stage')
for c in CIN_ROWS:
    nb = c['beats'].count(' / ') + 1
    if not 6 <= nb <= 12:
        errs.append(f'{c["cin_id"]}: {nb} beats')
if not 43 <= cin_total <= 47:
    errs.append(f'cinematics total {cin_total} min')
for b in BARKS:
    if not okbark(b['text_en']):
        errs.append(f'bark length {b["str_id"]}: {b["text_en"]}')
ids = collections.Counter(r['scene_id'] for r in ROWS)
if any(v > 1 for v in ids.values()):
    errs.append('duplicate scene ids')
# sentence-frame share in barks (first two words)
fr = collections.Counter(' '.join(b['text_en'].split()[:2]) for b in BARKS)
top = fr.most_common(1)[0]
if top[1] > 0.05 * len(BARKS):
    errs.append(f'bark frame over 5%: {top}')
fb = collections.Counter(r['beats'].split(' / ')[0][3:][:18] for r in ROWS)
if fb.most_common(1)[0][1] > 0.05 * len(ROWS):
    errs.append(f'scene opener frame over 5%: {fb.most_common(1)[0]}')
cov = {s[1] for s in SB} - {r['quest_id'] for r in ROWS if r['kind'] == 'lucid_moment'}
if cov:
    errs.append(f'missing lucid moments: {cov}')
miss_mq = [q for q in MQ_ORDER if q not in {r['quest_id'] for r in ROWS}]
if miss_mq:
    errs.append(f'main quests without scenes: {miss_mq}')
bosses_cov = {b['ACT_ID'] for b in all_bosses} - {('ACT_' + r['scene_id'][4:].rsplit('_', 1)[0]) for r in ROWS if r['kind'] in ('boss_intro',)}
if bosses_cov:
    errs.append(f'bosses without intro: {bosses_cov}')
cq = collections.Counter(r['quest_id'] for r in ROWS if r['quest_id'].startswith('CMPQ_'))
thin = [f'CMPQ_C{c}_{n:02d}' for c in range(1, 9) for n in range(1, 6) if cq[f'CMPQ_C{c}_{n:02d}'] < 2]
if thin:
    errs.append(f'companion quests with <2 scenes: {thin}')


def write(name, cols, rows):
    p = os.path.join(WR, name)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


REQ = [
    ('FLG_OSTRA_CONFRONTED', 'New flag: set by the Anchor confrontation (CNT_OSTRA_CONTRADICTIONS >= 3); read by MQ_A2_06 payoff scene', 'design/campaign/flags.csv', 'campaign owns flags'),
    ('REQ_STORY_FLAGS', 'Companion approval/left/returned/romance/recruit flags (FLG_C1_APPROVAL_25 and kin), FLG_HK_JOINED, FLG_SG_JOINED, FLG_OSTRA_SILENT, FLG_OSTRA_ASKED_STOP and the two Tomas flags are defined in design/campaign/seeds/system_flags.json; add them to the story-state save table', 'design/campaign/flags.csv', 'done in campaign; data/tech to add to save table'),
    ('ACT_NPC_HOLLOWED_OFFICER', 'Mini-boss in MQ_P_02 (Hush speaks through him at 10%)', 'data/world/npcs.csv', 'not one of the 44 bosses'),
    ('ACT_<FAC>_LEADER', 'Squad leader bark role for HOLLOWED, REMNANT, THORN, CHOIRBORN (or map to the heavy)', 'data/actors/enemies.csv', '6th bark role'),
    ('ACT_NPC_TOWNSFOLK_<LOC>', 'Speaker groups for town ambient VO per settlement and hub tier', 'data/world/npcs.csv', 'VO casting groups'),
    ('STR_BARK_*', f'{len(BARKS)} bark sample keys in design/writing/barks.csv to move into data/ui/strings_data.csv at lock', 'data/ui/strings_data.csv', ''),
    ('STR_DLG_<SCENE>_nnn', 'Dialogue line key pattern for scenes in dialogue_scenes.csv (style guide 5)', 'data/ui/strings_data.csv', 'at VO script lock'),
    ('UI_HINT_COLD', 'Ostra hint text color shift after the Anchor confrontation (story pass B)', 'data/ui', 'UI note'),
    ('UI_OSTRA_SILENT', 'HUD hint and map-update loss during MQ_A2_07 (story pass H)', 'data/ui', 'UI note'),
]

write('dialogue_scenes.csv', COLS, ROWS)
write('cinematics.csv', ['cin_id', 'name', 'title', 'quest_id', 'minutes', 'typical_run', 'typical_minutes', 'condition', 'location', 'characters', 'beats', 'music_cue', 'ostra_stage', 'notes', 'status'], CIN_ROWS)
write('barks.csv', BCOLS, BARKS)
write('scene_summary.csv', SCOLS, SUM)
with open(os.path.join(WR, 'requests_dialogue.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['id', 'request', 'target_table', 'notes'])
    w.writerows(REQ)

kc = collections.Counter(r['kind'] for r in ROWS)
print(f'scenes {len(ROWS)} lines {total_lines} | kinds {dict(kc)}')
print(f'cinematics {len(CIN_ROWS)} typical {cin_total} min, authored {cin_authored} | barks {len(BARKS)} {dict(collections.Counter(b["kind"] for b in BARKS))}')
print(f'warnings {len(warn)}:', *warn[:30], sep='\n  ')
if errs:
    print(f'ERRORS {len(errs)}:', *errs[:40], sep='\n  ')
    sys.exit(1)
print('self-check clean')
