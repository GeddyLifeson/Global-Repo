"""Join the fantasy-biome sites (DiaithirRPG PR #146 sites.csv) to courts. Run: python3 -I placement.py"""
import csv, json, os, zlib
H = os.path.dirname(os.path.abspath(__file__))
M = {}
for court, cultures in {
 'diaithir': 'Irish Scottish Welsh Breton Manx British Celtic Gaulish Galician Occitan',
 'nilotic': 'Egyptian Nubian', 'mesopotamian': 'Sumerian Babylonian Assyrian Mesopotamian',
 'anatolian': 'Anatolian', 'canaanite': 'Canaanite Levantine Phoenician Nabataean', 'minoan': 'Minoan Maltese',
 'hellenic': 'Greek', 'italic': 'Roman Etruscan', 'germanic': 'Norse', 'slavic': 'Slavic', 'baltic': 'Baltic',
 'steppe': 'Dacian', 'iranian': 'Persian', 'vedic': 'Indian', 'sinic': 'Chinese', 'yamato': 'Japanese Ryukyuan',
 'yoruba': 'Yoruba Ashanti', 'maya': 'Maya Zapotec Mesoamerican Cholula', 'nahua': 'Aztec Toltec',
 'andean': 'Andean Inca Quechua Chavín Nazca Tiwanaku', 'polynesian': 'Hawaiian Māori Samoan Tongan Tonga Rapa Nui Polynesian Micronesian Vanuatu',
 'dreaming': 'Adnyamathanha Anangu Bininj Bundjalung Jardwadjali Kija Mutthi Wajarri Warumungu',
 'plains': 'Lakota Dakota Blackfoot Crow', 'woodland': 'Adena Mississippian Muscogee Haudenosaunee Wabanaki Poverty Point culture',
 'northwest': 'Haida Puyallup Klamath Wintu Koyukon', 'arctic': 'Inuit Sámi Nenets Ainu', 'steppeeast': 'Mongolian Altai Buryat Kyrgyz',
 'eastafrica': 'Maasai Kikuyu Chagga Shona Venda San Ethiopian', 'sahel': 'Dogon Tuareg Bakweri Saharan African',
 'highlandasia': 'Buddhist Tibetan Burmese Khmer Korean', 'sunda': 'Javanese Balinese Vietnamese', 'caucasus': 'Armenian Georgian Caucasian Commagene',
 'amazon': 'Guaraní Yanomami Taíno Pemon Muisca', 'southwest': 'Hopi Navajo Ancestral Puebloan Ute', 'ice1': 'Palaeolithic'}.items():
    for cu in cultures.replace('Rapa Nui', 'Rapa_Nui').replace('Poverty Point culture', 'Poverty_Point_culture').replace('Ancestral Puebloan', 'Ancestral_Puebloan').split():
        M[cu.replace('_', ' ')] = court
M['Sri Lankan'] = 'highlandasia'
gods, crit = json.load(open(H + '/out/gods.json')), json.load(open(H + '/out/creatures.json'))
courts = {c['id']: c for c in json.load(open(H + '/out/courts.json'))}
rows, miss = [], set()
def pick(pool, key):
    return pool[zlib.crc32(key.encode()) % len(pool)] if pool else None
for s in csv.DictReader(open(H + '/src/sites_fantasy_pr146.csv', encoding='utf8')):
    cu = s['culture']
    court = M.get(cu)
    if not court: miss.add(cu); continue
    living = s['living'] == '1'
    benign = living or courts[court]['living']
    want = {'3': 'H', '2': 'M', '1': 'L'}[s['tier']]
    pool = [g for g in gods if g['court'] == court and g['rank'] == want] or [g for g in gods if g['court'] == court]
    cp = [c for c in crit if c['court'] == court and (not benign or not c['hostile'])] or [c for c in crit if c['court'] == court]
    g, c = pick(pool, s['id']), pick(cp, s['id'] + 'c')
    rows.append(dict(site=s['id'], tier=s['tier'], court=court, patron=g['id'] if g else '', creature=c['id'] if c else '', benign_only=int(benign),
                     avatar=int(bool(c) and c['preset'] == 'avatar' and not benign)))
if miss: raise SystemExit('unmapped cultures: %s' % sorted(miss))
with open(H + '/out/placement.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(rows), 'sites placed;', sum(r['benign_only'] for r in rows), 'benign only;', sum(r['avatar'] for r in rows), 'avatar sites')

# vault.json support: a culture is dead only when its court is dead and no site of that culture is flagged living
import re
slug = lambda s: re.sub(r'[^a-z0-9]+', '_', s.lower().replace('ā', 'a').replace('á', 'a').replace('í', 'i').replace('é', 'e')).strip('_')
live = {}
for s in csv.DictReader(open(H + '/src/sites_fantasy_pr146.csv', encoding='utf8')):
    live[s['culture']] = live.get(s['culture'], False) or s['living'] == '1'
dead = {slug(cu): True for cu, court in M.items() if not courts[court]['living'] and (court == 'diaithir' or not live.get(cu, False))}
json.dump(dict(dead=dead, court_of={slug(cu): c for cu, c in M.items()}, note='dead=true: theft from a temple vault of this culture brings the court curse. Prehistoric Age I cultures are never dead here (descendants live).'),
          open(H + '/out/vault_culture_courts.json', 'w'), indent=1)
print(len(dead), 'dead cultures:', sorted(dead))
