"""Merge cand_all.jsonl with vision outputs of dish_photo_pick_* into picks.json (id -> chosen photo with credit)."""
import json, re, sys, glob
cand = {}
for l in open('/mnt/project-files/dishes/cand_all.jsonl'):
    r = json.loads(l); cand[r['id']] = r['cand']
picks = {}
for f in sorted(glob.glob('/mnt/project-files/compute/jobs/dish_photo_pick_[0-9]*/out.jsonl')):
    for l in open(f):
        r = json.loads(l)
        try: j = json.loads(re.search(r'\{.*\}', r['text'], re.S).group(0)); b = int(j.get('best', 0))
        except Exception: continue
        if b and j.get('dish_visible', True) and r['id'] in cand and 1 <= b <= len(cand[r['id']]): picks[r['id']] = cand[r['id']][b - 1]
json.dump(picks, open('/home/user/work/photo/picks_all.json', 'w'), indent=1); print(len(picks), 'picked')
