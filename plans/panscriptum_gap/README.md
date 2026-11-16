# Panscriptum gap fill (character pages with no entry)
Source lists: Category:Characters of each Fandom wiki (marvel 106,177 pages, dc 33,780). Lead wikitext fetched by S6970, one Haiku Batch call per page by S6971 (job folder compute/jobs/panscriptum-gap/).
Every row carries source_wiki, source_page_id, source_title and source_url; rows without a source are never written. Names are coined; summaries are original (no 4-word run or capitalised word from the page).
Files: `<wiki>.entries.jsonl.gz` (full entries with feats and powers `id:magnitude`), `<wiki>.master_rows.tsv` (rows for PANSCRIPTUM_MASTER.tsv, adds source_page_id/title/url and powers).
Ids: <REALM2>.<universe>.E<n>.originate.9NNNNN (invented omniverse entries, never page-sourced assays; renamed from "assay" per review A5, awaiting Marlon ruling) (counter compute/id_counters/gap_<host>, starts 900001).
DC: 23,764 of 33,780 accepted (70%). Marvel: 72,826 of 106,167 (69%). The rest failed the copy or name-leak check and can be retried.

## Run on the PC model router (S6972)
Jobs: `jobs/retry-dc.jobs.jsonl.gz` (10,016) and `jobs/retry-marvel.jobs.jsonl.gz` (33,341), the rows the first pass rejected. Each job already has its coined name, era and cleaned lead text.
```
python3 -I tools/panscriptum_gap/gap_run.py plans/panscriptum_gap/jobs/retry-dc.jobs.jsonl.gz out/dc.retry.jsonl Orintanum 1500001 --url http://127.0.0.1:8788/v1 --workers 3
python3 -I tools/panscriptum_gap/gap_run.py plans/panscriptum_gap/jobs/retry-marvel.jobs.jsonl.gz out/marvel.retry.jsonl Losaustanum 1600001 --url http://127.0.0.1:8788/v1 --workers 3
```
Resumable (rerun the same command). Rejected ids go to `<out>.rejected`. Add `--limit 200` for a pilot first. Commit the out files (they are the new entries, each with source page id and URL).
