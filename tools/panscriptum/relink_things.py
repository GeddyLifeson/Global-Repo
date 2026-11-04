# S6977 Source link for every non-being Panscriptum card (items, places, events, factions, concepts...), no AI: exact summary join to assay_merged gives wiki|lead; unlinked assay cards get TF-IDF top-12 candidates for a later model pick.
# Usage: relink_things.py MASTER_UNIVERSE_MAP.json ASSAY_MERGED.jsonl LEADS_DIR CARDS_DIR OUT_THINGS.tsv JOB_DIR
# status: linked (exact join) | match_high/match_low/no_match (TF-IDF, pending model pick) | original (originated layers, pack-* layers: no wiki page by design).
import csv,glob,json,os,sys,collections
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
umap,am,leads_dir,cards_dir,out,jd=sys.argv[1:7]
um={v.lower():k for k,v in json.load(open(umap)).items()}
link={}
for l in open(am,encoding='utf-8'):
    d=json.loads(l)
    link[d['summary']]=d['id']
rows=[];todo=collections.defaultdict(list)
for f in glob.glob(cards_dir+'/*.json'):
    for v in json.load(open(f)).values():
        for e in v:
            if not e or e[2]=='NPC': continue
            p=e[0].split('.'); layer=p[-2] if len(p)>2 else p[0]
            r=dict(id=e[0],name=e[1],type=e[2],layer=layer,source_wiki='',source_lead_idx='',score='',status='original',shard=os.path.basename(f))
            if e[4] in link:
                w,i=link[e[4]].rsplit('|',1); r.update(source_wiki=w,source_lead_idx=i,status='linked')
            elif layer=='assay':
                s=um.get(e[0].split('.')[1].lower(),''); r['status']='no_match'; r['source_wiki']=s
                if s and os.path.exists(f'{leads_dir}/{s}.jsonl'): todo[s].append((r,e[4]))
            rows.append(r)
os.makedirs(jd,exist_ok=True); jobs=open(jd+'/in.jsonl','w',encoding='utf-8')
SYS=("You match a rewritten game-wiki entry to the wiki page it was rewritten from. Names, places and numbers were changed, but the kind of thing and its traits stay. "
"Pick the one candidate that is clearly the same subject, or 0 if none is. Reason in at most two short sentences, then end your reply with the JSON object on its own line: {\"pick\": <number 0-12>}.")
for slug,rs in todo.items():
    leads=[x for x in map(json.loads,open(f'{leads_dir}/{slug}.jsonl',encoding='utf-8')) if len(x['text'])>40]
    vec=TfidfVectorizer(sublinear_tf=True,stop_words='english',ngram_range=(1,2)); L=vec.fit_transform([x['text'] for x in leads])
    for i in range(0,len(rs),2000):
        part=rs[i:i+2000]; S=(vec.transform([t for _,t in part])@L.T).toarray(); top=np.argsort(-S,axis=1)[:,:12]
        for a,(r,t) in enumerate(part):
            s1=S[a,top[a,0]]; s2=S[a,top[a,1]]
            r.update(source_lead_idx=leads[top[a,0]]['i'],score=f'{s1:.3f}',status='match_high' if s1>=.30 and s1-s2>=.05 else 'match_low' if s1>=.20 else 'no_match')
            c=[leads[x] for x in top[a]]
            jobs.write(json.dumps({'id':r['id'],'system':SYS,'prompt':f"Entry: {t}\n\nCandidates:\n"+"\n".join(f"{b+1}. {x['text'][:220]}" for b,x in enumerate(c)),'cands':[x['i'] for x in c],'wiki':slug},ensure_ascii=False)+'\n')
with open(out,'w',encoding='utf-8',newline='') as o:
    w=csv.DictWriter(o,list(rows[0]),delimiter='\t',lineterminator='\n'); w.writeheader(); w.writerows(rows)
print(len(rows),collections.Counter(r['status'] for r in rows))
