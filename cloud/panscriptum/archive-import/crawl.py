"""Pull the free public text of The Archive In Between into raw/ (research only, never committed).

python3 -I crawl.py OUTDIR
"""
import html, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
WIKI = "https://theunofficialarchiveinbetweenwiki.miraheze.org/w/api.php"
SUB = "https://thearchiveinbetween.substack.com/api/v1"
SITE = "https://www.thearchiveinbetween.com"


def get(url, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research crawl)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                print("FAIL", url, e, file=sys.stderr)
                return None
            time.sleep(2 ** i)


def text(h):
    h = re.sub(r"(?is)<(script|style|nav|footer|header)\b.*?</\1>", " ", h or "")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def wiki():
    titles, cont = [], {}
    while True:
        q = {"action": "query", "list": "allpages", "aplimit": "500", "apnamespace": "0", "format": "json", **cont}
        d = json.loads(get(WIKI + "?" + urllib.parse.urlencode(q)))
        titles += [p["title"] for p in d["query"]["allpages"]]
        if "continue" not in d:
            break
        cont = d["continue"]
    with open(OUT / "wiki.jsonl", "w", encoding="utf-8") as f:
        for i in range(0, len(titles), 20):
            q = {"action": "query", "prop": "extracts|categories", "explaintext": "1", "exlimit": "20",
                 "cllimit": "max", "redirects": "1", "format": "json", "titles": "|".join(titles[i:i + 20])}
            d = json.loads(get(WIKI + "?" + urllib.parse.urlencode(q)))
            for p in d["query"]["pages"].values():
                f.write(json.dumps({"title": p["title"], "text": p.get("extract", ""),
                                    "categories": [c["title"].split(":", 1)[1] for c in p.get("categories", [])],
                                    "url": "https://theunofficialarchiveinbetweenwiki.miraheze.org/wiki/" +
                                           urllib.parse.quote(p["title"].replace(" ", "_"))}, ensure_ascii=False) + "\n")
    print("wiki", len(titles))


def substack():
    n, off = 0, 0
    with open(OUT / "substack.jsonl", "w", encoding="utf-8") as f:
        while True:
            posts = json.loads(get(f"{SUB}/archive?sort=new&offset={off}&limit=50") or "[]")
            if not posts:
                break
            for p in posts:
                body = ""
                if p.get("audience") == "everyone":
                    full = get(f"{SUB}/posts/{p['slug']}")
                    body = text(json.loads(full).get("body_html")) if full else ""
                f.write(json.dumps({"title": p.get("title"), "date": p.get("post_date"), "url": p.get("canonical_url"),
                                    "audience": p.get("audience"), "subtitle": p.get("subtitle"), "text": body},
                                   ensure_ascii=False) + "\n")
                n += 1
            off += 50
    print("substack", n)


def site():
    xml = get(SITE + "/sitemap.xml") or ""
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    with open(OUT / "site.jsonl", "w", encoding="utf-8") as f:
        for u in urls:
            if any(s in u for s in ("/cart", "/apparel/p/", "/books/p/")):
                continue
            f.write(json.dumps({"url": u, "text": text(get(u))}, ensure_ascii=False) + "\n")
    print("site", len(urls))


for job in (wiki, substack, site):
    try:
        job()
    except Exception as e:
        print("JOB FAIL", job.__name__, e, file=sys.stderr)
