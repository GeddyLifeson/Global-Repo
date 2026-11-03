#!/usr/bin/env python3 -I
# S0312
"""Profile every kept (not clean-room) jar of the pack for the compat data pack (plans/INTEGRATION.md).

usage: profile_jars.py AUDIT.csv DISTRIBUTION_DIR OUT_DIR [WORKERS] [PACK_MODS_DIR]
Downloads each third-party jar from distribution/sources.json (or takes ours from ports/), reads it, writes OUT_DIR/<jar>.json,
deletes the download. Profile: mod ids, block/item ids (models, lang), recipe result ids, c: tag members, recipes that name
namespaces not in the pack (full JSON kept so a load-condition override can be written)."""
import csv, hashlib, json, os, re, subprocess, sys, tempfile, zipfile, tomllib
from concurrent.futures import ThreadPoolExecutor

REF = re.compile(r'"(?:item|id|tag|block|fluid)"\s*:\s*"#?([a-z0-9_.-]+):')


def pw_index(mods):
    """jar name -> local jar path, or {url, sha256} from the pack's mods/*.pw.toml links."""
    idx = {}
    for f in os.listdir(mods):
        p = os.path.join(mods, f)
        if zipfile.is_zipfile(p): idx[f] = p; continue
        try:
            t = tomllib.loads(open(p, "rb").read().decode("utf-8", "replace"))
            idx[t["filename"]] = {"url": t["download"]["url"], "sha256": t["download"]["hash"]}
        except Exception: pass
    return idx


def fetch(jar, dist, src, tmp):
    p = os.path.join(dist, "ports", jar)
    if os.path.exists(p): return p
    s = src.get(jar)
    if isinstance(s, str): return s
    if not s: return None
    out = os.path.join(tmp, jar)
    subprocess.run(["curl", "-sSL", "--retry", "3", "-o", out, s["url"]], check=True)
    if hashlib.sha256(open(out, "rb").read()).hexdigest() != s["sha256"]: raise RuntimeError("hash")
    return out


def profile(path):
    z = zipfile.ZipFile(path); names = z.namelist()
    try: ids = [m["modId"] for m in tomllib.loads(z.read("META-INF/neoforge.mods.toml").decode())["mods"]]
    except Exception: ids = []
    items, blocks, results, ctags = set(), set(), set(), {}
    recipes = {}
    for n in names:
        m = re.match(r"^assets/([^/]+)/models/item/(.+)\.json$", n)
        if m: items.add(f"{m[1]}:{m[2]}")
        m = re.match(r"^assets/([^/]+)/blockstates/(.+)\.json$", n)
        if m: blocks.add(f"{m[1]}:{m[2]}")
        m = re.match(r"^data/([^/]+)/(recipes?)/(.+)\.json$", n)
        if m:
            t = z.read(n).decode("utf-8", "replace"); recipes[n] = t
            try:
                j = json.loads(t); r = j.get("result")
                r = r.get("id") or r.get("item") if isinstance(r, dict) else r
                if isinstance(r, str): results.add(r)
            except Exception: pass
        m = re.match(r"^data/c/tags/(?:item|items|block|blocks)/(.+)\.json$", n)
        if m:
            try: ctags[m[1]] = len(json.loads(z.read(n))["values"])
            except Exception: pass
    ns = {re.match(r"^(?:assets|data)/([^/]+)/", n)[1] for n in names if re.match(r"^(?:assets|data)/([^/]+)/", n)} | set(ids)
    refs = {r: sorted(set(REF.findall(t))) for r, t in recipes.items()}
    return {"mod_ids": ids, "namespaces": sorted(ns), "items": sorted(items), "blocks": sorted(blocks),
            "result_ids": sorted(results), "c_tags": ctags, "recipe_refs": refs,
            "recipe_json": {k: v for k, v in recipes.items() if len(v) < 20000}}


def main(audit, dist, out, workers=8, mods=None):
    src = json.load(open(os.path.join(dist, "sources.json")))
    if mods: src = {**src, **pw_index(mods)}
    rows = [r for r in csv.DictReader(open(audit)) if r["final_route"] != "clean-room"]
    os.makedirs(out, exist_ok=True)

    def one(r):
        jar = r["file"]; o = os.path.join(out, jar + ".json")
        if os.path.exists(o): return jar, "have"
        with tempfile.TemporaryDirectory() as tmp:
            try:
                p = fetch(jar, dist, src, tmp)
                if not p: return jar, "no-source"
                d = profile(p); d.update(jar=jar, title=r["title"], route=r["final_route"], target=r["target_module"], family=r["family"])
                json.dump(d, open(o, "w"))
                return jar, "ok"
            except Exception as e: return jar, f"err {e}"
    with ThreadPoolExecutor(int(workers)) as ex:
        res = list(ex.map(one, rows))
    bad = [x for x in res if x[1] not in ("ok", "have")]
    print(len(rows), "jars;", len(bad), "problems"); [print(*b) for b in bad]


if __name__ == "__main__":
    if len(sys.argv) < 4: sys.exit(__doc__)
    main(*sys.argv[1:])
