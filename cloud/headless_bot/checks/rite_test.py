# S6891 checks/rite_test.py [OUTDIR]: rite on a planet (ports #142 data + #153 loader): /rite page, use the planet's Ascendant altar, play 2 steps, expect the spell scroll drop.
# Jars: diaithir-bosses (built from diaithircompat), diaithir_druidry (build.py), Spell Engine + Spell Power + deps (Modrinth, modrinth_fetch.py), plus a tiny test dimension
# diaithir_planets:alaenneirae (flat) built here because the dimension jar is not delivered yet.
import sys, glob, time, pathlib, json, zipfile, os
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
P = '/home/user/geddylifeson/diaithir-ports/'
LIB = sorted(glob.glob('/tmp/claude-0/riteslib/*.jar'))
JARS = [P + 'diaithir-bosses/build/libs/diaithir-bosses-neoforge-26.1.2-1.0.0.jar', P + 'diaithir-druidry/build/diaithir_druidry-0.1.0.jar'] + LIB
out = sys.argv[1] if len(sys.argv) > 1 else None
RITE = 'AR.alaenneirae.E1.powers.000398'; DIM = 'diaithir_planets:alaenneirae'
td = pathlib.Path('/tmp/claude-0/testdim.jar')
with zipfile.ZipFile(td, 'w') as z:
    z.writestr('META-INF/MANIFEST.MF', 'Manifest-Version: 1.0\n')
    z.writestr('META-INF/neoforge.mods.toml', 'modLoader="lowcodefml"\nloaderVersion="[1,)"\nlicense="MIT"\n[[mods]]\nmodId="testdim"\nversion="1"\n')
    z.writestr('data/diaithir_planets/dimension/alaenneirae.json', json.dumps({'type': 'minecraft:overworld', 'generator': {'type': 'minecraft:flat', 'settings': {'biome': 'minecraft:plains', 'features': False, 'lakes': False, 'layers': [{'block': 'minecraft:bedrock', 'height': 1}, {'block': 'minecraft:stone', 'height': 126}, {'block': 'minecraft:grass_block', 'height': 1}], 'structure_overrides': []}}}))
# planet biome tags (#diaithir_planets:<planet>) come from the overworld-biomes #145 jar, not delivered yet; the bosses jar will not boot without them
planets = sorted({n.split('/')[-1][:-5] for n in zipfile.ZipFile(JARS[0]).namelist() if 'worldgen/structure/planet_altar/' in n and n.endswith('.json')})
with zipfile.ZipFile(td, 'a') as z:
    for pl in planets: z.writestr(f'data/diaithir_planets/tags/worldgen/biome/{pl}.json', json.dumps({'values': ['minecraft:plains'] if pl == 'alaenneirae' else []}))
rep = {}
with Lane('rite', JARS + [str(td)], props={'difficulty': 'easy'}, srv_xmx='3G', out=out) as L:
    L.start_client(); d = L.drive
    S = lambda c, w=1.0: L.server_cmd(c, w)
    IN = f'execute in {DIM} run '
    S('time set day'); S('gamemode survival Tester'); S('clear Tester')
    rep['info'] = S(f'rite info {RITE}', 1.5)
    rep['dim'] = S(IN + 'forceload add 0 0', 2)
    rep['place'] = S(IN + 'place structure diaithirbosses:planet_altar/alaenneirae 0 64 0', 6)
    altar = None
    for x in range(0, 10):
        for y in (64, 65):
            for z in range(0, 10):
                if any('Test passed' in l for l in S(IN + f'execute if block {x} {y} {z} diaithirbosses:ascendant_altar', 0.15)): altar = (x, y, z)
    rep['altar_at'] = altar
    ax, ay, az = altar or (4, 64, 4)
    rep['tp'] = S(f'execute in {DIM} run tp Tester {ax + 0.5} {ay} {az - 3.5} facing {ax + 0.5} {ay + 0.5} {az + 0.5}', 3); S('execute as Tester at Tester run tp @s ~ ~ ~ 0 22', 1)
    L.shot('01_at_altar.png')
    rep['page'] = S(f'execute as Tester run rite page {RITE}', 1.5); S('give Tester minecraft:amethyst_shard 3')
    L.shot('02_page_given.png'); d.key('1'); time.sleep(0.4)
    d.key('r'); time.sleep(2.5); L.shot('03_altar_use_page.png'); rep['use_page'] = L.log_lines('server', r'rite|Rite|altar')[-4:]
    S('item replace entity Tester hotbar.0 with minecraft:amethyst_shard 3'); d.key('1'); time.sleep(0.4); d.key('r'); time.sleep(2.5); L.shot('04_altar_step1.png')
    for i in range(10): S(IN + f'summon minecraft:spider {ax + 0.5} {ay} {az + 5.5} {{NoAI:1b}}', 0.3)
    S(IN + 'kill @e[type=minecraft:spider]', 2.5); L.shot('05_step2_kills.png')
    rep['items'] = S(IN + f'execute as @e[type=minecraft:item,x={ax},y={ay},z={az},distance=..10] run data get entity @s Item', 1.5)
    rep['count_items'] = S(IN + f'execute if entity @e[type=minecraft:item,x={ax},y={ay},z={az},distance=..10]', 1)
    time.sleep(1); L.shot('06_after.png')
    rep['server_rite_lines'] = L.log_lines('server', r'[Rr]ite|learned|Venaerys|spell_scroll')[-15:]
    rep['client_chat'] = L.log_lines('client', r'\[CHAT\]')[-20:]
    rep['errors'] = [l for l in L.log_lines('server', r'ERROR|Exception') if not any(x in l for x in ('DebugFile', 'kqueue', 'layers'))][:15]
json.dump(rep, open((out or '.') + '/rite_report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, str(v)[:700])
