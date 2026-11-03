# S6831 Names for a {id: English} file in all 130 culture languages, built against each language's rules file (Haiku, cached; 5 repair rounds, then relaxed fallback on spelling patterns).
# python3 -I names_for_terms.py TERMS.json OUT.json   key from ANTHROPIC_API_KEY (never printed)
import json, os, sys, threading, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.dirname(os.path.abspath(__file__)) + '/regen_relaxed.py').read()
exec(src[:src.index('def main')])
terms = json.load(open(sys.argv[1])); slugs = sorted(A.rules)
uniq = sorted(set(terms.values())); res = {s: {} for s in slugs}; last = {s: {} for s in slugs}; lock = threading.Lock()
rules = {s: open(f'{R}/linguistics/rules/{s}.json').read() for s in slugs}
hard = {}
for s in slugs:
    d = json.load(open(f'{R}/linguistics/rules/{s}.json'))
    hard[s] = 'HARD CONSTRAINTS: spell names ONLY with these letters/graphemes: ' + ' '.join(d['allowed_graphemes']) + ' (plus space, hyphen, apostrophe, ' + d['extra_allowed_chars'] + '). Any other letter or diacritic is rejected; transliterate with these. Avoid these regex patterns on the lowercase name: ' + ' | '.join(d['forbidden_patterns']) + f". Max word length {d['max_word_length']}.\n\nTerms:\n"
def job(s, ch):
    got = call(rules[s], ch, hard[s], last[s])
    with lock:
        for i, t in ch:
            nm = got.get(i)
            if nm:
                r = A.check(s, nm)
                if not r: res[s][t] = nm
                else: last[s][t] = (nm, r[:2])
for rnd in range(5):
    jobs = [(s, list(enumerate([t for t in uniq if t not in res[s]][k:k + 120]))) for s in slugs for k in range(0, len([t for t in uniq if t not in res[s]]), 120)]
    if not jobs: break
    with cf.ThreadPoolExecutor(96) as ex: list(ex.map(lambda a: job(*a), jobs))
for s in slugs:
    for t, (nm, r) in last[s].items():
        if t not in res[s] and not any(x.startswith(('char:', 'long:')) for x in r): res[s][t] = nm
out = {i: dict([('en', e)] + [(s, res[s][e]) for s in slugs if e in res[s]]) for i, e in terms.items()}
json.dump(out, open(sys.argv[2], 'w'), ensure_ascii=False)
print(sum(len(v) - 1 for v in out.values()), len(terms) * len(slugs))
