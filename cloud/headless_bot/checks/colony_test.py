# S6928 checks/colony_test.py [OUTDIR]: /colony list|info|found|where|party + planet weather hazards (diaithir-overworld-biomes, planets PR #217), then a server restart and /colony where.
import sys, time, pathlib, json, os, subprocess
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
JARS = ['/mnt/project-files/test-jars/planets/diaithir-overworld-biomes-neoforge-26.1.2-1.0.0.jar']
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
with Lane('colony', JARS, props={'difficulty': 'easy'}, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive
    S = lambda c, w=1.0: L.server_cmd(c, w)
    def chat(c, w=3.0, shot=None):
        n0 = len(L.log_lines('client', r'\[CHAT\]'))
        d.chat(c); time.sleep(w)
        r = [l.split('[CHAT]')[-1].strip() for l in L.log_lines('client', r'\[CHAT\]')][n0:]
        if shot: L.shot(shot)
        rep[c] = r; print(c, *['   ' + x[:300] for x in r], sep='\n'); return r
    S('gamemode survival Tester'); S('time set day')
    chat('/colony list'); chat('/colony info ameosastia')
    chat('/colony found ameosastia', 8, '01_found.png')
    rep['pos_after_found'] = S('data get entity Tester Dimension', 1) + S('data get entity Tester Pos', 1)
    chat('/colony where', 3, '02_where.png')
    chat('/planet weather ameosastia')
    rep['effects'] = S('data get entity Tester active_effects', 1); time.sleep(20)
    rep['effects_20s'] = S('data get entity Tester active_effects', 1); L.shot('03_outdoors.png')
    chat('/colony party add Nobody'); chat('/colony party leave')
    rep['file'] = open(str(L.srv / 'world/diaithir_colonies.json')).read() if (L.srv / 'world/diaithir_colonies.json').exists() else 'NO FILE'
    print('FILE', rep['file'][:500])
    # restart server, rejoin, /colony where
    S('save-all flush', 4); S('stop', 12)
    os.killpg(L.cproc.pid, 9) if L.cproc.poll() is None else None
    subprocess.run(['pkill', '-9', '-f', 'unix_args.txt'], capture_output=True); time.sleep(3)
    (L.srv / 'cmd.in').unlink(); L.srv_log_old = (L.srv / 'server.log').rename(L.srv / 'server_run1.log')
    L.start_server(); L.start_client(); chat('/colony where', 3, '04_where_after_restart.png')
    rep['errors'] = [l for l in L.log_lines('server', r'ERROR|Exception') if not any(x in l for x in ('DebugFile', 'kqueue', 'layers'))][:15]
    rep['errors_run1'] = [l for l in open(L.srv / 'server_run1.log', errors='replace').read().splitlines() if ('ERROR' in l or 'Exception' in l) and not any(x in l for x in ('DebugFile', 'kqueue', 'layers'))][:15]
json.dump(rep, open((out or '.') + '/colony_report.json', 'w'), indent=1)
