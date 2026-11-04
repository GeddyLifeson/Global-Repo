#!/usr/bin/env python3
"""S6961 extract_being_powers.py: map every Panscriptum being to power ids by keyword scan of its data card (name + summary). No AI.
Usage: python3 -I extract_being_powers.py [--db library.sqlite] [--pool POWER_POOL.tsv] [--out being_powers.tsv] [--stats] [--find ARCHETYPE]
Out TSV: id, name, realm, power_ids (highest tier first). Within a family (super_speed_1/2/3) only the top matching tier is kept."""
import re, sqlite3, sys, csv, argparse
from collections import Counter, defaultdict
P = '/mnt/project-files/'
ap = argparse.ArgumentParser()
ap.add_argument('--db', default=P + 'codex-store/library.sqlite')
ap.add_argument('--pool', default=P + 'plans/powers/POWER_POOL.tsv')
ap.add_argument('--grants', default=P + 'plans/powers/ARCHETYPE_GRANTS.tsv')
ap.add_argument('--out', default='being_powers.tsv')
ap.add_argument('--stats', action='store_true')
ap.add_argument('--find', nargs='*', help='archetype names from ARCHETYPE_GRANTS (or all)')
a = ap.parse_args()

def rx(kw):
    parts = []
    for k in kw.split('|'):
        k = k.strip()
        if not k: continue
        short = len(re.sub(r'[^a-z]', '', k)) <= 3
        parts.append(r'\b' + k + (r'\b' if short or k.endswith(')') and False else (r'\b' if short else '')))
    return re.compile('|'.join(parts), re.I)

pool = list(csv.DictReader(open(a.pool), delimiter='\t'))
fam = lambda i: re.sub(r'_\d$', '', i)
pat = {p['id']: rx(p['keywords']) for p in pool}
tier = {p['id']: int(p['tier']) for p in pool}

def powers(text):
    best = {}
    for pid, r in pat.items():
        if r.search(text):
            f = fam(pid)
            if f not in best or tier[pid] > tier[best[f]]: best[f] = pid
    return sorted(best.values(), key=lambda i: (-tier[i], i))

c = sqlite3.connect('file:%s?mode=ro' % a.db, uri=True)
cnt, n, withp = Counter(), 0, 0
rows = []
for i, nm, realm, s in c.execute("select id,name,realm,summary from entry where kind='being'"):
    n += 1
    ps = powers(nm + '. ' + (s or ''))
    if ps:
        withp += 1; cnt.update(ps)
        rows.append((i, nm, realm, ','.join(ps)))
with open(a.out, 'w') as f:
    for r in rows: f.write('\t'.join(r) + '\n')
print(f'{n} beings, {withp} with at least one power -> {a.out}', file=sys.stderr)
if a.stats:
    for k, v in cnt.most_common(): print(k, v)
if a.find:
    G = dict(l.split('\t') for l in open(a.grants).read().splitlines()[1:])
    for name in (a.find or G):
        want = set(G[name].split(','))
        print('==', name)
        for k, r in sorted(((len(want & set(r[3].split(','))), r) for r in rows), key=lambda x: -x[0])[:8]: print(k, r[0], r[1], r[3])
