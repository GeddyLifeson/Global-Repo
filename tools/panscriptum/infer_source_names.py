# S6966 Fills inferred_source in PANSCRIPTUM_MASTER.tsv from the wiki lead text: template OfficialName/MainPage/Name field, else the words before "is/was a/an/the". No AI; blank when the lead has no name.
# Usage: python3 -I infer_source_names.py MASTER.tsv OUT.tsv
import csv, json, re, sys
L = '/mnt/project-files/assay-c3m/leads/'
T = re.compile(r'\|\s*(?:OfficialName|MainPage|Name|Title|Real Name|Alias)\s*=\s*([^|}\n]+)')
I = re.compile(r"^\s*(?:'''|\")?([A-Z0-9][^.,:;()|{}\n]{1,60}?)(?:'''|\")?\s+(?:is|was|are|were)\s+(?:a|an|the|one|also|best|known|\d)\b")
rows = list(csv.reader(open(sys.argv[1]), delimiter='\t')); H = rows[0]
need = {}
for r in rows[1:]:
    if r[6]: need.setdefault(r[6], set()).add(int(r[7]))
got = {}
for w, idx in need.items():
    for l in open(L + w + '.jsonl'):
        d = json.loads(l)
        if d['i'] not in idx: continue
        t = d['text']; m = T.search(t) if t.lstrip().startswith('{{') else I.match(t)
        if m: got[(w, d['i'])] = m.group(1).strip().replace('"', '')[:80]
n = 0
with open(sys.argv[2], 'w', newline='') as o:
    wr = csv.writer(o, delimiter='\t', lineterminator='\n'); wr.writerow(H)
    for r in rows[1:]:
        if r[6]:
            r[8] = got.get((r[6], int(r[7])), ''); n += bool(r[8])
        wr.writerow(r)
print(n, 'of', sum(1 for r in rows[1:] if r[6]))
