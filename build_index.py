# S0002 build_index.py: assigns stable IDs (ids.tsv: id,device,path) and renders SCRIPTS_INDEX.md from <device>_inventory.tsv files.
import csv,os,sys,glob
R=sys.argv[1]; ids={}; 
idf=os.path.join(R,'ids.tsv')
if os.path.exists(idf):
    for r in csv.reader(open(idf),delimiter='\t'): ids[(r[1],r[2])]=r[0]
n=max([int(v[1:]) for v in ids.values()]+[0])
rows=[]
for f in sorted(glob.glob(os.path.join(R,'*_inventory.tsv')),key=lambda x:(not os.path.basename(x).startswith('global'),x)):
    dev=os.path.basename(f).split('_')[0]
    for r in list(csv.reader(open(f),delimiter='\t'))[1:]:
        k=(dev,r[0])
        if k not in ids: n+=1; ids[k]='S%04d'%n
        rows.append((ids[k],dev,r[0],r[1],r[2] if len(r)>2 else '',r[3] if len(r)>3 else ''))
with open(idf,'w',newline='') as o:
    w=csv.writer(o,delimiter='\t')
    for (d,p),i in sorted(ids.items(),key=lambda x:x[1]): w.writerow([i,d,p])
rows.sort()
out=['# Global script catalogue','',
'Every script, one stable ID. Borrow by ID; copies live in this repo under `<device>/<path>` when marked yes. Source of truth for IDs: `ids.tsv`. Rebuild with S0002 (`python3 build_index.py <repo>`).','',
'Devices: `cloud` = /mnt/project-files (shared folder), `pc` = Fountain-of-Lateralus-Rex, `laptop` = MSI.','',
'Run hints: .py `python3 <file>` (PC `py`), .ps1 via a hidden launcher (never a visible window), .sh `bash`, .js/.mjs `node`. Norton deletes .bat, so avoid it.','',
'| ID | Device | Path | What | Copy |','|---|---|---|---|---|']
for i,d,p,sz,w,c in rows: out.append(f'| {i} | {d} | `{p}` | {w.replace("|","/")} | {c} |')
open(os.path.join(R,'SCRIPTS_INDEX.md'),'w').write('\n'.join(out)+'\n')
print(n)
