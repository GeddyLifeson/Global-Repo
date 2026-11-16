# Handoff: Finish economy, rites and misc items (J10)

Context hit 125k at 2026-11-09 ~18:40Z. Quiet thread rule applies.

## Done
- V1_CHECKLIST: M7 and Z5 ticked with evidence; L1,L2,L7,L11,L12,M2,P3 marked BLOCKED with the needed id. PR: global-repo #128 (draft, branch claude/project-thread-yzyymm, base claude/project-thread-wx17x3).
- plans/P1_COMPUTE_REROUTE.md lists the 7 compute jobs without out.jsonl.

## P1 in progress: relink-things (9,668 rows, in /mnt/project-files/compute/jobs/relink-things/in.jsonl)
- Coordinator said run in-thread with subagents (API has no credit; Marlon said no credit). Cheap TF-IDF script was tested and is NOT accurate enough to auto-accept, so every row is judged by a Sonnet subagent.
- Method: `python3 -I plans/relink/make_shards.py <in.jsonl> <dir>` makes 97 shards s000..s096 (100 rows each, ~130k tokens each). One Agent (model sonnet, background) per shard reads it, writes out/sNNN.tsv `id<TAB>pick` (0 = none), replies with nonzero count. Pilot s000: 16/100 matched.
- Finished and saved to plans/relink/*.tsv: whatever is there at handoff (check ls). Shards launched but possibly unfinished when this was written: s011-s024 (outputs land in the old thread scratchpad out/, may be lost if the container is reclaimed; rerun any shard with no tsv).
- Do NOT use the Workflow tool (needs Marlon's explicit opt-in); use the Agent tool, about 12 at a time.
- Remaining after all 97 tsvs exist: build out.jsonl in the job folder format ({id,text,lane}, text ending in {"pick": N}) or a merged tsv in the job folder, commit tsvs to GR, then run panscriptum-gap retry-dc and retry-marvel (jobs.jsonl in /mnt/project-files/compute/jobs/panscriptum-gap/retry-*/), same shard-and-judge method, then tick P1 with the ledger/out evidence.

## Notes
- Marlon's scale approval (relayed by coordinator, not cited): about 200M tokens allowed, stop at 90% weekly usage.
- API key present but returns "credit too low". Do not use.
