import sys,os,io,glob,zipfile,collections
sys.path.insert(0,"/home/user/work/pix")
from classify import listing
from pixel_icons import render
import item_specs as S
from build_list import jar,kjs,colour
from PIL import Image
BAKED="/home/user/diaithirrpg/tools/art/blender/baked/"
O=BAKED+"pixel/assets/"
L=listing(); stats=collections.Counter(); pairs=[]
for (ns,rel),kind in sorted(L.items()):
    p=f"assets/{ns}/textures/item/{rel}.png"; png=None
    if p in jar: png=jar[p].read(p)
    elif p in kjs:
        f=f"/home/user/work/packsrc/kubejs/{p}"; png=open(f,"rb").read() if os.path.exists(f) else None
    rgb=None
    if png:
        try:
            m,s2,v=S.colours(png); rgb=v if kind in("gem","shard") and S.sat(v)>0.3 else m; stats["src"]+=1
        except Exception: rgb=None
    if rgb is None:
        rgb=colour(rel); stats["name"]+=1
        if rgb==(140,138,132):
            import re,hashlib,colorsys
            tok=re.sub(r"(dusts?|tiny|small|clumps?|gravels?|fragments?|crystals?|shards?|nuggets?|ingots?|raw|gems?|ores?|storage_blocks|dirty|crushed|oritech|neovitae|theurgy|alchemical|sulfurs|[_.])","",rel.split(".")[-1]) or rel
            h=int(hashlib.md5(tok.encode()).hexdigest()[:6],16)
            r_=colorsys.hsv_to_rgb((h%360)/360,0.45+(h>>9)%40/100,0.6+(h>>5)%30/100); rgb=tuple(int(c*255) for c in r_)
    im=render(kind,f"{ns}:{rel}",tuple(rgb))
    f=f"{O}{ns}/textures/item/{rel}.png"; os.makedirs(os.path.dirname(f),exist_ok=True); im.save(f); pairs.append((ns,rel,kind))
print(len(pairs),stats)
import json;json.dump(pairs,open("pairs.json","w"))
