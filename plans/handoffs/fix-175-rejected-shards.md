# Fix the 175 rejected judged shards: result 11-19
Branch claude/project-thread-n8vzje (PR #143). Full revalidation: 479 PASS, 2 REJECT (was 306 / 175). match_regress: 0 known-wrong accepted, 0/300 known-right rejected, 76 sibling false accepts (= baseline).
## Left
- Shard 143: every row marked b0, shard never judged. Needs a real judging pass (recipe plans/handoffs/judge-160-927.md).
- Shard 266: 7 identical stripped rows ("Obtained from , an item purchased in Moonglade during the Lunar Festival.") cannot be resolved to pages; 2 over the 2% cap. Needs the row source re-cut or a signed decision.
## Tools added (plans/powers/judge/tools)
lengthen_quotes.py, repoint_src.py, refresh_cache.py, resolve_nosrc.py. Edits are logged in HOLDS.txt (SRCEDIT, OVERRIDE) and SRCEDIT_nosrc_2026-11-19.tsv.
## Caveats
- 474+27 no-source rows resolved by exact title; beings got b1 with z "none stated"; items b0 (WoW armour left b0, as in earlier shards).
- 7 DC rows (shards 5, 8, 44, 85) had been judged against broken cached pages ("nl:Zatanna"); re-judged by hand. 4 signed OVERRIDEs (shards 5, 44, 113) for DC pages rewritten since the batch cut.
- Live check: 22 of 25 sampled quotes verbatim on the live wiki now; 3 gear quotes drifted (wiki edits since the cache). The validator uses the cache.
