# S0337 Validates progression/graph.json: every system is required to finish the pack, no dead ends, solo-completable, Age-gated, interlocked; optional data pack check. python3 -I check_progression.py graph.json [--report] [--datapack DIR]
import json,sys,os,glob,collections
a=sys.argv[1:]; G=json.load(open(a[0],encoding='utf-8')); rep='--report' in a
dp=a[a.index('--datapack')+1] if '--datapack' in a else None
AG=G['ages']; ai={x:i for i,x in enumerate(AG)}; N=G['nodes']; WIN=G['win']
E=[];W=[]
byid={}
for n in N:
    if n['id'] in byid: E.append('duplicate node '+n['id'])
    byid[n['id']]=n
    if n['system'] not in G['owners']: E.append(f"{n['id']}: unknown system {n['system']}")
    if n['age'] not in ai: E.append(f"{n['id']}: bad age {n['age']}")
    for k in('name','module','quest'):
        if not n.get(k): E.append(f"{n['id']}: missing {k}")
    if not n['makes']: E.append(n['id']+': makes nothing')
    for k in('W','s'):
        if k in n and not(isinstance(n[k],(int,float)) and n[k]>0): E.append(f"{n['id']}: {k} must be a positive number (SI: W, s)")
# producers
prod=collections.defaultdict(list)
for n in N:
    for r in n['makes']: prod[r].append(n)
for n in N:
    for r in n['needs']:
        if r not in prod: E.append(f"{n['id']}: needs {r} but nothing makes it")
# implicit Age gate: non-gate node of Age >= II also needs gate.<age>
def need(n):
    r=list(n['needs'])
    if not n.get('gate') and ai[n['age']]>=1: r.append('gate.'+n['age'])
    if n.get('station') and n['station'] not in r: r.append(n['station'])
    return r
for n in N:
    if n.get('gate') and n['makes']!=['gate.'+AG[ai[n['age']]+1]]: E.append(n['id']+': gate node must make gate.<next age>')
def reach(skip_sys=None):
    have=set(); done=set(); ch=True
    while ch:
        ch=False
        for n in N:
            if n['id'] in done or n.get('coop') or n['system']==skip_sys: continue
            if all(r in have for r in need(n)):
                done.add(n['id']); have.update(n['makes']); ch=True
    return done,have
done,have=reach()
for n in N:
    if n["id"] not in done and not n.get("coop"): E.append(f"{n['id']}: unreachable solo (missing: {[r for r in need(n) if r not in have]})")
# coop-only resources
for r,ps in prod.items():
    if all(p.get('coop') for p in ps): E.append(f"{r}: only coop nodes make it, no solo alternative")
# age monotone
for n in N:
    for r in n['needs']:
        ps=[p for p in prod.get(r,[]) if not p.get('coop')]
        if ps and min(ai[p['age']] for p in ps)>ai[n['age']]:
            E.append(f"{n['id']} (Age {n['age']}) needs {r} first made in Age {min((p['age'] for p in ps),key=ai.get)}")
# dead ends
used=set(r for n in N for r in need(n))
for n in N:
    for r in n['makes']:
        if r not in used and n['id']!=WIN and r not in str(n.get('terminal','')).split(','): E.append(f"{n['id']}: {r} is made but nothing uses it (dead end)")
# every system required
sysn=sorted(set(n['system'] for n in N)-{'win'})
for s in sysn:
    d,h=reach(s)
    if WIN in d: E.append(f"system '{s}' is skippable: the win node is reachable without it")
# interlock
feeds=collections.defaultdict(set); fed=collections.defaultdict(set)
for n in N:
    for r in need(n):
        for p in prod.get(r,[]):
            if p['system']!=n['system'] and n['system']!='win':
                feeds[p['system']].add(n['system']); fed[n['system']].add(p['system'])
for s in sysn:
    if len(feeds[s])<3 or len(fed[s])<3: E.append(f"system '{s}' weakly interlocked: feeds {len(feeds[s])}, fed by {len(fed[s])} (need >=3 each)")
# module map and kept-mod shortcuts
MODS=G.get('modules',{})
for n in N:
    if n['module'] not in MODS: E.append(f"{n['id']}: module {n['module']} missing from graph modules map")
for k in G.get('kept',[]):
    if k['age'] not in ai: E.append(f"kept {k['mod']}: bad age"); continue
    for r in k['makes']:
        ps=[p for p in prod.get(r,[]) if not p.get('coop')]
        if not ps: E.append(f"kept {k['mod']}: {r} not in graph"); continue
        first=min(ai[p['age']] for p in ps)
        if ai[k['age']]<first: E.append(f"kept {k['mod']} (Age {k['age']}) makes {r} before the graph does (Age {AG[first]}): shortcut, raise its Age gate")
# stations, not grids
ST=G.get('stations',{}); FORMS=G.get('forms',{}); SP=tuple(G.get('service_prefixes',[])); rec=[n for n in N if 'item' in n]; grid=0
for n in rec:
    f=n.get('form')
    if f not in FORMS: E.append(f"{n['id']}: item needs a form {sorted(FORMS)}"); continue
    if f=='quick': grid+=1; continue
    if n.get('station') not in ST: E.append(f"{n['id']}: station {n.get('station')} not in stations registry")
    if f=='assembly':
        k=[r for r in n['needs'] if not r.startswith(SP)]
        if len(k)>6: E.append(f"{n['id']}: assembly has {len(k)} part inputs; join major parts only (max 6)")
for r in ST:
    if r not in prod: E.append(f"station {r}: nothing makes it")
share=grid/len(rec) if rec else 0
if share>0.15: E.append(f"crafting-grid recipes are {share:.0%} of item recipes (max 15%): move them onto stations")
# data pack
if dp:
    for f in glob.glob(os.path.join(dp,'data','*','recipe','xmod_*.json')):
        j=json.load(open(f,encoding='utf-8')); nid=j.get('_node'); n=byid.get(nid)
        if not n: E.append(f"{f}: _node {nid} not in graph"); continue
        if n.get('item') and j['result']['id']!=n['item']: E.append(f"{f}: result {j['result']['id']} != graph item {n['item']}")
        for i in j.get('ingredients',[])+[x for r in j.get('pattern',[]) for x in []]:
            if i.startswith('#diaithir:progression/'):
                t=i[1:]; r=t.split('progression/')[1]
                if r not in prod: E.append(f"{f}: tag {t} maps to unknown resource {r}")
print(f"item recipes {len(rec)}, on stations {len(rec)-grid}, crafting grid {grid}")
print(f"nodes {len(N)}, systems {len(sysn)}, resources {len(prod)}, reached {len(done)}/{len(N)}, win {'REACHABLE' if WIN in done else 'NOT REACHABLE'}")
if rep:
    print('\nsystem | nodes | first Age | feeds | fed by')
    for s in sysn:
        ns=[n for n in N if n['system']==s]
        print(f"{s} | {len(ns)} | {min(ai[n['age']] for n in ns) and AG[min(ai[n['age']] for n in ns)] or 'I'} | {len(feeds[s])} {sorted(feeds[s])} | {len(fed[s])}")
    print('\nAge | nodes'); [print(x,sum(1 for n in N if n['age']==x)) for x in AG]
for w in W: print('WARN',w)
for e in E: print('ERROR',e)
print('OK' if not E else f'{len(E)} errors'); sys.exit(1 if E else 0)
