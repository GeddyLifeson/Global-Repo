import re,sys,json,subprocess,urllib.parse,html,os
OUT='/mnt/project-files/game-plan/design/audio/samples/freesound/src'
os.makedirs(OUT,exist_ok=True)
Q=json.load(open(sys.argv[1]))
def get(u):
    return subprocess.run(['curl','-sSL','--max-time','60',u],capture_output=True).stdout
res=json.load(open(OUT+'/../sources.json')) if os.path.exists(OUT+'/../sources.json') else {}
for key,(q,lo,hi) in Q.items():
    if key in res: continue
    pick=None
    for lic in ['Creative Commons 0','Attribution']:
        f=f'license:"{lic}" duration:[{lo} TO {hi}]'
        u='https://freesound.org/search/?'+urllib.parse.urlencode({'q':q,'f':f,'s':'Downloads (most first)'})
        h=get(u).decode('utf8','ignore')
        for m in re.finditer(r'data-sound-id="(\d+)"\s+data-username="([^"]+)".*?data-mp3="([^"]+)".*?data-title="([^"]*)"\s+data-duration="([\d.]+)"',h,re.S):
            sid,user,mp3,title,dur=m.groups()
            if not (lo<=float(dur)<=hi): continue
            pick=dict(id=sid,user=user,title=html.unescape(title),dur=float(dur),licence=lic,mp3=mp3.replace('-lq.mp3','-hq.mp3'));break
        if pick: break
    if not pick: print('NONE',key,q); continue
    # verify licence on sound page
    page=get(f"https://freesound.org/people/{pick['user']}/sounds/{pick['id']}/").decode('utf8','ignore')
    lm=re.search(r'creativecommons\.org/(publicdomain/zero|licenses/[a-z-]+)/([\d.]+)',page)
    pick['licence_url']=('https://'+lm.group(0)) if lm else ''
    if 'nc' in pick['licence_url'].split('/')[-3:-2][0] if lm else False: print('NC skip',key);continue
    fn=f"{OUT}/{key}.mp3"
    open(fn,'wb').write(get(pick['mp3']))
    pick['file']=fn; res[key]=pick
    print(key,pick['id'],pick['user'],pick['licence'],pick['licence_url'],round(pick['dur'],1),pick['title'][:40])
json.dump(res,open(OUT+'/../sources.json','w'),indent=1)
