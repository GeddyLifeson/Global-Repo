#!/usr/bin/env python3
"""Resolve each batch row to its wiki page (title + URL) and fetch the full page text. Used by judge.py.
  pages.py resolve N      writes batches/shard_N.src.jsonl = {id,title,url,host} per row (committed; small)
Full text is fetched live by judge.py (pages.text) and cached outside git (~/.cache/judge)."""
import json, os, re, sys, time, difflib, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, '..', 'batches') + '/'
CACHE = os.path.expanduser('~/.cache/judge/'); os.makedirs(CACHE, exist_ok=True)
UA = {'User-Agent': 'PanscriptumJudge/1.0 (personal catalogue)'}
HOSTS = {}
for l in open(os.path.join(HERE, 'wikis.tsv'), encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if len(p) == 2: HOSTS[p[0]] = p[1].split(',')
def api(host, params):
    q = urllib.parse.urlencode({**params, 'format': 'json', 'formatversion': 2})
    for path in ('/api.php', '/w/api.php'):
        for k in range(3):
            try: return json.load(urllib.request.urlopen(urllib.request.Request(f'https://{host}{path}?{q}', headers=UA), timeout=40))
            except Exception as e:
                err = e; time.sleep(1 + k)
    raise err
def norm(s): return re.sub(r'[^0-9a-z]+', '', s.lower())
def match(a, b):
    a, b = norm(a)[:80], norm(b)[:80]
    return bool(a) and difflib.SequenceMatcher(None, a, b).ratio() >= 0.75
def namef(t):
    m = re.split(r' \(|, | (?:is|was|are|were) ', t, maxsplit=1)[0]
    return m[:60]
def intro(host, titles):
    """{title: intro text} for up to 20 titles, redirects resolved (input title -> final)."""
    d = api(host, {'action': 'query', 'prop': 'extracts', 'exintro': 1, 'explaintext': 1, 'exlimit': 'max', 'redirects': 1, 'titles': '|'.join(titles)})
    q = d.get('query', {}); mp = {}
    for x in q.get('normalized', []) + q.get('redirects', []): mp[x['from']] = x['to']
    ex = {p['title']: (p.get('extract', '') or '(no extract)') for p in q.get('pages', []) if not p.get('missing')}
    out = {}
    for t in titles:
        f = t
        for _ in range(3): f = mp.get(f, f)
        out[t] = (f, ex.get(f, ''))
    return out
def resolve(n):
    R = [json.loads(l) for l in open(f'{B}shard_{n}.jsonl', encoding='utf-8')]
    res, weak = {}, {}
    todo = list(enumerate(R))
    for host_i in range(2):
        left = []
        for s in range(0, len(todo), 20):
            ch = todo[s:s + 20]; wiki = {}
            for i, r in ch: wiki.setdefault(r['id'].rsplit('|', 1)[0], []).append((i, r))
            for w, items in wiki.items():
                hosts = HOSTS.get(w, [])
                if host_i >= len(hosts): continue
                h = hosts[host_i]; names = list({namef(r['text']) for i, r in items})
                got = intro(h, names)
                for i, r in items:
                    f, ex = got[namef(r['text'])]
                    if ex == '(no extract)': weak.setdefault(i, (f, h))
                    elif ex and match(r['text'], ex): res[i] = (f, h)
        todo = [(i, r) for i, r in todo if i not in res]
    for i, r in todo:  # fallback: full-text search on each host
        w = r['id'].rsplit('|', 1)[0]
        for h in HOSTS.get(w, []):
            try:
                c = []
                for q in (r['text'][:100], namef(r['text']), ' '.join(namef(r['text']).split()[1:])):
                    if q: c += [x['title'] for x in api(h, {'action': 'query', 'list': 'search', 'srsearch': q, 'srlimit': 3, 'srnamespace': 0})['query']['search'] if x['title'] not in c]
                got = intro(h, c) if c else {}
            except Exception: continue
            hit = next(((f, h) for f, ex in got.values() if ex != '(no extract)' and match(r['text'], ex)), None)
            if hit: res[i] = hit; break
    for i, (f, h) in weak.items():  # page exists but has no intro extract: accept only if the page has no text at all (template pages)
        if i not in res and not full_extract(h, f): res[i] = (f, h)
    path = f'{B}shard_{n}.src.jsonl'
    with open(path, 'w', encoding='utf-8') as o:
        for i, r in enumerate(R):
            t, h = res.get(i, ('', ''))
            u = f"https://{h}/wiki/" + urllib.parse.quote(t.replace(' ', '_')) if t else ''
            o.write(json.dumps({'id': r['id'], 'title': t, 'url': u}, ensure_ascii=False) + '\n')
    print(f'{path}: resolved {len(res)}/{len(R)}')
def full_extract(h, title):
    d = api(h, {'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'titles': title})
    return (d['query']['pages'][0].get('extract', '') or '').strip()
def srcs(n):
    p = f'{B}shard_{int(n)}.src.jsonl'
    if not os.path.exists(p): resolve(int(n))
    return [json.loads(l) for l in open(p, encoding='utf-8')]
def text(url, limit=12000):
    """Full plain text of the page (cached outside git)."""
    if not url: return ''
    f = CACHE + re.sub(r'\W+', '_', url)[-150:] + '.txt'
    if os.path.exists(f): return open(f, encoding='utf-8').read()
    h, t = url.split('/')[2], urllib.parse.unquote(url.split('/wiki/', 1)[1]).replace('_', ' ')
    d = api(h, {'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'titles': t})
    x = (d['query']['pages'][0].get('extract', '') or '')[:limit]
    open(f, 'w', encoding='utf-8').write(x); return x
def exists(url):
    h, t = url.split('/')[2], urllib.parse.unquote(url.split('/wiki/', 1)[1]).replace('_', ' ')
    return not any(x.get('missing') for x in api(h, {'action': 'query', 'titles': t})['query']['pages'])
if __name__ == '__main__' and sys.argv[1] == 'resolve': resolve(int(sys.argv[2]))
