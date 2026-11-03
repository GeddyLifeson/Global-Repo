#!/usr/bin/env python3 -I
# S0316
"""Recipe fixes and cross-mod smelting for the compat datapack (plans/INTEGRATION.md section 2).

usage: gen_recipes.py PROFILE_DIR MATRIX_CSV DATAPACK_DIR
1. A recipe that names a namespace absent from the whole pack is re-issued at its own path with a neoforge:mod_loaded condition for each
   missing namespace, so it is skipped instead of dangling. 'Absent' = not a namespace of any profiled jar, not a mod id in the matrix.
2. Every dust or raw item with no smelting/blasting recipe in its own jar gets one to the pack's canonical ingot for that metal
   (vanilla first, else the first mod id alphabetically), so every mod's dust becomes the one shared ingot."""
import csv, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_tags import classify

CORE = {"minecraft", "c", "neoforge", "forge", "fabric", "kubejs", "diaithircompat"}
VANILLA = {"copper", "iron", "gold", "netherite"}


def main(prof, matrix, out):
    profs = [json.load(open(f)) for f in glob.glob(f"{prof}/*.json")]
    known = set(CORE)
    for p in profs: known |= set(p["namespaces"]) | set(p["mod_ids"])
    for r in csv.DictReader(open(matrix)): known |= set(r["mod_ids"].split())
    fixed = 0
    for p in profs:
        for path, refs in p["recipe_refs"].items():
            miss = sorted(set(refs) - known)
            if not miss or path not in p["recipe_json"]: continue
            try: j = json.loads(p["recipe_json"][path])
            except Exception: continue
            have = json.dumps(j.get("neoforge:conditions", []))
            miss = [m for m in miss if f'"{m}"' not in have]
            if not miss: continue
            cond = [{"type": "neoforge:mod_loaded", "modid": m} for m in miss]
            j["neoforge:conditions"] = (j.get("neoforge:conditions") or []) + cond
            o = os.path.join(out, path); os.makedirs(os.path.dirname(o), exist_ok=True)
            json.dump(j, open(o, "w"), indent=1); fixed += 1
    ingots = {}
    for p in profs:
        for i in p["items"]:
            c = classify(i.split(":", 1)[1])
            if c and c[0] == "ingots": ingots.setdefault(c[1], set()).add(i)
    made = 0
    for p in profs:
        smelted = " ".join(t for t in p["recipe_json"].values() if '"smelting"' in t or '"blasting"' in t)
        for i in p["items"]:
            c = classify(i.split(":", 1)[1])
            if not c or c[0] not in ("dusts", "raw_materials") or c[1] not in ingots or i in smelted: continue
            res = f"minecraft:{c[1]}_ingot" if c[1] in VANILLA else sorted(ingots[c[1]])[0]
            ns, name = i.split(":", 1)
            for typ, t in (("smelting", 200), ("blasting", 100)):
                j = {"neoforge:conditions": [{"type": "neoforge:mod_loaded", "modid": ns}], "type": f"minecraft:{typ}", "category": "misc",
                     "ingredient": i, "result": {"id": res}, "experience": 0.7, "cookingtime": t}
                o = os.path.join(out, "data/diaithircompat/recipe", f"xmod_{typ}_{ns}_{name}.json"); os.makedirs(os.path.dirname(o), exist_ok=True)
                json.dump(j, open(o, "w"), indent=1)
            made += 1
    print(f"{fixed} recipes given load conditions; {made} dust/raw smelting+blasting pairs")


if __name__ == "__main__":
    if len(sys.argv) != 4: sys.exit(__doc__)
    main(*sys.argv[1:])
