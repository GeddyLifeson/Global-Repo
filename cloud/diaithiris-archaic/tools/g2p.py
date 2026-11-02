"""Reconstructed pronunciation for archaic Diaithiris spelling (rules documented in GRAMMAR_ARCHAIC.md)."""
import re
VOW = "aeiouàèìòù"
SL = set("eiìè")
VM = {"a": "a", "e": "ɛ", "i": "i", "o": "ɔ", "u": "u", "à": "aː", "è": "eː", "ì": "iː", "ò": "oː", "ù": "uː"}
DI = {"ae": "ɛː", "ai": "ai", "oi": "oi", "ei": "ei", "au": "au", "ia": "iə", "ua": "uə", "uo": "uo", "iu": "ju",
      "io": "iɔ", "eo": "jɔ", "ou": "ɔu", "ao": "ɯː"}
INIT = {"bh": "v", "mh": "v", "dh": "ɣ", "gh": "ɣ", "fh": "", "ph": "f", "sh": "h", "th": "h", "ch": "x"}
CONS = {"b": "b", "c": "k", "d": "d", "f": "f", "g": "g", "h": "h", "j": "dʒ", "k": "k", "l": "l", "m": "m", "n": "n",
        "p": "p", "q": "k", "r": "ɾ", "s": "s", "t": "t", "v": "v", "w": "w", "x": "ks", "z": "z", "y": "j"}


def vgroups(w):
    return [(m.start(), m.end()) for m in re.finditer(r"[aeiouàèìòù]+", w)]


def word(w):
    w = w.lower()
    if not w:
        return ""
    g = vgroups(w)
    if not g:
        return w
    out = []
    i = 0
    n = len(w)
    first_v = g[0][0]
    while i < n:
        c = w[i]
        if c in VOW:
            j = i
            while j < n and w[j] in VOW:
                j += 1
            grp = w[i:j]
            seg = ""
            k = 0
            while k < len(grp):
                if grp[k:k + 2] in DI:
                    seg += DI[grp[k:k + 2]]; k += 2
                else:
                    seg += VM[grp[k]]; k += 1
            out.append(seg)
            i = j
            continue
        d = w[i:i + 2]
        # broad or slender: next vowel group, else previous
        nv = next((w[a] for a, b in g if a >= i), None)
        pv = next((w[b - 1] for a, b in reversed(g) if b <= i), None)
        sl = (nv in SL) if nv else (pv in SL)
        if d in INIT and (i == 0 or w[i + 1:i + 2] in VOW or True) and d != "ch":
            out.append(INIT[d]); i += 2; continue
        if d == "ch":
            out.append("ç" if sl else "x"); i += 2; continue
        if d == "ng":
            out.append("ŋ"); i += 2; continue
        if d in ("nd", "ld", "mb"):
            out.append({"nd": "nd", "ld": "ld", "mb": "mb"}[d]); i += 2; continue
        if d in ("sc", "sk"):
            out.append("sk"); i += 2; continue
        p = CONS.get(c, c)
        if c in "lnr":
            p += "ʲ" if sl else "ˠ"
        elif c == "s" and sl:
            p = "ʃ"
        elif c in "ptk" or c in "c":
            if i == 0 or (i == first_v - 0 and False):
                p += "ʰ"
        out.append(p)
        i += 1
    s = "".join(out)
    if not s.startswith("ˈ"):
        s = "ˈ" + s
    return s


def phrase(t):
    return " ".join(word(x) for x in re.findall(r"[^\W\d_]+", t))
