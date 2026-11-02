"""Panscriptum coverage crawl: wiki titles -> missing-entry queues with lead text.

python -s crawl.py titles [host...]   # every mainspace title + categories, per host (resumable)
python -s crawl.py diff     # per source: titles we lack, meta pages dropped -> missing/<slug>.jsonl
python -s crawl.py leads [slug[@i/n]...]  # section-0 wikitext (plain) for each missing title
python -s crawl.py names    # leads -> names/<slug>.json.gz for tools/offload/write_entries.py
Paths: wikis.tsv next to this file; records in ../panscriptum/data/records; output in OUT.
"""
import glob, gzip, json, os, re, sys, threading, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("COVERAGE_OUT", r"E:\DiaithirRPG\panscriptum-crawl\coverage")
RECORDS = os.environ.get("RECORDS", r"E:\DiaithirRPG\panscriptum\data\records")
LOG = os.environ.get("COVERAGE_LOG", r"E:\DiaithirRPG\logs\coverage_crawl.md")
UA = {"User-Agent": "PanscriptumCoverage/1.0 (personal catalogue; 1 req/s)"}
META = re.compile(r"real[ -]world|cast|crew|voice act|actors|staff|writers|artists|disambig|gallery|"
                  r"images|transcript|community|users|policy|help|templates|stubs|merchandise|"
                  r"toys|soundtrack|rumou?rs|candidates for deletion", re.I)
_lock = threading.Lock()


def log(msg):
    with _lock, open(LOG, "a", encoding="utf-8") as f:
        f.write(f"- {time.strftime('%H:%M:%S')} {msg}\n")


def api(host, params):
    q = urllib.parse.urlencode({**params, "format": "json", "formatversion": 2})
    for path in ("/api.php", "/w/api.php", "/mediawiki/api.php"):
        for attempt in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(f"https://{host}{path}?{q}", headers=UA), timeout=40) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code in (429, 503):
                    time.sleep(60 * (attempt + 1)); continue
                break
            except Exception:
                time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{host}: API unreachable")


def wikis():
    """[(slugs sharing one wiki set, hosts)]; a group's missing titles go to its first slug."""
    groups = {}
    for line in open(os.path.join(HERE, "wikis.tsv"), encoding="utf-8"):
        slug, w = line.rstrip("\n").split("\t")
        groups.setdefault(w, []).append(slug)
    return [(slugs, [h for h in w.split(",") if "." in h and ":" not in h]) for w, slugs in groups.items()]


BIG = {"dc.fandom.com", "marvel.fandom.com", "wowpedia.fandom.com", "warcraft.wiki.gg", "prowrestling.fandom.com", "en.uesp.net"}
CUTS = ["", "C", "F", "J", "M", "P", "S", "V"]


def shards():
    hosts = sorted({h for _, hs in wikis() for h in hs})
    return [h for h in hosts if h not in BIG] + [f"{h}@{a}" for h in sorted(BIG & set(hosts)) for a in CUTS]


def crawl_host(spec):
    host, _, start = spec.partition("@")
    stop = CUTS[CUTS.index(start) + 1] if "@" in spec and start != CUTS[-1] else None
    path, state = os.path.join(OUT, "titles", spec + ".jsonl.gz"), os.path.join(OUT, "titles", spec + ".state.json")
    st = json.load(open(state)) if os.path.exists(state) else {"n": 0, "cont": {"gapfrom": start} if start else {}}
    if st.get("done"):
        return
    p = {"action": "query", "generator": "allpages", "gapnamespace": 0, "gapfilterredir": "nonredirects",
         "gaplimit": "max", "prop": "categories", "clshow": "!hidden", "cllimit": "max"}
    try:
        while True:
            d = api(host, {**p, **st["cont"]})
            pages = [pg for pg in d.get("query", {}).get("pages", []) if not stop or pg["title"] < stop]
            with gzip.open(path, "at", encoding="utf-8") as f:
                for pg in pages:
                    f.write(json.dumps({"title": pg["title"], "cats": [c["title"].split(":", 1)[1] for c in pg.get("categories", [])]}) + "\n")
            st["n"] += len(pages)
            if "continue" not in d or (stop and d["continue"].get("gapcontinue", "") >= stop):
                st["done"] = True
            else:
                st["cont"] = d["continue"]
            json.dump(st, open(state, "w"))
            if st.get("done"):
                break
            if st["n"] % 20000 < len(pages):
                log(f"{spec}: {st['n']} pages")
            time.sleep(1)
        log(f"{spec}: done {st['n']}")
    except Exception as e:
        log(f"{spec}: FAILED at {st['n']} ({e})")


def norm(s):
    s = re.sub(r"\s*\(.*?\)$", "", s.replace("_", " ")).lower()
    return re.sub(r"[^0-9a-z\u00c0-\uffff]+", "", s)


def diff():
    os.makedirs(os.path.join(OUT, "missing"), exist_ok=True)
    summary = []
    for slugs, hosts in wikis():
        files = [os.path.join(RECORDS, s + ".json") for s in slugs]
        if not hosts or not any(map(os.path.exists, files)):
            continue
        slug = slugs[0]
        have = {norm(e.get("name", "")) for fp in files if os.path.exists(fp)
                for e in json.load(open(fp, encoding="utf-8"))["entries"]}
        seen, kept, total = set(), [], 0
        for h in hosts:
            for fp in glob.glob(os.path.join(OUT, "titles", h + ".jsonl.gz")) + glob.glob(os.path.join(OUT, "titles", h + "@*.jsonl.gz")):
                for line in gzip.open(fp, "rt", encoding="utf-8"):
                    r = json.loads(line); k = norm(r["title"])
                    if "/" in r["title"] or any(META.search(c) for c in r["cats"]) or k in seen:
                        continue
                    seen.add(k); total += 1
                    if k not in have:
                        kept.append({"title": r["title"], "host": h, "cats": r["cats"]})
        with open(os.path.join(OUT, "missing", slug + ".jsonl"), "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r) + "\n" for r in kept)
        summary.append((slug, len(have), total, len(kept)))
    summary.sort(key=lambda r: -r[3])
    with open(os.path.join(OUT, "REAL_GAP.tsv"), "w", encoding="utf-8") as f:
        f.write("source\tour_entries\tin_universe_pages\tmissing\n")
        f.writelines(f"{s}\t{a}\t{b}\t{c}\n" for s, a, b, c in summary)
    log(f"diff: {len(summary)} sources, {sum(r[3] for r in summary)} missing titles -> REAL_GAP.tsv")


def plain(wt):
    wt = re.sub(r"\{\{[^{}]*\}\}", "", re.sub(r"\{\{[^{}]*\}\}", "", wt))
    wt = re.sub(r"\[\[(?:File|Image|Category):[^\]]*\]\]|<ref[^>]*/>|<ref.*?</ref>|<[^>]+>", "", wt, flags=re.S)
    wt = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", wt)
    return re.sub(r"\s+", " ", re.sub(r"'{2,}|^[|!{].*$", "", wt, flags=re.M)).strip()[:900]


def leads_for(spec):
    """spec = slug or slug@i/n (every n-th missing title from i), so big sources split across jobs."""
    slug, _, shard = spec.partition("@")
    si, sn = map(int, (shard or "0/1").split("/"))
    dst = os.path.join(OUT, "leads", f"{slug}@{si}.jsonl")
    done = {json.loads(l)["title"] for l in open(dst, encoding="utf-8")} if os.path.exists(dst) else set()
    todo = [json.loads(l) for l in gzip.open(os.path.join(OUT, "missing", slug + ".jsonl.gz"), "rt", encoding="utf-8")][si::sn]
    hosts = {}
    for r in todo:
        if r["title"] not in done:
            hosts.setdefault(r["host"], []).append(r)
    for batch in (g[i:i + 50] for g in hosts.values() for i in range(0, len(g), 50)):
        try:
            d = api(batch[0]["host"], {"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
                                       "rvsection": 0, "titles": "|".join(r["title"] for r in batch)})
        except Exception as e:
            log(f"{spec}: leads FAILED at {len(done)} ({e})"); return
        text = {p["title"]: p.get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("content", "") for p in d["query"]["pages"]}
        with open(dst, "a", encoding="utf-8") as f:
            for r in batch:
                r["lead"] = plain(text.get(r["title"], ""))
                r["url"] = f"https://{r['host']}/wiki/" + urllib.parse.quote(r["title"].replace(" ", "_"))
                f.write(json.dumps(r) + "\n")
        done.update(r["title"] for r in batch)
        time.sleep(1)
    log(f"{spec}: leads done {len(done)}")


def names():
    """leads/<slug>@*.jsonl -> names/<slug>.json.gz in write_entries.py's input shape (lead text as facts)."""
    os.makedirs(os.path.join(OUT, "names"), exist_ok=True)
    rows = {}
    for fp in glob.glob(os.path.join(OUT, "leads", "*@*.jsonl")):
        slug = os.path.basename(fp).rsplit("@", 1)[0]
        for line in open(fp, encoding="utf-8"):
            r = json.loads(line)
            if r["lead"]:
                rows.setdefault(slug, {})[r["title"]] = {"name": re.sub(r"\s*\(.*?\)$", "", r["title"]), "type": (r["cats"] or [""])[0],
                                                         "facts": r["lead"][:600], "wiki_page": r["url"]}
    for slug, by in rows.items():
        with gzip.open(os.path.join(OUT, "names", slug + ".json.gz"), "wt", encoding="utf-8") as f:
            json.dump(list(by.values()), f, ensure_ascii=False)
    log(f"names: {sum(map(len, rows.values()))} names with lead text across {len(rows)} sources")


def main():
    step = sys.argv[1]
    os.makedirs(os.path.join(OUT, "titles"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "leads"), exist_ok=True)
    only = sys.argv[2:]
    if step == "hosts":
        print(json.dumps(only or shards()))
    elif step == "titles":
        hosts = only or shards()
        with ThreadPoolExecutor(12) as ex:
            list(ex.map(crawl_host, hosts))
        log("titles: all hosts finished")
    elif step == "diff":
        diff()
    elif step == "names":
        names()
    elif step == "leads":
        order = only or [l.split("\t")[0] for l in open(os.path.join(OUT, "REAL_GAP.tsv"), encoding="utf-8")][1:]
        with ThreadPoolExecutor(8) as ex:
            list(ex.map(leads_for, order))
        log("leads: all sources finished")


if __name__ == "__main__":
    main()
