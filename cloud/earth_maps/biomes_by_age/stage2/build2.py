"""Stage 2 of the Biomes By Age page: HYDE slices for Ages IV-VII, dated lakes, crust rebound, a Koppen-Geiger Future.
Run: python3 -I build2.py   (numpy, Pillow). Writes s<key>.png (+ _lu _cr _ur _rb) and slices2.json into /tmp/claude-0/bm2/.
R channel classes: 0 sea, 1-27 BIOME4, 28 land ice, 29 no data, 30 lake."""
import json, io, zlib, base64
import numpy as np
from PIL import Image

D = '/home/user/dwt-alps/src/main/resources/data/tellus/diaithir/'
OUT = '/tmp/claude-0/bm2/'
W, H = 1440, 720
HYDE = '/tmp/claude-0/hyde_dl/ant/anthromes/asc/'
KG = '/tmp/claude-0/kg/'

elev = np.array(Image.fromarray(np.load('/tmp/claude-0/bm/elev.npy').astype(np.float32), 'F').resize((W, H), Image.BILINEAR))
lat = 90 - (np.arange(H) + 0.5) * 0.25
lon = -180 + (np.arange(W) + 0.5) * 0.25
LAT, LON = np.meshgrid(lat, lon, indexing='ij')
tl = json.load(open(D + 'era_timeline.json'))['sea']

def sea_m(ka):
    return float(np.interp(14873 - ka * 1000, [p[0] for p in tl], [p[1] for p in tl]))
def nearest2(a): return np.repeat(np.repeat(a, 2, axis=0), 2, axis=1)
def pool(a, f, how):
    h, w = a.shape; b = a.reshape(h // f, f, w // f, f)
    return b.max(axis=(1, 3)) if how == 'max' else b.mean(axis=(1, 3))
def enc(arr):
    buf = io.BytesIO(); Image.fromarray(arr, 'L').save(buf, 'PNG', optimize=True); return buf.getvalue()

# ---- ice and crust rebound -------------------------------------------------------------------------
def ice_thk(ka):
    ik = int(round(ka)); name = 'ice_thickness.png' if ik == 15 else f'ice_thickness_{ik}ka.png'
    try: a = np.array(Image.open(D + name)).astype(np.float32)
    except FileNotFoundError: return np.zeros((H, W), np.float32)
    return pool(a, 5, 'mean')
THK = {k: ice_thk(k) for k in range(15, -1, -1)}
def ice_mask(ka): return THK[int(round(ka))] > 30

# Flexural smoothing: gaussian of sigma 1.5 degrees (6 cells) in frequency space.
fy = np.fft.fftfreq(H)[:, None]; fx = np.fft.rfftfreq(W)[None, :]
def _g(sig): return np.exp(-2 * np.pi ** 2 * sig * sig * (fx ** 2 + fy ** 2))
# Plate response: a gaussian of sigma 1.5 degrees minus a wider one (sigma 3 degrees) at weight 0.5, kernel integral 1 -> peripheral forebulge about 9% of the depression
GK = (_g(6) - 0.5 * _g(12)) / 0.5
def blur(a): return np.fft.irfft2(np.fft.rfft2(a) * GK, s=a.shape)
RATIO, TAU = 0.20, 7.0                                  # ice/mantle load ratio and relaxation time in ka, fitted to published marine limits and present uplift
E = {k: RATIO * blur(THK[k]) for k in THK}
Dk = {15: E[15].copy()}
for k in range(15, 0, -1):
    Eb = (E[k] + E[k - 1]) / 2
    Dk[k - 1] = Eb + (Dk[k] - Eb) * np.exp(-1.0 / TAU)
DELTA = {k: (Dk[k] - Dk[0]).astype(np.float32) for k in Dk}   # extra depression against today, metres
for k in (15, 12, 10, 8, 6, 4, 2): print('rebound', k, 'ka max depression vs today', round(float(DELTA[k].max()), 1), 'm')

# ---- lakes -----------------------------------------------------------------------------------------
def decode_lakes():
    out = []
    for f in ('lakes.json', 'lakes_glacial.json'):
        for l in json.load(open(D + f))['lakes']:
            w, h, res = l['width'], l['height'], l['res']; rb = (w + 7) >> 3
            bits = np.frombuffer(zlib.decompress(base64.b64decode(l['mask'])), np.uint8).reshape(h, rb)
            full = np.unpackbits(bits, axis=1)[:, :w].astype(bool)
            # sample at 0.25 deg cell: 4x4 sub-samples, lake where 30% of them are in the mask
            r0 = int(np.floor((l['north'] - 0) / 0.25)); 
            cells = np.zeros((H, W), np.float32)
            sub = (np.arange(4) + 0.5) / 4 * 0.25
            for sy in sub:
                for sx in sub:
                    la = LAT - 0.125 + sy; lo = LON - 0.125 + sx
                    cx = np.floor((lo - l['west']) / res).astype(int); cy = np.floor((l['north'] - la) / res).astype(int)
                    ok = (cx >= 0) & (cx < w) & (cy >= 0) & (cy < h)
                    v = np.zeros((H, W), bool); v[ok] = full[cy[ok], cx[ok]]
                    cells += v
            out.append({'name': l['name'], 'level': l['level_m'], 'mask': cells / 16 >= 0.3,
                        'start': l.get('start_ka'), 'end': l.get('end_ka'), 'glacial': f == 'lakes_glacial.json'})
    return out
LAKES = decode_lakes()
END = {'Baltic Ice Lake': 11.7}
for l in LAKES: print('lake', l['name'], int(l['mask'].sum()), 'cells')
def lakes_at(ka, sea):
    m = np.zeros((H, W), bool)
    for l in LAKES:
        if l['start'] is not None:
            ok = l['end'] <= ka <= l['start']
        else:
            ok = ka >= END.get(l['name'], 0) and ka >= 9.99      # game has no end date; drawn through Age I only
            if l['name'] == 'Black Sea lake': ok = ok and sea < l['level']
        if ok: m |= l['mask']
    return m

# ---- people (HYDE 3.2.1 anthromes) ----------------------------------------------------------------
SHARE = {11: 0.9, 12: 0.8, 21: 0.6, 22: 0.6, 23: 0.6, 24: 0.5, 31: 0.7, 32: 0.7, 33: 0.55, 34: 0.3, 41: 0.5, 42: 0.4, 43: 0.2, 51: 0.15, 52: 0.1}
CROP = [12, 21, 22, 23, 24, 31, 32, 33, 34]
def read_asc(p):
    data = open(p, 'rb').read(); head, _, body = data.partition(b'NODATA_value'); _, _, rest = body.partition(b'\n')
    nc = int(head.split(b'ncols')[1].split()[0]); nr = int(head.split(b'nrows')[1].split()[0])
    return np.array(rest.decode().split(), dtype=np.float32).reshape(nr, nc).astype(np.int16)
LUT = np.zeros(256, np.uint8)
for c, s in SHARE.items(): LUT[c] = round(s * 255)
def hyde(year):
    lab = f'{year}AD'; a = read_asc(f'{HYDE}{lab}_anthromes/anthromes{lab}.asc'); a = np.clip(a, 0, 255)
    lu = pool(LUT[a], 3, 'max').astype(np.uint8)
    cr = pool(np.where(np.isin(a, CROP), 255, 0).astype(np.uint8), 3, 'max').astype(np.uint8)
    ur = pool(np.where(a == 11, 255, np.where(a == 12, 150, 0)).astype(np.uint8), 3, 'max').astype(np.uint8)
    return lu, cr, ur
def hyde_old(ka):
    ik = int(round(ka)); lu = cr = np.zeros((H, W), np.uint8)
    if ik <= 10:
        lu = pool(np.array(Image.open(D + f'landuse_{ik}ka.png')), 3, 'max').astype(np.uint8)
        cr = pool(np.array(Image.open(D + f'cropland_{ik}ka.png')), 3, 'max').astype(np.uint8)
    return lu, cr, np.zeros((H, W), np.uint8)

# ---- Koppen-Geiger future ---------------------------------------------------------------------------
def kg(path):
    a = np.array(Image.open(path)); ys = np.clip(((90 - lat) / 0.1).astype(int), 0, a.shape[0] - 1); xs = np.clip(((lon + 180) / 0.1).astype(int), 0, a.shape[1] - 1)
    return a[np.ix_(ys, xs)]
KG0 = kg(KG + '1991_2020/koppen_geiger_0p1.tif')
print('KG check Sahara', KG0[int((90 - 24) / .25), int((10 + 180) / .25)], 'Amazon', KG0[int((90 + 3) / .25), int((-60 + 180) / .25)], 'Alberta', KG0[int((90 - 55) / .25), int((-115 + 180) / .25)])
BASE0 = nearest2(np.array(Image.open(D + 'biome4_0ka.png'))).astype(np.uint8)
def _climate05():
    a = np.array(Image.open(D + 'climate0ka_a.png')).astype(np.float64); d = np.array(Image.open(D + 'climate0ka_d.png')).astype(np.float64)
    return [a[..., 0] / 2.5 - 50, a[..., 1] / 2.5 - 80, a[..., 2] / 3.8 - 15, (a[..., 3] / 3.0) ** 2, (d / 6.0) ** 2]
def analog(scn):
    """Nearest climate analog at the 0.5 degree grid of the vegetation data: a land cell whose Koppen-Geiger class changes takes the
    BIOME4 class AND the climate values (T, C, W, P, D) of the nearest place on Earth (great-circle) that has the future class today.
    Saves the 0.5 degree class and climate rasters for the palette run."""
    k0 = np.array(Image.open(KG + '1991_2020/koppen_geiger_0p5.tif')); kf = np.array(Image.open(KG + f'2071_2099/{scn}/koppen_geiger_0p5.tif'))
    bio = np.array(Image.open(D + 'biome4_0ka.png')).astype(np.uint8); clim = _climate05()
    h5, w5 = bio.shape; la5 = 90 - (np.arange(h5) + 0.5) * 0.5; lo5 = -180 + (np.arange(w5) + 0.5) * 0.5
    LA5, LO5 = np.meshgrid(la5, lo5, indexing='ij'); landv = bio > 0
    changed = (kf != k0) & (kf > 0) & landv
    XYZ = np.stack([np.cos(np.radians(LA5)) * np.cos(np.radians(LO5)), np.cos(np.radians(LA5)) * np.sin(np.radians(LO5)), np.sin(np.radians(LA5))], -1)
    cls = bio.copy(); cl = [c.copy() for c in clim]
    for k in np.unique(kf[changed]):
        tgt = changed & (kf == k); src = (k0 == k) & landv
        if not src.any(): continue
        P = XYZ[tgt]; S = XYZ[src]; out = np.empty(len(P), np.int64)
        for a in range(0, len(P), 2000): out[a:a + 2000] = np.argmax(P[a:a + 2000] @ S.T, axis=1)
        cls[tgt] = bio[src][out]
        for c, c0 in zip(cl, clim): c[tgt] = c0[src][out]
    np.savez_compressed(OUT + f'future_{scn}.npz', cls=cls, T=cl[0], C=cl[1], W=cl[2], P=cl[3], D=cl[4])
    return nearest2(cls).astype(np.uint8), float(changed.sum() / max(1, landv.sum()))

# ---- render -----------------------------------------------------------------------------------------
def render(key, ka, base_ka, human, lakes=True, rebound=None, fut=None):
    if fut: cls, ch = analog(fut); sea = 0.6
    else: cls = nearest2(np.array(Image.open(D + f'biome4_{int(base_ka)}ka.png'))).astype(np.uint8); sea = sea_m(ka)
    cls = np.where(cls == 0, 29, cls)
    land0 = elev > sea
    ice = ice_mask(ka) if not fut else np.zeros((H, W), bool)
    gl = (LAT > 59) & (LAT < 84) & (LON > -75) & (LON < -10) & (elev > 300); an = LAT < -62
    ice = (ice | gl | an) & land0
    rbflood = np.zeros((H, W), bool); rbmax = 0.0
    land = land0
    fbexp = np.zeros((H, W), bool); fbmax = 0.0
    if rebound is not None and not fut:
        land_rb = (elev - rebound) > sea
        rbflood = land0 & ~land_rb & ~ice
        fbexp = land_rb & ~land0 & ~ice
        land = land_rb | ice
        rbmax = float(rebound[rbflood].max()) if rbflood.any() else 0.0
        fbmax = float(-rebound[fbexp].min()) if fbexp.any() else 0.0
        if fbexp.any():
            need = fbexp & (cls == 29)
            for _ in range(24):
                if not need.any(): break
                for sh, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
                    nb = np.roll(cls, sh, axis=ax); ok = need & (nb != 29) & (nb != 0)
                    cls = np.where(ok, nb, cls); need = need & ~ok
    R = np.where(land, cls, 0).astype(np.uint8); R[ice] = 28
    lake = np.zeros((H, W), bool)
    if lakes and not fut:
        lake = lakes_at(ka, sea) & land & ~ice; R[lake] = 30
    lu, cr, ur = human
    keep = land & ~ice & ~lake
    lu = np.where(keep, lu, 0).astype(np.uint8); cr = np.where(keep, cr, 0).astype(np.uint8); ur = np.where(keep, ur, 0).astype(np.uint8)
    st = {'sea': round(sea, 1), 'land_pct': round(float(land.mean()) * 100, 1), 'ice_pct': round(float((R == 28).mean()) * 100, 1),
          'lake_pct': round(float(lake.mean()) * 100, 2), 'rb_m': round(rbmax), 'rb_pct': round(float(rbflood.mean()) * 100, 2),
          'fb_m': round(fbmax), 'fb_pct': round(float(fbexp.mean()) * 100, 2)}
    if fut: st['changed_pct'] = round(ch * 100, 1)
    open(OUT + f's{key}.png', 'wb').write(enc(R))
    for nme, arr in (('lu', lu), ('cr', cr), ('ur', ur), ('rb', (rbflood * 255).astype(np.uint8)), ('fb', (fbexp * 255).astype(np.uint8))):
        if arr.any(): open(OUT + f's{key}_{nme}.png', 'wb').write(enc(arr))
    print(key, st); return st

slices = {}
for ka in range(15, -1, -1):
    slices[str(ka)] = render(str(ka), ka, ka, hyde_old(ka), rebound=DELTA[ka])
# Ages IV-VII: HYDE year slices on today's potential vegetation
for yr in (1700, 1800, 1850, 1900, 1930, 1960, 2000, 2017):
    slices[f'y{yr}'] = render(f'y{yr}', (1950 - yr) / 1000, 0, hyde(yr), lakes=False, rebound=None)
for scn in ('ssp245', 'ssp585'):
    slices['f' + scn[3:]] = render('f' + scn[3:], 0, 0, (np.zeros((H, W), np.uint8),) * 3, fut=scn)
json.dump(slices, open(OUT + 'slices2.json', 'w'))
