import json,os,collections
R='/home/user/diaithirrpg/content'
u=json.load(open('uses.json'))
pr=json.load(open(R+'/economy/kubejs/data/diaithir/prices.json'))
ti=json.load(open(R+'/tech_items.json'))
def age(i):
    t=ti['items'].get(i) or ti['namespaces'].get(i.split(':')[0]) or ''
    return t.split('.')[-1] if t else '?'
strong={'recipe','quest','codex','loot','cuisine'}
todo=[i for i in sorted(u) if not (set(u[i])&strong)]
print(len(todo),'of',len(u))
SYS=open('sys.txt').read()
rows=[];by=collections.defaultdict(list)
for i in todo: by[i.split(':')[0]].append(i)
for ns,l in sorted(by.items()):
    for k in range(0,len(l),30):
        ch=l[k:k+30]
        lines='\n'.join(f"{i}|age={age(i)}|price={pr[i][0]}|seen={','.join(sorted(u[i])) or 'none'}" for i in ch)
        rows.append({'id':f'{ns}-{k//30}','system':SYS,'prompt':lines})
print(len(rows),'rows')
n=500
for s in range(0,len(rows),n):
    d=f'/mnt/project-files/compute/jobs/item_roles-s{s//n:02d}'
    os.makedirs(d,exist_ok=True)
    with open(d+'/in.jsonl','w') as f:
        for r in rows[s:s+n]: f.write(json.dumps(r)+'\n')
    open(d+'/README','w').write("model: haiku\nmax_tokens 6000\nowner: item-roles thread (cmsg_01EpyoqYuwV3X4z3b4zk5pEKTr1WhEFUZyP3jxkzwwqujv)\nSource: DiaithirRPG claude/pack-v1-3 prices.json ids with no recipe/quest/codex/loot/cuisine use in content/; scan in Global-Repo plans/ITEM_ROLES.md.\nCHECK: out text is a JSON array, one object per input line, ids match exactly, role_class in the allowed list, links only from the allowed list. Failures go to item_roles-retry.\n")
