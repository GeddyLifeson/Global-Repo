from common import *

# ---------- Base player resources ----------
write('player_base_stats.csv', ['STAT_ID','Stat','Base','Per Vigor point','Per attribute point','Attribute','Cap','Regen / rule','Notes'], [
 ['STAT_HEALTH','Health',400,8,4,'Grit',1600,'Only restored by Tonics, Anchors, lifesteal perks','Red bar'],
 ['STAT_WARD','Ward',150,8,3,'Lore',900,'Full refill starts 4.5 s after last hit; refills at 12.5% of max per second','Blue bar over Health'],
 ['STAT_BREATH','Breath',100,8,0,'-',300,'Regen 40/s after 1.2 s since last spend; 20/s while blocking; 50% regen while Exhausted','Green bar, stamina'],
 ['STAT_EQUIPLOAD','Equip Load',40,0,1,'Might',140,'Light <30%, Medium <70%, Heavy <=100%, Overloaded >100% (walk only)','Weight units'],
 ['STAT_POISE','Poise',0,0,0.5,'Might',150,'From armor; resets 8 s after last hit','Hyperarmor during heavy attacks adds weapon poise'],
 ['STAT_STATUSRES','Status Resist',20,0,1.5,'Grit',200,'Status buildup threshold for player = 100 + Status Resist','Per status'],
 ['STAT_ABILRECH','Ability Recharge',0,0,0.4,'Lore',40,'% cooldown reduction, cap 40%','Cast/Strike/Step/Surge'],
 ['STAT_CRIT','Critical Damage',100,0,1,'Finesse',180,'% of AR on ripostes, backstabs, stance-break crits','Base crit multiplier 3.0x of AR'],
 ['STAT_BREATHREGEN','Breath Regen Bonus',0,0,0.5,'Finesse',30,'% bonus to 40/s base','-'],
 ['STAT_CARRY','Carry Weight',150,0,2,'Might',350,'Over limit: no sprint, no fast travel','Inventory, not Equip Load'],
 ['STAT_TONICS','Tonic charges',4,0,0,'-',12,'+1 per Tonic Seed (8 in world); each heals 45% max Health over 0.8 s','Refill at Anchors'],
 ['STAT_TONICHEAL','Tonic heal',0.45,0,0,'-',0.60,'+0.05 per Tonic upgrade (3 upgrades, ITM_MAT_TONICBLOOM)','Fraction of max Health'],
 ['STAT_MOVESPEED','Move speed',5.0,0,0,'-',8.0,'Walk 2.0 m/s, run 5.0, sprint 7.0, crouch 2.5; Heavy load -10%','m/s'],
 ['STAT_ROLL','Roll',0,0,0,'-',0,'Light: 13 i-frames of 24, 4.5 m; Medium: 12 of 28, 4.0 m; Heavy: 9 of 36, 3.0 m; Breath 15','60 fps frames'],
 ['STAT_PARRY','Parry window',6,0,0,'-',10,'6 active frames; Assist adds +4; riposte window 60 frames','60 fps'],
 ['STAT_BURNT','Burnt Ward/Breath',0,0,0,'-',0.30,'5% of Ward damage and 3% of Breath spent lowers that bar max until rest; floor 70% of max','Clears at Anchor'],
])

# ---------- Attributes ----------
write('attributes.csv', ['ATTR_ID','Attribute','Scales','Secondary effects','Soft cap 1','Soft cap 2','Hard cap'], [
 ['ATTR_MIGHT','Might','Heavy Arms, Polearms, Unarmed, heavy firearms, Iron Weave','+1 Equip Load, +0.5 Poise, +2 Carry per point',20,35,60],
 ['ATTR_FINESSE','Finesse','Blades, curved/dagger/twinblade, all light firearms','+1% Crit Damage, +0.5% Breath regen per point',20,35,60],
 ['ATTR_LORE','Lore','All Weave abilities, Shard lance, Resonance power','+3 Ward, -0.4% ability cooldown per point',20,35,60],
 ['ATTR_GRIT','Grit','Shields, Guard counters, Tonic potency over 30','+4 Health, +1.5 Status Resist per point; Tonic +0.5% per point above 30',20,35,60],
])
def attr_curve(p):
    v=0
    for i in range(1,p+1):
        v += 0.025 if i<=20 else 0.02 if i<=35 else 0.01 if i<=50 else 0.005
    return round(v,4)
write('attribute_scaling_curve.csv',['Points','Curve value (0-1)','Marginal'],[[p,attr_curve(p),round(attr_curve(p)-attr_curve(p-1),4) if p>1 else 0.025] for p in range(1,61)])
write('scaling_grades.csv',['Grade','Coefficient','Max bonus at 60 points','Meaning'],[
 [g,c,f'+{round(c*100)}%',d] for g,c,d in [('S',1.5,'Primary, build-defining'),('A',1.2,'Primary'),('B',0.9,'Strong secondary'),('C',0.6,'Secondary'),('D',0.35,'Light'),('E',0.15,'Trace'),('-',0,'None')]])

# ---------- Character level ----------
rows=[];cum=0;cumE=0
for L in range(1,101):
    nxt = round(12.5*L+75) if L<100 else 0
    ec = player_level_cost(L) if L<100 else 0
    rows.append([L,nxt,cum,ec,cumE,L-1,L-1,(L-1)//2,
        next((r[1] for r in REGIONS[:6] if r[2]<=L<=r[3]),'Endgame' if L>70 else '')])
    cum+=nxt;cumE+=ec
write('level_curve.csv',['Level','Skill-XP to next','Cumulative skill-XP','Ember to kindle next','Cumulative Ember','Vigor points total','Perk points total','Attribute points total','Matching region band'],rows)

# ---------- Skills ----------
SK=[('SKL_BLADES','Blades','Steel','Finesse','combat'),('SKL_HEAVY','Heavy Arms','Steel','Might','combat'),
('SKL_POLEARMS','Polearms','Steel','Might','combat'),('SKL_GUARD','Guard','Steel','Grit','combat'),
('SKL_UNARMED','Unarmed','Steel','Might','combat'),('SKL_EMBERRITE','Ember Rite','Weave','Lore','combat'),
('SKL_STORMRITE','Storm Rite','Weave','Lore','combat'),('SKL_HOLLOWRITE','Hollow Rite','Weave','Lore','combat'),
('SKL_WARDING','Warding','Weave','Lore','combat'),('SKL_SHAPING','Shaping','Weave','Lore','combat'),
('SKL_FIREARMS','Firearms','Salvage','Finesse','combat'),('SKL_ENGINEERING','Engineering','Salvage','Lore','craft'),
('SKL_INFILTRATION','Infiltration','Salvage','Finesse','craft'),('SKL_SPEECH','Speech','Salvage','Grit','craft')]
COVER={'SKL_BLADES':'Straight sword, curved blade, dagger, twinblade','SKL_HEAVY':'Greatsword, axe, hammer','SKL_POLEARMS':'Polearm, spear, glaive',
'SKL_GUARD':'Shields, blocking, parry, guard counter','SKL_UNARMED':'Fist weapons, kicks, grabs','SKL_EMBERRITE':'Ember and Iron Weave abilities',
'SKL_STORMRITE':'Storm and Frost Weave abilities','SKL_HOLLOWRITE':'Hollow and Bloom Weave abilities','SKL_WARDING':'Ward capacity, Ward recharge, counter-cast',
'SKL_SHAPING':'Resonances, Rites crafting, Echo summons','SKL_FIREARMS':'All firearms and Shard lance','SKL_ENGINEERING':'Tinkering, Smithing, vehicles, turrets, hacking',
'SKL_INFILTRATION':'Stealth, lockpicking, pickpocket, backstab','SKL_SPEECH':'Persuade, barter, faction reputation gain'}
write('skills.csv',['SKL_ID','Skill','Group','Primary attribute','XP curve','Covers','Start rank (no Origin bonus)','Max rank','Perk tree size'],
 [[a,b,c,d,'CRV_COMBAT' if e=='combat' else 'CRV_CRAFT',COVER[a],5,100,12] for a,b,c,d,e in SK])
rows=[];cc=0;cf=0
for r in range(1,100):
    c=round(1.0*r**1.95+10); f=round(1.4*r**1.95+25)
    cc+=c;cf+=f; rows.append([r,c,cc,f,cf,r+1])
write('skill_rank_curve.csv',['Rank','CRV_COMBAT XP to next','CRV_COMBAT cumulative','CRV_CRAFT XP to next','CRV_CRAFT cumulative','Character skill-XP granted on reaching next rank'],rows)

A=[('SKL_BLADES',[('Hit enemy with blade',6),('Critical/riposte with blade',30),('Stance break with blade',20),('Kill with blade',12)]),
('SKL_HEAVY',[('Hit enemy with heavy weapon',8),('Charged heavy hit',14),('Stance break',20),('Kill',12)]),
('SKL_POLEARMS',[('Hit enemy with polearm',6),('Hit at max reach (>2.5 m)',9),('Mounted polearm hit',10),('Kill',12)]),
('SKL_GUARD',[('Block an attack (per 10 damage blocked)',3),('Perfect parry',25),('Guard counter hit',15),('Survive hit while blocking above 50% Breath',4)]),
('SKL_UNARMED',[('Unarmed hit',5),('Grab/throw',18),('Kill unarmed',14),('Stance break unarmed',22)]),
('SKL_EMBERRITE',[('Ember/Iron ability hit (per target)',10),('Apply Burn',12),('Kill with Ember/Iron',14),('Trigger combo Ember-on-Root',25)]),
('SKL_STORMRITE',[('Storm/Frost ability hit (per target)',10),('Apply Shock or Slow',12),('Trigger Shatter combo',25),('Kill',14)]),
('SKL_HOLLOWRITE',[('Hollow/Bloom ability hit (per target)',10),('Apply Drain or Root',12),('Heal ally via Bloom (per 50 HP)',6),('Kill',14)]),
('SKL_WARDING',[('Ward absorbs damage (per 20)',2),('Counter-cast an enemy spell',30),('Break enemy Ward with opposite element',15),('Full Ward recharge mid-fight',5)]),
('SKL_SHAPING',[('Use a Resonance',40),('Craft a Rite',25),('Summon an Echo',20),('Resonance hit (per target)',8)]),
('SKL_FIREARMS',[('Firearm hit',4),('Headshot',10),('Kill with firearm',10),('Hit beyond optimal range',6)]),
('SKL_ENGINEERING',[('Tinker an item',15),('Smith an upgrade (per level)',30),('Hack a turret/door',35),('Repair vehicle part',12)]),
('SKL_INFILTRATION',[('Each 5 s undetected within 15 m of enemy',2),('Pick a lock (by tier 1-5)',10),('Pickpocket success',20),('Sneak attack',25)]),
('SKL_SPEECH',[('Successful persuade',40),('Buy/sell (per 500 Ember)',5),('Complete faction quest',60),('Discover new dialogue option',8)])]
rows=[]
for s,acts in A:
    for i,(a,x) in enumerate(acts,1): rows.append([f'{s}_XP{i}',s,a,x,'XP x clamp(enemy level / player level, 0.5, 2.0) where an enemy is involved; 0 vs targets 10+ levels below'])
write('skill_xp_actions.csv',['XPA_ID','SKL_ID','Action','Base XP','Modifier'],rows)

# ---------- Origins ----------
O=[('ORG_CRASHKNIGHT','Crash-Knight','Hull Knight in salvaged plate',(16,10,6,14),(4,0,2),{'SKL_HEAVY':20,'SKL_GUARD':20,'SKL_BLADES':10},['ITM_WPN_GREATSWORD_HULLCLEAVER','ITM_SHD_HULLPLATE_KITE','ITM_ARM_CRASHKNIGHT_SET']),
('ORG_HULLWITCH','Hullwitch','Ship-tech caster',(6,10,18,10),(0,4,2),{'SKL_EMBERRITE':20,'SKL_STORMRITE':15,'SKL_WARDING':15},['ITM_CAT_HULLWITCH_FOCUS','ITM_WPN_DAGGER_RIVET','ITM_ARM_HULLWITCH_SET']),
('ORG_SCAVENGER','Scavenger','Wreck-diver with guns',(8,16,8,12),(2,2,2),{'SKL_FIREARMS':20,'SKL_ENGINEERING':20,'SKL_INFILTRATION':10},['ITM_WPN_SCOUTRIFLE_SALVAGE','ITM_WPN_PISTOL_RIVETGUN','ITM_ARM_SCAVENGER_SET']),
('ORG_LANTERNPRIEST','Lantern Priest','Church warden of ship logs',(10,8,14,12),(2,2,2),{'SKL_HOLLOWRITE':20,'SKL_WARDING':15,'SKL_SPEECH':15},['ITM_WPN_HAMMER_CENSER','ITM_CAT_LANTERN_TOME','ITM_ARM_LANTERNPRIEST_SET']),
('ORG_RANGER','Ranger','Wilds hunter',(10,16,10,8),(2,0,4),{'SKL_POLEARMS':20,'SKL_FIREARMS':15,'SKL_INFILTRATION':15},['ITM_WPN_POLEARM_THORNSPEAR','ITM_WPN_SNIPER_LONGBARREL','ITM_ARM_RANGER_SET']),
('ORG_UNBOUND','Unbound','Blank slate, no kit',(10,10,10,10),(0,0,0),{},['ITM_ARM_COLONIST_RAGS'])]
rows=[]
for oid,n,d,(m,f,l,g),(vh,vw,vb),sk,kit in O:
    hp=400+vh*8+g*4; ward=150+vw*8+l*3; br=100+vb*8
    rows.append([oid,n,d,m,f,l,g,m+f+l+g,vh,vw,vb,hp,ward,br,'; '.join(f'{k}+{v}' for k,v in sk.items()) or 'None (+6 free attribute points instead)',
        ' | '.join(kit),'ITM_CON_TONIC x4; ITM_AMMO_COMMON x60' if oid!='ORG_UNBOUND' else 'ITM_CON_TONIC x4; 1500 Ember'])
write('origins.csv',['ORG_ID','Origin','Fantasy','Might','Finesse','Lore','Grit','Attribute total','Vigor in Health','Vigor in Ward','Vigor in Breath','Start Health','Start Ward','Start Breath','Skill bonuses (added to base 5)','Starting kit (item refs)','Starting consumables'],rows)

# ---------- Weave abilities (6 elements x 4 slots) ----------
SLOT={'Cast':(8.0,1.0,'Thrown/launched, 2.5 m blast'),'Strike':(10.0,1.4,'Melee-range burst, 3 m cone'),'Step':(6.0,0.0,'Dash 6 m, 10 i-frames'),'Surge':(0,3.5,'Super; charged by damage and kills')}
NAMES={'Ember':['Cinder Flask','Forge Palm','Flare Step','Kiln Heart'],'Storm':['Arc Seed','Thunder Knuckle','Bolt Step','Tempest Crown'],
'Hollow':['Null Orb','Siphon Grip','Shade Step','Eclipse'],'Frost':['Rime Shard','Glacier Fist','Skate','Winter Hymn'],
'Bloom':['Thorn Pod','Root Lash','Petal Step','Verdant Gate'],'Iron':['Rivet Mine','Anvil Strike','Bulwark Step','Iron Crown']}
SKL={'Ember':'SKL_EMBERRITE','Iron':'SKL_EMBERRITE','Storm':'SKL_STORMRITE','Frost':'SKL_STORMRITE','Hollow':'SKL_HOLLOWRITE','Bloom':'SKL_HOLLOWRITE'}
STAT={'Ember':'Burn','Storm':'Shock','Hollow':'Drain','Frost':'Slow','Bloom':'Root','Iron':'Shatter'}
rows=[]
for e in ELEMENTS:
    for i,(s,(cd,mult,desc)) in enumerate(SLOT.items()):
        cdv={'Cast':28,'Strike':22,'Step':8,'Surge':0}[s]
        rows.append([f'ABL_{e.upper()}_{s.upper()}',NAMES[e][i],e,s,SKL[e],mult,cdv,'Charge 100% (damage dealt 1 pt per 10 dmg, kill +6, assist +3, passive 0.5/s)' if s=='Surge' else '',
            {'Cast':40,'Strike':35,'Step':0,'Surge':300}[s],STAT[e],desc,'Damage = AR_Lore x Mult; AR_Lore = (60 + 4 x Lore) x (1 + rite skill rank/200)','Cast/Strike radius +10% per perk rank'])
write('weave_abilities.csv',['ABL_ID','Name','Element','Slot','Skill','Damage mult','Cooldown s','Surge charge rule','Status buildup','Status','Shape','Damage formula','Notes'],rows)

# ---------- Statuses ----------
write('status_effects.csv',['STS_ID','Status','Element','Enemy threshold (base)','Player threshold','Decay per s','Duration s','Effect','Immunity after s'],[
 ['STS_BURN','Burn','Ember',100,'100+Status Resist',10,6,'2% max HP + 5 per s; -20% healing received',4],
 ['STS_SHOCK','Shock','Storm',100,'100+Status Resist',12,4,'Ward recharge disabled; next hit chains 30% damage to 2 targets within 6 m',5],
 ['STS_DRAIN','Drain','Hollow',120,'120+Status Resist',8,5,'Lose 3% max Ward and 3% max Breath per s; attacker heals 1% of their max HP per s',6],
 ['STS_SLOW','Slow','Frost',100,'100+Status Resist',10,5,'-30% move and attack speed; at 3 stacks within 10 s becomes Frozen (2.5 s, x1.3 damage taken)',8],
 ['STS_ROOT','Root','Bloom',110,'110+Status Resist',10,3,'Cannot move or dodge; can still attack and block',6],
 ['STS_SHATTER','Shatter','Iron',130,'130+Status Resist',6,8,'Armor and Defense -25%; +20% poise damage taken',6],
 ['STS_EXHAUST','Exhausted','None','-','Breath hits 0',0,1.5,'Cannot roll or sprint; Breath regen 50%',0],
])
write('element_combos.csv',['CMB_ID','Trigger','Requires','Effect','Cooldown per target s'],[
 ['CMB_SHATTERSHOCK','Frost hit','Target Shocked','+50% stance damage for 4 s',10],
 ['CMB_WILDFIRE','Ember hit','Target Rooted','Burn spreads to all Rooted targets within 5 m',8],
 ['CMB_THAWDRAIN','Hollow Drain','Target Frozen','Freeze ends; caster heals 10% of damage dealt',8],
 ['CMB_MAGNETIC','Storm hit','Target Shattered','Pulls targets within 4 m to the hit target, 1 s stagger',12],
 ['CMB_OVERGROWTH','Bloom hit','Target Burning','Burn ends; Root duration +100%',10],
 ['CMB_VOIDRIME','Frost hit','Target Drained','Drain duration resets; target Slow stacks +1',10]])
write('element_matrix.csv',['Attacker element']+ELEMENTS+['Kinetic'],[
 [a]+[(3.0 if OPPOSITE[d]==a else 0.5 if d==a else 1.0) for d in ELEMENTS]+[0.5] for a in ELEMENTS]+[['Kinetic (vs Ward)']+[0.5]*6+[0.5],['Weave any (vs Health)']+[0.8]*6+[1.0]])

# ---------- Formulas ----------
F=[('FRM_AR','Attack Rating','AR = WeaponBase x (1 + sum over attributes of GradeCoef x AttrCurve(points)) x (1 + upgrade bonus) ','Grades from scaling_grades.csv, curve from attribute_scaling_curve.csv; weapon base and upgrade from data/items'),
('FRM_DMG','Damage dealt','Dmg = AR x MoveMult x 100 / (100 + TargetDefense) x (1 - TargetResist[type]) x ElementMult x CritMult x CoopFactor','Minimum 10% of AR x MoveMult'),
('FRM_WARDHIT','Damage vs Ward','WardDmg = Dmg x (Kinetic 0.5 | Weave 1.5) x (3.0 if element is Ward tint opposite); overflow carries to Health at Kinetic 1.0 / Weave 0.8','Ward always absorbs before Health'),
('FRM_HEADSHOT','Headshot','x2.0 damage only when target Ward = 0; x1.25 on Ward','Bosses: weak points per boss_parts'),
('FRM_FALLOFF','Firearm falloff','Mult = 1 at <= OptimalRange, linear to 0.5 at 2 x OptimalRange, floor 0.5','Optimal range per weapon in data/items'),
('FRM_CRIT','Critical strike','Dmg = AR x WeaponCritMult(default 3.0) x (Crit Damage/100)','Riposte, backstab, stance-break crit'),
('FRM_POISE','Player poise','Staggered when incoming poise damage in 8 s window > Poise; heavy-attack hyperarmor adds WeaponPoise','Knockdown on 3rd stagger within 6 s, then 2 s immunity'),
('FRM_STANCE','Enemy stance','Stance meter fills by attack poise damage; break at Stance value; regen after Stance/13 s delay at 10% per s','Break opens crit window 120 frames (bosses 150)'),
('FRM_BLOCK','Block cost','BreathCost = Dmg x (1 - ShieldStability/100); Guard Break if Breath < cost','Chip damage = Dmg x (1 - Shield physical block %)'),
('FRM_BREATH','Breath regen','Regen = 40 x (1 + Finesse bonus) per s after 1.2 s; 20/s while blocking','Light 12-18, heavy 25-35, roll 15, backstep 8, sprint 8/s, jump 10'),
('FRM_STATUS','Status buildup','Buildup per hit = AbilityBuildup x (1 + rite rank/200); proc at threshold; threshold +25% after each proc for 30 s','Bosses x2.0 threshold'),
('FRM_ROLLTYPE','Roll type','LoadRatio = Equipped weight / Equip Load; Light < 0.30, Medium < 0.70, Heavy <= 1.00','See STAT_ROLL'),
('FRM_LEVELUP','Level up','Skill rank-up grants character skill-XP = new rank; when skill-XP passes level threshold the level is kindled at an Anchor for Ember','level_curve.csv'),
('FRM_EMBER_LEVELCOST','Ember to kindle a level','Cost(L) = floor(0.02 L^3 + 3 L^2 + 100 L + 500)','L = current level'),
('FRM_ENEMY_HP','Enemy health','Base and leader enemies: absolute HP per level from DR-SYS-010 rev 2 (tools/enemy_curve_target.csv); outside their band and for creatures, RoleMult x FactionMult x (60 + 18 L), scaled to meet the band edge. HP rises every level','enemies.csv'),
('FRM_ENEMY_DMG','Enemy damage','Dmg = AttackMult x Damage per 1.0 mult at level (enemy_stats_by_level.csv, DR-SYS-010 rev 2); creatures use AttackMult x (8 + 1.6 L)','enemy_attacks.csv'),
('FRM_ENEMY_DEF','Enemy defense','Def = DefMult x (10 + 2 L)','Used in FRM_DMG'),
('FRM_EMBER_DROP','Enemy Ember','Ember = 0.16 x DropMult x (10 + 1.5 L^1.5) x (0.25 if 10+ levels below player)','Echo summons do not reduce drops'),
('FRM_BOSS_HP','Boss health','HP = ClassMult x (400 + 140 L), rounded to 10','bosses.csv'),
('FRM_BOSS_DMG','Boss damage','Dmg = MoveMult x (20 + 4 L)','boss_moves.csv'),
('FRM_DEATH','Death','All carried Ember drops as Shard-ghost; recover = 100%; die before recovering = ghost replaced, 50% of old ghost added to new ghost','Ghost persists through fast travel'),
('FRM_TONIC','Tonic','Heal = MaxHealth x TonicHeal (0.45 + 0.05 per upgrade) x (1 + 0.005 x max(0, Grit-30))','0.8 s heal, 1.1 s animation'),
('FRM_ECHO','Echo summon','Echo level = player level; HP 70%, damage 60% of an equal-level player build; 1 Echo, despawns on boss kill or Echo death','Costs ITM_CON_ECHOSIGIL'),
('FRM_UTILITY','AI utility score','Score(point) = wDist x (1 - dist/30) + wCover x CoverQuality + wAllies x min(allies,4)/4 + wWard x (OwnWard/MaxWard) - wExposure x LoS_to_player','Weights per AIP in ai_profiles.csv; re-evaluate every 0.5 s'),
('FRM_MORALE','Morale','Morale starts at profile base; on leader death Fodder flee for 6 s at 60% chance (plan 3.4, DR-014), others -40; -10 per ally death within 15 m, +20 while leader alive within 20 m; panic below PanicThreshold (flee 6 s)','Fodder/skirmisher only'),
('FRM_ACCURACY','Enemy hit chance','P(hit) = Acc10 at <= 10 m, linear to Acc30 at 30 m, to Acc60 at 60 m; x0.6 if player sprinting, x0.75 if in partial cover','Per AIP'),
('FRM_REP','Reputation gain','Gain = Base x (1 + Speech rank/200) x (0.5 if rival-faction aligned)','reputation_actions.csv'),
('FRM_PRICE','Buy price','Price = ItemBase x (1 - min(0.20, Speech/500)) x FactionDiscount','Sell = 12% of base x (1 + Speech/1000)'),
]
write('derived_formulas.csv',['FRM_ID','Name','Formula','Notes / source table'],[list(f) for f in F])
