# S6892 checks/tank_drive.py [OUTDIR]: IV tank (diaithirtanks.tank_mk1): icon, place, find the seat by scanning aims with an empty hand (R), then throttle/steer/fire keys.
import sys, time, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
PF = '/mnt/project-files/'
JARS = [PF + 'rewrite-jars/combat-classes/diaithir-arms-neoforge-26.1.2-1.0.1.jar', PF + 'Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar']
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
    rep['ride_cmd'] = S('ride Tester mount @e[type=mts:builder_existing,limit=1,sort=nearest]', 1.5)
    rr = S('data get entity Tester RootVehicle', 0.8)
    if any('following' in l for l in rr): mounted = True; rep['mounted_via'] = 'ride command'
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
        d.key('n'); time.sleep(0.8); L.shot('02b_parkbrake_toggled.png')  # IV car.park = N
        for name, key, secs in [('w', 'w', 5), ('space', 'space', 1.0), ('w', 'w', 3)]:
            d.hold(key, secs); time.sleep(0.5)
        L.shot('03a_after_gas_fire.png'); rep['veh_pos_mid'] = S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 0.8)
        for name, key, secs in [('w', 'w', 3), ('s', 's', 1.5), ('a', 'a', 1.5), ('d', 'd', 1.5), ('space', 'space', 0.5)]:
            d.hold(key, secs); time.sleep(0.5)
        L.shot('03_driven.png')
        rep['pos_after'] = S('data get entity Tester Pos', 0.8); rep['veh_pos_after'] = S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 0.8)
    rep['client_errors'] = [l for l in L.log_lines('client', r'ERROR|Exception') if not any(x in l for x in ('authlib', 'Realms', '401', 'OpenAL', 'profile key', 'SoundSystem', 'MTSERROR: Welcome'))][:10]
json.dump(rep, open((out or '.') + '/tank_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, str(v)[:400])
