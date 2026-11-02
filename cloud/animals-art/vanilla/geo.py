"""GeckoLib creatures (Occultism spirits, Neovitae daemons): convert.py geo layers, each painted on its own same-named skin.

    python3 geo.py BLENDER_PYTHON GEO_LAYERS_JSON TEX_ROOT OUT [--list]
"""
import json, sys
from pathlib import Path
from auto import PARTS
from vanilla import run

BODY = [('daemonium', 'hide'), ('afrit', 'hide'), ('marid', 'hide'), ('devil', 'hide'),
        ('djinni', 'skin|cloth'), ('foliot', 'skin|cloth'), ('demonic', 'skin|cloth'), ('trader', 'skin|cloth')]


def table(layers_json, tex_root):
    out = {}
    for key in json.load(open(layers_json)):
        ns, name = key.split(':')
        body = next((m for w, m in BODY if w in name), None)
        rel = f'assets/{ns}/textures/entity/{name}'
        if body is None or not (Path(tex_root) / f'{rel}.png').exists():
            continue
        rules = PARTS + ([(r'(^|/)head', 'skin')] if '|' in body else []) + [(r'.', body)]
        out[f'{ns}_{name}'] = (key, [rel], '-', rules, False)
    return out


if __name__ == '__main__':
    blender, layers_json, tex, outdir = sys.argv[1:5]
    t = table(layers_json, tex)
    if '--list' in sys.argv:
        for k, v in t.items():
            print(k, v[1], v[3][-1][1])
        sys.exit()
    run(t, blender, layers_json, tex, outdir, list(t))
