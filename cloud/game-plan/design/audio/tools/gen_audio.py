#!/usr/bin/env python3
"""Generate every Shardfall audio-direction table into design/audio/.
Reads game data (read-only) from game-plan/data and shardfall-assets.xlsx.
Run: python3 design/audio/tools/gen_audio.py   (from game-plan/)"""
import csv, os, re
from collections import Counter, defaultdict

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
    return rows

def tok(s):
    return re.sub(r'[^A-Za-z0-9]+', '', s.title())

regions = {r['reg_id']: r for r in rd('world/regions.csv')}
bosses = rd('actors/bosses.csv')
phases = defaultdict(list)
for p in rd('actors/boss_phases.csv'):
    phases[p['ACT_ID']].append(p)
npcs = rd('world/npcs.csv')
factions = rd('actors/factions.csv')
enemies = rd('actors/enemies.csv')

# ---------------------------------------------------------------- palettes
# region: (short code, mode, tempo explore, tempo combat, signature instruments, Meridian-side colour)
PAL = {
 'REG_01': ('CDR', 'D Phrygian', 72, 132, 'low brass; frame drums and taiko; hurdy-gurdy drone; bowed and struck hull plate', 'cracked reactor hum pitched to D'),
 'REG_02': ('SAL', 'A Dorian', 80, 140, 'nyckelharpa; low male work-song choir; ocean drum; struck rigging and chain', 'wet tape-delay on choir, sonar ping motif'),
 'REG_03': ('THN', 'E Aeolian', 66, 126, 'wooden flutes; hardanger fiddle; bodhran; plucked psaltery; prepared piano', 'granular-stretched birdsong'),
 'REG_04': ('GLS', 'C Lydian', 90, 150, 'glass harmonica; waterphone; low strings; anvil and pipe percussion', 'analog step-sequencer arps'),
 'REG_05': ('RIM', 'B Aeolian', 60, 120, 'female choir; celesta; crystal bowls; solo cello', 'frozen-reverb pads (infinite tails)'),
 'REG_06': ('HOL', 'F Locrian', 54, 116, 'contrabass clarinet; bowed cymbals; reversed choir; sub drones', 'bit-crushed, dropped-sample-rate orchestra'),
 'REG_Q':  ('QUI', 'G whole-tone', 64, 138, 'modular synths; processed orchestra; ship machinery as percussion', 'every leitmotif played backwards or decayed'),
 'REG_U':  ('UND', 'D Phrygian dominant', 84, 144, 'industrial percussion from Meridian machinery; tuba; distorted cello', 'servo and hydraulic loops in tempo'),
 'REG_HUB':('HUB', 'G Mixolydian', 76, 0, 'pipe organ in a hull chapel; chamber strings; lute; ship bells', 'faint bridge-console bleeps'),
}

music = []  # cue_id, category, context, owner_ref, wwise_state, length_s, loop, layers, tempo, mode, instrumentation, stems, minutes_unique, notes
# plan Phase 3 vertical slice: Region 1, Ostra, one town, one site, one field boss, Citadel first boss
SLICE_REFS = {'REG_01', 'ACT_NPC_OSTRA', 'ACT_BOSS_ASHCOLOSSUS', 'ACT_BOSS_SPINEGATE'}
SLICE_PFX = ('MUS_THEME_MAIN', 'MUS_BOSS_ASHCOLOSSUS', 'MUS_BOSS_SPINEGATE', 'MUS_STG_', 'MUS_CIN_OPENING', 'MUS_CIN_ACT1_INTRO_OSTRA', 'MUS_MENU_TITLE')
def cue(cid, cat, ctx, ref, state, length, loop, layers, tempo, mode, inst, stems, notes=''):
    slice = 'Yes' if (ref in SLICE_REFS or cid.startswith(SLICE_PFX)) else ''
    music.append([cid, cat, ctx, ref, state, length, 'Yes' if loop else 'No', layers, tempo, mode, inst,
                  stems, round(length / 60, 2), slice, notes])

ST = 'Perc; Low; Mid; High; Choir/Solo'
# core motifs
cue('MUS_THEME_MAIN', 'Theme', 'Main theme: Shard motif (4 notes, rising 4th then falling minor 2nd) for full orchestra, choir and synth', '', 'Music_Menu=Title', 210, False, 1, 76, 'D Dorian', 'full orchestra; mixed choir; Meridian synth bed', ST, 'Source of every other motif')
cue('MUS_THEME_OSTRA', 'Theme', 'Ostra leitmotif: Shard motif on solo synth-voice, harmony gains notes as her memory returns', 'ACT_NPC_OSTRA', '', 120, False, 1, 70, 'D Dorian', 'vocoded solo voice; glass harmonica; strings', ST, '5 memory-state versions exist inside Ostra cinematics')
cue('MUS_THEME_QUIET', 'Theme', 'The Quiet motif: Shard motif inverted and played in reverse', 'REG_Q', '', 150, False, 1, 64, 'G whole-tone', 'modular synth; reversed choir', ST)
cue('MUS_THEME_WEAVE', 'Theme', 'The Weave motif: open-fifth drone and folk ornament, the fantasy side of the score', '', '', 120, False, 1, 66, 'A Dorian', 'folk ensemble; hardanger fiddle; female choir', ST)
cue('MUS_THEME_MERIDIAN', 'Theme', 'The Meridian motif: arpeggiated analog synth and brass, the sci-fi side of the score', '', '', 120, False, 1, 96, 'C Lydian', 'analog synths; brass section', ST)

# regions: explore day/night, 3 tension layers, combat 3 intensities, discovery stingers, citadel, town
for rid, (code, mode, te, tc, inst, mer) in PAL.items():
    r = regions[rid]; name = r['name']; base = f'MUS_{code}'
    insts = f'{inst}; Meridian colour: {mer}'
    if rid == 'REG_HUB':
        for sub, ln in (('DAY', 240), ('NIGHT', 240), ('FACTIONHALL', 150), ('MARKET', 180), ('ARENA_LOBBY', 120), ('RAIDGATE', 120)):
            cue(f'{base}_{sub}', 'Hub', f'{name} {sub.lower().replace("_", " ")}', rid, f'Music_Region={code}; Music_Sub={sub}', ln, True, 3, te, mode, insts, ST)
        continue
    for sub, ln in (('EXPLORE_DAY', 300), ('EXPLORE_NIGHT', 300)):
        cue(f'{base}_{sub}', 'Region explore', f'{name} {sub.split("_")[1].lower()} exploration; sparse, 30-90 s silences between phrases', rid, f'Music_Region={code}; Music_Mode=Explore', ln, True, 3, te, mode, insts, ST, 'Layers: bed / melody / tension (RTPC Threat)')
    cue(f'{base}_TENSION', 'Region tension', f'{name} enemies aware but not engaged', rid, f'Music_Mode=Tension', 90, True, 2, te, mode, insts, ST)
    for lvl, ln in ((1, 120), (2, 120), (3, 120)):
        cue(f'{base}_COMBAT_L{lvl}', 'Region combat', f'{name} combat intensity {lvl} (Threat {["0-35", "35-70", "70-100"][lvl-1]})', rid, f'Music_Mode=Combat; Combat_Level={lvl}', ln, True, 4, tc, mode, insts, ST, 'Bar-synced; L2/L3 add stems over L1')
    cue(f'{base}_COMBAT_END', 'Stinger', f'{name} combat resolved', rid, '', 6, False, 1, tc, mode, insts, 'Stereo')
    cue(f'{base}_DISCOVERY', 'Stinger', f'{name} new landmark discovered', rid, '', 8, False, 1, te, mode, insts, 'Stereo')
    if rid not in ('REG_Q', 'REG_U'):
        cue(f'{base}_CITADEL', 'Dungeon', f'{name} Citadel interior', rid, 'Music_Mode=Dungeon', 240, True, 3, te, mode, insts, ST)
        cue(f'{base}_SITE', 'Dungeon', f'{name} catacomb/cave/mine/tower site (shared by ~5 sites)', rid, 'Music_Mode=Dungeon', 180, True, 3, te, mode, insts, ST)
        cue(f'{base}_TOWN', 'Region town', f'{name} settlement', rid, 'Music_Mode=Town', 180, True, 2, te, mode, insts, ST)
        cue(f'{base}_HOLLOWING', 'Region explore', f'{name} after the Hollowing drains the land (late-game world state)', rid, 'World_State=Hollowed', 240, True, 3, te - 10, mode, insts + '; detuned by -30 cents', ST)

# factions
for f in factions:
    fid, fn = f['FAC_ID'], f['Faction']
    cue(f'MUS_FAC_{fid[4:]}', 'Faction theme', f'{fn} theme (hall, questline key scenes, leader entrances)', fid, 'Music_Faction=' + fid[4:], 150, False, 2, 80, 'per faction', 'built on Shard motif; faction colour instrument', ST)

# bosses: one cue per phase (layered loop), intro, transition per phase change, victory
CLS_LEN = {'Shard-bearer': 180, 'Citadel': 150, 'Raid': 210, 'Field': 120, 'Site': 120, 'Undervault': 150, 'Final': 210}
for b in bosses:
    aid = b['ACT_ID']; code = aid.replace('ACT_BOSS_', '')
    rid = b['Region']; pal = PAL.get(rid, PAL['REG_Q'])
    cls = b['Class']; n = int(b['Phases'])
    choir = 'full choir' if cls in ('Shard-bearer', 'Raid', 'Final') else 'chamber choir' if cls == 'Citadel' else 'no choir'
    inst = f'{pal[4]}; {choir}; boss motif unique to {b["Boss"]}'
    cue(f'MUS_BOSS_{code}_INTRO', 'Boss', f'{b["Boss"]} intro (fog wall crossed; skippable on retry)', aid, 'Music_Boss=' + code, 8 if cls in ('Field', 'Site') else 14, False, 1, pal[3], pal[1], inst, 'Stereo + stems')
    for p in phases.get(aid, []):
        ph = p['Phase']
        cue(f'MUS_BOSS_{code}_P{ph}', 'Boss', f'{b["Boss"]} phase {ph} ({p["Starts at HP %"]}-{p["Ends at HP %"]}% HP); {p["Audio"]}', p['BPH_ID'], f'Music_Boss={code}; Boss_Phase={ph}', CLS_LEN[cls], True, 3, pal[3] + 6 * (int(ph) - 1), pal[1], inst, ST, 'Layers: rhythm / motif / enrage (RTPC Boss_HP)')
        if int(ph) > 1:
            cue(f'MUS_BOSS_{code}_T{ph}', 'Boss', f'{b["Boss"]} transition into phase {ph} (fills the invulnerable roar)', p['BPH_ID'], '', 3, False, 1, pal[3], pal[1], inst, 'Stereo')
    cue(f'MUS_BOSS_{code}_WIN', 'Boss', f'{b["Boss"]} defeated', aid, '', 12 if cls in ('Shard-bearer', 'Raid', 'Final') else 6, False, 1, pal[2], pal[1], inst, 'Stereo')

# activities and modes
for cid, ctx, ln, loop in (
    ('MUS_STRIKE_COMBAT', 'Strike combat (endgame 3-player, plan 3.11)', 180, True),
    ('MUS_STRIKE_END', 'Strike complete', 10, False),
    ('MUS_RAID_LOBBY', 'Raid assembly in The Quiet', 120, True),
    ('MUS_RAID_ENCOUNTER_MECH', 'Raid puzzle/mechanic phases (non-boss)', 240, True),
    ('MUS_RAID_WIPE', 'Raid wipe', 6, False),
    ('MUS_PVP_PREGAME', 'Arena countdown', 30, False),
    ('MUS_PVP_MATCH', 'Arena match (low bed so footsteps read)', 240, True),
    ('MUS_PVP_LASTMIN', 'Arena final minute', 60, True),
    ('MUS_PVP_WIN', 'Arena victory', 8, False),
    ('MUS_PVP_LOSS', 'Arena defeat', 8, False),
    ('MUS_INVASION', 'Invader arrives (overrides region music)', 120, True),
    ('MUS_COOP_JOIN', 'Co-op partner joins', 4, False),
):
    cue(cid, 'Activity', ctx, '', 'Music_Mode=' + cid[4:], ln, loop, 3 if loop else 1, 140, 'varies', 'score palette of the host region plus Meridian synths', ST if loop else 'Stereo')

for cid, ctx, ln in (
    ('MUS_STG_DEATH', 'Player death (Ember burned)', 5), ('MUS_STG_ANCHOR_LIT', 'Anchor lit', 6), ('MUS_STG_ANCHOR_REST', 'Rest at Anchor', 4),
    ('MUS_STG_LEVELUP', 'Level up', 3), ('MUS_STG_SKILL_RANK', 'Skill rank up', 2), ('MUS_STG_SHARD_GAINED', 'Shard taken from a Shard-bearer', 15),
    ('MUS_STG_RESONANCE', 'Resonance unlocked', 5), ('MUS_STG_LEGENDARY', 'Shardborn/legendary drop', 3), ('MUS_STG_QUEST_DONE', 'Quest complete', 4),
    ('MUS_STG_QUEST_FAIL', 'Quest failed', 4), ('MUS_STG_ECHO_SUMMON', 'Echo summoned', 3), ('MUS_STG_MAP_FRAGMENT', 'Map fragment found', 4),
    ('MUS_STG_REP_TIER', 'Reputation tier reached', 4), ('MUS_STG_LORE_STONE', 'Choir stone read', 6), ('MUS_STG_SECRET', 'Secret found', 3),
):
    cue(cid, 'Stinger', ctx, '', '', ln, False, 1, 0, 'key-matched to current region (6 key variants)', 'core motif fragment', 'Stereo', 'Key-matched: one render per region mode')

for cid, ctx, ln, loop in (
    ('MUS_MENU_TITLE', 'Title screen (main theme arrangement)', 210, True), ('MUS_MENU_CREATOR', 'Character creator / Origin pick', 180, True),
    ('MUS_MENU_PAUSE', 'Pause (current cue low-passed, no new music)', 0, False), ('MUS_MENU_CREDITS', 'Credits suite', 600, False),
    ('MUS_MENU_LOADING', 'Loading (ambient bed, 3 variations)', 90, True), ('MUS_MENU_MAP', 'Map/inventory (duck current cue -9 dB, no swap)', 0, False),
):
    cue(cid, 'Menu', ctx, '', 'Music_Menu=' + cid[9:].title(), ln, loop, 1, 72, 'D Dorian', 'main theme orchestration', ST if ln else '-')

CIN = [('OPENING', 'Opening: the Meridian falls (in-engine)', 420), ('ACT1_INTRO_OSTRA', 'Ostra wakes in the Shard', 150),
       ('ACT1_END', 'Act 1 to 2: the Quiet seen in the sky', 240), ('ACT2_SHARD_1', 'First Act 2 Shard returned', 90),
       ('ACT2_SHARD_4', 'Fourth Shard: the way to the Quiet opens', 180), ('ACT3_ASCENT', 'Leaving Veyl for the Quiet', 240),
       ('ACT3_OSTRA_MEMORY', 'Ostra remembers why the Meridian fell', 180), ('ENDING_MERIDIAN', 'Ending: restore the Meridian (sci-fi)', 360),
       ('ENDING_WEAVE', 'Ending: bind the Shards to the Weave (fantasy)', 360), ('ENDING_QUIET', 'Ending: take the Quiet (dark)', 360)]
# plan 5.7: opening, act transitions and three endings, about 45 minutes
for cid, ctx, ln in CIN:
    cue(f'MUS_CIN_{cid}', 'Cinematic', ctx, '', 'Music_Mode=Cinematic', ln, False, 1, 0, 'scored to picture', 'full orchestra, choir and synth; ending cues lean wholly acoustic (Weave), wholly synth (Meridian) or decayed (Quiet)', ST, 'Scored to locked picture in P5; temp from themes before')

M_HDR = ['cue_id', 'category', 'context', 'owner_ref', 'wwise_state', 'length_s', 'loop', 'layers', 'tempo_bpm', 'mode', 'instrumentation', 'stems', 'minutes', 'vertical_slice', 'notes']
wr('music_cues.csv', M_HDR, music)

# ---------------------------------------------------------------- adaptive music rules
RULES = [
 ('MR01', 'State group', 'Music_Region', 'CDR SAL THN GLS RIM HOL QUI UND HUB', 'Set by region volume on entry; 4 s crossfade at next bar', 'Region boundaries overlap 50 m to avoid flapping'),
 ('MR02', 'State group', 'Music_Mode', 'Explore Tension Combat Dungeon Town Cinematic Boss Activity Silence', 'Priority Cinematic > Boss > Activity > Combat > Tension > Dungeon > Town > Explore > Silence', 'Highest-priority request wins'),
 ('MR03', 'RTPC', 'Threat', '0-100', 'Pacing director intensity score (plan Part 1b: build-up, sustain peak, peak fade, relax; Ward breaks and Breath spends feed it). Sum of aware enemies x role weight, Ward break +15, Breath spend +5, decays 8/s out of combat. Director phase maps to music: build-up = Tension, sustain peak = Combat L2-L3, peak fade = Combat L1, relax = COMBAT_END then silence', 'Drives Combat_Level and stem volumes'),
 ('MR04', 'State', 'Combat_Level', '1 2 3', 'Threat 0-35 = 1, 35-70 = 2, 70-100 = 3; go up on next beat, go down only after 6 s below threshold', 'Hysteresis stops pumping'),
 ('MR05', 'Transition', 'Explore -> Tension', '', 'Any enemy reaches Suspicious; next bar; tension stem fades in over 2 bars', ''),
 ('MR06', 'Transition', 'Tension/Explore -> Combat', '', 'Any enemy reaches Engaged; next beat; 1-beat drum pickup; skip pickup if player struck first (instant cut on downbeat)', ''),
 ('MR07', 'Transition', 'Combat -> Explore', '', 'No Engaged enemy for 8 s; play <REGION>_COMBAT_END stinger then 20 s silence before explore resumes', 'Silence matters: Souls-style quiet after fights'),
 ('MR08', 'Transition', 'Boss entry', '', 'Fog wall crossed: duck everything, INTRO stinger, P1 starts on stinger end', 'Retry: skip intro, start P1 at bar 1'),
 ('MR09', 'Transition', 'Boss phase change', '', 'BPH phase start fires T<n> stinger aligned to the roar; P<n> starts on the downbeat after', 'Transition length matches 3.0 s invulnerable window'),
 ('MR10', 'RTPC', 'Boss_HP', '0-100', 'Enrage stem fades in below 20% HP of final phase', ''),
 ('MR11', 'Transition', 'Boss defeated', '', 'Hard stop on kill frame, 1.5 s silence, WIN stinger, then 30 s silence', ''),
 ('MR12', 'Transition', 'Player death', '', 'All music stops in 0.5 s; DEATH stinger; music resumes from Anchor state after respawn', ''),
 ('MR13', 'Rule', 'Explore density', '', 'Explore cues play phrases then 30-90 s random silence; total music on-time in explore 55%', 'Stops fatigue over 100+ hours'),
 ('MR14', 'Rule', 'Stinger key match', '', 'Stingers pick the render in the current region mode; never overlap two stingers (queue, drop if older than 3 s)', ''),
 ('MR15', 'Rule', 'Co-op', '', 'Music is local: each client follows its own Threat and position; boss music syncs to host boss state', ''),
 ('MR16', 'Rule', 'PvP', '', 'Music bus capped at -18 dB relative; no combat layers; footsteps and reloads must read', ''),
 ('MR17', 'State', 'World_State', 'Normal Hollowed', 'Region switches to HOLLOWING cues after the Hollowing event in that region', ''),
 ('MR18', 'RTPC', 'Ostra_Memory', '0-5', 'Raised by main quest beats; selects Ostra motif harmony and her voice processing chain', 'Same RTPC drives VO DSP'),
 ('MR19', 'Rule', 'Day/night', '', 'Day/night swap only at a phrase end while in Explore', ''),
 ('MR20', 'Rule', 'Stealth', '', 'Crouched and undetected: explore melody stem muted, bed and tension only', ''),
 ('MR21', 'Rule', 'Menus', '', 'Pause and inventory low-pass the current cue at 800 Hz and duck -9 dB; never swap cues', ''),
 ('MR22', 'Rule', 'Act drift', '', 'Mix ratio of synth to acoustic stems rises by act: Act 1 10%, Act 2 30%, Act 3 80% (RTPC Act_Drift)', 'Score turns from fantasy to sci-fi with the story'),
]
wr('music_system_rules.csv', ['rule_id', 'type', 'name', 'values', 'behaviour', 'notes'], RULES)

# ---------------------------------------------------------------- VO cast and line counts
cast = []  # vo_id, character, kind, ref, voice_spec, lines_en, studio, notes
def vc(vid, ch, kind, ref, spec, lines, notes=''):
    cast.append([vid, ch, kind, ref, spec, lines, notes])

vc('VO_OSTRA', 'Ostra', 'Narrator / ship intelligence', 'ACT_NPC_OSTRA', 'Female, 30s-50s, warm then fractured; recorded dry, processed at runtime by memory state', 6000, 'Tutorial, region intros, lore, combat hints, 5 memory states')
for n in npcs:
    role = n['role']
    if role == 'Faction leader':
        vc('VO_' + n['act_id'].replace('ACT_NPC_', ''), n['name'], 'Faction leader', n['act_id'], 'Lead actor', 1500, 'Questline, hall barks, Strike/raid radio handler')
    elif role.startswith('Companion'):
        vc('VO_' + n['act_id'].replace('ACT_', ''), n['name'], 'Companion', n['act_id'], role.split(': ', 1)[1] + ('; processed synthetic voice' if 'drone' in role else ''), 2500, 'Loyalty quest, banter, combat barks, reactions to 44 bosses plus Hush and 9 regions')
    elif role == 'Vendor':
        trader = 'trader' in n['name'].lower()
        vc('VO_' + n['act_id'].replace('ACT_NPC_', ''), n['name'], 'Vendor', n['act_id'], 'Supporting actor', 150 if trader else 300, 'Greet, buy, sell, refuse, rumours')
    elif role.startswith('Summoned ally'):
        vc('VO_ECHO', n['name'], 'Summoned ally', n['act_id'], 'Choral double-voice (2 actors layered)', 300, 'Summon, ally combat barks')
SPEAK = {'Shard-bearer': 250, 'Citadel': 150, 'Raid': 200}
HUMAN_SITE = {'SMUGGLERQUEEN', 'WRECKFOREMAN', 'MIRRORKNIGHT', 'LASTPILOT', 'TOWERWITCH', 'CRYPTABBOT', 'CLOCKPRIOR', 'VAULTKEEPER', 'SKIMMERACE', 'ARKKNIGHT'}
for b in bosses:
    code = b['ACT_ID'].replace('ACT_BOSS_', '')
    n = SPEAK.get(b['Class'], 60 if code in HUMAN_SITE else 0)
    if n:
        vc('VO_BOSS_' + code, b['Boss'], 'Boss (' + b['Class'] + ')', b['ACT_ID'], 'Lead actor' if b['Class'] in ('Shard-bearer', 'Raid') else 'Supporting actor', n, 'Intro, phase taunts, player-death taunts, death line, lore')
    else:
        vc('VO_BOSS_' + code, b['Boss'], 'Boss (creature)', b['ACT_ID'], 'No dialogue: creature vocals are sound design (SFX tab, Bosses group)', 0)
# enemy bark sets
BARK_CATS = ['spotted', 'search_start', 'lost_target', 'found_again', 'flank', 'cover', 'suppress', 'reload', 'grenade_throw', 'grenade_warn', 'ally_down', 'leader_down_flee', 'low_ward', 'hurt', 'death', 'taunt', 'player_dodge', 'player_stagger', 'idle_chat', 'warn_player_in_shadow', 'ward_broken', 'charge', 'retreat', 'victory', 'call_backup']
VAR = 6
for fid, fname, voices, spec in (('FAC_THORN', 'Thorn Clans', 6, 'Human, rough, 3 m / 3 f'),
                                 ('FAC_CHOIRBORN', 'Choirborn of the Quiet', 4, 'Half-sung chant, 2 m / 2 f, harmonised in DSP'),
                                 ('FAC_REMNANT', 'Remnant', 3, 'Actor read through synthetic processing (no TTS)'),
                                 ('FAC_HOLLOWED', 'Hollowed', 4, 'Broken speech fragments and groans, 2 m / 2 f')):  # plan 3.9: four enemy factions
    cats = len(BARK_CATS) if fid != 'FAC_HOLLOWED' else 10
    for v in range(1, voices + 1):
        vc(f'VO_BARK_{fid[4:]}_{v:02d}', f'{fname} voice {v}', 'Enemy bark set', fid, spec, cats * VAR, f'{cats} bark categories x {VAR} variants')
for v in range(1, 13):
    vc(f'VO_TOWN_{v:02d}', f'Townsfolk voice {v}', 'Ambient NPC', 'REG_*', ['Cinderreach', 'Saltmere', 'Thornwood', 'Glasswaste', 'Rimefall', 'Lantern Hold'][(v - 1) // 2] + ' accent, ' + ('m' if v % 2 else 'f'), 250, 'Greetings, walla lines, reactions to player gear and reputation')
for v, s in enumerate(('Body A voice 1', 'Body A voice 2', 'Body B voice 1', 'Body B voice 2'), 1):
    vc(f'VO_PLAYER_{v}', f'Player {s}', 'Player', 'ORG_*', 'Efforts plus co-op callouts; player picks voice in creator', 120, 'Efforts on SFX tab; 60 co-op ping callouts x 2 reads')
vc('VO_ANNOUNCER_ARENA', 'Arena announcer', 'Announcer', 'REG_HUB', 'Lead actor, dry and close', 400, 'Modes, streaks, score, round start/end')
used = sum(c[5] for c in cast)
POOL_CHARS = 120 - sum(1 for c in cast if c[5])
pool = 60000 - used
vc('VO_POOL_CAMPAIGN', 'Quest NPC roster (campaign thread owns names)', 'Quest NPCs', 'design/campaign/', f'{POOL_CHARS} characters, so the cast totals 120 (plan 5.5); cast after campaign roster lands', pool, 'Budget held so total = 60,000 (asset A090)')
speaking = sum(1 for c in cast if c[5] and c[0] != 'VO_POOL_CAMPAIGN') + POOL_CHARS
# The campaign thread owns characters and line counts (design/campaign/vo_budget.csv).
# When it exists, the cast is its speakers; this script only adds voice direction.
VB = os.path.join(GP, 'design', 'campaign', 'vo_budget.csv')
if os.path.exists(VB):
    spec = {c[3]: (c[1], c[2], c[4]) for c in cast}
    spec.update({
        'PLAYER': ('The Kindled (player)', 'Player', 'Two voice sets, A and B, picked in the creator; each records every line (campaign 02-characters)'),
        'ACT_BOSS_HUSH': ('Hush', 'Final boss / villain', 'Calm, slightly too friendly, always "we"; recorded as 8-24 whisper and spoken takes for the Hush crowd chain (sonic_identity SID_HUSH)'),
        'ACT_NPC_IRES': ('Captain Edda Ires', 'Story lead', 'Lead actor; masked lines get the lamplighter-mask filter'),
    })
    agg, src = Counter(), defaultdict(list)
    with open(VB, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['speaker'] == 'TOTAL':
                continue
            agg[r['speaker']] += int(r['lines']); src[r['speaker']].append(r['source'])
    cast = []
    for sp_, n in agg.most_common():
        nm, kind, vs = spec.get(sp_, (sp_, 'See design/campaign/02-characters.md', 'Cast per campaign character notes'))
        cast.append(['VO_' + re.sub(r'[^A-Z0-9]+', '_', sp_.upper().replace('ACT_', '')).strip('_'), nm, kind, sp_, vs, n, '; '.join(dict.fromkeys(src[sp_]))[:200]])
wr('vo_cast.csv', ['vo_id', 'character', 'kind', 'ref', 'voice_spec', 'lines_en', 'notes'], cast)

# barks detail
wr('vo_bark_categories.csv', ['category', 'trigger', 'cooldown_s', 'max_concurrent', 'variants_per_voice'],
   [[c, t, cd, mc, VAR] for c, t, cd, mc in [
    ('spotted', 'AI state to Engaged', 8, 1), ('search_start', 'AI to Searching', 10, 1), ('lost_target', 'Search times out', 10, 1),
    ('found_again', 'Re-acquire after search', 8, 1), ('flank', 'Utility AI picks flank point', 12, 1), ('cover', 'Enters cover', 10, 2),
    ('suppress', 'Fires suppressing burst', 10, 1), ('reload', 'Reload start', 6, 2), ('grenade_throw', 'Throws grenade', 6, 1),
    ('grenade_warn', 'Player grenade lands within 6 m', 4, 1), ('ally_down', 'Ally dies within 20 m', 6, 1), ('leader_down_flee', 'Morale break (60% flee)', 0, 3),
    ('low_ward', 'Own Ward under 25%', 10, 1), ('hurt', 'Damage over 10% max HP', 1.5, 3), ('death', 'Dies', 0, 4),
    ('taunt', 'Player at <30% HP', 15, 1), ('player_dodge', 'Player dodges their attack', 12, 1), ('player_stagger', 'Player stance broken', 12, 1),
    ('idle_chat', 'Unaware pairs within 8 m', 45, 1), ('warn_player_in_shadow', 'Suspicious', 10, 1), ('ward_broken', 'Own Ward breaks', 6, 1),
    ('charge', 'Starts gap-closer', 8, 1), ('retreat', 'Moves to fallback point', 10, 1), ('victory', 'Player dies nearby', 0, 1), ('call_backup', 'Leader calls reinforcements', 20, 1)]])

LANGS = [('en-US', 'Voice + text', 'Source'), ('fr-FR', 'Voice + text', 'A093'), ('de-DE', 'Voice + text', 'A093'), ('es-ES', 'Voice + text', 'A093'),
         ('ja-JP', 'Voice + text', 'A093'), ('pt-BR', 'Text', 'plan 7.4: voice in 5, so A093 pt-BR VO dropped'), ('it-IT', 'Text', 'plan: text in 12'), ('pl-PL', 'Text', ''),
         ('ru-RU', 'Text', ''), ('ko-KR', 'Text', ''), ('zh-Hans', 'Text', ''), ('zh-Hant', 'Text', '')]
wr('vo_languages.csv', ['locale', 'scope', 'source', 'vo_lines'], [[l, s, src, 60000 if 'Voice' in s else 0] for l, s, src in LANGS])

# ---------------------------------------------------------------- ambience
AMB_LAYERS = [
 ('BED_DAY', 'Quad/7.1.4 bed, 4 min loop', 'Region day bed'), ('BED_NIGHT', 'Quad bed, 4 min loop', 'Region night bed'),
 ('WIND', 'RTPC Altitude + Wind_Speed', 'Wind by altitude and exposure'), ('WEATHER', 'State Weather', 'Rain/storm/snow/ash per region weather table'),
 ('WILDLIFE', 'Random one-shots 20-60 m, 3D', '8+ critter calls, day and night sets'), ('EMITTERS', 'Placed 3D emitters', 'Region set pieces (wreck wind, bells, machinery, surf)'),
 ('WEAVE_HUM', 'RTPC Shard_Proximity', 'Tonal hum near Shards and Anchors, tuned to region mode'), ('HOLLOWING', 'RTPC Hollowing 0-1', 'Low drone and dropouts; birds go silent at 1'),
 ('INTERIOR', 'Room tone per kit, convolution reverb', 'Caves, buildings, wreck interiors'), ('CITADEL', 'Room tone + emitters', 'Citadel interior bed'),
 ('WALLA', 'Crowd density RTPC', 'Settlement crowd'), ('WATER', 'Spline emitters', 'Rivers, shore, falls'),
]
REGION_DETAIL = {
 'REG_01': 'ash fall hiss, cooling hull metal ticks, distant forge hammers, ember crackle', 'REG_02': 'surf, gulls, rigging creak, storm thunder rolls, foghorns',
 'REG_03': 'canopy rustle, insects, frogs, creaking roots, clan drums far off', 'REG_04': 'glass grains singing in wind, wreck groans, servo whine, heat shimmer tone',
 'REG_05': 'snow crunch fields, ice cracking, wolves, choir-stone resonance', 'REG_06': 'cavern drips, deep machinery heartbeat, Hollowed moans, wind through bone',
 'REG_Q': 'ship ventilation, failing life-support alarms, vacuum quiet, alien choir in the hull', 'REG_U': 'reactor thrum, steam, conveyors, Remnant drone chatter',
 'REG_HUB': 'bridge consoles, chapel bells, market walla, smithy, ship hull settling'}
amb = []
for rid, det in REGION_DETAIL.items():
    code = PAL[rid][0]
    for lid, how, desc in AMB_LAYERS:
        if rid == 'REG_Q' and lid in ('WILDLIFE', 'WEATHER', 'WATER', 'WALLA'):
            continue
        if rid == 'REG_HUB' and lid in ('WILDLIFE', 'HOLLOWING', 'CITADEL'):
            continue
        amb.append([f'AMB_{code}_{lid}', rid, regions[rid]['name'], lid, how, desc, det if lid in ('BED_DAY', 'BED_NIGHT', 'EMITTERS') else ''])
wr('ambience_layers.csv', ['amb_id', 'region', 'region_name', 'layer', 'driver', 'description', 'region_specifics'], amb)

# ---------------------------------------------------------------- mix
MIX = [
 ('Loudness', 'Integrated, home (console/PC speakers)', '-24 LUFS +/-2', 'Measured over 30 min of mixed gameplay'),
 ('Loudness', 'Integrated, Night/Headphones mode', '-18 LUFS +/-2', 'Narrow dynamic range'),
 ('Loudness', 'True peak', '-1 dBTP max', 'Master limiter'),
 ('Loudness', 'Dialogue anchor', '-27 LUFS short-term for Ostra and cinematic lines', 'Everything else mixes around dialogue'),
 ('Loudness', 'Cinematics', '-24 LUFS integrated per cinematic', ''),
 ('Format', 'Output', '7.1.4 Atmos (PC/Xbox), Tempest 3D (PS5), 5.1, stereo, binaural headphones', 'Object audio for bosses and Ostra glitches'),
 ('Format', 'Masters', '48 kHz / 24-bit WAV; music stems 48/24 interleaved', ''),
 ('Format', 'Runtime codec', 'Vorbis q6 SFX, q4 ambience, Opus 96 kbps VO, ATRAC9/XMA per platform for music', 'Final per platform memory pass in P6'),
 ('Dynamic range', 'Modes', 'Home Theatre (wide), Standard (default), Night (narrow)', 'Options menu; maps to master compressor presets'),
 ('Buses', 'Master', 'Master > Music, SFX, VO, Ambience, UI, Cinematic', 'Each user-adjustable in options'),
 ('Buses', 'SFX children', 'Player, Weapons, Weave, Enemies, Bosses, Foley, World, Vehicles', ''),
 ('Buses', 'VO children', 'Ostra, Dialogue, Barks_Ally, Barks_Enemy, Announcer', 'STR_OPT_VOL_OSTRA gets its own slider'),
 ('Ducking', 'Ostra/dialogue speaks', 'Music -6 dB, Ambience -4 dB, Barks_Enemy -6 dB, 150 ms attack 600 ms release', 'Side-chain'),
 ('Ducking', 'Boss intro', 'All but Bosses and Music -12 dB for 4 s', ''),
 ('Ducking', 'Ward break / Stance break', 'Everything -3 dB 250 ms, high-shelf cut, so the break reads', 'Readability pillar'),
 ('HDR', 'Wwise HDR window', '24 dB window; priorities: boss telegraph > player hurt > Ward break > player weapon > enemy weapon > ambience', 'Telegraph sounds never masked'),
 ('Voices', 'Physical voice limit', 'PS5/XSX 128, PC 160, XSS 96; virtual voices unlimited with kill-quietest', ''),
 ('Voices', 'Per-sound limits', 'Footsteps 12, gunshots 24 (4 per gun), impacts 16, barks 3 at once, enemy deaths 4', ''),
 ('Spatial', 'Reverb', 'Wwise Spatial Audio rooms and portals, convolution IRs per kit (40 IRs)', ''),
 ('Spatial', 'Weapon tails', 'Indoor/outdoor/canyon/wreck tail switch by ray-cast room estimate', 'Plan 5.6'),
 ('Spatial', 'Attenuation', 'Gunshot audible 300 m with distant layer past 80 m; melee 40 m; footsteps 25 m (PvP 35 m)', 'Per-firearm falloff in firearm_classes'),
 ('Accessibility', 'Visual sound cues', 'Directional indicators for footsteps, gunfire, telegraphs (option)', ''),
 ('Accessibility', 'Mono and subtitles', 'Mono downmix option; subtitles on by default with speaker names and size options', ''),
 ('Memory', 'Budget', 'Resident 160 MB console (SFX banks + current region), streamed music and VO', ''),
]
wr('mix_standards.csv', ['area', 'item', 'standard', 'notes'], MIX)

# ---------------------------------------------------------------- event map from SFX tab + music + VO
try:
    import openpyxl
    wb = openpyxl.load_workbook(os.path.join(GP, 'shardfall-assets.xlsx'), read_only=True, data_only=True)
    sfx = [r for r in wb['SFX'].iter_rows(min_row=2, values_only=True) if r[0]]
except Exception as e:
    print('SFX tab not read:', e); sfx = []
ev, seen = [], Counter()
for sid, grp, owner, event, varn, *_ in sfx:
    name = f'Play_SFX_{tok(grp)}_{tok(owner or "")}_{tok(event or "")}'[:120]
    seen[name] += 1
    if seen[name] > 1:
        name += f'_{seen[name]}'
    bank = 'SB_' + tok(grp)
    ev.append([name, 'SFX', sid, bank, varn])
# SFX asset hooks: first matching rule in tools/sfx_hook_rules.csv names the event; a hook with no rule gets its own pending event (batch 5)
with open(os.path.join(OUT, 'tools', 'sfx_hook_rules.csv'), newline='', encoding='utf-8') as f:
    HRULES = [(re.compile(r['pattern']), r['wwise_event']) for r in csv.DictReader(f)]
known, hmap = {e[0] for e in ev}, []
for h in rd('assets/asset_hooks.csv'):
    if h['kind'] != 'SFX':
        continue
    e = next((m.expand(t) for p, t in HRULES if (m := p.fullmatch(h['hook']))), None)
    if e and e not in known:
        raise SystemExit(f"sfx_hook_rules.csv: {h['hook']} names unknown event {e}")
    hmap.append([h['hook'], e or 'Play_' + h['hook'], 'mapped' if e else 'pending'])
pending = [r for r in hmap if r[2] == 'pending']
ev += [[e, 'SFX', hk, 'SB_' + hk.split('_')[1], 1] for hk, e, _ in pending]
wr('sfx_hook_map.csv', ['hook', 'wwise_event', 'status'], hmap)
os.makedirs(os.path.join(OUT, 'samples', 'full', 'sfx_b5'), exist_ok=True)
wr('samples/full/sfx_b5/manifest.csv', ['event_id', 'file', 'duration_s', 'sources', 'status'], [[e, '', '', '', 'pending'] for _, e, _ in pending])
for m in music:
    ev.append(['Play_' + m[0], 'Music', m[0], 'MB_' + m[0].split('_')[1], m[7]])
for c in cast:
    if c[5]:
        ev.append(['Play_' + c[0], 'VO (dialogue event, line chosen by Wwise dialogue path)', c[0], 'VB_' + c[0][3:], c[5]])
for a in amb:
    ev.append(['Play_' + a[0], 'Ambience', a[0], 'AB_' + a[0].split('_')[1], 1])
wr('event_map.csv', ['wwise_event', 'kind', 'source_id', 'soundbank', 'variations_or_lines'], ev)

# ---------------------------------------------------------------- summary
tot = Counter(); mins = Counter()
for m in music:
    tot[m[1]] += 1; mins[m[1]] += m[12]
    if m[13]: tot['_slice'] += 1
with open(os.path.join(OUT, 'summary.txt'), 'w') as f:
    f.write('Music cues by category (count, unique minutes)\n')
    for k in tot:
        f.write(f'  Vertical slice (subset): {tot[k]} cues\n' if k == '_slice' else f'  {k}: {tot[k]} cues, {mins[k]:.1f} min\n')
    f.write(f'  TOTAL: {len(music)} cues, {sum(mins.values()):.1f} min\n')
    f.write(f'VO: {sum(c[5] for c in cast)} English lines in {len(cast)} cast rows from the campaign voice budget (plan counts 120 voiced characters; one actor can voice several townsfolk)\n')
    f.write(f'VO lines all languages: {sum(c[5] for c in cast) * 5}\n')
    f.write(f'Ambience layers: {len(amb)}\nWwise events: {len(ev)}\n')
print(open(os.path.join(OUT, 'summary.txt')).read())
