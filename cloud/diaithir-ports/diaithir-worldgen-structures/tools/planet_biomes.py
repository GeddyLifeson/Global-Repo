#!/usr/bin/env python3
# S6848 Planet biome map: settlement biome_entry (entry id) -> diaithir_planets biome id, per planet. Writes planet_biome_map.json.
"""Usage: planet_biomes.py REF   (REF = git ref of diaithir-ports holding diaithir-overworld-biomes, e.g. pr145c).
specs/<planet>.json lists the land biomes in order, each with the Library entry it is named for; the planet stem's multi_noise
biome list holds the same biomes in the same order, so index i of one is index i of the other."""
import json,subprocess,sys,os
REF=sys.argv[1]; G=["git","-C",os.path.dirname(os.path.abspath(__file__))+"/../.."]
base="diaithir-overworld-biomes/src/main/resources/data/diaithir_planets/planet_stems/"
def show(p): return subprocess.run(G+["show",f"{REF}:{p}"],capture_output=True,text=True).stdout
names=[l.split("/")[-1][:-5] for l in subprocess.run(G+["ls-tree","--name-only",REF,base],capture_output=True,text=True).stdout.split()]
out={}
for pl in names:
    try: st=json.loads(show(base+pl+".json")); spec=json.load(open(f"/mnt/project-files/planets/specs/{pl}.json"))
    except Exception as e: print("skip",pl,e); continue
    bl=[b["biome"] for b in st["generator"]["biome_source"]["biomes"]]
    out[pl]={b["entry"]:bl[i] for i,b in enumerate(spec["biomes"]) if i<len(bl)}
json.dump(out,open(os.path.dirname(os.path.abspath(__file__))+"/planet_biome_map.json","w"),indent=0)
print(len(out),"planets",sum(len(v) for v in out.values()),"land biomes")
