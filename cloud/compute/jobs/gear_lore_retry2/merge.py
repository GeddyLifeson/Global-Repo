import json,pathlib,re
d=pathlib.Path(__file__).parent
JOB='gear_lore'; LIB='gear_lore.json'
orig=pathlib.Path('/mnt/project-files/compute/jobs')/JOB
info={}
for l in open(orig/'in.jsonl'):
    o=json.loads(l); info[o['id']]=o
lib=pathlib.Path('/mnt/project-files/library-sync')/LIB
rows=json.load(open(lib)) if lib.exists() else []
have={r[0] for r in rows}
OK={'gear_lore':lambda n,t:8<=n<=18,'relics_lore':lambda n,t:8<=n<=20,
    'combat_lore':lambda n,t:20<=n<=45 and re.search(r'\d',t),'diaithir-bosses_lore':lambda n,t:25<=n<=55}[JOB]
ages=json.load(open(orig/'ages.json')) if (orig/'ages.json').exists() else {}
added=0
for l in open(d/'out.jsonl'):
    o=json.loads(l); t=o['text'].strip().split('\n')[0].strip().strip('"'); r=info.get(o['id'])
    if not r or r['name'] in have or '\u2014' in t or not OK(len(t.split()),t): continue
    if JOB=='gear_lore': row=[r['name'],'item',ages.get(r['name'],3),'gear_lore',t]
    elif JOB=='relics_lore': row=[r['name'],'item',r['age'],'relics',t+' '+r['mech']]
    elif JOB=='combat_lore': row=[r['name'],'concept' if r['id'].split(':')[1] in ('stamina','parry','roll','age') else 'item',1,'combat',t]
    else: row=[r['name'],'being',r['age'],'bosses',t]
    rows.append(row); have.add(r['name']); added+=1
json.dump(rows,open(lib,'w'),ensure_ascii=False)
print(added,'added;',len(rows),'rows in',lib.name)
