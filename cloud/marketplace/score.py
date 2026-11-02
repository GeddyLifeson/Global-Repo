import csv, re, sys
AREAS = {
 "minecraft_java": r"minecraft|neoforge|\bforge\b|fabricmc|\bmods?\b|modding|gradle|\bjava\b|\bjvm\b|maven|kotlin|curseforge|modrinth",
 "wiki_data": r"wiki|wikidata|mediawiki|sparql|scrap|crawl|dataset|\bcsv\b|sqlite|duckdb|parquet|knowledge graph",
 "llm_bulk": r"\bllm|inference|ollama|openrouter|groq|cerebras|gemini|embedding|vector|batch|huggingface|kaggle",
 "design_assets": r"image|texture|sprite|pixel|blender|\b3d\b|svg|figma|icon|audio|sound|music|freesound|diagram|mermaid|drawio|draw\.io",
 "writing": r"screenplay|screenwrit|fountain|final draft|grammar|proofread|docx|\bword\b|\bpdf|markdown|translat|novel|story",
 "sports": r"\bnfl\b|football|sports|espn|\bnba\b|odds|fantasy",
 "construction": r"construction|contractor|estimat|invoice|scope of work|permit|real estate|property|blueprint",
 "email_calendar": r"gmail|e-?mail|calendar|outlook|imap|google drive|google docs|sheets",
 "devops": r"github|\bgit\b|docker|backup|monitor|secret|lint|\btests?\b|security|vulnerab|dependenc|ci/cd|code review|static analysis",
 "token_saving": r"memory|context|compress|summar|documentation|docs|semantic|code search|codebase|token",
}
def score(text):
    t = text.lower()
    hits = {a: len(re.findall(p, t)) for a, p in AREAS.items()}
    return {a: h for a, h in hits.items() if h}
rows = []
for path, src in [("apps_raw.txt", "app"), ("apps_11_40.txt", "app"), ("apps_41_71.txt", "app")]:
    for line in open(path, encoding="utf-8"):
        p = [x.strip() for x in line.split("|")]
        if len(p) >= 2 and p[0] and not p[0].startswith("PAGE"):
            rows.append({"source": src, "name": p[0], "description": p[1], "free": p[2] if len(p) > 2 else "", "repo": "", "packages": "", "keys": ""})
cat = ""
for line in open("actions.txt", encoding="utf-8"):
    if line.startswith("##"): cat = line[2:].split("(")[0].strip(); continue
    p = [x.strip() for x in line.split("|")]
    if len(p) >= 2 and p[0]: rows.append({"source": "action:" + cat, "name": p[0], "description": p[1], "free": "", "repo": "", "packages": "", "keys": ""})
for r in csv.DictReader(open("mcp_registry.csv", encoding="utf-8")):
    rows.append({"source": "mcp" + (":remote" if r["remote"] else ""), "name": r["name"], "description": (r["title"] + " " + r["description"]).strip(),
                 "free": "", "repo": r["repo"], "packages": r["packages"], "keys": r["env_keys"]})
seen, out = set(), []
for r in rows:
    k = (r["source"][:3], r["name"].lower())
    if k in seen: continue
    seen.add(k)
    h = score(r["name"].split("/")[-1] + " " + r["description"])
    r["areas"] = " ".join(sorted(h)); r["score"] = sum(h.values()) + (1 if r["source"].startswith("mcp") and r["packages"] and not r["keys"] else 0)
    out.append(r)
out.sort(key=lambda r: -r["score"])
with open(sys.argv[1], "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["source", "name", "description", "areas", "score", "free", "repo", "packages", "keys"]); w.writeheader(); w.writerows(out)
from collections import Counter
print(len(out), Counter(r["source"].split(":")[0] for r in out), "scored>0:", sum(1 for r in out if r["score"] > 0))
print(Counter(a for r in out for a in r["areas"].split()))
