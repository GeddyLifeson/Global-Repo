import sys,re,json,gzip,multiprocessing as mp
sys.path.insert(0,'/tmp/s')
import xml.etree.ElementTree as ET
def clean(a):
    t,w=a
    import flat
    return t,flat.flat(w)[:12000]
def gen(path):
    for ev,el in ET.iterparse(path,events=('end',)):
        if el.tag.endswith('}page'):
            ns=el.find('{*}ns')
            if ns is not None and ns.text=='0':
                t=el.find('{*}title').text
                rd=el.find('{*}redirect')
                tx=el.find('{*}revision/{*}text')
                w=tx.text or '' if tx is not None else ''
                if rd is not None or w.lstrip().upper().startswith('#REDIRECT'):
                    m=re.search(r'\[\[([^\]|#]+)',w)
                    yield ('R',t,m.group(1).strip() if m else '')
                else: yield ('P',t,w)
            el.clear()
if __name__=='__main__':
    src,out=sys.argv[1:3]
    reds={};items=[]
    for k,t,w in gen(src):
        if k=='R': reds[t]=w
        else: items.append((t,w))
    print(len(items),len(reds),flush=True)
    res={}
    with mp.Pool(8) as p:
        for t,x in p.imap_unordered(clean,items,chunksize=200): res[t]=x
    json.dump({'pages':res,'redirects':reds},gzip.open(out,'wt',encoding='utf-8'),ensure_ascii=False)
    print('done',len(res))
