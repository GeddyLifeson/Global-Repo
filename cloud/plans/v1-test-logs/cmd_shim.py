"""Linux shim for tools/testrig/cmd.py: writes commands to the server console (cmd.txt read by boot.sh) and prints the new log."""
import os, sys, time
from pathlib import Path
ROOT = Path(os.environ.get("MCROOT", "/home/user/v1accept"))
LOG = ROOT / "server" / "logs" / "latest.log"
start = LOG.stat().st_size
with open(ROOT / "server" / "cmd.txt", "a", encoding="utf-8") as f:
    for c in sys.argv[1:]:
        f.write(c + "\n")
time.sleep(float(os.environ.get("WAIT", "3")))
with open(LOG, "rb") as f:
    f.seek(start)
    print(f.read().decode("utf-8", "replace")[-6000:])
