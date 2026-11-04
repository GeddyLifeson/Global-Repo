# S6942 checks/cargo_one.py [OUTDIR]: one flatbed, one pallet: geometry numbers + screenshots from 6 blocks back looking down; clear order test; nudge-follow test.
import sys, time, pathlib, json, os, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
V = '/mnt/project-files/vehicles-test/'
JARS = [V + 'diaithir-arms-neoforge-26.1.2-1.0.1.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar', V + 'diaithir-carts-neoforge-26.1.2-1.0.0.jar', V + 'diaithir-units-neoforge-26.1.2-1.0.0.jar']
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
with Lane('cargo1', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive; S = L.server_cmd
    CG = lambda c, w=1.2: S('execute as Tester at Tester run diaithircargo ' + c, w)
    S('time set day'); S('weather clear'); S('gamemode creative Tester'); S('clear Tester')
    S('tp Tester 0.5 -60 0.5 0 35', 1); S('item replace entity Tester hotbar.0 with mts:diaithirtrucks.trailer_flatbed'); d.key('1'); time.sleep(0.5); d.key('r'); time.sleep(9); S('item replace entity Tester hotbar.0 with minecraft:air')
    rep['veh'] = ''.join(S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 1.0))[-60:]
    rep['veh_rot'] = ''.join(S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Rotation', 1.0))[-60:]
    S('tp Tester 0.5 -57 -6.5 0 40', 1.5); time.sleep(1.5)
    L.shot('01_empty_6_back.png')
    rep['clear0'] = CG('clear'); rep['load_pallet'] = CG('load pallet', 1.5); time.sleep(1)
    rep['status1'] = CG('status', 1.0)
    rep['bd'] = [x[-700:] for x in S('data get entity @e[type=block_display,limit=1,sort=nearest]', 1.5)]
    rep['bd_all_pos'] = [x[-200:] for x in S('execute as @e[type=block_display] run data get entity @s Pos', 1.5)]
    L.shot('02_one_pallet_6_back.png')
    S('tp Tester 0.5 -52 2.5 0 90', 1.5); time.sleep(1.5); L.shot('03_one_pallet_top_down.png')
    S('tp Tester -6 -58 -4 0 25', 1.5); time.sleep(1.2); L.shot('03b_pallet_x_minus6_view.png')
    S('tp Tester 6 -58 -6 150 25', 1.5); time.sleep(1.2); L.shot('03c_from_plus_x.png')
    S('tp Tester 4.5 -59 2.5 90 15', 1.5); time.sleep(1); L.shot('04_one_pallet_side.png')
    rep['clear1'] = CG('clear')
    for w in ('pallet', 'barrel', 'crate', 'chest', 'container_20'): CG('load ' + w, 1.0)
    rep['status5'] = CG('status', 1.0); rep['clear5'] = CG('clear', 1.5); rep['status_after_clear5'] = CG('status', 1.0)
    CG('load pallet', 1.0); rep['status_p'] = CG('status', 1.0)
    # nudge-follow: move the vehicle 2 blocks and rotate, stay within 8 blocks
    S('tp Tester 0.5 -57 -6.5 0 40', 1.2)
    S('execute as @e[type=mts:builder_existing,limit=1,sort=nearest] at @s run tp @s ~ ~ ~2', 1.5); time.sleep(2)
    rep['status_nudge'] = CG('status', 1.0); L.shot('05_after_nudge2.png')
    rep['veh_after'] = ''.join(S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 1.0))[-60:]
    rep['bd_after'] = [x[-200:] for x in S('execute as @e[type=block_display] run data get entity @s Pos', 1.5)]
json.dump(rep, open((out or '.') + '/cargo_one_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, str(v)[:900])
