#!/usr/bin/env python3
"""Make a 'v1 core' copy of a packwiz pack tree: drop the mods in v1_core_cutlist.json (mods with no Age I content).
usage: make_core.py PACK_DIR   (edits in place: removes mods/*.pw.toml or mods/*.jar whose jar filename is in the list,
then rewrites index.toml and pack.toml hashes). Work on a copy; do not run on the main pack."""
import json, sys, os, re, hashlib, tomllib
root = sys.argv[1]
cut = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v1_core_cutlist.json'))))
rm = []
for f in sorted(os.listdir(os.path.join(root, 'mods'))):
    p = os.path.join(root, 'mods', f)
    if f.endswith('.pw.toml'):
        fn = tomllib.load(open(p, 'rb')).get('filename', '')
        if fn in cut: rm.append(f)
    elif f in cut: rm.append(f)
for f in rm: os.remove(os.path.join(root, 'mods', f))
idx = open(os.path.join(root, 'index.toml')).read()
for f in rm:
    idx = re.sub(r'\[\[files\]\]\nfile = "mods/' + re.escape(f) + r'"\n(?:[^\[]*?)\n\n?', '', idx)
open(os.path.join(root, 'index.toml'), 'w').write(idx)
ih = hashlib.sha256(idx.encode()).hexdigest()
pk = open(os.path.join(root, 'pack.toml')).read()
pk = re.sub(r'(\[index\][^\[]*hash = ")[0-9a-f]+', lambda m: m.group(1) + ih, pk)
open(os.path.join(root, 'pack.toml'), 'w').write(pk)
print(f'removed {len(rm)} of {len(cut)} listed mods')
