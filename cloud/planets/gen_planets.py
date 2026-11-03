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
(D/'pack.mcmeta').write_text(json.dumps({"pack":{"description":"Panscriptum planets (generated)","min_format":84,"max_format":101}}))
lang={}
POOL={'Bloom':['plains','forest','flower_forest','meadow'],'Frost':['snowy_plains','ice_spikes','snowy_taiga','frozen_peaks'],
 'Storm':['windswept_hills','jagged_peaks','stony_peaks','windswept_forest'],'Hollow':['dripstone_caves','lush_caves','deep_dark','stony_shore'],
 'Ember':['nether_wastes','crimson_forest','warped_forest','basalt_deltas'],'Iron':['desert','badlands','savanna','eroded_badlands'],
 'Quiet':['end_highlands','end_midlands','end_barrens','small_end_islands']}
TPL=O/'templates'
def tint(o,k):
    if isinstance(o,dict): return {a:tint(b,a) for a,b in o.items()}
    if isinstance(o,list): return [tint(b,k) for b in o]
    if isinstance(o,str) and re.fullmatch(r'#[0-9a-f]{6}',o) and 'color' in k:
        return '#'+''.join('%02x'%max(0,min(255,int(o[i:i+2],16)+d)) for i,d in zip((1,3,5),k_d))
    return o
B=D/'data/diaithir_planets/worldgen/biome'; T=D/'data/diaithir_planets/tags/worldgen/biome'
B.mkdir(parents=True,exist_ok=True); T.mkdir(parents=True,exist_ok=True)
CELLS=[((-1,0),(-1,0)),((-1,0),(0,1)),((0,1),(-1,0)),((0,1),(0,1))]
for x in out:
    if x['planet_id']=='diaithir': continue
    h=int(x['hash'],16); names=POOL[x['soil']]
    names=names[h%4:]+names[:h%4]
    global k_d
    k_d=((h&63)-32,((h>>6)&63)-32,((h>>12)&63)-32)
    ids=[];cells=[]
    for n,(t,hu) in zip(names,CELLS):
        j=json.loads((TPL/(n+'.json')).read_text()); bid=x['planet_id']+'_'+n
        (B/(bid+'.json')).write_text(json.dumps(tint(j,'')))
        ids.append('diaithir_planets:'+bid)
        cells.append({"biome":ids[-1],"parameters":{"temperature":list(map(float,t)),"humidity":list(map(float,hu)),"continentalness":[-1.0,1.0],"erosion":[-1.0,1.0],"depth":[-1.0,1.0],"weirdness":[-1.0,1.0],"offset":0.0}})
    (T/(x['planet_id']+'.json')).write_text(json.dumps({"values":ids}))
    d={"type":"minecraft:"+x['dimension_type'],"generator":{"type":"minecraft:noise","settings":"minecraft:"+x['noise_settings'],
       "biome_source":{"type":"minecraft:multi_noise","biomes":cells}}}
    (D/'data/diaithir_planets/dimension'/(x['planet_id']+'.json')).write_text(json.dumps(d))
    lang['dimension.diaithir_planets.'+x['planet_id']]=x['name']
(D/'assets/diaithir_planets/lang').mkdir(parents=True,exist_ok=True)
(D/'assets/diaithir_planets/lang/en_us.json').write_text(json.dumps(lang,indent=0))
print(len(out),'planets',sum(1 for x in out if x['planet_id']!='diaithir'),'dimensions')
