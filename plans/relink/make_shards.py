"""Shard relink-things/in.jsonl into 100-row text files for judging. Usage: python3 -I make_shards.py <in.jsonl> <outdir>"""
import json,os,re,sys
def parse(p):
    e=p.split('\n\nCandidates:\n')
    return e[0].replace('Entry: ','',1),[re.sub(r'^\d+\. ','',x) for x in re.split(r'\n(?=\d+\. )',e[1].strip())]
R=[json.loads(l) for l in open(sys.argv[1])]
os.makedirs(sys.argv[2],exist_ok=True)
for s in range(0,len(R),100):
    with open(f'{sys.argv[2]}/s{s//100:03d}.txt','w') as f:
        for r in R[s:s+100]:
            ent,c=parse(r['prompt'])
            f.write(f"## {r['id']}\nE: {ent}\n"+"\n".join(f"{n+1}. {x[:200]}" for n,x in enumerate(c))+"\n")
