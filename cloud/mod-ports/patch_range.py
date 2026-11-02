"""Relax one dependency versionRange in a NeoForge jar's mods.toml (open-licence mods only).
Usage: patch_range.py IN.jar OUT.jar MODID_OF_DEPENDENCY NEW_RANGE"""
import re
import sys
import zipfile

src, dst, dep, rng = sys.argv[1:5]
zi = zipfile.ZipFile(src)
zo = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for it in zi.infolist():
    b = zi.read(it.filename)
    if it.filename == 'META-INF/neoforge.mods.toml':
        t = b.decode()
        t, n = re.subn(r'(modId\s*=\s*"%s"[^\[]*?versionRange\s*=\s*)"[^"]*"' % re.escape(dep), r'\1"%s"' % rng, t, flags=re.S)
        print('patched', n)
        b = t.encode()
    zo.writestr(it, b)
zo.close()
