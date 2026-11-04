# S6945 checks/cars_pump.py [OUTDIR]: pump-to-vehicle (units #221 0025b0e4) + unseated drive with a pallet on a pickup. Env CARS_VEH (default ford_f1), engfix2 jars.
import sys, time, pathlib, json, os, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
V = '/mnt/project-files/vehicles-test/'; E = V + 'engfix2/'
UNITS = os.environ.get('UNITS_JAR', '/tmp/claude-0/unitsjar/diaithir-units-neoforge-26.1.2-1.0.0.jar')
JARS = [E + 'diaithir-arms-neoforge-26.1.2-1.0.1.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar', E + 'diaithir-carts-neoforge-26.1.2-1.0.0.jar', UNITS]
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
veh = os.environ.get('CARS_VEH', 'ford_f1')
with Lane('carspump', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive; S = L.server_cmd
    st = lambda c, w=1.5: [re.sub(r'.*MinecraftServer\]: ', '', x) for x in S(c, w)]
    DV = lambda c, w=1.5: st('execute as Tester at Tester run diaithirvehicle ' + c, w)
    CG = lambda c, w=1.5: st('execute as Tester at Tester run diaithircargo ' + c, w)
    S('time set day'); S('gamemode survival Tester'); S('clear Tester'); S('op Tester')
    S('tp Tester 0.5 -60 0.5 0 35', 1); S(f'item replace entity Tester hotbar.0 with mts:diaithirvehicles.{veh}'); d.key('1'); time.sleep(0.5); d.key('r'); time.sleep(12); S('item replace entity Tester hotbar.0 with minecraft:air')
    S('tp Tester 4.5 -60 -1.5 0 20', 1.2)
    POS = lambda: re.findall(r'-?[\d.]+d', ''.join(S('execute at Tester run data get entity @e[type=mts:builder_existing,distance=..60,limit=1,sort=nearest] Pos', 1.5)))
    rep['pos0'] = POS(); rep['status0'] = DV('status', 2.0)
    # barrel + rack beside the vehicle (rack pulls 20 L/s from the adjacent barrel into vehicles within 5 blocks)
    S('setblock 3 -60 -2 diaithirunits:loading_rack', 0.5); S('setblock 4 -60 -2 diaithirunits:fuel_barrel', 0.5)
    rep['pump_fill'] = st('diaithirfuel fill 4 -60 -2 petrol 100', 1.0)
    rep['barrel_before'] = ''.join(S('data get block 4 -60 -2', 1.2))[-260:]
    time.sleep(6)
    rep['status_after_pump'] = DV('status', 2.0); rep['barrel_after'] = ''.join(S('data get block 4 -60 -2', 1.2))[-260:]
    rep['start'] = DV('start'); time.sleep(2); rep['status_started'] = DV('status', 2.0)
    rep['load'] = CG('load pallet', 2.0); rep['cargo0'] = CG('status', 1.5)
    rep['drive'] = DV('drive 1'); time.sleep(8)
    rep['status_driving'] = DV('status', 2.0); rep['pos1'] = POS(); rep['cargo1'] = CG('status', 1.5)
    L.shot('01_after_drive.png')
json.dump(rep, open((out or '.') + '/cars_pump_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, json.dumps(v)[:700])
