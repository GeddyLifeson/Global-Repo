import json,pathlib
d=pathlib.Path(__file__).parent
rows_in={}
for l in open(d/'in.jsonl'):
    o=json.loads(l); rows_in[o['id']]=o
rows=[]
for l in open(d/'out.jsonl'):
    o=json.loads(l); t=o['text'].strip().strip('"'); r=rows_in.get(o['id'])
    if r and 25<=len(t.split())<=55 and '\u2014' not in t: rows.append([r['name'],'being',r['age'],'bosses',t])
json.dump(rows,open('/mnt/project-files/library-sync/diaithir-bosses.json','w'),ensure_ascii=False)
print(len(rows),'of',len(rows_in))
