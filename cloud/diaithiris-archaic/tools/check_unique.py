"""python3 -I check_unique.py DIR : every tech name in TECH_NAMES_CORE.json + TECH_NAMES_MODS.json must be unique."""
import json, sys, collections
d = sys.argv[1]
names = {}
for f in ("TECH_NAMES_CORE.json", "TECH_NAMES_MODS.json"):
    names.update({f + ":" + k: v for k, v in json.load(open(d + "/" + f, encoding="utf8")).items()})
dup = [v for v, n in collections.Counter(names.values()).items() if n > 1]
print(len(names), "names,", len(dup), "duplicates", dup[:5])
sys.exit(1 if dup else 0)
