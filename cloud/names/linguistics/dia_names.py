# S6832 Diaithiris (archaic) names for {id: English}: Haiku builds a classical Gaelic-root kenning, tools/archaic.py applies the sound laws, goidelic_words.txt guards against modern equals. Writes {id: {en, diaithir}}.
# python3 -I dia_names.py TERMS.json OUT.json   key from ANTHROPIC_API_KEY (never printed)
import json, os, sys, unicodedata, threading, concurrent.futures as cf
H = '/mnt/project-files/diaithiris-archaic'
sys.path.insert(0, H + '/tools'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import archaic as AR
exec(open(os.path.dirname(os.path.abspath(__file__)) + '/regen_relaxed.py').read().split('def lang(')[0].split('def main')[0]) if False else None
import urllib.request, time
KEY = os.environ['ANTHROPIC_API_KEY']
AR.MEMO.update(json.load(open(H + '/archaic_map.json'))); AR.OVERRIDES.update(json.load(open(H + '/tools/overrides.json')))
REAL = set(l.strip().lower() for l in open(H + '/tools/goidelic_words.txt', encoding='utf8'))
AR.REAL = REAL
SYS = """You build classical Gaelic compound names (kennings) for objects in a game. Given numbered English terms, give for each ONE compound word in Scottish Gaelic spelling (grave accents, sc not sg is NOT needed; use ordinary Scottish Gaelic spelling), built from real Gaelic roots for the meaning, written as a single word with no spaces or hyphens, head noun first then modifiers in the genitive, as in Mactìreanamhòr (wolf), Eachsean (horse old), Leisceanlàirfamhair (ground sloth), Càmhalrèidhthìre (plains camel), Ailbheancoille (forest elk), Dobhranleasleathannfamhair. Two to four roots, 8 to 28 letters. Capitalise the first letter. Do not output the plain modern word alone for the thing: always make a compound or kenning. Return JSON {"n":[{"i":number,"name":string}]} covering every number."""
SCH = {'type': 'object', 'additionalProperties': False, 'required': ['n'], 'properties': {'n': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['i', 'name'], 'properties': {'i': {'type': 'integer'}, 'name': {'type': 'string'}}}}}}
def call(items):
    body = {'model': 'claude-haiku-5-5', 'max_tokens': 8000, 'thinking': {'type': 'disabled'}, 'system': [{'type': 'text', 'text': SYS, 'cache_control': {'type': 'ephemeral', 'ttl': '1h'}}],
            'messages': [{'role': 'user', 'content': '\n'.join(f'{i}. {t}' for i, t in items)}], 'output_config': {'format': {'type': 'json_schema', 'schema': SCH}}}
    req = urllib.request.Request('https://api.anthropic.com/v1/messages', json.dumps(body).encode(), {'x-api-key': KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    for a in range(4):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            return {x['i']: x['name'] for x in json.loads(next(b['text'] for b in r['content'] if b['type'] == 'text'))['n']}
        except Exception: time.sleep(3 * (a + 1))
    return {}
terms = json.load(open(sys.argv[1])); uniq = sorted(set(terms.values())); res = {}; lock = threading.Lock()
def job(ch):
    got = call(ch)
    with lock:
        for i, t in ch:
            nm = got.get(i)
            if nm and ' ' not in nm and nm.lower() not in REAL: res[t] = AR.text(nm)
for rnd in range(3):
    pend = [t for t in uniq if t not in res]
    if not pend: break
    chunks = [list(enumerate(pend[k:k + 100])) for k in range(0, len(pend), 100)]
    with cf.ThreadPoolExecutor(32) as ex: list(ex.map(job, chunks))
out = {i: {'en': e, 'diaithir': res[e]} for i, e in terms.items() if e in res}
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False)
print(len(out), len(terms))
