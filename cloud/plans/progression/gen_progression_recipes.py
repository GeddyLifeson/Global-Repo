# S0338 Writes the dormant cross-mod recipe data pack from progression/graph.json: one shapeless recipe per node with an item, tags as inputs, neoforge conditions keep it off until the item and tags exist. python3 -I gen_progression_recipes.py graph.json OUTDIR
import json,sys,os,shutil
G=json.load(open(sys.argv[1],encoding='utf-8')); out=sys.argv[2]
VAN={'wood':'#minecraft:logs','stone':'#minecraft:stone_crafting_materials','flint':'minecraft:flint','clay':'minecraft:clay_ball','sand':'#minecraft:sand'}
SKIP={'water','wild_game','wild_plants'}  # fluids and world sources are not recipe inputs
shutil.rmtree(out,ignore_errors=True); R=os.path.join(out,'data','diaithir','recipe'); T=os.path.join(out,'data','diaithir','tags','item','progression')
os.makedirs(R); os.makedirs(T)
json.dump({"pack":{"description":"Diaithir progression: dormant cross-mod recipes (generated)","min_format":[101,1],"max_format":[101,1]}},open(os.path.join(out,'pack.mcmeta'),'w'),indent=1)
tags=set(); n_rec=0; n_st=0; skipped=[]
SP=tuple(G['service_prefixes'])
def ing(r):
    if r in VAN: return VAN[r]
    if r.startswith('c:'): return '#'+r
    tags.add(r); return '#diaithir:progression/'+r
for n in G['nodes']:
    if 'item' not in n: continue
    ins=[ing(r) for r in n['needs'] if r not in SKIP and (r in VAN or not r.startswith(SP))]
    if not ins or len(ins)>9: skipped.append(n['id']); continue
    cond=[{"type":"neoforge:item_exists","item":n['item']}]
    cond+=[{"type":"neoforge:not","value":{"type":"neoforge:tag_empty","tag":i[1:]}} for i in ins if i.startswith('#diaithir:')]
    if n.get('form')=='quick' or not n.get('station'):
        pass
    else:
        st=G['stations'][n['station']]
        cond=[{"type":"neoforge:mod_loaded","modid":"diaithir_stations"}]+cond
        j={"neoforge:conditions":cond,"_node":n['id'],"_age":n['age'],"type":"diaithir:station_recipe","station":st['block'],"stage":n['form'],"ingredients":ins,"result":{"id":n['item'],"count":1},"time_s":n.get('s',{'part':10,'assembly':20,'process':5}[n['form']])}
        json.dump(j,open(os.path.join(R,'xmod_'+n['id'].replace('.','_')+'.json'),'w'),indent=1); n_rec+=1; n_st+=1; continue
    j={"neoforge:conditions":cond,"_node":n['id'],"_age":n['age'],"type":"minecraft:crafting_shapeless","category":"misc","ingredients":ins,"result":{"id":n['item'],"count":1}}
    json.dump(j,open(os.path.join(R,'xmod_'+n['id'].replace('.','_')+'.json'),'w'),indent=1); n_rec+=1
for t in sorted(tags): json.dump({"replace":False,"values":[]},open(os.path.join(T,t+'.json'),'w'))
shutil.copy(sys.argv[1],os.path.join(out,'data','diaithir','progression_graph.json'))
print(f'{n_rec} recipes ({n_st} on stations, {n_rec-n_st} grid), {len(tags)} empty tags for owners to fill; skipped (no inputs or over 9): {len(skipped)}')
