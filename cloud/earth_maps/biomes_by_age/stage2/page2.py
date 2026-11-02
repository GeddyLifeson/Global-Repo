import base64, json, sys, os
sys.path.insert(0, '/tmp/claude-0/bm2')
from pal import PAL
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
slices = json.load(open('slices2.json'))
imgs = {}
for k, st in slices.items():
    d = {'c': b64(f's{k}.png')}
    for x in ('lu', 'cr', 'ur', 'rb'):
        p = f's{k}_{x}.png'
        if os.path.exists(p): d[x] = b64(p)
    d.update(st); imgs[k] = d
data = {'imgs': imgs, 'depth': b64('depth.png'), 'pal': {str(k): v for k, v in PAL.items()}}
html = open('template2.html').read().replace('/*DATA*/', 'const DATA=' + json.dumps(data, separators=(',', ':')) + ';')
open('biomes_by_age.html', 'w').write(html); print(len(html))
