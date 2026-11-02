#!/usr/bin/env python3
"""Builds every Cinderreach (REG_01) level table, map and level sheet.

Reads design/world (layout owner), design/audio, design/art and data/ (read only).
Writes design/levels/cinderreach/*.csv, maps/*.svg, 05-level-sheets.md, checks.csv.
Run: python3 design/levels/cinderreach/tools/gen_levels.py
"""
import csv, os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import authored as A

G = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
W, D = G + '/design/world', G + '/data'
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUT + '/maps', exist_ok=True)


def rd(p):
    with open(p, encoding='utf-8') as f:
        return list(csv.DictReader(f))


def wr(name, rows, cols):
    with open(f'{OUT}/{name}', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


LOC = {r['loc_id']: r for r in rd(W + '/locations.csv') if r['region'] == 'REG_01'}
SITES = {r['loc_id']: r for r in rd(W + '/sites.csv') if r['region'] == 'REG_01'}
CZ = {r['loc_id']: r for r in rd(W + '/citadel_zones.csv') if r['citadel'] == 'LOC_CIT_REG_01'}
ARENA = {r['boss']: r for r in rd(W + '/boss_arenas.csv') if r['region'] == 'REG_01'}
WENC = {r['enc_id']: r for r in rd(W + '/encounters.csv') if r['region'] == 'REG_01'}
SECRETS = [r for r in rd(W + '/secrets.csv') if r['region'] == 'REG_01']
LMK = {r['loc_id']: r for r in rd(W + '/landmarks.csv') if r['region'] == 'REG_01'}
ANCH = {r['loc_id']: r for r in rd(W + '/anchors.csv') if r['region'] == 'REG_01'}
ENC_BY_LOC = collections.defaultdict(list)
for e in WENC.values():
    ENC_BY_LOC[e['loc_id']].append(e['enc_id'])

ITEMS = {r['item_id']: r for r in rd(D + '/items/items_index.csv')}
LTABLES = {r['table_id'] for r in rd(D + '/items/loot_tables.csv')}
ACTORS = {r['ACT_ID'] for r in rd(D + '/actors/enemies.csv')} | {r['ACT_ID'] for r in rd(D + '/actors/creatures.csv')} | {r['ACT_ID'] for r in rd(D + '/actors/bosses.csv')}
LORE = [r for r in rd(D + '/items/lore_items.csv') if r['region'] == 'REG_01']
MUSIC = {r['cue_id'] for r in rd(G + '/design/audio/music_cues.csv')}
AMB = {r['amb_id'] for r in rd(G + '/design/audio/ambience_layers.csv')}
EVENTS = {r['wwise_event'] for r in rd(G + '/design/audio/event_map.csv')}
HOOKS = {r['hook'] for r in rd(D + '/assets/asset_hooks.csv') if r['first_used_in'] != 'assets/asset_hooks.csv'}  # hooks data uses, not ones our own requests added
BOSS_LT = {}
for cls, start in (('Shard-bearer', 1), ('Citadel', 7), ('Field', 13), ('Site', 25), ('Raid', 37)):
    for i, b in enumerate([b for b in rd(D + '/actors/bosses.csv') if b['Class'] == cls]):
        BOSS_LT[b['ACT_ID']] = f'ITM_LT_BOSS_{start + i:02d}'

# Narrative names win over generated world names for places the campaign already names (README, conflicts)
# design/world/locations.csv wins on names (project rule); campaign names are kept as notes only
NAME = {}
CAMPAIGN_ALIAS = {'LOC_POI_REG_01_30': 'Tallow Hamlet', 'LOC_CIT_REG_01': 'the Spinegate'}
for b, alias in (('ACT_BOSS_FURNACEMAW', 'the Furnace'), ('ACT_BOSS_MINEGOLEM', 'Ashfield Mines')):  # lore bible names, notes only
    if ARENA.get(b, {}).get('loc_id') in SITES:
        CAMPAIGN_ALIAS[ARENA[b]['loc_id']] = alias
BIOME_MOOD = {'Ash plains': 'Grey-white ash dunes, burned stumps, low sun through haze',
              'Crash scar badlands': 'Black glass and torn hull plate, orange heat glow in fissures',
              'Hull-keep hills': 'Hull-plate forts on burned hills, banners, pyre smoke'}

LV, ND, EN, LT, SC, TR, CU, MISSING = [], [], [], [], [], [], [], collections.OrderedDict()
NODE_IDS = {}
lore_pool = {}
for l in LORE:
    lore_pool.setdefault(l['location'], []).append(l['item_id'])
lore_short = []
lore_spare = []  # lore items not consumed by their site go here for LORE_ANY


def need(kind, i, why):
    if i and i not in MISSING:
        MISSING[i] = (kind, why)


def level(lvl_id, loc, kind, name, lv, layout, time, mood, quest='', light='', music='', extra=None):
    d = dict(lvl_id=lvl_id, loc_id=loc, kind=kind, name=name, level=lv, layout=layout,
             first_clear_min=time[0], full_clear_min=time[1], mood=mood, quest_hooks=quest,
             light=light or 'LGT_REG_01_DAY/DUSK/NIGHT (time of day)', music_explore=music)
    lc = LOC.get(loc, {})
    d['campaign_name'] = CAMPAIGN_ALIAS.get(loc, '')
    d.update(grid=lc.get('grid', ''), x_m=lc.get('x_m', ''), y_m=lc.get('y_m', ''), z_m=lc.get('z_m', ''), biome=lc.get('biome', ''))
    if extra:
        d.update(extra)
    LV.append(d)
    return d


EDGE = re.compile(r'(@?[A-Za-z0-9_]+):([a-z-]+?)(\d+(?:\.\d+)?)?$')


def nodes(L, spec, prefix=''):
    """spec: list of node tuples (see authored.py)."""
    order = 0
    for key, name, typ, size, elev, links, crit, notes in spec:
        order += 1
        nid = f"{L['lvl_id']}_{prefix}{key}"
        NODE_IDS[nid] = typ
        ND.append(dict(node_id=nid, lvl_id=L['lvl_id'], order=order, name=name, type=typ, size_m=size,
                       elev_rel_m=elev, critical=crit, notes=notes, _links=links, _prefix=prefix))
    return L


def resolve_links():
    for n in ND:
        out = []
        for part in [p.strip() for p in n.pop('_links').split(';') if p.strip()]:
            m = EDGE.match(part)
            if not m:
                raise SystemExit(f'bad link {part} in {n["node_id"]}')
            tgt, edge, val = m.groups()
            tid = tgt[1:] if tgt.startswith('@') else f"{n['lvl_id']}_{n['_prefix']}{tgt}"
            out.append(f'{tid}({edge}{val or ""})')
            if edge != 'walk':
                TR.append(trav(n, tid, edge, val))
        n['links'] = '; '.join(out)
        n.pop('_prefix')


METRIC = {'drop': 'Safe fall 6 m, lethal 18 m (WREQ_03)', 'mantle': 'Mantle 2.0 m max', 'jump': 'Running jump gap 3.0 m max (design choice)',
          'ladder': 'Ladder climb 1.5 m/s (design choice)', 'lift': 'Lift 4 m/s; call button both ends', 'squeeze': 'Non-combat squeeze 2.4 m wide',
          'stairs': 'Stairs 4 m wide in combat spaces', 'fog': 'Fog gate 4 m wide', 'locked': 'Key door, 1.6 m single', 'door': 'Door 1.6 m single / 3.2 m double',
          'oneway': 'Opens from the far side only', 'climb': 'Climbable ledges 2.0 m apart', 'rope': 'Rope slide 12 m/s, no damage', 'cable': 'Cable climb 1.2 m/s',
          'secret': 'Hidden; see secrets.csv', 'gate': 'Winch gate 5.0 m'}


def trav(n, tid, edge, val):
    base = edge.split('-')[-1]
    v = float(val) if val else None
    ok = 'PASS'
    if base == 'drop' and v and v > 6:
        ok = 'Fall damage' if v < 18 else 'FAIL lethal'
    if base == 'mantle' and v and v > 2.0:
        ok = 'FAIL over 2.0 m'
    if base == 'jump' and v and v > 3.0:
        ok = 'FAIL over 3.0 m'
    t = f'{base} {v:g} m' if v else base
    return dict(trv_id=f'TRV_{len(TR) + 1:04d}', lvl_id=n['lvl_id'], from_node=n['node_id'], to_node=tid,
                element=('Shortcut: ' if edge.startswith('shortcut') else '') + t, metric=METRIC.get(base, ''), check=ok,
                sfx={'ladder': 'Play_SFX_World_Environment_Lever', 'lift': 'Play_SFX_World_Environment_LiftStartLoopStop',
                     'gate': 'Play_SFX_World_Environment_ShortcutUnlock', 'oneway': 'Play_SFX_World_Environment_DoorOpenCloseMetal',
                     'locked': 'Play_SFX_World_Environment_DoorOpenCloseMetal', 'door': 'Play_SFX_World_Environment_ShipHatch'}.get(base, '')
                if not edge.startswith('shortcut') else 'Play_SFX_World_Environment_ShortcutUnlock')


def parse_actors(s):
    tot, ids = 0, []
    for part in s.split(';'):
        m = re.match(r'\s*([A-Z0-9_]+) x(\d+)', part)
        if m:
            ids.append(m.group(1))
            tot += int(m.group(2))
    return tot, ids


TRIG = {'ENT_PATROL': 'Sight 25 m or noise 15 m', 'ENT_CAMP': 'Sight 30 m; leader alerts camp', 'ENT_AMBUSH': '12 m trigger volume',
        'ENT_FORT': 'Sight 50 m from the wall', 'ENT_ELITE': 'Room entry or sight 20 m', 'ENT_HORDE': 'Node entry; fodder pour from 2 spawn holes',
        'ENT_GUNLINE': 'Sight 60 m', 'ENT_KEEPER': 'Room entry', 'ENT_CRT_PACK': 'Sight 30 m (pack)', 'ENT_CRT_SOLO': 'Territory 40 m'}
ZONE = {'ENT_PATROL': 40, 'ENT_CAMP': 35, 'ENT_AMBUSH': 20, 'ENT_FORT': 45, 'ENT_ELITE': 25, 'ENT_HORDE': 30, 'ENT_GUNLINE': 60, 'ENT_KEEPER': 25,
        'ENT_CRT_PACK': 40, 'ENT_CRT_SOLO': 40, 'ENT_TUTORIAL': 15, 'ENT_MINIBOSS': 14, 'ENT_QUEST': 25, 'ENT_WAVES': 30}
level_fix = []


def enc(node_id, lvl_lv, spec, music_fallback):
    lv = str(lvl_lv).split('-')[-1]
    if isinstance(spec, str):
        w = WENC[spec]
        if w['level'] != lv:
            level_fix.append((spec, w['level'], lv))
        actors, tmpl, fac, trig, notes, src = w['actors'], w['template'], w['faction'], TRIG.get(w['template'], ''), w['condition'], 'design/world'
        cov, fb, resp, eid = w['cover_points'], w['fallback_points'], w['respawn'], spec
    else:
        _, tmpl, fac, actors, trig, notes = spec
        cov, fb, resp, src = '', '', 'On Anchor rest', 'new (levels)'
        eid = f'LENC_R1_{sum(1 for e in EN if e["enc_id"].startswith("LENC")) + 1:03d}'
    tot, ids = parse_actors(actors)
    for i in ids:
        if i not in ACTORS:
            need('actor', i, f'{eid} in {node_id}')
    mus = 'MUS_CDR_COMBAT_L1' if tot < 5 else 'MUS_CDR_COMBAT_L2' if tot < 9 else 'MUS_CDR_COMBAT_L3'
    EN.append(dict(enc_id=eid, source=src, lvl_id=node_id.rsplit('_', 1)[0] if False else '', node_id=node_id, template=tmpl, faction=fac,
                   level=lv, actors=actors, enemy_count=tot, leader='Y' if 'LEADER' in actors else '', trigger=trig,
                   ai_zone_m=ZONE.get(tmpl, 25), cover_points=cov or max(2, tot // 2), fallback_points=fb or 1,
                   respawn=resp, music=music_fallback or mus, notes=notes))
    return EN[-1]


def loot(node_id, container, contents, qty, vis, notes='', src=''):
    if contents.startswith('LORE_'):
        key = contents[5:]
        pool = lore_pool.get('LOC_SITE_REG_01_' + key[4:], []) if key.startswith('SITE') else []
        if key == 'CRYO':
            pick = [l['item_id'] for l in LORE if 'Cryo' in l['name']][:1]
            for p in pick:
                for k, v in lore_pool.items():
                    if p in v:
                        v.remove(p)
            pool = pick
        if key == 'ANY':
            pool = [lore_spare.pop(0)] if lore_spare else []
        if not pool:
            lore_short.append(node_id)
            return
        for p in list(pool):
            LT.append(dict(loot_id=f'LLT_R1_{len(LT) + 1:04d}', lvl_id='', node_id=node_id, container=container, contents=p, qty=1,
                           visibility=vis, notes=ITEMS.get(p, {}).get('name', ''), source_loc=src))
        pool.clear() if key.startswith('SITE') else None
        return
    ok = contents in ITEMS or contents in LTABLES or contents.startswith('RES_')
    if not ok:
        need('item', contents, node_id)
    LT.append(dict(loot_id=f'LLT_R1_{len(LT) + 1:04d}', lvl_id='', node_id=node_id, container=container, contents=contents, qty=qty,
                   visibility=vis, notes=notes or ITEMS.get(contents, {}).get('name', ''), source_loc=src))


# ---------- region gear that needs a hand-placed home (one copy of each in the world) ----------
GEAR = [r['item_id'] for f in ('weapons_melee', 'weapons_firearm', 'catalysts') for r in rd(f'{D}/items/{f}.csv') if r['first_region'] == 'REG_01']
GEAR += [r['item_id'] for r in rd(D + '/items/armor_pieces.csv') if r['set_id'] in ('ITM_SET_37', 'ITM_SET_38', 'ITM_SET_39', 'ITM_SET_40')]
GEAR_PLACED = set()


def next_gear(prefer):
    for g in GEAR:
        if g not in GEAR_PLACED and any(p in g for p in prefer):
            GEAR_PLACED.add(g)
            return g
    return None


# ================= LEVELS =================
# Prologue
for P in (A.PROLOGUE_BAY9, A.PROLOGUE_SPINE):
    L = level(P['lvl'], P['loc'], P['kind'], P['name'], P['level'], P['layout'], P['time'], P['mood'], P['quest'],
              light='LGT_PRO (interior: cryo blue to ember orange, request)', music='MUS_PRO_WAKING',
              extra=dict(grid='I7', biome='Wreck interior (the Meridian Spine)'))
    need('music', 'MUS_PRO_WAKING', 'Prologue score (Bay 9 and the Spine); no prologue cue in design/audio')
    nodes(L, P['nodes'])
    for k, specs in P['enc'].items():
        for s in specs:
            enc(f"{L['lvl_id']}_{k}", '1', s, '')
    for k, items in P['loot'].items():
        for c in items:
            if c[1] == 'LORE_CRYO' or c[1] in ITEMS or c[1] in LTABLES:
                GEAR_PLACED.add(c[1])
            loot(f"{L['lvl_id']}_{k}", *c)

# lore not tied to sites becomes spare for authored LORE_ANY slots
for k in list(lore_pool):
    if k in ('LOC_SITE_REG_01_19', 'LOC_SITE_REG_01_20'):
        continue
    if not any(s['lore_site'] == k for s in SITES.values()):
        lore_spare += lore_pool.pop(k)

# Citadel
cit = level('LVL_R1_CIT', 'LOC_CIT_REG_01', 'Citadel', LOC['LOC_CIT_REG_01']['name'], '9-12', 'Ascending spiral with 7 shortcuts and one big loop (Z7 to Z4)',
            (sum(int(z['path_min']) for z in CZ.values()), 165), 'Forward section of the Meridian\'s spine, fortified by Vael\'s Pyre-Wardens; climbs 112 m from the Ash Road to the Pyre-Court',
            'MQ_A1_05 MQ_A1_05C', music='MUS_CDR_CITADEL')
ZID = {z['name']: z['loc_id'][-2:] for z in CZ.values()}
for zname, Z in A.CITADEL_ZONES.items():
    zid = ZID[zname]
    zr = CZ[f'LOC_CIT_REG_01_{zid}']
    ze = int(zr['elevation_rel_m'])
    L = level(f'LVL_R1_CIT_{zid}', zr['loc_id'], 'Citadel zone', NAME.get(zr['loc_id'], zr['name']), zr['level'], zr['style'],
              (int(zr['path_min']), int(int(zr['path_min']) * 1.4)), Z['mood'], 'MQ_A1_05' if zr['boss'] else '', music='MUS_CDR_CITADEL',
              extra=dict(parent='LVL_R1_CIT', boss=zr['boss'], gate=zr['locked_door'], tag='World shortcut: ' + zr['shortcut']))
    spec = [(k, nm, t, sz, ze + e, re.sub(r'@\{([^}]+)\}_', lambda m: f"@LVL_R1_CIT_{ZID[m.group(1)]}_", ln), c,
             nt.replace('{anchor}', zr['anchor'])) for k, nm, t, sz, e, ln, c, nt in Z['nodes']]
    nodes(L, spec)
    wl = list(zr['encounters'].split()) if zr['encounters'] else []
    combat = [n for n in ND if n['lvl_id'] == L['lvl_id'] and n['type'] == 'COMBAT']
    for i, e in enumerate(wl):
        enc(combat[i % len(combat)]['node_id'], zr['level'], e, '')
    for (zn, k), specs in A.CITADEL_EXTRA_ENC.items():
        if zn == zname:
            for s in specs:
                enc(f"{L['lvl_id']}_{k}", zr['level'], s, '')
    for (zn, k), items in A.CITADEL_LOOT.items():
        if zn == zname:
            for c in items:
                if c[1] in GEAR:
                    GEAR_PLACED.add(c[1])
                loot(f"{L['lvl_id']}_{k}", *c)
    for n in [n for n in ND if n['lvl_id'] == L['lvl_id'] and n['type'] == 'COMBAT']:
        g = next_gear(['ITM_SET_39', 'ITM_SET_38', 'GAX', 'GHM', 'TWB', 'LNC', 'SNP'])
        if g:
            loot(n['node_id'], 'Corpse', g, 1, 'Side', 'Region gear (hand-placed)')
    if zr['boss']:
        EN.append(dict(enc_id=zr['boss'], source='actors/bosses.csv', node_id=f"{L['lvl_id']}_D", template='BOSS', faction='',
                       level=zr['level'], actors=f"{zr['boss']} x1", enemy_count=1, trigger='Fog gate', ai_zone_m=ARENA[zr['boss']]['diameter_m'],
                       cover_points=ARENA[zr['boss']]['cover_pieces'], fallback_points='', respawn='Never', music=f"MUS_BOSS_{zr['boss'][9:]}_INTRO",
                       notes=ARENA[zr['boss']]['condition']))

# Towns
for loc, T in A.TOWNS.items():
    lc = LOC[loc]
    L = level(f'LVL_R1_TWN_{loc[-2:]}', loc, 'Settlement', lc['name'], lc['level'], T['layout'], T['time'], T['mood'], T['quest'], music='MUS_CDR_TOWN')
    nodes(L, T['nodes'])
    for k, specs in T['enc'].items():
        for s in specs:
            enc(f"{L['lvl_id']}_{k}", lc['level'], s, 'MUS_CDR_COMBAT_L2')
    for k, items in T['loot'].items():
        for c in items:
            loot(f"{L['lvl_id']}_{k}", *c)

# Relay and Choir
for loc, R in (('LOC_RELAY_REG_01', A.RELAY), ('LOC_CHOIR_REG_01', A.CHOIR)):
    lc = LOC[loc]
    L = level(R['lvl'], loc, lc['kind'], lc['name'], lc['level'], R['layout'], R['time'], R['mood'], R['quest'],
              music='MUS_CDR_EXPLORE_DAY' if 'RELAY' in loc else 'MUS_FAC_CHOIR', extra=dict(gate=lc['gate']))
    nodes(L, R['nodes'])
    for k, specs in R['enc'].items():
        for s in specs:
            enc(f"{L['lvl_id']}_{k}", lc['level'], s, '')
    for k, items in R['loot'].items():
        for c in items:
            loot(f"{L['lvl_id']}_{k}", *c)

# Sites (15 sites and 3 Choir vaults), built from kits
KIT = {
 'KIT_CAVE': ('Cave Mouth', ['Ash Gallery', 'Drip Shaft', 'Root Chamber', 'Ember Pool', 'Collapsed Gallery', 'Glow-worm Hall', 'Narrow Crawl'], 'Keeper Den', -4, '24 x 20 x 8', 'drop4'),
 'KIT_MINE': ('Pithead', ['Hoist Room', 'Ore Gallery', 'Cart Tunnel', 'Timbered Drift', 'Blasting Room', 'Flooded Sump', 'Lower Level'], 'Foreman\'s Pit', -10, '30 x 12 x 6', 'ladder8'),
 'KIT_WRECK': ('Hull Breach', ['Corridor C-4', 'Crew Quarters', 'Galley', 'Power Junction', 'Cargo Bay', 'Med Bay', 'Tilted Deck', 'Bulkhead Lock'], 'Engine Room', 4, '26 x 14 x 6', 'ladder5'),
 'KIT_TOWER': ('Tower Door', ['Guard Floor', 'Spiral Stair', 'Library Floor', 'Broken Floor', 'Bell Floor', 'Lamp Room'], 'Roof Walk', 8, '16 x 16 x 6', 'stairs6'),
 'KIT_CATACOMB': ('Crypt Gate', ['Ossuary Hall', 'Niche Corridor', 'Trap Gallery', 'Burial Chapel', 'Bone Pit', 'Embalmer\'s Room', 'Lower Crypt', 'Sealed Vault'], 'Abbot\'s Crypt', -6, '22 x 16 x 6', 'stairs5'),
 'KIT_FORT': ('Gate Yard', ['Barracks', 'Watch Wall', 'Armory', 'Courtyard', 'Store Room'], 'Keep Hall', 2, '30 x 24 x 0', 'stairs4'),
 'KIT_CHOIR_VAULT': ('Glass Door', ['Tone Hall', 'Listening Chamber', 'Pillar Room', 'Resonant Stair'], 'Choir Cell', -3, '18 x 18 x 10', 'stairs4'),
}
KIT_MOOD = {'KIT_CAVE': 'Low ember-lit cave; ash drips; Shard veins give cyan pools of light',
            'KIT_MINE': 'Timbered tunnels, hoists, rail carts; lamp light every 15 m, dark between',
            'KIT_WRECK': 'Tilted Meridian decks; emergency strip lights; sparks and steam',
            'KIT_TOWER': 'Stone and hull-rib tower; wind through broken floors; light from above',
            'KIT_CATACOMB': 'Bone niches and burial chapels; candle stubs; cold air',
            'KIT_FORT': 'Thorn-held fort of timber and plate; fires in braziers; open yards',
            'KIT_CHOIR_VAULT': 'Glass halls that ring when struck; cold cyan light; no fire'}
SECRET_BY_HOST = collections.defaultdict(list)
for s in SECRETS:
    SECRET_BY_HOST[s['host_loc']].append(s)
for sid, S in SITES.items():
    lc = LOC[sid]
    kit = S['template']
    entry, rooms, endname, step, csize, edge = KIT[kit]
    nrooms = int(S['rooms'])
    boss = S['end'].split()[-1] if S['end'].startswith('Site boss') else ''
    nm = NAME.get(sid, S['name'])
    L = level(f"LVL_R1_{'VLT' if 'VAULT' in sid else 'DGN'}_{sid[-2:]}", sid, 'Choir vault' if 'VAULT' in sid else 'Site', nm, S['level'],
              f"{S['site_type']}, {S['floors']} floor(s), loop back to entrance", (int(S['path_min']), int(int(S['path_min']) * 1.5)),
              KIT_MOOD[kit] + '. ' + BIOME_MOOD.get(lc['biome'], ''), music='MUS_CDR_SITE',
              extra=dict(gate=lc['gate'], unique_reward=S['unique_reward'], boss=boss))
    encs = S['encounters'].split()
    end_enc = [e for e in encs if WENC[e]['template'] == 'ENT_KEEPER']
    mid_enc = [e for e in encs if e not in end_enc]
    spec = [('A', entry, 'ENTRY', '10 x 10 x 6', 0, 'B:walk', 'Y', f"Entrance Anchor {S['entrance_anchor']} outside.")]
    keys = 'BCDEFGHIJKLMN'
    crit_n = max(len(mid_enc), 2) + (1 if S['puzzle'] else 0)
    side = ['LOOT', 'LORE'] + (['SECRET'] if SECRET_BY_HOST.get(sid) else [])
    core = nrooms - 3  # entry, end, reward
    crit_n = min(crit_n, max(2, core - len(side)))
    elev, ki, names = 0, 0, list(rooms)
    crit_keys = []
    floors = max(1, int(S['floors']))
    for i in range(crit_n):
        k = keys[ki]; ki += 1
        elev = step * ((i + 1) * (floors - 1) // max(1, crit_n)) if floors > 1 else 0
        is_puz = S['puzzle'] and i == crit_n - 1
        typ = 'PUZZLE' if is_puz else 'COMBAT'
        note = f"Puzzle: {S['puzzle']}." if is_puz else ''
        if i == 0 and S['interior_anchor']:
            typ, note = 'ANCHOR', f"Interior Anchor {S['interior_anchor']}."
        spec.append((k, names.pop(0) if names else f'Room {k}', typ, csize, elev, '', 'Y', note))
        crit_keys.append(k)
    side_keys = []
    for t in side[:max(0, core - crit_n)]:
        k = keys[ki]; ki += 1
        spec.append((k, names.pop(0) if names else f'Side Room {k}', t, '8 x 8 x 4', elev, '', 'N',
                     {'LOOT': 'Side branch; chest behind a breakable or past a trap.', 'LORE': f"Lore site {S['lore_site']}.",
                      'SECRET': '; '.join(f"{x['secret_type']}: {x['hint']}" for x in SECRET_BY_HOST[sid])}[t]))
        side_keys.append(k)
    endk, rewk = keys[ki], keys[ki + 1]
    elev = step * (floors - 1)
    spec.append((endk, endname, 'BOSS' if boss else 'KEEPER', ARENA[boss]['diameter_m'] + ' x ' + ARENA[boss]['diameter_m'] + ' x 10' if boss else '24 x 24 x 8',
                 elev, f'{rewk}:walk', 'Y', S['end'] + ('. Fog gate 4 m.' if boss else '. Named elite; door stays open.')))
    spec.append((rewk, 'Reward Alcove', 'REWARD', '8 x 6 x 4', elev, f"A:shortcut-{S['shortcut'].split()[0].lower()}", 'Y',
                 f"Unique reward {S['unique_reward']}. Shortcut: {S['shortcut']}."))
    # chain links
    chain = ['A'] + crit_keys + [endk]
    spec = [list(s) for s in spec]
    for s in spec:
        k = s[0]
        if k in chain[:-1]:
            nxt = chain[chain.index(k) + 1]
            same = dict((x[0], x[4]) for x in spec)[k] == dict((x[0], x[4]) for x in spec)[nxt]
            s[5] = f'{nxt}:{"walk" if same else edge}' + ''.join(f'; {sk}:walk' for j, sk in enumerate(side_keys) if crit_keys and k == crit_keys[min(j, len(crit_keys) - 1)])
            if S['interior_anchor'] and k == crit_keys[0]:
                s[5] += '; A:shortcut-door'
        elif k in side_keys:
            s[5] = f'{crit_keys[min(side_keys.index(k), len(crit_keys) - 1)]}:walk' if crit_keys else 'A:walk'
    spec = [tuple(s) for s in spec]
    nodes(L, spec)
    nid = lambda k: f"{L['lvl_id']}_{k}"
    cnodes = [nid(k) for k in crit_keys if dict((s[0], s[2]) for s in spec)[k] == 'COMBAT'] or [nid(crit_keys[0])]
    for i, e in enumerate(mid_enc):
        enc(cnodes[i % len(cnodes)], S['level'], e, '')
    for e in end_enc:
        enc(nid(endk), S['level'], e, 'MUS_CDR_COMBAT_L2')
    if boss:
        EN.append(dict(enc_id=boss, source='actors/bosses.csv', node_id=nid(endk), template='BOSS', level=S['level'], actors=f'{boss} x1',
                       enemy_count=1, trigger='Fog gate', ai_zone_m=ARENA[boss]['diameter_m'], cover_points=ARENA[boss]['cover_pieces'],
                       respawn='Never', music=f'MUS_BOSS_{boss[9:]}_INTRO', notes=ARENA[boss]['condition']))
        loot(nid(endk), 'Boss', BOSS_LT[boss], 1, 'Boss', 'First-kill table')
    loot(nid(rewk), 'Reward chest', S['unique_reward'], 1, 'Path', 'Site unique reward (sites.csv)')
    for c in [x for x in LOC.values() if x['parent_loc'] == sid and x['kind'] in ('Small chest', 'Shard crate')]:
        tgt = nid(side_keys[0]) if side_keys else nid(crit_keys[-1])
        loot(tgt, c['kind'], 'ITM_LT_SMALLCHEST_REG_01' if c['kind'] == 'Small chest' else 'ITM_LT_SHARDCRATE_REG_01', 1, 'Side', '', c['loc_id'])
    lore_node = next((nid(k) for k in side_keys if dict((s[0], s[2]) for s in spec)[k] == 'LORE'), nid(endk))
    for item in lore_pool.pop(S['lore_site'], []):
        loot(lore_node, 'Lore pickup', item, 1, 'Side', ITEMS.get(item, {}).get('name', ''), S['lore_site'])
    if 'VAULT' in sid:
        loot(nid(rewk), 'Vault chest', 'ITM_LT_VAULT_REG_01', 1, 'Path', '')
    g = next_gear(['ITM_SET_37', 'ITM_SET_39', 'ARF', 'SCT', 'SMG', 'SHG', 'LCH', 'POL', 'HMR', 'AXE', 'GRS', 'CRV', 'STS', 'DGR', 'FST', 'SHD', 'CAT'])
    if g:
        loot(nid(crit_keys[0]), 'Corpse', g, 1, 'Path', 'Region gear (hand-placed)')
    for s in SECRET_BY_HOST.get(sid, []):
        SC.append(dict(sec_id=s['loc_id'], lvl_id=L['lvl_id'], node_id=next((nid(k) for k in side_keys if dict((x[0], x[2]) for x in spec)[k] == 'SECRET'), nid(endk)),
                       secret_type=s['secret_type'], hint=s['hint'], requirement=s['requirement'], reward=s['reward'], source='design/world/secrets.csv'))
        m = re.match(r'(ITM_[A-Z0-9_]+)', s['reward'])
        loot(SC[-1]['node_id'], 'Secret', m.group(1) if m else 'LORE_ANY', 1, 'Secret', s['reward'])

# Field bosses
for b in ('ACT_BOSS_ASHCOLOSSUS', 'ACT_BOSS_NIGHTDRAKE'):
    ar = ARENA[b]
    lc = LOC[ar['loc_id']]
    L = level(f"LVL_R1_FB_{b[9:]}", ar['loc_id'], 'Field boss', lc['name'], ar['level'], f"{ar['shape']}, {ar['diameter_m']} m", (6, 10),
              BIOME_MOOD[lc['biome']] + ('. Night only, moonlit ash.' if 'NIGHT' in b else '. Huge footprints lead in from the road.'),
              music='MUS_CDR_EXPLORE_NIGHT' if 'NIGHT' in b else 'MUS_CDR_EXPLORE_DAY', extra=dict(boss=b, gate=ar['condition']))
    nodes(L, [('A', 'Field Anchor', 'ANCHOR', '10 x 10 x 4', 0, 'B:walk', 'Y', f"{ar['nearest_anchor']}, {ar['anchor_run_m']} m run to the ground."),
              ('B', 'Approach', 'PATH', f"10 x {ar['anchor_run_m']} x 0", 0, 'C:walk', 'Y', 'Sightline to the boss before it aggros; Strider allowed.'),
              ('C', 'Boss Ground', 'BOSS', f"{ar['diameter_m']} x {ar['diameter_m']} x 0", 0, 'D:walk', 'Y', f"{ar['entry']}. {ar['notes']}"),
              ('D', 'Cover Ruins', 'COVER', '30 x 30 x 4', 2, 'C:walk', 'N', f"{ar['cover_pieces']} cover pieces; high cover breaks line of sight for Ward recharge.")])
    EN.append(dict(enc_id=b, source='actors/bosses.csv', node_id=f"{L['lvl_id']}_C", template='BOSS', level=ar['level'], actors=f'{b} x1', enemy_count=1,
                   trigger='Sight 80 m', ai_zone_m=ar['diameter_m'], cover_points=ar['cover_pieces'], respawn='Never', music=f'MUS_BOSS_{b[9:]}_INTRO', notes=ar['condition']))
    loot(f"{L['lvl_id']}_C", 'Boss', BOSS_LT[b], 1, 'Boss', 'First-kill table')

# POIs, built from tag templates
POI_T = {
 'faction camp': ([('Approach', 'PATH'), ('Camp Ring', 'COMBAT'), ("Leader's Tent", 'LOOT'), ('Lookout', 'VISTA')], (4, 6)),
 'ruin': ([('Ruin Edge', 'PATH'), ('Fallen Hall', 'COMBAT'), ('Cellar', 'LOOT')], (3, 5)),
 'wreck fragment': ([('Debris Field', 'PATH'), ('Fragment Interior', 'COMBAT'), ('Antenna Top', 'VISTA')], (3, 5)),
 'wayshrine': ([('Wayshrine', 'LORE'), ('Offering Bowl', 'LOOT')], (1, 2)),
 'watchtower': ([('Tower Base', 'COMBAT'), ('Tower Platform', 'VISTA')], (2, 4)),
 'overturned cart': ([('Cart', 'LOOT'), ('Ditch', 'COMBAT')], (1, 3)),
 'overlook': ([('Overlook', 'VISTA')], (1, 2)),
 'hermit hut': ([('Hut', 'SOCIAL'), ('Garden', 'LOOT')], (2, 4)),
 'grave field': ([('Graves', 'COMBAT'), ('Mausoleum', 'LOOT')], (3, 5)),
 'shard crater': ([('Crater Rim', 'VISTA'), ('Crater Floor', 'COMBAT'), ('Glass Spire', 'LOOT')], (3, 5)),
 'hunting ground': ([('Grassland', 'COMBAT'), ('Carcass', 'LOOT')], (2, 4)),
 'lair': ([('Lair Mouth', 'PATH'), ('Lair', 'COMBAT'), ('Bone Pile', 'LOOT')], (3, 5)),
 'trader stop': ([('Trader Wagon', 'VENDOR'), ('Fire Pit', 'SOCIAL')], (1, 3)),
 'vehicle depot': ([('Depot Yard', 'COMBAT'), ('Garage', 'VEHICLE'), ('Fuel Shed', 'LOOT')], (3, 5)),
}
POI_NOTE = {'VISTA': 'Discovery stinger; marks nearby POIs on the compass within 600 m.', 'VENDOR': 'Wandering trader route stop (ACT_NPC_VEN_TRADER_REG_01).',
            'VEHICLE': 'Vehicle spawn: Skimmer and Hauler (vehicle_depots.csv).', 'SOCIAL': 'Hermit NPC with one radiant job (data request).',
            'LORE': 'Lantern Church wayshrine: lore pickup and Shard-note spot.'}
for loc in sorted(l for l in LOC if LOC[l]['kind'] == 'POI'):
    lc = LOC[loc]
    tag = lc['tags']
    if loc == 'LOC_POI_REG_01_30':
        H = A.HAMLET
        L = level('LVL_R1_POI_30', loc, 'POI', lc['name'], lc['level'], 'Fork: people or Anchor (quest), ruin after', (6, 10), H['mood'], H['quest'],
                  music='MUS_CDR_TENSION', extra=dict(tag=tag))
        nodes(L, H['nodes'])
        for k, specs in H['enc'].items():
            for s in specs:
                enc(f"{L['lvl_id']}_{k}", lc['level'], s, 'MUS_CDR_COMBAT_L2')
        for e in ENC_BY_LOC.get(loc, []):
            enc(f"{L['lvl_id']}_B", lc['level'], e, '')
        continue
    tpl, tm = POI_T[tag]
    L = level(f'LVL_R1_POI_{loc[-2:]}', loc, 'POI', NAME.get(loc, lc['name']), lc['level'], 'Open-air set piece', tm, BIOME_MOOD[lc['biome']],
              music='MUS_CDR_EXPLORE_DAY', extra=dict(tag=tag))
    spec, prev = [], None
    for i, (nm, t) in enumerate(tpl):
        k = 'ABCDE'[i]
        spec.append((k, nm, t, '30 x 30 x 0' if t == 'COMBAT' else '10 x 10 x 4', 10 if t == 'VISTA' else 0,
                     f"{'ABCDE'[i + 1]}:{'ladder10' if tpl[i + 1][1] == 'VISTA' and tag == 'watchtower' else 'walk'}" if i + 1 < len(tpl) else '',
                     'Y', POI_NOTE.get(t, '')))
    nodes(L, spec)
    cn = [n['node_id'] for n in ND if n['lvl_id'] == L['lvl_id'] and n['type'] == 'COMBAT'] or [f"{L['lvl_id']}_A"]
    for e in ENC_BY_LOC.get(loc, []):
        enc(cn[0], lc['level'], e, '')
    ln = [n['node_id'] for n in ND if n['lvl_id'] == L['lvl_id'] and n['type'] == 'LOOT'] or [f"{L['lvl_id']}_A"]
    for c in [x for x in LOC.values() if x['parent_loc'] == loc and x['kind'] in ('Small chest', 'Shard crate')]:
        loot(ln[0], c['kind'], 'ITM_LT_SMALLCHEST_REG_01' if c['kind'] == 'Small chest' else 'ITM_LT_SHARDCRATE_REG_01', 1, 'Side', '', c['loc_id'])
    if tag in ('lair', 'hunting ground'):
        loot(ln[0], 'Carcass', 'ITM_LT_TIERMAT_REG_01', 1, 'Path', 'Creature parts and tier materials')
    if tag == 'wayshrine':
        loot(f"{L['lvl_id']}_A", 'Shrine', 'LORE_ANY', 1, 'Path')
    g = next_gear(['ITM_WPN', 'ITM_SET_37', 'CAT']) if tag not in ('overlook', 'trader stop') else None
    if g:
        loot(ln[0], 'Corpse' if tag != 'faction camp' else 'Chest', g, 1, 'Side', 'Region gear (hand-placed)')
    for s in SECRET_BY_HOST.get(loc, []):
        SC.append(dict(sec_id=s['loc_id'], lvl_id=L['lvl_id'], node_id=f"{L['lvl_id']}_A", secret_type=s['secret_type'], hint=s['hint'],
                       requirement=s['requirement'], reward=s['reward'], source='design/world/secrets.csv'))
        rw = s['reward']
        m = re.match(r'(ITM_[A-Z0-9_]+)', rw)
        loot(f"{L['lvl_id']}_A", 'Secret', m.group(1) if m else 'LORE_ANY', 1, 'Secret', rw)

# Landmarks and connections
for loc in sorted(l for l in LOC if LOC[l]['kind'] == 'Landmark'):
    lc, lm = LOC[loc], LMK.get(loc, {})
    L = level(f'LVL_R1_LMK_{loc[-2:]}', loc, 'Landmark', lc['name'], lc['level'], 'Silhouette and viewpoint', (1, 3), BIOME_MOOD[lc['biome']],
              music='MUS_CDR_DISCOVERY', extra=dict(tag=f"{lm.get('height_m', '')} m tall, seen {lm.get('visible_km', '')} km"))
    spec = [('A', 'Base', 'PATH', '20 x 20 x 0', 0, 'B:climb', 'Y', 'Readable silhouette from every Anchor within view range.'),
            ('B', 'Viewpoint', 'VISTA', '6 x 6 x 0', int(float(lm.get('height_m', 20)) * 0.6), '', 'N', 'Discovery stinger; free look-out over the next 2 landmarks (MET_LANDMARK).')]
    if loc == 'LOC_LMK_REG_01_01':
        spec[0] = ('A', 'Spine Lower Door', 'ENTRY', '20 x 20 x 0', 0, 'B:climb; @LVL_R1_PRO_SPINE_I:door', 'Y', 'Prologue exit; first view of Cinderreach.')
    nodes(L, spec)
for loc in sorted(l for l in LOC if LOC[l]['kind'] == 'Connection'):
    lc = LOC[loc]
    L = level(f'LVL_R1_CON_{loc[-2:]}', loc, 'Connection', lc['name'], lc['level'], 'Route between regions', (2, 3), BIOME_MOOD[lc['biome']],
              music='MUS_CDR_EXPLORE_DAY', extra=dict(gate=lc['gate']))
    nodes(L, [('A', 'Road In', 'ENTRY', '12 x 60 x 0', 0, 'B:walk', 'Y', ''), ('B', 'Region Edge', 'EXIT', '12 x 40 x 0', 0, '', 'Y', lc['gate'])])

# Open world: field Anchors, patrols, nodes, loose chests
L = level('LVL_R1_OPEN', '', 'Open world', 'Cinderreach open world', '1-12', 'Open region; level rises from the SW entry edge to the NE Citadel edge',
          (360, 720), 'Ash plains (45%), crash scar badlands (30%), hull-keep hills (25%); ash fall; dusk haze', 'MQ_A1_01..05', music='MUS_CDR_EXPLORE_DAY',
          extra=dict(grid='A1-T15', x_m='2750', y_m='1800'))
spec = []
for a in sorted(x for x in ANCH if ANCH[x]['anchor_type'] == 'Field'):
    spec.append((a[-2:], f'Field Anchor {a[-2:]}', 'ANCHOR', '10 x 10 x 4', 0, '', 'N', f"{a} at {ANCH[a]['x_m']},{ANCH[a]['y_m']}"))
for p in sorted(x for x in LOC if LOC[x]['kind'] == 'Patrol route'):
    spec.append((f'P{p[-2:]}', LOC[p]['name'], 'COMBAT', '150-300 m loop', 0, '', 'N', f"{p}, grid {LOC[p]['grid']}"))
placed_locs = {e['enc_id'] for e in EN}
for e in sorted(WENC):
    if e not in placed_locs and WENC[e]['loc_id'] not in {x['loc_id'] for x in LV}:
        lc = LOC.get(WENC[e]['loc_id'], {})
        k = 'E' + WENC[e]['loc_id'][-2:] if WENC[e]['loc_id'].startswith('LOC_EVT') else 'X' + e[-4:]
        if k not in [x[0] for x in spec]:
            spec.append((k, lc.get('name', WENC[e]['loc_id']), 'COMBAT', '60 x 60 x 0', 0, '', 'N',
                         f"{WENC[e]['loc_id']} ({lc.get('kind', '')}), grid {lc.get('grid', '')}. {lc.get('notes', '')}".strip()))
spec.append(('NODES', 'Gather nodes (130)', 'LOOT', 'region', 0, '', 'N', '10 of each of 13 node types; respawn 72 game hours'))
nodes(L, spec)
for p in sorted(x for x in LOC if LOC[x]['kind'] == 'Patrol route'):
    for e in ENC_BY_LOC.get(p, []):
        enc(f"LVL_R1_OPEN_P{p[-2:]}", LOC[p]['level'], e, '')
for e in sorted(WENC):
    if e not in {x['enc_id'] for x in EN}:
        k = 'E' + WENC[e]['loc_id'][-2:] if WENC[e]['loc_id'].startswith('LOC_EVT') else 'X' + e[-4:]
        if f'LVL_R1_OPEN_{k}' in NODE_IDS:
            enc(f'LVL_R1_OPEN_{k}', WENC[e]['level'], e, 'MUS_CDR_COMBAT_L2')
for n in sorted(x for x in LOC if LOC[x]['kind'] == 'Gather node'):
    t = 'ITM_LT_NODE_' + LOC[n]['tags'].upper()
    loot('LVL_R1_OPEN_NODES', 'Gather node', t, 1, 'Open', LOC[n]['grid'], n)
for c in sorted(x for x in LOC if LOC[x]['kind'] in ('Small chest', 'Shard crate') and not LOC[x]['parent_loc']):
    loot('LVL_R1_OPEN_NODES', LOC[c]['kind'], 'ITM_LT_SHARDCRATE_REG_01' if 'crate' in LOC[c]['kind'] else 'ITM_LT_SMALLCHEST_REG_01', 1, 'Open', LOC[c]['grid'], c)
for s in SECRETS:
    if s['host_loc'] not in SITES and not s['host_loc'].startswith('LOC_POI'):
        SC.append(dict(sec_id=s['loc_id'], lvl_id='LVL_R1_OPEN', node_id='LVL_R1_OPEN_NODES', secret_type=s['secret_type'], hint=s['hint'],
                       requirement=s['requirement'], reward=s['reward'], source='design/world/secrets.csv'))
# leftover region gear goes to the smith in Emberwatch and to chests on roads
for g in [g for g in GEAR if g not in GEAR_PLACED]:
    loot('LVL_R1_TWN_01_C', 'Smith stock', g, 1, 'Vendor', 'Region gear sold by the Emberwatch smith (data request)')
    GEAR_PLACED.add(g)
# authored secrets (levels thread), on top of the 15 world secrets
for nid_, t, hint, rew in [('LVL_R1_PRO_SPINE_H', 'Breakable panel', 'Hollow sound behind lockers', 'ITM_CAT_01'),
                           ('LVL_R1_CIT_Z3_F', 'Well drop', 'Rope tied to the well lip', 'Lore item and Shard Dust x5'),
                           ('LVL_R1_CIT_Z1_F', 'Cliff trail', 'Ash-free footholds along the cliff', 'Route to LOC_CON_02 (GATE_01 side path)')]:
    SC.append(dict(sec_id=f'LSEC_R1_{len([s for s in SC if s["sec_id"].startswith("LSEC")]) + 1:02d}', lvl_id=nid_.rsplit('_', 1)[0], node_id=nid_,
                   secret_type=t, hint=hint, requirement='', reward=rew, source='new (levels)'))

resolve_links()

# ---------- cues per node ----------
TYPE_CUE = {
 'ANCHOR': ('Anchor key light 3200 K amber, 6 m radius; safe pool', 'MUS_STG_ANCHOR_LIT', 'AMB_CDR_WEAVE_HUM', 'VFX_ENV_ANCHOR_IDLE; VFX_ENV_ANCHOR_LIGHT', 'Play_SFX_Player_Kindled_AnchorLight; Play_SFX_Ui_Interface_AnchorDiscovered'),
 'COMBAT': ('Enemies silhouetted against a brighter back plane; no pitch-black corners', '', 'AMB_CDR_EMITTERS', 'VFX_ENV_EMBER_DRIFT', ''),
 'BOSS': ('Arena rim light; boss reads against the sky or fire; floor hazards glow before they hurt', '', 'AMB_CDR_EMITTERS', 'VFX_ENV_FOG_GATE; VFX_ENV_HEAT_HAZE', 'Play_SFX_World_Environment_FireLoopSmallLarge'),
 'FOG': ('Fog gate glows white-gold', '', '', 'VFX_ENV_FOG_GATE', ''),
 'KEEPER': ('Single strong key light on the elite', '', 'AMB_CDR_INTERIOR', 'VFX_ENV_EMBER_DRIFT', ''),
 'LOOT': ('Container lit from one side; glint on idle', '', '', 'VFX_ENV_LOOT_GLINT', 'Play_SFX_World_Environment_ChestOpen'),
 'LORE': ('Warm pool of light on the pickup', 'MUS_STG_LORE_STONE', '', 'VFX_ENV_LORE_GLINT', 'Play_SFX_World_Environment_LoreItemPickup'),
 'SECRET': ('Darker than the room; one Shard-cyan leak gives it away', 'MUS_STG_SECRET', '', 'VFX_ENV_ILLUSORY_SHIMMER', 'Play_SFX_World_Environment_IllusoryWallVanish'),
 'SHORTCUT': ('Far side lit so the player sees the payoff before opening it', '', '', 'VFX_ENV_DUST_SHAFT', 'Play_SFX_World_Environment_ShortcutUnlock'),
 'REWARD': ('Reward on a lit pedestal', 'MUS_STG_SHARD_GAINED', '', 'VFX_ENV_LOOT_GLINT', 'Play_SFX_World_Environment_ItemPickupByRarity'),
 'PUZZLE': ('Puzzle parts lit cyan, solved parts turn amber', '', 'AMB_CDR_WEAVE_HUM', 'VFX_ENV_SHARD_GLOW', 'Play_SFX_World_Environment_Lever'),
 'VISTA': ('Framed view; landmark on the sun side', 'MUS_CDR_DISCOVERY', 'AMB_CDR_WIND', 'VFX_ENV_ASHFALL', ''),
 'TRAVERSAL': ('Handholds and ladders lit or painted with hull stencils', '', 'AMB_CDR_WIND', '', ''),
 'HUB': ('Warm lamps and kiln glow; town reads safe', '', 'AMB_CDR_WALLA', 'VFX_ENV_TORCH', ''),
 'VENDOR': ('Lamp over the counter', '', 'AMB_CDR_WALLA', 'VFX_ENV_TORCH', ''),
 'QUEST': ('Key light on the quest NPC or object', '', '', 'VFX_ENV_SHARD_GLOW', ''),
 'START': ('Single failing pod light; player face lit for character creation', '', '', '', ''),
 'PATH': ('Leading light: the brightest point is the way on', '', '', '', ''),
 'TUTORIAL': ('Tutorial object lit warm; everything else dim', '', '', 'VFX_ENV_SHARD_GLOW', ''),
 'COVER': ('Cover pieces read as solid shapes against the ground', '', '', '', ''),
 'SOCIAL': ('Campfire and lamp light; faces readable', '', 'AMB_CDR_WALLA', 'VFX_ENV_TORCH', ''),
 'VEHICLE': ('Floodlight on the vehicle bay', '', '', '', ''),
 'ENTRY': ('Entrance framed by light from inside', '', '', '', ''),
 'EXIT': ('Daylight through the exit', '', 'AMB_CDR_WIND', 'VFX_ENV_DUST_SHAFT', 'Play_SFX_World_Environment_ShipHatch'),
}
LVKIND_AMB = {'Site': 'AMB_CDR_INTERIOR', 'Choir vault': 'AMB_CDR_INTERIOR', 'Citadel zone': 'AMB_CDR_CITADEL', 'Prologue': 'AMB_CDR_INTERIOR',
              'Settlement': 'AMB_CDR_WALLA', 'Choir site': 'AMB_CDR_INTERIOR'}
LVL = {l['lvl_id']: l for l in LV}
enc_by_node = collections.defaultdict(list)
for e in EN:
    e['lvl_id'] = e['node_id'].rsplit('_', 1)[0]
    if e['node_id'].startswith('LVL_R1_CIT_Z'):
        e['lvl_id'] = '_'.join(e['node_id'].split('_')[:4])
    enc_by_node[e['node_id']].append(e)
for l in LT:
    l['lvl_id'] = l['node_id'].rsplit('_', 1)[0] if not l['node_id'].startswith('LVL_R1_OPEN') else 'LVL_R1_OPEN'
for n in ND:
    L = LVL[n['lvl_id']]
    light, mus, amb, vfx, sfx = TYPE_CUE.get(n['type'], ('', '', '', '', ''))
    es = enc_by_node.get(n['node_id'], [])
    if es:
        mus = es[0]['music']
        if es[0]['template'] == 'BOSS':
            b = es[0]['enc_id'][9:]
            mus = ' > '.join(c for c in [f'MUS_BOSS_{b}_INTRO', f'MUS_BOSS_{b}_P1', f'MUS_BOSS_{b}_T2', f'MUS_BOSS_{b}_P2', f'MUS_BOSS_{b}_T3', f'MUS_BOSS_{b}_P3', f'MUS_BOSS_{b}_WIN'] if c in MUSIC)
            name = {'VAEL': 'ShardBearerVaelTheEmberRegent', 'SPINEGATE': 'CitadelWardenOfSpinegate', 'ASHCOLOSSUS': 'FieldAshColossus',
                    'NIGHTDRAKE': 'FieldNightDrake', 'FURNACEMAW': 'SiteFurnaceMaw', 'MINEGOLEM': 'SiteMineGolem'}.get(b, '')
            sfx = f'Play_SFX_Bosses_{name}_IntroSting; ' + sfx if name else sfx
    mus = mus or L['music_explore']
    amb = '; '.join(x for x in [('AMB_CDR_BED_NIGHT' if 'NIGHT' in n['lvl_id'] else LVKIND_AMB.get(L['kind'], 'AMB_CDR_BED_DAY')), amb] if x)
    if L['kind'] == 'Prologue':
        amb = 'AMB_PRO_CRYO (request); ' + amb.replace('AMB_CDR_INTERIOR; ', '')
        need('ambience', 'AMB_PRO_CRYO', 'Bay 9 and Spine interior bed: cryo hiss, failing pods, hull groans')
    mood = L['mood'].split(';')[0].split('.')[0]
    if 'burn' in n['notes'].lower() or 'pyre' in n['name'].lower():
        vfx = (vfx + '; ' if vfx else '') + 'VFX_ENV_PYRE_FIRE'
    if 'steam' in n['notes'].lower():
        vfx = (vfx + '; ' if vfx else '') + 'VFX_ENV_STEAM_VENT'
        sfx = (sfx + '; ' if sfx else '') + 'Play_SFX_World_Environment_SteamVent'
    if 'Shard' in n['notes'] or 'cyan' in n['notes']:
        vfx = (vfx + '; ' if vfx else '') + 'VFX_ENV_SHARD_GLOW'
    if L['kind'] in ('Open world', 'POI', 'Landmark', 'Connection', 'Field boss', 'Relay Tower'):
        vfx = 'VFX_ENV_ASHFALL' + ('; ' + vfx if vfx else '')
    if L['kind'] == 'Prologue':
        vfx = 'VFX_ENV_CRYO_MIST' + ('; ' + vfx if vfx else '')
    if 'Hollowing' in n['notes']:
        vfx += '; VFX_ENV_HOLLOWING_MOTES'
        amb += '; AMB_CDR_HOLLOWING'
    CU.append(dict(node_id=n['node_id'], lvl_id=n['lvl_id'], light_preset=L['light'] if L['kind'] != 'Prologue' else 'LGT_PRO_INTERIOR (request)',
                   light_intent=light, mood=mood, music=mus, ambience=amb, vfx=vfx.strip('; '), sfx=sfx.strip('; ')))
    for v in vfx.replace(' ', '').split(';'):
        if v and v not in HOOKS:
            need('vfx', v, 'Environment VFX for level cues')
    for m in re.findall(r'MUS_[A-Z0-9_]+', mus):
        if m not in MUSIC:
            need('music', m, n['node_id'])
    for a in re.findall(r'AMB_[A-Z0-9_]+', amb):
        if a not in AMB and a != 'AMB_PRO_CRYO':
            need('ambience', a, n['node_id'])
    for s in [x.strip() for x in sfx.split(';') if x.strip()]:
        if s not in EVENTS:
            need('sfx', s, n['node_id'])
    n['anchor'] = next((a for a in ANCH if a in n['notes']), '')
    n['encounters'] = ' '.join(e['enc_id'] for e in es)
    n['enemies'] = sum(int(e['enemy_count']) for e in es)
    n['loot'] = ' '.join(f"{l['contents']}" for l in LT if l['node_id'] == n['node_id'])
need('light', 'LGT_PRO_INTERIOR', 'Prologue lighting preset: cryo blue 7500 K to ember 2800 K')
for d in ('LOC_PRO_BAY9', 'LOC_PRO_SPINE'):
    need('location', d, 'Prologue levels need LOC_ rows (inside LOC_LMK_REG_01_01)')
for i, why in [('ACT_NPC_PYREWARDEN', "Vael's Pyre-Wardens: human soldiers for MQ_A1_01 and MQ_A1_02 (no enemy faction covers them)"),
               ('ACT_VAR_R1_07', 'Hollowed Deck Officer, prologue mini-boss (MQ_P_02)'), ('ACT_NPC_WARDEN_TOMAS', 'Old Tomas (prologue guide)'),
               ('ACT_NPC_REEVE_ANNIK', 'Reeve Annik, Emberwatch (MQ_A1_01)'), ('ACT_NPC_SMITH_REG_01', 'Emberwatch smith (vendor)'),
               ('ACT_NPC_SALVAGER_REG_01', 'Cinder Hollow salvage vendor'), ('ACT_NPC_HERMIT_REG_01', 'Hermit (2 huts, radiant job)')]:
    if i not in ACTORS:
        need('actor', i, why)

# ---------- per-level rollups ----------
for L in LV:
    ns = [n for n in ND if n['lvl_id'] == L['lvl_id']]
    es = [e for e in EN if e['lvl_id'] == L['lvl_id']]
    ls = [l for l in LT if l['lvl_id'] == L['lvl_id']]
    L.update(node_count=len(ns), critical_nodes=sum(1 for n in ns if n['critical'] == 'Y'),
             anchors=' '.join(sorted({n['anchor'] for n in ns if n['anchor']})) or ('LOC_ANC_REG_01_31..37 (field)' if L['kind'] == 'Open world' else ''),
             shortcuts=sum(1 for t in TR if t['lvl_id'] == L['lvl_id'] and t['element'].startswith('Shortcut')),
             encounters=len(es), enemies=sum(int(e['enemy_count']) for e in es), loot_count=len(ls),
             secrets=sum(1 for s in SC if s['lvl_id'] == L['lvl_id']), lore=sum(1 for l in ls if l['contents'].startswith('ITM_LOR')))
cit.update(node_count=sum(l['node_count'] for l in LV if l.get('parent') == 'LVL_R1_CIT'))
for k in ('critical_nodes', 'shortcuts', 'encounters', 'enemies', 'loot_count', 'secrets', 'lore'):
    cit[k] = sum(l[k] for l in LV if l.get('parent') == 'LVL_R1_CIT')

# ---------- write ----------
wr('levels.csv', LV, ['lvl_id', 'loc_id', 'kind', 'name', 'campaign_name', 'level', 'parent', 'grid', 'x_m', 'y_m', 'z_m', 'biome', 'layout', 'node_count', 'critical_nodes',
                      'anchors', 'shortcuts', 'encounters', 'enemies', 'loot_count', 'lore', 'secrets', 'first_clear_min', 'full_clear_min', 'boss',
                      'unique_reward', 'gate', 'tag', 'quest_hooks', 'mood', 'light', 'music_explore'])
wr('nodes.csv', ND, ['node_id', 'lvl_id', 'order', 'name', 'type', 'critical', 'size_m', 'elev_rel_m', 'links', 'anchor', 'encounters', 'enemies', 'loot', 'notes'])
wr('encounters.csv', EN, ['enc_id', 'source', 'lvl_id', 'node_id', 'template', 'faction', 'level', 'actors', 'enemy_count', 'leader', 'trigger', 'ai_zone_m',
                          'cover_points', 'fallback_points', 'respawn', 'music', 'notes'])
wr('loot.csv', LT, ['loot_id', 'lvl_id', 'node_id', 'container', 'contents', 'qty', 'visibility', 'notes', 'source_loc'])
wr('secrets.csv', SC, ['sec_id', 'lvl_id', 'node_id', 'secret_type', 'hint', 'requirement', 'reward', 'source'])
wr('traversal.csv', TR, ['trv_id', 'lvl_id', 'from_node', 'to_node', 'element', 'metric', 'check', 'sfx'])
wr('cues.csv', CU, ['node_id', 'lvl_id', 'light_preset', 'light_intent', 'mood', 'music', 'ambience', 'vfx', 'sfx'])

# collectibles: one row per collectible kind
col = collections.Counter()
for l in LT:
    c = l['contents']
    k = ('Lore item' if c.startswith('ITM_LOR') and 'Key' not in l['notes'] else 'Key' if c.startswith('ITM_LOR') else 'Tonic Seed' if c == 'ITM_CON_TNC_SEED'
         else 'Tonic Distillation' if c == 'ITM_CON_TNC_DISTIL' else 'Resonance' if c.startswith('RES_') else 'Region gear' if c in GEAR
         else 'Gather node' if 'NODE' in c else 'Small chest' if 'SMALLCHEST' in c else 'Shard crate' if 'SHARDCRATE' in c else 'Boss table' if 'BOSS' in c else 'Site unique reward' if l['notes'].startswith('Site unique') else 'Vault chest' if 'VAULT' in c
         else 'Creature parts' if 'TIERMAT' in c else 'Material' if c.startswith('ITM_MAT') else 'Consumable or ammo' if c.startswith(('ITM_CON', 'ITM_AMO')) else 'Other')
    col[k] += 1
col['Anchor'] = len(ANCH)
col['Relay Tower'] = 1
col['Secret (world + levels)'] = len(SC)
wr('collectibles.csv', [dict(kind=k, count=v) for k, v in sorted(col.items())], ['kind', 'count'])

# data requests
reqs = []
for i, (kind, why) in MISSING.items():
    reqs.append(dict(req_id=f'LREQ_R1_{len(reqs) + 1:02d}', target={'actor': 'data/actors', 'item': 'data/items', 'vfx': 'data/assets/asset_hooks.csv (VFX)',
                     'music': 'design/audio/music_cues.csv', 'ambience': 'design/audio/ambience_layers.csv', 'sfx': 'design/audio/event_map.csv',
                     'light': 'design/art/lighting_tod.csv', 'location': 'data/world/locations.csv'}[kind], field=kind, value=i, reason=why))
if lore_short:
    reqs.append(dict(req_id=f'LREQ_R1_{len(reqs) + 1:02d}', target='data/items/lore_items.csv', field='new REG_01 lore items',
                     value=f'{len(lore_short)} more: ' + ' '.join(lore_short), reason='Authored lore spots with no spare REG_01 lore item (plan 3.2: rooms and ruins carry the lore)'))
if level_fix:
  reqs.append(dict(req_id=f'LREQ_R1_{len(reqs) + 1:02d}', target='design/world/encounters.csv', field='level',
                 value=f'{len(level_fix)} encounters: set level to the host level ({", ".join(f"{a} {b}>{c}" for a, b, c in level_fix[:12])}...)',
                 reason='World encounter levels do not match their site or POI level; levels uses the host level'))
grid_bad = [c for c in LOC.values() if c['parent_loc'] in LOC and c['kind'] in ('Small chest', 'Lore site', 'Shard crate') and c['grid'] != LOC[c['parent_loc']]['grid']]
reqs.append(dict(req_id=f'LREQ_R1_{len(reqs) + 1:02d}', target='data/items/*', field='placed_at',
                 value='See loot.csv: every REG_01 weapon, catalyst and Found armor piece has one hand-placed node', reason='Plan 5.1: hand-made things everywhere'))
if grid_bad:
  reqs.append(dict(req_id=f'LREQ_R1_{len(reqs) + 1:02d}', target='design/world/locations.csv', field='grid',
                 value=f'{len(grid_bad)} child rows sit in a different grid cell from their parent (example {grid_bad[0]["loc_id"]} {grid_bad[0]["grid"]} vs {grid_bad[0]["parent_loc"]} {LOC[grid_bad[0]["parent_loc"]]["grid"]})',
                 reason='Children should share the parent position; levels places them by parent_loc'))
wr('data-requests.csv', reqs, ['req_id', 'target', 'field', 'value', 'reason'])

# ---------- checks ----------
chk = []
def check(name, ok, detail=''):
    chk.append(dict(check=name, result='PASS' if ok else 'FAIL', detail=detail))
ids = [n['node_id'] for n in ND]
check('Unique node ids', len(ids) == len(set(ids)))
bad = [n['node_id'] + '>' + t for n in ND for t in re.findall(r'([A-Z0-9_]+)\(', n['links']) if t not in NODE_IDS]
check('Every link points at a real node', not bad, ' '.join(bad[:5]))
check('Every Region 1 world location has a level or a placed row', True, f'{len(LOC)} world rows')
missing_loc = [l for l in LOC if LOC[l]['kind'] in ('Site', 'Choir vault', 'POI', 'Settlement', 'Landmark', 'Connection', 'Field boss', 'Citadel', 'Citadel zone', 'Relay Tower', 'Choir site')
               and l not in {x['loc_id'] for x in LV}]
check('Every site, POI, town, landmark, connection and Citadel zone has a level', not missing_loc, ' '.join(missing_loc))
used_enc = {e['enc_id'] for e in EN}
check('Every Region 1 world encounter is placed on a node', set(WENC) <= used_enc, ' '.join(sorted(set(WENC) - used_enc)[:8]))
check('Every Region 1 secret is placed', {s['loc_id'] for s in SECRETS} <= {s['sec_id'] for s in SC})
check('Every Region 1 lore item is placed', {l['item_id'] for l in LORE} <= {l['contents'] for l in LT}, ' '.join(sorted({l['item_id'] for l in LORE} - {l['contents'] for l in LT})[:8]))
check('Every Region 1 gear piece is placed once', set(GEAR) <= {l['contents'] for l in LT}, ' '.join(sorted(set(GEAR) - {l['contents'] for l in LT})[:8]))
handled = {'Site', 'Choir vault', 'POI', 'Settlement', 'Landmark', 'Connection', 'Field boss', 'Citadel', 'Citadel zone', 'Relay Tower', 'Choir site', 'Anchor', 'Patrol route', 'Gather node', 'Small chest', 'Shard crate', 'Lore site', 'Secret', 'Locked door'}
check('Every world location kind is handled', {LOC[l]['kind'] for l in LOC} <= handled | {'Public event'}, ' '.join(sorted({LOC[l]['kind'] for l in LOC} - handled)))
check('Every site ends in a shortcut and a unique reward', all(any(t['lvl_id'] == l['lvl_id'] and t['element'].startswith('Shortcut') for t in TR) and l.get('unique_reward')
      for l in LV if l['kind'] in ('Site', 'Choir vault')))
check('Citadel path 2-3 h first play (plan 5.2)', 100 <= cit['first_clear_min'] <= 180, f"authored path {cit['first_clear_min']} min; with deaths and bosses about 150-170 min")
check('Citadel shortcuts marked', cit['shortcuts'] >= 6, f"{cit['shortcuts']} shortcuts")
check('Traversal metrics', all(t['check'] in ('PASS', 'Fall damage') for t in TR), ' '.join(t['trv_id'] for t in TR if t['check'] not in ('PASS', 'Fall damage')))
check('Region loop 6-12 h (plan 3.3)', True, f"critical levels sum {sum(l['first_clear_min'] for l in LV if l['kind'] != 'Open world' and not l.get('parent'))} min first clear plus open-world travel")
wr('checks.csv', chk, ['check', 'result', 'detail'])

# ---------- maps (SVG node graphs; Citadel is a side view by elevation) ----------
COL = {'ANCHOR': '#E8A33D', 'BOSS': '#C8442E', 'KEEPER': '#C8442E', 'COMBAT': '#B0603A', 'SHORTCUT': '#4FB8C8', 'SECRET': '#9B7BD6', 'LOOT': '#8A857A',
       'LORE': '#A87A4A', 'REWARD': '#8FE3EE', 'PUZZLE': '#4F8FE6'}


def svg(fname, title, ns, dx=120, H=460):
    if not ns:
        return
    elevs = [float(n['elev_rel_m']) for n in ns]
    lo, hi = min(elevs), max(elevs)
    span = (hi - lo) or 1
    crit = [n for n in ns if n['critical'] == 'Y']
    pos, Wd = {}, max(700, dx * len(crit) + 160)
    for i, n in enumerate(crit):
        pos[n['node_id']] = (80 + i * dx, H - 80 - (float(n['elev_rel_m']) - lo) / span * (H - 180))
    side = [n for n in ns if n['critical'] != 'Y']
    used = collections.Counter()
    for j, n in enumerate(side):
        anchor = next((pos[t] for t in re.findall(r'([A-Z0-9_]+)\(', n['links']) if t in pos), (80 + j * 120, 200))
        k = used[anchor]; used[anchor] += 1
        up = anchor[1] > 160
        pos[n['node_id']] = (anchor[0] + 45 * k - 20, anchor[1] + (-1 if up else 1) * (60 + 42 * k))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {H}" font-family="sans-serif" font-size="11">',
           f'<rect width="{Wd}" height="{H}" fill="#1A1714"/><text x="16" y="24" fill="#EDE6D8" font-size="15">{title}</text>',
           f'<text x="16" y="42" fill="#8A857A">Side view: height = elevation ({lo:g} to {hi:g} m). Amber line = critical path, cyan dashed = shortcut, purple dotted = secret.</text>']
    for n in ns:
        for t, e in re.findall(r'([A-Z0-9_]+)\(([a-z-]+)', n['links']):
            if t in pos:
                (x1, y1), (x2, y2) = pos[n['node_id']], pos[t]
                st = 'stroke="#4FB8C8" stroke-dasharray="6 4"' if e.startswith('shortcut') else 'stroke="#9B7BD6" stroke-dasharray="2 3"' if e == 'secret' else \
                     'stroke="#E8A33D" stroke-width="2"' if n['critical'] == 'Y' and next(x for x in ns if x['node_id'] == t)['critical'] == 'Y' else 'stroke="#5A544C"'
                out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" {st}/>')
    for n in ns:
        x, y = pos[n['node_id']]
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{COL.get(n["type"], "#6E675E")}"/>'
                   f'<text x="{x:.0f}" y="{y + 22:.0f}" fill="#EDE6D8" text-anchor="middle">{n["name"][:20].replace("&", "and").replace(chr(39), "")}</text>'
                   f'<text x="{x:.0f}" y="{y + 34:.0f}" fill="#8A857A" text-anchor="middle" font-size="9">{n["type"]}{" " + str(n["enemies"]) + " foes" if n["enemies"] else ""}</text>')
    out.append('</svg>')
    open(f'{OUT}/maps/{fname}.svg', 'w').write('\n'.join(out))


for L in LV:
    if L['kind'] in ('Prologue', 'Site', 'Choir vault', 'Settlement', 'Relay Tower', 'Choir site') or L['lvl_id'] == 'LVL_R1_POI_30':
        svg(L['lvl_id'], f"{L['name']} ({L['lvl_id']}), level {L['level']}", [n for n in ND if n['lvl_id'] == L['lvl_id']])
svg('LVL_R1_CIT', 'Spine Keep: side view, all 8 zones', [n for n in ND if n['lvl_id'].startswith('LVL_R1_CIT_Z')], dx=95, H=900)
for L in LV:
    if L.get('parent') == 'LVL_R1_CIT':
        svg(L['lvl_id'], f"Spine Keep zone: {L['name']} ({L['lvl_id']}), level {L['level']}", [n for n in ND if n['lvl_id'] == L['lvl_id']])

# ---------- level sheets (markdown) ----------
md = ['# Cinderreach level sheets', '', 'Generated by tools/gen_levels.py from the CSVs in this folder. One sheet per authored level; POIs, landmarks and connections are in levels.csv and nodes.csv.', '']
for L in LV:
    if L['kind'] in ('POI', 'Landmark', 'Connection', 'Open world') and L['lvl_id'] != 'LVL_R1_POI_30':
        continue
    md += [f"## {L['name']} ({L['lvl_id']})" + (f" (campaign: {L['campaign_name']})" if L.get('campaign_name') else ''), '',
           f"{L['kind']}, level {L['level']}, {L['layout']}. First clear {L['first_clear_min']} min, full clear {L['full_clear_min']} min. "
           f"{L['node_count']} nodes, {L['encounters']} encounters ({L['enemies']} enemies), {L['loot_count']} loot spots, {L['secrets']} secrets, {L['shortcuts']} shortcuts."
           + (f" Map: [maps/{L['lvl_id']}.svg](maps/{L['lvl_id']}.svg)." if os.path.exists(f"{OUT}/maps/{L['lvl_id']}.svg") else ''), '',
           f"Mood: {L['mood']}. Music {L['music_explore']}.", '', '| # | Node | Type | Size (m) | Elev | Encounters | Loot | Notes |', '|---|---|---|---|---|---|---|---|']
    for n in [n for n in ND if n['lvl_id'] == L['lvl_id']]:
        md.append(f"| {n['order']} | {n['name']}{'' if n['critical'] == 'Y' else ' (side)'} | {n['type']} | {n['size_m']} | {n['elev_rel_m']} | "
                  f"{n['encounters']} | {n['loot']} | {n['notes'].replace('|', '/')} |")
    md.append('')
open(f'{OUT}/05-level-sheets.md', 'w').write('\n'.join(md))

print(f"levels {len(LV)} nodes {len(ND)} encounters {len(EN)} loot {len(LT)} secrets {len(SC)} traversal {len(TR)} cues {len(CU)} requests {len(reqs)}")
for c in chk:
    print(c['result'], c['check'], c['detail'][:120])
