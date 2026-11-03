#!/usr/bin/env python3
# S6884 # Convention (c:) tags for the worldgen-structures module. Run from the module folder: python3 -I tools/c_tags.py
import os,json,collections,re
R="src/main/resources/data"; NS="diaithir_worldgen"
def w(p,v):
    p=f"{R}/{p}"; os.makedirs(os.path.dirname(p),exist_ok=True); json.dump(v,open(p,"w"),indent=1)
cls=collections.defaultdict(list); sets=[]
base=f"{R}/{NS}/worldgen/structure"
for planet in sorted(os.listdir(base+"/lib")):
    for f in sorted(os.listdir(f"{base}/lib/{planet}")):
        m=re.match(r"([a-z_]+?)_\d",f) or re.match(r"(_settle)",f)
        c=(m.group(1) if m else "other").strip("_")
        cls[c].append(f"{NS}:lib/{planet}/{f[:-5]}")
for c,l in cls.items(): w(f"c/tags/worldgen/structure/{NS}/{c}.json",{"values":l})
w("c/tags/worldgen/structure/mazes.json",{"values":[f"{NS}:rc/maze_{t}" for t in ("stone","sand","nether","ice","deep")]})
w("c/tags/worldgen/structure/villages.json",{"values":[f"#c:{NS}/settlement"]})
w("c/tags/worldgen/structure/ruins.json",{"values":[f"#c:{NS}/ruin",f"#c:{NS}/tomb"]})
w("c/tags/worldgen/structure/dungeons.json",{"values":[f"#c:{NS}/delve","#c:mazes"]})
w("c/tags/worldgen/structure/diaithir_worldgen.json",{"values":[f"#{NS}:all"]})
w("c/tags/worldgen/biome/has_diaithir_worldgen_structures.json",{"values":[{"id":f"#{NS}:lib/{p}","required":False} for p in sorted(os.listdir(f"{R}/{NS}/tags/worldgen/biome/lib")) if p.endswith(".json")]+[{"id":f"#{NS}:rc/{t}","required":False} for t in ("stone","sand","nether","ice","deep")]})
print({c:len(l) for c,l in cls.items()})
