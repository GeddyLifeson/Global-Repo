import json,zipfile,glob,os,re,io,sys
from PIL import Image
sys.path.insert(0,"/home/user/diaithirrpg/tools/art/blender")
audit=json.load(open("/mnt/project-files/audit/assets_missing.json"))
jar={}
for j in glob.glob("/home/user/work/modjars/*.jar")+glob.glob("/home/user/work/packsrc/mods/*.jar"):
    try: z=zipfile.ZipFile(os.path.realpath(j))
    except Exception: continue
    for n in z.namelist():
        if n.startswith("assets/"): jar.setdefault(n,z)
kjs={k.split("kubejs/")[1] for k in glob.glob("/home/user/work/packsrc/kubejs/assets/**/*.*",recursive=True)}
has=lambda p:p in jar or p in kjs
COL={"platinum":(190,205,215),"silver":(190,194,200),"gold":(214,170,60),"iron":(150,140,135),"copper":(184,102,60),"tin":(170,180,185),"lead":(100,104,126),"nickel":(168,170,150),"zinc":(160,170,170),"aluminum":(176,184,190),"aluminium":(176,184,190),"osmium":(120,160,190),"uranium":(110,160,70),"iridium":(210,214,222),"diamond":(90,220,210),"emerald":(60,200,100),"quartz":(226,222,212),"pearl":(226,222,214),"lapis":(50,80,170),"redstone":(190,40,30),"coal":(36,34,36),"vibranium":(140,60,190),"unobtainium":(150,70,200),"allthemodium":(230,170,40),"neovitae":(150,20,30),"blood":(150,20,30),"black":(34,34,38),"white":(220,218,210),"red":(180,50,40),"blue":(50,90,170),"green":(60,140,60),"yellow":(210,180,50),"orange":(210,120,40),"purple":(120,60,160),"pink":(210,120,150),"magenta":(170,60,150),"cyan":(50,150,170),"lime":(120,190,50),"brown":(110,76,48),"gray":(110,110,112),"grey":(110,110,112),"tan":(190,160,110),"silver":(190,194,200),"bronze":(176,120,60),"steel":(140,148,155),"fire":(214,92,30),"rainbow":(150,100,200),"salt":(226,222,214),"sulfur":(210,200,60),"sulfuric":(210,200,60),"mercury":(180,184,190),"caloric":(210,100,40)}
def colour(name):
    for w in re.split(r"[_/.\-]",name):
        if w in COL: return COL[w]
    return (140,138,132)
def png(c):
    b=io.BytesIO(); Image.new("RGBA",(16,16),c+(255,)).save(b,"PNG"); return b.getvalue()
items=[]      # ns,path,texture ref, has_model, has_tex
for i,r in audit:
    ns,p=i.split(":",1)
    if "no item definition" in r:
        items.append((ns,p))
# aether tex-missing item textures
extra=[]
for ref in ["aether_ii:item/armor_charm_runes_agility","aether_ii:item/armor_charm_runes_defense","aether_ii:item/armor_charm_runes_health","aether_ii:item/armor_charm_runes_resistance","aether_ii:item/armor_charm_runes_toughness","aether_ii:item/tool_charm_runes_efficiency","aether_ii:item/tool_charm_runes_reach","aether_ii:item/weapon_charm_runes_damage","aether_ii:item/weapon_charm_runes_dexterity","aether_ii:item/weapon_charm_runes_knockback","silentgear:item/trident"]:
    extra.append(ref)
for ip in ["moa_egg","moa_feather"]:
    s=jar[f"assets/aether_ii/items/{ip}.json"].read(f"assets/aether_ii/items/{ip}.json").decode()
    for t in sorted(set(re.findall(r'"(aether_ii:item/[a-z_]+)"',s))):
        if not has(f"assets/aether_ii/textures/{t.split(':')[1]}.png"): extra.append(t)
print(len(items),len(extra))
json.dump({"items":items,"extra":extra},open("list.json","w"))
