"""Per-culture Age I hearth courts (3 gods, 2 creatures each) for every Age I culture in MASTER_CULTURES.csv.
Output: src/age1_generated.txt (same DSL as pantheons.txt). Beliefs of Age I cultures are unknown: these are invented, benign, tied to each culture's land, prey and tool."""
import csv, re, os
H = os.path.dirname(os.path.abspath(__file__))
M = [x for x in csv.DictReader(open('/mnt/project-files/cultures/MASTER_CULTURES.csv', encoding='utf8')) if x['kind'] == 'age1_culture']
ARCH = {}
for l in open('/mnt/project-files/diaithiris-archaic/CULTURE_NAMES.md', encoding='utf8'):
    p = [c.strip() for c in l.split('|')]
    if len(p) > 5 and p[1] and not p[1].startswith(('Culture', '---')):
        ARCH[p[1]] = re.sub(r'\*', '', p[3])
CLS = {
 'cold': (['ice', 'forest', 'lake', 'river', 'mountain', 'sea'], ['reindeer', 'elk', 'salmon', 'horse', 'seal'], ['wolf', 'bear', 'fox']),
 'europe': (['cave', 'forest', 'river', 'hill', 'bog', 'coast', 'lake'], ['deer', 'horse', 'boar', 'salmon', 'bull', 'elk'], ['bear', 'wolf', 'fox']),
 'levant': (['desert', 'spring', 'hill', 'river', 'valley', 'mountain'], ['goat', 'hare', 'deer', 'bull', 'horse'], ['lion', 'wolf', 'fox']),
 'africa': (['forest', 'river', 'plain', 'mountain', 'lake', 'coast', 'desert'], ['cow', 'elephant', 'deer', 'horse', 'goat'], ['lion', 'serpent', 'wolf']),
 'asia': (['river', 'forest', 'mountain', 'coast', 'cave', 'valley'], ['deer', 'boar', 'salmon', 'bull', 'goat'], ['bear', 'wolf', 'serpent']),
 'sahul': (['desert', 'river', 'coast', 'mountain', 'forest', 'plain'], ['bird', 'salmon', 'goat', 'turtle', 'seal'], ['serpent', 'wolf', 'eagle']),
 'namerica': (['plain', 'forest', 'mountain', 'coast', 'lake', 'river', 'desert'], ['bull', 'elephant', 'deer', 'elk', 'salmon', 'horse'], ['wolf', 'bear', 'lion']),
 'samerica': (['mountain', 'forest', 'river', 'coast', 'plain', 'cave'], ['deer', 'goat', 'bird', 'salmon', 'horse'], ['bear', 'serpent', 'eagle']),
}
def cls(r):
    r = r.lower()
    for k, ws in (('sahul', ('australia', 'tasmania', 'guinea', 'sahul')), ('africa', ('africa', 'kenya', 'uganda', 'congo', 'angola', 'sahara', 'nubia', 'nile', 'libya', 'algeria')),
                  ('samerica', ('chile', 'peru', 'ecuador', 'colombia', 'brazil', 'amazon', 'south america', 'andes', 'venezuela')),
                  ('namerica', ('america', 'alaska', 'yukon', 'plains', 'woodlands', 'basin', 'mexico', 'pacific coast', 'columbia')),
                  ('levant', ('levant', 'euphrates', 'tigris', 'zagros', 'negev', 'anatolia', 'caucasus', 'mesopotamia')),
                  ('cold', ('siberia', 'yakutia', 'yenisei', 'baikal', 'mongolia', 'kamchatka', 'urals')),
                  ('asia', ('china', 'japan', 'india', 'sri lanka', 'se asia', 'asia')),
                  ('europe', ('europe', 'britain', 'denmark', 'scandinavia', 'norw', 'italy', 'baltic', 'poland', 'france', 'franco', 'doggerland', 'russia')),):
        if any(w in r for w in ws): return k
    return 'europe'
TOOL = [('point', 'point'), ('microblade', 'blade'), ('microlith', 'blade'), ('blade', 'blade'), ('pottery', 'pot'), ('pot', 'pot'), ('grain', 'grain'), ('agricult', 'grain'), ('scraper', 'knife'), ('shell', 'shell'), ('Neolithic', 'house')]
import json
CN = json.load(open('/mnt/project-files/diaithiris-archaic/culture_names.json', encoding='utf8'))
LIVING = {'americas1', 'woodland', 'northwest', 'arctic', 'dreaming', 'andaman', ''}
out, seen = [], {}
for x in M:
    u, reg = x['unit'], x['region']
    c = cls(reg); land, prey, pred = CLS[c]
    n = seen[c] = seen.get(c, -1) + 1
    L, P, R = land[n % len(land)], prey[(n * 2 + 1) % len(prey)], pred[n % len(pred)]
    tool = next((t for k, t in TOOL if k.lower() in u.lower()), 'stone')
    slug = re.sub(r'[^a-z0-9]+', '_', u.lower())[:40].strip('_')
    living = x['court'] in LIVING
    title = 'The ' + CN[re.sub(r'[^a-z0-9]+', '_', u.lower()).strip('_')] + ' Hearth'  # Diaithiris name only; real culture names never reach players
    out += [f"T|a1_{slug}|{title}|{reg}|{'living' if living else 'dead'}|1|invented Age I hearth for {u}|Invented, benign and wild; real beliefs unknown.",
            f"G|H|mother of the {L} of this people|mother,{L},{tool}|{L}|{'fruit' if living else 'bone'}",
            f"G|M|lord of the {P} hunt|lord,{P},{tool}|{P}|hide",
            f"G|L|spirit of the {tool} and the ancestors|spirit,{tool},{L}|{tool}|bone",
            f"C|{P} spirit|{P},spirit,{L}|{L}|beast|n|-",
            f"C|{R} of the {L}|{R},{L},{tool}|{L}|beast|{'n' if living else 'y'}|-"]
open(H + '/src/age1_generated.txt', 'w', encoding='utf8').write('\n'.join(out) + '\n')
print(len(M), 'cultures', len(out), 'lines')
