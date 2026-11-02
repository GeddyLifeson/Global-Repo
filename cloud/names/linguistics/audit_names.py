# S0311 Audits every culture name in names/*.json against names/linguistics/rules/<slug>.json (graphemes, forbidden patterns, word length); writes audit.json + audit_summary.csv
# python3 -I audit_names.py
import csv, glob, json, os, re, unicodedata
R = '/mnt/project-files/names'
rules = {}
for f in glob.glob(R + '/linguistics/rules/*.json'):
    d = json.load(open(f))
    g = sorted({x.lower() for x in d['allowed_graphemes'] if x}, key=len, reverse=True)
    extra = set(d['extra_allowed_chars'].lower()) | set(" -'’.")
    pats = []
    for p in d['forbidden_patterns']:
        try: pats.append(re.compile(p))
        except re.error: pass
    rules[d['slug']] = (g, extra, pats, d['max_word_length'])

def check(slug, name):
    g, extra, pats, mx = rules[slug]
    n = unicodedata.normalize('NFC', name.lower())
    out = []
    for w in re.split(r"[ \-]+", n):
        if len(w) > mx: out.append('long:' + w)
    i = 0
    while i < len(n):
        if n[i] in extra: i += 1; continue
        for x in g:
            if n.startswith(x, i): i += len(x); break
        else:
            out.append('char:' + n[i]); i += 1
    for p in pats:
        m = p.search(n)
        if m: out.append('forbidden:' + p.pattern)
    return out

bad = {}; tot = {}
for f in sorted(glob.glob(R + '/*.json')):
    try: d = json.load(open(f))
    except Exception: continue
    if not isinstance(d, dict): continue
    for eid, v in d.items():
        if not isinstance(v, dict): continue
        for s, name in v.items():
            if s in rules and isinstance(name, str):
                tot[s] = tot.get(s, 0) + 1
                r = check(s, name)
                if r: bad.setdefault(s, []).append([os.path.basename(f), eid, name, r[:3]])
json.dump(bad, open(R + '/linguistics/audit.json', 'w'), ensure_ascii=False)
w = csv.writer(open(R + '/linguistics/audit_summary.csv', 'w'))
w.writerow(['slug', 'names', 'failing', 'pct'])
for s in sorted(tot): w.writerow([s, tot[s], len(bad.get(s, [])), round(100 * len(bad.get(s, [])) / tot[s], 1)])
print(sum(tot.values()), sum(len(x) for x in bad.values()))
