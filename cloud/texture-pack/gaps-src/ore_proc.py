"""Pixel-art ore faces and nugget sheets from the real-material colours (ores_all.json)."""
import json, os, re, random, sys, hashlib
sys.path.insert(0, "/home/user/work/pix")
from PIL import Image
from pixel_icons import Cv, ramp, poly, sphere_shade, N
G = "/home/user/diaithirrpg/tools/art/blender/baked/"
NUG = [(2, 2, 3, 3, 2), (9, 4, 3, 2, 1), (12, 9, 2, 3, 2), (3, 9, 2, 2, 1), (6, 12, 3, 2, 2), (13, 1, 2, 2, 1)]
METALS = r"iron|copper|gold|tin|lead|silver|nickel|zinc|alumin|bauxite|uranium|osmium|platinum|titan|tungsten|cobalt|ardite|bronze|brass|steel|mithril|iridium|manganese|chrom|lithium|antimony|monazite|cinnabar|galena|sphalerite"
HOSTF = {"stone": "stone", "deepslate": "deepslate", "netherrack": "netherrack", "end_stone": "end_stone"}
hosts = {k: Image.open(f"{G}vanilla/assets/minecraft/textures/block/{v}.png").convert("RGBA").resize((N, N), Image.NEAREST) for k, v in HOSTF.items()}


def kind_of(name):
    if "coal" in name: return "coal"
    if "redstone" in name or "cinnabar" in name: return "glow"
    if re.search(METALS, name): return "metal"
    return "gem"


def face(name, base, rgb, rnd):
    k = kind_of(name); R = ramp(tuple(rgb), k in ("metal",))
    if k == "coal": R = ramp((34, 34, 38)); R[4] = (150, 150, 160, 255)
    host = hosts[base].copy(); hp = host.load()
    cv = Cv()
    for (u, v, w, h, l) in NUG:
        cx, cy = u * 2 + w + rnd.uniform(-.4, .4), v * 2 + h + rnd.uniform(-.4, .4)
        rx, ry = w + .9, h + .9
        if k == "gem":
            r = max(rx, ry); poly(cv, [(cx - r * .5, cy - r), (cx + r * .5, cy - r), (cx + r, cy), (cx + r * .5, cy + r), (cx - r * .5, cy + r), (cx - r, cy)], R[2])
            poly(cv, [(cx - r * .5, cy - r), (cx + r * .5, cy - r), (cx, cy)], R[4]); poly(cv, [(cx - r, cy), (cx - r * .5, cy - r), (cx, cy)], R[3])
            poly(cv, [(cx + r, cy), (cx, cy), (cx + r * .5, cy + r)], R[1]); poly(cv, [(cx + r * .5, cy + r), (cx, cy), (cx - r * .5, cy + r)], R[1])
        else:
            sphere_shade(cv, cx, cy, rx, ry, R, rnd.randrange(999), 0.07)
    m = cv.mask()
    for x, y in m:   # soft shadow on the host
        for dx, dy in ((1, 1), (2, 1), (1, 2)):
            if (x + dx, y + dy) not in m and 0 <= x + dx < N and 0 <= y + dy < N:
                r, g, b, a = hp[x + dx, y + dy]; hp[x + dx, y + dy] = (int(r * .55), int(g * .55), int(b * .55), a)
    cv.outline(R[0])
    for y in range(N):
        for x in range(N):
            if cv.px[y][x]: hp[x, y] = cv.px[y][x]
    if k == "glow":
        for _ in range(26):
            x, y = rnd.randrange(N), rnd.randrange(N)
            if (x, y) not in m and cv.px[y][x] is None: hp[x, y] = (230, 70, 50, 255) if rnd.random() < .6 else (255, 150, 110, 255)
    else:
        for _ in range(10):
            x, y = rnd.randrange(N), rnd.randrange(N)
            if cv.px[y][x] is None: hp[x, y] = R[3]
    return host.resize((64, 64), Image.NEAREST)


def heap(name, rgb, rnd):
    k = kind_of(name); R = ramp(tuple(rgb), k == "metal")
    if k == "coal": R = ramp((34, 34, 38)); R[4] = (150, 150, 160, 255)
    seeds = [(rnd.randrange(N), rnd.randrange(N), rnd.choice((1, 2, 2, 3, 3, 3, 4 if k != "coal" else 3))) for _ in range(44)]
    lab = [[0] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            best = min(range(len(seeds)), key=lambda i: min((seeds[i][0] - x + dx) ** 2 + (seeds[i][1] - y + dy) ** 2 for dx in (-N, 0, N) for dy in (-N, 0, N)))
            lab[y][x] = best
    im = Image.new("RGBA", (N, N)); px = im.load()
    for y in range(N):
        for x in range(N):
            c = R[seeds[lab[y][x]][2]]
            edge = any(lab[(y + dy) % N][(x + dx) % N] != lab[y][x] for dx, dy in ((1, 0), (0, 1)))
            px[x, y] = R[1] if edge else c
    return im.resize((64, 64), Image.NEAREST)


def main():
    ores = json.load(open("/home/user/work/pix/ores_all.json")); n = 0
    for o in ores:
        ns, path, base = o["ns"], o["path"], o["base"]; name = path.split("/")[-1]
        rnd = random.Random(int(hashlib.md5(name.encode()).hexdigest()[:8], 16))
        d = f"{G}ores/assets/{ns}/textures/block/{path}"
        face(name, base, o["ore_rgb"], rnd).save(d + ".png"); heap(name, o["ore_rgb"], rnd).save(d + "_heap.png"); n += 1
        if name in ("diamond_ore", "emerald_ore", "redstone_ore"):
            Image.open(d + ".png").save(d + "_glow.png"); Image.open(d + "_heap.png").save(d + "_glow_heap.png")
    print(n, "ores")


if __name__ == "__main__": main()
