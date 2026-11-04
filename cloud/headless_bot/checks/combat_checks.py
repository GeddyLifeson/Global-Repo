# S6868 checks/combat_checks.py: boss looks (26 bosses), armour models on armor stands, IV vehicle (diaithirtanks) placing/driving. Light pack:
# diaithir-bosses + diaithir-arms 1.0.1 + Immersive Vehicles. python3 -I combat_checks.py [OUTDIR] [--only bosses|armour|vehicles]
import sys, glob, time, pathlib, json, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
from discover import discover
PF = '/mnt/project-files/'
JARS = [PF + 'builds/mod-ports/diaithir-bosses-neoforge-26.1.2-1.0.0.jar', PF + 'rewrite-jars/combat-classes/diaithir-arms-neoforge-26.1.2-1.0.1.jar', PF + 'Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar']
args = [a for a in sys.argv[1:] if not a.startswith('--')]; out = args[0] if args else None
only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
bosses = discover(JARS[0])['entities']; arms = discover(JARS[1])['items']
sets = sorted({re.sub(r'_helmet$', '', i.split(':')[1]) for i in arms if i.endswith('_helmet')})
report = {}
with Lane('combat', JARS, props={'difficulty': 'easy'}, srv_xmx='3G', out=out) as L:
    print('joined', L.start_client()); d = L.drive
    for c in ('gamemode creative Tester', 'time set day', 'weather clear', 'gamerule mob_griefing false', 'gamerule do_mob_spawning false'): L.server_cmd(c)
    L.wait_render(); time.sleep(4)
    if only in (None, 'bosses'):
        for b in bosses:
            n = b.split(':')[1]
            L.server_cmd('kill @e[type=!player]'); L.server_cmd('tp Tester 0.5 -60 0.5 180 8', 0.3)
            fb = L.server_cmd(f'summon {b} 0.5 -60 -14 {{NoAI:1b,Invulnerable:1b,PersistenceRequired:1b}}', 1.0)
            L.server_cmd('tp Tester 0.5 -60 0.5 180 8', 3); L.shot(f'boss_{n}.png'); report[f'boss:{n}'] = any('Summoned' in l for l in fb) or fb
    if only in (None, 'armour'):
        L.server_cmd('kill @e[type=!player]')
        for s in sets:
            L.server_cmd('kill @e[type=armor_stand]'); L.server_cmd('summon armor_stand 0.5 -60 3.5 {ShowArms:1b,Rotation:[180f,0f]}', 0.8)
            fb = []
            for slot, piece in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots')):
                fb += L.server_cmd(f'item replace entity @e[type=armor_stand,limit=1] armor.{slot} with diaithirarms:{s}_{piece}', 0.4)
            L.server_cmd('tp Tester 0.5 -60 0.5 0 0', 0.3); L.server_cmd('tp Tester 0.5 -59.2 1.6 0 5', 2.5); L.shot(f'armour_{s}.png')
            report[f'armour:{s}'] = 'ok' if all('Replaced' in l for l in fb) else fb
    if only in (None, 'vehicles'):
        L.server_cmd('kill @e[type=!player]'); L.server_cmd('tp Tester 0.5 -60 0.5 0 35', 1)
        print(L.server_cmd('item replace entity Tester hotbar.0 with mts:diaithirtanks.tank_mk1', 0.8))
        d.key('1'); time.sleep(0.5); L.shot('vehicle_0_held.png')
        d.key('r'); time.sleep(5); L.shot('vehicle_1_placed.png')      # R = use (options.txt remap)
        L.server_cmd('tp Tester 0.5 -60 -9 0 15', 2); L.shot('vehicle_2_view.png')
        ents = L.server_cmd('execute as Tester at Tester run say near: @e[distance=..30,type=!player]', 1); print('entities', ents)
        d.key('r'); time.sleep(2); L.shot('vehicle_3_use.png')
        d.hold('w', 3); time.sleep(1); L.shot('vehicle_4_w.png')
    print('server errs', [l for l in L.log_lines('server', r'ERROR|Exception') if 'DebugFile' not in l and 'kqueue' not in l and 'layers' not in l][:6])
    print('client errs', [l for l in L.log_lines('client', r'ERROR|Exception|Missing|missing') if 'authlib' not in l and 'Realms' not in l and '401' not in l and 'properties' not in l][:10])
json.dump(report, open((out or '.') + '/combat_report.json', 'w'), indent=1)
