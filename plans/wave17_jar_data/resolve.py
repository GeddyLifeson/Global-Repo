# Resolve pack jar names (from the packwiz index) to local files; search extra roots for the rest.
import os,sys,json
names=[l.strip() for l in open('E:/wave17_extract/pack_jar_names.txt',encoding='utf-8') if l.strip()]
pri=['mods_wave17_backup','mods','mods_wave21','mods_wave22','disabled-stale','mods_client_only','mods_dupes22','mods_wave20_pre']
idx={}
def scan(root,deep):
    for dp,dn,fn in os.walk(root):
        for f in fn:
            if f.endswith('.jar'): idx.setdefault(f,os.path.join(dp,f))
        if not deep: dn[:]=[]
for d in pri: scan('C:/MCTestServer/'+d,False)
for r in ['C:/Prism','C:/DiaithirServer','C:/MCTestServer/pack_push/repo/mods','C:/MCTestServer/pack_push/repo/client','C:/MCTestServer/pack_push/repo/diaithir','E:/diaithir-ports-build']:
    if os.path.isdir(r): scan(r,True)
res={n:idx.get(n) for n in names}
json.dump(res,open('E:/wave17_extract/resolved.json','w'),indent=0)
print(sum(1 for v in res.values() if v),'found',[n for n,v in res.items() if not v])
