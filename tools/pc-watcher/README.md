# pc-watcher: run the API job watcher on the PC so it does not depend on cloud containers
Cloud containers restart every few minutes to an hour and kill the watcher. These scripts are the same watcher (`watch.py`), direct-call runner (`sync.py`), Batch runner (`batch.py`, only for READMEs that say "batch"), backlog resumer (`rescue.py`) and helper (`common.py`), made path-portable.

## What it needs
- Python 3 (any recent), no extra packages. Use the standard library only.
- The project-files folder as a real path. Default `/mnt/project-files`; on the PC set the environment variable `PROJECT_FILES` to the folder (for example the synced copy of compute/). It must contain `compute/jobs/`, `compute/secrets/anthropic_key` and `compute/ledger.csv`.
- The key is read from `compute/secrets/anthropic_key` when `ANTHROPIC_API_KEY` is not set. It is never written anywhere by these scripts. Do not copy it into this folder or into git.
- Optional `RUN_DIR` (where logs and `HOLD` live; defaults to this folder). Create an empty file named `HOLD` there to pause claiming; delete it to resume. Create it when the API says the usage limit is reached.

## Start it hidden (no windows, no .bat files)
Run through the existing hidden launcher, `E:\launch_hidden.ps1`, which starts a process with no console window. Two processes, started once:
1. `pythonw.exe -I <this folder>\watch.py` (claims new job folders within 5 s, runs `sync.py` per job, 96 threads each)
2. `pythonw.exe -I <this folder>\rescue.py` (resumes jobs that are claimed but short of their input rows; 10 jobs x 64 threads at a time; ends with "all done" in its output)
Use `pythonw.exe`, not `python.exe`, so no console appears. Wrap each in a loop at the launcher level (a scheduled task "at logon" with restart on failure) rather than a .bat. Logs: `<RUN_DIR>\<job>.log`.

## Do not run it twice
Only one watcher may run at a time (two would both claim folders; claims are `.claimed` files so double-claims are rare but runs double the spend). Before starting it on the PC, the cloud-side watcher has to be told to stop: create `/tmp/claude-0/run/HOLD` in the compute-lanes thread container, or just let it die. Tell the compute-lanes thread when the PC watcher is up.

## Behaviour to know
- Job folder protocol is in `compute/LANES.md`. README keys: `max_tokens N`, `model: haiku|sonnet|opus`, the words `sync` / `batch`.
- Rows resume from `out.jsonl`; a corrupted line (killed mid-write) makes sync.py crash with JSONDecodeError. Fix by keeping only lines that parse, then rerun.
- On a usage-limit reply ("You have reached your specified API usage limits") create `HOLD`; 400 replies drop the row.
