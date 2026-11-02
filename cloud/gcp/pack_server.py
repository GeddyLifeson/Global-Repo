r"""Packs the test server (E:\MCTest\diaithir_server, else E:\MCTest\server) for the Google Cloud VM.

Writes E:\DiaithirRPG\.gcp\server.tar.partNN (380 MB each, so the cloud session can stage them) and server.sha256.
Same exclusions as tools/release/sync_pack.ps1: no world saves, logs, backups, player lists or test-only jars.
"""
import hashlib, pathlib, re, tarfile

SRC = next(p for p in map(pathlib.Path, (r"E:\MCTest\diaithir_server", r"E:\MCTest\server")) if (p / "mods").is_dir())
OUT = pathlib.Path(r"E:\DiaithirRPG\.gcp")
PART = 380 * 2**20
SKIP_DIRS = {"simplebackups", "backups", "logs", "crash-reports", "debug", ".mixin.out", "journeymap", "mapfrontiers", "mods_client_only"}
SKIP_FILES = re.compile(r"(whitelist|ops|banned-players|banned-ips|usercache|usernamecache)\.json|.*\.log|loadbots.*\.jar|server\.pid", re.I)


class Parts:
    """Write-only file that rolls over to a new part every PART bytes."""
    def __init__(self):
        self.n, self.f, self.left, self.sha = 0, None, 0, hashlib.sha256()

    def write(self, b):
        size = len(b)
        self.sha.update(b)
        while b:
            if not self.left:
                self.f and self.f.close()
                self.f, self.left, self.n = open(OUT / f"server.tar.part{self.n:02d}", "wb"), PART, self.n + 1
            chunk, b = b[:self.left], b[self.left:]
            self.f.write(chunk)
            self.left -= len(chunk)
        return size


def keep(info):
    rel = pathlib.PurePosixPath(info.name).relative_to("server")
    top = SRC / rel.parts[0] if rel.parts else SRC
    if rel.parts and (rel.parts[0] in SKIP_DIRS or (top.is_dir() and (top / "level.dat").exists())):
        return None
    return None if len(rel.parts) == 1 and SKIP_FILES.fullmatch(rel.name) else info


OUT.mkdir(exist_ok=True)
for old in OUT.glob("server.tar.part*"):
    old.unlink()
out = Parts()
with tarfile.open(fileobj=out, mode="w|") as tar:
    tar.add(SRC, arcname="server", filter=keep)
out.f.close()
(OUT / "server.sha256").write_text(f"{out.sha.hexdigest()}  server.tar\n")
print(f"{SRC} -> {out.n} parts in {OUT}, sha256 {out.sha.hexdigest()[:12]}")
