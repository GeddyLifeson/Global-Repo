#!/usr/bin/env python3
"""Shardfall world and level design generator.

Reads data/ (read-only) and writes every table and SVG in design/world/.
Rules come from the master plan, section 3.7 and Phase 5.1-5.3: six surface
regions of about 3.5 km2, an Undervault under three regions, the Quiet ring
(about 2 km2, three sub-areas), one Citadel, 2-3 towns, 15-20 sites, 30-40 small
POIs, two field bosses and one Choir site per region, Anchors every 400-600 m
and at every site entrance, one Relay Tower per region, a landmark every 40-60 s
of riding. Everything else is a Shardfall choice. Seeded, so IDs and coordinates
are stable across runs.

Run: python3 design/world/tools/gen_world_design.py
"""
import csv, math, os, random, re, sys
# RETIRED 2026-10-03: the world tables are frozen and other threads build on them. Rerunning would overwrite
# anchors, sites, encounters and the rest. New places go through tools/append_locations.py (append only).
if '--force' not in sys.argv:
    sys.exit('Frozen: use tools/append_locations.py; pass --force only for a deliberate continuity pass.')
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
DATA = os.path.join(OUT, '..', '..', 'data')
SVG = os.path.join(OUT, 'maps')
os.makedirs(SVG, exist_ok=True)
R = random.Random(20261003)

def rd(p):
    with open(os.path.join(DATA, p), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def wr(name, rows, cols=None):
    cols = cols or list(rows[0].keys())
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)
    print(f'{name}: {len(rows)} rows')

# ---------------------------------------------------------------- source data
regions = {r['reg_id']: r for r in rd('world/regions.csv')}
enemies = rd('actors/enemies.csv')
creatures = rd('actors/creatures.csv')
bosses = {r['ACT_ID']: r for r in rd('actors/bosses.csv')}
old_locs = rd('world/locations.csv')
lore = rd('items/lore_items.csv')
res = rd('actors/resonances.csv')
npcs = rd('world/npcs.csv')
hooks = {r['hook'] for r in rd('assets/asset_hooks.csv')}
firearms = rd('items/weapons_firearm.csv')
uniq_pool = defaultdict(list)          # unique site rewards by region
for f in ['items/weapons_melee.csv', 'items/weapons_firearm.csv', 'items/catalysts.csv', 'items/weapon_arts.csv']:
    for r in rd(f):
        if r.get('rarity') in ('Rare', 'Relic') and r.get('first_region', '').startswith('REG_'):
            uniq_pool[r['first_region']].append(r['item_id'])
keys = [r for r in lore if 'Key (' in r['name']]

# ---------------------------------------------------------------- world frame
# Surface map: 10,000 m east x 5,625 m north, origin at the south-west corner.
# Grid cells are 250 m, labelled column letters (A..AN) + row number (1..23).
W, H, CELL = 10000, 5625, 250
def grid(x, y):
    c = int(x // CELL); r = int(y // CELL) + 1
    col = chr(65 + c) if c < 26 else 'A' + chr(65 + c - 26)
    return f'{col}{r}'

# Region shapes: ellipses with area about 3.5 km2 (plan 3.7). Layout follows the
# Visual Bible world-map mockup: Cinderreach south-west, Saltmere north-centre,
# Thornwood east, Glasswaste north-east, Rimefall north-west, Hollowdeep far east.
REG = {
 'REG_01': dict(c=(2750, 1800), r=(1200, 930), entry=225, apex=45, z=(40, 260), act='Act 1',
     biomes=[('Ash plains', .45), ('Crash scar badlands', .30), ('Hull-keep hills', .25)],
     weather='Ash fall, dry; dusk haze', fac={'HOLLOWED': .6, 'THORN': .4},
     adj=['Ash', 'Cinder', 'Ember', 'Soot', 'Kiln', 'Scorch', 'Charred', 'Smoke'],
     towns=['Emberwatch', 'Cinder Hollow', "Wreckers' Rest"],
     landmarks=['The Meridian Spine (wreck ridge)', 'Cryo Field (pod crater)', 'Burning Mast', 'Hullgate Arch',
                'The Smelter Stacks', 'Ash Colossus Footprints', 'Kindled Cairn'],
     cit=('Spine Keep', ['Ash Road Approach', 'Hullgate Barbican', 'Lower Bailey', 'Rampart Walk', 'Spinegate Bridge',
                         'Reactor Undercroft', 'Knight Chapter Halls', 'The Ember Throne']),
     sites=['Cave', 'Mine', 'Wreck section', 'Tower', 'Catacomb', 'Cave', 'Wreck section', 'Mine', 'Tower',
            'Catacomb', 'Fort', 'Wreck section', 'Cave', 'Fort', 'Mine'],
     siteboss={'ACT_BOSS_FURNACEMAW': 'Old Smelter Works', 'ACT_BOSS_MINEGOLEM': 'Cinderdeep Mine'},
     vehicles='Skimmer (roads, ash plains); Hauler (crash scar); Flyer: none (Act 1 teaches ground first)'),
 'REG_02': dict(c=(4750, 3450), r=(1250, 890), entry=225, apex=30, z=(0, 45), act='Act 1',
     biomes=[('Flooded salt flats', .45), ('Cargo-deck shallows', .30), ('Storm cliffs', .25)],
     weather='Rain squalls, lightning storms 30% of game days', fac={'HOLLOWED': .3, 'REMNANT': .4, 'THORN': .3},
     adj=['Salt', 'Brine', 'Tide', 'Drowned', 'Gull', 'Wrack', 'Foam', 'Squall'],
     towns=['Stiltmarket', 'Brinehook', 'Low Tide Chapel'],
     landmarks=['Beached Ark Deck', 'Signal Mast Array', 'The Salt Cathedral', 'Stilt Lanterns', 'Drowned Cargo Stacks',
                'Stormglass Lighthouse', 'Leviathan Ribs'],
     cit=('The Drowned Hold', ['Causeway Locks', 'Floodgate Yard', 'Bilge Market', 'Mast Gallery', "Cantor's Nave",
                               'Ballast Deep', 'Admiralty Decks', 'The Storm Deck']),
     sites=['Sunken hold', 'Wreck section', 'Smuggler cave', 'Tower', 'Wreck section', 'Sunken hold', 'Cave',
            'Tower', 'Wreck section', 'Smuggler cave', 'Fort', 'Sunken hold', 'Wreck section', 'Cave', 'Fort'],
     siteboss={'ACT_BOSS_SMUGGLERQUEEN': "Smugglers' Grotto", 'ACT_BOSS_WRECKFOREMAN': 'Hull Nine Breaker Yard'},
     vehicles='Skimmer (salt flats); Hauler (causeways); Flyer (Remnant skiffs, hijack)'),
 'REG_03': dict(c=(6550, 2050), r=(1100, 1010), entry=180, apex=0, z=(80, 320), act='Act 2',
     biomes=[('Redbark forest', .50), ('Reactor bog', .25), ('Bramble ravines', .25)],
     weather='Fog mornings, pollen drift, warm rain', fac={'THORN': .6, 'HOLLOWED': .2, 'REMNANT': .2},
     adj=['Thorn', 'Redbark', 'Briar', 'Moss', 'Root', 'Bramble', 'Fen', 'Sap'],
     towns=['Redbark Lodge', 'Thicket Steading'],
     landmarks=['The Reactor Fragment', 'Mother Tree', 'Antler Gate', 'Bog Lantern Field', 'Hanging Hulls',
                'Briar Engine Stacks', 'Hound Barrows'],
     cit=('The Briar Engine', ['Root Gate', 'Thorn Market', 'Coolant Fen', 'Bough Walk', "Halden's Grave Hall",
                               'Reactor Roots', 'Canopy Works', 'The Bloom Heart']),
     sites=['Cave', 'Reactor ruin', 'Catacomb', 'Tower', 'Cave', 'Fort', 'Reactor ruin', 'Wreck section', 'Cave',
            'Catacomb', 'Fort', 'Tower', 'Wreck section', 'Cave', 'Reactor ruin'],
     siteboss={'ACT_BOSS_ROTHYDRA': 'Rotfen Sump', 'ACT_BOSS_BROODQUEEN': 'Broodhollow Caves'},
     vehicles='Skimmer (logging roads only); Hauler: none (forest); Flyer (canopy clearings, hijack)'),
 'REG_04': dict(c=(7400, 4000), r=(1300, 860), entry=200, apex=20, z=(150, 420), act='Act 2',
     biomes=[('Glass desert', .50), ('Singing dunes', .30), ('Strike crater', .20)],
     weather='Heat shimmer, glass storms (visibility 60 m) 20% of game days', fac={'REMNANT': .5, 'THORN': .3, 'HOLLOWED': .2},
     adj=['Glass', 'Dune', 'Mirage', 'Sun', 'Lens', 'Singing', 'Sand', 'Prism'],
     towns=['Glassmouth Caravanserai', 'Choirtower Hamlet'],
     landmarks=['The Choir Spire', 'Strike Crater Rim', 'Basilisk Spines', 'Mirror Flats', 'Hauler Road Pylons',
                'Fallen Shuttle', 'The Singing Arch'],
     cit=('The Choir Spire', ['Dune Gate', 'Glassblower Terraces', 'Lens Courts', 'Sun Gallery', 'Engine Foundry',
                              'Spire Cisterns', 'Choir Ascent', 'The Iron Choir Loft']),
     sites=['Tower', 'Wreck section', 'Cave', 'Lab', 'Fort', 'Wreck section', 'Tower', 'Cave', 'Lab', 'Fort',
            'Wreck section', 'Catacomb', 'Tower', 'Cave', 'Lab'],
     siteboss={'ACT_BOSS_MIRRORKNIGHT': 'Hall of Panes', 'ACT_BOSS_LASTPILOT': 'Shuttle Bay Wreck'},
     vehicles='Skimmer (dunes); Hauler (convoy roads); Flyer (Remnant gunships, hijack)'),
 'REG_05': dict(c=(2150, 4000), r=(1250, 890), entry=0, apex=170, z=(300, 900), act='Act 2',
     biomes=[('Frozen highlands', .45), ('Drive-section glacier', .30), ('Monastery valleys', .25)],
     weather='Snow, blizzards (visibility 40 m) at night above 700 m', fac={'CHOIRBORN': .4, 'REMNANT': .4, 'HOLLOWED': .2},
     adj=['Rime', 'Frost', 'Hoar', 'Snow', 'Bell', 'Lamp', 'Glacier', 'Pale'],
     towns=['Rimehold', 'Lampwick', 'Frostgate Hamlet'],
     landmarks=['The Drive Section', 'Saint Drive Abbey Bells', 'Frost Titan Throne', 'Ice-Locked Ark Knight', 'Lamp Road',
                'Witch Needle', 'Glacier Mouth'],
     cit=('Saint Drive Abbey', ['Pilgrim Stair', 'Bell Gate', 'Cloister Snows', 'Reliquary Walk', 'Choir Mother Chancel',
                                'Drive Coolant Crypts', 'Abbot Lanterns', 'The Rime Altar']),
     sites=['Catacomb', 'Cave', 'Tower', 'Monastery ruin', 'Wreck section', 'Cave', 'Catacomb', 'Monastery ruin',
            'Fort', 'Tower', 'Cave', 'Wreck section', 'Monastery ruin', 'Fort', 'Cave'],
     siteboss={'ACT_BOSS_TOWERWITCH': "Witch's Needle", 'ACT_BOSS_CRYPTABBOT': "Abbot's Crypt"},
     vehicles='Skimmer (Lamp Road); Hauler (glacier); Flyer (valleys, hijack)'),
 'REG_06': dict(c=(8800, 1650), r=(1050, 1060), entry=180, apex=0, z=(100, 640), act='Act 2',
     biomes=[('Grey barrens', .40), ('Floating shelves', .35), ('Hollowed city fringe', .25)],
     weather='Colourless; debris drifts upward; no rain', fac={'HOLLOWED': .5, 'CHOIRBORN': .4, 'REMNANT': .1},
     adj=['Hollow', 'Grey', 'Drift', 'Lifted', 'Hush', 'Bone', 'Faded', 'Ghost'],
     towns=['Last Light', 'Driftanchor'],
     landmarks=['The Lifted City', 'Upward Falls', 'Bone Harvest Fields', 'Sentinel Pair', 'Broken Orbit Tether',
                'Clockhouse Tower', 'The Pale Hole'],
     cit=('The Lifted City', ['Tether Docks', 'Floating Bazaar', 'Hanging Streets', 'Lamp Spires', "Lamplighter's Way",
                              'Underside Gardens', 'Ascendant Palace', 'The Twin Throne']),
     sites=['Wreck section', 'Catacomb', 'Tower', 'Lab', 'Cave', 'Fort', 'Wreck section', 'Catacomb', 'Tower',
            'Lab', 'Cave', 'Fort', 'Wreck section', 'Tower', 'Catacomb'],
     siteboss={'ACT_BOSS_CLOCKPRIOR': "Prior's Clockhouse", 'ACT_BOSS_VAULTKEEPER': 'Deep Vault Nine'},
     vehicles='Skimmer (barrens); Hauler: none (floating ground); Flyer (between shelves, hijack)'),
}
HUB = dict(c=(4100, 2450), r=(300, 250), z=120)
SHARD = {'REG_01': 'ACT_BOSS_VAEL', 'REG_02': 'ACT_BOSS_CORSA', 'REG_03': 'ACT_BOSS_SORREL',
         'REG_04': 'ACT_BOSS_BRANNOCH', 'REG_05': 'ACT_BOSS_RIME', 'REG_06': 'ACT_BOSS_HOLLOWTWINS'}
CITB = {'REG_01': 'ACT_BOSS_SPINEGATE', 'REG_02': 'ACT_BOSS_CANTOR', 'REG_03': 'ACT_BOSS_HALDEN',
        'REG_04': 'ACT_BOSS_GRAFTED', 'REG_05': 'ACT_BOSS_YSSE', 'REG_06': 'ACT_BOSS_LAMPLIGHTER'}
FIELD = defaultdict(list); SITEB = defaultdict(list)
for b in bosses.values():
    if b['Class'] == 'Field': FIELD[b['Region']].append(b['ACT_ID'])
    if b['Class'] == 'Site': SITEB[b['Region']].append(b['ACT_ID'])
FIELD_COND = {'ACT_BOSS_NIGHTDRAKE': 'Night only (20:00-05:00)', 'ACT_BOSS_ASHCOLOSSUS': 'Roams a 600 m loop on the ash plain',
              'ACT_BOSS_LEVIATHAN': 'Surfaces in the deep channel when the player is within 80 m',
              'ACT_BOSS_SKIMMERACE': 'Vehicle chase; starts when the player drives the salt-flat circuit',
              'ACT_BOSS_HAULER': 'Wandering convoy on the Hauler Road; full loop 9 min',
              'ACT_BOSS_BONEHARVESTER': 'Night only (20:00-05:00)', 'ACT_BOSS_FROSTTITAN': 'Wakes on approach; blizzard during fight'}
CHOIR = {r['Region']: (r['RES_ID'], re.search(r'\((.*)\)', r['Source']).group(1)) for r in res if r['Source'].startswith('Choir site')}

def lvl_band(reg):
    g = regions[reg]; return int(g['level_min']), int(g['level_max'])

# ---------------------------------------------------------------- geometry helpers
def inside(reg, x, y, shrink=1.0):
    (cx, cy), (rx, ry) = REG[reg]['c'], REG[reg]['r']
    return ((x - cx) / (rx * shrink)) ** 2 + ((y - cy) / (ry * shrink)) ** 2 <= 1

def edge_pt(reg, ang, k=0.9):
    (cx, cy), (rx, ry) = REG[reg]['c'], REG[reg]['r']
    a = math.radians(ang); return cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)

def t_of(reg, x, y):
    """0 at the region entry, 1 at the apex (Shard-bearer seat)."""
    ex, ey = edge_pt(reg, REG[reg]['entry']); ax, ay = edge_pt(reg, REG[reg]['apex'])
    dx, dy = ax - ex, ay - ey
    return max(0.0, min(1.0, ((x - ex) * dx + (y - ey) * dy) / (dx * dx + dy * dy)))

def level_at(reg, x, y):
    lo, hi = lvl_band(reg); return round(lo + (hi - lo) * t_of(reg, x, y))

def elev(reg, x, y):
    lo, hi = REG[reg]['z']; n = 0.5 + 0.25 * math.sin(x / 640) * math.cos(y / 820) + 0.25 * t_of(reg, x, y)
    return round(lo + (hi - lo) * n)

def biome(reg, x, y):
    # biome bands sweep across the region along the entry-apex axis
    t = t_of(reg, x, y); acc = 0
    for name, share in REG[reg]['biomes']:
        acc += share
        if t <= acc + 1e-9: return name
    return REG[reg]['biomes'][-1][0]

placed = defaultdict(list)   # reg -> [(x,y,kind)]
def place(reg, mind, shrink=0.92, near=None, spread=None, tries=4000, tband=None):
    (cx, cy), (rx, ry) = REG[reg]['c'], REG[reg]['r']
    for _ in range(tries):
        if near:
            x = near[0] + R.uniform(-spread, spread); y = near[1] + R.uniform(-spread, spread)
        else:
            x = R.uniform(cx - rx, cx + rx); y = R.uniform(cy - ry, cy + ry)
        if not inside(reg, x, y, shrink): continue
        if tband and not (tband[0] <= t_of(reg, x, y) <= tband[1]): continue
        if all((x - px) ** 2 + (y - py) ** 2 >= mind ** 2 for px, py, _ in placed[reg]):
            placed[reg].append((x, y, '')); return round(x), round(y)
    mind *= 0.7
    return place(reg, mind, shrink, near, spread, tries, tband) if mind > 5 else (round(near[0]), round(near[1]))

LOCS = []
def loc(lid, kind, reg, name, x, y, z=None, layer='Surface', parent='', level=None, gate='', tags='', notes=''):
    if level is None: level = level_at(reg, x, y) if reg in REG and 'c' in REG[reg] else ''
    if z is None: z = elev(reg, x, y) if reg in REG and 'c' in REG[reg] else 0
    row = dict(loc_id=lid, kind=kind, region=reg, name=name, layer=layer, parent_loc=parent, x_m=x, y_m=y, z_m=z,
               grid=grid(x, y) if layer in ('Surface', 'Undervault') else '', level=level,
               biome=biome(reg, x, y) if reg in REG and 'c' in REG[reg] else '', gate=gate, tags=tags, notes=notes)
    LOCS.append(row); return row

# ---------------------------------------------------------------- factions -> actors
ROLES = ['FODDER', 'SHIELDBEARER', 'SKIRMISHER', 'ARTILLERY', 'HEAVY', 'LEADER']
variants = defaultdict(list)   # (reg, base) -> [var ids]
for e in enemies:
    if e['Tier'] == 'Regional variant': variants[(e['Regions'], e['Base ACT_ID'])].append(e['ACT_ID'])
crt_by_reg = defaultdict(list)
for c in creatures:
    for g in c['Regions'].split():
        if c['Hostility'] != 'Passive': crt_by_reg[g].append(c)

def actor(reg, fac, role):
    base = f'ACT_{fac}_{role}'
    v = variants.get((reg, base))
    return R.choice(v) if v and R.random() < 0.5 else base

TEMPLATES = [  # id, name, role mix, cover, fallback, respawn, use
 ('ENT_PATROL', 'Road patrol', {'FODDER': 3, 'SKIRMISHER': 1}, 2, 1, 'On Anchor rest', 'Roads between Anchors; walks a 150-300 m loop'),
 ('ENT_CAMP', 'Faction camp', {'FODDER': 4, 'SHIELDBEARER': 1, 'ARTILLERY': 1, 'LEADER': 1}, 6, 2, 'On Anchor rest; leader stays dead', 'POI camps; one leader whose death can panic fodder'),
 ('ENT_AMBUSH', 'Ambush', {'SKIRMISHER': 3, 'ARTILLERY': 1}, 3, 1, 'On Anchor rest', 'Ravines, ruins, site corridors; triggers on a 12 m volume'),
 ('ENT_FORT', 'Fortified line', {'SHIELDBEARER': 2, 'ARTILLERY': 2, 'HEAVY': 1, 'FODDER': 2}, 8, 3, 'On Anchor rest', 'Gates and walls; built for gun and spell play, flanks for melee'),
 ('ENT_ELITE', 'Elite and escort', {'HEAVY': 1, 'FODDER': 2}, 2, 1, 'Heavy stays dead', 'Site mid-points and dangerous POIs'),
 ('ENT_HORDE', 'Horde', {'FODDER': 8, 'LEADER': 1}, 2, 2, 'On Anchor rest', 'Hollowed nests and Citadel courtyards; tests crowd tools'),
 ('ENT_GUNLINE', 'Gun line', {'ARTILLERY': 3, 'SHIELDBEARER': 2, 'SKIRMISHER': 2}, 10, 3, 'On Anchor rest', 'Long sightline spaces (40-120 m); cover every 8-12 m'),
 ('ENT_KEEPER', 'Site keeper', {'HEAVY': 1, 'LEADER': 1, 'FODDER': 2}, 4, 1, 'Never (unique per site)', 'Ends a site with no site boss; a named elite, not a boss'),
 ('ENT_CRT_PACK', 'Creature pack', {}, 0, 0, 'On Anchor rest', 'Pack creatures (3-4)'),
 ('ENT_CRT_SOLO', 'Large creature', {}, 0, 0, 'On Anchor rest', 'One large or huge creature'),
]
TPL = {t[0]: t for t in TEMPLATES}
ENC = []
def encounter(lrow, tpl, reg=None, fac=None, layer=None, cond=''):
    reg = reg or lrow['region']; fw = REG[reg]['fac'] if reg in REG and 'c' in REG[reg] else EXTRA_FAC[reg]
    if tpl.startswith('ENT_CRT'):
        pool = [c for c in crt_by_reg[reg] if (c['Size'] in ('Small', 'Medium')) == (tpl == 'ENT_CRT_PACK')] or crt_by_reg[reg]
        c = R.choice(pool); n = R.randint(3, 4) if tpl == 'ENT_CRT_PACK' else 1
        acts = f"{c['ACT_ID']} x{n}"; fac = 'Creature'
    else:
        fac = fac or R.choices(list(fw), weights=list(fw.values()))[0]
        cnt = defaultdict(int)
        for role, n in TPL[tpl][2].items():
            for _ in range(n): cnt[actor(reg, fac, role)] += 1
        acts = '; '.join(f'{a} x{n}' for a, n in cnt.items())
        fac = 'FAC_' + fac
    eid = f'ENC_{len(ENC) + 1:04d}'
    ENC.append(dict(enc_id=eid, loc_id=lrow['loc_id'], region=reg, layer=layer or lrow['layer'], x_m=lrow['x_m'], y_m=lrow['y_m'],
                    template=tpl, faction=fac, level=lrow['level'], actors=acts, cover_points=TPL[tpl][3],
                    fallback_points=TPL[tpl][4], respawn=TPL[tpl][5], condition=cond))
    return eid

EXTRA_FAC = {'REG_U': {'HOLLOWED': .4, 'REMNANT': .4, 'THORN': .2}, 'REG_Q': {'CHOIRBORN': 1.0}}

# ---------------------------------------------------------------- old LOC ids by region/kind
old = defaultdict(list)
for r in old_locs:
    old[(r['region'], r['kind'])].append(r['loc_id'])
used_old = set()

def take_old(reg, kind):
    for lid in old[(reg, kind)]:
        if lid not in used_old: used_old.add(lid); return lid
    return None

ANCH = []; SITES = []; ZONES = []; ARENAS = []; SECRETS = []; CONNS = []; LMK = []; VEH = []
def anchor(reg, x, y, kind, parent, layer='Surface', z=None, level=None, note=''):
    n = sum(1 for a in ANCH if a['region'] == reg) + 1
    row = loc(f'LOC_ANC_{reg}_{n:02d}', 'Anchor', reg, f'Anchor, {parent or kind}', x, y, z=z, layer=layer, parent=parent,
              level=level, tags=kind, notes=note)
    ANCH.append(dict(loc_id=row['loc_id'], region=reg, layer=layer, anchor_type=kind, parent_loc=parent, x_m=x, y_m=y,
                     fast_travel='No (until lit)' if kind != 'Hub' else 'Yes'))
    return row

def arena(boss, lrow, anc):
    b = bosses[boss]; ph = int(b['Phases']); suf = boss.replace('ACT_BOSS_', '')
    hk = [f'ARENA_{suf}_P{i}' for i in range(1, ph + 1) if f'ARENA_{suf}_P{i}' in hooks]
    size = {'Shard-bearer': (60, 70), 'Citadel': (45, 55), 'Field': (90, 150), 'Site': (30, 40), 'Raid': (70, 90)}[b['Class']]
    dia = R.randint(*size)
    shape = R.choice({'Field': ['Open ground', 'Crater bowl', 'Road and ruins'], 'Site': ['Round chamber', 'Long hall', 'Pit with ledges'],
                      'Raid': ['Multi-platform', 'Ring room with lanes']}.get(b['Class'], ['Round court', 'Long nave', 'Stepped platform']))
    ARENAS.append(dict(boss=boss, boss_name=b['Boss'], class_=b['Class'], level=b['Level'], loc_id=lrow['loc_id'], region=lrow['region'],
                       layer=lrow['layer'], x_m=lrow['x_m'], y_m=lrow['y_m'], arena_hooks=' '.join(hk), shape=shape, diameter_m=dia,
                       cover_pieces=0 if b['Class'] == 'Site' else max(4, dia // 12), entry='Fog gate (4 m wide), one-way while fighting' if b['Class'] != 'Field' else 'Open; leash 1.5x diameter, resets after 20 s out of range',
                       nearest_anchor=anc['loc_id'] if anc else '', anchor_run_m=R.randint(25, 60) if b['Class'] != 'Field' else R.randint(80, 160),
                       phase_change=' / '.join(f'P{i}: {hk[i-1]}' for i in range(2, len(hk) + 1)) or 'Same arena',
                       hazards=b['Notes'] or '', condition=FIELD_COND.get(boss, '')))

# Site templates: type -> (kit, floors, rooms, path minutes, shortcut forms, encounter templates, puzzles)
SC_STD = ['Kick-down ladder to the entrance', 'One-way door to the entrance hall', 'Lift back up to the entrance Anchor', 'Drop-down hatch above the entrance']
STEMPL = {
 'Cave': ('KIT_CAVE', (1, 2), (6, 9), (10, 16), SC_STD, ['ENT_AMBUSH', 'ENT_CRT_PACK', 'ENT_ELITE'], ['', 'Light the Shard-lamps to reveal a path']),
 'Mine': ('KIT_MINE', (2, 3), (7, 10), (14, 22), SC_STD + ['Mine cart rail back to the entrance'], ['ENT_HORDE', 'ENT_AMBUSH', 'ENT_ELITE'], ['Restart the hoist', '']),
 'Wreck section': ('KIT_WRECK', (2, 4), (8, 12), (15, 25), SC_STD + ['Pressure door cycled from inside'], ['ENT_GUNLINE', 'ENT_FORT', 'ENT_AMBUSH'], ['Route power between three panels', 'Vent the flooded deck']),
 'Tower': ('KIT_TOWER', (4, 6), (6, 8), (10, 15), ['Lift from the top to the base', 'Rope drop from the top'], ['ENT_GUNLINE', 'ENT_AMBUSH', 'ENT_ELITE'], ['', 'Climb the outside on cables']),
 'Catacomb': ('KIT_CATACOMB', (2, 3), (8, 11), (14, 20), SC_STD, ['ENT_HORDE', 'ENT_AMBUSH', 'ENT_ELITE'], ['Lever trap gauntlet', 'Statue puzzle']),
 'Fort': ('KIT_FORT', (1, 2), (5, 8), (10, 18), ['Gate winch opens the front gate', 'Postern door to the road'], ['ENT_FORT', 'ENT_CAMP', 'ENT_GUNLINE'], ['']),
 'Sunken hold': ('KIT_WRECK_FLOODED', (2, 3), (7, 10), (14, 22), SC_STD + ['Drain the hold to open the lower hatch'], ['ENT_AMBUSH', 'ENT_CRT_PACK', 'ENT_GUNLINE'], ['Pump the water level up or down']),
 'Smuggler cave': ('KIT_CAVE_SMUGGLER', (1, 2), (6, 9), (10, 18), SC_STD + ['Hidden sea door'], ['ENT_AMBUSH', 'ENT_CAMP'], ['']),
 'Reactor ruin': ('KIT_REACTOR', (2, 3), (7, 10), (15, 24), SC_STD, ['ENT_FORT', 'ENT_HORDE', 'ENT_GUNLINE'], ['Coolant valves in order', 'Shield the reactor core to cross']),
 'Lab': ('KIT_LAB', (2, 3), (6, 9), (12, 20), SC_STD, ['ENT_GUNLINE', 'ENT_FORT'], ['Find three access codes in logs']),
 'Monastery ruin': ('KIT_MONASTERY', (1, 3), (6, 9), (12, 20), SC_STD + ['Bell rope lowers the gate'], ['ENT_AMBUSH', 'ENT_ELITE', 'ENT_HORDE'], ['Ring the bells in the order of the hymn']),
 'Choir vault': ('KIT_CHOIR_VAULT', (1, 2), (4, 6), (10, 14), ['Glass door that opens from inside'], ['ENT_ELITE', 'ENT_AMBUSH'], ['Match the tone pillars']),
}

# ================================================================= SURFACE REGIONS
BOSS_STYPE = {'Old Smelter Works': 'Mine', 'Cinderdeep Mine': 'Mine', "Smugglers' Grotto": 'Smuggler cave', 'Hull Nine Breaker Yard': 'Wreck section',
              'Rotfen Sump': 'Reactor ruin', 'Broodhollow Caves': 'Cave', 'Hall of Panes': 'Tower', 'Shuttle Bay Wreck': 'Wreck section',
              "Witch's Needle": 'Tower', "Abbot's Crypt": 'Catacomb', "Prior's Clockhouse": 'Tower', 'Deep Vault Nine': 'Lab'}
UV_ENTRY_REG = ['REG_02', 'REG_03', 'REG_05']
unique_used = set()
for reg, g in REG.items():
    nm = regions[reg]['name']; lo, hi = lvl_band(reg); rr = int(reg[-2:])
    # Citadel at the apex edge, zones run back toward the centre
    ax, ay = edge_pt(reg, g['apex'], 0.72)
    citx, city = place(reg, 50, near=(ax, ay), spread=30)
    cname, znames = g['cit']
    cit = loc(f'LOC_CIT_{reg}', 'Citadel', reg, cname, citx, city, level=f'{hi - 3}-{hi}', tags='legacy;shortcuts;story',
              notes=f'Legacy site, 2-3 h first-play path, 8 zones; Citadel boss {CITB[reg]}, Shard-bearer {SHARD[reg]}')
    LMK.append(dict(loc_id=cit['loc_id'], region=reg, name=cname, height_m=R.randint(90, 160), visible_km=4.0, role='Citadel silhouette'))
    path_total = 0; zx, zy = citx, city
    ex, ey = edge_pt(reg, g['entry'], 0.0)
    for i, zn in enumerate(znames, 1):
        k = (8 - i) / 8.0
        zx2 = round(citx + (g['c'][0] - citx) * 0.35 * k + R.uniform(-40, 40)); zy2 = round(city + (g['c'][1] - city) * 0.35 * k + R.uniform(-40, 40))
        zl = round(hi - 3 + 3 * i / 8)
        zrow = loc(f'LOC_CIT_{reg}_Z{i}', 'Citadel zone', reg, f'{cname}: {zn}', zx2, zy2, z=elev(reg, zx2, zy2) + i * 14, parent=cit['loc_id'], level=zl)
        pm = R.randint(14, 22) if i not in (5, 8) else R.randint(8, 12); path_total += pm
        style = ['Melee close quarters', 'Gun gallery (40-80 m sightlines)', 'Mixed', 'Vertical climb', 'Boss approach'][(i * 3 + rr) % 5] if i not in (5, 8) else 'Boss arena'
        has_anchor = i in (1, 3, 5, 6, 8)
        a = anchor(reg, zx2, zy2, 'Citadel', zrow['loc_id'], z=zrow['z_m'], level=zl, note='Before the boss fog gate' if i in (5, 8) else '') if has_anchor else None
        sc = {1: 'none (entry)', 2: 'Barbican winch gate opens back to Z1 Anchor', 3: 'Kick-down ladder to Z2',
              4: 'One-way door to Z3 Anchor', 5: 'Lift from boss antechamber to Z3', 6: 'Drop-down plank to Z5 Anchor',
              7: 'Bridge lowered from Z7 to Z4 (big loop)', 8: 'Elevator from seat to Z1 (exit)'}[i]
        door = take_old(reg, 'Locked door') if i in (2, 4, 6, 7) else None
        if door:
            ky = [k_['item_id'] for k_ in keys if f'({reg[-2:]})' in k_['name']] or [keys[0]['item_id']]
            loc(door, 'Locked door', reg, f'Locked door, {cname}', zx2 + 8, zy2 + 5, parent=zrow['loc_id'], level=zl, gate=f'Key {ky[(i // 2) % len(ky)]}')
        encs = []
        if i == 5: arena(CITB[reg], zrow, a)
        elif i == 8: arena(SHARD[reg], zrow, a)
        else:
            for tpl in R.sample(['ENT_FORT', 'ENT_AMBUSH', 'ENT_HORDE', 'ENT_GUNLINE', 'ENT_ELITE', 'ENT_CAMP'], 3):
                encs.append(encounter(zrow, tpl))
        ZONES.append(dict(loc_id=zrow['loc_id'], citadel=cit['loc_id'], order=i, name=zn, level=zl, path_min=pm,
                          elevation_rel_m=i * 14, style=style, anchor=a['loc_id'] if a else '', shortcut=sc,
                          locked_door=door or '', encounters=' '.join(encs),
                          boss=CITB[reg] if i == 5 else (SHARD[reg] if i == 8 else '')))
    cit['notes'] += f'; authored path {path_total} min'

    # Relay Tower near the centre, on high ground
    rx_, ry_ = place(reg, 150, near=g['c'], spread=250)
    relay = loc(f'LOC_RELAY_{reg}', 'Relay Tower', reg, f'{nm} Relay Tower', rx_, ry_, z=elev(reg, rx_, ry_) + 80, tags='map reveal;climb',
                notes='Climb in 3 stages (ledges, lift, ladder); Ostra fills in the region map at the top')
    LMK.append(dict(loc_id=relay['loc_id'], region=reg, name=relay['name'], height_m=80, visible_km=3.0, role='Map reveal'))
    anchor(reg, rx_ + 20, ry_ - 15, 'Relay', relay['loc_id'])

    # Towns: existing TOWN_01 plus new
    for i, tn in enumerate(g['towns'], 1):
        tb = (0.05, 0.35) if i == 1 else (0.2, 0.85)
        tx, ty = place(reg, 350, tband=tb)
        lid = take_old(reg, 'Settlement') if i == 1 else f'LOC_TOWN_{reg}_{i:02d}'
        trow = loc(lid, 'Settlement', reg, tn, tx, ty, tags='town;vendors;quests' if i == 1 else 'town;quests',
                   notes='Main town: smith, trader stop, faction contact' if i == 1 else 'Small settlement')
        anchor(reg, tx + 15, ty + 10, 'Town', trow['loc_id'])

    # Landmarks: a large silhouette roughly every 700 m (40-60 s on a Strider at 14 m/s)
    for i, ln in enumerate(g['landmarks'], 1):
        lx, ly = place(reg, 420, tband=(0.0, 0.12) if 'Cryo' in ln else None)
        lrow = loc(f'LOC_LMK_{reg}_{i:02d}', 'Landmark', reg, ln, lx, ly, tags='landmark;sightline')
        LMK.append(dict(loc_id=lrow['loc_id'], region=reg, name=ln, height_m=R.randint(25, 120), visible_km=round(R.uniform(1.5, 3.5), 1), role='Navigation'))

    # Sites: 15 authored + 3 existing Choir vaults = 18 (plan 15-20)
    uq = [u for u in uniq_pool[reg] if u not in unique_used]; R.shuffle(uq)
    sb = dict(g['siteboss']); sb_types = {'Old Smelter Works': 'Mine', 'Cinderdeep Mine': 'Mine'}
    boss_slots = {}
    stypes = list(g['sites'])
    for bi, (bid, bname) in enumerate(sb.items()):
        boss_slots[3 + bi * 7] = (bid, bname)
    vaults = old[(reg, 'Choir vault')]
    allsites = [(t, None) for t in stypes] + [('Choir vault', v) for v in vaults]
    lore_sites = old[(reg, 'Lore site')]
    for si, (stype, vid) in enumerate(allsites, 1):
        bl_ = int(bosses[boss_slots[si][0]]['Level']) if si in boss_slots else None
        tb_ = (max(0, (bl_ - lo) / (hi - lo) - 0.08), min(1, (bl_ - lo) / (hi - lo) + 0.08)) if bl_ else None
        sx, sy = place(reg, 260, tband=tb_)
        lid = vid or f'LOC_DGN_{reg}_{si:02d}'
        if vid: used_old.add(vid)
        bossinfo = boss_slots.get(si)
        if bossinfo: stype = BOSS_STYPE[bossinfo[1]]
        if bossinfo: sname = bossinfo[1]
        elif vid: sname = f"{R.choice(g['adj'])} Choir Vault"
        else:
            noun = {'Cave': ['Cave', 'Grotto', 'Hollow'], 'Mine': ['Mine', 'Delve', 'Pit'], 'Wreck section': ['Wreck', 'Hulk', 'Bulkhead'],
                    'Tower': ['Tower', 'Spire', 'Watch'], 'Catacomb': ['Catacombs', 'Ossuary', 'Crypt'], 'Fort': ['Fort', 'Redoubt', 'Stockade'],
                    'Sunken hold': ['Sunken Hold', 'Flooded Hold'], 'Smuggler cave': ['Smugglers\' Cut', 'Runners\' Cave'],
                    'Reactor ruin': ['Reactor Ruin', 'Coolant Works'], 'Lab': ['Laboratory', 'Medbay'], 'Monastery ruin': ['Priory', 'Hermitage']}[stype]
            sname = f"{R.choice(g['adj'])} {R.choice(noun)}"
            while any(s['name'] == sname for s in SITES): sname = f"{R.choice(g['adj'])} {R.choice(noun)}"
        srow = loc(lid, 'Choir vault' if vid else 'Site', reg, sname, sx, sy, tags=f'site;{stype.lower()};radiant',
                   gate='Choir Seal Key or Choir standing Friendly' if vid else '')
        ent = anchor(reg, sx + 12, sy - 12, 'Site entrance', lid)
        tmpl = STEMPL[stype]
        rooms = R.randint(*tmpl[2]); length = R.randint(*tmpl[3])
        encs = [encounter(srow, R.choice(tmpl[5])) for _ in range(max(3, rooms // 2))]
        end_boss = bossinfo[0] if bossinfo else ''
        if end_boss: arena(end_boss, srow, ent)
        else: encs.append(encounter(srow, 'ENT_KEEPER'))
        inner = anchor(reg, sx - 10, sy + 14, 'Site interior', lid, z=srow['z_m'] - 20) if length >= 20 else None
        if not uq:
            uq = [u for rg in sorted(uniq_pool, key=lambda k: abs(int(k[-2:]) - rr)) for u in uniq_pool[rg] if u not in unique_used]
        reward = uq.pop(0) if uq else 'ITM_LT_ARTS'
        unique_used.add(reward)
        ls = lore_sites[si - 1] if si <= len(lore_sites) else ''
        if ls:
            used_old.add(ls); loc(ls, 'Lore site', reg, f'Lore site, {sname}', sx + 5, sy + 5, z=srow['z_m'] - 10, parent=lid)
        ch = take_old(reg, 'Small chest')
        if ch: loc(ch, 'Small chest', reg, f'Small chest, {sname}', sx - 6, sy + 3, z=srow['z_m'] - 12, parent=lid)
        if stype in ('Wreck section', 'Lab', 'Sunken hold', 'Reactor ruin', 'Fort'):
            cr = take_old(reg, 'Shard crate')
            if cr: loc(cr, 'Shard crate', reg, f'Shard crate, {sname}', sx + 4, sy - 6, z=srow['z_m'] - 12, parent=lid)
        SITES.append(dict(loc_id=lid, region=reg, name=sname, site_type=stype, template=tmpl[0], level=srow['level'],
                          floors=R.randint(*tmpl[1]), rooms=rooms, path_min=length, entrance_anchor=ent['loc_id'],
                          interior_anchor=inner['loc_id'] if inner else '', shortcut=R.choice(tmpl[4]),
                          end=f'Site boss {end_boss}' if end_boss else 'Site keeper elite', encounters=' '.join(encs),
                          unique_reward=reward, lore_site=ls, puzzle=R.choice(tmpl[6]) if tmpl[6] else ''))

    # Choir site (one per region, hidden, grants a Resonance)
    rid, cn = CHOIR[reg]
    cx_, cy_ = place(reg, 300, tband=(0.3, 0.9))
    crow = loc(f'LOC_CHOIR_{reg}', 'Choir site', reg, cn, cx_, cy_, gate='Hidden: entrance shows only after a Shard-note hint or Ostra line within 40 m',
               tags='secret;resonance', notes=f'Grants {rid}; short trial (3 rooms, 12-15 min), no boss')
    anchor(reg, cx_ + 10, cy_ + 10, 'Site entrance', crow['loc_id'])
    encounter(crow, 'ENT_ELITE')

    # Field bosses
    for fb in FIELD[reg]:
        fx, fy = place(reg, 350, tband=(0.25, 0.85))
        frow = loc(f'LOC_FB_{fb.replace("ACT_BOSS_", "")}', 'Field boss', reg, f"{bosses[fb]['Boss']} grounds", fx, fy,
                   level=bosses[fb]['Level'], tags='field boss', notes=FIELD_COND.get(fb, ''))
        a = anchor(reg, fx + 110, fy - 60, 'Field', frow['loc_id'], note='Rest point near a field boss')
        arena(fb, frow, a)

    # Small POIs: 35 (plan 30-40)
    POI_T = [('Faction camp', 'ENT_CAMP'), ('Ruin', 'ENT_AMBUSH'), ('Wreck fragment', 'ENT_PATROL'), ('Wayshrine', ''),
             ('Watchtower', 'ENT_GUNLINE'), ('Overturned cart', 'ENT_AMBUSH'), ('Overlook', ''), ('Hermit hut', ''),
             ('Grave field', 'ENT_HORDE'), ('Shard crater', 'ENT_ELITE'), ('Hunting ground', 'ENT_CRT_PACK'),
             ('Lair', 'ENT_CRT_SOLO'), ('Trader stop', ''), ('Vehicle depot', 'ENT_FORT')]
    for i in range(1, 36):
        kind, tpl = POI_T[(i - 1) % len(POI_T)]
        px, py = place(reg, 160)
        prow = loc(f'LOC_POI_{reg}_{i:02d}', 'POI', reg, f"{R.choice(g['adj'])} {kind}", px, py, tags=kind.lower())
        if tpl: encounter(prow, tpl)
        if kind == 'Vehicle depot':
            VEH.append(dict(loc_id=prow['loc_id'], region=reg, vehicles=g['vehicles'], x_m=px, y_m=py))
        if kind == 'Trader stop':
            prow['notes'] = f'Route stop for ACT_NPC_VEN_TRADER_{reg}'
        ch = take_old(reg, 'Small chest') if i % 3 != 0 else None
        if ch: loc(ch, 'Small chest', reg, f"Small chest, {prow['name']}", px + 4, py + 4, parent=prow['loc_id'])

    # Field Anchors on a jittered 500 m hex grid (plan 400-600 m), skipping spots near other Anchors
    (cx, cy), (rx, ry) = g['c'], g['r']; sp = 500
    for j, yy in enumerate(range(int(cy - ry), int(cy + ry) + 1, int(sp * 0.866))):
        for xx in range(int(cx - rx) + (sp // 2 if j % 2 else 0), int(cx + rx) + 1, sp):
            x, y = xx + R.uniform(-60, 60), yy + R.uniform(-60, 60)
            if not inside(reg, x, y, 0.95): continue
            if any((x - a['x_m']) ** 2 + (y - a['y_m']) ** 2 < 300 ** 2 for a in ANCH if a['region'] == reg): continue
            anchor(reg, round(x), round(y), 'Field', '')

    # Fill gaps: add Anchors where any point is more than 300 m from one (keeps spacing at or under 600 m)
    samples = [(x, y) for x in range(int(cx - rx), int(cx + rx), 60) for y in range(int(cy - ry), int(cy + ry), 60) if inside(reg, x, y, 0.95)]
    while True:
        fa = [(a['x_m'], a['y_m']) for a in ANCH if a['region'] == reg]
        d, p = max((min(math.dist(sm, q) for q in fa), sm) for sm in samples)
        if d <= 300: break
        anchor(reg, p[0], p[1], 'Field', '')

    # Patrols on the road network (roads = minimum spanning tree over Anchors)
    ra = [a for a in ANCH if a['region'] == reg and a['anchor_type'] in ('Field', 'Town', 'Relay', 'Site entrance')]
    for i in range(10):
        a = R.choice(ra)
        prow = loc(f'LOC_PATROL_{reg}_{i + 1:02d}', 'Patrol route', reg, f'Patrol near {a["loc_id"]}', a['x_m'] + 60, a['y_m'] + 40, tags='patrol')
        encounter(prow, 'ENT_PATROL' if i % 3 else 'ENT_CRT_PACK', cond='Night: +1 skirmisher' if i % 4 == 0 else '')

    # Remaining chests, crates, doors, gather nodes, lore sites: scatter with parents left blank
    for kind in ('Small chest', 'Shard crate', 'Locked door', 'Lore site', 'Gather node'):
        while True:
            lid = take_old(reg, kind)
            if not lid: break
            x, y = place(reg, 25 if kind == 'Gather node' else 60)
            gate = ''
            if kind == 'Locked door':
                ky = [k_['item_id'] for k_ in keys if f'({reg[-2:]})' in k_['name']] or [keys[0]['item_id']]
                gate = f'Key {R.choice(ky)}'
            n = 'Lore site, ' + nm if kind == 'Lore site' else f'{kind}, {nm}'
            if kind == 'Lore site' and any(t['region'] == reg and t['kind'] == 'Settlement' for t in LOCS):
                tw = [t for t in LOCS if t['region'] == reg and t['kind'] == 'Settlement'][0]
                x, y = tw['x_m'] + R.randint(-40, 40), tw['y_m'] + R.randint(-40, 40)
            loc(lid, kind, reg, n, x, y, gate=gate,
                tags=re.sub(r'LOC_NODE_(.*)_REG_.*', r'\1', lid).lower() if kind == 'Gather node' else '')

    # Secrets: 15 per region
    SEC_T = ['Illusory wall', 'Illusory wall', 'Illusory wall', 'Hidden ledge path', 'Hidden ledge path', 'Breakable floor',
             'Breakable floor', 'Resonance gate', 'Night-only event', 'Hidden merchant', 'Shard-note cache', 'Sunken chest',
             'Rooftop route', 'Vehicle jump', 'Echo duel']
    for i, st in enumerate(SEC_T, 1):
        host = R.choice([s for s in SITES if s['region'] == reg] + [l for l in LOCS if l['region'] == reg and l['kind'] == 'POI'])
        hx = [l for l in LOCS if l['loc_id'] == host['loc_id']][0]
        srow = loc(f'LOC_SEC_{reg}_{i:02d}', 'Secret', reg, f'{st} at {host["name"]}', hx['x_m'] + R.randint(-30, 30), hx['y_m'] + R.randint(-30, 30),
                   parent=host['loc_id'], tags='secret')
        hint = {'Illusory wall': 'Hit the wall; cracked mortar and a draft of Shard light', 'Hidden ledge path': 'Ledges painted with old hull stencils',
                'Breakable floor': 'Cracked plate with a hollow sound when walked on', 'Resonance gate': 'Choir glyph on the door',
                'Night-only event': 'Lantern lights up at 20:00', 'Hidden merchant': 'Footprints lead behind a waterfall or wreck panel',
                'Shard-note cache': 'A pre-placed Shard-note points to it', 'Sunken chest': 'Glint under water or ash',
                'Rooftop route': 'Climbable vines or cables on a wall', 'Vehicle jump': 'Ramp line visible from the road', 'Echo duel': 'Echo ghost kneeling at a grave'}[st]
        gate = {'Resonance gate': 'RES_GRAVITYLIFT or RES_SHARDWALL', 'Vehicle jump': 'Skimmer or Strider double jump'}.get(st, '')
        SECRETS.append(dict(loc_id=srow['loc_id'], region=reg, secret_type=st, host_loc=host['loc_id'], hint=hint, requirement=gate,
                            reward=''))

# Tonic Seeds (8) and Tonic Distillations (8) go into secrets, at least one per region, rest in later regions
for item, n in (('ITM_CON_TNC_SEED', 8), ('ITM_CON_TNC_DISTIL', 8)):
    regs = ['REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06', 'REG_05', 'REG_06']
    for reg in regs[:n]:
        s = R.choice([s for s in SECRETS if s['region'] == reg and not s['reward']]); s['reward'] = item
for s in SECRETS:
    if not s['reward']:
        s['reward'] = R.choice(['Unique site reward pool', 'ITM_MAT_STAR_01 x1', 'Region loot table chest', 'Lore item and Shard Dust x5', 'Seals: none (campaign)'])
        if s['secret_type'] == 'Hidden merchant': s['reward'] = 'Hidden stock: Rare weapon arts (ITM_LT_ARTS)'

# ================================================================= HUB, UNDERVAULT, QUIET, ENDGAME
hubx, huby = HUB['c']
DIST = [('LOC_LANTERN_HOLD', 'Hub', 'Lantern Hold (whole city)', 0, 0, 'Meridian bridge section; no combat'),
        ('LOC_HUB_ANCHORPLAZA', 'Hub district', 'Anchor Plaza', 0, 0, 'Hub Anchor, Echo shrine, Shard-note board'),
        ('LOC_HUB_FLIGHTDECK', 'Hub district', 'Flight Deck Market', 120, -60, 'Armorer, Clothier, Apothecary, Tinker, Quartermaster stalls'),
        ('LOC_HUB_CHAPEL', 'Hub district', 'Bridge Chapel', -120, 80, 'Lantern Church hall; Archivist Oswin Hale'),
        ('LOC_HUB_MUSTER', 'Hub district', "Knights' Muster", -160, -40, 'Hull Knights hall; Knight-Commander Iselde Marr'),
        ('LOC_HUB_DOCKS', 'Hub district', 'Salvage Docks', 200, 90, "Salvagers' Guild hall; Guildmistress Petra Quell"),
        ('LOC_HUB_WHISPER', 'Hub district', 'Whisper Gallery', -60, -150, 'Quiet Hand hall (hidden door); The Speaker; invasion toggle'),
        ('LOC_HUB_LENSLOFT', 'Hub district', 'Lens Loft', 40, 170, 'Choir hall; Precentor Amaury Lisk; Choir Archivist vendor'),
        ('LOC_HUB_ASCENSION', 'Hub district', 'Ascension Lift', 0, 220, 'Gate to the Quiet (Act 3) and the raid'),
        ('LOC_HUB_PROVING', 'Hub district', 'Proving Deck', 230, -120, 'Arena PvP lobby; Seal Warden'),
        ('LOC_HUB_WARDROBE', 'Hub district', 'Wardrobe Shop', 160, 30, 'Cosmetics shop, real-money prices'),
        ('LOC_HUB_FORGE', 'Hub district', 'Keel Forge', -200, 120, 'Smithing, Rites, Tinkering and Brewing benches'),
        ('LOC_HUB_STRIKEMAP', 'Hub district', 'Navigation Table', 60, 60, 'Strike and Hollowed Citadel launcher')]
for lid, kind, name, dx, dy, note in DIST:
    used_old.add(lid)
    loc(lid, kind, 'REG_HUB', name, hubx + dx, huby + dy, z=HUB['z'], layer='Hub', parent='' if lid == 'LOC_LANTERN_HOLD' else 'LOC_LANTERN_HOLD',
        level='', tags='hub', notes=note)
anchor('REG_HUB', hubx, huby, 'Hub', 'LOC_HUB_ANCHORPLAZA', layer='Hub', z=HUB['z'], level='')

# NPC placement (vendors, leaders, companion recruit spots; companions default, campaign thread may move them)
NPC_AT = {'ACT_NPC_HULLKNIGHT_COMMANDER': 'LOC_HUB_MUSTER', 'ACT_NPC_LANTERN_ARCHIVIST': 'LOC_HUB_CHAPEL', 'ACT_NPC_SALVAGER_BOSS': 'LOC_HUB_DOCKS',
          'ACT_NPC_QUIETHAND_SPEAKER': 'LOC_HUB_WHISPER', 'ACT_NPC_CHOIR_PRECENTOR': 'LOC_HUB_LENSLOFT', 'ACT_NPC_VEN_APOTHECARY': 'LOC_HUB_FLIGHTDECK',
          'ACT_NPC_VEN_ARCHIVIST': 'LOC_HUB_LENSLOFT', 'ACT_NPC_VEN_ARMORER': 'LOC_HUB_FLIGHTDECK', 'ACT_NPC_VEN_CLOTHIER': 'LOC_HUB_FLIGHTDECK',
          'ACT_NPC_VEN_QUARTERMASTER': 'LOC_HUB_FLIGHTDECK', 'ACT_NPC_VEN_SEALS': 'LOC_HUB_PROVING', 'ACT_NPC_VEN_TINKER': 'LOC_HUB_FLIGHTDECK',
          'ACT_NPC_ECHO': 'LOC_HUB_ANCHORPLAZA (summoned at any Anchor)',
          'ACT_CMP_C1': 'LOC_TOWN_REG_01_01', 'ACT_CMP_C2': 'LOC_TOWN_REG_05_01', 'ACT_CMP_C3': 'LOC_TOWN_REG_02_01', 'ACT_CMP_C4': 'LOC_HUB_WHISPER',
          'ACT_CMP_C5': 'LOC_TOWN_REG_04_02', 'ACT_CMP_C6': 'LOC_TOWN_REG_03_02', 'ACT_CMP_C7': 'LOC_TOWN_REG_03_01', 'ACT_CMP_C8': 'LOC_UV_REG_02_S02'}
NPCROWS = []
for n in npcs:
    a = n['act_id']
    if a.startswith('ACT_NPC_VEN_TRADER_'):
        reg = a[-6:]; stops = [l['loc_id'] for l in LOCS if l['region'] == reg and 'Trader stop' in l['name']]
        towns = [l['loc_id'] for l in LOCS if l['region'] == reg and l['kind'] == 'Settlement']
        NPCROWS.append(dict(act_id=a, name=n['name'], home_loc=towns[0], schedule='Route: ' + ' > '.join(towns[:1] + stops) + ' (1 stop per 6 game hours)'))
    else:
        NPCROWS.append(dict(act_id=a, name=n['name'], home_loc=NPC_AT.get(a, ''), schedule='Recruit spot until recruited, then Lantern Hold' if a.startswith('ACT_CMP') else 'Fixed; sleeps 23:00-06:00 behind the stall'))

# Undervault: three sections under Saltmere, Thornwood and Rimefall, joined by the Spine Tunnels under the hub
UV = {'REG_02': ('Drowned Cargo Lift', 'Cargo Vaults', (30, 42)), 'REG_03': ('Root Shaft', 'Weave Caverns', (42, 56)), 'REG_05': ('Rime Well', 'Frozen Sumps', (56, 70))}
UV_SITES = ['Cargo bay', 'Weave grotto', 'Shard vein gallery', 'Collapsed tram station', 'Crawler nest', 'Sealed reactor cell']
REG['REG_U'] = dict(fac=EXTRA_FAC['REG_U'])
for reg, (ename, sec, (l0, l1)) in UV.items():
    gx, gy = REG[reg]['c']; ox, oy = gx - 250, gy - 200
    erow = loc(f'LOC_UV_ENTRY_{reg[-2:]}', 'Undervault entry', reg, f'{ename} ({regions[reg]["name"]})', round(ox), round(oy),
               tags='undervault;entry', notes=f'Leads down to {sec}')
    anchor(reg, round(ox) + 15, round(oy) + 10, 'Site entrance', erow['loc_id'])
    for i in range(1, 7):
        x = round(gx + 520 * math.cos(i * 1.05)); y = round(gy + 420 * math.sin(i * 1.05)); lv = round(l0 + (l1 - l0) * i / 6)
        srow = loc(f'LOC_UV_{reg}_S{i:02d}', 'Undervault site', 'REG_U', f'{sec}: {UV_SITES[i - 1]}', x, y, z=-60 - i * 25, layer='Undervault',
                   parent=erow['loc_id'], level=lv, tags='undervault')
        for tpl in R.sample(['ENT_HORDE', 'ENT_AMBUSH', 'ENT_ELITE', 'ENT_CRT_SOLO', 'ENT_CRT_PACK', 'ENT_FORT'], 2):
            encounter(srow, tpl, reg='REG_U')
        if i % 2: anchor('REG_U', x + 10, y + 10, 'Undervault', srow['loc_id'], layer='Undervault', z=srow['z_m'], level=lv)
    CONNS.append(dict(con_id=f'CON_UV_{reg[-2:]}', from_reg=reg, to_reg='REG_U', type='Lift and shaft', loc_id=erow['loc_id'],
                      gate='Open (level band makes it a stretch goal)' if reg == 'REG_02' else 'Act 2', x_m=round(ox), y_m=round(oy)))
for a, b, n in (('REG_02', 'REG_03', 'Spine Tunnel East'), ('REG_02', 'REG_05', 'Spine Tunnel West')):
    mx = (REG[a]['c'][0] + REG[b]['c'][0]) // 2; my = (REG[a]['c'][1] + REG[b]['c'][1]) // 2
    trow = loc(f'LOC_UV_TUNNEL_{a[-2:]}{b[-2:]}', 'Undervault tunnel', 'REG_U', n, mx, my, z=-140, layer='Undervault', level=50, tags='undervault;tram',
               notes='Cargo tram line; tram cars are moving platforms; 2 km')
    encounter(trow, 'ENT_GUNLINE', reg='REG_U')
    anchor('REG_U', mx, my, 'Undervault', trow['loc_id'], layer='Undervault', z=-140, level=50, note='Tram platform')

# The Quiet: ring section unrolled to 4,000 x 500 m (2 km2), three sub-areas (plan 5.3)
REG['REG_Q'] = dict(fac=EXTRA_FAC['REG_Q'])
QA = [('LOC_Q_HULL', 'Outer Hull Ring', 0, 1300, (68, 72), 'Vacuum walks between airlocks; magnetic boots; planet below the floor'),
      ('LOC_Q_GALLERIES', 'Seamless Galleries', 1300, 2700, (72, 76), 'Low gravity 0.4 g: jumps x2.5 height, falls never lethal'),
      ('LOC_Q_SPINDLE', 'Core Spindle', 2700, 4000, (76, 80), 'Rotating gravity; floor becomes wall at each ring joint')]
qn = 0
for lid, name, x0, x1, (l0, l1), note in QA:
    arow = loc(lid, 'Quiet sub-area', 'REG_Q', name, (x0 + x1) // 2, 250, z=0, layer='Quiet', level=f'{l0}-{l1}', tags='act3', notes=note)
    for i in range(1, 7):
        x = x0 + (x1 - x0) * i // 7; y = 250 + (120 if i % 2 else -120); lv = round(l0 + (l1 - l0) * i / 6); qn += 1
        r_ = loc(f'LOC_Q_{lid[6:]}_{i:02d}', 'Quiet room', 'REG_Q', f'{name}, room {i}', x, y, z=0, layer='Quiet', parent=lid, level=lv)
        encounter(r_, R.choice(['ENT_FORT', 'ENT_GUNLINE', 'ENT_AMBUSH', 'ENT_ELITE']), reg='REG_Q')
        if i in (1, 4): anchor('REG_Q', x, y, 'Quiet', r_['loc_id'], layer='Quiet', z=0, level=lv)
core = loc('LOC_Q_CORE', 'Quiet sub-area', 'REG_Q', 'The Hush Core', 3950, 250, z=0, layer='Quiet', parent='LOC_Q_SPINDLE', level=80,
           tags='final boss;endings', notes='Final campaign boss arena; three ending sequences branch from here')
ca = anchor('REG_Q', 3900, 250, 'Quiet', 'LOC_Q_CORE', layer='Quiet', z=0, level=80, note='Before the final boss')
arena('ACT_BOSS_QUIETCORE', core, ca)
for kind in ('Small chest', 'Shard crate', 'Locked door', 'Lore site', 'Gather node', 'Choir vault'):
    for reg, layer, xr, yr in (('REG_Q', 'Quiet', (0, 4000), (0, 500)), ('REG_U', 'Undervault', None, None)):
        while True:
            lid = take_old(reg, kind)
            if not lid: break
            if layer == 'Quiet':
                x, y = R.randint(*xr), R.randint(*yr); lv = 68 + round(12 * x / 4000)
                par = 'LOC_Q_HULL' if x < 1300 else ('LOC_Q_GALLERIES' if x < 2700 else 'LOC_Q_SPINDLE')
            else:
                s = R.choice([l for l in LOCS if l['kind'] == 'Undervault site']); x, y, lv, par = s['x_m'] + R.randint(-40, 40), s['y_m'] + R.randint(-40, 40), s['level'], s['loc_id']
            loc(lid, kind, reg, f'{kind}, {regions[reg]["name"]}', x, y, z=0 if layer == 'Quiet' else -100, layer=layer, parent=par, level=lv)

# Raid (6 players): The Unmade Choir, four wings reusing the Quiet's kit at 80-92
RAIDW = [('ACT_BOSS_QUIETCORE', 'Wing 1: Core Breach'), ('ACT_BOSS_ARCHIVIST', 'Wing 2: The Archive Ring'),
         ('ACT_BOSS_MERIDIANGHOST', "Wing 3: Meridian's Echo"), ('ACT_BOSS_UNMADECHOIR', 'Wing 4: The Unmade Choir')]
END = []
for i, (b, nm) in enumerate(RAIDW, 1):
    r_ = loc(f'LOC_END_RAID_{i:02d}', 'Raid wing', 'REG_Q', nm, 500 + i * 800, -400, z=0, layer='Quiet (raid instance)', level=bosses[b]['Level'],
             tags='raid;6 players', notes='Opens from LOC_HUB_ASCENSION after the campaign; weekly lockout')
    if b != 'ACT_BOSS_QUIETCORE': arena(b, r_, None)
    else: ARENAS[-1]['notes'] = 'Campaign solo fight here; raid version in LOC_END_RAID_01 reuses the arena with 6-player mechanics'
    END.append(dict(loc_id=r_['loc_id'], activity='Raid', name=nm, players='6', level=bosses[b]['Level'], space='New wing built from the Quiet kit',
                    boss=b, length_min=R.randint(35, 60), reward='Raid loot (ITM_LT_BOSS_*) and Seals'))
# Strikes (3 players): one per region at launch, routed through existing sites, ending at a remixed field arena
for i, reg in enumerate(['REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06'], 1):
    s1, s2 = [s for s in SITES if s['region'] == reg][4:6]; fb = FIELD[reg][0]
    END.append(dict(loc_id=f'LOC_END_STRIKE_{i:02d}', activity='Strike', name=f'{regions[reg]["name"]} Strike', players='3', level='75-80',
                    space=f'{s1["loc_id"]} > open ground > {s2["loc_id"]} > LOC_FB_{fb.replace("ACT_BOSS_", "")}', boss=fb + ' (empowered)',
                    length_min=R.randint(20, 30), reward='REG_END loot band'))
    END.append(dict(loc_id=f'LOC_END_HCIT_{i:02d}', activity='Hollowed Citadel', name=f'Hollowed {REG[reg]["cit"][0]}', players='1-4', level='75-80',
                    space=f'LOC_CIT_{reg} with Hollowing grade, remixed patrols, two zones sealed, shortcuts pre-opened',
                    boss=f'{CITB[reg]} and {SHARD[reg]} (Hollowed)', length_min=R.randint(45, 70), reward='REG_END loot band; seasonal rotation'))
ARENA_MAPS = [('Flight Deck', 'LOC_HUB_PROVING', 'Symmetric, two levels, 60 x 40 m'), ('Salt Pans', 'LOC_POI_REG_02_14', 'Open with vehicle lanes, 120 x 90 m'),
              ('Redbark Mill', 'LOC_POI_REG_03_07', 'Tight, three lanes, 70 x 50 m'), ('Glass Lens', 'LOC_POI_REG_04_21', 'Long sightlines, 110 x 50 m'),
              ('Bell Cloister', 'LOC_POI_REG_05_14', 'Vertical, four floors, 50 x 50 m'), ('Lifted Steps', 'LOC_POI_REG_06_28', 'Floating platforms with jump pads, 80 x 80 m')]
for i, (nm, src, desc) in enumerate(ARENA_MAPS, 1):
    END.append(dict(loc_id=f'LOC_END_ARENA_{i:02d}', activity='Arena PvP 3v3', name=nm, players='6', level='Normalized', space=f'Separate map themed on {src}; {desc}',
                    boss='', length_min=10, reward='Seals; power weapons on timers (items/arena_power_weapons.csv)'))
for e in END:
    if not any(l['loc_id'] == e['loc_id'] for l in LOCS):
        loc(e['loc_id'], e['activity'], 'REG_END', e['name'], 0, 0, z=0, layer='Instance', level=e['level'], tags='endgame', notes=e['space'])

# ================================================================= CONNECTIONS AND GATES
CON_DEF = [
 ('CON_01', 'REG_01', 'REG_HUB', 'Road', 'Meridian Spine Road', 'Open after the first town (slice path)'),
 ('CON_02', 'REG_01', 'REG_02', 'Citadel pass', 'Spine Keep gatehouse', 'Defeat ACT_BOSS_SPINEGATE, or take the Ash Cliffs side path (level 14+ enemies)'),
 ('CON_03', 'REG_HUB', 'REG_02', 'Causeway', 'Flight Deck Causeway', 'Opens from the Saltmere side (one-way gate)'),
 ('CON_04', 'REG_02', 'REG_05', 'Dike road', 'Western Dikes', 'Act 2: storm wall falls when ACT_BOSS_CORSA dies'),
 ('CON_05', 'REG_02', 'REG_04', 'Mountain pass', 'Stormbreak Pass', 'Act 2: ACT_BOSS_CORSA defeated'),
 ('CON_06', 'REG_HUB', 'REG_03', 'Gate', 'Briar Gate', 'Act 2: ACT_BOSS_CORSA defeated'),
 ('CON_07', 'REG_01', 'REG_03', 'Trench', 'Ember Trench', 'Open but dangerous (Thornwood level 20+ past the trench mouth)'),
 ('CON_08', 'REG_03', 'REG_06', 'Bridge', 'Root Bridge', 'Act 2 (open; level band 55+ is the gate)'),
 ('CON_09', 'REG_04', 'REG_06', 'Drop', 'Glassfall Descent', 'One-way drop; a lift sends it back once lit from below'),
 ('CON_10', 'REG_01', 'REG_05', 'Stair', 'Cinder Stair', 'One-way: unbarred from the Rimefall side'),
 ('CON_11', 'REG_03', 'REG_04', 'Road', 'Pylon Road', 'Act 2'),
 ('CON_12', 'REG_HUB', 'REG_Q', 'Lift', 'Ascension Lift', 'Act 3: any four Shard-bearers defeated (plan 3.8); Vael and Corsa are Act 1 story bosses, so two of the four Act 2 Shard-bearers'),
]
for cid, a, b, typ, nm, gate in CON_DEF:
    pa = HUB['c'] if a == 'REG_HUB' else REG[a]['c']; pb = HUB['c'] if b == 'REG_HUB' else (REG[b]['c'] if b in REG and 'c' in REG[b] else HUB['c'])
    x, y = round((pa[0] + pb[0]) / 2), round((pa[1] + pb[1]) / 2)
    reg = a if a != 'REG_HUB' else b
    if reg == 'REG_Q': reg = 'REG_HUB'
    loc(f'LOC_{cid}', 'Connection', reg if reg in REG and 'c' in REG[reg] else 'REG_HUB', nm, x, y, z=0 if reg == 'REG_HUB' else None,
        level='' if reg == 'REG_HUB' else None, gate=gate, tags='connection')
    CONNS.append(dict(con_id=cid, from_reg=a, to_reg=b, type=typ, loc_id=f'LOC_{cid}', gate=gate, x_m=x, y_m=y))

GATES = [
 ('GATE_01', 'Leave Cinderreach for Saltmere', 'ACT_BOSS_SPINEGATE defeated, or Ash Cliffs side path', 'Act 1'),
 ('GATE_02', 'Act 2 opens (Thornwood, Glasswaste, Rimefall, Hollowdeep roads)', 'ACT_BOSS_CORSA defeated', 'Act 1 > 2'),
 ('GATE_03', 'Act 3 opens (Ascension Lift to the Quiet)', 'Any four Shard-bearers: ACT_BOSS_VAEL, ACT_BOSS_CORSA and two of the four Act 2 Shard-bearers', 'Act 2 > 3'),
 ('GATE_04', 'Choir vaults', 'Choir Seal Key (lore keys) or FAC_CHOIR standing Friendly', 'Any'),
 ('GATE_05', 'Choir sites', 'Hidden entrance revealed by a Shard-note hint or Ostra within 40 m', 'Any'),
 ('GATE_06', 'Strider mount', 'Buy the Strider Harness (ITM_CON_UTL_HARNESS, Tinker, 2,500 Ember) and tame a wild Strider (Cinderreach, Thornwood or Rimefall)', 'Act 1'),
 ('GATE_07', 'Vehicles', 'Skimmer and Hauler at Vehicle depots after the Salvagers\' Guild opening quest (QST_SG_00); Flyers by hijack only', 'Act 1'),
 ('GATE_08', 'Region map', 'Climb the region Relay Tower', 'Any'),
 ('GATE_09', 'Fast travel', 'Lit Anchors only; blocked in combat and inside a Citadel until its zone Anchor is lit', 'Any'),
 ('GATE_10', 'Endgame', 'Campaign finished: raid, strikes, Hollowed Citadels; Arena PvP from level 20', 'Endgame'),
 ('GATE_11', 'Resonance secrets', 'RES_GRAVITYLIFT (Root Choir) and RES_SHARDWALL (Cinder Choir) open optional secrets; never the main path', 'Any'),
]

# ================================================================= TRAVERSAL AND METRICS
TRAV = [
 ('TRV_WALK', 'Walk / run / sprint', 'Start', 'Run 5.0 m/s (STAT_MOVESPEED); sprint 7.5 m/s for 8 Breath/s', 'All'),
 ('TRV_JUMP', 'Jump', 'Start', 'Height 1.1 m, gap 3.0 m running; 10 Breath', 'All'),
 ('TRV_MANTLE', 'Mantle and ledge grab', 'Start', 'Mantle up to 2.0 m; no free climbing (climb only on ladders, vines, cables)', 'All'),
 ('TRV_FALL', 'Falling', 'Start', 'No damage under 6 m; damage 6-18 m; lethal over 18 m (Quiet galleries: never lethal)', 'All'),
 ('TRV_SWIM', 'Wading and swimming', 'Start', 'Wade under 1.2 m (speed x0.6); swim 2.5 m/s, no attacks, no ammo', 'REG_02 REG_03'),
 ('TRV_LADDER', 'Ladders, lifts, kick-down ladders', 'Start', 'Ladder 2 m/s; lifts 4 m/s; every site has at least one', 'All'),
 ('TRV_STRIDER', 'Strider (mount)', 'GATE_06', 'Gallop 14 m/s; double jump 6 m; glide 4:1; not in sites, Citadels, Undervault or the Quiet', 'Surface'),
 ('TRV_SKIMMER', 'Skimmer (2 seats)', 'GATE_07', 'Top speed 32 m/s; hull 600, engine 150, wheels 120 each (plan Part 1b)', 'REG_01 REG_02 REG_03 REG_04 REG_05 REG_06'),
 ('TRV_HAULER', 'Hauler (6 seats, turret)', 'GATE_07', 'Top speed 18 m/s; hull 1,800, engine 450, turret 400, wheels 300 each', 'REG_01 REG_02 REG_04 REG_05'),
 ('TRV_FLYER', 'Flyer (hijack)', 'Board a stunned enemy flyer', 'Top speed 40 m/s, ceiling 120 m above ground; hull 900, engines 200, wings 250', 'REG_02 REG_03 REG_04 REG_05 REG_06'),
 ('TRV_ANCHOR', 'Anchor fast travel', 'GATE_09', 'Between lit Anchors; load under 15 s on console (plan Phase 7)', 'All layers'),
 ('TRV_LIFTCURRENT', 'Lift currents', 'Start', 'Hollowdeep updrafts carry the player up 40 m in 5 s; glide off the top', 'REG_06'),
 ('TRV_TRAM', 'Undervault cargo trams', 'Start', 'Moving platforms on the Spine Tunnels, 12 m/s', 'REG_U'),
 ('TRV_LOWG', 'Low gravity and mag boots', 'Act 3', 'Galleries 0.4 g (jumps x2.5); Outer Hull mag boots on marked plates; Spindle gravity rotates at ring joints', 'REG_Q'),
]
FA = defaultdict(int)
for f in firearms:
    try: FA[f['weapon_class']] = max(FA[f['weapon_class']], int(float(f['falloff_end_m'])))
    except ValueError: pass
METRICS = [
 ('MET_CAPSULE', 'Player capsule', '0.45 m radius, 1.8 m tall', 'Min clearance 2.2 m'),
 ('MET_CORRIDOR_MELEE', 'Combat corridor (melee)', '4.0 m wide minimum', 'Greatswords and polearms need swing room; 2.4 m only for non-combat squeezes'),
 ('MET_DOOR', 'Doors', 'Single 1.6 m, double 3.2 m, Hauler gate 5.0 m', ''),
 ('MET_FOGGATE', 'Boss fog gate', '4.0 m wide, Anchor within 25-60 m of the gate', 'Plan 3.4: respawn near a boss'),
 ('MET_COVER_LOW', 'Low cover', '1.0 m (crouch-aim over)', 'Spacing 8-12 m in gun spaces'),
 ('MET_COVER_HIGH', 'High cover', '2.0 m, breaks line of sight for Ward recharge (4.5 s)', 'Every combat space has at least one LOS break per 15 m of front'),
 ('MET_SIGHTLINE_CQ', 'Close range space', '0-15 m', 'Shotgun, SMG, melee'),
 ('MET_SIGHTLINE_MID', 'Mid range space', '15-50 m', 'Auto rifle, pistol, Weave casts'),
 ('MET_SIGHTLINE_LONG', 'Long range space', '50-120 m', 'Scout and sniper rifles; one per region route section, never on the only path'),
 ('MET_FALLOFF', 'Firearm falloff ends (from items data)', '; '.join(f'{k} {v} m' for k, v in sorted(FA.items())), 'Long spaces should not exceed the longest falloff'),
 ('MET_ARENA_SITE', 'Site boss arena', '30-40 m diameter', ''),
 ('MET_ARENA_CIT', 'Citadel boss arena', '45-55 m', ''),
 ('MET_ARENA_SHARD', 'Shard-bearer arena', '60-70 m', 'Strider not allowed'),
 ('MET_ARENA_FIELD', 'Field boss ground', '90-150 m', 'Strider allowed'),
 ('MET_ARENA_RAID', 'Raid room', '70-90 m', 'Six-player spacing'),
 ('MET_SLOPE', 'Slopes', 'Walkable 45 deg, Strider 50 deg, vehicle 30 deg', ''),
 ('MET_LANDMARK', 'Landmark rhythm', 'A new landmark on screen every 40-60 s of riding (560-840 m at 14 m/s)', 'Plan 5.1'),
 ('MET_ANCHOR', 'Anchor spacing', '400-600 m in the field; one at every site entrance', 'Plan 3.7'),
 ('MET_SITE_LOOP', 'Site loop', '10-25 min; ends in a shortcut to the entrance and a unique reward', 'Plan 3.3 and 3.7'),
 ('MET_CITADEL', 'Citadel path', '2-3 h first play, side-view flow with every shortcut marked; 60% of testers find each shortcut', 'Plan 5.2'),
 ('MET_PARTICLES', 'VFX cover limit', '30% of screen in 4-player co-op', 'Visual Bible'),
]
# ================================================================= PLAN FIXES (applied after generation so IDs and coordinates stay stable)
# Plan Phase 3.1: the slice enters the Citadel and beats "its first boss" inside the Citadel's first third,
# so the Citadel boss sits in zone 3 (end of the first third) and zone 5 becomes a normal zone.
locmap = {l['loc_id']: l for l in LOCS}
for reg in [r for r in REG if 'c' in REG[r]]:
    z3 = next(z for z in ZONES if z['loc_id'] == f'LOC_CIT_{reg}_Z3'); z5 = next(z for z in ZONES if z['loc_id'] == f'LOC_CIT_{reg}_Z5')
    l3, l5 = locmap[z3['loc_id']], locmap[z5['loc_id']]
    for k in ('name', 'path_min', 'style', 'boss'):
        z3[k], z5[k] = z5[k], z3[k]
    l3['name'], l5['name'] = l5['name'], l3['name']
    z5['encounters'], z3['encounters'] = z3['encounters'], ''
    for e in ENC:
        if e['loc_id'] == z3['loc_id']:
            e.update(loc_id=z5['loc_id'], x_m=l5['x_m'], y_m=l5['y_m'], level=l5['level'])
    a = next(a for a in ARENAS if a['boss'] == CITB[reg])
    a.update(loc_id=z3['loc_id'], x_m=l3['x_m'], y_m=l3['y_m'], nearest_anchor=z3['anchor'])
    # Plan 2.5 asks for three shortcuts per 30-minute Citadel quarter: 14 shortcuts per Citadel
    SC2 = {1: 'Winch gate from Z2 back to the Z1 Anchor', 2: 'Barbican winch gate opens back to Z1; side postern to the field',
           3: 'Lift from the boss antechamber to the Z1 Anchor', 4: 'One-way door to the Z3 Anchor; rope drop to Z2',
           5: 'Kick-down ladder to the Z4 roof; chain gate to the Z3 Anchor', 6: 'Drop-down plank to the Z5 Anchor; flooded tunnel to Z2',
           7: 'Bridge lowered from Z7 to Z4 (big loop); service lift to the Z6 Anchor', 8: 'Elevator from the seat to Z1 (exit)'}
    for z in ZONES:
        if z['citadel'] == f'LOC_CIT_{reg}': z['shortcut'] = SC2[z['order']]
    locmap[f'LOC_CIT_{reg}']['notes'] = locmap[f'LOC_CIT_{reg}']['notes'].replace('Citadel boss', 'Citadel boss (zone 3)').replace('Shard-bearer ACT', 'Shard-bearer (zone 8) ACT')
# Plan Part 1b (Skyrim take): cap only the first region's sites; later sites have a level floor and float up inside the band
for s in SITES:
    s['level_rule'] = 'Fixed level' if s['region'] == 'REG_01' else f"Floor {s['level']}, floats up to band max {lvl_band(s['region'])[1]}"
# Plan pillar "The horizon is a promise": every landmark holds hand-made content, so link each to the nearest site or POI
for m in LMK:
    lm = locmap[m['loc_id']]
    if m['role'] == 'Navigation':
        near = min((l for l in LOCS if l['region'] == lm['region'] and l['kind'] in ('Site', 'POI', 'Choir vault') and l['layer'] == 'Surface'),
                   key=lambda l: math.dist((l['x_m'], l['y_m']), (lm['x_m'], lm['y_m'])))
        m['holds'] = near['loc_id']
    else: m['holds'] = lm['loc_id']
# Plan Part 1b (Fallout 76 and Destiny takes): public events on a short timer in each region. Separate RNG so nothing above moves.
R2 = random.Random(777)
EVT = ['Shard-fall', 'Remnant convoy', 'Hollowed surge', 'Thorn raid on a caravan']
for reg in [r for r in REG if 'c' in REG[r]]:
    for i, ev in enumerate(EVT, 1):
        host = R2.choice([l for l in LOCS if l['region'] == reg and l['kind'] == 'POI'])
        erow = loc(f'LOC_EVT_{reg}_{i:02d}', 'Public event', reg, f"{ev} at {host['name']}", host['x_m'] + 40, host['y_m'] - 40, parent=host['loc_id'],
                   tags='public event;co-op', notes='Starts every 10-15 min when a player is within 300 m; 1-4 players; plan Part 1b takes')
        save = R; globals()['R'] = R2
        encounter(erow, 'ENT_HORDE' if 'surge' in ev else ('ENT_GUNLINE' if 'convoy' in ev else 'ENT_CAMP'), cond='Public event wave 1 of 3')
        globals()['R'] = save

# Continuity CP-11 (2026-10-03 vault names, 2026-10-06 all repeats and generic labels): name_fixes.csv from tools/unique_names.py
if os.path.exists(os.path.join(OUT, 'name_fixes.csv')):
    with open(os.path.join(OUT, 'name_fixes.csv'), encoding='utf-8') as _f:
        _fix = {r['loc_id']: r['new_name'] for r in csv.DictReader(_f)}
    for _r in LOCS + SITES:
        _r['name'] = _fix.get(_r['loc_id'], _r['name'])
# ================================================================= CHECKS
CHECK = []
ids = [l['loc_id'] for l in LOCS]
dup = {i for i in ids if ids.count(i) > 1}
CHECK.append(('Unique LOC ids', 'PASS' if not dup else 'FAIL ' + ' '.join(sorted(dup)[:10])))
missing = [r['loc_id'] for r in old_locs if r['loc_id'] not in set(ids)]
CHECK.append(('Every data/world/locations.csv id placed', 'PASS' if not missing else f'FAIL {len(missing)} missing: ' + ' '.join(missing[:10])))
for reg in ['REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06']:
    fa = [(a['x_m'], a['y_m']) for a in ANCH if a['region'] == reg and a['layer'] == 'Surface']
    nn = [min(math.dist(p, q) for q in fa if q != p) for p in fa]
    (cx, cy), (rx, ry) = REG[reg]['c'], REG[reg]['r']
    worst = 0
    for _ in range(3000):
        x, y = R.uniform(cx - rx, cx + rx), R.uniform(cy - ry, cy + ry)
        if inside(reg, x, y, 0.95): worst = max(worst, min(math.dist((x, y), q) for q in fa))
    area = math.pi * rx * ry / 1e6
    ns = sum(1 for s in SITES if s['region'] == reg); np_ = sum(1 for l in LOCS if l['region'] == reg and l['kind'] == 'POI')
    nt = sum(1 for l in LOCS if l['region'] == reg and l['kind'] == 'Settlement')
    CHECK.append((f'{reg} area {area:.2f} km2 (plan about 3.5)', 'PASS' if 3.2 <= area <= 3.8 else 'FAIL'))
    CHECK.append((f'{reg} sites {ns} (15-20), POIs {np_} (30-40), towns {nt} (2-3)', 'PASS' if 15 <= ns <= 20 and 30 <= np_ <= 40 and 2 <= nt <= 3 else 'FAIL'))
    CHECK.append((f'{reg} Anchors {len(fa)}; farthest point from any Anchor {worst:.0f} m (target under 300 m = 600 m spacing)', 'PASS' if worst <= 330 else 'WARN'))
bl = {a['boss'] for a in ARENAS}
CHECK.append((f'Boss arenas {len(bl)} of {len(bosses)}', 'PASS' if bl == set(bosses) else 'FAIL missing ' + ' '.join(sorted(set(bosses) - bl))))
act_ids = {e['ACT_ID'] for e in enemies} | {c['ACT_ID'] for c in creatures}
bad = {a.split(' x')[0] for e in ENC for a in e['actors'].split('; ') if a.split(' x')[0] not in act_ids}
CHECK.append(('Every encounter ACT_ id exists in data/actors', 'PASS' if not bad else 'FAIL ' + ' '.join(sorted(bad))))
offband = [e['enc_id'] for e in ENC if isinstance(e['level'], int) and e['region'] in regions and not (int(regions[e['region']]['level_min']) <= e['level'] <= int(regions[e['region']]['level_max']))]
CHECK.append(('Encounter levels inside their region band', 'PASS' if not offband else f'FAIL {len(offband)}'))
CHECK.append(('Tonic Seeds placed 8, Distillations 8', 'PASS' if sum(s['reward'] == 'ITM_CON_TNC_SEED' for s in SECRETS) == 8 and sum(s['reward'] == 'ITM_CON_TNC_DISTIL' for s in SECRETS) == 8 else 'FAIL'))
CHECK.append(('Citadel boss in zone 3 for every Citadel (plan 3.1 slice)', 'PASS' if all(z['boss'] in CITB.values() for z in ZONES if z['order'] == 3) else 'FAIL'))
CHECK.append(('Unique site rewards not reused', 'PASS' if len({s['unique_reward'] for s in SITES}) == len(SITES) else 'WARN some sites share a fallback reward'))

# ================================================================= WRITE TABLES
LOCS.sort(key=lambda l: (l['region'], l['kind'], l['loc_id']))
# FROZEN 2026-10-03: level threads and the campaign key to locations.csv. Never overwrite it; a regen goes to
# locations.regen.csv for comparison, and real changes go to data-requests.csv for the continuity pass.
wr('locations.regen.csv' if os.path.exists(os.path.join(OUT, 'locations.csv')) else 'locations.csv', LOCS)
wr('regions_layout.csv', [dict(reg_id=reg, name=regions[reg]['name'], act=g['act'], level_min=lvl_band(reg)[0], level_max=lvl_band(reg)[1],
    center_x_m=g['c'][0], center_y_m=g['c'][1], radius_x_m=g['r'][0], radius_y_m=g['r'][1], area_km2=round(math.pi * g['r'][0] * g['r'][1] / 1e6, 2),
    elevation_m=f"{g['z'][0]}-{g['z'][1]}", entry_bearing_deg=g['entry'], apex_bearing_deg=g['apex'],
    biomes='; '.join(f'{b} {int(s * 100)}%' for b, s in g['biomes']), weather=g['weather'],
    factions='; '.join(f'FAC_{f} {int(w * 100)}%' for f, w in g['fac'].items()), vehicles=g['vehicles'],
    citadel=f'LOC_CIT_{reg}', shard_bearer=SHARD[reg], citadel_boss=CITB[reg], field_bosses=' '.join(FIELD[reg]), site_bosses=' '.join(SITEB[reg]),
    choir_site=f'LOC_CHOIR_{reg}', relay=f'LOC_RELAY_{reg}', undervault_entry=f'LOC_UV_ENTRY_{reg[-2:]}' if reg in UV else '',
    level_rule='Level rises from the entry edge to the Citadel (Shard-bearer) edge; filler scales inside the band only')
    for reg, g in REG.items() if 'c' in g] + [
    dict(reg_id='REG_HUB', name='Lantern Hold', act='All', level_min='', level_max='', center_x_m=HUB['c'][0], center_y_m=HUB['c'][1], radius_x_m=HUB['r'][0],
         radius_y_m=HUB['r'][1], area_km2=round(math.pi * 300 * 250 / 1e6, 2), elevation_m='120 (bridge deck)', biomes='City in the Meridian bridge', factions='No combat'),
    dict(reg_id='REG_U', name='The Undervault', act='Act 1 to 2', level_min=30, level_max=70, area_km2=3.0, elevation_m='-60 to -210',
         biomes='Cargo Vaults (under Saltmere, 30-42); Weave Caverns (under Thornwood, 42-56); Frozen Sumps (under Rimefall, 56-70); Spine Tunnels join them',
         factions='; '.join(f'FAC_{f} {int(w * 100)}%' for f, w in EXTRA_FAC['REG_U'].items())),
    dict(reg_id='REG_Q', name='The Quiet', act='Act 3', level_min=68, level_max=80, area_km2=2.0, elevation_m='Orbit; local frame 4,000 x 500 m',
         biomes='Outer Hull Ring; Seamless Galleries (0.4 g); Core Spindle (rotating gravity)', factions='FAC_CHOIRBORN 100%')])
wr('connections.csv', CONNS)
wr('gates.csv', [dict(gate_id=a, what=b, requirement=c, act=d) for a, b, c, d in GATES])
wr('anchors.csv', ANCH)
wr('landmarks.csv', LMK)
wr('sites.csv', SITES)
wr('site_templates.csv', [dict(site_type=k, kit=v[0], floors=f'{v[1][0]}-{v[1][1]}', rooms=f'{v[2][0]}-{v[2][1]}', path_min=f'{v[3][0]}-{v[3][1]}',
    shortcut_forms=' | '.join(v[4]), encounter_templates=' '.join(v[5]), puzzles=' | '.join(p for p in v[6] if p),
    rule='Ends in a shortcut to the entrance and a unique reward; at least one lore item; no repeated boss') for k, v in STEMPL.items()])
wr('citadel_zones.csv', ZONES)
wr('encounters.csv', ENC)
wr('encounter_templates.csv', [dict(template=t[0], name=t[1], roles='; '.join(f'{k} x{v}' for k, v in t[2].items()) or 'Creatures', cover_points=t[3],
    fallback_points=t[4], respawn=t[5], use=t[6]) for t in TEMPLATES])
for a in ARENAS: a.setdefault('notes', '')
wr('boss_arenas.csv', ARENAS, ['boss', 'boss_name', 'class_', 'level', 'loc_id', 'region', 'layer', 'x_m', 'y_m', 'arena_hooks', 'shape', 'diameter_m',
    'cover_pieces', 'entry', 'nearest_anchor', 'anchor_run_m', 'phase_change', 'hazards', 'condition', 'notes'])
wr('secrets.csv', SECRETS)
wr('traversal.csv', [dict(trv_id=a, name=b, unlock=c, values=d, where=e) for a, b, c, d, e in TRAV])
wr('level_metrics.csv', [dict(met_id=a, name=b, value=c, note=d) for a, b, c, d in METRICS])
wr('vehicle_depots.csv', VEH)
wr('npc_placement.csv', NPCROWS)
wr('endgame_spaces.csv', END)
wr('checks.csv', [dict(check=a, result=b) for a, b in CHECK])

REQ = [
 ('data/world/locations.csv', 'columns x_m y_m z_m layer parent_loc level gate', 'Copy from design/world/locations.csv', 'Gives every LOC_ a position; link.py should read it instead of generating bare rows'),
 ('data/world/locations.csv', 'new LOC_ kinds', 'Anchor, Relay Tower, Site, Citadel, Citadel zone, Landmark, POI, Field boss, Choir site, Secret, Patrol route, Connection, Undervault entry/site/tunnel, Quiet sub-area/room, Raid wing, Strike, Hollowed Citadel, Arena PvP 3v3, Hub district', 'Campaign and radiant quests target these'),
 ('data/actors/player_base_stats.csv', 'STAT_JUMP, STAT_MANTLE, STAT_SAFEFALL, STAT_LETHALFALL, STAT_SPRINTSPEED, STAT_SWIMSPEED', '1.1 m; 2.0 m; 6 m; 18 m; 7.5 m/s; 2.5 m/s', 'Level metrics depend on them (traversal.csv)'),
 ('data/actors/creatures.csv or new mounts table', 'Strider mount stats', 'Gallop 14 m/s, double jump 6 m, glide ratio 4:1', 'Plan 3.7 names the double jump and glide; numbers are Shardfall choices'),
 ('new data/world/vehicles.csv', 'VEH_SKIMMER, VEH_HAULER, VEH_FLYER', 'Speeds 32 / 18 / 40 m/s; part health from plan Part 1b; seats 2 / 6 / 2', 'Vehicle depots in vehicle_depots.csv'),
 ('data/items/consumables.csv', 'ITM_CON_TNC_SEED and ITM_CON_TNC_DISTIL locations', 'See secrets.csv rows with those rewards', '8 of each, one or more per region'),
 ('data/items/lore_items.csv', 'location column', 'Lore sites now sit inside sites (parent_loc in locations.csv)', 'Plan rule: at least one lore item per site; keep location as LOC_SITE_*'),
 ('data/items/*', 'unique site rewards', 'sites.csv unique_reward column (Rare and Relic items whose first_region matches)', 'Plan site rule: every site ends in a unique reward; items should mark source = that LOC_DGN_'),
 ('data/actors/bosses.csv', 'ACT_BOSS_QUIETCORE campaign role', 'Solo final campaign boss at level 80 in LOC_Q_CORE; raid version in LOC_END_RAID_01', 'Plan lists a final boss but no 41st boss; campaign thread to confirm'),
 ('data/world/npcs.csv', 'home_loc column', 'See npc_placement.csv', 'Companion recruit spots are defaults the campaign thread can move'),
 ('data/world/quests.csv', 'location column', 'QST_ rows should point at LOC_ ids here', 'For the campaign thread'),
 ('data/assets/asset_hooks.csv', 'environment kits KIT_*', ' '.join(sorted({v[0] for v in STEMPL.values()})), 'Site kits the asset thread should list (MESH_ sets)'),
 ('data/world/regions.csv', 'REG_02 to REG_06 bands vs Visual Bible', 'Kept data bands (10-22, 20-34, 32-46, 44-58, 55-70)', 'Visual Bible cards show older bands; data wins per data/README'),
]
wr('data-requests.csv', [dict(req_id=f'WREQ_{i:02d}', target=a, field=b, value=c, reason=d) for i, (a, b, c, d) in enumerate(REQ, 1)])

# ================================================================= SVG MAPS
PAL = {'REG_01': ('#3a2a22', '#c9773b'), 'REG_02': ('#203a40', '#a9cfc6'), 'REG_03': ('#2a1a18', '#a8562e'), 'REG_04': ('#1e1a2e', '#c7a8e0'),
       'REG_05': ('#1a2430', '#9ab8d0'), 'REG_06': ('#141418', '#c9c4cf')}
SYM = {'Anchor': ('tri', '#8fe3ee', 5), 'Settlement': ('sq', '#e8873a', 7), 'Site': ('circ', '#e7e2d6', 5), 'Choir vault': ('circ', '#b48cff', 5),
       'Citadel': ('dia', '#ffffff', 10), 'Relay Tower': ('bar', '#8fe3ee', 9), 'Landmark': ('star', '#d9c3a0', 6), 'Field boss': ('skull', '#ff3b30', 7),
       'Choir site': ('dia', '#b48cff', 6), 'POI': ('dot', '#9a968c', 2.5), 'Undervault entry': ('circ', '#3fb0b0', 7), 'Connection': ('sq', '#ffffff', 5)}
def sym(kind, x, y):
    s, c, r = SYM[kind]
    if s == 'tri': return f'<path d="M{x-r} {y+r*0.8}L{x} {y-r}L{x+r} {y+r*0.8}Z" fill="{c}"/>'
    if s == 'sq': return f'<rect x="{x-r/2}" y="{y-r/2}" width="{r}" height="{r}" fill="{c}"/>'
    if s == 'circ': return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{c}" stroke-width="2"/>'
    if s == 'dia': return f'<rect x="{x-r/2}" y="{y-r/2}" width="{r}" height="{r}" fill="none" stroke="{c}" stroke-width="2" transform="rotate(45 {x} {y})"/>'
    if s == 'bar': return f'<path d="M{x} {y+r}V{y-r}" stroke="{c}" stroke-width="3"/><circle cx="{x}" cy="{y-r}" r="3" fill="{c}"/>'
    if s == 'star': return f'<path d="M{x} {y-r}L{x+r*0.3} {y-r*0.3}L{x+r} {y}L{x+r*0.3} {y+r*0.3}L{x} {y+r}L{x-r*0.3} {y+r*0.3}L{x-r} {y}L{x-r*0.3} {y-r*0.3}Z" fill="{c}"/>'
    if s == 'skull': return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" fill-opacity=".85"/><path d="M{x-3} {y-1}h2M{x+1} {y-1}h2" stroke="#000" stroke-width="2"/>'
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>'

def svg(name, w, h, body, title):
    with open(os.path.join(SVG, name), 'w') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="IBM Plex Mono,monospace" role="img" aria-label="{title}">'
                f'<rect width="{w}" height="{h}" fill="#0c0d0f"/>{body}</svg>')

def mst(pts):
    if not pts: return []
    used = {0}; edges = []
    best = {i: (math.dist(pts[0], pts[i]), 0) for i in range(1, len(pts))}
    while best:
        i = min(best, key=lambda k: best[k][0]); d, j = best.pop(i); used.add(i); edges.append((pts[i], pts[j]))
        for k in best:
            dk = math.dist(pts[i], pts[k])
            if dk < best[k][0]: best[k] = (dk, i)
    return edges

def legend(x, y, kinds):
    out = [f'<rect x="{x-10}" y="{y-18}" width="230" height="{len(kinds)*18+16}" fill="#14120f" stroke="#2a2f37"/>']
    for i, k in enumerate(kinds):
        out.append(sym(k, x + 6, y + i * 18) + f'<text x="{x+22}" y="{y+i*18+4}" font-size="12" fill="#e7e2d6">{k}</text>')
    return ''.join(out)

# World overview, 1 px = 10 m
S = 0.1; WY = lambda y: (H - y) * S
b = [f'<g stroke="#1d2026">' + ''.join(f'<path d="M{i*CELL*4*S} 0V{H*S}"/>' for i in range(11)) + ''.join(f'<path d="M0 {WY(j*CELL*4)}H{W*S}"/>' for j in range(6)) + '</g>']
for reg, g in REG.items():
    if 'c' not in g: continue
    (cx, cy), (rx, ry) = g['c'], g['r']; f_, s_ = PAL[reg]
    b.append(f'<ellipse cx="{cx*S}" cy="{WY(cy)}" rx="{rx*S}" ry="{ry*S}" fill="{f_}" stroke="{s_}" stroke-width="2"/>')
    lo, hi = lvl_band(reg)
    b.append(f'<text x="{cx*S}" y="{WY(cy)-4}" text-anchor="middle" font-family="Spectral SC,Georgia,serif" font-size="20" fill="#e7e2d6">{regions[reg]["name"]}</text>'
             f'<text x="{cx*S}" y="{WY(cy)+14}" text-anchor="middle" font-size="12" fill="#9a968c">{reg} · levels {lo}-{hi} · {g["act"]}</text>')
for reg, (en, sec, lv) in UV.items():
    cx, cy = REG[reg]['c']; b.append(f'<ellipse cx="{cx*S}" cy="{WY(cy)}" rx="56" ry="45" fill="none" stroke="#3fb0b0" stroke-dasharray="4 4"/>')
b.append(f'<path d="M{REG["REG_05"]["c"][0]*S} {WY(REG["REG_05"]["c"][1])}L{REG["REG_02"]["c"][0]*S} {WY(REG["REG_02"]["c"][1])}L{REG["REG_03"]["c"][0]*S} {WY(REG["REG_03"]["c"][1])}" fill="none" stroke="#3fb0b0" stroke-dasharray="2 6" stroke-width="2"/>')
b.append(f'<ellipse cx="{HUB["c"][0]*S}" cy="{WY(HUB["c"][1])}" rx="30" ry="25" fill="#5a4632" stroke="#e0a04a" stroke-width="2"/>'
         f'<text x="{HUB["c"][0]*S}" y="{WY(HUB["c"][1])+42}" text-anchor="middle" font-family="Spectral SC,Georgia,serif" font-size="15" fill="#e0a04a">Lantern Hold</text>')
for c in CONNS:
    if c['to_reg'] in ('REG_U', 'REG_Q'): continue
    pa = HUB['c'] if c['from_reg'] == 'REG_HUB' else REG[c['from_reg']]['c']; pb = HUB['c'] if c['to_reg'] == 'REG_HUB' else REG[c['to_reg']]['c']
    dash = '' if 'Open' in c['gate'] or 'Road' in c['type'] else ' stroke-dasharray="8 5"'
    b.append(f'<line x1="{pa[0]*S}" y1="{WY(pa[1])}" x2="{pb[0]*S}" y2="{WY(pb[1])}" stroke="#e8873a" stroke-opacity=".55" stroke-width="2"{dash}/>')
    b.append(f'<text x="{c["x_m"]*S}" y="{WY(c["y_m"])-6}" text-anchor="middle" font-size="11" fill="#e8873a">{c["con_id"]}</text>')
for l in LOCS:
    if l['layer'] == 'Surface' and l['kind'] in ('Citadel', 'Relay Tower', 'Settlement', 'Field boss', 'Undervault entry'):
        b.append(sym(l['kind'], round(l['x_m'] * S, 1), round(WY(l['y_m']), 1)))
b.append(legend(20, 30, ['Citadel', 'Relay Tower', 'Settlement', 'Field boss', 'Undervault entry']))
b.append(f'<text x="{W*S-16}" y="{H*S-14}" text-anchor="end" font-size="12" fill="#9a968c">10 x 5.6 km · grid 1 km · dashed orange = gated · dashed teal = Undervault · Ascension Lift (CON_12) to the Quiet from the hub</text>')
svg('world_map.svg', W * S, H * S, ''.join(b), 'Shardfall world map')

# Region maps, 1 px = 3 m
for reg, g in REG.items():
    if 'c' not in g: continue
    (cx, cy), (rx, ry) = g['c'], g['r']; sc = 1 / 3; pad = 60
    ox, oy = cx - rx - pad / sc, cy + ry + pad / sc
    P = lambda x, y: (round((x - ox) * sc, 1), round((oy - y) * sc, 1))
    w, h = round(2 * rx * sc + 2 * pad) + 240, round(2 * ry * sc + 2 * pad)
    f_, s_ = PAL[reg]; e = P(cx, cy)
    b = [f'<ellipse cx="{e[0]}" cy="{e[1]}" rx="{rx*sc}" ry="{ry*sc}" fill="{f_}" stroke="{s_}" stroke-width="2"/>']
    for k in range(1, 4):
        b.append(f'<ellipse cx="{e[0]}" cy="{e[1]}" rx="{rx*sc*k/4}" ry="{ry*sc*k/4}" fill="none" stroke="{s_}" stroke-opacity=".08"/>')
    road = [(a['x_m'], a['y_m']) for a in ANCH if a['region'] == reg and a['layer'] == 'Surface' and a['anchor_type'] in ('Field', 'Town', 'Relay', 'Site entrance')]
    road.append((REG[reg]['c'][0], REG[reg]['c'][1])); road.append(next((l['x_m'], l['y_m']) for l in LOCS if l['loc_id'] == f'LOC_CIT_{reg}'))
    for p, q in mst(road):
        a1, a2 = P(*p), P(*q); b.append(f'<line x1="{a1[0]}" y1="{a1[1]}" x2="{a2[0]}" y2="{a2[1]}" stroke="#d9c3a0" stroke-opacity=".35" stroke-width="2"/>')
    for z in [z for z in ZONES if z['citadel'] == f'LOC_CIT_{reg}']:
        l = next(l for l in LOCS if l['loc_id'] == z['loc_id']); p = P(l['x_m'], l['y_m'])
        b.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="3" fill="#fff" fill-opacity=".5"/>')
    for l in LOCS:
        if l['region'] == reg and l['layer'] == 'Surface' and l['kind'] in SYM:
            p = P(l['x_m'], l['y_m']); b.append(sym(l['kind'], *p))
            if l['kind'] in ('Citadel', 'Settlement', 'Landmark', 'Field boss', 'Choir site', 'Relay Tower', 'Connection', 'Undervault entry') or (l['kind'] in ('Site', 'Choir vault')):
                fs = 13 if l['kind'] in ('Citadel', 'Settlement') else 10
                b.append(f'<text x="{p[0]+8}" y="{p[1]-6}" font-size="{fs}" fill="#e7e2d6" fill-opacity=".85">{l["name"]} <tspan fill="#9a968c">{l["level"]}</tspan></text>')
    en, ap = P(*edge_pt(reg, g['entry'])), P(*edge_pt(reg, g['apex']))
    b.append(f'<text x="{en[0]}" y="{en[1]+18}" text-anchor="middle" font-size="12" fill="#8fe3ee">ENTRY · L{lvl_band(reg)[0]}</text>'
             f'<text x="{ap[0]}" y="{ap[1]-14}" text-anchor="middle" font-size="12" fill="#ff3b30">APEX · L{lvl_band(reg)[1]}</text>')
    b.append(f'<text x="16" y="28" font-family="Spectral SC,Georgia,serif" font-size="24" fill="#e7e2d6">{regions[reg]["name"]}</text>'
             f'<text x="16" y="46" font-size="12" fill="#9a968c">{reg} · {math.pi*rx*ry/1e6:.1f} km² · 1 px = 3 m · roads join the Anchors</text>')
    b.append(legend(w - 220, 80, ['Connection', 'Undervault entry', 'Anchor', 'Settlement', 'Site', 'Choir vault', 'Citadel', 'Relay Tower', 'Landmark', 'Field boss', 'Choir site', 'POI']))
    svg(f'region_{reg}.svg', w, h, ''.join(b), f'{regions[reg]["name"]} layout')

# Citadel side-view flows: x = path order, y = height; solid = main path, dashed = shortcut
for reg in [r for r in REG if 'c' in REG[r]]:
    zs = [z for z in ZONES if z['citadel'] == f'LOC_CIT_{reg}']
    w, h = 1200, 460; b = [f'<text x="20" y="30" font-family="Spectral SC,Georgia,serif" font-size="22" fill="#e7e2d6">{REG[reg]["cit"][0]}: side-view flow</text>']
    pos = {z['order']: (80 + (z['order'] - 1) * 150, 380 - z['elevation_rel_m'] * 2.5 - (40 if z['order'] % 2 else 0)) for z in zs}
    for i in range(1, 8):
        (x1, y1), (x2, y2) = pos[i], pos[i + 1]; b.append(f'<line x1="{x1+50}" y1="{y1}" x2="{x2-50}" y2="{y2}" stroke="#e7e2d6" stroke-width="2"/>')
    back = {2: 1, 3: 2, 4: 3, 5: 3, 6: 5, 7: 4, 8: 1}
    for a_, b_ in back.items():
        (x1, y1), (x2, y2) = pos[a_], pos[b_]; mx = (x1 + x2) / 2; my = max(y1, y2) + 40 + 10 * (a_ - b_)
        b.append(f'<path d="M{x1} {y1+22}Q{mx} {my} {x2} {y2+22}" fill="none" stroke="#8fe3ee" stroke-dasharray="6 5" stroke-width="1.5"/>')
    for z in zs:
        x, y = pos[z['order']]; boss = z['boss']
        col = '#ff3b30' if boss else '#3a352d'
        b.append(f'<rect x="{x-50}" y="{y-20}" width="100" height="40" fill="#191714" stroke="{col}" stroke-width="2"/>'
                 f'<text x="{x}" y="{y-4}" text-anchor="middle" font-size="10" fill="#e7e2d6">Z{z["order"]} {z["name"][:18]}</text>'
                 f'<text x="{x}" y="{y+11}" text-anchor="middle" font-size="9" fill="#9a968c">L{z["level"]} · {z["path_min"]} min</text>')
        if z['anchor']: b.append(sym('Anchor', x + 44, y - 26))
        if boss: b.append(f'<text x="{x}" y="{y-28}" text-anchor="middle" font-size="10" fill="#ff3b30">{bosses[boss]["Boss"][:24]}</text>')
    b.append('<text x="20" y="445" font-size="11" fill="#9a968c">Solid: main path left to right, rising. Dashed cyan: shortcuts back to earlier Anchors. Triangles: Anchors. Red: boss arenas.</text>')
    svg(f'citadel_{reg}.svg', w, h, ''.join(b), f'{REG[reg]["cit"][0]} flow')

# Undervault, Quiet, Hub
b = []; S2 = 0.12
for reg, (en, sec, lv) in UV.items():
    cx, cy = REG[reg]['c']; b.append(f'<ellipse cx="{cx*S2}" cy="{(H-cy)*S2}" rx="{600*S2}" ry="{500*S2}" fill="#08100f" stroke="#3fb0b0"/>'
                                     f'<text x="{cx*S2}" y="{(H-cy)*S2-66}" text-anchor="middle" font-size="13" fill="#8fe3ee">{sec} · L{lv[0]}-{lv[1]} · under {regions[reg]["name"]}</text>')
for l in LOCS:
    if l['layer'] == 'Undervault':
        x, y = l['x_m'] * S2, (H - l['y_m']) * S2
        b.append(sym('Anchor', x, y) if l['kind'] == 'Anchor' else (f'<circle cx="{x}" cy="{y}" r="5" fill="#3fb0b0"/>' if l['kind'] in ('Undervault site', 'Undervault tunnel') else f'<circle cx="{x}" cy="{y}" r="1.5" fill="#173a38"/>'))
b.append(f'<path d="M{REG["REG_05"]["c"][0]*S2} {(H-REG["REG_05"]["c"][1])*S2}L{REG["REG_02"]["c"][0]*S2} {(H-REG["REG_02"]["c"][1])*S2}L{REG["REG_03"]["c"][0]*S2} {(H-REG["REG_03"]["c"][1])*S2}" fill="none" stroke="#3fb0b0" stroke-width="3" stroke-dasharray="10 6"/>'
         '<text x="16" y="28" font-family="Spectral SC,Georgia,serif" font-size="22" fill="#e7e2d6">The Undervault</text><text x="16" y="46" font-size="12" fill="#9a968c">Plan view over the surface frame; dashed line = Spine Tunnels (cargo tram)</text>')
svg('undervault.svg', W * S2, H * S2, ''.join(b), 'Undervault layout')
b = ['<text x="16" y="28" font-family="Spectral SC,Georgia,serif" font-size="22" fill="#e7e2d6">The Quiet (ring section, unrolled)</text>']
for lid, name, x0, x1, lv, note in QA:
    b.append(f'<rect x="{20+x0*0.29}" y="60" width="{(x1-x0)*0.29}" height="150" fill="#22252a" stroke="#e8e6e0"/><text x="{20+(x0+x1)/2*0.29}" y="80" text-anchor="middle" font-size="12" fill="#e8e6e0">{name} · L{lv[0]}-{lv[1]}</text>'
             f'<text x="{20+(x0+x1)/2*0.29}" y="228" text-anchor="middle" font-size="10" fill="#9a968c">{note[:70]}</text>')
for l in LOCS:
    if l['layer'] == 'Quiet' and l['kind'] in ('Quiet room', 'Anchor', 'Quiet sub-area') and l['loc_id'] not in [q[0] for q in QA]:
        x, y = 20 + l['x_m'] * 0.29, 60 + l['y_m'] * 0.3
        b.append(sym('Anchor', x, y) if l['kind'] == 'Anchor' else f'<circle cx="{x}" cy="{y}" r="{8 if "CORE" in l["loc_id"] else 4}" fill="{"#c8281e" if "CORE" in l["loc_id"] else "#e8e6e0"}"/>')
svg('quiet.svg', 1200, 250, ''.join(b), 'The Quiet layout')
b = ['<text x="16" y="28" font-family="Spectral SC,Georgia,serif" font-size="22" fill="#e7e2d6">Lantern Hold districts</text>']
for lid, kind, name, dx, dy, note in DIST[1:]:
    x, y = 300 + dx * 1.1, 290 - dy * 1.1
    b.append(f'<rect x="{x-70}" y="{y-18}" width="140" height="36" rx="3" fill="#1c1814" stroke="#e0a04a"/><text x="{x}" y="{y-2}" text-anchor="middle" font-size="11" fill="#e7e2d6">{name}</text>'
             f'<text x="{x}" y="{y+11}" text-anchor="middle" font-size="8" fill="#9a968c">{note[:30]}</text>')
svg('hub.svg', 640, 560, ''.join(b), 'Lantern Hold layout')
print('\n'.join(f'{a}: {b}' for a, b in CHECK))
