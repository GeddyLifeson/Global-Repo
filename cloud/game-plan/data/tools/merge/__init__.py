"""Design-request merge layer. link.py calls run(T, D) after the core link pass and before the asset-hook registry is built.
Each module m_*.py defines FILES (design request files it owns, relative to game-plan/design) and apply(T, ctx).
Modules patch the loaded tables in T only (never the generators), so they compose and re-run cleanly on every build.
Every row of every owned request file must get exactly one ctx.log(...) call: applied, skipped or conflict, with a reason.
The campaign module runs last. Rules: the master plan wins; design/world/locations.csv wins on place names and IDs;
anything already present is skipped; when two requests conflict, apply the one that matches the plan and log the other as conflict."""
import csv, glob, importlib, os
LAST = ('m_campaign', 'm_antislop', 'm_numeric')

class Ctx:
    def __init__(self, T, D):
        self.T, self.D = T, D
        self.G = os.path.dirname(D)                      # game-plan/
        self.DESIGN = os.path.join(self.G, 'design')
        self.report = []
    # ---- tables
    def rows(self, k):
        h, rr = self.T[k]; return [dict(zip(h, r)) for r in rr]
    def ids(self, k):
        return {r[0] for r in self.T[k][1]} if k in self.T else set()
    def all_ids(self):
        return {r[0] for h, rr in self.T.values() for r in rr if r}
    def append(self, k, d):
        """Append dict d (keys = header names; unknown keys add columns). Returns False if the key already exists."""
        h, rr = self.T.setdefault(k, [list(d.keys()), []])
        if any(r and r[0] == str(d[h[0]]) for r in rr): return False
        for c in d:
            if c not in h:
                h.append(c); [r.append('') for r in rr]
        rr.append([str(d.get(c, '')) for c in h]); return True
    def edit(self, k, key, col, value):
        h, rr = self.T[k]
        if col not in h: h.append(col); [r.append('') for r in rr]
        i = h.index(col); n = 0
        for r in rr:
            if r[0] == key: r[i] = str(value); n += 1
        return n
    def string(self, sid, text, screen='Design merge', note=''):
        """Add a string to ui/strings_data.csv unless it exists in strings.csv or strings_data.csv."""
        if sid in self.ids('ui/strings.csv') or sid in self.ids('ui/strings_data.csv'): return False
        import math
        return self.append('ui/strings_data.csv', {'str_id': sid, 'screen': screen, 'text_en': text, 'max_chars': math.ceil(len(text) * 1.4), 'tokens': '', 'notes': note})
    def design_rows(self, rel):
        with open(os.path.join(self.DESIGN, rel), newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
    # ---- report
    def log(self, file, req_id, status, target, reason):
        assert status in ('applied', 'skipped', 'conflict'), status
        self.report.append(dict(source=file, req_id=req_id, status=status, target=target, reason=reason))

def run(T, D):
    ctx = Ctx(T, D)
    here = os.path.dirname(os.path.abspath(__file__))
    mods = sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(here, 'm_*.py')))
    mods = [m for m in mods if m not in LAST] + [m for m in LAST if m in mods]
    if os.environ.get('MERGE_ONLY'): mods = [m for m in mods if m in os.environ['MERGE_ONLY'].split(',')]
    for m in mods:
        importlib.import_module('merge.' + m).apply(T, ctx)
    # every request row must be accounted for
    owned = {}
    for m in mods:
        for f in importlib.import_module('merge.' + m).FILES: owned[f] = m
    for p in sorted(glob.glob(os.path.join(ctx.DESIGN, '**', 'data-requests.csv'), recursive=True)):
        rel = os.path.relpath(p, ctx.DESIGN)
        rows = list(csv.reader(open(p, newline='', encoding='utf-8')))[1:]
        got = [r for r in ctx.report if r['source'] == rel]
        if rel not in owned:
            for r in rows: ctx.log(rel, r[0], 'skipped', '', 'no merge module owns this file yet')
        elif len(got) < len(rows):
            seen = {g['req_id'] for g in got}
            for r in rows:
                if r[0] not in seen: ctx.log(rel, r[0], 'skipped', '', f'not handled by {owned[rel]}')
    with open(os.environ.get('MERGE_REPORT') or os.path.join(ctx.DESIGN, 'merge-report.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, ['source', 'req_id', 'status', 'target', 'reason']); w.writeheader(); w.writerows(ctx.report)
    return ctx.report
