# S0336 add_rows.py: register rows of a hand-fed type (T threads, P PRs/branches) with stable IDs. python3 -I add_rows.py <repo> <PREFIX>  < tsv(key<TAB>meta)
# Existing keys keep their ID and get their meta updated. IDs come from claim_id.py (no clashes). Paths/metadata only, never secrets or emails.
import sys,csv,subprocess,pathlib
R=pathlib.Path(sys.argv[1]).resolve(); P=sys.argv[2]
rows=[l.rstrip('\n').split('\t',1) for l in sys.stdin if l.strip()]
(R/'registry').mkdir(exist_ok=True); (R/'catalog').mkdir(exist_ok=True)
rf=R/'registry'/f'{P}.tsv'; cf=R/'catalog'/f'{P}.tsv'
reg={r[1]:r[0] for r in csv.reader(open(rf),delimiter='\t')} if rf.exists() else {}
meta={r[1]:r[2] for r in list(csv.reader(open(cf),delimiter='\t'))[1:]} if cf.exists() else {}
new=[k for k,_ in rows if k not in reg]
if new:
    ids=subprocess.run([sys.executable,'-I',str(R/'claim_id.py'),P,str(len(new))],capture_output=True,text=True,check=True).stdout.split()
    reg.update(zip(new,ids))
for k,m in rows: meta[k]=m if len(rows[0])>1 else ''
csv.writer(open(rf,'w',newline=''),delimiter='\t').writerows(sorted((i,k) for k,i in reg.items()))
w=csv.writer(open(cf,'w',newline=''),delimiter='\t'); w.writerow(['id','path','meta'])
for k in sorted(meta,key=lambda k:reg[k]): w.writerow([reg[k],k,meta[k]])
print(len(new),'new',len(meta),'total')
