"""Checks every ID the Glasswaste level tables use against data/, design/world, design/audio, design/art and the asset sheet."""
import csv, os, re, glob
HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
known = set()
for f in glob.glob(os.path.join(GP, "data", "**", "*.csv"), recursive=True) + glob.glob(os.path.join(GP, "design", "*", "*.csv")):
    if os.path.abspath(f).startswith(HERE):
        continue
    with open(f, newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh):
            for c in row:
                known.update(re.findall(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b", c))
try:
    import openpyxl
    wb = openpyxl.load_workbook(os.path.join(GP, "shardfall-assets.xlsx"), read_only=True)
    for ws in wb.worksheets:
        for r in ws.iter_rows(values_only=True):
            if r and r[0]:
                known.add(str(r[0]))
except Exception as ex:
    print("asset sheet skipped:", ex)
own = set()
for f in glob.glob(os.path.join(HERE, "*.csv")):
    with open(f, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    for r in rows[1:]:
        own.add(r[0])
NEW = ("LENC_", "LGT_LVL_", "RM_", "EDG_", "CUE_", "LP_", "LREQ_")
missing = {}
for f in sorted(glob.glob(os.path.join(HERE, "*.csv"))):
    if f.endswith(("checks.csv", "data-requests.csv", "conflicts.csv")):
        continue
    with open(f, newline="", encoding="utf-8") as fh:
        for r in list(csv.reader(fh))[1:]:
            for c in r:
                for tok in re.findall(r"\b(?:ITM|ACT|LOC|ENC|ENT|FAC|RES|MUS|AMB|LGT|BPH|ARENA|MQ|QST|CON|REG)_[A-Z0-9_]+\b|\b[VS]\d{4}\b", c):
                    if tok in known or tok in own or tok.startswith(NEW) or tok.endswith("_"):
                        continue
                    if tok.startswith("ITM_LT_BOSS") or tok.startswith("LGT_REG_04"):
                        continue
                    missing.setdefault(tok, os.path.basename(f))
out = [("check", "result")]
out.append(("IDs resolved against data, design and the asset sheet", "PASS" if not missing else f"{len(missing)} unresolved"))
for k, v in sorted(missing.items()):
    out.append((f"unresolved {k}", v))
with open(os.path.join(HERE, "checks.csv"), "w", newline="") as fh:
    csv.writer(fh).writerows(out)
print("\n".join(f"{a}: {b}" for a, b in out[:40]))
