import base64, json, sys
sys.path.insert(0, '/tmp/claude-0/bm')
from pal import PAL
import os
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
slices = json.load(open('slices.json'))
imgs = {}
for k in list(range(0, 16)) + ['future']:
    d = {'c': b64(f's{k}.png')}
    for x in ('lu', 'cr'):
        p = f's{k}_{x}.png'
        if os.path.exists(p): d[x] = b64(p)
    d.update(slices[str(k)])
    imgs[str(k)] = d
data = {'imgs': imgs, 'depth': b64('depth.png'),
        'pal': {str(k): v for k, v in PAL.items()}}
html = open('template.html').read().replace('/*DATA*/', 'const DATA=' + json.dumps(data, separators=(',', ':')) + ';')
open('biomes_by_age.html', 'w').write(html)
print(len(html))
