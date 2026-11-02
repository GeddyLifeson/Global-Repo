import json,pathlib
d=pathlib.Path(__file__).parent
names={json.loads(l)['id']:json.loads(l)['name'] for l in open(d/'in.jsonl')}
rows=[]
for l in open(d/'out.jsonl'):
    o=json.loads(l); t=o['text'].strip().strip('"')
    if 18<=len(t.split())<=45 and '\u2014' not in t: rows.append([names[o['id']],'item',1,'tanning',t])
json.dump(rows,open('/mnt/project-files/library-sync/diaithir-tanning.json','w'),ensure_ascii=False)
print(len(rows),'of',len(names))
