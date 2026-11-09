# S6978 Runs the S6975 judge prompt over a page queue on OpenAI-compatible endpoints (model router, Ollama), resumable, validated, optional git push.
"""python judge_pc.py QUEUE.jsonl[.gz] OUT.jsonl EP [EP ...] [--push N]
EP = name=http://host:port/v1,model[,workers]   e.g.  router=http://127.0.0.1:8788/v1,auto,8   ollama=http://127.0.0.1:11434/v1,gpt-oss:20b,1
Each endpoint pulls pages from one shared queue. Results use the judge_pages format; ids already in OUT are skipped, so rerun to resume.
Rows failing JSON/validation are kept as {"id","error"} and retried once on the next endpoint. --push N commits and pushes OUT every N results."""
import json, sys, os, gzip, csv, time, threading, queue, subprocess, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import judge_pages as jp

def post(url, model, system, text, key):
    body = {'model': model, 'temperature': 0, 'max_tokens': 500,
            'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': text[:2500]}]}
    h = {'content-type': 'application/json', 'authorization': 'Bearer ' + key}
    rq = urllib.request.Request(url + '/chat/completions', data=json.dumps(body).encode(), headers=h)
    return json.load(urllib.request.urlopen(rq, timeout=300))['choices'][0]['message']['content'] or ''

def main():
    a = sys.argv[1:]; push = 0
    if '--push' in a: k = a.index('--push'); push = int(a[k + 1]); del a[k:k + 2]
    qf, of, eps = a[0], a[1], a[2:]
    system = jp.system_prompt(); ids = {r['id'] for r in jp.pool_rows()}
    op = gzip.open if qf.endswith('.gz') else open
    rows = [json.loads(l) for l in op(qf, 'rt', encoding='utf-8')]
    done = set()
    if os.path.exists(of):
        for l in open(of, encoding='utf-8'):
            d = json.loads(l)
            if 'error' not in d: done.add(d['id'])
    q = queue.Queue()
    for r in rows:
        if r['id'] not in done: q.put((r, 0))
    print('queue', q.qsize(), 'already done', len(done), flush=True)
    lock = threading.Lock(); out = open(of, 'a', encoding='utf-8'); n = [0]; key = os.environ.get('JUDGE_KEY', 'x')

    def flush_push():
        out.flush()
        subprocess.run(['git', 'add', of], check=False); subprocess.run(['git', 'commit', '-qm', 'PC judge results'], check=False)
        subprocess.run(['git', 'push', '-q'], check=False)

    def work(name, url, model):
        while True:
            try: r, tries = q.get_nowait()
            except queue.Empty: return
            try:
                v, why = jp.validate(r['text'], jp.parse(post(url, model, system, r['text'], key)), ids)
                rec = {'id': r['id'], **v} if v else None
                if rec: rec['by'] = name
            except Exception as e:
                rec, why = None, str(e)[:120]
            if rec is None:
                if tries < 2: q.put((r, tries + 1)); time.sleep(1); continue
                rec = {'id': r['id'], 'error': why or 'parse', 'by': name}
            with lock:
                out.write(json.dumps(rec, ensure_ascii=False) + '\n'); n[0] += 1
                if n[0] % 100 == 0: out.flush(); print(n[0], 'done', flush=True)
                if push and n[0] % push == 0: flush_push()

    ts = []
    for e in eps:
        name, rest = e.split('=', 1); p = rest.split(',')
        for _ in range(int(p[2]) if len(p) > 2 else 4):
            t = threading.Thread(target=work, args=(name, p[0], p[1])); t.start(); ts.append(t)
    for t in ts: t.join()
    flush_push() if push else out.flush()
    print('finished', n[0])

if __name__ == '__main__': main()
