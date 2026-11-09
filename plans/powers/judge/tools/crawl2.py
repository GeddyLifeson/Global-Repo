import json,sys,time,urllib.request,urllib.parse,gzip,os
# usage: crawl2.py host out.jsonl.gz [sleep_s]  -- raw wikitext of every ns0 non-redirect page; resumable (out.cont holds the continue token)
host,out=sys.argv[1:3]; nap=float(sys.argv[3]) if len(sys.argv)>3 else 0
UA={'User-Agent':'PanscriptumJudge/1.0 (personal catalogue)'}
cf=out+'.cont'; cont=json.load(open(cf)) if os.path.exists(cf) else {}
o=gzip.open(out,'at',encoding='utf-8'); n=0; t0=time.time()
while True:
    q={'action':'query','generator':'allpages','gapnamespace':0,'gaplimit':500,'gapfilterredir':'nonredirects','prop':'revisions','rvprop':'content','rvslots':'main','format':'json','formatversion':2,**cont}
    d=None
    for k in range(40):
        try: d=json.load(urllib.request.urlopen(urllib.request.Request(f'https://{host}/api.php?'+urllib.parse.urlencode(q),headers=UA),timeout=90)); break
        except Exception as e:
            time.sleep(min(600,10*(k+1)) if '429' in str(e) else 3*(k+1))
    if d is None: print('FAIL',cont,flush=True); break
    for p in d.get('query',{}).get('pages',[]):
        if p.get('revisions'): o.write(json.dumps([p['title'],p['revisions'][0]['slots']['main']['content'][:40000]],ensure_ascii=False)+'\n')
    o.flush(); n+=1
    if 'continue' not in d: print('done',flush=True); break
    cont=d['continue']; json.dump(cont,open(cf,'w'))
    if n%20==0: print(n,int(time.time()-t0),flush=True)
    time.sleep(nap)
