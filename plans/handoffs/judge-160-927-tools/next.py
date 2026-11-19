import os,sys
os.chdir('/home/user/global-repo/plans/powers/judge')
k=int(sys.argv[1])
ready=[int(l.split()[0]) for l in open('READY_SHARDS.txt') if l[0].isdigit() and 160<=int(l.split()[0])<=927]
done={int(f[6:-10]) for f in os.listdir('out') if f.endswith('.out.jsonl')}
fl=set(map(int,open('/tmp/claude-0/inflight.txt').read().split()))
import json
def blank(n): return sum(1 for l in open(f'batches/shard_{n}.src.jsonl') if l.strip() and not json.loads(l)['url'])
nx=[];skip=[]
for n in ready:
    if n in done or n in fl or len(nx)>=k: continue
    (skip if blank(n)>5 else nx).append(n)
open('/tmp/claude-0/inflight.txt','a').write(' '+' '.join(map(str,skip)));open('/tmp/claude-0/prescreen_hold.txt','a').write(' '.join(map(str,skip))+'\n')
open('/tmp/claude-0/inflight.txt','a').write(' '+' '.join(map(str,nx)))
print(nx)
