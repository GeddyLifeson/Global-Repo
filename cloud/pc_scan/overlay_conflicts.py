"""For each overlay conflict on a target: if the target still holds the previous overlay version (OLD commit), or the
file is one fix_atm11_261.py re-patches, it is safe to take the new overlay version. Prints the classification;
with --write copies the safe ones. Usage: python -I overlay_conflicts.py <target root> <new overlay pack dir> <OLD> [--write]"""
import subprocess, sys
from pathlib import Path

target, new_pack, old = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
write = "--write" in sys.argv
REPATCHED = {"laser_drill.js", "controllers.js", "auto_forge.js", "runic_crucible.js", "runic_enchanter.js",
             "star_altar.js", "atm_star_creative.js", "sawing.js"}
safe, real = [], []
for f in sorted(p for p in (new_pack / "kubejs").rglob("*") if p.is_file()):
    rel = f.relative_to(new_pack)
    t = target / rel
    if not t.exists() or t.read_bytes() == f.read_bytes():
        continue
    prev = subprocess.run(["git", "-c", "safe.directory=*", "-C", r"E:\DiaithirRPG", "show",
                           f"{old}:tools/ports/pack/{rel.as_posix()}"], capture_output=True).stdout
    if (prev and t.read_bytes().replace(b"\r\n", b"\n") == prev.replace(b"\r\n", b"\n")) or rel.name in REPATCHED:
        safe.append(rel)
        if write:
            t.write_bytes(f.read_bytes())
    else:
        real.append(rel)
print("take new overlay:", len(safe))
for r in real:
    print("REAL CONFLICT", r)
