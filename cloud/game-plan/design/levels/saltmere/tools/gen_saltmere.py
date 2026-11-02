# Saltmere (REG_02) level design generator.
# Reads design/world (positions, sites, encounters, anchors, secrets), data/ (items, actors)
# and shardfall-assets.xlsx (VFX/SFX ids). Writes every Saltmere level top to bottom:
# level_index, level_nodes, level_edges, level_encounters, level_loot, level_cues, maps/*.svg, checks.csv.
# Never hand-edit the CSVs; change this script and re-run:  python3 tools/gen_saltmere.py
import csv, math, os, random, re, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = ROOT + '/design/levels/saltmere'
W = ROOT + '/design/world'
D = ROOT + '/data'
os.makedirs(OUT + '/maps', exist_ok=True)

def rd(p):
    with open(p, encoding='utf-8') as f:
        return list(csv.DictReader(f))

def wr(name, rows, cols):
    with open(f'{OUT}/{name}', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, '') for c in cols})

REG = 'REG_02'
locs = [r for r in rd(W + '/locations.csv') if r['region'] == REG]
L = {r['loc_id']: r for r in locs}
ENC = collections.defaultdict(list)
for r in rd(W + '/encounters.csv'):
    if r['region'] == REG:
        ENC[r['loc_id']].append(r)
SITES = {r['loc_id']: r for r in rd(W + '/sites.csv') if r['region'] == REG}
ANC = collections.defaultdict(list)
for r in rd(W + '/anchors.csv'):
    if r['region'] == REG:
        ANC[r['parent_loc']].append(r)
ZONES = [r for r in rd(W + '/citadel_zones.csv') if r['citadel'] == 'LOC_CIT_REG_02']
ARENA = {r['boss']: r for r in rd(W + '/boss_arenas.csv') if r['region'] == REG}
SECRET = {r['loc_id']: r for r in rd(W + '/secrets.csv') if r['region'] == REG}
LORE = collections.defaultdict(list)
for r in rd(D + '/items/lore_items.csv'):
    if r['region'] == REG:
        LORE[r['location']].append(r['item_id'])
PIECES = collections.defaultdict(list)
for r in rd(D + '/items/armor_pieces.csv'):
    PIECES[r['set_id']].append(r['item_id'])

# ---------------------------------------------------------------- known ids (for checks)
KNOWN = set()
for dp, _, fs in os.walk(D):
    for f in fs:
        if f.endswith('.csv'):
            for r in rd(os.path.join(dp, f)):
                v = list(r.values())
                if v and v[0]:
                    KNOWN.add(v[0])
for f in os.listdir(W):
    if f.endswith('.csv'):
        for r in rd(W + '/' + f):
            v = list(r.values())
            if v and v[0]:
                KNOWN.add(v[0])
AUDIO = set()
for r in rd(ROOT + '/design/audio/event_map.csv'):
    AUDIO.add(r['wwise_event'])
for f in ('music_cues.csv', 'ambience_layers.csv'):
    for r in rd(ROOT + '/design/audio/' + f):
        AUDIO.add(list(r.values())[0])

# ---------------------------------------------------------------- VFX / SFX ids from the asset sheet
VFX, SFX = {}, {}
def _xlsx_rows(path, sheet):  # stdlib fallback when openpyxl is not installed
    import zipfile, xml.etree.ElementTree as ET
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
          'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', ns):
            shared.append(''.join(t.text or '' for t in si.iter('{%s}t' % ns['m'])))
    rid = next(sh.get('{%s}id' % ns['r']) for sh in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets', ns) if sh.get('name') == sheet)
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    tgt = rels[rid].lstrip('/'); tgt = tgt if tgt.startswith('xl/') else 'xl/' + tgt
    out = []
    for row in ET.fromstring(z.read(tgt)).iter('{%s}row' % ns['m']):
        vals = {}
        for c in row.findall('m:c', ns):
            ref = re.match(r'[A-Z]+', c.get('r')).group(0); col = 0
            for ch in ref: col = col * 26 + ord(ch) - 64
            t = c.get('t'); v = c.find('m:v', ns)
            if t == 'inlineStr': val = ''.join(x.text or '' for x in c.iter('{%s}t' % ns['m']))
            elif t == 's': val = shared[int(v.text)]
            else: val = v.text if v is not None else None
            vals[col - 1] = val
        out.append(tuple(vals.get(i) for i in range(max(vals) + 1 if vals else 0)))
    return out

try:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(ROOT + '/shardfall-assets.xlsx', read_only=True)
        _sheet = lambda name: list(wb[name].iter_rows(values_only=True))
    except ImportError:
        _sheet = lambda name: _xlsx_rows(ROOT + '/shardfall-assets.xlsx', name)
    for sheet, store in (('VFX', VFX), ('SFX', SFX)):
        for r in _sheet(sheet)[1:]:
            r = tuple(r) + (None,) * 4
            store[(str(r[2]), str(r[3]))] = r[0]
except Exception as e:  # sheet unreadable: keep names, checks will flag
    print('asset sheet not read:', e)

def vx(owner, effect):
    for (o, ef), i in VFX.items():
        if owner in o and effect in ef:
            return i
    return f'MISSING_VFX({owner}/{effect})'

def sx(owner, effect):
    for (o, ef), i in SFX.items():
        if owner in o and effect in ef:
            return i
    return f'MISSING_SFX({owner}/{effect})'

V = dict(
    shard=vx('Environment', 'Shard crystal glow'), weave=vx('Environment', 'Weave threads'),
    relay=vx('Environment', 'Relay Tower activation'), reveal=vx('Environment', 'Map reveal pulse'),
    door=vx('Environment', 'Door open'), chest=vx('Environment', 'Chest open'),
    shortcut=vx('Environment', 'Shortcut unlock'), lift=vx('Environment', 'Elevator'),
    lever=vx('Environment', 'Lever pull'), wall=vx('Environment', 'Breakable wall'),
    trap=vx('Environment', 'Trap'), lore=vx('Environment', 'Lore item shimmer'),
    torch=vx('Environment', 'Torches'), water=vx('Environment', 'Waterfall'),
    steam=vx('Environment', 'Steam vents'), sparks=vx('Environment', 'Sparking wreckage'),
    holo=vx('Environment', 'Hologram terminals'), props=vx('Environment', 'Destructible props'),
    barrel=vx('Environment', 'Explosive barrel'), motes=vx('Environment', 'Dust motes'),
    birds=vx('Environment', 'Bird flocks'), rainl=vx('Sky', 'Rain light'), rainh=vx('Sky', 'Rain heavy'),
    fog=vx('Sky', 'Fog'), lightning=vx('Sky', 'Lightning'), region=vx('R2 Saltmere', 'Region signature'),
    ostra_map=vx('Ostra', 'Map fill-in'), ostra_in=vx('Ostra', 'Hologram appear'),
    hollow=vx('Environment', 'Hollowing upward'), quiet=vx('Environment', 'The Quiet in the sky'),
    glow={'Common': vx('Environment', 'Loot glow Common'), 'Forged': vx('Environment', 'Loot glow Forged'),
          'Rare': vx('Environment', 'Loot glow Rare'), 'Relic': vx('Environment', 'Loot glow Relic'),
          'Shardborn': vx('Environment', 'Loot glow Shardborn')},
    skim_wake=vx('Skimmer', 'Dust / water wake'), flyer_hijack=vx('Enemy flyer', 'Hijack sparks'),
)
S = dict(
    wood=sx('Environment', 'Door open/close wood'), metal=sx('Environment', 'Door open/close metal'),
    hatch=sx('Environment', 'Ship hatch'), chest=sx('Environment', 'Chest open'),
    shortcut=sx('Environment', 'Shortcut unlock'), lift=sx('Environment', 'Lift'),
    lever=sx('Environment', 'Lever'), wall=sx('Environment', 'Breakable wall'),
    illusory=sx('Environment', 'Illusory wall'), trap=sx('Environment', 'Traps'),
    pickup=sx('Environment', 'Item pickup'), lore=sx('Environment', 'Lore item pickup'),
    relay=sx('Environment', 'Relay Tower'), hum=sx('Environment', 'Shard hum'),
    fire=sx('Environment', 'Fire loop'), water=sx('Environment', 'Water stream'),
    steam=sx('Environment', 'Steam vent'), sparks=sx('Environment', 'Sparks'),
    terminal=sx('Environment', 'Terminal beep'), barrel=sx('Environment', 'Explosive barrel'),
    rainl=sx('Sky', 'Rain light'), rainh=sx('Sky', 'Rain heavy'), rainsurf=sx('Sky', 'Rain on surfaces'),
    thunder=sx('Sky', 'Thunder'), wind=sx('Sky', 'Wind'),
)

# ---------------------------------------------------------------- tables we fill
LEVELS, NODES, EDGES, ENCS, LOOT, CUES, CHECKS = [], [], [], [], [], [], []
NODE_BY_LVL = collections.defaultdict(list)
_n = collections.Counter()

def lvl_code(loc_id):
    return loc_id.replace('LOC_', '').replace('_REG_02', '')

def node(lvl, name, role, floor=0, gx=0, gy=0, size='12x12x5', space='CQ', cover='0/0',
         water='Dry', light='', mood='', anchor='', notes='', key=None):
    _n[lvl] += 1
    nid = f'LN_{lvl_code(lvl)}_{_n[lvl]:02d}'
    row = dict(node_id=nid, loc_id=lvl, order=_n[lvl], name=name, role=role, floor=floor, gx=gx, gy=gy,
               size_m=size, space=space, cover_low_high=cover, water=water, lighting=light, mood=mood,
               anchor=anchor, notes=notes, key=key or name)
    NODES.append(row)
    NODE_BY_LVL[lvl].append(row)
    return nid

def edge(lvl, a, b, kind='Walk', length=15, critical='Yes', gate='', notes=''):
    eid = f'LE_{lvl_code(lvl)}_{sum(1 for e in EDGES if e["loc_id"] == lvl) + 1:02d}'
    EDGES.append(dict(edge_id=eid, loc_id=lvl, from_node=a, to_node=b, type=kind, length_m=length,
                      critical=critical, gate=gate, notes=notes))
    return eid

_e = collections.Counter()
def enc(lvl, nid, template, faction, level, actors, trigger, world='', cover='', fallback='',
        respawn='On Anchor rest', intent='', cond=''):
    _e[lvl] += 1
    ENCS.append(dict(lenc_id=f'LENC_{lvl_code(lvl)}_{_e[lvl]:02d}', loc_id=lvl, node_id=nid, world_enc=world,
                     template=template, faction=faction, level=level, actors=actors,
                     enemy_count=sum(int(m) for m in re.findall(r' x(\d+)', actors)), trigger=trigger,
                     cover_points=cover, fallback_points=fallback, respawn=respawn, intent=intent, condition=cond))

_l = collections.Counter()
def loot(lvl, nid, container, item, qty='1', vis='Off path', rarity='', notes='', src=''):
    _l[lvl] += 1
    LOOT.append(dict(loot_id=f'LL_{lvl_code(lvl)}_{_l[lvl]:02d}', loc_id=lvl, node_id=nid, container=container,
                     item=item, qty=qty, visibility=vis, rarity=rarity, source_loc=src, notes=notes))

_c = collections.Counter()
def cue(lvl, nid, trigger, music='', amb='', sfx='', vfx='', light='', notes=''):
    _c[lvl] += 1
    CUES.append(dict(cue_id=f'LC_{lvl_code(lvl)}_{_c[lvl]:02d}', loc_id=lvl, node_id=nid, trigger=trigger,
                     music=music, ambience=amb, sfx=sfx, vfx=vfx, lighting=light, notes=notes))

def level(loc_id, kind, name, layout, crit, first_min, full_min, traversal, mood, light, music, amb,
          notes='', quest='', gate=''):
    r = L.get(loc_id, {})
    LEVELS.append(dict(loc_id=loc_id, kind=kind, name=name, biome=r.get('biome', ''), level=r.get('level', ''),
                       x_m=r.get('x_m', ''), y_m=r.get('y_m', ''), z_m=r.get('z_m', ''), grid=r.get('grid', ''),
                       layout=layout, critical_path=crit, first_play_min=first_min, completion_min=full_min,
                       traversal=traversal, mood=mood, lighting=light, music=music, ambience=amb,
                       quest_hooks=quest, gate=gate or r.get('gate', ''), notes=notes))

def rng(key):
    return random.Random(key)

# ---------------------------------------------------------------- actors
VARIANT = {('FAC_HOLLOWED', 'FODDER'): 'ACT_VAR_R2_01', ('FAC_REMNANT', 'FODDER'): 'ACT_VAR_R2_02',
           ('FAC_THORN', 'FODDER'): 'ACT_VAR_R2_03', ('FAC_HOLLOWED', 'SKIRMISHER'): 'ACT_VAR_R2_04',
           ('FAC_REMNANT', 'SKIRMISHER'): 'ACT_VAR_R2_05', ('FAC_THORN', 'SKIRMISHER'): 'ACT_VAR_R2_06'}
TPL = {r['template']: r for r in rd(W + '/encounter_templates.csv')}
BIOME_FAC = {'Flooded salt flats': [('FAC_THORN', 45), ('FAC_HOLLOWED', 35), ('FAC_REMNANT', 20)],
             'Cargo-deck shallows': [('FAC_REMNANT', 60), ('FAC_HOLLOWED', 25), ('FAC_THORN', 15)],
             'Storm cliffs': [('FAC_REMNANT', 45), ('FAC_HOLLOWED', 35), ('FAC_THORN', 20)]}
BIOME_CRT = {'Flooded salt flats': (['ACT_CRT_HULLCRAB', 'ACT_CRT_SHARDRATSWARM'], ['ACT_CRT_SALTSERPENT']),
             'Cargo-deck shallows': (['ACT_CRT_HULLCRAB', 'ACT_CRT_RUSTBEETLE', 'ACT_CRT_SHARDRATSWARM'], ['ACT_CRT_SALTSERPENT', 'ACT_CRT_STORMRAY']),
             'Storm cliffs': (['ACT_CRT_RUSTBEETLE', 'ACT_CRT_SHARDRATSWARM'], ['ACT_CRT_CLIFFROC', 'ACT_CRT_STORMRAY'])}

def pick_fac(biome, key):
    opts = BIOME_FAC.get(biome, BIOME_FAC['Flooded salt flats'])
    x = rng(key).uniform(0, 100)
    for f, w in opts:
        x -= w
        if x <= 0:
            return f
    return opts[0][0]

def actors_for(template, fac, biome, key):
    r = rng(key)
    if template == 'ENT_CRT_PACK':
        return f'{r.choice(BIOME_CRT[biome][0])} x{r.choice([3, 4])}'
    if template == 'ENT_CRT_SOLO':
        return f'{r.choice(BIOME_CRT[biome][1])} x1'
    out = []
    short = fac.replace('FAC_', '')
    for part in TPL[template]['roles'].split(';'):
        role, n = part.strip().rsplit(' x', 1)
        n = int(n)
        var = VARIANT.get((fac, role))
        if var and n >= 2:
            out += [f'ACT_{short}_{role} x{n - n // 2}', f'{var} x{n // 2}']
        elif var:
            out.append(f'{var} x{n}')
        else:
            out.append(f'ACT_{short}_{role} x{n}')
    return '; '.join(out)

def new_enc(lvl, nid, template, trigger, intent='', fac=None, cond='', respawn=None, level_=None):
    loc = L.get(lvl, {})
    biome = loc.get('biome', 'Flooded salt flats')
    lv = level_ or re.sub(r'-.*', '', loc.get('level', '14') or '14')
    key = f'{lvl}{nid}{template}'
    if template.startswith('ENT_CRT'):
        fac = ''
    else:
        fac = fac or pick_fac(biome, key)
    t = TPL[template]
    enc(lvl, nid, template, fac, lv, actors_for(template, fac, biome, key), trigger,
        cover=t['cover_points'], fallback=t['fallback_points'], respawn=respawn or t['respawn'],
        intent=intent, cond=cond)

def world_enc(lvl, nid, e, trigger, intent=''):
    enc(lvl, nid, e['template'], e['faction'], e['level'], e['actors'], trigger, world=e['enc_id'],
        cover=e['cover_points'], fallback=e['fallback_points'], respawn=e['respawn'], intent=intent,
        cond=e.get('condition', ''))

# ---------------------------------------------------------------- lighting and mood presets (design choices)
EXT = 'LGT_REG_02_* (time of day); PPV_REG_02'
LIGHT = {
    'wreck': 'Interior: cyan Shard-lamp key 6,500 K at 120-180 lux, red emergency strips 2,000 K at 15 lux, dark pockets under 5 lux',
    'flooded': 'Interior: daylight shafts through hull breaches 5,500 K at 400 lux on the water, caustics on ceilings, water-line glow 40 lux',
    'cave': 'Interior: bioluminescent salt crust 7,000 K at 30 lux, torch pools 2,200 K at 200 lux, entrance spill 5,000 K',
    'tower': 'Interior: storm light through slit windows 7,000 K at 250 lux, brazier pools 2,100 K, lightning flashes every 8-20 s at the top',
    'fort': 'Exterior court lit by LGT_REG_02_*; interiors oil lanterns 2,400 K at 150 lux; watchfires 1,900 K',
    'smuggler': 'Interior: hooded lanterns 2,300 K at 120 lux, moonlit sea door 4,100 K, dark water under 5 lux',
    'choir': 'Interior: Choir-glass refracting violet-cyan 8,000 K at 80 lux, tone pillars pulse 0.5 Hz, no warm light',
    'citadel': 'Mixed: storm exterior (LGT_REG_02_STORM forced during MQ_A1_08), chapel candle banks 2,000 K, Shard-lamp cyan in the ark decks',
    'town': EXT + '; lanterns on stilts 2,300 K at dusk and night, market awnings tint daylight teal',
}
MOOD = {
    'wreck': 'Claustrophobic, creaking, things moving behind bulkheads',
    'flooded': 'Cold, quiet, chest-deep water slows everything; dread of what is under the surface',
    'cave': 'Salt-white glitter, dripping, echoing surf',
    'tower': 'Exposed, wind-blasted, a climb toward the storm',
    'fort': 'Watchful, fortified, raider banners snapping in the wind',
    'smuggler': 'Secretive, lamp-lit, the sea breathing through the rock',
    'choir': 'Holy and wrong; a hymn just below hearing',
}

# ---------------------------------------------------------------- loot helpers
LOOT_KINDS = ('Small chest', 'Shard crate', 'Lore site', 'Gather node')
def loot_item(loc):
    k = loc['kind']
    if k == 'Small chest':
        return 'ITM_LT_SMALLCHEST_REG_02', 'Common'
    if k == 'Shard crate':
        return 'ITM_LT_SHARDCRATE_REG_02', 'Common'
    if k == 'Gather node':
        t = loc['loc_id'][len('LOC_NODE_'):].rsplit('_REG_', 1)[0]
        return 'ITM_LT_NODE_' + t, 'Common'
    return '', ''

def dist(a, b):
    return math.hypot(float(a['x_m']) - float(b['x_m']), float(a['y_m']) - float(b['y_m']))

# ---------------------------------------------------------------- generic graph helpers
def snake(i, step=2, row=4):
    r, c = divmod(i, row)
    return (c if r % 2 == 0 else row - 1 - c) * step, r * step

def place_world_loot(lvl, nodes_pref):
    """Put the world thread's chests, crates, lore sites and gather nodes of this level onto nodes."""
    kids = [l for l in locs if l['parent_loc'] == lvl and l['kind'] in LOOT_KINDS]
    kids += FIELD_ASSIGN.get(lvl, [])
    for i, k in enumerate(kids):
        nid = nodes_pref[i % len(nodes_pref)]
        if k['kind'] == 'Lore site':
            for it in LORE.get(k['loc_id'], []):
                loot(lvl, nid, 'Lore item', it, vis='Off path', rarity='Lore', src=k['loc_id'])
            if not LORE.get(k['loc_id']):
                loot(lvl, nid, 'Lore site', 'none (story set dressing)', vis='Off path', src=k['loc_id'])
        else:
            it, rar = loot_item(k)
            loot(lvl, nid, k['kind'], it, vis='Off path' if k['kind'] != 'Gather node' else 'Visible',
                 rarity=rar, src=k['loc_id'])

# Field loot (no parent): attach to the nearest level within 160 m, otherwise to the open field
LEVEL_KINDS = ('Site', 'Choir vault', 'Choir site', 'POI', 'Landmark', 'Settlement', 'Relay Tower',
               'Field boss', 'Connection', 'Undervault entry')
LEVEL_LOCS = [l for l in locs if l['kind'] in LEVEL_KINDS]
FIELD_ASSIGN = collections.defaultdict(list)
for l in locs:
    if l['kind'] in LOOT_KINDS and not l['parent_loc']:
        best = min(LEVEL_LOCS, key=lambda m: dist(l, m))
        FIELD_ASSIGN[best['loc_id'] if dist(l, best) <= 160 else 'REG_02'].append(l)

def secret_nodes(lvl, host_nodes):
    """Secrets the world thread put at this level become secret nodes off a host node."""
    out = []
    for s in [l for l in locs if l['kind'] == 'Secret' and l['parent_loc'] == lvl]:
        meta = SECRET.get(s['loc_id'], {})
        host = host_nodes[len(out) % len(host_nodes)]
        nid = node(lvl, f'Secret: {meta.get("secret_type", "secret")}', 'Secret', size='6x6x4', space='CQ',
                   notes=f'{s["loc_id"]}; hint: {meta.get("hint", "")}; needs: {meta.get("requirement", "") or "nothing"}')
        kind = {'Illusory wall': 'Illusory wall', 'Breakable floor': 'Drop (breakable floor)',
                'Hidden ledge path': 'Ledge path', 'Rooftop route': 'Climb (cables)',
                'Vehicle jump': 'Vehicle jump', 'Sunken chest': 'Swim', 'Resonance gate': 'Resonance gate',
                'Hidden merchant': 'Hidden path', 'Night-only event': 'Timed (20:00-04:00)',
                'Shard-note cache': 'Hidden path', 'Echo duel': 'Walk'}.get(meta.get('secret_type', ''), 'Hidden path')
        edge(lvl, host, nid, kind, 8, 'No', meta.get('requirement', ''), meta.get('hint', ''))
        rew = meta.get('reward', '')
        items = re.findall(r'ITM_[A-Z0-9_]+', rew)
        if items:
            for it in items:
                q = re.search(it + r' x(\d+)', rew)
                loot(lvl, nid, 'Secret cache', it, q.group(1) if q else '1', 'Secret', src=s['loc_id'])
        elif 'Region loot table chest' in rew:
            loot(lvl, nid, 'Secret chest', 'ITM_LT_VAULT_REG_02', vis='Secret', rarity='Rare', src=s['loc_id'])
        elif 'Lore item and Shard Dust' in rew:
            loot(lvl, nid, 'Secret cache', 'ITM_MAT_DUST_01', '5', 'Secret', src=s['loc_id'])
        elif 'Unique site reward pool' in rew:
            loot(lvl, nid, 'Secret chest', 'ITM_LT_ARTS', vis='Secret', rarity='Rare', src=s['loc_id'],
                 notes='Site reward pool = weapon art table')
        elif 'Hidden stock' in rew:
            loot(lvl, nid, 'Hidden merchant', 'ITM_LT_ARTS', vis='Secret', src=s['loc_id'], notes=rew)
        if meta.get('secret_type') == 'Illusory wall':
            cue(lvl, nid, 'Wall struck', sfx=S['illusory'], vfx=V['wall'])
        elif meta.get('secret_type') == 'Breakable floor':
            cue(lvl, nid, 'Floor broken', sfx=S['wall'], vfx=V['wall'])
        else:
            cue(lvl, nid, 'Secret found', music='Play_MUS_SAL_DISCOVERY', vfx=V['lore'])
        out.append(nid)
    return out

def anchor_of(lvl, kind=None):
    a = [x for x in ANC.get(lvl, []) if kind is None or x['anchor_type'] == kind]
    return a[0]['loc_id'] if a else ''

def ext_cues(lvl, nid, biome, storm=False):
    cue(lvl, nid, 'Exterior weather (Weather state)', amb='AMB_SAL_WEATHER',
        sfx=f'{S["rainl"]} {S["rainh"]} {S["thunder"]}', vfx=f'{V["rainl"]} {V["rainh"]} {V["region"]}' +
        (f' {V["lightning"]}' if storm or biome == 'Storm cliffs' else ''), light=EXT,
        notes='Storms on 30% of game days (world regions_layout)')

# =================================================================== CITADEL: The Drowned Hold
CIT = 'LOC_CIT_REG_02'
# Rooms per zone, keyed by the world zone NAME so a re-ordered citadel_zones.csv still works.
# (name, role, size, space, cover low/high, water, notes). Anchors, doors, shortcuts and order come from citadel_zones.csv.
CIT_PLAN = {
 'Causeway Locks': [('Causeway Head', 'Entry', '20x40x0', 'MID', '4/2', 'Wade', 'First sight of the Hold: the beached flagship hull rising behind the chapel spire'),
        ('Lock Gate One', 'Combat', '24x30x8', 'MID', '6/3', 'Wade', 'Gun line on the lock wall; low cover in the tide channel; flank via the sluice catwalk'),
        ('Sluice Catwalk', 'Traversal', '4x40x3', 'CQ', '0/2', 'Dry', 'Optional flank 4 m wide; ambush drops from the lock housing'),
        ('Lock Gate Two', 'Combat', '24x30x8', 'CQ', '4/4', 'Wade', 'Tide channel floods to swim depth during storms'),
        ('Winch House', 'Loot', '10x10x5', 'CQ', '0/0', 'Dry', 'Small chest; the winch is broken here and is repaired from the next zone (shortcut)')],
 'Floodgate Yard': [('Floodgate Stair', 'Traversal', '8x30x22', 'CQ', '0/2', 'Dry', 'Switchback stair up the floodgate face, 3 landings'),
        ('Gatekeeper Landing', 'Combat', '18x18x6', 'CQ', '2/3', 'Dry', 'Shield wall holds the landing; artillery on the gate top'),
        ('Barbican Yard', 'Combat', '30x30x10', 'MID', '6/4', 'Dry', 'Fortified line; explosive barrels by the gun port'),
        ('Barbican Winch', 'Shortcut', '8x8x6', 'CQ', '0/0', 'Dry', 'Turn the winch'),
        ('Locked Bell Store', 'Locked', '8x10x5', 'CQ', '0/0', 'Dry', 'Bulkhead Guard piece')],
 'Cantor\'s Nave': [('Chapel Antechamber', 'Entry', '12x16x8', 'CQ', '0/0', 'Wade', 'Anchor before the fog gate; the lift back starts here'),
        ('Cantor\'s Nave (the Drowned Chapel)', 'Boss', '48x48x20', 'MID', '0/4', 'Wade', 'Half-flooded nave; pillars break line of sight'),
        ('Choir Loft', 'Reward', '10x14x6', 'CQ', '0/0', 'Dry', 'Corsa\'s signal codes (MQ_A1_07); Cantor first-kill Shardborn')],
 'Mast Gallery': [('Mast Foot', 'Traversal', '16x16x30', 'MID', '2/2', 'Dry', 'Climb the fallen mast; cables count as climbable'),
        ('Rigging Walk', 'Combat', '6x50x2', 'MID', '0/3', 'Dry', 'Drones on the yardarms; falls over 18 m are lethal'),
        ('Crow\'s Nest', 'Loot', '8x8x4', 'LONG', '0/0', 'Dry', 'Sniper perch; Rare chest'),
        ('Mast Gallery Hall', 'Combat', '20x40x12', 'MID', '6/4', 'Dry', 'Gun line with shield-bearers'),
        ('Gallery One-Way Door', 'Shortcut', '4x4x4', 'CQ', '0/0', 'Dry', 'One-way door and rope drop'),
        ('Mooring Watch Locker', 'Locked', '8x8x4', 'CQ', '0/0', 'Dry', 'Mooring Watch piece')],
 'Bilge Market': [('Bilge Market Gate', 'Entry', '12x12x6', 'CQ', '0/2', 'Dry', 'Stalls of the drowned market still stocked'),
        ('Long Gallery', 'Combat', '12x80x10', 'LONG', '8/4', 'Dry', 'Gun gallery 40-80 m; cover every 10 m; melee route under the floor'),
        ('Under-Gallery Crawl', 'Traversal', '4x60x3', 'CQ', '0/4', 'Wade', 'Melee and stealth alternative; shard-rat swarms'),
        ('Fishmonger Row', 'Combat', '20x30x6', 'MID', '4/6', 'Dry', 'Horde in the stalls; leader on the scale platform'),
        ('Ladder Drop', 'Shortcut', '4x4x14', 'CQ', '0/0', 'Dry', 'Kick-down ladder and chain gate')],
 'Ballast Deep': [('Ballast Stair', 'Traversal', '6x20x18', 'CQ', '0/0', 'Wade', 'Down into the flagship\'s ballast; water rises with each landing'),
        ('Ballast Tank One', 'Combat', '20x20x8', 'CQ', '0/4', 'Swim', 'Swim depth; no attacks while swimming; enemies on the gantries'),
        ('Pump Control', 'Puzzle', '10x10x5', 'CQ', '0/0', 'Dry', 'Drain tank two by running 3 valves in order'),
        ('Ballast Tank Two', 'Combat', '20x30x8', 'CQ', '2/4', 'Wade', 'Drained; Hollowed nest in the silt'),
        ('Plank Drop', 'Shortcut', '4x4x10', 'CQ', '0/0', 'Dry', 'Drop-down plank and flooded tunnel'),
        ('Ballast Strongroom', 'Locked', '8x8x4', 'CQ', '0/0', 'Dry', 'Locked strongroom')],
 'Admiralty Decks': [('Admiralty Lift', 'Traversal', '8x8x30', 'CQ', '0/0', 'Dry', 'Lift through the hull'),
        ('Officers\' Deck', 'Combat', '30x20x6', 'MID', '6/4', 'Dry', 'Officers; leader is a drowned lieutenant'),
        ('Chart Room', 'Loot', '10x10x4', 'CQ', '0/0', 'Dry', 'Map table; lore items'),
        ('Upper Bridge', 'Combat', '24x24x8', 'MID', '4/4', 'Dry', 'Elite heavy at the helm; storm through the broken glass'),
        ('Bridge Lowering', 'Shortcut', '6x30x0', 'CQ', '0/0', 'Dry', 'Lower the bridge: the big loop of the Citadel'),
        ('Admiral\'s Cabin', 'Locked', '10x8x4', 'CQ', '0/0', 'Dry', 'Locked cabin')],
 'The Storm Deck': [('Storm Stair', 'Entry', '10x20x16', 'MID', '0/2', 'Dry', 'Anchor before the fog gate'),
        ('The Storm Deck', 'Boss', '60x60x0', 'MID', '0/5', 'Wade', 'Corsa on the beached ark deck in a forced storm; hull chunks for cover; Strider not allowed'),
        ('Admiral\'s Seat', 'Reward', '10x10x6', 'CQ', '0/0', 'Dry', 'Heart Shard choice 2; elevator to the exit')],
}
ZONES.sort(key=lambda z: int(z['order']))
cit_min = sum(int(z['path_min']) for z in ZONES)
cit_nodes, zfirst, zrows = {}, {}, {}
prev_last = None
for zi, zone in enumerate(ZONES):
    zn, zid = zone['name'], zone['loc_id']
    plan = CIT_PLAN.get(zn) or [(zn + ' Entry', 'Entry', '20x20x6', 'MID', '2/2', 'Dry', 'Generic zone (no hand plan)'),
                                (zn + ' Fight', 'Combat', '24x24x8', 'MID', '4/4', 'Dry', '')]
    ids = []
    for i, (nm, role, size, space, cover, water, notes) in enumerate(plan):
        anc = zone['anchor'] if i == 0 else ''
        extra = ''
        if role == 'Shortcut':
            extra = '; shortcut: ' + zone['shortcut']
        if role == 'Locked':
            if not zone['locked_door']:
                continue
            extra = f'; {zone["locked_door"]} needs {L.get(zone["locked_door"], {}).get("gate", "").replace("Key ", "")}'
        nid = node(CIT, nm, role, floor=zi, gx=i * 3, gy=zi * 3, size=size, space=space, cover=cover, water=water,
                   light=LIGHT['citadel'], mood=zone['style'], anchor=anc,
                   notes=f'{zid} {zn}; {notes}{extra}', key=f'{zn}:{nm}')
        ids.append((nid, role, water))
        cit_nodes[f'{zn}:{nm}'] = nid
    zfirst[zid[-2:]] = ids[0][0]
    zrows[zid] = ids
    main = [n for n, r, w in ids if r not in ('Shortcut', 'Locked', 'Loot')]
    if prev_last:
        edge(CIT, prev_last, main[0], 'Stair' if zi % 2 else 'Door', 20, 'Yes', notes=f'Into {zn}')
    for a, b in zip(main, main[1:]):
        edge(CIT, a, b, 'Fog gate' if any(x == b and r == 'Boss' for x, r, w in ids) else
             ('Door (opens on boss death)' if any(x == b and r == 'Reward' for x, r, w in ids) else 'Walk'), 20)
    for n, r, w in ids:
        if r == 'Loot':
            edge(CIT, main[min(1, len(main) - 1)], n, 'Door', 10, 'No')
        if r == 'Locked':
            edge(CIT, main[-1], n, 'Locked door', 6, 'No', zone['locked_door'])
            loot(CIT, n, 'Locked room chest', 'ITM_LT_VAULT_REG_02', vis='Locked', rarity='Rare', src=zone['locked_door'])
        if r == 'Shortcut':
            edge(CIT, main[-1], n, 'Walk', 8, 'No')
    prev_last = main[-1]
    combat = [n for n, r, w in ids if r in ('Combat', 'Traversal')] or [n for n, r, w in ids]
    for k, wid in enumerate(zone['encounters'].split()):
        e = next(x for x in ENC[zid] if x['enc_id'] == wid)
        world_enc(CIT, combat[k % len(combat)], e, 'Enter node (12 m volume) or line of sight', zone['style'])
    if not zone['boss']:
        extra = {'Melee close quarters': 'ENT_AMBUSH', 'Vertical climb': 'ENT_AMBUSH', 'Gun gallery (40-80 m sightlines)': 'ENT_GUNLINE',
                 'Boss approach': 'ENT_ELITE'}.get(zone['style'], 'ENT_AMBUSH')
        new_enc(CIT, combat[-1], extra, 'Enter node', 'Added for Citadel density (design choice)', level_=zone['level'])
        if zone['style'] in ('Melee close quarters', 'Gun gallery (40-80 m sightlines)'):
            new_enc(CIT, combat[0], 'ENT_HORDE', 'Enter node', 'Hollowed overflow; tests crowd tools', fac='FAC_HOLLOWED', level_=zone['level'])
    first = ids[0][0]
    cue(CIT, first, f'Enter {zn}', music='MUS_SAL_CITADEL' if not zone['boss'] else '', amb='AMB_SAL_CITADEL', light=LIGHT['citadel'])
    if zone['anchor']:
        cue(CIT, first, 'Anchor lit', music='Play_MUS_STG_ANCHOR_LIT', sfx=S['hum'], vfx=V['shard'], notes=zone['anchor'])
    for n, r, w in ids:
        if r == 'Loot':
            cue(CIT, n, 'Chest opened', sfx=S['chest'], vfx=V['chest'])
        if r == 'Combat' and w != 'Dry':
            cue(CIT, n, 'Wading', sfx=S['water'], vfx=V['water'])
        if r == 'Puzzle':
            cue(CIT, n, 'Valves turned', sfx=S['lever'] + ' ' + S['steam'], vfx=V['steam'])
# shortcuts: parse "Zn" targets from each zone's world shortcut text
for zone in ZONES:
    ids = zrows[zone['loc_id']]
    src = next((n for n, r, w in ids if r == 'Shortcut'), None)
    if not src:
        src = ids[0][0] if 'antechamber' in zone['shortcut'] else next((n for n, r, w in ids if r == 'Reward'), ids[-1][0])
    targets = re.findall(r'Z(\d)', zone['shortcut'])
    if 'exit' in zone['shortcut'] and not targets:
        targets = ['1']
    for t in dict.fromkeys(targets):
        if f'Z{t}' == zone['loc_id'][-2:]:
            continue
        part = next((p for p in re.split(r'[;,]', zone['shortcut']) if f'Z{t}' in p), zone['shortcut']).strip()
        edge(CIT, src, zfirst[f'Z{t}'], 'Shortcut: ' + part, 0, 'No', notes='Opens from the far side only')
    if 'field' in zone['shortcut']:
        edge(CIT, src, ids[0][0], 'Shortcut: ' + zone['shortcut'].split(';')[-1].strip(), 0, 'No', notes='Exit to the open field')
    cue(CIT, src, 'Shortcut opened', sfx=S['shortcut'] + ' ' + (S['lift'] if re.search('Lift|lift|Elevator|elevator', zone['shortcut']) else S['lever']),
        vfx=V['shortcut'], notes=zone['shortcut'])
def cn(key):
    return cit_nodes.get(key)
for a, b, k, crit in (('Causeway Locks:Lock Gate One', 'Causeway Locks:Sluice Catwalk', 'Walk', 'Flank route'),
                      ('Bilge Market:Long Gallery', 'Bilge Market:Under-Gallery Crawl', 'Drop', 'Melee route under the gallery'),
                      ('Bilge Market:Under-Gallery Crawl', 'Bilge Market:Fishmonger Row', 'Ladder', '')):
    if cn(a) and cn(b):
        edge(CIT, cn(a), cn(b), k, 6, 'No', notes=crit)
bosses = [z for z in ZONES if z['boss']]
LEVEL_QUEST = []
for z in bosses:
    boss = z['boss']
    ids = zrows[z['loc_id']]
    bn = next(n for n, r, w in ids if r == 'Boss')
    a = ARENA[boss]
    lt = {'ACT_BOSS_CANTOR': 'ITM_LT_BOSS_08', 'ACT_BOSS_CORSA': 'ITM_LT_BOSS_02'}[boss]
    shb = {'ACT_BOSS_CANTOR': 'ITM_SHB_A02', 'ACT_BOSS_CORSA': 'ITM_SHB_W02'}[boss]
    enc(CIT, bn, 'BOSS', '', a['level'], f'{boss} x1', 'Cross the fog gate', cover=a['cover_pieces'], fallback='0',
        respawn='Never', intent=f'{a["shape"]} {a["diameter_m"]} m; {a["phase_change"]}; {a["hazards"]}')
    loot(CIT, bn, 'Boss drop', lt, vis='Critical', rarity='Boss', notes='Boss loot table')
    loot(CIT, bn, 'Boss drop (first kill)', shb, vis='Critical', rarity='Shardborn')
    nm = 'CORSA' if 'CORSA' in boss else 'CANTOR'
    owner = 'Corsa' if nm == 'CORSA' else 'Drowned Cantor'
    sxn = 'ShardBearerCorsaStormAdmiral' if nm == 'CORSA' else 'CitadelTheDrownedCantor'
    cue(CIT, bn, 'Fog gate crossed', music=f'Play_MUS_BOSS_{nm}_INTRO Play_MUS_BOSS_{nm}_P1', sfx=f'Play_SFX_Bosses_{sxn}_IntroSting',
        vfx=f'{vx(owner, "Arena barrier")} {vx(owner, "Intro")}')
    cue(CIT, bn, 'Phase 2', music=f'Play_MUS_BOSS_{nm}_T2 Play_MUS_BOSS_{nm}_P2', sfx=f'Play_SFX_Bosses_{sxn}_PhaseTransition',
        vfx=f'{vx(owner, "Phase transition")} {vx(owner, "Phase 2 aura")}')
    if nm == 'CORSA':
        cue(CIT, bn, 'Phase 3', music='Play_MUS_BOSS_CORSA_T3 Play_MUS_BOSS_CORSA_P3', sfx=S['thunder'], vfx=V['lightning'] + ' ' + V['rainh'],
            light='LGT_REG_02_STORM forced; lightning every 6 s', notes='Heavy rain forced for the fight')
    cue(CIT, bn, 'Boss defeated', music=f'Play_MUS_BOSS_{nm}_WIN', sfx=f'Play_SFX_Bosses_{sxn}_Death',
        vfx=f'{vx(owner, "Death")} {vx(owner, "Shard / Resonance release") if nm == "CORSA" else vx(owner, "Reward drop")}')
    LEVEL_QUEST.append(f'{"MQ_A1_07 The Drowned Chapel" if nm == "CANTOR" else "MQ_A1_08 The Beached Ark"} ends in {z["loc_id"][-2:]}')
if cn("Cantor's Nave:Choir Loft"):
    loot(CIT, cn("Cantor's Nave:Choir Loft"), 'Quest item', "Corsa's signal codes (MQ_A1_07; needs an ITM_ id, DR-SAL-04)", vis='Critical')
for k, it in (('Causeway Locks:Winch House', 'ITM_LT_SMALLCHEST_REG_02'), ("Mast Gallery:Crow's Nest", 'ITM_LT_VAULT_REG_02'),
              ('Admiralty Decks:Chart Room', 'ITM_LT_SMALLCHEST_REG_02')):
    if cn(k):
        loot(CIT, cn(k), 'Chest', it, vis='Off path', rarity='Rare' if 'VAULT' in it else 'Common')
for k, it in zip(['Floodgate Yard:Locked Bell Store', 'Bilge Market:Fishmonger Row', 'Mast Gallery:Mast Gallery Hall', 'Bilge Market:Long Gallery'], PIECES['ITM_SET_42']):
    if cn(k):
        loot(CIT, cn(k), 'Armor stand', it, vis='Off path', rarity='Rare', notes='Bulkhead Guard set (found), design choice')
for k, it in zip(['Mast Gallery:Mooring Watch Locker', 'Admiralty Decks:Chart Room', "Admiralty Decks:Officers' Deck", 'Ballast Deep:Ballast Tank Two'], PIECES['ITM_SET_43']):
    if cn(k):
        loot(CIT, cn(k), 'Armor stand', it, vis='Off path', rarity='Rare', notes='Mooring Watch set (found), design choice')
for k, it in (('Floodgate Yard:Barbican Yard', 'ITM_ART_10'), ('Ballast Deep:Ballast Tank One', 'ITM_ART_13')):
    if cn(k):
        loot(CIT, cn(k), 'Pedestal', it, vis='Off path', rarity='Rare', notes='Weapon art (found copy), design choice')
if cn('Bilge Market:Bilge Market Gate'):
    loot(CIT, cn('Bilge Market:Bilge Market Gate'), 'Hidden stall', 'ITM_LT_CONSUMABLE', '2', 'Off path')
for host, typ, rew in (('Causeway Locks:Sluice Catwalk', 'Illusory wall behind the sluice wheel', PIECES['ITM_SET_44'][0]),
                       ("Mast Gallery:Crow's Nest", 'Hidden ledge path along the hull stencils', 'ITM_MAT_STAR_01'),
                       ('Ballast Deep:Ballast Tank One', 'Sunken chest at the tank floor (swim)', PIECES['ITM_SET_44'][1]),
                       ('Admiralty Decks:Upper Bridge', 'Breakable floor under the helm', 'ITM_LT_ARTS')):
    if not cn(host):
        continue
    sn = node(CIT, 'Secret: ' + typ, 'Secret', size='6x6x4', notes='Citadel-only secret (design choice)')
    edge(CIT, cn(host), sn, 'Secret', 8, 'No')
    loot(CIT, sn, 'Secret cache', rew, vis='Secret', rarity='Relic' if 'SET_44' in rew else 'Rare')
    cue(CIT, sn, 'Secret found', music='Play_MUS_SAL_DISCOVERY', sfx=S['illusory'] if 'Illusory' in typ else S['wall'], vfx=V['wall'])
level(CIT, 'Citadel', 'The Drowned Hold (its nave is the campaign\'s Drowned Chapel)',
      f'Side-view node graph, {len(ZONES)} zones, {len(NODE_BY_LVL[CIT])} nodes; shortcuts from world citadel_zones.csv',
      ' > '.join(f'{z["loc_id"][-2:]} {z["name"]}' for z in ZONES), cit_min, int(cit_min * 1.45),
      'Walk, wade, swim, ladders, lifts, mast cables; no Strider or vehicles',
      'Drowned grandeur: a chapel built into a beached warship, the storm rising as you climb',
      LIGHT['citadel'], 'MUS_SAL_CITADEL; Play_MUS_BOSS_CANTOR_*; Play_MUS_BOSS_CORSA_*', 'AMB_SAL_CITADEL',
      'Plan 3.7 and 5.2: 2-3 h first play, every shortcut marked; zone order, minutes, anchors and shortcuts follow world citadel_zones.csv',
      '; '.join(LEVEL_QUEST))

# =================================================================== SITES
KIT = {
 'Sunken hold': ('flooded', ['Hatch Shaft', 'Flooded Companionway', 'Cargo Bay', 'Pump Room', 'Bilge Crawl', 'Ballast Tank', 'Lower Hold', 'Brig', 'Keel Vault', 'Chain Locker']),
 'Wreck section': ('wreck', ['Breach Mouth', 'Tilted Corridor', 'Mess Hall', 'Reactor Spur', 'Crew Berths', 'Cargo Lift Well', 'Engine Gallery', 'Bulkhead Junction', 'Armory', 'Hull Rupture', 'Command Nook', 'Cold Store']),
 'Smuggler cave': ('smuggler', ['Sea Mouth', 'Tide Steps', 'Stash Cavern', 'Lantern Walk', 'Drying Racks', 'Counting Room', 'Boat Pool', 'Queen\'s Grotto', 'Bolt Hole']),
 'Tower': ('tower', ['Tower Foot', 'Guard Ring', 'Spiral Stair', 'Signal Room', 'Storm Gallery', 'Lamp Crown', 'Roof']),
 'Cave': ('cave', ['Cave Mouth', 'Salt Crust Hall', 'Echo Pool', 'Crab Warren', 'Narrow Squeeze', 'Drip Gallery', 'Tide Chamber', 'Deep Pool', 'Glow Hollow']),
 'Fort': ('fort', ['Outer Palisade', 'Gate Court', 'Barracks', 'Watch Wall', 'Mess', 'Chief\'s Hall', 'Storehouse', 'Postern']),
}
SITE_TRAV = {'Sunken hold': 'Wade, swim, hatches, ladders', 'Wreck section': 'Tilted floors, ladders, crawlspaces, lifts',
             'Smuggler cave': 'Wade, rope bridges, boat pool swim', 'Tower': 'Spiral stairs, outside cables, lift',
             'Cave': 'Squeezes, ledges, pools', 'Fort': 'Walls, ladders, gate winch'}
SITE_MUSIC = {'Smuggler cave': 'MUS_SAL_SITE', 'Fort': 'MUS_SAL_TENSION'}
ARTS = ['ITM_ART_08', 'ITM_ART_09', 'ITM_ART_11', 'ITM_ART_12', 'ITM_ART_14']
TIDE = list(PIECES['ITM_SET_41'])
site_ids = sorted(l['loc_id'] for l in locs if l['kind'] == 'Site')
for si, sid in enumerate(site_ids):
    s = SITES[sid]
    loc = L[sid]
    stype = s['site_type']
    kit, names = KIT[stype]
    r = rng(sid)
    rooms = max(6, int(s['rooms']))
    floors = max(1, int(s['floors']))
    branch_n = 2 if rooms >= 8 else 1
    main_n = rooms - branch_n
    # main path: entrance, mid rooms, arena, reward
    mids = names[1:-1]
    r.shuffle(mids)
    seq = [names[0]] + mids[:main_n - 3] + ['Keeper Arena' if 'boss' not in s['end'] else 'Boss Arena', 'Reward Room']
    roles = ['Entry'] + [('Puzzle' if (s['puzzle'] and i == (main_n - 3) // 2) else ('Combat' if i % 2 == 0 else 'Traversal'))
                         for i in range(main_n - 3)] + ['Boss' if 'boss' in s['end'] else 'Keeper', 'Reward']
    ent_anc = anchor_of(sid, 'Site entrance')
    int_anc = anchor_of(sid, 'Site interior')
    ids = []
    for i, (nm, role) in enumerate(zip(seq, roles)):
        gx, gy = snake(i)
        fl = min(floors - 1, i * floors // len(seq))
        sp = 'LONG' if stype == 'Tower' and role == 'Combat' and fl > 1 else ('MID' if role in ('Combat', 'Keeper', 'Boss') and r.random() < 0.5 else 'CQ')
        size = {'Entry': '12x12x6', 'Combat': f'{r.choice([16, 20, 24])}x{r.choice([20, 24, 30])}x{r.choice([5, 6, 8])}',
                'Traversal': f'4x{r.choice([20, 30, 40])}x4', 'Puzzle': '14x14x6', 'Keeper': '24x24x8',
                'Boss': f'{ARENA.get(next((b for b, a in ARENA.items() if a["loc_id"] == sid), ""), {}).get("diameter_m", "32")}x' +
                        f'{ARENA.get(next((b for b, a in ARENA.items() if a["loc_id"] == sid), ""), {}).get("diameter_m", "32")}x10',
                'Reward': '8x10x4'}[role]
        water = 'Swim' if kit == 'flooded' and role == 'Traversal' else ('Wade' if kit in ('flooded', 'smuggler') and role != 'Reward' else 'Dry')
        anc = ent_anc if role == 'Entry' else ''
        note = ''
        if role == 'Puzzle':
            note = 'Puzzle: ' + s['puzzle']
        if role == 'Reward':
            note = 'Unique reward ' + s['unique_reward'] + '; shortcut: ' + s['shortcut']
        nid = node(sid, nm, role, fl, gx, gy, size, sp, f'{r.randint(2, 6) if role in ("Combat", "Keeper") else 0}/{r.randint(2, 4) if role in ("Combat", "Keeper", "Boss") else 1}',
                   water, LIGHT[kit], MOOD[kit], anc, note)
        ids.append((nid, role))
    # interior anchor on the middle node
    if int_anc:
        mid = ids[len(ids) // 2][0]
        for x in NODES:
            if x['node_id'] == mid:
                x['anchor'] = int_anc
    for (a, ra), (b, rb) in zip(ids, ids[1:]):
        kind = {'Sunken hold': 'Hatch', 'Wreck section': 'Bulkhead door', 'Tower': 'Stair', 'Fort': 'Door'}.get(stype, 'Walk')
        if rb in ('Boss', 'Keeper'):
            kind = 'Fog gate' if rb == 'Boss' else 'Door'
        if rb == 'Reward':
            kind = 'Door (opens on clear)'
        edge(sid, a, b, kind, r.choice([10, 15, 20, 25]))
    edge(sid, ids[-1][0], ids[0][0], 'Shortcut: ' + s['shortcut'], 0, 'No', notes='Plan 3.7 site rule: ends in a shortcut to the entrance')
    # branches
    hosts = [n for n, rr in ids[1:-2]]
    branches = []
    for b in range(branch_n):
        bn = node(sid, r.choice(names[1:-1]) + ' (side)', 'Loot', min(floors - 1, b), 9, b * 2, '8x10x4', 'CQ', '0/1',
                  'Dry', LIGHT[kit], MOOD[kit], notes='Optional side room')
        edge(sid, hosts[b % len(hosts)], bn, 'Door', 8, 'No')
        branches.append(bn)
    secs = secret_nodes(sid, hosts)
    # encounters
    combat = [n for n, rr in ids if rr in ('Combat', 'Traversal', 'Entry')]
    keeper = [n for n, rr in ids if rr in ('Keeper', 'Boss')][0]
    ws = ENC.get(sid, [])
    ci = 0
    for e in ws:
        if e['template'] == 'ENT_KEEPER':
            world_enc(sid, keeper, e, 'Enter arena', 'Site keeper: named elite, not a boss')
        else:
            world_enc(sid, combat[1 + ci % (len(combat) - 1)], e, 'Enter node (12 m volume)')
            ci += 1
    boss = next((b for b, a in ARENA.items() if a['loc_id'] == sid), None)
    if boss:
        a = ARENA[boss]
        enc(sid, keeper, 'BOSS', '', a['level'], f'{boss} x1', 'Cross the fog gate', cover=a['cover_pieces'], fallback='0',
            respawn='Never', intent=f'{a["shape"]} {a["diameter_m"]} m; {a["hazards"]}; {a["condition"]}')
        lt = {'ACT_BOSS_SMUGGLERQUEEN': 'ITM_LT_BOSS_26', 'ACT_BOSS_WRECKFOREMAN': 'ITM_LT_BOSS_32'}[boss]
        loot(sid, keeper, 'Boss drop', lt, vis='Critical', rarity='Boss')
        nm = boss.replace('ACT_BOSS_', '')
        owner = {'SMUGGLERQUEEN': 'Smuggler Queen', 'WRECKFOREMAN': 'Wreck Foreman'}[nm]
        sxn = {'SMUGGLERQUEEN': 'SiteSmugglerQueen', 'WRECKFOREMAN': 'SiteWreckForeman'}[nm]
        cue(sid, keeper, 'Fog gate crossed', music=f'Play_MUS_BOSS_{nm}_INTRO', sfx=f'Play_SFX_Bosses_{sxn}_IntroSting',
            vfx=f'{vx(owner, "Arena barrier")} {vx(owner, "Intro")}')
        cue(sid, keeper, 'Phase 2', music=f'Play_MUS_BOSS_{nm}_T2 Play_MUS_BOSS_{nm}_P2', sfx=f'Play_SFX_Bosses_{sxn}_PhaseTransition',
            vfx=vx(owner, 'Phase transition'))
        cue(sid, keeper, 'Boss defeated', music=f'Play_MUS_BOSS_{nm}_WIN', sfx=f'Play_SFX_Bosses_{sxn}_Death', vfx=vx(owner, 'Death'))
    # extra fights where the world gave fewer than one per two combat nodes (design choice)
    tpls = SITES and [t for t in rd(W + '/site_templates.csv') if t['site_type'] == stype][0]['encounter_templates'].split()
    covered = {e['node_id'] for e in ENCS if e['loc_id'] == sid}
    for n, rr in ids:
        if rr == 'Combat' and n not in covered:
            new_enc(sid, n, r.choice(tpls), 'Enter node', 'Fills an empty combat room (design choice)')
    # loot
    reward = [n for n, rr in ids if rr == 'Reward'][0]
    rew = s['unique_reward']
    loot(sid, reward, 'Reward chest', rew, vis='Critical', rarity='Rare', notes='Unique site reward (world sites.csv)')
    if si < len(TIDE):
        loot(sid, branches[0], 'Corpse', TIDE[si], vis='Off path', rarity='Forged', notes='Tidewreck set (found), design choice')
    if 4 <= si < 4 + len(ARTS):
        loot(sid, branches[-1], 'Pedestal', ARTS[si - 4], vis='Off path', rarity='Rare', notes='Weapon art (found copy), design choice')
    place_world_loot(sid, branches + [n for n, rr in ids if rr in ('Combat', 'Traversal', 'Puzzle')] + [reward])
    # cues
    ent = ids[0][0]
    cue(sid, ent, 'First entry', music='Play_MUS_SAL_DISCOVERY ' + SITE_MUSIC.get(stype, 'MUS_SAL_SITE'),
        amb='AMB_SAL_INTERIOR; ' + sx('R2 Saltmere', 'Interior'), light=LIGHT[kit])
    cue(sid, ent, 'Anchor lit', music='Play_MUS_STG_ANCHOR_LIT', sfx=S['hum'], vfx=V['shard'], notes=ent_anc)
    ext = {'flooded': (S['water'], V['water']), 'wreck': (S['sparks'], V['sparks']), 'smuggler': (S['water'], V['torch']),
           'tower': (S['wind'] + ' ' + S['thunder'], V['lightning']), 'cave': (S['water'], V['motes']), 'fort': (S['fire'], V['torch'])}[kit]
    for n, rr in ids[1:-1]:
        cue(sid, n, 'Room loop', sfx=ext[0], vfx=ext[1])
    for n, rr in ids:
        if rr == 'Puzzle':
            cue(sid, n, 'Puzzle solved', music='Play_MUS_SAL_DISCOVERY', sfx=S['lever'] + ' ' + (S['steam'] if 'Vent' in s['puzzle'] or 'Pump' in s['puzzle'] else S['terminal']),
                vfx=V['steam'] if 'Vent' in s['puzzle'] or 'Pump' in s['puzzle'] else V['holo'])
    cue(sid, reward, 'Shortcut opened', sfx=S['shortcut'] + (' ' + S['lift'] if 'Lift' in s['shortcut'] else ''), vfx=V['shortcut'], notes=s['shortcut'])
    cue(sid, reward, 'Reward chest', sfx=S['chest'], vfx=V['chest'] + ' ' + V['glow']['Rare'])
    path = int(s['path_min'])
    level(sid, 'Site', loc['name'], f'Node graph, {len(NODE_BY_LVL[sid])} nodes, {floors} floor(s), kit {s["template"]}',
          ' > '.join(x for x in seq), path, int(path * 1.4), SITE_TRAV[stype], MOOD[kit], LIGHT[kit],
          SITE_MUSIC.get(stype, 'MUS_SAL_SITE'), 'AMB_SAL_INTERIOR',
          f'{stype}; ends: {s["end"]}; lore site {s["lore_site"]}' + ('; Smuggler Queen can be talked down at Speech 60' if sid == 'LOC_DGN_REG_02_03' else ''),
          'Radiant quests use this site' + ('; Tamsin Rook (ACT_CMP_C3) line ends here' if sid == 'LOC_DGN_REG_02_03' else '') +
          ('; Saltmere Strike start' if sid == 'LOC_DGN_REG_02_05' else '') + ('; Saltmere Strike mid' if sid == 'LOC_DGN_REG_02_06' else ''))

# =================================================================== CHOIR VAULTS
VAULT_ROOMS = [('Glass Door', 'Entry'), ('Antechamber of Echoes', 'Combat'), ('Tone Pillar Hall', 'Puzzle'),
               ('Keeper\'s Choir', 'Keeper'), ('Reliquary', 'Reward')]
for vi, vid in enumerate(sorted(l['loc_id'] for l in locs if l['kind'] == 'Choir vault')):
    s = SITES[vid]
    ids = []
    for i, (nm, role) in enumerate(VAULT_ROOMS):
        gx, gy = snake(i, 2, 3)
        ids.append((node(vid, nm, role, 0, gx, gy, {'Entry': '6x8x5', 'Combat': '14x14x8', 'Puzzle': '18x18x10', 'Keeper': '20x20x10', 'Reward': '8x8x6'}[role],
                         'CQ', '1/2' if role in ('Combat', 'Keeper') else '0/0', 'Dry', LIGHT['choir'], MOOD['choir'],
                         anchor_of(vid) if role == 'Entry' else '',
                         {'Puzzle': 'Match the tone pillars: strike 4 pillars in the order the hymn plays (3 rounds)',
                          'Entry': 'Gate: ' + L[vid]['gate']}.get(role, '')), role))
    for (a, _), (b, rb) in zip(ids, ids[1:]):
        edge(vid, a, b, 'Glass door' if rb != 'Reward' else 'Door (opens on clear)', 10)
    edge(vid, ids[-1][0], ids[0][0], 'Shortcut: ' + s['shortcut'], 0, 'No')
    secs = secret_nodes(vid, [ids[1][0], ids[2][0]])
    for e in ENC.get(vid, []):
        world_enc(vid, ids[3][0] if e['template'] == 'ENT_KEEPER' else ids[1][0], e, 'Enter node')
    loot(vid, ids[4][0], 'Reward chest', s['unique_reward'], vis='Critical', rarity='Rare')
    loot(vid, ids[4][0], 'Vault chest', 'ITM_LT_VAULT_REG_02', vis='Critical', rarity='Rare')
    if vi == 0:
        loot(vid, ids[2][0], 'Pedestal', PIECES['ITM_SET_44'][2], vis='Off path', rarity='Relic', notes='Kelp-Silk set (found)')
    if vi == 2:
        loot(vid, ids[2][0], 'Pedestal', PIECES['ITM_SET_44'][3], vis='Off path', rarity='Relic', notes='Kelp-Silk set (found)')
    place_world_loot(vid, [ids[1][0], ids[2][0], ids[4][0]])
    cue(vid, ids[0][0], 'First entry', music='Play_MUS_SAL_DISCOVERY Play_MUS_FAC_CHOIR', amb='AMB_SAL_INTERIOR', sfx=S['hum'], vfx=V['weave'])
    cue(vid, ids[2][0], 'Pillar struck', sfx=S['hum'], vfx=V['shard'], notes='Each pillar plays one note of the Saltmere mode (A Dorian)')
    cue(vid, ids[4][0], 'Glass door opens', sfx=S['shortcut'], vfx=V['shortcut'])
    level(vid, 'Choir vault', L[vid]['name'], 'Node graph, 5 rooms in a loop', ' > '.join(n for n, _ in VAULT_ROOMS),
          int(s['path_min']), int(int(s['path_min']) * 1.3), 'Walk; glass doors', MOOD['choir'], LIGHT['choir'],
          'Play_MUS_FAC_CHOIR', 'AMB_SAL_INTERIOR',
          'Gate ' + L[vid]['gate'],
          'MQ_A1_06: Hal Merrow (ACT_CMP_C5) hides here (design choice)' if vi == 1 else 'Choir faction radiant')

# =================================================================== CHOIR SITE: Tide Choir (Resonance)
CH = 'LOC_CHOIR_REG_02'
ch = [node(CH, 'Drowned Steps (hidden entrance)', 'Entry', 0, 0, 0, '6x10x4', 'CQ', '0/0', 'Wade', LIGHT['choir'], MOOD['choir'], anchor_of(CH), L[CH]['gate']),
      node(CH, 'Trial of Breath', 'Traversal', 0, 2, 0, '10x40x6', 'CQ', '0/2', 'Swim', LIGHT['choir'], MOOD['choir'], notes='Underwater swim between air bells; 4 bells, 6 s apart'),
      node(CH, 'Trial of the Current', 'Combat', 0, 4, 0, '20x20x8', 'MID', '0/3', 'Wade', LIGHT['choir'], MOOD['choir'], notes='Water surges push the player 3 m every 5 s; Choir wisps attack'),
      node(CH, 'Trial of Silence', 'Puzzle', 0, 4, 2, '16x16x8', 'CQ', '0/0', 'Dry', LIGHT['choir'], MOOD['choir'], notes='Cross the hall while the hymn is quiet; moving while it plays resets the hall'),
      node(CH, 'Undertow Well', 'Reward', 0, 2, 2, '12x12x10', 'CQ', '0/0', 'Wade', LIGHT['choir'], MOOD['choir'], notes='Grants RES_UNDERTOW; well spout carries the player back to the entrance')]
for a, b in zip(ch, ch[1:]):
    edge(CH, a, b, 'Swim' if a == ch[0] else 'Walk', 15)
edge(CH, ch[-1], ch[0], 'Shortcut: well spout (water lift)', 0, 'No')
for e in ENC.get(CH, []):
    world_enc(CH, ch[2], e, 'Enter node')
enc(CH, ch[2], 'ENT_CRT_PACK', '', L[CH]['level'], 'ACT_CRT_CHOIRWISP x4', 'Enter node', respawn='On Anchor rest', intent='Wisps ride the surges')
loot(CH, ch[4], 'Resonance', 'RES_UNDERTOW', vis='Critical', rarity='Resonance')
place_world_loot(CH, [ch[1], ch[3]])
cue(CH, ch[0], 'Entrance revealed', music='Play_MUS_SAL_DISCOVERY Play_MUS_FAC_CHOIR', sfx=S['hum'], vfx=V['weave'], notes='Shows after a Shard-note hint or Ostra line within 40 m')
cue(CH, ch[1], 'Air bell reached', sfx=S['water'], vfx=V['water'])
cue(CH, ch[4], 'Resonance granted', sfx=S['hum'], vfx=V['shard'] + ' ' + V['weave'], light='Well lights to full cyan over 3 s')
level(CH, 'Choir site', 'Tide Choir', 'Node graph, 3 trial rooms in a ring', 'Steps > Breath > Current > Silence > Well', 14, 15,
      'Swim, wade', MOOD['choir'], LIGHT['choir'], 'Play_MUS_FAC_CHOIR', 'AMB_SAL_INTERIOR', 'Short trial, no boss (world)', 'Choir questline hook')

# =================================================================== TOWNS
TOWNS = {
 'LOC_TOWN_REG_02_01': ('Stiltmarket', 30, [
    ('Causeway Gate', 'Entry', 'Anchor; siege barricade during MQ_A1_06'),
    ('Harbor Office', 'Quest', 'ACT_NPC_HARBOR_MOSS (Harbormaster Moss) gives MQ_A1_06'),
    ('Stilt Market Square', 'Hub', 'Wandering trader ACT_NPC_VEN_TRADER_REG_02 (route start); faction contact board'),
    ('Smithy Platform', 'Vendor', 'Smith (upgrades); Riveted sets ITM_SET_64-66 crafted here'),
    ('Infirmary Barge', 'Quest', 'Sister Calla (ACT_CMP_C6) treats Hollowed sailors'),
    ('Net Lofts', 'Loot', 'Rooftop route; lore sites LOC_SITE_REG_02_19 and 20'),
    ('Smugglers\' Pier', 'Quest', 'Tamsin Rook (ACT_CMP_C3) recruit spot (world npc_placement)'),
    ('Seawall', 'Combat', 'MQ_A1_06 siege: drowned fleet lands here'),
 ]),
 'LOC_TOWN_REG_02_02': ('Brinehook', 15, [
    ('Hook Jetty', 'Entry', 'Anchor; skimmer moorings'),
    ('Salt Pans', 'Hub', 'Salt workers; radiant job board (bounties, salvage runs)'),
    ('Rigging Shed', 'Vendor', 'Tinker stall (ammo, Strider Harness ITM_CON_UTL_HARNESS stock)'),
    ('Watch Hut', 'Quest', 'Hull Knight recruiter: faction questline hook'),
    ('Drying Rack Lane', 'Loot', 'Small chest behind the racks'),
 ]),
 'LOC_TOWN_REG_02_03': ('Low Tide Chapel', 15, [
    ('Tide Steps', 'Entry', 'Anchor; reachable on foot only at low tide (06:00-12:00, 18:00-24:00), skimmer otherwise'),
    ('Chapel Nave', 'Hub', 'Lantern Church shrine; reads Meridian logs as scripture'),
    ('Bell Tower', 'Quest', 'Lantern Church questline hook; bell rope opens the crypt'),
    ('Crypt', 'Loot', 'Lore items; Tonic upgrade altar is not here (Anchors only)'),
    ('Pilgrim Huts', 'Vendor', 'Brewer (Tonics and buffs)'),
 ]),
}
for tid, (nm, mins, rooms) in TOWNS.items():
    ids = []
    for i, (rn, role, note) in enumerate(rooms):
        gx, gy = snake(i, 3, 3)
        ids.append(node(tid, rn, role, 0, gx, gy, '20x20x6' if role != 'Hub' else '40x40x8', 'MID', '2/4' if role == 'Combat' else '0/2',
                        'Wade' if 'Pier' in rn or 'Jetty' in rn else 'Dry', LIGHT['town'], 'Weathered, busy, frightened of the storms',
                        anchor_of(tid) if role == 'Entry' else '', note))
    hub = ids[[r[1] for r in rooms].index('Hub')]
    edge(tid, ids[0], hub, 'Boardwalk', 40)
    for n in ids[1:]:
        if n != hub:
            edge(tid, hub, n, 'Boardwalk' if tid != 'LOC_TOWN_REG_02_03' else 'Walk', 25, 'No')
    place_world_loot(tid, ids[1:])
    for n, (rn, role, note) in zip(ids, rooms):
        if role == 'Loot' and not any(x['node_id'] == n for x in LOOT):
            loot(tid, n, 'Small chest', 'ITM_LT_SMALLCHEST_REG_02', vis='Off path')
    if tid == 'LOC_TOWN_REG_02_01':
        sw = ids[-1]
        enc(tid, sw, 'ENT_FORT', 'FAC_REMNANT', '12', 'ACT_REMNANT_SHIELDBEARER x2; ACT_REMNANT_ARTILLERY x2; ACT_REMNANT_HEAVY x1; ACT_REMNANT_FODDER x1; ACT_VAR_R2_02 x1',
            'MQ_A1_06 step 2', cover='8', fallback='3', respawn='Never', intent='Wave 1: Corsa\'s drowned fleet lands at the seawall', cond='MQ_A1_06 active')
        enc(tid, sw, 'ENT_HORDE', 'FAC_HOLLOWED', '12', 'ACT_HOLLOWED_FODDER x4; ACT_VAR_R2_01 x4; ACT_HOLLOWED_LEADER x1',
            'Wave 1 cleared', cover='2', fallback='2', respawn='Never', intent='Wave 2: Hollowed sailors; town guards fight beside the player', cond='MQ_A1_06 active')
        cue(tid, sw, 'Siege start', music='MUS_SAL_COMBAT_L2', sfx=S['barrel'] + ' ' + S['fire'], vfx=V['barrel'] + ' ' + V['torch'], notes='MQ_A1_06')
    cue(tid, ids[0], 'Enter town', music='MUS_SAL_TOWN', amb='AMB_SAL_WALLA; ' + sx('R2 Saltmere', 'Town walla'), light=LIGHT['town'])
    cue(tid, ids[0], 'Anchor lit', music='Play_MUS_STG_ANCHOR_LIT', sfx=S['hum'], vfx=V['shard'])
    cue(tid, hub, 'Night', amb='AMB_SAL_BED_NIGHT', vfx=V['torch'], light='Stilt lanterns on 19:00-06:00')
    level(tid, 'Settlement', nm, f'Node graph, {len(rooms)} districts around a hub', ' > '.join(r[0] for r in rooms[:3]), mins, mins * 2,
          'Boardwalks, wading; Strider allowed outside, dismount on boardwalks', 'Weathered, busy, frightened of the storms',
          LIGHT['town'], 'MUS_SAL_TOWN', 'AMB_SAL_WALLA', L[tid]['notes'],
          'MQ_A1_06 Storm Coast' if tid.endswith('01') else 'Faction and radiant hooks')

# =================================================================== POIs
POI_T = {  # type: (nodes [(name, role)], minutes, template, light, mood)
 'faction camp': ([('Perimeter', 'Entry'), ('Tents', 'Combat'), ('Leader\'s Tent', 'Loot')], 5, 'ENT_CAMP', EXT, 'Smoke, banners, guards bored until they are not'),
 'ruin': ([('Broken Arch', 'Entry'), ('Courtyard', 'Combat'), ('Cellar', 'Loot')], 4, 'ENT_AMBUSH', EXT, 'Quiet stones, salt-crusted carvings'),
 'wreck fragment': ([('Hull Plate', 'Entry'), ('Inside the Frame', 'Loot')], 3, 'ENT_CRT_PACK', EXT, 'Metal groaning in the tide'),
 'wayshrine': ([('Shrine', 'Entry')], 2, '', EXT, 'Calm; a candle that never goes out'),
 'watchtower': ([('Tower Base', 'Entry'), ('Tower Top', 'Loot')], 4, 'ENT_GUNLINE', EXT, 'Exposed; long view over the flats'),
 'overturned cart': ([('Cart', 'Entry')], 2, 'ENT_AMBUSH', EXT, 'Someone did not make it'),
 'overlook': ([('Path Up', 'Entry'), ('Overlook', 'Vista')], 3, '', EXT, 'Wind and the whole region below'),
 'hermit hut': ([('Hut', 'Entry'), ('Back Room', 'Loot')], 4, '', EXT, 'Lonely; a kettle still warm'),
 'grave field': ([('Grave Rows', 'Entry'), ('Mass Grave', 'Combat')], 4, 'ENT_HORDE', EXT, 'Hollowed rising from the salt'),
 'shard crater': ([('Crater Rim', 'Entry'), ('Crater Floor', 'Combat')], 4, 'ENT_ELITE', EXT, 'Humming air, glowing glass'),
 'hunting ground': ([('Tracks', 'Entry'), ('Feeding Flats', 'Combat')], 4, 'ENT_CRT_PACK', EXT, 'Birds scatter; something big feeds'),
 'lair': ([('Lair Mouth', 'Entry'), ('Nest', 'Combat')], 4, 'ENT_CRT_SOLO', EXT, 'Bones and a smell'),
 'trader stop': ([('Stall', 'Entry')], 2, '', EXT, 'Wandering trader stops here every 6 game hours'),
 'vehicle depot': ([('Depot Yard', 'Entry'), ('Garage', 'Vendor')], 3, 'ENT_PATROL', EXT, 'Engines ticking; skimmers and haulers ready'),
}
for pid in sorted(l['loc_id'] for l in locs if l['kind'] == 'POI'):
    loc = L[pid]
    t = loc['tags']
    rooms, mins, tpl, light, mood = POI_T[t]
    ids = [node(pid, rn, role, 0, i * 2, 0, '20x20x6' if role != 'Entry' else '16x16x6', 'MID', '3/2' if role == 'Combat' else '1/1',
                'Wade' if loc['biome'] != 'Storm cliffs' else 'Dry', light, mood, '', '') for i, (rn, role) in enumerate(rooms)]
    for a, b in zip(ids, ids[1:]):
        edge(pid, a, b, 'Climb (cables)' if t == 'watchtower' else 'Walk', 20)
    secret_nodes(pid, ids)
    target = [n for n, (rn, role) in zip(ids, rooms) if role == 'Combat'] or ids
    if ENC.get(pid):
        for e in ENC[pid]:
            world_enc(pid, target[0], e, 'Line of sight or 25 m')
    elif tpl:
        new_enc(pid, target[0], tpl, 'Line of sight or 25 m', 'POI fight (design choice)')
    if t == 'vehicle depot':
        loot(pid, ids[-1], 'Vehicle', 'Skimmer and Hauler spawn (TRV_SKIMMER, TRV_HAULER)', vis='Visible', notes='GATE_07')
        cue(pid, ids[-1], 'Vehicle spawned', sfx=sx('Skimmer', 'Engine idle'), vfx=V['skim_wake'])
    if t == 'wayshrine':
        loot(pid, ids[0], 'Shrine offering', 'ITM_LT_CONSUMABLE', vis='Visible', notes='Once per 72 h restock')
    if t == 'overlook':
        cue(pid, ids[-1], 'Vista', music='Play_MUS_SAL_DISCOVERY', vfx=V['birds'], notes='Camera hint toward the next landmark')
    if t == 'shard crater':
        cue(pid, ids[-1], 'Crater hum', sfx=S['hum'], vfx=V['shard'])
    place_world_loot(pid, [n for n, (rn, role) in zip(ids, rooms) if role in ('Loot', 'Combat')] or ids)
    if t in ('faction camp', 'ruin', 'hermit hut') and not any(x['loc_id'] == pid and x['container'] == 'Small chest' for x in LOOT):
        loot(pid, ids[-1], 'Small chest', 'ITM_LT_SMALLCHEST_REG_02', vis='Off path', notes='POI chest (design choice)')
    ext_cues(pid, ids[0], loc['biome'])
    level(pid, 'POI', loc['name'], f'{len(ids)} node(s)', ' > '.join(r[0] for r in rooms), mins, mins + 2,
          'Open field; Strider and vehicles', mood, light, 'MUS_SAL_EXPLORE_DAY / NIGHT', 'AMB_SAL_BED_DAY / NIGHT', t, loc['notes'])

# =================================================================== LANDMARKS
LMK = {
 'LOC_LMK_REG_02_01': [('Ark Shadow', 'Entry', 'The hull blots out the sun; 117 m tall'), ('Torn Hangar', 'Combat', 'Thorn raiders strip the hull'), ('Keel Climb', 'Traversal', 'Cables up the keel'), ('Flight Deck', 'Vista', 'View to the Drowned Hold and the Relay')],
 'LOC_LMK_REG_02_02': [('Mast Field', 'Entry', 'Dozens of signal masts sing in the wind'), ('Array Hub', 'Combat', 'Remnant drones maintain the array'), ('Mast Top', 'Vista', 'Hijackable flyer perches here')],
 'LOC_LMK_REG_02_03': [('Salt Doors', 'Entry', 'A cathedral carved from a salt dome'), ('Nave of Crystal', 'Combat', 'Hollowed congregation'), ('Bell Loft', 'Vista', 'Lightning rod; bell rings in storms')],
 'LOC_LMK_REG_02_04': [('Lantern Line', 'Entry', 'Stilt lanterns across the flats; they light at dusk'), ('Lamplighter\'s Perch', 'Loot', 'Climb one stilt: small chest')],
 'LOC_LMK_REG_02_05': [('Stack Maze', 'Entry', 'Containers stacked 95 m high'), ('Gantry Crane', 'Combat', 'Remnant gun line on the crane'), ('Stack Crown', 'Vista', 'Glide-off point over the shallows')],
 'LOC_LMK_REG_02_06': [('Lighthouse Rocks', 'Entry', 'Stormglass catches lightning'), ('Lamp Room', 'Quest', 'QST_SHB_W14 Stormcrown finale: channel 3 strikes into the lens')],
 'LOC_LMK_REG_02_07': [('Rib Arches', 'Entry', 'Skeleton of a leviathan 61 m high'), ('Marrow Pools', 'Combat', 'Hull crabs nest in the bones')],
}
for lid, rooms in LMK.items():
    loc = L[lid]
    ids = [node(lid, rn, role, 0, i * 3, 0, '30x30x10', 'MID' if role != 'Vista' else 'LONG', '2/2' if role == 'Combat' else '0/1',
                'Wade' if loc['biome'] != 'Storm cliffs' else 'Dry', EXT, '', '', note) for i, (rn, role, note) in enumerate(rooms)]
    for a, b in zip(ids, ids[1:]):
        edge(lid, a, b, 'Climb (cables)' if 'Climb' in rooms[ids.index(b)][0] or 'Top' in rooms[ids.index(b)][0] or 'Crown' in rooms[ids.index(b)][0] else 'Walk', 30)
    for n, (rn, role, note) in zip(ids, rooms):
        if role == 'Combat':
            if ENC.get(lid):
                for e in ENC[lid]:
                    world_enc(lid, n, e, 'Line of sight')
            else:
                tpl = 'ENT_CRT_PACK' if 'crabs' in note else ('ENT_HORDE' if 'Hollowed' in note else ('ENT_GUNLINE' if 'gun' in note or 'drones' in note else 'ENT_CAMP'))
                fac = 'FAC_HOLLOWED' if 'Hollowed' in note else ('FAC_REMNANT' if 'Remnant' in note else 'FAC_THORN')
                new_enc(lid, n, tpl, 'Line of sight', 'Landmark fight (design choice)', fac=fac)
        if role == 'Vista':
            cue(lid, n, 'Vista', music='Play_MUS_SAL_DISCOVERY', vfx=V['birds'] + ' ' + V['region'])
        if role == 'Loot':
            loot(lid, n, 'Small chest', 'ITM_LT_SMALLCHEST_REG_02', vis='Off path', notes='design choice')
        if role == 'Quest':
            loot(lid, n, 'Quest reward', 'ITM_SHB_W14', vis='Critical', rarity='Shardborn', notes='QST_SHB_W14 (design choice for where it ends)')
            cue(lid, n, 'Lens charged', sfx=S['thunder'] + ' ' + S['hum'], vfx=V['lightning'] + ' ' + V['shard'], light='Lens flares to 50,000 lux for 1 s per strike')
    place_world_loot(lid, ids)
    cue(lid, ids[0], 'First sight', music='Play_MUS_SAL_DISCOVERY', notes=f'Visible {next(r["visible_km"] for r in rd(W + "/landmarks.csv") if r["loc_id"] == lid)} km')
    ext_cues(lid, ids[0], loc['biome'], storm=lid.endswith('06'))
    level(lid, 'Landmark', loc['name'], f'{len(ids)} nodes, vertical', ' > '.join(r[0] for r in rooms), 6, 10,
          'Strider, cables, glide off the top', 'Awe; a silhouette that pulls the player across the flats', EXT,
          'Play_MUS_SAL_DISCOVERY', 'AMB_SAL_EMITTERS', 'Landmark rhythm: one new silhouette every 40-60 s of riding (world level_metrics)',
          'QST_SHB_W14' if lid.endswith('06') else '')

# =================================================================== RELAY TOWER
RL = 'LOC_RELAY_REG_02'
rl = [node(RL, 'Relay Base', 'Entry', 0, 0, 0, '30x30x6', 'MID', '4/3', 'Wade', EXT, 'Guarded', anchor_of(RL), 'Remnant hold the base'),
      node(RL, 'Stage 1: Ledges', 'Traversal', 1, 0, 2, '6x6x35', 'CQ', '0/0', 'Dry', EXT, 'Climb', notes='Ledge climb 35 m; Breath rests every 10 m'),
      node(RL, 'Stage 2: Service Lift', 'Puzzle', 2, 0, 4, '6x6x40', 'CQ', '0/0', 'Dry', EXT, 'Climb', notes='Restart the lift generator (1 lever, 1 fuse found on the platform)'),
      node(RL, 'Stage 3: Ladder Spire', 'Traversal', 3, 0, 6, '3x3x31', 'CQ', '0/0', 'Dry', EXT, 'Exposed', notes='Ladder 31 m in the wind; drones harass'),
      node(RL, 'Relay Crown', 'Reward', 4, 0, 8, '10x10x4', 'LONG', '0/0', 'Dry', EXT, 'Triumph', notes='Ostra fills in the region map')]
for a, b, k in zip(rl, rl[1:], ['Climb (ledges)', 'Lift', 'Ladder', 'Ladder']):
    edge(RL, a, b, k, 30)
edge(RL, rl[-1], rl[0], 'Shortcut: glide or lift down', 0, 'No')
for e in ENC.get(RL, []):
    world_enc(RL, rl[0], e, 'Enter base')
if not ENC.get(RL):
    new_enc(RL, rl[0], 'ENT_GUNLINE', 'Enter base', 'Relay guard (design choice)', fac='FAC_REMNANT')
    new_enc(RL, rl[3], 'ENT_AMBUSH', 'Halfway up the ladder', 'Hornet drones harass the climb', fac='FAC_REMNANT')
place_world_loot(RL, rl)
cue(RL, rl[0], 'Anchor lit', music='Play_MUS_STG_ANCHOR_LIT', sfx=S['hum'], vfx=V['shard'])
cue(RL, rl[2], 'Lift restarted', sfx=S['lever'] + ' ' + S['lift'], vfx=V['lever'] + ' ' + V['lift'])
cue(RL, rl[4], 'Relay activated', music='Play_MUS_SAL_DISCOVERY', sfx=S['relay'], vfx=f'{V["relay"]} {V["reveal"]} {V["ostra_in"]} {V["ostra_map"]}',
    notes='Map reveal; Ostra line (campaign VO)')
level(RL, 'Relay Tower', 'Saltmere Relay Tower', 'Vertical, 5 nodes', 'Base > Ledges > Lift > Ladder > Crown', 8, 10,
      'Climb, lift, ladder; glide down', 'Exposed climb above the storm', EXT, 'Play_MUS_SAL_DISCOVERY', 'AMB_SAL_WIND', '80 m tall, visible 3 km', 'Region map reveal')

# =================================================================== FIELD BOSSES
FB = {
 'LOC_FB_LEVIATHAN': ('ACT_BOSS_LEVIATHAN', 'ITM_LT_BOSS_14', 'Reef Leviathan', 'FieldReefLeviathan', 'LEVIATHAN',
     [('Shore Shelf', 'Entry', 'Anchor; harpoon racks (throwable, 3)'), ('Deep Channel', 'Boss', 'Surfaces when the player is within 80 m'),
      ('Rib Shallows', 'Cover', 'Wreck ribs block tail sweeps'), ('Skimmer Slip', 'Vehicle', 'Fight from a skimmer for ranged passes')]),
 'LOC_FB_SKIMMERACE': ('ACT_BOSS_SKIMMERACE', 'ITM_LT_BOSS_20', 'Skimmer Ace', 'FieldSkimmerAce', 'SKIMMERACE',
     [('Start Line', 'Entry', 'Anchor; drive the salt-flat circuit to start'), ('Flats Straight', 'Boss', '900 m straight; ace boosts and fires'),
      ('Cargo Chicane', 'Cover', 'Containers break line of sight'), ('Cliff Hairpin', 'Boss', 'Ramp jump; ace tries to ram you off'),
      ('Finish Basin', 'Reward', 'Duel ends; ace bails out and fights on foot at 25%')]),
}
for fid, (boss, lt, owner, sxn, mus, rooms) in FB.items():
    loc = L[fid]
    a = ARENA[boss]
    ids = [node(fid, rn, role, 0, i * 3, (i % 2) * 2, f'{a["diameter_m"]}x{a["diameter_m"]}x0' if role == 'Boss' else '40x40x0', 'LONG' if role == 'Boss' else 'MID',
                f'0/{a["cover_pieces"]}' if role == 'Boss' else '0/3', 'Wade', EXT, 'Open, loud, dangerous',
                anchor_of(fid) if role == 'Entry' else '', note) for i, (rn, role, note) in enumerate(rooms)]
    for x, y in zip(ids, ids[1:]):
        edge(fid, x, y, 'Drive' if 'SKIMMER' in boss else 'Walk', 120)
    bn = [n for n, r in zip(ids, rooms) if r[1] == 'Boss'][0]
    enc(fid, bn, 'BOSS', '', a['level'], f'{boss} x1', 'Proximity', cover=a['cover_pieces'], respawn='Never',
        intent=f'{a["entry"]}; {a["hazards"]}; {a["condition"]}')
    loot(fid, bn, 'Boss drop', lt, vis='Critical', rarity='Boss')
    if 'SKIMMER' in boss:
        loot(fid, ids[-1], 'Quest reward', 'ITM_SHB_A14', vis='Critical', rarity='Shardborn', notes='QST_SHB_A14 Wake Treads ends with this duel (design choice)')
    place_world_loot(fid, ids)
    cue(fid, bn, 'Boss engaged', music=f'Play_MUS_BOSS_{mus}_INTRO Play_MUS_BOSS_{mus}_P1', sfx=f'Play_SFX_Bosses_{sxn}_IntroSting', vfx=vx(owner, 'Intro'))
    cue(fid, bn, 'Phase 2', music=f'Play_MUS_BOSS_{mus}_T2 Play_MUS_BOSS_{mus}_P2', sfx=f'Play_SFX_Bosses_{sxn}_PhaseTransition', vfx=vx(owner, 'Phase transition'))
    cue(fid, bn, 'Boss defeated', music=f'Play_MUS_BOSS_{mus}_WIN', sfx=f'Play_SFX_Bosses_{sxn}_Death', vfx=vx(owner, 'Death'))
    ext_cues(fid, ids[0], loc['biome'])
    level(fid, 'Field boss', loc['name'], f'Open ground {a["diameter_m"]} m, leash 1.5x', ' > '.join(r[0] for r in rooms), 8, 12,
          'Strider allowed; skimmer' if 'LEVIATHAN' in boss else 'Skimmer required', 'Spectacle', EXT,
          f'Play_MUS_BOSS_{mus}_*', 'AMB_SAL_BED_DAY', loc['notes'], 'Saltmere Strike final boss (empowered)' if 'LEVIATHAN' in boss else 'QST_SHB_A14')

# =================================================================== CONNECTIONS, UNDERVAULT ENTRY, PATROLS
CONN = {
 'LOC_CON_03': ('Flight Deck Causeway', [('Causeway Gate', 'Entry', 'One-way gate opens from the Saltmere side (to Lantern Hold)'), ('Flight Deck', 'Traversal', 'Old ark flight deck used as a bridge')]),
 'LOC_CON_04': ('Western Dikes', [('Storm Wall', 'Gate', 'Act 2: falls when ACT_BOSS_CORSA dies (to Rimefall)'), ('Dike Road', 'Traversal', 'Hauler-width road on the dike')]),
 'LOC_CON_05': ('Stormbreak Pass', [('Pass Mouth', 'Gate', 'Act 2: opens when ACT_BOSS_CORSA dies (to Glasswaste)'), ('Switchbacks', 'Traversal', 'Strider climb; vehicle slope limit 30 deg')]),
 'LOC_UV_ENTRY_02': ('Drowned Cargo Lift', [('Lift House', 'Entry', 'Anchor LOC_ANC_REG_02_43'), ('Shaft Top', 'Traversal', 'Lift ride 4 m/s down to the Undervault Cargo Vaults (REG_U owns what is below)')]),
}
for cid, (nm, rooms) in CONN.items():
    loc = L[cid]
    ids = [node(cid, rn, role, 0, i * 3, 0, '20x40x6', 'MID', '0/2', 'Dry', EXT, 'Threshold', anchor_of(cid) if role == 'Entry' else '', note)
           for i, (rn, role, note) in enumerate(rooms)]
    edge(cid, ids[0], ids[1], 'Lift' if 'UV' in cid else 'Walk', 60, 'Yes', loc['gate'])
    place_world_loot(cid, ids)
    if 'UV' in cid:
        cue(cid, ids[1], 'Lift ride', sfx=S['lift'], vfx=V['lift'], music='Play_MUS_UND_DISCOVERY')
        new_enc(cid, ids[0], 'ENT_ELITE', 'Enter lift house', 'Guard on the lift (design choice)')
    else:
        cue(cid, ids[0], 'Gate opens', sfx=S['shortcut'] + ' ' + S['metal'], vfx=V['shortcut'])
    level(cid, 'Connection' if 'UV' not in cid else 'Undervault entry', nm, '2 nodes', ' > '.join(r[0] for r in rooms), 2, 3,
          'Walk, Strider, vehicles' if 'UV' not in cid else 'Lift', 'Threshold', EXT, '', 'AMB_SAL_WIND', loc['gate'] or loc['notes'])

for pid in sorted(l['loc_id'] for l in locs if l['kind'] == 'Patrol route'):
    loc = L[pid]
    r = rng(pid)
    rad = r.choice([60, 75, 90])
    ids = []
    for k in range(4):
        ang = k * math.pi / 2
        ids.append(node(pid, f'Waypoint {k + 1} ({int(float(loc["x_m"]) + rad * math.cos(ang))}, {int(float(loc["y_m"]) + rad * math.sin(ang))})',
                        'Waypoint', 0, 1 + int(math.cos(ang) * 1.5), 1 + int(math.sin(ang) * 1.5), '10x10x0', 'MID', '1/1', 'Wade', EXT, '', '',
                        'Pause 6 s; look around'))
    for a, b in zip(ids, ids[1:] + ids[:1]):
        edge(pid, a, b, 'Patrol leg', int(rad * 1.41))
    for e in ENC.get(pid, []):
        world_enc(pid, ids[0], e, 'Line of sight 40 m', 'Walks the loop; joins nearby fights within 60 m')
    level(pid, 'Patrol route', loc['name'], f'Loop of 4 waypoints, about {int(rad * 5.6)} m', 'Loop', 1, 1, 'Open field', 'Threat on the road', EXT,
          'MUS_SAL_TENSION', 'AMB_SAL_BED_DAY', 'ENT_PATROL loop 150-300 m (world)')

# =================================================================== PUBLIC EVENTS (world adds them; 3 waves each)
for vid in sorted(l['loc_id'] for l in locs if l['kind'] == 'Public event'):
    loc = L[vid]
    ws = ENC.get(vid, [])
    fac = ws[0]['faction'] if ws else pick_fac(loc['biome'], vid)
    ids = [node(vid, 'Event ring (300 m start radius)', 'Entry', 0, 0, 0, '600x600x0', 'LONG', '-', 'Mixed', EXT, 'Alarm', notes=loc['notes']),
           node(vid, 'Wave 1 ground', 'Combat', 0, 2, 0, '60x60x0', 'MID', '6/4', 'Wade', EXT, 'Chaos', notes='Wave 1 (world encounter)'),
           node(vid, 'Wave 2 ground', 'Combat', 0, 4, 0, '60x60x0', 'MID', '6/4', 'Wade', EXT, 'Chaos', notes='Wave 2: flank from the far side'),
           node(vid, 'Wave 3: leader', 'Boss', 0, 6, 0, '40x40x0', 'MID', '4/4', 'Wade', EXT, 'Climax', notes='Wave 3: leader and heavy; event chest on clear')]
    for a, b in zip(ids, ids[1:]):
        edge(vid, a, b, 'Event wave', 40)
    for e in ws:
        world_enc(vid, ids[1], e, 'Event start', 'Wave 1')
    new_enc(vid, ids[2], 'ENT_AMBUSH', 'Wave 1 cleared', 'Wave 2 (design choice)', fac=fac, respawn='Per event')
    new_enc(vid, ids[3], 'ENT_ELITE', 'Wave 2 cleared', 'Wave 3 (design choice); scales by coop_scaling', fac=fac, respawn='Per event')
    loot(vid, ids[3], 'Event chest', 'ITM_LT_VAULT_REG_02', vis='Critical', rarity='Rare', notes='One per player per event')
    loot(vid, ids[3], 'Event chest', 'ITM_LT_TIERMAT_REG_02', '2-4', 'Critical')
    cue(vid, ids[0], 'Event start', music='MUS_SAL_COMBAT_L2', sfx=S['thunder'] if 'Shard-fall' in loc['name'] else S['barrel'],
        vfx=V['shard'] if 'Shard-fall' in loc['name'] else V['torch'], notes='HUD event banner (UI thread)')
    cue(vid, ids[3], 'Event complete', music='MUS_SAL_COMBAT_END', sfx=S['chest'], vfx=V['chest'] + ' ' + V['glow']['Rare'])
    level(vid, 'Public event', loc['name'], '4 nodes, 3 waves', 'Start > Wave 1 > Wave 2 > Wave 3', 6, 6, 'Open field', 'Chaotic, social',
          EXT, 'MUS_SAL_COMBAT_L2', 'AMB_SAL_BED_DAY', loc['notes'], 'Host POI ' + loc['parent_loc'])

# =================================================================== ENDGAME AND PVP SPACES (Saltmere kit)
for eid, nm, crit, mins, note in (
    ('LOC_END_STRIKE_02', 'Tidewreck strike (3 players; owner design/levels/multiplayer LOC_MP_STK_02)',
     'See design/levels/multiplayer mp_maps.csv / mp_nodes.csv LOC_MP_STK_02: drop at Gull Hulk (LOC_DGN_REG_02_05) > pump-room holdout > tide-hop traversal > Choir vault in Tide Sunken Hold (LOC_DGN_REG_02_06) > field-boss pair Reef Leviathan + Skimmer Ace (LOC_FB_LEVIATHAN)', 24,
     'Same space as the multiplayer strike, which owns the layout, timing (21-24 min) and rewards; this row only points to it. '
     'Saltmere draft detail kept as a note for the multiplayer thread: the old draft crossed the open ground between the two sites on skimmers and had shortcuts pre-opened; '
     'the owner version crosses on foot (tide hop) and adds the Skimmer Ace to the boss fight.'),
    ('LOC_END_HCIT_02', 'Hollowed Drowned Hold (1-4 players)', 'Z1 > Z3 > Z5 Cantor (Hollowed) > Z7 > Z8 Corsa (Hollowed); Z2 and Z6 sealed', 49,
     'Citadel nodes with Hollowing grade (V1199, V1200; AMB_SAL_HOLLOWING; MUS_SAL_HOLLOWING); level 75-80'),
    ('LOC_END_ARENA_02', 'Salt Pans (3v3 PvP; owner design/levels/multiplayer ARENA_MP_02)',
     'See design/levels/multiplayer layouts/ARENA_MP_02.txt: 76 x 48 m salt flats, brine lanes, three wreck islands, two power weapon pads', 9,
     'Same map as the multiplayer arena, which owns the layout; the Saltmere node graph was dropped as a duplicate. '
     'Differences in the dropped Saltmere draft (note only): 120 x 90 m with bases 120 m apart, three lanes (vehicle lane with skimmers, depot lane in a Foam Vehicle depot garage, stack lane container maze), one centre power pad. '
     'The owner map is smaller for 6 players and has no vehicles.')):
    owned = 'STRIKE' in eid or 'ARENA' in eid
    LEVELS.append(dict(loc_id=eid, kind='Endgame', name=nm, biome='', level='80 (sync)' if owned else '75-80',
                       layout='Owned by design/levels/multiplayer (see critical_path)' if owned else 'Reuses Saltmere nodes',
                       critical_path=crit, first_play_min=mins, completion_min=mins, traversal='', mood='', lighting=EXT,
                       music='MUS_MP_STK02_EXPLORE; MUS_MP_STK02_COMBAT; MUS_MP_STK02_BOSS' if 'STRIKE' in eid else ('MUS_SAL_HOLLOWING' if 'HCIT' in eid else ('MUS_MP_PVP02_MATCH' if 'ARENA' in eid else '')),
                       ambience='AMB_SAL_HOLLOWING' if 'HCIT' in eid else ('SFX_MP_AMB_STK02' if 'STRIKE' in eid else ('SFX_MP_AMB_PVP02' if 'ARENA' in eid else '')), notes=note))

# =================================================================== OPEN FIELD (loot outside any level)
FL = 'REG_02'
field_anc = [a for a in ANC.get('', [])] + [a for a in sum(ANC.values(), []) if a['anchor_type'] == 'Field']
seen = set()
fnodes = {}
for a in field_anc:
    if a['loc_id'] in seen:
        continue
    seen.add(a['loc_id'])
    fnodes[a['loc_id']] = (node(FL, f'Field near {a["loc_id"]}', 'Field', 0, int(float(a['x_m']) // 100), int(float(a['y_m']) // 100), '400x400x0', 'LONG', '-', 'Mixed', EXT, '', a['loc_id']), a)
for l in FIELD_ASSIGN.get(FL, []):
    best = min(fnodes.values(), key=lambda t: dist(l, t[1]))
    if l['kind'] == 'Lore site':
        for it in LORE.get(l['loc_id'], []):
            loot(FL, best[0], 'Lore item', it, vis='Off path', rarity='Lore', src=l['loc_id'])
    else:
        it, rar = loot_item(l)
        loot(FL, best[0], l['kind'], it, vis='Visible' if l['kind'] == 'Gather node' else 'Off path', rarity=rar, src=l['loc_id'],
             notes=f'({l["x_m"]}, {l["y_m"]})')
loot(FL, list(fnodes.values())[0][0], 'Quest reward', 'ITM_SHB_A08', vis='Critical', rarity='Shardborn',
     notes='QST_SHB_A08 Starmetal Carapace ends at Wrack Shard crater LOC_POI_REG_02_10 during a meteor night (design choice)')
LEVELS.append(dict(loc_id=FL, kind='Open field', name='Saltmere open field', layout=f'{len(fnodes)} field cells around field Anchors',
                   critical_path='See README region critical path', lighting=EXT, music='MUS_SAL_EXPLORE_DAY; MUS_SAL_EXPLORE_NIGHT',
                   ambience='AMB_SAL_BED_DAY; AMB_SAL_BED_NIGHT; AMB_SAL_WILDLIFE; AMB_SAL_WATER',
                   notes='Loot outside any level, attached to the nearest field Anchor'))

# =================================================================== totals per level
for lv in LEVELS:
    lid = lv['loc_id']
    e = [x for x in ENCS if x['loc_id'] == lid]
    lt = [x for x in LOOT if x['loc_id'] == lid]
    lv['nodes'] = len(NODE_BY_LVL[lid])
    lv['encounters'] = len(e)
    lv['enemies'] = sum(x['enemy_count'] for x in e)
    lv['loot_rows'] = len(lt)
    lv['collectibles'] = sum(1 for x in lt if x['container'] in ('Lore item',) or 'TNC' in x['item'] or x['rarity'] in ('Shardborn', 'Relic', 'Resonance'))
    lv['secrets'] = sum(1 for n in NODE_BY_LVL[lid] if n['role'] == 'Secret')
    lv['anchors'] = ' '.join(sorted({n['anchor'] for n in NODE_BY_LVL[lid] if n['anchor']}))

# =================================================================== checks
def chk(name, ok, detail=''):
    CHECKS.append(dict(check=name, result='PASS' if ok else 'FAIL', detail=detail))

refs = set()
for row in ENCS + LOOT:
    for v in (row.get('actors', ''), row.get('item', ''), row.get('world_enc', '')):
        refs |= set(re.findall(r'\b(?:ACT|ITM|ENC|RES)_[A-Z0-9_]+', v))
missing = sorted(r for r in refs if r not in KNOWN)
chk('Every ACT_/ITM_/ENC_/RES_ id in encounters and loot exists in data/ or design/world', not missing, ' '.join(missing[:20]))
aud = set()
for c in CUES:
    for v in (c['music'], c['ambience'], c['sfx']):
        aud |= set(x for x in re.split(r'[ ;]+', v) if x.startswith(('MUS_', 'AMB_', 'Play_')))
miss_a = sorted(a for a in aud if a not in AUDIO)
chk('Every audio cue exists in design/audio', not miss_a, ' '.join(miss_a[:20]))
allfx = ' '.join(c['vfx'] + ' ' + c['sfx'] for c in CUES)
chk('Every VFX/SFX id found in shardfall-assets.xlsx', 'MISSING' not in allfx, ' '.join(set(re.findall(r'MISSING_[A-Z]+\([^)]*\)', allfx))))
need = [l['loc_id'] for l in locs if l['kind'] in ('Public event', 'Site', 'Choir vault', 'Choir site', 'POI', 'Landmark', 'Settlement', 'Relay Tower', 'Field boss', 'Connection', 'Undervault entry', 'Patrol route', 'Citadel')]
have = {lv['loc_id'] for lv in LEVELS}
chk('Every Saltmere level location has a level row', all(n in have for n in need), ' '.join(n for n in need if n not in have))
chk('Every Citadel zone is covered', all(any(n['notes'].startswith(z['loc_id']) for n in NODE_BY_LVL[CIT]) for z in ZONES))
for lid in [l for l in need if l.startswith(('LOC_DGN', 'LOC_VAULT', 'LOC_CHOIR'))]:
    ok = any(e['loc_id'] == lid and e['type'].startswith('Shortcut') for e in EDGES)
    if not ok:
        chk(f'{lid} ends in a shortcut', False)
chk('Every site, vault and Choir site ends in a shortcut to its entrance (plan 3.7)',
    all(any(e['loc_id'] == lid and e['type'].startswith('Shortcut') for e in EDGES) for lid in need if lid.startswith(('LOC_DGN', 'LOC_VAULT', 'LOC_CHOIR'))))
placed = {x['source_loc'] for x in LOOT if x['source_loc']}
want = [l['loc_id'] for l in locs if l['kind'] in LOOT_KINDS]
chk('Every world chest, crate, lore site and gather node is placed on a node', all(w in placed for w in want),
    f'{sum(w in placed for w in want)}/{len(want)}')
world_e = {e['enc_id'] for v in ENC.values() for e in v}
used = {x['world_enc'] for x in ENCS if x['world_enc']}
chk('Every world encounter in Saltmere is placed on a node', world_e <= used, ' '.join(sorted(world_e - used)[:20]))
chk('Every world secret in Saltmere is a node', all(any(s in n['notes'] for n in NODES) for s in SECRET), '')
chk('Citadel first play 120-180 min (plan 3.7)', 120 <= cit_min <= 180, f'{cit_min} min')
for lid in need:
    if lid.startswith(('LOC_DGN', 'LOC_VAULT')):
        lv = next(x for x in LEVELS if x['loc_id'] == lid)
        if not 10 <= int(lv['first_play_min']) <= 25:
            chk(f'{lid} site loop 10-25 min (plan 3.3)', False, lv['first_play_min'])
chk('Site loops 10-25 min (plan 3.3)', all(10 <= int(x['first_play_min']) <= 25 for x in LEVELS if x['kind'] in ('Site', 'Choir vault')))
# connectivity: every node reachable from the first node of its level (edges both ways)
bad = []
for lid, ns in NODE_BY_LVL.items():
    if lid in (FL,) or not ns:
        continue
    adj = collections.defaultdict(set)
    for e in EDGES:
        if e['loc_id'] == lid:
            adj[e['from_node']].add(e['to_node'])
            adj[e['to_node']].add(e['from_node'])
    seen, st = {ns[0]['node_id']}, [ns[0]['node_id']]
    while st:
        for m in adj[st.pop()]:
            if m not in seen:
                seen.add(m)
                st.append(m)
    if len(ns) > 1 and len(seen) < len(ns):
        bad.append(lid)
chk('Every node is reachable inside its level', not bad, ' '.join(bad))
def mins(kinds, ids=None):
    return sum(int(x['first_play_min'] or 0) for x in LEVELS if x['kind'] in kinds and (ids is None or x['loc_id'] in ids))
crit = mins(('Citadel', 'Relay Tower')) + mins(('Settlement',), {'LOC_TOWN_REG_02_01'}) + 90
typical = mins(('Citadel', 'Relay Tower', 'Settlement', 'Field boss', 'Choir site')) + 8 * 17 + 15 * 4 + 120
full = mins(('Citadel', 'Relay Tower', 'Settlement', 'Field boss', 'Choir site', 'Site', 'Choir vault', 'POI', 'Landmark', 'Public event', 'Connection', 'Undervault entry')) + 150
chk('Typical region run 6-12 h (plan 3.3): Citadel, towns, relay, field bosses, Choir site, 8 sites, 15 POIs, travel', 360 <= typical <= 720,
    f'critical path {crit} min; typical {typical} min; completionist {full} min (all levels plus travel)')
# =================================================================== write
wr('level_index.csv', LEVELS, ['loc_id', 'kind', 'name', 'biome', 'level', 'x_m', 'y_m', 'z_m', 'grid', 'layout', 'nodes', 'critical_path',
                               'first_play_min', 'completion_min', 'anchors', 'encounters', 'enemies', 'loot_rows', 'collectibles', 'secrets',
                               'traversal', 'mood', 'lighting', 'music', 'ambience', 'quest_hooks', 'gate', 'notes'])
wr('level_nodes.csv', NODES, ['node_id', 'loc_id', 'order', 'name', 'role', 'floor', 'gx', 'gy', 'size_m', 'space', 'cover_low_high', 'water',
                              'anchor', 'lighting', 'mood', 'notes'])
wr('level_edges.csv', EDGES, ['edge_id', 'loc_id', 'from_node', 'to_node', 'type', 'length_m', 'critical', 'gate', 'notes'])
wr('level_encounters.csv', ENCS, ['lenc_id', 'loc_id', 'node_id', 'world_enc', 'template', 'faction', 'level', 'actors', 'enemy_count', 'trigger',
                                   'cover_points', 'fallback_points', 'respawn', 'intent', 'condition'])
wr('level_loot.csv', LOOT, ['loot_id', 'loc_id', 'node_id', 'container', 'item', 'qty', 'visibility', 'rarity', 'source_loc', 'notes'])
wr('level_cues.csv', CUES, ['cue_id', 'loc_id', 'node_id', 'trigger', 'music', 'ambience', 'sfx', 'vfx', 'lighting', 'notes'])
wr('checks.csv', CHECKS, ['check', 'result', 'detail'])

# =================================================================== maps (node graphs)
COL = {'Entry': '#4F8FE6', 'Boss': '#C0392B', 'Keeper': '#E67E22', 'Reward': '#8FE3EE', 'Secret': '#9B7BD6', 'Shortcut': '#27AE60',
       'Puzzle': '#F1C40F', 'Loot': '#A87A4A', 'Locked': '#7F8C8D'}
for lid, ns in NODE_BY_LVL.items():
    if len(ns) < 3 or lid == FL:
        continue
    pos = {}
    sec_i = 0
    for n in ns:
        x, y = float(n['gx']), float(n['gy'])
        if n['role'] == 'Secret':
            x, y = -2, sec_i * 2
            sec_i += 1
        pos[n['node_id']] = (60 + (x + 2) * 55, 60 + y * 55)
    w = max(p[0] for p in pos.values()) + 160
    h = max(p[1] for p in pos.values()) + 100
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" font-family="sans-serif" font-size="10">',
           f'<rect width="100%" height="100%" fill="#14181c"/><text x="10" y="20" fill="#eee" font-size="14">{lid}</text>']
    for e in EDGES:
        if e['loc_id'] != lid:
            continue
        (x1, y1), (x2, y2) = pos[e['from_node']], pos[e['to_node']]
        c = '#27AE60' if e['type'].startswith('Shortcut') else ('#9B7BD6' if e['critical'] == 'No' else '#ccc')
        dash = ' stroke-dasharray="5,4"' if e['critical'] == 'No' else ''
        out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{c}" stroke-width="2"{dash}/>')
    for n in ns:
        x, y = pos[n['node_id']]
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{COL.get(n["role"], "#888")}"/>'
                   f'<text x="{x + 12:.0f}" y="{y + 4:.0f}" fill="#eee">{n["order"]}. {n["name"][:34].replace("&", "and").replace("<", "")}</text>')
    out.append('</svg>')
    open(f'{OUT}/maps/{lvl_code(lid)}.svg', 'w').write('\n'.join(out))

print(f'{len(LEVELS)} levels, {len(NODES)} nodes, {len(EDGES)} edges, {len(ENCS)} encounters, {len(LOOT)} loot rows, {len(CUES)} cues')
for c in CHECKS:
    if c['result'] != 'PASS' or True:
        print(c['result'], c['check'], c['detail'][:200])
