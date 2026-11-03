# S6856 checks/qol_checks.py: DRIVER.md "Join checklist: qol-client clean-room group" (lookat box, claims map, ctm) with screenshots.
# python3 -I qol_checks.py [OUTDIR]   (cloud only; flat overworld at spawn, light pack = the five qol-client jars)
import sys, glob, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
JARS = sorted(glob.glob('/mnt/project-files/rewrite-jars/qol-client/*.jar'))
out = sys.argv[1] if len(sys.argv) > 1 else None
res = {}
with Lane('qol', JARS, out=out) as L:
    print('joined', L.start_client()); d = L.drive
    # standing spot: flat world, spawn (-8,-60,5). Platform of known blocks 4 m north (z=-4), player looks north (yaw 180).
    L.server_cmd('gamemode creative Tester'); L.server_cmd('time set day'); L.server_cmd('weather clear')
    L.server_cmd('tp Tester 0.5 -60 0.5 180 10', 2); L.shot('00_spawn.png')
    # 1. look-at box: a block, a mob, a waypoint stone, a claimed chunk
    L.server_cmd('setblock 0 -60 -3 minecraft:stone'); L.look(0.5, -60, 0.5, 180, 20); L.shot('01_lookat_block.png')
    L.server_cmd('summon minecraft:pig 0.5 -60 -3.5 {NoAI:1b}'); L.look(0.5, -60, 0.5, 180, 20); L.shot('02_lookat_mob.png')
    L.server_cmd('setblock 0 -60 -3 diaithirwaypoints:waypoint_stone'); L.look(0.5, -60, 0.5, 180, 20); L.shot('03_lookat_waypoint.png')
    L.server_cmd('execute as Tester at Tester run claim'); time.sleep(1)
    L.server_cmd('setblock 0 -60 -3 minecraft:stone'); L.look(0.5, -60, 0.5, 180, 20); L.shot('04_lookat_claimed_chunk.png')
    # 2. claims map screen
    d.chat('/claim map'); time.sleep(2); L.shot('05_claim_map_screen.png'); d.key('Escape'); time.sleep(1)
    print('server lines', L.log_lines('server', r'ERROR|Exception')[:4])
# 3. connected textures, flag off then on (two joins: the toml is read at client start)
WALL = ['fill -4 -60 -6 4 -60 -6 diaithirctm:connected_glass', 'fill -2 -59 -8 0 -57 -8 diaithirctm:connected_plating', 'fill 2 -59 -8 4 -57 -8 diaithirctm:connected_glass', 'setblock 6 -60 -6 diaithirctm:connected_plating']
for tag, files in (('off', {}), ('on', {'config/diaithirctm-client.toml': 'enabled = true\n'})):
    with Lane('qol_ctm_' + tag, JARS, client_files=files, out=out) as L:
        L.start_client(); L.server_cmd('gamemode creative Tester'); L.server_cmd('time set day')
        for w in WALL: L.server_cmd(w)
        L.look(0.5, -60, 0.5, 180, 12); L.shot(f'06_ctm_{tag}.png'); L.look(0.5, -60, -2.5, 160, 10); L.shot(f'07_ctm_{tag}_close.png')
        print(tag, L.log_lines('client', r'diaithirctm|ctm')[:3])
