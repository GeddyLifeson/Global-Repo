from PIL import Image, ImageDraw, ImageEnhance, ImageChops
import random, os
V="/home/user/diaithirrpg/tools/art/blender/baked/vanilla/assets/minecraft/textures/block/"
O="/home/user/diaithirrpg/tools/art/blender/baked/gaps/assets/"
iron=Image.open(V+"iron_block.png").convert("RGBA")
def out(ref,im):
    ns,p=ref.split(":");f=f"{O}{ns}/textures/{p}.png";os.makedirs(os.path.dirname(f),exist_ok=True);im.convert("RGBA").save(f)
def tint(im,rgb,k=0.5):
    t=Image.new("RGBA",im.size,rgb+(255,));return Image.blend(im,t,k)
def grit(im,seed,n=120):
    r=random.Random(seed);d=ImageDraw.Draw(im)
    for _ in range(n):
        x,y=r.randrange(64),r.randrange(64);c=r.choice([(60,44,34,255),(30,30,32,255),(120,76,44,255)]);d.point((x,y),c)
    return im
def frame(im,col=(40,42,44,255),w=3):
    d=ImageDraw.Draw(im);d.rectangle([0,0,63,63],outline=col,width=w);
    for x,y in((6,6),(57,6),(6,57),(57,57)):d.ellipse([x-2,y-2,x+2,y+2],fill=(70,72,74,255),outline=(20,20,22,255))
    return im
def panel(rgb,seed,k=0.55): return grit(frame(tint(iron,rgb,k)),seed)
white=(196,194,186)
out("cookingforblockheads:block/fridge_side",panel(white,1))
out("cookingforblockheads:block/fridge_back",panel((176,174,168),2))
out("cookingforblockheads:block/fridge_inside",grit(tint(iron,(222,226,230),0.7),3,40))
b=panel((70,72,76),4,0.6);out("cookingforblockheads:block/oven_bottom",b)
def oven(active):
    im=panel((86,88,92),5,0.6);d=ImageDraw.Draw(im)
    d.rectangle([12,18,51,48],fill=(18,18,20,255),outline=(150,150,148,255),width=2)
    if active: d.rectangle([15,24,48,45],fill=(220,110,30,255)); d.rectangle([20,32,43,45],fill=(250,190,60,255))
    d.rectangle([14,9,49,12],fill=(150,60,40,255));return im
out("cookingforblockheads:block/oven_front",oven(False));out("cookingforblockheads:block/oven_front_active",oven(True))
fl=Image.new("RGBA",(64,64));d=ImageDraw.Draw(fl)
for i in range(4):
    for j in range(4): d.rectangle([i*16,j*16,i*16+15,j*16+15],fill=(150,148,142,255) if (i+j)%2 else (96,98,100,255),outline=(50,50,52,255))
out("cookingforblockheads:block/kitchen_floor",grit(fl,6))
out("cobblegengalore:iron_block/side",iron)
dt=panel((70,100,140),7);ImageDraw.Draw(dt).rectangle([0,26,63,38],fill=(40,70,120,255));out("dimstorage:block/dimtank_side",dt)
out("dimstorage:block/dimtank_bottom",panel((60,64,70),8))
for n in (1,2,3):
    t=panel((100,60,60),10+n);d=ImageDraw.Draw(t);d.ellipse([16,16,47,47],outline=(220,90,40,255),width=2+n);out(f"equivox:block/entropy_sink/top_{n}",t)
mu=Image.open(V+"stone_bricks.png").convert("RGBA");out("aether_ii:block/mural",mu)
nb=Image.open(V+"note_block.png").convert("RGBA");out("aether_ii:block/music_block",nb)
out("twilightforest:block/stone_twist/twist_crown",Image.open(V+"smooth_stone.png").convert("RGBA"))
out("dimstorage:block/dimtank_top",panel((60,64,70),9))
# diaithir coal items + blocks live in kit already; coal ore block textures exist
print("ok")
