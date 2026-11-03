# Planet world builder (Stage B). python3 -I gen_world.py planet_id [..]|ALL  -- reads specs/<id>.json (Stage A), writes into datapack/.
# Per planet: entry-named biomes (cloned from vanilla 26.1.2 templates, tinted), ocean/beach/river/cave roles, climate grid,
# own dimension_type (sky), optional own noise_settings (lava or no sea), biome tag. Data only.
import json,re,sys,pathlib
O=pathlib.Path('/mnt/project-files/planets'); D=O/'datapack/data/diaithir_planets'; L=O/'datapack/assets/diaithir_planets/lang/en_us.json'
TPL=O/'templates'; BASE=O/'base'
import sqlite3
S=sqlite3.connect('file:/mnt/attach/project-files/codex-store/library.sqlite?mode=ro',uri=True)
def tpl(n): return json.loads((TPL/(n+'.json')).read_text())
def hexok(c,d): return c if isinstance(c,str) and re.fullmatch(r'#[0-9a-fA-F]{6}',c) else d
def dark(c,f=0.6): return '#'+''.join('%02x'%int(int(c[i:i+2],16)*f) for i in (1,3,5))
def biome(arch,pid,key,grass=None,foliage=None,water=None,sky=None,fog=None,precip=None,temp=None):
    b=tpl(arch); e=b.setdefault('effects',{})
    if grass: e['grass_color']=grass
    if foliage: e['foliage_color']=foliage
    if water: e['water_color']=water
    a=b.setdefault('attributes',{})
    if water: a['minecraft:visual/water_fog_color']=dark(water)
    if precip=='none': b['has_precipitation']=False
    elif precip in('rain','snow'):
        b['has_precipitation']=True
        if precip=='snow' and b.get('temperature',0.5)>0.1: b['temperature']=0.0
        if precip=='rain' and b.get('temperature',0.5)<0.15: b['temperature']=0.5
    return b
def atmo_apply(b,at):
    if not at: return b
    a=b.setdefault('attributes',{})
    ps=at.get('particles') or []
    if ps and at.get('grounded',True):
        a['minecraft:visual/ambient_particles']=[{"particle":{"type":"minecraft:"+p['type']},"probability":max(0.001,min(0.15,float(p.get('probability',0.02))))} for p in ps]
    f=hexok(at.get('fog'),None)
    if f: a['minecraft:visual/fog_color']=f
    pb=at.get('precip_bias')
    if pb=='dry': b['has_precipitation']=False
    elif pb=='snow' and b.get('has_precipitation',True): b['has_precipitation']=True; b['temperature']=min(b.get('temperature',0.5),0.0)
    elif pb=='rain' and b.get('has_precipitation',True): b['has_precipitation']=True; b['temperature']=max(b.get('temperature',0.5),0.5)
    return b
def full(**k):
    p={"temperature":[-1.0,1.0],"humidity":[-1.0,1.0],"continentalness":[-1.0,1.0],"erosion":[-1.0,1.0],"depth":[-1.0,1.0],"weirdness":[-1.0,1.0],"offset":0.0}
    p.update(k); return p
def build(pid,name,sp,lang):
    (D/'worldgen/biome').mkdir(parents=True,exist_ok=True); (D/'tags/worldgen/biome').mkdir(parents=True,exist_ok=True)
    (D/'dimension_type').mkdir(exist_ok=True); (D/'planet_stems').mkdir(exist_ok=True)
    for old in (D/'worldgen/biome').glob(pid+'_*.json'): old.unlink()
    water=hexok(sp.get('sea',{}).get('water'),'#3f76e4'); ids=[]; cells=[]
    def put(key,b,disp,par):
        b=atmo_apply(b,sp.get('atmo')); bid=f'{pid}_{key}'; (D/'worldgen/biome'/(bid+'.json')).write_text(json.dumps(b))
        full_id='diaithir_planets:'+bid; ids.append(full_id); lang['biome.diaithir_planets.'+bid]=disp
        cells.append({"biome":full_id,"parameters":par})
    used=set()
    for i,bs in enumerate(sp['biomes']):
        r=S.execute("select name from entry where id=?",(bs['entry'],)).fetchone()
        if not r: continue
        t=hexok(bs.get('temp'),None) if False else float(bs.get('temp',0)); h=float(bs.get('humid',0))
        t=max(-1,min(1,t)); h=max(-1,min(1,h)); key=re.sub(r'[^a-z0-9]+','_',r[0].lower()).strip('_') or f'b{i}'
        if key in used: key=f'{key}{i}'
        used.add(key)
        b=biome(bs['archetype'],pid,key,hexok(bs.get('grass'),None),hexok(bs.get('foliage'),None),hexok(bs.get('water'),water),precip=bs.get('precip'))
        put(key,b,r[0],full(temperature=t,humidity=h,continentalness=[-0.11,1.0],depth=[-1.0,0.2]))
    oc=sp.get('ocean_archetype','ocean'); deep=oc if oc.startswith('deep') else 'deep_'+oc if tpl_exists('deep_'+oc) else 'deep_ocean'
    put('deep_sea',biome(deep,pid,'deep',water=water),name+' Deep Sea',full(continentalness=[-1.0,-0.455],depth=[-1.0,0.2]))
    put('sea',biome(oc.replace('deep_',''),pid,'sea',water=water),name+' Sea',full(continentalness=[-0.455,-0.19],depth=[-1.0,0.2]))
    put('shore',biome(sp.get('beach_archetype','beach'),pid,'shore',water=water),name+' Shore',full(continentalness=[-0.19,-0.11],depth=[-1.0,0.2]))
    put('river',biome(sp.get('river_archetype','river'),pid,'river',water=water),name+' River',full(continentalness=[-0.11,1.0],erosion=[-0.2,0.55],weirdness=[-0.05,0.05],depth=[-1.0,0.2]))
    put('hollows',biome('lush_caves',pid,'hollows',water=water),name+' Hollows',full(depth=[0.2,1.0],humidity=[0.0,1.0]))
    put('grottoes',biome('dripstone_caves',pid,'grottoes',water=water),name+' Grottoes',full(depth=[0.2,1.0],humidity=[-1.0,0.0]))
    (D/'tags/worldgen/biome'/(pid+'.json')).write_text(json.dumps({"values":ids}))
    # dimension_type with this planet's sky
    t=json.loads((BASE/'dimension_type_overworld.json').read_text()); a=t['attributes']; s=sp.get('sky',{})
    a['minecraft:visual/sky_color']=hexok(s.get('sky'),'#78a7ff'); a['minecraft:visual/fog_color']=hexok(s.get('fog'),'#c0d8ff')
    cc=s.get('cloud','');a['minecraft:visual/cloud_color']=cc if re.fullmatch(r'#[0-9a-fA-F]{8}',str(cc)) else '#ccffffff'
    try: a['minecraft:visual/cloud_height']=float(s.get('cloud_height',192.33))
    except: pass
    at=sp.get('atmo') or {}
    if hexok(at.get('fog'),None): a['minecraft:visual/fog_color']=at['fog']
    try: a['minecraft:visual/star_brightness']=max(0.0,min(1.0,float(at['stars'])))
    except Exception: pass
    if at.get('night')=='bright': t['ambient_light']=0.15
    (D/'dimension_type'/(pid+'.json')).write_text(json.dumps(t))
    # noise settings
    ter=sp.get('terrain','normal'); base={'normal':'overworld','amplified':'amplified','large_biomes':'large_biomes'}.get(ter,'overworld')
    liq=sp.get('sea',{}).get('liquid','water'); ns='minecraft:'+base
    if liq in('lava','none'):
        n=json.loads((BASE/f'noise_settings_{base}.json').read_text())
        if liq=='lava': n['default_fluid']={'Name':'minecraft:lava','Properties':{'level':'0'}}
        else: n['sea_level']=-64
        (D/'worldgen/noise_settings').mkdir(parents=True,exist_ok=True); (D/'worldgen/noise_settings'/(pid+'.json')).write_text(json.dumps(n)); ns='diaithir_planets:'+pid
    dim={"type":"diaithir_planets:"+pid,"generator":{"type":"minecraft:noise","settings":ns,"biome_source":{"type":"minecraft:multi_noise","biomes":cells}}}
    import hashlib; dim['neoforge:seed_override']=int.from_bytes(hashlib.sha256(pid.encode()).digest()[:8],'big',signed=True); (D/'planet_stems'/(pid+'.json')).write_text(json.dumps(dim)); lang['dimension.diaithir_planets.'+pid]=name
def tpl_exists(n): return (TPL/(n+'.json')).exists()
if __name__=='__main__':
    P={p['planet_id']:p for p in json.load(open(O/'planets.json'))}
    want=sys.argv[1:]; lang=json.loads(L.read_text())
    for pid in (P if want==['ALL'] else want):
        f=O/'specs'/(pid+'.json')
        if f.exists() and pid!='diaithir': build(pid,P[pid]['name'],json.loads(f.read_text()),lang); print('built',pid)
    L.write_text(json.dumps(lang,indent=0))
    prof={}
    for pid in P:
        f=O/'specs'/(pid+'.json')
        if f.exists() and pid!='diaithir':
            a=json.loads(f.read_text()).get('atmo') or {}
            ps=a.get('particles') or []
            prof[pid]={'bias':a.get('precip_bias','mixed'),'stormy':a.get('storms')=='stormy','particle':ps[0]['type'] if ps and a.get('grounded',True) else ''}
    (O/'datapack/diaithir_planet_weather.json').write_text(json.dumps(prof))
