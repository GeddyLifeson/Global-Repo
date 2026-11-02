"""Builds datatable_map.csv: how every CSV in game-plan/data maps into Unreal. Rerun after data changes."""
import csv, glob, os, re
ROOT = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
OUT = os.path.join(os.path.dirname(__file__), '..', 'datatable_map.csv')
MULTI = {'loot_tables', 'vendors', 'enemy_stats_by_level', 'upgrade_costs', 'armor_stat_rolls', 'input_preset_bindings'}
CURVE = {'level_curve', 'skill_rank_curve', 'attribute_scaling_curve', 'stat_curve'}
STRINGS = {'strings', 'strings_data'}
FORMULA = {'formulas', 'derived_formulas', 'economy_formulas'}
RUNTIME = {  # which runtime system reads each table
 'actors': 'Actors/AI', 'items': 'Items/Inventory', 'ui': 'UI', 'world': 'World', 'assets': 'Editor only'}
pascal = lambda s: ''.join(w.capitalize() for w in re.split(r'[_\W]+', s) if w)
rows = []
for p in sorted(glob.glob(os.path.join(ROOT, '*', '*.csv'))):
    folder, name = p.split(os.sep)[-2], os.path.splitext(os.path.basename(p))[0]
    with open(p, newline='', encoding='utf-8') as f:
        r = list(csv.reader(f))
    hdr, n = r[0], len(r) - 1
    if name in STRINGS:
        kind, asset = 'StringTable', f'/Game/Localization/ST_{pascal(name)}'
        note = 'Imported as UStringTable; key=column 1, source=English text; localized via Localization Dashboard'
    elif name in CURVE:
        kind, asset = 'CurveTable', f'/Game/Data/{pascal(folder)}/CT_{pascal(name)}'
        note = 'Rows become FRealCurve; read via FCurveTableRowHandle / GAS ScalableFloat'
    elif name in FORMULA:
        kind, asset = 'DataTable+Code', f'/Game/Data/{pascal(folder)}/DT_{pascal(name)}'
        note = 'Formula text is documentation; each FRM_/ITM_F_ ID gets a C++ implementation in USfFormulaLibrary checked by unit test against the CSV examples'
    elif name in MULTI:
        kind, asset = 'DataTable (grouped)', f'/Game/Data/{pascal(folder)}/DT_{pascal(name)}'
        note = f'Several rows per key: importer makes RowName = {hdr[0]}+"__"+index and builds a TMultiMap cache at load'
    elif folder == 'assets':
        kind, asset = 'Editor report', '-'
        note = 'Not shipped. SfAssetAudit commandlet checks every hook resolves to a real asset'
    else:
        kind, asset = 'DataTable', f'/Game/Data/{pascal(folder)}/DT_{pascal(name)}'
        note = 'RowName = first column ID'
    rows.append([f'{folder}/{name}.csv', n, hdr[0], len(hdr), kind, f'F{pascal(name)}Row' if kind.startswith('DataTable') else '-',
                 asset, RUNTIME.get(folder, '-'), 'Async soft-load' if n > 500 else 'Load at boot', note])
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['csv', 'rows', 'key_column', 'columns', 'ue_type', 'ue_struct', 'ue_asset', 'runtime_owner', 'load_policy', 'notes'])
    w.writerows(rows)
print(len(rows), 'tables ->', OUT)
