# S6861 merge_order.py
# merge_order.py: merge order for stacked PRs. python3 -I merge_order.py ports.json rpg.json > MERGE_ORDER.csv
# Inputs: JSON lists as returned by the GitHub list_pull_requests tool (number, title, head.ref, base.ref, draft).
# Output CSV: wave, repo, number, base, head, partner, title. Wave 0 = base is not an open PR head (merge any time, any order).
# Wave n = stacked n levels deep; merge a wave only after the wave above it. partner = same head branch in the other repo (merge together).
import json,sys,csv
def load(p):
    d=json.load(open(p))
    if d and 'text' in d[0]: d=json.loads(d[0]['text'])
    return d
repos={'ports':load(sys.argv[1]),'rpg':load(sys.argv[2])}
rows=[]
for r,d in repos.items():
    by={p['head']['ref']:p for p in d}
    def wave(p):
        b=by.get(p['base']['ref']); return 0 if not b else 1+wave(b)
    for p in d: rows.append((wave(p),r,p['number'],p['base']['ref'],p['head']['ref'],p['title']))
heads={}
for w,r,n,b,h,t in rows: heads.setdefault(h,[]).append((r,n))
rows.sort(key=lambda x:(x[0],x[1],x[2]))
out=csv.writer(sys.stdout)
out.writerow(['wave','repo','number','base','head','partner','title'])
for w,r,n,b,h,t in rows:
    pt=' '.join(f'{rr}#{nn}' for rr,nn in heads[h] if rr!=r)
    out.writerow([w,r,n,b,h,pt,t[:90]])
