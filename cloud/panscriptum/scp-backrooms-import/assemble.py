"""research-json -> kit records + index edits for the SCP Foundation and the Backrooms.

python3 assemble.py KIT_PANSCRIPTUM SCP_EXTRACT.jsonl
scp-NN.json are keyed by "id" (names/urls come from the extract); scp-lore.json and backrooms-*.json carry name/wiki_page.
"""
import hashlib, json, re, sys
from pathlib import Path

KIT, RES = Path(sys.argv[1]) / "data", Path(__file__).parent / "research-json"
EXTRACT = {x["id"]: x for x in map(json.loads, open(sys.argv[2], encoding="utf-8"))}
CATEGORY = {
    "Persons": "Persons (named individual characters, real or fictional)",
    "Places": "Places & Locations (worlds, regions, cities, planes, ships-as-places)",
    "Factions": "Factions & Organizations (groups, nations, guilds, companies, orders)",
    "Powers": "Powers, Abilities & Systems (magic systems, power systems, tech systems, disciplines)",
    "Events": "Events (major storyline events, wars, historical turning points within the fiction)",
    "Peoples": "Peoples & Species (races, species and peoples as kinds, distinct from the individuals of that kind)",
    "Relics": "Vessels & Things (items, vehicles, weapons, artifacts, notable objects)",
    "Media": "Media (in-fiction media: books, songs, broadcasts, works that exist within the story itself)",
}
LICENSE = ("Source wiki text is CC BY-SA 3.0 (Wikidot); every entry is rewritten in our own words and links its page, "
           "where the original authors are credited. Third-party names stay internal: the Library coins its own.")
SOURCES = {
    "SCP Foundation": dict(slug="scp-foundation", files="scp-*.json", ceiling="SCP-3812",
        why="The wiki's best-known apex anomaly: a being that exists across every layer of narrative reality and rewrites lower layers at will.",
        notes="Collaborative horror wiki of contained anomalies (SCP articles, Series I-X, 001 proposals, -EX and joke files) "
              "plus its Groups of Interest, staff, sites and concepts. Decommissioned and archived articles excluded. " + LICENSE,
        genre={"genre": "cosmic_horror", "register": "compact",
               "priors": {"landform": "continents", "climate": "temperate", "condition": "settled", "tech": "industrial"}}),
    "The Backrooms": dict(slug="the-backrooms", files="backrooms-*.json", ceiling="The Backrooms (the whole level stack)",
        why="No single entity outranks the space itself: the endless stack of levels swallows anyone who noclips out of reality.",
        notes="Collaborative liminal-horror wiki of numbered Levels, Entities, Objects, Groups and Phenomena reached by noclipping "
              "out of reality. " + LICENSE,
        genre={"genre": "cosmic_horror", "register": "sibilant",
               "priors": {"landform": "shattered", "climate": "temperate", "condition": "ruined", "tech": "industrial"}}),
}
SPINE, NAV_NODE = "II.N.5", "6.1.0"  # horror shelf; shares the Lovecraftian mythos' metaverse node


def dump(path, obj, **kw):
    path.write_text(json.dumps(obj, ensure_ascii=False, **kw) + ("\n" if path.read_text(encoding="utf-8").endswith("\n") else ""), encoding="utf-8")


def entry(e):
    if "id" in e:  # numbered SCP article
        x = EXTRACT.get(e["id"])
        if not x:
            return None
        e = dict(e, name=f'{x["id"]}: {x["nick"]}' if x["nick"] else x["id"], wiki_page=x["url"])
    if "u" in e:  # Backrooms page
        e = dict(e, wiki_page="https://backrooms-wiki.wikidot.com" + e["u"])
    desc = e.get("description", "").strip().replace("—", ", ").replace("–", "-")
    if e.get("topic") not in CATEGORY or not desc or not e.get("name"):
        return None
    return {"name": e["name"].strip().replace("—", "-"), "type": e.get("type", "").strip().replace("—", "-"), "description": desc, "scale_note": "",
            "category": CATEGORY[e["topic"]], "attestation": "Transcribed", "magnitude": "unassayed", "topic": e["topic"],
            "catalogued": True, "subroom": "none", "wiki_page": e.get("wiki_page", "")}


codes_p, genres_p, nav_p = KIT / "CHARTER_SPINE_CODES.json", KIT / "GENRES.json", KIT / "NAVTREE.json"
codes, genres, nav = (json.loads(p.read_text(encoding="utf-8")) for p in (codes_p, genres_p, nav_p))
for src, s in SOURCES.items():
    entries, seen = [], set()
    for f in sorted(RES.glob(s["files"])):
        for raw in json.loads(f.read_text(encoding="utf-8")):
            e = entry(raw)
            k = e and re.sub(r"[^a-z0-9]", "", e["name"].lower())
            if e and k not in seen:
                seen.add(k); entries.append(e)
    if not entries:
        print(src, "no research yet"); continue
    rec = {"source": src, "category": "Web Fiction", "mode": "web", "entries": entries,
           "synthesis": {"source": src, "total_entries": len(entries), "ceiling_entity": s["ceiling"], "ceiling_rationale": s["why"],
                         "provisional_magnitude": "unassayed", "canon_branches": [], "integration_notes": s["notes"],
                         "legacy_magnitude_text": "", "method": "own-words catalogue from the CC BY-SA wiki (2026-10-18)", "demoted_by": ""},
           "status": "catalogued", "attestation": "Transcribed",
           "_writer": {"by": "scp-backrooms import (2026-10-18)", "entries": len(entries),
                       "digest": hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16]}}
    (KIT / "records" / f'{s["slug"]}.json').write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    codes[src] = SPINE
    genres.setdefault(src, {**s["genre"], "score": 0, "confidence": 0.0, "runners_up": [], "genre_field_size": 0,
                            "genres_with_signal": 0, "set_by": "hand (2026-10-18)"})
    node = nav["nodes"][NAV_NODE]
    if src not in node["s"]:
        node["s"] = sorted(node["s"] + [src])
        for k in ("6.1.0", "6.1", "6"):
            nav["nodes"][k]["src"] += 1
    print(src, len(entries), "entries")
dump(codes_p, dict(sorted(codes.items())), indent=2)
dump(genres_p, genres, indent=2)
dump(nav_p, nav, separators=(",", ":"))
