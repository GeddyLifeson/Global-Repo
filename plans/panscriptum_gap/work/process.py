# python3 -I process.py S tag : validate new worker replies, assign ids, append to out/<tag>.jsonl (state in done.json)
import sys,os,json,glob,importlib.util
S,tag=sys.argv[1:3]; host={'dc':'dc.fandom.com','marvel':'marvel.fandom.com'}[tag]; univ={'dc':'Orintanum','marvel':'Losaustanum'}[tag]
spec=importlib.util.spec_from_file_location('gb',S+'/spec/gap_batch.py'); gb=importlib.util.module_from_spec(spec); spec.loader.exec_module(gb)
jobs={j['id']:j for j in map(json.loads,open(f'/mnt/project-files/compute/jobs/panscriptum-gap/retry-{tag}/{host}.jobs.jsonl'))}
cf=f'/mnt/project-files/compute/id_counters/gap_{host}'; nxt=int(open(cf).read().strip())
sf=f'{S}/{tag}/state.json'; st=json.load(open(sf)) if os.path.exists(sf) else {'files':[],'seen':[],'ok':0,'bad':0,'miss':0}
seen=set(st['seen']); outf=f'{S}/{tag}/accepted.jsonl'; new=0
with open(outf,'a') as o:
    for f in sorted(glob.glob(f'{S}/{tag}/out/*.jsonl')):
        if f in st['files']: continue
        for l in open(f):
            try: r=json.loads(l); j=jobs[r['id']]; assert r['id'] not in seen
            except Exception: st['miss']+=1; continue
            seen.add(r['id'])
            try:
                rep=r['reply']; txt=rep if isinstance(rep,str) else json.dumps(rep)
                e=gb.accept(j,txt,host,univ,nxt); nxt+=1; st['ok']+=1; new+=1; o.write(json.dumps(e,ensure_ascii=False)+'\n')
            except Exception: st['bad']+=1
        st['files'].append(f)
st['seen']=sorted(seen); json.dump(st,open(sf,'w')); open(cf,'w').write(str(nxt))
print(tag,'new',new,'ok',st['ok'],'bad',st['bad'],'unmatched',st['miss'],'of',len(jobs),'next id',nxt)
