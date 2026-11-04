# S6955 export_kubejs.py: write plans/ITEM_ROLES.csv as per-namespace JSON for the pack (kubejs/data/diaithir/item_roles/<ns>.json). python3 -I export_kubejs.py <roles.csv> <out_dir>
import sys,csv,json,os,re,collections
R=csv.DictReader(open(sys.argv[1]));O=sys.argv[2];os.makedirs(O,exist_ok=True)
by=collections.defaultdict(dict);cl=lambda s:re.sub(r'\s*[—–]\s*',', ',s).strip()
for r in R:
    ns,p=r['id'].split(':',1)
    by[ns][p]=[r['role_class'],cl(r['role'])[:200],cl(r['props'])[:120],r['links'],r['age'],cl(r['where'])[:80]]
for ns,d in by.items():
    json.dump({'ns':ns,'roles':d},open(f'{O}/{ns}.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(by),'namespaces',sum(len(d) for d in by.values()),'items')
