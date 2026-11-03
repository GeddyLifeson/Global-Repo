# S6820 Library entries to content form: Haiku classifier (direct parallel calls, cached prompt), resumable
# L2C classify: Library entries -> in-game content form. Usage: classify.py <out.jsonl> [limit] [offset]
import sqlite3, json, os, sys, urllib.request, threading, time, concurrent.futures as cf, random
DB='file:/mnt/project-files/codex-store/library.sqlite?mode=ro'
OUT=sys.argv[1]; LIMIT=int(sys.argv[2]) if len(sys.argv)>2 else 0; OFF=int(sys.argv[3]) if len(sys.argv)>3 else 0
KEY=open('/mnt/project-files/compute/secrets/anthropic_key').read().strip()
MODEL='claude-haiku-5-5'; BATCH=40; WORKERS=32
RULES={('being','persons'):'NPC',('being','gods'):'GOD',('being','gods-future'):'GOD',('being','gods-rodos'):'GOD',
('being','fauna'):'MOB',('being','fossils'):'MOB',('being','creatures'):'MOB',('being','creatures-future'):'MOB',('being','creatures-rodos'):'MOB',('being','bestiary'):'MOB',
('item','weapons'):'WEAPON',('item','arms'):'WEAPON',('item','relics'):'RELIC',('item','clothing'):'ARMOR',('item','dishes'):'FOOD',('item','dishes-future'):'FOOD',('item','dishes-rodos'):'FOOD',('item','drinks'):'FOOD',
('concept','powers'):'SPELL',('concept','techs'):'TECH',('concept','civics'):'TECH',('concept','magic'):'SPELL',
('event','quests'):'QUEST',('faction','factions'):'FACTION',('faction','peoples'):'FACTION',('faction','cultures'):'FACTION',('faction','mythology'):'FACTION',('faction','mythology-future'):'FACTION',('faction','mythology-rodos'):'FACTION'}
SYS="""You sort Library entries (fictional-world lore, original retellings) by the in-game content each could become in a Minecraft-style game. Pick exactly ONE code per entry from what the text itself describes. Never invent; if the text only gives history, pick LORE.
Codes:
MOB = a creature, animal, monster, spirit or beast that could be a spawnable entity
BOSS = a named, singular, mighty foe, tyrant, dragon, archmage or champion fought as a boss
NPC = an ordinary or notable person (trader, scholar, guard, hero, ruler) who could stand in a village or give a quest
GOD = a deity, saint or worshipped power, fit for a shrine
WEAPON = weapon or combat tool (blade, bow, staff used to fight)
ARMOR = armor, clothing, wearable gear
TOOL = non-combat tool, device, machine, vehicle, instrument, gadget
FOOD = dish, drink, consumable meal or potion
RELIC = magical or legendary artifact, charm, gem, rune, unique treasure
MATERIAL = a raw substance, ore, metal, plant, resource, ingredient
STRUCTURE = a building, ruin, fortress, temple, dungeon, tower or site that could be a generated structure
SETTLEMENT = a city, town, village, camp or realm center
BIOME = a landscape, region type, forest, sea, waste, climate zone
DIMENSION = a whole plane, world, realm or pocket-world reached by travel
TECH = a technology, craft method, science, civic institution or doctrine that could be a tech-tree node
SPELL = a magical art, power, ability, rite or school
QUEST = a task, journey, mission, contest or quest-like event with an objective
FACTION = an order, guild, tribe, people, house, company or army (reputation faction)
LORE = pure history, concept, event or idea with no buildable form; page only
Input lines: idx|universe|source-kind/section|name|text. Output ONLY lines idx|CODE, one per input line, nothing else.
Examples:
7|Lumera|being/assay|Orryk the Gaunt|A towering plague-lord whose breath withers fields and who leads the ash legions.  -> 7|BOSS
8|Lumera|item/assay|Dawnfire Lance|A long spear tipped with sunlit crystal, carried by the vanguard.  -> 8|WEAPON
9|Lumera|place/assay|Ashen Reach|A wind-scoured plain of grey dust where little grows.  -> 9|BIOME
10|Lumera|event/assay|The Third Sundering|A war in which the northern kingdoms broke the old league.  -> 10|LORE
11|Lumera|concept/assay|Wheelcraft|The art of turning grain into flour with water-driven stones, taught in the river towns.  -> 11|TECH
12|Lumera|being/assay|Marsh Gar|A pike-headed wader that hunts in the reeds.  -> 12|MOB"""
def conn(): return sqlite3.connect(DB,uri=True)
def post(body,tries=6):
    for a in range(tries):
        try:
            r=urllib.request.Request('https://api.anthropic.com/v1/messages',json.dumps(body).encode(),{'x-api-key':KEY,'anthropic-version':'2023-06-01','content-type':'application/json'})
            return json.load(urllib.request.urlopen(r,timeout=90))
        except Exception as e:
            time.sleep(min(60,2**a+random.random()))
            err=e
    raise err
lock=threading.Lock()
def work(rows,fout):
    lines=[f"{i}|{u}|{k}/{l}|{n}|{(s or '')[:230]}" for i,(rid,u,k,l,n,s) in enumerate(rows)]
    d=post({'model':MODEL,'max_tokens':400,'thinking':{'type':'disabled'},'system':[{'type':'text','text':SYS,'cache_control':{'type':'ephemeral','ttl':'1h'}}],'messages':[{'role':'user','content':'\n'.join(lines)}]})
    got={}
    for ln in ''.join(b.get('text','') for b in d['content']).splitlines():
        if '|' in ln:
            a,b=ln.split('|',1)
            if a.strip().isdigit(): got[int(a)]=b.strip()
    u=d['usage']
    with lock:
        for i,r in enumerate(rows): fout.write(json.dumps({'id':r[0],'code':got.get(i)})+'\n')
        fout.flush()
        open('/mnt/project-files/compute/ledger.csv','a').write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},library-to-content,{MODEL},{u['input_tokens']},{u['output_tokens']},{u.get('cache_creation_input_tokens',0)},{u.get('cache_read_input_tokens',0)}\n")
if __name__=='__main__':
    done=set()
    if os.path.exists(OUT):
        for l in open(OUT):
            j=json.loads(l)
            if j['code']: done.add(j['id'])
    c=conn(); todo=[]
    for rid,u,k,l,n,s in c.execute("select id,universe,kind,locale,name,summary from entry where pack_id is null order by n"):
        if (k,l) in RULES or rid in done: continue
        todo.append((rid,u,k,l,n,s))
    todo=todo[OFF:]
    if LIMIT: todo=todo[:LIMIT]
    print('to classify',len(todo),flush=True)
    chunks=[todo[i:i+BATCH] for i in range(0,len(todo),BATCH)]
    with open(OUT,'a') as f, cf.ThreadPoolExecutor(WORKERS) as ex:
        futs=[ex.submit(work,ch,f) for ch in chunks]
        for n,fu in enumerate(cf.as_completed(futs)):
            try: fu.result()
            except Exception as e: print('ERR',e,flush=True)
            if n%200==0: print(n,len(chunks),flush=True)
