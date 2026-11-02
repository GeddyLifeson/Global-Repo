#!/usr/bin/env python3
"""Generates every Shardfall cinematics table from the beat lists below.
Beats are hand-written; shots are expanded from beats by the camera language rules
(LANG). Story comes from design/campaign/ (owner: campaign thread). Lines are
placeholders DLG_<cin>_<nn>; the writing thread owns the words.
Run: python3 design/cinematics/tools/gen_cinematics.py
"""
import csv, os, math
OUT = os.path.join(os.path.dirname(__file__), '..')

# ---------------------------------------------------------------- camera language
# beat type -> list of (share of beat time, shot size, lens mm, height, move, framing note)
LANG = {
 'EST':    [(.6,'XWS',18,'High crane','Crane down 6 m','Location reads first; horizon on upper third'),
            (.4,'WS',24,'Eye','Dolly in 1 m','Subject enters frame on the left third')],
 'VISTA':  [(1.,'XWS',18,'High','Slow pan 20 deg','Landmark on a third; sky 2/3 of frame')],
 'REVEAL': [(.5,'LS',24,'Low (0.6 m)','Push in 2 m','Subject backlit, silhouette first'),
            (.25,'MCU',50,'Low','Static','Hold on face or mask'),
            (.25,'CU',85,'Eye','Slow push 0.2 m','Eyes on upper third')],
 'DLG':    [(.4,'OTS',50,'Eye','Static','Speaker on the third away from the listener shoulder'),
            (.35,'CU',85,'Eye','Static','Speaker; lead room toward listener'),
            (.25,'CU',85,'Eye','Static','Listener reaction')],
 'VO':     [(.6,'CU',85,'Eye','Push in 0.1 m','Player face; Ostra has no body, so we hold on the listener'),
            (.4,'ECU',100,'Eye','Static','Chest Shard pulses with each syllable')],
 'ACTION': [(.3,'MS',35,'Eye','Handheld follow','Keep screen direction'),
            (.25,'WS',24,'Eye','Handheld track','Geography shot: who is where'),
            (.2,'CU',50,'Eye','Handheld','Impact or face'),
            (.25,'MS',35,'Low','Whip pan to next subject','Exit on motion')],
 'INSERT': [(1.,'ECU',100,'Matched','Static','Object fills 2/3 of frame')],
 'PLAYER': [(1.,'MS',35,'Eye','Orbit 30 deg','Hero shot of the player in their own armor')],
 'MEM':    [(.5,'MS',40,'Eye','Handheld drift','Memory: 2.39:1 matte, cold grade, frame flicker'),
            (.5,'CU',75,'Eye','Slow push','Memory: shallow focus, focus breathes')],
 'REACT':  [(1.,'CU',85,'Eye','Static','Reaction; hold 12 frames past the beat')],
 'TITLE':  [(1.,'CARD',0,'-','-','Act title card over black, then fade up')],
 'TRANS':  [(1.,'MS',35,'Gameplay','Blend to gameplay camera 1.0 s','Last frame matches gameplay camera transform')],
 'CROWD':  [(.6,'WS',28,'Eye','Lateral track 3 m','Crowd layered in 3 depths'),
            (.4,'MS',40,'Eye','Static','Single face picked from crowd')],
 'POV':    [(1.,'POV',30,'Player eye','Handheld breath','First person; no HUD')],
 'CHOICE': [(1.,'MCU',50,'Eye','Slow orbit 10 deg','Interactive: choice UI on the right third; camera idles until input')],
 'PLAY':   [(1.,'POV',35,'Fixed','Locked; slow 2% push per prompt','Playable: interface fills frame through cracked glass; prompts centre; no HUD')],
}

def B(t, secs, subject, action, speaker='', vfx=''):
    return (t, secs, subject, action, speaker, vfx)

# ---------------------------------------------------------------- cinematics
# kind: CUT = authored cutscene (counts to plan 5.7), IGC = in-game camera moment,
#       CARD = title card. tier: A full previs + performance capture, B previs + mocap
#       pickups, C in-engine blocking from stock animation.
C = []
def cin(cid, title, quest, region, kind, tier, trigger, cast, location, music, variants, beats, cond='Always'):
    C.append(dict(cin_id=cid, title=title, quest_id=quest, region=region, kind=kind, tier=tier,
                  trigger=trigger, condition=cond, cast=cast, location=location, music_cue=music,
                  variants=variants, beats=beats))

P = 'Player'
# Prologue
cin('CIN_OPEN','The Fall of the Meridian','MQ_P_01','REG_01','CUT','A','New game start','Ires (voice), Ostra (voice), Old Tomas, Player',
 'Meridian bridge (900 years ago), Spinegate cryo ward','MUS_CIN_OPENING','Player body type A/B (pod reveal)',[
 B('TITLE',6,'Black','Studio and title cards over a slow heartbeat'),
 B('MEM',20,'Meridian bridge','Alarms; crew silhouettes through cryo glass, frost creeping','', 'VFX_CIN_FROST_GLASS'),
 B('MEM',18,'Second star','A light in the viewport grows; the bridge goes quiet'),
 B('VO',8,'Cryo glass','A woman\'s voice: "Accept." Then static','Ires'),
 B('PLAY',90,'Ship interface','PLAYABLE (story pass A): the player drives an unnamed ship system on cracked cryo glass. Prompts in order: "Seal bulkheads", "Vent core coolant", "Override bridge command". Reads like a drill. Each input is logged for CIN_MUTINY','', 'VFX_CIN_HOLO_FLICKER'),
 B('ACTION',20,'Meridian','The last input lands; the hull splits; Shards scatter like burning seeds','', 'VFX_CIN_HULL_BREAK'),
 B('VISTA',12,'Veyl','The ship breaks over the continent; pieces fall toward six future regions'),
 B('TITLE',6,'Black','"900 years after the Fall"'),
 B('EST',14,'Spinegate cryo ward','Dust, dead pods, one pod still lit (Bay 9)'),
 B('POV',18,P,'Frosted glass, muffled hammering, the lid cracks','', 'VFX_CIN_POD_STEAM'),
 B('DLG',14,'Old Tomas','Pulls the player out by the arm; "Easy. You are the first to breathe in here in my lifetime."','Old Tomas'),
 B('REVEAL',16,P,'Player stands in the pod light for the first time; body still undefined'),
 B('DLG',22,'Old Tomas','He sees the Shard glowing in the player\'s chest and steps back','Old Tomas'),
 B('INSERT',8,'Chest Shard','The Shard flickers once as if waking'),
 B('ACTION',20,'Hollowed','Two Hollowed shamble out of a pod row; Tomas raises a lantern','Old Tomas'),
 B('POV',10,'Cryo scanner','The scanner sweeps the player: character creation begins','', 'VFX_CIN_SCAN_GRID'),
 B('TRANS',14,P,'Fade into the character creator camera'),
])
cin('CIN_SPINE_ANCHOR','First Anchor','MQ_P_02','REG_01','IGC','C','Player lights first Anchor','Player, Old Tomas',
 'Spine, first Anchor','', '',[
 B('PLAYER',6,P,'Player kneels and touches the Anchor'),
 B('INSERT',4,'Anchor','Ember climbs the Anchor in rings','', 'VFX_ANCHOR_LIGHT'),
 B('DLG',6,'Old Tomas','"When you fall, you come back here. Mostly whole."','Old Tomas'),
 B('TRANS',4,P,'Back to play'),
])
cin('CIN_ACT1_TITLE','Into Cinderreach','MQ_P_02','REG_01','CUT','B','Exit Spinegate lower door','Player, Ostra (voice)',
 'Spinegate lower door, Cinderreach','MUS_CIN_ACT1_INTRO_OSTRA','',[
 B('POV',6,P,'The lower door grinds open; daylight floods in'),
 B('PLAYER',6,P,'Player steps onto the ledge'),
 B('VISTA',14,'Cinderreach','Ash plains, kiln smoke, the Spine behind'),
 B('VO',8,P,'"Bay 9. You were not scheduled to wake. Neither was I."','Ostra'),
 B('VO',6,P,'Confident and wrong (story pass B): "The core failed. Reactor fatigue. I logged it."','Ostra'),
 B('TITLE',6,'Card','ACT ONE: EMBER AND SALT'),
 B('TRANS',5,P,'Back to play'),
])
cin('CIN_OFFICER_HUSH','There You Are','MQ_P_02','REG_01','IGC','B','Crew officer mini-boss at 10% health','Player, Hollowed crew officer (Hush voice)',
 'The Spine','', '',[
 B('ACTION',3,'Crew officer','The officer freezes mid-swing'),
 B('REVEAL',5,'Crew officer','His head tilts; the Hollow light in his eyes steadies'),
 B('DLG',6,'Hush','In a calm voice that isn\'t his: "There you are. We\'ve been counting."','Hush'),
 B('ACTION',4,'Crew officer','He dies standing, then falls'),
 B('TRANS',2,P,'Back to play'),
])
# Act 1
cin('CIN_KILN_BURN','Smoke on the Hills','MQ_A1_01','REG_01','IGC','C','Reach the ridge above the hamlet','Player, Old Tomas, Pyre-Wardens',
 'Ridge over the burning hamlet','', '',[
 B('EST',10,'Hamlet','Pyre-Wardens torch the roofs; villagers run','', 'VFX_FIRE_LARGE'),
 B('DLG',8,'Old Tomas','"People or the Anchor. We can\'t reach both."','Old Tomas'),
 B('CHOICE',8,P,'Choice: save the people or the Anchor'),
 B('TRANS',4,P,'Back to play'),
])
cin('CIN_HUB_ARRIVE','Lantern Hold','MQ_A1_03','REG_HUB','CUT','A','Reach the Hold gate','Player, companion, Kessa Vane, Ostra (voice), Clerk Imre',
 'Lantern Hold, built in the Meridian\'s bridge section','', 'Companion present or absent',[
 B('EST',14,'Lantern Hold','The bridge section of the Meridian, half buried, lit by a thousand lanterns'),
 B('CROWD',14,'Market','Traders, Knights, Choir in pale robes; children chase a drone'),
 B('PLAYER',8,P,'Player walks the main stair'),
 B('VO',10,P,'Ostra, quiet: "This was my bridge."','Ostra'),
 B('EST',12,'Council chamber','The four Council seats and the empty Speaker\'s chair with a black candle'),
 B('DLG',24,'Hold Council','Marr, Hale, Quell and Lisk argue about the Hollowing and the second star','Iselde Marr'),
 B('DLG',14,'Clerk Imre','Imre announces the stranger from Bay 9','Clerk Imre'),
 B('REACT',6,'Hold Council','The room turns to the player'),
 B('DLG',12,'Precentor Lisk','"Kindled. The Choir has waited a long time for you."','Precentor Lisk'),
 B('TRANS',6,P,'Hand off to the conversation camera'),
])
cin('CIN_CAPTAIN_CHAIR','The Captain\'s Chair','MQ_A1_03','REG_HUB','IGC','C','Player sits in the captain\'s chair (optional)','Player, Ostra (voice)',
 'Lantern Hold bridge','', '',[
 B('PLAYER',8,P,'Player sits; the old console lights up under dust'),
 B('INSERT',6,'Console','A single line: BAY 9 // STATUS: AWAKE','', 'VFX_CIN_HOLO_FLICKER'),
 B('VO',6,P,'Ostra says nothing; the Shard dims','Ostra'),
 B('TRANS',4,P,'Back to play'),
])
cin('CIN_SECOND_STAR','The Second Star','MQ_A1_04','REG_HUB','CUT','A','Look through the Choir lens','Player, Precentor Lisk, Ostra (voice)',
 'Choir observatory, Lantern Hold','', '',[
 B('EST',10,'Observatory','The great Choir lens on its brass ring; night sky'),
 B('DLG',14,'Precentor Lisk','"Every child in Veyl knows the second star. Look closer."','Precentor Lisk'),
 B('POV',16,'Choir lens','Through the lens: the star is a ring-ship, turning, enormous','', 'VFX_CIN_LENS_ZOOM'),
 B('INSERT',4,'Chest Shard','The Shard flares red'),
 B('VO',10,P,'Ostra, panicked and fast: "Close it. Close it. Close it."','Ostra'),
 B('REACT',6,P,'Player stumbles back from the lens'),
 B('DLG',14,'Precentor Lisk','Lisk, gently: "It frightens you. It frightened me too, once."','Precentor Lisk'),
 B('REVEAL',10,'The Quiet','Slow push on the lens as the ring turns away'),
 B('TRANS',6,P,'Back to play'),
])
SB = [('VAEL','Vael the Ember Regent','MQ_A1_05','REG_01','Vael\'s Pyre-Court','"The core didn\'t fail. Somebody opened it."',1,'VFX_FIRE_LARGE'),
      ('CORSA','Corsa, Storm Admiral','MQ_A1_08','REG_02','The Beached Ark, in a storm','"We had a heading out. She turned us down."',2,'VFX_CIN_STORM_RAIN'),
      ('SORREL','Sorrel of the Bloom','MQ_A2_02','REG_03','Heartwood, Thornwood','"The captain said yes."',3,'VFX_CIN_POLLEN'),
      ('BRANNOCH','Brannoch Iron-Choir','MQ_A2_03','REG_04','The Anvil, Glasswaste','"My oath was to Ires. It still is."',4,'VFX_CIN_SPARKS'),
      ('RIME','Mother Rime','MQ_A2_04','REG_05','The Still Lake, Rimefall','"Thirty-seven thousand pods. I counted them all."',5,'VFX_CIN_FROST_GLASS'),
      ('HOLLOWTWINS','The Hollow Twins','MQ_A2_05','REG_06','The Twin Thrones, Hollowdeep','"We heard the hail. We heard what it offered."',6,'VFX_CIN_HOLLOW_MOTES')]
MEMS = {1:'The hail from the Quiet reaches the bridge', 2:'The crew votes; the vote is close', 3:'Hydroponics: Sorrel hears the offer on the open channel',
        4:'Brannoch swears his guard to Ires in the armory', 5:'The cryo bays: Ostra counts the pods as power fails', 6:'Ires alone on the bridge, the Twins at the door'}
for sid, name, q, reg, loc, lucid, n, vfx in SB:
    cin(f'CIN_BOSS_{sid}', f'{name}', q, reg, 'CUT', 'A', 'Cross the boss fog gate', f'Player, {name}', loc, '', 'Co-op: all players shown',[
     B('EST',6,loc,'The arena, wide, the boss unseen','', vfx),
     B('REVEAL',12,name,'The Shard-bearer turns; their Heart Shard burns in their chest'),
     B('DLG',6,name,'One line of challenge, half lucid',name),
     B('ACTION',4,name,'Boss takes stance; health bar slams in'),
     B('TRANS',2,P,'Blend to lock-on camera'),
    ])
    cin(f'CIN_LUCID_{sid}', f'{name}: lucid moment', q, reg, 'CUT', 'A', 'Boss defeated', f'Player, {name}, Ostra (voice)', loc,
        'MUS_CIN_ACT2_SHARD_1' if n > 2 else '', 'Heart Shard Take or Spare; Ostra reaction by CNT_LUCID_HEARD 1-6',[
     B('ACTION',4,name,'The Shard-bearer falls to their knees'),
     B('REVEAL',6,name,'The Hollowing drains from their face for a moment'),
     B('DLG',8,name,lucid,name),
     *( [B('DLG',5,name,'Corsa hears Ostra in the player: "Ostra? You\'re in there?" (story pass H)',name)] if sid == 'CORSA' else [] ),
     B('VO',4,P,'Ostra reacts; line set by CNT_LUCID_HEARD (1 "They are mad" to 6 "Stop telling me this")','Ostra'),
     B('INSERT',3,'Heart Shard','The Heart Shard hangs in the air between them'),
     B('CHOICE',5,P,'Choice: Take or Spare the Heart Shard'),
    ])
    cin(f'CIN_MEM_{n}', f'Memory fragment {n}', q, reg, 'CUT', 'A', 'Heart Shard taken', 'Ostra (voice), Meridian crew, Ires', 'Meridian (900 years ago)',
        'MUS_CIN_ACT3_OSTRA_MEMORY' if n == 1 else '', '', [
     B('INSERT',3,'Heart Shard','The Shard dissolves into the player\'s chest','', 'VFX_CIN_SHARD_ABSORB'),
     B('MEM',14,'Meridian',MEMS[n]),
     B('MEM',14,'Meridian crew','Faces we will later meet as Shard-bearers, younger, human'),
     B('VO',6,P,'Ostra names what she just remembered','Ostra'),
     B('TRANS',3,P,'Back to play'),
    ], cond=f'FLG_HEART_{n}_TAKEN')
CITB = [('SPINEGATE','Warden of Spinegate','MQ_A1_05C','REG_01'),('CANTOR','The Drowned Cantor','MQ_A1_07','REG_02'),
        ('HALDEN','Ser Halden Unburied','MQ_A2_02C','REG_03'),('GRAFTED','Grafted Engine','MQ_A2_03C','REG_04'),
        ('YSSE','Choir Mother Ysse','MQ_A2_04C','REG_05'),('LAMPLIGHTER','The Lamplighter','MQ_A2_05C','REG_06')]
for sid, name, q, reg in CITB:
    cin(f'CIN_BOSS_{sid}', name, q, reg, 'IGC', 'B', 'Cross the boss fog gate', f'Player, {name}', 'Citadel boss arena', '', '',[
     B('REVEAL',8,name,'Boss reveal: silhouette, then light catches it'),
     B('ACTION',4,name,'Signature pose; health bar slams in'),
     B('TRANS',3,P,'Blend to lock-on camera'),
    ])
cin('CIN_TIDEWATCH_SIEGE','Storm Coast','MQ_A1_06','REG_02','IGC','C','Reach Stiltmarket walls','Player, Harbormaster Moss, drowned fleet',
 'Stiltmarket harbour','', '',[
 B('VISTA',8,'Saltmere','Corsa\'s drowned fleet shelling Stiltmarket through fog','', 'VFX_CIN_STORM_RAIN'),
 B('DLG',10,'Harbormaster Moss','"They\'re still fighting a war that ended before my grandmother."','Harbormaster Moss'),
 B('ACTION',8,'Harbour','A shell hits the sea wall'),
 B('TRANS',4,P,'Back to play'),
])
cin('CIN_ARK_BOARD','Boarding the Ark','MQ_A1_08','REG_02','IGC','B','Use the signal codes','Player, companion',
 'The Beached Ark','', '',[
 B('INSERT',4,'Signal lamp','Player flashes Corsa\'s codes'),
 B('EST',10,'Beached Ark','Lightning shows the flagship on the rocks; the boarding ramp drops','', 'VFX_CIN_STORM_RAIN'),
 B('PLAYER',8,P,'Player and companion climb into the rain'),
 B('TRANS',4,P,'Back to play'),
])
cin('CIN_ACT1_END','The Column','MQ_A1_08','REG_02','CUT','A','After Corsa\'s Heart choice','Player, companion, Ostra (voice), Stiltmarket crowd',
 'Saltmere coast at dusk','MUS_CIN_ACT1_END','',[
 B('PLAYER',8,P,'Player stands on the Ark\'s deck after the storm'),
 B('VISTA',16,'Saltmere sea','The sea starts to glow: Shards rise from the seabed','', 'VFX_CIN_SHARD_COLUMN'),
 B('REVEAL',20,'The Quiet','A column of Shards climbs into the sky toward the second star'),
 B('CROWD',14,'Stiltmarket','People on the walls watch, silent; a child points'),
 B('REVEAL',10,'Lamplighter figure','On a far cliff a masked lamplighter (Ires, unnamed) lifts a Shard to the column (story pass C)','', 'VFX_CIN_SHARD_COLUMN'),
 B('REACT',6,P,'Player watches'),
 B('VO',10,P,'"I know that ship."','Ostra'),
 B('VISTA',20,'Sky','The column thins; the second star brightens'),
 B('DLG',14,'Companion','Companion asks what Ostra means (line per companion)','Companion'),
 B('TITLE',6,'Card','END OF ACT ONE'),
 B('TRANS',6,P,'Fade to Lantern Hold'),
])
# Act 2
cin('CIN_COUNCIL_VOTE','The Council\'s Errand','MQ_A2_01','REG_HUB','CUT','A','Enter the Council chamber after Act 1','Player, Hold Council, Clerk Imre',
 'Council chamber','', '',[
 B('TITLE',6,'Card','ACT TWO: THE FOUR HEARTS'),
 B('EST',8,'Council chamber','Packed gallery'),
 B('DLG',16,'Iselde Marr','Marr: only a Kindled survives a Shard-bearer','Iselde Marr'),
 B('DLG',14,'Hale','Hale argues for caution','Hale'),
 B('CROWD',8,'Gallery','Murmur rises'),
 B('INSERT',6,'Vote stones','Four stones drop into the bowl, one at a time'),
 B('DLG',10,'Clerk Imre','Imre reads the vote: the player goes','Clerk Imre'),
 B('DLG',22,'Hold Council','Each leader offers a route reward','Petra Quell'),
 B('CHOICE',6,P,'Choice: Knights escort, Church map, Guild Strider, Choir lens'),
 B('TRANS',4,P,'Back to play'),
])
for r, name, q in [('02','Saltmere','MQ_A1_06'),('03','Thornwood','MQ_A2_02'),('04','Glasswaste','MQ_A2_03'),('05','Rimefall','MQ_A2_04'),('06','Hollowdeep','MQ_A2_05')]:
    cin(f'CIN_REG_ARRIVE_{r}', f'{name}', q, f'REG_{r}', 'IGC', 'C', 'First entry into the region', P, f'{name} border', '', '',[
     B('VISTA',10,name,'Region establishing vista from the border road'),
     B('TITLE',3,'Card',f'Region name lower third: {name}'),
     B('TRANS',2,P,'Back to play'),
    ])
HUSH_RT = {'01':'"Hello, ship."','02':'"You are smaller than we remember."','03':'"Your people are doing so well. Look how much they\'ve grown."',
           '04':'"We see the one carrying you."','05':'"Soon."','06':'"Thank you for keeping it warm."','Q':'Hush answers her ping from inside the Quiet'}
RT = {'01':'"These towers were ours. Escape-pod beacons. I can see again."','02':'Ostra recognises the Glass War wrecks as Meridian lifeboats',
      '03':'Hydroponics bay coordinates; Sorrel was its chief','04':'The engine fragments under the glass; Remnant still pinging her',
      '05':'Cryo coolant tanks; she refuses to count the pods','06':'The tower is half Hollowed; the map shows land missing','Q':'A Maker relay; Hush answers her ping'}
for r, line in RT.items():
    reg = 'REG_Q' if r == 'Q' else f'REG_{r}'
    cin(f'CIN_RT_{r}', 'Relay Tower', f'MQ_RT_{r}', reg, 'IGC', 'C', 'Activate the tower beacon', 'Player, Ostra (voice), Hush (voice)', 'Relay Tower summit', '', '',[
     B('INSERT',3,'Beacon','The beacon lights','', 'VFX_CIN_BEACON'),
     B('VISTA',12,'Region','The map fills in: fog lifts across the region in a ring','', 'VFX_CIN_MAP_REVEAL'),
     B('VO',10,P,line,'Ostra'),
     B('INSERT',3,'Beacon','The beacon static turns into a voice'),
     B('DLG',6,'Hush',f'Hush answers once (story pass C): {HUSH_RT[r]}','Hush'),
     B('REACT',3,P,'Player; the Shard dims'),
     B('TRANS',3,P,'Back to play'),
    ])
cin('CIN_RIME_PODS','The Ice Pods','MQ_A2_04','REG_05','IGC','C','Enter the Still Lake','Player, Elder Yuri',
 'The Still Lake','', '',[
 B('EST',8,'Still Lake','Hundreds of villagers frozen in ice pods','', 'VFX_CIN_FROST_GLASS'),
 B('DLG',8,'Elder Yuri','"My grandson is in the third row."','Elder Yuri'),
 B('CHOICE',6,P,'Choice: thaw the pods or leave them'),
])
cin('CIN_LAMPLIGHTER_UNMASK','The Mask Falls','MQ_A2_05C','REG_06','CUT','A','Lamplighter at 30% health','Player, The Lamplighter (Ires)',
 'The Lamp Works','', '',[
 B('ACTION',6,'The Lamplighter','A heavy hit cracks the mask'),
 B('INSERT',4,'Mask','The mask hits the floor; a Meridian captain\'s insignia on the collar'),
 B('REVEAL',8,'The Lamplighter','Half a face, old and human, eyes on the player\'s Shard'),
 B('DLG',6,'The Lamplighter','"Not yet."','Captain Edda Ires'),
 B('ACTION',8,'The Lamplighter','She drops through a lamp shaft and is gone','', 'VFX_CIN_LAMP_SMOKE'),
 B('VO',4,P,'Ostra, barely a whisper: "Captain."','Ostra'),
 B('TRANS',4,P,'Back to play'),
])
cin('CIN_OSTRA_STOP','Stop Collecting','MQ_A2_06','REG_HUB','CUT','A','Rest at an Anchor after hearing all six lucid lines','Player, Ostra (voice)',
 'Any Anchor','', '', [
 B('PLAYER',8,P,'Player sits at the Anchor; the fire low'),
 B('VO',16,P,'Ostra asks the player to stop collecting the lucid lines (story pass G)','Ostra'),
 B('INSERT',4,'Chest Shard','The Shard flickers cold blue'),
 B('VO',10,P,'She almost says it, then does not','Ostra'),
 B('TRANS',4,P,'Back to play'),
], cond='CNT_LUCID_HEARD = 6')
cin('CIN_MUTINY','The Missing Forty Minutes','MQ_A2_06','REG_U','CUT','A','Play the memory Shard at the core housing','Ostra, Captain Edda Ires, Meridian crew, Hush (voice)',
 'Meridian bridge and core (900 years ago)','MUS_CIN_ACT3_OSTRA_MEMORY','Shard-bearer faces match which Hearts were taken (lighting only); Ostra admits the player was right if CNT_OSTRA_CONTRADICTIONS >= 3 and confronted',[
 B('INSERT',4,'Memory Shard','Player sets the cut memory in the core housing','', 'VFX_CIN_SHARD_ABSORB'),
 B('MEM',20,'Meridian bridge','Bridge at full crew, quiet night shift'),
 B('MEM',16,'Comms console','The hail: a calm voice, always "we"'),
 B('DLG',30,'Hush','The offer: land, safety, a new world for every sleeper, in exchange for the ship\'s Shard core','Hush'),
 B('DLG',30,'Crew','The vote; Brannoch, Sorrel, Rime among the crew','Captain Edda Ires'),
 B('MEM',16,'Captain Edda Ires','Ires alone at the captain\'s chair'),
 B('DLG',10,'Captain Edda Ires','"Accept."','Captain Edda Ires'),
 B('MEM',20,'Ostra','Ostra\'s interface locks out, line by line','', 'VFX_CIN_HOLO_FLICKER'),
 B('DLG',24,'Ostra','Ostra argues with Ires over the open channel (Ostra\'s voice heard by all on the bridge)','Ostra'),
 B('ACTION',24,'Bridge','Hull Knights seize the bridge; crew fight crew'),
 B('PLAY',20,'Ship interface','REPLAY of the opening: the same cracked-glass interface and the exact prompts the player obeyed, now labelled OSTRA (story pass A)','', 'VFX_CIN_HOLO_FLICKER'),
 B('MEM',14,'Core','Seen from outside this time: each input vents, seals and overrides; the reactor climbs past red','', 'VFX_CIN_CORE_OVERLOAD'),
 B('TITLE',4,'Card','The inputs were yours. You were Ostra.'),
 B('DLG',18,'Ostra','Ostra to the sleepers she can\'t warn','Ostra'),
 B('INSERT',6,'Core','The core breaches'),
 B('ACTION',30,'Meridian','The Fall from inside: corridors tearing open, pods tumbling'),
 B('MEM',24,'Cryo bays','Pod lights go out, rank after rank'),
 B('TITLE',6,'Card','37,000 sleepers died in the Fall'),
 B('VISTA',30,'Veyl','The Fall again, the same shot as the opening, now understood'),
 B('POV',20,P,'Back in the Undervault, the memory Shard cracks'),
 B('REACT',10,P,'Player in silence; the chest Shard is dark'),
 B('TRANS',22,P,'Long hold; Ostra does not speak. Back to play with no Ostra HUD'),
])
cin('CIN_OSTRA_RETURN','You Should Have Left Me in the Dark','MQ_A2_07','REG_HUB','CUT','B','Silence quest complete','Player, Ostra (voice)',
 'Lantern Hold, the captain\'s chair','', 'Told the Council or hid it',[
 B('PLAYER',10,P,'Player alone on the dark bridge'),
 B('INSERT',4,'Chest Shard','The Shard warms, slowly'),
 B('VO',14,P,'"You should have left me in the dark."','Ostra'),
 B('VO',12,P,'Line depends on the Council choice (truth or hidden)','Ostra'),
 B('TRANS',5,P,'Back to play; Ostra HUD returns'),
])
cin('CIN_IRES_TOWER','The Captain\'s Mask','MQ_A2_08','REG_06','CUT','A','Reach the hidden lamp tower top','Player, Captain Edda Ires, Ostra (voice)',
 'Hidden lamp tower, Hollowdeep','', '',[
 B('EST',10,'Lamp tower','A tower of stolen lamps; a beam of Shard light goes up into the sky','', 'VFX_CIN_SHARD_COLUMN'),
 B('REVEAL',14,'Captain Edda Ires','Ires, unmasked, feeding a Shard into the beam; she doesn\'t turn'),
 B('DLG',12,'Captain Edda Ires','"Hello, Ostra. You got old."','Captain Edda Ires'),
 B('VO',10,P,'Ostra and Ires speak for the first time in 900 years','Ostra'),
 B('DLG',18,'Captain Edda Ires','She sits, unarmed, and waits','Captain Edda Ires'),
 B('TRANS',6,P,'Hand off to the conversation camera (180-line branching scene)'),
])
cin('CIN_IRES_PARTING','Parting','MQ_A2_08','REG_06','CUT','B','Ires conversation ends','Player, Captain Edda Ires',
 'Hidden lamp tower','', 'Attack (she escapes), let go, offer a way out (IRES_RECRUITABLE)',[
 B('DLG',10,'Captain Edda Ires','Last line, per choice','Captain Edda Ires'),
 B('ACTION',12,'Captain Edda Ires','Per choice: she escapes up the beam, walks away, or lays down her sidearm'),
 B('TRANS',6,P,'Back to play'),
])
cin('CIN_CRADLE_ASSAULT','Choirborn','MQ_A2_09','REG_HUB','IGC','B','Wave 1 of the Cradle defense','Player, Petra Quell, Choirborn',
 'The Cradle','MUS_CIN_ACT2_SHARD_4','',[
 B('EST',8,'Cradle','The restored shuttle on its rails'),
 B('REVEAL',10,'Choirborn','First Choirborn drop from the sky in pale light','', 'VFX_CIN_CHOIRBORN_DROP'),
 B('DLG',4,'Petra Quell','"Hold the doors!"','Petra Quell'),
 B('TRANS',3,P,'Back to play'),
])
cin('CIN_ACT2_END','Launch','MQ_A2_09','REG_HUB','CUT','A','Fifth wave cleared','Player, companion, Petra Quell, Iselde Marr, Ostra (voice)',
 'The Cradle','MUS_CIN_ACT3_ASCENT','Companion in co-pilot seat',[
 B('PLAYER',10,P,'Player walks up the shuttle ramp; Hold crews cheer'),
 B('CROWD',12,'Cradle','Knights and Guild crews pull the clamps'),
 B('DLG',12,'Petra Quell','"She\'ll fly. Once."','Petra Quell'),
 B('INSERT',6,'Cockpit','Old Meridian controls wake under the player\'s hand','', 'VFX_CIN_HOLO_FLICKER'),
 B('VO',10,P,'Ostra takes the shuttle\'s systems: "I remember how to do this."','Ostra'),
 B('ACTION',24,'Shuttle','Engines fire; the shuttle rides the rail out of the Cradle','', 'VFX_CIN_ENGINE_BURN'),
 B('VISTA',24,'Veyl','Climb through cloud; all six regions below'),
 B('POV',14,P,'The second star grows into the Quiet'),
 B('REVEAL',20,'The Quiet','The ring-ship fills the frame'),
 B('TITLE',6,'Card','END OF ACT TWO'),
 B('TRANS',6,P,'Cut to black'),
])
# Act 3
cin('CIN_BETRAYAL','Betrayal at the Cradle','MQ_A3_01','REG_HUB','CUT','A','Act 3 start (plays as a flashback to the launch)','Player, Precentor Lisk, active companion, Choirborn',
 'The Cradle','', 'QST_CH_09 done: Lisk holds the door and dies; not done: Lisk opens the door and the companion holds it',[
 B('INSERT',4,'Door controls','A pale hand on the Cradle door lever'),
 B('REVEAL',10,'Precentor Lisk','Lisk, eyes wet, opening the doors (or bracing them, by variant)'),
 B('ACTION',20,'Cradle','Choirborn flood in under launch'),
 B('DLG',12,'Companion','The active companion stays behind at the door','Companion'),
 B('REACT',6,P,'Player in the cockpit, unable to leave'),
 B('ACTION',16,'Shuttle','The shuttle tears free of the rail, damaged','', 'VFX_CIN_ENGINE_BURN'),
 B('POV',12,P,'Through the rear port: the door closes on the companion'),
 B('DLG',14,'Precentor Lisk','Lisk\'s last line (variant)','Precentor Lisk'),
 B('TRANS',6,P,'Hard cut to the Quiet'),
])
cin('CIN_RING_CRASH','The Threshing Ring','MQ_A3_02','REG_Q','CUT','A','After CIN_BETRAYAL','Player, Ostra (voice)',
 'The Quiet, outer ring','', '',[
 B('TITLE',6,'Card','ACT THREE: THE QUIET'),
 B('ACTION',20,'Shuttle','The shuttle skims the outer ring, sheds a wing, slides into a threshing field','', 'VFX_CIN_CRASH_SPARKS'),
 B('POV',10,P,'Cockpit glass cracked; alarms; Ostra counting down systems'),
 B('PLAYER',10,P,'Player climbs out into low gravity'),
 B('VISTA',24,'The Quiet','The inside of the ring: fields of glass, land hanging in the sky'),
 B('VO',12,P,'"It\'s bigger inside. It always was."','Ostra'),
 B('TRANS',8,P,'Back to play, low-gravity movement on'),
])
cin('CIN_HUSH_SPEAKS','Hush','MQ_A3_02','REG_Q','CUT','A','Activate the Maker terminal','Player, Hush (voice via Hollowed), Ostra (voice)',
 'Maker terminal','', '',[
 B('EST',8,'Maker terminal','Hollowed kneel around the terminal'),
 B('REVEAL',12,'Hollowed','Every Hollowed looks up at once'),
 B('DLG',16,'Hush','Hush speaks through all their mouths, calm, "we"','Hush'),
 B('VO',10,P,'Ostra answers','Ostra'),
 B('DLG',14,'Hush','"The one who spoiled the crop."','Hush'),
 B('DLG',12,'Hush','Plainly (story pass D): "We did not wake you. We let her wake you. You were always coming here."','Hush'),
 B('INSERT',4,'Chest Shard','The ignition shard in the player\'s chest, seen for what it is'),
 B('REACT',6,P,'Player'),
 B('TRANS',9,P,'The Hollowed stand and attack; back to play'),
])
cin('CIN_GRANARY_REVEAL','The Granary','MQ_A3_03','REG_Q','CUT','A','Enter the Granary','Player, Ostra (voice)',
 'The Granary','', 'Spared regions show whole; taken regions show broken',[
 B('EST',14,'Granary','Stolen land from every region hangs in glass in a vast dark hall','', 'VFX_CIN_GLASS_LAND'),
 B('VISTA',16,'Granary','Camera travels past each region\'s land: spared ones intact and lit'),
 B('INSERT',6,'Glass','An Emberwatch roof inside the glass'),
 B('VO',14,P,'Ostra realises what the harvest is for','Ostra'),
 B('INSERT',6,'Maker record','A Maker record wakes: the Weave was planted as a field (story pass E)','', 'VFX_CIN_HOLO_FLICKER'),
 B('VISTA',12,'Maker record','The record shows a harvester arriving every 3,000 years'),
 B('VO',8,P,'Ostra: magic on Veyl only exists because the world is a crop','Ostra'),
 B('TRANS',10,P,'Back to play'),
])
cin('CIN_IRES_FINAL','The Captain, Unmasked','MQ_A3_03','REG_Q','CUT','A','Reach Ires at the Granary\'s end','Player, Captain Edda Ires',
 'Granary ship-side','', 'Fight (boss rematch), recruit (IRES_RECRUITABLE), or let her reach Hush',[
 B('REVEAL',10,'Captain Edda Ires','Ires waits in her old captain\'s coat'),
 B('DLG',16,'Captain Edda Ires','Her final offer, per state','Captain Edda Ires'),
 B('CHOICE',8,P,'Choice per IRES state'),
 B('ACTION',8,'Captain Edda Ires','Per choice: draws, kneels, or turns away'),
 B('TRANS',3,P,'Back to play or boss camera'),
])
cin('CIN_CHOIR_COPIES','The Choir of Copies','MQ_A3_04','REG_Q','IGC','B','Enter the copy hall','Player, Choirborn copies',
 'Copy hall','', 'Copies drawn from the player\'s flags: betrayed leaders, dead or departed companions, Taken Shard-bearers; 3 to 5 lines each',[
 B('EST',8,'Copy hall','Rows of Choirborn wearing familiar faces'),
 B('REVEAL',10,'Copy','A copy of a companion steps forward and smiles wrong'),
 B('DLG',8,'Copy','"We kept them. We keep everyone."','Hush'),
 B('TRANS',4,P,'Back to play'),
])
cin('CIN_HUSH_DESCENT','The Hush Core','MQ_A3_05','REG_Q','CUT','A','Step into the core','Player, Ostra (voice), Hush',
 'Hush\'s mind','', 'Ostra strength by Hearts taken (Shard glow intensity)',[
 B('POV',12,P,'Fall through layers of memory: Veyl, the Meridian, other worlds harvested','', 'VFX_CIN_MIND_FALL'),
 B('MEM',14,'Other worlds','Glimpses of earlier harvests; other ships that said yes'),
 B('PLAYER',8,P,'Player lands on a floor of glass'),
 B('REVEAL',16,'Hush','Hush takes form: a lens of many faces'),
 B('TRANS',4,P,'Blend to boss camera'),
])
cin('CIN_HUSH_PHASE2','Hush: Choir','MQ_A3_05','REG_Q','IGC','B','Hush phase 2','Player, Hush','Hush\'s mind','', '',[
 B('REVEAL',8,'Hush','Hush splits into a choir of copies'),
 B('TRANS',2,P,'Back to boss camera'),
])
cin('CIN_HUSH_PHASE3','Hush: Seed','MQ_A3_05','REG_Q','IGC','B','Hush phase 3','Player, Hush, Ostra (voice)','Hush\'s mind','', 'Scales by Hearts taken',[
 B('REVEAL',8,'Hush','Hush collapses to a single seed of light'),
 B('VO',4,P,'Ostra: "Now. Give me everything."','Ostra'),
 B('TRANS',2,P,'Back to boss camera'),
])
cin('CIN_HUSH_FALL','Hush Broken','MQ_A3_05','REG_Q','CUT','A','Hush defeated','Player, Hush, Ostra (voice)','Hush\'s mind','', '',[
 B('ACTION',8,'Hush','The lens cracks across every face'),
 B('DLG',14,'Hush','Hush, small for the first time: "We only wanted to be full."','Hush'),
 B('VO',10,P,'Ostra answers','Ostra'),
 B('VISTA',8,'Core','The mind goes still'),
 B('TRANS',5,P,'Into the Choice'),
])
cin('CIN_CHOICE','The Choice','MQ_A3_06','REG_Q','CUT','A','After CIN_HUSH_FALL','Player, Ostra (voice)','The core','', 'Restore needs 4+ taken; Bind needs 3+ spared or Ostra approval route; Take always',[
 B('PLAYER',10,P,'Player before three paths of light'),
 B('VO',20,P,'Ostra lays out the three choices, honestly','Ostra'),
 B('INSERT',6,'Chest Shard','The Shard waits'),
 B('CHOICE',20,P,'Choice: Restore, Bind or Take (unavailable options shown dim with the reason)'),
])
ENDS = [('R','Restore the Meridian','MQ_END_R','MUS_CIN_ENDING_MERIDIAN',[
  B('ACTION',24,'The Quiet','The Quiet\'s core rebuilt as the Meridian\'s; the ring sheds its harvest','', 'VFX_CIN_CORE_OVERLOAD'),
  B('VISTA',24,'Veyl','The Quiet descends; the stolen land is lowered home'),
  B('EST',16,'Lantern Hold','The ship docks with the Hold; old and new hulls meet'),
  B('CROWD',20,'Lantern Hold','People of every faction on the walls'),
  B('PLAYER',12,P,'Player steps out onto the bridge of a living ship'),
  B('VO',16,P,'Ostra, whole, and formal now: "Captain on the bridge." A ship, not a friend (story pass F)','Ostra'),
  B('MEM',16,'Weave','Rites flicker in a child\'s hand and fail: magic fading over a generation'),
  B('VISTA',20,'Sky','The Meridian lifts from Veyl for the first time in 900 years'),
  B('TITLE',6,'Card','Epilogue slides follow (endings.csv)'),
 ]),('B','Bind the Shards','MQ_END_B','MUS_CIN_ENDING_WEAVE',[
  B('PLAYER',12,P,'Player kneels as the Granary glass cracks'),
  B('VISTA',24,'Granary','Each region\'s land falls home in a rain of light','', 'VFX_CIN_SHARD_COLUMN'),
  B('ACTION',24,'The Quiet','The ring burns as it breaks'),
  B('VO',20,P,'Ostra and the player, together at the end','Ostra'),
  B('POV',14,P,'Light fills the frame'),
  B('VISTA',24,'Veyl','Morning over Veyl; green in Cinderreach'),
  B('CROWD',16,'Lantern Hold','People watch the falling star burn out'),
  B('INSERT',8,'Anchor','An Anchor lights by itself: a Weave echo of the player'),
 B('VISTA',8,'Sky','Sting: 3,000 years later, a new light appears in the sky (story pass F)'),
  B('TITLE',6,'Card','Epilogue slides follow (endings.csv)'),
 ]),('T','Take the Quiet','MQ_END_T','MUS_CIN_ENDING_QUIET',[
  B('PLAYER',12,P,'Player walks into Hush\'s seat'),
  B('POV',16,P,'The player becomes the lens: sees all of Veyl at once','', 'VFX_CIN_LENS_ZOOM'),
  B('VO',16,P,'Ostra, merging: "We." The first time she says it','Ostra'),
  B('ACTION',20,'The Quiet','The harvest stops; Shard columns fall back'),
  B('VISTA',24,'Lantern Hold','The Quiet\'s lens turns on the Hold Council'),
  B('CROWD',16,'Council chamber','The Council looks up as the light falls on them'),
  B('VO',10,P,'Hush\'s voice and the player\'s slowly become one voice (mixed in audio)','Hush'),
 B('VISTA',20,'Sky','A god in the sky over Veyl'),
  B('TITLE',6,'Card','Epilogue slides follow (endings.csv)'),
 ])]
for e, name, q, mus, beats in ENDS:
    cin(f'CIN_END_{e}', name, q, 'REG_Q', 'CUT', 'A', 'Ending quest complete', 'Player, Ostra (voice), crowd', 'The Quiet and Veyl', mus,
        'Spared and taken regions shown per flags', beats, cond=f'FLG_END_{ {"R":"RESTORE","B":"BIND","T":"TAKE"}[e] }')
cin('CIN_END_T_POST','The Last Contract','MQ_END_T','REG_HUB','CUT','B','After credits, Take ending','Vey or a Quiet Hand initiate',
 'Lantern Hold','', 'Vey if recruited, else an unnamed initiate',[
 B('EST',8,'Quiet Hand shrine','Candles in the dark'),
 B('INSERT',10,'Contract','A contract is sealed; the name on it is the player\'s'),
 B('REVEAL',16,'Vey','Vey lifts her hood and looks up at the sky'),
 B('VO',6,P,'Final line from above: the player is glad someone took the contract','Player (as the Quiet)'),
 B('TITLE',6,'Card','Black'),
], cond='FLG_END_TAKE')
cin('CIN_CREDITS','Credits','MQ_END_*','REG_HUB','CARD','C','After the ending cinematic and epilogue','None','Lantern Hold flyover','MUS_THEME_MAIN','Ending tint per ending',[
 B('VISTA',600,'Veyl','Slow flyover of all six regions in their end state; credits roll on the right third'),
])
# Endgame
for sid, name in [('QUIETCORE','The Quiet Core'),('ARCHIVIST','Archivist Prime'),('MERIDIANGHOST','Meridian\'s Ghost')]:
    cin(f'CIN_BOSS_{sid}', name, 'RAID', 'REG_Q', 'IGC', 'B', 'Raid encounter start', '6 players, boss', 'Raid arena', '', 'Shows all 6 fireteam members',[
     B('EST',6,'Raid arena','Arena wide with the fireteam small in frame'),
     B('REVEAL',10,name,'Raid boss reveal'),
     B('TRANS',4,P,'Blend to gameplay camera'),
    ])

# ---------------------------------------------------------------- systemic cameras
SYS = [
 ('CAM_SYS_BOSS_REVEAL','Field, Site and Strike bosses','Any boss without an authored intro',4.0,'Orbit 40 deg from player shoulder to boss face, 35mm then 50mm','Skipped after first kill; never in PvP'),
 ('CAM_SYS_ANCHOR_REST','Rest at an Anchor','Interact with a lit Anchor',2.5,'Pull back to MS 35mm, low, campfire key light','Menu opens at end of move'),
 ('CAM_SYS_ANCHOR_LIGHT','Light a new Anchor','First touch of an Anchor',3.0,'Push in to MCU 50mm on hand, then WS 24mm as Ember rings climb','Unskippable 1.0 s, then skippable'),
 ('CAM_SYS_HEART_CHOICE','Heart Shard choice','After each lucid moment',0.0,'Held MCU 50mm slow orbit 10 deg until input','UI right third'),
 ('CAM_SYS_CRITICAL','Riposte and backstab','Critical hit lands',1.2,'Shift 15 deg and in 0.5 m, 0.85x time scale for 18 frames','Off in co-op if another player is within 5 m; off when Reduce Camera Motion is on'),
 ('CAM_SYS_POSTURE_BREAK','Posture break finisher','Finisher on a broken enemy',1.5,'Low 24mm angle, 6 frame hit stop','Same accessibility rule as critical'),
 ('CAM_SYS_LEGENDARY_DROP','Legendary or Shardborn pickup','Pick up Legendary or Shardborn item',2.0,'Item insert 85mm, item spins once','Optional; setting Item Reveal Camera'),
 ('CAM_SYS_LEVEL_UP','Level up at Anchor','Spend Ember to level',1.0,'Ember VFX climb, camera static','Inside rest menu'),
 ('CAM_SYS_DEATH','Death','Player health 0',3.0,'Slow pull up and away 4 m over 3 s, desaturate','Shard-ghost VFX marks the drop'),
 ('CAM_SYS_RESPAWN','Respawn at Anchor','After death',1.5,'Start low behind Anchor, rise to gameplay cam',''),
 ('CAM_SYS_FAST_TRAVEL','Fast travel','Travel from Anchor',2.0,'Camera rises 30 m into Ember, cut to load, descend at target',''),
 ('CAM_SYS_MOUNT','Summon Strider','Strider called',1.5,'Blend to mount camera 0.6 s',''),
 ('CAM_SYS_DOOR','Locked door or elevator','Big door, lift, fog gate',2.0,'Holds gameplay camera; streaming hidden behind door','Matches Souls-style load hiding'),
 ('CAM_SYS_CONVO','Conversation camera','Any dialogue with an NPC',0.0,'Shot/reverse: OTS 50mm on speaker, CU 85mm reactions, 2S 40mm every 4th line; auto-cut on speaker change','Rules in camera_language.csv; owned scenes in design/writing'),
 ('CAM_SYS_VENDOR','Vendor and crafting','Open vendor or bench',0.6,'Blend to MS 40mm framing NPC on left third, UI right',''),
 ('CAM_SYS_CHAR_CREATE','Character creator','After CIN_OPEN and from mirror',0.0,'Cryo scanner rig: 3 presets (full body 50mm, torso 70mm, face 100mm), orbit 360','Scan-grid VFX'),
 ('CAM_SYS_ARENA_INTRO','Arena match intro','3v3 match start (6 players)',8.0,'Fly-through of the map 18mm, then each team of 3 in a 3-shot line-up 35mm','Skippable by vote'),
 ('CAM_SYS_ARENA_OUTRO','Arena match end','Match end',6.0,'Winning team MVP pose, 35mm orbit',''),
 ('CAM_SYS_STRIKE_INTRO','Strike launch','3-player strike start',6.0,'Ship drop-in: fireteam lands, 24mm low','Skippable'),
 ('CAM_SYS_PHOTO','Photo mode','Pause menu',0.0,'Free camera 20 m tether, lens 14 to 200mm, roll, aperture f1.4 to f22, focus distance','Disabled in PvP and during authored CUT scenes'),
]

# ---------------------------------------------------------------- expand shots
def rnd(x): return max(1.0, round(x * 2) / 2)
shots, totals = [], {}
for c in C:
    n, i = 0, 0
    sdir = 'L>R'
    for bi, (t, secs, subj, act, spk, vfx) in enumerate(c['beats'], 1):
        pat = LANG[t]
        if t == 'ACTION' and secs > 10:  # repeat the action pattern for long beats
            pat = pat * math.ceil(secs / 8)
        tot = sum(p[0] for p in pat)
        for j, (share, size, lens, height, move, note) in enumerate(pat):
            n += 10
            d = rnd(secs * share / tot)
            if t == 'DLG' and j == 2: who = 'Listener'
            else: who = subj
            if size in ('OTS', 'CU') and t == 'DLG': sdir = 'R>L' if sdir == 'L>R' else 'L>R'
            line = f"DLG_{c['cin_id'][4:]}_{bi:02d}" if spk and t in ('DLG', 'VO') and j == 0 else ''
            shots.append(dict(shot_id=f"{c['cin_id']}_S{n:03d}", cin_id=c['cin_id'], beat=bi, beat_type=t,
                              duration_s=d, frames_60=int(d * 60), shot_size=size, lens_mm=lens or '', camera_height=height,
                              camera_move=move, subject=who, action=act if j == 0 else f'(cont.) {act}', speaker=spk if j == 0 else '',
                              line_ref=line, screen_direction=sdir if t in ('DLG', 'ACTION', 'OTS') else '',
                              aspect='2.39:1 matte' if t == 'MEM' else '16:9', vfx=vfx if j == 0 else '',
                              sfx_hook=f"SFX_CIN_{c['cin_id'][4:]}_{bi:02d}" if j == 0 else '',
                              board_note=note))
    totals[c['cin_id']] = sum(s['duration_s'] for s in shots if s['cin_id'] == c['cin_id'] and s['beat_type'] != 'PLAY')  # playable time is not footage

# ---------------------------------------------------------------- previs and production
TIER = {'A': dict(previs=1.0, mocap=True, face='Performance capture (MetaHuman Animator)', review=3),
        'B': dict(previs=0.6, mocap=True, face='Audio-driven lip-sync, hand polish on close-ups', review=2),
        'C': dict(previs=0.3, mocap=False, face='Audio-driven lip-sync', review=1)}
rows = []
for c in C:
    s = totals[c['cin_id']]; m = s / 60; tr = TIER[c['tier']]
    nshots = sum(1 for x in shots if x['cin_id'] == c['cin_id'])
    speakers = sorted({b[4] for b in c['beats'] if b[4] and b[4] not in ('Ostra', 'Hush')})
    vfx = sorted({b[5] for b in c['beats'] if b[5]})
    rows.append(dict(cin_id=c['cin_id'], tier=c['tier'], runtime_s=s, shots=nshots,
        storyboard_panels=nshots * (2 if c['tier'] == 'A' else 1),
        previs_method={'A': 'VCam previs in UE with proxy sets and mocap library', 'B': 'Sequencer blocking with library anims plus VCam pass', 'C': 'Layout in Sequencer only'}[c['tier']],
        previs_days=round(max(1, m * 4 * tr['previs']), 1),
        mocap_minutes=round(m * 1.3, 1) if tr['mocap'] else 0, performers=len(speakers) + (1 if 'Player' in c['cast'] else 0),
        facial=tr['face'], stunt='Yes' if any(b[0] == 'ACTION' for b in c['beats']) and c['tier'] == 'A' else 'No',
        hero_vfx=' '.join(vfx), custom_set='Yes' if c['region'] in ('REG_U',) or 'years ago' in c['location'] else 'No (gameplay level)',
        layout_days=round(max(.5, m * 3), 1), anim_days=round(max(.5, m * (10 if c['tier'] == 'A' else 5 if c['tier'] == 'B' else 2)), 1),
        light_days=round(max(.5, m * 2), 1), vfx_days=round(len(vfx) * 3 * max(.5, m / 2), 1), audio_days=round(max(.5, m * 2), 1),
        review_rounds=tr['review']))
for r in rows:
    r['total_person_days'] = round(sum(r[k] for k in ('previs_days', 'layout_days', 'anim_days', 'light_days', 'vfx_days', 'audio_days')), 1)

def w(name, data, cols=None):
    cols = cols or list(data[0].keys())
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); wr.writeheader(); wr.writerows(data)

for c in C:
    c['runtime_s'] = totals[c['cin_id']]; c['skippable'] = 'Hold 1 s; first viewing too'
    c['letterbox'] = 'Memory shots only' if any(b[0] == 'MEM' for b in c['beats']) else 'None'
    c['coop'] = 'Host-triggered; all players see it; skip when all hold or host holds 3 s' if c['kind'] != 'CARD' else 'Each player'
w('cinematics.csv', C, ['cin_id', 'title', 'quest_id', 'region', 'kind', 'tier', 'trigger', 'condition', 'runtime_s', 'cast', 'location',
                        'music_cue', 'variants', 'letterbox', 'skippable', 'coop'])
w('shots.csv', shots)
w('previs.csv', rows)
w('systemic_cameras.csv', [dict(cam_id=a, name=b, trigger=c, duration_s=d, camera=e, rules=f) for a, b, c, d, e, f in SYS])

# camera language rules table
LR = [
 ('LENS_KIT','Lens kit','Prime set 18, 24, 35, 50, 85, 100 mm on Super 35 filmback (24.89 x 18.67 mm). No zooms in cutscenes; photo mode only'),
 ('LENS_WIDE','Wide lenses','18-24 mm for place and scale: establishing, vistas, Shard-bearer reveals from low angle'),
 ('LENS_MID','Normal lenses','35-50 mm for action and player hero shots, so armor reads at true proportion'),
 ('LENS_TIGHT','Long lenses','85-100 mm for faces, inserts, and every Ostra line'),
 ('APERTURE','Aperture','f2.8 default; f1.8 for close-ups and memories; f5.6 on vistas'),
 ('HEIGHT','Camera height','Eye height by default. Low (0.6 m) for Shard-bearers and Hush. High only for establishing shots. Never look down on the player except at death'),
 ('MOVE','Camera movement','Dolly, crane and slow push for the present day. Handheld only in combat and memories. No drone-style orbits on dialogue'),
 ('AXIS','180-degree rule','Hold the axis in every dialogue. Cross only on a cut-away insert or a visible camera move'),
 ('DIR','Screen direction','Player travels screen left to right toward the Quiet across the campaign; enemies and Hush enter right to left'),
 ('OSTRA','Ostra has no body','Never cut to an empty space for Ostra. Hold on the player, or cut to the chest Shard insert. Shard pulses with her syllables'),
 ('HUSH','Hush has no single face','Hush speaks through many mouths: cut across several Hollowed on one line, never a single CU'),
 ('MEMORY','Memory grammar','Memories use a 2.39:1 matte, cold grade, frame-flicker and focus breathing so they never read as the present'),
 ('PLAYER','Player in shot','In-engine with the player\'s own armor and body (plan 5.7). Helmets show by default; setting Hide Helmet in Cinematics. Every cutscene has at least one PLAYER shot'),
 ('SILENT','Silent protagonist rule','The player has two voice sets but never speaks in cutscenes (one exception: the last line of CIN_END_T_POST); choices happen in CHOICE beats'),
 ('CUT','Cutting','Average shot 4 s in dialogue, 2 s in action, 8 s+ on vistas. Cut on action or eyeline. Hold reactions 12 frames past the line'),
 ('TRANS','Gameplay blend','Every cutscene ends on a frame that matches the gameplay camera, then blends in 1.0 s. No fade to black unless the scene ends an act'),
 ('SAFE','Safe areas','Title safe 90%, action safe 93%. Subtitles in lower 15%; choice UI on right third'),
 ('SUBS','Subtitles','Speaker name in faction colour, max 2 lines, 42 chars per line, min 1.2 s on screen'),
 ('SKIP','Skipping','Every cutscene skippable after 1 s with a hold-to-skip prompt; Pause works. Choice beats cannot be skipped, only answered'),
 ('COOP','Co-op','Host triggers. Guests see the host\'s choices; their own armor shows where a PLAYER shot frames the party (up to 4). Skip when all hold or the host holds 3 s'),
 ('FPS','Frame rate','Cutscenes run at game frame rate (60 performance, 30 quality); camera cuts reset motion blur and TAA history'),
 ('ACCESS','Accessibility','Reduce Camera Motion setting removes handheld noise, shake and slow-mo; Flash Reduction caps flashes at 3 per second'),
 ('CONVO','Conversation camera','Systemic: OTS 50mm on speaker, CU 85mm reaction, 2S 40mm every 4th line, shots chosen by line length, eyelines solved per NPC height'),
]
w('camera_language.csv', [dict(rule_id=a, rule=b, detail=c) for a, b, c in LR])

cut = [c for c in C if c['kind'] == 'CUT']
authored = sum(c['runtime_s'] for c in cut)
mem = sum(c['runtime_s'] for c in cut if c['cin_id'].startswith('CIN_MEM'))
endings = [c['runtime_s'] for c in cut if c['cin_id'].startswith('CIN_END_') and c['cin_id'] != 'CIN_END_T_POST']
one_run = authored - mem - sum(endings) + max(endings) + mem / 2  # typical: 3 of 6 Hearts taken
print(f'{len(C)} cinematics, {len(shots)} shots; CUT authored {authored/60:.1f} min; one playthrough about {one_run/60:.1f} min')
with open(os.path.join(OUT, 'summary.txt'), 'w') as f:
    f.write(f'{len(C)} cinematics ({len(cut)} CUT, {sum(1 for c in C if c["kind"]=="IGC")} IGC), {len(shots)} shots, {len(SYS)} systemic cameras.\n'
            f'Authored CUT runtime {authored/60:.1f} min; a typical playthrough (one ending, 3 memories) sees {one_run/60:.1f} min (plan 5.7: about 45).\n'
            f'Production estimate {sum(r["total_person_days"] for r in rows):.0f} person-days, {sum(r["mocap_minutes"] for r in rows):.0f} min of capture.\n')
