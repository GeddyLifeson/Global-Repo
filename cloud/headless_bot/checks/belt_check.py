# S6940 checks/belt_check.py [OUTDIR]: Tool Belt (ports #302) client boot, item, curios belt slot, radial menu (R). Env BELT_GEAR_JAR = built diaithir-gear jar.
import sys, glob, time, pathlib, os, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
JARS = [os.environ['BELT_GEAR_JAR']] + sorted(glob.glob('/tmp/claude-0/riteslib/*.jar'))
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
with Lane('belt', JARS, srv_xmx='3G', out=out) as L:
    rep['joined'] = L.start_client(); d = L.drive; S = L.server_cmd
    S('gamemode creative Tester'); S('time set day'); S('tp Tester 0.5 -60 0.5 0 15', 1); L.wait_render()
    S('give Tester toolbelt:belt'); S('give Tester minecraft:diamond_pickaxe'); S('give Tester minecraft:iron_sword'); time.sleep(1)
    d.key('1'); time.sleep(0.5); L.shot('01_belt_held.png')
    rep['curios'] = S('curios replace belt 0 Tester with toolbelt:belt', 1.2); time.sleep(1.5)
    rep['curios_list'] = S('data get entity Tester Inventory', 1)[0][:300]
    L.shot('02_after_equip.png')
    d.key('r'); time.sleep(1.5); L.shot('03_radial_R.png')
    d.key('Escape'); time.sleep(0.5)
    rep['client_errors'] = [l[:260] for l in L.log_lines('client', r'ERROR|Exception|Missing sprite') if not any(x in l for x in ('authlib', 'Realms', '401', 'OpenAL', 'profile key', 'SoundSystem', 'MTSERROR'))][:12]
    rep['server_errors'] = [l[:260] for l in L.log_lines('server', r'ERROR|Exception')][:8]
json.dump(rep, open((out or '.') + '/belt_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, str(v)[:500])
