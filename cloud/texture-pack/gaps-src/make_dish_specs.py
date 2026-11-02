"""Per-dish kit specs: archetype from the dish name, food colours from the dish's own 16 px icon, 3D vessel and food parts."""
import json,glob,os,re,colorsys,hashlib,numpy as np,sys
from PIL import Image
SRC='/home/user/work/dish/orig/content/cuisine/kubejs/assets/diaithir/textures/item/dish/'
TX='/home/user/work/dish/kit/tex/'; os.makedirs(TX,exist_ok=True)
def colours(f):
    a=np.array(Image.open(f).convert('RGBA')).reshape(-1,4); a=a[a[:,3]>200][:,:3].astype(float)/255
    hsv=np.array([colorsys.rgb_to_hsv(*p) for p in a])
    keep=(hsv[:,2]>0.18)&~((hsv[:,1]<0.16)&(hsv[:,2]>0.72))      # drop outline and white plate
    k=a[keep] if keep.sum()>6 else a
    main=np.median(k,axis=0); d=((k-main)**2).sum(1); sec=k[np.argsort(-d)[:max(1,len(k)//6)]].mean(0)
    return tuple((main*255).astype(int)),tuple((sec*255).astype(int))
RULES=[('drink',r'tea|coffee|latte|mead|wine|beer|cider|juice|lemonade|milk|smoothie|cocktail|sake|vodka|spirit|brandy|ale$|kvass|grappa|whisk|rum|gin$|tonic|soda|cola|cocoa|chocolate_drink|eggnog|punch|nectar|elixir|posset|kefir|ayran|lassi|horchata|sorbet_drink|water'),
 ('skewer',r'skewer|satay|yakitori|kebab|souvlaki|shashlik|brochette|spiedini'),
 ('tube',r'sausage|frikandel|hot_dog|churro|kielbasa|salami|chorizo|merguez|bratwurst|banana|plantain_stick|spring_roll|burrito|taquito|cigar|pastrami|baguette'),
 ('fish',r'smoked_fish|fish$|salmon|tuna|trout|herring|mackerel|sardine|eel|sushi|sashimi|anchov|cod$|carp|catfish'),
 ('roast',r'pit_roast|roast|steak|ribs|ham$|brisket|joint|rack_of|leg_of|haunch|turkey|chicken$|duck|goose|lamb|cutlet|chop|schnitzel|katsu|tonkatsu|meatloaf|burger'),
 ('mix',r'gathered_mix|trail_mix|forage|medley|assortment'),
 ('cake',r'cake|torte|cheesecake|gateau|tiramisu|brownie|cupcake|muffin'),
 ('pie',r'pie|tart|quiche|pizza|pasty|pastilla|empanada|flan|galette|cobbler|crumble|strudel|baklava|pavlova|tarte'),
 ('bun',r'bun|dumpling|baozi|momo|gyoza|mochi|mooncake|doughnut|donut|beignet|puff|samosa|samsa|pierogi|ravioli|tortellini|knish|bao|dim_sum|croquette|meatball|falafel|arancini|fritter|cookie|biscuit|scone'),
 ('flat',r'bread|naan|roti|lavash|flatbread|paratha|pita|tortilla|blini|pancake|crepe|injera|boxty|waffle|focaccia|arepa|dosa|chapati|tostada|cracker|wafer|toast|loaf|bagel|pretzel|brioche'),
 ('bowl',r'soup|stew|curry|chowder|porridge|congee|ramen|pho|broth|dal|chili|gumbo|goulash|risotto|beans|pudding|salad|noodle|rice|tagine|hide_bag|paella|pilaf|stir_fry|chow|hotpot|bisque|casserole|oatmeal|gruel|pasta|spaghetti|mac_and|lasagna|moussaka|ratatouille|jambalaya|bibimbap|poke|bowl|sauce|dip|hummus|yogurt|jelly|custard|mousse|ice_cream|sorbet|compote')]
def kind(n):
    for k,rx in RULES:
        if re.search(rx,n): return k
    return 'plate'
def hrs(n,i): return int(hashlib.md5((n+str(i)).encode()).hexdigest()[:8],16)/0xffffffff
def foodmat(n,main,sec):
    r=np.random.RandomState(int(hashlib.md5(n.encode()).hexdigest()[:6],16)); N=64
    f=np.fft.fftfreq(N)[:,None]**2+np.fft.fftfreq(N)[None,:]**2; f[0,0]=1
    def fn(b):
        a=np.fft.ifft2(np.fft.fft2(r.randn(N,N))/f**(b/2)).real; a-=a.min(); return a/a.max()
    blot=fn(2.4); sp=(fn(0.8)>0.86).astype(float)
    m=np.array(main,float)[None,None,:]; s=np.array(sec,float)[None,None,:]
    t=np.clip((blot-0.5)*3+0.5,0,1)[...,None]*0.55+sp[...,None]*0.7
    col=m*(1-t)+s*t; col=col*(0.86+0.28*fn(3.0)[...,None])
    Image.fromarray(np.clip(col,0,255).astype('uint8'),'RGB').save(TX+n+'_c.png')
    h=np.clip(0.45*fn(2.0)+0.45*fn(1.0)*0.8+0.4*sp,0,1); Image.fromarray((h*255).astype('uint8'),'L').save(TX+n+'_h.png')
    return {'type':'relief','img':TX+n+'_c.png','hgt':TX+n+'_h.png','disp':0.02,'noise':0.05,'mottle':0.2}
V={'ceramic':{'type':'flat','rgb':[214,208,196],'rough':0.32},'clay':{'type':'flat','rgb':[122,78,52],'rough':0.6},
   'board':{'type':'wood','rgb':[132,96,62]},'glassm':{'type':'glass','rgb':[170,205,215]},'ironm':{'type':'metal','rgb':[88,90,94],'metal':0.8,'rough':0.4,'rust':0.2}}
def box(m,a,b,bv=0.4,**k): d={'part':'box','mat':m,'from':a,'to':b,'geom':True,'bevel':bv}; d.update(k); return d
def cyl(m,a,b,r,bv=0.2,**k): d={'part':'cyl','mat':m,'from':a,'to':b,'r':r,'geom':True,'bevel':bv}; d.update(k); return d
def bits(n,sm,y,rad,cnt=5,sz=0.7):
    o=[]
    for i in range(cnt):
        a=hrs(n,i)*6.28; d=hrs(n,i+9)*rad
        x,z=8+d*np.cos(a),8+d*np.sin(a); o.append(box(sm,[x-sz,y,z-sz],[x+sz,y+sz*1.2,z+sz],0.3))
    return o
def build(n,k,fm,sm):
    p=[]
    if k=='bowl':
        p+=[cyl('clay',[8,5.2,8],[8,8.8,8],5.8,0.8),cyl(fm,[8,8.2,8],[8,9.0,8],4.9,0.5)]+bits(n,sm,9.0,3.6,6)
    elif k=='plate' :
        p+=[cyl('ceramic',[8,6.0,8],[8,6.7,8],6.6,0.25),cyl(fm,[8,6.7,8],[8,8.2,8],4.2,0.9)]+bits(n,sm,8.1,3.2,5)
    elif k=='roast':
        p+=[box('board',[1.5,6,3],[14.5,7,13],0.4),box(fm,[3.5,7,4.5],[12.5,10,11.5],1.6),box(sm,[4.5,10,5.5],[11.5,10.7,10.5],0.5)]
    elif k=='fish':
        p+=[box('board',[1.5,6,3.5],[14.5,7,12.5],0.4),box(fm,[2.5,7,5.5],[13.5,9.2,10.5],1.8),box(sm,[2.0,7,6.6],[4.2,8.2,9.4],0.8),box(sm,[4.5,9.2,6.5],[11.5,9.6,9.5],0.3)]
    elif k=='mix':
        p+=[cyl('board',[8,5.5,8],[8,8.5,8],6.0,0.9),cyl(fm,[8,8.0,8],[8,9.2,8],5.0,0.8)]+bits(n,sm,9.2,4.0,8,0.9)
    elif k=='cake':
        p+=[cyl('ceramic',[8,6.0,8],[8,6.6,8],6.8,0.2),cyl(fm,[8,6.6,8],[8,10.2,8],4.6,0.7),cyl(sm,[8,10.2,8],[8,10.9,8],4.7,0.4)]+bits(n,sm,10.9,3,4,0.8)
    elif k=='pie':
        p+=[cyl('ironm',[8,6.0,8],[8,6.9,8],6.5,0.3),cyl(fm,[8,6.9,8],[8,8.6,8],5.8,0.9),cyl(fm,[8,8.6,8],[8,9.0,8],4.6,0.5)]+bits(n,sm,9.0,3.0,4,0.7)
    elif k=='bun':
        p+=[cyl('ceramic',[8,6.0,8],[8,6.6,8],6.4,0.25),cyl(fm,[5.2,6.6,6],[5.2,9.6,6],3.0,1.2,),cyl(fm,[10.6,6.6,6.5],[10.6,9.2,6.5],2.8,1.2),cyl(fm,[8,6.6,10.4],[8,9.4,10.4],2.9,1.2)]
    elif k=='flat':
        p+=[cyl('board',[8,6.0,8],[8,6.7,8],6.8,0.25),cyl(fm,[8,6.7,8],[8,7.8,8],5.8,0.7),cyl(fm,[8,7.8,8],[8,8.1,8],4.6,0.4)]
    elif k=='tube':
        p+=[cyl(fm,[2.5,8,6],[13.5,8,6],2.0,0.9),cyl(fm,[2.5,8,10],[13.5,8,10],2.0,0.9),cyl(sm,[3,10,8],[13,10,8],0.6,0.1)]
    elif k=='skewer':
        p+=[cyl('board',[1.5,8,8],[14.5,8,8],0.45,0.05)]+[cyl(fm if i%2==0 else sm,[4+i*2.8,8,8],[5.8+i*2.8,8,8],1.9,0.8) for i in range(4)]
    elif k=='drink':
        p+=[cyl('ceramic',[8,5.0,8],[8,10.6,8],3.3,0.5),cyl(fm,[8,10.4,8],[8,11.0,8],2.9,0.2),box('ceramic',[11,6.6,7.2],[13.6,9.6,8.8],0.6)]
    return p
files=sorted(glob.glob(SRC+'*.png')); S=[]; kinds={}
for f in files:
    n=os.path.basename(f)[:-4]; k=kind(n); kinds[n]=k
    main,sec=colours(f); fm,sm=foodmat(n,main,sec),'f_'+n+'_s'
    mats=dict(V); mats['f_'+n]=fm; mats['f_'+n+'_s']={'type':'flat','rgb':[int(c) for c in sec],'rough':0.8}
    S.append({'name':n,'parts':build(n,k,'f_'+n,sm),'views':['icon'],'zoom':0.6,'tilt':28,'materials':mats})
json.dump(S,open('/home/user/work/dish/kit/all.json','w'))
import collections;print(collections.Counter(kinds.values()))
json.dump(kinds,open('/home/user/work/dish/kit/kinds.json','w'))
