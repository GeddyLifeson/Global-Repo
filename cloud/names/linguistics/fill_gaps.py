# S6833 Fills empty language slots in a names_for_terms output: 6 repair rounds with rejection feedback, then relaxed fallbacks (spelling patterns, then diacritics stripped). Rewrites OUT in place.
# python3 -I fill_gaps.py TERMS.json OUT.json   key from ANTHROPIC_API_KEY (never printed)
import json, os, sys, threading, unicodedata, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.dirname(os.path.abspath(__file__)) + '/regen_relaxed.py').read()
exec(src[:src.index('def main')])
terms = json.load(open(sys.argv[1])); out = json.load(open(sys.argv[2])); slugs = sorted(A.rules)
rules = {s: open(f'{R}/linguistics/rules/{s}.json').read() for s in slugs}; hard = {}
for s in slugs:
    d = json.load(open(f'{R}/linguistics/rules/{s}.json'))
    hard[s] = 'HARD CONSTRAINTS: spell names ONLY with these letters/graphemes: ' + ' '.join(d['allowed_graphemes']) + ' (plus space, hyphen, apostrophe, ' + d['extra_allowed_chars'] + '). Any other letter or diacritic is rejected; use plain letters only. Avoid these regex patterns on the lowercase name: ' + ' | '.join(d['forbidden_patterns']) + f". Max word length {d['max_word_length']}.\n\nTerms:\n"
res = {s: {} for s in slugs}; last = {s: {} for s in slugs}; lock = threading.Lock()
for i, e in terms.items():
    for s in slugs:
        if s in out.get(i, {}): res[s][e] = out[i][s]
uniq = sorted(set(terms.values()))
def job(s, ch):
    got = call(rules[s], ch, hard[s], last[s])
    with lock:
        for i, t in ch:
            nm = got.get(i)
            if nm:
                r = A.check(s, nm)
                if not r: res[s][t] = nm
                else: last[s][t] = (nm, r[:2])
for rnd in range(6):
    jobs = []
    for s in slugs:
        pend = [t for t in uniq if t not in res[s]]
        jobs += [(s, list(enumerate(pend[k:k + 60]))) for k in range(0, len(pend), 60)]
    print('round', rnd, len(jobs), flush=True)
    if not jobs: break
    with cf.ThreadPoolExecutor(64) as ex: list(ex.map(lambda a: job(*a), jobs))
def strip(n): return ''.join(c for c in unicodedata.normalize('NFD', n) if not unicodedata.combining(c))
for s in slugs:
    for t, (nm, r) in last[s].items():
        if t in res[s]: continue
        if not any(x.startswith(('char:', 'long:')) for x in r): res[s][t] = nm
        elif not [x for x in A.check(s, strip(nm)) if x.startswith(('char:', 'long:'))]: res[s][t] = strip(nm)
for i, e in terms.items():
    d = out.setdefault(i, {'en': e})
    for s in slugs:
        if e in res[s]: d[s] = res[s][e]
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False)
print(sum(len(v) - 1 for v in out.values()), len(terms) * len(slugs))
