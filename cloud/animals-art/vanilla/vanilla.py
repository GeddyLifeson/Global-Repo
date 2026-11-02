"""Paint vanilla mob skins fresh at 64x (4x), the locked Diaithir creature method, from ExportLayers.java polygons.

    python3 vanilla.py BLENDER_PYTHON LAYERS_JSON VANILLA_TEXTURES_DIR OUT_DIR [mob ...]
Each mob: bake AO on its own UVs (poly_ao.py), paint every face as its own picture (paint.py materials), keep the
original face features (eyes, nostrils, mouth) as crisp painted marks, then grade. The old skin sets soft colours only.
"""
import json, re, subprocess, sys, zlib
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paint import paint_face, grade, soft, blur

DEPTH = 1.35   # stronger relief than the Untamed Wilds set: vanilla boxes are bigger and flatter, so the surface must carry the detail

HERE = Path(__file__).resolve().parent
HOOVES = r'leg'
# mob: layer, textures, hidden parts, [(regex on 'part#cube', material)], hooves on the legs
MOBS = {
    'cow': ('CowModel#createBodyLayer', ['cow/cow_temperate', 'cow/cow_cold@ColdCowModel#createBodyLayer', 'cow/cow_warm@WarmCowModel#createBodyLayer', 'cow/mooshroom_red', 'cow/mooshroom_brown'], '-',
            [(r'/head#[23]', 'horn'), (r'/body#1', 'skin')], True),
    'pig': ('PigModel#createBodyLayer', ['pig/pig_temperate', 'pig/pig_cold@ColdPigModel#createBodyLayer', 'pig/pig_warm'], '-', [(r'.', 'skin')], True),
    'sheep': ('SheepModel#createBodyLayer', ['sheep/sheep'], '-', [(r'/head#0', 'skin')], True),
    'sheep_wool': ('SheepFurModel#createFurLayer', ['sheep/sheep_wool'], '-', [(r'.', 'wool')], False),
    'chicken': ('AdultChickenModel#createBodyLayer', ['chicken/chicken_temperate', 'chicken/chicken_cold@ColdChickenModel#createBodyLayer', 'chicken/chicken_warm'], '-',
                [(r'beak|_leg', 'horn'), (r'red_thing', 'skin'), (r'.', 'feather')], False),
    'horse': ('AbstractEquineModel#createBodyMesh', ['horse/horse_brown', 'horse/horse_white', 'horse/horse_black', 'horse/horse_chestnut',
              'horse/horse_creamy', 'horse/horse_darkbrown', 'horse/horse_gray', 'horse/donkey@DonkeyModel#createBodyLayer@1', 'horse/mule@DonkeyModel#createBodyLayer@1'], r'chest',
              [(r'mane|tail', 'shaggy')], True),
    'wolf': ('AdultWolfModel#createBodyLayer', ['wolf/wolf', 'wolf/wolf_ashen', 'wolf/wolf_black', 'wolf/wolf_chestnut', 'wolf/wolf_rusty',
             'wolf/wolf_snowy', 'wolf/wolf_spotted', 'wolf/wolf_striped', 'wolf/wolf_woods'], '-', [(r'upper_body|tail', 'shaggy')], False),
    'goat': ('GoatModel#createBodyLayer', ['goat/goat'], '-', [(r'horn', 'horn'), (r'/head#2|/body#1', 'shaggy')], True),
    'llama': ('LlamaModel#createBodyLayer', ['llama/llama_brown', 'llama/llama_creamy', 'llama/llama_gray', 'llama/llama_white'], r'chest', [(r'.', 'shaggy')], True),
    'polar_bear': ('PolarBearModel#createBodyLayer', ['bear/polarbear'], '-', [(r'.', 'shaggy')], False),
    'fox': ('AdultFoxModel#createBodyLayer', ['fox/fox', 'fox/fox_snow'], '-', [(r'tail', 'shaggy')], False),
    'rabbit': ('AdultRabbitModel#createBodyLayer', ['rabbit/rabbit_brown', 'rabbit/rabbit_white', 'rabbit/rabbit_black', 'rabbit/rabbit_gold',
               'rabbit/rabbit_salt', 'rabbit/rabbit_white_splotched'], '-', [], False),
    'cat': ('AdultFelineModel#createBodyMesh', ['cat/cat_tabby', 'cat/ocelot', 'cat/cat_black', 'cat/cat_calico', 'cat/cat_siamese', 'cat/cat_red',
            'cat/cat_white', 'cat/cat_british_shorthair', 'cat/cat_persian', 'cat/cat_ragdoll', 'cat/cat_jellie', 'cat/cat_all_black'], '-', [], False),
    'panda': ('PandaModel#createBodyLayer', ['panda/panda', 'panda/panda_brown'], '-', [(r'.', 'shaggy')], False),
    'camel': ('AdultCamelModel#createBodyLayer', ['camel/camel'], r'saddle|bridle|reins', [(r'hump', 'shaggy')], False),
    'armadillo': ('AdultArmadilloModel#createBodyLayer', ['armadillo/armadillo'], r'^/cube$', [(r'/body#|tail', 'shell'), (r'ear', 'hide'), (r'.', 'hide')], False),
    'turtle': ('AdultTurtleModel#createBodyLayer', ['turtle/turtle'], r'egg_belly', [(r'/body#0', 'shell'), (r'.', 'skin')], False),
    'frog': ('FrogModel#createBodyLayer', ['frog/frog_temperate', 'frog/frog_cold', 'frog/frog_warm'], r'tongue|croaking', [(r'.', 'skin')], False),
    'sniffer': ('SnifferModel#createBodyLayer', ['sniffer/sniffer'], '-', [(r'nose|mouth', 'hide'), (r'.', 'shaggy')], False),
    'bee': ('AdultBeeModel#createBodyLayer', ['bee/bee'], r'stinger', [(r'wing', 'wing'), (r'antenna|leg', 'horn'), (r'.', 'fur')], False),
    'parrot': ('ParrotModel#createBodyLayer', ['parrot/parrot_red_blue', 'parrot/parrot_blue', 'parrot/parrot_green', 'parrot/parrot_yellow_blue', 'parrot/parrot_grey'],
               '-', [(r'beak|feather$', 'horn'), (r'leg', 'horn'), (r'.', 'feather')], False),
    'bat': ('BatModel#createBodyLayer', ['bat/bat'], '-', [(r'wing', 'hide')], False),
    'axolotl': ('AdultAxolotlModel#createBodyLayer', ['axolotl/axolotl_wild', 'axolotl/axolotl_lucy', 'axolotl/axolotl_gold', 'axolotl/axolotl_cyan', 'axolotl/axolotl_blue'],
                '-', [(r'gills', 'wing'), (r'.', 'skin')], False),
}
H = r'/(hat|jacket|left_sleeve|right_sleeve|left_pants|right_pants)$'   # overlay shells: left out of the AO bake
MONSTERS = {
    'zombie': ('HumanoidModel#createMesh', ['zombie/zombie', 'zombie/husk'], H, [(r'head', 'skin'), (r'.', 'skin|cloth')], False),
    'drowned': ('DrownedModel#createBodyLayer', ['zombie/drowned'], H, [(r'head', 'skin'), (r'.', 'skin|cloth')], False),
    'skeleton': ('SkeletonModel#createBodyLayer', ['skeleton/skeleton', 'skeleton/stray', 'skeleton/wither_skeleton', 'skeleton/bogged'], H,
                 [(r'.', 'bone')], False),
    'creeper': ('CreeperModel#createBodyLayer', ['creeper/creeper'], '-', [(r'.', 'skin')], False),
    'spider': ('SpiderModel#createSpiderBodyLayer', ['spider/spider', 'spider/cave_spider'], '-', [(r'leg', 'chitin'), (r'.', 'fur')], False),
    'enderman': ('EndermanModel#createBodyLayer', ['enderman/enderman'], H, [(r'.', 'skin')], False),
    'slime': ('SlimeModel#createOuterBodyLayer', ['slime/slime'], '-', [(r'.', 'gel')], False),
    'magma_cube': ('MagmaCubeModel#createBodyLayer', ['slime/magmacube'], '-', [(r'.', 'stone')], False),
    'blaze': ('BlazeModel#createBodyLayer', ['blaze/blaze'], '-', [(r'head', 'stone'), (r'.', 'metal')], False),
    'ghast': ('GhastModel#createBodyLayer', ['ghast/ghast', 'ghast/ghast_shooting'], '-', [(r'.', 'skin')], False),
    'phantom': ('PhantomModel#createBodyLayer', ['phantom/phantom'], '-', [(r'wing', 'wing'), (r'.', 'hide')], False),
    'witch': ('WitchModel#createBodyLayer', ['witch/witch'], r'jacket', [(r'hat', 'cloth'), (r'head|nose', 'skin'), (r'.', 'skin|cloth')], False),
    'illager': ('IllagerModel#createBodyLayer', ['illager/pillager', 'illager/vindicator', 'illager/evoker', 'illager/illusioner'], r'^/(left|right)_arm$|hat',
                [(r'head|nose', 'skin'), (r'.', 'skin|cloth')], False),
    'ravager': ('RavagerModel#createBodyLayer', ['illager/ravager'], '-', [(r'horn', 'horn'), (r'.', 'hide')], True),
    'vex': ('VexModel#createBodyLayer', ['illager/vex'], '-', [(r'wing', 'wing'), (r'.', 'skin')], False),
    'guardian': ('GuardianModel#createBodyLayer', ['guardian/guardian', 'guardian/guardian_elder'], '-', [(r'spike', 'horn'), (r'.', 'chitin')], False),
    'silverfish': ('SilverfishModel#createBodyLayer', ['silverfish/silverfish'], '-', [(r'.', 'chitin')], False),
    'endermite': ('EndermiteModel#createBodyLayer', ['endermite/endermite'], '-', [(r'.', 'chitin')], False),
    'warden': ('WardenModel#createBodyLayer', ['warden/warden'], '-', [(r'tendril', 'skin'), (r'.', 'skin')], False),
    'piglin': ('AdultPiglinModel#createBodyLayer', ['piglin/piglin', 'piglin/piglin_brute'], H, [(r'head|ear', 'skin'), (r'.', 'skin|cloth')], False),
    'zombified_piglin': ('AdultZombifiedPiglinModel#createBodyLayer', ['piglin/zombified_piglin'], H, [(r'head|ear', 'skin'), (r'.', 'skin|cloth')], False),
    'hoglin': ('HoglinModel#createBodyLayer', ['hoglin/hoglin', 'hoglin/zoglin'], '-', [(r'horn', 'horn'), (r'mane', 'shaggy'), (r'.', 'skin')], True),
    'strider': ('AdultStriderModel#createBodyLayer', ['strider/strider', 'strider/strider_cold'], '-', [(r'bristle', 'shaggy'), (r'.', 'skin')], False),
    'shulker': ('ShulkerModel#createBodyLayer', ['shulker/shulker'] + [f'shulker/shulker_{c}' for c in ('black', 'blue', 'brown', 'cyan', 'gray', 'green', 'light_blue',
                'light_gray', 'lime', 'magenta', 'orange', 'pink', 'purple', 'red', 'white', 'yellow')], '-', [(r'head', 'gel'), (r'.', 'stone')], False),
    'breeze': ('BreezeModel#createBodyLayer', ['breeze/breeze'], r'wind', [(r'.', 'gel')], False),
    'creaking': ('CreakingModel#createBodyLayer', ['creaking/creaking'], '-', [(r'.', 'wood')], False),
    'wither': ('WitherBossModel#createBodyLayer', ['wither/wither'], '-', [(r'.', 'bone')], False),
    'iron_golem': ('IronGolemModel#createBodyLayer', ['iron_golem/iron_golem'], '-', [(r'.', 'metal')], False),
    'snow_golem': ('SnowGolemModel#createBodyLayer', ['snow_golem/snow_golem'], '-', [(r'arm', 'wood'), (r'.', 'stone')], False),
}
MOBS.update(MONSTERS)
BESTIARY = {   # Diaithir Bestiary (GeckoLib), converted with convert.py geo
    'aurelith': ('aurelith', ['diaithirbestiary/aurelith'], '-', [(r'halo|arm', 'metal'), (r'head', 'skin'), (r'.', 'cloth')], False),
    'bumblesnout': ('bumblesnout', ['diaithirbestiary/bumblesnout'], '-', [(r'snout', 'skin'), (r'.', 'fur')], True),
    'emberwyrm': ('emberwyrm', ['diaithirbestiary/emberwyrm'], '-', [(r'wing', 'wing'), (r'.', 'shell')], False),
    'hollowmourn': ('hollowmourn', ['diaithirbestiary/hollowmourn'], '-', [(r'head', 'bone'), (r'.', 'cloth')], False),
    'ironstrider': ('ironstrider', ['diaithirbestiary/ironstrider'], '-', [(r'.', 'metal')], False),
}
MOBS.update(BESTIARY)


def material(rules, part, cube):
    key = f'{part}#{cube}'
    for rx, mat in rules:
        if re.search(rx, key):
            return 'pelt' if mat == 'fur' else mat
    return 'pelt'


def components(mask):
    """4-connected components of a small boolean mask, as lists of (y, x)."""
    seen = np.zeros_like(mask); out = []
    for y, x in zip(*np.nonzero(mask)):
        if seen[y, x]:
            continue
        stack, comp = [(y, x)], []
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop(); comp.append((cy, cx))
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; stack.append((ny, nx))
        out.append(comp)
    return out


def features(orig, face, s):
    """Keep the face's small, high-contrast marks (eyes, nostrils, mouth) from the original, drawn crisp on the new paint."""
    rgb = orig[..., :3].astype(np.float32); a = orig[..., 3] > 0
    if a.sum() < 4:
        return face
    med = np.median(rgb[a], 0)
    dist = np.linalg.norm(rgb - med, axis=2)
    mask = (dist > 60) & a
    for comp in components(mask):
        if len(comp) > max(6, a.sum() // 8):  # big patches are markings, already carried by the soft colour
            continue
        ys = [p[0] for p in comp]
        for y, x in comp:
            c = rgb[y, x]
            sl = (slice(y * s, (y + 1) * s), slice(x * s, (x + 1) * s))
            k = max(1, s // 4)
            tile = np.tile(c, (s, s, 1)) * 0.92
            tile[-k:, :] *= 0.8; tile[:, -k:] *= 0.85         # bevel: features sit in the surface
            if c.mean() < 70 and y == min(ys):              # wet highlight on dark eyes
                tile[:k, :k] = np.clip(c * 0.6 + 120, 0, 255)
            face[sl] = tile
    return face


def furry(img, s, kind, rng):
    """Upscaled colour with crisp markings: patch edges are broken along the strands instead of blurred into smears."""
    h, w = img.shape[:2]
    if h < 2 or w < 2:
        return img
    n1, n2 = rng.random((h, w)), rng.random((h, w))
    along = 1 if w > h * 1.3 else 0
    amp = {'fur': 0.9, 'pelt': 0.9, 'shaggy': 1.4, 'wool': 0.8, 'feather': 0.6}.get(kind, 0.35) * s
    dx = (blur(n1, s, along) - 0.5) * amp * 4; dy = (blur(n2, s, along) - 0.5) * amp * 4
    if kind == 'shaggy':
        dy = np.abs(dy) * 1.5   # hair hangs down
    yy, xx = np.mgrid[0:h, 0:w]
    sy = np.clip(np.round(yy + dy).astype(int), 0, h - 1); sx = np.clip(np.round(xx + dx).astype(int), 0, w - 1)
    out = img[sy, sx]
    return soft(out, max(1, s // 3))


def two(base, a, kinds, occl, rng, s, legs, ref, orig):
    """'skin|cloth': texels close to the skin colour get the first material, the rest the second."""
    k1, k2 = kinds.split('|')
    f1 = paint_face(base, a, k1, occl, rng, s, legs, DEPTH); f2 = paint_face(base, a, k2, occl, rng, s, legs, DEPTH)
    near = np.linalg.norm(orig[..., :3] - ref, axis=2) < 45
    m = soft(near.astype(np.float32).repeat(s, 0).repeat(s, 1), max(1, s // 2))[..., None]
    return f1 * m + f2 * (1 - m)


def paint_mob(layer, rules, hide, hooves, src, ao, s=4):
    k = src.size[0] // layer['tw']
    if k > 1 and src.size == (layer['tw'] * k, layer['th'] * k):   # a hi-res skin: keep its detail, scale the UVs instead
        layer = dict(tw=layer['tw'] * k, th=layer['th'] * k, faces=[dict(f, v=[[*v[:3], v[3] * k, v[4] * k] for v in f['v']]) for f in layer['faces']])
        s = max(1, s // k)
    tw, th = layer['tw'], layer['th']
    src = np.asarray(src.convert('RGBA').resize((tw, th), Image.NEAREST) if src.size != (tw, th) else src.convert('RGBA'), np.float32)
    big = src.repeat(s, 0).repeat(s, 1)
    ao = np.asarray(ao.convert('L'), np.float32) / 255
    out = big.copy(); out[..., :3] = grade(out[..., :3])   # texels no face uses keep the original, graded
    rng = np.random.default_rng(zlib.crc32(json.dumps(rules).encode()))
    done = set(); ref = None
    covered = np.zeros(big.shape[:2], bool)
    for f in layer['faces']:   # skin colour: the middle of the head's front face
        P = np.array([v[:3] for v in f['v']]); n = np.cross(P[1] - P[0], P[2] - P[0])
        if re.search(r'head$', f['part']) and n[2] < -0.1 * np.linalg.norm(n) and f['cube'] == 0:
            us = [v[3] for v in f['v']]; vs = [v[4] for v in f['v']]
            crop = src[int(min(vs)):int(max(vs)), int(min(us)):int(max(us))]
            if (crop[..., 3] > 0).any():
                ref = np.median(crop[crop[..., 3] > 0][:, :3], 0); break
    for f in layer['faces']:
        hidden = hide != '-' and re.search(hide, f['part'])
        us = [v[3] for v in f['v']]; vs = [v[4] for v in f['v']]
        x0, x1, y0, y1 = (int(round(t)) for t in (min(us), max(us), min(vs), max(vs)))
        if x1 <= x0 or y1 <= y0 or (x0, y0, x1, y1) in done:
            continue
        done.add((x0, y0, x1, y1))
        sl = (slice(y0 * s, y1 * s), slice(x0 * s, x1 * s))
        a = big[sl][..., 3]
        if not (a > 0).any():
            continue
        kind = material(rules, f['part'], f['cube'])
        P = np.array([v[:3] for v in f['v']]); n = np.cross(P[1] - P[0], P[2] - P[0]); n /= np.linalg.norm(n) + 1e-9
        base = np.maximum(furry(big[sl][..., :3], s, kind, rng), 26)  # very dark skins still show their grain
        if kind in ('horn', 'hoof'):  # one flat colour, the grain comes from the height field
            base = np.broadcast_to(big[sl][..., :3][a > 0].mean(0), base.shape)
        flat = min(f['box']) < 0.01
        occl = np.full(a.shape, 0.85, np.float32) if hidden else np.maximum(ao[sl], 0.75) if flat else ao[sl]
        legs = bool(re.search(r'leg', f['part']))
        if '|' in kind:
            face = two(base, a, kind, occl, rng, s, legs, ref if ref is not None else base.reshape(-1, 3).mean(0), src[y0:y1, x0:x1])
        else:
            face = paint_face(base, a, kind, occl, rng, s, legs, DEPTH)
        tone = soft(rng.random(a.shape), 3 * s)   # broad light and dark across big faces, so they never read as flat
        face = face * (1 + 0.5 * (tone - tone.mean()) / (tone.std() + 1e-6) * 0.08)[..., None]
        if hooves and legs and abs(n[1]) < 0.5:   # hoof band: the bottom of each leg's side faces
            hb = max(s, (y1 - y0) * s // 6)
            hoof = paint_face(np.broadcast_to(np.array([58, 48, 40], np.float32), (hb, (x1 - x0) * s, 3)), a[-hb:], 'hoof', occl[-hb:], rng, s, False, DEPTH)
            face[-hb:] = hoof
        if re.search(r'head|nose|snout|mouth|beak', f['part']) and n[2] < -0.7:   # forward-facing face of the head
            face = features(src[y0:y1, x0:x1], face, s)
        out[sl] = np.dstack([grade(face), a]); covered[sl] = True
    # texels no face of this layer uses (other variants' parts): painted too, each block as its own face
    left = (big[..., 3] > 0) & ~covered
    small = left[::s, ::s]
    default = rules[-1][1] if rules and rules[-1][0] == r'.' else 'pelt'
    for comp in components(small):
        ys = [p[0] for p in comp]; xs = [p[1] for p in comp]
        sl = (slice(min(ys) * s, (max(ys) + 1) * s), slice(min(xs) * s, (max(xs) + 1) * s))
        a = big[sl][..., 3]
        kind = default.split('|')[-1]
        face = paint_face(furry(big[sl][..., :3], s, kind, rng), a, kind, np.full(a.shape, 0.85, np.float32), rng, s, False, DEPTH)
        m = left[sl][..., None]
        out[sl] = np.where(m, np.dstack([grade(face), a]), out[sl])
    paint_mob.uncovered = float(small.sum()) / max(1, (big[::s, ::s, 3] > 0).sum())
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def run(table, blender, layers_json, tex, outdir, names):
    layers = json.load(open(layers_json)); outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    for mob in names:
        key, textures, hide, rules, hooves = table[mob]
        ao = outdir / f'_ao_{mob}.png'
        subprocess.run([blender, str(HERE / 'poly_ao.py'), layers_json, key, '4', hide, str(ao)], check=True, capture_output=True)
        for t in textures:
            t, _, k = t.partition('@')
            a2 = ao
            if k:   # this skin has its own model (cold cow horns, donkey chests)
                a2 = outdir / f'_ao_{mob}_{k.split("#")[0]}.png'
                subprocess.run([blender, str(HERE / 'poly_ao.py'), layers_json, k, '4', hide, str(a2)], check=True, capture_output=True)
            dst = outdir / f'{t}.png'; dst.parent.mkdir(parents=True, exist_ok=True)
            paint_mob(layers[k or key], rules, hide, hooves, Image.open(Path(tex) / f'{t}.png'), Image.open(a2)).save(dst)
            print(f'  {t}: {paint_mob.uncovered:.0%} of texels outside the model', flush=True)
        print(mob, len(textures), flush=True)


if __name__ == '__main__':
    blender, layers_json, tex, outdir = sys.argv[1:5]
    run(MOBS, blender, layers_json, tex, outdir, sys.argv[5:] or list(MOBS))
