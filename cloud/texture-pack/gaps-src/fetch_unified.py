"""Resumable candidate search: for each dish, Haiku's queries against Commons and Openverse (cc0/pdm/by/by-sa). Appends one line per dish to CAND.jsonl.
    python3 fetch_unified.py QUERIES_OUT.jsonl CAND.jsonl [workers]"""
import json, sys, os, re, time, threading, concurrent.futures as cf
sys.path.insert(0, '/home/user/work/photo')
import fetch_candidates as fc, fetch_more as fm
qs = {}
for l in open(sys.argv[1]):
    r = json.loads(l)
    try: j = json.loads(re.search(r'\{.*\}', r['text'], re.S).group(0)); qs[r['id']] = ([q for q in j.get('queries', []) if q], j.get('real', True))
    except Exception: pass
out = sys.argv[2]; done = set()
if os.path.exists(out): done = {json.loads(l)['id'] for l in open(out)}
lock = threading.Lock()
def work(n):
    q, real = qs[n]
    if not q: q = [n.replace('_', ' ')]
    try:
        have = []
        for x in q[:2]:
            have += [c for c in fc.find(x)[1] if all(c['title'] != h['title'] for h in have)][:3]
        _, allc = fm.more((n, q, have))
    except Exception: allc = []
    with lock: open(out, 'a').write(json.dumps({'id': n, 'real': real, 'cand': allc}) + '\n')
todo = [n for n in qs if n not in done]
with cf.ThreadPoolExecutor(int(sys.argv[3]) if len(sys.argv) > 3 else 6) as ex: list(ex.map(work, todo))
print('done', len(todo))
