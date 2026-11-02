"""Map genre roles, cert areas and GDC talks (genre_sources.csv) to owning design folders.
First matching rule wins. Writes genre_checklist.csv. Run: python3 tools/map_genre.py"""
import csv, os, re, collections
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESIGN = os.path.dirname(HERE)
RULES = [  # (regex on department+item, owner folder or UNOWNED:<group>)
 (r'nintendo', 'OUT_OF_SCOPE: plan platforms are PC, PS5, Xbox Series'),
 (r'rating|parental|child|personal information|regional ratings', 'production'),
 (r'store assets|storefront|purchasing|digital sales|eshop', 'liveops'),
 (r'locali|language', 'production'),
 (r'accessib', 'accessibility'),
 (r'haptic|adaptive trigger|controller behavior|button prompt', 'controls'),
 (r'monetization', 'liveops'),
 (r'companion app', 'companion'),
 (r'it support|release management', 'production'),
 (r'user-generated|forge|map-editor|editor asset', 'forgeframe'),
 (r'xbox xr|playstation trc|platform engineer|pc platform', 'platform'),
 (r'player support|customer service|trust & safety|crm', 'social'),
 (r'consumer products|licensing|transmedia|supply chain|manufacturing', 'licensing'),
 (r'community|esports|live ops|live content|marketing|public relations|brand|trailer|video editor|motion graphics designer \(marketing\)|digital marketing|consumer insights|product manager|commerce', 'liveops'),
 (r'user research|playtest|data scientist|analytics|statistician|insights manager|pro team', 'research'),
 (r'qa|quality|test|sdet', 'production'),
 (r'raid|strike|pvp|multiplayer modes|investment|engagement|progression|economy|difficulty', 'loops'),
 (r'level design|level designer|open world designer|modular level', 'levels'),
 (r'quest|story director|narrative director', 'campaign'),
 (r'narrative|writ|lore|universe|editor \(writing\)|managing editor', 'writing'),
 (r'combatant|bot ai|sandbox designer|systems designer|gameplay designer|game designer|technical designer|lead designer|head of design', 'systems'),
 (r'ux|ui |ui$|ui/|interface|graphic designer|motion \(ui\)|creative technologist', 'ui'),
 (r'cinemat|cg supervisor|colour script|layout artist|matte', 'cinematics'),
 (r'animat|mocap|motion capture|rigging|facial|performance \(mocap\)', 'art'),
 (r'voice actor|audio|sound|music|composer|dialogue|orchestr|conductor|mix', 'audio'),
 (r'simulation|wind|grass|vegetation', 'simulation'),
 (r'art|groom|look development|lighting|vfx|fx|skybox|terrain', 'art'),
 (r'engineer|programmer|architect|devops|build|release|infrastructure|telemetry|database|networking|rendering|stability|title quality|save|suspend|account|network|profile|display name|naming|dlc|content package|privileges|communication|leaderboard|headset|install|segmentation|sign-in|trophies|cross-gen|terminology', 'tech'),
 (r'world', 'world'),
 (r'.*', 'production'),  # leadership, production, outsourcing, finance, legal, HR, IT, facilities
]
R = list(csv.DictReader(open(os.path.join(HERE, 'genre_sources.csv'))))
out = []
for i, r in enumerate(R, 1):
    t = (r['department'] + ' ' + r['item']).lower()
    it = r['item'].lower(); dep = r['department'].lower()
    if 'nintendo' in dep:
        owner = RULES[0][1]
    elif 'xbox xr' in dep or 'trc' in dep:  # cert items go to the platform thread unless a topic owner exists
        owner = next((o for p, o in RULES[1:7] if re.search(p, it)), 'platform')
    else:  # item wins over department, so a role is not pulled in by its department name
        owner = next((o for p, o in RULES[:-1] if re.search(p, it)), None) or next(o for p, o in RULES if re.search(p, t))
    if ':' in owner: status = owner.split(':')[0].lower()
    else:
        p = os.path.join(DESIGN, owner) if owner not in ('ui',) else os.path.join(DESIGN, '..', 'data', 'ui')
        has = os.path.isdir(p) and any(f for _, _, fs in os.walk(p) for f in fs)
        status = 'owned, files present' if has else 'owned, in progress'
    out.append([f'GEN-{i:03d}', r['kind'], r['department'], r['item'], owner, status, r['games_or_platform'], r['source_url']])
with open(os.path.join(HERE, 'genre_checklist.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['id','kind','department','item','owner_folder','status','games_or_platform','source_url']); w.writerows(out)
c = collections.Counter(o[4] for o in out)
for k, v in sorted(c.items(), key=lambda x: -x[1]): print(v, k)
for o in out:
    if o[4].startswith('UNOWNED'): print(' ', o[4], '|', o[3])
