# S6889 checks/carts_server.py [OUTDIR]: server-only: diaithir-carts + Immersive Vehicles; `diaithircarts roadtest`, summon item for vehicle ids, log scan.
import sys, time, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
J = ['/mnt/project-files/vehicles-test/diaithir-carts-neoforge-26.1.2-1.0.0.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar']
ids = ['willys_mb', 'm113', 'routemaster', 'ford_f1', 'vw_type_2', 'nope']
rep = {}
with Lane('carts', J, out=sys.argv[1] if len(sys.argv) > 1 else None, srv_xmx='3G') as L:
    L.server_cmd('forceload add 0 0', 2)
    rep['roadtest'] = L.server_cmd('diaithircarts roadtest', 8)
    for i in ids:
        rep[i] = L.server_cmd('summon item 0 -58 0 {Item:{id:"mts:diaithirvehicles.%s",count:1}}' % i, 1.2)
    time.sleep(1); rep['items'] = L.server_cmd('data get entity @e[type=item,limit=20,sort=nearest,x=0,y=-58,z=0] Item', 1) 
    rep['count_items'] = L.server_cmd('execute if entity @e[type=item]', 1)
    rep['mts_log'] = L.log_lines('server', r'MTSERROR|mts|diaithirvehicles|pack|Pack')[:60]
    rep['errors'] = [l for l in L.log_lines('server', r'ERROR|Exception') if not any(x in l for x in ('DebugFile', 'kqueue', 'layers'))][:40]
json.dump(rep, open((sys.argv[1] if len(sys.argv) > 1 else '.') + '/carts_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, str(v)[:600])
