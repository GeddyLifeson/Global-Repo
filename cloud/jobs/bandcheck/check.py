"""python3 check.py out-keyed.jsonl: magnitude on the ladder and within the row's ceiling, short basis, no em/en dashes."""
import json, os, sys
L = [f"M{i}" for i in range(11)]
rows = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bandcheck.jsonl"))}
bad = 0
for n, line in enumerate(open(sys.argv[1]), 1):
    try:
        r = json.loads(line); o = r["output"]; m = o["magnitude"]; b = o["basis"]; c = rows[r["id"]]["ceiling"]
        ok = m in L and L.index(m) <= L.index(c if c in L else "M10") and 0 < len(b) <= 300 and "—" not in b and "–" not in b
    except Exception:
        ok = False
    if not ok:
        bad += 1; print("line", n, "bad")
print("bad", bad); sys.exit(1 if bad else 0)
