"""Merge assay entry-draft outputs and build retry jobs.
  python3 -I assay_merge.py merge    -> /mnt/project-files/library-content/assay_merged.jsonl (parseable entries; later source wins)
  python3 -I assay_merge.py retry N  -> compute/jobs/assay-retry-N/{in.jsonl,README.md} for ids whose text is not parseable JSON
Order of precedence (last wins): original assay-*/out.jsonl, assay-tail-*, assay-retry-*. Skips ({"skip":true}) are kept out of the merge but are not retried."""
import glob, json, sys
J = '/mnt/project-files/compute/jobs'
ONLY = 'Reply with only the single JSON object, with no other text before or after it.'
def dirs():
    allj = sorted(glob.glob(J + '/assay-*/'))
    kind = lambda d: 2 if '/assay-retry-' in d else 1 if '/assay-tail-' in d else 0
    return sorted(allj, key=lambda d: (kind(d), d))
def load():
    rows = {}
    for d in dirs():
        try:
            for line in open(d + 'out.jsonl'):
                try: r = json.loads(line); rows[r['id']] = r['text']
                except Exception: pass
        except OSError: pass
    return rows
def parsed(t):
    try: v = json.loads(t)
    except Exception: return None
    return v if isinstance(v, dict) else None
rows = load()
if sys.argv[1] == 'merge':
    ok = skip = bad = 0
    with open('/mnt/project-files/library-content/assay_merged.jsonl', 'w') as o:
        for i, t in rows.items():
            v = parsed(t)
            if v is None: bad += 1
            elif v.get('skip') or 'name' not in v: skip += 1
            else: v['id'] = i; o.write(json.dumps(v, ensure_ascii=False) + '\n'); ok += 1
    print(len(rows), ok, skip, bad)
else:
    n = sys.argv[2]; need = {i for i, t in rows.items() if parsed(t) is None}
    prompts = {}
    for d in dirs():                      # latest prompt for the id
        try:
            for line in open(d + 'in.jsonl'):
                r = json.loads(line)
                if r['id'] in need: prompts[r['id']] = r['prompt']
        except OSError: pass
    import os
    out = f'{J}/assay-retry-{n}'; os.makedirs(out, exist_ok=True)
    with open(out + '/in.jsonl', 'w') as f:
        for i in sorted(need & prompts.keys()):
            p = prompts[i] if ONLY in prompts[i] else prompts[i] + '\n\n' + ONLY
            f.write(json.dumps({'id': i, 'prompt': p}) + '\n')
    open(out + '/README.md', 'w').write('Retry of assay rows whose first and tail runs returned no parseable JSON. Same prompt plus a JSON-only line. max_tokens 800, thinking off, JSON only. Out rows {id, text}. Owner: library-content thread. Merge with assay_merge.py (retry wins).\n')
    print(len(need), len(need & prompts.keys()))
