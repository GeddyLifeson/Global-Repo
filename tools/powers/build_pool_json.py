# S6965 build_pool_json.py: POWER_POOL.tsv to the pack's pool.json (pool id -> source power ids with {m}, kind, mob emulation for active powers).
# Run: python3 -I build_pool_json.py POWER_POOL.tsv OUT_pool.json. An active power with no row in ACT stops the run.
import csv,json,sys
ACT={
'levitation':{'k':'self','e':'levitation','a':0,'t':100,'cd':400},
'dash':{'k':'self','e':'speed','a':4,'t':40,'cd':200},
'blink':{'k':'blink','range':24,'cd':160},
'phase':{'k':'self','e':'resistance','a':3,'t':60,'cd':300},
'vibrating_palm':{'k':'ray','range':4,'dmg':10,'cd':100,'p':'minecraft:crit'},
'ki_blast':{'k':'ray','range':24,'dmg':8,'cd':80,'p':'minecraft:flame'},
'energy_beam':{'k':'ray','range':40,'dmg':14,'cd':100,'p':'minecraft:end_rod'},
'fireball':{'k':'ray','range':24,'dmg':8,'cd':100,'fire':5,'p':'minecraft:flame'},
'freeze_breath':{'k':'aoe','r':8,'e':'slowness','a':2,'t':100,'cd':200,'p':'minecraft:snowflake'},
'whirlwind':{'k':'aoe','r':6,'e':'levitation','a':1,'t':40,'cd':160,'p':'minecraft:cloud'},
'gravity_repulse':{'k':'aoe','r':6,'e':'slowness','a':1,'t':40,'push':1.5,'cd':160,'p':'minecraft:poof'},
'flying_sword':{'k':'ray','range':20,'dmg':12,'cd':120,'p':'minecraft:sweep_attack'},
'qi_heal':{'k':'self','e':'regeneration','a':2,'t':100,'cd':300},
'time_stop':{'k':'aoe','r':32,'e':'slowness','a':254,'t':100,'cd':600,'p':'minecraft:portal'},
'telepathy':{'k':'aoe','r':64,'e':'glowing','a':0,'t':600,'cd':200},
'dragon_form':{'k':'self','e':'strength','a':3,'t':200,'cd':600},
}
pool={}
for r in csv.DictReader(open(sys.argv[1],encoding='utf-8'),delimiter='\t'):
    d={'sources':r['source_power'].split(','),'slot':r['slot'],'kind':r['kind']}
    if r['kind']=='A':
        if r['id'] not in ACT: sys.exit('no mob emulation for active power '+r['id'])
        d['mob']=ACT[r['id']]
    pool[r['id']]=d
json.dump(pool,open(sys.argv[2],'w'),indent=1); print(len(pool),'pool powers')
