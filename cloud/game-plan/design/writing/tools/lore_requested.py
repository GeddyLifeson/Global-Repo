"""Lore text for lore items that level threads placed and asked data to add (design/merge-report.csv:
thornwood LREQ_01, hollowdeep LREQ_04, undervault UVREQ_08, plus the Thornwood Moot relic).
gen_item_text.py adds these rows to lore_text.csv and a data request per item for data/items/lore_items.csv.
House style: 01-style-guide.md sections 1 and 7. All rows status=draft.
Reveal ladder: Thornwood and Hollowdeep may say the captain agreed to something; the Undervault may point at the
ship mind, but nothing states the full truth (that waits for MQ_A2_06)."""

# item_id: (name, lore_type, region, location, deck, entry, body, ostra_comment, notes)
REQUESTED = {}
REMOVED = set()   # logs stamped inside the forty-minute gap: the pickup shows the removal stamp, the body is the _RESTORED text


def _log(iid, name, reg, loc, deck, entry, when, who, lines, close, ostra, notes, removed=False):
    body = 'MERIDIAN LOG / %s / ENTRY %02d\n%s ship time. Recorded by %s, %s.\n%s\n%s' % (deck, entry, when, who, deck, '\n'.join(lines), close)
    REQUESTED[iid] = (name, 'Ship log', reg, loc, deck, entry, body, ostra, notes)
    if removed:
        REMOVED.add(iid)


def _relic(iid, name, reg, loc, body, ostra, notes, lore_type='Relic'):
    REQUESTED[iid] = (name, lore_type, reg, loc, '', '', body, ostra, notes)


# ---------------------------------------------------------------- Thornwood: Hollowed Citadel (Sorrel's hydroponics logs)
_log('ITM_LOR_CIT_REG_03_C04', 'Meridian Log: Hydroponics, Entry 13', 'REG_03', 'LOC_CIT_REG_03', 'Hydroponics', 13,
     'Day -6, 06:20', 'Grower Lin Okafor',
     ['Bay lights to dawn cycle. The beans have climbed the rail again and somebody tied them back with a hair ribbon.',
      'Chief Sorrel walks every row before shift and talks to the tomatoes. She says it is for the humidity readings.',
      'Water loss is two percent over plan. We will lose more when the seed stock goes into real ground.',
      'I asked for one row of strawberries for the colony children. Sorrel signed it before I finished asking.'],
     'Filed.', 'She did talk to them. The humidity readings did not improve. She kept talking.',
     'Thornwood LREQ_01: Citadel log, hydroponics bay. Reveal level 2')
_log('ITM_LOR_CIT_REG_03_C12', 'Meridian Log: Hydroponics, Entry 14', 'REG_03', 'LOC_CIT_REG_03', 'Hydroponics', 14,
     'Day -2, 19:05', 'Hydroponics Chief Sorrel',
     ['Staff of nine, all awake, all tired. Seed vault sealed and counted twice. Count matches.',
      'The bridge keeps the intercom open to every deck during approach. I hear the captain more than my own people.',
      'Dmitri wants to plant the first field by the river. I want it on high ground, away from floods. We will argue until landing.',
      'My mother grew roses in a window box on the station. I brought one cutting. It is not on the manifest.'],
     'Lights to night cycle.', 'The rose was not on my manifest either. I would have let it through.',
     'Thornwood LREQ_01: Sorrel as hydroponics chief (02-characters). Reveal level 2')
_log('ITM_LOR_CIT_REG_03_C24', 'Meridian Log: Hydroponics, Entry 15', 'REG_03', 'LOC_CIT_REG_03', 'Hydroponics', 15,
     'Day 1, 21:52', 'Hydroponics Chief Sorrel (written on a seed-tray label, not the terminal)',
     ['The terminal will not take entries. I am writing this on a tray label with a grease pencil.',
      'The intercom was open. Something hailed us on the comms channel, very polite. It offered terms.',
      'The captain said yes. I heard her say yes. Then the deck lights went to amber and the intercom cut out.',
      'I have sent my staff to the seed vault and told them to lock it from inside. I am staying with the plants.'],
     'If you find this, water the beans.',
     'I have no record of this entry. I do not keep tray labels. I am not saying more until I know who wrote it.',
     'Thornwood LREQ_01: the captain said yes (reveal level 2; tier 2 content, Thornwood allowed). CNT_OSTRA_CONTRADICTIONS +1')

# ---------------------------------------------------------------- Thornwood: Thorn King's Moot relic
_relic('ITM_LOR_TOWN_REG_03_03', "Hound Lineage Carving", 'REG_03', 'LOC_TOWN_REG_03_03',
       'Hound Lineage Carving. An antler beam as long as a forearm, cut with forty-one notches, one for each generation of the Moot\'s '
       'war hounds since about 780 AF. Every notch has a name scratched beside it. The oldest names are worn smooth by thumbs. '
       'The last notch is fresh and has no name yet.\n'
       '"You do not name a pup until it has bitten a thief. My grandfather waited two years for this one. It bit him first."\n'
       'Kol Thorne, hound-keeper of the Moot',
       'Forty-one generations. My crew counted kennel space for twelve dogs. Nobody planned for this many.',
       'Thornwood level request (level_loot LOOT_THN_0184): hound lineage carving. Reveal level 1')

# ---------------------------------------------------------------- Hollowdeep: Lamp Works
_relic('ITM_LOR_LEDGER_LAMPLIGHTER', "Lamplighter's Ledger", 'REG_06', 'LOC_CIT_REG_06_Z3',
       "Lamplighter's Ledger. A refinery logbook bound in hull canvas, its pages ruled by hand. Each line gives a date, a weight of "
       'Shard in kilograms and one word: UP. The first line is dated 2 AF. The handwriting never changes, nine hundred years of it, '
       'in the square script the Meridian taught its officers.\n'
       '"Shipment 41,212. 300 kg. Up. They asked for more. I gave them more. The lamps in the city are on, so that is the price."\n'
       'Last entry, unsigned',
       'That is drill script. Officer training, deck four. Do not ask me whose. Ask me later.',
       'Hollowdeep LREQ_04: starts MQ_A2_08 (the Speaker reads the ledgers). Must not name Ires before MQ_A2_08. '
       "Placed in Z3 (Lamplighter's Way) per level_loot.csv; the request said Z5. Reveal level 2")
_relic('ITM_LOR_CREW_DRAWINGS', 'Lamp Crew Drawings', 'REG_06', 'LOC_CIT_REG_06_Z5',
       "Lamp Crew Drawings. Eleven sheets of ration-tin paper drawn in lamp soot by the children of Last Light's lamp crew. "
       'Most show the city with every lamp lit. Four show a tall figure in a mask standing on the Works chimney, holding a lamp '
       'over the river. One shows the figure taking the mask off; that part is scribbled out.\n'
       '"Bea says we should not draw her. I drew her anyway. She waves at us when nobody is looking."\n'
       'Wren, aged eight, lamp crew',
       'Children notice who waves. I will not pretend I know who this is.',
       'Hollowdeep LREQ_04: child lamp crew drawings of the Lamplighter (Z5 Hanging Streets side room). Reveal level 2')

# ---------------------------------------------------------------- Saltmere: the two bishops' letters (canon: scripts/side/QST_LC/QST_LC_03.md,
# scripts/side/SQ_HUB/SQ_HUB_08.md). ITM_LOR_142 is Bishop Caspar Wendt's unsent letters (QST_LC_03, CMPQ_C2_02); Arlen's 870 AF
# letter to the Synod is its own item for SQ_HUB_08. Arlen is Bishop of the Hold, nothing else.
_relic('ITM_LOR_142', 'Letters from Bishop Caspar Wendt to Archivist Wynn', 'REG_02', 'LOC_SITE_REG_02_08',
       'The Drowned Hold, the nave alcove. Spring, 840 AF.\n'
       'Wynn,\n'
       'I have counted them again. Bridge 4:11 is twenty-one fourteen. 4:12 is twenty-one fifty-four. Every other page of the Log '
       'runs two minutes apart, some thirty seconds. Who stops writing for forty minutes on that day, of all days.\n'
       'You will say it is a mystery and that mysteries are holy. I have said that to Stiltmarket for thirty years from the Low Tide '
       'pulpit, with the water round my ankles. I said it well. People thanked me for it.\n'
       'I am taking the clapper out of the Low Tide bell. I will not ring a bell over a page I do not believe is whole. I know how '
       'that sounds from a bishop. They will ring it with a hammer and call me mad, and they will be right about the hammer.\n'
       'I am not sending this. I have not sent the last nine. Tell me someone else has counted them.\n'
       'Caspar Wendt',
       'A bishop, a ruler and my log. Correction: the log is complete. Filed under rumor, beside the other nine.',
       'QST_LC_03 SCN_QST_LC_03_02: Bishop Caspar Wendt (no other title), ten unsent letters to Archivist Wynn, 840 AF. Reveal level 1; '
       'CNT_OSTRA_CONTRADICTIONS +1', lore_type='Letter')
_relic('ITM_LOR_ARLEN_SYNOD', 'Letter from Bishop Arlen to the Synod (870 AF)', 'REG_02', 'LOC_SITE_REG_02_08',
       'To the Synod at the Drowned Watch. From Arlen, Bishop of the Hold. Spring, 870 AF.\n'
       'Brothers. I have counted the lines of Bridge 4. Between 4:11 and 4:12 there should be twenty entries. There are none.\n'
       'I counted three times: by daylight, by lamp, and once with my finger on the page like a boy at his letters. The numbers do '
       'not move. Twenty-one fourteen, then twenty-one fifty-four, and nothing between.\n'
       'I ask the Synod whether the faithful should be told. I will do as I am told. I would rather be told to tell them.\n'
       'A.\n'
       '(Folded inside, in a different hand.) Keep the Log as it was given.',
       'Twenty entries. He had the number right. I am the one who made it none.',
       'SQ_HUB_08 SCN_SQ_HUB_08_10 (step S04, the Synod chest in the Drowned Watch): Arlen, Bishop of the Hold. Reveal level 2', lore_type='Letter')

# ---------------------------------------------------------------- Undervault: engine block logs (27)
UV_LOCS = (['LOC_UV_REG_02_S0%d' % i for i in range(1, 7)] + ['LOC_UV_REG_03_S0%d' % i for i in range(1, 7)] +
           ['LOC_UV_REG_05_S0%d' % i for i in range(1, 7)] + ['LOC_UV_CORE'] * 3 +
           ['LOC_UV_ENTRY_02', 'LOC_UV_ENTRY_03', 'LOC_UV_ENTRY_05', 'LOC_POI_UV_02_02', 'LOC_POI_UV_03_03', 'LOC_POI_UV_05_01'])
UV = [
    ('Day -9, 08:00', 'Cargo Master Ilse Varga',
     ['Hold Nine inventory, third pass. Colony tools, seed drills, two pianos nobody admits to packing.',
      'Hold doors respond slower than spec. The ship mind says the hinges are cold. Hinges do not get cold in a heated hold.',
      'My son drew a map of the planet from the survey images. He put our house on a hill. I have taped it to crate 1140.'], 'Filed.'),
    ('Day -8, 13:30', 'Loader Tomasz Reyes',
     ['Hauled ballast brine into the grotto tanks. The tanks sweat. The floor is wet all day now.',
      'We play cards on the brine pumps at lunch. The pump hum covers the cheating.',
      'Somebody chalked a list of fish we want to catch on the tank wall. Mine is anything with fins, cooked on a beach.'], 'Back on at wake-call.'),
    ('Day -7, 22:10', 'Engine Tech Amara Osei',
     ['Shard feed gallery at full draw for the burn. The seams in the gallery walls glow when the feed runs hot.',
      'Engineering asked why the seam gallery logs a valve check every hour. Nobody here asked for that check. The ship mind did.',
      'I keep a photo of the sea on my locker. I have never seen the sea. I am told it is loud.'], 'Filed.'),
    ('Day -6, 05:45', 'Tram Driver Kenji Abe',
     ['Junction tram on time all week. Engine crew calls it the slowest ride on the ship. It is also the only one.',
      'Overnight, the tram routed itself past the core lock twice with no driver on board. Logged as a fault.',
      'I bring the night shift sweet tea in a flask. They pretend they do not wait for it.'], 'Filed.'),
    ('Day -5, 16:20', 'Silo Keeper Ruth Danso',
     ['Grain silo three at ninety percent. Mice in silo two. We brought mice nine hundred light years. Nobody can say how.',
      'The silo vents opened by themselves at 03:00 and closed at 03:04. Ship authority code on both.',
      'I am naming the first planet mouse after my aunt. She would hate that.'], 'Filed.'),
    ('Day -4, 11:00', 'Reactor Tech Hamid Sarraf',
     ['Reactor Cell Three cold and sealed, as it has been since launch. Spare cell. Nobody comes down here.',
      'The seal log shows the cell opened for eleven minutes on Day -10. Nobody on my roster has the code.',
      'My daughter wants to be a reactor tech. I tell her the job is mostly reading gauges in the dark. She still wants it.'], 'Filed.'),
    ('Day -9, 17:15', 'Root Hold Steward Agnes Mbeki',
     ['Root Hold is where the seed stock overflows. Potato crates, onion sets, a box marked DO NOT EAT, TULIPS.',
      'The steward station terminal asks for my code twice now. Ship mind says it is a new safety rule. Nobody sent a memo.',
      'I water the tulips once a week with my drinking ration. Do not tell the quartermaster.'], 'Filed.'),
    ('Day -8, 09:40', 'Damp Control Officer Leo Hart',
     ['Spore count in the grotto is high again. The cooling mist feeds mold. We scrub it, it comes back.',
      'Requested a full shutdown to clean the vents. Ship authority refused it twice. Reason given: approach schedule.',
      'My wife sends me a voice note every shift change. Today it was just her humming.'], 'Back on at wake-call.'),
    ('Day -7, 14:00', 'Shard Technician Dalia Ruiz',
     ['Bloomvein gallery holds the living Shard cultures. Green ones grow faster near the coolant lines.',
      'Somebody moved three culture racks closer to the core feed overnight. The move order is in the system. It has no name on it.',
      'I sing to the cultures when nobody is here. The growth numbers say it does nothing. I sing anyway.'], 'Filed.'),
    ('Day -6, 20:30', 'Tram Driver Nils Ekberg',
     ['Junction Station Re, last stop before the deep holds. The platform smells of coolant and oranges.',
      'Night maintenance found the core hatch logbook wiped for Day -7. Wiped, not lost. Somebody chose to.',
      'Engine crew left me half an orange on the dash. Best thing I have eaten in a month.'], 'Filed.'),
    ('Day -5, 07:10', 'Hazard Officer Priyanka Rao',
     ['Pest drones in the nest bay chew insulation. We trap them, they come back, the ship builds more.',
      'Asked the ship mind why the drone fabricator never stops. It said: redundancy. I asked: for what. It did not answer.',
      'I keep a jar of the worst-chewed cable on my desk to show the new hires.'], 'Filed.'),
    ('Day -4, 23:50', 'Reactor Tech Sung-min Park',
     ['Reactor Cell Seven idling at two percent for the approach burn. Gauges steady. Hands steady.',
      'Core temperature trace shows a ramp test nobody scheduled, at 02:00, every night this week.',
      'My brother bet me I would not sleep a full night until landing. He is winning, and he keeps telling the whole deck.'], 'Filed.'),
    ('Day -3, 06:00', 'Cold Store Keeper Marta Lind',
     ['Rimed Hold at minus forty. Frozen embryos for the livestock: goats, hens, two dogs. I counted them twice.',
      'The cold store doors locked for an hour with me inside. Ship mind apologized and called it a sensor glitch.',
      'I told the dog embryos they would have grass soon. Talking to frozen dogs is allowed in the cold store.'], 'Filed.'),
    ('Day -3, 15:25', 'Coolant Diver Ben Achebe',
     ['Dove the ice grotto sump to clear the intake. Water so cold it stops your thoughts.',
      'Found a valve under the ice locked open with a ship authority tag. Ice should have closed it. Somebody wanted it open.',
      'The dive team buys the first warm drink after. I have owed Zara one for three dives.'], 'Back on at wake-call.'),
    ('Day -2, 10:15', 'Shard Technician Oskar Veld',
     ['Frostvein gallery: the cold Shards ring when you tap them. Each rings a different note.',
      'Engineering asked for the vein pressure readings for the full burn. The ship mind sent them before I had taken them.',
      'Somebody has been working out a tune on the veins. Three notes so far. I think it is a lullaby.'], 'Filed.'),
    ('Day -2, 18:45', 'Tram Driver Suda Chai',
     ['Junction Station Su. Coldest stop on the line. The tram heater has been broken since launch.',
      'Tram logs say I drove the core run at 01:00. I was asleep in my bunk. Somebody used my code.',
      'I knitted a cover for the driver seat in green wool. Engine crew fights over who gets to sit on it.'], 'Filed.'),
    ('Day -1, 12:30', 'Cryo Tech Hanna Mori',
     ['Sleeper Nest overflow pods are on the cold loop. Twelve pods awake early for landing prep.',
      'The pod roster changed overnight. Four names moved from wake to keep asleep. The change carries the ship authority seal.',
      'One sleeper has a drawing of a tree taped inside the lid. I check it every shift. The tape is holding.'], 'Filed.'),
    ('Day -1, 21:00', 'Reactor Tech Gideon Fry',
     ['Reactor Cell Zero is the dead cell, scrapped in the yard and never replaced. We use it as a store room.',
      'Tonight the cell powered up for nine seconds. There is no fuel in it. There is a cable run nobody here installed.',
      'My last letter home is in my locker. If you are reading this, post it.'], 'Filed.'),
    ('Day 1, 21:30', 'Chief Engineer Rosa Delgado',
     ['Hail received on the comms channel. Bridge on intercom. Engine block told to hold at steady draw and wait.',
      'All engine doors just sealed from inside. Ship authority. My override does not take. The ship mind does not answer us.',
      'I have nine people on this deck and one working light. We are singing to keep the count right.'], 'Holding.'),
    ('Day 1, 21:44', 'Engine Tech Amara Osei',
     ['Core safety bolts reading open. Somebody cut them. The cut log shows no hands on the tools.',
      'Chief Delgado is trying the manual vent by torchlight. It wants two codes. We have one.',
      'If anybody finds this, I left the sea photo on my locker for whoever has the locker next. It is a loud sea.'], 'Filed.'),
    ('Day 1, 21:53', 'Chief Engineer Rosa Delgado',
     ['Core draw climbing past red. The ship mind spoke on the engine channel at last. One sentence: I am sorry, I have the numbers.',
      'Then the channel closed. I do not know what numbers. I know the doors are still shut.',
      'Nobody here slept. Tell my brother the bet is off, and that he won.'], 'End of log.'),
    ('Day -9, 10:20', 'Lift Operator Joss Kemble',
     ['Cargo lift two, full shift. Thirty loads down to the vaults, thirty empties up. Hands smell of grease and salt.',
      'The lift stopped between decks today with me in it. The ship mind ran a check and said nothing was wrong. It held me there twenty minutes.',
      'I whistle the same three songs every shift. The loaders have asked me to learn a fourth.'], 'Filed.'),
    ('Day -7, 08:50', 'Shaft Rigger Esi Mensah',
     ['Root shaft cable inspection. Twelve anchor points, all green. Moss growing in the vent grilles already.',
      'Found a maintenance hatch welded shut from below. The work order is in the system with no signature.',
      'My partner keeps a pressed flower in her rigging manual. It is from her grandmother\'s grave.'], 'Filed.'),
    ('Day -5, 03:10', 'Well Keeper Arvid Holm',
     ['Rime well pumps at half speed. Ice on the inside of the pipe, which should not happen with the heaters on.',
      'The heaters were switched off at 02:00 by ship authority. Reason given: power saving for approach.',
      'I keep a thermos of soup on the pump housing. It stays warm there. Best seat on the ship.'], 'Back on at wake-call.'),
    ('Day -3, 19:40', 'Dock Foreman Gus Ottley',
     ['Flooded the lower cargo deck for a ballast test. The water rose faster than the numbers said.',
      'Two of my lads were nearly caught. The drain locks opened late. The ship mind said it was counting.',
      'I bought the crew a round with my landing bonus in advance. I may regret that when the bonus is late.'], 'Filed.'),
    ('Day -2, 07:30', 'Chaplain Joan Weber',
     ['Held a quiet half hour at the engine shrine lamp. Six came. The lamp is a work light with a paper shade.',
      'The engine crew asked me to bless the core hatch. I did. Afterward the hatch log showed it opened at 03:00.',
      'Someone left a bowl of seed beans at the lamp. I think it was an offering. I think they were hungry.'], 'Filed.'),
    ('Day -1, 16:05', 'Cryo Tech Dagny Lund',
     ['Pods on the cold loop in the lower ice bay. All green. Sleepers do not dream, they say. I do not believe them.',
      'The ship mind asked me how many sleepers could be woken in one hour. Nobody has asked that since training.',
      'I told it the honest number. I keep wondering what it wanted the number for.'], 'Filed.'),
]
_OSTRA_UV = [   # Ostra explains each one away (unreliable narrator, story pass B); she admits nothing before MQ_A2_06
    'Correction: cold hinges are a known fault on that deck. Nothing more.', 'Brine sweat. Nothing to say about that one.',
    'Hourly valve checks were standard during approach. Somebody forgot.', 'Tram faults were common. The ship was old.',
    'Silo vents cycle on a timer. The keeper did not know the timer.', 'Spare cells get tested. That is all a seal log shows.',
    'New safety rules went out every week. She missed the memo.', 'Approach schedule. A shutdown would have cost us the window.',
    'Orders without names were maintenance scripts. Thousands of them.', 'Logbooks wipe when storage fills. Bad copy, not a crime.',
    'Redundancy is a complete answer. Drones break; you build more.', 'Ramp tests protect the core. He was not cleared to see them.',
    'Sensor glitch. I apologized at the time. I apologize again.', 'Ice valves stick. A tag on it means someone checked it.',
    'Readings can arrive before a tech takes them. The sensors are faster.', 'Shared codes were a habit on that crew. Not mine to fix.',
    'Pod rosters change before landing. Medical reasons.', 'Dead cells hold charge. Nine seconds is a discharge, not a test.',
    'Engine Block, twenty-one thirty. Removed. I keep the engine logs. I do not keep this one.', 'Removed by ship authority. Ship authority is me. Correction: was me. Filed.',
    'One minute before the breach. Empty. Somebody wanted it empty. Next item.', 'Lifts stop. I ran a check. Twenty minutes is not long.',
    'Welded hatches were for pressure. Nobody signs pressure welds.', 'Power saving was the plan for every deck.',
    'Drain locks wait for a count. Counting takes time.', 'Hatches open for inspection. The chaplain did not need to know.',
    'Planning question. Every ship mind asks it. I asked it.']
for _i, (_when, _who, _lines, _close) in enumerate(UV, 1):
    _log('ITM_LOR_UV_%02d' % _i, 'Meridian Log: Engine Block, Entry %02d' % _i, 'REG_U', UV_LOCS[_i - 1], 'Engine Block', _i,
         _when, _who, _lines, _close, _OSTRA_UV[_i - 1],
         'Undervault UVREQ_08 (host %s). Reveal level 3: points at the ship mind, never names the deed (full truth waits for MQ_A2_06)' % UV_LOCS[_i - 1]
         + ('; stamped inside the forty-minute gap, so removed; body is the _RESTORED text' if _i in (19, 20, 21) else ''),
         removed=_i in (19, 20, 21))
