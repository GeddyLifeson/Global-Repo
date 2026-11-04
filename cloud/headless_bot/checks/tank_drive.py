# S6892 checks/tank_drive.py [OUTDIR]: IV tank (diaithirtanks.tank_mk1): icon, place, find the seat by scanning aims with an empty hand (R), then throttle/steer/fire keys.
import sys, time, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
PF = '/mnt/project-files/'
import os
ARMS = os.environ.get('TANK_ARMS_JAR', PF + 'vehicles-test/diaithir-arms-neoforge-26.1.2-1.0.1.jar')
EXTRA = [x for x in os.environ.get('TANK_EXTRA_JARS', '').split(':') if x]  # e.g. vehicles-test units + carts jars (ignition command /diaithirvehicle)
JARS = [ARMS, PF + 'Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar'] + EXTRA
out = sys.argv[1] if len(sys.argv) > 1 else None; rep = {}
CF = {'config/mtsconfigclient.json': open(os.environ['TANK_CLIENT_CFG']).read()} if os.environ.get('TANK_CLIENT_CFG') else None  # e.g. fullHUD_1P=true variant
with Lane('tank', JARS, client_files=CF, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive; S = L.server_cmd
    S('time set day'); S('gamemode ' + ('survival' if os.environ.get('TANK_SURV') else 'creative') + ' Tester'); S('clear Tester'); S('tp Tester 0.5 -60 0.5 0 35', 1)
    S('item replace entity Tester hotbar.0 with mts:diaithirtanks.tank_mk1'); L.wait_render(); d.key('1'); time.sleep(0.5); L.shot('01_icon_held.png')
    d.key('r'); time.sleep(5); S('item replace entity Tester hotbar.0 with minecraft:air')
    rep['missing_texture_warnings'] = len(L.log_lines('client', r'Missing textures in model mts:item/diaithirtanks'))
    rep['entities'] = S('execute as Tester run say near: @e[distance=..20,type=!player]', 1)
    mounted = False
    import re, math
    pos = S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 1); rep['veh_pos'] = pos
    m = re.search(r'\[(-?[\d.]+)d, (-?[\d.]+)d, (-?[\d.]+)d\]', ' '.join(pos)); vx, vy, vz = (float(m[1]), float(m[2]), float(m[3])) if m else (0.5, -60, 2.5)
    import re
    rep['entity_data_600'] = ''.join(S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest]', 1.5))[:900]
    # instrument item on the hull: stand 3 blocks off the hull side, aim at it, right-click with mts:diaithirtanks.speedo in hand
    S('item replace entity Tester hotbar.1 with mts:diaithirtanks.speedo'); S(f'tp Tester {vx + 3.0:.2f} {vy:.2f} {vz:.2f} 90 20', 0.8); d.key('2'); time.sleep(0.5); d.key('r'); time.sleep(1.5); L.shot('01b_speedo_on_hull.png')
    rep['after_speedo_click'] = S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest]', 1.5)[0][-400:] if True else ''
    S('item replace entity Tester hotbar.1 with minecraft:air'); d.key('1'); time.sleep(0.4); S(f'tp Tester {vx + 4.0:.2f} {vy:.2f} {vz:.2f} 90 15', 1.0); time.sleep(1.5); L.shot('01c_parked_engine_off_nearby.png')
    if os.environ.get('TANK_SURV'): S('clear Tester'); time.sleep(0.5); d.key('1'); time.sleep(0.3)  # survival: drop the join handbook so R is an empty-hand click and no GUI eats keys
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
        DV = lambda c, w=1.2: S('execute as Tester at Tester run diaithirvehicle ' + c, w)
        rep['seat_pos'] = S('data get entity Tester Pos', 0.6)
        S('gamemode survival Tester'); time.sleep(0.5)
        rep['start'] = DV('start'); time.sleep(1.5); rep['status_after_start'] = DV('status'); L.shot('02_hud_after_start.png')
        d.key('F5'); time.sleep(1.5); L.shot('02c_third_person.png'); d.key('F5'); time.sleep(1.0); L.shot('02d_back_first_person.png')
        if os.environ.get('TANK_FUEL'):
            rep['fuel_drive1'] = DV('drive 1')
            rep['fuel_status'] = []
            for _ in range(3):
                rep['fuel_status'].append(DV('status')); time.sleep(5)
            L.shot('06_fuel_drive1.png')
            json.dump(rep, open(os.path.join(sys.argv[1], 'tank_report.json'), 'w'), indent=1, default=str)
            raise SystemExit
        if os.environ.get('TANK_FIRE_FIRST'):  # fire while seated, stopped, before driving (a tp after driving drops the seat)
            ENT0 = "execute as Tester at Tester run say ents: @e[distance=..80,type=!player]"
            ents0 = lambda: ' '.join(S(ENT0, 1.0)).split('ents: ')[-1]
            rep['ff_seat_check'] = S('data get entity Tester RootVehicle', 0.6)
            import re as _r
            def gunstate():
                t = ''.join(S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest]', 1.5))
                return _r.findall(r'loadedBullet\d: \{[^}]*count: \d+\}', t)
            rep['ff_gun_before'] = gunstate()
            rep['ff_before'] = ents0(); nl = len(L.log_lines('server', r'.'))
            if os.environ.get('TANK_FIRE_CMD'):
                if os.environ.get('TANK_IMPACT'):
                    S('difficulty easy')
                    for x in (12, 20, 30, 45): S(f'summon minecraft:pig {x}.5 -60 2.5 {{NoAI:1b,Silent:1b}}', 0.3)
                    S('fill 60 -60 0 60 -57 5 minecraft:stone', 0.5); S('setblock 25 -60 2 minecraft:tnt', 0.3)
                    rep['impact_before'] = ents0()
                rep['ff_status_before'] = S('execute as Tester at Tester run diaithirvehicle status', 1.0)
                rep['ff_cmd'] = S('execute as Tester at Tester run diaithirvehicle fire ' + os.environ.get('TANK_FIRE_TICKS', '60'), 1.0); time.sleep(1.5); L.shot('05c_fire_cmd_1.png'); time.sleep(2.5)
                rep['ff_status_after'] = S('execute as Tester at Tester run diaithirvehicle status', 1.0); rep['ff_ents_cmd'] = ents0(); rep['impact_blocks'] = S('execute if block 60 -58 2 minecraft:stone run say stone_intact', 0.5) + S('execute if block 25 -60 2 minecraft:tnt run say tnt_intact', 0.5); rep['ff_gun_cmd'] = gunstate(); L.shot('05d_fire_cmd_2.png')
            d.hold('space', 3.0); time.sleep(0.5); L.shot('05a_fire_seated.png'); d.hold('space', 0.2); time.sleep(0.3); L.shot('05b_fire_seated_tap.png')
            rep['ff_gun_after'] = gunstate()
            rep['ff_after'] = ents0(); rep['ff_server_lines'] = [l[:240] for l in L.log_lines('server', r'.')[nl:] if 'ents:' not in l][:15]
            rep['ff_vehicle_after'] = ''.join(S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest]', 1.5))[:100]
        VL = lambda: [l.split(']: ', 1)[-1] for l in L.log_lines('server', r't-\d+s .*engines=')]
        n0 = len(VL()); DV('watch 12', 0.5); d.hold('w', 12); time.sleep(2); rep['watch_W_held'] = VL()[n0:]; L.shot('03_hud_W_held.png')
        n1 = len(VL()); DV('watch 12', 0.5); time.sleep(14); rep['watch_W_released'] = VL()[n1:]
        rep['veh_pos_end'] = S(VP, 0.6)
        DV('drive 0'); DV('stop'); time.sleep(6)
        vp = re.search(r'\[(-?[\d.]+)d, (-?[\d.]+)d, (-?[\d.]+)d\]', ' '.join(S(VP, 0.6)))
        if vp:
            S(f'tp Tester {float(vp[1]) + 4.0:.2f} {float(vp[2]):.2f} {float(vp[3]):.2f} 90 15', 1.0); time.sleep(2); L.shot('04c_stopped_engine_off_nearby.png')
            S(f'tp Tester {float(vp[1]) + 2.4:.2f} {float(vp[2]):.2f} {float(vp[3]):.2f} 90 15', 1.0)
        ENT = "execute as Tester at Tester run say ents: @e[distance=..60,type=!player]"
        def ents():
            return ' '.join(S(ENT, 1.0)).split('ents: ')[-1]
        rep['veh_full'] = ''.join(S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest]', 1.5)); import re as _re; rep['veh_parts'] = _re.findall(r'systemName: "([^"]+)"', rep['veh_full'])
        rep['fire_entities_before'] = ents(); nl0 = len(L.log_lines('server', r'.'))
        d.hold('space', 3.0); time.sleep(0.5); L.shot('05_fire.png')
        rep['fire_entities_after'] = ents()
        rep['fire_new_server_lines'] = [l[:240] for l in L.log_lines('server', r'.')[nl0:] if 'ents:' not in l][:15]
        rep['fire_client_lines'] = [l[:200] for l in L.log_lines('client', r'(?i)fire|shell|bullet|gun|cannon|projectile')][-8:]
        L.shot('03_driven.png')
        rep['pos_after'] = S('data get entity Tester Pos', 0.8); rep['veh_pos_after'] = S('data get entity @e[type=mts:builder_existing,limit=1,sort=nearest] Pos', 0.8)
    rep['client_instrument_lines'] = L.log_lines('client', r'(?i)instrument|speedo|tacho|diaithirtanks:|instruments\.png|gauge|null')[:40]
    rep['client_errors'] = [l for l in L.log_lines('client', r'ERROR|Exception') if not any(x in l for x in ('authlib', 'Realms', '401', 'OpenAL', 'profile key', 'SoundSystem', 'MTSERROR: Welcome'))][:10]
json.dump(rep, open((out or '.') + '/tank_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, str(v)[:400])
