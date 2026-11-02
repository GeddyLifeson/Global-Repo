"""Append the research-json batches to the kit's League of Legends record (append-only, so existing indices hold).

python3 assemble.py KIT_PANSCRIPTUM
"""
import hashlib, json, re, sys
from pathlib import Path

REC = Path(sys.argv[1]) / "data" / "records" / "league-of-legends.json"
RES = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "research-json"
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
key = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

r = json.loads(REC.read_text(encoding="utf-8"))
seen = {key(e["name"]) for e in r["entries"]}
added = 0
for f in sorted(RES.glob("*.json")):
    for e in json.loads(f.read_text(encoding="utf-8")):
        name, desc = e["name"].strip(), e["description"].strip().replace("—", ", ")
        if key(name) in seen or e.get("topic") not in CATEGORY or not desc:
            continue
        seen.add(key(name))
        r["entries"].append({"name": name, "type": e["type"].strip(), "description": desc, "scale_note": "",
                             "category": CATEGORY[e["topic"]], "attestation": "Transcribed", "magnitude": "unassayed",
                             "topic": e["topic"], "catalogued": True, "subroom": "none",
                             "wiki_page": e.get("wiki_page", "")})
        added += 1
n = len(r["entries"])
r["synthesis"]["total_entries"] = n
r["_writer"] = {"by": "league-of-legends import (2026-10-18)", "entries": n,
                "digest": hashlib.sha256(json.dumps(r["entries"], sort_keys=True).encode()).hexdigest()[:16]}
REC.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
print(added, "added;", n, "total")
