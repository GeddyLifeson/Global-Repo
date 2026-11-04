# S6979 Builds the PC judging queue: ~20k lead pages (strongest Haiku power evidence + weapon/armor/vehicle candidates), minus all in-thread shard pages.
"""python3 pc_priority.py OUT.jsonl.gz [N=20000]   (run in the cloud; needs /mnt/project-files). Row: {"id","text"} sorted by priority."""
import json, sys, re, glob, gzip, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from judge_pages import iter_leads, junk
J = '/mnt/project-files/plans/powers/judge'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
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
