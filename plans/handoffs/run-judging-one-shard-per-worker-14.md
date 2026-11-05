# Handoff: Run judging one shard per worker (14), GR branch claude/project-thread-qpjd6w (canonical)
Recipe: handoff 13. Work dir plans/powers/judge. Brief tools/worker_brief.txt -> /tmp/wb.txt; Agent prompt "Read /tmp/wb.txt and follow it. SHARD=N LO=a HI=b." Max 6 parallel. Merge (run in background, takes >2 min): `python3 tools/autofix.py N parts/shard_N_[0-9]*.json; timeout 500 python3 tools/split.py merge N parts/shard_N_[0-9]*.json parts/shard_N_fix.json`.
Workers stop at ~60k after 10-15 rows on shard 3 (heavy pages): use ranges of ~12 rows.
## Passed and pushed
4 and 80 (out/ written, problems 0). 4 needed n[234]=Fireglide.
## Shard 3 (only other unjudged ready shard; cache+batches checked out from origin/claude/project-thread-8lxbuh, committed here)
Part files exist for: 0-16, 17-28, 62-73, 74-85(+86?), 57-61, 108-119, 120-142, 167-183, 185-196, 197-209, 210-249.
In flight when I stopped: 29-41, 41-57, 86-98, 98-108, 143-155 (check parts/ for shard_3_29, _41, _86, _98, _143).
Not launched: 155-167. Also 184 (167 worker covered 167-183) and 196 gaps: verify no row gap/overlap, e.g. 74 worker said rows 74-86 and 86 worker overlaps on 86; drop one.
Then merge 3.
## Shard 2
Held: row 119 fire-emblem|2851 needs resolver fix (PC). Parts shard_2_*.json exist. Merge once resolver fixed.
## After
Other holds in HOLDS.txt (5, 81, 1, 82, 86, 92) need lead-match fixes on the PC side.
