#!/usr/bin/env python3
"""Build pack-* Library cards from mod jars (real lang text and recipes only; nothing invented).
Usage: python3 -I tools/pack_cards.py JAR_DIR MISSING_IDS_TSV OUT_JSONL
MISSING_IDS_TSV: first column = pack id (ns:path), e.g. from tools/panscriptum_parity.py gap.
Card = id, name (en_us lang), desc (lang keys <key>.desc/.tooltip/.description, if present),
made_from (ingredients of the first recipe whose result is the id), mod (jar name), jar (file).
Ids with no lang key still get a card with name=None so J16 can list them."""
import json, sys, zipfile, glob, os, collections
jar_dir, ids_f, out = sys.argv[1:4]
want = {l.split("\t")[0].strip() for l in open(ids_f, encoding="utf-8") if ":" in l}
by_ns = collections.defaultdict(set)
for i in want: by_ns[i.split(":")[0]].add(i)
cards = {}
def ing(x):
    if isinstance(x, list): return [j for e in x for j in ing(e)]
    if isinstance(x, dict): return [x.get("item") or x.get("tag") and "#" + x["tag"]] if (x.get("item") or x.get("tag")) else []
    return [x] if isinstance(x, str) else []
for jar in sorted(glob.glob(os.path.join(jar_dir, "*.jar"))):
    try: z = zipfile.ZipFile(jar)
    except zipfile.BadZipFile: continue
    names = z.namelist()
    nss = {n.split("/")[1] for n in names if n.startswith("assets/") and n.count("/") > 1} & by_ns.keys()
    for ns in nss:
        lang = {}
        try: lang = json.loads(z.read(f"assets/{ns}/lang/en_us.json"))
        except Exception: pass
        for i in by_ns[ns]:
            p = i.split(":")[1]
            nm = lang.get(f"item.{ns}.{p}") or lang.get(f"block.{ns}.{p}")
            ds = next((lang[k] for t in ("desc", "tooltip", "description") for s in ("item", "block")
                       if (k := f"{s}.{ns}.{p}.{t}") in lang), None)
            cards[i] = {"id": i, "name": nm, "desc": ds, "made_from": None, "mod": ns, "jar": os.path.basename(jar)}
    for n in names:
        if "/recipe" in n and n.endswith(".json"):
            try: r = json.loads(z.read(n))
            except Exception: continue
            res = r.get("result")
            rid = res.get("id") or res.get("item") if isinstance(res, dict) else res
            c = cards.get(rid) if isinstance(rid, str) else None
            if c and c["made_from"] is None:
                c["made_from"] = sorted(set(filter(None, ing(r.get("ingredients") or r.get("ingredient") or list((r.get("key") or {}).values())))))
with open(out, "w", encoding="utf-8") as f:
    for i in sorted(want): f.write(json.dumps(cards.get(i) or {"id": i, "name": None, "desc": None, "made_from": None, "mod": i.split(":")[0], "jar": None}, ensure_ascii=False) + "\n")
n = len(want); h = sum(1 for i in want if i in cards and cards[i]["name"])
print(f"{n} ids, {h} with a lang name, {n-h} without (J16 list)")
