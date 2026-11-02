"""Rejoins a jar from its 8 MB parts and checks every sha256.

    python jar_reassemble.py JAR_NAME [OUT_DIR]     (run in the folder holding JAR_NAME.partNNN and JAR_NAME.parts.sha256)

Needs JAR_NAME.parts.sha256 (one "hash  part" line per part) and JAR_NAME.sha256 (hash of the whole jar).
Writes JAR_NAME into OUT_DIR (default: ./assembled)."""
import hashlib, sys
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit(__doc__)
here = Path(__file__).resolve().parent
name = sys.argv[1]
out = Path(sys.argv[2]) if len(sys.argv) > 2 else here / "assembled"
out.mkdir(parents=True, exist_ok=True)
sha = lambda b: hashlib.sha256(b).hexdigest()
parts = [l.split() for l in (here / f"{name}.parts.sha256").read_text().splitlines() if l.strip()]
bad = [p for h, p in parts if not (here / p).exists() or sha((here / p).read_bytes()) != h]
if bad:
    sys.exit("missing or corrupt parts: " + ", ".join(bad))
data = b"".join((here / p).read_bytes() for _, p in parts)
want = (here / f"{name}.sha256").read_text().split()[0]
if sha(data) != want:
    sys.exit("joined jar does not match its checksum")
(out / name).write_bytes(data)
print("ok", name, len(data), want)
