# S0312 Regenerates every culture name that fails its language rules (Haiku, rules file cached per language, up to 3 repair rounds); writes names/linguistics/regen/<slug>.json {file|id: name}
# python3 -I regen_names.py [slug ...]   key from ANTHROPIC_API_KEY (never printed)
import glob, json, os, sys, time, urllib.request, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_names as A
R = A.R; OUT = R + '/linguistics/regen'; MODEL = 'claude-haiku-5-5'; KEY = os.environ['ANTHROPIC_API_KEY']; CH = 120
os.makedirs(OUT, exist_ok=True)
SYS = """You coin names in one culture's language for a game, the way a specialist linguist of that language would build them. You get the language's rules file (phonology, orthography, morphology, compounding, attested roots, constraints). For each numbered English term, build a name from real roots or regular word formation in that language (or its stated proxy), following the noun-phrase order, compounding and orthography in the rules, using only the allowed graphemes and avoiding forbidden patterns. Keep it short (usually 1 to 3 words). Do not copy the English. Do not use modern Irish, Scottish Gaelic or Manx words unless the language is Goidelic. Where the proxy is speculative, keep to the proxy's regular patterns. Return JSON: {"n":[{"i":number,"name":string}]} covering every number."""
SCH = {'type': 'object', 'additionalProperties': False, 'required': ['n'], 'properties': {'n': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['i', 'name'], 'properties': {'i': {'type': 'integer'}, 'name': {'type': 'string'}}}}}}

def call(rules_txt, items):
    user = '\n'.join(f"{i}. {t}" for i, t in items)
    body = {'model': MODEL, 'max_tokens': 8000, 'thinking': {'type': 'between_tools'},
            'system': [{'type': 'text', 'text': SYS + '\n\nRULES FILE:\n' + rules_txt, 'cache_control': {'type': 'ephemeral', 'ttl': '1h'}}],
            'messages': [{'role': 'user', 'content': user}], 'output_config': {'format': {'type': 'json_schema', 'schema': SCH}}}
    req = urllib.request.Request('https://api.anthropic.com/v1/messages', json.dumps(body).encode(), {'x-api-key': KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    for a in range(4):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            u = r['usage']
            open(R + '/../compute/ledger.csv', 'a').write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())},name-regen,{MODEL},{u.get('input_tokens')},{u.get('output_tokens')},{u.get('cache_creation_input_tokens')},{u.get('cache_read_input_tokens')}\n")
            return {x['i']: x['name'] for x in json.loads(next(b['text'] for b in r['content'] if b['type'] == 'text'))['n']}
        except Exception:
            time.sleep(3 * (a + 1))
    return {}

def main():
    import threading
    bad = json.load(open(R + '/linguistics/audit.json'))
    want = set(sys.argv[1:])
    en = {}
    for f in glob.glob(R + '/*.json'):
        try: d = json.load(open(f))
        except Exception: continue
        if isinstance(d, dict):
            for eid, v in d.items():
                if isinstance(v, dict) and 'en' in v: en[(os.path.basename(f), eid)] = v['en']
    todo = {s: {f'{f}|{e}': en[(f, e)] for f, e, _, _ in rows if (f, e) in en} for s, rows in bad.items() if not want or s in want}
    terms = {s: sorted(set(t.values())) for s, t in todo.items()}
    res = {}
    for s in todo:
        p = f'{OUT}/{s}.terms.json'
        res[s] = json.load(open(p)) if os.path.exists(p) else {}
    rules = {s: open(f'{R}/linguistics/rules/{s}.json').read() for s in todo}
    lock = threading.Lock(); done = [0]
    def job(s, ch):
        got = call(rules[s], ch)
        with lock:
            for i, t in ch:
                nm = got.get(i)
                if nm and not A.check(s, nm): res[s][t] = nm
            done[0] += 1
            if done[0] % 100 == 0:
                for q in res: json.dump(res[q], open(f'{OUT}/{q}.terms.json', 'w'), ensure_ascii=False)
                print('calls', done[0], flush=True)
    for rnd in range(4):
        jobs = []
        for s in todo:
            pend = [t for t in terms[s] if t not in res[s]]
            for k in range(0, len(pend), CH): jobs.append((s, list(enumerate(pend[k:k + CH]))))
        print('round', rnd, 'chunks', len(jobs), flush=True)
        if not jobs: break
        with cf.ThreadPoolExecutor(24) as ex: list(ex.map(lambda a: job(*a), jobs))
        for q in res: json.dump(res[q], open(f'{OUT}/{q}.terms.json', 'w'), ensure_ascii=False)
    for s in todo:
        out = {k: res[s][t] for k, t in todo[s].items() if t in res[s]}
        json.dump(out, open(f'{OUT}/{s}.json', 'w'), ensure_ascii=False)
        print('ok', s, len(out), len(todo[s]), flush=True)
main()
