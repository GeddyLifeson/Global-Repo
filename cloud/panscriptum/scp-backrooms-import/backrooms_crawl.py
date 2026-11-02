"""Crawl backrooms-wiki.wikidot.com tag listings and page text into JSONL (stdlib only).

python backrooms_crawl.py OUT_DIR
Writes OUT_DIR/backrooms_raw.jsonl ({url,title,tags_seen,text}) and OUT_DIR/backrooms_crawl.log.
Resumable: skips urls already in the jsonl.
"""
import html, json, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = "https://backrooms-wiki.wikidot.com"
TAGS = ["level", "entity", "object", "group", "phenomenon", "location", "outpost", "sub-level", "frontrooms", "event", "hub"]
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
RAW, LOG = OUT / "backrooms_raw.jsonl", OUT / "backrooms_crawl.log"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PanscriptumCatalogue/1.0"}

def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")
    print(msg, flush=True)

def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            log(f"retry {i} {url}: {e}")
            time.sleep(3 * (i + 1))
    return ""

def text(fragment):
    fragment = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", fragment)
    fragment = re.sub(r"(?is)<div[^>]*(rate|footer|licensebox|collapsible-block-folded)[^>]*>.*?</div>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()

links = {}
for tag in TAGS:
    page = get(f"{BASE}/system:page-tags/tag/{tag}")
    found = re.findall(r'<div class="title">\s*<a href="(/[^"#?]+)"[^>]*>(.*?)</a>', page, re.S)
    if not found:
        found = [(h, "") for h in re.findall(r'href="(/[a-z0-9][a-z0-9:-]*)"', page.split('id="tagged-pages-list"')[-1])]
    for h, t in found:
        links.setdefault(h, {"tags_seen": [], "list_title": text(t)})["tags_seen"].append(tag)
    log(f"tag {tag}: {len(found)} pages; total {len(links)}")

done = set()
if RAW.exists():
    done = {json.loads(l)["url"] for l in RAW.open(encoding="utf-8") if l.strip()}
todo = [h for h in links if BASE + h not in done and not h.startswith("/system:")]
log(f"to fetch {len(todo)} (already {len(done)})")

def one(h):
    page = get(BASE + h)
    m = re.search(r'<div id="page-title">(.*?)</div>', page, re.S)
    body = page.split('<div id="page-content">', 1)[-1].split('<div class="page-tags">', 1)
    tags = re.findall(r'/system:page-tags/tag/([^"#]+)', body[1] if len(body) > 1 else "")
    time.sleep(0.4)
    return {"url": BASE + h, "title": text(m.group(1)) if m else links[h]["list_title"],
            "tags_seen": links[h]["tags_seen"], "tags": tags[:30], "text": text(body[0])[:2500]}

with RAW.open("a", encoding="utf-8") as f, ThreadPoolExecutor(4) as ex:
    for n, rec in enumerate(ex.map(one, todo), 1):
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if n % 100 == 0:
            f.flush(); log(f"fetched {n}/{len(todo)}")
log("DONE " + str(len(todo)))
