# S6869 checks/storage_checks.py: open the menu of every storage-logistics block with the real client (R = use) and screenshot it.
# python3 -I storage_checks.py [OUTDIR]   Jars: all of rewrite-jars/storage-logistics. Menus drive from a row of placed blocks.
import sys, glob, time, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
from discover import discover
JARS = sorted(glob.glob('/mnt/project-files/rewrite-jars/storage-logistics/*.jar'))
out = sys.argv[1] if len(sys.argv) > 1 else None
ids = [b for j in JARS for b in discover(j)['blocks'] if not b.split(':')[1].startswith(('foundry_bricks', 'energy_pipe', 'fluid_pipe', 'item_pipe'))]
rep = {}
with Lane('storage', JARS, out=out, srv_xmx='3G') as L:
    L.start_client(); d = L.drive
    for c in ('gamemode creative Tester', 'time set day'): L.server_cmd(c)
    L.wait_render()
    for b in ids:
        n = b.replace(':', '_')
        L.server_cmd('setblock 0 -60 -3 minecraft:air'); fb = L.server_cmd(f'setblock 0 -60 -3 {b}', 0.8)
        L.look(0.5, -60, 0.5, 180, 20); L.shot(f'{n}_0_block.png')
        d.key('r'); time.sleep(2.5); L.shot(f'{n}_1_menu.png'); d.key('Escape'); time.sleep(1)
        rep[b] = {'placed': any('Changed' in l for l in fb)}
    print('client errs', [l for l in L.log_lines('client', r'ERROR|Exception|Missing') if not any(x in l for x in ('authlib', 'Realms', '401', 'properties'))][:10])
    print('server errs', [l for l in L.log_lines('server', r'ERROR|Exception') if not any(x in l for x in ('DebugFile', 'kqueue', 'layers'))][:6])
json.dump(rep, open((out or '.') + '/storage_report.json', 'w'), indent=1)
