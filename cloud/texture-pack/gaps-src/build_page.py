"""Progress page: finished photo icons (64 px) next to their source photo, with credits."""
import json, os, base64, io, html, glob
from PIL import Image
cand = {}
for l in open('/mnt/project-files/dishes/cand_all.jsonl'):
    r = json.loads(l); cand[r['id']] = r['cand']
picks = json.load(open('/home/user/work/photo/picks_all.json'))
done = sorted(os.path.basename(f)[:-4] for f in glob.glob('/home/user/work/photo/cut_all/*.png'))
def b64(im, fmt='PNG'):
    b = io.BytesIO(); im.save(b, fmt); return base64.b64encode(b.getvalue()).decode()
cards = ''; credits = []
for n in done:
    p = picks.get(n)
    if not p: continue
    k = next((i for i, x in enumerate(cand[n]) if x['title'] == p['title']), 0)
    try: src = Image.open('/mnt/project-files/dishes/thumbs/%s_%d.jpg' % (n, k)).convert('RGB'); src.thumbnail((128, 128)); sb = b64(src, 'JPEG').replace('PNG', 'JPEG')
    except Exception: sb = ''
    icon = Image.open('/home/user/work/photo/cut_all/%s.png' % n)
    credits.append({'dish': n, 'title': p['title'], 'author': p['author'], 'license': p['license'], 'licurl': p.get('licurl', ''), 'page': p.get('page')})
    cards += '<figure><div class="pair"><img class="ic" src="data:image/png;base64,%s" width="64" height="64" alt=""><img class="src" src="data:image/jpeg;base64,%s" alt=""></div><figcaption><b>%s</b><br><a href="%s">%s</a>, %s</figcaption></figure>\n' % (
        b64(icon), sb, html.escape(n.replace('_', ' ')), html.escape(p.get('page') or '#'), html.escape((p['author'] or 'unknown')[:40]), html.escape(p['license']))
json.dump(credits, open('/mnt/project-files/dishes/CREDITS.json', 'w'), indent=1)
open('/mnt/project-files/dishes/CREDITS.md', 'w').write('# Dish photo credits\n\n' + '\n'.join('- %s: "%s" by %s, %s (%s)' % (c['dish'], c['title'], c['author'] or 'unknown', c['license'], c['page']) for c in credits) + '\n')
page = '''<title>Dish Photo Icons</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root{--bg:#f3f1ee;--fg:#22211f;--mute:#6b665f;--card:#fff;--line:#d9d4cc;--stage:#3a3a3e;--acc:#b4531a}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1b1a19;--fg:#ece8e1;--mute:#a09a90;--card:#262523;--line:#3b3935;--acc:#e08a4a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#1b1a19;--fg:#ece8e1;--mute:#a09a90;--card:#262523;--line:#3b3935;--acc:#e08a4a;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;padding-block:24px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:1200px;margin:0 auto}h1{font-size:1.5rem;margin:0 0 6px}.count{font-size:2rem;font-weight:700;color:var(--acc);font-variant-numeric:tabular-nums}
p{color:var(--mute);max-width:70ch;margin:0 0 18px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
figure{margin:0;background:var(--card);border:1px solid var(--line);padding:10px;display:flex;flex-direction:column;gap:8px;min-width:0}
.pair{display:flex;gap:10px;align-items:center;justify-content:center}.ic{width:64px;height:64px;background:var(--stage);flex:none;image-rendering:auto}.src{max-width:96px;max-height:96px;border:1px solid var(--line)}
figcaption{font-size:12px;color:var(--mute);overflow-wrap:anywhere}figcaption b{color:var(--fg)}a{color:var(--acc)}
</style>
<main><h1>Dish photo icons</h1><div class="count">%d <span style="font-size:1rem;font-weight:400;color:var(--mute)">of 1,365 done</span></div>
<p>Each icon is a real, openly licensed photo (Wikimedia Commons or Flickr CC) picked by the API as the best match for the dish, cut out, cropped and shrunk to 64 px. The small square is the actual size in the pack; the photo beside it is the source. Dishes with no usable photo get a Blender render instead. Credits ship with the pack. This page is republished as batches finish.</p>
<div class="grid">
%s</div></main>''' % (len(credits), cards)
open('/home/user/work/photo/page.html', 'w').write(page); print(len(credits), 'cards', len(page) // 1024, 'KB')
