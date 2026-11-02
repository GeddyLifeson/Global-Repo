"""Renders the per-slice class grids for the Biomes By Age page. Run: python3 -I build.py  (needs numpy, Pillow)
Each slice -> 1440x720 RGBA PNG: R = class (0 sea, 1-27 BIOME4, 28 land ice, 29 no data), G = sea depth shade / land cropland share,
B = share of woodland cleared by people (HYDE), A = 255."""
import json, base64, io
import numpy as np
from PIL import Image

D = '/home/user/dwt-alps/src/main/resources/data/tellus/diaithir/'
OUT = '/tmp/claude-0/bm/'
W, H = 1440, 720

elev05 = np.load(OUT + 'elev.npy')                       # 360 x 720, 0.5 deg, north first, m
def up2(a):                                              # bilinear x2 for a smoother coast
    im = Image.fromarray(a.astype(np.float32), 'F').resize((W, H), Image.BILINEAR)
    return np.array(im)
elev = up2(elev05)
lat = 90 - (np.arange(H) + 0.5) * 0.25
lon = -180 + (np.arange(W) + 0.5) * 0.25
LAT, LON = np.meshgrid(lat, lon, indexing='ij')

tl = json.load(open(D + 'era_timeline.json'))['sea']
def sea_m(ka):
    lc = 14873 - ka * 1000
    xs = [p[0] for p in tl]; ys = [p[1] for p in tl]
    return float(np.interp(lc, xs, ys))

def nearest2(a):                                         # 720x360 -> 1440x720 repeat
    return np.repeat(np.repeat(a, 2, axis=0), 2, axis=1)

def pool(a, f, how):                                     # block reduce
    h, w = a.shape
    b = a.reshape(h // f, f, w // f, f)
    return b.max(axis=(1, 3)) if how == 'max' else b.mean(axis=(1, 3))

def ice_mask(ka):
    ik = int(round(ka))
    name = 'ice_thickness.png' if ik == 15 else f'ice_thickness_{ik}ka.png'
    try:
        a = np.array(Image.open(D + name)).astype(np.float32)
    except FileNotFoundError:
        return np.zeros((H, W), bool)
    return pool(a, 5, 'mean') > 30                       # more than 30 m of extra ice

def human(ka):
    ik = int(round(ka))
    lu = np.zeros((H, W), np.uint8); cr = np.zeros((H, W), np.uint8)
    if ik <= 10:
        lu = pool(np.array(Image.open(D + f'landuse_{ik}ka.png')), 3, 'max').astype(np.uint8)
        cr = pool(np.array(Image.open(D + f'cropland_{ik}ka.png')), 3, 'max').astype(np.uint8)
    return lu, cr

def render(ka, future=False):
    cls = np.array(Image.open(D + f'biome4_{0 if future else int(ka)}ka.png'))
    cls = nearest2(cls).astype(np.uint8)
    sea = 2.0 if future else sea_m(ka)
    if future:
        # sketch: biome belts move 4 degrees poleward (about +3 C), nothing else changes
        sh = 16                                          # 16 rows of 0.25 deg
        out = cls.copy()
        north = LAT > 0
        src_n = np.clip(np.arange(H) + sh, 0, H - 1)    # a northern cell takes the class from 4 deg further south
        src_s = np.clip(np.arange(H) - sh, 0, H - 1)
        out[:H // 2] = cls[src_n[:H // 2]]
        out[H // 2:] = cls[src_s[H // 2:]]
        cls = out
    land = elev > sea
    cls = np.where(cls == 0, 29, cls)                    # vegetated-class 0 = no data (south of 60 S)
    ice = ice_mask(0 if future else ka)
    # Greenland and Antarctica carry ice at every date
    gl = (LAT > 59) & (LAT < 84) & (LON > -75) & (LON < -10) & (elev > 300)
    an = LAT < -62
    if future:
        gl = (LAT > 61) & (LAT < 83) & (LON > -60) & (LON < -22) & (elev > 1200)   # coastal Greenland melts back
    ice = (ice | gl | an) & land
    R = np.where(land, cls, 0).astype(np.uint8)
    R = np.where(ice, 28, R).astype(np.uint8)
    lu, cr = (np.zeros((H, W), np.uint8),) * 2 if future else human(ka)
    lu = np.where(land & ~ice, lu, 0).astype(np.uint8); cr = np.where(land & ~ice, cr, 0).astype(np.uint8)
    def enc(arr, mode):
        buf = io.BytesIO(); Image.fromarray(arr, mode).save(buf, 'PNG', optimize=True); return buf.getvalue()
    pal = Image.new('P', (1, 1)); pal.putpalette([v for i in range(256) for v in (i, i, i)])
    im = Image.fromarray(R, 'L').convert('P'); 
    imp = Image.fromarray(R, 'L'); buf = io.BytesIO(); imp.save(buf, 'PNG', optimize=True)
    png = buf.getvalue()
    extra = {'lu': enc(lu, 'L') if lu.any() else None, 'cr': enc(cr, 'L') if cr.any() else None}
    stats = {'sea': round(sea, 1), 'land_pct': round(float(land.mean()) * 100, 1), 'ice_pct': round(float(ice.mean()) * 100, 1)}
    return png, extra, stats

slices = {}
for ka in list(range(15, -1, -1)):
    png, ex, st = render(ka)
    open(OUT + f's{ka}.png', 'wb').write(png)
    for k, v in ex.items():
        if v: open(OUT + f's{ka}_{k}.png', 'wb').write(v)
    slices[ka] = st
    print(ka, st, len(png), {k: len(v) for k, v in ex.items() if v})
png, ex, st = render(0, future=True)
open(OUT + 'sfuture.png', 'wb').write(png); slices['future'] = st; print('future', st, len(png))
json.dump(slices, open(OUT + 'slices.json', 'w'))

sea0 = 0.0
depth = np.clip(-elev, 0, 6000)
shade = np.where(elev < 0, 255 - np.clip(depth / 6000 * 200, 0, 200), 0).astype(np.uint8)
Image.fromarray(shade, 'L').save(OUT + 'depth.png', optimize=True)
print('depth', len(open(OUT + 'depth.png', 'rb').read()))
