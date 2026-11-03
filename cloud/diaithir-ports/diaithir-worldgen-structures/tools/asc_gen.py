#!/usr/bin/env python3
# S6934 Age VII/VIII + Rodos sites (own design, ASCENDANT.md): nine Ascendant rite sites and three shard sites.
"""Usage: python3 -I tools/asc_gen.py (run in the module folder). Vanilla blocks only.
These are game-original sites (not Panscriptum entries); they are listed in this module README."""
import os,sys,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import lib_sites as L
from lib_sites import G,NS,w,jig,tmpl
F=L.F
def ring(g,cx,r,y0,y1,blk,n):
    import math
    for i in range(n):
        a=i*6.2832/n; x=int(round(cx+r*math.cos(a))); z=int(round(cx+r*math.sin(a))); g.box(x,y0,z,x,y1,z,blk)
def base(W,blk,under="cobblestone"):
    g=G(); g.box(0,-F,0,W-1,-1,W-1,under); g.box(0,0,0,W-1,0,W-1,blk); return g
SITES={}
def site(sid,name,tier,text):
    def d(fn): SITES[sid]=(name,tier,text,fn); return fn
    return d
@site("antlered_hollow","Antlered Hollow",1,"A sunken ring of bone-white antlers around an empty hollow. The Antlered Hollow wakes where an altar stands at its heart.")
def _(): 
    W=17; c=8; g=base(W,"podzol")
    g.box(c-3,-3,c-3,c+3,0,c+3,"air"); g.box(c-3,-F,c-3,c+3,-3,c+3,"coarse_dirt")
    ring(g,c,6,1,4,"spruce_fence",14); ring(g,c,6,5,5,"bone_block",14); ring(g,c,4,1,1,"moss_block",10); return g,W
@site("cauldron_heart","Cauldron-Heart",1,"A stone bowl with a hot red core. The Cauldron-Heart wakes where an altar stands in the bowl.")
def _():
    W=17; c=8; g=base(W,"stone_bricks")
    g.box(c-4,0,c-4,c+4,2,c+4,"stone_bricks"); g.box(c-3,1,c-3,c+3,2,c+3,"air"); g.box(c-2,0,c-2,c+2,0,c+2,"magma_block"); g.set(c,1,c,"cauldron")
    for x,z in((c-4,c-4),(c+4,c-4),(c-4,c+4),(c+4,c+4)): g.box(x,3,z,x,5,z,"nether_bricks"); g.set(x,6,z,"lantern[hanging=false]")
    return g,W
@site("tide_reaver","Tide Reaver Dock",1,"A drowned jetty of dark planks and prismarine posts. The Tide Reaver wakes where an altar stands at its end.")
def _():
    W=17; g=base(W,"dark_oak_planks","prismarine_bricks")
    for x in range(0,W,4):
        for z in range(0,W,4): g.box(x,-F,z,x,3,z,"prismarine_bricks")
    g.box(0,1,0,W-1,1,0,"dark_oak_fence"); g.box(0,1,W-1,W-1,1,W-1,"dark_oak_fence"); g.box(4,0,4,12,0,12,"sea_lantern" if False else "prismarine"); return g,W
@site("foundry_sovereign","Foundry Sovereign Forge",2,"A blackstone forge hall, anvils in rows. The Foundry Sovereign wakes where an altar stands before the great furnace.")
def _():
    W=21; c=10; g=base(W,"blackstone","deepslate_bricks")
    g.shell(2,0,2,W-3,6,W-3,"polished_blackstone_bricks"); g.box(3,1,3,W-4,5,W-4,"air"); g.box(c-1,0,2,c+1,2,2,"air")
    for x in range(4,W-4,3): g.set(x,1,5,"anvil[facing=north]"); g.set(x,1,W-6,"blast_furnace[facing=south]")
    g.box(3,6,3,W-4,6,W-4,"deepslate_tiles"); return g,W
@site("mist_weaver","Mist Weaver Spire",2,"A thin white spire wound in glass. The Mist Weaver wakes where an altar stands at its foot.")
def _():
    W=15; c=7; g=base(W,"calcite")
    g.box(c-1,0,c-1,c+1,14,c+1,"quartz_pillar"); g.box(c,3,c,c,14,c,"white_stained_glass")
    for y in range(2,14,3): ring(g,c,3,y,y,"white_stained_glass",12)
    ring(g,c,5,1,1,"snow_block",16); return g,W
@site("ash_seraph","Ash Seraph Dais",2,"A wide dais of ash and basalt under black wings of stone. The Ash Seraph wakes where an altar stands at its centre.")
def _():
    W=19; c=9; g=base(W,"basalt[axis=y]","smooth_basalt")
    g.box(c-4,0,c-4,c+4,1,c+4,"polished_basalt[axis=y]"); g.box(c-2,2,c-2,c+2,2,c+2,"magma_block")
    for s in(-1,1):
        for i in range(1,6): g.box(c+s*(3+i),1,c-i+1,c+s*(3+i),1+i,c-i+1,"blackstone")
    return g,W
@site("dusk_wyrm","Dusk Wyrm Spine",3,"An arch of enormous ribs lying across the land. The Dusk Wyrm wakes where an altar stands under the spine.")
def _():
    import math
    W=25; c=12; g=base(W,"coarse_dirt")
    for x in range(2,W-2,3):
        r=(W-5)/2.0
        h=int(round(7*math.sqrt(max(0,1-((x-c)/r)**2))))+1
        g.box(x,1,8,x,h,8,"bone_block"); g.box(x,1,16,x,h,16,"bone_block"); g.box(x,h,8,x,h,16,"bone_block")
    g.box(c-1,0,c-1,c+1,0,c+1,"obsidian"); return g,W
@site("rootbreaker","Rootbreaker Grove",3,"A ring of broken trees with their roots in the air. The Rootbreaker wakes where an altar stands among the roots.")
def _():
    W=21; c=10; g=base(W,"rooted_dirt","mud")
    ring(g,c,7,1,7,"mangrove_log[axis=y]",12); ring(g,c,6,1,2,"mangrove_roots",18); ring(g,c,7,8,8,"mangrove_leaves[persistent=true]",12)
    g.box(c-2,0,c-2,c+2,0,c+2,"moss_block"); return g,W
@site("last_wheel","The Last Wheel Clock",3,"A wheel of twelve stones laid flat, a shard at its hub. The Last Wheel wakes where an altar stands at the hub.")
def _():
    W=27; c=13; g=base(W,"smooth_stone","stone_bricks")
    ring(g,c,11,0,0,"gold_block",12); ring(g,c,11,1,3,"stone_brick_wall",12); ring(g,c,8,0,0,"chiseled_stone_bricks",24); g.box(c-1,0,c-1,c+1,0,c+1,"amethyst_block"); return g,W
@site("shard_spire","Shard Spire",4,"A tall spire grown from age shards. It hums on the hour. Shard sites bear the Last Wheel's drops.")
def _():
    W=15; c=7; g=base(W,"calcite","tuff")
    for i,h in enumerate((12,9,7,5)):
        dx,dz=((0,0),(2,1),(-2,2),(1,-3))[i]; g.box(c+dx,1,c+dz,c+dx,h,c+dz,"amethyst_block"); g.set(c+dx,h+1,c+dz,"amethyst_cluster[facing=up]")
    return g,W
@site("shard_gate","Shard Gate",4,"A tall arch of dark stone and amethyst. The Gate stands closed until the Last Wheel is beaten and the rush cleared.")
def _():
    W=15; c=7; g=base(W,"polished_deepslate","deepslate_bricks")
    g.box(3,1,c,4,9,c,"deepslate_bricks"); g.box(W-5,1,c,W-4,9,c,"deepslate_bricks"); g.box(3,10,c,W-4,10,c,"chiseled_deepslate")
    g.box(5,1,c,W-6,1,c,"air"); g.box(5,10,c,W-6,10,c,"amethyst_block"); return g,W
@site("shard_ogham","Ogham Circle",4,"Nine stones for nine trees: Birch, Rowan, Alder, Willow, Ash, Hawthorn, Oak, Holly, Hazel.")
def _():
    W=21; c=10; g=base(W,"grass_block","cobblestone"); ring(g,c,8,1,4,"stone_bricks",9); ring(g,c,8,5,5,"chiseled_stone_bricks",9); g.set(c,0,c,"enchanting_table"); return g,W
def main():
    ages={}
    for sid,(name,tier,text,fn) in SITES.items():
        g,W=fn()
        nbt=L.building_nbt("landmark","Iron",2,(g.b,W,W))
        w(f"data/{NS}/structure/asc/{sid}.nbt",nbt)
        pool=f"asc/{sid}"
        w(f"data/{NS}/worldgen/template_pool/{pool}.json",{"name":f"{NS}:{pool}","fallback":"minecraft:empty","elements":[{"weight":1,"element":{"element_type":"minecraft:single_pool_element","location":f"{NS}:asc/{sid}","projection":"rigid","processors":"minecraft:empty"}}]})
        age=7 if tier==1 else 8
        w(f"data/{NS}/tags/worldgen/biome/asc/{sid}.json",{"values":["#minecraft:is_overworld"]})
        w(f"data/{NS}/worldgen/structure/asc/{sid}.json",{"type":"minecraft:jigsaw","biomes":f"#{NS}:asc/{sid}","step":"surface_structures","spawn_overrides":{},"terrain_adaptation":"beard_thin","start_pool":f"{NS}:{pool}","size":1,"max_distance_from_center":24,"use_expansion_hack":False,"start_height":{"absolute":-1},"project_start_to_heightmap":"WORLD_SURFACE_WG","liquid_settings":"ignore_waterlogging"})
        salt=int(hashlib.md5(("asc"+sid).encode()).hexdigest()[:7],16)
        w(f"data/{NS}/worldgen/structure_set/asc/{sid}.json",{"structures":[{"structure":f"{NS}:asc/{sid}","weight":1}],"placement":{"type":"minecraft:random_spread","spacing":120,"separation":40,"salt":salt}})
        ages.setdefault(age,[]).append(f"{NS}:asc/{sid}")
    for a,l in ages.items(): w(f"data/{NS}/tags/worldgen/structure/asc_age_{a}.json",{"values":l})
    print("asc sites",len(SITES),{a:len(l) for a,l in ages.items()})
if __name__=="__main__": main()
