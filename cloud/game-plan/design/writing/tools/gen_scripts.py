#!/usr/bin/env python3
"""Parse the screenplay scripts in design/writing/scripts/**/*.md into dialogue_lines.csv.
Format: scripts/README.md. gen_dialogue.py then uses the voiced line counts for scripted scenes.
Run: python3 design/writing/tools/gen_scripts.py (build.py runs it first)."""
import csv, glob, os, re, sys, collections

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(W, 'scripts')
CAST = {'PLAYER': 'PLAYER', 'OSTRA': 'ACT_NPC_OSTRA', 'HUSH': 'ACT_BOSS_HUSH', 'TOMAS': 'ACT_NPC_WARDEN_TOMAS',
        'IRES': 'ACT_NPC_IRES', 'UI': 'UI', 'TITLE': 'UI'}
UNVOICED = {'UI'}
LINE = re.compile(r"^(\s*)(?:- \[([^\]]+)\] )?([A-Z][A-Z0-9_' ]*?)(?: \(([^)]*)\))?: (.+)$")
COLS = ['str_id', 'scene_id', 'quest_id', 'line_no', 'speaker', 'speaker_id', 'branch', 'tags', 'direction', 'text_en',
        'max_chars', 'voiced', 'script', 'status']


def parse(path, errs, warns):
    rel = os.path.relpath(path, W)
    cast, rows, qid, scene, n, branch = dict(CAST), [], '', None, 0, ''
    for i, raw in enumerate(open(path, encoding='utf-8'), 1):
        line = raw.rstrip('\n')
        where = f'{rel}:{i}'
        if line.startswith('# '):
            qid = line[2:].split()[0]
        elif line.startswith('Cast:'):
            for pair in line[5:].split(';'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    cast[k.strip()] = v.strip()
        elif line.startswith('## '):
            scene, n, branch = re.split(r'\s', line[3:].strip())[0], 0, ''
        elif scene and (m := LINE.match(line)):
            ind, tag, spk, paren, text = m.groups()
            if tag:
                branch = f'{scene}_{tag}'
            elif not ind:
                branch = ''
            if spk not in cast:
                errs.append(f'{where} speaker {spk} not in Cast')
                continue
            text = text.strip()
            if '...' in text or '…' in text or '\u2014' in text:
                errs.append(f'{where} ellipsis or em dash: {text[:50]}')
            if len(text) > 160:
                errs.append(f'{where} line {len(text)} chars, max 160')
            if spk == 'PLAYER' and len(text) > 50:
                warns.append(f'{where} player line {len(text)} chars')
            n += 1
            key = scene[4:] if scene.startswith('SCN_') else scene
            rows.append({'str_id': f'STR_DLG_{key}_{n:03d}', 'scene_id': scene, 'quest_id': qid, 'line_no': n, 'speaker': spk,
                         'speaker_id': cast[spk], 'branch': branch, 'tags': tag or '', 'direction': paren or '', 'text_en': text,
                         'max_chars': 70 if spk == 'PLAYER' else 160, 'voiced': 'no' if cast[spk] in UNVOICED else 'yes',
                         'script': rel, 'status': 'draft'})
    return rows


def write_id_requests(rows):
    """Actor, flag and counter ids the scripts use that no data/ table has yet, for the data owners."""
    ID = re.compile(r'\b(?:ACT|FLG|CNT)_[A-Z0-9_]+\b')
    data = os.path.join(os.path.dirname(os.path.dirname(W)), 'data')
    known = set()
    for p in glob.glob(os.path.join(data, '**', '*.csv'), recursive=True):
        known |= set(ID.findall(open(p, encoding='utf-8', errors='ignore').read()))
    used = collections.defaultdict(set)
    for r in rows:
        for t in ID.findall(r['speaker_id'] + ' ' + r['tags']):
            used[t].add(r['script'])
    with open(os.path.join(W, 'scripts_id_requests.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'kind', 'scripts'])
        for k in sorted(set(used) - known):
            w.writerow([k, k.split('_')[0].lower(), '; '.join(sorted(used[k])[:3])])


def main():
    errs, warns, rows = [], [], []
    lenient = '--lenient' in sys.argv   # build.py: leave out files with errors (work in progress) instead of stopping
    for p in sorted(glob.glob(os.path.join(SCRIPTS, '**', '*.md'), recursive=True)):
        if os.path.basename(p) not in ('README.md', 'CONTINUITY.md'):
            e = []
            got = parse(p, e, warns)
            if e and lenient:
                warns.append(f'left out {os.path.relpath(p, W)}: {len(e)} errors, first: {e[0]}')
            else:
                rows += got; errs += e
    dup = [k for k, v in collections.Counter(r['str_id'] for r in rows).items() if v > 1]
    if dup:
        errs.append(f'duplicate scene line ids, e.g. {dup[0]} (a scene id is used in two places)')
    with open(os.path.join(W, 'dialogue_lines.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    write_id_requests(rows)
    v = sum(r['voiced'] == 'yes' for r in rows)
    print(f'dialogue_lines.csv: {len(rows)} lines ({v} voiced), {len({r["scene_id"] for r in rows})} scenes, '
          f'{sum(len(r["text_en"].split()) for r in rows)} words; {len(warns)} warnings')
    for x in warns[:20] + errs[:40]:
        print(x)
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
