"""Turn other model formats into the same posed-polygon layers ExportLayers.java writes, so vanilla.py paints them.

    python3 convert.py OUT.json geo NAME FILE.geo.json [...]      GeckoLib / Bedrock geometry
    python3 convert.py OUT.json tabula NAME FILE.tbl [...]        Tabula (Wyrmlore dragons, sea serpents)
    python3 convert.py OUT.json uwjava NAME FILE.java [...]       AdvancedModelBox code (Untamed Wilds, Uranus/Wyrmlore)
Space and UVs follow Minecraft's ModelPart.Cube exactly: y down, model faces -Z, vertices in blocks (1/16).
"""
import json, math, re, sys, zipfile
import numpy as np


def rot(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    X = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]); Y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]); Z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Z @ Y @ X


def pose(pivot, r):
    m = np.eye(4); m[:3, :3] = rot(*r); m[:3, 3] = np.array(pivot) / 16
    return m


def box_faces(mat, part, cube, x, y, z, w, h, d, g, mirror, u, v, tw, th, faces_uv=None):
    """ModelPart.Cube: 6 polygons, legacy box UV (or per-face rects {dir: (u0, v0, u1, v1)})."""
    x0, y0, z0, x1, y1, z1 = x - g, y - g, z - g, x + w + g, y + h + g, z + d + g
    if mirror:
        x0, x1 = x1, x0
    t0, t1, t2, t3 = (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)
    l0, l1, l2, l3 = (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
    U0, U1, U2, U22, U3, U4 = u, u + d, u + d + w, u + d + w + w, u + d + w + d, u + d + w + d + w
    V0, V1, V2 = v, v + d, v + d + h
    quads = {'down': ([l1, l0, t0, t1], U1, V0, U2, V1), 'up': ([t2, t3, l3, l2], U2, V1, U22, V0),
             'west': ([t0, l0, l3, t3], U0, V1, U1, V2), 'north': ([t1, t0, t3, t2], U1, V1, U2, V2),
             'east': ([l1, t1, t2, l2], U2, V1, U3, V2), 'south': ([l0, l1, l2, l3], U3, V1, U4, V2)}
    out = []
    for k, (vs, a, b, c, e) in quads.items():
        if faces_uv is not None:
            if k not in faces_uv:
                continue
            a, b, c, e = faces_uv[k]
        uv = [(c, b), (a, b), (a, e), (c, e)]
        if mirror:
            vs = vs[::-1]; uv = uv[::-1]
        P = [(mat @ np.array([p[0] / 16, p[1] / 16, p[2] / 16, 1]))[:3] for p in vs]
        out.append(dict(part=part, cube=cube, box=[w, h, d], v=[[*map(float, p), float(t[0]), float(t[1])] for p, t in zip(P, uv)]))
    return out


def geo(path):
    """GeckoLib: pivot x and origin x negated, x/y rotations negated (as GeckoLib's BakedModelFactory), then y-up -> y-down."""
    g = json.load(open(path))['minecraft:geometry'][0]
    desc = g['description']; tw, th = desc['texture_width'], desc['texture_height']
    bones = {b['name']: b for b in g.get('bones', [])}
    flip = np.diag([-1.0, -1.0, 1.0, 1.0])     # GeckoLib y-up space -> model space (180 degrees about Z)
    faces = []

    def bone_mat(b):
        m = np.eye(4) if not b.get('parent') else bone_mat(bones[b['parent']])
        px, py, pz = b.get('pivot', [0, 0, 0]); rx, ry, rz = b.get('rotation', [0, 0, 0])
        P = np.array([-px, py, pz]) / 16
        t = np.eye(4); t[:3, 3] = P; ti = np.eye(4); ti[:3, 3] = -P
        r = np.eye(4); r[:3, :3] = rot(math.radians(-rx), math.radians(-ry), math.radians(rz))
        return m @ t @ r @ ti

    for name, b in bones.items():
        M = bone_mat(b)
        for i, c in enumerate(b.get('cubes', [])):
            (ox, oy, oz), (sx, sy, sz) = c['origin'], c['size']
            m = M
            if 'rotation' in c:
                px, py, pz = c.get('pivot', [0, 0, 0]); rx, ry, rz = c['rotation']
                P = np.array([-px, py, pz]) / 16
                t = np.eye(4); t[:3, 3] = P; ti = np.eye(4); ti[:3, 3] = -P
                r = np.eye(4); r[:3, :3] = rot(math.radians(-rx), math.radians(-ry), math.radians(rz))
                m = M @ t @ r @ ti
            uv = c.get('uv', [0, 0]); fuv = None
            if isinstance(uv, dict):
                fuv = {k: (f['uv'][0], f['uv'][1], f['uv'][0] + f.get('uv_size', [0, 0])[0], f['uv'][1] + f.get('uv_size', [0, 0])[1]) for k, f in uv.items()}
                uv = [0, 0]
            # y-up cube in GeckoLib space; build it y-down by flipping, so the box unwrap matches the game's
            for f in box_faces(flip @ m @ flip, '/' + name, i, ox, -(oy + sy), oz, sx, sy, sz, c.get('inflate', 0), c.get('mirror', b.get('mirror', False)), uv[0], uv[1], tw, th, fuv):
                faces.append(f)
    return dict(tw=tw, th=th, faces=faces)


def tree(parts, roots, tw, th):
    faces = []

    def walk(n, parent, path):
        p = parts[n]; m = parent @ pose(p['pivot'], p['rot'])
        for i, b in enumerate(p['boxes']):
            x, y, z, w, h, d = b[:6]; g = b[6] if len(b) > 6 else 0
            faces.extend(box_faces(m, path + '/' + n, i, x, y, z, w, h, d, g, p['mirror'], p['uv'][0], p['uv'][1], tw, th))
        for c in p['children']:
            walk(c, m, path + '/' + n)
    for r in roots:
        walk(r, np.eye(4), '')
    return dict(tw=tw, th=th, faces=faces)


def tabula(path):
    with zipfile.ZipFile(path) as z:
        t = json.loads(z.read('model.json'))
    parts, roots = {}, []

    def add(c, parent):
        n = c['name']
        while n in parts:
            n += '_'
        parts[n] = dict(pivot=c['position'], rot=[math.radians(a) for a in c['rotation']], boxes=[[*c['offset'], *c['dimensions'], c.get('mcScale', 0)]],
                        mirror=c.get('txMirror', False), uv=c['txOffset'], children=[])
        (parts[parent]['children'] if parent else roots).append(n)
        for k in c.get('children', []):
            add(k, n)
    for c in t['cubes']:
        add(c, None)
    return tree(parts, roots, t['textureWidth'], t['textureHeight'])


def fnum(x):
    """A literal from Java code; a variable (such as a model scale passed in) counts as 0."""
    try:
        return float(x.strip().rstrip('Ff'))
    except ValueError:
        return 0.0


def uwjava(path):
    num = r'(-?[\d.]+)F?'
    t = open(path).read()
    tw = int(re.search(r'texWidth = (\d+)', t).group(1)); th = int(re.search(r'texHeight = (\d+)', t).group(1))
    parts = {}
    for m in re.finditer(r'this\.(\w+) = new \w*Model(?:Box|Renderer)\w*\(this, (-?\d+), (-?\d+)\)', t):
        parts[m[1]] = dict(uv=[int(m[2]), int(m[3])], pivot=[0, 0, 0], rot=[0, 0, 0], boxes=[], mirror=False, children=[])
    for m in re.finditer(r'this\.(\w+)\.mirror = true', t):
        if m[1] in parts:
            parts[m[1]]['mirror'] = True
    for m in re.finditer(r'this\.(\w+)\.(?:setRotationPoint|setPos)\(' + ', '.join([num] * 3) + r'\)', t):
        if m[1] in parts:
            parts[m[1]]['pivot'] = [float(m[i]) for i in (2, 3, 4)]
    for m in re.finditer(r'this\.(\w+)\.addBox\(([^)]*)\)', t):
        if m[1] in parts:
            parts[m[1]]['boxes'].append([fnum(x) for x in m[2].split(',')][:7])
    for m in re.finditer(r'setRotateAngle\((?:this\.)?(\w+), ' + ', '.join([num] * 3) + r'\)', t):
        if m[1] in parts:
            parts[m[1]]['rot'] = [float(m[i]) for i in (2, 3, 4)]
    for m in re.finditer(r'this\.(\w+)\.rotateAngle([XYZ]) = ' + num, t):
        if m[1] in parts:
            parts[m[1]]['rot']['XYZ'.index(m[2])] = float(m[3])
    for m in re.finditer(r'this\.(\w+)\.addChild\(this\.(\w+)\)', t):
        if m[1] in parts and m[2] in parts:
            parts[m[1]]['children'].append(m[2])
    roots = [p for p in parts if not any(p in q['children'] for q in parts.values())]
    return tree(parts, roots, tw, th)


if __name__ == '__main__':
    out, kind, *rest = sys.argv[1:]
    try:
        data = json.load(open(out))
    except FileNotFoundError:
        data = {}
    for name, path in zip(rest[::2], rest[1::2]):
        try:
            data[name] = {'geo': geo, 'tabula': tabula, 'uwjava': uwjava}[kind](path)
            print(name, len(data[name]['faces']))
        except Exception as e:
            print(name, 'skipped:', e)
    json.dump(data, open(out, 'w'))
