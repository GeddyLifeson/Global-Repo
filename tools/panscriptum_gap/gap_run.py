# S6972 gap_run.py: run gap-fill jobs against any OpenAI-compatible endpoint (model router, Ollama) with the same validator as gap_batch.py. Resumable.
# python3 -I gap_run.py <jobs.jsonl[.gz]> <out.jsonl> <universe> <idstart> [--url http://127.0.0.1:8788/v1] [--model NAME] [--workers 4] [--limit N] [--key KEY]
# Writes accepted entries to <out.jsonl>, rejected/failed job ids to <out.jsonl>.rejected (never retried in the same file). Run stops cleanly on Ctrl-C and resumes.
import sys,os,json,gzip,time,threading,argparse,urllib.request,urllib.error
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import gap_batch as g
ap=argparse.ArgumentParser(); ap.add_argument('jobs'); ap.add_argument('out'); ap.add_argument('universe'); ap.add_argument('idstart',type=int)
ap.add_argument('--url',default='http://127.0.0.1:8788/v1'); ap.add_argument('--model',default='auto'); ap.add_argument('--workers',type=int,default=4)
ap.add_argument('--limit',type=int,default=0); ap.add_argument('--key',default=os.environ.get('GAP_KEY','none')); a=ap.parse_args()
op=gzip.open if a.jobs.endswith('.gz') else open
jobs=[json.loads(l) for l in op(a.jobs,'rt')]; host=jobs[0]['id'].split('|')[0]
rej=a.out+'.rejected'; done=set()
for f in (a.out,rej):
    if os.path.exists(f):
        for l in open(f):
            try: d=json.loads(l); done.add(d['source_page_id'] if 'source_page_id' in d else d['pid'])
            except Exception: pass
todo=[j for j in jobs if j['pid'] not in done]; todo=todo[:a.limit] if a.limit else todo
print(len(jobs),'jobs',len(todo),'todo',flush=True)
lock=threading.Lock(); st={'n':a.idstart,'ok':0,'bad':0}; it=iter(todo)
def call(j):
    body={'model':a.model,'max_tokens':1200,'temperature':0.7,'messages':[{'role':'system','content':g.SYS},{'role':'user','content':json.dumps({'name':j['name'],'text':j['text']},ensure_ascii=False)}]}
    for k in range(6):
        try:
            rq=urllib.request.Request(a.url.rstrip('/')+'/chat/completions',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+a.key,'Content-Type':'application/json'})
            return json.load(urllib.request.urlopen(rq,timeout=300))['choices'][0]['message']['content']
        except urllib.error.HTTPError as e:
            if e.code not in(429,500,502,503): return None
        except Exception: pass
        time.sleep(5*2**k)
def worker():
    while True:
        with lock:
            j=next(it,None)
        if j is None: return
        txt=call(j); e=None
        if txt:
            try:
                with lock: n=st['n']; st['n']+=1
                e=g.accept(j,txt,host,a.universe,n)
            except Exception: e=None
        with lock:
            if e: open(a.out,'a').write(json.dumps(e,ensure_ascii=False)+'\n'); st['ok']+=1
            else: open(rej,'a').write(json.dumps({'pid':j['pid']})+'\n'); st['bad']+=1
            if (st['ok']+st['bad'])%100==0: print(st,flush=True)
ts=[threading.Thread(target=worker) for _ in range(a.workers)]
[t.start() for t in ts]
try: [t.join() for t in ts]
except KeyboardInterrupt: os._exit(0)
print('done',st)
