# Direct-parallel Haiku 5.5 caller for a job folder (watcher fallback): python3 -I spec_run.py JOBDIR. Key read from file, never printed.
import json,sys,pathlib,urllib.request,concurrent.futures as cf
job=pathlib.Path(sys.argv[1]); key=open('/mnt/project-files/compute/secrets/anthropic_key').read().strip()
def call(r):
    b={"model":"claude-haiku-5-5","max_tokens":2500,"thinking":{"type":"disabled"},"system":[{"type":"text","text":r['system'],"cache_control":{"type":"ephemeral"}}],"messages":[{"role":"user","content":r['prompt']}]}
    q=urllib.request.Request('https://api.anthropic.com/v1/messages',json.dumps(b).encode(),{'x-api-key':key,'anthropic-version':'2023-06-01','content-type':'application/json'})
    for t in range(3):
        try:
            d=json.load(urllib.request.urlopen(q,timeout=120)); return {"id":r['id'],"text":''.join(x.get('text','') for x in d['content']),"usage":d.get('usage')}
        except Exception as e: err=str(e)
    return {"id":r['id'],"error":err}
rows=[json.loads(l) for l in open(job/'in.jsonl')]
with cf.ThreadPoolExecutor(24) as ex, open(job/'out.jsonl','w') as f:
    for o in ex.map(call,rows): f.write(json.dumps(o)+'\n')
print('done',len(rows))
