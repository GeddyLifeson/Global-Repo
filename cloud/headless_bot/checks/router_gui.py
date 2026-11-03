# S6871 checks/router_gui.py [OUTDIR]: router GUI (storage-logistics, ports #123) with the real client, tries several placements and aims.
import sys, glob, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
JARS = sorted(glob.glob('/mnt/project-files/rewrite-jars/storage-logistics/*.jar'))
with Lane('router', JARS, out=sys.argv[1] if len(sys.argv) > 1 else None, srv_xmx='3G') as L:
    L.start_client(); d = L.drive
    L.server_cmd('gamemode survival Tester'); L.server_cmd('time set day'); L.server_cmd('clear Tester')
    L.wait_render()
    for i, (blk, yaw, pitch, sx, sz) in enumerate([('diaithirrouting:router', 180, 20, 0, -3), ('diaithirrouting:router[facing=south]', 180, 20, 0, -3), ('diaithirrouting:router', 180, 35, 0, -2)]):
        L.server_cmd(f'setblock {sx} -60 {sz} air'); print(L.server_cmd(f'setblock {sx} -60 {sz} {blk}', 0.8))
        L.look(0.5, -60, 0.5, yaw, pitch); L.shot(f'router_{i}_0.png'); d.key('r'); time.sleep(3); L.shot(f'router_{i}_1.png')
        print(i, L.log_lines('client', r'RouterScreen|Exception')[-2:])
