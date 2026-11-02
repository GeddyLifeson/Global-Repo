#!/usr/bin/env python3
"""Append-only pass over the frozen design/world/locations.csv (3 Oct 2026).

Adds the places requested by design/campaign (LOC_CQ_* with no world match) and by
design/levels/*/data-requests.csv. Existing rows are never renamed, renumbered,
moved or reordered; new rows are appended at the end. Writes new_locations_map.csv
(old or requested ID -> world ID) so the campaign and level generators can re-key.
Safe to re-run: rows already appended are skipped.
"""
import csv, hashlib, math, os, re, random

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(W, '..')
def rd(p):
    with open(p, newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

LOCP = os.path.join(W, 'locations.csv')
locs = rd(LOCP); cols = list(locs[0].keys()); byid = {l['loc_id']: l for l in locs}
reg = {r['reg_id']: r for r in rd(os.path.join(W, 'regions_layout.csv'))}
NEW, MAP, ANCH_NEW = [], [], []

def grid(x, y):
    c = int(float(x) // 250); r = int(float(y) // 250) + 1
    return f"{chr(65 + c) if c < 26 else 'A' + chr(39 + c)}{r}"

def lvl(rg, x, y):
    g = reg[rg]; cx, cy, rx, ry = (float(g[k]) for k in ('center_x_m', 'center_y_m', 'radius_x_m', 'radius_y_m'))
    def ep(a): a = math.radians(float(a)); return cx + rx * .9 * math.cos(a), cy + ry * .9 * math.sin(a)
    (ex, ey), (ax, ay) = ep(g['entry_bearing_deg']), ep(g['apex_bearing_deg'])
    t = max(0, min(1, ((x - ex) * (ax - ex) + (y - ey) * (ay - ey)) / ((ax - ex) ** 2 + (ay - ey) ** 2)))
    return round(int(g['level_min']) + (int(g['level_max']) - int(g['level_min'])) * t)

def add(lid, kind, region, name, x, y, z, layer, parent='', level='', gate='', tags='', notes='', src=''):
    if lid in byid: return False
    row = {c: '' for c in cols}
    row.update(loc_id=lid, kind=kind, region=region, name=name, layer=layer, parent_loc=parent, x_m=x, y_m=y, z_m=z,
               grid=grid(x, y) if layer in ('Surface', 'Undervault') else '', level=level,
               biome=byid[parent]['biome'] if parent in byid else '', gate=gate, tags=tags, notes=(notes + f' [appended: {src}]').strip())
    byid[lid] = row; NEW.append(row); return True

def mapping(old, new, how, src):
    MAP.append(dict(old_id=old, world_id=new, how=how, source=src))

def nearest(region, x, y, kinds=('Site', 'POI', 'Settlement', 'Citadel', 'Choir vault', 'Landmark', 'Field boss')):
    c = [l for l in locs if l['region'] == region and l['kind'] in kinds and l['layer'] == 'Surface']
    return min(c, key=lambda l: math.dist((float(l['x_m']), float(l['y_m'])), (x, y))) if c else None

def free_spot(rg, lid):
    """Deterministic spot inside the region, at least 80 m from every placed row."""
    g = reg[rg]; cx, cy, rx, ry = (float(g[k]) for k in ('center_x_m', 'center_y_m', 'radius_x_m', 'radius_y_m'))
    R = random.Random(int(hashlib.md5(lid.encode()).hexdigest()[:8], 16))
    pts = [(float(l['x_m']), float(l['y_m'])) for l in byid.values() if l['region'] == rg and l['layer'] == 'Surface']
    for mind in (80, 60, 40, 20):
        for _ in range(3000):
            x, y = R.uniform(cx - rx, cx + rx), R.uniform(cy - ry, cy + ry)
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 > 0.85: continue
            if all(math.dist((x, y), p) >= mind for p in pts): return round(x), round(y)
    return round(cx), round(cy)

# ------------------------------------------------ level-thread aliases (campaign place = existing world place)
alias = {}
for r in rd(os.path.join(D, 'levels/glasswaste/quest_location_aliases.csv')):
    alias[r['quest_loc']] = (r['world_loc'], 'levels/glasswaste/quest_location_aliases.csv')
for r in rd(os.path.join(D, 'levels/thornwood/level_quest_map.csv')):
    if r['quest_loc'].startswith('LOC_CQ') and r['level_loc'] != r['quest_loc']:
        alias.setdefault(r['quest_loc'], (r['level_loc'], 'levels/thornwood/level_quest_map.csv'))
# level-thread positions for campaign places
pos, lvl_names = {}, {}
for f in ('levels/hollowdeep/levels.csv', 'levels/rimefall/levels.csv'):
    for r in rd(os.path.join(D, f)):
        lid = r.get('loc_id') or r.get('level_id')
        if lid and lid.startswith('LOC_CQ') and r.get('x_m'):
            pos[lid] = (float(r['x_m']), float(r['y_m']), r.get('level', ''), r.get('parent', ''), f)
            lvl_names[lid] = r.get('name', '')

# ------------------------------------------------ level-thread new places (done first so campaign aliases to them resolve)
lm1 = byid['LOC_LMK_REG_01_01']
for lid, nm, dz in (('LOC_PRO_BAY9', 'Bay 9 Cryo Ward', -10), ('LOC_PRO_SPINE', 'The Spine', 20)):
    add(lid, 'Prologue', 'REG_01', nm, int(lm1['x_m']), int(lm1['y_m']), int(lm1['z_m']) + dz, 'Surface', 'LOC_LMK_REG_01_01', 1,
        tags='prologue;interior', src='levels/cinderreach LREQ_R1_21/22')
add('LOC_TOWN_REG_03_03', 'Settlement', 'REG_03', "Thorn King's Moot", 7024, 1880, 0, 'Surface', '', 29, tags='town;quests', src='levels/thornwood LREQ_02')
for lid, nm, par, dx in (('LOC_SEC_REG_03_16', 'Illusory wall in the Spice Loft', 'LOC_CIT_REG_03_Z2', 12), ('LOC_SEC_REG_03_17', 'Hidden ledge path above Canopy Works', 'LOC_CIT_REG_03_Z7', -12)):
    z = byid[par]
    add(lid, 'Secret', 'REG_03', nm, int(z['x_m']) + dx, int(z['y_m']) + 8, int(z['z_m']) + 6, 'Surface', par, z['level'], tags='secret', src='levels/thornwood LREQ_05')
byid['LOC_TOWN_REG_03_03']['z_m'] = nearest('REG_03', 7024, 1880)['z_m']
if add('LOC_ANC_REG_03_40', 'Anchor', 'REG_03', "Anchor, Thorn King's Moot", 7039, 1890, byid['LOC_TOWN_REG_03_03']['z_m'], 'Surface',
       'LOC_TOWN_REG_03_03', 29, tags='Town', src='levels/thornwood LREQ_02'):
    ANCH_NEW.append(('LOC_ANC_REG_03_40', 'REG_03', 'Surface', 'Town', 'LOC_TOWN_REG_03_03', 7039, 1890))
# Undervault
add('LOC_UV_CORE', 'Undervault site', 'REG_U', 'The Engine Heart', 5210, 3337, -260, 'Undervault', 'LOC_UV_REG_02_S06', 46, tags='undervault;story', src='levels/undervault UVREQ_01')
def uvsite(lv):
    m = re.match(r'LV_UV_(0\d)_(S\d\d)', lv)
    if m: return f'LOC_UV_REG_{m.group(1)}_{m.group(2)}'
    m = re.match(r'LV_UV_TUN_(\d{4})', lv)
    if m: return f'LOC_UV_TUNNEL_{m.group(1)}'
    m = re.match(r'LV_UV_(0\d)_ENTRY', lv)
    if m: return f'LOC_UV_ENTRY_{m.group(1)}'
    return 'LOC_UV_CORE' if lv.startswith('LV_UV_CORE') else ''
for r in rd(os.path.join(D, 'levels/undervault/anchors.csv')):
    if r['source'] == 'new':
        par = uvsite(r['level_id']); lv = byid[par]['level'] if par in byid else ''
        if add(r['anchor_id'], 'Anchor', 'REG_U', f'Anchor, {par or r["level_id"]}', int(float(r['x_m'])), int(float(r['y_m'])), int(float(r['z_m'])),
               'Undervault', par, lv, tags='Undervault', src='levels/undervault UVREQ_02'):
            ANCH_NEW.append((r['anchor_id'], 'REG_U', 'Undervault', 'Undervault', par, int(float(r['x_m'])), int(float(r['y_m']))))
for r in rd(os.path.join(D, 'levels/undervault/secrets.csv')):
    par = uvsite(r['level_id']); p = byid.get(par)
    if p: add(r['secret_id'], 'Secret', 'REG_U', f"{r['secret_type']} at {p['name']}", int(p['x_m']) + 10, int(p['y_m']) - 10, int(p['z_m']), 'Undervault', par, p['level'],
              gate=r['requirement'], tags='secret', src='levels/undervault UVREQ_03')
for r in rd(os.path.join(D, 'levels/undervault/landmarks_pois.csv')):
    x, y = int(float(r['x_m'])), int(float(r['y_m']))
    sites = [l for l in byid.values() if l['kind'] == 'Undervault site']
    par = min(sites, key=lambda l: math.dist((float(l['x_m']), float(l['y_m'])), (x, y)))
    add(r['poi_id'], r['kind'], 'REG_U', r['name'], x, y, int(float(r['z_m'])), 'Undervault', par['loc_id'], par['level'], tags=r['kind'].lower(), src='levels/undervault UVREQ_04')
# The Quiet
for lid, x, nm in (('LOC_ANC_REG_Q_00', 40, 'Lander'), ('LOC_ANC_REG_Q_08', 1260, 'Joint Bearing'), ('LOC_ANC_REG_Q_09', 2650, 'the Lens')):
    lv = 68 + round(12 * x / 4000); par = 'LOC_Q_HULL' if x < 1300 else 'LOC_Q_GALLERIES'
    if add(lid, 'Anchor', 'REG_Q', f'Anchor, {nm}', x, 250, 0, 'Quiet', par, lv, tags='Quiet', src='levels/orbital-ring ORB_01'):
        ANCH_NEW.append((lid, 'REG_Q', 'Quiet', 'Quiet', par, x, 250))
for r in rd(os.path.join(D, 'levels/orbital-ring/nodes.csv')):
    if r['world_loc']: continue
    x = float(r['x_m']); lid = 'LOC_Q_ORB_' + r['node_id'][7:]
    par = 'LOC_Q_HULL' if x < 1300 else ('LOC_Q_GALLERIES' if x < 2700 else 'LOC_Q_SPINDLE')
    add(lid, 'Quiet room', 'REG_Q', r['name'], round(x), round(float(r['y_m'])), round(float(r['z_m'])), 'Quiet', par, 68 + round(12 * x / 4000),
        tags=r['kind'].lower(), notes=r['purpose'][:120], src='levels/orbital-ring ORB_02')
    mapping(r['node_id'], lid, 'new', 'levels/orbital-ring/nodes.csv')
# Multiplayer: strikes and arenas already exist as LOC_END_*; season-one maps and map nodes are new
for r in rd(os.path.join(D, 'levels/multiplayer/mp_maps.csv')):
    m = r['map_id']; num = m[-2:]
    if m.startswith('LOC_MP_STK_'):
        w = f'LOC_END_STRIKE_{num}'
        if num == 'S1': add(w, 'Strike', 'REG_END', r['name'], 0, 0, 0, 'Instance', level=r['level'], tags='endgame;season 1', src='levels/multiplayer MPR-05')
        mapping(m, w, 'existing' if num != 'S1' else 'new', 'levels/multiplayer/mp_maps.csv')
    elif m.startswith('ARENA_MP_'):
        w = f'LOC_END_ARENA_{num}'
        if num == 'S1': add(w, 'Arena PvP 3v3', 'REG_END', r['name'], 0, 0, 0, 'Instance', level='Normalized', tags='endgame;season 1', src='levels/multiplayer MPR-01/05')
        mapping(m, w, 'existing' if num != 'S1' else 'new', 'levels/multiplayer/mp_maps.csv')
mpmap = {m['old_id']: m['world_id'] for m in MAP}
for r in rd(os.path.join(D, 'levels/multiplayer/mp_nodes.csv')):
    par = mpmap.get(r['map_id'], r['map_id']); lid = 'LOC_MP_' + r['node_id']
    add(lid, 'Map node', 'REG_END', f"{byid[par]['name'] if par in byid else par}: {r['name']}", 0, 0, 0, 'Instance', par, '', tags=r['kind'],
        notes=f"world_loc {r['world_loc']}" if r['world_loc'] else '', src='levels/multiplayer MPR-05')
    mapping(r['node_id'], lid, 'new', 'levels/multiplayer/mp_nodes.csv')

# ------------------------------------------------ campaign places with no world match
names = {r['campaign_id']: r['campaign_name'] for r in rd(os.path.join(D, 'campaign/tools/loc_map.csv'))}
cq = [r['campaign_id'] for r in rd(os.path.join(D, 'campaign/tools/loc_map.csv')) if not r['world_id'] and not r['campaign_id'].endswith('_')]  # skip template prefixes such as LOC_TOWN_REG_
cq += [r['id'] for r in rd(os.path.join(D, 'campaign/data-requests.csv')) if r['id'].startswith('LOC_CQ_') and r['id'] not in cq and r['id'] != 'LOC_CQ_*']
for lid, n in lvl_names.items():  # level-thread places the campaign never listed (hollowdeep LREQ_02)
    if lid not in names:
        cq.append(lid); names[lid] = n
hub = byid['LOC_LANTERN_HOLD']; hubn = 0
for lid in cq:
    nm = names.get(lid) or lid[7:].replace('_', ' ').title()
    if lid in alias and alias[lid][0] in byid:
        mapping(lid, alias[lid][0], 'existing (level-thread alias)', alias[lid][1]); continue
    m = re.match(r'LOC_CQ_(REG_0\d|HUB|UV|Q)_', lid)
    rg = {'HUB': 'REG_HUB', 'UV': 'REG_U', 'Q': 'REG_Q'}.get(m.group(1), m.group(1)) if m else 'REG_HUB'
    if rg == 'REG_HUB':
        a = 2 * math.pi * (hubn % 12) / 12; rr = 90 + 60 * (hubn // 12); hubn += 1
        add(lid, 'Campaign place', 'REG_HUB', nm, int(hub['x_m']) + round(rr * math.cos(a)), int(hub['y_m']) + round(rr * math.sin(a)), int(hub['z_m']), 'Hub',
            'LOC_LANTERN_HOLD', '', tags='campaign;hub', src='campaign/tools/loc_map.csv')
    elif rg in ('REG_U', 'REG_Q'):
        sites = [l for l in byid.values() if l['region'] == rg and l['kind'] in ('Undervault site', 'Quiet sub-area')]
        p = sites[int(hashlib.md5(lid.encode()).hexdigest()[:4], 16) % len(sites)]
        add(lid, 'Campaign place', rg, nm, int(p['x_m']) + 25, int(p['y_m']) + 25, int(p['z_m']), p['layer'], p['loc_id'], p['level'], tags='campaign', src='campaign/tools/loc_map.csv')
    else:
        if lid in pos:
            x, y, lv, par, src = pos[lid]; par = par if par in byid else nearest(rg, x, y)['loc_id']; lv = lv or lvl(rg, x, y)
        else:
            x, y = free_spot(rg, lid); par = nearest(rg, x, y)['loc_id']; lv = lvl(rg, x, y); src = 'placed by world thread'
        add(lid, 'Campaign place', rg, nm, round(x), round(y), byid[par]['z_m'], 'Surface', par, lv, tags='campaign',
            notes='position from ' + src, src='campaign/tools/loc_map.csv')
    mapping(lid, lid, 'new (campaign ID kept)', 'campaign/tools/loc_map.csv')

# ------------------------------------------------ write (append only)
with open(LOCP, 'a', newline='', encoding='utf-8') as f:
    csv.DictWriter(f, fieldnames=cols).writerows(NEW)
AP = os.path.join(W, 'anchors.csv'); acols = list(rd(AP)[0].keys()); have = {a['loc_id'] for a in rd(AP)}
with open(AP, 'a', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=acols)
    for lid, rg, layer, typ, par, x, y in ANCH_NEW:
        if lid not in have: w.writerow(dict(loc_id=lid, region=rg, layer=layer, anchor_type=typ, parent_loc=par, x_m=x, y_m=y, fast_travel='No (until lit)'))
MP = os.path.join(W, 'new_locations_map.csv')
old = rd(MP) if os.path.exists(MP) else []
seen = {(m['old_id'], m['world_id']) for m in old}
with open(MP, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['old_id', 'world_id', 'how', 'source']); w.writeheader()
    w.writerows(old + [m for m in MAP if (m['old_id'], m['world_id']) not in seen])
ids = [l['loc_id'] for l in rd(LOCP)]
print(f'appended {len(NEW)} rows; locations.csv now {len(ids)}; duplicates {len(ids) - len(set(ids))}; map rows {len(MAP)}')
