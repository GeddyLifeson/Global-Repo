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
def noparen(s):
    while True:
        t = re.sub(r'\([^()]*\)|（[^（）]*）', '', s)
        if t == s: return s
        s = t
def _match(a, b):
    a, b = norm(a), norm(b); k = min(len(a), len(b), 80)
    if k and a[:k] in b[:k + 400]: return True  # lead after a stub/notice banner
    a, b = a[:k], b[:k]
    return bool(a) and difflib.SequenceMatcher(None, a, b).ratio() >= 0.75
def _inpage(a, b):
    """Fragment/stripped-link lead: a 40-char run from its middle or end appears verbatim in the page."""
    a, b = norm(a), norm(b)
    if len(a) >= 60:  # stripped-link lead: nearly all of it is an in-order subsequence of the page's opening
        sm = difflib.SequenceMatcher(None, a[:250], b[:600], autojunk=False)
        if sum(m.size for m in sm.get_matching_blocks()) / len(a[:250]) >= 0.95: return True
    return len(a) >= 60 and any(a[i:i + 40] in b for i in (len(a) // 2 - 20, len(a) - 40))
def match(a, b):
    a = re.sub(r'\[https?://\S+ ([^\]]*)\]', r'\1', a)  # [url label] -> label
    b2 = re.sub(r'(?m)^=+ .* =+$', '', re.sub(r'\[[^\]]*\]', '', b))  # page: drop link-stub brackets and heading lines (lead has them stripped)
    return _match(a, b) or _match(noparen(a), noparen(b)) or _match(a, b2) or _inpage(a, b)
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
    return m[:60]
def strip_art(n): return re.sub(r'^(?:The|A|An) ', '', n)
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
STOP = {'the', 'a', 'an', 'of', 'and', 'in', 'is', 'was', 'are', 'were', 'to', 'for'}
FIELDS = ('Name', 'name', 'nam', 'MainPage', 'OfficialName', 'CurrentAlias', 'LegacyNumber', 'Title')
def tfield(t, k):
    m = re.search(r'\|\s*' + k + r'\s*=\s*([^|}\n]+)', t)
    return m.group(1).strip() if m else ''
def img_stem(t):
    v = tfield(t, 'Image1') or tfield(t, 'Image')
    return re.sub(r' from .*$', '', re.sub(r'\.\w{3,4}$', '', v.replace('_', ' '))).strip()
def cands(text):
    """Ordered candidate page titles for a row: template fields, or word spans of the leading name (page titles are often a shorter form of it)."""
    out = []
    def add(c):
        c = c.strip()
        if 2 < len(c) <= 80 and c not in out: out.append(c)
    if re.match(r'\s*\{\{', text):
        st = img_stem(text)
        if '(' in st: add(st)
        for k in FIELDS: add(tfield(text, k))
        add(st)
        for k in ('rom', 'dub', 'dub2'): add(tfield(text, k))
        for k in ('Overview', 'Description', 'History'):  # subject of the first sentence of a prose field
            add(re.split(r' \(|, | (?:is|was|are|were) ', tfield(text, k), maxsplit=1)[0][:60])
        return out[:20]
    nm = re.split(r', | (?:is|was|are|were|may refer|can refer|refers) ', text, maxsplit=1)[0][:80]
    nm = re.sub(r'\([^()]{13,}\)|\([^()]*:[^()]*\)', '', nm).strip()  # drop long/translation parentheticals, keep short abbreviations like (ATC)
    if re.match(r'(?:is|was|are|were|\W)', nm) or len(nm) < 3: return out  # name stripped from the row (wikilink removed): found by the text search instead
    tok = re.findall(r'\S+', re.sub(r'[()]', ' ', nm))
    spans = [(i, j) for i in range(len(tok)) for j in range(i + 1, len(tok) + 1)] if len(tok) <= 6 else [(0, k) for k in range(1, 4)] + [(0, len(tok)), (1, len(tok))]
    for i, j in sorted(spans, key=lambda s: (s[0] > 0 and s[1] < len(tok), s[0] - s[1])):
        w = tok[i:j]
        if all(x.lower() in STOP for x in w) or (len(w) == 1 and len(w[0]) < 4 and not re.search(r'\d', w[0])): continue
        add(' '.join(w))
        if w[-1].endswith('s') and not w[-1].endswith('ss'): add(' '.join(w[:-1] + [w[-1][:-1]]))
    return out[:24]
ERRS = [0]
def lookup(h, titles, exist=False):
    """{title: (final title, intro text)}; retries transient errors (a swallowed 429 used to leave whole batches unresolved)."""
    got = {}
    for s in range(0, len(titles), 20):
        ch = titles[s:s + 20]
        for k in range(4):
            try:
                got.update(intro(h, ch))
                if exist:
                    d = api(h, {'action': 'query', 'redirects': 1, 'titles': '|'.join(ch)}); q = d.get('query', {}); mp = {}
                    for x in q.get('normalized', []) + q.get('redirects', []): mp[x['from']] = x['to']
                    ok = {p['title'] for p in q.get('pages', []) if not p.get('missing') and not p.get('invalid')}
                    for t in ch:
                        f = t
                        for _ in range(3): f = mp.get(f, f)
                        if f in ok and not got[t][1]: got[t] = (got[t][0], '(no extract)')  # exists, empty lead (template-only page)
                break
            except Exception as e:
                if k == 3: ERRS[0] += 1; print(f'  lookup failed {h} {ch[:2]}: {str(e)[:60]}', file=sys.stderr, flush=True)
                time.sleep(5 * (k + 1))
    return got
def shingles(s, k=4):
    w = re.findall(r'[0-9a-z]+', s.lower()); return {' '.join(w[i:i + k]) for i in range(len(w) - k + 1)}
def clean_row(t):
    t = re.sub(r'__\w+__|\[https?://\S+ ([^\]]*)\]', r'\1', t)
    t = re.sub(r'(?:^|\s)[a-z]{2,3}(?:-[a-z]+)?:\S+.*$', '', t)  # trailing interlanguage link (pl:Name)
    return re.sub(r'^[\s*:#,.)\]]+|\s\]\]', ' ', t).strip()
def search_cands(h, text):
    """Pages found by full-text search of several quoted/unquoted windows of the row (works when the name is missing from the row)."""
    c = clean_row(text); w = c.split()
    wins = [' '.join(w[i:i + 10]) for i in sorted({0, max(0, len(w) // 2 - 5), max(0, len(w) - 10)})] if len(w) > 6 else [c]
    out = []
    for q in wins + ['"%s"' % x for x in wins]:
        try: out += [x['title'] for x in api(h, {'action': 'query', 'list': 'search', 'srsearch': q, 'srlimit': 6, 'srnamespace': 0})['query']['search'] if x['title'] not in out]
        except Exception: ERRS[0] += 1
    return out[:12]
def by_text(h, text, thr=0.4):
    """Best search candidate whose full text contains >= thr of the row's 4-word shingles (survives holes and mid-page fragments)."""
    sh = shingles(clean_row(text))
    if len(sh) < 3: return None
    best = (0, None)
    for t in search_cands(h, text):
        pt = ' '.join(re.findall(r'[0-9a-z]+', full_extract(h, t).lower()))
        sc = sum(1 for x in sh if x in pt) / len(sh)
        if sc > best[0]: best = (sc, t)
    return best[1] if best[0] >= thr else None
def resolve(n):
    R = [json.loads(l) for l in open(f'{B}shard_{n}.jsonl', encoding='utf-8')]
    res, weak = {}, {}; ERRS[0] = 0
    for host_i in range(2):
        by = {}
        for i, r in enumerate(R):
            if i not in res: by.setdefault(r['id'].rsplit('|', 1)[0], []).append(i)
        for w, idx in by.items():
            hosts = HOSTS.get(w, [])
            if host_i >= len(hosts): continue
            h = hosts[host_i]; C = {i: cands(R[i]['text']) for i in idx}
            print(f'  resolve {n} {w} {len(idx)} rows', file=sys.stderr, flush=True)
            got = lookup(h, sorted({c for v in C.values() for c in v}), exist=any(R[i]['text'].lstrip().startswith('{{') for i in idx))
            for i in idx:
                tpl = R[i]['text'].lstrip().startswith('{{')
                for c in C[i]:
                    f, ex = got.get(c, (c, ''))
                    if ex == '(no extract)':
                        if tpl: res[i] = (f, h); break  # template row: the page named by its fields exists
                        weak.setdefault(i, (f, h))
                    elif ex and match(R[i]['text'], ex): res[i] = (f, h); break
    for i, (f, h) in weak.items():  # page exists with no text at all: accepted only if no later host had a matching page
        if i not in res and not full_extract(h, f): res[i] = (f, h)
    for i, r in enumerate(R):  # fallback: full-text search on each host
        if i in res: continue
        for h in HOSTS.get(r['id'].rsplit('|', 1)[0], []):
            t = by_text(h, r['text'])
            if t: res[i] = (t, h); break
    path = f'{B}shard_{n}.src.jsonl'
    with open(path, 'w', encoding='utf-8') as o:
        for i, r in enumerate(R):
            t, h = res.get(i, ('', ''))
            u = f"https://{h}/wiki/" + urllib.parse.quote(t.replace(' ', '_')) if t else ''
            o.write(json.dumps({'id': r['id'], 'title': t, 'url': u}, ensure_ascii=False) + '\n')
    miss = [r for i, r in enumerate(R) if i not in res]
    ap = f'{B}shard_{n}.absent.json'  # ABSENT RULE: every candidate title and text search ran without a request error and nothing matched -> the page is not on the wiki any more
    if miss and not ERRS[0]: json.dump([r['id'] for r in miss], open(ap, 'w'))
    elif os.path.exists(ap): os.remove(ap)
    if miss: open(os.path.join(HERE, '..', 'diag', f'shard_{n}.unresolved.jsonl'), 'w', encoding='utf-8').write(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in miss))
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
