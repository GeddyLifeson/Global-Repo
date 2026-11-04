# S6941 checks/cargo_check.py [OUTDIR]: vehicle cargo bays (PR 340): /diaithircargo load|status|clear on a flatbed and a ford_f1, screenshots, then save + server restart + status again.
import sys, time, pathlib, json, os, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
V = '/mnt/project-files/vehicles-test/'
JARS = [V + 'diaithir-arms-neoforge-26.1.2-1.0.1.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar', V + 'diaithir-carts-neoforge-26.1.2-1.0.0.jar', V + 'diaithir-units-neoforge-26.1.2-1.0.0.jar']
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
VEH = {'flatbed': 'mts:diaithirtrucks.trailer_flatbed', 'f1': 'mts:diaithirvehicles.ford_f1'}
with Lane('cargo', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive; S = L.server_cmd
    rep['bay_log'] = L.log_lines('server', r'cargo bays')[:3]
    CG = lambda c, w=1.2: S('execute as Tester at Tester run diaithircargo ' + c, w)
    S('time set day'); S('gamemode creative Tester'); S('clear Tester')
    for i, (nm, item) in enumerate(VEH.items()):
        x = i * 14
        S(f'tp Tester {x + 0.5} -60 0.5 0 35', 1); S(f'item replace entity Tester hotbar.0 with {item}'); d.key('1'); time.sleep(0.5); d.key('r'); time.sleep(4); S('item replace entity Tester hotbar.0 with minecraft:air')
        S(f'tp Tester {x + 3.5} -60 4.5 135 25', 1.0)
        rep[nm + '_ent'] = re.findall(r'packID: "[^"]*"|systemName: "[^"]*"', ''.join(S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest]', 1.5)))[-3:]
        if os.environ.get('CARGO_PROBE') and nm == 'flatbed':
            vp = re.findall(r'-?[\d.]+d', ''.join(S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 1.0)))
            rep['probe_vpos'] = vp
            for lbl, (dx, dz) in {'on': (0, 0), 'd1': (1, 0), 'd2z': (0, 2), 'm3': (-3, 0)}.items():
                S(f'tp Tester {float(vp[0][:-1]) + dx:.2f} {float(vp[1][:-1]):.2f} {float(vp[2][:-1]) + dz:.2f} 0 20', 0.8)
                rep['probe_' + lbl] = CG('status', 1.0)
            S(f'tp Tester {x + 3.5} -60 4.5 135 25', 1.0)
            rep['probe_console'] = S('diaithircargo status', 1.0)
        rep[nm + '_near'] = S(f'execute positioned {x + 0.5} -60 2.5 run say near @e[distance=..6,type=!player]', 1)
        L.shot(f'{nm}_00_empty.png')
        for what in ('pallet', 'barrel', 'crate', 'chest') + (('container_20',) if nm == 'flatbed' else ()):
            rep[f'{nm}_load_{what}'] = CG(f'load {what}', 1.5); time.sleep(0.8)
            L.shot(f'{nm}_01_{what}.png')
        rep[nm + '_status'] = CG('status', 1.0)
        L.look(x + 3.5, -60, 4.5, 135, 25); L.shot(f'{nm}_02_all.png')
        S(f'tp Tester {x + 0.5} -60 -8.5 0 20', 1.0); time.sleep(1); L.shot(f'{nm}_03_side.png')
        # move the vehicle: tp it, then see if loads follow
        S(f'execute as @e[type=mts:builder_existing,distance=..12] at @s run tp @s ~ ~ ~4 90 0', 1.0); time.sleep(2)
        L.shot(f'{nm}_04_after_tp.png')
        rep[nm + '_status_after_tp'] = CG('status', 1.0)
    if os.environ.get('CARGO_QUICK'): json.dump(rep, open((out or '.') + '/cargo_report.json', 'w'), indent=1); print(json.dumps(rep, indent=1)[:3000]); raise SystemExit
    # real path: hold a pallet item, right-click the deck
    S('give Tester diaithircarts:freight_pallet 2'); S('tp Tester 3.5 -60 4.5 135 25', 1); d.key('1'); time.sleep(0.5)
    S('clear Tester minecraft:chest'); S('give Tester diaithircarts:freight_pallet 2'); time.sleep(0.5)
    d.key('r'); time.sleep(1.5); L.shot('real_path_rclick.png')
    rep['real_status'] = CG('status', 1.0)
    rep['clear'] = CG('clear', 1.0); rep['status_cleared'] = CG('status', 1.0)
    for nm, item in VEH.items(): pass
    # reload then persistence
    CG('load pallet'); CG('load crate'); rep['pre_restart_status'] = CG('status', 1.0)
    S('save-all flush', 3); S('stop', 1)
    rep['stopped'] = L.expect_log('server', r'Stopping server|ThreadedAnvilChunkStorage|Saving worlds|All dimensions are saved', 60) is not None
    time.sleep(8)
    import signal; os.killpg(L.sproc.pid, signal.SIGKILL); time.sleep(5)
    try: os.unlink(L.srv / 'cmd.in')
    except Exception: pass
    L.start_server(); rep['restarted'] = True
    L.start_client(); d = L.drive; S = L.server_cmd
    S('gamemode creative Tester'); S('tp Tester 3.5 -60 4.5 135 25', 1.5); time.sleep(2)
    rep['post_restart_status'] = CG('status', 1.5); L.shot('post_restart.png')
    rep['post_restart_entities'] = S('execute as Tester run say near @e[distance=..30,type=!player]', 1)
    rep['server_errors'] = [l[:240] for l in L.log_lines('server', r'ERROR|Exception') if 'advancement' not in l and 'netty' not in l.lower() and 'Appender' not in l][:8]
json.dump(rep, open((out or '.') + '/cargo_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, str(v)[:400])
