import json,sys,re
sys.path.insert(0,"/home/user/diaithirrpg/tools/art/blender"); sys.path.insert(0,"/home/user/work/gaps")
import item_specs as S
from build_list import colour,png,has,jar
L=json.load(open("list.json"))
rows=[];specs=[];index=[];mats={}
def add(ns,item,ref):
    rows.append(f"gap\t{ns}\t{item}\tsprite\t{ref}")
    c=colour(item)
    al=item
    if re.search(r"clump|gravel|chunk|shard",item): al="raw_"+item
    elif "egg" in item: al="egg"
    elif re.search(r"turret|engine|aim",item): al="gear"
    elif re.search(r"module|controller|device|crafter|screen|builder|upgrade",item): al="circuit_"+item
    try: kind,spec=S.spec_for(ns,al,png(c),mats); spec["name"]=ns+"__"+item.replace("/","__")
    except Exception as e: print("skip",ns,item,e); return
    specs.append(spec); index.append((ns,item,kind,spec["name"]))
for ns,p in L["items"]:
    if has(f"assets/{ns}/models/item/{p}.json"): continue
    if has(f"assets/{ns}/textures/item/{p}.png"): continue
    if p.endswith("_ore") and ns=="diaithir": continue   # block items: use the block texture
    add(ns,p,f"{ns}:item/{p}")
for ref in L["extra"]:
    ns,p=ref.split(":");p=p.split("/",1)[1]
    add(ns,p,ref)
n=8
for i in range(n):
    sl=specs[i::n]; used={q["mat"] for s in sl for q in s["parts"]}
    for s in sl: s.pop("materials",None)
    if sl: sl[0]["materials"]={k:v for k,v in {**S.EXTRA,**mats}.items() if k in used}
    json.dump(sl,open(f"ispecs/slice_{i:02d}.json","w")) if __import__("os").makedirs("ispecs",exist_ok=True) is None else 0
open("ispecs/index.tsv","w").write("namespace\titem\tarchetype\tspec\n"+"".join("\t".join(r)+"\n" for r in index))
open("items.tsv","w").write("source\tnamespace\titem\tkind\ttextures\n"+"\n".join(rows)+"\n")
import collections;print(len(specs),collections.Counter(r[2] for r in index).most_common(12))
