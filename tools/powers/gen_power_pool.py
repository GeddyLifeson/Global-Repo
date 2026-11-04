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

 'time_stop':lambda m:[active('clock',1300-100*m,aoe(8+4*m,*[eff(e,254,20+20*m) for e in('slowness','weakness','mining_fatigue')]))],
 'telepathy':lambda m:[active('ender_eye',400-25*m,aoe(16+6*m,eff('glowing',0,100+60*m)))],
 'dash':lambda m:[{"type":"neoorigins:active_dash","cooldown_icon":"minecraft:breeze_rod","power":round(0.8+0.3*m,2),"cooldown_ticks":110-8*m,"allow_vertical":True}],
 'blink':lambda m:[{"type":"neoorigins:active_teleport","cooldown_icon":"minecraft:ender_pearl","range":float(8+6*m),"cooldown_ticks":220-15*m,"mode":"target"}],
 'phase':lambda m:[{"type":"neoorigins:active_phase","cooldown_icon":"minecraft:phantom_membrane","max_depth":2+2*m,"cooldown_ticks":220-14*m}],
 'levitation':lambda m:[active('feather',200-10*m,eff('levitation',m//4,40+20*m))],
 'fireball':lambda m:[active('fire_charge',110-7*m,proj('fire',1.6,2+1.5*m,2+0.3*m))],
 'freeze_breath':lambda m:[active('powder_snow_bucket',220-12*m,aoe(3+0.6*m,eff('slowness',1+m//2,60+20*m),{"type":"neoorigins:damage","amount":m*0.5,"source":{"name":"freeze"}}))],
 'whirlwind':lambda m:[active('breeze_rod',140-8*m,proj('air',1.8,1+m,3+0.5*m))],
 'gravity_repulse':lambda m:[active('echo_shard',160-9*m,aoe(3+0.7*m,eff('slowness',2,40+10*m),{"type":"neoorigins:damage","amount":1+0.7*m,"source":{"name":"magic"}}))],
 'vibrating_palm':lambda m:[active('blaze_rod',100-6*m,aoe(3+0.2*m,eff('weakness',m//3,60+10*m),{"type":"neoorigins:damage","amount":2*m,"source":{"name":"magic"}}))],
 'flying_sword':lambda m:[active('iron_sword',90-6*m,proj('air',3.0,2+2*m,1.2))],
 'qi_heal':lambda m:[active('golden_apple',300-15*m,eff('regeneration',m//3,60+20*m))],
 'barrage':lambda m:[attr('attack_speed',round(0.4*m,2)),attr('attack_damage',round(0.8*m,2))],
 'pressure_strike':lambda m:[{"type":"neoorigins:modify_damage","direction":"out","multiplier":round(1+0.06*m,2)}],
 'flight_boost':lambda m:[attr('flying_speed',round(0.1*m,2),'add_multiplied_base')],
 'boost_mobility':lambda m:[attr('movement_speed',round(0.04*m,2),'add_multiplied_base')],
 'boost_offense':lambda m:[attr('attack_damage',round(1.5*m,2))],
 'boost_defense':lambda m:[attr('armor',round(1.5*m,2)),attr('max_health',2*m)],
 'boost_utility':lambda m:[attr('follow_range',4*m)],}
for k,f in SC.items():
    for m in range(1,11): D[f'{k}_m{m}']=f(m)
# id | name | slot | tier | kind(P=passive works on mobs, A=active needs AI trigger) | source | keywords (regex-safe, lowercase)
E='neoorigins:'; N=NS+':'
# id | name | slot | magnitude ('1-10' scalable, '-' fixed) | kind(P passive works on mobs, A active needs a trigger) | source ({m} = magnitude) | keywords (regex, lowercase)
SA={'flight': '\\b(flies|flying|flew|fly|soars?|soaring|soared|winged|airborne|take flight|takes? to the (air|sky|skies)|on the wing|aloft)\\b', 'super_strength': '\\b(super.?strength|superhuman|(immense|incredible|great|enormous|tremendous|prodigious|brutal|unmatched|titanic|herculean|monstrous) strength|herculean|strength of (ten|a hundred|a thousand|giants|mountains|stars?)|strength to (split|shatter|move|crush|break)|(split|shatter|crush)s? (a )?(worlds?|mountains?|stars?|planets?|stone|steel|boulders)|move mountains)\\b', 'super_speed': '\\b(speedster|super.?speed|superhuman speed|(incredible|blinding|blazing|unmatched|tremendous) speed|lightning.speed|lightning.fast|moves? like lightning|swift as|faster than (sound|light|the eye|thought)|supersonic|hypersonic|speed force)\\b', 'invulnerability': '\\b(invulnerab\\w*|invincib\\w*|indestructible|impervious to \\w+|bulletproof|cannot be (harmed|hurt|killed|wounded|damaged|struck)|immune to (all|any|damage|harm|weapons|blades)|impenetrable (skin|hide|armou?r))\\b', 'regeneration': '\\b(regenerat\\w+|healing factor|heals? (quickly|rapidly|instantly|itself|wounds)|self.heal\\w*|rapid(ly)? heal\\w*)\\b', 'time_stop': '\\b(stops? time|stopping time|time.?stop|freez\\w+ time|halts? time|(command|control|manipulate)\\w* time)\\b', 'dragon_form': '\\b(shapeshift\\w*|shape.?shift\\w*|changes? (its |his |her |their )?(shape|form)|transforms? (in)?to|beast form|dragon form)\\b', 'energy_beam': '\\b(energy beams?|eye beams?|heat vision|optic blasts?|laser (beam|eyes)|fires? (a )?beams?|beam of (light|radiance|energy|fire|power|unlight|fury)|unleashes (a )?(scorching |searing |blinding )?beam|hurls? blazing (orbs|bolts))\\b', 'ki_resource': '\\b((ki|chi|qi) (user|master|energy|control|techniques?|blasts?|strikes?|arts?|warrior|fighter)s?|spirit energy|inner (energy|force)|aura (of|control|user)s?)\\b', 'levitation': '\\b(levitat\\w+|hovers?|floats? (in|above|over|through) the (air|sky))\\b', 'invisibility': '\\b(invisib\\w+|turns? invisible)\\b'}
W={'flight': '\\b(wings?|feathered|glides?|gliding|drifts? through the (sky|air)|sky.?bound)\\b', 'super_strength': '\\b(mighty|strong|strength|powerful|brute|brawn|hulking|towering|massive|great|formidable)\\b', 'super_speed': '\\b(swift\\w*|fast|faster|quick\\w*|speed|fleet\\w*|agile|lightning|darting|nimble)\\b', 'invulnerability': '\\b(unbreakable|tough|hardy|resilient|thick hide|armou?red|durable|enduring)\\b', 'regeneration': '\\b(mend\\w*|heal(s|ing|er|ers)?|restor\\w+|mend\\w*|recover\\w*|renew\\w*)\\b', 'time_stop': '\\b(flow of time|time itself|bends? time|temporal|chrono\\w*|time.?(lord|keeper|weaver|bender))\\b', 'dragon_form': '\\b(takes? the form of|assum\\w+ the form|transform\\w*|metamorph\\w*|polymorph\\w*|mimic\\w*|changeling)\\b', 'energy_beam': '\\b(beams?|lasers?|blasts?)\\b', 'ki_blast': '\\b(blasts?|bolts?)\\b', 'telepathy': '\\b(senses?|empath\\w+|sees? into|mind)\\b', 'fireball': '\\b(fire|flames?|burning|blazing)\\b', 'freeze_breath': '\\b(frost\\w*|ice|icy|frozen|cold)\\b', 'whirlwind': '\\b(wind\\w*|storm\\w*|gale)\\b', 'phase': '\\b(ghost\\w*|spectr\\w+|ethereal)\\b', 'blink': '\\b(vanish\\w*|appears?|disappears?)\\b', 'giant_size': '\\b(giant|towering|colossal|huge|vast)\\b', 'immortal_body': '\\b(eternal|enduring|long.lived|ancient)\\b', 'invisibility': '\\b(unseen|vanishes?|cloaked|shadow\\w*|stealth\\w*|hidden|sneak\\w*)\\b'}
RL={'ki_resource': 'Ki', 'pressure_strike': 'Martial|Ki', 'vibrating_palm': 'Martial|Ki', 'barrage': 'Martial|Ki', 'hard_body': 'Martial|Ki', 'flying_sword': 'Martial|Ki', 'ki_blast': 'Ki', 'qi_heal': 'Ki', 'blink': 'Ki', 'super_speed': 'Ki|Martial', 'super_strength': 'Martial|Ki'}
P=[
('flight','Flight','mobility','1-10','P',E+'draconic_flight','\\b(can|able to|capable of|power of|gift of) (fly|flight)\\b|\\b(flies|flying) (through|above|over|across|at)\\b|\\bsoars? (through|above)\\b|\\bsuperhuman flight\\b'),
('glide','Gliding','mobility','1-10','P',E+'elytrian_flight','\\bglid(e|es|ing) (on|through|above|over)\\b|\\bgliding wings\\b'),
('spectral_flight','Spectral Flight','mobility','1-10','P',E+'phantom_flight','\\bghostly flight\\b|\\bspectral flight\\b|\\bethereal flight\\b|\\bfloats? as a ghost\\b'),
('levitation','Levitation','mobility','1-10','A',E+'gravity_mage_levitation','\\blevitat(e|es|ing)\\b|\\bhovers? (in|above|over)\\b|\\btelekinetic levitation\\b'),
('super_speed','Super Speed','mobility','1-10','P',N+'super_speed_m{m}','\\bsuper.?speed\\b|\\bsuperhuman speed\\b|\\bspeedster\\b|\\bspeed force\\b|\\bmoves? (faster than|at the speed of) (sound|light)\\b|\\bhypersonic speed\\b|\\blightning.?fast reflexes\\b'),
('dash','Dash','mobility','1-10','A',E+'windwalker_gale_dash','\\bburst of speed\\b|\\bblinding dash\\b|\\bsudden dash\\b'),
('blink','Blink','mobility','1-10','A',E+'enderian_teleport','\\bteleport(s|ation)?\\b|\\binstant transmission\\b|\\bblinks? (across|to|away)\\b'),
('phase','Phase','mobility','1-10','A',E+'voidwalker_active_phase','\\bphas(e|es|ing) through\\b|\\bintangib(le|ility)\\b|\\bpasses? through (walls|solid)\\b'),
('super_strength','Super Strength','offense','1-10','P',N+'super_strength_m{m}','\\bsuper.?strength\\b|\\bsuperhuman strength\\b|\\bimmense(ly)? strong\\b|\\bunmatched strength\\b|\\bmove mountains\\b|\\bherculean strength\\b|\\btitanic strength\\b|\\bcrush(es)? (stone|steel|boulders|mountains)\\b'),
('barrage','Barrage','offense','1-10','P',N+'barrage','\\bbarrage of (punches|blows|strikes|fists)\\b|\\bflurry of (punches|blows|strikes)\\b|\\bhundred.{0,3}fist\\b|\\brapid.fire (punches|strikes|blows)\\b'),
('pressure_strike','Pressure-Point Strike','offense','1-10','P',E+'qi_core_pressure','\\bpressure.?points?\\b|\\bnerve strikes?\\b|\\bmeridian strikes?\\b|\\bdeath touch\\b|\\bhokuto\\b'),
('vibrating_palm','Vibrating Palm','offense','1-10','A',E+'qi_vibrating_palm','\\bvibrating palm\\b|\\bpalm strike\\b|\\binner.force strike\\b'),
('ki_blast','Ki Blast','offense','1-10','A',N+'ki_blast_m{m}','\\bki blasts?\\b|\\benergy blasts?\\b|\\bkamehameha\\b|\\bchi blasts?\\b|\\bspirit blasts?\\b|\\baura blasts?\\b'),
('energy_beam','Energy Beam','offense','1-10','A',N+'energy_beam_m{m}','\\benergy beams?\\b|\\beye beams?\\b|\\bheat vision\\b|\\boptic blasts?\\b|\\blaser (beam|eyes)\\b|\\bfires? beams? of\\b'),
('fireball','Fireball','offense','1-10','A',E+'draconic_active_fireball','\\bfireballs?\\b|\\bbreathes? fire\\b|\\bfire.breath\\b|\\bhurls? flames\\b'),
('freeze_breath','Freeze Aura','offense','1-10','A',E+'frostborn_freeze_aura','\\bfreezing breath\\b|\\bfrost breath\\b|\\bicy breath\\b|\\bfreeze aura\\b|\\bfreezes? (enemies|foes|water)\\b'),
('whirlwind','Whirlwind','offense','1-10','A',E+'air_mage_whirlwind','\\bwhirlwinds?\\b|\\bsummons? (a )?(cyclone|tornado)\\b|\\bwind blasts?\\b'),
('gravity_repulse','Repulse','offense','1-10','A',E+'gravity_mage_repulse','\\bforce push\\b|\\btelekinetic (blast|force|push)\\b|\\brepels? (enemies|foes|attackers)\\b|\\bgravity (blast|wave|manipulation)\\b'),
('flying_sword','Flying Sword','offense','1-10','A',E+'qi_flying_sword','\\bflying swords?\\b|\\bsword qi\\b|\\bspirit blades?\\b|\\bsword saint\\b'),
('invulnerability','Invulnerability','defense','1-10','P',N+'invulnerability_m{m}','\\binvulnerab(le|ility)\\b|\\binvincib(le|ility)\\b|\\bindestructible\\b|\\bimpervious to (damage|harm|weapons|bullets)\\b|\\bbulletproof\\b|\\bcannot be (harmed|hurt)\\b|\\bimpenetrable skin\\b'),
('hard_body','Diamond Body','defense','1-10','P',E+'golden_bell_diamond_body','\\biron body\\b|\\bdiamond body\\b|\\bgolden bell\\b|\\bsteel(en)? skin\\b|\\bbody of (iron|steel|diamond|stone)\\b'),
('iron_shirt','Iron Shirt','defense','1-10','P',E+'golden_bell_iron_shirt','\\biron shirt\\b|\\barmou?red skin\\b|\\bhardened skin\\b'),
('regeneration','Regeneration','defense','1-10','P',N+'regeneration_m{m}','\\bregenerat(e|es|ion|ing)\\b|\\bhealing factor\\b|\\bheals? (quickly|rapidly|instantly)\\b|\\bself.heal(ing)?\\b|\\brapid healing\\b'),
('qi_heal','Meditative Healing','defense','1-10','A',E+'qi_meditation_heal','\\bmeditative heal(ing)?\\b|\\bqi healing\\b|\\bheals? (through|by) meditation\\b'),
('immortal_body','Immortal Body','defense','1-10','P',E+'jianxian_immortal_body','\\bimmortal body\\b|\\bageless\\b|\\bdeathless\\b|\\bundying\\b'),
('time_stop','Time Stop','utility','1-10','A',N+'time_stop','\\bstops? time\\b|\\bstopping time\\b|\\btime.?stop\\b|\\bfreezes? time\\b|\\bfreezing time\\b|\\bhalts? time\\b'),
('telepathy','Telepathy','utility','1-10','A',N+'telepathy','\\btelepath(y|ic|ically)\\b|\\bmind.reading\\b|\\breads? (minds|thoughts)\\b'),
('invisibility','Invisibility','utility','1-10','P',E+'class_rogue_stealth','\\binvisib(le|ility)\\b|\\bturns? invisible\\b|\\bcloak of invisibility\\b'),
('giant_size','Giant Size','utility','1-10','P',E+'class_titan_size','\\bgrows? (to )?(giant|colossal|enormous|huge)\\b|\\bgiant size\\b|\\bgrows? into a giant\\b|\\bgrowth into a giant\\b'),
('dragon_form','Dragon Form','utility','1-10','A',E+'cave_dragon_form','\\bshapeshift(s|er|ing)?\\b|\\bshape.shift(s|er|ing)?\\b|\\bdragon form\\b|\\btransforms? into (a|an) (dragon|beast|wolf|bear)\\b|\\bbeast form\\b'),
('ki_resource','Ki Reserve','utility','1-10','P',E+'qi_resource','\\bki (user|master|energy|control|techniques?)\\b|\\bchi (master|energy|control)\\b|\\bqi (master|energy|control|cultivation)\\b|\\bcultivates? (ki|chi|qi)\\b|\\bspirit energy\\b'),
]
FULL={'time_stop','telepathy','dash','blink','phase','levitation','fireball','freeze_breath','whirlwind','gravity_repulse','vibrating_palm','flying_sword','qi_heal','barrage','pressure_strike'}
KEEP=('super_','invuln','regen','ki_blast','energy')  # already scalable designed powers, no base power
def src(r):
    i,base=r[0],r[5]
    if i in FULL: return N+i+'_m{m}'
    if i=='flight': return base+','+N+'flight_boost_m{m}'
    if i.startswith(KEEP): return base
    return base+','+N+i+'_boost_m{m}'
for r in P:
    if r[0] in FULL: [D.__setitem__(f'{r[0]}_m{m}',SC[r[0]](m)) for m in range(1,11)]
    elif r[0]!='flight' and not r[0].startswith(KEEP): [D.__setitem__(f'{r[0]}_boost_m{m}',SC['boost_'+r[2]](m)) for m in range(1,11)]
def comp(x):
    out=[]
    for part in x.split(','):
        if not part.startswith(N): out.append(part); continue
        k=part[len(N):]; n=len(D[k.replace('{m}','1')])
        out+=[N+(k if i==0 else k+f'_{i+1}') for i in range(n)]
    return ','.join(out)
for k,v in D.items():
    for i,c in enumerate(v): (O/'powers'/(k if i==0 else f'{k}_{i+1}')).with_suffix('.json').write_text(json.dumps(c,indent=1))
with open(O/'POWER_POOL.tsv','w') as f:
    f.write('id\tname\tslot\tmagnitude\tkind\tsource_power\tkeywords_strong\tkeywords_weak\trealms\n')
    for r in P: f.write('\t'.join(r[:5]+(comp(src(r)),SA.get(r[0],r[6]),W.get(r[0],''),RL.get(r[0],'')))+'\n')
# archetype grants: id[:magnitude] in priority order; the grant step takes the first N the NPC needs.
A={
'superman_analog':['flight:9','super_strength:9','invulnerability:9','energy_beam:7','super_speed:8','freeze_breath:7','regeneration:5','telepathy:2'],
'kenshiro_analog':['ki_resource:7','pressure_strike:9','barrage:8','hard_body:6','super_strength:6','vibrating_palm:7','super_speed:4'],
'goku_analog':['ki_resource:9','flight:8','ki_blast:9','energy_beam:9','super_strength:9','super_speed:8','blink:8','regeneration:6','qi_heal:6'],
'jotaro_analog':['barrage:8','super_strength:7','time_stop:4','invulnerability:4','super_speed:4','regeneration:3'],
'flash_analog':['super_speed:10','phase:7','dash:9','regeneration:8','invulnerability:2'],
}
with open(O/'ARCHETYPE_GRANTS.tsv','w') as f:
    f.write('archetype\tpowers_in_priority_order\n')
    for k,v in A.items(): f.write(k+'\t'+','.join(v)+'\n')
ids={r[0] for r in P}
for v in A.values():
    for e in v:
        i,_,m=e.partition(':'); assert i in ids and 1<=int(m)<=10,e
print(len(P),'pool powers,',sum(len(v) for v in D.values()),'designed files')
