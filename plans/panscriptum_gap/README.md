# Panscriptum gap fill (character pages with no entry)
Source lists: Category:Characters of each Fandom wiki (marvel 106,177 pages, dc 33,780). Lead wikitext fetched by S6970, one Haiku Batch call per page by S6971 (job folder compute/jobs/panscriptum-gap/).
Every row carries source_wiki, source_page_id, source_title and source_url; rows without a source are never written. Names are coined; summaries are original (no 4-word run or capitalised word from the page).
Files: `<wiki>.entries.jsonl.gz` (full entries with feats and powers `id:magnitude`), `<wiki>.master_rows.tsv` (rows for PANSCRIPTUM_MASTER.tsv, adds source_page_id/title/url and powers).
Ids: <REALM2>.<universe>.E<n>.assay.9NNNNN (counter compute/id_counters/gap_<host>, starts 900001).
DC: 23,764 of 33,780 accepted (70%); rest failed the copy or name-leak check and can be retried.
