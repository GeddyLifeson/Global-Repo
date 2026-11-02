"""Fixes ATM11 pack scripts for the 26.1.2 builds of their mods. Safe to rerun. Usage: python -I fix_atm11_261.py <kubejs dir>...
- Industrial Foregoing laser drill: catalyst is a plain item id, output is {"ingredient": <id or #tag>, "count"|"amount"}.
- Forbidden Arcanus beta.2: the five forge tier items became one item (tier is world-only), so recipes take the plain forge.
- IF dissolution chamber: ATM's recipe schema moved to where KubeJS 8 reads it."""
import json, re, sys
from pathlib import Path


def drop_statements(js, needles):
    """Removes each `allthemods.recipes...` chain (its head line plus deeper-indented `.call(...)` lines) naming a needle."""
    stmt = re.compile(r"(?m)^([ \t]*)allthemods\.recipes\.[^\r\n]*(?:\r?\n\1[ \t]+\.[^\r\n]*)*\r?\n?")  # ATM files are CRLF
    js.write_text(stmt.sub(lambda m: "" if any(n in m.group(0) for n in needles) else m.group(0),
                           js.read_text(encoding="utf-8")), encoding="utf-8")


for kjs in map(Path, sys.argv[1:]):
    for f in (kjs / "dynamic_data/industrialforegoing/recipe/laser_drill_ore").rglob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(d["catalyst"], dict):
            d["catalyst"] = d["catalyst"]["item"]
        out = d["output"]
        if "tag" in out:
            d["output"] = {"ingredient": "#" + out["tag"], "count": out.get("count", 1)}
        f.write_text(json.dumps(d, indent=2), encoding="utf-8")
    edits = {
        "server_scripts/mods/industrialforegoing/laser_drill.js": [
            ("          output: output,", "          output: { ingredient: output.fluid, amount: output.amount },"),
            ("          catalyst: {\n            item: catalyst\n          }", "          catalyst: catalyst")],
        "server_scripts/modpack/runic_multis/controllers.js": [
            ("forbidden_arcanus:hephaestus_forge_tier_5", "forbidden_arcanus:hephaestus_forge")],
        # MI multiblock members are block ids only, so the auto forge now takes a forge of any tier
        "startup_scripts/modern_industrialization/multiblocks/auto_forge.js": [
            ("forbidden_arcanus:hephaestus_forge_tier_5", "forbidden_arcanus:hephaestus_forge")],
    }
    for rel, pairs in edits.items():
        js = kjs / rel
        s = js.read_text(encoding="utf-8")
        for old, new in pairs:
            s = s.replace(old, new)
        js.write_text(s, encoding="utf-8")
    # KubeJS 8 reads <ns>/kubejs/recipe_schema from the server's datapacks (kubejs/data), not ATM's dynamic_data/kjs72
    # copies; this one matches IF 26.1.2's format
    dst = kjs / "data/industrialforegoing/kubejs/recipe_schema"
    dst.mkdir(parents=True, exist_ok=True)
    schema = (kjs / "dynamic_data/industrialforegoing/kubejs/kjs72/recipe_schema/dissolution_chamber.json").read_text(encoding="utf-8")
    (dst / "dissolution_chamber.json").write_text(schema.replace('"flat_sized_fluid_ingredient"', '"sized_fluid_ingredient"'),
                                                  encoding="utf-8")  # KubeJS 8's name for the type
    # A recipe naming something this pack lacks throws out of its whole ServerEvents.recipes handler, losing every
    # recipe after it in the file, so those statements go (forge tier items: forges now upgrade in the world;
    # kubejs:modularium: ATM never registers it; aureal from aureal once source fluid is swapped below).
    runic = kjs / "server_scripts/modpack/runic_multis"
    drop_statements(runic / "recipes/auto_forge.js", ("hephaestus_forge_tier_", "kubejs:modularium"))
    drop_statements(runic / "recipes/runic_crucible.js", ('fluidIn("1000x starbunclemania:source_fluid")',))
    drop_statements(runic / "recipes/runic_enchanter.js", ("enderio:stored_entity",))  # no such component in EnderIO 9
    swaps = {
        runic / "recipes/auto_forge.js": [('"allthemodium:alloy_pick"', '"allthemodium:alloy_pickaxe"')],
        runic / "recipes/runic_crucible.js": [("starbunclemania:source_fluid", "kubejs:liquid_aureal")],
        runic / "recipes/runic_enchanter.js": [
            ("starbunclemania:source_fluid", "kubejs:liquid_aureal"),
            ('stored_enchantments={levels:{"minecraft:${enchant.enchant}":${enchant.lvl}}}',  # 1.21.5+ format
             'stored_enchantments={"minecraft:${enchant.enchant}":${enchant.lvl}}')],
        runic / "recipes/star_altar.js": [("15x allthecompressed:nether_star_block_3x", "64x minecraft:nether_star")],
        kjs / "server_scripts/modpack/atm_star_creative.js": [
            ('"mekanism:creative_energy_cube[mekanism:energy={energy_containers:[L;9223372036854775807L]}]"',
             '"mekanism:creative_energy_cube"')],
        kjs / "server_scripts/unification/sawing.js": [  # one Mekanism sawing recipe still has the 1.21.1 {item, count} input
            ('r.json.asMap().input.has("ingredient") ? r.json.asMap().input.get("ingredient") : r.json.asMap().input',
             'r.json.asMap().input.has("ingredient") ? r.json.asMap().input.get("ingredient") : '
             'r.json.asMap().input.has("item") ? r.json.asMap().input.get("item").asString : r.json.asMap().input')],
    }
    for js, pairs in swaps.items():
        s = js.read_text(encoding="utf-8")
        for old, new in pairs:
            if not (old in new and new in s):  # the sawing fix contains its own target; apply it once
                s = s.replace(old, new)
        js.write_text(s, encoding="utf-8")
    # 26.1 ingredients are plain strings ("id" or "#tag"), not the 1.21.1 {item: ...} / {tag: ...} objects
    pnc = kjs / "server_scripts/mods/pneumaticcraft/recipes.js"
    if pnc.exists():
        s = re.sub(r"\{\s*item:\s*(\"[^\"]+\")\s*\}", r"\1", pnc.read_text(encoding="utf-8"))
        pnc.write_text(re.sub(r"\{\s*tag:\s*\"([^\"]+)\"\s*\}", r'"#\1"', s), encoding="utf-8")
    # 1.21.5+ enchantment components dropped the {levels: {...}} wrapper
    for js in (kjs / "server_scripts").rglob("*.js"):
        s = js.read_text(encoding="utf-8")
        fixed = re.sub(r"(enchantments=)\{levels:(\{[^{}]*\})\}", r"\1\2", s)
        if fixed != s:
            js.write_text(fixed, encoding="utf-8")
    # controller and recipe entries that need an Ars Nouveau item (the mod is not in this pack); 8-space lines keep the
    # match inside one { ... } entry
    controllers = runic / "controllers.js"
    controllers.write_text(re.sub(r"(?m)^      \{\r?\n(?:        [^\r\n]*\r?\n)*?        \w+: \"ars_nouveau:[^\r\n]*\r?\n"
                                  r"(?:        [^\r\n]*\r?\n)*?      \},?\r?\n", "", controllers.read_text(encoding="utf-8")),
                           encoding="utf-8")
    print(kjs, "ok")

