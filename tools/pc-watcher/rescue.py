import os,sys
PF=os.environ.get('PROJECT_FILES','/mnt/project-files').rstrip('/\\')+'/'
RUN=os.environ.get('RUN_DIR',os.path.dirname(os.path.abspath(__file__))).rstrip('/\\')+'/'
import os,re,subprocess,time,json
J=PF+'compute/jobs/'
M={'haiku':'claude-haiku-5-5','sonnet':'claude-sonnet-5-5','opus':'claude-opus-5-5'}
MAXJ=int(os.environ.get('RESCUE_JOBS','10'))
def n(p): return sum(1 for _ in open(p)) if os.path.exists(p) else 0
def pending():
    out=[]
    for j in sorted(os.listdir(J)):
        d=J+j+'/'
        if not os.path.exists(d+'in.jsonl') or not os.path.exists(d+'.claimed'): continue
        if j.startswith(('dish_comp_pick_1b','worldsys','libmob_classify')): continue
        if n(d+'out.jsonl')<n(d+'in.jsonl'): out.append(j)
    return out
running={}
import time as _t
live=lambda j: os.path.exists(J+j+'/out.jsonl') and _t.time()-os.path.getmtime(J+j+'/out.jsonl')<150   # portable: a job counts as live if it wrote in the last 150 s
tried={}
while True:
    for j in list(running):
        if running[j].poll() is not None: del running[j]
    todo=[j for j in pending() if j not in running and not live(j) and tried.get(j,0)<4]
    for j in todo:
        if len(running)>=MAXJ: break
        txt=''.join(open(J+j+'/'+f).read() for f in os.listdir(J+j) if f.upper().startswith(('README','CHECK')))
        m=re.search(r'max_tokens[ =:]*(\d+)',txt); mt=m.group(1) if m else '1200'
        mm=re.search(r'model[ :=]+(haiku|sonnet|opus)',txt,re.I); mdl=M[mm.group(1).lower()] if mm else M['haiku']
        env=dict(os.environ,SYNC_THREADS='64')
        running[j]=subprocess.Popen([sys.executable,'-I',RUN+'sync.py',j,mdl,mt],stdout=open(RUN+f'{j}.log','a'),stderr=subprocess.STDOUT,env=env)
        tried[j]=tried.get(j,0)+1; print('started',j,mdl,mt,flush=True)
    if not running and not todo and not [j for j in pending() if not live(j)]: print('all done',flush=True); break
    time.sleep(10)
