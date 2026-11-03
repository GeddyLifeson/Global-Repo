#!/usr/bin/env python3 -I
# S0317
"""Move non-trivial grid recipes of kept mods onto the Age ladder of stations (plans/PROGRESSION.md 7c, Marlon 11-03).

usage: gen_station_moves.py PROFILE_DIR RULES_JSONL GRAPH_JSON DATAPACK_DIR [STATS_JSON]
Vanilla (family 'vanilla') moves only tools, weapons and armour, Age by material (wood/stone/leather stay on the grid; copper II, iron/gold/chain III, diamond V, netherite VII).
Rule: the grid keeps simple everyday things (single-ingredient storage/slab/stair/plank/stick/door/food-style recipes, 2 slots or fewer);
tools, weapons, armour and multi-part machines (3+ distinct ingredients over 5+ slots) go to a station chosen by the mod's Age:
I-II hearth bench, III wright bench, IV smeltery (wright bench if no metal), V steam forge, VI-VII assembler, VIII+ fabricator; magic mods use the altar.
Only the five stations #163 registers are used (hearth bench, wright bench, smeltery, steam forge, fabricator); Age VI-VII (assembler) and magic (altar) recipes stay on the grid until those stations exist. Each moved recipe becomes two files: the original path re-issued with a condition that keeps it only while `diaithir_stations` is NOT loaded,
and a station recipe at data/<ns>/diaithir_stations/station_recipe/<name>.json (ports #163 codec: station key like station.wright_bench, stage, up to 9 {item|tag,count}, result, time_s, operator) that loads only with that mod. Nothing is lost if the station mod is absent. Ingredients are distinct items/tags, 1 each (owners balance)."""
import glob, json, os, re, sys

TRIVIAL = re.compile(r"(planks|stick|torch|button|pressure_plate|door|trapdoor|fence|gate|slab|stairs|wall|chest|barrel|bowl|boat|sign|bed|ladder|dye|paper|book|bread|cake|cookie|pie|sandwich|stew|soup|salad|juice|jam|block|nugget|ingot|ore|seed|bundle|crate|sack|bag|shelf|carpet|wool|glass|pane|lantern|candle|banner|frame|stone|brick|tile|paving|roof|shutter|pillar|planter|pot)")
EQUIP_WORDS = set("sword axe pickaxe shovel hoe leggings boots bow crossbow shield spear dagger mace hammer staff wand rifle pistol musket armor armour gun cannon helmet chestplate".split())
MACHINE = re.compile(r"(machine|generator|furnace|crusher|press|assembler|reactor|turbine|engine|pump|tank|pipe|conduit|cable|battery|capacitor|quarry|miner|smelter|centrifuge|mixer|extractor|compressor|forge|altar|controller|interface|terminal|drive|processor|circuit)")
STATIONS = ["", "station.hearth_bench", "station.hearth_bench", "station.wright_bench", "station.smeltery", "station.steam_forge", None, None, "station.fabricator"]  # None: no assembler/altar station registered yet (ports #163), recipe stays on the grid
METAL = re.compile(r"(ingot|plate|gear|rod|nugget|steel|iron|bronze|copper)")


def ing_id(x):
    if isinstance(x, list): x = x[0] if x else None
    if isinstance(x, str): return x
    if isinstance(x, dict):
        if "item" in x: return x["item"]
        if "tag" in x: return "#" + x["tag"]
    return None


def analyse(j):
    t = j.get("type", "")
    if t not in ("minecraft:crafting_shaped", "minecraft:crafting_shapeless", "crafting_shaped", "crafting_shapeless"): return None
    res = j.get("result"); rid = res.get("id") or res.get("item") if isinstance(res, dict) else res
    if not isinstance(rid, str) or (isinstance(res, dict) and (set(res) - {"id", "item", "count"})): return None
    cnt = res.get("count", 1) if isinstance(res, dict) else 1
    if "shaped" in t and "pattern" in j:
        slots = [c for row in j["pattern"] for c in row if c != " "]; key = {k: ing_id(v) for k, v in j.get("key", {}).items()}
        ings = [key.get(c) for c in slots]
    else: ings = [ing_id(x) for x in j.get("ingredients", [])]
    if not ings or any(i is None for i in ings): return None
    return rid, cnt, ings, j.get("category", "")


def decide(rid, ings, cat):
    name = rid.split(":")[1]; distinct = list(dict.fromkeys(ings))
    if re.search(r"(trim|template|stand)", name): return None
    if (EQUIP_WORDS & set(name.split('_'))) and len(ings) >= 4: return "part"
    if len(ings) <= 2 or len(distinct) == 1 or cat in ("food", "building", "redstone") and not MACHINE.search(name): return None
    if (EQUIP_WORDS & set(name.split('_'))) and len(ings) >= 3: return "part"
    if TRIVIAL.search(name) and not MACHINE.search(name): return None
    if len(distinct) >= 3 and len(ings) >= 5 or MACHINE.search(name) and len(distinct) >= 2: return "assembly"
    return None


def main(prof, rules, graph, out, stats=None):
    stations = json.load(open(graph))["stations"]; age = {}
    for l in open(rules):
        a = json.loads(l)
        if "error" not in a and a.get("mod_ids"): age[a["jar"]] = a["age"]
    moved = {}; kept = 0
    for f in sorted(glob.glob(f"{prof}/*.json")):
        p = json.load(open(f))
        if (p["jar"] not in age and p["family"] != "vanilla") or p["family"] == "diaithir-rewrite": continue
        fam = p["family"]; a = max(1, min(8, age.get(p["jar"], 1)))
        for path, txt in p["recipe_json"].items():
            try: j = json.loads(txt)
            except Exception: continue
            r = analyse(j)
            if not r: continue
            rid, cnt, ings, cat = r; form = decide(rid, ings, cat)
            if fam == "vanilla":  # vanilla: only tools, weapons and armour move; Age follows the material
                if form != "part" or set(rid.split(":")[1].split("_")) & {"wooden", "stone", "leather", "turtle"}: kept += 1; continue  # first-hour tools stay on the grid
                nm = rid.split(":")[1]; a = 7 if "netherite" in nm else 5 if "diamond" in nm else 3 if re.search(r"iron|golden|chainmail|bow|shield|trident|spear", nm) else 2 if "copper" in nm else 1
            if not form: kept += 1; continue
            st = None if fam.startswith("magic") else STATIONS[a]  # altar not registered yet
            if not st: kept += 1; continue
            if st == "station.smeltery" and not any(METAL.search(i) for i in ings): st = "station.wright_bench"
            cnt_by = {i: ings.count(i) for i in dict.fromkeys(ings)}; distinct = list(cnt_by)[:9]
            ns = p["mod_ids"][0] if p["mod_ids"] else path.split("/")[1]; name = os.path.splitext(os.path.basename(path))[0]
            NOT = {"type": "neoforge:not", "value": {"type": "neoforge:mod_loaded", "modid": "diaithir_stations"}}
            j2 = dict(j); j2["neoforge:conditions"] = list(j.get("neoforge:conditions", [])) + [NOT]
            o = os.path.join(out, path); os.makedirs(os.path.dirname(o), exist_ok=True); json.dump(j2, open(o, "w"), indent=1)
            s = {"station": st, "stage": form, "ingredients": [({"tag": i[1:]} if i.startswith("#") else {"item": i}) | {"count": min(64, cnt_by[i])} for i in distinct],
                 "result": {"id": rid, "count": cnt}, "time_s": 20 if form == "assembly" else 10, "operator": False}
            o = os.path.join(out, "data", ns, "diaithir_stations/station_recipe", f"{name}.json".replace("/", "_")); os.makedirs(os.path.dirname(o), exist_ok=True); json.dump(s, open(o, "w"), indent=1)
            moved.setdefault(st, 0); moved[st] += 1
    print("moved", sum(moved.values()), moved, "| left on grid", kept)
    if stats: json.dump({"moved": moved, "kept_on_grid": kept}, open(stats, "w"))


if __name__ == "__main__":
    if len(sys.argv) < 5: sys.exit(__doc__)
    main(*sys.argv[1:])
