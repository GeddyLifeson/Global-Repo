#!/usr/bin/env python3
"""S6985 selftest: breaks a copy of shard 160 in 11 ways and shows validate.py rejecting each one. Run: python3 selftest.py"""
import json, os, sys, copy, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import validate, judge
O = judge.O
base = [json.loads(l) for l in open(f'{O}shard_160.out.jsonl')]
meta = json.load(open(f'{O}shard_160.meta.json'))
def run(name, mut, fix_meta=True, want_reject=True):
    rows = copy.deepcopy(base); mut(rows)
    d = tempfile.mkdtemp(); p = d + '/o.jsonl'; mp = d + '/m.json'
    open(p, 'w').write(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
    m = {'rows': len(rows), 'beings': sum(r['b'] == 1 for r in rows), 'gear': sum(r['b'] == 2 for r in rows), 'powers': sum(len(r.get('p', [])) for r in rows), 'feats': sum(len(r.get('f', [])) for r in rows)} if fix_meta else meta
    json.dump(m, open(mp, 'w'))
    er = validate.check(160, p, mp)
    good = bool(er) == want_reject
    print(('OK   ' if good else 'FAIL ') + ('rejected: ' if er else 'accepted: ') + name + (f' -> {er[0][1][:110]}' if er else ''))
    return good
import feats
def addfeat(r, **kw):  # row 32 (Saviana) quote has a printed number; the feat maths is checked, not the wiki's physics
    q = 'Inflicts 24,500 to 31,500 Fire damage on players in front of her.'
    f = {'a': 'AP', 'q': q, 'tpl': 'stated_energy', 'in': {'energy': [24500, 'J', 'stated']}, 'canon': 'games', 'st': 'game'}
    f.update(feats.compute(f)); f.update(kw); r[32]['f'] = [f]
checks = [
 run('untouched shard 160', lambda r: None, want_reject=False),
 run('correct feat math (24500 J -> tier 4.389, game offset 0.5)', lambda r: addfeat(r), want_reject=False),
 run('wrong tier stored (T=9.9, true 4.389)', lambda r: addfeat(r, T=9.9)),
 run('wrong unit (J given as kg)', lambda r: addfeat(r, **{'in': {'energy': [24500, 'kg', 'stated']}})),
 run('number not in the quote (31 instead of 24500)', lambda r: addfeat(r, **{'in': {'energy': [31, 'J', 'stated']}, 'T': round(__import__('math').log10(31), 4)})),
 run('source weighting wrong (off=0 for a game source)', lambda r: addfeat(r, off=0.0)),
 run('power quote not in the page', lambda r: r[54]['p'][0].update(q='Fires a beam of pure sunlight')),
 run('unknown pool id', lambda r: r[54]['p'][0].update(id='laser_eyes')),
 run('magnitude outside 1-10', lambda r: r[54]['p'][0].update(m=14)),
 run('source URL points at another page', lambda r: r[3].update(u=r[4]['u'])),
 run('non-being carries a power', lambda r: r[4].update(p=[{'id': 'flight', 'm': 1, 'q': 'x', 'c': 'm'}])),
 run('Abilities page left blank with no reason', lambda r: r[75].update(z='')),
]
def drop(rows): rows[0]['b'] = 0
checks.append(run('totals: meta says 23 powers, rows hold 22', lambda r: r[54]['p'].pop(), fix_meta=False))
print('ALL EXPECTATIONS MET:', all(c for c in checks if c is not None))
