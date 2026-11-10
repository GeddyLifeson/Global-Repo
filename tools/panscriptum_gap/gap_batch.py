# S6971 gap_batch.py: turn fetched character leads into original Panscriptum entries via Haiku Batch. Every row keeps source host, page id, title, URL.
# python3 -I gap_batch.py build <host> <leads.jsonl.gz> <jobdir> [skip_titles.txt]   -> <jobdir>/<host>.jobs.jsonl
#                         submit <jobdir>/<host>.jobs.jsonl [chunk]                  -> posts batches, logs ids to <jobdir>/batches.json
#                         collect <jobdir> <host> <universe> <out.jsonl>             -> validated entries (rows without source are never written)
import sys,os,re,json,gzip,random,time,urllib.request,collections
MASTER='/mnt/project-files/plans/PANSCRIPTUM_MASTER.tsv'
KEY=lambda:open('/mnt/project-files/compute/secrets/anthropic_key').read().strip()
R2={'Arcane':'AR','Grounded':'GR','Ki':'KI','Martial':'MA','Mythic':'MY','Outer':'OU','Stellar':'ST'}
EXTRA=' Use no capitalised word, alias, place, team or title from the page text anywhere in the summary or scenes, and never repeat a run of four words from it. Refer to the entry only by its given name.'
SYS=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'originate_prompt.txt')).read().replace('Return JSON only: {"summary": <2 to 3 sentences, 40-700 characters>, "feats": [ up to 3 ]}.',
 'Return JSON only: {"summary": <2 to 3 sentences, 40-700 characters>, "feats": [ up to 3 ], "realm": one of Arcane|Grounded|Ki|Martial|Mythic|Outer|Stellar, "ceiling_T": <log10 joules of the entry\'s top feat in the source text, 2 to 70>, "powers": [ up to 4 of "id:magnitude" ]}. realm: Arcane magic, Grounded mundane or street level, Ki internal energy, Martial fighting skill, Mythic gods and legends, Outer cosmic, Stellar technology and space. powers: ids from flight glide spectral_flight levitation super_speed dash blink phase super_strength barrage pressure_strike vibrating_palm ki_blast energy_beam fireball freeze_breath whirlwind gravity_repulse flying_sword invulnerability hard_body iron_shirt regeneration qi_heal immortal_body time_stop telepathy invisibility giant_size dragon_form ki_resource; magnitude 1 peak human, 2 city block, 3 building, 4 city, 5 mountain, 6 island, 7 continent, 8 moon, 9 planet, 10 star or universe; only powers the text states.'+EXTRA)
def clean(t):
    t=re.sub(r'\[\[(?:File|Image):[^\]]*\]\]','',t); t=re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]',r'\1',t)
    t=re.sub(r"'{2,}|<ref[^>]*>.*?</ref>|<[^>]+>|\{\{|\}\}",' ',t); t=re.sub(r'\s*\|\s*(\w[\w ]*?)\s*=\s*',r'; \1: ',t)
    return re.sub(r'\s+',' ',t).strip()[:1800]
def master(univ):
    names=set(); pool=[]; eras=[]
    for l in open(MASTER):
        f=l.rstrip('\n').split('\t'); names.add(f[1].lower())
        if f[2]==univ: pool.append(f[1]); eras.append(f[4])
    return names,pool,eras
def build(host,leads,jd,skipf=None):
    univ=json.load(open('/mnt/project-files/assay-c3m/source_universe_map.json'))[host.split('.')[0]]
    names,pool,eras=master(univ); skip=set(open(skipf).read().split('\n')) if skipf else set()
    rnd=random.Random(host); chunks=[n[i:i+rnd.choice((2,3))] for n in pool for i in range(0,len(n)-2,3) if n[i:i+3].isalpha()] or ['va','lo','ri','en']
    os.makedirs(jd,exist_ok=True); seen=set(); n=0
    with open(f'{jd}/{host}.jobs.jsonl','w') as o:
        for l in gzip.open(leads,'rt'):
            r=json.loads(l); t=clean(r['text'])
            if len(t)<80 or r['pid'] in seen or r['title'] in skip or str(r['pid']) in skip: continue
            seen.add(r['pid'])
            while True:
                nm=''.join(rnd.choice(chunks) for _ in range(rnd.choice((2,3)))).capitalize()
                if 5<=len(nm)<=12 and nm.lower() not in names: names.add(nm.lower()); break
            era=rnd.choice(eras or ['E1']); n+=1
            o.write(json.dumps({'id':f'{host}|{r["pid"]}','pid':r['pid'],'title':r['title'],'name':nm,'era':era,'text':t},ensure_ascii=False)+'\n')
    print(n,'jobs')
def api(path,body=None):
    rq=urllib.request.Request('https://api.anthropic.com'+path,data=json.dumps(body).encode() if body else None,headers={'x-api-key':KEY(),'anthropic-version':'2023-06-01','content-type':'application/json'})
    return json.load(urllib.request.urlopen(rq,timeout=300))
def submit(jf,chunk=10000):
    jd=os.path.dirname(jf); bf=jd+'/batches.json'; B=json.load(open(bf)) if os.path.exists(bf) else []
    done={b['first'] for b in B}; jobs=[json.loads(l) for l in open(jf)]
    for i in range(0,len(jobs),chunk):
        part=jobs[i:i+chunk]
        if part[0]['id'] in done: continue
        reqs=[{'custom_id':re.sub(r'[^\w-]','_',j['id']),'params':{'model':os.environ.get('GAP_MODEL','claude-sonnet-5-5'),'max_tokens':1200,'system':[{'type':'text','text':SYS,'cache_control':{'type':'ephemeral'}}],
          'messages':[{'role':'user','content':json.dumps({'name':j['name'],'text':j['text']},ensure_ascii=False)}]}} for j in part]
        while True:
            try: b=api('/v1/messages/batches',{'requests':reqs}); break
            except urllib.error.HTTPError as e:
                if e.code!=429: raise
                time.sleep(120)
        B.append({'id':b['id'],'first':part[0]['id'],'n':len(part),'file':jf}); json.dump(B,open(bf,'w'))
        print('batch',b['id'],len(part),flush=True)
def grams(s,k=4):
    w=re.findall(r"\w+",s.lower()); return {' '.join(w[i:i+k]) for i in range(len(w)-k+1)}
def accept(j,txt,host,univ,n):
    """Validate one model reply for job j; return the entry or raise AssertionError/ValueError/KeyError."""
    d=json.loads(txt[txt.index('{'):txt.rindex('}')+1])
    s=d['summary']; realm=d['realm']; assert realm in R2 and 40<=len(s)<=900 and j['name'].lower() in s.lower()
    assert not (grams(s)&grams(j['text'])), 'copied'
    caps={w for w in re.findall(r'\b[A-Z][a-z]{3,}\b',j['title']+' '+j['text'])}-{'The','This','That','With'}
    assert not [w for w in re.findall(r'\b[A-Z][a-z]{3,}\b',s) if w in caps and w!=j['name']], 'leak'
    ce=float(d['ceiling_T']); assert 1<=ce<=75
    feats=[f for f in d.get('feats',[])[:3] if f.get('axis') in('AP','Dur','v') and (f.get('speed_m_s',0) or 0)<=3e8 and 0<(f.get('energy_J') or f.get('speed_m_s') or 0) and (f.get('energy_J') or 1)<=10**(ce+2)]
    pw=[p for p in d.get('powers',[])[:4] if re.fullmatch(r'[a-z_]+:(10|[1-9])',p)]
    return {'id':f'{R2[realm]}.{univ.lower()}.{j["era"]}.originate.{n}','name':j['name'],'universe':univ,'realm':realm,'era':j['era'],'age':int(j['era'][1:]),'summary':s,'feats':feats,'ceiling_T':d.get('ceiling_T'),'powers':pw,
      'source_wiki':host,'source_page_id':j['pid'],'source_title':j['title'],'source_url':f'https://{host}/wiki/'+j['title'].replace(' ','_')}
def collect(jd,host,univ,outf):
    BA=json.load(open(jd+'/batches.json')); B=[b for b in BA if os.path.basename(b['file']).startswith(host)]
    jobs={re.sub(r'[^\w-]','_',j['id']):j for j in map(json.loads,open(f'{jd}/{host}.jobs.jsonl'))}
    cf=f'/mnt/project-files/compute/id_counters/gap_{host}'; nxt=int(open(cf).read()) if os.path.exists(cf) else 900001
    ok=bad=0; wait=0
    with open(outf,'a') as o:
        for b in B:
            st=api('/v1/messages/batches/'+b['id'])
            if st['processing_status']!='ended': wait+=1; continue
            if b.get('got'): continue
            rq=urllib.request.Request(st['results_url'],headers={'x-api-key':KEY(),'anthropic-version':'2023-06-01'})
            for l in urllib.request.urlopen(rq,timeout=600):
                r=json.loads(l); j=jobs.get(r['custom_id'])
                try:
                    txt=''.join(c.get('text','') for c in r['result']['message']['content'])
                    e=accept(j,txt,host,univ,nxt); nxt+=1; ok+=1
                    o.write(json.dumps(e,ensure_ascii=False)+'\n')
                except Exception: bad+=1
            b['got']=True
    json.dump(BA,open(jd+'/batches.json','w')); open(cf,'w').write(str(nxt)); print('ok',ok,'bad',bad,'waiting batches',wait)
if __name__=='__main__':
    a=sys.argv[1:]
    {'build':lambda:build(*a[1:]),'submit':lambda:submit(a[1],*map(int,a[2:])),'collect':lambda:collect(*a[1:])}[a[0]]()
