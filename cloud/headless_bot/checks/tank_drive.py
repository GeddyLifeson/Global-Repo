# S6892 checks/tank_drive.py [OUTDIR]: IV tank (diaithirtanks.tank_mk1): icon, place, find the seat by scanning aims with an empty hand (R), then throttle/steer/fire keys.
import sys, time, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
PF = '/mnt/project-files/'
import os
ARMS = os.environ.get('TANK_ARMS_JAR', PF + 'rewrite-jars/combat-classes/diaithir-arms-neoforge-26.1.2-1.0.1.jar')
EXTRA = [x for x in os.environ.get('TANK_EXTRA_JARS', '').split(':') if x]  # e.g. vehicles-test units + carts jars (ignition command /diaithirvehicle)
JARS = [ARMS, PF + 'Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar'] + EXTRA
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
with Lane('tank', JARS, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive; S = L.server_cmd
    S('time set day'); S('gamemode creative Tester'); S('clear Tester'); S('tp Tester 0.5 -60 0.5 0 35', 1)
    S('item replace entity Tester hotbar.0 with mts:diaithirtanks.tank_mk1'); L.wait_render(); d.key('1'); time.sleep(0.5); L.shot('01_icon_held.png')
    d.key('r'); time.sleep(5); S('item replace entity Tester hotbar.0 with minecraft:air')
    rep['missing_texture_warnings'] = len(L.log_lines('client', r'Missing textures in model mts:item/diaithirtanks'))
    rep['entities'] = S('execute as Tester run say near: @e[distance=..20,type=!player]', 1)
    mounted = False
    import re, math
    pos = S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 1); rep['veh_pos'] = pos
    m = re.search(r'\[(-?[\d.]+)d, (-?[\d.]+)d, (-?[\d.]+)d\]', ' '.join(pos)); vx, vy, vz = (float(m[1]), float(m[2]), float(m[3])) if m else (0.5, -60, 2.5)
    # first try the vanilla ride command (works when the vehicle exposes a passenger slot), then fall back to scanning for the seat
    import re
    rep['ride_cmd'] = S('ride Tester mount @e[type=mts:builder_existing,limit=1,sort=nearest]', 1.5)
    rr = S('data get entity Tester RootVehicle', 0.8)
    pp = S('data get entity Tester Pos', 0.8); rep['pos_after_ride'] = pp
    if any('following' in l for l in rr): mounted = True; rep['mounted_via'] = 'ride command'
    elif any(re.search(r'\[2\.[3-5]\d*d', l) for l in pp): mounted = True; rep['mounted_via'] = 'player at seat 1 world position (2.4, y, z); RootVehicle is not set for IV seats'
    # scan: ring around the vehicle, aim at points up the hull, empty hand, R, test RootVehicle
    for r in ((3.0, 5.0, 2.0) if not mounted else ()):
        for ang in range(0, 360, 45):
            px, pz = vx + r * math.cos(math.radians(ang)), vz + r * math.sin(math.radians(ang)); yaw = math.degrees(math.atan2(-(vx - px), vz - pz))
            for pitch in (5, 20, 40):
                S(f'tp Tester {px:.2f} {vy:.2f} {pz:.2f} {yaw:.1f} {pitch}', 0.4); d.key('r'); time.sleep(0.9)
                rr = S('data get entity Tester RootVehicle', 0.6)
                if any('following' in l for l in rr): mounted = True; rep['mounted_at'] = (round(px, 1), round(pz, 1), round(yaw), pitch); break
            if mounted: break
        if mounted: break
    L.shot('02_after_mount_try.png'); rep['mounted'] = mounted
    if mounted:
        rep['pos_before'] = S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 0.8)
        rep['start_cmd'] = S('execute as Tester run diaithirvehicle start', 1.5); time.sleep(1); L.shot('02a_after_start.png')
        VP = "data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos"
        for label, press_n in (('brake_as_spawned', False), ('brake_toggled_once', True), ('brake_toggled_twice', True)):
            if press_n: d.key('n'); time.sleep(0.8)
            p0 = S(VP, 0.6); d.hold('w', 4); time.sleep(0.5); p1 = S(VP, 0.6); rep['gas_' + label] = (p0[-1:], p1[-1:])
            L.shot(f'03_{label}.png')
        d.hold('space', 1.0); time.sleep(0.5); L.shot('04_fire.png')
        rep['server_log_tail'] = L.log_lines('server', r'engine|Engine|fuel|Fuel|tank|Tank')[-6:]
        L.shot('03_driven.png')
        rep['pos_after'] = S('data get entity Tester Pos', 0.8); rep['veh_pos_after'] = S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 0.8)
    rep['client_errors'] = [l for l in L.log_lines('client', r'ERROR|Exception') if not any(x in l for x in ('authlib', 'Realms', '401', 'OpenAL', 'profile key', 'SoundSystem', 'MTSERROR: Welcome'))][:10]
json.dump(rep, open((out or '.') + '/tank_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, str(v)[:400])
