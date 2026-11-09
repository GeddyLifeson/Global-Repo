# S6970 fetch_leads.py: list Category:Characters of a Fandom wiki and fetch each page's lead wikitext (resumable, ~1 req/s).
# python3 -I fetch_leads.py <host e.g. marvel.fandom.com> <outdir>   -> <outdir>/<host>.jsonl.gz  rows {pid,title,text}
import sys,os,json,gzip,time,urllib.request,urllib.parse
host,out=sys.argv[1],sys.argv[2]; os.makedirs(out,exist_ok=True)
fn=os.path.join(out,host+'.jsonl.gz'); tf=os.path.join(out,host+'.titles.json')
def api(**p):
    p['format']='json'; u=f'https://{host}/api.php?'+urllib.parse.urlencode(p)
    for k in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'shardfall-gap/1'}),timeout=60))
        except Exception as e: time.sleep(2*2**k)
    raise SystemExit('api failed')
if os.path.exists(tf): titles=json.load(open(tf))
else:
    titles=[];c={}
    while True:
        d=api(action='query',list='categorymembers',cmtitle='Category:Characters',cmlimit='max',cmtype='page',**c)
        titles+=[(m['pageid'],m['title']) for m in d['query']['categorymembers']]
        if 'continue' not in d: break
        c={'cmcontinue':d['continue']['cmcontinue']}; time.sleep(.5)
    json.dump(titles,open(tf,'w'))
done=set()
if os.path.exists(fn):
    try:
        for l in gzip.open(fn,'rt'): done.add(json.loads(l)['req'])
    except EOFError: pass
todo=[t for t in titles if t[0] not in done]
print(len(titles),'listed',len(todo),'todo',flush=True)
for i in range(0,len(todo),50):
    b=todo[i:i+50]; d=api(action='query',titles='|'.join(t for _,t in b),redirects='1',prop='revisions',rvslots='main',rvprop='content',rvsection='0')
    byt={p['title']:p for p in d['query'].get('pages',{}).values()}
    redir={r['from']:r['to'] for r in d['query'].get('redirects',[])}
    rows=[]
    for pid,t in b:
        p=byt.get(redir.get(t,t)); tx=''
        if p and p.get('revisions'): tx=p['revisions'][0]['slots']['main'].get('*') or p['revisions'][0]['slots']['main'].get('content','')
        rows.append({'req':pid,'pid':p['pageid'] if p and 'pageid' in p else pid,'title':p['title'] if p else t,'text':tx[:3000]})
    with gzip.open(fn,'at') as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')
    time.sleep(.8)
print('done')
