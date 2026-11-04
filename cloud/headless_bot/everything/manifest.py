# S6986 everything/manifest.py JAR_OR_DIR... [-o manifest.json]: static census of what a pack ships: blocks, items, entities, recipes (with parsed grid/result),
# loot tables, dimensions, item tags, plus static recipe checks (unknown result/ingredient, identical-grid conflicts, items with no obtain path).
# KubeJS-script recipes are not parseable here; they are listed as js_recipe_files so the live run can say UNTESTED for them. python3 -I manifest.py ...
import sys, json, zipfile, re, pathlib
def jars_in(args):
    for a in args:
        p = pathlib.Path(a)
        if p.is_dir():
            yield from sorted(p.rglob('*.jar'))
        elif p.suffix == '.jar': yield p
def norm(i):  # item id or #tag with namespace
    return i if ':' in i else 'minecraft:' + i
def ing_ids(v):
    if isinstance(v, str): return [norm(v)]
    if isinstance(v, list): return [x for e in v for x in ing_ids(e)]
    if isinstance(v, dict):
        if 'item' in v: return [norm(v['item'])]
        if 'tag' in v: return ['#' + norm(v['tag'])]
    return []
def census(jars):
    M = {k: {} for k in ('blocks', 'items', 'entities', 'recipes', 'loot', 'dimensions', 'tags')}; M['js_recipe_files'] = []
    for j in jars:
        z = zipfile.ZipFile(j); names = z.namelist(); src = j.name
        for n in names:
            m = re.match(r'assets/([^/]+)/(blockstates|items)/([^/]+)\.json$', n)
            if m: M['blocks' if m[2] == 'blockstates' else 'items'][f'{m[1]}:{m[3]}'] = src; continue
            m = re.match(r'assets/([^/]+)/lang/en_us\.json$', n)
            if m:
                for k in json.loads(z.read(n)):
                    mm = re.match(r'entity\.([^.]+)\.([^.]+)$', k)
                    if mm: M['entities'][f'{mm[1]}:{mm[2]}'] = src
                continue
            m = re.match(r'data/([^/]+)/(recipes?)/(.+)\.json$', n)
            if m:
                try: d = json.loads(z.read(n))
                except Exception: continue
                res = d.get('result'); rid = res if isinstance(res, str) else (res or {}).get('id') or (res or {}).get('item')
                cnt = 1 if isinstance(res, str) else (res or {}).get('count', 1)
                M['recipes'][f'{m[1]}:{m[3]}'] = {'type': d.get('type', ''), 'result': norm(rid) if rid else None, 'count': cnt, 'pattern': d.get('pattern'),
                    'key': {k: ing_ids(v) for k, v in d.get('key', {}).items()}, 'ingredients': [ing_ids(x) for x in d.get('ingredients', [])] if isinstance(d.get('ingredients'), list) else d.get('ingredients'),
                    'ingredient': ing_ids(d['ingredient']) if 'ingredient' in d else None, 'src': src}
                continue
            m = re.match(r'data/([^/]+)/loot_tables?/(.+)\.json$', n)
            if m: M['loot'][f'{m[1]}:{m[2]}'] = sorted(set(re.findall(r'"name"\s*:\s*"([^"]+)"', z.read(n).decode('utf8', 'replace')))); continue
            m = re.match(r'data/([^/]+)/dimension/([^/]+)\.json$', n)
            if m: M['dimensions'][f'{m[1]}:{m[2]}'] = src; continue
            m = re.match(r'data/([^/]+)/tags/items?/(.+)\.json$', n)
            if m:
                try: M['tags'][f'{m[1]}:{m[2]}'] = [v if isinstance(v, str) else v.get('id', '') for v in json.loads(z.read(n)).get('values', [])]
                except Exception: pass
    return M
def checks(M):
    known = set(M['items']) | set(M['blocks']); out = []
    def vanilla(i): return i.startswith('minecraft:')
    sig = {}
    for rid, r in M['recipes'].items():
        res = r['result']
        if res and not vanilla(res) and res not in known: out.append((rid, 'FAIL', f'result {res} is not a registered item'))
        ing = {x for ids in (list(r['key'].values()) + (r['ingredients'] or [] if isinstance(r['ingredients'], list) else [])) for x in ids}
        if r['ingredient']: ing |= set(r['ingredient'])
        for x in ing:
            if not x.startswith('#') and not vanilla(x) and x not in known: out.append((rid, 'FAIL', f'ingredient {x} is not a registered item'))
            if x.startswith('#') and x[1:] not in M['tags'] and x[1:].split(':')[0] not in ('minecraft', 'c', 'neoforge'): out.append((rid, 'FAIL', f'ingredient tag {x} has no tag file'))
        grid = json.dumps([r['type'], r['pattern'], sorted(r['key'].items()), sorted(map(sorted, r['ingredients'])) if isinstance(r['ingredients'], list) else None, r['ingredient']], sort_keys=True)
        sig.setdefault(grid, []).append(rid)
    for g, ids in sig.items():
        res = {M['recipes'][i]['result'] for i in ids}
        if len(ids) > 1 and len(res) > 1: [out.append((i, 'FAIL', f'conflict: same inputs as {[x for x in ids if x != i]} but different results {sorted(res)}')) for i in ids]
        elif len(ids) > 1: [out.append((i, 'FAIL', f'duplicate of {[x for x in ids if x != i]}')) for i in ids]
    made = {r['result'] for r in M['recipes'].values()}; dropped = {i for v in M['loot'].values() for i in v}
    for i in sorted(M['items']):
        if i not in made and i not in dropped and i not in M['blocks']: out.append((i, 'INFO', 'item has no recipe and no loot table drop in the jars (check KubeJS recipes / creative-only)'))
    return out
if __name__ == '__main__':
    a = sys.argv[1:]; o = a[a.index('-o') + 1] if '-o' in a else 'manifest.json'
    if '-o' in a: i = a.index('-o'); a = a[:i] + a[i + 2:]
    M = census(list(jars_in(a))); M['static_checks'] = checks(M)
    json.dump(M, open(o, 'w'), indent=1)
    print({k: len(v) for k, v in M.items()})
