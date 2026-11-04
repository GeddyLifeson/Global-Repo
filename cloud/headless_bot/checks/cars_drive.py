# S6946 checks/cars_drive.py [OUTDIR]: pickup (ford_f1): fuel by loading rack, mount the driver seat by aimed click, load a pallet, drive with W and turn with A, vehicle vs display positions.
import sys, time, pathlib, json, os, re, math, threading
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
V = '/mnt/project-files/vehicles-test/'; E = V + os.environ.get('ARMS_DIR', 'engfix2') + '/'
UNITS = os.environ.get('UNITS_JAR', '/tmp/claude-0/unitsjar/diaithir-units-neoforge-26.1.2-1.0.0.jar')
CARTS = os.environ.get('CARTS_JAR', V + 'nested-carts.jar')
JARS = [E + 'diaithir-arms-neoforge-26.1.2-1.0.1.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar', CARTS, UNITS]
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
veh = os.environ.get('CARS_VEH', 'ford_f1')
with Lane('carsdrive', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive; S = L.server_cmd
    st = lambda c, w=1.5: [re.sub(r'.*MinecraftServer\]: ', '', x) for x in S(c, w)]
    DV = lambda c, w=1.5: st('execute as Tester at Tester run diaithirvehicle ' + c, w)
    CG = lambda c, w=1.5: st('execute as Tester at Tester run diaithircargo ' + c, w)
    S('time set day'); S('gamemode survival Tester'); S('clear Tester'); S('op Tester')
    S('tp Tester 0.5 -60 0.5 0 35', 1); S(f'item replace entity Tester hotbar.0 with mts:diaithirvehicles.{veh}'); d.key('1'); time.sleep(0.5); d.key('r'); time.sleep(12); S('item replace entity Tester hotbar.0 with minecraft:air'); S('clear Tester')
    S('setblock 3 -60 -2 diaithirunits:loading_rack', 0.5); S('setblock 4 -60 -2 diaithirunits:fuel_barrel', 0.5)
    rep['pump_fill'] = st('diaithirfuel fill 4 -60 -2 petrol 100', 1.0); time.sleep(6)
    rep['load_before_mount'] = None
    # mount: aim at the driver seat: local (-0.4, 0.9, 0.2); vehicle at (0.5,-60,2.5) heading +x
    vx, vy, vz = 0.5, -60.0, 2.5; rep['mounted'] = False; tries = []
    for sz in (-0.4, 0.4):
        sx, sy, sz_w = vx + 0.2, vy + 0.9, vz + sz
        for stand in ((sx, sz_w - 2.5), (sx, sz_w + 2.5), (sx - 2.5, sz_w), (sx + 2.5, sz_w)):
            for dy in (0.6, 1.0, 1.4):
                px, pz = stand; py = vy
                yaw = math.degrees(math.atan2(-(sx - px), sz_w - pz)); dist = math.hypot(sx - px, sz_w - pz); pitch = -math.degrees(math.atan2((sy + dy - 0.9) - (py + 1.62), dist)) * -1
                S(f'tp Tester {px:.2f} {py:.2f} {pz:.2f} {yaw:.1f} {math.degrees(math.atan2((py + 1.62) - (sy + 0.1), dist)):.1f}', 0.4); d.key('r'); time.sleep(0.9)
                rr = S('data get entity Tester RootVehicle', 0.6)
                if any('following' in l or 'Attach' in l for l in rr):
                    rep['mounted'] = True; rep['mount_at'] = (round(px, 1), round(pz, 1), round(yaw), sz); break
            if rep['mounted']: break
        if rep['mounted']: break
    L.shot('02_after_mount_try.png')
    if rep['mounted']:
        rep['seat_pos'] = S('data get entity Tester Pos', 0.6)
        rep['start'] = DV('start'); time.sleep(2); rep['status0'] = DV('status', 2.0)
        d.key('F5'); time.sleep(1.2); d.key('F5'); time.sleep(1.0)
        rep['load'] = CG('load pallet', 2.0); rep['cargo0'] = CG('status', 1.5)
        def sample():
            p = lambda c: ' '.join(S('execute at Tester run data get entity ' + c, 0.5))
            f = lambda t: re.findall(r'\[[^\]]*\]', t)[-1:]
            return {'veh_pos': f(p('@e[type=mts:builder_existing,distance=..80,limit=1,sort=nearest] Pos')), 'disp_pos': f(p('@e[type=block_display,distance=..80,limit=1,sort=nearest] Pos'))}
        rep['samples'] = []
        thw = threading.Thread(target=lambda: d.hold('w', 16)); thw.start(); t0 = time.time(); tha = None
        while thw.is_alive():
            el = time.time() - t0
            if el > 7 and tha is None: tha = threading.Thread(target=lambda: d.hold('a', 5)); tha.start()
            if el > 6 and 'cargo_moving' not in rep: rep['cargo_moving'] = CG('status', 0.8); rep['veh_moving'] = DV('status', 0.8); L.shot('03_driving.png')
            rep['samples'].append(dict(t=round(el, 1), turning=bool(tha and tha.is_alive()), **sample()))
        if tha: tha.join()
        rep['cargo_turned'] = CG('status', 1.2); rep['veh_after'] = DV('status', 1.2); L.shot('04_after.png')
json.dump(rep, open((out or '.') + '/cars_drive_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, json.dumps(v)[:600])
