# S6991 orphan_roles.py: classify the strict orphans (no recipe, loot, trade, tag or server-script use) and write plans/ITEM_ROLES_ORPHANS.csv. python3 -I orphan_roles.py orphans.txt roles.csv out.csv
import sys,re,csv,collections
ids=[l for l in open(sys.argv[1]).read().split('\n') if l]
have={r['id'] for r in csv.DictReader(open(sys.argv[2]))}
EGG=re.compile(r'spawn_egg|_egg$|^spawn_|dragonegg')
def cls(i):
    ns,p=i.split(':',1)
    if ns=='diaithirbosses':
        if p.endswith('_trophy'): return 'boss_trophy','Trophy dropped by its boss; mounts in the trophy hall and counts for the boss ledger','loot: boss entity loot table (missing)'
        if p.endswith('spawn_egg'): return 'spawn_egg','Admin and test summon for the boss; players summon through the altar and rite','admin only'
        return 'boss_system','Boss rite part: altar, catalyst, core, token or gate used to call and reward a boss','recipe/loot: rite station (missing)'
    if EGG.search(p): return 'spawn_egg','Spawn egg: creative and test item; players meet the creature in the world','admin only'
    if re.search(r'preview|debug|villager_tracker|^torch_\d|_item$',p) and not re.search('berry|mushroom',p): return 'technical','Technical or placement-preview item, not for players; hide from creative tab and recipe viewer','hide'
    if re.search(r'bush|sapling|leaves|roots|grass|fern|vine|mushroom|coral|flower|plant|crop|berry|shroom|moss|reed|kelp',p): return 'worldgen_plant','Wild plant or foliage placed by world generation; harvested in the field, drops come from the block loot table','block drop (Java or loot; needs LOG)'
    if re.search(r'bucket|bottle',p): return 'creature_container','Container for catching a creature; filled in the field','Java drop (needs LOG)'
    return 'other','Content item with no recipe, loot or trade; needs a source assigned by its Age lane','source missing'
rows=[];c=collections.Counter()
for i in sorted(ids):
    k,r,s=cls(i); c[(k)]+=1
    rows.append([i,k,r,s,'already_in_ITEM_ROLES' if i in have else 'new'])
with open(sys.argv[3],'w',newline='') as f:
    w=csv.writer(f);w.writerow(['id','orphan_class','role','source_status','roles_csv']);w.writerows(rows)
print(len(rows),dict(c))
