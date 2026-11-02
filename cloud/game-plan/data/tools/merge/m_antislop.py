"""antislop copy pass (game-plan/antislop/). Runs after every other merge module.
R-02: no em dashes in player-facing text; a cut-off line ("missing— never mind") becomes an ellipsis.
Template filler: the text generators reuse a small pool of flavor sentences, so the same line shows up in up to 30 different
journals, letters and item descriptions. A flavor sentence is kept the first time it appears and dropped after that, unless
dropping it would leave the string empty. Lines with numbers or tokens are mechanics, not flavor, and are never touched.
Every change is listed in game-plan/antislop/copy_changes.csv.
Last, the tokens column is set to the {TOKENS} the final text uses (B09 checker)."""
import csv, os, re

FILES = []
FLAVOR = {'Lore codex', 'Lore reader', 'Quest journal', 'Item description', 'Terminal'}
MECH = re.compile(r'[0-9%{]')  # numbers and tokens mark mechanics text
TOKEN = re.compile(r'\{([A-Z]+_[a-z0-9_]+)\}')
EM = [(re.compile(r'\s*—\s*(?=[a-z])'), '... '), (re.compile(r'\s*—\s*'), ', ')]


def units(t):
    """Lines when the text has them (log entries, letters), else sentences, keeping a bracketed note and its quote together."""
    if '\n' in t:
        return t.splitlines(keepends=True)
    out, cur = [], ''
    for s in re.split(r'(?<=[.!?])(?= )', t):
        cur += s
        if cur.count('[') == cur.count(']') and cur.count('"') % 2 == 0:
            out.append(cur); cur = ''
    return out + [cur] if cur else out


def key(u):
    u = u.strip()
    if u.startswith('[') and u.endswith(']'):   # reader markers such as [ENTRY REMOVED BY SHIP AUTHORITY] are UI, not flavor
        return None
    return u if len(u) > 30 and not MECH.search(u) else None


def dedup(us, seen):
    """Drop flavor units already used elsewhere, with the short sentences that trail them."""
    keep, dropping = [], False
    for u in us:
        k = key(u)
        if k:
            dropping = k in seen
            seen.add(k)
        elif dropping and MECH.search(u):
            dropping = False
        if not dropping:
            keep.append(u)
        if u.endswith('\n'):
            dropping = False
    return keep


def apply(T, ctx):
    h, rows = T['ui/strings_data.csv']
    sid, scr, txt, tok = h.index('str_id'), h.index('screen'), h.index('text_en'), h.index('tokens')
    seen, log = set(), []
    for r in rows:
        t = r[txt]
        for pat, rep in EM:
            t = pat.sub(rep, t)
        if r[scr] in FLAVOR:
            us = units(t)
            keep = dedup(us, seen)
            if keep and len(keep) < len(us):
                t = ''.join(keep).strip()
        if t != r[txt]:
            log.append({'str_id': r[sid], 'rule': 'R-02 em dash' if '—' in r[txt] else 'repeated flavor line', 'before': r[txt], 'after': t})
            r[txt] = t
        r[tok] = ' '.join(sorted(set(TOKEN.findall(t))))
    with open(os.path.join(ctx.G, 'antislop', 'copy_changes.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, ['str_id', 'rule', 'before', 'after']); w.writeheader(); w.writerows(log)
