from common import *
# ---------- Resonances ----------
R=[('RES_EMBERRAIN','Ember Rain','Shard-bearer ACT_BOSS_VAEL','R1',90,8,'Meteor shower 15 m radius: 12 impacts x (0.6 x AR_Lore), 40 Burn each','+4 impacts','+radius 20 m; impacts leave fire 3 s'),
('RES_LANCE','Lance of the Meridian (orbital point-defense beam)','Shard-bearer ACT_BOSS_CORSA','R2',150,4,'Orbital beam, 3 m wide, tracks a marked point at 3 m/s; 8 x AR_Lore per s','+2 s duration','Beam splits in 2 for last 2 s'),
('RES_BLOOMGATE','Bloomgate (root field)','Shard-bearer ACT_BOSS_SORREL','R3',75,8,'10 m field: enemies Root 2 s every 3 s; allies heal 2% max HP/s','+2 m radius','Allies cleansed of statuses on entry'),
('RES_IRONSKIN','Iron Skin','Shard-bearer ACT_BOSS_BRANNOCH','R4',60,12,'-40% damage taken, +60 poise, +50% Breath regen; move speed -10%','-50% damage','Reflect 20% melee damage'),
('RES_STILLPOINT','Stillpoint (slow time)','Shard-bearer ACT_BOSS_RIME','R5',120,6,'Enemies within 25 m at 30% speed (bosses 60%)','+1.5 s','Bosses 50%'),
('RES_ECHOLEGION','Echo Legion (summon past Kindled)','Shard-bearer ACT_BOSS_HOLLOWTWINS','R6',180,30,'Summons 3 Echo Kindled at 50% player stats (FRM_ECHO) for 30 s','4 Echoes','Echoes copy your Surge'),
('RES_SHARDWALL','Shardwall (instant cover)','Choir site R1 (Cinder Choir)','R1',40,20,'Crystal wall 6 x 3 m, 40% max HP x 10 durability; blocks shots both ways','2 walls','Wall reflects 25% bullets'),
('RES_UNDERTOW','Undertow (pull enemies)','Choir site R2 (Tide Choir)','R2',45,2,'Pulls enemies within 15 m to a point; 30 poise; non-boss Shock 60','+5 m','Pulled enemies Slow 2 stacks'),
('RES_GRAVITYLIFT','Gravity Lift','Choir site R3 (Root Choir)','R3',50,5,'Lifts enemies under 3 m tall within 8 m for 3 s; airborne take +30% damage','+2 s','Slam down for 1.5 x AR_Lore'),
('RES_QUIETVOICE','Quiet Voice (fear/panic)','Choir site R4 (Glass Choir)','R4',70,6,'Non-boss enemies within 20 m panic and flee; Leaders resist 50%','Leaders affected','Panicked take +20% damage'),
('RES_BLINKCHORUS','Blink Chorus (group teleport)','Choir site R5 (Rime Choir)','R5',90,0,'Teleports you and co-op allies within 30 m to a marked point up to 60 m','+20 m range','Arrival burst 2 m stagger'),
('RES_OVERCLOCK','Ostra Overclock (ability reset)','Choir site R6 (Deep Choir)','R6',240,0,'Resets Cast, Strike, Step cooldowns and gives 25% Surge','+Surge 50%','Also refills 1 Tonic')]
write('resonances.csv',['RES_ID','Resonance','Source','Region','Cooldown s','Duration s','Effect (tier 1)','Tier 2 upgrade','Tier 3 upgrade','Tier 2 cost','Tier 3 cost','Cooldown scaling'],
 [list(r)+['3 ITM_MAT_CHOIRGLASS + 20000 Ember','2 ITM_MAT_STARMETAL + 60000 Ember','Cooldown x (1 - Shaping perks) x (1 - Lore x 0.002)'] for r in R])

# ---------- Factions ----------
write('factions.csv',['FAC_ID','Faction','Type','Hub hall','Questline length','Rival (joining closes)','Theme','Join requirement','Leader (actor)'],[
 ['FAC_HULLKNIGHTS','Hull Knights','Joinable','Lantern Hold: Knights\' Gate',12,'','Honor and war','Reputation Neutral (0) + quest QST_HK_00','ACT_NPC_HULLKNIGHT_COMMANDER'],
 ['FAC_LANTERNCHURCH','Lantern Church','Joinable','Lantern Hold: Log Chapel',12,'FAC_CHOIR','Faith built on ship logs','Neutral + quest QST_LC_00','ACT_NPC_LANTERN_ARCHIVIST'],
 ['FAC_SALVAGERS','Salvagers\' Guild','Joinable','Lantern Hold: Undermarket',11,'','Thieves and traders','Infiltration 20 + quest QST_SG_00','ACT_NPC_SALVAGER_BOSS'],
 ['FAC_QUIETHAND','Quiet Hand','Joinable','Hidden: The Still Room',14,'','Assassins; contracts; opt-in invasions','Kill an innocent or find The Still Room note','ACT_NPC_QUIETHAND_SPEAKER'],
 ['FAC_CHOIR','The Choir','Joinable','Lantern Hold: Choir Spire',10,'FAC_LANTERNCHURCH','Mages who hear the Shards','Shaping 20 + quest QST_CH_00','ACT_NPC_CHOIR_PRECENTOR'],
 ['FAC_HOLLOWED','Hollowed','Enemy','-','-','-','Shard-sick swarm','Always hostile',''],
 ['FAC_REMNANT','Remnant','Enemy','-','-','-','Crashed-ship drones','Always hostile (hackable with PRK_ENGINEERING_08)',''],
 ['FAC_THORN','Thorn Clans','Enemy / neutral','-','-','-','Raiders','Hostile; Neutral at Salvagers Honored',''],
 ['FAC_CHOIRBORN','Choirborn of the Quiet','Enemy','-','-','-','Late-game elites','Always hostile',''],
])
TIERS=[('REP_HOSTILE','Hostile',-5000,-1001,'Attacked on sight in their halls; prices +50%'),('REP_WARY','Wary',-1000,-1,'No quests; prices +20%'),
('REP_NEUTRAL','Neutral',0,499,'Join quest available'),('REP_FRIENDLY','Friendly',500,1499,'Vendor tier 2; prices -5%'),('REP_HONORED','Honored',1500,2999,'Vendor tier 3; prices -10%; faction armor unlocked'),
('REP_EXALTED','Exalted',3000,5999,'Prices -15%; faction Shardborn unlocked; title'),('REP_SWORN','Sworn',6000,99999,'Questline finale; faction companion; hall bed')]
write('reputation_tiers.csv',['REP_ID','Tier','Min','Max','Unlocks'],[list(t) for t in TIERS])
write('reputation_actions.csv',['RPA_ID','Action','Base rep','Applies to','Notes'],[
 ['RPA_QUEST_MAIN','Complete faction questline quest',400,'That faction','Rival -300'],['RPA_QUEST_SIDE','Complete faction side/radiant job',120,'That faction','Weekly cap 1200 from radiant'],
 ['RPA_BOUNTY','Kill faction bounty target',60,'Hull Knights',''],['RPA_DONATE','Donate 1000 Ember',25,'Lantern Church','Max 20 per game week'],
 ['RPA_FENCE','Fence 5000 Ember of stolen goods',50,'Salvagers\' Guild',''],['RPA_CONTRACT','Contract bonus condition met',150,'Quiet Hand','Base contract 200'],
 ['RPA_INVADE','Successful invasion',80,'Quiet Hand','PvP opt-in'],['RPA_CHOIRSITE','Clear a Choir site',200,'The Choir','Lantern Church -100'],
 ['RPA_CRIME_SEEN','Crime witnessed in hall',-300,'Hall owner',''],['RPA_KILL_MEMBER','Kill a member',-1500,'That faction','Hostile for 7 game days minimum'],
 ['RPA_RIVAL_JOIN','Join rival faction',-6000,'Rival faction','Sets Hostile; reconcile only with PRK_SPEECH_12']])

# ---------- Co-op ----------
write('coop_scaling.csv',['COOP_ID','Content','Players','Enemy HP mult','Stance mult','Enemy damage mult','Ember per player','Loot rolls','Notes'],
 [['COOP_OW_%d'%p,'Open world',p,1+0.5*(p-1),1+0.25*(p-1),1.0 if p<3 else 1.1,1.0,'1 per player (instanced)','Recalculated on join/leave'] for p in (1,2,3,4)]+
 [['COOP_STRIKE_3','Strikes',3,2.0,1.5,1.1,1.0,'1 per player (instanced)','Matchmade fireteam of exactly 3; no scaling']]+
 [['COOP_BOSS_%d'%p,'Bosses',p,m,1+0.25*(p-1),1.0 if p<3 else 1.1,1.0,'1 per player','Recalculated on join/leave; Echo counts as 0.5 player'] for p,m in ((1,1.0),(2,1.7),(3,2.3),(4,2.9))]+
 [['COOP_RAID_6','Raid',6,1.0,1.0,1.0,1.0,'1 per player + Seals','Tuned for 6; no scaling'],
  ['COOP_ARENA_3V3','Arena PvP','3v3 (6)','-','-','-','-','Seals per match (win 5, loss 2)','Matchmade teams of exactly 3; gear normalized; Marlon chose 3v3 over the larger teams in the plan (3 Oct 2026)'],
  ['COOP_LEVEL','Level sync','2-4','-','-','-','-','-','Guests above region band synced down to band max +5; below band max keep own level, floor at band min']])

# ---------- Challenge scaling (no campaign difficulty menu per plan; Assist lives with the accessibility thread) ----------
write('challenge_scaling.csv',['CHL_ID','Content','Type','Enemy HP','Enemy damage','Player effect','Rewards','Notes'],[
 ['CHL_NG1','New Game+1','Cycle','x1.6','x1.5','Keep all','x1.5 Ember','Bosses +1 move weight shuffle'],
 ['CHL_NG2','New Game+2','Cycle','x1.9','x1.7','Keep all','x1.75 Ember',''],
 ['CHL_NG3','New Game+3','Cycle','x2.1','x1.85','Keep all','x2.0 Ember','Cap: NG+7 same as NG+3 values +5% per extra cycle'],
 ['CHL_HOLLOWCIT','Hollowed Citadels','Endgame weekly','x2.0 at level 80','x1.6','Weekly modifier pair from list','Featured Citadel 15 Seals (ITM_LT_ENDGAME_HOLLOWED_CITADEL)','Modifiers: Burn floors, double Ward, no Tonics in phase 3, Choirborn reinforcements'],
 ['CHL_LAMPLIGHTER_RQ','The Lamplighter rematch (MQ_A3_03)','Story rematch','x1.10 (ACT_BOSS_LAMPLIGHTER rescaled from level 69 to 76)','x1.10','None','Quest reward only; no second Shardborn','Same boss, not a new one, so the count stays at 44 bosses; fought in REG_Q, arena hook ARENA_IRES_RQ']])

# ---------- Region bands ----------
write('region_bands.csv',['Region ID','Region','Min level','Max level','Element tint','Open-world scaling','Notes'],
 [[r[0],r[1],r[2],r[3],r[4],'Scales inside band only' if r[0] not in ('RH',) else 'No combat','Act 1' if r[0] in('R1','R2') else 'Act 2 open order' if r[0][1:].isdigit() else 'Act 3' if r[0]=='RQ' else ''] for r in REGIONS])

# ---------- Economy ----------
E=[('ECO_CUR_EMBER','Ember','Currency','Main currency: kindle levels, buy, upgrade','Enemy kills (FRM_EMBER_DROP), bosses, selling, quests','Kindling levels, vendors, Smithing, Resonance tiers, bribes','Dropped on death (FRM_DEATH)'),
('ECO_CUR_SEAL','Seals','Weekly token','Raid and PvP rewards','Strike 10, Hollowed Citadel 15, raid boss 20-40, arena win 5 / loss 2 (items/loot_tables.csv)','Seal Warden in Lantern Hold (items/vendors.csv ITM_VEN_SEALS)','Weekly cap 100; carry cap 500; kept on death'),
('ECO_MAT_HULLSCRAP','Hull Scrap','Material (common)','Smithing +1 to +5, Tinkering','Remnant, wrecks, dismantle Common/Forged','Upgrades','Cannot be bought'),
('ECO_MAT_SHARDDUST','Shard Dust','Material (uncommon)','Smithing +6 to +10, Rites','Hollowed, Choirborn, crystal nodes (R2+)','Upgrades, Rites','Cannot be bought'),
('ECO_MAT_CHOIRGLASS','Choir Glass','Material (rare)','Smithing +11 to +14, Resonance tier 2','Choirborn, Choir sites, Citadel bosses','Upgrades, Resonances','Cannot be bought'),
('ECO_MAT_STARMETAL','Starmetal','Material (endgame)','Smithing +15, Shardborn upgrades, Resonance tier 3','Shard-bearers, raids, Hollowed Citadels','Max upgrades','Cannot be bought')]
write('economy_currencies.csv',['ECO_ID','Name','Kind','Use','Sources','Sinks','Rules'],[list(e) for e in E])
write('economy_formulas.csv',['ECOF_ID','Formula','Expression','Example'],[
 ['ECOF_LEVEL','Kindle a level','floor(0.02 L^3 + 3 L^2 + 100 L + 500)',f'L10 = {player_level_cost(10)}; L35 = {player_level_cost(35)}; L70 = {player_level_cost(70)}'],
 ['ECOF_DROP','Enemy Ember','0.16 x DropMult x (10 + 1.5 L^1.5)',f'Fodder L35 = {ember_drop(35,0.5)}; Heavy L35 = {ember_drop(35,2.0)}'],
 ['ECOF_BOSS','Boss Ember','ClassEmber (Site 0.1, Field 0.4, Citadel 0.6, Shard-bearer 1.0, Undervault 0.4, Raid 0.5, Final 1.0) x Kindle cost at boss level',f'Vael L12 = {round(1.0*player_level_cost(12))}'],
 ['ECOF_UPGRADE','Smithing upgrade to +n','Ember = Step(n) x RarityMult (Common 1, Forged 1.3, Rare 1.7, Relic 2.2, Shardborn 3.0); Step(n) = weapon 150 x 1.18^(n-1), armor 120 x 1.3^(n-1), rounded to 10 (items/upgrade_costs.csv); materials per data/items','+5 Rare weapon = '+str(round(150*1.18**4*1.7/10)*10)],
 ['ECOF_BUY','Buy price','ItemBase x PriceMult(rarity) x (1 + 0.05 u) x (1 - min(0.20, Speech/500)) x FactionTierDiscount','Base and PriceMult from data/items (ITM_F_PRICE_BUY)'],
 ['ECOF_SELL','Sell price','floor(Buy price at Speech 0 x 0.12 x (1 + Speech/1000)) (ITM_F_PRICE_SELL)','Stolen goods only to Salvagers (PRK_SPEECH_03)'],
 ['ECOF_RESTOCK','Vendor restock','Every 72 game hours; vendor Ember unlimited','Investor perk adds stock'],
 ['ECOF_DEATH','Death loss','On death: ghost = carried Ember; on second death before recovery: new ghost = carried + 50% of old ghost','Expected loss per unrecovered death = 50% of one ghost'],
 ['ECOF_RITE','Rite cost','Ember = sum over effects (Magnitude^1.3 x Duration^0.6 x Area^0.4 x EffectBase) x (1 - Shaping/250)','Crafted bonus cap 15% (18% with PRK_ENGINEERING_12 for Smithing/Tinkering)'],
 ['ECOF_BRIBE','Bounty clear','Bounty x 1.0 (Bribe perk 0.6)','Bounty = 40 per minor crime, 1000 per murder'],
 ['ECOF_INFLOW','Target Ember income','All sources per hour of play at band: about 1.9 x Kindle cost at band midpoint, about 65% of it spent on kindling (B08 SIM-01)','Region 3 midpoint L27: '+str(round(1.9*player_level_cost(27)))+' per hour'],
 ['ECOF_SEALS','Seal prices','Raid armor piece 15, raid weapon 20, Strider skin 10 (cosmetic shop items cannot be bought with Seals and Seals cannot be bought)','Weekly cap 100'],
])
