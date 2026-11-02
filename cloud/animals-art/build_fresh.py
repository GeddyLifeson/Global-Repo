"""All 35 skins: Blender AO bake + fresh Factorio-style paint.  python3 build_fresh.py BLENDER_PYTHON ENTITIES_DIR OUT [SCALE]"""
import json, subprocess, sys, pathlib, tempfile
from PIL import Image
from paint import paint

bpy_python, entities, out = sys.argv[1], pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
s = int(sys.argv[4]) if len(sys.argv) > 4 else 4
IDS = {'Elephantid': 'elephantid', 'Cervid': 'cervid', 'Equid': 'equid', 'Bovid': 'bovid', 'Canid': 'canid', 'GroundSloth': 'ground_sloth', 'Glyptodont': 'glyptodont'}
models = json.load(open('models.json'))
tmp = pathlib.Path(tempfile.mkdtemp())
for plan, i in IDS.items():
    (out / i).mkdir(parents=True, exist_ok=True)
    for sp in json.load(open(entities / f'{i}.json'))['species']:
        ao = tmp / f"{i}_{sp['name']}.png"
        subprocess.run([bpy_python, 'ao_bake.py', 'models.json', plan, str(sp['variant']), str(s), str(ao)], check=True, capture_output=True)
        paint(models[plan], plan, sp['name'], sp['variant'], Image.open(f"src16/{i}/{sp['name']}.png"), Image.open(ao), s).save(out / i / f"{sp['name']}.png")
        print(i, sp['name'], flush=True)
