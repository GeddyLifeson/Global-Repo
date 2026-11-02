"""Scan every data/ and design/ file: definitions = first column of each CSV; refs = ID tokens anywhere. Print undefined refs by prefix and folder."""
import csv,re,os,sys,collections,glob
csv.field_size_limit(10**9)
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SKIP=('ui-mockups','audio/samples','__pycache__','merge-report.csv','continuity')
PFX=sys.argv[1].split(',') if len(sys.argv)>1 else ['LOC','QST','ACT','ITM','FLG','CDX','ACH','MQ','SQ','FQ','CQ','REG','BPH','MOV','ABL','RES','PRK','SKL','STK','PVP_MAP','VEH','SSN','EVT','ENC','STR']
tok=re.compile(r'\b(?:%s)_[A-Z0-9][A-Z0-9_]*\b'%'|'.join(PFX))
files=[]
for dp,dn,fn in os.walk(ROOT):
  if any(s in dp for s in SKIP): continue
  for f in fn:
    if f.endswith(('.csv','.md','.json','.txt')) and not any(s in f for s in SKIP): files.append(os.path.join(dp,f))
defs=set(); refs=collections.defaultdict(set)
for p in files:
  if p.endswith('.csv'):
    try:
      for i,row in enumerate(csv.reader(open(p,encoding='utf-8',errors='replace'))):
        if i and row: defs.add(row[0].strip())
    except Exception as e: print('ERR',p,e)
for p in files:
  rel=os.path.relpath(p,ROOT)
  for m in tok.findall(open(p,encoding='utf-8',errors='replace').read()):
    if m.endswith('_'): continue
    refs[m].add(rel)
def ok(t):
  if t in defs: return True
  # pattern refs like FOO_* handled by endswith; allow prefix-of-defined (IDs used as families)
  return False
und=collections.Counter(); byfolder=collections.defaultdict(collections.Counter); ex=collections.defaultdict(list)
for t,srcs in refs.items():
  if ok(t): continue
  p=t.split('_')[0]
  for s in srcs:
    f='/'.join(s.split('/')[:3]) if s.startswith('design/levels') else '/'.join(s.split('/')[:2])
    byfolder[p][f]+=1
  und[p]+=1; ex[p].append(t)
for p,n in und.most_common():
  print(p,n,'eg',sorted(ex[p])[:4],dict(byfolder[p].most_common(6)))
print('defs',len(defs),'files',len(files))
