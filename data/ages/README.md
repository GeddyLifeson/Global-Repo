# Items with no Age (V1 audit finding 5)

Made by `assign_ages.py` (S6957) from `audit/tech_age_resolved_per_item.json` (7,250 ids with no Age) and `era-index/tech_ages_by_item_unmerged.csv`.

- `NOAGE_ASSIGNED.csv`: 7,249 item ids, each with an Age and the reason. 6,173 come from the existing by-item classification; the other 1,076 from rules (material, mob home, namespace). `minecraft:air` is not an item and is skipped.
- `NAMESPACE_DEFAULTS.json`: Age default for every namespace that had none, including the former `nontech` list and the new `diaithirtrees` (I) and `diaithir_planets` (VIII). It covers ids that are not in the snapshot, such as the 1,141 diaithirtrees and 840 planet items the audit counted.

Applied to DiaithirRPG `content/tech_ages.json` in rpg#280 with `python3 -I assign_ages.py PROJECT_FILES data/ages TECH_AGES.json AUDIT_NOAGE_IDS.txt`; the audit's `noage.py` then reports 0 of 47,200. To apply by hand: merge `NAMESPACE_DEFAULTS.json` into the `namespaces` map and the CSV rows into `items` of DiaithirRPG `content/tech_ages.json`, empty `nontech`, then run `tools/techages` and `test_tech_ages.py`. Item-level rows beat namespace defaults. Rows in the 12.7% that sit in a namespace with a default need no row.
The audit's 5,989-id list is `/mnt/project-files/audit/v1-2026-11-04/noage_ids.txt`; its ids are covered by the namespace defaults here (45 added after the audit).
