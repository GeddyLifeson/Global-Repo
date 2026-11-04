# S6976 Sonnet pass for the 6,032 unlinked assay beings: build a compute job (each being plus its 12 best TF-IDF candidate leads), then merge the picks into the master sheet.
# Usage: relink_llm.py jobs MASTER.tsv UNIVERSE_MAP.json LEADS_DIR CARDS_DIR JOB_DIR | apply MASTER.tsv JOB_DIR LEADS_DIR OUT_MASTER.tsv UNLINKED.tsv OUT_UNLINKED.tsv COVERAGE.tsv OUT_COVERAGE.tsv
import csv,glob,json,os,sys,collections,re
K=12
SYS=("You match a rewritten game-wiki entry to the wiki page it was rewritten from. Names, places and numbers were changed, but the kind of being, traits and events stay. "
"Pick the one candidate that is clearly the same subject, or 0 if none is. Reply with JSON only: {\"pick\": <number 0-12>}.")
def jobs(master,umap,leads_dir,cards_dir,jd):
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    um={v.lower():k for k,v in json.load(open(umap)).items()}
    cards={}
    for f in glob.glob(cards_dir+'/*.json'):
        for v in json.load(open(f)).values():
            for e in v:
                if e: cards[e[0]]=e[4]
    todo=collections.defaultdict(list)
    for r in csv.DictReader(open(master,encoding='utf-8'),delimiter='\t'):
        if r['relink_status'] in('match_high','match_low','no_match') and r['relink_wiki']: todo[r['relink_wiki']].append(r['id'])
    os.makedirs(jd,exist_ok=True); n=0
    with open(jd+'/in.jsonl','w',encoding='utf-8') as o:
        for slug,ids in todo.items():
            leads=[x for x in map(json.loads,open(f'{leads_dir}/{slug}.jsonl',encoding='utf-8')) if len(x['text'])>40]
            vec=TfidfVectorizer(sublinear_tf=True,stop_words='english',ngram_range=(1,2)); L=vec.fit_transform([x['text'] for x in leads])
            for i in range(0,len(ids),2000):
                part=ids[i:i+2000]; S=(vec.transform([cards[j] for j in part])@L.T).toarray(); top=np.argsort(-S,axis=1)[:,:K]
                for a,j in enumerate(part):
                    c=[leads[t] for t in top[a]]
                    p=f"Entry: {cards[j]}\n\nCandidates:\n"+"\n".join(f"{b+1}. {x['text'][:220]}" for b,x in enumerate(c))
                    o.write(json.dumps({'id':j,'prompt':p,'system':SYS,'max_tokens':20,'cands':[x['i'] for x in c],'wiki':slug},ensure_ascii=False)+'\n'); n+=1
    open(jd+'/README','w').write(f"Owner: relink thread (S6975). {n} Panscriptum beings, each with {K} candidate wiki leads; reply JSON {{\"pick\":N}}, 0 for none. Haiku, max_tokens 20. Failures retry in relink-assay-retry.\n")
    print(n)
def apply(master,jd,leads_dir,out,unl,out_unl,cov,out_cov):
    meta={}
    for l in open(jd+'/in.jsonl',encoding='utf-8'):
        d=json.loads(l); meta[d['id']]=(d['wiki'],d['cands'])
    pick={}
    for l in open(jd+'/out.jsonl',encoding='utf-8'):
        d=json.loads(l)
        try: pick[d['id']]=int(json.loads(re.findall(r'\{\s*"pick"\s*:\s*\d+\s*\}',d['text'])[-1])['pick'])
        except Exception: pass
    rows=list(csv.DictReader(open(master,encoding='utf-8'),delimiter='\t')); cols=list(rows[0].keys())+['llm_wiki','llm_lead_idx','llm_status']
    for r in rows:
        r.update(llm_wiki='',llm_lead_idx='',llm_status='')
        if r['id'] in meta:
            p=pick.get(r['id'])
            if p is None: r['llm_status']='failed'
            elif p==0 or p>len(meta[r['id']][1]): r['llm_status']='none'
            else: r.update(llm_wiki=meta[r['id']][0],llm_lead_idx=meta[r['id']][1][p-1],llm_status='match')
    with open(out,'w',encoding='utf-8',newline='') as o:
        w=csv.DictWriter(o,cols,delimiter='\t',lineterminator='\n'); w.writeheader(); w.writerows(rows)
    got={(r['llm_wiki'],str(r['llm_lead_idx'])) for r in rows if r['llm_status']=='match'}
    old=collections.Counter(); new=collections.Counter()
    with open(unl,encoding='utf-8') as f,open(out_unl,'w',encoding='utf-8',newline='') as o:
        for n,l in enumerate(f):
            p=l.split('\t',2); old[p[0]]+=1
            if n and (p[0],p[1]) in got: continue
            new[p[0]]+=1; o.write(l)
    cr=list(csv.reader(open(cov,encoding='utf-8'),delimiter='\t')); h=cr[0]
    for r in cr[1:]:
        k=old[r[0]]-new[r[0]]
        if k:
            for c,s in(('no_entry',-1),('entry_not_in_library',1)): r[h.index(c)]=str(int(r[h.index(c)])+s*k)
    csv.writer(open(out_cov,'w',encoding='utf-8',newline=''),delimiter='\t',lineterminator='\n').writerows(cr)
    print(collections.Counter(r['llm_status'] for r in rows if r['llm_status']),'gaps closed',sum(old.values())-sum(new.values()))
a=sys.argv[1:]; {'jobs':jobs,'apply':apply}[a[0]](*a[1:])
