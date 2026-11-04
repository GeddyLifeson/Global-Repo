"""Regroup assay tail and retry outputs into per-slug shards the existing importer (panscriptum/c3m/tools_merge_assay.py) understands.
  python3 -I assay_regroup.py   -> compute/jobs/assay-<slug>-t001.. (in.jsonl + out.jsonl, 500 rows each) for every slug; retry rows win over tail rows.
Writes only rows that are skips or parse as a JSON object; already-regrouped ids are not regrouped again. Marks the source tail/retry dirs as merged so the importer does not read them as slugs."""
import glob, json, os
J = '/mnt/project-files/compute/jobs'; LOG = '/mnt/project-files/assay-c3m/merged_shards.txt'
def src(kind):
    out = {}
    for d in sorted(glob.glob(f'{J}/assay-{kind}-*/')):
        try:
            for l in open(d + 'out.jsonl'):
                try: r = json.loads(l); out[r['id']] = r
                except Exception: pass
        except OSError: pass
    return out
rows = src('tail'); rows.update(src('retry'))          # retry wins
bad = lambda t: not isinstance(_p(t), dict)
def _p(t):
    try: return json.loads(t)
    except Exception: return None
by = {}
for i, r in rows.items():
    if bad(r['text']): continue
    by.setdefault(i.split('|')[0], []).append(r)
done = {os.path.basename(p.rstrip('/')) for p in glob.glob(f'{J}/assay-*-t[0-9][0-9][0-9]/')}
made = []
for slug, rs in sorted(by.items()):
    rs.sort(key=lambda r: int(r['id'].split('|')[1]) if r['id'].split('|')[1].isdigit() else 0)
    have = set()
    for p in glob.glob(f'{J}/assay-{slug}-t[0-9][0-9][0-9]/out.jsonl'):
        have |= {json.loads(l)['id'] for l in open(p)}
    rs = [r for r in rs if r['id'] not in have]
    k = len([d for d in done if d.startswith(f'assay-{slug}-t')])
    for a in range(0, len(rs), 500):
        k += 1; d = f'{J}/assay-{slug}-t{k:03d}'; os.makedirs(d, exist_ok=True)
        chunk = rs[a:a + 500]
        open(d + '/in.jsonl', 'w').write(''.join(json.dumps({'id': r['id'], 'prompt': ''}) + '\n' for r in chunk))
        open(d + '/out.jsonl', 'w').write(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in chunk))
        open(d + '/README.md', 'w').write('Regrouped tail/retry rows for one slug (assay_regroup.py). Importer: panscriptum/c3m/tools_merge_assay.py.\n'); made.append(os.path.basename(d))
src_dirs = [os.path.basename(p.rstrip('/')) for p in glob.glob(f'{J}/assay-tail-*/') + glob.glob(f'{J}/assay-retry-*/')]
with open(LOG, 'a') as f: f.write(''.join(x + '\n' for x in src_dirs))
print(len(made), sum(len(v) for v in by.values()))
