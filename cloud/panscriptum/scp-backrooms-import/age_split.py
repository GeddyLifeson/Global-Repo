"""Per-entry Age sort for one source with staging/age_sort.py's rule (PR #11).

python3 age_split.py AGE_SORT_PY RECORD.json OUT.json
"""
import importlib.util, json, sys
from collections import Counter

spec = importlib.util.spec_from_file_location("age_sort", sys.argv[1]); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
rec = json.load(open(sys.argv[2], encoding="utf-8"))
ages = [A.age_of(e) for e in rec["entries"]]
marked = Counter(a for a in ages if a)
fallback = max((a for a, n in marked.items() if n >= sum(marked.values()) * 0.05), default=1)
ages = [a or fallback for a in ages]
c = Counter(ages)
json.dump({"source": rec["source"], "rule": "staging/age_sort.py (PR #11) per entry; index = position in the record entries list",
           "counts": {f"Age {a}": c[a] for a in sorted(c)}, "ages": ages}, open(sys.argv[3], "w"), separators=(",", ":"))
print(rec["source"], dict(sorted(c.items())), "fallback", fallback)
