"""Check finished work against the Shardfall Bible (bible/BIBLE.md).

    python3 bible/check.py PATH [PATH ...]   files or folders you changed
    python3 bible/check.py --data            canon counts vs data/, then data/tools/validate.py

Errors (exit 1): canon rule broken (rules.csv), retired name or term, ID that no data table defines,
banned word or em dash in player-facing text. Warnings: slop words in player-facing text, em dash elsewhere."""
import csv, os, re, subprocess, sys

csv.field_size_limit(10**9)
B = os.path.dirname(os.path.abspath(__file__))
G = os.path.dirname(B)
sys.path.insert(0, os.path.join(G, 'design', 'writing', 'tools'))
from canon_names import RENAME, RENAME_RX  # noqa: E402  retired town names
from check_text import BANNED  # noqa: E402  writing style guide banned words

TEXT = ('.csv', '.md', '.txt', '.json', '.html', '.svg', '.py', '.h', '.cpp', '.ini')
SKIP = ('__pycache__', 'audio/samples', 'design/research', 'design/audit', 'design/continuity', 'bible', '-facts.md',
        'merge-report.csv', 'copy_changes.csv', 'canon_names.py', 'check_text.py', '01-style-guide.md', 'master-plan.txt')
PLAYER = ('design/writing', 'data/ui', 'design/ui-mockups', 'design/cinematics', 'design/frontend', 'design/companion')
IDS = re.compile(r'\b(?:ACT|LOC|ITM|QST|FLG|CNT|REG|FAC|MQ|SQ|CMPQ)_[A-Z0-9_]*[A-Z0-9]\b(?![_*./{%<>\\\[])')
QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")  # in code only string literals hold IDs; names like MQ_ORDER are variables
PREFIX = re.compile(r"(?:startswith|endswith)\(\(?[^)]*\)|(?:" + QUOTED.pattern + r")\s*\+")  # ID prefixes that code completes
NUMBERED = re.compile(r'_[A-Z]?\d+$')  # SQ_REG_01 names the SQ_REG_01_nn family


def rows(name):
    with open(os.path.join(B, name), encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


TERMS = rows('terms.csv')


def literal(rid, term, note, guard=''):
    """A plain word rule: cheap substring test first, regex only on a hit."""
    term = term.strip()
    return rid, term.lower(), re.compile(guard + r'\b' + re.escape(term) + r'\b', re.I), note


RULES = [(r['id'], None, re.compile(r['regex'], re.I if r['ignore_case'] == '1' else 0), r['canon']) for r in rows('rules.csv')]
RULES += [('RETIRED_NAME', o.lower(), rx, f'now "{n}"') for (o, _), (rx, n) in zip(RENAME, RENAME_RX)]
RULES += [literal('RETIRED_TERM', t['term'], t['use_instead'], r'(?<!\bno )(?<!without )') for t in TERMS if t['status'] == 'retired']  # "no loot boxes" states the rule
PLAYER_ERR = [literal('BANNED', w, 'banned by the writing style guide') for w in BANNED]
SLOP = [literal('SLOP', t['term'], t['use_instead']) for t in TERMS if t['status'] == 'slop']


def defined_ids():
    ids = {t['term'] for t in TERMS if t['status'] == 'token'}
    tables = [os.path.join(dp, f) for top in ('data', 'design/world') for dp, _, fn in os.walk(os.path.join(G, top)) for f in fn if f.endswith('.csv')]
    for t in tables + [os.path.join(G, 'design/liveops/future_content_ids.csv')]:  # reserved future IDs count as defined
        with open(t, encoding='utf-8', errors='replace') as fh:
            ids.update(line.split(',', 1)[0].strip() for line in fh)
    with open(os.path.join(G, 'design/campaign/tools/loc_map.csv'), encoding='utf-8', newline='') as fh:
        ids.update(r['campaign_id'] for r in csv.DictReader(fh) if r['world_id'])  # campaign aliases of world places
    fams = {'_'.join(i.split('_')[:k]) for i in ids for k in (1, 2)}  # family names such as LOC_CQ or CMPQ_C4
    for i in ids:
        while m := NUMBERED.search(i):
            i = i[:m.start()]
            fams.add(i)
    return ids | fams


def files(paths):
    for p in map(os.path.abspath, paths):
        if os.path.isfile(p):
            yield p, os.path.relpath(p, G)
            continue
        for dp, _, fn in os.walk(p):
            for f in fn:
                rel = os.path.relpath(os.path.join(dp, f), G)
                if f.endswith(TEXT) and not any(s in rel for s in SKIP):
                    yield os.path.join(dp, f), rel


def scan(line, rules, at, out):
    low = line.lower()
    for rid, lit, rx, note in rules:
        if lit is not None and lit not in low:
            continue
        m = rx.search(line)
        if m:
            out.append(f'{at} {rid} "{m.group(0)}": {note}')


def check(paths):
    ids, errs, warns = None, [], []
    for f, rel in files(paths):
        player, check_ids = rel.startswith(PLAYER), not rel.startswith('data/')
        if check_ids and ids is None:
            ids = defined_ids()
        rules = RULES + PLAYER_ERR if player else RULES
        with open(f, encoding='utf-8', errors='replace') as fh:
            for n, line in enumerate(fh, 1):
                if 'bible: ok' in line:  # detector code that names retired terms on purpose
                    continue
                at = f'{rel}:{n}'
                scan(line, rules, at, errs)
                if player:
                    scan(line, SLOP, at, warns)
                if '—' in line:
                    (errs if player else warns).append(f'{at} EM_DASH: game text uses an ellipsis or a comma, never an em dash')
                if check_ids and '_' in line:
                    for t in set(IDS.findall(' '.join(QUOTED.findall(PREFIX.sub('', line))) if f.endswith('.py') else line)) - ids:
                        errs.append(f'{at} UNKNOWN_ID {t}: no data table defines it (add it through its owner, see bible/production.md)')
    return errs, warns


def check_data():
    errs = []
    for r in rows('numbers.csv'):
        with open(os.path.join(G, 'data', r['table']), encoding='utf-8', newline='') as fh:
            data = list(csv.DictReader(fh))
        if r['filter']:
            col, op, val = re.match(r'(\w+)(!=|\^=|=)(.*)', r['filter']).groups()
            test = {'=': lambda v: v == val, '!=': lambda v: v != val, '^=': lambda v: v.startswith(val)}[op]
            data = [x for x in data if test(x[col])]
        if len(data) != int(r['value']):
            errs.append(f"data/{r['table']} COUNT {r['key']} is {len(data)}, canon is {r['value']} ({r['source']})")
    v = subprocess.run([sys.executable, os.path.join(G, 'data', 'tools', 'validate.py')], capture_output=True, text=True)
    out = v.stdout.strip()
    print(out.splitlines()[-1] if out else v.stderr.strip())
    if v.returncode:
        errs.append('data/tools/validate.py failed (see its output)')
    return errs, []


def main(argv):
    if not argv:
        sys.exit(__doc__)
    errs, warns = check_data() if argv == ['--data'] else check(argv)
    for w in warns:
        print('WARN', w)
    for e in errs:
        print('ERROR', e)
    print(f'bible check: {len(errs)} errors, {len(warns)} warnings')
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main(sys.argv[1:])
