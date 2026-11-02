import sys,os,re,json,glob,subprocess
sys.path.insert(0,"/home/user/work/pix"); sys.path.insert(0,"/home/user/diaithirrpg/tools/art/blender")
from matlib import resolve,pick,token
from materials import METAL,GEM,RAW,FICT
import bulk_ores
bulk_ores.FACTORIO={}
OV={"iron":(156,84,58),"tin":(104,86,70),"lead":(150,156,172),"zinc":(166,124,72),"aluminum":(178,112,78),"aluminium":(178,112,78),"uranium":(214,200,56),"titanium":(124,66,56),"tungsten":(104,90,78),"nickel":(122,172,122),"cobalt":(150,140,150),"manganese":(84,80,86),"chromium":(96,98,104),"osmium":(130,150,176),"platinum":(206,210,214),"silver":(214,216,220),"iridium":(222,224,230),"antimony":(176,180,188)}
B="/home/user/diaithirrpg/tools/art/blender/baked/ores/assets/"
ores=[]
for f in sorted(glob.glob(B+"*/textures/block/*_heap.png")):
    ns=f.split("/assets/")[1].split("/")[0]; path=os.path.basename(f)[:-9]
    if path.endswith("_glow"): continue
    name=path.split("/")[-1]; base=("deepslate" if "deepslate" in name else "netherrack" if re.search(r"nether|netherrack|crimson|warped|blackstone",name) and "quartz" not in name or name.startswith("nether_") else "end_stone" if re.search(r"^end_|endstone|end_stone",name) else "stone")
    tok=re.sub(r"(^|_)(deepslate|nether|end|endstone|stone|netherrack|ore|poor|dense|small|large)(?=_|$)","_",name); tok=re.sub(r"_+","_",tok).strip("_")
    r=resolve(tok,"raw"); rgb=None
    if r:
        src,k,fam,c,cut,note=r
        key=k if src=="real" else fam
        if src=="real" and fam=="metal": rgb=OV.get(k) or METAL[k][0]
        elif src=="real": rgb=c
        else: rgb=c
    if rgb is None:
        im=__import__("PIL.Image",fromlist=["x"]).open(f).convert("RGB").resize((1,1)); rgb=im.getpixel((0,0))
    ores.append({"ns":ns,"path":path,"base":base,"ore_rgb":list(rgb)})
print(len(ores))
n=4
for i in range(n): json.dump(ores[i::n],open(f"/home/user/work/pix/ores_slice{i}.json","w"))
json.dump(ores,open("/home/user/work/pix/ores_all.json","w"))
