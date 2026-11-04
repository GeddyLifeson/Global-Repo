# S6947 checks/cargo_nested.py [OUTDIR]: nested bay save (#346): flatbed, load container_20, load pallet (goes inside), save, restart, status again.
import sys, time, pathlib, json, os, re, signal
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
V = '/mnt/project-files/vehicles-test/' + os.environ.get('ARMS_DIR', 'combined') + '/'
UNITS = os.environ.get('UNITS_JAR', '/tmp/claude-0/unitsjar/diaithir-units-neoforge-26.1.2-1.0.0.jar')
JARS = [V + 'diaithir-arms-neoforge-26.1.2-1.0.1.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar', V + 'diaithir-carts-neoforge-26.1.2-1.0.0.jar', UNITS]
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
with Lane('nested', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive; S = L.server_cmd
    st = lambda c, w=1.5: [re.sub(r'.*MinecraftServer\]: ', '', x) for x in S(c, w)]
    CG = lambda c, w=1.5: st('execute as Tester at Tester run diaithircargo ' + c, w)
    S('time set day'); S('gamemode creative Tester'); S('clear Tester')
    S('tp Tester 0.5 -60 0.5 0 35', 1); S('item replace entity Tester hotbar.0 with mts:diaithirtrucks.trailer_flatbed'); d.key('1'); time.sleep(0.5); d.key('r'); time.sleep(4); S('item replace entity Tester hotbar.0 with minecraft:air')
    S('tp Tester 3.5 -60 4.5 135 25', 1.0)
    rep['load_container'] = CG('load container_20'); rep['status1'] = CG('status')
    rep['load_pallet'] = CG('load pallet'); rep['load_pallet2'] = CG('load pallet'); rep['status2'] = CG('status')
    L.look(3.5, -60, 4.5, 135, 25); L.shot('01_loaded.png')
    S('save-all flush', 3); S('stop', 1)
    rep['stopped'] = L.expect_log('server', r'Stopping server|Saving worlds|All dimensions are saved', 60) is not None
    time.sleep(8); os.killpg(L.sproc.pid, signal.SIGKILL); time.sleep(5)
    try: os.unlink(L.srv / 'cmd.in')
    except Exception: pass
    L.start_server(); L.start_client(); d = L.drive; S = L.server_cmd
    st = lambda c, w=1.5: [re.sub(r'.*MinecraftServer\]: ', '', x) for x in S(c, w)]
    CG = lambda c, w=1.5: st('execute as Tester at Tester run diaithircargo ' + c, w)
    S('gamemode creative Tester'); S('tp Tester 3.5 -60 4.5 135 25', 1.5); time.sleep(2)
    rep['status_after_restart'] = CG('status', 2.0); L.shot('02_after_restart.png')
    rep['errors'] = [l[:240] for l in L.log_lines('server', r'ERROR|Exception') if 'advancement' not in l][:8]
json.dump(rep, open((out or '.') + '/nested_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, json.dumps(v)[:500])
