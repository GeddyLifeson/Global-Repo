"""Re-lay a model texture after its boxes moved or changed size: every face of the
new layout is filled from the matching face of the old layout (nearest resize).
New parts copy a named source part, or a flat colour."""
import json, sys, pathlib
from PIL import Image

def faces(p, b):
    u, v = p['uv']; w, h, d = (int(round(t)) for t in b[3:6])
    return [(u, v + d, d, h), (u + d, v + d, w, h), (u + d + w, v + d, d, h), (u + 2 * d + w, v + d, w, h), (u + d, v, w, d), (u + d + w, v, w, d)]

def rebake(old, new, img, source, colour):
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for name, p in new['parts'].items():
        src = old['parts'].get(source.get(name, name))
        for bi, b in enumerate(p['boxes']):
            for (x, y, w, h), k in zip(faces(p, b), range(6)):
                if w <= 0 or h <= 0:
                    continue
                if name in colour or not src:
                    out.paste(Image.new('RGBA', (w, h), tuple(colour[name])), (x, y)); continue
                sx, sy, sw, sh = faces(src, src['boxes'][min(bi, len(src['boxes']) - 1)])[k]
                if sw <= 0 or sh <= 0:
                    continue
                out.paste(img.crop((sx, sy, sx + sw, sy + sh)).resize((w, h), Image.NEAREST), (x, y))
    return out

if __name__ == '__main__':
    old, new = (json.load(open(f))[sys.argv[3]] for f in sys.argv[1:3])
    source = {'body_hips': 'body_main', 'tail_tip': 'tail'}
    colour = {f'claw_{s}_{i}': [58, 48, 40, 255] for s in ('left', 'right') for i in (1, 2, 3)}
    for png in sys.argv[5:]:
        rebake(old, new, Image.open(png).convert('RGBA'), source, colour).save(pathlib.Path(sys.argv[4]) / pathlib.Path(png).name)
