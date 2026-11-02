"""Specs and map images for the tanning set, rendered through the Diaithir Blender kit (run_kit.py)."""
import json,numpy as np,os,sys
from PIL import Image
BL='/home/user/diaithirrpg/tools/art/blender/'
MAPS=BL+'masters/tan/'; os.makedirs(MAPS,exist_ok=True)
rs=np.random.RandomState(5)
def fnoise(n,beta,seed):
    r=np.random.RandomState(seed); f=np.fft.fftfreq(n)[:,None]**2+np.fft.fftfreq(n)[None,:]**2; f[0,0]=1
    a=np.fft.ifft2(np.fft.fft2(r.randn(n,n))/f**(beta/2)).real; a-=a.min(); return a/a.max()
def pores(n,seed,count=140):
    r=np.random.RandomState(seed); h=np.zeros((n,n))
    yy,xx=np.mgrid[0:n,0:n]
    for _ in range(count):
        cx,cy=r.randint(0,n,2); d=np.minimum(abs(xx-cx),n-abs(xx-cx))**2+np.minimum(abs(yy-cy),n-abs(yy-cy))**2
        h+=np.exp(-d/1.6)*r.uniform(.5,1)
    return np.clip(h,0,1)
def save_h(name,a): Image.fromarray((np.clip(a,0,1)*255).astype('uint8'),'L').save(MAPS+name+'_h.png')
def save_c(name,rgb,shade):
    c=np.array(rgb,float)[None,None,:]*shade[...,None]; Image.fromarray(np.clip(c,0,255).astype('uint8'),'RGB').save(MAPS+name+'_c.png')
N=64
grain=1-0.55*pores(N,1)-0.25*fnoise(N,2.2,2)           # leather: pores plus soft creases
crease=fnoise(N,3.0,3)
lh=np.clip(0.55+0.3*(fnoise(N,2.0,4)-.5)-0.35*pores(N,1)+0.25*(crease-.5),0,1)
hair=np.zeros((N,N)); r=np.random.RandomState(9)
for _ in range(900):                                     # hair-on hide: short strokes
    x,y=r.randint(0,N),r.randint(0,N); l=r.randint(3,7); a=r.uniform(-.4,.4)
    for t in range(l): hair[(y+t)%N,int(x+a*t)%N]=r.uniform(.5,1)
fh=np.clip(0.5*hair+0.5*fnoise(N,2.2,6),0,1)
rope=np.zeros((N,N)); yy,xx=np.mgrid[0:N,0:N]
rope=0.5+0.5*np.sin((yy*2*np.pi/16)+((xx%32)*0.35))  # twisted strands, rows run along x
rope=np.clip(rope*0.8+0.2*fnoise(N,2.4,8),0,1)
TONES={'raw':((118,92,68),fh),'scraped':((214,190,156),lh),'wet':((92,60,40),lh),'supple':((156,98,56),lh),'harness':((112,66,38),lh),
       'hard':((70,44,30),lh),'bind':((150,106,66),lh),'bench':((126,76,44),lh),'fleshraw':((186,104,106),lh),'palehide':((222,216,204),fh),
       'rope':((178,150,100),rope)}
M={}
for k,(rgb,h) in TONES.items():
    shade=0.78+0.4*h if k in('raw','palehide') else 0.8+0.35*h
    save_h('h_'+k,h); save_c('c_'+k,rgb,shade)
    rough=0.85 if k not in('wet','hard') else 0.45
    M['tan_'+k]={'type':'relief','img':'masters/tan/c_%s_c.png'%k,'hgt':'masters/tan/h_%s_h.png'%k,'disp':0.012 if k!='rope' else 0.02,'noise':0.04,'mottle':0.25}
M['tan_steel']={'type':'metal','rgb':[110,114,118],'metal':0.9,'rough':0.34,'rust':0.12,'dirt':0.5,'wear':0.8,'brushed':0.6}
M['tan_wood']={'type':'wood','rgb':[132,92,58],'grain':[0.5,7.0]}
M['tan_woodh']={'type':'wood','rgb':[104,74,50],'vertical':True}
M['tan_woodwet']={'type':'wood','rgb':[58,42,32],'vertical':True,'weather':0.0}
M['tan_woodend']={'type':'endgrain','rgb':[140,100,64]}
M['tan_bark']={'type':'bark','rgb':[84,62,44],'ridges':6,'plates':2.5,'depth':0.04,'lichen':0.2}
M['tan_metal2']={'type':'metal2','rgb':[70,74,80],'metal':0.8,'rough':0.45}
def box(m,a,b,bevel=0.3,**k): d={'part':'box','mat':m,'from':a,'to':b,'geom':True,'bevel':bevel}; d.update(k); return d
def cyl(m,a,b,r,**k): d={'part':'cyl','mat':m,'from':a,'to':b,'r':r,'geom':True}; d.update(k); return d
import math
def outline(s,legs=((.70,4.0,.38),(2.44,4.0,.38),(3.84,4.0,.38),(5.58,4.0,.38)),neck=(4.71,2.8,.30),tail=(1.57,1.6,.18),seed=3):
    r=np.random.RandomState(seed); pts=[]
    for i in range(44):
        th=2*math.pi*i/44; v=3.5+0.35*math.sin(3*th+seed)
        for (c,a,w) in list(legs)+[neck,tail]:
            d=(th-c+math.pi)%(2*math.pi)-math.pi; v+=a*math.exp(-(d/w)**2)
        v+=r.uniform(-.18,.18)
        pts.append([8+s*v*math.cos(th)*1.0,8+s*v*math.sin(th)*1.0])
    return [[round(a,3),round(b,3)] for a,b in pts]
def slab(mat,pts,y0=7.4,y1=8.5,bevel=0.35): return {'part':'slab','mat':mat,'pts':pts,'y0':y0,'y1':y1,'geom':True,'bevel':bevel,'subdiv':4}
def hide(mat,s,seed=3): return [slab(mat,outline(s*0.95,seed=seed))]
S=[]
def item(name,parts,tilt=40,zoom=0.62): S.append({'name':name,'parts':parts,'views':['icon'],'zoom':zoom,'tilt':tilt,'materials':{k:v for k,v in M.items()}})
for sz,s in(('small',.62),('medium',.8),('large',1.0)):
    item(f'{sz}_hide',hide('tan_raw',s,3)); item(f'scraped_hide_{sz}',hide('tan_scraped',s)); item(f'wet_tanned_hide_{sz}',hide('tan_wet',s))
item('supple_leather',[box('tan_supple',[3,6.8,3],[13,7.9,13],.3,rot=[0,0,0]),box('tan_supple',[3.5,7.9,3.5],[12.5,9,12.5],.3,rot=[0,18,0])])
item('harness_leather',[box('tan_harness',[2.5,7,3],[13.5,8.4,13],.35),box('tan_harness',[3,8.4,6.4],[13,9.2,8],.2),box('tan_steel',[7.4,8.4,5.8],[9,9.6,8.6],.15)])
item('hardened_leather',[box('tan_hard',[3,6.6,3],[13,8.4,13],.5),box('tan_hard',[4.5,8.4,4.5],[11.5,9.2,11.5],.5)])
item('binding_leather',[cyl('tan_bind',[5.5,8.6,7],[10.5,8.6,7],3.6),slab('tan_bind',[[8,9.5],[12.5,13.8],[11.6,14.8],[6.8,10.6]],7.2,7.9,.2)],tilt=30)
item('leather_scraps',[slab('tan_scraped',[[2,3],[6,2.4],[8,5],[7,8],[3,7.6]],7.2,8.0,.25),slab('tan_supple',[[9,5],[13.5,6],[14,9.5],[10.5,10.5],[8.5,8]],7.2,8.1,.25),slab('tan_wet',[[4,10],[8,9.6],[9.5,13],[5.5,14],[3,12.5]],7.2,8.0,.25)])
item('bark',[cyl('tan_bark',[2,8,5],[14,8,5],2.6),cyl('tan_bark',[3,8,10.5],[13,8,10.5],2.3),cyl('tan_bark',[2.5,10.4,7.8],[13.5,10.4,7.8],2.1)])
ITEM_AWL=None
item('awl',[box('tan_wood',[6.4,7.5,2.0],[9.6,9.5,6.4],.5),box('tan_steel',[7.4,8.1,6.4],[8.6,9.0,14.6],.12)],tilt=35,zoom=.56)
item('tanners_knife',[box('tan_wood',[6.2,7.5,1.8],[9.8,9.6,6.6],.5),box('tan_steel',[6.6,8.1,6.6],[9.4,9.0,14.8],.15)],tilt=35,zoom=.56)
json.dump(S,open('/home/user/work/tanning/kit/specs.json','w'))
# block material sheets are rendered from these single-part specs (a sheet exists for each material used)
json.dump([{'name':'sheets','parts':[box(k,[0,0,0],[1,1,1],0.0) for k in('tan_bench','tan_rope','tan_woodend','tan_woodh','tan_woodwet','tan_metal2','tan_steel','tan_bark')],'views':['up'],'materials':{k:v for k,v in M.items()}}],open('/home/user/work/tanning/kit/sheets.json','w'))
print(len(S),'item specs')
