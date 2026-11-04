import os,sys
PF=os.environ.get('PROJECT_FILES','/mnt/project-files').rstrip('/\\')+'/'
RUN=os.environ.get('RUN_DIR',os.path.dirname(os.path.abspath(__file__))).rstrip('/\\')+'/'
import os,re,subprocess,sys,time,json
sys.path.insert(0,RUN); import common
BATCH_IN={'claude-haiku-5-5':0.05,'claude-sonnet-5-5':1.0,'claude-opus-5-5':2.0}  # $/MTok at Batch rates
BATCH_OUT={'claude-haiku-5-5':0.25,'claude-sonnet-5-5':5.0,'claude-opus-5-5':10.0}
def estimate(d,mdl,mt):
    """free pre-flight: count_tokens on the first row (text only) scaled by row count; logs the Batch-rate ceiling cost"""
    try:
        rows=[json.loads(l) for l in open(d+'in.jsonl')]; r=rows[0]
        body={'model':mdl,'messages':[{'role':'user','content':r['prompt']}]}
        if r.get('system'): body['system']=r['system']
        tin=common.count_tokens(mdl,body)*len(rows); c=tin*BATCH_IN[mdl]/1e6+len(rows)*mt*BATCH_OUT[mdl]/1e6
        open(d+'.estimate','w').write(f'rows={len(rows)} input_tokens~{tin} ceiling_cost_usd~{c:.2f} (before caching, at full max_tokens)\n'); return len(rows),c
    except Exception as e: return 0,0
J=PF+'compute/jobs/'
while True:
    if os.path.exists(RUN+'HOLD'):
        time.sleep(30); continue
    for j in sorted(os.listdir(J)):
        d=J+j+'/'
        if not os.path.exists(d+'in.jsonl') or os.path.exists(d+'out.jsonl') or os.path.exists(d+'.claimed'): continue
        open(d+'.claimed','w').write(time.strftime('%FT%TZ'))
        txt=''.join(open(d+f).read() for f in os.listdir(d) if f.upper().startswith(('README','CHECK')))
        m=re.search(r'max_tokens[ =:]*(\d+)',txt); mt=int(m.group(1)) if m else 1200
        mm=re.search(r'model[ :=]+(haiku|sonnet|opus)',txt,re.I); mdl={'haiku':'claude-haiku-5-5','sonnet':'claude-sonnet-5-5','opus':'claude-opus-5-5'}[mm.group(1).lower()] if mm else 'claude-haiku-5-5'
        n,est=estimate(d,mdl,mt)
        # Batch is 50% off and caches shared prefixes; Sonnet/Opus bulk (>=40 rows) goes Batch unless the README says `sync`
        use_batch=bool(re.search(r'\bbatch\b',txt,re.I))
        subprocess.Popen([sys.executable,'-I',RUN+''+('batch.py' if use_batch else 'sync.py'),j,*([str(mt),mdl] if use_batch else [mdl,str(mt)])],stdout=open(RUN+f'{j}.log','w'),stderr=subprocess.STDOUT)
        print('claimed',j,mt,mdl,'batch' if use_batch else 'sync',f'~${est:.2f} ceiling',flush=True)
    time.sleep(5)
