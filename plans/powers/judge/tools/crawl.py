import json,sys,time,urllib.request,urllib.parse,gzip
sys.path.insert(0,'/tmp/s'); import pages as P
host,out=sys.argv[1:3]
cont={}; n=0; t0=time.time()
res={};reds={}
while True:
    q={'action':'query','generator':'allpages','gapnamespace':0,'gaplimit':500,'gapfilterredir':'nonredirects','prop':'revisions','rvprop':'content','rvslots':'main','format':'json','formatversion':2,**cont}
    for k in range(8):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(f'https://{host}/api.php?'+urllib.parse.urlencode(q),headers={'User-Agent':'PanscriptumJudge/1.0 (personal catalogue)'}),timeout=90)); break
        except Exception as e: print('ERR',str(e)[:80],flush=True); time.sleep(5*(k+1)); d=None
    if d is None: print('FAIL',cont,flush=True); break
    for p in d.get('query',{}).get('pages',[]):
        if p.get('revisions'): res[p['title']]=P.wiki2txt(p['revisions'][0]['slots']['main']['content'])[:12000]
    n+=1
    if n%20==0: print(n,len(res),int(time.time()-t0),flush=True)
    if 'continue' not in d: break
    cont=d['continue']
json.dump({'pages':res,'redirects':{}},gzip.open(out,'wt',encoding='utf-8'),ensure_ascii=False)
print('done',len(res),flush=True)
