# S6887 checks/clientui_checks.py [OUTDIR]: boot + join with the 10 client-ui jars, HUD, inventory, chat, F3, tooltip screenshots, error scan.
import sys, glob, time, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
SKIP = [a[7:] for a in sys.argv if a.startswith('--skip=')]
JARS = [j for j in sorted(glob.glob('/mnt/project-files/rewrite-jars/client-ui/*.jar')) if not any(s in j for s in SKIP)]
out = ([a for a in sys.argv[1:] if not a.startswith('--')] or [None])[0]
with Lane('clientui', JARS, out=out, srv_xmx='3G') as L:
    print('joined', L.start_client()); d = L.drive
    L.server_cmd('time set day'); L.server_cmd('gamemode survival Tester'); L.server_cmd('give Tester minecraft:diamond_sword'); L.server_cmd('give Tester minecraft:golden_apple 3')
    L.server_cmd('summon minecraft:zombie 0.5 -60 4.5 {NoAI:1b}'); L.look(0.5, -60, 0.5, 0, 10, ) if False else L.server_cmd('tp Tester 0.5 -60 0.5 0 5', 2)
    L.shot('01_hud.png'); d.key('e'); time.sleep(2); L.shot('02_inventory.png'); d.key('Escape'); time.sleep(1)
    d.key('F3'); time.sleep(2); L.shot('03_f3.png'); d.key('F3'); time.sleep(1)
    d.key('t'); time.sleep(0.5); d.text('hello world'); time.sleep(0.5); L.shot('04_chat.png'); d.key('Escape'); time.sleep(0.5)
    d.key('F5'); time.sleep(1.5); L.shot('05_thirdperson.png'); d.key('F5'); d.key('F5'); time.sleep(0.5)
    d.key('Escape'); time.sleep(1.5); L.shot('06_pause.png')
    errs = [l for l in L.log_lines('client', r'ERROR|Exception|FATAL|Missing textures|Mixin') if not any(x in l for x in ('authlib', 'Realms', '401', 'properties', 'OpenAL', 'profile key', 'SoundSystem'))]
    json.dump({'alive': L.cproc.poll() is None, 'client_errors': errs[:40], 'n': len(errs)}, open(str(L.out / 'clientui_report.json'), 'w'), indent=1)
    print('alive', L.cproc.poll() is None, 'errors', len(errs)); [print(e[:220]) for e in errs[:15]]
