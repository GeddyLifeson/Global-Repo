# Global catalogue (everything, by ID)

One ID per artefact, never reused. Paths and metadata only; the repo is public, so no secrets, emails or private data.

| Prefix | What | File | Kept current by |
|---|---|---|---|
| S | scripts (all devices) | `SCRIPTS_INDEX.md`, `ids.tsv` | `scan_cloud.py` (S0001), `build_index.py` (S0002), PC/laptop scans |
| D | docs, plans, Bible, notes (.md .txt .html) | `catalog/D.tsv` | `crawl_all.py` (S0335) |
| F | data files (.csv .tsv .json .dat: names, cultures, compat matrix) | `catalog/F.tsv` | `crawl_all.py` |
| M | modules, mods, jars | `catalog/M.tsv` | `crawl_all.py` |
| A | art and texture sets (dirs of 3+ images) | `catalog/A.tsv` | `crawl_all.py` |
| J | compute jobs (`compute/jobs/*`) | `catalog/J.tsv` | `crawl_all.py` |
| L | laptop projects and repos (index of what lives on the MSI) | `catalog/L.tsv` | `add_rows.py`; source `compute/index_laptop.tsv` |
| B | game and tool backends on the laptop (data formats, mod loaders, APIs) | `catalog/B.tsv` | `add_rows.py`; source `compute/index_laptop_backends.tsv` |
| G | games installed on the PC (Steam/Epic) with backend hints | `catalog/G.tsv` | `add_rows.py`; source `compute/index_pc.tsv` |
| R | projects and repos on the PC | `catalog/R.tsv` | same |
| I | installed programs on the PC | `catalog/I.tsv` | same |
| L, B | laptop projects, laptop backends | `catalog/L.tsv`, `catalog/B.tsv` | see above |
| T | project threads and what each owns | `catalog/T.tsv` | `add_rows.py` (S0336) |
| P | PRs and branches across repos | `catalog/P.tsv` | `add_rows.py` |

Paths are relative to `/mnt/project-files` unless a device column says otherwise. `registry/<PREFIX>.tsv` maps ID to key and is the source of truth for IDs.

Refresh: `git pull --rebase`, `python3 -I crawl_all.py .`, commit, push. New IDs: `python3 -I claim_id.py <PREFIX> [count]` (atomic, retries on races).
