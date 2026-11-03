#!/usr/bin/env python3 -I
# S0315
"""Assemble the compat datapack from jar profiles + the API's per-mod answers (plans/INTEGRATION.md sections 3, 4, 6, 7).

usage: gen_data.py PROFILE_DIR RULES_JSONL TECH_ITEMS_JSON DATAPACK_DIR
Writes data/diaithircompat/{upgrades/targets,units,ages,codex,quests}/<modid>.json. Rule patterns are checked against the jar's own block ids
(or 'ns:*' for a namespace of the jar); anything else is dropped. Ages only for namespaces tech_items.json does not already cover.
Codex and quest files are links and ids only (title = the mod's real title); no prose is invented."""
import glob, json, os, sys

ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
KINDS = {"speed", "productivity", "efficiency", "quality"}


def w(base, sub, name, obj):
    p = os.path.join(base, "data/diaithircompat", sub, name + ".json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=1, sort_keys=False)


def main(prof, rules, tech, out):
    profs = {json.load(open(f))["jar"]: json.load(open(f)) for f in glob.glob(f"{prof}/*.json")}
    known_ns = set(json.load(open(tech))["namespaces"])
    ans = [json.loads(l) for l in open(rules)]
    byfam = {}
    for p in profs.values(): byfam.setdefault(p["family"], []).append(p)
    st = dict(rules=0, units=0, ages=0, mods=0, dropped=0)
    for a in ans:
        p = profs.get(a["jar"])
        if not p or "error" in a or not p["mod_ids"]: continue
        mid = p["mod_ids"][0]; blocks = set(p["blocks"]); ns = set(p["namespaces"])
        good = []
        for r in a["rules"]:
            pat = r["pattern"]
            if not (pat in blocks or (pat.endswith(":*") and pat[:-2] in ns and pat[:-2] in {i.split(":")[0] for i in blocks})):
                st["dropped"] += 1; continue
            kinds = [k for k in r["allowed"] if k in KINDS] or ["speed"]
            good.append({"pattern": pat, "priority": 100, "slots": max(1, min(4, r["slots"])), "allowed": kinds, "max_quality": max(0, min(4, r["max_quality"]))})
        if good: w(out, "upgrades/targets", mid, {"rules": good}); st["rules"] += len(good)
        if a["units"]: w(out, "units", mid, {"mod": mid, "stores": a["units"], "canonical": "plans/UNITS.md"}); st["units"] += 1
        age = max(1, min(8, a["age"])); gaps = [n for n in p["mod_ids"] if n not in known_ns]
        if gaps: w(out, "ages", mid, {"mods": gaps, "age": ROMAN[age]}); st["ages"] += 1
        tags = sorted(t for t in p["c_tags"])[:20]
        nxt = [q["mod_ids"][0] for q in byfam[p["family"]] if q is not p and q["mod_ids"]][:3]
        w(out, "codex", mid, {"mod": mid, "title": p["title"], "family": p["family"], "route": p["route"], "module": p["target"], "c_tags": tags,
                              "upgrade_rules": len(good), "units": a["units"], "age": ROMAN[age], "quest": f"diaithircompat:meet/{mid}"})
        w(out, "quests", mid, {"id": f"diaithircompat:meet/{mid}", "title": f"Meet {p['title']}", "age": ROMAN[age], "next": [f"diaithircompat:meet/{n}" for n in nxt]})
        st["mods"] += 1
    print(st)


if __name__ == "__main__":
    if len(sys.argv) != 5: sys.exit(__doc__)
    main(*sys.argv[1:])
