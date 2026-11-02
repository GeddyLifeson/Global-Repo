"""B27: imports the sample library into /Game/Audio from sf_audio_spec.json (tools/gen_audio_spec.py).

Pass the library folder (game-plan/design/audio/samples/full); files are read in place, never copied.
Editor: py sf_import_audio.py D:/game-plan/design/audio/samples/full
Headless: UnrealEditor-Cmd.exe Shardfall.uproject -run=pythonscript -script="sf_import_audio.py D:/game-plan/design/audio/samples/full"

Writes one Sound Wave per OGG (/Game/Audio/Waves), one Sound Cue per event (/Game/Audio/Cues, random variation),
then DT_SfSounds, DT_SfMusicCues and DA_SfMusicRules. Existing waves and cues are kept, so a rerun only imports
what is new; delete /Game/Audio/Cues to rebuild every cue. The tables and the rules asset are rewritten every run.
"""
import json
import os
import sys

import unreal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/Game/Audio"
BATCH = 200
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()
LIB = unreal.EditorAssetLibrary


def stem(rel):
    return os.path.splitext(os.path.basename(rel))[0]


def import_waves(source, events):
    tasks = []
    for ev in events.values():
        for rel in ev["files"]:
            if LIB.does_asset_exist(f"{ev['wave_folder']}/{stem(rel)}"):
                continue
            task = unreal.AssetImportTask()
            task.filename = os.path.join(source, rel)
            task.destination_path = ev["wave_folder"]
            task.automated = task.save = True
            task.replace_existing = False
            tasks.append(task)
    missing = [t.filename for t in tasks if not os.path.isfile(t.filename)]
    if missing:
        raise RuntimeError(f"{len(missing)} library files not found, first: {missing[0]}")
    with unreal.ScopedSlowTask(len(tasks), "Importing audio") as slow:
        slow.make_dialog(True)
        for i in range(0, len(tasks), BATCH):
            if slow.should_cancel():
                raise RuntimeError("Cancelled")
            ASSETS.import_asset_tasks(tasks[i:i + BATCH])
            slow.enter_progress_frame(len(tasks[i:i + BATCH]))
    return [t.filename for t in tasks if not t.get_editor_property("imported_object_paths")]


def build_cues(events):
    failed = []
    with unreal.ScopedSlowTask(len(events), "Building sound cues") as slow:
        slow.make_dialog(True)
        for event, ev in events.items():
            slow.enter_progress_frame(1)
            folder, name = ev["cue"].split(".")[0].rsplit("/", 1)
            if LIB.does_asset_exist(f"{folder}/{name}"):
                continue
            waves = [LIB.load_asset(f"{ev['wave_folder']}/{stem(rel)}") for rel in ev["files"]]
            if None in waves:
                failed.append(event)
                continue
            cue = ASSETS.create_asset(name, folder, unreal.SoundCue, unreal.SoundCueFactoryNew())
            unreal.SfAudioCueLibrary.build_variation_cue(cue, waves, ev["loop"])
            cue.set_editor_property("priority", float(ev["priority"]))
            if ev["play_when_silent"]:
                cue.set_editor_property("virtualization_mode", unreal.VirtualizationMode.PLAY_WHEN_SILENT)
            LIB.save_loaded_asset(cue, False)
    return failed


def write_table(name, struct, rows):
    path = f"{ROOT}/{name}"
    if LIB.does_asset_exist(path):
        table = LIB.load_asset(path)
    else:
        factory = unreal.DataTableFactory()
        factory.struct = struct.static_struct()
        table = ASSETS.create_asset(name, ROOT, unreal.DataTable, factory)
    if not unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table, json.dumps(rows)):
        raise RuntimeError(f"{name}: rows rejected, see the Output Log")
    LIB.save_loaded_asset(table, False)


def write_rules(values):
    path = f"{ROOT}/DA_SfMusicRules"
    rules = (LIB.load_asset(path) if LIB.does_asset_exist(path)
             else ASSETS.create_asset("DA_SfMusicRules", ROOT, unreal.SfMusicRules, unreal.DataAssetFactory()))
    for prop, value in values.items():
        rules.set_editor_property(prop, value)
    LIB.save_loaded_asset(rules, False)


def main(source):
    with open(os.path.join(HERE, "sf_audio_spec.json"), encoding="utf-8") as f:
        spec = json.load(f)
    failed = import_waves(source, spec["events"])
    failed += build_cues(spec["events"])
    write_table("DT_SfSounds", unreal.SfSoundRow, [{"Name": k, "Sound": v} for k, v in spec["sounds"].items()])
    write_table("DT_SfMusicCues", unreal.SfMusicCueRow, spec["music"])
    write_rules(spec["rules"])
    if failed:
        raise RuntimeError(f"{len(failed)} audio imports failed, first: {failed[0]}")
    unreal.log(f"sf_import_audio: {len(spec['events'])} cues, {len(spec['sounds'])} sound rows, {len(spec['music'])} music cues")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise RuntimeError("Usage: py sf_import_audio.py <game-plan/design/audio/samples/full>")
    main(" ".join(sys.argv[1:]))
