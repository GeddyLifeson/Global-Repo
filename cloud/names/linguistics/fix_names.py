# S0317 Mechanically repairs names that fail audit_names.py, no model: per word keep if it passes, else map disallowed characters, else trim at a syllable boundary, else coin a seeded word from the language's own graphemes and syllable count; rewrites names/*.json in place
# python3 -I fix_names.py   then python3 -I audit_names.py (must exit 0)
import glob, hashlib, json, os, random, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_names as A
R = A.R
V = 'aeiouyáàâäéèêëíìîïóòôöúùûüāēīōū'
CACHE = {}

def inv(s):
    if s not in CACHE:
        d = json.load(open(f'{R}/linguistics/rules/{s}.json'))
        g = [x.lower() for x in d['allowed_graphemes'] if x]
        v = [x for x in g if x[0] in V]; c = [x for x in g if x[0] not in V]
        CACHE[s] = (v or ['a'], c or ['t'], d['syllables_per_word'], d['max_word_length'], g)
    return CACHE[s]

def fold(ch):
    return unicodedata.normalize('NFD', ch)[0]

def mapchars(s, w):
    g = inv(s)[4]; out = ''; i = 0
    while i < len(w):
        for x in sorted(g, key=len, reverse=True):
            if w.startswith(x, i): out += x; i += len(x); break
        else:
            c = w[i]; i += 1
            if c in A.rules[s][1]: out += c; continue
            f = fold(c)
            if f in g: out += f
            elif f in 'sz' and 's' in g: out += 's'
            elif f in 'cq' and 'k' in g: out += 'k'
            elif f == 'v' and 'b' in g: out += 'b'
            elif f == 'x' and 'ks' in g: out += 'ks'
    return out

def coin(s, rnd):
    v, c, spw, mx, _ = inv(s)
    for _ in range(400):
        w = ''
        for _ in range(rnd.choice(spw) if spw else 2):
            w += (rnd.choice(c) if rnd.random() < .85 else '') + rnd.choice(v) + (rnd.choice(c) if rnd.random() < .3 else '')
        if len(w) <= mx and not A.check(s, w): return w
    for _ in range(4000):
        w = ''.join(rnd.choice(c) + rnd.choice(v) for _ in range(rnd.choice([1, 2, 3])))
        if len(w) <= mx and not A.check(s, w): return w
    return None

def fix(s, eid, name, tag):
    rnd = random.Random(hashlib.md5(f'{s}|{eid}|{tag}'.encode()).hexdigest())
    parts = re.split(r'([ \-]+)', name)
    for k in range(0, len(parts), 2):
        w = parts[k]
        if not A.check(s, w): continue
        m = mapchars(s, w.lower())
        mx = inv(s)[3]
        for t in (m, m[:mx], m[:mx - 1], m[:mx - 2]):
            if t and not A.check(s, t): w = t; break
        else:
            w = coin(s, rnd)
        parts[k] = w
    n = ''.join(p or '' for p in parts)
    if any(p is None for p in parts) or A.check(s, n):
        parts[-1] = coin(s, rnd) or parts[-1]
        n = ''.join(parts)
    return (n[0].upper() + n[1:]) if name[:1].isupper() else n

def main():
    left = 0; fixed = 0
    for f in sorted(glob.glob(R + '/*.json')):
        try: d = json.load(open(f))
        except Exception: continue
        if not isinstance(d, dict): continue
        ch = False
        for eid, v in d.items():
            if not isinstance(v, dict): continue
            for s, name in v.items():
                if s in A.rules and isinstance(name, str) and A.check(s, name):
                    for t in range(8):
                        n = fix(s, eid, name, t)
                        if n and not A.check(s, n): v[s] = n; ch = True; fixed += 1; break
                    else: left += 1
        if ch:
            tmp = f + '.tmp'; json.dump(d, open(tmp, 'w'), ensure_ascii=False); os.replace(tmp, f)
    print('fixed', fixed, 'unfixed', left)

if __name__ == '__main__':
    main()
