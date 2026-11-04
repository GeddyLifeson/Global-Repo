# S6945 report.py: build plans/ITEM_ROLES.md from uses.json (scan_uses.py) and ITEM_ROLES.csv. python3 -I report.py <uses.json> <roles.csv> <out.md>
import sys,json,csv,collections
u=json.load(open(sys.argv[1]));R=list(csv.DictReader(open(sys.argv[2])))
st={'recipe','quest','codex','loot','cuisine'}
strong=sum(1 for c in u.values() if set(c)&st);zero=[i for i,c in u.items() if not c]
cls=collections.Counter(r['role_class'] for r in R)
lk=collections.Counter(l for r in R for l in r['links'].split('|') if l)
dec=[r for r in R if r['decor_only']=='True']
nsd=collections.defaultdict(lambda:[0,0])
for r in R:
    n=r['id'].split(':')[0];nsd[n][0]+=1;nsd[n][1]+=r['decor_only']=='True'
missing=[i for i in u if i not in {r['id'] for r in R} and not set(u[i])&st]
tot=len(R) or 1
o=[f"# Item roles (Marlon rule 11-03: every item has a real role)\n",
f"Registry list: {len(u)} priced item ids in DiaithirRPG `claude/pack-v1-3` (`economy/kubejs/data/diaithir/prices.json`; no server dump exists in the repo, so this is the closest full list). Pack-layer use scan: `tools/item_roles/scan_uses.py`.\n",
f"- Strong pack-layer use (recipe, quest, Codex, loot or cuisine file mentions it): {strong}\n- Needed a role: {len(u)-strong}; roles assigned so far: {len(R)}; still unassigned: {len(missing)}\n- Zero mentions anywhere in the pack layer (true orphans): {len(zero)}\n- Caveat: mod-internal recipes live in the jars and are not scanned, so 'no use' means no hookup in OUR layer (Age station, vendor, quest, Codex).\n",
"## Rules applied\nRole may be an Age use, a material with real properties (density, strength) for vehicles/ships/rails/structures, or anything useful Minecraft never gave it. Genuinely decorative items stay `decor`. Every role lists 2-5 cross-system links.\n",
"## Role classes\n|class|items|\n|---|---|\n"]+[f"|{k}|{v}|\n" for k,v in cls.most_common()]
o.append("\n## Cross-system link counts (low = under-integrated system)\n|system|items linked|share|\n|---|---|---|\n")
o+= [f"|{k}|{v}|{100*v/tot:.1f}%|\n" for k,v in lk.most_common()]
iso=[s for s in 'economy vehicles ships rail storage rites codex quests progression building machines food spoilage autonomy circuit munitions npc_wages energy'.split() if lk[s]<0.02*tot]
o.append(f"\n## Isolated or thin systems (under 2% of items linked): {', '.join(iso) or 'none'}\nThese need a pass: either real parts are missing (vehicle/ship/rail part items, munitions, circuit) or roles should route items into them.\n")
o.append(f"\n## Decor-only: {len(dec)} items ({100*len(dec)/tot:.1f}%), kept decorative. Highest-decor namespaces:\n|namespace|items|decor|\n|---|---|---|\n")
o+= [f"|{n}|{a}|{b}|\n" for n,(a,b) in sorted(nsd.items(),key=lambda x:-x[1][1])[:25]]
o.append("\n## Files\n`plans/ITEM_ROLES.csv` (id, role_class, role, where, props, links, decor_only), `plans/ITEM_ROLES_ORPHANS.txt` (zero-mention ids).\n")
open(sys.argv[3],'w').write(''.join(o))
open(sys.argv[3].replace('.md','_ORPHANS.txt'),'w').write('\n'.join(sorted(zero))+'\n')
