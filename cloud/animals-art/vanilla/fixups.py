"""Skins auto.py could not match by coverage, given their real models: MCA profession outfits (the player body layout,
drawn over the villager) and the Millager plain villager and commander (vanilla villager layout).

    python3 fixups.py BLENDER_PYTHON LAYERS_JSON TEX_ROOT OUT
LAYERS_JSON is auto.py's, with the vanilla VillagerModel#createBodyModel added as 'millager:VanillaVillager' and PlayerModel#createMesh as 'mca:VanillaPlayer'.
Forbidden Arcanus' pixie skins are left alone: nothing in the mod draws them (no model, no renderer).
"""
import sys
from vanilla import run

MCA = 'assets/mca/textures/entity/villager/profession/'
TABLE = {
    'mca_profession': ('mca:VanillaPlayer', [MCA + p for p in ('adventurer', 'archer', 'cultist', 'guard', 'outlaw')], '-',
                       [(r'(^|/)head', 'cloth'), (r'.', 'cloth')], False),
    'millager_villager': ('millager:VanillaVillager', ['assets/millager/textures/entity/villager/villager', 'assets/millager/textures/entity/villager/profession/commander'],
                          '-', [(r'head|nose', 'skin'), (r'.', 'skin|cloth')], False),
}

def preview(tex):
    return TABLE


if __name__ == '__main__':
    blender, layers_json, tex, outdir = sys.argv[1:5]
    run(TABLE, blender, layers_json, tex, outdir, list(TABLE))

