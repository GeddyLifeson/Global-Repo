"""Add SCP Foundation and The Backrooms to TIERS.json and append their worlds' shelfmarks to SHELFMARKS.json.

python3 marks.py KIT_PANSCRIPTUM RUN_WORLDS_JSON
Each copies the Lovecraftian mythos' stack with its own multiverse (144, 145; 143 is held by PR #9's Archive In Between).
"""
import json, sys
from pathlib import Path

KIT = Path(sys.argv[1])
NEW = {"SCP Foundation": 144, "The Backrooms": 145}
tiers_p, marks_p = KIT / "data" / "TIERS.json", KIT / "data" / "SHELFMARKS.json"
tiers = json.loads(tiers_p.read_text(encoding="utf-8"))
for src, mv in NEW.items():
    tiers.setdefault(src, dict(tiers["the Lovecraftian mythos"], multiverse=mv, hyperverse_contested_by=[]))
tiers_p.write_text(json.dumps(tiers, indent=2, ensure_ascii=False), encoding="utf-8")

sys.path.insert(0, str(KIT / "src"))
import address_space as A  # reads TIERS.json at import, so after the rows land

marks = json.loads(marks_p.read_text(encoding="utf-8"))
worlds = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
for src in NEW:
    new = sorted({w["designation"] for w in worlds if w["source"] == src} - set(marks))
    for d in new:
        addr, mark, gaps = A.assign_and_mark(d, tiers[src])
        marks[d] = {"address": addr, "shelfmark": mark, "map_seed": A.map_seed(addr), **({"uncharted": list(gaps)} if gaps else {})}
    print(src, len(new), "designations;", new and marks[new[0]]["shelfmark"])
marks_p.write_text(json.dumps(marks, indent=2, ensure_ascii=False), encoding="utf-8")
