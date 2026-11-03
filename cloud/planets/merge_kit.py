# Validates kit job output against the menus and stores it as specs/<id>.json["kit"]. python3 -I merge_kit.py JOBDIR
import json,sys,pathlib,re
J=pathlib.Path(sys.argv[1]); O=pathlib.Path('/mnt/project-files/planets/specs')
src=open('/mnt/project-files/planets/kit_jobs.py').read()
def menu(n): return set(re.search(n+r'="([^"]*)"\.split\(\)',src).group(1).split())
BASES,LOGS,LEAVES,UNDER,FLOW=[menu(n) for n in ('BASES','LOGS','LEAVES','UNDER','FLOW')]
ORES={'coal','iron','copper','gold','redstone','lapis','diamond'}
ok=bad=0
for l in open(J/'out.jsonl'):
    o=json.loads(l)
    try:
        t=o['text']; k=json.loads(t[t.index('{'):t.rindex('}')+1])
        k['trees']=[x for x in k.get('trees',[]) if x.get('base') in BASES and x.get('log') in LOGS and x.get('leaves') in LEAVES][:3]
        k['undergrowth']=[x for x in k.get('undergrowth',[]) if x.get('block') in UNDER][:3]
        k['flowers']=[x for x in k.get('flowers',[]) if x in FLOW][:4]
        k['ores']={a:max(0.0,min(3.0,float(v))) for a,v in k.get('ores',{}).items() if a in ORES}
        k['density']=max(0.2,min(2.0,float(k.get('density',1.0))))
        f=O/(o['id']+'.json'); sp=json.loads(f.read_text()); sp['kit']=k; f.write_text(json.dumps(sp,indent=1)); ok+=1
    except Exception as e: bad+=1; print(o['id'],repr(o.get('error',e))[:80])
print(ok,bad)
