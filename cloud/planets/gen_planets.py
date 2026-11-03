# S6830 gen_planets.py: Panscriptum planets, one per store universe (planets.tsv, dimension datapack)
# Panscriptum planets: one planet per store universe. python3 -I gen_planets.py
# Reads library-content/content.sqlite + universe_placement.json; writes planets.tsv/json, datapack/, lang. Data only, no jars.
import sqlite3,json,re,hashlib,pathlib
R=pathlib.Path('/mnt/project-files'); O=R/'planets'
c=sqlite3.connect(f'file:{R}/library-content/content.sqlite?mode=ro',uri=True)
P=json.load(open(R/'library-content/universe_placement.json'))
FORMS=['NPC','MOB','BOSS','WEAPON','ARMOR','TOOL','RELIC','SPELL','TECH','QUEST','FACTION','STRUCTURE','SETTLEMENT','BIOME','DIMENSION','GOD','FOOD','MATERIAL','LORE','PACK']
# soil -> (dimension_type, noise_settings, biome_source preset)
HOST={'Bloom':('overworld','overworld','overworld'),'Frost':('overworld','amplified','overworld'),
 'Storm':('overworld','floating_islands','overworld'),'Hollow':('overworld_caves','caves','overworld'),
 'Ember':('the_nether','nether','nether'),'Iron':('overworld','large_biomes','overworld'),'Quiet':('the_end','end','end')}
rows={}
for u,tier,n in c.execute("select universe,tier,count(*) from content group by 1,2"):
    r=rows.setdefault(u,{'tiers':{}}); r['tiers'][tier]=n
for u,f,n in c.execute("select universe,form,count(*) from content group by 1,2"):
    rows[u].setdefault('forms',{})[f]=n
out=[]
for u,p in P.items():
    r=rows[u]; t=r['tiers']; tot=sum(t.values())
    age=min([k for k,v in t.items() if v>=50] or [min(t)])
    slug=re.sub(r'[^a-z0-9_]','_',u.lower()); soil=p['soil']
    dt,ns,bs=HOST[soil]
    if u=='Diaithir': dt=ns=bs='terra'
    out.append(dict(planet_id=slug,name=u,dimension='diaithir_planets:'+slug if u!='Diaithir' else 'minecraft:overworld',
      soil=soil,realm=p['realm'],spine=p['spine'],shelfmark=p['shelfmark'],office=p['office'],
      opens_age=age,ages=sorted(t),entries=tot,dimension_type=dt,noise_settings=ns,biome_source=bs,
      hash=hashlib.sha256(u.encode()).hexdigest()[:8],forms={f:r['forms'].get(f,0) for f in FORMS}))
out.sort(key=lambda x:x['spine'])
for i,x in enumerate(out): x['orbit']=int(x['spine'].split('.')[-1])
json.dump(out,open(O/'planets.json','w'),indent=1)
with open(O/'planets.tsv','w') as f:
    h=['planet_id','name','dimension','soil','realm','spine','opens_age','entries']+FORMS
    f.write('\t'.join(h)+'\n')
    for x in out: f.write('\t'.join(str(x.get(k,x['forms'].get(k))) for k in h)+'\n')
D=O/'datapack'; (D/'data/diaithir_planets/dimension').mkdir(parents=True,exist_ok=True)
(D/'pack.mcmeta').write_text(json.dumps({"pack":{"description":"Panscriptum planets (generated)","pack_format":94}}))
lang={}
for x in out:
    if x['planet_id']=='diaithir': continue
    d={"type":"minecraft:"+x['dimension_type'],"generator":{"type":"minecraft:noise","settings":"minecraft:"+x['noise_settings'],
       "biome_source":{"type":"minecraft:multi_noise","preset":"minecraft:"+x['biome_source']} if x['biome_source']!='end' else {"type":"minecraft:the_end"}}}
    (D/'data/diaithir_planets/dimension'/(x['planet_id']+'.json')).write_text(json.dumps(d))
    lang['dimension.diaithir_planets.'+x['planet_id']]=x['name']
(D/'assets/diaithir_planets/lang').mkdir(parents=True,exist_ok=True)
(D/'assets/diaithir_planets/lang/en_us.json').write_text(json.dumps(lang,indent=0))
print(len(out),'planets',sum(1 for x in out if x['planet_id']!='diaithir'),'dimensions')
