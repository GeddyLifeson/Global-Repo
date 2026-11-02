#!/usr/bin/env python3
"""Generate every Undervault level table, level sheet and map.

Owner: the Undervault levels thread. Inputs (read only): design/world/*.csv and data/.
Run: python3 design/levels/undervault/tools/gen_undervault.py
Every value not taken from the plan, world or data is a Shardfall design choice (3 Oct 2026).
"""
import csv, math, os, re, glob

GP = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
OUT = os.path.join(GP, 'design', 'levels', 'undervault')
W = os.path.join(GP, 'design', 'world')
D = os.path.join(GP, 'data')

def rd(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def wr(name, rows, cols=None):
    cols = cols or list(rows[0].keys())
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, '') for c in cols})

# ---------------------------------------------------------------- inputs
LOC = {r['loc_id']: r for r in rd(os.path.join(W, 'locations.csv'))}
WENC = {}
for r in rd(os.path.join(W, 'encounters.csv')):
    if r['layer'] == 'Undervault':
        WENC.setdefault(r['loc_id'], []).append(r)
WANC = {r['parent_loc']: r['loc_id'] for r in rd(os.path.join(W, 'anchors.csv')) if r['layer'] == 'Undervault' and not r['loc_id'].startswith('LOC_ANC_UV_')}  # skip anchors our own requests added

used = set()
for p in glob.glob(os.path.join(W, '*.csv')):
    used |= set(re.findall(r'ITM_[A-Z0-9_]+', open(p, encoding='utf-8').read()))

def items(fn, region, rar):
    return [r['item_id'] for r in rd(os.path.join(D, 'items', fn))
            if r['first_region'] == region and r['rarity'] in rar and r['item_id'] not in used]

ALL_IDS = set()
for p in glob.glob(os.path.join(D, '**', '*.csv'), recursive=True):
    for r in rd(p):
        k = list(r.values())[0] if r else ''
        if k and r.get('first_used_in') != 'assets/asset_hooks.csv': ALL_IDS.add(k)  # skip hooks only our own requests added

bosses = rd(os.path.join(D, 'actors', 'bosses.csv'))
def fit(cls, col):
    pts = [(float(b['Level']), float(b[col])) for b in bosses if b['Class'] == cls]
    n = len(pts); mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
    k = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)
    return lambda L: int(round((my + k * (L - mx)) / 10) * 10)
HP = {c: fit(c, 'HP (solo)') for c in ('Site', 'Citadel')}
EMB = {c: fit(c, 'Ember reward') for c in ('Site', 'Citadel')}

# ---------------------------------------------------------------- areas (design choices)
AREAS = {
 '02': dict(name='Cargo Vaults', above='Saltmere', lootreg='REG_04', elem='STM', elname='Storm',
            facs=['FAC_REMNANT', 'FAC_HOLLOWED'],
            mood='Flooded cargo holds under the salt flats; brine to the shin, salt crust on every rail, conveyors that still twitch',
            light='LGT_UND; vein cyan #3FC8C0 plus sodium emergency strobes #E89A3A on 4 s cycle; wet floors, fog 0.04',
            hazard='Brine pools carry Storm current when a conduit sparks: 25 Storm damage per s plus Shock buildup 20 per s; dry islands every 8-12 m',
            haz_vfx='VFX_UV_BRINE_ARC', haz_sfx='SFX_UV_BRINE_ARC',
            names=['Hold Nine', 'The Brine Grotto', 'Seam Gallery', 'Junction Station Ka', 'The Brood Silo', 'Reactor Cell Three'],
            pois=[('Brine Falls', 'Salt-water cascade off a split ballast tank', 'ITM_MAT_ESS_STM x2'),
                  ('The Drowned Foreman', 'Corpse in a flooded crane cab, still holding his manifest', 'ITM_LOR_UV_25'),
                  ('Conveyor Graveyard', 'Thirty stalled conveyors; ride the live ones', 'ITM_LT_SMALLCHEST_REG_04'),
                  ('Stuck Lift Car', 'Cargo car jammed 20 m up the shaft; climb the cables', 'ITM_MAT_HULL_03 x1')],
            lmk=('The Bulkhead Cliff', 90, 0.6, 'An engine bulkhead wall 90 m high streaked with lit veins; visible from every Cargo Vaults site')),
 '03': dict(name='Weave Caverns', above='Thornwood', lootreg='REG_05', elem='BLM', elname='Bloom',
            facs=['FAC_THORN', 'FAC_HOLLOWED'],
            mood='Redbark roots have burst through the engine hull; Weave threads hang in the air and spores drift like snow',
            light='LGT_UND; vein cyan #3FC8C0 shifting to Bloom green-gold #B6D86A from spore clusters; volumetric shafts through root gaps, fog 0.06',
            hazard='Spore clouds: standing inside 3 s applies Root (3 s); Ember damage or a torch burns a cloud off for 30 s',
            haz_vfx='VFX_UV_SPORE_CLOUD', haz_sfx='SFX_UV_SPORE_PUFF',
            names=['Root Hold', 'The Spore Grotto', 'Bloomvein Gallery', 'Junction Station Re', 'The Hollow Nest', 'Reactor Cell Seven'],
            pois=[('Spore Garden', 'A grown-over hydroponic deck, still producing', 'ITM_MAT_HRB_06 x4'),
                  ('Thorn Clan Dig Camp', 'Raiders mining roots for Weave sap', 'ITM_LT_SMALLCHEST_REG_05'),
                  ('Weave Lantern Shrine', 'Choir offerings at a root that hums', 'ITM_LOR_UV_26'),
                  ('Hanging Hauler', 'A six-seat hauler caught in roots 15 m up', 'ITM_MAT_PRT_09 x2')],
            lmk=('The Root Crown', 120, 0.8, 'Thornwood roots wrapped around a 120 m cooling tower, glowing green-gold at the top')),
 '05': dict(name='Frozen Sumps', above='Rimefall', lootreg='REG_06', elem='FRS', elname='Frost',
            facs=['FAC_HOLLOWED', 'FAC_REMNANT'],
            mood='Coolant sumps frozen solid; ice bridges over black water, breath fogs, vein light refracts blue through every wall',
            light='LGT_UND; vein cyan #3FC8C0 refracted to pale ice blue #A8D8F0 through ice; low white haze, fog 0.05, specular ice floors',
            hazard='Coolant geysers vent on a 9 s cycle (1.5 s warning hiss): 60 Frost damage and Slow 2 stacks inside 4 m; ice floors cut roll distance 20%',
            haz_vfx='VFX_UV_GEYSER', haz_sfx='SFX_UV_GEYSER_HISS',
            names=['Rimed Hold', 'The Ice Grotto', 'Frostvein Gallery', 'Junction Station Su', 'The Sleeper Nest', 'Reactor Cell Zero'],
            pois=[('Pods in the Ice', 'Twelve sleeper pods frozen in a sump wall; scanning them names the dead', 'ITM_LOR_UV_27'),
                  ('Geyser Field', 'Timed geysers around a coolant valve', 'ITM_MAT_ESS_FRS x3'),
                  ('Ice Mirror Hall', 'Polished ice reflects a hidden door', 'ITM_LT_VAULT_REG_06'),
                  ('Frostbitten Camp', 'Dead Salvagers around a cold stove', 'ITM_MAT_GLASS_02 x1')],
            lmk=('The Frozen Turbine', 70, 0.5, 'A 70 m drive turbine locked mid-turn in blue ice')),
}

# ---------------------------------------------------------------- site archetypes (design choices)
# role, room name, w x d x h (m), traversal into room, notes
ARCH = {
 'S01': dict(kind='Cargo bay', kit='KIT_UNDERVAULT', end='Site keeper elite', path=(15, 22),
   puzzle='Run the gantry crane: three switches lift a container into place as a bridge across the bay',
   secret=('Breakable floor', 'Drop a container with the crane onto the cracked plate', 'A dull boom under the bay floor; a drafty grate'),
   shortcut='Cargo lift from the manifest office back up to the loading dock',
   rooms=[('Entry', 'Loading dock', (20, 30, 8), 'Ramp from threshold', 'Anchor; first view of the bay through a torn door'),
          ('Traverse', 'Container stacks', (30, 40, 14), 'Climb 3 container tiers (1.2 m vaults)', 'Teaches vertical climbing'),
          ('Combat', 'Bay floor', (40, 60, 16), 'Drop 4 m from stacks', 'Main fight; containers as high cover every 12 m'),
          ('Loot', 'Quartermaster cage', (10, 12, 4), 'Side door, locked from inside until bay is cleared', 'Optional'),
          ('Puzzle', 'Gantry control cab', (16, 16, 6), 'Ladder 10 m', 'Crane puzzle'),
          ('Combat', 'Upper catwalks', (12, 50, 4), 'Container bridge (crane)', 'Gunline space; long sight 40-60 m'),
          ('Secret', 'Sealed container', (6, 12, 3), 'Hidden under the bay floor', 'Optional'),
          ('Traverse', 'Crane ride', (10, 40, 30), 'Ride the crane hook down 25 m', 'Set piece; no combat'),
          ('End', 'Manifest office', (14, 14, 5), 'Pressure door', 'Elite fight then unique reward and lore')]),
 'S02': dict(kind='Weave grotto', kit='KIT_CAVE', end='Unique reward and lore', path=(12, 18),
   puzzle='Light the Shard-lamps: four lamps on the walls; each lit lamp makes one Weave thread bridge solid',
   secret=('Illusory wall', 'Hit the wall behind the third lamp', 'Hit the wall; cracked rock and a draft of Shard light'),
   shortcut='Kick-down ladder from the heart-pool ledge to the grotto mouth',
   rooms=[('Entry', 'Grotto mouth', (14, 18, 8), 'Narrow crawl 2.4 m', 'Anchor at entrance'),
          ('Traverse', 'Thread bridge', (6, 30, 20), 'Walk a Weave thread 30 m over a 20 m drop', 'Falls are lethal; checkpoint at bridge start'),
          ('Combat', 'Pool chamber', (30, 30, 12), 'Thread bridge exit', 'Ambush from pool edges'),
          ('Loot', 'Root alcove', (8, 10, 4), 'Side squeeze', 'Optional'),
          ('Puzzle', 'Lamp gallery', (24, 24, 14), 'Climb 6 m', 'Shard-lamp puzzle'),
          ('Combat', 'Hanging gallery', (12, 40, 18), 'Lit thread bridges', 'Fight on 4 m wide ledges'),
          ('Secret', 'Echo pocket', (6, 8, 4), 'Illusory wall', 'Optional'),
          ('Traverse', 'Waterfall drop', (8, 8, 22), 'Slide and drop 18 m into a pool (no fall damage)', 'One-way'),
          ('End', 'Heart-pool', (20, 20, 10), 'Swim 12 m', 'Unique reward and lore on an altar')]),
 'S03': dict(kind='Shard vein gallery', kit='KIT_MINE', end='Site keeper elite', path=(16, 24),
   puzzle='Restart the hoist: carry two charged cells (slow walk, no roll) to the hoist house',
   secret=('Breakable wall', 'Heavy attack, Shrapnel or Launcher on the shored-up drift', 'Rotten timbers and loose glowing ore'),
   shortcut='Mine cart rail from the mother vein back to the survey adit',
   rooms=[('Entry', 'Survey adit', (8, 30, 5), 'Adit door', 'Anchor at entrance'),
          ('Traverse', 'Cart line', (6, 80, 6), 'Ride an ore cart 80 m, duck under 3 beams', 'Set piece'),
          ('Combat', 'Vein face', (35, 40, 14), 'Cart stop', 'Horde fight; ore pillars as cover'),
          ('Loot', 'Assay room', (10, 10, 4), 'Side door', 'Optional; 2 gather nodes'),
          ('Puzzle', 'Hoist house', (16, 20, 18), 'Stairs 12 m', 'Hoist puzzle'),
          ('Combat', 'Deep stope', (20, 50, 30), 'Hoist cage ride down 25 m', 'Vertical fight on three ledges'),
          ('Secret', 'Collapsed drift', (6, 20, 4), 'Breakable wall', 'Optional'),
          ('Traverse', 'Vein chasm', (12, 40, 40), 'Ledge shimmy and two 3 m jumps', 'Lit by the vein itself'),
          ('End', 'Mother vein', (24, 24, 16), 'Chasm floor', 'Elite fight; 4 gather nodes')]),
 'S04': dict(kind='Collapsed tram station', kit='KIT_UNDERVAULT', end='Spine Tunnel connection', path=(14, 20),
   puzzle='Route power between three panels to re-couple a tram car as a bridge over the collapsed platform',
   secret=('Hidden hatch', 'Drop into the maintenance pit under platform B', 'A missing floor grate and a cold draft'),
   shortcut='Pressure door from the tunnel mouth back to the concourse, cycled from inside',
   rooms=[('Entry', 'Concourse', (30, 40, 10), 'Stairs from the cavern', 'Anchor at entrance'),
          ('Traverse', 'Ticket hall', (20, 24, 8), 'Climb over a fallen ceiling', 'Signage teaches tram routes'),
          ('Combat', 'Platform A', (12, 80, 8), 'Hall exit', 'Long fight; tram cars as cover'),
          ('Loot', 'Lost luggage', (10, 12, 4), 'Side room', 'Optional'),
          ('Puzzle', 'Signal box', (10, 10, 6), 'Ladder 6 m', 'Power routing puzzle'),
          ('Combat', 'Platform B wreck', (12, 80, 8), 'Re-coupled car bridge', 'Gunline fight'),
          ('Secret', 'Maintenance pit', (6, 30, 3), 'Hidden hatch', 'Optional'),
          ('Traverse', 'Derailed car crawl', (4, 30, 3), 'Crawl through a tipped car 2.4 m', 'Non-combat squeeze'),
          ('End', 'Tunnel mouth', (14, 30, 10), 'Car exit', 'Tram platform; joins the Spine Tunnel')]),
 'S05': dict(kind='Crawler nest', kit='KIT_CAVE', end='Site keeper elite', path=(14, 20),
   puzzle='Burn the resin walls: carry a lit vent torch (or any Ember damage) to melt three resin seals',
   secret=('Hidden ledge', 'Climb the husk pile to a ledge above the hatchery', 'Claw marks going up the wall'),
   shortcut='Rope drop from the nest heart lip back to the chitin breach',
   rooms=[('Entry', 'Chitin breach', (12, 16, 6), 'Hull breach', 'Anchor; crawler sounds start'),
          ('Traverse', 'Egg tunnels', (4, 60, 3), 'Crouch tunnels 2.4 m', 'Non-combat; eggs hatch on noise'),
          ('Combat', 'Brood hall', (30, 30, 10), 'Tunnel exit', 'Ambush from ceiling holes'),
          ('Loot', 'Husk pile', (10, 10, 6), 'Side cave', 'Optional'),
          ('Puzzle', 'Resin walls', (20, 20, 8), 'Resin-sealed passage', 'Resin puzzle'),
          ('Combat', 'Hatchery', (30, 36, 12), 'Melted seal', 'Crawler pack plus faction squad'),
          ('Secret', 'Old crawl', (6, 14, 4), 'Hidden ledge', 'Optional'),
          ('Traverse', 'Drop shaft', (8, 8, 26), 'Drop 3 x 6 m onto resin pads', 'One-way'),
          ('End', 'Nest heart', (32, 32, 14), 'Shaft floor', 'Crawler alpha elite then reward')]),
 'S06': dict(kind='Sealed reactor cell', kit='KIT_REACTOR', end='Area boss', path=(20, 28),
   puzzle='Coolant valves in order: four valves, the order is painted on the reactor log in the control deck',
   secret=('Shielded vault', 'Open the vault with the shield charge from the control deck before the boss', 'A lead-lined door with a dead charge socket'),
   shortcut='Service lift from the spent core room back to the containment airlock',
   rooms=[('Entry', 'Containment airlock', (12, 16, 6), 'Airlock cycle 6 s (hides load)', 'Anchor at entrance'),
          ('Traverse', 'Coolant gallery', (10, 70, 12), 'Pipe walk 1.5 m wide, hazard below', 'Area hazard lesson'),
          ('Combat', 'Turbine hall', (40, 50, 20), 'Gallery exit', 'Fort fight; turbines as cover'),
          ('Loot', 'Tool crib', (10, 10, 4), 'Side door', 'Optional'),
          ('Puzzle', 'Valve station', (20, 20, 10), 'Stair 8 m', 'Valve puzzle'),
          ('Combat', 'Control deck', (24, 30, 6), 'Valve-opened door', 'Last fight before the boss'),
          ('Secret', 'Shielded vault', (8, 8, 4), 'Shield charge door', 'Optional'),
          ('Anchor', 'Pre-cell lock', (10, 12, 6), 'Lock door', 'Anchor 40 m from the fog gate'),
          ('Boss', 'Reactor cell', (36, 36, 18), 'Fog gate 4 m', 'Area boss arena'),
          ('End', 'Spent core room', (14, 14, 8), 'Opens after the boss', 'Unique reward and lore')]),
}
SITE_ORDER = ['S01', 'S02', 'S03', 'S04', 'S05', 'S06']

UV_BOSSES = {
 '02': dict(id='ACT_BOSS_UV_STEVEDORE', name='The Stevedore', cls='Site', level=42, fac='FAC_REMNANT', arch='Loader frame (Remnant), 6 m',
            elem='Iron', weak='Storm', phases=2, thr='60', diam=36, shape='Square cargo cell with 4 container stacks (high cover) that it can throw',
            hazards='Brine floor arcs (Storm) when it slams a conduit; containers break after 2 throws',
            p1='Grab-and-throw containers, shoulder charge 20 m, stomp 6 m',
            p2='At 60%: tears off its cage; magnetic pull 12 m into a crush combo; floor arcs every 10 s',
            mus='MUS_BOSS_UV_STEVEDORE', tells='Red work lights on its arms 0.8 s before a throw'),
 '03': dict(id='ACT_BOSS_UV_ROOTWRIGHT', name='The Rootwright', cls='Site', level=56, fac='FAC_THORN', arch='Thorn Clan engineer fused with redbark, 3.5 m',
            elem='Bloom', weak='Ember', phases=2, thr='55', diam=38, shape='Round turbine pit with 6 root pillars; pillars regrow 20 s after cut',
            hazards='Spore clouds from cut roots (Root 3 s); Ember burns them',
            p1='Hook-axe combos, root snare line 15 m, summons 2 Thorn fodder at 80%',
            p2='At 55%: merges with the roots; arena-wide root eruptions from 3 tells at a time, heals 1% per s while touching a pillar',
            mus='MUS_BOSS_UV_ROOTWRIGHT', tells='Green sap glow on the roots it will erupt 1.0 s before'),
 '05': dict(id='ACT_BOSS_UV_SUMPMOTHER', name='The Sump Mother', cls='Site', level=70, fac='Creature', arch='Undervault Crawler queen, 8 m long',
            elem='Frost', weak='Ember', phases=2, thr='50', diam=40, shape='Frozen sump disc over black water; ice breaks in 4 marked sections',
            hazards='Coolant geysers on 9 s cycle; broken ice sections drop to water (lethal) for 20 s then refreeze',
            p1='Burrows under ice and erupts on the player, tail sweep 270 deg, egg spit spawns 3 crawlers',
            p2='At 50%: shatters 2 ice sections; frost breath line 25 m; calls 1 Undervault Crawler every 30 s (max 2)',
            mus='MUS_BOSS_UV_SUMPMOTHER', tells='Ice cracks and bubbles 1.2 s before an eruption'),
 'CORE': dict(id='ACT_BOSS_UV_GOVERNOR', name='The Governor', cls='Citadel', level=46, fac='FAC_REMNANT', arch="The engine block's safety intelligence in a core-tending frame, 7 m",
            elem='Iron', weak='Storm', phases=3, thr='70 35', diam=50, shape='Round core housing ring around the cracked core; 3 coolant pillars as LOS breaks',
            hazards='Core flare every 25 s from phase 2: stand behind a pillar or take 300 Iron damage',
            p1='Arm sweeps, tracking welding beam 30 m, deploys 2 Scrap Drones',
            p2="At 70%: Ostra's voice is locked out; core flares begin; it seals one pillar with a shutter every 40 s",
            p3='At 35%: overload; moves faster, beam splits in 3, floor plates electrify in a rotating quarter (Storm, Shock)',
            mus='MUS_BOSS_UV_GOVERNOR', tells='Core light goes white 1.5 s before a flare; plates hum 1.0 s before they electrify'),
}

TIME_S = {'Entry': 30, 'Traverse': 90, 'Combat': 180, 'Loot': 45, 'Puzzle': 180, 'Secret': 75, 'End': 180, 'Anchor': 15, 'Boss': 420,
          'Lift': 60, 'Transit': 120, 'POI': 180, 'Story': 300}
OPTIONAL = {'Loot', 'Secret', 'POI'}

def mat_tier(L):
    if L < 44: return 'ITM_MAT_HULL_03', 'ITM_MAT_DUST_02'
    if L < 56: return 'ITM_MAT_DUST_02', 'ITM_MAT_GLASS_01'
    if L < 65: return 'ITM_MAT_GLASS_02', 'ITM_MAT_DUST_03'
    return 'ITM_MAT_GLASS_02', 'ITM_MAT_STAR_01'

THROW = {'STM': 'ITM_CON_THR_STORM', 'BLM': 'ITM_CON_THR_SEED', 'FRS': 'ITM_CON_THR_FROST'}

# ---------------------------------------------------------------- build
levels, rooms, edges, encs, loot, secrets, anchors, cues, pois, bossrows, reqs = [], [], [], [], [], [], [], [], [], [], []
new_hooks = set()
lore_n = [0]
enc_n = [0]

def lore():
    lore_n[0] += 1
    return 'ITM_LOR_UV_%02d' % lore_n[0]

def new_enc(level_id, room_id, x, y, template, fac, lvl, actors, cover, fallback, respawn='On Anchor rest', note=''):
    enc_n[0] += 1
    eid = 'ENC_UV_%03d' % enc_n[0]
    encs.append(dict(enc_id=eid, source='new', level_id=level_id, room_id=room_id, x_m=x, y_m=y, template=template, faction=fac,
                     level=lvl, actors=actors, total=sum(int(a.split(' x')[1]) for a in actors.split('; ')), cover_points=cover,
                     fallback_points=fallback, respawn=respawn, note=note))
    return eid

def fac_set(fac, role_set, n=1):
    f = fac.replace('FAC_', '')
    sets = {'ambush': 'ACT_%s_SKIRMISHER x3; ACT_%s_ARTILLERY x1',
            'patrol': 'ACT_%s_FODDER x3; ACT_%s_SHIELDBEARER x1',
            'elite': 'ACT_%s_HEAVY x1; ACT_%s_LEADER x1; ACT_%s_FODDER x2',
            'pair': 'ACT_%s_SHIELDBEARER x1; ACT_%s_SKIRMISHER x2'}
    s = sets[role_set]
    return s.replace('%s', f)

def room_cues(role, area, kind=''):
    a = AREAS.get(area, {})
    mus = {'Combat': 'MUS_UND_COMBAT_L2', 'Boss': '', 'Secret': 'MUS_UND_DISCOVERY', 'End': 'MUS_UND_COMBAT_END',
           'Puzzle': 'MUS_UND_TENSION', 'Traverse': 'MUS_UND_EXPLORE_DAY'}.get(role, 'MUS_UND_EXPLORE_DAY')
    amb = {'Entry': 'AMB_UND_INTERIOR', 'Combat': 'AMB_UND_EMITTERS', 'Traverse': 'AMB_UND_EMITTERS'}.get(role, 'AMB_UND_INTERIOR')
    sfx = {'Entry': 'SFX_UV_ANCHOR_HUM', 'Traverse': a.get('haz_sfx', 'SFX_UV_MACHINE_GROAN'), 'Combat': 'SFX_UV_ALARM_KLAXON',
           'Loot': 'SFX_UV_CRATE_OPEN', 'Puzzle': 'SFX_UV_MECH_ENGAGE', 'Secret': 'SFX_UV_SECRET_REVEAL', 'End': 'SFX_UV_REWARD_CHIME',
           'Anchor': 'SFX_UV_ANCHOR_HUM', 'Boss': 'SFX_UV_FOGGATE', 'Lift': 'SFX_UV_LIFT_RIDE', 'Transit': 'SFX_UV_TRAM_RUN',
           'POI': 'SFX_UV_MACHINE_GROAN', 'Story': 'SFX_UV_CORE_PULSE'}[role]
    vfx = {'Entry': 'VFX_UV_ANCHOR_LIGHT', 'Traverse': a.get('haz_vfx', 'VFX_UV_DUST_FALL'), 'Combat': 'VFX_UV_VEIN_PULSE',
           'Loot': 'VFX_UV_LOOT_GLINT', 'Puzzle': 'VFX_UV_PUZZLE_SOLVED', 'Secret': 'VFX_UV_ILLUSION_BREAK', 'End': 'VFX_UV_REWARD_BEAM',
           'Anchor': 'VFX_UV_ANCHOR_LIGHT', 'Boss': 'VFX_UV_FOGGATE', 'Lift': 'VFX_UV_DUST_FALL', 'Transit': 'VFX_UV_TRAM_SPARKS',
           'POI': 'VFX_UV_VEIN_PULSE', 'Story': 'VFX_UV_CORE_GLOW'}[role]
    new_hooks.update([sfx, vfx])
    light = {'Entry': 'Anchor amber #E8A23A 2,000 lm key over vein cyan fill', 'Combat': 'Vein cyan fill; 2-3 work lamps 1,500 lm for readable silhouettes',
             'Secret': 'Dark (0.5 lux) until opened, then a vein bloom', 'Boss': 'Arena rim light 3,000 lm plus boss emissive tells',
             'End': 'Reward pedestal spot 1,200 lm, cyan', 'Loot': 'Single hanging lamp 600 lm'}.get(role, 'Vein cyan only, player torch 8 m radius')
    return mus, amb, sfx, vfx, light

def add_room(level_id, rid, role, name, size, trav, notes, x, y, z, area, crit, enc='', lootids='', anchor='', extra=None):
    mus, amb, sfx, vfx, light = room_cues(role, area)
    if extra: mus = extra.get('mus', mus); sfx = extra.get('sfx', sfx); vfx = extra.get('vfx', vfx); light = extra.get('light', light)
    t = TIME_S[role]
    rooms.append(dict(room_id=rid, level_id=level_id, role=role, name=name, w_m=size[0], d_m=size[1], h_m=size[2],
                      x_m=round(x), y_m=round(y), z_m=round(z), grid_10m='%d,%d,%d' % (round(x) // 10, round(y) // 10, round(z) // 10),
                      critical_path='Yes' if crit else 'No', traversal_in=trav, encounters=enc, loot=lootids, anchor=anchor,
                      light=light, music=mus, ambience=amb, sfx=sfx, vfx=vfx, time_s=t, notes=notes))

def edge(level_id, a, b, kind, length, gate='', one_way='No'):
    edges.append(dict(level_id=level_id, from_room=a, to_room=b, type=kind, length_m=length, one_way=one_way, gate=gate))

def lt(item, qty, container, room, level_id, note=''):
    loot.append(dict(level_id=level_id, room_id=room, container=container, item=item, qty=qty,
                     status='exists' if item.split(' ')[0] in ALL_IDS else 'requested', note=note))

anc_n = [0]
def new_anchor(level_id, room, x, y, z, why):
    anc_n[0] += 1
    aid = 'LOC_ANC_UV_%02d' % anc_n[0]
    anchors.append(dict(anchor_id=aid, source='new', level_id=level_id, room_id=room, x_m=round(x), y_m=round(y), z_m=round(z), reason=why, fast_travel='Yes once lit'))
    return aid

sec_n = [0]
def add_secret(level_id, room, typ, hint, req, reward, area):
    sec_n[0] += 1
    sid = 'LOC_SEC_UV_%02d' % sec_n[0]
    secrets.append(dict(secret_id=sid, level_id=level_id, room_id=room, secret_type=typ, hint=hint, requirement=req, reward=reward, area=area))
    return sid

lv_meta = {}
def add_level(level_id, loc_id, name, area, kind, kit, level, critical, mood, light, notes, gate=''):
    lv_meta[level_id] = dict(level_id=level_id, loc_id=loc_id, name=name, area=AREAS[area]['name'] if area in AREAS else area,
                             kind=kind, kit=kit, level=level, critical_path=critical, mood=mood, lighting=light, gate=gate, notes=notes)
    levels.append(lv_meta[level_id])

# pick unique rewards per area
uniq = {}
for ak, a in AREAS.items():
    rr = {'REG_04': ['Rare'], 'REG_05': ['Rare', 'Relic'], 'REG_06': ['Relic']}[a['lootreg']]
    lists = [items('weapons_melee.csv', a['lootreg'], rr), items('weapons_firearm.csv', a['lootreg'], rr),
             items('armor_pieces.csv', a['lootreg'], rr), items('weapon_arts.csv', a['lootreg'], rr + ['Forged', 'Common'])]
    pool = [x for grp in zip(*[l + [None] * 9 for l in lists]) for x in grp if x]
    uniq[ak] = pool

def ring(cx, cy, n, r, i, rot=0.0):
    ang = rot + 2 * math.pi * i / n
    return cx + r * math.cos(ang), cy + r * math.sin(ang)

# ---- descents (entries)
DESC = {
 '02': ('Drowned Cargo Lift', 'Ride a cargo lift 106 m down a flooded shaft (lift 53 s at 2 m/s; hides streaming)', 'Lift'),
 '03': ('Root Shaft', 'Climb down a 323 m root-choked shaft: root ladders, two rope anchors, ledge jumps of 3 m', 'Traverse'),
 '05': ('Rime Well', 'Maintenance elevator 774 m through the drive section (77 s at 10 m/s; hides streaming), then an ice stair', 'Lift'),
}
for ak in ['02', '03', '05']:
    a = AREAS[ak]; eloc = LOC['LOC_UV_ENTRY_%s' % ak]; s1 = LOC['LOC_UV_REG_%s_S01' % ak]
    lid = 'LV_UV_%s_ENTRY' % ak
    zs, ze = float(eloc['z_m']), float(s1['z_m'])
    lvl = int(s1['level'])
    add_level(lid, eloc['loc_id'], eloc['name'].split(' (')[0], ak, 'Descent', 'KIT_UNDERVAULT', lvl, 'Yes',
              'Surface light dies away; the first Shard veins appear 40 m down', 'Surface TOD at the mouth, LGT_UND below the lower gate',
              'Optional region entry; level jump warning popup at the mouth')
    ex, ey = float(eloc['x_m']), float(eloc['y_m'])
    pts = [(ex, ey, zs), (ex, ey, zs - 10), (ex + 20, ey + 10, (zs + ze) / 2), (ex + 40, ey + 20, ze + 15), (ex + 60, ey + 30, ze)]
    nm, how, r2 = DESC[ak]
    spec = [('Entry', nm + ' mouth', (16, 16, 8), 'Surface', 'Surface Anchor within 60 m (world); warning sign: level %d+ below' % lvl),
            (r2, 'The descent', (8, 8, int(zs - ze)), how, 'No combat during the ride'),
            ('Combat', 'Mid landing', (20, 24, 8), 'Lift stop or ledge', 'First Undervault fight'),
            ('Traverse', 'Lower gate', (10, 20, 8), 'Gate wheel (hold Interact 2 s)', 'Light changes to LGT_UND; music to MUS_UND_EXPLORE_DAY'),
            ('Entry', 'Threshold', (20, 20, 10), 'Walk', 'Leads to %s (%s)' % (a['names'][0], s1['loc_id']))]
    prev = None
    for i, (role, n, sz, tr, nt) in enumerate(spec):
        rid = '%s_R%02d' % (lid, i + 1)
        x, y, z = pts[i]
        e = ''
        if role == 'Combat':
            e = new_enc(lid, rid, x, y, 'ENT_AMBUSH', a['facs'][0], lvl - 2, fac_set(a['facs'][0], 'patrol'), 3, 1)
        lids = ''
        if i == 2:
            lt(THROW[a['elem']], 2, 'Corpse', rid, lid); lids = THROW[a['elem']] + ' x2'
        add_room(lid, rid, role, n, sz, tr, nt, x, y, z, ak, True, e, lids, extra={'mus': 'MUS_UND_TENSION'} if i == 1 else None)
        if prev: edge(lid, prev, rid, {'Lift': 'Lift', 'Traverse': 'Climb'}.get(spec[i - 1][0], 'Walk') if i == 2 else 'Walk',
                      int(math.dist(pts[i - 1], pts[i])))
        prev = rid
    edge(lid, prev, 'LV_UV_%s_S01_R01' % ak, 'Walk', 40)

# ---- sites
for ak, a in AREAS.items():
    upool = list(uniq[ak])
    for si, sk in enumerate(SITE_ORDER):
        loc = LOC['LOC_UV_REG_%s_%s' % (ak, sk)]
        ar = ARCH[sk]; lvl = int(loc['level'])
        lid = 'LV_UV_%s_%s' % (ak, sk)
        add_level(lid, loc['loc_id'], a['names'][si], ak, ar['kind'], ar['kit'], lvl, 'No',
                  a['mood'], a['light'], 'Hazard: ' + a['hazard'], gate='Core Hatch to the Engine Heart (MQ_A2_06)' if (ak == '02' and sk == 'S06') else '')
        cx, cy, cz = float(loc['x_m']), float(loc['y_m']), float(loc['z_m'])
        n = len(ar['rooms']); R = 70 + 5 * n
        wenc = WENC.get(loc['loc_id'], [])
        combat_i = 0; prev = None; first = None; crit_ids = []
        for i, (role, nm, sz, tr, nt) in enumerate(ar['rooms']):
            rid = '%s_R%02d' % (lid, i + 1)
            x, y = ring(cx, cy, n, R, i, rot=si * 0.7)
            z = cz - (25.0 * i / (n - 1))
            crit = role not in OPTIONAL
            e, lids, anc = '', [], ''
            if role == 'Entry':
                anc = WANC.get(loc['loc_id']) or new_anchor(lid, rid, x, y, z, 'Plan 3.7: an Anchor at every site entrance')
            if role == 'Anchor':
                anc = new_anchor(lid, rid, x, y, z, 'MET_FOGGATE: Anchor 25-60 m from a boss fog gate')
            if role == 'Combat':
                if combat_i < len(wenc):
                    w = wenc[combat_i]; e = w['enc_id']
                    encs.append(dict(enc_id=e, source='world', level_id=lid, room_id=rid, x_m=round(x), y_m=round(y), template=w['template'],
                                     faction=w['faction'], level=w['level'], actors=w['actors'],
                                     total=sum(int(t.split(' x')[1]) for t in w['actors'].split('; ')), cover_points=w['cover_points'],
                                     fallback_points=w['fallback_points'], respawn=w['respawn'], note='Placed by world; room chosen here'))
                else:
                    e = new_enc(lid, rid, x, y, 'ENT_AMBUSH', a['facs'][1], lvl, fac_set(a['facs'][1], 'ambush'), 3, 1)
                combat_i += 1
            if role == 'Traverse' and i > 1:
                e = new_enc(lid, rid, x, y, 'ENT_AMBUSH', a['facs'][1], lvl, fac_set(a['facs'][1], 'pair'), 2, 1, note='Small ambush on the traversal')
            if role == 'End' and ar['end'] == 'Site keeper elite':
                if sk == 'S05':
                    e = new_enc(lid, rid, x, y, 'ENT_CRT_SOLO', 'Creature', lvl + 1, 'ACT_CRT_UNDERVAULTCRAWLER x1; ACT_CRT_SHARDRATSWARM x2', 0, 0,
                                'Heavy stays dead', 'Crawler alpha: x1.5 HP elite of ACT_CRT_UNDERVAULTCRAWLER')
                else:
                    e = new_enc(lid, rid, x, y, 'ENT_ELITE', a['facs'][0], lvl + 1, fac_set(a['facs'][0], 'elite'), 2, 1, 'Heavy stays dead', 'Site keeper elite')
            if role == 'Boss':
                b = UV_BOSSES[ak]
                e = new_enc(lid, rid, x, y, 'BOSS', b['fac'], b['level'], '%s x1' % b['id'], 3, 0, 'Never', 'Area boss')
            m1, m2 = mat_tier(lvl)
            if role == 'Loot':
                lt('ITM_LT_SMALLCHEST_%s' % a['lootreg'], 1, 'Chest', rid, lid); lt(m1, 2, 'Chest', rid, lid)
                lids = ['ITM_LT_SMALLCHEST_%s' % a['lootreg'], m1 + ' x2']
            if role == 'Combat' and combat_i == 1:
                lt(THROW[a['elem']], 2, 'Corpse', rid, lid); lids = [THROW[a['elem']] + ' x2']
            if role == 'Combat' and combat_i == 2:
                lt('ITM_MAT_ESS_%s' % a['elem'], 2, 'Corpse', rid, lid); lids = ['ITM_MAT_ESS_%s x2' % a['elem']]
            if role == 'Traverse' and i > 1:
                lt('ITM_LT_SHARDCRATE_%s' % a['lootreg'], 1, 'Shard crate', rid, lid); lids = ['ITM_LT_SHARDCRATE_%s' % a['lootreg']]
            if role == 'Secret':
                typ, req, hint = ar['secret']
                rw = 'ITM_LT_VAULT_%s' % a['lootreg']
                if sk in ('S03', 'S06'): rw += '; ITM_MAT_INF_%s x1' % a['elem']
                add_secret(lid, rid, typ, hint, req, rw, ak)
                for it in rw.split('; '):
                    lt(it.split(' x')[0], it.split(' x')[1] if ' x' in it else 1, 'Secret cache', rid, lid)
                lids = [rw]
            if role == 'End':
                u = upool.pop(0) if upool else 'ITM_LT_GEAR_%s' % a['lootreg']
                lo = lore()
                lt(u, 1, 'Unique reward pedestal', rid, lid, 'Site rule: unique reward'); lt(lo, 1, 'Lore', rid, lid, 'Engine block log')
                lt(m2, 1, 'Pedestal', rid, lid)
                lids = [u, lo, m2]
                if sk == 'S03':
                    lt(m1, 4, 'Gather nodes (respawn on rest)', rid, lid); lids.append(m1 + ' x4 nodes')
            if role == 'Boss':
                b = UV_BOSSES[ak]
                for it in ('ITM_MAT_SPC_ASCENDANT', 'ITM_LT_GEAR_%s' % a['lootreg'], 'ITM_LT_BOSS_UV_%s' % ak):
                    lt(it, 1, 'Boss drop', rid, lid)
                lids = ['ITM_MAT_SPC_ASCENDANT', 'ITM_LT_GEAR_%s' % a['lootreg'], 'ITM_LT_BOSS_UV_%s' % ak]
            extra = None
            if role == 'Boss':
                extra = {'mus': UV_BOSSES[ak]['mus']}; new_hooks.add(UV_BOSSES[ak]['mus'])
            if role == 'Puzzle':
                nt = nt + ': ' + ar['puzzle']
            add_room(lid, rid, role, nm, sz, tr, nt, x, y, z, ak, crit, e, '; '.join(lids), anc, extra)
            if crit:
                if crit_ids:
                    one = 'Yes' if 'drop' in tr.lower() or 'slide' in tr.lower() else 'No'
                    gate = 'Puzzle solved' if 'bridge' in tr.lower() or 'opened' in tr.lower() or 'melted' in tr.lower() or 'coupled' in tr.lower() else ''
                    if role == 'Boss': gate = 'Fog gate'
                    if ar['rooms'][i - 1][0] == 'Boss' or (role == 'End' and sk == 'S06'): gate = 'Boss defeated'
                    edge(lid, crit_ids[-1], rid, tr.split(' (')[0][:40], int(math.dist((x, y), prev_xy)), gate, one)
                crit_ids.append(rid); prev_xy = (x, y)
            else:
                hub = crit_ids[-1]
                edge(lid, hub, rid, tr.split(' (')[0][:40], 15, 'Hidden' if role == 'Secret' else '')
        edge(lid, crit_ids[-1], crit_ids[0], 'Shortcut: ' + ar['shortcut'], int(R * 0.6), 'Opens from the far side', 'Yes')
        if sk == 'S04':
            tun = 'LV_UV_TUN_0203' if ak == '03' else ('LV_UV_TUN_0205' if ak == '05' else 'LV_UV_TUN_0203 and LV_UV_TUN_0205')
            edge(lid, crit_ids[-1], tun, 'Tram platform', 0)
        if si < 5:
            edge(lid, crit_ids[-1], 'LV_UV_%s_%s_R01' % (ak, SITE_ORDER[si + 1]), 'Cavern path', int(math.dist((cx, cy), (float(LOC['LOC_UV_REG_%s_%s' % (ak, SITE_ORDER[si + 1])]['x_m']), float(LOC['LOC_UV_REG_%s_%s' % (ak, SITE_ORDER[si + 1])]['y_m'])))))

# ---- Spine Tunnels
TUN = {'0203': ('Spine Tunnel East', '02', '03'), '0205': ('Spine Tunnel West', '02', '05')}
for tk, (tn, fa, ta) in TUN.items():
    loc = LOC['LOC_UV_TUNNEL_%s' % tk]
    lid = 'LV_UV_TUN_%s' % tk
    A0 = LOC['LOC_UV_REG_%s_S04' % fa]; A1 = LOC['LOC_UV_REG_%s_S04' % ta]
    add_level(lid, loc['loc_id'], tn, fa, 'Tram tunnel', 'KIT_UNDERVAULT', int(loc['level']), 'No',
              'A 2 km straight cargo tram line; trams pass every 90 s; the dark between stations is total',
              'LGT_UND; tram headlamps 4,000 lm moving; platform sodium lamps #E89A3A every 250 m', 'TRV_TRAM 12 m/s; tram cars are moving platforms')
    lv_meta[lid]['area'] = 'Spine Tunnels'
    spec = [('Entry', 'Station platform (%s)' % AREAS[fa]['names'][3], 'Joins %s' % A0['loc_id']),
            ('Transit', 'Tram yard', 'Board a tram car (moving platform)'),
            ('Loot', 'Maintenance alcove', 'Step off between trams'),
            ('Traverse', 'Collapsed segment', 'Tram stops; walk a 1.5 m ledge 120 m over a pit'),
            ('Anchor', 'Midline platform', 'Gunline fight, then Anchor'),
            ('Secret', 'Signal tower', 'Climb the dead signal mast'),
            ('Traverse', 'Hazard cut', AREAS[ta]['hazard'].split(':')[0] + ' section 200 m'),
            ('Combat', 'Ambush siding', 'A stalled tram used as a barricade'),
            ('Entry', 'Station platform (%s)' % AREAS[ta]['names'][3], 'Joins %s' % A1['loc_id'])]
    prev = None
    for i, (role, nm, nt) in enumerate(spec):
        rid = '%s_R%02d' % (lid, i + 1)
        t = i / 8.0
        x = float(A0['x_m']) + t * (float(A1['x_m']) - float(A0['x_m'])); y = float(A0['y_m']) + t * (float(A1['y_m']) - float(A0['y_m']))
        z = float(loc['z_m'])
        e, lids, anc = '', [], ''
        lvl = int(loc['level'])
        if role == 'Anchor':
            w = WENC.get(loc['loc_id'], [])[0]
            e = w['enc_id']; anc = WANC.get(loc['loc_id'], '')
            encs.append(dict(enc_id=e, source='world', level_id=lid, room_id=rid, x_m=round(x), y_m=round(y), template=w['template'], faction=w['faction'],
                             level=w['level'], actors=w['actors'], total=sum(int(q.split(' x')[1]) for q in w['actors'].split('; ')),
                             cover_points=w['cover_points'], fallback_points=w['fallback_points'], respawn=w['respawn'], note='Placed by world'))
        if role == 'Combat':
            e = new_enc(lid, rid, x, y, 'ENT_FORT', AREAS[ta]['facs'][0], lvl, fac_set(AREAS[ta]['facs'][0], 'elite'), 6, 2)
        if role == 'Loot':
            lt('ITM_LT_SMALLCHEST_REG_04', 1, 'Chest', rid, lid); lt('ITM_MAT_PRT_10', 2, 'Crate', rid, lid)
            lids = ['ITM_LT_SMALLCHEST_REG_04']
        if role == 'Secret':
            add_secret(lid, rid, 'Climb', 'A lit window at the top of a dead signal mast', 'Climb the mast cables (no tram running)', 'ITM_LT_VAULT_REG_05', 'Tunnels')
            lt('ITM_LT_VAULT_REG_05', 1, 'Secret cache', rid, lid); lids = ['ITM_LT_VAULT_REG_05']
        if role == 'Traverse' and i == 6:
            lt('ITM_LT_SHARDCRATE_REG_05', 1, 'Shard crate', rid, lid); lids = ['ITM_LT_SHARDCRATE_REG_05']
        add_room(lid, rid, role, nm, (12, 250, 9), 'Tram' if role == 'Transit' else 'Walk', nt, x, y, z, ta, role not in OPTIONAL, e, '; '.join(lids), anc)
        if prev: edge(lid, prev, rid, 'Tram or walk', 250)
        prev = rid

# ---- Engine Heart (core housing, MQ_A2_06)
c6 = LOC['LOC_UV_REG_02_S06']
lid = 'LV_UV_CORE'
add_level(lid, 'LOC_UV_CORE', 'The Engine Heart', '02', 'Core housing (main quest)', 'KIT_REACTOR', 46, 'Yes (MQ_A2_06)',
          'The cracked core of the Meridian; 400 sleepers still in their pods; the air shakes with a slow pulse every 6 s',
          'LGT_UND; core white-cyan #DFF8FF pulse 6 s, 8,000 lm at the core; pod hall in cold blue #6FA8D8 standby light',
          'Below Reactor Cell Three; opens with Brother Odo\'s map during MQ_A2_06', gate='MQ_A2_06 active and Odo\'s map (ITM_KEY_UV_ODOMAP)')
lv_meta[lid]['area'] = 'Cargo Vaults (deep)'
cx, cy, cz = float(c6['x_m']) - 60, float(c6['y_m']) - 120, -260
CORE = [('Entry', 'Core Hatch', (6, 6, 12), 'Ladder from Spent core room', 'Gate: MQ_A2_06'),
        ('Traverse', 'Spine ladderway', (6, 6, 40), 'Ladder 40 m', ''),
        ('Story', 'Cold Berth', (40, 80, 12), 'Walk', '400 sleeper pods on standby power; no combat; Restore ending wakes them'),
        ('Combat', 'Coolant ring', (16, 120, 10), 'Ring corridor', 'Remnant fort around the ring'),
        ('Loot', "Engineer's office", (10, 12, 4), 'Side door', "Chief Engineer's logs"),
        ('Traverse', 'Ring return', (6, 40, 6), 'One-way door', 'Shortcut 1 back to the ladderway'),
        ('Puzzle', 'Injector array', (24, 24, 16), 'Stairs', 'Align three injectors (rotate dials so beams meet the core port)'),
        ('Combat', 'Spine catwalk', (6, 90, 30), 'Injector bridge', 'Hollowed horde on a narrow catwalk; Remnant artillery across the gap'),
        ('Transit', 'Mag-rail', (4, 160, 6), 'Ride a maintenance cart on a magnetic rail', 'Cart under fire from 2 Mortar Frames'),
        ('Traverse', 'Ring lift', (6, 6, 30), 'Lift', 'Shortcut 2 up to the coolant ring'),
        ('Secret', "Captain's override locker", (4, 4, 3), 'Behind a loose panel in the mag-rail tunnel', ''),
        ('Anchor', "Governor's antechamber", (12, 16, 8), 'Lock door', 'Anchor 45 m from the fog gate'),
        ('Boss', 'Core housing', (50, 50, 30), 'Fog gate 4 m', 'The Governor'),
        ('Story', 'Core cradle', (12, 12, 10), 'Opens after the boss', "Ostra's cut memory as a Shard; CIN_MUTINY (6 min)"),
        ('Lift', 'Emergency lift', (6, 6, 175), 'Lift 175 m', 'Shortcut 3 to Reactor Cell Three spent core room')]
prev = None; prev_xy = None
for i, (role, nm, sz, tr, nt) in enumerate(CORE):
    rid = '%s_R%02d' % (lid, i + 1)
    x, y = ring(cx, cy, len(CORE), 110, i)
    z = cz - 40 * i / (len(CORE) - 1)
    e, lids, anc, extra = '', [], '', None
    if role == 'Entry': anc = new_anchor(lid, rid, x, y, z, 'Plan 3.7: Anchor at the entrance')
    if role == 'Anchor': anc = new_anchor(lid, rid, x, y, z, 'MET_FOGGATE')
    if nm == 'Coolant ring':
        e = new_enc(lid, rid, x, y, 'ENT_FORT', 'FAC_REMNANT', 46, 'ACT_REMNANT_SHIELDBEARER x2; ACT_REMNANT_ARTILLERY x2; ACT_REMNANT_HEAVY x1; ACT_REMNANT_FODDER x3', 8, 3)
        lt('ITM_CON_THR_STORM', 3, 'Corpse', rid, lid); lids = ['ITM_CON_THR_STORM x3']
    if nm == 'Spine catwalk':
        e = new_enc(lid, rid, x, y, 'ENT_HORDE', 'FAC_HOLLOWED', 46, 'ACT_HOLLOWED_FODDER x8; ACT_HOLLOWED_LEADER x1', 2, 2)
        e += ' ' + new_enc(lid, rid, x, y, 'ENT_GUNLINE', 'FAC_REMNANT', 46, 'ACT_REMNANT_ARTILLERY x2', 4, 1)
    if nm == 'Mag-rail':
        e = new_enc(lid, rid, x, y, 'ENT_GUNLINE', 'FAC_REMNANT', 46, 'ACT_REMNANT_ARTILLERY x2; ACT_REMNANT_SKIRMISHER x2', 0, 0, note='Fires on the moving cart')
    if role == 'Boss':
        b = UV_BOSSES['CORE']
        e = new_enc(lid, rid, x, y, 'BOSS', 'FAC_REMNANT', 46, '%s x1' % b['id'], 3, 0, 'Never', 'Main quest boss')
        extra = {'mus': b['mus']}; new_hooks.add(b['mus'])
        for it in ('ITM_MAT_SPC_ASCENDANT', 'ITM_LT_GEAR_REG_04', 'ITM_LT_BOSS_UV_CORE'): lt(it, 1, 'Boss drop', rid, lid)
        lids = ['ITM_MAT_SPC_ASCENDANT', 'ITM_LT_GEAR_REG_04', 'ITM_LT_BOSS_UV_CORE']
    if nm == "Engineer's office":
        for it in ('ITM_LT_SMALLCHEST_REG_04', lore(), lore()): lt(it, 1, 'Desk', rid, lid)
        lids = ['ITM_LT_SMALLCHEST_REG_04', 'ITM_LOR_UV x2']
    if nm == 'Cold Berth':
        lo = lore(); lt(lo, 1, 'Pod manifest', rid, lid); lids = [lo]
    if role == 'Secret':
        add_secret(lid, rid, 'Hidden panel', 'One panel in the mag-rail tunnel is a different colour', 'Stop the cart (brake lever) and hit the panel',
                   "ITM_LT_VAULT_REG_04; ITM_KEY_UV_OVERRIDE (opens the Captain's pod in Cold Berth: lore and a Relic)", 'Core')
        lt('ITM_LT_VAULT_REG_04', 1, 'Secret cache', rid, lid); lt('ITM_KEY_UV_OVERRIDE', 1, 'Secret cache', rid, lid)
        lids = ['ITM_LT_VAULT_REG_04', 'ITM_KEY_UV_OVERRIDE']
    if nm == 'Core cradle':
        lt('ITM_KEY_UV_OSTRAMEMORY', 1, 'Quest item', rid, lid, 'MQ_A2_06 objective; plays CIN_MUTINY'); lids = ['ITM_KEY_UV_OSTRAMEMORY']
        extra = {'mus': 'MUS_UV_MEMORY', 'light': 'Core cradle lit only by the memory Shard, 400 lm cyan'}; new_hooks.add('MUS_UV_MEMORY')
    if nm == 'Cold Berth':
        extra = {'mus': 'MUS_UV_COLD_BERTH', 'light': 'Pod standby blue #6FA8D8, 400 pods x 40 lm, no other light'}; new_hooks.add('MUS_UV_COLD_BERTH')
    add_room(lid, rid, role, nm, sz, tr, nt, x, y, z, '02', role not in OPTIONAL, e, '; '.join(lids), anc, extra)
    if prev and role not in OPTIONAL:
        edge(lid, prev, rid, tr, int(math.dist((x, y), prev_xy)), 'Fog gate' if role == 'Boss' else ('Boss defeated' if nm == 'Core cradle' else ''))
    if role in OPTIONAL:
        edge(lid, prev, rid, tr, 15, 'Hidden' if role == 'Secret' else '')
    else:
        prev = rid; prev_xy = (x, y)
edge(lid, 'LV_UV_CORE_R06', 'LV_UV_CORE_R02', 'Shortcut 1: one-way door', 30, 'Opens from the far side', 'Yes')
edge(lid, 'LV_UV_CORE_R10', 'LV_UV_CORE_R04', 'Shortcut 2: ring lift', 30, 'Call from below', 'No')
edge(lid, 'LV_UV_CORE_R15', 'LV_UV_02_S06_R10', 'Shortcut 3: emergency lift', 175, 'Boss defeated', 'No')
edge('LV_UV_02_S06', 'LV_UV_02_S06_R10', 'LV_UV_CORE_R01', 'Core Hatch', 12, 'MQ_A2_06 and ITM_KEY_UV_ODOMAP')

# ---- landmarks and POIs
pn = 0
for ak, a in AREAS.items():
    sites = [LOC['LOC_UV_REG_%s_%s' % (ak, s)] for s in SITE_ORDER]
    mx = sum(float(s['x_m']) for s in sites) / 6; my = sum(float(s['y_m']) for s in sites) / 6
    nm, h, vis, desc = a['lmk']
    pn += 1
    pois.append(dict(poi_id='LOC_LMK_UV_%s' % ak, kind='Landmark', area=a['name'], name=nm, x_m=round(mx), y_m=round(my), z_m=-120,
                     height_m=h, visible_km=vis, description=desc, reward='', time_min=0, music='MUS_UND_DISCOVERY', vfx='VFX_UV_VEIN_PULSE'))
    for j, (pnm, pdesc, rew) in enumerate(a['pois']):
        x, y = ring(mx, my, 4, 160, j, 0.4)
        pid = 'LOC_POI_UV_%s_%02d' % (ak, j + 1)
        pois.append(dict(poi_id=pid, kind='POI', area=a['name'], name=pnm, x_m=round(x), y_m=round(y), z_m=-100 - 20 * j,
                         height_m='', visible_km='', description=pdesc, reward=rew, time_min=3, music='MUS_UND_DISCOVERY', vfx='VFX_UV_LOOT_GLINT'))
        it = rew.split(' x')[0]
        lt(it, rew.split(' x')[1] if ' x' in rew else 1, 'POI', pid, 'POI')
pois.append(dict(poi_id='LOC_LMK_UV_CORE', kind='Landmark', area='Spine Tunnels', name='The Engine Heart glow', x_m=round(cx), y_m=round(cy), z_m=-140,
                 height_m=0, visible_km=1.0, description='The core pulse lights the tunnel walls white every 6 s near the Cargo Vaults junction; it pulls the eye toward the Core Hatch',
                 reward='', time_min=0, music='', vfx='VFX_UV_CORE_GLOW'))
new_hooks.update(['VFX_UV_CORE_GLOW', 'VFX_UV_LOOT_GLINT', 'VFX_UV_VEIN_PULSE'])

# area-level secrets (one per area, in the descent)
for ak, a in AREAS.items():
    rid = 'LV_UV_%s_ENTRY_R02' % ak
    add_secret('LV_UV_%s_ENTRY' % ak, rid, 'Hidden ledge', 'A ledge with a glowing vein below the descent route', 'Stop the lift or climb off at the halfway marker',
               'ITM_LT_VAULT_%s; %s' % (a['lootreg'], lore()), ak)
    lt('ITM_LT_VAULT_%s' % a['lootreg'], 1, 'Secret cache', rid, 'LV_UV_%s_ENTRY' % ak); lt('ITM_LOR_UV_%02d' % lore_n[0], 1, 'Secret cache', rid, 'LV_UV_%s_ENTRY' % ak)

# ---- bosses
for k, b in UV_BOSSES.items():
    hp = HP[b['cls']](b['level']); em = EMB[b['cls']](b['level'])
    host = 'LV_UV_CORE_R13' if k == 'CORE' else 'LV_UV_%s_S06_R09' % k
    bossrows.append(dict(boss=b['id'], name=b['name'], class_=b['cls'], level=b['level'], faction=b['fac'], archetype=b['arch'], room=host,
                         hp_solo=hp, ember=em, element=b['elem'], weak_to=b['weak'], phases=b['phases'], phase_hp_pct=b['thr'],
                         arena_shape=b['shape'], diameter_m=b['diam'], fog_gate='4 m, one-way while fighting',
                         anchor_run_m=45 if k == 'CORE' else 40, hazards=b['hazards'], phase1=b['p1'], phase2=b['p2'], phase3=b.get('p3', ''),
                         tells=b['tells'], music=b['mus'], drops='ITM_MAT_SPC_ASCENDANT 100%%; ITM_LT_GEAR_*; ITM_LT_BOSS_UV_%s' % k,
                         sfx='SFX_UV_BOSS_%s_*' % b['id'].split('_')[-1], vfx='VFX_UV_BOSS_%s_*' % b['id'].split('_')[-1],
                         note='HP and Ember fitted from data/actors/bosses.csv %s class' % b['cls']))

# ---- per-level totals
for L in levels:
    rs = [r for r in rooms if r['level_id'] == L['level_id']]
    crit = sum(int(r['time_s']) for r in rs if r['critical_path'] == 'Yes')
    full = sum(int(r['time_s']) for r in rs)
    es = [e for e in encs if e['level_id'] == L['level_id']]
    L.update(rooms=len(rs), encounters=len(es), enemies=sum(int(e['total']) for e in es),
             loot_rows=len([l for l in loot if l['level_id'] == L['level_id']]),
             secrets=len([s for s in secrets if s['level_id'] == L['level_id']]),
             anchors=len([r for r in rs if r['anchor']]),
             first_clear_min=round(crit / 60), full_clear_min=round(full / 60))

# ---------------------------------------------------------------- write
os.makedirs(os.path.join(OUT, 'sheets'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'maps'), exist_ok=True)
wr('levels.csv', levels, ['level_id', 'loc_id', 'name', 'area', 'kind', 'kit', 'level', 'critical_path', 'gate', 'rooms', 'encounters', 'enemies',
                          'loot_rows', 'secrets', 'anchors', 'first_clear_min', 'full_clear_min', 'mood', 'lighting', 'notes'])
wr('rooms.csv', rooms)
wr('edges.csv', edges)
wr('encounters.csv', encs)
wr('loot.csv', loot)
wr('secrets.csv', secrets)
wr('anchors.csv', anchors + [dict(anchor_id=v, source='world', level_id='', room_id=next((r['room_id'] for r in rooms if r['anchor'] == v), ''),
                                  reason='Placed by world', fast_travel='No (until lit)') for v in WANC.values()],
   ['anchor_id', 'source', 'level_id', 'room_id', 'x_m', 'y_m', 'z_m', 'reason', 'fast_travel'])
wr('landmarks_pois.csv', pois)
wr('bosses.csv', bossrows)

# data requests
R = []
def rq(target, field, value, reason): R.append(dict(req_id='UVREQ_%02d' % (len(R) + 1), target=target, field=field, value=value, reason=reason))
rq('data/world/locations.csv', 'new LOC rows', 'LOC_UV_CORE (Undervault site, REG_U, The Engine Heart, x %d y %d z -260, level 46, parent LOC_UV_REG_02_S06)' % (cx, cy), 'Campaign MQ_A2_06 core housing has no location')
rq('data/world/locations.csv', 'new LOC rows', '%d anchors LOC_ANC_UV_01..%02d (see anchors.csv, source=new)' % (anc_n[0], anc_n[0]), 'Plan 3.7 Anchor at every site entrance; MET_FOGGATE')
rq('data/world/locations.csv', 'new LOC rows', '%d secrets LOC_SEC_UV_01..%02d (see secrets.csv)' % (sec_n[0], sec_n[0]), 'Undervault secrets')
rq('data/world/locations.csv', 'new LOC rows', 'LOC_LMK_UV_02/03/05/CORE and LOC_POI_UV_* (see landmarks_pois.csv)', 'Undervault landmarks and POIs')
rq('data/actors/bosses.csv', 'new rows', '; '.join('%s %s %s L%d HP %d' % (b['boss'], b['name'], b['class_'], b['level'], b['hp_solo']) for b in bossrows), 'Area bosses and the MQ_A2_06 boss (see bosses.csv for phases and arenas)')
rq('data/actors/boss_moves.csv and boss_phases.csv', 'new rows', 'Moves and phases for the 4 ACT_BOSS_UV_* from bosses.csv phase columns', 'Boss frame data')
rq('data/items/loot_tables.csv', 'new tables', 'ITM_LT_BOSS_UV_02, _03, _05, _CORE (Ember via ECOF_BOSS, Ascendant 35%, gear x4 Rare+ like ITM_LT_BOSS_36)', 'Boss drops')
rq('data/items/lore_items.csv', 'new rows', 'ITM_LOR_UV_01..27, lore_type Ship log (Meridian engine block), region REG_U; hosts in loot.csv', 'Site rule: at least one lore item per site')
rq('data/items (key items)', 'new rows', "ITM_KEY_UV_ODOMAP (Brother Odo's map, MQ_A2_06), ITM_KEY_UV_OSTRAMEMORY (Ostra's cut memory Shard), ITM_KEY_UV_OVERRIDE (Captain's override key)", 'Quest and secret gates')
rq('data/assets/asset_hooks.csv', 'new hooks', ' '.join(sorted(h for h in new_hooks if h not in ALL_IDS)), 'Undervault level cues (also MUS_BOSS_UV_* to design/audio/music_cues.csv)')
rq('data/ui/strings.csv', 'new strings', 'STR_LOC_<id>_NAME for every level, room-free: %d levels, %d POIs and landmarks, 4 boss names' % (len(levels), len(pois)), 'Map and banner names')
rq('data/items/loot_tables.csv', 'new tables (optional)', 'none: decided 2026-10-06 that Undervault containers reuse the surface band tables', 'Until then loot.csv uses the surface tables whose band matches each area (REG_04/05/06)')
wr('data-requests.csv', R)

# conflicts
C = [dict(conflict='Undervault shaft regions', source_a='design/campaign/01-lore-bible.md: under Cinderreach, Glasswaste and Hollowdeep',
          source_b='design/world/locations.csv: entries in Saltmere, Thornwood and Rimefall', resolution='Followed world (owns region layout); plan 3.7 only says three regions. Campaign thread should update the lore bible.'),
     dict(conflict='Same six site types in each area', source_a='Plan 3.7: reskins capped at one per region', source_b='design/world/locations.csv names the same six site kinds per area',
          resolution='Each site has its own name, area hazard, puzzle twist and unique reward here; world may want to vary the kinds'),
     dict(conflict='Undervault entry level vs site level', source_a='Entry LOC_UV_ENTRY_02 level 14 (Saltmere)', source_b='First site below is level 32',
          resolution='Kept; the descent mouth shows a level warning popup (NTF request to UI) and the threshold has a dropped-corpse warning')]
wr('conflicts.csv', C)

# ---------------------------------------------------------------- level sheets
for L in levels:
    lid = L['level_id']
    rs = [r for r in rooms if r['level_id'] == lid]
    out = ['# %s (%s)' % (L['name'], lid), '',
           '%s, %s. Level %s. Location %s. Kit %s.' % (L['kind'], L['area'], L['level'], L['loc_id'], L['kit']), '',
           '**Time:** %s min on the critical path, %s min for everything. **Rooms:** %s. **Encounters:** %s (%s enemies). **Secrets:** %s. **Anchors:** %s.' % (
               L['first_clear_min'], L['full_clear_min'], L['rooms'], L['encounters'], L['enemies'], L['secrets'], L['anchors']), '',
           '**Mood:** %s.' % L['mood'], '', '**Lighting:** %s.' % L['lighting'], '']
    if L['gate']: out += ['**Gate:** %s.' % L['gate'], '']
    if L['notes']: out += ['**Notes:** %s.' % L['notes'], '']
    out += ['## Rooms (critical path marked)', '', '| Room | Role | Name | Size m | z m | Path | Way in | Encounters | Loot | Cues (music / SFX / VFX) |', '|---|---|---|---|---|---|---|---|---|---|']
    for r in rs:
        out.append('| %s | %s | %s | %sx%sx%s | %s | %s | %s | %s | %s | %s / %s / %s |' % (r['room_id'][-3:], r['role'], r['name'], r['w_m'], r['d_m'], r['h_m'], r['z_m'],
                   'crit' if r['critical_path'] == 'Yes' else 'opt', r['traversal_in'], r['encounters'], r['loot'], r['music'], r['sfx'], r['vfx']))
    out += ['', '## Connections', '']
    for e in edges:
        if e['level_id'] == lid:
            out.append('- %s to %s: %s, %s m%s%s' % (e['from_room'], e['to_room'], e['type'], e['length_m'], ', one-way' if e['one_way'] == 'Yes' else '',
                                                    ', gate: ' + e['gate'] if e['gate'] else ''))
    es = [e for e in encs if e['level_id'] == lid]
    if es:
        out += ['', '## Encounters', '']
        for e in es: out.append('- %s (%s) in %s: %s, level %s, %s; cover %s, fallback %s, respawn %s' % (e['enc_id'], e['source'], e['room_id'][-3:], e['template'], e['level'], e['actors'], e['cover_points'], e['fallback_points'], e['respawn']))
    ss = [s for s in secrets if s['level_id'] == lid]
    if ss:
        out += ['', '## Secrets', '']
        for s in ss: out.append('- %s in %s: %s. Hint: %s. Needs: %s. Reward: %s.' % (s['secret_id'], s['room_id'][-3:], s['secret_type'], s['hint'], s['requirement'], s['reward']))
    bs = [b for b in bossrows if b['room'].startswith(lid + '_')]
    for b in bs:
        out += ['', '## Boss: %s (%s)' % (b['name'], b['boss']), '',
                '%s class, level %s, %s HP solo, %s Ember. %s. Element %s, weak to %s.' % (b['class_'], b['level'], b['hp_solo'], b['ember'], b['archetype'], b['element'], b['weak_to']), '',
                '- Arena: %s, %s m. Fog gate %s. Anchor run %s m.' % (b['arena_shape'], b['diameter_m'], b['fog_gate'], b['anchor_run_m']),
                '- Hazards: %s.' % b['hazards'], '- Phase 1: %s.' % b['phase1'], '- Phase 2: %s.' % b['phase2']]
        if b['phase3']: out.append('- Phase 3: %s.' % b['phase3'])
        out += ['- Tells: %s.' % b['tells'], '- Music %s. Drops: %s.' % (b['music'], b['drops'])]
    open(os.path.join(OUT, 'sheets', lid + '.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')

# ---------------------------------------------------------------- maps (node graphs, top view)
def svg(name, lids, title):
    rs = [r for r in rooms if r['level_id'] in lids]
    xs = [r['x_m'] for r in rs]; ys = [r['y_m'] for r in rs]
    x0, x1, y0, y1 = min(xs) - 60, max(xs) + 60, min(ys) - 60, max(ys) + 60
    s = 900 / max(x1 - x0, y1 - y0)
    P = lambda x, y: ((x - x0) * s + 20, (y1 - y) * s + 40)
    pos = {r['room_id']: P(r['x_m'], r['y_m']) for r in rs}
    col = {'Entry': '#E8A23A', 'Combat': '#D0503C', 'Boss': '#9B2C2C', 'Secret': '#9B7BD6', 'Loot': '#4F8FE6', 'Puzzle': '#3FC8C0',
           'Anchor': '#E8A23A', 'End': '#8FE3EE', 'Story': '#DFF8FF'}
    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="sans-serif" font-size="9">' % (940, 980),
         '<rect width="100%" height="100%" fill="#10181A"/>', '<text x="20" y="22" fill="#EEE" font-size="14">%s (top view, node graph; colour = room role)</text>' % title]
    for e in edges:
        if e['from_room'] in pos and e['to_room'] in pos:
            (ax, ay), (bx, by) = pos[e['from_room']], pos[e['to_room']]
            dash = ' stroke-dasharray="4 3"' if e['one_way'] == 'Yes' or e['type'].startswith('Shortcut') else ''
            o.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#7A8A8A"%s/>' % (ax, ay, bx, by, dash))
    for r in rs:
        x, y = pos[r['room_id']]
        o.append('<circle cx="%.0f" cy="%.0f" r="5" fill="%s"/>' % (x, y, col.get(r['role'], '#9AA')))
        o.append('<text x="%.0f" y="%.0f" fill="#CCD">%s</text>' % (x + 7, y + 3, r['room_id'].replace('LV_UV_', '')))
    o.append('</svg>')
    open(os.path.join(OUT, 'maps', name), 'w').write('\n'.join(o))
for ak, a in AREAS.items():
    svg('area_%s.svg' % ak, ['LV_UV_%s_ENTRY' % ak] + ['LV_UV_%s_%s' % (ak, s) for s in SITE_ORDER], a['name'])
svg('engine_heart.svg', ['LV_UV_CORE'], 'The Engine Heart')
svg('spine_tunnels.svg', ['LV_UV_TUN_0203', 'LV_UV_TUN_0205', 'LV_UV_02_S04', 'LV_UV_03_S04', 'LV_UV_05_S04'], 'Spine Tunnels')

# summary
print('levels', len(levels), 'rooms', len(rooms), 'edges', len(edges), 'encounters', len(encs), 'enemies', sum(int(e['total']) for e in encs),
      'loot', len(loot), 'requested', sum(1 for l in loot if l['status'] == 'requested'), 'secrets', len(secrets), 'new anchors', anc_n[0],
      'pois', len(pois), 'first_clear_h', round(sum(L['first_clear_min'] for L in levels) / 60, 1), 'full_h', round(sum(L['full_clear_min'] for L in levels) / 60, 1))
