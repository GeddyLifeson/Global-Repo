"""Palette run for the modelled Future: BIOME4 class and climate come from the 0.5 degree climate-analog rasters (build2.analog), sea +0.6 m."""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/user/dwt-biome/world/earth/biome/palette')
import palette as P, sim
pal = P.Palette(json.load(open(P.DEFAULT_RULES))); dem = sim.Dem6()
bands = [(60, 85), (35, 60), (10, 35), (-15, 10), (-40, -15), (-60, -40)]
for scn, key in (('ssp245', 'f245'), ('ssp585', 'f585')):
    z = np.load(f'/tmp/claude-0/bm2/future_{scn}.npz')
    sim.CLS = z['cls'].astype(np.uint8); sim.T_, sim.C_, sim.W_, sim.P_, sim.D_ = z['T'], z['C'], z['W'], z['P'], z['D']; sim.SEA = 0.6
    t = time.time(); res = [sim.region(pal, s, n, -180, 180, 0.125, dem, relief_off_m=2500.0, relief_factor=0.55) for (s, n) in bands]
    names = np.concatenate([r['names'] for r in res], 0); vocab = {}; idx = np.full(names.shape, -1, np.int16)
    for i in range(names.shape[0]):
        for j in range(names.shape[1]):
            v = names[i, j]
            if v: idx[i, j] = vocab.setdefault(v, len(vocab))
    np.savez_compressed(f'/tmp/claude-0/bm3/names_{key}.npz', idx=idx, vocab=np.array(list(vocab), dtype=object), sea=0.6)
    print(key, 'done', round(time.time() - t), 's', len(vocab), flush=True)
