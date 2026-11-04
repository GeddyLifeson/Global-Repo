# usage: python3 gen.py <shard> '<json cfg>'  cfg: b0 [idx], w/a/v [idx gear weapon/armor/vehicle], n {idx:name}, p {idx:[{id,m,q,c}]}, x {idx:[..]}, vam [idx] (adds vampirism), were [idx] (lycanthropy)
import json,re,sys
d='/mnt/project-files/plans/powers/judge/inthread/'
n=int(sys.argv[1]); c=json.loads(sys.argv[2]); g=lambda k:{int(a):b for a,b in c.get(k,{}).items()}
b0=set(c.get('b0',[])); kind={}
for k,v in (('w','weapon'),('a','armor'),('v','vehicle')):
    for i in c.get(k,[]): kind[i]=v
names=g('n'); P=g('p'); X=g('x')
for i in c.get('vam',[]): X.setdefault(i,[]).append('vampirism')
for i in c.get('were',[]): X.setdefault(i,[]).append('lycanthropy')
R=[json.loads(l) for l in open(f'{d}shard_{n:02d}.jsonl')]
out=[]
for i,r in enumerate(R):
    t=r['text']
    if i in b0: out.append({'id':r['id'],'b':0});continue
    if i in names: nm=names[i]
    elif re.match(r'(is|was|are|were|This)\b|[(,]',t): nm=''
    else:
        nm=re.split(r' \(|, | (?:is|was|are|were) ',t,maxsplit=1)[0]
        if i in kind: nm=re.sub(r'^(The|A|An) ','',nm)
    if len(nm)>=60: nm=' '.join(nm.split()[:2]); print('trunc',i,nm)
    assert nm in t and len(nm)<60,(i,nm)
    ps=P.get(i,[])
    for p in ps: assert p['q'] in t and 1<=p['m']<=10,(i,p)
    if i in kind: out.append({'id':r['id'],'b':2,'k':kind[i],'n':nm,'m':1,'q':'','c':'l','p':ps,'x':X.get(i,[])})
    else: out.append({'id':r['id'],'b':1,'n':nm,'p':ps,'x':X.get(i,[])})
missing=[i for i in range(len(R)) if i not in b0 and i not in names and False]
open(f'{d}shard_{n:02d}.out.jsonl','w').write(''.join(json.dumps(o)+'\n' for o in out))
print(len(out),[(i,o['n']) for i,o in enumerate(out) if o.get('n') and len(o['n'])>28])
