# S6828 Build Codex quest store from Library QUEST entries (real summary text, Age-gated)
import sqlite3, json, os, sys
C='/mnt/project-files/library-content/content.sqlite'
L='/mnt/project-files/codex-store/library.sqlite'
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'quests.sqlite')
if os.path.exists(OUT): os.remove(OUT)
o=sqlite3.connect(OUT)
o.execute("create table quest(id text primary key,title text,summary text,age int,tier int,universe text,realm text,era text,spine text,objective text)")
o.execute("create index q_age on quest(age,universe)")
c=sqlite3.connect('file:'+C+'?mode=ro',uri=True); c.execute("attach database 'file:"+L+"?mode=ro' as l") if False else None
l=sqlite3.connect('file:'+L+'?mode=ro',uri=True)
text={r[0]:r for r in l.execute("select id,name,summary,age from entry where kind='event'") } if False else None
miss=0;n=0
for id,name,tier,uni,realm,era,spine in c.execute("select id,name,tier,universe,realm,era,spine from content where form='QUEST'"):
    r=l.execute("select name,summary,age from entry where id=?",(id,)).fetchone()
    if not r or not (r[1] or '').strip(): miss+=1; continue
    # objective: read-the-entry only; no invented tasks
    o.execute("insert into quest values(?,?,?,?,?,?,?,?,?,?)",(id,r[0],r[1].strip(),r[2],tier,uni,realm,era,spine,'read_entry'))
    n+=1
o.commit()
print('quests',n,'missing text',miss)
for a,k in o.execute("select age,count(*) from quest group by 1"):print('age',a,k)
