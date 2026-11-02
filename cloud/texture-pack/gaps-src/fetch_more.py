"""Add Openverse (Flickr CC and others; by/by-sa/cc0/pdm only) and more Commons queries to each dish's candidate list.
    python3 fetch_more.py QUERIES_OUT.jsonl CANDDIR   (reads/updates CANDDIR/cand.json, writes thumbs)"""
import json, sys, os, re, time, urllib.parse, urllib.request, concurrent.futures as cf
sys.path.insert(0, '/home/user/work/photo')
import fetch_candidates as fc
UA = fc.UA
OV_FAILS = 0
def ov(q):
    url = 'https://api.openverse.org/v1/images/?' + urllib.parse.urlencode({'q': q, 'page_size': 8, 'license': 'cc0,pdm,by,by-sa', 'category': 'photograph', 'mature': 'false'})
    global OV_FAILS
    if OV_FAILS > 12: return []
    try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=14)).get('results', [])
    except Exception:
        OV_FAILS += 1; return []
def more(args):
    n, qs, have = args; out = []
    words = [w for q in qs[:2] for w in re.split(r'\W+', q.lower()) if len(w) > 3]
    for q in qs[:2]:
        for r in ov(q):
            if min(r.get('width') or 0, r.get('height') or 0) < 300: continue
            text = ((r.get('title') or '') + ' ' + ' '.join(t.get('name', '') for t in r.get('tags') or [])).lower()
            if not any(w in text for w in words): continue
            if r['license'] in ('by-nd', 'by-nc', 'by-nc-sa', 'by-nc-nd'): continue
            out.append({'title': r.get('title') or q, 'thumb': r.get('thumbnail') or r['url'], 'url': r['url'], 'page': r.get('foreign_landing_url'), 'license': 'CC ' + r['license'].upper() + ' ' + (r.get('license_version') or ''),
                        'author': (r.get('creator') or '')[:120], 'licurl': r.get('license_url') or '', 'source': r.get('source')})
        if len(out) >= 6: break
    for q in qs[:2]:  # extra Commons pass with the better queries
        if len(have) + len(out) >= 8: break
        out += [x for x in fc.find(q)[1] if all(x['title'] != h['title'] for h in have)][:3]
    return n, (have + out)[:8]
if __name__ == '__main__':
    qs = {}
    for l in open(sys.argv[1]):
        r = json.loads(l)
        try: j = json.loads(re.search(r'\{.*\}', r['text'], re.S).group(0)); qs[r['id']] = [q for q in j['queries'] if q]
        except Exception: pass
    cd = sys.argv[2]; cand = json.load(open(cd + '/cand.json'))
    todo = [(n, qs[n], cand.get(n, [])) for n in cand if n in qs]
    with cf.ThreadPoolExecutor(3) as ex:
        for n, c in ex.map(more, todo): cand[n] = c
    os.makedirs(cd + '/thumbs', exist_ok=True)
    def dl(a):
        n, k, x = a; f = '%s/thumbs/%s_%d.jpg' % (cd, n, k)
        if not os.path.exists(f):
            for t in range(3):
                try: open(f, 'wb').write(urllib.request.urlopen(urllib.request.Request(x['thumb'], headers={'User-Agent': UA}), timeout=40).read()); break
                except Exception: time.sleep(2)
    with cf.ThreadPoolExecutor(4) as ex: list(ex.map(dl, [(n, k, x) for n, c in cand.items() for k, x in enumerate(c)]))
    json.dump(cand, open(cd + '/cand.json', 'w'), indent=1)
    print(sum(1 for c in cand.values() if c), 'of', len(cand), 'dishes have candidates;', sum(len(c) for c in cand.values()), 'total')
