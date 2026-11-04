#!/usr/bin/env python3
"""Judge-thread helper (S6975 companion). One command each: show, write. See ../PLAYBOOK.md.
  judge.py show N [START END]        compact page print: idx | head | power/scale evidence sentences
  judge.py write N 'JSON'            validate + write shard_NN.out.jsonl (nothing else needed)
"""
import json, re, sys, csv, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pages
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, '..', 'batches') + '/'
O = os.path.join(HERE, '..', 'out') + '/'
POOLF = os.path.join(HERE, '..', '..', 'POWER_POOL.tsv')
SCALE = r'planet|stars?\b|galax|universe|continent|ocean|island|mountain|moon|city|cities|building|army|armies|tons?\b|kilomet|miles?\b|mach|light.?speed|destroy|shatter|devastat|invulnerab|immortal|indestructible|unstoppable|omnipot|godlike|supernatural|superhuman'
VAM = re.compile(r'\b(Lasombra|Gangrel|Nosferatu|Tremere|Ventrue|Toreador|Brujah|Malkavian|Tzimisce|Setite|Assamite|Cappadocian|Hecata|Giovanni|Banu Haqim|Samedi|vampire|Kindred|Followers? of Set|Caitiff|Cainite)\b')
def pool():
    return list(csv.DictReader(open(POOLF, encoding='utf-8'), delimiter='\t'))
def rows(n):
    return [json.loads(l) for l in open(f'{B}shard_{int(n)}.jsonl', encoding='utf-8')]
def kw():
    parts = [r['keywords_strong'] for r in pool() if r['keywords_strong']]
    out = []
    for p in parts:
        try: out.append(re.compile(p, re.I))
        except re.error: pass
    return out
def show(n, s=0, e=10**9):
    """idx|title|url-tail|lead ## evidence sentences from the FULL page (powers/abilities/scale)."""
    K = kw(); sc = re.compile(SCALE, re.I); R = rows(n); S = pages.srcs(n)
    idx = [i for i in range(len(R)) if s <= i < e]
    with ThreadPoolExecutor(6) as ex: full = dict(zip(idx, ex.map(lambda i: pages.text(S[i]['url']) or R[i]['text'], idx)))
    for i in idx:
        t = full[i].replace('\n', ' ')
        sents = re.split(r'(?<=[.!?]) ', t)
        ev = [x for x in sents[1:] if sc.search(x) or any(k.search(x) for k in K)]
        head = R[i]['text'].replace('\n', ' ')[:130]
        print(f"{i}|{S[i]['title'] or 'NO-SOURCE'}|{head}" + (f" ## {' '.join(ev)[:420]}" if ev else ''))
def write(n, cfg):
    """cfg keys: d (default 0|1; rows not listed get it), b0 [idx], b1 [idx], n {idx:name},
    p {idx:[[pool_id,mag,quote,conf]]}, W {idx:[kind,name,mag,quote,conf]} (weapon/armor/vehicle), x {idx:[..]}, auto 1 (vampirism/possession x)"""
    n = int(n); R = rows(n); S = pages.srcs(n); ids = {r['id'] for r in pool()}
    g = lambda k: {int(a): v for a, v in cfg.get(k, {}).items()}
    names, P, W, X, SM = g('n'), g('p'), g('W'), g('x'), g('s')
    first = lambda t: re.split(r'(?<=[.!?]) ', t.replace('\n', ' ').strip(), maxsplit=1)[0][:200]
    SM = {i: SM.get(i) or first(R[i]['text']) for i in range(len(R))}
    b0, b1, dflt = set(cfg.get('b0', [])), set(cfg.get('b1', [])), cfg.get('d', 0)
    out, err = [], []
    for i, r in enumerate(R):
        t = pages.text(S[i]['url']) or r['text']; o = {'id': r['id'], 'b': 0}
        if i in W:
            k, nm, m, q, c = W[i]
            if not S[i]['url']: err.append((i, 'no source page'))
            elif not SM.get(i): err.append((i, 'summary s required'))
            elif k in ('weapon', 'armor', 'vehicle') and 1 <= m <= 10 and q in t and (nm in t or nm == ''):
                o = {'id': r['id'], 'b': 2, 'k': k, 'n': nm, 'm': m, 'q': q, 'c': c, 'p': [], 'u': S[i]['url'], 's': SM[i]}
            else: err.append((i, 'W bad kind/mag/quote/name'))
        elif i in b1 or (dflt == 1 and i not in b0):
            if not S[i]['url']: err.append((i, 'no source page'))
            if not SM.get(i): err.append((i, 'summary s required'))
            if i in names: nm = names[i]
            elif re.match(r'(is|was|are|were|This)\b|[(,]', t): nm = ''
            else: nm = re.split(r' \(|, | (?:is|was|are|were) ', t, maxsplit=1)[0]
            if nm not in t or len(nm) >= 60: err.append((i, f'name not in text/too long: {nm[:40]!r} (set n)')); nm = ''
            ps = []
            for pid, m, q, c in P.get(i, []):
                if pid in ids and 1 <= m <= 10 and q in t and c in ('h', 'm', 'l'): ps.append({'id': pid, 'm': m, 'q': q, 'c': c})
                else: err.append((i, f'power dropped {pid} {q[:30]!r}'))
            x = list(X.get(i, []))
            if cfg.get('auto'):
                if VAM.search(t) and 'vampirism' not in x: x.append('vampirism')
                if 'possessing' in t and 'possession' not in x: x.append('possession')
            o = {'id': r['id'], 'b': 1, 'n': nm, 'p': ps, 'x': x, 'u': S[i]['url'], 's': SM.get(i, '')}
        o['u'] = S[i]['url']; o['t'] = S[i]['title']
        out.append(o)
    path = f'{O}shard_{n}.out.jsonl'
    open(path, 'w', encoding='utf-8').write(''.join(json.dumps(o, ensure_ascii=False) + '\n' for o in out))
    print(f"wrote {path}: {len(out)} rows, beings {sum(o['b']==1 for o in out)}, gear {sum(o['b']==2 for o in out)}, powers {sum(len(o.get('p',[])) for o in out)}, problems {len(err)}")
    for e in err: print('  ', e)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'show': show(a[1], *map(int, a[2:]))
    elif a[0] == 'write': write(a[1], json.loads(a[2]))
    else: print(__doc__)
