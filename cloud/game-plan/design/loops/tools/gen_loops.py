"""Generates the numeric loop tables in design/loops/ from data/. Run: python3 tools/gen_loops.py (from design/loops/).
Reads data/ read-only. New design values are marked in the tables' notes as Shardfall loop choices."""
import csv, os, math
D = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
OUT = os.path.join(os.path.dirname(__file__), '..')
def rd(p): return list(csv.DictReader(open(os.path.join(D, p), encoding='utf-8')))
def wr(name, rows):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
def kindle(L): return math.floor(0.02*L**3 + 3*L**2 + 100*L + 500)          # ECOF_LEVEL
def drop(L): return 10 + 1.5*L**1.5                                         # FRM_EMBER_DROP base
DR_KILL, DR_SITE = 0.16, 0.1   # DR-001 and DR-002, then B08 SIM-01
def boss_ember(cls, L, req=False):
    if req and cls == 'Site': return DR_SITE*kindle(L)
    return {'Site':0.1,'Field':0.4,'Citadel':0.6,'Shard-bearer':1.0,'Raid':0.5}[cls]*kindle(L)  # ECOF_BOSS

bands = {r['Region ID']: (int(r['Min level']), int(r['Max level']), r['Region']) for r in rd('actors/region_bands.csv')}
bands['REG_END'] = (75, 100, 'Endgame')
mid = {k: (a+b)//2 for k, (a, b, _) in bands.items()}
inflow = {k: 1.9*kindle(m) for k, m in mid.items()}                        # ECOF_INFLOW (all sources)
def sinks(reg):  # share of income per sink; kindling plus death loss is what moves the level
    if reg == 'REG_END': return {'kindle_levels':0.33,'smithing':0.30,'vendors':0.05,'resonance_tiers':0.25,'rites_bribes':0.02,'death_loss':0.05}
    if reg in ('REG_06','REG_Q'): return {'kindle_levels':0.45,'smithing':0.20,'vendors':0.08,'resonance_tiers':0.20,'rites_bribes':0.02,'death_loss':0.05}
    return {'kindle_levels':0.60,'smithing':0.20,'vendors':0.12,'resonance_tiers':0.00,'rites_bribes':0.03,'death_loss':0.05}
band_of = {'Cinderreach':'REG_01','Saltmere':'REG_02','Thornwood':'REG_03','Glasswaste':'REG_04','Rimefall':'REG_05','Hollowdeep':'REG_06','Endgame':'REG_END','The Quiet':'REG_Q'}

# 1. Level pacing -----------------------------------------------------------
rows, cum = [], 0.0
for r in rd('actors/level_curve.csv'):
    L = int(r['Level'])
    if L == 100: break
    reg = band_of[r['Matching region band']]
    if 68 <= L <= 74: reg = 'REG_Q'
    cost = int(r['Ember to kindle next']); h = cost/(inflow[reg]*(sinks(reg)['kindle_levels'] + sinks(reg)['death_loss']))
    cum += h
    rows.append({'level': L, 'region': reg, 'ember_to_next': cost, 'ember_per_hour_band': round(inflow[reg]),
                 'hours_this_level': round(h, 2), 'cumulative_hours': round(cum, 1),
                 'skill_xp_to_next': r['Skill-XP to next'], 'perk_points_total': r['Perk points total'],
                 'attribute_points_total': r['Attribute points total']})
wr('progression_pacing.csv', rows)

# 2. Encounter templates ----------------------------------------------------
ROLE = {'Fodder':(1.0,0.5),'Skirmisher':(1.5,0.8),'Artillery':(1.5,0.9),'Shield-bearer':(2.0,0.9),'Heavy':(4.0,2.0),'Leader':(4.0,2.5)}  # (threat points LOOP choice, Ember mult from enemies.csv)
T = [  # id, name, comp, target clear s, loot table suffix, notes
 ('ENC_PATROL','Patrol',{'Fodder':3,'Skirmisher':1},30,'none','Roams a 120 m loop; 1 per 250 m of road'),
 ('ENC_PICKET','Picket',{'Fodder':2,'Artillery':1,'Shield-bearer':1},45,'none','Guards a road choke or tower base'),
 ('ENC_AMBUSH','Ambush',{'Skirmisher':2,'Artillery':2,'Heavy':1},60,'none','Triggers inside a 25 m volume; telegraphed by Shard hum 2 s before'),
 ('ENC_CAMP','Camp',{'Fodder':4,'Skirmisher':2,'Artillery':1,'Shield-bearer':1,'Leader':1},120,'SMALLCHEST','Leader death applies FRM_MORALE -40; 1 small chest'),
 ('ENC_ELITE','Elite pack',{'Heavy':1,'Fodder':2},60,'faction HEAVY','Heavy drops its faction loot table'),
 ('ENC_HOLDOUT','Holdout (3 waves)',{'Fodder':8,'Skirmisher':3,'Artillery':2,'Shield-bearer':2,'Heavy':1},210,'SHARDCRATE','Waves of about 6 TP, next wave at 2 alive or 25 s'),
 ('ENC_SITE','Site (dungeon) trash',{'Fodder':14,'Skirmisher':6,'Artillery':4,'Shield-bearer':4,'Heavy':2,'Leader':1},600,'SHARDCRATE + site boss','6 rooms, 1 Anchor at the midpoint, then site boss'),
 ('ENC_CHOIRVAULT','Choir vault',{'Shield-bearer':3,'Skirmisher':3,'Heavy':2,'Leader':1},300,'VAULT','Choirborn or regional variants; 3 per region'),
]
rows = []
CONTAINER_REG = {'REG_U': 'REG_05', 'REG_END': 'REG_Q'}  # Undervault (level 50) and endgame reuse the band's container tables
for reg, (a, b, nm) in bands.items():
    if reg in ('REG_HUB',): continue
    L = mid[reg]
    for tid, name, comp, secs, lt, note in T:
        tp = sum(ROLE[k][0]*n for k, n in comp.items()); n = sum(comp.values())
        em = round(sum(ROLE[k][1]*n*drop(L) for k, n in comp.items()))
        rows.append({'enc_id': f'{tid}_{reg}', 'template': name, 'region': reg, 'level': L,
                     'composition': '; '.join(f'{n} {k}' for k, n in comp.items()), 'enemies': n, 'threat_points': tp,
                     'target_clear_s': secs, 'ember': em, 'ember_per_min': round(em/(secs/60)),
                     'loot': ('ITM_LT_'+lt+'_'+CONTAINER_REG.get(reg, reg)) if lt in ('SMALLCHEST','SHARDCRATE','VAULT') else lt,
                     'notes': note})
wr('encounter_templates.csv', rows)

# 3. 30-minute session budget per band -----------------------------------------
SEG = [  # minute start, minute end, activity, encounters
 (0,1,'Rest at Anchor, spend Ember, set Tonics',[]),
 (1,4,'Travel to waypoint (mount or on foot), 1 patrol on the way',['ENC_PATROL']),
 (4,8,'Point of interest 1: camp',['ENC_CAMP']),
 (8,10,'Gather nodes (3) and a lore site',[]),
 (10,13,'Picket at a tower; climb tower, map reveal',['ENC_PICKET']),
 (13,23,'Site (dungeon) with its boss',['ENC_SITE','BOSS_Site']),
 (23,25,'Ambush on the way back',['ENC_AMBUSH']),
 (25,28,'Elite pack or world event',['ENC_ELITE']),
 (28,30,'Return to Anchor, kindle a level or upgrade',[]),
]
by_id = {r['enc_id']: r for r in rows}
srows = []
for reg in ['REG_01','REG_02','REG_03','REG_04','REG_05','REG_06','REG_Q']:
    tot = tq = 0
    for s, e, act, encs in SEG:
        em = eq = 0
        for x in encs:
            if x == 'BOSS_Site': em += boss_ember('Site', mid[reg]); eq += boss_ember('Site', mid[reg], True)
            else: em += by_id[f'{x}_{reg}']['ember']; eq += by_id[f'{x}_{reg}']['ember']*DR_KILL
        tot += em; tq += eq
        srows.append({'region': reg, 'minute_from': s, 'minute_to': e, 'activity': act, 'ember_current_data': round(em), 'ember_with_DR001_DR002': round(eq), 'running_total_with_DRs': round(tq)})
    target = inflow[reg]/2
    srows.append({'region': reg, 'minute_from': 30, 'minute_to': 30, 'activity': f'TOTAL; ECOF_INFLOW/2 target {round(target)}, of which kills+bosses should be 65% = {round(0.65*target)}',
                  'ember_current_data': f'{round(tot)} ({round(100*tot/target)}% of target)', 'ember_with_DR001_DR002': f'{round(tq)} ({round(100*tq/target)}% of target)', 'running_total_with_DRs': ''})
wr('session_30min.csv', srows)

# 4. Economy flow per band (per hour) ---------------------------------------
erows = []
for reg in ['REG_01','REG_02','REG_03','REG_04','REG_05','REG_06','REG_Q','REG_END']:
    I = inflow[reg]
    src = {'kills':0.45,'bosses':0.20,'quests_and_pouches':0.15,'selling':0.12,'chests_and_crates':0.08}
    snk = sinks(reg)
    r = {'band': reg, 'level_mid': mid[reg], 'ember_in_per_hour': round(I)}
    r.update({f'src_{k}': round(I*v) for k, v in src.items()}); r.update({f'sink_{k}': round(I*v) for k, v in snk.items()})
    r['net'] = round(I - sum(I*v for v in snk.values()))
    erows.append(r)
wr('economy_flow.csv', erows)

# 5. Endgame activities (LOOP choices except where a data ID is cited) -----------------------
H = ['act_id','activity','players','level','length_min','unlock','reward_table','seals','repeat_rule','failure_state','data_ids']
EG = [
 ('EG_STRIKE','Strike (6 at launch, STK_01..06)','3 (matchmade or premade; solo allowed)','80 (COOP_LEVEL sync)','20-25','Campaign Act 3 start + level 75','ITM_LT_ENDGAME_STRIKE','10','Seals until weekly cap; featured Strike of the week x2 Seals on first 3 clears','Team wipe = restart from last checkpoint (3 per Strike); 3 wipes on one checkpoint = return to orbit, no reward','ITM_LT_ENDGAME_STRIKE; COOP_OW_1..3; ACT_BOSS field pairs at L80'),
 ('EG_CITADEL','Hollowed Citadel (6, one per region)','1-4','80 (CHL_HOLLOWCIT HP x2.0, dmg x1.6)','35-50','Region Citadel cleared + level 78','ITM_LT_ENDGAME_HOLLOWED_CITADEL','15 (see DR-004)','One featured Citadel per week with 2 modifiers from CHL_HOLLOWCIT; others give Seals x1','Death = Anchor respawn inside (2 Anchors per Citadel); no Tonics in phase 3 if that modifier rolls','CHL_HOLLOWCIT; COOP_BOSS_1..4; ACT_BOSS Citadel class'),
 ('EG_RAID','Raid: The Quiet (4 encounters)','6 (premade or Raid Finder, see matchmaking.csv)','80/84/88/92 per boss','150-240 full clear','Campaign complete + level 80','ITM_LT_BOSS_37..40','20-40 per boss','Shardborn and Seals once per boss per week (lockout); repeat kills give Ember and 1 gear roll','Wipe = encounter reset, 10 s; 8 wipes = no penalty, keep trying; raid lockout persists until weekly reset','COOP_RAID_6; ACT_BOSS_QUIETCORE ARCHIVIST MERIDIANGHOST UNMADECHOIR; BPH_*; BAI_*'),
 ('EG_ARENA','Arena PvP 3v3','6','Normalized: all at 80, upgrades capped +15 in Ranked','8 to 10 per match','Level 30 + QST tutorial match','ITM_LT_ENDGAME_ARENA_WIN / _LOSS','5 win / 2 loss','Seals until weekly cap; 25% gear roll each match','Leaving early = 15 min queue lock (ERR_ACTIVITY_LOCK); 3 leaves in 24 h = 2 h lock','ITM_PWR_01..06; UV-031'),
 ('EG_INVADE','Invasions (opt-in)','1 invader vs 1-4','Invader synced by COOP_LEVEL + upgrade within +3','3-8','Quiet Hand joined or CNF_INVASIONS_ON','RPA_INVADE','0','Max 1 invasion per host per 10 min','Invader death = no loss; host death = normal FRM_DEATH','FAC_QUIETHAND; RPA_INVADE; NTF_INVADED'),
 ('EG_NG','New Game+ cycles','1-4','Bands + NG scaling','60-90 h per cycle','Any ending','Region tables x DIF_NG Ember','0','Up to NG+7','As campaign','DIF_NG1..3'),
 ('EG_SHBQ','Shardborn quests (14)','1-4','Band of region','45-90 each','Per QST_SHB_* trigger','ITM_SHB_A07..A15, ITM_SHB_W11..W15','0','Once per character','Quest step fail = retry at last step','QST_SHB_A07..A15, QST_SHB_W11..W15'),
 ('EG_FACTION','Faction finales and radiant jobs','1-4','Any','15-30 per job','REP_SWORN for finale','RPA_QUEST_SIDE','0','Radiant rep cap 1200 per week','Job fail = no rep, retry next restock','FAC_*; REP_*; RPA_*'),
]
wr('endgame_activities.csv', [dict(zip(H, r)) for r in EG])

# 6. Matchmaking playlists ----------------------------------------------------------
H = ['mm_id','playlist','team','search_rule','widen_after','widen_rule','timeout_s','join_in_progress','backfill','host','errors']
MM = [
 ('MM_COOP_SIGN','Campaign co-op via summon sign','2-4','Same region; guest level within COOP_LEVEL sync; same or later main quest','60 s','Any region band the guest has entered','none (sign stays until host rests)','Yes','No','Host client; server-side loot validation','ERR_SESSION_FULL ERR_JOIN_FAIL ERR_VERSION_MISMATCH ERR_NAT'),
 ('MM_COOP_INVITE','Campaign co-op invite','2-4','Friend list; no level rule (COOP_LEVEL sync)','-','-','30 (invite expires)','Yes','No','Host client','ERR_JOIN_FAIL ERR_HOST_LEFT'),
 ('MM_STRIKE','Strike playlist','3','Level 75+, same region pref (ping < 80 ms)','45 s','Ping < 150 ms','300 then offer solo start (ERR_MM_TIMEOUT)','Yes until final boss','Yes, slot opens 10 s after a leave','Dedicated server','ERR_MM_TIMEOUT ERR_NET_LOST'),
 ('MM_CITADEL','Hollowed Citadel finder','2-4','Level 78+','60 s','Any level 75+','300 then solo','Yes until phase 3 of final boss','Yes','Host client','ERR_MM_TIMEOUT'),
 ('MM_RAIDFINDER','Raid Finder','6','Level 80+, same lockout state per boss, ping < 80 ms','120 s','Ping < 150 ms','900','Yes between encounters only','Yes between encounters','Dedicated server','ERR_MM_TIMEOUT ERR_ACTIVITY_LOCK'),
 ('MM_ARENA_QUICK','Arena Quickplay 3v3','3','Connection first; hidden skill rating +/-400','30 s','+/-800, then any','240','Yes in first 5 min','Yes','Dedicated server','ERR_MM_TIMEOUT ERR_KICKED'),
 ('MM_ARENA_RANKED','Arena Ranked 3v3','3','Skill rating +/-150; fireteam size matched 1v1,2v2,3v3','45 s','+/-300 then +/-500','420','No','No (3v2 continues; loss reduced 50%)','Dedicated server','ERR_MM_TIMEOUT ERR_ACTIVITY_LOCK'),
 ('MM_INVADE','Invasion search','1 vs host team','Host opted in; invader level synced; weapon upgrade within +3 (plan 3.7)','90 s','+5 upgrade','600','-','-','Host client','ERR_JOIN_FAIL'),
]
wr('matchmaking.csv', [dict(zip(H, r)) for r in MM])

# 7. Season calendar (13 weeks, quarterly per plan Phase 9) -----------------------------------
rows = []
for w in range(1, 14):
    feat = f'STK_{(w-1)%6+1:02d}' if w > 1 else 'STK_S1 (new seasonal Strike)'
    cit = ['REG_01','REG_02','REG_03','REG_04','REG_05','REG_06'][(w-1)%6]
    ev = 'Seasonal event (3 weeks)' if 5 <= w <= 7 else ('Iron Trial PvP weekend (Fri-Mon)' if w in (3, 10) else ('Double Seals weekend' if w == 12 else '-'))
    rows.append({'week': w, 'featured_strike': feat, 'featured_citadel': f'Hollowed Citadel {cit} + 2 modifiers', 'raid_challenge': ['QUIETCORE','ARCHIVIST','MERIDIANGHOST','UNMADECHOIR'][(w-1)%4],
                 'event': ev, 'arena_map_rotation': 'New seasonal map featured' if w <= 2 else f'Map pool slot {(w-1)%6+1}',
                 'season_track_ranks_target': min(50, round(w*50/11)), 'notes': 'Week 13: season wrap, track rewards claimable 2 more weeks' if w == 13 else ''})
wr('season_calendar.csv', rows)
print('ok', len(EG), 'endgame,', len(MM), 'playlists,', round(cum,1), 'h to level 100')
