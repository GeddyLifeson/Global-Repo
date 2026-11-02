"""B19: imports design/frontend screens.csv and widgets.csv into DT_Screens and DT_Widgets, then creates the
Widget Blueprint shells for every screen, the HUD, the modal popups and the shared button.

Editor: py sf_build_ui.py [frontend dir]   (default <project>/Design/frontend)
Headless: UnrealEditor-Cmd.exe Shardfall.uproject -run=pythonscript -script="sf_build_ui.py"
Re-running re-imports the tables and only creates missing Blueprints; existing ones keep their layout.
"""
import csv
import os
import sys

import unreal

PROJECT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT, "Design", "frontend")
TMP = os.path.join(PROJECT, "Intermediate", "SfImport", "frontend")
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()
LIB = unreal.EditorAssetLibrary

TABLES = [  # csv, asset, struct, {column: (property, convert)}
    ("screens.csv", "/Game/Data/Ui/DT_Screens", unreal.SfScreenRow, {
        "layer": ("Layer", lambda v: "Modal" if "Modal" in v else "Menu"),
        "input_context": ("InputContext", str),
        "pauses_game": ("bPausesGame", lambda v: "true" if v.startswith("Yes") else "false"),
    }),
    ("widgets.csv", "/Game/Data/Ui/DT_Widgets", unreal.SfWidgetRow, {
        "screen_id": ("ScreenId", str),
        "str_id": ("StrId", str),
        "target": ("Target", str),
        "default_focus": ("bDefaultFocus", lambda v: "true" if v == "Yes" else "false"),
    }),
]
SHELLS = [  # folder, name, parent
    ("/Game/UI/HUD", "WBP_HUD", unreal.SfLensWidget),
    ("/Game/UI/Popups", "WBP_Popup_Modal", unreal.SfPopupWidget),
    ("/Game/UI/Popups", "WBP_Popup_Error", unreal.SfPopupWidget),
    ("/Game/UI/Common", "WBP_Button", unreal.SfButton),
]


def import_table(name, asset, struct, columns):
    with open(os.path.join(SRC, name), newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    path = os.path.join(TMP, name)
    os.makedirs(TMP, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        out = csv.writer(f)
        out.writerow(["Name"] + [prop for prop, _ in columns.values()])
        for r in rows:
            out.writerow([next(iter(r.values()))] + [conv(r[col]) for col, (_, conv) in columns.items()])
    factory = unreal.CSVImportFactory()
    settings = factory.get_editor_property("automated_import_settings")
    settings.import_type = unreal.CSVImportType.ECSV_DATA_TABLE
    settings.import_row_struct = struct.static_struct()
    factory.set_editor_property("automated_import_settings", settings)
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path, task.destination_name = asset.rsplit("/", 1)
    task.automated = task.replace_existing = task.save = True
    task.factory = factory
    ASSETS.import_asset_tasks([task])
    if not task.get_editor_property("imported_object_paths"):
        raise RuntimeError(f"SfBuildUI: {name} failed to import")
    return [next(iter(r.values())) for r in rows]


def shell(folder, name, parent):
    if LIB.does_asset_exist(f"{folder}/{name}"):
        return False
    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    LIB.save_loaded_asset(ASSETS.create_asset(name, folder, unreal.WidgetBlueprint, factory), False)
    return True


def main():
    screens = import_table(*TABLES[0])
    import_table(*TABLES[1])
    made = sum(shell("/Game/UI/Screens", f"WBP_{s}", unreal.SfScreenWidget) for s in screens)
    made += sum(shell(*s) for s in SHELLS)
    unreal.log(f"SfBuildUI: {len(screens)} screens, {made} new Widget Blueprints")


main()
