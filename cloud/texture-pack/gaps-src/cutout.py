"""Download picked photos, cut the background out (rembg, cloud only), crop tight, colour-correct, 64 px with a slight sharpen.
    python3 cutout.py PICKS.json OUTDIR   (PICKS: {id: {url_thumb...}} from pick_photos.py)"""
import json, sys, os, io, time, urllib.request
os.environ.setdefault('U2NET_HOME', '/mnt/project-files/models/u2net')
os.makedirs(os.environ['U2NET_HOME'], exist_ok=True)
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from rembg import remove, new_session
UA = 'DiaithirTextures/1.0 (+https://github.com/GeddyLifeson; open-licence dish photo lookup)'
sess = new_session('isnet-general-use')
def fetch(url):
    url = url.replace('/384px-', '/640px-')
    for t in range(4):
        try: return Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40).read())).convert('RGB')
        except Exception: time.sleep(2 + 2 * t)
def process(im):
    cut = remove(im, session=sess).convert('RGBA')
    a = cut.getchannel('A'); m = a.point(lambda v: 255 if v > 40 else 0); bb = m.getbbox()
    cover = sum(m.resize((32, 32)).getdata()) / 255 / 1024.0
    if not bb or cover < 0.10 or (bb[2] - bb[0]) < 0.3 * im.width and (bb[3] - bb[1]) < 0.3 * im.height:
        # cutout lost the dish: centre square crop with a soft round mask
        s0 = int(min(im.size) * 0.86); l, t = (im.width - s0) // 2, (im.height - s0) // 2
        sq = im.crop((l, t, l + s0, t + s0)).convert('RGBA'); mk = Image.new('L', (s0, s0), 0)
        from PIL import ImageDraw; ImageDraw.Draw(mk).ellipse((0, 0, s0 - 1, s0 - 1), fill=255); mk = mk.filter(ImageFilter.GaussianBlur(s0 * 0.012)); sq.putalpha(mk)
        cut = sq; bb = (0, 0, s0, s0)
    cut = cut.crop(bb); w, h = cut.size; s = max(w, h); sq = Image.new('RGBA', (s, s), (0, 0, 0, 0)); sq.paste(cut, ((s - w) // 2, (s - h) // 2))
    pad = int(s * 0.04); big = Image.new('RGBA', (s + 2 * pad, s + 2 * pad), (0, 0, 0, 0)); big.paste(sq, (pad, pad))
    sm = big.resize((64, 64), Image.LANCZOS)
    rgb = sm.convert('RGB'); alpha = sm.getchannel('A')
    rgb = ImageOps.autocontrast(rgb, cutoff=0.4); rgb = ImageEnhance.Color(rgb).enhance(1.08); rgb = ImageEnhance.Brightness(rgb).enhance(0.96)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=0.8, percent=70, threshold=2))
    alpha = alpha.point(lambda v: 0 if v < 24 else (255 if v > 200 else v))
    out = rgb.convert('RGBA'); out.putalpha(alpha); return out
if __name__ == '__main__':
    picks = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True); ok = 0
    for k, p in picks.items():
        if os.path.exists('%s/%s.png' % (out, k)): continue
        im = fetch(p['thumb'])
        if im is None: continue
        r = process(im)
        if r: r.save('%s/%s.png' % (out, k)); ok += 1
    print(ok, 'cut out')
