"""16x sources (final UV layout) -> shared Factorio style -> realistic eyes -> 32x textures."""
import json, sys, pathlib, importlib.util
from PIL import Image
from eyes import paint_eyes
spec = importlib.util.spec_from_file_location('factorio_style', sys.argv[1]); ps = importlib.util.module_from_spec(spec); spec.loader.exec_module(ps)
OUT = pathlib.Path(sys.argv[2])
ids = {'Elephantid':'elephantid','Cervid':'cervid','Equid':'equid','Bovid':'bovid','Canid':'canid','GroundSloth':'ground_sloth','Glyptodont':'glyptodont'}
models = json.load(open('models.json'))
for k, i in ids.items():
    m = models[k]; faces = []
    for p in m['parts'].values():
        u, v = p['uv']
        for b in p['boxes']:
            w, h, d = (int(round(t)) for t in b[3:6])
            faces += [[u, v + d, d, h], [u + d, v + d, w, h], [u + d + w, v + d, d, h], [u + 2 * d + w, v + d, w, h], [u + d, v, w, d], [u + d + w, v, w, d]]
    faces = [f for f in faces if f[2] > 0 and f[3] > 0]
    (OUT / i).mkdir(parents=True, exist_ok=True)
    for png in sorted(pathlib.Path('src16', i).glob('*.png')):
        img = ps.style(Image.open(png).convert('RGBA'), faces=faces, material='natural')
        s = img.width // m['tw']
        assert img.size == (m['tw'] * s, m['th'] * s), img.size
        paint_eyes(img, m, scale=s, look='real').save(OUT / i / png.name)
