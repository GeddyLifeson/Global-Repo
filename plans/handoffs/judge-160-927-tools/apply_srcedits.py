#!/usr/bin/env python3
"""Apply `SRCEDIT shard=N row=(id X) old=(blank) new=URL` lines from HOLDS.txt to batches/shard_N.src.jsonl.
Run from plans/powers/judge after merging the pipeline branch, before validate.py. Idempotent; refuses non-blank old."""
import json, re, sys
for n, i, u in re.findall(r'(?m)^SRCEDIT shard=(\d+) row=\(id (\S+)\) old=\(blank\) new=(\S+)', open('HOLDS.txt', encoding='utf-8').read()):
    p = f'batches/shard_{n}.src.jsonl'; rows = [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]
    hit = [r for r in rows if r['id'] == i]
    assert len(hit) == 1, (n, i)
    if hit[0]['url'] == u: continue
    assert not hit[0]['url'], (n, i, hit[0]['url'])
    hit[0]['url'] = u; hit[0]['title'] = u.rsplit('/', 1)[1].replace('_', ' ')
    open(p, 'w', encoding='utf-8').write(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows)); print('patched', n, i)
