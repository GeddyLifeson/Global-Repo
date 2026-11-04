# S6943 checks/cargo_multi.py [OUTDIR]: cargo geometry on several vehicle types: place, load, status, display transformation, side screenshot.
import sys, time, pathlib, json, os, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
V = '/mnt/project-files/vehicles-test/'
JARS = [V + 'diaithir-arms-neoforge-26.1.2-1.0.1.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar', V + 'diaithir-carts-neoforge-26.1.2-1.0.0.jar', V + 'diaithir-units-neoforge-26.1.2-1.0.0.jar']
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
CASES = [('flatbed_container20', 'mts:diaithirtrucks.trailer_flatbed', 'container_20'), ('flatbed_pallet', 'mts:diaithirtrucks.trailer_flatbed', 'pallet'),
         ('tank_pallet', 'mts:diaithirtanks.tank_mk1', 'pallet'), ('van_pallet', 'mts:diaithirvehicles.vw_type_2', 'pallet'), ('mack_pallet', 'mts:diaithirvehicles.mack_type_75', 'pallet'),
         ('dryvan_pallet', 'mts:diaithirtrucks.trailer_dry_van', 'pallet'), ('lowboy_container20', 'mts:diaithirtrucks.trailer_lowboy', 'container_20')]
sel = os.environ.get('CARGO_ONLY'); 
with Lane('cargom', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive; S = L.server_cmd
    CG = lambda c, w=1.2: S('execute as Tester at Tester run diaithircargo ' + c, w)
    S('time set day'); S('weather clear'); S('gamemode creative Tester'); S('clear Tester')
    for i, (nm, item, load) in enumerate(CASES):
        if sel and nm not in sel.split(','): continue
        x = 40 * i; r = {}
        S(f'tp Tester {x + 0.5} -60 0.5 0 35', 1); S(f'item replace entity Tester hotbar.0 with {item}'); d.key('1'); time.sleep(0.5); d.key('r'); time.sleep(14 if i == 0 else 11); S('item replace entity Tester hotbar.0 with minecraft:air')
        pos = re.findall(r'-?[\d.]+d', ''.join(S('execute at Tester run data get entity @e[type=mts:builder_existing,distance=..15,limit=1,sort=nearest] Pos', 2.0)))
        r['veh_pos'] = pos
        r['load'] = CG(f'load {load}', 2.0); time.sleep(1)
        r['status'] = [re.sub(r'.*MinecraftServer\]: ', '', x) for x in CG('status', 2.0)]
        r['display'] = re.findall(r'(?:translation: \[[^\]]*\]|left_rotation: \[[^\]]*\]|scale: \[[^\]]*\]|Name: "[^"]*")', ''.join(S('execute at Tester run data get entity @e[type=block_display,distance=..15,limit=1,sort=nearest]', 2.5)))
        if pos:
            vx, vy, vz = (float(p[:-1]) for p in pos)
            for k, (px, pz, yaw) in {'side': (vx, vz - 9, 0), 'end': (vx + 9, vz, 90)}.items():
                S(f'tp Tester {px:.1f} {vy + 0.5:.1f} {pz:.1f} {yaw} 8', 1.5); time.sleep(1.2); L.shot(f'{nm}_{k}.png')
        rep[nm] = r
        CG('clear', 0.5)
json.dump(rep, open((out or '.') + '/cargo_multi_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, json.dumps(v)[:900])
