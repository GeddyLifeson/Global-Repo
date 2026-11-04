#!/usr/bin/env python3 -I
# S6950
"""Convention tags for building, tree, furniture and rail blocks by name suffix (plans/INTEGRATION.md section 1).

usage: gen_tags_extra.py PROFILE_DIR DATAPACK_DIR [JAR_PREFIX ...]
Only jars whose name starts with a given prefix (default: diaithir-furniture, diaithir-trees, diaithir-carts, diaithir-buildcraft, diaithir-ctm).
Writes vanilla/c: tags (minecraft:logs/planks/leaves/saplings/slabs/stairs/walls/fences/rails, c:glass_blocks, c:glass_panes, c:furniture/<kind>),
every entry required=false, merging with any tag file already there."""
import glob, json, os, re, sys

# suffix -> (tag namespace:path list) ; applies to blocks (B) and items (I)
SUFFIX = {"log": ["minecraft:logs"], "wood": ["minecraft:logs"], "planks": ["minecraft:planks"], "leaves": ["minecraft:leaves"], "sapling": ["minecraft:saplings"],
          "slab": ["minecraft:slabs"], "stairs": ["minecraft:stairs"], "wall": ["minecraft:walls"], "fence": ["minecraft:fences"], "pane": ["c:glass_panes"],
          "rail": ["minecraft:rails"], "glass": ["c:glass_blocks"], "lamp": ["c:lamps"], "paving": ["c:paving"], "roof": ["c:roofs"], "shutter": ["c:shutters"]}
FURN = ("table", "chair", "stool", "couch", "chaise", "bookshelf", "cabinet", "counter", "desk", "drawer", "sideboard", "wardrobe")


def add(tags, kind, tag, i):
    tags.setdefault((kind, tag), set()).add(i)


def main(prof, out, *prefixes):
    prefixes = prefixes or ("diaithir-furniture", "diaithir-trees", "diaithir-carts", "diaithir-buildcraft", "diaithir-ctm")
    tags = {}
    for f in sorted(glob.glob(f"{prof}/*.json")):
        d = json.load(open(f))
        if not d["jar"].startswith(prefixes): continue
        for kind, ids in (("block", d["blocks"]), ("item", d["items"] + d["blocks"])):
            for i in ids:
                last = i.split(":", 1)[1].split("_")[-1]
                for t in SUFFIX.get(last, []): add(tags, kind, t, i)
                if last in FURN: add(tags, kind, f"c:furniture/{last}", i); add(tags, kind, "c:furniture", i)
    n = 0
    for (kind, tag), ids in sorted(tags.items()):
        ns, path = tag.split(":")
        p = os.path.join(out, "data", ns, "tags", kind, path + ".json"); os.makedirs(os.path.dirname(p), exist_ok=True)
        cur = json.load(open(p))["values"] if os.path.exists(p) else []
        have = {(v["id"] if isinstance(v, dict) else v) for v in cur}
        vals = cur + [{"id": i, "required": False} for i in sorted(ids) if i not in have]
        json.dump({"replace": False, "values": vals}, open(p, "w"), indent=1); n += len(ids)
    print(len(tags), "tag files,", n, "entries")


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(*sys.argv[1:])
