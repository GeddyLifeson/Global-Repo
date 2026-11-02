"""Find openly licensed Wikimedia Commons photos for each dish.
    python3 fetch_candidates.py NAMES.json OUTDIR   -> OUTDIR/cand.json (id -> [{url,thumb,title,author,license,page}]), OUTDIR/thumbs/<id>_<k>.jpg"""
import json, sys, os, re, time, html, urllib.parse, urllib.request, concurrent.futures as cf
UA = 'DiaithirTextures/1.0 (+https://github.com/GeddyLifeson; open-licence dish photo lookup)'
OK_LIC = re.compile(r'^(cc0|public domain|pd|cc[- ]by(-sa)?[- ]?\d|cc[- ]by(-sa)?$|attribution)', re.I)
BAD_TITLE = re.compile(r'logo|map|flag|diagram|stamp|coat of arms|menu|recipe card|book|poster|sign|\.svg|\.pdf|\.tif|\.ogg|\.webm|cookbook|painting|drawing|statue', re.I)
def api(params):
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    for t in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30))
        except Exception as e: time.sleep(2 + t * 2)
    return {}
def strip(s): return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()
def query_for(n): return n.replace('_', ' ')
def find(n):
    q = query_for(n)
    d = api({'action': 'query', 'generator': 'search', 'gsrsearch': q + ' filetype:bitmap', 'gsrnamespace': 6, 'gsrlimit': 8, 'prop': 'imageinfo',
             'iiprop': 'url|extmetadata|size|mime', 'iiurlwidth': 384, 'format': 'json'})
    out = []
    for p in sorted(d.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 99)):
        ii = (p.get('imageinfo') or [{}])[0]; md = ii.get('extmetadata', {})
        lic = strip(md.get('LicenseShortName', {}).get('value')); 
        if not ii or ii.get('mime') not in ('image/jpeg', 'image/png') or min(ii.get('width', 0), ii.get('height', 0)) < 400: continue
        if BAD_TITLE.search(p['title']) or not OK_LIC.match(lic or ''): continue
        # the dish name's main words should appear in the file title or description
        words = [w for w in re.split(r'[\s_]+', q.lower()) if len(w) > 3]
        text = (p['title'] + ' ' + strip(md.get('ImageDescription', {}).get('value'))).lower()
        if words and not any(w in text for w in words): continue
        out.append({'title': p['title'], 'thumb': ii['thumburl'], 'url': ii['url'], 'page': ii.get('descriptionurl'), 'license': lic,
                    'author': strip(md.get('Artist', {}).get('value'))[:120], 'licurl': strip(md.get('LicenseUrl', {}).get('value'))})
        if len(out) == 4: break
    return n, out
if __name__ == '__main__':
    names = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out + '/thumbs', exist_ok=True)
    cand = {}
    with cf.ThreadPoolExecutor(4) as ex:
        for n, c in ex.map(find, names): cand[n] = c
    for n, c in cand.items():
        for k, x in enumerate(c):
            f = '%s/thumbs/%s_%d.jpg' % (out, n, k)
            if not os.path.exists(f):
                for t in range(3):
                    try: open(f, 'wb').write(urllib.request.urlopen(urllib.request.Request(x['thumb'], headers={'User-Agent': UA}), timeout=30).read()); break
                    except Exception: time.sleep(2)
                time.sleep(0.25)
    json.dump(cand, open(out + '/cand.json', 'w'), indent=1)
    print(sum(1 for c in cand.values() if c), 'of', len(cand), 'dishes have candidates')
