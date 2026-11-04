# S6969 Full source-page coverage: every lead page of every source wiki vs the Library. No AI.
# For each wiki: lead pages, pages with an assay entry, entries filed in the Library, being-kind pages, named pages; lists unlinked pages with a name guess.
# Usage: python3 -I coverage_check.py OUT_DIR   (reads /mnt/project-files)
import json, os, re, sqlite3, sys, csv, glob, collections
P = '/mnt/project-files/'; out = sys.argv[1]; os.makedirs(out, exist_ok=True)
db = sqlite3.connect('file:' + P + 'codex-store/library.sqlite?mode=ro', uri=True)
inlib = {s for (s,) in db.execute("select summary from entry where id like '%.assay.%'")}
am = {}
for l in open(P + 'library-content/assay_merged.jsonl'):
    d = json.loads(l); am[d['id']] = (d['kind'], d['summary'] in inlib)
T = re.compile(r'\|\s*(?:OfficialName|MainPage|Name|Title|Real Name|Alias)\s*=\s*([^|}\n]+)')
I = re.compile(r"^\s*(?:'''|\")?([A-Z0-9][^.,:;()|{}\n]{1,60}?)(?:'''|\")?\s+(?:is|was|are|were)\s+(?:a|an|the|one|also|best|known|\d)\b")
tot = collections.Counter(); S = csv.writer(open(out + '/coverage_by_source.tsv', 'w'), delimiter='\t', lineterminator='\n')
S.writerow(['source', 'lead_pages', 'empty_leads', 'with_entry_in_library', 'entry_not_in_library', 'no_entry', 'no_entry_named', 'no_entry_unnamed', 'beings_with_entry'])
U = csv.writer(open(out + '/unlinked_pages.tsv', 'w'), delimiter='\t', lineterminator='\n'); U.writerow(['source', 'lead_idx', 'name_guess', 'lead_start'])
for f in sorted(glob.glob(P + 'assay-c3m/leads/*.jsonl')):
    w = os.path.basename(f)[:-6]; c = collections.Counter()
    for l in open(f):
        d = json.loads(l); t = d['text']; c['pages'] += 1
        if not t.strip(): c['empty'] += 1
        a = am.get(f"{w}|{d['i']}")
        if a is None:
            c['none'] += 1; m = (T.search(t) if t.lstrip().startswith('{{') else I.match(t))
            c['named' if m else 'unnamed'] += 1
            if t.strip(): U.writerow([w, d['i'], m.group(1).strip().replace('"', '')[:80] if m else '', t[:100].replace('\t', ' ').replace('\n', ' ')])
        elif a[1]: c['lib'] += 1; c['being'] += a[0] == 'being'
        else: c['notlib'] += 1
    S.writerow([w, c['pages'], c['empty'], c['lib'], c['notlib'], c['none'], c['named'], c['unnamed'], c['being']]); tot.update(c)
print(dict(tot))
