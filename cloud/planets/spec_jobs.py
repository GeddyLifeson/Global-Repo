# S6831-pending planet spec job builder. python3 -I spec_jobs.py JOBDIR planet_id [planet_id...]  (or ALL)
# Builds in.jsonl for the compute watcher: one row per planet, real entry text only.
import sqlite3,json,sys,pathlib,random
R=pathlib.Path('/mnt/project-files'); job=pathlib.Path(sys.argv[1]); want=sys.argv[2:]
P=json.load(open(R/'planets/planets.json'))
ARCH="plains forest flower_forest meadow sunflower_plains birch_forest dark_forest taiga old_growth_pine_taiga snowy_plains ice_spikes snowy_taiga snowy_slopes grove frozen_peaks jagged_peaks stony_peaks windswept_hills windswept_forest windswept_savanna savanna desert badlands eroded_badlands wooded_badlands jungle sparse_jungle swamp mangrove_swamp cherry_grove mushroom_fields".split()
OC="ocean deep_ocean frozen_ocean deep_frozen_ocean warm_ocean lukewarm_ocean beach snowy_beach river frozen_river".split()
SYS=f"""You design the surface of one fictional planet for a Minecraft-style game, using ONLY the supplied planet entries (real text). Never invent places that the entries do not support; if the entries are thin, use fewer biomes. Reply with JSON only, no prose.
Schema: {{"sky":{{"sky":"#rrggbb","fog":"#rrggbb","cloud":"#aarrggbb","cloud_height":number 120-260}},
"weather":{{"kind":"rain|snow|none|ash","frequency":"rare|normal|frequent"}},
"sea":{{"liquid":"water|lava|none","water":"#rrggbb"}},
"terrain":"normal|amplified|large_biomes",
"biomes":[{{"entry":"<entry id from input>","archetype":"<one of {' '.join(ARCH)}>","temp":-1..1,"humid":-1..1,"grass":"#rrggbb","foliage":"#rrggbb","water":"#rrggbb","precip":"none|rain|snow"}}] (5 to 10 entries),
"ocean_archetype":"<one of {' '.join(OC[:6])}>","beach_archetype":"beach|snowy_beach","river_archetype":"river|frozen_river","notes":"one sentence"}}
temp -1 cold to 1 hot, humid -1 dry to 1 wet; spread the biomes across the range so they tile. Colours reflect the entry text (mood, light, element)."""
c=sqlite3.connect(f'file:{R}/library-content/content.sqlite?mode=ro',uri=True)
s=sqlite3.connect(f'file:/mnt/attach/project-files/codex-store/library.sqlite?mode=ro',uri=True)
rows=[]
for p in P:
    if p['planet_id']=='diaithir' or (want and want!=['ALL'] and p['planet_id'] not in want): continue
    ids=[r[0] for r in c.execute("select id from content where universe=? and form in ('BIOME','DIMENSION','SETTLEMENT','STRUCTURE')",(p['name'],))]
    random.Random(p['planet_id']).shuffle(ids); ids=ids[:70]
    ents=[s.execute("select id,name,substr(summary,1,220) from entry where id=?",(i,)).fetchone() for i in ids]
    txt="\n".join(f"{i} | {n} | {m}" for i,n,m in ents if i)
    rows.append({"id":p['planet_id'],"system":SYS,"prompt":f"Planet: {p['name']} (soil {p['soil']}, realm {p['realm']})\nEntries (id | name | text):\n{txt}"})
job.mkdir(parents=True,exist_ok=True)
with open(job/'in.jsonl','w') as f:
    for r in rows: f.write(json.dumps(r)+'\n')
open(job/'README.md','w').write("max_tokens 2500\nmodel: haiku\nCheck: valid JSON matching the schema; every biome.entry is an id from the input; archetype in list. Owner: planets thread.\n")
print(len(rows),'rows')
