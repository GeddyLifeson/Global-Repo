import os,sys
PF=os.environ.get('PROJECT_FILES','/mnt/project-files').rstrip('/\\')+'/'
RUN=os.environ.get('RUN_DIR',os.path.dirname(os.path.abspath(__file__))).rstrip('/\\')+'/'
import json,sys,os,time,urllib.request
sys.path.insert(0,RUN); import common
job,maxtok=sys.argv[1],int(sys.argv[2]); model=sys.argv[3] if len(sys.argv)>3 else 'claude-haiku-5-5'
d=PF+f'compute/jobs/{job}/'; K=(os.environ.get('ANTHROPIC_API_KEY') or open(PF+'compute/secrets/anthropic_key').read().strip())
H={'x-api-key':K,'anthropic-version':'2023-06-01','content-type':'application/json'}
def api(path,body=None):
    r=urllib.request.Request('https://api.anthropic.com'+path,json.dumps(body).encode() if body else None,H)
    return urllib.request.urlopen(r,timeout=300)
rows=[json.loads(l) for l in open(d+'in.jsonl')]
OC=common.out_config(d)  # effort / structured-output schema from the job folder
done=set()
if os.path.exists(d+'out.jsonl'): done={json.loads(l)['id'] for l in open(d+'out.jsonl')}
rows=[(i,r) for i,r in enumerate(rows) if r['id'] not in done]
import os.path as _p
pre=_p.commonprefix([r['prompt'] for _,r in rows]) if len(rows)>1 else ''
pre=pre[:min(len(r['prompt']) for _,r in rows)-1] if pre else ''
pre=pre if len(pre)>2400 else ''  # min cacheable is 512 tokens on 5.5 models (~2000 chars)
ids={}; batches=[]
for s in range(0,len(rows),1500):
    reqs=[]
    for i,r in rows[s:s+1500]:
        p={'model':model,'max_tokens':maxtok,'thinking':{'type':'disabled' if 'haiku' in model else 'between_tools'},'messages':[{'role':'user','content':([{'type':'text','text':pre,'cache_control':{'type':'ephemeral','ttl':'1h'}},{'type':'text','text':r['prompt'][len(pre):]}] if pre else r['prompt'])}]}
        if r.get('system'): p['system']=[{'type':'text','text':r['system'],'cache_control':{'type':'ephemeral','ttl':'1h'}}] if len(r['system'])>2400 else r['system']
        if r.get('images'):
            blocks=[common.img(f) for f in r['images']]  # Files API: upload once, reuse file_id
            p['messages'][0]['content']=([{'type':'text','text':pre,'cache_control':{'type':'ephemeral','ttl':'1h'}}] if pre else [])+blocks+[{'type':'text','text':r['prompt'][len(pre):]}]  # shared text first (cached), then per-row images
        if OC: p['output_config']=OC
        reqs.append({'custom_id':f'r{i}','params':p}); ids[f'r{i}']=r['id']
    batches.append(json.load(api('/v1/messages/batches',{'requests':reqs}))['id'])
print('submitted',batches,flush=True)
n=0
for b in batches:
    while json.load(api('/v1/messages/batches/'+b))['processing_status']!='ended': time.sleep(30)
    for l in api(f'/v1/messages/batches/{b}/results'):
        j=json.loads(l)
        if j['result']['type']=='succeeded':
            t=''.join(c.get('text','') for c in j['result']['message']['content'])
            u=j['result']['message']['usage']; open(PF+'compute/ledger.csv','a').write(f"{time.strftime('%FT%TZ')},{job},{model},{u['input_tokens']},{u['output_tokens']},{u.get('cache_creation_input_tokens') or 0},{u.get('cache_read_input_tokens') or 0}\n")
            open(d+'out.jsonl','a').write(json.dumps({'id':ids[j['custom_id']],'text':t,'lane':'claude-batch'},ensure_ascii=False)+'\n'); n+=1
    print('collected',b,n,flush=True)
print('done',n)
