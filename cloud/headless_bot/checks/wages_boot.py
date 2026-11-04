# S6893 checks/wages_boot.py [OUTDIR]: server-only boot of the KubeJS economy (RPG #259 scripts) with KubeJS, Rhino, Lightman's, diaithir-ages, carts + IV; scans [economy] and script errors.
import sys, glob, time, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
RPG = '/home/user/diaithirrpg/content/economy/'
JARS = sorted(glob.glob('/tmp/claude-0/econlib/*.jar')) + ['/mnt/project-files/builds/ages-diaithir2/diaithir-ages-neoforge-26.1.2-0.1.0-diaithir.2.jar', '/mnt/project-files/vehicles-test/diaithir-carts-neoforge-26.1.2-1.0.0.jar', '/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar']
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
with Lane('wages', JARS, server_dirs={'kubejs': RPG + 'kubejs', 'config': RPG + 'config'}, srv_xmx='3G', out=out) as L:
    S = L.server_cmd
    rep['economy'] = S('economy', 2); rep['reload'] = S('kubejs reload server_scripts', 8)
    rep['lines'] = L.log_lines('server', r'\[economy\]|kubejs|KubeJS|ages|Ages')[-40:]
    rep['errors'] = [l for l in L.log_lines('server', r'ERROR|Exception|error') if not any(x in l for x in ('DebugFile', 'kqueue', 'layers'))][:30]
json.dump(rep, open((out or '.') + '/wages_boot.json', 'w'), indent=1)
for k, v in rep.items(): print(k, str(v)[:1500])
