# S6990 assign_ages_folded.py: Age for the 312 ids of folded DiaithirRPG modules that assign_ages.py left without one. Per item, by material/tier/function. python3 -I assign_ages_folded.py NOAGE_IDS.txt data/ages
import csv,json,re,sys
ids=[l.strip() for l in open(sys.argv[1]) if l.strip()];OUT=sys.argv[2]
have={r['item'] for r in csv.DictReader(open(f'{OUT}/NOAGE_ASSIGNED.csv'))}
ns_def=set(json.load(open(f'{OUT}/NAMESPACE_DEFAULTS.json'))['namespaces'])
def rule(i):
    ns,p=i.split(':',1)
    if ns=='diaithir_classes':
        return 'VI' if 'composite' in p else 'V' if 'steel' in p else 'II' if 'bronze' in p else 'III','classes: tier by material (bronze II, steel V, composite VI), rest III'
    if ns=='diaithirrelics': return 'III','Celtic relic'
    if ns=='diaithirrouting': return ('IV','hopper') if 'hopper' in p else ('VI','router/module/filter (tech-by-age: Mekanism/IF era)')
    if ns=='diaithirpipes': return {'basic':'IV','improved':'V','advanced':'VI'}.get(p.rsplit('_',1)[-1],'IV'),'pipe tier'
    if ns=='diaithirportable':
        t=re.match(r'(wood|iron|gold|diamond|netherite)_',p)
        if t: return {'wood':'II','iron':'III','gold':'III','diamond':'V','netherite':'VI'}[t[1]],'container tier'
        return ('VII','deep null') if 'deep_null' in p else ('IV' if re.search('magnet|void',p) else 'III'),'portable upgrade'
    if ns=='diaithir_end': return 'VII','End material'
    if ns=='diaithir_overworld_biomes': return 'I','overworld biome item'
    if 'netherite' in p: return 'VI','jewelry netherite tier'
    if p.startswith('jewelry_'): return ('III' if re.search('copper|iron|gold|gem_vein|jade|citrine',p) else 'IV'),'jewelry by metal/gem (III copper-gold, IV gems and uniques)'
    if re.search(r'^(ruby|sapphire|topaz)',p): return 'IV','gem'
    if p.startswith('easy_villagers'): return 'VI','villager automation'
    if re.search('magnet|demagnetization|fluid_hopper|redstone_clock|tps_meter',p): return 'V','electric/automation utility'
    if p.startswith('crafting_on_a_stick'): return 'III','portable station'
    if re.search('spawn_egg',p): return 'I','spawn egg'
    if p.startswith('utilitarian_') or p in('pocket_bench','utility_lamp','wayfinder_compass','sky_sand','angel_block'): return ('II' if re.search('carpet|banner|grrass|drit|snad|lamp|tiny|trowel|bucket|muffler|raider|dropper|tag|order',p) else 'IV'),'utility block, early'
    return None,None
rows=[];nr=[]
for i in sorted(ids):
    if i in have or i.split(':')[0] in ns_def: continue
    a,w=rule(i)
    (rows if a else nr).append((i,a,w) if a else i)
print(len(rows),'assigned;',len(nr),'unresolved',nr[:10])
with open(f'{OUT}/FOLDED_ASSIGNED.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['item','age','why']);w.writerows(rows)
