#!/usr/bin/env python3
"""Panscriptum == modpack parity. Prints pack mods missing from the Panscriptum,
Panscriptum mods missing from the pack, and id-level gaps. Exit 1 on empty input, any mod-list gap, or more than MAX_GAP ids on either side.
Usage: python3 -I tools/panscriptum_parity.py [pack_item_ids.tsv] [library.sqlite] [MAX_GAP=0]"""
import sqlite3, sys
P = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/pack_item_ids.tsv"
L = sys.argv[2] if len(sys.argv) > 2 else "/mnt/project-files/codex-store/library.sqlite"
MAX_GAP = int(sys.argv[3]) if len(sys.argv) > 3 else 0
pack = {l.split("\t")[0] for l in open(P, encoding="utf-8") if ":" in l}
db = sqlite3.connect(f"file:{L}?mode=ro", uri=True)
lib = {r[0] for r in db.execute("select pack_id from entry where pack_id is not null")}
ns = lambda s: {i.split(":")[0] for i in s}
a, b = sorted(ns(pack) - ns(lib)), sorted(ns(lib) - ns(pack))
print(f"pack mods {len(ns(pack))}, Panscriptum pack-linked mods {len(ns(lib))}")
print(f"pack mods missing from Panscriptum ({len(a)}):", *a)
print(f"Panscriptum mods missing from pack ({len(b)}):", *b)
print(f"ids: pack {len(pack)}, linked {len(lib)}, pack ids without entry {len(pack-lib)}, entry ids not in pack {len(lib-pack)}")
bad = []
if not pack or not lib: bad.append("empty pack or library id set")
if a or b: bad.append("mod-list gap")
if max(len(pack - lib), len(lib - pack)) > MAX_GAP: bad.append(f"id gap above {MAX_GAP}")
if bad: print("FAIL:", "; ".join(bad))
sys.exit(1 if bad else 0)
