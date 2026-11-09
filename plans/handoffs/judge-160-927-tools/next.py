import os,sys
os.chdir('/home/user/global-repo/plans/powers/judge')
k=int(sys.argv[1])
ready=[int(l.split()[0]) for l in open('READY_SHARDS.txt') if l[0].isdigit() and 160<=int(l.split()[0])<=927]
done={int(f[6:-10]) for f in os.listdir('out') if f.endswith('.out.jsonl')}
fl=set(map(int,open('/tmp/claude-0/inflight.txt').read().split()))
nx=[n for n in ready if n not in done and n not in fl][:k]
open('/tmp/claude-0/inflight.txt','a').write(' '+' '.join(map(str,nx)))
print(nx)
