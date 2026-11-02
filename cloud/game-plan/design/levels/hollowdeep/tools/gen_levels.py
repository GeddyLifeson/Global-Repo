#!/usr/bin/env python3
"""Hollowdeep (REG_06) level design generator.

Reads the world thread's tables (design/world/) and data/ live, so rerun it
whenever those change:  python3 design/levels/hollowdeep/tools/gen_levels.py
Writes every table in design/levels/hollowdeep/ plus maps/*.svg and checks.csv.
Hand-authored content (Citadel zones, towns, field bosses, Relay, landmarks,
campaign places, Ostra lines) lives in this file; sites, vaults, POIs and
patrols are built from kit templates with a fixed seed per location.
"""
import csv, math, os, random, re, zlib, collections, glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
W = os.path.join(ROOT, 'design', 'world')
D = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'design', 'levels', 'hollowdeep')
REG = 'REG_06'


def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def wr(name, rows, cols):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)


def rng(key):
    return random.Random(zlib.crc32(key.encode()))


def dist(a, b):
    return math.hypot(float(a['x_m']) - float(b['x_m']), float(a['y_m']) - float(b['y_m']))


# ---------------------------------------------------------------- inputs
LOC = {r['loc_id']: r for r in rd(os.path.join(W, 'locations.csv'))}
R6 = {k: v for k, v in LOC.items() if v['region'] == REG}
SITES = {r['loc_id']: r for r in rd(os.path.join(W, 'sites.csv')) if r['region'] == REG}
ZONES = [r for r in rd(os.path.join(W, 'citadel_zones.csv')) if r['citadel'] == 'LOC_CIT_REG_06']
ENC = {r['enc_id']: r for r in rd(os.path.join(W, 'encounters.csv'))}
ENC_BY_LOC = collections.defaultdict(list)
for e in ENC.values():
    ENC_BY_LOC[e['loc_id']].append(e['enc_id'])
ARENAS = {r['boss']: r for r in rd(os.path.join(W, 'boss_arenas.csv')) if r['region'] == REG}
ANCH = {r['loc_id']: r for r in rd(os.path.join(W, 'anchors.csv')) if r['region'] == REG}
SECRETS = [r for r in rd(os.path.join(W, 'secrets.csv')) if r['region'] == REG]
LAYOUT = [r for r in rd(os.path.join(W, 'regions_layout.csv')) if r['reg_id'] == REG][0]
TEMPLATES = {r['template']: r for r in rd(os.path.join(W, 'encounter_templates.csv'))}
LORE = [r for r in rd(os.path.join(D, 'items', 'lore_items.csv')) if r['region'] == REG]
BOSSES = {r['ACT_ID']: r for r in rd(os.path.join(D, 'actors', 'bosses.csv'))}
CRT = [r for r in rd(os.path.join(D, 'actors', 'creatures.csv')) if REG in r['Regions']]
LGT = {r['time_of_day']: r['light_id'] for r in rd(os.path.join(ROOT, 'design', 'art', 'lighting_tod.csv')) if r['region'] == REG}

# every known ID, for validation
KNOWN = set()
for p in glob.glob(os.path.join(D, '**', '*.csv'), recursive=True):
    for r in rd(p):
        v = list(r.values())[0]
        if v and r.get('first_used_in') != 'assets/asset_hooks.csv':  # skip hooks only our own requests added
            KNOWN.add(v.strip())
for p in ['locations.csv', 'encounters.csv', 'secrets.csv']:
    KNOWN |= {list(r.values())[0] for r in rd(os.path.join(W, p))}
for p in glob.glob(os.path.join(ROOT, 'design', 'audio', '*.csv')) + glob.glob(os.path.join(ROOT, 'design', 'art', '*.csv')):
    for r in rd(p):
        v = list(r.values())[0]
        if v:
            KNOWN.add(v.strip())

# ---------------------------------------------------------------- shared vocab (design choices)
FAC_MIX = [('FAC_HOLLOWED', 50), ('FAC_CHOIRBORN', 40), ('FAC_REMNANT', 10)]  # regions_layout
FAC_NAME = {'FAC_HOLLOWED': 'HOLLOWED', 'FAC_CHOIRBORN': 'CHOIRBORN', 'FAC_REMNANT': 'REMNANT'}
VAR = {('FAC_HOLLOWED', 'FODDER'): 'ACT_VAR_R6_01', ('FAC_REMNANT', 'FODDER'): 'ACT_VAR_R6_02',
       ('FAC_CHOIRBORN', 'FODDER'): 'ACT_VAR_R6_03', ('FAC_HOLLOWED', 'SKIRMISHER'): 'ACT_VAR_R6_04',
       ('FAC_REMNANT', 'SKIRMISHER'): 'ACT_VAR_R6_05', ('FAC_CHOIRBORN', 'SKIRMISHER'): 'ACT_VAR_R6_06'}
CRT_PACK = [c['ACT_ID'] for c in CRT if c['Size'] in ('Small', 'Medium') and c['Hostility'] == 'Hostile']
CRT_SOLO = [c['ACT_ID'] for c in CRT if c['Size'] in ('Large', 'Huge')]

KIT_ROOMS = {
    'KIT_WRECK': ['Breach Hatch', 'Cargo Spine', 'Bulkhead Corridor', 'Crew Deck', 'Pump Room', 'Reactor Gallery',
                  'Observation Blister', 'Drop Shaft', 'Hull Gash', 'Engine Cradle', 'Galley', 'Med Alcove', 'Cold Locker'],
    'KIT_CATACOMB': ['Ossuary Stair', 'Bone Gallery', 'Niche Corridor', 'Lantern Crypt', 'Collapsed Nave', 'Charnel Pit',
                     'Reliquary', "Mourners' Hall", 'Root Tunnel', 'Sealed Tomb', 'Prayer Cell', 'Drift Ossuary'],
    'KIT_TOWER': ['Base Hall', 'Winding Stair', 'Gear Loft', 'Bell Chamber', 'Balcony Ring', 'Clock Face', 'Upper Gallery', 'Crown'],
    'KIT_LAB': ['Decon Airlock', 'Triage Ward', 'Records Office', 'Cold Storage', 'Specimen Hall', 'Server Crypt',
                'Surgical Theatre', 'Quarantine Block', 'Lift Lobby', 'Name Wall'],
    'KIT_CAVE': ['Cave Mouth', 'Drip Gallery', 'Glass-root Squeeze', 'Floating Stone Hall', 'Upfall Chamber', 'Pale Pool',
                 'Hollow Den', 'Echo Chamber'],
    'KIT_FORT': ['Gatehouse', 'Outer Yard', 'Barracks', 'Wall Walk', 'Keep Hall', 'Armory', 'Postern Stair', 'Signal Roof'],
    'KIT_CHOIR_VAULT': ['Glass Antechamber', 'Tone Pillar Hall', 'Listening Gallery', 'Choir Sanctum', 'Reliquary Niche', 'Glass Door Hall'],
}
KIT_LIGHT = {
    'KIT_WRECK': 'Emergency strips 6500 K cyan every 4 m, two in five dead or sparking; EV100 3-6; dust shafts through hull gashes; fog 0.15 grey-violet',
    'KIT_CATACOMB': 'Shard-lamp candles 2400 K amber in pools every 10 m, dark between (EV100 2-5); bone dust drifting upward through the beams',
    'KIT_TOWER': 'Window shafts from the region sun (time of day), brass clockwork bounce 3200 K; EV100 6-10; dust motes rise, never fall',
    'KIT_LAB': 'Dead ceiling panels, one in five flickering 5600 K; red 1800 K emergency in quarantine rooms; EV100 4-7',
    'KIT_CAVE': 'Shard veins give cyan bounce; floating stones silhouetted against upward falls; EV100 2-6; player lantern matters',
    'KIT_FORT': 'Exterior time-of-day light; Hollow-fire braziers (desaturated white flame, 7000 K) at gates and stairs',
    'KIT_CHOIR_VAULT': 'Choir glass refracts violet-white; tone pillars pulse light on each note; EV100 5-8; no shadows on the glass',
}
KIT_MOOD = {
    'KIT_WRECK': 'Claustrophobic, metallic, the ship still groaning as the ground under it lifts',
    'KIT_CATACOMB': 'Quiet grief; the dead are drifting out of their niches one bone at a time',
    'KIT_TOWER': 'Vertigo and order; machines still keeping time for no one',
    'KIT_LAB': 'Clinical dread; names and records of the Hollowing, the first patients',
    'KIT_CAVE': 'Upside-down wonder; water and stone falling up into the dark',
    'KIT_FORT': 'Last stand that already failed; barricades face inward',
    'KIT_CHOIR_VAULT': 'Sacred and wrong; the walls sing back when you speak',
}
KIT_ROOMTONE = {'KIT_WRECK': 'metal creak, pressure hiss', 'KIT_CATACOMB': 'stone hush, bone clicks', 'KIT_TOWER': 'clock tick 1 Hz, wind at height',
                'KIT_LAB': 'dead ballast hum, drip', 'KIT_CAVE': 'reverse drips, sub rumble', 'KIT_FORT': 'wind on walls, flag rope',
                'KIT_CHOIR_VAULT': 'held choir chord, glass ring'}

# hooks: existing ones are validated; new ones go to data-requests
SFX = {'anchor_light': 'Play_SFX_Player_Kindled_AnchorLight', 'anchor_rest': 'Play_SFX_Player_Kindled_AnchorRest',
       'area': 'Play_SFX_Ui_Interface_AreaDiscovered', 'anchor_found': 'Play_SFX_Ui_Interface_AnchorDiscovered',
       'chest': 'Play_SFX_World_Environment_ChestOpen', 'shortcut': 'Play_SFX_World_Environment_ShortcutUnlock',
       'lift': 'Play_SFX_World_Environment_LiftStartLoopStop', 'lever': 'Play_SFX_World_Environment_Lever',
       'illusory': 'Play_SFX_World_Environment_IllusoryWallVanish', 'lore': 'Play_SFX_World_Environment_LoreItemPickup',
       'relay': 'Play_SFX_World_Environment_RelayTowerActivate', 'door_metal': 'Play_SFX_World_Environment_DoorOpenCloseMetal',
       'door_wood': 'Play_SFX_World_Environment_DoorOpenCloseWood',
       # proposed
       'fog_enter': 'Play_SFX_World_Environment_FogGateEnter', 'locked': 'Play_SFX_World_Environment_LockedRattle',
       'key_use': 'Play_SFX_World_Environment_KeyUnlock', 'puzzle': 'Play_SFX_World_Environment_PuzzleSolved',
       'updrift': 'Play_SFX_World_Hollowdeep_UpdriftGust', 'lamp': 'Play_SFX_World_Hollowdeep_LampIgnite',
       'tone': 'Play_SFX_World_Hollowdeep_TonePillar', 'chain': 'Play_SFX_World_Hollowdeep_TetherStrain'}
VFX = {'updrift': 'VFX_LVL_HOL_UPDRIFT', 'lamp': 'VFX_LVL_HOL_SHARDLAMP', 'glassriver': 'VFX_LVL_HOL_GLASSRIVER',
       'upfall': 'VFX_LVL_HOL_UPFALL', 'drain': 'VFX_LVL_HOL_COLOURDRAIN', 'fog': 'VFX_LVL_FOGGATE', 'anchor': 'VFX_LVL_ANCHOR_LIGHT',
       'illusory': 'VFX_LVL_ILLUSORY_DISSOLVE', 'shortcut': 'VFX_LVL_SHORTCUT_DUST', 'tone': 'VFX_LVL_HOL_TONEPILLAR',
       'chute': 'VFX_LVL_HOL_LAMPCHUTE', 'relay': 'VFX_LVL_RELAY_BEAM', 'glint': 'VFX_LVL_LOOT_GLINT', 'tether': 'VFX_LVL_HOL_TETHER_SPARK',
       'skybeam': 'VFX_LVL_HOL_SHARD_SKYBEAM', 'heart': 'VFX_LVL_HOL_HEARTSHARD'}
MUS = {'explore': 'Music_Region=HOL; Music_Mode=Explore', 'site': 'Music_Mode=Dungeon (MUS_HOL_SITE)', 'citadel': 'Music_Mode=Dungeon (MUS_HOL_CITADEL)',
       'town': 'Music_Mode=Town (MUS_HOL_TOWN)', 'tension': 'Music_Mode=Tension (MUS_HOL_TENSION)', 'silence': 'Music_Mode=Silence (2 s fade)'}

ROWS = collections.defaultdict(list)   # table -> rows
STRINGS = []                           # new strings
REQ = []                               # data requests
CONFLICTS = []
NEW_IDS = set()                        # IDs this folder proposes


def S(sid, text, ctx):
    STRINGS.append({'str_id': sid, 'text': text, 'max_chars': math.ceil(len(text) * 1.4), 'context': ctx})
    NEW_IDS.add(sid)
    return sid


def level_row(loc_id, kind, name, **kw):
    r = {'loc_id': loc_id, 'kind': kind, 'name': name}
    r.update(kw)
    ROWS['levels'].append(r)
    return r


NODE_SEQ = collections.Counter()


def node(loc_id, name, func, crit='Y', floor=0, elev=0, size='20x20x6', space='MID', cover='', trv='TRV_WALK', light='', mood='', notes=''):
    NODE_SEQ[loc_id] += 1
    nid = 'LVN_%s_%02d' % (loc_id.replace('LOC_', ''), NODE_SEQ[loc_id])
    lo, hi = (cover.split('/') + [''])[:2] if cover else ('', '')
    ROWS['nodes'].append({'node_id': nid, 'loc_id': loc_id, 'seq': NODE_SEQ[loc_id], 'name': name, 'function': func, 'critical': crit,
                          'floor': floor, 'elev_rel_m': elev, 'size_m': size, 'space': space, 'cover_low': lo, 'cover_high': hi,
                          'traversal': trv, 'lighting': light, 'mood': mood, 'notes': notes})
    return nid


def edge(loc_id, a, b, etype='Path', two_way='Yes', opens_from='', req='', length=15, notes=''):
    if etype == 'Shortcut' and any(e['type'] == 'Shortcut' and {e['from_node'], e['to_node']} == {a, b} for e in ROWS['edges']):
        return
    eid = 'LVE_%s_%02d' % (loc_id.replace('LOC_', ''), sum(1 for e in ROWS['edges'] if e['loc_id'] == loc_id) + 1)
    ROWS['edges'].append({'edge_id': eid, 'loc_id': loc_id, 'from_node': a, 'to_node': b, 'type': etype, 'two_way': two_way,
                          'opens_from': opens_from, 'requirement': req, 'length_m': length, 'notes': notes})


def chain(loc_id, nodes, etype='Path', length=15):
    for a, b in zip(nodes, nodes[1:]):
        edge(loc_id, a, b, etype, length=length)


ENC_N = [0]


def actors_for(template, fac, r):
    if template in ('ENT_CRT_PACK',):
        c = r.choice(CRT_PACK)
        return '%s x%d' % (c, r.choice([3, 4]))
    if template == 'ENT_CRT_SOLO':
        return '%s x1' % r.choice(CRT_SOLO)
    out = []
    for part in TEMPLATES[template]['roles'].split(';'):
        role, n = part.strip().split(' x')
        n = int(n)
        base = 'ACT_%s_%s' % (FAC_NAME[fac], role)
        v = VAR.get((fac, role))
        if v and n > 1:
            out += ['%s x%d' % (v, n // 2), '%s x%d' % (base, n - n // 2)]
        elif v and r.random() < 0.5:
            out.append('%s x%d' % (v, n))
        else:
            out.append('%s x%d' % (base, n))
    return '; '.join(out)


def pick_fac(r):
    x = r.randint(1, 100)
    acc = 0
    for f, w in FAC_MIX:
        acc += w
        if x <= acc:
            return f
    return FAC_MIX[0][0]


TRIGGER = {'ENT_PATROL': 'Patrol loop, aggro on sight 35 m', 'ENT_CAMP': 'Idle at camp; aggro on sight 30 m or noise',
           'ENT_AMBUSH': 'Hidden; 12 m trigger volume, drop from above or out of niches', 'ENT_FORT': 'Holds the line; aggro at 50 m',
           'ENT_ELITE': 'Heavy idles facing the entry; escorts wake on aggro', 'ENT_HORDE': 'Asleep in a heap; wakes on noise or 15 m',
           'ENT_GUNLINE': 'Fires from cover at 60 m; flanker pair moves at 20 m', 'ENT_KEEPER': 'Named elite waits at the far wall; door seals on entry',
           'ENT_CRT_PACK': 'Roams 40 m radius; flees below 25% pack size', 'ENT_CRT_SOLO': 'Territorial; warns at 40 m, charges at 25 m'}


def place_enc(loc_id, nid, enc_id=None, template=None, level=None, note='', r=None):
    """Place a world encounter (enc_id) or create a level one (LENC)."""
    if enc_id:
        e = ENC[enc_id]
        template, fac, lvl, actors, cov, fb, resp = e['template'], e['faction'], e['level'], e['actors'], e['cover_points'], e['fallback_points'], e['respawn']
        src = enc_id
    else:
        ENC_N[0] += 1
        src = 'LENC_06_%04d' % ENC_N[0]
        NEW_IDS.add(src)
        fac = pick_fac(r) if not template.startswith('ENT_CRT') else 'Creature'
        actors = actors_for(template, fac, r)
        t = TEMPLATES[template]
        lvl, cov, fb, resp = level, t['cover_points'], t['fallback_points'], t['respawn']
    n = sum(int(p.split(' x')[1]) for p in actors.split(';') if ' x' in p)
    ROWS['enc'].append({'place_id': 'LEP_%s_%02d' % (loc_id.replace('LOC_', ''), sum(1 for x in ROWS['enc'] if x['loc_id'] == loc_id) + 1),
                        'loc_id': loc_id, 'node_id': nid, 'enc_id': src, 'source': 'world' if enc_id else 'levels (new)', 'template': template,
                        'faction': fac, 'level': lvl, 'actors': actors, 'actor_count': n, 'trigger': TRIGGER.get(template, 'On sight 30 m'),
                        'cover_points': cov, 'fallback_points': fb, 'respawn': resp, 'notes': note})
    return src


def loot(loc_id, nid, container, item, qty='1', vis='Critical path', src='', notes=''):
    ROWS['loot'].append({'lot_id': 'LLT_%s_%02d' % (loc_id.replace('LOC_', ''), sum(1 for x in ROWS['loot'] if x['loc_id'] == loc_id) + 1),
                         'loc_id': loc_id, 'node_id': nid, 'container': container, 'item_or_table': item, 'qty': qty,
                         'visibility': vis, 'world_loc': src, 'notes': notes})


def cue(loc_id, nid, trigger, audio='', music='', amb='', vfx='', light='', popup='', vo=''):
    ROWS['cues'].append({'cue_id': 'LCU_%s_%02d' % (loc_id.replace('LOC_', ''), sum(1 for x in ROWS['cues'] if x['loc_id'] == loc_id) + 1),
                         'loc_id': loc_id, 'node_id': nid, 'trigger': trigger, 'audio_events': audio, 'music_state': music,
                         'ambience': amb, 'vfx': vfx, 'lighting': light, 'popup': popup, 'vo_string': vo})


def checkpoint(loc_id, anchor, nid, kind, boss_run='', shortcut='', notes=''):
    ROWS['checkpoints'].append({'loc_id': loc_id, 'anchor_id': anchor, 'node_id': nid, 'kind': kind, 'boss_run_m': boss_run,
                                'shortened_by': shortcut, 'notes': notes})


def name_str(loc_id, text):
    return S('STR_%s_NAME' % loc_id, text, 'Area name banner and map label')


def discover(loc_id, nid, name, ostra=None, music='explore', amb='AMB_HOL_BED_DAY', vfx=''):
    sid = name_str(loc_id, name)
    vo = S('STR_VO_OSTRA_%s' % loc_id.replace('LOC_', ''), ostra, 'Ostra line on first entry (VO)') if ostra else ''
    cue(loc_id, nid, 'Discover (first entry)', SFX['area'] + '; Play_MUS_HOL_DISCOVERY', MUS[music], amb, vfx, LGT.get('Day', ''),
        'NTF_DISCOVER (%s)' % sid, vo)


def anchor_cues(loc_id, nid, anchor):
    cue(loc_id, nid, 'Anchor lit (%s)' % anchor, SFX['anchor_found'] + '; ' + SFX['anchor_light'], '', 'AMB_HOL_WEAVE_HUM', VFX['anchor'],
        'Anchor point light 3200 K, 6 m radius, flickers up with Updrift', 'BAN_ANCHOR')


def shortcut_cue(loc_id, nid, form):
    k = 'lift' if 'Lift' in form or 'Elevator' in form else ('lever' if 'winch' in form.lower() or 'Bridge' in form else 'shortcut')
    cue(loc_id, nid, 'Shortcut opened: %s' % form, SFX[k] + '; ' + SFX['shortcut'], '', '', VFX['shortcut'], '', 'NTF_DISCOVER (shortcut)')


def nearest_anchor(p):
    best = min(ANCH.values(), key=lambda a: dist(a, p))
    return best['loc_id'], round(dist(best, p))


# ---------------------------------------------------------------- hand-written Ostra lines (first entry)
OSTRA = {
    'LOC_CIT_REG_06': "That city is floating. Not tethered, not built up there. It fell upward, and somebody chained it back.",
    'LOC_TOWN_REG_06_01': "Lamps on every post. Someone here worked out that the Hollowing hates steady light.",
    'LOC_TOWN_REG_06_02': "They chained the houses to the ground. Hold on to something before you sleep here.",
    'LOC_RELAY_REG_06': "Half the tower is grey. Climb carefully. Some of these rungs aren't really here anymore.",
    'LOC_CHOIR_REG_06': "There's a voice under the floor. It's mine. Older. I don't remember recording it.",
    'LOC_FB_BONEHARVESTER': "Something has been stacking the dead in rows. Neat rows. Please don't be here after dark.",
    'LOC_FB_SENTINELS': "Two guards and one lift. Whatever they protect, they've been doing it for nine hundred years.",
    'LOC_DGN_REG_06_01': "Bulkhead seven. I know this section. It used to be on the ground.",
    'LOC_DGN_REG_06_02': "Everyone down here is asleep. Keep it that way if you can.",
    'LOC_DGN_REG_06_03': "Hear that? Every tick lands exactly one second apart. Fight to the clock.",
    'LOC_DGN_REG_06_04': "The first Hollowed were brought here for treatment. The charts stop in the middle of a word.",
    'LOC_DGN_REG_06_05': "The water's falling up. If you drop something in here, it's gone.",
    'LOC_DGN_REG_06_06': "The barricades face inward. They weren't keeping anything out.",
    'LOC_DGN_REG_06_07': "Cryo deck. Some pods are still sealed. Don't look at the names.",
    'LOC_DGN_REG_06_08': "Ghost lights in the crypt. They follow footsteps that aren't yours.",
    'LOC_DGN_REG_06_09': "A watchtower with nothing left to watch. The land it guarded is gone.",
    'LOC_DGN_REG_06_10': "Vault Nine. A list of every sleeper who died in the Fall. Thirty-seven thousand names.",
    'LOC_DGN_REG_06_11': "Pale stone, pale water. Even the echoes come back quieter.",
    'LOC_DGN_REG_06_12': "A redoubt on a shelf of floating rock. The road it held just drifted away.",
    'LOC_DGN_REG_06_13': "A hull section rising slowly. Every day it's a little higher.",
    'LOC_DGN_REG_06_14': "Bone spire. They built it from what the Hollowing left behind.",
    'LOC_DGN_REG_06_15': "This crypt was sealed from the inside. Whoever did it stayed.",
    'LOC_VAULT_REG_06_01': "Choir glass. Speak softly. It remembers every word.",
    'LOC_VAULT_REG_06_02': "Bones and glass. The Choir buried their singers standing up.",
    'LOC_VAULT_REG_06_03': "This vault hums in a key that hurts. I think it's tuned to the Quiet.",
    'LOC_LMK_REG_06_01': "From here the whole city hangs in the air like a held breath.",
    'LOC_LMK_REG_06_02': "Upward falls. The river leaves the ground and never comes back.",
    'LOC_LMK_REG_06_03': "Fields of bone, all laid out. That's harvest work, not war.",
    'LOC_LMK_REG_06_04': "The Sentinel Pair. Don't stare. They notice.",
    'LOC_LMK_REG_06_05': "An orbit tether from the Meridian. It used to reach the sky. It nearly still does.",
    'LOC_LMK_REG_06_06': "Clockhouse Tower. It keeps time for the Prior, and the Prior keeps time for nothing.",
    'LOC_LMK_REG_06_07': "The Pale Hole. The land didn't sink. It was taken.",
    'LOC_CQ_REG_06_LAMP_TOWER': "A lamp tower nobody lights. Shard light going up, not out. She's here.",
    'LOC_CQ_REG_06_GLASS_RIVER': "The river turned to glass mid-flow. Don't skate on it. It's thinner than it looks.",
    'LOC_CON_08': "Hollowdeep. Colour drains past this bridge. Watch your Ward. Watch your footing.",
    'LOC_CON_09': "One-way drop. We're not getting back up this way until we light the lift from below.",
}
ZONE_OSTRA = {
    'Tether Docks': "Tether docks. Every cable here holds a street down. Cut one and a district leaves.",
    'Floating Bazaar': "A market that floats. The stalls are still open. Nobody's selling.",
    'Hanging Streets': "Narrow streets hanging upside down from the rock. Keep your blade short.",
    'Lamp Spires': "Lamp spires. Every crown burns upward. She was feeding them before she ran.",
    "Lamplighter's Way": "The Lamp Works. Whatever she's feeding the sky comes from here.",
    'Underside Gardens': "Gardens on the underside. They grow downward, toward the ground they miss.",
    'Ascendant Palace': "The palace of the Twins. Every mirror shows two of you.",
    'The Twin Throne': "The Twin Throne. Two Shard-bearers, one Heart. Be ready.",
}

# ---------------------------------------------------------------- 1. Citadel (hand-authored)
CIT = 'LOC_CIT_REG_06'
cit = R6[CIT]
ZSPEC = {  # zone order -> list of (name, function, crit, size, space, cover, traversal, notes)
    'Tether Docks': [('Tether Landing', 'Entrance', 'Y', '30x24x0', 'MID', '3/2', 'TRV_WALK', 'Arrive by cable car from the Grey Wayshrine side; Anchor here'),
        ('Cable-car Platform', 'Combat', 'Y', '40x18x0', 'LONG', '4/3', 'TRV_WALK', 'Gun line across a 60 m gap; second car is a moving platform'),
        ('Mooring Yard', 'Combat', 'Y', '45x35x0', 'MID', '6/3', 'TRV_WALK', 'Camp among cargo chained to bollards; tethers strain overhead'),
        ('Snapped Tether Walk', 'Combat', 'Y', '4x60x0', 'CQ', '0/2', 'TRV_WALK TRV_JUMP', 'Melee 4 m wide catwalk along a broken cable; ambush from below'),
        ('Crane Loft', 'Side', 'N', '12x12x8', 'CQ', '1/1', 'TRV_LADDER', 'Ladder up; small chest and a view of the whole route'),
        ('Dock Gate Winch', 'Hub', 'Y', '16x16x6', 'MID', '2/2', 'TRV_WALK', 'Winch lifts the Bazaar gate')],
    'Floating Bazaar': [('Bazaar Gate', 'Hub', 'Y', '14x10x8', 'CQ', '1/2', 'TRV_WALK', 'Barbican winch here later reopens the way to the Z1 Anchor'),
        ('Drifting Stalls', 'Combat', 'Y', '50x50x0', 'MID', '6/4', 'TRV_WALK TRV_JUMP', 'Stall islands joined by plank bridges; horde on the central island'),
        ('Lantern Market Square', 'Combat', 'Y', '40x40x0', 'MID', '5/3', 'TRV_WALK', 'Choirborn camp in the square; leader on the fountain rim'),
        ("Moneychanger's Vault", 'Side', 'N', '10x12x4', 'NONE', '', 'TRV_WALK', 'Behind the locked door; vault chest'),
        ('Upturned Fountain', 'Traversal', 'Y', '12x12x30', 'NONE', '', 'TRV_LIFTCURRENT', 'Water falls upward; ride the lift current to Z3'),
        ('Rope Bridge', 'Combat', 'Y', '3x45x0', 'CQ', '0/0', 'TRV_WALK', 'Swaying bridge; artillery shells from Z3 balconies')],
    'Hanging Streets': [('Underside Lane', 'Anchor', 'Y', '6x30x5', 'CQ', '0/3', 'TRV_WALK', 'Streets hang from the rock; Anchor at the lamp post'),
        ('Laundry Alleys', 'Combat', 'Y', '4x50x5', 'CQ', '0/4', 'TRV_WALK', 'Melee-only width; Glasscrawlers drop from the lines'),
        ('Bell Lane Stair', 'Combat', 'Y', '6x40x14', 'CQ', '0/3', 'TRV_WALK', 'Brute and escort hold the stair'),
        ('Lamp Crew Den', 'Side', 'N', '10x10x4', 'NONE', '', 'TRV_WALK', "Children's lamp crew hideout; drawings of the Lamplighter (lore)"),
        ('Collapsed Terrace', 'Shortcut', 'N', '15x20x8', 'MID', '2/2', 'TRV_FALL', 'Kick-down ladder back to the Bazaar'),
        ('Spire Foot', 'Combat', 'Y', '30x30x0', 'MID', '4/3', 'TRV_WALK', 'Horde in the base of the spires')],
    'Lamp Spires': [('Spire Base', 'Hub', 'Y', '20x20x10', 'MID', '2/2', 'TRV_WALK', 'Lamp lifts start here'),
        ('Cable Lift', 'Traversal', 'Y', '4x4x40', 'NONE', '', 'TRV_LADDER', 'Exposed cage lift; Hornet Drones harass during the ride'),
        ('Lamp Gallery', 'Combat', 'Y', '70x12x0', 'LONG', '6/4', 'TRV_WALK', 'Long gallery between spires; snipers on the far spire (one long space per route)'),
        ('Wick Store', 'Side', 'N', '10x10x4', 'NONE', '', 'TRV_WALK', 'Locked door; oil, wicks and a Shard Lance'),
        ('Spire Crown Walk', 'Combat', 'Y', '5x50x0', 'CQ', '1/2', 'TRV_JUMP TRV_STRIDER', 'Glide or jump gaps between crowns; ambush'),
        ('Spire Back Door', 'Shortcut', 'N', '4x6x3', 'NONE', '', 'TRV_WALK', 'One-way door down to the Z3 Anchor'),
        ('Works Gate', 'Hub', 'Y', '12x8x8', 'NONE', '', 'TRV_WALK', 'The Lamp Works doors')],
    "Lamplighter's Way": [('Works Antechamber', 'Anchor', 'Y', '16x16x8', 'NONE', '', 'TRV_WALK', 'Anchor; Echo sign spot for summons'),
        ('Fog Gate', 'Gate', 'Y', '4x2x5', 'NONE', '', 'TRV_WALK', 'Fog gate 4 m wide'),
        ('Lamp Works Floor', 'Boss', 'Y', '53x53x20', 'ARENA', '4/0', 'TRV_WALK', 'Stepped platform arena, 4 cover pieces; lamps rise as she loses HP'),
        ('Lamp Chute', 'Story', 'Y', '6x6x80', 'NONE', '', 'TRV_LADDER', 'She escapes up the chute at 30% HP; afterwards a broken ladder leads to her ledgers'),
        ('Works Lift', 'Shortcut', 'N', '5x5x30', 'NONE', '', 'TRV_LADDER', 'Lift from the antechamber down to Z3')],
    'Underside Gardens': [('Garden Gate', 'Anchor', 'Y', '12x10x6', 'MID', '1/2', 'TRV_WALK', 'Anchor at the gate arch'),
        ('Hanging Orchards', 'Combat', 'Y', '40x40x12', 'MID', '3/5', 'TRV_WALK TRV_JUMP', 'Trees grow downward; fight on root platforms'),
        ('Root Bridges', 'Combat', 'Y', '4x60x0', 'CQ', '0/1', 'TRV_WALK', 'Choir Wisps swarm the bridges'),
        ('Glasshouse', 'Side', 'N', '16x12x8', 'NONE', '', 'TRV_WALK', 'Locked; a Choir glass garden, Tonic Distillation'),
        ('Plank Drop', 'Shortcut', 'N', '4x10x12', 'NONE', '', 'TRV_FALL', 'Drop-down plank back to the Z5 Anchor'),
        ('Palace Underlift', 'Combat', 'Y', '20x20x30', 'MID', '2/2', 'TRV_LADDER', 'Lift up into the palace; elite at the top')],
    'Ascendant Palace': [('Palace Steps', 'Combat', 'Y', '30x40x12', 'LONG', '5/3', 'TRV_WALK', 'Wide steps; gun line from the portico'),
        ('Hall of Petitions', 'Combat', 'Y', '35x50x14', 'MID', '6/4', 'TRV_WALK', 'Fortified line of pews and petition desks'),
        ('Mirror Gallery', 'Combat', 'Y', '8x60x8', 'CQ', '0/4', 'TRV_WALK', 'Blinkblades teleport between mirrors; mirrors show the real one'),
        ('Palace Armory', 'Side', 'N', '12x12x5', 'NONE', '', 'TRV_WALK', 'Locked; armory rack'),
        ('Bridge Winch', 'Shortcut', 'N', '10x10x6', 'NONE', '', 'TRV_WALK', 'Lowers the long bridge back to the Lamp Spires (big loop)'),
        ('Throne Approach', 'Combat', 'Y', '20x40x10', 'MID', '3/3', 'TRV_WALK', 'Choirborn honour guard')],
    'The Twin Throne': [('Throne Antechamber', 'Anchor', 'Y', '14x14x8', 'NONE', '', 'TRV_WALK', 'Anchor; last rest'),
        ('Fog Gate', 'Gate', 'Y', '4x2x5', 'NONE', '', 'TRV_WALK', 'Fog gate 4 m wide'),
        ('Twin Throne Nave', 'Boss', 'Y', '70x30x25', 'ARENA', '5/0', 'TRV_WALK', 'Long nave arena; two thrones at the far end; Strider not allowed'),
        ('Heart Shard Dais', 'Story', 'Y', '10x10x4', 'NONE', '', 'TRV_WALK', 'Heart Shard choice (take or spare); Lucid line'),
        ('Seat Elevator', 'Shortcut', 'N', '5x5x110', 'NONE', '', 'TRV_LADDER', 'Elevator from the seat down to the Tether Landing (exit)')],
}
ZLIGHT = {
    'Tether Docks': 'Exterior TOD; tether cables carry blue-white spark runs every 8 s; city underside lit by Shard lamps',
    'Floating Bazaar': 'Hanging lanterns 2700 K over stalls, swaying with updrift; grey sky behind; dust rises through light',
    'Hanging Streets': 'Lamp posts every 12 m upside down; deep shade between (EV100 4); laundry casts moving shadows',
    'Lamp Spires': 'Lamp crowns 2200 K burn upward in tall columns; vertical god rays; long sightlines lit for snipers',
    "Lamplighter's Way": 'Works furnaces white-hot 6500 K; Shard beam to the sky through the roof; lamps rise during the fight',
    'Underside Gardens': 'Bioluminescent roots, pale cyan; ground visible far below through gaps; EV100 3-5',
    'Ascendant Palace': 'Cold palace light through tall glass, 7000 K; mirrors double every light source',
    'The Twin Throne': 'Single sky shaft onto the dais; two thrones backlit; arena darkens per phase',
}
ZMOOD = {'Tether Docks': 'Wind, cables, a city overhead', 'Floating Bazaar': 'Ghost market, wares still on the tables', 'Hanging Streets': 'Tight, dark, upside-down homes',
         'Lamp Spires': 'Climb into light; vertigo', "Lamplighter's Way": 'Industrial sacrifice; heat and noise', 'Underside Gardens': 'Eerie beauty, quiet, falling-up petals',
         'Ascendant Palace': 'Cold ceremony; reflections; dread', 'The Twin Throne': 'Grief; two rulers who heard the hail'}
door_key = {}
for li in LORE:
    if li['lore_type'] == 'Key' and li['unlocks']:
        door_key[li['unlocks']] = li['item_id']
z_nodes = {}
ZID = {z['name']: z['loc_id'] for z in ZONES}
ORD = {int(z['order']): z['name'] for z in ZONES}
pending_sc = []
GENERIC_ZONE = [('Zone Entry', 'Hub', 'Y', '20x20x6', 'MID', '2/2', 'TRV_WALK', ''), ('Main Street', 'Combat', 'Y', '30x30x0', 'MID', '4/3', 'TRV_WALK', ''), ('Side Court', 'Side', 'N', '12x12x4', 'NONE', '', 'TRV_WALK', ''), ('Inner Gate', 'Combat', 'Y', '20x30x0', 'MID', '3/3', 'TRV_WALK', ''), ('Back Way', 'Shortcut', 'N', '4x10x4', 'NONE', '', 'TRV_WALK', '')]
lvl = level_row(CIT, 'Citadel', LOC[CIT]['name'], story_name='', parent='', level=cit['level'],
                x_m=cit['x_m'], y_m=cit['y_m'], biome=cit['biome'], layout='Node graph across 8 vertical zones; side view in maps/citadel_flow.svg',
                rooms=sum(len(v) for v in ZSPEC.values()), first_play_min=sum(int(z['path_min']) for z in ZONES),
                completion_min=round(sum(int(z['path_min']) for z in ZONES) * 1.45), entry=ZONES[0]['anchor'],
                music='MUS_HOL_CITADEL', ambience='AMB_HOL_CITADEL; AMB_HOL_WIND; AMB_HOL_HOLLOWING',
                lighting=LGT.get('Day', '') + ' outside; per zone inside', mood='A city that fell upward, held by chains; the Lamplighter feeds it to the sky',
                vfx='%s; %s; %s' % (VFX['updrift'], VFX['tether'], VFX['skybeam']),
                quests='MQ_A2_05C The Lamp Works; MQ_A2_05 The Twin Thrones; MQ_A2_08 trail starts at the Lamp Chute',
                notes='Plan 5.2: side-view flow with every shortcut marked; first play %s min (plan 2-3 h)' % sum(int(z['path_min']) for z in ZONES))
discover(CIT, '', LOC[CIT]['name'], OSTRA[CIT], 'citadel', 'AMB_HOL_CITADEL', VFX['updrift'])
prev_last = None
for z in ZONES:
    zid, o = z['loc_id'], int(z['order'])
    zl = LOC[zid]
    r = rng(zid)
    level_row(zid, 'Citadel zone', z['name'], story_name='', parent=CIT, level=z['level'], x_m=zl['x_m'], y_m=zl['y_m'], biome=zl['biome'],
              layout='Zone %d of 8, %s; elevation +%s m' % (o, z['style'], z['elevation_rel_m']), rooms=len(ZSPEC.get(z['name'], GENERIC_ZONE)),
              first_play_min=z['path_min'], completion_min=round(int(z['path_min']) * 1.4), entry=z['anchor'] or '',
              music='MUS_HOL_CITADEL' if not z['boss'] else 'MUS_BOSS_%s_*' % z['boss'].replace('ACT_BOSS_', ''),
              ambience='AMB_HOL_CITADEL; ' + ('AMB_HOL_WIND' if o in (1, 4, 7) else 'AMB_HOL_INTERIOR'),
              lighting=ZLIGHT.get(z['name'], 'Exterior time of day'), mood=ZMOOD.get(z['name'], ''), vfx=VFX['updrift'], quests='', notes='Shortcut: ' + z['shortcut'])
    ids = []
    for i, (nm, fn, crit, size, space, cov, trv, note) in enumerate(ZSPEC.get(z['name'], GENERIC_ZONE)):
        floor = 0
        nid = node(zid, nm, fn, crit, floor, int(z['elevation_rel_m']) + i * 2, size, space, cov, trv, ZLIGHT.get(z['name'], 'Exterior time of day'), ZMOOD.get(z['name'], ''), note)
        ids.append((nid, fn, nm))
    z_nodes[z['name']] = ids
    crit_ids = [n for n, fn, _ in ids if fn not in ('Side', 'Shortcut')]
    chain(zid, crit_ids)
    for n, fn, nm in ids:
        if fn == 'Side':
            dk = [d for d in R6 if R6[d]['kind'] == 'Locked door' and R6[d]['parent_loc'] == zid]
            if dk:
                k = door_key.get(dk[0], '')
                wk = R6[dk[0]]['gate'].replace('Key ', '')
                if k and wk != k:
                    CONFLICTS.append({'what': 'Key for ' + dk[0], 'a': 'world locations.csv gate: ' + wk, 'b': 'items lore_items.csv unlocks: ' + k,
                                      'choice': 'Levels use the key whose own row says it unlocks the door (%s)' % k})
                edge(zid, crit_ids[min(2, len(crit_ids) - 1)], n, 'Locked door', 'Yes', 'Either side', '%s (key %s)' % (dk[0], k or wk), 8)
                cue(zid, n, 'Locked door tried / opened', SFX['locked'] + '; ' + SFX['key_use'] + '; ' + SFX['door_metal'], popup='INL_LOCKED_KEY')
            else:
                edge(zid, crit_ids[min(1, len(crit_ids) - 1)], n, 'Ladder' if 'Loft' in nm else 'Path', length=12)
        if fn == 'Shortcut':
            src_c = crit_ids[0] if 'Antechamber' in crit_ids[0] or nm == 'Works Lift' else crit_ids[-1]
            edge(zid, src_c, n, 'Path', length=10, notes='Leads to the shortcut')
    # encounters: world first, then fill combat nodes
    combat = [n for n, fn, _ in ids if fn == 'Combat']
    wenc = z['encounters'].split() if z['encounters'] else []
    for i, n in enumerate(combat):
        if i < len(wenc) and wenc[i] in ENC:
            place_enc(zid, n, wenc[i])
        else:
            tpl = {'Melee close quarters': 'ENT_AMBUSH', 'Vertical climb': 'ENT_GUNLINE'}.get(z['style'], r.choice(['ENT_CAMP', 'ENT_FORT', 'ENT_ELITE', 'ENT_HORDE', 'ENT_AMBUSH']))
            nm = [x for x in ids if x[0] == n][0][2]
            if 'Gallery' in nm or 'Steps' in nm or 'Platform' in nm:
                tpl = 'ENT_GUNLINE'
            if 'Root Bridges' in nm:
                tpl = 'ENT_CRT_PACK'
            place_enc(zid, n, template=tpl, level=z['level'], r=r, note='Fills a combat node the world table left empty')
    for extra in wenc[len(combat):]:
        if extra in ENC:
            place_enc(zid, combat[-1] if combat else ids[0][0], extra, note='Second group in the same space; wakes when the first is half dead')
    # anchors, boss, cues
    if z['anchor']:
        an = [n for n, fn, _ in ids if fn in ('Entrance', 'Anchor')]
        anchor_nid = an[0] if an else ids[0][0]
        boss_run = ''
        if z['boss'] and z['boss'] in ARENAS:
            boss_run = ARENAS[z['boss']]['anchor_run_m']
        checkpoint(zid, z['anchor'], anchor_nid, 'Citadel' + (' pre-boss' if z['boss'] else ''), boss_run,
                   '', 'Rest respawns zone enemies except elites (plan 3.4)')
        anchor_cues(zid, anchor_nid, z['anchor'])
    zone_disc = S('STR_VO_OSTRA_CIT_REG_06_Z%d' % o, ZONE_OSTRA.get(z['name'], ''), 'Ostra line on entering the zone (VO)')
    name_str(zid, z['name'])
    cue(zid, ids[0][0], 'Enter zone', SFX['area'], MUS['citadel'], 'AMB_HOL_CITADEL', VFX['updrift'], ZLIGHT.get(z['name'], 'Exterior time of day'), 'NTF_DISCOVER (STR_%s_NAME)' % zid, zone_disc)
    if prev_last:
        edge(CIT, prev_last, ids[0][0], 'Path', length=25, notes='Zone %d to %d' % (o - 1, o))
    prev_last = [n for n, fn, _ in ids if fn not in ('Side', 'Shortcut')][-1]
    if z['boss']:
        b = z['boss']
        a = ARENAS.get(b, {})
        bn = [n for n, fn, _ in ids if fn == 'Boss'][0]
        gate = [n for n, fn, _ in ids if fn == 'Gate'][0]
        cue(zid, gate, 'Fog gate crossed', SFX['fog_enter'], 'Music_Boss=%s (Play_MUS_BOSS_%s_INTRO)' % (b[9:], b[9:]), '', VFX['fog'], '', 'PRM_FOG / PRM_FOG_COOP')
        for ph in range(1, int(BOSSES[b]['Phases']) + 1):
            cue(zid, bn, 'Boss phase %d' % ph, '', 'Boss_Phase=%d (MUS_BOSS_%s_P%d)' % (ph, b[9:], ph), '', 'ARENA_%s_P%d' % (b[9:], ph),
                ZLIGHT.get(z['name'], 'Exterior time of day'), 'BAN_PHASE' if ph > 1 else '')
        cue(zid, bn, 'Boss defeated', '', MUS['silence'], 'AMB_HOL_CITADEL', VFX['anchor'], '', 'BAN_BOSS_DEAD')
        ROWS['enc'].append({'place_id': 'LEP_%s_B' % zid.replace('LOC_', ''), 'loc_id': zid, 'node_id': bn, 'enc_id': b, 'source': 'actors/bosses.csv',
                            'template': 'Boss', 'faction': '', 'level': BOSSES[b]['Level'], 'actors': b + ' x1', 'actor_count': 1,
                            'trigger': 'Fog gate', 'cover_points': a.get('cover_pieces', ''), 'fallback_points': '', 'respawn': 'Never',
                            'notes': '%s, %s m; %s' % (a.get('shape', ''), a.get('diameter_m', ''), a.get('hazards', ''))})
        for part in BOSSES[b]['Drops (item refs)'].split(';'):
            loot(zid, bn, 'Boss drop', part.strip().split(' ')[0], (part.strip().split(' x')[1] if ' x' in part else '1'), 'Boss')
        if BOSSES[b].get('Resonance unlocked'):
            loot(zid, bn, 'Boss drop', BOSSES[b]['Resonance unlocked'], '1', 'Boss', notes='Resonance granted on first kill')
    sc = [n for n, fn, _ in ids if fn == 'Shortcut']
    pending_sc.append((z, sc[0] if sc else ids[0][0]))
    # zone loot: pickups and side rewards
    for n, fn, nm in ids:
        if fn == 'Combat':
            loot(zid, n, 'Corpse pickup', 'ITM_LT_TIERMAT_REG_06', '1', 'Critical path', notes='On a Hollowed corpse at the room edge')
        if fn == 'Side':
            loot(zid, n, 'Small chest', 'ITM_LT_SMALLCHEST_REG_06', '1', 'Side room')
    if z['name'] == "Lamplighter's Way":
        loot(zid, z_nodes["Lamplighter's Way"][3][0], 'Lore pickup', 'ITM_LOR_LEDGER_LAMPLIGHTER', '1', 'Critical path', notes="Lamplighter's ledger; starts MQ_A2_08")
        NEW_IDS.add('ITM_LOR_LEDGER_LAMPLIGHTER')
        cue(zid, z_nodes["Lamplighter's Way"][3][0], 'Lamplighter flees at 30% HP', 'Play_SFX_Bosses_Lamplighter_Escape', MUS['tension'], '', VFX['chute'], '', '',
            S('STR_VO_OSTRA_LAMPLIGHTER_FLEE', "Her mask. That insignia is a Meridian captain's. Ires?", 'Ostra, after the Lamplighter flees'))
    if z['name'] == 'The Twin Throne':
        cue(zid, z_nodes['The Twin Throne'][3][0], 'Heart Shard choice', '', MUS['silence'], '', VFX['heart'], 'Sky shaft narrows to the dais', 'CNF (Heart Shard: take or spare)',
            S('STR_VO_LUCID_TWINS', 'We heard the hail. We heard what it offered.', 'The Hollow Twins, dying (story line from 03-main-story)'))
for z, src in pending_sc:
    txt = z['shortcut']
    if not txt or txt.startswith('none'):
        continue
    for part in txt.split(';'):
        tg = sorted(set(re.findall(r'Z(\d)', part)))
        for t in tg:
            tn = ORD.get(int(t))
            if tn and tn != z['name']:
                edge(CIT, src, z_nodes[tn][0][0], 'Shortcut', 'After opening', 'This side', part.strip(), 0, '%s to %s' % (z['name'], tn))
        if not tg:
            pn = node(z['loc_id'], 'Field Postern', 'Shortcut', 'N', 0, int(z['elevation_rel_m']), '3x3x3', 'NONE', '', 'TRV_WALK', '', '', part.strip())
            edge(z['loc_id'], src, pn, 'Path', length=10)
            edge(CIT, pn, 'FIELD', 'Shortcut', 'After opening', 'Inside', part.strip(), 0, 'Out to the region map; Citadel re-entry without the Docks') if False else None
        shortcut_cue(z['loc_id'], src, part.strip())
# Citadel tonic seed + distillation + the glasshouse
loot(ZID['Underside Gardens'], z_nodes['Underside Gardens'][3][0], 'Pedestal', 'ITM_CON_TNC_DISTIL', '1', 'Side room', notes='Glasshouse behind the locked door')
loot(ZID['Hanging Streets'], z_nodes['Hanging Streets'][3][0], 'Lore pickup', 'ITM_LOR_CREW_DRAWINGS', '1', 'Side room', notes='Child lamp crew drawings of the Lamplighter')
NEW_IDS.add('ITM_LOR_CREW_DRAWINGS')
loot(ZID['Lamp Spires'], z_nodes['Lamp Spires'][3][0], 'Pedestal', 'ITM_LT_GEAR_REG_06', '1', 'Side room', notes='Wick Store: firearm pool, rarity floor Rare')
loot(ZID['Ascendant Palace'], z_nodes['Ascendant Palace'][3][0], 'Weapon rack', 'ITM_LT_GEAR_REG_06', '2', 'Side room', notes='Palace Armory: rarity floor Rare')
loot(ZID['Tether Docks'], z_nodes['Tether Docks'][4][0], 'Corpse pickup', 'ITM_CON_TNC_SEED', '1', 'Side room', notes='Crane Loft; dead lamp crew child clutching it')
# Citadel secrets (level-only)
for zo, ni, typ, tell, req, rew in [
        (2, 1, 'Hidden ledge path', 'Stall awnings form steps to a roof', '', 'ITM_LT_SMALLCHEST_REG_06'),
        (3, 2, 'Illusory wall', 'Laundry hides a cracked wall with Shard light behind it', '', 'ITM_MAT_STAR_01 x1'),
        (4, 4, 'Glide route', 'A lamp crown with no lamp, lined up with a far ledge', 'Strider glide or Step', 'ITM_LT_ARTS'),
        (6, 1, 'Breakable floor', 'Root platform with a hollow sound', '', 'ITM_CON_TNC_SEED'),
        (7, 2, 'Mirror passage', 'One mirror shows no reflection of the player', '', 'Shardborn quest clue for QST_SHB_A12')]:
    zid = ZID[ORD[zo]]
    sid = 'LSEC_%s_%d' % (zid.replace('LOC_', ''), ni)
    NEW_IDS.add(sid)
    ROWS['secrets'].append({'sec_id': sid, 'loc_id': zid, 'node_id': z_nodes[ORD[zo]][ni][0], 'world_secret': '', 'type': typ, 'tell': tell, 'requirement': req, 'reward': rew})
    if typ == 'Illusory wall':
        cue(zid, z_nodes[ORD[zo]][ni][0], 'Illusory wall struck', SFX['illusory'], '', '', VFX['illusory'])

# ---------------------------------------------------------------- 2. Sites and Choir vaults (kit templates)
lore_by_site = collections.defaultdict(list)
for li in LORE:
    host = LOC.get(li['location'], {}).get('parent_loc') or li['location']
    lore_by_site[host].append(li)
sec_by_host = collections.defaultdict(list)
for s in SECRETS:
    sec_by_host[s['host_loc']].append(s)
    lp = LOC.get(s['loc_id'], {}).get('parent_loc', '')
    if lp and lp != s['host_loc']:
        CONFLICTS.append({'what': 'Host of ' + s['loc_id'], 'a': 'locations.csv parent_loc ' + lp, 'b': 'secrets.csv host_loc ' + s['host_loc'],
                          'choice': 'Levels follow secrets.csv (it carries the tell and reward)'})
PUZZLE_RULE = {
    'Route power between three panels': 'Three junction panels in three rooms; each lights a cable run on the floor; all three open the bulkhead',
    'Statue puzzle': 'Turn four mourner statues to face the sealed tomb; wrong facing wakes an ambush',
    'Find three access codes in logs': 'Three terminals each show one digit group in a log; door keypad takes all three (codes randomised per save)',
    'Vent the flooded deck': 'Open two vents in order (low then high); water drains upward through the ceiling, revealing the lower hatch',
    'Lever trap gauntlet': 'Corridor of blade and dart traps; three levers each disarm one trap; a fourth lever is a trap itself',
    'Climb the outside on cables': 'Exterior cable climb, 3 rest ledges; updrift gusts every 6 s push the player 1 m upward',
    'Match the tone pillars': 'Strike pillars to match a tone sung by the vault; 3 rounds of 3, 4 and 5 notes; failure spawns 2 Acolytes',
    'Light the Shard-lamps to reveal a path': 'Light 4 lamps; floating stones settle into a bridge while lamps burn (90 s)',
}
for sid, s in SITES.items():
    l = R6.get(sid)
    if not l:
        continue
    r = rng(sid)
    kit = s['template']
    rooms = int(s['rooms'])
    floors = int(s['floors'])
    vault = s['site_type'] == 'Choir vault'
    boss = s['end'].replace('Site boss ', '') if s['end'].startswith('Site boss') else ''
    enc_ids = s['encounters'].split()
    keeper = [e for e in enc_ids if e in ENC and ENC[e]['template'] == 'ENT_KEEPER']
    fights = [e for e in enc_ids if e not in keeper]
    side_n = max(1, round((rooms - 2) * 0.3))
    main_n = rooms - 2 - side_n
    names = KIT_ROOMS[kit][:]
    if kit != 'KIT_TOWER':
        r.shuffle(names)
    first = {'KIT_WRECK': 'Breach Hatch', 'KIT_CATACOMB': 'Ossuary Stair', 'KIT_TOWER': 'Base Hall', 'KIT_LAB': 'Decon Airlock',
             'KIT_CAVE': 'Cave Mouth', 'KIT_FORT': 'Gatehouse', 'KIT_CHOIR_VAULT': 'Glass Antechamber'}[kit]
    names.remove(first)
    names = [first] + names
    while len(names) < rooms:
        names.append('%s %d' % (names[len(names) % len(KIT_ROOMS[kit])], len(names)))
    story = ''
    level_row(sid, s['site_type'], s['name'], story_name=story, parent='', level=s['level'], x_m=l['x_m'], y_m=l['y_m'], biome=l['biome'],
              layout='%s, %d floors, %d rooms (%d critical, %d side); %s' % (s['site_type'], floors, rooms, main_n + 2, side_n, kit),
              rooms=rooms + 1, first_play_min=s['path_min'], completion_min=int(s['path_min']) + 2 * side_n + 3 * len(sec_by_host[sid]),
              entry=s['entrance_anchor'], music='MUS_HOL_SITE' if not boss else 'MUS_HOL_SITE; MUS_BOSS_%s_*' % boss[9:],
              ambience='AMB_HOL_INTERIOR (%s)' % KIT_ROOMTONE[kit], lighting=KIT_LIGHT[kit], mood=KIT_MOOD[kit],
              vfx=VFX['updrift'] + ('; ' + VFX['tone'] if vault else ''), quests=l['gate'] if vault else '',
              notes='Site rule (plan 3.7): ends in "%s" to the entrance and unique reward %s' % (s['shortcut'], s['unique_reward']))
    dz = 1 if kit == 'KIT_TOWER' else -1
    fh = 8 if kit == 'KIT_TOWER' else 6
    ext = node(sid, 'Approach', 'Entrance', 'Y', 0, 0, '30x30x0', 'MID', '2/2', 'TRV_WALK TRV_STRIDER', LGT.get('Day', ''), 'Exterior, region light', 'Entrance Anchor 17 m away')
    checkpoint(sid, s['entrance_anchor'], ext, 'Site entrance', '', s['shortcut'])
    anchor_cues(sid, ext, s['entrance_anchor'])
    discover(sid, ext, s['name'], OSTRA.get(sid), 'site', 'AMB_HOL_INTERIOR')
    main = []
    side = []
    for i in range(main_n):
        fl = min(floors - 1, i * floors // max(1, main_n))
        sz = r.choice(['18x24x6', '4.5x30x4', '24x30x8', '12x16x5'])
        sp = 'CQ' if sz.startswith('4.5') else ('LONG' if sz.startswith('24') and kit in ('KIT_WRECK', 'KIT_LAB', 'KIT_FORT', 'KIT_TOWER') else 'MID')
        main.append(node(sid, names[1 + i], 'Combat', 'Y', fl, dz * fl * fh, sz, sp, '%d/%d' % (r.randint(1, 4), r.randint(1, 3)),
                         'TRV_WALK' + (' TRV_LADDER' if i and fl != min(floors - 1, (i - 1) * floors // max(1, main_n)) else ''), KIT_LIGHT[kit], KIT_MOOD[kit]))
    endname = 'Boss Chamber' if boss else ('Keeper Hall' if not vault else 'Choir Sanctum')
    end = node(sid, endname, 'Boss' if boss else 'Keeper', 'Y', floors - 1, dz * (floors - 1) * fh,
               '%dx%dx12' % ((int(ARENAS[boss]['diameter_m']),) * 2) if boss else '24x24x8', 'ARENA' if boss else 'MID',
               '%s/0' % ARENAS[boss]['cover_pieces'] if boss else '3/2', 'TRV_WALK', KIT_LIGHT[kit], 'Climax', 'Door seals on entry' if not boss else 'Fog gate')
    rew = node(sid, 'Reward Room', 'Reward', 'Y', floors - 1, dz * (floors - 1) * fh, '8x8x4', 'NONE', '', 'TRV_WALK', 'Single Shard light on the pedestal', 'Relief')
    for j in range(side_n):
        side.append(node(sid, names[1 + main_n + j], 'Side', 'N', min(floors - 1, j), dz * min(floors - 1, j) * fh, '10x12x4', 'CQ', '1/1', 'TRV_WALK', KIT_LIGHT[kit], KIT_MOOD[kit], 'Optional; loot and lore'))
    chain(sid, [ext] + main + [end, rew])
    for j, sn in enumerate(side):
        hub = main[min(len(main) - 1, (j * 2 + 1) % max(1, len(main)))] if main else ext
        edge(sid, hub, sn, r.choice(['Path', 'Door', 'Drop', 'Ladder']), length=r.randint(8, 25))
    if rooms >= 9 and len(side) >= 1 and len(main) >= 4:
        edge(sid, side[-1], main[-1], 'One-way', 'No', 'Side room', 'Drop down', 6, 'Interlocking loop back onto the path')
    # puzzle
    if s['puzzle']:
        pz = main[(2 * len(main)) // 3] if main else end
        for row in ROWS['nodes']:
            if row['node_id'] == pz:
                row['notes'] = (row['notes'] + '; ' if row['notes'] else '') + 'PUZZLE: ' + PUZZLE_RULE.get(s['puzzle'], s['puzzle'])
        cue(sid, pz, 'Puzzle solved', SFX['puzzle'] + ('; ' + SFX['tone'] if vault else ''), '', '', VFX['tone'] if vault else VFX['shortcut'])
    # interior anchor
    if s['interior_anchor']:
        mid = main[len(main) // 2] if main else end
        checkpoint(sid, s['interior_anchor'], mid, 'Site interior', '', '', 'Halfway rest')
        anchor_cues(sid, mid, s['interior_anchor'])
    # encounters
    slots = main[:] if main else [end]
    for i, e in enumerate(fights):
        if e in ENC:
            n = slots[i] if i < len(slots) else (side[(i - len(slots)) % len(side)] if side else slots[-1])
            place_enc(sid, n, e, note='' if i < len(slots) else 'Guards a side room')
    for i, n in enumerate(slots[len(fights):]):
        place_enc(sid, n, template=r.choice(['ENT_AMBUSH', 'ENT_ELITE']), level=s['level'], r=r, note='Fills an empty critical room')
    for e in keeper:
        place_enc(sid, end, e, note='Site keeper; unique, never respawns')
    if boss:
        a = ARENAS[boss]
        ROWS['enc'].append({'place_id': 'LEP_%s_B' % sid.replace('LOC_', ''), 'loc_id': sid, 'node_id': end, 'enc_id': boss, 'source': 'actors/bosses.csv',
                            'template': 'Boss', 'faction': '', 'level': BOSSES[boss]['Level'], 'actors': boss + ' x1', 'actor_count': 1,
                            'trigger': 'Fog gate', 'cover_points': a['cover_pieces'], 'fallback_points': '', 'respawn': 'Never',
                            'notes': '%s, %s m; %s' % (a['shape'], a['diameter_m'], a['hazards'])})
        cue(sid, end, 'Fog gate crossed', SFX['fog_enter'], 'Music_Boss=%s (Play_MUS_BOSS_%s_INTRO)' % (boss[9:], boss[9:]), 'Play_SFX_Bosses_*_ArenaAmbience', VFX['fog'], '', 'PRM_FOG; BAN_SITE_BOSS')
        cue(sid, end, 'Boss defeated', '', MUS['silence'], '', VFX['anchor'], '', 'BAN_BOSS_DEAD')
        for part in BOSSES[boss]['Drops (item refs)'].split(';'):
            loot(sid, end, 'Boss drop', part.strip().split(' ')[0], '1', 'Boss')
    else:
        cue(sid, end, 'Keeper engaged', 'Play_SFX_World_Environment_DoorOpenCloseMetal', 'Combat_Level=3', '', '', 'Room lights dim to 50% on aggro', '')
    # loot
    loot(sid, rew, 'Pedestal', s['unique_reward'], '1', 'Critical path', notes='Unique site reward (plan 3.7)')
    cue(sid, rew, 'Site cleared', SFX['chest'], 'MUS_HOL_COMBAT_END', '', VFX['glint'], '', 'NTF_SITE_CLEAR')
    for i, n in enumerate(main):
        if i % 2 == 0:
            loot(sid, n, 'Corpse pickup', 'ITM_LT_TIERMAT_REG_06', '1', 'Critical path')
        else:
            loot(sid, n, 'Corpse pickup', 'ITM_LT_CONSUMABLE', '1', 'Critical path')
    for li in lore_by_site.get(sid, []):
        n = side[0] if side and li['lore_type'] != 'Key' else (main[0] if main else rew)
        loot(sid, n, 'Key' if li['lore_type'] == 'Key' else 'Lore pickup', li['item_id'], '1', 'Side room' if n in side else 'Critical path',
             li['location'], 'Opens ' + li['unlocks'] if li['unlocks'] else li['name'])
        cue(sid, n, 'Picked up ' + li['item_id'], SFX['lore'], '', '', '', '', 'NTF_CODEX')
    chests = [x for x in R6.values() if x['kind'] == 'Small chest' and x['parent_loc'] == sid]
    crates = [x for x in R6.values() if x['kind'] == 'Shard crate' and x['parent_loc'] == sid]
    for i, c in enumerate(chests):
        loot(sid, side[i % len(side)] if side else main[-1], 'Small chest', 'ITM_LT_SMALLCHEST_REG_06', '1', 'Side room', c['loc_id'])
    for c in crates:
        loot(sid, main[-1] if main else rew, 'Shard crate', 'ITM_LT_SHARDCRATE_REG_06', '1', 'Critical path', c['loc_id'], 'Charged ammo refill before the end fight')
    if vault:
        loot(sid, rew, 'Vault chest', 'ITM_LT_VAULT_REG_06', '1', 'Critical path')
    # world secrets hosted here
    for sc in sec_by_host.get(sid, []):
        n = side[-1] if side else main[0]
        ROWS['secrets'].append({'sec_id': sc['loc_id'], 'loc_id': sid, 'node_id': n, 'world_secret': sc['loc_id'], 'type': sc['secret_type'],
                                'tell': sc['hint'], 'requirement': sc['requirement'], 'reward': sc['reward']})
        if sc['secret_type'] == 'Illusory wall':
            cue(sid, n, 'Illusory wall struck', SFX['illusory'], '', '', VFX['illusory'])
    # shortcut back
    edge(sid, rew, ext, 'Shortcut', 'After opening', 'Reward side', s['shortcut'], 0, 'Site rule: back to the entrance')
    shortcut_cue(sid, rew, s['shortcut'])
    if sid == 'LOC_DGN_REG_06_03':
        roof = node(sid, 'Roof', 'Story', 'N', floors, floors * 8 + 4, '20x20x0', 'LONG', '2/1', 'TRV_LADDER', LGT.get('Dusk', ''), 'Exposed, windy, the whole region below',
                    'LOC_CQ_REG_06_CLOCK_PRIORY_ROOF for companion quest CMPQ_C4_05; reached by a hatch from the Crown after the Prior dies')
        edge(sid, end, roof, 'Ladder', 'Yes', '', 'ACT_BOSS_CLOCKPRIOR defeated', 10)
        name_str('LOC_CQ_REG_06_CLOCK_PRIORY_ROOF', R6['LOC_DGN_REG_06_03']['name'] + ' Roof')

# ---------------------------------------------------------------- 3. Choir site
CH = 'LOC_CHOIR_REG_06'
c = R6[CH]
level_row(CH, 'Choir site', c['name'], story_name='', parent='', level=c['level'], x_m=c['x_m'], y_m=c['y_m'], biome=c['biome'],
          layout='Hidden trial, 3 rooms in a line, no boss', rooms=4, first_play_min=13, completion_min=15, entry='LOC_ANC_REG_06_27',
          music='MUS_HOL_SITE (Choir variant: reversed choir only)', ambience='AMB_HOL_INTERIOR (held choir chord)', lighting=KIT_LIGHT['KIT_CHOIR_VAULT'],
          mood='A trial inside a song; Ostra hears her own older voice', vfx=VFX['tone'], quests='', notes=c['notes'] + '; ' + c['gate'])
n0 = node(CH, 'Silent Hollow', 'Entrance', 'Y', 0, 0, '20x20x0', 'NONE', '', 'TRV_WALK', LGT.get('Night', ''), 'Nothing here until the hint', 'Entrance appears after a Shard-note hint or Ostra line within 40 m')
n1 = node(CH, 'Listening Stair', 'Trial', 'Y', -1, -8, '4x40x10', 'NONE', '', 'TRV_WALK', KIT_LIGHT['KIT_CHOIR_VAULT'], 'Hushed', 'Step only on the lit treads; a wrong step resets the stair')
n2 = node(CH, 'Echo Hall', 'Combat', 'Y', -1, -12, '24x24x10', 'MID', '0/4', 'TRV_WALK', KIT_LIGHT['KIT_CHOIR_VAULT'], 'Tense', 'Elite echo duel; Ward-break test')
n3 = node(CH, 'Resonance Altar', 'Reward', 'Y', -2, -18, '12x12x12', 'NONE', '', 'TRV_WALK', 'Single cyan shaft', 'Awe', 'Grants RES_OVERCLOCK')
chain(CH, [n0, n1, n2, n3])
edge(CH, n3, n0, 'Shortcut', 'After opening', 'Altar side', 'Glass lift to the surface', 0)
for e in ENC_BY_LOC[CH]:
    place_enc(CH, n2, e)
loot(CH, n3, 'Resonance altar', 'RES_OVERCLOCK', '1', 'Critical path')
checkpoint(CH, 'LOC_ANC_REG_06_27', n0, 'Site entrance')
anchor_cues(CH, n0, 'LOC_ANC_REG_06_27')
discover(CH, n1, c['name'], OSTRA[CH], 'site', 'AMB_HOL_INTERIOR')
cue(CH, n3, 'Resonance granted', SFX['tone'] + '; Play_SFX_Resonances_OstraOverclockAbilityReset_OstraVoiceLine', MUS['silence'], '', VFX['tone'], '', 'NTF_ABIL_UNLOCK')

# ---------------------------------------------------------------- 4. Towns (hand-authored)
TOWNS = {
    'LOC_TOWN_REG_06_01': ('', 'LOC_ANC_REG_06_07', 30, [
        ('Lamp Gate', 'Entrance', '14x10x8', 'Anchor inside the gate; two lamp posts that never go out'),
        ('Lamp Ring', 'Service', '120x6x4', 'Wall of 40 lamps the child crew relights at dusk (event 19:30); defend event for CMPQ_C6_05'),
        ('Market Row', 'Service', '40x12x6', 'ACT_NPC_VEN_TRADER_REG_06 (route start); smith ACT_NPC_VEN_SMITH_REG_06 (proposed)'),
        ('Lamp Crew Loft', 'Service', '12x10x6', 'Child lamp crew; radiant job board'),
        ('Hospice', 'Story', '20x14x6', 'LOC_CQ_REG_06_LASTLIGHT_HOSPICE (CMPQ_C6_04, CMPQ_C6_05); Hollowed patients behind glass'),
        ('Faction Post', 'Service', '10x10x5', 'Faction contact (main town rule)'),
        ('Well Square', 'Hub', '24x24x0', 'Fountain with upward spray; Shard-note spot; co-op meet point'),
        ('Watch Platform', 'Vista', '8x8x0', 'Sightline to the Lifted City (landmark rhythm)')]),
    'LOC_TOWN_REG_06_02': ('', 'LOC_ANC_REG_06_08', 15, [
        ('Mooring Post', 'Entrance', '12x12x0', 'Anchor at a giant mooring post'),
        ('Chain Street', 'Hub', '6x80x0', 'Houses chained to the ground; chains creak in updrift gusts'),
        ('Salvage Yard', 'Service', '30x20x0', 'Tinker stall (Hull Scrap trades); vehicle parts'),
        ('Drift Shrine', 'Service', '10x10x6', 'Lantern Church shrine; rest bench'),
        ('Lookout', 'Vista', '6x6x0', 'View of the floating shelves and Flyer lanes')]),
}
for tid, (story, anc, mins, spec) in TOWNS.items():
    t = R6[tid]
    level_row(tid, 'Settlement', t['name'], story_name='', parent='', level=t['level'], x_m=t['x_m'], y_m=t['y_m'], biome=t['biome'],
              layout='Safe hub, %d nodes around a central square; no combat except scripted events' % len(spec), rooms=len(spec), first_play_min=mins,
              completion_min=mins * 2, entry=anc, music='MUS_HOL_TOWN', ambience='AMB_HOL_WALLA; AMB_HOL_BED_DAY',
              lighting='Lamps 2700 K everywhere; the brightest place in the region (EV100 +2 over the field)', mood='Stubborn hope; light as a weapon',
              vfx=VFX['lamp'], quests='CMPQ_C6_04; CMPQ_C6_05; MQ_A2_05 opens here' if tid.endswith('01') else '', notes=t['notes'])
    ids = [node(tid, nm, fn, 'Y' if fn in ('Entrance', 'Hub') else 'N', 0, 0, sz, 'NONE', '', 'TRV_WALK', 'Lamp light 2700 K', 'Safe', note) for nm, fn, sz, note in spec]
    for n in ids[1:]:
        edge(tid, ids[0] if len(ids) < 6 else ids[6] if n != ids[6] else ids[0], n, 'Path', length=20)
    checkpoint(tid, anc, ids[0], 'Town')
    anchor_cues(tid, ids[0], anc)
    discover(tid, ids[0], t['name'], OSTRA[tid], 'town', 'AMB_HOL_WALLA')
    cue(tid, ids[1], 'Dusk lamp lighting (19:30)', SFX['lamp'], '', 'AMB_HOL_WALLA', VFX['lamp'], 'Lamps ignite one by one around the ring over 40 s')
    if tid.endswith('01'):
        name_str('LOC_CQ_REG_06_LASTLIGHT_HOSPICE', R6['LOC_TOWN_REG_06_01']['name'] + ' Hospice')

# ---------------------------------------------------------------- 5. Field bosses
for b, story_nodes in [('ACT_BOSS_BONEHARVESTER', [('Road In', 'Entrance', '8x120x0', 'Strider road; corpses laid in rows either side'),
                                                    ('Corpse Fields', 'Approach', '80x80x0', 'Harvest rows; Grave Vultures scatter on approach'),
                                                    ('Harvest Ring', 'Boss', None, 'Ruins in a ring; collects corpses to heal (night only 20:00-05:00)'),
                                                    ('Ossuary Cart', 'Reward', '6x4x3', 'The cart it fills; Ascendant Shard and loot')]),
                       ('ACT_BOSS_SENTINELS', [('Approach Causeway', 'Entrance', '10x150x0', 'Causeway onto a shelf; open to Flyer hijack'),
                                               ('Lift Plaza', 'Boss', None, 'Two Sentinels guard the shelf lift; one rests while the other fights at 50%'),
                                               ('Shelf Lift', 'Traversal', '8x8x60', 'Freight lift up to the floating shelves; works after the kill (region shortcut)'),
                                               ('Sentinel Plinths', 'Reward', '20x10x0', 'Plinths hold the loot')])]:
    a = ARENAS[b]
    fid = a['loc_id']
    f = R6[fid]
    level_row(fid, 'Field boss', f['name'], story_name='', parent='', level=a['level'], x_m=f['x_m'], y_m=f['y_m'], biome=f['biome'],
              layout='Open arena %s m (%s), %s cover pieces; leash 1.5x diameter' % (a['diameter_m'], a['shape'], a['cover_pieces']), rooms=len(story_nodes),
              first_play_min=8, completion_min=12, entry=a['nearest_anchor'], music='MUS_BOSS_%s_*' % b[9:], ambience='AMB_HOL_BED_NIGHT' if 'BONE' in b else 'AMB_HOL_WIND',
              lighting=LGT.get('Night' if 'BONE' in b else 'Day', ''), mood='Dread' if 'BONE' in b else 'Duel of giants', vfx=VFX['updrift'],
              quests='', notes=f['notes'] or a['condition'])
    ids = []
    for nm, fn, sz, note in story_nodes:
        ids.append(node(fid, nm, fn, 'Y' if fn != 'Traversal' else 'N', 0, 0, sz or '%sx%sx0' % (a['diameter_m'], a['diameter_m']),
                        'ARENA' if fn == 'Boss' else 'LONG', '%s/0' % a['cover_pieces'] if fn == 'Boss' else '', 'TRV_WALK TRV_STRIDER', '', '', note))
    chain(fid, ids)
    bn = [i for i, s in zip(ids, story_nodes) if s[1] == 'Boss'][0]
    ROWS['enc'].append({'place_id': 'LEP_%s_B' % fid.replace('LOC_', ''), 'loc_id': fid, 'node_id': bn, 'enc_id': b, 'source': 'actors/bosses.csv', 'template': 'Boss',
                        'faction': '', 'level': a['level'], 'actors': b + ' x1', 'actor_count': 1, 'trigger': 'Aggro at 60 m; open arena', 'cover_points': a['cover_pieces'],
                        'fallback_points': '', 'respawn': 'Never', 'notes': a['entry']})
    for e in ENC_BY_LOC[fid]:
        place_enc(fid, ids[1], e)
    if 'BONE' in b:
        place_enc(fid, ids[1], template='ENT_CRT_PACK', level=a['level'], r=rng(fid), note='Grave Vultures; scatter, do not fight')
    for part in BOSSES[b]['Drops (item refs)'].split(';'):
        loot(fid, ids[-1], 'Boss drop', part.strip().split(' ')[0], '1', 'Boss')
    checkpoint(fid, a['nearest_anchor'], ids[0], 'Field', a['anchor_run_m'], '', 'Open arena; no fog gate')
    discover(fid, ids[0], f['name'], OSTRA[fid], 'tension', 'AMB_HOL_BED_NIGHT')
    cue(fid, bn, 'Boss aggro', '', 'Music_Boss=%s' % b[9:], '', '', '', 'Boss bar')
    cue(fid, bn, 'Boss defeated', '', MUS['silence'], '', VFX['anchor'], '', 'BAN_BOSS_DEAD')

# ---------------------------------------------------------------- 6. Relay Tower
RL = 'LOC_RELAY_REG_06'
rr = R6[RL]
level_row(RL, 'Relay Tower', rr['name'], story_name='', parent='', level=rr['level'], x_m=rr['x_m'], y_m=rr['y_m'], biome=rr['biome'],
          layout='Vertical climb in 3 stages, 80 m', rooms=5, first_play_min=7, completion_min=9, entry='LOC_ANC_REG_06_06', music='MUS_HOL_EXPLORE_DAY',
          ambience='AMB_HOL_WIND', lighting=LGT.get('Day', ''), mood='Exposed; half the rungs are grey and crumble', vfx=VFX['relay'],
          quests='MQ_RT_06 (the map shows land missing)', notes=rr['notes'])
ids = [node(RL, 'Tower Base', 'Entrance', 'Y', 0, 0, '20x20x0', 'MID', '2/2', 'TRV_WALK', '', '', 'Anchor nearby; 1 patrol'),
       node(RL, 'Ledge Climb', 'Traversal', 'Y', 1, 25, '4x4x25', 'NONE', '', 'TRV_MANTLE TRV_JUMP', '', '', 'Stage 1: ledges; Hollowed rungs crumble 2 s after touch'),
       node(RL, 'Service Lift', 'Traversal', 'Y', 2, 55, '3x3x30', 'NONE', '', 'TRV_LADDER', '', '', 'Stage 2: lift; Hornet Drones harass'),
       node(RL, 'Mast Ladder', 'Traversal', 'Y', 3, 78, '1x1x23', 'NONE', '', 'TRV_LADDER', '', '', 'Stage 3: ladder; updrift gusts every 6 s'),
       node(RL, 'Beacon Platform', 'Reward', 'Y', 4, 80, '6x6x0', 'NONE', '', 'TRV_WALK', '', '', 'Map reveal; glide down with the Strider or ride the lift')]
chain(RL, ids)
edge(RL, ids[-1], ids[0], 'Drop', 'No', 'Top', 'Glide or lift', 0)
for e in ENC_BY_LOC[RL]:
    place_enc(RL, ids[0], e)
place_enc(RL, ids[2], template='ENT_AMBUSH', level=rr['level'], r=rng(RL), note='Drones attack the lift cage')
checkpoint(RL, 'LOC_ANC_REG_06_06', ids[0], 'Relay')
discover(RL, ids[0], rr['name'], OSTRA[RL])
cue(RL, ids[-1], 'Relay activated', SFX['relay'], 'Play_MUS_HOL_DISCOVERY', 'AMB_HOL_WIND', VFX['relay'], '', 'BAN_TOWER; TUT_TOWER (first tower only)',
    S('STR_VO_OSTRA_RELAY_REG_06_MAP', "There. Map's done. And there are holes in it. Land I can't see because it isn't there.", 'Ostra at the top (MQ_RT_06)'))

# ---------------------------------------------------------------- 7. Landmarks
LMK_SPEC = {
    'LOC_LMK_REG_06_01': ('Vista', 'The Lifted City seen from below; the Citadel silhouette lines up with the Tether Docks cable', 'TRV_WALK'),
    'LOC_LMK_REG_06_02': ('Traversal', 'River falls upward 98 m; ride the lift current to a shelf ledge with a chest', 'TRV_LIFTCURRENT'),
    'LOC_LMK_REG_06_03': ('Vista', 'Rows of bones to the horizon; Bone Harvester grounds visible at night by its lantern', 'TRV_WALK'),
    'LOC_LMK_REG_06_04': ('Vista', 'Two Sentinel statues 95 m tall; their heads turn to track the player at 200 m (no attack)', 'TRV_WALK'),
    'LOC_LMK_REG_06_05': ('Climb', 'Meridian orbit tether, 104 m of cable; mantle route to a Starmetal node at the top', 'TRV_MANTLE TRV_LADDER'),
    'LOC_LMK_REG_06_06': ('Vista', 'Clockhouse Tower strikes the hour; the bell can be heard 2 km away and marks game time', 'TRV_WALK'),
    'LOC_LMK_REG_06_07': ('Vista', 'Sinkhole 400 m across; no bottom renders; debris rises out of it in slow columns', 'TRV_WALK TRV_STRIDER'),
}
for lid, (fn, note, trv) in LMK_SPEC.items():
    m = R6[lid]
    an, ad = nearest_anchor(m)
    lmk = [x for x in rd(os.path.join(W, 'landmarks.csv')) if x['loc_id'] == lid][0]
    level_row(lid, 'Landmark', m['name'], story_name='', parent='', level=m['level'], x_m=m['x_m'], y_m=m['y_m'], biome=m['biome'],
              layout='%s m tall, seen from %s km; 3 nodes' % (lmk['height_m'], lmk['visible_km']), rooms=3, first_play_min=3, completion_min=5, entry=an,
              music='Play_MUS_HOL_DISCOVERY', ambience='AMB_HOL_WIND; AMB_HOL_EMITTERS', lighting=LGT.get('Dusk', ''), mood='Awe', vfx=VFX['upfall'] if 'Falls' in m['name'] else VFX['updrift'],
              quests='', notes=note)
    ids = [node(lid, 'Approach', 'Entrance', 'Y', 0, 0, '40x40x0', 'MID', '', 'TRV_WALK TRV_STRIDER', '', '', 'Nearest Anchor %s at %d m' % (an, ad)),
           node(lid, 'Base', fn, 'Y', 0, 0, '30x30x0', 'MID', '2/2', trv, '', '', note),
           node(lid, 'Vista Point', 'Vista', 'N', 1, int(float(lmk['height_m']) // 3), '6x6x0', 'NONE', '', trv, '', '', 'Shard-note spot; camera framing for the screenshot')]
    chain(lid, ids)
    discover(lid, ids[1], m['name'], OSTRA[lid], 'explore', 'AMB_HOL_WIND', VFX['upfall'] if 'Falls' in m['name'] else VFX['updrift'])
    if lid.endswith('02'):
        loot(lid, ids[2], 'Small chest', 'ITM_LT_SMALLCHEST_REG_06', '1', 'Secret', notes='Only reachable by the lift current')
    if lid.endswith('05'):
        loot(lid, ids[2], 'Gather node', 'ITM_LT_NODE_STAR_METEOR', '1', 'Side room', notes='Starmetal at the tether top')

# ---------------------------------------------------------------- 8. POIs and patrols (templates)
POI_T = {
    'faction camp': [('Perimeter', 'Entrance', 'Watch fires and a lookout'), ('Camp Ring', 'Combat', 'Tents, cover every 8-12 m'), ('Leader Tent', 'Reward', 'Leader sleeps here; camp chest')],
    'ruin': [('Broken Arch', 'Entrance', 'Collapsed gate'), ('Ruin Court', 'Combat', 'Low walls for cover'), ('Cellar', 'Reward', 'Cellar hatch; chest or lore')],
    'wreck fragment': [('Hull Shard', 'Entrance', 'Hull plate standing on end'), ('Interior Pocket', 'Reward', 'Crawl-in pocket; salvage')],
    'wayshrine': [('Shrine Steps', 'Entrance', 'Lantern Church wayshrine'), ('Altar', 'Reward', 'Shard-note and offering bowl; Echo summon sign spot')],
    'watchtower': [('Tower Foot', 'Entrance', 'Ladder start'), ('Tower Top', 'Vista', 'View ring; artillery post')],
    'overturned cart': [('Cart', 'Reward', 'Spilled cargo; corpse with a note')],
    'overlook': [('Path Up', 'Entrance', 'Switchback'), ('Overlook Edge', 'Vista', 'Frames the next landmark')],
    'hermit hut': [('Yard', 'Entrance', 'Hollow-fire stove'), ('Hut', 'Reward', 'Hermit journal; maybe alive at night')],
    'grave field': [('Grave Rows', 'Combat', 'Graves lift and drift; Shamblers rise'), ('Mausoleum', 'Reward', 'Sealed tomb')],
    'shard crater': [('Crater Rim', 'Entrance', 'Glass rim'), ('Crater Floor', 'Combat', 'Shard veins; gather nodes')],
    'hunting ground': [('Game Trail', 'Entrance', 'Tracks'), ('Feeding Ground', 'Combat', 'Creature pack')],
    'lair': [('Lair Mouth', 'Entrance', 'Bones outside'), ('Den', 'Combat', 'Large creature; nest loot')],
    'trader stop': [('Wagon Stop', 'Service', 'Wandering trader stop on route; safe while trader is present')],
    'vehicle depot': [('Depot Yard', 'Service', 'Skimmer spawn; Flyer landing pad'), ('Workshop', 'Reward', 'Parts crate')],
}
POI_MIN = {'faction camp': 6, 'ruin': 4, 'grave field': 4, 'lair': 4, 'hunting ground': 3, 'shard crater': 3}
for pid, p in sorted(R6.items()):
    if p['kind'] != 'POI':
        continue
    kind = p['tags'].split(';')[0]
    spec = POI_T.get(kind, [('Site', 'Entrance', '')])
    an, ad = nearest_anchor(p)
    level_row(pid, 'POI', p['name'], story_name='', parent='', level=p['level'], x_m=p['x_m'], y_m=p['y_m'], biome=p['biome'],
              layout='%s; %d nodes within 40 m' % (kind, len(spec)), rooms=len(spec), first_play_min=POI_MIN.get(kind, 2),
              completion_min=POI_MIN.get(kind, 2) + 2 * len(sec_by_host.get(pid, [])), entry=an, music='MUS_HOL_EXPLORE_DAY', ambience='AMB_HOL_BED_DAY; AMB_HOL_EMITTERS',
              lighting=LGT.get('Day', ''), mood='', vfx=VFX['updrift'], quests=p['notes'], notes='Nearest Anchor %d m' % ad)
    ids = [node(pid, nm, fn, 'Y', 0, 0, '20x20x0', 'MID' if fn == 'Combat' else 'NONE', '3/2' if fn == 'Combat' else '', 'TRV_WALK TRV_STRIDER', '', '', note) for nm, fn, note in spec]
    chain(pid, ids)
    name_str(pid, p['name'])
    encs = ENC_BY_LOC[pid]
    tgt = [i for i, s in zip(ids, spec) if s[1] == 'Combat'] or [ids[0]]
    for e in encs:
        place_enc(pid, tgt[0], e)
    if kind in ('faction camp', 'ruin', 'cellar', 'overturned cart', 'wreck fragment', 'hermit hut', 'grave field', 'vehicle depot'):
        loot(pid, ids[-1], 'Small chest' if kind != 'vehicle depot' else 'Parts crate', 'ITM_LT_SMALLCHEST_REG_06' if kind != 'vehicle depot' else 'ITM_LT_NODE_PARTS_CRATE', '1', 'Critical path')
    if kind == 'wayshrine':
        loot(pid, ids[-1], 'Offering bowl', 'ITM_LT_CONSUMABLE', '1', 'Critical path')
    for sc in sec_by_host.get(pid, []):
        ROWS['secrets'].append({'sec_id': sc['loc_id'], 'loc_id': pid, 'node_id': ids[-1], 'world_secret': sc['loc_id'], 'type': sc['secret_type'],
                                'tell': sc['hint'], 'requirement': sc['requirement'], 'reward': sc['reward']})
    cue(pid, ids[0], 'Discover', SFX['area'], MUS['explore'], 'AMB_HOL_EMITTERS', '', '', 'NTF_DISCOVER (STR_%s_NAME)' % pid)
for pid, p in sorted(R6.items()):
    if p['kind'] != 'Patrol route':
        continue
    r = rng(pid)
    rad = r.randint(75, 150)
    level_row(pid, 'Patrol route', p['name'], story_name='', parent='', level=p['level'], x_m=p['x_m'], y_m=p['y_m'], biome=p['biome'],
              layout='Loop of 4 waypoints, radius %d m (%d m walk)' % (rad, round(2 * math.pi * rad)), rooms=4, first_play_min=2, completion_min=2,
              entry=p['name'].split()[-1], music='MUS_HOL_TENSION on sight', ambience='AMB_HOL_BED_DAY', lighting='', mood='', vfx='', quests='', notes='Walk speed 1.4 m/s; pauses 6 s at each waypoint')
    ids = [node(pid, 'Waypoint %s' % c, 'Patrol', 'Y', 0, 0, '10x10x0', 'MID', '1/1', 'TRV_WALK', '', '', 'Bearing %d deg, %d m from centre' % (90 * i + r.randint(-20, 20), rad))
           for i, c in enumerate('ABCD')]
    chain(pid, ids + [ids[0]], length=round(math.pi * rad / 2))
    for e in ENC_BY_LOC[pid]:
        place_enc(pid, ids[0], e)

# public events (world kind "Public event") and a fallback for any new kind the world adds
EVT_STAGES = [('Warning', 'Event', 'Ostra warns; HUD event banner at 300 m; 30 s countdown'), ('Wave 1', 'Combat', 'World encounter group'),
              ('Wave 2', 'Combat', 'Reinforcements from the fallback points, +50% count'), ('Finale', 'Combat', 'Elite and escort; event timer 5 min total'),
              ('Event Cache', 'Reward', 'Chest for everyone who took part (loot per player)')]
HANDLED = {'Anchor', 'Gather node', 'Small chest', 'Shard crate', 'Locked door', 'Secret', 'Lore site', 'Citadel zone', 'Citadel', 'Site', 'Choir vault',
           'Choir site', 'Settlement', 'Field boss', 'Relay Tower', 'Landmark', 'POI', 'Patrol route'}
for pid, p in sorted(R6.items()):
    if p['kind'] in HANDLED:
        continue
    r = rng(pid)
    an, ad = nearest_anchor(p)
    ev = p['kind'] == 'Public event'
    spec = EVT_STAGES if ev else [('Approach', 'Entrance', ''), ('Main Space', 'Combat', ''), ('Cache', 'Reward', '')]
    level_row(pid, p['kind'], p['name'], story_name='', parent=p['parent_loc'], level=p['level'], x_m=p['x_m'], y_m=p['y_m'], biome=p['biome'],
              layout=('Timed public event in 5 stages around %s' % p['parent_loc']) if ev else 'Fallback layout, 3 nodes', rooms=len(spec),
              first_play_min=5 if ev else 3, completion_min=5 if ev else 3, entry=an, music='MUS_HOL_COMBAT_L1 rising to L3 by the finale' if ev else 'MUS_HOL_EXPLORE_DAY',
              ambience='AMB_HOL_BED_DAY', lighting=LGT.get('Day', ''), mood='Sudden, loud, co-op', vfx=VFX['updrift'], quests='', notes=p['notes'][:160])
    ids = [node(pid, a, b, 'Y', 0, 0, '60x60x0' if b == 'Combat' else '20x20x0', 'MID' if b == 'Combat' else 'NONE', '5/3' if b == 'Combat' else '', 'TRV_WALK TRV_STRIDER', '', '', c) for a, b, c in spec]
    chain(pid, ids)
    name_str(pid, p['name'])
    combat = [i for i, s_ in zip(ids, spec) if s_[1] == 'Combat']
    for k, e in enumerate(ENC_BY_LOC[pid]):
        place_enc(pid, combat[k % len(combat)], e)
    if ev:
        place_enc(pid, combat[1], template='ENT_PATROL', level=p['level'], r=r, note='Wave 2 reinforcements')
        place_enc(pid, combat[2], template='ENT_ELITE', level=p['level'], r=r, note='Finale')
        loot(pid, ids[-1], 'Event cache', 'ITM_LT_GEAR_REG_06', '1', 'Critical path', notes='Per player; plus ITM_LT_TIERMAT_REG_06 x2')
        cue(pid, ids[0], 'Event starts', 'Play_SFX_Ui_Interface_EventStart', MUS['tension'], '', VFX['skybeam'] if 'Shard' in p['name'] else '', '', 'NTF_DISCOVER (event)',
            S('STR_VO_OSTRA_%s' % pid.replace('LOC_', ''), {'01': 'Shards falling. Get under something, then get what lands.', '02': 'Remnant convoy. Drones, cargo, guns. Hit the lead walker first.',
              '03': 'Hollowed surge. They come in a wave. Hold a choke point.', '04': 'Raiders on a caravan. If we move now, someone lives.'}.get(pid[-2:], 'Something is happening nearby.'), 'Ostra, public event start'))
        cue(pid, ids[-1], 'Event complete', SFX['chest'], 'MUS_HOL_COMBAT_END', '', VFX['glint'], '', 'BAN (event complete)')
    if 'Thorn' in p['name']:
        CONFLICTS.append({'what': 'Faction in ' + pid, 'a': 'name says Thorn raid', 'b': 'Hollowdeep factions: Hollowed, Choirborn, Remnant (regions_layout)',
                          'choice': 'Level uses the encounter as placed (its own faction); world thread should rename the event'})

# ---------------------------------------------------------------- 9. Campaign places and borders
CQ = [('LOC_CQ_REG_06_GLASS_RIVER', 'Glass River', 'Campaign place', 8240, 1640, 58,
       [('River Bank', 'Entrance', 'Glass ice edge'), ('Glass Crossing', 'Traversal', 'Glass cracks under heavy armour (Equip Load over 70%) after 3 s; slide physics'),
        ('Frozen Current', 'Combat', 'Shamblers trapped in the glass break free when the player passes'), ('Drowned Cart', 'Story', 'CMPQ_C6_04 step: what the river took')],
       'CMPQ_C6_04 What the River Took', 'Placed between LOC_TOWN_REG_06_01 and LOC_DGN_REG_06_02 (design choice)'),
      ('LOC_CQ_REG_06_LAMP_TOWER', "Ires's Lamp Tower", 'Campaign place', 9700, 2190, 69,
       [('Rim Path', 'Entrance', 'Path along the Pale Hole rim; ledger clues on three posts'), ('Tower Foot', 'Combat', 'Choirborn guard; elite'),
        ('Spiral of Lamps', 'Traversal', '120 m spiral; lamps point up, not out'), ('Feeding Room', 'Story', 'Shards fed into a beam to the sky'),
        ("Ires's Lantern Room", 'Story', 'MQ_A2_08 conversation; Ires does not fight here')],
       'MQ_A2_08 The Captain\'s Mask', 'New location: on the Pale Hole rim (design choice); hidden until the ledger is read'),
      ('LOC_CON_08', 'Root Bridge (Hollowdeep side)', 'Border', None, None, 55,
       [('Bridge End', 'Entrance', 'Thornwood colour drains to grey across 40 m'), ('Grey Verge', 'Combat', 'First Hollowdeep patrol'), ('First View', 'Vista', 'Lifted City on the horizon')],
       '', 'Main entry from Thornwood (CON_08)'),
      ('LOC_CON_09', 'Glassfall Descent (landing)', 'Border', None, None, 57,
       [('Landing Shelf', 'Entrance', 'One-way drop lands here'), ('Return Lift', 'Shortcut', 'Lift back up once lit from below')],
       '', 'Entry from Glasswaste (CON_09)')]
for cid, nm, kind, x, y, lv, spec, q, note in CQ:
    base = LOC.get(cid, {})
    x = x if x is not None else base.get('x_m', '')
    y = y if y is not None else base.get('y_m', '')
    level_row(cid, kind, nm, story_name='', parent='', level=lv, x_m=x, y_m=y, biome=base.get('biome', 'Grey barrens'), layout='%d nodes' % len(spec), rooms=len(spec),
              first_play_min=6 if kind == 'Border' else 15, completion_min=8 if kind == 'Border' else 20, entry=nearest_anchor({'x_m': x, 'y_m': y})[0],
              music='MUS_HOL_EXPLORE_DAY' if kind == 'Border' else 'MUS_HOL_TENSION', ambience='AMB_HOL_BED_DAY; AMB_HOL_HOLLOWING',
              lighting=LGT.get('Dusk', ''), mood='', vfx=VFX['glassriver'] if 'GLASS' in cid else (VFX['skybeam'] if 'LAMP' in cid else VFX['drain']), quests=q, notes=note)
    if cid not in LOC:
        NEW_IDS.add(cid)
    ids = [node(cid, a, b, 'Y', 0, 0, '20x20x0', 'MID' if b == 'Combat' else 'NONE', '3/2' if b == 'Combat' else '', 'TRV_WALK', '', '', c) for a, b, c in spec]
    chain(cid, ids)
    for n, s in zip(ids, spec):
        if s[1] == 'Combat':
            place_enc(cid, n, template='ENT_ELITE' if 'LAMP' in cid else 'ENT_PATROL', level=lv, r=rng(cid))
    discover(cid, ids[0], nm, OSTRA.get(cid), 'explore', 'AMB_HOL_HOLLOWING', VFX['drain'])
    if 'CON_08' in cid:
        cue(cid, ids[0], 'Cross into Hollowdeep', SFX['updrift'], 'Music_Region=HOL', 'AMB_HOL_HOLLOWING (RTPC 0 to 0.6 over 40 m)', VFX['drain'], 'Saturation lerps 1.0 to 0.55 over 40 m')

# ---------------------------------------------------------------- 10. Field placements: chests, crates, gather nodes, doors, lore without a site
LEVEL_POS = [l for l in ROWS['levels'] if l['x_m'] not in ('', None) and l['kind'] not in ('Citadel zone',)]


def nearest_level(p, maxd=150):
    best = min(LEVEL_POS, key=lambda l: dist(l, p))
    return best['loc_id'] if dist(best, p) <= maxd else 'FIELD'


first_node = {}
for nrow in ROWS['nodes']:
    first_node.setdefault(nrow['loc_id'], nrow['node_id'])
placed_world = {x['world_loc'] for x in ROWS['loot'] if x['world_loc']}
NODE_LT = {'glass_cluster': 'ITM_LT_NODE_GLASS_CLUSTER', 'parts_crate': 'ITM_LT_NODE_PARTS_CRATE', 'scrap_pile': 'ITM_LT_NODE_SCRAP_PILE',
           'shard_vein': 'ITM_LT_NODE_SHARD_VEIN', 'star_meteor': 'ITM_LT_NODE_STAR_METEOR'}
for lid, p in sorted(R6.items()):
    if p['kind'] in ('Small chest', 'Shard crate', 'Gather node') and lid not in placed_world:
        host = nearest_level(p)
        tag = p['tags']
        it = {'Small chest': 'ITM_LT_SMALLCHEST_REG_06', 'Shard crate': 'ITM_LT_SHARDCRATE_REG_06'}.get(p['kind']) or NODE_LT.get(tag, 'ITM_LT_NODE_' + tag.upper())
        an, ad = nearest_anchor(p)
        loot(host, first_node.get(host, ''), p['kind'], it, '1', 'Field' if host == 'FIELD' else 'Side room', lid,
             'x %s y %s; nearest Anchor %s %d m' % (p['x_m'], p['y_m'], an, ad))
    if p['kind'] == 'Locked door' and not p['parent_loc']:
        host = nearest_level(p, 400)
        k = door_key.get(lid, p['gate'].replace('Key ', ''))
        n = node(host, 'Locked Door', 'Side', 'N', 0, 0, '3.2x2x4', 'NONE', '', 'TRV_WALK', '', '', '%s; key %s; behind: ITM_LT_SMALLCHEST_REG_06' % (lid, k))
        edge(host, first_node.get(host, n), n, 'Locked door', 'Yes', 'Either side', '%s (key %s)' % (lid, k), 10)
        loot(host, n, 'Small chest', 'ITM_LT_SMALLCHEST_REG_06', '1', 'Side room', lid, 'Behind the locked door')
        wk = p['gate'].replace('Key ', '')
        if wk != k:
            CONFLICTS.append({'what': 'Key for ' + lid, 'a': 'world locations.csv gate: ' + wk, 'b': 'items lore_items.csv unlocks: ' + k,
                              'choice': 'Levels use the key whose own row says it unlocks the door (%s)' % k})
for host, lis in lore_by_site.items():
    if host in first_node and not any(x['item_or_table'] == lis[0]['item_id'] for x in ROWS['loot']):
        for li in lis:
            loot(host, first_node[host], 'Key' if li['lore_type'] == 'Key' else 'Lore pickup', li['item_id'], '1', 'Side room', li['location'], li['name'])
    elif host not in first_node:
        for li in lis:
            p = LOC.get(li['location'])
            h = nearest_level(p, 400) if p else 'FIELD'
            loot(h, first_node.get(h, ''), 'Key' if li['lore_type'] == 'Key' else 'Lore pickup', li['item_id'], '1', 'Side room', li['location'], li['name'])
# secrets hosted on levels not yet handled
done = {s['world_secret'] for s in ROWS['secrets']}
for sc in SECRETS:
    if sc['loc_id'] not in done:
        h = sc['host_loc'] if sc['host_loc'] in first_node else 'FIELD'
        ROWS['secrets'].append({'sec_id': sc['loc_id'], 'loc_id': h, 'node_id': first_node.get(h, ''), 'world_secret': sc['loc_id'], 'type': sc['secret_type'],
                                'tell': sc['hint'], 'requirement': sc['requirement'], 'reward': sc['reward']})
# field anchors as checkpoints
for aid, a in ANCH.items():
    if a['anchor_type'] == 'Field' and not any(c['anchor_id'] == aid for c in ROWS['checkpoints']):
        h = nearest_level(a, 200)
        checkpoint(h, aid, first_node.get(h, ''), 'Field', '', '', 'x %s y %s' % (a['x_m'], a['y_m']))

# ---------------------------------------------------------------- strings for the remaining levels, data requests, conflicts
have = {s['str_id'] for s in STRINGS}
for l in ROWS['levels']:
    sid = 'STR_%s_NAME' % l['loc_id']
    if sid not in have:
        name_str(l['loc_id'], l['story_name'] or l['name'])
        have.add(sid)
for l in ROWS['levels']:
    l['name_str'] = 'STR_%s_NAME' % l['loc_id']

CONFLICTS.append({'what': 'Place names (towns, sites, Citadel)', 'a': 'world locations.csv names', 'b': 'campaign lore bible names (Clock Priory, Vault of Names, Lamp Works; town names now match the world)',
                  'choice': 'Project rule: world locations.csv wins on names and IDs; campaign is renaming its story names and VO to match. Levels use world names everywhere'})
CONFLICTS.append({'what': 'Undervault under Hollowdeep', 'a': 'lore bible 5: under Cinderreach, Glasswaste, Hollowdeep', 'b': 'world connections: entries in REG_02, REG_03, REG_05',
                  'choice': 'No Undervault entry built in Hollowdeep (world owns layout). Deep Vault Nine stays a surface vault'})
CONFLICTS.append({'what': 'Lamplighter phases', 'a': 'bosses.csv: 3 phases at 65/30', 'b': 'story: flees at 30%',
                  'choice': 'First fight ends at the phase 3 threshold (she flees up the Lamp Chute); phase 3 plays in the MQ_A3_03 rematch'})

REQ += [
    {'req_id': 'LREQ_01', 'target': 'data/ui/strings.csv', 'field': 'new rows', 'value': 'All rows in level_strings.csv (%d strings: area names, Ostra lines, two story lines)' % len(STRINGS),
     'reason': 'No STR_LOC_*_NAME strings exist for discovery banners (NTF_DISCOVER) or map labels'},
    {'req_id': 'LREQ_02', 'target': 'data/world/locations.csv', 'field': 'new LOC_ rows', 'value': 'LOC_CQ_REG_06_LAMP_TOWER (9700, 2190, level 69); LOC_CQ_REG_06_GLASS_RIVER (8240, 1640, level 58); LOC_CQ_REG_06_LASTLIGHT_HOSPICE (inside LOC_TOWN_REG_06_01); LOC_CQ_REG_06_CLOCK_PRIORY_ROOF (top of LOC_DGN_REG_06_03)',
     'reason': 'Campaign quests MQ_A2_08, CMPQ_C6_04, CMPQ_C6_05, CMPQ_C4_05 target them; world thread to confirm positions'},
    {'req_id': 'LREQ_03', 'target': 'data/world/npcs.csv', 'field': 'new NPC', 'value': 'ACT_NPC_VEN_SMITH_REG_06, main-town smith, home LOC_TOWN_REG_06_01, sells region upgrade materials',
     'reason': 'World notes say the main town has a smith; no smith NPC exists for REG_06'},
    {'req_id': 'LREQ_04', 'target': 'data/items/lore_items.csv', 'field': 'new rows', 'value': "ITM_LOR_LEDGER_LAMPLIGHTER (Lamplighter's Ledger, LOC_CIT_REG_06_Z5, starts MQ_A2_08); ITM_LOR_CREW_DRAWINGS (Lamp Crew Drawings, LOC_CIT_REG_06_Z3)",
     'reason': 'Story clue and Citadel lore item'},
    {'req_id': 'LREQ_06', 'target': 'design/world (owner)', 'field': 'locked door keys', 'value': 'Use lore_items.csv unlocks column (ITM_LOR_346 opens LOC_DOOR_REG_06_06, and so on)', 'reason': 'locations.csv gate column is off by one key; see conflicts.csv'},
    {'req_id': 'LREQ_07', 'target': 'design/world/encounters.csv (owner) or a level encounter table in data/', 'field': 'new encounters', 'value': 'All LENC_06_* rows in level_encounters.csv',
     'reason': 'Combat nodes the world table left empty (Citadel has 2-3 h of path but 24 world groups)'},
]
# hooks to request
hooks = set()
for c in ROWS['cues']:
    for f in ('audio_events', 'vfx'):
        for h in c[f].replace(';', ' ').split():
            if h.startswith(('Play_', 'VFX_')) and '*' not in h:
                hooks.add(h)
for l in ROWS['levels']:
    for h in l['vfx'].replace(';', ' ').split():
        if h.startswith('VFX_'):
            hooks.add(h)
missing_hooks = sorted(h for h in hooks if h not in KNOWN)
REQ.append({'req_id': 'LREQ_08', 'target': 'data/assets/asset_hooks.csv and design/audio/event_map.csv', 'field': 'new hooks', 'value': '; '.join(missing_hooks),
            'reason': 'Level props, Hollowdeep set pieces and the Lamplighter escape'})
NEW_IDS |= set(missing_hooks)

# ---------------------------------------------------------------- write tables
wr('levels.csv', ROWS['levels'], ['loc_id', 'kind', 'name', 'story_name', 'name_str', 'parent', 'level', 'x_m', 'y_m', 'biome', 'layout', 'rooms', 'first_play_min',
                                  'completion_min', 'entry', 'music', 'ambience', 'lighting', 'mood', 'vfx', 'quests', 'notes'])
wr('level_nodes.csv', ROWS['nodes'], ['node_id', 'loc_id', 'seq', 'name', 'function', 'critical', 'floor', 'elev_rel_m', 'size_m', 'space', 'cover_low', 'cover_high',
                                      'traversal', 'lighting', 'mood', 'notes'])
wr('level_edges.csv', ROWS['edges'], ['edge_id', 'loc_id', 'from_node', 'to_node', 'type', 'two_way', 'opens_from', 'requirement', 'length_m', 'notes'])
wr('level_encounters.csv', ROWS['enc'], ['place_id', 'loc_id', 'node_id', 'enc_id', 'source', 'template', 'faction', 'level', 'actors', 'actor_count', 'trigger',
                                         'cover_points', 'fallback_points', 'respawn', 'notes'])
wr('level_loot.csv', ROWS['loot'], ['lot_id', 'loc_id', 'node_id', 'container', 'item_or_table', 'qty', 'visibility', 'world_loc', 'notes'])
wr('level_secrets.csv', ROWS['secrets'], ['sec_id', 'loc_id', 'node_id', 'world_secret', 'type', 'tell', 'requirement', 'reward'])
wr('level_checkpoints.csv', ROWS['checkpoints'], ['loc_id', 'anchor_id', 'node_id', 'kind', 'boss_run_m', 'shortened_by', 'notes'])
wr('level_cues.csv', ROWS['cues'], ['cue_id', 'loc_id', 'node_id', 'trigger', 'audio_events', 'music_state', 'ambience', 'vfx', 'lighting', 'popup', 'vo_string'])
wr('level_strings.csv', STRINGS, ['str_id', 'text', 'max_chars', 'context'])
wr('data-requests.csv', REQ, ['req_id', 'target', 'field', 'value', 'reason'])
seen = set()
CONF = [c for c in CONFLICTS if not (c['what'] in seen or seen.add(c['what']))]
wr('conflicts.csv', CONF, ['what', 'a', 'b', 'choice'])

# ---------------------------------------------------------------- SVG maps (node graphs; Citadel side view)
def svg_graph(loc_ids, fname, title, side_view=False):
    nodes = [n for n in ROWS['nodes'] if n['loc_id'] in loc_ids]
    if not nodes:
        return
    pos = {}
    col = collections.Counter()
    for n in nodes:
        lo = loc_ids.index(n['loc_id'])
        if side_view:
            i = int(n['seq']) - 1
            x = 80 + lo * 260 + (i % 2) * 125
            y = 900 - int(float(n['elev_rel_m'])) * 5 - (i // 2) * 40
        else:
            fl = abs(int(n['floor'] or 0))
            if n['critical'] == 'Y':
                col['crit'] += 1
                x = 20 + col['crit'] * 125
                y = 70 + fl * 70
            else:
                hub = next((e['from_node'] for e in ROWS['edges'] if e['to_node'] == n['node_id'] and e['from_node'] in pos), None)
                hx, hy = pos.get(hub, (20 + (col['crit'] + 1) * 125, 70))
                col[hub] += 1
                x, y = hx, hy + 45 * col[hub] + 15
        pos[n['node_id']] = (x, y)
    W_ = max(p[0] for p in pos.values()) + 160
    H_ = max(p[1] for p in pos.values()) + 90
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif" font-size="10">' % (W_, H_),
           '<rect width="100%" height="100%" fill="#1d1c22"/>', '<text x="20" y="24" fill="#e8e4dc" font-size="14">%s</text>' % title]
    colors = {'Shortcut': '#8FE3EE', 'Locked door': '#A87A4A', 'One-way': '#9B7BD6', 'Drop': '#9B7BD6'}
    for e in ROWS['edges']:
        if e['from_node'] in pos and e['to_node'] in pos:
            (x1, y1), (x2, y2) = pos[e['from_node']], pos[e['to_node']]
            c = colors.get(e['type'], '#8A857A')
            dash = ' stroke-dasharray="6,4"' if e['type'] in colors else ''
            if side_view and e['type'] == 'Shortcut':
                out.append('<path d="M%d %d Q%d %d %d %d" fill="none" stroke="%s" stroke-width="2"%s/>' % (x1, y1, (x1 + x2) // 2, min(y1, y2) - 120, x2, y2, c, dash))
            else:
                out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"%s/>' % (x1, y1, x2, y2, c, dash))
    fill = {'Boss': '#7a2e2e', 'Anchor': '#4F8FE6', 'Entrance': '#4F8FE6', 'Reward': '#9B7BD6', 'Side': '#3a3940', 'Shortcut': '#2c5a60'}
    for n in nodes:
        x, y = pos[n['node_id']]
        out.append('<rect x="%d" y="%d" width="104" height="30" rx="4" fill="%s" stroke="#e8e4dc" stroke-width="0.5"/>' % (x - 52, y - 15, fill.get(n['function'], '#55535c')))
        out.append('<text x="%d" y="%d" fill="#e8e4dc" text-anchor="middle">%s</text>' % (x, y - 2, n['name'][:20].replace('&', 'and').replace("'", '&#39;')))
        out.append('<text x="%d" y="%d" fill="#b8b2a8" text-anchor="middle" font-size="8">%s</text>' % (x, y + 10, n['function']))
    if side_view:
        for lo, lid in enumerate(loc_ids):
            zn = next((l['name'] for l in ROWS['levels'] if l['loc_id'] == lid), lid)
            out.append('<text x="%d" y="%d" fill="#8FE3EE" font-size="12">Z%d %s</text>' % (40 + lo * 260, H_ - 30, lo + 1, zn.replace("'", '&#39;')))
    out.append('<text x="20" y="%d" fill="#b8b2a8">Grey: path. Cyan dashed: shortcut. Bronze dashed: locked door. Violet dashed: one-way or drop. Blue: Anchor or entrance. Red: boss.</text>' % (H_ - 12))
    out.append('</svg>')
    open(os.path.join(OUT, 'maps', fname), 'w').write('\n'.join(out))


svg_graph([z['loc_id'] for z in ZONES], 'citadel_flow.svg', 'The Lifted City: side-view flow (height = elevation; dashed = shortcuts)', side_view=True)
for sid in list(SITES) + [CH, RL] + list(TOWNS) + [ARENAS['ACT_BOSS_BONEHARVESTER']['loc_id'], ARENAS['ACT_BOSS_SENTINELS']['loc_id'], 'LOC_CQ_REG_06_LAMP_TOWER']:
    svg_graph([sid], '%s.svg' % sid, '%s (%s)' % (next((l['name'] for l in ROWS['levels'] if l['loc_id'] == sid), sid), sid))

# ---------------------------------------------------------------- checks
CHECKS = []


def check(name, ok, detail=''):
    CHECKS.append({'check': name, 'result': 'PASS' if ok else 'FAIL', 'detail': detail})


ids = {n['node_id'] for n in ROWS['nodes']}
check('Edges point at real nodes', all(e['from_node'] in ids and e['to_node'] in ids for e in ROWS['edges']))
# reachability of critical nodes per level
bad = []
for l in ROWS['levels']:
    ns = [n['node_id'] for n in ROWS['nodes'] if n['loc_id'] == l['loc_id']]
    if not ns:
        continue
    adj = collections.defaultdict(set)
    for e in ROWS['edges']:
        adj[e['from_node']].add(e['to_node'])
        if e['two_way'] == 'Yes' or e['type'] == 'Path':
            adj[e['to_node']].add(e['from_node'])
    seen_, st = {ns[0]}, [ns[0]]
    while st:
        for m in adj[st.pop()]:
            if m not in seen_:
                seen_.add(m)
                st.append(m)
    miss = [n for n in ns if n not in seen_]
    if miss:
        bad.append('%s: %s' % (l['loc_id'], ' '.join(miss)))
check('Every node reachable from the level entrance', not bad, '; '.join(bad)[:400])
sites_ok = [s for s in SITES if s in R6 and not any(e['loc_id'] == s and e['type'] == 'Shortcut' for e in ROWS['edges'])]
check('Every site ends in a shortcut to its entrance (plan 3.7)', not sites_ok, ' '.join(sites_ok))
nolore = [s for s in SITES if s in R6 and not any(x['loc_id'] == s and x['container'] in ('Lore pickup', 'Key') for x in ROWS['loot'])]
check('Every site has at least one lore item (plan 5.1)', not nolore, ' '.join(nolore))
nouniq = [s for s, v in SITES.items() if s in R6 and not any(x['loc_id'] == s and x['item_or_table'] == v['unique_reward'] for x in ROWS['loot'])]
check('Every site has its unique reward', not nouniq, ' '.join(nouniq))
cit_min = sum(int(z['path_min']) for z in ZONES)
check('Citadel first play 2-3 h (plan 3.7, 5.2)', 120 <= cit_min <= 180, '%d min' % cit_min)
miss_ids = set()
for t, cols in [('enc', ['enc_id', 'actors']), ('loot', ['item_or_table']), ('checkpoints', ['anchor_id'])]:
    for row in ROWS[t]:
        for c in cols:
            for tok in row[c].replace(';', ' ').split():
                if tok[:4] in ('ACT_', 'ITM_', 'LOC_', 'ENC_', 'RES_') and tok not in KNOWN and tok not in NEW_IDS:
                    miss_ids.add(tok)
check('Every referenced ID exists in data/ or design/world, or is requested here', not miss_ids, ' '.join(sorted(miss_ids)))
placed = {x['world_loc'] for x in ROWS['loot']}
unplaced = [k for k, v in R6.items() if v['kind'] in ('Small chest', 'Shard crate', 'Gather node') and k not in placed]
check('Every world chest, crate and gather node placed', not unplaced, ' '.join(unplaced[:20]))
lore_placed = {x['item_or_table'] for x in ROWS['loot']}
check('Every REG_06 lore item placed', all(li['item_id'] in lore_placed for li in LORE), ' '.join(li['item_id'] for li in LORE if li['item_id'] not in lore_placed))
wenc = [e for e, v in ENC.items() if v['region'] == REG]
used = {x['enc_id'] for x in ROWS['enc']}
check('Every world encounter in REG_06 placed', all(e in used for e in wenc), ' '.join(e for e in wenc if e not in used))
sec_used = {s['world_secret'] for s in ROWS['secrets']}
check('Every world secret placed', all(s['loc_id'] in sec_used for s in SECRETS))
check('Every boss arena Anchor within plan reach', all(int(ARENAS[b]['anchor_run_m']) <= (60 if ARENAS[b]['class_'] != 'Field' else 150) for b in ARENAS),
      ' '.join('%s %sm' % (b, ARENAS[b]['anchor_run_m']) for b in ARENAS))
long_str = [s['str_id'] for s in STRINGS if len(s['text']) > 140]
check('Strings within 140 chars', not long_str, ' '.join(long_str))
wr('checks.csv', CHECKS, ['check', 'result', 'detail'])
print('levels', len(ROWS['levels']), 'nodes', len(ROWS['nodes']), 'edges', len(ROWS['edges']), 'encounters', len(ROWS['enc']),
      'loot', len(ROWS['loot']), 'secrets', len(ROWS['secrets']), 'checkpoints', len(ROWS['checkpoints']), 'cues', len(ROWS['cues']), 'strings', len(STRINGS))
for c in CHECKS:
    print(c['result'], c['check'], c['detail'][:300])
