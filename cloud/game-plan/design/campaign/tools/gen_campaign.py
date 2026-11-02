#!/usr/bin/env python3
"""Builds the campaign tables from seeds/*.json. Never hand-edit the CSVs it writes.
Usage: python3 design/campaign/tools/gen_campaign.py   (exit 1 on errors)"""
import csv, glob, json, os, re, sys, collections
C = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # design/campaign
D = os.path.join(os.path.dirname(os.path.dirname(C)), 'data')           # game-plan/data
TOK = re.compile(r'(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![a-z0-9])')
# Quest Ember = share x kindle cost at the region band midpoint (SIM-11); hub quests use their own level
EMBER_SHARE = {'Main': 0.5, 'Shardborn': 0}

def load(p):
    with open(p, newline='', encoding='utf-8') as f: return list(csv.reader(f))

# IDs the data folder defines (first column of every table, plus loot table keys)
known = set()
for p in glob.glob(os.path.join(D, '*', '*.csv')):
    if p.endswith(('world/quests.csv', 'world/npcs.csv', 'world/locations.csv')): continue   # the data merge fills these from our requests; counting them would drop the requests on the next run
    rows = load(p)
    known.update(r[0] for r in rows[1:] if r)
# Locations placed by the world thread count as known
WL = os.path.join(os.path.dirname(C), 'world', 'locations.csv')
if os.path.exists(WL): known.update(r[0] for r in load(WL)[1:] if r)
regions = {r[0]: (int(r[3]), int(r[4])) for r in load(os.path.join(D, 'world', 'regions.csv'))[1:]}
kindle = {int(r[0]): int(r[3]) for r in load(os.path.join(D, 'actors', 'level_curve.csv'))[1:]}
prefixes = {'_'.join(k.split('_')[:n]) for k in known for n in range(1, k.count('_') + 1)}

def w(name, header, rows):
    with open(os.path.join(C, name), 'w', newline='', encoding='utf-8') as f:
        cw = csv.writer(f); cw.writerow(header); cw.writerows(rows)

def j(x): return '; '.join(x) if isinstance(x, list) else ('; '.join(f'{k} {v:+d}' for k, v in x.items()) if isinstance(x, dict) else str(x or ''))
def mc(s): return max(8, round(len(s) * 1.4))
def pdesc(s):   # player-facing description: drop designer flag IDs such as (FLG_TRUTH_HIDDEN)
    s = re.sub(r'\s*\((?:FLG_[A-Z0-9_]+(?:,\s*|\s+and\s+|\s+or\s+)?)+\)', '', s)
    return re.sub(r'\s*\bFLG_[A-Z0-9_]+\b', '', s)

quests = []
for p in sorted(glob.glob(os.path.join(C, 'seeds', '*.json'))):
    b = os.path.basename(p)
    if b in ('cinematics.json', 'companion_approval.json', 'radiant.json', 'system_flags.json'): continue
    for q in json.load(open(p)): q['_file'] = b; quests.append(q)

err, warn = [], []
qids = [q['id'] for q in quests]
for d, n in collections.Counter(qids).items():
    if n > 1: err.append(f'duplicate quest id {d}')
qset = set(qids)
flags_set, flags_read = collections.defaultdict(set), collections.defaultdict(set)
new_ids = collections.defaultdict(set)
QROWS, SROWS, BROWS, RROWS, DROWS, STR = [], [], [], [], [], []

for q in quests:
    qid, typ = q['id'], q.get('type', '')
    reg, lvl = q.get('region', ''), int(q.get('level', 1) or 1)
    if reg in regions and not (regions[reg][0] - 2 <= lvl <= regions[reg][1] + 2): warn.append(f'{qid}: level {lvl} outside {reg} band')
    rw = q.get('rewards', {}) or {}
    band = regions.get(reg)
    mid = (band[0] + band[1]) // 2 if band and reg != 'REG_HUB' else lvl
    ember = int(round(EMBER_SHARE.get(typ, 0.25) * kindle[max(1, min(mid, max(kindle)))] / 50.0) * 50)
    for pr in q.get('prereq', []) or []:
        if pr.startswith(('FLG_', 'CNT_')): continue  # flag gates are allowed in prereq and are picked up as flags read
        if pr not in qset and pr not in known: err.append(f'{qid}: prereq {pr} is not a quest')
    steps, br, sc = q.get('steps', []), q.get('branches', []), q.get('scenes', [])
    vo = sum(int(s.get('lines', 0) or 0) for s in sc)
    QROWS.append([qid, q.get('name', ''), typ, q.get('line', ''), q.get('act', ''), reg, lvl, q.get('giver', ''), j(q.get('prereq', [])),
                  j(q.get('locations', [])), q.get('summary', ''), q.get('journal', ''), ember, j(rw.get('items', [])), j(rw.get('rep', {})),
                  j(q.get('enemies', [])), q.get('lore_item', ''), len(steps), len(br), len(sc), vo, f'STR_{qid}_NAME', f'STR_{qid}_DESC'])
    STR += [[f'STR_{qid}_NAME', 'Quest name', q.get('name', ''), mc(q.get('name', '')), '', typ],
            [f'STR_{qid}_DESC', 'Quest description', pdesc(q.get('summary', '')), mc(pdesc(q.get('summary', ''))), '', typ],
            [f'STR_{qid}_JOURNAL', 'Quest journal', q.get('journal', ''), mc(q.get('journal', '')), '', 'Shown on completion']]
    for i, s in enumerate(steps, 1):
        sid = f'{qid}_S{i:02d}'
        SROWS.append([sid, qid, i, s.get('type', ''), s.get('text', ''), s.get('target', ''), s.get('loc', ''), s.get('count', 1),
                      'yes' if s.get('optional') else 'no', f'STR_{sid}'])
        STR.append([f'STR_{sid}', 'Quest objective', s.get('text', ''), mc(s.get('text', '')), '', qid])
        if len(s.get('text', '')) > 60: warn.append(f'{sid}: objective over 60 chars')
    for i, b in enumerate(br, 1):
        bid = f'{qid}_B{i:02d}'
        for f in b.get('flags', []) or []: flags_set[f].add(qid)
        BROWS.append([bid, qid, b.get('choice', ''), b.get('requires', ''), b.get('outcome', ''), j(b.get('flags', [])), j(b.get('approval', {})), j(b.get('rep', {}))])
        STR.append([f'STR_{bid}', 'Dialogue choice', b.get('choice', ''), mc(b.get('choice', '')), '', qid])
    RROWS.append([qid, 'ember', 'ITM_CUR_EMBER', ember])
    for it in rw.get('items', []) or []: RROWS.append([qid, 'item', it, 1])
    for fac, v in (rw.get('rep', {}) or {}).items(): RROWS.append([qid, 'reputation', fac, v])
    for s in sc:
        DROWS.append([f'DLG_{qid}_{s.get("id", "S")}', qid, s.get('kind', ''), j(s.get('speakers', [])), s.get('purpose', ''), s.get('lines', 0)])
    # flags read anywhere in the quest text
    blob = json.dumps({k: v for k, v in q.items() if k != 'branches'}) + ' '.join(str(b.get('requires', '')) for b in br)
    for f in re.findall(r'FLG_[A-Z0-9_]+', blob): flags_read[f].add(qid)

# System and writing-scene flags (companion approval, faction joins, Ostra state): seeds/system_flags.json
SYSF = os.path.join(C, 'seeds', 'system_flags.json')
for sf in (json.load(open(SYSF)) if os.path.exists(SYSF) else []):
    if not re.fullmatch(r'FLG_[A-Z0-9_]+', sf['flag']): err.append(f"system flag {sf['flag']} is not a flag ID")
    flags_set[sf['flag']].update(sf.get('set_by', []))
    flags_read[sf['flag']].update(sf.get('read_by', []))

# Reference check: every UPPER_SNAKE token must resolve to data, a campaign quest, or a requested new ID
campaign_defined = qset | set(flags_set) | set(flags_read)
for row in QROWS + SROWS + BROWS + RROWS + DROWS:
    for c in row[1:]:
        for t in TOK.findall(str(c)):
            if t in known or t in campaign_defined or t in prefixes: continue
            if t.startswith(('FLG_', 'CNT_', 'CIN_', 'DLG_', 'STR_')): continue
            if t.startswith(('LOC_', 'ACT_')): new_ids[t].add(row[0].split('_S')[0].split('_B')[0]); continue
            if t.startswith(('ITM_', 'MQ_', 'QST_', 'SQ_', 'CMPQ_')): err.append(f'{row[0]}: unknown {t}')
# Flags read but never set (other than counters and ending flags set by the endings)
for f in sorted(set(flags_read) - set(flags_set)):
    warn.append(f'flag {f} read by {",".join(sorted(flags_read[f]))[:80]} but no branch sets it')

w('quests.csv', ['qst_id', 'name', 'type', 'line', 'act', 'region', 'level', 'giver', 'prereq', 'locations', 'summary', 'journal', 'ember',
                 'reward_items', 'reward_rep', 'enemies', 'lore_item', 'steps', 'branches', 'scenes', 'vo_lines', 'str_name', 'str_desc'], QROWS)
w('quest_steps.csv', ['step_id', 'qst_id', 'order', 'type', 'objective', 'target', 'loc', 'count', 'optional', 'str_id'], SROWS)
w('quest_branches.csv', ['branch_id', 'qst_id', 'choice', 'requires', 'outcome', 'flags_set', 'approval', 'reputation'], BROWS)
w('quest_rewards.csv', ['qst_id', 'kind', 'ref', 'amount'], RROWS)
w('dialogue_outline.csv', ['scene_id', 'qst_id', 'kind', 'speakers', 'purpose', 'est_lines'], DROWS)
allf = sorted(set(flags_set) | set(flags_read))
w('flags.csv', ['flag', 'set_by', 'read_by'], [[f, j(sorted(flags_set[f])), j(sorted(flags_read[f]))] for f in allf])

# Side tables
def side(name, header, keys, src):
    p = os.path.join(C, 'seeds', src)
    if not os.path.exists(p): warn.append(f'missing seeds/{src}'); return []
    data = json.load(open(p)); w(name, header, [[j(d.get(k, '')) for k in keys] for d in data]); return data
cins = json.load(open(os.path.join(C, 'seeds', 'cinematics.json')))  # briefs only; the master list is design/cinematics/cinematics.csv
side('companion_approval.csv', ['companion', 'trigger', 'delta'], ['companion', 'trigger', 'delta'], 'companion_approval.json')
rad = side('radiant_templates.csv', ['rad_id', 'name', 'shape', 'giver_pool', 'site_tags', 'target_pool', 'twists', 'objective_steps', 'reward_rule', 'repeat', 'lines_per_instance', 'bark_lines_total'],
           ['id', 'name', 'shape', 'giver_pool', 'site_tags', 'target_pool', 'twists', 'objective_steps', 'reward_rule', 'repeat', 'lines_per_instance', 'bark_lines_total'], 'radiant.json')
for r in rad: STR.append([f'STR_{r["id"]}_NAME', 'Quest name', r.get('name', ''), mc(r.get('name', '')), '', 'Radiant template'])
w('strings_campaign.csv', ['str_id', 'screen', 'text_en', 'max_chars', 'tokens', 'notes'], STR)

# Voice budget: scene lines split evenly across that scene's speakers
vo = collections.Counter()
for r in DROWS:
    sp = [s for s in r[3].split('; ') if s] or ['UNASSIGNED']
    for s in sp: vo[s] += int(r[5] or 0) / len(sp)
w('vo_budget_from_quests.csv', ['speaker', 'est_lines'], sorted([[k, round(v)] for k, v in vo.items()], key=lambda x: -x[1]))

# Data requests: new IDs the data folder must add, plus quests for world/quests.csv
REQ = []
for t in sorted(new_ids):
    REQ.append([t, 'new location' if t.startswith('LOC_') else 'new actor', 'world/locations.csv' if t.startswith('LOC_') else 'world/npcs.csv or actors/bosses.csv',
                'used by ' + j(sorted(new_ids[t])[:6])])
for q in QROWS:
    if q[0] not in known: REQ.append([q[0], 'new quest', 'world/quests.csv', f'{q[1]} | {q[2]} | {q[5]} | reward {q[13] or "Ember only"}'])
extra = os.path.join(C, 'tools', 'data_requests_manual.csv')
if os.path.exists(extra): REQ += load(extra)[1:]
w('data-requests.csv', ['id', 'request', 'target_table', 'notes'], REQ)

# Summary
types = collections.Counter(q[2] for q in QROWS)
print(f'quests {len(QROWS)} {dict(types)} | steps {len(SROWS)} | branches {len(BROWS)} | scenes {len(DROWS)} | quest VO lines {sum(int(r[5] or 0) for r in DROWS)} | flags {len(allf)} | cinematics {len(cins)} {sum(float(c.get("minutes", 0)) for c in cins):.1f} min | radiant {len(rad)} | strings {len(STR)} | data requests {len(REQ)}')
print(f'warnings {len(warn)}'); [print('  W', x) for x in warn[:40]]
print(f'errors {len(err)}'); [print('  E', x) for x in err[:60]]
sys.exit(1 if err else 0)
