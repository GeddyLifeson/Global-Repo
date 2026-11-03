# S0317 One direct cached Claude call per culture language: researches how a linguist builds words there, writes names/linguistics/rules/<slug>.json (24 concurrent, no Batch).
# python3 -I research_rules.py [slug ...]   key from ANTHROPIC_API_KEY (never printed)
import csv, json, os, re, sys, time, urllib.request, concurrent.futures as cf
ROOT = '/mnt/project-files/names'
OUT = ROOT + '/linguistics/rules'
MODEL = 'claude-sonnet-5-5'
KEY = os.environ['ANTHROPIC_API_KEY']
slug = lambda u: re.sub(r'[^a-z0-9]+', '_', u.lower()).strip('_')

SYSTEM = """You are a historical linguist advising a game studio that names objects (foods, tools, places, gods, ships, buildings) in 130 culture languages, ranging from Pleistocene archaeological cultures to historical states. Players read each name as the language of that culture. Names must be built the way a specialist in that language would build them, not as random syllables.

For the given culture, do this:
1. Identify the best-supported linguistic proxy. If the culture's language is attested, use it. If it is known only archaeologically, use the most defensible proto-language or language family for that region and period, and say how weak the link is (confidence: high, medium, low, speculative). Never invent a language and present it as attested.
2. Describe, from the real literature, how words are built: phoneme inventory, phonotactics (allowed syllable shapes, clusters, word-final restrictions, stress or tone effects on spelling), orthography (use a standard scholarly transliteration of the language, or the standard reconstruction notation such as Proto-Indo-European laryngeals, Sumerian sign-values, Egyptian transliteration), morphology (root types, affixation, reduplication, noun classes, case), compounding and derivation (head position, linkers, genitive constructions, how 'X of Y' and 'Y-maker' type names are formed), and word order inside noun phrases.
3. Give 10 to 16 real, well-attested roots or words with glosses that a name builder could use as models (only ones you are confident are real; mark anything reconstructed with an asterisk).
4. Give 6 worked pattern examples: an English concept such as 'River Stew' or 'Temple of the Sun' to the name, with a morpheme-by-morpheme gloss that follows the rules.
5. Give machine-checkable constraints for an automatic audit of names written in Latin script: the allowed graphemes (multi-letter units included), characters allowed besides letters (space, hyphen, apostrophe, diacritics), forbidden letter or sequence patterns as regular expressions applied to the lowercase name (Python re syntax), the typical syllable count range per word, and the maximum word length.
6. List the main scholarly sources (author, work, year). Only cite works that exist and that you are confident about; if unsure, name the standard reference grammar, dictionary or reconstruction project (for example Wiktionary reconstruction pages, Starling database, ASJP, Glottolog, eDIL, Pokorny, Allan, Hoffner and Melchert) rather than guess a page.
7. Add a Diaithiris-specific note only if the culture is the Diaithiris. Otherwise state that no word may be identical to a Modern Irish, Scottish Gaelic or Manx word unless the language is Goidelic.

Be accurate and concise. Mark uncertainty honestly. Output only the JSON object that matches the schema."""

STR = {'type': 'string'}
ARR = {'type': 'array', 'items': STR}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'required': [
    'proxy_language', 'confidence', 'proxy_rationale', 'phonology', 'phonotactics', 'orthography', 'morphology',
    'compounding', 'noun_phrase_order', 'attested_roots', 'worked_examples', 'allowed_graphemes', 'extra_allowed_chars',
    'forbidden_patterns', 'syllables_per_word', 'max_word_length', 'sources', 'notes'], 'properties': {
    'proxy_language': STR, 'confidence': {'type': 'string', 'enum': ['high', 'medium', 'low', 'speculative']},
    'proxy_rationale': STR, 'phonology': STR, 'phonotactics': STR, 'orthography': STR, 'morphology': STR,
    'compounding': STR, 'noun_phrase_order': STR,
    'attested_roots': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['form', 'gloss', 'reconstructed'], 'properties': {'form': STR, 'gloss': STR, 'reconstructed': {'type': 'boolean'}}}},
    'worked_examples': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False, 'required': ['english', 'name', 'gloss'], 'properties': {'english': STR, 'name': STR, 'gloss': STR}}},
    'allowed_graphemes': ARR, 'extra_allowed_chars': STR, 'forbidden_patterns': ARR,
    'syllables_per_word': {'type': 'array', 'items': {'type': 'integer'}}, 'max_word_length': {'type': 'integer'},
    'sources': ARR, 'notes': STR}}

def call(row, samples):
    user = (f"Culture: {row['unit']}\nKind: {row['kind']}\nAge/period index: {row['age']}\nRegion: {row['region']}\n"
            f"Slug: {slug(row['unit'])}\nCurrent game names for this culture (probably not linguistically sound; use only to see what kind of strings exist): {samples}")
    body = {'model': MODEL, 'max_tokens': 6000, 'thinking': {'type': 'between_tools'},
            'system': [{'type': 'text', 'text': SYSTEM, 'cache_control': {'type': 'ephemeral', 'ttl': '1h'}}],
            'messages': [{'role': 'user', 'content': user}],
            'output_config': {'format': {'type': 'json_schema', 'schema': SCHEMA}}}
    req = urllib.request.Request('https://api.anthropic.com/v1/messages', json.dumps(body).encode(), {
        'x-api-key': KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    for a in range(3):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=180))
            return json.loads(next(b['text'] for b in r['content'] if b['type']=='text')), r['usage']
        except Exception as e:
            err = str(e)
            time.sleep(4 * (a + 1))
    raise RuntimeError(err)

def main():
    rows = list(csv.DictReader(open('/mnt/attach/project-files/cultures/MASTER_CULTURES.csv')))
    want = set(sys.argv[1:])
    dish = json.load(open(ROOT + '/dishes.json'))
    ex = {}
    for k, v in list(dish.items())[:6]:
        for s, n in v.items():
            ex.setdefault(s, []).append(n)
    todo = [r for r in rows if (not want or slug(r['unit']) in want) and not os.path.exists(f"{OUT}/{slug(r['unit'])}.json")]
    def one(r):
        s = slug(r['unit'])
        d, u = call(r, '; '.join(ex.get(s, [])[:6]))
        d.update(unit=r['unit'], slug=s, model=MODEL)
        json.dump(d, open(f'{OUT}/{s}.json', 'w'), ensure_ascii=False, indent=1)
        open(ROOT + '/../compute/ledger.csv', 'a').write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())},name-linguistics,{MODEL},{u.get('input_tokens')},{u.get('output_tokens')},{u.get('cache_creation_input_tokens')},{u.get('cache_read_input_tokens')}\n")
        return s
    with cf.ThreadPoolExecutor(24) as ex_:
        futs = {ex_.submit(one, r): r for r in todo}
        for f in cf.as_completed(futs):
            try: print('ok', f.result(), flush=True)
            except Exception as e: print('FAIL', slug(futs[f]['unit']), e, flush=True)
main()
