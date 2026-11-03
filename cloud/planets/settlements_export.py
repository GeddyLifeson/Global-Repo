# Per-planet settlement table for the structures/NPC lanes: python3 -I settlements_export.py
# One row per SETTLEMENT entry on the planet (real Library entries), tied to one of the planet's own biomes by hash.
import sqlite3,json,pathlib,hashlib,collections
R=pathlib.Path('/mnt/project-files'); O=R/'planets'; (O/'settlements').mkdir(exist_ok=True)
c=sqlite3.connect(f'file:{R}/library-content/content.sqlite?mode=ro',uri=True)
s=sqlite3.connect('file:/mnt/attach/project-files/codex-store/library.sqlite?mode=ro',uri=True)
P={p['name']:p for p in json.load(open(O/'planets.json'))}
rows=collections.defaultdict(list)
for i,u,t,e,n in c.execute("select id,universe,tier,era,name from content where form='SETTLEMENT'"): rows[u].append((i,n,t,e))
idx=[]
for u,r in rows.items():
    pid=P[u]['planet_id']; f=O/'specs'/(pid+'.json')
    if pid=='diaithir' or not f.exists(): continue
    bio=[b['entry'] for b in json.load(open(f))['biomes']]
    with open(O/'settlements'/(pid+'.tsv'),'w') as out:
        out.write('entry_id\tname\ttier\tera\tbiome_entry\n')
        for i,n,t,e in sorted(r):
            out.write(f"{i}\t{n}\t{t}\t{e}\t{bio[int(hashlib.sha256(i.encode()).hexdigest(),16)%len(bio)]}\n")
    idx.append((pid,len(r)))
open(O/'settlements_index.tsv','w').write('planet_id\tsettlements\n'+''.join(f'{a}\t{b}\n' for a,b in sorted(idx)))
print(len(idx),'planets',sum(b for a,b in idx),'settlements')
