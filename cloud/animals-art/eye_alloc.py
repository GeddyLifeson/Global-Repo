"""Enlarge each model's eye planes for PureBD cartoon eyes and give them free UV space."""
import json, re, sys, numpy as np
M = json.load(open('models_pre_eyes.json'))
SIZE = {'Elephantid': (4, 5), 'Cervid': (3, 3), 'Equid': (3, 3), 'Bovid': (3, 3), 'Canid': (3, 3), 'GroundSloth': (3, 3), 'Glyptodont': (2, 3)}
J = sys.argv[1]
for k, m in M.items():
    occ = np.zeros((m['th'], m['tw']), bool)
    for p in m['parts'].values():
        u, v = p['uv']
        for b in p['boxes']:
            w, h, d = (int(round(t)) for t in b[3:6]); occ[v:v + d + h, u:u + 2 * (w + d)] = True
    h, d = SIZE[k]; W, H = 2 * d + 1, d + h + 1
    x, y = next((x, y) for y in range(m['th'] - H) for x in range(m['tw'] - W) if not occ[y:y + H, x:x + W].any())
    f = f'{J}/Model{k}.java'; t = open(f).read()
    for s in ('left', 'right'):
        t, c1 = re.subn(rf'this\.eye_{s} = new AdvancedModelBox\(this, \d+, \d+\);', f'this.eye_{s} = new AdvancedModelBox(this, {x}, {y});', t)
        t, c2 = re.subn(rf'this\.eye_{s}\.addBox\(0F, -0\.5F, -1F, 0F, 1F, 2F, 0F\);', f'this.eye_{s}.addBox(0F, {-h / 2:g}F, {-d / 2:g}F, 0F, {h}F, {d}F, 0F);', t)
        assert c1 == c2 == 1, (k, s)
    open(f, 'w').write(t); print(k, (x, y), (h, d))
