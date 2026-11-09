# S6948 checks/freight_selftest.py [OUTDIR]: runs /diaithircarts freighttest (and selftest) in a real world, prints PASS/FAIL lines.
import sys, time, pathlib, json, os, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
V = '/mnt/project-files/vehicles-test/' + os.environ.get('ARMS_DIR', 'combined') + '/'
JARS = [V + 'diaithir-arms-neoforge-26.1.2-1.0.1.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar', V + 'diaithir-carts-neoforge-26.1.2-1.0.0.jar', os.environ.get('UNITS_JAR', '/tmp/claude-0/unitsjar/diaithir-units-neoforge-26.1.2-1.0.0.jar')]
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
with Lane('frtest', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); S = L.server_cmd
    st = lambda c, w=1.5: [re.sub(r'.*MinecraftServer\]: ', '', x) for x in S(c, w)]
    S('op Tester'); S('time set day'); S('tp Tester 0.5 -60 0.5', 1)
    for c in ('freighttest', 'selftest'):
        rep[c] = st(f'execute as Tester at Tester run diaithircarts {c}', 12)
    rep['log'] = [l[-200:] for l in L.log_lines('server', r'(?i)freight.*(PASS|FAIL)|self test|BayData')][:20]
json.dump(rep, open((out or '.') + '/freight_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, json.dumps(v)[:900])
