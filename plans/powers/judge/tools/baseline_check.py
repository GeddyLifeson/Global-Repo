#!/usr/bin/env python3
"""Baseline check (BASELINE_CANON_METHOD.md): sd/w by case, Gibbs posterior width for sample characters, old guesses vs baseline."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feats
inf = feats.inference
OLD_M = {'stated': .2, 'measured': .3, 'scaled': .4, 'estimated': .6}
OLD_W = {'main': 1, 'extended': .5, 'games': .5, 'noncanon': .2}
def post(fs):  # fs: [(T, sd, w, source)] -> (median, 90% width)
    c = inf.Character('x', 'u', [inf.Feat(T, sd, w, st) for T, sd, w, st in fs])
    d, _ = inf.gibbs([c], n_iter=3000, burn=500, chains=2)
    x = d['x'].ravel(); lo, hi = np.percentile(x, [5, 95]); return round(float(np.median(x)), 2), round(float(hi - lo), 2)
def mk(tpl, inp, a='AP', canon='main', st='primary'):
    f = {'a': a, 'tpl': tpl, 'in': inp, 'canon': canon, 'st': st}; c = feats.compute(f)
    old = max(OLD_M[v[2]] for v in inp.values()); return c, (c['T'], np.hypot(old, inf.SOURCE_BIAS[st][1]), OLD_W[canon], st)
CASES = {
 'one stated 1e15 J, main': [mk('stated_energy', {'energy': [1e15, 'J', 'stated']})],
 'one stated 1e15 J, game wiki': [mk('stated_energy', {'energy': [1e15, 'J', 'stated']}, canon='games', st='game')],
 'one scaled 1 km sphere, main': [mk('fragment_sphere', {'diameter': [1000, 'm', 'scaled'], 'j_per_cc': [8, 'J/cm^3', 'scaled']})],
 'one estimated 1 km sphere, main': [mk('fragment_sphere', {'diameter': [1000, 'm', 'estimated'], 'j_per_cc': [8, 'J/cm^3', 'scaled']})],
 'three stated 1e15 J agree, main': [mk('stated_energy', {'energy': [1e15, 'J', 'stated']})] * 3,
 'stated 1e15 main + 1e18 noncanon': [mk('stated_energy', {'energy': [1e15, 'J', 'stated']}), mk('stated_energy', {'energy': [1e18, 'J', 'stated']}, canon='noncanon')],
}
if __name__ == '__main__':
    print('case | new sd/w | new post (med, 90% width) | old post')
    for k, v in CASES.items():
        new = [(c['T'], c['sd'], c['w'], s) for (c, _), s in zip(v, [x[1][3] for x in v])]
        # c['sd'] already includes SOURCE_BIAS extra via effective(); pass base sd back out
        new = [(c['T'], float(np.sqrt(max(c['sd'] ** 2 - inf.SOURCE_BIAS[o[3]][1] ** 2, 1e-12))), c['w'], o[3]) for c, o in v]
        print(k, '|', [(round(n[1], 2), n[2]) for n in new], '|', post(new), '|', post([o for _, o in v]))
