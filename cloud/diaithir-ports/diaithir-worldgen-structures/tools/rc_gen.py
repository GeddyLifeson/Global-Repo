#!/usr/bin/env python3
# S6850 Recurrent Complex function group: mazes, biome transformers, inventory generators, Age tags (clean-room, data only).
"""Usage: rc_gen.py. Covers what Recurrent Complex does, from its public description only (no code, templates or assets of the mod):
 - mazes: jigsaw labyrinths of 7x6x7 cells (hub, straight, turn, tee, cross, dead end, room) in five themes;
 - transformers: processor lists that swap a structure's materials for the biome (desert, snow, jungle, nether, mossy);
 - inventory generators: themed chest loot tables (rc/chest/<kind>), plus a spawner and chest in each room;
 - natural generation: one structure per theme with c:/minecraft biome tags and Age tags `rc_age_<n>`.
Writes under src/main/resources/data/diaithir_worldgen/."""
import os,sys,json,hashlib,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import gen
from gen import w,NS
import lib_sites as L
F=0
SZ=7; H=6
THEMES={
 "stone":dict(w="stone_bricks",m="mossy_stone_bricks",c="cracked_stone_bricks",f="cobblestone",l="wall_torch",age=2,tag=["#minecraft:is_overworld"],mob="minecraft:zombie",under=False),
 "sand":dict(w="sandstone",m="cut_sandstone",c="smooth_sandstone",f="sand",l="wall_torch",age=2,tag=["#c:is_desert","#minecraft:is_badlands"],mob="minecraft:husk",under=False),
 "nether":dict(w="nether_bricks",m="cracked_nether_bricks",c="red_nether_bricks",f="blackstone",l="soul_wall_torch",age=3,tag=["#minecraft:is_nether"],mob="minecraft:wither_skeleton",under=False,nether=True),
 "ice":dict(w="packed_ice",m="snow_block",c="blue_ice",f="snow_block",l="wall_torch",age=3,tag=["#c:is_snowy"],mob="minecraft:stray",under=False),
 "deep":dict(w="deepslate_bricks",m="cracked_deepslate_bricks",c="tuff_bricks",f="deepslate_tiles",l="soul_wall_torch",age=4,tag=["#c:is_underground"],mob="minecraft:cave_spider",under=True)}
OPEN={"hub":"NESW","room":"NESW","cross":"NESW","tee":"NEW","straight":"NS","turn":"NE","dead":"N"}
WEIGHT={"straight":4,"turn":4,"tee":3,"cross":1,"dead":2,"room":2}
DIRS={"N":(3,0,-1),"S":(3,0,1),"E":(1,0,3),"W":(-1,0,3)}  # face centres; filled below
ORI={"N":"north_up","S":"south_up","E":"east_up","W":"west_up"}
def cell(th,kind):
    t=THEMES[th]; g=L.G(); g.box(0,0,0,SZ-1,0,SZ-1,t["f"]); g.box(0,H-1,0,SZ-1,H-1,SZ-1,t["w"])
    for x in range(SZ):
        for z in range(SZ):
            for y in range(1,H-1):
                edge=x in(0,SZ-1) or z in(0,SZ-1)
                if edge:
                    r=int(hashlib.md5(f"{th}{kind}{x}{y}{z}".encode()).hexdigest()[:2],16)%10
                    g.set(x,y,z,t["w"] if r<6 else t["m"] if r<9 else t["c"])
    g.box(1,1,1,SZ-2,H-2,SZ-2,"air")
    for d in OPEN[kind]:
        if d=="N": g.box(2,1,0,4,3,0,"air")
        if d=="S": g.box(2,1,SZ-1,4,3,SZ-1,"air")
        if d=="W": g.box(0,1,2,0,3,4,"air")
        if d=="E": g.box(SZ-1,1,2,SZ-1,3,4,"air")
    blocks={k:(L.gen.fixblock(v),None) for k,v in g.b.items()}
    for k in list(blocks):  # convert F offset: grid y already shifted by G.set; keep as is
        pass
    yy=0+L.F+1  # jigsaw row = floor+1 in G's shifted coordinates
    conn={"N":(3,yy,0),"S":(3,yy,SZ-1),"W":(0,yy,3),"E":(SZ-1,yy,3)}
    for d in OPEN[kind]:
        blocks[conn[d]]=(f"minecraft:jigsaw[orientation={ORI[d]}]",L.jig(f"{NS}:rc_cell",f"{NS}:rc_cell",f"{NS}:rc/maze/{th}/cell",ORI[d]))
    if kind in("room","hub"):
        for x,z in((1,1),(SZ-2,1),(1,SZ-2),(SZ-2,SZ-2)):
            for y in range(1,H-1): blocks[(x,y+L.F,z)]=(L.gen.fixblock(t["m"]),None)
        blocks[(3,1+L.F,3)]=("minecraft:chest[facing=south]",{"id":(8,"minecraft:chest"),"LootTable":(8,f"{NS}:rc/chest/{'armory' if th!='ice' else 'library'}")})
        blocks[(2,1+L.F,3)]=("minecraft:spawner",{"id":(8,"minecraft:mob_spawner"),"SpawnData":(10,{"entity":(10,{"id":(8,t["mob"])})})})
    elif kind=="dead":
        blocks[(3,1+L.F,3)]=("minecraft:chest[facing=south]",{"id":(8,"minecraft:chest"),"LootTable":(8,f"{NS}:rc/chest/treasury")})
    else:
        blocks[(3,H-2+L.F-1,2)]=(f"minecraft:{t['l']}[facing=south]" if t["l"].endswith("torch") and False else "minecraft:lantern[hanging=true]",None)
    return L.tmpl(blocks,(SZ,H+L.F,SZ))
CHESTS={"armory":["iron_sword","iron_chestplate","shield","arrow","bow","iron_ingot","chainmail_helmet"],
 "library":["book","paper","enchanted_book","ink_sac","name_tag","compass","clock"],
 "treasury":["gold_ingot","emerald","diamond","gold_nugget","amethyst_shard","lapis_lazuli","golden_apple"],
 "kitchen":["bread","cooked_beef","apple","carrot","potato","baked_potato","cake"],
 "tomb":["bone","rotten_flesh","gold_ingot","iron_axe","skeleton_skull" if False else "arrow","torch","candle"],
 "lab":["redstone","glowstone_dust","gunpowder","glass_bottle","blaze_powder","sugar","spider_eye"]}
def chest(kind):
    it=[i for i in CHESTS[kind] if i in gen.IT]
    return {"type":"minecraft:chest","pools":[{"rolls":{"type":"minecraft:uniform","min":2,"max":5},"entries":[{"type":"minecraft:item","name":"minecraft:"+i,"weight":10-j,"functions":[{"function":"minecraft:set_count","count":{"type":"minecraft:uniform","min":1,"max":3}}]} for j,i in enumerate(it)]}]}
TRANS={"desert":[("stone_bricks","sandstone"),("mossy_stone_bricks","cut_sandstone"),("cobblestone","sand"),("oak_planks","birch_planks")],
 "snow":[("stone_bricks","packed_ice"),("cobblestone","snow_block"),("oak_planks","spruce_planks"),("mossy_stone_bricks","blue_ice")],
 "jungle":[("stone_bricks","mossy_stone_bricks"),("cobblestone","mossy_cobblestone"),("oak_planks","jungle_planks")],
 "nether":[("stone_bricks","nether_bricks"),("cobblestone","blackstone"),("oak_planks","crimson_planks"),("mossy_stone_bricks","cracked_nether_bricks")],
 "mossy":[("stone_bricks","mossy_stone_bricks"),("cobblestone","mossy_cobblestone")]}
def proc(rules):
    return {"processors":[{"processor_type":"minecraft:rule","rules":[{"input_predicate":{"predicate_type":"minecraft:random_block_match","block":"minecraft:"+a,"probability":0.85},"location_predicate":{"predicate_type":"minecraft:always_true"},"output_state":{"Name":"minecraft:"+b}} for a,b in rules]}]}
def main():
    for k in CHESTS: w(f"data/{NS}/loot_table/rc/chest/{k}.json",chest(k))
    for n,r in TRANS.items(): w(f"data/{NS}/worldgen/processor_list/rc/{n}.json",proc(r))
    ages=collections.defaultdict(list)
    for th,t in THEMES.items():
        els=[];caps=[]
        for kind in ("hub","room","cross","tee","turn","straight","dead"):
            w(f"data/{NS}/structure/rc/maze/{th}/{kind}.nbt",cell(th,kind))
            el={"element_type":"minecraft:single_pool_element","location":f"{NS}:rc/maze/{th}/{kind}","projection":"rigid","processors":"minecraft:empty"}
            if kind=="dead": caps.append({"weight":1,"element":el})
            if kind in WEIGHT: els.append({"weight":WEIGHT[kind],"element":el})
        w(f"data/{NS}/worldgen/template_pool/rc/maze/{th}/cell.json",{"name":f"{NS}:rc/maze/{th}/cell","fallback":f"{NS}:rc/maze/{th}/cap","elements":els})
        w(f"data/{NS}/worldgen/template_pool/rc/maze/{th}/cap.json",{"name":f"{NS}:rc/maze/{th}/cap","fallback":"minecraft:empty","elements":caps})
        w(f"data/{NS}/worldgen/template_pool/rc/maze/{th}/hub.json",{"name":f"{NS}:rc/maze/{th}/hub","fallback":"minecraft:empty","elements":[{"weight":1,"element":{"element_type":"minecraft:single_pool_element","location":f"{NS}:rc/maze/{th}/hub","projection":"rigid","processors":"minecraft:empty"}}]})
        w(f"data/{NS}/tags/worldgen/biome/rc/{th}.json",{"values":[{"id":x[1:],"required":False} if False else ({"id":x,"required":False} if x.startswith("#c:") else x) for x in t["tag"]]})
        sid=f"rc/maze_{th}"
        w(f"data/{NS}/worldgen/structure/{sid}.json",{"type":"minecraft:jigsaw","biomes":f"#{NS}:rc/{th}","step":"underground_structures" if t["under"] or t.get("nether") else "surface_structures",
          "spawn_overrides":{},"terrain_adaptation":"encapsulate" if t["under"] else "beard_thin","start_pool":f"{NS}:rc/maze/{th}/hub","size":7,"max_distance_from_center":80,"use_expansion_hack":False,
          "start_height":{"absolute":(-30 if t["under"] else 64 if t.get("nether") else -1)},**({} if t["under"] or t.get("nether") else {"project_start_to_heightmap":"WORLD_SURFACE_WG"})})
        salt=int(hashlib.md5(("rc"+th).encode()).hexdigest()[:7],16)
        w(f"data/{NS}/worldgen/structure_set/{sid}.json",{"structures":[{"structure":f"{NS}:{sid}","weight":1}],"placement":{"type":"minecraft:random_spread","spacing":34,"separation":12,"salt":salt}})
        ages[t["age"]].append(f"{NS}:{sid}")
    for a,l in ages.items(): w(f"data/{NS}/tags/worldgen/structure/rc_age_{a}.json",{"values":l})
    w("migration_recurrentcomplex.json",{"note":"Recurrent Complex Volts keeps its structures as template files in its config folder, not as registry ids, so no old ids exist in the pack. Any recurrentcomplex: reference falls back to these:","old_prefix":"recurrentcomplex","new_structures":[f"{NS}:rc/maze_{t}" for t in THEMES]})
    print("rc themes",len(THEMES),"cells",len(THEMES)*7)
if __name__=="__main__": main()
