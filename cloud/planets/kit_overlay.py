# Layers each planet's real-entry kit (specs/<id>.json["kit"]) on top of the archetype families already applied by
# rewrite-jars/biomes-dimensions/tools/planets/planetfeat.py. Run AFTER planetfeat. Writes into the module's worldgen/.
# Reskins family trees with the planet's log/leaves, scales ore veins by the planet's richness, adds extra trees,
# undergrowth and flowers. Shared files keyed by content so planets with equal kits share features.
import json,re,sys,os,glob,hashlib
M='/home/user/diaithir-ports/diaithir-overworld-biomes/src/main/resources/data/diaithir_planets/worldgen'
SP='/mnt/project-files/planets/specs'; VF='/mnt/project-files/planets/base/vf'
ORES={'coal':'coal_ore','iron':'iron_ore','copper':'copper_ore','gold':'gold_ore','redstone':'redstone_ore','lapis':'lapis_ore','diamond':'diamond_ore'}
def rj(k,n):
    try: return json.load(open(f'{M}/{k}/{n}.json'))
    except Exception: return None
def wj(k,n,o):
    os.makedirs(f'{M}/{k}',exist_ok=True); json.dump(o,open(f'{M}/{k}/{n}.json','w'),separators=(',',':'))
def h(*a): return hashlib.sha1('|'.join(map(str,a)).encode()).hexdigest()[:8]
def ref(x): return x.split(':',1)[1] if x.startswith('diaithir_planets:') else None
def reskin(cf,log,leaves):
    t=json.dumps(cf)
    t=re.sub(r'minecraft:[a-z_]+_log',lambda m:'minecraft:'+(log if log.endswith('stem') else log+'_log'),t)
    t=re.sub(r'minecraft:[a-z_]+_leaves',lambda m:'minecraft:'+leaves+'_leaves',t)
    return json.loads(t)
def scale(pf,m):
    for pl in pf['placement']:
        if pl.get('type')=='minecraft:count' and isinstance(pl.get('count'),int): pl['count']=max(1,round(pl['count']*m))
def patch(block,count):
    nm=f'k_{block}_{count}'
    if not os.path.exists(f'{M}/placed_feature/{nm}.json'):
        st={"Name":"minecraft:"+block}
        wj('configured_feature',nm,{"type":"minecraft:simple_block","config":{"to_place":{"type":"minecraft:simple_state_provider","state":st}}})
        wj('placed_feature',nm,{"feature":"diaithir_planets:"+nm,"placement":[{"type":"minecraft:count","count":count*8},{"type":"minecraft:in_square"},{"type":"minecraft:heightmap","heightmap":"MOTION_BLOCKING_NO_LEAVES"},{"type":"minecraft:biome"},{"type":"minecraft:block_predicate_filter","predicate":{"type":"minecraft:all_of","predicates":[{"type":"minecraft:replaceable"},{"type":"minecraft:matching_fluids","fluids":"minecraft:empty"},{"type":"minecraft:would_survive","state":st}]}}]})
    return 'diaithir_planets:'+nm
def extra_tree(t,n):
    nm=f'kt_{t["base"]}_{t["log"]}_{t["leaves"]}_{n}'
    if not os.path.exists(f'{M}/placed_feature/{nm}.json'):
        cf=reskin(json.load(open(f'{VF}/cf_{t["base"]}.json')),t['log'],t['leaves']); wj('configured_feature',nm,cf)
        pl=json.load(open(f'{VF}/pf_trees_plains.json')); pl['feature']='diaithir_planets:'+nm; pl['placement'][0]={"type":"minecraft:count","count":n}; wj('placed_feature',nm,pl)
    return 'diaithir_planets:'+nm
cache={}
def adapt(pid,k,pfid):
    """returns replacement placed id for a family placed feature, or None to drop it"""
    if re.search(r'_m\d_\d$|_k[0-9a-f]{8}$',pfid): return pfid
    key=(pfid,json.dumps(k,sort_keys=True))
    if key in cache: return cache[key]
    pf=rj('placed_feature',ref(pfid)); out=pfid
    if pf and isinstance(pf.get('feature'),str) and ref(pf['feature']):
        cf=rj('configured_feature',ref(pf['feature'])); txt=json.dumps(cf)
        if cf and '_log' in txt and k.get('trees'):
            t=k['trees'][0]; nm=f'{ref(pfid)}_k{h(t["log"],t["leaves"])}'
            if not os.path.exists(f'{M}/placed_feature/{nm}.json'):
                wj('configured_feature',nm,reskin(cf,t['log'],t['leaves'])); p2=dict(pf); p2['feature']='diaithir_planets:'+nm; wj('placed_feature',nm,p2)
            out='diaithir_planets:'+nm
        elif cf and re.search(r'minecraft:(coal|iron|copper|gold|redstone|lapis|diamond)_ore',txt):
            o=re.search(r'minecraft:(coal|iron|copper|gold|redstone|lapis|diamond)_ore',txt).group(1)
            m=round(float((k.get('ores') or {}).get(o,1.0))*2)/2
            if m<=0: out=None
            elif m!=1.0:
                nm=f'{ref(pfid)}_m{str(m).replace(".","_")}'
                if not os.path.exists(f'{M}/placed_feature/{nm}.json'):
                    p2=json.loads(json.dumps(pf)); scale(p2,m); wj('placed_feature',nm,p2)
                out='diaithir_planets:'+nm
    cache[key]=out; return out
def main(ids):
    n=0
    for sp in sorted(glob.glob(SP+'/*.json')):
        pid=os.path.basename(sp)[:-5]; s=json.load(open(sp)); k=s.get('kit')
        if not k or pid=='alaima' or (ids and pid not in ids): continue
        dens=float(k.get('density',1.0)); extra=[]
        for i,t in enumerate(k.get('trees') or []):
            if i==0: continue
            c=max(1,round(3*dens*int(t.get('weight',1)))); extra.append(extra_tree(t,c))
        for u in k.get('undergrowth') or []: extra.append(patch(u['block'],max(1,round(2*int(u.get('weight',2))*max(0.5,dens)))))
        for f in k.get('flowers') or []: extra.append(patch(f,1))
        for bf in glob.glob(f'{M}/biome/{pid}_*.json'):
            if bf.endswith(('_sea.json','_deep_sea.json','_shore.json','_river.json','_hollows.json','_grottoes.json')): continue
            d=json.load(open(bf)); ft=d['features']
            for st in (6,9):
                new=[]
                for x in ft[st]:
                    if x.startswith('diaithir_planets:k') and ('/' not in x) and x.split(':')[1].startswith(('kt_','k_')): continue
                    y=adapt(pid,k,x) if x.startswith('diaithir_planets:') else x
                    if y: new.append(y)
                ft[st]=new
            ft[9]=ft[9]+extra
            json.dump(d,open(bf,'w'),separators=(',',':')); n+=1
    print('biomes layered',n)
if __name__=='__main__': main(set(sys.argv[1:]))
# fix-up: planetfeat prefixes vanilla refs (e.g. minecraft:huge_red_mushroom) with the family; point missing ones back to vanilla.
def fixrefs():
    for f in glob.glob(M+'/configured_feature/*.json'):
        t=open(f).read(); ch=False
        for m in set(re.findall(r'diaithir_planets:([a-z0-9_]+)',t)):
            if not os.path.exists(f'{M}/configured_feature/{m}.json') and not os.path.exists(f'{M}/placed_feature/{m}.json'):
                v=re.sub(r'^[a-z_]+?_[abc]_','',m); t=t.replace('diaithir_planets:'+m,'minecraft:'+v); ch=True
        if ch: open(f,'w').write(t)
fixrefs()
