"""Preview page for the long tail (auto.py, geo.py, the Wyrmlore dread): python3 tail_page.py S_DIR OUT.html"""
import base64, json, re, sys
from pathlib import Path
import auto, geo, wyrm

S, dest = Path(sys.argv[1]), sys.argv[2]
b64 = lambda p: 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
nice = lambda t: t.split('/')[-1].replace('_', ' ').capitalize()
GROUPS = {'productivebees': 'Productive Bees', 'aquaculture': 'Aquaculture fish', 'occultism': 'Occultism spirits and familiars',
          'neovitae': 'Neovitae daemons', 'stellaris': 'Stellaris aliens', 'iceandfire': 'Wyrmlore dread'}
out = []


def add(table, layers, tex, painted, limit=None):
    L = json.load(open(layers))
    for name, (key, skins, hide, rules, hooves) in table.items():
        m = L[key]; ns = skins[0].split('/')[1] if skins[0].startswith('assets/') else 'iceandfire'
        skins = [s for s in skins if not re.search(r'blink|sleeping|_mid_|_closed_|inactive', s)][:limit]
        out.append(dict(plan=nice(skins[0]) if len(skins) == 1 else name.split('_', 1)[-1].replace('_', ' ').replace('Model', '').replace('createBodyLayer', '').strip().capitalize(),
                        group=GROUPS.get(ns, 'Other mod mobs'), tw=m['tw'], th=m['th'], hide=hide,
                        faces=[dict(part=f['part'], v=[[round(x, 5) for x in v] for v in f['v']]) for f in m['faces']],
                        species=[dict(name=nice(s), tex=b64(f'{painted}/{s}.png'), old=b64(f'{tex}/{s}.png'), faces=None) for s in skins]))


w = wyrm.table(S / 'wyrm/tex')
add({k: w[k] for k in ('dread_knight', 'dread_lich', 'dread_queen', 'dread_thrall', 'dread_ghoul')}, S / 'wyrm/layers.json', S / 'wyrm/tex', S / 'wyrm/dout', limit=4)
add(geo.table(S / 'geo/layers.json', S / 'geo'), S / 'geo/layers.json', S / 'geo', S / 'geo/out')
a = auto.table(S / 'auto/layers.json', S / 'auto/tex')
bees = {k: v for k, v in a.items() if k.startswith('productivebees')}
add({k: v for k, v in a.items() if k not in bees}, S / 'auto/layers.json', S / 'auto/tex', S / 'auto/out', limit=4)
add(bees, S / 'auto/layers.json', S / 'auto/tex', S / 'auto/out', limit=12)
out.sort(key=lambda d: list(GROUPS.values()).index(d['group']) if d['group'] in GROUPS.values() else 99)
intro = ("The rest of the creatures, painted with the same improved method: Wyrmlore's dread knights, liches, thralls, ghouls and queen, "
         "Occultism's spirits and familiars, Neovitae's daemons, Aquaculture's fish, Stellaris aliens, the villager and guard mods, and the bees "
         "(12 of the 976 bee skins shown). Drag to turn, pick a skin, and flip to the old look to compare.")
t = open(Path(__file__).with_name('template.html')).read()
t = t.replace('__TITLE__', 'Every other creature').replace('__INTRO__', intro).replace('__GRID__', f'All {len(out)} models').replace('__DATA__', json.dumps(out, separators=(',', ':')))
open(dest, 'w').write(t)
print(len(out), sum(len(d['species']) for d in out), round(len(t) / 1e6, 1), 'MB')
