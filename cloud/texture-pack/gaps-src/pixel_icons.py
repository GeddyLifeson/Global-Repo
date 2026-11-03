"""S0294 Hand-drawn style 32 px sprites (shown at 64 px, nearest) for gems, shards, nuggets, raw ore, dust and ingots.
Each kind has its own silhouette; shape variant, colour ramp and speckle come from the material's colour and name."""
import colorsys, hashlib, io, math, random, sys, os, json, zipfile, glob
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/user/work/pix"); sys.path.insert(0, "/home/user/diaithirrpg/tools/art/blender"); sys.path.insert(0, "/home/user/work/gaps")
N = 32
LIGHT = (-0.5, -0.6, 0.62)
_l = math.sqrt(sum(v * v for v in LIGHT)); LIGHT = tuple(v / _l for v in LIGHT)


def ramp(rgb, metal=False):
    """5 colours dark..light (outline, shadow, base, light, glint) with hue drifting cool in shade, warm in light."""
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    if s < 0.22 and v > 0.78 and not metal:
        b = rgb
        return [(70, 108, 138, 255), (128, 176, 206, 255), tuple(b) + (255,), (232, 246, 255, 255), (255, 255, 255, 255)]
    v = min(max(v, 0.28), 0.92)
    out = []
    for dv, ds, dh in ((-0.62, 0.15, 0.03), (-0.30, 0.08, 0.015), (0, 0, 0), (0.17, -0.12, -0.012), (0.42, -0.45, -0.02)):
        if metal: ds *= 0.6
        r = colorsys.hsv_to_rgb((h + dh) % 1, min(1, max(0, s + ds)), min(1, max(0.06, v + dv * (0.9 if v > 0.5 else 1.1))))
        out.append(tuple(int(c * 255) for c in r) + (255,))
    return out


class Cv:
    def __init__(self): self.px = [[None] * N for _ in range(N)]
    def put(self, x, y, c):
        if 0 <= x < N and 0 <= y < N: self.px[y][x] = c
    def mask(self): return {(x, y) for y in range(N) for x in range(N) if self.px[y][x]}
    def outline(self, c):
        m = self.mask()
        for x, y in m:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + dx, y + dy) not in m: self.put(x + dx, y + dy, c)
    def img(self):
        im = Image.new("RGBA", (N, N))
        for y in range(N):
            for x in range(N):
                if self.px[y][x]: im.putpixel((x, y), self.px[y][x])
        return im


def poly(cv, pts, c):
    im = Image.new("L", (N * 4, N * 4)); ImageDraw.Draw(im).polygon([(x * 4 + 2, y * 4 + 2) for x, y in pts], fill=255)
    im = im.resize((N, N), Image.BOX)
    for y in range(N):
        for x in range(N):
            if im.getpixel((x, y)) > 127: cv.put(x, y, c)


def sphere_shade(cv, cx, cy, rx, ry, R, seed=0, noise=0.0):
    rnd = random.Random(seed)
    for y in range(N):
        for x in range(N):
            dx, dy = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            d = dx * dx + dy * dy
            if d > 1: continue
            nz = math.sqrt(1 - d)
            i = -(dx * LIGHT[0] * -1) * 0  # placeholder to keep structure simple
            i = (dx * LIGHT[0] + dy * LIGHT[1] + nz * LIGHT[2])
            i += rnd.uniform(-noise, noise)
            lvl = 4 if i > 0.93 else 3 if i > 0.62 else 2 if i > 0.3 else 1
            cv.put(x, y, R[lvl])


def seeded(name): return random.Random(int(hashlib.md5(name.encode()).hexdigest()[:8], 16))


# ---- gems: facet lists (polygon, shade) on a 32 grid
CUTS = {
 "brilliant": [([(8, 11), (11, 7), (21, 7), (24, 11)], 3), ([(11, 7), (16, 11), (21, 7)], 4), ([(8, 11), (16, 11), (16, 26)], 2),
               ([(16, 11), (24, 11), (16, 26)], 1), ([(8, 11), (11, 7), (16, 11)], 3), ([(16, 11), (21, 7), (24, 11)], 2)],
 "emerald": [([(10, 6), (22, 6), (26, 10), (6, 10)], 3), ([(6, 10), (26, 10), (26, 22), (6, 22)], 2), ([(10, 26), (22, 26), (26, 22), (6, 22)], 1),
             ([(10, 12), (22, 12), (22, 20), (10, 20)], 4), ([(10, 12), (22, 12), (26, 10), (6, 10)], 3), ([(10, 20), (22, 20), (26, 22), (6, 22)], 1)],
 "hexagon": [([(16, 5), (25, 10), (16, 15), (7, 10)], 4), ([(7, 10), (16, 15), (16, 27), (7, 21)], 2), ([(16, 15), (25, 10), (25, 21), (16, 27)], 1)],
 "trillion": [([(16, 5), (27, 24), (5, 24)], 2), ([(16, 5), (16, 18), (5, 24)], 3), ([(16, 5), (27, 24), (16, 18)], 1), ([(5, 24), (16, 18), (27, 24)], 2), ([(16, 9), (21, 20), (11, 20)], 4)],
 "teardrop": [([(16, 4), (22, 14), (22, 22), (16, 27), (10, 22), (10, 14)], 2), ([(16, 4), (22, 14), (16, 16), (10, 14)], 4), ([(10, 14), (16, 16), (16, 27), (10, 22)], 3), ([(16, 16), (22, 14), (22, 22), (16, 27)], 1)],

 "oval": [([(9, 8), (16, 8), (16, 16), (5, 16)], 3), ([(16, 8), (23, 8), (27, 16), (16, 16)], 2), ([(5, 16), (16, 16), (16, 25), (9, 25)], 2),
          ([(16, 16), (27, 16), (23, 25), (16, 25)], 1), ([(16, 11), (21, 16), (16, 21), (11, 16)], 4), ([(9, 8), (16, 8), (16, 11), (11, 16)], 4)],
 "prism": [([(8, 12), (13, 12), (16, 4)], 4), ([(13, 12), (19, 12), (16, 4)], 3), ([(19, 12), (24, 12), (16, 4)], 2),
           ([(8, 12), (13, 12), (13, 27), (8, 27)], 3), ([(13, 12), (19, 12), (19, 27), (13, 27)], 2), ([(19, 12), (24, 12), (24, 27), (19, 27)], 1)],
 "shardglass": [([(6, 24), (13, 5), (20, 14), (26, 24)], 1), ([(6, 24), (13, 5), (15, 17)], 3), ([(13, 5), (20, 14), (15, 17)], 2), ([(15, 17), (20, 14), (26, 24), (6, 24)], 1)],
}


def cabochon(name, rgb, rnd, R):
    cv = Cv(); sphere_shade(cv, 16, 17, 10, 8, R, rnd.randrange(999), 0.03)
    tok = name.lower()
    fl = None
    if "lapis" in tok: fl = (226, 186, 70)
    elif "turquoise" in tok: fl = (60, 90, 80)
    elif "opal" in tok or "ammolite" in tok: fl = None
    for _ in range(7 if fl else 0):
        x, y = rnd.randrange(8, 24), rnd.randrange(11, 24)
        if cv.px[y][x]: cv.put(x, y, fl + (255,))
    if "opal" in tok or "ammolite" in tok:
        for c, (x, y) in zip(((120, 220, 190), (230, 130, 200), (240, 200, 90), (120, 160, 240)), ((12, 17), (17, 15), (20, 19), (14, 21))):
            if cv.px[y][x]: cv.put(x, y, c + (255,))
    cv.outline(R[0]); return cv


def gem(name, rgb, rnd, cut=None):
    cv, R = Cv(), ramp(rgb)
    if cut == "cabochon": return cabochon(name, rgb, rnd, R)
    if cut not in CUTS: cut = "brilliant"
    for pts, sh in CUTS[cut]: poly(cv, pts, R[sh])
    cv.outline(R[0])
    lit = sorted((p for p in cv.mask() if cv.px[p[1]][p[0]] in (R[3], R[4])), key=lambda p: (p[0] - 10) ** 2 + (p[1] - 9) ** 2)
    for x, y in lit[:2] + [(lit[0][0] + 1, lit[0][1] + 1)] if lit else []: cv.put(x, y, (255, 255, 255, 255) if cut != "hexagon" else R[4])
    return cv


def shard(name, rgb, rnd, cut=None):
    cv, R = Cv(), ramp(rgb)
    spikes = [(9, 24, 5, 15), (16, 26, 7, 4), (23, 24, 5, 11)] if rnd.random() < .7 else [(12, 26, 7, 6), (21, 25, 6, 13)]
    for cx, by, w, top in sorted(spikes, key=lambda s: s[3] * -1):
        l, r = cx - w // 2, cx + w // 2
        poly(cv, [(l, by), (l, top + 4), (cx, top), (cx, by)], R[3]); poly(cv, [(cx, by), (cx, top), (r, top + 4), (r, by)], R[1])
        poly(cv, [(l, top + 4), (cx, top), (r, top + 4), (cx, top + 6)], R[4])
        cv.put(l, top + 5, R[4]); cv.put(l, top + 6, R[4])
    cv.outline(R[0]); return cv


def nugget(name, rgb, rnd, cut=None):
    cv, R = Cv(), ramp(rgb, True)
    blobs = [(12, 20, 6, 5), (20, 18, 6, 6), (16, 13, 5, 4)] if rnd.random() < .5 else [(10, 21, 5, 4), (18, 20, 7, 6), (21, 12, 4, 4)]
    for cx, cy, rx, ry in blobs: sphere_shade(cv, cx, cy, rx, ry, R, rnd.randrange(999), 0.05)
    cv.outline(R[0]); return cv


def raw(name, rgb, rnd, cut=None):
    hostc, vein = cut if cut else ((118, 108, 98), rgb)
    cv = Cv(); host = ramp(hostc); R = ramp(vein, True)
    pts = [(6, 20), (8, 12), (14, 7), (21, 8), (26, 14), (25, 22), (18, 26), (10, 25)]
    pts = [(x + rnd.uniform(-1, 1), y + rnd.uniform(-1, 1)) for x, y in pts]
    poly(cv, pts, host[2])
    c = (16, 17)
    for y in range(N):
        for x in range(N):
            if cv.px[y][x]:
                i = ((x - c[0]) * LIGHT[0] + (y - c[1]) * LIGHT[1]) / -9 + rnd.uniform(-.18, .18)
                cv.put(x, y, host[3] if i < -0.35 else host[2] if i < 0.3 else host[1])
    m = cv.mask()
    for _ in range(5):
        px, py = rnd.choice(sorted(m)); w = rnd.choice((2, 3, 3, 4))
        for dy in range(w):
            for dx in range(w + rnd.randrange(2)):
                if (px + dx, py + dy) in m and not (dx + dy > w + 1):
                    cv.put(px + dx, py + dy, R[3 if dx + dy < 2 else 2 if dx + dy < w else 1])
        cv.put(px, py, R[4])
    cv.outline(host[0]); return cv


def dust(name, rgb, rnd, cut=None):
    cv, R = Cv(), ramp(rgb)
    tiny = "tiny" in name or "speck" in name
    base, hh, ww = (24, 8 if tiny else 14, 7 if tiny else 12)
    for y in range(base - hh, base + 1):
        t = (y - (base - hh)) / hh
        half = int(1 + (t ** 0.55) * ww + rnd.uniform(-.5, .5))
        for x in range(16 - half, 16 + half + 1):
            i = ((x - 16) * LIGHT[0] + (y - (base - hh * .6)) * LIGHT[1] * 0.8) / (ww * 0.9) * -1
            lvl = 3 if i > 0.35 else 2 if i > -0.25 else 1
            if rnd.random() < .16: lvl = min(4, max(1, lvl + rnd.choice((-1, 1))))
            cv.put(x, y, R[lvl])
    for _ in range(3 if tiny else 6):
        x, y = rnd.randrange(8, 24), base + 1 + rnd.randrange(2)
        cv.put(x, y, R[rnd.choice((1, 2, 2, 3))])
    cv.outline(R[0]); return cv


def ingot(name, rgb, rnd, cut=None):
    cv, R = Cv(), ramp(rgb, True)
    poly(cv, [(7, 14), (11, 9), (25, 9), (21, 14)], R[3])          # top
    poly(cv, [(7, 14), (21, 14), (21, 22), (7, 22)], R[2])         # front
    poly(cv, [(21, 14), (25, 9), (25, 17), (21, 22)], R[1])        # side
    for x in range(9, 20): cv.put(x, 15, R[4]) if cv.px[15][x] else 0
    for x in range(12, 23): cv.put(x, 10, R[4])
    poly(cv, [(10, 18), (18, 18), (18, 20), (10, 20)], R[1])       # stamped recess
    cv.outline(R[0]); return cv


KIND = {"gem": gem, "shard": shard, "nugget": nugget, "raw": raw, "dust": dust, "ingot": ingot}


def render(kind, name, rgb, cut=None):
    cv = KIND[kind](name, rgb, seeded(name), cut)
    return cv.img().resize((64, 64), Image.NEAREST)


def from_csv(path, out):
    """CSV columns: ns,path,kind,r,g,b  (kind gem|shard|nugget|raw|dust|ingot). Writes {out}/{ns}/textures/item/{path}.png at 64 px.
    Run: python3 pixel_icons.py --csv rows.csv --out DIR"""
    import csv
    n = 0
    for r in csv.DictReader(open(path, newline="")):
        im = render(r["kind"], r["ns"] + ":" + r["path"], (int(r["r"]), int(r["g"]), int(r["b"])))
        f = f"{out.rstrip('/')}/{r['ns']}/textures/item/{r['path']}.png"; os.makedirs(os.path.dirname(f), exist_ok=True); im.save(f); n += 1
    print(n, "icons")


if __name__ == "__main__" and "--csv" in sys.argv:
    a = sys.argv; from_csv(a[a.index("--csv") + 1], a[a.index("--out") + 1])
