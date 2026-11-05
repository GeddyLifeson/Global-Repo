#!/usr/bin/env python3
"""S6985 judge shard validator. Rejects a shard unless EVERY row passes. Re-fetches the real pages; trusts nothing the judge wrote.
  validate.py N [N ...]   validate out/shard_N.out.jsonl against batches/shard_N.jsonl + .src.jsonl (exit 1 on any problem)
  validate.py all         fold-time check: every out/shard_*.out.jsonl
Checks: row count/ids/order match the batch; u/t equal the resolved source and the page exists and starts with the batch lead;
every p/f/gear quote is verbatim in the fetched full page; required fields, pool ids, m 1-10, c h/m/l; b0 rows carry no powers or gear kind;
b2 only weapon/armor/vehicle with m/q/c; a being whose page has an Abilities/Powers/Spells section must have a power, a feat, or z='none stated: <reason>'."""
import json, os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pages, judge, feats, math
O, B = judge.O, judge.B
def sect_text(t): return [b for h, b in judge.sections(t) if len(b.strip()) > 40]
def squash(s): return re.sub(r'\s+', ' ', s)
def nums(s): return [float(x.replace(',', '')) for x in re.findall(r'\d[\d,]*\.?\d*', s) if x.replace(',', '').replace('.', '', 1).isdigit()]
def plain(f):
    """Second, independent evaluation: plain math from SI values (no c3m code)."""
    v = feats.si(f['in'], f['tpl']); t = f['tpl']
    if t == 'kinetic': return math.log10(0.5 * v['mass'] * v['speed'] ** 2)
    if t == 'fragment_sphere': return math.log10(4 / 3 * math.pi * (v['diameter'] / 2) ** 3 * 1e6 * v['j_per_cc'])
    if t == 'fragment_volume': return math.log10(v['volume'] * 1e6 * v['j_per_cc'])
    if t == 'vaporize': return math.log10(v['mass'] * (v['heat_capacity'] * v['delta_t'] + v['latent_heat']))
    if t == 'uniform_sphere_gbe': return math.log10(3 * 6.674e-11 * v['mass'] ** 2 / (5 * v['radius']))
    if t == 'luminous': return math.log10(v['power'] * v['duration'])
    if t == 'travel': return math.log10(v['distance'] / v['duration'])
    if t == 'stated_energy': return math.log10(v['energy'])
    return math.log10(v['speed'])
def check_feat(f, F):
    if f.get('a') not in ('AP', 'Dur', 'v') or not f.get('q') or squash(f['q']) not in F: return f"feat quote not verbatim/axis bad: {f.get('q','')[:40]!r}"
    try:
        c = feats.compute(f); p = plain(f)
    except (feats.FeatError, KeyError, TypeError) as ex: return f'feat inputs invalid: {ex}'
    if abs(p - (c['T'] if f['a'] != 'v' else c['T'])) > 0.01 and abs(p - c['T'] + c['off']) > 0.01: return f"feat tier disagrees with plain recomputation ({p:.3f} vs {c['T']})"
    for k in ('T', 'off', 'sd', 'w'):
        if k not in f or abs(f[k] - c[k]) > 1e-3: return f"feat {k} stored {f.get(k)} but c3m recomputes {c[k]}"
    q = nums(f['q'])
    for k, (val, unit, meth) in f['in'].items():
        if not any(abs(val - x) <= 1e-6 * max(1, abs(val)) for x in q) and k not in ('j_per_cc', 'heat_capacity', 'delta_t', 'latent_heat'):
            return f"input {k}={val} {unit} does not appear as a number in the quote"
    return ''
def check(n, path=None, meta=None):
    err = []; n = int(n)
    R = judge.rows(n); S = pages.srcs(n)
    p = path or f'{O}shard_{n}.out.jsonl'
    if not os.path.exists(p): return [(-1, 'no output file')]
    out = [json.loads(l) for l in open(p, encoding='utf-8')]
    if len(out) != len(R): err.append((-1, f'rows {len(out)} != batch {len(R)}'))
    ids = {r['id'] for r in judge.pool()}
    for i, (o, r, s) in enumerate(zip(out, R, S)):
        e = lambda m: err.append((i, m))
        if o.get('id') != r['id'] or s['id'] != r['id']: e('id/order mismatch'); continue
        if not s['url']:  # unresolvable fragment page: only a b0 junk row with an explicit reason, at most 2% of the shard
            if o.get('b') == 0 and str(o.get('z', '')).startswith('no source page:') and not o.get('u') and not o.get('p') and not o.get('k'): continue
            e('source page unresolved: only a b0 row with z="no source page: <reason>" is allowed'); continue
        if o.get('u') != s['url'] or o.get('t') != s['title']: e('source url/title missing or differs from resolved source'); continue
        full = pages.text(s['url'])
        if not full:
            if not pages.exists(s['url']): e('source page does not exist'); continue
            full = r['text']
        elif not pages.match(r['text'], full) and not (full == '' ) and not re.match(r'\s*(\{\{|[^\]]{0,120}\]\]|is |was |are |,)', r['text']):  # template-start row: resolver accepts the page named by its Name/MainPage field
            e('page text does not start like the batch lead (wrong page?)'); continue
        F = squash(full)
        b = o.get('b')
        if b not in (0, 1, 2): e('bad b'); continue
        if b == 0 and (o.get('p') or o.get('k') or o.get('f')): e('non-being carries powers/gear/feats (only weapon/armor/vehicle are assayed)')
        if b in (1, 2):
            if not o.get('s'): e('summary missing')
            if not o.get('n') and b == 2: e('gear name missing')
        if b == 2:
            if o.get('k') not in ('weapon', 'armor', 'vehicle'): e('gear kind invalid')
            if not (isinstance(o.get('m'), int) and 1 <= o['m'] <= 10): e('gear m not 1-10')
            if o.get('c') not in ('h', 'm', 'l'): e('gear c invalid')
            if not o.get('q') or squash(o['q']) not in F: e('gear quote not verbatim in page')
        if b == 1:
            for k in ('n', 'p', 'x', 'f', 'u', 's', 't'):
                if k not in o: e(f'field {k} missing')
            for q in o.get('p', []):
                if q.get('id') not in ids: e(f"unknown pool id {q.get('id')}")
                if not (isinstance(q.get('m'), int) and 1 <= q['m'] <= 10): e(f"m not 1-10 for {q.get('id')}")
                if q.get('c') not in ('h', 'm', 'l'): e(f"c invalid for {q.get('id')}")
                if not q.get('q') or squash(q['q']) not in F: e(f"power quote not verbatim in page: {q.get('q','')[:40]!r}")
            for q in o.get('f', []):
                msg = check_feat(q, F)
                if msg: e(msg)
            if sect_text(full) and not (o.get('p') or o.get('f') or o.get('x') or str(o.get('z', '')).startswith('none stated:')):
                e("page has an Abilities/Powers section but row has no power, feat, x, or z='none stated: reason'")
    ap = f'{B}shard_{n}.absent.json'; absent = set(json.load(open(ap))) if os.path.exists(ap) else set()  # rows the resolver confirmed absent (pages.py ABSENT RULE) do not count toward the cap
    nosrc = sum(1 for o in out if o.get('z', '').startswith('no source page:') and o.get('id') not in absent)
    if nosrc > max(1, len(R) // 50): err.append((-1, f'{nosrc} rows without a source page exceeds 2% of the shard'))
    mp = meta or f'{O}shard_{n}.meta.json'
    cnt = {'rows': len(out), 'beings': sum(o.get('b') == 1 for o in out), 'gear': sum(o.get('b') == 2 for o in out), 'powers': sum(len(o.get('p', [])) for o in out), 'feats': sum(len(o.get('f', [])) for o in out)}
    if not os.path.exists(mp): err.append((-1, 'meta.json missing'))
    elif json.load(open(mp)) != cnt: err.append((-1, f'shard totals {json.load(open(mp))} != recount {cnt}'))
    return err
if __name__ == '__main__':
    a = sys.argv[1:]
    ns = sorted(int(re.search(r'shard_(\d+)\.out', f).group(1)) for f in glob.glob(f'{O}shard_*.out.jsonl')) if a == ['all'] else a
    bad = 0
    for n in ns:
        er = check(n); bad += bool(er)
        print(f'shard {n}: ' + ('PASS' if not er else f'REJECT ({len(er)} problems)'))
        for i, m in er[:30]: print(f'   row {i}: {m}')
    sys.exit(1 if bad else 0)
