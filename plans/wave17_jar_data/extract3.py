# Read-only dump from the resolved pack jars: merged en_us lang, item/block ids, and recipe/loot/tag JSON as one jsonl. Usage: extract3.py OUTDIR
import zipfile, sys, os, json, re
out = sys.argv[1]
jars = sorted(v for v in json.load(open('E:/wave17_extract/resolved.json')).values() if v)
os.makedirs(out, exist_ok=True)
dj = open(out + '/data.jsonl', 'w', encoding='utf-8')
lang, ids, rows, n_data = {}, {'item': set(), 'block': set()}, [], 0
rx = re.compile(r'^data/([^/]+)/(recipes?|loot_tables?|tags)/(.+)\.json$')
mx = re.compile(r'^assets/([^/]+)/(models/item|blockstates)/(.+)\.json$')
for j in jars:
    jn = os.path.basename(j)
    try:
        z = zipfile.ZipFile(j)
    except Exception as e:
        print('BAD', jn, e)
        continue
    for n in z.namelist():
        if n.startswith('assets/') and n.endswith('/lang/en_us.json'):
            ns = n.split('/')[1]
            try:
                d = json.loads(z.read(n).decode('utf-8-sig'))
            except Exception as e:
                print('LANGERR', jn, n, e)
                continue
            lang.setdefault(ns, {}).update(d)
            rows.append((jn, ns, len(d)))
            continue
        m = mx.match(n)
        if m:
            ids['item' if m[2] == 'models/item' else 'block'].add(m[1] + ':' + m[3])
            continue
        m = rx.match(n)
        if m:
            row = {'jar': jn, 'ns': m[1], 'kind': m[2], 'path': m[3], 'json': z.read(n).decode('utf-8-sig', 'replace')}
            dj.write(json.dumps(row, ensure_ascii=False) + '\n')
            n_data += 1
dj.close()
for ns, d in lang.items():
    for k in d:
        m = re.match(r'^(item|block)\.([^.]+)\.(.+)$', k)
        if m and m[2] == ns and not m[3].endswith(('.desc', '.tooltip')):
            ids[m[1]].add(ns + ':' + m[3].replace('.', '/'))
json.dump(lang, open(out + '/lang_en_us.json', 'w', encoding='utf-8'), ensure_ascii=False)
for k in ids:
    open(f'{out}/ids_{k}.txt', 'w').write('\n'.join(sorted(ids[k])))
open(out + '/lang_sources.tsv', 'w').write('\n'.join('\t'.join(map(str, r)) for r in rows))
print(len(rows), 'lang files', len(lang), 'ns', len(ids['item']), 'item ids', len(ids['block']), 'block ids', n_data, 'data files')
