#!/usr/bin/env python3 -I
# S0313
"""Generate c: convention tag unions from jar profiles (plans/INTEGRATION.md section 1).

usage: gen_tags.py PROFILE_DIR DATAPACK_DIR
Item/block ids whose names follow a material pattern (iron_ingot, raw_tin, plate_steel, gear_bronze, silver_ore ...) are added
to data/c/tags/{item,block}/<group>/<material>.json with required=false, so a missing mod never breaks the tag."""
import glob, json, os, re, sys

METALS = set("""copper iron gold silver tin lead zinc nickel aluminum aluminium uranium osmium platinum titanium tungsten steel bronze brass invar
electrum constantan cobalt manganese chromium lithium magnesium iridium palladium cadmium bismuth antimony mercury netherite refined_iron
refined_obsidian refined_glowstone enderium lumium signalum plutonium thorium boron sulfur sulphur rose_gold steeleaf knightmetal fiery
ironwood stainless_steel pewter rubber silicon sapphire ruby amethyst topaz peridot quartz certus_quartz fluix emerald diamond lapis
coal charcoal obsidian glowstone ender_pearl redstone""".split())
PRE = r"(?:deepslate_|nether_|end_|stone_)?"


def classify(name):
    """(group, material) or None for a registry path."""
    for pat, grp in ((r"(.+)_ingot$", "ingots"), (r"ingot_(.+)$", "ingots"), (r"(.+)_nugget$", "nuggets"), (r"nugget_(.+)$", "nuggets"),
                     (r"raw_(.+)$", "raw_materials"), (r"(.+)_raw$", "raw_materials"), (r"(.+)_dust$", "dusts"), (r"dust_(.+)$", "dusts"),
                     (r"(.+)_plate$", "plates"), (r"plate_(.+)$", "plates"), (r"(.+)_gear$", "gears"), (r"gear_(.+)$", "gears"),
                     (r"(.+)_rod$", "rods"), (r"rod_(.+)$", "rods"), (r"(.+)_wire$", "wires"), (r"wire_(.+)$", "wires"),
                     (r"(.+)_gem$", "gems"), (r"gem_(.+)$", "gems"), (r"(.+)_crystal$", "gems")):
        m = re.match(pat, name)
        if m and m[1] in METALS: return grp, m[1]
    m = re.match(PRE + r"(.+)_ore$", name) or re.match(r"ore_(.+)$", name)
    if m and m[1] in METALS: return "ores", m[1]
    m = re.match(r"(.+)_block$", name) or re.match(r"block_(.+)$", name)
    if m and m[1] in METALS: return "storage_blocks", m[1]
    return None


def main(prof, out):
    tags = {}
    for f in sorted(glob.glob(f"{prof}/*.json")):
        d = json.load(open(f))
        for kind, ids in (("item", d["items"]), ("block", d["blocks"])):
            for i in ids:
                ns, name = i.split(":", 1)
                if ns == "minecraft" or "/" in name: continue
                c = classify(name)
                if not c: continue
                grp, mat = c
                if kind == "block" and grp not in ("ores", "storage_blocks"): continue
                tags.setdefault((kind, grp, mat), set()).add(i)
    n = 0
    for (kind, grp, mat), ids in sorted(tags.items()):
        p = os.path.join(out, "data/c/tags", kind, grp, mat + ".json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump({"replace": False, "values": [{"id": i, "required": False} for i in sorted(ids)]}, open(p, "w"), indent=1)
        n += len(ids)
    print(len(tags), "tag files,", n, "entries")


if __name__ == "__main__":
    if len(sys.argv) != 3: sys.exit(__doc__)
    main(*sys.argv[1:])
