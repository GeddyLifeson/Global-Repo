"""Hand-authored Cinderreach levels: prologue, Spine Keep, towns, Relay Tower, Choir site.

Node tuple: (key, name, type, "W x D x H m", elevation_rel_m, links, critical, notes)
links: "KEY:edge[value]; ..." where edge is walk, stairs, ladder, lift, drop, mantle, jump,
squeeze, door, locked, oneway, shortcut, fog, secret, climb, cable, rope. A key starting with @ is a
node in another level (full node id).
Encounter spec: world ENC_ id, or ("NEW", template, faction, "ACT_<ID> xN; ...", trigger, notes).
Loot spec: (container, contents, qty, visibility, notes).
"""

PROLOGUE_BAY9 = dict(
    lvl='LVL_R1_PRO_BAY9', loc='LOC_PRO_BAY9', kind='Prologue', name='Bay 9 Cryo Ward', level='1',
    layout='Linear tutorial corridor', time=(12, 15), quest='MQ_P_01',
    mood='Frozen dark ward; pod lights failing to red; frost on glass; the first warm light is the bay door',
    nodes=[
        ('A', 'Pod 9', 'START', '6 x 6 x 4', 0, 'B:walk', 'Y', 'Cold open CIN_OPEN ends here. Old Tomas pulls the player out; cryo scanner runs Origin pick (character creation).'),
        ('B', 'Ward Row', 'PATH', '60 x 8 x 5', 0, 'C:walk; D:walk', 'Y', 'Tutorial TUT move and camera. 40 frozen sleepers in pods; 3 pods flicker to draw the eye forward.'),
        ('D', 'Sleeper Tag Alcove', 'LORE', '5 x 4 x 4', 0, 'B:walk', 'Y', 'Dead sleeper tag pickup. Ostra first words: "Bay 9. You were not scheduled to wake." Required pickup gates the door.'),
        ('C', 'Ward Junction', 'COMBAT', '22 x 18 x 6', 0, 'E:walk; F:squeeze', 'Y', 'First fight: two Hollowed. Tutorials attack, dodge. Pod racks give 2 m high cover.'),
        ('E', 'Tonic Locker', 'LOOT', '4 x 3 x 3', 0, 'C:walk', 'Y', 'Crimson Tonic tutorial. Locker opens with one press; Tonic count 4.'),
        ('F', 'Frost Vent Squeeze', 'TRAVERSAL', '2.4 x 14 x 2.4', 0, 'G:walk', 'Y', 'Non-combat squeeze. Steam vent cycles 3 s on, 2 s off: teaches timing a dodge through hazards.'),
        ('G', 'Bay Door', 'EXIT', '6 x 6 x 6', 2, '@LVL_R1_PRO_SPINE_A:door', 'Y', 'Hatch opens on warm Ember light from the Spine. Load seam (streaming).'),
    ],
    enc={'C': [('NEW', 'ENT_TUTORIAL', 'FAC_HOLLOWED', 'ACT_HOLLOWED_FODDER x2', 'Scripted: wake when player passes pod 12', 'Damage x0.5 in prologue; cannot kill the player before the dodge prompt')]},
    loot={'E': [('Locker', 'ITM_CON_TNC_CRIMSON', 4, 'Path', 'Tonic flask, 4 charges')],
          'D': [('Pickup', 'LORE_CRYO', 1, 'Path', 'First Cryo Bay log in the region list')]},
)

PROLOGUE_SPINE = dict(
    lvl='LVL_R1_PRO_SPINE', loc='LOC_PRO_SPINE', kind='Prologue', name='The Spine', level='1-2',
    layout='Vertical climb with two loops', time=(20, 25), quest='MQ_P_02',
    mood='Inside the broken keel: tilted decks, ember light through hull cracks, ash falling in shafts',
    nodes=[
        ('A', 'Spine Hatch', 'ENTRY', '8 x 8 x 6', 0, 'B:walk', 'Y', 'Tomas leads. Ostra silent. Ash drifts in from cracks above: the way is up.'),
        ('B', 'Keel Climb', 'TRAVERSAL', '12 x 30 x 18', 4, 'C:ladder4; D:mantle1.5', 'Y', 'Teaches ladders and mantles (1.5 m then 2.0 m). Tomas waits at each ledge.'),
        ('C', 'Armory Wreck', 'LOOT', '14 x 10 x 5', 8, 'D:walk', 'Y', 'Salvaged pistol pickup; guard tutorial against a training dummy rig.'),
        ('D', 'Range Gallery', 'COMBAT', '40 x 12 x 8', 10, 'E:walk; H:secret', 'Y', 'Firearms tutorial: aim switches to first person; targets at 15, 25, 30 m. Three Hollowed walk in at 30 m.'),
        ('H', 'Cracked Locker Room', 'SECRET', '6 x 5 x 3', 10, 'D:walk', 'N', 'Breakable panel (hollow sound). Optional Common catalyst for non-casters to try Rites.'),
        ('E', 'Rite Shrine', 'TUTORIAL', '10 x 10 x 8', 14, 'F:walk', 'Y', 'Rite basics: Cast slot on a burning brazier, Ember Rite lights it. Opens the iris door.'),
        ('F', 'First Anchor', 'ANCHOR', '12 x 12 x 10', 16, 'G:walk; B:shortcut-drop5', 'Y', 'Light the first Anchor. Death and Ember tutorial (forced: a beam drops on the player after resting is taught). Drop back to Keel Climb is the first shortcut.'),
        ('G', "Officer's Deck", 'BOSS', '28 x 28 x 10', 20, 'I:walk', 'Y', 'Mini-boss: Hollowed crew officer in old uniform. Two telegraphed attacks, one grab. Ostra calls the Shard "mine" and goes quiet.'),
        ('I', 'Lower Door', 'EXIT', '10 x 6 x 8', 18, '@LVL_R1_LMK_01_A:door', 'Y', 'Door opens onto Cinderreach. Vista: Spine Keep on the far hills, Relay Tower mid-distance. Act 1 title card.'),
    ],
    enc={'D': [('NEW', 'ENT_TUTORIAL', 'FAC_HOLLOWED', 'ACT_HOLLOWED_FODDER x3', 'Scripted after the third target', 'Walk in a line at 30 m so the pistol works')],
         'G': [('NEW', 'ENT_MINIBOSS', 'FAC_HOLLOWED', 'ACT_HOLLOWED_HEAVY x1', 'Room entry; doors close (no fog gate)', 'Stand-in for the crew officer; data request for ACT_VAR_R1_07 Hollowed Deck Officer')]},
    loot={'C': [('Weapon rack', 'ITM_WPN_PST_01', 1, 'Path', 'Salvaged pistol from MQ_P_02'), ('Ammo box', 'ITM_AMO_COM', 60, 'Path', '')],
          'H': [('Locker', 'ITM_CAT_01', 1, 'Secret', '')],
          'G': [('Body', 'ITM_LT_HOLLOWED_LEADER', 1, 'Path', 'Officer drops leader table plus 200 Ember')]},
)

# Spine Keep: zones keyed by the world thread's zone names (design/world/citadel_zones.csv owns order,
# level, anchors and shortcuts). Node elevations are offsets on top of the zone's elevation_rel_m.
# '@{Zone name}_X' links to node X of another zone; '{anchor}' in notes is the zone's Anchor.
CITADEL_ZONES = {
 'Ash Road Approach': dict(mood='Pilgrim road lined with burned pyres; Spine Keep looms 133 m above; dusk haze', nodes=[
    ('A', 'Ash Road Anchor', 'ANCHOR', '14 x 14 x 8', 0, 'B:walk', 'Y', 'Anchor {anchor} under a toppled hull rib. First full view of the Keep.'),
    ('B', 'Pilgrim Road', 'PATH', '12 x 180 x 0', 2, 'C:walk', 'Y', 'Rising road between pyre stakes. Elite and escort walk down it.'),
    ('C', 'Pyre Field', 'COMBAT', '60 x 50 x 0', 4, 'D:walk; E:walk; F:climb', 'Y', 'Open field; pyre stacks are 2 m high cover every 10 m. Thorn barricade line at the far end.'),
    ('D', 'Cart Barricade', 'LOOT', '16 x 10 x 3', 4, 'C:walk', 'N', 'Wrecked supply wagons. Dead Hull Knight holds the Captain Cabin Key.'),
    ('E', 'Hull Plate Ramp', 'COMBAT', '20 x 90 x 0', 10, '@{Hullgate Barbican}_A:walk', 'Y', 'Gun line on the ramp; 40-90 m sightline up to the barbican; cover every 10 m.'),
    ('F', 'Ash Cliffs Trail', 'SECRET', '3 x 220 x 0', 12, '@LVL_R1_CON_02_A:walk', 'N', 'Cliff path around the Keep to the Saltmere gatehouse (GATE_01 side path; level 14 enemies past the midpoint).'),
 ]),
 'Hullgate Barbican': dict(mood='Black gatehouse of hull plate; murder holes glow with braziers; Hollowed nest (ash and rot)', nodes=[
    ('A', 'Hullgate Arch', 'ENTRY', '20 x 10 x 34', 0, 'B:walk', 'Y', 'Main gate shut; a fallen plate leaves a breach. Landmark LOC_LMK_REG_01_04 is this arch.'),
    ('B', 'Breach Crawl', 'TRAVERSAL', '2.4 x 18 x 2.4', 0, 'C:ladder6', 'Y', 'Non-combat squeeze, then a 6 m ladder up into the yard.'),
    ('C', 'Gatehouse Yard', 'COMBAT', '35 x 30 x 12', 6, 'D:stairs; G:walk; F:locked', 'Y', 'Hollowed nest; the leader stands on a cart. Kill it to break fodder.'),
    ('D', 'Murder Gallery', 'COMBAT', '4 x 40 x 4', 12, 'E:walk; H:walk', 'Y', 'Firing slits over the yard; 4 m walkway (melee minimum).'),
    ('E', 'Winch Room', 'SHORTCUT', '10 x 8 x 6', 12, '@{Ash Road Approach}_A:shortcut-gate', 'Y', 'Barbican winch raises the main gate back to the Ash Road Anchor.'),
    ('H', 'Side Postern', 'SHORTCUT', '3 x 6 x 3', 6, '@{Ash Road Approach}_C:shortcut-door', 'N', 'Postern door out to the Pyre Field (bar lifts from inside).'),
    ('F', "Captain's Cabin", 'LOOT', '8 x 8 x 4', 6, 'C:walk', 'N', 'LOC_DOOR_REG_01_01, key ITM_LOR_348. Captain log and a Relic.'),
    ('G', 'Stair Shaft', 'COMBAT', '8 x 8 x 14', 14, '@{Spinegate Bridge}_A:stairs', 'Y', 'Dark stairwell ambush; Glasscrawlers on the ceiling drop at 12 m.'),
 ]),
 'Spinegate Bridge': dict(mood="A hull bridge over a 70 m gorge; the Warden's gatehouse burns blue-white at the far end", nodes=[
    ('A', 'Antechamber Anchor', 'ANCHOR', '12 x 12 x 8', 0, 'B:walk; C:walk', 'Y', 'Anchor {anchor}; 54 m from the fog gate.'),
    ('B', 'Lift Hall', 'SHORTCUT', '6 x 6 x 28', 0, '@{Ash Road Approach}_A:shortcut-lift28', 'Y', 'Lift from the boss antechamber down to the Ash Road Anchor.'),
    ('C', 'Spinegate Fog', 'FOG', '4 x 2 x 4', 0, 'D:fog', 'Y', 'Fog gate 4 m wide, one-way while fighting.'),
    ('D', 'Spinegate Bridge', 'BOSS', '48 x 48 x 0', 0, 'E:walk', 'Y', 'ACT_BOSS_SPINEGATE. Stepped platform, 4 cover pieces. P2 opens gatehouse lanes (ARENA_SPINEGATE_P2). Slice ends here (plan 3.1).'),
    ('E', 'Bridge Far Side', 'REWARD', '20 x 14 x 6', 0, '@{Rampart Walk}_A:stairs; @LVL_R1_CON_02_A:walk', 'Y', 'Boss drop; the Warden\'s belt key ITM_LOR_355. Gatehouse road to Saltmere (GATE_01).'),
 ]),
 'Rampart Walk': dict(mood='Wind-blasted wall top; a lethal drop on the outside; ash gusts; ember sky', nodes=[
    ('A', 'Rampart Stair', 'TRAVERSAL', '6 x 30 x 14', 0, 'B:stairs', 'Y', 'Three switchback flights.'),
    ('B', 'Wall Walk', 'COMBAT', '5 x 120 x 0', 2, 'C:walk; H:walk', 'Y', 'Camp on the wall; artillery on towers; outer side is a lethal 30 m drop. Big-loop bridge from the Chapter Halls lands here.'),
    ('H', 'Rope Drop', 'SHORTCUT', '3 x 3 x 0', 2, '@{Hullgate Barbican}_C:shortcut-rope28', 'N', 'Rope down into the Gatehouse Yard.'),
    ('C', 'Broken Span', 'TRAVERSAL', '5 x 10 x 0', 4, 'D:jump2.5; D:mantle1.8', 'Y', 'Gap of 2.5 m and a 1.8 m mantle; ash gusts every 6 s push 0.5 m.'),
    ('D', 'Tower Ambush', 'COMBAT', '14 x 14 x 10', 6, 'E:locked; F:walk', 'Y', 'Briar Stalkers drop from the parapet.'),
    ('E', 'Signal Tower', 'LOOT', '8 x 8 x 12', 12, 'D:walk', 'N', 'LOC_DOOR_REG_01_08, key ITM_LOR_355. View back over the Spinegate Bridge.'),
    ('F', 'Gatehouse Roof', 'COMBAT', '24 x 24 x 0', 10, 'G:walk; @{Lower Bailey}_A:stairs', 'Y', 'Shield line. Ward-break lesson: the opposite element breaks Ward 3x faster.'),
    ('G', 'One-way Door', 'SHORTCUT', '3 x 3 x 3', 10, '@{Spinegate Bridge}_A:shortcut-oneway', 'Y', 'Opens down to the Antechamber Anchor.'),
 ]),
 'Lower Bailey': dict(mood='Bailey under smoke; Thorn raiders camp among cryo-pod chapels; cookfires', nodes=[
    ('A', 'Bailey Anchor', 'ANCHOR', '10 x 10 x 8', 0, 'B:walk', 'Y', 'Anchor {anchor} in a chapel niche built from cryo pods.'),
    ('B', 'Thorn Camp Court', 'COMBAT', '40 x 35 x 0', 0, 'C:walk; D:walk; F:drop5; I:walk', 'Y', 'Camp; leader at the cookfire.'),
    ('C', 'Strider Pens', 'LOOT', '20 x 12 x 5', 0, 'B:walk', 'N', 'Strider skeletons in stalls; small chest.'),
    ('I', 'Chain Gate', 'SHORTCUT', '6 x 4 x 6', 0, '@{Spinegate Bridge}_A:shortcut-gate', 'N', 'Chain gate opens a stair down to the Antechamber Anchor.'),
    ('D', 'Barracks Hall', 'COMBAT', '4 x 60 x 4', 2, 'E:walk; G:walk', 'Y', 'Close quarters: 4 m corridors, bunks as low cover.'),
    ('E', 'Ladder Drop', 'SHORTCUT', '4 x 4 x 14', 2, '@{Rampart Walk}_F:shortcut-ladder14', 'Y', 'Kick-down ladder to the Gatehouse Roof.'),
    ('F', 'Well Cistern', 'SECRET', '12 x 12 x 6', -5, 'B:ladder5', 'N', 'Drop down the well; Choir glyph and a lore page; ladder back up.'),
    ('G', 'Inner Gate Ground', 'COMBAT', '30 x 50 x 0', 4, 'H:walk; @{Reactor Undercroft}_A:stairs', 'Y', 'Killing ground under the inner wall; gun line on the wall.'),
    ('H', 'Hanged Knight', 'LOOT', '6 x 6 x 4', 4, 'G:walk', 'N', 'Hanged Hull Knight holds the Undercroft Key ITM_LOR_362.'),
 ]),
 'Reactor Undercroft': dict(mood="The Meridian's reactor bay under the Keep; cyan Shard light; steam; hum rising", nodes=[
    ('A', 'Coolant Stair', 'PATH', '6 x 40 x 14', 0, 'B:stairs', 'Y', 'Light shifts from fire orange to Shard cyan.'),
    ('B', 'Undercroft Anchor', 'ANCHOR', '10 x 10 x 6', 0, 'C:walk', 'Y', 'Anchor {anchor}.'),
    ('C', 'Pump Hall', 'COMBAT', '30 x 24 x 10', 0, 'D:walk; E:locked; H:walk', 'Y', 'Camp; steam vents cycle 3 s on and 3 s off (10 dmg/s).'),
    ('H', 'Flooded Tunnel', 'SHORTCUT', '3 x 80 x 3', -6, '@{Hullgate Barbican}_C:shortcut-door', 'N', 'Swim 25 m under a hull plate; opens a grate into the Gatehouse Yard.'),
    ('D', 'Reactor Trench', 'COMBAT', '12 x 70 x 8', 2, 'F:ladder8', 'Y', 'Horde pours from vents; burning floor patches (5 dmg/s).'),
    ('E', 'Cracked Containment', 'LORE', '10 x 10 x 8', 0, 'C:walk', 'N', 'LOC_DOOR_REG_01_15, key ITM_LOR_362. Meridian log on the core: "Somebody opened it." Hollowing motes.'),
    ('F', 'Cable Run', 'COMBAT', '3 x 60 x 0', 10, 'G:walk; @{Knight Chapter Halls}_A:stairs', 'Y', 'Ambush on 3 m catwalks (guns and spells, not greatswords).'),
    ('G', 'Plank Bridge', 'SHORTCUT', '3 x 12 x 0', 10, '@{Lower Bailey}_A:shortcut-bridge', 'Y', 'Drop-down plank becomes a bridge to the Bailey Anchor.'),
 ]),
 'Knight Chapter Halls': dict(mood="Burned chapter halls of the Hull Knights; scorched banners; Vael's sermons painted on the walls", nodes=[
    ('A', 'Chapter Gallery', 'PATH', '10 x 50 x 10', 0, 'B:walk; I:walk', 'Y', 'Banners of the old chapters burned to the pole.'),
    ('I', 'Service Lift', 'SHORTCUT', '4 x 4 x 14', 0, '@{Reactor Undercroft}_B:shortcut-lift14', 'N', 'Service lift to the Undercroft Anchor.'),
    ('B', 'Hall of Oaths', 'COMBAT', '18 x 60 x 14', 0, 'C:walk; D:ladder8', 'Y', 'Horde in a pillared hall; leader at the oath stone.'),
    ('C', 'Refectory', 'COMBAT', '24 x 20 x 8', 0, 'E:walk; F:locked', 'Y', 'Camp at long tables.'),
    ('D', 'Archive Loft', 'LORE', '14 x 10 x 6', 8, 'B:drop6', 'N', 'Pyre-Court sermons; lore and a catalyst.'),
    ('E', 'Drawbridge Winch', 'SHORTCUT', '10 x 8 x 6', 0, '@{Rampart Walk}_B:shortcut-bridge', 'Y', 'Lowers the bridge from the halls to the Wall Walk: the big loop.'),
    ('F', 'Reliquary', 'LOOT', '8 x 8 x 6', 0, 'C:walk', 'N', 'LOC_DOOR_REG_01_22 (key ITM_LOR_362). Relic armor piece.'),
    ('G', 'Pyre Stair', 'COMBAT', '12 x 40 x 14', 10, '@{The Ember Throne}_A:stairs', 'Y', 'Last defense line before the court.'),
 ]),
 'The Ember Throne': dict(mood="Vael's Pyre-Court: a round court open to the sky, effigies of burned villagers, a throne of hull ribs", nodes=[
    ('A', 'Court Anchor', 'ANCHOR', '10 x 10 x 6', 0, 'B:walk; F:walk', 'Y', 'Anchor {anchor}; 42 m from the fog gate.'),
    ('B', 'Effigy Hall', 'PATH', '10 x 30 x 12', 0, 'C:walk', 'Y', 'Quiet before the fight; effigies of villagers; no enemies.'),
    ('C', 'Pyre-Court Fog', 'FOG', '4 x 2 x 4', 0, 'D:fog', 'Y', 'Fog gate 4 m wide.'),
    ('D', "Vael's Pyre-Court", 'BOSS', '65 x 65 x 0', 0, 'E:walk', 'Y', 'ACT_BOSS_VAEL. Round court, 5 cover pieces. P3 edges burn (5 dmg/s). Strider not allowed.'),
    ('E', 'Heart Shard Altar', 'QUEST', '10 x 10 x 6', 2, 'F:walk', 'Y', 'MQ_A1_05 Heart Shard choice: Take or Spare. Ostra memory fragment 1 if taken.'),
    ('F', 'Throne Elevator', 'SHORTCUT', '6 x 6 x 98', 0, '@{Ash Road Approach}_A:shortcut-lift98', 'Y', 'Elevator from the seat down to the Ash Road Anchor (exit).'),
 ]),
}

CITADEL_EXTRA_ENC = {   # zone name, node: added so the path fills 2-3 hours; world gives 3 per combat zone
 ('Ash Road Approach', 'C'): [('NEW', 'ENT_PATROL', 'FAC_THORN', 'ACT_VAR_R1_02 x3; ACT_VAR_R1_04 x1', 'Sight 25 m', 'Walks the field edge')],
 ('Hullgate Barbican', 'D'): [('NEW', 'ENT_GUNLINE', 'FAC_HOLLOWED', 'ACT_HOLLOWED_ARTILLERY x2; ACT_VAR_R1_05 x1', 'Gallery entry', 'Shoots into the yard until engaged')],
 ('Lower Bailey', 'D'): [('NEW', 'ENT_AMBUSH', 'FAC_THORN', 'ACT_VAR_R1_04 x2; ACT_THORN_SKIRMISHER x1', '12 m volume at the bunk row', '')],
 ('Rampart Walk', 'B'): [('NEW', 'ENT_GUNLINE', 'FAC_THORN', 'ACT_THORN_ARTILLERY x2; ACT_VAR_R1_06 x1', 'Sight 60 m', 'Tower artillery')],
 ('Reactor Undercroft', 'C'): [('NEW', 'ENT_ELITE', 'FAC_HOLLOWED', 'ACT_HOLLOWED_HEAVY x1; ACT_VAR_R1_01 x2', 'Room entry', 'Heavy stays dead')],
 ('Knight Chapter Halls', 'B'): [('NEW', 'ENT_ELITE', 'FAC_THORN', 'ACT_THORN_HEAVY x1; ACT_VAR_R1_02 x2', 'Leader death', 'Heavy enters when the leader dies')],
 ('Knight Chapter Halls', 'G'): [('NEW', 'ENT_ELITE', 'FAC_THORN', 'ACT_THORN_HEAVY x1; ACT_THORN_LEADER x1; ACT_VAR_R1_06 x2', 'Stair midpoint', 'Pyre-Warden honor guard')],
}

CITADEL_LOOT = {
 ('Ash Road Approach', 'D'): [('Body', 'ITM_LOR_348', 1, 'Side', 'Captain Cabin Key'), ('Wagon', 'ITM_LT_SMALLCHEST_REG_01', 1, 'Side', '')],
 ('Hullgate Barbican', 'F'): [('Chest', 'ITM_SET_40_HEAD', 1, 'Locked', 'Dustwalker (Relic) helm'), ('Desk', 'LORE_ANY', 1, 'Locked', '')],
 ('Spinegate Bridge', 'D'): [('Boss', 'ITM_LT_BOSS_07', 1, 'Boss', 'Warden of Spinegate first-kill table')],
 ('Spinegate Bridge', 'E'): [('Boss belt', 'ITM_LOR_355', 1, 'Path', "Warden's belt key, opens the Signal Tower")],
 ('Rampart Walk', 'E'): [('Chest', 'ITM_SET_38_CHEST', 1, 'Locked', 'Cinder Warden (Rare) chest')],
 ('Lower Bailey', 'C'): [('Small chest', 'ITM_LT_SMALLCHEST_REG_01', 1, 'Side', '')],
 ('Lower Bailey', 'F'): [('Altar', 'LORE_ANY', 1, 'Secret', ''), ('Altar', 'ITM_MAT_DUST_01', 5, 'Secret', 'Shard Dust')],
 ('Lower Bailey', 'H'): [('Body', 'ITM_LOR_362', 1, 'Side', 'Undercroft Key, opens doors 15 and 22')],
 ('Reactor Undercroft', 'E'): [('Console', 'LORE_ANY', 1, 'Locked', '')],
 ('Knight Chapter Halls', 'D'): [('Shelf', 'LORE_ANY', 1, 'Side', ''), ('Lectern', 'ITM_CAT_04', 1, 'Side', '')],
 ('Knight Chapter Halls', 'F'): [('Reliquary', 'ITM_SET_40_CHEST', 1, 'Locked', 'Dustwalker (Relic) chest')],
 ('The Ember Throne', 'D'): [('Boss', 'ITM_LT_BOSS_01', 1, 'Boss', 'Vael first-kill table; guaranteed Shardborn (data/README choice 9)')],
}

TOWNS = {
 'LOC_TOWN_REG_01_01': dict(name='Emberwatch', layout='Hub with spokes', time=(15, 30), quest='MQ_A1_01 MQ_A1_02',
   mood='Brick kilns glowing day and night; soot-black roofs; people watch the hills for Vael\'s smoke',
   nodes=[
    ('A', 'Road Gate', 'ENTRY', '8 x 6 x 6', 0, 'B:walk', 'Y', 'Palisade of hull ribs; two militia NPCs; town music fades in at 60 m.'),
    ('B', 'Kiln Square', 'HUB', '40 x 40 x 0', 0, 'C:walk; D:walk; E:walk; F:walk; G:walk; H:walk; I:walk', 'Y', 'Anchor LOC_ANC_REG_01_07 by the well. Notice board for radiant bounties.'),
    ('C', 'Smithy', 'VENDOR', '12 x 10 x 6', 0, 'B:walk', 'N', 'Smith (upgrades, Common weapons). Data request for the smith NPC.'),
    ('D', "Reeve's Hall", 'QUEST', '16 x 12 x 8', 2, 'B:walk', 'Y', 'Reeve Annik: MQ_A1_01 giver. Hall fills with survivors after the hamlet fight (count shapes population).'),
    ('E', 'The Kilns', 'QUEST', '30 x 20 x 10', 0, 'B:walk; J:walk', 'Y', 'Kessa Vane (ACT_CMP_C1) hides in kiln 3. MQ_A1_02 fight with her old squad here.'),
    ('F', 'Trader Stop', 'VENDOR', '10 x 8 x 4', 0, 'B:walk', 'N', 'ACT_NPC_VEN_TRADER_REG_01 when on route (72 h restock).'),
    ('G', 'Ember Shrine', 'LORE', '8 x 8 x 8', 2, 'B:walk', 'N', 'Lantern Church shrine; ship-log scripture; lore item.'),
    ('H', 'Watch Platform', 'VISTA', '6 x 6 x 14', 14, 'B:ladder14', 'N', 'Watch platform over the town. Shows Kiln Ruin (the hamlet) smoke at dusk.'),
    ('I', 'Refugee Camp', 'SOCIAL', '24 x 18 x 0', 0, 'B:walk', 'N', 'Tents fill after MQ_A1_01 (0, 6 or 12 survivors).'),
    ('J', 'Kiln Pits', 'LORE', '14 x 10 x 6', -6, 'E:stairs', 'N', 'Lore site LOC_SITE_REG_01_19 in the clay pits.'),
   ],
   enc={'E': [('NEW', 'ENT_QUEST', 'FAC_HULLKNIGHTS', 'ACT_NPC_PYREWARDEN x4', 'MQ_A1_02 step: squad arrives', 'Skip with Speech 25 or Hull Knight Friendly. Data request: Pyre-Warden NPC combat actor')]},
   loot={'G': [('Shrine', 'LORE_ANY', 1, 'Side', '')], 'J': [('Pit', 'LORE_SITE19', 1, 'Side', '')]}),
 'LOC_TOWN_REG_01_02': dict(name='Cinder Hollow', layout='Linear across a ford', time=(10, 20), quest='',
   mood='Grey water choked with ash; a rope ferry; stilt houses; fishermen pulling hull scrap from the silt',
   nodes=[
    ('A', 'West Bank', 'ENTRY', '20 x 10 x 0', 0, 'B:walk', 'Y', 'Anchor LOC_ANC_REG_01_08 under the ferry tower.'),
    ('B', 'Ferry Winch', 'TRAVERSAL', '8 x 30 x 0', -2, 'C:walk', 'Y', 'Rope ferry across 30 m of ash water; 20 s crossing; Strider can wade at the shallows 200 m north.'),
    ('C', 'Stilt Row', 'HUB', '30 x 20 x 4', 2, 'D:walk; E:walk; F:ladder4', 'Y', 'Stilt houses; quest givers for radiant salvage runs.'),
    ('D', 'Salvage Tables', 'VENDOR', '10 x 8 x 4', 2, 'C:walk', 'N', 'Hull Scrap buy-back and Tinker basics (data request for the vendor).'),
    ('E', 'Silt Pens', 'LORE', '10 x 10 x 2', -1, 'C:walk', 'N', 'Lore site LOC_SITE_REG_01_20.'),
    ('F', 'Lookout Loft', 'VISTA', '6 x 6 x 10', 10, 'C:ladder4', 'N', 'View south to the Cinder Stair (one-way to Rimefall).'),
   ],
   enc={}, loot={'E': [('Silt', 'LORE_SITE20', 1, 'Side', '')], 'F': [('Crate', 'ITM_LT_SMALLCHEST_REG_01', 1, 'Side', '')]}),
 'LOC_TOWN_REG_01_03': dict(name="Wreckers\' Rest", layout='Loop through a hull section', time=(10, 20), quest='',
   mood='Salvager town inside a tipped hull section; sparks, cutting torches, hammock streets on cables',
   nodes=[
    ('A', 'Cargo Ramp', 'ENTRY', '12 x 20 x 8', 0, 'B:walk', 'Y', 'Anchor LOC_ANC_REG_01_09 at the ramp foot.'),
    ('B', 'Hold Market', 'HUB', '36 x 24 x 14', 2, 'C:walk; D:walk; E:ladder6', 'Y', 'Market in the cargo hold; Salvagers\' Guild contact (faction intro).'),
    ('C', 'Cutting Floor', 'VENDOR', '20 x 14 x 8', 2, 'B:walk', 'N', 'Tinker vendor: gadgets and ammo; Skimmer parts.'),
    ('D', "Guild Bunk", 'QUEST', '10 x 8 x 4', 2, 'B:walk', 'N', 'Salvagers\' Guild questline start.'),
    ('E', 'Cable Streets', 'TRAVERSAL', '4 x 60 x 0', 8, 'B:drop6', 'N', 'Hammock walkways on cables; loop back to the market.'),
   ],
   enc={}, loot={'E': [('Hammock', 'ITM_LT_SMALLCHEST_REG_01', 1, 'Side', '')]}),
}

RELAY = dict(lvl='LVL_R1_RELAY', layout='Vertical climb (3 stages)', time=(8, 10), quest='MQ_RT_01',
  mood='An 80 m escape-pod beacon tower of hull ribs; its dead lamp turns Ostra-blue when lit',
  nodes=[
    ('A', 'Beacon Base', 'ANCHOR', '16 x 16 x 6', 0, 'B:mantle2', 'Y', 'Anchor LOC_ANC_REG_01_06. Ostra: "These towers were ours."'),
    ('B', 'Ledge Stage', 'TRAVERSAL', '8 x 8 x 26', 26, 'C:mantle2', 'Y', 'Stage 1: 13 mantles of 2.0 m on painted hull stencils.'),
    ('C', 'Lift Stage', 'TRAVERSAL', '6 x 6 x 30', 56, 'D:lift30', 'Y', 'Stage 2: restart the lift (route power through one panel).'),
    ('D', 'Ladder Stage', 'TRAVERSAL', '3 x 3 x 20', 76, 'E:ladder20', 'Y', 'Stage 3: 20 m ladder in the wind.'),
    ('E', 'Beacon Top', 'COMBAT', '14 x 14 x 0', 80, 'F:walk; A:shortcut-rope80', 'Y', 'Small fight at the top; rope slide back to the base (shortcut).'),
    ('F', 'Beacon Lamp', 'QUEST', '6 x 6 x 4', 80, 'E:walk', 'Y', 'Map reveal; Ostra scene; region map fills.'),
  ],
  enc={'E': [('NEW', 'ENT_AMBUSH', 'FAC_HOLLOWED', 'ACT_VAR_R1_03 x3; ACT_HOLLOWED_ARTILLERY x1', 'Top reached', 'Glasscrawlers climb up after the player')]},
  loot={'F': [('Beacon', 'ITM_LT_SMALLCHEST_REG_01', 1, 'Path', '')]})

CHOIR = dict(lvl='LVL_R1_CHOIR', layout='Three-room trial', time=(12, 15), quest='',
  mood='A sealed glass hall under the plain; Shard tones ring when walked; no fire, only cold cyan light',
  nodes=[
    ('A', 'Hidden Entrance', 'ENTRY', '4 x 4 x 4', -6, 'B:walk', 'Y', 'Shows only after a Shard-note hint or an Ostra line within 40 m. Anchor LOC_ANC_REG_01_30.'),
    ('B', 'Hall of Echoes', 'PUZZLE', '20 x 20 x 10', -10, 'C:walk', 'Y', 'Follow the tone: floor plates ring; walk the 5-note phrase heard at the door.'),
    ('C', 'Glass Bridge', 'TRAVERSAL', '3 x 30 x 0', -10, 'D:walk', 'Y', 'Invisible bridge appears one plate ahead while the player hums (hold Interact).'),
    ('D', 'Trial Chamber', 'COMBAT', '24 x 24 x 10', -12, 'E:walk', 'Y', 'Trial fight.'),
    ('E', 'Choir Heart', 'REWARD', '10 x 10 x 12', -12, 'A:shortcut-lift12', 'Y', 'Grants RES_SHARDWALL. Lift back up to the entrance.'),
  ],
  enc={'D': ['ENC_0103']}, loot={'E': [('Choir Heart', 'RES_SHARDWALL', 1, 'Path', 'Resonance')]})

HAMLET = dict(name='Kiln Ruin (campaign: Tallow Hamlet)', quest='MQ_A1_01', mood='A hamlet of six cottages on fire; Pyre-Wardens herd villagers; the Anchor stone sits in the far field',
  nodes=[
    ('A', 'Hamlet Lane', 'ENTRY', '8 x 80 x 0', 0, 'B:walk; C:walk', 'Y', 'Choice point: villagers (left) or the Anchor (right).'),
    ('B', 'Burning Green', 'COMBAT', '40 x 40 x 0', 0, 'A:walk', 'N', 'Save the people: 3 waves.'),
    ('C', 'Anchor Field', 'ANCHOR', '30 x 30 x 0', 2, 'A:walk', 'N', 'Save the Anchor: one wave, unlocks fast travel early.'),
  ],
  enc={'B': [('NEW', 'ENT_WAVES', 'FAC_HULLKNIGHTS', 'ACT_NPC_PYREWARDEN x3; ACT_NPC_PYREWARDEN x4; ACT_NPC_PYREWARDEN x5', 'MQ_A1_01 choice: people', '3 waves; 12 villagers, each Pyre-Warden alive 20 s burns one')],
       'C': [('NEW', 'ENT_WAVES', 'FAC_HULLKNIGHTS', 'ACT_NPC_PYREWARDEN x4', 'MQ_A1_01 choice: Anchor', 'One wave')]})
