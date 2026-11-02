"""Wyrmlore (Ice and Fire CE port) creatures, the locked Diaithir creature method.

    python3 wyrm.py BLENDER_PYTHON LAYERS_JSON TEX_ROOT OUT [creature ...]
LAYERS_JSON from convert.py (tabula dragons and sea serpent, AdvancedModelBox models); TEX_ROOT holds iceandfire/entity/...
Every full skin is painted, including blink and sleeping skins; glow overlays (_eyes), armour, saddles and eggs are not.
"""
import re, sys
from pathlib import Path
from vanilla import run

SCALES = [(r'Wing|Finger|Membrane|Fin', 'wing'), (r'Horn|Claw|Toe|Teeth|Tooth|Spike|Club|Spine', 'horn'), (r'.', 'shell')]
SKIP = r'_eyes|armor|saddle|bridle|chest|egg|breath|skeleton|fire_horn|fire_mouth|ice_horn|ice_mouth|lightning_horn|lightning_mouth|male_|overlay|beam|house|stone|shopping|weapon|_skull|horse|shield|black_frost|feather|decapitated|head_|^stone_player'
TABLE = {   # creature: layer, texture folder + filename regex, hidden parts, material rules, hooves
    'firedragon': ('firedragon', 'firedragon', r'^(red|green|bronze|gray)_\d', '-', SCALES, False),
    'icedragon': ('icedragon', 'icedragon', r'^(blue|white|sapphire|silver)_\d', '-', SCALES, False),
    'lightningdragon': ('lightningdragon', 'lightningdragon', r'^(electric|amethyst|copper|black)_\d', '-', SCALES, False),
    'seaserpent': ('seaserpent', 'seaserpent', r'^seaserpent_', '-', [(r'Fin', 'wing'), (r'Teeth', 'horn'), (r'.', 'shell')], False),
    'amphithere': ('AmphithereModel', 'amphithere', r'^amphithere_', '-', [(r'Beak|Teeth|Club', 'horn'), (r'.', 'feather')], False),
    'cockatrice': ('CockatriceModel', 'cockatrice', r'^cockatrice_\d\.png', '-', [(r'Jaw|Claw|Foot|Leg', 'horn'), (r'Comb|Wattle', 'skin'), (r'.', 'feather')], False),
    'cockatrice_chick': ('CockatriceChickModel', 'cockatrice', r'_chick', '-', [(r'Jaw|Claw|Foot|Leg', 'horn'), (r'.', 'feather')], False),
    'cyclops': ('CyclopsModel', 'cyclops', r'^cyclops_', '-', [(r'Horn|Teeth', 'horn'), (r'Loin', 'cloth'), (r'.', 'skin')], False),
    'deathworm': ('DeathWormModel', 'deathworm', r'^deathworm_', '-', [(r'Tooth|Spine|Hook', 'horn'), (r'.', 'skin')], False),
    'dread_beast': ('DreadBeastModel', 'dread', r'^dread_beast', '-', [(r'pelt', 'shaggy'), (r'.', 'bone')], False),
    'dread_ghoul': ('DreadGhoulModel', 'dread', r'^dread_ghoul_(closed|mid|open)', '-', [(r'.', 'hide')], False),
    'dread_knight': ('DreadKnightModel', 'dread', r'^dread_knight_\d', '-', [(r'crown|chestplate', 'metal'), (r'cloak|sleeve|robe', 'cloth'), (r'.', 'bone')], False),
    'dread_lich': ('DreadLichModel', 'dread', r'^dread_lich_\d', '-', [(r'hood|robe|sleeve', 'cloth'), (r'.', 'bone')], False),
    'dread_queen': ('DreadKnightModel', 'dread', r'^dread_queen', '-', [(r'crown|chestplate', 'metal'), (r'cloak|sleeve|robe', 'cloth'), (r'.', 'skin')], False),
    'dread_thrall': ('DreadThrallModel', 'dread', r'^dread_thrall\.png', '-', [(r'headware', 'metal'), (r'.', 'bone')], False),
    'dread_scuttler': ('DreadScuttlerModel', 'dread', r'^dread_scuttler', '-', [(r'.', 'chitin')], False),
    'ghost': ('GhostModel', 'ghost', r'^ghost_(blue|green|white)', '-', [(r'mask|jaw', 'bone'), (r'.', 'cloth')], False),
    'gorgon': ('GorgonModel', 'gorgon', r'^gorgon_(active|passive)', '-', [(r'Snake', 'shell'), (r'.', 'skin|cloth')], False),
    'hippocampus': ('HippocampusModel', 'hippocampus', r'^(hippocampus_|rainbow)', r'Saddle|Stirrup|Rein|NoseBand|Chest', [(r'Fin|Fluke', 'wing'), (r'Mane', 'shaggy'), (r'.', 'skin')], False),
    'hippogryph': ('HippogryphModel', 'hippogryph', r'^(alex|black|brown|chestnut|creamy|dark_brown|dodo|gray|raptor|white)', r'Saddle|Stirrup|Rein|NoseBand|Chest',
                   [(r'Beak|Claw|Toe', 'horn'), (r'Wing|Finger|Head|Neck|Crest|Quill|Front', 'feather'), (r'.', 'fur')], True),
    'hydra': ('HydraBodyModel', 'hydra', r'^hydra_\d', '-', [(r'Spike', 'horn'), (r'.', 'shell')], False),
    'pixie': ('PixieModel', 'pixie', r'^pixie_\d', '-', [(r'Wing', 'wing'), (r'Dress', 'cloth'), (r'.', 'skin')], False),
    'siren': ('SirenModel', 'siren', r'^siren_', '-', [(r'Hair', 'shaggy'), (r'Fin|Fluke|Tail', 'shell'), (r'.', 'skin')], False),
    'stymphalian_bird': ('StymphalianBirdModel', 'stymphalianbird', r'^stymphalian_bird', '-', [(r'Wing|Finger|Tail|Crest', 'metal'), (r'Toe|Jaw|Front', 'horn'), (r'.', 'feather')], False),
    'troll': ('TrollModel', 'troll', r'^troll_(forest|frost|mountain)\.png', r'blade|block|bottom|column|handle|log|top', [(r'horn|teeth', 'horn'), (r'loin', 'cloth'), (r'.', 'skin')], False),
}


def table(tex_root):
    out = {}
    for name, (layer, folder, rx, hide, rules, hooves) in TABLE.items():
        files = sorted(p.stem for p in (Path(tex_root) / 'iceandfire/entity' / folder).glob('*.png')
                       if re.search(rx, p.name) and not re.search(SKIP, p.name))
        out[name] = (layer, [f'iceandfire/entity/{folder}/{f}' for f in files], hide, rules, hooves)
    return out


def preview(tex_root):
    """The page: dragons at their adult stage, one skin per colour; every other creature's skins without blinks."""
    out = {}
    for k, (layer, skins, hide, rules, hooves) in table(tex_root).items():
        keep = [s for s in skins if (re.search(r'_4$', s) if 'dragon' in k else not re.search(r'blink|sleeping|injured|aggressive', s))]
        out[k] = (layer, keep[:2] if 'dragon' in k else keep, hide, rules, hooves)   # page size: two colours per dragon
    return out


if __name__ == '__main__':
    blender, layers_json, tex, outdir = sys.argv[1:5]
    t = table(tex)
    run(t, blender, layers_json, tex, outdir, sys.argv[5:] or list(t))
