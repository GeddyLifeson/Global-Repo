import json,pathlib
d=pathlib.Path(__file__).parent
meta={json.loads(l)['id']:json.loads(l) for l in open(d/'in.jsonl')}
out=pathlib.Path('/mnt/project-files/library-sync/alexs-caves.json')
rows=json.load(open(out)) if out.exists() else []
have={r[0] for r in rows}
add=0
for l in open(d/'out.jsonl'):
    o=json.loads(l); t=o['text'].strip().strip('"'); m=meta[o['id']]
    if m['name'] not in have and 6<=len(t.split())<=90 and '\u2014' not in t and m['name']:
        rows.append([m['name'],m['kind'],4,m['locale'],t]); have.add(m['name']); add+=1
json.dump(rows,open(out,'w'),ensure_ascii=False)
print(add,'added;',len(rows),'rows in alexs-caves.json')
