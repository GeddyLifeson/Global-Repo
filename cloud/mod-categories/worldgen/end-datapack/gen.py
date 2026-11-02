import json, os
R='/home/user/endpack/diaithir_end_dp'
def w(p,o):
    p=os.path.join(R,p); os.makedirs(os.path.dirname(p),exist_ok=True)
    json.dump(o,open(p,'w'),indent=1)
w('../pack.mcmeta',{"pack":{"description":"Diaithir End biomes (clean-room)","min_format":[101,1],"max_format":[999,0]}}) if False else None
os.makedirs(R,exist_ok=True)
json.dump({"pack":{"description":"Diaithir End biomes (clean-room)","min_format":[101,1],"max_format":[999,0]}},open(R+'/pack.mcmeta','w'))
# name, parent band, surface block, [(feature block, tries)], water colour
B={
 'crystal_spires':('highlands','minecraft:calcite',[('minecraft:amethyst_cluster',6),('minecraft:end_rod',3)],'#b48cff'),
 'rime_reach':('highlands','minecraft:snow_block',[('minecraft:packed_ice',5),('minecraft:end_rod',2)],'#9fd8ff'),
 'sporewood':('midlands','minecraft:warped_nylium',[('minecraft:warped_fungus',8),('minecraft:warped_roots',12)],'#3fd0a0'),
 'ashen_dunes':('midlands','minecraft:soul_soil',[('minecraft:soul_fire',5)],'#6b6560'),
 'hollow_barrens':('barrens','minecraft:sculk',[],'#27333f'),
 'glimmer_isles':('small_islands','minecraft:moss_block',[('minecraft:moss_carpet',20),('minecraft:flowering_azalea',3),('minecraft:end_rod',2)],'#7fe07f'),
}
def feats(parent,extra):
    f=[[] for _ in range(11)]
    if parent in('highlands','midlands'): f[4]=['minecraft:end_gateway_return']
    f[9]=['minecraft:chorus_plant']+extra
    return f
def biome(parent,feat_ids,water):
    return {"carvers":[],"downfall":0.5,"effects":{"water_color":water},"features":feats(parent,feat_ids),"has_precipitation":False,"spawn_costs":{},
     "spawners":{k:[] for k in ["ambient","axolotls","creature","misc","underground_water_creature","water_ambient","water_creature"]}|{"monster":[{"type":"minecraft:enderman","maxCount":4,"minCount":4,"weight":10}]},"temperature":0.5}
for n,(par,surf,fs,water) in B.items():
    ids=[]
    for i,(blk,tries) in enumerate(fs):
        fid=f'{n}_{i}'; ids.append('diaithir_end:'+fid)
        w(f'data/diaithir_end/worldgen/configured_feature/{fid}.json',{"type":"minecraft:simple_block","config":{"to_place":{"type":"minecraft:simple_state_provider","state":{"Name":blk}}}})
        w(f'data/diaithir_end/worldgen/placed_feature/{fid}.json',{"feature":'diaithir_end:'+fid,"placement":[
          {"type":"minecraft:count","count":{"type":"minecraft:uniform","min_inclusive":0,"max_inclusive":3}},{"type":"minecraft:in_square"},
          {"type":"minecraft:heightmap","heightmap":"WORLD_SURFACE_WG"},{"type":"minecraft:biome"},
          {"type":"minecraft:count","count":tries*4},
          {"type":"minecraft:random_offset","xz_spread":{"type":"minecraft:trapezoid","min":-6,"max":6,"plateau":0},"y_spread":{"type":"minecraft:trapezoid","min":-3,"max":3,"plateau":0}},
          {"type":"minecraft:block_predicate_filter","predicate":{"type":"minecraft:all_of","predicates":[
            {"type":"minecraft:matching_block_tag","tag":"minecraft:air"},
            {"type":"minecraft:solid","offset":[0,-1,0]}]}}]})
    w(f'data/diaithir_end/worldgen/biome/{n}.json',biome(par,ids,water))
# noise settings override: temperature/vegetation noise so multi_noise can vary biomes
ns=json.load(open('/tmp/claude-0/w/mc/data/minecraft/worldgen/noise_settings/end.json'))
ns['noise_router']['temperature']={"type":"minecraft:mul","argument1":2.5,"argument2":{"type":"minecraft:noise","noise":"minecraft:temperature","xz_scale":0.5,"y_scale":0.0}}
ns['noise_router']['vegetation']={"type":"minecraft:noise","noise":"minecraft:vegetation","xz_scale":0.12,"y_scale":0.0}
def sd(off): return {"type":"minecraft:stone_depth","offset":off,"add_surface_depth":False,"secondary_depth_range":0,"surface_type":"floor"}
rules=[{"type":"minecraft:condition","if_true":{"type":"minecraft:biome","biome_is":['diaithir_end:'+n]},
        "then_run":{"type":"minecraft:condition","if_true":sd(0),"then_run":{"type":"minecraft:block","result_state":{"Name":s[1]}}}} for n,s in B.items()]
ns['surface_rule']={"type":"minecraft:sequence","sequence":rules+[ns['surface_rule']]}
w('data/minecraft/worldgen/noise_settings/end.json',ns)
# Wover (BCLib dependency) owns the End biome source; our biomes join its c:is_end/* tags
tag={'highlands':'highland','midlands':'midland','barrens':'barrens','small_islands':'small_island'}
land=[]
for band,t in tag.items():
    vals=['diaithir_end:'+n for n,s_ in B.items() if s_[0]==band]
    land+=vals
    w(f'data/c/tags/worldgen/biome/is_end/{t}.json',{"replace":False,"values":vals})
w('data/c/tags/worldgen/biome/is_end/land.json',{"replace":False,"values":land})

for n,(par,surf,fs,water) in B.items():
    w(f'data/diaithir_end/wover/worldgen/biome_data/{n}.json',{"type":"betternether:biome","biome":"diaithir_end:"+n,"generation_data":{"intended_placement":"minecraft:is_end","parameter_points":[{"continentalness":0.0,"depth":0.0,"erosion":0.0,"humidity":0.0,"offset":0.0,"temperature":0.0,"weirdness":0.0}]}})
