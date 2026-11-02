#!/usr/bin/env python3
"""Rebuild all Shardfall data: folder generators, then the link pass, then the validator. Usage: python3 data/tools/build.py"""
import subprocess, sys, os
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
steps = [('items', ['gen_items.py']), ('actors/tools', ['run_all.py']), ('ui/gen', ['ui_c.py']), ('tools', ['link.py']), ('tools', ['validate.py'])]
for cwd, args in steps:
    r = subprocess.run([sys.executable] + args, cwd=os.path.join(D, cwd), capture_output=True, text=True)
    print(f'{cwd}/{args[0]}: ' + (r.stdout.strip().splitlines() or [''])[-1])
    if r.returncode:
        print(r.stdout[-3000:], r.stderr[-3000:]); sys.exit(r.returncode)
