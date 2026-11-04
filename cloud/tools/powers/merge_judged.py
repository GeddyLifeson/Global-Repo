# S6980 Merges validated S6975 judge results (shard/PC outputs) into BEING_POWER_EVIDENCE.tsv, BEING_POWERS.tsv and GEAR_SCALE.tsv via PANSCRIPTUM_MASTER source links.
"""python3 merge_judged.py OUT_DIR RESULT.jsonl[.gz] ...   (reads/rewrites OUT_DIR/BEING_POWER_EVIDENCE.tsv, BEING_POWERS.tsv; writes GEAR_SCALE.tsv, JUDGED_RESULTS.jsonl)
Pages are validated again against their input text (shard files / queue). A being with judged powers replaces its old rows; a being judged with no powers keeps the old rows.
Duplicate page ids: the later result file wins. Join: master.source_wiki + source_lead_idx == page id."""
import json, sys, os, csv, gzip, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import judge_pages as jp
out, files = sys.argv[1], sys.argv[2:]
R = '/mnt/project-files/plans'
text = {}
for f in glob.glob('/mnt/project-files/plans/powers/judge/inthread/shard_??.jsonl') + glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../plans/powers/pcrun/priority.jsonl.gz')):
    for l in (gzip.open(f, 'rt', encoding='utf-8') if f.endswith('.gz') else open(f, encoding='utf-8')):
        d = json.loads(l); text[d['id']] = d['text']
ids = {r['id'] for r in jp.pool_rows()}
res, bad = {}, 0
for f in files:
    for l in (gzip.open(f, 'rt', encoding='utf-8') if f.endswith('.gz') else open(f, encoding='utf-8')):
        d = json.loads(l)
        if d['id'] not in text or 'error' in d: bad += 1; continue
        v, why = jp.validate(text[d['id']], dict(d), ids)
        if v is None: bad += 1; continue
        res[d['id']] = {'id': d['id'], **v}
print('pages', len(res), 'rejected', bad)
key = {}
for r in csv.DictReader(open(f'{R}/PANSCRIPTUM_MASTER.tsv', encoding='utf-8'), delimiter='\t'):
    if r['source_wiki']: key[f"{r['source_wiki']}|{r['source_lead_idx']}"] = r['id']
new = collections.defaultdict(dict)
gear = []
for pid, d in res.items():
    if d['b'] == 2:
        w, i = pid.split('|'); gear.append([w, i, d['k'], d['n'], d['m'], d['q'], d['c']])
    if d['b'] in (1, 2) and d['p'] and pid in key:
        for p in d['p']:
            cur = new[key[pid]].get(p['id'])
            if not cur or p['m'] > cur['m']: new[key[pid]][p['id']] = p
print('beings with judged powers linked', len(new), 'gear rows', len(gear))
with open(f'{out}/BEING_POWER_EVIDENCE.tsv', encoding='utf-8') as f: ev = [l.rstrip('\n').split('\t') for l in f]
ev = [r for r in ev if r[0] not in new]
for k, ps in new.items():
    for p in ps.values(): ev.append([k, p['id'], str(p['m']), 'judge@S6975', {'h': 'high', 'm': 'medium', 'l': 'low'}[p['c']], p['q'].replace('\t', ' ')])
hdr, rest = ev[0], ev[1:]
with open(f'{out}/BEING_POWER_EVIDENCE.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('\t'.join(hdr) + '\n'); f.writelines('\t'.join(r) + '\n' for r in rest)
with open(f'{out}/BEING_POWERS.tsv', encoding='utf-8') as f: bp = [l.rstrip('\n').split('\t') for l in f]
d0 = {r[0]: r for r in bp[1:]}
for k, ps in new.items(): d0[k] = [k, ','.join(f"{p['id']}:{p['m']}" for p in sorted(ps.values(), key=lambda p: -p['m'])), '']
with open(f'{out}/BEING_POWERS.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('\t'.join(bp[0]) + '\n'); f.writelines('\t'.join(r) + '\n' for r in d0.values())
with open(f'{out}/GEAR_SCALE.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('source_wiki\tlead_idx\tkind\tname\tmagnitude\tquote\tconfidence\n'); f.writelines('\t'.join(map(str, r)) + '\n' for r in gear)
with open(f'{out}/JUDGED_RESULTS.jsonl', 'w', encoding='utf-8') as f:
    f.writelines(json.dumps(d, ensure_ascii=False) + '\n' for d in res.values())
