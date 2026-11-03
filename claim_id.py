# S0322 claim_id.py: atomically claim the next free ID. python3 -I claim_id.py [PREFIX] [count] [note]
# PREFIX: S script, D doc, F data, M module/jar, A art set, J compute job, T thread, P PR/branch, L laptop project, B backend, G game, R PC project, I program.
# Counter of record = /mnt/project-files/compute/id_counters/<PREFIX> (shared by every thread, no GitHub push needed), guarded by an atomic mkdir lock.
# Also mirrors the new value into the repo's next_id / next_<PREFIX> file (commit it with your next change) and logs the claim to id_counters/claims.log.
# Falls back to the repo file when the shared folder is missing. Never picks by hand; S starts at 6816.
import sys,os,time,pathlib,datetime
a=sys.argv[1:]; P=a.pop(0) if a and a[0].isalpha() and len(a[0])==1 else 'S'
n=int(a.pop(0)) if a and a[0].isdigit() else 1; note=' '.join(a)[:100]
R=pathlib.Path(__file__).resolve().parent; D=pathlib.Path('/mnt/project-files/compute/id_counters')
repo=R/('next_id' if P=='S' else 'next_'+P)
floor=6816 if P=='S' else 1
if D.is_dir():
    lock=D/(P+'.lock'); t0=time.time()
    while True:
        try: os.mkdir(lock); break
        except FileExistsError:
            if time.time()-lock.stat().st_mtime>30: 
                try: os.rmdir(lock)
                except OSError: pass
            elif time.time()-t0>60: sys.exit('lock timeout')
            else: time.sleep(0.3)
    try:
        f=D/P
        cur=max(int(f.read_text().strip()) if f.exists() else 1, int(repo.read_text().strip()) if repo.exists() else 1, floor)
        f.write_text(str(cur+n)+'\n')
        open(D/'claims.log','a').write(f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ} {P}{cur:04d}-{P}{cur+n-1:04d} {note}\n")
    finally: os.rmdir(lock)
else:
    cur=max(int(repo.read_text().strip()) if repo.exists() else 1,floor)
repo.write_text(str(cur+n)+'\n')
print(' '.join(f'{P}{i:04d}' for i in range(cur,cur+n)))
