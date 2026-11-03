#!/usr/bin/env python3 -I
# S0314
"""Ask Claude (Haiku 5.5, direct parallel calls, cached prefix) which blocks of each kept mod are working blocks, plus unit, Age.

usage: gen_rules_api.py PROFILE_DIR OUT_JSONL [WORKERS]
Needs ANTHROPIC_API_KEY in the environment (never printed). One row per mod: {jar, rules, units, age}. Usage appended to compute/ledger.csv if present."""
import csv, glob, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

SYSTEM = """You write compat data for a Minecraft 26.1 NeoForge modpack. For one mod you get its title, mod ids and its block ids (and some item ids).
Decide which blocks are WORKING BLOCKS: machines, generators, altars, ovens, crushers, furnaces, brewers, workbenches with progress, farms, quarries,
miners, pipes with tick logic only if they process. Decorative, plain storage, worldgen and ore blocks are not.
Return JSON {"rules":[{"pattern":..., "slots":1-4, "allowed":[...], "max_quality":0-4}], "units":[...], "age":1-8}.
- pattern: an exact id 'ns:block', or 'ns:*' only when the whole mod is machines; at most 12 rules; use ids that appear in the input. Group by prefix with a glob like 'ns:*_furnace' is NOT allowed: list ids or use ns:*.
- allowed: subset of speed, productivity, efficiency, quality. Generators and pumps: speed, efficiency. Pure converters: speed, efficiency. Crop or farm blocks: speed, productivity.
- max_quality 0 normal .. 4 legendary: simple machines 2, advanced 3, endgame 4.
- slots: basic machine 2, advanced 3, multiblock controller 4.
- units: which of these third-party units the mod stores, by id, ONLY if the mod clearly uses one: neoforge:fe (any Forge energy/RF), mekanism:joule, ic2:eu, ae2:ae, buildcraft:mj, botania:mana, arsnouveau:source, neoforge:mb (fluids in mB), create:su, pneumaticcraft:heat. Empty list if unknown.
- age: tech Age 1..8 (1 stone, 2 bronze, 3 iron/classical, 4 medieval, 5 industrial steam, 6 electric, 7 atomic/digital, 8 future) where this mod's machines belong.
Libraries, client mods, worldgen, mobs, decoration: rules empty, units empty, age by theme.
Output only the JSON."""
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["rules", "units", "age"], "properties": {
    "rules": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["pattern", "slots", "allowed", "max_quality"],
              "properties": {"pattern": {"type": "string"}, "slots": {"type": "integer"}, "max_quality": {"type": "integer"},
                             "allowed": {"type": "array", "items": {"type": "string", "enum": ["speed", "productivity", "efficiency", "quality"]}}}}},
    "units": {"type": "array", "items": {"type": "string"}}, "age": {"type": "integer"}}}


def call(key, user):
    body = {"model": "claude-haiku-5-5", "max_tokens": 1500, "thinking": {"type": "disabled"},
            "system": [{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral", "ttl": "1h"}}],
            "messages": [{"role": "user", "content": user}],
            "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}}}
    for t in range(4):
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
                                     {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            return json.loads(r["content"][0]["text"]), r["usage"]
        except Exception as e:
            err = e; time.sleep(2 ** t)
    raise err


def main(prof, out, workers=24):
    key = os.environ["ANTHROPIC_API_KEY"]
    done = {json.loads(l)["jar"] for l in open(out)} if os.path.exists(out) else set()
    files = [f for f in sorted(glob.glob(f"{prof}/*.json")) if os.path.basename(f)[:-5] not in done]
    ledger = []

    def one(f):
        d = json.load(open(f))
        blocks = sorted(d["blocks"])[:400]
        user = f"Mod: {d['title']}\nMod ids: {' '.join(d['mod_ids'])}\nBlocks ({len(d['blocks'])}): {' '.join(blocks)}\nSome items: {' '.join(sorted(d['items'])[:60])}"
        try: j, u = call(key, user)
        except Exception as e: return {"jar": d["jar"], "error": str(e)[:100]}
        ledger.append((d["jar"], u))
        return {"jar": d["jar"], "mod_ids": d["mod_ids"], **j}
    with ThreadPoolExecutor(int(workers)) as ex, open(out, "a") as o:
        for r in ex.map(one, files): o.write(json.dumps(r) + "\n"); o.flush()
    led = "/mnt/project-files/compute/ledger.csv"
    if os.path.exists(led):
        with open(led, "a", newline="") as lf:
            w = csv.writer(lf)
            for jar, u in ledger:
                w.writerow([time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "compat-rules", "claude-haiku-5-5", u.get("input_tokens", 0), u.get("output_tokens", 0),
                            u.get("cache_creation_input_tokens", 0), u.get("cache_read_input_tokens", 0)])
    print(len(files), "mods asked;", sum(u.get("cache_read_input_tokens", 0) for _, u in ledger), "cached tokens read")


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(*sys.argv[1:])
