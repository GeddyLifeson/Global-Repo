# Orphan roles and J16 lang gaps from the extracted wave17 jar data (nothing invented: a role is only emitted when a recipe, loot table or tag in the jars names the id).
# Usage: roles.py OUT_DIR ORPHANS_CSV OUTDIR_RESULT
import json, sys, csv, collections
D, orph_f, R = sys.argv[1:4]
orph = [r['id'] for r in csv.DictReader(open(orph_f, encoding='utf-8-sig'))]
want = set(orph)
made = collections.defaultdict(list)     # id -> [(src, ingredients)]
used = collections.defaultdict(list)     # id -> [(src, result)]
loot = collections.defaultdict(list)     # id -> [loot table src]
tags = {}                                # tag id -> [values]
recs = []

def walk_ing(x, acc):
    if isinstance(x, str):
        acc.add(x)
    elif isinstance(x, list):
        for e in x: walk_ing(e, acc)
    elif isinstance(x, dict):
        for k in ('item', 'id'):
            if isinstance(x.get(k), str): acc.add(x[k])
        if isinstance(x.get('tag'), str): acc.add('#' + x['tag'])
        for k in ('ingredients', 'ingredient', 'items', 'key', 'base', 'addition', 'template', 'input', 'inputs'):
            if k in x: walk_ing(x[k] if k != 'key' else list(x['key'].values()), acc)

def walk_loot(x, acc):
    if isinstance(x, dict):
        if x.get('type', '').endswith('item') and isinstance(x.get('name'), str): acc.add(x['name'])
        for v in x.values(): walk_loot(v, acc)
    elif isinstance(x, list):
        for e in x: walk_loot(e, acc)

for line in open(D + '/data.jsonl', encoding='utf-8'):
    r = json.loads(line)
    try: j = json.loads(r['json'], strict=False)
    except Exception: continue
    src = f"{r['jar']}:data/{r['ns']}/{r['kind']}/{r['path']}.json"
    if r['kind'].startswith('tag') or r['kind'] == 'tags':
        if r['path'].startswith('items/') or r['path'].startswith('item/') or r['path'].startswith('blocks/') or r['path'].startswith('block/'):
            tid = r['ns'] + ':' + r['path'].split('/', 1)[1]
            tags.setdefault(tid, []).extend(v if isinstance(v, str) else v.get('id', '') for v in j.get('values', []))
    elif r['kind'].startswith('loot'):
        acc = set(); walk_loot(j, acc)
        for i in acc & want: loot[i].append(src)
    else:
        res = j.get('result') or j.get('output') or j.get('results')
        rid = set(); walk_ing(res, rid)
        ing = set(); walk_ing({k: v for k, v in j.items() if k not in ('result', 'output', 'results', 'type', 'category', 'group')}, ing)
        for i in rid & want: made[i].append((src, sorted(ing)))
        recs.append((src, rid, ing))

def expand(t, seen=None):
    seen = seen or set(); out = set()
    for v in tags.get(t, []):
        if v.startswith('#'):
            if v[1:] not in seen: seen.add(v[1:]); out |= expand(v[1:], seen)
        else: out.add(v)
    return out
tagmem = collections.defaultdict(list)
for t in list(tags):
    for v in expand(t):
        if v in want: tagmem[v].append(t)
tagused = collections.defaultdict(list)
for src, rid, ing in recs:
    for i in ing:
        if i in want: used[i].append((src, sorted(rid)))
        elif i.startswith('#'):
            for m in expand(i[1:]) & want: tagused[m].append((src, i, sorted(rid)))

out = csv.writer(open(R + '/ITEM_ROLES_ORPHANS_RESOLVED.csv', 'w', newline='', encoding='utf-8'))
out.writerow(['id', 'role_class', 'role', 'evidence'])
closed = 0; still = []
for i in orph:
    parts = []; ev = []
    if made[i]:
        s, ing = made[i][0]
        parts.append('Crafted from ' + ', '.join(ing[:8])); ev.append(s)
    if loot[i]:
        parts.append('Dropped or found via loot table ' + loot[i][0].split(':', 1)[1].split('/', 3)[-1].removesuffix('.json')); ev.append(loot[i][0])
    if used[i]:
        s, res = used[i][0]
        parts.append('Ingredient in ' + ', '.join(res[:4])); ev.append(s)
    elif tagused[i]:
        s, t, res = tagused[i][0]
        parts.append(f'Used via tag {t} in ' + ', '.join(res[:4])); ev.append(s)
    if parts:
        cls = 'crafted' if made[i] else 'loot' if loot[i] else 'ingredient'
        out.writerow([i, cls, '; '.join(parts), ' | '.join(ev)]); closed += 1
    else: still.append(i)
open(R + '/ITEM_ROLES_ORPHANS_STILL_OPEN.txt', 'w').write('\n'.join(still))
by = collections.Counter(i.split(':')[0] for i in still)
print(len(orph), 'orphans', closed, 'with a jar-data role', len(still), 'still open', by.most_common(8))
