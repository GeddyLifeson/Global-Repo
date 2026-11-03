# S6823 Gives every Library entry a Collection, class, canon status, spine code and shelfmark from its soil
# L2C place_all: gives every Library entry a Collection, class, canon status, spine code and Panscriptum shelfmark. Usage: place_all.py content.sqlite placement.json
import sqlite3, json, sys, collections
SOIL={'Martial':('Frost','R','Hull'),'Ki':('Ember','S','Lamplighter'),'Arcane':('Bloom','T','Reader'),'Stellar':('Iron','U','Salvager'),'Mythic':('Storm','V','Chorister'),'Grounded':('Hollow','W','Hand'),'Outer':('Quiet','X','Custodian')}
CHARTER={'Diaithir':'II.L.8','Shardfall':'II.F.9'}  # decided by the owner 2026-10-18
COLL={'MOB':('IV','Beast'),'BOSS':('V','Person'),'NPC':('V','Person'),'GOD':('III','God'),'WEAPON':('VI','Relic'),'ARMOR':('VI','Relic'),'TOOL':('VI','Relic'),'RELIC':('VI','Relic'),'FOOD':('VI','Substance'),'MATERIAL':('VI','Substance'),
 'STRUCTURE':('II','World'),'SETTLEMENT':('II','World'),'BIOME':('II','World'),'DIMENSION':('II','World'),'FACTION':('II','Polity'),'SPELL':('VII','Praxis'),'TECH':('VII','Praxis'),'QUEST':('VIII','Event'),'LORE':('VIII','Event'),'PACK':('VI','Relic')}
d=sqlite3.connect(sys.argv[1])
us=d.execute("select universe,realm,count(*) from content group by 1,2").fetchall()
byrealm=collections.defaultdict(list)
for u,r,n in us:
    if u not in CHARTER: byrealm[r].append(u)
place={}
for r,l in byrealm.items():
    soil,let,office=SOIL[r]
    for i,u in enumerate(sorted(l,key=str.lower),1): place[u]=(f'II.{let}.{i}',soil,office,r)
for u,code in CHARTER.items():
    r=[x[1] for x in us if x[0]==u]
    if r: place[u]=(code,SOIL[r[0]][0],SOIL[r[0]][2],r[0])
shelf={u:f"Ω › H? › X? › Mt.{p[1]} › Mv.? › U-{p[0]} (provisional)" for u,p in place.items()}
for col in ('collection','class','canon_status','spine','shelfmark'):
    try: d.execute(f"alter table content add column {col} text")
    except sqlite3.OperationalError: pass
rows=[]
for rid,f,u in d.execute("select id,form,universe from content").fetchall():
    c,k=COLL[f]; rows.append((c,k,'Omniverse canon',place[u][0],shelf[u],rid))
d.executemany("update content set collection=?,class=?,canon_status=?,spine=?,shelfmark=? where id=?",rows)
d.commit()
json.dump({u:{'spine':p[0],'soil':p[1],'office':p[2],'realm':p[3],'shelfmark':shelf[u]} for u,p in sorted(place.items())},open(sys.argv[2],'w'),indent=1)
print(len(place),'universes placed;',d.execute("select count(*) from content where spine is null").fetchone()[0],'entries without spine')
print(collections.Counter(p[0].split('.')[1] for p in place.values()))
