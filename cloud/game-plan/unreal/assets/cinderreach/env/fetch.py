"""Download the Cinderreach environment set listed in spec.csv; write manifest.csv and CREDITS.csv.

Sources are all CC0: Poly Haven (models 2K glTF, HDRIs 2K .hdr), ambientCG (2K PNG materials), Kenney (kit zips).
A row's pin column fixes the exact source asset ID; otherwise the query picks one.
Rerun safely: finished assets are skipped; a row whose download no longer matches its pin is fetched again. Usage: python3 fetch.py
"""
import csv, io, json, re, shutil, threading, zipfile
from functools import cache
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

HERE = Path(__file__).parent
UA = {"User-Agent": "Shardfall-asset-fetch/1.0"}
MAX_ASSET_MB = 150
PICK = threading.Lock()


def get(url):
    with urlopen(Request(url, headers=UA), timeout=120) as r:
        return r.read()


def save(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(get(url))


@cache
def ph_catalog(kind):
    return json.loads(get(f"https://api.polyhaven.com/assets?t={kind}s"))


def polyhaven(row, dest, taken):
    words = row["query"].lower().split()
    def score(item):
        aid, a = item
        text = " ".join([aid, a["name"], *a.get("tags", []), *a.get("categories", [])]).lower()
        return (all(w in text for w in words), words[0] in text, a.get("download_count", 0))
    with PICK:
        catalog = ph_catalog(row["kind"])
        if row["pin"]:
            aid, info = row["pin"], catalog[row["pin"]]
        else:
            aid, info = max(((k, v) for k, v in catalog.items() if k not in taken), key=score)
            if not score((aid, info))[1]:
                raise LookupError("no match")
            taken.add(aid)
    files = json.loads(get(f"https://api.polyhaven.com/files/{aid}"))
    if row["kind"] == "hdri":
        f = files["hdri"]["2k"]["hdr"]
        parts = {f"{aid}_2k.hdr": f}
    else:
        f = files["gltf"]["2k"]["gltf"]
        parts = {Path(f["url"]).name: f, **f.get("include", {})}
    if sum(p["size"] for p in parts.values()) > MAX_ASSET_MB << 20:
        raise ValueError("over size cap")
    for path, p in parts.items():
        save(p["url"], dest / path)
    return aid, f"https://polyhaven.com/a/{aid}", ", ".join(info.get("authors", {})) or "Poly Haven"


def ambientcg(row, dest, taken):
    search = f"id={row['pin']}" if row["pin"] else f"type=Material&q={quote(row['query'])}&sort=Popular&limit=10"
    found = json.loads(get(f"https://ambientcg.com/api/v2/full_json?{search}&include=downloadData"))["foundAssets"]
    with PICK:
        asset = next(a for a in found if row["pin"] or a["assetId"] not in taken)
        taken.add(asset["assetId"])
    dl = next(d for d in asset["downloadFolders"]["default"]["downloadFiletypeCategories"]["zip"]["downloads"] if d["attribute"] == "2K-PNG")
    zipfile.ZipFile(io.BytesIO(get(dl["downloadLink"]))).extractall(dest)
    return asset["assetId"], f"https://ambientcg.com/view?id={asset['assetId']}", "ambientCG (Lennart Demes)"


def kenney(row, dest):
    page = f"https://kenney.nl/assets/{row['query']}"
    url = re.search(r'https://kenney\.nl/media/pages/assets/[^"\']+\.zip', get(page).decode()).group(0)
    zipfile.ZipFile(io.BytesIO(get(url))).extractall(dest)
    return row["query"], page, "Kenney (kenney.nl)"


def main():
    spec = list(csv.DictReader(open(HERE / "spec.csv")))
    old = {r["asset_id"]: r for r in csv.DictReader(open(HERE / "manifest.csv"))} if (HERE / "manifest.csv").exists() else {}
    def done(row):
        prev = old.get(row["asset_id"], {})
        return prev.get("status") == "downloaded" and prev["source_id"] == (row["pin"] or prev["source_id"])

    taken = {"polyhaven": set(), "ambientcg": set(), "kenney": set()}
    for row in spec:
        sid = row["pin"] or (old[row["asset_id"]]["source_id"] if done(row) else "")
        taken[row["source"]].add(sid)

    def fetch(row):
        prev = old.get(row["asset_id"], {})
        if done(row):
            return {**prev, **row}
        dest = HERE / row["kind"] / row["asset_id"]
        shutil.rmtree(dest, ignore_errors=True)
        out = {**row, "source_id": "", "url": "", "author": "", "licence": "CC0 1.0", "path": "", "status": ""}
        try:
            if row["source"] == "polyhaven":
                sid, url, author = polyhaven(row, dest, taken["polyhaven"])
            elif row["source"] == "ambientcg":
                sid, url, author = ambientcg(row, dest, taken["ambientcg"])
            else:
                sid, url, author = kenney(row, dest)
            out.update(source_id=sid, url=url, author=author, path=str(dest.relative_to(HERE)), status="downloaded")
        except Exception as e:
            out["status"] = f"not fetched: {type(e).__name__}: {e}"[:160]
        return out

    with ThreadPoolExecutor(8) as pool:
        rows = list(pool.map(fetch, spec))

    with open(HERE / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(HERE / "CREDITS.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["asset_id", "source", "source_id", "url", "licence", "author", "used_in"])
        w.writerows([r["asset_id"], r["source"], r["source_id"], r["url"], r["licence"], r["author"], r["slice_use"]]
                    for r in rows if r["status"] == "downloaded")
    done = sum(r["status"] == "downloaded" for r in rows)
    print(f"{done}/{len(rows)} downloaded")


if __name__ == "__main__":
    main()
