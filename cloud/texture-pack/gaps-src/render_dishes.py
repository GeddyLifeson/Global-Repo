"""out.jsonl (scene specs from the API) -> kit specs -> sharded Blender renders -> 64 px PNGs + review images.
    python3 render_dishes.py OUT_JSONL WORKDIR [shards=3]"""
import json, sys, os, subprocess, shutil, glob
sys.path.insert(0, '/home/user/work/dish')
import make_dish_scenes as m
from PIL import Image
out, work = sys.argv[1], sys.argv[2]; N = int(sys.argv[3]) if len(sys.argv) > 3 else 3
shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
specs = []; bad = []
for line in open(out):
    r = json.loads(line)
    try:
        sc = m.parse(r['text']); assert sc and 'vessel' in sc and sc.get('layers')
        for L in sc['layers']:
            if L.get('k') not in ('mound', 'pool', 'chunk', 'slice', 'fillet', 'ball', 'cyl', 'wedge', 'egg', 'shrimp', 'leaf', 'ring', 'noodles', 'scatter', 'grains'): L['k'] = 'chunk'
        specs.append(m.wrap(r['id'], sc))
    except Exception as e: bad.append(r['id'])
print(len(specs), 'ok', len(bad), 'unparsed', bad[:10])
json.dump(bad, open(work + '/bad.json', 'w'))
ps = []
for k in range(N):
    json.dump(specs[k::N], open(work + '/s%d.json' % k, 'w'))
    ps.append(subprocess.Popen(['/root/bpyenv/bin/python', '/home/user/diaithirrpg/tools/art/blender/dish_run.py', '--', work + '/s%d.json' % k, work + '/o%d' % k, '--res', '64', '--samples', '64', '--no-sheets'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
for p in ps: p.wait()
os.makedirs(work + '/png', exist_ok=True); os.makedirs(work + '/rev', exist_ok=True)
for f in glob.glob(work + '/o*/*_icon.png'):
    n = os.path.basename(f)[:-9]; t = Image.open(f).convert('RGBA')
    t64 = t.resize((64, 64), Image.LANCZOS); t64.save(work + '/png/%s.png' % n)
    bg = Image.new('RGBA', (256, 256), (60, 60, 64, 255)); bg.alpha_composite(t64.resize((256, 256), Image.NEAREST)); bg.convert('RGB').save(work + '/rev/%s.png' % n)
print(len(glob.glob(work + '/png/*.png')), 'rendered')
