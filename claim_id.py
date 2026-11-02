# S0322 claim_id.py: atomically claim the next free script ID. python3 -I claim_id.py [count]  -> prints the IDs.
# Rebases onto origin/main, bumps ./next_id, commits and pushes just that file; retries if another registrar won the race.
import subprocess,sys,pathlib
R=pathlib.Path(__file__).parent; n=int(sys.argv[1]) if len(sys.argv)>1 else 1
def g(*a): return subprocess.run(['git','-C',str(R),*a],capture_output=True,text=True)
for _ in range(8):
    g('pull','-q','--rebase','--autostash','origin','main')
    cur=int((R/'next_id').read_text().strip()); (R/'next_id').write_text(str(cur+n)+'\n')
    g('add','next_id'); g('commit','-qm',f'claim S{cur:04d}-S{cur+n-1:04d}')
    if g('push','-q','origin','main').returncode==0:
        print(' '.join(f'S{i:04d}' for i in range(cur,cur+n))); sys.exit(0)
    g('reset','-q','--hard','origin/main')
sys.exit('could not claim an ID')
