# S0335 crawl_all.py: keeps the global catalogue current. Crawls /mnt/project-files, assigns stable IDs per type, writes catalog/<type>.tsv (paths and metadata only; no file contents beyond a title line).
# Types: D docs (.md .txt .html), F data (.csv .tsv .json .dat), M modules (.jar, parts folded), A art sets (dirs of images), J compute jobs. T threads and P PRs come from catalog/T.tsv and catalog/P.tsv (written by sessions via add_row).
# Run: python3 -I crawl_all.py <repo>    (then commit + push; IDs come from claim_id.py so threads never clash)
import os,re,sys,csv,subprocess,pathlib,collections
SRC='/mnt/project-files'; R=pathlib.Path(sys.argv[1]).resolve()
SKIP_DIR={'archive','secrets','node_modules','.git','withdrawn','staged','uploads','screenshots','shots'}
SKIP_NAME=re.compile(r'(secret|token|password|credential|\.env|_key|anthropic_key|apikey)',re.I)
IMG={'.png','.jpg','.jpeg','.webp','.gif','.ogg','.wav','.mp3'}
MB=3_000_000
def title(p):
    try:
        for l in open(p,encoding='utf-8',errors='replace'):
            s=l.strip().lstrip('#').strip()
            if len(s)>3: return re.sub(r'[\w.+-]+@[\w-]+\.\w+','',s)[:120]
    except Exception: pass
    return ''
rec=collections.defaultdict(dict)  # type -> key -> meta
imgdirs=collections.defaultdict(lambda:[0,0])
for d,ds,fs in os.walk(SRC):
    rel=os.path.relpath(d,SRC); top=rel.split(os.sep)[0]
    ds[:]=[x for x in ds if x not in SKIP_DIR]
    if rel.startswith('compute'+os.sep+'jobs') and rel.count(os.sep)>=2: ds[:]=[]
    if rel=='compute'+os.sep+'jobs':
        for j in ds: 
            jp=os.path.join(d,j); n=sum(len(f) for _,_,f in os.walk(jp)); rec['J'][os.path.join(rel,j)]=f'{n} files'
    for f in fs:
        if SKIP_NAME.search(f): continue
        p=os.path.join(d,f); r=os.path.join(rel,f) if rel!='.' else f; ext=os.path.splitext(f)[1].lower()
        try: sz=os.path.getsize(p)
        except OSError: continue
        if ext in('.md','.txt','.html') and sz<MB: rec['D'][r]=title(p)+f' | {sz} B'
        elif ext in('.csv','.tsv','.json','.dat') and not rel.startswith('compute'+os.sep+'jobs'): rec['F'][r]=f'{sz} B'
        elif ext=='.jar' or re.search(r'\.jar\.part000$',f):
            k=r.replace('.part000',''); rec['M'][k]=f'{sz} B'+(' (split)' if 'part000' in f else '')
        elif ext in IMG:
            imgdirs[rel][0]+=1; imgdirs[rel][1]+=sz
for k,(n,sz) in imgdirs.items():
    if n>=3: rec['A'][k]=f'{n} images, {sz//1024} KB'
def claim(P,n): return subprocess.run([sys.executable,'-I',str(R/'claim_id.py'),P,str(n)],capture_output=True,text=True,check=True).stdout.split()
(R/'catalog').mkdir(exist_ok=True); (R/'registry').mkdir(exist_ok=True)
for P in 'DFMAJ':
    reg={}; rf=R/'registry'/f'{P}.tsv'
    if rf.exists(): reg={r[1]:r[0] for r in csv.reader(open(rf),delimiter='\t')}
    new=[k for k in sorted(rec[P]) if k not in reg]
    if new:
        for k,i in zip(new,claim(P,len(new))): reg[k]=i
    with open(rf,'w',newline='') as o: csv.writer(o,delimiter='\t').writerows(sorted(((i,k) for k,i in reg.items())))
    with open(R/'catalog'/f'{P}.tsv','w',newline='') as o:
        w=csv.writer(o,delimiter='\t'); w.writerow(['id','path','meta'])
        for k in sorted(rec[P]): w.writerow([reg[k],k,rec[P][k]])
    print(P,len(rec[P]),len(new),'new')
