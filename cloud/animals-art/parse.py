"""Parse Untamed Wilds code-built models into JSON for a three.js viewer."""
import json, re, sys, base64, pathlib

src = pathlib.Path(sys.argv[1])
num = r'(-?[\d.]+)F?'
out = {}
for name in sys.argv[2:]:
    t = (src / f'Model{name}.java').read_text()
    tw = int(re.search(r'texWidth = (\d+)', t).group(1))
    th = int(re.search(r'texHeight = (\d+)', t).group(1))
    parts = {}
    for m in re.finditer(r'this\.(\w+) = new AdvancedModelBox\(this, (\d+), (\d+)\)', t):
        parts[m[1]] = dict(uv=[int(m[2]), int(m[3])], pivot=[0, 0, 0], rot=[0, 0, 0], boxes=[], mirror=False, children=[], sets=None)
    for m in re.finditer(r'this\.(\w+)\.mirror = true', t):
        parts[m[1]]['mirror'] = True
    for m in re.finditer(r'this\.(\w+)\.setRotationPoint\(' + ', '.join([num] * 3) + r'\)', t):
        parts[m[1]]['pivot'] = [float(m[i]) for i in (2, 3, 4)]
    for m in re.finditer(r'this\.(\w+)\.addBox\(([^)]*)\)', t):
        parts[m[1]]['boxes'].append([float(x.strip().rstrip('F')) for x in m[2].split(',')][:7])
    for m in re.finditer(r'setRotateAngle\((\w+), ' + ', '.join([num] * 3) + r'\)', t):
        parts[m[1]]['rot'] = [float(m[i]) for i in (2, 3, 4)]
    for m in re.finditer(r'this\.(\w+)\.addChild\(this\.(\w+)\)', t):
        parts[m[1]]['children'].append(m[2])
    sets = {m[1]: [int(x) for x in m[2].split(',')] for m in re.finditer(r'int\[\] (SET_\d+) = \{([^}]*)\}', t)}
    for m in re.finditer(r'this\.(\w+)\.showModel = in\((SET_\d+), mob\.getVariant\(\)\)', t):
        parts[m[1]]['sets'] = sets[m[2]]
    roots = [p for p in parts if not any(p in q['children'] for q in parts.values())]
    out[name] = dict(tw=tw, th=th, parts=parts, roots=roots)
json.dump(out, sys.stdout)
