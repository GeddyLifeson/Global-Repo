# S6946 apply_ages.py: add tech_ages.json Age (authoritative) next to the draft Age in ITEM_ROLES.csv; counts drafts that differ. python3 -I apply_ages.py <tech_ages.json> <roles.csv>
import sys,csv,json,re,collections
t=json.load(open(sys.argv[1]));P=sys.argv[2]
rom=re.compile(r'\bAge (VIII|VII|VI|IV|V|III|II|I)\b')
def age(i):
    return t.get('items',{}).get(i) or t['decided'].get(i) or t['namespaces'].get(i.split(':')[0]) or ''
R=list(csv.DictReader(open(P)));F=[f for f in R[0] if f not in('age','draft_age')]
diff=collections.Counter();thin=('VIII','RODOS','V','II')
for r in R:
    m=rom.search(r['where']);r['draft_age']=m.group(1) if m else ''
    r['age']=age(r['id']) or r['draft_age']
    if r['draft_age'] and age(r['id']) and r['draft_age']!=age(r['id']): diff[(r['draft_age'],age(r['id']))]+=1
w=csv.DictWriter(open(P,'w',newline=''),F+['age','draft_age']);w.writeheader();w.writerows(R)
n=collections.Counter(r['age'] for r in R)
print('rows',len(R),'ages',dict(n));print('draft differs from tech_ages:',sum(diff.values()),diff.most_common(6))
