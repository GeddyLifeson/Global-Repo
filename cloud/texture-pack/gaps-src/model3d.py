"""3D item models (held, dropped, in frames) that match the 64 px icons: faceted gems, bevelled ingots, lumpy nuggets,
rock-and-vein raw ore, stepped dust piles. Each item gets a palette strip (the icon's own colour ramp) and an item
definition that shows the flat icon in the GUI and the 3D model everywhere else."""
import json, os, sys, re, math, random
sys.path.insert(0, "/home/user/work/pix"); sys.path.insert(0, "/home/user/work/gaps")
from PIL import Image
from pixel_icons import ramp
from build_list import jar
O = "/home/user/diaithirrpg/tools/art/blender/baked/models3d/assets/"
G = "/home/user/diaithirrpg/tools/art/blender/baked/"
DISPLAY = {
 "ground": {"rotation": [0, 0, 0], "translation": [0, 2.5, 0], "scale": [0.55, 0.55, 0.55]},
 "fixed": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.6, 0.6, 0.6]},
 "thirdperson_righthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.38, 0.38, 0.38]},
 "thirdperson_lefthand": {"rotation": [75, 45, 0], "translation": [0, 2.5, 0], "scale": [0.38, 0.38, 0.38]},
 "firstperson_righthand": {"rotation": [0, 45, 0], "translation": [0, 1, 0], "scale": [0.4, 0.4, 0.4]},
 "firstperson_lefthand": {"rotation": [0, 225, 0], "translation": [0, 1, 0], "scale": [0.4, 0.4, 0.4]},
 "head": {"rotation": [0, 0, 0], "translation": [0, 13, 7], "scale": [0.8, 0.8, 0.8]},
}
FACE = dict(up=3, down=1, north=2, south=2, east=1, west=2)


class Model:
    def __init__(self, n): self.els = []; self.n = n; self.w = 16 / n
    def box(self, a, b, face=None, rot=None, off=0, glint_top=False):
        f = dict(FACE); f.update(face or {})
        if glint_top: f["up"] = 4
        el = {"from": list(map(lambda v: round(v, 3), a)), "to": list(map(lambda v: round(v, 3), b)), "faces": {}}
        for k, i in f.items():
            u0 = (i + off) * self.w; el["faces"][k] = {"uv": [round(u0 + 0.05, 3), 0, round(u0 + self.w - 0.05, 3), 16], "texture": "#0"}
        if rot: el["rotation"] = rot
        self.els.append(el)
    def oct(self, cx, cz, rx, rz, y0, y1, **kw):
        self.box((cx - rx, y0, cz - rz), (cx + rx, y1, cz + rz), **kw)
        self.box((cx - rx, y0, cz - rz), (cx + rx, y1, cz + rz), rot={"origin": [cx, y0, cz], "axis": "y", "angle": 45}, **kw)
    def json(self, tex):
        return {"textures": {"0": tex, "particle": tex}, "elements": self.els, "display": DISPLAY}


def gem(m, cut):
    if cut == "emerald":
        m.box((4, 3.5, 5.5), (12, 11.5, 10.5)); m.box((5.5, 3.5, 4), (10.5, 11.5, 12))
        m.box((5, 11.5, 6), (11, 12.4, 10)); m.box((6, 11.5, 5), (10, 12.4, 11), glint_top=True)
    elif cut == "oval":
        m.oct(8, 8, 4.6, 3.2, 7, 9); m.oct(8, 8, 3.4, 2.4, 9, 10.6); m.box((5.5, 10.6, 6.3), (10.5, 11.2, 9.7), glint_top=True)
        m.oct(8, 8, 3.4, 2.4, 5, 7); m.oct(8, 8, 2.2, 1.6, 3.6, 5); m.box((7.2, 2.8, 7.2), (8.8, 3.6, 8.8))
    elif cut == "prism":
        m.oct(8, 8, 2.6, 2.6, 2, 10); m.oct(8, 8, 1.8, 1.8, 10, 12, face={"up": 3}); m.box((7.2, 12, 7.2), (8.8, 13.6, 8.8), glint_top=True)
    elif cut == "cabochon":
        m.oct(8, 8, 4.4, 3.4, 3.5, 6); m.oct(8, 8, 3.4, 2.6, 6, 7.6); m.oct(8, 8, 2.2, 1.7, 7.6, 8.6, glint_top=True)
    elif cut == "shardglass":
        m.box((6.5, 2, 6.5), (9.5, 11, 9.5), rot={"origin": [8, 2, 8], "axis": "z", "angle": 22.5}); m.box((5, 2, 7), (7.5, 8, 9.5), rot={"origin": [6, 2, 8], "axis": "z", "angle": -22.5}, face={"up": 4})
        m.box((8.5, 2, 6), (11, 7, 8.5), rot={"origin": [9, 2, 7], "axis": "x", "angle": 22.5})
    elif cut == "teardrop":
        m.oct(8, 8, 3.2, 3.2, 3, 9); m.oct(8, 8, 2.2, 2.2, 9, 11.5); m.box((7.2, 11.5, 7.2), (8.8, 13.4, 8.8), glint_top=True)
    else:  # brilliant
        m.oct(8, 8, 3.8, 3.8, 7, 9); m.oct(8, 8, 3, 3, 9, 10.6); m.box((6, 10.6, 6), (10, 11.2, 10), glint_top=True)
        m.oct(8, 8, 3, 3, 5.2, 7); m.oct(8, 8, 2, 2, 3.6, 5.2); m.box((7.2, 2.6, 7.2), (8.8, 3.6, 8.8))


def shard(m, rgb, cut):
    for (cx, cz, r, h, ang) in ((6, 8, 1.8, 9, -22.5), (10, 7.5, 1.6, 12, 0), (9.5, 10.5, 1.4, 6, 22.5)):
        m.box((cx - r, 2, cz - r), (cx + r, 2 + h, cz + r), rot={"origin": [cx, 2, cz], "axis": "z", "angle": ang})
        m.box((cx - r * .6, 2 + h, cz - r * .6), (cx + r * .6, 3.4 + h, cz + r * .6), rot={"origin": [cx, 2 + h, cz], "axis": "z", "angle": ang}, glint_top=True)


def nugget(m, rnd):
    for cx, cz, s, y in ((6, 8, 2.8, 5), (10, 7, 2.4, 4.6), (8, 10, 2.0, 4.2), (8.5, 6.5, 1.6, 7)):
        m.box((cx - s, y - s, cz - s), (cx + s, y + s, cz + s), rot={"origin": [cx, y, cz], "axis": "y", "angle": 22.5})
        m.box((cx - s * .85, y - s * .85, cz - s * .85), (cx + s * .85, y + s * .85, cz + s * .85), rot={"origin": [cx, y, cz], "axis": "y", "angle": -22.5}, glint_top=True)


def ingot(m):
    m.box((2.5, 3, 5), (13.5, 5, 11)); m.box((3.5, 5, 5.7), (12.5, 7.4, 10.3)); m.box((4.5, 7.4, 6.4), (11.5, 8.2, 9.6), glint_top=True)
    m.box((6, 4, 4.7), (10, 4.6, 5), face={"north": 1, "south": 1})


def raw(m, rnd):  # swatches 0-4 host, 5-9 vein
    host = lambda **k: k
    for cx, cz, s, y, a in ((7, 8, 3.6, 4, 22.5), (10.5, 8.5, 2.8, 3.4, -22.5), (8, 6, 2.4, 3, 0), (8.5, 10.4, 2.2, 3.1, 22.5)):
        m.box((cx - s, y - s + 1, cz - s), (cx + s, y + s + 1, cz + s), rot={"origin": [cx, y, cz], "axis": "y", "angle": a})
    m.box((5.2, 6.8, 6.5), (9.4, 9.2, 10), rot={"origin": [7, 8, 8], "axis": "y", "angle": 22.5})
    for x, y, z, s in ((4.2, 5.5, 8, 1.7), (9, 8.8, 5.8, 1.8), (12, 5, 9, 1.6), (7, 9.8, 9, 1.8), (8, 4.2, 4.8, 1.6), (6, 4.2, 11.5, 1.5), (11, 7.6, 11, 1.4), (5.5, 8, 5, 1.4)):
        m.box((x - s, y - s, z - s), (x + s, y + s, z + s), face={k: 5 + v for k, v in FACE.items()}, glint_top=False, rot={"origin": [x, y, z], "axis": "y", "angle": 45})


def dust(m, rnd):
    layers = ((10.5, 1.6), (8.4, 1.5), (6.4, 1.4), (4.4, 1.3), (2.4, 1.1))
    y = 2
    for i, (w, h) in enumerate(layers):
        r = w / 2
        m.box((8 - r, y, 8 - r), (8 + r, y + h, 8 + r), face={"up": 3 if i < 4 else 4, "north": 2, "south": 2, "east": 1, "west": 2}, rot={"origin": [8, y, 8], "axis": "y", "angle": 22.5 * (i % 2)})
        y += h
    for x, z in ((3.4, 9.5), (12.4, 7.5), (6, 13), (11, 12.6)):
        m.box((x - .6, 2, z - .6), (x + .6, 2.8, z + .6), face={"up": 3})


def palette(rgb, kind, cut):
    if kind == "raw":
        host, vein = cut if cut else ((118, 108, 98), rgb)
        cols = ramp(host) + ramp(vein, True)
    else:
        cols = ramp(rgb, kind in ("nugget", "ingot"))
    im = Image.new("RGBA", (len(cols), 1))
    for i, c in enumerate(cols): im.putpixel((i, 0), c)
    return im, len(cols)


def build(ns, rel, p, sprite_model):
    kind, rgb, cut = p["kind"], tuple(p["rgb"]), p["cut"]
    rnd = random.Random(hash(rel) & 0xffff)
    pal, n = palette(rgb, kind, cut)
    m = Model(n)
    if kind == "gem": gem(m, cut if isinstance(cut, str) else "brilliant")
    elif kind == "shard": shard(m, rgb, cut)
    elif kind == "nugget": nugget(m, rnd)
    elif kind == "ingot": ingot(m)
    elif kind == "raw": raw(m, rnd)
    else: dust(m, rnd)
    flat = rel.replace("/", "__")
    tpath = f"{O}{ns}/textures/item/factory3d/{flat}.png"; os.makedirs(os.path.dirname(tpath), exist_ok=True); pal.save(tpath)
    mpath = f"{O}{ns}/models/item/factory3d/{flat}.json"; os.makedirs(os.path.dirname(mpath), exist_ok=True)
    json.dump(m.json(f"{ns}:item/factory3d/{flat}"), open(mpath, "w"))
    d = {"model": {"type": "minecraft:select", "property": "minecraft:display_context",
         "cases": [{"when": ["gui", "on_shelf"], "model": sprite_model if isinstance(sprite_model, dict) else {"type": "minecraft:model", "model": sprite_model}}],
         "fallback": {"type": "minecraft:model", "model": f"{ns}:item/factory3d/{flat}"}}}
    ip = f"{O}{ns}/items/{rel}.json"; os.makedirs(os.path.dirname(ip), exist_ok=True); json.dump(d, open(ip, "w"))


def main():
    params = json.load(open("/home/user/work/pix/params.json"))
    V = {"coal": ("raw", (34, 34, 38), ((30, 30, 34), (84, 84, 96))), "charcoal": ("raw", (44, 36, 32), ((40, 34, 30), (96, 76, 60))), "flint": ("gem", (86, 86, 94), "shardglass"),
         "clay_ball": ("gem", (160, 168, 184), "cabochon"), "slime_ball": ("gem", (110, 204, 92), "cabochon"), "ghast_tear": ("gem", (244, 244, 246), "teardrop"),
         "heart_of_the_sea": ("gem", (48, 150, 190), "cabochon"), "brick": ("ingot", (176, 86, 64), None), "nether_brick": ("ingot", (78, 36, 44), None),
         "netherite_scrap": ("raw", (96, 76, 66), ((58, 46, 42), (112, 86, 74))), "sugar": ("dust", (240, 240, 240), None), "bone_meal": ("dust", (236, 232, 218), None),
         "resin_clump": ("raw", (210, 120, 44), ((184, 98, 40), (236, 156, 64))), "resin_brick": ("ingot", (204, 104, 44), None), "blaze_powder": ("dust", (240, 160, 40), None),
         "gunpowder": ("dust", (86, 86, 90), None), "glowstone_dust": ("dust", (246, 204, 92), None)}
    for k, (kind, rgb, cut) in V.items(): params[f"minecraft:{k}"] = {"kind": kind, "rgb": list(rgb), "cut": cut}
    done = skipped = 0
    for key, p in params.items():
        ns, rel = key.split(":", 1)
        if not os.path.exists(f"{G}pixel/assets/{ns}/textures/item/{rel}.png"): continue
        dp = f"assets/{ns}/items/{rel}.json"; sprite = None
        if dp in jar:
            try: d = json.loads(jar[dp].read(dp))
            except Exception: d = {}
            m = d.get("model", {})
            if m.get("type") == "minecraft:model" and not m.get("tints"): sprite = m["model"]
            elif m: sprite = m  # tinted, select or condition definitions: the original runs in gui and on shelves
        elif os.path.exists(f"{G}gaps/assets/{ns}/items/{rel}.json"): sprite = f"{ns}:item/{rel}"
        if not sprite: skipped += 1; continue
        build(ns, rel, p, sprite); done += 1
    print(done, "3D models;", skipped, "skipped (special item definitions)")


if __name__ == "__main__": main()
