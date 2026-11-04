# S6944 merge_roles.py: merge item_roles-* out.jsonl into plans/ITEM_ROLES.csv; list failed rows to retry. python3 -I merge_roles.py <jobs_dir> <out_csv> <retry_in.jsonl>
import sys,json,glob,csv,re,collections
J,O,RT=sys.argv[1:4]
CL=set('material station_input machine_part vehicle_part ship_part rail_part structure tool_weapon ammo food_drink medicine_rite rite_ingredient currency_trade storage_container energy_fuel automation decor other'.split())
LK=set('economy vehicles ships rail storage rites codex quests progression building machines food spoilage autonomy circuit munitions npc_wages energy'.split())
rows={};bad=[];inp={}
for f in sorted(glob.glob(J+'/item_roles-*/in.jsonl')):
    for l in open(f):
        r=json.loads(l);inp[r['id']]=r
for f in sorted(glob.glob(J+'/item_roles-*/out.jsonl')):
    for l in open(f):
        o=json.loads(l);t=o.get('text','')
        m=re.search(r'\[.*\]',t,re.S)
        try:
            a=json.loads(m.group(0));ids=[x.split('|')[0] for x in inp[o['id']]['prompt'].split('\n')]
            assert [x['id'] for x in a]==ids
            for x in a:
                assert x['role_class'] in CL
                x['links']=[k for k in x.get('links',[]) if k in LK]
                rows[x['id']]=x
        except Exception: bad.append(o['id'])
with open(O,'w',newline='') as f:
    w=csv.writer(f);w.writerow('id,role_class,role,where,props,links,decor_only'.split(','))
    for i in sorted(rows):
        x=rows[i];w.writerow([i,x['role_class'],x.get('role',''),x.get('where',''),x.get('props',''),'|'.join(x['links']),x.get('decor_only',False)])
with open(RT,'w') as f:
    for b in set(bad)|(set(inp)-{o for o in set(inp) if all(i in rows for i in [x.split('|')[0] for x in inp[o]['prompt'].split('\n')])}): f.write(json.dumps(inp[b])+'\n')
c=collections.Counter(x['role_class'] for x in rows.values());print(len(rows),'items',len(bad),'bad rows',dict(c))
