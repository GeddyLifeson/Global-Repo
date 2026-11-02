import base64, json, sys, os
sys.path.insert(0, '/tmp/claude-0/bm2')
from pal import PAL
B2 = '/tmp/claude-0/bm2/'; B3 = '/tmp/claude-0/bm3/'
def b64(p): return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
slices = json.load(open(B2 + 'slices2.json')); pkd = json.load(open(B3 + 'pk.json'))
imgs = {}
for k, st in slices.items():
    d = {'c': b64(B2 + f's{k}.png')}
    for x in ('lu', 'cr', 'ur', 'rb', 'fb'):
        p = B2 + f's{k}_{x}.png'
        if os.path.exists(p): d[x] = b64(p)
    if k in pkd['pk']: d['pk'] = 'data:image/png;base64,' + pkd['pk'][k]
    elif k.startswith('y'): d['pkref'] = '0'
    d.update(st); imgs[k] = d
data = {'imgs': imgs, 'depth': b64(B2 + 'depth.png'), 'pal': {str(k): v for k, v in PAL.items()}, 'vocab': pkd['vocab'], 'dom': pkd['dom']}
html = open(B3 + 'template3.html').read().replace('/*DATA*/', 'const DATA=' + json.dumps(data, separators=(',', ':')) + ';')
open(B3 + 'biomes_by_age.html', 'w').write(html); print(len(html))
