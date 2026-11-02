"""Dish icon specs v2: vessel from the catalogue's shape, food built from the dish's own recipe ingredients."""
import json,glob,os,re,colorsys,hashlib,collections,numpy as np,sys
sys.path.insert(0,'/home/user/work/dish/kit')
from PIL import Image
import importlib.util
spec=importlib.util.spec_from_file_location('v1','/home/user/work/dish/kit/make_dish_specs.py')
SRC='/home/user/work/dish/orig/content/cuisine/kubejs/assets/diaithir/textures/item/dish/'
TX='/home/user/work/dish/kit/tex/'
src=open('/home/user/work/dish/kit/make_dish_specs.py').read().split("files=sorted(glob.glob")[0]
exec(src)                      # colours, foodmat, V, box, cyl, bits, hrs
C=json.load(open('/home/user/work/dish/cuisine.json'))
REC=collections.defaultdict(list)
for r in C['recipes']: REC[r['o']].append(r)
SHAPE={x[0].split('/')[-1]:x[4] for x in C['dishes']}
# ingredient keyword -> (part kind, rgb, priority)   lower priority number = shown first
ING=[(r'beef|steak|brisket|lamb|mutton|venison|boar|bush_meat|bison|goat|oxtail|seal_meat|hedgehog|pigeon|rabbit|veal|pork|bacon|ham$|sausage|chorizo|mince|ground_|liver|heart|kidney|tripe|rib|shank|belly|hock|whale|jerky|meat','chunk',(120,66,46),0),
 (r'chicken|turkey|duck|goose|quail|pheasant|fowl|wing|thigh|drumstick','chunk',(200,150,96),0),
 (r'salmon|tuna|trout|snapper|herring|pike|cod|haddock|mackerel|sardine|anchovy|carp|catfish|eel|halibut|bass|bream|fish(?!_sauce)|swordfish|tilapia|bonito','fillet',(222,128,100),0),
 (r'shrimp|prawn|crab|lobster|crayfish|langoustine|krill','shrimp',(226,104,64),0),
 (r'clam|mussel|oyster|snail|scallop|cockle|abalone|paua|squid|octopus|calamari|urchin','shell',(196,184,170),0),
 (r'grub|worm|cricket|insect|locust|termite|ant','grub',(214,196,150),0),
 (r'egg(?!_white_ferment)|yolk','egg',(244,238,226),1),
 (r'tofu|tempeh|paneer|halloumi','wedge',(236,226,196),1),
 (r'cheese|parmesan|feta|mozzarella|cheddar|gruyere|ricotta|mascarpone|curd','wedge',(236,190,70),1),
 (r'rice|couscous|quinoa|bulgur|barley|millet|farro|semolina|sago|tapioca|oats|teff|amaranth|grits|polenta|cornmeal','grains',(238,232,214),2),
 (r'noodle|pasta|spaghetti|vermicelli|macaroni|ramen|udon|soba|linguine|fettuccine|lasagna','strands',(236,214,150),2),
 (r'bean|lentil|chickpea|pea$|green_pea|peas|edamame|adzuki|lima|fava|soy_bean|peanut','beans',(150,96,56),2),
 (r'tomato|bush_tomato|cherry|strawberry|raspberry|cranberry|lingonberry|pomegranate|radish|beet','ball',(196,44,36),3),
 (r'blueberry|blackberry|elderberry|bilberry|grape|plum|juniper|olive|aronia|currant|acai','ball',(70,58,110),3),
 (r'apple|lemon|lime|orange|banana|mango|peach|pear|apricot|pineapple|papaya|guava|lychee|date|fig|coconut|citrus|tangerine|yuzu|calamansi','ball',(228,172,56),3),
 (r'pepper|chile|chili|scotch_bonnet|emberpepper|capsicum|paprika|bellpepper|jalapeno|habanero|pimento','ball',(200,48,32),3),
 (r'carrot|pumpkin|squash|sweet_potato|yam|turnip|parsnip|swede|kumara|cassava|taro|ube','disc',(224,120,40),3),
 (r'potato|plantain|breadfruit|jicama|celeriac|salsify|chestnut|acorn|corn|maize|hominy','chunk',(216,184,112),3),
 (r'cucumber|zucchini|courgette|celery|leek|eggplant|aubergine|okra|artichoke|asparagus|cabbage|broccoli|cauliflower|bok_choy|kale|chard','disc',(120,162,70),3),
 (r'spinach|lettuce|nettle|dock|cress|sorrel|arugula|greens|kale|leaf|seaweed|nori|kombu|wakame|dulse|ti_leaf|molokhia|collard|vertical','leaf',(66,126,52),4),
 (r'mushroom|morel|porcini|shiitake|enoki|truffle|chanterelle','cap',(150,110,74),3),
 (r'onion|shallot|garlic|ginger|scallion|chive|wild_garlic|ramp','disc',(236,226,200),5),
 (r'parsley|cilantro|coriander|dill|mint|basil|thyme|oregano|rosemary|sage|tarragon|chervil|marjoram|lovage|bay|herb|lemongrass|shiso|perilla|epazote|culantro','fleck',(70,140,60),6),
 (r'almond|walnut|hazelnut|pistachio|cashew|pine_nut|macadamia|pecan|chestnut|nut|seed|sesame|poppy|sunflower|flax|chia','nuts',(190,150,96),6),
 (r'cream|yoghurt|yogurt|sour_cream|labneh|kefir|skyr|buttermilk|coconut_milk|milk|butter|ghee|moonmilk|mascarpone','dollop',(246,242,232),7),
 (r'chocolate|cocoa','dollop',(66,40,30),7),
 (r'honey|thunderhoney|syrup|jaggery|brown_sugar|sugar|caramel','dollop',(214,150,40),7),
 (r'cinnamon|cardamom|cumin|turmeric|saffron|nutmeg|clove|allspice|star_anise|curry|garam|masala|pepper_|sumac|zaatar|harissa|berbere|mustard|vanilla|spice|paprika','fleck',(196,120,40),8)]
def classify(i):
    n=i.split(':')[1].split('/')[-1]
    for rx,k,c,p in ING:
        if re.search(rx,n): return k,c,p,n
    return None
def spots(n,r,cnt,seed=0):
    out=[]
    for i in range(cnt):
        a=hrs(n,seed+i)*6.2832; d=(0.25+0.75*hrs(n,seed+i+50))*r
        out.append((8+d*np.cos(a),8+d*np.sin(a)))
    return out
def part_for(kind,rgb,y,n,rad,mats,seed):
    key='ing_%d_%d_%d'%rgb; mats[key]={'type':'flat','rgb':list(rgb),'rough':0.7}
    out=[]
    if kind=='chunk':
        for i,(x,z) in enumerate(spots(n,rad,4,seed)): out.append(box(key,[x-1,y,z-1],[x+1.1,y+1.3,z+1.0],0.55,rot=[0,hrs(n,seed+i)*90,0]))
    elif kind=='fillet':
        x,z=spots(n,rad*0.5,1,seed)[0]; out.append(box(key,[x-2.6,y,z-1.2],[x+2.6,y+1.0,z+1.2],0.5,rot=[0,hrs(n,seed)*60-30,0]))
    elif kind=='shrimp':
        for i,(x,z) in enumerate(spots(n,rad,3,seed)): out.append(cyl(key,[x-1.6,y+0.6,z],[x+1.6,y+0.6,z],0.8,0.4))
    elif kind=='shell':
        for i,(x,z) in enumerate(spots(n,rad,4,seed)): out.append(cyl(key,[x,y,z],[x,y+1.0,z],1.1,0.5))
    elif kind=='grub':
        for i,(x,z) in enumerate(spots(n,rad,4,seed)): out.append(cyl(key,[x-1.1,y+0.5,z],[x+1.1,y+0.5,z],0.65,0.3))
    elif kind=='egg':
        x,z=spots(n,rad*0.5,1,seed)[0]; out+=[cyl(key,[x,y,z],[x,y+0.5,z],2.0,0.3)]; mats['yolk']={'type':'flat','rgb':[236,170,40],'rough':0.4}; out.append(cyl('yolk',[x,y+0.5,z],[x,y+1.3,z],0.9,0.4))
    elif kind=='wedge':
        for i,(x,z) in enumerate(spots(n,rad,3,seed)): out.append(box(key,[x-1,y,z-1],[x+1.1,y+1.1,z+0.9],0.3,rot=[0,hrs(n,seed+i)*90,0]))
    elif kind=='grains':
        for i,(x,z) in enumerate(spots(n,rad,16,seed)): out.append(box(key,[x-.35,y,z-.2],[x+.35,y+.45,z+.2],0.15,rot=[0,hrs(n,seed+i)*180,0]))
    elif kind=='strands':
        for i in range(5): z=8-rad*0.5+i*rad*0.25; out.append(cyl(key,[8-rad*0.55,y+0.2,z],[8+rad*0.55,y+0.2,z],0.4,0.1))
    elif kind=='beans':
        for i,(x,z) in enumerate(spots(n,rad,8,seed)): out.append(cyl(key,[x,y,z],[x,y+0.7,z],0.6,0.3))
    elif kind=='ball':
        for i,(x,z) in enumerate(spots(n,rad,4,seed)): out.append(cyl(key,[x,y,z],[x,y+1.3,z],0.95,0.5))
    elif kind=='disc':
        for i,(x,z) in enumerate(spots(n,rad,5,seed)): out.append(cyl(key,[x,y,z],[x,y+0.4,z],1.0,0.15))
    elif kind=='leaf':
        for i,(x,z) in enumerate(spots(n,rad,4,seed)): out.append(box(key,[x-1.3,y,z-0.8],[x+1.3,y+0.35,z+0.8],0.2,rot=[0,hrs(n,seed+i)*150,0]))
    elif kind=='cap':
        for i,(x,z) in enumerate(spots(n,rad,3,seed)): out.append(cyl(key,[x,y,z],[x,y+0.9,z],1.1,0.45))
    elif kind=='nuts':
        for i,(x,z) in enumerate(spots(n,rad,7,seed)): out.append(box(key,[x-.4,y,z-.4],[x+.4,y+.7,z+.4],0.25))
    elif kind=='dollop':
        x,z=spots(n,rad*0.4,1,seed)[0]; out.append(cyl(key,[x,y,z],[x,y+1.2,z],1.5,0.7))
    else:  # fleck
        for i,(x,z) in enumerate(spots(n,rad,9,seed)): out.append(box(key,[x-.3,y,z-.3],[x+.3,y+.3,z+.3],0.1))
    return out
def toppings(n,ing,y,rad,mats):
    got={};
    for i in ing:
        c=classify(i)
        if c and c[0] not in got: got[c[0]]=c
    pick=sorted(got.values(),key=lambda c:c[2])[:4]
    out=[]
    for k,(kind,rgb,p,nm) in enumerate(pick): out+=part_for(kind,rgb,y,n,rad,mats,k*17)
    return out,pick
def vessel(n,shape,fm,sm,ing,mats):
    p=[]
    if shape=='plate':
        p+=[cyl('ceramic',[8,6.0,8],[8,6.7,8],6.6,0.25),cyl(fm,[8,6.7,8],[8,7.7,8],4.8,0.8)]; t,_=toppings(n,ing,7.6,4.0,mats); p+=t
    elif shape=='bowl':
        vm='clay' if hrs(n,3)>0.5 else 'ceramic'
        p+=[cyl(vm,[8,5.2,8],[8,8.8,8],5.8,0.8),cyl(fm,[8,8.2,8],[8,9.0,8],4.9,0.5)]; t,_=toppings(n,ing,8.9,3.8,mats); p+=t
    elif shape=='cookie':
        p+=[cyl('board',[8,6.0,8],[8,6.7,8],6.6,0.25)]
        for i,(x,z) in enumerate([(5.2,6.2),(10.6,6.6),(8,10.6)]): p+=[cyl(fm,[x,6.7,z],[x,7.8,z],2.6,0.7)]+[box(sm,[x+dx-.35,7.7,z+dz-.35],[x+dx+.35,8.1,z+dz+.35],0.1) for dx,dz in((-0.8,-0.5),(0.7,0.4),(0.1,-1.0))]
    elif shape=='sausage':
        p+=[cyl(fm,[2.5,8,6],[13.5,8,6],2.0,0.9),cyl(fm,[2.5,8,10],[13.5,8,10],2.0,0.9)]
    elif shape=='cup':
        p+=[cyl('ceramic',[8,5.0,8],[8,10.6,8],3.3,0.5),cyl(fm,[8,10.4,8],[8,11.0,8],2.9,0.2),box('ceramic',[11,6.6,7.2],[13.6,9.6,8.8],0.6)]
    elif shape=='pie':
        p+=[cyl('ironm',[8,6.0,8],[8,6.9,8],6.5,0.3),cyl(fm,[8,6.9,8],[8,8.8,8],5.8,0.9)]+[box(sm,[3.2,8.8,7.5+i*1.5],[12.8,9.3,8.4+i*1.5],0.2) for i in range(-1,2)]+[box(sm,[7.5+i*1.5,8.8,3.2],[8.4+i*1.5,9.3,12.8],0.2) for i in range(-1,2)]
    elif shape=='flat':
        p+=[cyl('board',[8,6.0,8],[8,6.7,8],6.8,0.25),cyl(fm,[8,6.7,8],[8,7.7,8],5.9,0.7)]; t,_=toppings(n,ing,7.7,4.2,mats); p+=t
    elif shape=='jar':
        p+=[cyl('glassm',[8,5.0,8],[8,10.4,8],3.5,0.6),cyl(fm,[8,5.4,8],[8,11.0,8],3.0,0.4),cyl('ironm',[13.5,5.0,9],[13.5,5.8,9],2.4,0.3)]
    elif shape=='loaf':
        p+=[box('board',[1.5,6,4],[14.5,6.8,12],0.3),box(fm,[2.8,6.8,5],[13.2,8.8,11],1.1),box(fm,[3.4,8.6,5.6],[12.6,9.8,10.4],1.4)]+[box(sm,[4.5+i*2.4,9.5,6.4],[5.2+i*2.4,10,9.6],0.15,rot=[0,20,0]) for i in range(3)]
    elif shape=='wrap':
        t,pick=toppings(n,ing,0,1,{})
        p+=[cyl(fm,[2.5,8,8],[13.5,8,8],2.5,1.0)]
        for i,(kind,rgb,pr,nm) in enumerate(pick[:3]):
            key='ing_%d_%d_%d'%rgb; mats[key]={'type':'flat','rgb':list(rgb),'rough':0.7}; p.append(cyl(key,[12.2+i*0.2,8.2,7.2+i*0.7],[14.4,8.2,7.2+i*0.7],0.9,0.5))
    elif shape=='skewer':
        _,pick=toppings(n,ing,0,1,{}); cols=[pk[1] for pk in pick] or [tuple(int(v) for v in sm.__class__ and (160,110,70))]
        p+=[cyl('board',[1.5,8,8],[14.5,8,8],0.45,0.05)]
        for i in range(4):
            c=cols[i%len(cols)]; key='ing_%d_%d_%d'%tuple(c); mats[key]={'type':'flat','rgb':list(c),'rough':0.7}; p.append(cyl(key,[4+i*2.8,8,8],[5.8+i*2.8,8,8],1.9,0.8))
    elif shape=='cake':
        p+=[cyl('ceramic',[8,6.0,8],[8,6.6,8],6.8,0.2),cyl(fm,[8,6.6,8],[8,10.2,8],4.6,0.7),cyl(sm,[8,10.2,8],[8,10.9,8],4.7,0.4)]; t,_=toppings(n,ing,10.9,3.0,mats); p+=t
    elif shape=='wheel':
        p+=[cyl(fm,[8,6,8],[8,10,8],5.6,0.8),box(sm,[11,6.2,6.5],[14,8.6,9.5],0.4,rot=[0,25,0])]
    else:
        p+=[cyl('ceramic',[8,6.0,8],[8,6.7,8],6.6,0.25),cyl(fm,[8,6.7,8],[8,8.2,8],4.2,0.9)]
    return p
S=[];cnt=collections.Counter()
for f in sorted(glob.glob(SRC+'*.png')):
    n=os.path.basename(f)[:-4]; shape=SHAPE.get(n,'plate'); cnt[shape]+=1
    main,sec=colours(f); fm=foodmat(n,main,sec); smk='f_'+n+'_s'
    mats=dict(V); mats['f_'+n]=fm; mats[smk]={'type':'flat','rgb':[int(c) for c in sec],'rough':0.8}
    ing=[]
    for r in REC.get('diaithir:dish/'+n,[])[:2]: ing+=list(r['i'].keys())
    S.append({'name':n,'parts':vessel(n,shape,'f_'+n,smk,ing,mats),'views':['icon'],'zoom':0.6,'tilt':28,'materials':mats})
json.dump(S,open('/home/user/work/dish/kit/all2.json','w')); print(cnt,len(S))
