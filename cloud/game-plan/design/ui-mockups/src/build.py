"""Build the Shardfall screen gallery: pull real values from data/ into DATA, inline src/ into ../index.html."""
import csv, json, os
H = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(H, "..", "..", "..", "data")
rd = lambda p: list(csv.DictReader(open(os.path.join(D, p), encoding="utf-8")))

melee, fire = rd("items/weapons_melee.csv"), rd("items/weapons_firearm.csv")
armor, cons, mats = rd("items/armor_pieces.csv"), rd("items/consumables.csv"), rd("items/materials.csv")
idx = {r["item_id"]: r for r in melee + fire + armor + cons + mats}
strings = {r["str_id"]: r["text_en"] for r in rd("ui/strings.csv")}
pick = lambda rows, keys: [{k: r.get(k, "") for k in keys} for r in rows]

vendor = []
for r in rd("items/vendors.csv"):
    if r["vendor_id"] == "ITM_VEN_QUARTERMASTER" and r["item_id"] in idx:
        i = idx[r["item_id"]]
        vendor.append(dict(name=i["name"], cls=i.get("weapon_class", ""), rarity=i.get("rarity", ""), ar=i.get("phys_ar", ""),
                           el=i.get("element", ""), elar=i.get("element_ar", ""), w=i.get("weight", ""), price=r["price"],
                           g=[i.get(k, "") for k in ("grade_might", "grade_finesse", "grade_lore", "grade_grit")]))

DATA = dict(
    rarities=pick(rd("items/rarities.csv"), ["name", "frame_color_hex"]),
    bands=pick(rd("actors/region_bands.csv"), ["Region", "Min level", "Max level", "Element tint"]),
    bosses=pick([b for b in rd("actors/bosses.csv") if b["Class"] == "Shard-bearer"],
                ["Boss", "Region name", "Level", "HP (solo)", "Ward", "Ward element", "Phases", "Phase HP thresholds %", "Ember reward", "Weak points / parts"]),
    shardborn=rd("items/shardborn.csv")[:12],
    melee=pick([m for m in melee if m["rarity"] in ("Common", "Forged", "Rare", "Relic")],
               ["name", "weapon_class", "rarity", "phys_ar", "element", "element_ar", "grade_might", "grade_finesse", "grade_lore", "grade_grit", "weight", "breath_light", "poise_light", "sell_price"]),
    perks=[dict(id=p[list(p)[0]], name=list(p.values())[2], rank=list(p.values())[3], max=list(p.values())[4], req=list(p.values())[5], desc=list(p.values())[6])
           for p in rd("actors/perks.csv") if list(p.values())[1] == "SKL_BLADES"],
    skills=pick(rd("actors/skills.csv"), list(rd("actors/skills.csv")[0].keys())[:3]),
    vendor=vendor[:12],
    shop=pick([c for c in rd("items/cosmetics.csv") if "Wardrobe" in c["acquisition"] or c["kind"] != "Dye"],
              ["name", "kind", "color_hex", "acquisition", "price_ember", "price_seals", "price_usd"]),
    s={k: v for k, v in strings.items() if k.split("_")[1] in ("TITLE", "DEATH", "DLG", "ANCHOR", "VENDOR", "LOOT", "HUD", "INV", "MAP", "SKILL")},
)
out = os.path.join(H, "data.js")
open(out, "w").write("const DATA=" + json.dumps(DATA, ensure_ascii=False) + ";\n")

parts = {n: open(os.path.join(H, n), encoding="utf-8").read() for n in ("head.html", "ui.css", "paint.js", "data.js", "app.js")}
import re
from icons import ICONS, AUTH
GI = os.path.join(H, "gi")
sym, cred = [], [["asset","used_as","author","source_url","licence","notes"]]
for sid,(f,fill) in ICONS.items():
    d = re.findall(r'<path[^>]*fill="#fff"[^>]*d="([^"]+)"', open(os.path.join(GI, f + ".svg")).read())
    sym.append(f'<symbol id="{sid}" viewBox="0 0 512 512"><path fill="{fill}" d="{d[0]}"/></symbol>')
    a = f.split("/")[0]
    cred.append([f.split("/")[1] + ".svg", sid, AUTH[a], f"https://game-icons.net/1x1/{a}/{f.split('/')[1]}.html", "CC BY 3.0", "recolored; path unchanged"])
cred.append(["paint.js landscapes, figures, map", "all backdrops and key art", "Shardfall team (procedural code)", "game-plan/design/ui-mockups/src", "original work", "no third-party images"])
csv.writer(open(os.path.join(H, "..", "CREDITS.csv"), "w", newline="")).writerows(cred)
parts["head.html"] = parts["head.html"].replace("<!--ICONS-->", "".join(sym))
html = parts["head.html"].replace("/*CSS*/", parts["ui.css"]).replace("//JS", parts["paint.js"] + "\n" + parts["data.js"] + "\n" + parts["app.js"])
open(os.path.join(H, "..", "index.html"), "w", encoding="utf-8").write(html)
print("built", len(html), "bytes;", {k: len(v) for k, v in DATA.items() if isinstance(v, list)})
