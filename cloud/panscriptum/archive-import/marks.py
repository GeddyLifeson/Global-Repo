"""Add The Archive In Between to TIERS.json and append its worlds' shelfmarks to SHELFMARKS.json.

python3 marks.py KIT_PANSCRIPTUM RUN_WORLDS_JSON
"""
import json, sys
from pathlib import Path

KIT, SRC = Path(sys.argv[1]), "The Archive In Between"
tiers_p, marks_p = KIT / "data" / "TIERS.json", KIT / "data" / "SHELFMARKS.json"
tiers = json.loads(tiers_p.read_text(encoding="utf-8"))
if SRC not in tiers:
    row = dict(tiers["Magic: The Gathering — all planes"])  # same Blind Eternities stack, its own multiverse
    row.update(multiverse=max(v["multiverse"] for v in tiers.values()) + 1, hyperverse_contested_by=[])
    tiers[SRC] = row
    tiers_p.write_text(json.dumps(tiers, indent=2, ensure_ascii=False), encoding="utf-8")

sys.path.insert(0, str(KIT / "src"))
import address_space as A  # reads TIERS.json at import, so after the row lands

marks = json.loads(marks_p.read_text(encoding="utf-8"))
new = sorted({w["designation"] for w in json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")) if w["source"] == SRC})
for d in new:
    if d in marks:
        continue
    addr, mark, gaps = A.assign_and_mark(d, tiers[SRC])
    marks[d] = {"address": addr, "shelfmark": mark, "map_seed": A.map_seed(addr), **({"uncharted": list(gaps)} if gaps else {})}
marks_p.write_text(json.dumps(marks, indent=2, ensure_ascii=False), encoding="utf-8")
print(tiers[SRC]["multiverse"], len(new), "designations;", marks[new[0]]["shelfmark"])
