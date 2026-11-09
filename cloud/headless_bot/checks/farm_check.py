# S6949 checks/farm_check.py [OUTDIR]: ports #338 farmkitchen (+agritechevolved, hydrofarm) + carts boot, reapertest, item/block registry.
import sys, time, pathlib, json, os, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
B = '/mnt/project-files/builds/pr338/'
JARS = [B + 'diaithir-farmkitchen-neoforge-26.1.2-1.0.0.jar', B + 'diaithir-carts-neoforge-26.1.2-1.0.0.jar'] + [j for j in os.environ.get('EXTRA_JARS', '').split(',') if j]
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
with Lane('farm', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); S = L.server_cmd
    st = lambda c, w=1.5: [re.sub(r'.*MinecraftServer\]: ', '', x) for x in S(c, w)]
    rep['errors'] = [l[:260] for l in L.log_lines('server', r'ERROR|Exception|Missing|missing') if 'advancement' not in l.lower()][:15]
    S('op Tester'); S('time set day'); S('gamemode creative Tester'); S('clear Tester'); S('tp Tester 0.5 -60 0.5', 1)
    rep['reapertest'] = st('execute as Tester at Tester run diaithirfarmkitchen reapertest', 15)
    items = ['agritechevolved:advanced_planter', 'agritechevolved:biomass_burner', 'agritechevolved:basic_planter', 'hydrofarm:hydroponics_bed', 'hydrofarm:autocrafter', 'hydrofarm:energy_cell', 'hydrofarm:hydroelectric_generator']
    rep['give'] = {i: st(f'give Tester {i} 1', 0.6)[-1:] for i in items}
    rep['setblock'] = {}
    for n, i in enumerate(items):
        rep['setblock'][i] = st(f'setblock {3 + n * 2} -60 3 {i}', 0.6)[-1:]
    S('tp Tester 9 -58 -2 0 30', 1); time.sleep(2); L.shot('02_blocks.png')
    rep['blocks_present'] = {i: st(f'execute if block {3 + n * 2} -60 3 {i}', 0.6)[-1:] for n, i in enumerate(items)}
    L.shot('01_after.png')
    rep['mods_log'] = [l[-180:] for l in L.log_lines('server', r'(?i)agritechevolved|hydrofarm|diaithirfarmkitchen')][:25]
json.dump(rep, open((out or '.') + '/farm_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, json.dumps(v)[:1200])
