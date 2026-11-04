# S6939 checks/wages_steps.py OUTDIR: RPG #259 wages on a live KubeJS server: village steps 1-4, company steps 1-3 (drives real functions through checks/wages_driver/zz_wagetest.js, copied into a temp kubejs dir; edit RPG path/paths below).
import sys, glob, json, pathlib, re
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))
from lane import Lane
RPG='/home/user/diaithirrpg/content/economy/'
JARS = sorted(glob.glob('/tmp/claude-0/econlib/*.jar')) + ['/mnt/project-files/builds/ages-diaithir2/diaithir-ages-neoforge-26.1.2-0.1.0-diaithir.2.jar','/mnt/project-files/vehicles-test/diaithir-carts-neoforge-26.1.2-1.0.0.jar','/mnt/project-files/Immersive_Vehicles-26.1-24.0.0-diaithir.2.jar']
out=sys.argv[1]; rep={}
with Lane('wages', JARS, server_dirs={'kubejs':'/tmp/claude-0/wt_kubejs/kubejs','config':RPG+'config'}, srv_xmx='3G', out=out) as L:
    S=L.server_cmd
    def step(name, cmd, w=3):
        r=[l for l in S(cmd,w) if '[wt]' in l or 'economy' in l or 'ERROR' in l]
        rep[name]=r; print(name, *[x[-300:] for x in r], sep='\n  ')
    S('forceload add -16 -16 16 16',3); S('setworldspawn 0 -60 0',1)
    for i in range(3): S('summon minecraft:villager 0 -60 %d {NoAI:1b,PersistenceRequired:1b,VillagerData:{profession:"minecraft:farmer",level:1,type:"minecraft:plains"}}'%i,1)
    S('summon minecraft:villager 3 -60 0 {NoAI:1b,PersistenceRequired:1b,VillagerData:{profession:"minecraft:armorer",level:1,type:"minecraft:plains"}}',1)
    step('T types','wt types')
    S('difficulty easy',1); step('P probe (fresh villager, no strike set)','wt probe')
    import sys as _s; _s.exit(0) if False else None
    step('V1 setup','wt village_setup')
    step('V2 week1','wt week'); step('V2 week2','wt week'); step('V2 keepers','wt keepers')
    step('V3 week3','wt week')
    step('V4 week4','wt week',5); step('V4 rebels','execute as @e[tag=wage_rebel] run say REBEL',3)
    step('V4 villagers left','execute as @e[type=minecraft:villager] run say V',3)
    step('V4 manual summon (script form)','summon minecraft:vindicator 0 -60 0 {CustomName:\'{"text":"Unpaid Farmer"}\',PersistenceRequired:1b,Tags:["wage_rebel"]}',3)
    S('summon minecraft:villager 0 -60 5 {NoAI:1b,PersistenceRequired:1b,VillagerData:{profession:"minecraft:mason",level:1,type:"minecraft:plains"}}',1)
    step('C1 setup','wt company_setup')
    step('C2 week1','wt week'); step('C2 week2','wt week'); step('C2 state','wt company_state')
    step('C3 pay','wt company_pay'); step('C3 week','wt week'); step('C3 state','wt company_state')
    rep['revolt_line']=L.log_lines('server', r'\[economy\].*revolt')
    rep['script_errors']=L.log_lines('server', r'KubeJS Server/\]: server_scripts|with \d+ errors')
json.dump(rep,open(out+'/wages_steps.json','w'),indent=1)
print('REVOLT LINE', rep['revolt_line']); print('SCRIPT', *rep['script_errors'], sep='\n ')
