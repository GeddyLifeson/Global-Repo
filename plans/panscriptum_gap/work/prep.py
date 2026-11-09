import sys,os,json,importlib.util
S=sys.argv[1]; spec=importlib.util.spec_from_file_location('gb',S+'/spec/gap_batch.py'); gb=importlib.util.module_from_spec(spec); spec.loader.exec_module(gb)
open(S+'/sys.txt','w').write(gb.SYS)
N=50
for tag,host in (('dc','dc.fandom.com'),('marvel','marvel.fandom.com')):
    rows=[json.loads(l) for l in open(f'/mnt/project-files/compute/jobs/panscriptum-gap/retry-{tag}/{host}.jobs.jsonl')]
    os.makedirs(f'{S}/{tag}/in',exist_ok=True); os.makedirs(f'{S}/{tag}/out',exist_ok=True)
    for i in range(0,len(rows),N):
        with open(f'{S}/{tag}/in/s{i//N:03d}.jsonl','w') as o:
            for r in rows[i:i+N]: o.write(json.dumps({'id':r['id'],'user':json.dumps({'name':r['name'],'text':r['text']},ensure_ascii=False)},ensure_ascii=False)+'\n')
    print(tag,len(rows),(len(rows)+N-1)//N)
