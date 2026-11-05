"""Split-judging helpers (no network, cache only).
split.py ranges N [chars=160000]  -> idx ranges, ~chars of page text each (~40k tokens)
split.py dump N lo hi             -> FULL text of rows lo..hi-1 (idx|title|lead, then page text)
split.py check N lo hi part.json  -> verify a part config: idx in range, quotes verbatim
split.py merge N part.json...     -> union parts (d=0) and run judge.py write N (validates)"""
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
import pages, judge
def load(n):
    R, S = judge.rows(n), pages.srcs(n)
    return R, S, [(pages.text(S[i]['url']) or R[i]['text']) if S[i]['url'] else R[i]['text'] for i in range(len(R))]
def main(a):
    c, n = a[0], int(a[1]); R, S, T = load(n)
    if c == 'ranges':
        lim = int(a[2]) if len(a) > 2 else 160000; out, lo, acc = [], 0, 0
        for i, t in enumerate(T):
            if acc and acc + len(t) > lim: out.append((lo, i)); lo, acc = i, 0
            acc += len(t)
        out.append((lo, len(T)))
        if len(out) > 1 and out[-1][1] - out[-1][0] < 20: out[-2:] = [(out[-2][0], out[-1][1])]
        print(json.dumps(out))
    elif c == 'dump':
        for i in range(int(a[2]), int(a[3])): print(f"#### {i}|{S[i]['title'] or 'NO-SOURCE'}|{R[i]['id']}\nLEAD: {R[i]['text'][:200]}\nTEXT: {T[i]}\n")
    elif c == 'check':
        lo, hi, cfg = int(a[2]), int(a[3]), json.load(open(a[4])); bad = []
        for k in ('n', 'p', 'W', 'x', 'f', 'z', 's', 'u0'):
            for i, v in cfg.get(k, {}).items():
                i = int(i)
                if not lo <= i < hi: bad.append((k, i, 'outside range')); continue
                qs = [q[2] for q in v] if k == 'p' else [v[3]] if k == 'W' else [q[1] for q in v] if k == 'f' else []
                for q in qs:
                    if not judge.inq(q, T[i]): bad.append((k, i, 'quote not verbatim: ' + q[:40]))
        bad += [('b1', i, 'outside range') for i in cfg.get('b1', []) if not lo <= i < hi]
        print('OK' if not bad else bad)
    elif c == 'merge':
        m = {'d': 0, 'b1': [], 'auto': 0}
        for f in a[2:]:
            p = json.load(open(f)); m['b1'] += p.get('b1', []); m['auto'] |= p.get('auto', 0)
            for k, v in p.items():
                if isinstance(v, dict): m.setdefault(k, {}).update(v)
        judge.write(n, m)
main(sys.argv[1:])
