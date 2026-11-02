#!/usr/bin/env python3
"""Builds design/cinematics/data-requests.csv from cinematics.csv and shots.csv. Run after gen_cinematics.py."""
import csv, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
C = list(csv.DictReader(open(os.path.join(D, 'cinematics.csv'))))
rows = []
for c in C:
    i = c['cin_id'][4:]
    rows.append((f'ANIM_CIN_{i}', 'new asset', 'assets/asset_hooks.csv', f'Level Sequence and capture for {c["cin_id"]} ({c["runtime_s"]} s, tier {c["tier"]})'))
    rows.append((f'SFX_CIN_{i}_*', 'new asset', 'assets/asset_hooks.csv', f'Per-beat SFX hooks for {c["cin_id"]}; see shots.csv sfx_hook'))
    if not c['music_cue']: rows.append((f'MUS_CIN_{i}', 'new cue', 'design/audio/music_cues.csv', f'Cue for {c["cin_id"]}, {c["runtime_s"]} s; audio may fold short IGCs into region stingers'))
    rows.append((f'STR_CIN_{i}_TITLE', 'new string', 'ui/strings.csv', f'Scene title for the Theater replay menu: "{c["title"]}"'))
vfx = sorted({s['vfx'] for s in csv.DictReader(open(os.path.join(D, 'shots.csv'))) if s['vfx']})
rows += [(v, 'new asset (if missing)', 'assets/asset_hooks.csv', 'Hero cinematic VFX, see previs.csv hero_vfx') for v in vfx]
rows += [('DLG_<CIN>_<nn>', 'new lines', 'design/writing', 'Every line_ref in shots.csv needs a written line; writing thread owns text and VO IDs'),
 ('STR_SET_CINE_HIDE_HELMET', 'new string', 'ui/strings.csv', 'Setting: Hide Helmet in Cinematics (default Off)'),
 ('STR_SET_CINE_REDUCE_MOTION', 'new string', 'ui/strings.csv', 'Setting: Reduce Camera Motion (removes handheld, shake, slow-mo)'),
 ('STR_SET_ITEM_REVEAL_CAM', 'new string', 'ui/strings.csv', 'Setting: Item Reveal Camera (default On)'),
 ('PRM_CIN_HOLD_SKIP', 'new popup', 'ui/popups.csv', 'Prompt "Hold {BTN_CONFIRM} to skip", appears after 1 s, bottom right'),
 ('PRM_CIN_COOP_SKIP', 'new popup', 'ui/popups.csv', 'Prompt "{n}/{m} ready to skip" in co-op'),
 ('UI_MENU_THEATER', 'new screen', 'ui/', 'Theater replay menu in Extras: seen CUT scenes by act, needs a seen flag per CIN'),
 ('CIN_OPEN input log', 'save field', 'design/tech (save system)', 'Store the order and timing of the 3 prompts in CIN_OPEN so CIN_MUTINY replays the player\'s exact inputs')]
with open(os.path.join(D, 'data-requests.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id', 'request', 'target_table', 'notes']); w.writerows(rows)
print(len(rows), 'requests')
