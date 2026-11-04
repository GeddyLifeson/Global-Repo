# S6830 Name coverage: every item/block/entity/biome/structure id in rewrite jars (and optional lang json files) vs names/*.json; prints named/pending per module, writes pending.json {id: English}
# python3 -I coverage.py [extra_lang.json:label ...]
import glob, json, os, re, sys, zipfile, collections
R = '/mnt/project-files/names'
named = set()
for f in glob.glob(R + '/*.json'):
    try: d = json.load(open(f))
    except Exception: continue
    if isinstance(d, dict): named.update(k for k, v in d.items() if isinstance(v, dict) and len(v) > 5)
KEY = re.compile(r'^(item|block|entity|biome|structure|fluid_type)\.([a-z0-9_.-]+?)\.(.+)$')
def conv(k):
    m = KEY.match(k)
    return f"{m.group(2)}:{m.group(3).replace('.', '/') if m.group(1) == 'structure' else m.group(3)}" if m else None
mods = collections.defaultdict(dict)
def add(label, lang):
    for k, v in lang.items():
        i = conv(k)
        if i and isinstance(v, str) and len(v) < 60 and not re.search(r'\.(desc|tooltip|lore)', k): mods[label][i] = v
for jar in glob.glob('/mnt/project-files/rewrite-jars/*/*.jar'):
    z = zipfile.ZipFile(jar)
    for n in z.namelist():
        if n.endswith('/lang/en_us.json'): add(os.path.basename(jar).split('-neoforge')[0], json.loads(z.read(n)))
for a in sys.argv[1:]:
    p, label = a.rsplit(':', 1); add(label, json.load(open(p)))
pend = {}
for m in sorted(mods):
    p = {i: e for i, e in mods[m].items() if i not in named and i.replace('/', '.') not in named}
    pend.update({f'{m}|{i}': e for i, e in p.items()})
    print(f'{m}: named {len(mods[m]) - len(p)}, pending {len(p)}')
json.dump(pend, open(R + '/linguistics/pending.json', 'w'), ensure_ascii=False)
print('total pending', len(pend))
