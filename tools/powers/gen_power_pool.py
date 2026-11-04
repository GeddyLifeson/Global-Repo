# S6960 gen_power_pool.py: writes the shared NPC power pool (POWER_POOL.tsv), designed power datapack JSONs and archetype grants.
# Pool powers are existing NeoOrigins 2.2.30 power ids where one exists; gaps are composed from NeoOrigins action types (namespace diaithirpowers). Run: python3 -I gen_power_pool.py OUTDIR
import json,sys,pathlib
O=pathlib.Path(sys.argv[1]); (O/'powers').mkdir(parents=True,exist_ok=True)
NS='diaithirpowers'
def attr(a,v,op='add_value'): return {"type":"neoorigins:attribute_modifier","attribute":"minecraft:"+a,"amount":v,"operation":op}
def eff(e,amp,dur): return {"type":"neoorigins:apply_effect","effect":"minecraft:"+e,"amplifier":amp,"duration":dur}
def active(icon,cd,action): return {"type":"neoorigins:active_ability","cooldown_icon":"minecraft:"+icon,"cooldown_ticks":cd,"entity_action":action}
def aoe(r,*acts): return {"type":"neoorigins:area_of_effect","radius":r,"include_source":False,"entity_action":{"type":"neoorigins:and","actions":list(acts)}}
def proj(et,sp,dmg,r=2.5): return {"type":"neoorigins:spawn_projectile","entity_type":"neoorigins:magic_orb","effect_type":et,"speed":sp,"inaccuracy":0.0,
  "on_hit_action":aoe(r,{"type":"neoorigins:damage","amount":dmg,"source":{"name":"magic"}})}
def persist(*e): return {"type":"neoorigins:persistent_effect","toggleable":False,"ambient":True,"show_particles":False,"show_icon":False,"effects":[{"effect":"minecraft:"+n,"amplifier":a} for n,a in e]}
def dmg_in(m): return {"type":"neoorigins:modify_damage","direction":"in","multiplier":m}
D={}  # designed power id -> list of component JSONs (one file each: id, id_2 ...)
for t,(ad,kb) in enumerate([(4,0.5),(10,1.5),(20,3)],1): D[f'super_strength_{t}']=[attr('attack_damage',ad),attr('attack_knockback',kb)]
for t,(m,kr,ar) in enumerate([(0.6,0.5,4),(0.3,0.9,10),(0.05,1.0,20)],1): D[f'invulnerability_{t}']=[dmg_in(m),attr('knockback_resistance',kr),attr('armor',ar)]
for t,(m,j) in enumerate([(0.5,1),(1.0,2),(2.0,3)],1): D[f'super_speed_{t}']=[attr('movement_speed',m,'add_multiplied_base'),persist(('speed',j-1))]
D['barrage']=[attr('attack_speed',4.0),attr('attack_damage',5.0)]
D['regeneration_fast']=[persist(('regeneration',2))]
D['ki_blast']=[active('blaze_powder',40,proj('fire',2.0,8.0))]
D['energy_beam']=[active('end_rod',20,proj('air',4.0,14.0,1.5))]
D['time_stop']=[active('clock',600,aoe(32,eff('slowness',254,100),eff('weakness',254,100),eff('mining_fatigue',254,100)))]
D['telepathy']=[active('ender_eye',200,aoe(64,eff('glowing',0,600)))]
for k,v in D.items():
    for i,c in enumerate(v): (O/'powers'/(k if i==0 else f'{k}_{i+1}')).with_suffix('.json').write_text(json.dumps(c,indent=1))
# id | name | slot | tier | kind(P=passive works on mobs, A=active needs AI trigger) | source | keywords (regex-safe, lowercase)
E='neoorigins:'; N=NS+':'
P=[
('flight','Flight','mobility',3,'P',E+'draconic_flight','fly|flight|flies|flying|airborne|soar|levitat|winged'),
('glide','Gliding','mobility',1,'P',E+'elytrian_flight','glide|gliding|wings|winged'),
('spectral_flight','Spectral Flight','mobility',2,'P',E+'phantom_flight','ghost|spectr|ethereal|phantom'),
('levitation','Levitation','mobility',1,'A',E+'gravity_mage_levitation','levitat|hover|float|telekin'),
('super_speed_1','Super Speed I','mobility',1,'P',N+'super_speed_1','swift|fleet|fast|quick|speedster'),
('super_speed_2','Super Speed II','mobility',2,'P',N+'super_speed_2','super.?speed|blur|lightning.?fast|hypersonic'),
('super_speed_3','Super Speed III','mobility',3,'P',N+'super_speed_3','speed.?force|faster than light|speedster|run.{0,12}(light|sound)|vibrat'),
('dash','Dash','mobility',1,'A',E+'windwalker_gale_dash','dash|burst of speed|lunge|charge'),
('blink','Blink','mobility',2,'A',E+'enderian_teleport','teleport|blink|instant transmission|warp'),
('phase','Phase','mobility',3,'A',E+'voidwalker_active_phase','phase|intangib|pass through|wall.?walk'),
('super_strength_1','Super Strength I','offense',1,'P',N+'super_strength_1','strong|mighty|powerful|brawn|herculean'),
('super_strength_2','Super Strength II','offense',2,'P',N+'super_strength_2','super.?human strength|superhuman|crush|shatter|titanic strength'),
('super_strength_3','Super Strength III','offense',3,'P',N+'super_strength_3','super.?strength|move mountains|lift.{0,15}(planet|mountain)|limitless strength'),
('barrage','Barrage','offense',2,'P',N+'barrage','barrage|flurry|rapid.{0,10}(punch|strike|blow)|hundred.{0,10}fist|ora'),
('pressure_strike','Pressure-Point Strike','offense',2,'P',E+'qi_core_pressure','pressure.?point|nerve strike|meridian|death touch|hokuto'),
('vibrating_palm','Vibrating Palm','offense',2,'A',E+'qi_vibrating_palm','palm|vibrating|inner.?force|shockwave strike'),
('ki_blast','Ki Blast','offense',2,'A',N+'ki_blast','ki blast|energy blast|kamehameha|chi blast|spirit blast|aura blast'),
('energy_beam','Energy Beam','offense',3,'A',N+'energy_beam','beam|laser|heat.?vision|eye.?beam|optic blast|ray'),
('fireball','Fireball','offense',2,'A',E+'draconic_active_fireball','fireball|fire.?breath|flame|blaze|pyro'),
('freeze_breath','Freeze Aura','offense',2,'A',E+'frostborn_freeze_aura','freez|frost|ice|cryo|cold breath'),
('whirlwind','Whirlwind','offense',2,'A',E+'air_mage_whirlwind','whirlwind|cyclone|tornado|gale|wind blast'),
('gravity_repulse','Repulse','offense',2,'A',E+'gravity_mage_repulse','repel|repulse|force push|telekinetic blast|gravity'),
('flying_sword','Flying Sword','offense',3,'A',E+'qi_flying_sword','flying sword|sword qi|spirit blade|sword saint'),
('invulnerability_1','Tough Hide','defense',1,'P',N+'invulnerability_1','tough|hardy|thick.?skin|resilien'),
('invulnerability_2','Near Invulnerability','defense',2,'P',N+'invulnerability_2','bulletproof|impervious|invulnerab|unbreakable'),
('invulnerability_3','Invulnerability','defense',3,'P',N+'invulnerability_3','invulnerab|invincib|indestructible|immortal|cannot be (harmed|hurt)'),
('hard_body','Diamond Body','defense',2,'P',E+'golden_bell_diamond_body','iron body|diamond body|golden bell|steel skin|body of'),
('iron_shirt','Iron Shirt','defense',1,'P',E+'golden_bell_iron_shirt','iron shirt|armou?red skin|hardened'),
('regeneration','Regeneration','defense',2,'P',E+'verdant_apex_regeneration','regenerat|heal(s|ing)? (quickly|rapidly)|self.?heal|rapid heal'),
('regeneration_fast','Rapid Regeneration','defense',3,'P',N+'regeneration_fast','rapid regeneration|instant heal|heal.{0,10}wounds'),
('qi_heal','Meditative Healing','defense',1,'A',E+'qi_meditation_heal','meditat|inner peace|qi heal|restor'),
('immortal_body','Immortal Body','defense',2,'P',E+'jianxian_immortal_body','immortal|ageless|deathless|undying|no fall'),
('time_stop','Time Stop','utility',3,'A',N+'time_stop','time stop|stop(s|ped)? time|freez(e|es|ing) time|the world|chronos|temporal'),
('telepathy','Telepathy','utility',1,'A',N+'telepathy','telepath|mind.?read|read minds|psychic|sense'),
('invisibility','Invisibility','utility',2,'P',E+'class_rogue_stealth','invisib|unseen|vanish|cloak|stealth'),
('giant_size','Giant Size','utility',2,'P',E+'class_titan_size','giant|colossal|titan|grow.{0,10}(huge|giant)'),
('dragon_form','Dragon Form','utility',3,'A',E+'cave_dragon_form','shapeshift|dragon form|transform|beast form|polymorph'),
('ki_resource','Ki Reserve','utility',1,'P',E+'qi_resource','ki|chi|qi|aura|spirit energy|ki.?user'),
]
with open(O/'POWER_POOL.tsv','w') as f:
    comp=lambda x: ','.join(NS+':'+(k if i==0 else f'{k}_{i+1}') for k in [x[len(NS)+1:]] for i in range(len(D[k]))) if x.startswith(N) else x
    f.write('id\tname\tslot\ttier\tkind\tsource_power\tkeywords\n')
    for r in P: f.write('\t'.join(map(str,r[:5]+(comp(r[5]),)+r[6:]))+'\n')
# archetype grants: ordered by priority; the grant step takes the first N the NPC needs, ki_resource first when any ki power is granted.
A={
'superman_analog':['flight','super_strength_3','invulnerability_3','energy_beam','super_speed_2','freeze_breath','regeneration'],
'kenshiro_analog':['ki_resource','pressure_strike','barrage','hard_body','super_strength_2','vibrating_palm','super_speed_1'],
'goku_analog':['ki_resource','flight','ki_blast','energy_beam','super_strength_3','super_speed_2','blink','regeneration','qi_heal'],
'jotaro_analog':['barrage','super_strength_2','time_stop','invulnerability_1','super_speed_1','regeneration'],
'flash_analog':['super_speed_3','phase','dash','regeneration_fast','invulnerability_1'],
}
with open(O/'ARCHETYPE_GRANTS.tsv','w') as f:
    f.write('archetype\tpowers_in_priority_order\n')
    for k,v in A.items(): f.write(k+'\t'+','.join(v)+'\n')
ids={r[0] for r in P}; assert all(p in ids for v in A.values() for p in v)
print(len(P),'pool powers,',sum(len(v) for v in D.values()),'designed files')
