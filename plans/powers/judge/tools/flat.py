import re,html as H
SKIP={'image','id','icon','width','height','class','style','align','color','link','size','caption','alt','float','border','bgcolor','imagewidth','sort','ref','refs','date','patch','nolink','nocat','category','cat','float','lang','code'}
NOISE=re.compile(r'^\s*(cite|clear|main|see also|further|about|sidebar|navbox|stub|cleanup|nomerge|merge|otheruses|for|dablink|hatnote|delete|speedy|move|disambig|toc|reflist|references|wowhead|icon|classlink|coord|patch|ptr|link|small|nowrap|mp|nobr|spoiler|quote2|wowheadlink|wikipedia|lang)\b',re.I)
def split_args(body):
    out=[];d=0;b=0;cur=''
    for ch in body:
        if ch in '[{': d+=1
        elif ch in ']}': d-=1
        if ch=='|' and d==0: out.append(cur);cur=''
        else: cur+=ch
    out.append(cur); return out
def tpl(m):
    a=split_args(m.group(1)); name=a[0].strip()
    if NOISE.match(name) or name.startswith('#') or ':' in name[:12] and name.lower().startswith(('file','image','category')): return ''
    pos=[];named=[]
    for x in a[1:]:
        k,e,v=x.partition('=')
        if e and re.fullmatch(r'\s*[\w \-/]{1,30}\s*',k):
            k=k.strip().lower()
            if k in SKIP or not v.strip() or v.strip().lower() in ('0','1','yes','no','true','false'): continue
            named.append((k,v.strip()))
        elif x.strip(): pos.append(x.strip())
    ab=name.lower().startswith(('abilit','spell','power'))
    if ab and pos:  # {{abilities|Name|desc}}: Name — desc (range, notes)
        s=pos[0]+((' — '+' '.join(pos[1:])) if len(pos)>1 else '')
        r=[v for k,v in named if k in('range','notes','cost','cooldown','cast','cd')]
        return ' '+s+(' ('+'; '.join(r)+')' if r else '')+' '
    if 'box' in name.lower() or name.lower().startswith(('sidebar','character','npc','creature','item ')) and not pos: return ''
    return ' '.join(pos)+(' ' if pos and named else '')+' '.join(v for k,v in named)
def table(m):
    t=m.group(0)
    t=re.sub(r'(?m)^\{\|.*$|^\|\+.*$|^\|-.*$|^\|\}.*$','',t)
    t=re.sub(r'(?m)^[|!]\s*(?:[^|\n\[]*\|(?!\|))?',lambda x:'',t)
    return re.sub(r'\|\||!!',' ',t)
def flat(w):
    w=re.sub(r'(?s)<!--.*?-->|<ref[^>]*/>|<ref[^>]*>.*?</ref>|<(gallery|noinclude|references|script|style)\b.*?</\1>','',w)
    w=re.sub(r'(?s)\{\|.*?\n\|\}',table,w)
    for _ in range(8):
        n=re.sub(r'\{\{([^{}]*)\}\}',tpl,w)
        if n==w: break
        w=n
    w=re.sub(r'\[\[(?:File|Image|Category):[^\]]*\]\]','',w,flags=re.I)
    w=re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]',r'\1',w)
    w=re.sub(r'\[https?://\S+ ([^\]]*)\]|\[https?://\S+\]',r'\1',w)
    w=re.sub(r"'{2,}",'',w); w=re.sub(r'<[^>]+>','',w)
    w=re.sub(r'^[*#:;]+ *','',w,flags=re.M)
    w=re.sub(r'(?m)^(=+)\s*(.*?)\s*=+\s*$',lambda m:f"{m.group(1)} {m.group(2)} {m.group(1)}",w)
    return re.sub(r'[ \t]+',' ',re.sub(r'\n\s*\n+','\n',H.unescape(w))).strip()
