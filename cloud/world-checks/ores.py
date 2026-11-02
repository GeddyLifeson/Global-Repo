"""Ore Y histogram per site: actual Y bands, and Y mapped back to the vanilla profile (Tellus shell mapping)."""
import json, sys, collections
import numpy as np
SEA = 200
VANILLA = {"coal": (0, 320), "iron": (-64, 384), "copper": (-16, 112), "gold": (-64, 32), "redstone": (-96, 15),
           "diamond": (-144, 16), "lapis": (-64, 64), "emerald": (-16, 480)}

def kind(n):
    return n.split(":")[1].replace("deepslate_", "").replace("_ore", "")

def report(name):
    d = json.load(open(f"out_{name}.json"))
    col = {(x, z): (g, f) for x, z, g, t, s, f, *_ in d["cols"]}
    by = collections.defaultdict(list)
    for n, x, y, z in d["ores"]:
        g, f = col[(x, z)]
        V = min(max(63 + g - SEA, 63), 319); D = g - (f + 1)
        by[kind(n)].append((y, g - y, V - (g - y) * (V + 64) / D, D / (V + 64)))
    g = np.array([c[2] for c in d["cols"]]); chunks = len(d["cols"]) / 256
    out = {"site": name, "chunks": chunks, "ground_y": [int(g.min()), int(np.median(g)), int(g.max())], "ores": {}}
    for k, rows in sorted(by.items()):
        a = np.array(rows)
        y, depth, v, f = a.T
        out["ores"][k] = {"per_chunk": round(len(a) / chunks, 1), "y_p5_p50_p95": [int(np.percentile(y, p)) for p in (5, 50, 95)],
                          "depth_p5_p50_p95": [int(np.percentile(depth, p)) for p in (5, 50, 95)],
                          "vanilla_y_p1_p50_p99": [int(np.percentile(v, p)) for p in (1, 50, 99)],
                          "vanilla_band": VANILLA.get(k), "stretch": round(float(np.median(f)), 2)}
    return out

if __name__ == "__main__":
    for s in sys.argv[1:]:
        r = report(s); print(json.dumps(r))
