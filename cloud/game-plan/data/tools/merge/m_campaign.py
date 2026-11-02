"""Campaign data requests (design/campaign/data-requests.csv): new actors, quests and locations, plus a few changes.
Runs last. Reads the campaign, world and writing design files at run time (nothing about them is hard-coded):
- locations: design/world/locations.csv wins on IDs and names; campaign/tools/loc_map.csv says which world ID a campaign place became.
- actors: names from campaign strings, 02-characters.md, writing/glossary.csv or writing/codex_entries.csv; else derived from the ID.
- quests: campaign/quests.csv for the data, campaign/strings_campaign.csv for name and description strings."""
import collections, csv, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'design', 'writing', 'tools'))
from canon_names import canon  # noqa: E402

FILES = ['campaign/data-requests.csv']
F = FILES[0]
TOK = re.compile(r'(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![a-z0-9])')
KIND = {'Main': 'Main quest', 'Faction': 'Faction questline', 'Companion': 'Companion quest', 'Side': 'Side quest', 'Shardborn': 'Exotic quest'}


def _read(ctx, rel):
    p = os.path.join(ctx.DESIGN, rel)
    return ctx.design_rows(rel) if os.path.exists(p) else []


def _norm(s):
    s = re.sub(r'\(.*?\)', '', s.lower())
    s = re.sub(r'^the ', '', s.strip())
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()


def _region_of(loc_id):
    m = re.match(r'LOC_CQ_(REG_\d\d|HUB|REG_Q|REG_U)', loc_id)
    if not m: return ''
    return 'REG_HUB' if m.group(1) == 'HUB' else m.group(1)


def _derive_name(act):
    s = re.sub(r'^ACT_(NPC|BOSS|CMP)_', '', act)
    return canon(' '.join(w.capitalize() for w in s.split('_')))


def _actor_names(ctx, S):
    """ID -> (name, role, source) from the design files, in priority order."""
    out = {}
    doc = os.path.join(ctx.DESIGN, 'campaign/02-characters.md')
    if os.path.exists(doc):
        txt = open(doc, encoding='utf-8').read()
        for line in txt.splitlines():
            m = re.match(r'\|\s*(ACT_[A-Z0-9_]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|', line)
            if m: out.setdefault(m.group(1), (m.group(2), m.group(3), 'campaign/02-characters.md'))
            m = re.match(r'\|\s*([^|]+?)\s*\((ACT_[A-Z0-9_]+)\)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|', line)
            if m: out.setdefault(m.group(2), (m.group(1), m.group(4), 'campaign/02-characters.md'))
        for m in re.finditer(r'^\*\*([^*(]+?)\s*\((ACT_[A-Z0-9_]+)', txt, re.M):
            out.setdefault(m.group(2), (m.group(1).strip(), '', 'campaign/02-characters.md'))
    for r in _read(ctx, 'writing/glossary.csv'):
        m = re.match(r'(ACT_[A-Z0-9_]+)', r.get('notes', ''))
        if m and r.get('category') == 'Character': out.setdefault(m.group(1), (r['term'], '', 'writing/glossary.csv'))
    for r in _read(ctx, 'writing/codex_entries.csv'):
        if r.get('owner_id', '').startswith('ACT_') and r.get('title_en'):
            out.setdefault(r['owner_id'], (r['title_en'], '', 'writing/codex_entries.csv'))
    # campaign strings win over everything when they name the actor
    for sid, text in S.items():
        m = re.match(r'STR_(ACT_[A-Z0-9_]+)_NAME$', sid)
        if m: out[m.group(1)] = (text, out.get(m.group(1), ('', '', ''))[1], 'campaign/strings_campaign.csv')
    return out


def apply(T, ctx):
    req = ctx.design_rows(F)
    S = {r['str_id']: r['text_en'] for r in _read(ctx, 'campaign/strings_campaign.csv')}
    CQ = {r['qst_id']: r for r in _read(ctx, 'campaign/quests.csv')}
    W = {r['loc_id']: r for r in _read(ctx, 'world/locations.csv')}
    LM = {r['campaign_id']: r for r in _read(ctx, 'campaign/tools/loc_map.csv')}
    PN = _read(ctx, 'writing/place_names.csv')
    LOCK = 'world/locations.csv'
    log = lambda rid, st, tgt, why: ctx.log(F, rid, st, tgt, why)
    done = set()          # request rows handled (index)
    added_quests, added_npcs, qstr = [], [], {}

    def wmap(lid):        # campaign place -> world ID (world wins)
        w = LM.get(lid, {}).get('world_id', '')
        return w if w and w in W else lid

    # ---------------------------------------------------------------- locations
    wname = collections.defaultdict(list)
    for lid, r in W.items(): wname[(_norm(r['name']), r['region'])].append(lid)
    for r in PN: wname[(_norm(r['text_en']), r['region'])].append(r['loc_id'])
    for i, r in enumerate(req):
        if r['request'] != 'new location': continue
        done.add(i); lid = r['id']; h = T[LOCK][0]
        if lid in ctx.ids(LOCK):
            log(lid, 'skipped', LOCK, f'already applied: {lid} is in data/world/locations.csv'); continue
        if lid in W:
            w = W[lid]; d = {c: w.get(c, '') for c in h if c in ('loc_id', 'kind', 'region', 'name', 'notes')}
            ctx.append(LOCK, d); log(lid, 'applied', LOCK, f'added from design/world/locations.csv with the world name "{w["name"]}" and region {w["region"]}'); continue
        m = LM.get(lid, {}); wid = m.get('world_id', '')
        if wid and wid != lid:
            wn = W.get(wid, {}).get('name', m.get('world_name', ''))
            log(lid, 'conflict', LOCK, f'world has this place as {wid} ({wn}); world wins, so the campaign should use {wid} and no new location was added'); continue
        reg = _region_of(lid); cname = m.get('campaign_name') or _derive_name(lid.replace('LOC_CQ_', '').replace(reg + '_', '').replace('HUB_', ''))
        hit = [x for x in wname.get((_norm(cname), reg), []) if x != lid]
        if hit:
            log(lid, 'conflict', LOCK, f'world has a place named "{cname}" in {reg} as {hit[0]}; world wins, so no new location was added'); continue
        name = cname[0].upper() + cname[1:]
        d = dict(loc_id=lid, kind='Quest location', region=reg, name=name, notes='not in world/locations.csv; added for campaign')
        if 'layer' in h: d['layer'] = 'Hub' if reg == 'REG_HUB' else 'Surface'
        ctx.append(LOCK, {c: d.get(c, '') for c in h})
        src = 'campaign/tools/loc_map.csv' if m.get('campaign_name') else 'derived from the ID'
        log(lid, 'applied', LOCK, f'not in world/locations.csv; added for campaign as "{name}" in {reg} (name from {src})')

    # ---------------------------------------------------------------- actors
    NK = 'world/npcs.csv'
    names = _actor_names(ctx, S)
    act_loc = collections.defaultdict(collections.Counter)
    for st in _read(ctx, 'campaign/quest_steps.csv'):
        if st.get('target', '').startswith('ACT_') and st.get('loc'): act_loc[st['target']][wmap(st['loc'])] += 1
    for q in CQ.values():
        if q['giver'].startswith('ACT_') and q['locations']: act_loc[q['giver']][wmap(q['locations'].split('; ')[0])] += 1
    enemy_ids = ctx.ids('actors/enemies.csv'); base_vars = sorted(x for x in enemy_ids if x.startswith('ACT_VAR_'))
    hush_npc = False
    for i, r in enumerate(req):
        if r['request'] != 'new actor': continue
        done.add(i); a = r['id']
        if a.startswith('ACT_VAR_') and a in enemy_ids:
            log(a, 'skipped', 'actors/enemies.csv', 'already applied: regional variant added by actors/tools/gen_enemies.py (decided 2026-10-03; enemy cap 69)'); continue
        if a.startswith('ACT_VAR_'):
            reg = a.split('_')[2]
            have = [x for x in base_vars if x.split('_')[2] == reg]
            log(a, 'conflict', 'actors/enemies.csv', f'enemy types are locked at 69 (README choice 24), and {reg} already has {len(have)} variants ({have[0]} to {have[-1]}); plan wins, so this seventh-plus variant was not added and the quest should use an existing variant')
            continue
        if a in added_npcs:
            log(a, 'skipped', NK, f'already applied: duplicate request; {a} was added by its earlier row in this file'); continue
        if any(a in ctx.ids(k) for k in T if k.startswith(('world/', 'actors/'))):
            log(a, 'skipped', NK, f'already applied: {a} is already in data'); continue
        nm, role, src = names.get(a, ('', '', ''))
        derived = not nm
        if derived: nm = _derive_name(a)
        if a == 'ACT_BOSS_HUSH':
            role = 'Final boss, story actor (plan 5.3, outside the 44 bosses); boss stats pending'
            loc = 'LOC_Q_CORE'
        else:
            if not role or role.startswith('See '): role = 'Campaign NPC'
            loc = act_loc[a].most_common(1)[0][0] if act_loc[a] else ''
        sid = f'STR_{a}_NAME'
        ctx.append(NK, dict(act_id=a, name=nm, role=role, fac_id='', location=loc, vendor_id='', str_id=sid))
        clash = not ctx.string(sid, nm, 'Data name', 'Campaign actor') and \
            next((x[2] for k in ('ui/strings.csv', 'ui/strings_data.csv') for x in T[k][1] if x[0] == sid), nm) != nm
        added_npcs.append(a); hush_npc |= a == 'ACT_BOSS_HUSH'
        how = 'name derived from the ID (no campaign string or design/writing name exists)' if derived else f'name "{nm}" from {src}'
        if a == 'ACT_BOSS_HUSH': how += '; bosses.csv needs HP, Ward, resistances, moves and phases that campaign data does not give, so it goes to npcs'
        if clash: log(a, 'conflict', NK, f'added to world/npcs.csv ({how}) but {sid} already exists with other text; existing text kept (1 clash)')
        else: log(a, 'applied', NK, f'added to world/npcs.csv; {how}')

    # ---------------------------------------------------------------- quests
    QK = 'world/quests.csv'
    for i, r in enumerate(req):
        if r['request'] != 'new quest': continue
        done.add(i); q = r['id']
        if q in ctx.ids(QK):
            log(q, 'skipped', QK, f'already applied: {q} is in data/world/quests.csv'); continue
        c = CQ.get(q)
        if not c:
            log(q, 'skipped', QK, 'nothing to apply: the quest is not in design/campaign/quests.csv'); continue
        name = S.get(c.get('str_name') or f'STR_{q}_NAME', c['name'])
        desc = S.get(c.get('str_desc') or f'STR_{q}_DESC', c['summary'])
        ctx.append(QK, dict(qst_id=q, name=name, kind=KIND.get(c['type'], c['type'] + ' quest'),
                            fac_id=c['line'] if c['line'].startswith('FAC_') else '', region=c['region'],
                            reward=c['reward_items'], act=c['act'], level=c['level'], giver=c['giver'], prereq=c['prereq'],
                            locations='; '.join(dict.fromkeys(wmap(x) for x in c['locations'].split('; ') if x)), ember=c['ember'],
                            reward_rep=c['reward_rep'], lore_item=c['lore_item']))
        added_quests.append(q); qstr[q] = (i, name, desc, c)

    # ---------------------------------------------------------------- keep only references that resolve
    defined = ctx.all_ids()
    for k0, (h0, _) in T.items(): defined.update(TOK.findall(','.join(h0)))
    dropped = collections.Counter()

    def clean(k, key, col):
        h, rr = T[k]; j = h.index(col)
        for row in rr:
            if row[0] != key: continue
            parts = [p for p in row[j].split('; ') if p]
            keep = [p for p in parts if all(t in defined for t in TOK.findall(p))]
            if len(keep) != len(parts): dropped[(k, col)] += len(parts) - len(keep); row[j] = '; '.join(keep)
    for q in added_quests:
        for col in ('reward', 'giver', 'prereq', 'locations', 'reward_rep', 'lore_item'): clean(QK, q, col)
    for a in added_npcs:
        for col in ('role', 'location'): clean(NK, a, col)

    # quest strings, added once every ID they could mention exists; text with unresolved IDs is not added
    for q, (i, name, desc, c) in qstr.items():
        clashes, missing = 0, []
        for sid, text, scr in ((f'STR_{q}_NAME', name, 'Data name'), (f'STR_{q}_DESC', desc, 'Data description')):
            bad = [t for t in TOK.findall(text) if t not in defined]
            if bad: missing += bad; continue
            if not ctx.string(sid, text, scr, 'Campaign quest'):
                old = next((x[2] for k in ('ui/strings.csv', 'ui/strings_data.csv') for x in T[k][1] if x[0] == sid), text)
                clashes += old != text
        if missing:
            log(q, 'conflict', QK, f'added "{name}" from design/campaign/quests.csv, but its description string was not added because it names {", ".join(dict.fromkeys(missing))}, which data does not define (story flags belong to design/tech)')
        elif clashes:
            log(q, 'conflict', QK, f'added "{name}" from design/campaign/quests.csv, but {clashes} of its name/description strings already exist with other text; existing text kept')
        else:
            log(q, 'applied', QK, f'added "{name}" ({c["type"]}, {c["region"]}) from design/campaign/quests.csv with name and description strings')

    # continuity pass: data quests that still carry a placeholder name take the campaign name
    ph = re.compile(r'questline, opening$|^Shardborn quest [AW]\d+$')
    h, rows = T[QK]; ni = h.index('name'); renamed = []
    for row in rows:
        c = CQ.get(row[0])
        if c and ph.search(row[ni]):
            nm = S.get(c.get('str_name') or f'STR_{row[0]}_NAME', c['name'])
            row[ni] = nm; renamed.append(row[0])
            for sk in ('ui/strings_data.csv', 'ui/strings.csv'):
                if ctx.edit(sk, f'STR_{row[0]}_NAME', 'text_en', nm): break
            else: ctx.string(f'STR_{row[0]}_NAME', nm, 'Quests')
    if renamed: ctx.log('continuity pass', 'QST_NAMES', 'applied', QK, f'{len(renamed)} placeholder quest names replaced with design/campaign/quests.csv names: {" ".join(renamed)}')
    # ---------------------------------------------------------------- quest steps, branches and journal (B09)
    # Writer text (m_writing, already merged) wins; the campaign first pass fills any key the writers lack.
    have = ctx.ids('ui/strings.csv') | ctx.ids('ui/strings_data.csv')
    CS = {r['str_id']: r for r in _read(ctx, 'campaign/strings_campaign.csv')}
    def pick(writer, campaign=None, screen='Quest journal'):
        campaign = writer if campaign is None else campaign
        if writer in have: return writer
        r = CS.get(campaign)
        if not r or any(t not in defined for t in TOK.findall(r['text_en'])): return ''
        ctx.string(campaign, r['text_en'], screen, 'Campaign first pass'); have.add(campaign); return campaign
    opt = lambda x: x if x in have else ''
    ref = lambda x: next((t for t in TOK.findall(x[:x.find(' (')] if ' (' in x else x) if t in defined), '')   # "ACT_X (note)" -> ACT_X
    FL, steps, branches = (_read(ctx, f'campaign/{f}.csv') for f in ('flags', 'quest_steps', 'quest_branches'))
    cnt = sorted({t for rows in (steps, branches, CQ.values(), FL) for r in rows for v in r.values() for t in TOK.findall(v or '') if t.startswith('CNT_')})
    defined.update(r['flag'] for r in FL); defined.update(cnt)
    keep = lambda v: '; '.join(x for x in re.split(r'[;,]\s*', v) if x in defined)
    for r in FL: ctx.append('world/flags.csv', dict(flg_id=r['flag'], kind='flag', set_by=keep(r['set_by']), read_by=keep(r['read_by'])))
    for c in cnt: ctx.append('world/flags.csv', dict(flg_id=c, kind='counter', set_by='', read_by=''))
    dq = ctx.ids(QK)
    steps = [st for st in steps if st['qst_id'] in dq]
    branches = [b for b in branches if b['qst_id'] in dq]
    for st in steps:
        q, o = st['qst_id'], int(st['order'])
        k = f'STR_{q}_STEP_{o:02d}'
        ctx.append('world/quest_steps.csv', dict(step_id=st['step_id'], qst_id=q, order=o, type=st['type'], target_id=ref(st['target']),
                   loc_id=ref(wmap(st['loc'])), count=st['count'], optional=st['optional'], obj_str=pick(k, st['str_id'], 'Quest objective'),
                   dir_str=opt(k + '_DIR'), jrn_str=opt(f'STR_{q}_JRN_{o:02d}')))
    for b in branches:
        k = f'STR_{b["qst_id"]}_BR_{b["branch_id"][-2:]}'
        ctx.append('world/quest_branches.csv', dict(branch_id=b['branch_id'], qst_id=b['qst_id'], label_str=pick(k, f'STR_{b["branch_id"]}', 'Dialogue choice'),
                   outcome_str=opt(k + '_OUT'), requires=b['requires'], flags_set=b['flags_set'], approval=b['approval'], reputation=b['reputation']))
    for row in T[QK][1]:
        q = row[0]
        for s in ('OFFER', 'DONE', 'JOURNAL'): ctx.edit(QK, q, s.lower() + '_str', pick(f'STR_{q}_{s}'))
        pick(f'STR_{q}_NAME', screen='Data name'); pick(f'STR_{q}_DESC', screen='Data description')
    for sid in CS:
        if sid.startswith('STR_RAD_') and sid.endswith('_NAME'): pick(sid, screen='Quest name')
    ctx.log('B09', 'QUEST_STEPS', 'applied', 'world/quest_steps.csv',
            f'{len(steps)} quest steps and {len(branches)} branches from design/campaign, linked to writer strings (campaign text where writers have none); '
            f'quests gain offer, done and journal strings; {len(FL)} story flags and {len(cnt)} counters in world/flags.csv. No campaign steps yet for {" ".join(sorted(dq - set(CQ)))}.')
    # ---------------------------------------------------------------- other requests
    for i, r in enumerate(req):
        if i in done: continue
        a, kind, tgt = r['id'], r['request'], r['target_table']
        if a == 'ACT_BOSS_HUSH' and kind == 'new boss':
            where = 'it is in world/npcs.csv as a story actor' if hush_npc or 'ACT_BOSS_HUSH' in ctx.ids(NK) else 'it is not placed yet'
            log(a, 'skipped', 'actors/bosses.csv', f'nothing campaign data can fill: bosses.csv needs HP, Ward, resistances, MOV_ and BPH_ rows and an arena asset that the actors thread must author; {where}')
        elif a == 'ACT_BOSS_LAMPLIGHTER':
            BK = 'actors/bosses.csv'; row = next((x for x in ctx.rows(BK) if x['ACT_ID'] == a), None)
            if row is None: log(a, 'conflict', BK, 'ACT_BOSS_LAMPLIGHTER is not in actors/bosses.csv'); continue
            if 'escape' in row['Notes'].lower():
                log(a, 'skipped', BK, 'already applied: the Lamplighter notes already describe the escape'); continue
            ok = lambda t: t in defined
            q1, q2, ires = ('MQ_A2_05' if ok('MQ_A2_05') else 'the Act 2 fight'), ('MQ_A3_03' if ok('MQ_A3_03') else 'Act 3'), ('ACT_NPC_IRES' if ok('ACT_NPC_IRES') else 'Captain Ires')
            note = f'Escapes at 30% HP in {q1} (counts as defeated for drops); returns unmasked in {q2} at level 76 as Captain Ires ({ires}) with her sidearm. Rematch stats pending (actors thread)'
            ctx.edit(BK, a, 'Notes', (row['Notes'] + '; ' if row['Notes'] else '') + note)
            log(a, 'applied', BK, 'escape at 30% HP and the unmasked rematch added to the Lamplighter notes; no extra boss row, so the plan\'s 40-boss count holds and rematch stats are left to the actors thread')
        elif a == 'FAC_SALVAGERS':
            FK = 'actors/factions.csv'; rows = ctx.rows(FK)
            cur = next(x['Questline length'] for x in rows if x['FAC_ID'] == a)
            other = sum(int(x['Questline length']) for x in rows if x['FAC_ID'] != a and x['Questline length'].isdigit())
            n = sum(1 for x in CQ.values() if x['line'] == a)
            if cur == str(n): log(a, 'skipped', FK, f'already applied: questline length is {n}')
            elif other + n == 60:
                ctx.edit(FK, a, 'Questline length', n); log(a, 'applied', FK, f'questline length {cur} to {n}, so the five lines total the plan\'s 60 (plan 5.5)')
            else: log(a, 'conflict', FK, f'setting {n} would make the five lines total {other + n}, not the plan\'s 60; kept {cur}')
        elif a == 'QST_CHOIR_01':
            if a not in ctx.ids(QK):
                log(a, 'skipped', QK, 'already applied: QST_CHOIR_01 is not in data/world/quests.csv'); continue
            if 'QST_CH_01' not in ctx.ids(QK):
                log(a, 'conflict', QK, 'QST_CH_01 is not in data/world/quests.csv, so the Choir Archivist unlock cannot move to it; QST_CHOIR_01 kept'); continue
            n = 0
            for k, (h, rr) in T.items():
                for row in rr:
                    for j in range(1, len(row)):
                        if 'QST_CHOIR_01' in row[j]: row[j] = row[j].replace('QST_CHOIR_01', 'QST_CH_01'); n += 1
            T[QK][1] = [x for x in T[QK][1] if x[0] != a]
            T['ui/strings_data.csv'][1] = [x for x in T['ui/strings_data.csv'][1] if x[0] != 'STR_QST_CHOIR_01_NAME']
            log(a, 'applied', QK, f'dropped the duplicate QST_CHOIR_01 and pointed its {n} references (Choir Archivist stock unlock) at QST_CH_01')
        elif a == 'REG_U':
            RK = 'world/regions.csv'
            ents = sorted(x for x in W if x.startswith('LOC_UV_ENTRY_'))
            if not ents: log(a, 'conflict', RK, 'design/world/locations.csv has no Undervault entries to name'); continue
            parts = []
            for e in ents:
                w = W[e]; parts.append(f'{w["name"]}, {e}' if e in defined else w['name'])
            regs = [W[e]['region'] for e in ents]
            note = f'Underground layer under {len(ents)} regions ({", ".join(regs)}; plan 3.7). Entries: ' + '; '.join(parts)
            cur = next(x['notes'] for x in ctx.rows(RK) if x['reg_id'] == a)
            if cur == note: log(a, 'skipped', RK, 'already applied: REG_U notes name the three entries'); continue
            ctx.edit(RK, a, 'notes', note)
            log(a, 'applied', RK, f'REG_U notes now say the Undervault lies under {", ".join(regs)} with entries {", ".join(ents)}, as in design/world')
        elif a == 'UI_PORTRAIT_*':
            spk = set()
            for d in _read(ctx, 'campaign/dialogue_outline.csv'):
                spk.update(s for s in d['speakers'].split('; ') if s.startswith('ACT_NPC_'))
            have = ctx.ids(NK); n = 0
            for s in sorted(spk & have):
                n += ctx.edit(NK, s, 'portrait', 'UI_PORTRAIT_' + s[len('ACT_NPC_'):])
            miss = len(spk - have)
            log(a, 'applied', 'assets/asset_hooks.csv', f'{n} speaking ACT_NPC actors got a UI_PORTRAIT_ hook in a new world/npcs.csv portrait column, which link.py registers in asset_hooks.csv' + (f'; {miss} speakers are not in world/npcs.csv' if miss else ''))
        elif a == 'CIN_*':
            cin = [x['cin_id'] for x in _read(ctx, 'cinematics/cinematics.csv')]
            cells = ' '.join(c for h, rr in T.values() for row in rr for c in row)
            have = sum(1 for c in cin if f'ANIM_{c}' in cells)
            if cin and have == len(cin): log(a, 'skipped', 'assets/asset_hooks.csv', f'already applied: all {len(cin)} ANIM_CIN_ hooks are in data')
            else: log(a, 'skipped', 'assets/asset_hooks.csv', f'owned by design/cinematics (its data-requests.csv lists the ANIM_CIN_ and SFX_CIN_ hooks per scene, {have} of {len(cin)} in data now); left to that merge so the hooks are not added twice')
        elif tgt.startswith(('design/', 'production')):
            owner = 'production' if tgt.startswith('production') else '/'.join(tgt.split(' ')[0].split('/')[:2])
            log(a, 'skipped', tgt, f'outside data/: owned by {owner}')
        elif a == 'ITM_KEY_*':
            log(a, 'skipped', 'items/', 'nothing concrete to apply: the request proposes the ITM_KEY_ family without listing each key, its quest or its name; the items thread defines them and quest steps name keys in plain text until then')
        else:
            log(a, 'skipped', tgt, f'nothing to apply: {kind} request not handled by the campaign merge')
