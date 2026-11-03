# Merges atmo job output into specs/<id>.json under key "atmo". python3 -I merge_atmo.py JOBDIR
import json,sys,pathlib,sqlite3
J=pathlib.Path(sys.argv[1]); O=pathlib.Path('/mnt/project-files/planets/specs')
s=sqlite3.connect('file:/mnt/attach/project-files/codex-store/library.sqlite?mode=ro',uri=True)
PART=set("ash white_ash snowflake spore_blossom_air crimson_spore warped_spore cherry_leaves pale_oak_leaves end_rod soul glow firefly sculk_soul none".split())
ok=bad=0
for l in open(J/'out.jsonl'):
    o=json.loads(l)
    try:
        t=o['text']; a=json.loads(t[t.index('{'):t.rindex('}')+1])
        a['particles']=[p for p in a.get('particles',[]) if p.get('type') in PART-{'none'}][:3]
        if not s.execute("select 1 from entry where id=?",(a.get('why_entry'),)).fetchone(): a['grounded']=False
        f=O/(o['id']+'.json'); sp=json.loads(f.read_text()); sp['atmo']=a; f.write_text(json.dumps(sp,indent=1)); ok+=1
    except Exception as e: bad+=1; print(o['id'],e)
print(ok,bad)
