import json,os,re,sys,glob
sys.path.insert(0,"/home/user/work/gaps")
from build_list import jar,kjs,has,audit
O="/home/user/diaithirrpg/tools/art/blender/baked/gaps/assets/"
def w(path,obj):
    os.makedirs(os.path.dirname(path),exist_ok=True);json.dump(obj,open(path,"w"),indent=1)
nd=0
for i,r in audit:
    if "no item definition" not in r: continue
    ns,p=i.split(":",1)
    model=f"{ns}:item/{p}"
    if not has(f"assets/{ns}/models/item/{p}.json"):
        if ns=="diaithir" and p.endswith("_ore"):
            m={"parent":"minecraft:block/cube_all","textures":{"all":f"{ns}:block/{p}"}}
        else:
            tex=f"{ns}:item/{p}"
            if has(f"assets/{ns}/textures/block/{p}.png") and not has(f"assets/{ns}/textures/item/{p}.png"): tex=f"{ns}:block/{p}"
            m={"parent":"minecraft:item/generated","textures":{"layer0":tex}}
        w(f"{O}{ns}/models/item/{p}.json",m)
    w(f"{O}{ns}/items/{p}.json",{"model":{"type":"minecraft:model","model":model}}); nd+=1
# extra textures need no model (mod models exist). lang:
lang={}
for n,z in jar.items():
    if re.fullmatch(r"assets/[^/]+/lang/en_us\.json",n):
        try: lang.setdefault(n.split("/")[1],set()).update(json.loads(z.read(n).decode("utf-8-sig")).keys())
        except Exception: pass
for k in glob.glob("/home/user/work/packsrc/kubejs/assets/*/lang/en_us.json"):
    lang.setdefault(k.split("/")[-3],set()).update(json.load(open(k)).keys())
def title(p): return " ".join(x.capitalize() for x in re.split(r"[_/.\-]+",p) if x)
new={}
for i,r in audit:
    if "no lang name" not in r: continue
    ns,p=i.split(":",1);key=p.replace("/",".")
    have=lang.get(ns,set())
    if f"item.{ns}.{key}" in have or f"block.{ns}.{key}" in have: continue
    new.setdefault(ns,{})[f"item.{ns}.{key}"]=title(p)
    new[ns][f"block.{ns}.{key}"]=title(p)
for ns,d in new.items(): w(f"{O}{ns}/lang/en_us.json",d)
print(nd,"definitions;",sum(len(d)//2 for d in new.values()),"names in",len(new),"namespaces")
