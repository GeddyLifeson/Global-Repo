"""527 drink icon specs for the Diaithir kit: a 3D vessel per drink, liquid tinted by its colour, accents by category."""
import json, io, contextlib, hashlib, sys
sys.path.insert(0, '/home/user/work/cookware')
with contextlib.redirect_stdout(io.StringIO()):
    import make_cw as m
box, cyl = m.box, m.cyl
M = dict(m.M)
LAB = [[226, 214, 180], [196, 60, 50], [60, 90, 150], [230, 190, 70], [70, 120, 80], [40, 40, 44], [200, 200, 205], [150, 80, 140]]
for i, c in enumerate(LAB): M['lab%d' % i] = {'type': 'flat', 'rgb': c, 'rough': 0.6}
M['cork'] = {'type': 'wood', 'rgb': [190, 150, 100]}
M['wax_r'] = {'type': 'flat', 'rgb': [150, 30, 30], 'rough': 0.4}
M['foam'] = {'type': 'flat', 'rgb': [244, 240, 226], 'rough': 0.9}
M['stoneware'] = {'type': 'flat', 'rgb': [176, 150, 112], 'rough': 0.6}
M['stonew2'] = {'type': 'flat', 'rgb': [120, 100, 80], 'rough': 0.6}
M['leaf'] = {'type': 'flat', 'rgb': [70, 130, 60], 'rough': 0.7}
M['grain'] = {'type': 'flat', 'rgb': [212, 178, 80], 'rough': 0.7}
M['stopper'] = {'type': 'glass', 'rgb': [200, 220, 225]} if False else {'type': 'flat', 'rgb': [196, 216, 224], 'rough': 0.1}
def hx(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
def mats(c, name):
    r = hx(c)
    M['L_' + name] = {'type': 'flat', 'rgb': r, 'rough': 0.15}
    M['G_' + name] = {'type': 'flat', 'rgb': [int(v * .78) for v in r], 'rough': 0.08}
    M['W_' + name] = {'type': 'flat', 'rgb': [int(v * .6 + 40) for v in r], 'rough': 0.5}
def build(d):
    n = d['id']; h = int(hashlib.md5(n.encode()).hexdigest(), 16)
    mats(d['color'], n); L, G = 'L_' + n, 'G_' + n
    lab = 'lab%d' % (h % len(LAB)); v = d['vessel']; p = []
    wood = 'woodd' if d['aged'] else 'wood'
    if v in ('mug', 'pint'):
        r = 4.0 if v == 'mug' else 3.4; top = 12 if v == 'mug' else 13
        if v == 'mug':
            p += [cyl(wood, [8, 3, 8], [8, top, 8], r, 0.6), cyl(L, [8, top - 0.9, 8], [8, top + 0.05, 8], r - 0.7, 0.2),
                  box('iron', [8 + r - 0.3, 5, 7.2], [8 + r + 2.4, 10, 8.8], 0.6), box('iron', [8 - r - 0.2, 4.2, 7.0], [8 + r + 0.2, 4.7, 9.0], 0.1) if False else cyl('iron', [8, 5.2, 8], [8, 5.6, 8], r + 0.05, 0.1), cyl('iron', [8, 9.4, 8], [8, 9.8, 8], r + 0.05, 0.1)]
        else:
            p += [cyl(G, [8, 3, 8], [8, 7, 8], r - 0.35, 0.3), cyl(G, [8, 7, 8], [8, top, 8], r + 0.25, 0.3), cyl('glass', [8, 3, 8], [8, 3.5, 8], r - 0.2, 0.1) if False else cyl('stopper', [8, 3, 8], [8, 3.5, 8], r - 0.2, 0.1)]
        if d['hopped']: p.append(cyl('foam', [8, top - 0.3, 8], [8, top + 1.4, 8], r - (0.5 if v == 'mug' else 0.0), 0.7))
        elif h % 3 == 0: p.append(cyl('leaf', [8 + 1, top, 8], [8 + 1, top + 0.8, 8], 1.1, 0.3))
    elif v == 'wine_bottle':
        p += [cyl(G, [8, 3, 8], [8, 9.6, 8], 2.7, 0.9), cyl(G, [8, 9.6, 8], [8, 11, 8], 1.8, 0.7), cyl(G, [8, 11, 8], [8, 14, 8], 1.1, 0.3), cyl(lab, [8, 5, 8], [8, 8, 8], 2.78, 0.1), cyl('wax_r' if h % 2 else 'black', [8, 13.4, 8], [8, 14.8, 8], 1.2, 0.3)]
    elif v == 'squat_bottle':
        p += [cyl(G, [8, 3, 8], [8, 8, 8], 3.6, 1.2), cyl(G, [8, 8, 8], [8, 9.4, 8], 2.2, 0.8), cyl(G, [8, 9.4, 8], [8, 11.4, 8], 1.3, 0.3), cyl(lab, [8, 4.4, 8], [8, 7, 8], 3.65, 0.1), cyl('cork', [8, 11.2, 8], [8, 12.8, 8], 1.2, 0.3)]
    elif v == 'jug':
        p += [cyl('stoneware', [8, 3, 8], [8, 9.5, 8], 4.2, 1.6), cyl('stoneware', [8, 9.5, 8], [8, 11, 8], 2.6, 0.9), cyl('stoneware', [8, 11, 8], [8, 12.4, 8], 1.7, 0.4), cyl(L, [8, 11.4, 8], [8, 12.5, 8], 1.45, 0.2), cyl(lab, [8, 5.4, 8], [8, 8, 8], 4.28, 0.1), cyl(G, [8, 8.2, 8], [8, 8.8, 8], 4.26, 0.1), box('stoneware', [11.4, 6.5, 7.3], [13.6, 11.5, 8.7], 0.6)]
        p.append(box('cork', [7.4, 12.2, 7.4], [8.6, 13.6, 8.6], 0.3))
    elif v == 'flask':
        p += [box('steel', [4.4, 3, 6.4], [11.6, 11, 9.6], 1.0), cyl('steel', [8, 11, 8], [8, 12.4, 8], 1.5, 0.4), cyl('W_' + n, [8, 12.4, 8], [8, 13.6, 8], 1.8, 0.4), box(L, [4.8, 4.2, 9.5], [11.2, 8.6, 9.9], 0.2), box(lab, [5.6, 5, 9.8], [10.4, 7.6, 10.1], 0.1)]
    elif v == 'dram_bottle':
        p += [cyl(G, [8, 3.4, 8], [8, 9, 8], 2.4, 0.7), cyl(G, [8, 9, 8], [8, 10, 8], 1.6, 0.5), cyl(G, [8, 10, 8], [8, 12, 8], 1.0, 0.3), cyl(lab, [8, 4.6, 8], [8, 7.4, 8], 2.46, 0.1), cyl('cork', [8, 11.8, 8], [8, 13.6, 8], 1.15, 0.3)]
    else:  # decanter
        p += [cyl(G, [8, 3, 8], [8, 7.4, 8], 4.2, 1.3), cyl(G, [8, 7.4, 8], [8, 10, 8], 2.5, 0.8), cyl(G, [8, 10, 8], [8, 13, 8], 1.3, 0.4), cyl('stopper', [8, 13, 8], [8, 14.6, 8], 1.9, 0.6), cyl('stopper', [8, 14.6, 8], [8, 15.4, 8], 0.8, 0.3), cyl(lab, [8, 4.6, 8], [8, 6.4, 8], 4.3, 0.1)]
    # category accents at the base
    c = d['cat']
    if c == 'fruit': p += [cyl(L, [12.6, 3, 11], [12.6, 4.8, 11], 1.1, 0.5), cyl('leaf', [12.6, 4.8, 11], [12.6, 5.2, 11], 0.9, 0.3)]
    elif c == 'grain': p += [box('grain', [2.8 + k * 0.7, 3, 11 + (k % 2) * 0.6], [3.3 + k * 0.7, 5.6 + k * 0.4, 11.5 + (k % 2) * 0.6], 0.2) for k in range(3)]
    elif c == 'fort': p += [cyl('sun', [8, 2.9, 8], [8, 3.2, 8], 4.6, 0.1)] if False else []
    return {'name': n, 'parts': p, 'views': ['icon'], 'zoom': 0.6, 'tilt': 20, 'materials': M}
d = json.load(open('/mnt/project-files/textures/drinks/DRINK_ICON_SPEC.json'))
specs = [build(x) for x in d]
for k in range(3): json.dump(specs[k::3], open('/home/user/work/drinks/shard%d.json' % k, 'w'))
print(len(specs))
