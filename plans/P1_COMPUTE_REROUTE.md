# P1 compute queue: disposition of the 7 jobs without out.jsonl (2026-11-09)

API is out of credit and Marlon said not to add any. Nothing below has been run. "Route" is the proposed lane, not a done move.

| Job | Rows | State | Proposed route |
|---|---|---|---|
| dish_comp_pick_1b | 110 | README says CLOSED | none, finished/closed |
| libmob_hab | 1484 | superseded by libmob_hab-s00..s07 | none, check those shards instead |
| roster-verify | script | PC script, no prompts | PC run: `python -I tools/verify_roster.py` (~6 min) |
| worldsys-code | 20 | out.direct 11, out.compat 20, partial 9 exist | merge existing outs, finish gaps in a code thread |
| relink-things | 9668 | held, Sonnet | jobs-local (ModelRouter) with TF-IDF top-1 fallback; in-thread only for the failed rows |
| panscriptum-gap | dc, marvel (+retries) | out.jsonl exists for dc, marvel, pilot; retry-* have no out | route retry-dc/retry-marvel to jobs-local |
| diaithirrpg-conflicts | 0 | empty folder | delete or give it an in.jsonl |

Running relink-things (9,668 rows) or the retries through session subagents would burn session tokens, the scarcest resource per master CLAUDE.md section 0; use free lanes first.
