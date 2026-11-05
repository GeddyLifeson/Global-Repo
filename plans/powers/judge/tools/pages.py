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
import threading
_L = threading.Lock(); _T = {}
def api(host, params):
    with _L:  # per-host throttle: fandom 429s on bursts
        t = max(time.time(), _T.get(host, 0.0)); _T[host] = t + 0.5
    if t > time.time(): time.sleep(t - time.time())
    return _api(host, params)
def _api(host, params):
    q = urllib.parse.urlencode({**params, 'format': 'json', 'formatversion': 2})
    for path in ('/api.php', '/w/api.php'):
        for k in range(6):
            try: return json.load(urllib.request.urlopen(urllib.request.Request(f'https://{host}{path}?{q}', headers=UA), timeout=40))
            except Exception as e:
                err = e
                if '429' in str(e):
                    with _L: _T[host] = max(_T.get(host, 0.0), time.time() + 20 * (k + 1))  # pause that host for every thread
                time.sleep(1 + k)
    raise err
def norm(s): return re.sub(r'[^0-9a-z]+', '', s.lower())
def match(a, b):
    a, b = norm(a), norm(b); k = min(len(a), len(b), 80); a, b = a[:k], b[:k]
    return bool(a) and difflib.SequenceMatcher(None, a, b).ratio() >= 0.75
def html2txt(h):
    """Rendered HTML -> plain text with '== Heading ==' lines (for wikis without TextExtracts, e.g. fandom)."""
    import html as H
    h = re.sub(r'(?is)<div[^>]*(hatnote|dablink|notice|mbox)[^>]*>.*?</div>', '', h)
    h = re.sub(r'(?is)<(script|style|table|aside|sup|figure)\b.*?</\1>', '', h)
    h = re.sub(r'(?is)<h([2-6])[^>]*>(.*?)</h\1>', lambda m: '\n' + '=' * (int(m.group(1)) - 0) + ' ' + re.sub(r'<[^>]+>|\[edit\]', '', m.group(2)).strip() + ' ' + '=' * int(m.group(1)) + '\n', h)
    h = re.sub(r'(?i)<br\s*/?>|</(p|li|div|dd|dt|tr)>', '\n', h)
    h = H.unescape(re.sub(r'<[^>]+>', '', h))
    return re.sub(r'\n\s*\n+', '\n', re.sub(r'[ \t]+', ' ', h)).strip()
def wiki2txt(w):
    """Wikitext -> plain text with '== Heading ==' lines (lossy, deterministic; the validator checks quotes against this same text)."""
    import html as H
    w = re.sub(r'(?s)<!--.*?-->|<ref[^>]*/>|<ref[^>]*>.*?</ref>|<(gallery|noinclude|references)\b.*?</\1>', '', w)
    for _ in range(6): w = re.sub(r'\{\{[^{}]*\}\}|\{\|[^{}]*?\|\}', '', w)
    w = re.sub(r'\[\[(?:File|Image|Category):[^\]]*\]\]', '', w, flags=re.I)
    w = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', w)
    w = re.sub(r'\[https?://\S+ ([^\]]*)\]|\[https?://\S+\]', r'\1', w)
    w = re.sub(r"'{2,}", '', w); w = re.sub(r'<[^>]+>', '', w)
    w = re.sub(r'^[*#:;]+ *', '', w, flags=re.M)
    return re.sub(r'\n\s*\n+', '\n', H.unescape(w)).strip()
def _full(host, t):
    f, x = ptext(host, t)
    if x:  # cache the full page now so text() needs no second request
        u = f"https://{host}/wiki/" + urllib.parse.quote(f.replace(' ', '_'))
        open(CACHE + re.sub(r'\W+', '_', u)[-150:] + '.txt', 'w', encoding='utf-8').write(x[:12000])
    return f, x
def ptext(host, title, intro_only=False):
    """Plain page text via action=parse; '(no extract)' if page missing/empty (matches the extracts convention)."""
    try:
        d = api(host, {'action': 'parse', 'page': title, 'prop': 'text', 'redirects': 1, 'disableeditsection': 1, **({'section': 0} if intro_only else {})})
        return d['parse']['title'], html2txt(d['parse']['text'])
    except Exception:
        return title, ''
def namef(t):
    m = re.match(r'\s*\{\{', t) and re.search(r'\|\s*(?:MainPage|Name|OfficialName|Title|rom)\s*=\s*([^|}\n]+)', t)  # template-start rows: name from the template fields
    if m: return m.group(1).strip()[:60]
    m = re.split(r' \(|, | (?:is|was|are|were) ', t, maxsplit=1)[0]
    return re.sub(r'^(?:The|A|An) ', '', m)[:60]
def intro(host, titles):
    """{title: intro text} for up to 20 titles, redirects resolved (input title -> final)."""
    d = api(host, {'action': 'query', 'prop': 'extracts', 'exintro': 1, 'explaintext': 1, 'exlimit': 'max', 'redirects': 1, 'titles': '|'.join(titles)})
    q = d.get('query', {}); mp = {}
    if 'extracts' in str(d.get('warnings', '')) + str(q.get('warnings', '')):  # wiki without TextExtracts: one batched wikitext request, cleaned to plain text
        d = api(host, {'action': 'query', 'prop': 'revisions', 'rvprop': 'content', 'rvslots': 'main', 'redirects': 1, 'titles': '|'.join(titles)})
        q = d.get('query', {}); mp = {}
        for x in q.get('normalized', []) + q.get('redirects', []): mp[x['from']] = x['to']
        got = {}
        for p in q.get('pages', []):
            if isinstance(p, dict) and not p.get('missing') and p.get('revisions'):
                got[p['title']] = wiki2txt(p['revisions'][0]['slots']['main']['content'])
        out = {}
        for t in titles:
            f = t
            for _ in range(3): f = mp.get(f, f)
            x = got.get(f, '')
            if x:
                u = f"https://{host}/wiki/" + urllib.parse.quote(f.replace(' ', '_'))
                open(CACHE + re.sub(r'\W+', '_', u)[-150:] + '.txt', 'w', encoding='utf-8').write(x[:12000])
            out[t] = (f, x[:600] if x else '')
        return out
    for x in q.get('normalized', []) + q.get('redirects', []): mp[x['from']] = x['to']
    ex = {p['title']: (p.get('extract', '') or '(no extract)') for p in q.get('pages', []) if isinstance(p, dict) and not p.get('missing')}
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
            print(f'  resolve {n} pass{host_i} {s}/{len(todo)}', file=sys.stderr, flush=True)
            for i, r in ch: wiki.setdefault(r['id'].rsplit('|', 1)[0], []).append((i, r))
            for w, items in wiki.items():
                hosts = HOSTS.get(w, [])
                if host_i >= len(hosts): continue
                h = hosts[host_i]; names = list({namef(r['text']) for i, r in items})
                try: got = intro(h, names)
                except Exception: continue
                for i, r in items:
                    f, ex = got[namef(r['text'])]
                    if ex in ('(no extract)', '') and re.match(r'\s*\{\{', r['text']) and (ex or not api(h, {'action': 'query', 'titles': f})['query']['pages'][0].get('missing')): res[i] = (f, h)  # template row, page exists but has an empty lead
                    elif ex == '(no extract)': weak.setdefault(i, (f, h))
                    elif ex and match(r['text'], ex): res[i] = (f, h)
                    elif ex and ex != '(no extract)' and re.match(r'\s*\{\{', r['text']): res[i] = (f, h)  # template-start row: the page named by its Name/MainPage field
        todo = [(i, r) for i, r in todo if i not in res]
    for i, r in todo:  # fallback: full-text search on each host
        w = r['id'].rsplit('|', 1)[0]
        for h in HOSTS.get(w, []):
            try:
                c = []
                for q in (r['text'][:100], r['text'][60:160], namef(r['text']), ' '.join(namef(r['text']).split()[1:])):
                    if q: c += [x['title'] for x in api(h, {'action': 'query', 'list': 'search', 'srsearch': q, 'srlimit': 3, 'srnamespace': 0})['query']['search'] if x['title'] not in c]
                got = intro(h, c) if c else {}
            except Exception: continue
            hit = next(((f, h) for f, ex in got.values() if ex != '(no extract)' and match(r['text'], ex)), None)
            if not hit:  # mid-page fragment: accept a candidate whose full text contains the row's opening words
                nt = norm(r['text']); keys = [k for k in (nt[:60], nt[60:120]) if len(k) >= 30]  # the 2nd key survives stripped names at the start
                hit = next(((f, h) for f, _ in got.values() if any(k in (pt := norm(full_extract(h, f))) for k in keys)), None)
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
    if 'extracts' in str(d.get('warnings', '')): return ptext(h, title)[1]
    return (d['query']['pages'][0].get('extract', '') or '').strip()
def srcs(n):
    p = f'{B}shard_{int(n)}.src.jsonl'
    if not os.path.exists(p): resolve(int(n))
    return [json.loads(l) for l in open(p, encoding='utf-8')]
_PK = {}
def _packed():
    if not _PK:
        import glob, gzip
        for g in glob.glob(os.path.join(HERE, '..', 'cache', '*.pages.json.gz')):
            _PK.update(json.load(gzip.open(g, 'rt', encoding='utf-8')))
        _PK[''] = ''
    return _PK
def text(url, limit=12000):
    """Full plain text of the page (cached outside git)."""
    if not url: return ''
    c = _packed()
    if url in c: return c[url]
    f = CACHE + re.sub(r'\W+', '_', url)[-150:] + '.txt'
    if os.path.exists(f): return open(f, encoding='utf-8').read()
    h, t = url.split('/')[2], urllib.parse.unquote(url.split('/wiki/', 1)[1]).replace('_', ' ')
    d = api(h, {'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'titles': t})
    x = intro(h, [t]).get(t, ('', ''))[0] and open(CACHE + re.sub(r'\W+', '_', url)[-150:] + '.txt', encoding='utf-8').read() if 'extracts' in str(d.get('warnings', '')) and os.path.exists(CACHE + re.sub(r'\W+', '_', url)[-150:] + '.txt') else ptext(h, t)[1][:limit] if 'extracts' in str(d.get('warnings', '')) else (d['query']['pages'][0].get('extract', '') or '')[:limit]
    open(f, 'w', encoding='utf-8').write(x); return x
def exists(url):
    h, t = url.split('/')[2], urllib.parse.unquote(url.split('/wiki/', 1)[1]).replace('_', ' ')
    return not any(x.get('missing') for x in api(h, {'action': 'query', 'titles': t})['query']['pages'])
if __name__ == '__main__' and sys.argv[1] == 'resolve': resolve(int(sys.argv[2]))
