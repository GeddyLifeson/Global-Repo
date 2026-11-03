# S6916 age_balance.py: builds the per-Age coverage matrix (plans/AGE_BALANCE_MATRIX.csv) from graph.json, tech_ages_by_item and era-index feeds.
import csv,json,glob,os,statistics,sys,collections
P=sys.argv[1] if len(sys.argv)>1 else '/mnt/project-files'
OUT=sys.argv[2] if len(sys.argv)>2 else 'plans/AGE_BALANCE_MATRIX.csv'
AGES=['I','II','III','IV','V','VI','VII','VIII','RODOS']
def norm(a): a=str(a).upper(); return {'FUTURE':'VIII','1':'I','2':'II','3':'III','4':'IV','5':'V','6':'VI','7':'VII','8':'VIII','9':'RODOS'}.get(a,a)
G={'decor':'chisel mcw bibliocraft refurbished_furniture framedblocks domum_ornamentum stoneworks luminax casinodeco structurize regions_unexplored biomesoplenty productivetrees minecraft ecologics auroral strainers utilitarian diaithirbridges',
 'machines':'create modern_industrialization mekanism enderio oritech energizedpower pneumaticcraft railcraft powah industrialforegoing rftools projectred morered classicpipes pipez quarryplus computercraft sfm laserio integrated modularrouters fluxnetworks routers stepcrafter elevatorid titanium',
 'storage':'refinedstorage ae2 megacells extendedae advanced_ae extradisks sophisticated functionalstorage ironchest cabletiers refinedtypes universalgrid dimstorage logisticsnetworks deepnull',
 'magic':'occultism theurgy neovitae forbidden_arcanus evilcraft reliquary rootsclassic apotheosis apothic wizards runes spell_engine mysticalagradditions',
 'gear':'tconstruct silentgear silentgems paladins rogues archers jewelry irons_jewelry musketmod pointblank jousting artifacts sgearmetalworks productivemetalworks equivox sceptersteel mininggadgets buildinggadgets constructionstick justdirethings',
 'farm_food':'croptopia farmersdelight cookingforblockheads forestry productivebees productivefarming mysticalagriculture agritechevolved aquaculture farmingforblockheads matc',
 'fauna_dims':'untamedwilds iceandfire vampirism aether_ii twilightforest geore hostilenetworks bhc',
 'econ_social':'lightmanscurrency roulettecasino mca minecolonies millager easy_npc easy_villagers blockhuttownhall'}
def grp(ns):
    for g,v in G.items():
        if any(ns.startswith(p) for p in v.split()): return g
    return 'other'
rows=collections.OrderedDict()
def put(k,vals): rows[k]={a:vals.get(a,0) for a in AGES}
g=json.load(open(f'{P}/plans/progression/graph.json'))
c=collections.defaultdict(collections.Counter)
for n in g['nodes']: c[n['system']][norm(n['age'])]+=1; c['ALL'][norm(n['age'])]+=1
for s in sorted(c): put('nodes:'+s,c[s])
it=collections.defaultdict(collections.Counter)
for r in csv.DictReader(open(f'{P}/era-index/tech_ages_by_item_unmerged.csv')):
    a=norm(r['age'])
    if a in AGES: it[grp(r['item'].split(':')[0])][a]+=1
for k in sorted(it): put('items:'+k,it[k])
for f in sorted(glob.glob(f'{P}/era-index/feeds/*.json')):
    d=json.load(open(f)); be=d.get('by_era')
    if be and 'quests' not in str(be)[:20]: put('feed:'+d['system'],{norm(k):v for k,v in be.items() if isinstance(v,int)})
for p in ('corpus_library',):
    put('corpus:library',{norm(k):v for k,v in json.load(open(f'{P}/era-index/corpus.json'))[p].items()})
with open(OUT,'w',newline='') as f:
    w=csv.writer(f); w.writerow(['row']+AGES+['median_I_VII'])
    for k,v in rows.items(): w.writerow([k]+[v[a] for a in AGES]+[statistics.median(v[a] for a in AGES[:7])])
print(len(rows),'rows ->',OUT)
