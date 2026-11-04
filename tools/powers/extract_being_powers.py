#!/usr/bin/env python3
"""S6961 extract_being_powers.py: map every Panscriptum being to power ids by keyword scan of its data card (name + summary). No AI.
Usage: python3 -I extract_being_powers.py [--out DIR]
Writes DIR/BEING_POWERS.tsv (key, powers as id:magnitude in priority order, count; the grant step input),
DIR/BEING_POWER_EVIDENCE.tsv (key, power, magnitude, rule, confidence, quote: one row per being and power).
Magnitude comes only from scale words in the same sentence as the power's keyword hit; nothing else is guessed.
Scale: Panscriptum Power P = floor(10*log10 J + 0.5) (The Omniverse and the Library of the Omniverse, section 5 'Realm ceilings'; c3m/measure.py REFERENCE_J).
Doc anchors: human punch P30=1, building P100=3, city P150=4, moon GBE P291=8, Earth GBE P324=9, star P418=10 (universe P700 also 10).
Magnitudes 2, 5, 6, 7 are linear interpolations between the nearest anchors (rule suffix ~interp). Rule text is 'word@P<n>'."""
import re, sqlite3, sys, csv, argparse
from collections import Counter
P = '/mnt/project-files/'
ap = argparse.ArgumentParser()
ap.add_argument('--db', default=P + 'codex-store/library.sqlite')
ap.add_argument('--pool', default=P + 'plans/powers/POWER_POOL.tsv')
ap.add_argument('--out', default=P + 'plans/powers')
a = ap.parse_args()

# rule id (with the P it stands for), magnitude, regex. Highest magnitude present in the evidence sentence wins.
SCALE = [('feat-cosmic@P418', 10, r'(splits?|shatters?|destroys?|cleaves?) (whole |entire |a |the )?(worlds?|stars?|planets?|galax\w+|suns?)|star-?scale|world-?splitting|galactic'),
         ('planet@P324', 9, r'planet(ary)?s?|worlds?'), ('moon@P291', 8, r'moons?'), ('ocean-continent@P255~interp', 7, r'oceans?|continents?'),
         ('island@P220~interp', 6, r'islands?'), ('mountain@P185~interp', 5, r'mountains?|ridgelines?|peaks?'), ('city@P150', 4, r'cit(y|ies)|towns?|fortress(es)?'),
         ('building@P100', 3, r'buildings?|tanks?|towers?|spires?|vehicles?|boulders?|walls?'), ('street@P65~interp', 2, r'city blocks?|streets?|doors?|crowds?|horses?')]
SPEED = [('speed-light@P324', 9, r'(speed|faster) (of|than) light|light-?speed'), ('speed-sound@P255~interp', 6, r'(speed|faster) (of|than) sound|supersonic|hypersonic')]
SCALE = [(r, m, re.compile(r'\b(?:' + w + r')\b', re.I)) for r, m, w in SCALE]
SPEED = [(r, m, re.compile(r'\b(?:' + w + r')\b', re.I)) for r, m, w in SPEED]

def measure(sentence, pid, weak):
    """-> (magnitude, rule, confidence, hit_word_pos) from scale words in the evidence sentence."""
    table = (SPEED if pid == 'super_speed' else []) + SCALE
    best = None
    for rule, m, r in table:
        mm = r.search(sentence)
        if mm and (best is None or m > best[0]): best = (m, rule, mm.start())
    return best

def sentence(text, s, e):
    a_ = max(text.rfind(c, 0, s) for c in '.!?') + 1
    ends = [i for i in (text.find(c, e) for c in '.!?') if i >= 0]
    b_ = min(ends) + 1 if ends else len(text)
    return text[a_:b_], s - a_

pool = list(csv.DictReader(open(a.pool), delimiter='\t'))
rx = lambda x: re.compile(x, re.I) if x else None
strong = {p['id']: rx(p['keywords_strong']) for p in pool}
weak = {p['id']: rx(p['keywords_weak']) for p in pool}
realms = {p['id']: rx(p['realms']) for p in pool}

def powers(text, realm):
    out = {}
    def add(pid, m, rank, is_weak):
        if pid in out: return
        sent, off = sentence(text, m.start(), m.end())
        b = measure(sent, pid, is_weak)
        mag, rule, conf = (b[0], b[1], 'high' if abs(b[2] - off) <= 80 else 'medium') if b else (1, 'default@P30', 'default')
        if is_weak and mag > 2: mag, rule = 2, rule + '+weak-cap'
        q = sent.strip()
        if len(q) > 240: s0 = max(0, off - 120); q = q[s0:s0 + 240].strip()
        out[pid] = (rank, pid, mag, rule, conf, q)
    for pid in strong:
        m = strong[pid].search(text) if strong[pid] else None
        if m: add(pid, m, 0, False)
        elif pid == 'ki_resource' and realms[pid] and realms[pid].search(realm) and pid not in out:
            out[pid] = (0, pid, 1, 'realm@P30', 'default', 'realm: ' + realm)
    for pid in weak:
        m = weak[pid].search(text) if weak[pid] else None
        if m: add(pid, m, 1 if realms[pid] and realms[pid].search(realm) else 2, True)
    return [v for _, *v in sorted(out.values(), key=lambda v: (v[0], v[1]))]

c = sqlite3.connect('file:%s?mode=ro' % a.db, uri=True)
n = nb = 0; conf = Counter()
with open(a.out + '/BEING_POWERS.tsv', 'w') as f1, open(a.out + '/BEING_POWER_EVIDENCE.tsv', 'w') as f2:
    f1.write('key\tpowers\tcount\n'); f2.write('key\tpower\tmagnitude\trule\tconfidence\tquote\n')
    for i, nm, realm, s in c.execute("select id,name,realm,summary from entry where kind='being'"):
        n += 1
        ps = powers(nm + '. ' + (s or ''), realm)
        if not ps: continue
        nb += 1
        f1.write(f"{i}\t{','.join('%s:%d' % (p[0], p[1]) for p in ps)}\t\n")
        for p in ps:
            conf[p[3]] += 1
            f2.write(f"{i}\t{p[0]}\t{p[1]}\t{p[2]}\t{p[3]}\t{p[4].replace(chr(9), ' ').replace(chr(10), ' ')}\n")
print(f'{n} beings, {nb} with powers; rows by confidence: {dict(conf)}', file=sys.stderr)
