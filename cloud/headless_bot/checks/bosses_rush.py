# S6870 checks/bosses_rush.py JAR [OUTDIR]: real-client look at every diaithir-bosses boss (spawn, texture, boss bar) and a /boss rush start run.
# Requested by the bosses thread (ports #125). Server commands run as console 'execute as Tester at Tester'; screenshots from the real client.
import sys, time, pathlib, json, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
from discover import discover
args = [a for a in sys.argv[1:] if not a.startswith('--')]; jar = args[0]; out = args[1] if len(args) > 1 else None
ids = [e.split(':')[1] for e in discover(jar)['entities']]
X = 'execute as Tester at Tester run '
rep = {}
skip = '--skip-gallery' in sys.argv
import zipfile
REQ = json.loads(zipfile.ZipFile(jar).read('data/diaithirbosses/rush.json'))['requires_kills']
with Lane('bossrush', [jar], props={'difficulty': 'easy'}, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive
    for c in ('gamemode creative Tester', 'time set day', 'weather clear', 'gamerule spawn_mobs false', 'tp Tester 0.5 -60 0.5 180 8'): L.server_cmd(c)
    L.wait_render()
    for c in ('boss age 8', 'boss mode standard'): print(c, L.server_cmd(X + c, 1.0))
    lst = L.server_cmd(X + 'boss list', 1.5); print('boss list', lst)
    for b in ([] if skip else ids):
        L.server_cmd('kill @e[type=!player,type=!minecraft:item]'); L.server_cmd('tp Tester 0.5 -60 0.5 180 8', 0.3)
        fb = L.server_cmd(X + f'boss spawn {b}', 1.0); L.server_cmd('tp Tester 0.5 -60 0.5 180 8', 3.5); L.shot(f'boss_{b}.png')
        rep[b] = {'spawn_feedback': [l.split(']: ', 1)[-1] for l in fb][:2]}
    L.server_cmd('kill @e[type=!player,type=!minecraft:item]', 1)
    # unlock: beat the required bosses (spawn then /kill: runs the death hook), then start the rush as the player so feedback reaches the client
    for b in REQ:
        L.server_cmd(X + f'boss spawn {b}', 1.5); L.server_cmd(X + f'kill @e[type=diaithirbosses:{b}]', 1.5)
    rep['_required'] = REQ
    d.chat('/boss rush start'); time.sleep(2); L.shot('rush_00_start.png')
    print('rush start log', L.log_lines('server', r'Tester.*(rush|Rush)|fighters|locked')[-4:])
    for i in range(1, 40):
        time.sleep(4); L.shot(f'rush_{i:02d}.png')
        k = L.server_cmd('kill @e[type=!player,type=!minecraft:item]', 1.5)
        if any(re.search(r'rush.*(clear|complete|finished|won)|cleared', l, re.I) for l in L.log_lines('server', r'[Rr]ush|cleared')): break
    rep['_rush_log'] = L.log_lines('server', r'[Rr]ush')[-12:]; rep['_rush_steps'] = i
    rep['_client_errors'] = [l for l in L.log_lines('client', r'ERROR|Exception|Missing textures|missing') if not any(x in l for x in ('authlib', 'Realms', '401', 'properties', 'OpenAL', 'profile key'))][:15]
    rep['_server_errors'] = [l for l in L.log_lines('server', r'ERROR|Exception') if not any(x in l for x in ('DebugFile', 'kqueue', 'layers'))][:10]
    rep['_client_alive'] = L.cproc.poll() is None
json.dump(rep, open((out or '.') + '/bossrush_report.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k.startswith('_')}, indent=1)[:2500])
