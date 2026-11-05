# Handoff: Run judging one shard per worker (14), GR branch claude/project-thread-qpjd6w (canonical)
Recipe: handoff 13. Work dir plans/powers/judge. Brief tools/worker_brief.txt -> /tmp/wb.txt; Agent prompt "Read /tmp/wb.txt and follow it. SHARD=N LO=a HI=b." Max 6 parallel. Merge (run in background, takes >2 min): `python3 tools/autofix.py N parts/shard_N_[0-9]*.json; timeout 500 python3 tools/split.py merge N parts/shard_N_[0-9]*.json parts/shard_N_fix.json`.
Workers stop at ~60k after 10-15 rows on shard 3 (heavy pages): use ranges of ~12 rows.
## Passed and pushed
4 and 80 (out/ written, problems 0). 4 needed n[234]=Fireglide.
## Shard 3
All parts judged and merged. HOLD: row 125 lead-match only (see HOLDS.txt); merged output in held/. Needs resolver/lead fix, then re-merge, then move held/shard_3.* to out/.
## Shard 2
Held: row 119 fire-emblem|2851 needs resolver fix (PC). Parts shard_2_*.json exist. Merge once fixed.
## After
No unjudged ready shards remain. Other holds in HOLDS.txt (1, 2, 3, 5, 81, 82, 86, 92) need lead-match/resolver fixes. Check READY_SHARDS.txt on claude/project-thread-8lxbuh for newly ready shards.
