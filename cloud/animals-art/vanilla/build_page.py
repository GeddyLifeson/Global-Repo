"""Preview page for a batch of vanilla mobs: python3 build_page.py LAYERS_JSON VANILLA_TEX PAINTED_DIR OUT.html TITLE GROUP mob ..."""
import base64, json, sys
from pathlib import Path
from vanilla import MOBS
layers_json, tex, painted, dest, title, group, *mobs = sys.argv[1:]
if mobs and mobs[0].startswith('--table='):   # another creature table, e.g. --table=wyrm (preview subset)
    import importlib
    mod = importlib.import_module(mobs.pop(0)[8:])
    MOBS = mod.preview(tex)
L = json.load(open(layers_json))
b64 = lambda p: 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
nice = lambda t: t.split('/')[-1].replace('_', ' ').capitalize()
def lay(t):
    k = t.partition('@')[2]
    return [dict(part=f['part'], v=[[round(x, 5) for x in v] for v in f['v']]) for f in L[k]['faces']] if k else None


out = []
for mob in mobs:
    key, textures, hide, rules, hooves = MOBS[mob]
    m = L[key]
    faces = [dict(part=f['part'], v=[[round(x, 5) for x in v] for v in f['v']]) for f in m['faces']]
    out.append(dict(plan=mob.replace('_', ' ').capitalize(), group=group, tw=m['tw'], th=m['th'], hide=hide, faces=faces,
                    species=[dict(name=nice(t.split('@')[0]), tex=b64(f"{painted}/{t.split('@')[0]}.png"), old=b64(f"{tex}/{t.split('@')[0]}.png"), faces=lay(t)) for t in textures]))
    if mob == 'sheep':  # the wool coat is its own layer over the body
        k2, t2 = MOBS['sheep_wool'][0], MOBS['sheep_wool'][1][0]
        out[-1]['overlay'] = dict(tw=L[k2]['tw'], th=L[k2]['th'], faces=[dict(v=[[round(x, 5) for x in v] for v in f['v']]) for f in L[k2]['faces']],
                                  tex=b64(f'{painted}/{t2}.png'), old=b64(f'{tex}/{t2}.png'))
intro = ("Every vanilla animal redrawn at 64x with the method you approved for the Ice Age animals: the game's own model, "
         "rebuilt in Blender for baked shadows, then each face painted fresh (fur, wool, feathers, hide, shell, horn, hoof), "
         "lit from the upper left, with dust and mud, keeping each face's eyes and nose. Drag to turn, pick a skin, and flip to the old look to compare.")
t = open(Path(__file__).with_name('template.html')).read()
t = t.replace('__TITLE__', title).replace('__INTRO__', intro).replace('__GRID__', f'All {len(out)} {group.lower()}').replace('__DATA__', json.dumps(out, separators=(',', ':')))
open(dest, 'w').write(t)
