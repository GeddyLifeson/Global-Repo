#!/usr/bin/env python3
"""Make Create mixing recipes (heated basin) from diaithirbrewing recipe JSON.

usage: gen_create_bridge.py <recipe dir> <out data dir>
Reads data/<ns>/diaithirbrewing/*.json files under <recipe dir> and writes
<out>/create/recipe/mixing/brew_<ns>_<name>.json, gated on diaithir_create being loaded.
The basin batch is one bucket of base, so the yield is the recipe's servings.
"""
import json, sys, pathlib

BUCKET = 81000  # fluid units in the port: 20250 per 250 mb
BASES = {
    "minecraft:water_bucket": {"type": "fluid_stack", "amount": BUCKET, "fluid": "minecraft:water"},
    "minecraft:milk_bucket": {"type": "fluid_tag", "amount": BUCKET, "fluid_tag": "#c:milk"},
}

def convert(ns, name, r):
    base = BASES.get(r.get("base"))
    if base is None:
        return None, f"base {r.get('base')} has no Create fluid"
    items = []
    for item, n in r["ingredients"].items():
        items += [item] * n
    if len(items) > 9:
        return None, f"{len(items)} ingredient items, Create allows 9"
    return {
        "neoforge:conditions": [{"type": "neoforge:mod_loaded", "modid": "diaithir_create"}],
        "type": "create:mixing",
        "heat_requirement": "heated",
        "processing_time": max(20, r["ticks"]),
        "ingredients": items,
        "fluid_ingredients": [base],
        "results": [{"id": r["drink"], "count": r.get("servings", 1)}],
    }, None

def main(src, out):
    src, out = pathlib.Path(src), pathlib.Path(out)
    made = skipped = 0
    for f in sorted(src.glob("data/*/diaithirbrewing/*.json")):
        ns = f.parts[f.parts.index("data") + 1]
        rec, why = convert(ns, f.stem, json.loads(f.read_text()))
        if rec is None:
            print(f"skip {ns}:{f.stem}: {why}")
            skipped += 1
            continue
        dest = out / "create" / "recipe" / "mixing" / f"brew_{ns}_{f.stem}.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(rec, indent=2) + "\n")
        made += 1
    print(f"{made} written, {skipped} skipped")

if __name__ == "__main__":
    main(*sys.argv[1:3])
