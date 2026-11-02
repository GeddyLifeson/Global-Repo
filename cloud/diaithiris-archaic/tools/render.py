import re
def line(x):
    nm = f"**{x['rod']}**"
    if x.get('kenning'): nm += " ✦"
    p = x['pos']
    meta=[]
    if p=='n':
        parts=[]
        if x.get('g'): parts.append(x['g']+'.')
        if x.get('gen'): parts.append(f"gen. *{x['gen']}*")
        if x.get('pl'): parts.append(f"pl. *{x['pl']}*")
        s = "n."+(f" ({', '.join(parts)})" if parts else '')
    elif p=='v':
        s = "v."+(f" (vn. *{x['vn']}*)" if x.get("vn") and x["vn"]!=x["rod"] else "")
    else: s={'phrase':'phr'}.get(p,p)+'.'
    en = x['en'] + (f" ({x['sense']})" if x.get('sense') else '')
    if x.get('lit'): en += f'; lit. "{x["lit"]}"'
    ipa = f" /{x['ipa']}/" if x.get('ipa') else ''
    return f"- {nm} {s} — {en}{ipa} `{x['level']}`"


def line_en(x):
    en = f"**{x['en']}**" + (f" ({x['sense']})" if x.get('sense') else '')
    s = f"*{x['rod']}*" + (" ✦" if x.get('kenning') else '')
    p = x['pos']
    if p == 'n':
        s += " n." + (f" {x['g']}." if x.get('g') else '')
        if x.get('gen'): s += f", gen. *{x['gen']}*"
        if x.get('pl'): s += f", pl. *{x['pl']}*"
    elif p == 'v' and x.get('vn') and x['vn'] != x['rod']:
        s += f" v. vn. *{x['vn']}*"
    return f"- {en} — {s}"
