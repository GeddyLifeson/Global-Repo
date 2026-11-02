#!/usr/bin/env python3
"""Shardfall weapons -> Minecraft item models (cuboid, Blockbench-compatible), 32x textures, mapping CSV, contact sheets.

    python3 gen.py [ITEMS_DIR]     default: ../../data/items. Deterministic; rerun after data changes.

Every weapon is drawn as pixel parts on a 32 or 64 px canvas (2 px per model unit = 32x). The same parts give the
texture (front view) and the 3D elements (each part has its own thickness), so a model and its texture never drift.
"""
import colorsys, csv, json, math, random, shutil, sys, zlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ITEMS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "data" / "items"
ASSETS = HERE / "pack" / "assets" / "shardfall"

MAT = {  # base colors; Bible element and Lens colors are exact, the rest are salvage materials
    "steel": "#9AA3AB", "darksteel": "#4E545C", "hull": "#6F8290", "rust": "#8E5B3A", "starmetal": "#DCD5BA",
    "gold": "#CFA545", "brass": "#B58A42", "copper": "#B0693C", "wood": "#6E4C31", "leather": "#4B3528",
    "bone": "#D2C6A6", "ceramic": "#DADDD6", "choirglass": "#BBA9E2", "quiet": "#2A2632", "stone": "#7D7A72",
    "frost": "#CDEFFC", "bloom": "#2FB89A", "bloomwood": "#55703D", "storm": "#B48CFF", "hollow": "#5A3A7A",
    "ember": "#F06A2A", "lens": "#8FE3EE", "iron": "#B9A27A", "garnet": "#9E3446", "amethyst": "#9B7BD6",
}
THEMES = [  # name words -> (main, trim, grip); first matching row wins
    ("Starmetal Orbit Gyre", "starmetal", "gold", "leather"),
    ("Choir Pilgrim Archivist", "choirglass", "steel", "leather"),
    ("Lantern Ember Cinder Reactor Kindling Ash Sun", "darksteel", "brass", "leather"),
    ("Remnant Servo Cryo Courier Emitter Conductor Arena Orbital Reaper Gravity", "ceramic", "darksteel", "darksteel"),
    ("Clan Bone Reaver Boulder", "bone", "wood", "leather"),
    ("Thorn Briar Bloom", "bloomwood", "bloom", "wood"),
    ("Frost Rime", "frost", "steel", "leather"),
    ("Quiet Hollow Grave Silence", "quiet", "hollow", "quiet"),
    ("Storm", "darksteel", "storm", "leather"),
    ("Castellan Banneret Officer Captain Knight Meridian Iron Castle", "steel", "gold", "leather"),
    ("Hull Bulkhead Hatch Keel Rivet Deck Wreck Mooring Anchor Salvag Scaveng Rotor Crash Rattle Ranger",
     "hull", "rust", "wood"),
]
ELEM = {"Ember": "ember", "Storm": "storm", "Hollow": "hollow", "Frost": "frost", "Bloom": "bloom", "Iron": "iron"}
LEVEL = {"Common": 0, "Forged": 1, "Rare": 2, "Relic": 3, "Shardborn": 4, "Arena": 3}
LONG = {"GRS", "TWB", "GAX", "GHM", "POL", "STF", "ARF", "SCT", "SHG", "SNP", "LCH", "LNC"}
GUNS = {"PST", "SMG", "ARF", "SCT", "SHG", "SNP", "LCH", "LNC"}
STYLE_SHADE = {"groove": 1}


def ramp(hexc):
    H, L, S = colorsys.rgb_to_hls(*(int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)))
    out = []
    for dl, dh in ((-0.30, 0.03), (-0.15, 0.015), (0, 0), (0.12, -0.015), (0.24, -0.03)):
        rgb = colorsys.hls_to_rgb((H + dh) % 1, min(max(L + dl, 0.04), 0.96), S)
        out.append(tuple(round(c * 255) for c in rgb) + (255,))
    return out


RAMP = {k: ramp(v) for k, v in MAT.items()}


# ---- pixel shapes -------------------------------------------------------------------------------------------------
def shape(n, fn):
    im = Image.new("L", (n, n))
    fn(ImageDraw.Draw(im))
    px = im.load()
    return {(x, y) for x in range(n) for y in range(n) if px[x, y]}


def poly(n, pts): return shape(n, lambda d: d.polygon(pts, fill=1))
def oval(n, box): return shape(n, lambda d: d.ellipse(box, fill=1))
def ring(n, box, w): return shape(n, lambda d: d.ellipse(box, outline=1, width=w))
def line(n, pts, w=1): return shape(n, lambda d: d.line(pts, fill=1, width=w))
def rect(x0, y0, x1, y1): return {(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
def bar(cx, y0, y1, w): return rect(cx - w // 2, y0, cx - w // 2 + w - 1, y1)
def mirx(pix, cx): return {(2 * cx - 1 - x, y) for x, y in pix}
def miry(pix, n): return {(x, n - 1 - y) for x, y in pix}


def blade(cx, tip, base, w, point, curve=0, single=False):
    out, span = set(), max(base - tip, 1)
    for y in range(tip, base + 1):
        t = y - tip
        ww = w if t >= point else max(1, round(w * (t + 1) / (point + 1)))
        x0 = cx - w // 2 + round(curve * ((base - y) / span) ** 2)
        if not single:
            x0 += (w - ww) // 2
        out |= {(x, y) for x in range(x0, x0 + ww)}
    return out


def edge(pix, side=-1):
    """Leftmost (side -1) or rightmost (+1) pixel of each row."""
    rows = {}
    for x, y in pix:
        rows.setdefault(y, []).append(x)
    return {((min if side < 0 else max)(xs), y) for y, xs in rows.items()}


def outline(pix):
    return {(x, y) for x, y in pix if any(q not in pix for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))}


# ---- one weapon ---------------------------------------------------------------------------------------------------
class W:
    def __init__(s, it):
        s.it, s.code, s.lvl, s.nm = it, it["code"], LEVEL[it["rarity"]], it["name"].lower()
        s.n = 64 if s.code in LONG else 32
        s.cx = s.n // 2
        s.rng = random.Random(zlib.crc32(it["id"].encode()))
        words = it["name"].replace("-", " ").replace("'", " ").split()
        s.main, s.trim, s.grip = next((m, t, g) for keys, m, t, g in THEMES + [("", "steel", "darksteel", "leather")]
                                      if not keys or any(k in w for k in keys.split() for w in words))
        if s.lvl == 1 and s.trim in ("darksteel", "rust", "steel"):
            s.trim = "copper"
        if s.lvl >= 3 and s.trim in ("darksteel", "rust", "steel", "copper"):
            s.trim = "gold"
        s.furn = "wood" if s.grip == "leather" else s.grip
        s.acc = ELEM.get(it["element"])
        s.glow = 10 if s.acc and s.acc != "iron" and s.lvl >= 2 else 0
        s.gem = "lens" if s.lvl == 4 else (s.acc or ("amethyst" if s.lvl == 3 else "garnet")) if s.lvl >= 2 else None
        s.gemglow = 12 if s.lvl == 4 else s.glow
        s.wear = (0.12, 0.08, 0.05, 0.03, 0.02)[s.lvl]
        s.parts, s.own = [], {}

    def has(s, *words): return any(w in s.nm for w in words)

    def add(s, pix, mat, t, style="flat", glow=0):
        i = len(s.parts)
        s.parts.append(dict(mat=mat, t=t, style=style, glow=glow, pix=set()))
        for p in pix:
            if 0 <= p[0] < s.n and 0 <= p[1] < s.n:
                if p in s.own:
                    s.parts[s.own[p]]["pix"].discard(p)
                s.own[p] = i
                s.parts[i]["pix"].add(p)

    def gemat(s, x, y, size=2, t=4):
        if s.gem:
            pix = poly(s.n, [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]) if size > 2 else \
                rect(x - 1, y - 1, x, y)
            s.add(pix, s.gem, t, "glow" if s.gemglow else "flat", s.gemglow)

    def accent(s, pix, t):
        if s.acc:
            s.add(pix, s.acc, t, "glow" if s.glow else "flat", s.glow)


# ---- melee --------------------------------------------------------------------------------------------------------
def blade_part(w, cx, tip, base, bw, point, curve=0, single=False):
    pix = blade(cx, tip, base, bw, point, curve, single)
    w.add(pix, w.main, 2, "bevel")
    if w.lvl >= 1 and bw >= 4 and not curve:
        w.add(bar(cx, tip + point + 2, base - 2, 2), w.main, 1, "groove")
    if w.acc and w.lvl >= 2:
        w.accent(edge(pix, -1 if not single else 1), 2)
    return pix


def hilt(w, y, gw, glen, style="bar", gh=2, pw=None):
    n, cx = w.n, w.cx
    if style == "disc":
        g = oval(n, (cx - gw // 2, y - 1, cx + gw // 2 - 1, y + gh))
    else:
        g = bar(cx, y, y + gh - 1, gw)
        lx, rx = cx - gw // 2, cx + gw // 2 - 1
        if style == "up":
            g |= rect(lx, y - 2, lx, y - 1) | rect(rx, y - 2, rx, y - 1)
        if style == "wing":
            wing = poly(n, [(lx, y - 5), (cx - 2, y), (lx + 2, y + gh - 1)])
            g |= wing | mirx(wing, cx)
    w.add(g, w.trim, 3)
    w.add(bar(cx, y + gh, y + gh + glen - 1, 2), w.grip, 2, "wrap")
    pe = y + gh + glen
    w.add(bar(cx, pe, pe + 1, pw or (4 if w.lvl >= 1 else 2)), w.trim, 3)
    w.gemat(cx, y + gh // 2, 3 if w.lvl == 4 else 2, 4)
    return cx, y + gh + glen / 2


def sts(w):
    r, cx = w.rng, w.cx
    gy, bw = 22, 6 if w.lvl >= 3 else 4
    blade_part(w, cx, r.randint(1, 3), gy - 1, bw, r.randint(3, 5))
    if w.has("light"):  # Ostra's Last Light: a Shard core down the blade
        w.add(bar(cx, 8, gy - 3, 2), "lens", 2, "glow", 12)
    return hilt(w, gy, r.choice((8, 10)) + 2 * (w.lvl >= 3), r.choice((5, 6)), "wing" if w.lvl == 4 else r.choice(("bar", "up")))


def crv(w):
    r, cx = w.rng, w.cx
    gy = 22
    pix = blade_part(w, cx - 1, r.randint(2, 4), gy - 1, r.choice((3, 4)), 4, r.choice((3, 4, 5)), True)
    if w.has("hymn", "choir"):
        w.accent({p for p in pix if (p[0] + p[1]) % 5 == 0}, 3)
    g = hilt(w, gy, r.choice((6, 8)), 6, "bar")
    if w.has("saber", "duelist", "hymn") or w.lvl >= 3:
        w.add(rect(cx + 3, gy + 1, cx + 3, gy + 7) | rect(cx + 1, gy + 8, cx + 3, gy + 8), w.trim, 2)
    return g


def dgr(w):
    r, cx = w.rng, w.cx
    thin = w.has("stiletto", "scalpel", "splinter")
    gy = 19
    blade_part(w, cx, r.randint(5, 9), gy - 1, 2 if thin else r.choice((3, 4)), 2 if thin else 3)
    return hilt(w, gy, r.choice((6, 8)), 5, "disc" if w.has("rondel") else "wing" if w.lvl == 4 else "bar")


def grs(w):
    r, cx, n = w.rng, w.cx, w.n
    gy, bw, tip = 44, r.choice((6, 8)), r.randint(2, 5)
    if w.has("monolith", "bulkhead"):
        w.add(bar(cx, tip, gy - 1, bw + 2), w.main, 3, "bevel")
        w.add({(cx - bw // 2, y) for y in range(tip + 3, gy - 2, 5)} | {(cx + bw // 2 - 1, y) for y in range(tip + 3, gy - 2, 5)},
              w.trim, 4)
        if w.acc:
            w.accent(bar(cx, tip + 4, gy - 4, 2), 3)
    elif w.has("keel"):
        lx = cx - bw // 2
        w.add(poly(n, [(lx, tip), (lx + 3, tip), (cx + bw // 2 + 3, tip + 14), (cx + bw // 2, gy - 1), (lx, gy - 1)]),
              w.main, 3, "bevel")
        w.add({(lx + 1, y) for y in range(tip + 4, gy - 2, 4)}, w.trim, 4)
    else:
        blade_part(w, cx, tip, gy - 1, bw, 6)
    return hilt(w, gy, r.choice((14, 16, 18)), 9, "wing" if w.lvl >= 3 else "up", 3, 6)


def twb(w):
    r, cx, n = w.rng, w.cx, w.n
    bw, top = r.choice((4, 6)), 27
    up = blade(cx, r.randint(3, 8), top - 2, bw, 5, 2 if w.has("rotor", "gyre") else 0, w.has("rotor", "gyre"))
    down = miry(blade(cx, r.randint(3, 8), top - 2, bw, 5, 2 if w.has("rotor", "gyre") else 0, w.has("rotor", "gyre")), n)
    if w.has("rotor", "gyre"):
        down = mirx(down, cx)
    w.add(up | down, w.main, 2, "bevel")
    if w.acc and w.lvl >= 1:
        w.accent(edge(up) | edge(down, 1), 2)
    gw = r.choice((8, 10))
    guards = bar(cx, top - 1, top, gw) | bar(cx, n - top - 1, n - top, gw)
    if w.has("sun", "gyre", "orbit"):
        sun = ring(n, (cx - 10, top - 14, cx + 9, top + 5), 3)
        w.add(sun | miry(sun, n), w.acc or w.trim, 3, "glow" if w.glow else "flat", w.glow)
    w.add(guards, w.trim, 3)
    w.add(bar(cx, top + 1, n - top - 2, 2), w.grip, 2, "wrap")
    w.gemat(cx, n // 2, 3 if w.lvl == 4 else 2, 4)
    return cx, n / 2


def haft(w, y0, y1, g0, g1, t=2):
    w.add(bar(w.cx, y0, y1, 2), w.furn if w.main != "ceramic" else "darksteel", t)
    w.add(bar(w.cx, g0, g1, 2), w.grip, t + 1, "wrap")


def axe_head(w, cx, y, k, double):
    n = w.n
    if w.has("rime", "frost"):
        head = poly(n, [(cx - 1, y), (cx - 6 * k, y - 2 * k), (cx - 12 * k, y + 4 * k), (cx - 8 * k, y + 6 * k),
                        (cx - 12 * k, y + 10 * k), (cx - 5 * k, y + 12 * k), (cx - 1, y + 9 * k)])
    else:
        head = poly(n, [(cx - 1, y + k), (cx - 5 * k, y + k), (cx - 9 * k, y - k), (cx - 11 * k, y + 5 * k),
                        (cx - 9 * k, y + 12 * k), (cx - 5 * k, y + 9 * k), (cx - 1, y + 9 * k)])
    if double:
        head |= mirx(head, cx)
    w.add(head, w.main, 2, "bevel")
    if w.acc and w.lvl >= 2:
        w.accent(edge(head), 3)
    w.add(bar(cx, y, y + 9 * k, 4), w.trim, 4)
    if not double and w.lvl >= 3:
        w.add(poly(n, [(cx + 1, y + 3 * k), (cx + 6 * k, y + 5 * k), (cx + 1, y + 7 * k)]), w.trim, 3)
    w.gemat(cx, y + 4 * k, 2, 5)


def axe(w):
    haft(w, 2, 30, 23, 29)
    axe_head(w, w.cx, 3, 1, w.has("battleaxe"))
    return w.cx, 26


def gax(w):
    haft(w, 4, 62, 44, 58)
    axe_head(w, w.cx, 6, 2, w.has("castellan", "wreck") or w.rng.random() < 0.4)
    return w.cx, 51


def hammer_head(w, cx, y, s):
    n = w.n
    if w.has("star"):
        w.add(oval(n, (cx - 6 * s, y, cx + 5 * s, y + 11 * s)), w.main, 5)
        spikes = set()
        for a in range(0, 360, 45):
            px, py = cx - 0.5 + 7.5 * s * math.cos(math.radians(a)), y + 5.5 * s + 7.5 * s * math.sin(math.radians(a))
            spikes |= rect(round(px) - (s > 1), round(py) - (s > 1), round(px), round(py))
        w.add(spikes, w.trim, 3)
    elif w.has("anchor"):
        w.add(bar(cx, y, y + 12 * s, 2 * s), w.main, 4)
        w.add(bar(cx, y + s, y + 2 * s, 10 * s), w.main, 4)
        arc = {p for p in ring(n, (cx - 7 * s, y + 3 * s, cx + 6 * s, y + 14 * s), 2 * s) if p[1] > y + 9 * s}
        w.add(arc | poly(n, [(cx - 8 * s, y + 7 * s), (cx - 5 * s, y + 10 * s), (cx - 8 * s, y + 11 * s)]) |
              poly(n, [(cx + 7 * s, y + 7 * s), (cx + 4 * s, y + 10 * s), (cx + 7 * s, y + 11 * s)]), w.main, 4, "bevel")
    elif w.has("boulder"):
        w.add(oval(n, (cx - 9 * s, y, cx + 8 * s, y + 10 * s)), "stone", 6)
    else:
        mat = "wood" if w.has("mallet") else w.main
        hw, hh = (6 + w.rng.randint(0, 2)) * s, (4 + w.rng.randint(0, 1)) * s
        w.add(poly(n, [(cx - hw + s, y), (cx + hw - 1 - s, y), (cx + hw - 1, y + s), (cx + hw - 1, y + 2 * hh - s),
                       (cx + hw - 1 - s, y + 2 * hh), (cx - hw + s, y + 2 * hh), (cx - hw, y + 2 * hh - s), (cx - hw, y + s)]),
              mat, 5 * min(s, 2) - 1 if s > 1 else 5)
        w.add(rect(cx - hw, y + hh - 1, cx - hw + s, y + hh) | rect(cx + hw - 1 - s, y + hh - 1, cx + hw - 1, y + hh),
              w.trim, 6 if s == 1 else 9)
        if w.has("grave", "well"):
            w.add(oval(n, (cx - 3 * s, y + hh - 3 * s, cx + 2 * s, y + hh + 2 * s)), "hollow", 6, "glow", 8)
        elif w.acc:
            w.accent(bar(cx, y + 2, y + 2 * hh - 2, 2 * s), 6)
    w.gemat(cx, y + 5 * s, 2, 7)


def hmr(w):
    haft(w, 8, 30, 22, 29)
    hammer_head(w, w.cx, 1, 1)
    return w.cx, 26


def ghm(w):
    haft(w, 10, 62, 46, 58)
    hammer_head(w, w.cx, 2, 2)
    return w.cx, 52


def pol(w):
    n, cx, r = w.n, w.cx, w.rng
    haft(w, 10, 62, 38, 50)
    w.add(bar(cx, 61, 63, 4), w.trim, 3)
    if w.has("anchor"):
        hammer_head(w, cx, 0, 2)
        w.add({p for y in range(28, 38, 3) for p in bar(cx, y, y + 1, 4)}, w.trim, 3)
        return cx, 44
    kind = "fork" if w.has("fork") else "halberd" if w.has("halberd") else "poleaxe" if w.has("poleaxe") else \
        r.choice(("spear", "spear", "halberd")) if w.lvl >= 2 else "spear"
    if kind == "fork":
        w.add(blade(cx - 7, 1, 15, 2, 3) | blade(cx + 7, 1, 15, 2, 3) | blade(cx, 0, 15, 2, 3), w.main, 2, "bevel")
        w.add(bar(cx, 15, 17, 18), w.trim, 3)
    else:
        tip = blade(cx, 0, 17 if kind == "spear" else 11, 6 if kind == "spear" else 4, 8 if kind == "spear" else 5)
        w.add(tip, w.main, 2, "bevel")
        if kind in ("halberd", "poleaxe"):
            ax = poly(n, [(cx - 1, 11), (cx - 12, 7), (cx - 15, 16), (cx - 12, 26), (cx - 1, 21)])
            back = poly(n, [(cx + 1, 12), (cx + 10, 10), (cx + 4, 17), (cx + 1, 17)]) if kind == "halberd" else rect(cx + 1, 13, cx + 7, 20)
            w.add(ax, w.main, 2, "bevel")
            w.add(back, w.main if kind == "halberd" else w.trim, 3)
            if w.acc and w.lvl >= 2:
                w.accent(edge(ax), 3)
        elif w.acc and w.lvl >= 2:
            w.accent(edge(tip), 3)
        w.add(bar(cx, 17 if kind == "spear" else 22, 20 if kind == "spear" else 25, 4), w.trim, 3)
    w.gemat(cx, 19, 2, 5)
    return cx, 44


def fst(w, shard=False):
    n = w.n
    mat = "leather" if w.has("wrapped") else w.main
    w.add(rect(10, 21, 21, 30), mat, 4, "wrap" if mat == "leather" else "flat")
    w.add(rect(10, 21, 21, 22), w.trim, 5)
    w.add(rect(9, 10, 22, 20) - {(9, 10), (22, 10), (9, 20), (22, 20)}, mat, 5)
    for i, x in enumerate((10, 13, 16, 19)):
        w.add(rect(x, 3 + (i in (0, 3)), x + 2, 10), mat, 4)
    w.add(rect(6, 12, 8, 17), mat, 4)
    w.add(rect(10, 9, 21, 10), w.trim, 6)
    if w.has("clan", "castellan", "thorn") or w.lvl >= 3:
        spikes = {(x, y) for x in (11, 14, 17, 20) for y in (7, 8)}
        if w.has("thorn"):
            spikes |= {(x, y) for x, y in outline(rect(9, 10, 22, 20)) if (x * 3 + y) % 4 == 0}
        w.add(spikes, w.acc or w.trim if w.has("thorn") else w.trim, 7, "glow" if w.has("thorn") and w.glow else "flat",
              w.glow if w.has("thorn") else 0)
    if shard:
        w.add(poly(n, [(15.5, 11), (19, 15), (15.5, 19), (12, 15)]), "lens", 7, "glow", 12)
        w.add({p for y in (24, 27) for p in rect(10, y, 21, y)}, w.acc or "lens", 5, "glow", w.glow or 10)
    elif w.acc and w.lvl >= 1:
        w.accent(rect(12, 13, 19, 14), 6)
    w.gemat(15, 25, 2, 6)
    return 15.5, 17


def shd(w):
    n, r = w.n, w.rng
    kind = "round" if w.has("buckler", "hatch") else "heater" if w.has("heater") else \
        "pavise" if w.has("pavise", "barrier", "plate", "door") else r.choice(("heater", "round", "pavise"))
    if kind == "round":
        body = oval(n, (8, 8, 23, 23)) if w.has("buckler") else oval(n, (4, 4, 27, 27))
    elif kind == "heater":
        body = poly(n, [(5, 2), (26, 2), (26, 15), (15.5, 30), (5, 15)])
    else:
        body = rect(7, 1, 24, 30) - {(7, 1), (24, 1), (7, 2), (24, 2), (8, 1), (23, 1)}
    w.add(body, w.main, 2)
    w.add(outline(body), w.trim, 3)
    if w.has("hatch"):
        wheel = ring(n, (9, 9, 22, 22), 1) | line(n, [(10, 10), (21, 21)]) | line(n, [(21, 10), (10, 21)]) | \
            rect(15, 9, 16, 22) | rect(9, 15, 22, 16)
        w.add(wheel, w.trim, 4)
        w.add(oval(n, (13, 13, 18, 18)), w.trim, 6)
    else:
        if w.lvl >= 2:
            w.add(rect(15, 5, 16, 26) | rect(9, 11, 22, 12), w.trim, 3)
        w.add(oval(n, (12, 12, 19, 19)), w.trim, 5)
        if w.acc:
            w.accent(oval(n, (14, 14, 17, 17)), 6)
    w.gemat(15, 15, 2, 7)
    return 15.5, 15.5


def stf(w):
    n, cx = w.n, w.cx
    w.add(bar(cx, 14, 62, 2), w.furn, 2)
    w.add(bar(cx, 38, 48, 2), w.grip, 3, "wrap")
    w.add(bar(cx, 61, 63, 4), w.trim, 3)
    if w.has("lens"):
        w.add(ring(n, (cx - 10, 0, cx + 9, 19), 2), w.trim, 4)
        w.add(oval(n, (cx - 8, 2, cx + 7, 17)), "lens", 2, "glow", 12)
        w.add(bar(cx, 18, 22, 4), w.trim, 4)
        return cx, 43
    claw = line(n, [(cx - 1, 15), (cx - 6, 10), (cx - 6, 4), (cx - 3, 1)], 2)
    w.add(claw | mirx(claw, cx), w.trim, 3)
    focus = w.acc or ("lens" if w.lvl == 4 else "choirglass")
    w.add(oval(n, (cx - 4, 4, cx + 3, 11)), focus, 4, "glow", w.glow or (12 if focus == "lens" else 6))
    if w.has("thorn", "bloom"):
        w.add({(x, y) for x, y in outline(bar(cx, 16, 36, 4)) if (x + y) % 5 == 0}, "bloom", 3)
    w.add(bar(cx, 12, 15, 4), w.trim, 4)
    return cx, 43


def seal(w):
    n, cx = w.n, w.cx
    if w.has("fork"):
        w.add(bar(cx - 4, 2, 15, 2) | bar(cx + 4, 2, 15, 2) | bar(cx, 14, 16, 10), w.main, 2, "bevel")
        w.add(bar(cx, 17, 30, 2), w.grip, 2, "wrap")
    elif w.has("censer"):
        w.add(oval(n, (12, 7, 19, 14)), "ember", 3, "glow", 10)
        w.add(ring(n, (9, 4, 22, 17), 1) | rect(15, 4, 16, 17), w.trim, 4)
        w.add(rect(15, 18, 16, 30) - {(15, y) for y in range(19, 30, 2)}, w.trim, 1)
    elif w.has("reliquary"):
        w.add(rect(9, 4, 22, 18), w.main, 4)
        w.add(rect(12, 7, 19, 14), w.acc or "choirglass", 5, "glow", w.glow or 6)
        w.add(outline(rect(9, 4, 22, 18)), w.trim, 5)
        w.add(bar(cx, 19, 30, 2), w.grip, 2, "wrap")
    else:
        disc = oval(n, (7, 3, 24, 20))
        w.add(disc, w.main, 3)
        w.add(ring(n, (9, 5, 22, 18), 1), w.trim, 4)
        w.add(poly(n, [(15.5, 7), (19, 11.5), (15.5, 16), (12, 11.5)]), w.acc or w.trim, 4,
              "glow" if w.glow else "flat", w.glow)
        w.add(bar(cx, 21, 29, 2), w.grip, 2, "wrap")
        w.add(bar(cx, 30, 31, 4), w.trim, 3)
    w.gemat(cx, 25, 2, 4)
    return cx, 25


# ---- firearms (side view, muzzle to the right) --------------------------------------------------------------------
def cell(w, box, t):
    if w.acc:
        w.accent(rect(*box), t)


def pst(w):
    n, r = w.n, w.rng
    lb = -3 if w.has("snub") else r.randint(0, 3)
    if w.has("magnum", "cannon", "word"):
        w.add(rect(7, 11, 13, 15), w.main, 4)
        w.add(rect(19, 10, 26 + lb, 12), w.main, 3, "bevel")
        w.add(oval(n, (12, 9, 19, 16)), w.trim, 6)
        w.add(rect(7, 9, 8, 10), "darksteel", 2)
    else:
        w.add(rect(7, 10, 22 + lb, 15), w.main, 4)
        w.add(rect(22 + lb, 11, 24 + lb, 13), "darksteel", 2)
        w.add({(x, 11) for x in range(15, 21 + lb, 2)}, "darksteel", 5)
    w.add(poly(n, [(8, 15), (13, 15), (12, 25), (6, 25)]), w.furn, 4)
    w.add(rect(13, 16, 17, 16) | rect(17, 16, 17, 19) | rect(13, 19, 17, 19), w.trim, 2)
    w.add({(21 + lb, 9)}, "darksteel", 2)
    cell(w, (14, 13, 18, 14), 5)
    w.gemat(10, 20, 2, 5)
    return 9.5, 20


def smg(w):
    n = w.n
    w.add(rect(5, 11, 23, 17), w.main, 4)
    w.add(rect(23, 12, 29 + 2 * w.has("wasp"), 14), "darksteel", 3)
    w.add(oval(n, (13, 17, 22, 26)) if w.has("hive") else rect(16, 18, 19, 28), "darksteel", 5 if w.has("hive") else 3)
    w.add(poly(n, [(8, 17), (12, 17), (11, 25), (7, 25)]), w.furn, 4)
    w.add(rect(0, 12, 5, 13) | rect(0, 13, 1, 17), w.trim, 2)
    w.add(rect(8, 9, 10, 10), "darksteel", 2)
    cell(w, (11, 13, 21, 14), 5)
    w.gemat(14, 15, 2, 5)
    return 9.5, 21


RIFLE = {  # receiver box, barrel end, barrel rows, stock?, mag box, grip x
    "ARF": dict(recv=(16, 24, 40, 33), bend=58, brow=(27, 29), mag=(30, 34, 35, 46), guard=(40, 24, 52, 32)),
    "SCT": dict(recv=(16, 24, 38, 32), bend=61, brow=(27, 28), mag=(30, 33, 34, 41), guard=(38, 25, 50, 31), scope=(20, 17, 38, 21)),
    "SNP": dict(recv=(14, 24, 36, 32), bend=63, brow=(27, 28), mag=(28, 33, 32, 39), guard=(36, 25, 46, 31), scope=(16, 15, 40, 21)),
    "SHG": dict(recv=(16, 24, 36, 33), bend=62, brow=(24, 27), guard=(42, 28, 52, 32)),
}


def rifle(w):
    n, r = w.n, w.rng
    s = dict(RIFLE[w.code], bend=min(63, RIFLE[w.code]["bend"] + r.randint(-5, 0)))
    if "mag" in s:
        mx0, my0, mx1, my1 = s["mag"]
        s["mag"] = (mx0, my0, mx1, my1 + r.randint(-3, 2))
    x0, y0, x1, y1 = s["recv"]
    w.add(rect(*s["recv"]), w.main, 4)
    w.add(rect(x1, s["brow"][0], s["bend"], s["brow"][1]), "darksteel", 3 if w.code == "SHG" else 2)
    if w.code == "SHG":
        w.add(rect(x1, 28, s["bend"] - 4, 30), "darksteel", 2)
    w.add(rect(*s["guard"]), w.furn if w.code == "SHG" else w.main, 4 if w.code == "SHG" else 3)
    if "mag" in s:
        mx0, my0, mx1, my1 = s["mag"]
        w.add(poly(n, [(mx0, my0), (mx1, my0), (mx1 + 3, my1), (mx0 + 3, my1)]), "darksteel", 3)
    if "scope" in s:
        sx0, sy0, sx1, sy1 = s["scope"]
        w.add(rect(sx0 + 2, sy0 + 1, sx1 - 2, sy1 - 1) | rect(sx0, sy0, sx0 + 2, sy1) | rect(sx1 - 2, sy0, sx1, sy1),
              "darksteel", 4)
        w.add(rect(sx1 - 3, sy0 + 1, sx1 - 3, sy1 - 1), w.acc if w.glow else "choirglass", 5, "glow", w.glow or 4)
        w.add(rect((sx0 + sx1) // 2 - 1, sy1 + 1, (sx0 + sx1) // 2 + 1, y0 - 1), "darksteel", 2)
    else:
        w.add(rect(x0 + 4, y0 - 4, x0 + 12, y0 - 1) - rect(x0 + 6, y0 - 3, x0 + 10, y0 - 1), w.trim, 2)
    w.add(poly(n, [(x0 + 3, y1), (x0 + 8, y1), (x0 + 7, y1 + 11), (x0 + 2, y1 + 11)]), w.furn, 4)
    if r.random() < 0.4 and w.code != "SHG":  # skeleton stock
        w.add(rect(2, y0 + 1, x0, y0 + 2) | rect(2, y1 + 1, x0 - 2, y1 + 2) | rect(1, y0 + 1, 3, y1 + 4), w.trim, 2)
    else:
        w.add(poly(n, [(1, y0 + 1), (x0, y0), (x0, y1 - 1), (4, y1 + 4), (1, y1 + 4)]), w.furn, 3)
    if w.lvl >= 2:
        e = s["bend"]
        w.add(rect(e - 3, s["brow"][0] - 1, e, s["brow"][1] + 1), "darksteel", 4)
    if w.code == "SNP":
        w.add(rect(x1 - 2, y1, x1, y1 + 2), w.trim, 5)
        if w.has("silence"):
            w.add(rect(52, 25, 63, 30), "quiet", 5)
        if w.lvl >= 3:
            w.add(line(n, [(46, 30), (42, 41)]) | line(n, [(46, 30), (50, 41)]), "darksteel", 2)
    if w.has("reactor"):
        w.add(rect(x0 + 10, y0 + 2, x1 - 6, y1 - 2), w.trim, 5)
        w.add(rect(x0 + 12, y0 + 3, x1 - 8, y1 - 3), "ember", 6, "glow", 12)
    else:
        cell(w, (x0 + 10, y0 + 3, x1 - 6, y0 + 4), 5)
    if w.lvl >= 3:
        w.add(rect(x0, y0, x1, y0), w.trim, 5)
    w.gemat(x0 + 6, y0 + 4, 2, 6)
    return x0 + 5, y1 + 6


def lch(w):
    n = w.n
    if w.has("rain"):
        w.add(rect(10, 20, 56, 23) | rect(10, 25, 56, 28) | rect(10, 30, 56, 33), w.main, 5)
    else:
        w.add(rect(10, 21, 56, 33) - {(10, 21), (56, 21), (10, 33), (56, 33)}, w.main, 6)
    w.add(rect(10, 20, 13, 34) | rect(52, 20, 55, 34), w.trim, 7)
    if w.has("hopper"):
        w.add(oval(n, (18, 8, 31, 21)), "darksteel", 5)
    if w.has("mooring", "harpoon"):
        w.add(poly(n, [(56, 24), (63, 27), (56, 30)]), "steel", 3, "bevel")
    w.add(rect(26, 34, 30, 44), w.furn, 4)
    w.add(rect(40, 34, 43, 41), w.furn, 4)
    w.add(rect(30, 16, 36, 20), "darksteel", 3)
    cell(w, (16, 26, 48, 27), 7)
    w.gemat(20, 27, 2, 8)
    return 28, 39


def lnc(w):
    n = w.n
    w.add(rect(12, 25, 42, 33), w.main, 4)
    prong = poly(n, [(42, 25), (60, 21), (62, 23), (44, 28)])
    prongs = prong | miry(prong, 58)
    if w.has("crown"):
        prongs |= rect(42, 28, 58, 30)
    w.add(prongs, w.trim, 3, "bevel")
    w.add(poly(n, [(53, 25.5), (58, 29), (53, 32.5), (48, 29)]), "lens", 4, "glow", 12)
    w.add({p for x in (20, 25, 30, 35) for p in rect(x, 24, x + 1, 34)}, w.acc or "lens", 6, "glow", w.glow or 10)
    w.add(poly(n, [(16, 33), (21, 33), (20, 43), (15, 43)]), w.furn, 4)
    w.add(poly(n, [(2, 26), (12, 25), (12, 32), (2, 34)]), w.furn, 3)
    w.gemat(16, 29, 2, 6)
    return 18, 38


BUILD = {"STS": sts, "CRV": crv, "DGR": dgr, "GRS": grs, "TWB": twb, "AXE": axe, "GAX": gax, "HMR": hmr, "GHM": ghm,
         "POL": pol, "FST": fst, "SGT": lambda w: fst(w, True), "SHD": shd, "STF": stf, "SEAL": seal, "PST": pst,
         "SMG": smg, "ARF": rifle, "SCT": rifle, "SNP": rifle, "SHG": rifle, "LCH": lch, "LNC": lnc}
HOLD = {  # our rotations; translations are solved so the grip lands where a vanilla sword's grip lands
    "blade": ([0, -90, 10], [0, -90, -20], 1.0), "gun": ([0, -90, 0], [0, -90, 5], 0.6),
    "fist": ([0, -90, -90], [0, -90, -90], 0.8), "shield": ([0, 0, 0], [0, 10, 0], 0.8)}
VANILLA = {"thirdperson_righthand": ([0, -90, 55], [0, 4, 0.5], 0.85),
           "firstperson_righthand": ([0, -90, 25], [1.13, 3.2, 1.13], 0.68)}
VANILLA_GRIP = (3, 3, 8)


# ---- texture, elements, display -----------------------------------------------------------------------------------
def texture(w):
    img = Image.new("RGBA", (w.n, w.n))
    for p in w.parts:
        pix, rp, style = p["pix"], RAMP[p["mat"]], p["style"]
        rows = {}
        for x, y in pix:
            rows.setdefault(y, []).append(x)
        for x, y in pix:
            if style == "glow":
                k = 4 if all(q in pix for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))) else 3
            elif style == "wrap":
                k = 3 if (x + y) % 3 == 0 else 1
            elif style == "bevel":
                xs = rows[y]
                k = 4 if x == min(xs) else 1 if x == max(xs) else 3 if x < (min(xs) + max(xs)) / 2 else 2
            else:
                k = STYLE_SHADE.get(style, 2)
                if (x, y - 1) not in pix or (x - 1, y) not in pix:
                    k = 3
                elif (x, y + 1) not in pix or (x + 1, y) not in pix:
                    k = 1
            if style != "glow":
                if (x + 1, y) not in w.own or (x, y + 1) not in w.own:
                    k = 0
                roll = w.rng.random()
                k = max(0, k - 1) if roll < w.wear else min(4, k + 1) if roll > 0.97 else k
            img.putpixel((x, y), rp[k])
    return img


def rects(pix):
    rows = {}
    for x, y in pix:
        rows.setdefault(y, []).append(x)
    runs = []
    for y in sorted(rows):
        xs = sorted(rows[y])
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == prev + 1:
                prev = x
                continue
            runs.append((start, prev, y))
            if x is not None:
                start = prev = x
    live, out = {}, []
    for x0, x1, y in runs:
        r = live.get((x0, x1))
        if r and r[3] == y - 1:
            r[3] = y
        else:
            if r:
                out.append(r)
            live[(x0, x1)] = [x0, x1, y, y]
    return out + list(live.values())


def elements(w, o):
    f, n, out = 16 / w.n, w.n, []
    uv = lambda a, b, c, d: [round(v * f, 4) for v in (a, b, c, d)]
    for p in w.parts:
        t = p["t"]
        for x0, x1, y0, y1 in rects(p["pix"]):
            faces = {"north": uv(x1 + 1, y0, x0, y1 + 1), "east": uv(x1, y0, x1 + 1, y1 + 1),
                     "south": uv(x0, y0, x1 + 1, y1 + 1), "west": uv(x0, y0, x0 + 1, y1 + 1),
                     "up": uv(x0, y0, x1 + 1, y0 + 1), "down": uv(x0, y1, x1 + 1, y1 + 1)}
            e = {"from": [x0 / 2 + o, (n - 1 - y1) / 2 + o, 8 - t / 4], "to": [(x1 + 1) / 2 + o, (n - y0) / 2 + o, 8 + t / 4],
                 "faces": {k: {"uv": v, "texture": "#0"} for k, v in faces.items()}}
            if p["glow"]:
                e["light_emission"] = p["glow"]
            out.append(e)
    return out


def rot(rx, ry, rz):
    def m(a, axis):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        return {"x": [[1, 0, 0], [0, c, -s], [0, s, c]], "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]],
                "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis]
    mul = lambda A, B: [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mul(mul(m(rx, "x"), m(ry, "y")), m(rz, "z"))


def apply(M, v): return [sum(M[i][k] * v[k] for k in range(3)) for i in range(3)]


def solve(rotation, scale, point, target):
    """Translation that puts model point `point` at `target` (minus the vanilla offset) after rotate+scale."""
    p = apply(rot(*rotation), [scale * (c - 8) for c in point])
    return [round(t - q, 3) for t, q in zip(target, p)]


def display(w, els, grip, kind):
    third, first, gs = HOLD[kind]
    d = {}
    for slot, ours in (("thirdperson_righthand", third), ("firstperson_righthand", first)):
        vr, vt, vs = VANILLA[slot]
        target = [a + b for a, b in zip(vt, apply(rot(*vr), [vs * (c - 8) for c in VANILLA_GRIP]))]
        s = round(vs * gs, 3)
        d[slot] = {"rotation": ours, "translation": [max(-80, min(80, v)) for v in solve(ours, s, grip, target)],
                   "scale": [s] * 3}
    lo = [min(e["from"][i] for e in els) for i in range(3)]
    hi = [max(e["to"][i] for e in els) for i in range(3)]
    center = [(a + b) / 2 for a, b in zip(lo, hi)]
    for slot, r, k in (("gui", [0, 0, -45 if kind != "shield" else 0], 1.0), ("fixed", [0, 180, 45 if kind != "shield" else 0], 1.0),
                       ("ground", [0, 0, -45 if kind != "shield" else 0], 0.5)):
        M = rot(*r)
        corners = [apply(M, [(hi[i] if (c >> i) & 1 else lo[i]) - 8 for i in range(3)]) for c in range(8)]
        ext = max(max(c[i] for c in corners) - min(c[i] for c in corners) for i in (0, 1))
        s = round(min(1.6, 15.5 / ext) * k, 3)
        d[slot] = {"rotation": r, "translation": solve(r, s, center, [0, 0, 0]), "scale": [s] * 3}
    return d


def kind_of(code):
    return "gun" if code in GUNS else "fist" if code in ("FST", "SGT") else "shield" if code == "SHD" else "blade"


# ---- data ---------------------------------------------------------------------------------------------------------
def rows(name):
    with open(ITEMS / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def slug(itm): return itm.removeprefix("ITM_").lower()  # matches convert.py item_id() after "shardfall:"


def load():
    code = {r["name"]: r["class_id"].removeprefix("ITM_CLS_") for r in rows("melee_classes.csv") + rows("firearm_classes.csv")}
    code["Catalyst"] = "STF"
    cat = {"Staff": "STF", "Seal": "SEAL", "Shard Gauntlet": "SGT"}
    out = []
    for r in rows("weapons_melee.csv"):
        out.append(dict(id=r["item_id"], name=r["name"], code=code[r["weapon_class"]], cls=r["weapon_class"], rarity=r["rarity"],
                        element=r["element"], group="Melee", registered="yes"))
    for r in rows("weapons_firearm.csv"):
        out.append(dict(id=r["item_id"], name=r["name"], code=code[r["weapon_class"]], cls=r["weapon_class"], rarity=r["rarity"],
                        element=r["damage_type"], group="Firearms", registered="no (guns not converted yet)"))
    for r in rows("shardborn.csv"):
        if r["kind"] == "weapon":
            c = code[r["slot_or_class"]]
            out.append(dict(id=r["item_id"], name=r["name"], code=c, cls=r["slot_or_class"], rarity="Shardborn",
                            element=r["element"], group="Shardborn",
                            registered="yes" if c not in GUNS and c != "STF" else "no (convert.py skips this class)"))
    for r in rows("catalysts.csv"):
        out.append(dict(id=r["item_id"], name=r["name"], code=cat[r["catalyst_type"]], cls=r["catalyst_type"], rarity=r["rarity"],
                        element="", group="Catalysts", registered="no (catalysts not converted yet)"))
    for r in rows("arena_power_weapons.csv"):
        out.append(dict(id=r["item_id"], name=r["name"], code=code[r["base_class"]], cls=r["base_class"], rarity="Arena",
                        element="", group="Arena", registered="no (arena weapons not converted yet)"))
    return out


# ---- contact sheet ------------------------------------------------------------------------------------------------
def preview(w, img, k):
    depth = {}
    for p in w.parts:
        for q in p["pix"]:
            depth[q] = p["t"]
    a = k * 0.45
    pad = round(4 * a) + 2
    out = Image.new("RGBA", (w.n * k + 2 * pad, w.n * k + 2 * pad))
    d = ImageDraw.Draw(out)
    src = img.load()
    for z2 in range(-9, 10):  # half-pixel depth layers, back to front
        z = z2 / 2
        for (x, y), t in depth.items():
            if -t / 2 <= z <= t / 2:
                c = src[x, y]
                if z < t / 2:
                    c = tuple(round(v * 0.55) for v in c[:3]) + (255,)
                ox, oy = pad + x * k - z * a, pad + y * k + z * a
                d.rectangle([round(ox), round(oy), round(ox) + k - 1, round(oy) + k - 1], fill=c)
    return out


def sheet(items, title, path):
    cols, tw, th = 10, 156, 196
    rws = math.ceil(len(items) / cols)
    W_, H_ = cols * tw + 24, rws * th + 64
    im = Image.new("RGB", (W_, H_), (23, 22, 26))
    d = ImageDraw.Draw(im)
    font = lambda s, b=False: ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if b else ''}.ttf", s)
    d.text((12, 14), title, fill=(232, 228, 218), font=font(22, True))
    rar = {r["name"]: r["frame_color_hex"] for r in rows("rarities.csv")}
    rar["Arena"] = "#CFA545"
    for i, (it, pv) in enumerate(items):
        x, y = 12 + (i % cols) * tw, 52 + (i // cols) * th
        d.rectangle([x, y, x + tw - 8, y + th - 8], fill=(32, 31, 36))
        d.rectangle([x, y, x + tw - 8, y + 3], fill=rar[it["rarity"]])
        pv = pv.copy()
        pv.thumbnail((140, 140), Image.NEAREST)
        im.paste(pv, (x + (tw - 8 - pv.width) // 2, y + 8 + (140 - pv.height) // 2), pv)
        words, lines = it["name"].split(), [""]
        for wd in words:
            if len(lines[-1] + " " + wd) > 22 and lines[-1]:
                lines.append(wd)
            else:
                lines[-1] = (lines[-1] + " " + wd).strip()
        for j, ln in enumerate(lines[:2]):
            d.text((x + 5, y + 150 + j * 13), ln, fill=(232, 228, 218), font=font(11))
        d.text((x + 5, y + 176), slug(it["id"]), fill=(140, 136, 128), font=font(9))
    im.save(path, optimize=True)


# ---- main ---------------------------------------------------------------------------------------------------------
def main():
    if ASSETS.exists():
        shutil.rmtree(ASSETS)
    for sub in ("items", "models/item", "textures/item/weapon"):
        (ASSETS / sub).mkdir(parents=True)
    (HERE / "pack" / "pack.mcmeta").write_text(json.dumps({"pack": {
        "description": "Shardfall weapon models (generated by gen.py)", "pack_format": 46,
        "supported_formats": [46, 999], "min_format": 46, "max_format": 999}}, indent=1))
    groups, mapping = {}, []
    for it in load():
        w = W(it)
        gx, gy = BUILD[it["code"]](w)
        img = texture(w)
        o = 8 - w.n / 4
        els = elements(w, o)
        assert all(-16 <= v <= 32 for e in els for v in e["from"] + e["to"]), it["id"]
        grip = (gx / 2 + o, (w.n - gy) / 2 + o, 8)
        s = slug(it["id"])
        img.save(ASSETS / "textures/item/weapon" / f"{s}.png")
        tex = f"shardfall:item/weapon/{s}"
        model = {"credit": "Shardfall, original; generated by game-plan/minecraft/shardfall-weapons/gen.py",
                 "texture_size": [w.n, w.n], "gui_light": "front", "textures": {"0": tex, "particle": tex},
                 "elements": els, "display": display(w, els, grip, kind_of(it["code"]))}
        (ASSETS / "models/item" / f"{s}.json").write_text(json.dumps(model, separators=(",", ":")))
        (ASSETS / "items" / f"{s}.json").write_text(json.dumps({"model": {"type": "minecraft:model", "model": f"shardfall:item/{s}"}}))
        groups.setdefault(it["group"], []).append((it, preview(w, img, 4 if w.n == 32 else 2)))
        mapping.append({"itm_id": it["id"], "kubejs_id": "shardfall:" + s, "name": it["name"], "group": it["group"],
                        "class": it["cls"], "rarity": it["rarity"], "element": it["element"], "model": f"shardfall:item/{s}",
                        "texture": tex, "canvas_px": w.n, "elements": len(els), "hold": kind_of(it["code"]),
                        "registered_by_convert_py": it["registered"]})
    with open(HERE / "mapping.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(mapping[0]))
        wr.writeheader()
        wr.writerows(mapping)
    if (HERE / "overrides").exists():  # hand-edited models/textures win over generated ones
        shutil.copytree(HERE / "overrides", ASSETS, dirs_exist_ok=True)
    for g, items in groups.items():
        sheet(items, f"Shardfall weapons: {g} ({len(items)})", HERE / f"contact_sheet_{g.lower()}.png")
    print(f"{len(mapping)} weapons, {sum(m['elements'] for m in mapping)} elements -> {HERE}")


if __name__ == "__main__":
    main()
