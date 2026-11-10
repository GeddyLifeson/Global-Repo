import sys,re,json,subprocess
n=sys.argv[1]; parts=sys.argv[2:]
fix=f"parts/shard_{n}_fix.json"
try: cfg=json.load(open(fix))
except Exception: cfg={}
for _ in range(2):
    o=subprocess.run(["python3","tools/split.py","merge",n,*parts,fix] if cfg else ["python3","tools/split.py","merge",n,*parts],capture_output=True,text=True).stdout
    z=cfg.setdefault("z",{}); nn=cfg.setdefault("n",{})
    # no auto-z: a row with an Abilities section and no power must be read and judged by a worker (review A6)
    for m in re.finditer(r"\((\d+), \"name not in text/too long: '(.+?)(?:\\\\xa0| is | was )",o): nn[m.group(1)]=m.group(2)
    for m in re.finditer(r"\((\d+), \"name not in text/too long: \"(.+?)(?:\\\\xa0| is | was )",o): nn[m.group(1)]=m.group(2)
    json.dump(cfg,open(fix,"w"))
print(o.strip().splitlines()[0] if o.strip() else o)
