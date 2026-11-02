from common import *
ROLE={ # role: hp mult, def mult, stance, ember mult, speed m/s, height m
 'Fodder':(0.6,0.6,20,0.5,4.5,1.8),'Shield-bearer':(1.2,1.2,45,0.9,3.5,2.0),'Skirmisher':(0.8,0.7,25,0.8,6.5,1.8),
 'Artillery':(0.7,0.6,25,0.9,3.5,1.9),'Heavy':(2.5,1.5,80,2.0,3.0,3.2),'Leader':(2.0,1.3,60,2.5,4.5,2.3)}
FAC={ # faction id, name, hp mult, ward frac, regions, asset, aggression bias, notes
 'Hollowed':('FAC_HOLLOWED',1.0,0.0,['R1','R2','R3','R4','R5','R6','RU'],'A025','Swarm, no Ward; weak to Ember and Bloom'),
 'Remnant':('FAC_REMNANT',0.7,0.5,['R2','R3','R4','R5','R6','RU'],'A026','Shielded drones; Ward tinted Iron by default'),
 'Thorn Clans':('FAC_THORN',1.1,0.0,['R1','R2','R3','R4','RU'],'A027','Morale system; flankers and berserkers'),
 'Choirborn':('FAC_CHOIRBORN',1.2,0.4,['R5','R6','RQ'],'A028','Teleport and counter-cast; Ward tinted Hollow by default'),
}
NAMES={'Hollowed':['Shardsick Shambler','Husk Warden','Glasscrawler','Shard Spitter','Hollowed Brute','Hollow Herald'],
 'Remnant':['Scrap Drone','Bulwark Drone','Hornet Drone','Mortar Frame','Siege Walker','Overseer Node'],
 'Thorn Clans':['Clan Raider','Thorn Shieldman','Briar Stalker','Bonebow Archer','Thorn Berserker','Clan Warchief'],
 'Choirborn':['Choir Acolyte','Hymn Ward','Blinkblade','Choir Lancer','Choir Colossus','Choir Cantor']}
ROLES=list(ROLE)
# resist profile per faction: Slash,Pierce,Blunt,Bullet,Weave, Ember,Storm,Hollow,Frost,Bloom,Iron (fraction)
RES={'Hollowed':[0.0,0.1,-0.1,0.0,0.0,-0.25,0,0.5,0,-0.25,0],'Remnant':[0.2,0.1,-0.2,0.2,-0.1,0,-0.3,0,0.1,0,0.3],
 'Thorn Clans':[0,-0.1,0,-0.1,0.1,-0.2,0,0,0.1,0.3,0],'Choirborn':[0.1,0.1,0.1,0.1,0.25,0,0,0.5,0,-0.3,0]}
WARDTINT={'Remnant':'Iron','Choirborn':'Hollow'}
# attacks: (name, type, element, mult, poise, startup, active, recovery, range m, telegraph, block/parry)
ATK={
'Hollowed':[[('Flailing Claw','Slash','None',0.8,8,22,6,30,1.6,'Arm raises over shoulder, Shard glow','Block/Parry'),('Lunge Bite','Pierce','None',1.0,10,30,8,40,3.0,'Crouch then hiss','Block/Parry'),('Shard Burst','Weave','Hollow',1.2,12,45,4,50,2.5,'Chest Shard flares white, 0.75 s','Block')],
 [('Slab Shove','Blunt','None',0.9,25,26,6,34,2.0,'Shield pulled back','Block'),('Overhead Slab','Blunt','None',1.3,30,38,6,44,2.2,'Shield lifted overhead','Block/Parry'),('Brace','None','None',0,0,10,60,10,0,'Plants feet, Shard dims','-')],
 [('Wall Leap','Slash','None',1.0,10,18,8,36,6.0,'Skitter sound, rear-up','Block/Parry'),('Ceiling Drop','Pierce','None',1.4,15,30,6,46,0,'Drops from above, glass crackle','Dodge'),('Raking Combo x3','Slash','None',0.6,6,14,4,28,1.8,'Rapid clicking','Block/Parry')],
 [('Shard Glob','Weave','Hollow',1.1,10,40,0,40,25,'Throat bulges glowing','Dodge'),('Spit Spray','Weave','Hollow',0.5,4,30,30,40,8,'Head rears, gurgle','Block'),('Burrow Retreat','None','None',0,0,20,40,20,0,'Sinks into ground','-')],
 [('Ground Slam','Blunt','None',1.8,60,50,8,60,4.0,'Both fists raised, roar','Dodge'),('Sweeping Backhand','Blunt','None',1.4,40,36,10,50,3.5,'Torso twists away','Block'),('Shard Eruption','Weave','Hollow',2.0,50,70,10,70,6.0,'Back spikes glow 1.2 s','Dodge')],
 [('Herald Cry','Buff','Hollow',0,0,40,60,30,20,'Screams; nearby Hollowed +25% damage 15 s','Interrupt'),('Raking Talon','Slash','None',1.2,20,24,6,36,2.2,'Wing-arm flares','Block/Parry'),('Hollow Nova','Weave','Hollow',1.6,40,60,8,60,5,'Floats up 0.5 m, pulse builds','Dodge')]],
'Remnant':[[('Spark Ram','Blunt','Storm',0.8,8,24,6,32,2.0,'Thruster whine','Block/Parry'),('Rivet Burst','Bullet','None',0.4,2,30,40,30,20,'Red laser dot','Cover'),('Self-Destruct','Blunt','Storm',2.0,40,90,4,0,3.0,'Rapid beeping 1.5 s','Dodge')],
 [('Shield Charge','Blunt','None',1.0,30,30,20,40,6.0,'Shield glows, wheels spin up','Block'),('Arc Baton','Blunt','Storm',1.2,20,24,6,34,2.0,'Baton crackles','Block/Parry'),('Ward Pulse','Weave','Iron',0.8,20,40,4,40,4.0,'Ward ripples outward','Dodge')],
 [('Strafing Fire','Bullet','None',0.35,1,20,60,20,30,'Rotor pitch drops','Cover'),('Dive Sting','Pierce','None',1.2,12,28,8,50,8.0,'Climbs and stalls','Dodge'),('Flare Drop','Weave','Storm',0.9,10,30,4,30,6.0,'Orange flare','Dodge')],
 [('Mortar Arc','Blunt','None',1.6,40,60,0,60,60,'Red ground circle 1.5 s before','Dodge'),('Cluster Shell','Blunt','None',0.6,10,70,0,60,50,'Three circles','Dodge'),('Point Defense','Bullet','None',0.3,1,10,40,10,15,'Turret spins up','Cover')],
 [('Leg Stomp','Blunt','None',1.6,60,40,6,50,4.0,'Leg rises, hydraulics hiss','Dodge'),('Rail Cannon','Bullet','Storm',2.4,60,80,6,70,80,'Blue charge line 1.3 s','Cover'),('Sweep Laser','Weave','Iron',1.2,30,50,60,40,25,'Laser paints ground','Jump/Dodge')],
 [('Repair Beam','Buff','Iron',0,0,20,120,20,25,'Green beam to ally; heals 4% max HP/s','Interrupt'),('Ward Link','Buff','Iron',0,0,40,600,20,20,'Links allies, +50% Ward 10 s','Interrupt'),('Arc Lash','Weave','Storm',1.3,20,30,6,40,6,'Antennae crackle','Dodge')]],
'Thorn Clans':[[('Hatchet Chop','Slash','None',1.0,12,22,6,32,1.8,'Yell, arm back','Block/Parry'),('Rush Combo x2','Slash','None',0.8,10,18,6,30,2.0,'Sprint in','Block/Parry'),('Throw Hatchet','Slash','None',0.9,8,30,0,30,15,'Draw back throw','Dodge')],
 [('Shield Bash','Blunt','None',0.9,25,22,6,30,1.8,'Shield shoulder dip','Block'),('Thorn Spear Thrust','Pierce','None',1.2,18,26,6,36,3.0,'Spear drawn back','Block/Parry'),('Turtle','None','None',0,0,10,90,10,0,'Kneels behind shield','-')],
 [('Flank Slash','Slash','None',1.1,10,16,6,30,2.0,'Rustle behind player','Block/Parry'),('Briar Net','None','Bloom',0,0,30,0,30,10,'Net whirls overhead; 40 Root buildup','Dodge'),('Poison Dart','Pierce','Hollow',0.5,2,20,0,24,20,'Blowpipe raised; 30 Drain buildup','Dodge')],
 [('Bone Arrow','Pierce','None',1.0,8,40,0,30,40,'Bow drawn, creak','Dodge/Block'),('Fire Arrow','Pierce','Ember',1.1,8,50,0,30,40,'Flame at arrowhead; 30 Burn','Dodge'),('Volley','Pierce','None',0.6,4,60,0,40,35,'Archers shout together','Cover')],
 [('Frenzy Combo x4','Slash','None',0.9,15,20,6,26,2.4,'Red warpaint glows, roar','Block'),('Leaping Cleave','Slash','None',2.0,45,40,8,60,6.0,'Jumps high','Dodge'),('Berserk','Buff','None',0,0,30,0,20,0,'Under 40% HP: +30% speed, +20% damage, ignores morale','-')],
 [('War Horn','Buff','None',0,0,40,60,30,25,'Horn raised; allies +30 morale, +15% damage 20 s','Interrupt'),('Greataxe Sweep','Slash','None',1.6,40,34,8,50,3.5,'Axe pulled wide','Dodge'),('Chieftain Charge','Blunt','None',1.4,50,30,24,40,8,'Lowers horns','Dodge')]],
'Choirborn':[[('Hymn Bolt','Weave','Hollow',1.0,8,30,0,30,25,'Mouth glows, single note','Dodge'),('Blink Strike','Slash','None',1.0,12,20,6,30,2.0,'Vanishes with chime','Parry'),('Counter-cast','None','Hollow',0,0,8,30,20,0,'Raises palm when player casts; reflects 50%','Wait')],
 [('Choir Barrier','Buff','Hollow',0,0,30,300,20,8,'Dome over allies; absorbs 30% max HP','Break with Bloom'),('Resonant Slam','Blunt','Hollow',1.2,30,34,6,40,2.5,'Staff hums','Block/Parry'),('Silence','None','Hollow',0,0,40,0,30,10,'Ring of runes; disables abilities 4 s','Dodge')],
 [('Blink Combo x3','Slash','None',0.8,10,12,4,24,2.0,'Chime each blink','Parry'),('Phase Lunge','Pierce','Hollow',1.4,15,24,8,40,8.0,'Afterimage forms','Dodge'),('Mirror Step','None','None',0,0,6,10,10,6,'Teleports behind on player heavy attack','-')],
 [('Choir Lance','Weave','Hollow',1.8,30,60,6,50,50,'Long chord, beam forms 1 s','Cover/Dodge'),('Echo Rain','Weave','Hollow',0.7,8,70,60,40,30,'Notes rise above player','Move'),('Teleport Retreat','None','None',0,0,10,10,10,15,'Fades','-')]
 ,[('Colossal Chord','Weave','Hollow',2.2,60,70,10,70,8,'Body rings, rising pitch 1.2 s','Dodge'),('Fist of Hymns','Blunt','None',1.8,50,44,8,60,4,'Arm glows','Dodge'),('Gravity Well','None','Hollow',0,0,50,180,30,10,'Pulls player 3 m/s toward it','Sprint out')],
 [('Unmaking Song','Weave','Hollow',1.5,30,60,120,40,12,'Choir chant swells; pulses 4x','Break LoS'),('Recall','Buff','Hollow',0,0,40,0,30,30,'Revives one fallen Choirborn at 50%','Interrupt'),('Counter Choir','None','Hollow',0,0,8,60,20,15,'Reflects next 3 spells','Wait')]]}
AIP_BASE={ # role: aggression, pref range, wDist,wCover,wAllies,wWard,wExposure, react ms, acc10,acc30,acc60, retreat ward, morale, panic, attack tokens
 'Fodder':(0.9,2,0.8,0.1,0.6,0.0,0.1,450,0.6,0.3,0.1,0,50,25,4),'Shield-bearer':(0.6,3,0.6,0.3,0.4,0.5,0.2,350,0.7,0.5,0.2,0.2,70,15,2),
 'Skirmisher':(0.8,4,0.7,0.4,0.2,0.3,0.6,300,0.7,0.5,0.25,0.3,55,25,2),'Artillery':(0.4,25,0.2,0.9,0.3,0.4,0.8,500,0.8,0.6,0.4,0.5,60,30,1),
 'Heavy':(0.7,3,0.7,0.0,0.2,0.2,0.0,600,0.6,0.5,0.3,0,90,0,1),'Leader':(0.5,8,0.4,0.6,0.8,0.5,0.5,300,0.8,0.6,0.35,0.4,100,0,1)}
FADJ={'Hollowed':(0.15,-0.2,'Swarm: ignores cover; flanks by numbers'),'Remnant':(-0.1,0.1,'Coordinated: shares targets, rotates Ward-low units to back'),
 'Thorn Clans':(0.1,0,'Flank: 40% of skirmishers path to player rear; morale-driven'),'Choirborn':(0,0.15,'Blink: teleport to cover when exposed > 2 s; counter-cast on player casts')}
LOOT={'Hollowed':'ITM_MAT_HULLSCRAP 40%; ITM_MAT_SHARDDUST 8%; ITM_CON_TONICSHARD 3%','Remnant':'ITM_MAT_HULLSCRAP 60%; ITM_AMMO_CHARGED 25%; ITM_MAT_SHARDDUST 10%',
 'Thorn Clans':'ITM_MAT_HULLSCRAP 30%; ITM_AMMO_COMMON 50%; ITM_CON_THORNSALVE 10%','Choirborn':'ITM_MAT_CHOIRGLASS 12%; ITM_MAT_SHARDDUST 25%; ITM_AMMO_HEAVY 6%'}
LOOT_ROLE={'Heavy':'; ITM_LOOT_TABLE_{F}_HEAVY 100% (1 roll Forged+)','Leader':'; ITM_LOOT_TABLE_{F}_LEADER 100% (1 roll Rare 20%)'}
RESH=['Res Slash','Res Pierce','Res Blunt','Res Bullet','Res Weave']+['Res '+e for e in ELEMENTS]
enemies=[];attacks=[];aips=[];bylevel=[]
for f,(fid,fhp,wf,regs,asset,note) in FAC.items():
    fk=fid[4:]
    for i,role in enumerate(ROLES):
        hm,dm,st,em,spd,ht=ROLE[role]; name=NAMES[f][i]
        aid=f'ACT_{fk}_{role.upper().replace("-","")}'
        lo=min(REG[r][2] for r in regs); hi=max(REG[r][3] for r in regs)
        ref=lo+ (hi-lo)//2
        ag,pr,wd,wc,wa,ww,we,rt,a10,a30,a60,rw,mo,pa,tok=AIP_BASE[role]; adj=FADJ[f]
        aip=f'AIP_{fk}_{role.upper().replace("-","")}'
        aips.append([aip,f,role,round(min(1,ag+adj[0]),2),pr,wd,round(min(1,wc+adj[1]),2) if wc else wc,wa,ww,we,rt,a10,a30,a60,rw,mo if f!='Remnant' else 'n/a',pa if f in('Hollowed','Thorn Clans') else 'n/a',tok,
            30 if role!='Artillery' else 60,90 if role!='Artillery' else 120,15,adj[2]])
        loot=LOOT[f]+LOOT_ROLE.get(role,'').format(F=fk)
        hp,wref,dref=target(aid,ref,hm*fhp)
        enemies.append([aid,name,fid,role,'Leader' if role=='Leader' else 'Base','',' '.join(regs),f'{lo}-{hi}',ref,round(hm*fhp,2),hp,wref,WARDTINT.get(f,'None') if wf else 'None',
            defense_at(ref,dm),st,*RES[f],aip,em,ember_drop(ref,em),loot,spd,ht,'Head' if f!='Remnant' else 'Core (rear vent)',asset,'Prototype enemy (A011)' if aid=='ACT_REMNANT_SHIELDBEARER' else ''])
        for j,a in enumerate(ATK[f][i]):
            n,t,el,m,po,s,ac,rc,rg,tel,cnt=a
            attacks.append([f'ATK_{aid[4:]}_{j+1}',aid,n,t,el,m,round(dref*m) if m else 0,po,s,ac,rc,max(0,rc-10),rg,tel,cnt,'Dodge timing: roll on frame '+str(max(1,s-8))+'-'+str(s)+' of startup' if m else ''])
        for L in range(1,81):
            _h,_w,_d=target(aid,L,hm*fhp); bylevel.append([aid,L,_h,_w,defense_at(L,dm),_d,ember_drop(L,em)])
# Regional variants: 6 per region R1-R6 = 36 (24 bases + 36; raid adds and extra variants bring the total to 69 enemy types)
EXTRA={'R1':[('Hollowed','Artillery'),('Thorn Clans','Artillery')],'R2':[('Hollowed','Shield-bearer'),('Remnant','Shield-bearer')],'R3':[('Hollowed','Artillery')]}
ADJ={'R1':'Cinder','R2':'Saltborn','R3':'Bramble','R4':'Glass','R5':'Rime','R6':'Deep'}
for rid in ['R1','R2','R3','R4','R5','R6']:
    _,rn,lo,hi,el=REG[rid]
    facs=[f for f in FAC if rid in FAC[f][3]]
    picks=[]; k=0
    order=[0,2,1,3,4,5]
    while len(picks)<6:
        f=facs[k%len(facs)]; role=ROLES[order[(k//len(facs))%6]]
        picks.append((f,role)); k+=1
    picks+=EXTRA.get(rid,[])   # quest-placed variants (campaign SQ_REG_*), approved 2026-10-03: enemy types 69
    for n,(f,role) in enumerate(picks):
        base=[e for e in enemies if e[2]==FAC[f][0] and e[3]==role][0]
        L=lo+(hi-lo)//3 if n<3 else hi-(hi-lo)//4
        hm=ROLE[role][0]*FAC[f][1]; hp,_vw,_vd=target(base[0],L,base[9]); _k=hm/base[9]; hp,_vw=round(hp*_k),round(_vw*_k)   # variants keep their base role's curve (DR-SYS-010 rev 2)
        res=list(base[15:26]); ei=5+ELEMENTS.index(el); oi=5+ELEMENTS.index(OPPOSITE[el])
        res[ei]=round(res[ei]+0.4,2); res[oi]=round(res[oi]-0.25,2)
        vid=f'ACT_VAR_{rid}_{n+1:02d}'
        enemies.append([vid,f'{ADJ[rid]} {base[1].split(" ",1)[-1] if f=="Hollowed" and base[1].startswith("Shard") else base[1]}',base[2],role,'Regional variant',base[0],rid,f'{lo}-{hi}',L,base[9],hp,_vw,el if FAC[f][2] else 'None',
            defense_at(L,ROLE[role][1]),round(ROLE[role][2]*1.1),*res,base[26],ROLE[role][3]*1.2,ember_drop(L,ROLE[role][3]*1.2),base[29]+f'; ITM_MAT_{el.upper()}ESSENCE 15%',base[30],base[31],base[32],'A029',
            f'{el} tint; 30% of physical attack damage converted to {el}; attacks add 20 {el} status buildup'])
# Raid add units (levels/multiplayer MPR-06), approved 2026-10-03: stats from their faction base at the raid level
RAID=[('ACT_RAID_CONDUIT','Conduit Drone','Remnant','Fodder',80,'Raid Wing 1; drops 1 Conduit charge on death'),
      ('ACT_RAID_INDEXWARDEN','Index Warden','Choirborn','Leader',84,'Raid Wing 2; drops a Reading Glass'),
      ('ACT_RAID_GHOSTOFFICER','Ghost Officer','Choirborn','Shield-bearer',88,'Raid Wing 3; station-bound, grants Rank on death'),
      ('ACT_RAID_CHORISTER','Chorister','Choirborn','Artillery',92,'Raid Wing 4; +25% damage aura 15 m for allies')]
for aid,name,f,role,L,note in RAID:
    base=[e for e in enemies if e[2]==FAC[f][0] and e[3]==role][0]
    hm=ROLE[role][0]*FAC[f][1]; hp,_vw,_vd=target(base[0],L,base[9]); _k=hm/base[9]; hp,_vw=round(hp*_k),round(_vw*_k)
    enemies.append([aid,name,base[2],role,'Raid add',base[0],'RQ',f'{L}-{L}',L,base[9],hp,_vw,base[12],defense_at(L,ROLE[role][1]),ROLE[role][2],*base[15:26],base[26],0,0,
        'None (raid mechanic unit)',base[30],base[31],base[32],'A028' if f=='Choirborn' else 'A026',note])
H=['ACT_ID','Name','FAC_ID','Role','Tier','Base ACT_ID','Regions','Level band','Reference level','HP mult','HP @ref','Ward @ref','Ward element','Defense @ref','Stance']+RESH+['AIP_ID','Ember mult','Ember @ref','Drops (item refs, chance)','Move speed m/s','Height m','Weak point','Asset ref','Notes']
write('enemies.csv',H,enemies)
write('enemy_attacks.csv',['ATK_ID','ACT_ID','Attack','Damage type','Element','Damage mult','Damage @ref level','Poise damage','Startup frames','Active frames','Recovery frames','Punish window frames','Range m','Telegraph','Counter','Dodge note'],attacks)
write('enemy_stats_by_level.csv',['ACT_ID','Level','HP','Ward','Defense','Damage per 1.0 mult','Ember'],bylevel)

# ---------- Creatures ----------
C=[ # name, regions, hostility, size, hp mult, stance, AIP, atk1, atk2, drops
('Ashhound','R1','Hostile','Medium',0.8,25,'PACK',('Ember Bite','Pierce','Ember',1.0,22),('Pounce','Blunt','None',1.3,34),'ITM_MAT_HIDE 60%; ITM_MAT_EMBERESSENCE 10%'),
('Bloom Stalker','R3','Hostile','Large',1.6,50,'AMBUSH',('Vine Lash','Slash','Bloom',1.2,28),('Root Snare','None','Bloom',0,40),'ITM_MAT_BLOOMPOD 40%; ITM_MAT_HIDE 50%'),
('Bog Leech','R3','Hostile','Small',0.4,10,'SWARM',('Latch','Pierce','Hollow',0.5,14),('Drain Suck','Weave','Hollow',0.3,30),'ITM_MAT_LEECHOIL 50%'),
('Choir Wisp','R5 R6 RQ','Hostile','Small',0.5,10,'FLYER',('Hymn Spark','Weave','Hollow',0.8,26),('Blink','None','None',0,10),'ITM_MAT_CHOIRGLASS 6%; ITM_MAT_SHARDDUST 30%'),
('Cinder Drake','R1 R4','Hostile','Large',2.2,70,'FLYER',('Flame Breath','Weave','Ember',1.6,50),('Tail Whip','Blunt','None',1.4,30),'ITM_MAT_DRAKESCALE 70%; ITM_MAT_EMBERESSENCE 30%'),
('Cliff Roc','R2 R5','Territorial','Large',1.8,60,'FLYER',('Talon Dive','Pierce','None',1.8,48),('Wing Gust','None','Storm',0.4,30),'ITM_MAT_FEATHER 80%; ITM_MAT_HIDE 30%'),
('Frost Elk','R5','Passive','Medium',1.0,35,'PREY',('Antler Gore','Pierce','None',1.2,30),('Kick','Blunt','None',0.9,22),'ITM_MAT_HIDE 80%; ITM_CON_MEAT 100%'),
('Glasswing Moth','R4','Passive','Small',0.2,5,'PREY',('Dust Cloud','None','Iron',0,40),('Flutter','None','None',0,10),'ITM_MAT_GLASSDUST 70%'),
('Grave Vulture','R6 R1','Scavenger','Medium',0.6,20,'SCAVENGER',('Peck','Pierce','None',0.8,18),('Carrion Screech','None','Hollow',0,40),'ITM_MAT_FEATHER 60%'),
('Hull Crab','R2','Territorial','Medium',1.2,45,'TERRITORIAL',('Pincer Crush','Blunt','None',1.3,32),('Shell Spin','Blunt','None',1.0,40),'ITM_MAT_HULLSCRAP 50%; ITM_MAT_CHITIN 60%'),
('Ironback Tortoise','R4','Passive','Large',3.0,90,'PREY',('Shell Slam','Blunt','Iron',1.8,60),('Withdraw','None','None',0,60),'ITM_MAT_STARMETAL 2%; ITM_MAT_CHITIN 80%'),
('Lantern Fox','R1 R3 RH','Passive','Small',0.3,5,'PREY',('Nip','Pierce','None',0.4,12),('Flee Flash','None','None',0,10),'ITM_MAT_HIDE 60%; ITM_MAT_LANTERNTAIL 20%'),
('Marrow Wolf','R5 R6','Hostile','Medium',1.0,30,'PACK',('Marrow Bite','Pierce','Frost',1.1,24),('Howl','Buff','None',0,40),'ITM_MAT_HIDE 70%; ITM_MAT_BONE 50%'),
('Moss Golem','R3','Territorial','Large',2.8,90,'TERRITORIAL',('Boulder Fist','Blunt','None',1.8,44),('Spore Burst','Weave','Bloom',1.0,60),'ITM_MAT_BLOOMPOD 60%; ITM_MAT_STONEHEART 15%'),
('Quiet Mite','RQ R6','Hostile','Small',0.3,5,'SWARM',('Bite','Pierce','Hollow',0.4,10),('Burst','Weave','Hollow',0.9,50),'ITM_MAT_SHARDDUST 20%'),
('Rust Beetle','R2 R4 RU','Territorial','Small',0.6,20,'TERRITORIAL',('Acid Spit','Weave','Iron',0.8,30),('Horn Ram','Blunt','None',0.9,24),'ITM_MAT_CHITIN 70%; ITM_MAT_HULLSCRAP 30%'),
('Salt Serpent','R2','Hostile','Large',1.8,55,'AMBUSH',('Strike','Pierce','None',1.4,22),('Brine Spit','Weave','Storm',1.0,40),'ITM_MAT_SERPENTSKIN 70%'),
('Shard Wyrm (juvenile)','R4 R6 RU','Hostile','Huge',4.0,110,'APEX',('Shard Breath','Weave','Iron',2.0,60),('Coil Crush','Blunt','None',1.8,50),'ITM_MAT_STARMETAL 25%; ITM_MAT_WYRMSCALE 100%'),
('Shardrat swarm','RU R1 R2','Hostile','Small',0.25,5,'SWARM',('Gnaw','Pierce','None',0.3,10),('Scatter','None','None',0,10),'ITM_MAT_SHARDDUST 15%'),
('Storm Ray','R2','Territorial','Large',1.4,40,'FLYER',('Static Glide','Weave','Storm',1.2,30),('Tail Barb','Pierce','Storm',1.0,24),'ITM_MAT_STORMESSENCE 30%; ITM_MAT_HIDE 40%'),
('Strider (wild)','R1 R3 R5','Passive','Large',1.6,50,'PREY',('Kick','Blunt','None',1.2,30),('Leap Away','None','None',0,10),'Tameable: ITM_KEY_STRIDERHARNESS required'),
('Thornboar','R3 R1','Territorial','Medium',1.2,40,'TERRITORIAL',('Tusk Charge','Pierce','None',1.5,36),('Thorn Bristle','Pierce','Bloom',0.6,20),'ITM_MAT_HIDE 80%; ITM_CON_MEAT 100%'),
('Undervault Crawler','RU','Hostile','Large',2.0,60,'AMBUSH',('Mandible Snap','Slash','None',1.5,30),('Web Spit','None','Hollow',0,40),'ITM_MAT_CHITIN 70%; ITM_MAT_CHOIRGLASS 4%'),
('Veyl Deer','R1 R3 R5','Passive','Medium',0.6,15,'PREY',('Kick','Blunt','None',0.6,20),('Bolt','None','None',0,10),'ITM_MAT_HIDE 80%; ITM_CON_MEAT 100%')]
SIZEEM={'Small':0.3,'Medium':0.7,'Large':1.5,'Huge':3.0}
crows=[];catk=[]
for n,regs,hos,size,hm,st,aip,a1,a2,drop in C:
    cid='ACT_CRT_'+''.join(ch for ch in n.split(' (')[0].upper() if ch.isalpha())
    rl=regs.split(); lo=min(REG[r][2] for r in rl); hi=max(REG[r][3] for r in rl); ref=(lo+hi)//2
    hp=enemy_hp(ref,hm)
    crows.append([cid,n,regs,hos,size,f'{lo}-{hi}',ref,hm,hp,defense_at(ref,0.6 if size=='Small' else 1.0),st,'AIP_CRT_'+aip,SIZEEM[size],ember_drop(ref,SIZEEM[size]),drop,'A030'])
    for j,(an,t,el,m,s) in enumerate([a1,a2]):
        catk.append([f'ATK_{cid[4:]}_{j+1}',cid,an,t,el,m,enemy_dmg(ref,m) if m else 0,round(m*20),s,6 if m else 0,round(s*1.3),round(s*1.3)-10,'2.0' if t in ('Blunt','Pierce','Slash') else '8.0','Animal tell: wind-up '+str(round(s/60,2))+' s',('Block/Dodge' if m else 'Status/utility'),''])
write('creatures.csv',['ACT_ID','Name','Regions','Hostility','Size','Level band','Reference level','HP mult','HP @ref','Defense @ref','Stance','AIP_ID','Ember mult','Ember @ref','Drops (item refs, chance)','Asset ref'],crows)
attacks+=catk
write('enemy_attacks.csv',['ATK_ID','ACT_ID','Attack','Damage type','Element','Damage mult','Damage @ref level','Poise damage','Startup frames','Active frames','Recovery frames','Punish window frames','Range m','Telegraph','Counter','Dodge note'],attacks)
CR=[('AIP_CRT_PACK',0.8,3,'Circles at 6 m, 2 attack tokens, retreat at 30% HP, alpha death = flee'),('AIP_CRT_AMBUSH',0.9,2,'Hidden until player within 6 m; first attack +30% damage'),
('AIP_CRT_SWARM',1.0,1,'Groups of 6-12; each member 1 attack per 3 s; scatters from Ember'),('AIP_CRT_FLYER',0.6,10,'Hovers 6-15 m; lands to attack; grounded 4 s by stance break'),
('AIP_CRT_PREY',0.0,0,'Flees at 25 m detection; fights only when cornered'),('AIP_CRT_TERRITORIAL',0.5,3,'Warns at 20 m (posture 3 s), attacks inside 12 m, gives up beyond 40 m'),
('AIP_CRT_SCAVENGER',0.3,3,'Attacks only targets under 30% HP or corpses; flees when hit twice'),('AIP_CRT_APEX',1.0,4,'Hunts players within 60 m; ignores other creatures; enrages at 50% HP (+20% speed)')]
for a,ag,pr,d in CR: aips.append([a,'Creature',a[8:].title(),ag,pr,'','','','','',400,'','','','','n/a','n/a','',25,90,20,d])
write('ai_profiles.csv',['AIP_ID','Faction','Role','Aggression 0-1','Preferred range m','wDist','wCover','wAllies','wWard','wExposure','Reaction ms','Acc @10 m','Acc @30 m','Acc @60 m','Retreat at Ward fraction','Morale base','Panic threshold','Attack tokens','Sight m','Sight FOV deg','Hearing m','Behaviour notes'],aips)
