"""Numeric columns import as numbers (B04 row structs). Runs last.
In a column whose values are numbers, a "-"/"n/a" cell becomes blank, "+5" becomes 5, a range "9-12" keeps its low end and
adds <col>_max, and any other text (a formula or a pointer to another table) moves to the row's notes column, once per row.
Lists like "65; 30" and short codes like "P" or "END" are left alone: a column holding them stays a string."""
import re

FILES = []
NUM = re.compile(r'-?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$')  # same rule as FLOAT in unreal/tools/GenRowStructs.py
NULL = {'', '-', 'n/a', 'N/A', '—'}
RANGE = re.compile(r'(\d+)-(\d+)$')
CODE = re.compile(r'[A-Za-z]{1,4}$')


def kind(v):
    if v in NULL: return 'null'
    if NUM.match(v): return 'num'
    if NUM.match(v.lstrip('+')): return 'plus'
    return 'range' if RANGE.match(v) else 'text'


def add_col(h, rr, col):
    h.append(col)
    for r in rr: r.append('')
    return len(h) - 1


def apply(T, ctx):
    fixed = {}
    for k, (h, rr) in T.items():
        if k.startswith(('ui/', 'assets/')): continue
        for j in range(1, len(h)):
            kinds = [kind(r[j]) for r in rr]
            vals = [r[j] for r, t in zip(rr, kinds) if t != 'null']
            num = sum(t in ('num', 'plus') for t in kinds)
            dirty = any(t != 'num' for t, r in zip(kinds, rr) if r[j])
            if not vals or not dirty or num < 0.7 * len(vals) or any(';' in v or CODE.match(v) for v in vals): continue
            col = h[j]
            ni = next((h.index(c) for c in ('notes', 'Notes', 'note', 'why') if c in h), None)
            if ni is None and 'text' in kinds: ni = add_col(h, rr, 'notes')
            mi = add_col(h, rr, col + '_max') if 'range' in kinds else None
            for r, t in zip(rr, kinds):
                v = r[j]
                r[j] = RANGE.match(v).group(1) if t == 'range' else v.lstrip('+') if t in ('num', 'plus') else ''
                if mi: r[mi] = RANGE.match(v).group(2) if t == 'range' else r[j]
                if t == 'text' and v not in r[ni]: r[ni] = (r[ni] + '; ' if r[ni] else '') + f'{col}: {v}'
            fixed.setdefault(k, []).append(col)
    ctx.log('B04', 'NUMERIC_COLUMNS', 'applied', 'all tables',
            'numeric columns cleaned (notes and formulas moved to the notes column, ranges split into _max): '
            + '; '.join(f'{k} {", ".join(c)}' for k, c in fixed.items()))
