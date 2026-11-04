# S6979 Builds the PC judging queue: ~20k lead pages (strongest Haiku power evidence + weapon/armor/vehicle candidates), minus all in-thread shard pages.
"""python3 pc_priority.py OUT.jsonl.gz [N=20000]   (run in the cloud; needs /mnt/project-files). Row: {"id","text"} sorted by priority."""
import json, sys, re, glob, gzip, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from judge_pages import iter_leads, junk
J = '/mnt/project-files/plans/powers/judge'
SH = sys.argv[1] == '--shards'
N = int(sys.argv[2]) if len(sys.argv) > 2 and not SH else 20000
skip = {json.loads(l)['id'] for f in glob.glob(f'{J}/inthread/shard_*.jsonl') for l in open(f, encoding='utf-8')}
score = {}
other = set()
for l in open(f'{J}/haiku_partial_results.jsonl', encoding='utf-8'):
    d = json.loads(l)
    if d.get('b') == 1 and d.get('p'):
        ms = [p['m'] for p in d['p']]
        score[d['id']] = max(ms) * 10 + len(ms) + sum(p['c'] == 'h' for p in d['p']) * 3
    elif d.get('b') == 0: other.add(d['id'])
GEAR = re.compile(r'\b(sword|blade|katana|axe|spear|bow|staff|hammer|gun|rifle|cannon|blaster|weapon|armou?r|shield|helmet|gauntlet|suit|ship|starship|spacecraft|battleship|cruiser|carrier|tank|mech|mecha|robot suit|vehicle|aircraft|airship|fighter|jet|train|car|truck|submarine|warship|craft|zeppelin|dreadnought|gundam|walker)\b', re.I)
texts, gear = {}, []
for w, i, t in iter_leads():
    k = f'{w}|{i}'
    if k in skip or junk(t): continue
    if k in score: texts[k] = t
    elif GEAR.search(t[:160]) and k not in score: gear.append((k, t))
if SH:
    first, count = int(sys.argv[2]), int(sys.argv[3])
    qids = {json.loads(l)['id'] for l in gzip.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../plans/powers/pcrun/priority.jsonl.gz'), 'rt', encoding='utf-8')}
    hint = {}
    for l in open(f'{J}/haiku_partial_results.jsonl', encoding='utf-8'):
        d = json.loads(l)
        if d.get('b') == 1 and not d.get('p'): hint[d['id']] = len(d.get('x') or [])
        elif d.get('b') == 0: hint.setdefault(d['id'], -1)
    judged = set(hint) | set(score)
    g2, b2, u2 = [], [], []
    for w, i, t in iter_leads():
        k = f'{w}|{i}'
        if k in skip or k in qids or k in score or junk(t): continue
        if GEAR.search(t[:160]): g2.append((k, t))
        elif hint.get(k, -2) >= 0: b2.append((hint[k], k, t))
        elif k not in judged: u2.append((k, t))
    b2.sort(key=lambda x: -x[0])
    seq = g2 + [(k, t) for _, k, t in b2] + u2
    print('gear', len(g2), 'beings-no-power', len(b2), 'unjudged', len(u2))
    for n in range(count):
        ch = seq[n * 250:(n + 1) * 250]
        with open(f'{J}/inthread/shard_{first + n:02d}.jsonl', 'w', encoding='utf-8') as o:
            for k, t in ch: o.write(json.dumps({'id': k, 'text': t[:700]}, ensure_ascii=False) + '\n')
    sys.exit()
beings = sorted(texts, key=lambda k: -score[k])
nb = min(len(beings), int(N * 0.6))
rows = [(k, texts[k]) for k in beings[:nb]]
# interleave so the router meets both kinds early
gear = gear[:N - nb]
rows_all = []
b, g = list(rows), list(gear)
while b or g:
    for _ in range(3):
        if b: rows_all.append(b.pop(0))
    if g: rows_all.append(g.pop(0))
with gzip.open(sys.argv[1], 'wt', encoding='utf-8') as o:
    for k, t in rows_all[:N]: o.write(json.dumps({'id': k, 'text': t[:1500]}, ensure_ascii=False) + '\n')
print('beings', nb, 'gear candidates', len(gear), 'total', min(len(rows_all), N), 'skipped shard pages', len(skip))
