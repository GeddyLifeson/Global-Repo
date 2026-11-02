import json,pathlib,re
d=pathlib.Path(__file__).parent
info={}
for l in open(d/'in.jsonl'):
    o=json.loads(l); info[o['id']]=o
rows=json.load(open(d/'base.json'))
for l in open(d/'out.jsonl'):
    o=json.loads(l); t=o['text'].strip().strip('"')
    n=len(t.split())
    if o['id'] in info and 20<=n<=45 and re.search(r'\d',t) and '\u2014' not in t:
        kind='concept' if o['id'].split(':')[1] in ('stamina','parry','roll','age') else 'item'
        rows.append([info[o['id']]['name'],kind,1,'combat',t])
json.dump(rows,open('/mnt/project-files/library-sync/combat.json','w'),ensure_ascii=False)
print(len(rows),'rows of',len(info)+1)
