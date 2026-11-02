"""Builds the API job that asks Claude for a per-dish Blender scene spec, and wraps returned scenes for dish_run.py."""
import json, re, sys, os, glob, random, collections
sys.path.insert(0, '/home/user/diaithirrpg/tools/art/blender')
KITDIR = '/home/user/work/dish/'
cu = json.load(open(KITDIR + 'cuisine.json'))
SHAPE = {x[0].split('/')[-1]: x[4] for x in cu['dishes']}
REC = collections.defaultdict(list)
for r in cu['recipes']: REC[r['o'].split('/')[-1]].append(r)
SYSTEM = open(KITDIR + 'scene_instructions.md').read()
def dish_prompt(n):
    rs = REC.get(n, [])[:2]; ing = []
    for r in rs: ing += [i.split(':')[-1].replace('_', ' ') for i in r['i']]
    ing = list(dict.fromkeys(ing))
    st = rs[0]['s'].replace('_', ' ') if rs else ''; me = rs[0].get('m', '') if rs else ''
    return 'Dish id: %s\nName: %s\nCatalogue shape: %s\nCooked in: %s (%s)\nIngredients: %s\nReturn only the JSON object.' % (n, n.replace('_', ' '), SHAPE.get(n, 'plate'), st, me, ', '.join(ing[:14]))
def names_all(): return sorted(os.path.basename(f)[:-4] for f in glob.glob('/home/user/work/dish/orig/content/cuisine/kubejs/assets/diaithir/textures/item/dish/*.png'))
def job(names, out):
    os.makedirs(out, exist_ok=True)
    with open(out + '/in.jsonl', 'w') as f:
        for n in names: f.write(json.dumps({'id': n, 'system': SYSTEM, 'prompt': dish_prompt(n)}) + '\n')
def wrap(n, scene, zoom=0.58, tilt=14):
    return {'name': n, 'views': ['icon'], 'tilt': tilt, 'zoom': zoom, 'materials': {'d': {'type': 'flat', 'rgb': [200, 200, 200]}}, 'parts': [{'part': 'scene', 'mat': 'd', 'scene': scene}]}
def parse(text):
    m = re.search(r'\{.*\}', text, re.S)
    return json.loads(m.group(0)) if m else None
