# Handoff: bulk judge page download (PC)
State: repo E:\work\gr (branch claude/project-thread-8lxbuh). bulk.py 0 5 2 running since 10:51 (log E:\work\bulk_a.log), no output yet; shard 0/1 src.jsonl not written after ~10 min (wiki resolve slow or 429-retrying; check with Get-CimInstance for bulk.py).
Inputs: shard_NN.jsonl only in project library (read_project_file plans/powers/judge/inthread/shard_NN.jsonl). Done 00-19, placed at E:\mnt\project-files\plans\powers\judge\inthread\ (OLD path from E: cwd). Each read saves a tool-results blob; E:\work\place.py maps blobs sorted by timestamp to shard_NN in order (sequential calls only, never skip a number). Next: 20..159.
Then: python plans/powers/judge/tools/bulk.py 0 160 2 from E: drive; commit cache+batches every 20 shards, push to branch. Bash allow rule for bulk.py granted by Marlon.
When shards 0-4 land: message judge lane thread cmsg_01EpyoqYuwV3X4z3b4zk5pEKULbNT7MtmcLmgbLY9DuN9Q directly.
