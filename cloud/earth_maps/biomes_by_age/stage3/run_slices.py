"""Runs the Age I pack-biome palette engine (world/earth/biome/palette, the Python mirror of EraPalette) once per dated slice.
Usage (from the palette dir, DEM_CACHE set): python3 run_slices.py <ka> [<ka> ...]
Writes /tmp/claude-0/bm3/names_<ka>.npz: lat/lon axes at 0.125 degree, int16 biome index (-1 = none) into biomes.json."""
import json, sys, time, math
import numpy as np
from PIL import Image
sys.path.insert(0, '/home/user/dwt-biome/world/earth/biome/palette')
import palette as P, sim

OUT = sim.OUT
TL = json.load(open('/home/user/dwt-alps/src/main/resources/data/tellus/diaithir/era_timeline.json'))['sea']
def sea_m(ka): return float(np.interp(14873 - ka * 1000, [p[0] for p in TL], [p[1] for p in TL]))

def use(ka):
    sim.CLS = np.array(Image.open(OUT / f'biome4_{ka}ka.png'))
    a = np.array(Image.open(OUT / f'climate{ka}ka_a.png')).astype(np.float64)
    d = np.array(Image.open(OUT / f'climate{ka}ka_d.png')).astype(np.float64)
    sim.T_ = a[..., 0] / 2.5 - 50; sim.C_ = a[..., 1] / 2.5 - 80; sim.W_ = a[..., 2] / 3.8 - 15
    sim.P_ = (a[..., 3] / 3.0) ** 2; sim.D_ = (d / 6.0) ** 2
    sim.SEA = sea_m(ka)

if __name__ == '__main__':
    pal = P.Palette(json.load(open(P.DEFAULT_RULES)))
    dem = sim.Dem6()
    bands = [(60, 85), (35, 60), (10, 35), (-15, 10), (-40, -15), (-60, -40)]
    for ka in [int(x) for x in sys.argv[1:]]:
        t = time.time(); use(ka); res = []
        for (s, n) in bands:
            res.append(sim.region(pal, s, n, -180, 180, 0.125, dem, relief_off_m=2500.0, relief_factor=0.55))
        names = np.concatenate([r['names'] for r in res], 0)
        vocab = {}
        idx = np.full(names.shape, -1, np.int16)
        for i in range(names.shape[0]):
            for j in range(names.shape[1]):
                v = names[i, j]
                if v:
                    idx[i, j] = vocab.setdefault(v, len(vocab))
        np.savez_compressed(f'/tmp/claude-0/bm3/names_{ka}.npz', idx=idx, vocab=np.array(list(vocab), dtype=object), sea=sim.SEA)
        print(ka, 'ka done', round(time.time() - t), 's', len(vocab), 'biomes', flush=True)
