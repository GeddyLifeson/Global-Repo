#!/usr/bin/env python3
"""S6961 extract_being_powers.py: map every Panscriptum being to power ids by keyword scan of its data card (name + summary). No AI.
Usage: python3 -I extract_being_powers.py [--db library.sqlite] [--pool POWER_POOL.tsv] [--out being_powers.tsv] [--stats] [--find ARCHETYPE]
Out TSV: id, name, realm, power_ids (highest tier first). Scalable powers carry :magnitude (1-10) from card scale words."""
import re, sqlite3, sys, csv, argparse
from collections import Counter, defaultdict
P = '/mnt/project-files/'
ap = argparse.ArgumentParser()
ap.add_argument('--db', default=P + 'codex-store/library.sqlite')
ap.add_argument('--pool', default=P + 'plans/powers/POWER_POOL.tsv')
ap.add_argument('--grants', default=P + 'plans/powers/ARCHETYPE_GRANTS.tsv')
ap.add_argument('--out', default='being_powers.tsv')
ap.add_argument('--stats', action='store_true')
ap.add_argument("--find", nargs="*", default=None, help='archetype names from ARCHETYPE_GRANTS (or all)')
a = ap.parse_args()

def rx(kw):
    return re.compile(r'\b(?:' + '|'.join(k.strip() for k in kw.split('|') if k.strip()) + r')\b', re.I)

# scale words -> magnitude 1-10 (README.md in plans/powers); highest hit wins, default 1
SCALE = [(10, r'splits? (whole )?worlds?|shatters? (stars?|worlds?)|stars?-scale|universe|omniverse|galax\w+'), (9, r'planets?|planetary'),
         (8, r'moons?'), (7, r'oceans?|continents?'), (6, r'islands?'), (5, r'mountains?|ridgelines?'), (4, r'cit(y|ies)|towns?'),
         (3, r'buildings?|tanks?|towers?|spires?'), (2, r'city blocks?|streets?|walls?')]
SCALE = [(m, re.compile(r'\b(?:' + w + r')\b', re.I)) for m, w in SCALE]
def magnitude(text):
    return next((m for m, r in SCALE if r.search(text)), 1)

pool = list(csv.DictReader(open(a.pool), delimiter='\t'))
pat = {p['id']: rx(p['keywords']) for p in pool}
scalable = {p['id'] for p in pool if p['magnitude'] != '-'}
slot = {p['id']: p['slot'] for p in pool}

def powers(text):
    m = magnitude(text)
    hits = [pid + (':%d' % m if pid in scalable else '') for pid, r in pat.items() if r.search(text)]
    return hits

c = sqlite3.connect('file:%s?mode=ro' % a.db, uri=True)
cnt, n, withp = Counter(), 0, 0
rows = []
for i, nm, realm, s in c.execute("select id,name,realm,summary from entry where kind='being'"):
    n += 1
    ps = powers(nm + '. ' + (s or ''))
    if realm == 'Ki' and 'ki_resource' not in ps: ps.append('ki_resource')
    if ps:
        withp += 1; cnt.update(ps)
        rows.append((i, nm, realm, ','.join(ps)))
with open(a.out, 'w') as f:
    for r in rows: f.write('\t'.join(r) + '\n')
print(f'{n} beings, {withp} with at least one power -> {a.out}', file=sys.stderr)
if a.stats:
    for k, v in cnt.most_common(): print(k, v)
if a.find is not None:
    G = dict(l.split('\t') for l in open(a.grants).read().splitlines()[1:])
    for name in (a.find or G):
        want = {re.sub(r'_\d$', '', x) for x in G[name].split(',')}
        print('==', name)
        for k, r in sorted(((len(want & {x.split(':')[0] for x in r[3].split(',')}), r) for r in rows), key=lambda x: -x[0])[:8]: print(k, r[0], r[1], r[3])
