#!/usr/bin/env python3
"""python3 validate.py catalogue/<file>.psv [more]  -> prints errors, exit 1 if any."""
import json,re,sys,os
H=os.path.dirname(os.path.abspath(__file__))
R=json.load(open(H+'/regions.json')); UW=json.load(open(H+'/uw_existing.json'))
PL=open(H+'/PLANS.md').read()
GEN=set(); 
for l in PL.splitlines():
    if l and not l.startswith(('#','Every','Pick','`','Rough')) and not l.startswith('uw'):
        GEN|=set(l.split())
UWP=set(UW)
DIET={'herb','carn','omni','pisc','insect','fil','scav','frug','nect'}
HAB=set("forest jungle plains savanna taiga swamp desert badlands mountain icy river lake coast reef ocean_warm ocean_cold ocean_deep cave island tundra grassland wetland".split())
PER=set("Cambrian Ordovician Silurian Devonian Carboniferous Permian Triassic Jurassic Cretaceous Paleocene Eocene Oligocene Miocene Pliocene Pleistocene".split())
ROCK=set("sandstone shale limestone mudstone coal amber chalk marine_sediment volcanic_ash tar permafrost conglomerate".split())
BOX=re.compile(r'^box\((-?\d+(\.\d+)?,){3}-?\d+(\.\d+)?\)$')
def rng(s,e,n):
    if not s.strip(): e.append(f'{n}: empty range'); return
    for r in s.split(';'):
        r=r.strip()
        if r not in R and not BOX.match(r): e.append(f'{n}: unknown region {r!r}')
def plan(p,e,n):
    if p.startswith('uw:'):
        if p[3:] not in UWP: e.append(f'{n}: unknown uw plan {p}')
    elif p.startswith('gen:'):
        if p[4:] not in GEN: e.append(f'{n}: unknown gen plan {p}')
    else: e.append(f'{n}: bad plan {p}')
ids=set(); bad=0
for fn in sys.argv[1:]:
    e=[]; cnt=0
    for i,l in enumerate(open(fn,encoding='utf8'),1):
        l=l.rstrip('\n')
        if not l.strip() or l.startswith('#'): continue
        f=l.split('|'); n=f'{os.path.basename(fn)}:{i}'; cnt+=1
        fossil=fn.endswith('fossil.psv') or 'fossil' in os.path.basename(fn)
        if fossil:
            if len(f)!=15: e.append(f'{n}: {len(f)} fields, want 15'); continue
            id_,_,_,p,per,a,b,rock,reg,form,sc,kg,diet,dna,notes=f
            plan(p,e,n)
            if per not in PER: e.append(f'{n}: period {per}')
            try:
                if not float(a)>=float(b): e.append(f'{n}: ma_from<ma_to')
                float(sc);float(kg)
            except: e.append(f'{n}: number')
            if rock not in ROCK: e.append(f'{n}: rock {rock}')
            rng(reg,e,n)
            if diet not in DIET: e.append(f'{n}: diet {diet}')
            if dna not in '12345' or len(dna)!=1: e.append(f'{n}: dna_tier')
        else:
            if len(f)!=12: e.append(f'{n}: {len(f)} fields, want 12'); continue
            id_,_,_,p,uk,reg,ext,sc,diet,hab,kg,notes=f
            plan(p,e,n); rng(reg,e,n)
            if uk!='-':
                fam,_,sp=uk.partition('/')
                if sp not in UW.get(fam,[]): e.append(f'{n}: uwkey {uk} not in uw_existing')
            if ext!='-' and not re.fullmatch(r'-?\d+',ext): e.append(f'{n}: ext {ext}')
            elif ext!='-' and int(ext)<-12900: e.append(f'{n}: extinct before 12900 BC, belongs in fossil file')
            try: float(sc);float(kg)
            except: e.append(f'{n}: number')
            if diet not in DIET: e.append(f'{n}: diet {diet}')
            for h in hab.split(';'):
                if h not in HAB: e.append(f'{n}: habitat {h}')
        if not re.fullmatch(r'[a-z][a-z0-9_]*',id_): e.append(f'{n}: id {id_!r}')
        if id_ in ids: e.append(f'{n}: duplicate id {id_}')
        ids.add(id_)
    print(fn,cnt,'rows',len(e),'errors'); print('\n'.join(e[:40])); bad+=len(e)
sys.exit(1 if bad else 0)
