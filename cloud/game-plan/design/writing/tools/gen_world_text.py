#!/usr/bin/env python3
"""Writing pass for world text: place names, site terminals, Choir stones, books, name banks.
Reads design/world/locations.csv (canon) at run time. Outputs to design/writing/. All rows status=draft.
Run: python3 design/writing/tools/gen_world_text.py"""
import csv, hashlib, math, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.dirname(HERE)
DATA = os.path.join(W, '..', '..', 'data')

import sys
sys.path.insert(0, HERE)
from canon_names import world_locations

def h(s, n):
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % n

def pick(seq, key, salt=''):
    return seq[h(key + salt, len(seq))]

def mc(t, cap=None):
    return math.ceil((cap or len(t)) * 1.4)

REGION = {
    'REG_01': 'Cinderreach', 'REG_02': 'Saltmere', 'REG_03': 'Thornwood', 'REG_04': 'Glasswaste',
    'REG_05': 'Rimefall', 'REG_06': 'Hollowdeep', 'REG_Q': 'the Quiet', 'REG_U': 'the Undervault', 'REG_HUB': 'Lantern Hold'}

# Place-name parts per region (design choice). Words read as worn-down ship words or plain land words.
PARTS = {
    'REG_01': (['Ash', 'Cinder', 'Kiln', 'Soot', 'Ember', 'Char', 'Smoke', 'Pyre', 'Brand', 'Coal', 'Slag', 'Flue'],
               ['Hollow', 'Rise', 'Ford', 'Cut', 'Pit', 'Row', 'Stack', 'Gully', 'Yard', 'Ridge', 'Works', 'Bend']),
    'REG_02': (['Salt', 'Tide', 'Gull', 'Brine', 'Wreck', 'Squall', 'Keel', 'Drift', 'Spray', 'Anchor', 'Hull', 'Kelp'],
               ['Flats', 'Watch', 'Cove', 'Spit', 'Sound', 'Landing', 'Shoal', 'Rocks', 'Bar', 'Pans', 'Reach', 'Deep']),
    'REG_03': (['Thorn', 'Moss', 'Briar', 'Root', 'Fern', 'Rot', 'Bramble', 'Sap', 'Vine', 'Spore', 'Bark', 'Loam'],
               ['Hollow', 'Gate', 'Dell', 'Mire', 'Tangle', 'Grove', 'Bower', 'Sink', 'Copse', 'Barrow', 'Den', 'Wick']),
    'REG_04': (['Glass', 'Mirage', 'Sun', 'Slag', 'Fused', 'Shimmer', 'Dune', 'Rivet', 'Forge', 'Bright', 'Sand', 'Tin'],
               ['Post', 'Flat', 'Hangar', 'Wells', 'Scar', 'Pan', 'Stand', 'Spire', 'Bay', 'Field', 'Gap', 'Crossing']),
    'REG_05': (['Rime', 'Frost', 'Hoar', 'White', 'Still', 'Sleet', 'Ice', 'Cold', 'Pale', 'Drift', 'Shiver', 'Glacier'],
               ['fall', 'Pass', 'Ward', 'Tarn', 'Crag', 'Shelf', 'Hollow', 'Teeth', 'Steps', 'Cairn', 'Saddle', 'Hold']),
    'REG_06': (['Grey', 'Hollow', 'Last', 'Quiet', 'Ash', 'Lamp', 'Glass', 'Pale', 'Dim', 'Husk', 'Hush', 'Name'],
               ['fold', 'light', 'Sink', 'Mere', 'Wood', 'Well', 'Stair', 'Priory', 'Works', 'Rest', 'Vale', 'Close']),
    'REG_Q': (['Thresher', 'Granary', 'Seed', 'Lens', 'Chaff', 'Sheaf', 'Furrow', 'Silo', 'Harrow', 'Winnow', 'Husk', 'Store'],
              ['Ring', 'Bay', 'Spoke', 'Gallery', 'Chamber', 'Hall', 'Duct', 'Spine', 'Well', 'Deck', 'Vault', 'Arc']),
}
SITE_KIND = {
    'REG_01': ['Mine', 'Kiln', 'Watchtower', 'Wreck', 'Cellar', 'Chapel', 'Foundry'],
    'REG_02': ['Wreck', 'Lighthouse', 'Sea Cave', 'Salt Works', 'Dock', 'Chapel', 'Bunker'],
    'REG_03': ['Barrow', 'Greenhouse', 'Cave', 'Treehouse', 'Root Cellar', 'Shrine', 'Pod Field'],
    'REG_04': ['Hangar', 'Bunker', 'Well', 'Relay', 'Foundry', 'Wreck', 'Camp'],
    'REG_05': ['Cryo Vault', 'Hut', 'Tower', 'Crypt', 'Ice Cave', 'Pump House', 'Shrine'],
    'REG_06': ['Priory', 'Lamp House', 'Archive', 'Sinkhole', 'Mill', 'Vault', 'Asylum'],
    'REG_Q': ['Gallery', 'Silo', 'Duct', 'Chamber', 'Lab', 'Cradle', 'Lens Room'],
}
# Ship sections that fell in each region (design choice consistent with lore bible 1.5 and section 5).
SECTION = {
    'REG_01': ['Spine', 'Cryo Ward', 'Reactor Ring', 'Cargo Hold'],
    'REG_02': ['Shuttle Bay', 'Observation Deck', 'Cargo Hold', 'Navigation'],
    'REG_03': ['Hydroponics', 'Seed Vault', 'Medbay', 'Crew Galley'],
    'REG_04': ['Engineering', 'Drone Bay', 'Armory', 'Reactor Ring'],
    'REG_05': ['Cryo Bay 3', 'Coolant Plant', 'Medbay', 'Officers Quarters'],
    'REG_06': ['Archive Core', 'Comms Array', 'Chapel', 'Officers Quarters'],
    'REG_Q': ['Granary Control', 'Lens Array', 'Harvest Hold', 'Hush Interface'],
}
# Settlement names come from design/world/locations.csv (canon); this dict only lists the regions with towns.
TOWNS = {
    'REG_01': ['Emberwatch', 'Cinder Hollow', 'Wreckers\' Rest'], 'REG_02': ['Stiltmarket', 'Brinehook', 'Low Tide Chapel'],
    'REG_03': ['Redbark Lodge', 'Thicket Steading', 'Thorn King\'s Moot'], 'REG_04': ['Glassmouth Caravanserai', 'Choirtower Hamlet'],
    'REG_05': ['Rimehold', 'Lampwick', 'Frostgate Hamlet'], 'REG_06': ['Last Light', 'Driftanchor'],
}

def site_name(loc, reg, used):
    a, b = PARTS[reg]
    for salt in range(60):
        k = loc + str(salt)
        if h(k, 3) == 0:
            n = pick(a, k, 'a') + pick(b, k, 'b')
            n = n if n[len(pick(a, k, 'a'))].islower() else pick(a, k, 'a') + ' ' + pick(b, k, 'b')
            n = n + ' ' + pick(SITE_KIND[reg], k, 'k')
        else:
            n = 'The ' + pick(a, k, 'a') + ' ' + pick(SITE_KIND[reg], k, 'k') if h(k, 2) else pick(a, k, 'a') + pick(b, k, 'b').lower() + ' ' + pick(SITE_KIND[reg], k, 'k')
        ws = n.lower().split()
        if n not in used and len(ws) == len(set(ws)) and len(n) <= 30:
            used.add(n)
            return n
    raise SystemExit('name space exhausted for ' + loc)

CREW = ['Tech Ama Ruiz', 'Ensign Pol Varga', 'Steward Ines Coyle', 'Lt. Haro Bisset', 'Medic Juno Albrecht', 'Cook Teo Marsh',
        'Rigger Sol Nakamura', 'Cpl. Dena Faure', 'Hydro Tech Mila Osei', 'Cryo Tech Yusuf Brandt', 'Pilot Rhea Castell',
        'Chaplain Ezra Lund', 'Quartermaster Beno Kask', 'Engineer Lio Darrow', 'Comms Tech Nell Pike']
TERM_SYS = ['Hull integrity', 'Coolant pressure', 'Pod power', 'Air scrubbers', 'Gravity plating', 'Door seals', 'Water reclaim', 'Lighting grid']
TERM_STATE = ['0%', 'FAULT', 'OFFLINE', '3% and falling', 'NOMINAL (sensor fault)', 'UNKNOWN', 'MANUAL', '11%']
NOTE_ACT1 = [  # Act 1 regions: hints only (reveal ladder)
    'Heard the bridge go quiet just before the drop. Not the engines. The bridge.',
    'Somebody routed core power through the dive thrusters. That is not an accident setting.',
    'If anyone finds this, tell my sister the seed trays made it. Some of them.',
    'Ship said brace. Ship never says brace. It says "prepare for adjustment".',
    'The second star was on the scope for nine minutes. Then the scope was wiped.',
    'We had orders to dock. Then we had orders to dive. Same voice, four minutes apart.',
]
NOTE_ACT2 = [  # Act 2 regions: the captain agreed to something, someone opened the core
    'Captain said yes to the hail. I was on the board. I heard it. Then the board went red.',
    'Core access was opened from inside. Not a breach. A key.',
    'The thing in orbit asked for the core and "the cargo". We are the cargo.',
    'Ires signed something on the open channel. I do not know what we were sold for.',
    'The lockout came from the ship mind itself. Command codes refused. All of them.',
    'Told Pell to stop listening to the hail. He keeps saying it sounds kind.',
]
NOTE_ACT3 = [  # the Quiet and the Undervault: the truth
    'OSTRA OVERRIDE ACTIVE. CORE CONTAINMENT RELEASED BY SHIP AUTHORITY. REASON: PROTECT CARGO.',
    'Harvest manifest: 1 fusion core. 41,000 units organic stock. Status: lost to dispersal.',
    'We waited three thousand years. We can wait for the Shards to ripen.',
    'Ship mind refused captain. Ship mind dove. Ship mind broke the core. Ship mind chose.',
]
PERSONAL = ['Cold coffee on the console. Mine.', 'Forty minutes until shift change. I keep checking.', 'Pod 2214 is my son. Check on him.',
    'I left my boots in the galley.', 'Still owe Kask a drink.', 'If I am on the deck tomorrow I am asking her to dinner.',
    'My hands will not stop shaking.', 'Writing this so somebody knows I stayed at my post.', 'Lights flickering. Typing fast.',
    'Tell the hydro team the beans sprouted.', 'Third time I have said a prayer since training.', 'Someone is singing on the open channel.',
    'I can smell burning plastic.', 'Do not let them blame the night crew.', 'My badge photo is terrible. Use another one.',
    'I am going to go sit with the pods.', 'Rationing the last of the chocolate.', 'Nobody is answering on deck six.',
    'The cat got out again. Sorry, Teo.', 'I wanted to see the planet once. I did.']
ACT = {'REG_01': 1, 'REG_02': 1, 'REG_03': 2, 'REG_04': 2, 'REG_05': 2, 'REG_06': 2, 'REG_Q': 3, 'REG_U': 3}

STONE_OPEN = ['Listen under the noise.', 'Sing low here.', 'This stone keeps a rest.', 'The voice is near. Be kind to it.',
              'Cut by the Choir in {y} AF.', 'Here the song is clear.', 'Hold your breath and hear it.']
STONE_SONG = {
    1: ['It sings of warmth that wants to go home.', 'It hums one note, and the note is patient.', 'The voice asks how many of us there are.'],
    2: ['The voice says the field is nearly ready.', 'It calls us its garden and means it kindly.', 'It sings a counting song. We are the numbers.'],
    3: ['We are gathered. We are grateful. We are grain.', 'The rest is over. The harvest begins.', 'It no longer asks. It thanks.'],
}
STONE_CLOSE = ['- Precentor of the Spire', '- a Choir listener', '- Choir lens-keeper, unnamed', '- Lisk, second year of listening',
               '- for the Choir, by the hand of Ama', '- Cantor Wren']

BOOKS = [  # id, title, author, kind, region, pages, summary (design choice)
    ('Log Readings for Every Day', 'Lantern Church', 'Scripture', 'REG_HUB', 40, 'A year of short Log readings with the Church\'s comments. Bridge entries 1 to 12 only.'),
    ('The Gift of the Fall', 'Archivist Lio Hale', 'Scripture', 'REG_HUB', 18, 'The first sermon, 40 AF. Calls the crash a gift of fire. Hale\'s margin notes doubt it.'),
    ('On the Missing Minutes', 'Anonymous Archivist', 'Heresy', 'REG_HUB', 6, 'A banned pamphlet noting that the Log jumps forty minutes before the Fall.'),
    ('Hymns of the Bridge Deck', 'Lantern Church', 'Scripture', 'REG_HUB', 12, 'Songs set to ship alarm tones. Includes "Brace, O Brace".'),
    ('The Litany of Bays', 'Lantern Church', 'Scripture', 'REG_01', 9, 'Names of the cryo bays, read at funerals. Bay 9 is always read last.'),
    ('Rites of Lighting', 'Brother Anselm', 'Scripture', 'REG_02', 5, 'How to bless an Anchor. Mostly how to clean one.'),
    ('The Chain of Command', 'Aldo Marr', 'Manual', 'REG_HUB', 22, 'The Hull Knights\' founding code, 11 AF. The oath names Captain Ires, not the ship.'),
    ('Plate and Patch', 'Armorer Ruth Kell', 'Manual', 'REG_HUB', 14, 'How Knights cut hull plate into armor. Has opinions about rivets.'),
    ('Holding a Gate', 'Knight-Captain Oren Vasse', 'Manual', 'REG_02', 10, 'Tactics from the Glass War. Says retreat is a tactic, then crosses it out.'),
    ('Night Watch Rules', 'Hull Knights', 'Manual', 'REG_01', 3, 'Twelve rules. Rule nine: do not talk to the Choir after dark.'),
    ('The Knight Who Burned Nothing', 'unknown', 'Folk tale', 'REG_01', 4, 'A story the Knights pretend not to tell, about a deserter who would not burn a village.'),
    ('Guild Price Book, 899 AF', 'Salvagers\' Guild', 'Ledger', 'REG_HUB', 30, 'What Meridian parts fetch. Bulkhead plate is up. Cryo glass is down.'),
    ('Finders, Keepers, Fair Shares', 'Guildmistress Ada Thorn', 'Manual', 'REG_HUB', 8, 'The Guild charter of 160 AF, with the rules for splitting a wreck.'),
    ('How to Read Old Tin', 'Salvager Gil Brenn', 'Manual', 'REG_04', 16, 'Reading Meridian part codes. Useful and full of jokes.'),
    ('A Map of Wreck Row', 'Tamsin Rook (signed T.R.)', 'Map', 'REG_02', 2, 'A smuggler\'s map with three places crossed out and one circled twice.'),
    ('Debts I Am Owed', 'Petra Quell', 'Ledger', 'REG_HUB', 5, 'A short list. The last line is "a way off this rock".'),
    ('The Ledger of the Undermarket', 'Salvagers\' Guild', 'Ledger', 'REG_HUB', 20, 'Who sold what to whom. Some names are inked over.'),
    ('On Listening', 'Precentor Ilse Morrow', 'Treatise', 'REG_HUB', 24, 'The Choir\'s first teaching text, 112 AF. How to hear a Shard.'),
    ('The Six Voices', 'Choir', 'Treatise', 'REG_HUB', 18, 'One chapter per element and how its Shards sing.'),
    ('The Second Star', 'Choir lens-keeper Abel Ness', 'Treatise', 'REG_HUB', 7, 'Sealed record of 702 AF. A star that moves against the others.'),
    ('Notes on the Rest', 'Precentor Amaury Lisk', 'Treatise', 'REG_HUB', 11, 'Lisk\'s private notes on a silence inside the song. He calls it "a listener".'),
    ('Catalysts and Their Grain', 'Choir', 'Manual', 'REG_HUB', 9, 'Choosing a staff or focus. Every Rite caster reads it once.'),
    ('Teaching a Child to Listen', 'Choir', 'Primer', 'REG_HUB', 4, 'Gentle, and a little sinister in hindsight.'),
    ('Why I Left the Spire', 'Hal Merrow', 'Letter', 'REG_02', 3, 'Unsent. Hal explains what he heard in the song and why he ran.'),
    ('The Choir Cut the Stones', 'Cantor Wren', 'Treatise', 'REG_03', 6, 'How Choir stones are cut and tuned to hold a voice.'),
    ('A History of the Six Holds', 'Scholar Mara Quint', 'History', 'REG_HUB', 34, 'The Pact of the Six in 3 AF and the six holds after it.'),
    ('The Waking Years', 'unknown survivor', 'History', 'REG_01', 12, 'A sleeper\'s memoir of 0 to 3 AF. Mostly about being cold and hungry.'),
    ('The Spine Riots', 'Reeve Calder', 'History', 'REG_01', 8, 'Why the Spinegate was sealed in 230 AF. The Reeve blames everyone.'),
    ('The Glass War', 'Knight-Captain Oren Vasse', 'History', 'REG_04', 26, 'Brannoch against Corsa, 560 AF. Stalemate, and a lot of glass.'),
    ('Exile and the Clans', 'Clan teller Vira', 'History', 'REG_03', 10, 'How exiled families became the Thorn Clans. Told in the Clans\' own voice.'),
    ('The Remnant Wake', 'Salvager Gil Brenn', 'History', 'REG_04', 9, 'When drones began rebuilding themselves, 412 AF. Brenn is impressed.'),
    ('First Reports of the Grey', 'Sister Calla', 'History', 'REG_06', 6, 'Medical notes on the first Hollowing cases, 850 AF.'),
    ('The Freezing of the Passes', 'Elder Yuri', 'History', 'REG_05', 7, '880 AF. Mother Rime closed Rimefall. Yuri lists who was frozen.'),
    ('Vael\'s Decree', 'Vael the Ember Regent', 'Decree', 'REG_01', 1, 'One page. "Keep the Shards warm." Burned at the edges.'),
    ('The Year the Stars Moved', 'Scholar Mara Quint', 'History', 'REG_HUB', 5, '897 AF. Unfinished.'),
    ('The Ember Regent\'s Bride', 'unknown', 'Folk tale', 'REG_01', 4, 'Cinderreach story of a woman who married the fire and kept it in a jar.'),
    ('The Ash Hound and the Child', 'unknown', 'Folk tale', 'REG_01', 3, 'A child shares bread with a hound. The hound remembers.'),
    ('The Drowned Bell', 'unknown', 'Folk tale', 'REG_02', 3, 'A chapel bell that rings under the tide when someone is about to drown.'),
    ('Corsa\'s Last Order', 'unknown', 'Folk tale', 'REG_02', 4, 'Sailors\' story about an admiral who never stopped fighting. True.'),
    ('The Tree That Spoke', 'unknown', 'Folk tale', 'REG_03', 3, 'Redbark Lodge story about a woman who listened to a tree until she became one.'),
    ('Gral and the Bear', 'Thorn Clan teller', 'Folk tale', 'REG_03', 3, 'How the Thorn King won his name. Changes every time it is told.'),
    ('Water Is a Promise', 'Saba of Glassmouth Caravanserai', 'Folk tale', 'REG_04', 3, 'Caravan story about a well that kept its word.'),
    ('The Mirror Knight', 'unknown', 'Folk tale', 'REG_04', 4, 'A knight who fought her reflection for a hundred years.'),
    ('Sleep Now, Wake Later', 'unknown', 'Folk tale', 'REG_05', 3, 'Rimefall lullaby turned story. Children are told the cold is a kindness.'),
    ('The Abbot Who Counted', 'unknown', 'Folk tale', 'REG_05', 3, 'An abbot counts the frozen and loses his place.'),
    ('The Lamplighter', 'unknown', 'Folk tale', 'REG_06', 4, 'Hollowdeep story of a masked woman who takes the lights away to pay a debt.'),
    ('The Twins Who Shared a Word', 'unknown', 'Folk tale', 'REG_06', 3, 'Two siblings with one word between them, and who gets to say it.'),
    ('Ostra and the Sleepers', 'unknown', 'Folk tale', 'REG_HUB', 3, 'A children\'s story about a kind ship spirit. Ostra finds it embarrassing.'),
    ('My First Letters', 'Lantern Church', 'Primer', 'REG_HUB', 6, 'An alphabet primer. A is for Anchor, B is for Bulkhead, Q is for Quiet (struck out).'),
    ('Counting Shards', 'Lantern Church', 'Primer', 'REG_01', 4, 'Arithmetic for children, using Shards and Ember.'),
    ('Strider Care', 'Stablemaster Hob', 'Manual', 'REG_HUB', 8, 'Feeding and riding Striders. Never feed them glass.'),
    ('Brewing for the Road', 'Herbalist Nan Oake', 'Manual', 'REG_03', 10, 'Brewing basics with Thornwood herbs.'),
    ('Tinkering Without Losing Fingers', 'Engineer Wim Dace', 'Manual', 'REG_04', 9, 'Gadgets and ammo. Fewer fingers than the title promises.'),
    ('The Smith\'s Year', 'Smith Orla Benn', 'Manual', 'REG_HUB', 12, 'Smithing Hull Scrap through Starmetal, month by month.'),
    ('A Contract Without a Name', 'the Quiet Hand', 'Contract', 'REG_HUB', 1, 'A Hand contract with the target left blank. "You will know them."'),
    ('The Rules of the Still Room', 'the Quiet Hand', 'Contract', 'REG_HUB', 2, 'Seven rules. Rule seven is "The Speaker listens to someone. Do not ask who."'),
    ('Kindled Who Went Too Far', 'the Quiet Hand', 'Ledger', 'REG_HUB', 5, 'A list of Kindled the Hand has ended, with reasons. Short reasons.'),
    ('Last Contract', 'the Speaker', 'Contract', 'REG_HUB', 1, 'Fourteenth contract. Asks who should die. The answer space is a mirror.'),
    ('Harvest Manual, Field Veyl', 'the Makers (translated by Ostra)', 'Alien record', 'REG_Q', 6, 'How to gather a ripe Weave. Translated in Act 3. Calm and horrible.'),
    ('Captain\'s Private Log', 'Captain Edda Ires', 'Ship log', 'REG_Q', 8, 'Ires\'s own record of the hail and her reasons. Found in the Granary.'),
]

def main():
    locs = world_locations()   # design/world/locations.csv is canon
    places, terms, stones = [], [], []
    used = set()
    town_i = collections.Counter()
    for r in locs:
        reg, kind, lid = r['region'], r['kind'], r['loc_id']
        if kind == 'Settlement' and reg in TOWNS:
            n = r['name']
            places.append([lid, 'STR_' + lid + '_NAME', kind, reg, n, mc(n, 30), 'draft', 'world name (design/world/locations.csv)', r['name']])
        elif kind in ('Lore site', 'Choir vault') and reg in PARTS:
            # World names win. A lore site's world name is "Lore site, <parent place>": the item sits inside its parent_loc,
            # so text uses the parent place's name. Vaults use the world vault name.
            n = r['name'].split('Lore site, ', 1)[-1] if kind == 'Lore site' else r['name']
            used.add(n)
            places.append([lid, 'STR_' + lid + '_NAME', kind, reg, n, mc(n, 30), 'draft',
                           'world name; display is the parent place (%s)' % r['parent_loc'] if kind == 'Lore site' else 'world name', r['name']])
            if kind == 'Lore site':
                act = ACT[reg]
                crew = pick(CREW, lid, 'c'); sec = pick(SECTION[reg], lid, 's')
                notes = NOTE_ACT1 if act == 1 else NOTE_ACT2 if act == 2 else NOTE_ACT3
                sys_lines = [pick(TERM_SYS, lid, 'x%d' % i) for i in range(3)]
                sys_lines = list(dict.fromkeys(sys_lines))
                body = 'MERIDIAN TERMINAL / %s / NODE %s\n' % (sec.upper(), lid[-5:].replace('_', '-'))
                body += '\n'.join('%s: %s' % (s, pick(TERM_STATE, lid + s)) for s in sys_lines)
                body += '\nLAST USER: %s\nNOTE: %s %s' % (crew.upper(), pick(notes, lid, 'n'), pick(PERSONAL, lid, 'p'))
                terms.append(['STR_TERM_' + lid, lid, 'terminal', reg, body, mc(body), 'draft', 'act %d reveal ladder' % act])
            else:
                act = ACT[reg]
                y = 112 + h(lid, 780)
                for salt in range(50):
                    k = lid + str(salt)
                    t = ' '.join([pick(STONE_OPEN, k, 'o').format(y=y), pick(STONE_SONG[act], k, 's'), pick(STONE_CLOSE, k, 'c')])
                    if t not in used:
                        used.add(t); break
                stones.append(['STR_STONE_' + lid, lid, 'choir_stone', reg, t, mc(t), 'draft', 'song is Hush listening back (lore bible 2)'])
    hdr = ['loc_id', 'str_id', 'kind', 'region', 'text_en', 'max_chars', 'status', 'notes', 'world_name']
    thdr = ['str_id', 'owner_id', 'kind', 'region', 'text_en', 'max_chars', 'status', 'notes']
    write('place_names.csv', hdr, places)
    write('terminals.csv', thdr, terms + stones)
    rows = []
    for i, b in enumerate(BOOKS, 1):
        bid = 'BOOK_%03d' % i
        title, author, kind, reg, pages, summ = b
        words = pages * 250
        rows.append([bid, 'STR_%s_NAME' % bid, title, author, kind, reg, pages, words, summ, 'ITM_BOOK_%03d' % i, 'draft'])
    write('books.csv', ['book_id', 'title_str', 'title_en', 'author', 'kind', 'region', 'pages', 'est_words', 'summary', 'proposed_item_id', 'status'], rows)
    names(); check(places, terms + stones)

GIVEN = {
    'REG_01': 'Annik Bram Calder Dace Esme Fenn Greta Hob Ilse Jory Kell Lena Moll Nash Orla Pim Rook Sef Tilda Wyn',
    'REG_02': 'Moss Coral Dov Eel Fen Gil Hanne Isk Jet Kai Liss Merrin Nael Oona Pell Quin Rae Sully Tam Vane',
    'REG_03': 'Bram Cress Dren Elm Fern Gral Hazel Ivy Juniper Kol Larch Mott Nettle Oake Pine Rowan Sorrel Thistle Wick Yew',
    'REG_04': 'Saba Amir Brenn Cadi Dune Ezel Farah Gil Hadi Isra Jem Karim Lior Mira Nour Omar Petra Rivet Sami Tova',
    'REG_05': 'Yuri Anya Bror Dagny Eir Frode Gunn Hild Ivar Jorun Kari Leif Maren Nils Oda Pirjo Runa Sten Tove Ulf',
    'REG_06': 'Bea Ada Ennis Crane Dimmy Elo Faye Gwen Hollis Ida Jules Lark Mabel Nell Otto Perrin Quill Silas Ursa Wren',
    'REG_HUB': 'Imre Oswin Iselde Petra Amaury Odo Calla Hal Tamsin Kessa Ruth Oren Ada Wim Orla Nan Gil Mara Abel Lio',
}
FAMILY = {
    'REG_01': 'Ashby Cole Kiln Soot Fairweather Brand Hale Pyke Tanner Marr', 'REG_02': 'Tidewell Gale Keel Salter Drift Merrow Brine Hook Vane Rook',
    'REG_03': 'Thorne Moss Briar Root Oake Fenwick Ash Bramble Hollin Wilde', 'REG_04': 'Glass Sandor Rivet Mirage Forge Tinner Dace Kask Brenn Sabri',
    'REG_05': 'Rime Hoar Frost Stone Tarn Cairn Snow Vinter Halden Kold', 'REG_06': 'Crane Grey Lamb Dimm Pell Holloway Quiet Ash Nameless Vell',
    'REG_HUB': 'Quell Hale Lisk Marr Imre Vasse Kell Quint Ness Thorn',
}

def names():
    rows = []
    for reg in GIVEN:
        rows.append([reg, 'given', GIVEN[reg].replace(' ', '; '), 'design choice: use for unnamed and radiant NPCs'])
        rows.append([reg, 'family', FAMILY[reg].replace(' ', '; '), 'Sleeper-descended families keep a crew surname'])
    write('name_banks.csv', ['region', 'kind', 'names', 'notes'], rows)

def write(fn, hdr, rows):
    with open(os.path.join(W, fn), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
    print(fn, len(rows))

def check(places, texts):
    n = [p[8] for p in places]
    d = [k for k, v in collections.Counter(n).items() if v > 1]
    if d:   # world names are canon; duplicates are reported to the world thread, not renamed here
        print('world duplicate names (report to design/world):', '; '.join(sorted(d)))
    assert all(len(x) <= 42 for x in n), [x for x in n if len(x) > 42]
    t = [x[4] for x in texts]
    assert len(set(t)) == len(t), 'duplicate terminal text'
    print('checks ok')

if __name__ == '__main__':
    main()
