"""Compare names given next to IDs in every CSV with the canonical name (world locations, data actors/npcs/quests/items)."""
import csv,os,collections,sys
csv.field_size_limit(10**9)
R=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
canon={}
def load(p,idc,nc):
  for r in csv.DictReader(open(R+'/'+p)):
    if r.get(idc) and r.get(nc): canon.setdefault(r[idc],(r[nc],p))
load('design/world/locations.csv','loc_id','name')
load('data/actors/bosses.csv','ACT_ID','Boss'); load('data/actors/enemies.csv','ACT_ID','Name')
load('data/world/npcs.csv','act_id','name'); load('data/world/quests.csv','qst_id','name')
load('data/items/items_index.csv','item_id','name'); load('data/actors/factions.csv','FAC_ID','Faction')
NAMECOLS=('name','boss','boss_name','npc_name','display_name','place_name','location_name','title','quest_name','name_en','text_en','Name','Boss','world_name','loc_name')
out=[]
for dp,dn,fn in os.walk(R):
  if any(s in dp for s in ('ui-mockups','samples','continuity','__pycache__','design/audit')): continue
  for f in fn:
    if not f.endswith('.csv') or f=='merge-report.csv': continue
    p=os.path.join(dp,f); rel=os.path.relpath(p,R)
    try: rd=csv.reader(open(p,errors='replace')); hdr=next(rd)
    except StopIteration: continue
    ncols=[i for i,h in enumerate(hdr) if h.strip() in NAMECOLS]
    if not ncols: continue
    for row in rd:
      if not row: continue
      ids=[c for c in row[:3] if c in canon]
      if not ids: continue
      i=ids[0]; cn,src=canon[i]
      if rel==src: continue
      for nc in ncols[:1]:
        if nc<len(row) and row[nc] and hdr[nc]!='text_en' or (hdr[nc]=='text_en' and row[1].endswith('_NAME') if len(row)>1 else False):
          v=row[nc].strip()
          if v and v.lower().strip('. ')!=cn.lower() and v.lower().lstrip('the ')!=cn.lower().lstrip('the '):
            out.append((rel,i,v,cn,src))
w=csv.writer(open(R+'/design/continuity/names_raw.csv','w',newline='')); w.writerow(['file','id','name_here','canonical','canonical_source']); w.writerows(out)
c=collections.Counter(o[0] for o in out)
for k,v in c.most_common(40): print(v,k)
print(len(out))
