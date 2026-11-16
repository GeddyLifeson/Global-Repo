# J16/J2 from the wave17 jar extract: English names for every item and block id, and the ids with no name key.
import json, zipfile, os, collections
O = 'E:/wave17_extract/out3/'
lang = json.load(open(O + 'lang_en_us.json', encoding='utf-8'))
# the three lang files json.load rejected: reread leniently
for jn, ns in [('diaithir-worldgen-suite-neoforge-26.1.2-1.0.0.jar', 'patpat'), ('diaithir-worlds-ext-suite-neoforge-26.1.2-1.0.0.jar', 'deeper_dark'), ('adorabuild-structures-2.11.0-neoforge-26.1.1.jar', 'adorabuild_structures')]:
    p = [v for k, v in json.load(open('E:/wave17_extract/resolved.json')).items() if k == jn][0]
    raw = zipfile.ZipFile(p).read(f'assets/{ns}/lang/en_us.json').decode('utf-8-sig', 'replace')
    try:
        lang.setdefault(ns, {}).update(json.loads(raw, strict=False))
    except Exception as e:
        print('still bad', ns, e, len(raw))
flat = {k: v for d in lang.values() for k, v in d.items()}
items = open(O + 'ids_item.txt').read().split('\n')
blocks = open(O + 'ids_block.txt').read().split('\n')
def key(kind, i):
    ns, p = i.split(':', 1); return f'{kind}.{ns}.{p.replace("/", ".")}'
def name(kind, i):
    return flat.get(key(kind, i))
os.makedirs('E:/wave17_extract/res', exist_ok=True)
noi, nob = [], []
with open('E:/wave17_extract/res/LANG_NAMES_WAVE17.tsv', 'w', encoding='utf-8', newline='') as f:
    f.write('id\tkind\tname\n')
    for i in sorted(set(items)):
        n = name('item', i) or name('block', i)
        if n: f.write(f'{i}\titem\t{n}\n')
        else: noi.append(i)
    for i in sorted(set(blocks)):
        n = name('block', i)
        if n: f.write(f'{i}\tblock\t{n}\n')
        else: nob.append(i)
open('E:/wave17_extract/res/J16_NO_NAME_ITEMS.txt', 'w').write('\n'.join(noi))
open('E:/wave17_extract/res/J16_NO_NAME_BLOCKS.txt', 'w').write('\n'.join(nob))
c = collections.Counter(i.split(':')[0] for i in noi)
print(len(set(items)), 'item ids', len(noi), 'without name;', len(set(blocks)), 'block ids', len(nob), 'without name;', c.most_common(6), collections.Counter(i.split(':')[0] for i in nob).most_common(6))
