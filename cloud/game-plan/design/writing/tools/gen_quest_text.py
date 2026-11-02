#!/usr/bin/env python3
"""Shardfall writing: quest text, radiant notices, tutorials, Ostra hints, loading tips.

Reads data/ and design/campaign/ at run time (campaign CSVs first; if they are empty,
the campaign seeds/*.json in the same schema), so a rerun picks up later changes.
Never writes outside design/writing/. Python 3 stdlib only. Text is seeded by ID.
All output rows are drafts for a human writer (style guide 9).
"""
import csv, hashlib, json, math, os, random, re, sys, collections, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DATA = ROOT + '/data'
CAMP = ROOT + '/design/campaign'
OUT = ROOT + '/design/writing'
COLS = ['str_id', 'owner_id', 'kind', 'text_en', 'max_chars', 'status', 'notes']



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
from canon_names import canon, world_locations, world_names

def rd(path):
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return _norm_region(list(csv.DictReader(f)))


def rng(key):
    return random.Random(int(hashlib.sha1(key.encode()).hexdigest()[:12], 16))


def cap1(s):
    return s[:1].upper() + s[1:] if s else s


def low1(s):
    if not s:
        return s
    w = s.split(' ', 1)[0]
    if w.isupper() and len(w) > 1:
        return s
    if w in ('I',) or w.startswith('Ostra') or w in KEEP_CASE:
        return s
    return s[:1].lower() + s[1:]


KEEP_CASE = set()

# ---------------------------------------------------------------- names
NAMES = {}


def load_names():
    for r in rd(DATA + '/world/npcs.csv'):
        NAMES[r['act_id']] = r['name']
    for r in rd(DATA + '/actors/bosses.csv'):
        NAMES[r['ACT_ID']] = r['Boss']
    for r in rd(DATA + '/actors/enemies.csv'):
        NAMES[r['ACT_ID']] = r['Name']
    for r in rd(DATA + '/actors/creatures.csv'):
        NAMES[r['ACT_ID']] = r['Name']
    for r in rd(DATA + '/items/items_index.csv'):
        NAMES[r['item_id']] = r['name']
    for r in rd(DATA + '/items/lore_items.csv'):
        NAMES[r['item_id']] = r['name']
    for r in rd(DATA + '/world/regions.csv'):
        NAMES[r['reg_id']] = r['name']
    for r in rd(OUT + '/place_names.csv'):
        NAMES[r['loc_id']] = r['text_en']
    for r in world_locations():   # design/world/locations.csv is canon
        NAMES[r['loc_id']] = 'Lantern Hold' if r['kind'] == 'Hub' else r['name']
    for md in ('02-characters.md', '05-story-pass.md'):
        p = CAMP + '/' + md
        if os.path.exists(p):
            for m in re.finditer(r'\|\s*(ACT_[A-Z0-9_]+)\s*\|\s*([^|]+?)\s*\|', open(p, encoding='utf-8').read()):
                nm = re.sub(r'\s*\(.*?\)', '', m.group(2)).strip()
                if nm and not nm.startswith('ACT_') and len(nm) < 40:
                    NAMES.setdefault(m.group(1), nm)
            for m in re.finditer(r'([A-Z][\w\'-]+(?: [A-Z][\w\'-]+){0,3}) \((ACT_[A-Z0-9_]+)\)', open(p, encoding='utf-8').read()):
                NAMES.setdefault(m.group(2), m.group(1))
    NAMES['ACT_NPC_OSTRA'] = 'Ostra'


IDRE = re.compile(r'^(ACT|LOC|ITM|QST|MQ|SQ|CMPQ|FLG|REG|CIN|CNT|RAD)_[A-Z0-9_<>]+$')
PREFIX_STRIP = ['ACT_NPC_', 'ACT_CRT_', 'ACT_BOSS_', 'ACT_CMP_', 'ACT_', 'ITM_', 'FLG_']


def name_of(x):
    x = (x or '').strip()
    if not x:
        return ''
    if x in NAMES:
        return NAMES[x]
    if not IDRE.match(x):
        return x
    m = re.match(r'LOC_CQ_(?:REG_[0-9A-Z]+|HUB)_(.+)', x)
    if m:
        return canon('the ' + m.group(1).replace('_', ' ').title())
    m = re.match(r'LOC_(?:TOWN|SITE|VAULT)_(REG_[0-9A-Z]+)_', x)
    if m:
        return REG[m.group(1)]['town'] if 'TOWN' in x else 'a ' + ('Choir vault' if 'VAULT' in x else 'ruin') + ' in ' + REG[m.group(1)]['name']
    for p in PREFIX_STRIP:
        if x.startswith(p):
            return canon(x[len(p):].replace('_', ' ').title())
    return canon(x.replace('_', ' ').title())


def scrub(text):
    """Replace IDs inside designer text with names; drop sentences that only cite quest or flag IDs."""
    def rep(m):
        t = m.group(0)
        if re.match(r'(QST|MQ|SQ|CMPQ|FLG|CIN|CNT|RAD)_', t):
            return '\x00'
        return name_of(t)
    t = re.sub(r'\b(?:ACT|LOC|ITM|QST|MQ|SQ|CMPQ|FLG|CIN|CNT|RAD)_[A-Z0-9_]+', rep, text)
    t = re.sub(r'\s*\([^)]*\x00[^)]*\)', '', t)
    sents = [s for s in re.split(r'(?<=[.!?])\s+', t) if '\x00' not in s]
    t = ' '.join(sents)
    t = t.replace('\x00', '')
    return re.sub(r'\s+', ' ', t).strip()


def notebook(text):
    t = re.sub(r"\bThe player's\b", 'My', text)
    t = re.sub(r"\bthe player's\b", 'my', t)
    t = re.sub(r'(^|[.!?]\s+)The player\b', lambda m: m.group(1) + 'I', t)
    t = re.sub(r'\bthe player\b', 'me', t)
    t = re.sub(r'\bThe player\b', 'I', t)
    return t


IRREG = {'find': 'found', 'go': 'went', 'take': 'took', 'bring': 'brought', 'read': 'read', 'speak': 'spoke',
         'meet': 'met', 'get': 'got', 'hold': 'held', 'choose': 'chose', 'light': 'lit', 'steal': 'stole',
         'win': 'won', 'lead': 'led', 'ride': 'rode', 'break': 'broke', 'leave': 'left', 'tell': 'told',
         'fight': 'fought', 'sneak': 'snuck', 'swim': 'swam', 'buy': 'bought', 'pay': 'paid', 'sell': 'sold',
         'put': 'put', 'set': 'set', 'hide': 'hid', 'dig': 'dug', 'ring': 'rang', 'wake': 'woke', 'feed': 'fed',
         'hear': 'heard', 'give': 'gave', 'drive': 'drove', 'say': 'said', 'keep': 'kept', 'let': 'let',
         'sit': 'sat', 'stand': 'stood', 'run': 'ran', 'see': 'saw', 'throw': 'threw', 'shoot': 'shot',
         'make': 'made', 'catch': 'caught', 'teach': 'taught', 'sing': 'sang', 'draw': 'drew', 'fly': 'flew',
         'freeze': 'froze', 'cut': 'cut', 'beat': 'beat', 'sleep': 'slept', 'send': 'sent', 'spend': 'spent',
         'lose': 'lost', 'build': 'built', 'shut': 'shut', 'write': 'wrote', 'do': 'did', 'be': 'was',
         'eat': 'ate', 'drink': 'drank', 'climb': 'climbed', 'survive': 'survived', 'kill': 'killed',
         'stop': 'stopped', 'plan': 'planned', 'drop': 'dropped', 'grab': 'grabbed', 'trap': 'trapped',
         'swap': 'swapped', 'ship': 'shipped', 'tip': 'tipped', 'step': 'stepped', 'slip': 'slipped',
         'rid': 'rid', 'shed': 'shed', 'bid': 'bid', 'hit': 'hit', 'quit': 'quit', 'spread': 'spread',
         'seek': 'sought', 'think': 'thought', 'fall': 'fell', 'rise': 'rose', 'wear': 'wore', 'tear': 'tore',
         'bear': 'bore', 'swear': 'swore', 'forgive': 'forgave', 'understand': 'understood', 'undo': 'undid',
         'outrun': 'outran', 'overhear': 'overheard', 'rebuild': 'rebuilt', 'rewind': 'rewound', 'wind': 'wound',
         'bind': 'bound', 'feel': 'felt', 'deal': 'dealt', 'mean': 'meant', 'lend': 'lent', 'bend': 'bent',
         'begin': 'began', 'come': 'came', 'become': 'became', 'shake': 'shook', 'strike': 'struck',
         'hang': 'hung', 'stick': 'stuck', 'sweep': 'swept', 'creep': 'crept', 'weep': 'wept', 'flee': 'fled',
         'show': 'showed', 'carry': 'carried', 'escort': 'escorted', 'search': 'searched', 'recover': 'recovered'}


def past_verb(v):
    lv = v.lower()
    if lv in IRREG:
        p = IRREG[lv]
    elif lv.endswith('e'):
        p = lv + 'd'
    elif re.search(r'[^aeiou]y$', lv):
        p = lv[:-1] + 'ied'
    else:
        p = lv + 'ed'
    return p.capitalize() if v[:1].isupper() else p


def to_past(phrase):
    phrase = phrase.strip().rstrip('.')
    m = re.match(r"(Don't|Do not)\s+(\w+)(.*)", phrase, re.I)
    if m:
        return "Didn't " + m.group(2).lower() + m.group(3)
    w = phrase.split(' ', 1)
    rest = w[1] if len(w) > 1 else ''
    out = past_verb(w[0]) + (' ' + rest if rest else '')
    out = re.sub(r'\bor\s+(\w+)', lambda m: 'or ' + (past_verb(m.group(1)) if m.group(1).lower() in IRREG or m.group(1).lower() in ('fight', 'talk', 'pay') else m.group(1)), out, count=1)
    out = re.sub(r'\byour\b', 'my', out)
    out = re.sub(r'\byourself\b', 'myself', out)
    out = re.sub(r'\byou\b', 'me', out)
    return out


def plural(n):
    if n.endswith(('s', 'x', 'ch', 'sh')):
        return n
    if n.endswith('y') and not n.endswith(('ay', 'ey', 'oy')):
        return n[:-1] + 'ies'
    if n.endswith('man'):
        return n[:-3] + 'men'
    return n + 's'


# ---------------------------------------------------------------- engine
SLOT = re.compile(r'<(\w+)>')


def fill(t, slots, r):
    def g(m):
        k = m.group(1)
        kk = k.lower()
        v = slots.get(kk, slots.get(k, ''))
        if isinstance(v, (list, tuple)):
            v = r.choice(v) if v else ''
        v = str(v)
        return cap1(v) if k[:1].isupper() and k[1:] == kk[1:] and k != kk else v
    s = SLOT.sub(g, t)
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.replace(' .', '.').replace(' ,', ',').replace('..', '.')
    return cap1(s)


class Table:
    def __init__(self, name, expected):
        self.name = name
        self.rows = []
        self.use = collections.Counter()
        self.texts = set()
        self.limit = max(3, int(math.ceil(0.05 * max(expected, 1))))
        self.expected = expected

    def compose(self, key, parts, cap, joiner=' ', soft=False):
        """parts: list of (bank_id, bank, slots). Picks one frame per part (seeded),
        respecting the 5% frame limit and uniqueness; returns text."""
        r = rng(key)
        for attempt in range(400):
            idxs, bits = [], []
            for bid, bank, slots in parts:
                order = list(range(len(bank)))
                r.shuffle(order)
                choice = None
                for i in order:
                    if attempt < 300 and self.use[(bid, i)] >= self.limit:
                        continue
                    choice = i
                    break
                if choice is None:
                    choice = order[0]
                idxs.append((bid, choice))
                bits.append(fill(bank[choice], slots, r))
            t = joiner.join(b for b in bits if b)
            t = re.sub(r'\s+', ' ', t).strip()
            if len(t) <= cap and t not in self.texts:
                for k in idxs:
                    self.use[k] += 1
                self.texts.add(t)
                return t
        if soft:
            return None
        raise RuntimeError('no text fits for %s in %s' % (key, self.name))

    def add(self, str_id, owner, kind, text, cap, notes='', status='draft', **extra):
        if cap:
            assert len(text) <= cap, (str_id, len(text), cap, text)
        self.texts.add(text)
        row = dict(str_id=str_id, owner_id=owner, kind=kind, text_en=text,
                   max_chars=math.ceil((cap or len(text)) * 1.4), status=status, notes=notes)
        row['_cap'] = cap
        row.update(extra)
        self.rows.append(row)
        return row

    def frame_share(self):
        if not self.rows or not self.use:
            return 0.0
        return max(self.use.values()) / len(self.rows)


def write(path, rows, cols):
    tmp = path + '.tmp'
    with open(tmp, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)
    os.replace(tmp, path)

# ---------------------------------------------------------------- regions
# Shardfall design choices for landmarks, details and sayings (lore bible 5, world-life 7).
REG = {
 'REG_01': dict(name='Cinderreach', stage=1, act='1', elem='Ember', town='Emberwatch', town2='Cinder Hollow',
   lm=['the broken spine on the skyline', 'the kiln chimneys', 'the black ridge road', 'the burnt orchard',
       'the slag stream', 'the charred windmill', 'the old pod crater', 'the ash forest', 'the miners\' rope bridge',
       'the Pyre-Court beacon'],
   det=['Ash got into everything, even the bread <name> gave me.', 'A dog followed me halfway, then thought better of it.',
        'Someone had chalked a child\'s height on a burnt doorframe. Three marks, then none.',
        'The wind smelled of pitch and wet wool.', 'Found a kettle still warm in an empty house near <loc>.',
        'The ridge glowed after dark, the way it does now.', 'A woman was sweeping ash off a step with no house behind it.',
        '<name> counted the chimneys smoking. Six. There used to be forty.', 'My boots will never be grey again. They are black now. Fine.',
        'A warden\'s torch moved along the ridge and nobody in <town> breathed until it passed.',
        '<name> pressed a carved Shard lamp into my hand and would not take it back.',
        'Charcoal burners were singing an alarm-tone song to keep time.'],
   open=['Smoke on the ridge again. Keep your voice down.', 'Vael\'s wardens came through at wake-call. Took the <family> boy\'s boots, of all things.',
         'You\'re the sleeper Annik talks about. Good. We\'re short of hands that don\'t shake.',
         'Don\'t light anything. I mean it. Not even a pipe.', 'Ash in the well, ash in the bread, and now this.',
         'My chimney is the only one on this street still drawing. I\'d like to keep it that way.',
         'If the smoke turns white, run. If it\'s grey, listen to me.'],
   hazard='ash fall', saying='Smoke on the ridge, bring the children in.', food='charcoal-baked galley beans',
   work='charcoal burning', fear='their own lord\'s fire', insult='"your chimney draws backward"', weather='Cinder',
   token='lumps of slag', custom='carves a Shard lamp for every child that survives a winter', greeting='"Clear air."',
   oath='"By the spine."', people='miners'),
 'REG_02': dict(name='Saltmere', stage=1, act='1', elem='Storm', town='Stiltmarket', town2='Brinehook',
   lm=['the Beached Ark\'s mast', 'the salt flats', 'the harbor wall', 'the drowned watchtower', 'Wreck Row\'s hulls',
       'the tide pools', 'the gull rocks', 'the lighthouse stump', 'the causeway posts', 'the net sheds'],
   det=['Salt crusted on my sleeves by noon.', '<name> mended a net while we talked and never once looked down at it.',
        'The tide came in faster than <name> promised. It always does, apparently.', 'A gull stole half my fish and looked proud of it.',
        'Rain came sideways off the wrecks and then stopped as if someone switched it off.',
        'Found a child\'s boat carved from hull plate near <loc>. Left it where it was.',
        'Thunder rolled out on the flats with no cloud to explain it.', 'Two old sailors were arguing about a storm from sixty years ago. Both lost.',
        'Every house in <town> has a lamp in the window for a boat that is still out.',
        'The causeway posts are painted with names. Drowned, <name> said, or married. Same paint.',
        'Somebody had tied a ribbon to a wreck\'s rib. It looked new.', 'Smelled smoked fish for an hour after. Not unpleasant.'],
   open=['Tide\'s turning in an hour. Talk fast.', 'Storm\'s coming in off the wrecks. They always come off the wrecks.',
         'Three boats went out. Two came back. That\'s a good week here.', 'Mind the nets. My husband mends them and he\'ll know you stepped on them.',
         'Salt in your boots already? You\'ll fit right in.', 'Corsa\'s flags are up on the Beached Ark again. Nobody\'s on deck to raise them.',
         'Tide takes, tide gives back. Never the same thing. Today it gave me a problem.'],
   hazard='squalls', saying='Tide takes, tide gives back, never the same thing.', food='salt fish on tuber bread',
   work='net mending', fear='storms and old war wrecks', insult='"you\'d drown in a bucket"', weather='Squall',
   token='mussel shells', custom='paints a name on a causeway post for every boat lost', greeting='"Fair tide."',
   oath='"Deep and dry."', people='fishers'),
 'REG_03': dict(name='Thornwood', stage=2, act='2', elem='Bloom', town='Redbark Lodge', town2='Thicket Steading',
   lm=['the giant hollow oak', 'the root bridge', 'the rot line', 'the old hydroponics dome', 'the moss falls',
       'the Clan totem poles', 'the bramble wall', 'the fallen trunk road', 'the glowing fern beds', 'the Moot drums'],
   det=['Roots had moved the path since <name> last walked it.', 'Rot smelled sweet. Nobody warned me it would smell sweet.',
        'The ferns lit up blue when I stepped on them and dimmed when I said sorry.',
        '<name> chewed a root the whole time and offered me half. I declined. Mistake, maybe.',
        'Heard the Moot drums far off. Two beats, a gap, two beats.', 'A Clan child watched me from a branch and did not blink once.',
        'Something large moved in the canopy above <loc> and decided I was not worth it.',
        'Galley beans grow wild here, waist high. Ate a handful.', 'The trees are quiet in the rotten patches. That is how you know.',
        '<name> marked the trail with knotted grass so I could get home. Kind.', 'Got bramble cuts on both hands. Worth it.',
        'Somebody had built a tiny shrine of ship screws in a tree root.'],
   open=['Roots are moving again. Don\'t laugh, I\'ve measured.', 'Rot in the east field, rot in the cellar, rot in my cousin\'s temper.',
         'You walked in on the path? Lucky. Paths move here.', 'The Clans took our goat. The goat came back. Now they want it back again.',
         'Sorrel hasn\'t spoken to a person in twenty years. The trees talk plenty.', 'Mind the brambles. They\'re older than my grandmother and meaner.',
         'Root deep or blow away, they say. I\'m about to blow away.'],
   hazard='spore drifts', saying='Root deep or blow away.', food='galley bean stew with forest mushrooms',
   work='herb gathering', fear='rot and the Brood Caves', insult='"shallow-rooted"', weather='Rootstorm',
   token='acorns', custom='plants a tree for each feud ended and burns one for each feud started', greeting='"Deep roots."',
   oath='"On my root."', people='foresters'),
 'REG_04': dict(name='Glasswaste', stage=2, act='2', elem='Iron', town='Glassmouth Caravanserai', town2='Choirtower Hamlet',
   lm=['the shattered dune ridge', 'the Remnant pylon', 'the caravan well', 'the fused crater', 'the glass arches',
       'the Last Hangar\'s tail fin', 'the mirror flats', 'the wind-cut pillars', 'the old Glass War trench', 'the signal mirror'],
   det=['Drank before talking. <name> insisted, and was right.', 'The glass rang under my boots like a bell left out in the sun.',
        'Heat shimmer made the pylon look like it was walking. It was not. Probably.',
        '<name> traded me cactus water for a story and said the story was short.', 'A Remnant drone fixed a fence nobody needed and rolled away.',
        'Sand in my teeth. Sand in my pack. Sand in a sealed jar, somehow.', 'Found Glass War helmets near <loc>, lined up neatly by someone.',
        'The caravan dogs barked at the sky for an hour.', 'At night the glass gave the heat back and everything glowed faintly.',
        'A mosaic on a well showed a ship falling. The ship was smiling. Odd choice.', '<name> paid a water debt to a man three days dead. Poured it on the sand.',
        'Saw my reflection in the mirror flats a hundred times over. All of them tired.'],
   open=['Drink first. Water is a promise. Now we talk.', 'Heat\'s up early. So are the drones.',
         'Caravan\'s three days late. Saba says that\'s nothing. Saba says that every time.', 'The glass sang last night. Glass shouldn\'t sing.',
         'You owe me a cup of water for sitting in my shade. We\'ll call it even if you help.', 'The Remnant fixed the road again. Badly. Into a wall.',
         'Sit in the shade. Not that shade. That one\'s mine.'],
   hazard='glass storms', saying='Water is a promise.', food='cactus water and flatbread baked on hot glass',
   work='glassblowing', fear='thirst and the Remnant', insult='"you\'d spill a well"', weather='Mirage',
   token='glass chips', custom='keeps a water debt book in every household, settled at funerals', greeting='"Cool shade."',
   oath='"Dry well, if I lie."', people='caravaners'),
 'REG_05': dict(name='Rimefall', stage=3, act='2', elem='Frost', town='Rimehold', town2='Lampwick',
   lm=['the frozen waterfall', 'the coolant vents', 'the monks\' stair', 'the white pass', 'the pod field under the ice',
       'the bell cairn', 'the frost lily slope', 'the snowed-in sledge road', 'the leaning radio mast', 'the Still Lake shore'],
   det=['Cold enough that my breath froze on my scarf.', '<name> offered tuber bread so hard I used it as a wedge.',
        'Frost lilies grew only near the coolant vents. Pretty. Poisonous, <name> says.',
        'Saw faces in the ice near <loc>. Did not stop to count them.', 'The bell cairn rang once with no wind.',
        'Monks walked past in silence and left a hot stone by my feet.', 'The sledge dogs slept in a heap and snored in shifts.',
        'Snow fell straight down, very quietly, for an hour.', '<name> has kept a pot of tea warm for eleven years for a son in the ice.',
        'My fingers did not work for a while. They do now.', 'A child in <town> asked if I was frozen too, once. Said yes.',
        'The stove in the post shed had a waiting list.'],
   open=['Shut the door. Heat\'s money up here.', 'We wait for the thaw. We\'ve been waiting eleven years.',
         'Mother Rime froze my neighbor "for later". It\'s later. I\'d like him back.', 'Cold makes people honest. Sit by the stove and I\'ll be honest.',
         'The passes closed again. The passes are always closed.', 'Snow\'s quiet today. Quiet snow means something\'s walking in it.',
         'Wait for the thaw, they say. I\'m done waiting.'],
   hazard='whiteouts', saying='Wait for the thaw.', food='tuber bread and Strider milk tea',
   work='herding', fear='being frozen "for later"', insult='"thaw-brained"', weather='Whiteout',
   token='frozen berries', custom='leaves one chair empty at every table for someone in the ice', greeting='"Warm hands."',
   oath='"Freeze me if I lie."', people='herders'),
 'REG_06': dict(name='Hollowdeep', stage=3, act='2', elem='Hollow', town='Last Light', town2='Driftanchor',
   lm=['the sinkhole city rim', 'the glass river', 'the greywood forest', 'the lamp posts of Last Light', 'the Clock Priory spire',
       'the collapsed bridge', 'the Twin Thrones\' arch', 'the silent mill', 'the name wall', 'the fog line'],
   det=['<name> said their own name three times before answering mine.', 'The greywood snapped like old bread when I touched it.',
        'The river was glass. A fish was stuck in it, mid-turn.', 'Lamp crew kids ran past with poles taller than they were.',
        'Fog came up to the lamp line and stopped there, like it was polite.', 'Found a coat near <loc> with a name stitched inside. Kept the name.',
        'Somebody had written "I was here and I was Mara" on a wall. Wrote my name under it.',
        'No birds. Not one. You notice it after a while.', '<name> forgot what we were talking about and laughed about it, a bit too long.',
        'The name wall in <town> had a new line since yesterday.', 'Heard a Hollowed humming a lullaby, half of it.',
        'Lamps in <town> burn all day. Nobody complains about the oil.'],
   open=['Say your name. Out loud. Good. I write mine on my sleeve, in case.', 'Lamp crew\'s short again. Kids run it. Kids shouldn\'t have to.',
         'I forgot my sister\'s birthday this year. I had never forgotten it before.', 'Grey came over the north ridge last week. The trees stopped making noise.',
         'Don\'t drink the river. It\'s glass now.', 'Keep a lamp lit and keep talking. That\'s how we do it here.',
         'Tell me your name again. Humor me.'],
   hazard='grey fog', saying='Say your name every morning.', food='mushroom broth with a spoon of salt from the coast',
   work='lamp tending', fear='forgetting', insult='"nameless"', weather='Fogwalker',
   token='lamp wicks', custom='reads the name wall aloud at dusk, every name, every night', greeting='"Name kept."',
   oath='"Forget me if I lie."', people='lamp crews'),
 'REG_HUB': dict(name='Lantern Hold', stage=1, act='1', elem='', town='Lantern Hold', town2='the Undermarket',
   lm=['the Bridge Deck stairs', 'the Knights\' Gate', 'the Log Chapel bells', 'the Choir Spire', 'the Undermarket lifts',
       'the Cradle doors', 'the crater lake jetty', 'the arena wall', 'the captain\'s empty chair', 'the council bench'],
   det=['The whole Hold leaned a little, the way it always does. Got used to it.', '<name> sold me a pie and a rumor. The pie was better.',
        'Knights changed the guard with more shouting than seemed needed.', 'Chapel bells rang the hour in alarm tones. Nobody jumped but me.',
        'The lifts groaned all the way down.', 'A Choir lens on the Spire caught the light and threw it across the lake.',
        'Kids were playing Bays and Ladders on the jetty with bottle caps.', 'Undermarket smelled of oil, fish and somebody\'s argument.',
        'Somebody had polished the captain\'s chair. Again. Nobody sits in it.', '<name> was painting a hull plate sign and asked how to spell "honest".',
        'The council clerk walked past with a stack of papers taller than his head.', 'Heard three faction songs at once from three windows.'],
   open=['The Hold holds. Mostly. Not my stall, but mostly.', 'You\'re a Kindled. Everybody\'s staring. Ignore them, I do.',
         'Council\'s arguing again. They argue so we don\'t have to.', 'Undermarket rent went up. Bridge Deck rent went up. My patience went down.',
         'Mind the stairs. The whole Hold is standing on its nose.', 'Got a minute? Everybody here has a favor and nobody has a minute.'],
   hazard='', saying='The Hold holds.', food='Undermarket fish pie', work='trade', fear='being sent back out',
   insult='"lift-sick"', weather='Bridge', token='bottle caps', custom='salutes the captain\'s empty chair on the way past',
   greeting='"Green board."', oath='"On the bridge."', people='Hold folk'),
 'REG_U': dict(name='the Undervault', stage=3, act='2', elem='Iron', town='the shaft-head camp', town2='the lift cage',
   lm=['the reactor ring', 'the coolant canal', 'the cryo gallery', 'the engine pistons', 'the drone nests',
       'the collapsed lift', 'the warning lights', 'the pipe bridge', 'the core housing door', 'the maintenance ladder'],
   det=['The walls hummed. I hummed back once. It stopped. I stopped.', 'Warning lights still blink here after nine hundred years. Someone set them well.',
        'Found a crew mug near <loc> with a name scratched off.', 'Coolant fog made my fingers ache.',
        'A pod in the gallery still had a green light. Did not open it. Wrote the number down.',
        'Pistons as tall as the Hold, standing still mid-stroke.', 'Drones repaired a pipe that led nowhere.',
        'Heard dripping for an hour and never found where.', '<name> at the shaft head said nobody comes back up quiet. I came back quiet.',
        'Ship script on every door. I could almost read it.', 'My lamp was the only warm thing for half a mile.', 'The air tasted like old coins.'],
   open=['Down here the walls hum. Don\'t hum back.', 'Shaft-head says nobody\'s been this deep in a century. Shaft-head lies.',
         'Lift\'s working today. Don\'t ask about tomorrow.', 'Bring a lamp, bring a spare, bring a spare for the spare.',
         'They say the engine still has a heartbeat. I\'ve heard it.', 'Rope\'s good. Rope\'s always good. Rope is all we have.'],
   hazard='coolant leaks', saying='Rope is all we have.', food='tinned galley rations', work='shaft salvage',
   fear='the lift failing', insult='"lamp-shy"', weather='Piston', token='rivets', custom='ties a knot in the lift rope for every crew that comes back',
   greeting='"Rope holds."', oath='"Cut my rope."', people='shaft crews'),
 'REG_Q': dict(name='the Quiet', stage=4, act='3', elem='Hollow', town='the Cradle landing', town2='the Threshing Ring',
   lm=['the Threshing Ring', 'the Granary glass', 'the stolen fields hanging in the dark', 'the Hush Core light', 'the curved horizon',
       'the Choirborn barracks', 'the seed vaults', 'the gravity seams', 'the harvest rails', 'the lander'],
   det=['Every step was too long. Gravity is lazy here.', 'Saw a field from Thornwood hanging in glass, ferns still lit.',
        'The floor curved up behind me until I could not look.', 'The quiet here is a sound.', 'A Choirborn spoke in a voice I had heard before.',
        'Found a Thornwood acorn in a seed vault near <loc>. Put it in my pocket.', 'My Ward shimmered at nothing.',
        'The rails carried Shards past like grain.', 'No smell at all. That was the worst part.', 'The lander ticked as it cooled.',
        'Veyl turned slowly in the window. I could see the Hold, I think.', 'I talked to Ostra more than usual. She let me.'],
   open=['You came up. Nobody comes up.', 'Gravity\'s wrong. Your stomach will tell you before I do.',
         'We are a long way from any Anchor. Choose carefully.', 'This is the harvester. Act like it can hear us.',
         'Keep moving. Standing still here feels like being counted.', 'They kept the fields. Look at them.'],
   hazard='gravity seams', saying='Be still and be gathered.', food='nothing', work='harvest', fear='being counted',
   insult='"seed"', weather='Harvest', token='seeds', custom='', greeting='', oath='', people='Choirborn'),
}
FAMILIES = {}
GIVEN = {}


def load_namebanks():
    for r in rd(OUT + '/name_banks.csv'):
        lst = [x.strip() for x in r['names'].split(';') if x.strip()]
        (GIVEN if r['kind'] == 'given' else FAMILIES)[r['region']] = lst
    allg = sum(GIVEN.values(), []) or ['Moll', 'Pim', 'Esme']
    allf = sum(FAMILIES.values(), []) or ['Marr', 'Hale', 'Pell']
    for k in REG:
        GIVEN.setdefault(k, allg)
        FAMILIES.setdefault(k, allf)
        REG[k]['given'] = GIVEN[k]
        REG[k]['family'] = FAMILIES[k]


def reg_of(code):
    return REG.get(code) or REG['REG_HUB']


COMPASS = ['north', 'south', 'east', 'west', 'northeast', 'northwest', 'southeast', 'southwest']

# ---------------------------------------------------------------- voices (quest offers)
V = {
 'knight': dict(
   open=['Post report, sleeper. Short version.', 'Gate holds. Barely. That is why you are here.',
         'Chain of command says I pick my best Knight for this. You are not a Knight. You will do.',
         'You are on the deck and on my roster. Congratulations.', 'I have forty Knights and thirty-one pairs of boots. Listen fast.',
         'Logged at wake-call, handed to you by noon. That is fast for us.', 'Stand there. Not there, that is the drain. There.'],
   ask=['Orders: <task>.', 'Your post is simple. <Task>, then <task2>.', '<Task>. Do it clean and report in person.',
        'I need a hull out there to <task>. Yours is the one not on a duty roster.', 'First, <task>. Then <task2>. In that order, sleeper.',
        'Here is the job. <Task>. Nobody improvises.'],
   aside=['Sergeant <given> bet me a week\'s bread you would say no.', 'If you see Knight-Post Seven, tell them they owe the mess two lights.',
          'Bring back anything with the old crest on it. We keep count.', 'Do not tell the Church about this one until it is done.',
          'Last Knight I sent came back with a goat. Do not come back with a goat.'],
   close=['Logged. Move.', 'That is an order, even if you do not take orders.', 'Back by wake-call, or I send someone to find your hull.',
          'Questions go up the chain. The chain is me. No questions.', 'Dismissed. That means go.']),
 'church': dict(
   open=['Peace on your deck, sleeper. Sit, if the bench will hold you.', 'The Log says a stranger helps where kin cannot. Log, Chapel 2:9. Convenient, that.',
         'Brother <given> fell asleep in the reading again, so the job comes to you.', 'I prayed for help. I will be honest, I pictured someone taller.',
         'Light keep you. I need a favor and a quiet tongue.', 'Wipe your boots. The Log forgives mud. The sexton does not.'],
   ask=['Would you <task>? Gently, if gentleness is possible.', 'There is a small matter: <task>, and then <task2>.',
        'The Log asks little of us. I ask a bit more: <task>.', 'If you could <task>, the Chapel would remember it at dusk reading.',
        'Someone must <task>. The Log does not say who. I am saying you.'],
   aside=['Do not mention it to the Choir. They would make it about singing.', 'Sister <given> keeps a candle lit for this. She would like to put it out.',
          'The Archivists will want it written down. I will want it true.', 'I will bless your boots when you come back. They need it.',
          'There is soup after. There is always soup after.'],
   close=['Go with the Log. Logged.', 'The Fall gave us this world. Go and keep a little of it. Logged.',
          'Come back whole. I hate writing names in the book.', 'Rise, as we rose. Logged.']),
 'salvager': dict(
   open=['Sleeper. You look like someone who is owed money. So am I.', 'Good news: there is work. Bad news: it is the kind I will not do myself.',
         'Do not touch that, it is priced. Sit there. Also priced. Fine, stand.', 'Every job is a fair share job, and today your share is fair-ish.',
         'That crate is not junk, it is Meridian. Junk is cheaper. Here is the job.', 'You have honest hands. I can fix that. Later. First, work.'],
   ask=['Go <task>. Finders keep a tenth, the Guild keeps the rest, everybody is happy.', 'Simple run: <task>, then <task2>. Simple runs pay simple money.',
        'I need you to <task>. Do not haggle. You will lose.', '<Task>. If it is old tin, it is mine. If it is alive, it is your problem.',
        'Job sheet says <task>. Job sheet lies a little. Budget for that.'],
   aside=['<given> swears there is a working cooler down there. <given> also swore off cards.', 'If you break anything shiny, it goes on your tab.',
          'The last crew came back with all their fingers and none of the cargo. Reverse that.', 'Petra wants a cut. Petra always wants a cut. Act surprised.',
          'There is a bonus. There is always a bonus. I just never pay it.'],
   close=['Fair share. Shake on it. Your hand is filthy. Shake anyway.', 'Off you go. The clock is ticking and so is the interest.',
          'Come back rich or come back with a good story. I only pay for one.', 'Finders keepers, sleeper. Mostly me.']),
 'quiet': dict(
   open=['You will listen. Then you will go.', 'Wind from the east. A name on the table. Yours to carry.',
         'There is a contract. It is short. So is the time.', 'Sit. Keep your hood up. You were not here.',
         'Clear sky, cold night. Good weather for this.'],
   ask=['You will <task>. Then you will <task2>.', 'You will <task>. No one will thank you.', 'At dusk you will <task>. After that, the choice is yours.',
        '<Task>. Leave nothing the Knights can follow.', 'You will <task>, and you will be quick about it.'],
   aside=['There is a bonus if no one hears it happen.', 'One leaves. You decide which.', 'The Speaker asked for you by the shape of your hands.',
          'There is a cup of tea on the sill. It is not for you.', 'You will be tempted to ask why. You will not ask.'],
   close=['Clear skies after. Go.', 'Expect rain. Go anyway.', 'When it is done, light no lamp.', 'Fog by morning. Be gone before it lifts.']),
 'choir': dict(
   open=['Hush, hush. No, not that Hush. Just quiet, please.', 'Listen under the noise. There. You heard it.',
         'A voice went flat out in the wilds. We want to know why.', 'The Spire hums a half-tone low today. Bad sign, or bad tuning.',
         'The Precentor sends a request, sung in a minor key.', 'Rest a moment. Rest is part of the song. Now, the work.'],
   ask=['Would you <task>? Take a lens. Try not to scratch it.', 'The chorus needs someone to <task>, then <task2>.',
        'Go and <task>. Note the pitch. Any pitch.', '<Task>. If a Shard sings to you, do not sing back.',
        'Your part in this is simple: <task>.'],
   aside=['Cantor <given> claims it is in E flat. Cantor <given> is tone-deaf.', 'Bring back the rest you hear, the silence between the notes.',
          'The Church will call this heresy. The Church calls breakfast heresy.', 'Do not lend the lens to an Archivist. They never return lenses.',
          'If your ears ring after, that is normal. If they sing, come see me.'],
   close=['Go in tune.', 'Hold the note. Go.', 'Come back with an ear full of it.', 'Mind the rests. They matter most.']),
 'ires': dict(
   open=['Sleeper. Stand straight. You are on a bridge, whatever it looks like.', 'A deal is a deal. I am offering one.',
         'Crewman. Kindled. Whatever you are calling yourself this year.'],
   ask=['Your task: <task>. Then <task2>.', 'You will <task>. I keep my promises. They are heavy, but I keep them.',
        '<Task>. That is the whole of it.'],
   aside=['I have carried this longer than your manifest has had a name.', 'I signed for this once. I am still signing.'],
   close=['That is my word. Take it or do not.', 'Dismissed, crewman.']),
 'hush': dict(
   open=['We are glad you came. We are always glad.', 'Hello, ship. Hello, the one carrying it.'],
   ask=['We would like you to <task>. We do not mind if you refuse.', '<Task>. Then <task2>. We will wait. We are good at waiting.'],
   aside=['A field is not angry with the rain.', 'We never lie. It saves so much time.'],
   close=['Go well. We will see you.', 'You are almost ready.']),
 'villager': dict(
   open=[],
   ask=['I need someone to <task>.', 'Could you <task>? I would go, but my knees do not bend that way anymore.',
        'Here is the job: <task>. After that, <task2>.', 'Nobody else will <task>, and I have asked everybody twice.',
        '<Task>. That is all. Well, that and <task2>.', 'If you <task>, I will owe you, and I pay my debts. Mostly.',
        'You look like you could <task> without fuss. Could you?'],
   aside=['<given> down the lane will swear I am exaggerating. <given> is wrong.', 'If you pass <town2>, tell my cousin I am alive and still right.',
          'I can pay in lights or soup. The soup is better.', 'My manifest thinks I am mad for asking a sleeper. My manifest is cold-slept, all of them.',
          'Bring back my kettle if you see it. Long story.', 'Do not tell the reeve. The reeve worries, and then I have to listen to it.',
          'The <family> family said a Kindled would not bother. Prove them wrong. Please.'],
   close=['Go on, then. Before I change my mind.', 'Green board when you are back, I hope.', 'Logged? Logged. Go.', 'I will keep the stove going.',
          'Mind yourself out there. Hulls do not patch like they used to.', 'I will be here. Where else would I be.']),
}
OSTRA_GIVER = {
 1: dict(open=['Status: you are awake. Good.', 'Noted. Something needs doing. It is you.', 'Correction: we are not resting. We are going.',
               'Ship mind to sleeper. Pay attention.'],
         ask=['Objective: <task>. Then <task2>.', 'Proceed. <Task>.', 'Priority one: <task>.', 'Plan: <task>. I made the plan. It is a good plan.'],
         aside=['I checked the numbers twice. Three times. They are fine.', 'Unknown cause. I dislike unknown.', 'Do not touch the glowing parts. Correction: touch them carefully.'],
         close=['Go.', 'Moving now would be efficient.', 'I will be here. I am always here.']),
 2: dict(open=['I think we should go. I think.', 'Can I ask you something? Later. It can wait.', 'I keep finding gaps. In the map. In me. Never mind.'],
         ask=['I think we need to <task>. Then <task2>.', 'Will you <task>? I would, but I am in your chest.', '<Task>. Do you agree? I think you agree.'],
         aside=['I remember this place. I do not remember remembering it.', 'Tell me if I repeat myself. I have started to.'],
         close=['Go. I will keep count.', 'I think that is all. It is not all. Go anyway.']),
 3: dict(open=['I had the numbers. I need you to listen anyway.', 'Thirty-seven thousand. I know. I will not say it again today.', 'Please.'],
         ask=['<Task>. Then <task2>. I owe them that.', 'We have to <task>. I cannot fix it. You can try.', '<Task>. I am sorry it is you.'],
         aside=['I kept every number. I just did not keep them safe.', 'You can be angry. Do it walking.'],
         close=['Go.', 'I will be quiet. Unless you need me.']),
 4: dict(open=['Whatever you choose, I will hold the door.', 'We are close now. I would like to say this properly.', 'I have stopped counting. It helps, a little.'],
         ask=['When you are ready, <task>. After that, <task2>.', 'The next step is to <task>. The step after is yours to choose.', 'I think it is time to <task>.'],
         aside=['You were right about me before I was. Thank you for waiting.', 'I am not afraid. I checked.'],
         close=['I am with you.', 'Go when you are ready.']),
}
COMPANION = {
 'ACT_CMP_C1': (['Do not salute. I am done with that.', 'My old squad is on the road again. I can smell their boot grease.', 'I need a hand. Not a Knight. A hand.'],
                ['Watch my left. I will watch yours.', 'If it goes wrong, I am the one they want. Remember that.']),
 'ACT_CMP_C2': (['I found another page. It should not exist either.', 'Forgive me, I have been up since wake-call reading the same line.', 'The Log has a gap shaped exactly like a question.'],
                ['Bring a pencil. Two. I break them.', 'If the Archivists ask, we are cataloguing hymnals.']),
 'ACT_CMP_C3': (['One last job. I know. I always say that.', 'Before you ask: yes, I owe her money. No, not that much. Some.', 'I have a plan. It has two holes. You are one of the fillings.'],
                ['Fair share, partner. Fifty-fifty. Sixty-forty. We will talk.', 'If I run, run faster.']),
 'ACT_CMP_C4': (['You will come with me. That was not a question.', 'I was told to watch you. I am telling you instead.', 'There is a name on my list. I want it off.'],
                ['Quiet feet.', 'Do not thank me. It makes it harder.']),
 'ACT_CMP_C5': (['The song got louder last night. I need to do something about it.', 'Sorry. I am listening to two things at once. Go on. No, I will go on.', 'I can hear her in you. Ostra. She hums when she is worried.'],
                ['If I start humming, hit me. Gently.', 'Stay close. It is quieter near you.']),
 'ACT_CMP_C6': (['I have a cure that works half the time. I want the other half.', 'Wash your hands. Now listen.', 'Three patients this morning. One asked for her mother, then for my name.'],
                ['Bring clean cloth if you see any.', 'Do not die. I am out of the good bandages.']),
 'ACT_CMP_C7': (['The Moot will want my head. I would like to keep it.', 'My clan has a feud with a family that ran out of members. We are still feuding.', 'Root deep or blow away. I am tired of blowing away.'],
                ['Walk behind me at the Moot. Not too close. It is rude.', 'If they draw, I draw. You decide after.']),
 'ACT_CMP_C8': (['Maintenance request logged. Requester: Unit 9. Priority: personal.', 'Query: do you have time. Assumption: yes.', 'My orders say repair. My orders are nine hundred years old. I would like new ones.'],
                ['Proceeding. Please remain near for repair.', 'I will count your steps. It is soothing.']),
}
COMP_ASK = ['Help me <task>.', 'I need you to <task>. Then <task2>.', 'We <task>. Together, or not at all.', 'First we <task>. After that, <task2>.',
            'Will you <task>? I would ask someone else, but there is no one else.', 'The job is to <task>. I will explain the rest on the road.',
            'All I need is for us to <task>.']
FAC_VOICE = {'FAC_HULLKNIGHTS': 'knight', 'FAC_LANTERNCHURCH': 'church', 'FAC_SALVAGERS': 'salvager',
             'FAC_QUIETHAND': 'quiet', 'FAC_CHOIR': 'choir'}
NPC_FAC = {}

# step-type banks: objective (UI, max 60), task phrase (offer), journal frame (past), direction endpoint mode
OBJ = {
 'go': ['Reach <l>', 'Travel to <l>', 'Head for <l>', 'Make your way to <l>', 'Get to <l>', 'Go to <l>'],
 'talk': ['Speak with <t>', 'Find <t> and talk', 'Talk to <t>', 'Ask <t> what happened', 'Hear <t> out', 'Talk to <t> at <l>'],
 'kill': ['Defeat <t>', 'Clear <t> from <l>', 'Put down <t>', 'Drive off <t>', 'Kill <t>', 'Deal with <t>'],
 'collect': ['Collect <c><t>', 'Gather <c><t>', 'Recover <c><t>', 'Bring back <c><t>', 'Find <c><t>'],
 'interact': ['Use <t>', 'Examine <t>', 'Activate <t>', 'Search <t>', 'Inspect <t>'],
 'escort': ['Escort <t> to <l>', 'Get <t> safely to <l>', 'Lead <t> to <l>', 'Walk <t> to <l>', 'Escort <t>'],
 'defend': ['Defend <l>', 'Hold <l>', 'Protect <t>', 'Keep <t> safe', 'Hold the line at <l>'],
 'stealth': ['Slip into <l> unseen', 'Get past <t> unseen', 'Sneak into <l>', 'Stay hidden in <l>', 'Move through <l> unseen'],
 'puzzle': ['Solve <t>', 'Open <t>', 'Work out <t>', 'Unlock <t>', 'Figure out <t>'],
 'choice': ['Decide the fate of <t>', 'Make your choice', 'Choose what happens to <t>', 'Decide about <t>', 'Make the call on <t>'],
 'survive': ['Survive at <l>', 'Hold out at <l>', 'Survive the attack', 'Last until wake-call', 'Stay alive at <l>'],
 'boss': ['Defeat <t>', 'Face <t>', 'Bring down <t>', 'Fight <t>', 'Defeat <t> at <l>'],
}
MODE = {'go': 'place', 'talk': 'person', 'kill': 'foe', 'collect': 'thing', 'interact': 'thing', 'escort': 'person',
        'defend': 'place', 'stealth': 'place', 'puzzle': 'thing', 'choice': 'person', 'survive': 'place', 'boss': 'foe'}
ROUTE = ['From <from>, head <dir> along <lm1>.', 'Leave <from> by the <dir> road and keep <lm1> on the left.',
         'Start at <from> and walk <dir> until <lm1> falls behind.', 'Take the <dir> track out of <from>, past <lm1>.',
         'Go <dir> from <from>; <lm1> marks the halfway point.', 'From the Anchor nearest <from>, follow <lm1> <dir>.',
         'Pass <lm1>, <dir> of <from>.', 'Ride <dir> from <from> and keep <lm1> in sight.',
         'Leave <from> heading <dir>, with <lm1> on the right.', 'Walk <dir> out of <from> and climb toward <lm1>.',
         'Follow <lm1> <dir> from <from>.', 'Head <dir> of <from> until <lm1> is close enough to touch.']
END = {
 'place': ['Past <lm2>, look for <dest>.', 'Watch for <dest> just below <lm2>.', 'At <lm2>, turn toward <dest>.',
           'Find <dest> between <lm2> and the next Anchor.', 'Look for <dest> near <lm2>.', 'Beyond <lm2>, the path ends at <dest>.'],
 'person': ['Ask after <dest> by <lm2>.', 'Look for <dest> in the shadow of <lm2>.', 'Listen for <dest> near <lm2>.',
            'Near <lm2>, ask anyone for <dest>.', 'Search around <lm2> for <dest>.', 'Wait at <lm2> and expect <dest>.'],
 'foe': ['Listen for <dest> past <lm2>.', 'Expect <dest> where <lm2> narrows.', 'Tracks lead from <lm2> straight to <dest>.',
         'Watch the far side of <lm2> for <dest>.', 'Approach <lm2> slowly and expect <dest>.', 'Beyond <lm2>, expect trouble: <dest>.'],
 'thing': ['Search around <lm2> for <dest>.', 'Check the ground by <lm2> for <dest>.', 'Look under <lm2> for <dest>.',
           'Look near <lm2> for <dest>.', 'From <lm2>, scan the ground for <dest>.', 'Search the area past <lm2> for <dest>.'],
}
JRN_TAIL = {
 'go': ['Took longer than it looked on the map.', 'Nobody stopped me. Nobody waved, either.', 'Rested at the Anchor on the way.'],
 'talk': ['Talked more than I expected. Listened more than that.', 'Left with more questions than I brought.', 'Got the truth, or a version of it.'],
 'kill': ['My hands shook after. They stopped.', 'It was quick. That is the best I can say.', 'Cleaned my blade twice.'],
 'collect': ['Heavier than it looked.', 'Counted twice to be sure.', 'Wrapped it in a spare shirt.'],
 'interact': ['It worked on the second try.', 'Something clicked, deep inside.', 'Ostra went quiet for a moment after.'],
 'escort': ['Nobody got left behind.', 'Kept the pace slow. It was not my pace to set.', 'Heard a lot of complaints. All of them alive.'],
 'defend': ['It held. Barely.', 'Counted the dents after. A lot of dents.', 'Nobody broke through.'],
 'stealth': ['Held my breath longer than I knew I could.', 'Nobody saw me. I think.', 'My knees hurt from crouching.'],
 'puzzle': ['Felt clever for a full minute.', 'Ostra pretended she had known all along.', 'Wrong twice, right once. Once is enough.'],
 'choice': ['I will think about this one tonight.', 'Wrote it down so I would own it.', 'Nobody told me it was right.'],
 'survive': ['Still on the deck.', 'Wake-call never looked so good.', 'Slept badly after.'],
 'boss': ['Sat down for a long time after.', 'Still on the deck. Barely.', 'The quiet after was the loudest part.'],
}
TASK = {'go': 'get to <l>', 'talk': 'find <t>', 'kill': 'deal with <t>', 'collect': 'bring back <c><t>', 'interact': 'look at <t>',
        'escort': 'walk <t> to <l>', 'defend': 'hold <l>', 'stealth': 'get into <l> unseen', 'puzzle': 'open <t>',
        'choice': 'settle what happens to <t>', 'survive': 'last the night at <l>', 'boss': 'face <t>'}
QNAME_PROPOSED = {'QST_HK_00': 'Report to the Gate', 'QST_LC_00': 'Evening Reading', 'QST_SG_00': 'Finders\' Fee',
                  'QST_CH_00': 'The Listening Lesson', 'QST_CHOIR_01': 'Stock for the Archivist', 'QST_QH_00': 'A Name on the Table'}

# ---------------------------------------------------------------- campaign loading
def load_campaign():
    """Campaign CSVs win; if they hold no rows, read the seeds (same schema). Returns (quests, source)."""
    qs = rd(CAMP + '/quests.csv')
    if qs:
        steps = collections.defaultdict(list)
        for s in rd(CAMP + '/quest_steps.csv'):
            steps[s['qst_id']].append(s)
        brs = collections.defaultdict(list)
        for b in rd(CAMP + '/quest_branches.csv'):
            brs[b['qst_id']].append(b)
        out = []
        for q in qs:
            st = sorted(steps[q['qst_id']], key=lambda s: int(s.get('order') or 0))
            out.append(dict(id=q['qst_id'], name=q['name'], type=q.get('type', ''), line=q.get('line', ''), act=q.get('act', ''),
                            region=q.get('region', ''), giver=q.get('giver', ''), summary=q.get('summary', ''),
                            journal=q.get('journal', ''),
                            steps=[dict(text=s.get('objective', ''), type=s.get('type', ''), target=s.get('target', ''), loc=s.get('loc', ''),
                                        count=s.get('count') or 1, optional=s.get('optional', '')) for s in st],
                            branches=[dict(choice=b.get('choice', ''), outcome=b.get('outcome', ''), id=b.get('branch_id', '')) for b in brs[q['qst_id']]]))
        return out, 'design/campaign CSVs'
    out = []
    for p in sorted(glob.glob(CAMP + '/seeds/*.json')):
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception as e:
            print('WARN seed unreadable', p, e)
            continue
        if isinstance(d, list):
            for q in d:
                if isinstance(q, dict) and 'steps' in q and q.get('id'):
                    out.append(q)
    return out, ('design/campaign/seeds/*.json (CSVs empty)' if out else 'none')


def synth_world(w):
    """Skeleton steps for a data/world quest the campaign has not designed yet (placeholder)."""
    r = w['region'] if w['region'] in REG else 'REG_HUB'
    k = w['qst_id']
    rg = rng(k)
    sites = [x['loc_id'] for x in rd(OUT + '/place_names.csv') if x['region'] == r and x['kind'] == 'Lore site'] or ['LOC_SITE_%s_01' % r]
    s1, s2 = rg.sample(sites, 2) if len(sites) > 1 else (sites[0], sites[0])
    npc = {'REG_01': 'ACT_NPC_REEVE_ANNIK', 'REG_02': 'ACT_NPC_HARBOR_MOSS', 'REG_03': 'ACT_NPC_BRIAR_REEVE_HOLT',
           'REG_04': 'ACT_NPC_MIRAGE_SABA', 'REG_05': 'ACT_NPC_HEARTH_ELDER_YURI', 'REG_06': 'ACT_NPC_LASTLIGHT_BEA'}.get(r, 'ACT_NPC_COUNCIL_CLERK')
    lead = {'REG_04': 'ACT_REMNANT_LEADER', 'REG_05': 'ACT_CHOIRBORN_LEADER', 'REG_06': 'ACT_CHOIRBORN_LEADER'}.get(r, 'ACT_THORN_LEADER')
    town = 'LOC_TOWN_%s_01' % r if r.startswith('REG_0') else 'LOC_LANTERN_HOLD'
    if w['kind'].startswith('Exotic'):
        item = name_of(w['reward'])
        steps = [dict(type='talk', target=npc, loc=town), dict(type='go', target='', loc=s1),
                 dict(type='interact', target='the Choir stone', loc=s1),
                 dict(type='collect', target='%s Shard splinter' % REG[r]['elem'], loc=s1, count=3),
                 dict(type='kill', target=lead, loc=s2), dict(type='interact', target=item, loc=s2, text='Claim ' + item)]
        return dict(id=k, name=item, type='Shardborn', line='SHB', region=r, giver=npc, summary='', steps=steps, branches=[],
                    _proposed=True)
    leader = {'FAC_HULLKNIGHTS': 'ACT_NPC_HULLKNIGHT_COMMANDER', 'FAC_LANTERNCHURCH': 'ACT_NPC_LANTERN_ARCHIVIST',
              'FAC_SALVAGERS': 'ACT_NPC_SALVAGER_BOSS', 'FAC_CHOIR': 'ACT_NPC_CHOIR_PRECENTOR',
              'FAC_QUIETHAND': 'ACT_NPC_QUIETHAND_SPEAKER'}.get(w['fac_id'], 'ACT_NPC_COUNCIL_CLERK')
    task = {'FAC_HULLKNIGHTS': dict(type='defend', target='the Knights\' Gate', loc='LOC_CQ_HUB_KNIGHTS_GATE'),
            'FAC_LANTERNCHURCH': dict(type='interact', target='the Log terminal', loc='LOC_CQ_HUB_LOG_CHAPEL'),
            'FAC_SALVAGERS': dict(type='collect', target='salvage tag', count=3, loc='LOC_CQ_HUB_UNDERMARKET'),
            'FAC_CHOIR': dict(type='interact', target='the Choir lens', loc='LOC_CQ_HUB_CHOIR_SPIRE')}.get(w['fac_id'], dict(type='go', target='', loc='LOC_LANTERN_HOLD'))
    steps = [dict(type='talk', target=leader, loc='LOC_LANTERN_HOLD'), dict(type='go', target='', loc=task['loc']), task,
             dict(type='talk', target=leader, loc='LOC_LANTERN_HOLD', text='Report to ' + name_of(leader))]
    return dict(id=k, name=QNAME_PROPOSED.get(k, w['name']), type='Faction', line=w['fac_id'], region='REG_HUB', giver=leader,
                summary='', steps=steps, branches=[], _proposed=True)


def thing_name(x):
    x = re.sub(r'\s*\((?:if|unless|when)\b[^)]*\)?', '', x or '').strip()   # flag conditions are design notes, not player text
    x = re.sub(r'\s*\([^)]*\b[A-Z]+_[A-Z0-9_]+[^)]*\)', '', x).strip()   # bracketed ID notes too
    if not IDRE.match(x):
        x = scrub(x)
    n = name_of(x)
    if not n:
        return ''
    if IDRE.match(x or '') or x in NAMES:
        return n
    if re.match(r'(?i)^(a|an|the|any|all|every|each|some|two|three|four|five|six|\d|her|his|their|my|your)\b', n):
        return low1(n)
    if n[:1].isupper() and len(n.split()) <= 3 and all(w[:1].isupper() for w in n.split()):
        return n
    if re.match(r"^[A-Z][\w-]*'s\b", n):
        return n
    return 'the ' + low1(n)


def voice_of(q):
    g = q.get('giver') or ''
    region = q.get('region') or 'REG_HUB'
    line = q.get('line') or ''
    if g == 'ACT_NPC_OSTRA':
        return 'ostra', OSTRA_GIVER[reg_of(region)['stage']]
    if g in COMPANION:
        o, c = COMPANION[g]
        return 'companion', dict(open=o, ask=COMP_ASK, aside=[], close=c)
    if 'IRES' in g:
        return 'ires', V['ires']
    if 'HUSH' in g:
        return 'hush', V['hush']
    fac = NPC_FAC.get(g) or (line if line in FAC_VOICE else '')
    if not fac:
        for pre, f in (('ACT_NPC_HK_', 'FAC_HULLKNIGHTS'), ('ACT_NPC_LC_', 'FAC_LANTERNCHURCH'), ('ACT_NPC_SG_', 'FAC_SALVAGERS'),
                       ('ACT_NPC_QH_', 'FAC_QUIETHAND'), ('ACT_NPC_CH_', 'FAC_CHOIR')):
            if g.startswith(pre):
                fac = f
    if fac in FAC_VOICE:
        return FAC_VOICE[fac], V[FAC_VOICE[fac]]
    vb = dict(V['villager'])
    vb['open'] = reg_of(region)['open']
    return 'villager', vb


def human_line(q):
    s = scrub(q.get('summary') or '')
    sents = [x.strip() for x in re.split(r'(?<=[.!?])\s+', s) if x.strip()]
    best, bs = None, -99
    for i, x in enumerate(sents):
        if not (40 <= len(x) <= 220):
            continue
        if re.match(r'(?i)(if|reward|unlock|this quest|optional|branch|then|after|when|once|whether|depending|either|meanwhile)\b', x):
            continue
        if re.search(r"(?i)\bor (not|doesn't|does not|don't)\b|\bthe player (can|may|must|chooses)", x):
            continue
        sc = i / max(1, len(sents))
        if re.search(r"(?i)\b(wants?|asks?|keeps?|would like|gives?|hands?|laughs?|cries|names?|writes?|kettle|tea|bread|letter|son|daughter|mother|father|sister|brother|child)\b", x):
            sc += 2
        if re.search(r"(?i)\b(Hush|Shard|harvest|core|Weave)\b", x):
            sc -= 0.5
        if sc > bs:
            best, bs = x, sc
    return notebook(best) if best else None


DONE_FALLBACK = ['<Giver> said thank you twice, the second time quieter.', '<Giver> made tea and forgot to drink it. So did I.',
                 '<Giver> laughed for the first time since I met them, at nothing much.', '<Giver> wrote my name in a ledger, next to the price of salt.',
                 '<Giver> asked me to stay for supper. I stayed.', '<Giver> did not say anything. Just nodded. It was plenty.',
                 '<Giver> gave me <thing> and would not hear a word about it.', '<Giver> was already asleep in a chair when I got back. Left a note.',
                 '<Giver> asked what it was like out there. Told the truth, mostly.', '<Giver> counted the lights twice and then paid me double by mistake. I gave half back.']


def gen_quests():
    camp, src = load_campaign()
    world = rd(DATA + '/world/quests.csv')
    have = {q['id'] for q in camp}
    quests = list(camp)
    world_only = [w for w in world if w['qst_id'] not in have]
    for w in world_only:
        quests.append(synth_world(w))
    exp = sum(3 + 3 * len(q.get('steps', [])) + 2 * len(q.get('branches', [])) for q in quests)
    T = Table('quest_text', exp)
    for q in quests:
        qid = q['id']
        region = q.get('region') if q.get('region') in REG else 'REG_HUB'
        R = reg_of(region)
        rg = rng(qid)
        gname = name_of(q.get('giver', '')) or 'the giver'
        vname, vb = voice_of(q)
        prop = q.get('_proposed')
        base_note = ('world quest; steps are a placeholder skeleton until the campaign designs it' if prop else 'source: ' + src)
        # NAME
        nm = q.get('name') or qid
        T.add('STR_%s_NAME' % qid, qid, 'quest_name', nm, 32 if len(nm) <= 32 else None,
              notes=('proposed title; world name "%s" is a placeholder' % next((w['name'] for w in world if w['qst_id'] == qid), '')) if prop else 'campaign name')
        # step contexts
        ctx = []
        for i, s in enumerate(q.get('steps', []), 1):
            st = (s.get('type') or 'go').strip().lower()
            if st not in OBJ:
                st = 'interact'
            tgt_raw = s.get('target') or ''
            t = thing_name(tgt_raw)
            l = name_of(s.get('loc') or '') or R['town']
            try:
                cnt = int(float(s.get('count') or 1))
            except ValueError:
                cnt = 1
            if cnt > 1 and t:
                t = plural(re.sub(r'^the ', '', t))
            c = '%d ' % cnt if cnt > 1 else ''
            if not t:
                t = l
            ctx.append(dict(i=i, type=st, t=t, l=l, c=c, text=(s.get('text') or '').strip(), raw=tgt_raw, opt=str(s.get('optional')).lower() in ('true', '1', 'yes')))
        # OFFER
        tasks = []
        for c in ctx:
            if c['type'] == 'choice' or (c['type'] == 'talk' and c['raw'] == q.get('giver')):
                continue
            tk = c['text'] if c['text'] and len(c['text']) <= 60 else fill(TASK[c['type']], dict(t=c['t'], l=c['l'], c=c['c']), rg)
            tk = low1(tk.rstrip('.'))
            if tk not in tasks:
                tasks.append(tk)
            if len(tasks) == 2:
                break
        if not tasks:
            tasks = ['help me with something that will not wait']
        first = gname.split()[0] if gname else ''
        if first and vname in ('companion', 'villager', 'knight', 'church', 'salvager', 'choir', 'quiet'):
            tasks = [re.sub(r"\b%s's\b" % re.escape(first), 'my', re.sub(r'\b%s\b(?!\')' % re.escape(first), 'me', t)) for t in tasks]
            tasks = [re.sub(r'\b(follow|escort|meet|find) me\b', 'go', t) for t in tasks]
        slots = dict(task=tasks[0], task2=tasks[1] if len(tasks) > 1 else '', given=R['given'], family=R['family'],
                     town=R['town'], town2=R['town2'])
        ask = [a for a in vb['ask'] if (len(tasks) > 1 or '<task2>' not in a)]
        bid = 'offer_%s' % vname
        variants = [[(bid + '_o', vb['open'], slots), (bid + '_a%d' % len(tasks), ask, slots), (bid + '_s', vb.get('aside') or vb['close'], slots), (bid + '_c', vb['close'], slots)],
                    [(bid + '_o', vb['open'], slots), (bid + '_a%d' % len(tasks), ask, slots), (bid + '_c', vb['close'], slots)],
                    [(bid + '_o', vb['open'], slots), (bid + '_a%d' % len(tasks), ask, slots)]]
        if vname == 'companion':
            variants = [v for v in variants[1:]]
        txt = None
        for parts in variants:
            parts = [p for p in parts if p[1]]
            txt = T.compose(qid + '_OFFER', parts, 300, soft=True)
            if txt:
                break
        if not txt:
            txt = T.compose(qid + '_OFFER2', [(bid + '_a1', [a for a in vb['ask'] if '<task2>' not in a], dict(slots, task=tasks[0][:200]))], 300)
        T.add('STR_%s_OFFER' % qid, qid, 'quest_offer', txt, 300, notes='voice: %s (%s)' % (vname, gname))
        # steps
        for c in ctx:
            n = '%02d' % c['i']
            sl = dict(t=c['t'], l=c['l'], c=c['c'])
            if c['text'] and len(c['text']) <= 60 and c['text'].rstrip('.') not in T.texts:
                obj = c['text'].rstrip('.')
                T.add('STR_%s_STEP_%s' % (qid, n), qid, 'step_objective', obj, 60, notes='campaign step text' + ('; optional' if c['opt'] else ''))
                T.texts.add(obj)
            else:
                obj = T.compose('%s_S%s' % (qid, n), [('obj_' + c['type'], OBJ[c['type']], sl)], 60, soft=True)
                if not obj:
                    obj = T.compose('%s_S%sb' % (qid, n), [('obj_' + c['type'] + '_short', [x for x in OBJ[c['type']] if '<l>' not in x] or ['Continue'], dict(sl, t=c['t'][:40], l=''))], 60)
                T.add('STR_%s_STEP_%s' % (qid, n), qid, 'step_objective', obj, 60, notes=('generated from type %s' % c['type']) + (('; campaign text over 60' if len(c['text']) > 60 else '; campaign text "%s" repeats another step, varied' % c['text']) if c['text'] else ''))
            # DIR
            lm1, lm2 = rng(qid + n + 'lm').sample(R['lm'], 2)
            frm = R['town2'] if c['l'] == R['town'] else rng(qid + n).choice([R['town'], R['town2']])
            mode = MODE[c['type']]
            dest = c['l'] if mode == 'place' else c['t']
            dl = dict(frm=frm, dir=COMPASS, lm1=lm1, lm2=lm2, dest=dest)
            dl['from'] = frm
            d = T.compose('%s_D%s' % (qid, n), [('dir_route', ROUTE, dl), ('dir_end_' + mode, END[mode], dl)], 160, soft=True)
            if not d:
                d = T.compose('%s_D%sb' % (qid, n), [('dir_route', ROUTE, dl), ('dir_end_' + mode, END[mode], dict(dl, dest=dest[:50]))], 160, soft=True) \
                    or T.compose('%s_D%sc' % (qid, n), [('dir_route', ROUTE, dl)], 160)
            T.add('STR_%s_STEP_%s_DIR' % (qid, n), qid, 'step_direction', d, 160,
                  notes='Explorer mode (plan 3.8); landmarks are writing choices, level design to confirm')
            # JRN
            pastobj = to_past(obj)
            js = dict(name=R['given'], loc=c['l'], town=R['town'])
            pools = [('jrn_det_' + region, R['det'], js), ('jrn_tail_' + c['type'], JRN_TAIL[c['type']], js)]
            pool = pools[rng(qid + n + 'p').randrange(2)]
            j = T.compose('%s_J%s' % (qid, n), [('fixed_' + qid + n, [pastobj + '.'], {}), pool], 220, soft=True) \
                or T.compose('%s_J%sb' % (qid, n), [('fixed_' + qid + n, [pastobj + '.'], {}), pools[0], pools[1]], 220)
            T.add('STR_%s_JRN_%s' % (qid, n), qid, 'journal_entry', j, 220, notes='past tense notebook')
        # branches
        for bi, b in enumerate(q.get('branches', []), 1):
            n = '%02d' % bi
            ch = scrub(b.get('choice') or '').rstrip('.')
            lab = ch
            if len(lab) > 50:
                for sep in (',', ';', ' and ', ' to ', ' but ', ' (', ' with '):
                    if sep in lab and len(lab.split(sep)[0]) <= 50 and len(lab.split(sep)[0]) >= 8:
                        lab = lab.split(sep)[0]
                        break
            if len(lab) > 50:
                lab = lab[:50].rsplit(' ', 1)[0]
            if lab in T.texts:
                lab = (lab[:44] + ' (%s)' % n) if len(lab) > 44 else lab + ' (%s)' % n
            T.add('STR_%s_BR_%s' % (qid, n), qid, 'branch_label', lab, 50, notes='from campaign choice' + ('; shortened' if lab != ch else ''))
            outc = notebook(scrub(b.get('outcome') or ''))
            head = to_past(ch) + '.'
            o = head
            for sent in re.split(r'(?<=[.!?])\s+', outc):
                if sent and len(o) + 1 + len(sent) <= 220:
                    o = o + ' ' + sent
                else:
                    break
            if len(o) > 220:
                o = o[:217].rsplit(' ', 1)[0] + '.'
            if o in T.texts:
                o = (o[:200] + ' Wrote it down.') if len(o) <= 205 else o[:205].rsplit(' ', 1)[0] + '. Noted.'
            T.add('STR_%s_BR_%s_OUT' % (qid, n), qid, 'branch_outcome', o, 220, notes='from campaign outcome; writer to voice')
        # DONE
        jl = scrub(q.get('journal') or '')
        h = human_line(q)
        if jl and len(jl) <= 220 and jl not in T.texts:
            T.add('STR_%s_DONE' % qid, qid, 'quest_done', jl, 220, notes='campaign journal line' + ('; summary human moment for the writer: ' + h if h else ''))
        elif h and h not in T.texts:
            T.add('STR_%s_DONE' % qid, qid, 'quest_done', h, 220, notes='human moment from campaign summary')
        else:
            thing = next((c['t'] for c in ctx if c['type'] == 'collect'), 'a cup of something hot')
            d = T.compose(qid + '_DONE', [('done_fb', DONE_FALLBACK, dict(giver=gname, thing=thing)), ('done_det_' + region, R['det'], dict(name=R['given'], loc=R['town'], town=R['town']))], 220)
            T.add('STR_%s_DONE' % qid, qid, 'quest_done', d, 220, notes='template; campaign summary had no usable human moment')
    return T, quests, src, len(camp), world_only

# ---------------------------------------------------------------- radiant
RAD_FAC = {'RAD_01': 'FAC_HULLKNIGHTS', 'RAD_02': 'FAC_SALVAGERS', 'RAD_03': 'FAC_HULLKNIGHTS', 'RAD_04': 'none (settlement boards)',
           'RAD_05': 'FAC_SALVAGERS', 'RAD_06': 'FAC_SALVAGERS', 'RAD_07': 'FAC_SALVAGERS', 'RAD_08': 'FAC_HULLKNIGHTS',
           'RAD_09': 'FAC_LANTERNCHURCH', 'RAD_10': 'FAC_CHOIR', 'RAD_11': 'FAC_LANTERNCHURCH; FAC_QUIETHAND', 'RAD_12': 'FAC_QUIETHAND'}
FAC_KEY = {'FAC_HULLKNIGHTS': 'knight', 'FAC_SALVAGERS': 'salvager', 'FAC_LANTERNCHURCH': 'church', 'FAC_CHOIR': 'choir', 'FAC_QUIETHAND': 'quiet'}
RAD_FALLBACK = [('RAD_%02d' % i, n, s) for i, (n, s) in enumerate([
    ('Hollowed Bounty', 'bounty'), ('Remnant Bounty', 'bounty'), ('Clan Bounty', 'bounty'), ('Field Hunt Contract', 'bounty'),
    ('Salvage Run: Wreck Section', 'salvage'), ('Salvage Run: Undervault Shaft', 'salvage'), ('Salvage Run: Glass Field', 'salvage'),
    ('Rescue: Lost Caravan', 'rescue'), ('Rescue: Hollowing Watch', 'rescue'), ('Rescue: Taken by the Choir', 'rescue'),
    ('Rescue: Shard-ghost Recovery', 'rescue'), ('Bounty: Rogue Kindled', 'bounty')], 1)]
BOARD_OPEN = {
 'knight': ['BY ORDER OF THE KNIGHTS\' GATE.', 'Posted by the Gate, logged at wake-call.', 'Hull Knights notice. Read it, then act on it.',
            'Knights\' warrant, open to any hull that can swing.', 'From the duty sergeant, who is busy.', 'Gate business. Volunteers wanted, cowards noted.',
            'Posted under the chain of command.'],
 'salvager': ['GUILD JOB. Fair share terms.', 'Undermarket board, priced to move.', 'Salvagers\' Guild job sheet.', 'Finders wanted. Keepers negotiable.',
              'Guild factor posting. No refunds.', 'Work for hands with no fear of old tin.', 'Job\'s open. Petra\'s watching.'],
 'church': ['Lantern Church almonry. Peace on your deck.', 'Posted at the Log Chapel door.', 'The Church asks; the Log remembers.',
            'A request from the almoners, in kindness.', 'Read at dusk. Answered by anyone.', 'Church notice. Logged.', 'For the attention of a charitable hull.'],
 'choir': ['Choir Spire, in a minor key.', 'The chorus asks a favor.', 'Posted by the Cantors. Listen carefully.', 'A voice is missing.',
           'Spire notice. Sung once, written down twice.', 'From the Precentor\'s office, quietly.', 'From the Choir, who hear more than they say.'],
 'quiet': ['A contract, left where you would find it.', 'Read once. Burn after.', 'No name. No seal. A job.', 'You found this. That was the test.',
           'Weather: clear. Contract: open.', 'Folded twice, left under a stone.', 'For one reader only.'],
 'settlement': ['HUNTERS\' BOARD.', 'Village notice, pinned with a fishhook.', 'Posted by the reeve\'s clerk.', 'Help wanted. We mean it.',
                'Settlement board, weather-stained.', 'From the people of this town.', 'Read this. Then tell your cousin.'],
}
BOARD_CLOSE = {
 'knight': ['Pay: {VAR_reward}. Report at the Gate.', '{VAR_reward} on delivery of proof. Logged.', 'Bounty {VAR_reward}. No proof, no pay.',
            'Reward {VAR_reward}, and the sergeant\'s nod.', '{VAR_reward}, paid at the Gate. Boots extra.', 'Fee: {VAR_reward}. The chain of command thanks you.'],
 'salvager': ['Pays {VAR_reward}. Fair share applies.', '{VAR_reward} on the barrel. Haggling costs ten percent.', 'Fee {VAR_reward}, minus breakages.',
              '{VAR_reward}. Do not ask Petra for more. She will say yes and mean no.', 'Reward: {VAR_reward}. Receipts are for the weak.', '{VAR_reward} in lights, or a favor worth more.'],
 'church': ['The Chapel offers {VAR_reward} and a blessing.', '{VAR_reward} from the alms box. Logged.', 'Reward {VAR_reward}. Soup after.',
            'Offering: {VAR_reward}. The Log forgets nothing, including you.', '{VAR_reward}, and a name read at dusk.', '{VAR_reward}. Rise, as we rose.'],
 'choir': ['{VAR_reward} for a safe return.', 'The Spire pays {VAR_reward}, in tune.', 'Reward {VAR_reward}. Rest after.', '{VAR_reward}, and a lens for a week.',
           'Fee: {VAR_reward}. Hold the note.', '{VAR_reward}, paid on the Spire stair.'],
 'quiet': ['{VAR_reward}. More if no one hears.', 'Payment {VAR_reward}, left where you left them.', '{VAR_reward}. A bonus for a clean bonus.',
           'Fee {VAR_reward}. You were never here.', '{VAR_reward}. Expect rain.', '{VAR_reward}, in a cup on the sill.'],
 'settlement': ['We can pay {VAR_reward}. We scraped for it.', '{VAR_reward} and supper.', 'Reward {VAR_reward}. Bring the hide.',
                '{VAR_reward}, and the whole town owes you one.', '{VAR_reward}. Ask for the reeve.', '{VAR_reward}, and you can keep the teeth.'],
}
RAD_CORE = {
 'RAD_01': ['{ACT_name} has been seen near {LOC_name}, walking like it still has somewhere to be.', 'Hollowed at {LOC_name}. One leads the rest. That one is {ACT_name}.',
            '{ACT_name} took two goats last week and the fence the week before. The goats were not the worst of it.', 'There is a pack at {LOC_name}, and {ACT_name} is keeping it together.'],
 'RAD_02': ['{ACT_name} has parked itself on the trade road at {LOC_name} and is issuing tickets.', 'Old tin at {LOC_name}. {ACT_name} runs it like it owns the place. It does not. We do.',
            '{ACT_name} shot a water barrel, then apologized in ship script. Shoot back.', 'Remnant activity at {LOC_name}. Primary pest: {ACT_name}. Bring proof of scrap.'],
 'RAD_03': ['Clan raiders at {LOC_name}, led by {ACT_name}, who signs his name on our doors in mud.', '{ACT_name} and his band took a cart of seed from {LOC_name}. We want the seed. They can keep the cart.',
            '{ACT_name} has shouted his family name outside {LOC_name} every night this week. We know it by heart now. We would like to forget it.',
            'Raiders camped at {LOC_name}. Their chief is {ACT_name}. Their manners are worse.'],
 'RAD_04': ['{ACT_name} has taken three Striders from the paddock near {LOC_name}. The fourth is nervous.', 'Hunt wanted: {ACT_name}, last seen at {LOC_name}, big as a cart and meaner than the cart\'s owner.',
            'Something has been eating the smokehouse stock. Tracks say {ACT_name}. Tracks lead to {LOC_name}.', '{ACT_name} is nesting at {LOC_name}. We would take a hide, a head or a good story.'],
 'RAD_05': ['Wreck section at {LOC_name}, sealed since the Fall. The Guild wants {ITM_name} out of it before someone else does.',
            'A hull piece came up at {LOC_name} after the rain. Inside: {ITM_name}, maybe. Outside: rats, definitely.',
            'Salvage run to {LOC_name}. Bring back {ITM_name}. Leave the ghosts.', 'Claim filed on {LOC_name}. Item of interest: {ITM_name}. Item of concern: everything else down there.'],
 'RAD_06': ['Shaft crew wanted for {LOC_name}. Target: {ITM_name}. Rope provided. Courage not provided.', 'The engine block gave up {ITM_name} on the survey. Someone has to go down to {LOC_name} and fetch it.',
            'Down the shaft at {LOC_name}, past the third warning light, there is {ITM_name}. Go and get it.', 'The lift goes down to {LOC_name}. Usually it comes back up. Bring {ITM_name} when it does.'],
 'RAD_07': ['Glass field at {LOC_name}, sheets still clear since the war. We want {ITM_name}, cut clean.', 'Cutters wanted for {LOC_name}. Bring back {ITM_name}. Bring water for two days, and a hat.',
            'The storm uncovered {ITM_name} at {LOC_name}. The glassblowers are already fighting over it. Settle it.', 'Fused glass at {LOC_name}, good grade. Bring back {ITM_name}. Do not look at your reflection too long.'],
 'RAD_08': ['Caravan overdue from {LOC_name}. Six Striders, two drivers, one very loud dog.', 'Our caravan stopped answering lamp signals near {LOC_name}. Find it. Find them.',
            'The post sledge never reached {LOC_name}. Neither did the letters, or the man who carries them.', 'Traders missing on the road past {LOC_name}. Last seen arguing about the route.'],
 'RAD_09': ['Someone has gone missing near {LOC_name}. They forgot their name last week and remembered it this morning.', 'Watch needed at {LOC_name}. A woman walked into the fog there and her lamp went out.',
            'Lost: one grandfather, near {LOC_name}. Answers to his name on good days.', 'The lamp shed at {LOC_name} counts one fewer at dusk than at dawn. Find out who.'],
 'RAD_10': ['Choirborn took one of ours from {LOC_name}. {ACT_name} sang them out of their bed.', 'A student of the Spire is held at {LOC_name}. {ACT_name} keeps the door. Bring them home.',
            '{ACT_name} led a hymn through {LOC_name} and left with a listener who never sang a note in her life.', 'The chorus is one voice short. The missing voice is at {LOC_name}, behind {ACT_name}.'],
 'RAD_11': ['A Kindled fell at {LOC_name} and the Shard-ghost is still glowing. Recover the Ember.', 'Anchor keeper\'s notice: unclaimed Shard-ghost at {LOC_name}. {ACT_name} was near when it went dark.',
            'Ember is sitting in a ghost at {LOC_name}. It belongs to somebody. Bring it back to their name.', 'A Shard-ghost has burned at {LOC_name} for six days. Somebody should go and see whose.'],
 'RAD_12': ['{ACT_name} has been dying on purpose at {LOC_name}, and coming back richer each time.', 'Warrant: {ACT_name}, Kindled, last seen at {LOC_name}, using the long sleep for profit.',
            '{ACT_name} keeps getting up. The Anchor at {LOC_name} keeps letting them. One of those can change.', '{ACT_name} robbed {LOC_name} three times this month and died twice doing it.'],
}
RAD_GIVE = {
 'knight': ['You read the notice. Good. Go.', 'I would send a Knight, but they are all busy being Knights.', 'Proof or it did not happen, sleeper.',
            'Chain of command says volunteers first. You are first.', 'Watch the flanks out there. Everyone forgets the flanks.', 'I will log the job under your name. Spell it slowly.',
            'Do not make it a story. Make it a report.', 'Sergeant says it is easy. Sergeant has never left the Gate.'],
 'salvager': ['Ah, the notice. Place, job, money. That is the whole pitch.', 'Everyone wants old tin and nobody wants to fetch it. Enter you.',
              'If you find two, you found one. Understand?', 'Fair share. You take the risk, I take the share. Fair.', 'Do not let the job sheet scare you. Let me scare you. It is more accurate.',
              'Easy money. That is why I am not doing it.', 'Mind the rats. The rats know the prices too.', 'Come back with it in one piece, or with all the pieces.'],
 'church': ['The Log teaches patience. The family teaches urgency.', 'Bless you for reading the board. Most people just pin things over it.',
            'Take a Tonic from the shelf. The Log will not mind. The sexton might.', 'This weighs on the whole Chapel.', 'We will read their name at dusk, whatever happens. I would rather read it as found.',
            'Be kind out there, even when it is hard. Especially then.', 'Go with the Log. And a lamp.', 'Sister wrote the notice. She cried on the ink. That smudge is grief.'],
 'choir': ['You saw the notice. Did you hear it too?', 'It went quiet out there. We want to know why.', 'Take this tuning fork. If it hums, leave.',
           'The song is louder there. Do not sing along, however catchy.', 'We would go ourselves, but we would stop to listen. You will not.', 'Rest before you go. Rest is part of it.',
           'Count your steps in fours. It keeps the song out.', 'Bring them back in their own voice. That is all we ask.'],
 'quiet': ['You read it. Now forget you read it.', 'Tonight. Not tomorrow.', 'You will be tempted to ask questions. Ask the weather.', 'The bonus is optional. The contract is not.',
           'You will know them by how little they fear dying.', 'Dusk is best. Fog is better.', 'One leaves. Make sure it is you.', 'No lamp on the way back.'],
 'settlement': ['You took the notice down? Good. People kept drawing on it.', 'Everybody knows. Nobody goes. You will go?', 'My cousin went last time. My cousin is still talking about it, which is the problem.',
                'There is stew when you are back. There is stew if you are not, but it is sadder.', 'The reeve can pay. The reeve will complain, but pay.', 'Mind the ground out there. It is soft, and so are the people near it.',
                'Do not be a hero. Be quick.', 'Bring back something we can show the children.'],
}
RAD_DONE_V = {
 'knight': ['Proof received. Logged. You are on the deck and on the books.', 'Clean work. I will tell the sergeant he owes me bread.', 'Report filed under your name. Spelled it wrong, sorry.',
            'The Gate holds another week. Do not let it go to your head.', 'Good. Next time, fewer dents.', 'Logged and paid. Dismissed.', 'The mess will hear about this. Mostly true.', 'That will quiet the board for a day.'],
 'salvager': ['Lovely. Fair share, minus a small fee for my enthusiasm.', 'That is real Meridian. I can smell the money.', 'Pay is in the barrel. Count it. I did. Twice.',
              'Petra is happy. Rare sight. Enjoy it.', 'Not a scratch. You have ruined my excuse to underpay you.', 'Good haul. I would hug you, but you are filthy.', 'Next job is worse. You will love it.', 'Signed, stamped and already resold.'],
 'church': ['The Log remembers good work. So do I. Logged.', 'We will read this at dusk, with your name in it.', 'Thank you. Have some soup. No, more than that.',
            'The family cried. The good kind, I think.', 'You came back whole. Thank the Fall.', 'I will mark it in the book. The happy column, for once.', 'Rise, as we rose. Logged.', 'Light keep you, sleeper.'],
 'choir': ['The note is back in tune. Thank you.', 'We heard it end from here. A clean rest.', 'You kept your own voice. Good.', 'The chorus is whole again, near enough.',
           'Rest now. You earned the quiet.', 'The Precentor will write a line about this. A short line. He is busy.', 'Your ears are ringing. That passes.', 'Held. Thank you.'],
 'quiet': ['Done. Good. Forget it.', 'Bonus noted. Or not. You will see.', 'The weather has cleared.', 'Payment is on the sill. The tea is still not for you.',
           'You were not there. Well done.', 'Fog lifts. Name struck.', 'The Speaker nodded. That is rare.', 'Go home. Light no lamp.'],
 'settlement': ['The whole street is talking about you. Mostly nice things.', 'Here is your pay, and a jar of pickles. Do not argue.', 'My cousin says you were lucky. My cousin is jealous.',
                'We will sleep tonight. First time in a week.', 'The children want to see the proof. Show them, then hide it.', 'The reeve paid without complaining. Be proud of that alone.', 'Stew is on. Sit.', 'Come back any time. Bring more luck.'],
}
RAD_REMARK = {
 'RAD_01': (['It used to be someone. Remember that, then do it anyway.', 'Take the badge if it has one.', 'Hollowed do not run. That makes it easier and worse.'],
            ['The board is one name shorter.', 'Somebody will light a lamp for it tonight.', 'One less shape in the fog.']),
 'RAD_02': (['Shoot the legs first. Old tin hates that.', 'It talks in ship script. Do not answer.', 'Bring back the scrap. The scrap pays the bounty.'],
            ['The caravans roll by morning.', 'That is a lot of scrap for one tin pest.', 'It said something polite on the way down, I hear.']),
 'RAD_03': (['Raiders break when their loudest one breaks.', 'They will shout a family name. Ignore it.', 'Bring back the seed if it is there.'],
            ['The road is quiet. The Clans will be back, just not today.', 'The seed is back in the barn.', 'Nobody is shouting outside tonight.']),
 'RAD_04': (['Downwind. Always downwind.', 'Bring the hide whole. Hunters are fussy.', 'If it has young, think about it.'],
            ['That is a lot of meat for the smokehouse.', 'The paddock is calm again.', 'The hunters will argue about that hide for a week.']),
 'RAD_05': (['The section is old. Step where the rivets are.', 'If a crate has a name on it, read the name.', 'Rival crews smile a lot. Count their hands.'],
            ['Clean pull. The wreck can sleep now.', 'That crate is worth more than the boat it came in.', 'The Guild ledger is happy. So am I.']),
 'RAD_06': (['Count the warning lights. Third one, you are close.', 'If the lift groans twice, climb.', 'Bring a spare lamp, and a spare for the spare.'],
            ['You came back up. Not everyone does.', 'The shaft crew tied a knot in the rope for you.', 'The engine block is a little lighter.']),
 'RAD_07': (['Cut with the grain. Glass has grain, ask anyone.', 'Water for two days. Drink on the hour.', 'Do not stare into the mirror flats.'],
            ['Not a bubble in it. Lovely.', 'The glassblowers will stop fighting. For a day.', 'That sheet will be a chapel window somewhere.']),
 'RAD_08': (['Look for the dog. The dog always survives.', 'Follow the wheel ruts until they stop.', 'Bring back names, whatever else you bring.'],
            ['The families are at the gate already.', 'The dog came back first, of course.', 'The caravan is late, but it is home.']),
 'RAD_09': (['Say their name when you find them. Loud.', 'Keep your lamp lit. Keep talking.', 'If they do not know you, that is normal now.'],
            ['They said their own name on the walk home.', 'The lamp line is whole again.', 'The family is arguing again. That is a good sign.']),
 'RAD_10': (['Do not sing, whatever they sing at you.', 'The vault doors open on the rest beat.', 'They may not want to come. Bring them if you can.'],
            ['They hummed all the way back. Not the song. Their own tune.', 'The Spire lit a lamp in the window.', 'One voice back in the chorus.']),
 'RAD_11': (['Ghosts stay warm a week. After that the Ember goes cold.', 'Read the name, if there is one.', 'Whatever killed them may still be close.'],
            ['The Ember is back where it belongs.', 'The keeper wrote the name in the Anchor book.', 'The ghost went out like a lamp at wake-call.']),
 'RAD_12': (['They come back from death. Make this the last time.', 'Their Anchor is close. So is yours.', 'The bonus matters. So does finishing.'],
            ['Struck from the list.', 'They will not be getting up from that one.', 'The Anchor is quiet now.']),
}
TWIST = {  # keyword in campaign twist -> line (notebook voice); index order follows radiant.json
 'RAD_01': [('badge', '{ACT_name} still wore a town badge on its coat. A woman at the board asked for it back, and asked me not to clean it first.'),
            ('timed', '{ACT_name} was walking a pack toward a farm with washing on the line. No time to be careful.'),
            ('decoy', 'There were two Heralds at {LOC_name}. One was only wearing the coat. The other was watching me work that out.'),
            ('neighbour', 'The man who posted it lived next door to {ACT_name}, before. He wants to know it was quick. He wants me to say so even if it was not.'),
            ('Shard-ghost', 'A dead Kindled\'s Shard-ghost glowed near {LOC_name}, Ember still in it, a name scratched on the stone beside it.'),
            ('Thorn', 'Thorn raiders got to {ACT_name} first. Now they are holding up its head at the board and asking for my pay.'),
            ('half', '{ACT_name} was only half gone. It asked me what day it was. Sister Calla might take it, if I can walk it there.')],
 'RAD_02': [('road', '{ACT_name} was not attacking anyone. It was paving the caravan road, very slowly, into a cliff.'),
            ('hijack', 'The Siege Walker\'s legs gave out and the hatch popped open. It has a seat. It has controls.'),
            ('cryo', 'The drones were guarding a cryo crate. Something inside knocked twice.'),
            ('ALLIED', 'The drones stopped and waited when they saw me, polite as clerks. Word from Unit 9 has spread. This could be a talk.'),
            ('child', 'A child in {LOC_name} has named {ACT_name} Button and feeds it bolts. The child would like it not to be shot.'),
            ('empty', 'The Mortar Frame was shelling an empty town it thinks is full. Every house it hits has been empty for forty years.')],
 'RAD_03': [('surrender', '{ACT_name} wants to surrender. Just not to a Hull Knight. Apparently I count as not a Hull Knight.'),
            ('starving', 'The raiders were starving. They took seed grain, not silver. A child in the camp was chewing raw beans.'),
            ('Dren', '{ACT_name} is from Dren\'s old clan. Dren has opinions about this. Loud ones.'),
            ('lying', 'The poster lied. The raider he wants dead is a man he owes forty lights.'),
            ('Morale', 'Their shieldman holds the whole band together. If he falls, the rest will run.'),
            ('Hostages', 'There are hostages in the camp at {LOC_name}. Three of them, one with a broken arm.')],
 'RAD_04': [('Alpha', 'The beast has a Shard grown right into its hide. It glows when it breathes. It will hit harder and pay better.'),
            ('young', 'It was guarding young. Four of them, each the size of a loaf. I could drive it off instead.'),
            ('hunter', 'Another hunter beat me there. She is under a tree at {LOC_name} with a leg that bends the wrong way.'),
            ('Hollowed', 'The beast never touched the herd. The bite marks are human. Hollowed, out past the ridge.'),
            ('alive', 'The Strider breeders want it alive. They have a pen, a rope and a great deal of confidence.'),
            ('Weather', 'The weather turned halfway through the hunt. Lost the trail, then found it again by smell.')],
 'RAD_05': [('Rival', 'A rival crew was already on the wreck at {LOC_name}, arguing over who saw it first. Trade, scare or fight.'),
            ('coffin', 'The crate was a coffin. A crew name was stenciled on the lid, still readable.'),
            ('unstable', 'The section groaned the moment I stepped in. I had minutes, not an afternoon.'),
            ('forged', 'The Guild claim was forged. The wreck belongs to the village that has tended it for a century.'),
            ('Petra', 'There was a working Meridian part under the bunks. Petra will pay extra. Petra will deny saying so.'),
            ('booby', 'Smugglers had wired the crate with a trap. Crude. It would still have taken my hand.')],
 'RAD_06': [('Lift', 'The lift failed behind me. The way up is now a ladder, a pipe and some hope.'),
            ('pod', 'A sleeper pod in the gallery still had power. Green light, faint. I wrote the number down.'),
            ('nest', 'Crawlers had nested right on top of {ITM_name}.'),
            ('Choirborn', 'Choirborn were already stripping the shaft, and they sang while they worked.'),
            ('Coolant', 'Coolant was leaking across the gallery floor. Frost Ward Brew, or frozen boots.'),
            ('load-bearing', '{ITM_name} was holding up the gallery. I could take it and run.')],
 'RAD_07': [('Glass War', 'A Glass War soldier lay under the glass. When I touched it, an Echo played his last order.'),
            ('Basilisk', 'Basilisk tracks crossed the field. If it shows up, I look at my feet and nowhere else.'),
            ('Sandstorm', 'A sandstorm swallowed the route. The moths knew the way, so I followed the moths.'),
            ('Remnant', 'Remnant drones were sorting the glass at {LOC_name} and claim it as theirs. They keep a ledger.'),
            ('perfect', 'The glassblower does not want a sackful. She wants one perfect sheet: no bubbles, no scratches.'),
            ('Hauler', 'A Hauler was buried up to its turret. Dig it out and it might drive home.')],
 'RAD_08': [('Driver', 'The driver is hurt and will not leave her Strider. The Strider will not leave her either.'),
            ('child', 'A child was hiding in the cargo, eating the dried fruit. Stowaway, and proud of it.'),
            ('Lamplighter', 'The caravan was carrying Shards for the Lamplighter\'s buyers. That changes who wants it back.'),
            ('manifest', 'Only the cargo survived. The manifest has nine names on it. The families should have it.'),
            ('ransom', 'Raiders have the caravan and want a ransom. They wrote the price on a hull plate.'),
            ('Blizzard', 'The storm closed in. Nobody moves until it lifts, me included.')],
 'RAD_09': [('purpose', 'Nobody took them. They walked out on purpose and left a note under the bread.'),
            ('already', 'They are already Hollowed. They still hum their old work song. Calla, or an end.'),
            ('lamp', 'A lamp is out on the line and the fog is moving in through the gap.'),
            ('hid', 'The family knew they were sick and hid it. They are ashamed. They are also right here.'),
            ('debt', 'They are fine. Hiding from a debt in a root cellar, eating someone else\'s jam.'),
            ('Ostra', 'A Shard-touched child at {LOC_name} can hear Ostra. She says Ostra sounds tired.')],
 'RAD_10': [('stay', 'The captive does not want rescuing. They say the song is the first quiet they have had in years.'),
            ('rebuilt', 'The captive is half rebuilt. They will need talking out of the vault, slowly.'),
            ('teacher', '{ACT_name} used to teach at the Spire. The one who posted this studied under them.'),
            ('empty', 'The vault was empty. Fresh scratches on the floor, all pointing up.'),
            ('Hal', 'Hal heard the song in the vault and stopped walking. He needs a minute. Maybe more.'),
            ('stealth', 'If they see me coming, the captive dies. Quiet, then.')],
 'RAD_11': [('alive', 'The Kindled was not dead. Pinned under a beam at {LOC_name}, very annoyed and quite alive.'),
            ('family', 'The Ember in the ghost belongs to a family in town. Return it or keep it. They will never know which.'),
            ('bait', 'The ghost was bait. The Quiet Hand was waiting in the rafters.'),
            ('abused', 'This Kindled used the long sleep as a business. The Quiet Hand would like the ghost left where it is.'),
            ('guarded', 'Whatever killed them is still standing over the ghost.'),
            ('Two ghosts', 'There were two ghosts. Someone tried this before me and did not come back.')],
 'RAD_12': [('Ward break', 'Bonus: the target must fall before their Ward breaks. One clean stroke.'),
            ('falling', 'Bonus: something heavy, from above. The Hand appreciates gravity.'),
            ('Anchor', '{ACT_name} ran for their Anchor. Every death sends them back there. I know the way too.'),
            ('protecting', 'The target is the only thing standing between {LOC_name} and the raiders.'),
            ('ritual', '{ACT_name} asked to be finished for good. The Hand has a ritual for that. It is short.'),
            ('forged', 'The warrant is forged. A rival paid for the ink.')],
}
TOKRE = re.compile(r'\{([A-Z]+)_[a-z_]+\}')
ALLOWED_RAD_TOK = {'{LOC_name}', '{ACT_name}', '{ITM_name}', '{VAR_reward}'}


def gen_radiant():
    p = CAMP + '/seeds/radiant.json'
    camp = []
    if os.path.exists(p):
        try:
            camp = json.load(open(p, encoding='utf-8'))
        except Exception:
            camp = []
    src = 'design/campaign/seeds/radiant.json' if camp else 'writing fallback list'
    if not camp:
        camp = [dict(id=i, name=n, shape=s, twists=[], target_pool=[], site_tags=[], reward_rule='100 x level Ember') for i, n, s in RAD_FALLBACK]
    tpl_rows, rows_exp = [], 0
    for c in camp:
        rows_exp += 8 + 6 + 6 + max(4, len(c.get('twists', [])))
    T = Table('radiant_text', rows_exp)
    for c in camp:
        rid = c['id']
        fac = RAD_FAC.get(rid, 'none (settlement boards)')
        vk = FAC_KEY.get(fac.split(';')[0].strip(), 'settlement')
        core = RAD_CORE.get(rid, ['Work at {LOC_name}. {ACT_name} is the problem.', 'Job at {LOC_name}. Bring back {ITM_name}.',
                                  '{LOC_name} needs a hand. Ask about {ACT_name}.', 'Help wanted at {LOC_name}.'])
        for i in range(1, 9):
            t = T.compose('%s_N%d' % (rid, i), [('rad_open_' + vk, BOARD_OPEN[vk], {}), ('rad_core_' + rid, core, {}),
                                               ('rad_close_' + vk, BOARD_CLOSE[vk], {})], 300)
            T.add('STR_RAD_%s_NOTICE_%02d' % (rid[4:], i), rid, 'notice', t, 300, notes='tokens: LOC_name place, ACT_name target, ITM_name item, VAR_reward Ember amount')
        give, done = RAD_REMARK.get(rid, (['Be careful.', 'Be quick.', 'Be back.'], ['Good work.', 'Done.', 'Paid.']))
        for i in range(1, 7):
            t = T.compose('%s_G%d' % (rid, i), [('rad_give_' + vk, RAD_GIVE[vk], {}), ('rad_gr_' + rid, give, {})], 160)
            T.add('STR_RAD_%s_GIVER_%02d' % (rid[4:], i), rid, 'giver_line', t, 160, notes='voice: %s; voiced (radiant giver budget)' % vk)
        for i in range(1, 7):
            t = T.compose('%s_C%d' % (rid, i), [('rad_done_' + vk, RAD_DONE_V[vk], {}), ('rad_dr_' + rid, done, {})], 160)
            T.add('STR_RAD_%s_DONE_%02d' % (rid[4:], i), rid, 'completion_line', t, 160, notes='voice: %s' % vk)
        tw = c.get('twists', [])
        bank = TWIST.get(rid, [])
        used = set()
        n_tw = 0
        for i, twist in enumerate(tw, 1):
            line = None
            for kw, l in bank:
                if kw.lower() in twist.lower() and l not in used:
                    line = l
                    break
            note = 'campaign twist: %s' % twist
            if not line:
                line = 'The notice left something out: ' + low1(scrub(twist)).rstrip('.') + '.'
                note += '; generic frame, writer to voice'
            used.add(line)
            if len(line) > 220:
                line = line[:217].rsplit(' ', 1)[0] + '.'
            T.add('STR_RAD_%s_TWIST_%02d' % (rid[4:], i), rid, 'twist_line', line, 220, notes=note)
            n_tw += 1
        tpl_rows.append(dict(rad_id=rid, name=c.get('name', ''), kind=c.get('shape', ''), giver_faction=fac,
                             slots='LOC_name: %s; ACT_name: %s; ITM_name: %s; VAR_reward: Ember' % (
                                 ' '.join(c.get('site_tags', [])) or 'site from tagged list',
                                 ' | '.join(name_of(x) if IDRE.match(x) else x for x in c.get('target_pool', [])) or 'target from tagged list',
                                 'salvage item from loot table' if c.get('shape') == 'salvage' else 'proof item'),
                             twist_pool='%d twists: %s' % (n_tw, ', '.join('STR_RAD_%s_TWIST_%02d' % (rid[4:], k) for k in range(1, n_tw + 1))),
                             reward_rule=(c.get('reward_rule', '') + '; faction jobs add rep, capped at 1,200 per faction per week (loops 06)').strip('; '),
                             notes='keyed to campaign %s; giver_faction is a writing design choice' % rid))
    return T, tpl_rows, src

# ---------------------------------------------------------------- tutorials
TUT_REWRITE = {
 'TUT_SURGE': ('Surge', '{BTN_surge} Release your Surge. It charges as you fight.', 'banned word'),
 'TUT_DEATH': ('Shard-ghost', 'You dropped all the Ember you carried. Reach your ghost to take it back. Die before you do and half of it burns.',
               'wrong rule: all carried Ember drops (FRM_DEATH, ITM_F_DEATH_EMBER), not half'),
 'TUT_ECHO': ('Echoes', 'Light an Echo Lantern at an Anchor to call an Echo for the next boss. It fights at your level.',
              'item is the Echo Lantern (data README 16); FRM_ECHO sets Echo level = player level'),
 'TUT_QUIET': ('The Quiet', 'The raid launches from here. Strikes, the featured Citadel and raid lockouts reset every Tuesday at 17:00 UTC.',
               'Strikes and Citadels run in the regions, not the Quiet (loops 06); reset time from loops 06'),
}
# Titles for tutorials that data added without a title string (orbital ring); request: add STR_<id>_T and set title_str.
TUT_TITLE_NEW = {'TUT_ORB_MAGBOOT': 'Mag Boots', 'TUT_ORB_KICKOFF': 'Kick Off', 'TUT_ORB_THRUST': 'Thrust',
                 'TUT_ORB_TETHER': 'Ostra\'s Tether', 'TUT_ORB_LOWG': 'Low Gravity', 'TUT_ORB_SEAM': 'Gravity Seams',
                 'TUT_ORB_COMETDROP': 'Comet Drop'}
TUT_NEW = [
 ('TUT_STRIDER', 'Your Strider', '{BTN_strider} Call your Strider. It comes at a run from wherever you left it.', 'First Strider earned; once per profile; completes on: Call once', 'HUD'),
 ('TUT_STRIDER_JUMP', 'Double Jump and Glide', 'Press {BTN_jump} twice on a Strider to double jump. Hold {BTN_glide} in the air to glide. Gliding drains Breath.', 'First 10 s riding a Strider near a ledge; once per profile; completes on: Glide 2 s', 'HUD'),
 ('TUT_HIJACK', 'Hijack', 'Break a skimmer, hauler or flyer\'s engine, then {BTN_interact} to take it. Wrecked engines make easy doors.', 'Enemy vehicle engine broken within 10 m; once per profile; completes on: Hijack once', 'HUD'),
 ('TUT_GHOST', 'Your Shard-ghost', '{BTN_interact} Take back your Ember. A ghost waits where you fell until you return or die again.', 'Player within 15 m of own Shard-ghost, first time; once per profile; completes on: Recover', 'HUD'),
 ('TUT_INFUSE', 'Infusions', '{BTN_confirm} Infuse a weapon at a smithing bench. Elements trade some attribute scaling for elemental damage.', 'First infusion material picked up or bench Infuse tab opened; once per profile', 'Crafting: Smithing'),
 ('TUT_ART', 'Weapon Arts', '{BTN_art} Use your Weapon Art. Each Art costs Breath, and some have a cooldown.', 'First weapon with a Weapon Art equipped; once per profile; completes on: Use Art once', 'HUD'),
 ('TUT_RITES', 'Rites Crafting', '{BTN_confirm} Combine effects into your own Rite. Stronger, longer or wider costs more Ember and cools down slower.', 'Rites table first used; once per profile', 'Crafting: Rites'),
 ('TUT_TINKER', 'Tinkering', '{BTN_confirm} Build gadgets and ammo at a Tinker bench. Engineering perks add new designs.', 'Tinker bench first used; once per profile', 'Crafting: Tinkering'),
 ('TUT_BREW', 'Brewing', '{BTN_confirm} Brew Tonics and buffs. Red moss and Shard dust are the base of most recipes.', 'Brewing table first used; once per profile', 'Crafting: Brewing'),
 ('TUT_SHARDBORN', 'Shardborn', 'Equip one Shardborn weapon and one Shardborn armor piece at a time. Pick the pair that fits your build in {BTN_inventory}.', 'First Shardborn item picked up; once per profile', 'Equipment and loadout'),
 ('TUT_HEART', 'Heart Shard', 'Take: +5% max Ward and a memory. Spare: the bearer dies a person and the land stops Hollowing. {BTN_confirm} Choose.', 'First Shard-bearer defeated, before the Take or Spare prompt; once per profile', 'HUD'),
 ('TUT_INVASION', 'Invasions', 'Invasions are off by default. Turn them on in {BTN_social} to invade other worlds and be invaded in yours.', 'Quiet Hand joined, or Co-op menu opened at level 20+; once per profile', 'Co-op and multiplayer lobby'),
 ('TUT_CONTRACT', 'Contract Bonuses', 'Quiet Hand contracts list a bonus condition. Meet it for 25% more pay. Miss it and the contract still counts.', 'First Quiet Hand contract accepted; once per profile', 'Journal'),
 ('TUT_SEALS', 'Seals', 'Weekly endgame activities pay Seals. Spend them with the Seal Warden. Seal income caps each week and resets Tuesday.', 'First Seal earned; once per profile', 'Endgame hub'),
 ('TUT_STRIKES', 'Strikes', 'Strikes are 3-player runs ending in a field-boss pair. Featured Strikes pay double Seals on your first 3 clears.', 'Endgame hub first opened at level 75; once per profile', 'Endgame hub'),
 ('TUT_RAID', 'The Raid', 'Six players, four bosses, no scaling. Checkpoints hold per boss until the weekly reset. Wipes cost no Ember.', 'Raid gate first approached; once per profile', 'Endgame hub'),
 ('TUT_POWER', 'Power Weapons', '{BTN_interact} Grab a power weapon from its pad. They ignore upgrades and perks, so anyone can win with one.', 'First Arena match, first power weapon spawn; once per profile', 'HUD'),
 ('TUT_ASSIST', 'Assist Option', 'Assist adds aim help and longer parry windows. It does not change enemy damage. Find it in Accessibility.', 'Accessibility options first opened; once per profile', 'Options'),
 ('TUT_PERK_RANK', 'Locked Perks', 'This perk needs a higher skill rank. Use the skill to raise it; the rank shows on the node. {BTN_confirm} Back.', 'First locked perk node selected; once per profile', 'Perk trees'),
 ('TUT_ATTR', 'Attribute Points', '{BTN_confirm} Spend your attribute point on Might, Finesse, Lore or Grit. You earn one every two levels.', 'First attribute point earned; once per profile', 'Level up'),
 ('TUT_ORIGIN', 'Origins', 'Your Origin sets starting stats and gear, nothing more. Any build is open from any Origin. {BTN_confirm} Choose.', 'Origin screen in character creation; once per profile', 'Character creation'),
 ('TUT_LOAD', 'Equip Load', 'Under 30% load you roll fast. Under 70%, normal. At 70% and up, slow. Over 100% you cannot roll. Check {BTN_inventory}.', 'Equip Load first passes 30%; once per profile', 'Inventory'),
 ('TUT_HEADSHOT', 'Headshots', 'Headshots deal double damage once a target\'s Ward is down. Against a Ward they deal x1.25. {BTN_aim} Aim high.', 'First firearm hit on a Warded head; once per profile', 'HUD'),
 ('TUT_RESTOCK', 'Vendor Stock', 'Vendors restock every 72 game hours, and their Ember never runs out. {BTN_confirm} Sell freely.', 'Second vendor visit; once per profile', 'Vendor'),
 ('TUT_CRAFT_CAP', 'Crafting Cap', 'Crafted bonuses stop at 15%, or 18% for Smithing and Tinkering with the top Engineering perk. {BTN_confirm} Got it.', 'First crafted bonus reaches 15%; once per profile', 'Crafting: Smithing'),
]
COVERED = {'Elemental Ward break (3x to opposite)': 'TUT_WARD_BREAK', 'Perk rank gates 25/50/75/100': 'TUT_PERKS',
           'Strider mount and glide button': 'TUT_VEHICLE'}


def gen_tutorials():
    S = {r['str_id']: r for r in rd(DATA + '/ui/strings.csv')}
    for r in rd(DATA + '/ui/strings_data.csv'):   # merged strings (writing and design text) live here
        S.setdefault(r['str_id'], r)
    _new_ids = {t[0] for t in TUT_NEW}   # tutorials this file adds: the data merge brings them back each rebuild, so keep emitting them as new
    P = [r for r in rd(DATA + '/ui/popups.csv') if r['kind'] == 'tutorial' and r['popup_id'] not in _new_ids]
    T = Table('tutorial_text', 2 * (len(P) + len(TUT_NEW)))
    cols = COLS + ['trigger']
    stats = collections.Counter()
    for p in P:
        tid = p['popup_id']
        t0 = S.get(p['title_str'], {}).get('text_en', '') or TUT_TITLE_NEW.get(tid, '')
        b0 = S.get(p['body_str'], {}).get('text_en', '')
        if tid in TUT_REWRITE:
            t1, b1, why = TUT_REWRITE[tid]
            st, note = 'draft', 'rewritten: ' + why + '; was: ' + b0
            stats['rewritten'] += 1
        else:
            probs = banned_hits(t0 + ' ' + b0)
            if probs or len(t0) > 24 or len(b0) > 140:
                raise SystemExit('existing tutorial %s breaks the guide (%s) and has no rewrite' % (tid, probs))
            t1, b1, st, note = t0, b0, 'existing', 'kept; passes style guide'
            stats['kept'] += 1
        T.add(p['title_str'] or 'STR_%s_T' % tid, tid, 'tutorial_title', t1, 24, status=st, notes=note, trigger=p['trigger'])
        T.add(p['body_str'] or 'STR_%s_B' % tid, tid, 'tutorial_body', b1, 140, status=st, notes=note, trigger=p['trigger'])
    existing = {p['popup_id'] for p in P}
    reqs = [dict(id=p['popup_id'], request='Add STR_%s_T "%s" to data/ui/strings and set popups.csv title_str=STR_%s_T' % (p['popup_id'], TUT_TITLE_NEW[p['popup_id']], p['popup_id']),
                 target_table='data/ui/popups.csv', notes='tutorial has no title string; text in design/writing/tutorial_text.csv')
            for p in P if p['popup_id'] in TUT_TITLE_NEW and not S.get(p['title_str'], {}).get('text_en')]
    for tid, title, body, trig, screen in TUT_NEW:
        if tid in existing:
            continue
        T.add('STR_%s_T' % tid, tid, 'tutorial_title', title, 24, notes='new', trigger=trig)
        T.add('STR_%s_B' % tid, tid, 'tutorial_body', body, 140, notes='new; numbers from data (see requests)', trigger=trig)
        stats['new'] += 1
        layer = 'HUD left card' if screen == 'HUD' else 'Menu overlay card'
        reqs.append(dict(id=tid, request='Add popup row: kind=tutorial; screen=%s; layer=%s; trigger=%s; title_str=STR_%s_T; body_str=STR_%s_B; '
                                         'duration_s=8.0 or until action; dismiss=Action done or 8 s; priority=3; queue_rule=One at a time; suppressed in combat and dialogue; '
                                         'sfx_hook=SFX_UI_TUTORIAL' % (screen, layer, trig, tid, tid),
                         target_table='data/ui/popups.csv', notes='text in design/writing/tutorial_text.csv; also add both STR_ rows to data/ui/strings.csv'))
    return T, cols, reqs, stats


# ---------------------------------------------------------------- Ostra hints
WP_OVERRIDE = {
 'ACT_BOSS_HOLLOWTWINS': ('whichever twin is Drained', '1.2', ''), 'ACT_BOSS_SMUGGLERQUEEN': ('her parry timing', '', ''),
 'ACT_BOSS_HAULER': ('the engine', '', '; break it and you can hijack the thing'), 'ACT_BOSS_NIGHTDRAKE': ('the wings', '', '; 600 damage to a wing grounds it'),
 'ACT_BOSS_ROTHYDRA': ('the necks', '', '; sever all three and phase 2 never happens'), 'ACT_BOSS_ASHCOLOSSUS': ('the knees', '1.5', ' to stance'),
 'ACT_BOSS_BRANNOCH': ('the Choir pipes on his back', '1.5', ''), 'ACT_BOSS_QUIETCORE': ('the three containment nodes', '3.0', ''),
 'ACT_BOSS_ARCHIVIST': ('the four data cores', '2.5', ''), 'ACT_BOSS_SENTINELS': ('the core of whichever one is not shielding', '1.5', ''),
 'ACT_BOSS_BASILISK': ('the eyes', '1.8', '; hitting them blinds it 6 s'), 'ACT_BOSS_GRAFTED': ('the reactor', '2.0', ' once both arms break'),
 'ACT_BOSS_SORREL': ('the heart-flower', '2.0', ' once a Root combo opens it'), 'ACT_BOSS_RIME': ('the ice veil', '1.5', ' after you break her Ward with Ember'),
 'ACT_BOSS_VAEL': ('the Crown Shard', '1.5', ' once his stance breaks'), 'ACT_BOSS_TOWERWITCH': ('the familiar crow', '2.0', '; kill it and she stops teleporting'),
 'ACT_BOSS_MIRRORKNIGHT': ('the mirror shield', '1.5', ' once 800 damage breaks it'), 'ACT_BOSS_LAMPLIGHTER': ('the lantern', '2.0', '; break it and phase 2 ends early'),
 'ACT_BOSS_FURNACEMAW': ('the belly furnace', '2.0', ' while it is open'), 'ACT_BOSS_ROTHYDRA_': None,
}
STAGE_OF = {r: REG[r]['stage'] for r in REG}
HINT = {  # stage -> level -> frames. Slots: wp, m, cond, ward, ctr, tip, boss
 1: {1: ['Noted: it guards <wp> more than anything else. Things guard what hurts.', 'Observation. It turns <wp> away every time you close in.',
         'Two attempts logged. <Wp> is the only part it protects. Correction: was protecting.', 'Status: losing. <Wp> looks breakable. That was a hint.'],
     2: ['Correction: stop hitting the parts that do not matter. <Wp> takes x<m><cond>.', 'Data: <wp>, x<m><cond>. I would aim there. I do not have hands.',
         'Four failures. I am not counting. <Wp>: x<m><cond>.', 'Noted for the third time: <wp>, x<m><cond>. I can repeat it slower.'],
     3: ['<Ward>Status needs double buildup on it. Spend that effort on <wp>.', '<Ward>Do not bother with status; its threshold is doubled. <Tip>',
         'Six. Fine. <Ward>Status builds at half speed here. <Tip>', '<Ward>Its status threshold is twice normal. Hit, do not poison. <Tip>']},
 2: {1: ['I think it is guarding <wp>. Do you see it too?', 'Have you noticed how it hides <wp> from you? I have.',
         'I think we keep missing... never mind. Look at <wp>.', 'Can I tell you something? It flinches near <wp>. I think.'],
     2: ['<Wp>. x<m><cond>. I think that is right. I am fairly sure.', 'Can I suggest something? <Wp>, x<m><cond>.',
         'I had this somewhere. Here: <wp>, x<m><cond>.', 'Do you trust me on this? <Wp> takes x<m><cond>.'],
     3: ['<Ward>Status needs double buildup on it. I think that is why nothing sticks.', '<Ward>Its status threshold is doubled. Did you know? I did not, until now. <Tip>',
         'I think I know the rest. <Ward>Status at half speed. <Tip>', 'Six times. Are you all right? <Ward><Tip>']},
 3: {1: ['<Wp>. It hides it. I hid things too.', 'Look at <wp>. Please.', 'It protects <wp>. Everyone protects something.', '<Wp>. That is all I have. It is enough.'],
     2: ['x<m> on <wp><cond>. I have the numbers. I always have the numbers.', '<Wp>, x<m><cond>. I kept that number, at least.',
         '<Wp>. x<m><cond>. Use it. I did not use mine well.', 'Numbers: <wp>, x<m><cond>. Those I can give you.'],
     3: ['<Ward>Status costs double. <Tip>', 'Six. I counted. <Ward><Tip>', '<Ward>Its status threshold is doubled. I am sorry it took six.', '<Tip> <Ward>That is everything.']},
 4: {1: ['It keeps <wp> turned away from you. You will see it if you wait.', 'Watch <wp>. You will know what to do with it.',
         'There is a reason it shields <wp>. Take your time.', 'Breathe. Then look at <wp>.'],
     2: ['<Wp> takes x<m> damage<cond>. How you reach it is yours to decide.', 'If it helps: <wp>, x<m><cond>. You choose when.',
         'I will tell you plainly. <Wp> takes x<m><cond>.', '<Wp>, x<m><cond>. I will be quiet now and let you work.'],
     3: ['<Ward>Its status threshold is doubled, so trust your weapon. <Tip>', 'You have done this before. <Ward><Tip>',
         '<Ward>Status will be slow. <Tip> I will hold the door.', 'One more thing, then I am done. <Ward><Tip>']},
}
HINT_COLD = {1: ['<Wp>. Look.', 'Watch <wp>.', '<Wp>. Obvious.', 'It guards <wp>.'],
             2: ['<Wp>. x<m>.', 'x<m>. <Wp>.', '<Wp>, x<m>. Again.', 'Hit <wp>. x<m>.'],
             3: ['<WardC>Status: double. <Wp>.', '<WardC>Skip status. Hit <wp>.', 'Status doubled. <WardC>Go for <wp>.', '<WardC>Hit <wp> harder.']}
RG_TOPIC = {
 'tower': {1: 'Correction: the map is blank because you have not climbed <tower>. Climb it.', 2: 'I think the map would help. <Tower> first?',
           3: '<Tower>. Climb it. I need to see.', 4: 'If you climb <tower>, I can show you the whole of <reg>.'},
 'anchor': {1: 'Anchors in <reg> sit every few hundred meters. Light each one. Dying is cheaper that way.', 2: 'Have you lit the Anchor near <site>? I think you missed it.',
            3: 'Light the Anchors in <reg>. I would rather not lose you between them.', 4: 'There is an Anchor near <site>. It would make the road back shorter.'},
 'town': {1: '<Town>: people, beds, prices. Noted.', 2: 'I think <town> could use you. They will not ask.', 3: '<Town>. They are still here. Go and see them.',
          4: 'The people of <town> have waited a long time. Visit when you can.'},
 'site': {1: 'Unknown structure at <site>. Ship parts in the walls. Investigate.', 2: 'There is something at <site>. I think it is mine.',
          3: '<Site>. There is a log there. I do not want to read it. Read it.', 4: '<Site> holds a story. You decide if you want it.'},
 'site2': {1: 'Noted: <site> has a locked door and a smell of old coolant. Both are promising.', 2: 'Can we look at <site>? I keep thinking about it.',
           3: '<Site>. Someone died there. Several someones.', 4: 'There is a quiet place at <site>. Go there when you need to.'},
 'field1': {1: '<Fb> is out there. <Fbnote>. Come back stronger, or come back faster.', 2: 'I think <fb> has seen us. <Fbnote>.',
            3: '<Fb>. <Fbnote>. Be careful.', 4: '<Fb> roams here. <Fbnote>. Fight it when you are ready, not before.'},
 'field2': {1: 'Second threat logged: <fb>. <Fbnote>.', 2: 'There is another one. <Fb>. <Fbnote>. Why are there always two?',
            3: '<Fb>. <Fbnote>. Two big things in one region. I counted.', 4: '<Fb> is the other one. <Fbnote>.'},
 'element': {1: '<Elem> Wards everywhere here. <Ctr> breaks them three times faster. Pack <ctr>.', 2: 'Most Wards here are <elem>, I think. <Ctr> would help.',
             3: '<Elem> Wards. <Ctr> breaks them at triple rate. I kept that number.', 4: 'Enemies here mostly carry <elem> Wards. <Ctr> answers them best.'},
 'enemy': {1: 'Hostiles in <reg>: <enemy>. Leaders first. The rest lose their nerve.', 2: 'I think <enemy> all want <reg>. Have you seen their leaders?',
           3: '<Enemy>, all over <reg>. Leaders first.', 4: '<Enemy> hold this region. Their leaders keep them together.'},
 'hazard': {1: '<Hazard> incoming. Ward drains in storms; get under a roof.', 2: 'Is that <hazard>? I think we should find cover.',
            3: '<Hazard>. Cover.', 4: 'There is <hazard> coming. A roof would be wise.'},
 'lore': {1: '<Lore>', 2: '<Lore>', 3: '<Lore>', 4: '<Lore>'},
}
RG_LORE = {  # Act 1 Ostra is confidently wrong about lore (05-story-pass B); never about mechanics
 'REG_01': ('The core failed. Reactor fatigue. I logged it. The spine broke on impact, nothing more.', 'intentionally wrong (Act 1 unreliable narrator); contradiction source for CNT_OSTRA_CONTRADICTIONS'),
 'REG_02': ('The Glass War wrecks are old. The Meridian came down clean. Correction: clean enough.', 'intentionally wrong (Act 1 unreliable narrator)'),
 'REG_03': ('I think the hydroponics bay fell here. I think I remember choosing where. That is wrong. I did not choose.', 'Act 2: uncertain, not yet the truth'),
 'REG_04': ('The Remnant follow maintenance orders. Mine, I think. I never gave them. I think I never gave them.', 'Act 2'),
 'REG_05': ('Thirty-seven thousand pods. I know the number. I do not want to know why I know.', 'stage 3 voice'),
 'REG_06': ('They forget here. I forgot on purpose. Do not tell anyone. There is no one to tell.', 'stage 3 voice'),
}
HUB_U_Q = {
 'REG_HUB': [('Vendors restock every 72 game hours. Their Ember never runs out. Mine does. Ours does.', 'vendor restock (ECOF_RESTOCK)'),
             ('Correction: that is not a throne. It is the captain\'s chair. Do not sit in it. Unless you want to.', ''),
             ('The Knights\' Gate, the Log Chapel, the Spire, the Undermarket. Five factions. Two of them dislike each other permanently.', 'Choir and Church rivalry'),
             ('Storage is on the Bridge Deck. Your pack is not infinite. Noted twice.', ''),
             ('The Seal Warden takes Seals only. Raid armor 15, weapons 20. Nobody can buy Seals. Good.', 'ECOF_SEALS'),
             ('Smithing bench: Undermarket. Upgrades to +20. Every level costs more than the last.', ''),
             ('The Cradle was a shuttle bay. It still has a lift. Noted for later.', ''),
             ('Mirrors in the Hold change your look for free. Vanity is efficient here.', ''),
             ('This bridge is mine. Was mine. The deck plates are in the same order.', ''),
             ('Arena wall, east tier. Four against four. Power weapons on pads every 120 s.', 'loops 06')],
 'REG_U': [('Shafts down here open from Cinderreach, Glasswaste and Hollowdeep. Three doors, one engine.', ''),
           ('Coolant leaks freeze Breath regen. Frost Ward Brew helps. Walking around them helps more.', ''),
           ('The Vault Keeper guards a vault of names. Keyhole chest, x2.0. I would know that door anywhere.', ''),
           ('Sleeper pods with green lights. Four hundred, maybe. Do not open them. Count them.', 'Undervault 400 sleepers (04 endings)'),
           ('Crawlers nest near heat. The engine is all heat.', ''),
           ('Lifts fail. Ladders do not. Climb.', ''),
           ('These are my engines. I know the hum. I do not know why it stopped.', ''),
           ('Remnant here still run maintenance. They will fix you if you stand still. Do not stand still.', ''),
           ('Iron Wards down here. Storm breaks Iron three times faster.', ''),
           ('The core housing is ahead. I will be quiet there. I do not know why.', 'foreshadows MQ_A2_06')],
 'REG_Q': [('Gravity is lower here. Your jumps go farther and your falls last longer.', ''),
           ('The Threshing Ring is the outer ring. The Choirborn sleep there. They do not sleep.', ''),
           ('The Granary holds the land it took. If you spared a Heart, that land can still go home.', '04 Spare rule'),
           ('Hush hears everything here. Speak anyway. It never lies, so listen too.', ''),
           ('Hollow Wards on most things. Bloom breaks Hollow three times faster.', ''),
           ('No Anchors past the lander until you light one. Choose your fights.', ''),
           ('The fields hanging in glass are real. The ferns are still lit.', ''),
           ('Choirborn teleport after a heavy hit. Watch for the shimmer, then turn.', ''),
           ('The Hush Core is at the center. Whatever you choose there, I will hold the door.', ''),
           ('I wanted to come here once. Before. I think that is why we are here now.', '')],
}
GENERAL = [  # (warm stage-1 line, cold line, source)
 ('Noted: your Ward refills 4.5 s after the last hit. Stop getting hit for 4.5 s.', 'Ward: 4.5 s. Stop getting hit.', 'TUT_WARD'),
 ('Breath at zero means Exhausted: no rolls, no sprint, half regen for 1.5 s. Do not do that.', 'Breath zero: no rolls. Avoid.', 'STS_EXHAUST'),
 ('Correction: blocking still costs Breath. The shield is not a wall. Walls do not get tired.', 'Blocking costs Breath.', 'FRM_BLOCK'),
 ('Kinetic damage does half to a Ward. Weave does 1.5 times. I prefer Weave. I am biased.', 'Kinetic: half on Ward. Use Weave.', 'FRM_WARDHIT'),
 ('Headshots do double only when the Ward is down. On a Ward, x1.25. Patience, then the head.', 'Ward down first. Then the head.', 'FRM_HEADSHOT'),
 ('Each status proc raises that status threshold 25% for 30 s. Repeat procs get expensive.', 'Repeat procs cost 25% more.', 'FRM_STATUS'),
 ('Slow stacks. Three within 10 s and the target freezes for 2.5 s, taking x1.3. Arithmetic is lovely.', 'Three Slows: Frozen. x1.3.', 'STS_SLOW'),
 ('Drain takes 3% of Ward and Breath per second and feeds the attacker. Do not stand in it.', 'Drain feeds them. Move.', 'STS_DRAIN'),
 ('Burn cuts healing received by 20%. Drink your Tonic after it ends, not during.', 'Burn: -20% healing. Wait.', 'STS_BURN'),
 ('Shock stops Ward recharge and chains 30% damage to two nearby targets. Crowds hate Shock.', 'Shock chains. Use it on crowds.', 'STS_SHOCK'),
 ('Root stops movement and dodges, not swings. A rooted enemy can still hit you. Noted from experience.', 'Rooted enemies still swing.', 'STS_ROOT'),
 ('Shatter: armor and Defense -25%, poise damage +20%. Then use something heavy.', 'Shatter, then heavy.', 'STS_SHATTER'),
 ('Your carried Ember drops as a Shard-ghost when you die. Reach it. If you die first, half of it burns.', 'Ghost. Reach it. Or lose half.', 'FRM_DEATH'),
 ('Elites and bosses stay dead after an Anchor rest. Normal enemies do not. Neither do you, technically.', 'Elites stay dead. Others return.', 'lore 3'),
 ('Unmet weapon requirements cut damage 40% and raise Breath costs 25%. Read the requirements. I did.', 'Requirements. Read them.', 'ITM_F_REQ'),
 ('A +20 weapon deals 2.5 times its base. Upgrades matter more than names.', '+20: 2.5x base.', 'ITM_F_UPG_MULT'),
 ('Tonic heal: 40% of max Health, plus 2.5% per Tonic Distillation. Distill them.', 'Tonic: 40% plus potency.', 'ITM_F_TONIC'),
 ('Enemies ten or more levels below you give a quarter of the Ember. Move on.', 'Low enemies, low Ember. Move on.', 'FRM_EMBER_DROP'),
 ('Staggered enemies take a critical. Heavy attacks break stance. I enjoy this part.', 'Stance broken. Critical.', 'FRM_STANCE'),
 ('Enemy stance starts recovering after a delay, then refills 10% per second. Keep the pressure on.', 'Keep pressure. Stance refills.', 'FRM_STANCE'),
 ('Your poise breaks if you take more poise damage than you have in 8 s. Heavy attacks give hyperarmor.', 'Poise: 8 s window.', 'FRM_POISE'),
 ('Firearms lose damage past their optimal range. Walk closer. Or do not, and miss politely.', 'Range falloff. Close in.', 'FRM_FALLOFF'),
 ('One attribute point every two levels. Might, Finesse, Lore or Grit. All four are acceptable choices. Mostly.', 'Attribute point. Spend it.', 'plan 3.3'),
 ('Gains in an attribute slow past its first soft cap and again past the second. Spread out.', 'Soft caps. Spread out.', 'attributes.csv'),
 ('Crafted bonuses stop at 15%. Stacking more is decoration.', 'Craft cap: 15%.', 'ITM_F_CRAFT_CAP'),
 ('Rites cost more Ember and cool down slower the bigger, longer and wider you make them.', 'Bigger Rite, longer cooldown.', 'ITM_F_RITE_COST'),
 ('Vendors buy at a quarter of their price. Haggle with Speech, or accept it like me.', 'Sell price: a quarter.', 'ITM_F_PRICE_SELL'),
 ('Under 30% Equip Load you roll fast. Over 100% you do not roll at all. I recommend rolling.', 'Load over 100%: no roll.', 'ITM_F_EQUIP_LOAD'),
 ('Only one Shardborn weapon and one Shardborn armor piece at a time. They are jealous objects.', 'One Shardborn each. Choose.', 'STR_EQ_SHARDBORN_LOCK_D'),
 ('Echoes fight at your level with 70% health. They are recordings. Be kind to them anyway.', 'Echo: your level, 70% health.', 'FRM_ECHO'),
 ('Co-op adds 50% enemy health for a second player. More hands, more work. Same reward each.', 'Co-op: more health on them.', 'coop_scaling'),
 ('Speech raises reputation gains. Rival-faction work earns half. Politics is a tax.', 'Rival work: half reputation.', 'FRM_REP'),
 ('Bounties: 40 per minor crime, 1,000 per murder. I am not judging. I am counting.', 'Murder bounty: 1,000.', 'ECOF_BRIBE'),
 ('Resonances are strong and slow. Long cooldowns. Use them when it matters, not when it is fun.', 'Resonance: long cooldown.', 'resonances.csv'),
 ('Weapon Arts cost Breath. An Art with no Breath left is a dance with no music. Correction: a stumble.', 'Arts cost Breath.', 'weapon_arts.csv'),
 ('Parry with good timing, then critical. Bucklers give a wider window. I measured.', 'Parry, then critical.', 'TIP_004'),
 ('Sneak attacks deal triple. Crouch, approach, apply. Simple procedure.', 'Sneak: triple.', 'TUT_SNEAK'),
 ('Ward breaks faster to its opposite element: three times. Ember and Frost, Storm and Iron, Hollow and Bloom.', 'Opposites: x3 on Ward.', 'element_matrix'),
 ('Weave damage to Health is 0.8. To a Ward it is 1.5. Shields first, bodies after.', 'Weave: Wards first.', 'FRM_WARDHIT'),
 ('Your level is the sum of your skills. Use a skill, raise it, raise you. Efficient design. Not mine.', 'Skills make your level.', 'TUT_SKILLS'),
]


def counter_of(elem):
    for r in rd(DATA + '/actors/element_matrix.csv'):
        a = r['Attacker element']
        if a in ('Ember', 'Storm', 'Hollow', 'Frost', 'Bloom', 'Iron') and r.get(elem) == '3.0':
            return a
    return ''


def parse_wp(b):
    if b['ACT_ID'] in WP_OVERRIDE and WP_OVERRIDE[b['ACT_ID']]:
        return WP_OVERRIDE[b['ACT_ID']]
    t = b['Weak points / parts']
    m = re.search(r'x(\d\.\d)', t)
    mult = m.group(1) if m else ''
    name = re.split(r' x\d| \(|;|,', t)[0].strip()
    cond = ''
    c = re.search(r'\(([^)]*)\)', t)
    if c and 'x' not in c.group(1):
        cond = ' (' + c.group(1) + ')'
    after = t.split('x' + mult, 1)[1].strip() if mult and ('x' + mult) in t else ''
    if after and not after.startswith(('(', ';', ',')):
        cond = ' ' + after
    nm = name[:1].lower() + name[1:]
    if not nm.startswith(('the ', 'its ', 'her ', 'his ')):
        nm = 'the ' + nm
    return nm, mult, cond


def gen_ostra():
    bosses = rd(DATA + '/actors/bosses.csv')
    exp = 2 * (3 * len(bosses) + 10 * len(REG) + len(GENERAL))
    T = Table('ostra_hints', exp)
    cols = COLS + ['variant', 'stage', 'trigger']
    cold_note = 'COLD variant: used when CNT_OSTRA_CONTRADICTIONS >= 3 and the confrontation flag is set (05-story-pass B); UI shifts hint text color'

    def pair(sid, owner, kind, warm_parts, cold_parts, stage, trigger, note):
        w = T.compose(sid, warm_parts, 120, soft=True)
        if not w:
            bid_, bank_, sl_ = warm_parts[0]
            w = T.compose(sid + 'b', [(bid_, bank_, dict(sl_, tip=''))], 120, soft=True) or \
                T.compose(sid + 'c', [(bid_, bank_, dict(sl_, tip='', ward=sl_.get('wardc', '')))], 120)
        T.add(sid, owner, kind, w, 120, notes=note, variant='warm', stage=stage, trigger=trigger)
        c = T.compose(sid + '_C', cold_parts, 120, soft=True) or \
            T.compose(sid + '_C2', [('hc_named', ['<Boss>: <wp>.', '<Boss>. <Wp>. Now.', '<Boss>. <WardC>Again.'], dict(cold_parts[0][2]))], 120)
        T.add(sid + '_COLD', owner, kind, c, 120, notes=cold_note, variant='cold', stage=stage, trigger=trigger + '; cold')
    for b in bosses:
        bid = b['ACT_ID']
        reg = b['Region'] if b['Region'] in REG else 'REG_Q'
        stg = STAGE_OF.get(reg, 1)
        wp, m, cond = parse_wp(b)
        welem = b['Ward element'] if b['Ward element'] not in ('', 'None') else ''
        ctr = counter_of(welem) if welem else ''
        ward = ('%s Ward: %s breaks it three times faster. ' % (welem, ctr)) if welem else 'No Ward. '
        wardc = ('%s on the Ward. ' % ctr) if welem else 'No Ward. '
        note = b['Notes'].rstrip('.')
        tip = cap1(note) + '.' if note and len(note) < 60 else 'Hit ' + wp + '.'
        if not m:
            m = '1.0'
            mtxt = ''
        sl = dict(wp=wp, m=m, cond=cond, ward=ward, wardc=wardc, ctr=ctr, tip=tip, boss=b['Boss'].split(',')[0])
        if not m or m == '1.0':
            sl['m'] = 'more'
        for lvl, d in ((1, 2), (2, 4), (3, 6)):
            sid = 'STR_OSTRA_HINT_%s_%d' % (bid.replace('ACT_BOSS_', ''), lvl)
            warm = HINT[stg][lvl]
            if lvl == 2 and sl['m'] == 'more':
                warm = [w.replace('x<m>', 'extra damage').replace('takes extra damage damage', 'takes extra damage') for w in warm]
            cold = HINT_COLD[lvl] if not (lvl == 2 and sl['m'] == 'more') else ['<Wp>. Look again.', 'Watch <wp>.', '<Wp>. Again.']
            pair(sid, bid, 'boss_hint', [('h%d_%d' % (stg, lvl), warm, sl)], [('hc_%d' % lvl, cold, sl)], stg,
                 'after death %d to %s' % (d, b['Boss']), 'from bosses.csv weak point, Ward element and status rule (x2.0 thresholds)')
    # regions
    places = collections.defaultdict(list)
    for r in rd(OUT + '/place_names.csv'):
        places[r['region']].append(r['text_en'])
    for reg, R in REG.items():
        stg = R['stage']
        sid0 = 'STR_OSTRA_HINT_%s' % reg.replace('REG_', 'R')
        if reg in HUB_U_Q:
            for i, (line, n) in enumerate(HUB_U_Q[reg], 1):
                line = line if len(line) <= 120 else line[:117].rsplit(' ', 1)[0] + '.'
                T.add('%s_%02d' % (sid0, i), reg, 'region_hint', line, 120, notes=n or 'handwritten bank', variant='warm', stage=stg, trigger='exploring %s' % R['name'])
                cold = re.split(r'(?<=[.])\s+', line)[0]
                if cold == line or len(cold) < 12:
                    cold = ' '.join(line.split()[:6]).rstrip(',.') + '.'
                if cold in T.texts:
                    cold = cold.rstrip('.') + '. Noted.'
                T.add('%s_%02d_COLD' % (sid0, i), reg, 'region_hint', cold, 120, notes=cold_note, variant='cold', stage=stg, trigger='exploring %s; cold' % R['name'])
            continue
        rg = rng(reg)
        sites = places.get(reg) or [R['town']]
        s1, s2, s3 = (rg.sample(sites, 3) if len(sites) >= 3 else (sites * 3)[:3])
        fbs = [b for b in bosses if b['Region'] == reg and b['Class'] == 'Field']
        ens = [e for e in rd(DATA + '/actors/enemies.csv') if reg in e['Regions'].split() and e['Tier'] == 'Leader']
        fl = sorted({{'HOLLOWED': 'Hollowed', 'REMNANT': 'Remnant', 'THORN': 'Thorn Clans', 'CHOIRBORN': 'Choirborn'}.get(e['ACT_ID'].split('_')[1], '') for e in ens} - {''})
        enemy = (', '.join(fl[:-1]) + ' and ' + fl[-1]) if len(fl) > 1 else (fl[0] if fl else 'Hollowed')
        elem = R['elem']
        sl = dict(tower='the %s Relay Tower' % R['name'], reg=R['name'], town=R['town'], site=s1, elem=elem, ctr=counter_of(elem),
                  enemy=enemy, hazard=R['hazard'] or 'a storm', lore=RG_LORE.get(reg, ('', ''))[0])
        topics = [('tower', {}), ('anchor', dict(site=s3)), ('town', {}), ('site', dict(site=s1)), ('site2', dict(site=s2)),
                  ('element', {}), ('enemy', {}), ('hazard', {}), ('lore', {})]
        for k, fb in enumerate(fbs[:2]):
            topics.insert(5 + k, ('field%d' % (k + 1), dict(fb=fb['Boss'], fbnote=fb['Notes'].rstrip('.'))))
        topics = topics[:10]
        for i, (tp, extra) in enumerate(topics, 1):
            s = dict(sl, **extra)
            frame = RG_TOPIC[tp][stg]
            note = RG_LORE[reg][1] if tp == 'lore' else 'region topic: ' + tp
            w = fill(frame, s, rg)
            if len(w) > 120:
                w = w[:117].rsplit(' ', 1)[0] + '.'
            T.add('%s_%02d' % (sid0, i), reg, 'region_hint', w, 120, notes=note, variant='warm', stage=stg, trigger='exploring %s' % R['name'])
            cold = {'tower': 'Climb <tower>.', 'anchor': 'Light the Anchors.', 'town': '<Town>. Go.', 'site': '<Site>. Search it.',
                    'site2': '<Site>. Locked. Open it.', 'field1': '<Fb>. Careful.', 'field2': '<Fb>. Also careful.',
                    'element': '<Ctr> for <elem> Wards.', 'enemy': '<Enemy>. Leaders first.', 'hazard': '<Hazard>. Cover.',
                    'lore': 'The core failed. That is all.' if stg == 1 else 'Not now.'}[tp]
            c = fill(cold, s, rg)
            if c in T.texts:
                c = c.rstrip('.') + ' (%s).' % R['name']
            T.add('%s_%02d_COLD' % (sid0, i), reg, 'region_hint', c, 120, notes=cold_note + ('; ' + note if tp == 'lore' else ''), variant='cold', stage=stg, trigger='exploring %s; cold' % R['name'])
    for i, (w, c, src) in enumerate(GENERAL, 1):
        T.add('STR_OSTRA_HINT_SYS_%02d' % i, 'SYSTEM', 'system_hint', w, 120, notes='source: ' + src, variant='warm', stage=1, trigger='contextual, mechanic in play')
        T.add('STR_OSTRA_HINT_SYS_%02d_COLD' % i, 'SYSTEM', 'system_hint', c, 120, notes=cold_note, variant='cold', stage=1, trigger='contextual; cold')
    return T, cols

# ---------------------------------------------------------------- loading tips
FACT_TIPS = [  # hand-picked facts from data/ (source in notes); phrased once, checked against existing tips
 ('Headshots only double damage once the Ward is down. Against a Ward they deal x1.25.', 'FRM_HEADSHOT'),
 ('Blocking refills Breath at 20 per second, half the normal rate. Lower the shield to recover.', 'FRM_BREATH'),
 ('Every time a status takes hold, its threshold rises 25% for 30 seconds.', 'FRM_STATUS'),
 ('Kindling level 10 costs 1,820 Ember. Level 35 costs 8,532. Level 70 costs 29,060.', 'ECOF_LEVEL'),
 ('Enemies 10 or more levels below you drop a quarter of their usual Ember.', 'FRM_EMBER_DROP'),
 ('Die before reaching your Shard-ghost and the new ghost holds your carried Ember plus half the old one.', 'ECOF_DEATH'),
 ('A Tonic heals 40% of max Health, plus 2.5% for each step of Tonic Distillation, up to 8.', 'ITM_F_TONIC'),
 ('A +20 weapon hits 2.5 times as hard as the same weapon at +0.', 'ITM_F_UPG_MULT'),
 ('Wielding a weapon without its attribute requirements cuts damage 40% and raises Breath costs 25%.', 'ITM_F_REQ'),
 ('Crafted bonuses cap at 15%. The top Engineering perk lifts Smithing and Tinkering to 18%.', 'ECOF_RITE'),
 ('Vendors restock every 72 game hours and never run out of Ember to pay you.', 'ECOF_RESTOCK'),
 ('Vendors buy at a quarter of their sell price. Speech nudges it up.', 'ITM_F_PRICE_SELL'),
 ('Raid armor costs 15 Seals and raid weapons cost 20. Seals cannot be bought.', 'ECOF_SEALS'),
 ('Speech raises every reputation gain. Work for a rival faction earns half.', 'FRM_REP'),
 ('A minor crime adds a 40 Ember bounty. Murder adds 1,000.', 'ECOF_BRIBE'),
 ('You are staggered when poise damage taken in 8 seconds exceeds your Poise. Heavy attacks add hyperarmor.', 'FRM_POISE'),
 ('Critical hits use the weapon\'s crit multiplier, 3.0 unless the weapon says otherwise.', 'FRM_CRIT'),
 ('Relic armor rolls 3 bonus stats from Health, Ward, Breath, Ability Recharge and Equip Load, never the same one twice.', 'ITM_F_ARMOR_ROLL'),
 ('One attribute point arrives every two levels.', 'plan 3.3'),
 ('Anchors bring back normal enemies when you rest. Elites and bosses stay dead.', 'lore bible 3'),
 ('Enemy stance starts refilling after a delay of its Stance value divided by 13 seconds, then refills 10% per second.', 'FRM_STANCE'),
 ('Firearms keep full damage up to their optimal range, then lose it gradually.', 'FRM_FALLOFF'),
 ('Shardborn armor upgrades to +10, with Ascendant needed at +5 and +10.', 'shardborn.csv'),
 ('A Rite\'s cooldown grows with its magnitude, duration and area, between 6 and 90 seconds.', 'ITM_F_RITE_COST'),
 ('Each co-op player rolls their own loot. Nobody takes yours.', 'ITM_F_DROP'),
 ('Bosses roll gear at four times the weight for Rare and better.', 'ITM_F_DROP_RARITY'),
 ('Drained enemies lose 3% of max Ward and Breath per second, and the attacker heals while it lasts.', 'STS_DRAIN'),
 ('Three Slows inside 10 seconds freeze a target for 2.5 seconds, and frozen targets take x1.3 damage.', 'STS_SLOW'),
 ('Exhausted lasts 1.5 seconds: no rolls, no sprint, Breath regen halved. Leave a sliver of Breath.', 'STS_EXHAUST'),
 ('Raid wipes reset the encounter after 10 seconds and cost no Ember.', 'loops 06'),
 ('Arena caps Tonics at 3 per life.', 'loops 06'),
 ('Ranked Arena sets every weapon to +15, whatever you have upgraded.', 'loops 06'),
 ('Featured Strikes pay double Seals on your first 3 clears each week.', 'loops 06'),
 ('A +20 weapon needs 9 Starmetal and 4 Ascendant in total.', 'loops 06'),
]


def gen_tips():
    S = rd(DATA + '/ui/strings.csv')
    existing = [r['text_en'] for r in S if r['screen'] == 'Loading screens' or r['str_id'].startswith(('STR_TIP_', 'STR_LORE_'))]
    nums = [int(m.group(1)) for r in S for m in [re.match(r'STR_TIP_(\d{3})$', r['str_id'])] if m]
    start = (max(nums) + 1) if nums else 1
    T = Table('loading_tips', 200)
    cols = COLS + ['region', 'tip_type']

    def words(t):
        return set(re.findall(r'[a-z0-9]+', t.lower())) - {'the', 'a', 'and', 'of', 'to', 'it', 'is', 'you', 'your', 'in', 'for', 'on', 'at'}
    ex_words = [words(t) for t in existing]

    def dup_existing(t):
        w = words(t)
        return any(len(w & e) / max(1, len(w | e)) >= 0.5 for e in ex_words)
    mech = []

    def add_m(t, region, src):
        if len(t) <= 140 and not dup_existing(t) and t not in [m[0] for m in mech]:
            mech.append((t, region, src))
    for r in rd(DATA + '/actors/status_effects.csv'):
        if r['Enemy threshold (base)'] in ('-', ''):
            continue
        add_m('%s needs %s buildup on most enemies. Once it ends, they resist it for %s seconds.' % (r['Status'], r['Enemy threshold (base)'], r['Immunity after s']), 'ALL', r['STS_ID'])
    elem_reg = {REG[k]['elem']: k for k in ('REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06')}
    frames_e = ['%s Wards take triple Ward damage from %s. Much of %s carries %s.', '%s breaks before %s three times as fast. Pack accordingly for %s, where %s runs strong.']
    for i, e in enumerate(['Ember', 'Storm', 'Hollow', 'Frost', 'Bloom', 'Iron']):
        c = counter_of(e)
        reg = elem_reg.get(e, 'ALL')
        rn = REG[reg]['name'] if reg in REG else 'Veyl'
        add_m((frames_e[0] % (e, c, rn, e)) if i % 2 == 0 else ('An %s Ward breaks three times as fast under %s. %s runs on %s.' % (e, c, rn, e) if e[0] in 'AEIOU' else 'A %s Ward breaks three times as fast under %s. %s runs on %s.' % (e, c, rn, e)), reg, 'element_matrix')
    add_m('Kinetic damage does half against a Ward. Weave damage does 1.5 times, then 0.8 against Health.', 'ALL', 'FRM_WARDHIT')
    for r in rd(DATA + '/actors/resonances.csv'):
        nm = re.sub(r'\s*\(.*?\)', '', r['Resonance'])
        src = r['Source']
        m = re.search(r'ACT_BOSS_\w+', src)
        who = name_of(m.group(0)) if m else src
        add_m('%s comes from %s. It recharges in %s seconds.' % (nm, who, r['Cooldown s']), r['Region'], r['RES_ID'])
    for r in rd(DATA + '/actors/origins.csv'):
        add_m('%s starts at Might %s, Finesse %s, Lore %s, Grit %s. Any build is still open from there.' % (r['Origin'], r['Might'], r['Finesse'], r['Lore'], r['Grit']), 'ALL', r['ORG_ID'])
    for r in rd(DATA + '/actors/attributes.csv'):
        add_m('%s gains slow after %s points and again after %s. It stops at %s.' % (r['Attribute'], r['Soft cap 1'], r['Soft cap 2'], r['Hard cap']), 'ALL', r['ATTR_ID'])
    for r in rd(DATA + '/items/infusions.csv'):
        if r['name'] in ('Plain',):
            continue
        if r['element']:
            add_m('%s infusion turns 40%% of physical damage into %s. On a firearm, all of it.' % (r['name'], r['element']), elem_reg.get(r['element'], 'ALL'), r['infusion_id'])
        else:
            add_m('%s infusion: %s.' % (r['name'], r['rule'].replace(';', ',')), 'ALL', r['infusion_id'])
    for r in rd(DATA + '/items/arena_power_weapons.csv'):
        add_m('The %s respawns every %s seconds in Arena: %s.' % (r['name'], r['respawn_s'], r['special']), 'REG_END', r['item_id'])
    for r in rd(DATA + '/actors/coop_scaling.csv'):
        if r['COOP_ID'] in ('COOP_OW_3', 'COOP_OW_4', 'COOP_BOSS_4'):
            add_m('With %s players, %s enemies get x%s health and x%s stance.' % (r['Players'], 'boss' if 'BOSS' in r['COOP_ID'] else 'open-world', r['Enemy HP mult'], r['Stance mult']), 'ALL', r['COOP_ID'])
    for t, s in FACT_TIPS:
        add_m(t, 'ALL', s)
    perks = rd(DATA + '/actors/perks.csv')
    for r in perks:
        if r['Skill rank required'] == '100':
            eff = r['Effect (per rank)'].replace('CAPSTONE: ', '')
            t = '%s, the %s capstone at rank 100: %s.' % (r['Perk'], name_of(r['SKL_ID']).title() if False else next((s['Skill'] for s in rd(DATA + '/actors/skills.csv') if s['SKL_ID'] == r['SKL_ID']), r['SKL_ID']), eff)
            add_m(t, 'ALL', r['PRK_ID'])
    mech = mech[:100]
    # lore tips
    LF = ['<Reg> saying: "<saying>" Said at doors, at funerals and to stubborn goats.',
          'Ask for <food> in <town> and you will get it, with an opinion.', '<Town> <custom>.',
          'In <reg>, calling someone <insult> starts a fight. Calling them cold-slept ends a friendship.',
          '<Reg> <people> greet each other with <greeting> and swear <oath>.', 'Children in <town2> play Bays and Ladders with <token> for counters.',
          '<Reg> fears <fear> more than any Kindled.', 'The fastest Strider in <town> is always named <weather>. There have been eleven.',
          'Nobody in <town> says "vented" where a priest can hear. They say "the long sleep" and look at their boots.',
          'In <town2>, "red-lit" means trouble and "green board" means supper is ready.',
          'If an elder in <town> says "logged", the matter is closed. If they say it twice, leave.',
          'On Lighting Night, every berth in <town> lights an Ember lamp and names its dead aloud.',
          'On Fall Day, <town> stays up until wake-call. Children get a ship biscuit and a long story.',
          'Most hands in <reg> know <work>. Most mouths in <reg> know an opinion about it.']
    CREW = ['Hydroponics reports beans again. Morale reports beans again.', 'Whoever keeps feeding Ballast: the cat is now over regulation weight.',
            'Shift change at wake-call. Coffee is a privilege, not a right.', 'Reminder: the captain\'s chair is not a coat rack.',
            'Galley is out of salt. Galley is not out of opinions.', 'Seal your bulkhead before you sleep.', 'The stars are where we left them. Good.',
            'Medbay requests the return of all borrowed blankets.', 'Engineering asks that nobody hum near the reactor ring. It hums back.',
            'Observation Deck closed for cleaning. Someone cried on the glass again.', 'Check your pod numbers twice. The long sleep is a long time.',
            'Green board on all decks. Go to bed.', 'Do not drift in the corridors. Walk like you mean it.',
            'Shuttle Bay inventory: four shuttles, three pilots, one argument.', 'Archive Core: please stop renaming the files.',
            'If you are reading this, you are on the deck. Congratulations.', 'Chapel hours extended. Bring your own candle.',
            'Officers\' Quarters: lights out means lights out.', 'Cargo Hold: whoever stacked the seed crates upside down, thank you for nothing.',
            'All crew: write home, even if home cannot write back.', 'Lost: one wrench, sentimental value. Ask for Pell.',
            'The bridge asks for quiet during approach. The bridge always asks for quiet.', 'Cryo Bay 3 is cold. That is the point of Cryo Bay 3.',
            'Someone left a plant on the reactor ring. It is thriving. Nobody touch it.']
    DECKS = ['Bridge', 'Hydroponics', 'Cargo Hold', 'Chapel', 'Cryo Bay 3', 'Engineering', 'Medbay', 'Observation Deck', 'Officers Quarters',
             'Reactor Ring', 'Shuttle Bay', 'Archive Core']
    OCC = ['before a long walk', 'over a new boat', 'when the bread rises', 'at the first snow', 'at weddings, to groans', 'over a sick Strider',
           'to children who will not sleep', 'when a lamp is lit', 'at funerals, softly', 'before a hard bargain', 'when the well is low', 'at the end of a shift']
    lore = []
    regs = [k for k in REG]
    quota = {k: 11 for k in regs}
    quota[regs[0]] += 100 - 11 * len(regs)
    ci = 0
    for reg in regs:
        R = REG[reg]
        sl = dict(reg=R['name'], town=R['town'], town2=R['town2'], **{k: R[k] for k in ('saying', 'food', 'custom', 'insult', 'people', 'greeting', 'oath', 'token', 'fear', 'weather', 'work')})
        n_log = 3 if reg != 'REG_Q' else quota[reg]
        frames = [f for f in LF if all(sl.get(s.lower()) for s in SLOT.findall(f))]
        if reg in ('REG_Q', 'REG_U'):
            frames = [f for f in frames if not re.search(r'Lighting Night|Fall Day|Bays|Strider|elder|red-lit|vented', f)]
        rg = rng('lore' + reg)
        rg.shuffle(frames)
        got = 0
        for f in frames:
            if got >= quota[reg] - n_log:
                break
            t = fill(f, sl, rg)
            if len(t) <= 140 and not dup_existing(t):
                lore.append((t, reg, 'region culture (02-world-life 7)'))
                got += 1
        while got < quota[reg]:
            line = CREW[ci % len(CREW)]
            ci += 1
            cit = 'Log, %s %d:%d' % (DECKS[rg.randrange(len(DECKS))], rg.randint(1, 40), rg.randint(1, 20))
            if reg == 'REG_Q':
                t = '"%s" %s. %s' % (line, cit, rg.choice(['In the Quiet, Choirborn repeat it in borrowed voices.', 'Hush keeps it filed with the harvest records.',
                                                           'It is cut into a Granary door, upside down.', 'A Choirborn hummed it once, slightly off.',
                                                           'The Quiet stores it like seed.']))
            else:
                t = '"%s" %s. %s reads it %s.' % (line, cit, cap1(R['name']), rg.choice(OCC))
            if len(t) > 140:
                t = '"%s" %s.' % (line, cit)
            if len(t) <= 140:
                lore.append((t, reg, 'Church Log quote; mundane crew line, safe for reveal ladder'))
                got += 1
    k = start
    for t, reg, src in mech:
        T.add('STR_TIP_%03d' % k, 'LOADING', 'tip_mechanics', t, 140, notes='source: ' + src, region=reg, tip_type='mechanics')
        k += 1
    for t, reg, src in lore[:100]:
        T.add('STR_TIP_%03d' % k, 'LOADING', 'tip_lore', t, 140, notes=src, region=reg, tip_type='lore')
        k += 1
    return T, cols, start, len(existing)


# ---------------------------------------------------------------- checks
BANNED = STYLE_BANNED + ['journey', 'ancient']


def banned_hits(t):
    lt = t.lower()
    hits = [w for w in BANNED if re.search(r'\b' + re.escape(w) + r'\w*', lt)]
    if '...' in t or '…' in t:
        hits.append('ellipsis')
    if '!' in t:
        hits.append('exclamation')
    return hits


def check(T, cols, path, extra_tok=None):
    rows = T.rows
    assert rows, path
    ids = collections.Counter(r['str_id'] for r in rows)
    dup_ids = [k for k, v in ids.items() if v > 1]
    texts = collections.Counter(r['text_en'] for r in rows if r['kind'] != 'quest_name')
    qn = collections.Counter(r['text_en'] for r in rows if r['kind'] == 'quest_name')
    for k, v in qn.items():
        if v > 1:
            print('   NOTE campaign quest name used %d times: %s' % (v, k))
    dups = [k for k, v in texts.items() if v > 1]
    bad = []
    for r in rows:
        if not r['text_en'].strip():
            bad.append((r['str_id'], 'empty'))
        if r['_cap'] and len(r['text_en']) > r['_cap']:
            bad.append((r['str_id'], 'over cap'))
        h = banned_hits(r['text_en'])
        if h:
            bad.append((r['str_id'], h))
        if extra_tok:
            for tok in re.findall(r'\{[A-Za-z]+_[a-z_]+\}', r['text_en']):
                if tok not in extra_tok:
                    bad.append((r['str_id'], 'token ' + tok))
    kinds = collections.Counter(r['kind'] for r in rows)
    print('%-18s rows=%5d dup_text=%d dup_ids=%d problems=%d max_frame_share=%.3f kinds=%s' % (
        T.name, len(rows), len(dups), len(dup_ids), len(bad), T.frame_share(), dict(kinds)))
    for b in bad[:15]:
        print('   PROBLEM', b)
    for d in dups[:10]:
        print('   DUP', d)
    for d in dup_ids[:10]:
        print('   DUP ID', d)
    return not bad and not dups and not dup_ids


def main():
    load_names()
    load_namebanks()
    for r in rd(DATA + '/world/npcs.csv'):
        if r['fac_id'] and r['role'] == 'Faction leader':
            NPC_FAC[r['act_id']] = r['fac_id']
    ok = True
    QT, quests, src, n_camp, world_only = gen_quests()
    ok &= check(QT, COLS, 'quest_text')
    RT, tpl, rsrc = gen_radiant()
    ok &= check(RT, COLS, 'radiant_text', ALLOWED_RAD_TOK)
    TT, tcols, treqs, tstats = gen_tutorials()
    ok &= check(TT, tcols, 'tutorial_text')
    OT, ocols = gen_ostra()
    ok &= check(OT, ocols, 'ostra_hints')
    LT, lcols, tip_start, n_exist = gen_tips()
    ok &= check(LT, lcols, 'loading_tips')
    if not ok and '--force' not in sys.argv:
        raise SystemExit('self-check failed; nothing written')
    write(OUT + '/quest_text.csv', QT.rows, COLS)
    write(OUT + '/radiant_text.csv', RT.rows, COLS)
    write(OUT + '/radiant_templates_writing.csv', tpl, ['rad_id', 'name', 'kind', 'giver_faction', 'slots', 'twist_pool', 'reward_rule', 'notes'])
    write(OUT + '/tutorial_text.csv', TT.rows, tcols)
    write(OUT + '/ostra_hints.csv', OT.rows, ocols)
    write(OUT + '/loading_tips.csv', LT.rows, lcols)
    reqs = list(treqs)
    reqs += [
     dict(id='STR_QUEST_TEXT', request='Move STR_<QST>_NAME/OFFER/DONE/STEP_nn/STEP_nn_DIR/JRN_nn/BR_nn/BR_nn_OUT rows from design/writing/quest_text.csv into data/ui/strings_data.csv once status=approved', target_table='data/ui/strings_data.csv', notes='%d rows' % len(QT.rows)),
     dict(id='STR_RAD', request='Move STR_RAD_<id>_NOTICE/GIVER/DONE/TWIST rows into data/ui/strings_data.csv once approved', target_table='data/ui/strings_data.csv', notes='%d rows' % len(RT.rows)),
     dict(id='TOKEN_LOC', request='Allow the {LOC_name} runtime token prefix (LOC) in UI text; radiant notices use it for the site', target_table='data/README.md (token prefixes)', notes='README allows ITM ACT PRK VAR BTN SKL ATTR ELEM STATUS FAC CMP REGION only; style guide 5 lists {SITE}{TARGET}{TWIST}{REWARD} for notices; this table uses {LOC_name}{ACT_name}{ITM_name}{VAR_reward} per the writing brief'),
     dict(id='STR_OSTRA_HINT', request='Add STR_OSTRA_HINT_* rows (warm and _COLD variants) to data/ui/strings_data.csv; add a HUD hint color state for cold hints; suppress all hints during MQ_A2_07', target_table='data/ui/strings_data.csv; data/ui/popups.csv', notes='%d rows incl. cold variants and one rule row' % len(OT.rows)),
     dict(id='STR_TIP_NUMBERING', request='New loading tips are numbered STR_TIP_%03d..%03d because STR_TIP_001..052 already exist in data/ui/strings.csv' % (tip_start, tip_start + len(LT.rows) - 1), target_table='data/ui/strings.csv', notes='region column lets loading screens filter; ALL = any region, REG_END = endgame screens'),
     dict(id='STR_TIP_008', request='Fix: says you drop half your Ember on death; data says all carried Ember drops and half burns only if you die again first', target_table='data/ui/strings.csv', notes='FRM_DEATH, ITM_F_DEATH_EMBER, ECOF_DEATH'),
     dict(id='STR_TIP_018', request='Fix: headshots double damage only when the target Ward is 0 (x1.25 on Ward), not "to most enemies"', target_table='data/ui/strings.csv', notes='FRM_HEADSHOT'),
     dict(id='STR_TIP_021', request='Check: Root duration says 2.5 s; status_effects.csv says 3 s', target_table='data/ui/strings.csv', notes='STS_ROOT'),
     dict(id='STR_TIP_037', request='Fix: the tip quoted a weekly Seal figure other than the cap; the cap is settled at 100 Seals a week (plan 3.10)', target_table='data/ui/strings.csv; data/actors/economy_formulas.csv; design/loops/06-endgame.md', notes='TUT_SEALS avoids the number until settled'),
     dict(id='STR_TIP_051', request='Check: status decay "after 3 seconds" vs ITM_F_STATUS "decay 10/s after 2 s"', target_table='data/ui/strings.csv', notes=''),
     dict(id='STR_TIP_REG_R2_R3_R5', request='Fix level bands: Saltmere 10-22, Thornwood 20-34, Rimefall 44-58 per data/world/regions.csv', target_table='data/ui/strings.csv', notes='strings say 10-24, 22-36, 42-58'),
     dict(id='STR_TUT_DEATH_B', request='Replace with the rewrite in tutorial_text.csv (all carried Ember drops)', target_table='data/ui/strings.csv', notes=''),
     dict(id='STR_TUT_SURGE_B', request='Replace with the rewrite in tutorial_text.csv (banned word)', target_table='data/ui/strings.csv', notes=''),
     dict(id='STR_TUT_ECHO_B', request='Replace with the rewrite in tutorial_text.csv (Echo Lantern)', target_table='data/ui/strings.csv', notes='also STR_TIP_024 says spirit allies summoned at an Anchor; fine but name the Echo Lantern'),
     dict(id='STR_TUT_QUIET_B', request='Replace with the rewrite in tutorial_text.csv (Strikes and Citadels are not in the Quiet)', target_table='data/ui/strings.csv', notes=''),
    ]
    write(OUT + '/requests_quests.csv', reqs, ['id', 'request', 'target_table', 'notes'])
    print('QUESTS: %d quests covered (%d from %s, %d world-only skeletons: %s); %d steps, %d branches' % (
        len(quests), n_camp, src, len(world_only), ' '.join(w['qst_id'] for w in world_only) or 'none',
        sum(len(q.get('steps', [])) for q in quests), sum(len(q.get('branches', [])) for q in quests)))
    print('RADIANT: %d templates from %s; tutorials %s; tips start at STR_TIP_%03d (existing loading strings: %d)' % (len(tpl), rsrc, dict(tstats), tip_start, n_exist))


if __name__ == '__main__':
    main()
