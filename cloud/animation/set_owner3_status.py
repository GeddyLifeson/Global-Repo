# S6876 Sets status in plans/ANIMATIONS_COVERAGE.csv for owner 3 (mobs, NPCs, bosses) rows. Run: python3 -I set_owner3_status.py <csv>
import csv, sys
DONE_NS = {"diaithirbestiary"}  # GeckoLib clips idle/walk/attack/fly + hurt/death/spawn
DONE_ID = {"AN08359"}           # Ascendant/planet boss attack, rise and death poses (diaithir-bosses LookModel)
OWN_NS_PREFIX = "diaithir"  # our own namespaces stay todo unless listed above
p = sys.argv[1]
rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
for r in rows:
    if not r["owner"].startswith("3"):
        continue
    if r["namespace"] in DONE_NS or r["id"] in DONE_ID:
        r["status"] = "done"
    elif r["namespace"].startswith(OWN_NS_PREFIX):
        pass
    elif r["status"] == "todo":
        r["status"] = "route"  # third-party mod keeps its own animations
w = csv.DictWriter(open(p, "w", newline="", encoding="utf-8"), fieldnames=list(rows[0]))
w.writeheader(); w.writerows(rows)
