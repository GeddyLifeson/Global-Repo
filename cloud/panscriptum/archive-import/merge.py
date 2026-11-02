"""Merge one new source from a build run without the two LFS records (dc, marvel) into the committed outputs.

python merge.py RUN_DIR SOURCE   (RUN_DIR was seeded with the committed slots.json, worlds.json, shelves.json)
"""
import bisect, json, sys
from pathlib import Path

COMMITTED = Path("/home/user/omni/content/omniverse")
RUN, SRC = Path(sys.argv[1]), sys.argv[2]
load = lambda p: json.loads(p.read_text(encoding="utf-8"))

worlds, run_worlds = load(COMMITTED / "worlds.json"), load(RUN / "worlds.json")
slots, run_slots = load(COMMITTED / "slots.json"), load(RUN / "slots.json")
shelves, run_shelves = load(COMMITTED / "shelves.json"), load(RUN / "shelves.json")
new = [w for w in run_worlds if w["source"] == SRC]
phantoms = [v for k, v in run_slots.items() if k not in slots and k not in {w["id"] for w in new}]
for w in new:  # a phantom home world (dc/marvel missing) sorted before us in the same dimension took a slot
    shift = sum(1 for p in phantoms if p["dimension"] == w["dimension"] and p["slot"] < w["slot"])
    slots[w["id"]] = dict(run_slots[w["id"]], slot=w["slot"] - shift)
    w["slot"] -= shift
    w["centre"] = [(w["slot"] % 64) * 32768, (w["slot"] // 64) * 32768]  # build.py COLUMNS, SLOT_SPACING
for w in new:
    bisect.insort(worlds, w, key=lambda m: m["designation"])
shelves[SRC] = run_shelves[SRC]

cat, run_cat = load(COMMITTED / "kubejs/panscriptum/catalogue.json"), load(RUN / "kubejs/panscriptum/catalogue.json")
shelf = next(s for s in run_cat["shelves"] if s["name"] == shelves[SRC])
by_id = {w["id"]: w for w in new}
for row in shelf["worlds"]:
    row[3:5] = by_id[row[0]]["centre"]
names = [s["name"] for s in cat["shelves"]]
pos = bisect.bisect(names, shelf["name"])
cat["shelves"].insert(pos, shelf)
run_pos = [s["name"] for s in run_cat["shelves"]].index(shelf["name"])
for wing, run_wing in zip(cat["wings"], run_cat["wings"]):
    for lec in wing["lecterns"]:
        lec["shelves"] = [i + (i >= pos) for i in lec["shelves"]]
        run_lec = next(l for l in run_wing["lecterns"] if l["name"] == lec["name"])
        if run_pos in run_lec["shelves"]:
            bisect.insort(lec["shelves"], pos)

(COMMITTED / "worlds.json").write_text(json.dumps(worlds, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
for p, obj in ((COMMITTED / "slots.json", slots), (COMMITTED / "shelves.json", shelves)):
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False), encoding="utf-8")
(COMMITTED / "kubejs/panscriptum/catalogue.json").write_text(
    json.dumps(cat, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
print(f"{len(new)} worlds, shelf {shelf['name']} ({shelf['spine']}, {shelf['rank']}) at index {pos}")
