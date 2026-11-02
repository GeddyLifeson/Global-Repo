"""Mod mobs exported by ExportLayers.java from the mod's own jar (Twilight Forest, Aether II), the locked creature method.

    python3 mods.py BLENDER_PYTHON LAYERS_JSON TEX_ROOT OUT [mob ...]
TEX_ROOT holds assets/<namespace>/textures/entity/...; skins are found by glob. Glow layers (_emissive, _eyes, _glow), armour,
saddles, wings drawn as their own layer and banners are left alone.
"""
import re, sys
from pathlib import Path
from vanilla import run

TF, AE = 'assets/twilightforest/textures/entity/', 'assets/aether_ii/textures/entity/mobs/'
SKIP = r'_emissive|_eyes|_glow|saddle|collar|_wings\.png|_lines|_timer|_rune|_eye|_charging|_dazed'
SC = [(r'leg|claw|mandible|horn|pincer|antenna', 'horn'), (r'wing', 'wing'), (r'.', 'chitin')]
TABLE = {
    # Twilight Forest
    'tf_adherent': ('AdherentModel#create', [TF + 'adherent'], '-', [(r'.', 'cloth')], False),
    'tf_alpha_yeti': ('AlphaYetiModel#create', [TF + 'yetialpha'], '-', [(r'horn', 'horn'), (r'.', 'shaggy')], False),
    'tf_bighorn': ('BighornModel#create', [TF + 'bighorn'], '-', [(r'horn', 'horn'), (r'head', 'skin'), (r'.', 'wool')], True),
    'tf_block_goblin': ('BlockChainGoblinModel#create', [TF + 'blockgoblin'], '-', [(r'head', 'skin'), (r'.', 'skin|cloth')], False),
    'tf_boar': ('BoarModel#create', [TF + 'wildboar'], '-', [(r'.', 'shaggy')], True),
    'tf_bunny': ('BunnyModel#create', [TF + 'bunny*'], '-', [], False),
    'tf_carminite_golem': ('CarminiteGolemModel#create', [TF + 'carminitegolem'], '-', [(r'.', 'metal')], False),
    'tf_cicada': ('CicadaModel#create', [TF + 'cicada-model'], '-', SC, False),
    'tf_deer': ('DeerModel#create', [TF + 'wilddeer'], '-', [(r'antler|horn', 'horn')], True),
    'tf_fire_beetle': ('FireBeetleModel#create', [TF + 'firebeetle'], '-', SC, False),
    'tf_harbinger_cube': ('HarbingerCubeModel#create', [TF + 'apocalypse2'], '-', [(r'.', 'stone')], False),
    'tf_hydra': ('HydraModel#create', [TF + 'hydra4'], '-', [(r'spike|tooth|fang', 'horn'), (r'.', 'shell')], False),
    'tf_kobold': ('KoboldModel#create', [TF + 'kobold'], '-', [(r'head|ear', 'skin'), (r'.', 'skin|cloth')], False),
    'tf_lich': ('LichModel#create', [TF + 'twilightlich64'], '-', [(r'crown', 'metal'), (r'.', 'cloth')], False),
    'tf_goblin_knight': ('LowerGoblinKnightModel#create', [TF + 'doublegoblin'], '-', [(r'head', 'skin'), (r'.', 'skin|cloth')], False),
    'tf_minoshroom': ('MinoshroomModel#create', [TF + 'minoshroomtaur'], '-', [(r'horn', 'horn'), (r'.', 'fur')], True),
    'tf_minotaur': ('MinotaurModel#create', [TF + 'minotaur'], '-', [(r'horn', 'horn'), (r'.', 'fur')], False),
    'tf_moonworm': ('MoonwormModel#create', [TF + 'moonworm'], '-', [(r'.', 'skin')], False),
    'tf_mosquito_swarm': ('MosquitoSwarmModel#create', [TF + 'mosquitoswarm'], '-', SC, False),
    'tf_naga': ('NagaModel#create', [TF + 'nagahead'], '-', [(r'.', 'shell')], False),
    'tf_penguin': ('PenguinModel#create', [TF + 'penguin'], '-', [(r'beak|feet|foot', 'horn'), (r'.', 'feather')], False),
    'tf_pinch_beetle': ('PinchBeetleModel#create', [TF + 'pinchbeetle'], '-', SC, False),
    'tf_raven': ('RavenModel#create', [TF + 'raven'], '-', [(r'beak|leg', 'horn'), (r'.', 'feather')], False),
    'tf_redcap': ('RedcapModel#create', [TF + 'redcap', TF + 'redcapsapper'], r'/(hat|jacket)$', [(r'head|ear', 'skin'), (r'.', 'skin|cloth')], False),
    'tf_skeleton_druid': ('SkeletonDruidModel#create', [TF + 'skeletondruid'], r'/hat$', [(r'.', 'bone')], False),
    'tf_snow_queen': ('SnowQueenModel#create', [TF + 'snowqueen'], r'/hat$', [(r'crown', 'metal'), (r'head', 'skin'), (r'.', 'skin|cloth')], False),
    'tf_squirrel': ('SquirrelModel#create', [TF + 'squirrel2'], '-', [(r'tail', 'shaggy')], False),
    'tf_tower_ghast': ('TFGhastModel#create', [TF + 'towerghast', TF + 'towerghast_fire', TF + 'towerghast_openeyes'], '-', [(r'.', 'skin')], False),
    'tf_ur_ghast': ('UrGhastModel#create', [TF + 'towerboss', TF + 'towerboss_fire', TF + 'towerboss_openeyes'], '-', [(r'.', 'skin')], False),
    'tf_tiny_bird': ('TinyBirdModel#create', [TF + 'tinybird*'], '-', [(r'beak|leg', 'horn'), (r'.', 'feather')], False),
    'tf_troll': ('TrollModel#create', [TF + 'troll'], '-', [(r'.', 'skin')], False),
    'tf_wraith': ('WraithModel#create', [TF + 'wraith'], '-', [(r'.', 'cloth')], False),
    'tf_yeti': ('YetiModel#create', [TF + 'yeti2'], '-', [(r'.', 'shaggy')], False),
    # Aether II
    'ae_aechor_plant': ('AechorPlantModel#createBodyLayer', [AE + 'aechor_plant/*'], '-', [(r'.', 'skin')], False),
    'ae_aerbunny': ('AerbunnyModel#createBodyLayer', [AE + 'aerbunny/*'], '-', [(r'.', 'shaggy')], False),
    'ae_aerwhale': ('AerwhaleModel#createBodyLayer', [AE + 'aerwhale/*'], '-', [(r'.', 'skin')], False),
    'ae_burrukai': ('BurrukaiModel#createBodyLayer', [AE + 'burrukai/*/burrukai_[hm]*[ld]c.png', AE + 'burrukai/highfields/burrukai_highfields', AE + 'burrukai/magnetic/burrukai_magnetic'], '-', [(r'horn', 'horn'), (r'.', 'shaggy')], True),
    'ae_burrukai_arctic': ('ArcticBurrukaiModel#createBodyLayer', [AE + 'burrukai/arctic/burrukai_arctic'], '-', [(r'horn', 'horn'), (r'.', 'shaggy')], True),
    'ae_kirrid': ('HighfieldsKirridModel#createBodyLayer', [AE + 'kirrid/highfields/kirrid_highfields', AE + 'kirrid/highfields/kirrid_highfields_wool'], '-', [(r'horn', 'horn'), (r'.', 'wool')], True),
    'ae_kirrid_arctic': ('ArcticKirridModel#createBodyLayer', [AE + 'kirrid/arctic/kirrid_arctic', AE + 'kirrid/arctic/kirrid_arctic_wool'], '-', [(r'horn', 'horn'), (r'.', 'wool')], True),
    'ae_kirrid_magnetic': ('MagneticKirridModel#createBodyLayer', [AE + 'kirrid/magnetic/kirrid_magnetic', AE + 'kirrid/magnetic/kirrid_magnetic_wool'], '-', [(r'horn', 'horn'), (r'.', 'wool')], True),
    'ae_arkenium_taluton': ('ArkeniumTalutonModel#createBodyLayer', [AE + 'arkenium_taluton/*'], '-', [(r'.', 'stone')], False),
    'ae_gravitite_taluton': ('GravititeTalutonModel#createBodyLayer', [AE + 'gravitite_taluton/*'], '-', [(r'.', 'stone')], False),
    'ae_bladeshroom_hunter': ('BladeshroomHunterModel#createBodyLayer', [AE + 'bladeshroom_hunter/*'], '-', [(r'.', 'skin')], False),
    'ae_carrion_sprout': ('CarrionSproutModel#createBodyLayer', [AE + 'carrion_sprout/*'], '-', [(r'.', 'skin')], False),
    'ae_cockatrice': ('CockatriceModel#createBodyLayer', [AE + 'cockatrice/*'], '-', [(r'beak|leg|claw|toe', 'horn'), (r'.', 'feather')], False),
    'ae_detonation_sentry': ('DetonationSentryModel#createBodyLayer', [AE + 'detonation_sentry/detonation_sentry'], '-', [(r'.', 'stone')], False),
    'ae_flying_cow': ('FlyingCowModel#createBodyLayer', [AE + 'flying_cow/flying_cow'], '-', [(r'horn', 'horn')], True),
    'ae_glitterwing': ('GlitterwingModel#createBodyLayer', [AE + 'glitterwing/*'], '-', SC, False),
    'ae_mimic': ('MimicModel#createBodyLayer', [AE + 'mimic/sentry_crate_mimic'], '-', [(r'tooth|teeth', 'horn'), (r'.', 'wood')], False),
    'ae_moa': ('MoaModel#createBodyLayer', [AE + 'moa/moa_base', AE + 'moa/moa_feather_*', AE + 'moa/moa_keratin', AE + 'moa/raptor*'], '-', [(r'beak|leg|toe|claw', 'horn'), (r'.', 'feather')], False),
    'ae_phyg': ('PhygModel#createBodyLayer', [AE + 'phyg/phyg'], '-', [(r'.', 'skin')], True),
    'ae_prismallard': ('PrismallardModel#createBodyLayer', [AE + 'prismallard/*'], '-', [(r'beak|leg|feet', 'horn'), (r'.', 'feather')], False),
    'ae_sentry_golem': ('SentryGolemModel#createBodyLayer', [AE + 'sentry_golem/sentry_golem', AE + 'sentry_golem/sentry_golem_ranged'], '-', [(r'.', 'stone')], False),
    'ae_sheepuff': ('SheepuffModel#createBodyLayer', [AE + 'sheepuff/*'], '-', [(r'head', 'skin'), (r'.', 'wool')], True),
    'ae_shroudwing': ('ShroudwingModel#createBodyLayer', [AE + 'shroudwing/*'], '-', [(r'wing', 'wing'), (r'.', 'chitin')], False),
    'ae_skephid': ('SkephidModel#createBodyLayer', [AE + 'skephid/skephid'], '-', [(r'.', 'skin')], False),
    'ae_skyroot_lizard': ('SkyrootLizardModel#createBodyLayer', [AE + 'skyroot_lizard/*'], '-', [(r'.', 'skin')], False),
    'ae_slider': ('SliderModel#createBodyLayer', [AE + 'slider/slider_asleep', AE + 'slider/slider_awake', AE + 'slider/slider_awake_critical'], '-', [(r'.', 'stone')], False),
    'ae_swet': ('SwetModel#createBodyLayer', [AE + 'swet/*'], '-', [(r'.', 'gel')], False),
    'ae_taegore': ('TaegoreModel#createBodyLayer', [AE + 'taegore/*/*'], '-', [(r'tusk|horn', 'horn'), (r'.', 'shaggy')], True),
    'ae_tempest': ('TempestModel#createBodyLayer', [AE + 'tempest/tempest'], '-', [(r'.', 'gel')], False),
    'ae_zephyr': ('ZephyrModel#createBodyLayer', [AE + 'zephyr/zephyr'], '-', [(r'.', 'gel')], False),
}


def table(tex_root):
    root = Path(tex_root); out = {}
    for name, (layer, pats, hide, rules, hooves) in TABLE.items():
        skins = []
        for p in pats:
            hits = sorted(root.glob(p if p.endswith('.png') or p.endswith('*') else p + '.png'))
            skins += [str(h.relative_to(root))[:-4] for h in hits if h.suffix == '.png' and not re.search(SKIP, h.name) and not re.search(r'baby', h.name)]
        out[name] = (layer, list(dict.fromkeys(skins)), hide, rules, hooves)
    return out


def preview(tex_root):
    return table(tex_root)


if __name__ == '__main__':
    blender, layers_json, tex, outdir = sys.argv[1:5]
    t = table(tex)
    run(t, blender, layers_json, tex, outdir, sys.argv[5:] or list(t))
