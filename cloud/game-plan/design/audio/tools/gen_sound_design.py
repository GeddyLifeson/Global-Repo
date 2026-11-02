#!/usr/bin/env python3
"""Shardfall sound design: sonic identity, layered recipes, readability rules,
mix priority, music stems and region ambience beds. Reads game data read-only.
Run from game-plan/: python3 design/audio/tools/gen_sound_design.py"""
import csv, os

GP = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
OUT = os.path.join(GP, 'design', 'audio')
D = os.path.join(GP, 'data')

def rd(p):
    with open(os.path.join(D, p), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def wr(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print(f'{name}: {len(rows)} rows')

# ======================================================== 1. sonic identity
# id, subject, core idea, signature layers, frequency home, always, never, sample
ID = [
 ('SID_SHARD', 'Shard magic (all Weave casting)', 'Glass that sings. Every Shard sound starts as struck or bowed crystal and blooms into a faint choir formant, because Shards are fused reactor glass that the Weave learned to sing through.',
  'Bowed crystal bowl / wine-glass rub; struck glass harmonica; formant-filtered choir "ah" pad; ring modulator at the region key root; reactor hum underneath (60 Hz family, never pure 60)',
  '1.2-6 kHz shimmer, 200-400 Hz formant body', 'Pitch every cast to the current region mode (6 key variants)', 'Never use generic "magic whoosh" libraries or reversed cymbals as the main layer', 'shard_cast_bloom.wav'),
 ('SID_EMBER_CUR', 'Ember (the currency, carried in the chest Shard)', 'A warm heartbeat of light. Picking Ember up should feel like a pulse joining your own; losing it should feel like a pulse going missing.',
  'Soft felt-mallet celesta + glass tick; a low "thum" (55-70 Hz, 80 ms) like a heartbeat; ember crackle grains; pitch climbs a pentatonic step per pickup inside a 1.5 s window', '55-70 Hz thump, 2-5 kHz chime', 'Chain pickups climb in pitch (max 8 steps) then reset', 'Never a coin or cash-register sound', 'ember_pickup.wav'),
 ('SID_WARD', 'Ward (blue energy layer over health)', 'A held breath of glass and current. Ward sounds glassy while healthy, crackles as it thins, and breaks with a shatter the whole mix makes room for.',
  'Hit: bright glass tink + electric sizzle (pitched up as Ward drops); Low (<25%): fizzing crackle bed + faint 2-tone flutter; Break: glass shatter + sub drop 120 to 35 Hz + air-pressure whump + 300 ms world high-cut; Recharge: rising filtered sweep over 1.2 s ending in a clean bell at full', 'Hits 2-8 kHz, break sub 35-120 Hz', 'Break and full-recharge always audible over everything except boss telegraphs', 'Never reuse the player Ward break for enemy Wards: enemy break is lower, shorter, panned to source', 'ward_break.wav; ward_recharge.wav'),
 ('SID_BREATH', 'Breath (stamina)', 'Your body, not a UI. Breath is told with vocal efforts and lungs.', 'Effort vocal per action (from player voice set A/B); rising breath rate as Breath drops; empty = ragged inhale + 120 ms dropout of player weapon sounds', 'Voice band 150 Hz-4 kHz', 'Empty-Breath sound fires once per empty, never loops', 'Never a beep or meter tick', ''),
 ('SID_HEALTH', 'Health and Tonics', 'Wet, physical, close.', 'Hurt: body-impact thud + cloth + vocal; low health (<25%): muffled world (low-pass 2.5 kHz), slow heartbeat 50 bpm, tinnitus 6 kHz sine at -36 dB; Tonic: cork pop, glass gulp, warm swell', 'Heartbeat 40-90 Hz', 'Low-health filter releases over 1.5 s after healing', 'Never stack heartbeat with Hush pressure; Hush wins', ''),
 ('SID_HUSH', 'Hush (the mind of the Quiet)', 'A crowd that agrees with itself. Hush is many whispering voices saying the same words a hair out of sync, always "we", calm and close, coming from everywhere at once.',
  '8-24 whisper takes of the Hush actor, each delayed 5-40 ms and detuned +/-15 cents; formant shift -2 semitones; 18-25 Hz pressure tone (felt on subs, -30 dB on stereo); pre-roll: world ambience sucked out with a 600 ms reverse-reverb inhale; G whole-tone shimmer pad', 'Whisper band 2-9 kHz, pressure 18-25 Hz', 'Diffuse (ambisonic, no point source) unless speaking through a Hollowed mouth or Choir lens: then point source dry + diffuse wet', 'Never loud. Hush is mixed at speech level and the world gets quieter instead', 'hush_whisper.wav'),
 ('SID_OSTRA', 'Ostra (ship mind in the chest Shard)', 'A voice inside your sternum. Starts broken, ends whole.', 'Dry actor read; runtime chain by Ostra_Memory 0-5: 0 = 300-3k band-pass, 8-bit crush, dropouts; 2 = 200-5k, light crush; 4 = full range, chest resonance (180 Hz peak); 5 = full range plus a subtle second "true" voice under it', 'Voice band, chest resonance 150-220 Hz', 'Mono, centred, never spatialised (she is inside you)', 'Never reverb from the room the player stands in', 'ostra_glitch.wav'),
 ('SID_MERIDIAN', 'Meridian technology (ship salvage, Remnant, firearms, vehicles)', 'Old machines that still want to work.', 'Servo whine, relay clicks, capacitor charge, hydraulic hiss, hull-metal groans, data chirps; everything slightly worn (wow and flutter, dust crackle)', 'Servo 1-4 kHz, hull 40-200 Hz', 'Every Meridian sound gets one "age" layer (rattle, grit, flutter)', 'Never clean modern sci-fi UI blips', ''),
 ('SID_WEAVE', 'The Weave (nature, the living field)', 'The world breathing in a key.', 'Wind tones, wood creaks, insects and birds tuned loosely to the region mode; Weave hum near Shards and Anchors', 'Full range', 'Weave hum always in the region key', '', 'anchor_lit.wav'),
 ('SID_ELEM_EMBER', 'Element: Ember (fire)', 'Forge, not campfire.', 'Bellows whoomp, forge roar, molten drip sizzle, hot metal tick; Burn status = crackle grains on the target', '80-400 Hz roar, 3-8 kHz crackle', '', 'Never generic campfire loops', ''),
 ('SID_ELEM_STORM', 'Element: Storm', 'A static charge that wants to jump.', 'Tesla-coil buzz, snap, thunder clap layered with ship capacitor discharge; Shock status = intermittent zaps on the target', '2-10 kHz snaps, 50-120 Hz thunder', '', '', ''),
 ('SID_ELEM_HOLLOW', 'Element: Hollow', 'Sound being taken away.', 'Reverse swells, spectral freeze, gated vacuum, a "suck" that removes high end from nearby sounds; Drain status = low pulse pulling toward caster', 'Removes 3-10 kHz locally', 'Hollow ducks nearby SFX by 3 dB in a 4 m radius', '', ''),
 ('SID_ELEM_FROST', 'Element: Frost', 'Ice under pressure.', 'Ice creak, crystallising crackle, glass chime, cold wind breath; Slow status = slowed-down copies of the target footsteps; Shatter combo = big glass burst', '1-6 kHz crackle', '', '', ''),
 ('SID_ELEM_BLOOM', 'Element: Bloom', 'Growth you can hear.', 'Root creak, wet tearing fibre, seed-pod pops, leaf rustle swells, wooden flute breath; Root status = creaking binds', '150 Hz-3 kHz', '', '', ''),
 ('SID_ELEM_IRON', 'Element: Iron', 'Weight and rivets.', 'Anvil strike, rivet gun, chain rattle, heavy plate clang, magnetic hum', '100 Hz-2 kHz', '', '', ''),
]
FACTION_ID = {
 'FAC_HULLKNIGHTS': ('Hull Knights', 'Salvaged hull plate armour: deep plate clanks, rivet rattles, a ship bell motif in their hall; disciplined unison shouts'),
 'FAC_LANTERNCHURCH': ('Lantern Church', 'Ship logs read as scripture: chanted log entries, censer chains, bridge-console chimes reused as liturgical bells'),
 'FAC_SALVAGERS': ("Salvagers' Guild", 'Tools and trade: ratchets, cutting torches, coin-like Hull Scrap clinks, haggling walla, whistled signals'),
 'FAC_QUIETHAND': ('Quiet Hand', 'Assassins: near silence, cloth over leather, a single muffled click before a strike; their invasion horn is a breath through a bone flute'),
 'FAC_CHOIR': ('The Choir', 'Mages who hear the Shards: sustained sung tones that match the region key, glass resonance, overtone singing'),
 'FAC_HOLLOWED': ('Hollowed (enemy)', 'Shard-sick bodies: wet breath, glass grinding in joints, broken speech fragments, Hush whisper bleed when a leader is near'),
 'FAC_REMNANT': ('Remnant (enemy)', 'Crashed-ship drones: servo whine, coolant hiss, targeting chirps, radio-squelch callouts read by an actor and processed'),
 'FAC_THORN': ('Thorn Clans (enemy)', 'Raiders: bone and wood, war whoops, horn calls, briar rattle on armour, heavy breathing berserkers'),
 'FAC_CHOIRBORN': ('Choirborn of the Quiet (enemy)', 'Elite sung chant in Hush harmony (G whole-tone), teleport = choir inhale + glass pop, counter-cast = reversed chord'),
}
for fid, (n, d) in FACTION_ID.items():
    ID.append((f'SID_{fid[4:]}', 'Faction: ' + n, d.split(':')[0] + '.', d, '', 'Faction leitmotif instrument appears in faction foley sweeteners', '', ''))
wr('sonic_identity.csv', ['sid', 'subject', 'core_idea', 'signature_layers', 'frequency_home', 'always', 'never', 'sample'], ID)

# ======================================================== 2. layered recipes
R = []  # rec_id, family, ref, name, transient, body, tail, mechanical, distance, indoor, processing, readability, sample
def rec(rid, fam, ref, name, tr, body, tail, mech, dist, ind, proc, read, sample=''):
    R.append([rid, fam, ref, name, tr, body, tail, mech, dist, ind, proc, read, sample])

# --- melee classes (weight sets everything: bigger = lower, longer, more pre-swing)
MELEE = {
 'STS': ('Straight Sword', 'Tight steel "shing" on draw; impact: 2 ms metal tick + flesh slap', 'Mid whoosh 300-900 Hz, 180 ms', 'Short ring 200 ms', 'Crossguard rattle, scabbard leather', 'Dark Souls straight sword: dependable, mid-weight'),
 'CRV': ('Curved Sword', 'Thin bright slice transient, high whistle on swing', 'Fast whoosh 500-1.5k Hz, 120 ms', 'Short airy tail', 'Ring-mail jingle on wielder', ''),
 'GRS': ('Greatsword', 'Heavy wind-up drag (scrape on stone if blade dips), impact: chunky metal + bone crunch', 'Low whoosh 120-500 Hz, 350 ms', 'Long ring 600 ms, sub thud on ground hits', 'Grip creak, armour shift', 'Wind-up audible 300 ms before active frames'),
 'AXE': ('Axe', 'Chop transient: wood handle knock + bit bite', 'Mid whoosh, slightly pitched', 'Short wooden rattle', 'Haft creak', ''),
 'HMR': ('Hammer', 'Blunt crack, no ring', 'Low thump whoosh', 'Dull thud decay', 'Head rattle on haft', 'Blunt hits boom, they do not ring'),
 'POL': ('Polearm', 'Long thin swish, spear-point "tsk" on thrust', 'Long whoosh with doppler on sweeps', 'Haft vibration 150 ms', 'Haft knocks against armour', ''),
 'FST': ('Fist', 'Knuckle leather pop + body thud', 'Very short whoosh', 'None', 'Wrap creak, gauntlet plates', 'Fastest, tightest sounds in the game'),
 'DGR': ('Dagger', 'Needle tick, wet stab', 'Tiny fast whoosh', 'None', 'Sheath snap', 'Backstab adds a held-breath silence 80 ms then a deep thud'),
 'SHD': ('Shield', 'Bash: plate boom + body grunt; block: material-specific clang', 'Wide low whoosh', 'Plate resonance 400 ms', 'Strap and boss rattle', 'Perfect block adds a bright "ting" layer, parry adds a glass chime'),
 'TWB': ('Twinblade', 'Double transient 40 ms apart', 'Spinning whoosh with phasing', 'Dual short rings', 'Central grip clatter', ''),
 'GAX': ('Greataxe', 'Massive chop, wood split crack', 'Very low whoosh 80-300 Hz, 450 ms', 'Earth thud and debris on ground hit', 'Haft groan', 'Longest wind-ups after greathammer'),
 'GHM': ('Greathammer', 'Ground-shaking boom, stone crack', 'Sub-heavy whoosh 60-250 Hz, 500 ms', 'Debris rain 800 ms, camera-shake sync', 'Iron head rattle', 'Charged heavy has a rising rumble so opponents hear it coming'),
}
for c in rd('items/melee_classes.csv'):
    code = c['class_id'][-3:]; n, tr, body, tail, mech, note = MELEE[code]
    rec(f'REC_MEL_{code}', 'Melee weapon', c['class_id'], n, tr, body, tail, mech,
        'Past 25 m: drop body whoosh, keep transient, low-pass 4 kHz; past 40 m: inaudible', 'Short early reflections, +2 dB low-mids, metal rings get room tail from Spatial Audio room',
        'Light/heavy/charged each a separate event; 4-6 variations per swing, pitch +/-3%, no repeat within 3; impact by material x damage type (see SFX tab Impacts)',
        'Whoosh length tracks active frames from melee_frame_data; enemy weapons of same class are 2 dB quieter and lower-passed so the player always hears their own hits first. ' + note)

FIRE = {
 'PST': ('Pistol', 'Sharp crack 1-4 kHz with 3 ms Meridian "capacitor tick" pre-transient', 'Short mid punch', 'Snappy 400 ms tail', 'Slide clack, mag drop, Shard cell click-in'),
 'ARF': ('Auto Rifle', 'Mid crack per round, loop-and-tail system', 'Mechanical chatter of bolt carrier', 'Rolling tail on release', 'Bolt rattle, belt jingle, overheat tick when barrel is hot'),
 'SCT': ('Scout Rifle', 'Heavy crack with a metallic "ting" on headshot', 'Firm body thump', 'Long outdoor slap-back', 'Lever-like cycling clunk'),
 'SMG': ('Submachine Gun', 'Tight high crack, fast', 'Light body', 'Short tail', 'Fast bolt chatter'),
 'SHG': ('Shotgun', 'Huge low boom, pellet spray hiss', 'Chest punch 60-150 Hz', 'Long rolling tail', 'Pump/break-action clack, shell clatter'),
 'SNP': ('Sniper Rifle', 'Supersonic crack + muzzle boom split', 'Deep body', 'Very long valley echo outdoors', 'Bolt throw, scope glint chime when an enemy sniper aims at the player (readability)'),
 'LCH': ('Launcher', 'Thump of launch + rocket ignition hiss', 'Rocket motor body following projectile (3D)', 'Explosion: 3-layer (crack, body, debris) with distance tail', 'Reload: tube clank, warhead slide'),
 'LNC': ('Shard Lance', 'Charge: rising crystal whine 0.6 s with glass ticks accelerating; fire: glass crack + electric snap', 'Beam body: choir formant + ring-mod at region root, sustained while beam is held', 'Tail: shattering glass shimmer and a Meridian capacitor discharge "thoom"', 'Cell vent hiss, crystal re-seat clink'),
}
for c in rd('items/firearm_classes.csv'):
    code = c['class_id'][-3:]; n, tr, body, tail, mech = FIRE[code]
    rec(f'REC_FIRE_{code}', 'Firearm', c['class_id'], n, tr, body, tail, mech,
        'Three layers crossfaded by distance: close (0-30 m), mid (30-120 m, transient softened, tail up), far (120-300 m, body only, 300 ms delay = speed of sound); plan 5.6 falloff',
        'Indoor: tight slap from Spatial Audio room, shorter tail, +3 dB low end; outdoor: open tail; canyon/wreck: tail switch by ray-cast estimate',
        'First-person (ADS) mix: transient +2 dB, mechanical +4 dB; third-person: tail +2 dB. Per-shot random from 6-8 variations; loop-and-tail for full-auto',
        'Kinetic damage vs Ward plays a duller impact (weak) and vs flesh a wet crack (strong); Weave damage is the reverse, so the player hears the matchup',
        'shard_lance.wav' if code == 'LNC' else '')

# --- abilities
EL = {i[0].replace('SID_ELEM_', ''): i for i in ID if i[0].startswith('SID_ELEM_')}
SLOT = {
 'Cast': ('Throw: element-coloured whoosh + glass flick', 'Projectile loop in element palette (3D, doppler)', 'Detonation: 3-layer burst in element palette, 2.5 m', 'Glass vial or Shard casing clink on throw'),
 'Strike': ('Melee burst: element transient on hand impact', 'Short 150 ms element bloom', 'Element-specific tail 400 ms', 'Gauntlet/Shard crackle in hand'),
 'Step': ('Dash: element "pop" at start position', 'Airy whoosh 6 m with element texture', 'Arrival pop quieter than departure', 'Cloth flap, armour shift'),
 'Surge': ('Activation: 1.2 s rising swell with choir formant and region-key chord', 'Sustained element bed for the Surge duration, 2-layer, ducks music 3 dB', 'End: release sigh + element tail', 'Heartbeat of Ember pulse under the bed'),
}
for a in rd('actors/weave_abilities.csv'):
    el = a['Element'].upper(); s = SLOT[a['Slot']]; sig = EL[el][3]
    rec(f'REC_{a["ABL_ID"]}', 'Weave ability', a['ABL_ID'], f'{a["Name"]} ({a["Element"]} {a["Slot"]})', s[0], s[1], s[2], s[3],
        'Enemy-cast versions audible to 60 m; player-cast to 40 m for allies', 'Detonations get room tail; Surge beds do not (they are inside the player)',
        f'Element palette: {sig}. Pitch to region mode.', 'Every enemy-cast ability has a 0.4-0.8 s wind-up in its element palette before release')
RES = {
 'RES_EMBERRAIN': 'Sky ignites: rising roar then staggered meteor whistles and impacts across 20 m',
 'RES_LANCE': 'Orbital point-defense beam: 1.5 s targeting chirps from the sky, then a column of Shard Lance tone 10x scale with ship capacitor boom',
 'RES_BLOOMGATE': 'Root field erupts: wet fibre tearing swell, creaking binds on each enemy',
 'RES_IRONSKIN': 'Player body to iron: plate clamp, hollow metallic footsteps for the duration, hits on player clang',
 'RES_STILLPOINT': 'Slow time: all world sound pitched down 1 octave with tape-stop curve, player sounds stay normal pitch',
 'RES_ECHOLEGION': 'Past Kindled summoned: a crowd of Ember heartbeats and faint armour, ghost choir',
 'RES_SHARDWALL': 'Instant cover: crystal wall grows with fast glass crackle and a ringing settle',
 'RES_UNDERTOW': 'Pull enemies: Hollow suck, rising pitch as targets slide, collision thuds',
 'RES_GRAVITYLIFT': 'Weightlessness: bass drops out, airy shimmer, slowed debris tinkle',
 'RES_QUIETVOICE': 'Fear: player speaks one Hush-processed word; enemies flee with panicked barks',
 'RES_BLINKCHORUS': 'Group teleport: choir inhale, glass pop per ally, arrival exhale',
 'RES_OVERCLOCK': 'Ostra Overclock: Ostra radio burst, relay clacks, all cooldowns reset with a cascade of ready-chimes',
}
for r in rd('actors/resonances.csv'):
    on, _, rest = RES.get(r['RES_ID'], ': ').partition(': ')
    rec(f'REC_{r["RES_ID"]}', 'Resonance', r['RES_ID'], r['Resonance'], on, rest, 'Long tail, world reacts (birds scatter, debris)', 'Shard in chest resonates (player-only layer)',
        'Audible region-wide for big Resonances (Lance, Ember Rain) with distant thunder-like tail', 'Indoor: compressed tail, debris rattle', 'Unique, no variations needed; hero sound, mixed hot', 'Resonances own the mix for 1 s: duck SFX 4 dB, music 6 dB')

# --- enemy archetypes: faction palette x role
ROLE = {
 'Fodder': ('Light footsteps, fast vocal grunts', 'Weak weapon swings, 2 variations', 'Death: short vocal + body fall', 'Loose gear rattle', 'Swarm: max 4 fodder vocals at once'),
 'Shield-bearer': ('Heavy shield bashes, plate steps', 'Shield block clang tells the player to flank', 'Death: shield drop clatter', 'Shield strap rattle', 'Shield raise has its own sound so the player knows when it is down'),
 'Skirmisher': ('Quick steps, flank whoosh', 'Dodge/teleport tell', 'Death: quick yelp', 'Light gear', 'Flank movement gets a rear-panned cue if behind the player'),
 'Artillery': ('Charge-up tell before each shot', 'Projectile loop', 'Impact in faction palette', 'Weapon mechanism', 'Every shot has a wind-up of 0.5 s+; incoming projectiles have a whistle that rises as they close'),
 'Heavy': ('Ground-shaking footsteps (sub layer)', 'Huge swings with long wind-up roar', 'Death: big fall, armour/scrap rain', 'Massive gear clatter', 'Wind-ups 0.6-1.0 s, always louder than the player weapon'),
 'Leader': ('Distinct vocal timbre, horn or call', 'Rallying call raises nearby morale', 'Death: a call cut short, then fodder panic barks', 'Banner or relic jingle', 'Leader death is a readable event: 0.3 s pause in combat music stems then panic'),
}
PAL = {'FAC_HOLLOWED': 'wet breath, glass grinding joints, broken speech, Hush whisper bleed',
       'FAC_REMNANT': 'servo whine, coolant hiss, targeting chirp, squelched radio callouts',
       'FAC_THORN': 'bone and wood gear, war whoops, horn calls, briar rattle',
       'FAC_CHOIRBORN': 'sung chant in G whole-tone, glass pops, reversed chords'}
for e in rd('actors/enemies.csv'):
    if e['Tier'] and 'VAR' in e['ACT_ID']:
        continue
    if e['FAC_ID'] not in PAL:
        continue
    r = ROLE.get(e['Role'], ROLE['Fodder'])
    rec(f'REC_{e["ACT_ID"]}', 'Enemy', e['ACT_ID'], f'{e["Name"]} ({e["Role"]})', r[0], r[1], r[2], r[3],
        'Vocals to 35 m, footsteps to 25 m, weapons per weapon class', 'Room tail from Spatial Audio; vocals get extra early reflections indoors',
        f'Faction palette: {PAL[e["FAC_ID"]]}. Regional variants (Cinder, Saltborn...) add one region sweetener (ash crackle, salt drip, ice crust, etc.)', r[4])

CRE = {'hound': 'canine snarls and pants', 'wolf': 'canine howls and snarls', 'fox': 'small fox yips', 'drake': 'reptile hiss and wing beats', 'wyrm': 'reptile hiss with glass grind',
       'roc': 'huge bird screech and wing gusts', 'elk': 'deer bellow, hooves', 'deer': 'deer calls, hooves', 'moth': 'soft wing flutter with glass shimmer', 'vulture': 'bird croaks, wing flaps',
       'crab': 'shell clacks, hull-metal scraping', 'tortoise': 'slow heavy steps, shell resonance', 'leech': 'wet suction', 'stalker': 'low purrs, leaf rustle', 'wisp': 'tiny choir tones', 'golem': 'stone grind, moss squelch',
       'mite': 'chittering with Hush whisper', 'beetle': 'carapace clicks, rust grit', 'serpent': 'water hiss, scale slither', 'swarm': 'massed squeaks and claws', 'ray': 'electric hum and water flaps',
       'strider': 'mount: deep chuffs, padded gallop', 'boar': 'grunts and squeals', 'crawler': 'many legs on metal'}
for c in rd('actors/creatures.csv'):
    n = c['Name'].lower(); src = next((v for k, v in CRE.items() if k in n), 'animal vocals')
    rec(f'REC_{c["ACT_ID"]}', 'Creature', c['ACT_ID'], c['Name'], f'Vocal onset: {src}', 'Movement foley scaled to size', 'Vocal tail with region reverb', 'Shard growths on body add a glass tick layer',
        'Calls carry 60-150 m (used as ambience one-shots when passive)', 'Room tail', 'Real animal recordings designed and pitched; no stock-library calls unprocessed', 'Aggro vocal plays before first attack (Hostile and Territorial only)')

# --- bosses
ARCH = {
 'KNIGHT': ('Armoured footsteps and cloak, weapon drag', 'Weapon class palette at 1.5x size', 'Phase roar: helmet-filtered war cry'),
 'CASTER': ('Robes, Shard focus hum', 'Element palette casts with 1.0 s tells', 'Phase change: choir swell in region key'),
 'GIANT': ('Sub-heavy steps felt in the controller', 'Ground slams with debris rain', 'Phase roar: low bellow with stone crack'),
 'MACHINE': ('Servo, hydraulics, reactor whine', 'Mechanical attacks with charge-up whines', 'Phase change: power surge, relay cascade, alarm tone'),
 'BEAST': ('Claws and breath', 'Bites and swipes with vocal tells', 'Phase roar: animal bellow layered with Shard glass'),
 'DUO': ('Two distinct timbres, panned to each body', 'Each body has its own tell family', 'When one falls, the survivor gets a grief roar and its music stem doubles'),
 'MULTI': ('Many-body foley (heads, limbs, units)', 'Overlapping tells, each body panned', 'Phase change: all bodies cry together'),
 'FLYER': ('Wing beats, air gusts with doppler', 'Dive attacks with rising whistle', 'Phase roar: aerial screech with echo'),
}
ELEM_OF = {'REG_01': 'EMBER', 'REG_02': 'STORM', 'REG_03': 'BLOOM', 'REG_04': 'IRON', 'REG_05': 'FROST', 'REG_06': 'HOLLOW', 'REG_Q': 'HOLLOW'}
bosses = rd('actors/bosses.csv')
for b in bosses:
    a = ARCH.get(b['Archetype'], ARCH['KNIGHT']); el = (b['Ward element'] if b['Ward element'] != 'None' else '') or ELEM_OF.get(b['Region'], 'IRON')
    el = el.upper(); hush = ' Last phase: Hush speaks one line through the boss (campaign 05-story-pass C).' if b['Class'] == 'Shard-bearer' else ''
    rec(f'REC_{b["ACT_ID"]}', 'Boss', b['ACT_ID'], f'{b["Boss"]} ({b["Class"]}, {b["Archetype"]}, {b["Height m"]} m)',
        a[0], a[1] + f'; element palette {EL[el][3][:70]}...', a[2], f'Weak points ({b["Weak points / parts"][:60]}) get a distinct crack when hit; part break = big shatter',
        'Boss sounds never attenuate below -12 dB inside the arena; outside the fog wall the arena is heard as a distant muffled bed',
        'Arena-specific convolution IR (one per boss arena)',
        f'Unique signature attack sound per boss; every attack in boss_moves.csv gets a tell sound timed to its startup frames.{hush}',
        'Telegraph family: light = whoosh tell; heavy = rising roar 0.5 s+; grab = cloth/breath inhale; unblockable = Shard choir shriek + red-shifted ring (same sound on every boss so players learn it once)')
rec('REC_ACT_BOSS_HUSH', 'Boss', 'ACT_BOSS_HUSH', 'Hush (final boss, campaign 02-characters)', 'Pre-roll: the whole world inhales (600 ms reverse reverb), all ambience removed',
    'Phase 1 the Lens: glass-and-choir attacks; phase 2+: Hush whisper crowd becomes the weapon, words as attack tells', 'Each phase ends in total silence for 1.5 s',
    'Ship machinery of the Quiet as percussion', 'No distance: Hush is everywhere in its own ship', 'The Quiet hull IR, 6 s tail', 'All Hush layers from SID_HUSH; music and Hush share the G whole-tone key',
    'Hush says the attack name before unblockables ("We lift.") so the tell is literally spoken')

# --- core systems
CORE = [
 ('WARD_HIT', 'Ward hit (player)', 'Glass tink 2-8 kHz', 'Electric sizzle 80 ms', 'Short shimmer', '', 'Player-only (2D)', '', 'Pitch rises as Ward falls (+5 semitones at 10%)', 'Tells you how much Ward is left without looking', ''),
 ('WARD_LOW', 'Ward under 25% (player)', 'Crackle onset', 'Fizzing crackle bed + 2-tone flutter', 'Stops on recharge or break', '', '2D', '', 'Bed at -22 dB, ducks nothing', 'Urgent but not alarming', ''),
 ('WARD_BREAK', 'Ward break (player)', 'Glass shatter burst', 'Sub drop 120 to 35 Hz + pressure whump', '0.8 s glass shimmer debris', 'Electric discharge crackle', '2D', '', 'World high-cut 300 ms, -3 dB everything else; HDR top tier', 'The single most important combat sound: you are now taking health damage', 'ward_break.wav'),
 ('WARD_RECHARGE', 'Ward recharge start and full (4.5 s after last hit)', 'Soft click (recharge starting)', 'Rising filtered sweep 1.2 s', 'Clean bell at full', 'Capacitor whine', '2D', '', 'Bell is in region key', 'Tells you it is safe to re-engage', 'ward_recharge.wav'),
 ('ENEMY_WARD_BREAK', 'Enemy Ward break', 'Lower, shorter shatter panned to the enemy', 'Element-tinted crack', 'Short debris', '', '3D to 50 m', 'Room tail', 'Match-element break plays a brighter "bonus" layer (3x break speed rule)', 'Tells the player headshots now deal 2x', ''),
 ('STANCE_BREAK', 'Enemy stance break', 'Heavy crunch + glass crack', 'Enemy groan/servo failure by faction', 'Ringing tail 0.5 s', '', '3D', 'Room', 'Slow-mo feel: 100 ms duck of all SFX before the crunch', 'Open for critical strike', 'stance_break.wav'),
 ('CRIT', 'Critical strike / riposte', 'Silence 80 ms, then deep stab', 'Bone crack + body', 'Low thud and Ember bloom', '', '3D', '', 'Mixed hottest of all player attacks', 'Payoff', ''),
 ('PARRY', 'Parry', 'Bright metallic ting + glass chime', 'Short ring', 'Shimmer', '', '3D', '', 'Pitched to region key', 'Instant confirmation of timing', 'parry.wav'),
 ('PERFECT_DODGE', 'Perfect dodge (capstone perk)', 'Air whip', 'Time-smear (pitch-down 30 ms)', 'Ember flicker', '', '2D', '', '', 'Confirms i-frames used', ''),
 ('BREATH_EMPTY', 'Breath empty', 'Ragged inhale', 'Player sounds dip 120 ms', '', '', '2D', '', 'Once per empty', 'Stop attacking', ''),
 ('TONIC', 'Tonic drink', 'Cork pop', 'Gulp x2', 'Warm swell', 'Glass clink', '3D for co-op', '', '', 'Allies hear you heal', ''),
 ('EMBER_PICKUP', 'Ember pickup', 'Glass tick + felt celesta note', 'Heartbeat thum 60 Hz', 'Short warm shimmer', 'Ember crackle grains', '2D', '', 'Chain pickups climb a pentatonic step each (max 8)', 'Reward', 'ember_pickup.wav'),
 ('EMBER_DROP', 'Death: Ember drops as a Shard-ghost', 'Heartbeat stops', 'Ember pulse leaves the body (descending chime)', 'Ghost hum begins at the death spot', '', 'Ghost hum 3D to 40 m', '', '', 'You can hear your lost Ember while you run back', ''),
 ('EMBER_RECOVER', 'Ember recovered', 'Heartbeat returns, doubled', 'Ascending chime cascade', 'Warm bloom', '', '2D', '', '', 'Relief', ''),
 ('ANCHOR_LIT', 'Anchor lit', 'Shard strike', 'Weave hum ignites into a chord in region key', 'Long bloom 4 s', 'Mechanical clamp of Meridian beacon', '3D to 80 m (others hear Anchors light)', 'Room', 'Music stinger MUS_STG_ANCHOR_LIT sits on top in key', 'Safe place', 'anchor_lit.wav'),
 ('LEVEL_UP', 'Level up', 'Chest Shard pulse', 'Rising chord', 'Bloom', '', '2D', '', '', 'Progress', ''),
 ('INVASION', 'Invasion warning (Quiet Hand)', 'Bone-flute breath', 'Low drone swells over 3 s', 'World ambience drops 6 dB until invader dies', '', '2D', '', '', 'Danger from a player', ''),
 ('RELAY_TOWER', 'Relay Tower map fill', 'Ostra radio ping', 'Data chirp cascade as map fills', 'Hush answers once (campaign) with whisper', '', '2D + tower emitter', '', '', 'Map gained', ''),
 ('SHARD_NOTE', 'Shard-note read', 'Glass tap', 'Whispered word (no voice: tone only)', 'Short chime', '', '3D', '', '', 'Another player left this', ''),
 ('STRIDER', 'Strider mount', 'Chuff call', 'Padded gallop loop by speed', 'Double-jump wing whump, glide wind', 'Saddle leather, Meridian harness clinks', 'Hooves to 50 m', '', '', '', ''),
 ('SKIMMER', 'Skimmer vehicle', 'Ignition cough', 'Engine loop by RPM (granular)', 'Exhaust pops on decel', 'Repulsor whine, part damage rattles', 'Engine to 200 m', 'Tunnels: engine reflections', 'Damaged parts (plan Part 1b part health) add grinding layers per part', 'Hear a disabled engine', ''),
 ('HAULER', 'Hauler vehicle', 'Diesel-like turbine start', 'Heavy engine loop + tracks/wheels', 'Turret traverse whine', 'Hull groans', 'Engine to 300 m', '', 'Turret fire uses Launcher recipe at 1.5x', '', ''),
 ('FLYER', 'Enemy flyer', 'Turbine whine', 'Jet loop with doppler', 'Fly-by roar', 'Wing damage flutter', 'To 400 m', '', 'Hijack: hatch clank + Ostra override chirp', '', ''),
]
for cid, n, tr, body, tail, mech, dist, ind, proc, read, smp in CORE:
    rec(f'REC_CORE_{cid}', 'Core system', '', n, tr, body, tail, mech, dist, ind, proc, read, smp)

wr('sfx_recipes.csv', ['rec_id', 'family', 'ref', 'name', 'transient', 'body', 'tail', 'mechanical_detail', 'distance_variant', 'indoor_variant', 'processing', 'readability', 'sample'], R)

# ======================================================== 3. combat readability
READ = [
 ('Incoming attack', 'Every enemy and boss attack has a tell sound aligned to its startup frames; tell length = startup time', 'Plan 3.2 "Every fight is readable"'),
 ('Attack type', 'Light = whoosh tell; heavy = rising roar 0.5 s+; grab = inhale/cloth; unblockable = Shard choir shriek (same on every enemy and boss)', 'One vocabulary learned once'),
 ('Direction', 'Attacks from outside the camera view get +3 dB and a rear-panned whoosh; HRTF on headphones', ''),
 ('Ward state', 'Hit pitch rises as Ward falls; low-Ward crackle; break shatter; recharge sweep and full bell', 'Player never needs to look at the bar'),
 ('Damage matchup', 'Kinetic on Ward and Weave on flesh sound dull (wrong tool); kinetic on flesh and Weave on Ward sound sharp (right tool); matching element on enemy Ward adds a bright bonus layer', 'Teaches the element rule by ear'),
 ('Headshot', 'Headshot only after Ward down: metallic ting + body crack; before Ward is down a headshot sounds like a normal Ward hit', ''),
 ('Enemy awareness', 'Unaware: idle chatter; Suspicious: search bark + music Tension; Engaged: spotted bark + music Combat; one bark per group, not per enemy', 'Halo-style'),
 ('Morale break', 'Leader death: call cut short, 0.3 s music stem gap, fodder panic barks', 'Plan 2.6 morale'),
 ('Stance', 'Enemy stance near break: armour creak / servo strain layer at 80%+; break = crunch', ''),
 ('Status buildup', 'Each status has a buildup loop on the target that rises in pitch as it nears proc; proc = element burst', ''),
 ('Low health', 'World low-pass 2.5 kHz, heartbeat, faint tinnitus', ''),
 ('Ally down (co-op)', 'Downed ally: Ember heartbeat slowing from their position, audible to 60 m', 'Revive cue'),
 ('Sniper aim', 'Enemy sniper aiming at the player: scope glint chime + rising tone 1.0 s before shot', ''),
 ('Grenades', 'Enemy grenade landing within 6 m: bounce clink + warning bark; fuse ticks audible within 4 m', ''),
 ('Boss phase', 'Phase transition: roar + music transition stinger during the 3.0 s invulnerable window', 'boss_phases.csv'),
 ('Hush', 'Hush lines in Shard-bearer last phases and at Relay Towers duck the world rather than playing loud', 'Campaign 05-story-pass'),
]
wr('combat_readability.csv', ['situation', 'rule', 'source'], READ)

# ======================================================== 4. mix priority
PRI = [
 (1, 'Boss and enemy telegraphs (tells, unblockable shriek)', 'Never ducked; HDR top', 'Ducks music -4 dB'),
 (2, 'Player Ward break, low-health, Breath empty', 'Never ducked', 'High-cut world 300 ms on Ward break'),
 (3, 'Dialogue: Ostra, Hush, cinematic and quest lines', 'Ducked only by tiers 1-2', 'Ducks music -6, ambience -4, enemy barks -6'),
 (4, 'Player weapons, abilities, Resonances', '', 'Resonances duck SFX -4 for 1 s'),
 (5, 'Incoming damage on player, parry, crit, stance break', '', 'Stance break pre-ducks SFX 100 ms'),
 (6, 'Enemy weapons and abilities (non-telegraph)', 'Ducked by 1-5', ''),
 (7, 'Enemy and ally barks', 'Max 3 concurrent', ''),
 (8, 'Foley, footsteps (PvP raises footsteps to tier 4)', '', ''),
 (9, 'Music', 'Ducked by 1, 3, Resonances', ''),
 (10, 'Ambience and weather', 'Ducked by 3, Hush, invasion', ''),
 (11, 'UI', 'Never ducked; mixed under SFX', ''),
]
wr('mix_priority.csv', ['tier', 'what', 'ducked_by', 'ducks'], PRI)

# ======================================================== 5. music stems
STEMS = [
 ('Explore', 'Bed (drone/pads)', 'Always on', 'Region mode drone; Weave instruments'),
 ('Explore', 'Melody', 'Off while crouched/undetected; phrase gaps 30-90 s', 'Region signature instrument plays Shard motif variant'),
 ('Explore', 'Tension', 'RTPC Threat 1-35', 'Low strings or bowed metal'),
 ('Combat', 'Percussion', 'Combat L1+', 'Region percussion (taiko, bodhran, anvil...)'),
 ('Combat', 'Low ostinato', 'Combat L1+', 'Brass/strings ostinato'),
 ('Combat', 'Mid harmony', 'Combat L2+', 'Region ensemble'),
 ('Combat', 'High / choir', 'Combat L3', 'Choir or lead line'),
 ('Combat', 'Meridian synth', 'RTPC Act_Drift (10/30/80%)', 'Synth doubling that grows by act'),
 ('Boss', 'Rhythm', 'Boss_Phase 1+', 'Boss motif rhythm'),
 ('Boss', 'Motif', 'Boss_Phase 1+', 'Unique boss motif'),
 ('Boss', 'Enrage', 'RTPC Boss_HP < 20% in final phase', 'Choir and brass doubling'),
 ('Boss', 'Hush voice', 'Shard-bearer last phase only', 'Hush whisper crowd in G whole-tone over the boss key'),
]
wr('music_stems.csv', ['context', 'stem', 'driver', 'content'], STEMS)

# ======================================================== 6. region ambience beds
BEDS = [
 ('REG_01', 'Cinderreach', 'Ash-fall hiss (pink noise, 4-10 kHz) + cooling hull ticks + distant forge hammers every 20-40 s + ember crackle; night: hull groans, ash wolves far off', 'Hot dry wind across wreck ribs whistling in D', 'Low reactor hum from buried hull, 55 Hz'),
 ('REG_02', 'Saltmere', 'Surf wash (stereo, 8 s cycle) + gulls + rigging creak + bells on buoys; storms add thunder rolls and rain on wood and metal', 'Sea wind, wet', 'Foghorns tuned to A'),
 ('REG_03', 'Thornwood', 'Dense canopy rustle + insects + frog choruses + creaking roots; clan drums far off at night', 'Little wind under canopy, gusts above', 'Wooden knocks in E Aeolian'),
 ('REG_04', 'Glasswaste', 'Glass sand grains singing in wind (granular resonators) + wreck groans + heat shimmer tone + servo whine of Remnant in distance', 'Hot wind with glass-tone harmonics in C Lydian', 'Ship hull resonance'),
 ('REG_05', 'Rimefall', 'Snow hush (very quiet bed) + ice cracking + wolves + choir-stone resonance at sites', 'Cold wind, blizzards as weather state', 'Crystal bowl tones in B'),
 ('REG_06', 'Hollowdeep', 'Cavern drips + deep machinery heartbeat + Hollowed moans far off + wind through bone', 'Cave drafts', 'Sub pulses 30-40 Hz, Hush whisper bleed near the Quiet tether'),
 ('REG_Q', 'The Quiet', 'Ship ventilation + failing life-support alarms (distant) + vacuum quiet in breached sections + alien choir inside the hull', 'None (pressurised) or none at all (vacuum: only body-conducted sound)', 'Hush field always present at -40 dB'),
 ('REG_U', 'The Undervault', 'Reactor thrum + steam vents + conveyor clatter + Remnant drone chatter', 'Ventilation drafts', 'Machinery in tempo with Undervault music'),
 ('REG_HUB', 'Lantern Hold', 'Bridge consoles + chapel bells + market walla + smithy + hull settling', 'Drafts through bridge windows', 'Ship bells in G Mixolydian'),
]
wr('region_beds.csv', ['reg_id', 'region', 'bed', 'wind', 'tonal_layer'], BEDS)
