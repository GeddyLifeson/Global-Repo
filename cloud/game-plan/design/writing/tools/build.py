#!/usr/bin/env python3
"""Rebuild every writing table, merge data requests, then run the text checker.
Run after any change to data/ or design/campaign/: python3 design/writing/tools/build.py"""
import csv, glob, os, subprocess, sys
T = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(T)
subprocess.run([sys.executable, os.path.join(T, 'gen_scripts.py'), '--lenient'], check=True)
for g in ['gen_world_text.py', 'gen_item_text.py', 'gen_codex.py', 'gen_quest_text.py', 'gen_dialogue.py']:
    print('==', g); subprocess.run([sys.executable, os.path.join(T, g)], check=True)
rows = []
for fn in [os.path.join(T, 'manual_requests.csv')] + sorted(glob.glob(os.path.join(W, 'requests_*.csv'))):
    part = os.path.basename(fn).replace('requests_', '').replace('.csv', '').replace('manual_', 'writing')
    for r in csv.DictReader(open(fn)):
        rows.append([r['id'], r['request'], r['target_table'], r['notes'], part])
with open(os.path.join(W, 'data-requests.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'request', 'target_table', 'notes', 'part']); w.writerows(rows)
print('data-requests.csv', len(rows))
sys.exit(subprocess.run([sys.executable, os.path.join(T, 'check_text.py')]).returncode)
