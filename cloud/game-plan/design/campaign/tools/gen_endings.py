#!/usr/bin/env python3
"""Writes endings.csv (epilogue slides) and vo_budget.csv (whole-campaign voice plan). Run after gen_campaign.py."""
import csv, os, collections
C = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def w(n, h, rows):
    with open(os.path.join(C, n), 'w', newline='', encoding='utf-8') as f: cw = csv.writer(f); cw.writerow(h); cw.writerows(rows)

END = {'R': 'Restore', 'B': 'Bind', 'T': 'Take'}
REG = {  # region: (heart flag n, place, people, healed image, hollowed image)
 'REG_01': (1, 'Cinderreach', 'the kiln families', 'grass came back through the ash', 'the ash never settled'),
 'REG_02': (2, 'Saltmere', 'the Stiltmarket crews', 'the sea ran clear to the horizon', 'the tides turned to glass at low water'),
 'REG_03': (3, 'Thornwood', 'the Thorn Clans', 'the Bloom Heart flowered for the first time in a century', 'the great trees greyed from the crown down'),
 'REG_04': (4, 'Glasswaste', 'the Mirage caravans', 'rain fell on the glass and stayed', 'the glass spread a mile every year'),
 'REG_05': (5, 'Rimefall', 'the people of Rimehold', 'the passes thawed each spring', 'the cold kept its grip on the passes'),
 'REG_06': (6, 'Hollowdeep', 'Bea Crane\'s lamp crew', 'the lamps in Last Light were finally left unlit', 'the lamps in Last Light burned day and night')}
ENDTXT = {'R': 'when the Meridian flew again, {p} were among the first to crew her', 'B': 'with the Weave whole again, {p} sang the old songs with new words',
          'T': 'under the Quiet\'s eye, {p} learned to work by its light and keep their voices low'}
rows = []
for reg, (n, place, people, healed, hollow) in REG.items():
    for e in END:
        for st in ('SPARED', 'TAKEN'):
            img = healed if st == 'SPARED' else hollow
            txt = f'In {place}, {img}, and ' + ENDTXT[e].format(p=people) + '.'
            rows.append([f'EPI_{reg}_{e}_{st}', END[e], 'Region', reg, f'FLG_END_{END[e].upper()} + FLG_HEART_{n}_{st}', txt, 18])
FAC = {'FAC_HULLKNIGHTS': ('Iselde Marr', {'R': 'turned the Hull Knights into the Meridian\'s first navy', 'B': 'broke her sword over the captain\'s chair and sent the Knights home to their farms', 'T': 'kept the Hold\'s gates and never once looked up'}),
       'FAC_LANTERNCHURCH': ('Oswin Hale', {'R': 'added forty minutes to the Log and read them aloud every year', 'B': 'wrote the Kindled into the Log as the last entry', 'T': 'closed the Bridge Chapel and taught children to read from it in secret'}),
       'FAC_SALVAGERS': ('Petra Quell', {'R': 'flew her stitched ship beside the Meridian and charged the crew for fuel', 'B': 'left Veyl alone in her ship, a small light going out past the moons', 'T': 'sold the Quiet\'s shadows by the yard and got very rich'}),
       'FAC_QUIETHAND': ('The Speaker', {'R': 'put down the mask, and nobody heard the old voice again', 'B': 'lit one black candle for the Kindled and closed the Whisper Gallery', 'T': 'sent one last contract upward, addressed to the sky'}),
       'FAC_CHOIR': ('the Choir', {'R': 'lost its songs as the Weave thinned and became a school of engineers', 'B': 'heard the Shards sing in their own voice for the first time', 'T': 'became the Quiet\'s priesthood and forgot why that should frighten them'})}
for fac, (who, d) in FAC.items():
    for e in END:
        rows.append([f'EPI_{fac}_{e}', END[e], 'Faction', fac, f'FLG_END_{END[e].upper()} + joined {fac}', f'{who[0].upper() + who[1:]} {d[e]}.', 16])
CMP = {'ACT_CMP_C1': 'Kessa Vane', 'ACT_CMP_C2': 'Brother Odo', 'ACT_CMP_C3': 'Tamsin Rook', 'ACT_CMP_C4': 'Vey', 'ACT_CMP_C5': 'Hal Merrow',
       'ACT_CMP_C6': 'Sister Calla', 'ACT_CMP_C7': 'Dren', 'ACT_CMP_C8': 'Unit 9'}
CSTATE = {'LOYAL': ('approval 75+', '{n} stayed at the Kindled\'s side to the end and told the story right, every time.'),
          'NEUTRAL': ('approval -49 to 74', '{n} went their own way after it was over, and did well enough.'),
          'GONE': ('left the party', '{n} was gone long before the end. Nobody in Lantern Hold knew where.')}
for c, n in CMP.items():
    for st, (cond, t) in CSTATE.items():
        rows.append([f'EPI_{c}_{st}', 'Any', 'Companion', c, cond, t.format(n=n), 14])
for fl, t in [('FLG_IRES_DEAD', 'Captain Edda Ires was buried beside the Navigation Table, under the chair she had sat in nine hundred years before.'),
              ('FLG_IRES_ALLY', 'Captain Ires took the helm one last time, and kept a different word.'),
              ('FLG_IRES_TO_HUSH', 'Captain Ires kept her deal. Nobody was left to hold her to it.')]:
    rows.append([f'EPI_IRES_{fl[9:]}', 'Any', 'Ires', 'ACT_NPC_IRES', fl, t, 12])
for e, t in [('R', 'Ostra took the Meridian\'s helm. She ran the ship perfectly, and she never again asked the Kindled how they were.'),
             ('B', 'Ostra went down with the Kindled. Her last log entry was one word: Forgiven.'),
             ('T', 'Ostra and Hush became one quiet voice. Some nights the Choir swears it hears her arguing.')]:
    rows.append([f'EPI_OSTRA_{e}', END[e], 'Ostra', 'ACT_NPC_OSTRA', f'FLG_END_{END[e].upper()}', t, 10])
for e, t in [('R', 'The Weave thinned. Within a generation the last Rite failed, the Choir fell silent, and children asked what a Kindled was.'), ('B', 'Three thousand years later, a new light appeared in the sky over Veyl, and it was not a star.'), ('T', 'The Quiet Hand\'s last contract reached the sky. The thing that had been the Kindled read it and was glad.')]:
    rows.append([f'EPI_COST_{e}', END[e], 'Cost', 'ENDING', f'FLG_END_{END[e].upper()}', t, 12])
for e, t in [('R', 'Lantern Hold became a port.'), ('B', 'Lantern Hold became a city like any other, and that was the point.'), ('T', 'Lantern Hold kept its lamps lit and its windows shuttered.')]:
    rows.append([f'EPI_HUB_{e}', END[e], 'Lantern Hold', 'REG_HUB', f'FLG_END_{END[e].upper()}', t, 8])
w('endings.csv', ['slide_id', 'ending', 'kind', 'subject', 'condition', 'text_en', 'narration_seconds'], rows)

# Whole-campaign VO plan. Quest scenes come from vo_budget_from_quests.csv; barks and systemic lines are Shardfall choices.
q = {}
p = os.path.join(C, 'vo_budget_from_quests.csv')
if os.path.exists(p):
    with open(p) as f: q = {r[0]: int(r[1]) for r in list(csv.reader(f))[1:]}
SYS = [  # speaker, systemic lines beyond quest scenes (Shardfall choices sized to the plan's 60,000-line target, 5.5)
 ('PLAYER', 'Second voice set (B) re-records every PLAYER quest line', q.get('PLAYER', 0)),
 ('PLAYER', 'Combat and reaction barks, voice sets A and B (1,500 each)', 3000),
 ('ACT_NPC_OSTRA', 'Lore item comments 400, region/boss/site comments 1,400, hints and map 900, contradiction and confront set 300, NG+ 300, lucid-count reactions 120', 3420),
 ('ACT_CMP_C1..C8', 'Quest reactions: 4 lines x 234 quests x 8 companions', 4 * 234 * 8),
 ('ACT_CMP_C1..C8', 'Location barks 40 x 9 regions, combat 120, banter 60, per companion', 540 * 8),
 ('ACT_CMP_C1..C8', 'Companion-to-companion banter: 28 pairs x 30 lines', 840),
 ('Faction leaders x5', 'Hub reactions to main-quest milestones and choices: 40 beats x 5', 200),
 ('ACT_BOSS_HUSH', 'Relay Tower answers, boss-phase lines, Hollowed whispers by region', 600),
 ('Enemy factions', '4 factions x 6 roles x 40 barks x 3 voices', 2880),
 ('Bosses', '45 bosses (44 plus Hush) x 25 lines', 1125),
 ('Town ambient', '13 towns + hub x 30 NPCs x 12 lines', 14 * 30 * 12),
 ('Vendors', '17 vendors x 40', 680),
 ('Radiant givers and targets', '12 templates x 25 instances x 12 lines', 3600),
 ('Epilogue narration', 'endings.csv slides', len(rows)),
 ('Lore item readings', 'ITM_LOR_001..400 read aloud', 400),
 ('Branch outcomes', 'Each quest branch (quest_branches.csv) gets its own outcome dialogue, about 14 lines', 14 * max(0, sum(1 for _ in open(os.path.join(C, 'quest_branches.csv'))) - 1)),
 ('Shard-bearer lucid moments and graves', '6 x (Take + Spare variants) x 20', 240)]
out = [[k, 'quest scenes', v] for k, v in sorted(q.items(), key=lambda x: -x[1])] + [[s, n, v] for s, n, v in SYS]
tot = sum(r[2] for r in out)
out.append(['TOTAL', 'English lines; plan target 60,000', tot])
w('vo_budget.csv', ['speaker', 'source', 'lines'], out)
print(f'endings slides {len(rows)} | vo total {tot}')
