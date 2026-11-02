"""Agent research (aib/*.json) -> kit record + the kit index edits for The Archive In Between."""
import hashlib, json, re, sys
from pathlib import Path

KIT = Path("/home/user/diaithirrpg/panscriptum/data")
AIB = Path("/mnt/project-files/panscriptum/archive-import/research-json")
SRC = "The Archive In Between"
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


def dump(path, obj, **kw):
    path.write_text(json.dumps(obj, ensure_ascii=False, **kw) + ("\n" if path.read_text(encoding="utf-8").endswith("\n") else ""), encoding="utf-8")


def roundtrips(path, **kw):
    t = path.read_text(encoding="utf-8")
    return json.dumps(json.loads(t), ensure_ascii=False, **kw) == t.rstrip("\n")


entries, seen = [], set()
for f in sorted(AIB.glob("*.json")):
    for e in json.loads(f.read_text(encoding="utf-8")):
        e["name"] = re.sub(r"^(?:Annex |Universe )?([A-Z]-\d{4}[A-Z])$", r"Universe \1", e["name"].strip())
        if e["name"] == "The Pale Lodge":
            e["description"] += " (No link to Diaithir's Pale.)"
        key = e["name"].lower()
        if key in seen or e.get("topic") not in CATEGORY:
            continue
        seen.add(key)
        entries.append({"name": e["name"].strip(), "type": e["type"].strip(), "description": e["description"].strip(),
                        "scale_note": "", "category": CATEGORY[e["topic"]], "attestation": "Transcribed",
                        "magnitude": "unassayed", "topic": e["topic"], "catalogued": True, "subroom": "none",
                        "wiki_page": e.get("wiki_page", "")})
digest = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()[:16]
record = {
    "source": SRC, "category": "Web Fiction", "mode": "web", "entries": entries,
    "synthesis": {
        "source": SRC, "total_entries": len(entries), "ceiling_entity": "True Gods",
        "ceiling_rationale": "The setting ranks deity-class entities above everything else it files; its True Gods "
                             "rule whole universes, which no other catalogued entity is shown to do.",
        "provisional_magnitude": "unassayed", "canon_branches": [],
        "integration_notes": "Anthology of short files from many universes, each tagged with an Annex code that "
                             "measures its distance from the collection's prime reality (A-0001A). Catalogued in our "
                             "own words from the free public posts and the fan wiki; paid Patreon and eBook content "
                             "excluded. Its Pale Lodge is unrelated to Diaithir's Pale.",
        "legacy_magnitude_text": "", "method": "own-words catalogue from public sources (2026-10-18)",
        "demoted_by": "",
    },
    "status": "catalogued", "attestation": "Transcribed",
    "_writer": {"by": "archive-in-between thread", "entries": len(entries), "digest": digest},
}
out = KIT / "records" / "the-archive-in-between.json"
out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

codes_p, genres_p, nav_p = KIT / "CHARTER_SPINE_CODES.json", KIT / "GENRES.json", KIT / "NAVTREE.json"
fmt = {"indent": 2, "sort_keys": True}
for p, kw in ((codes_p, fmt), (genres_p, {"indent": 2}), (nav_p, {"separators": (",", ":")})):
    if not roundtrips(p, **kw):
        sys.exit(f"{p.name} would be reformatted; check its layout")
codes = json.loads(codes_p.read_text(encoding="utf-8"))
codes[SRC] = "II.E.9"
dump(codes_p, codes, **fmt)
genres = json.loads(genres_p.read_text(encoding="utf-8"))
genres[SRC] = {"genre": "cosmic_horror", "score": 0, "confidence": 0.0, "register": "sibilant",
               "priors": {"landform": "shattered", "climate": "temperate", "condition": "ruined", "tech": "spacefaring"},
               "runners_up": [], "genre_field_size": 0, "genres_with_signal": 0, "set_by": "hand (2026-10-18)"}
dump(genres_p, genres, indent=2)
nav = json.loads(nav_p.read_text(encoding="utf-8"))
node = nav["nodes"]["6.6.6"]  # Magic: The Gathering's metaverse node: Set II.E, the Blind Eternities
if SRC not in node["s"]:
    node["s"] = sorted(node["s"] + [SRC])
    for k in ("6.6.6", "6.6", "6"):
        nav["nodes"][k]["src"] += 1
dump(nav_p, nav, separators=(",", ":"))
print(len(entries), "entries ->", out)
