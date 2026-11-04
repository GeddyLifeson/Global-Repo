# S6964 Builds plans/PANSCRIPTUM_MASTER.tsv: one row per Library being (id, name, universe, realm, era, source wiki + lead index, powers, pack entity, card shard). No AI.
# Source link: assay_merged.jsonl id "wiki|n" joins to the Library entry by identical summary; leads/<wiki>.jsonl line n is the original page lead.
# Usage: python3 -I master_sheet.py OUT.tsv  (reads /mnt/project-files)
import sqlite3, json, sys, csv, os
P = '/mnt/project-files/'
out = sys.argv[1]
db = sqlite3.connect('file:' + P + 'codex-store/library.sqlite?mode=ro', uri=True)
src = {}
for l in open(P + 'library-content/assay_merged.jsonl'):
    d = json.loads(l)
    w, n = d['id'].rsplit('|', 1)
    src.setdefault(d['summary'], (w, n))
powers = {}
for l in list(open(P + 'plans/powers/BEING_POWERS.tsv'))[1:]:
    k, *r = l.rstrip('\n').split('\t')
    powers[k] = r[0] if r else ''
shard = {}
for f in os.listdir(P + 'library-content/books/entries'):
    if not f.endswith('.json'): continue
    for ph in json.load(open(P + 'library-content/books/entries/' + f)).values():
        for row in ph if isinstance(ph, list) else []:
            if isinstance(row, list) and row and isinstance(row[0], str): shard[row[0]] = f
H = ['id', 'name', 'universe', 'realm', 'era', 'age', 'source_wiki', 'source_lead_idx', 'inferred_source', 'powers', 'pack_id', 'card_shard']
with open(out, 'w', newline='') as o:
    w = csv.writer(o, delimiter='\t', lineterminator='\n'); w.writerow(H)
    for i, nm, u, rl, er, ag, pk, sm in db.execute("select id,name,universe,realm,era,age,pack_id,summary from entry where kind='being' order by id"):
        s = src.get(sm, ('', ''))
        w.writerow([i, nm, u, rl, er, ag, s[0], s[1], '', powers.get(i, ''), pk or '', shard.get(i, '')])
