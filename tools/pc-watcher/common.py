import os,sys
PF=os.environ.get('PROJECT_FILES','/mnt/project-files').rstrip('/\\')+'/'
RUN=os.environ.get('RUN_DIR',os.path.dirname(os.path.abspath(__file__))).rstrip('/\\')+'/'
import json,os,re,base64,hashlib,urllib.request,uuid
K=(os.environ.get('ANTHROPIC_API_KEY') or open(PF+'compute/secrets/anthropic_key').read().strip())
FJ=RUN+'files.json'
def readme(d):
    return ''.join(open(d+f).read() for f in os.listdir(d) if f.upper().startswith(('README','CHECK')))
def out_config(d):
    """output_config from the job folder: effort from README ('effort: low|medium|high|max'), schema.json -> structured outputs"""
    oc={}
    m=re.search(r'effort[ :=]+(low|medium|high|xhigh|max)',readme(d),re.I)
    if m: oc['effort']=m.group(1).lower()
    if os.path.exists(d+'schema.json'): oc['format']={'type':'json_schema','schema':json.load(open(d+'schema.json'))}
    return oc
def _files(): return json.load(open(FJ)) if os.path.exists(FJ) else {}
def img(path):
    """image block via the Files API (upload once, reuse the file_id across rows and jobs); falls back to base64"""
    raw=open(path,'rb').read(); h=hashlib.sha1(raw).hexdigest(); fs=_files()
    if h not in fs:
        try:
            b=uuid.uuid4().hex
            body=(f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(path)}"\r\nContent-Type: image/png\r\n\r\n').encode()+raw+f'\r\n--{b}--\r\n'.encode()
            r=urllib.request.Request('https://api.anthropic.com/v1/files',body,{'x-api-key':K,'anthropic-version':'2023-06-01','content-type':'multipart/form-data; boundary='+b})
            fs[h]=json.load(urllib.request.urlopen(r,timeout=120))['id']; json.dump(fs,open(FJ,'w'))
        except Exception as e:
            return {'type':'image','source':{'type':'base64','media_type':'image/png','data':base64.b64encode(raw).decode()}}
    return {'type':'image','source':{'type':'file','file_id':fs[h]}}
def count_tokens(model,body):
    """free pre-flight token count (no generation)"""
    b={k:v for k,v in body.items() if k in('model','system','messages')}
    r=urllib.request.Request('https://api.anthropic.com/v1/messages/count_tokens',json.dumps(b).encode(),{'x-api-key':K,'anthropic-version':'2023-06-01','content-type':'application/json'})
    return json.load(urllib.request.urlopen(r,timeout=60))['input_tokens']
