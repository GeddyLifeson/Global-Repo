# S6975 Judge every wiki lead page with Claude Haiku (Batch API): being or not, powers from the shared pool, magnitude 1-10, evidence quote, missing powers.
"""Usage (key from env ANTHROPIC_API_KEY, never printed):
  judge_pages.py build  WORKDIR [--pilot]      write inputs.jsonl (skips empty/junk leads); --pilot = ~300 chosen rows
  judge_pages.py fetch  WORKDIR wiki=Title ... append live-fetched pages (section 0) to inputs.jsonl
  judge_pages.py sync   WORKDIR [N]            direct calls for the pilot (24 threads) -> results_sync.jsonl
  judge_pages.py submit WORKDIR                Batch chunks of 5000 -> batches.json
  judge_pages.py collect WORKDIR               fetch finished batches -> results.jsonl, validate, usage totals
  judge_pages.py tsv    WORKDIR OUT.tsv        flatten validated results to one row per (page, power)
"""
import json, os, sys, re, glob, random, csv, time, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor
LEADS = '/mnt/project-files/assay-c3m/leads'
POOL = '/mnt/project-files/plans/powers/POWER_POOL.tsv'
MODEL = os.environ.get('JUDGE_MODEL', 'claude-haiku-5-5')
API = 'https://api.anthropic.com/v1'
GLOSS = {'dragon_form': 'shapeshifting, beast/dragon/monster transformation', 'ki_resource': 'user of ki/chi/qi/spirit energy/aura',
         'giant_size': 'growing to giant size', 'hard_body': 'body hardened like iron/diamond/stone', 'iron_shirt': 'armoured or toughened skin',
         'immortal_body': 'ageless, deathless, undying', 'phase': 'passing through solid matter, intangibility', 'blink': 'teleportation',
         'gravity_repulse': 'telekinetic or force push/gravity blast', 'qi_heal': 'healing others/self through meditation or qi',
         'pressure_strike': 'pressure-point, nerve or meridian strikes, death touch', 'flying_sword': 'flying swords, sword qi',
         'levitation': 'hovering, floating', 'glide': 'gliding on wings or membranes', 'barrage': 'rapid-fire flurries of punches/strikes',
         'invulnerability': 'cannot be harmed by ordinary attacks', 'dash': 'bursts of speed', 'super_speed': 'superhuman running or movement speed',
         'whirlwind': 'wind/cyclone attacks', 'freeze_breath': 'ice/frost breath or cold aura', 'fireball': 'fire attacks, flame breath',
         'ki_blast': 'ki/spirit/chi energy blasts', 'energy_beam': 'beams: eye beams, lasers, heat vision, radiant beams',
         'vibrating_palm': 'inner-force palm strikes', 'telepathy': 'mind reading or mental communication', 'time_stop': 'stopping or controlling time',
         'invisibility': 'becoming unseen', 'regeneration': 'rapid healing', 'spectral_flight': 'ghostly flight', 'flight': 'flying under own power',
         'super_strength': 'superhuman strength'}

def pool():
    return [r for r in csv.DictReader(open(POOL, encoding='utf-8'), delimiter='\t')]

def system_prompt():
    lines = '\n'.join(f"- {r['id']}: {GLOSS.get(r['id'], r['name'])}" for r in pool())
    return f"""You judge one wiki page lead (the opening text, name often stripped) for a game that grants superpowers to characters.
Reply with ONE line of compact JSON and nothing else, whatever the input is. Garbage, code, or anything that is not a page lead gets {{"b":0}}. Never write prose.

STEP 1. Classify the page: a being (named character, creature, deity or individual who acts), a weapon, armor, a vehicle (craft, ship, mech, car, any rideable or piloted machine), or other (episodes, other items, places, songs, groups, concepts, game mechanics, real people who are not characters, image/file junk). If other reply exactly {{"b":0}}.
STEP 1b. If a weapon, armor or vehicle reply {{"b":2,"k":"weapon|armor|vehicle","n":"<its name as written in the text or empty>","m":<1-10 overall scale of what it can affect or withstand>,"q":"<verbatim quote showing the scale, or empty>","c":"h|m|l","p":[same power entries as below, only if the text states a pool power it grants or fires]}}. Use the same magnitude scale; ordinary gear is 1.
STEP 2. If a being reply {{"b":1,"n":"<its name as written in the text or empty>","p":[{{"id":"<pool id>","m":<1-10>,"q":"<verbatim quote from the text, max 120 chars>","c":"h|m|l"}}],"x":["<short snake_case name of a power the text states that no pool id covers>"]}}
- "p": only powers the text states or clearly implies, ids ONLY from this pool:
{lines}
- Judge ONLY the powers of the page's own subject, never of other characters the text mentions (a page about a student who watches a hero fight has no hero powers).
- Every p entry needs a verbatim quote copied exactly from the text, and the quote itself must state or plainly show that power (a sentence about training, a title or a fighting style is not a quote for strength or ki). No such quote, no power. An empty p is normal and correct for most pages. Do not invent powers a character is merely famous for; judge only this text.
- "m" is the magnitude 1-10 of that power, judged from what the text says it can affect: 1 peak human, 2 city block, 3 building or tank, 4 city, 5 mountain, 6 island, 7 ocean or continent, 8 moon, 9 planet, 10 star, galaxy, universe or reality. Words like "godlike", "unmatched" or "world-shaking" without a scale mean 6-8 low confidence; no scale words at all means 1-3 low confidence.
- "c" is your confidence in the power and magnitude: h text states it with scale evidence, m text states it without clear scale, l inferred or no scale.
- "x": powers the text states that fit no pool id (e.g. necromancy, shadow_manipulation, shapeshifting is NOT missing: use dragon_form). Empty list if none.
- Keep it short: at most 8 powers, no extra keys, no explanations."""

def junk(t):
    t = t.strip()
    return len(t) < 40 or bool(re.match(r'^[^ ]+\.(jpg|jpeg|png|gif|svg|webp|ogg|mp3)\b', t, re.I)) or t.lower().startswith(('link=', 'file:'))

def iter_leads():
    for f in sorted(glob.glob(f'{LEADS}/*.jsonl')):
        w = os.path.basename(f)[:-6]
        for l in open(f, encoding='utf-8'):
            d = json.loads(l)
            yield w, d['i'], d.get('text', '')

PILOT_FIND = [('dc', r'Superman|Kal-El|Man of Steel'), ('marvel', r'Superman|Hulk'), ('dragon-ball-z', r'Goku|Kakarot'), ('fist-of-the-north-star', r'Kenshiro'),
              ('jojo-s-bizarre-adventure', r'Jotaro'), ('dc', r'\bFlash\b|Barry Allen|speedster'), ('dragon-ball-z', r'Vegeta|Frieza'),
              ('marvel', r'Thor|Silver Surfer'), ('fist-of-the-north-star', r'Raoh')]

def cmd_build(wd, pilot):
    os.makedirs(wd, exist_ok=True)
    rows, skipped = [], 0
    for w, i, t in iter_leads():
        if junk(t): skipped += 1; continue
        rows.append({'id': f'{w}|{i}', 'text': t})
    print('pages', len(rows) + skipped, 'kept', len(rows), 'skipped', skipped)
    if pilot:
        random.seed(7)
        pick = {}
        for w, rx in PILOT_FIND:
            c = [r for r in rows if r['id'].startswith(w + '|') and re.search(rx, r['text'])]
            for r in c[:3]: pick[r['id']] = r
        rest = [r for r in rows if r['id'] not in pick]
        for r in random.sample(rest, 300 - len(pick)): pick[r['id']] = r
        rows = list(pick.values())
        print('pilot rows', len(rows), 'chosen hits', sum(1 for _ in PILOT_FIND))
    with open(f'{wd}/inputs.jsonl', 'w', encoding='utf-8') as o:
        for r in rows: o.write(json.dumps(r, ensure_ascii=False) + '\n')

def req_body(text, system, title=None):
    return {'model': MODEL, 'max_tokens': 400, 'thinking': {'type': 'disabled' if 'haiku' in MODEL else 'between_tools'},
            'system': [{'type': 'text', 'text': system, 'cache_control': {'type': 'ephemeral', 'ttl': '1h'}}],
            'messages': [{'role': 'user', 'content': (f'Title: {title}\n\n' if title else '') + text[:3000]}]}

def call(path, body=None, method=None):
    h = {'x-api-key': os.environ['ANTHROPIC_API_KEY'], 'anthropic-version': '2023-06-01', 'content-type': 'application/json'}
    rq = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, headers=h, method=method)
    for a in range(8):
        try:
            return json.load(urllib.request.urlopen(rq, timeout=300))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 529) and a < 7: time.sleep(2 ** a); continue
            raise RuntimeError(f'{e.code} {e.read()[:300]}')
        except Exception:
            if a == 7: raise
            time.sleep(2 ** a)

WIKI_HOST = {'dc': 'dc.fandom.com', 'marvel': 'marvel.fandom.com', 'dragon-ball-z': 'dragonball.fandom.com', 'fist-of-the-north-star': 'hokuto.fandom.com',
              'jojo-s-bizarre-adventure': 'jojo.fandom.com'}

def cmd_fetch(wd, specs):
    """specs: wiki=Title,... ; fetches section 0 of each page live and appends it to inputs.jsonl with id wiki|t:Title."""
    import urllib.parse, html
    with open(f'{wd}/inputs.jsonl', 'a', encoding='utf-8') as o:
        for sp in specs:
            w, t = sp.split('=', 1)
            u = f"https://{WIKI_HOST[w]}/api.php?action=parse&page={urllib.parse.quote(t)}&prop=text&section=0&format=json&redirects=1"
            rq = urllib.request.Request(u, headers={'User-Agent': 'DiaithirAssay/1.0 (+https://github.com/GeddyLifeson)'})
            j = json.load(urllib.request.urlopen(rq, timeout=60))
            if 'parse' not in j: print('MISS', w, t, str(j)[:120]); continue
            h = j['parse']['text']['*']
            h = re.sub(r'<(script|style|aside|table)\b.*?</\1>', ' ', h, flags=re.S)
            tx = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h))).strip()
            o.write(json.dumps({'id': f'{w}|t:{t}', 'title': t, 'text': tx[:2500]}, ensure_ascii=False) + '\n'); print(w, t, len(tx))

def cmd_sync(wd, n):
    system = system_prompt()
    rows = [json.loads(l) for l in open(f'{wd}/inputs.jsonl', encoding='utf-8')][:n]
    lock = threading.Lock(); out = open(f'{wd}/results_sync.jsonl', 'w', encoding='utf-8')
    def one(r):
        try:
            m = call('/messages', req_body(r['text'], system, r.get('title')))
            rec = {'id': r['id'], 'text': m['content'][0]['text'] if m['content'] else '', 'usage': m['usage']}
        except Exception as e:
            rec = {'id': r['id'], 'error': str(e)[:300]}
        with lock: out.write(json.dumps(rec, ensure_ascii=False) + '\n'); out.flush()
    with ThreadPoolExecutor(12) as ex: list(ex.map(one, rows))

def cmd_submit(wd):
    system = system_prompt()
    rows = [json.loads(l) for l in open(f'{wd}/inputs.jsonl', encoding='utf-8')]
    bf = f'{wd}/batches.json'
    done = json.load(open(bf)) if os.path.exists(bf) else []
    have = {b['n0'] for b in done}
    for s in range(0, len(rows), 5000):
        if s in have: continue
        ch = rows[s:s + 5000]
        reqs = [{'custom_id': f'r{s + k}', 'params': req_body(r['text'], system, r.get('title'))} for k, r in enumerate(ch)]
        b = call('/messages/batches', {'requests': reqs})
        done.append({'n0': s, 'n': len(ch), 'batch': b['id']})
        json.dump(done, open(bf, 'w'))
        print('submitted', s, b['id'], flush=True)

def parse(text):
    m = re.search(r'\{.*\}', text, re.S)
    return json.loads(m.group(0)) if m else None

def validate(text_src, obj, pool_ids):
    if not isinstance(obj, dict) or obj.get('b') not in (0, 1, 2): return None, 'shape'
    if obj['b'] == 0: return {'b': 0}, ''
    ps, bad = [], 0
    if obj['b'] == 2:
        try: m = int(obj['m']); assert 1 <= m <= 10 and obj['k'] in ('weapon', 'armor', 'vehicle')
        except Exception: return None, 'shape'
        q = obj.get('q') or ''
        obj['p'] = obj.get('p') or []
    for p in obj.get('p', [])[:8]:
        try:
            ok = p['id'] in pool_ids and 1 <= int(p['m']) <= 10 and p.get('q') and p['q'] in text_src and p.get('c') in ('h', 'm', 'l')
        except Exception: ok = False
        if ok: ps.append({'id': p['id'], 'm': int(p['m']), 'q': p['q'], 'c': p['c']})
        else: bad += 1
    extra = {'k': obj['k'], 'm': m, 'q': q if q in text_src else '', 'c': obj.get('c', 'l')} if obj['b'] == 2 else {}
    return {'b': obj['b'], **extra, 'n': str(obj.get('n', ''))[:80], 'p': ps, 'x': [str(x)[:40] for x in obj.get('x', [])][:8], 'dropped': bad}, ''

def cmd_collect(wd):
    rows = [json.loads(l) for l in open(f'{wd}/inputs.jsonl', encoding='utf-8')]
    ids = {r['id'] for r in pool_rows()}
    res = {}
    rf = f'{wd}/results.jsonl'
    if os.path.exists(rf):
        for l in open(rf, encoding='utf-8'): d = json.loads(l); res[d['id']] = d
    tot = {'input_tokens': 0, 'output_tokens': 0, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0}
    pend = 0
    bl = json.load(open(f'{wd}/batches.json'))
    for b in bl:
        st = call(f"/messages/batches/{b['batch']}")
        if st['processing_status'] != 'ended': pend += 1; continue
        if b.get('collected'): continue
        rq = urllib.request.Request(st['results_url'], headers={'x-api-key': os.environ['ANTHROPIC_API_KEY'], 'anthropic-version': '2023-06-01'})
        for l in urllib.request.urlopen(rq, timeout=600):
            d = json.loads(l); k = int(d['custom_id'][1:]); src = rows[k]
            if d['result']['type'] != 'succeeded': res[src['id']] = {'id': src['id'], 'error': d['result']['type']}; continue
            m = d['result']['message']; u = m['usage']
            for t in tot: tot[t] += u.get(t) or 0
            txt = m['content'][0]['text'] if m['content'] else ''
            try: v, why = validate(src['text'], parse(txt), ids)
            except Exception: v, why = None, 'parse'
            res[src['id']] = {'id': src['id'], **(v or {'error': why or 'parse'})}
        b['collected'] = True
        json.dump(bl, open(f'{wd}/batches.json', 'w'))
    with open(rf, 'w', encoding='utf-8') as o:
        for d in res.values(): o.write(json.dumps(d, ensure_ascii=False) + '\n')
    print('results', len(res), 'batches pending', pend, 'usage', tot)

def pool_rows(): return pool()

def cmd_tsv(wd, out):
    with open(out, 'w', encoding='utf-8', newline='') as o:
        w = csv.writer(o, delimiter='\t', lineterminator='\n')
        w.writerow(['source_wiki', 'lead_idx', 'kind', 'item_magnitude', 'name_in_text', 'power', 'magnitude', 'confidence', 'quote', 'missing_powers'])
        for l in open(f'{wd}/results.jsonl', encoding='utf-8'):
            d = json.loads(l)
            if d.get('b') not in (1, 2): continue
            wk, i = d['id'].split('|')
            for p in d['p'] or [{'id': '', 'm': '', 'c': '', 'q': ''}]:
                w.writerow([wk, i, d.get('k', 'being'), d.get('m', ''), d['n'], p['id'], p['m'], p['c'], p['q'], ','.join(d['x'])])

if __name__ == '__main__':
    c, wd = sys.argv[1], sys.argv[2]
    if c == 'build': cmd_build(wd, '--pilot' in sys.argv)
    elif c == 'fetch': cmd_fetch(wd, sys.argv[3:])
    elif c == 'sync': cmd_sync(wd, int(sys.argv[3]) if len(sys.argv) > 3 else 10**9)
    elif c == 'submit': cmd_submit(wd)
    elif c == 'collect': cmd_collect(wd)
    elif c == 'tsv': cmd_tsv(wd, sys.argv[3])
