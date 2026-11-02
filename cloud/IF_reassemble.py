"""Rejoins the Industrial Factory resource pack zips from their 8 MB parts and checks every sha256.

    python reassemble.py [OUT_DIR]        (run inside the folder holding the parts, SHA256SUMS.txt, ZIP_SHA256SUMS.txt)

Writes "Industrial Factory N.zip" into OUT_DIR (default: this folder's parent "assembled"). Put all 12 zips in the
instance's resourcepacks folder."""
import hashlib, re, sys
from pathlib import Path

here = Path(__file__).resolve().parent
out = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "assembled"
out.mkdir(parents=True, exist_ok=True)
sha = lambda b: hashlib.sha256(b).hexdigest()
want = dict(l.split()[::-1] for l in (here / "SHA256SUMS.txt").read_text().splitlines() if l.strip())
bad = [n for n, h in want.items() if not (here / n).exists() or sha((here / n).read_bytes()) != h]
if bad:
    sys.exit("missing or corrupt parts: " + ", ".join(bad))
zips = {}
for p in sorted(here.glob("IF*.zip.part*")):
    zips.setdefault(re.match(r"IF(\d+)\.zip", p.name)[1], []).append(p)
final = {l[66:].strip(): l[:64] for l in (here / "ZIP_SHA256SUMS.txt").read_text().splitlines() if l.strip()}
for n, ps in sorted(zips.items(), key=lambda kv: int(kv[0])):
    name = f"Industrial Factory {n}.zip"
    data = b"".join(p.read_bytes() for p in ps)
    if final.get(name) and sha(data) != final[name]:
        sys.exit(f"{name}: joined file does not match its checksum")
    (out / name).write_bytes(data)
    print("ok", name, len(data))
print("done, copy the zips from", out)
