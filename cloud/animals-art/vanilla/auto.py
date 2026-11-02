"""The long tail of mod mobs: each skin is matched to its model automatically, the locked creature method paints it.

    python3 auto.py BLENDER_PYTHON LAYERS_JSON TEX_ROOT OUT [--list]
LAYERS_JSON holds every mod's layers as '<namespace>:<Layer>' (ExportLayers.java on each jar). A skin goes to the layer of
its own namespace whose UV faces best match the skin's painted texels (size must fit, 1x, 2x or 4x). Materials come from
the creature's name (fish get scales, golems stone, robots metal, people skin and cloth) and from part names.
"""
import json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image
from vanilla import run

SKIP = (r'equipment|armor|/chest|boat|sign|banner|_eyes|emissive|glow|overlay|projectile|magic_circle|rocket|crib|/rod/|hdpe|flag|globe|'
        r'black_hole|lander|rover|launch|pumpjack|tackle|/base/|/dye/|_e\.png|shield|crackiness|beam|breath|spark|wind|_layer|bucket|'
        r'injector|forbiddenomicon|jar|skull|book|kapow|alarm|jetpack|scuba|free_runners|flamethrower|disassembler|energy_cube|'
        r'pixie|mca/textures/entity/villager|millager/textures/entity/villager/|transporter|flame|buckler|tnt|hook|bobber|neptune|space_suit|gravity')
NAMES = [   # creature name -> body material
    (r'jelly', 'gel'),
    (r'fish|cod|salmon|tuna|bass|trout|pike|carp|catfish|gar|perch|bluegill|minnow|piranha|arapaima|tambaqui|capitaine|synodontis|'
     r'muskellunge|halibut|pollock|herring|smallmouth|brown_trout|red_grouper|boulti|bayad|tilapia|blackfish|pink_salmon|rainbow|'
     r'starshell|goldfish|leech|jellyfish', 'feather'),
    (r'golem|crawler', 'stone'), (r'robit|mech|sentry', 'metal'), (r'werewolf|beaver|deer|goat|chimera|bat_|wolf', 'shaggy'),
    (r'bee', 'fur'), (r'ghost|soul|spirit|jelly|slime', 'gel'), (r'parasite|libelle|beetle|crawler', 'chitin'),
    (r'dragon|cthulhu|beholder|nautilus|turtle', 'shell'),
    (r'guard|villager|millager|pillager|vindicator|evoker|trader|alien|blacksmith|fairy|mummy|headless|reaper|steve|human', 'skin|cloth'),
]
PARTS = [(r'wing', 'wing'), (r'horn|tusk|claw|beak|antler|stinger|tooth|teeth|fang', 'horn'), (r'hair|mane|beard', 'shaggy'),
         (r'(^|/)head', 'skin')]


def score(layer, img):
    """How well a layer's UV faces fit a skin's painted texels (F1 of coverage)."""
    if not layer['tw'] or not layer['th']:
        return 0.0
    k = img.shape[1] / layer['tw']
    if k not in (1, 2, 4) or img.shape[0] != layer['th'] * k:
        return 0.0
    m = np.zeros(img.shape[:2], bool)
    for f in layer['faces']:
        us = [v[3] * k for v in f['v']]; vs = [v[4] * k for v in f['v']]
        m[int(min(vs)):int(max(vs)), int(min(us)):int(max(us))] = True
    a = img[..., 3] > 0
    if not a.any() or not m.any():
        return 0.0
    p = (a & m).sum() / m.sum(); r = (a & m).sum() / a.sum()
    return 2 * p * r / (p + r + 1e-9)


def named(key, rel):
    """Does the skin's path share a word with the model's class name?"""
    words = {w.lower() for w in re.findall(r'[A-Z][a-z]+', key.split(':')[1].split('#')[0])} - {'Model', 'model', 'familiar', 'entity', 'base', 'layer', 'create', 'body', 'renderer', 'events', 'client', 'handler'}
    return any(w in rel.lower() for w in words if len(w) > 2)


def table(layers_json, tex_root):
    L = json.load(open(layers_json)); root = Path(tex_root); out = {}
    for png in sorted(root.glob('assets/*/textures/entity/**/*.png')):
        rel = str(png.relative_to(root))[:-4]
        if re.search(SKIP, rel + '.png'):
            continue
        ns = rel.split('/')[1]
        img = np.asarray(Image.open(png).convert('RGBA'))
        cands = [(score(v, img) + (0.2 if named(k, rel) else 0), named(k, rel), k) for k, v in L.items() if k.split(':')[0] == ns]
        if 'productivebees' == ns:   # every bee skin uses the vanilla bee layout
            cands = [(score(L['productivebees:VanillaBee'], img), True, 'productivebees:VanillaBee')]
        if not cands:
            continue
        best, by_name, key = max(cands)
        if best < (0.55 if by_name else 0.85):
            continue
        name = rel.lower()
        body = next((m for rx, m in NAMES if re.search(rx, name)), 'fur')
        rules = PARTS + ([(r'(^|/)head', 'skin')] if '|' in body else []) + [(r'.', body)]
        mob = f'{ns}:{Path(rel).parent.name}/{Path(rel).name}'
        out.setdefault(key, ('', [], '-', rules, False))
        out[key][1].append(rel)
    # one entry per layer; its rules from the first skin's name
    return {k.replace(':', '_').replace('#', '_'): (k, v[1], v[2], v[3], v[4]) for k, v in out.items()}


if __name__ == '__main__':
    blender, layers_json, tex, outdir = sys.argv[1:5]
    t = table(layers_json, tex)
    if '--list' in sys.argv:
        for k, v in t.items():
            print(k, len(v[1]), [s.split('/')[-1] for s in v[1]][:8], v[3][-1][1])
        sys.exit()
    run(t, blender, layers_json, tex, outdir, list(t))
