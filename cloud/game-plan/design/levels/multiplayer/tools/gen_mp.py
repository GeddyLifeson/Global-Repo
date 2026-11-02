#!/usr/bin/env python3
"""Shardfall multiplayer level design generator.

Writes every table and doc in design/levels/multiplayer/ from the data below.
Reads data/ and design/ read-only to validate IDs. Run:
    python3 design/levels/multiplayer/tools/gen_mp.py
Every value not quoted from the plan, data/ or design/loops is a design choice (3 Oct 2026).
"""
import csv, math, os, re, sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
GP = os.path.abspath(os.path.join(OUT, '..', '..', '..'))  # game-plan/
D = os.path.join(GP, 'data')

# ---------------------------------------------------------------- ID sources
def ids(path, col=0):
    p = os.path.join(GP, path)
    with open(p, newline='', encoding='utf-8') as f:
        r = csv.reader(f); next(r)
        return {row[col] for row in r if row}

KNOWN = set()
for p in ['data/actors/enemies.csv', 'data/actors/bosses.csv', 'data/actors/boss_phases.csv',
          'data/actors/boss_moves.csv', 'data/items/items_index.csv', 'data/items/loot_tables.csv',
          'design/audio/music_cues.csv', 'design/art/lighting_tod.csv', 'design/art/post_process_volumes.csv',
          'design/world/locations.csv', 'data/actors/coop_scaling.csv', 'data/assets/asset_hooks.csv']:
    KNOWN |= ids(p)
# ui strings / popups keys
for p in ['data/ui/strings.csv', 'data/ui/popups.csv']:
    KNOWN |= ids(p)

# New IDs this folder defines and asks other owners to add (see data-requests.csv)
PENDING = set()

def w(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        cw = csv.writer(f); cw.writerow(header); cw.writerows(rows)

# ---------------------------------------------------------------- shared rules
CELL_M = 2  # arena grid cell size

# ================================================================ STRIKES
# Structure from design/loops/06-endgame.md: drop in, Holdout, traversal, Choir vault,
# field-boss pair at L80. 3 players, COOP_OW_3 / COOP_BOSS_3 scaling, level 80 sync.
STRIKES = [
 dict(id='STK_01', name='The Ash Crown', reg='REG_01', light='LGT_REG_01_DUSK', ppv='PPV_REG_01',
      start='LOC_DGN_REG_01_05', vault='LOC_DGN_REG_01_06', arena='LOC_FB_ASHCOLOSSUS',
      fod=['ACT_VAR_R1_01', 'ACT_VAR_R1_02'], sk=['ACT_VAR_R1_03', 'ACT_VAR_R1_04'], sh='ACT_VAR_R1_05',
      art='ACT_THORN_ARTILLERY', hv='ACT_HOLLOWED_HEAVY', ld='ACT_THORN_LEADER',
      bossA='ACT_BOSS_ASHCOLOSSUS', bossB='ACT_BOSS_NIGHTDRAKE', mins=22,
      mood='Burnt orange dusk, ash snow falling, crash-scar glow from below; hope against a dying sky',
      trav=('Skimmer run', 'Two skimmers spawn at the crypt mouth; cross 420 m of ash plain between 3 ember geysers that erupt every 9 s (telegraph 1.5 s, 400 dmg).'),
      hold='Ostra uplink at the Ash Crypt bell tower: hold a 10 m ring for 120 s while Ostra maps the vault.',
      vmech=('Ember braziers', 'Carry 3 Ember Cores (dropped by the Warchief and two Shieldmen) to 3 braziers; each lit brazier drops one vault seal. Carrier cannot dodge-roll, only walk-dodge.'),
      hazard='Ash Colossus stomps open magma vents (3 m, 5 s) that persist 20 s; the Drake strafes in a straight line marked by a red ash trail 2 s ahead.'),
 dict(id='STK_02', name='Tidewreck', reg='REG_02', light='LGT_REG_02_STORM', ppv='PPV_REG_02',
      start='LOC_DGN_REG_02_05', vault='LOC_DGN_REG_02_06', arena='LOC_FB_LEVIATHAN',
      fod=['ACT_VAR_R2_01', 'ACT_VAR_R2_02'], sk=['ACT_VAR_R2_05', 'ACT_VAR_R2_06'], sh='ACT_REMNANT_SHIELDBEARER',
      art='ACT_REMNANT_ARTILLERY', hv='ACT_REMNANT_HEAVY', ld='ACT_REMNANT_LEADER',
      bossA='ACT_BOSS_LEVIATHAN', bossB='ACT_BOSS_SKIMMERACE', mins=24,
      mood='Green-grey storm surf, wet hull plate, lightning silhouettes the wreck; tense and cold',
      trav=('Tide hop', 'Cross a broken hull chain on foot; the tide floods the low decks for 15 s every 45 s (drowning 8% HP/s). High ledges are safe.'),
      hold='Hold the pump room while Ostra restarts the bilge pumps; three waves through two flooded doors, 120 s.',
      vmech=('Flood valves', 'Turn 3 valves (6 s channel each, interrupted by damage) to drain the vault; each valve channel spawns 2 Hornet Drones.'),
      hazard='Leviathan surfaces at one of 4 marked gill pools; Skimmer Ace laps the lagoon and must be shot off its skimmer (engine weak point) before melee can hit it.'),
 dict(id='STK_03', name='Briar Hunt', reg='REG_03', light='LGT_REG_03_NIGHT', ppv='PPV_REG_03',
      start='LOC_DGN_REG_03_05', vault='LOC_DGN_REG_03_06', arena='LOC_FB_THORNHOUND',
      fod=['ACT_VAR_R3_03', 'ACT_VAR_R3_02'], sk=['ACT_VAR_R3_06', 'ACT_VAR_R3_05'], sh='ACT_THORN_SHIELDBEARER',
      art='ACT_THORN_ARTILLERY', hv='ACT_THORN_HEAVY', ld='ACT_THORN_LEADER',
      bossA='ACT_BOSS_THORNHOUND', bossB='ACT_BOSS_BOGMATRIARCH', mins=23,
      mood='Moonlit canopy, blue haze, red clan torches; a hunt where the team is the prey',
      trav=('Canopy glide', 'Strider glide between 6 great trees (gaps 18 to 32 m); thermal vents give lift; Bonebow Archers on two trees shoot gliders.'),
      hold='Defend the clan totem the team has captured: Warchiefs try to re-light it; hold 120 s and stop 3 relight channels (8 s each).',
      vmech=('Thorn seals', 'Burn 4 thorn seals with Ember damage (any source, 600 each) while a Briar Stalker pack hunts the burner.'),
      hazard='Bog Matriarch floods the low ground with spawn pools (Root on touch); the Hound marks the farthest player and charges after 2 s.'),
 dict(id='STK_04', name='Lens of Noon', reg='REG_04', light='LGT_REG_04_DAY', ppv='PPV_REG_04',
      start='LOC_DGN_REG_04_05', vault='LOC_DGN_REG_04_06', arena='LOC_FB_BASILISK',
      fod=['ACT_VAR_R4_02', 'ACT_VAR_R4_01'], sk=['ACT_VAR_R4_05', 'ACT_VAR_R4_04'], sh='ACT_REMNANT_SHIELDBEARER',
      art='ACT_REMNANT_ARTILLERY', hv='ACT_HOLLOWED_HEAVY', ld='ACT_REMNANT_LEADER',
      bossA='ACT_BOSS_BASILISK', bossB='ACT_BOSS_HAULER', mins=25,
      mood='White noon glare over glass dunes, hard shadows, heat shimmer; exposed and dazzling',
      trav=('Hauler escort', 'Ride a six-seat hauler 650 m through a glass canyon; one player drives, one mans the turret, one repairs (hauler HP 12,000).'),
      hold='Hold the canyon relay while its dish re-aligns; enemies drop from two Remnant carriers, 120 s.',
      vmech=('Sun lenses', 'Rotate 3 mirror lenses so the noon beam hits the vault eye; each lens turns 45 degrees per interact; wrong angle burns the vault floor.'),
      hazard='Basilisk gaze petrifies anyone facing it for 2 s (look away cue); the Wandering Hauler circles the arena edge and must lose engine, turret, wheels.'),
 dict(id='STK_05', name='The Frozen Choir', reg='REG_05', light='LGT_REG_05_DAWN', ppv='PPV_REG_05',
      start='LOC_DGN_REG_05_05', vault='LOC_DGN_REG_05_06', arena='LOC_FB_FROSTTITAN',
      fod=['ACT_VAR_R5_03', 'ACT_VAR_R5_01'], sk=['ACT_VAR_R5_06', 'ACT_VAR_R5_05'], sh='ACT_CHOIRBORN_SHIELDBEARER',
      art='ACT_CHOIRBORN_ARTILLERY', hv='ACT_REMNANT_HEAVY', ld='ACT_CHOIRBORN_LEADER',
      bossA='ACT_BOSS_FROSTTITAN', bossB='ACT_BOSS_ARKKNIGHT', mins=24,
      mood='Pale pink dawn on blue ice, frozen choir statues, breath fog; reverent and lonely',
      trav=('Ice bridge', 'Cross a 300 m ice bridge that cracks behind the team; standing still over 4 s stacks Slow; Blinkblades ambush at the halfway pylon.'),
      hold='Keep the abbey brazier alive (HP 8,000) for 120 s; Choir Acolytes channel frost at it.',
      vmech=('Bell tones', 'Ring 3 bells in the order the vault hums (shown as rising frost rings); a wrong bell spawns a Choir Lancer.'),
      hazard='Frost Titan breath freezes a 90-degree cone (Freeze at 3 Slow stacks); the Ark-Knight duels the closest player and parries ranged shots in phase 2.'),
 dict(id='STK_06', name='The Bone Lift', reg='REG_06', light='LGT_REG_06_NIGHT', ppv='PPV_REG_06',
      start='LOC_DGN_REG_06_05', vault='LOC_DGN_REG_06_06', arena='LOC_FB_BONEHARVESTER',
      fod=['ACT_VAR_R6_03', 'ACT_VAR_R6_01'], sk=['ACT_VAR_R6_04', 'ACT_VAR_R6_05'], sh='ACT_CHOIRBORN_SHIELDBEARER',
      art='ACT_HOLLOWED_ARTILLERY', hv='ACT_CHOIRBORN_HEAVY', ld='ACT_CHOIRBORN_LEADER',
      bossA='ACT_BOSS_BONEHARVESTER', bossB='ACT_BOSS_SENTINELS', mins=25,
      mood='Black void lit by violet Shard veins and lantern pools; the land being pulled into the sky',
      trav=('Falling platforms', 'Climb 9 floating rock platforms that drift upward and crumble 6 s after first touch; jump pads at platforms 3 and 7.'),
      hold='Hold a lantern pool: outside the light, Hollowing drains 2% HP/s; the pool shrinks from 12 m to 6 m over 120 s.',
      vmech=('Lantern dark', 'Vault is pitch dark; carry 3 lanterns from pedestals to sockets; a lantern carrier lights 8 m; dropping it near a Hollow Herald snuffs it.'),
      hazard='Bone Harvester drags players with a hook (break with 300 dmg to the cage); Twin Sentinels swap the shield between them every 20 s.'),
 dict(id='STK_S1', name='The Sunken Index', reg='REG_U', light='LGT_UND', ppv='PPV_UND',
      start='', vault='', arena='', season=1,
      fod=['ACT_HOLLOWED_FODDER', 'ACT_REMNANT_FODDER'], sk=['ACT_REMNANT_SKIRMISHER', 'ACT_HOLLOWED_SKIRMISHER'], sh='ACT_HOLLOWED_SHIELDBEARER',
      art='ACT_REMNANT_ARTILLERY', hv='ACT_REMNANT_HEAVY', ld='ACT_HOLLOWED_LEADER',
      bossA='ACT_BOSS_VAULTKEEPER', bossB='ACT_BOSS_CLOCKPRIOR', mins=25,
      mood='Flooded ship archive under the crust, teal emergency light, dripping cable forests; claustrophobic',
      trav=('Sluice ride', 'Ride a flooded sluice on a cargo raft for 500 m; switch tracks at 3 junctions by shooting signal lamps (missed lamp = drone ambush branch).'),
      hold='Defend the archive pump terminal while Ostra copies a lost log, 120 s, from three vents.',
      vmech=('Index locks', 'Match 4 clock faces to the time shown on Ostra\'s log (rotate by striking); each correct face opens one bolt.'),
      hazard='Vault Keeper slams flood the floor (Shock conducts in water x1.5); Clock Prior stops time for 3 s every 30 s, freezing anyone not in a gear-light.'),
]

STRIKE_NODES = [  # node suffix, kind, name pattern, size m, checkpoint, desc
 ('N01', 'drop', 'Drop Anchor', '20x20', 'CP1', 'Fireteam spawns from orbit drop; Anchor lit; strike banner'),
 ('N02', 'approach', 'Approach', '120x40', '', 'Two patrol groups; flank path on high ground; lore item in side alcove'),
 ('N03', 'holdout', 'Holdout', '50x50', '', 'Segment 1 (Holdout template)'),
 ('N04', 'traversal', 'Traversal', 'route', '', 'Traversal set piece'),
 ('N05', 'vault_gate', 'Vault Gate', '20x16', 'CP2', 'Anchor; ammo and Tonic refill crate'),
 ('N06', 'vault', 'Choir Vault', '40x40', '', 'Segment 2 (Choir vault template)'),
 ('N07', 'gauntlet', 'Gauntlet', '80x24', '', 'Heavy push corridor with side cover'),
 ('N08', 'boss_gate', 'Boss Gate', '16x12', 'CP3', 'Fog wall; Anchor; last refill'),
 ('N09', 'boss', 'Boss Arena', '70x70', '', 'Field-boss pair'),
 ('N10', 'exit', 'Reward Cache', '16x16', '', 'Strike chest, Ostra line, return to orbit after 30 s'),
]
EDGE_LEN = [('N01', 'N02', 60, 'path'), ('N02', 'N03', 90, 'path'), ('N03', 'N04', 20, 'gate opens after Holdout'),
            ('N04', 'N05', 0, 'route end'), ('N05', 'N06', 15, 'door'), ('N06', 'N07', 25, 'vault seal'),
            ('N07', 'N08', 40, 'path'), ('N08', 'N09', 10, 'fog wall'), ('N09', 'N10', 20, 'opens on boss death'),
            ('N07', 'N05', 30, 'one-way shortcut drop')]

def strike_rows():
    maps, nodes, edges, encs, spawns, loot, cps, strs, cues = [], [], [], [], [], [], [], [], []
    for s in STRIKES:
        sid = s['id']; key = sid.replace('STK_', 'STK')
        PENDING.add(f'LOC_MP_{sid}')
        maps.append([f'LOC_MP_{sid}', 'Strike', s['name'], s['reg'], '3', '80 (sync)', f"{s['mins']-3}-{s['mins']}",
                     s['mins'], '~1.1 km route', s['light'], s['ppv'], s['mood'],
                     f'MUS_MP_{key}_EXPLORE; MUS_MP_{key}_COMBAT; MUS_MP_{key}_BOSS', f'SFX_MP_AMB_{key}',
                     'COOP_OW_3 (adds) / COOP_BOSS_3 (bosses)', 'Season 1' if s.get('season') else 'Launch'])
        for nid, kind, nm, size, cp, desc in STRIKE_NODES:
            extra = {'holdout': s['hold'], 'traversal': f"{s['trav'][0]}: {s['trav'][1]}",
                     'vault': f"{s['vmech'][0]}: {s['vmech'][1]}", 'boss': s['hazard']}.get(kind, '')
            loc = {'drop': s['start'], 'vault': s['vault'], 'boss': s['arena']}.get(kind, '')
            nodes.append([f'{sid}_{nid}', f'LOC_MP_{sid}', nid, kind, nm, size, cp, loc, (desc + ('. ' + extra if extra else '')).strip()])
        for a, b, L, t in EDGE_LEN:
            L2 = 450 if (a, b) == ('N03', 'N04') and 'Hauler' in s['trav'][0] else L
            edges.append([f'{sid}_{a}', f'{sid}_{b}', t, L2 if L2 else s['trav'][0] + ' route'])
        # checkpoints
        for i, n in enumerate(['N01', 'N05', 'N08'], 1):
            cps.append([f'{sid}_CP{i}', f'LOC_MP_{sid}', f'{sid}_{n}', 'Anchor', 'Team wipe returns here; 3 wipes at one checkpoint = return to orbit (06-endgame.md)', 'Refill Tonics to 3 per player at CP2 and CP3'])
        # encounters + waves
        F1, F2 = s['fod']; K1, K2 = s['sk']
        plan = [
          ('E1', 'N02', 'Patrol', 'Clear or sneak past', '', [(1, F1, 4), (1, K1, 2), (2, F2, 4), (2, s['art'], 1)]),
          ('E2', 'N03', 'Holdout', s['hold'], '120 s; zone empty 10 s = progress paused, not lost',
             [(1, F1, 6), (1, K1, 3), (2, s['sh'], 2), (2, s['art'], 2), (2, F2, 4), (3, s['hv'], 1), (3, s['ld'], 1), (3, K2, 4)]),
          ('E3', 'N04', 'Traversal', s['trav'][1], 'Fall = respawn at route start segment, no wipe count', [(1, K1, 3), (1, s['art'], 2)]),
          ('E4', 'N06', 'Vault', s['vmech'][1], 'No timer; adds respawn every 40 s until the vault opens (cap 10 alive)',
             [(1, s['sh'], 2), (1, s['art'], 2), (1, F1, 6), (2, s['ld'], 1), (2, K2, 3)]),
          ('E5', 'N07', 'Gauntlet', 'Push through to the boss gate', '', [(1, s['hv'], 2), (1, s['art'], 2), (1, K1, 4), (1, F2, 4)]),
          ('E6', 'N09', 'Boss pair', f"{s['bossA']} engages first; {s['bossB']} enters at {s['bossA']} 50% HP. When one dies the other gains +15% damage (Bereft). {s['hazard']}",
             'Soft enrage 8 min: arena hazard frequency x2', [(1, s['bossA'], 1), (2, F1, 6), (3, s['bossB'], 1), (4, F2, 4)]),
        ]
        trig = {1: 'on enter', 2: 'wave 1 at 25% alive or 40 s', 3: 'wave 2 at 25% alive or 40 s', 4: 'every 45 s while a boss lives (cap 8 alive)'}
        btrig = {1: 'fog wall crossed', 2: f"{s['bossA']} at 66% HP", 3: f"{s['bossA']} at 50% HP", 4: 'every 45 s (cap 8 alive)'}
        for eid, node, kind, obj, rule, waves in plan:
            encs.append([f'{sid}_{eid}', f'LOC_MP_{sid}', f'{sid}_{node}', kind, obj, rule, sum(c for _, _, c in waves)])
            for wv, act, cnt in waves:
                tg = (btrig if kind == 'Boss pair' else trig)[wv]
                spawns.append([f'{sid}_{eid}', wv, act, cnt, '80', tg, f'{sid}_{node}_SP{wv}'])
        # loot
        loot += [[f'{sid}_E2', 'Holdout cache', 'ITM_MAT_DUST_02', '100%', '2-3', 'Every clear'],
                 [f'{sid}_E4', 'Vault chest', 'ITM_LT_ENDGAME_STRIKE', '100%', '1 roll', 'Every clear'],
                 [f'{sid}_E4', 'Vault chest', 'ITM_MAT_GLASS_02', '100%', '1-2', 'Every clear'],
                 [f'{sid}_E6', s['bossA'], 'ITM_LT_ENDGAME_STRIKE', '100%', '1 roll', 'Every clear'],
                 [f'{sid}_E6', s['bossB'], 'ITM_LT_ENDGAME_STRIKE', '100%', '1 roll', 'Every clear'],
                 [f'{sid}_E6', s['bossB'], 'ITM_MAT_SPC_ASCENDANT', '25%', '1', 'Every clear'],
                 [f'{sid}_N10', 'Strike chest', 'ITM_MAT_STAR_01', '100%', '2-4', 'Every clear (6-12 over 3 featured clears, 06-endgame.md)'],
                 [f'{sid}_N10', 'Strike chest', 'ITM_CUR_SEALS', '100%', '10', 'x2 on first 3 featured clears; weekly cap 100'],
                 [f'{sid}_N02', 'Lore alcove', 'ITM_LT_ENDGAME_STRIKE', '15%', '1 roll', 'First clear per week']]
        # strings
        strs += [[f'STR_MP_{sid}_NAME', s['name']],
                 [f'STR_MP_{sid}_DESC', f"Strike. {s['mood'].split(';')[0]}."],
                 [f'STR_MP_{sid}_OBJ_HOLD', 'Hold the zone ({VAR_SECONDS} s)'],
                 [f'STR_MP_{sid}_OBJ_TRAV', s['trav'][0]],
                 [f'STR_MP_{sid}_OBJ_VAULT', s['vmech'][0] + ' ({VAR_COUNT}/{VAR_TOTAL})'],
                 [f'STR_MP_{sid}_OBJ_BOSS', 'Defeat the guardians']]
        # cues
        cues += [[f'MUS_MP_{key}_EXPLORE', 'Music', sid, 'N01-N02, N04, N05', 'Region motif, low strings, 70 bpm'],
                 [f'MUS_MP_{key}_COMBAT', 'Music', sid, 'E2, E4, E5 start', 'Region combat layer, 120 bpm, stingers on wave start'],
                 [f'MUS_MP_{key}_BOSS', 'Music', sid, 'E6', 'Boss-pair track, swaps lead at bossB entry'],
                 [f'SFX_MP_AMB_{key}', 'Ambience', sid, 'whole map', s['mood']],
                 [f'VFX_MP_{key}_TRAV', 'VFX', sid, 'E3', s['trav'][0] + ' hazards and telegraphs'],
                 [f'VFX_MP_{key}_VAULT', 'VFX', sid, 'E4', s['vmech'][0] + ' objects, carried state and success burst'],
                 [f'SFX_MP_{key}_VAULT', 'SFX', sid, 'E4', s['vmech'][0] + ' interact, progress tick, success chord']]
    for c in cues: PENDING.add(c[0])
    return maps, nodes, edges, encs, spawns, loot, cps, strs, cues

# ================================================================ RAID
RAID = [
 dict(n=1, loc='LOC_END_RAID_01', name='Core Breach', boss='ACT_BOSS_QUIETCORE', lvl=80, mins=47, add='ACT_RAID_CONDUIT',
      nodes=[('Raid Gate', 'drop', 'CP', 'Lantern Hold raid gate drop pod lands on the Quiet hull; banner, Ostra line'),
             ('Airlock Gauntlet', 'traversal', '', 'Three airlocks cycle every 12 s; venting = 18 m/s knockback into void. Two levers 40 m apart must be held at once (split 3/3) to stop a cycle for 20 s'),
             ('Spinal Corridor', 'adds', '', '140 m corridor of Remnant drones; secret vent behind the 2nd bulkhead to the wing chest'),
             ('Reactor Approach', 'gate', 'CP', 'Anchor; wipe checkpoint; refill'),
             ('Core Chamber', 'boss', '', '60 m round chamber, 3 raised node platforms at 120 degrees, gravity pads on the walls'),
             ('Core Vault', 'exit', '', 'Loot vault; path to Wing 2')],
      mech=[('Containment', 'The Core is immune (Hollow shell) until all 3 containment nodes are overloaded within 15 s of each other. Killing a Conduit Drone gives its killer 1 Conduit charge (max 10); standing on a node spends charges, 10 overload it.', '3 runners (one per node), 2 add clear, 1 stance breaker', 'Nodes glow white to blue as charge fills; 15 s ring timer on HUD', 'Nodes reset; boss casts Core Overload (heavy raid damage)'),
            ('Exposure', 'After overload the Core opens for 20 s; nodes take x3.0 damage (weak point), core takes x1.5.', 'All', 'Shell petals open; core turns violet', 'Shell closes; next cycle'),
            ('Gravity Inversion', 'Phase 2+: floor and ceiling swap for 10 s every 70 s; only the 6 wall gravity pads are safe.', 'All', '3 s klaxon, pads light green', 'Fall into the core shaft = death'),
            ('Orbital Purge', 'Enrage at 9:00 in the boss room.', 'All', 'Purge countdown on HUD from 8:30', 'Wipe')],
      chal=('No Overcharge', 'Never hold more than 8 Conduit charges'), adds=[('ACT_RAID_CONDUIT', 6), ('ACT_REMNANT_SKIRMISHER', 4), ('ACT_REMNANT_HEAVY', 1)],
      approach=[('ACT_REMNANT_FODDER', 10), ('ACT_REMNANT_SHIELDBEARER', 3), ('ACT_REMNANT_ARTILLERY', 2), ('ACT_REMNANT_LEADER', 1)],
      mood='Black hull, white rim light from the planet below, violet core glow; vast and silent', boss_hp='348,000', kill='8-9 min'),
 dict(n=2, loc='LOC_END_RAID_02', name='The Archive Ring', boss='ACT_BOSS_ARCHIVIST', lvl=84, mins=35, add='ACT_RAID_INDEXWARDEN',
      nodes=[('Ring Dock', 'drop', 'CP', 'Anchor; the ring turns slowly overhead'),
             ('Rotating Stacks', 'traversal', '', 'Two parallel stack rings rotate 90 degrees every 30 s; each team of 3 presses 4 plates on its ring in the same 5 s window to open the hall door'),
             ('Reading Hall', 'adds', '', 'Choirborn and an Index Warden; the Warden\'s death drops the Reading Glass key'),
             ('Reading Room', 'gate', 'CP', 'Anchor; secret shelf puzzle for the wing chest (pull 3 books shown in the hall murals)'),
             ('The Index', 'boss', '', '60 m ring floor around a data well; 4 data cores on pillars at the compass points'),
             ('Stacks Exit', 'exit', '', 'Loot vault; lift to Wing 3')],
      mech=[('Reader', 'One player stands in the Reading Circle for 3 s to become the Reader (25 s). Only the Reader sees which of the 4 data cores shows the true glyph; the team must break that core (2.5x weak point). Breaking a wrong core triggers Purge Record.', '1 Reader + 5 damage', 'Reader sees glyphs over cores; others see blank cores', 'Purge Record: raid-wide Storm damage 60% of max HP'),
            ('Index Maze', 'Phase 2: the floor folds into a hedge of light walls for 30 s; 2 players inside must collect 3 key shards while the rest defend the boss\'s anchor.', '2 maze runners', 'Walls rise with a page-turn sound', 'Uncollected shard = Purge Record'),
            ('Recompile', 'Phase 3: every 40 s the Archivist copies the last-broken core; break it again within 10 s.', 'All', 'Core re-forms with a rising data chime', 'Boss heals 5%'),
            ('Total Recall', 'Enrage at 8:00.', 'All', 'Ring lights go red', 'Wipe')],
      chal=('Single Reader', 'The same player must be Reader for the whole fight'), adds=[('ACT_RAID_INDEXWARDEN', 1), ('ACT_CHOIRBORN_FODDER', 6), ('ACT_CHOIRBORN_SKIRMISHER', 3)],
      approach=[('ACT_CHOIRBORN_FODDER', 8), ('ACT_CHOIRBORN_SHIELDBEARER', 2), ('ACT_CHOIRBORN_ARTILLERY', 2), ('ACT_RAID_INDEXWARDEN', 1)],
      mood='Warm amber archive light inside a cold ring; floating text glyphs; quiet library tension', boss_hp='364,800', kill='7-8 min'),
 dict(n=3, loc='LOC_END_RAID_03', name="Meridian's Echo", boss='ACT_BOSS_MERIDIANGHOST', lvl=88, mins=58, add='ACT_RAID_GHOSTOFFICER',
      nodes=[('Echo Bridge', 'drop', 'CP', 'Anchor; the Meridian as it was before the crash, replayed in pale light'),
             ('Ghost Decks', 'traversal', '', 'Stealth decks: 8 Echo Sentries sweep light cones (12 m, 40 degrees). Being seen triggers an alarm wave and seals the deck for 60 s'),
             ('Mess Hall', 'adds', '', 'Holdout against 3 waves of ghost crew; Ghost Officer leads wave 3'),
             ('Bridge Approach', 'gate', 'CP', 'Anchor; the wing chest is in the captain\'s quarters behind a code from the Mess Hall logs'),
             ('The Bridge', 'boss', '', '50 x 40 m bridge deck; 3 stations (Helm, Comms, Reactor); 6 escape pods along the rear wall'),
             ('Bridge Exit', 'exit', '', 'Loot vault; ladder to Wing 4')],
      mech=[('Chain of Command', 'The Ghost is warded while any of 3 Ghost Officers (one per station) lives. The player who kills an officer gets Rank (40 s); only a player with Rank can damage the Captain\'s badge (x2.0).', '3 officer killers, 3 support', 'Officer nameplates show their station icon', 'Officers revive at 0:40 if the Ghost is not damaged'),
            ('Captain\'s Order', 'Marks 2 players; they must stand at opposite stations within 6 s.', 'Marked pair', 'Order glyph over the pair and their target station', 'Both marked players die'),
            ('Abandon Ship', 'Phase 2 at 65%: everyone must enter one of 6 escape pods within 8 s; each pod holds one player; then the deck is purged.', 'All', 'Siren, pod lights blink', 'Players outside a pod die'),
            ('Final Log', 'Enrage at 10:00.', 'All', 'Ship log voice counts down', 'Wipe')],
      chal=('Skeleton Crew', 'Kill all 3 officers within 10 s of each other each cycle'), adds=[('ACT_RAID_GHOSTOFFICER', 3), ('ACT_CHOIRBORN_FODDER', 6), ('ACT_CHOIRBORN_SKIRMISHER', 3)],
      approach=[('ACT_CHOIRBORN_FODDER', 12), ('ACT_CHOIRBORN_SKIRMISHER', 4), ('ACT_CHOIRBORN_HEAVY', 1), ('ACT_RAID_GHOSTOFFICER', 1)],
      mood="Faded blue ghost light over the Meridian's pre-crash bridge; grief and memory", boss_hp='381,600', kill='9-10 min'),
 dict(n=4, loc='LOC_END_RAID_04', name='The Unmade Choir', boss='ACT_BOSS_UNMADECHOIR', lvl=92, mins=47, add='ACT_RAID_CHORISTER',
      nodes=[('Quiet Nave', 'drop', 'CP', 'Anchor; the Quiet\'s heart, a cathedral of hull ribs'),
             ('Tuning Fork Bridge', 'traversal', '', 'Call and response: the bridge plays a 4 to 6 note phrase; players strike the matching chimes on 6 pylons; mistakes drop bridge segments'),
             ('Choir Loft', 'adds', '', 'Choristers buff all enemies in 15 m (+25% damage) until killed'),
             ("Conductor's Stair", 'gate', 'CP', 'Anchor; final refill; wing chest behind the organ pipes (hit 3 pipes in the bridge order)'),
             ('The Unmade Choir', 'boss', '', '70 m round stage; Treble and Bass halves on opposite rims; the Conductor floats at the centre'),
             ('The Last Vault', 'exit', '', 'Final loot; Ostra scene; BAN_RAID_DONE')],
      mech=[('Harmony', 'Treble and Bass must die within 10 s of each other or the survivor casts Revive Partner at full HP.', 'Two teams of 3', 'Linked health bars on HUD', 'Partner revived'),
            ('Dissonance', 'Every 35 s each player gets Treble or Bass tone; a player must stand within 6 m of an opposite-tone player when the 8 s timer ends.', 'Pairs', 'Tone icon over head, high or low hum', '45% max HP burst to anyone within 8 m'),
            ('Conductor', 'Phase 3: the Conductor (x2.0) is only damageable while both halves are stunned by Synced Slam parries (stance break both within 5 s).', '2 stance breakers', 'Conductor baton glows', 'No damage window'),
            ('Crescendo', 'Enrage at 10:00; also casts at 12% HP unless 3 players use a Resonance within 4 s.', 'Resonance holders', 'Choir swells; 4 s bar', 'Wipe')],
      chal=('Perfect Pitch', 'No Dissonance burst for the whole fight'), adds=[('ACT_RAID_CHORISTER', 4), ('ACT_CHOIRBORN_SKIRMISHER', 4), ('ACT_CHOIRBORN_HEAVY', 1)],
      approach=[('ACT_RAID_CHORISTER', 3), ('ACT_CHOIRBORN_FODDER', 8), ('ACT_CHOIRBORN_LEADER', 1), ('ACT_CHOIRBORN_HEAVY', 2)],
      mood='Bone-white ribs, black void, choir light in gold and violet; the game\'s most beautiful and frightening room', boss_hp='398,400', kill='9-10 min'),
]
RAID_ADDS = ['ACT_RAID_CONDUIT', 'ACT_RAID_INDEXWARDEN', 'ACT_RAID_GHOSTOFFICER', 'ACT_RAID_CHORISTER']

def raid_rows():
    PENDING.update(RAID_ADDS)
    maps, nodes, edges, encs, spawns, loot, cps, mechs, strs, cues = [], [], [], [], [], [], [], [], [], []
    for r in RAID:
        n = r['n']; key = f'RAID{n}'; b = r['boss'].replace('ACT_BOSS_', '')
        maps.append([r['loc'], 'Raid wing', r['name'], 'REG_Q', '6', r['lvl'], f"{r['mins']-8}-{r['mins']+8}", r['mins'],
                     'node graph', 'LGT_QUIET_INT', 'PPV_QUIET', r['mood'],
                     f'MUS_HUB_RAIDGATE (gate); MUS_MP_{key}_EXPLORE; MUS_BOSS_{b}_INTRO/P1/T2/P2/T3/P3/WIN',
                     f'SFX_MP_AMB_{key}', 'COOP_RAID_6 (no scaling)', 'Launch'])
        prev = None
        for i, (nm, kind, cp, desc) in enumerate(r['nodes'], 1):
            nid = f'{key}_N{i:02d}'
            nodes.append([nid, r['loc'], f'N{i:02d}', kind, nm, {'boss': '60x60', 'traversal': 'route'}.get(kind, '40x30'), cp, '', desc])
            if prev: edges.append([prev, nid, 'path' if kind != 'boss' else 'fog wall', {'traversal': 180, 'adds': 140, 'boss': 15}.get(kind, 40)])
            prev = nid
            if cp: cps.append([f'{key}_CP{i}', r['loc'], nid, 'Raid checkpoint', 'Wipe = encounter reset after 10 s, no Ember loss (06-endgame.md)', 'Saved per boss until weekly reset'])
        edges.append([f'{key}_N06', f'RAID{n+1}_N01' if n < 4 else 'REG_HUB', 'wing link' if n < 4 else 'return to Lantern Hold', 60])
        # encounters
        e = [(f'{key}_E1', f'{key}_N02', 'Traversal puzzle', r['nodes'][1][3], '', []),
             (f'{key}_E2', f'{key}_N03', 'Add encounter', r['nodes'][2][3], '', r['approach']),
             (f'{key}_E3', f'{key}_N05', 'Raid boss', f"{r['boss']} ({r['boss_hp']} HP, 3 phases BPH_{b}_1..3). Target kill {r['kill']}.", r['mech'][-1][1], [(r['boss'], 1)] + r['adds'])]
        for eid, node, kind, obj, rule, waves in e:
            encs.append([eid, r['loc'], node, kind, obj, rule, sum(c for _, c in waves)])
            for i, (act, c) in enumerate(waves, 1):
                tg = 'on enter' if i == 1 or kind != 'Raid boss' else ('every 60 s from phase 1 (cap 2x count alive)' if act != r['add'] else 'per mechanic cycle')
                spawns.append([eid, 1 if i == 1 else 2, act, c, r['lvl'], tg, f'{node}_SP{i}'])
        for i, (mn, rule, roles, tele, fail) in enumerate(r['mech'], 1):
            mid = f'MECH_{key}_{i:02d}'; PENDING.add(mid)
            mechs.append([mid, r['loc'], f'{key}_E3', mn, rule, roles, tele, fail, f'VFX_MP_{key}_M{i}', f'SFX_MP_{key}_M{i}', f'STR_MP_{mid}'])
            strs.append([f'STR_MP_{mid}', mn]); strs.append([f'STR_MP_{mid}_TIP', rule.split('.')[0] + '.'])
            cues.append([f'VFX_MP_{key}_M{i}', 'VFX', r['loc'], mn, tele])
            cues.append([f'SFX_MP_{key}_M{i}', 'SFX', r['loc'], mn, tele])
        mechs.append([f'MECH_{key}_CHAL', r['loc'], f'{key}_E3', 'Weekly challenge: ' + r['chal'][0], r['chal'][1], 'All', 'Challenge banner on raid HUD when featured (season_calendar raid_challenge)', 'Challenge failed, kill still counts', '', '', f'STR_MP_MECH_{key}_CHAL'])
        PENDING.add(f'MECH_{key}_CHAL'); strs.append([f'STR_MP_MECH_{key}_CHAL', r['chal'][0]])
        loot += [[f'{key}_E3', r['boss'], f'ITM_LT_BOSS_{36+n}', '100%', '2-3 rolls (x4 weight Rare+)', 'First kill per week; repeat kills 1 roll + Ember'],
                 [f'{key}_E3', r['boss'], f'ITM_SHB_W{6+n:02d}', '100%', '1', 'First kill per week (weekly Shardborn)'],
                 [f'{key}_E3', r['boss'], 'ITM_CUR_SEALS', '100%', str({1: 20, 2: 27, 3: 33, 4: 40}[n]), 'First kill per week; counts toward the 100 weekly cap (MPR-07)'],
                 [f'{key}_E3', r['boss'], 'ITM_MAT_STAR_01', '100%', '2', 'First kill per week'],
                 [f'{key}_N04', 'Wing secret chest', 'ITM_MAT_STAR_02', '100%', '1', 'Once per week'],
                 [f'{key}_N04', 'Wing secret chest', f'ITM_LT_BOSS_{36+n}', '100%', '1 roll', 'Once per week'],
                 [f'{key}_E3', 'Challenge reward', f'ITM_LT_BOSS_{36+n}', '100%', '1 extra roll', 'Featured challenge completed, once per week']]
        strs += [[f'STR_MP_{key}_NAME', r['name']], [f'STR_MP_{key}_DESC', f"Raid wing {n}. Level {r['lvl']}. Six players."]]
        cues += [[f'MUS_MP_{key}_EXPLORE', 'Music', r['loc'], 'N01-N04', 'Quiet motif, sparse choir and synth bed'],
                 [f'SFX_MP_AMB_{key}', 'Ambience', r['loc'], 'whole wing', r['mood']],
                 [f'VFX_MP_{key}_TRAV', 'VFX', r['loc'], 'E1', r['nodes'][1][0] + ' telegraphs']]
    for c in cues:
        if not c[0].startswith('MUS_BOSS'): PENDING.add(c[0])
    return maps, nodes, edges, encs, spawns, loot, cps, mechs, strs, cues

# ================================================================ ARENA 3v3
# Legend (cell = 2 m): # wall  o pillar  w glass (blocks move, not sight)  c low cover
# . floor  = raised +4 m  + raised +8 m  / ramp  ^ jump pad  ~ void or deep water (death)
# s shallow brine (slow 20%)  A team start  a respawn  P power pad  h health and ammo crate
# 1 2 3 control zones. Authored left half; right half is the left rotated 180 degrees
# (A->B, a->b, 1->3) so both teams get the same map.
ARENAS = [
 dict(id='ARENA_MP_01', name='Flight Deck', theme='LOC_HUB_PROVING', reg='REG_HUB', w=24, h=16, light='LGT_HUB_NIGHT', ppv='PPV_HUB',
      pads=['ITM_PWR_01', 'ITM_PWR_04'], style='Symmetric hangar, two levels; mid catwalk controls the power pad',
      mood='Night hangar under the Meridian bridge, sodium work lights, open bay to the stars', grid='''
a..c....=..
...##...=.c
A..#h...=..
a......./..
#..c...##.P
...o.....c.
..c...o...2
....1.c....
..##....c..
h.#...=....
a.....=..o.
..c...=....
.......#c..
a..c.......''') ,
 dict(id='ARENA_MP_02', name='Salt Pans', theme='LOC_POI_REG_02_14', reg='REG_02', w=38, h=24, light='LGT_REG_02_DAY', ppv='PPV_REG_02',
      pads=['ITM_PWR_05', 'ITM_PWR_02'], style='Open salt flats with brine lanes and three wreck islands; long mid lane for the sniper pad',
      mood='Blinding white salt, turquoise brine, rusted hull ribs; bright and exposed', grid='''
a...c.....sss.....
A.h..c....sss..c..
a....#.....s......
..c..#..c.........
.....#....ooo..c..
...c......o.o.....
..........ooo..P..
sss.....c.........
sss..c.......c....
.s.......1........
....#.c.......c...
....#.....ss......
.c..#.....ss.....2
......c...........
a........#..c.....
...c.....#........
.........#...ss...
a..c..........s...
h.......c.........
....c.......ss....
a.........c.......
..................''') ,
 dict(id='ARENA_MP_03', name='Redbark Mill', theme='LOC_POI_REG_03_07', reg='REG_03', w=30, h=20, light='LGT_REG_03_DUSK', ppv='PPV_REG_03',
      pads=['ITM_PWR_06', 'ITM_PWR_04'], style='Tight three-lane mill: water wheel lane, saw floor (mid), loft lane',
      mood='Red timber mill at dusk, sawdust in the light shafts, water wheel thunder', grid='''
a..#..........
A..#...c...##.
a..#.h.....#..
...........#.P
###..##c......
....o.....c...
..c...##......
.....1#....c.2
..#...#.......
..#.c.......##
..........c.#.
##..##...h..#.
a...#.........
...c#...c..o..
a.......#.....
...c....#..c..
a.......#.....
....c.........''') ,
 dict(id='ARENA_MP_04', name='Glass Lens', theme='LOC_POI_REG_04_21', reg='REG_04', w=42, h=18, light='LGT_REG_04_DAY', ppv='PPV_REG_04',
      pads=['ITM_PWR_05', 'ITM_PWR_01'], style='Long glass observatory: 80 m lens lane, glass walls block movement but not sight; flank tunnels under the dunes',
      mood='Glass dunes at noon, prisms throwing rainbow bands, a huge cracked lens at centre', grid='''
a.....c.........w...
A..h.....c......w...
a...######..........
..........#....c...P
..c...www.#.........
......w.......c.....
.......1..ww.......2
..c...........ww....
#####.....c.........
....#...c.......c...
a.......#####.......
...c....#.....c.....
a.....h.#...........
......c.......c.....
a...................
....c.......c.......''') ,
 dict(id='ARENA_MP_05', name='Bell Cloister', theme='LOC_POI_REG_05_14', reg='REG_05', w=20, h=20, light='LGT_REG_05_DUSK', ppv='PPV_REG_05',
      pads=['ITM_PWR_03', 'ITM_PWR_02'], style='Vertical cloister, 4 floors (ground, +4, +8, +12 bell deck); stairs at the corners, jump pads to the bell',
      mood='Snowbound abbey bell tower at dusk, candlelit galleries, the bell booms each minute', grid='''
a..c=====
A...=+++=
a.h.=+P+=
....=+++=
.c../...=
.......c.
..o..1...
.c....o.2
.../.....
=......c.
=.^..c...
=....../.
a.c......
....h..c.
a..../...
..c......
a........
.........''') ,
 dict(id='ARENA_MP_06', name='Lifted Steps', theme='LOC_POI_REG_06_28', reg='REG_06', w=30, h=30, light='LGT_REG_06_NIGHT', ppv='PPV_REG_06',
      pads=['ITM_PWR_06', 'ITM_PWR_02'], style='Floating rock platforms over the void, joined by bridges and jump pads; falling is death',
      mood='Rocks drifting upward through violet Shard light; the Hollowing made into a playground', grid='''
a..c..~~~~~~~~
A.h...~~~...~~
a....c~~~.P.~~
......^~~...~~
~~..~~~~~~.~~~
~~..~~~~~~.~~~
~~^.~~~...c..~
~~~~~~~.1....~
~~~~~~~..c...^
...c..~~~~~~~~
.h...^~~~~~~~~
a.....~~~..c..
...c..~~~....2
a.....~~~^....
~~.~~~~~~~~~~~
~~.~~~~...c.~~
~~^~~~~.....~~
~~~~~~~~^...~~
...c....~~~~~~
a.......~~~~~~
.....c..~~~~~~
a.......~~~~~~
...c....~~~~~~
.........~~~~~
...........~~~
..c..........~
...........c..
..............''') ,
 dict(id='ARENA_MP_S1', name='Undervault Sluice', theme='', reg='REG_U', w=26, h=20, light='LGT_UND', ppv='PPV_UND', season=1,
      pads=['ITM_PWR_02', 'ITM_PWR_04'], style='Season 1 map: flooded archive with a central sluice channel; gates on the channel open every 45 s, changing routes',
      mood='Teal emergency light, cable forests, rushing water under grates', grid='''
a...c......~
A.h....c...~
a.....##...~
...c..#....~
......#..P.=
.c.........~
....o..c...~
..1....../.~
......c....2
.##.....c..2
..#.......h~
a.#..c.....~
.......#...~
a..c...#..c=
.......#...~
a....c.....~
...........~
...c.......~''') ,
]
MIRROR = {'A': 'B', 'a': 'b', '1': '3'}

def build_grid(a):
    W, H, half = a['w'], a['h'], a['w'] // 2
    rows = [r for r in a['grid'].strip('\n').split('\n')]
    bad = [r for r in rows if len(r) > half - 1]
    assert not bad and len(rows) <= H - 2, (a['id'], bad[:2], len(rows))
    inner = [('#' + r.ljust(half - 1, '.')) for r in rows]
    while len(inner) < H - 2: inner.append('#' + '.' * (half - 1))
    left = ['#' * half] + inner + ['#' * half]
    g = []
    for r in range(H):
        right = ''.join(MIRROR.get(ch, ch) for ch in reversed(left[H - 1 - r]))
        g.append(left[r] + right)
    return g

BLOCK_SIGHT = set('#o'); BLOCK_MOVE = set('#ow~')

def los(g, p, q):
    (r0, c0), (r1, c1) = p, q
    n = max(abs(r1 - r0), abs(c1 - c0)) * 2 or 1
    for i in range(1, n):
        r = round(r0 + (r1 - r0) * i / n); c = round(c0 + (c1 - c0) * i / n)
        if g[r][c] in BLOCK_SIGHT: return False
    return True

def bfs(g, s):
    H, W = len(g), len(g[0]); dist = {s: 0}; q = deque([s])
    while q:
        r, c = q.popleft()
        steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if g[r][c] == '^':  # jump pad: 16 m launch in any direction
            steps += [(dr, dc) for dr in range(-8, 9) for dc in range(-8, 9) if (dr, dc) != (0, 0)]
        for dr, dc in steps:
            nr, nc = r + dr, c + dc
            if 0 <= nr < H and 0 <= nc < W and (nr, nc) not in dist and g[nr][nc] not in BLOCK_MOVE:
                dist[(nr, nc)] = dist[(r, c)] + 1; q.append((nr, nc))
    return dist

def clusters(g, ch):
    pts = [(r, c) for r, row in enumerate(g) for c, x in enumerate(row) if x == ch]
    if ch == '2' and pts: return [pts]
    out, seen = [], set()
    for p in pts:
        if p in seen: continue
        grp, st = [], [p]
        while st:
            q = st.pop()
            if q in seen: continue
            seen.add(q); grp.append(q)
            st += [x for x in pts if abs(x[0] - q[0]) <= 1 and abs(x[1] - q[1]) <= 1 and x not in seen]
        out.append(grp)
    return out

def arena_rows():
    maps, pts, sights, checks, strs, cues, layouts = [], [], [], [], [], [], []
    for a in ARENAS:
        g = build_grid(a); mid = a['id']; key = mid.replace('ARENA_MP_', 'PVP')
        PENDING.add(mid)
        layouts.append((a, g))
        maps.append([mid, 'Arena 3v3', a['name'], a['reg'], '6 (3v3)', 'Normalized 80; Ranked caps upgrades at +15', '8-10', 9,
                     f"{a['w']*CELL_M} x {a['h']*CELL_M} m", a['light'], a['ppv'], a['mood'],
                     f'MUS_HUB_ARENA_LOBBY (lobby); MUS_MP_{key}_MATCH; MUS_MP_PVP_FINAL', f'SFX_MP_AMB_{key}',
                     'None (PvP)', 'Season 1' if a.get('season') else 'Launch'])
        named = []
        def add(kind, ch, label):
            for i, grp in enumerate(clusters(g, ch), 1):
                r = sum(p[0] for p in grp) / len(grp); c = sum(p[1] for p in grp) / len(grp)
                r, c = min(((rr, cc) for rr in range(len(g)) for cc in range(len(g[0])) if g[rr][cc] not in BLOCK_MOVE),
                           key=lambda p: (p[0] - r) ** 2 + (p[1] - c) ** 2)  # snap to nearest walkable cell
                pid = f'{mid}_{label}{i}'; named.append((pid, kind, (r, c)))
                pts.append([pid, mid, kind, round(c * CELL_M + 1, 1), round(r * CELL_M + 1, 1),
                            {'=': 4, '+': 8}.get(g[round(r)][round(c)], 0), ''])
        add('Team A start', 'A', 'SPAWN_A'); add('Team B start', 'B', 'SPAWN_B')
        add('Team A respawn', 'a', 'RESP_A'); add('Team B respawn', 'b', 'RESP_B')
        add('Power weapon pad', 'P', 'PAD'); add('Health and ammo crate', 'h', 'CRATE')
        add('Control zone A side', '1', 'ZONE1'); add('Control zone centre', '2', 'ZONE2'); add('Control zone B side', '3', 'ZONE3')
        # assign power weapons: pads sorted by distance to centre; centre-most gets pads[0]
        H, W = len(g), len(g[0]); ctr = ((H - 1) / 2, (W - 1) / 2)
        padrows = [p for p in pts if p[1] == mid and p[2] == 'Power weapon pad']
        padrows.sort(key=lambda p: (p[4] / CELL_M - ctr[0]) ** 2 + (p[3] / CELL_M - ctr[1]) ** 2)
        for i, p in enumerate(padrows):
            p[6] = a['pads'][0]  # mirrored pair: same weapon both sides
        z2 = [p for p in named if p[1] == 'Control zone centre']
        if z2:
            pr, pc = z2[0][2]; pid = f'{mid}_PAD_C'
            named.append((pid, 'Power weapon pad', (pr, pc)))
            pts.append([pid, mid, 'Power weapon pad (centre, first spawn 2:00)', round(pc * CELL_M + 1, 1), round(pr * CELL_M + 1, 1), 0, a['pads'][1]])
        # Last Light: pads hold one random power weapon from round 3 (loops 06-endgame.md)
        # fairness and sightlines
        A = [p for p in named if p[1] == 'Team A start'][0][2]; B = [p for p in named if p[1] == 'Team B start'][0][2]
        dA, dB = bfs(g, A), bfs(g, B)
        for pid, kind, p in named:
            if kind in ('Power weapon pad', 'Control zone centre', 'Control zone A side', 'Control zone B side'):
                checks.append([mid, pid, 'path from A start (m)', dA.get(p, -1) * CELL_M, 'path from B start (m)', dB.get(p, -1) * CELL_M])
        reach = all(p in dA for _, _, p in named)
        checks.append([mid, 'ALL', 'every point reachable from A start', 'yes' if reach else 'NO', 'B start reachable', 'yes' if B in dA else 'NO'])
        resp_safe = sum(1 for pid, k, p in named if k == 'Team A respawn' and all(math.dist(p, q) * CELL_M >= 30 or not los(g, p, q) for _, k2, q in named if k2 == 'Team B respawn'))
        checks.append([mid, 'ALL', 'A respawns out of sight of, or 30 m+ from, every B respawn', resp_safe, 'of', sum(1 for _, k, _ in named if k == 'Team A respawn')])
        key_pts = [x for x in named if x[1] != 'Health and ammo crate']
        lines = []
        for i in range(len(key_pts)):
            for j in range(i + 1, len(key_pts)):
                (p1, k1, a1), (p2, k2, a2) = key_pts[i], key_pts[j]
                if los(g, a1, a2):
                    lines.append((round(math.dist(a1, a2) * CELL_M, 1), p1, p2))
        lines.sort(reverse=True)
        for L, p1, p2 in lines[:6]:
            tag = 'sniper lane' if L >= 50 else 'rifle lane' if L >= 25 else 'close'
            sights.append([mid, p1, p2, L, tag])
        strs += [[f'STR_MP_{mid}_NAME', a['name']], [f'STR_MP_{mid}_DESC', a['style'].split(';')[0] + '.']]
        cues += [[f'MUS_MP_{key}_MATCH', 'Music', mid, 'match start', 'Map theme, 128 bpm, intensity follows score gap'],
                 [f'SFX_MP_AMB_{key}', 'Ambience', mid, 'whole map', a['mood']]]
        for c in cues[-2:]: PENDING.add(c[0])
    return maps, pts, sights, checks, strs, cues, layouts

ARENA_MODES = [
 ['PVP_CLASH', 'Clash', 'Team kills', 'First to 30 kills', '8:00', 'Most kills at time; tie = sudden death, next kill wins (max 1:00, then draw)', '6 s', 'Lead of 20 ends the match (mercy)', 'Pads per map; first spawn 1:00; respawn per arena_power_weapons.csv respawn_s'],
 ['PVP_CONTROL', 'Control', '3 zones (ZONE1..3)', 'First to 150 points; each held zone scores 1 point every 2 s; kill = +1', '8:00', 'Most points at time; tie = overtime until a zone flips', '6 s', 'Capture 6 s alone, 4.5 s with 2, 3.5 s with 3; contested zones pause', 'Same as Clash'],
 ['PVP_LASTLIGHT', 'Last Light', 'Elimination', 'First to 4 round wins (best of 7)', '1:30 per round', 'At 1:00 ZONE2 lights; holding it 8 s wins the round; at 1:30 the team with more total HP wins', 'none', 'Revive a teammate by holding 4 s at their Shard (once per round each)', 'One random power weapon on ZONE2 pad from round 3 (06-endgame.md)'],
]
ARENA_RULES = [
 ['RULE_PVP_TONICS', 'Tonics', '3 per life (06-endgame.md)'],
 ['RULE_PVP_RESPAWN_PICK', 'Respawn choice', 'Pick the team respawn point with no enemy in line of sight and the largest distance to the nearest enemy; never within 12 m of an enemy'],
 ['RULE_PVP_SPAWN_FLIP', 'Spawn flip', 'If 2 enemies stand within 16 m of a team\'s respawn cluster for 5 s, that team spawns on the far-side cluster (Clash and Control only)'],
 ['RULE_PVP_POWER_ANNOUNCE', 'Power weapon call', 'UI_ANNOUNCE_POWER_WEAPON and VO 10 s before a pad spawns; pad shows a 10 s ring'],
 ['RULE_PVP_SURGE', 'Surge charge', 'Surge (super) charge rate x0.6 in Arena so each player gets about 2 per match'],
 ['RULE_PVP_RESONANCE', 'Resonances', 'Disabled in Arena (they bend the world, plan 3.4); Weave abilities on normal cooldowns'],
 ['RULE_PVP_OOB', 'Out of bounds', '5 s warning then death; void and deep water kill at once'],
 ['RULE_PVP_LEAVE', 'Leaving', '15 min queue lock; 3 in 24 h = 2 h (06-endgame.md)'],
 ['RULE_PVP_REWARD', 'Rewards', 'ITM_LT_ENDGAME_ARENA_WIN / _LOSS; 5 Seals win, 2 loss; 25% gear roll each match (endgame_activities.csv)'],
]

# ================================================================ main
def md_table(h, rows):
    return '| ' + ' | '.join(h) + ' |\n| ' + ' | '.join('---' for _ in h) + ' |\n' + ''.join('| ' + ' | '.join(str(x).replace('|', '/') for x in r) + ' |\n' for r in rows)

def main():
    s = strike_rows(); r = raid_rows(); ar = arena_rows()
    MH = ['map_id', 'type', 'name', 'region', 'players', 'level', 'target_min_range', 'target_min', 'size', 'light_id', 'ppv_id', 'mood', 'music', 'ambience', 'scaling', 'release']
    w('mp_maps.csv', MH, s[0] + r[0] + ar[0])
    w('mp_nodes.csv', ['node_id', 'map_id', 'node', 'kind', 'name', 'size_m', 'checkpoint', 'world_loc', 'description'], s[1] + r[1])
    w('mp_edges.csv', ['from_node', 'to_node', 'type', 'length_m'], s[2] + r[2])
    w('mp_encounters.csv', ['enc_id', 'map_id', 'node_id', 'kind', 'objective_or_mechanic', 'rule_or_timer', 'total_enemies'], s[3] + r[3])
    w('mp_spawns.csv', ['enc_id', 'wave', 'act_id', 'count', 'level', 'trigger', 'spawn_point'], s[4] + r[4])
    w('mp_loot.csv', ['source', 'what', 'item_id', 'chance', 'qty', 'rule'], s[5] + r[5])
    w('mp_checkpoints.csv', ['cp_id', 'map_id', 'node_id', 'kind', 'wipe_rule', 'refill'], s[6] + r[6])
    w('raid_mechanics.csv', ['mech_id', 'map_id', 'enc_id', 'name', 'rule', 'roles', 'telegraph', 'fail_result', 'vfx', 'sfx', 'string'], r[7])
    w('arena_points.csv', ['point_id', 'map_id', 'kind', 'x_m', 'y_m', 'z_m', 'power_weapon'], ar[1])
    w('arena_sightlines.csv', ['map_id', 'from_point', 'to_point', 'length_m', 'class'], ar[2])
    w('arena_checks.csv', ['map_id', 'point', 'check', 'value', 'check2', 'value2'], ar[3])
    w('arena_modes.csv', ['mode_id', 'name', 'objective', 'win', 'timer', 'time_or_tie', 'respawn', 'special', 'power_weapons'], ARENA_MODES)
    w('arena_rules.csv', ['rule_id', 'name', 'rule'], ARENA_RULES)
    allstr = s[7] + r[8] + ar[4] + [[f'STR_MP_{m[0]}_NAME', m[1]] for m in ARENA_MODES] + [[f'STR_MP_{m[0]}_WIN', m[3]] for m in ARENA_MODES]
    w('mp_strings.csv', ['str_id', 'en', 'max_chars'], [[k, v, math.ceil(len(v) * 1.4)] for k, v in allstr])
    allcues = s[8] + r[9] + ar[5] + [['MUS_MP_PVP_FINAL', 'Music', 'all arenas', 'last 60 s or match point', 'Shared tension layer'],
                                       ['VFX_MP_PAD_SPAWN', 'VFX', 'all arenas', 'power pad 10 s ring then spawn', 'Gold ring fills; beam on spawn'],
                                       ['SFX_MP_PAD_SPAWN', 'SFX', 'all arenas', 'power pad spawn', 'Rising chime + VO call'],
                                       ['VFX_MP_ZONE', 'VFX', 'all arenas', 'control zone state', 'Ring in team colour; contested = flicker'],
                                       ['VFX_MP_RESPAWN', 'VFX', 'all modes', 'player respawn', 'Shard re-forms in 0.8 s']]
    for c in allcues[-5:]: PENDING.add(c[0])
    w('mp_cues.csv', ['cue_id', 'kind', 'map', 'trigger', 'description'], allcues)
    PENDING.update(x[0] for x in allstr)
    # layouts
    os.makedirs(os.path.join(OUT, 'layouts'), exist_ok=True)
    for a, g in ar[6]:
        with open(os.path.join(OUT, 'layouts', a['id'] + '.txt'), 'w') as f:
            f.write(f"{a['name']} ({a['id']}), {a['w']*CELL_M} x {a['h']*CELL_M} m, cell = {CELL_M} m, north up\n")
            f.write('Legend: # wall, o pillar, w glass, c low cover, . floor, = +4 m, + +8 m, / ramp, ^ jump pad, ~ void or deep water, s brine, A/B starts, a/b respawns, P power pad, h crate, 1 2 3 zones\n\n')
            f.write('\n'.join(g) + '\n')
    # ------------------------------------------------ validation
    errs = []
    def chk(ref, where):
        if ref and ref not in KNOWN and ref not in PENDING: errs.append(f'{where}: unknown {ref}')
    for row in s[4] + r[4]: chk(row[2], 'spawns')
    for row in s[5] + r[5]: chk(row[2], 'loot')
    for row in s[0] + r[0] + ar[0]: chk(row[9], 'light'); chk(row[10], 'ppv')
    for row in s[1]: chk(row[7], 'node loc')
    for m in RAID: chk(m['loc'], 'raid loc'); chk(m['boss'], 'raid boss'); [chk(f"BPH_{m['boss'][9:]}_{i}", 'phase') for i in (1, 2, 3)]
    for a in ARENAS: [chk(p, 'pad') for p in a['pads']]; chk(a['theme'], 'theme')
    for c in allcues: chk(c[0], 'cue')
    for row in r[0]:
        for mus in re.findall(r'MUS_BOSS_\w+?_(?:INTRO)', row[12]): chk(mus, 'music')
    chk('UI_ANNOUNCE_POWER_WEAPON', 'rule'); chk('BAN_RAID_DONE', 'raid')
    with open(os.path.join(OUT, 'validation.txt'), 'w') as f:
        f.write(f'{len(errs)} errors\n' + '\n'.join(errs) + '\n')
        f.write(f'pending new IDs (requested in data-requests.csv): {len(PENDING)}\n')
    print(len(errs), 'errors'); print('\n'.join(errs[:30]))
    # ------------------------------------------------ docs
    doc = ['# Strikes (3 players, level 80)\n', 'Generated by tools/gen_mp.py from the tables in this folder. Structure from design/loops/06-endgame.md; all other values are design choices.\n']
    for st in STRIKES:
        doc.append(f"\n## {st['id']} {st['name']} ({st['reg']}, {st['mins']} min)\n\nMood: {st['mood']}. Light {st['light']}, {st['ppv']}.\n")
        doc.append(md_table(['node', 'name', 'cp', 'what happens'], [[n[2], n[4], n[6], n[8]] for n in s[1] if n[1] == f"LOC_MP_{st['id']}"]))
        doc.append('\nFlow: N01 > N02 > N03 > N04 > N05 > N06 > N07 > N08 > N09 > N10, with a one-way drop N07 > N05.\n\nEnemies:\n\n')
        doc.append(md_table(['encounter', 'wave', 'enemy', 'count', 'trigger'], [[x[0], x[1], x[2], x[3], x[5]] for x in s[4] if x[0].startswith(st['id'] + '_')]))
    open(os.path.join(OUT, '01-strikes.md'), 'w').write(''.join(doc))
    doc = ['# Raid: The Quiet (6 players, 4 wings)\n', 'Generated by tools/gen_mp.py. Boss levels, HP, phases and lockout come from data/ and design/loops; mechanics are design choices.\n']
    for m in RAID:
        key = f"RAID{m['n']}"
        doc.append(f"\n## Wing {m['n']}: {m['name']} (level {m['lvl']}, {m['mins']} min, {m['boss']})\n\nMood: {m['mood']}.\n\n")
        doc.append(md_table(['node', 'name', 'cp', 'what happens'], [[n[2], n[4], n[6], n[8]] for n in r[1] if n[1] == m['loc']]))
        doc.append('\nMechanics:\n\n' + md_table(['mechanic', 'rule', 'roles', 'telegraph', 'fail'], [[x[3], x[4], x[5], x[6], x[7]] for x in r[7] if x[1] == m['loc']]))
    open(os.path.join(OUT, '02-raid.md'), 'w').write(''.join(doc))
    doc = ['# Arena PvP 3v3\n', 'Generated by tools/gen_mp.py. Maps are point-symmetric (right half = left half rotated 180 degrees), so routes to pads and zones are equal for both teams; arena_checks.csv proves it.\n\n## Modes\n\n',
           md_table(['mode', 'win', 'timer', 'respawn', 'special'], [[m[1], m[3], m[4], m[6], m[7]] for m in ARENA_MODES]), '\n## Rules\n\n', md_table(['rule', 'what'], [[x[1], x[2]] for x in ARENA_RULES])]
    for a, g in ar[6]:
        doc.append(f"\n## {a['name']} ({a['id']}), {a['w']*CELL_M} x {a['h']*CELL_M} m\n\n{a['style']}. Mood: {a['mood']}. Power weapons: {', '.join(a['pads'])}.\n\n```\n" + '\n'.join(g) + '\n```\n\nLongest sightlines:\n\n')
        doc.append(md_table(['from', 'to', 'm', 'class'], [x[1:] for x in ar[2] if x[0] == a['id']]))
    open(os.path.join(OUT, '03-arena.md'), 'w').write(''.join(doc))
    return 1 if errs else 0

if __name__ == '__main__':
    sys.exit(main())
