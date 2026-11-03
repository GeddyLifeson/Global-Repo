# Planet atmosphere pass (weather, particles, fog, night): python3 -I atmo_jobs.py JOBDIR ALL|ids   then spec_run.py JOBDIR, then merge_atmo.py JOBDIR
import sqlite3,json,sys,pathlib,random,collections
R=pathlib.Path('/mnt/project-files'); job=pathlib.Path(sys.argv[1]); want=sys.argv[2:]
P=json.load(open(R/'planets/planets.json'))
PART="ash white_ash snowflake spore_blossom_air crimson_spore warped_spore cherry_leaves pale_oak_leaves end_rod soul glow firefly sculk_soul none".split()
SYS=f"""You choose the weather and air of one fictional planet for a Minecraft-style game, from the planet's REAL entries only (given as id | name | text). Different planets must feel different: read what the entries actually describe (fire, ash, snow, spores, mist, storms, lights, spirits, machinery smoke, petals, glass dust ...) and do not default to ash. If the entries say nothing about air or weather, choose a mild option and set "grounded" to false. "precip_bias" must be "mixed" unless the entries clearly describe a rainless, airless or desert-wide place (then "dry") or a clearly wet or frozen one (then "rain" or "snow"); never choose "dry" just because the place is dark, magical or ruined. Pick "storms":"stormy" when the entries describe storms, lightning, tempests, war-torn skies or similar.
Reply with JSON only:
{{"particles":[{{"type":"<one of {' '.join(PART)}>","probability":0.004-0.12}}] (0 to 3 items; 'none' alone means clear air),
"fog":"#rrggbb","fog_density":"thin|normal|thick","night":"normal|bright|dark","stars":0.0-1.0,
"precip_bias":"rain|snow|dry|mixed","storms":"calm|stormy","why_entry":"<one entry id from the input that most supports this choice>","why":"<8 words>","grounded":true|false}}"""
c=sqlite3.connect(f'file:{R}/library-content/content.sqlite?mode=ro',uri=True)
s=sqlite3.connect('file:/mnt/attach/project-files/codex-store/library.sqlite?mode=ro',uri=True)
by=collections.defaultdict(list)
for i,u in c.execute("select id,universe from content where form in ('BIOME','DIMENSION','STRUCTURE','SETTLEMENT','LORE','POWER','SPELL')"): by[u].append(i)
rows=[]
for p in P:
    if p['planet_id']=='diaithir' or (want and want!=['ALL'] and p['planet_id'] not in want): continue
    ids=sorted(by[p['name']]); random.Random('atmo'+p['planet_id']).shuffle(ids); ids=ids[:80]
    ents=[s.execute("select id,name,substr(summary,1,200) from entry where id=?",(i,)).fetchone() for i in ids]
    rows.append({"id":p['planet_id'],"system":SYS,"prompt":f"Planet: {p['name']} (soil {p['soil']})\nEntries:\n"+"\n".join(f"{i} | {n} | {m}" for i,n,m in ents if i)})
job.mkdir(parents=True,exist_ok=True)
with open(job/'in.jsonl','w') as f:
    for r in rows: f.write(json.dumps(r)+'\n')
open(job/'README.md','w').write("max_tokens 2500\nmodel: haiku\nCheck: valid JSON; why_entry is an input id. Owner: planets thread.\n")
print(len(rows),'rows')
