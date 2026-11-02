import sys,os,re,json,collections,hashlib,colorsys
sys.path.insert(0,"/home/user/work/pix")
from materials import METAL,GEM,RAW,FICT
from pixel_icons import render
import item_specs as S
from build_list import jar,kjs,colour
BAKED="/home/user/diaithirrpg/tools/art/blender/baked/"; O=BAKED+"pixel/assets/"
KW=r"(dusts?|tiny|small|clumps?|gravels?|fragments?|crystals?|shards?|nuggets?|ingots?|raw|gems?|ores?|storage_blocks|dirty|crushed|double|hot|oritech|neovitae|theurgy|alchemical|sulfurs|materials|powder|ground|chunks?|rough|speck|pieces?|piece)"
JUNK=r"meat|pizza|pasta|bucket|processor|mold|saw$|tempura|cheese|cinnamon|venison|protein|pork|fillet|_tea$|disc_|marker|template|chip|packer|overlay|configurator|prismoss|prismarite|mesh|warp_stone|sprout|grinding_ball|^w_t|lemon|roast|feather|pri_ard|iron_bar|shell|beaver|brick|^cast|fire_clay|^sand|end_stone|blackstone|packed_ice|blue_ice|water_|lava|activation|obelisk|spiritus|essence|catalyst|base_|hollow|dimensional|confusing|enticing|spirit_attuned|glittery|attuned|pixie|artifact|logic|research|infusion|weather|transformation|hybrid|construction|player_|xp|time|sky$|scales_|spell|stygian_steel_|trim|aerial|fragile|mundabitur|niotic|nitro|ghost|dull|dormant|dread|fiery|growth|resin|saw|^ized_|^lized_|mono_line|primitive|reprocessed|irradiated_result|single"
def token(rel):
    t=rel.split("/")[-1].split(".")[-1]; t=re.sub(KW,"_",t); return re.sub(r"_+","_",t).strip("_")
def resolve(tok,kind):
    words=tok.split("_"); keys=[]
    for n in range(len(words),0,-1):
        for i in range(0,len(words)-n+1): keys.append("_".join(words[i:i+n]))
    for k in keys:
        if k in FICT:
            base,c=FICT[k]; return ("analogue",k,base,c,None,f"fictional {k} ~ {base}")
    for k in keys:
        if k in GEM: c,cut,note=GEM[k]; return ("real",k,"gem",c,cut,note)
        if k in METAL: return ("real",k,"metal",None,None,METAL[k][2])
    return None
def pick(kind,tok):
    r=resolve(tok,kind)
    if not r: return None
    src,k,fam,c,cut,note=r
    if src=="analogue":
        if fam=="gem": rgb=c; fam2="gem"; cut2="oval"
        else:
            m=METAL[fam]; rgb=c; fam2="metal"; cut2=None
        mat=("analogue",fam2)
    else: fam2=fam; rgb=c; cut2=cut; mat=("real",fam2)
    if fam2=="metal":
        key=k if src=="real" else fam
        pol,pow_,_=METAL[key] if key in METAL else (rgb,rgb,"")
        if src=="analogue": 
            pol=pow_=c; 
        col=pow_ if kind=="dust" else pol
        if src=="analogue" and kind=="dust": col=tuple(int(x*.82) for x in c)
        if kind=="raw":
            host,vein,_=RAW.get(key,((112,106,100),pol,""))
            if src=="analogue": host,vein=(112,106,100),c
            return mat+(col,(host,vein),note)
        if kind in("gem","shard"): return mat+(col,"brilliant" if kind=="gem" else None,note)
        return mat+(col,None,note)
    # gem family
    col=rgb
    if kind=="dust": col=tuple(min(255,int(x*.9+20)) for x in rgb)
    if kind in("nugget","ingot"): col=rgb
    if kind=="raw": return mat+(col,((112,108,102),col),note)
    if kind in("gem","shard"): return mat+(col,cut2,note)
    return mat+(col,None,note)
pairs=json.load(open("pairs.json")); table=collections.OrderedDict(); stats=collections.Counter(); params={}
import shutil
for (ns,rel,kind) in pairs:
    tok=token(rel); f=f"{O}{ns}/textures/item/{rel}.png"
    if re.search(JUNK,tok) or re.search(JUNK,rel.split("/")[-1].split(".")[-1]):
        if os.path.exists(f): os.remove(f)
        stats["junk"]+=1; continue
    p=pick(kind,tok)
    if p:
        srcname,fam,rgb,cut,note=p; stats[srcname]+=1
    else:
        pn=f"assets/{ns}/textures/item/{rel}.png"; png=None
        if pn in jar: png=jar[pn].read(pn)
        elif pn in kjs and os.path.exists(f"/home/user/work/packsrc/kubejs/{pn}"): png=open(f"/home/user/work/packsrc/kubejs/{pn}","rb").read()
        rgb=None
        if png:
            try: m,s2,v=S.colours(png); rgb=v if kind in("gem","shard") and S.sat(v)>0.3 else m
            except Exception: pass
        if rgb is None:
            rgb=colour(rel)
            if rgb==(140,138,132):
                h=int(hashlib.md5(tok.encode()).hexdigest()[:6],16); rgb=tuple(int(c*255) for c in colorsys.hsv_to_rgb((h%360)/360,.45+(h>>9)%40/100,.6+(h>>5)%30/100))
        srcname,fam,cut,note="sprite","?",None,"no real counterpart: mod sprite colour"; stats["sprite"]+=1
        if kind=="raw": cut=((112,106,100),rgb)
    params[f"{ns}:{rel}"]={"kind":kind,"rgb":list(rgb),"cut":cut}
    im=render(kind,f"{ns}:{rel}",tuple(rgb),cut)
    os.makedirs(os.path.dirname(f),exist_ok=True); im.save(f)
    table.setdefault(tok,{"rgb":list(rgb),"source":srcname,"note":note,"kinds":set(),"n":0}); table[tok]["kinds"].add(kind); table[tok]["n"]+=1
print(stats)
json.dump({k:{**v,"kinds":sorted(v["kinds"])} for k,v in table.items()},open("table.json","w"),indent=0)
print(len(table))

json.dump(params,open('params.json','w'))
