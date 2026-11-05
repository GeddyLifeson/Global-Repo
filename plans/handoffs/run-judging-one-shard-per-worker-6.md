# Handoff: Run judging one shard per worker (6), GR branch claude/project-thread-ddv1l7, 11-05 ~20:52Z
Context hit 153k (cap 125k). Stopped launching.
## Method (b, coordinator-approved): split by page-text size, full reads
- tools/split.py (pushed): `ranges N` (~160k chars per part), `dump N lo hi` (full text), `check N lo hi part.json`, `merge N part.json...` (union, d=0, runs judge.py write + validate).
- Worker brief: /tmp/claude/partbrief.txt (lost on container reset; recreate: worker reads PLAYBOOK.md, `split.py dump`, reads ALL text in chunks, writes parts/shard_N_<lo>.json with b1,n,p,W,x,z,f,u0, runs `split.py check`, no commit, one-line reply. z "none stated: reason" REQUIRED for any being whose page has Abilities/Powers-type section but no power/x/feat). Parts missing z/n are fixed by a small fixer agent writing parts/shard_N_fix.json then re-merge with all parts.
- Parent merges, validates, commits, pushes. Keep validate.py strict.
## State
- PASS pushed: 85 (this thread), 65 (keyword-scanned, in SKIMMED.txt, must be redone under (b)), plus earlier passes from threads 4/5 (confirm full-read status; coordinator says unconfirmed ones go to SKIMMED.txt).
- Parts done, awaiting merge: 86 (parts 0, 97, 160 + fix agent aa60d125... was running; if parts/shard_86_fix.json exists merge all 4); 92 (parts 0, 109 done; part 182-250 running -> parts/shard_92_182.json); 105 (parts 0-54, 54-95 running; still need 95-174, 174-250).
- HOLD (resolver/lead-match, see HOLDS.txt): 1 (rows 44,77), 2 (row 119), 5 (rows 201,203-205; cfg diag/shard_5_write_cfg.json), 81 (row 184), 82 (only row 169 fails; parts complete, `split.py merge 82 parts/shard_82_{0,53,124,194,fix}.json`, copy in held/). 86 will also hold on rows 152 232 233 241 (lead-match) unless the PC fixes them.
- Not started: 87 (parts [0,53][53,134][134,196][196,250]), 106-113 115 116 118-120 123-136, 64 re-check (already PASS from thread 5), 1/2/5/81 redo after resolver fix.
- Over-2% held, awaiting PC resolver rerun: 0 3 51 80 99 101 102 152 and 4 12 13 14 88 89 93 94 96.
## Next steps
1. Check parts/ and merge/validate 86, 92 (after last part), 105; spawn fixers for z/n problems.
2. Launch remaining shards by `split.py ranges N`, max 6 workers.
3. Lead-match failures keep recurring (parenthetical romaji/kana stripped from batch leads): needs a resolver/lead re-cut on the PC side, not a validator loosening.
4. Redo SKIMMED.txt shards under (b); open draft PR ddv1l7 -> main (none yet); validate.py all.
