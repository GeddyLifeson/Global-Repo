# S6866 Generates ANIMATIONS_COVERAGE.csv: one row per entity, block entity, interactive block, item use action, profession, spell, vehicle and player action from the pack registries plus our rewrite jars; assigns owner helpers 1-4.
# Usage: python3 -I gen_animations_coverage.py [OUT_DIR]   (default /mnt/project-files/plans). Rerun any time; keeps status of existing rows.
import csv, gzip, json, re, sys, zipfile, glob, pathlib, collections
PM = pathlib.Path('/mnt/project-files/packmap'); REG = PM / 'registries'
JARS = '/mnt/project-files/rewrite-jars/**/*.jar'
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/plans')
H1, H2, H3, H4 = '1-body-firstperson', '2-melee-guns', '3-mobs-npcs-bosses', '4-machines-blocks-vehicles'
COLS = ['id', 'category', 'namespace', 'thing', 'kind', 'animations_needed', 'engine_route', 'owner', 'status', 'source']

def reg(n): return json.load(open(REG / (n + '.json')))
dump = json.load(gzip.open(PM / 'pack_dump.json.gz'))
tags = dump['tags']
def tagged(*names):
    s = set()
    for n in names:
        for i in tags.get(n, []):
            if isinstance(i, dict): i = i.get('id', '')
            if i and not i.startswith('#'): s.add(i)
    return s

# ids from our rewrite jars (newer than the registry dump) and existing animation assets
jar_ids = {'entity': set(), 'block': set(), 'item': set()}
anim_assets = set()
for j in glob.glob(JARS, recursive=True):
    try: z = zipfile.ZipFile(j)
    except Exception: continue
    for n in z.namelist():
        if re.search(r'(animations?|geo)/[^/]+\.json$', n): anim_assets.add(pathlib.PurePath(n).stem)
        if n.endswith('/lang/en_us.json'):
            try: lang = json.loads(z.read(n))
            except Exception: continue
            for k in lang:
                m = re.match(r'(entity|block|item)\.([a-z0-9_]+)\.([a-z0-9_./]+)$', k)
                if m: jar_ids[m[1]].add(m[2] + ':' + m[3].replace('.', '/'))

rows = []
def add(cat, ns, thing, kind, need, route, owner, source):
    rows.append(dict(category=cat, namespace=ns, thing=thing, kind=kind, animations_needed=need,
                     engine_route=route, owner=owner, status='todo', source=source))
ns_of = lambda i: i.split(':')[0]

# ---- entities
VEH_NS = {'mts', 'immersive_aircraft', 'aviator_dream', 'valkyrienskies', 'man_of_many_planes', 'diaithir_carts', 'railcraft'}
VEH_RE = re.compile(r'boat|raft|minecart|cart$|_cart|aircraft|airship|plane|helicopter|zeppelin|car$|truck|tank|ship|vehicle|bike|train|locomotive|balloon|ufo|rocket')
PROJ_RE = re.compile(r'arrow|bolt|bullet|fireball|projectile|thrown|snowball|egg$|pearl|potion|trident|shot|missile|dart|laser|spit|orb|charge|needle|cannonball|grenade|wind_charge|firework|spell|beam|slash|wave|blast')
MISC_RE = re.compile(r'item$|item_frame|painting|marker|display|experience|xp_|area_effect|lightning|armor_stand|falling_block|tnt|interaction|leash|evoker_fangs|ominous|primed|effect_cloud|bobber|decoration|seat|stand$')
BOSS_RE = re.compile(r'boss|dragon|wither|warden|lich|titan|colossus|ancient|elder|sovereign|wyrm|seraph|reaver|overlord|king$|queen$|hydra|ravager|naga|ur_ghast|minoshroom|alpha_yeti|snow_queen|knight_phantom|gorgon|cyclops')
NPC_NS = {'easy_npc', 'mca', 'millager', 'villager_trading_plus'}
NPC_RE = re.compile(r'villager|npc|trader|merchant|guard|citizen|settler|vendor|banker|innkeeper|priest|blacksmith|librarian')
REGENT = set(reg('entity_type'))
for e in sorted(REGENT | jar_ids['entity']):
    ns, name = e.split(':', 1)
    src = 'registry' if e in REGENT else 'rewrite-jar'
    if ns in VEH_NS or VEH_RE.search(name):
        add('vehicle', ns, e, 'entity', 'idle,drive/fly/sail,steer,brake,seats,driver hands,wheels,propellers,hatches,damage,destroyed', 'Immersive Vehicles + GeckoLib + PAL seats', H4, src)
    elif re.search(r'(egg|skull)$', name):
        add('entity-misc', ns, e, 'entity', 'spawn,idle,hit,despawn (spin/bob/pop as fits)', 'GeckoLib or vanilla renderer tweaks', H3, src)
    elif PROJ_RE.search(name) and (not BOSS_RE.search(name) or re.search(r'(charge|arrow|breath|bolt|shot)$', name)):
        add('projectile', ns, e, 'entity', 'launch,flight spin,trail,impact,despawn', 'GeckoLib/particles; pairs with the weapon that fires it', H2, src)
    elif BOSS_RE.search(name) or ns == 'diaithirbosses':
        add('boss', ns, e, 'entity', 'idle,walk,run,melee x3,ranged,special,phase change,rite wake,roar,hurt,death', 'GeckoLib + PAL', H3, src)
    elif MISC_RE.search(name):
        add('entity-misc', ns, e, 'entity', 'spawn,idle,hit,despawn (spin/bob/pop as fits)', 'GeckoLib or vanilla renderer tweaks', H3, src)
    elif ns in NPC_NS or NPC_RE.search(name):
        add('npc', ns, e, 'entity', 'idle,walk,run,work,talk,trade,sit,sleep,hurt,death,wave,gesture', 'GeckoLib + PAL', H3, src)
    else:
        extra = ''
        if re.search(r'bird|bat|bee|parrot|fly|wing|butterfly|dragonfly|phantom|owl|eagle|hawk|crow|vulture|allay|vex|ghast', name): extra += ',fly,glide,land'
        if re.search(r'fish|cod|salmon|squid|shark|whale|dolphin|turtle|frog|axolotl|guardian|eel|ray|jelly|crab|lobster|nautilus', name): extra += ',swim,flop'
        add('mob', ns, e, 'entity', 'idle,walk,run,attack,hurt,death,sleep,eat,look,sit' + extra, 'GeckoLib + EMF/ETF', H3, src)
    if name in anim_assets: rows[-1]['status'] = 'asset-exists'

# ---- villager professions and NPC activities
for p in reg('villager_profession'):
    add('npc', ns_of(p), p, 'profession', 'work at station,talk,trade,sit,sleep,celebrate', 'GeckoLib + PAL', H3, 'registry')
for a in reg('activity'):
    add('npc', ns_of(a), a, 'activity', 'activity pose/loop', 'GeckoLib + PAL', H3, 'registry')

# ---- block entities and interactive blocks
bes = set(reg('block_entity_type'))
def be_need(n):
    if re.search(r'chest|barrel|shulker|crate|drawer|cabinet|locker|safe|box|bin|cupboard|wardrobe|trunk', n): return 'idle,open,close,lid/drawer motion'
    if re.search(r'tank|fluid|drum|cistern|reservoir|vat|cauldron|keg', n): return 'idle,fill level,flow,drain'
    if re.search(r'turret|cannon|gun|sentry|laser|tesla|trap', n): return 'idle,track,fire,reload,destroyed'
    if re.search(r'door|gate|hatch|portcullis|drawbridge|trapdoor', n): return 'open,close'
    if re.search(r'sign|banner|flag|head|skull|bed|lectern|book|shelf|frame|mount|pot|jar|lantern|lamp|torch|candle', n): return 'idle,sway/flicker,interact'
    if re.search(r'pipe|cable|conduit|duct|wire|belt|conveyor|rail|tube|channel', n): return 'idle,item/fluid/energy flow,connection change'
    if re.search(r'generator|engine|reactor|turbine|boiler|furnace|smelter|crusher|press|mill|grinder|pulverizer|centrifuge|assembler|crafter|macerator|compressor|extractor|refinery|forge|kiln|oven|processor|synthesizer|fabricator|incinerator|infuser|enchant|altar|ritual|anvil|workbench|table|station', n): return 'idle,working loop,done,jam/no-power'
    return 'idle,working,done'
JB = {i for i in jar_ids['block'] if re.search(r'machine|generator|furnace|press|chest|tank|station|altar|belt|turret', i)}
STATICBE = r'chest|barrel|door|gate|sign|banner|bed|head|skull|lectern|shelf|frame|pot|jar|lantern|lamp|torch|candle|trapdoor'
for b in sorted(bes | JB):
    ns, name = b.split(':', 1)
    r = 'GeckoLib; Foundry belts' if re.search(r'belt|conveyor|splitter|inserter|arm', name) else 'GeckoLib block entity renderer'
    add('block-entity' if re.search(STATICBE, name) else 'machine', ns, b, 'block entity', be_need(name), r, H4, 'registry' if b in bes else 'rewrite-jar')

BLK = [  # (regex, group, animations)
    (r'(^|_)trapdoor', 'trapdoor', 'open,close'), (r'(^|_)door($|_)', 'door', 'open,close,knock'),
    (r'fence_gate|gate$', 'gate', 'open,close'), (r'lever', 'lever', 'toggle'),
    (r'button', 'button', 'press'), (r'pressure_plate', 'pressure plate', 'press,release'),
    (r'piston', 'piston', 'extend,retract'), (r'(^|_)bell$', 'bell', 'ring swing'),
    (r'campfire|furnace|smoker|blast_furnace', 'fire block', 'lit loop,flicker'), (r'torch|lantern|candle|lamp', 'light block', 'flicker'),
    (r'chest|barrel|shulker_box|crate|drawer', 'storage block', 'open,close'), (r'bed$', 'bed', 'sleep pose'),
    (r'leaves|grass|fern|flower|sapling|vine|reed|bush|crop|wheat|kelp|seagrass|lily|moss_carpet|petals|mushroom', 'foliage', 'wind sway'),
    (r'water|lava|fluid', 'fluid', 'flow'), (r'portal', 'portal', 'swirl loop'), (r'sign|banner|flag', 'cloth/sign', 'wind sway'),
]
AMBIENT = ('foliage', 'fluid', 'light block', 'cloth/sign')  # summarised per namespace, not one row each
grp = collections.Counter()
REGB = set(reg('block'))
for b in sorted(REGB | jar_ids['block']):
    ns, name = b.split(':', 1)
    for rx, g, need in BLK:
        if re.search(rx, name):
            grp[(ns, g)] += 1
            if g not in AMBIENT and b not in bes:
                add('block', ns, b, 'block', need, 'GeckoLib or block-state model animation', H4, 'registry' if b in REGB else 'rewrite-jar')
            break
    else: grp[(ns, 'static')] += 1

# ---- items: use actions from tags and name patterns
IT = set(reg('item')) | jar_ids['item']
def names(rx, exclude=None): return {i for i in IT if re.search(rx, i) and not (exclude and re.search(exclude, i))}
USE = [
    ('sword', tagged('minecraft:swords') | names(r'(^|_)(sword|saber|sabre|rapier|katana|claymore|scimitar|cutlass|blade)$'), 'swing x3 combo,thrust,block,sheathe'),
    ('axe', tagged('minecraft:axes') | names(r'(^|_)axe$|battleaxe'), 'swing x3,chop'),
    ('pickaxe', tagged('minecraft:pickaxes') | names(r'pickaxe'), 'mine swing'),
    ('shovel', tagged('minecraft:shovels') | names(r'shovel|spade'), 'dig swing'),
    ('hoe', tagged('minecraft:hoes') | names(r'(^|_)hoe$'), 'till swing'),
    ('spear', tagged('c:tools/trident') | names(r'spear|lance|pike|halberd|glaive|javelin|trident'), 'thrust,throw,charge'),
    ('mace/hammer', tagged('c:tools/mace') | names(r'(^|_)(mace|hammer|club|flail|maul)$|warhammer'), 'overhead swing,smash'),
    ('staff/wand', names(r'(^|_)(staff|wand|scepter|sceptre)$|caster', 'fishing'), 'cast raise,channel,release'),
    ('dagger/knife', tagged('c:tools/knife') | names(r'dagger|knife|dirk|kris|stiletto'), 'stab,slash,throw'),
    ('bow', tagged('c:tools/bow', 'minecraft:enchantable/bow') | names(r'(^|_)bow$|longbow'), 'draw,hold,release,nock'),
    ('crossbow', tagged('c:tools/crossbow') | names(r'crossbow'), 'load,aim,fire'),
    ('gun', tagged('c:tools/ranged_weapon') | names(r'(^|_)(gun|rifle|pistol|shotgun|musket|revolver|smg|carbine|blunderbuss|cannon|launcher|minigun|sniper|flamethrower)(_|$)|^pointblank:'), 'hold,aim,fire,reload,inspect,sprint-lower'),
    ('shield', tagged('c:tools/shield') | names(r'shield'), 'raise,block hit,lower'),
    ('shears', tagged('c:tools/shear') | names(r'shears'), 'snip'),
    ('fishing rod', tagged('c:tools/fishing_rod') | names(r'fishing_rod'), 'cast,wait,reel'),
    ('wrench/tool', tagged('c:tools/wrench', 'c:tools/brush', 'c:tools/igniter') | names(r'wrench|screwdriver|multimeter|scanner|brush$|flint_and_steel'), 'use/apply'),
    ('food', tagged('c:foods', 'minecraft:fishes'), 'eat (bite loop)'),
    ('drink/potion', tagged('c:drinks', 'c:potions', 'c:potions/bottle', 'c:drink_containing/bottle'), 'drink (tilt,sip)'),
    ('throwable', names(r'snowball|ender_pearl|egg$|grenade|bomb|throwing|molotov|thrown'), 'wind-up,throw'),
    ('spell/scroll', names(r'scroll|spell_book|spellbook|grimoire|tome|rune_stone'), 'open,read,cast'),
    ('horn/instrument', names(r'horn|flute|lute|drum|lyre|harp|trumpet|bagpipe|whistle|ocarina|violin|instrument'), 'play'),
    ('spyglass/map', names(r'spyglass|telescope|binocular|(^|_)map$|compass$|clock$'), 'raise to eye,read'),
    ('elytra/wings', names(r'elytra|wings|jetpack|glider|parachute'), 'deploy,glide,flap,fold'),
    ('mount gear', names(r'saddle|lead$|harness'), 'equip,mount'),
]
H1G = {'food', 'drink/potion', 'fishing rod', 'spyglass/map', 'wrench/tool', 'spell/scroll', 'horn/instrument', 'mount gear', 'elytra/wings', 'throwable'}
claimed = set(); itemrows = 0
for g, ids, need in USE:
    for i in sorted(ids & IT):
        if i in claimed: continue
        claimed.add(i)
        owner = H1 if g in H1G else H2
        cat = 'item-use' if owner == H1 else ('gun' if g == 'gun' else 'melee')
        add(cat, ns_of(i), i, 'item (%s)' % g, need, 'PAL pose layer' + (' + clean-room combat-arms' if owner == H2 else ''), owner, 'registry' if i in reg('item') else 'rewrite-jar'); itemrows += 1
heldonly = len(IT) - len(claimed)

# ---- class skills
for s in reg('spell'):
    add('class skill', ns_of(s), s, 'spell/skill', 'cast windup,release,hit effect', 'PAL + spell_engine pose', H2, 'registry')

# ---- fixed lists
def fixed(cat, owner, route, items, need):
    for thing in items: add(cat, 'diaithir', thing, 'action', need, route, owner, 'seed')
fixed('player', H1, 'PAL + clean-room vanilla body layer (first person shares the pose layer)', 'walk,run,sprint,sneak,sneak-walk,crawl,swim,swim-sprint,tread water,climb,ladder,vine,scaffold,glide (elytra),fall,land (soft/hard),jump,ride horse,ride boat,ride cart,ride mount,sit,sleep,stand up,use item,eat,drink,block,mine,place block,interact,open container,close container,fish,brew,craft,enchant,trade,sit at seat,get hurt,die,respawn,emote wheel,equip armor,swap hotbar,drop item,pick up item,throw,push/pull,carry,dive,wade,punch (empty hand),hold torch,hold map,hold spyglass,wave,point,nod,shake head,dance,cheer,bow,salute,pray,laugh,crouch interact'.split(','), 'third-person body + first-person arms')
fixed('gun', H2, 'clean-room, ties to #158', 'hold,aim,fire,reload,inspect,unjam,sprint lower,tank turret,tank driver,mounted gun,cannon,grenade throw'.split(','), 'viewmodel + third person')
fixed('boss', H3, 'own, GeckoLib + PAL', ['Ascendant boss attacks (35 bosses in diaithirbosses)', 'Ascendant rites (altar steps, boss wake)', 'Celtic rite casting (player)', 'Boss rush arena events'], 'cast poses + boss telegraphs')
fixed('vehicle', H4, 'Immersive Vehicles + PAL', ['Keelwright ship piloting', 'Foundry operator seat', 'seats (all seat types)', 'driver hands on wheel/stick', 'wheels', 'propellers/rotors', 'hatches/doors', 'landing gear', 'turret rotation', 'sails/rigging', 'rudder/helm', 'cranes/arms'], 'piloting poses + part motion')
fixed('machine', H4, 'GeckoLib', ['Foundry belts'], 'item flow, splitters, inserters')
fixed('npc', H3, 'GeckoLib + PAL', ['culture NPC archetypes (Panscriptum NPC lane)', 'shopkeeper', 'guard', 'quest giver', 'priest/ritual leader'], 'idle/work loops')
fixed('emote', H1, 'Emotecraft (GPL3, merge_port)', ['all Emotecraft emotes + custom pack'], 'player emote set')

# ---- write, keeping statuses already set in an earlier file
dest = OUT / 'ANIMATIONS_COVERAGE.csv'
old = {}
if dest.exists():
    try:
        for r in csv.DictReader(open(dest, encoding='utf-8')):
            if r.get('status') not in (None, '', 'todo'): old[(r['category'], r['thing'])] = r['status']
    except Exception: pass
for n, r in enumerate(rows, 1):
    r['id'] = 'AN%05d' % n
    r['status'] = old.get((r['category'], r['thing']), r['status'])
with open(dest, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, COLS); w.writeheader(); w.writerows(rows)
with open(OUT / 'ANIMATIONS_COVERAGE_STATIC.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['namespace', 'group', 'blocks', 'animations_needed', 'owner'])
    needs = {b[1]: b[2] for b in BLK}
    for (ns, g), c in sorted(grp.items(), key=lambda x: (-x[1], x[0])):
        w.writerow([ns, g, c, needs.get(g, 'none (static block; generic held/placed pose only)'), H4])
cnt = collections.Counter((r['owner'], r['category']) for r in rows)
print('rows', len(rows), '| item use rows', itemrows, '| held-only items', heldonly, '| anim assets', len(anim_assets), '| jar ids', {k: len(v) for k, v in jar_ids.items()})
for k, v in sorted(cnt.items()): print(*k, v)
