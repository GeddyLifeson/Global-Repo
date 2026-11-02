"""Replace one source's worlds, slots and shelf in the committed omniverse outputs with a build run's (run made without dc/marvel).

python3 merge2.py COMMITTED_DIR RUN_DIR SOURCE
"""
import bisect, json, sys
from pathlib import Path

COMMITTED, RUN, SRC = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
load = lambda p: json.loads(p.read_text(encoding="utf-8"))

worlds = [w for w in load(COMMITTED / "worlds.json") if w["source"] != SRC]
slots, run_slots = load(COMMITTED / "slots.json"), load(RUN / "slots.json")
new = [w for w in load(RUN / "worlds.json") if w["source"] == SRC]
taken = {(v["dimension"], v["slot"]) for k, v in slots.items() if k not in {w["id"] for w in new}}
for w in new:
    if w["id"] in slots:
        assert (slots[w["id"]]["dimension"], slots[w["id"]]["slot"]) == (w["dimension"], w["slot"]), w["id"]
    else:
        assert (w["dimension"], w["slot"]) not in taken, w["id"]
        slots[w["id"]] = run_slots[w["id"]]
    bisect.insort(worlds, w, key=lambda m: m["designation"])

shelves, run_shelves = load(COMMITTED / "shelves.json"), load(RUN / "shelves.json")
assert shelves[SRC] == run_shelves[SRC]
cat, run_cat = load(COMMITTED / "kubejs/panscriptum/catalogue.json"), load(RUN / "kubejs/panscriptum/catalogue.json")
names = [s["name"] for s in cat["shelves"]]
assert names == [s["name"] for s in run_cat["shelves"]]  # same shelf order, so lectern indices stand
i = names.index(shelves[SRC])
cat["shelves"][i] = run_cat["shelves"][i]

(COMMITTED / "worlds.json").write_text(json.dumps(worlds, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
(COMMITTED / "slots.json").write_text(json.dumps(slots, indent=1, sort_keys=True, ensure_ascii=False), encoding="utf-8")
(COMMITTED / "kubejs/panscriptum/catalogue.json").write_text(
    json.dumps(cat, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
s = cat["shelves"][i]
print(f"{len(new)} worlds, shelf {s['name']} ({s['spine']}, {s['rank']})")
