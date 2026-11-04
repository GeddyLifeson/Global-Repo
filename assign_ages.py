# S6957 assign_ages.py: gives every item with no Age one (V1 audit hole, 12.7%). Writes data/ages/NOAGE_ASSIGNED.csv and NAMESPACE_DEFAULTS.json. python3 -I assign_ages.py [PROJECT_FILES] [OUT_DIR]
import csv,json,re,sys,os,collections
P=sys.argv[1] if len(sys.argv)>1 else '/mnt/project-files'
OUT=sys.argv[2] if len(sys.argv)>2 else 'data/ages'
ORD=['I','II','III','IV','V','VI','VII','VIII','RODOS']
mx=lambda a,b:max(a,b,key=ORD.index)
res=json.load(open(f'{P}/audit/tech_age_resolved_per_item.json'))
tbl={r['item']:r['age'] for r in csv.DictReader(open(f'{P}/era-index/tech_ages_by_item_unmerged.csv'))}
ta=json.load(open(f'{P}/era-index/tech_ages_unmerged.json')); NS=ta['namespaces']
# Materials follow plans/progression/graph.json: copper/tin I-II, bronze II, iron/silver/gold/lead III, steel V, modern metals VI.
MAT=[('II','copper tin bronze coal charcoal'),('III','iron silver gold lead zinc brass electrum pearl nickel'),
 ('V','steel aluminium aluminum invar constantan'),('VI','osmium uranium platinum titanium tungsten cobalt antimony lithium iridium refined_obsidian refined_glowstone netherite')]
def mat(s):
    for a,w in MAT:
        if any(x in s for x in w.split()): return a
    return None
NETHER='blaze piglin wither ghast magma hoglin strider zoglin nether'.split(); END='enderman endermite shulker ender_dragon dragon'.split()
def egg(p):
    m=p.replace('_spawn_egg','')
    return 'VII' if any(x in m for x in END) else 'V' if any(x in m for x in NETHER) else 'I'
def rule(i):
    ns,p=i.split(':',1)
    if ns=='jaopca':
        form,_,m=p.partition('.'); a=mat(m) or 'VI'
        if form.startswith('oritech'): a=mx(a,'VI')
        elif form.startswith(('neovitae','theurgy')): a=mx(a,'IV')
        return a,'jaopca form.material'
    if ns=='alltheores':
        a=mat(p) or 'VI'
        return (mx(a,'V') if re.search('dirty_dust|clump|shard|crystal',p) else a),'alltheores material, ore-chain forms V+'
    if ns=='mts': return ('VII' if p.startswith('pwic_') else 'VI'),'mts: modern military vehicles VII, vehicle parts VI'
    if ns=='minecraft' and p.endswith('_spawn_egg'): return egg(p),'spawn egg by mob home (nether V, end VII)'
    if p.endswith('_spawn_egg'): return egg(p),'spawn egg by mob home (nether V, end VII)'
    if ns=='diaithir_planets': return 'VIII','planet content opens with the space hull (ship.hull_space)'
    if ns=='diaithirtrees': return 'I','trees and wood are Age I'
    if ns=='jdturrets': return 'VI','defence.turret is Age VI'
    if ns=='modulargolems': return 'IV','golem workshop, machine age IV'
    if ns=='mutantmonsters': return 'V','mutant mobs and drops'
    if ns=='deepworlds': return 'VII','blueprint and charter items, settlement city/foundry tier'
    if ns in('vs_eureka','valkyrienskies'): return 'III','ship helm and assembler (ship.helm, Age III)'
    if ns=='betterarcheology': return 'III','archaeology digs, fossils start Age III'
    if ns=='untamedwilds': return 'I','wild species spawn from Age I'
    if ns=='diaithir': return 'III','own misc items, mid Age'
    if ns in NS: return NS[ns],'namespace default'
    if ns=='factionapi': return 'III','vampirism faction items (vampirism is Age III)'
    if ns=='neoorigins': return 'I','origin choice at start'
    if mat(p): return mat(p),'tool/item material'
    return 'I','fallback: Age I (no rule matched)'
SRC=collections.Counter(); rows=[]; unk=[]
for i,v in sorted(res.items()):
    if v is not None or i=='minecraft:air': continue
    if i in tbl: a,w=tbl[i],'tech_ages_by_item (classify.py)'
    else:
        r=rule(i)
        if not r: unk.append(i); continue
        a,w=r
    if a not in ORD: unk.append(i); continue
    rows.append((i,a,w)); SRC[w.split(' (')[0]]+=1
os.makedirs(OUT,exist_ok=True)
with open(f'{OUT}/NOAGE_ASSIGNED.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['item','age','why']); w.writerows(rows)
# defaults so items not in the snapshot (new or renamed ids) still get an Age
D={'diaithirtrees':'I','diaithir_planets':'VIII','diaithir':'III','jaopca':'VI','alltheores':'VI','mts':'VI','jdturrets':'VI','modulargolems':'IV','mutantmonsters':'V','deepworlds':'VII','vs_eureka':'III','valkyrienskies':'III','betterarcheology':'III','untamedwilds':'I',
 'minecraft':'I','regions_unexplored':'I','biomesoplenty':'I','lightmanscurrency':'I'}
# Namespaces the V1 audit found with no default (theme to Age follows plans/progression/graph.json).
D.update({'ae2wtlib':'VII','appflux':'VII','merequester':'VII','diaithirlinkedstorage':'VII','simpleteleporters':'VII','diaithirbosses':'VII',
 'archimedes':'IV','theaurorian':'IV','toms_storage':'IV','diaithircompass':'IV','diaithirwaypoints':'IV','diaithirfirearms':'IV','nutritionalbalance':'IV','yo_hooks':'IV',
 'diaithirarms':'V','diaithirbuildcraft':'V','diaithirbuildcraft2':'V','immersive_machinery':'V','netherchested':'V',
 'copperhopper':'VI','hoppergadgetry':'VI','tinypipes':'VI','diaithircomputing':'VI','diaithircropgenes':'VI','diaithirfilters':'VI','hangglider':'VI','quarry':'VI',
 'diaithirfoundry':'III','extendedcrafting':'III','diaithirupgrades':'III','echochest':'III','horseman':'III','horsepowered':'III','justhammers':'III','linkedchests':'III',
 'colossalchests':'II','diaithircarts':'II','diaithirfarmkitchen':'II','diaithirfurniture':'II','storagedrawers':'II',
 'diaithirclaims':'I','diaithircreatureutils':'I','effortlessbuilding':'I','homeostatic':'I','immersive_melodies':'I','moblassos':'I','natures_spirit':'I','solonion':'I'})
for n in ta['nontech']: D.setdefault(n,'I')
json.dump({'_doc':'Namespace default Age for namespaces that had none (nontech list, new modules). Item rows in NOAGE_ASSIGNED.csv override. Merge into content/tech_ages.json namespaces; nontech list then empties.','namespaces':dict(sorted(D.items()))},open(f'{OUT}/NAMESPACE_DEFAULTS.json','w'),indent=1)
print(len(rows),'assigned,',len(unk),'unassigned',unk[:10]); print(SRC.most_common())
print(collections.Counter(a for _,a,_ in rows))

# Optional merge: python3 -I assign_ages.py PROJECT_FILES OUT_DIR TECH_AGES.json AUDIT_NOAGE_IDS.txt
if len(sys.argv)>4:
    tf=sys.argv[3]; T=json.load(open(tf,encoding='utf-8'))
    audit=[l.strip() for l in open(sys.argv[4]) if l.strip()]
    use={i.split(':')[0] for i in audit}|{r[0].split(':')[0] for r in rows}
    for ns,a in D.items():
        if ns in use and ns not in T['namespaces']: T['namespaces'][ns]=a
        if ns in T['namespaces'] and ns in T['nontech']: T['nontech'].remove(ns)
    for i,a,w in rows:
        if i in T['items'] or i in T['decided']: continue
        if a==T['namespaces'].get(i.split(':')[0]): continue
        (T['items'] if w.startswith('tech_ages_by_item') else T['decided'])[i]=a
    T['nontech']=[n for n in T['nontech'] if n not in T['namespaces']]  # a namespace with an Age is not non-tech (test_tech_ages)
    open(tf,'w',encoding='utf-8').write(json.dumps(T,indent=2,ensure_ascii=False))
    print('merged into',tf,len(T['namespaces']),'namespaces',len(T['items']),'items',len(T['decided']),'decided',len(T['nontech']),'nontech')
