"""Diaithiris archaic layer: regular sound-change rules run backwards from modern Goidelic spelling.

Rules (applied per word, in this order; initial lenition digraphs are untouched, they are the mutation system):
 1  ea > e          (bean > ben)           8  th#   > d  word-final th / dh / gh > d / d / g
 2  ao > ae         (craobh > craeb)       9  bh mh > b m non-initial
 3  io > iu         (iomadh > iumad)      10  dh gh > d g non-initial
 4  ua > uo         (luath > luod)        11  th    > t  non-initial
 5  eu > ei                              12  nn ll mm > nd ld mb  (ceann > cend)
 6  unstressed a > o before r l n m      13  sh > s non-initial, fh dropped
 7  air > oir unstressed
"""
import re

V = "aeiouàèìòùAEIOUÀÈÌÒÙ"
INIT_DIG = ("bh", "ch", "dh", "fh", "gh", "mh", "ph", "sh", "th")
PROTECT = {"diaithìr", "diaithìris", "diaithìreach", "diaithìrich"}
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def split_init(w):
    """(initial, rest): initial lenition digraph (or first letter) stays as written."""
    lw = w.lower()
    if len(lw) > 2 and lw[:2] in INIT_DIG and lw[2] in V:
        return w[:2], w[2:]
    if lw[:1] in V:
        return "", w
    return w[:1], w[1:]


def unstress(rest, init):
    """a > o / air > oir in non-first syllables before r l n m (no digraph, not word start)."""
    out = []
    groups = list(re.finditer(r"[aeiouàèìòù]+|[^aeiouàèìòù]+", init + rest, re.I))
    seen_vowel = False
    s = init + rest
    res = ""
    for g in groups:
        t = g.group()
        if t[0].lower() in "aeiouàèìòù":
            if seen_vowel:
                nxt = s[g.end():g.end() + 1].lower()
                if t == "a" and nxt in ("r", "l", "n", "m"):
                    t = "o"
                elif t == "ai" and nxt in ("r", "l", "n", "m"):
                    t = "oi"
            seen_vowel = True
        res += t
    return res[len(init):]


def rules(rest, final_ok=True):
    r = rest
    r = re.sub(r"a?ichean$", "igna", r)
    r = r.replace("aigh", "eig")
    r = re.sub(r"ea(?=[^aeiouàèìòù]|$)", "e", r)
    r = re.sub(r"ea", "e", r)
    r = r.replace("ao", "ae")
    r = re.sub(r"io(?!n)", "iu", r)
    r = r.replace("ìo", "ìu")
    r = r.replace("ua", "uo")
    r = r.replace("eu", "ei")
    r = r.replace("ui", "oi")
    r = re.sub(r"(?<=[^aeiouàèìòù])e$", "i", r)
    r = re.sub(r"(th|dh)$", "d", r)
    r = re.sub(r"gh$", "g", r)
    r = r.replace("bh", "b").replace("mh", "m")
    r = r.replace("dh", "d").replace("gh", "g").replace("th", "t")
    r = r.replace("fh", "").replace("sh", "s")
    r = re.sub(r"ich$", "ig", r)
    r = re.sub(r"(?<=[^aeiouàèìòù][aeiou])ag$", "oc", r)
    r = re.sub(r"(?<=[aeiouàèìòù])nn", "nd", r)
    r = re.sub(r"(?<=[aeiouàèìòù])ll", "ld", r)
    r = re.sub(r"(?<=[aeiouàèìòù])mm", "mb", r)
    return r


REAL = set()
MEMO = {}
USED = set()
OVERRIDES = {}


def fallback(c):
    """Extra thematic vowel when the regular result is still a living Goidelic word."""
    cands = []
    m = re.match(r"([^aeiouàèìòù]*)([aeiouàèìòù])(?![aeiouàèìòù])", c)
    if m:
        sub = {"a": "au", "e": "ia", "i": "ie", "o": "ou", "u": "ui", "à": "ài", "è": "èi", "ì": "ìa", "ò": "òi", "ù": "ùa"}[m.group(2)]
        cands.append(c[:m.start(2)] + sub + c[m.end(2):])
    if c[-1] in "aeiouàèìòù":
        cands += [c + "d", c + "g", c + "n"]
    elif re.search(r"[eiìè][^aeiouàèìòù]*$", c):
        cands += [c + "i", c + "e", c + "a"]
    else:
        cands += [c + "u", c + "o", c + "a"]
    for k in cands:
        if k not in REAL and k not in USED:
            return k
    return c + "r"


def diaithiris(o, init):
    """Island laws, made to keep every form clear of the attested Old Irish spelling:
    10 c > k (not before h); 11 stressed short e > ie; 12 unstressed o from law 8 > u."""
    o = re.sub(r"c(?!h)", "k", o)
    m = re.match(r"([^aeiouàèìòù]*)e(?![aeiouàèìòù])", o)
    if m:
        o = o[:m.end() - 1] + "ie" + o[m.end():]
    g = list(re.finditer(r"[aeiouàèìòù]+", o))
    for x in reversed(g[1:]):
        if x.group() in ("o", "oi") and o[x.end():x.end() + 1] in ("r", "l", "n", "m"):
            o = o[:x.start()] + "u" + x.group()[1:] + o[x.end():]
    return o


def core(lw):
    if lw in OVERRIDES:
        return OVERRIDES[lw]
    if lw in PROTECT:
        return lw
    init, rest = split_init(lw)
    o = init + unstress(rules(rest), init)
    o = diaithiris(o, init)
    if o == lw or o in REAL or (o in USED and MEMO.get(lw) != o):
        o = fallback(o)
    return o


def word(w, overrides=None):
    lw = w.lower()
    if len(lw) == 1 and lw not in OVERRIDES:
        return w
    o = MEMO.get(lw)
    if o is None:
        o = MEMO[lw] = core(lw)
        USED.add(o)
    if w[:1].isupper():
        o = o[:1].upper() + o[1:]
    if w.isupper() and len(w) > 1:
        o = o.upper()
    return o


def text(s, overrides=None, only=None):
    """Transform every Diaithiris token in s. only: optional set; tokens outside it are left alone."""
    def f(m):
        t = m.group()
        if only is not None and t.lower() not in only:
            return t
        return word(t, overrides)
    return WORD.sub(f, s)


if __name__ == "__main__":
    import json, os, sys
    here = os.path.dirname(os.path.abspath(__file__))
    for fn, tgt in (("archaic_map.json", MEMO), ("overrides.json", OVERRIDES)):
        p = os.path.join(here, "..", fn) if fn == "archaic_map.json" else os.path.join(here, fn)
        if os.path.exists(p):
            tgt.update(json.load(open(p, encoding="utf8")))
    for a in sys.argv[1:]:
        print(a, "->", text(a))
