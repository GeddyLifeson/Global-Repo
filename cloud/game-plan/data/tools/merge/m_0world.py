"""World and level design requests (design/world, design/levels/*). Runs first (the zero sorts it first) because it rebuilds
data/world/locations.csv from design/world/locations.csv (WREQ_01), which every later module's LOC_ references resolve against.
Design wins on place names and LOC_ IDs. A level request that adds a location is applied only when design/world/locations.csv
already holds that ID with matching values; otherwise it is a conflict and the world file wins. Everything is read at build time,
so the module follows the design file as the world thread changes it."""
import csv, os, re, math

FILES = ['world/data-requests.csv'] + [f'levels/{r}/data-requests.csv' for r in
         ('cinderreach', 'glasswaste', 'hollowdeep', 'multiplayer', 'orbital-ring', 'rimefall', 'saltmere', 'thornwood', 'undervault')]

TOK = re.compile(r'(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![a-z0-9])')
AP = ('MESH', 'VFX', 'SFX', 'ANIM', 'UI', 'ARENA')          # link.py registers these hooks from every table after the merge
RUNTIME_OK = {'ITM', 'ACT', 'PRK', 'VAR', 'BTN', 'SKL', 'ATTR', 'ELEM', 'STATUS', 'FAC', 'CMP', 'REGION'}
STALE = ['Ashfall Reach', 'Region 2', 'Region 3', 'Region 4', 'Region 5', 'Region 6', 'Seals Quartermaster', 'TXT_', 'Lanterns', 'Hardcore']  # bible: ok
# 'Lanterns' means the removed currency; these two place names (design/world/locations.csv) are allowed
NOT_STALE = ('Stilt Lanterns', 'Abbot Lanterns')
def unstale(c):
    for n in NOT_STALE: c = c.replace(n, '')
    return c

REGNAME = {}


def apply(T, ctx):
    D = ctx.DESIGN
    reqs = {f: ctx.design_rows(f) for f in FILES}
    done = set()

    def log(f, rid, status, target, reason):
        assert (f, rid) not in done, (f, rid)
        done.add((f, rid)); ctx.log(f, rid, status, target, reason)

    def rows(rel):
        with open(os.path.join(D, rel), newline='', encoding='utf-8') as fh: return list(csv.DictReader(fh))

    def have(rel): return os.path.exists(os.path.join(D, rel))
    REGNAME.update({r['reg_id']: r['name'] for r in ctx.rows('world/regions.csv')})

    # ------------------------------------------------------------ resolution helpers (mirror validate.py)
    def defined_set():
        d = set()
        for h, rr in T.values():
            d.update(TOK.findall(','.join(h)))
            d.update(r[0] for r in rr if r)
        p = set()
        for x in d:
            for n in range(1, x.count('_') + 1): p.add('_'.join(x.split('_')[:n]))
        return d, p
    DEF = {}

    def refresh(): DEF['d'], DEF['p'] = defined_set()

    def bad_tokens(c):
        out = []
        for m in TOK.finditer(c or ''):
            t, after = m.group(0), c[m.end():m.end() + 2]
            if after.startswith(('_*', '_<', '*')) or re.match(r'_[a-z]', after):
                if t not in DEF['d'] and t not in DEF['p']: out.append(t)
            elif t not in DEF['d'] and t.split('_')[0] not in AP: out.append(t)
        for m in re.finditer(r'\{([A-Z]+)_[a-z_]+\}', c or ''):
            if m.group(1) not in RUNTIME_OK: out.append(m.group(0))
        return out

    def stale(c): return [s for s in STALE if s in unstale(c or '')]

    def clean(c):
        """Drop the parts of a free-text cell that carry unresolved IDs or stale names: bracketed groups first, then
        semicolon parts; blank the cell if that is not enough. Returns (text, changed)."""
        if not bad_tokens(c) and not stale(c): return c, False
        x = c
        for pat in (r'\s*\([^()]*\)', r'\s*\[[^\[\]]*\]'):
            x = re.sub(pat, lambda m: '' if (bad_tokens(m.group(0)) or stale(m.group(0))) else m.group(0), x)
        if bad_tokens(x) or stale(x):
            x = '; '.join(p for p in x.split('; ') if not bad_tokens(p) and not stale(p))
        x = re.sub(r'\s+([.,;])', r'\1', re.sub(r'\s{2,}', ' ', x)).strip(' ;,')
        if bad_tokens(x) or stale(x): x = ''
        return x, True

    def rt_norm(t):  # data convention for runtime tokens is {PFX_lowercase}
        return re.sub(r'\{([A-Z]+)_([A-Z0-9_]+)\}', lambda m: '{%s_%s}' % (m.group(1), m.group(2).lower()) if m.group(1) in RUNTIME_OK else m.group(0), t)

    # ------------------------------------------------------------ WREQ_01: locations from design/world/locations.csv
    W = 'world/data-requests.csv'
    G_all = rows('world/locations.csv')
    G = [r for r in G_all if re.fullmatch(r'LOC_[A-Z0-9]+(?:_[A-Z0-9]+)*', r['loc_id'] or '')]   # template rows such as LOC_TOWN_REG_ are not IDs
    bad_ids = [r['loc_id'] for r in G_all if r not in G]
    GI = {r['loc_id']: r for r in G}
    gh = list(G[0].keys())
    old_h, old_rows = T['world/locations.csv']
    old = {r[0]: dict(zip(old_h, r)) for r in old_rows}
    kept = [k for k in old if k not in GI]
    newrows = []
    for r in G:
        newrows.append([r.get(c, '') or '' for c in gh])
    for k in kept:
        o = old[k]; newrows.append([o.get(c, '') for c in gh])
    T['world/locations.csv'] = [gh, newrows]
    LI = {r[0]: i for i, r in enumerate(newrows)}

    # lore_items.unlocks is the owner of which key opens which door (design gate column is one key off, see hollowdeep LREQ_06)
    unlocks = {}
    for r in ctx.rows('items/lore_items.csv'):
        if r['unlocks']: unlocks.setdefault(r['unlocks'], []).append(r['item_id'])
    gi = gh.index('gate'); ki = gh.index('kind'); gate_fix = 0
    for r in newrows:
        if r[ki] == 'Locked door' and r[0] in unlocks:
            g = 'Key ' + ' or '.join(unlocks[r[0]])
            if r[gi] != g: r[gi] = g; gate_fix += 1

    # Marlon: Arena PvP is 3v3 (6 players); multiplayer MPR-01 gives the 3v3 map sizes
    MP = 'levels/multiplayer/data-requests.csv'
    SIZES = {'01': '48 x 32', '02': '76 x 48', '03': '60 x 40', '04': '84 x 36', '05': '40 x 40', '06': '60 x 60'}
    ni = gh.index('notes'); arena_fix = 0
    for r in newrows:
        if r[ki] == 'Arena PvP 4v4':  # bible: ok
            r[ki] = 'Arena PvP 3v3'; arena_fix += 1
            n = r[0][-2:]
            if n in SIZES and not r[ni].endswith('6 players'):
                r[ni] = re.sub(r'\d+ x \d+ m$', SIZES[n] + ' m', r[ni]) + '; 3v3, 6 players'
    wardrobe = 0
    for r in newrows:
        if 'Lanterns cosmetics shop' in r[ni]:
            r[ni] = r[ni].replace('Lanterns cosmetics shop', 'Cosmetics shop, priced in USD (items/cosmetics.csv)'); wardrobe += 1

    # ------------------------------------------------------------ new ID-bearing rows from other requests (before cleaning)
    # NPCs ----------------------------------------------------------------
    NPC = 'world/npcs.csv'
    place = {r['act_id']: r for r in rows('world/npc_placement.csv')}
    nh = T[NPC][0]
    for c in ('home_loc', 'schedule'):
        if c not in nh: ctx.edit(NPC, '__none__', c, '')
    home_set = 0
    for r in T[NPC][1]:
        p = place.get(r[0])
        if p:
            h = T[NPC][0]
            if r[h.index('home_loc')] != p['home_loc'] or r[h.index('schedule')] != p['schedule']:
                r[h.index('home_loc')] = p['home_loc']; r[h.index('schedule')] = p['schedule']; home_set += 1
    npc_added = {}

    def add_npc(aid, name, role, fac, loc):
        sid = f'STR_{aid}_NAME'
        ok = ctx.append(NPC, dict(act_id=aid, name=name, role=role, fac_id=fac, location=loc, vendor_id='', str_id=sid, home_loc=loc, schedule=''))
        ctx.string(sid, name, 'Data name', 'NPC name (design/levels merge)')
        npc_added[aid] = ok
        return ok

    # Items ---------------------------------------------------------------
    def add_item(iid, name, cat, effect, desc=None, note=''):
        ok = ctx.append('items/consumables.csv', dict(item_id=iid, name=name, category=cat, effect=effect, magnitude='', duration_s='', max_stack='1',
                                                      buy_price='0', sell_price='0', weight='0', use_time_s='', craft_recipe='', icon='', vfx='', sfx=''))
        ctx.append('items/items_index.csv', dict(item_id=iid, name=name, category='Consumable', rarity='', file='consumables.csv'))
        ctx.string(f'STR_{iid}_NAME', name, 'Item name', cat)
        if desc: ctx.string(f'STR_{iid}_DESC', desc, 'Item description', note or cat)
        return ok

    # ------------------------------------------------------------ level node and placement import (DRQ_L05_06, DR-SAL-03, LREQ_04_01)
    LV = os.path.join(D, 'levels')
    REGION_OF = {'hollowdeep': 'REG_06', 'rimefall': 'REG_05', 'saltmere': 'REG_02', 'thornwood': 'REG_03', 'glasswaste': 'REG_04'}
    thn_loc = {r['lvl_id']: r['loc_id'] for r in rows('levels/thornwood/levels.csv')} if have('levels/thornwood/levels.csv') else {}
    nodes = []   # dicts
    def nadd(node_id, reg, loc, seq, name, role, crit, exits, src):
        nodes.append(dict(node_id=node_id, region=reg, loc_id=loc, seq=seq, name=name, role=role, critical=crit, exits=exits, source=src))
    if have('levels/hollowdeep/level_nodes.csv'):
        for r in rows('levels/hollowdeep/level_nodes.csv'):
            nadd(r['node_id'], 'REG_06', r['loc_id'], r['seq'], r['name'], r['function'], r['critical'], '', 'levels/hollowdeep/level_nodes.csv')
    if have('levels/rimefall/level_nodes.csv'):
        for r in rows('levels/rimefall/level_nodes.csv'):
            nadd(r['node_id'], 'REG_05', r['level_id'], r['order'], r['name'], r['node_type'], r['critical_path'], ' '.join(TOK.findall(r['links'])), 'levels/rimefall/level_nodes.csv')
    if have('levels/saltmere/level_nodes.csv'):
        for r in rows('levels/saltmere/level_nodes.csv'):
            nadd(r['node_id'], 'REG_02', r['loc_id'], r['order'], r['name'], r['role'], '', '', 'levels/saltmere/level_nodes.csv')
    if have('levels/thornwood/level_nodes.csv'):
        for r in rows('levels/thornwood/level_nodes.csv'):
            nadd(r['node_id'], 'REG_03', thn_loc.get(r['lvl_id'], ''), r['seq'], r['name'], r['role'] or r['room_type'], r['crit'], ' '.join(TOK.findall(r['exits'])), 'levels/thornwood/level_nodes.csv')
    gw_rooms = 0
    if have('levels/glasswaste/rooms.csv'):
        ex = {}
        for e in rows('levels/glasswaste/edges.csv') if have('levels/glasswaste/edges.csv') else []:
            ex.setdefault(e['from_room'], []).append(e['to_room'])
        for r in rows('levels/glasswaste/rooms.csv'):
            nadd(r['room_id'], 'REG_04', r['level'], r['order'], r['name'], r['role'], r['critical_path'], ' '.join(ex.get(r['room_id'], [])), 'levels/glasswaste/rooms.csv + edges.csv')
            gw_rooms += 1
    seen = set(); dup = 0; nodes_u = []
    for n in nodes:
        if n['node_id'] in seen: dup += 1; continue
        seen.add(n['node_id']); nodes_u.append(n)
    if nodes_u:
        T['world/level_nodes.csv'] = [list(nodes_u[0].keys()), []]
        for n in nodes_u: ctx.append('world/level_nodes.csv', n)

    plc = []
    def padd(pid, kind, reg, loc, node, ref, qty, what, src):
        plc.append(dict(place_id=pid, kind=kind, region=reg, loc_id=loc, node_id=node, ref=ref, qty=qty, container_or_trigger=what, source=src))
    for reg, f, idc, locc, refc, qtyc, whatc in [
            ('hollowdeep', 'level_loot', 'lot_id', 'loc_id', 'item_or_table', 'qty', 'container'),
            ('rimefall', 'level_loot', 'loot_id', 'level_id', 'item', 'qty', 'container'),
            ('saltmere', 'level_loot', 'loot_id', 'loc_id', 'item', 'qty', 'container'),
            ('thornwood', 'level_loot', 'loot_id', 'lvl_id', 'item_ref', 'qty', 'container'),
            ('hollowdeep', 'level_encounters', 'place_id', 'loc_id', 'actors', 'actor_count', 'trigger'),
            ('rimefall', 'level_encounters', 'enc_id', 'level_id', 'actors', 'total', 'trigger'),
            ('saltmere', 'level_encounters', 'lenc_id', 'loc_id', 'actors', 'enemy_count', 'trigger'),
            ('thornwood', 'level_encounters', 'lenc_id', 'lvl_id', 'actors', 'enemy_count', 'trigger')]:
        rel = f'levels/{reg}/{f}.csv'
        if not have(rel): continue
        for r in rows(rel):
            loc = thn_loc.get(r[locc], '') if reg == 'thornwood' else r[locc]
            padd(r[idc], 'Loot' if 'loot' in f else 'Encounter', REGION_OF[reg], loc, r['node_id'], r[refc], r[qtyc], r[whatc], rel)

    # gravity zones and traversal verbs (ORB_13)
    ORB = 'levels/orbital-ring/data-requests.csv'
    for rel, key in (('levels/orbital-ring/gravity_zones.csv', 'world/gravity_zones.csv'), ('levels/orbital-ring/traversal_verbs.csv', 'world/traversal_verbs.csv')):
        if have(rel):
            rr = rows(rel)
            T[key] = [list(rr[0].keys()), []]          # this module owns the table: rebuilt on every build
            for r in rr: ctx.append(key, r)

    # buffs table (DRQ_L05_07)
    RIM = 'levels/rimefall/data-requests.csv'
    T['actors/buffs.csv'] = [['BUF_ID', 'Effect', 'Duration s', 'Source', 'Notes'], []]   # owned here, rebuilt every build
    buf_ok = ctx.append('actors/buffs.csv', {'BUF_ID': 'BUF_WAYSHRINE_FROST', 'Effect': 'Frost resistance +10%', 'Duration s': '600',
                                             'Source': 'Praying at a wayshrine POI', 'Notes': 'One wayshrine buff per region element (design/levels/rimefall)'})

    # ------------------------------------------------------------ per-request work that adds IDs
    CDR = 'levels/cinderreach/data-requests.csv'; HOL = 'levels/hollowdeep/data-requests.csv'; SAL = 'levels/saltmere/data-requests.csv'
    UV = 'levels/undervault/data-requests.csv'; THN = 'levels/thornwood/data-requests.csv'; GLS = 'levels/glasswaste/data-requests.csv'
    add_npc('ACT_NPC_PYREWARDEN', 'Pyrewarden', 'Quest combatant (Hull Knights squad, Emberwatch)', 'FAC_HULLKNIGHTS', 'LOC_TOWN_REG_01_01')
    add_npc('ACT_NPC_REEVE_ANNIK', 'Reeve Annik', 'Quest NPC: Emberwatch headwoman', '', 'LOC_TOWN_REG_01_01')
    add_npc('ACT_NPC_SMITH_REG_01', 'Smith', 'Vendor (smith)', '', 'LOC_TOWN_REG_01_01')
    add_npc('ACT_NPC_SALVAGER_REG_01', 'Salvage vendor', 'Vendor (salvage)', 'FAC_SALVAGERS', 'LOC_TOWN_REG_01_02')
    add_npc('ACT_NPC_HERMIT_REG_01', 'Hermit', 'Radiant job giver (two huts)', '', 'LOC_POI_REG_01_08; LOC_POI_REG_01_22')
    add_npc('ACT_NPC_VEN_SMITH_REG_06', 'Smith', 'Vendor (smith): region upgrade materials', '', 'LOC_TOWN_REG_06_01')
    add_npc('ACT_NPC_HARBOR_MOSS', 'Harbormaster Moss', 'Quest NPC: Stiltmarket leader', '', 'LOC_TOWN_REG_02_01')
    add_item('ITM_QST_SIGNALCODES', "Corsa's Signal Codes", 'Quest item', 'Quest item (MQ_A1_07 reward); cannot be sold')
    orb_str = {r['str_id']: r['en'] for r in rows('levels/orbital-ring/strings.csv')} if have('levels/orbital-ring/strings.csv') else {}
    add_item('ITM_CON_KEY_ORB_SIGIL', orb_str.get('STR_ITM_ORB_SIGIL_NAME', 'Maker Sigil'), 'Key item', 'Opens the Granary Gate (REG_Q); cannot be sold',
             orb_str.get('STR_ITM_ORB_SIGIL_DESC'), 'Key item (orbital ring)')
    for iid, nm in (('ITM_KEY_UV_ODOMAP', "Brother Odo's map"), ('ITM_KEY_UV_OSTRAMEMORY', "Ostra's cut memory Shard"), ('ITM_KEY_UV_OVERRIDE', "Captain's override key")):
        add_item(iid, nm, 'Key item', 'Quest and secret gate key (Undervault); cannot be sold')

    # ------------------------------------------------------------ clean every new or rebuilt table
    refresh()
    loc_clean = loc_name_fallback = 0
    nmi = gh.index('name')
    for r in newrows:
        for j in range(1, len(gh)):
            c2, ch = clean(r[j])
            if ch:
                if j == nmi and not c2:
                    c2 = f"{r[ki]}, {REGNAME.get(r[gh.index('region')], r[gh.index('region')])}"; loc_name_fallback += 1
                r[j] = c2; loc_clean += 1
    refresh()
    # nodes: blank loc or exits that do not resolve
    node_fix = 0
    if 'world/level_nodes.csv' in T:
        h = T['world/level_nodes.csv'][0]
        for r in T['world/level_nodes.csv'][1]:
            for j in range(1, len(h)):
                if h[j] == 'exits':
                    keep = [x for x in r[j].split() if not bad_tokens(x)]
                    if len(keep) != len(r[j].split()): node_fix += 1
                    r[j] = ' '.join(keep)
                else:
                    c2, ch = clean(r[j]); node_fix += ch; r[j] = c2
    refresh()
    plc_kept = plc_drop = 0; drop_why = {}
    T['world/level_placements.csv'] = [list(plc[0].keys()) if plc else ['place_id'], []]
    pseen = set()
    for p in plc:
        if p['place_id'] in pseen: plc_drop += 1; drop_why['duplicate id'] = drop_why.get('duplicate id', 0) + 1; continue
        pseen.add(p['place_id'])
        if bad_tokens(p['node_id']): p['node_id'] = ''
        p['container_or_trigger'], _ = clean(p['container_or_trigger'])
        b = bad_tokens(p['loc_id']) or bad_tokens(p['ref']) or stale(p['ref'])
        if b:   # open-world rows (thornwood LVL_THN_WORLD) keep a blank loc_id
            plc_drop += 1
            for t in b: drop_why[t] = drop_why.get(t, 0) + 1
            continue
        ctx.append('world/level_placements.csv', p); plc_kept += 1
    for key in ('world/gravity_zones.csv', 'world/traversal_verbs.csv'):
        if key in T:
            for r in T[key][1]:
                for j in range(1, len(r)): r[j] = clean(r[j])[0]
    for r in T[NPC][1]:
        for j in range(1, len(r)): r[j] = clean(r[j])[0]
    for k in ('items/consumables.csv',):
        for r in T[k][1]:
            if r[0] in ('ITM_QST_SIGNALCODES', 'ITM_CON_KEY_ORB_SIGIL') or r[0].startswith('ITM_KEY_UV_'):
                for j in range(1, len(r)): r[j] = clean(r[j])[0]
    refresh()
    LOCS = {r[0]: dict(zip(gh, r)) for r in T['world/locations.csv'][1]}

    # ------------------------------------------------------------ helpers for logging location requests
    def loc_req(f, rid, ids, specs=None, target='data/world/locations.csv', extra=''):
        miss = [i for i in ids if i not in GI]
        dis = []
        for i, sp in (specs or {}).items():
            if i not in GI: continue
            for c, v in sp.items():
                got = GI[i].get(c, '')
                try: same = abs(float(got) - float(v)) < 0.51
                except ValueError: same = got.strip().lower() == str(v).strip().lower()
                if not same: dis.append(f'{i} {c} {got!r} (asked {v!r})')
        if miss or dis:
            bits = []
            if miss: bits.append(f"{len(miss)} of {len(ids)} IDs are not in design/world/locations.csv ({', '.join(miss[:6])}{' ...' if len(miss) > 6 else ''})")
            if dis: bits.append('design disagrees on ' + '; '.join(dis[:4]))
            log(f, rid, 'conflict', target, 'World wins: ' + ' and '.join(bits) + '; data follows design/world/locations.csv.' + extra)
        else:
            log(f, rid, 'applied', target, f'All {len(ids)} requested locations are in design/world/locations.csv with matching values, so WREQ_01 copies them into data.' + extra)

    def add_hooks(f, rid, toks, extra=''):
        toks = sorted(set(toks))
        hooks = [t for t in toks if t.split('_')[0] in AP]
        other = [t for t in toks if t.split('_')[0] not in AP]
        used = {m for k, (h, rr) in T.items() if k != 'assets/asset_hooks.csv' for r in rr for c in r for m in TOK.findall(c)}
        new = 0
        for t in hooks:
            ctx.append('assets/asset_hooks.csv', dict(hook=t, kind=t.split('_')[0], first_used_in='design request', first_row=t, uses='0'))
            if t not in used: new += 1
        note = f' {len(other)} non-hook IDs ({", ".join(other[:4])}{" ..." if len(other) > 4 else ""}) are outside data/: owned by the audio/asset threads.' if other else ''
        if not hooks:
            log(f, rid, 'skipped', 'data/assets/asset_hooks.csv', 'outside data/: owned by the audio/asset threads; none of these IDs is an asset-hook prefix.' + extra); return
        if new == 0:
            log(f, rid, 'skipped', 'data/assets/asset_hooks.csv', f'already applied: all {len(hooks)} hooks are already used by data tables.' + note + extra); return
        log(f, rid, 'applied', 'data/assets/asset_hooks.csv', f'{new} hooks registered in asset_hooks.csv ({len(hooks) - new} already used by data tables).' + note + extra)

    def merge_strings(f, rid, pairs, target='data/ui/strings_data.csv', screen='Design merge', extra='', partial=None):
        add = pres = clash = bad = 0
        for sid, text, note in pairs:
            text = rt_norm(text); note = clean(note or '')[0]
            if bad_tokens(text) or stale(text): bad += 1; continue
            S = {r[0]: r[2] for k in ('ui/strings.csv', 'ui/strings_data.csv') for r in T[k][1]}
            if sid in S:
                if S[sid] == text: pres += 1
                else: clash += 1
                continue
            if ctx.string(sid, text, screen, note): add += 1
        msg = f'{add} strings added, {pres} already present'
        if clash: msg += f', {clash} kept existing text'
        if bad: msg += f', {bad} skipped (unresolved IDs in text)'
        msg += '.' + extra
        status = 'conflict' if (clash or bad or partial) else ('applied' if add else 'skipped')
        if status == 'skipped': msg = 'already applied: ' + msg
        log(f, rid, status, target, msg + (partial or ''))

    def loc_name_pairs(pairs):
        """STR_LOC_<id>_NAME: design names win. Text that matches the design name (case-insensitive, or one contains the other) is kept."""
        out, clash = [], 0
        for sid, text, note in pairs:
            if sid.startswith('STR_LOC_') and sid.endswith('_NAME') and sid[4:-5] in LOCS:
                dn = LOCS[sid[4:-5]]['name']
                a, b = dn.lower(), text.lower()
                if a and not (a == b or a in b or b in a):
                    out.append((sid, dn, note + '; design name (level text was ' + text + ')')); clash += 1; continue
            out.append((sid, text, note))
        return out, clash

    # ============================================================ world/data-requests.csv
    for r in reqs[W]:
        rid = r['req_id']
        if rid == 'WREQ_01':
            msg = f"locations.csv rebuilt from design/world/locations.csv: {len(G)} design rows, columns {' '.join(gh[4:])}; {len(kept)} data-only IDs kept"
            if bad_ids: msg += f"; {len(bad_ids)} design rows left out because their loc_id is not a valid ID ({', '.join(repr(b) for b in bad_ids[:3])})"
            if gate_fix: msg += f'; {gate_fix} locked-door gates set from items/lore_items.csv unlocks'
            if arena_fix: msg += f'; {arena_fix} arenas written as Arena PvP 3v3'
            if loc_clean: msg += f'; {loc_clean} cells trimmed of IDs that do not resolve in data or stale names ({loc_name_fallback} names fell back to kind and region)'
            log(W, rid, 'applied', 'data/world/locations.csv', msg + '.')
        elif rid == 'WREQ_02':
            kinds = {x[ki] for x in newrows}
            log(W, rid, 'conflict', 'data/world/locations.csv', f'The new kinds arrive with WREQ_01 ({len(kinds)} kinds in data now), except the old larger arena kind: it lost to multiplayer MPR-01 (Marlon chose 3v3, 6 players), so arenas are Arena PvP 3v3.')
        elif rid == 'WREQ_03':
            add = 0
            for sid, nm, base, unit in [('STAT_JUMP', 'Jump height', '1.1', 'm'), ('STAT_MANTLE', 'Mantle height', '2.0', 'm'), ('STAT_SAFEFALL', 'Safe fall height', '6', 'm'),
                                        ('STAT_LETHALFALL', 'Lethal fall height', '18', 'm'), ('STAT_SWIMSPEED', 'Swim speed', '2.5', 'm/s')]:
                add += ctx.append('actors/player_base_stats.csv', {'STAT_ID': sid, 'Stat': nm, 'Base': base, 'Per Vigor point': '0', 'Per attribute point': '0', 'Attribute': '-',
                                                                    'Cap': base, 'Regen / rule': 'Level metrics depend on it (design/world/traversal.csv)', 'Notes': unit})
            log(W, rid, 'conflict', 'data/actors/player_base_stats.csv', f'{add} stats added (jump, mantle, safe fall, lethal fall, swim); STAT_SPRINTSPEED 7.5 m/s not added: STAT_MOVESPEED already sets sprint 7.0 m/s and the actors table wins.')
        elif rid == 'WREQ_04':
            n = ctx.edit('actors/creatures.csv', 'ACT_CRT_STRIDER', 'Mount (tamed)', 'Gallop 14 m/s; double jump 6 m; glide ratio 4:1')
            log(W, rid, 'applied' if n else 'conflict', 'data/actors/creatures.csv', 'Mount (tamed) column set on ACT_CRT_STRIDER: gallop 14 m/s, double jump 6 m, glide 4:1.' if n else 'ACT_CRT_STRIDER is missing from creatures.csv.')
        elif rid == 'WREQ_05':
            log(W, rid, 'conflict', 'data/world/vehicles.csv', 'Speeds 32/18/40 m/s disagree with design/systems/vehicles.csv (118/82/160 km/h); the systems table owns vehicles and wins (systems DR-SYS-005 creates the table).')
        elif rid == 'WREQ_06':
            sec = rows('world/secrets.csv'); n = 0
            for iid in ('ITM_CON_TNC_SEED', 'ITM_CON_TNC_DISTIL'):
                ls = [s['loc_id'] for s in sec if s['reward'].strip() == iid and s['loc_id'] in LOCS]
                n += ctx.edit('items/consumables.csv', iid, 'locations', ' '.join(ls))
            log(W, rid, 'applied', 'data/items/consumables.csv', 'locations column set on Tonic Seed and Tonic Distillation from design/world/secrets.csv (8 secrets each).')
        elif rid == 'WREQ_07':
            log(W, rid, 'skipped', 'data/items/lore_items.csv', 'already applied: every lore item location is a LOC_SITE_* and WREQ_01 brings each site\'s parent_loc.')
        elif rid == 'WREQ_08':
            items = ctx.ids('items/items_index.csv'); n = miss = 0
            for s in rows('world/sites.csv'):
                u = s['unique_reward'].strip()
                if u in items: n += ctx.edit('items/items_index.csv', u, 'source_loc', s['loc_id'])
                elif u: miss += 1
            log(W, rid, 'applied' if not miss else 'conflict', 'data/items/items_index.csv', f'source_loc set on {n} unique site rewards from design/world/sites.csv' + (f'; {miss} rewards are not data items.' if miss else '.'))
        elif rid == 'WREQ_09':
            log(W, rid, 'conflict', 'data/actors/bosses.csv', 'Lost to multiplayer MPR-11 and orbital-ring ORB_15: ACT_BOSS_QUIETCORE stays the raid Wing 1 boss (LOC_END_RAID_01, level 80); the campaign final boss is ACT_BOSS_HUSH (campaign thread).')
        elif rid == 'WREQ_10':
            log(W, rid, 'applied' if home_set else 'skipped', 'data/world/npcs.csv', (f'home_loc and schedule set on {home_set} NPCs from design/world/npc_placement.csv.' if home_set else 'already applied: home_loc matches npc_placement.csv.'))
        elif rid == 'WREQ_11':
            log(W, rid, 'skipped', 'data/world/quests.csv', 'Note for the campaign thread: design/world names no quest-to-location map; quests.csv has a location column for the quests levels placed (saltmere DR-SAL-02).')
        elif rid == 'WREQ_12':
            log(W, rid, 'skipped', 'data/assets/asset_hooks.csv', 'outside data/: owned by the asset thread (shardfall-assets.xlsx); KIT_ is not an asset-hook prefix, so asset_hooks.csv cannot carry it.')
        elif rid == 'WREQ_13':
            b = {x['reg_id']: f"{x['level_min']}-{x['level_max']}" for x in ctx.rows('world/regions.csv')}
            ok = [b.get(k) for k in ('REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06')] == ['10-22', '20-34', '32-46', '44-58', '55-70']
            log(W, rid, 'skipped' if ok else 'conflict', 'data/world/regions.csv', 'already applied: regions.csv keeps the data bands.' if ok else 'regions.csv bands differ from the note.')
        elif r['target'].startswith('design/'):
            extra = ''
            if 'locked door' in r['field'].lower(): extra = ' Data already takes locked-door keys from items/lore_items.csv unlocks (WREQ_01).'
            if 'arena' in r['field'].lower(): extra = f' Data already writes the arenas as Arena PvP 3v3, 6 players ({arena_fix} rows set this build).'
            log(W, rid, 'skipped', r['target'], 'outside data/: owned by design/world (world thread continuity record).' + extra)
        else:
            log(W, rid, 'skipped', r['target'], 'Not handled: this row was added after the m_0world module was written; nothing applied.')

    # ============================================================ cinderreach
    for r in reqs[CDR]:
        rid, tgt = r['req_id'], r['target']
        if tgt.startswith('design/audio'): log(CDR, rid, 'skipped', tgt, 'outside data/: owned by design/audio.')
        elif tgt.startswith('design/art'): log(CDR, rid, 'skipped', tgt, 'outside data/: owned by design/art.')
        elif 'asset_hooks' in tgt: add_hooks(CDR, rid, TOK.findall(r['value']))
        elif tgt == 'data/world/locations.csv':
            loc_req(CDR, rid, [r['value']], {r['value']: {'parent_loc': 'LOC_LMK_REG_01_01'}})
        elif r['value'] == 'ACT_NPC_TOMAS':
            log(CDR, rid, 'conflict', 'data/world/npcs.csv', 'Old Tomas is ACT_NPC_WARDEN_TOMAS in the campaign cast (design/campaign/02-characters.md); the campaign ID wins, so ACT_NPC_TOMAS is not added.')
        elif r['field'] == 'actor':
            aid = r['value']
            log(CDR, rid, 'applied' if npc_added.get(aid) else 'skipped', 'data/world/npcs.csv',
                (f'{aid} added to world/npcs.csv with a home location and name string.' if npc_added.get(aid) else f'already applied: {aid} is in world/npcs.csv.'))
        elif tgt == 'data/items/lore_items.csv':
            log(CDR, rid, 'conflict', 'data/items/lore_items.csv', 'Missing content: the request names level spots (LVL_ ids, not data IDs) but no lore item names or text, and lore_items needs a text string; the writing thread owns lore text.')
        elif r['field'] == 'placed_at':
            lv = {x['lvl_id']: x['loc_id'] for x in rows('levels/cinderreach/levels.csv')}
            items = {x['item_id']: x for x in ctx.rows('items/items_index.csv')}
            n = 0; setp = {k for k, v in items.items() if v.get('placed_at')}
            for x in rows('levels/cinderreach/loot.csv'):
                it = x['contents'].strip(); loc = lv.get(x['lvl_id'], '')
                if it in items and it.startswith(('ITM_WPN_', 'ITM_CAT_', 'ITM_ARM_')) and loc in LOCS and it not in setp:
                    setp.add(it); n += ctx.edit('items/items_index.csv', it, 'placed_at', loc) > 0
            log(CDR, rid, 'applied' if n else 'skipped', 'data/items/items_index.csv', f'placed_at set on {n} REG_01 weapons, catalysts and armor pieces from design/levels/cinderreach/loot.csv (level mapped to its LOC_).' if n else 'already applied.')
        elif tgt.startswith('design/world'):
            log(CDR, rid, 'skipped', tgt, 'outside data/: owned by design/world (world thread).')
        else:
            log(CDR, rid, 'skipped', tgt, 'not handled')

    # ============================================================ glasswaste
    for r in reqs[GLS]:
        rid, tgt = r['req_id'], r['target']
        if rid == 'LREQ_04_01':
            log(GLS, rid, 'applied', 'data/world/level_nodes.csv', f'{gw_rooms} Glasswaste rooms imported with exits from edges.csv into data/world/level_nodes.csv, the one node table for every region (the name rimefall DRQ_L05_06 asks for).')
        elif rid in ('LREQ_04_05', 'LREQ_04_06'):
            log(GLS, rid, 'skipped', tgt, 'outside data/: owned by design/world (world thread); its place names are frozen and data copies them.')
        elif rid == 'LREQ_04_07':
            log(GLS, rid, 'skipped', tgt, 'Note only: current key placement is kept; nothing to change.')
        elif tgt.startswith('shardfall-assets'):
            log(GLS, rid, 'skipped', tgt, 'outside data/: owned by the asset thread (shardfall-assets.xlsx).')
        else:
            owner = tgt.split(' ')[0].rsplit('/', 1)[0] if '/' in tgt else tgt
            log(GLS, rid, 'skipped', tgt, f'outside data/: owned by {owner}.')

    # ============================================================ hollowdeep
    for r in reqs[HOL]:
        rid, tgt = r['req_id'], r['target']
        if rid == 'LREQ_01':
            src = rows('levels/hollowdeep/level_strings.csv')
            pairs, cl = loc_name_pairs([(x['str_id'], x['text'], x['context']) for x in src])
            merge_strings(HOL, rid, pairs, extra=(f' {cl} area names use the design/world name.' if cl else ''))
        elif rid == 'LREQ_02':
            loc_req(HOL, rid, ['LOC_CQ_REG_06_LAMP_TOWER', 'LOC_CQ_REG_06_GLASS_RIVER', 'LOC_CQ_REG_06_LASTLIGHT_HOSPICE', 'LOC_CQ_REG_06_CLOCK_PRIORY_ROOF'],
                    {'LOC_CQ_REG_06_LAMP_TOWER': {'x_m': 9700, 'y_m': 2190, 'level': 69}, 'LOC_CQ_REG_06_GLASS_RIVER': {'x_m': 8240, 'y_m': 1640, 'level': 58},
                     'LOC_CQ_REG_06_LASTLIGHT_HOSPICE': {'parent_loc': 'LOC_TOWN_REG_06_01'}, 'LOC_CQ_REG_06_CLOCK_PRIORY_ROOF': {'parent_loc': 'LOC_DGN_REG_06_03'}})
        elif rid == 'LREQ_03':
            a = 'ACT_NPC_VEN_SMITH_REG_06'
            log(HOL, rid, 'applied' if npc_added.get(a) else 'skipped', 'data/world/npcs.csv', f'{a} added (Smith, home LOC_TOWN_REG_06_01); no stock list was given, so items/vendors.csv has no rows for it.' if npc_added.get(a) else f'already applied: {a} is in world/npcs.csv.')
        elif rid == 'LREQ_04':
            log(HOL, rid, 'conflict', 'data/items/lore_items.csv', 'Missing content: names and places are given but no lore text (lore_items needs a text string; the writing thread owns lore text), and the request puts the ledger in Z5 while level_loot.csv puts it in Z3.')
        elif rid == 'LREQ_06':
            log(HOL, rid, 'skipped', tgt, 'outside data/: owned by design/world; data/world/locations.csv already takes locked-door keys from lore_items.csv unlocks (WREQ_01).')
        elif rid == 'LREQ_07':
            n = sum(1 for p in T['world/level_placements.csv'][1] if p[0].startswith('LEP_'))
            log(HOL, rid, 'applied', 'data/world/level_placements.csv', f'{n} Hollowdeep level encounters imported into data/world/level_placements.csv (saltmere DR-SAL-03 table).')
        elif rid == 'LREQ_08':
            add_hooks(HOL, rid, TOK.findall(r['value']), extra=' The Play_SFX_ events belong to design/audio/event_map.csv (outside data/).')
        else:
            log(HOL, rid, 'skipped', tgt, 'not handled')

    # ============================================================ multiplayer
    for r in reqs[MP]:
        rid, tgt = r['req_id'], r['target']
        if rid == 'MPR-01':
            log(MP, rid, 'applied', 'data/world/locations.csv', f'Data side applied: {arena_fix} arenas are Arena PvP 3v3 with 6 players and the 3v3 sizes; design/world/endgame_spaces.csv itself is owned by the world thread.')
        elif rid in ('MPR-02', 'MPR-03'):
            log(MP, rid, 'skipped', tgt, 'outside data/: owned by design/loops (loops thread).')
        elif rid == 'MPR-04':
            log(MP, rid, 'skipped', tgt, 'outside data/: owned by design/world (world thread); data copies the strike names and bosses from design/world/locations.csv.')
        elif rid == 'MPR-05':
            maps = [x['map_id'] for x in rows('levels/multiplayer/mp_maps.csv') if x['map_id'].startswith(('LOC_MP_', 'ARENA_MP_'))]
            loc_req(MP, rid, maps, extra=' The world thread placed these spaces as LOC_END_STRIKE_*/LOC_END_ARENA_* with LOC_MP_* node rows, which data carries.')
        elif rid == 'MPR-06':
            ok = all(i in ctx.ids('actors/enemies.csv') for i in ('ACT_RAID_CONDUIT', 'ACT_RAID_INDEXWARDEN', 'ACT_RAID_GHOSTOFFICER', 'ACT_RAID_CHORISTER'))
            log(MP, rid, 'applied' if ok else 'conflict', 'data/actors/enemies.csv', 'Four raid add types added by actors/tools/gen_enemies.py (decided 2026-10-03; enemy cap is now 69). Their mechanic drops (Conduit charge, Reading Glass) stay in the raid design; data rows drop nothing.')
        elif rid == 'MPR-07':
            want = {'ACT_BOSS_QUIETCORE': 20, 'ACT_BOSS_ARCHIVIST': 27, 'ACT_BOSS_MERIDIANGHOST': 33, 'ACT_BOSS_UNMADECHOIR': 40}
            h = T['actors/bosses.csv'][0]; di = h.index('Drops (item refs)'); n = 0
            for b in T['actors/bosses.csv'][1]:
                if b[0] in want:
                    nv = re.sub(r'\d+ ITM_CUR_SEALS', f'{want[b[0]]} ITM_CUR_SEALS', b[di])
                    if nv != b[di]: b[di] = nv; n += 1
            log(MP, rid, 'applied' if n else 'skipped', 'data/actors/bosses.csv', f'Raid first-weekly-kill Seals set on {n} bosses: Quiet Core 20, Archivist 27, Meridian Ghost 33, Unmade Choir 40 (loops economy).' if n else 'already applied: raid Seals match.')
        elif rid == 'MPR-08':
            cues = [x['cue_id'] for x in rows('levels/multiplayer/mp_cues.csv')] if have('levels/multiplayer/mp_cues.csv') else []
            add_hooks(MP, rid, [c for c in cues if '_MP_' in c and TOK.fullmatch(c)])
        elif rid == 'MPR-09':
            log(MP, rid, 'skipped', tgt, 'outside data/: owned by design/audio (audio thread).')
        elif rid == 'MPR-10':
            src = rows('levels/multiplayer/mp_strings.csv')
            merge_strings(MP, rid, [(x['str_id'], x['en'], 'Multiplayer (design/levels/multiplayer)') for x in src], extra=' Runtime tokens written as {VAR_name} per data convention.')
        elif rid == 'MPR-11':
            log(MP, rid, 'skipped', tgt, 'outside data/: owned by design/campaign and orbital-ring; data/actors/bosses.csv already has ACT_BOSS_QUIETCORE as a level 80 raid boss.')
        elif rid == 'MPR-12':
            ok = {'COOP_OW_3', 'COOP_BOSS_3'} <= ctx.ids('actors/coop_scaling.csv')
            log(MP, rid, 'skipped', 'data/actors/coop_scaling.csv', 'Note only, no change asked: COOP_OW_3 and COOP_BOSS_3 already exist.' if ok else 'Note only; coop rows missing.')
        else:
            log(MP, rid, 'skipped', tgt, 'not handled')

    # ============================================================ orbital-ring
    for r in reqs[ORB]:
        rid, tgt = r['req_id'], r['target']
        if rid == 'ORB_01':
            loc_req(ORB, rid, ['LOC_ANC_REG_Q_00', 'LOC_ANC_REG_Q_08', 'LOC_ANC_REG_Q_09'],
                    {'LOC_ANC_REG_Q_00': {'x_m': 40, 'y_m': 250}, 'LOC_ANC_REG_Q_08': {'x_m': 1260, 'y_m': 250}, 'LOC_ANC_REG_Q_09': {'x_m': 2650, 'y_m': 250}})
        elif rid == 'ORB_02':
            nd = [x for x in rows('levels/orbital-ring/nodes.csv') if x['node_id'].startswith('ND_ORB_')]
            ids = ['LOC_Q_ORB_' + x['node_id'][7:] for x in nd]
            loc_req(ORB, rid, ids, {('LOC_Q_ORB_' + x['node_id'][7:]): {'x_m': x['x_m'], 'y_m': x['y_m'], 'z_m': x['z_m']} for x in nd})
        elif rid in ('ORB_03',):
            log(ORB, rid, 'skipped', tgt, 'outside data/: owned by design/world (world thread).')
        elif rid == 'ORB_04':
            if 'ACT_BOSS_HUSH' in ctx.ids('actors/bosses.csv'):
                ctx.edit('actors/bosses.csv', 'ACT_BOSS_HUSH', 'Arena', 'ARENA_HUSH_P1 (1.0 g); ARENA_HUSH_P2 (0.4 g floating islands); ARENA_HUSH_P3 (0 g mag platforms)')
                log(ORB, rid, 'applied', 'data/actors/bosses.csv', 'Arena column set on ACT_BOSS_HUSH with gravity per phase.')
            else:
                log(ORB, rid, 'conflict', 'data/actors/bosses.csv', 'Missing: ACT_BOSS_HUSH has no row when this module runs (the campaign module adds it last); the arena hooks ARENA_HUSH_P1..P3 are registered by ORB_11 and the gravity per phase is in world/gravity_zones.csv (GRV_CORE).')
        elif rid == 'ORB_05':
            log(ORB, rid, 'conflict', 'data/actors/bosses.csv', 'Needs an owner decision: bosses.csv has one row per boss at one level, and a scaled copy would be a boss outside the plan\'s 40; ARENA_IRES_RQ is registered by ORB_11.')
        elif rid == 'ORB_06':
            log(ORB, rid, 'skipped', 'data/actors/enemy_stats_by_level.csv', 'already applied: every base enemy has stats for levels 1 to 80 and regional variants scale from their base by HP ratio (data/README 27).')
        elif rid == 'ORB_07':
            ids = ['ACT_NPC_HULLKNIGHT_COMMANDER', 'ACT_NPC_LANTERN_ARCHIVIST', 'ACT_NPC_SALVAGER_BOSS', 'ACT_NPC_CHOIR_PRECENTOR', 'ACT_NPC_QUIETHAND_SPEAKER'] + [f'ACT_CMP_C{i}' for i in range(1, 9)]
            n = ctx.edit('actors/enemies.csv', 'ACT_CHOIRBORN_LEADER', 'Copy skins', ' '.join('MESH_COPY_' + i for i in ids))
            log(ORB, rid, 'applied' if n else 'conflict', 'data/actors/enemies.csv', f'Copy skins column on ACT_CHOIRBORN_LEADER: {len(ids)} MESH_COPY_ hooks for the five faction leaders and eight companions; the Meridian captain has no data ID, so no hook for it.')
        elif rid == 'ORB_08':
            log(ORB, rid, 'applied' if 'ITM_CON_KEY_ORB_SIGIL' in ctx.ids('items/consumables.csv') else 'conflict', 'data/items/consumables.csv',
                'ITM_CON_KEY_ORB_SIGIL Maker Sigil added (Key item, weight 0, sell 0) to consumables.csv and items_index.csv with name and description strings.')
        elif rid == 'ORB_09':
            src = rows('levels/orbital-ring/strings.csv')
            merge_strings(ORB, rid, [(x['str_id'], x['en'], 'Orbital ring (design/levels/orbital-ring)') for x in src], extra=' Runtime tokens written as {BTN_name} per data convention.')
        elif rid == 'ORB_10':
            cues = rows('levels/orbital-ring/cues.csv')
            when = {}
            for c in cues:
                for t in TOK.findall(c['note']):
                    when.setdefault(t, c['moment'])
            tmpl = {k: dict(zip(T['ui/popups.csv'][0], next(x for x in T['ui/popups.csv'][1] if x[0] == k))) for k in ('TUT_MOVE', 'BAN_REGION', 'PRM_GHOST_NEAR', 'INL_CANT_COMBAT', 'NTF_SKILL_UP')}
            pre = {'TUT': 'TUT_MOVE', 'BAN': 'BAN_REGION', 'PRM': 'PRM_GHOST_NEAR', 'INL': 'INL_CANT_COMBAT', 'NTF': 'NTF_SKILL_UP'}
            ids = TOK.findall(r['value'].replace('PRM_ORB_VALVE/TERMINAL/SOIL/TALKCOPY', 'PRM_ORB_VALVE PRM_ORB_TERMINAL PRM_ORB_SOIL PRM_ORB_TALKCOPY').replace('INL_ORB_TETHER/OUTOFREACH', 'INL_ORB_TETHER INL_ORB_OUTOFREACH'))
            secs = [(k, v) for k, v in orb_str.items() if k.startswith('STR_ORB_SEC_')]
            plan = [(i, 'STR_' + i, when.get(i, 'Orbital ring level cue (design/levels/orbital-ring/cues.csv)')) for i in ids if i.split('_')[0] in pre]
            plan += [('BAN_ORB_' + k[8:], k, f'First entry into {v}') for k, v in secs]
            S = {x[0] for k in ('ui/strings.csv', 'ui/strings_data.csv') for x in T[k][1]}
            add = pres = miss = 0
            for pid, sid, trig in plan:
                if sid not in S: miss += 1; continue
                d = dict(tmpl[pre[pid.split('_')[0]]]); d['popup_id'] = pid; d['trigger'] = trig
                if pid.startswith('TUT'): d['title_str'], d['body_str'] = '', sid
                else: d['title_str'], d['body_str'] = sid, ''
                if pid.startswith('TUT'): d['trigger'] = trig + '; once per profile'
                if ctx.append('ui/popups.csv', d): add += 1
                else: pres += 1
            log(ORB, rid, 'applied' if add and not miss else ('skipped' if not add and not miss else 'conflict'), 'data/ui/popups.csv',
                f'{add} popups added ({pres} already present{", " + str(miss) + " missing their string" if miss else ""}), including one banner per section name (BAN_ORB_SEC_00..06); layout, timing and sound copied from the matching existing popup kind.')
        elif rid == 'ORB_11':
            toks = []
            for rel, cols in (('levels/orbital-ring/cues.csv', ('audio', 'vfx', 'note')), ('levels/orbital-ring/traversal_verbs.csv', ('sfx', 'vfx'))):
                for x in rows(rel):
                    for c in cols:
                        v = x[c]
                        for m in re.finditer(r'((?:VFX|SFX)_ORB_[A-Z0-9_]+)((?:\s*/\s*_[A-Z0-9_]+)*)', v):
                            base = m.group(1); toks.append(base)
                            for suf in re.findall(r'_[A-Z0-9_]+', m.group(2)):
                                toks.append(base.rsplit('_', 1)[0] + suf)
            toks += ['ARENA_HUSH_P1', 'ARENA_HUSH_P2', 'ARENA_HUSH_P3', 'ARENA_IRES_RQ']
            add_hooks(ORB, rid, toks, extra=' MAT_HULL_MAGPLATE is a material, not an asset-hook prefix, so it stays with the asset thread.')
        elif rid == 'ORB_13':
            g = len(T.get('world/gravity_zones.csv', [[], []])[1]); t = len(T.get('world/traversal_verbs.csv', [[], []])[1])
            log(ORB, rid, 'applied', 'data/world/gravity_zones.csv', f'New tables world/gravity_zones.csv ({g} GRV_ rows) and world/traversal_verbs.csv ({t} ORB_TRV_ rows); bracketed notes that cite IDs not in data (MAT_, TRV_, MQ_) were dropped.')
        elif rid in ('ORB_12', 'ORB_14', 'ORB_15'):
            own = {'ORB_12': 'design/audio (audio thread)', 'ORB_14': 'design/systems', 'ORB_15': 'design/audit (owner decision); data keeps ACT_BOSS_QUIETCORE as raid Wing 1 only'}[rid]
            log(ORB, rid, 'skipped', tgt, f'outside data/: owned by {own}.')
        else:
            log(ORB, rid, 'skipped', tgt, 'not handled')

    # ============================================================ rimefall
    for r in reqs[RIM]:
        rid, tgt = r['req_id'], r['target']
        if rid == 'DRQ_L05_01':
            add_hooks(RIM, rid, TOK.findall(r['value']))
        elif rid == 'DRQ_L05_05':
            loc_req(RIM, rid, TOK.findall(r['value']))
        elif rid == 'DRQ_L05_06':
            nn = len(T.get('world/level_nodes.csv', [[], []])[1])
            log(RIM, rid, 'conflict', 'data/world/level_*.csv', f'Nodes imported as world/level_nodes.csv ({nn} rows, all regions); loot and encounters went into one world/level_placements.csv as saltmere DR-SAL-03 asks (that shape wins); level_cues not imported: their MUS_/AMB_/LGT_ cue IDs have no owner table in data.')
        elif rid == 'DRQ_L05_07':
            log(RIM, rid, 'applied' if buf_ok else 'skipped', 'data/actors/buffs.csv', 'New table actors/buffs.csv with BUF_WAYSHRINE_FROST: Frost resistance +10% for 600 s from praying at a wayshrine.' if buf_ok else 'already applied.')
        elif rid == 'DRQ_L05_10':
            log(RIM, rid, 'skipped', tgt, 'Note only for the loot thread; nothing to apply.')
        else:
            owner = re.sub(r'\s*\(.*', '', tgt)
            log(RIM, rid, 'skipped', tgt, f'outside data/: owned by {owner}.')

    # ============================================================ saltmere
    for r in reqs[SAL]:
        rid, tgt = r['req_id'], r['target']
        if rid == 'DR-SAL-01':
            log(SAL, rid, 'applied', 'data/items/consumables.csv', 'ITM_QST_SIGNALCODES Corsa\'s Signal Codes added (Quest item, weight 0, sell 0) with its name string; no description text was given, so no _DESC string.')
        elif rid == 'DR-SAL-02':
            want = {'QST_SHB_W14': 'LOC_LMK_REG_02_06', 'QST_SHB_A14': 'LOC_FB_SKIMMERACE', 'QST_SHB_A08': 'LOC_POI_REG_02_10'}
            n = 0; bad = []
            for q, l in want.items():
                if l in LOCS and q in ctx.ids('world/quests.csv'): n += ctx.edit('world/quests.csv', q, 'location', l)
                else: bad.append(q)
            if 'location' not in T['world/quests.csv'][0]: ctx.edit('world/quests.csv', '__none__', 'location', '')
            log(SAL, rid, 'applied' if not bad else 'conflict', 'data/world/quests.csv', f'location column added; {n} Saltmere exotic quests placed' + (f'; missing quest or location for {", ".join(bad)}.' if bad else '.'))
        elif rid == 'DR-SAL-03':
            top = sorted(drop_why.items(), key=lambda x: -x[1])[:4]
            log(SAL, rid, 'applied', 'data/world/level_placements.csv', f'New table world/level_placements.csv: {plc_kept} loot and encounter rows from the four regions with level_loot/level_encounters; {plc_drop} rows left out because a LOC_, item or actor ID is not in data'
                + (' (' + ', '.join(f'{k} x{v}' for k, v in top) + ')' if top else '') + '.')
        elif rid == 'DR-SAL-04':
            moss = npc_added.get('ACT_NPC_HARBOR_MOSS')
            log(SAL, rid, 'conflict', 'data/world/npcs.csv', ('ACT_NPC_HARBOR_MOSS added (home LOC_TOWN_REG_02_01)' if moss else 'ACT_NPC_HARBOR_MOSS already present') +
                f"; recruit spots for Hal Merrow and Sister Calla lose to design/world/npc_placement.csv ({place.get('ACT_CMP_C5', {}).get('home_loc')} and {place.get('ACT_CMP_C6', {}).get('home_loc')}).")
        elif rid == 'DR-SAL-05':
            h = T['actors/creatures.csv'][0]; ri = h.index('Regions'); n = 0
            for c in T['actors/creatures.csv'][1]:
                if c[0] == 'ACT_CRT_CHOIRWISP' and 'REG_02' not in c[ri].split():
                    c[ri] = ' '.join(sorted(c[ri].split() + ['REG_02'])); n += 1
            log(SAL, rid, 'applied' if n else 'skipped', 'data/actors/creatures.csv', 'REG_02 added to ACT_CRT_CHOIRWISP regions (Tide Choir trial); its level band is unchanged.' if n else 'already applied: REG_02 is listed.')
        elif rid == 'DR-SAL-06':
            notes = {'ITM_SET_41': 'Site reward; found in Saltmere sites', 'ITM_SET_42': 'Site reward; found in The Drowned Hold', 'ITM_SET_43': 'Site reward; found in The Drowned Hold',
                     'ITM_SET_44': 'Site reward; found in Citadel secrets and the Foam and Brine Choir vaults'}
            n = sum(ctx.edit('items/armor_sets.csv', k, 'note', v) for k, v in notes.items())
            log(SAL, rid, 'applied', 'data/items/armor_sets.csv', f'note set on {n} found sets (ITM_SET_41..44) with their fixed Saltmere placements.')
        else:
            log(SAL, rid, 'skipped', tgt, 'not handled')

    # ============================================================ thornwood
    for r in reqs[THN]:
        rid, tgt = r['req_id'], r['target']
        if rid == 'LREQ_01':
            log(THN, rid, 'conflict', 'data/items/lore_items.csv', 'Missing content: three Citadel logs are described by subject only; lore_items needs a text string and the writing thread owns lore text.')
        elif rid == 'LREQ_02':
            loc_req(THN, rid, ['LOC_TOWN_REG_03_03', 'LOC_ANC_REG_03_40'], {'LOC_TOWN_REG_03_03': {'name': "Thorn King's Moot", 'level': 29, 'x_m': 7024, 'y_m': 1880}})
        elif rid in ('LREQ_03', 'LREQ_04', 'LREQ_05'):
            log(THN, rid, 'skipped', tgt, f"outside data/: owned by {tgt.split(' ')[0]}.")
        elif rid == 'LREQ_06':
            want = dict(re.findall(r'(ITM_LOR_\d+) opens (LOC_DOOR_REG_03_\d+)', r['value']))
            lu = {x['item_id']: x['unlocks'] for x in ctx.rows('items/lore_items.csv')}
            ok = all(lu.get(k) == v for k, v in want.items())
            log(THN, rid, 'skipped' if ok else 'conflict', 'data/items/lore_items.csv', 'already applied: lore_items.csv unlocks match all nine keys.' if ok else 'lore_items.csv unlocks differ.')
        elif rid == 'LREQ_07':
            log(THN, rid, 'conflict', 'data/items/vendors.csv', 'Missing content: vendors.csv holds one row per stocked item and no stock is given' + ('' if 'LOC_TOWN_REG_03_03' in LOCS else ', and LOC_TOWN_REG_03_03 is not in design/world/locations.csv') + '.')
        elif rid in ('LREQ_08', 'LREQ_09'):
            log(THN, rid, 'skipped', tgt, f"outside data/: owned by {tgt.split(' ')[0]}.")
        else:
            log(THN, rid, 'skipped', tgt, 'not handled')

    # ============================================================ undervault
    for r in reqs[UV]:
        rid, tgt = r['req_id'], r['target']
        if rid == 'UVREQ_01':
            loc_req(UV, rid, ['LOC_UV_CORE'], {'LOC_UV_CORE': {'name': 'The Engine Heart', 'x_m': 5210, 'y_m': 3337, 'z_m': -260, 'level': 46, 'parent_loc': 'LOC_UV_REG_02_S06'}})
        elif rid == 'UVREQ_02':
            a = [x for x in rows('levels/undervault/anchors.csv') if x['source'] == 'new']
            loc_req(UV, rid, [x['anchor_id'] for x in a], {x['anchor_id']: {'x_m': x['x_m'], 'y_m': x['y_m'], 'z_m': x['z_m']} for x in a})
        elif rid == 'UVREQ_03':
            loc_req(UV, rid, [x['secret_id'] for x in rows('levels/undervault/secrets.csv')])
        elif rid == 'UVREQ_04':
            p = rows('levels/undervault/landmarks_pois.csv')
            loc_req(UV, rid, [x['poi_id'] for x in p], {x['poi_id']: {'name': x['name'], 'x_m': x['x_m'], 'y_m': x['y_m']} for x in p})
        elif rid == 'UVREQ_05':
            ok = all(i in ctx.ids('actors/bosses.csv') for i in ('ACT_BOSS_UV_STEVEDORE', 'ACT_BOSS_UV_ROOTWRIGHT', 'ACT_BOSS_UV_SUMPMOTHER', 'ACT_BOSS_UV_GOVERNOR'))
            log(UV, rid, 'applied' if ok else 'conflict', 'data/actors/bosses.csv', 'Four Undervault bosses added by actors/tools/gen_bosses.py as class Undervault (decided 2026-10-03; 44 bosses plus Hush).')
        elif rid in ('UVREQ_06', 'UVREQ_07'):
            log(UV, rid, 'applied', tgt, 'Moves and phases are generated with the bosses in gen_bosses.py; loot tables ITM_LT_BOSS_UV_02/03/05/CORE are in items/gen_items.py.')
        elif rid == 'UVREQ_08':
            log(UV, rid, 'conflict', 'data/items/lore_items.csv', 'Missing content: no names or lore text for the 27 items (lore_items needs a text string; the writing thread owns lore text and says no lore items sit in the Undervault).')
        elif rid == 'UVREQ_09':
            ok = all(i in ctx.ids('items/consumables.csv') for i in ('ITM_KEY_UV_ODOMAP', 'ITM_KEY_UV_OSTRAMEMORY', 'ITM_KEY_UV_OVERRIDE'))
            log(UV, rid, 'applied' if ok else 'conflict', 'data/items/consumables.csv', 'Three key items added (Key item, weight 0, sell 0) to consumables.csv and items_index.csv with name strings.')
        elif rid == 'UVREQ_10':
            add_hooks(UV, rid, TOK.findall(r['value']), extra=' MUS_ cues go to design/audio/music_cues.csv (outside data/).')
        elif rid == 'UVREQ_11':
            pairs = []
            for x in rows('levels/undervault/levels.csv'):
                pairs.append((f"STR_{x['loc_id']}_NAME", x['name'], 'Area name banner and map label (design/levels/undervault)'))
            for x in rows('levels/undervault/landmarks_pois.csv'):
                pairs.append((f"STR_{x['poi_id']}_NAME", x['name'], 'Area name banner and map label (design/levels/undervault)'))
            known = [p for p in pairs if p[0][4:-5] in LOCS]; unk = len(pairs) - len(known)
            known, cl = loc_name_pairs(known)
            merge_strings(UV, rid, known, extra=(f' {cl} names use the design/world name.' if cl else ''),
                          partial=(f' {unk} names for locations not in design/world/locations.csv not added; boss names come from bosses.csv.' if unk else ''))
        elif rid == 'UVREQ_12':
            log(UV, rid, 'skipped', tgt, 'Optional and gives no table rows; loot.csv keeps using the surface tables as it says.')
        else:
            log(UV, rid, 'skipped', tgt, 'not handled')
