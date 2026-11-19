#!/usr/bin/env python3
"""Rows whose judged u/t differ from the resolver's current src url: when both pages match the batch lead and every quote is verbatim in the resolver's page, repoint u/t to the resolver's page.
  repoint_src.py N [N ...]   edits out/shard_N.out.jsonl; prints rows left for re-judging"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pages, judge, validate
sq = validate.squash
def quotes(o): return [x.get('q', '') for x in o.get('p', [])] + [f.get('q', '') for f in o.get('f', [])] + ([o['q']] if o.get('b') == 2 else [])
for n in sys.argv[1:]:
    p = f'{judge.O}shard_{n}.out.jsonl'; out = [json.loads(l) for l in open(p, encoding='utf-8')]
    R = judge.rows(int(n)); S = pages.srcs(n); ch = 0
    for i, (o, r, s) in enumerate(zip(out, R, S)):
        if not o.get('u') or not s['url'] or (o['u'] == s['url'] and o.get('t') == s['title']): continue
        T = pages.text(s['url'])
        if T and pages.match(r['text'], T) and all(sq(q) in sq(T) for q in quotes(o)):
            o['u'], o['t'] = s['url'], s['title']; ch += 1
        else: print(f'shard {n} row {i}: re-judge (quotes/lead not on resolver page {s["url"][-40:]})')
    open(p, 'w', encoding='utf-8').write(''.join(json.dumps(o, ensure_ascii=False) + '\n' for o in out))
    if ch: print(f'shard {n}: repointed {ch}')
