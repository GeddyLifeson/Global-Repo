import csv, json, sys, time, urllib.parse, urllib.request
out, cur, rows = sys.argv[1], None, {}
while True:
    q = {"limit": 100, "version": "latest", **({"cursor": cur} if cur else {})}
    d = json.load(urllib.request.urlopen("https://registry.modelcontextprotocol.io/v0/servers?" + urllib.parse.urlencode(q), timeout=60))
    for s in d["servers"]:
        v = s["server"]
        rows[v["name"]] = {"name": v["name"], "title": v.get("title", ""), "description": (v.get("description") or "").replace("\n", " "),
                           "repo": (v.get("repository") or {}).get("url", ""),
                           "packages": " ".join(sorted({p.get("registryType", "") for p in v.get("packages", [])})),
                           "remote": "yes" if v.get("remotes") else "", "env_keys": " ".join(sorted({e["name"] for p in v.get("packages", []) for e in p.get("environmentVariables", []) if e.get("isSecret") or e.get("isRequired")}))}
    cur = d.get("metadata", {}).get("nextCursor")
    if not cur: break
    time.sleep(0.1)
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(next(iter(rows.values()))))
    w.writeheader(); w.writerows(rows.values())
print(len(rows))
