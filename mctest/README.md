# mctest: overnight test tooling (review Batch 5, G2-G15)

`overnight_watchdog.py` (S6990) replaces the prose plan `overnight-client-run.md`. Stdlib only, Windows. Copy it to `C:\MCTestServer\tools\` and start it with `E:\launch_hidden.ps1` (hidden window). PC launches only 2 AM-4 PM Chicago while Marlon is away. Live `run` is UNTESTED; the stage scanner and heap check were only dry-run on synthetic logs.

```
python overnight_watchdog.py preflight                 # read-only machine checks
python overnight_watchdog.py dry-run <server_latest.log> [client_latest.log]   # stage verdicts from existing logs, no launch
python overnight_watchdog.py --config cfg.json run     # launch, watch, write overnight\overnight_result.md
```
`cfg.json` overrides keys in `CFG` (set `client_cmd`, `client_dir`, `client_gc_log` first; client_cmd is empty by default so no client starts until Marlon's real Prism line is filled in).

## What each finding became
| ID | Where |
|---|---|
| G2 | the script itself (one file, owns its PIDs, kills only those, `taskkill` after RCON `stop` + 120 s) |
| G3 | stage table with per-stage budgets; silent resource-reload stage judged by `gc.log` (>=95% heap after GC for 3 samples = FAIL "heap too small"), not log mtime or CPU |
| G4 | preflight: free RAM >= 20 GB, free commit >= 24 GB, >= 10 GB free again before the client starts; no "Press Yes" path, any shortfall aborts |
| G6 | refuses to start a client if any `javaw` already runs; never clicks through an error screen; no relaunch |
| G7 | `ram.csv` row every 60 s; on an unexplained exit the bundle holds the last RAM rows. Windows event IDs 1074/6006/41/2004 are NOT read yet (follow-up) |
| G8 | RCON items run with a log line as evidence; player set to creative via RCON right after join. Input-driven items (Offgrid x3, Space-fire tank, Tool Belt, Codex, title screen) are written as NOT RUN until an input helper has a dry-run; they stay a one-page checklist for Marlon |
| G10 | stage budgets come from wall time (JVM start to Done), not the "Done (Ns)" figure; result rows carry both log line numbers so both can be read |
| G11 | server command is fixed in `CFG["server_cmd"]` with the .116 args file; preflight fails if that file is missing. Deleting the .78 and .109 libraries stays Marlon's call |
| G12 | baseline counts to compare later boots against are in FULL_REVIEW G12; counting them in the script is a follow-up |
| G13 | not done here: the "obtainable" category drop and the 37 follow-up rows need the PC harness (`run_all.py`) |
| G14 | client dir is a config key (`client_dir`); stating which Prism root is production belongs in the master CLAUDE.md |
| G15 | preflight checks every jar in both mods folders for `neoforge.mods.toml` and the D&T jar size; the diff against the pack index is a follow-up |

## Pass evidence
`overnight_result.md` has one row per stage and test with PASS/FAIL/NOT RUN, file, line number and the quoted line. Screenshots are not taken (current captures leak other windows, G9); a failure bundle holds log tails, `ram_tail.csv` and `jcmd Thread.print` only. Never commit `server.properties`, screenshots or the bundle.
