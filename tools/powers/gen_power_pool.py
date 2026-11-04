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
D={}  # designed power id -> list of component JSONs; scalable ones get 10 variants <id>_m1.._m10
SC={  # scalable id -> function(magnitude 1..10) -> components
 'super_strength':lambda m:[attr('attack_damage',2*m),attr('attack_knockback',round(0.3*m,2))],
 'invulnerability':lambda m:[dmg_in(round(max(0.02,1-0.098*m),3)),attr('knockback_resistance',round(m/10,2)),attr('armor',2*m)],
 'super_speed':lambda m:[attr('movement_speed',round(0.25*m,2),'add_multiplied_base'),persist(('speed',round(m*0.3)))],
 'regeneration':lambda m:[persist(('regeneration',min(4,(m-1)//2)))],
 'ki_blast':lambda m:[active('blaze_powder',40,proj('fire',2.0,2.0*m))],
 'energy_beam':lambda m:[active('end_rod',20,proj('air',4.0,2.5*m,1.5))],
}
for k,f in SC.items():
    for m in range(1,11): D[f'{k}_m{m}']=f(m)
D['barrage']=[attr('attack_speed',4.0),attr('attack_damage',5.0)]
D['time_stop']=[active('clock',600,aoe(32,eff('slowness',254,100),eff('weakness',254,100),eff('mining_fatigue',254,100)))]
D['telepathy']=[active('ender_eye',200,aoe(64,eff('glowing',0,600)))]
for k,v in D.items():
    for i,c in enumerate(v): (O/'powers'/(k if i==0 else f'{k}_{i+1}')).with_suffix('.json').write_text(json.dumps(c,indent=1))
# id | name | slot | tier | kind(P=passive works on mobs, A=active needs AI trigger) | source | keywords (regex-safe, lowercase)
E='neoorigins:'; N=NS+':'
# id | name | slot | magnitude ('1-10' scalable, '-' fixed) | kind(P passive works on mobs, A active needs a trigger) | source ({m} = magnitude) | keywords (regex, lowercase)
P=[
('flight','Flight','mobility','-','P',E+'draconic_flight','\\b(can|able to|capable of|power of|gift of) (fly|flight)\\b|\\b(flies|flying) (through|above|over|across|at)\\b|\\bsoars? (through|above)\\b|\\bsuperhuman flight\\b'),
('glide','Gliding','mobility','-','P',E+'elytrian_flight','\\bglid(e|es|ing) (on|through|above|over)\\b|\\bgliding wings\\b'),
('spectral_flight','Spectral Flight','mobility','-','P',E+'phantom_flight','\\bghostly flight\\b|\\bspectral flight\\b|\\bethereal flight\\b|\\bfloats? as a ghost\\b'),
('levitation','Levitation','mobility','-','A',E+'gravity_mage_levitation','\\blevitat(e|es|ing)\\b|\\bhovers? (in|above|over)\\b|\\btelekinetic levitation\\b'),
('super_speed','Super Speed','mobility','1-10','P',N+'super_speed_m{m}','\\bsuper.?speed\\b|\\bsuperhuman speed\\b|\\bspeedster\\b|\\bspeed force\\b|\\bmoves? (faster than|at the speed of) (sound|light)\\b|\\bhypersonic speed\\b|\\blightning.?fast reflexes\\b'),
('dash','Dash','mobility','-','A',E+'windwalker_gale_dash','\\bburst of speed\\b|\\bblinding dash\\b|\\bsudden dash\\b'),
('blink','Blink','mobility','-','A',E+'enderian_teleport','\\bteleport(s|ation)?\\b|\\binstant transmission\\b|\\bblinks? (across|to|away)\\b'),
('phase','Phase','mobility','-','A',E+'voidwalker_active_phase','\\bphas(e|es|ing) through\\b|\\bintangib(le|ility)\\b|\\bpasses? through (walls|solid)\\b'),
('super_strength','Super Strength','offense','1-10','P',N+'super_strength_m{m}','\\bsuper.?strength\\b|\\bsuperhuman strength\\b|\\bimmense(ly)? strong\\b|\\bunmatched strength\\b|\\bmove mountains\\b|\\bherculean strength\\b|\\btitanic strength\\b|\\bcrush(es)? (stone|steel|boulders|mountains)\\b'),
('barrage','Barrage','offense','-','P',N+'barrage','\\bbarrage of (punches|blows|strikes|fists)\\b|\\bflurry of (punches|blows|strikes)\\b|\\bhundred.{0,3}fist\\b|\\brapid.fire (punches|strikes|blows)\\b'),
('pressure_strike','Pressure-Point Strike','offense','-','P',E+'qi_core_pressure','\\bpressure.?points?\\b|\\bnerve strikes?\\b|\\bmeridian strikes?\\b|\\bdeath touch\\b|\\bhokuto\\b'),
('vibrating_palm','Vibrating Palm','offense','-','A',E+'qi_vibrating_palm','\\bvibrating palm\\b|\\bpalm strike\\b|\\binner.force strike\\b'),
('ki_blast','Ki Blast','offense','1-10','A',N+'ki_blast_m{m}','\\bki blasts?\\b|\\benergy blasts?\\b|\\bkamehameha\\b|\\bchi blasts?\\b|\\bspirit blasts?\\b|\\baura blasts?\\b'),
('energy_beam','Energy Beam','offense','1-10','A',N+'energy_beam_m{m}','\\benergy beams?\\b|\\beye beams?\\b|\\bheat vision\\b|\\boptic blasts?\\b|\\blaser (beam|eyes)\\b|\\bfires? beams? of\\b'),
('fireball','Fireball','offense','-','A',E+'draconic_active_fireball','\\bfireballs?\\b|\\bbreathes? fire\\b|\\bfire.breath\\b|\\bhurls? flames\\b'),
('freeze_breath','Freeze Aura','offense','-','A',E+'frostborn_freeze_aura','\\bfreezing breath\\b|\\bfrost breath\\b|\\bicy breath\\b|\\bfreeze aura\\b|\\bfreezes? (enemies|foes|water)\\b'),
('whirlwind','Whirlwind','offense','-','A',E+'air_mage_whirlwind','\\bwhirlwinds?\\b|\\bsummons? (a )?(cyclone|tornado)\\b|\\bwind blasts?\\b'),
('gravity_repulse','Repulse','offense','-','A',E+'gravity_mage_repulse','\\bforce push\\b|\\btelekinetic (blast|force|push)\\b|\\brepels? (enemies|foes|attackers)\\b|\\bgravity (blast|wave|manipulation)\\b'),
('flying_sword','Flying Sword','offense','-','A',E+'qi_flying_sword','\\bflying swords?\\b|\\bsword qi\\b|\\bspirit blades?\\b|\\bsword saint\\b'),
('invulnerability','Invulnerability','defense','1-10','P',N+'invulnerability_m{m}','\\binvulnerab(le|ility)\\b|\\binvincib(le|ility)\\b|\\bindestructible\\b|\\bimpervious to (damage|harm|weapons|bullets)\\b|\\bbulletproof\\b|\\bcannot be (harmed|hurt)\\b|\\bimpenetrable skin\\b'),
('hard_body','Diamond Body','defense','-','P',E+'golden_bell_diamond_body','\\biron body\\b|\\bdiamond body\\b|\\bgolden bell\\b|\\bsteel(en)? skin\\b|\\bbody of (iron|steel|diamond|stone)\\b'),
('iron_shirt','Iron Shirt','defense','-','P',E+'golden_bell_iron_shirt','\\biron shirt\\b|\\barmou?red skin\\b|\\bhardened skin\\b'),
('regeneration','Regeneration','defense','1-10','P',N+'regeneration_m{m}','\\bregenerat(e|es|ion|ing)\\b|\\bhealing factor\\b|\\bheals? (quickly|rapidly|instantly)\\b|\\bself.heal(ing)?\\b|\\brapid healing\\b'),
('qi_heal','Meditative Healing','defense','-','A',E+'qi_meditation_heal','\\bmeditative heal(ing)?\\b|\\bqi healing\\b|\\bheals? (through|by) meditation\\b'),
('immortal_body','Immortal Body','defense','-','P',E+'jianxian_immortal_body','\\bimmortal body\\b|\\bageless\\b|\\bdeathless\\b|\\bundying\\b'),
('time_stop','Time Stop','utility','-','A',N+'time_stop','\\bstops? time\\b|\\bstopping time\\b|\\btime.?stop\\b|\\bfreezes? time\\b|\\bfreezing time\\b|\\bhalts? time\\b'),
('telepathy','Telepathy','utility','-','A',N+'telepathy','\\btelepath(y|ic|ically)\\b|\\bmind.reading\\b|\\breads? (minds|thoughts)\\b'),
('invisibility','Invisibility','utility','-','P',E+'class_rogue_stealth','\\binvisib(le|ility)\\b|\\bturns? invisible\\b|\\bcloak of invisibility\\b'),
('giant_size','Giant Size','utility','-','P',E+'class_titan_size','\\bgrows? (to )?(giant|colossal|enormous|huge)\\b|\\bgiant size\\b|\\bgrows? into a giant\\b|\\bgrowth into a giant\\b'),
('dragon_form','Dragon Form','utility','-','A',E+'cave_dragon_form','\\bshapeshift(s|er|ing)?\\b|\\bshape.shift(s|er|ing)?\\b|\\bdragon form\\b|\\btransforms? into (a|an) (dragon|beast|wolf|bear)\\b|\\bbeast form\\b'),
('ki_resource','Ki Reserve','utility','-','P',E+'qi_resource','\\bki (user|master|energy|control|techniques?)\\b|\\bchi (master|energy|control)\\b|\\bqi (master|energy|control|cultivation)\\b|\\bcultivates? (ki|chi|qi)\\b|\\bspirit energy\\b'),
]
def comp(x):
    if not x.startswith(N): return x
    k=x[len(N):]; n=len(D[k.replace('{m}','1')])
    return ','.join(N+(k if i==0 else k+f'_{i+1}') for i in range(n))
with open(O/'POWER_POOL.tsv','w') as f:
    f.write('id\tname\tslot\tmagnitude\tkind\tsource_power\tkeywords\n')
    for r in P: f.write('\t'.join(r[:5]+(comp(r[5]),)+r[6:])+'\n')
# archetype grants: id[:magnitude] in priority order; the grant step takes the first N the NPC needs.
A={
'superman_analog':['flight','super_strength:9','invulnerability:9','energy_beam:7','super_speed:8','freeze_breath','regeneration:5'],
'kenshiro_analog':['ki_resource','pressure_strike','barrage','hard_body','super_strength:6','vibrating_palm','super_speed:4'],
'goku_analog':['ki_resource','flight','ki_blast:9','energy_beam:9','super_strength:9','super_speed:8','blink','regeneration:6','qi_heal'],
'jotaro_analog':['barrage','super_strength:7','time_stop','invulnerability:4','super_speed:4','regeneration:3'],
'flash_analog':['super_speed:10','phase','dash','regeneration:8','invulnerability:2'],
}
with open(O/'ARCHETYPE_GRANTS.tsv','w') as f:
    f.write('archetype\tpowers_in_priority_order\n')
    for k,v in A.items(): f.write(k+'\t'+','.join(v)+'\n')
ids={r[0]:r[3] for r in P}
for v in A.values():
    for e in v:
        i,_,m=e.partition(':'); assert i in ids and (ids[i]=='-')==(m=='') and (not m or 1<=int(m)<=10),e
print(len(P),'pool powers,',sum(len(v) for v in D.values()),'designed files')
