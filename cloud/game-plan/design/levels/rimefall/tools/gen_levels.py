#!/usr/bin/env python3
"""Rimefall (REG_05) level design generator.

Reads the live world tables (design/world/), the campaign seeds and data/,
and writes every Rimefall level as tables, one-page sheets and node-graph SVGs.
Re-run after the world or campaign threads regenerate:  python3 tools/gen_levels.py
Every value not taken from the plan, data/ or design/world/ is a Shardfall design
choice (3 Oct 2026), deterministic per loc_id so reruns are stable.
"""
import csv, glob, hashlib, json, math, os, random, re
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
GP = os.path.abspath(os.path.join(OUT, '..', '..', '..'))
W = os.path.join(GP, 'design', 'world')
D = os.path.join(GP, 'data')
REG = 'REG_05'


def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def wr(name, rows, cols):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)


def rng(key):
    return random.Random(int(hashlib.md5(key.encode()).hexdigest()[:8], 16))


def short(loc):  # LOC_DGN_REG_05_03 -> DGN_05_03
    return loc.replace('LOC_', '').replace('REG_05', '05').replace('__', '_')

# ---------------------------------------------------------------- load
LOC = [r for r in rd(os.path.join(W, 'locations.csv')) if r['region'] == REG]
LB = {r['loc_id']: r for r in LOC}
SITES = {r['loc_id']: r for r in rd(os.path.join(W, 'sites.csv')) if r['region'] == REG}
ENC = [r for r in rd(os.path.join(W, 'encounters.csv')) if r['region'] == REG]
ENC_BY = defaultdict(list)
for e in ENC:
    ENC_BY[e['loc_id']].append(e)
ENCID = {e['enc_id']: e for e in ENC}
ARENA = {r['loc_id']: r for r in rd(os.path.join(W, 'boss_arenas.csv')) if r['region'] == REG}
CITZ = {r['loc_id']: r for r in rd(os.path.join(W, 'citadel_zones.csv')) if r['loc_id'].startswith('LOC_CIT_REG_05')}
SECRETS = [r for r in rd(os.path.join(W, 'secrets.csv')) if r['region'] == REG]
ANCH = [r for r in rd(os.path.join(W, 'anchors.csv')) if r['region'] == REG]
LMK = {r['loc_id']: r for r in rd(os.path.join(W, 'landmarks.csv')) if r['region'] == REG}
NPCP = [r for r in rd(os.path.join(W, 'npc_placement.csv')) if 'REG_05' in r['home_loc'] or 'REG_05' in r['schedule']]
LAY = [r for r in rd(os.path.join(W, 'regions_layout.csv')) if r['reg_id'] == REG][0]
CONS = [r for r in rd(os.path.join(W, 'connections.csv')) if REG in (r['from_reg'], r['to_reg'])]
STEMPL = {r['site_type']: r for r in rd(os.path.join(W, 'site_templates.csv'))}
LORE = [r for r in rd(os.path.join(D, 'items', 'lore_items.csv')) if r['region'] == REG]
LORE_BY = defaultdict(list)
for r in LORE:
    LORE_BY[r['location']].append(r)
BOSS = {r['ACT_ID']: r for r in rd(os.path.join(D, 'actors', 'bosses.csv')) if r['Region'] == REG}
ENEMY = {r['ACT_ID']: r for r in rd(os.path.join(D, 'actors', 'enemies.csv'))}
CRT = {r['ACT_ID']: r for r in rd(os.path.join(D, 'actors', 'creatures.csv'))}
GEAR = []
for f, cat in (('weapons_melee', 'W'), ('weapons_firearm', 'F'), ('armor_pieces', 'A'), ('catalysts', 'C')):
    GEAR += [(r['item_id'], r['rarity'], cat) for r in rd(os.path.join(D, 'items', f + '.csv')) if r.get('first_region') == REG]
GEAR.sort()
SHB_Q = [r for r in rd(os.path.join(D, 'world', 'quests.csv')) if r['region'] == REG]
LGT = [r['lgt_id'] if 'lgt_id' in r else list(r.values())[0] for r in rd(os.path.join(GP, 'design', 'art', 'lighting_tod.csv')) if REG in list(r.values())[1]]

# campaign seeds: every quest step that touches a Rimefall location
QHOOK = defaultdict(list)
# campaign seed places that are existing levels (design choice: hooks attach to the real level)
CQ_ALIAS = {'LOC_CQ_REG_05_ABBOTS_CRYPT': 'LOC_DGN_REG_05_10', 'LOC_CQ_REG_05_CONSERVATORY': 'LOC_CIT_REG_05',
            'LOC_CQ_REG_05_YSSES_CONSERVATORY': 'LOC_CIT_REG_05_Z5', 'LOC_CQ_REG_05_YSSE_CONSERVATORY': 'LOC_CIT_REG_05_Z5',
            'LOC_CQ_REG_05_CONSERVATORY_GLASSHOUSE': 'LOC_CIT_REG_05_Z4', 'LOC_CQ_REG_05_COOLANT_WORKS': 'LOC_CIT_REG_05_Z6',
            'LOC_CQ_REG_05_RELAY_TOWER': 'LOC_RELAY_REG_05', 'LOC_CQ_REG_05_RIME_CHOIR': 'LOC_CHOIR_REG_05',
            'LOC_CQ_REG_05_STILL_LAKE': 'LOC_CIT_REG_05_Z8', 'LOC_CQ_REG_05_WHITE_TOWER': 'LOC_DGN_REG_05_03',
            'LOC_CQ_REG_05_PASS_HOLLOW': 'LOC_TOWN_REG_05_02'}
# new quest spaces: proposed host level for placement (world thread sets final x/y)
CQ_NEAR = {'LOC_CQ_REG_05_TITAN_PASS': 'LOC_FB_FROSTTITAN', 'LOC_CQ_REG_05_HEARTHWARD_PASS': 'LOC_TOWN_REG_05_01',
           'LOC_CQ_REG_05_WHITE_TOWER_ROAD': 'LOC_DGN_REG_05_03', 'LOC_CQ_REG_05_SEV_ICEHOUSE': 'LOC_TOWN_REG_05_01',
           'LOC_CQ_REG_05_ELK_VALLEY': 'LOC_POI_REG_05_25', 'LOC_CQ_REG_05_FROZEN_GATE': 'LOC_CIT_REG_05_Z1',
           'LOC_CQ_REG_05_FROZEN_PASS': 'LOC_LMK_REG_05_07', 'LOC_CQ_REG_05_HIGH_ROAD': 'LOC_LMK_REG_05_05',
           'LOC_CQ_REG_05_PACT_CAIRN': 'LOC_POI_REG_05_09'}
CQ_LOCS = set()
for p in glob.glob(os.path.join(GP, 'design', 'campaign', 'seeds', '*.json')):
    try:
        qs = json.load(open(p))
    except Exception:
        continue
    for q in qs if isinstance(qs, list) else []:
        for s in q.get('steps', []):
            l = s.get('loc', '')
            if 'REG_05' in l:
                l2 = CQ_ALIAS.get(l, l)
                QHOOK[l2].append('%s: %s%s' % (q.get('id'), s.get('text'), '' if l2 == l else ' (seed loc ' + l + ')'))
                if l2.startswith('LOC_CQ_'):
                    CQ_LOCS.add(l2)
# main quest hooks from the plan and 03-main-story (fixed IDs)
MAINQ = {
    'LOC_TOWN_REG_05_01': ['MQ_A2_04: the town is freezing; take the job from the elder', 'ACT_CMP_C2 Brother Odo recruit spot'],
    'LOC_CIT_REG_05': ['MQ_A2_04C: clear the Citadel to reach Mother Rime'],
    'LOC_CIT_REG_05_Z5': ['MQ_A2_04C: defeat ACT_BOSS_YSSE (Citadel quest complete)'],
    'LOC_CIT_REG_05_Z8': ['MQ_A2_04: thaw-the-pods choice, then ACT_BOSS_RIME; Lucid line; Heart Shard choice'],
    'LOC_RELAY_REG_05': ['MQ_RT_05: climb the Relay; Ostra fills the map; cryo coolant tanks line'],
    'LOC_UV_ENTRY_05': ['MQ_A2_06 (after two Heart Shards): one of three ways down to the Undervault'],
    'LOC_CHOIR_REG_05': ['Hidden Choir site: trial grants RES_BLINKCHORUS'],
}

# ---------------------------------------------------------------- design tables (choices)
BIOME_MOOD = {
    'Frozen highlands': ('Open white plateaus, wind-scoured rock, wolf tracks; lonely and exposed', '#DCE6EE snow, #5C6B78 rock'),
    'Drive-section glacier': ('Blue ice swallowing the Meridian drive section; hull ribs through the ice, coolant mist, humming Shards', '#9FD3E8 ice, #8FE3EE Shard, #3A4450 hull'),
    'Monastery valleys': ('Narrow valleys of terraced abbey ruins, prayer flags, bells in the wind; holy and dying', '#E9E2D4 stone, #B48A4A bronze, #8FE3EE Shard'),
}
KIT_INFO = {
    # kit: (room names, light, interior PPV, mood, traversal, ambience extra, vfx)
    'KIT_CAVE': (['Ice mouth', 'Frozen gallery', 'Crevasse bridge', 'Shard-lamp chamber', 'Meltwater pool', 'Collapsed shaft', 'Icicle hall', 'Wolf den', 'Rime chimney', 'Glass seam'],
                 'Dark; Shard-lamp pools 150-300 lux at 6500 K cyan, ice bounce; player lantern needed between pools',
                 'PPV_REG_05_CAVE', 'Tight, dripping, cold blue; sound of ice settling',
                 'Ice slides (downhill only, 6 m/s), crevasse jumps up to 3.0 m, crawl squeezes 2.4 m (no combat)',
                 'Play_AMB_RIM_INTERIOR (cave room tone)', 'VFX_ENV_RIM_ICEDRIP VFX_ENV_RIM_SHARDLAMP VFX_ENV_RIM_BREATHFOG'),
    'KIT_CATACOMB': (['Stair down', 'Ossuary niche hall', 'Frozen crypt row', 'Bone bridge', 'Reliquary', 'Flooded vault (frozen)', 'Lever hall', 'Abbot tombs', 'Charnel well', 'Sealed chapel', 'Coffin gallery'],
                     'Very dark; candle-shrine pools 80-150 lux at 2200 K, cyan Shard veins 40 lux; warm against cold',
                     'PPV_REG_05_CATACOMB', 'Silent and holy; frost on every skull; dread',
                     'Stairs and drop-downs (max safe drop 6 m), lever-operated portcullis, breakable coffin lids',
                     'Play_AMB_RIM_INTERIOR (catacomb room tone)', 'VFX_ENV_RIM_FROSTBREATH_TOMB VFX_ENV_RIM_CANDLE VFX_ENV_RIM_BREATHFOG'),
    'KIT_TOWER': (['Base hall', 'Spiral stair', 'Gallery floor', 'Outer cable run', 'Bell loft', 'Broken floor', 'Crown'],
                  'Daylight through arrow slits (shafts 2000 lux), storm-grey outside; height reads by wind gusts',
                  'PPV_REG_05_TOWER', 'Vertigo; wind howls louder each floor',
                  'Spiral stairs, outer cable climb (hold, 1.5 m/s), rope drop shortcut from the top; falls over 12 m kill',
                  'Play_AMB_RIM_WIND (altitude RTPC rises per floor)', 'VFX_ENV_RIM_SNOWGUST VFX_ENV_RIM_SPINDRIFT'),
    'KIT_MONASTERY': (['Gatehouse', 'Snowed cloister', 'Refectory', 'Bell tower base', 'Scriptorium', 'Dormitory', 'Prayer hall', 'Abbot cell', 'Garden of stones'],
                      'Overcast daylight in cloisters 8000 lux, interiors 300 lux candle and bronze lamp at 2700 K',
                      'PPV_REG_05_MONASTERY', 'Abandoned faith; prayer flags, bells, snow drifted through roofs',
                      'Roof walks, collapsed floors, bell ropes (climbable), snowdrifts slow sprint 20%',
                      'Play_AMB_RIM_EMITTERS (bells, flags)', 'VFX_ENV_RIM_SNOWFALL_INT VFX_ENV_RIM_PRAYERFLAG VFX_ENV_RIM_BELLDUST'),
    'KIT_WRECK': (['Hull breach', 'Frozen corridor', 'Cryo bay', 'Coolant junction', 'Maintenance shaft', 'Crew quarters', 'Power room', 'Bulkhead hall', 'Observation blister', 'Drive cradle'],
                  'Emergency strips 50 lux red #C24A3A, cryo pods glow 6500 K cyan, flashlight territory',
                  'PPV_REG_05_WRECK', 'Sci-fi dead ship under ice; pods, frost on glass, faint alarm loop',
                  'Ladders, crawl vents 2.4 m, zero-power doors pried open (2 s), tilted decks 15 deg',
                  'Play_SFX_World_Environment_TerminalBeep + Play_AMB_RIM_INTERIOR (wreck tone)', 'VFX_ENV_RIM_COOLANTMIST VFX_ENV_RIM_CRYOVENT VFX_ENV_RIM_SPARKS'),
    'KIT_FORT': (['Outer palisade', 'Gate yard', 'Barracks', 'Wall walk', 'Keep', 'Armory'],
                 'Exterior daylight; braziers 1800 K at night',
                 'PPV_REG_05', 'Hostile camp on a frozen ridge; smoke, banners, gun nests',
                 'Wall ladders, broken palisade gaps, gate winch, postern door; Strider allowed in the yard',
                 'Play_AMB_RIM_EMITTERS (fires, flags)', 'VFX_ENV_RIM_BRAZIER VFX_ENV_RIM_SNOWGUST'),
    'KIT_CHOIR_VAULT': (['Glass antechamber', 'Tone pillar hall', 'Resonant stair', 'Choir cell', 'Inner reliquary', 'Echo gallery'],
                        'Self-lit Choir glass 400 lux, cyan #8FE3EE with violet #9B7BD6 caustics; no shadows',
                        'PPV_REG_05_CHOIR', 'Beautiful and wrong; air hums a held chord',
                        'Glass floors (see-through drops), tone pillars, glass door shortcut from inside',
                        'Play_AMB_RIM_WEAVE_HUM (Shard_Proximity high)', 'VFX_ENV_RIM_CHOIRGLASS VFX_ENV_RIM_TONEPILLAR'),
}
SITE_KIT = {'Cave': 'KIT_CAVE', 'Catacomb': 'KIT_CATACOMB', 'Tower': 'KIT_TOWER', 'Monastery ruin': 'KIT_MONASTERY',
            'Wreck section': 'KIT_WRECK', 'Fort': 'KIT_FORT', 'Choir vault': 'KIT_CHOIR_VAULT'}
TEMPLATE_COVER = {'ENT_GUNLINE': ('long 50-120 m', 'low 6 high 4'), 'ENT_FORT': ('mid 15-50 m', 'low 5 high 3'),
                  'ENT_AMBUSH': ('close 0-15 m', 'low 1 high 2'), 'ENT_ELITE': ('mid 15-50 m', 'low 1 high 2'),
                  'ENT_HORDE': ('close 0-15 m', 'low 0 high 2'), 'ENT_KEEPER': ('mid 15-50 m', 'low 2 high 2'),
                  'ENT_PATROL': ('mid 15-50 m', 'low 2 high 1'), 'ENT_CAMP': ('mid 15-50 m', 'low 4 high 2'),
                  'ENT_CRT_PACK': ('mid 15-50 m', 'low 0 high 1'), 'ENT_CRT_SOLO': ('long 50-120 m', 'low 0 high 2')}
TEMPLATE_TRIGGER = {'ENT_AMBUSH': '12 m trigger volume at the room midpoint; 2 drop from ceiling or ledges',
                    'ENT_HORDE': 'Wake when the player crosses the room threshold or makes noise within 20 m',
                    'ENT_GUNLINE': 'Aware at 60 m line of sight; opens fire at 50 m',
                    'ENT_FORT': 'Aware at 40 m; alarm bell calls the yard in 6 s unless the ringer dies first',
                    'ENT_ELITE': 'Heavy idles facing away (backstab chance); escorts wake on hit',
                    'ENT_KEEPER': 'Scripted: keeper stands when the player passes the room midpoint; 2 s intro bark',
                    'ENT_PATROL': 'Walks a 150-300 m loop; detects at 25 m (12 m crouched)',
                    'ENT_CAMP': 'Idle around the fire; detect at 30 m; leader shouts orders',
                    'ENT_CRT_PACK': 'Pack sleeps; wakes at 15 m or on any shot within 40 m',
                    'ENT_CRT_SOLO': 'Territorial; warns at 40 m (roar), attacks at 25 m'}
ROLE_TALLY = re.compile(r'(ACT_[A-Z0-9_]+) x(\d+)')

POI_TEMPL = {
    'faction camp': (['Perimeter watch', 'Fire ring', 'Leader tent', 'Supply cache'], 4, 'Approach from the ridge to scout; leader tent holds the cache'),
    'ruin': (['Broken wall', 'Snowed court', 'Cellar'], 3, 'Climb the broken wall for the overlook; cellar holds the chest'),
    'wreck fragment': (['Hull plate field', 'Breach', 'Sealed locker'], 3, 'Pry the breach; locker needs Engineering 25 or a crowbar pull'),
    'wayshrine': (['Shrine step', 'Offering niche'], 2, 'Pray for a 10 min Frost resistance +10% blessing'),
    'watchtower': (['Tower foot', 'Ladder', 'Lookout'], 3, 'Lookout marks 3 nearby POIs on the compass'),
    'overturned cart': (['Wreckage', 'Body under snow'], 2, 'Small story vignette; corpse loot'),
    'overlook': (['Ledge path', 'Vista point'], 2, 'Vista point frames the Citadel; Shard-note slot'),
    'hermit hut': (['Yard', 'Hut interior'], 2, 'Hermit NPC by day, empty by night'),
    'grave field': (['Gate', 'Rows', 'Old cairn'], 3, 'Read 3 grave markers for a lore line'),
    'shard crater': (['Crater rim', 'Crater floor', 'Shard core'], 3, 'Shard core can be mined for Shard Dust (3 hits)'),
    'hunting ground': (['Tree line', 'Clearing', 'Den'], 3, 'Creature pack roams the clearing'),
    'lair': (['Mouth', 'Bone floor', 'Nest'], 3, 'Large creature sleeps in the nest'),
    'trader stop': (['Road bend', 'Fire and tent'], 2, 'Wandering trader stops here 1 game hour every 6'),
    'vehicle depot': (['Gate', 'Vehicle bay', 'Fuel shed'], 3, 'Spawns region vehicles; repair bench'),
}
TOWN_NODES = ['Town gate', 'Market square', 'Smithy', 'Trader', 'Hearth hall (inn)', 'Shrine Anchor', "Elder's house",
              'Faction contact', 'Strider stable', 'Watch wall', 'Houses (east)', 'Houses (west)']


def tally(actors):
    c = Counter()
    for a, n in ROLE_TALLY.findall(actors or ''):
        c[a] += int(n)
    return c


def lvl_of(l):
    m = re.findall(r'\d+', l.get('level', '') or '0')
    return int(m[-1]) if m else 0


def light_for(biome, kit=None):
    tod = 'LGT_REG_05_DAWN LGT_REG_05_DAY LGT_REG_05_DUSK LGT_REG_05_NIGHT LGT_REG_05_STORM'
    if kit:
        return KIT_INFO[kit][1] + '; volume ' + KIT_INFO[kit][2]
    return 'Exterior time of day ' + tod + '; volume PPV_REG_05; night above 700 m triggers blizzard (40 m visibility)'

# ---------------------------------------------------------------- outputs
LEVELS, NODES, ENCS, LOOT, CUES, POINTS = [], [], [], [], [], []
SVGS = {}
used_gear = set()
loot_n = [0]
cue_n = [0]
gear_pool = [g for g in GEAR]


def add_loot(level, node, item, qty, container, vis, cond=''):
    loot_n[0] += 1
    LOOT.append(dict(loot_id='LP_05_%04d' % loot_n[0], level_id=level, node_id=node, item=item, qty=qty,
                     container=container, visibility=vis, condition=cond))
    return item


def add_cue(level, node, trigger, audio, vfx='', note=''):
    cue_n[0] += 1
    CUES.append(dict(cue_id='CUE_05_%04d' % cue_n[0], level_id=level, node_id=node, trigger=trigger,
                     audio_event=audio, vfx_hook=vfx, notes=note))


def pick_gear(r, prefer=None):
    pool = [g for g in gear_pool if g[0] not in used_gear and (prefer is None or g[2] in prefer)]
    if not pool:
        pool = [g for g in gear_pool if g[0] not in used_gear] or gear_pool
    g = r.choice(pool)
    used_gear.add(g[0])
    return g[0]


def consumable(r):
    return r.choice(['ITM_CON_BRW_FRS', 'ITM_CON_BRW_EMB', 'ITM_CON_THR_FROST', 'ITM_CON_THR_SHARD', 'ITM_CON_THR_FLASH',
                     'ITM_CON_FOD_TEA', 'ITM_CON_FOD_STEW', 'ITM_CON_UTL_FLARE', 'ITM_CON_UTL_OIL', 'ITM_CON_UTL_AMMO_C',
                     'ITM_CON_UTL_AMMO_G', 'ITM_CON_UTL_ECHO', 'ITM_CON_BRW_WRD'])


def material(r):
    return r.choice(['ITM_MAT_DUST_01', 'ITM_MAT_GLASS_01', 'ITM_MAT_GLASS_01', 'ITM_MAT_DUST_01', 'ITM_MAT_INF_FRS',
                     'ITM_MAT_ESS_FRS', 'ITM_MAT_HULL_02', 'ITM_MAT_STAR_01'])


def node_id(level, i):
    return 'ND_%s_%02d' % (short(level), i)


def build_graph(level, names_types, crit_order, branches, shortcut_from, shortcut_to, shortcut_desc):
    """names_types: list of (name, type, floor, elev). crit_order: indices on critical path.
    branches: list of (from_idx, to_idx). Returns node rows (without contents)."""
    rows = []
    links = defaultdict(list)
    for a, b in zip(crit_order, crit_order[1:]):
        links[a].append((b, 'path'))
        links[b].append((a, 'back'))
    for a, b in branches:
        links[a].append((b, 'branch'))
        links[b].append((a, 'back'))
    if shortcut_from is not None:
        links[shortcut_from].append((shortcut_to, 'shortcut: ' + shortcut_desc))
        links[shortcut_to].append((shortcut_from, 'shortcut (locked until opened from the far side)'))
    for i, (nm, tp, fl, el) in enumerate(names_types):
        rows.append(dict(node_id=node_id(level, i + 1), level_id=level, order=i + 1, name=nm, node_type=tp,
                         floor=fl, elev_rel_m=el,
                         links=' | '.join('%s (%s)' % (node_id(level, j + 1), k) for j, k in links[i]),
                         critical_path='Y' if i in crit_order else 'N'))
    return rows


def size_for(r, tp):
    if tp in ('Boss arena',):
        return None
    w = {'Corridor': (4, 6), 'Room': (10, 18), 'Hall': (18, 30), 'Gun space': (40, 80), 'Puzzle': (12, 20),
         'Reward': (6, 10), 'Entrance': (8, 14), 'Branch': (6, 12), 'Exterior': (30, 80), 'Vertical': (8, 12)}.get(tp, (10, 16))
    a = r.randint(*w)
    b = r.randint(max(4, w[0]), w[1] + 6)
    h = r.choice([4, 5, 6, 8, 10]) if tp not in ('Vertical',) else r.choice([12, 18, 24])
    return '%d x %d x %d m' % (a, b, h)


def fmt_tally(c):
    return '; '.join('%s x%d' % (a, n) for a, n in sorted(c.items()))


def site_level(loc, kind_label):
    """Sites, Choir vaults (site template)."""
    s = SITES[loc]
    L = LB.get(loc, {})
    r = rng(loc)
    kit = s['template']
    names, light, ppv, mood, trav, amb, vfx = KIT_INFO.get(kit, KIT_INFO['KIT_CAVE'])
    nrooms = max(4, int(s['rooms'] or 6))
    floors = max(1, int(s['floors'] or 1))
    has_boss = s['end'].startswith('Site boss')
    boss = s['end'].split()[-1] if has_boss else ''
    interior_anchor = s.get('interior_anchor', '')
    nbranch = max(1, nrooms // 4)
    ncrit = max(5, nrooms - nbranch)
    # critical path rooms
    pool = names[1:]
    r.shuffle(pool)
    crit = [(names[0], 'Entrance')]
    mid = ncrit // 2
    puzzle = s.get('puzzle', '')
    for k in range(1, ncrit - 2):
        nm = pool[(k - 1) % len(pool)]
        tp = 'Corridor' if k % 3 == 1 else ('Hall' if k == mid else 'Room')
        if puzzle and k == min(ncrit - 3, mid + 1):
            nm, tp = 'Puzzle: ' + puzzle, 'Puzzle'
        crit.append((nm, tp))
    crit.append(('Boss arena' if has_boss else 'Keeper hall', 'Boss arena' if has_boss else 'Hall'))
    crit.append(('Reward room and shortcut', 'Reward'))
    branch = [('Side room: ' + pool[-(b + 1) % len(pool)], 'Branch') for b in range(nbranch)]
    allnodes = crit + branch
    sign = 1 if kit in ('KIT_TOWER',) else -1 if kit in ('KIT_CATACOMB', 'KIT_CAVE', 'KIT_WRECK') else 1
    nt = []
    for i, (nm, tp) in enumerate(allnodes):
        ci = i if i < len(crit) else r.randint(1, len(crit) - 3)
        fl = 1 + (ci * floors) // max(1, len(crit))
        el = sign * round(ci * (floors * 6 if kit != 'KIT_TOWER' else floors * 9) / max(1, len(crit) - 1))
        nt.append((nm, tp, fl, el))
    crit_idx = list(range(len(crit)))
    br = [(r.randint(1, len(crit) - 3), len(crit) + b) for b in range(nbranch)]
    rows = build_graph(loc, nt, crit_idx, br, len(crit) - 1, 0, s['shortcut'])
    # anchors
    rows[0]['anchor'] = s['entrance_anchor'] + ' (outside the entrance)'
    if interior_anchor:
        rows[mid]['anchor'] = interior_anchor
    # encounters
    encs = [ENCID[e] for e in s['encounters'].split() if e in ENCID] or ENC_BY.get(loc, [])
    keeper = [e for e in encs if e['template'] == 'ENT_KEEPER']
    elite = [e for e in encs if e['template'] == 'ENT_ELITE']
    rest = [e for e in encs if e not in keeper and e not in elite]
    slots = [i for i in range(1, len(crit) - 2)]
    place = {}
    for j, e in enumerate(rest):
        place[e['enc_id']] = slots[(j * max(1, len(slots) // max(1, len(rest)))) % len(slots)] if slots else 1
    for e in elite:
        place[e['enc_id']] = mid if mid < len(crit) - 2 else max(1, len(crit) - 3)
    for e in keeper:
        place[e['enc_id']] = len(crit) - 2
    for e in encs:
        i = place[e['enc_id']]
        rows[i].setdefault('encounters', []).append(e['enc_id'])
        enc_row(loc, rows[i]['node_id'], e)
    if has_boss:
        a = ARENA.get(loc, {})
        rows[len(crit) - 2]['size_m'] = '%s m %s' % (a.get('diameter_m', '38'), a.get('shape', 'round').lower())
        rows[len(crit) - 2]['notes'] = 'Fog gate 4 m; %s; arena hooks %s; nearest Anchor %s m' % (a.get('condition', ''), a.get('arena_hooks', ''), a.get('anchor_run_m', ''))
        bs = boss.replace('ACT_BOSS_', '')
        add_cue(loc, rows[len(crit) - 2]['node_id'], 'Fog gate crossed', 'Play_MUS_BOSS_%s_INTRO then _P1; _T2 and _P2 at %s%% HP; _WIN on kill' % (bs, BOSS.get(boss, {}).get('Phase HP thresholds %', '62')),
                'VFX_ENV_FOGGATE', 'Boss bar with STR_%s_NAME' % boss)
    # sizes, cover, light
    for i, n in enumerate(rows):
        n.setdefault('size_m', size_for(r, n['node_type']))
        tps = [ENCID[e]['template'] for e in n.get('encounters', [])]
        sl, cv = TEMPLATE_COVER.get(tps[0], ('close 0-15 m', 'low 1 high 1')) if tps else ('close 0-15 m', 'low 0 high 1')
        n['sightline'], n['cover'] = sl, cv
        n['light'] = light.split(';')[0]
    # loot
    lore_site = s.get('lore_site', '')
    rew = rows[len(crit) - 1]['node_id']
    add_loot(loc, rew, s['unique_reward'], 1, 'Pedestal chest (unique)', 'Lit by a Shard beam; seen from the boss room')
    for lr in LORE_BY.get(lore_site, []):
        tgt = rows[len(crit) + r.randrange(nbranch)]['node_id'] if lr['lore_type'] != 'Key' else rows[mid]['node_id']
        add_loot(loc, tgt, lr['item_id'], 1, 'Corpse or lectern' if lr['lore_type'] != 'Key' else 'Keeper or elite drop', 'Glint (lore shimmer)')
    for b in range(nbranch):
        nd = rows[len(crit) + b]['node_id']
        add_loot(loc, nd, pick_gear(r), 1, 'Chest', 'Hidden around a corner; 1 glint visible from the main path')
        add_loot(loc, nd, consumable(r), r.randint(1, 3), 'Corpse', 'Glint')
    for i in range(1, len(crit) - 2):
        if r.random() < 0.6:
            add_loot(loc, rows[i]['node_id'], material(r), r.randint(1, 3), 'Corpse or crate', 'Glint')
    add_loot(loc, rows[len(crit) - 2]['node_id'], 'ITM_CON_UTL_POUCH_M', 1, 'Keeper or boss drop', 'Drops on kill')
    for ch in [c for c in LOC if c['kind'] == 'Small chest' and c['parent_loc'] == loc]:
        nd = rows[len(crit) + r.randrange(nbranch)]['node_id']
        add_loot(loc, nd, 'ITM_LT_SMALLCHEST_REG_05', 1, 'Small chest ' + ch['loc_id'], 'Tucked behind cover')
    for ch in [c for c in LOC if c['kind'] == 'Shard crate' and c['parent_loc'] == loc]:
        add_loot(loc, rows[mid]['node_id'], 'ITM_LT_SHARDCRATE_REG_05', 1, 'Shard crate ' + ch['loc_id'], 'Cyan glow through the lid')
    if has_boss:
        for it in BOSS.get(boss, {}).get('Drops (item refs)', '').split(';'):
            if it.strip():
                add_loot(loc, rows[len(crit) - 2]['node_id'], it.strip().split()[0], 1, 'Boss drop', 'On kill')
    # secrets
    sec = [x for x in SECRETS if x['host_loc'] == loc]
    for x in sec:
        nd = rows[len(crit) + r.randrange(nbranch)]
        nd['secret'] = '%s: %s' % (x['loc_id'], x['secret_type'])
        add_loot(loc, nd['node_id'], x['reward'] if x['reward'].startswith('ITM_') else 'ITM_MAT_STAR_01 x1', 1, 'Secret ' + x['loc_id'], x['hint'])
    # interactables and cues
    rows[0]['interactables'] = 'Anchor (outside), site banner STR'
    add_cue(loc, rows[0]['node_id'], 'Enter site volume', 'Play_MUS_RIM_SITE; Play_AMB_RIM_INTERIOR', vfx.split()[0], 'Site name banner (BAN_) on first entry')
    if puzzle:
        pz = [n for n in rows if n['node_type'] == 'Puzzle']
        if pz:
            pz[0]['interactables'] = puzzle
            add_cue(loc, pz[0]['node_id'], 'Puzzle solved', 'Play_SFX_World_Environment_Lever; Play_MUS_STG_SECRET', 'VFX_ENV_RIM_PUZZLE_SOLVE')
    rows[len(crit) - 1]['interactables'] = 'Shortcut: ' + s['shortcut']
    add_cue(loc, rows[len(crit) - 1]['node_id'], 'Shortcut opened', 'Play_SFX_World_Environment_ShortcutUnlock', '', 'Popup NTF shortcut opened')
    add_cue(loc, rew, 'Unique reward taken', 'Play_SFX_World_Environment_ItemPickupByRarity', 'VFX_ENV_RIM_SHARDBEAM')
    for n in rows:
        n['encounters'] = ' '.join(n.get('encounters', []))
        n['audio'] = amb
        n['vfx'] = vfx
    NODES.extend(rows)
    SVGS[loc] = rows
    crit_s = ' > '.join(n['node_id'][-2:] + ' ' + n['name'] for n in rows if n['critical_path'] == 'Y')
    t = tally_level(loc)
    path = int(s['path_min'] or 15)
    LEVELS.append(base_level(loc, L, kind_label, s['name']) | dict(
        layout_type='Node graph, %s (%s), %d floors' % (s['site_type'], kit, floors), nodes=len(rows),
        critical_path=crit_s, branches=nbranch, encounters=len(encs), enemies=fmt_tally(t),
        boss=boss, anchors=' '.join(x for x in (s['entrance_anchor'], interior_anchor) if x),
        shortcut=s['shortcut'], puzzle=puzzle, traversal=trav, mood=mood + '. ' + BIOME_MOOD.get(L.get('biome', ''), ('', ''))[0],
        lighting=light + '; volume ' + ppv, music='MUS_RIM_SITE' + ('; MUS_BOSS_%s_*' % boss.replace('ACT_BOSS_', '') if boss else ''),
        ambience=amb, key_vfx=vfx, time_first_min=path, time_repeat_min=max(4, round(path * 0.4)),
        unique_reward=s['unique_reward']))


def tally_level(loc):
    c = Counter()
    for e in ENCS:
        if e['level_id'] == loc:
            c.update(tally(e['actors']))
    return c


def enc_row(level, node, e, extra_note=''):
    sl, cv = TEMPLATE_COVER.get(e['template'], ('', ''))
    t = tally(e['actors'])
    leader = [a for a in t if 'LEADER' in a]
    ENCS.append(dict(enc_id=e['enc_id'], level_id=level, node_id=node, template=e['template'], faction=e['faction'],
                     level=e['level'], actors=e['actors'], total=sum(t.values()), trigger=TEMPLATE_TRIGGER.get(e['template'], ''),
                     cover=cv, cover_points=e['cover_points'], fallback_points=e['fallback_points'], respawn=e['respawn'],
                     leader=' '.join(leader) + (' (kill: fodder panic 60% chance, flee 6 s)' if leader else ''),
                     sightline=sl, music='Threat RTPC drives MUS_RIM_COMBAT_L1..L3', notes=(e.get('condition', '') + ' ' + extra_note).strip()))


def base_level(loc, L, kind, name):
    return dict(level_id=loc, kind=kind, name=name, level=L.get('level', ''), biome=L.get('biome', ''), grid=L.get('grid', ''),
                x_m=L.get('x_m', ''), y_m=L.get('y_m', ''), z_m=L.get('z_m', ''),
                secrets=' '.join(x['loc_id'] for x in SECRETS if x['host_loc'] == loc),
                collectibles=' '.join(sorted(set(l['item'] for l in LOOT if l['level_id'] == loc and (l['item'].startswith('ITM_LOR_') or l['item'].startswith('ITM_CON_TNC'))))),
                quest_hooks=' | '.join(MAINQ.get(loc, []) + QHOOK.get(loc, [])),
                lore_alias='')

# ---------------------------------------------------------------- Citadel
CIT_ROOMS = {
    'Vertical climb': [('Stair foot', 'Exterior'), ('Switchback stair', 'Vertical'), ('Landing guardhouse', 'Room'), ('Upper stair', 'Vertical'), ('Gate terrace', 'Exterior')],
    'Gun gallery (40-80 m sightlines)': [('Gallery mouth', 'Corridor'), ('Long gallery', 'Gun space'), ('Gun nest', 'Room'), ('Winch room', 'Room')],
    'Boss approach': [('Cloister walk', 'Corridor'), ('Snowed garth', 'Hall'), ('Chapter house', 'Room'), ('Antechamber', 'Room')],
    'Mixed': [('Reliquary door', 'Corridor'), ('Relic hall', 'Hall'), ('Side chapels', 'Room'), ('Bridge mechanism', 'Room')],
    'Boss arena': [('Antechamber', 'Room'), ('Fog gate', 'Corridor'), ('Arena', 'Boss arena'), ('Lift or seat', 'Reward')],
}


def citadel():
    cit = LB['LOC_CIT_REG_05']
    zones = sorted(CITZ.values(), key=lambda z: int(z['order']))
    allrows = []
    for z in zones:
        loc = z['loc_id']
        r = rng(loc)
        tmpl = list(CIT_ROOMS.get(z['style'], CIT_ROOMS['Mixed']))
        if z['boss'] == 'ACT_BOSS_RIME':
            tmpl = [('Pod hall (frozen villagers)', 'Hall'), ('Fog gate', 'Corridor'), ('Still Lake court', 'Boss arena'), ('Elevator seat', 'Reward')]
        nt = [(nm, tp, 1 + i // 2, int(z['elevation_rel_m']) + i * 3) for i, (nm, tp) in enumerate(tmpl)]
        side = ('Side: ' + r.choice(['Ossuary niche', 'Bell loft', 'Collapsed scriptorium', 'Coolant pipe crawl', 'Pilgrim dormitory', 'Frozen kitchen']), 'Branch', 1, int(z['elevation_rel_m']) - 4)
        nt.append(side)
        crit = list(range(len(tmpl)))
        sc = z['shortcut']
        rows = build_graph(loc, nt, crit, [(1, len(nt) - 1)], None if 'none' in sc else len(tmpl) - 1, 0, sc)
        rows[0]['anchor'] = z['anchor']
        encs = [ENCID[e] for e in z['encounters'].split() if e in ENCID]
        for j, e in enumerate(encs):
            i = [1, 2, 0][j % 3] if len(tmpl) > 2 else 0
            if rows[i]['node_type'] == 'Boss arena':
                i = 0
            rows[i].setdefault('encounters', []).append(e['enc_id'])
            enc_row(loc, rows[i]['node_id'], e)
        if z['boss']:
            a = ARENA.get(loc, {})
            ar = [n for n in rows if n['node_type'] == 'Boss arena'][0]
            ar['size_m'] = '%s m %s' % (a.get('diameter_m', ''), a.get('shape', '').lower())
            ar['notes'] = '%s; hooks %s; Anchor %s at %s m' % (a.get('condition', ''), a.get('arena_hooks', ''), a.get('nearest_anchor', ''), a.get('anchor_run_m', ''))
            bs = z['boss'].replace('ACT_BOSS_', '')
            add_cue(loc, ar['node_id'], 'Fog gate crossed', 'Play_MUS_BOSS_%s_INTRO; _P1; _T2/_P2 at 65%%; _T3/_P3 at 30%%; _WIN' % bs, 'VFX_ENV_FOGGATE', '')
            for it in BOSS[z['boss']]['Drops (item refs)'].split(';'):
                it = it.strip().split()[0]
                add_loot(loc, ar['node_id'], it, 1, 'Boss drop', 'On kill')
            if BOSS[z['boss']].get('Resonance unlocked'):
                add_loot(loc, ar['node_id'], BOSS[z['boss']]['Resonance unlocked'], 1, 'Resonance (granted on kill)', 'Cinematic absorb')
            if z['boss'] == 'ACT_BOSS_RIME':
                for w in (1, 2):
                    e = dict(enc_id='LENC_05_RIME_W%d' % w, template='ENT_HORDE', faction='FAC_HOLLOWED', level='58',
                             actors='ACT_VAR_R5_01 x6; ACT_HOLLOWED_HEAVY x1', cover_points='5', fallback_points='0',
                             respawn='Never', condition='Only if pods were thawed (MQ_A2_04 choice)')
                    enc_row(loc, ar['node_id'], e, 'Wave %d spawns at %s HP from the pod alcoves' % (w, '65%' if w == 1 else '30%'))
                    ar.setdefault('encounters', []).append(e['enc_id'])
        if z['locked_door']:
            rows[-1]['interactables'] = 'Locked door %s (%s)' % (z['locked_door'], LB.get(z['locked_door'], {}).get('gate', ''))
        for n in rows:
            n.setdefault('size_m', size_for(r, n['node_type']))
            n['sightline'] = 'long 50-120 m' if n['node_type'] == 'Gun space' else 'mid 15-50 m' if n['node_type'] in ('Hall', 'Exterior') else 'close 0-15 m'
            n['cover'] = 'low 6 high 4' if n['node_type'] == 'Gun space' else 'low 2 high 2'
            n['light'] = 'Abbey: overcast 8000 lux outside, 300 lux candle and bronze lamp inside, Shard veins cyan; volume PPV_REG_05_CITADEL'
            n['audio'] = 'Play_MUS_RIM_CITADEL; Play_AMB_RIM_CITADEL'
            n['vfx'] = 'VFX_ENV_RIM_SNOWFALL_INT VFX_ENV_RIM_BELLDUST' + (' VFX_ENV_RIM_COOLANTMIST' if 'Coolant' in z['name'] or 'Crypt' in z['name'] else '')
            n['encounters'] = ' '.join(n.get('encounters', []))
        side_nd = rows[-1]['node_id']
        add_loot(loc, side_nd, pick_gear(r), 1, 'Chest', 'Off the main path; visible from the branch door')
        add_loot(loc, rows[1]['node_id'], material(r), r.randint(2, 4), 'Corpse', 'Glint')
        add_loot(loc, rows[0]['node_id'], consumable(r), 2, 'Corpse', 'Glint')
        if sc and 'none' not in sc:
            add_cue(loc, rows[len(tmpl) - 1]['node_id'], 'Shortcut opened', 'Play_SFX_World_Environment_ShortcutUnlock', '', sc)
        if z['anchor']:
            add_cue(loc, rows[0]['node_id'], 'Anchor lit', 'Play_MUS_STG_ANCHOR_LIT', 'VFX_ANCHOR_LIGHT', '')
        NODES.extend(rows)
        SVGS[loc] = rows
        allrows += rows
        t = tally_level(loc)
        LEVELS.append(base_level(loc, LB.get(loc, {}), 'Citadel zone', z['name']) | dict(
            layout_type='Node graph, Citadel zone %s of 8 (%s)' % (z['order'], z['style']), nodes=len(rows),
            critical_path=' > '.join(n['node_id'][-2:] + ' ' + n['name'] for n in rows if n['critical_path'] == 'Y'),
            branches=1, encounters=len([e for e in ENCS if e['level_id'] == loc]), enemies=fmt_tally(t), boss=z['boss'],
            anchors=z['anchor'], shortcut=sc, puzzle='', traversal='Stairs, ladders, bridge and lift shortcuts; no Strider inside the walls',
            mood='Saint Drive Abbey: a monastery built into the frozen drive section; bells, pilgrims frozen mid-prayer, Choir glass growing over stone',
            lighting='PPV_REG_05_CITADEL; ' + 'LGT_REG_05_DUSK as the authored key (Citadel weather locked to dusk for readability)',
            music='MUS_RIM_CITADEL' + ('; MUS_BOSS_%s_*' % z['boss'].replace('ACT_BOSS_', '') if z['boss'] else ''),
            ambience='Play_AMB_RIM_CITADEL', key_vfx=rows[0]['vfx'], time_first_min=z['path_min'],
            time_repeat_min=max(3, round(int(z['path_min']) * 0.35)), unique_reward=''))
    LEVELS.append(base_level('LOC_CIT_REG_05', cit, 'Citadel', cit['name']) | dict(
        layout_type='Side-view flow of 8 zones (see 02-citadel.md, maps/LOC_CIT_REG_05.svg)', nodes=len(allrows),
        critical_path=' > '.join(z['name'] for z in zones), branches=8, encounters=len([e for e in ENCS if e['level_id'].startswith('LOC_CIT_REG_05')]),
        enemies=fmt_tally(sum((tally_level(z['loc_id']) for z in zones), Counter())), boss='ACT_BOSS_YSSE ACT_BOSS_RIME',
        anchors=' '.join(z['anchor'] for z in zones if z['anchor']), shortcut='7 shortcuts (one per zone after Z1), big loop Z7 to Z4',
        traversal='Climb from 757 m to 889 m; no mounts inside', mood='The region\'s summit and its grief', lighting='PPV_REG_05_CITADEL',
        music='MUS_RIM_CITADEL', ambience='Play_AMB_RIM_CITADEL', key_vfx='', time_first_min=sum(int(z['path_min']) for z in zones),
        time_repeat_min=round(sum(int(z['path_min']) for z in zones) * 0.35), unique_reward='ITM_SHB_A05 ITM_SHB_W05',
        lore_alias=''))

# ---------------------------------------------------------------- other level kinds


def simple_level(loc, kind, nodes_spec, crit, layout, extra, enc_nodes=None, kit_light=None):
    L = LB.get(loc, {})
    r = rng(loc)
    nt = [(nm, tp, 1, i * 2) for i, (nm, tp) in enumerate(nodes_spec)]
    br = [(crit[-1] if crit else 0, i) for i in range(len(nt)) if i not in crit]
    rows = build_graph(loc, nt, crit, br, None, 0, '')
    encs = ENC_BY.get(loc, [])
    for j, e in enumerate(encs):
        i = (enc_nodes[j % len(enc_nodes)] if enc_nodes else min(len(rows) - 1, 1 + j))
        rows[i].setdefault('encounters', []).append(e['enc_id'])
        enc_row(loc, rows[i]['node_id'], e)
    for n in rows:
        n.setdefault('size_m', size_for(r, n['node_type']))
        tps = [ENCID[e]['template'] for e in n.get('encounters', []) if e in ENCID]
        sl, cv = TEMPLATE_COVER.get(tps[0], ('mid 15-50 m', 'low 2 high 1')) if tps else ('mid 15-50 m', 'low 1 high 1')
        n['sightline'], n['cover'] = sl, cv
        n['light'] = kit_light or 'Exterior time of day (LGT_REG_05_*)'
        n['audio'] = 'Play_AMB_RIM_BED_DAY/NIGHT; Play_AMB_RIM_WIND'
        n['vfx'] = 'VFX_ENV_RIM_SNOWGUST VFX_ENV_RIM_BREATHFOG'
        n['encounters'] = ' '.join(n.get('encounters', []))
    for x in [x for x in SECRETS if x['host_loc'] == loc]:
        nd = rows[-1]
        nd['secret'] = '%s: %s' % (x['loc_id'], x['secret_type'])
        add_loot(loc, nd['node_id'], x['reward'] if x['reward'].startswith('ITM_') else 'ITM_MAT_STAR_01 x1', 1, 'Secret ' + x['loc_id'], x['hint'])
    for ch in [c for c in LOC if c['kind'] == 'Small chest' and c['parent_loc'] == loc]:
        add_loot(loc, rows[-1]['node_id'], 'ITM_LT_SMALLCHEST_REG_05', 1, 'Small chest ' + ch['loc_id'], 'Behind the main prop')
    NODES.extend(rows)
    SVGS[loc] = rows
    t = tally_level(loc)
    row = base_level(loc, L, kind, L.get('name', loc)) | dict(
        layout_type=layout, nodes=len(rows), critical_path=' > '.join(n['node_id'][-2:] + ' ' + n['name'] for n in rows if n['critical_path'] == 'Y'),
        branches=len(rows) - len(crit), encounters=len(encs), enemies=fmt_tally(t), boss='', anchors=' '.join(a['loc_id'] for a in ANCH if a['parent_loc'] == loc),
        shortcut='', puzzle='', traversal='Open ground; Strider allowed; snow slows sprint 20% off-road',
        mood=BIOME_MOOD.get(L.get('biome', ''), ('', ''))[0], lighting=light_for(L.get('biome', '')),
        music='MUS_RIM_EXPLORE_DAY/NIGHT; MUS_RIM_DISCOVERY on first sight', ambience='Play_AMB_RIM_BED_DAY/NIGHT',
        key_vfx='VFX_ENV_RIM_SNOWGUST', time_first_min=3, time_repeat_min=1, unique_reward='')
    row.update(extra)
    LEVELS.append(row)
    return rows


def towns():
    for loc in sorted(l for l in LB if LB[l]['kind'] == 'Settlement'):
        L = LB[loc]
        main = loc.endswith('_01')
        spec = [(n, 'Exterior' if i in (0, 1, 9) else 'Room') for i, n in enumerate(TOWN_NODES if main else TOWN_NODES[:2] + TOWN_NODES[4:8] + TOWN_NODES[9:10])]
        rows = simple_level(loc, 'Town', spec, [0, 1], 'Hub-and-spoke: gate > square > buildings around it',
                            dict(traversal='Walk only inside the walls (Strider stabled at the gate); rooftops climbable on the east side',
                                 mood='Warm against the cold: chimney smoke, hearth light, people stamping snow off boots. ' + ('Main town, slowly freezing (MQ_A2_04)' if main else 'Small hamlet on the road'),
                                 lighting='Hearth windows 2700 K, lanterns at 1800 K at night; exterior LGT_REG_05_*',
                                 music='MUS_RIM_TOWN', ambience='Play_AMB_RIM_WALLA; Play_AMB_RIM_BED_DAY/NIGHT',
                                 key_vfx='VFX_ENV_RIM_CHIMNEYSMOKE VFX_ENV_RIM_HEARTHGLOW', time_first_min=25 if main else 10, time_repeat_min=5,
                                 lore_alias=''),
                            kit_light='Hearth 2700 K interiors; exterior LGT_REG_05_*')
        r = rng(loc)
        npcs = [n for n in NPCP if n['home_loc'] == loc]
        for n in rows:
            n['audio'] = 'Play_MUS_RIM_TOWN; Play_AMB_RIM_WALLA'
            n['vfx'] = 'VFX_ENV_RIM_CHIMNEYSMOKE'
        byname = {n['name']: n for n in rows}
        if 'Shrine Anchor' in byname:
            byname['Shrine Anchor']['anchor'] = ' '.join(a['loc_id'] for a in ANCH if a['parent_loc'] == loc) or 'Town Anchor'
            add_cue(loc, byname['Shrine Anchor']['node_id'], 'Anchor lit', 'Play_MUS_STG_ANCHOR_LIT', 'VFX_ANCHOR_LIGHT')
        if 'Smithy' in byname:
            byname['Smithy']['interactables'] = 'Smithing bench, vendor (town smith)'
        if 'Trader' in byname:
            byname['Trader']['interactables'] = 'Trader vendor; wandering trader stop ACT_NPC_VEN_TRADER_REG_05'
        for n in npcs:
            tgt = byname.get('Hearth hall (inn)', rows[1])
            tgt['interactables'] = (tgt.get('interactables', '') + '; ' + n['act_id'] + ' (' + n['name'] + ')').strip('; ')
        add_cue(loc, rows[0]['node_id'], 'Enter town volume', 'Play_MUS_RIM_TOWN', '', 'Region banner, combat disabled inside walls (weapons sheathed)')
        add_loot(loc, rows[-1]['node_id'], consumable(r), 2, 'Barrel', 'Free pickup')


def poi_levels():
    for loc in sorted(l for l in LB if LB[l]['kind'] == 'POI'):
        L = LB[loc]
        tag = L['tags']
        names, n, note = POI_TEMPL.get(tag, (['Approach', 'Center'], 2, ''))
        spec = [(nm, 'Exterior' if i == 0 else 'Room') for i, nm in enumerate(names)]
        encn = [1] if len(spec) > 1 else [0]
        rows = simple_level(loc, 'POI', spec, list(range(len(spec) - 1)) or [0], 'Small node graph (%s)' % tag,
                            dict(puzzle=note, time_first_min=2 + len(spec), time_repeat_min=1), enc_nodes=encn)
        r = rng(loc)
        add_loot(loc, rows[-1]['node_id'], material(r), r.randint(1, 3), 'Corpse or cache', 'Glint')
        if tag in ('faction camp', 'lair', 'wreck fragment', 'shard crater'):
            add_loot(loc, rows[-1]['node_id'], pick_gear(r) if r.random() < 0.5 else consumable(r), 1, 'Cache', 'Glint')
        if tag == 'wayshrine':
            add_cue(loc, rows[-1]['node_id'], 'Pray', 'Play_SFX_World_Environment_ShardHumLoop', 'VFX_ENV_RIM_SHRINEGLOW', 'Blessing: Frost resistance +10% for 600 s')
        if tag == 'vehicle depot':
            rows[1]['interactables'] = 'Vehicle spawn pad: ' + LAY['vehicles']
        if tag in ('overlook', 'watchtower'):
            add_cue(loc, rows[-1]['node_id'], 'Reach vista', 'Play_MUS_RIM_DISCOVERY', '', 'Marks nearby POIs')


def field_bosses():
    for loc in sorted(l for l in LB if LB[l]['kind'] == 'Field boss'):
        a = ARENA[loc]
        b = a['boss']
        spec = [('Approach road', 'Exterior'), ('Outer ring (leash edge)', 'Exterior'), ('Arena core', 'Boss arena'), ('Vantage rocks', 'Room'), ('Spoils', 'Reward')]
        rows = simple_level(loc, 'Field boss', spec, [0, 1, 2, 4], 'Open arena %s, %s m' % (a['shape'], a['diameter_m']),
                            dict(boss=b, traversal='Strider allowed; vantage rocks give a ranged perch 6 m up; ' + a['condition'],
                                 music='MUS_BOSS_%s_*' % b.replace('ACT_BOSS_', ''), time_first_min=12, time_repeat_min=4,
                                 anchors=a['nearest_anchor'], mood=(a.get('notes') or '') + ' ' + BIOME_MOOD.get(LB[loc]['biome'], ('', ''))[0]))
        ar = rows[2]
        ar['size_m'] = '%s m %s, %s cover pieces' % (a['diameter_m'], a['shape'].lower(), a['cover_pieces'])
        ar['notes'] = a['entry'] + '; hooks ' + a['arena_hooks']
        add_cue(loc, ar['node_id'], 'Boss wakes', 'Play_MUS_BOSS_%s_INTRO; _P1; _T2/_P2 at 62%%; _WIN' % b.replace('ACT_BOSS_', ''), 'VFX_ENV_RIM_BLIZZARDWALL' if 'blizzard' in (a.get('notes') or '').lower() else '')
        for it in BOSS[b]['Drops (item refs)'].split(';'):
            add_loot(loc, rows[4]['node_id'], it.strip().split()[0], 1, 'Boss drop', 'On kill')


def special_levels():
    # Relay
    loc = 'LOC_RELAY_REG_05'
    rows = simple_level(loc, 'Relay Tower', [('Tower foot', 'Exterior'), ('Stage 1: ledges', 'Vertical'), ('Stage 2: service lift', 'Vertical'), ('Stage 3: ladder', 'Vertical'), ('Summit dish', 'Reward')],
                        [0, 1, 2, 3, 4], 'Vertical climb in 3 stages, 80 m', dict(traversal='Ledges (grab and shimmy), service lift needs the breaker on stage 1, exposed ladder in wind gusts (pause 1 s every 4 s gust)',
                                                                                   music='MUS_RIM_EXPLORE_DAY then MUS_STG_MAP_FRAGMENT at the top', time_first_min=8, time_repeat_min=2), enc_nodes=[0])
    add_cue(loc, rows[4]['node_id'], 'Activate relay', 'Play_SFX_World_Environment_RelayTowerActivate; Play_MUS_STG_MAP_FRAGMENT', 'VFX_ENV_RELAY_PULSE', 'Region map revealed; Ostra MQ_RT_05 line')
    # Choir site
    loc = 'LOC_CHOIR_REG_05'
    rows = simple_level(loc, 'Choir site', [('Hidden approach (glass seam)', 'Exterior'), ('Glass antechamber', 'Room'), ('Trial of echoes', 'Hall'), ('Resonance chamber', 'Reward')],
                        [0, 1, 2, 3], 'Hidden linear site, 4 nodes', dict(traversal='Entrance appears only after a Shard-note hint or Ostra line within 40 m', music='MUS_RIM_SITE; MUS_STG_RESONANCE',
                                                                          mood='A held chord in the ice; the Choir still sings here', lighting=KIT_INFO['KIT_CHOIR_VAULT'][1], time_first_min=12, time_repeat_min=3), enc_nodes=[2], kit_light=KIT_INFO['KIT_CHOIR_VAULT'][1])
    add_loot(loc, rows[3]['node_id'], 'RES_BLINKCHORUS', 1, 'Resonance altar', 'Granted after the trial')
    add_cue(loc, rows[3]['node_id'], 'Resonance granted', 'Play_MUS_STG_RESONANCE; Play_SFX_Resonances_BlinkChorusGroupTeleport_OstraVoiceLine', 'VFX_ENV_RIM_CHOIRGLASS')
    # Undervault entry
    loc = 'LOC_UV_ENTRY_05'
    simple_level(loc, 'Undervault entry', [('Well head', 'Exterior'), ('Winch house', 'Room'), ('Shaft descent (3 lifts)', 'Vertical'), ('Frozen Sumps landing', 'Reward')],
                 [0, 1, 2, 3], 'Vertical shaft to REG_U', dict(traversal='Winch lift in 3 stages (40 s each), ice-crusted ladders as a fallback; leads to the Frozen Sumps (REG_U, Undervault thread)',
                                                              music='MUS_RIM_EXPLORE_NIGHT then MUS_UND_*', time_first_min=6, time_repeat_min=2, gate=LB[loc].get('gate', '')))
    # Landmarks
    for loc in sorted(l for l in LB if LB[l]['kind'] == 'Landmark'):
        lm = LMK.get(loc, {})
        simple_level(loc, 'Landmark', [('Approach', 'Exterior'), ('Base', 'Exterior'), ('Top or vista', 'Reward')], [0, 1, 2],
                     'Landmark, %s m tall, seen from %s km' % (lm.get('height_m', ''), lm.get('visible_km', '')),
                     dict(traversal='Climbable where a route is painted with old hull stencils; otherwise a vista point at the base', time_first_min=3, time_repeat_min=1))
    # Campaign quest spaces
    for loc in sorted(CQ_LOCS):
        near = LB.get(CQ_NEAR.get(loc, ''), {})
        r = rng(loc)
        x = int(near.get('x_m') or 2150) + r.randint(-180, 180)
        y = int(near.get('y_m') or 4000) + r.randint(-180, 180)
        LB.setdefault(loc, dict(loc_id=loc, kind='Quest space', name=loc.replace('LOC_CQ_REG_05_', '').replace('_', ' ').title(),
                                level=near.get('level', '50'), biome=near.get('biome', 'Frozen highlands'), grid=near.get('grid', ''), x_m=x, y_m=y, z_m=near.get('z_m', '')))
        simple_level(loc, 'Quest space', [('Approach', 'Exterior'), ('Scene', 'Room'), ('Aftermath', 'Reward')], [0, 1, 2],
                     'Quest space from campaign seeds; proposed within 180 m of %s' % (CQ_NEAR.get(loc) or 'region centre'), dict(time_first_min=6, time_repeat_min=2))
    # Public events (world thread)
    for loc in sorted(l for l in LB if LB[l]['kind'] == 'Public event'):
        rows = simple_level(loc, 'Public event', [('Event edge (300 m start radius)', 'Exterior'), ('Event ring', 'Exterior'), ('Spoils', 'Reward')], [0, 1, 2],
                            'Open event ring, 60 m', dict(traversal='Open; Strider and vehicles allowed', music='MUS_RIM_COMBAT_L2 on start; MUS_RIM_COMBAT_END on success',
                                                          puzzle=LB[loc].get('notes', ''), time_first_min=6, time_repeat_min=6), enc_nodes=[1])
        add_loot(loc, rows[2]['node_id'], 'ITM_LT_GEAR_REG_05', 1, 'Event chest (per player)', 'Spawns on success')
        add_cue(loc, rows[1]['node_id'], 'Event starts', 'Play_MUS_RIM_COMBAT_L2', 'VFX_ENV_EVENT_BEACON', 'Banner BAN_ public event; timer 5 min')


def points():
    host_of = {}
    for n in NODES:
        host_of.setdefault(n['level_id'], n['node_id'])
    for l in LOC:
        k = l['kind']
        if k not in ('Small chest', 'Shard crate', 'Gather node', 'Anchor', 'Lore site', 'Locked door', 'Patrol route'):
            continue
        r = rng(l['loc_id'])
        parent = l['parent_loc']
        contents, cue, vfx, note = '', '', '', ''
        if k == 'Small chest':
            contents, cue, note = 'ITM_LT_SMALLCHEST_REG_05', 'Play_SFX_World_Environment_ChestOpen', 'Open 1.2 s; mimics none in Rimefall (design choice)'
        elif k == 'Shard crate':
            contents, cue, vfx = 'ITM_LT_SHARDCRATE_REG_05', 'Play_SFX_World_Environment_ChestOpen', 'VFX_ENV_RIM_SHARDLAMP'
        elif k == 'Gather node':
            tag = l['tags']
            contents = {'glass_cluster': 'ITM_MAT_GLASS_01 x1-2', 'herb': 'ITM_MAT_HRB_%02d x1-3' % r.randint(1, 14), 'ore': 'ITM_MAT_HULL_02 x1-2',
                        'scrap': 'ITM_MAT_HULL_01 x2-4', 'shard_vein': 'ITM_MAT_DUST_01 x1-3'}.get(tag, 'ITM_MAT_DUST_01 x1') if tag else 'ITM_MAT_DUST_01 x1'
            cue, note = 'Play_SFX_World_Environment_ItemPickupByRarity', 'Respawns after 72 game hours (vendor restock rule)'
        elif k == 'Anchor':
            a = [x for x in ANCH if x['loc_id'] == l['loc_id']]
            contents = (a[0]['anchor_type'] if a else '') + '; fast travel ' + (a[0]['fast_travel'] if a else '')
            cue, vfx, note = 'Play_MUS_STG_ANCHOR_LIT; Play_MUS_STG_ANCHOR_REST', 'VFX_ANCHOR_LIGHT', 'Rest: refill Tonics, respawn normal enemies'
        elif k == 'Lore site':
            contents = ' '.join(x['item_id'] for x in LORE_BY.get(l['loc_id'], []))
            cue = 'Play_SFX_World_Environment_LoreItemPickup; Play_MUS_STG_LORE_STONE'
        elif k == 'Locked door':
            contents, cue = l['gate'], 'Play_SFX_World_Environment_DoorOpenCloseMetal'
            kid = l['gate'].split()[-1]
            src = [x['location'] for x in LORE if x['item_id'] == kid]
            note = 'Key found at ' + (src[0] if src else 'unknown')
        elif k == 'Patrol route':
            encs = ENC_BY.get(l['loc_id'], [])
            contents = ' '.join(e['enc_id'] for e in encs)
            for e in encs:
                enc_row(l['loc_id'], '', e)
            note = '150-300 m loop around ' + l['name'].split()[-1]
        POINTS.append(dict(loc_id=l['loc_id'], kind=k, name=l['name'], level=l['level'], grid=l['grid'], x_m=l['x_m'], y_m=l['y_m'], z_m=l['z_m'],
                           host_level=parent, contents=contents, audio=cue, vfx=vfx, notes=note))


def svg(loc, rows, title):
    n = len(rows)
    W_, H_ = 900, 140 + 90 * ((n + 5) // 6)
    pos = {}
    crit = [x for x in rows if x['critical_path'] == 'Y']
    br = [x for x in rows if x['critical_path'] != 'Y']
    for i, x in enumerate(crit):
        row, col = divmod(i, 6)
        if row % 2:
            col = 5 - col
        pos[x['node_id']] = (80 + col * 145, 90 + row * 120)
    for j, x in enumerate(br):
        pos[x['node_id']] = (80 + (j % 6) * 145, 90 + ((len(crit) + 5) // 6) * 120 + 30 + (j // 6) * 80)
    H_ = max(pos.values(), key=lambda p: p[1])[1] + 70
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif" font-size="11">' % (W_, H_),
           '<rect width="100%" height="100%" fill="#14181D"/>',
           '<text x="16" y="28" fill="#DCE6EE" font-size="15">%s</text>' % title.replace('&', 'and'),
           '<text x="16" y="48" fill="#8FA3B3">solid: critical path, dashed: branch, cyan: shortcut</text>']
    for x in rows:
        x1, y1 = pos[x['node_id']]
        for part in x['links'].split(' | '):
            if not part:
                continue
            tid, kind = part.split(' ', 1)
            if tid not in pos or 'back' in kind or 'locked' in kind:
                continue
            x2, y2 = pos[tid]
            col = '#8FE3EE' if 'shortcut' in kind else '#C8D2DA'
            dash = ' stroke-dasharray="5,4"' if 'branch' in kind else ''
            out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"%s/>' % (x1, y1, x2, y2, col, dash))
    for x in rows:
        cx, cy = pos[x['node_id']]
        fill = '#9B3A3A' if x['node_type'] == 'Boss arena' else '#2F6F8F' if x.get('anchor') else '#B48A4A' if x['node_type'] == 'Reward' else '#3A4450'
        out.append('<rect x="%d" y="%d" width="120" height="44" rx="6" fill="%s" stroke="#DCE6EE"/>' % (cx - 60, cy - 22, fill))
        nm = (x['name'][:16]).replace('&', 'and').replace('<', '')
        out.append('<text x="%d" y="%d" fill="#FFFFFF" text-anchor="middle">%s %s</text>' % (cx, cy - 4, x['node_id'][-2:], nm))
        tag = ('E:%d ' % len(x['encounters'].split()) if x.get('encounters') else '') + ('A ' if x.get('anchor') else '') + ('S' if x.get('secret') else '')
        out.append('<text x="%d" y="%d" fill="#9FD3E8" text-anchor="middle">%s</text>' % (cx, cy + 13, tag))
    out.append('</svg>')
    os.makedirs(os.path.join(OUT, 'maps'), exist_ok=True)
    open(os.path.join(OUT, 'maps', loc + '.svg'), 'w').write('\n'.join(out))


def sheet(lv):
    loc = lv['level_id']
    rows = [n for n in NODES if n['level_id'] == loc]
    encs = [e for e in ENCS if e['level_id'] == loc]
    loot = [l for l in LOOT if l['level_id'] == loc]
    cues = [c for c in CUES if c['level_id'] == loc]
    L = ['# %s (%s)' % (lv['name'], loc), '',
         '%s, level %s, %s, grid %s, position %s, %s m (height %s m).' % (lv['kind'], lv['level'], lv['biome'], lv['grid'], lv['x_m'], lv['y_m'], lv['z_m']), '']
    if lv.get('lore_alias'):
        L += ['Also called: %s.' % lv['lore_alias'], '']
    L += ['| Field | Value |', '| --- | --- |']
    for k in ('layout_type', 'critical_path', 'boss', 'anchors', 'shortcut', 'puzzle', 'traversal', 'mood', 'lighting', 'music', 'ambience', 'key_vfx',
              'enemies', 'unique_reward', 'collectibles', 'secrets', 'quest_hooks', 'time_first_min', 'time_repeat_min'):
        if str(lv.get(k, '')).strip():
            L.append('| %s | %s |' % (k.replace('_', ' '), str(lv[k]).replace('|', '/')))
    L += ['', '![node graph](../maps/%s.svg)' % loc, '', '## Nodes', '', '| Node | Name | Type | Floor | Elev m | Size | Links | Encounters | Anchor / secret / interactables |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for n in rows:
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (n['node_id'], n['name'], n['node_type'], n['floor'], n['elev_rel_m'], n.get('size_m', ''),
                                                                    n['links'].replace('|', ';'), n.get('encounters', ''),
                                                                    '; '.join(x for x in (n.get('anchor', ''), n.get('secret', ''), n.get('interactables', ''), n.get('notes', '')) if x).replace('|', '/')))
    if encs:
        L += ['', '## Encounters', '', '| Enc | Node | Template | Enemies | Trigger | Respawn |', '| --- | --- | --- | --- | --- | --- |']
        for e in encs:
            L.append('| %s | %s | %s | %s | %s | %s |' % (e['enc_id'], e['node_id'], e['template'], e['actors'], e['trigger'], e['respawn']))
    if loot:
        L += ['', '## Loot', '', '| Node | Item | Qty | Container | How it reads |', '| --- | --- | --- | --- | --- |']
        for l in loot:
            L.append('| %s | %s | %s | %s | %s |' % (l['node_id'], l['item'], l['qty'], l['container'], l['visibility']))
    if cues:
        L += ['', '## Audio and VFX cues', '', '| Node | Trigger | Audio | VFX | Notes |', '| --- | --- | --- | --- | --- |']
        for c in cues:
            L.append('| %s | %s | %s | %s | %s |' % (c['node_id'], c['trigger'], c['audio_event'], c['vfx_hook'], c['notes']))
    os.makedirs(os.path.join(OUT, 'sheets'), exist_ok=True)
    open(os.path.join(OUT, 'sheets', loc + '.md'), 'w').write('\n'.join(L) + '\n')


STYLE_BEATS = {
    'Vertical climb': 'A climb with the enemy above you. Artillery fires down the switchbacks, so each landing has a high wall to break line of sight and recharge Ward. Melee players push up the stair; gun players hold landings and pick off lancers on the parapets.',
    'Gun gallery (40-80 m sightlines)': 'A long gallery built for rifles: cover every 8-12 m, two side alcoves that flank the gun nest for melee builds, and a winch room at the end that opens the shortcut.',
    'Boss approach': 'A quiet stretch before a boss. Snow falls through the broken roof, the music thins out, and the last fight is a small one so the player arrives with Tonics left.',
    'Mixed': 'Mixed spaces: tight chapels for melee, one long relic hall for guns, and a bridge mechanism that sets up the big loop later.',
}


def docs():
    lv = {l['level_id']: l for l in LEVELS}
    zones = sorted(CITZ.values(), key=lambda z: int(z['order']))
    T = ['# Saint Drive Abbey: Citadel walkthrough (LOC_CIT_REG_05)', '',
         'Generated by tools/gen_levels.py from design/world/citadel_zones.csv and boss_arenas.csv. Zone order, names and anchors come from the world thread; the beats, node graphs, loot and cues are this thread\'s design choices. Per-zone detail is in sheets/LOC_CIT_REG_05_Z*.md; the whole flow is maps/LOC_CIT_REG_05.svg.', '',
         'Names follow design/world/locations.csv (project rule: the world table wins on location names and IDs; the campaign thread is renaming to match). Campaign seed places that point at the Abbey are mapped onto its zones.', '',
         '## Shape', '',
         'The Abbey climbs from %s m to %s m over 8 zones (level %s). Plan 5.2 asks for a 2 to 3 hour first play and every shortcut found by at least 60%% of testers. First-play path time here is %s minutes of zone time plus fights and deaths; budget 150 minutes median. A repeat run through opened shortcuts is about %s minutes.' % (
             LB[zones[0]['loc_id']]['z_m'], LB[zones[-1]['loc_id']]['z_m'], LB['LOC_CIT_REG_05']['level'], lv['LOC_CIT_REG_05']['time_first_min'], lv['LOC_CIT_REG_05']['time_repeat_min']), '',
         '| Zone | Name | Level | Style | Anchor | Shortcut back | Locked side door | Boss | First-play min |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for z in zones:
        T.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (z['order'], z['name'], z['level'], z['style'], z['anchor'] or 'none', z['shortcut'],
                                                              (z['locked_door'] + ' (' + LB.get(z['locked_door'], {}).get('gate', '') + ')') if z['locked_door'] else '', z['boss'], z['path_min']))
    T += ['', 'Locked doors in the Abbey guard side rooms only, never the critical path. Their keys are found in the region\'s sites and vaults (points.csv lists where), so a player who explored first gets extra loot and a safer route.', '', '## Zone by zone', '']
    for z in zones:
        loc = z['loc_id']
        l = lv[loc]
        T += ['### %s. %s (level %s)' % (z['order'], z['name'], z['level']), '']
        if z['boss'] == 'ACT_BOSS_RIME':
            b, a = BOSS[z['boss']], ARENA[loc]
            T.append('The pod hall comes first: villagers from Rimehold frozen in ice pods along both walls, the reason for MQ_A2_04. Before the fog gate the player chooses to thaw the pods or leave them. Thawing saves them but adds two waves of frozen Hollowed to the fight (LENC_05_RIME_W1 at 65%%, LENC_05_RIME_W2 at 30%%, each ACT_VAR_R5_01 x6 and ACT_HOLLOWED_HEAVY x1, spawning from the pod alcoves). Mother Rime (%s HP solo, Frost Ward %s, weak to Ember) fights in a %s m %s; %s. Phases at %s%% HP. Kill drops %s and grants %s, then the seat elevator returns the player to the Abbey gate.' % (
                b['HP (solo)'], b['Ward'], a['diameter_m'], a['shape'].lower(), a['condition'].lower(), b['Phase HP thresholds %'], b['Drops (item refs)'], b['Resonance unlocked']))
        elif z['boss']:
            b, a = BOSS[z['boss']], ARENA[loc]
            T.append('%s waits past a short antechamber with the Anchor %s m from the fog gate. %s HP solo, %s Ward %s, weak point: %s. Arena: %s m %s; %s. Phases at %s%% HP. Drops %s. Killing her completes MQ_A2_04C and opens the lift back to the Abbey gate.' % (
                b['Boss'], a['anchor_run_m'], b['HP (solo)'], b['Ward element'], b['Ward'], b['Weak points / parts'], a['diameter_m'], a['shape'].lower(), a['condition'].lower(), b['Phase HP thresholds %'], b['Drops (item refs)']))
        else:
            T.append(STYLE_BEATS.get(z['style'], STYLE_BEATS['Mixed']))
        T += ['', 'Critical path: %s.' % l['critical_path'], '', 'Enemies: %s.' % (l['enemies'] or 'none'), '']
        if l['quest_hooks']:
            T += ['Quest steps here: %s.' % l['quest_hooks'].replace(' | ', '; '), '']
    T += ['## Tests', '', '- Blind test with 10 players (plan 5.2); each shortcut must be found by 6 of 10.', '- Median first play 120 to 180 minutes; any zone over 25 minutes median gets an extra Anchor or a shorter path.',
          '- Both bosses: 20 testers, median first kill 3 to 12 attempts for Mother Rime (plan 5.4).']
    open(os.path.join(OUT, '02-citadel.md'), 'w').write('\n'.join(T) + '\n')

    # region flow
    order = sorted([l for l in LEVELS if l['kind'] in ('Town', 'Site', 'Choir vault', 'Field boss', 'Relay Tower', 'Choir site', 'Undervault entry', 'Citadel')],
                   key=lambda l: (lvl_of(l), l['level_id']))
    CORE = ('Citadel', 'Town', 'Site', 'Choir vault', 'Field boss', 'Relay Tower', 'Choir site', 'Undervault entry')
    tot = lambda k: sum(int(l['time_first_min'] or 0) for l in LEVELS if l['kind'] in k)
    R = ['# Rimefall level flow (REG_05)', '',
         'Generated by tools/gen_levels.py. Region facts come from design/world/regions_layout.csv: level %s to %s, %s km2, %s; weather: %s; enemy mix: %s; vehicles: %s.' % (
             LAY['level_min'], LAY['level_max'], LAY['area_km2'], LAY['biomes'], LAY['weather'], LAY['factions'], LAY['vehicles']), '',
         '## Ways in and out', '']
    for c in CONS:
        R.append('- %s: %s to %s by %s at %s (%s, %s m). Gate: %s.' % (c['con_id'], c['from_reg'], c['to_reg'], c['type'], c['loc_id'], c['x_m'], c['y_m'], c['gate']))
    R += ['', '## Main path', '',
          '1. Arrive at the low (level 44) edge and reach Rimehold (LOC_TOWN_REG_05_01). MQ_A2_04 starts with the elder; Brother Odo can be recruited here.',
          '2. Climb the Rimefall Relay Tower (LOC_RELAY_REG_05) for the map and Ostra\'s MQ_RT_05 line.',
          '3. Optional but expected: sites, vaults and the two field bosses in rising level order (table below) to reach the Citadel at level 55.',
          '4. Saint Drive Abbey (02-citadel.md): Choir Mother Ysse (MQ_A2_04C), then Mother Rime and the Heart Shard choice (MQ_A2_04).', '',
          'Critical path time, first play: town %s min, relay %s min, Citadel %s min. Core content (Citadel, towns, sites, vaults, field bosses, Relay, Choir site, Undervault entry) is %s minutes of level time; with about 25%% for travel that is %.1f hours, inside the plan\'s 6 to 12 hours per region. Full completion including every POI, landmark, event and quest space is about %.1f hours.' % (
              lv['LOC_TOWN_REG_05_01']['time_first_min'], lv['LOC_RELAY_REG_05']['time_first_min'], lv['LOC_CIT_REG_05']['time_first_min'],
              tot(CORE), tot(CORE) * 1.25 / 60, sum(int(l['time_first_min'] or 0) for l in LEVELS if l['kind'] != 'Citadel zone') * 1.25 / 60), '',
          '## Suggested order by level', '', '| Level | Place | Kind | Grid | First-play min | Boss or reward |', '| --- | --- | --- | --- | --- | --- |']
    for l in order:
        R.append('| %s | [%s](sheets/%s.md) | %s | %s | %s | %s |' % (l['level'], l['name'], l['level_id'], l['kind'], l['grid'], l['time_first_min'], l['boss'] or l['unique_reward']))
    R += ['', '## Totals', '']
    cnt = Counter(l['kind'] for l in LEVELS)
    R += ['- Levels: %s.' % ', '.join('%s %d' % (k, v) for k, v in sorted(cnt.items())),
          '- Nodes %d, encounters %d (%d enemies), loot placements %d, audio and VFX cues %d, point objects %d (chests, crates, gather nodes, Anchors, lore sites, doors, patrols).' % (
              len(NODES), len(ENCS), sum(int(e['total']) for e in ENCS), len(LOOT), len(CUES), len(POINTS)),
          '- Collectibles in the region: %s.' % ', '.join('%s %d' % (k, v) for k, v in sorted(Counter(
              'Lore items' if i.startswith('ITM_LOR_') else 'Tonic upgrades' if i.startswith('ITM_CON_TNC') else 'Resonances' if i.startswith('RES_') else 'Shardborn' if i.startswith('ITM_SHB') else 'Ascendant Shards'
              for i in [x['item'] for x in LOOT] if i.startswith(('ITM_LOR_', 'ITM_CON_TNC', 'RES_', 'ITM_SHB_', 'ITM_MAT_SPC_ASCENDANT'))).items()))]
    open(os.path.join(OUT, '01-region-flow.md'), 'w').write('\n'.join(R) + '\n')



def requests_and_conflicts():
    vfx = sorted(set(v for c in CUES for v in c['vfx_hook'].split()) | set(v for n in NODES for v in n.get('vfx', '').split()) | set(v for l in LEVELS for v in str(l.get('key_vfx', '')).split()))
    vfx = [v for v in vfx if v.startswith('VFX_')]
    ppv = sorted(set(k[2] for k in KIT_INFO.values()) | {'PPV_REG_05_CITADEL'})
    Q = [
        ('DRQ_L05_01', 'data/assets/asset_hooks.csv (asset thread)', 'VFX hooks', ' '.join(vfx), 'Environment and level VFX used by Rimefall levels; none exist yet'),
        ('DRQ_L05_02', 'design/art/post_process_volumes.csv (art thread)', 'PPV volumes', ' '.join(p for p in ppv if p != 'PPV_REG_05'), 'Interior volumes per kit; lighting values are in levels.csv lighting column'),
        ('DRQ_L05_03', 'design/audio/event_map.csv (audio thread)', 'SFX events', 'Play_SFX_World_Environment_IceSlideLoop Play_SFX_World_Environment_IceCrack Play_SFX_World_Environment_CableClimb Play_SFX_World_Environment_BellRing Play_SFX_World_Environment_TonePillar Play_SFX_World_Environment_PodThaw Play_SFX_World_Environment_WinchGate', 'Interactions the Rimefall kits need (ice slides, cable climbs, bell and tone puzzles, pod thaw, winch gates)'),
        ('DRQ_L05_04', 'design/world/encounters.csv (world thread)', 'new rows', 'LENC_05_RIME_W1 and LENC_05_RIME_W2: ENT_HORDE, FAC_HOLLOWED, level 58, ACT_VAR_R5_01 x6; ACT_HOLLOWED_HEAVY x1, condition FLG pods thawed', 'MQ_A2_04 thaw choice adds 2 waves (03-main-story)'),
        ('DRQ_L05_05', 'design/world/locations.csv then data/world/locations.csv', 'new LOC_CQ rows', ' '.join(sorted(CQ_LOCS)), 'Quest spaces from campaign seeds with no position; proposed x/y in levels.csv (within 180 m of a named host)'),
        ('DRQ_L05_06', 'data/tools/link.py', 'import tables', 'design/levels/<region>/level_nodes.csv, level_loot.csv, level_encounters.csv, level_cues.csv as data/world/level_*.csv', 'Puts level design under the validator; registers prefixes ND_ (node), LP_ (loot placement), CUE_ (cue), LENC_ (level encounter)'),
        ('DRQ_L05_07', 'data/actors/status_effects.csv or a buffs table', 'new buff', 'BUF_WAYSHRINE_FROST: Frost resistance +10% for 600 s, from praying at a wayshrine POI', 'Wayshrine POIs need a reward; one buff per region element'),
        ('DRQ_L05_08', 'design/campaign seeds (campaign thread)', 'use existing IDs', '; '.join('%s = %s' % (k, v) for k, v in sorted(CQ_ALIAS.items())), 'Seeds name places that already exist; this thread already maps them'),
        ('DRQ_L05_09', 'design/campaign seeds (campaign thread)', 'Shardborn quest hosts', 'QST_SHB_W11 (ITM_SHB_W11) finale at LOC_DGN_REG_05_12 wreck; QST_SHB_A11 (ITM_SHB_A11) finale at LOC_VAULT_REG_05_02', 'data/world/quests.csv lists both in REG_05 with no location; proposed hosts fit the item themes'),
        ('DRQ_L05_10', 'data/items/loot_tables.csv', 'note only', 'Fixed gear placements in level_loot.csv use REG_05 Rare and Relic items once each (%d of %d)' % (len(used_gear), len(GEAR)), 'So the loot thread can exclude placed uniques from random pools if wanted'),
    ]
    with open(os.path.join(OUT, 'data-requests.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['req_id', 'target', 'field', 'value', 'reason'])
        w.writerows(Q)
    C = []
    for loc, s_ in SITES.items():
        if loc in LB and LB[loc]['name'] != s_['name']:
            C.append((loc, 'design/world/sites.csv vs locations.csv', 'name', '%s vs %s' % (s_['name'], LB[loc]['name']), 'World thread: one generator run should write both'))
    C += [
        ('design/world/*', 'world generator', 'stability', 'Names, positions, anchors and zone order changed between runs on 3 Oct', 'Seed the world generator; this thread rebuilds from live tables, so its sheets follow whatever the world writes last'),
    ]
    keys = Counter(LB[d]['gate'] for d in LB if LB[d]['kind'] == 'Locked door')
    for k, v in keys.items():
        if v > 1:
            C.append((k, 'design/world/locations.csv', 'locked doors', '%s opens %d doors' % (k, v), 'Fine if intended; otherwise give each door its own key'))
    with open(os.path.join(OUT, 'conflicts.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'where', 'field', 'conflict', 'suggestion'])
        w.writerows(C)

def main():
    for d in ('sheets', 'maps'):
        for f in glob.glob(os.path.join(OUT, d, '*')):
            os.remove(f)
    citadel()
    for loc in sorted(SITES):
        site_level(loc, 'Choir vault' if 'VAULT' in loc else 'Site')
    towns()
    field_bosses()
    special_levels()
    poi_levels()
    points()
    # refresh collectibles now that all loot exists
    for lv in LEVELS:
        lv['collectibles'] = ' '.join(sorted(set(l['item'] for l in LOOT if l['level_id'] == lv['level_id'] and
                                                 (l['item'].startswith(('ITM_LOR_', 'ITM_CON_TNC', 'RES_', 'ITM_SHB_', 'ITM_MAT_SPC_ASCENDANT'))))))
        lv['enemies'] = fmt_tally(tally_level(lv['level_id'])) if lv['kind'] != 'Citadel' else lv['enemies']
    LEVELS.sort(key=lambda x: (['Citadel', 'Citadel zone', 'Site', 'Choir vault', 'Town', 'Field boss', 'Relay Tower', 'Choir site', 'Undervault entry', 'Landmark', 'POI', 'Public event', 'Quest space'].index(x['kind']), x['level_id']))
    LCOLS = ['level_id', 'kind', 'name', 'lore_alias', 'level', 'biome', 'grid', 'x_m', 'y_m', 'z_m', 'layout_type', 'nodes', 'critical_path', 'branches',
             'encounters', 'enemies', 'boss', 'anchors', 'shortcut', 'puzzle', 'traversal', 'mood', 'lighting', 'music', 'ambience', 'key_vfx',
             'unique_reward', 'collectibles', 'secrets', 'quest_hooks', 'time_first_min', 'time_repeat_min']
    wr('levels.csv', LEVELS, LCOLS)
    wr('level_nodes.csv', NODES, ['node_id', 'level_id', 'order', 'name', 'node_type', 'floor', 'elev_rel_m', 'size_m', 'links', 'critical_path', 'encounters',
                                  'anchor', 'secret', 'interactables', 'sightline', 'cover', 'light', 'audio', 'vfx', 'notes'])
    wr('level_encounters.csv', ENCS, ['enc_id', 'level_id', 'node_id', 'template', 'faction', 'level', 'actors', 'total', 'trigger', 'cover', 'cover_points',
                                      'fallback_points', 'respawn', 'leader', 'sightline', 'music', 'notes'])
    wr('level_loot.csv', LOOT, ['loot_id', 'level_id', 'node_id', 'item', 'qty', 'container', 'visibility', 'condition'])
    wr('level_cues.csv', CUES, ['cue_id', 'level_id', 'node_id', 'trigger', 'audio_event', 'vfx_hook', 'notes'])
    wr('points.csv', POINTS, ['loc_id', 'kind', 'name', 'level', 'grid', 'x_m', 'y_m', 'z_m', 'host_level', 'contents', 'audio', 'vfx', 'notes'])
    for lv in LEVELS:
        if lv['kind'] != 'POI' or True:
            rows = SVGS.get(lv['level_id'])
            if rows:
                svg(lv['level_id'], rows, '%s (%s)' % (lv['name'], lv['level_id']))
            if lv['kind'] != 'Citadel':
                sheet(lv)
    docs()
    requests_and_conflicts()
    # whole-Citadel side view
    allr = [n for n in NODES if n['level_id'].startswith('LOC_CIT_REG_05_Z')]
    svg('LOC_CIT_REG_05', allr, 'Saint Drive Abbey, all zones')
    # checks
    ids = Counter(n['node_id'] for n in NODES)
    dup = [k for k, v in ids.items() if v > 1]
    nodeset = set(ids)
    bad_links = [n['node_id'] for n in NODES for p in n['links'].split(' | ') if p and p.split()[0] not in nodeset]
    placed = set(e['enc_id'] for e in ENCS)
    missing_enc = [e['enc_id'] for e in ENC if e['enc_id'] not in placed]
    lore_unplaced = [x['item_id'] for x in LORE if x['item_id'] not in set(l['item'] for l in LOOT) and not x['location'].startswith('LOC_SITE_REG_05_1') and x['location'] not in ('LOC_SITE_REG_05_19', 'LOC_SITE_REG_05_20')]
    print('levels', len(LEVELS), 'nodes', len(NODES), 'encounters', len(ENCS), 'loot', len(LOOT), 'cues', len(CUES), 'points', len(POINTS))
    print('dup nodes', dup[:5], 'bad links', bad_links[:5], 'world encounters not placed', missing_enc[:10], 'gear used', len(used_gear), '/', len(GEAR))
    print('kinds', Counter(l['kind'] for l in LEVELS))
    # every ITM_/ACT_/RES_ reference must exist in data/
    known = set()
    for f in glob.glob(os.path.join(D, '**', '*.csv'), recursive=True):
        with open(f, newline='', encoding='utf-8') as fh:
            known.update(r[0] for r in csv.reader(fh) if r)
    bad = set()
    for tbl in (LOOT, ENCS, POINTS, LEVELS):
        for row in tbl:
            for v in row.values():
                bad.update(t for t in re.findall(r'\b(?:ITM|ACT|RES)_[A-Z0-9_]+', str(v)) if t not in known)
    print('unknown data IDs', sorted(bad) or 'none')


if __name__ == '__main__':
    main()
