"""B07: builds the Enhanced Input actions and mapping contexts from sf_input_spec.json (tools/gen_input.py).

Editor: py sf_build_input.py
Headless: UnrealEditor-Cmd.exe Shardfall.uproject -run=pythonscript -script="sf_build_input.py"
Re-running updates the assets in place.
"""
import json
import os

import unreal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/Game/Input"
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()
LIB = unreal.EditorAssetLibrary


def load_or_create(folder, name, cls, factory):
    path = f"{folder}/{name}"
    return LIB.load_asset(path) if LIB.does_asset_exist(path) else ASSETS.create_asset(name, folder, cls, factory)


def resolve(value, actions):
    if not isinstance(value, list):
        return value
    kind, *args = value
    if kind == "enum":
        return getattr(getattr(unreal, args[0]), args[1])
    if kind == "vec":
        return unreal.Vector(*args)
    if kind == "combo":  # [action, seconds between presses, presses]
        step = unreal.InputComboStepData(combo_step_action=actions[args[0]], time_to_press_key=args[1])
        return [step] * args[2]
    return actions[args[0]]


def instances(entries, prefix, outer, actions):
    out = []
    for cls, props in entries:
        obj = unreal.new_object(getattr(unreal, prefix + cls), outer)
        for prop, value in props.items():
            obj.set_editor_property(prop, resolve(value, actions))
        out.append(obj)
    return out


def mapping(m, imc, actions):
    km = unreal.EnhancedActionKeyMapping(action=actions[m["action"]], key=unreal.Key(key_name=m["key"]))
    km.set_editor_property("triggers", instances(m["triggers"], "InputTrigger", imc, actions))
    km.set_editor_property("modifiers", instances(m["modifiers"], "InputModifier", imc, actions))
    if m["name"]:
        settings = unreal.new_object(unreal.PlayerMappableKeySettings, imc)
        settings.set_editor_property("name", m["name"])
        km.set_editor_property("setting_behavior", unreal.PlayerMappableKeySettingBehaviors.OVERRIDE_SETTINGS)
        km.set_editor_property("player_mappable_key_settings", settings)
    else:
        km.set_editor_property("setting_behavior", unreal.PlayerMappableKeySettingBehaviors.IGNORE_SETTINGS)
    return km


def set_mappings(imc, maps):
    try:  # 5.6 keeps the default mappings in a struct beside the per-profile overrides
        data = imc.get_editor_property("default_key_mappings")
    except Exception:
        imc.set_editor_property("mappings", maps)
        return
    data.set_editor_property("mappings", maps)
    imc.set_editor_property("default_key_mappings", data)


def main():
    with open(os.path.join(HERE, "sf_input_spec.json")) as f:
        spec = json.load(f)
    actions = {}
    for a in spec["actions"]:
        action = load_or_create(f"{ROOT}/Actions", a["id"], unreal.InputAction, unreal.InputAction_Factory())
        action.set_editor_property("value_type", getattr(unreal.InputActionValueType, a["type"].upper()))
        actions[a["id"]] = action
    for name, maps in spec["contexts"].items():
        imc = load_or_create(f"{ROOT}/Contexts", name, unreal.InputMappingContext,
                             unreal.InputMappingContext_Factory())
        set_mappings(imc, [mapping(m, imc, actions) for m in maps])
    LIB.save_directory(ROOT, only_if_is_dirty=True, recursive=True)
    unreal.log(f"SfInput: {len(actions)} actions, {len(spec['contexts'])} mapping contexts built under {ROOT}")


main()
