# Planet flora/ore kit pass: python3 -I kit_jobs.py JOBDIR ALL|ids ; spec_run.py JOBDIR ; merge_kit.py JOBDIR
import sqlite3,json,sys,pathlib,random,collections
R=pathlib.Path('/mnt/project-files'); job=pathlib.Path(sys.argv[1]); want=sys.argv[2:]
P=json.load(open(R/'planets/planets.json'))
BASES="oak fancy_oak birch spruce pine acacia dark_oak jungle_tree cherry".split()
LOGS="oak spruce birch jungle acacia dark_oak mangrove cherry pale_oak crimson_stem warped_stem".split()
LEAVES="oak spruce birch jungle acacia dark_oak mangrove cherry azalea flowering_azalea pale_oak".split()
UNDER="short_grass fern dead_bush bush firefly_bush brown_mushroom red_mushroom crimson_roots warped_roots nether_sprouts moss_carpet pink_petals azalea flowering_azalea cactus".split()
FLOW="dandelion poppy blue_orchid allium azure_bluet red_tulip orange_tulip white_tulip pink_tulip oxeye_daisy cornflower lily_of_the_valley torchflower wither_rose".split()
SYS=f"""You choose the plants and ores of one fictional planet for a Minecraft-style game from the planet's REAL entries only (id | name | text). Make planets differ and use the whole range of options (tree shapes, wood and leaf types, density, ores). crimson_stem/warped_stem only if the entries clearly mention fungus, spores, blood, nether, crimson or warped; pale_oak only for ghostly, bone-white or pale themes; otherwise pick woods and leaves by the climate and materials the entries describe (spruce/pine for cold, acacia/jungle for hot, cherry/azalea for blossoms, birch/oak for mild, mangrove for swamp). Use density above 1.2 for forested or jungle worlds and below 0.5 for deserts, ice and barrens. Make planets differ: read what the entries describe (forests, glass, bone, coral, rust, fungus, blossoms, ash, ice, metal, crystal...) and pick matching options; do not default to oak. If the entries say little about plants, choose a modest kit and set "grounded" to false.
Reply with JSON only:
{{"trees":[{{"base":"<{'|'.join(BASES)}>","log":"<{'|'.join(LOGS)}>","leaves":"<{'|'.join(LEAVES)}>","weight":1-3}}] (1 to 3 trees),
"density":0.2-2.0 (how wooded the planet is),
"undergrowth":[{{"block":"<{'|'.join(UNDER)}>","weight":1-5}}] (1 to 3),
"flowers":["<{'|'.join(FLOW)}>"] (0 to 4),
"ores":{{"coal":0-3,"iron":0-3,"copper":0-3,"gold":0-3,"redstone":0-3,"lapis":0-3,"diamond":0-3}} (1.0 = like Earth, 0 = none, 3 = very rich; make it reflect the entries: metal worlds rich in iron/copper, crystal worlds rich in diamond/lapis, barren worlds poor),
"why_entry":"<entry id from the input that best supports this kit>","grounded":true|false}}"""
c=sqlite3.connect(f'file:{R}/library-content/content.sqlite?mode=ro',uri=True)
s=sqlite3.connect('file:/mnt/attach/project-files/codex-store/library.sqlite?mode=ro',uri=True)
by=collections.defaultdict(list)
for i,u in c.execute("select id,universe from content where form in ('BIOME','DIMENSION','MATERIAL','TOOL','FOOD','LORE','STRUCTURE')"): by[u].append(i)
rows=[]
for p in P:
    if p['planet_id']=='diaithir' or (want and want!=['ALL'] and p['planet_id'] not in want): continue
    ids=sorted(by[p['name']]); random.Random('kit'+p['planet_id']).shuffle(ids); ids=ids[:80]
    ents=[s.execute("select id,name,substr(summary,1,200) from entry where id=?",(i,)).fetchone() for i in ids]
    rows.append({"id":p['planet_id'],"system":SYS,"prompt":f"Planet: {p['name']} (soil {p['soil']})\nEntries:\n"+"\n".join(f"{i} | {n} | {m}" for i,n,m in ents if i)})
job.mkdir(parents=True,exist_ok=True)
with open(job/'in.jsonl','w') as f:
    for r in rows: f.write(json.dumps(r)+'\n')
open(job/'README.md','w').write("max_tokens 2500\nmodel: haiku\nCheck: valid JSON from menus. Owner: planets thread.\n")
print(len(rows),'rows')
