# S0311 Compile-fix loop: gradle compileJava per module, sends errors plus real class candidates to the Claude API, rewrites failing files, repeats
import json,re,subprocess,sys,pathlib,os,urllib.request,datetime
sys.path.insert(0,'/tmp/claude-0/s')
KEY=open('/mnt/project-files/compute/secrets/anthropic_key').read().strip()
CLS=open('/tmp/claude-0/s/mcclasses.txt').read().split('\n')
env=dict(os.environ,JAVA_HOME='/tmp/claude-0/jdk25',PATH='/tmp/claude-0/jdk25/bin:'+os.environ['PATH'])
def call(p):
    b={"model":"claude-sonnet-5-5","max_tokens":20000,"thinking":{"type":"between_tools"},"messages":[{"role":"user","content":p}]}
    r=urllib.request.Request("https://api.anthropic.com/v1/messages",json.dumps(b).encode(),{"x-api-key":KEY,"anthropic-version":"2023-06-01","content-type":"application/json"})
    d=json.load(urllib.request.urlopen(r,timeout=900));u=d['usage']
    open('/mnt/project-files/compute/ledger.csv','a').write(f"{datetime.datetime.now(datetime.UTC):%Y-%m-%dT%H:%M:%SZ},cr6-fix,claude-sonnet-5-5 sync,{u['input_tokens']},{u['output_tokens']},0,{u.get('cache_read_input_tokens',0)}\n")
    return ''.join(c.get('text','') for c in d['content'])
def run(m):
    m=pathlib.Path(m)
    for rnd in range(5):
        r=subprocess.run(['./gradlew','compileJava','--no-daemon','-q','-Porg.gradle.java.installations.paths=/tmp/claude-0/jdk25'],cwd=m,env=env,capture_output=True,text=True)
        out=r.stdout+r.stderr
        if r.returncode==0: return m.name,'OK',rnd
        errs=[l for l in out.split('\n') if 'error:' in l or l.strip().startswith(('symbol:','location:','^'))]
        errtxt="\n".join(out.split('\n')[:400])
        names=set(re.findall(r'symbol:\s+class (\w+)',out))|set(re.findall(r'package ([\w.]+) does not exist',out))
        hints=[]
        for n in names:
            c=[x for x in CLS if x.endswith('/'+n) or n in x.split('/')[-1]][:8]
            hints.append(f"{n}: "+(", ".join(c) or "NOT FOUND in 26.1.2"))
        files={str(p.relative_to(m/'src/main/java')):p for p in (m/'src/main/java').rglob('*.java')}
        bad=[p for k,p in files.items() if p.name in out or k in out]
        src="\n".join(f"=== {k} ===\n{p.read_text()}" for k,p in files.items() if p in bad)
        txt=call(f"Fix these Java compile errors (Minecraft 26.1.2 NeoForge 26.1.2.109, Mojang mappings; APIs changed a lot, trust the compiler and the class hints, do not guess APIs, simplify the feature if needed).\n\nCOMPILER OUTPUT:\n{errtxt}\n\nREAL CLASS CANDIDATES (full internal names for missing simple names):\n"+"\n".join(hints)+f"\n\nSOURCE OF FAILING FILES:\n{src}\n\nOutput ONLY the corrected full files in this format, no prose:\n=== path/relative/to/src/main/java ===\n<code>")
        for p,body in re.findall(r"=== (.+?) ===\n(.*?)(?=\n=== |\Z)",txt,re.S):
            body=re.sub(r"^```\w*\n|\n```\s*$","",body.strip())+"\n"
            (m/'src/main/java'/p).write_text(body)
    return m.name,'FAIL',out[:1500]
if __name__=='__main__':
    import concurrent.futures as cf
    mods=sys.argv[1:]
    run(mods[0]) if False else None
    with cf.ThreadPoolExecutor(3) as ex:
        for f in [ex.submit(run,m) for m in mods]:
            try: print(f.result(),flush=True)
            except Exception as e: print('ERR',e,flush=True)
