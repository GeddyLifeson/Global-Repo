"""Download candidate thumbs, build montages (up to 8 photos, 4 per row) and the API vision job.
    python3 make_pick_job.py CAND.jsonl START END JOBNAME"""
import json, sys, os, time, urllib.request, concurrent.futures as cf
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/user/work/photo'); import fetch_candidates as fc
rows = [json.loads(l) for l in open(sys.argv[1])][int(sys.argv[2]):int(sys.argv[3])]
job = '/mnt/project-files/compute/jobs/' + sys.argv[4]; rev = '/mnt/project-files/dishes/pickmont'; th = '/mnt/project-files/dishes/thumbs'
for d in (job, rev, th): os.makedirs(d, exist_ok=True)
def dl(a):
    n, k, x = a; f = '%s/%s_%d.jpg' % (th, n, k)
    if not os.path.exists(f):
        for t in range(2):
            try: open(f, 'wb').write(urllib.request.urlopen(urllib.request.Request(x['thumb'], headers={'User-Agent': fc.UA}), timeout=25).read()); break
            except Exception: time.sleep(1)
with cf.ThreadPoolExecutor(8) as ex: list(ex.map(dl, [(r['id'], k, x) for r in rows for k, x in enumerate(r['cand'])]))
SYSTEM = ("You judge candidate photos for a tiny 64 px food icon. You get ONE image: up to 8 photos in a grid (4 per row), each numbered 1 to 8 in its corner. "
          "Given the dish name, pick the single best photo: it must clearly show that exact dish (not a different dish, an ingredient, a menu, a person, a market stall or packaging), "
          "the dish should be the main subject filling much of the frame, whole plate/bowl/portion visible, ideally top-down or three-quarter, sharp, well lit, uncluttered. "
          "Reply with ONLY a JSON object: {\"best\": 1-8 or 0 if none is acceptable, \"dish_visible\": true/false, \"why\": \"six words\"}.")
n = 0
with open(job + '/in.jsonl', 'w') as f:
    for r in rows:
        v = r['cand']
        if not v: continue
        T = 224; cols = min(4, len(v)); rws = (len(v) + 3) // 4; m = Image.new('RGB', (T * cols, T * rws), (30, 30, 30))
        for i in range(len(v)):
            try: im = Image.open('%s/%s_%d.jpg' % (th, r['id'], i)).convert('RGB')
            except Exception: im = Image.new('RGB', (10, 10))
            s = T / max(im.size); im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))))
            t = Image.new('RGB', (T, T), (30, 30, 30)); t.paste(im, ((T - im.width) // 2, (T - im.height) // 2)); d = ImageDraw.Draw(t); d.rectangle((0, 0, 26, 26), fill=(0, 0, 0)); d.text((8, 6), str(i + 1), fill=(255, 255, 0))
            m.paste(t, ((i % 4) * T, (i // 4) * T))
        m.save('%s/%s.png' % (rev, r['id']), optimize=True)
        f.write(json.dumps({'id': r['id'], 'system': SYSTEM, 'prompt': 'Dish: %s\nJSON only.' % r['id'].replace('_', ' '), 'images': ['%s/%s.png' % (rev, r['id'])]}) + '\n'); n += 1
open(job + '/README', 'w').write('Vision pick of dish photos. model: haiku. max_tokens 200. Check rule: JSON with best 0-8. Owner: texture lead thread.\n')
print(n, 'rows with candidates of', len(rows))
