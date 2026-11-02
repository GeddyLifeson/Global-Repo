"""8 drink crops x 4 growth stages (+seeds) and 12 drink-ingredient/instrument items for the Diaithir kit."""
import json, io, contextlib, math
import sys; sys.path.insert(0, '/home/user/work/cookware')
with contextlib.redirect_stdout(io.StringIO()):
    import make_cw as m
box, cyl = m.box, m.cyl
M = dict(m.M)
def F(n, rgb, r=0.7): M[n] = {'type': 'flat', 'rgb': rgb, 'rough': r}
for n, c in dict(g1=[70, 130, 56], g2=[96, 156, 66], g3=[52, 100, 48], gry=[130, 150, 110], gry2=[170, 184, 150], blue=[60, 80, 190], yel=[232, 196, 60], gold=[220, 170, 50],
                 purple=[130, 70, 170], red=[190, 40, 36], white=[236, 232, 220], dark=[44, 32, 28], root=[196, 150, 90], rootd=[160, 110, 62], bark=[150, 90, 54], barkd=[104, 64, 40],
                 lic=[60, 42, 30], lic2=[110, 80, 50], pale=[222, 214, 160], seed=[170, 130, 70], seedd=[90, 62, 40], mold=[240, 238, 226], green_br=[108, 120, 50], soil=[100, 70, 48]).items(): F(n, c)
def leaf(mat, x, y, ln, wd, ang, z=8.0): return box(mat, [x - wd / 2, y, z - 0.25], [x + wd / 2, y + ln, z + 0.25], 0.15, rot=[0, 0, ang], pivot=[x, y, z]) if False else box(mat, [x - wd / 2, y, z - 0.4], [x + wd / 2, y + ln, z + 0.4], 0.3, rot=[0, 0, ang])
def stem(mat, x, y0, y1, r=0.45): return cyl(mat, [x, y0, 8], [x, y1, 8], r, 0.05)
def plant(kind, s):
    p = []
    h = [3, 6, 10, 14][s]; k = s / 3
    if kind == 'gentian':  # rosette of broad leaves, tall stem with blue trumpets
        p += [stem('g1', 8, 0, h)] + [leaf('g2', 8 + d * 1.5, 0, 3 + 3 * k, 2.4, d * 55) for d in (-1, 1)]
        if s >= 2: p += [leaf('g1', 8 + d * 2.5, h * .45, 3.2, 2.2, d * 70) for d in (-1, 1)]
        if s == 3: p += [cyl('blue', [8, h - 1, 8], [8, h + 1, 8], 1.5, 0.4), cyl('blue', [5.8, h - 4, 8], [5.8, h - 2.4, 8], 1.2, 0.4), cyl('blue', [10.2, h - 6, 8], [10.2, h - 4.4, 8], 1.2, 0.4)]
    elif kind == 'wormwood':  # grey-green feathery sprays
        p += [stem('gry', 8, 0, h)] + [leaf('gry2', 8 + d * (1 + k * 1.4), 1 + i * 2.6 * max(k, .35), 2 + 3 * k, 1.1, d * 38) for i in range(1 + s) for d in (-1, 1)]
        if s == 3: p += [cyl('yel', [8, h, 8], [8, h + 1.0, 8], 0.6, 0.2), cyl('yel', [6.4, h - 3, 8], [6.4, h - 2, 8], 0.5, 0.2)]
    elif kind == 'angelica':  # tall umbel
        p += [stem('g2', 8, 0, h, 0.7)] + [leaf('g1', 8 + d * 3, 0.5 + s, 2.6 + 2 * k, 2.6, d * 60) for d in (-1, 1)]
        if s == 3: p += [cyl('pale', [8, h - 1, 8], [8, h + 0.6, 8], 3.4, 0.6)] + [cyl('pale', [8 + dx, h - 1.2, 8], [8 + dx, h - 0.2, 8], 1.0, 0.3) for dx in (-3.6, 3.6)]
        elif s == 2: p += [cyl('g3', [8, h, 8], [8, h + 1, 8], 1.2, 0.4)]
    elif kind == 'cassia':  # young cinnamon-like bush, glossy pointed leaves
        p += [stem('bark', 8, 0, h, 0.6)] + [leaf('g3', 8 + d * (1.2 + 1.6 * k), 1 + (i * 2.8), 3 + 1.4 * k, 1.8, d * 45) for i in range(s + 1) for d in (-1, 1)]
        if s == 3: p += [cyl('red', [8, h, 8], [8, h + 1, 8], 0.9, 0.3)]
    elif kind == 'cinchona':  # small tree: trunk and leaf canopy
        p += [stem('bark', 8, 0, h, 0.5 + 0.35 * s)] + [leaf('g1', 8 + d * (1.5 + 1.8 * k), h * .6 + (i * 1.6), 3 + 1.5 * k, 2.2, d * (50 + i * 8)) for i in range(1 + s) for d in (-1, 1)]
        if s == 3: p += [cyl('g2', [8, h - 3.5, 8], [8, h - 0.5, 8], 4.4, 1.4), cyl('red', [5, h - 2, 8], [5, h - 1, 8], 0.9, 0.3), cyl('red', [11, h - 1.5, 8], [11, h - 0.5, 8], 0.9, 0.3)]
    elif kind == 'licorice':  # bushy pinnate leaves with pale-purple flower spike
        p += [stem('g3', 8, 0, h)] + [leaf('g2', 8 + d * (0.8 + 0.5 * i), 1 + i * 2.2, 2 + k, 1.6, d * 50) for i in range(1 + s) for d in (-1, 1)]
        if s == 3: p += [cyl('purple', [8, h, 8], [8, h + 1.8, 8], 0.9, 0.3)]
    elif kind == 'millet':  # grass with drooping seed head
        p += [leaf('g2', 8 + d * (0.6 + k * 1.5), 0, 3 + 7 * k, 1.0, d * (12 + 18 * k)) for d in (-1, 0, 1)] + [stem('g2', 8, 0, h * .9, 0.35)]
        if s == 3: p += [cyl('gold', [8.6, h * .9 - 1, 8], [8.6, h + 1.0, 8], 1.1, 0.5), cyl('gold', [9.4, h - 3, 8], [9.4, h - 1, 8], 0.9, 0.4)]
        elif s == 2: p += [cyl('g1', [8, h * .9, 8], [8, h, 8], 0.8, 0.3)]
    else:  # saffron crocus
        p += [leaf('g1', 8 + d * (0.5 + k), 0, 4 + 6 * k, 0.8, d * (6 + 16 * k)) for d in (-1, 0, 1)]
        if s >= 2: p += [cyl('purple', [8, 0, 8], [8, 3 + 2 * (s - 2), 8], 1.7 if s == 3 else 0.9, 0.5)]
        if s == 3: p += [cyl('red', [8, 5, 8], [8, 6.4, 8], 0.4, 0.1)]
    return p
specs = []
M['soilbed'] = M['soil']
for kind in ('gentian', 'wormwood', 'angelica', 'cassia', 'cinchona', 'licorice', 'millet', 'saffron'):
    for s in range(4):
        specs.append({'name': 'block/%s_stage%d' % (kind, s), 'parts': plant(kind, s), 'views': ['south'], 'materials': M})
    # seeds: small heap of seeds with a few husks
    mat = 'seed' if kind not in ('millet',) else 'gold'
    seeds = [box(mat, [3 + (i * 2.3) % 8, 4.6 + (i % 3) * 0.3, 4 + (i * 1.7) % 7], [4.7 + (i * 2.3) % 8, 6.2 + (i % 3) * 0.3, 5.5 + (i * 1.7) % 7], 0.3, rot=[0, i * 30, 0]) for i in range(9)]
    seeds += [box('seedd', [5 + (i * 1.9) % 5, 6, 5 + (i * 2.7) % 5], [6.5 + (i * 1.9) % 5, 7.2, 6.2 + (i * 2.7) % 5], 0.25, rot=[0, i * 50, 0]) for i in range(5)]
    specs.append({'name': 'item/%s_seeds' % kind, 'parts': seeds, 'views': ['icon'], 'zoom': 0.62, 'tilt': 38, 'materials': M})
def I(n, parts, tilt=35, zoom=0.6): specs.append({'name': 'item/' + n, 'parts': parts, 'views': ['icon'], 'zoom': zoom, 'tilt': tilt, 'materials': M})
I('gentian_root', [cyl('rootd', [8, 4, 8], [8, 9, 8], 1.8, 0.7), box('root', [3, 5, 6.5], [13, 6.6, 8.5], 0.6, rot=[0, 0, 12]), box('root', [4, 7.4, 7], [12.5, 8.8, 8.8], 0.6, rot=[0, 0, -10]), box('rootd', [3, 4, 8.5], [11, 5.2, 9.8], 0.5, rot=[0, 0, -18]), cyl('blue', [8, 9, 8], [8, 10.4, 8], 1.4, 0.4), cyl('g1', [9.8, 9, 8], [9.8, 10, 8], 0.8, 0.2)])
I('wormwood', [stem('gry', 8, 3, 12, 0.5)] + [leaf('gry2', 8 + d * 1.6, 3.2 + i * 1.8, 3.4, 1.4, d * 38) for i in range(4) for d in (-1, 1)] + [box('rootd', [6.5, 3.6, 7], [9.5, 4.6, 9], 0.2), cyl('yel', [8, 12, 8], [8, 13, 8], 0.6, 0.2)])
I('angelica_root', [cyl('root', [7, 4, 8], [7, 11, 8], 2.4, 1.0), box('rootd', [3, 5, 7.2], [6, 6.2, 8.6], 0.4, rot=[0, 0, 40]), box('rootd', [9, 6, 7.2], [13, 7.2, 8.6], 0.4, rot=[0, 0, -30]), cyl('rootd', [10, 4, 8], [10, 8.4, 8], 1.2, 0.5), cyl('g2', [7, 11, 8], [7, 12.4, 8], 0.9, 0.3)])
I('cassia_bark', [cyl('bark', [4, 7, 8], [12, 7, 8], 1.8, 0.8) if False else box('bark', [3, 6, 6.4], [13, 8.4, 9.2], 1.0, rot=[0, 0, 8]), box('barkd', [3, 8.2, 6.8], [13, 9.6, 8.8], 0.9, rot=[0, 0, 8]), box('bark', [4, 4.6, 6.8], [12, 6.2, 9], 0.8, rot=[0, 0, 8]), box('barkd', [11.6, 6.4, 7], [13.4, 8.2, 8.6], 0.4, rot=[0, 0, 8])])
I('cinchona_bark', [box('barkd', [3, 5, 5], [11, 6.6, 10], 0.4, rot=[0, 14, 0]), box('bark', [5, 6.6, 6], [13, 8, 11], 0.4, rot=[0, -16, 0]), box('red', [6, 8, 7.4], [10, 8.5, 9], 0.2, rot=[0, -16, 0]), box('barkd', [4, 8, 4.6], [9, 9, 8], 0.4, rot=[0, 30, 0])])
I('licorice_root', [box('lic', [3, 6, 5.5], [13, 7.4, 7.3], 0.6, rot=[0, 8, 4]), box('lic2', [3.4, 7.6, 7], [12.6, 8.8, 8.7], 0.6, rot=[0, -6, -3]), box('lic', [4, 4.6, 8], [12, 5.8, 9.6], 0.6, rot=[0, 4, 6]), box('pale', [2.6, 6.2, 5.6], [3.6, 7.2, 7.2], 0.3), box('pale', [12.4, 7.8, 7.2], [13.4, 8.8, 8.6], 0.3)])
I('millet', [stem('g2', 6, 3, 10, 0.4), stem('g2', 9, 3, 11, 0.4), cyl('gold', [6, 8, 8], [6.8, 13, 8], 1.4, 0.7), cyl('gold', [9, 9, 8], [9.9, 14, 8], 1.5, 0.7), cyl('gold', [11.6, 7, 8], [11.8, 11.4, 8], 1.2, 0.6), box('seedd', [4, 3, 7.4], [12, 3.8, 9], 0.2)])
I('saffron', [box('pale', [4, 4, 6], [12, 5, 10], 0.5), cyl('purple', [6, 5, 8], [6, 9, 8], 1.6, 0.6), cyl('purple', [10, 5, 8], [10, 8.4, 8], 1.4, 0.6)] + [box('red', [6.6 + i * 0.8, 9, 7.6], [7.0 + i * 0.8, 11.4 + (i % 2), 8.0], 0.05, rot=[0, 0, (i - 1) * 14]) for i in range(3)] + [box('red', [9.8 + i * 0.8, 8.4, 7.6], [10.2 + i * 0.8, 10.6, 8.0], 0.05, rot=[0, 0, (i - 1) * 14]) for i in range(2)])
I('koji', [cyl('clay', [8, 4, 8], [8, 7.6, 8], 5.2, 1.2), cyl('mold', [8, 7.2, 8], [8, 8.6, 8], 4.4, 1.0), box('white', [5.6, 8.4, 6], [7.2, 9.2, 7.6], 0.4), box('white', [8.4, 8.4, 8], [10, 9.1, 9.5], 0.4), box('pale', [7.2, 8.4, 9], [8.6, 9, 10], 0.3), cyl('mold', [8, 8.2, 8], [8, 8.9, 8], 3.6, 0.5)], 38)
I('hydrometer', [cyl('glass', [8, 3, 8], [8, 14, 8], 0.9, 0.3), cyl('red', [8, 3.4, 8], [8, 5.4, 8], 1.5, 0.5), cyl('dark', [8, 3, 8], [8, 3.5, 8], 1.7, 0.2)] + [box('dark', [9, 7 + i * 1.3, 7.2], [10.6, 7.3 + i * 1.3, 8.8], 0.02) for i in range(4)] + [cyl('white', [8, 9, 8], [8, 13, 8], 0.55, 0.1)], 28)
I('thermometer', [cyl('glass', [8, 4, 8], [8, 14, 8], 0.9, 0.3), cyl('red', [8, 4, 8], [8, 9, 8], 0.5, 0.1), cyl('red', [8, 3.4, 8], [8, 5, 8], 1.7, 0.6), box('woodd', [9.4, 5, 7.2], [11.2, 14, 8.8], 0.3)] + [box('dark', [10.8, 6 + i * 1.5, 7.0], [12.2, 6.3 + i * 1.5, 9.0], 0.02) for i in range(5)], 28)
I('off_brew', [cyl('glass', [8, 3, 8], [8, 8.6, 8], 4.4, 1.6), cyl('glass', [8, 8.6, 8], [8, 12, 8], 1.5, 0.5), cyl('green_br', [8, 3.4, 8], [8, 7.6, 8], 4.0, 1.4), cyl('cork', [8, 12, 8], [8, 13.4, 8], 1.7, 0.4) if 'cork' in M else cyl('woodd', [8, 12, 8], [8, 13.4, 8], 1.7, 0.4), cyl('g1', [6, 7.4, 8], [6, 8.6, 8], 0.9, 0.5), cyl('g1', [10, 6.6, 8], [10, 8, 8], 0.7, 0.5), cyl('g2', [8.2, 7.6, 6], [8.2, 8.5, 6], 0.7, 0.4)], 30)
json.dump(specs, open('/home/user/work/crops/specs.json', 'w')); print(len(specs))
