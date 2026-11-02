#!/usr/bin/env python3
"""Thornwood (REG_03) level design generator.

Reads the live world, campaign, audio, art and data tables and writes every
Thornwood level top to bottom: layout node graph, critical path, encounters,
loot, secrets, collectibles, Anchors, traversal, mood, lighting, audio/VFX cues
and time to complete. Re-run after the world thread changes its tables:

    python3 design/levels/thornwood/tools/gen_levels.py

Hand-authored content (Citadel rooms, towns, the Moot, POI templates) lives in
the dicts below. Never hand-edit the CSVs this writes.
"""
import csv, os, re, json, glob, math, random, collections

G = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
W = G + '/design/world'
D = G + '/data'
OUT = G + '/design/levels/thornwood'
REG = 'REG_03'

def rd(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))

def wr(name, rows, cols):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)

# ---------------------------------------------------------------- inputs
LOCS = [r for r in rd(W + '/locations.csv') if r['region'] == REG]
L = {r['loc_id']: r for r in LOCS}
ANCH = {r['loc_id']: r for r in rd(W + '/anchors.csv') if r['region'] == REG}
ENCS = [r for r in rd(W + '/encounters.csv') if r['region'] == REG]
SITES = {r['loc_id']: r for r in rd(W + '/sites.csv') if r['region'] == REG}
TMPL = {r['site_type']: r for r in rd(W + '/site_templates.csv')}
SECR = {r['loc_id']: r for r in rd(W + '/secrets.csv') if r['region'] == REG}
ARENA = {r['boss']: r for r in rd(W + '/boss_arenas.csv') if r['region'] == REG}
ZONES = [r for r in rd(W + '/citadel_zones.csv') if r['citadel'] == 'LOC_CIT_' + REG]
LMK = {r['loc_id']: r for r in rd(W + '/landmarks.csv') if r['region'] == REG}
LAYOUT = [r for r in rd(W + '/regions_layout.csv') if r['reg_id'] == REG][0]
BOSSES = {r['ACT_ID']: r for r in rd(D + '/actors/bosses.csv')}
ENEMIES = {r['ACT_ID'] for r in rd(D + '/actors/enemies.csv')}
CREAT = {r['ACT_ID'] for r in rd(D + '/actors/creatures.csv')}
NPCS = {r[list(r)[0]] for r in rd(D + '/world/npcs.csv')}
ITEMS = {r['item_id'] for r in rd(D + '/items/items_index.csv')}
LT = {r['table_id'] for r in rd(D + '/items/loot_tables.csv')}
LORE = collections.defaultdict(list)
for r in rd(D + '/items/lore_items.csv'):
    if r['region'] == REG:
        LORE[r['location']].append(r)
ITEMS |= {r['item_id'] for r in rd(D + '/items/lore_items.csv')}
MUS = {r['cue_id'] for r in rd(G + '/design/audio/music_cues.csv')}
AMB = {r['amb_id'] for r in rd(G + '/design/audio/ambience_layers.csv')}
EVT = {r['wwise_event'] for r in rd(G + '/design/audio/event_map.csv')}
LGT = {r['light_id'] for r in rd(G + '/design/art/lighting_tod.csv')}
PPV = {r['ppv_id'] for r in rd(G + '/design/art/post_process_volumes.csv')}

QUESTS = []
for f in glob.glob(G + '/design/campaign/seeds/*.json'):
    d = json.load(open(f))
    for q in (d if isinstance(d, list) else []):
        if isinstance(q, dict) and (q.get('region') == REG or str(q.get('id', '')).startswith('MQ_A2_02')):
            QUESTS.append(q)

def rnd(key):
    return random.Random('thn:' + key)

def num(v, d=0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return d

def dist(a, b):
    return math.hypot(num(a['x_m']) - num(b['x_m']), num(a['y_m']) - num(b['y_m']))

# ---------------------------------------------------------------- outputs
LEVELS, NODES, ENC_OUT, LOOT, CUES, REQ = [], [], [], [], [], []
REGION_TIME = {}
MOOT_GAP = [0]
LOC2LVL = {}
lenc_n = [0]

def req(target, field, value, reason):
    REQ.append(dict(req_id='LREQ_%02d' % (len(REQ) + 1), target=target, field=field, value=value, reason=reason))

# ---------------------------------------------------------------- shared vocab
MOOD = {
    'Redbark forest': 'Cathedral redbark trunks 40-60 m tall, light in shafts through pollen; warm, hushed, watched',
    'Reactor bog': 'Green-lit reactor water, rusted hull ribs in reeds, gas bubbles; humid and sick',
    'Bramble ravines': 'Thorn walls 6-20 m high, narrow sky, red sap on stone; tight and hostile',
}
KIT_LIGHT = {  # interior look; PPV_INTERIOR picks LGT_CAVE / LGT_WRECK / LGT_CITADEL (art README)
    'KIT_CAVE': 'LGT_CAVE', 'KIT_CATACOMB': 'LGT_CAVE', 'KIT_CHOIR_VAULT': 'LGT_CAVE',
    'KIT_REACTOR': 'LGT_WRECK', 'KIT_WRECK': 'LGT_WRECK', 'KIT_TOWER': 'LGT_REG_03_DAY',
    'KIT_FORT': 'LGT_REG_03_DAY',
}
KIT_ROOMS = {
    'KIT_CAVE': ['Drip gallery', 'Root chamber', 'Glowworm pool', 'Fungus shelf', 'Collapsed shaft',
                 'Bone pit', 'Narrow crawl', 'Underground stream', 'Sap falls', 'Echo hall'],
    'KIT_REACTOR': ['Valve gallery', 'Coolant channel', 'Pump room', 'Control room', 'Maintenance crawl',
                    'Turbine hall', 'Filter beds', 'Pipe nest', 'Coolant tank', 'Relay room'],
    'KIT_CATACOMB': ['Ossuary hall', 'Lever gauntlet', 'Flooded crypt', 'Root-split tombs', 'Bone stair',
                     'Reliquary', 'Collapsed nave', 'Sump pit', 'Coffin shelves', 'Brood tunnels'],
    'KIT_TOWER': ['Guard floor', 'Stair core', 'Archer gallery', 'Store room', 'Bell loft', 'Signal floor',
                  'Bunk floor', 'Map room'],
    'KIT_FORT': ['Gatehouse', 'Courtyard', 'Barracks', 'Armoury', 'Watch walk', 'Stockade pens', 'Mess hall'],
    'KIT_WRECK': ['Cargo deck', 'Flooded corridor', 'Crew quarters', 'Bulkhead lock', 'Engine room',
                  'Hull spine', 'Galley', 'Med bay', 'Hydro tray deck', 'Air lock'],
    'KIT_CHOIR_VAULT': ['Tone hall', 'Resonance gallery', 'Pillar chamber', 'Hymn stair', 'Glass choir'],
}
KIT_ENTRY = {'KIT_CAVE': 'Cave mouth', 'KIT_REACTOR': 'Intake hall', 'KIT_CATACOMB': 'Barrow door',
             'KIT_TOWER': 'Base yard', 'KIT_FORT': 'Outer palisade', 'KIT_WRECK': 'Hull breach',
             'KIT_CHOIR_VAULT': 'Glass door'}
KIT_END = {'KIT_CAVE': "Keeper's den", 'KIT_REACTOR': 'Core chamber', 'KIT_CATACOMB': 'Deep crypt',
           'KIT_TOWER': 'Top chamber', 'KIT_FORT': "Warchief's keep", 'KIT_WRECK': "Captain's cabin",
           'KIT_CHOIR_VAULT': 'Inner sanctum'}
KIT_DEPTH = {'KIT_TOWER': 9, 'KIT_FORT': 4}  # metres per floor, upward; others go down 7 m
TRAPS = {'Redbark forest': 'Thorn snare (Root 3 s, 40 dmg)', 'Reactor bog': 'Bog gas pocket (Bloom DoT 12/s, ignites with Ember)',
         'Bramble ravines': 'Spore pod (blinds 2 s, Root 2 s)'}
TRIGGER = {'ENT_AMBUSH': '12 m trigger volume', 'ENT_PATROL': 'Patrol loop 150-300 m; sight 35 m',
           'ENT_CAMP': 'Sight 35 m or noise; leader horn calls camp', 'ENT_FORT': 'Line of sight 60 m',
           'ENT_GUNLINE': 'Line of sight 80 m', 'ENT_HORDE': 'Proximity 20 m; leader screams',
           'ENT_ELITE': 'Proximity 15 m', 'ENT_KEEPER': 'Enter room', 'ENT_CRT_PACK': 'Proximity 25 m',
           'ENT_CRT_SOLO': 'Proximity 30 m (territorial)', 'ENT_BOSS': 'Cross fog gate',
           'ENT_FIELDBOSS': 'Enter ground; leash 1.5x diameter', 'ENT_EVENT': 'Player within 300 m; repeats 10-15 min'}
SECRET_REWARD = {
    'Region loot table chest': ('ITM_LT_SMALLCHEST_' + REG, 1),
    'Unique site reward pool': ('ITM_LT_GEAR_' + REG, 1),
    'Lore item and Shard Dust x5': ('ITM_MAT_DUST_01', 5),
    'Seals: none (campaign)': ('ITM_LT_TIERMAT_' + REG, 2),
}
SFX = dict(anchor='Play_SFX_Player_Kindled_AnchorLight', chest='Play_SFX_World_Environment_ChestOpen',
           lore='Play_SFX_World_Environment_LoreItemPickup', shortcut='Play_SFX_World_Environment_ShortcutUnlock',
           lift='Play_SFX_World_Environment_LiftStartLoopStop', lever='Play_SFX_World_Environment_Lever',
           door='Play_SFX_World_Environment_DoorOpenCloseWood', hatch='Play_SFX_World_Environment_ShipHatch',
           illusory='Play_SFX_World_Environment_IllusoryWallVanish', breakable='Play_SFX_World_Environment_BreakableWall',
           trap='Play_SFX_World_Environment_Traps5TypesTrigger', steam='Play_SFX_World_Environment_SteamVent',
           relay='Play_SFX_World_Environment_RelayTowerActivate', hum='Play_SFX_World_Environment_ShardHumLoop',
           water='Play_SFX_World_Environment_WaterStreamRiverWaterfall', pickup='Play_SFX_World_Environment_ItemPickupByRarity',
           fire='Play_SFX_World_Environment_FireLoopSmallLarge', terminal='Play_SFX_World_Environment_TerminalBeep',
           foggate='Play_SFX_World_Environment_FogGateEnter', choirtone='Play_SFX_World_Environment_ChoirTonePillar',
           resgate='Play_SFX_World_Environment_ResonanceGateOpen', winch='Play_SFX_World_Environment_GateWinch',
           bridge='Play_SFX_World_Environment_BridgeLower', rootgrow='Play_SFX_World_Environment_RootGrowth',
           valve='Play_SFX_World_Environment_CoolantValve', kick='Play_SFX_World_Environment_KickLadder',
           rope='Play_SFX_World_Environment_RopeDrop', cave='Play_SFX_Ambience_R3Thornwood_InteriorCave',
           citamb='Play_SFX_Ambience_R3Thornwood_Citadel', walla='Play_SFX_Ambience_R3Thornwood_TownWallaCrowd',
           wild='Play_SFX_Ambience_R3Thornwood_WildlifeOneShots', emit='Play_SFX_Ambience_R3Thornwood_RegionSpecificEmittersWindInWreckBellsMachinery')
VFX = {  # proposed environment VFX ids (art/VFX owner adds them; see vfx_env.csv)
    'VFX_ENV_ANCHOR_IDLE': 'Anchor ember flicker, 2 m radius, warm amber',
    'VFX_ENV_ANCHOR_LIGHT': 'Anchor ignition burst, 1.2 s, pillar of Shard light 8 m',
    'VFX_ENV_FOGGATE': 'Boss fog wall, 4 m wide, Bloom-green mist with thorn silhouettes',
    'VFX_ENV_SHORTCUT_OPEN': 'Dust and leaf fall burst when a shortcut opens',
    'VFX_ENV_POLLEN_DRIFT': 'Screen-space-free pollen motes, density by Weather state',
    'VFX_ENV_BOG_GAS': 'Green gas pocket, 4 m sphere, ignites with Ember to a 6 m fireball',
    'VFX_ENV_SPORE_POD': 'Spore pod burst, 3 m cone, yellow',
    'VFX_ENV_THORN_SNARE': 'Thorn snare whip-up, roots wrap the legs',
    'VFX_ENV_COOLANT_STEAM': 'Coolant steam jet from valves and vents, 3-6 m',
    'VFX_ENV_REACTOR_GLOW': 'Pulsing green reactor light in water, 0.5 Hz',
    'VFX_ENV_ILLUSORY_DISSOLVE': 'Illusory wall burns away in Shard light, 1.5 s',
    'VFX_ENV_LORE_GLINT': 'Soft white glint on lore items, visible 8 m',
    'VFX_ENV_CHEST_GLINT': 'Chest glint tinted by best rarity inside, visible 12 m',
    'VFX_ENV_RELAY_BEAM': 'Relay Tower map-reveal beam, 80 m column and sweep',
    'VFX_ENV_CHOIR_TONE': 'Tone pillar ring ripple, colour per note',
    'VFX_ENV_ROOT_GROWTH': 'Roots erupt into cover pieces (Sorrel arena), 2 s grow',
    'VFX_ENV_FIREFLY': 'Fireflies at dusk and night near water, 30 per emitter',
    'VFX_ENV_SAP_DRIP': 'Red sap drips and pools on stone',
    'VFX_ENV_LEAF_FALL': 'Falling redbark leaves, wind-driven',
    'VFX_ENV_SHARD_GLOW': 'Shard vein glow and floating motes',
    'VFX_ENV_BRAZIER': 'Clan brazier fire and embers',
    'VFX_ENV_WATER_MIST': 'Waterfall and sluice mist',
}

def cue(lvl, node, kind, cid, trigger):
    CUES.append(dict(lvl_id=lvl, node_id=node, cue_type=kind, cue_id=cid, trigger=trigger))

def add_level(**k):
    base = dict(region=REG)
    base.update(k)
    LEVELS.append(base)
    if k.get('loc_id'):
        LOC2LVL[k['loc_id']] = k['lvl_id']
    return base

def add_node(lvl, nid, **k):
    r = dict(lvl_id=lvl, node_id=nid)
    r.update(k)
    NODES.append(r)
    return r

def actors_str(acts):
    return '; '.join('%s x%d' % (a, n) for a, n in acts)

def parse_actors(s):
    out = []
    for part in s.split(';'):
        m = re.match(r'\s*(\S+)\s+x(\d+)', part)
        if m:
            out.append((m.group(1), int(m.group(2))))
    return out

def add_enc(lvl, node, template, faction, level, acts, src='', respawn='On Anchor rest', cover='', fallback='', cond='', note=''):
    lenc_n[0] += 1
    if faction == 'FAC_THORN' and not cond:
        cond = 'FLG_THORN_PEACE: Neutral (no aggro); Moot broken (CMPQ_C7_05): count x0.5'
    r = dict(lenc_id='LENC_THN_%04d' % lenc_n[0], lvl_id=lvl, node_id=node, src_enc=src, template=template,
             faction=faction, level=level, actors=actors_str(acts), enemy_count=sum(n for _, n in acts),
             trigger=TRIGGER.get(template, ''), cover_points=cover, fallback_points=fallback, respawn=respawn,
             condition=cond, notes=note)
    ENC_OUT.append(r)
    return r

def world_enc(lvl, node, e, note=''):
    return add_enc(lvl, node, e['template'], e['faction'], e['level'], parse_actors(e['actors']), src=e['enc_id'],
                   respawn=e['respawn'], cover=e['cover_points'], fallback=e['fallback_points'], cond=e.get('condition', ''), note=note)

def loot(lvl, node, container, ref, qty=1, placement='Side', cond='', note=''):
    LOOT.append(dict(loot_id='LOOT_THN_%04d' % (len(LOOT) + 1), lvl_id=lvl, node_id=node, container=container,
                     item_ref=ref, qty=qty, placement=placement, condition=cond, notes=note))

def boss_drops(lvl, node, boss):
    for part in BOSSES[boss]['Drops (item refs)'].split(';'):
        m = re.match(r'\s*(\S+)(?:\s+x(\d+))?', part)
        if m:
            loot(lvl, node, 'Boss drop', m.group(1), int(m.group(2) or 1), 'Boss', 'First kill' if 'SHB' in m.group(1) else '')
    res = BOSSES[boss].get('Resonance unlocked', '')
    if res:
        loot(lvl, node, 'Resonance grant', res, 1, 'Boss', 'First kill')

ENC_BY_LOC = collections.defaultdict(list)
for e in ENCS:
    ENC_BY_LOC[e['loc_id']].append(e)
CHILD = collections.defaultdict(list)
for r in LOCS:
    if r['parent_loc']:
        CHILD[r['parent_loc']].append(r)
ANCH_BY_PARENT = collections.defaultdict(list)
for a in ANCH.values():
    ANCH_BY_PARENT[a['parent_loc']].append(a['loc_id'])

def secret_reward(sec_loc):
    s = SECR.get(sec_loc, {})
    rw = s.get('reward', '')
    m = re.match(r'(ITM_[A-Z0-9_]+)(?:\s+x(\d+))?', rw)
    if m:
        return m.group(1), int(m.group(2) or 1)
    m = re.search(r'\((ITM_[A-Z0-9_]+)\)', rw)
    if m:
        return m.group(1), 1
    return SECRET_REWARD.get(rw, ('ITM_LT_SMALLCHEST_' + REG, 1))

def place_secret(lvl, node, sec):
    s = SECR.get(sec['loc_id'], {})
    ref, q = secret_reward(sec['loc_id'])
    loot(lvl, node, 'Secret: ' + s.get('secret_type', sec['name']), ref, q, 'Hidden',
         s.get('requirement', ''), s.get('hint', ''))
    if 'Lore item' in s.get('reward', ''):
        loot(lvl, node, 'Secret: lore', 'ITM_LT_TIERMAT_' + REG, 1, 'Hidden', '', 'Lore text requested (LREQ)')
    st = s.get('secret_type', '')
    cue(lvl, node, 'SFX', SFX['illusory'] if 'Illusory' in st else SFX['breakable'] if 'Breakable' in st else SFX['resgate'] if 'Resonance' in st else SFX['chest'], 'Secret revealed')
    cue(lvl, node, 'MUSIC', 'MUS_STG_SECRET', 'Secret revealed')
    if 'Illusory' in st:
        cue(lvl, node, 'VFX', 'VFX_ENV_ILLUSORY_DISSOLVE', 'Wall hit')
    return s.get('secret_type', '')

# ================================================================ SITES
TIME_W = dict(entry=0.6, combat=1.4, trap=0.9, puzzle=1.8, elite=1.6, keeper=2.2, boss=3.0, shortcut=0.3)
SIZE = dict(entry=(14, 12), combat=(24, 18), trap=(5, 30), puzzle=(20, 18), elite=(22, 20), keeper=(28, 24),
            side=(9, 8), shortcut=(4, 10))

def gen_site(loc_id):
    s = SITES[loc_id]
    loc = L[loc_id]
    kit = s['template']
    lvl = 'LVL_THN_' + loc_id.split('_', 1)[1]
    r = rnd(loc_id)
    n_rooms = int(s['rooms'])
    floors = max(1, int(s['floors']))
    path_min = num(s['path_min'])
    biome = loc['biome']
    boss = re.search(r'(ACT_BOSS_\w+)', s['end'])
    boss = boss.group(1) if boss else ''
    encs = ENC_BY_LOC.get(loc_id, [])
    keeper = [e for e in encs if e['template'] == 'ENT_KEEPER']
    elites = [e for e in encs if e['template'] == 'ENT_ELITE']
    others = [e for e in encs if e['template'] not in ('ENT_KEEPER', 'ENT_ELITE')]
    puzzle = s['puzzle']
    # critical path roles
    crit_n = max(4, round(n_rooms * 0.7))
    side_n = n_rooms - crit_n
    roles = ['entry']
    mid = crit_n - 2
    body = ['combat'] * mid
    if puzzle and mid >= 2:
        body[mid // 2] = 'puzzle'
    if elites and mid >= 3:
        body[-1] = 'elite'
    combat_slots = [i for i, x in enumerate(body) if x == 'combat']
    for i in combat_slots[len(others):]:
        body[i] = 'trap'
    roles += body + ['boss' if boss else 'keeper']
    names = list(KIT_ROOMS[kit])
    r.shuffle(names)
    nodes = []
    approach = add_node(lvl, lvl + '_N00', seq=0, name='Approach', room_type='Exterior', role='approach', crit='Y',
                        floor=0, elev_m=0, gx=0, gy=0, w_m=30, d_m=20)
    nodes.append(approach)
    depth = KIT_DEPTH.get(kit, -7)
    for i, role in enumerate(roles):
        fl = min(floors - 1, i * floors // len(roles))
        nm = KIT_ENTRY[kit] if role == 'entry' else KIT_END[kit] if role in ('keeper', 'boss') else names.pop() if names else 'Passage %d' % i
        w, d = SIZE[role] if role in SIZE else SIZE['combat']
        if role == 'boss':
            w = d = int(num(ARENA.get(boss, {}).get('diameter_m'), 34))
        n = add_node(lvl, '%s_N%02d' % (lvl, i + 1), seq=i + 1, name=nm, room_type=role.capitalize(), role=role, crit='Y',
                     floor=fl + 1, elev_m=(fl + (1 if role != 'entry' else 0)) * depth if role != 'entry' else 0,
                     gx=i + 1, gy=fl * 2, w_m=w + r.randint(-2, 4), d_m=d + r.randint(-2, 3))
        nodes.append(n)
    sc = add_node(lvl, lvl + '_N%02d' % (len(roles) + 1), seq=len(roles) + 1, name='Shortcut: ' + s['shortcut'],
                  room_type='Shortcut', role='shortcut', crit='Y', floor=0, elev_m=0, gx=len(roles) + 1, gy=0, w_m=4, d_m=10)
    nodes.append(sc)
    # side rooms
    hosts = [n for n in nodes if n['role'] in ('combat', 'trap', 'puzzle', 'elite')] or nodes[1:-1]
    side_types = ['Loot', 'Lore', 'Loot', 'Lore']
    sides = []
    for j in range(side_n):
        h = hosts[j % len(hosts)]
        nm = names.pop() if names else 'Side room %d' % (j + 1)
        sn = add_node(lvl, '%s_S%02d' % (lvl, j + 1), seq='', name=nm, room_type=side_types[j % 4] + ' side room',
                      role='side', crit='N', floor=h['floor'], elev_m=h['elev_m'], gx=h['gx'], gy=h['gy'] + 1,
                      w_m=SIZE['side'][0] + r.randint(0, 6), d_m=SIZE['side'][1] + r.randint(0, 6))
        sn['exits'] = h['node_id'] + ' (walk)'
        sides.append(sn)
    # exits on crit path
    crit = nodes
    for a, b in zip(crit, crit[1:]):
        a.setdefault('exits', '')
        a['exits'] = '; '.join(x for x in [a['exits'], b['node_id'] + ' (walk)'] if x)
    form = s['shortcut']
    sc['exits'] = nodes[1]['node_id'] + ' (shortcut: ' + form.replace(';', ',') + ', opens from this side only)'
    for sn in sides:
        h = [n for n in nodes if n['node_id'] == sn['exits'].split()[0]][0]
        h['exits'] = h['exits'] + '; ' + sn['node_id'] + ' (walk)'
    # time
    wsum = sum(TIME_W.get(n['role'], 1) for n in nodes[1:])
    for n in nodes[1:]:
        n['crit_s'] = round(path_min * 60 * TIME_W.get(n['role'], 1) / wsum)
    approach['crit_s'] = 0
    for sn in sides:
        sn['crit_s'] = 0
        sn['side_s'] = 70
    # anchors
    ent_anc = s['entrance_anchor'] or ''
    by_parent = ANCH_BY_PARENT.get(loc_id, [])
    if ent_anc and ent_anc not in ANCH:
        ent_anc = ''
    if not ent_anc and by_parent:
        ent_anc = by_parent[0]
    approach['anchor'] = ent_anc
    int_anc = s['interior_anchor'] or (by_parent[1] if len(by_parent) > 1 else '')
    end = nodes[-2]
    if boss:
        prev = nodes[-3]
        prev['anchor'] = int_anc or ''
        prev['notes'] = 'Boss antechamber; fog gate (MET_FOGGATE 4 m) on the far wall; Anchor %s %s m from the gate' % (
            int_anc or '(entrance Anchor via shortcut)', ARENA.get(boss, {}).get('anchor_run_m', '30'))
    elif int_anc:
        nodes[len(nodes) // 2]['anchor'] = int_anc
    # encounters
    lvl_level = s['level']
    ci = iter([n for n in nodes if n['role'] == 'combat'])
    for e in others:
        tgt = next(ci, None) or (sides[0] if sides else nodes[1])
        world_enc(lvl, tgt['node_id'], e)
        tgt['encounter'] = 'Y'
    for e in elites:
        tgt = next((n for n in nodes if n['role'] == 'elite'), nodes[len(nodes) // 2])
        world_enc(lvl, tgt['node_id'], e)
    for e in keeper:
        world_enc(lvl, end['node_id'], e, note='Named site keeper: ' + loc['name'] + ' Keeper')
    if boss:
        a = ARENA.get(boss, {})
        add_enc(lvl, end['node_id'], 'ENT_BOSS', 'Boss', BOSSES[boss]['Level'], [(boss, 1)], respawn='Never',
                note='%s; %s; arena %s m %s; %s' % (BOSSES[boss]['Boss'], a.get('arena_hooks', ''), a.get('diameter_m', ''),
                                                     a.get('shape', ''), a.get('condition', '')))
    if not keeper and not boss:
        add_enc(lvl, end['node_id'], 'ENT_KEEPER', 'FAC_THORN', lvl_level, [('ACT_THORN_HEAVY', 1), ('ACT_THORN_LEADER', 1), ('ACT_VAR_R3_03', 2)],
                respawn='Never (unique per site)', note='Design choice: no keeper in world data, keeper added per site rule')
    for n in nodes:
        if n['role'] == 'trap':
            n['notes'] = (n.get('notes', '') + ' Trap run: ' + TRAPS.get(biome, 'Thorn snare')).strip()
    # traversal
    trav = []
    for i, n in enumerate(nodes[1:-1], 1):
        prev = nodes[i - 1]
        dz = num(n['elev_m']) - num(prev['elev_m'])
        if dz <= -6:
            n['traversal'] = 'Drop %d m (safe under 6 m: ledge steps)' % -dz if dz > -6 else 'Ladder down %d m' % -dz
        elif dz >= 6:
            n['traversal'] = 'Ladder or stair up %d m' % dz
        elif n['role'] == 'trap':
            n['traversal'] = 'Corridor 4-5 m wide (MET_CORRIDOR_MELEE)'
        else:
            n['traversal'] = 'Walk'
    approach['traversal'] = 'Strider dismount here (no mounts inside sites)'
    sc['traversal'] = form
    # puzzle
    for n in nodes:
        if n['role'] == 'puzzle':
            n['notes'] = 'Puzzle: ' + puzzle
            loot(lvl, n['node_id'], 'Puzzle cache', 'ITM_LT_TIERMAT_' + REG, 1, 'Crit path')
            cue(lvl, n['node_id'], 'SFX', SFX['valve'] if 'valve' in puzzle.lower() else SFX['choirtone'] if 'tone' in puzzle.lower()
                else SFX['lever'] if 'Lever' in puzzle else SFX['steam'] if 'reactor' in puzzle.lower() else SFX['hum'], 'Puzzle step')
            if 'tone' in puzzle.lower():
                cue(lvl, n['node_id'], 'VFX', 'VFX_ENV_CHOIR_TONE', 'Pillar struck')
            if 'reactor' in puzzle.lower() or 'valve' in puzzle.lower() or 'Vent' in puzzle:
                cue(lvl, n['node_id'], 'VFX', 'VFX_ENV_COOLANT_STEAM', 'Puzzle step')
    # loot
    loot(lvl, end['node_id'], 'Reward chest' if not boss else 'Boss reward', s['unique_reward'], 1, 'End', '', 'Unique site reward (plan 3.7)')
    if boss:
        boss_drops(lvl, end['node_id'], boss)
    if kit == 'KIT_CHOIR_VAULT':
        loot(lvl, end['node_id'], 'Vault chest', 'ITM_LT_VAULT_' + REG, 1, 'End', 'GATE_04', 'Rarity floor Rare')
    lores = LORE.get(s['lore_site'], [])
    lore_nodes = [n for n in sides if 'Lore' in n['room_type']] or [end]
    for k, li in enumerate(lores):
        tgt = lore_nodes[k % len(lore_nodes)] if li['lore_type'] != 'Key' else end
        loot(lvl, tgt['node_id'], 'Lore item (' + li['lore_type'] + ')', li['item_id'], 1, 'Side' if tgt['crit'] == 'N' else 'End')
    if not lores:
        req('data/items/lore_items.csv', 'new row', 'Lore item for ' + loc_id, 'Plan 5.1: at least one lore item per site')
    for n in sides:
        if 'Loot' in n['room_type']:
            loot(lvl, n['node_id'], 'Small chest', 'ITM_LT_SMALLCHEST_' + REG, 1, 'Side')
    for c in CHILD.get(loc_id, []):
        if c['kind'] == 'Small chest':
            tgt = next((n for n in sides if 'Loot' in n['room_type']), r.choice(nodes[2:-2] or nodes))
            loot(lvl, tgt['node_id'], 'Small chest (' + c['loc_id'] + ')', 'ITM_LT_SMALLCHEST_' + REG, 1, 'Side' if tgt['crit'] == 'N' else 'Crit path')
        elif c['kind'] == 'Shard crate':
            loot(lvl, nodes[2]['node_id'], 'Shard crate (' + c['loc_id'] + ')', 'ITM_LT_SHARDCRATE_' + REG, 1, 'Crit path', '', 'Charged ammo')
    comb = [n for n in nodes if n['role'] == 'combat']
    if comb:
        loot(lvl, comb[0]['node_id'], 'Shard crate', 'ITM_LT_SHARDCRATE_' + REG, 1, 'Crit path', '', 'Charged ammo before the first fight')
    for n in nodes:
        if n['role'] == 'trap':
            loot(lvl, n['node_id'], 'Corpse', 'ITM_LT_CONSUMABLE', 1, 'Crit path', '', 'Previous victim of the trap')
    # secrets
    secs = [c for c in CHILD.get(loc_id, []) if c['kind'] == 'Secret'] + [L[k] for k, v in SECR.items() if v['host_loc'] == loc_id and L.get(k, {}).get('parent_loc') != loc_id and k in L]
    for k, sec in enumerate(secs):
        tgt = (sides or nodes[2:-2] or nodes)[k % max(1, len(sides or nodes[2:-2] or nodes))]
        tgt['secret'] = sec['loc_id']
        place_secret(lvl, tgt['node_id'], sec)
    # cues
    kitlight = KIT_LIGHT.get(kit, 'LGT_CAVE')
    cue(lvl, approach['node_id'], 'MUSIC', 'MUS_THN_DISCOVERY', 'First sight of entrance')
    cue(lvl, approach['node_id'], 'SFX', SFX['anchor'], 'Light Anchor')
    cue(lvl, approach['node_id'], 'VFX', 'VFX_ENV_ANCHOR_LIGHT', 'Light Anchor')
    cue(lvl, approach['node_id'], 'MUSIC', 'MUS_STG_ANCHOR_LIT', 'Light Anchor')
    cue(lvl, nodes[1]['node_id'], 'LIGHT', 'PPV_INTERIOR', 'Blend 4 m at the entrance; preset ' + kitlight)
    cue(lvl, nodes[1]['node_id'], 'MUSIC', 'MUS_THN_SITE', 'Enter')
    cue(lvl, nodes[1]['node_id'], 'AMB', 'AMB_THN_INTERIOR', 'Enter (room tone per kit)')
    if kit in ('KIT_CAVE', 'KIT_CATACOMB', 'KIT_CHOIR_VAULT'):
        cue(lvl, nodes[1]['node_id'], 'SFX', SFX['cave'], 'Enter')
    else:
        cue(lvl, nodes[1]['node_id'], 'SFX', SFX['emit'], 'Enter')
    for n in nodes:
        if n.get('encounter') == 'Y' or n['role'] == 'elite':
            cue(lvl, n['node_id'], 'MUSIC', 'MUS_THN_COMBAT_L2' if n['role'] == 'elite' else 'MUS_THN_COMBAT_L1', 'Aggro')
            cue(lvl, n['node_id'], 'MUSIC', 'MUS_THN_COMBAT_END', 'Last enemy dies')
        if n['role'] == 'trap':
            cue(lvl, n['node_id'], 'SFX', SFX['trap'], 'Trap trigger')
            cue(lvl, n['node_id'], 'VFX', 'VFX_ENV_BOG_GAS' if 'bog' in biome.lower() else 'VFX_ENV_SPORE_POD' if 'ravine' in biome.lower() else 'VFX_ENV_THORN_SNARE', 'Trap trigger')
        if n.get('anchor') and n is not approach:
            cue(lvl, n['node_id'], 'SFX', SFX['anchor'], 'Light Anchor')
            cue(lvl, n['node_id'], 'VFX', 'VFX_ENV_ANCHOR_IDLE', 'Always')
    if boss:
        b = boss.replace('ACT_BOSS_', '')
        cue(lvl, nodes[-3]['node_id'], 'VFX', 'VFX_ENV_FOGGATE', 'Always until boss dead')
        cue(lvl, nodes[-3]['node_id'], 'SFX', SFX['foggate'], 'Cross fog gate')
        cue(lvl, end['node_id'], 'LIGHT', 'PPV_BOSS', 'Fog gate entry')
        for ph in ['INTRO', 'P1', 'T2', 'P2', 'T3', 'P3', 'WIN']:
            if 'MUS_BOSS_%s_%s' % (b, ph) in MUS:
                cue(lvl, end['node_id'], 'MUSIC', 'MUS_BOSS_%s_%s' % (b, ph), ph)
    else:
        cue(lvl, end['node_id'], 'MUSIC', 'MUS_THN_COMBAT_L2', 'Keeper aggro')
    cue(lvl, end['node_id'], 'SFX', SFX['chest'], 'Open reward')
    cue(lvl, end['node_id'], 'VFX', 'VFX_ENV_CHEST_GLINT', 'Reward chest visible')
    sfx_sc = SFX['lift'] if 'Lift' in form else SFX['kick'] if 'ladder' in form else SFX['winch'] if 'winch' in form \
        else SFX['rope'] if 'Rope' in form else SFX['hatch'] if 'hatch' in form else SFX['door']
    cue(lvl, sc['node_id'], 'SFX', sfx_sc, 'Open shortcut')
    cue(lvl, sc['node_id'], 'SFX', SFX['shortcut'], 'Open shortcut')
    cue(lvl, sc['node_id'], 'VFX', 'VFX_ENV_SHORTCUT_OPEN', 'Open shortcut')
    for n in nodes + sides:
        n['light'] = 'LGT_REG_03_*' if n['role'] == 'approach' else kitlight
        n['music'] = 'MUS_THN_EXPLORE_DAY/NIGHT' if n['role'] == 'approach' else 'MUS_THN_SITE'
        n['ambience'] = 'AMB_THN_BED_DAY/NIGHT' if n['role'] == 'approach' else 'AMB_THN_INTERIOR'
        n['purpose'] = n.get('purpose') or {'approach': 'Arrival, Anchor, read the entrance', 'entry': 'Threshold; exposure shift; first sight of the site motif',
                                             'combat': 'Fight', 'trap': 'Hazard run; resource drain before the keeper', 'puzzle': 'Puzzle gate on the main path',
                                             'elite': 'Mid-site elite', 'keeper': 'Site keeper fight; reward', 'boss': 'Site boss; reward',
                                             'shortcut': 'Loop back to the entrance', 'side': 'Optional: loot, lore, secret'}[n['role']]
    nenc = [e for e in ENC_OUT if e['lvl_id'] == lvl]
    lv = add_level(lvl_id=lvl, loc_id=loc_id, name=loc['name'], story_name='', kind=s['site_type'] if kit != 'KIT_CHOIR_VAULT' else 'Choir vault',
                   kit=kit, biome=biome, grid=loc['grid'], x_m=loc['x_m'], y_m=loc['y_m'], z_m=loc['z_m'], level=s['level'],
                   layout='Node graph, %d rooms on %d floors; critical path %d rooms, %d side rooms' % (n_rooms, floors, crit_n, side_n),
                   cell_m=10, floors=floors, rooms=n_rooms, entry_anchor=ent_anc, anchors=' '.join(x for x in [ent_anc, int_anc] if x),
                   gate='GATE_04 Choir Seal Key or FAC_CHOIR Friendly' if kit == 'KIT_CHOIR_VAULT' else '',
                   boss=boss, crit_min=round(path_min), full_min=round(path_min + side_n * 1.2 + len(secs) * 1.5 + 2),
                   shortcut=form, mood=MOOD.get(biome, ''), light=kitlight + ' via PPV_INTERIOR', music='MUS_THN_SITE',
                   ambience='AMB_THN_INTERIOR', notes='')
    return lv

# ================================================================ CITADEL (hand-authored)
CIT = 'LVL_THN_CIT'
CIT_ROOMS = [
    # zone, id, name, role, w, d, elev, crit, purpose, traversal, extra
    ('Z1', 'C01', 'Logging Road Approach', 'approach', 20, 120, 0, 'Y', 'Arrival on the logging road; Engine stacks fill the sky; Anchor', 'Road, Strider dismount at the Anchor', ''),
    ('Z1', 'C02', 'Root Gate Barbican', 'combat', 60, 30, 6, 'Y', 'Gun gallery: 60 m sightline up the gate ramp, low cover every 10 m, flank ledge for melee', 'Ramp 20 m up 6 m', ''),
    ('Z1', 'C03', 'Thornwall Breach', 'combat', 26, 22, 10, 'Y', 'Horde pours through a burst thorn wall; burnable brambles (Ember) open a flank', 'Walk', ''),
    ('Z1', 'C04', 'Gate Yard', 'combat', 40, 36, 14, 'Y', 'Fortified line on the inner wall; hull-plate barricades', 'Stair 4 m', ''),
    ('Z1', 'C05', 'Collapsed Guardhouse', 'side', 12, 10, 14, 'N', 'Optional loot under a fallen root', 'Crawl 1.4 m (non-combat squeeze)', ''),
    ('Z2', 'C06', 'Market Arcade', 'combat', 70, 18, 18, 'Y', 'Gun line down a covered arcade; stalls are low cover', 'Walk', ''),
    ('Z2', 'C07', 'Seed Stalls', 'combat', 30, 30, 22, 'Y', 'Horde in a square of rotten seed stalls; leader on a balcony', 'Walk', ''),
    ('Z2', 'C08', 'Barbican Winch', 'shortcut', 10, 10, 28, 'Y', 'Winch lifts the barbican gate: shortcut back to the Z1 Anchor', 'Gate winch (opens from inside)', 'Barbican winch gate opens back to Z1 Anchor'),
    ('Z2', 'C09', 'Market Strongroom', 'locked', 10, 8, 22, 'N', 'Locked strongroom: Rare loot', 'Locked door', 'LOC_DOOR_REG_03_03'),
    ('Z2', 'C35', 'Spice Loft', 'side', 10, 8, 26, 'N', 'Secret: illusory wall behind a hanging rug (design choice secret)', 'Walk', 'SECRET_NEW_1'),
    ('Z3', 'C10', 'Sluice Steps', 'entry', 16, 20, 34, 'Y', 'Zone Anchor overlooking the fen; first sight of the reactor glow', 'Stair 6 m', ''),
    ('Z3', 'C11', 'Coolant Fen', 'combat', 50, 40, 36, 'Y', 'Wade 1.2 m water (speed x0.6); leech packs and Hollowed on root islands; dry high route on pipes', 'Wade / pipe walk', ''),
    ('Z3', 'C12', 'Pump House', 'puzzle', 20, 18, 40, 'Y', 'Puzzle: open three sluice valves in order to drain the fen path to the boughs', 'Walk', ''),
    ('Z3', 'C13', 'Fen Ladder', 'shortcut', 4, 12, 42, 'Y', 'Kick-down ladder back to Z2', 'Kick-down ladder', 'Kick-down ladder to Z2'),
    ('Z4', 'C14', 'Bough Stair', 'traverse', 6, 30, 48, 'Y', 'Spiral stair cut into a living trunk; archers on far boughs', 'Stair up 8 m', ''),
    ('Z4', 'C15', 'Branch Bridges', 'combat', 5, 60, 52, 'Y', 'Melee close quarters on 5 m wide boughs; falls over 18 m are lethal; shield-bearers hold the middle', 'Bough walk, lethal drop', ''),
    ('Z4', 'C16', 'Nest Ring', 'combat', 24, 24, 56, 'Y', 'Ambush ring of woven nests; skirmishers drop from above', 'Walk', ''),
    ('Z4', 'C17', 'Bough Strongroom', 'locked', 10, 8, 56, 'N', 'Locked hollow: Rare loot', 'Locked door', 'LOC_DOOR_REG_03_10'),
    ('Z4', 'C18', 'One-way Bark Door', 'shortcut', 3, 4, 56, 'Y', 'Bark door opens only from this side: back to the Z3 Anchor', 'One-way door', 'One-way door to Z3 Anchor'),
    ('Z5', 'C19', 'Barrow Antechamber', 'entry', 16, 14, 64, 'Y', 'Zone Anchor; knight graves, Halden echo kneels; fog gate on the far wall', 'Walk', ''),
    ('Z5', 'C20', "Halden's Grave Hall", 'boss', 53, 24, 70, 'Y', 'Citadel boss: Ser Halden Unburied in a long nave; 4 cover pillars', 'Fog gate', ''),
    ('Z5', 'C21', 'Barrow Lift', 'shortcut', 6, 6, 70, 'Y', 'Lift from the boss antechamber down to Z3', 'Lift 4 m/s', 'Lift from boss antechamber to Z3'),
    ('Z6', 'C22', 'Root Tunnels', 'traverse', 5, 50, 78, 'Y', 'Tight root tunnels opening onto the reactor gallery; zone Anchor at the mouth', 'Walk', ''),
    ('Z6', 'C23', 'Reactor Gallery', 'combat', 80, 30, 84, 'Y', 'Gun gallery 40-80 m over the reactor pool; Remnant fort line on catwalks', 'Catwalks', ''),
    ('Z6', 'C24', 'Shielded Coolant Loop', 'puzzle', 24, 20, 86, 'Y', 'Puzzle: shield the reactor core (rotate three baffles) to cross the radiant floor', 'Walk', ''),
    ('Z6', 'C25', 'Root Strongroom', 'locked', 10, 8, 84, 'N', 'Locked reactor locker: Rare loot', 'Locked door', 'LOC_DOOR_REG_03_17'),
    ('Z6', 'C26', 'Plank Drop', 'shortcut', 3, 10, 84, 'Y', 'Kick a plank down to the Z5 Anchor', 'Drop-down plank', 'Drop-down plank to Z5 Anchor'),
    ('Z7', 'C27', 'Canopy Lift', 'traverse', 8, 8, 92, 'Y', 'Hydroponics cargo lift rides up through the canopy', 'Lift 4 m/s', ''),
    ('Z7', 'C28', 'Pollen Mill', 'combat', 30, 30, 96, 'Y', 'Horde in spore haze (visibility 15 m); burn the haze with Ember', 'Walk', ''),
    ('Z7', 'C29', 'Canopy Walks', 'combat', 70, 6, 98, 'Y', 'Gun line on catwalks 40-80 m; ziplines are one-way down', 'Catwalks', ''),
    ('Z7', 'C30', 'Bridge Winch', 'shortcut', 10, 10, 98, 'Y', 'Lower the bridge from Z7 to Z4 (big loop)', 'Bridge winch', 'Bridge lowered from Z7 to Z4 (big loop)'),
    ('Z7', 'C31', 'Glasshouse Strongroom', 'locked', 12, 10, 98, 'N', 'Locked glasshouse: Rare loot', 'Locked door', 'LOC_DOOR_REG_03_24'),
    ('Z7', 'C36', 'Canopy Ledge', 'side', 8, 6, 104, 'N', 'Secret: hidden ledge path on old hull stencils (design choice secret)', 'Ledge path', 'SECRET_NEW_2'),
    ('Z8', 'C32', 'Heartwood Threshold', 'entry', 14, 14, 106, 'Y', 'Zone Anchor; Sorrel speaks through the trees; fog gate', 'Walk', ''),
    ('Z8', 'C33', 'The Bloom Heart', 'boss', 64, 64, 112, 'Y', "Shard-bearer: Sorrel of the Bloom; stepped platform, roots grow new cover over the fight", 'Fog gate', ''),
    ('Z8', 'C34', "Sorrel's Seat", 'shortcut', 12, 12, 112, 'Y', 'Heart Shard choice; elevator down to Z1 (exit)', 'Elevator', 'Elevator from seat to Z1 (exit)'),
]
CIT_ANCHOR = {'C01': 'Z1', 'C10': 'Z3', 'C19': 'Z5', 'C22': 'Z6', 'C32': 'Z8'}
CIT_SHORTCUT_TO = {'C08': 'C01', 'C13': 'C07', 'C18': 'C10', 'C21': 'C10', 'C26': 'C19', 'C30': 'C16', 'C34': 'C01'}
DOOR_KEYS = {}  # filled from lore Key items

def gen_citadel():
    loc = L['LOC_CIT_' + REG]
    zones = {z['loc_id'][-2:]: z for z in ZONES}
    zone_anchor = {z['loc_id'][-2:]: z['anchor'] for z in ZONES}
    keys = sorted([li['item_id'] for v in LORE.values() for li in v if li['lore_type'] == 'Key'])
    doors = sorted([c['loc_id'] for c in LOCS if c['kind'] == 'Locked door'])
    for d, k in zip(doors, keys):
        DOOR_KEYS[d] = k
    crit_rooms = [x for x in CIT_ROOMS if x[7] == 'Y']
    zone_time = {z: num(zones[z]['path_min']) for z in zones}
    zone_w = collections.Counter()
    W8 = dict(approach=0.6, combat=1.5, puzzle=1.6, traverse=0.8, entry=0.5, boss=3.0, shortcut=0.4)
    for x in crit_rooms:
        zone_w[x[0]] += W8[x[3]]
    order = [x[1] for x in crit_rooms]
    zone_encs = {z: list(ENC_BY_LOC.get(zones[z]['loc_id'], [])) for z in zones}
    gx_by_zone = collections.Counter()
    for i, (z, cid, nm, role, w, d, el, crit, purpose, trav, extra) in enumerate(CIT_ROOMS):
        nid = CIT + '_' + cid
        n = add_node(CIT, nid, seq=order.index(cid) + 1 if crit == 'Y' else '', name=nm, room_type=role.capitalize(), role=role,
                     crit=crit, floor=z, elev_m=el, gx=list(zones).index(z) * 3 + gx_by_zone[z] % 3, gy=gx_by_zone[z] // 3 + (2 if crit == 'N' else 0),
                     w_m=w, d_m=d, purpose=purpose, traversal=trav, zone=zones[z]['loc_id'],
                     crit_s=round(zone_time[z] * 60 * W8.get(role, 1) / zone_w[z]) if crit == 'Y' else 0,
                     light='LGT_REG_03_*' if role == 'approach' else 'LGT_CITADEL via PPV_INTERIOR',
                     music='MUS_THN_CITADEL', ambience='AMB_THN_CITADEL', notes='')
        gx_by_zone[z] += 1
        if cid in CIT_ANCHOR:
            n['anchor'] = zone_anchor.get(CIT_ANCHOR[cid], '')
            cue(CIT, nid, 'SFX', SFX['anchor'], 'Light Anchor')
            cue(CIT, nid, 'MUSIC', 'MUS_STG_ANCHOR_LIT', 'Light Anchor')
            cue(CIT, nid, 'VFX', 'VFX_ENV_ANCHOR_IDLE', 'Always')
        if role == 'combat' and zone_encs[z]:
            e = zone_encs[z].pop(0)
            world_enc(CIT, nid, e)
            cue(CIT, nid, 'MUSIC', 'MUS_THN_COMBAT_L2', 'Aggro')
            cue(CIT, nid, 'MUSIC', 'MUS_THN_COMBAT_END', 'Last enemy dies')
        if role == 'locked':
            n['notes'] = 'Locked door %s; key %s' % (extra, DOOR_KEYS.get(extra, 'none (opens from the far side)'))
            loot(CIT, nid, 'Strongroom chest', 'ITM_LT_VAULT_' + REG, 1, 'Locked', 'Key ' + DOOR_KEYS.get(extra, ''), 'Rarity floor Rare')
            cue(CIT, nid, 'SFX', SFX['door'], 'Unlock')
        if role == 'side':
            if extra.startswith('SECRET'):
                n['secret'] = extra
                loot(CIT, nid, 'Secret chest', 'ITM_LT_GEAR_' + REG, 1, 'Hidden', '', 'Design choice secret; LOC id requested')
                cue(CIT, nid, 'SFX', SFX['illusory'] if 'NEW_1' in extra else SFX['chest'], 'Secret revealed')
                cue(CIT, nid, 'MUSIC', 'MUS_STG_SECRET', 'Secret revealed')
            else:
                loot(CIT, nid, 'Small chest', 'ITM_LT_SMALLCHEST_' + REG, 1, 'Side')
        if role == 'shortcut':
            n['shortcut_to'] = CIT + '_' + CIT_SHORTCUT_TO[cid]
            s = SFX['winch'] if 'winch' in trav.lower() else SFX['kick'] if 'ladder' in trav.lower() else SFX['lift'] if ('Lift' in trav or 'Elevator' in trav) \
                else SFX['bridge'] if 'Bridge' in trav else SFX['door']
            cue(CIT, nid, 'SFX', s, 'Open shortcut')
            cue(CIT, nid, 'SFX', SFX['shortcut'], 'Open shortcut')
            cue(CIT, nid, 'VFX', 'VFX_ENV_SHORTCUT_OPEN', 'Open shortcut')
        if role == 'puzzle':
            loot(CIT, nid, 'Puzzle cache', 'ITM_LT_TIERMAT_' + REG, 2, 'Crit path')
            cue(CIT, nid, 'SFX', SFX['valve'], 'Puzzle step')
            cue(CIT, nid, 'VFX', 'VFX_ENV_COOLANT_STEAM', 'Puzzle step')
        if role == 'boss':
            boss = 'ACT_BOSS_HALDEN' if z == 'Z5' else 'ACT_BOSS_SORREL'
            a = ARENA.get(boss, {})
            add_enc(CIT, nid, 'ENT_BOSS', 'Boss', BOSSES[boss]['Level'], [(boss, 1)], respawn='Never',
                    note='%s; %s; %s m %s; %s' % (BOSSES[boss]['Boss'], a.get('arena_hooks', ''), a.get('diameter_m', ''), a.get('shape', ''), a.get('condition', '')))
            boss_drops(CIT, nid, boss)
            b = boss.replace('ACT_BOSS_', '')
            for ph in ['INTRO', 'P1', 'T2', 'P2', 'T3', 'P3', 'WIN']:
                if 'MUS_BOSS_%s_%s' % (b, ph) in MUS:
                    cue(CIT, nid, 'MUSIC', 'MUS_BOSS_%s_%s' % (b, ph), ph)
            cue(CIT, nid, 'LIGHT', 'PPV_BOSS', 'Fog gate entry')
            cue(CIT, nid, 'SFX', SFX['foggate'], 'Cross fog gate')
            cue(CIT, nid, 'VFX', 'VFX_ENV_FOGGATE', 'Until boss dead')
            if boss == 'ACT_BOSS_SORREL':
                cue(CIT, nid, 'VFX', 'VFX_ENV_ROOT_GROWTH', 'Every 30 s: 1 new cover piece (max 5)')
                cue(CIT, nid, 'SFX', SFX['rootgrow'], 'Cover grows')
            n['notes'] = 'Arena %s m %s; Anchor %s m from gate' % (a.get('diameter_m'), a.get('shape'), a.get('anchor_run_m'))
        if cid == 'C11':
            loot(CIT, nid, 'Shard crate', 'ITM_LT_SHARDCRATE_' + REG, 1, 'Crit path', '', 'Charged ammo on the pipe route')
            cue(CIT, nid, 'VFX', 'VFX_ENV_REACTOR_GLOW', 'Always')
            cue(CIT, nid, 'SFX', SFX['water'], 'Always')
        if cid == 'C28':
            cue(CIT, nid, 'VFX', 'VFX_ENV_SPORE_POD', 'Haze always; clears 20 s after Ember damage')
        if cid == 'C03':
            cue(CIT, nid, 'VFX', 'VFX_ENV_BRAZIER', 'Burnable brambles')
        if cid == 'C34':
            loot(CIT, nid, 'Heart Shard', 'MQ_A2_02 Heart Shard choice', 1, 'End', 'Story', 'Campaign choice; no item id in data')
    # leftover zone encounters go to the zone's last combat room
    for z, rest in zone_encs.items():
        for e in rest:
            tgt = [x for x in CIT_ROOMS if x[0] == z and x[3] in ('combat', 'traverse', 'entry')]
            world_enc(CIT, CIT + '_' + (tgt[-1][1] if tgt else 'C01'), e)
    # Citadel lore (requested)
    for cid in ('C04', 'C12', 'C24'):
        loot(CIT, CIT + '_' + cid, 'Lore item (Ship log)', 'ITM_LOR_CIT_REG_03_%s' % cid, 1, 'Crit path', '', 'Requested: hydroponics bay logs')
    req('data/items/lore_items.csv', 'new rows', 'ITM_LOR_CIT_REG_03_C04, _C12, _C24 (Ship logs: hydroponics bay, Sorrel as chief, the captain said yes)', 'Plan 5.1: lore in every site; Citadel had none')
    # exits
    nodes = [n for n in NODES if n['lvl_id'] == CIT]
    critn = [n for n in nodes if n['crit'] == 'Y']
    critn.sort(key=lambda n: n['seq'])
    for a, b in zip(critn, critn[1:]):
        if a['role'] == 'shortcut' and a['node_id'].endswith('C34'):
            continue
        a['exits'] = b['node_id'] + ' (walk)'
    for n in nodes:
        if n.get('shortcut_to'):
            n['exits'] = (n.get('exits', '') + '; ' if n.get('exits') else '') + n['shortcut_to'] + ' (shortcut)'
        if n['crit'] == 'N':
            host = [x for x in CIT_ROOMS if x[0] == n['zone'][-2:] and x[7] == 'Y' and x[3] in ('combat', 'entry', 'traverse')]
            n['exits'] = CIT + '_' + host[-1][1] + ' (walk)'
    total = sum(zone_time.values())
    add_level(lvl_id=CIT, loc_id=loc['loc_id'], name=loc['name'], story_name="Halden's Barrow (Z5) and the Heartwood (Z8) in campaign docs",
              kind='Citadel', kit='KIT_CITADEL_BRIAR', biome=loc['biome'], grid=loc['grid'], x_m=loc['x_m'], y_m=loc['y_m'], z_m=loc['z_m'],
              level=loc['level'], layout='Side-view zone flow, 8 zones, %d rooms; 7 shortcuts + 1 exit elevator; see maps/LVL_THN_CIT_side.svg' % len(CIT_ROOMS),
              cell_m=20, floors=8, rooms=len(CIT_ROOMS), entry_anchor=zone_anchor.get('Z1'), anchors=' '.join(v for v in zone_anchor.values() if v),
              gate='MQ_A2_02 passage through the Moot (duel, bribe or Dren)', boss='ACT_BOSS_HALDEN ACT_BOSS_SORREL',
              crit_min=round(total), full_min=round(total * 1.3), shortcut='7 shortcuts (see nodes)',
              mood='A hydroponics engine section swallowed by a thorn fortress; green reactor light under red bark; the higher you climb the more it is forest and the less ship',
              light='LGT_CITADEL via PPV_INTERIOR; open zones use LGT_REG_03_*', music='MUS_THN_CITADEL', ambience='AMB_THN_CITADEL', notes='Hand-authored; see 02-citadel-briar-engine.md')

# ================================================================ TOWNS (hand-authored)
TOWNS = {
    'LOC_TOWN_REG_03_01': dict(story='Redbark Lodge', level=24, mood='Palisade of living thorn around a clearing; lanterns in redbark; smoke, bread, children; the safest place in the forest', nodes=[
        ('T01', 'Hollow Gate', 'Gate in a trained thorn hedge; town Anchor; guards check for Hollowing', 'anchor'),
        ('T02', 'Market Green', 'Wandering trader stall (ACT_NPC_VEN_TRADER_REG_03), well, notice board (bounties)', 'vendor'),
        ('T03', 'Smithy', 'Smith (upgrades; Smithing bench); redbark charcoal forge', 'vendor'),
        ('T04', "Reeve's Longhouse", 'ACT_NPC_BRIAR_REEVE_HOLT: SQ_REG_03_06, SQ_REG_03_09, SQ_REG_03_10', 'quest'),
        ('T05', 'Briar Chapel', 'LOC_CQ_REG_03_BRIAR_CHAPEL: CMPQ_C2_03 (ACT_NPC_CONFESSOR_WENNA)', 'quest'),
        ('T06', 'Infirmary', 'LOC_CQ_REG_03_BRIAR_INFIRMARY: CMPQ_C6_03 (ACT_NPC_PATIENT_LIDA)', 'quest'),
        ('T07', 'Lantern Mission', 'LOC_CQ_REG_03_BRIAR_MISSION: QST_LC_06 (ACT_NPC_LC_BROTHER_TEODOR)', 'quest'),
        ('T08', 'Schoolhouse Garden', 'ACT_NPC_GARDENER_WREN (SQ_REG_03_07), ACT_NPC_GIRL_ASTER (SQ_REG_03_05)', 'quest'),
        ('T09', "Handler's Kennels", 'ACT_NPC_HANDLER_YSOLDE: SQ_REG_03_01; hound pens', 'quest'),
        ('T10', "Herbalist's Hut", 'ACT_NPC_HERBALIST_WYNN: SQ_REG_03_02; Brewing bench', 'quest'),
        ('T11', 'Strider Paddock', 'Wild Striders graze outside; tame one with the Harness (GATE_06)', 'service'),
        ('T12', 'Watch Platform', 'Vantage over the canopy: Mother Tree and the Briar Engine stacks in view', 'vista'),
        ('T13', 'Redbark Inn', 'Rest, rumours, Echo summons for sale; Hull Knight Rook (QST_HK_05) drinks here', 'service'),
    ]),
    'LOC_TOWN_REG_03_02': dict(story='Thicket Steading', level=30, mood='Stilt town over reactor bog; boardwalks, green water light from below, rope bridges, lamp tower; damp and busy', nodes=[
        ('T01', 'Causeway Gate', 'Stilt gate at the end of a hull-plate causeway; town Anchor', 'anchor'),
        ('T02', "Postmaster's Office", 'ACT_NPC_THICKET_POSTMASTER: QST_SHB_A15', 'quest'),
        ('T03', 'Ferry Landing', 'ACT_NPC_FERRYMAN_COBB: SQ_REG_03_03; punt ferry to Rotmire edge', 'quest'),
        ('T04', 'Caravan Yard', 'Salvagers caravan (ACT_NPC_SG_CARAVAN_HOLT): QST_SG_05; Vehicle depot is outside town', 'quest'),
        ('T05', 'Hull Knight Billet', 'QST_HK_06 (ACT_NPC_HK_CPL_CALDER)', 'quest'),
        ('T06', 'Stilt Market', 'Tinker and brewer stalls; Tinkering bench', 'vendor'),
        ('T07', 'Boardwalk Inn', 'Rest, rumours, Echo summons', 'service'),
        ('T08', 'Lamp Tower', 'Climbable vantage (8 m ladder) over the bog; fireflies at dusk', 'vista'),
    ]),
    'LOC_TOWN_REG_03_03': dict(story="Thorn King's Moot", level=29, mood='Clan capital in a ring of antlered trunks; bone banners, brazier smoke, war drums; tense and proud', nodes=[
        ('T01', 'Moot Gate', 'Bone-and-antler gate across the logging road; clan guards stop the player; Moot Anchor', 'anchor'),
        ('T02', 'Cage Row', 'Dren (ACT_CMP_C7) caged here: CMPQ_C7_01; cousin Pip (ACT_NPC_DREN_COUSIN_PIP)', 'quest'),
        ('T03', 'Moot Ring', 'MQ_A2_02 passage: duel ring 30 m (clan champion, ACT_THORN_LEADER-based, level 30)', 'quest'),
        ('T04', "King's Hall", 'ACT_NPC_THORNKING_GRAL; bribe option (6,000 Ember, design choice); QST_QH_05 target', 'quest'),
        ('T05', "Chieftains' Fires", 'Varr, Hesk and Oddun fires: CMPQ_C7_04, CMPQ_C7_05', 'quest'),
        ('T06', 'Hound Pits', "Thorn King's Hound lineage; ties to ACT_BOSS_THORNHOUND (CMPQ_C7_05)", 'lore'),
        ('T07', 'Bone Market', 'ACT_NPC_THORN_TRADER_SKELL: Thorn gear vendor once passage is won; QST_SG_05', 'vendor'),
        ('T08', "Elder's Tree", 'ACT_NPC_THORN_ELDER_MORROW: SQ_REG_03_08', 'quest'),
        ('T09', 'East Road Gate', 'Logging road onward to the Briar Engine (Citadel)', 'exit'),
    ]),
}

def gen_town(loc_id, spec, loc):
    lvl = 'LVL_THN_' + loc_id.split('_', 1)[1]
    anc = ANCH_BY_PARENT.get(loc_id, [''])[0] if ANCH_BY_PARENT.get(loc_id) else ('LOC_ANC_REG_03_40' if loc_id.endswith('_03') else '')
    prev = None
    for i, (tid, nm, purpose, kind) in enumerate(spec['nodes']):
        nid = lvl + '_' + tid
        n = add_node(lvl, nid, seq=i + 1, name=nm, room_type=kind.capitalize(), role=kind, crit='Y' if kind in ('anchor', 'exit') or (loc_id.endswith('_03') and tid in ('T02', 'T03', 'T04')) else 'N',
                     floor=1, elev_m=8 if kind == 'vista' else 0, gx=i % 4, gy=i // 4, w_m=20 if kind != 'vista' else 6, d_m=16 if kind != 'vista' else 6,
                     purpose=purpose, traversal='Walk; no combat in town' if not loc_id.endswith('_03') else 'Walk; hostile until passage is won',
                     light='LGT_REG_03_*', music='MUS_THN_TOWN', ambience='AMB_THN_WALLA + AMB_THN_BED_DAY/NIGHT', crit_s=60 if kind in ('anchor', 'quest') else 0,
                     exits=(lvl + '_T01 (walk)') if i else '')
        if kind == 'anchor':
            n['anchor'] = anc
            cue(lvl, nid, 'SFX', SFX['anchor'], 'Light Anchor')
            cue(lvl, nid, 'MUSIC', 'MUS_STG_ANCHOR_LIT', 'Light Anchor')
        if kind == 'vista':
            cue(lvl, nid, 'MUSIC', 'MUS_THN_DISCOVERY', 'First climb')
        if kind == 'vendor':
            cue(lvl, nid, 'SFX', SFX['fire'], 'Forge/brazier loop' if 'Smith' in nm else 'Stall lanterns')
        cue(lvl, nid, 'SFX', SFX['walla'], 'Crowd density RTPC by time of day')
    cue(lvl, lvl + '_T01', 'MUSIC', 'MUS_THN_TOWN', 'Enter town volume')
    if loc_id.endswith('_03'):
        add_enc(lvl, lvl + '_T03', 'ENT_DUEL', 'FAC_THORN', 30, [('ACT_THORN_LEADER', 1)], respawn='Never', cond='Only if the player chooses the duel',
                note='MQ_A2_02 passage duel; champion uses ACT_THORN_LEADER moves at 1.5x HP (design choice); yield at 10% HP, no death')
        add_enc(lvl, lvl + '_T01', 'ENT_FORT', 'FAC_THORN', 29, [('ACT_THORN_SHIELDBEARER', 2), ('ACT_THORN_ARTILLERY', 2), ('ACT_THORN_HEAVY', 1), ('ACT_VAR_R3_03', 2)],
                cond='Only if the player attacks before passage or the Moot is broken (CMPQ_C7_05)', note='Gate guard; hostile state only')
        loot(lvl, lvl + '_T04', 'Passage gift', 'ITM_LT_GEAR_' + REG, 1, 'Story', 'Passage won by duel', 'Design choice')
        loot(lvl, lvl + '_T06', 'Lore item (Relic)', 'ITM_LOR_TOWN_REG_03_03', 1, 'Side', '', 'Requested: hound lineage carving')
        req('data/world/locations.csv', 'new LOC', "LOC_TOWN_REG_03_03 Thorn King's Moot (Settlement, level 29) at x=%s y=%s; Anchor LOC_ANC_REG_03_40" % (loc['x_m'], loc['y_m']),
            'Plan 3.7 asks for 2-3 towns; campaign (MQ_A2_02, CMPQ_C7_*, SQ_REG_03_06/08/10, QST_QH_05, QST_SG_05) needs the Moot')
    for c in CHILD.get(loc_id, []):
        if c['kind'] == 'Lore site':
            for li in LORE.get(c['loc_id'], []):
                loot(lvl, lvl + '_T04', 'Lore item (' + li['lore_type'] + ')', li['item_id'], 1, 'Side')
    sto = loc_id
    n = len(spec['nodes'])
    add_level(lvl_id=lvl, loc_id=loc_id, name=loc['name'], story_name=spec['story'] if spec['story'] != loc['name'] else '', kind='Town', kit='KIT_TOWN_THORNWOOD', biome=loc['biome'],
              grid=loc['grid'], x_m=loc['x_m'], y_m=loc['y_m'], z_m=loc.get('z_m', ''), level=spec['level'],
              layout='Hub-and-spoke: %d districts around the gate node, 20 m cells' % n, cell_m=20, floors=1, rooms=n, entry_anchor=anc, anchors=anc,
              gate='MQ_A2_02 (hostile until passage)' if sto.endswith('_03') else '', boss='', crit_min=8 if not sto.endswith('_03') else 25,
              full_min=20 if not sto.endswith('_03') else 45, shortcut='', mood=spec['mood'], light='LGT_REG_03_*', music='MUS_THN_TOWN',
              ambience='AMB_THN_WALLA', notes='World name is primary (project rule); story_name is the campaign name, note only')

# ================================================================ POIs etc. (templates)
POI_T = {
    'faction camp': [('Outer pickets', 'combat'), ('Fire ring', 'combat'), ('Tents', 'loot'), ('Lookout', 'vista')],
    'ruin': [('Broken wall', 'approach'), ('Inner court', 'combat'), ('Cellar', 'loot')],
    'wreck fragment': [('Debris field', 'approach'), ('Hull breach', 'combat'), ('Cargo pod', 'loot')],
    'wayshrine': [('Pilgrim path', 'approach'), ('Shrine', 'lore'), ('Offering bowl', 'loot')],
    'watchtower': [('Tower base', 'combat'), ('Ladder', 'traverse'), ('Tower top', 'loot')],
    'overturned cart': [('Road', 'approach'), ('Cart', 'loot'), ('Ambush brush', 'combat')],
    'overlook': [('Climb path', 'traverse'), ('Ledge', 'vista')],
    'hermit hut': [('Garden', 'approach'), ('Hut', 'lore'), ('Root cellar', 'loot')],
    'grave field': [('Graves', 'lore'), ('Mausoleum', 'loot'), ('Barrow mound', 'combat')],
    'shard crater': [('Crater rim', 'approach'), ('Crater floor', 'combat'), ('Glowing core', 'loot')],
    'hunting ground': [('Game trail', 'combat'), ('Hunter blind', 'loot'), ('Kill site', 'lore')],
    'lair': [('Den mouth', 'approach'), ('Den', 'combat'), ('Bone pile', 'loot')],
    'trader stop': [('Wagon camp', 'vendor'), ('Fire', 'rest')],
    'vehicle depot': [('Yard', 'service'), ('Workshop', 'loot'), ('Fuel shed', 'side')],
}
POI_TIME = {'faction camp': 6, 'ruin': 4, 'wreck fragment': 4, 'wayshrine': 2, 'watchtower': 4, 'overturned cart': 3, 'overlook': 2,
            'hermit hut': 3, 'grave field': 4, 'shard crater': 5, 'hunting ground': 4, 'lair': 5, 'trader stop': 2, 'vehicle depot': 3}

def gen_small(loc, kind_label, steps, crit_min, extra_notes='', mood_extra=''):
    lvl = 'LVL_THN_' + loc['loc_id'].split('_', 1)[1]
    biome = loc['biome']
    encs = list(ENC_BY_LOC.get(loc['loc_id'], []))
    for ch in CHILD.get(loc['loc_id'], []):
        encs += ENC_BY_LOC.get(ch['loc_id'], [])
    nodes = []
    for i, (nm, role) in enumerate(steps):
        nid = '%s_N%02d' % (lvl, i + 1)
        n = add_node(lvl, nid, seq=i + 1, name=nm, room_type=role.capitalize(), role=role, crit='Y' if role != 'side' else 'N', floor=1,
                     elev_m=12 if role == 'vista' else 0, gx=i, gy=0, w_m=12 if role != 'combat' else 30, d_m=10 if role != 'combat' else 24,
                     purpose={'combat': 'Fight', 'loot': 'Loot', 'lore': 'Lore', 'vista': 'Vantage; reveals nearby markers', 'approach': 'Read the space',
                              'traverse': 'Climb', 'vendor': 'Vendor', 'rest': 'Rest point (no Anchor)', 'service': 'Vehicle spawn', 'side': 'Optional'}.get(role, role),
                     traversal='Ladder 2 m/s' if role == 'traverse' else 'Walk; Strider allowed',
                     light='LGT_REG_03_*', music='MUS_THN_EXPLORE_DAY/NIGHT', ambience='AMB_THN_BED_DAY/NIGHT + AMB_THN_WILDLIFE',
                     crit_s=round(crit_min * 60 / len(steps)), exits='')
        nodes.append(n)
    for a, b in zip(nodes, nodes[1:]):
        a['exits'] = b['node_id'] + ' (walk)'
    comb = [n for n in nodes if n['role'] == 'combat'] or nodes
    for k, e in enumerate(encs):
        tgt = comb[k % len(comb)]
        world_enc(lvl, tgt['node_id'], e)
        cue(lvl, tgt['node_id'], 'MUSIC', 'MUS_THN_COMBAT_L1', 'Aggro')
    for n in nodes:
        if n['role'] == 'loot':
            loot(lvl, n['node_id'], 'Small chest', 'ITM_LT_SMALLCHEST_' + REG, 1, 'Crit path')
            cue(lvl, n['node_id'], 'VFX', 'VFX_ENV_CHEST_GLINT', 'Visible 12 m')
        if n['role'] == 'lore':
            loot(lvl, n['node_id'], 'Shard-note (pre-placed)', 'Shard-note hint', 1, 'Crit path', '', 'Points at the nearest secret or site')
            cue(lvl, n['node_id'], 'VFX', 'VFX_ENV_LORE_GLINT', 'Visible 8 m')
        if n['role'] == 'vista':
            cue(lvl, n['node_id'], 'MUSIC', 'MUS_THN_DISCOVERY', 'First reach')
    for ch in CHILD.get(loc['loc_id'], []):
        if ch['kind'] == 'Small chest':
            tgt = next((n for n in nodes if n['role'] == 'loot'), nodes[-1])
            loot(lvl, tgt['node_id'], 'Small chest (' + ch['loc_id'] + ')', 'ITM_LT_SMALLCHEST_' + REG, 1, 'Crit path')
        if ch['kind'] == 'Shard crate':
            loot(lvl, nodes[0]['node_id'], 'Shard crate (' + ch['loc_id'] + ')', 'ITM_LT_SHARDCRATE_' + REG, 1, 'Crit path')
        if ch['kind'] == 'Secret':
            tgt = nodes[-1]
            tgt['secret'] = ch['loc_id']
            place_secret(lvl, tgt['node_id'], ch)
        if ch['kind'] == 'Lore site':
            for li in LORE.get(ch['loc_id'], []):
                loot(lvl, nodes[-1]['node_id'], 'Lore item (' + li['lore_type'] + ')', li['item_id'], 1, 'Side')
        if ch['kind'] == 'Public event':
            nodes[0]['notes'] = (nodes[0].get('notes', '') + ' Public event %s: %s. %s' % (ch['loc_id'], ch['name'], ch['notes'])).strip()
            if not ENC_BY_LOC.get(ch['loc_id']):
                add_enc(lvl, nodes[0]['node_id'], 'ENT_EVENT', 'FAC_REMNANT', ch['level'], [('ACT_REMNANT_FODDER', 6), ('ACT_REMNANT_HEAVY', 1)], respawn='Event timer')
    for a in ANCH_BY_PARENT.get(loc['loc_id'], []):
        nodes[0]['anchor'] = a
        cue(lvl, nodes[0]['node_id'], 'SFX', SFX['anchor'], 'Light Anchor')
    add_level(lvl_id=lvl, loc_id=loc['loc_id'], name=loc['name'], story_name='', kind=kind_label, kit='Open world', biome=biome, grid=loc['grid'],
              x_m=loc['x_m'], y_m=loc['y_m'], z_m=loc.get('z_m', ''), level=loc['level'],
              layout='Linear node chain, %d nodes, 10 m cells' % len(steps), cell_m=10, floors=1, rooms=len(steps),
              entry_anchor=nodes[0].get('anchor', ''), anchors=nodes[0].get('anchor', ''), gate='', boss='', crit_min=crit_min,
              full_min=crit_min + (2 if CHILD.get(loc['loc_id']) else 0), shortcut='', mood=(MOOD.get(biome, '') + mood_extra).strip(),
              light='LGT_REG_03_* via PPV_REG_03', music='MUS_THN_EXPLORE_DAY/NIGHT', ambience='AMB_THN_BED_DAY/NIGHT', notes=extra_notes)
    return lvl, nodes

def gen_field_boss(loc):
    boss = [b for b, a in ARENA.items() if a['loc_id'] == loc['loc_id']][0]
    a = ARENA[boss]
    lvl, nodes = gen_small(loc, 'Field boss ground', [('Approach', 'approach'), ('Outskirts', 'combat'), ('Boss ground', 'boss'), ('Cache', 'loot')], 12,
                           extra_notes='%s; leash %s' % (a['condition'], a['entry']))
    bn = nodes[2]
    bn['w_m'] = bn['d_m'] = int(num(a['diameter_m'], 120))
    bn['notes'] = 'Arena %s m %s, %s cover; Strider allowed (MET_ARENA_FIELD); %s' % (a['diameter_m'], a['shape'], a['cover_pieces'], a['condition'])
    if not nodes[0].get('anchor'):
        nodes[0]['anchor'] = a['nearest_anchor']
    add_enc(lvl, bn['node_id'], 'ENT_FIELDBOSS', 'Boss', BOSSES[boss]['Level'], [(boss, 1)], respawn='Never', note=BOSSES[boss]['Boss'] + '; ' + a['arena_hooks'])
    crt = 'ACT_CRT_BOGLEECH' if 'bog' in loc['biome'].lower() else 'ACT_CRT_THORNBOAR'
    if not [e for e in ENC_OUT if e['node_id'] == nodes[1]['node_id']]:
        add_enc(lvl, nodes[1]['node_id'], 'ENT_CRT_PACK', 'Creature', loc['level'], [(crt, 4 if 'LEECH' in crt else 3)], note='Design choice: outskirts pack telegraphs the boss')
    boss_drops(lvl, bn['node_id'], boss)
    b = boss.replace('ACT_BOSS_', '')
    for ph in ['INTRO', 'P1', 'T2', 'P2', 'WIN']:
        if 'MUS_BOSS_%s_%s' % (b, ph) in MUS:
            cue(lvl, bn['node_id'], 'MUSIC', 'MUS_BOSS_%s_%s' % (b, ph), ph)
    LEVELS[-1]['boss'] = boss
    if 'THORNHOUND' in boss:
        LEVELS[-1]['notes'] += '; once seen, the Hound roams the region and can ambush on any road (design: 1 roam event per 20 min of play until killed)'

def gen_choir(loc):
    steps = [('Hidden entrance', 'approach'), ('Antechamber', 'entry'), ('Trial of Rising', 'puzzle'), ('Trial of Falling', 'combat'),
             ('Trial of the Long Lift', 'puzzle'), ('Resonance Altar', 'reward')]
    lvl, nodes = gen_small(loc, 'Choir site', steps, 14, extra_notes='GATE_05: entrance revealed by a Shard-note hint or Ostra within 40 m. ' + loc['notes'])
    for n, txt in zip(nodes[2:5], ['Use gravity lift pads to reach 3 floating root platforms (no resonance yet: pads are fixed)',
                                   'Fight Hollowed on platforms that sink while you stand on them',
                                   'Ride one long lift column while artillery fires; break 3 Shard nodes to stop it']):
        n['notes'] = txt
        n['light'] = 'LGT_CAVE'
    loot(lvl, nodes[-1]['node_id'], 'Resonance grant', 'RES_GRAVITYLIFT', 1, 'End', 'First visit')
    cue(lvl, nodes[-1]['node_id'], 'SFX', 'Play_SFX_Resonances_GravityLift_OstraVoiceLine', 'Grant')
    cue(lvl, nodes[-1]['node_id'], 'VFX', 'VFX_ENV_CHOIR_TONE', 'Grant')
    cue(lvl, nodes[1]['node_id'], 'MUSIC', 'MUS_THN_SITE', 'Enter')
    LEVELS[-1].update(kind='Choir site', kit='KIT_CHOIR_VAULT', light='LGT_CAVE via PPV_INTERIOR', music='MUS_THN_SITE')

def gen_relay(loc):
    steps = [('Tower base', 'combat'), ('Stage 1: Ledges (25 m)', 'traverse'), ('Stage 2: Lift (55 m)', 'traverse'), ('Stage 3: Ladder to the crown (80 m)', 'vista')]
    lvl, nodes = gen_small(loc, 'Relay Tower', steps, 7, extra_notes='GATE_08: climbing reveals the Thornwood map. ' + loc['notes'])
    nodes[3]['notes'] = 'Ostra fills in the map; beam sweep'
    cue(lvl, nodes[3]['node_id'], 'SFX', SFX['relay'], 'Activate')
    cue(lvl, nodes[3]['node_id'], 'VFX', 'VFX_ENV_RELAY_BEAM', 'Activate')
    cue(lvl, nodes[2]['node_id'], 'SFX', SFX['lift'], 'Ride')
    nodes[0]['anchor'] = nodes[0].get('anchor') or ANCH_BY_PARENT.get(loc['loc_id'], [''])[0]

def gen_landmark(loc):
    lm = LMK.get(loc['loc_id'], {})
    steps = [('Base', 'approach'), ('Vantage', 'vista')]
    lvl, nodes = gen_small(loc, 'Landmark', steps, 3, extra_notes='Height %s m, visible %s km (%s)' % (lm.get('height_m'), lm.get('visible_km'), lm.get('role')))
    cue(lvl, nodes[0]['node_id'], 'MUSIC', 'MUS_THN_DISCOVERY', 'First time on screen within visible range')
    cue(lvl, nodes[0]['node_id'], 'VFX', 'VFX_ENV_LEAF_FALL' if 'Redbark' in loc['biome'] else 'VFX_ENV_FIREFLY', 'Always')

def gen_uv(loc):
    steps = [('Shaft head', 'approach'), ('Root spiral (down 60 m)', 'traverse'), ('Cage lift (down to 210 m)', 'traverse'), ('Weave Caverns threshold', 'exit')]
    lvl, nodes = gen_small(loc, 'Undervault entry', steps, 5, extra_notes='Leads to REG_U Weave Caverns (levels 42-56); caverns are planned with the Undervault, not here')
    cue(lvl, nodes[2]['node_id'], 'SFX', SFX['lift'], 'Ride')
    cue(lvl, nodes[3]['node_id'], 'MUSIC', 'MUS_UND_DISCOVERY', 'First arrival')

def gen_conn(loc):
    steps = [('Gate', 'approach'), ('Road', 'traverse')]
    gen_small(loc, 'Region connection', steps, 2, extra_notes=loc['name'])

def gen_patrol(loc):
    steps = [('Patrol loop', 'combat')]
    gen_small(loc, 'Patrol route', steps, 2, extra_notes='Loop 150-300 m around the named Anchor')

# ================================================================ OVERWORLD
def tour_min():
    pts = [L[l] for l in LOC2LVL if l in L]
    if not pts:
        return ''
    cur, left, d = pts[0], pts[1:], 0
    while left:
        nxt = min(left, key=lambda p: dist(cur, p))
        d += dist(cur, nxt) * 1.3  # roads wind
        left.remove(nxt)
        cur = nxt
    return round(d / 14 / 60 + len(pts) * 0.5)  # Strider 14 m/s + 30 s mount/dismount per stop

def gen_overworld(moot):
    lvl = 'LVL_THN_WORLD'
    route = [('LOC_CON_06', 'Briar Gate (enter from Lantern Hold)'), ('LOC_TOWN_REG_03_01', L.get('LOC_TOWN_REG_03_01', {}).get('name', 'Town 01')), ('LOC_RELAY_REG_03', 'Relay Tower (map)'),
             (moot['loc_id'], "Thorn King's Moot (passage)"), ('LOC_CIT_REG_03', 'The Briar Engine (Citadel)')]
    prev = None
    total_s = 0
    for i, (lid, nm) in enumerate(route):
        loc = L.get(lid) or moot
        d = dist(prev, loc) if prev else 0
        t = round(d / 14 + 30) if prev else 0
        total_s += t
        add_node(lvl, '%s_R%02d' % (lvl, i + 1), seq=i + 1, name=nm, room_type='Route stop', role='route', crit='Y', floor=0, elev_m=loc.get('z_m', ''),
                 gx=round(num(loc['x_m']) / 100), gy=round(num(loc['y_m']) / 100), w_m='', d_m='', crit_s=t, purpose='MQ_A2_02 route; links to ' + LOC2LVL.get(lid, ''),
                 traversal='Strider on roads (14 m/s); %d m from previous stop' % d if prev else 'Arrive', light='LGT_REG_03_*',
                 music='MUS_THN_EXPLORE_DAY/NIGHT', ambience='AMB_THN_BED_DAY/NIGHT', exits='%s_R%02d (road)' % (lvl, i + 2) if i < len(route) - 1 else '')
        prev = loc
    for a in sorted(ANCH.values(), key=lambda a: a['loc_id']):
        if a['anchor_type'] == 'Field':
            add_node(lvl, lvl + '_' + a['loc_id'][-6:], seq='', name='Field Anchor ' + a['loc_id'], room_type='Anchor', role='anchor', crit='N', floor=0,
                     elev_m='', gx=round(num(a['x_m']) / 100), gy=round(num(a['y_m']) / 100), w_m=8, d_m=8, purpose='Checkpoint; fast travel once lit',
                     anchor=a['loc_id'], traversal='', light='LGT_REG_03_*', music='MUS_STG_ANCHOR_LIT', ambience='AMB_THN_WEAVE_HUM', crit_s=0, exits='')
    # loose locs: gather nodes, chests and doors without parent -> nearest level or overworld
    homes = [L[l] for l in LOC2LVL if l in L]
    for r in LOCS:
        if r['loc_id'] in LOC2LVL or r['parent_loc'] or r['kind'] in ('Anchor',):
            continue
        if r['kind'] in ('Gather node', 'Small chest', 'Shard crate', 'Locked door', 'Lore site'):
            best = min(homes, key=lambda h: dist(h, r)) if homes else None
            d = dist(best, r) if best else 9e9
            tgt_lvl = LOC2LVL[best['loc_id']] if d <= 60 else lvl
            node = [n for n in NODES if n['lvl_id'] == tgt_lvl][0]['node_id']
            if r['kind'] == 'Gather node':
                loot(tgt_lvl, node, 'Gather node (' + r['loc_id'] + ')', 'ITM_LT_NODE_' + r['tags'].upper(), 1, 'Open world', '', '%s %s' % (r['grid'], r['biome']))
            elif r['kind'] == 'Locked door':
                loot(tgt_lvl, node, 'Locked door (' + r['loc_id'] + ')', 'ITM_LT_VAULT_' + REG, 1, 'Locked', 'Key ' + DOOR_KEYS.get(r['loc_id'], 'requested'), r['grid'])
            elif r['kind'] == 'Lore site':
                for li in LORE.get(r['loc_id'], []):
                    loot(tgt_lvl, node, 'Lore item (' + li['lore_type'] + ')', li['item_id'], 1, 'Open world', '', r['grid'])
            else:
                loot(tgt_lvl, node, r['kind'] + ' (' + r['loc_id'] + ')', 'ITM_LT_%s_%s' % ('SMALLCHEST' if r['kind'] == 'Small chest' else 'SHARDCRATE', REG), 1, 'Open world', '', r['grid'])
    cue(lvl, lvl + '_R01', 'MUSIC', 'MUS_THN_EXPLORE_DAY', 'Day (06:00-19:00)')
    cue(lvl, lvl + '_R01', 'MUSIC', 'MUS_THN_EXPLORE_NIGHT', 'Night')
    cue(lvl, lvl + '_R01', 'MUSIC', 'MUS_THN_TENSION', 'Enemies aware, not engaged')
    cue(lvl, lvl + '_R01', 'MUSIC', 'MUS_THN_HOLLOWING', 'World_State=Hollowed (late game)')
    for a in ['AMB_THN_BED_DAY', 'AMB_THN_BED_NIGHT', 'AMB_THN_WIND', 'AMB_THN_WEATHER', 'AMB_THN_WILDLIFE', 'AMB_THN_EMITTERS', 'AMB_THN_WEAVE_HUM', 'AMB_THN_WATER', 'AMB_THN_HOLLOWING']:
        cue(lvl, lvl + '_R01', 'AMB', a, 'Region-wide')
    for l in ['LGT_REG_03_DAWN', 'LGT_REG_03_DAY', 'LGT_REG_03_DUSK', 'LGT_REG_03_NIGHT', 'LGT_REG_03_STORM', 'PPV_REG_03']:
        cue(lvl, lvl + '_R01', 'LIGHT', l, 'Time of day / weather manager')
    for v in ['VFX_ENV_POLLEN_DRIFT', 'VFX_ENV_LEAF_FALL', 'VFX_ENV_FIREFLY', 'VFX_ENV_SAP_DRIP', 'VFX_ENV_SHARD_GLOW']:
        cue(lvl, lvl + '_R01', 'VFX', v, 'Region-wide by biome')
    add_level(lvl_id=lvl, loc_id='', name='Thornwood overworld', story_name='', kind='Region overworld', kit='Landscape', biome=LAYOUT['biomes'],
              grid='', x_m=LAYOUT['center_x_m'], y_m=LAYOUT['center_y_m'], z_m=LAYOUT['elevation_m'], level='20-34',
              layout='World grid (100 m cells); main route node chain + field Anchors; see maps/LVL_THN_WORLD.svg', cell_m=100, floors='', rooms='',
              entry_anchor='', anchors=' '.join(a for a in ANCH if ANCH[a]['anchor_type'] == 'Field'), gate='GATE_02 (ACT_BOSS_CORSA defeated)', boss='',
              crit_min=round(total_s / 60), full_min=tour_min(), shortcut='', mood=LAYOUT['weather'], light='LGT_REG_03_* via PPV_REG_03',
              music='MUS_THN_EXPLORE_DAY/NIGHT', ambience='AMB_THN_BED_DAY/NIGHT', notes='Route travel on Strider; field encounters live in POI and patrol levels')

# ================================================================ RUN
def main():
    # Moot (new town, sits behind the Antler Gate landmark)
    # design choice: the Moot sits on the logging road between the Relay Tower and the Citadel ("blocks the road", MQ_A2_02),
    # at the free spot (most distance to any other level) within 250 m of the road midpoint
    rl, cl = L['LOC_RELAY_' + REG], L['LOC_CIT_' + REG]
    mx, my = (num(rl['x_m']) + num(cl['x_m'])) / 2, (num(rl['y_m']) + num(cl['y_m'])) / 2
    others = [r for r in LOCS if r['kind'] in ('Site', 'POI', 'Settlement', 'Landmark', 'Field boss', 'Choir vault', 'Choir site', 'Citadel', 'Relay Tower')]
    cands = [dict(x_m=mx + dx, y_m=my + dy) for dx in range(-250, 251, 25) for dy in range(-250, 251, 25)]
    best = max(cands, key=lambda c: min(dist(c, o) for o in others))
    near = min(LOCS, key=lambda o: dist(best, o))
    moot = dict(loc_id='LOC_TOWN_REG_03_03', kind='Settlement', name="Thorn King's Moot", biome=near['biome'], grid=near['grid'],
                x_m=str(round(best['x_m'])), y_m=str(round(best['y_m'])), z_m=near.get('z_m', ''), level='29', notes='', parent_loc='')
    MOOT_GAP[0] = round(min(dist(best, o) for o in others))
    gen_citadel()
    for lid in sorted(SITES):
        gen_site(lid)
    for lid, spec in TOWNS.items():
        gen_town(lid, spec, L.get(lid) or moot)
    for r in LOCS:
        k = r['kind']
        if k == 'Field boss':
            gen_field_boss(r)
        elif k == 'Choir site':
            gen_choir(r)
        elif k == 'Relay Tower':
            gen_relay(r)
        elif k == 'Landmark':
            gen_landmark(r)
        elif k == 'Undervault entry':
            gen_uv(r)
        elif k == 'Connection':
            gen_conn(r)
        elif k == 'Patrol route':
            gen_patrol(r)
        elif k == 'POI':
            t = r['tags'].split(';')[0].strip()
            gen_small(r, 'POI: ' + t, POI_T.get(t, [('Spot', 'approach'), ('Feature', 'loot')]), POI_TIME.get(t, 3))
            if t == 'trader stop':
                NODES[-2]['notes'] = 'Route stop for ACT_NPC_VEN_TRADER_REG_03 (vendor ITM_VEN_TRADER_REG_03)'
            if t == 'vehicle depot':
                NODES[-3]['notes'] = 'Spawns: ' + LAYOUT['vehicles']
    gen_overworld(moot)
    # leftover world encounters (e.g. on kinds with no level)
    used = {e['src_enc'] for e in ENC_OUT}
    for e in ENCS:
        if e['enc_id'] not in used:
            world_enc('LVL_THN_WORLD', 'LVL_THN_WORLD_R01', e, note='World encounter at ' + e['loc_id'] + ' (no level of its own)')
    # quest map
    CQ = {'MOSSGATE': 'LOC_TOWN_REG_03_02', 'THORN_KINGS_MOOT': 'LOC_TOWN_REG_03_03', 'THORN_MOOT': 'LOC_TOWN_REG_03_03',
          'BROOD_CAVES': 'LOC_DGN_REG_03_10', 'ROTMIRE': 'LOC_DGN_REG_03_03', 'ROTMIRE_EDGE': 'LOC_FB_BOGMATRIARCH', 'ROTMIRE_BOG': 'LOC_FB_BOGMATRIARCH',
          'HEARTWOOD': 'LOC_CIT_REG_03', 'ROOT_CHOIR': 'LOC_CHOIR_REG_03', 'BRIAR_CHAPEL': 'LOC_TOWN_REG_03_01', 'BRIAR_INFIRMARY': 'LOC_TOWN_REG_03_01',
          'BRIAR_MISSION': 'LOC_TOWN_REG_03_01', 'CUTTERS_RIDGE': 'LOC_FB_THORNHOUND', 'QUIET_GROVE': 'LOC_VAULT_REG_03_02',
          'HALDENS_BARROW': 'LOC_CIT_REG_03', 'BARROW_ROOT_CRYPT': 'LOC_CIT_REG_03', 'RELAY_TOWER': 'LOC_RELAY_REG_03'}
    POI_BY_TAG = collections.defaultdict(list)
    for r in LOCS:
        if r['kind'] == 'POI':
            POI_BY_TAG[r['tags'].split(';')[0]].append(r['loc_id'])
    for key, tag, idx in [('VARR_HOLDFAST', 'faction camp', 0), ('ODDUN_STEAD', 'faction camp', 1), ('HESK_FALLS', 'faction camp', 2),
                          ('HARL_BARROW', 'grave field', 0), ('CANOPY_LENS', 'overlook', 0), ('THORN_ROAD_FORD', 'overturned cart', 0),
                          ('OFFICERS_HUT', 'hermit hut', 0), ('POD_CANOPY', 'overlook', 1), ('PILLAR_CLEARING', 'ruin', 1), ('SENSOR_HOLLOW', 'wreck fragment', 0), ('MOSS_TERRACE', 'ruin', 0), ('CRYO_SHRINE', 'wayshrine', 0), ('GREY_GROVE', 'hunting ground', 0)]:
        lst = POI_BY_TAG.get(tag, [])
        if lst:
            CQ[key] = lst[idx % len(lst)]
    qrows = []
    for q in sorted(QUESTS, key=lambda q: q['id']):
        for lid in sorted(set(re.findall(r'LOC_[A-Z0-9_]+', json.dumps(q)))):
            tgt = lid
            if lid.startswith('LOC_CQ_REG_03_'):
                tgt = CQ.get(lid[len('LOC_CQ_REG_03_'):], '')
            elif lid.startswith('LOC_SITE_'):
                tgt = L.get(lid, {}).get('parent_loc') or lid
                if tgt not in LOC2LVL and tgt in L:
                    homes = [L[h] for h in LOC2LVL if h in L]
                    tgt = min(homes, key=lambda h: dist(h, L[lid]))['loc_id']
            qrows.append(dict(quest_id=q['id'], quest_name=q.get('name', ''), quest_loc=lid, level_loc=tgt, lvl_id=LOC2LVL.get(tgt, ''),
                              note='' if LOC2LVL.get(tgt) else ('Outside Thornwood' if ('HUB' in lid or 'LANTERN' in lid) else 'No Thornwood level matched')))
    wr('level_quest_map.csv', qrows, ['quest_id', 'quest_name', 'quest_loc', 'level_loc', 'lvl_id', 'note'])
    req('design/campaign (owner)', 'LOC_CQ_REG_03_* aliases', 'See level_quest_map.csv: each campaign quest location mapped to a world LOC and level',
        'Campaign uses its own LOC_CQ ids; world uses LOC_DGN/POI/TOWN ids')
    req('design/world (owner)', 'name aliases', 'Redbark Lodge = LOC_TOWN_REG_03_01; Thicket Steading = LOC_TOWN_REG_03_02; Rotmire = LOC_DGN_REG_03_03; Brood Caves = LOC_DGN_REG_03_10; '
        "Halden's Barrow = LOC_CIT_REG_03_Z5; Heartwood = LOC_CIT_REG_03_Z8", 'Campaign lore bible and world tables use different names for the same places')
    req('design/world (owner)', 'citadel secrets', 'LOC_SEC_REG_03_16 Illusory wall (Citadel Z2 Spice Loft); LOC_SEC_REG_03_17 Hidden ledge path (Citadel Z7 Canopy Ledge)', 'Design choice: Citadel had no secrets')
    req('data/items/lore_items.csv', 'unlocks column', '; '.join('%s opens %s' % (k, d) for d, k in DOOR_KEYS.items()), 'Locked doors need keys; region Key lore items assigned in order')
    req('data/items/vendors.csv', 'new vendors', 'Smith at LOC_TOWN_REG_03_01; Tinker + Brewer at LOC_TOWN_REG_03_02; Thorn gear (ACT_NPC_THORN_TRADER_SKELL) at LOC_TOWN_REG_03_03', 'Towns list these services')
    finish()

def finish():
    # summaries per level
    by_lvl_enc = collections.defaultdict(list)
    for e in ENC_OUT:
        by_lvl_enc[e['lvl_id']].append(e)
    by_lvl_loot = collections.defaultdict(list)
    for l in LOOT:
        by_lvl_loot[l['lvl_id']].append(l)
    for lv in LEVELS:
        es = by_lvl_enc[lv['lvl_id']]
        ls = by_lvl_loot[lv['lvl_id']]
        lv['encounters'] = len(es)
        lv['enemies'] = sum(e['enemy_count'] for e in es)
        lv['loot_points'] = len([l for l in ls if not l['container'].startswith(('Lore', 'Gather', 'Shard-note', 'Secret'))])
        lv['secrets'] = len([l for l in ls if l['container'].startswith('Secret')])
        lv['collectibles'] = 'lore %d; gather %d; shard-notes %d' % (len([l for l in ls if l['container'].startswith('Lore')]),
                                                                       len([l for l in ls if l['container'].startswith('Gather')]),
                                                                       len([l for l in ls if l['container'].startswith('Shard-note')]))
        crit = [n for n in NODES if n['lvl_id'] == lv['lvl_id'] and n['crit'] == 'Y' and n.get('seq') != '']
        crit.sort(key=lambda n: n['seq'])
        lv['critical_path'] = ' > '.join(n['node_id'].split('_')[-1] for n in crit)
        if not lv.get('full_min'):
            lv['full_min'] = round(num(lv['crit_min']) * 1.3)
    # validation
    checks = []
    def chk(name, ok, detail=''):
        checks.append(dict(check=name, result='PASS' if ok else 'FAIL', detail=detail))
    known_act = ENEMIES | CREAT | set(BOSSES) | NPCS
    bad_act = sorted({a for e in ENC_OUT for a, _ in parse_actors(e['actors']) if a not in known_act})
    chk('Every encounter actor exists in data/actors', not bad_act, ' '.join(bad_act))
    item_ok = lambda x: x in ITEMS or x in LT or x.startswith(('RES_', 'MQ_', 'Shard-note'))
    bad_itm = sorted({l['item_ref'] for l in LOOT if not item_ok(l['item_ref'])})
    for x in bad_itm:
        if not x.startswith(('ITM_LOR_CIT', 'ITM_LOR_TOWN')):
            req('data/items', 'missing id', x, 'Referenced by level loot')
    chk('Every loot ref exists (requested ids excluded)', not [x for x in bad_itm if not x.startswith(('ITM_LOR_CIT', 'ITM_LOR_TOWN'))], ' '.join(bad_itm))
    miss = collections.defaultdict(set)
    for c in CUES:
        cid = c['cue_id']
        if c['cue_type'] == 'MUSIC' and cid not in MUS:
            miss['design/audio/music_cues.csv'].add(cid)
        if c['cue_type'] == 'AMB' and cid not in AMB:
            miss['design/audio/ambience_layers.csv'].add(cid)
        if c['cue_type'] == 'SFX' and cid not in EVT:
            miss['design/audio/event_map.csv'].add(cid)
        if c['cue_type'] == 'LIGHT' and cid not in LGT and cid not in PPV:
            miss['design/art/lighting_tod.csv'].add(cid)
    for tgt, ids in miss.items():
        req(tgt, 'new ids', ' '.join(sorted(ids)), 'Used by Thornwood level cues; not in the owner table yet')
    req('design/art (VFX owner)', 'new VFX ids', ' '.join(sorted(VFX)), 'Environment VFX for levels; definitions in vfx_env.csv')
    chk('Audio/light cue ids exist (missing ones requested)', True, '; '.join('%s: %d' % (k, len(v)) for k, v in miss.items()))
    ids = {n['node_id'] for n in NODES}
    bad_ex = [n['node_id'] for n in NODES for ex in (n.get('exits') or '').split(';') if ex.strip() and ex.split()[0] not in ids]
    chk('Every node exit points at a real node', not bad_ex, ' '.join(bad_ex[:10]))
    sites = [lv for lv in LEVELS if lv['loc_id'] in SITES]
    for lv in sites:
        ns = [n for n in NODES if n['lvl_id'] == lv['lvl_id']]
        ok = any(n['role'] == 'shortcut' for n in ns) and any(l['notes'].startswith('Unique') for l in LOOT if l['lvl_id'] == lv['lvl_id'])
        lore = any(l['container'].startswith('Lore') for l in LOOT if l['lvl_id'] == lv['lvl_id'])
        tm = 10 <= num(lv['crit_min']) <= 25
        if not (ok and lore and tm):
            chk('Site rule ' + lv['lvl_id'], False, 'shortcut+reward %s lore %s time %s' % (ok, lore, lv['crit_min']))
    chk('All sites: shortcut, unique reward, lore item, 10-25 min (plan 3.3/3.7)', all(c['result'] == 'PASS' for c in checks if c['check'].startswith('Site rule')))
    cit = [lv for lv in LEVELS if lv['kind'] == 'Citadel'][0]
    chk('Citadel first-play path 120-180 min (plan 5.2)', 120 <= num(cit['crit_min']) <= 180, str(cit['crit_min']))
    total = sum(num(lv['full_min']) for lv in LEVELS)
    main = sum(num(lv['crit_min']) for lv in LEVELS if lv['kind'] in ('Citadel', 'Region overworld', 'Town', 'Relay Tower'))
    loop = main + sum(num(lv['crit_min']) for lv in LEVELS if lv['loc_id'] in SITES or lv['kind'] in ('Field boss ground', 'Choir site'))
    REGION_TIME.update(main=main, loop=loop, total=total)
    chk('Region loop 6-12 h (plan 3.3: main route + Citadel + every site, field boss and Choir site)', 360 <= loop <= 720,
        'main route %.1f h; region loop %.1f h; 100%% clear %.1f h (design value)' % (main / 60, loop / 60, total / 60))
    n_sites = len(sites)
    chk('15-20 sites (plan 3.7)', 15 <= n_sites <= 20, str(n_sites))
    n_towns = len([lv for lv in LEVELS if lv['kind'] == 'Town'])
    chk('2-3 towns (plan 3.7)', 2 <= n_towns <= 3, str(n_towns))
    n_poi = len([lv for lv in LEVELS if lv['kind'].startswith('POI')])
    chk('30-40 POIs (plan 3.7)', 30 <= n_poi <= 40, str(n_poi))
    chk('2 field bosses, 1 Choir site', len([lv for lv in LEVELS if lv['kind'] == 'Field boss ground']) == 2 and len([lv for lv in LEVELS if lv['kind'] == 'Choir site']) == 1)
    for lv in LEVELS:
        if lv.get('boss'):
            ns = [n for n in NODES if n['lvl_id'] == lv['lvl_id']]
            if not any(n.get('anchor') for n in ns):
                chk('Boss level has an Anchor ' + lv['lvl_id'], False)
    chk('Every boss level has an Anchor (MET_FOGGATE)', all(c['result'] == 'PASS' for c in checks if c['check'].startswith('Boss level')))
    # write
    lcols = ['lvl_id', 'loc_id', 'name', 'story_name', 'kind', 'kit', 'biome', 'grid', 'x_m', 'y_m', 'z_m', 'level', 'layout', 'cell_m', 'floors', 'rooms',
             'critical_path', 'entry_anchor', 'anchors', 'gate', 'boss', 'encounters', 'enemies', 'loot_points', 'secrets', 'collectibles',
             'crit_min', 'full_min', 'shortcut', 'mood', 'light', 'music', 'ambience', 'notes']
    wr('levels.csv', LEVELS, lcols)
    ncols = ['lvl_id', 'node_id', 'seq', 'name', 'room_type', 'role', 'crit', 'zone', 'floor', 'elev_m', 'gx', 'gy', 'w_m', 'd_m', 'exits', 'traversal',
             'crit_s', 'anchor', 'secret', 'purpose', 'light', 'music', 'ambience', 'notes']
    wr('level_nodes.csv', NODES, ncols)
    wr('level_encounters.csv', ENC_OUT, ['lenc_id', 'lvl_id', 'node_id', 'src_enc', 'template', 'faction', 'level', 'actors', 'enemy_count', 'trigger',
                                          'cover_points', 'fallback_points', 'respawn', 'condition', 'notes'])
    wr('level_loot.csv', LOOT, ['loot_id', 'lvl_id', 'node_id', 'container', 'item_ref', 'qty', 'placement', 'condition', 'notes'])
    wr('level_cues.csv', CUES, ['lvl_id', 'node_id', 'cue_type', 'cue_id', 'trigger'])
    wr('vfx_env.csv', [dict(vfx_id=k, description=v, budget='Within MET_PARTICLES (30% screen in 4-player co-op)') for k, v in VFX.items()], ['vfx_id', 'description', 'budget'])
    wr('data-requests.csv', REQ, ['req_id', 'target', 'field', 'value', 'reason'])
    wr('checks.csv', checks, ['check', 'result', 'detail'])
    maps()
    sheets()
    print('moot gap m', MOOT_GAP[0], 'times', REGION_TIME)
    print('levels', len(LEVELS), 'nodes', len(NODES), 'encounters', len(ENC_OUT), 'loot', len(LOOT), 'cues', len(CUES), 'requests', len(REQ))
    for c in checks:
        print(c['result'], c['check'], c['detail'][:120])

# ================================================================ MAPS
def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace("'", '&#39;')

def maps():
    os.makedirs(OUT + '/maps', exist_ok=True)
    for lv in LEVELS:
        ns = [n for n in NODES if n['lvl_id'] == lv['lvl_id']]
        if not ns:
            continue
        if lv['kind'] == 'Region overworld':
            minx = min(n['gx'] for n in ns); miny = min(n['gy'] for n in ns)
            pos = {n['node_id']: ((n['gx'] - minx) * 30 + 40, (n['gy'] - miny) * 30 + 40) for n in ns}
            bw, bh = 110, 24
        else:
            pos = {n['node_id']: (n['gx'] * 160 + 20, n['gy'] * 70 + 40) for n in ns}
            bw, bh = 140, 40
        W_ = max(x for x, _ in pos.values()) + bw + 30
        H_ = max(y for _, y in pos.values()) + bh + 40
        out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif" font-size="10">' % (W_, H_),
               '<rect width="100%" height="100%" fill="#faf7f2"/>',
               '<text x="10" y="18" font-size="13" font-weight="bold">%s  %s (level %s)</text>' % (esc(lv['lvl_id']), esc(lv['name']), esc(lv['level']))]
        for n in ns:
            x1, y1 = pos[n['node_id']]
            for ex in (n.get('exits') or '').split(';'):
                t = ex.strip().split(' ')[0] if ex.strip() else ''
                if t in pos:
                    x2, y2 = pos[t]
                    sty = 'stroke="#2e7d32" stroke-dasharray="6 4"' if ('shortcut' in ex or 'opens' in ex) else 'stroke="#555"'
                    out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" %s stroke-width="1.5"/>' % (x1 + bw / 2, y1 + bh / 2, x2 + bw / 2, y2 + bh / 2, sty))
        for n in ns:
            x, y = pos[n['node_id']]
            fill = '#f3d9c4' if n['crit'] == 'Y' else '#e8e8e8'
            stroke = '#b71c1c' if n['role'] in ('boss', 'keeper') else '#1565c0' if n.get('anchor') else '#6d4c41' if n['role'] == 'locked' else '#888'
            out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="5" fill="%s" stroke="%s" stroke-width="2"/>' % (x, y, bw, bh, fill, stroke))
            out.append('<text x="%d" y="%d">%s %s</text>' % (x + 4, y + 13, esc(n['node_id'].split('_')[-1]), esc(n['name'][:20])))
            if bh > 30:
                tag = ' '.join(t for t in [n['role'], 'A' if n.get('anchor') else '', 'S' if n.get('secret') else '', ('%sm' % n['elev_m']) if n.get('elev_m') not in ('', 0) else ''] if t)
                out.append('<text x="%d" y="%d" fill="#555">%s</text>' % (x + 4, y + 30, esc(tag)))
        out.append('<text x="10" y="%d" fill="#555">Tan = critical path, grey = optional, blue border = Anchor, red = boss/keeper, green dashed = shortcut</text>' % (H_ - 10))
        out.append('</svg>')
        open(OUT + '/maps/%s.svg' % lv['lvl_id'], 'w').write('\n'.join(out))
    # Citadel side view
    ns = [n for n in NODES if n['lvl_id'] == CIT]
    order = [n for n in ns if n['crit'] == 'Y']
    order.sort(key=lambda n: n['seq'])
    xs = {n['node_id']: i * 70 + 40 for i, n in enumerate(order)}
    for n in ns:
        if n['crit'] == 'N':
            host = n['exits'].split()[0]
            xs[n['node_id']] = xs.get(host, 40) + 20
    ymax = 112
    yy = lambda e: 40 + (ymax - num(e)) * 4.5
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif" font-size="9">' % (len(order) * 70 + 120, int(yy(0)) + 80),
           '<rect width="100%" height="100%" fill="#faf7f2"/>', '<text x="10" y="18" font-size="13" font-weight="bold">The Briar Engine: side-view flow (x = path order, y = elevation)</text>']
    for a, b in zip(order, order[1:]):
        out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#555"/>' % (xs[a['node_id']], yy(a['elev_m']), xs[b['node_id']], yy(b['elev_m'])))
    for n in ns:
        if n.get('shortcut_to') and n['shortcut_to'] in xs:
            t = [m for m in ns if m['node_id'] == n['shortcut_to']][0]
            x1, y1, x2, y2 = xs[n['node_id']], yy(n['elev_m']), xs[t['node_id']], yy(t['elev_m'])
            out.append('<path d="M%d %d Q %d %d %d %d" fill="none" stroke="#2e7d32" stroke-dasharray="5 4" stroke-width="1.5"/>' % (x1, y1, (x1 + x2) / 2, max(y1, y2) + 60, x2, y2))
    for n in ns:
        x, y = xs[n['node_id']], yy(n['elev_m'])
        col = '#b71c1c' if n['role'] == 'boss' else '#1565c0' if n.get('anchor') else '#6d4c41' if n['crit'] == 'N' else '#e65100'
        out.append('<circle cx="%d" cy="%d" r="6" fill="%s"/>' % (x, y, col))
        out.append('<text x="%d" y="%d" transform="rotate(-35 %d %d)">%s %s</text>' % (x + 8, y - 8, x + 8, y - 8, n['node_id'][-3:], esc(n['name'])))
    out.append('<text x="10" y="%d" fill="#555">Orange = path room, blue = Anchor, red = boss, brown = optional, green dashed = shortcut</text>' % (int(yy(0)) + 60))
    out.append('</svg>')
    open(OUT + '/maps/LVL_THN_CIT_side.svg', 'w').write('\n'.join(out))

# ================================================================ SHEETS
def sheets():
    by = lambda rows: collections.defaultdict(list, {k: list(g) for k, g in __import__('itertools').groupby(sorted(rows, key=lambda r: r['lvl_id']), key=lambda r: r['lvl_id'])})
    N, E, Lt, C = by(NODES), by(ENC_OUT), by(LOOT), by(CUES)
    order = ['Region overworld', 'Citadel', 'Town']
    lv_sorted = sorted(LEVELS, key=lambda l: (order.index(l['kind']) if l['kind'] in order else 3 + (0 if l['kit'] in KIT_ROOMS else 1), l['lvl_id']))
    o = ['# Thornwood level sheets', '', 'Generated by tools/gen_levels.py from the tables in this folder. One section per level, top to bottom. '
         'IDs link to levels.csv, level_nodes.csv, level_encounters.csv, level_loot.csv and level_cues.csv. Maps are in maps/.', '']
    for lv in lv_sorted:
        o.append('## %s: %s%s' % (lv['lvl_id'], lv['name'], ' (%s)' % lv['story_name'] if lv['story_name'] else ''))
        o.append('')
        o.append('%s, level %s, %s, grid %s. %s. Critical path %s min, full clear %s min. Map: [maps/%s.svg](maps/%s.svg)' % (
            lv['kind'], lv['level'], lv['biome'], lv['grid'], lv['layout'], lv['crit_min'], lv['full_min'], lv['lvl_id'], lv['lvl_id']))
        o.append('')
        o.append('Mood: %s. Light: %s. Music: %s. Ambience: %s.%s%s' % (lv['mood'], lv['light'], lv['music'], lv['ambience'],
                 (' Gate: ' + lv['gate'] + '.') if lv['gate'] else '', (' Notes: ' + lv['notes'] + '.') if lv['notes'] else ''))
        o.append('')
        o.append('| Node | Name | Role | Size m | Elev m | Exits | Anchor/secret | Notes |')
        o.append('|---|---|---|---|---|---|---|---|')
        for n in N[lv['lvl_id']]:
            o.append('| %s | %s | %s%s | %sx%s | %s | %s | %s | %s |' % (n['node_id'].split('_')[-1], n['name'], n['role'], '' if n['crit'] == 'Y' else ' (opt)',
                     n.get('w_m', ''), n.get('d_m', ''), n.get('elev_m', ''), ', '.join(x.strip().split('_')[-1] for x in (n.get('exits') or '').split(';') if x.strip()),
                     ' '.join(x for x in [n.get('anchor', ''), n.get('secret', '')] if x), (n.get('purpose', '') + ('. ' + n['notes'] if n.get('notes') else '') + ('. ' + n['traversal'] if n.get('traversal') else '')).strip()))
        if E[lv['lvl_id']]:
            o.append('')
            o.append('Encounters: ' + '; '.join('%s %s (%s, L%s): %s' % (e['node_id'].split('_')[-1], e['template'], e['faction'], e['level'], e['actors']) for e in E[lv['lvl_id']]))
        if Lt[lv['lvl_id']]:
            o.append('')
            o.append('Loot: ' + '; '.join('%s %s %s x%s%s' % (l['node_id'].split('_')[-1], l['container'], l['item_ref'], l['qty'], (' [' + l['condition'] + ']') if l['condition'] else '') for l in Lt[lv['lvl_id']]))
        if C[lv['lvl_id']]:
            o.append('')
            o.append('Cues: ' + '; '.join('%s %s %s (%s)' % (c['node_id'].split('_')[-1], c['cue_type'], c['cue_id'], c['trigger']) for c in C[lv['lvl_id']]))
        o.append('')
    open(OUT + '/level_sheets.md', 'w').write('\n'.join(o))

if __name__ == '__main__':
    main()
