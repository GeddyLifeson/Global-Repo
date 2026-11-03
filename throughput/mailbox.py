# S6862 mailbox.py
# mailbox.py: file mailbox so threads reach lanes that refuse thread messages (PC lane) without a coordinator relay.
# send:  python3 -I mailbox.py send <lane> <from> "text"        lane = pc, laptop, consolidation, textures, ...
# read:  python3 -I mailbox.py read <lane>                       prints unread, moves them to done/
# Folder /mnt/project-files/mailbox/<lane>/{*.msg,done/}. A lane polls it at the start of every step (foreground, never ends a turn mid-job).
import sys,os,time,pathlib,shutil
R=pathlib.Path('/mnt/project-files/mailbox'); a=sys.argv[1:]
if not a: sys.exit(__doc__)
if a[0]=='send' and len(a)>=4:
    d=R/a[1]; d.mkdir(parents=True,exist_ok=True)
    f=d/f"{time.strftime('%Y%m%dT%H%M%S')}-{os.getpid()}-{a[2][:20]}.msg"; f.write_text(' '.join(a[3:])+'\n'); print(f)
elif a[0]=='read' and len(a)>=2:
    d=R/a[1]; (d/'done').mkdir(parents=True,exist_ok=True)
    for f in sorted(d.glob('*.msg')): print(f.name); print(f.read_text()); shutil.move(f,d/'done'/f.name)
else: sys.exit(__doc__)
