"""Future Earth heightmap: reproject Azgaar's world.png (Web Mercator, fitted to Natural Earth) to
equirectangular, raise the sea and apply the edits listed in future_earth.json."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC_X0, SRC_K, SRC_Y0 = 282.5, 95.0, 178.0  # world.png Mercator fit (calib.py, IoU 0.94)
LAT_N, LAT_S, LON_W, LON_E = 72.0, -56.0, -170.0, 180.0
W, H = 1600, 585  # output size, ratio matches the map's 2400x878 canvas
SEA = 51  # Azgaar sea level (lightness 0.2)
M_PER_V = 12  # metres per grey level in the lowlands, read off known towns (Paris, Berlin, Memphis, Moscow)

cfg = json.load(open(sys.argv[1]))
src = np.array(Image.open(sys.argv[2])).astype(float)

lon = LON_W + (np.arange(W) + 0.5) / W * (LON_E - LON_W)
lat = LAT_N - (np.arange(H) + 0.5) / H * (LAT_N - LAT_S)
sx = SRC_X0 + SRC_K * np.radians(lon)
sy = SRC_Y0 - SRC_K * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))
SX, SY = np.meshgrid(sx, sy)
x0, y0 = np.floor(SX).astype(int), np.floor(SY).astype(int)
fx, fy = SX - x0, SY - y0
sh, sw = src.shape
g = lambda y, x: src[np.clip(y, 0, sh - 1), np.clip(x, 0, sw - 1)]
h = (g(y0, x0) * (1 - fx) * (1 - fy) + g(y0, x0 + 1) * fx * (1 - fy)
     + g(y0 + 1, x0) * (1 - fx) * fy + g(y0 + 1, x0 + 1) * fx * fy)

# sea rise: land below the new shoreline drowns as shallow shelf, the rest keeps its height above the old sea
rise = cfg["seaRiseMetres"] / M_PER_V
land = h >= SEA
h = np.where(land, np.where(h - rise >= SEA, h - rise, SEA - 3), h)

def px(latlon):
    la, lo = latlon
    return ((lo - LON_W) / (LON_E - LON_W) * W, (LAT_N - la) / (LAT_N - LAT_S) * H)

def mask(e):
    im = Image.new("L", (W, H))
    d = ImageDraw.Draw(im)
    if "poly" in e:
        d.polygon([px(p) for p in e["poly"]], fill=255)
    elif "line" in e:
        wpx = e["width"] / (LON_E - LON_W) * W
        d.line([px(p) for p in e["line"]], fill=255, width=max(2, round(wpx)))
    else:
        la, lo, rla, rlo = e["ellipse"]
        (xa, ya), (xb, yb) = px((la + rla, lo - rlo)), px((la - rla, lo + rlo))
        d.ellipse([xa, ya, xb, yb], fill=255)
    return np.array(im.filter(ImageFilter.GaussianBlur(1))) / 255.0

for e in cfg["edits"]:
    m = mask(e)
    k = e["kind"]
    if k == "sea":
        h = h * (1 - m) + np.minimum(h, SEA - 8) * m
    elif k in ("raise", "island"):
        h = h * (1 - m) + np.maximum(h, e["value"]) * m
    elif k == "scale":
        h = np.where(h >= SEA, SEA + (h - SEA) * (1 - m * (1 - e["factor"])), h)
    elif k == "crater":
        inner = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5))) / 255.0
        ring = np.clip(m - inner, 0, 1)
        h = h * (1 - ring) + np.maximum(h, e["rim"]) * ring
        h = h * (1 - inner) + (SEA - 12) * inner

Image.fromarray(np.clip(h, 0, 255).astype(np.uint8)).save(sys.argv[3])
