import json,re,os,sys,collections
R='/home/user/diaithirrpg'
prices=json.load(open(R+'/content/economy/kubejs/data/diaithir/prices.json'))
ids=set(prices)
tok=re.compile(r'[a-z0-9_.\-]+:[a-z0-9_./\-]+')
skip={'prices.json','tech_items.json','REGISTRY_DUMP.json','MERGE_TABLE.json','MERGE_TABLE.csv','id_migration.json'}
def cat(p):
    p=p.lower()
    for k,c in (('/recipe','recipe'),('/recipes','recipe'),('vendor','vendor'),('loot','loot'),('quest','quest'),('modonomicon','codex'),('library','codex'),('/tags/','tag'),('spoilage','spoil'),('integration','bridge'),('cuisine','cuisine'),('/tech','tech')):
        if k in p: return c
    return 'other'
use=collections.defaultdict(lambda: collections.Counter())
n=0
for root,d,fs in os.walk(R+'/content'):
    if '.git' in root: continue
    for f in fs:
        if f in skip or not f.endswith(('.json','.js','.csv','.tsv','.md','.snbt','.txt','.zs','.mcfunction')): continue
        p=os.path.join(root,f)
        try:
            if os.path.getsize(p)>8e6: continue
            t=open(p,errors='ignore').read()
        except: continue
        c=cat(p); n+=1
        for m in set(tok.findall(t)):
            if m in ids: use[m][c]+=1
print('files',n,file=sys.stderr)
out={i:dict(use[i]) for i in ids}
json.dump(out,open('/tmp/ir/uses.json','w'))
none=[i for i in ids if not out[i]]
print(len(ids),'zero-use',len(none))
cc=collections.Counter(i.split(':')[0] for i in none)
print(cc.most_common(40))
