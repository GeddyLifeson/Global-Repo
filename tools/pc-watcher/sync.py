import os,sys
PF=os.environ.get('PROJECT_FILES','/mnt/project-files').rstrip('/\\')+'/'
RUN=os.environ.get('RUN_DIR',os.path.dirname(os.path.abspath(__file__))).rstrip('/\\')+'/'
import json,os,sys,time,urllib.request,urllib.error,threading,base64
import os.path as _p
sys.path.insert(0,RUN); import common
job,model,mt=sys.argv[1],sys.argv[2],int(sys.argv[3])
d=PF+f'compute/jobs/{job}/';K=(os.environ.get('ANTHROPIC_API_KEY') or open(PF+'compute/secrets/anthropic_key').read().strip())
H={'x-api-key':K,'anthropic-version':'2023-06-01','content-type':'application/json'}
rows=[json.loads(l) for l in open(d+'in.jsonl')];fn=d+'out.jsonl'
done={json.loads(l)['id'] for l in open(fn)} if os.path.exists(fn) else set()
OC=common.out_config(d)
lock=threading.Lock();todo=[r for r in rows if r['id'] not in done]
# shared prompt prefix goes first with cache_control (min cacheable 512 tokens on 5.5 models, ~2000 chars)
pre=_p.commonprefix([r['prompt'] for r in todo]) if len(todo)>1 else ''
pre=pre[:min(len(r['prompt']) for r in todo)-1] if pre else ''
pre=pre if len(pre)>2400 else ''
CC={'type':'ephemeral','ttl':'1h'}
def body(r):
    txt=[{'type':'text','text':pre,'cache_control':CC},{'type':'text','text':r['prompt'][len(pre):]}] if pre else [{'type':'text','text':r['prompt']}]
    img=[common.img(f) for f in r.get('images',[])]
    b={'model':model,'max_tokens':mt,'thinking':{'type':'disabled' if 'haiku' in model else 'between_tools'},'messages':[{'role':'user','content':txt[:1]+img+txt[1:] if pre else img+txt}]}
    if OC: b['output_config']=OC
    if r.get('system'): b['system']=[{'type':'text','text':r['system'],'cache_control':CC}] if len(r['system'])>2400 else r['system']
    return b
def one(r):
    b=body(r);j=None
    for a in range(10):
        try:
            j=json.load(urllib.request.urlopen(urllib.request.Request('https://api.anthropic.com/v1/messages',json.dumps(b).encode(),H),timeout=180));break
        except urllib.error.HTTPError as e:
            j=None
            if e.code in (429,529,500,502,503):
                try: w=float(e.headers.get('retry-after') or 0)
                except: w=0
                time.sleep(min(90,max(w,3*2**a))+__import__('random').random()*3)
            elif e.code==400: return
            else: time.sleep(min(60,5*2**a))
        except Exception as e: j=None;time.sleep(min(60,5*2**a))
    if not j: return
    t=''.join(c.get('text','') for c in j['content']);u=j['usage']
    with lock:
        open(fn,'a').write(json.dumps({'id':r['id'],'text':t,'lane':model},ensure_ascii=False)+'\n')
        open(PF+'compute/ledger.csv','a').write(f"{time.strftime('%FT%TZ')},{job},{model}-sync,{u['input_tokens']},{u['output_tokens']},{u.get('cache_creation_input_tokens') or 0},{u.get('cache_read_input_tokens') or 0}\n")
def run():
    while True:
        with lock:
            if not todo: return
            r=todo.pop()
        one(r)
if todo and (pre or any(r.get('system') for r in todo)):
    one(todo.pop())  # warm the cache with one call first so the parallel calls read it
ts=[threading.Thread(target=run) for _ in range(int(os.environ.get("SYNC_THREADS","96")))];[t.start() for t in ts];[t.join() for t in ts];print('done')
