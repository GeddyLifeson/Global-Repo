"""Creature variants left over after the main batches (the entity lane's list): baby, tame and angry skins, villager biome and
job outfits, coat variants, and the odd mod mob. Each skin takes the model and materials of an approved sibling in its own
folder when its texels fit that model; otherwise the best-fitting model of its namespace (or vanilla's), as in auto.py.

    python3 lane6.py BLENDER_PYTHON LAYERS_JSON TEX_ROOT OUT LIST_JSON SIBLINGS_JSON [--list]
LAYERS_JSON holds every layer as '<namespace>:<Layer>'; SIBLINGS_JSON maps an approved skin path ('assets/ns/textures/entity/...')
to [layer, hide, rules, hooves]; LIST_JSON is the lane list ([namespace, 'entity/...png'] pairs) already cut to creatures.
"""
import json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image
from auto import NAMES, PARTS, score, named
from vanilla import run

SKIP = (r'spit|stinger|creeper_armor|exploding|evoker_fangs|color_palettes|/markers/|sage_chest|_collar|_saddle|/saddle|'
        r'1bit_elite_blaze_(sword|core)|lightwell|daemonium_animaris_charging|old_zombie_piglin|guardian_familiar_(christmas|tree)|controlled_zombie|slimebeetle|terracube|wingnis|blook|moa_baby_base|bee_golem_flash')
VILLAGER = r'(^|/)(villager|zombie_villager|wandering_trader)/'
WORDS = r'wolf|horse|slime|zombie|cow|pig|chicken|illager|pillager|skeleton|spider'


def fits(L, k, img):
    return score(L[k], img) if k in L else -1


def inside(layer, img):
    """Share of the skin's painted texels that land on the model's faces: near 1 for an overlay drawn for that model."""
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
    return (a & m).sum() / max(a.sum(), 1)


def babies(L, key):
    """The baby model beside an adult one, if the game has it ('AdultWolfModel' -> 'BabyWolfModel')."""
    ns, cls = key.split(':', 1); c = cls.split('#')[0].replace('Adult', '')
    return [k for k in L if k.startswith(f'{ns}:Baby{c}')]


def table(layers_json, tex_root, list_json, sib_json):
    L = json.load(open(layers_json)); sib = json.load(open(sib_json)); out = {}; miss = []
    uniq = lambda items: list({json.dumps(v): v for k, v in items}.values())
    for ns, p in json.load(open(list_json)):
        rel = f'assets/{ns}/textures/{p[:-4]}'
        if re.search(SKIP, rel):
            continue
        img = np.asarray(Image.open(Path(tex_root) / f'{rel}.png').convert('RGBA'))
        folder, name = rel.rsplit('/', 1)
        near = uniq((k, v) for k, v in sib.items() if k.rsplit('/', 1)[0] == folder)
        if len({v[0] for v in near}) > 3:   # a flat folder of unrelated mobs: only a sibling that shares a word with this skin counts
            words = {w for w in re.split(r'[_\-\d]+', name) if len(w) > 2}
            near = uniq((k, v) for k, v in sib.items() if k.rsplit('/', 1)[0] == folder
                        and words & {w for w in re.split(r'[_\-\d]+', k.rsplit('/', 1)[1]) if len(w) > 2})
        if not near:   # an overlay variant of an approved skin elsewhere in the mod: 'guard_steve' for 'guard_steve_desert'
            pre = [(len(k.rsplit('/', 1)[1]), v) for k, v in sib.items() if k.startswith(f'assets/{ns}/') and name.startswith(k.rsplit('/', 1)[1])]
            near = [max(pre, key=lambda x: x[0])[1]] if pre else []
        if not near and ns != 'minecraft':   # a mod's own wolf or cow drawn on vanilla's model
            w = re.findall(WORDS, rel.split('/textures/')[1])
            near = uniq((k, v) for k, v in sib.items() if w and k.startswith(f'assets/minecraft/textures/entity/{w[-1]}/'))
        opts = [(v[0], v) for v in near] + [(b, v) for v in near for b in (babies(L, v[0]) if 'baby' in name else [])]
        best = max(opts, key=lambda o: (fits(L, o[0], img) >= 0.45 or (o[0] in L and inside(L[o[0]], img) >= 0.9), fits(L, o[0], img)), default=None)
        kin = best[1] if best else None
        if '/entity/player/' in rel:   # the default player skins (wide and slim arms share the player layout)
            layer, hide, rules, hooves = 'minecraft:PlayerModel#createMesh', '-', [(r'(^|/)head', 'skin'), (r'.', 'skin|cloth')], False
        elif re.search(VILLAGER, rel):   # biome, job and badge overlays: always on the villager body
            zombie, baby = 'zombie' in rel, 'baby' in rel
            layer = f"minecraft:{'Baby' if baby else ''}{'ZombieVillager' if zombie else 'Villager'}Model#" + ('createBodyLayer' if zombie else 'createBodyModel')
            hide, rules, hooves = '-', [(r'(^|/)(head|nose)', 'skin'), (r'.', 'skin|cloth')], False
        elif best and best[0] in L and (fits(L, best[0], img) >= 0.45 or inside(L[best[0]], img) >= 0.9):
            layer = best[0]; _, hide, rules, hooves = kin
        else:
            pool = [k for k in L if k.split(':')[0] == ns or k.startswith('minecraft:')]
            cands = [(score(L[k], img) + (0.2 if named(k, rel) else 0), named(k, rel), k) for k in pool]
            s, by_name, layer = max(cands, default=(0, False, None))
            named_fit = [k for k in pool if named(k, rel) and inside(L[k], img) >= 0.95 and score(L[k], img) > 0.1]
            if named_fit and (layer is None or s < (0.5 if by_name else 0.8)):
                layer = max(named_fit, key=lambda k: score(L[k], img)); s = 1
            if layer is None or s < (0.5 if by_name else 0.8):
                miss.append((rel, round(float(s), 2), layer)); continue
            if kin:   # a baby or alternate pose keeps its parent's materials
                hide, rules, hooves = '-', kin[2], kin[3]
            else:
                body = next((m for rx, m in NAMES if re.search(rx, rel.lower())), 'fur')
                hide, hooves = '-', False
                rules = PARTS + ([(r'(^|/)head', 'skin')] if '|' in body else []) + [(r'.', body)]
        if layer not in L:
            miss.append((rel, 0, layer)); continue
        key = f'{layer}|{hide}|{json.dumps(rules)}|{hooves}'
        out.setdefault(key, [layer, [], hide, [tuple(r) for r in rules], hooves])[1].append(rel)
    return {re.sub(r'\W+', '_', v[0]) + f'_{i}': tuple(v) for i, v in enumerate(out.values())}, miss

if __name__ == '__main__':
    blender, layers_json, tex, outdir, lst, sibs = sys.argv[1:7]
    t, miss = table(layers_json, tex, lst, sibs)
    if '--list' in sys.argv:
        for k, v in t.items():
            print(k, len(v[1]), [s.split('/')[-1] for s in v[1]][:6], v[3][-1][1] if v[3] else 'default')
        print('unmatched', len(miss)); [print(' ', m) for m in miss]
        sys.exit()
    run(t, blender, layers_json, tex, outdir, list(t))
