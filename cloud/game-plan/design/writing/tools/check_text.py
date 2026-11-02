#!/usr/bin/env python3
"""Loc pre-check for every text table in design/writing/ (style guide section 9, step 4).
Checks: empty text, length over max_chars, unknown {TOKENS}, banned words, exclamation marks outside
barks, duplicate text inside a table. Exits 1 on any error. Run: python3 design/writing/tools/check_text.py"""
import csv, glob, os, re, sys, collections

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PFX = {'ITM', 'ACT', 'PRK', 'VAR', 'BTN', 'SKL', 'ATTR', 'ELEM', 'STATUS', 'FAC', 'CMP', 'REGION', 'LOC'}
BANNED = ['realm', 'ancient evil', 'tapestry', 'testament', 'delve', 'embark', 'unleash', 'unravel', 'whispers of',
          'a dance of', 'beacon of hope', 'fate itself', 'little did', ' thee ', 'mayhap', 'thou ']
TEXT_COLS = re.compile(r'^(text_en|t[123]_en|ostra_en|title_en)$')
DUP_OK = {'dialogue_lines.csv', 'glossary.csv', 'name_banks.csv', 'scene_summary.csv', 'writing_budget.csv', 'writing_schedule.csv'}

def main():
    errs, warns, n = [], [], 0
    for fn in sorted(glob.glob(os.path.join(W, '*.csv'))):
        base = os.path.basename(fn)
        rows = list(csv.DictReader(open(fn, encoding='utf-8')))
        if not rows:
            continue
        cols = [c for c in rows[0] if TEXT_COLS.match(c)]
        seen = collections.Counter()
        for i, r in enumerate(rows, 2):
            for c in cols:
                t = (r.get(c) or '').strip()
                where = '%s:%d %s' % (base, i, c)
                if not t:
                    if c == 'text_en':
                        errs.append(where + ' empty')
                    continue
                n += 1
                mc = r.get('max_chars', '')
                if mc.isdigit() and c == 'text_en' and len(t) > int(mc):
                    errs.append('%s length %d > %s' % (where, len(t), mc))
                for tok in re.findall(r'\{([A-Z]+)_[A-Za-z0-9_]+\}', t):
                    if tok not in TOKEN_PFX:
                        errs.append('%s unknown token prefix %s' % (where, tok))
                low = ' ' + t.lower() + ' '
                for b in BANNED:
                    if b in low:
                        errs.append('%s banned "%s"' % (where, b.strip()))
                if '!' in t and 'bark' not in base and 'BARK' not in r.get('str_id', '') and '/barks/' not in r.get('script', ''):
                    warns.append(where + ' exclamation mark')
                if not re.search(r'(_NAME|_BR_\d+)$', r.get('str_id', '')):
                    seen[t] += 1
        if base not in DUP_OK:
            d = [t for t, k in seen.items() if k > 1]
            if d:
                errs.append('%s: %d duplicate texts, e.g. %r' % (base, len(d), d[0][:60]))
    print('checked %d strings; %d errors, %d warnings' % (n, len(errs), len(warns)))
    for e in errs[:50]:
        print('ERROR', e)
    for w in warns[:20]:
        print('WARN', w)
    sys.exit(1 if errs else 0)

if __name__ == '__main__':
    main()
