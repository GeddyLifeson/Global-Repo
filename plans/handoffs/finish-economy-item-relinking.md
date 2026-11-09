# Handoff: Finish economy item relinking (J10 successor)

Written 2026-11-09 ~18:55Z at 210k context. Quiet-thread rule applies.

## Done
- relink-things COMPLETE: 97 shards, 9,668 rows, 1,313 picks. plans/relink/s000-s096.tsv on GR claude/project-thread-yzyymm (draft PR #128). out.jsonl written to /mnt/project-files/compute/jobs/relink-things/ ({id,text,lane}, text ends {"pick": N}). P1_COMPUTE_REROUTE.md row updated.
- Method used: one Sonnet Agent per 100-row shard (brief + shard file in the scratchpad), up to 20 at once (hard cap 20 concurrent). A lexical prefilter was tested and rejected: it would lose ~44% of true matches.

## Next: panscriptum-gap retries (coordinator said do in-session, DC first then Marvel, Sonnet subagents in parallel, push in batches, stop at 90% weekly usage)
Jobs: /mnt/project-files/compute/jobs/panscriptum-gap/retry-dc/dc.fandom.com.jobs.jsonl (10,016 rows) and retry-marvel/marvel.fandom.com.jobs.jsonl (33,341 rows). Row fields: id ("host|pid"), pid, title, name, era, text. These are the rows that failed in the first API run.

THE SPEC IS FOUND: GR branch `claude/project-thread-28p9u0`, tools/panscriptum_gap/ (gap_batch.py, originate_prompt.txt, gap_run.py, fetch_leads.py). Fetch with `git show origin/claude/project-thread-28p9u0:tools/panscriptum_gap/gap_batch.py`.
- System prompt SYS = originate_prompt.txt with the first "Return JSON only" line replaced and EXTRA appended, exactly as built at the top of gap_batch.py. Build it by importing/exec'ing that file's SYS (do not retype).
- User message per row = json.dumps({"name": row.name, "text": row.text}). Model reply = JSON with summary, feats, realm, ceiling_T, powers.
- Validation + entry build: `accept(j, txt, host, univ, n)` in gap_batch.py (rejects copied 4-grams, leaked capitalised words from title/text, bad realm, etc.). Rows that fail are dropped.
- Universe: source_universe_map.json (/mnt/project-files/assay-c3m/); dc -> Orintanum. Check marvel's value.
- Id counter: /mnt/project-files/compute/id_counters/gap_<host> holds the next number (starts 900001); the first dc run used 900200-923963, so READ the file before writing and update it after. Ids look like MY.orintanum.E6.assay.<n>.
- Append accepted entries to a NEW file (e.g. retry-dc/out.jsonl), never edit dc/out.jsonl. Source fields (host, pid, title, url) are mandatory.
- Check the 3 retry titles/pids are not already in dc/out.jsonl (checked: 0 overlap for dc).

## Suggested orchestration (keep own context small)
1. Write a small script (python3 -I) that splits the retry file into shards of ~60-80 rows as text files (name + text) in the scratchpad.
2. Per shard, an Agent (model sonnet, background): read /tmp/.../sys.txt (the SYS prompt) and the shard, write one line per row {"id":..., "reply": <JSON object>} to out/<shard>.jsonl, reply only with a count.
3. A script runs accept() on every reply, assigns ids from the counter, appends to the out file. Run it after each wave and push (GR branch yzyymm, plans/ + out file in job folder; the job folder is a network mount, /mnt/project-files is nearly full).
4. Each agent launch+result costs ~1k tokens of coordinator context, so batch many shards per agent (agents can loop over several shard files) and consider a lead agent per ~10 shards.
5. Tick P1 in plans/V1_CHECKLIST.md with the counts when done.

## Rules reminders
Never merge, no GitHub Actions, never delete PANSCRIPTUM_MASTER entries, no invented entries (validator enforces), do not use the Workflow tool, no Anthropic API (no credit).
