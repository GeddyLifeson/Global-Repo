#!/usr/bin/env python3
# S6835 Panscriptum STRUCTURE entries -> jigsaw sites (plaque with the entry's own text + class building), data only.
"""Usage: lib_sites.py [--limit N]. Reads codex-store/library.sqlite (summary = real entry text), library-content/content.sqlite
(STRUCTURE ids) and planets/planets.tsv. Writes under src/main/resources/data/diaithir_worldgen/: per-entry plaque
templates, per (planet,class,band) start pools, shared class buildings, structures, one structure_set per planet,
planet biome tags and Age structure tags. The plaque is a lectern holding a written book with the entry text verbatim."""
import math,sqlite3,re,os,sys,json,csv,hashlib,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import gen
from gen import N,nbt,w,NS,OUT
SRC="/mnt/project-files/"
LIM=int(sys.argv[sys.argv.index("--limit")+1]) if "--limit" in sys.argv else 0

# ---- classification (first match on the first sentence, then the whole text) ----
CLASSES=[("bridge","bridge|crossing|causeway|viaduct"),("tower","tower|spire|lighthouse|beacon|obelisk|minaret|pillar"),
("tomb","tomb|burial|crypt|grave|barrow|mausoleum|catacomb|ossuary|cairn"),
("temple","shrine|temple|sanctuary|sacred|altar|chapel|monastery|abbey|oracle|cathedral|worship"),
("harbor","harbou?r|dock|wharf|quay|reef|sunken|drowned|shipyard|jetty|pier|lagoon"),
("fortress","fortress|fort\\b|keep|citadel|stronghold|castle|bastion|rampart|garrison|outpost|fortified|walled|watchtower|barracks"),
("delve","cavern|cave|grotto|mine\\b|tunnel|subterranean|delve|underground|dungeon|burrow|buried|catacomb|chasm|pit\\b|hollow"),
("forge","forge|foundry|factory|workshop|furnace|mill\\b|quarry|station|rail|refinery|smelt|engine|reactor|lab"),
("hall","hall|court|arena|library|academy|theat|market|palace|manor|house|inn\\b|tavern|guild|school|museum|stadium|bath|barracks|amphitheat"),
("garden","garden|grove|orchard|field|farm|spring|well\\b|lake|pool|meadow|forest|glade|fountain|oasis"),
("ruin","ruin|fallen|crumbl|broken|forgotten|collapsed|shattered|wreck|remnant|abandoned")]
CRE=[(c,re.compile(p,re.I)) for c,p in CLASSES]
def classify(text):
    first=re.split(r"(?<=[.!?])\s",text,1)[0]
    for src in (first,text):
        for c,r in CRE:
            if r.search(src): return c
    return "landmark"
BANDS=[(1,2),(3,4),(5,6),(7,9)]
def band(t):
    for i,(a,b) in enumerate(BANDS):
        if a<=t<=b: return i
    return 3

# ---- palettes per soil (vanilla blocks only) ----
PAL={"Bloom":dict(w="stone_bricks",m="mossy_stone_bricks",f="cobblestone",a="oak_log[axis=y]",r="spruce_planks",l="lantern",g="oak_leaves[persistent=true]",c="chiseled_stone_bricks"),
"Frost":dict(w="packed_ice",m="snow_block",f="blue_ice",a="spruce_log[axis=y]",r="spruce_planks",l="lantern",g="spruce_leaves[persistent=true]",c="snow_block"),
"Storm":dict(w="quartz_bricks",m="calcite",f="smooth_quartz",a="quartz_pillar[axis=y]",r="white_concrete",l="sea_lantern",g="azalea_leaves[persistent=true]",c="chiseled_quartz_block"),
"Hollow":dict(w="deepslate_bricks",m="cracked_deepslate_bricks",f="deepslate_tiles",a="polished_deepslate",r="tuff_bricks",l="soul_lantern",g="glow_lichen",c="chiseled_deepslate"),
"Iron":dict(w="polished_andesite",m="stone_bricks",f="smooth_stone",a="cut_copper",r="weathered_cut_copper",l="lantern",g="moss_block",c="iron_block"),
"Ember":dict(w="nether_bricks",m="cracked_nether_bricks",f="blackstone",a="polished_blackstone_bricks",r="red_nether_bricks",l="soul_lantern",g="crimson_roots",c="chiseled_nether_bricks"),
"Quiet":dict(w="end_stone_bricks",m="purpur_block",f="end_stone",a="purpur_pillar[axis=y]",r="purpur_block",l="end_rod[facing=up]",g="chorus_flower[age=5]",c="chiseled_polished_blackstone")}
SIZE=[("s",1),("m",2),("l",3)]
F=4  # foundation depth below the floor (jigsaw row)

class G:
    def __init__(s): s.b={}
    def set(s,x,y,z,v): s.b[(x,y+F,z)]=v
    def box(s,x0,y0,z0,x1,y1,z1,v):
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                for z in range(z0,z1+1): s.set(x,y,z,v)
    def shell(s,x0,y0,z0,x1,y1,z1,v):
        for x in range(x0,x1+1):
            for y in range(y0,y1+1):
                for z in range(z0,z1+1):
                    if x in(x0,x1) or z in(z0,z1) or y in(y0,y1): s.set(x,y,z,v)
def pal(soil): return PAL[soil]
def lamp(p): return p["l"]+"[hanging=false]" if p["l"].endswith("lantern") and p["l"]!="sea_lantern" else p["l"]
def build(cls,soil,k,seed):
    """returns (grid, W, Dz): grid keys (x,y,z) y includes foundation; door/jigsaw at (W//2,F,Dz-1) facing south."""
    p=pal(soil); g=G(); h=int(hashlib.md5(f"{cls}{soil}{k}{seed}".encode()).hexdigest()[:8],16)
    W=7+4*k; D=7+4*k; hh=4+2*k
    cx=W//2
    def rnd(x,y,z,n): return int(hashlib.md5(f"{h}{x}.{y}.{z}".encode()).hexdigest()[:4],16)%n
    # foundation
    g.box(0,-F,0,W-1,-1,D-1,p["f"])
    if cls=="tower":
        W=D=5+2*k; cx=W//2; g.box(0,-F,0,W-1,-1,D-1,p["f"]); H=10+8*k
        g.shell(0,0,0,W-1,H,D-1,p["w"]); g.box(1,0,1,W-2,H-1,W-2,"air"); g.box(1,0,1,W-2,0,W-2,p["f"])
        for y in range(3,H,4): g.set(cx,y,0,"glass_pane"); g.set(cx,y,D-1,"glass_pane"); g.set(0,y,cx,"glass_pane"); g.set(W-1,y,cx,"glass_pane")
        for x in range(0,W,2):
            for z in (0,D-1): g.set(x,H+1,z,p["w"])
            g.set(x,H+1,0,p["w"]); g.set(0,H+1,x,p["w"]); g.set(W-1,H+1,x,p["w"])
        g.set(cx,H-1,cx,lamp(p))
        g.set(cx,0,D-1,"air"); g.set(cx,1,D-1,"air")
    elif cls=="temple":
        g.box(0,0,0,W-1,0,D-1,p["f"]); g.box(1,1,1,W-2,1,D-2,p["w"])
        for x in (1,W-2):
            for z in range(2,D-1,2): g.box(x,2,z,x,hh,z,p["a"])
        g.box(1,hh+1,1,W-2,hh+1,D-2,p["r"]); g.set(cx,2,2,p["c"]); g.set(cx,3,2,lamp(p))
    elif cls=="tomb":
        r=W//2
        for x in range(W):
            for z in range(D):
                d=((x-cx)**2+(z-cx)**2)**.5
                if d<=r+.5:
                    top=int((r-d)*.9)
                    for y in range(0,top+1): g.set(x,y,z,"coarse_dirt" if y<top else "grass_block" if soil in("Bloom","Iron") else p["m"])
        g.box(cx-1,0,cx-1,cx+1,2,cx+1,"air"); g.box(cx,0,cx+1,cx,1,D-1,"air"); g.set(cx,0,cx,"chest[facing=south]")
    elif cls=="fortress":
        g.shell(0,0,0,W-1,hh,D-1,p["w"]); g.box(1,0,1,W-2,hh-1,D-2,"air"); g.box(1,0,1,W-2,0,D-2,p["f"])
        for x,z in((0,0),(W-1,0),(0,D-1),(W-1,D-1)): g.box(x-(x>0),0,z-(z>0),x+(x==0),hh+3,z+(z==0),p["m"])
        for x in range(0,W,2):
            for z in (0,D-1): g.set(x,hh+1,z,p["w"])
        g.set(cx,0,D-1,"air"); g.set(cx,1,D-1,"air"); g.set(cx,2,D-1,"air"); g.set(cx,0,cx,"chest[facing=south]")
    elif cls=="delve":
        g.box(0,-F,0,W-1,-1,D-1,p["f"]); g.box(1,-F,1,W-2,-1,D-2,"air")
        g.box(0,-F,0,W-1,-F,D-1,p["f"])
        g.shell(0,-F,0,W-1,hh,D-1,p["w"]); g.box(1,-F+1,1,W-2,hh-1,D-2,"air")
        for i in range(0,W-2,3): g.set(1+i,-F+1,1,lamp(p))
        g.set(cx,-F+1,cx,"chest[facing=south]"); g.box(cx,0,D-1,cx,2,D-1,"air")
    elif cls=="hall":
        g.box(0,0,0,W-1,0,D-1,p["f"]); g.shell(0,1,0,W-1,hh,D-1,p["w"]); g.box(1,1,1,W-2,hh-1,D-2,"air")
        for z in range(2,D-1,2): g.box(1,1,z,1,hh-1,z,p["a"]); g.box(W-2,1,z,W-2,hh-1,z,p["a"])
        g.box(0,hh+1,0,W-1,hh+1,D-1,p["r"]); g.set(cx,1,D-1,"air"); g.set(cx,2,D-1,"air"); g.set(cx,1,cx,p["c"])
    elif cls=="harbor":
        g.box(0,0,0,W-1,0,D-1,"spruce_planks");
        for x in range(0,W,3):
            for z in range(0,D,3): g.box(x,-F,z,x,-1,z,"spruce_log[axis=y]")
        g.shell(1,1,1,4,3,4,"spruce_planks"); g.box(2,1,2,3,2,3,"air"); g.set(cx,1,D-1,"lantern[hanging=false]")
    elif cls=="ruin":
        g.shell(0,0,0,W-1,hh,D-1,p["m"])
        for (x,y,z),v in list(g.b.items()):
            if y>=F and rnd(x,y,z,100)<30+int(y*4): del g.b[(x,y,z)]
        for (x,y,z) in [(x,y,z) for (x,y,z) in g.b if y>=F+1 and rnd(x,y,z,100)<8]: g.b[(x,y,z)]="cobweb" if soil=="Hollow" else p["g"]
        g.set(cx,0,cx,"chest[facing=south]")
    elif cls=="forge":
        g.box(0,0,0,W-1,0,D-1,p["f"]); g.shell(0,1,0,W-1,hh,D-1,p["w"]); g.box(1,1,1,W-2,hh-1,D-2,"air"); g.set(cx,1,D-1,"air"); g.set(cx,2,D-1,"air")
        g.set(2,1,2,"blast_furnace[facing=south]"); g.set(3,1,2,"anvil"); g.set(2,2,2,"air"); g.box(W-3,1,2,W-3,hh+3,2,"bricks"); g.set(W-3,1,3,"lava_cauldron" if False else "cauldron")
        g.box(0,hh+1,0,W-1,hh+1,D-1,p["r"])
    elif cls=="garden":
        g.box(0,0,0,W-1,0,D-1,"grass_block" if soil in("Bloom","Iron","Storm") else p["f"]);
        for x in range(W):
            for z in range(D):
                r=rnd(x,1,z,10)
                if (x in(0,W-1) or z in(0,D-1)): g.set(x,1,z,"oak_fence" if soil in("Bloom","Iron") else p["m"])
                elif r<3: g.set(x,1,z,p["g"].split("[")[0]+("[persistent=true]" if "leaves" in p["g"] else ""))
        g.set(cx,0,cx,"water"); g.set(cx,1,cx,"air"); g.set(cx,1,D-1,"air")
    elif cls=="bridge":
        W=5; D=9+8*k; cx=2; g.b.clear(); g.box(0,-F,0,4,-1,0,p["f"]); g.box(0,-F,D-1,4,-1,D-1,p["f"])
        g.box(1,0,0,3,0,D-1,p["w"])
        for z in range(0,D): g.set(0,1,z,p["a"].split("[")[0] if z%4==0 else "stone_brick_wall" if soil!="Quiet" else "purpur_block"); g.set(4,1,z,p["a"].split("[")[0] if z%4==0 else "stone_brick_wall" if soil!="Quiet" else "purpur_block")
        for z in range(2,D-2,4): g.box(1,-F,z,3,-1,z,p["w"])
    else:  # landmark: standing stone ring around a plinth
        r=W//2-1
        for i in range(8 if k<3 else 12):
            import math
            x=int(round(cx+r*math.cos(i*6.2832/(8 if k<3 else 12)))); z=int(round(cx+r*math.sin(i*6.2832/(8 if k<3 else 12))))
            g.box(x,0,z,x,2+rnd(x,0,z,3)+k,z,p["a"].split("[")[0]+"[axis=y]" if "pillar" in p["a"] or "log" in p["a"] else p["a"])
        g.box(cx-1,0,cx-1,cx+1,0,cx+1,p["c"]); g.set(cx,1,cx,lamp(p))
    return g.b,W,D


# ---- Terra: one building per entry, shaped and made from what its text says ----
NUM={"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7}
MATS=[("terracotta|clay","terracotta","bricks"),("red brick|brick","bricks","stone_bricks"),("timber|wooden|wood\\b|thatch","oak_planks","oak_log[axis=y]"),
("white|limestone|chalk|marble","calcite","smooth_quartz"),("sand|desert|sandstone|dune","sandstone","cut_sandstone"),("copper|bronze","cut_copper","copper_block"),
("steel|iron|glass|machine","iron_block","glass"),("gold","gold_block","polished_andesite"),("earth|turf|sod","coarse_dirt","dirt"),("ice|snow|cold","packed_ice","snow_block"),("basalt|dark|black","polished_blackstone_bricks","blackstone"),("stone|rock|megalith|boulder","stone_bricks","cobblestone")]
def terra_build(text,cls):
    t=text.lower(); t=t.split(" anchor:")[0]
    wall,acc="stone_bricks","cobblestone"
    for p,a,b in MATS:
        if re.search(p,t): wall,acc=a,b; break
    k=3 if re.search(r"huge|vast|great|giant|widest|enormous|towering",t) else 1 if re.search(r"small|little|tiny|low\b",t) else 2
    n=next((v for w,v in NUM.items() if re.search(r"\b"+w+r"\b",t)),2)
    g=G(); W=D=9+4*k; cx=W//2
    def shape():
        if re.search(r"pyramid|stepped|ziggurat|layer after layer",t): return "pyramid"
        if re.search(r"\bring\b|circle|henge|standing stone|stones? (stand|are set|rise)|megalith",t): return "ring"
        if re.search(r"soldier|figures|rows of",t): return "rows"
        if re.search(r"cave|overhang|rock shelter|cliff|gorge|rock wall",t): return "cave"
        if re.search(r"mound|barrow|tumulus|hill (is|was) raised|piled",t): return "mound"
        if re.search(r"dome",t): return "dome"
        if re.search(r"\bgate\b",t): return "gate"
        if re.search(r"walled|citadel|\bcity\b|\btown\b|fort\b|stronghold",t): return "walled"
        if re.search(r"towers?\b",t): return "towers"
        if re.search(r"harbou?r|port\b|ships|quay|dock",t): return "harbor"
        if re.search(r"bridge|crossing",t): return "bridge"
        return None
    sh=shape()
    g.box(0,-F,0,W-1,-1,D-1,"cobblestone")
    if sh=="pyramid":
        for y in range(0,(W+1)//2):
            g.box(y,y,y,W-1-y,y,D-1-y,wall if y%2==0 else acc)
        g.box(cx,(W+1)//2,cx,cx,(W+1)//2,cx,"gold_block" if "gold" in t else wall); g.set(cx,0,D-1,"air"); g.box(cx,0,D-1,cx,1,D-1,"air")
    elif sh=="ring":
        r=W//2-1; m=6+3*k
        for i in range(m):
            a=i*6.2832/m; x=int(round(cx+r*math.cos(a))); z=int(round(cx+r*math.sin(a))); g.box(x,0,z,x,2+k,z,wall)
        for i in range(0,m,2):
            a=i*6.2832/m; b=(i+1)*6.2832/m
            x=int(round(cx+r*math.cos((a+b)/2))); z=int(round(cx+r*math.sin((a+b)/2))); g.set(x,3+k,z,wall)
        g.set(cx,0,cx,acc)
    elif sh=="rows":
        g.box(1,-2,1,W-2,-1,D-2,"air")
        for x in range(2,W-2,2):
            for z in range(2,D-2,2): g.box(x,-1,z,x,0,z,"terracotta"); g.set(x,1,z,"carved_pumpkin[facing=south]" if False else "terracotta")
        g.set(cx,-1,cx,"chest[facing=south]")
    elif sh=="cave":
        g.box(0,0,0,W-1,hh_:=3+2*k,D-1,wall); g.box(2,0,2,W-3,hh_-2,D-1,"air")
        for y in range(1,hh_-2):
            for x in range(3,W-3,2): g.set(x,y,2,"orange_terracotta" if (x+y)%3==0 else acc)
    elif sh=="mound":
        r=W//2
        for x in range(W):
            for z in range(D):
                d=((x-cx)**2+(z-cx)**2)**.5
                if d<=r+.5:
                    top=int((r-d)*.9)
                    for y in range(0,top+1): g.set(x,y,z,"coarse_dirt" if y<top else "grass_block")
        g.box(cx-1,0,cx-1,cx+1,2,cx+1,"air"); g.box(cx,0,cx+1,cx,1,D-1,"air"); g.set(cx,0,cx,"chest[facing=south]")
    elif sh=="dome":
        r=W//2
        for x in range(W):
            for z in range(D):
                for y in range(0,r+1):
                    d=((x-cx)**2+(z-cx)**2+y*y)**.5
                    if r-1<d<=r+.5: g.set(x,y,z,wall)
        g.box(cx,0,D-1,cx,2,D-1,"air")
    elif sh=="gate":
        for x in (1,2,W-3,W-2): g.box(x,0,cx,x,5+2*k,cx+1,wall)
        g.box(1,6+2*k,cx,W-2,7+2*k,cx+1,acc); g.box(3,0,cx,W-4,5+2*k,cx+1,"air")
        g.box(0,0,0,W-1,0,D-1,"cobblestone")
    elif sh=="walled":
        g.shell(0,0,0,W-1,3+k,D-1,wall); g.box(1,0,1,W-2,2+k,D-2,"air"); g.box(1,0,1,W-2,0,D-2,"dirt_path")
        for (x,z) in((0,0),(W-1,0),(0,D-1),(W-1,D-1)): g.box(x,0,z,x,5+k,z,acc)
        for x in range(2,W-3,4):
            for z in range(2,D-3,4): g.shell(x,1,z,x+2,3,z+2,"oak_planks" if "brick" not in t else "bricks"); g.box(x+1,1,z+1,x+1,2,z+1,"air")
        g.box(cx,1,D-1,cx,3,D-1,"air")
    elif sh=="towers":
        m=min(n,4)
        for i in range(m):
            x0=1+i*((W-4)//max(1,m-1)) if m>1 else cx-1
            g.shell(x0,0,2,x0+2,10+4*k,4,wall); g.box(x0+1,1,3,x0+1,9+4*k,3,"air"); g.set(x0+1,6+2*k,2,"glass_pane")
            for y in range(2,10+4*k,3): g.set(x0+1,y,5,"glass_pane")
        if m>1: g.box(1,8+2*k,3,W-2,8+2*k,3,acc)
    elif sh=="harbor":
        g.box(0,0,0,W-1,0,D-1,"spruce_planks")
        for x in range(0,W,3):
            for z in range(0,D,3): g.box(x,-F,z,x,-1,z,"spruce_log[axis=y]")
        for x in (3,W-4): g.box(x,1,3,x,6,3,"spruce_log[axis=y]"); g.box(x,5,3,x,5,D-2,"spruce_fence")
    elif sh=="bridge":
        D=9+8*k; g.b.clear(); g.box(1,0,0,W-2,0,D-1,wall)
        for z in range(D): g.set(1,1,z,"stone_brick_wall"); g.set(W-2,1,z,"stone_brick_wall")
        for z in range(2,D-2,4): g.box(2,-F,z,W-3,-1,z,wall)
        g.box(0,-F,0,W-1,-1,0,"cobblestone")
    else:
        PAL["_t"]=dict(PAL["Bloom"],w=wall,f=acc,m=acc,c=wall)
        b,W,D=build(cls,"_t",k,len(text))
        return b,W,D,"class:"+cls,t
    return g.b,W,D,sh,t

def loot_json(cls):
    L={"tomb":["gold_ingot","bone","iron_sword","golden_apple","amethyst_shard"],"delve":["flint","bone","coal","raw_copper","lapis_lazuli"],
       "temple":["gold_nugget","candle","book","emerald","paper"],"fortress":["iron_ingot","arrow","iron_axe","bread","shield"],
       "forge":["iron_ingot","coal","iron_pickaxe","redstone","copper_ingot"],"tower":["spyglass","book","paper","ender_pearl","arrow"],
       "hall":["book","paper","bread","emerald","name_tag"],"harbor":["fishing_rod","cod","string","rope" if False else "lead","compass"],
       "garden":["wheat_seeds","apple","carrot","potato","bone_meal"],"bridge":["stick","iron_nugget","bread","coal","string"],
       "ruin":["cobweb","bone","stick","coal","clay_ball"],"landmark":["flint","stick","clay_ball","gold_nugget","amethyst_shard"]}
    it=[i for i in L[cls] if i in gen.IT]
    return {"type":"minecraft:chest","pools":[{"rolls":{"type":"minecraft:uniform","min":2,"max":4},"entries":[{"type":"minecraft:item","name":"minecraft:"+i,"weight":10-j,"functions":[{"function":"minecraft:set_count","count":{"type":"minecraft:uniform","min":1,"max":4}}]} for j,i in enumerate(it)]}]}
SPAWN={"tomb":"minecraft:skeleton","delve":"minecraft:cave_spider","fortress":"minecraft:zombie","ruin":"minecraft:zombie"}

def jig(name,target,pool,orient,final="minecraft:air"):
    return {"id":(8,"minecraft:jigsaw"),"name":(8,name),"target":(8,target),"pool":(8,pool),"joint":(8,"aligned"),"final_state":(8,final),"placement_priority":(3,0),"selection_priority":(3,0)}
def tmpl(blocks,size,palette_extra=None):
    keys=[];ents=[]
    for pos,(spec,be) in blocks.items():
        if spec not in keys: keys.append(spec)
        e={"pos":(9,(3,list(pos))),"state":(3,keys.index(spec))}
        if be: e["nbt"]=(10,be)
        ents.append(e)
    pl=[]
    for k in keys:
        n,pr=gen.block(k); d={"Name":(8,n)}
        if pr: d["Properties"]=(10,pr)
        pl.append(d)
    return nbt({"size":(9,(3,list(size))),"palette":(9,(10,pl)),"blocks":(9,(10,ents)),"entities":(9,(10,[])),"DataVersion":(3,gen.DV)})

def building_nbt(cls,soil,k,custom=None):
    b,W,D=custom if custom else build(cls,soil,k,0)
    top=max(y for _,y,_ in b)+1
    blocks={}
    for (x,y,z),v in b.items():
        v=gen.fixblock(v)
        be=None
        if v.startswith("minecraft:chest"): be={"id":(8,"minecraft:chest"),"LootTable":(8,f"{NS}:lib/loot/{cls}")}
        blocks[(x,y,z)]=(v,be)
    cx=W//2
    if cls in SPAWN and (cx,F,cx) not in blocks:
        blocks[(cx,F,cx)]=("minecraft:spawner",{"id":(8,"minecraft:mob_spawner"),"SpawnData":(10,{"entity":(10,{"id":(8,SPAWN[cls])})})})
    if not any(v[0].startswith("minecraft:chest") for v in blocks.values()) and (cx,F,cx-1) not in blocks:
        blocks[(cx,F,cx-1)]=("minecraft:chest[facing=south]",{"id":(8,"minecraft:chest"),"LootTable":(8,f"{NS}:lib/loot/{cls}")})
    blocks[(cx,F,D)]=("minecraft:jigsaw[orientation=south_up]",jig(f"{NS}:lib_site",f"{NS}:lib_site","minecraft:empty","south_up","minecraft:air"))
    return tmpl(blocks,(max(x for x,_,_ in blocks)+1,max(top,max(y for _,y,_ in blocks)+1),max(z for _,_,z in blocks)+1))

def pages(text):
    out=[];cur=""
    for wd in text.split():
        if len(cur)+len(wd)+1>230: out.append(cur);cur=wd
        else: cur=(cur+" "+wd).strip()
    if cur: out.append(cur)
    return out
def plaque_nbt(name,text,target_pool,npc=None):
    book={"id":(8,"minecraft:written_book"),"count":(3,1),"components":(10,{"minecraft:written_book_content":(10,{
        "title":(10,{"raw":(8,name[:32])}),"author":(8,"Panscriptum"),
        "pages":(9,(10,[{"raw":(8,p)} for p in pages(text)]))})})}
    blocks={(0,0,0):("minecraft:jigsaw[orientation=north_up]",jig(f"{NS}:lib_site",f"{NS}:lib_site",target_pool,"north_up")),
            (0,0,1):("minecraft:lectern[facing=south,has_book=true,powered=false]",{"id":(8,"minecraft:lectern"),"Book":(10,book),"Page":(3,0)})}
    if npc:  # NPC hook: a barrel beside the lectern; its custom name is "lib_npc:<call number>:<count>"
        blocks[(1,0,1)]=("minecraft:barrel[facing=up]",{"id":(8,"minecraft:barrel"),"CustomName":(8,"lib_npc:%s:%d"%npc)})
    return tmpl(blocks,(2 if npc else 1,1,2))

DIMOVR={"Ember":"nether","Hollow":"under","Quiet":"end","Frost":"surf","Bloom":"surf","Storm":"surf","Iron":"surf"}
def structure_json(planet,cls,b,soil,start_pool):
    kind=DIMOVR[soil]; under=cls=="delve" or kind in("under",)
    d={"type":"minecraft:jigsaw","biomes":f"#{NS}:lib/{planet}","step":"underground_structures" if under else "surface_structures",
       "spawn_overrides":{},"terrain_adaptation":"none" if under or kind=="nether" else "beard_thin","start_pool":start_pool,"size":2,
       "max_distance_from_center":24,"use_expansion_hack":False,"liquid_settings":"ignore_waterlogging" if False else "apply_waterlogging"}
    if under: d["start_height"]={"absolute":(-30 if kind=="surf" else 24)}
    elif kind=="nether": d["start_height"]={"absolute":64}
    else: d["start_height"]={"absolute":-1}; d["project_start_to_heightmap"]="WORLD_SURFACE_WG"
    return d

def main():
    L=sqlite3.connect("file:"+SRC+"codex-store/library.sqlite?mode=ro",uri=True)
    C=sqlite3.connect("file:"+SRC+"library-content/content.sqlite?mode=ro",uri=True)
    P={r["planet_id"]:r for r in csv.DictReader(open(SRC+"planets/planets.tsv"),delimiter="\t")}
    rows=C.execute("select id,universe,tier,name from content where form='STRUCTURE' order by id").fetchall()
    if LIM: rows=rows[:LIM]
    by=collections.defaultdict(list)  # (planet,cls,band) -> [(path)]
    npcs=collections.defaultdict(dict)
    for i,u,n in C.execute("select id,universe,name from content where form='NPC'"):
        if n and len(n)>=5: npcs[u].setdefault(n.lower(),i)
    npc_rows=[]
    idx=[]
    seen_b=set(); terra_shapes=collections.Counter()
    for i in range(0,len(rows),900):
        ch=rows[i:i+900]
        txt={r[0]:r[1] for r in L.execute("select id,summary from entry where id in (%s)"%",".join("?"*len(ch)),[c[0] for c in ch])}
        for eid,uni,tier,name in ch:
            planet=re.sub(r"[^a-z0-9_]","",uni.lower()); pl=P[planet]; soil=pl["soil"]
            text=txt[eid]; cls=classify(text); bd=band(tier or 1)
            slug=re.sub(r"[^a-z0-9_]","_",eid.lower().split(".",1)[1].replace(planet+".","")) if False else re.sub(r"[^a-z0-9]+","_",eid.lower()).strip("_")
            path=f"lib/{planet}/{slug}"
            target=f"{NS}:lib/bld/{soil.lower()}/{cls}"
            if planet=="diaithir":
                tb=terra_build(text,cls)
                if tb:
                    bpath=f"lib/diaithir/b/{slug}"; cust=(tb[0],tb[1],tb[2]); terra_shapes[tb[3]]+=1
                    w(f"data/{NS}/structure/{bpath}.nbt",building_nbt(cls,soil,2,cust))
                    w(f"data/{NS}/worldgen/template_pool/{bpath}.json",{"name":f"{NS}:{bpath}","fallback":"minecraft:empty","elements":[{"weight":1,"element":{"element_type":"minecraft:single_pool_element","location":f"{NS}:{bpath}","projection":"rigid","processors":"minecraft:empty"}}]})
                    target=f"{NS}:{bpath}"
            hit=None; wl=re.findall(r"[^\W\d_]+",text.lower()); nd=npcs.get(uni,{})
            for n in (3,2,1):
                for j in range(len(wl)-n+1):
                    nid=nd.get(" ".join(wl[j:j+n]))
                    if nid: hit=(nid,1); break
                if hit: break
            if hit: npc_rows.append((eid,hit[0],hit[1]))
            w(f"data/{NS}/structure/{path}.nbt",plaque_nbt(name or eid,text,target,hit))
            by[(planet,cls,bd)].append(path); idx.append((eid,planet,cls,bd,tier or 1,f"{NS}:{path}"))
            seen_b.add((soil,cls))
    for c in {c for (_,c,_) in by}: w(f"data/{NS}/loot_table/lib/loot/{c}.json",loot_json(c))
    print("terra shapes",dict(terra_shapes))
    # shared buildings
    for soil,cls in seen_b:
        els=[]
        for sz,k in SIZE:
            w(f"data/{NS}/structure/lib/bld/{soil.lower()}/{cls}_{sz}.nbt",building_nbt(cls,soil,k))
            els.append({"weight":(4,2,1)[k-1],"element":{"element_type":"minecraft:single_pool_element","location":f"{NS}:lib/bld/{soil.lower()}/{cls}_{sz}","projection":"rigid","processors":"minecraft:empty"}})
        w(f"data/{NS}/worldgen/template_pool/lib/bld/{soil.lower()}/{cls}.json",{"name":f"{NS}:lib/bld/{soil.lower()}/{cls}","fallback":"minecraft:empty","elements":els})
    # pools, structures, sets, tags
    sets=collections.defaultdict(list); tags=collections.defaultdict(list); planets_used=set()
    for (planet,cls,bd),paths in sorted(by.items()):
        soil=P[planet]["soil"]; opens=int(P[planet]["opens_age"]); n=len(paths)
        sid=f"lib/{planet}/{cls}_{bd}"
        w(f"data/{NS}/worldgen/template_pool/lib/{planet}/{cls}/{bd}.json",{"name":f"{NS}:lib/{planet}/{cls}/{bd}","fallback":"minecraft:empty",
          "elements":[{"weight":1,"element":{"element_type":"minecraft:single_pool_element","location":f"{NS}:{p}","projection":"rigid","processors":"minecraft:empty"}} for p in paths]})
        w(f"data/{NS}/worldgen/structure/{sid}.json",structure_json(planet,cls,bd,soil,f"{NS}:lib/{planet}/{cls}/{bd}"))
        sets[planet].append({"structure":f"{NS}:{sid}","weight":n}); planets_used.add(planet)
        tags[min(8,opens-1+BANDS[bd][0])].append(f"{NS}:{sid}")
    for planet in planets_used:
        n=sum(s["weight"] for s in sets[planet]); sp=32 if n<60 else 24 if n<400 else 16
        salt=int(hashlib.md5(("lib"+planet).encode()).hexdigest()[:7],16)
        w(f"data/{NS}/worldgen/structure_set/lib/{planet}.json",{"structures":sets[planet],"placement":{"type":"minecraft:random_spread","spacing":sp,"separation":sp//3,"salt":salt}})
        vals=["#minecraft:is_overworld"] if planet=="diaithir" else [{"id":f"#diaithir_planets:{planet}","required":False}]
        w(f"data/{NS}/tags/worldgen/biome/lib/{planet}.json",{"values":vals})
    for a,l in tags.items(): w(f"data/{NS}/tags/worldgen/structure/lib_age_{a}.json",{"values":l})
    os.makedirs(OUT+f"/data/{NS}",exist_ok=True)
    with open(OUT+f"/data/{NS}/library_sites.tsv","w") as f:
        f.write("entry_id\tplanet\tclass\tband\ttier\ttemplate\n")
        for r in idx: f.write("\t".join(map(str,r))+"\n")
    with open(OUT+f"/data/{NS}/library_sites_npc.tsv","w") as f:
        f.write("site_entry_id\tnpc_call_number\tcount\n")
        for r in npc_rows: f.write("\t".join(map(str,r))+"\n")
    print(len(npc_rows),"sites with an NPC named in their text")
    print(len(idx),"entries",len(by),"start pools",len(planets_used),"planets",collections.Counter(c for (_,c,_) in by))
if __name__=="__main__": main()
