"""Preview page for lane6.py: python3 lane6_page.py LAYERS_JSON TEX_ROOT PAINTED LIST_JSON SIBLINGS_JSON OUT.html"""
import base64, json, re, sys
from pathlib import Path
import lane6

layers_json, tex, painted, lst, sibs, dest = sys.argv[1:7]
L = json.load(open(layers_json)); t, miss = lane6.table(layers_json, tex, lst, sibs)
b64 = lambda p: 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
nice = lambda s: s.split('/')[-1].replace('_', ' ').capitalize()
out = []
for name, (key, skins, hide, rules, hooves) in t.items():
    m = L[key]; ns = skins[0].split('/')[1]
    skins = [s for s in skins if (Path(painted) / f'{s}.png').exists()]
    show = skins[:3] if ns == 'productivebees' else skins[:6]
    if not show:
        continue
    out.append(dict(plan=f'{nice(show[0])}' + (f' +{len(skins) - 1}' if len(skins) > 1 else ''), group=ns.replace('_', ' ').title(), tw=m['tw'], th=m['th'], hide=hide,
                    faces=[dict(part=f['part'], v=[[round(x, 5) for x in v] for v in f['v']]) for f in m['faces']],
                    species=[dict(name=nice(s), tex=b64(f'{painted}/{s}.png'), old=b64(f'{tex}/{s}.png'), faces=None) for s in show]))
out.sort(key=lambda d: (d['group'] != 'Minecraft', d['group']))
n = sum(len(v[1]) for v in t.values())
intro = (f"The {n} creature variants still left on the entity list, painted the approved way: baby, tame and angry skins, horse markings, "
         "villager biome and job outfits (these are overlays worn over the villager, so they look sparse on their own), coat colours, "
         "bees, Aether and Twilight Forest mobs. Each one keeps the materials of its approved parent. Drag to turn, pick a skin, flip to the old look.")
page = open(Path(__file__).with_name('template.html')).read()
page = page.replace('__TITLE__', 'Creature variants').replace('__INTRO__', intro).replace('__GRID__', f'All {len(out)} models').replace('__DATA__', json.dumps(out, separators=(',', ':')))
open(dest, 'w').write(page)
print(len(out), sum(len(d['species']) for d in out), round(len(page) / 1e6, 1), 'MB')
