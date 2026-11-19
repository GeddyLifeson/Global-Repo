#!/usr/bin/env python3
"""Lengthen power/gear quotes under MINQ chars to the full page line (or sentence) that contains them, verbatim from the cached page.
  lengthen_quotes.py N [N ...] | all     edits out/shard_N.out.jsonl in place; prints rows it could not fix"""
import sys, os, re, json, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pages, judge, validate
sq = validate.squash; MINQ = validate.MINQ; MAXQ = 200
def expand(q, text):
    q = sq(q); lines = [sq(l) for l in text.split('\n')]; lines = [l for l in lines if l]
    best = None
    for i, l in enumerate(lines):
        m = re.search(r'(?<![A-Za-z])' + re.escape(q) + r'(?![A-Za-z])', l, re.I)
        if not m: continue
        cand = l
        if len(l) > MAXQ:  # long line: sentence around the hit
            s = max(l.rfind('. ', 0, m.start()) + 2, 0); e = l.find('. ', m.end()); e = len(l) if e < 0 else e + 1
            cand = l[s:e].strip()
            if len(cand) > MAXQ: cand = l[max(0, m.start() - 60):m.end() + 100]; cand = cand[cand.find(' ') + 1:] if m.start() > 60 else cand
        elif len(l) < MINQ:  # bare bullet: add the following line, else the preceding one
            H = lambda x: x.startswith('=')
            nxt = lines[i + 1] if i + 1 < len(lines) and not H(lines[i + 1]) else ''
            prv = lines[i - 1] if i else ''
            cand = f'{prv} {l}' if prv and H(prv) else f'{l} {nxt}' if nxt else f'{prv} {l}'
        if len(cand) >= MINQ and sq(cand) in sq(text) and (best is None or len(cand) < len(best)): best = cand
    return best
def fix(n):
    p = f'{judge.O}shard_{n}.out.jsonl'; out = [json.loads(l) for l in open(p, encoding='utf-8')]; bad = []; ch = 0
    for i, o in enumerate(out):
        if not o.get('u') or o.get('b') not in (1, 2): continue
        items = o.get('p', []) if o['b'] == 1 else [o]
        if not any(len(sq(x.get('q', ''))) < MINQ for x in items): continue
        t = pages.text(o['u'])
        for x in items:
            if len(sq(x.get('q', ''))) < MINQ:
                nq = expand(x.get('q', ''), t) if t and x.get('q') else None
                if nq: x['q'] = nq; ch += 1
                else: bad.append((i, x.get('q')))
    open(p, 'w', encoding='utf-8').write(''.join(json.dumps(o, ensure_ascii=False) + '\n' for o in out))
    return ch, bad
if __name__ == '__main__':
    a = sys.argv[1:]
    ns = sorted(int(re.search(r'shard_(\d+)\.out', f).group(1)) for f in glob.glob(f'{judge.O}shard_*.out.jsonl')) if a == ['all'] else a
    for n in ns:
        ch, bad = fix(n)
        if ch or bad: print(f'shard {n}: lengthened {ch}, unfixed {bad}')
