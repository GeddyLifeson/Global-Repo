"""Crawled wiki titles minus kit entries -> per-franchise write-job lists.

python3 gap.py CRAWL_DIR KIT_PANSCRIPTUM OUT_DIR
Keeps in-universe article pages only, dedupes across wikis, prints the per-source table.
"""
import gzip, json, re, sys
from pathlib import Path

CRAWL, KIT, OUT = map(Path, sys.argv[1:4])
FRANCHISE = {  # crawl file -> (franchise, kit record slug)
    "starwars": ("Star Wars", "star-wars"), "starwars-databank": ("Star Wars", "star-wars"),
    "memory-alpha": ("Star Trek", "star-trek"), "memory-beta": ("Star Trek", "star-trek"),
    "warhammer40k": ("Warhammer 40,000", "warhammer-40-000"), "lexicanum-40k": ("Warhammer 40,000", "warhammer-40-000"),
    "necromunda": ("Warhammer 40,000", "warhammer-40-000"),
    "warhammerfantasy": ("Warhammer Fantasy", "warhammer-fantasy"), "lexicanum-whf": ("Warhammer Fantasy", "warhammer-fantasy"),
    "ageofsigmar": ("Warhammer Age of Sigmar", "warhammer-age-of-sigmar"),
    "lexicanum-aos": ("Warhammer Age of Sigmar", "warhammer-age-of-sigmar"),
    "bloodbowl": ("Blood Bowl", "blood-bowl"),
}
META = re.compile(r"(performers|staff|writers|editors|directors|producers|composers|disambiguation|episodes|"
                  r"novels|comics|books|publishers|real.world|audiobooks|anthologies|magazines|soundtracks|"
                  r"video games|card games|miniatures|codexes|white dwarf|merchandise|toys)", re.I)
BOOK = re.compile(r"\((novel|novella|anthology|short story|audio|audio drama|book|codex|battletome|game|video game|white dwarf|miniatures?|card game|rulebook|supplement|magazine|comic|graphic novel|omnibus|e-?book|army book|campaign|boxed set)[^)]*\)", re.I)
key = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
base = lambda s: re.split(r"\s*\(|/", s)[0]


def in_universe(src, r):
    t, cats = r["title"], r["cats"]
    if ":" in t or t.startswith(("List of", '"')) or "(disambiguation)" in t:
        return False
    if src.startswith("lexicanum") and BOOK.search(t):  # archived title lists carry no categories
        return False
    if src == "starwars" and not {"Canon articles", "Legends articles"} & set(cats):
        return False
    return not any(META.search(c) for c in cats if not c.startswith("Memory Beta articles sourced"))


have = {}
for slug in {s for _, s in FRANCHISE.values()}:
    p = KIT / "data" / "records" / f"{slug}.json"
    names = [e["name"] for e in json.loads(p.read_text(encoding="utf-8"))["entries"]] if p.exists() else []
    have[slug] = {key(n) for n in names} | {key(base(n)) for n in names}
gaps, table = {}, []
for f in sorted(CRAWL.glob("*.jsonl.gz")):
    src = f.name.split(".")[0]
    if src not in FRANCHISE:
        continue
    fr, slug = FRANCHISE[src]
    rows = {}
    for line in gzip.open(f, "rt", encoding="utf-8"):
        r = json.loads(line)
        t = rows.setdefault(r["title"], {**r, "cats": []})  # the crawl splits one page's categories across rows
        t["cats"] += [c for c in r["cats"] if c not in t["cats"]]
        t["desc"] = t.get("desc") or r.get("desc", "")
    keep = [r for r in rows.values() if in_universe(src, r)]
    bucket, new = gaps.setdefault(fr, {}), 0
    for r in keep:
        k = key(re.sub(r"/Legends$", "", r["title"]))  # a Canon page and its Legends twin are one entry
        if k in bucket:
            bucket[k].setdefault("also", []).append(r["url"])
        if k in have[slug] or key(base(r["title"])) in have[slug] or k in bucket:
            continue
        bucket[k] = {"name": r["title"], "source": src, "url": r["url"], "cats": r["cats"][:8], "hint": r.get("desc", "")}
        new += 1
    table.append((src, fr, len(rows), len(keep), len(keep) - new, new))
OUT.mkdir(parents=True, exist_ok=True)
print("| Source | Pages crawled | In-universe | Already have or dup | New gap |\n|---|---|---|---|---|")
for src, fr, n, k, h, g in table:
    print(f"| {src} ({fr}) | {n:,} | {k:,} | {h:,} | {g:,} |")
for fr, b in gaps.items():
    p = OUT / f"gap-{key(fr)}.jsonl.gz"
    with gzip.open(p, "wt", encoding="utf-8") as o:
        for r in b.values():
            o.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(fr, f"{len(b):,} write jobs ->", p.name)
