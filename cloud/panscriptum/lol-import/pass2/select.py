"""Pick catalogue candidates from the raw LoL crawl that the kit record lacks. python3 select.py RAW_DIR RECORD OUT"""
import gzip, json, re, sys
from pathlib import Path

RAW, REC, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
key = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
have = {key(e["name"]) for e in json.loads(REC.read_text(encoding="utf-8"))["entries"]}
DROP_CAT = re.compile(r"Disambiguation|Riot Games staff|Debug|Patch|Esports|TFT|Riftbound|Skins|Cosmetic|Icons|Ward skins|Emotes|Chromas|Audio|Wild Rift", re.I)
KEEP_MAIN = re.compile(r"items|Champions|Monsters|Summoner spells|Runes|Game modes|Maps|Minions|Structures|Places|Characters|Species|Factions|Regions", re.I)
WIKI = "https://wiki.leagueoflegends.com/en-us/"
seen, out = set(have), []


def add(name, src, url, cats, text):
    k = key(name)
    if not k or k in seen:
        return
    seen.add(k)
    out.append({"name": name, "source": src, "url": url, "categories": cats[:8], "text": text[:1500]})


for l in gzip.open(RAW / "lolwiki.jsonl.gz", "rt", encoding="utf-8"):
    p = json.loads(l)
    t, cats = p["title"], [c.split(":", 1)[1] for c in p["categories"]]
    if "/" in t or any(DROP_CAT.search(c) for c in cats) or p["text"].lstrip().lower().startswith("#redirect"):
        continue
    url = WIKI + t.replace(" ", "_")
    if t.startswith("Universe:"):
        add(t[9:], "universe-wiki", url, cats, p["text"])
    elif t.startswith("LoR:"):
        if any(re.search(r"LoR (Champions|Followers|Landmarks|Equipment)", c) for c in cats):
            add(t[4:], "lor-wiki", url, cats, p["text"])
    elif ":" not in t and any(KEEP_MAIN.search(c) for c in cats):
        add(t, "lol-wiki", url, cats, p["text"])
for l in gzip.open(RAW / "arcane.jsonl.gz", "rt", encoding="utf-8"):
    p = json.loads(l)
    t = p["title"]
    if "/" not in t and not p["text"].lstrip().lower().startswith("#redirect"):
        add(t, "arcane-wiki", "https://arcane.fandom.com/wiki/" + t.replace(" ", "_"), [c.split(":", 1)[1] for c in p["categories"]], p["text"])
for l in gzip.open(RAW / "universe.jsonl.gz", "rt", encoding="utf-8"):
    r = json.loads(l)
    d = r.get("data") or {}
    if r["kind"] == "champion" and d:
        c = d.get("champion") or d
        add(c.get("name", r["slug"]), "universe", f"https://universe.leagueoflegends.com/en_us/champion/{r['slug']}/", [], json.dumps(c)[:1500])
    elif r["kind"] == "faction" and d:
        f = d.get("faction") or d
        add(f.get("name", r["slug"]), "universe", f"https://universe.leagueoflegends.com/en_us/region/{r['slug']}/", [], json.dumps(f)[:1500])
OUT.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in out) + "\n", encoding="utf-8")
from collections import Counter
print(len(out), Counter(o["source"] for o in out))
