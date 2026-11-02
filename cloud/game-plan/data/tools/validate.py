#!/usr/bin/env python3
"""Checks that every ID reference in data/*/*.csv resolves, shared names agree and game text fits (B09: max_chars, tokens, STR_ keys). Exit code 1 on any error.
Usage: python3 data/tools/validate.py [--all]  (--all prints every error, not the first 40)"""
import csv, os, re, glob, sys, collections
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOK = re.compile(r'(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![a-z0-9])')
RUNTIME = re.compile(r'\{([A-Z]+)_[a-z_]+\}')
RUNTIME_TOKEN = re.compile(r'\{([A-Z]+_[a-z0-9_]+)\}')
RUNTIME_OK = {'ITM', 'ACT', 'PRK', 'VAR', 'BTN', 'SKL', 'ATTR', 'ELEM', 'STATUS', 'FAC', 'CMP', 'REGION', 'LOC'}  # LOC: {LOC_name} in radiant notices (design/writing request)
MULTI = ('loot_tables', 'vendors', 'enemy_stats_by_level', 'upgrade_costs', 'armor_stat_rolls', 'input_preset_bindings')  # several rows per key by design
STALE = ['Ashfall Reach', 'Region 2', 'Region 3', 'Region 4', 'Region 5', 'Region 6', 'Seals Quartermaster', 'TXT_', 'Lanterns', 'Hardcore']  # bible: ok
# 'Lanterns' means the removed currency; these two place names (design/world/locations.csv) are allowed
NOT_STALE = ('Stilt Lanterns', 'Abbot Lanterns')
def unstale(c):
    for n in NOT_STALE: c = c.replace(n, '')
    return c

T = {}
for p in sorted(glob.glob(os.path.join(D, '*', '*.csv'))):
    with open(p, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    T[os.path.relpath(p, D)] = (rows[0], rows[1:])
defined, err, refs = set(), [], 0
for k, (h, rows) in T.items():
    defined.update(TOK.findall(','.join(h)))
    seen = set()
    for i, r in enumerate(rows):
        if len(r) != len(h): err.append(f'{k} row {i+2}: {len(r)} cells, header has {len(h)}')
        if r: defined.add(r[0])
        if r and r[0] in seen and not any(x in k for x in MULTI): err.append(f'{k}: duplicate id {r[0]}')
        if r: seen.add(r[0])
prefixes = {}
for d in defined:
    for n in range(1, d.count('_') + 1): prefixes['_'.join(d.split('_')[:n])] = 1
for k, (h, rows) in T.items():
    for r in rows:
        for j, c in enumerate(r):
            for s in STALE:
                if s in unstale(c): err.append(f'{k} {r[0]} [{h[j]}]: stale name "{s}"')
            for m in RUNTIME.finditer(c):
                if m.group(1) not in RUNTIME_OK: err.append(f'{k} {r[0]}: unknown runtime token {m.group(0)}')
            if j == 0: continue
            for m in TOK.finditer(c):
                t, after = m.group(0), c[m.end():m.end() + 2]
                refs += 1
                if after.startswith(('_*', '_<', '*')) or re.match(r'_[a-z]', after):
                    if t not in defined and t not in prefixes: err.append(f'{k} {r[0]} [{h[j]}]: pattern {t}_* matches nothing')
                elif t not in defined:
                    err.append(f'{k} {r[0]} [{h[j]}]: {t} does not resolve')
# shared names must agree with the owning table
S = {r[0]: r[2] for f in ('ui/strings.csv', 'ui/strings_data.csv') for r in T[f][1]}
def need(sid, text, owner):
    if sid not in S: err.append(f'{owner}: missing string {sid}')
    elif text is not None and S[sid] != text: err.append(f'{owner}: {sid} says "{S[sid]}", owner says "{text}"')
rows = lambda k: [dict(zip(T[k][0], r)) for r in T[k][1]]
for r in rows('actors/skills.csv'): need('STR_SKILL_' + r['SKL_ID'][4:], r['Skill'], 'actors/skills.csv')
for r in rows('actors/factions.csv'): need('STR_' + r['FAC_ID'], r['Faction'], 'actors/factions.csv')
for r in rows('actors/origins.csv'): need('STR_ORIGIN_' + r['ORG_ID'][4:], r['Origin'], 'actors/origins.csv')
for r in rows('actors/status_effects.csv'):
    if r['STS_ID'] != 'STS_EXHAUST': need('STR_STATUS_' + r['STS_ID'][4:], r['Status'], 'actors/status_effects.csv')
for r in rows('world/regions.csv'):
    if r['kind'] != 'Drop band': need(r['str_id'], r['name'], 'world/regions.csv')
for r in rows('items/melee_classes.csv') + rows('items/firearm_classes.csv'): need('STR_WFAM_' + r['class_id'][8:], r['name'], 'items classes')
for r in rows('items/items_index.csv'):
    if r['category'] != 'Lore item': need(f"STR_{r['item_id']}_NAME", r['name'], 'items/items_index.csv')
for r in rows('items/lore_items.csv'): need(r['text_id'], None, 'items/lore_items.csv')
# B09 text checks: length within max_chars, well-formed {PREFIX_name} tokens listed in the tokens column, every STR_ key reference resolves
STRKEY = re.compile(r'(?<![A-Za-z0-9_])STR_[A-Z0-9]+(?:_[A-Z0-9]+)*(?![A-Za-z0-9_*<])')
for f in ('ui/strings.csv', 'ui/strings_data.csv'):
    for r in rows(f):
        sid, t = r['str_id'], r['text_en']
        if not t.strip(): err.append(f'{f} {sid}: empty text')
        if not r['max_chars'].isdigit(): err.append(f'{f} {sid}: max_chars "{r["max_chars"]}" is not a number')
        elif len(t) > int(r['max_chars']): err.append(f'{f} {sid}: {len(t)} chars over max_chars {r["max_chars"]}')
        if re.search(r'[{}]', RUNTIME_TOKEN.sub('', t)): err.append(f'{f} {sid}: broken token in "{t[:60]}"')
        if set(r['tokens'].split()) != set(RUNTIME_TOKEN.findall(t)): err.append(f'{f} {sid}: tokens column "{r["tokens"]}" does not match the text')
for k, (h, rr) in T.items():
    for r in rr:
        for j, c in enumerate(r):
            if j == 0 and k in ('ui/strings.csv', 'ui/strings_data.csv'): continue
            for m in STRKEY.findall(c):
                if m not in S: err.append(f'{k} {r[0]} [{h[j]}]: {m} is not in the string tables')
for r in rows('ui/codex_entries.csv'):
    for c in ('t1_str', 't2_str', 't3_str', 'ostra_str'):
        if len(S.get(r[c], '')) > int(r['max_chars']): err.append(f"ui/codex_entries.csv {r['cdx_id']}: {r[c]} over max_chars {r['max_chars']}")
REGN = {r['reg_id']: r['name'] for r in rows('world/regions.csv')}
for k, (h, rr) in T.items():
    for j, c in enumerate(h):
        if c.lower() in ('region name', 'region_name'):
            ri = j - 1
            for r in rr:
                if r[ri] in REGN and r[j] != REGN[r[ri]] and r[ri] != 'REG_END': err.append(f'{k} {r[0]}: region {r[ri]} named "{r[j]}", world says "{REGN[r[ri]]}"')
for k in ('actors/enemy_attacks.csv', 'actors/boss_moves.csv'):   # wind-up minimums by attack type
    for r in rows(k):
        lo = 8 if r.get('Attack type') == 'Follow-up' else 12   # follow-ups 8, openers and standalone 12
        if r.get('Attack type') not in ('Opener', 'Standalone', 'Follow-up'): err.append(f"{k} {r[T[k][0][0]]}: Attack type missing")
        if r['Startup frames'].isdigit() and int(r['Startup frames']) < lo: err.append(f"{k} {r[T[k][0][0]]}: {r.get('Attack type')} startup {r['Startup frames']} < {lo} frames")
# dye colors must match their names: hue words need a hue in range, light/dark words need matching lightness
import colorsys
HUE = {'Red': (340, 20), 'Crimson': (340, 15), 'Wine': (330, 10), 'Rust': (5, 30), 'Orange': (15, 40), 'Copper': (15, 35), 'Amber': (30, 50), 'Saffron': (35, 50),
       'Gold': (35, 55), 'Brass': (35, 55), 'Bronze': (20, 45), 'Yellow': (40, 60), 'Olive': (50, 75), 'Moss': (70, 110), 'Pine': (120, 160), 'Jade': (130, 165),
       'Verdigris': (145, 180), 'Teal': (165, 190), 'Cyan': (180, 200), 'Sky': (195, 220), 'Cerulean': (195, 215), 'Blue': (200, 230), 'Cobalt': (210, 230),
       'Navy': (210, 235), 'Lavender': (250, 280), 'Violet': (260, 290), 'Plum': (290, 330), 'Pink': (320, 350), 'Clay': (10, 30)}
LIGHT = {'White': (0.80, 1), 'Snow': (0.85, 1), 'Ivory': (0.65, 1), 'Pearl': (0.80, 1), 'Starlight': (0.80, 1), 'Black': (0, 0.20), 'Obsidian': (0, 0.25),
         'Void': (0, 0.15), 'Charcoal': (0, 0.30), 'Silver': (0.40, 0.85)}
for r in rows('items/cosmetics.csv'):
    if r['kind'] != 'Dye' or not r['color_hex'].startswith('#'): continue
    rr, gg, bb = (int(r['color_hex'][k:k + 2], 16) / 255 for k in (1, 3, 5)); h, l, s = colorsys.rgb_to_hls(rr, gg, bb); h *= 360
    for w in r['name'].replace(' Dye', '').split():
        if w in HUE and s > 0.12:
            lo, hi = HUE[w]
            if not (lo <= h <= hi if lo < hi else h >= lo or h <= hi): err.append(f"items/cosmetics.csv {r['item_id']}: {r['name']} {r['color_hex']} hue {h:.0f} is not {w} ({lo}-{hi})")
        if w in HUE and s <= 0.12: err.append(f"items/cosmetics.csv {r['item_id']}: {r['name']} {r['color_hex']} is grey, not {w}")
        if w in LIGHT and not LIGHT[w][0] <= l <= LIGHT[w][1]: err.append(f"items/cosmetics.csv {r['item_id']}: {r['name']} {r['color_hex']} lightness {l:.2f} is not {w}")
def _lab(hx):
    c=[int(hx[k:k+2],16)/255 for k in (1,3,5)]; c=[((v+0.055)/1.055)**2.4 if v>0.04045 else v/12.92 for v in c]
    x=(0.4124*c[0]+0.3576*c[1]+0.1805*c[2])/0.95047; y=0.2126*c[0]+0.7152*c[1]+0.0722*c[2]; z=(0.0193*c[0]+0.1192*c[1]+0.9505*c[2])/1.08883
    f=lambda t: t**(1/3) if t>0.008856 else 7.787*t+16/116
    return 116*f(y)-16, 500*(f(x)-f(y)), 200*(f(y)-f(z))
RESERVED={'Health red':'#D4483F','Ward blue':'#4F8FE6','Breath green':'#7CC46A','Lens cyan':'#8FE3EE','Ember amber':'#E8873A','Signal red':'#FF3B30'}  # Visual Bible gameplay colors
RESERVED_MIN_DE=20
def _de(a,b): return sum((p-q)**2 for p,q in zip(_lab(a),_lab(b)))**0.5
for r in rows('items/cosmetics.csv'):
    if r['kind'] == 'Dye' and r['color_hex'].startswith('#'):
        for n, c in RESERVED.items():
            if _de(r['color_hex'], c) < RESERVED_MIN_DE: err.append(f"items/cosmetics.csv {r['item_id']}: {r['name']} {r['color_hex']} is within {_de(r['color_hex'], c):.0f} (CIE76) of reserved {n} {c}; minimum {RESERVED_MIN_DE}")
prev = {}
for r in rows('actors/enemy_stats_by_level.csv'):   # DR-SYS-010 rev 2: enemy HP must rise at every level
    a, L, hp = r['ACT_ID'], int(r['Level']), int(r['HP'])
    if a in prev and L == prev[a][0] + 1 and hp <= prev[a][1]: err.append(f'actors/enemy_stats_by_level.csv {a}: HP {hp} at level {L} does not rise above {prev[a][1]}')
    prev[a] = (L, hp)
c = collections.Counter(e.split(' ')[0] for e in err)
print(f'validate: {len(T)} tables, {len(defined)} ids, {refs} references, {len(err)} errors')
for e in (err if '--all' in sys.argv else err[:40]): print('  ' + e)
if err: print('  by file:', dict(c.most_common(10)))
sys.exit(1 if err else 0)
