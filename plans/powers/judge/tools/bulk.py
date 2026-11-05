#!/usr/bin/env python3
"""Bulk-download source pages (no model tokens). bulk.py A B [workers]: for shards A..B-1 copy batch, resolve rows to pages,
fetch full text, write cache/shard_N.pages.json.gz ({url: text}). pages.text() reads this cache first."""
import time, sys, os, json, gzip, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages
from concurrent.futures import ThreadPoolExecutor
J = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OLD = '/mnt/project-files/plans/powers/judge/inthread/shard_%02d.jsonl'
def one(n):
    for k in range(5):
        try: return _one(n)
        except Exception as e: err = e; time.sleep(30)
    return n, f'FAILED {err!r}'
def _one(n):
    out = f'{J}/cache/shard_{n}.pages.json.gz'
    if os.path.exists(out): return n, 'cached'
    b = f'{J}/batches/shard_{n}.jsonl'
    if not os.path.exists(b):
        if not os.path.exists(OLD % n): return n, 'no input'
        shutil.copy(OLD % n, b)
    S = pages.srcs(n)
    urls = sorted({s['url'] for s in S if s['url']})
    T = {}
    for k, u in enumerate(urls):
        T[u] = pages.text(u)
        if k % 25 == 0: print(f'  fetch {n} {k}/{len(urls)}', file=sys.stderr, flush=True)
    os.makedirs(f'{J}/cache', exist_ok=True)
    with gzip.open(out, 'wt', encoding='utf-8') as f: json.dump(T, f, ensure_ascii=False)
    return n, f"{len(urls)} pages, {sum(1 for s in S if not s['url'])} unresolved"
if __name__ == '__main__':
    a, b = int(sys.argv[1]), int(sys.argv[2])
    with ThreadPoolExecutor(int(sys.argv[3]) if len(sys.argv) > 3 else 6) as ex:
        for n, r in ex.map(one, range(a, b)): print(n, r, flush=True)
