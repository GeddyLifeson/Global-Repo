import sys,json,gzip,re,os,collections
sys.path.insert(0,'/tmp/s'); import pages as P
SRC={'world-of-warcraft':[('wowpedia.fandom.com','wo'),('warcraft.wiki.gg','ww')],'xenoblade':[('xenoblade.fandom.com','xe')]}
HOST=SRC
D={}
for w,l in SRC.items():
    D[w]=[(h,json.load(gzip.open(f'/tmp/s/{f}.json.gz','rt',encoding='utf-8'))) for h,f in l if os.path.exists(f'/tmp/s/{f}.json.gz')]
def find(d,t):
    for _ in range(4):
        if t in d['pages']: return t
        t2=d['redirects'].get(t) or d['redirects'].get(t[:1].upper()+t[1:])
        if not t2: 
            t=t[:1].upper()+t[1:]
            if t in d['pages']: return t
            return None
        t=t2
    return t if t in d['pages'] else None
def lead(x): return x[:900]
# shingle index fallback
IDX={}
for w,l in D.items():
    for h,d in l:
        ix=collections.defaultdict(list)
        for t,x in d['pages'].items():
            for s in list(P.shingles(lead(x)))[:60]: ix[s].append(t)
        IDX[h]=ix
def resolve_row(r):
    w=r['id'].rsplit('|',1)[0]
    cs=P.cands(r['text']); sh=P.shingles(P.clean_row(r['text']))
    for h,d in D[w]:
        for c in cs:
            f=find(d,c)
            if f and P.match(r['text'],lead(d['pages'][f])): return h,f,d['pages'][f]
        if len(sh)>=3:
            cnt=collections.Counter()
            for s in sh:
                l=IDX[h].get(s)
                if l and len(l)<30:
                    for t in l: cnt[t]+=1
            for t,n in cnt.most_common(5):
                pt=' '.join(re.findall(r'[0-9a-z]+',d['pages'][t].lower()))
                if sum(1 for s in sh if s in pt)/len(sh)>=0.4: return h,t,d['pages'][t]
    return None
if __name__=='__main__':
    lo,hi=int(sys.argv[1]),int(sys.argv[2]); G='/home/user/global-repo/plans/powers/judge/'
    tot=ok=0
    for n in range(lo,hi+1):
        p=f'{G}batches/shard_{n}.jsonl'
        if not os.path.exists(p): continue
        R=[json.loads(l) for l in open(p,encoding='utf-8')]
        out=[];cache={};miss=[]
        for r in R:
            w=r['id'].rsplit('|',1)[0]; z=resolve_row(r) if w in D else None; t=z and z[1]
            if z:
                u=f"https://{z[0]}/wiki/"+P.urllib.parse.quote(t.replace(' ','_')); cache[u]=z[2]
            else: u=''; miss.append(r['id'])
            out.append({'id':r['id'],'title':t or '','url':u})
        open(f'{G}batches/shard_{n}.src.jsonl','w',encoding='utf-8').write(''.join(json.dumps(o,ensure_ascii=False)+'\n' for o in out))
        json.dump(cache,gzip.open(f'{G}cache/shard_{n}.pages.json.gz','wt',encoding='utf-8'),ensure_ascii=False)
        if miss: json.dump(miss,open(f'{G}batches/shard_{n}.absent.json','w'))
        tot+=len(R);ok+=len(R)-len(miss); print(n,len(R)-len(miss),'/',len(R),flush=True)
    print('TOTAL',ok,tot)
