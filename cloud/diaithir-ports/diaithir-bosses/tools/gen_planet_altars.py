#!/usr/bin/env python3 -I
# S6831 Ascendant altar shrines for the planets: one structure + structure set per planet (216), one shared template and pool.
# Biomes come from the optional tag #diaithir_planets:<id> (diaithir-overworld-biomes #145); Terra is left to the #136 rite sites.
# NBT writer pattern from diaithir-worldgen-structures tools/gen.py. Usage: python3 -I tools/gen_planet_altars.py <planets.tsv>
import csv, gzip, io, json, os, struct, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = R + '/src/main/resources/data/diaithirbosses'
ns = lambda s: struct.pack('>H', len(s.encode())) + s.encode()
def pay(w, t, v):
    if t == 3: w(struct.pack('>i', v))
    elif t == 8: w(ns(v))
    elif t == 9:
        et, items = v; w(bytes([et]) + struct.pack('>i', len(items)))
        for i in items: pay(w, et, i)
    elif t == 10:
        for k, (tt, vv) in v.items(): w(bytes([tt]) + ns(k)); pay(w, tt, vv)
        w(b'\0')
def nbt(root):
    b = io.BytesIO(); b.write(b'\x0a' + ns('')); pay(b.write, 10, root); return gzip.compress(b.getvalue(), 9, mtime=0)
# 9x5x9: stone-brick floor (y0 foundation, y1 floor), the altar in the middle, four ogham stones, lanterns on posts
pal = ['minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'diaithirbosses:ascendant_altar', 'minecraft:cobblestone_wall', 'minecraft:lantern']
rune = [0, 3, 6, 8]
blocks, props = [], []
def put(x, y, z, state): blocks.append({'pos': (9, (3, [x, y, z])), 'state': (3, state)})
for x in range(9):
    for z in range(9):
        put(x, 0, z, 0)
        put(x, 1, z, 1 if (x + z) % 3 == 0 else 0)
put(4, 2, 4, 2)
for i, (x, z) in enumerate([(1, 1), (7, 1), (1, 7), (7, 7)]):
    put(x, 2, z, 5 + i)
for x, z in [(0, 0), (8, 0), (0, 8), (8, 8)]:
    put(x, 2, z, 3); put(x, 3, z, 4)
palette = [{'Name': (8, n)} for n in pal] + [{'Name': (8, 'diaithirbosses:ogham_stone'), 'Properties': (10, {'rune': (8, str(r))})} for r in rune]
root = {'size': (9, (3, [9, 5, 9])), 'palette': (9, (10, palette)), 'blocks': (9, (10, blocks)), 'entities': (9, (10, [])), 'DataVersion': (3, 4556)}
def w(path, data, binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb' if binary else 'w').write(data if binary else json.dumps(data, indent=1))
w(D + '/structure/planet_altar.nbt', nbt(root), True)
w(D + '/worldgen/template_pool/planet_altar.json', {'fallback': 'minecraft:empty', 'elements': [{'weight': 1, 'element': {'element_type': 'minecraft:single_pool_element', 'location': 'diaithirbosses:planet_altar', 'processors': 'minecraft:empty', 'projection': 'rigid'}}]})
n = 0
for r in csv.DictReader(open(sys.argv[1]), delimiter='\t'):
    p = r['planet_id']
    if r['dimension'] == 'minecraft:overworld': continue
    w(f'{D}/worldgen/structure/planet_altar/{p}.json', {'type': 'minecraft:jigsaw', 'biomes': f'#diaithir_planets:{p}', 'step': 'surface_structures', 'spawn_overrides': {}, 'terrain_adaptation': 'beard_thin', 'start_pool': 'diaithirbosses:planet_altar', 'size': 1, 'start_height': {'absolute': 0}, 'project_start_to_heightmap': 'WORLD_SURFACE_WG', 'max_distance_from_center': 80, 'use_expansion_hack': False})
    w(f'{D}/worldgen/structure_set/planet_altar/{p}.json', {'structures': [{'structure': f'diaithirbosses:planet_altar/{p}', 'weight': 1}], 'placement': {'type': 'minecraft:random_spread', 'spacing': 24, 'separation': 10, 'salt': 770000 + n}})
    n += 1
print(n, 'planets')
