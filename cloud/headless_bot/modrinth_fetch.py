# S6890 modrinth_fetch.py OUTDIR MC LOADER SLUG... : download the newest build of each Modrinth project for MC/loader plus its required dependencies (test lanes only, never rehosted).
import sys, json, urllib.request, urllib.parse, pathlib
out, mc, loader, *slugs = sys.argv[1:]; out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True); done = set()
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'diaithir-test-lane'})))
def fetch(p):
    if p in done: return
    done.add(p)
    q = urllib.parse.urlencode({'game_versions': json.dumps([mc]), 'loaders': json.dumps([loader])})
    vs = get(f'https://api.modrinth.com/v2/project/{p}/version?{q}')
    if not vs: print('NO BUILD', p); return
    v = vs[0]; f = next((x for x in v['files'] if x.get('primary')), v['files'][0]); dst = out / f['filename']
    if not dst.exists(): dst.write_bytes(urllib.request.urlopen(urllib.request.Request(f['url'], headers={'User-Agent': 'diaithir-test-lane'})).read())
    print('got', f['filename'])
    for d in v['dependencies']:
        if d['dependency_type'] == 'required' and d.get('project_id'): fetch(d['project_id'])
for s in slugs: fetch(s)
