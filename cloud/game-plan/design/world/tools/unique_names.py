#!/usr/bin/env python3
"""Continuity CP-11 (decided 2026-10-06): every place in design/world/locations.csv gets a unique name.

Generic labels ("Gather node, Cinderreach", "Lore site, Saltmere", "Anchor, LOC_DGN_REG_01_07") and repeats are
renamed from the nearest named place, the parent, a region word or the grid square. IDs never change.
Renames are logged in name_fixes.csv (gen_world_design.py applies that file too) and written to every
design/world CSV that has loc_id and name columns. Safe to re-run: a clean file gives no renames."""
import collections, csv, glob, math, os, re

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMED = ('Site', 'POI', 'Settlement', 'Citadel', 'Landmark', 'Choir vault', 'Field boss')
LORE_NOUNS = ['Memorial', 'Cairn', 'Marker Stone', 'Names Wall', 'Watch Post', 'Hull Marker', 'Old Beacon', 'Wreck Log']


def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def wr(p, rows):
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


locs = rd(os.path.join(W, 'locations.csv')); byid = {r['loc_id']: r for r in locs}
count = collections.Counter(r['name'] for r in locs)
region_name = {r['reg_id']: r['name'] for r in rd(os.path.join(W, 'regions_layout.csv'))}
LABEL_TAILS = set(region_name.values()) | {'Field', 'The Quiet', 'The Undervault'}
generic = lambda n: 'LOC_' in n or (', ' in n and n.split(', ', 1)[1] in LABEL_TAILS)  # "Gather node, Cinderreach"

named = collections.defaultdict(list)  # region -> [(loc_id, name, kind, (x, y))]
for r in locs:
    if r['kind'] in NAMED and r['layer'] == 'Surface' and not generic(r['name']):
        named[r['region']].append((r['loc_id'], r['name'], r['kind'], (float(r['x_m']), float(r['y_m']))))
poi_words = {g: list(dict.fromkeys(n.split()[0] for _, n, k, _ in v if k == 'POI')) for g, v in named.items()}


def nearest(r):
    c = [l for l in named[r['region']] if l[0] != r['loc_id']]
    if not c or not r['x_m']:
        return byid[r['parent_loc']]['name'] if r['parent_loc'] in byid else r['region']
    xy = (float(r['x_m']), float(r['y_m']))
    return min(c, key=lambda l: math.dist(l[3], xy))[1]


def place(r):
    p = byid.get(r['parent_loc'])
    return p['name'] if p and not generic(p['name']) else nearest(r)


def base(r):
    if not generic(r['name']) and count[r['name']] == 1:
        return r['name']
    k, n = r['kind'], re.sub(r'LOC_[A-Z0-9_]+', lambda m: new.get(m.group(0)) or byid.get(m.group(0), {}).get('name', m.group(0)), r['name'])
    if k == 'Anchor':
        where = n.split(', ', 1)[1] if n.startswith('Anchor, ') and not n.endswith('Field') else nearest(r)
        return f"{where} {'Deep ' if 'interior' in r['tags'] else 'Gate ' if 'entrance' in r['tags'] else ''}Anchor"
    if k == 'Gather node':
        kind = re.sub(r'_\d+$', '', r['tags'] or 'gather node').replace('_', ' ').capitalize()
        return f"{'Herb patch' if kind == 'Herb' else kind} near {nearest(r)}"
    if k in ('Locked door', 'Small chest', 'Shard crate'):
        return f'{k}, {place(r)}'
    if k == 'Patrol route':
        return n
    if k == 'Lore site' and n == 'Lore site, ' + region_name.get(r['region'], ''):
        return f'{nearest(r)} {LORE_NOUNS[0]}'
    if k == 'Landmark' and count[n] > 1:
        return n.removeprefix('The ') + ' Sightline'
    if k == 'Connection' and count[n] > 1:
        return n + ' shaft'
    return n


new = {}
for r in sorted(locs, key=lambda r: r['kind'] == 'Patrol route'):  # patrols name their Anchor, so Anchors go first
    new[r['loc_id']] = base(r)
taken = collections.Counter(new.values())
for r in sorted(locs, key=lambda r: r['loc_id']):  # repeats: lore nouns, region words, then grid square, then a number
    n = new[r['loc_id']]
    if taken[n] < 2:
        continue
    tries = [n.replace(LORE_NOUNS[0], x) for x in LORE_NOUNS[1:]] if LORE_NOUNS[0] in n else []
    tries += [n.replace(n.split()[0], w, 1) for w in poi_words.get(r['region'], [])] if r['kind'] == 'POI' else []
    tries += [n.replace(' at ', ' behind ', 1)] if ' at ' in n else []
    tries += [f"{n}, {r['grid']}"] if r['grid'] else []
    pick = next((t for t in tries if not taken[t]), None) or next(f'{n} {i}' for i in range(2, 999) if not taken[f'{n} {i}'])
    taken[n] -= 1; taken[pick] += 1; new[r['loc_id']] = pick

fixes = [dict(loc_id=r['loc_id'], old_name=r['name'], new_name=new[r['loc_id']]) for r in locs if new[r['loc_id']] != r['name']]
if fixes:
    FP = os.path.join(W, 'name_fixes.csv')
    old = rd(FP) if os.path.exists(FP) else []
    wr(FP, [o for o in old if o['loc_id'] not in new or new[o['loc_id']] == o['new_name']] + fixes)
    renamed = {f['loc_id']: (f['old_name'], f['new_name']) for f in fixes}
    for p in glob.glob(os.path.join(W, '*.csv')):
        rows = rd(p)
        if p.endswith('name_fixes.csv') or not rows or not {'loc_id', 'name'} <= rows[0].keys():
            continue
        hit = [x for x in rows if renamed.get(x['loc_id'], ('',))[0] == x['name']]
        for x in hit:
            x['name'] = renamed[x['loc_id']][1]
        if hit:
            wr(p, rows); print(os.path.basename(p), len(hit), 'renamed')
left = [n for n, c in taken.items() if c > 1]
print(f'{len(fixes)} renames; repeated names left: {len(left)}')
