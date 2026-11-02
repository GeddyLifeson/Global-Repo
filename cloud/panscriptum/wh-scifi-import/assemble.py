"""research-json -> kit records + index edits for all of Warhammer, Star Wars and Star Trek.

python3 assemble.py KIT_PANSCRIPTUM
Existing records are appended to (indices hold); Age of Sigmar and Blood Bowl are new records.
"""
import hashlib, json, re, sys
from pathlib import Path

KIT, RES = Path(sys.argv[1]) / "data", Path(__file__).parent / "research-json"
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
NOTE = ("Copyrighted setting: every entry is in our own words and links its wiki page. "
        "Third-party names stay internal: the Library coins its own.")
WH_GENRE = {"genre": "grimdark", "register": "guttural",
            "priors": {"landform": "shattered", "climate": "temperate", "condition": "wartorn", "tech": "medieval"}}
SOURCES = {  # source -> (slug, batch prefix, new-record fields or None)
    "Star Wars": ("star-wars", "sw", None),
    "Star Trek": ("star-trek", "st", None),
    "Warhammer 40,000": ("warhammer-40-000", "w40k", None),
    "Warhammer Fantasy": ("warhammer-fantasy", "whf", None),
    "Warhammer Age of Sigmar": ("warhammer-age-of-sigmar", "aos", dict(spine="II.G.3", category="Tabletop", genre=WH_GENRE,
        ceiling="Sigmar Heldenhammer",
        why="The God-King of Azyr leads the Pantheon of Order and reforged the Mortal Realms' defenders from mortal souls.",
        notes="Games Workshop's successor setting to Warhammer Fantasy: eight Mortal Realms built from the remnants of the "
              "destroyed World-that-Was, plus Warcry and Warhammer Underworlds. " + NOTE)),
    "Blood Bowl": ("blood-bowl", "bb", dict(spine="II.G.4", category="Tabletop",
        genre={"genre": "high_fantasy", "register": "guttural",
               "priors": {"landform": "continents", "climate": "temperate", "condition": "settled", "tech": "medieval"}},
        ceiling="Nuffle",
        why="The god of the game whose sacred rules every team plays by; star players come and go, Nuffle endures.",
        notes="Games Workshop's fantasy football game set in the Warhammer world, with its teams, star players, leagues "
              "and Dungeonbowl and Gutter Bowl variants. " + NOTE)),
}
NAV_NODE = "6.6.0"  # Warhammer Fantasy's metaverse node: Age of Sigmar and Blood Bowl share its multiverse
key = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
clean = lambda s: s.strip().replace("—", ", ").replace("–", "-")
FILLER = re.compile(r"(canon and is referenced by the characters|material of the expanded Star Wars fiction|from skill lists when building a roster"
                    r"|part of the core rules of the tabletop game|A named supporting character in that story|A named figure in the setting"
                    r"|recurring or notable figure of the modern|line of products by|universe and appears in its specialist games and video games"
                    r"|is a ship type fielded in fleet battles|creature or enemy kind that appears in the|one of the squad kinds available to players"
                    r"|is an aircraft type used in the|appears in the rosters of)")


def unpad(desc):  # drop the stock sentences batch writers appended to reach a word count; the first sentence always stays
    first, *rest = re.split(r"(?<=[.!?])\s+", desc)
    return " ".join([first] + [x for x in rest if not FILLER.search(x)])



def dump(path, obj, **kw):
    path.write_text(json.dumps(obj, ensure_ascii=False, **kw) + ("\n" if path.read_text(encoding="utf-8").endswith("\n") else ""), encoding="utf-8")


def digest(entries):
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16]


codes_p, genres_p, nav_p = KIT / "CHARTER_SPINE_CODES.json", KIT / "GENRES.json", KIT / "NAVTREE.json"
codes, genres, nav = (json.loads(p.read_text(encoding="utf-8")) for p in (codes_p, genres_p, nav_p))
for src, (slug, prefix, new) in SOURCES.items():
    path = KIT / "records" / f"{slug}.json"
    rec = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    entries = rec["entries"] if rec else []
    seen, before = {key(e["name"]) for e in entries}, len(entries)
    for f in sorted(RES.glob(f"{prefix}-*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            name, desc = clean(e.get("name", "")), unpad(clean(e.get("description", "")))
            if not name or not desc or key(name) in seen or e.get("topic") not in CATEGORY:
                continue
            seen.add(key(name))
            entries.append({"name": name, "type": clean(e.get("type", "")), "description": desc, "scale_note": "",
                            "category": CATEGORY[e["topic"]], "attestation": "Transcribed", "magnitude": "unassayed",
                            "topic": e["topic"], "catalogued": True, "subroom": "none", "wiki_page": e.get("wiki_page", "")})
    if len(entries) == before:
        print(src, "no new entries"); continue
    if rec is None:
        rec = {"source": src, "category": new["category"], "mode": "web", "entries": entries,
               "synthesis": {"source": src, "total_entries": 0, "ceiling_entity": new["ceiling"], "ceiling_rationale": new["why"],
                             "provisional_magnitude": "unassayed", "canon_branches": [], "integration_notes": new["notes"],
                             "legacy_magnitude_text": "", "method": "own-words catalogue (2026-10-18)", "demoted_by": ""},
               "status": "catalogued", "attestation": "Transcribed"}
        codes[src] = new["spine"]
        genres.setdefault(src, {**new["genre"], "score": 0, "confidence": 0.0, "runners_up": [], "genre_field_size": 0,
                                "genres_with_signal": 0, "set_by": "hand (2026-10-18)"})
        node = nav["nodes"][NAV_NODE]
        if src not in node["s"]:
            node["s"] = sorted(node["s"] + [src])
            for k in ("6.6.0", "6.6", "6"):
                nav["nodes"][k]["src"] += 1
    if "synthesis" in rec:
        rec["synthesis"]["total_entries"] = len(entries)
    rec["_writer"] = {"by": "warhammer/star-wars/star-trek import (2026-10-18)", "entries": len(entries), "digest": digest(entries)}
    path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(src, len(entries) - before, "added;", len(entries), "total")
dump(codes_p, dict(sorted(codes.items())), indent=2)
dump(genres_p, genres, indent=2)
dump(nav_p, nav, separators=(",", ":"))
