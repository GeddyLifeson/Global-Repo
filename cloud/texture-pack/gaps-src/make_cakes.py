"""Placed-cake block textures (top, side, bottom, cut inner) for the 15 cake dishes, in the vanilla cake layout, rendered through the kit."""
import json, io, contextlib, sys
sys.path.insert(0, '/home/user/work/cookware')
with contextlib.redirect_stdout(io.StringIO()):
    import make_cw as m
b, c = m.box, m.cyl
# name: sponge, filling, frosting, layers, topping, topcolour, rim
CAKES = {
 'malva_pudding': ((176, 98, 44), (214, 150, 70), (200, 120, 40), 2, 'glaze', (226, 150, 40)),
 'tres_leches_cake': ((242, 222, 170), (250, 244, 228), (252, 248, 238), 2, 'cherry', (190, 30, 40)),
 'black_cake_caribbean': ((48, 28, 22), (70, 40, 30), (240, 232, 214), 3, 'cherry', (150, 20, 30)),
 'sachertorte': ((92, 52, 34), (190, 90, 40), (58, 32, 24), 2, 'disc', (240, 232, 214)),
 'black_forest_cake': ((72, 42, 30), (250, 244, 232), (250, 244, 232), 3, 'cherry', (160, 16, 36)),
 'plum_pudding': ((54, 32, 26), (74, 42, 30), (250, 246, 238), 1, 'holly', (190, 30, 30)),
 'plantation_rum_cake': ((214, 150, 64), (230, 180, 96), (232, 160, 40), 1, 'glaze', (240, 190, 70)),
 'date_coffee_cake': ((150, 100, 60), (190, 140, 84), (176, 120, 64), 2, 'streusel', (200, 150, 90)),
 'low_gravity_protein_cake': ((226, 226, 214), (180, 210, 236), (170, 205, 240), 2, 'glaze', (120, 170, 230)),
 'circle_dance_honey_cakes': ((228, 170, 70), (240, 196, 100), (232, 160, 36), 1, 'glaze', (240, 180, 40)),
 'dobos_torte': ((236, 208, 150), (92, 54, 36), (176, 100, 36), 6, 'caramel', (190, 110, 30)),
 'lamington': ((240, 214, 150), (250, 244, 232), (82, 48, 32), 2, 'coconut', (252, 250, 244)),
 'pavlova': ((252, 250, 244), (252, 248, 236), (252, 250, 244), 1, 'berries', (200, 30, 50)),
 'ambrosia_honey_cake': ((232, 178, 72), (244, 206, 110), (236, 170, 40), 2, 'gold', (236, 196, 70)),
 'thunderhoney_mead_cake': ((226, 160, 52), (240, 190, 90), (210, 140, 30), 2, 'sparks', (110, 160, 240)),
}
specs = []
for n, (sp, fi, fr, L, top, tc) in CAKES.items():
    M = dict(m.M)
    def F(k, rgb, r=0.6): M[k] = {'type': 'flat', 'rgb': list(rgb), 'rough': r}
    F('sp', sp, 0.8); F('spd', tuple(int(v * .78) for v in sp), 0.8); F('fi', fi, 0.4); F('fr', fr, 0.35); F('tc', tc, 0.3); F('crumb', tuple(min(255, int(v * 1.12) + 6) for v in sp), 0.85); F('leaf', (60, 130, 56), 0.6)
    F('white', (252, 248, 238), 0.4); F('dark', (40, 24, 18), 0.5)
    h = 8.0; ly = (h - 2.2) / (L + 0.0)  # sponge layer height incl. filling
    side = []; y = 0.0
    for i in range(L):
        side += [b('sp' if i % 2 == 0 or L < 3 else 'spd', [0, y, 6], [16, y + ly * 0.78, 10], 0.15)]; y += ly * 0.78
        side += [b('fi', [0, y, 5.6], [16, y + ly * 0.22, 10.4], 0.2)]; y += ly * 0.22
    side += [b('fr', [0, 5.8, 5.5], [16, 8.0, 10.5], 0.4)]
    if top in ('glaze', 'caramel'): side += [c('fr', [x, 4.8, 8], [x, 6.2, 8], 0.9, 0.3) for x in (1.5, 4.5, 7.5, 10.5, 13.5)]
    if top == 'coconut': side += [b('white', [x, 0.5 + (x * 7) % 7, 5.4], [x + 0.9, 1.1 + (x * 7) % 7, 5.8], 0.1) for x in range(0, 15, 1)]
    topf = [b('fr', [0, 0, 0], [16, 1, 16], 0.3)]
    if top == 'cherry': topf += [c('tc', [8 + dx, 1, 8 + dz], [8 + dx, 2.8, 8 + dz], 1.6, 0.7) for dx, dz in ((-4, -4), (4, -4), (4, 4), (-4, 4), (0, 0))] + [c('white', [8 + dx, 1, 8 + dz], [8 + dx, 1.8, 8 + dz], 1.2, 0.5) for dx, dz in ((0, -5.5), (5.5, 0), (0, 5.5), (-5.5, 0))]
    elif top == 'berries': topf += [c('white', [8, 1, 8], [8, 2.4, 8], 6.5, 1.5)] + [c('tc' if i % 2 else 'leaf', [8 + 3.5 * __import__('math').cos(i), 2.2, 8 + 3.5 * __import__('math').sin(i)], [8 + 3.5 * __import__('math').cos(i), 3.6, 8 + 3.5 * __import__('math').sin(i)], 1.3, 0.6) for i in range(6)]
    elif top == 'glaze': topf += [c('tc', [8, 1, 8], [8, 1.5, 8], 6.4, 0.5)] + [b('tc', [2, 1.5, 3 + i * 3], [14, 1.9, 3.8 + i * 3], 0.2) for i in range(4)]
    elif top == 'caramel': topf += [c('tc', [8, 1, 8], [8, 1.7, 8], 7.2, 0.4)] + [b('crumb', [8, 1.7, 1], [8.8, 2.2, 15], 0.1, rot=[0, 30 * i, 0]) for i in range(3)]
    elif top == 'disc': topf += [c('white', [8, 1, 8], [8, 1.5, 8], 3.0, 0.2)] + [b('dark', [4.5, 1.5, 7.5], [11.5, 1.8, 8.5], 0.05)]
    elif top == 'holly': topf += [c('white', [8, 1, 8], [8, 2.2, 8], 5.8, 1.2)] + [b('leaf', [5.5, 2.2, 7.4], [10.5, 2.7, 8.6], 0.2, rot=[0, 30, 0]), b('leaf', [5.5, 2.2, 7.4], [10.5, 2.7, 8.6], 0.2, rot=[0, -30, 0])] + [c('tc', [8 + dx, 2.4, 8 + dz], [8 + dx, 3.6, 8 + dz], 0.9, 0.5) for dx, dz in ((0, 0), (1.4, 0.6), (-1.2, 0.9))]
    elif top == 'streusel': topf += [b('tc', [1 + (i * 3.7) % 13, 1, 1 + (i * 5.3) % 13], [2.8 + (i * 3.7) % 13, 1.9, 2.6 + (i * 5.3) % 13], 0.4) for i in range(18)]
    elif top == 'coconut': topf += [b('white', [1 + (i * 3.1) % 14, 1, 1 + (i * 4.7) % 14], [1.9 + (i * 3.1) % 14, 1.5, 1.6 + (i * 4.7) % 14], 0.15) for i in range(30)]
    elif top == 'gold': topf += [b('tc', [3 + i * 3, 1, 3 + (i % 2) * 6], [5 + i * 3, 1.3, 5 + (i % 2) * 6], 0.1, rot=[0, 20 * i, 0]) for i in range(4)] + [b('tc', [6, 1.3, 6], [10, 1.6, 10], 0.1, rot=[0, 45, 0])]
    elif top == 'sparks': topf += [c('tc', [8 + dx, 1, 8 + dz], [8 + dx, 1.4, 8 + dz], 0.9, 0.2) for dx, dz in ((-4, -3), (3, -4), (4, 3), (-3, 4), (0, 0))]
    bot = [b('spd', [0, 0, 0], [16, 1, 16], 0.4)] + [b('sp', [1 + i * 2.6, 1, 2], [2.6 + i * 2.6, 1.3, 14], 0.2) for i in range(5)]
    inner = []; y = 0.0
    for i in range(L):
        inner += [b('sp', [0, y, 0], [16, y + ly * 0.78, 4], 0.1), b('crumb', [0.8, y + 0.2, 2], [15.2, y + ly * 0.78 - 0.1, 4.4], 0.2)]; y += ly * 0.78
        inner += [b('fi', [0, y, 0], [16, y + ly * 0.22, 4.2], 0.15)]; y += ly * 0.22
    inner += [b('fr', [0, 5.8, 0], [16, 8, 4.2], 0.2)]
    for k, (parts, v) in {'side': (side, 'south'), 'top': (topf, 'up'), 'bottom': (bot, 'up'), 'inner': (inner, 'south')}.items():
        keys = ('sp', 'spd', 'fi', 'fr', 'tc', 'crumb', 'leaf', 'white', 'dark')  # kit caches materials by name, so keep them per cake
        parts = [dict(p, mat=(n + '_' + p['mat']) if p['mat'] in keys else p['mat']) for p in parts]
        MM = {(n + '_' + a if a in keys else a): bb for a, bb in M.items()}
        specs.append({'name': '%s_%s' % (n, k), 'parts': parts, 'views': [v], 'materials': MM})
json.dump(specs, open('/home/user/work/cake/cakes.json', 'w')); print(len(specs))
