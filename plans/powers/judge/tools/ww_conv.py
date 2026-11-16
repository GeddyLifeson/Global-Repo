import sys,json,gzip
sys.path.insert(0,'/tmp/s'); import flat
res={}
for l in gzip.open('/tmp/s/ww_raw.jsonl.gz','rt',encoding='utf-8'):
    try: t,w=json.loads(l)
    except Exception: continue
    res[t]=flat.flat(w)[:12000]
json.dump({'pages':res,'redirects':{}},gzip.open('/tmp/s/ww.json.gz','wt',encoding='utf-8'),ensure_ascii=False); print(len(res))
