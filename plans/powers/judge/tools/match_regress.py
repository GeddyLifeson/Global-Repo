#!/usr/bin/env python3
"""Regression gate for pages.match (review A15). Run before ANY change to pages.match/_match/_inpage/_wmatch:
  python3 tools/match_regress.py        check: known-wrong pairs rejected, frozen known-right pairs accepted, sibling false-accepts <= baseline
  python3 tools/match_regress.py init   (re)freeze match_regress.json from the current matcher: only after a reviewed change, logged in HOLDS.txt"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pages, judge
FIX = os.path.join(HERE, 'match_regress.json')
WRONG = [(88, 95, 'https://forgottenrealms.fandom.com/wiki/Mither_Mandaroze'), (89, 110, 'https://wowpedia.fandom.com/wiki/Mew'),
         (3, 125, 'https://halo.fandom.com/wiki/Colony')]  # known-wrong resolver picks named in HOLDS.txt
def lead(n, i): return judge.rows(n)[i]['text']
def page(u): return pages._packed().get(u, '')
def sample(seed=1, right=300, cross=3000):
    rnd = random.Random(seed); R, X = [], []; ns = sorted(int(os.path.basename(f).split('_')[1].split('.')[0]) for f in os.listdir(pages.B) if f.endswith('.src.jsonl'))
    for _ in range(40000):
        if len(R) >= right and len(X) >= cross: break
        n = rnd.choice(ns); S = pages.srcs(n); i = rnd.randrange(len(S))
        if not S[i]['url'] or not page(S[i]['url']): continue
        if len(R) < right: R.append([n, i, S[i]['url']])
        j = rnd.randrange(len(S))
        if j != i and S[j]['url'] and S[j]['url'] != S[i]['url'] and page(S[j]['url']) and len(X) < cross: X.append([n, i, S[j]['url']])
    return R, X
def run(R, X):
    wrong = [w for w in WRONG if page(w[2]) and pages.match(lead(w[0], w[1]), page(w[2]))]
    miss = [r for r in R if not pages.match(lead(r[0], r[1]), page(r[2]))]
    fa = sum(pages.match(lead(a, b), page(u)) for a, b, u in X)
    return wrong, miss, fa
if __name__ == '__main__':
    if sys.argv[1:] == ['init']:
        R, X = sample(); R = [r for r in R if pages.match(lead(r[0], r[1]), page(r[2]))]
        json.dump({'right': R, 'cross': X, 'baseline_false_accepts': run(R, X)[2]}, open(FIX, 'w')); print('frozen', len(R), 'right,', len(X), 'cross'); sys.exit(0)
    F = json.load(open(FIX)); wrong, miss, fa = run(F['right'], F['cross'])
    print(f"known-wrong accepted: {wrong}\nknown-right rejected: {len(miss)}/{len(F['right'])}\nsibling false accepts: {fa} (baseline {F['baseline_false_accepts']})")
    sys.exit(1 if wrong or miss or fa > F['baseline_false_accepts'] else 0)
