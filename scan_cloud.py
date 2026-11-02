# S0001 scripts-index builder: scans /mnt/project-files, copies non-secret scripts into the repo, emits cloud TSV.
import os,re,sys,shutil,csv
SRC='/mnt/project-files'; DST=sys.argv[1]
EXT={'.py','.ps1','.sh','.js','.mjs','.vbs','.cmd','.bat','.psm1'}
SKIP={'archive','secrets','node_modules','.git','withdrawn'}
SEC=re.compile(r'(sk-ant-[A-Za-z0-9_-]{10,}|gh[pous]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,}|gsk_[A-Za-z0-9]{20,}|[\w.+-]+@[\w-]+\.(com|net|org)|api[_-]?key\s*[=:]\s*[\'"][^\'"]{12,})',re.I)
rows=[]
for d,ds,fs in os.walk(SRC):
    ds[:]=[x for x in ds if x not in SKIP]
    for f in fs:
        if os.path.splitext(f)[1].lower() not in EXT: continue
        p=os.path.join(d,f); rel=os.path.relpath(p,SRC); sz=os.path.getsize(p)
        try: t=open(p,encoding='utf-8',errors='replace').read()
        except Exception: continue
        doc=''
        for l in t.splitlines()[:25]:
            s=l.strip().lstrip('#/*"\' ').strip()
            if len(s)>8 and not s.startswith(('!','import','using','$','from','param','@echo')) and not s.startswith('/usr'):
                doc=s[:140];break
        copied='no'
        if sz<200_000:
            t2=SEC.sub('REDACTED',t)
            o=os.path.join(DST,'cloud',rel); os.makedirs(os.path.dirname(o),exist_ok=True)
            open(o,'w',encoding='utf-8').write(t2); copied='yes'+('*' if t2!=t else '')
        rows.append((rel,sz,doc,copied))
rows.sort()
with open(os.path.join(DST,'cloud_inventory.tsv'),'w',newline='') as o:
    w=csv.writer(o,delimiter='\t');w.writerow(['path','bytes','what','copied']);w.writerows(rows)
print(len(rows))
