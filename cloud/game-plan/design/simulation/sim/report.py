"""Builds report.html (inline SVG charts) from the CSVs sim.py wrote. Run: python3 report.py"""
import csv, os
from html import escape
HERE = os.path.dirname(os.path.abspath(__file__))
def rd(n): return list(csv.DictReader(open(os.path.join(HERE, n), encoding='utf-8')))
ROUTES = {'main_path': ('Main path', 'var(--s1)'), 'completionist': ('Completionist', 'var(--s2)')}
NAMES = {'REG_01': 'Cinderreach', 'REG_02': 'Saltmere', 'REG_03': 'Thornwood', 'REG_04': 'Glasswaste',
         'REG_05': 'Rimefall', 'REG_06': 'Hollowdeep', 'REG_Q': 'The Quiet'}
W, H, R, T, B = 720, 320, 16, 24, 48

def frame(xmax, ymax, xlab, ylab, yticks, xticks, L=56):
    sx = lambda x: L + (W - L - R) * x / xmax
    sy = lambda y: H - B - (H - T - B) * y / ymax
    g = [f'<line x1="{L}" x2="{W - R}" y1="{sy(v)}" y2="{sy(v)}" class="grid"/><text x="{L - 6}" y="{sy(v) + 4}" class="tick" text-anchor="end">{v:g}</text>' for v in yticks]
    g += [f'<text x="{sx(v)}" y="{H - B + 16}" class="tick" text-anchor="middle">{v:g}</text>' for v in xticks]
    g.append(f'<text x="{(W + L) / 2}" y="{H - 4}" class="lab" text-anchor="middle">{xlab}</text><text x="4" y="{T - 10}" class="lab">{ylab}</text>')
    return sx, sy, g

def svg(body, title):
    return f'<figure><figcaption>{title}</figcaption><svg viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">{"".join(body)}</svg></figure>'

def level_chart():
    rows = rd('progression.csv'); xmax = max(float(r['hour']) for r in rows)
    sx, sy, g = frame(xmax, 80, 'Hours played', 'Level', range(0, 81, 10), range(0, int(xmax) + 1, 10))
    for b in (r for r in rd('level_vs_band.csv') if r['route'] == 'main_path'):
        g.append(f'<text x="{sx(1)}" y="{sy(int(b["band_min"])) - 3}" class="tick">{NAMES[b["region"]]} {b["band_min"]}</text>')
    for k, (name, col) in ROUTES.items():
        rr = [r for r in rows if r['route'] == k]
        band = [(sx(float(r['hour'])), sy(int(r['level_p90']))) for r in rr] + [(sx(float(r['hour'])), sy(int(r['level_p10']))) for r in rr[::-1]]
        g.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in band)}" fill="{col}" opacity=".15"/>')
        line = ' '.join(f"{sx(float(r['hour'])):.1f},{sy(int(r['level_p50'])):.1f}" for r in rr)
        g.append(f'<polyline points="{line}" fill="none" stroke="{col}" stroke-width="2"><title>{name}: median level, band shows 10th to 90th percentile</title></polyline>')
        last = next(r for r in rr if r['level_p50'] == '80')
        g.append(f'<text x="{sx(float(last["hour"])) + 4}" y="{sy(80) + (14 if k == "main_path" else 28)}" class="tick">{name} 80 at {last["hour"]} h</text>')
    return svg(g, 'Level against hours played (median, 10th to 90th percentile)')

def band_chart():
    rows = rd('level_vs_band.csv'); n = len(NAMES); rowh = (H - T - B) / n; L = 100
    sx, _, g = frame(85, 1, 'Level', '', [], range(0, 81, 10), L)
    for i, reg in enumerate(NAMES):
        y = T + i * rowh
        b = next(r for r in rows if r['region'] == reg)
        g.append(f'<rect x="{sx(int(b["band_min"]))}" y="{y + 4}" width="{sx(int(b["band_max"])) - sx(int(b["band_min"]))}" height="{rowh - 8}" rx="4" class="bandbar"><title>{NAMES[reg]} band {b["band_min"]} to {b["band_max"]}</title></rect>')
        g.append(f'<text x="{L - 6}" y="{y + rowh / 2 + 4}" class="tick" text-anchor="end">{NAMES[reg]}</text>')
        for j, (k, (name, col)) in enumerate(ROUTES.items()):
            r = next((r for r in rows if r['region'] == reg and r['route'] == k), None)
            if not r: continue  # route reached 80 before this region
            yy = y + rowh * (0.35 + 0.3 * j)
            x1, x2 = sx(int(r['entry_level_p50'])), sx(int(r['exit_level_p50']))
            g.append(f'<line x1="{x1}" x2="{x2}" y1="{yy}" y2="{yy}" stroke="{col}" stroke-width="2"/><circle cx="{x1}" cy="{yy}" r="4" fill="{col}"/><circle cx="{x2}" cy="{yy}" r="4" fill="{col}"><title>{name}: enters {NAMES[reg]} at {r["entry_level_p50"]}, leaves at {r["exit_level_p50"]}, {r["hours_p50"]} h (medians)</title></circle>')
    return svg(g, 'Player level entering and leaving each region against its band (grey); blue main path, orange completionist')

def ember_chart():
    rows = [r for r in rd('ember_by_band.csv') if r['route'] == 'main_path']
    ymax = max(max(int(r['ember_per_hour']), int(r['ecof_inflow_target'])) for r in rows) * 1.1
    sx, sy, g = frame(len(rows), ymax, '', 'Ember per hour', range(0, int(ymax), 10000), [])
    srcs = [('kills', 'var(--s1)', 'Kills'), ('bosses', 'var(--s2)', 'Bosses'), ('chests', 'var(--s3)', 'Chests and pouches'), ('quests', 'var(--s4)', 'Quests'), ('selling', 'var(--s5)', 'Selling')]
    for i, r in enumerate(rows):
        x, acc, bw = sx(i + 0.2), 0, sx(0.6) - sx(0)
        for k, col, name in srcs:
            v = int(r[f'ember_{k}_per_hour'])
            g.append(f'<rect x="{x}" y="{sy(acc + v) + 1}" width="{bw}" height="{max(0, sy(acc) - sy(acc + v) - 2)}" fill="{col}"><title>{NAMES[r["region"]]} {name}: {v:,}/h</title></rect>'); acc += v
        t = int(r['ecof_inflow_target'])
        g.append(f'<line x1="{x - 4}" x2="{x + bw + 4}" y1="{sy(t)}" y2="{sy(t)}" class="target"><title>ECOF_INFLOW target {t:,}/h</title></line>')
        g.append(f'<text x="{x + bw / 2}" y="{sy(acc) - 6}" class="tick" text-anchor="middle">{r["pct_of_target"]}%</text><text x="{x + bw / 2}" y="{H - B + 16}" class="tick" text-anchor="middle">{NAMES[r["region"]]}</text>')
    legend = ''.join(f'<span><i style="background:{c}"></i>{n}</span>' for _, c, n in srcs) + '<span><i class="tgt"></i>ECOF_INFLOW target</span>'
    return svg(g, 'Ember earned per hour by source against the ECOF_INFLOW target (label = % of target)') + f'<p class="legend">{legend}</p>'

def rarity_chart():
    rows = [r for r in rd('drop_rates.csv') if r['route'] == 'main_path']
    rar = [('common', 'var(--o1)'), ('forged', 'var(--o2)'), ('rare', 'var(--o3)'), ('relic', 'var(--o4)')]
    sx, sy, g = frame(len(rows), 100, '', '% of gear drops', range(0, 101, 20), [])
    for i, r in enumerate(rows):
        x, acc, bw = sx(i + 0.2), 0, sx(0.6) - sx(0)
        for k, col in rar:
            v = float(r[f'pct_{k}'])
            g.append(f'<rect x="{x}" y="{sy(acc + v) + 1}" width="{bw}" height="{max(0, sy(acc) - sy(acc + v) - 2)}" fill="{col}"><title>{NAMES[r["region"]]} {k.title()}: {v}%</title></rect>'); acc += v
        rp = float(r['table_pct_rare_plus'])
        g.append(f'<line x1="{x - 4}" x2="{x + bw + 4}" y1="{sy(100 - rp)}" y2="{sy(100 - rp)}" class="target"><title>Table Rare+ {rp}%</title></line>')
        g.append(f'<text x="{x + bw / 2}" y="{H - B + 16}" class="tick" text-anchor="middle">{NAMES[r["region"]]}</text><text x="{x + bw / 2}" y="{H - B + 30}" class="tick" text-anchor="middle">{r["gear_per_hour"]}/h</text>')
    legend = ''.join(f'<span><i style="background:{c}"></i>{k.title()}</span>' for k, c in rar) + '<span><i class="tgt"></i>Table Rare+ share (above the line)</span>'
    return svg(g, 'Rarity of gear drops by region (second label = gear drops per hour)') + f'<p class="legend">{legend}</p>'

def table(name, cols):
    rows = rd(name)
    return '<table><tr>' + ''.join(f'<th>{c}</th>' for c in cols) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{escape(r[c])}</td>' for c in cols) + '</tr>' for r in rows) + '</table>'

DARK = '--bg:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--grid:#2f2f2d;--band:#3a3a37;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;--o1:#184f95;--o2:#256abf;--o3:#5598e7;--o4:#b7d3f6'
CSS = f""":root{{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--grid:#e4e3dd;--band:#d9d8d0;--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--o1:#9ec5f4;--o2:#5598e7;--o3:#256abf;--o4:#0d366b}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){DARK}}}
:root[data-theme=dark]{DARK}
body{{background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:760px;padding:16px}}
svg{{width:100%;height:auto}}figure{{margin:24px 0}}figcaption{{font-weight:600;margin-bottom:6px}}
.grid{{stroke:var(--grid)}}.tick{{fill:var(--ink2);font-size:11px}}.lab{{fill:var(--ink2);font-size:12px}}.bandbar{{fill:var(--band)}}
.target{{stroke:var(--ink);stroke-width:2;stroke-dasharray:4 3}}.legend{{display:flex;flex-wrap:wrap;gap:12px;color:var(--ink2);font-size:13px}}
.legend i{{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}}.legend i.tgt{{border-top:2px dashed var(--ink);height:0;border-radius:0}}
table{{border-collapse:collapse;font-size:13px;display:block;overflow-x:auto}}td,th{{border-bottom:1px solid var(--grid);padding:4px 8px;text-align:left;vertical-align:top}}"""

s = rd('summary.csv')
head = ' '.join(f'{ROUTES[r["route"]][0]}: level 80 at {r["hours_to_80_p50"]} h median ({r["hours_to_80_p10"]} to {r["hours_to_80_p90"]} h), {r["gear_per_run"]} gear drops, {r["shardborn_per_run"]} Shardborn.' for r in s)
html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loot Economy Simulation</title><style>{CSS}</style></head><body>
<h1>Loot and economy simulation</h1><p>{s[0]['runs']} runs per route of the 30-minute session loop, level 1 to 80. {head} The plan sets the campaign at 60 to 90 hours and a region at 6 to 12 hours.</p>
{level_chart()}{band_chart()}{ember_chart()}{rarity_chart()}
<h2>Findings</h2>{table('findings.csv', ['id', 'severity', 'status', 'finding', 'choice', 'owner'])}</body></html>"""
open(os.path.join(HERE, 'report.html'), 'w', encoding='utf-8').write(html)
print('report.html written')
