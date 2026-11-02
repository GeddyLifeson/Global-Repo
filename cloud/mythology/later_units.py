"""Map the later-era culture units (cultures/LATER_AGE_UNITS.csv) to the invented V-to-Rodos courts. Run: python3 -I later_units.py"""
import csv, json, os, zlib
H = os.path.dirname(os.path.abspath(__file__))
MAP = {'kuonrig': 'deepship', 'lasuirrig': 'greatfield', 'kuonspiusach': 'deepship', 'talumnuod': 'greatfield', 'dunbuldach': 'furnace',
 'gainemrig': 'greatfield', 'guoltintech': 'furnace', 'saertulmach': 'highway', 'iarnbotrach': 'furnace+highway', 'oilen_nuod': 'deepship+wirelamp',
 'deiskertfurraigi': 'greatfield+deepship', 'solasstaid': 'wirelamp', 'katuirliunach': 'glasscity', 'olumaein': 'splitsun+highway',
 'eolaskumlacht': 'mindcloud+signal', 'skielbaili': 'splitsun+signal', 'realtsiulach': 'starroad+terraform', 'roudosach': 'lasttablet+returncourt',
 'glasdumuin': 'terraform', 'sinsermeisin': 'machineancestors', 'longkodlata': 'sleepships', 'soulasfada': 'farlight', 'fairechrotlach': 'orbitwatch',
 'liekdeirendach': 'lasttablet', 'kloichchruind': 'stonecircle', 'kiedtra': 'firstshore', 'teinedeired': 'rodosend'}
g = json.load(open(H + '/out/gods.json')); c = json.load(open(H + '/out/creatures.json'))
rows = []
for u in csv.DictReader(open('/mnt/project-files/cultures/LATER_AGE_UNITS.csv', encoding='utf8')):
    cs = MAP[u['slug']].split('+')
    gods = [x for k in cs for x in g if x['court'] == k]
    cr = [x for k in cs for x in c if x['court'] == k]
    hi = [x for x in gods if x['rank'] == 'H'] or gods
    pick = lambda pool, salt: pool[zlib.crc32((u['slug'] + salt).encode()) % len(pool)]
    p1 = pick(hi, 'a'); p2 = pick([x for x in gods if x is not p1], 'b')
    c1 = pick(cr, 'c'); c2 = pick([x for x in cr if x is not c1], 'd')
    rows.append(dict(slug=u['slug'], age=u['age'], courts='+'.join(cs), patron_god=p1['id'], second_god=p2['id'], creature_1=c1['id'], creature_2=c2['id'],
                     gods_available=len(gods), creatures_available=len(cr)))
with open(H + '/out/later_units.csv', 'w', newline='', encoding='utf8') as f:
    w = csv.DictWriter(f, rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(rows), 'units mapped')
