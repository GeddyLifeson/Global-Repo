"""S6865. Derive charter-style assay decimals (M<k>.dd +- iv) from scored c3m P values. Deterministic, no model calls.
P band floors = c3m refile.M_FLOOR (charter ruin edges, Axiom 22). Only status 'scored' entries get a decimal (H5: no worksheet, no number)."""
import gzip, glob, json, sqlite3
F = [20, 70, 120, 240, 324, 418, 510, 590, 700, 850, 990, 1000]
db = sqlite3.connect('/mnt/project-files/library-content/content.sqlite')
db.execute("drop table if exists assay_decimal")
db.execute("create table assay_decimal(id text primary key, p int, band text, decimal real, plusminus real, label text, third text)")
n = 0
for f in sorted(glob.glob('/mnt/project-files/assay-c3m/originate/final/*.jsonl.gz')):
    for line in gzip.open(f, 'rt'):
        r = json.loads(line)
        if r.get('status') not in ('scored', 'scored-one-axis') or r.get('p') is None: continue
        p = r['p']; k = max((i for i in range(11) if F[i] <= p), default=None)
        if k is None: continue
        w = F[k + 1] - F[k]
        d = min((p - F[k]) / w, 0.99); d = round(d, 2)
        pm = round(max(((r['hi'] - r['lo']) / 2) / w, 0.01), 2)
        third = 'shallow' if d < .33 else 'solid' if d < .67 else 'deep'
        db.execute("insert into assay_decimal values(?,?,?,?,?,?,?)", (r['id'], p, f'M{k}', d, pm, f'𝔄 M{k}.{int(d*100):02d} ± {pm:.2f}', third)); n += 1
db.commit(); print(n)
