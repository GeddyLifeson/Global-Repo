import json,pathlib
d=pathlib.Path(__file__).parent
names={json.loads(l)['id']:json.loads(l)['name'] for l in open(d/'in.jsonl')}
ages=json.load(open(d/'ages.json'))
rows=[]
for l in open(d/'out.jsonl'):
    o=json.loads(l); t=o['text'].strip().strip('"')
    if 8<=len(t.split())<=18 and '—' not in t: rows.append([names[o['id']],'item',ages.get(names[o['id']],3),'gear_lore',t])
json.dump(rows,open('/mnt/project-files/library-sync/gear_lore.json','w'),ensure_ascii=False)
print(len(rows),'of',len(names))
