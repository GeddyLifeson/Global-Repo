#!/usr/bin/env python3
"""Generates every Shardfall item table in this folder. Re-run to rebuild: python3 gen_items.py
Owned by the gear-and-items thread. IDs prefixed ITM_. Placeholders: ACT_* (data/actors), TXT_*/UI_* (data/ui), LOC_* (world)."""
import csv, os, random, math, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "actors", "tools"))
from common import player_level_cost
OUT = os.path.dirname(os.path.abspath(__file__))
R = random.Random(20261003)
def w(name, rows, cols):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        cw = csv.writer(f); cw.writerow(cols)
        for r in rows: cw.writerow([(int(v) if isinstance(v,float) and v.is_integer() and c.endswith(('price','value','ember')) else v) for c,v in ((c,r.get(c, '')) for c in cols)])
    print(f'{name}: {len(rows)}')

# ---------- core tables ----------
RAR = [  # id, name, hex, perk cols, armor rolls, stat mult, price mult, dismantle Hull Scrap, Shard Dust, Choir Glass, Starmetal
 ('COM','Common','#8A857A',0,0,1.00,1,2,0,0,0),('FRG','Forged','#A87A4A',2,1,1.04,2,4,1,0,0),
 ('RAR','Rare','#4F8FE6',3,2,1.08,4,6,2,0,0),('REL','Relic','#9B7BD6',4,3,1.12,8,8,4,1,0),
 ('SHB','Shardborn','#8FE3EE',4,0,1.12,15,10,6,3,1)]
RARMULT = {r[0]: r[5] for r in RAR}; PRICEMULT = {r[0]: r[6] for r in RAR}; RARNAME = {r[0]: r[1] for r in RAR}
w('rarities.csv', [dict(rarity_id='ITM_RAR_'+r[0], name=r[1], frame_color_hex=r[2], weapon_perk_columns=r[3],
   armor_stat_rolls=r[4] if r[0]!='SHB' else 'fixed', ar_and_armor_mult=r[5], price_mult=r[6],
   dismantle_hull_scrap=r[7], dismantle_shard_dust=r[8], dismantle_choir_glass=r[9], dismantle_starmetal=r[10],
   equip_limit='1 weapon + 1 armor piece' if r[0]=='SHB' else 'none', frame_icon='UI_ICON_RARITY_'+r[0]) for r in RAR],
  ['rarity_id','name','frame_color_hex','weapon_perk_columns','armor_stat_rolls','ar_and_armor_mult','price_mult',
   'dismantle_hull_scrap','dismantle_shard_dust','dismantle_choir_glass','dismantle_starmetal','equip_limit','frame_icon'])

ELEM = {'EMB':('Ember','Burn','FRS'),'STM':('Storm','Shock','BLM'),'HOL':('Hollow','Drain','IRN'),
        'FRS':('Frost','Slow','EMB'),'BLM':('Bloom','Root','STM'),'IRN':('Iron','Shatter','HOL')}
dt = [dict(dmg_id='ITM_DMG_SLA',name='Slash',family='Physical',vs_ward=1.0,vs_flesh=1.0,status='',ward_tint_breaks_3x='',notes='Melee edges'),
      dict(dmg_id='ITM_DMG_STR',name='Strike',family='Physical',vs_ward=1.0,vs_flesh=1.0,status='',ward_tint_breaks_3x='',notes='+30% stance damage vs armored (ACT_ tag armored)'),
      dict(dmg_id='ITM_DMG_PRC',name='Pierce',family='Physical',vs_ward=1.0,vs_flesh=1.0,status='',ward_tint_breaks_3x='',notes='Counter hits x1.25'),
      dict(dmg_id='ITM_DMG_KIN',name='Kinetic',family='Firearm',vs_ward=0.5,vs_flesh=1.25,status='',ward_tint_breaks_3x='',notes='Plan 3.4: strong vs flesh weak vs Ward')]
for k,(n,s,opp) in ELEM.items():
    dt.append(dict(dmg_id='ITM_DMG_'+k,name=n,family='Weave',vs_ward=1.5,vs_flesh=0.8,status=s,ward_tint_breaks_3x=ELEM[opp][0]+'-tinted Ward',notes=f'Opposite of {ELEM[opp][0]}; status threshold per enemy in data/actors'))
w('damage_types.csv', dt, ['dmg_id','name','family','vs_ward','vs_flesh','status','ward_tint_breaks_3x','notes'])
w('element_combos.csv', [
  dict(combo_id='ITM_CMB_01',first_status='Shock',then_element='Frost',result='Shatter',effect='+50% stance damage on the triggering hit and for 3 s'),
  dict(combo_id='ITM_CMB_02',first_status='Root',then_element='Ember',result='Wildfire',effect='Burn spreads to all Rooted targets within 5 m'),
  dict(combo_id='ITM_CMB_03',first_status='Frozen (Slow at full)',then_element='Hollow',result='Thaw Drain',effect='Freeze ends; attacker restores Ward equal to 10% of damage dealt')],
  ['combo_id','first_status','then_element','result','effect'])

GR = [('S',1.40,1.30),('A',1.10,1.00),('B',0.85,0.75),('C',0.60,0.50),('D',0.35,0.25),('E',0.15,0.01)]
GCOEF = {g:c for g,c,_ in GR}
w('scaling_grades.csv',[dict(grade=g,coef_at_plus0=c,display_threshold=t,coef_per_upgrade='+2.5% of coef per upgrade level') for g,c,t in GR],
  ['grade','coef_at_plus0','display_threshold','coef_per_upgrade'])
w('stat_curve.csv',[dict(attribute_value=s,stat_factor=f) for s,f in [(0,0),(10,0.20),(20,0.45),(40,0.75),(60,0.90),(80,1.00),(99,1.05)]],
  ['attribute_value','stat_factor'])

F = [
 ('F_UPG_MULT','Upgrade multiplier','up_mult(u) = 1 + 0.075*u ; weapons u=0..20, armor u=0..10 uses 1 + 0.06*u','+20 weapon = 2.5x base'),
 ('F_SCALE_COEF','Scaling coefficient','coef(grade,u) = grade_coef * (1 + 0.025*u)','grades from scaling_grades.csv'),
 ('F_STAT_FACTOR','Attribute factor','stat_factor(s) = piecewise linear over stat_curve.csv','soft caps 20/40/60/80'),
 ('F_AR','Attack rating per damage type','AR_t = base_t*up_mult(u)*rar_mult + sum over Might,Finesse,Lore,Grit of base_t*coef(grade_a,u)*stat_factor(attr_a)','physical scales with listed physical grades; element part scales with Lore (Iron with Grit)'),
 ('F_REQ','Unmet requirement','if any attr < req: AR = base*up_mult*rar_mult*0.6 and scaling 0; Breath costs +25%',''),
 ('F_HIT','Damage per hit','dmg = AR_t * motion_value * (1 - target_absorb_t) * (vs_ward or vs_flesh from damage_types)','target_absorb from data/actors'),
 ('F_PRECISION','Precision hit','firearm precision x2.0 only when target Ward = 0; melee crit = AR * crit_mult * 2.5 motion','plan 3.4'),
 ('F_FALLOFF','Range falloff','mult = 1 if d<=start; min if d>=end; else lerp(1,min,(d-start)/(end-start))',''),
 ('F_SHOTGUN','Pellets','each pellet deals impact; pellets per shot in firearm_classes.csv',''),
 ('F_STATUS','Status buildup','buildup per hit = status_value * up_mult(u) * motion_value; proc when >= target threshold (data/actors); decay 10/s after 2 s',''),
 ('F_ARMOR_ABS','Player absorption','total_absorb_t = 1 - product(1 - piece_absorb_t * up_mult_armor(u))',''),
 ('F_EQUIP_LOAD','Roll weight','load% = sum(equipped weight) / max_load (ACT_PLAYER_MAX_LOAD); light <30%, medium <70%, heavy >=70%, over 100% = no roll',''),
 ('F_BLOCK','Blocking','damage through = raw * (1 - block_absorb); Breath spent = raw * (1 - stability/100)','plan Part 1b gap values'),
 ('F_PRICE_BUY','Vendor buy price','buy = base_value * price_mult(rarity) * (1 + 0.05*u)','round to nearest 10'),
 ('F_PRICE_SELL','Vendor sell price','sell = floor(buy * 0.12)','lore and key items sell 0'),
 ('F_DROP','Drop roll','for each entry in table: roll < chance; weighted tables pick one entry by weight; each co-op player rolls separately, host-validated',''),
 ('F_DROP_RARITY','Rarity of generated gear','pick rarity by region weights in drop_rarity_by_region.csv; elite x2 weight on Rare+, boss x4','generated gear never rolls Shardborn; each Shardborn is a fixed boss, raid or quest reward (B08 SIM-08)'),
 ('F_DROP_UPG','Upgrade level of dropped gear','u = randint(band_min, band_max) from drop_rarity_by_region.csv; armor u = floor(weapon u / 2)',''),
 ('F_PERK_ROLL','Perk roll','one perk per active column, drawn uniformly from the weapon class pool; no duplicate perk on one weapon',''),
 ('F_ARMOR_ROLL','Armor stat roll','n rolls by rarity; each picks a stat (Health, Ward, Breath, Ability Recharge, Equip Load) without repeat, value uniform in armor_stat_rolls.csv range, rounded to step',''),
 ('F_CRAFT_CAP','Crafting cap','any crafted bonus (brew, rite, tinker mod) total <= 15%','plan 3.6'),
 ('F_RITE_COST','Rite crafting cooldown','cooldown_s = base_cd * (magnitude/10)^1.1 * (1 + duration_s/20) * (1 + area_m/8), clamp 6..90 s','Oblivion-style; base_cd per effect in data/actors spells'),
 ('F_TONIC','Tonic heal','heal = (40% + 2.5% * potency) of max Health over 0.8 s; potency 0..8 via Tonic Distillation','count 4..12 via Tonic Seeds'),
 ('F_UPG_COST','Upgrade cost','see upgrade_costs.csv',''),
 ('F_DEATH_EMBER','Ember on death','carried Ember drops as Shard-ghost; die again before reaching it = lose 50% of it','plan 3.4'),
]
w('formulas.csv',[dict(formula_id='ITM_'+a,name=b,expression=c,notes=d) for a,b,c,d in F],['formula_id','name','expression','notes'])

REG = [('REG_01','Cinderreach',1,12,0,2,(70,24,5.5,0.5,0)),('REG_02','Region 2',10,22,2,5,(60,30,8.5,1.5,0)),
       ('REG_03','Region 3',20,33,5,8,(50,34,13,3,0)),('REG_04','Region 4',31,44,8,11,(42,36,17,5,0)),
       ('REG_05','Region 5',42,56,11,14,(34,38,21,7,0)),('REG_06','Region 6',55,70,14,17,(28,38,25,9,0)),
       ('REG_Q','The Quiet (orbital)',68,75,17,19,(20,36,31,13,0)),('REG_END','Endgame',75,80,18,20,(15,35,34,16,0))]
w('drop_rarity_by_region.csv',[dict(region_id=r[0],region_name=r[1],level_min=r[2],level_max=r[3],drop_upg_min=r[4],drop_upg_max=r[5],
   pct_common=r[6][0],pct_forged=r[6][1],pct_rare=r[6][2],pct_relic=r[6][3],pct_shardborn=r[6][4]) for r in REG],
  ['region_id','region_name','level_min','level_max','drop_upg_min','drop_upg_max','pct_common','pct_forged','pct_rare','pct_relic','pct_shardborn'])

# upgrade costs
uc=[]
for u in range(1,21):
    tier,qty = [('HULL',[2,4,6,8,10]),('DUST',[2,3,4,6,8]),('GLASS',[1,2,3,4,6]),('STAR',[1,1,2,2,3])][(u-1)//5]
    uc.append(dict(item_kind='weapon',to_level=u,material='ITM_MAT_'+tier+'_01',qty=qty[(u-1)%5],
       shardborn_extra='ITM_MAT_SPC_ASCENDANT x1' if u%5==0 else '',ember=round(150*1.18**(u-1),-1),ar_mult_after=round(1+0.075*u,3)))
for u in range(1,11):
    m,q = [('HULL',2),('HULL',4),('HULL',6),('DUST',2),('DUST',3),('DUST',5),('GLASS',2),('GLASS',3),('STAR',1),('STAR',2)][u-1]
    uc.append(dict(item_kind='armor',to_level=u,material='ITM_MAT_'+m+'_01',qty=q,shardborn_extra='ITM_MAT_SPC_ASCENDANT x1' if u in (5,10) else '',
       ember=round(120*1.3**(u-1),-1),ar_mult_after=round(1+0.06*u,3)))
w('upgrade_costs.csv',uc,['item_kind','to_level','material','qty','shardborn_extra','ember','ar_mult_after'])

# ---------- melee ----------
#  code, class, skill, dtype, baseAR, wmin,wmax, light,heavy breath, poise L/H, reach, crit, speed(startup frames light), grades M/F/L/G, primary reqs
MC = [
 ('STS','Straight Sword','Blades','SLA',118,3.0,5.0,14,27,10,22,2.2,1.0,12,'CCEE','Might/Finesse'),
 ('CRV','Curved Sword','Blades','SLA',108,2.5,4.5,12,25,8,18,2.1,1.0,10,'DBEE','Finesse'),
 ('GRS','Greatsword','Heavy Arms','SLA',170,9.0,14.0,18,35,22,40,2.9,1.0,20,'BDEE','Might'),
 ('AXE','Axe','Heavy Arms','SLA',132,4.0,7.0,15,29,14,28,2.1,1.0,14,'BEED','Might'),
 ('HMR','Hammer','Heavy Arms','STR',150,7.0,12.0,17,33,24,42,2.3,1.0,18,'AEED','Might/Grit'),
 ('POL','Polearm','Polearms','PRC',122,5.0,8.0,15,28,12,24,3.2,1.0,14,'CCEE','Might/Finesse'),
 ('FST','Fist','Unarmed','STR',82,1.0,3.0,12,25,6,14,1.2,1.0,8,'EBEC','Finesse/Grit'),
 ('DGR','Dagger','Blades','PRC',84,1.0,2.5,12,25,5,12,1.5,1.3,8,'EBDE','Finesse'),
 ('SHD','Shield','Guard','STR',70,3.0,15.0,14,28,10,22,1.6,1.0,12,'DEEB','Grit'),
 ('TWB','Twinblade','Blades','SLA',104,4.0,6.0,13,26,8,18,2.4,1.0,11,'DBEE','Finesse'),
 ('GAX','Greataxe','Heavy Arms','SLA',182,11.0,16.0,20,38,26,46,2.8,1.0,22,'BEED','Might'),
 ('GHM','Greathammer','Heavy Arms','STR',196,13.0,20.0,21,40,30,52,2.7,1.0,24,'AEEC','Might/Grit')]
MN = {
'STS':"Salvager's Shortsword|Crash-Knight Arming Sword|Hullplate Longsword|Bridge-Watch Blade|Lantern Sword|Thorn-Clan Broadsword|Meridian Officer's Sword|Anchor-Keeper Sword|Choir-Glass Edge|Banneret's Longsword|Starmetal Spatha|Orbit-Warden Sword",
'CRV':"Scavenger's Cutlass|Reed Sickle-Sword|Thorn Scimitar|Deckhand's Saber|Ashfall Falchion|Hullwitch Shamshir|Clan Reaver's Tulwar|Choir Crescent|Remnant Arc-Blade|Lantern Duelist Saber|Quiet-Touched Kopis|Starmetal Sabre",
'GRS':"Bulkhead Greatsword|Crash-Knight Zweihander|Thorn Cleaver-Blade|Keel-Spine Greatsword|Lantern Executioner|Hull Knight Claymore|Choir Monolith|Remnant Hullcutter|Ashfall Flamberge|Castellan's Greatblade|Quiet Pillar|Starmetal Colossus",
'AXE':"Hull Hatchet|Salvager's Hand Axe|Thorn Bearded Axe|Clan Battleaxe|Bulkhead Greataxe|Lantern Headsman's Axe|Ember-Forge Axe|Remnant Splitter|Choir Glass Axe|Hull Knight Broadaxe|Quiet Reaper Axe|Starmetal Waraxe",
'HMR':"Rivet Mallet|Deck Hammer|Thorn Club|Anchor Maul|Lantern Censer-Mace|Hull Knight Warhammer|Keel Breaker|Remnant Piston Hammer|Choir Bell-Hammer|Castellan's Morning Star|Quiet Gravity Maul|Starmetal Sledge",
'POL':"Salvage Pike|Mooring Spear|Thorn Partisan|Hull Knight Halberd|Lantern Glaive|Antenna Lance|Clan War-Fork|Remnant Coil Spear|Choir Needle|Banneret's Poleaxe|Quiet Tether-Spear|Starmetal Voulge",
'FST':"Wrapped Knuckles|Rivet Cestus|Thorn Claws|Hull Gauntlets|Pressure Fists|Monk's Iron Wraps|Remnant Servo-Fists|Choir Resonator Knuckles|Clan Bear-Claws|Castellan's Gauntlets|Quiet Void Grips|Starmetal Knuckles",
'DGR':"Cryo-Pod Scalpel|Salvager's Knife|Thorn Kris|Quiet Hand Stiletto|Lantern Misericorde|Deckhand's Dirk|Remnant Splinter-Blade|Choir Glass Shard-Knife|Clan Throat-Cutter|Hull Knight Rondel|Orbit Parrying Dagger|Starmetal Fang",
'SHD':"Hatch-Door Buckler|Salvage Kite Shield|Thorn Hide Shield|Hull Knight Heater|Lantern Tower Shield|Bulkhead Greatshield|Remnant Barrier Plate|Choir Mirror Shield|Clan Spiked Targe|Castellan's Pavise|Quiet Null Shield|Starmetal Aegis",
'GAX':"Wreck Greataxe|Salvager's Cleaver-Axe|Thorn Bearded Greataxe|Clan Executioner|Lantern Doom-Axe|Hull Knight Moon-Axe|Ember-Forge Greataxe|Remnant Rotor-Axe|Choir Crescent Axe|Castellan's Greataxe|Quiet Reaper|Starmetal Greataxe",
'GHM':"Bulkhead Ram|Salvage Anvil|Thorn Root-Maul|Clan Boulder Hammer|Lantern Bell-Ram|Hull Knight Siege Hammer|Keel Hammer|Remnant Pile Driver|Choir Monolith Maul|Castellan's Greathammer|Quiet Collapse|Starmetal Greathammer",
'TWB':"Rotor Twinblade|Salvager's Staffblade|Thorn Double-Glaive|Lantern Twin-Flame|Remnant Turbine Blade|Choir Twinned Edge|Clan Bonebreaker|Hull Knight Dual Edge|Ashfall Whirlblade|Orbit Gyre-Blade|Quiet Ellipse|Starmetal Twinblade"}
KW = [('Lantern','EMB'),('Ember','EMB'),('Cinder','EMB'),('Ashfall','EMB'),('Choir','STM'),('Storm','STM'),('Spark','STM'),('Static','STM'),
      ('Quiet','HOL'),('Hollow','HOL'),('Frost','FRS'),('Rime','FRS'),('Glacier','FRS'),('Chill','FRS'),('Avalanche','FRS'),
      ('Bloom','BLM'),('Seed','BLM'),('Spore','BLM'),('Briar','BLM'),('Root','BLM'),('Thorn','BLM'),('Starmetal','IRN'),('Iron','IRN')]
def elem_of(n):
    for k,e in KW:
        if k in n: return e
    return ''
GV = {'S':6,'A':5,'B':4,'C':3,'D':2,'E':1,'-':0}; VG = {v:k for k,v in GV.items()}
def bump(g,d): return VG[max(1,min(6,GV[g]+d))]
MEL_RAR = ['COM']*3+['FRG']*3+['RAR']*3+['REL']*3
REGIDS = [r[0] for r in REG]
melee=[]; mel_attacks=[]
BASEVAL = {'COM':300,'FRG':600,'RAR':1200,'REL':2400,'SHB':6000}
for c in MC:
    code,cname,skill,dty,ar,wmin,wmax,lb,hb,pl,ph,reach,crit,su,grades,_ = c
    for i,n in enumerate(MN[code].split('|')):
        rar = MEL_RAR[i]; reg = REGIDS[i//2]; tier=i//2
        e = elem_of(n); var = 1 + R.uniform(-0.04,0.04)
        tot = round(ar*var)
        phys = tot if not e else round(tot*0.65); el = tot-phys if e else 0
        gm,gf,gl,gg = [bump(g, 1 if (rar=='REL' and g in 'BC') else 0) for g in grades]
        if e: gl = 'C' if e!='IRN' else gl; gg = 'C' if e=='IRN' else gg
        wt = round(wmin+(wmax-wmin)*(i/11)*R.uniform(0.85,1.0),1)
        reqs = {'M':0,'F':0,'L':0,'G':0}
        for a,g in zip('MFLG',(gm,gf,gl,gg)):
            if GV[g]>=3: reqs[a] = 8+3*tier+GV[g]*2
            elif GV[g]==2: reqs[a] = 6+tier*2
        row = dict(item_id=f'ITM_WPN_{code}_{i+1:02d}',name=n,weapon_class=cname,skill=skill,rarity=RARNAME[rar],
            first_region=reg,phys_type=dty,phys_ar=phys,element=ELEM[e][0] if e else '',element_ar=el,
            status=ELEM[e][1] if e else '',status_value=round(el*0.5) if e else 0,
            grade_might=gm,grade_finesse=gf,grade_lore=gl,grade_grit=gg,req_might=reqs['M'],req_finesse=reqs['F'],req_lore=reqs['L'],req_grit=reqs['G'],
            weight=wt,breath_light=lb,breath_heavy=hb,poise_light=pl,poise_heavy=ph,reach_m=reach,crit_mult=crit,
            block_absorb_phys=100 if code=='SHD' else (60 if code in('GRS','HMR','AXE','GAX','GHM') else 45),
            block_absorb_weave=round(55+tier*5) if code=='SHD' else 30,
            stability=round(45+35*(i/11)) if code=='SHD' else round(20+wt*2.5),
            perk_pool_col1='ITM_PRK_EDGE_*',perk_pool_col2='ITM_PRK_GRIP_*',perk_pool_col3='ITM_PRK_T1_* (melee+any)',perk_pool_col4='ITM_PRK_T2_* (melee+any)',
            perk_columns=dict((r[0],r[3]) for r in RAR)[rar],default_art='ITM_ART_'+code,
            max_upgrade=20,base_value=round(BASEVAL[rar]*(1+0.25*tier),-1),
            buy_price=round(BASEVAL[rar]*(1+0.25*tier)*PRICEMULT[rar],-1),sell_price=int(round(BASEVAL[rar]*(1+0.25*tier)*PRICEMULT[rar],-1)*0.12),
            icon='UI_ICON_'+f'WPN_{code}_{i+1:02d}',mesh=f'MESH_WPN_{code}_{i+1:02d}')
        melee.append(row)
    # frame data per class (60 fps)
    for (atk,mv,bm,pm,s_add,act,rec) in [('Light 1',1.00,1.0,1.0,0,4,18),('Light 2',1.05,1.0,1.0,1,4,18),('Light 3',1.20,1.0,1.2,3,5,22),
        ('Heavy',1.55,1.0,1.0,8,5,26),('Charged Heavy',2.10,1.15,1.6,22,6,30),('Running Attack',1.30,1.1,1.2,4,5,24),
        ('Jump Attack',1.45,1.0,1.4,6,5,26),('Guard Counter',1.70,1.0,1.5,5,5,22)]:
        heavy = 'Heavy' in atk or atk in ('Jump Attack','Guard Counter')
        mel_attacks.append(dict(attack_id=f'ITM_ATK_{code}_{atk.upper().replace(" ","_")}',weapon_class=cname,attack=atk,motion_value=mv,
            startup_frames=su+s_add,commit_frame=6,active_frames=act,recovery_frames=rec+(su//3),
            breath=round((hb if heavy else lb)*bm),poise_damage=round((ph if heavy else pl)*pm),
            hitbox='UI_none; collision capsule per mesh',notes='60 fps frames; can cancel into roll after recovery-8'))
mcols=list(melee[0].keys())
w('melee_frame_data.csv',mel_attacks,list(mel_attacks[0].keys()))
w('melee_classes.csv',[dict(class_id='ITM_CLS_'+c[0],name=c[1],skill=c[2],phys_type=c[3],base_ar=c[4],weight_min=c[5],weight_max=c[6],
   breath_light=c[7],breath_heavy=c[8],poise_light=c[9],poise_heavy=c[10],reach_m=c[11],crit_mult=c[12],light_startup_frames=c[13],
   default_grades_MFLG=c[14],primary_attributes=c[15],models=12) for c in MC],
   ['class_id','name','skill','phys_type','base_ar','weight_min','weight_max','breath_light','breath_heavy','poise_light','poise_heavy','reach_m','crit_mult','light_startup_frames','default_grades_MFLG','primary_attributes','models'])

# ---------- firearms ----------
FC = [ # code,name,slot,ammo,impact,pellets,rpm,mag,reserve,reload,f_start,f_end,f_min,ads_ms,zoom,stab,handling,req attr,grade, wmin,wmax
 ('PST','Pistol','Sidearm','Common',49,1,260,12,96,1.6,18,34,0.55,180,1.3,60,80,'Finesse','D',1.2,2.0),
 ('ARF','Auto Rifle','Primary','Common',24,1,600,32,288,2.2,28,50,0.60,260,1.5,50,55,'Finesse','D',3.5,4.5),
 ('SCT','Scout Rifle','Primary','Common',64,1,180,12,108,2.4,45,80,0.65,300,2.5,55,45,'Finesse','C',3.8,4.8),
 ('SMG','Submachine Gun','Primary','Common',17,1,900,40,320,1.9,14,26,0.50,200,1.2,40,75,'Finesse','D',2.5,3.5),
 ('SHG','Shotgun','Primary','Charged',16,9,70,5,30,0.55,6,14,0.25,240,1.2,45,50,'Might','D',4.0,5.5),
 ('SNP','Sniper Rifle','Primary','Charged',260,1,50,4,18,2.8,80,150,0.80,380,6.0,40,35,'Finesse','C',5.5,7.0),
 ('LCH','Launcher','Primary','Heavy',420,1,40,1,6,2.6,0,0,1.0,320,1.5,60,30,'Might','D',8.0,10.0),
 ('LNC','Shard Lance','Primary','Charged',300,1,43,5,20,2.5,40,70,0.70,280,2.0,55,40,'Lore','C',6.0,7.5)]
FN = {
'PST':"Deckhand Sidearm|Rivet Pistol|Lantern Hand-Cannon|Salvager's Snub|Static Arc Pistol|Rime Revolver|Hull Knight Service Pistol|Quiet Hand Whisper|Thorn Seed-Pistol|Starmetal Magnum",
'ARF':"Colony Defense Rifle|Salvage Auto|Ember-Feed Rifle|Hull Knight Battle Rifle|Storm Coil Rifle|Choir Rime Rifle|Remnant Repeater|Hollow Lung Rifle|Bloomtooth Auto|Starmetal Assault Rifle",
'SCT':"Survey Rifle|Ranger Longgun|Lantern Ember Scout|Hull Marksman|Storm Theodolite|Frostline Scout|Salvager's Pick|Quiet Sight|Briarwood Rifle|Iron Witness",
'SMG':"Rattle SMG|Pod-Bay Sprayer|Ember Hornet|Courier SMG|Spark Swarm|Chill Needle|Remnant Wasp|Hollow Hum|Seedstorm SMG|Iron Hive",
'SHG':"Breaching Scattergun|Deck Sweeper|Cinder Mouth|Hull Knight Lockbreaker|Static Burst|Frost Lung|Salvager's Double|Hollow Choke|Briar Blaster|Iron Doorkicker",
'SNP':"Orbit Longbore|Hull Watcher|Cinder Eye|Ranger's Patience|Stormcaller Sniper|Glacier Line|Salvager's Long Shot|Hollow Gaze|Rootbound Rifle|Iron Verdict",
'LCH':"Mooring Launcher|Salvage Tube|Ember Mortar|Hull Breaker|Storm Coil Launcher|Avalanche Tube|Grenade Hopper|Hollow Well|Spore Cannon|Iron Rain",
'LNC':"Shard Lance Prototype|Salvaged Railspike|Ember Lance|Hull Rail Lance|Storm Lance|Frost Lance|Rail of the Meridian|Hollow Lance|Bloom Lance|Iron Lance"}
FRAR = ['COM','COM','FRG','FRG','FRG','RAR','RAR','RAR','REL','REL']; FREG=[0,0,1,1,2,2,3,4,5,5]
guns=[]
for c in FC:
    code,cn,slot,ammo,imp,pel,rpm,mag,res,rl,fs,fe,fm,ads,zm,stb,hnd,ra,rg,wmin,wmax=c
    for i,n in enumerate(FN[code].split('|')):
        rar=FRAR[i]; tier=FREG[i]; e=elem_of(n)
        if code=='LNC' and not e: e=''
        v=1+R.uniform(-0.05,0.05); rpm_v=round(rpm*R.choice([0.9,1.0,1.0,1.1])); imp_v=round(imp*v*(rpm/rpm_v),1)
        guns.append(dict(item_id=f'ITM_WPN_{code}_{i+1:02d}',name=n,weapon_class=cn,slot=slot,ammo_type=ammo,rarity=RARNAME[rar],first_region=REGIDS[tier],
            damage_type=ELEM[e][0] if e else 'Kinetic',status=ELEM[e][1] if e else '',status_value=round(imp_v*pel*0.4) if e else 0,
            impact=imp_v,pellets=pel,rpm=rpm_v,body_dps_plus0=round(imp_v*pel*rpm_v/60),precision_mult=2.0,
            mag=mag+(2 if i%3==1 and mag>4 else 0),reserve=res,reload_s=round(rl*R.uniform(0.92,1.08),2),
            falloff_start_m=fs,falloff_end_m=fe,falloff_min=fm,blast_radius_m=4.0 if code=='LCH' else 0,
            charge_s=0.6 if code=='LNC' else 0,pierce_targets=3 if code=='LNC' else (1 if code=='SNP' else 0),
            ads_ms=ads,zoom=zm,stability=stb+R.randint(-6,6),handling=hnd+R.randint(-6,6),
            scaling_attr='Lore' if e else ra,scaling_grade=rg if not e else 'C',req_attr='Lore' if e else ra,req_value=8+tier*4,
            weight=round(wmin+(wmax-wmin)*R.random(),1),perk_pool_col1='ITM_PRK_BRL_* or ITM_PRK_SCP_*',perk_pool_col2='ITM_PRK_MAG_* or ITM_PRK_FGR_*',
            perk_pool_col3='ITM_PRK_T1_* (firearm+any)',perk_pool_col4='ITM_PRK_T2_* (firearm+any)',perk_columns=dict((r[0],r[3]) for r in RAR)[rar],
            max_upgrade=20,base_value=round(BASEVAL[rar]*(1+0.25*tier),-1),buy_price=round(BASEVAL[rar]*(1+0.25*tier)*PRICEMULT[rar],-1),
            sell_price=int(round(BASEVAL[rar]*(1+0.25*tier)*PRICEMULT[rar],-1)*0.12),icon=f'UI_ICON_WPN_{code}_{i+1:02d}',mesh=f'MESH_WPN_{code}_{i+1:02d}'))
w('weapons_firearm.csv',guns,list(guns[0].keys()))
w('firearm_classes.csv',[dict(class_id='ITM_CLS_'+c[0],name=c[1],slot=c[2],ammo_type=c[3],impact=c[4],pellets=c[5],rpm=c[6],mag=c[7],reserve=c[8],
   reload_s=c[9],falloff_start_m=c[10],falloff_end_m=c[11],falloff_min=c[12],ads_ms=c[13],zoom=c[14],stability=c[15],handling=c[16],
   scaling_attr=c[17],scaling_grade=c[18],weight_min=c[19],weight_max=c[20],skill='Firearms',models=10) for c in FC],
   ['class_id','name','slot','ammo_type','impact','pellets','rpm','mag','reserve','reload_s','falloff_start_m','falloff_end_m','falloff_min','ads_ms','zoom','stability','handling','scaling_attr','scaling_grade','weight_min','weight_max','skill','models'])
w('ammo.csv',[
 dict(item_id='ITM_AMO_COM',name='Common Rounds',used_by='Pistol, Auto Rifle, Scout Rifle, SMG',pickup_qty='Pistol 12 | Auto Rifle 32 | Scout 12 | SMG 40',source='Enemy drops 45% per kill (fodder 35%, heavy 80%); ammo crates',hud_color='#E6E2D8',craft='ITM_RCP_TNK_AMMO_COM'),
 dict(item_id='ITM_AMO_CHG',name='Charged Cells',used_by='Shotgun, Sniper Rifle, Shard Lance',pickup_qty='Shotgun 4 | Sniper 3 | Lance 5',source='Shard crates (100%), elites 25%',hud_color='#5FD3E8',craft='ITM_RCP_TNK_AMMO_CHG'),
 dict(item_id='ITM_AMO_HVY',name='Heavy Munitions',used_by='Launcher, arena power weapons',pickup_qty='Launcher 2',source='Heavy enemies 10%, bosses 100% on phase change, rare crates',hud_color='#B66CE0',craft='ITM_RCP_TNK_AMMO_HVY')],
 ['item_id','name','used_by','pickup_qty','source','hud_color','craft'])

# ---------- perks ----------
def P(prefix,col,app,lst):
    return [dict(perk_id=f'ITM_PRK_{prefix}_{i+1:02d}',column=col,applies_to=app if isinstance(app,str) else '',name=n,effect=e,
                 max_crafted_value='within 15% cap' if '%' in e else '') for i,(n,e) in enumerate(lst)]
EDGE=[('Honed Edge','+6% physical AR'),('Serrated Edge','+10% stance damage'),('Weighted Edge','+12% poise damage; +1 Breath per swing'),
 ('Keen Edge','+15% critical damage'),('Balanced Edge','-2 Breath on light attacks'),('Weave-Etched Edge','+8% element AR'),('Long Edge','+0.2 m reach'),
 ('Tempered Edge','+4% AR; +5 guard stability'),('Fluted Edge','-10% weight; -3% AR'),('Brutal Edge','+10% heavy attack damage'),
 ('Quick Edge','+6% attack speed'),('Hooked Edge','+20% guard counter damage'),('Runed Edge','+12% status buildup'),('Riveted Edge','+8% guard break damage'),('Needle Tip','+10% thrust damage')]
GRIP=[('Wrapped Grip','+5 guard stability'),('Long Grip','+0.1 m reach; +3% heavy damage'),('Counterweight Pommel','-8% recovery frames on heavies'),
 ('Iron Pommel','+10% poise damage on guard counters'),('Leather Grip','-1 Breath on all attacks'),('Shard-Set Pommel','+5% Surge charge from melee hits'),
 ('Cord Wrap','+10% running attack damage'),('Steel Crossguard','+8% block absorption (Weave)'),('Light Hilt','-15% weight'),('Basket Hilt','+10% block absorption (physical) on non-shields'),
 ('Ridged Grip','+4% critical chance window (+2 frames parry)'),('Weighted Grip','+6% jump attack damage'),('Bone Grip','+8% damage while Ward is down'),
 ('Anchor Grip','+15% resist to being disarmed/flinched'),('Choir-Wire Grip','+6% element AR; -4% physical AR')]
BRL=[('Smallbore','+7 range; +7 stability'),('Full Bore','+10 range; +10 stability; -10 handling'),('Fluted Barrel','+15 handling; +5 stability'),
 ('Hammer-Forged Rifling','+10 range'),('Corkscrew Rifling','+5 range; +5 stability; +5 handling'),('Arrowhead Brake','+10 recoil direction; +10 handling'),
 ('Chambered Compensator','+10 stability; -5 handling'),('Polygonal Rifling','+10 stability'),('Extended Barrel','+15 range; -10 handling'),
 ('Ported Barrel','+5% hip-fire accuracy; +5 stability'),('Weave-Coiled Barrel','+6% Weave damage'),('Choke','+20% pellet tightness (shotguns)'),
 ('Rangefinder Barrel','+10% zoom range bonus'),('Suppressor','-50% radar ping; -5 range'),('Hull-Plate Shroud','+10% damage to Ward')]
SCP=[('Iron Sights','zoom x1.0; +10 handling'),('Red Dot','zoom x1.3'),('Holo Sight','zoom x1.4; +5 aim assist'),('Rangefinder Scope','zoom x2.0; +10% falloff distance'),
 ('Hunter Scope','zoom x3.0; +5 stability'),('Long Glass','zoom x4.5'),('Weave Optic','highlights Ward tint at 40 m'),('Thermal Scope','see through smoke; zoom x2.0'),
 ('Flip-Up Sight','toggle x1.3/x2.5 zoom'),('Ostra Overlay','marks precision zones; zoom x1.8'),('Low Profile Sight','zoom x1.2; ADS 10% faster'),('Prism Sight','zoom x1.6; +5 range'),
 ('Survey Lens','zoom x2.5; reveals enemy level'),('Glare-Free Lens','no scope glint; zoom x3.0'),('Choir Lens','+5% precision damage; zoom x2.2')]
MAG=[('Extended Mag','+30% magazine size; -10 reload'),('Tactical Mag','+10% magazine; +10 reload; +5 stability'),('Flared Magwell','+15 reload; +5 stability'),
 ('Alloy Magazine','+20% reload speed when empty'),('Light Mag','+10 range; +10 reload'),('Ricochet Rounds','+10 range; +5 stability; ricochet once'),
 ('High-Caliber Rounds','+5 range; extra flinch to targets'),('Armor-Piercing Rounds','+10% damage to shield-bearers; +5 range'),('Accurized Rounds','+10 range'),
 ('Appended Mag','+20% magazine size'),('Shard-Charged Cells','+8% Weave damage; -10% magazine'),('Spring-Loaded Mag','+25 reload'),
 ('Drum Mag','+60% magazine; -20 reload; -10 handling'),('Steady Rounds','+15 stability; -5 range'),('Hollow-Point Rounds','+8% damage vs flesh; -8% vs Ward')]
FGR=[('Textured Grip','+10 handling; +5 stability'),('Vertical Grip','+15 stability'),('Angled Grip','+15 handling'),('Pistol Brace','+10 stability; +10% hip-fire accuracy'),
 ('Quickdraw Grip','+40 swap handling'),('Stock Pad','+10 stability; -5 handling'),('Sling Mount','+10% move speed while ADS'),('Rubber Wrap','-15% recoil kick'),
 ('Counterbalance Stock','recoil centered; -5 handling'),('Skeleton Stock','-20% weight; +5 handling'),('Bipod','+30 stability while crouched'),('Bulkhead Stock','+20 stability; -15 handling'),
 ('Ergonomic Grip','+5 handling; +5 reload'),('Weave Grip','+5% ability recharge on kills'),('Salvager Wrap','+10% ammo pickup')]
T1=[('Steady Hands','F','+20 handling for 4 s after a kill'),('Ward Breaker','A','+25% damage to Ward'),('Flesh Render','A','+15% damage to targets whose Ward is down'),
 ('Rampage','A','kills grant +10% damage for 3.5 s; stacks 3'),('Kill Clip','F','reload within 3 s of a kill: +25% damage for 5 s'),('Riposte Rhythm','M','guard counter within 1 s of a block: +30% damage'),
 ('Momentum','M','running attacks +20% damage and +15 poise'),('Breathless Fury','M','+12% damage while Breath under 25%'),('Surge Feeder','A','kills grant +3% Surge charge'),
 ('Elemental Echo','A','+20% status buildup'),('Opening Shot','F','first shot from a full magazine: +25 range, +20 accuracy'),('Headhunter','F','+15% precision damage once Ward is down'),
 ('Perpetual Motion','F','moving for 2 s: +20 stability, +20 reload'),("Executioner's Edge",'M','+20% critical strike damage'),('Stance Crusher','M','+20% poise damage vs targets above 50% stance'),
 ('Quickdraw','F','+60 handling; weapon swap 40% faster'),('Overflow','F','ammo pickup refills magazine to 150%'),('Shard Siphon','M','each hit restores 1 Breath'),
 ('Wardsteal','A','kills restore 15% of your Ward'),("Anchor's Patience",'A','+15% damage while Health is full'),('Last Stand','A','+20% damage while Health under 30%'),
 ('Feather Step','M','a roll within 1 s after an attack costs 5 less Breath'),('Cleave','M','heavy attacks hit 1 extra target in a +0.5 m arc'),('Pulse Rounds','F','every 4th shot deals +35% damage'),
 ('Shatter Point','A','+30% damage to Frozen or Rooted targets'),('Hip-Fire Grip','F','+30% hip-fire accuracy; +15% hip-fire precision'),('Rhythm Blade','M','alternating light and heavy: +8% damage, stacks 3'),
 ('Iron Will','M','no flinch during charged heavy'),('Snapshot Sights','F','aim down sights 30% faster'),('Shard Feed','F','precision kills refund 2 rounds to the magazine')]
T2=[('Firefly','F','precision kills explode for 120% of impact in 3 m (Ember)'),('Vorpal Edge','A','+10% damage to bosses and elites'),('Chain Reaction','A','kills cause a 2.5 m blast of the weapon element at 80% AR'),
 ('Echo Strike','M','every 5th hit repeats at 50% damage'),('Reconstruction','F','refills 10% of magazine per second after 2 s idle, up to 200%'),('Frenzy','F','after 10 s in combat: +15% damage, +50 reload'),
 ('Kindled Fury','A','kills grant +15% damage for 6 s'),('Thunder Lash','A','every 3rd consecutive hit chains Shock to 2 targets at 40%'),('Grave Wind','M','heavy attacks send a 6 m wave at 60% AR'),
 ('Bulwark','M','blocking costs 25% less Breath'),('Second Wind','A','kills restore 20 Breath'),('Overwatch','F','+20% damage to targets beyond 40 m'),('Close Quarters','F','+20% damage within 6 m'),
 ('Perfect Guard','M','perfect guards refund their Breath cost; next hit +25%'),('Sundering','M','hits lower target physical absorption by 10% for 5 s'),('Repulsor','M','guard counters knock back 4 m'),
 ('Demolitionist','A','kills grant 10% Cast cooldown'),('Volatile Rounds','F','+30% status buildup from element hits'),('Harmony','A','damage with this weapon gives your other weapon +20% for 4 s'),
 ('Trench Barrel','F','after a melee hit the next 3 hip-fire shots deal +50%'),("Hunter's Mark",'F','precision hits mark the target 6 s; allies deal +10% to it'),('Unbroken','A','+12% damage while Ward is full'),
 ('Tempest Edge','M','charged heavy releases a 4 m Storm burst at 70% AR'),('Frostbite','A','Slow from your hits lasts 20% longer'),('Ricochet','F','rounds bounce to 1 target within 8 m at 50%'),
 ('Heavy Impact','A','+30% stagger vs shield-bearers'),('Wellspring','A','kills drop an orb giving allies 10% ability charge'),('Swashbuckler','M','kills during a light chain: +6% damage, stacks 5'),
 ('Rapid Hit','F','precision hits +10 reload, stacks 5'),('Counter Charge','M','after blocking 3 hits the next heavy deals x1.5')]
APP={'F':'firearm','M':'melee','A':'any'}
perks = P('EDGE',1,'melee',EDGE)+P('GRIP',2,'melee',GRIP)+P('BRL',1,'firearm',BRL)+P('SCP',1,'firearm',SCP)+P('MAG',2,'firearm',MAG)+P('FGR',2,'firearm',FGR)
for pre,col,lst in (('T1',3,T1),('T2',4,T2)):
    for i,(n,a,e) in enumerate(lst):
        perks.append(dict(perk_id=f'ITM_PRK_{pre}_{i+1:02d}',column=col,applies_to=APP[a],name=n,effect=e,max_crafted_value=''))
for p in perks:
    p['attachment_mesh'] = 'MESH_ATT_'+p['perk_id'][8:] if p['perk_id'][8:11] in ('BRL','SCP','MAG','FGR') else ''
    p['icon']='UI_ICON_'+p['perk_id']
w('weapon_perks.csv',perks,['perk_id','column','applies_to','name','effect','max_crafted_value','attachment_mesh','icon'])

# ---------- weapon arts (40) ----------
ARTS=[('Bulwark Stance','SHD',0,0,0.0,30,'','Raise shield; +40 stability 4 s'),('Shield Bash','SHD',18,4,1.2,45,'','Shove 3 m'),
 ('Lion Charge','STS|GRS',22,6,1.9,40,'','Lunge 6 m'),('Crescent Sweep','CRV|TWB',20,5,1.6,25,'','360 degree slash 3 m'),
 ('Stormstep','CRV|DGR|STS',16,8,1.4,15,'STM','Blink 4 m then slash'),('Ember Brand','STS|GRS|AXE|HMR',24,12,1.8,30,'EMB','Ignite blade +25% Ember AR 20 s'),
 ('Frost Lash','STS|CRV|POL|TWB',22,10,1.7,25,'FRS','Ground wave 8 m'),('Hollow Grasp','DGR|FST',18,10,1.5,20,'HOL','Pull a target 5 m'),
 ('Thorn Whirl','POL|TWB',26,8,2.2,35,'BLM','Spinning roots 4 m'),('Iron Bulwark','SHD|HMR',20,14,0.0,0,'IRN','-30% damage taken 6 s'),
 ('Earthbreaker','HMR|GRS|AXE',30,10,2.6,70,'','Ground slam 4 m'),('Overhead Cleave','AXE|GRS',24,6,2.3,60,'','Jumping chop'),
 ('Impale','POL|DGR',20,6,2.0,35,'','Thrust that pins smaller enemies 1.5 s'),('Flurry','DGR|FST|CRV',22,6,0.4,8,'','8 rapid hits'),
 ('Parry','STS|CRV|DGR|SHD',6,0,0.0,0,'','Parry window frames 8-14'),('Riposte Sweep','TWB|POL',18,6,1.5,25,'','Counter-slash on block'),
 ('Quake Fist','FST',20,8,1.7,50,'','Punch shockwave 3 m'),('Pilgrim Step','ANY',10,3,0.0,0,'','Quickstep with i-frames 1-12'),
 ('War Cry','AXE|HMR|GRS',16,30,0.0,0,'','+15% AR 20 s; allies 8 m'),('Rain of Blades','DGR',28,14,0.5,10,'STM','Throws 6 Shard knives'),
 ('Gravity Pull','HMR|POL',24,12,1.0,30,'HOL','Pulls enemies in 6 m'),('Thorn Lance','POL',24,10,1.9,30,'BLM','Thorn spear 12 m'),
 ('Shatter Strike','HMR|AXE',26,10,2.2,55,'IRN','Shatter on hit'),('Cinder Dance','TWB|CRV',28,12,0.6,10,'EMB','5-hit spinning fire'),
 ('Glacial Guard','SHD',18,14,0.0,0,'FRS','Block freezes attacker 1 s'),('Arc Counter','STS|CRV',16,8,1.8,30,'STM','Guard counter adds Shock'),
 ('Hullsplitter','GRS',34,12,3.0,80,'','Charged overhead with hyperarmor'),('Phantom Slash','STS|DGR',22,10,1.6,20,'HOL','Teleport behind locked target 5 m'),
 ('Lantern Blessing','ANY',20,45,0.0,0,'EMB','Weapon +10% AR, allies too, 30 s'),('Rootbind','FST|POL',20,12,1.0,15,'BLM','Root target 2.5 s'),
 ('Tempest Spin','TWB',30,10,0.5,15,'STM','8-hit vortex 3 m'),('Plate Rain','GRS|HMR',32,20,1.6,40,'IRN','3 falling plates 4 m'),
 ('Rending Thrust','POL|STS',20,6,2.1,30,'','Breaks guard'),('Ward Rend','ANY',18,15,1.0,10,'','+100% damage to Ward 1 hit'),
 ('Ashen Step','DGR|CRV',14,5,1.0,10,'EMB','Backstep leaves fire 3 s'),('Choir Note','ANY',22,20,0.0,0,'STM','Stuns fodder within 5 m 2 s'),
 ('Hollow Bite','DGR|FST|CRV',18,8,1.6,20,'HOL','Drain status +60'),('Anvil Drop','HMR',28,9,2.8,75,'','Jump slam'),
 ('Skewer Volley','POL',26,12,0.8,15,'','3 thrown spears 15 m'),('Second Edge','ANY',12,6,1.0,15,'','Next attack within 2 s ignores block')]
arts=[]
for i,(n,cl,br,cd,mv,po,el,d) in enumerate(ARTS):
    arts.append(dict(item_id=f'ITM_ART_{i+1:02d}',name=n,compatible_classes=cl,breath_cost=br,cooldown_s=cd,motion_value=mv,poise_damage=po,
        element=ELEM[el][0] if el else '',description=d,rarity='Rare' if i<20 else 'Relic',first_region=REGIDS[min(5,i//7)],
        buy_price=1500 if i<20 else 4500,sell_price=375 if i<20 else 1125,anim='ANIM_ART_%02d'%(i+1),vfx='VFX_ART_%02d'%(i+1),sfx='SFX_ART_%02d'%(i+1),icon='UI_ICON_ART_%02d'%(i+1)))
# class default arts map to first art matching
for c in MC: arts_def={'STS':'ITM_ART_03','CRV':'ITM_ART_04','GRS':'ITM_ART_27','AXE':'ITM_ART_12','HMR':'ITM_ART_11','POL':'ITM_ART_13','FST':'ITM_ART_17','DGR':'ITM_ART_14','SHD':'ITM_ART_01','TWB':'ITM_ART_31','GAX':'ITM_ART_12','GHM':'ITM_ART_11'}
for m in melee: m['default_art']=arts_def[m['item_id'][8:11]]
w('weapons_melee.csv',melee,mcols)
w('weapon_arts.csv',arts,list(arts[0].keys()))

INF=[('PLN','Plain','',None,'none',''),('HVY','Heavy','',None,'Might +1 grade; Finesse/Lore/Grit to E; AR -5%','ITM_MAT_SPC_INF_HVY'),
 ('KEN','Keen','',None,'Finesse +1 grade; Might/Lore/Grit to E; AR -5%','ITM_MAT_SPC_INF_KEN')]+[
 (k,ELEM[k][0],k,0.4,f'40% of physical base becomes {ELEM[k][0]}; element scales with {"Grit" if k=="IRN" else "Lore"} at weapon top grade -1; firearms: all damage becomes {ELEM[k][0]}','ITM_MAT_INF_'+k) for k in ELEM]+[
 ('KIN','Kinetic (firearms)','',None,'Firearm returns to Kinetic; scaling Finesse at class grade','ITM_MAT_SPC_INF_KIN')]
w('infusions.csv',[dict(infusion_id='ITM_INF_'+a,name=b,element=ELEM[c][0] if c else '',conversion=d or 0,rule=e,material=f,material_qty=1 if f else 0,ember_cost=0 if a=='PLN' else 2000,station='Smithing bench (Lantern Hold, any lit Anchor forge)') for a,b,c,d,e,f in INF],
  ['infusion_id','name','element','conversion','rule','material','material_qty','ember_cost','station'])

# ---------- Shardborn (40: 20 weapons, 20 armor) ----------
SBW=[("Ostra's Last Light",'STS','EMB','Memory of Fire','3 hits within 6 s ignite the blade: +40% Ember AR for 10 s; charged heavy fires a 12 m arc at 150% AR'),
 ("The Meridian's Keel",'GRS','IRN','Keelbreaker','heavy attacks deal full damage through blocks and shields'),
 ("Choir's Unanswered Hymn",'CRV','STM','Unanswered','critical hits chain Shock to 3 enemies within 6 m at 60% AR'),
 ('Quietus','DGR','HOL','Last Breath','backstabs and ripostes kill non-boss enemies under 35% Health'),
 ('Anchorline','POL','IRN','Tether','Weapon Art pulls the target 8 m to you and staggers it'),
 ("Thornmother's Embrace",'FST','BLM','Overgrowth','every 10th hit roots all enemies within 4 m for 2 s'),
 ('The Hatch','SHD','','Sealed','perfect blocks reflect 100% of projectile damage to the shooter'),
 ('Twin Suns of Lantern Hold','TWB','EMB','Corona','while attacking, an Ember aura deals 15 x up_mult damage per second in 2.5 m'),
 ('Gravewell','HMR','HOL','Event Horizon','charged heavy creates a 5 m gravity well for 3 s'),
 ('Rimeheart','AXE','FRS','Deep Winter','striking a Frozen target Shatters it for +100% stance damage (instead of +50%)'),
 ('Last Word of Captain Ires','PST','','Fan the Hammer','hip-fire empties 6 shots in 0.6 s; precision x2 applies even with Ward up'),
 ('Reactor Breath','ARF','EMB','Chain Reactor','kills refill 40% of the magazine; 5 kills without reloading: +20% damage 8 s'),
 ('The Long Silence','SNP','HOL','Unseen','precision kills make you invisible for 3 s'),
 ('Stormcrown','LNC','STM','Crowned','beam chains to 4 enemies; no charge time while Surge is active'),
 ('Mourning Bell','SHG','FRS','Toll','each kill freezes enemies within 4 m for 1.5 s'),
 ('Seedfall','LCH','BLM','Scatter Bloom','projectiles split into 6 bomblets that root for 2 s'),
 ('Hive of the Remnant','SMG','STM','Swarm','hits spawn tracking drones (max 4) dealing 20 x up_mult per second for 5 s'),
 ('Witness of the Fall','SCT','IRN','Overpenetration','rounds pierce all targets and up to 1 m of cover'),
 ("Ostra's Lens",'CAT','','Recall','for 4 s after Surge ends, Rites and Cast have no cooldown'),
 ('Penitent Censer','CAT','EMB','Absolution','Rites cast within 2 s of a perfect dodge cost no cooldown')]
SBA=[('Crown of the Hollow King','Head','kills reduce Resonance cooldown by 2 s'),('Cryo-Visor of the First Waking','Head','enemy attack telegraphs glow 0.25 s earlier'),
 ("Ostra's Halo",'Head','Ward recharge delay 4.5 s becomes 3.0 s'),('Mask of the Quiet Hand','Head','invisible on enemy radar; first hit from stealth +50%'),('Lantern Mitre','Head','Cast recharges 30% faster for 6 s after a kill'),
 ('Bulkhead Aegis','Chest','the first hit after Ward breaks deals 60% less (once per 20 s)'),('Weavecoat of the Choir','Chest','Surge lasts 3 s longer'),
 ("Thornmother's Bark",'Chest','being hit roots the attacker for 1.5 s (8 s cooldown)'),('Starmetal Carapace','Chest','no flinch while Breath is above 50%'),('Shroud of Embers','Chest','rolls leave a 3 s fire trail dealing 30 x up_mult per second'),
 ('Gauntlets of the Lost Pilot','Arms','reload 40% faster; a perfect dodge reloads both weapons'),('Ironbound Vambraces','Arms','guard counters +50% damage'),
 ('Stormgrip Bracers','Arms','sprinting 3 s fully charges Strike'),("Hullwitch's Manacles",'Arms','Rite status buildup +50%'),("Reaper's Wraps",'Arms','critical strikes restore 30 Breath'),
 ('Greaves of the Long Fall','Legs','no fall damage; plunging attacks +60%'),('Wake Treads','Legs','sprinting costs no Breath out of combat and 50% less in combat'),
 ('Choirwalker Boots','Legs','Step ability holds 2 charges'),('Tassets of the Hoard','Legs','+50% material drops; -10% Ward'),('Anchor-Bound Legwraps','Legs','Ember-ghost loss on a second death is 25% instead of 50%')]
CLSN={c[0]:c[1] for c in MC}; CLSN.update({c[0]:c[1] for c in FC}); CLSN['CAT']='Catalyst'
# Plan 3.6/4.3: 30 Shardborn (15 weapons, 15 armor). Keep one weapon per class first, then fill; drop the 5th of each armor slot group.
_seen=set(); _keep=[]
for t in SBW:
    if t[1] not in _seen: _seen.add(t[1]); _keep.append(t)
SBW=_keep[:15]+[t for t in SBW if t not in _keep][:max(0,15-len(_keep))]
if not any(t[1]=='CAT' for t in SBW): SBW[-1]=next(t for t in _keep if t[1]=='CAT')   # keep one caster Shardborn
SBA=[t for k,t in enumerate(SBA) if k not in (4,9,14,18,19)]
def sbw_src(i): return f'ACT_BOSS_{i+1:02d} first kill' if i<6 else (f'ACT_BOSS_{31+i:02d} first kill (raid, weekly)' if i<10 else f'Exotic quest LOC_Q_SHB_W{i+1:02d}')
def sba_src(i): return f'ACT_BOSS_{i+7:02d} first kill' if i<6 else f'Exotic quest LOC_Q_SHB_A{i+1:02d}'
SHB_BY_BOSS={**{i+1:f'ITM_SHB_W{i+1:02d}' for i in range(6)},**{i+7:f'ITM_SHB_A{i+1:02d}' for i in range(6)},**{31+i:f'ITM_SHB_W{i+1:02d}' for i in range(6,10)}}
sb=[]
for i,(n,cl,e,pn,pe) in enumerate(SBW):
    sb.append(dict(item_id=f'ITM_SHB_W{i+1:02d}',name=n,kind='weapon',slot_or_class=CLSN[cl],element=ELEM[e][0] if e else ('Kinetic' if cl in [c[0] for c in FC] else 'Physical'),
      base_ref=f'ITM_CLS_{cl}' if cl!='CAT' else 'ITM_CAT_*',ar_or_defense_note='class base x1.12 (rarity); upgrade to +20 with Ascendant every 5 levels',
      perk_name=pn,perk_effect=pe,fixed_perks='best-in-class col1+col2 fixed; T1/T2 chosen by design',source=sbw_src(i),
      first_region=REGIDS[i%6],sell_price=1500,icon=f'UI_ICON_SHB_W{i+1:02d}'))
for i,(n,sl,pe) in enumerate(SBA):
    sb.append(dict(item_id=f'ITM_SHB_A{i+1:02d}',name=n,kind='armor',slot_or_class=sl,element='',base_ref='medium weight piece stats x1.12',
      ar_or_defense_note='fixed stats; upgrade to +10 with Ascendant at +5 and +10',perk_name=n.split(' of ')[0],perk_effect=pe,fixed_perks='',
      source=sba_src(i),first_region=REGIDS[i%6],sell_price=1500,icon=f'UI_ICON_SHB_A{i+1:02d}'))
w('shardborn.csv',sb,list(sb[0].keys()))

# ---------- catalysts (20) ----------
CATN=['Salvaged Rod','Hullwitch Staff','Lantern Seal','Kindling Gauntlet','Choir Tuning Fork','Thorn Wand','Ash Censer','Remnant Emitter','Pilgrim Seal','Frostglass Staff',
      'Storm Coil Gauntlet','Hollow Reliquary','Bloomheart Staff','Iron Sigil','Castellan Seal','Archivist Staff','Quiet Lens Gauntlet','Starmetal Staff','Orbit Seal','Shard Conductor']
CK=['Staff','Staff','Seal','Shard Gauntlet','Seal','Staff','Seal','Shard Gauntlet','Seal','Staff','Shard Gauntlet','Seal','Staff','Seal','Seal','Staff','Shard Gauntlet','Staff','Seal','Shard Gauntlet']
cats=[]
for i,n in enumerate(CATN):
    e=elem_of(n); tier=i*6//20; rar=['COM','FRG','FRG','RAR','RAR','REL'][tier]
    cats.append(dict(item_id=f'ITM_CAT_{i+1:02d}',name=n,catalyst_type=CK[i],rarity=RARNAME[rar],first_region=REGIDS[tier],rite_power=100+tier*8+(i%3)*3,
      grade_lore=['C','C','B','B','A','A'][tier] if CK[i]!='Shard Gauntlet' else 'C',grade_grit='D' if CK[i]=='Seal' else 'E',grade_finesse='C' if CK[i]=='Shard Gauntlet' else 'E',
      element_bonus=f'+15% {ELEM[e][0]} Rite damage' if e else '+5% all Rites',cast_speed_mult={'Staff':1.0,'Seal':1.1,'Shard Gauntlet':1.2}[CK[i]],
      melee_ar={'Staff':60,'Seal':30,'Shard Gauntlet':75}[CK[i]],req_lore=10+tier*6,weight={'Staff':4.0,'Seal':1.5,'Shard Gauntlet':2.5}[CK[i]],
      max_upgrade=20,buy_price=round(BASEVAL[rar]*PRICEMULT[rar]*(1+0.25*tier),-1),sell_price=int(round(BASEVAL[rar]*PRICEMULT[rar]*(1+0.25*tier),-1)*0.12),icon=f'UI_ICON_CAT_{i+1:02d}'))
w('catalysts.csv',cats,list(cats[0].keys()))

pw=[('Hullbreaker Cannon','Launcher','Heavy',650,3,90,'5 m blast'),('Choir Lance','Shard Lance','Charged',420,4,120,'chains to 2'),
    ('Arena Greatsword','Greatsword','none',380,0,120,'one-hit kill on unshielded players; 60 s hold limit'),('Reaper SMG','Submachine Gun','Common',22,60,90,'+50% move speed'),
    ('Orbital Spotter','Sniper Rifle','Charged',520,3,150,'marks target for all allies'),('Gravity Hammer','Hammer','none',450,0,150,'5 m knockback slam')]
w('arena_power_weapons.csv',[dict(item_id=f'ITM_PWR_{i+1:02d}',name=a,base_class=b,ammo=c,damage=d,ammo_in_pickup=e,respawn_s=f,special=g,mode='Arena PvP only; normalized, ignores upgrades and perks',spawn_announce='UI_ANNOUNCE_POWER_WEAPON') for i,(a,b,c,d,e,f,g) in enumerate(pw)],
  ['item_id','name','base_class','ammo','damage','ammo_in_pickup','respawn_s','special','mode','spawn_announce'])

# ---------- armor (90 sets x 4 pieces) ----------
SETS=[]
for n,wc in [('Crash-Knight','H'),('Hullwitch','L'),('Scavenger','M'),('Lantern Priest','M'),('Ranger','L'),('Unbound','L')]:
    SETS.append((f'{n} Origin',wc,'Origin starter','REG_01','COM','Starting kit for the '+n+' Origin'))
for fac,ranks,wc in [('Hull Knight',['Squire','Sworn','Banneret','Castellan','Marshal','Paragon'],'H'),('Lantern Church',['Acolyte','Lamplighter','Deacon','Confessor','Bishop','Luminary'],'M'),
    ("Salvagers' Guild",['Picker','Rigger','Fence','Cutter','Broker','Guildmaster'],'L'),('Quiet Hand',['Shade','Whisper','Knife','Veil','Silence','Hand'],'L'),('Choir',['Listener','Cantor','Chorister','Harmonist','Precentor','Voice'],'M')]:
    for t,rk in enumerate(ranks):
        SETS.append((f'{fac} {rk}',wc,'Faction',REGIDS[t],['COM','FRG','FRG','RAR','RAR','REL'][t],f'{fac} questline reward rank {t+1}'))
FOUND=[['Ashfall Scout','Cinder Warden','Reclaimer','Dustwalker'],['Tidewreck','Bulkhead Guard','Mooring Watch','Kelp-Silk'],['Rootwarden','Briar Knight','Mossback','Pollen Mask'],
       ['Stormglass','Antenna Priest','Static Ward','Thunderhide'],['Frostline','Cryo-Keeper','Glacier Plate','Rimewalker'],['Hollowveil','Ember Penitent','Deep Signal','Last Watch']]
for r,names in enumerate(FOUND):
    for j,n in enumerate(names):
        SETS.append((n,'LMHM'[j],'Found',REGIDS[r],['FRG','RAR','RAR','REL'][j],'Site reward'))
for t,mat in enumerate(['Scrap','Riveted','Dustforged','Shardsteel','Choirglass','Starmetal']):
    for wc,wn in [('L','Jack'),('M','Brigandine'),('H','Plate')]:
        SETS.append((f'{mat} {wn}',wc,'Crafted',REGIDS[t],['COM','FRG','FRG','RAR','RAR','REL'][t],'Smithing recipes ITM_RCP_SMT_'+mat.upper()+'_'+wn.upper()+'_<slot>'))
for fac in ['Hollowed','Remnant','Thorn Clan','Choirborn']:
    for j,(rk,wc) in enumerate([('Rag','L'),('Warrior','M'),('Champion','H')]):
        reg={'Hollowed':0,'Remnant':1,'Thorn Clan':2,'Choirborn':6}[fac]+j
        SETS.append((f'{fac} {rk}',wc,'Enemy drop',REGIDS[min(7,reg)],['FRG','RAR','REL'][j],f'Drops from {fac} enemies; see loot_tables.csv'))
assert len(SETS)==90, len(SETS)
WC={'L':('Light',14,18,22),'M':('Medium',28,28,18),'H':('Heavy',46,38,14)}  # full-set weight, phys absorb %, weave resist %
SL=[('Head',0.18,'Helm'),('Chest',0.36,'Cuirass'),('Arms',0.18,'Gauntlets'),('Legs',0.28,'Greaves')]
LWORD={'Light':['Hood','Coat','Wraps','Leggings'],'Medium':['Helm','Armor','Gloves','Trousers'],'Heavy':['Helm','Plate','Gauntlets','Greaves']}
sets_rows=[]; pieces=[]
for si,(n,wc,src,reg,rar,note) in enumerate(SETS):
    wname,wt,pa,wr=WC[wc]; tier=REGIDS.index(reg)
    sid=f'ITM_SET_{si+1:02d}'
    bonus2=bonus4=''
    if src in('Faction','Found','Enemy drop'):
        e=list(ELEM)[si%6]
        bonus2=f'+8% {ELEM[e][0]} resist' if src!='Faction' else '+5% Ward'
        bonus4={'Faction':'+10% damage while in a faction quest zone; +5 Breath','Found':'+6% damage to Ward; +3% Ability Recharge','Enemy drop':f'+10% damage vs {n.rsplit(" ",1)[0]} enemies'}[src]
    sets_rows.append(dict(set_id=sid,name=n,weight_class=wname,source=src,first_region=reg,rarity=RARNAME[rar],bonus_2pc=bonus2,bonus_4pc=bonus4,
        dye_channels=3,note=note,concept='UV-007',ornament='ITM_COS_ORN_'+f'{si+1:02d}' if si<50 else ''))
    for k,(slot,share,_) in enumerate(SL):
        m=RARMULT[rar]*(1+0.03*tier)
        pieces.append(dict(item_id=f'{sid}_{slot.upper()}',name=f'{n} {LWORD[wname][k]}',set_id=sid,slot=slot,weight_class=wname,rarity=RARNAME[rar],first_region=reg,
            weight=round(wt*share*(1+0.02*tier),1),absorb_phys_pct=round(pa*share*m,2),resist_weave_pct=round(wr*share*m,2),
            poise=round({'Light':4,'Medium':10,'Heavy':18}[wname]*share/0.25*m,1),stat_rolls=dict((r[0],r[4]) for r in RAR)[rar],
            max_upgrade=10,base_value=round(BASEVAL[rar]*share*2*(1+0.25*tier),-1),buy_price=round(BASEVAL[rar]*share*2*(1+0.25*tier)*PRICEMULT[rar],-1),
            sell_price=int(round(BASEVAL[rar]*share*2*(1+0.25*tier)*PRICEMULT[rar],-1)*0.12),icon=f'UI_ICON_{sid}_{slot.upper()}',mesh=f'MESH_{sid}_{slot.upper()}'))
w('armor_sets.csv',sets_rows,list(sets_rows[0].keys())); w('armor_pieces.csv',pieces,list(pieces[0].keys()))
rolls=[]
for st,mn,mx,step,unit in [('Health',10,30,1,'flat'),('Ward',10,30,1,'flat'),('Breath',3,8,1,'flat'),('Ability Recharge',2,5,0.5,'%'),('Equip Load',1.0,3.0,0.5,'flat')]:
    for r in RAR[:4]:
        mult={'COM':0,'FRG':1.0,'RAR':1.15,'REL':1.3}[r[0]]
        if mult: rolls.append(dict(stat=st,rarity=r[1],min=round(mn*mult,1),max=round(mx*mult,1),step=step,unit=unit,per='piece at +0; x up_mult_armor(u)'))
w('armor_stat_rolls.csv',rolls,['stat','rarity','min','max','step','unit','per'])

# ---------- cosmetics (120: 70 dyes, 50 ornaments) ----------
DYE=[('Ash Grey','#6E6A64'),('Bone White','#E8E1D0'),('Hull Steel','#7F8A92'),('Rust Red','#8E3B24'),('Ember Orange','#E06A1F'),('Lantern Gold','#D9A63A'),('Moss Green','#55693A'),
 ('Storm Blue','#2E5C8A'),('Frost Cyan','#8FD3E3'),('Hollow Violet','#4B2E63'),('Bloom Pink','#C76B8F'),('Iron Black','#1E1E22'),('Choir Teal','#2F8A84'),('Deep Navy','#1B2740'),
 ('Sand','#C9B48A'),('Clay','#A86A4A'),('Olive','#6B6B2E'),('Wine','#5E1A2B'),('Snow','#F4F6F7'),('Slate','#4A5359'),('Copper','#B0683A'),('Brass','#B59A4E'),('Verdigris','#4F8F7A'),
 ('Charcoal','#333333'),('Crimson','#9E1B2C'),('Saffron','#E3A21A'),('Pine','#244A35'),('Sky','#7FB2E5'),('Lavender','#9A86C2'),('Plum','#6A2C5A'),('Smoke','#8C8C8C'),
 ('Pearl','#E6E3DA'),('Cobalt','#1F4BA5'),('Jade','#2F8F5B'),('Amber','#CC8A1E'),('Cinder','#3F2A22'),('Starlight','#DCE4F2'),('Void','#0D0B14'),('Signal Red','#D12B2B'),('Hazard Yellow','#F2C230')]
# Premium dyes: base hue x finish, computed so every color matches its name (no random hexes).
import colorsys
DYE_BASE={'Silver':'#A8A9AD','Bronze':'#8C6239','Obsidian':'#24212B','Ivory':'#E9E3CF','Cerulean':'#2A7FBA'}
DYE_FIN={'Polished':(1.12,1.10),'Weathered':(0.90,0.65),'Burnished':(0.90,1.15),'Faded':(1.12,0.55),'Gleaming':(1.20,1.05),'Scorched':(0.78,0.80)}  # (lightness, saturation) multipliers
def dye_hex(base,fin):
    r,g,b=(int(DYE_BASE[base][k:k+2],16)/255 for k in (1,3,5)); h,l,s=colorsys.rgb_to_hls(r,g,b); lm,sm=DYE_FIN[fin]
    r,g,b=colorsys.hls_to_rgb(h,min(0.95,l*lm),min(1.0,s*sm)); return '#%02X%02X%02X'%(round(r*255),round(g*255),round(b*255))
DYE += [(f'{a} {b}',dye_hex(b,a)) for a in DYE_FIN for b in DYE_BASE][:30]
def _lab(hx):
    c=[int(hx[k:k+2],16)/255 for k in (1,3,5)]; c=[((v+0.055)/1.055)**2.4 if v>0.04045 else v/12.92 for v in c]
    x=(0.4124*c[0]+0.3576*c[1]+0.1805*c[2])/0.95047; y=0.2126*c[0]+0.7152*c[1]+0.0722*c[2]; z=(0.0193*c[0]+0.1192*c[1]+0.9505*c[2])/1.08883
    f=lambda t: t**(1/3) if t>0.008856 else 7.787*t+16/116
    return 116*f(y)-16, 500*(f(x)-f(y)), 200*(f(y)-f(z))
RESERVED={'Health red':'#D4483F','Ward blue':'#4F8FE6','Breath green':'#7CC46A','Lens cyan':'#8FE3EE','Ember amber':'#E8873A','Signal red':'#FF3B30'}  # Visual Bible gameplay colors
RESERVED_MIN_DE=20
def _de(a,b): return sum((p-q)**2 for p,q in zip(_lab(a),_lab(b)))**0.5
def clear_reserved(hx):
    # Keep the hue (so the name still fits); step lightness and saturation away until every reserved color is at least RESERVED_MIN_DE away
    r,g,b=(int(hx[k:k+2],16)/255 for k in (1,3,5)); h,l,s=colorsys.rgb_to_hls(r,g,b)
    for step in range(40):
        for dl in (-0.03*step, 0.03*step):
            for ds in (0, -0.04*step):
                cand='#%02X%02X%02X'%tuple(round(v*255) for v in colorsys.hls_to_rgb(h,min(0.95,max(0.05,l+dl)),max(0.15,min(1,s+ds))))
                if min(_de(cand,c) for c in RESERVED.values())>=RESERVED_MIN_DE: return cand
    return hx
cos=[]
for i,(n,hx) in enumerate(DYE):
    hx=clear_reserved(hx)
    earn = i<40
    cos.append(dict(item_id=f'ITM_COS_DYE_{i+1:02d}',name=n+' Dye',kind='Dye',color_hex=hx,applies_to='any armor dye channel',
        acquisition='Vendor (Ember)' if earn else 'Cosmetics shop',price_ember=round(500+i*110,-1) if earn else '',price_usd='' if earn else (1.99 if i<60 else 2.99),
        tradeable=0,power=0,icon=f'UI_ICON_DYE_{i+1:02d}'))
for i in range(50):
    s=sets_rows[i]; earn=i<20
    cos.append(dict(item_id=f'ITM_COS_ORN_{i+1:02d}',name=f'{s["name"]} Ornament',kind='Armor ornament',color_hex='',applies_to=s['set_id'],
        acquisition='Raid/arena reward (Seals)' if earn else 'Cosmetics shop',price_ember='',price_usd='' if earn else (4.99 if i<40 else 9.99),
        price_seals=60+i*5 if earn else '',tradeable=0,power=0,icon=f'UI_ICON_ORN_{i+1:02d}'))
# Plan 3.10: the shop sells armor dyes, Strider skins and emotes. No power.
SKINS=['Ashen Hide','Saltmere Dapple','Thornwood Russet','Glass-Scaled','Rimefall Frostcoat','Hollowdeep Pale','Lantern Barding','Hull Knight Caparison','Guild Trader Harness','Quiet Hand Shadow',
 'Choir Hymn Silks','Clan War Paint','Remnant Plating','Starmetal Barding','Ember Mane','Stormstriped','Bloomwoven Saddle','Ironbark Hide','Meridian Livery','Shard-Lit Bones']
for i,n in enumerate(SKINS):
    earn=i<6
    cos.append(dict(item_id=f'ITM_COS_STR_{i+1:02d}',name=n+' Strider Skin',kind='Strider skin',color_hex='',applies_to='ACT_CRT_STRIDER (tamed mount)',
        acquisition='Raid/arena reward (Seals)' if earn else 'Cosmetics shop',price_ember='',price_seals=80+i*10 if earn else '',
        price_usd='' if earn else (4.99 if i<16 else 7.99),tradeable=0,power=0,icon=f'UI_ICON_COS_STR_{i+1:02d}'))
EMOTES=['Salute','Kneel at Anchor','Lantern Raise','Bow','Wave','Point','Sit by Fire','Taunt','Shrug','Victory Fist','Pray','Clap','Dance of Ash','Knight\'s Oath','Guild Haggle',
 'Quiet Hand Vanish','Choir Hum','Clan Roar','Read the Logs','Ostra Glow']
for i,n in enumerate(EMOTES):
    earn=i<10
    cos.append(dict(item_id=f'ITM_COS_EMT_{i+1:02d}',name=n,kind='Emote',color_hex='',applies_to='player',
        acquisition='Unlocked in play (quests, factions, achievements)' if earn else 'Cosmetics shop',price_ember='',price_seals='',
        price_usd='' if earn else (1.99 if i<17 else 2.99),tradeable=0,power=0,icon=f'UI_ICON_COS_EMT_{i+1:02d}',anim=f'ANIM_EMOTE_{i+1:02d}'))
w('cosmetics.csv',cos,['item_id','name','kind','color_hex','applies_to','acquisition','price_ember','price_seals','price_usd','tradeable','power','icon','anim'])

# ---------- currencies ----------
w('currencies.csv',[
 dict(item_id='ITM_CUR_EMBER',name='Ember',use='Character level (cost curve in data/actors), vendors, upgrades, infusions',carry_cap=999999999,on_death='drops as Shard-ghost; second death loses 50%',weekly_cap='',source='kills (ACT_* ember tables), Ember Pouches, selling'),
 dict(item_id='ITM_CUR_SEALS',name='Seals',use='Endgame vendor: ornaments, Shardborn re-rolls, Ascendant Shards',carry_cap=500,on_death='kept',weekly_cap=100,source='strike 10, Hollowed Citadel 15, raid boss 20/27/33/40 by wing (boss drop), arena match win 5 loss 2')],
 ['item_id','name','use','carry_cap','on_death','weekly_cap','source'])

# ---------- consumables (40) ----------
C=[ # id,name,cat,effect,mag,dur,stack,buy,weight,recipe
('TNC_CRIMSON','Crimson Tonic','Tonic','Heal % max Health (F_TONIC)','40%+2.5%/potency',0.8,'4-12 (refill at Anchor)',0,0,''),
('TNC_SEED','Tonic Seed','Key upgrade','+1 max Crimson Tonic (8 in world)','+1',0,8,0,0,''),
('TNC_DISTIL','Tonic Distillation','Key upgrade','+1 Tonic potency (8 in world)','+1',0,8,0,0,''),
('BRW_EMB','Ember Ward Brew','Brew','+20% Ember resist','20%',120,10,180,0.2,'BRW'),('BRW_STM','Storm Ward Brew','Brew','+20% Storm resist','20%',120,10,180,0.2,'BRW'),
('BRW_HOL','Hollow Ward Brew','Brew','+20% Hollow resist','20%',120,10,180,0.2,'BRW'),('BRW_FRS','Frost Ward Brew','Brew','+20% Frost resist','20%',120,10,180,0.2,'BRW'),
('BRW_BLM','Bloom Ward Brew','Brew','+20% Bloom resist','20%',120,10,180,0.2,'BRW'),('BRW_IRN','Iron Ward Brew','Brew','+20% Iron resist','20%',120,10,180,0.2,'BRW'),
('BRW_MIG','Might Draught','Brew','+5 Might','+5',180,5,400,0.2,'BRW'),('BRW_FIN','Finesse Draught','Brew','+5 Finesse','+5',180,5,400,0.2,'BRW'),
('BRW_LOR','Lore Draught','Brew','+5 Lore','+5',180,5,400,0.2,'BRW'),('BRW_GRT','Grit Draught','Brew','+5 Grit','+5',180,5,400,0.2,'BRW'),
('BRW_BRT','Breath Tea','Brew','+15% Breath regen','15%',120,10,250,0.2,'BRW'),('BRW_WRD','Ward Salve','Brew','+15% max Ward','15%',180,10,300,0.2,'BRW'),
('THR_SHARD','Shard Grenade','Throwable','180 Ember damage x up_mult(region band) in 3 m; Burn 60','180',0,10,120,0.3,'TNK'),
('THR_STORM','Storm Pot','Throwable','150 Storm damage 3 m; Shock 70','150',0,10,120,0.3,'TNK'),('THR_FROST','Frost Jar','Throwable','140 Frost damage 3 m; Slow 80','140',0,10,120,0.3,'TNK'),
('THR_HOLLOW','Hollow Bomb','Throwable','150 Hollow damage 3 m; Drain 70','150',0,10,140,0.3,'TNK'),('THR_SEED','Seed Bomb','Throwable','120 Bloom damage 3 m; Root 90','120',0,10,140,0.3,'TNK'),
('THR_SHRAP','Iron Shrapnel','Throwable','200 Iron damage cone 5 m; Shatter 50','200',0,10,160,0.3,'TNK'),('THR_FLASH','Flash Charge','Throwable','Blind enemies in 6 m (they lose target)','',3,5,200,0.3,'TNK'),
('THR_SMOKE','Smoke Canister','Throwable','6 m smoke cloud; blocks sight','',8,5,150,0.4,'TNK'),('THR_KNIFE','Throwing Knives','Throwable','40 Pierce damage x up_mult; 1 per throw','40',0,30,15,0.1,'TNK'),
('THR_DECOY','Decoy Beacon','Throwable','Enemies within 15 m target it; 300 HP','',10,3,300,0.5,'TNK'),
('UTL_ECHO','Echo Lantern','Utility','Summon one NPC Echo (ACT_ECHO_*) for current boss or site','1',0,5,800,0.2,'BRW'),
('UTL_CHALK','Shard-note Chalk','Utility','Write a Shard-note (word list in data/ui)','',0,1,0,0,''),
('UTL_FLARE','Return Flare','Utility','Warp to last lit Anchor after 3 s channel','',0,5,500,0.1,'TNK'),
('UTL_POUCH_S','Small Ember Pouch','Utility','Grants Ember','200',0,99,0,0,''),('UTL_POUCH_M','Ember Pouch','Utility','Grants Ember','1500',0,99,0,0,''),
('UTL_POUCH_L','Heavy Ember Pouch','Utility','Grants Ember','8000',0,99,0,0,''),('UTL_PICK','Salvager Picks','Utility','Lockpick; Infiltration skill sets break chance (data/actors)','',0,50,20,0.05,'TNK'),
('UTL_OIL','Lantern Oil','Utility','Shoulder lantern light','',600,10,60,0.3,'BRW'),
('UTL_AMMO_C','Common Ammo Synth','Utility','Refill 50% of common reserve','50%',0,5,300,0.5,'TNK'),('UTL_AMMO_G','Charged Ammo Synth','Utility','Refill 50% of charged reserve','50%',0,3,600,0.5,'TNK'),
('FOD_RATION','Trail Ration','Food','+5 max Breath','50%',300,20,40,0.3,'BRW'),('FOD_WATER','Water Flask','Food','Breath regen +10%','60%',0,10,20,0.5,'BRW'),
('FOD_STEW','Hearty Stew','Food','+10 max Breath','+5',600,10,120,0.5,'BRW'),('FOD_JERKY','Strider Jerky','Food','+5% Breath regen','5%',300,20,50,0.2,'BRW'),
('FOD_TEA','Dreamless Tea','Food','Hollow (Drain) buildup -15%','50%',0,10,90,0.2,'BRW')]
assert len(C)==40,len(C)
cons=[dict(item_id='ITM_CON_'+a,name=b,category=c,effect=d,magnitude=e,duration_s=f,max_stack=g,buy_price=h,sell_price=h//4,weight=i,
     use_time_s=0.8 if c in('Tonic','Brew','Food') else (0.6 if c=='Throwable' else 1.0),craft_recipe=f'ITM_RCP_{j}_{a}' if j else '',
     icon='UI_ICON_CON_'+a,vfx='VFX_CON_'+a,sfx='SFX_CON_'+a) for a,b,c,d,e,f,g,h,i,j in C]
w('consumables.csv',cons,list(cons[0].keys()))

# ---------- materials (60) ----------
M=[]
for t,(code,nm,rn,rare,rr,val) in enumerate([('HULL','Hull Scrap','Hull Plate','Keel Fragment','Common',8),('DUST','Shard Dust','Shard Ingot','Shard Heart','Uncommon',40),
     ('GLASS','Choir Glass','Tuned Glass','Choir Prism','Rare',200),('STAR','Starmetal','Starmetal Bar','Starmetal Core','Endgame',900)]):
    M+= [(f'{code}_01',nm,'Upgrade',rr,val,999,f'Weapon +{t*5+1}..+{t*5+5}, armor upgrades'),(f'{code}_02',rn,'Upgrade (refined)',rr,val*12,99,f'Refined: 10x {nm}; crafted gear'),
         (f'{code}_03',rare,'Upgrade (rare)',rr,val*40,20,'Crafted Relic sets; Shardborn re-roll')]
M+= [('SPC_ASCENDANT','Ascendant Shard','Special','Mythic',5000,10,'Shardborn upgrade every 5 levels'),('SPC_INF_HVY','Heavy Whetstone','Infusion','Rare',1500,10,'Heavy infusion'),
     ('SPC_INF_KEN','Keen Whetstone','Infusion','Rare',1500,10,'Keen infusion'),('SPC_INF_KIN','Kinetic Breech','Infusion','Rare',1500,10,'Return firearm to Kinetic')]
M+= [(f'INF_{k}',f'{ELEM[k][0]} Core','Infusion','Rare',1500,10,f'{ELEM[k][0]} infusion') for k in ELEM]
M+= [(f'HRB_{i+1:02d}',n,'Brewing reagent','Common',v,99,u) for i,(n,v,u) in enumerate([('Redcap Moss',10,'Tonic-family brews'),('Emberroot',12,'Ember brews, Shard Grenade'),('Stormpetal',12,'Storm brews'),
     ('Hollow Lichen',14,'Hollow brews'),('Frostbell',12,'Frost brews'),('Bloomseed',12,'Bloom brews, Seed Bomb'),('Ironleaf',14,'Iron brews, Grit Draught'),('Lantern Wax',10,'Lantern Oil'),
     ('Clean Water',2,'Brewing base, Water Flask'),('Grain Sack',4,'Ration, Stew'),('Strider Meat',8,'Jerky, Stew'),('Salt',3,'Jerky, Ration'),('Bitterbark',16,'Draughts'),('Dreamweed',18,'Dreamless Tea, Echo Lantern')])]
M+= [(f'PRT_{i+1:02d}',n,'Tinkering part','Common' if i<6 else 'Uncommon',v,99,u) for i,(n,v,u) in enumerate([('Spring Coil',12,'Picks, Decoy'),('Powder Charge',15,'Ammo, grenades'),
     ('Casing Brass',6,'Common ammo'),('Wire Bundle',10,'Storm Pot, Flare'),('Fuse',8,'All throwables'),('Gear Set',14,'Decoy, Ammo Synth'),('Circuit Wafer',40,'Charged ammo, Decoy'),
     ('Lens Glass',30,'Flash Charge, scopes'),('Cell Housing',45,'Charged Cells'),('Explosive Gel',60,'Heavy Munitions, Shrapnel')])]
M+= [(f'MON_{i+1:02d}',n,'Monster part',r,v,99,u) for i,(n,r,v,u) in enumerate([('Hollow Ichor','Common',20,'Hollowed drop; Hollow brews/sets'),('Shard-Sick Tissue','Uncommon',60,'Hollowed elite; Echo Lantern'),
     ('Servo Coil','Common',25,'Remnant drop; Remnant sets'),('Remnant Core','Uncommon',80,'Remnant heavy; Charged Synth'),('Thorn Hide','Common',20,'Thorn Clan drop; Thorn sets'),
     ('Clan Trophy Bone','Uncommon',70,'Thorn Clan leader; Grit Draught'),('Choirborn Echo','Rare',300,'Choirborn drop; Choirborn sets'),('Quiet Fragment','Rare',500,'Quiet bosses; Relic crafting')])]
M+= [(f'ESS_{k}',f'{ELEM[k][0]} Essence','Rite reagent','Uncommon',90,99,f'Rites: {ELEM[k][0]} effects (1 per 10 magnitude)') for k in ELEM]
assert len(M)==60,len(M)
mats=[dict(item_id='ITM_MAT_'+a,name=b,category=c,rarity=d,base_value=e,sell_price=0 if c in('Upgrade','Upgrade (refined)','Upgrade (rare)','Special') else e//4,
      buyable='no' if c.startswith('Upgrade') or c=='Special' else 'yes',buy_price='' if c.startswith('Upgrade') or c=='Special' else e,max_stack=f,weight=0,uses=g,
      icon='UI_ICON_MAT_'+a,pickup_mesh='MESH_PICKUP_MAT_'+a) for a,b,c,d,e,f,g in M]
w('materials.csv',mats,list(mats[0].keys()))

# ---------- lore items (400) ----------
DECKS=['Bridge','Hydroponics','Cryo Bay 3','Reactor Ring','Engineering','Medbay','Cargo Hold','Chapel','Observation Deck','Officers Quarters','Shuttle Bay','Archive Core']
SEND=['a Hull Knight squire','Bishop Arlen','a Salvager fence','an unnamed Quiet Hand','Choir Precentor Vael','a Thorn Clan scout','a cryo technician','Captain Ires','a Lantern acolyte','a Remnant drone log']
RCPT=['their mother','the Guildmaster','a lost lover','the Lantern Synod','the Castellan','a debtor','an apprentice','no one','the Choir','a dead friend']
RELN=['Cracked Shard Pendant','Crew Badge','Rusted Hymnal','Pilot Wings','Cryo Tag','Clan Totem','Glass Bell','Ration Tin','Family Holo','Bent Compass','Knight Signet','Burned Map',
      'Choir Tuning Stone','Child Drawing','Prayer Lamp','Salvage License']
lore=[]; n=0
REGS7=['REG_01','REG_02','REG_03','REG_04','REG_05','REG_06','REG_Q']
for i in range(140):
    n+=1; lore.append(dict(item_id=f'ITM_LOR_{n:03d}',name=f'Meridian Log: {DECKS[i%12]}, Entry {i//12+1:02d}',lore_type='Ship log',region=REGS7[i%7],
        location=f'LOC_SITE_{REGS7[i%7]}_{i%20+1:02d}',text_id=f'TXT_LORE_{n:03d}',unlocks='',weight=0,sell_price=0,icon='UI_ICON_LORE_LOG'))
for i in range(120):
    n+=1; lore.append(dict(item_id=f'ITM_LOR_{n:03d}',name=f'Letter from {SEND[i%10]} to {RCPT[(i*3)%10]} ({i//10+1})',lore_type='Letter',region=REGS7[i%7],
        location=f'LOC_SITE_{REGS7[i%7]}_{(i*7)%20+1:02d}',text_id=f'TXT_LORE_{n:03d}',unlocks='',weight=0,sell_price=0,icon='UI_ICON_LORE_LETTER'))
for i in range(80):
    n+=1; lore.append(dict(item_id=f'ITM_LOR_{n:03d}',name=f'{RELN[i%16]}' + (f' ({i//16+1})' if i>=16 else ''),lore_type='Relic',region=REGS7[i%7],
        location=f'LOC_SITE_{REGS7[i%7]}_{(i*3)%20+1:02d}',text_id=f'TXT_LORE_{n:03d}',unlocks='',weight=0.1,sell_price=0,icon='UI_ICON_LORE_RELIC'))
KEYT=['Citadel Gate','Vault','Cell Block','Reactor Hatch','Chapel Door','Shortcut Lift','Armory','Captain Cabin','Choir Seal','Bulkhead']
for i in range(60):
    n+=1; r=REGS7[i%7]; lore.append(dict(item_id=f'ITM_LOR_{n:03d}',name=f'{KEYT[i%10]} Key ({r[-2:].replace("_","")})' + (f' {i//10+1}' if i>=10 else ''),lore_type='Key',region=r,
        location=f'LOC_SITE_{r}_{(i*5)%20+1:02d}',text_id=f'TXT_LORE_{n:03d}',unlocks=f'LOC_DOOR_{r}_{i+1:02d}',weight=0,sell_price=0,icon='UI_ICON_LORE_KEY'))
w('lore_items.csv',lore,list(lore[0].keys()))

# ---------- crafting recipes ----------
BREW_IN={'EMB':'HRB_02','STM':'HRB_03','HOL':'HRB_04','FRS':'HRB_05','BLM':'HRB_06','IRN':'HRB_07'}
rc=[]
def rcp(rid,station,out,qty,ins,ember,skill,rank):
    rc.append(dict(recipe_id=rid,station=station,output=out,output_qty=qty,inputs=' + '.join(f'{q}x ITM_MAT_{m}' if not m.startswith('ITM_') else f'{q}x {m}' for m,q in ins),
        ember_cost=ember,skill=skill,skill_rank_req=rank,craft_time_s=2.0,learned_from='default' if rank<=10 else f'Skill rank {rank}'))
for c in cons:
    a=c['item_id'][8:]; r=c['craft_recipe']
    if not r: continue
    if a.startswith('BRW_') and a[4:] in BREW_IN: rcp(r,'Brewing','ITM_CON_'+a,2,[('HRB_09',1),(BREW_IN[a[4:]],2),('HRB_01',1)],0,'Ember Rite',10)
    elif a.startswith('BRW_'): rcp(r,'Brewing','ITM_CON_'+a,1,[('HRB_09',1),('HRB_13',2),('MON_06' if a=='BRW_GRT' else 'HRB_01',1)],50,'Ember Rite',25)
    elif a.startswith('FOD_'): rcp(r,'Brewing','ITM_CON_'+a,1,{'FOD_RATION':[('HRB_10',1),('HRB_12',1)],'FOD_WATER':[('HRB_09',2)],'FOD_STEW':[('HRB_11',1),('HRB_10',1),('HRB_09',1)],
                         'FOD_JERKY':[('HRB_11',1),('HRB_12',1)],'FOD_TEA':[('HRB_14',1),('HRB_09',1)]}[a],0,'Ember Rite',1)
    elif a=='UTL_ECHO': rcp(r,'Brewing','ITM_CON_'+a,1,[('MON_02',1),('HRB_14',2),('HRB_08',1)],200,'Warding',30)
    elif a=='UTL_OIL': rcp(r,'Brewing','ITM_CON_'+a,2,[('HRB_08',2)],0,'Ember Rite',1)
    else:
        ins={'THR_SHARD':[('PRT_02',1),('PRT_05',1),('HRB_02',1)],'THR_STORM':[('PRT_04',1),('PRT_05',1),('HRB_03',1)],'THR_FROST':[('PRT_05',1),('HRB_05',2)],
             'THR_HOLLOW':[('PRT_05',1),('MON_01',2)],'THR_SEED':[('PRT_05',1),('HRB_06',2)],'THR_SHRAP':[('PRT_10',1),('HULL_01',3)],'THR_FLASH':[('PRT_08',1),('PRT_05',1)],
             'THR_SMOKE':[('PRT_05',1),('HRB_09',1),('HRB_12',1)],'THR_KNIFE':[('HULL_01',1)],'THR_DECOY':[('PRT_06',1),('PRT_07',1),('PRT_01',1)],'UTL_FLARE':[('PRT_04',1),('PRT_02',1)],
             'UTL_PICK':[('PRT_01',1)],'UTL_AMMO_C':[('PRT_03',4),('PRT_02',2),('PRT_06',1)],'UTL_AMMO_G':[('PRT_09',2),('PRT_07',1),('MON_04',1)]}[a]
        rcp(r,'Tinkering','ITM_CON_'+a,5 if a=='THR_KNIFE' else 1,ins,0,'Engineering',1 if a in('THR_KNIFE','UTL_PICK','THR_SHARD') else 20)
rcp('ITM_RCP_TNK_AMMO_COM','Tinkering','ITM_AMO_COM',40,[('PRT_03',2),('PRT_02',1)],0,'Engineering',1)
rcp('ITM_RCP_TNK_AMMO_CHG','Tinkering','ITM_AMO_CHG',4,[('PRT_09',1),('PRT_07',1)],0,'Engineering',25)
rcp('ITM_RCP_TNK_AMMO_HVY','Tinkering','ITM_AMO_HVY',1,[('PRT_10',1),('PRT_02',2),('MON_04',1)],0,'Engineering',50)
for t,code in enumerate(['HULL','DUST','GLASS','STAR']):
    rcp(f'ITM_RCP_SMT_REFINE_{code}','Smithing',f'ITM_MAT_{code}_02',1,[(f'{code}_01',10)],50*(t+1),'Engineering',1+t*20)
for s in sets_rows:
    if s['source']!='Crafted': continue
    mat=s['name'].split()[0]; t=['Scrap','Riveted','Dustforged','Shardsteel','Choirglass','Starmetal'].index(mat)
    base=['HULL_01','HULL_02','DUST_01','DUST_02','GLASS_02','STAR_02'][t]; q={'Light':3,'Medium':4,'Heavy':6}[s['weight_class']]
    for k,(slot,share,_) in enumerate(SL):
        rcp(f'ITM_RCP_SMT_{mat.upper()}_{s["name"].split()[1].upper()}_{slot.upper()}','Smithing',f'{s["set_id"]}_{slot.upper()}',1,
            [(base,max(1,round(q*share*4))),('MON_0'+str(2*(t%4)+1),2)],round(300*(1+t)**1.5,-1),'Engineering',[1,10,25,40,60,80][t])
w('crafting_recipes.csv',rc,list(rc[0].keys()))
w('rite_crafting.csv',[dict(rule_id='ITM_RITE_01',rule='Cooldown formula',value='ITM_F_RITE_COST'),dict(rule_id='ITM_RITE_02',rule='Reagent cost',value='1 Essence of the effect element per 10 magnitude (round up) + 1 Choir Glass per effect beyond the first'),
  dict(rule_id='ITM_RITE_03',rule='Max effects per Rite',value='Warding/Shaping rank <50: 2, <100: 3, 100: 4'),dict(rule_id='ITM_RITE_04',rule='Magnitude cap',value='crafted bonus portion <= 15% (ITM_F_CRAFT_CAP); damage magnitude cap 40 + skill rank'),
  dict(rule_id='ITM_RITE_05',rule='Station',value='Choir altar in Lantern Hold and every Choir site'),dict(rule_id='ITM_RITE_06',rule='Effect list',value='spell effects live in data/actors (ACT_SPELL_*)')],['rule_id','rule','value'])

# ---------- loot tables ----------
LT=[]
def lt(tid,owner,entry,qmin,qmax,chance,cond=''):
    LT.append(dict(table_id=tid,owner=owner,entry=entry,qty_min=qmin,qty_max=qmax,chance_pct=chance,condition=cond))
FMON={'Hollowed':('MON_01','MON_02'),'Remnant':('MON_03','MON_04'),'Thorn Clan':('MON_05','MON_06'),'Choirborn':('MON_07','MON_08')}
ROLE={'fodder':(1.0,3,35,0),'shield':(1.5,6,45,1),'skirmisher':(1.2,6,45,0),'artillery':(1.3,6,50,1),'heavy':(2.5,20,80,2),'leader':(3.0,30,60,2)}  # gear % cut for B08 SIM-06
for fac,(m1,m2) in FMON.items():
    for role,(em,gear,ammo,elite) in ROLE.items():
        tid=f'ITM_LT_{fac.upper().replace(" ","")}_{role.upper()}'; own=f'ACT_{fac.upper().replace(" ","")}_{role.upper()}_*'
        lt(tid,own,'ITM_CUR_EMBER','ACT_EMBER_KILL(role,region)','x'+str(em),100,'amount formula owned by data/actors')
        lt(tid,own,'ITM_MAT_'+m1,1,2 if role=='fodder' else 3,40)
        lt(tid,own,'ITM_MAT_'+m2,1,1,5+10*elite)
        lt(tid,own,'ITM_LT_TIERMAT_<region>',1,1,8+4*elite)  # B08 SIM-05
        lt(tid,own,'ITM_AMO_COM','class pickup','class pickup',ammo)
        lt(tid,own,'ITM_AMO_CHG','class pickup','class pickup',[0,5,25][elite])
        lt(tid,own,'ITM_AMO_HVY',1,1,10 if role=='heavy' else 0)
        lt(tid,own,'ITM_LT_CONSUMABLE',1,1,6+4*elite)
        lt(tid,own,'ITM_LT_GEAR_<region>',1,1,gear,'rarity per ITM_F_DROP_RARITY; elite weight x2 on Rare+ for heavy/leader')
        if fac!='Choirborn' or True: lt(tid,own,'ITM_LT_ENEMYSET_'+fac.upper().replace(' ',''),1,1,[1,2,4][elite])
for r in REG:
    reg=r[0]; t=REGIDS.index(reg)
    # tier mats
    tid='ITM_LT_TIERMAT_'+reg
    for code,wts in [('HULL',[80,60,40,25,15,10,5,5]),('DUST',[18,35,45,45,40,30,25,20]),('GLASS',[2,5,14,26,35,40,40,40]),('STAR',[0,0,0,4,10,20,30,35])]:
        lt(tid,'subtable','ITM_MAT_'+code+'_01',1,3,wts[t],'weighted pick')
    lt('ITM_LT_GEAR_'+reg,'subtable','POOL weapons_melee+weapons_firearm+catalysts first_region<='+reg,1,1,55,'weighted pick')
    lt('ITM_LT_GEAR_'+reg,'subtable','POOL armor_pieces first_region<='+reg+' (source Found/Enemy drop/Crafted)',1,1,45,'weighted pick')
    if t<7:
        # Small Ember Pouches scale with the band: 0.05 (chest) and 0.2 (vault) x kindle cost at band midpoint (B08 SIM-03)
        pouches=lambda share: max(1,round(share*player_level_cost((r[2]+r[3])//2)/200))
        for kind,(nmat,gear,cons_,ember) in {'SMALLCHEST':(2,15,60,pouches(0.05)),'SHARDCRATE':(3,0,0,0),'VAULT':(5,100,100,pouches(0.2))}.items():
            tid=f'ITM_LT_{kind}_{reg}'
            lt(tid,f'LOC_{kind}_{reg}_*','ITM_LT_TIERMAT_'+reg,1,nmat,100)
            if kind=='SHARDCRATE': lt(tid,f'LOC_{kind}_{reg}_*','ITM_AMO_CHG','class pickup x2','class pickup x2',100); lt(tid,f'LOC_{kind}_{reg}_*','ITM_MAT_DUST_01',1,2,60)
            if gear: lt(tid,f'LOC_{kind}_{reg}_*','ITM_LT_GEAR_'+reg,1,1 if kind!='VAULT' else 2,gear,'VAULT: rarity floor Rare' if kind=='VAULT' else '')
            if cons_: lt(tid,f'LOC_{kind}_{reg}_*','ITM_LT_CONSUMABLE',1,2,cons_)
            if ember: lt(tid,f'LOC_{kind}_{reg}_*','ITM_CON_UTL_POUCH_S',ember,ember,50 if kind=='SMALLCHEST' else 100)
            if kind!='SMALLCHEST': lt(tid,f'LOC_{kind}_{reg}_*','ITM_LT_ARTS',1,1,25 if kind=='VAULT' else 20)  # crates: B08 SIM-09
for c in cons:
    if c['category'] in('Brew','Throwable','Food') or c['item_id'] in('ITM_CON_UTL_FLARE','ITM_CON_UTL_PICK','ITM_CON_UTL_OIL','ITM_CON_UTL_POUCH_S'):
        lt('ITM_LT_CONSUMABLE','subtable',c['item_id'],1,3 if c['category']=='Throwable' else 1,{'Brew':4,'Throwable':6,'Food':5}.get(c['category'],8),'weighted pick')
for a in arts: lt('ITM_LT_ARTS','subtable',a['item_id'],1,1,3 if a['rarity']=='Rare' else 1,'weighted pick')
for fac in FMON:
    k=fac.upper().replace(' ','')
    for s in sets_rows:
        if s['source']=='Enemy drop' and s['name'].startswith(fac):
            for slot,*_ in SL: lt('ITM_LT_ENEMYSET_'+k,'subtable',f'{s["set_id"]}_{slot.upper()}',1,1,{'Light':50,'Medium':35,'Heavy':15}[s['weight_class']],'weighted pick')
BCAT=[('Shard-bearer',6),('Citadel boss',6),('Field boss',12),('Site boss',12),('Raid boss',4)]
bi=0
for cat,cnt in BCAT:
    for j in range(cnt):
        bi+=1; bid=f'ACT_BOSS_{bi:02d}'; tid=f'ITM_LT_BOSS_{bi:02d}'
        reg=REGIDS[j%6] if cat!='Raid boss' else 'REG_END'
        lt(tid,bid,'ITM_CUR_EMBER','ACT_EMBER_BOSS('+bid+')','',100,'owned by data/actors')
        if bi in SHB_BY_BOSS: lt(tid,bid,SHB_BY_BOSS[bi],1,1,100,'first kill per character; repeat kills 10% (raid: weekly)')
        lt(tid,bid,'ITM_MAT_SPC_ASCENDANT',1,{'Shard-bearer':2,'Raid boss':2}.get(cat,1),100 if cat in('Shard-bearer','Raid boss','Citadel boss') else 35)
        lt(tid,bid,'ITM_LT_GEAR_'+reg,2 if cat!='Site boss' else 1,3 if cat in('Shard-bearer','Raid boss') else 2,100,'boss: rarity weights x4 on Rare+')
        lt(tid,bid,'ITM_LT_ARTS',1,1,100 if cat in('Citadel boss','Field boss') else 30)
        lt(tid,bid,'ITM_LT_TIERMAT_'+reg,3,6,100)
        if cat=='Site boss' and j<8: lt(tid,bid,'ITM_CON_TNC_SEED',1,1,100,'first kill; 8 Tonic Seeds total')
        if cat=='Field boss' and j<8: lt(tid,bid,'ITM_CON_TNC_DISTIL',1,1,100,'first kill; 8 Distillations total')
# Undervault bosses (levels/undervault UVREQ_05-07), approved 2026-10-03: 4 bosses outside the plan's 40
for tid,bid,reg in [('ITM_LT_BOSS_UV_02','ACT_BOSS_UV_STEVEDORE','REG_02'),('ITM_LT_BOSS_UV_03','ACT_BOSS_UV_ROOTWRIGHT','REG_03'),('ITM_LT_BOSS_UV_05','ACT_BOSS_UV_SUMPMOTHER','REG_05'),('ITM_LT_BOSS_UV_CORE','ACT_BOSS_UV_GOVERNOR','REG_04')]:
    lt(tid,bid,'ITM_CUR_EMBER','ACT_EMBER_BOSS('+bid+')','',100,'owned by data/actors')
    lt(tid,bid,'ITM_MAT_SPC_ASCENDANT',1,1,100)
    lt(tid,bid,'ITM_LT_GEAR_'+reg,1,2,100,'boss: rarity weights x4 on Rare+')
    lt(tid,bid,'ITM_LT_TIERMAT_'+reg,3,6,100)
for act,seals in [('Strike',10),('Hollowed Citadel',15),('Arena win',5),('Arena loss',2)]:
    tid='ITM_LT_ENDGAME_'+act.upper().replace(' ','_')
    lt(tid,'activity','ITM_CUR_SEALS',seals,seals,100,'weekly cap 100')
    lt(tid,'activity','ITM_LT_GEAR_REG_END',1,1,100 if 'Arena' not in act else 25)
    if 'Arena' not in act: lt(tid,'activity','ITM_MAT_STAR_01',2,4,100)
NODES=[('SCRAP_PILE','HULL_01',2,5),('SHARD_VEIN','DUST_01',1,3),('GLASS_CLUSTER','GLASS_01',1,2),('STAR_METEOR','STAR_01',1,2)]+[(f'HERB_{i+1:02d}',f'HRB_{i+1:02d}',1,3) for i in range(8)]+[('PARTS_CRATE','PRT_*',1,3)]
for nm,m,a,b in NODES: lt('ITM_LT_NODE_'+nm,'LOC_NODE_'+nm+'_*','ITM_MAT_'+m,a,b,100,'respawns 72 game hours')
w('loot_tables.csv',LT,['table_id','owner','entry','qty_min','qty_max','chance_pct','condition'])

# ---------- vendors ----------
V=[]
def ven(vid,name,loc,item,price,stock,unlock=''):
    V.append(dict(vendor_id=vid,vendor_name=name,location=loc,item_id=item,price=price,currency='ITM_CUR_SEALS' if 'SEALS' in vid else 'ITM_CUR_EMBER',stock=stock,restock_game_h=72,unlock=unlock))
HOLD='LOC_LANTERN_HOLD'
for m in melee+guns:
    if m['rarity'] in('Common','Forged'): ven('ITM_VEN_QUARTERMASTER','Quartermaster',HOLD,m['item_id'],m['buy_price'],1,'' if m['first_region'] in('REG_01','REG_02') else f'Light first Anchor in {m["first_region"]}')
for p in pieces:
    if p['rarity'] in('Common','Forged') and 'Origin' not in p['name'] and p['set_id'] in [s['set_id'] for s in sets_rows if s['source'] in('Found','Enemy drop')]:
        ven('ITM_VEN_ARMORER','Armorer',HOLD,p['item_id'],p['buy_price'],1,f'Light first Anchor in {p["first_region"]}')
for c in cons:
    if c['buy_price']: ven('ITM_VEN_APOTHECARY' if c['category'] in('Brew','Food') or c['item_id'].endswith(('ECHO','OIL')) else 'ITM_VEN_TINKER',
                          'Apothecary' if c['category'] in('Brew','Food') else 'Tinker',HOLD,c['item_id'],c['buy_price'],{'Brew':5,'Food':10,'Throwable':10}.get(c['category'],3))
for mt in mats:
    if mt['buyable']=='yes': ven('ITM_VEN_TINKER' if mt['category']=='Tinkering part' else 'ITM_VEN_APOTHECARY','Tinker' if mt['category']=='Tinkering part' else 'Apothecary',HOLD,mt['item_id'],mt['buy_price'],20 if mt['category']!='Infusion' else 2,
        'Defeat any Citadel boss' if mt['category']=='Infusion' else '')
for a in arts[:20]: ven('ITM_VEN_ARCHIVIST','Choir Archivist',HOLD,a['item_id'],a['buy_price'],1,'Join or befriend the Choir (LOC_Q_CHOIR_01)')
for ct in cats[:12]: ven('ITM_VEN_ARCHIVIST','Choir Archivist',HOLD,ct['item_id'],ct['buy_price'],1)
for d in cos:
    if d['price_ember']: ven('ITM_VEN_CLOTHIER','Clothier',HOLD,d['item_id'],d['price_ember'],99)
for o in cos:
    if o.get('price_seals'): ven('ITM_VEN_SEALS','Seal Warden',HOLD,o['item_id'],o['price_seals'],1,'Reach Endgame')
ven('ITM_VEN_SEALS','Seal Warden',HOLD,'ITM_MAT_SPC_ASCENDANT',60,2,'Reach Endgame'); ven('ITM_VEN_SEALS','Seal Warden',HOLD,'ITM_MAT_STAR_01',10,20,'Reach Endgame')
for t,reg in enumerate(REGIDS[:6]):
    vid=f'ITM_VEN_TRADER_{reg}'
    for cid,st in [('ITM_CON_BRW_BRT',3),('ITM_CON_THR_SHARD',5),('ITM_CON_UTL_FLARE',2),('ITM_CON_FOD_RATION',10),('ITM_CON_UTL_PICK',10),('ITM_CON_UTL_AMMO_C',2)]:
        c=next(x for x in cons if x['item_id']==cid); ven(vid,f'Wandering trader ({reg})',f'LOC_TOWN_{reg}_01',cid,round(c['buy_price']*1.2),st)
    for g in [x for x in melee+guns if x['first_region']==reg][:4]: ven(vid,f'Wandering trader ({reg})',f'LOC_TOWN_{reg}_01',g['item_id'],round(g['buy_price']*1.2,-1),1)
# Thorn Trader Skell (thornwood LREQ_07): Thorn gear at the Thorn King's Moot; town smiths, tinkers and brewers are bench services with no stock
for g in [x for x in melee+guns if x['first_region']=='REG_03'][4:10]: ven('ITM_VEN_THORN_SKELL','Thorn Trader Skell','LOC_TOWN_REG_03_03',g['item_id'],round(g['buy_price']*1.15,-1),1)
for cid,st in [('ITM_CON_UTL_PICK',10),('ITM_CON_FOD_RATION',10)]:
    c=next(x for x in cons if x['item_id']==cid); ven('ITM_VEN_THORN_SKELL','Thorn Trader Skell','LOC_TOWN_REG_03_03',cid,round(c['buy_price']*1.15),st)
w('vendors.csv',V,['vendor_id','vendor_name','location','item_id','price','currency','stock','restock_game_h','unlock'])

# ---------- master index ----------
idx=[]
for f,rows,cat in [('weapons_melee.csv',melee,'Melee weapon'),('weapons_firearm.csv',guns,'Firearm'),('catalysts.csv',cats,'Catalyst'),('shardborn.csv',sb,'Shardborn'),
    ('weapon_arts.csv',arts,'Weapon Art'),('arena_power_weapons.csv',[{'item_id':f'ITM_PWR_{i+1:02d}','name':p[0]} for i,p in enumerate(pw)],'Arena power weapon'),
    ('armor_pieces.csv',pieces,'Armor piece'),('cosmetics.csv',cos,'Cosmetic'),('consumables.csv',cons,'Consumable'),('materials.csv',mats,'Material'),('lore_items.csv',lore,'Lore item'),
    ('ammo.csv',[{'item_id':'ITM_AMO_COM','name':'Common Rounds'},{'item_id':'ITM_AMO_CHG','name':'Charged Cells'},{'item_id':'ITM_AMO_HVY','name':'Heavy Munitions'}],'Ammo'),
    ('currencies.csv',[{'item_id':'ITM_CUR_EMBER','name':'Ember'},{'item_id':'ITM_CUR_SEALS','name':'Seals'}],'Currency')]:
    for r in rows: idx.append(dict(item_id=r['item_id'],name=r['name'],category=cat,rarity=r.get('rarity',''),file=f))
w('items_index.csv',idx,['item_id','name','category','rarity','file'])
