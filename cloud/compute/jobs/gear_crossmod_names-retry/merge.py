import json, pathlib, re, sys
d = pathlib.Path(__file__).parent
sys.path.insert(0, '/mnt/project-files/diaithiris-archaic/tools')
import archaic
rows = {}
for l in open(d / 'out.jsonl'):
    o = json.loads(l); t = o['text'].strip().strip('"').strip().lower()
    if re.fullmatch(r"[a-záéíóúàèìòù]{3,14}", t): rows[o['id']] = t
names = {k: archaic.word(v) for k, v in rows.items() if archaic.word(v) != v}
print(len(names), 'of', len(rows), 'names')
lib = []
for k, n in names.items():
    kind, ident = k.split(':', 1)
    lib.append([n[:1].upper() + n[1:], 'concept' if kind == 'family' else 'item', 4, 'crossmod_gear',
                f"Set family {ident}: wear two or more of its pieces for a bonus, gated by Age." if kind == 'family'
                else f"Socketable gem; matches the Silent Gems trait gem of the same stone."])
json.dump(lib, open('/mnt/project-files/library-sync/crossmod_gear.json', 'w'), ensure_ascii=False)
if '--lang' in sys.argv:
    p = pathlib.Path(sys.argv[sys.argv.index('--lang') + 1]); p.parent.mkdir(parents=True, exist_ok=True)
    lang = {}
    for k, n in names.items():
        kind, ident = k.split(':', 1)
        lang[('set.diaithirgear.' + ident) if kind == 'family' else ('item.apotheosis.gem.' + ident)] = n[:1].upper() + n[1:]
    p.write_text(json.dumps(lang, ensure_ascii=False, indent=1))
