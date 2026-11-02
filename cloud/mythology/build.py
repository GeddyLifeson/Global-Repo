"""Build mythology data from src/pantheons.txt. Run: python3 -I build.py
Names: two English words looked up in the Diaithiris lexicon, joined head+qualifier like the culture names.
"""
import json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
LEX = json.load(open('/mnt/project-files/diaithiris-archaic/LEXICON.json', encoding='utf8'))['entries']
NOUN = ('n', 'n. m.', 'n. f.', 'n. pl.')
lex = {}
for e in LEX:
    k = e['en'].lower()
    if k not in lex or (e['pos'] in NOUN and lex[k][1] not in NOUN):
        lex[k] = (e['rod'], e['pos'])
FORBID = set(json.load(open('/mnt/project-files/diaithiris-archaic/NAMES_MAP.json', encoding='utf8')).keys()) if os.path.exists('/mnt/project-files/diaithiris-archaic/NAMES_MAP.json') else set()
miss = set()

def name(words):
    out = ''
    for w in words.split(','):
        w = w.strip().lower()
        r = lex.get(w)
        if not r:
            miss.add(w); return None
        out += re.sub(r'[\s\-\']', '', r[0])
    return out[:1].upper() + out[1:]

AGE_ROMAN = 'I II III IV V VI VII'.split()
trad, cur, used = [], None, {}
for line in list(open(os.path.join(H, 'src/pantheons.txt'), encoding='utf8')) + list(open(os.path.join(H, 'src/age1_generated.txt'), encoding='utf8')) + list(open(os.path.join(H, 'src/later_ages.txt'), encoding='utf8')):
    line = line.rstrip('\n')
    if not line or line[0] == '#': continue
    p = line.split('|')
    if p[0] == 'T':
        cur = dict(id=p[1], title=p[2], region=p[3], status=p[4], age=int(p[5]), basis=p[6], rule=p[7], gods=[], creatures=[])
        trad.append(cur)
    elif p[0] == 'G':
        n = name(p[3]); cur['gods'].append(dict(rank=p[1], domain=p[2], name=n, words=p[3], emblem=p[4], offering=p[5]))
    elif p[0] == 'C':
        n = name(p[2]); cur['creatures'].append(dict(label=p[1], name=n, words=p[2], habitat=p[3], preset=p[4], hostile=p[5] == 'y', have=p[6]))
if miss:
    print('MISSING', sorted(miss)); sys.exit(1)
# uniqueness: suffix a tradition marker where a name repeats
seen = {}
for t in trad:
    for g in t['gods'] + t['creatures']:
        seen.setdefault(g['name'], []).append((t['id'], g))
dups = {n: v for n, v in seen.items() if len(v) > 1}
SUF = ['ach', 'achur', 'ain', 'oir', 'ad', 'ean', 'uil', 'ein', 'ird', 'ang', 'orn', 'eil']
taken = set(seen)
for n, v in dups.items():
    for i, (tid, g) in enumerate(v[1:]):
        k, cand = i, n + SUF[i % len(SUF)]
        while cand in taken:
            k += 1; cand = n + SUF[k % len(SUF)] + SUF[(k // len(SUF)) % len(SUF)]
        taken.add(cand); g['name'] = cand
json.dump(trad, open(os.path.join(H, 'mythology_full_WRITERS_ONLY.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(len(trad), 'traditions', sum(len(t['gods']) for t in trad), 'gods', sum(len(t['creatures']) for t in trad), 'creatures', len(dups), 'duplicate names fixed')

# ---------- outputs ----------
EFFECT = [  # keyword in domain -> (effect id, what the player feels)
 ('king', 'resistance', 'Damage resistance'), ('sovereign', 'resistance', 'Damage resistance'), ('war', 'strength', 'Strength'), ('battle', 'strength', 'Strength'), ('sword', 'strength', 'Strength'),
 ('storm', 'speed', 'Speed in rain'), ('thunder', 'strength', 'Strength in rain'), ('rain', 'speed', 'Speed in rain'),
 ('sea', 'dolphins_grace', 'Swim speed'), ('water', 'water_breathing', 'Water breathing'), ('river', 'dolphins_grace', 'Swim speed'), ('lake', 'water_breathing', 'Water breathing'),
 ('harvest', 'saturation', 'Slower hunger'), ('grain', 'saturation', 'Slower hunger'), ('maize', 'saturation', 'Slower hunger'), ('rice', 'saturation', 'Slower hunger'), ('field', 'saturation', 'Slower hunger'), ('plough', 'saturation', 'Slower hunger'), ('cattle', 'saturation', 'Slower hunger'), ('fruit', 'saturation', 'Slower hunger'), ('apple', 'saturation', 'Slower hunger'), ('peach', 'saturation', 'Slower hunger'),
 ('smith', 'haste', 'Mining speed'), ('forge', 'haste', 'Mining speed'), ('craft', 'haste', 'Mining speed'), ('iron', 'haste', 'Mining speed'), ('mountain', 'haste', 'Mining speed'),
 ('death', 'resistance', 'Damage resistance'), ('dead', 'resistance', 'Damage resistance'), ('underworld', 'resistance', 'Damage resistance'),
 ('heal', 'regeneration', 'Regeneration'), ('mercy', 'regeneration', 'Regeneration'), ('sun', 'regeneration', 'Regeneration by day'), ('light', 'regeneration', 'Regeneration by day'),
 ('hunt', 'night_vision', 'Night vision'), ('moon', 'night_vision', 'Night vision'), ('night', 'night_vision', 'Night vision'), ('forest', 'speed', 'Speed in woods'), ('wolf', 'speed', 'Speed'),
 ('wisdom', 'xp_gain', 'Extra experience'), ('magic', 'xp_gain', 'Extra experience'), ('learning', 'xp_gain', 'Extra experience'), ('scribe', 'xp_gain', 'Extra experience'), ('poetry', 'xp_gain', 'Extra experience'), ('music', 'xp_gain', 'Extra experience'),
 ('trickster', 'speed', 'Speed'), ('messenger', 'speed', 'Speed'), ('road', 'speed', 'Speed'), ('crossroad', 'speed', 'Speed'), ('hearth', 'fire_resistance', 'Fire resistance'), ('fire', 'fire_resistance', 'Fire resistance'), ('kitchen', 'fire_resistance', 'Fire resistance'),
 ('wealth', 'luck', 'Luck'), ('fate', 'luck', 'Luck'), ('luck', 'luck', 'Luck'), ('fortune', 'luck', 'Luck'), ('oath', 'luck', 'Luck'),
]
def effect(dom):
    d = dom.lower()
    for k, e, label in EFFECT:
        if k in d: return e, label
    return 'luck', 'Luck'
OFFER = {'grain': 'grain', 'honey': 'honey', 'milk': 'milk', 'drink': 'a drink', 'salt': 'salt', 'flower': 'flowers', 'incense': 'incense', 'metal': 'worked metal', 'fish': 'fish', 'fruit': 'fruit', 'bread': 'bread', 'hide': 'hides', 'cloth': 'woven cloth', 'bone': 'carved bone', 'ink': 'ink and parchment', 'coin': 'coins', 'amber': 'amber', 'rice': 'rice', 'corn': 'corn', 'water': 'clean water', 'palm': 'palm oil', 'ochre': 'ochre', 'chicha': 'brew', 'coca': 'leaf offerings', 'fat': 'rendered fat'}
RANKN = {'H': 'high', 'M': 'middle', 'L': 'lesser'}
RANKF = {'H': 4, 'M': 3, 'L': 2}  # offering value multiplier
lib, gods_out, crit_out = [], [], []
LORE = json.load(open(os.path.join(H, 'src/lore_lines.json'), encoding='utf8')) if os.path.exists(os.path.join(H, 'src/lore_lines.json')) else {}
for t in trad:
    age, living = t['age'], t['status'] == 'living'
    temple, vault = min(age + 1, 7), min(max(age + 1, 3), 7)
    court = t['title'].split(' (')[0]
    court = court[4:] if court.startswith('The ') else court
    court = 'the ' + court
    names = ', '.join(g['name'] for g in t['gods'] if g['rank'] == 'H')
    lib.append([court[0].upper()+court[1:], 'faction', age, 'mythology',
      f"A court of {len(t['gods'])} gods kept in {t['region']}. Its wayside shrines open in Age {AGE_ROMAN[age-1]}, its temples in Age {AGE_ROMAN[temple-1]}, and its temple vaults act as banks from Age {AGE_ROMAN[vault-1]}. Highest of them: {names}."
      + (" It is a living tradition in the world, so the game offers worship, blessings and shrines only." if living else " Its gods can bless the faithful, curse the oath-breaker and appear in the world.")])
    for g in t['gods']:
        e, lab = effect(g['domain'])
        offer = OFFER.get(g['offering'], g['offering'])
        tiers = {'H': 'every blessing tier', 'M': 'blessings up to rank 3', 'L': 'blessings up to rank 2'}[g['rank']]
        s = (f"A {RANKN[g['rank']]} god of {court}: {g['domain']}. Emblem: {g['emblem']}. Likes {offer}. Favour 0 to 100 gives {tiers}; the blessing is {lab} (one level per rank). Shrines in Age {AGE_ROMAN[age-1]}.")
        if not living: s += " Breaking an oath at its shrine brings a one-day curse until you make an offering."
        s = (LORE.get('god:%s.%s' % (t['id'], g['name'].lower())) + ' ' if 'god:%s.%s' % (t['id'], g['name'].lower()) in LORE else '') + s
        lib.append([g['name'], 'being', age, 'gods', s])
        gods_out.append(dict(id=f"{t['id']}.{g['name'].lower()}", name=g['name'], court=t['id'], rank=g['rank'], domain=g['domain'], emblem=g['emblem'], offering=g['offering'], effect=e, age=age, living=living))
    for c in t['creatures']:
        hostile = c['hostile'] and not living
        preset = c['preset'] if not living else ('beast' if c['preset'] == 'beast' else 'flyer')
        capage = min(age + (1 if preset == 'avatar' else 0), 7)
        if living: how = f"A gentle {c['habitat']} spirit-animal of {court}. It cannot be hurt, may follow a pilgrim to a shrine and gives a small blessing once a day."
        elif preset == 'avatar': how = f"An avatar of {court}, found at its mythic sites among the {c['habitat']}. A two-phase boss; it drops a relic of the court and, when beaten, ends the curse on the player who faced it."
        elif hostile: how = f"A hostile creature of {court} among the {c['habitat']}."
        else: how = f"A creature of {court} among the {c['habitat']}; it keeps to itself unless harmed and can be {'ridden once tamed' if preset == 'flyer' else 'tamed'}."
        if c['have'] != '-': how += " Uses the existing model and art."
        how = (LORE.get('creature:%s.%s' % (t['id'], c['name'].lower())) + ' ' if 'creature:%s.%s' % (t['id'], c['name'].lower()) in LORE else '') + how
        lib.append([c['name'], 'being', capage, 'creatures', how])
        crit_out.append(dict(id=f"{t['id']}.{c['name'].lower()}", name=c['name'], court=t['id'], habitat=c['habitat'], preset=preset, hostile=hostile, invulnerable=living, age=capage, existing=c['have'], living=living, home=t['region']))
CONCEPTS = [
 ["Favour", "concept", 1, "mythology", "Each player holds favour from 0 to 100 with each god. An offering at a shrine adds 2, 3 or 4 by the god's rank, once per day per god, and a god you ignore loses 1 a day down to 10. At 25, 50, 75 and 100 you earn blessing ranks 1 to 4."],
 ["Wayside shrine", "place", 1, "mythology", "A small cairn or post to a god of a court, open from the court's Age. Hold an offering the god likes and use it to add favour. Build it from 8 stone or wood and 1 of the god's emblem item."],
 ["Temple", "place", 2, "mythology", "A built hall to one court, opening one Age after its shrines. A priest NPC lives there and keeps the court's rites, sells offerings and speaks a blessing for coin once a day."],
 ["Temple vault", "place", 3, "mythology", "A strongroom under a temple that works as a bank from Age III. Coins of the temple's own culture can be kept, lent against goods and returned; a vault robbed brings the court's curse on the thief if the court is a dead one."],
 ["Blessing", "concept", 1, "mythology", "A boon from a god, matched to its domain: Strength, Speed, Regeneration, Haste, Night vision, Water breathing, Fire resistance, Luck, slower hunger or extra experience. Rank 1 to 4 adds a level each; one blessing at a time, lasting a day."],
 ["Curse", "concept", 2, "mythology", "A one-day setback from a dead court's god after an oath is broken at its shrine or a temple vault is robbed. An offering to that god lifts it. Living traditions never curse."],
 ["Divine encounter", "event", 3, "mythology", "From one Age after a court opens, its avatars may be met at the court's mythic sites. A dead court's avatar is a two-phase boss; a living tradition shows only a gentle visitation and a blessing."],
 ["Living tradition", "concept", 1, "mythology", "A court still followed by people today. The game gives it worship, blessings and shrines only: no bosses, no curses, no jokes at its expense, and no sacred names are used."],
]
ERA = {'starroad': 'Future', 'terraform': 'Future', 'machineancestors': 'Future', 'orbitwatch': 'Future', 'sleepships': 'Future', 'farlight': 'Future', 'lasttablet': 'Rodos', 'returncourt': 'Rodos', 'stonecircle': 'Rodos', 'firstshore': 'Rodos', 'rodosend': 'Rodos'}
era_of = {}
for t in trad:
    if t['id'] in ERA:
        era_of[t['title'].replace('The ', 'the ', 1)] = ERA[t['id']]
        for g in t['gods'] + t['creatures']: era_of[g['name']] = ERA[t['id']]
for row in lib:
    e = era_of.get(row[0]) or era_of.get(row[0][:1].lower() + row[0][1:])
    if e:
        row[4] = row[4].replace('Age VII', 'the %s Age' % e)
        row[3] = row[3] + '-' + e.lower()
DRUID = [
 (1, 'hearth fires and the first oak', 'Rites of the First Fire', 'Age I druidry: light a hearth fire at a cairn on a seasonal day and keep it a day to earn the grove-keepers\' trust. It teaches the first Celtic charm, a ward of oak leaves worth 1 heart of protection for a day.'),
 (2, 'grove oaths and the mistletoe cut', 'Rites of the Grove Oath', 'Age II druidry: swear an oath at a sacred oak and cut mistletoe with a gold-edged sickle on a full moon. Oaths bind for 30 days and give Luck while kept.'),
 (6, 'the oak in the electric city', 'Rites of the Roof Grove', 'Age VI druidry: tend an oak in a rooftop or park grove inside a city. Each tended grove gives its keeper Regeneration by day and slows pollution on the tiles around it.'),
 (7, 'the grove that remembers', 'Rites of the Living Archive', 'Age VII druidry: grove-keepers record songs and seasons in a seed archive. Each record of a vanished plant lets the keeper grow it again from seed once.'),
 (7, 'the grove among the stars', 'Rites of the Star Grove', 'Future Age druidry: a sealed grove in a ship or station keeps the old oaths. Its keeper gains Night vision and Water breathing there, and the grove makes oxygen for 4 players.'),
 (7, 'the last grove', 'Rites of the Last Oak', 'Rodos Age druidry: the last oak stands where the Island door once was. Keeping its fire lit through a full night opens the Return Court for that player and ends all curses on them.')]
for a, dom, nm, txt in DRUID:
    loc = 'druidry' + ('-future' if txt.startswith('Future') else '-rodos' if txt.startswith('Rodos') else '')
    lib.append([nm, 'event', a, loc, txt])
lib += CONCEPTS
json.dump(lib, open('/mnt/project-files/library-sync/mythology.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
os.makedirs(os.path.join(H, 'out'), exist_ok=True)
json.dump(gods_out, open(os.path.join(H, 'out/gods.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
json.dump(crit_out, open(os.path.join(H, 'out/creatures.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
json.dump([dict(id=t['id'], name=t['title'], region=t['region'], age=t['age'], living=t['status'] == 'living', rule=t['rule']) for t in trad], open(os.path.join(H, 'out/courts.json'), 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print('library entries', len(lib))
