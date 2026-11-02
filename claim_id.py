# S0322 claim_id.py: atomically claim the next free ID. python3 -I claim_id.py [PREFIX] [count]  (PREFIX S script, D doc, F data, M module/jar, A art set, J compute job, T thread, P PR/branch)
# Rebases onto origin/main, bumps ./next_id (S) or ./next_<PREFIX>, commits and pushes just that file; retries if another registrar won the race.
import subprocess,sys,pathlib
R=pathlib.Path(__file__).parent; a=sys.argv[1:]
P=a.pop(0) if a and a[0].isalpha() else 'S'; n=int(a[0]) if a else 1
f=R/('next_id' if P=='S' else 'next_'+P)
def g(*x): return subprocess.run(['git','-C',str(R),*x],capture_output=True,text=True)
for _ in range(8):
    g('pull','-q','--rebase','--autostash','origin','main')
    cur=int(f.read_text().strip()) if f.exists() else 1; f.write_text(str(cur+n)+'\n')
    g('add',f.name); g('commit','-qm',f'claim {P}{cur:04d}-{P}{cur+n-1:04d}')
    if g('push','-q','origin','main').returncode==0:
        print(' '.join(f'{P}{i:04d}' for i in range(cur,cur+n))); sys.exit(0)
    g('reset','-q','--hard','origin/main')
sys.exit('could not claim an ID')
