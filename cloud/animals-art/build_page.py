import json, base64, sys
R = '/home/user/geddylifeson/diaithir-ports/src/main/resources'
styled, dest = sys.argv[1], sys.argv[2]
m = json.load(open('models.json')); mo = json.load(open('models_orig.json'))
lang = json.load(open(R + '/assets/untamedwilds/lang/en_us.json'))
ids = {'Elephantid':'elephantid','Cervid':'cervid','Equid':'equid','Bovid':'bovid','Canid':'canid','GroundSloth':'ground_sloth','Glyptodont':'glyptodont'}
b64 = lambda p: 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
out = []
for k, i in ids.items():
    d = json.load(open(f'{R}/data/untamedwilds/entities/{i}.json'))
    sp = [dict(name=lang.get(f"entity.untamedwilds.{i}_{s['name']}", s['name']), sci=lang.get(f"entity.untamedwilds.{i}_{s['name']}.sciname", ''), v=s['variant'], scale=s.get('scale', 1),
               tex=b64(f"{styled}/{i}/{s['name']}.png"), old=b64(f"{R}/assets/untamedwilds/textures/entity/{i}/{s['name']}.png")) for s in d['species']]
    out.append(dict(id=i, plan=lang.get(f'entity.untamedwilds.{i}', k), model=m[k], oldModel=mo[k], species=sp, note='shape reworked: heavier hips, longer head, tail, claws' if k == 'GroundSloth' else ''))
open(dest, 'w').write(open('template.html').read().replace('__DATA__', json.dumps(out, separators=(',', ':'))))
