# S6974 Recover the source wiki page of Panscriptum beings that lost their link (no AI): TF-IDF cosine of the card text against the non-empty leads of the being's universe wiki.
# Usage: python3 -I relink_assayed.py MASTER.tsv UNIVERSE_MAP.json LEADS_DIR CARDS_DIR OUT_MASTER.tsv UNLINKED_PAGES.tsv OUT_UNLINKED.tsv
# Only layer=assay beings with no source_wiki are matched. Originated layers (persons, gods, fauna, ...) were written from generic briefs, not wiki pages, so they get status=original.
# Added columns: relink_wiki, relink_lead_idx, relink_score, relink_margin, relink_status (match_high|match_low|no_match|original|linked).
# match_high: score>=0.30 and margin>=0.05 over the runner-up. match_low: score>=0.20. Calibrated on linked beings (precision at 0.30 about 0.5, so even match_high needs review).
import csv,glob,json,os,sys,collections
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
master,umap,leads_dir,cards_dir,out,unl,out_unl=sys.argv[1:8]
um={v.lower():k for k,v in json.load(open(umap)).items()}
cards={}
for f in glob.glob(cards_dir+'/*.json'):
    for v in json.load(open(f)).values():
        for e in v:
            if e: cards[e[0]]=e[4]
rows=list(csv.DictReader(open(master,encoding='utf-8'),delimiter='\t'))
cols=list(rows[0].keys())+['relink_wiki','relink_lead_idx','relink_score','relink_margin','relink_status']
todo=collections.defaultdict(list)
for r in rows:
    r.update(relink_wiki='',relink_lead_idx='',relink_score='',relink_margin='')
    if r['source_wiki']: r['relink_status']='linked'
    elif r['id'].split('.')[-2]=='assay': r['relink_status']='no_match'; todo[um.get(r['universe'].lower(),'')].append(r)
    else: r['relink_status']='original'
byid={r['id']:r for r in rows}
for slug,rs in todo.items():
    if not slug or not os.path.exists(f'{leads_dir}/{slug}.jsonl'): continue
    leads=[x for x in map(json.loads,open(f'{leads_dir}/{slug}.jsonl',encoding='utf-8')) if len(x['text'])>40]
    if not leads: continue
    vec=TfidfVectorizer(sublinear_tf=True,stop_words='english',ngram_range=(1,2))
    L=vec.fit_transform([x['text'] for x in leads])
    for i in range(0,len(rs),2000):
        part=rs[i:i+2000]
        S=(vec.transform([cards[r['id']] for r in part])@L.T).toarray()
        top=np.argsort(-S,axis=1)[:,:2]
        for n,r in enumerate(part):
            s1,s2=S[n,top[n,0]],S[n,top[n,1]] if S.shape[1]>1 else 0
            r.update(relink_wiki=slug,relink_lead_idx=leads[top[n,0]]['i'],relink_score=f'{s1:.3f}',relink_margin=f'{s1-s2:.3f}')
            r['relink_status']='match_high' if s1>=.30 and s1-s2>=.05 else 'match_low' if s1>=.20 else 'no_match'
    print(slug,len(rs),flush=True)
with open(out,'w',encoding='utf-8',newline='') as o:
    w=csv.DictWriter(o,cols,delimiter='\t',lineterminator='\n'); w.writeheader(); w.writerows(rows)
got={(r['relink_wiki'],str(r['relink_lead_idx'])) for r in rows if r['relink_status']=='match_high'}
with open(unl,encoding='utf-8') as f, open(out_unl,'w',encoding='utf-8',newline='') as o:
    for n,l in enumerate(f):
        p=l.split('\t',2)
        if n and (p[0],p[1]) in got: continue
        o.write(l)
print(collections.Counter(r['relink_status'] for r in rows))
