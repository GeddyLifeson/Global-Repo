#!/usr/bin/env python3
"""S6985 helper: c3m feat maths. compute() turns a judged feat (template + inputs with units) into a tier using c3m measure.py and
inference.py (verbatim copies in c3m_lib/, from c3m.zip). Template names/units come from assay-c3m/SYSTEM_PROMPT.txt.
Tier = log10 joules (AP, Dur) or log10 m/s (v). Source weighting = inference.SOURCE_BIAS via Feat.effective()."""
import importlib.util, os, math, sys
HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name):
    sp = importlib.util.spec_from_file_location('c3m_' + name, os.path.join(HERE, 'c3m_lib', name + '.py'))
    m = importlib.util.module_from_spec(sp); sys.modules['c3m_' + name] = m; sp.loader.exec_module(m); return m
measure, inference = _load('measure'), _load('inference')
# unit -> (SI factor, dimension)
U = {'J': (1, 'E'), 'kJ': (1e3, 'E'), 'MJ': (1e6, 'E'), 'GJ': (1e9, 'E'), 'erg': (1e-7, 'E'), 'calorie': (4.184, 'E'),
     'ton_TNT': (4.184e9, 'E'), 'kiloton_TNT': (4.184e12, 'E'), 'megaton_TNT': (4.184e15, 'E'),
     'W': (1, 'P'), 'kW': (1e3, 'P'), 'MW': (1e6, 'P'), 'GW': (1e9, 'P'),
     'g': (1e-3, 'M'), 'kg': (1, 'M'), 'tonne': (1e3, 'M'),
     'mm': (1e-3, 'L'), 'cm': (1e-2, 'L'), 'm': (1, 'L'), 'km': (1e3, 'L'), 'light_year': (9.4607e15, 'L'),
     'cm^3': (1e-6, 'V'), 'm^3': (1, 'V'), 'km^3': (1e9, 'V'),
     's': (1, 'T'), 'min': (60, 'T'), 'h': (3600, 'T'), 'day': (86400, 'T'), 'year': (31557600, 'T'),
     'm/s': (1, 'S'), 'km/h': (1 / 3.6, 'S'), 'c': (299792458.0, 'S'),
     'J/cm^3': (1, 'JCC'), 'J/kg': (1, 'JKG'), 'J/(kg*K)': (1, 'CP'), 'K': (1, 'DT'), 'delta_degC': (1, 'DT')}
# template -> {input: dimension}
T = {'kinetic': {'mass': 'M', 'speed': 'S'}, 'fragment_sphere': {'diameter': 'L', 'j_per_cc': 'JCC'},
     'fragment_volume': {'volume': 'V', 'j_per_cc': 'JCC'},
     'vaporize': {'mass': 'M', 'heat_capacity': 'CP', 'delta_t': 'DT', 'latent_heat': 'JKG'},
     'uniform_sphere_gbe': {'mass': 'M', 'radius': 'L'}, 'luminous': {'power': 'P', 'duration': 'T'},
     'travel': {'distance': 'L', 'duration': 'T'}, 'stated_energy': {'energy': 'E'}, 'stated_speed': {'speed': 'S'}}
AXIS = {'kinetic': 'AP Dur', 'fragment_sphere': 'AP Dur', 'fragment_volume': 'AP Dur', 'vaporize': 'AP Dur', 'uniform_sphere_gbe': 'AP Dur',
        'luminous': 'AP Dur', 'stated_energy': 'AP Dur', 'travel': 'v', 'stated_speed': 'v'}
# Baseline (plans/powers/judge/BASELINE_CANON_METHOD.md, refinable): calculation sd in tiers = sqrt(FLOOR[tpl]^2 + sum((EXP*INPUT_SD[method])^2)).
INPUT_SD = {'stated': 0.05, 'measured': 0.08, 'scaled': 0.20, 'estimated': 0.40}   # 1 sd of log10(input), dex
METHOD_SD = INPUT_SD                                                              # known method names
EXP = {'kinetic': {'mass': 1, 'speed': 2}, 'fragment_sphere': {'diameter': 3, 'j_per_cc': 1}, 'fragment_volume': {'volume': 1, 'j_per_cc': 1},
       'vaporize': {'mass': 1, 'heat_capacity': 1, 'delta_t': 1, 'latent_heat': 1}, 'uniform_sphere_gbe': {'mass': 2, 'radius': 1},
       'luminous': {'power': 1, 'duration': 1}, 'travel': {'distance': 1, 'duration': 1}, 'stated_energy': {'energy': 1}, 'stated_speed': {'speed': 1}}
FLOOR = {'kinetic': .10, 'fragment_sphere': .30, 'fragment_volume': .30, 'vaporize': .20, 'uniform_sphere_gbe': .15,
         'luminous': .10, 'travel': .10, 'stated_energy': .05, 'stated_speed': .05}   # template/convention error, dex
# w = s0^2/(s0^2+sc^2), s0=.3 typical calc sd, sc = extra scatter vs main canon (extended .3, noncanon .6). Games = 1: SOURCE_BIAS('game') already shifts +.5 tiers and adds sd .5.
CANON_W = {'main': 1.0, 'extended': 0.5, 'games': 1.0, 'noncanon': 0.2}
class FeatError(ValueError): pass
def si(inputs, tpl):
    if tpl not in T: raise FeatError(f'unknown template {tpl}')
    if set(inputs) != set(T[tpl]): raise FeatError(f'{tpl} needs inputs {sorted(T[tpl])}')
    v = {}
    for k, dim in T[tpl].items():
        val, unit = inputs[k][0], inputs[k][1]
        if unit not in U or U[unit][1] != dim: raise FeatError(f'input {k}: unit {unit!r} is not a {dim} unit')
        if not (isinstance(val, (int, float)) and val > 0): raise FeatError(f'input {k}: value must be positive')
        v[k] = val * U[unit][0]
    return v
def compute(f):
    """f = {a, tpl, in:{name:[value,unit,method]}, st, canon} -> {T, off, sd, w}. Raises FeatError."""
    tpl = f['tpl']; v = si(f['in'], tpl)
    if f['a'] not in AXIS[tpl].split(): raise FeatError(f'template {tpl} cannot score axis {f["a"]}')
    if tpl == 'kinetic': t = measure.tier(0.5 * v['mass'] * v['speed'] ** 2)
    elif tpl == 'fragment_sphere': t = measure.sphere_frag_tier(v['diameter'], v['j_per_cc'])
    elif tpl == 'fragment_volume': t = measure.tier(v['volume'] * 1e6 * v['j_per_cc'])
    elif tpl == 'vaporize': t = measure.tier(v['mass'] * (v['heat_capacity'] * v['delta_t'] + v['latent_heat']))
    elif tpl == 'uniform_sphere_gbe': t = measure.tier(measure.uniform_sphere_gbe(v['mass'], v['radius']))
    elif tpl == 'luminous': t = measure.tier(v['power'] * v['duration'])
    elif tpl == 'stated_energy': t = measure.tier(v['energy'])
    elif tpl == 'travel': t = math.log10(v['distance'] / v['duration'])
    else: t = math.log10(v['speed'])
    methods = [x[2] for x in f['in'].values()]
    if any(m not in METHOD_SD for m in methods): raise FeatError('unknown method')
    sd = math.sqrt(FLOOR[tpl] ** 2 + sum((EXP[tpl][k] * INPUT_SD[x[2]]) ** 2 for k, x in f['in'].items()))
    st = f.get('st') or 'primary'
    ft = inference.Feat(float(t), sd, CANON_W[f.get('canon', 'main')], st if st in inference.SOURCE_BIAS else 'primary')
    x, off, sde = ft.effective()
    return {'T': round(float(x), 4), 'off': off, 'sd': round(float(sde), 4), 'w': ft.w}
