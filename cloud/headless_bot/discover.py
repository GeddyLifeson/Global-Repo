# S6867 discover.py JAR...: list registry ids a jar ships assets for (blockstates, items, entity lang keys); python3 -I discover.py [--json] JAR...
import sys, json, zipfile, re
def discover(jar):
    z = zipfile.ZipFile(jar); r = {'blocks': set(), 'items': set(), 'entities': set()}
    for n in z.namelist():
        m = re.match(r'assets/([^/]+)/(blockstates|items)/([^/]+)\.json$', n)
        if m: r['blocks' if m[2] == 'blockstates' else 'items'].add(f'{m[1]}:{m[3]}')
        m = re.match(r'assets/([^/]+)/lang/en_us\.json$', n)
        if m:
            for k in json.loads(z.read(n)):
                mm = re.match(r'entity\.([^.]+)\.([^.]+)$', k)
                if mm: r['entities'].add(f'{mm[1]}:{mm[2]}')
    return {k: sorted(v) for k, v in r.items()}
if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if x != '--json']
    for j in a:
        d = discover(j)
        if '--json' in sys.argv: print(json.dumps({j: d}))
        else: print(j.split('/')[-1], {k: len(v) for k, v in d.items()}); [print(' ', k, v[:40]) for k, v in d.items() if v]
