# S6822 Builds library-content/content.sqlite: form, template, owner module, tier per Library entry
# L2C build: library_to_content.tsv + codex store -> library-content/content.sqlite (one row per entry; stats are NOT stored, engine derives them from form+tier)
import sqlite3, sys, csv
OWNER={'MOB':'mobs','BOSS':'ascendant-125','NPC':'settlements','GOD':'magic-shrines','WEAPON':'combat-120','ARMOR':'combat-120','TOOL':'foundry-tech','FOOD':'cuisine','RELIC':'magic','MATERIAL':'foundry-tech','STRUCTURE':'worldgen-133','SETTLEMENT':'worldgen-133','BIOME':'biomes-dims','DIMENSION':'biomes-dims','TECH':'progression-graph','SPELL':'magic','QUEST':'codex-quests','FACTION':'cultures-economy','LORE':'library-only','PACK':'pack-existing'}
TEMPLATE={'MOB':'entity.library_mob','BOSS':'entity.ritual_boss','NPC':'entity.library_npc','GOD':'structure.shrine','WEAPON':'item.library_weapon','ARMOR':'item.library_armor','TOOL':'item.library_tool','FOOD':'item.library_food','RELIC':'item.library_relic','MATERIAL':'item.library_material','STRUCTURE':'structure.library_site','SETTLEMENT':'structure.library_settlement','BIOME':'biome.library_biome','DIMENSION':'dimension.library_world','TECH':'tech.node','SPELL':'magic.rite','QUEST':'quest.codex','FACTION':'faction.reputation','LORE':'book.only','PACK':'existing'}
forms={l.split('\t')[0]:l.split('\t')[1] for l in open(sys.argv[1]).read().splitlines()[1:]}
out=sys.argv[2]; import os
if os.path.exists(out): os.remove(out)
d=sqlite3.connect(out); d.execute("create table content(id text primary key, form text, template text, owner text, tier int, universe text, realm text, era text, name text, pack_id text)")
s=sqlite3.connect('file:/mnt/project-files/codex-store/library.sqlite?mode=ro',uri=True)
rows=[]
for rid,name,u,realm,era,age,pk in s.execute("select id,name,universe,realm,era,age,pack_id from entry"):
    f=forms.get(rid,'PENDING')
    if f=='PENDING': continue
    rows.append((rid,f,TEMPLATE[f],OWNER[f],age,u,realm,era,name,pk))
d.executemany("insert into content values(?,?,?,?,?,?,?,?,?,?)",rows); d.execute("create index c_form on content(form)"); d.commit()
print(len(rows))
