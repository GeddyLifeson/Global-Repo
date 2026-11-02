"""Factory-look filter for textures of mods added after the first coverage pass. Size and UV layout are kept."""
import zipfile,glob,io,os,sys,colorsys
from PIL import Image
M='/home/user/work/modjars/'
OUT='/home/user/diaithirrpg/tools/art/blender/baked/newmods/assets/'
have=set()
for z in glob.glob('/home/user/work/pack18/*.zip'): have|=set(zipfile.ZipFile(z).namelist())
B=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def pot(n): return n>0 and n&(n-1)==0
def style(im,item):
    im=im.convert('RGBA'); w,h=im.size; px=im.load(); o=Image.new('RGBA',im.size); q=o.load()
    for y in range(h):
        for x in range(w):
            r,g,b,a=px[x,y]
            if a==0: continue
            hh,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
            s=min(1,s*0.85)
            t=(B[y%4][x%4]-7.5)/16/5
            v=round(min(1,max(0,v+t))*6)/6
            v=0.08+v*0.9
            R,G,Bc=colorsys.hsv_to_rgb(hh,s,v)
            q[x,y]=(int(R*255),int(G*255),int(Bc*255),a)
    if item:
        for y in range(h):
            for x in range(w):
                if px[x,y][3]==0: continue
                for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                    nx,ny=x+dx,y+dy
                    if 0<=nx<w and 0<=ny<h and px[nx,ny][3]==0:
                        r,g,b,a=q[x,y]; q[x,y]=(r*2//3,g*2//3,b*2//3,a);break
    else:
        for x in range(w):
            for y in (0,h-1):
                r,g,b,a=q[x,y]
                if a: q[x,y]=(r*5//6,g*5//6,b*5//6,a)
    return o
n=0;skip=0
for p in ["minevegas","modulargolems","drones","untamedwilds-26.1.2-3.0.1-diaithir","the-backrooms"]:
    z=zipfile.ZipFile(glob.glob(M+p+'*.jar')[0])
    for name in z.namelist():
        if not(name.startswith('assets/') and '/textures/' in name and name.endswith('.png')) or name in have or '/font/' in name or '/gui/' in name: continue
        im=Image.open(io.BytesIO(z.read(name)))
        if not(pot(im.width) and pot(im.height)) or z.namelist().count(name+'.mcmeta') or (name+'.mcmeta') in z.namelist() or min(im.size)<16 and '/textures/block/' in name:
            skip+=1;continue
        o=style(im,'/textures/item/' in name)
        dst=OUT+name[len('assets/'):]; os.makedirs(os.path.dirname(dst),exist_ok=True); o.save(dst); n+=1
print(n,'styled',skip,'skipped')
