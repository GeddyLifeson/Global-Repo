import re,glob,os,sys
B="/home/user/diaithirrpg/tools/art/blender/baked/"
RULES=[("nugget",r"nugget"),
 ("ingot",r"(^|[_./])(ingot|bar)([_./]|$)"),
 ("raw",r"(^|[_./])raw[_.]|_raw$|clump|gravel|chunk|crushed|dirty_|rough|ore_piece"),
 ("dust",r"dust|powder|ground_|^redstone$|gunpowder|ashes|sawdust"),
 ("shard",r"shard|crystal|prism|fragment"),
 ("gem",r"(^|[_./])(gem|spiritus_gem_\w+|diamond|emerald|ruby|sapphire|topaz|peridot|amethyst|amythest|quartz|lapis_lazuli|garnet|opal|tanzanite|jade|onyx|citrine|heliodor|turquoise|zircon|agate|spinel|aquamarine|apatite|moonstone|bloodstone|pearl)(_gem)?$")]
EXCL=r"processor|storage_blocks|window|mcw|summon|heart|active|ring|necklace|glaive|aiot|mace|mold|overlay|charm|pearl_of|amulet|spear|lance|halberd|bow|hammer|scythe|coin|tempura|salmon|cast$|pulling|head|modifier|broken|great|knife|dagger|sickle|staff|wand|sigil|blade|armor|pickaxe|sword|axe|shovel|hoe|helmet|chestplate|leggings|boots|block|ore$|ore_|_ore|template|smithing|egg|bucket|bottle|potion|essence|seed|tool|drill|upgrade|catalyst|augment|cell|capacitor|bee|comb|honey|cluster|bud|lamp|lantern|glass|pane|stairs|slab|wall|torch|cast|mold|gear|plate|rod|wire|coil|casing|part"
def classify(name):
    base=name.split("/")[-1]
    if "/" in name and not name.startswith("materials/"): return None
    if re.search(EXCL,base) and not re.search(r"^(raw_|crushed|dirty_)",base) and "nugget" not in base and not re.search(r"(^|_)(dust|ingot|gem)(_|$)",base): return None
    for k,p in RULES:
        if re.search(p,base): return k
def listing():
    out={}
    for lane in ("items","gaps"):
        for f in glob.glob(B+lane+"/assets/*/textures/item/**/*.png",recursive=True):
            ns=f.split("/assets/")[1].split("/")[0]; rel=f.split("/textures/item/")[1][:-4]
            k=classify(rel)
            if k: out[(ns,rel)]=k
    return out
if __name__=="__main__":
    L=listing();import collections;c=collections.Counter(L.values());print(len(L),c)
    import random;random.seed(1)
    for k in c:
        print(k,[f"{a}:{b}" for (a,b),v in random.sample(sorted(L.items()),len(L)) if v==k][:14])
