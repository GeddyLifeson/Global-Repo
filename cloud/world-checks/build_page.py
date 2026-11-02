import base64, json, html
snow = [json.loads(l) for l in open("snow_all.jsonl")]
ores = {json.loads(l)["site"]: json.loads(l) for l in open("ores_all.jsonl")}
NAMES = {"alps_montblanc": "Mont Blanc, Alps", "scotland_bennevis": "Ben Nevis, Scotland", "andes_aconcagua": "Aconcagua, Andes",
         "kilimanjaro": "Kilimanjaro", "rwenzori": "Rwenzori", "himalaya_everest": "Everest, Himalaya", "paris_lowland": "Paris lowland"}

def img(s):
    return "data:image/png;base64," + base64.b64encode(open(f"map_{s}.png", "rb").read()).decode()

def chart(bands):
    rows = sorted(((int(k.split("..")[0]), v) for k, v in bands.items()), key=lambda r: r[0])
    rows = [r for r in rows if -1500 <= r[0] <= 2250]
    W, H, pad = 520, 170, 34
    bw = (W - pad - 8) / max(1, len(rows))
    out = [f'<svg viewBox="0 0 {W} {H + 34}" role="img" aria-label="snow share by height band">']
    for f in (0, .5, 1):
        y = H - f * (H - 10)
        out.append(f'<line x1="{pad}" x2="{W-8}" y1="{y:.0f}" y2="{y:.0f}" class="grid"/><text x="{pad-6}" y="{y+4:.0f}" class="ax" text-anchor="end">{int(f*100)}%</text>')
    for i, (lo, (n, f)) in enumerate(rows):
        x = pad + i * bw; h = f * (H - 10)
        cls = "above" if lo >= 0 else "below"
        out.append(f'<rect x="{x+1:.1f}" y="{H-h:.1f}" width="{bw-2:.1f}" height="{max(h,0.5):.1f}" class="{cls}"><title>{lo:+d} to {lo+250:+d} m: {f*100:.1f}% snow ({n:,} columns)</title></rect>')
        if lo % 500 == 0:
            out.append(f'<text x="{x:.1f}" y="{H+16}" class="ax" text-anchor="middle">{lo:+d}</text>')
    zero = pad + next((i for i, r in enumerate(rows) if r[0] >= 0), 0) * bw
    out.append(f'<line x1="{zero:.1f}" x2="{zero:.1f}" y1="4" y2="{H}" class="line"/><text x="{zero+4:.1f}" y="14" class="ax">snowline</text>')
    out.append(f'<text x="{(W+pad)/2:.0f}" y="{H+32}" class="ax" text-anchor="middle">metres above (+) or below (−) the Age I snowline</text></svg>')
    return "".join(out)

cards = []
for r in snow:
    s = r["site"]; v = r.get("pass")
    tag = {True: ("PASS", "ok"), False: ("ICE SHEET", "na"), None: ("ICE SHEET", "na")}[v]
    if s == "alps_montblanc":
        detail = f"Valleys sit under the 15 ka Alpine ice field, so they are snowed by the ice layer. Outside the ice, every column above the line is snowed ({r['snow_above_line+200']*100:.0f}%). Nothing below the line is left to test."
    elif s == "scotland_bennevis":
        detail = "Every generated column lies under the 15 ka Scottish ice cap and is snowed by the ice layer, which is the intended Age I look. The snowline itself is not testable here."
    else:
        detail = (f"Line {r['line_m']:,} m at {r['lat']}°. Snow on {r['snow_above_line+200']*100:.1f}% of columns 200 m or more above it, "
                  f"{r['snow_below_line-300']*100:.1f}% of columns 300 m or more below it. {r['land_cols']:,} land columns.")
    cards.append(f'''<article class="site"><header><h3>{NAMES[s]}</h3><span class="pill {tag[1]}">{tag[0]}</span></header>
<p>{html.escape(detail)}</p>{chart(r.get("bands", {})) if r.get("bands") else ""}
<figure><img src="{img(s)}" alt="Top-down map of the {NAMES[s]} strip"></figure></article>''')

def ore_rows(site, src=ores):
    o = src[site]["ores"]; rows = []
    for k in ("coal", "iron", "copper", "gold", "redstone", "lapis", "diamond", "emerald"):
        v = o[k]; b = v["vanilla_band"]
        rows.append(f"<tr><td>{k}</td><td>{v['per_chunk']}</td><td>{v['y_p5_p50_p95'][0]} to {v['y_p5_p50_p95'][2]}</td><td>{v['vanilla_y_p1_p50_p99'][0]} to {v['vanilla_y_p1_p50_p99'][2]}</td><td>{b[0]} to {b[1]}</td></tr>")
    return "".join(rows)

page = open("page_tpl.html").read()
ores11 = {json.loads(l)["site"]: json.loads(l) for l in open("/root/wc11/ores11.jsonl")}
page = page.replace("%PARIS11%", ore_rows("paris_lowland", ores11)).replace("%EVEREST11%", ore_rows("himalaya_everest", ores11))
page = page.replace("%CARDS%", "".join(cards)).replace("%PARIS%", ore_rows("paris_lowland")).replace("%EVEREST%", ore_rows("himalaya_everest"))
open("/mnt/project-files/world-checks/world_checks.html", "w").write(page)
print(len(page))
