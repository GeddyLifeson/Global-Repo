# S6981 Kind power templates: detects a being's kind (vampire, zombie, ...) and fills powers its page does not state, from an editable per-kind (and per-franchise) table.
"""python3 kind_templates.py build OUT_DIR   (reads judged shards, writes OUT_DIR/KIND_TEMPLATES.tsv, BEING_KINDS.tsv; keeps rows whose source is not 'observed')
Files in OUT_DIR (edit freely):
  KIND_MAP.tsv        kind, x_tag_regex (judge x tags), text_regex (definition in the lead: 'is a ...'), name_regex.  Seeded from SEED below if missing.
  KIND_TEMPLATES.tsv  kind, scope ('*' or wiki slug), powers (pool_id:m,...), n, source_page (wiki|lead_idx of an example that states the kind), source (observed|manual|seed), note.
Rules: template = refinable reference. A page-stated power always keeps its page value; template only fills ids the page does not state. Per-franchise row (scope=wiki) beats '*'.
observed rows are rebuilt from page-stated powers each run (median m, ids in >=35% of the kind's beings), so recurring corrections feed back; manual/seed rows survive rebuilds and win over observed at the same scope."""
import re, os, sys, json, csv, glob, gzip, collections, statistics
SEED = [  # kind, x_tag_regex, text_regex, name_regex
 ('vampire', r'vampir|blood_drink|diablerie|life_drain', r'vampires?|nosferatu|strigoi|upir', r'vampire'),
 ('zombie', r'zombi', r'zombies?|walking dead', r'zombie'),
 ('undead', r'undea|undeath|lich|ghoul|draugr|revenant', r'undead|liches|lich|ghouls?|draugr|revenants?|skeletons?|wights?|mummy|mummies', r'undead|lich|ghoul|skeleton|mummy'),
 ('lycanthrope', r'lycan|werewolf|wolf_form', r'were-?(wolf|wolves|bear|tiger|cat|fox|rat)\w*|lycanthropes?|werecreatures?', r'were-?(wolf|bear|tiger|cat|fox|rat)'),
 ('ghost', r'ghost|spectr|wraith|spirit_form', r'ghosts?|specters?|spectres?|wraiths?|phantoms?|poltergeists?', r'ghost|phantom|specter|spectre|wraith'),
 ('demon', r'demon|devil|fiend', r'demons?|devils?|fiends?|daemons?|imps?|succubus|incubus', r'demon|devil|succubus|incubus'),
 ('angel', r'angel|celestial', r'angels?|archangels?|celestials?|seraphs?|seraphim', r'angel'),
 ('cyborg', r'cyborg|augment', r'cyborgs?', r'cyborg'),
 ('android', r'android|robot|automaton', r'androids?|robots?|automatons?|automata|gynoids?|replicants?', r'android|robot'),
 ('mutant', r'mutant|mutation', r'mutants?', r'mutant'),
 ('dragon', r'dragon', r'dragons?|wyrms?|drakes?|wyverns?', r'dragon|wyrm|drake'),
 ('deity', r'god_like|divine_creation|deity', r'(a|an|the) (\w+ )?(god|goddess|deity)|deities|titans?', r'^(god|goddess) '),
 ('elemental', r'elemental_being', r'elementals?', r'elemental'),
 ('golem', r'golem', r'golems?|constructs?', r'golem'),
 ('fae', r'fae|fairy|faerie|pixie|sprite', r'fae|fairy|fairies|faeries|pixies?|sprites?|nymphs?|dryads?', r'fairy|pixie|nymph'),
 ('giant', r'giant', r'giants?|ogres?|jotunn', r'giant|ogre'),
 ('shapeshifter', r'shapeshift|changeling|skinwalk', r'shapeshifters?|changelings?|skinwalkers?|doppelg\w+', r'shapeshifter|changeling|skinwalker|doppelg'),
]
NEG = re.compile(r'(hunter|slayer|killer|hunting|fighter|exterminator)s?\b', re.I)
def load_map(d):
    p = os.path.join(d, 'KIND_MAP.tsv')
    if not os.path.exists(p):
        with open(p, 'w', encoding='utf-8', newline='') as f:
            f.write('kind\tx_tag_regex\ttext_regex\tname_regex\n'); f.writelines('\t'.join(r) + '\n' for r in SEED)
    rows = [l.rstrip('\n').split('\t') for l in open(p, encoding='utf-8')][1:]
    return [(k, re.compile(x) if x else None, re.compile(r'\b(is|was|are|were|became|become)\s+(?:an?|the|one of the)?\s*(?:[\w\'-]+\s+){0,4}?(?:' + t + r')\b(?!\s+(?:hunters?|slayers?|killers?))', re.I) if t else None, re.compile(n, re.I) if n else None) for k, x, t, n in rows]
def detect(kmap, text, name, xtags):
    """kinds = [(kind, how)]: x tag from the judge, definition in the first 300 chars of the lead, or kind word in the name."""
    out, lead = [], text[:300]
    for k, xr, tr, nr in kmap:
        if xr and any(xr.search(t) for t in xtags): out.append((k, 'x'))
        elif tr and tr.search(lead): out.append((k, 'text'))
        elif nr and name and nr.search(name) and not NEG.search(name): out.append((k, 'name'))
    return out
def read_templates(d):
    p = os.path.join(d, 'KIND_TEMPLATES.tsv')
    if not os.path.exists(p): return {}
    t = {}
    for r in csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'):
        pw = {a.split(':')[0]: int(a.split(':')[1]) for a in r['powers'].split(',') if a}
        t[(r['kind'], r['scope'])] = {'powers': pw, 'src': r['source_page'], 'source': r['source']}
    return t
def template_for(tpl, kind, wiki):
    """franchise row beats '*'; franchise fills only ids it states, '*' the rest (no override)."""
    out = {}
    for sc in (wiki, '*'):
        r = tpl.get((kind, sc))
        if r:
            for pid, m in r['powers'].items(): out.setdefault(pid, (m, f"{kind}@{sc}", r['src']))
    return out
def iter_judged(shard_dir, extra=()):
    """yields (id, text, result) for shard outputs (+ extra jsonl files with text in sibling shard files)."""
    for f in sorted(glob.glob(os.path.join(shard_dir, 'shard_??.jsonl')) + glob.glob(os.path.join(shard_dir, 'shard_???.jsonl'))):
        o = f[:-6] + '.out.jsonl'
        if not os.path.exists(o): continue
        text = {}
        for l in open(f, encoding='utf-8'):
            d = json.loads(l); text[d['id']] = d['text']
        for l in open(o, encoding='utf-8'):
            try: d = json.loads(l)
            except Exception: continue
            if d.get('id') in text and d.get('b') == 1 and 'error' not in d: yield d['id'], text[d['id']], d
GENRE = {  # genre baseline for kinds whose pages state no powers; magnitude 1 = peak human (C3M). Editable via KIND_TEMPLATES.tsv; build never overwrites it once source is manual.
 'vampire': 'super_strength:1,super_speed:1,regeneration:1,dragon_form:1', 'zombie': 'immortal_body:1,super_strength:1', 'undead': 'immortal_body:1',
 'lycanthrope': 'dragon_form:1,super_strength:1,super_speed:1,regeneration:1', 'ghost': 'phase:1,invisibility:1,spectral_flight:1', 'demon': 'flight:1,fireball:1,super_strength:1',
 'angel': 'flight:1,energy_beam:1', 'cyborg': 'super_strength:1,hard_body:1', 'android': 'super_strength:1,super_speed:1,hard_body:1', 'dragon': 'flight:1,fireball:1,hard_body:1,giant_size:2',
 'deity': 'immortal_body:1', 'golem': 'super_strength:1,hard_body:1', 'fae': 'levitation:1,invisibility:1', 'giant': 'giant_size:2,super_strength:1'}
JUNK = re.compile(r'\b(quests?|builds?|game mode|rifles?|weapons?|perks?|achievements?|cards?|skins?|armou?r|enemy|enemies|boss|unit in|trophy|episode|walkthrough)\b', re.I)
def defining_pages(leads_dir='/mnt/project-files/assay-c3m/leads'):
    """lead pages that define the kind itself ('Vampires are ...', 'The lich is a ...'): (kind, wiki, idx, text)."""
    for f in sorted(glob.glob(os.path.join(leads_dir, '*.jsonl'))):
        wiki = os.path.basename(f)[:-6]
        for l in open(f, encoding='utf-8'):
            d = json.loads(l); t = d['text']
            if not (150 <= len(t) <= 2500) or JUNK.search(t[:200]): continue
            for k, x, tr, nr in SEED:
                if re.match(r'^(?:The |A |An )?(?:\w+ )?(?:' + tr + r')\s+(?:\([^)]*\)\s*)?(?:are|is)\b', t[:80], re.I): yield k, wiki, d['i'], t
def stated_powers(text, strong):
    """pool ids whose strong keyword occurs in the text -> (id, verbatim sentence); same keywords as S6961, magnitude 1 (peak human) unless refined by hand."""
    return {pid: re.search(r'[^.!?]*' + rx.pattern + r'[^.!?]*', text, re.I | re.S).group(0).strip()[:200] for pid, rx in strong.items() if rx.search(text)}
def build(out, shard_dir='/mnt/project-files/plans/powers/judge/inthread'):
    kmap = load_map(out)
    stat = collections.defaultdict(lambda: collections.defaultdict(list))  # (kind,scope) -> pid -> [m]
    nb, ex, rows = collections.Counter(), {}, []
    for pid, text, d in iter_judged(shard_dir):
        wiki = pid.split('|')[0]
        for k, how in detect(kmap, text, d.get('n', ''), d.get('x', [])):
            rows.append((pid, k, how)); 
            for sc in ('*', wiki):
                nb[(k, sc)] += 1; ex.setdefault((k, sc), pid)
                for p in d['p']: stat[(k, sc)][p['id']].append(p['m'])
    import judge_pages as jp
    strong = {r['id']: re.compile(r['keywords_strong'], re.I) for r in jp.pool_rows() if r.get('keywords_strong')}
    dfn = collections.defaultdict(list)  # (kind,scope) -> [(idx page, powers)]
    for k, wiki, i, t in defining_pages():
        sp = stated_powers(t, strong)
        for sc in ('*', wiki): dfn[(k, sc)].append((f'{wiki}|{i}', sp))
    old = {}
    if os.path.exists(os.path.join(out, 'KIND_TEMPLATES.tsv')):
        for r in csv.DictReader(open(os.path.join(out, 'KIND_TEMPLATES.tsv'), encoding='utf-8'), delimiter='\t'):
            if r['source'] == 'manual': old[(r['kind'], r['scope'])] = r
    res = dict(old)
    for key in set(nb) | set(dfn):
        n = nb[key]; dp = dfn.get(key, [])
        if key in old or (n < (5 if key[1] == '*' else 3) and len(dp) < (3 if key[1] == '*' else 2)): continue
        ps = {i: int(round(statistics.median(ms))) for i, ms in stat[key].items() if n and len(ms) / n >= 0.35}
        cnt = collections.Counter(i for _, sp in dp for i in sp)
        for i, c in cnt.items():
            if c / len(dp) >= 0.3: ps.setdefault(i, 1)  # stated by >=30% of the kind's defining pages
        src = next((pg for pg, sp in dp if sp), ex.get(key, ''))
        res[key] = {'kind': key[0], 'scope': key[1], 'powers': ','.join(f'{i}:{m}' for i, m in sorted(ps.items(), key=lambda a: (-a[1], a[0]))), 'n': n + len(dp), 'source_page': src or ex.get(key, ''), 'source': 'observed', 'note': ''}
    for k, *_ in kmap:  # every kind gets a row so it can be edited
        r = res.get((k, '*')) or {'kind': k, 'scope': '*', 'powers': '', 'n': nb[(k, '*')], 'source_page': ex.get((k, '*'), ''), 'source': 'seed', 'note': ''}
        if r['source'] != 'manual':  # genre baseline underneath what the pages state
            have = {a.split(':')[0] for a in r['powers'].split(',') if a}
            r = dict(r, powers=','.join([a for a in r['powers'].split(',') if a] + [a for a in GENRE.get(k, '').split(',') if a and a.split(':')[0] not in have]), note='observed powers first, then genre baseline (seed); refine' if k in GENRE else 'no baseline; varies by being')
            if r['source'] == 'observed' and GENRE.get(k): r['source'] = 'observed+seed'
            res[(k, '*')] = r
    with open(os.path.join(out, 'KIND_TEMPLATES.tsv'), 'w', encoding='utf-8', newline='') as f:
        f.write('kind\tscope\tpowers\tn\tsource_page\tsource\tnote\n')
        for key in sorted(res):
            r = res[key]
            if not r['powers'] and key[1] != '*': continue
            f.write('\t'.join(str(r.get(c, '')) for c in ('kind', 'scope', 'powers', 'n', 'source_page', 'source', 'note')) + '\n')
    with open(os.path.join(out, 'BEING_KINDS.tsv'), 'w', encoding='utf-8', newline='') as f:
        f.write('page_id\tkind\thow\n'); f.writelines('\t'.join(r) + '\n' for r in rows)
    print('kinded beings', len({r[0] for r in rows}), 'template rows', len(res))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if __name__ == '__main__' and sys.argv[1:2] == ['build']: build(sys.argv[2])
