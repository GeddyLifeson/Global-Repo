"""Merge module for design/writing/data-requests.csv (writing thread).
Writing strings go to ui/strings_data.csv. Writing text replaces the seeded first-pass lore text (README choice 14) and the item
descriptions (REQ_ITEMS_001 and 009 say so); every other string ID that already exists keeps the data text (owner-tied names:
quest, vendor, item, actor, region names link.py syncs from their owner tables). design/world/locations.csv wins on place names
and LOC_ IDs, so place_names.csv names and new LOC_ IDs are logged as conflicts. Codex entries become ui/codex_entries.csv."""
import csv, glob, math, os, re, collections

FILES = ['writing/data-requests.csv']
F = 'writing/data-requests.csv'
TOK = re.compile(r'(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![a-z0-9])')
RUNTIME = re.compile(r'\{([A-Z]+)_[a-z_]+\}')
RUNTIME_OK = {'ITM', 'ACT', 'PRK', 'VAR', 'BTN', 'SKL', 'ATTR', 'ELEM', 'STATUS', 'FAC', 'CMP', 'REGION', 'LOC'}  # LOC added to validate.py for {LOC_name}
STALE = ['Ashfall Reach', 'Region 2', 'Region 3', 'Region 4', 'Region 5', 'Region 6', 'Seals Quartermaster', 'TXT_', 'Lanterns', 'Hardcore']  # bible: ok
# 'Lanterns' means the removed currency; these two place names (design/world/locations.csv) are allowed
NOT_STALE = ('Stilt Lanterns', 'Abbot Lanterns')
def unstale(c):
    for n in NOT_STALE: c = c.replace(n, '')
    return c

SCREEN = {'barks.csv': 'Barks', 'books.csv': 'Book', 'codex_entries.csv': 'Lore codex', 'item_text.csv': 'Item description',
          'loading_tips.csv': 'Loading screens', 'lore_text.csv': 'Lore reader', 'ostra_hints.csv': 'HUD hint', 'quest_text.csv': 'Quest journal',
          'radiant_text.csv': 'Radiant notice', 'terminals.csv': 'Terminal', 'tutorial_text.csv': 'HUD', 'place_names.csv': 'Map'}


def norm(s):
    return re.sub(r'[^a-z ]', '', s.lower().replace('’', "'")).replace('the ', '').strip()


class Strings:
    """Fast string table access (thousands of rows): same rules as ctx.string."""
    def __init__(self, T):
        self.T = T
        self.U = {r[0]: r for r in T['ui/strings.csv'][1]}
        self.S = {r[0]: r for r in T['ui/strings_data.csv'][1]}
        self.h = T['ui/strings_data.csv'][0]

    def get(self, sid):
        r = self.U.get(sid) or self.S.get(sid)
        return r[2] if r else None

    def add(self, sid, text, screen, note='', tokens=''):
        if sid in self.U or sid in self.S: return False
        d = dict(str_id=sid, screen=screen, text_en=text, max_chars=math.ceil(len(text) * 1.4), tokens=tokens, notes=note)
        r = [str(d.get(c, '')) for c in self.h]
        self.T['ui/strings_data.csv'][1].append(r); self.S[sid] = r
        return True

    def set(self, sid, text, note=None):
        r = self.U.get(sid) or self.S.get(sid)
        r[2] = text; r[3] = str(math.ceil(len(text) * 1.4))
        if note is not None: r[5] = note


def defined_ids(T):
    d = set()
    for h, rr in T.values():
        d.update(TOK.findall(','.join(h)))
        d.update(r[0] for r in rr if r)
    return d


def text_problem(t, defined):
    for s in STALE:
        if s in unstale(t): return f'stale word "{s}"'
    for m in RUNTIME.finditer(t):
        if m.group(1) not in RUNTIME_OK: return f'runtime token {m.group(0)}'
    bad = [m.group(0) for m in TOK.finditer(t) if m.group(0) not in defined]
    return ('unresolved ' + ' '.join(bad)) if bad else ''


def writing_pairs(ctx):
    """Every (file, str_id, text) pair in design/writing/*.csv: str_id/text_en columns and <x>_str/<x>_en columns."""
    out = []
    for p in sorted(glob.glob(os.path.join(ctx.DESIGN, 'writing', '*.csv'))):
        fn = os.path.basename(p)
        rows = ctx.design_rows('writing/' + fn)
        if not rows: continue
        cols = list(rows[0].keys())
        for a in cols:
            if a == 'str_id' or a.endswith('_str'):
                b = 'text_en' if a == 'str_id' else a[:-4] + '_en'
                if b not in cols: continue
                for r in rows:
                    if r[a]: out.append((fn, r[a], r[b], r))
    return out


def apply(T, ctx):
    log = lambda rid, st, tgt, why: ctx.log(F, rid, st, tgt, why)
    req = ctx.design_rows(F)
    S = Strings(T)
    pairs = writing_pairs(ctx)
    byid = {sid: (fn, t, r) for fn, sid, t, r in pairs}
    codex = ctx.design_rows('writing/codex_entries.csv')
    WLOC = ctx.design_rows('world/locations.csv')
    done = {}          # req_id -> (status, target, reason), logged in file order at the end

    # ---------------------------------------------------------------- tutorial rewrites in ui/strings.csv (explicit "Replace with the rewrite")
    for rid in ('STR_TUT_DEATH_B', 'STR_TUT_SURGE_B', 'STR_TUT_ECHO_B', 'STR_TUT_QUIET_B'):
        new = byid.get(rid, (None, None))[1]
        if new is None: done[rid] = ('skipped', 'ui/strings.csv', 'nothing to apply: tutorial_text.csv has no rewrite for this ID.')
        elif S.get(rid) == new: done[rid] = ('skipped', 'ui/strings.csv', 'already applied: text matches the tutorial_text.csv rewrite.')
        elif S.get(rid) is None: S.add(rid, new, 'HUD', 'design/writing/tutorial_text.csv'); done[rid] = ('applied', 'ui/strings_data.csv', 'added the tutorial_text.csv rewrite.')
        else: S.set(rid, new); done[rid] = ('applied', 'ui/strings.csv', 'replaced the text with the tutorial_text.csv rewrite as the request asks.')

    # ---------------------------------------------------------------- loading tip fixes that follow the owning data
    def tipfix(sid, old, new, why):
        t = S.get(sid)
        if t is None: return ('skipped', 'ui/strings.csv', f'nothing to apply: {sid} is not in data.')
        if old not in t: return ('skipped', 'ui/strings.csv', f'already applied: {sid} no longer says "{old}".')
        S.set(sid, t.replace(old, new)); return ('applied', 'ui/strings.csv', why)
    done['STR_TIP_021'] = tipfix('STR_TIP_021', '2.5 seconds', '3 seconds', 'Root duration set to 3 seconds to match actors/status_effects.csv STS_ROOT.')
    done['STR_TIP_051'] = tipfix('STR_TIP_051', 'after 3 seconds', 'after 2 seconds', 'decay delay set to 2 seconds to match items/formulas.csv ITM_F_STATUS.')
    REGW = {r[0]: r for r in T['world/regions.csv'][1]}
    rh = T['world/regions.csv'][0]
    fixed = []
    for tip, reg in (('STR_TIP_REG_R2', 'REG_02'), ('STR_TIP_REG_R3', 'REG_03'), ('STR_TIP_REG_R5', 'REG_05')):
        t = S.get(tip); r = REGW[reg]
        lo, hi = r[rh.index('level_min')], r[rh.index('level_max')]
        if t is None: continue
        nt = re.sub(r'level \d+ to \d+', f'level {lo} to {hi}', t)
        if nt != t: S.set(tip, nt); fixed.append(f'{r[1]} {lo}-{hi}')
    done['STR_TIP_REG_R2_R3_R5'] = ('applied', 'ui/strings.csv', 'region tips now use the world/regions.csv bands: ' + ', '.join(fixed) + '.') if fixed else \
        ('skipped', 'ui/strings.csv', 'already applied: region tips match world/regions.csv.')

    # ---------------------------------------------------------------- codex tab strings and codex title strings (before the bulk merge)
    for rid in ('STR_CDX_HISTORY', 'STR_CDX_WEAVE', 'STR_CDX_TIER_PENDING'):
        r = next(x for x in req if x['id'] == rid)
        text = re.search(r'"(.+?)"', r['request']).group(1)
        done[rid] = ('applied', 'ui/strings_data.csv', f'added "{text}" (screen Lore codex).') if S.add(rid, text, 'Lore codex', r['notes']) else \
            ('skipped', 'ui/strings_data.csv', 'already applied: string exists.')
    ctitle = {c['title_str']: c for c in codex}
    for r in req:
        if r['request'].startswith('new title string for codex entry'):
            c = ctitle.get(r['id'])
            if not c: done[r['id']] = ('skipped', 'ui/strings_data.csv', 'nothing to apply: codex_entries.csv has no title for this ID.'); continue
            done[r['id']] = ('applied', 'ui/strings_data.csv', f'added codex title "{c["title_en"]}" from codex_entries.csv.') \
                if S.add(r['id'], c['title_en'], 'Lore codex', f'Codex title for {c["cdx_id"]}; design/writing/codex_entries.csv') else \
                ('skipped', 'ui/strings_data.csv', 'already applied: string exists.')

    # ---------------------------------------------------------------- books: new item family ITM_BOOK_*
    books = ctx.design_rows('writing/books.csv')
    T['items/books.csv'] = [['item_id', 'name', 'title_str', 'author', 'kind', 'region', 'pages', 'weight', 'sell_price', 'icon', 'summary'], []]   # owned here, rebuilt each build
    for b in books:
        iid = b['proposed_item_id']
        S.add(f'STR_{iid}_NAME', b['title_en'], 'Item name', 'Book')
        ctx.append('items/books.csv', dict(item_id=iid, name=b['title_en'], title_str=b['title_str'], author=b['author'], kind=b['kind'],
                                           region=b['region'], pages=b['pages'], weight=0.5, sell_price=10, icon='UI_ICON_BOOK', summary=b['summary']))
        ctx.append('items/items_index.csv', dict(item_id=iid, name=b['title_en'], category='Book', rarity='', file='books.csv'))
    done['ITM_BOOK_001..060'] = ('applied', 'items/books.csv', f'built items/books.csv with {len(T["items/books.csv"][1])} books from books.csv (weight 0.5, sell 10 Ember, icon UI_ICON_BOOK) and indexed them in items_index.csv as category Book.')

    # ---------------------------------------------------------------- bulk merge of every writing string
    defined = defined_ids(T) | set(byid)
    WNAME = {w['loc_id']: w['name'] for w in WLOC}
    c = collections.Counter(); kept = collections.Counter(); held = []; keptids = []; heldtok = collections.Counter()
    for fn, sid, t, r in pairs:
        if not t: c['empty'] += 1; continue
        if fn == 'place_names.csv' and WNAME.get(r['loc_id'], t) != t:
            t = WNAME[r['loc_id']]; c['place'] += 1
        cur = S.get(sid)
        if cur is not None:
            if cur == t: c['present'] += 1
            elif sid in S.S and (re.match(r'STR_LOREITEM_\d+$', sid) or (fn == 'item_text.csv' and sid.endswith('_DESC'))):
                p = text_problem(t, defined)
                if p: held.append(sid); heldtok[p.split(' ')[0]] += 1; continue
                S.set(sid, t, f'design/writing/{fn}; writer text replaces the first pass')
                c['lore' if 'LOREITEM' in sid else 'desc'] += 1
            else:
                kept['quest names' if sid.startswith('STR_QST_') else 'vendor names' if sid.startswith('STR_ACT_NPC_VEN') else
                     'UI strings' if sid in S.U else 'actor names' if sid.startswith('STR_ACT_') else 'owner names'] += 1
                keptids.append(sid)
            continue
        p = text_problem(t, defined)
        if p:
            held.append(sid)
            for m in TOK.finditer(t):
                if m.group(0) not in defined: heldtok[m.group(0)] += 1
            continue
        toks = ' '.join(sorted({m.group(0)[1:-1] for m in RUNTIME.finditer(t)}))
        S.add(sid, t, SCREEN.get(fn, 'Writing'), f'design/writing/{fn}; status {r.get("status", "draft")}', toks)
        c['added'] += 1
    nk = sum(kept.values())
    reason = (f"merged design/writing strings: {c['added']} added, {c['lore']} seeded lore texts and {c['desc']} item descriptions replaced, "
              f"{c['present']} already present; kept the data text for {nk} clashing IDs ("
              + ', '.join(f'{v} {k}' for k, v in kept.items()) + " synced from their owner tables, e.g. " + ', '.join(keptids[:3]) + "), "
              f"gave {c['place']} place-name keys the world name (design/world/locations.csv wins), and left out {len(held)} strings whose text names IDs not in data "
              f"({', '.join(sorted(heldtok)[:6])}...: {', '.join(held[:4])}...).")
    done['STR_* (all writing text)'] = ('conflict' if nk or held or c['place'] else 'applied', 'ui/strings_data.csv', reason)
    bulk = 'already applied by the "STR_* (all writing text)" merge'
    for rid, what in [('STR_TERM_* / STR_STONE_*', 'terminal and Choir stone texts'), ('STR_CDX_*_T1..T3, STR_CDX_*_OSTRA', 'codex tier and Ostra texts'),
                      ('STR_BARK_*', 'bark samples'), ('REQ_ITEMS_002', 'STR_LOREITEM_nnn_RESTORED and _OSTRA keys (the MQ_A2_06 gate is a campaign flag)'),
                      ('STR_QUEST_TEXT', 'quest text (draft status; owner-tied quest names keep the data text)'), ('STR_RAD', 'radiant text'),
                      ('STR_OSTRA_HINT', 'Ostra hints (the cold color state and MQ_A2_07 suppression are UI behavior for the UI thread)'),
                      ('STR_TIP_NUMBERING', 'loading tips STR_TIP_053..252')]:
        n = sum(1 for fn, sid, t, r in pairs if (
            (rid.startswith('STR_TERM') and fn == 'terminals.csv') or (rid.startswith('STR_CDX') and fn == 'codex_entries.csv') or
            (rid == 'STR_BARK_*' and fn == 'barks.csv') or (rid == 'REQ_ITEMS_002' and re.match(r'STR_LOREITEM_\d+_(RESTORED|OSTRA)$', sid)) or
            (rid == 'STR_QUEST_TEXT' and fn == 'quest_text.csv') or (rid == 'STR_RAD' and fn == 'radiant_text.csv') or
            (rid == 'STR_OSTRA_HINT' and fn == 'ostra_hints.csv') or (rid == 'STR_TIP_NUMBERING' and fn == 'loading_tips.csv')) and S.get(sid) == t)
        done[rid] = ('skipped', 'ui/strings_data.csv', f'{bulk}: {n} {what} are in data.')
    nf = sum(1 for fn, sid, t, r in pairs if fn == 'item_text.csv' and sid.endswith('_FLAVOR') and S.get(sid) == t)
    done['REQ_ITEMS_001'] = ('skipped', 'ui/strings_data.csv', f'{bulk}: {nf} FLAVOR strings added and {c["desc"]} item descriptions replaced.')
    nshb = sum(1 for fn, sid, t, r in pairs if fn == 'item_text.csv' and re.match(r'STR_ITM_SHB_\w+_DESC$', sid) and S.get(sid) == t)
    done['REQ_ITEMS_009'] = ('skipped', 'ui/strings_data.csv', f'{bulk}: {nshb} Shardborn descriptions and the consumable descriptions carry the writer text.')

    # ---------------------------------------------------------------- codex table
    hdr = ['cdx_id', 'tab', 'title_str', 't1_str', 't2_str', 't3_str', 'ostra_str', 'owner_id', 'unlock_t1', 'unlock_t2', 'unlock_t3', 'max_chars', 'status']
    have = set(S.U) | set(S.S)
    defined2 = defined_ids(T) | {cx['cdx_id'] for cx in codex} | {r['qst_id'] for r in ctx.design_rows('campaign/quests.csv')}   # m_campaign runs last and adds these quests
    miss = collections.Counter(); missids = collections.Counter()
    def keep_ids(k, v):    # continuity pass: keep every unlock/owner ID that resolves, drop only the ones that do not
        if k not in ('owner_id', 'unlock_t1', 'unlock_t2', 'unlock_t3'): return v
        bad = [m.group(0) for m in TOK.finditer(v) if m.group(0) not in defined2]
        for b in bad: miss[k] += 1; missids[b] += 1
        return '' if bad else v
    rows = [[keep_ids(k, cx.get(k, '')) if (not k.endswith('_str') or cx[k] in have) else '' for k in hdr] for cx in codex]
    T['ui/codex_entries.csv'] = [hdr, rows]
    done['CODEX_UNLOCKS'] = ('conflict' if miss else 'applied', 'ui/codex_entries.csv',
        f'created ui/codex_entries.csv with {len(rows)} entries with owner and unlock IDs; {sum(miss.values())} unlock cells left blank because they cite IDs not in data: '
        + ', '.join(f'{k} x{v}' for k, v in missids.most_common(8)))

    # ---------------------------------------------------------------- locations: design/world/locations.csv wins
    P = ctx.design_rows('writing/place_names.csv')
    diff = [p for p in P if WNAME.get(p['loc_id']) not in (None, p['text_en'])]
    ex = diff[0]
    done['LOC_* names'] = ('conflict', 'world/locations.csv',
        f'design/world/locations.csv wins on place names: {len(diff)} of {len(P)} place_names.csv names differ from the world names '
        f'(e.g. {ex["loc_id"]} world "{WNAME[ex["loc_id"]]}", writing "{ex["text_en"]}"), so those keys carry the world names.')
    WN = collections.defaultdict(list)
    for w in WLOC: WN[norm(w['name'])].append(w)
    for r in req:
        if r['request'].startswith('New location ID'):
            name, reg = re.search(r'"(.+?)" \((REG_\w+)\)', r['request']).groups()
            hits = sorted(WN.get(norm(name), []), key=lambda w: w['region'] != reg)
            who = f'world names this place {hits[0]["loc_id"]} "{hits[0]["name"]}"' if hits else f'world has no location named "{name}"'
            done[r['id']] = ('conflict', 'world/locations.csv', f'LOC_ IDs are frozen to design/world/locations.csv, which has no {r["id"]}; {who}.')

    # ---------------------------------------------------------------- lore item fixes
    LH = T['items/lore_items.csv'][0]; ni = LH.index('name')
    IH = T['items/items_index.csv'][0]; ii = IH.index('name')
    IDX = {r[0]: r for r in T['items/items_index.csv'][1]}
    def rename(pat, repl, rows_key='items/lore_items.csv', col=ni):
        n = 0
        for r in T[rows_key][1]:
            nn = re.sub(pat, repl, r[col])
            if nn != r[col]:
                r[col] = nn; n += 1
                if r[0] in IDX: IDX[r[0]][ii] = nn
                if r[0] in IDX and f'STR_{r[0]}_NAME' in S.S: S.set(f'STR_{r[0]}_NAME', nn)
        return n
    n = rename(r'^Letter from Choir Precentor Vael to a lost lover', 'Letter from a Choir cantor to a lost lover')
    done['REQ_ITEMS_004'] = ('applied', 'items/lore_items.csv', f'renamed {n} letters to "Letter from a Choir cantor to a lost lover (n)" (Vael is the Ember Regent).') if n else \
        ('skipped', 'items/lore_items.csv', 'already applied: no letter names Precentor Vael.')
    n = rename(r'^Letter from Captain Ires to the Guildmaster', 'Letter from Captain Ires to the Guildmistress')
    done['REQ_ITEMS_005'] = ('applied', 'items/lore_items.csv', f'renamed {n} letters to "...to the Guildmistress".') if n else \
        ('skipped', 'items/lore_items.csv', 'already applied: no letter says Guildmaster in its name.')
    n = rename(r'^(.* Key \(\d+\)) \d+$', r'\1')
    done['REQ_ITEMS_006'] = ('applied', 'items/lore_items.csv', f'removed the trailing digit from {n} key names (the request estimated 50; {n} carried one).') if n else \
        ('skipped', 'items/lore_items.csv', 'already applied: no key name ends in a stray digit.')
    n = rename(r'\b(\w+) \1\b', r'\1', 'items/armor_pieces.csv', T['items/armor_pieces.csv'][0].index('name'))
    done['REQ_ITEMS_007'] = ('applied', 'items/armor_pieces.csv', f'fixed doubled words in {n} armor names, with items_index.csv and their STR_<ID>_NAME strings.') if n else \
        ('skipped', 'items/armor_pieces.csv', 'already applied: no doubled words in armor names.')
    flag = {r['owner_id'] for r in ctx.design_rows('writing/lore_text.csv') if 'CNT_OSTRA_CONTRADICTIONS +1' in r['notes']}
    if 'contradiction' in LH:
        done['REQ_ITEMS_003'] = ('skipped', 'items/lore_items.csv', 'already applied: lore_items.csv has a contradiction column.')
    else:
        for r in T['items/lore_items.csv'][1]: r.append('1' if r[0] in flag else '0')
        LH.append('contradiction')
        done['REQ_ITEMS_003'] = ('applied', 'items/lore_items.csv', f'added a contradiction column (1 for the {sum(1 for r in T["items/lore_items.csv"][1] if r[-1] == "1")} lore items whose writer notes carry CNT_OSTRA_CONTRADICTIONS +1); the counter itself belongs to the campaign flags.')

    # ---------------------------------------------------------------- tutorial popups
    PH = T['ui/popups.csv'][0]
    for r in req:
        if not r['request'].startswith('Add popup row:'): continue
        d = {}; last = None
        for seg in r['request'][len('Add popup row:'):].split(';'):
            seg = seg.strip()
            k, eq, v = seg.partition('=')
            if eq and k.strip() in PH: last = k.strip(); d[last] = v.strip()
            elif last: d[last] += '; ' + seg
        d['popup_id'] = r['id']
        miss = [d[k] for k in ('title_str', 'body_str') if d.get(k) and S.get(d[k]) is None]
        if miss: done[r['id']] = ('conflict', 'ui/popups.csv', f'popup not added: {" ".join(miss)} not found in tutorial_text.csv.'); continue
        done[r['id']] = ('applied', 'ui/popups.csv', f'added tutorial popup {r["id"]}; its strings come from tutorial_text.csv.') if ctx.append('ui/popups.csv', d) else \
            ('skipped', 'ui/popups.csv', f'already applied: popup {r["id"]} exists.')

    # ---------------------------------------------------------------- npc
    if ctx.append('world/npcs.csv', dict(act_id='ACT_NPC_HOLLOWED_OFFICER', name='Hollowed Officer', role='Mini-boss; the Hush speaks through him at 10% Health',
                                         fac_id='FAC_HOLLOWED', location='', vendor_id='', str_id='STR_ACT_NPC_HOLLOWED_OFFICER_NAME')):
        S.add('STR_ACT_NPC_HOLLOWED_OFFICER_NAME', 'Hollowed Officer', 'Data name')
        done['ACT_NPC_HOLLOWED_OFFICER'] = ('applied', 'world/npcs.csv', 'added the Hollowed Officer mini-boss NPC (not one of the 44 bosses) with its name string.')
    else:
        done['ACT_NPC_HOLLOWED_OFFICER'] = ('skipped', 'world/npcs.csv', 'already applied: ACT_NPC_HOLLOWED_OFFICER exists.')
    leaders = [f'ACT_{f}_LEADER' for f in ('HOLLOWED', 'REMNANT', 'THORN', 'CHOIRBORN')]
    have_l = [a for a in leaders if a in ctx.ids('actors/enemies.csv')]
    done['ACT_<FAC>_LEADER'] = ('skipped', 'actors/enemies.csv', f'already applied: {len(have_l)} of 4 Leader enemies exist ({", ".join(have_l)}), so barks can use the Leader role.')

    # ---------------------------------------------------------------- token prefix (validate.py change made by this merge)
    done['{LOC_name}'] = ('applied', 'tools/validate.py', 'validate.py now allows the LOC runtime token prefix, which the radiant notices need for {LOC_name}.')
    done['TOKEN_LOC'] = ('skipped', 'README.md', 'already applied: validate.py allows LOC; the README token list line is for the main thread.')

    # ---------------------------------------------------------------- notes, questions, other owners
    tip8 = 'STR_TIP_008 has no replacement line in design/writing, so the data text stays until the writer supplies one'
    other = {
        'QST_QH_00 / SQ_HUB_09': 'outside data/: owned by design/campaign (quest rename).',
        'ECO Seal cap': 'note: the Seal cap question (25 vs 100) is for the systems and loops threads; nothing for writing to apply.',
        'STR_TIP_008 / STR_TUT_DEATH_B': f'STR_TUT_DEATH_B rewrite is applied under its own row; {tip8}.',
        'STR_TIP_008': f'nothing to apply: {tip8}.',
        'STR_TIP_018': 'nothing to apply: no replacement line for STR_TIP_018 in design/writing; the writer needs to supply one.',
        'STR_TIP_037': 'nothing to apply: the request waits on the Seal cap decision and gives no replacement line.',
        'REG_U lore': 'nothing to apply yet: the request names no items, sites or text for the 10 Undervault lore items; writing adds them on rerun.',
        'REQ_ITEMS_008': 'note: a suggestion to place lore in the Undervault, with no items named.',
        'CNT_OSTRA_CONTRADICTIONS': 'outside data/: owned by design/campaign (flags.csv).',
        'ACT_NPC_TOWNSFOLK_<LOC>': 'outside data/: VO casting groups owned by design/audio; no per-settlement rows are named.',
        'STR_DLG_<SCENE>_nnn': 'note: a key pattern for dialogue lines that arrive at VO script lock; no text yet.',
        'UI_HINT_COLD': 'note: UI behavior for the UI thread; nothing in data to apply.',
        'UI_OSTRA_SILENT': 'note: UI behavior for the UI thread; nothing in data to apply.',
    }
    # continuity pass: new lore items the writing thread wrote text for ("Add lore_items row: k=v; ...")
    for r in req:
        cell = next((v for v in r.values() if isinstance(v, str) and v.startswith('Add lore_items row:')), None)
        if not cell or r['id'] in done: continue
        kv = dict(x.split('=', 1) for x in cell[len('Add lore_items row:'):].split('. Text')[0].split('; ') if '=' in x)
        kv = {k.strip(): v.strip() for k, v in kv.items()}
        if kv.get('text_id') not in S.U and kv.get('text_id') not in S.S:
            done[r['id']] = ('conflict', 'items/lore_items.csv', f"text {kv.get('text_id')} is not in data, so the item was not added."); continue
        new = ctx.append('items/lore_items.csv', {'item_id': kv['item_id'], 'name': kv['name'], 'lore_type': kv.get('lore_type', ''), 'region': kv.get('region', ''),
                         'location': kv.get('location', ''), 'text_id': kv['text_id'], 'unlocks': '', 'weight': kv.get('weight', '0'), 'sell_price': kv.get('sell_price', '0'),
                         'icon': kv.get('icon', ''), 'contradiction': kv.get('contradiction', '0')})
        ctx.append('items/items_index.csv', {'item_id': kv['item_id'], 'name': kv['name'], 'category': 'Lore item', 'rarity': '', 'file': 'lore_items.csv', 'source_loc': kv.get('location', '')})
        ctx.string(f"STR_{kv['item_id']}_NAME", kv['name'], 'Items')
        done[r['id']] = ('applied', 'items/lore_items.csv', f"lore item {kv['name']} added at {kv.get('location', '')} with text {kv['text_id']}.") if new else \
            ('skipped', 'items/lore_items.csv', 'already applied: the lore item is in data.')
    # canon renames of existing lore items the writing thread asks for ("Rename lore item: item_id=X; name=Y")
    for r in req:
        if not r['request'].startswith('Rename lore item:') or r['id'] in done: continue
        kv = dict(x.strip().split('=', 1) for x in r['request'][len('Rename lore item:'):].split('; '))
        lr = next((x for x in T['items/lore_items.csv'][1] if x[0] == kv['item_id']), None)
        if lr is None:
            done[r['id']] = ('conflict', 'items/lore_items.csv', f"{kv['item_id']} is not in data, so it was not renamed."); continue
        if lr[ni] == kv['name']:
            done[r['id']] = ('skipped', 'items/lore_items.csv', f"already applied: {kv['item_id']} is named \"{kv['name']}\"."); continue
        lr[ni] = kv['name']
        if lr[0] in IDX: IDX[lr[0]][ii] = kv['name']
        if f'STR_{lr[0]}_NAME' in S.S: S.set(f'STR_{lr[0]}_NAME', kv['name'])
        done[r['id']] = ('applied', 'items/lore_items.csv', f"renamed {kv['item_id']} to \"{kv['name']}\" with items_index.csv and its name string.")
    for r in req:
        rid = r['id']
        if rid in done: continue
        if rid in other: st = 'skipped'; why = other[rid]; tgt = r['target_table']
        elif 'campaign' in r['target_table']: st, tgt, why = 'skipped', r['target_table'], 'outside data/: owned by design/campaign (flags.csv).'
        else: st, tgt, why = 'skipped', r['target_table'], 'not recognised by m_writing.'
        done[rid] = (st, tgt, why)
    for r in req:
        st, tgt, why = done[r['id']]
        log(r['id'], st, tgt, why)
