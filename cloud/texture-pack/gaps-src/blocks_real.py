"""S0268 Real-material storage blocks: stacked ingots for metals, faceted mosaics for gems, rock-and-vein masses for raw ore.
Bulk placeholders without model calls: python3 blocks_real.py --csv rows.csv --out DIR   (columns in from_csv)"""
import re, os, sys, json, random, hashlib
sys.path.insert(0, "/home/user/work/pix"); sys.path.insert(0, "/home/user/work/gaps")
from PIL import Image
from pixel_icons import Cv, ramp, poly, sphere_shade, N
CSV_MODE = "--csv" in sys.argv  # CSV mode needs none of the jar/matlib scans
if not CSV_MODE:
    from matlib import resolve, token, METAL, GEM, RAW
    from build_list import jar
O = "/home/user/diaithirrpg/tools/art/blender/baked/pixel/assets/"
def up(cv): return cv.img().resize((64, 64), Image.NEAREST)
def rr(a): return random.Random(int(hashlib.md5(a.encode()).hexdigest()[:8], 16))


def metal_block(rgb, name):
    R = ramp(tuple(rgb), True); cv = Cv(); rnd = rr(name)
    for y in range(N):
        for x in range(N): cv.put(x, y, R[0])
    rows = 4; h = N // rows
    for r in range(rows):
        off = 0 if r % 2 == 0 else -4
        for i in range(-1, 4):
            x0 = off + i * 9 + 1; y0 = r * h + 1
            w, hh = 8, h - 2
            for y in range(hh):
                for x in range(w):
                    lvl = 4 if y == 0 and 1 < x < w - 1 else 3 if y <= 1 else 2 if y < hh - 2 else 1
                    if x == w - 1: lvl = min(lvl, 1) if y > 0 else lvl
                    cv.put(x0 + x, y0 + y, R[lvl])
            for x in (0, w - 1): cv.put(x0 + x, y0, R[1]); cv.put(x0 + x, y0 + hh - 1, R[1])
    for _ in range(14):
        x, y = rnd.randrange(N), rnd.randrange(N)
        c = cv.px[y][x]
        if c in (R[2], R[3]): cv.put(x, y, R[4] if rnd.random() < .5 else R[1])
    return up(cv)


def mosaic(rgb, name, cell=9, metal=False, dark_edge=True, glint=0.12):
    R = ramp(tuple(rgb), metal); rnd = rr(name)
    seeds = [(rnd.randrange(N), rnd.randrange(N), rnd.choice((1, 2, 2, 3, 3, 4 if rnd.random() < glint * 3 else 3))) for _ in range(int(N * N / cell ** 1.2))]
    lab = [[0] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            lab[y][x] = min(range(len(seeds)), key=lambda i: min((seeds[i][0] - x + dx) ** 2 + (seeds[i][1] - y + dy) ** 2 for dx in (-N, 0, N) for dy in (-N, 0, N)))
    cv = Cv()
    for y in range(N):
        for x in range(N):
            edge = any(lab[(y + dy) % N][(x + dx) % N] != lab[y][x] for dx, dy in ((1, 0), (0, 1)))
            cv.put(x, y, R[0] if edge and dark_edge else R[seeds[lab[y][x]][2]])
    return cv, R


def gem_block(rgb, name):
    cv, R = mosaic(rgb, name, cell=14, glint=0.2)
    for i in range(N):  # bevel frame
        for a, b in ((i, 0), (i, N - 1), (0, i), (N - 1, i)): cv.put(a, b, R[0])
        cv.put(i, 1, R[3]) if cv.px[1][i] != R[0] else 0
    return up(cv)


def raw_block(host, vein, name):
    cvh, H = mosaic(host, name, cell=9, dark_edge=True)
    V = ramp(tuple(vein), True); rnd = rr(name + "v"); cv = cvh
    for _ in range(9):
        cx, cy = rnd.uniform(3, N - 3), rnd.uniform(3, N - 3); rx, ry = rnd.uniform(1.5, 3), rnd.uniform(1.5, 2.6)
        t = Cv(); sphere_shade(t, cx, cy, rx, ry, V, rnd.randrange(99), .05); t.outline(V[0])
        for y in range(N):
            for x in range(N):
                if t.px[y][x]: cv.put(x, y, t.px[y][x])
    return up(cv)


def mass_block(rgb, name, coal=False):
    R = ramp(tuple(rgb)); cv = Cv(); rnd = rr(name)
    for y in range(N):
        for x in range(N): cv.put(x, y, R[0])
    for _ in range(40):
        cx, cy = rnd.uniform(0, N), rnd.uniform(0, N); rx, ry = rnd.uniform(3, 5.5), rnd.uniform(3, 5)
        t = Cv(); sphere_shade(t, cx, cy, rx, ry, R, rnd.randrange(99), .06); t.outline(R[0])
        for y in range(N):
            for x in range(N):
                if t.px[y][x]: cv.put(x, y, t.px[y][x])
    return up(cv)


def save(ns, p, im):
    f = f"{O}{ns}/textures/block/{p}.png"; os.makedirs(os.path.dirname(f), exist_ok=True); im.save(f)


def from_csv(path, out):
    """CSV columns: ns,path,kind,r,g,b  (kind metal|gem|raw|mass; raw takes r,g,b as the vein colour, optional host_r,host_g,host_b).
    Writes {out}/{ns}/textures/block/{path}.png at 64 px. Example row: mymod,tin_block,metal,200,200,210"""
    import csv
    global O; O = out.rstrip("/") + "/"
    n = 0
    for r in csv.DictReader(open(path, newline="")):
        c = (int(r["r"]), int(r["g"]), int(r["b"])); name = r["ns"] + ":" + r["path"]
        k = r["kind"]
        if k == "raw":
            host = (int(r.get("host_r") or 112), int(r.get("host_g") or 106), int(r.get("host_b") or 100)); im = raw_block(host, c, name)
        elif k == "gem": im = gem_block(c, name)
        elif k == "mass": im = mass_block(c, name)
        else: im = metal_block(c, name)
        save(r["ns"], r["path"], im); n += 1
    print(n, "blocks")


def main():
    if CSV_MODE:
        a = sys.argv; return from_csv(a[a.index("--csv") + 1], a[a.index("--out") + 1] if "--out" in a else O)
    # vanilla
    V = {"iron_block": metal_block(METAL["iron"][0], "iron"), "gold_block": metal_block(METAL["gold"][0], "gold"), "copper_block": metal_block((204, 120, 72), "copper"),
         "exposed_copper": metal_block((176, 124, 98), "xc"), "weathered_copper": metal_block((98, 146, 112), "wc"), "oxidized_copper": metal_block((72, 172, 148), "oc"),
         "netherite_block": metal_block((84, 72, 76), "nb"), "diamond_block": gem_block((196, 232, 244), "d"), "emerald_block": gem_block((28, 168, 92), "e"),
         "lapis_block": gem_block((34, 62, 152), "l"), "amethyst_block": gem_block((152, 92, 204), "a"), "redstone_block": mass_block((196, 28, 24), "r"),
         "coal_block": mass_block((34, 34, 38), "c"), "glowstone": mass_block((246, 204, 92), "g"),
         "raw_iron_block": raw_block((98, 74, 64), (118, 64, 50), "ri"), "raw_copper_block": raw_block((112, 104, 96), (204, 120, 72), "rc"), "raw_gold_block": raw_block((206, 202, 192), (232, 184, 52), "rg")}
    for k, im in V.items(): save("minecraft", k, im)
    n = 0
    for p in sorted(jar):
        m = re.fullmatch(r"assets/([^/]+)/textures/block/(raw_)?([a-z0-9_]+?)_block\.png", p)
        if not m: m2 = re.fullmatch(r"assets/([^/]+)/textures/block/(raw_)?(?:storage_blocks\.)?([a-z0-9_]+)\.png", p) if "storage_blocks" in p else None; m = m2
        if not m: continue
        ns, isRaw, tok = m.group(1), m.group(2), m.group(3)
        if ns == "minecraft": continue
        r = resolve(tok, "raw")
        if not r or "ore" in tok or re.search(r"coin|plating|reinforced|smooth|cut_|^quartz$|netherwood|obsidian", tok + p): continue
        src, k, fam, c, cut, note = r
        key = k if src == "real" else fam
        name = f"{ns}:{p}"
        if isRaw or "raw" in p:
            host, vein = RAW[key][:2] if key in RAW else ((112, 106, 100), c or METAL[key][0]) if src == "real" else ((112, 106, 100), c)
            im = raw_block(host, vein, name)
        elif fam == "gem" or (src == "real" and key in GEM):
            im = gem_block(c or GEM[key][0], name)
        else:
            col = c if src == "analogue" else METAL[key][0]
            im = metal_block(col, name)
        save(ns, p.split("/block/")[1][:-4], im); n += 1
    print(len(V), "vanilla;", n, "modded blocks")


if __name__ == "__main__": main()
