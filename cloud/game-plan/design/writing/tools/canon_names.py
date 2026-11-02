"""World place names for writing generators.
design/world/locations.csv is canon for every place name and LOC_ ID (data/world/locations.csv is its copy).
RENAME maps the old campaign/writing town names to the world names, for display text derived from IDs
(e.g. ACT_NPC_GREYFOLD_WIDOW -> "Driftanchor Widow"). IDs never change."""
import csv, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
WORLD_LOCS = os.path.join(ROOT, 'design', 'world', 'locations.csv')
if not os.path.exists(WORLD_LOCS):
    WORLD_LOCS = os.path.join(ROOT, 'data', 'world', 'locations.csv')

RENAME = [('Hearthward Pass', 'Rimehold Pass'), ('Kiln Village', 'Emberwatch'), ('Cinder Ford', 'Cinder Hollow'),
          ('Brandmoor', "Wreckers' Rest"), ('Tidewatch', 'Stiltmarket'), ('Saltcross', 'Brinehook'), ('Gullhaven', 'Low Tide Chapel'),
          ('Briar Hollow', 'Redbark Lodge'), ('Mossgate', 'Thicket Steading'), ('Mirage Post', 'Glassmouth Caravanserai'),
          ('Kiln-Glass', 'Choirtower Hamlet'), ('Kiln Glass', 'Choirtower Hamlet'), ('Hearthward', 'Rimehold'), ('Pass Hollow', 'Lampwick'),
          ('Tarnhold', 'Frostgate Hamlet'), ('Lastlight', 'Last Light'), ('Greyfold', 'Driftanchor')]


def world_locations():
    with open(WORLD_LOCS, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def world_names():
    return {r['loc_id']: r['name'] for r in world_locations()}


RENAME_RX = [(re.compile(r'(?<![\w-])(?<!Saltmere )' + re.escape(o) + r'(?![\w-])', re.I if ' ' in o else 0), n) for o, n in RENAME]


def canon(text):
    """Swap old town names for world names in display text built from IDs."""
    for rx, n in RENAME_RX:
        text = rx.sub(n, text)
    return text
