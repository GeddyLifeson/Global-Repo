"""B05: imports the game-plan/data CSVs into DataTables, CurveTables and StringTables.

Tables, structs and asset paths come from sf_import_manifest.json (written by tools/GenRowStructs.py).
Editor: py sf_import_data.py [data dir]   (default <project>/Data)
Headless: UnrealEditor-Cmd.exe Shardfall.uproject -run=pythonscript -script="sf_import_data.py"
"""
import csv
import json
import os
import sys

import unreal

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
DATA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJECT, "Data")
TMP = os.path.join(PROJECT, "Intermediate", "SfImport")
KINDS = {"DataTable": unreal.CSVImportType.ECSV_DATA_TABLE, "CurveTable": unreal.CSVImportType.ECSV_CURVE_TABLE}
STRING_COLUMNS = {"str_id": "Key", "text_en": "SourceString", "notes": "Comment"}
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()


def cell(value, cpp):
    if cpp == "bool":
        return "true" if value.lower() in ("true", "yes", "y") else "false"
    return value or ("0" if cpp in ("int32", "int64", "float") else "")


def numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def data_table_rows(t, header, body):
    index = {h: i for i, h in enumerate(header)}
    out, seen = [["Name"] + [p for _, p, _ in t["columns"]]], {}
    for r in body:
        key = r[0]
        if t["grouped"]:
            seen[key] = seen.get(key, -1) + 1
            key = f"{key}__{seen[key]}"
        out.append([key] + [cell(r[index[h]], cpp) for h, _, cpp in t["columns"]])
    return out


def curve_table_rows(header, body):
    """One curve per numeric column, keyed by the first column."""
    out = [["Name"] + [r[0] for r in body]]
    for i, h in enumerate(header[1:], 1):
        if all(numeric(r[i]) for r in body):
            out.append([h] + [r[i] for r in body])
    return out


def csv_task(path, asset, import_type, struct=None):
    factory = unreal.CSVImportFactory()
    settings = factory.get_editor_property("automated_import_settings")
    settings.import_type = import_type
    settings.import_curve_interp_mode = unreal.RichCurveInterpMode.RCIM_LINEAR
    if struct:
        settings.import_row_struct = getattr(unreal, struct[1:]).static_struct()
    factory.set_editor_property("automated_import_settings", settings)
    task = unreal.AssetImportTask()
    task.filename = path
    task.destination_path, task.destination_name = asset.rsplit("/", 1)
    task.automated = task.replace_existing = task.save = True
    task.factory = factory
    return task


def import_string_table(path, asset):
    folder, name = asset.rsplit("/", 1)
    table = (unreal.EditorAssetLibrary.load_asset(asset) if unreal.EditorAssetLibrary.does_asset_exist(asset)
             else ASSETS.create_asset(name, folder, unreal.StringTable, unreal.StringTableFactory()))
    return (unreal.SfStringTableImport.import_string_table_csv(table, path)
            and unreal.EditorAssetLibrary.save_loaded_asset(table, False))


def main():
    with open(os.path.join(HERE, "sf_import_manifest.json")) as f:
        manifest = json.load(f)
    tasks, failed = [], []
    for t in manifest:
        with open(os.path.join(DATA, t["csv"]), newline="", encoding="utf-8") as f:
            header, *body = list(csv.reader(f))
        if t["type"] == "DataTable":
            rows = data_table_rows(t, header, body)
        elif t["type"] == "CurveTable":
            rows = curve_table_rows(header, body)
        else:
            rows = [[STRING_COLUMNS.get(h, h) for h in header]] + body
        path = os.path.join(TMP, t["csv"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
        if t["type"] == "StringTable":
            if not import_string_table(path, t["asset"]):
                failed.append(t["csv"])
        else:
            tasks.append((t["csv"], csv_task(path, t["asset"], KINDS[t["type"]], t.get("struct"))))
    ASSETS.import_asset_tasks([task for _, task in tasks])
    failed += [name for name, task in tasks if not task.get_editor_property("imported_object_paths")]
    unreal.log(f"SfImport: {len(manifest) - len(failed)} of {len(manifest)} tables imported")
    if failed:
        raise RuntimeError("SfImport failed: " + ", ".join(failed))


main()
