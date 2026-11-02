import json,re,sys,collections,unicodedata
sys.path.insert(0,'/tmp/claude-0/w')
import archaic as A, g2p
from render import line, line_en
SRC='/mnt/project-files/LEXICON.json'
OUT=sys.argv[1]
d=json.load(open(SRC))['entries']
FIELDS=('rod','gen','pl','root','vn','comp','was')
tok=lambda s: re.findall(r"[^\W\d_]+",s)
S=collections.Counter()
for x in d:
    for k in FIELDS:
        if k in x: S.update(t.lower() for t in tok(x[k]))
def hs(p): return set(l.split('/')[0].strip().lower() for l in open(p,encoding='utf8',errors='ignore').read().splitlines()[1:])
ga=hs('/tmp/claude-0/ref/ain_dictionaries_ga_index.dic'); gd=hs('/tmp/claude-0/ref/ain_dictionaries_gd_index.dic')
OI=set(open('/tmp/claude-0/w/oldirish_known.txt',encoding='utf8').read().split()); OI|={unicodedata.normalize('NFD',w).encode('ascii','ignore').decode() for w in OI}
REAL=set(S)|ga|gd|OI|set(l.strip().lower() for l in open("/mnt/project-files/diaithiris-archaic/tools/goidelic_words.txt",encoding="utf8"))
A.REAL=REAL
A.OVERRIDES.update(json.load(open('/tmp/claude-0/w/overrides.json')))
for t,_ in S.most_common(): A.word(t)
GA=set(S)
ENG=collections.Counter()
for x in d: ENG.update(t.lower() for t in tok(x['en']))
ENGW={t for t,n in ENG.items() if n>=1}
GAONLY=GA-ENGW
NEUTRAL={'a','an','is','as','to','do','no','so','at','on','in','am','i','e','mo','mar','sin','seo','air','ann','de','le','ma','me','mi','na','ri','ro','s','tu','bi','dh'}
def fix_sense(s):
    glosses=[(m.start(),m.end()) for m in re.finditer(r"(?<=\s)'[^']+'(?=[\s,;:)]|$)",s)]
    ports=[]
    for gs,ge in glosses:
        st=max(s.rfind(c,0,gs) for c in '(;:,')+1
        seg=s[st:gs]
        ts=[t.lower() for t in tok(seg)]
        if any(t in ENGW and t not in GA for t in ts): continue
        if any(t in GAONLY for t in ts): ports.append((st,gs))
    def inr(i,rs): return any(a<=i<b for a,b in rs)
    def f(m):
        i=m.start(); t=m.group(); l=t.lower()
        if inr(i,glosses): return t
        if inr(i,ports) and l in GA: return A.word(t)
        if l in GAONLY: return A.word(t)
        return t
    return A.WORD.sub(f,s)
new=[]
for x in d:
    y=dict(x)
    for k in FIELDS:
        if k in y: y[k]=A.text(y[k])
    for k in ('sense','lit'):
        if k in y and "'" in y[k]: y[k]=fix_sense(y[k])
    if x.get('ipa'): y['ipa']=g2p.phrase(y['rod'])
    new.append(y)
json.dump({'language':'Diaithìris','source':'Archaic layer (see GRAMMAR_ARCHAIC.md)','entries':new},open(OUT+'/LEXICON.json','w'),ensure_ascii=False,indent=1)
mp={t:A.word(t) for t in sorted(S)}
json.dump(mp,open(OUT+'/archaic_map.json','w'),ensure_ascii=False,indent=0)
print(len(S),'tokens; unchanged',sum(1 for t,v in mp.items() if t==v),'in real',sum(1 for v in mp.values() if v in REAL),'distinct out',len(set(mp.values())))

def key(x):
    r=re.sub(r"^(an|am|a|na|nan|nam)\s+","",x['rod'],flags=re.I)
    return unicodedata.normalize('NFD',r).encode('ascii','ignore').decode().lower() or x['rod']
def head(k):
    c=k[:1].upper() if k else '-'
    return c if c.isalnum() or c in "'-" else "'"
def intro(path,n):
    L=open(path,encoding='utf8').read().split('\n')
    i=next(j for j,l in enumerate(L) if l.startswith('## '))
    return '\n'.join(L[:i])
def write(path,items,fmt,hk,src):
    out=[intro(src,len(new)).rstrip(),'']
    cur=None
    for x in sorted(items,key=hk):
        h=head(hk(x))
        if h!=cur: out+=['','## '+h,'']; cur=h
        out.append(fmt(x))
    open(path,'w',encoding='utf8').write('\n'.join(out)+'\n')
write(OUT+'/LEXICON.md',new,line,key,'/mnt/project-files/LEXICON.md')
write(OUT+'/LEXICON_EN.md',new,line_en,lambda x:x['en'].lower(),'/mnt/project-files/LEXICON_EN.md')
