# S6821 Merges rule and Haiku codes into library_to_content.tsv (id, form, source)
# L2C finalize: merge rule + model codes -> library_to_content.tsv (id, form, source). Usage: finalize.py <in.jsonl> <out.tsv>
import sqlite3, json, sys, collections
sys.path.insert(0,'.')
src=open('classify.py').read()
ns={}
exec("RULES="+src.split("RULES=")[1].split("\nSYS=")[0], ns)
RULES=ns['RULES']
VALID=set("MOB BOSS NPC GOD WEAPON ARMOR TOOL FOOD RELIC MATERIAL STRUCTURE SETTLEMENT BIOME DIMENSION TECH SPELL QUEST FACTION LORE".split())
mc={}
for l in open(sys.argv[1]):
    j=json.loads(l)
    if j['code'] in VALID: mc[j['id']]=j['code']
c=sqlite3.connect('file:/mnt/project-files/codex-store/library.sqlite?mode=ro',uri=True)
cnt=collections.Counter(); out=open(sys.argv[2],'w'); out.write('id\tform\tsource\n')
for rid,k,l,pk in c.execute("select id,kind,locale,pack_id from entry"):
    if pk: f,s='PACK','pack_id'
    elif (k,l) in RULES: f,s=RULES[(k,l)],'rule'
    elif rid in mc: f,s=mc[rid],'haiku'
    else: f,s='PENDING','none'
    cnt[(f,s)]+=1; out.write(f'{rid}\t{f}\t{s}\n')
json.dump({f'{a}|{b}':n for (a,b),n in cnt.items()},open(sys.argv[2]+'.counts.json','w'),indent=1)
tot=collections.Counter()
for (f,s),n in cnt.items(): tot[f]+=n
print(tot.most_common())
