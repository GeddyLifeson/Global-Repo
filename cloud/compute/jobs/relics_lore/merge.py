import json, pathlib, os
d = pathlib.Path(__file__).parent
rows_in = [json.loads(l) for l in open(d / "in.jsonl")]
info = {r["id"]: r for r in rows_in}
out, lore = [], {}
for l in open(d / "out.jsonl"):
    o = json.loads(l)
    t = o["text"].strip().strip('"')
    if 8 <= len(t.split()) <= 20 and "\u2014" not in t and o["id"] in info:
        r = info[o["id"]]
        out.append([r["name"], "item", r["age"], "relics", t + " " + r["mech"]])
        lore[o["id"].split(":", 1)[1]] = t
concept = ["Iarmadun", "concept", 3, "relics",
           "Twenty-six unique relics of Ages III to VII: heroes' weapons, shields and the trinkets of the otherworld. Weapons and shields are held; "
           "rings, torques, charms and belts sit in Curios slots. Each has one active or passive power; crafted ones need a catalyst, the rest turn up in structure chests."]
json.dump([concept] + out, open("/mnt/project-files/library-sync/relics.json", "w"), ensure_ascii=False)
mod = pathlib.Path("/home/user/wt/g2/diaithir-relics/tools/lore.json")
if mod.parent.exists():
    json.dump(lore, open(mod, "w"), ensure_ascii=False, indent=1)
print(len(out), "of", len(info))
