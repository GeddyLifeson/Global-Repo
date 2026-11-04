#!/usr/bin/env python3
# S6953
"""S6953 Moves a module's crafting-grid recipes (minecraft:crafting_shaped / crafting_shapeless) onto the Age stations.
Each recipe becomes data/<ns>/diaithir_stations/station_recipe/<name>.json (stage "assembly") and the grid file is deleted.
Station by Age of the result: I-II hearth bench, III-IV wright bench, V steam forge, VI-VII assembler, VIII+ fabricator.
Age comes from the recipe's "_age" (roman) or the module's age_gates.json entry for the result item, else III.
Usage: recipes_to_stations.py <module dir>...     Run again after a generator rewrites the grid recipes. Idempotent."""
import json, os, sys, collections

ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "RODOS": 8, "IX": 9, "FUTURE": 9}
STATION = {1: "station.hearth_bench", 2: "station.hearth_bench", 3: "station.wright_bench", 4: "station.wright_bench", 5: "station.steam_forge",
           6: "machine.assembler", 7: "machine.assembler", 8: "station.fabricator", 9: "station.fabricator"}
TIME_S = {1: 4, 2: 6, 3: 8, 4: 10, 5: 14, 6: 18, 7: 22, 8: 26, 9: 30}


def ing(s):
    return {"tag": s[1:]} if s.startswith("#") else {"item": s}


def convert(mod):
    gates = {}
    p = os.path.join(mod, "age_gates.json")
    if os.path.exists(p):
        gates = json.load(open(p)).get("items", {})
    n = 0
    for root, _, files in os.walk(os.path.join(mod, "src/main/resources/data")):
        if os.path.basename(root) != "recipe":
            continue
        ns = root.split(os.sep)[-2]
        for f in sorted(files):
            path = os.path.join(root, f)
            r = json.load(open(path))
            t = r.get("type")
            if t == "minecraft:crafting_shaped":
                keys = collections.Counter(c for row in r["pattern"] for c in row if c != " ")
                counts = collections.Counter({r["key"][k] if isinstance(r["key"][k], str) else r["key"][k].get("item") or "#" + r["key"][k]["tag"]: v for k, v in keys.items()})
                counts = collections.Counter()
                for k, v in keys.items():
                    e = r["key"][k]
                    counts[e if isinstance(e, str) else (e.get("item") or "#" + e["tag"])] += v
            elif t == "minecraft:crafting_shapeless":
                counts = collections.Counter()
                for e in r["ingredients"]:
                    counts[e if isinstance(e, str) else (e.get("item") or "#" + e["tag"])] += 1
            else:
                continue
            res = r["result"]
            age = ROMAN.get(str(r.get("_age") or gates.get(res["id"], "III")).upper(), 3)
            out = {"station": STATION[age], "stage": "assembly", "time_s": TIME_S[age],
                   "ingredients": [dict(ing(k), count=v) for k, v in counts.items()], "result": res}
            d = os.path.join(root, "..", "diaithir_stations", "station_recipe")
            os.makedirs(d, exist_ok=True)
            json.dump(out, open(os.path.join(d, f), "w"), indent=1)
            os.remove(path)
            n += 1
    print(mod, n, "recipes moved")


for m in sys.argv[1:]:
    convert(m)
