# S6878 localsync.py
# localsync.py: carries local-model jobs and mailbox files between the cloud and the PC through a private git branch (no Actions).
# cloud:  LOCALSYNC_DIR=/home/user/shardfall-game python3 -I localsync.py cloud                       (jobs dir /mnt/project-files/compute/jobs-local, mailbox /mnt/project-files/mailbox)
# PC:     pythonw localsync.py pc E:\DiaithirRPG\compute\jobs-local E:\DiaithirRPG\compute\mailbox   (run every minute, hidden)
# Repo: geddylifeson/shardfall-game (private), branch claude/project-thread-mbokg2, folder local-jobs/. Clone is created next to this script's temp dir.
# Flow: cloud writes jobs/<job>/{in.jsonl,README} and mailbox/{pc,laptop}/*.msg; the PC writes jobs/<job>/out.jsonl and mailbox/coordinator/*.msg.
# No keys or secrets in jobs. Each side only pushes the files it owns, so merges never collide.
import sys,os,subprocess,shutil,pathlib,tempfile
side=sys.argv[1]; J=pathlib.Path(sys.argv[2] if len(sys.argv)>2 else '/mnt/project-files/compute/jobs-local')
M=pathlib.Path(sys.argv[3] if len(sys.argv)>3 else '/mnt/project-files/mailbox')
URL=os.environ.get('LOCALSYNC_REPO','https://github.com/geddylifeson/shardfall-game'); BR='claude/project-thread-mbokg2'
R=pathlib.Path(os.environ.get('LOCALSYNC_DIR') or pathlib.Path(tempfile.gettempdir())/'localsync-repo')  # cloud: LOCALSYNC_DIR=/home/user/shardfall-game (credentialed checkout)
def git(*a,check=True): return subprocess.run(['git','-C',str(R),*a],capture_output=True,text=True,check=check)
if not (R/'.git').exists():
    subprocess.run(['git','clone','-q','--depth=1','-b',BR,URL,str(R)],check=True)
    git('config','user.name','localsync'); git('config','user.email','noreply@anthropic.com')
git('pull','-q','--rebase','origin',BR,check=False)
L=R/'local-jobs'
own_job={'cloud':{'in.jsonl','README','README.md'},'pc':{'out.jsonl'}}[side]
own_mail={'cloud':{'pc','laptop'},'pc':{'coordinator'}}[side]
def cp(a,b):
    if not b.exists() or a.read_bytes()!=b.read_bytes(): b.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(a,b); return 1
    return 0
n=0
# outbound
if J.is_dir():
    for d in J.iterdir():
        for f in (d.iterdir() if d.is_dir() else []):
            if f.name in own_job: n+=cp(f,L/'jobs'/d.name/f.name)
for box in own_mail:
    for f in (M/box).glob('*.msg') if (M/box).is_dir() else []: n+=cp(f,L/'mailbox'/box/f.name)
# inbound (files the other side owns)
inb={'cloud':{'out.jsonl'},'pc':{'in.jsonl','README','README.md'}}[side]
for d in (L/'jobs').iterdir() if (L/'jobs').is_dir() else []:
    for f in d.iterdir():
        if f.name in inb: cp(f,J/d.name/f.name)
inbox={'cloud':{'coordinator'},'pc':{'pc'}}[side]
for box in inbox:
    for f in (L/'mailbox'/box).glob('*.msg') if (L/'mailbox'/box).is_dir() else []: cp(f,M/box/f.name)
if n:
    git('add','-A'); git('commit','-qm',f'localsync {side}: {n} files')
    r=git('push','-q','origin',BR,check=False)
    if r.returncode: git('pull','-q','--rebase','origin',BR,check=False); git('push','-q','origin',BR,check=False)
print(f'{side}: pushed {n}')
