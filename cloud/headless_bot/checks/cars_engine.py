# S6944 checks/cars_engine.py [OUTDIR]: cars engine fix (ports #345): place ford_f1 / vw_type_2, check spawn warnings, diaithirvehicle start / status / fill, icon warnings.
import sys, time, pathlib, json, os, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
V = '/mnt/project-files/vehicles-test/'; E = V + os.environ.get('ENGFIX_DIR', 'engfix2') + '/'
JARS = [E + 'diaithir-arms-neoforge-26.1.2-1.0.1.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar', E + 'diaithir-carts-neoforge-26.1.2-1.0.0.jar', V + 'diaithir-units-neoforge-26.1.2-1.0.0.jar']
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
with Lane('cars', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive; S = L.server_cmd
    DV = lambda c, w=1.5: [re.sub(r'.*MinecraftServer\]: ', '', x) for x in S('execute as Tester at Tester run diaithirvehicle ' + c, w)]
    S('time set day'); S('gamemode survival Tester'); S('clear Tester')
    for i, (nm, item) in enumerate({'ford_f1': 'mts:diaithirvehicles.ford_f1', 'vw_type_2': 'mts:diaithirvehicles.vw_type_2', 'willys_mb': 'mts:diaithirvehicles.willys_mb'}.items()):
        x = 30 * i; n0 = len(L.log_lines('server', r'.'))
        S(f'tp Tester {x + 0.5} -60 0.5 0 35', 1); S(f'item replace entity Tester hotbar.0 with {item}'); d.key('1'); time.sleep(0.5); d.key('r'); time.sleep(11); S('item replace entity Tester hotbar.0 with minecraft:air')
        S(f'tp Tester {x + 3.5} -60 4.5 135 20', 1.0); r = {}
        r['spawn_log'] = [l[-260:] for l in L.log_lines('server', r'.')[n0:] if re.search(r'defaultFuelQty|no engine|without fuel', l)]
        r['start'] = DV('start'); time.sleep(1.5); r['status'] = DV('status', 2.0)
        r['fill'] = DV('fill', 1.5) + DV('fill gasoline 500', 1.5) + DV('fill 500', 1.5); r['status_after_fill'] = DV('status', 2.0)
        r['parts'] = re.findall(r'systemName: "([^"]+)"', ''.join(S('execute at Tester run data get entity @e[type=mts:builder_existing,distance=..15,limit=1,sort=nearest]', 2.5)))
        L.shot(f'{nm}.png'); rep[nm] = r
    rep['server_missing_icon'] = [l[-200:] for l in L.log_lines('server', r'(?i)missing.*(item|icon)|Missing textures in model mts:item/diaithir(vehicles|trucks)')][:6]
    rep['client_missing_icon'] = [l[-200:] for l in L.log_lines('client', r'Missing textures in model mts:item/diaithir(vehicles|trucks)')][:6]
json.dump(rep, open((out or '.') + '/cars_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, json.dumps(v)[:1200])
