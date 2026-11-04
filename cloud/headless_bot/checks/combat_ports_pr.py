# S6910 checks/combat_ports_pr.py: bot-test diaithir-ports PRs #302 (Tool Belt), #313 (sentry turret, mining laser), #316 (Yori rings/aglets in Curios), #309 (class skill trees).
# Needs jars built from the PR heads in /tmp/claude-0/jars (gear-302 arms-313 relics-316 classes-309) plus Curios, Spell Engine, Spell Power (modrinth_fetch.py -> /tmp/claude-0/deps).
# python3 -I combat_ports_pr.py OUTDIR [--only turret|laser|yori|classes|belt]
import sys, glob, time, pathlib, json, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
args = [a for a in sys.argv[1:] if not a.startswith('--')]; out = args[0]
only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
J = '/tmp/claude-0/jars/'; DEPS = sorted(glob.glob('/tmp/claude-0/deps/*.jar'))
JARS = ([] if '--nogear' in sys.argv else [J + 'gear-302.jar']) + [J + 'arms-313.jar', J + 'relics-316.jar', J + 'classes-309.jar'] + DEPS
R = {}
def val(L, c):  # last "has the value X" number from an `attribute ... get` feedback
    fb = ' '.join(L.server_cmd(c, 1.0)); m = re.search(r'value of [^:]*: ([-0-9.]+)', fb) or re.search(r'has a value of ([-0-9.]+)', fb)
    return float(m.group(1)) if m else fb
with Lane('pr', JARS, props={'difficulty': 'easy', 'spawn-monsters': 'false'}, srv_xmx='3G', out=out) as L:
    (L.cl / 'options.txt').open('a').write('key_key.toolbelt.open:key.keyboard.g\nkey_key.toolbelt.slot:key.keyboard.v\n')
    print('joined', L.start_client()); d = L.drive
    for c in ('gamemode survival Tester', 'time set day', 'weather clear', 'gamerule mob_griefing false', 'gamerule spawn_mobs false', 'kill @e[type=!player]'): L.server_cmd(c)
    L.wait_render(); time.sleep(3)
    L.look(0.5, -60, 0.5, 180, 8)
    if only in (None, 'classes'):
        base = val(L, 'attribute Tester minecraft:max_health get')
        print(L.server_cmd('execute as Tester run skills class fian'), L.server_cmd('execute as Tester run skills give Tester 5'))
        fb = L.server_cmd('execute as Tester run skills unlock hardy'); fb2 = L.server_cmd('execute as Tester run skills show')
        R['classes'] = {'base_max_health': base, 'unlock': fb, 'after_unlock': val(L, 'attribute Tester minecraft:max_health get'), 'show': fb2}
        L.server_cmd('execute as Tester run skills unlock shieldwall'); R['classes']['armor_after_shieldwall'] = val(L, 'attribute Tester minecraft:armor get')
        L.server_cmd('execute as Tester run skills reset'); R['classes']['after_reset'] = val(L, 'attribute Tester minecraft:max_health get')
        L.server_cmd('execute as Tester run skills class fian'); L.server_cmd('execute as Tester run skills give Tester 5'); L.server_cmd('execute as Tester run skills unlock hardy')
        L.server_cmd('kill Tester'); time.sleep(2); d.click(640,343); time.sleep(3); R['classes']['after_respawn'] = val(L, 'attribute Tester minecraft:max_health get')
        L.shot('classes.png'); L.server_cmd('execute as Tester run skills reset'); print(R['classes'])
    if only in (None, 'yori'):
        y = {}
        for item, slot, attr in (('emerald_ring', 'ring', 'minecraft:max_health'), ('netherite_ring', 'ring', 'minecraft:armor'), ('golden_aglet', 'charm', 'minecraft:movement_speed'), ('netherite_shield_charm', 'charm', 'minecraft:knockback_resistance')):
            b = val(L, f'attribute Tester {attr} get')
            fb = L.server_cmd(f'curios replace {slot} 0 Tester with diaithirrelics:{item}', 1.5); time.sleep(2.5)
            on = val(L, f'attribute Tester {attr} get')
            L.server_cmd(f'curios replace {slot} 0 Tester with air', 1.0); time.sleep(2.5)
            off = val(L, f'attribute Tester {attr} get')
            y[item] = {'curios_fb': fb, 'before': b, 'worn': on, 'removed': off}
        L.server_cmd('curios replace ring 0 Tester with diaithirrelics:emerald_ring'); time.sleep(2.5)
        d.key('e'); time.sleep(1.5); L.shot('yori_inventory.png'); d.key('Escape'); time.sleep(0.5)
        print(L.server_cmd('yoriselftest', 1.5)); R['yori'] = y; print(y)
    if only in (None, 'turret'):
        L.server_cmd('kill @e[type=!player]'); L.server_cmd('fill -3 -61 -20 3 -50 -4 air'); L.server_cmd('fill -3 -61 -20 3 -61 -4 stone')
        L.server_cmd('setblock 0 -60 -6 diaithirarms:sentry_turret'); L.server_cmd('item replace entity Tester hotbar.0 with arrow 16'); L.server_cmd('tp Tester 0.5 -60 -3.5 180 33', 1.5)
        d.key('1'); time.sleep(0.5); d.key('r'); time.sleep(1)
        st = L.server_cmd('data get block 0 -60 -6', 1)  # blockstate not in nbt; read via execute if
        L.server_cmd('execute if block 0 -60 -6 diaithirarms:sentry_turret[ammo=32]'); 
        ammo0 = [l for l in L.server_cmd('execute if block 0 -60 -6 diaithirarms:sentry_turret[ammo=32]', 1) if 'passed' in l]
        L.shot('turret_loaded.png')
        L.server_cmd('summon husk 0.5 -60 -14 {NoAI:1b,PersistenceRequired:1b,Health:20f,CanPickUpLoot:0b}', 1)
        L.server_cmd('summon cow 4.5 -60 -10 {NoAI:1b,PersistenceRequired:1b}', 1)
        L.shot('turret_t0.png'); hp = []
        for i in range(8):
            time.sleep(0.8); hp.append(L.server_cmd('data get entity @e[type=husk,limit=1] Health', 0.4))
        L.shot('turret_t24.png')
        cowhp = L.server_cmd('data get entity @e[type=cow,limit=1] Health', 1)
        am = [a for a in range(0, 33) if L.server_cmd(f'execute if block 0 -60 -6 diaithirarms:sentry_turret[ammo={a}] run say AMMO{a}', 0.4) and any(f'AMMO{a}' in l for l in L.server_cmd('say .', 0.1))]
        R['turret'] = {'loaded_16_arrows_ammo32': bool(ammo0), 'zombie_health_series': hp, 'cow_health': cowhp}
        print(R['turret'])
    if only in (None, 'laser'):
        L.server_cmd('kill @e[type=!player]'); L.server_cmd('fill -3 -61 -20 3 -50 -4 air'); L.server_cmd('fill -3 -61 -20 3 -61 -4 stone')
        L.server_cmd('setblock 0 -59 -10 stone'); L.server_cmd('setblock 0 -59 -12 obsidian'); L.server_cmd('setblock 0 -59 -14 dirt')
        L.server_cmd('item replace entity Tester hotbar.0 with diaithirarms:mining_laser'); L.server_cmd('tp Tester 0.5 -60 -5.5 180 0', 1.5)
        d.key('1'); time.sleep(0.5); L.shot('laser_held.png')
        d.key('r'); time.sleep(1.2); L.shot('laser_fired.png')
        stone_gone = any('passed' in l for l in L.server_cmd('execute unless block 0 -59 -10 stone', 1))
        L.server_cmd('tp Tester 0.5 -60 -7.5 180 0', 1.5)
        d.key('r'); time.sleep(1.2)
        obs_kept = any('passed' in l for l in L.server_cmd('execute if block 0 -59 -12 obsidian', 1))
        dur = L.server_cmd('data get entity Tester Inventory[{Slot:0b}]', 1)
        drops = L.server_cmd('execute as Tester at Tester run say items: @e[type=item,distance=..20]', 1)
        L.shot('laser_after.png'); R['laser'] = {'stone_cut': stone_gone, 'obsidian_refused': obs_kept, 'inventory_slot0': dur, 'drops': drops}; print(R['laser'])
    print('server errs', [l for l in L.log_lines('server', r'ERROR|Exception') if 'DebugFile' not in l and 'kqueue' not in l][:8])
    print('client errs', [l for l in L.log_lines('client', r'ERROR|Exception|Missing|missing') if 'authlib' not in l and 'Realms' not in l and '401' not in l and 'properties' not in l][:10])
json.dump(R, open(out + '/combat_ports_report.json', 'w'), indent=1)
