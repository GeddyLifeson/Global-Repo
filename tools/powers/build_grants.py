# S6963 build_grants.py: turn the extraction step's being-to-power list into kubejs/data/diaithir/powers/grants.json.
# Input TSV (header row): key<TAB>pool ids (comma, priority order)<TAB>count (optional). key = library id, or entity type id for plain mobs.
# Run: python3 -I build_grants.py BEINGS.tsv POOL.json OUT_grants.json [MAX_PER_BEING]. Unknown pool ids stop the run.
import csv,json,sys
rows=csv.reader(open(sys.argv[1],encoding='utf-8'),delimiter='\t'); next(rows)
pool=json.load(open(sys.argv[2])); out={}; bad=[]; cap=int(sys.argv[4]) if len(sys.argv)>4 else 99
for r in rows:
    if not r or not r[0].strip(): continue
    ids=[x for x in r[1].split(',') if x]; bad+=[x for x in ids if x not in pool]
    out[r[0]]=ids[:min(cap,int(r[2]) if len(r)>2 and r[2] else cap)]
if bad: sys.exit('unknown pool ids: '+', '.join(sorted(set(bad))))
json.dump(out,open(sys.argv[3],'w'),separators=(',',':')); print(len(out),'beings')
