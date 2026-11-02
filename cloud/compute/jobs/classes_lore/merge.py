import json,pathlib,re
d=pathlib.Path(__file__).parent
rd=d.parent/(d.name+'_retry')
meta={}
for l in open(d/'in.jsonl'):
    o=json.loads(l); meta[o['id']]=o
outs={}
for f in (d/'out.jsonl', rd/'out.jsonl'):
    if f.exists():
        for l in open(f):
            o=json.loads(l); outs[o['id']]=o
BAN=re.compile(r'\b(fian|fianna|sleagh|ceilg|cleirech)\b',re.I)
def retry(bad):
    if not bad: return
    rd.mkdir(exist_ok=True)
    with open(rd/'in.jsonl','w') as f:
        for i in bad:
            r=dict(meta[i]); r['system']=r['system']+' Never use the words Fian, Fianna, Sleagh, Ceilg or Cleirech; say warrior, archer, hunter or healer instead.'; f.write(json.dumps(r,ensure_ascii=False)+chr(10))
    (rd/'README').write_text('Retry rows of '+d.name+': rows that failed the check (modern Irish class words or length). Same format; merge.py of '+d.name+' reads out.jsonl here too.'+chr(10))
rows=[]; bad=[]
for i,m in meta.items():
    o=outs.get(i); t=o['text'].strip().strip('"') if o else ''
    if o and 8<=len(t.split())<=18 and '\u2014' not in t and not BAN.search(t) and not BAN.search(m['name']): rows.append([m['name'],'item',0,'classes_lore',t])
    else: bad.append(i)
retry(bad)
json.dump(rows,open('/mnt/project-files/library-sync/classes_lore.json','w'),ensure_ascii=False)
print(len(rows),'of',len(meta),'; retry rows',len(bad))
