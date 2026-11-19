#!/usr/bin/env python3
"""For rows an out file marks 'no source page', try every title candidate (pages.cands) on every host of the row's wiki; keep a page only when pages.match(row text, page text) accepts it.
  resolve_nosrc.py OUT.json N [N ...]   writes {shard: {row: [url, title]}} to OUT.json"""
import sys, os, json, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pages, judge
res = {}
for n in sys.argv[2:]:
    R = judge.rows(int(n)); O = [json.loads(l) for l in open(f'{judge.O}shard_{n}.out.jsonl', encoding='utf-8')]; res[n] = {}
    for i, (o, r) in enumerate(zip(O, R)):
        if not o.get('z', '').startswith('no source page:'): continue
        hit = None
        for h in pages.HOSTS.get(r['id'].rsplit('|', 1)[0], []):
            for c in pages.cands(r['text'])[:6]:
                try: t = pages.full_extract(h, c)
                except Exception: continue
                if t and pages.match(r['text'], t): hit = (f"https://{h}/wiki/" + urllib.parse.quote(c.replace(' ', '_')), c); break
            if hit: break
        if hit: res[n][i] = hit
    json.dump(res, open(sys.argv[1], 'w'), ensure_ascii=False)
