#!/usr/bin/env python3
"""python3 validate_coat.py <group>  (checks catalogue/coat_<group>.psv against <group>.psv ids)"""
import sys,re,json,os
H=os.path.dirname(os.path.abspath(__file__)); g=sys.argv[1]
UW=json.load(open(H+'/uw_existing.json'))
src=[l.split('|') for l in open(f'{H}/catalogue/{g}.psv',encoding='utf8') if l.strip() and not l.startswith('#')]
ids={f[0]:f[3] for f in src}
P=set("none spots stripes bands mane saddle mask blotch diamond mottled countershade eyespot rosettes".split())
seen=set(); e=[]
for i,l in enumerate(open(f'{H}/catalogue/coat_{g}.psv',encoding='utf8'),1):
    if not l.strip() or l.startswith('#'): continue
    f=l.rstrip('\n').split('|')
    if len(f)!=7: e.append(f'{i}: {len(f)} fields'); continue
    id_,d,b,a,bl,p,_=f
    if id_ not in ids: e.append(f'{i}: unknown id {id_}'); continue
    seen.add(id_)
    for c in (b,a,bl):
        if not re.fullmatch(r'#[0-9a-fA-F]{6}',c): e.append(f'{i}: colour {c}')
    if p not in P: e.append(f'{i}: pattern {p}')
    if ids[id_].startswith('uw:'):
        fam,_,sp=d.partition('/')
        if sp not in UW.get(fam,[]) or fam!=ids[id_][3:]: e.append(f'{i}: donor {d} for plan {ids[id_]}')
    elif d!='-': e.append(f'{i}: donor must be - for gen plan')
miss=set(ids)-seen
print(len(seen),'coats,',len(miss),'missing,',len(e),'errors'); print('\n'.join(e[:30])); print('missing:',sorted(miss)[:15])
sys.exit(1 if e or miss else 0)
