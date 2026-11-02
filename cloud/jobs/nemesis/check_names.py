"""python check_names.py <outputs.jsonl>: each line {"id", "output": {...}} for the nemesis_age_* jobs. Exit 1 on any problem."""
import json, re, sys
BANNED = re.compile(r"shadow|dark lord|doom|chaos|void|realm", re.I)
NEED = {"names": 60, "epithets": 40, "ranks": 5, "warbands": 8}
AGE_I = {"names": ["Odhar", "Dubhan", "Fiach", "Gormal", "Lorcan", "Mael", "Ruadh", "Seang", "Tadhg", "Uathach", "Brocc", "Conn", "Donn", "Garbh", "Iolar", "Liath", "Nathair", "Sgian", "Tuireann", "Mathan"]}
AGE_I_EPITHETS = {"the Grey", "Frost-Eye", "Bone-Breaker", "the Hollow", "Night-Walker", "Cold-Tooth", "the Gnawer", "Ash-Hide", "the Silent", "Herd-Bane", "the Starved", "Ice-Born", "Fire-Thief", "the Patient", "Long-Claw"}
bad = []
for line in open(sys.argv[1], encoding="utf-8"):
    row = json.loads(line); o = row["output"]; i = row["id"]
    for k, n in NEED.items():
        v = o.get(k, [])
        if len(v) != n or len(set(v)) != n: bad.append(f"{i}: {k} needs {n} unique, has {len(set(v))}")
        bad += [f"{i}: banned word in {x!r}" for x in v if BANNED.search(x)]
    if not isinstance(o.get("heir"), str) or not o["heir"].strip(): bad.append(f"{i}: heir missing")
    if i == "nemesis_age_I" and not set(AGE_I["names"]) <= set(o.get("names", [])): bad.append(f"{i}: Age I names must keep the original 20")
    if any(" " in n for n in o.get("names", [])): bad.append(f"{i}: names are one word")
    if i != "nemesis_age_I":
        same_e = set(o.get("epithets", [])) & AGE_I_EPITHETS
        same_n = set(o.get("names", [])) & set(AGE_I["names"])
        if same_e: bad.append(f"{i}: Age I epithets belong to Age I only: {sorted(same_e)}")
        if len(same_n) > 5: bad.append(f"{i}: {len(same_n)} of Age I's 20 names reused; at most 5")
print("\n".join(bad) or "OK"); sys.exit(1 if bad else 0)
