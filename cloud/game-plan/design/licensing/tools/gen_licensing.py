#!/usr/bin/env python3
"""Generate every CSV in design/licensing/. Run from game-plan/: python3 design/licensing/tools/gen_licensing.py
Values are Shardfall design choices (3 Oct 2026) unless a row cites the plan or design/liveops/."""
import csv, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
T = "[TITLE]"  # working title placeholder: "Shardfall" is taken (design/production/ratings_legal.md)


def cal(m):
    """Plan month to calendar month. Month 54 = launch, Apr 2031 (liveops), so month 0 = Oct 2026."""
    m = int(m)
    return f"{2026 + (9 + m) // 12}-{(9 + m) % 12 + 1:02d}"


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


# ---------------------------------------------------------------- categories
# id, category, example products, partner type, model, price band, first wave month, yr1 SKUs, age label, notes
CATS = [
    ("LIC_CAT_01", "Statues and premium collectibles", "1/6 and 1/4 scale polyresin statues of the six Shard-bearers, Kindled and Strider dioramas", "LIC_PTR_01", "License", "149-999", 54, 6, "15+ collectible", "Numbered runs; one Shard-bearer per release, in boss order"),
    ("LIC_CAT_02", "Action figures", "7-inch articulated figures: Kindled (melee and firearm builds), companions, Hull Knight, Hollowed", "LIC_PTR_02", "License", "24.99-39.99", 54, 8, "15+", "Swappable weapons reflect 'sword and rifle are equals' (plan 3.2)"),
    ("LIC_CAT_03", "Stylised vinyl figures", "4-inch stylised figures of companions, Unit 9, Ostra Shard", "LIC_PTR_02", "License", "14.99-19.99", 56, 10, "15+", "Never sold as blind boxes: nothing paid is random, in the game or out of it"),
    ("LIC_CAT_04", "Prop replicas and cosplay", "Retail Ostra Shard lamp, wearable Hull Knight helmet, foam Kindled sword and rifle, Anchor lantern", "LIC_PTR_01", "License", "79-399", 56, 5, "15+ (props 18+ where local law requires)", "Firearm replicas: bright orange tip and non-functional, per US and EU replica rules"),
    ("LIC_CAT_05", "Apparel", "Tees, hoodies, faction jackets, caps, socks", "LIC_PTR_03", "License + first-party", "24.99-89.99", 36, 40, "Adult sizes only", "Reveal wave sold first-party only; licensees from launch"),
    ("LIC_CAT_06", "Accessories", "Enamel pins, keychains, patches, backpacks, wallets", "LIC_PTR_03", "License + first-party", "9.99-79.99", 36, 25, "Adult", "Faction pin set matches the five Collector's pins"),
    ("LIC_CAT_07", "Jewelry", "Sterling Shard pendant, faction signet rings, Anchor earrings", "LIC_PTR_14", "License", "49-199", 56, 6, "Adult", "Nickel-free (EU REACH Annex XVII)"),
    ("LIC_CAT_08", "Homeware and drinkware", "Mugs, Lantern Hold tankard, throw blankets, Weave night light, coasters", "LIC_PTR_10", "License", "14.99-69.99", 54, 15, "Adult", "Food-contact tests for drinkware"),
    ("LIC_CAT_09", "Posters and art prints", "Key art posters, numbered giclee prints of Visual Bible paintings, region maps", "LIC_PTR_04", "First-party + license", "19.99-149", 36, 30, "All", "Artist credited on every print"),
    ("LIC_CAT_10", "Gaming accessories", "Controller faceplates and skins, headset, mouse pads, controller stands", "LIC_PTR_09", "License", "19.99-199", 54, 8, "All", "Needs platform-holder licensing for controllers"),
    ("LIC_CAT_11", "Music", "Original soundtrack: streaming, 2CD, 4LP vinyl box, Ostra theme 7-inch", "LIC_PTR_07", "License", "9.99-129.99", 54, 4, "All", "Rights cleared by audio (production ratings_legal.md music line)"),
    ("LIC_CAT_12", "Publishing", "Artbooks, novels, comics, anthology, guide book (see transmedia.csv)", "LIC_PTR_05; LIC_PTR_06", "License", "4.99-59.99", 50, 6, "Mature readers", "Canon rules in README apply"),
    ("LIC_CAT_13", "Tabletop", "Co-op board game (1 to 4 players, Citadel crawl), tabletop RPG core book, card game", "LIC_PTR_08", "License", "39.99-149", 60, 3, "14+", "Board game mirrors 1 to 4 players and Anchors"),
    ("LIC_CAT_14", "Puzzles, calendars, stationery", "1000-piece jigsaws, wall calendar, notebooks, map of Veyl print", "LIC_PTR_10", "License", "12.99-34.99", 54, 8, "All", "Calendar uses AF dating from the lore bible"),
    ("LIC_CAT_15", "Plush", "Unit 9 plush, Strider plush, Ostra Shard pillow", "LIC_PTR_11", "License", "19.99-49.99", 58, 4, "14+ (tested to toy standards anyway)", "Not marketed to children: M-rated brand"),
    ("LIC_CAT_16", "Construction sets", "Brick-built Lantern Hold, Strider, Spinegate cryo ward", "LIC_PTR_11", "License", "49.99-199.99", 66, 3, "16+", "Year two, after launch numbers prove demand"),
    ("LIC_CAT_17", "Digital fan goods", "Official cosplay patterns, 3D-print files, wallpapers", "LIC_PTR_04", "First-party", "0-29.99", 56, 12, "All", "Wallpapers free; patterns paid"),
    ("LIC_CAT_18", "Promotional partners", "Snack, drink and hardware promotions", "LIC_PTR_13", "Co-marketing", "-", 48, 3, "Adult audiences only", "Codes grant only cosmetics that are also earnable in play (liveops store rules)"),
]
write("product_categories.csv",
      ["category_id", "category", "products", "partner_type", "model", "price_band_usd", "first_wave_month", "first_wave_calendar", "year1_skus", "age_label", "notes"],
      [(c[0], c[1], c[2], c[3], c[4], c[5], c[6], cal(c[6]), c[7], c[8], c[9]) for c in CATS])

# ---------------------------------------------------------------- partner types
# no real companies named: partners are picked by RFP in month 34-38
PTRS = [
    ("LIC_PTR_01", "Premium collectibles maker", "LIC_CAT_01; LIC_CAT_04", "Exclusive per category, worldwide", "12% of wholesale", 250000, "50% of MG on signing", 3, "Proven polyresin sculpt and paint quality; numbered-run experience; GPSR responsible person in EU", 38),
    ("LIC_PTR_02", "Mass-market figure maker", "LIC_CAT_02; LIC_CAT_03", "Exclusive per category, worldwide", "10% of wholesale", 400000, "25% of MG", 3, "Specialty and online retail reach; articulated figure line history; no blind-box formats", 38),
    ("LIC_PTR_03", "Apparel and accessories licensee", "LIC_CAT_05; LIC_CAT_06", "Non-exclusive, by region (NA, EU+UK, APAC)", "12% of wholesale", 300000, "25% of MG", 3, "Adult sizing; ethical audit (SA8000 or amfori BSCI); regional retail reach", 40),
    ("LIC_PTR_04", "First-party store operator", "LIC_CAT_05; LIC_CAT_06; LIC_CAT_09; LIC_CAT_17", "Service contract, not a license", "Operator fee 18% of net sales", 0, "-", 3, "Print-on-demand plus stocked warehouse in NA and EU; ships to 40+ countries", 34),
    ("LIC_PTR_05", "Book publisher", "LIC_CAT_12 (artbooks, novels, anthology)", "Exclusive for English; foreign rights sublicensed", "10% of cover price hardcover, 8% paperback, 25% of net ebook and audio", 0, "150000 for the novel trilogy; 60000 per artbook", 5, "Genre fiction list; art book production quality; translation network for 12 text languages", 38),
    ("LIC_PTR_06", "Comics publisher", "LIC_CAT_12 (comics)", "Exclusive, worldwide English", "10% of cover price", 0, "40000 per series", 3, "Monthly series and collected editions; digital distribution", 40),
    ("LIC_PTR_07", "Music label", "LIC_CAT_11", "Exclusive physical; streaming self-distributed", "15% of wholesale on physical", 50000, "On signing", 5, "Vinyl pressing capacity booked 9 months ahead", 44),
    ("LIC_PTR_08", "Tabletop publisher", "LIC_CAT_13", "Exclusive per game type", "8% of wholesale", 100000, "25% of MG", 4, "Co-op board game track record; RPG line support", 50),
    ("LIC_PTR_09", "Peripheral maker", "LIC_CAT_10", "Non-exclusive", "10% of wholesale", 150000, "25% of MG", 2, "Holds official PlayStation and Xbox accessory licenses", 44),
    ("LIC_PTR_10", "Homeware and gift licensee", "LIC_CAT_08; LIC_CAT_14", "Non-exclusive, by region", "10% of wholesale", 100000, "25% of MG", 3, "Food-contact compliance; gift retail reach", 44),
    ("LIC_PTR_11", "Toy maker (plush, construction)", "LIC_CAT_15; LIC_CAT_16", "Exclusive per category", "8% of wholesale", 200000, "25% of MG", 3, "EN 71 and ASTM F963 lab program; adult collector lines", 50),
    ("LIC_PTR_12", "Animation studio and streaming platform", "Transmedia LIC_TM_08", "Option, then series deal", "Option fee 500000; license fee per episode; 5% of streamer-reported backend", 0, "Option fee", 7, "Adult animation slate; agrees to canon approval at script, animatic and final", 58),
    ("LIC_PTR_13", "Promotional partner", "LIC_CAT_18", "Campaign deal", "No royalty; partner funds media at 1:1 match", 0, "-", 1, "Brand fit with M rating; codes give earnable cosmetics only", 46),
    ("LIC_PTR_14", "Jewelry maker", "LIC_CAT_07", "Exclusive per category", "12% of wholesale", 75000, "50% of MG", 3, "Precious-metal hallmarking; nickel-free", 48),
    ("LIC_PTR_15", "Regional licensing agent", "All categories in Japan, Korea, China, LATAM", "Agent, by territory", "Commission 30% of royalties collected", 0, "-", 3, "Local retail relationships; local-language approvals", 40),
]
write("partner_types.csv",
      ["partner_id", "partner_type", "covers", "rights", "royalty", "min_guarantee_usd", "advance", "term_years", "selection_criteria", "sign_by_month", "sign_by_calendar"],
      [p + (cal(p[9]),) for p in PTRS])

# ---------------------------------------------------------------- products (launch-window SKUs with price bands)
# id, product, category, MSRP, wholesale share of MSRP, target COGS share of wholesale, wave month, units forecast yr1
PRDS = [
    ("Reveal tee: Shard motif", "LIC_CAT_05", 29.99, 36, 18000), ("Reveal hoodie: Meridian crest", "LIC_CAT_05", 64.99, 36, 7000),
    ("Reveal poster: key art", "LIC_CAT_09", 19.99, 36, 12000), ("Reveal pin: Ostra Shard", "LIC_CAT_06", 12.99, 36, 15000),
    ("Faction pin set (5)", "LIC_CAT_06", 39.99, 48, 20000), ("Map of Veyl print 60 x 45 cm", "LIC_CAT_09", 34.99, 48, 9000),
    ("Hull Knights jacket", "LIC_CAT_05", 89.99, 54, 6000), ("Lantern Church hoodie", "LIC_CAT_05", 64.99, 54, 8000),
    ("Salvagers' Guild work shirt", "LIC_CAT_05", 49.99, 54, 6000), ("Kindled tee (6 region colourways)", "LIC_CAT_05", 29.99, 54, 40000),
    ("Anchor beanie", "LIC_CAT_05", 24.99, 54, 10000), ("Strider backpack", "LIC_CAT_06", 79.99, 54, 5000),
    ("Unit 9 keychain", "LIC_CAT_06", 12.99, 54, 25000), ("Vael the Ember Regent 1/6 statue", "LIC_CAT_01", 399.00, 54, 4000),
    ("Kindled on Strider 1/4 statue (numbered 1,500)", "LIC_CAT_01", 999.00, 56, 1500), ("Kindled figure, sword build 7-inch", "LIC_CAT_02", 29.99, 54, 30000),
    ("Kindled figure, rifle build 7-inch", "LIC_CAT_02", 29.99, 54, 30000), ("Kessa Vane figure 7-inch", "LIC_CAT_02", 29.99, 54, 18000),
    ("Hollowed Knight figure 7-inch", "LIC_CAT_02", 34.99, 54, 15000), ("Unit 9 vinyl figure", "LIC_CAT_03", 16.99, 56, 25000),
    ("Ostra Shard lamp, retail (no CE numbering)", "LIC_CAT_04", 79.99, 56, 12000), ("Hull Knight wearable helmet", "LIC_CAT_04", 249.00, 58, 2500),
    ("Sterling Shard pendant", "LIC_CAT_07", 89.00, 56, 5000), ("Lantern Hold tankard", "LIC_CAT_08", 34.99, 54, 10000),
    ("Ember mug (heat-change)", "LIC_CAT_08", 19.99, 54, 20000), ("Weave throw blanket", "LIC_CAT_08", 49.99, 54, 6000),
    ("Controller faceplate set", "LIC_CAT_10", 29.99, 54, 15000), ("Extended mouse pad: Veyl map", "LIC_CAT_10", 29.99, 54, 20000),
    ("Soundtrack 2CD", "LIC_CAT_11", 24.99, 54, 8000), ("Soundtrack 4LP vinyl box", "LIC_CAT_11", 129.99, 56, 6000),
    ("Ostra's theme 7-inch single", "LIC_CAT_11", 19.99, 54, 5000), (f"The Art of {T} (trade hardcover)", "LIC_CAT_12", 45.00, 54, 40000),
    ("1000-piece jigsaw: Lantern Hold", "LIC_CAT_14", 24.99, 54, 12000), ("Wall calendar 901 AF", "LIC_CAT_14", 16.99, 54, 10000),
    ("Unit 9 plush", "LIC_CAT_15", 29.99, 58, 15000), ("Co-op board game: Citadels of Veyl", "LIC_CAT_13", 99.99, 62, 25000),
    ("Tabletop RPG core book", "LIC_CAT_13", 59.99, 64, 15000), ("Brick-built Lantern Hold", "LIC_CAT_16", 149.99, 66, 10000),
]
WH = {"First-party": None}  # first-party goods: we keep retail margin
rows = []
for i, (name, cat, msrp, m, units) in enumerate(PRDS, 1):
    first_party = m == 36 or cat in ("LIC_CAT_09",) and m < 54
    wholesale = round(msrp * 0.5, 2)  # retailers buy at 50% of MSRP (keystone), design choice
    if first_party:
        cogs = round(msrp * 0.28, 2)
        income = round(units * (msrp - cogs - msrp * 0.18), 0)  # less operator fee
        model = "First-party store"
        roy = "-"
    else:
        rate = next(float(p[4].split("%")[0]) for p in PTRS if p[0] == next(c[3] for c in CATS if c[0] == cat).split(";")[0])
        cogs = round(wholesale * 0.45, 2)
        income = round(units * wholesale * rate / 100, 0)
        model = "Licensed"
        roy = f"{rate:g}%"
    rows.append((f"LIC_PRD_{i:03d}", name, cat, model, f"{msrp:.2f}", f"{wholesale:.2f}", f"{cogs:.2f}", roy, m, cal(m), units, int(income)))
write("products.csv",
      ["product_id", "product", "category_id", "model", "msrp_usd", "wholesale_usd", "target_cogs_usd", "royalty", "wave_month", "wave_calendar", "units_yr1", "income_to_us_usd"],
      rows)
PRODUCT_INCOME = sum(r[-1] for r in rows)

# ---------------------------------------------------------------- roadmap
MS = [
    (6, "Gate 1", "Final title chosen from cleared shortlist; trademark filings start for title, logo, faction and creature names in Nice classes 9, 14, 16, 18, 20, 21, 24, 25, 28, 41", "Legal; production", "BLOCKER: no logo, product or contract until this lands"),
    (12, "Brand", "Logo and wordmark locked; Madrid Protocol filings in US, EU, UK, JP, KR, CN, AU, CA, BR, MX", "Legal; art", "Registrations take 12 to 24 months"),
    (30, "Brand", "Trademarks cleared (matches liveops marketing_beats month 30); domains and handles reserved", "Legal", "-"),
    (30, "Team", "Head of Consumer Products hired", "Production", "See team.csv"),
    (32, "Brand", "Consumer products style guide v1: logo lockups, key art, character turnarounds, palettes, fonts, faction marks, do and don't pages", "Art; consumer products", "Built from the Visual Bible and design/art/05-fonts.md"),
    (34, "Partners", "First-party store operator contracted; NDA pitches to collectibles, figure, apparel, publishing partners", "Consumer products", "-"),
    (36, "Reveal", "First-party store opens with the reveal wave (4 SKUs); transmedia producer hired", "Consumer products; marketing", "Reveal at a major showcase (liveops month 36)"),
    (38, "Partners", "Master licenses signed: collectibles, figures, publishing", "Consumer products; legal", "Retail buy windows run 9 to 12 months before shelf"),
    (40, "Partners", "Apparel, comics and regional agents signed; Collector's Edition component list approved", "Consumer products; supply chain", "-"),
    (42, "Approvals", "Licensee concept approvals; launch-window line shown to retail buyers at a licensing trade show", "Consumer products", "Concept, pre-production and final sample are the three approval gates"),
    (46, "Approvals", "Pre-production samples approved for launch wave", "Consumer products", "-"),
    (48, "Pre-orders", "Collector's Edition and licensed launch products open for pre-order (liveops month 48)", "Marketing; retail", "-"),
    (50, "Transmedia", "Free digital comic 'Bay 9' released", "Transmedia", "See transmedia.csv"),
    (52, "Sell-in", "Launch wave ships to retail; Collector's goods at regional kitting centres", "Licensees; supply chain", "See manufacturing_schedule.csv"),
    (54, "Launch", "Launch wave: about 60 licensed SKUs plus first-party store; artbook and soundtrack day one", "All", "Launch Tue 15 Apr 2031"),
]
SEASONS = [(57, "Season 1 Kiln", "Ember"), (60, "Season 2 Drowned Bells", "Storm"), (63, "Season 3 Root", "Bloom"), (66, "Season 4 Fathom + Expansion 1 The Sunken Fore", "Iron"),
           (69, "Season 5 Rime", "Frost"), (72, "Season 6 Hollow Choir", "Hollow"), (75, "Season 7 Undertow", "Sunken Fore"), (78, "Season 8 Crown + Expansion 2 The Burning Crown", "Crownfire")]
for m, s, theme in SEASONS:
    MS.append((m, "Season capsule", f"{s}: first-party capsule of 5 SKUs in the {theme} palette (tee, pin, print, mug, sticker sheet)", "Consumer products", "Season dates in liveops season_roadmap.csv"))
MS += [
    (66, "Expansion", "Expansion 1 licensed wave: Sunken Fore statue, figures, artbook vol. 2 announced", "Licensees", "-"),
    (66, "Annual", "Crashday merch drop (first Crashday, liveops events.csv), repeated each year", "Consumer products", "-"),
    (78, "Expansion", "Expansion 2 and Complete Edition wave; licensing renewals negotiated for year 4 onward", "Consumer products; legal", "Most licenses are 3-year terms signed month 38 to 50"),
]
MS.sort(key=lambda r: r[0])
write("roadmap.csv", ["milestone_id", "plan_month", "calendar", "stage", "milestone", "owner", "notes"],
      [(f"LIC_MS_{i:02d}", r[0], cal(r[0]), r[1], r[2], r[3], r[4]) for i, r in enumerate(MS, 1)])

# ---------------------------------------------------------------- transmedia
# id, format, title, era, seed in game, characters, spoiler tier, partner, announce, release, length, price, purpose
TMS = [
    ("Artbook", f"The Art of {T}", "All", "Visual Bible", "-", "Safe", "LIC_PTR_05", 48, 54, "200 pages, 23 x 30 cm hardcover", "45.00", "Same 200 pages as the Collector's artbook with a trade cover; spoilers past Act 1 kept out until launch +12 months"),
    ("Free digital comic", "Bay 9", "900 AF, the night before the game", "MQ_P_01 Spinegate cryo ward", "Spinegate ward keepers; an unnamed sleeper", "Safe", "LIC_PTR_06", 49, 50, "24 pages", "0", "Pre-launch marketing; ends as the player's pod opens"),
    ("Audio drama (free podcast)", "Log Readings", "40 AF onward", "BOOK_001 Log Readings for Every Day", "Lio Hale; Archivist Oswin Hale (narrator)", "Belief layer only", "First-party", 53, 55, "10 x 20 min", "0", "Voiced by the game cast; uses only bridge entries 1 to 12 like the in-game book"),
    ("Comic series", "The Chain of Command", "11 AF, founding of the Hull Knights", "BOOK_007 The Chain of Command", "Aldo Marr; young Iselde line ancestors", "Belief layer only", "LIC_PTR_06", 50, 52, "6 monthly issues of 28 pages, then a collected edition at month 58", "4.99 per issue; 19.99 collected", "Shows the oath being written; never explains why it names Ires and not the ship"),
    ("Novel 1", "The Waking Years", "0 to 3 AF", "BOOK_027 The Waking Years", "An unnamed Bay 4 survivor; the six officers as seen from below", "Belief layer only", "LIC_PTR_05", 52, 56, "110,000 words, hardcover and ebook, audiobook by game cast", "28.99", "Ends with the Pact of the Six; the crash cause is never shown"),
    ("Novel 2", "The Glass War", "560 AF", "BOOK_029 The Glass War; BOOK_009 Holding a Gate", "Knight-Captain Oren Vasse; Brannoch; Corsa", "Belief layer only", "LIC_PTR_05", 60, 66, "120,000 words", "28.99", "Lands with Expansion 1; Corsa and Brannoch already show the madness (lucid lines stay in the game)"),
    ("Novel 3", "The First Speaker", "301 AF, founding of the Quiet Hand", "BOOK_055 to BOOK_058 Quiet Hand contracts", "The first Speaker; Kindled targets", "Truth layer allowed only for what the game already reveals", "LIC_PTR_05", 74, 80, "110,000 words", "28.99", "Held to launch +26 months because the game reveals who the Speaker serves"),
    ("Animated limited series", "The Spine Riots", "230 AF", "BOOK_028 The Spine Riots", "Reeve Calder; the first Thorn Clan families", "Belief layer only", "LIC_PTR_12", 66, 90, "8 x 24 min adult animation", "Streaming", "Greenlight gate at month 58: 5M units sold; production 30 months"),
    ("Anthology", "Stories from the Six Holds", "3 to 899 AF", "One story per in-game book author in design/writing/books.csv", "Twelve in-game authors", "Belief layer only", "LIC_PTR_05", 68, 72, "12 stories, 90,000 words", "24.99", "Each story is written by a different novelist and edited by the narrative lead"),
    ("Tabletop RPG", "Veyl Roleplaying Game", "All eras before 900 AF", "Lore bible sections 2 to 6", "Player-made Kindled", "Belief layer only", "LIC_PTR_08", 60, 64, "320-page core book", "59.99", "Tier 3: inspired by, not canon"),
    ("Guidebook", f"{T}: The Field Atlas", "900 AF", "World and region data", "-", "Spoiler-flagged sections", "LIC_PTR_05", 52, 54, "352 pages", "49.99", "Maps and bestiary only; no walkthrough of choices so the game keeps the journal (plan 3.8)"),
    ("Live action", "Option only", "-", "-", "-", "-", "LIC_PTR_12", 0, 0, "-", "-", "No deal before 10M units sold and the animated series ships; review at month 96"),
]
write("transmedia.csv",
      ["project_id", "format", "working_title", "era", "seeded_by_in_game", "characters", "spoiler_rule", "partner", "announce_month", "release_month", "release_calendar", "length", "price_usd", "notes"],
      [(f"LIC_TM_{i:02d}", t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7] or "-", t[8] or "-", cal(t[8]) if t[8] else "-", t[9], t[10], t[11]) for i, t in enumerate(TMS, 1)])

# ---------------------------------------------------------------- Collector's Edition bill of materials
BOM = [
    ("Statue: Kindled on a Strider, 38 cm", "Polyresin, hand-painted, 4 parts with magnet keys; 2.8 kg", "Collectibles factory", 42.00, 85000, "Sculpt 12 wk, moulds 6 wk, run 12 wk"),
    ("Ostra Shard lamp, 20 cm", "Frosted PC shell, RGB LED board, USB-C 5 V, 3 modes, 1.5 m cable; no battery", "Electronics factory", 11.50, 58000, "Tooling 8 wk, run 8 wk; includes 18,000 certification"),
    ("SteelBook case", "Tinplate, embossed, debossed logo", "SteelBook maker", 2.60, 6000, "6 wk"),
    ("Artbook, 200 pages hardcover", "23 x 30 cm, 157 gsm matte art paper, FSC, foil cover", "Book printer", 7.80, 0, "Print 5 wk"),
    ("Cloth map of Veyl", "60 x 45 cm cotton canvas, hemmed, folded in sleeve", "Textile printer", 1.90, 0, "4 wk"),
    ("Faction pins (5)", "Soft enamel, 30 mm, gold plating, on backing card", "Pin maker", 2.75, 1500, "4 wk"),
    ("Kindled's field journal", "96 pages, linen-bound, 120 gsm cream paper", "Book printer", 2.40, 0, "Print 4 wk"),
    ("Numbered certificate", "300 gsm card, foil number 00001 to 60000", "Book printer", 0.25, 0, "2 wk"),
    ("Game: disc in SteelBook or PC code card", "Platform-replicated disc (PS5, Xbox Series) or printed code card (PC); average", "Platform replicators", 3.00, 0, "Gold master month 52 + 6 wk replication"),
    ("Packaging", "Rigid box with magnetic lid, moulded pulp inserts (no plastic), printed sleeve, brown shipper", "Packaging factory", 9.80, 12000, "6 wk"),
    ("Inserts", "Safety leaflet in 12 languages, Deluxe code card, GPSR label", "Book printer", 0.40, 0, "2 wk"),
    ("Assembly and factory QC", "Pack-out of everything except the disc; 100% lamp power-on test", "Packaging factory", 3.20, 0, "Runs with production"),
    ("Scrap and defect allowance", "3% overrun on statue and lamp", "-", 4.00, 0, "-"),
]
BOM_TOTAL = round(sum(b[3] for b in BOM), 2)
write("ce_bill_of_materials.csv",
      ["component_id", "component", "spec", "supplier_type", "unit_cost_usd", "one_off_tooling_usd", "lead_time"],
      [(f"LIC_MFG_{i:02d}",) + b for i, b in enumerate(BOM, 1)] + [("LIC_MFG_TOTAL", "Total per unit", f"Target 95.00 (liveops retail_editions.csv); headroom {95 - BOM_TOTAL:.2f}", "-", f"{BOM_TOTAL:.2f}", sum(b[4] for b in BOM), "-")])

# ---------------------------------------------------------------- manufacturing schedule (Collector's and physical)
MFG = [
    (40, 40, "Component list, price target and box design approved", "Production; art"),
    (41, 41, "RFQ to three suppliers per component; factory social-compliance audits", "Supply chain"),
    (42, 44, "Statue digital sculpt from the game's Kindled and Strider meshes; lamp industrial design", "Art; collectibles factory"),
    (44, 44, "Sculpt and paint master approved by art director", "Art"),
    (45, 46, "Moulds and injection tooling cut", "Factories"),
    (46, 47, "Engineering samples; lamp sent to accredited lab for FCC, CE, UKCA, RCM, KC tests", "Supply chain; lab"),
    (47, 47, "Pre-production sample signed off; all certificates in hand", "Supply chain; legal"),
    (48, 50, "Mass production of 60,000 units at about 5,000 a week (12 weeks); numbering at pack-out", "Factories"),
    (50, 50, "Third-party inspection, AQL 2.5 major and 4.0 minor, ISTA 3A drop test on packed units", "Inspection agency"),
    (50, 52, "Ocean freight to five regional kitting centres (5 to 6 weeks door to door)", "Freight forwarder"),
    (52, 53, "Discs replicated after gold master (6 weeks, liveops retail_skus.csv); PC units need no disc and ship first", "Platform replicators"),
    (53, 53, "Disc inserted into SteelBook, box sealed, labelled per retailer; about 3 days", "Kitting centres"),
    (53, 54, "Ship to retail and direct pre-order customers 2 weeks before launch", "3PL; retailers"),
    (54, 54, "Launch; no reprint ever (numbered run); damaged-unit spares 1% held per region", "Supply chain"),
]
write("manufacturing_schedule.csv", ["step_id", "start_month", "end_month", "start_calendar", "end_calendar", "step", "owner"],
      [(f"LIC_MFS_{i:02d}", a, b, cal(a), cal(b), s, o) for i, (a, b, s, o) in enumerate(MFG, 1)])

# ---------------------------------------------------------------- logistics (CE units by region from liveops retail_skus.csv)
SKUS = os.path.join(OUT, "..", "liveops", "retail_skus.csv")
units = {}
with open(SKUS) as f:
    for r in csv.DictReader(f):
        if r["edition_id"] == "ED_CE":
            units[r["region"]] = units.get(r["region"], 0) + int(r["first_run_units"])
LANES = {
    "NA": ("Guangdong, CN", "Ocean FCL to US West Coast", "3PL kitting centre, US West Coast", 5, 4.20, "US HTS 3926.40 statuettes of plastic, 5.3%; Section 301 tariffs may apply, so price checked at month 46", "FCC Part 15B, ICES-003, Prop 65 label"),
    "EU": ("Guangdong, CN", "Ocean FCL to Rotterdam", "3PL kitting centre, Netherlands", 6, 4.60, "CN 3926.40, 6.5%; VAT at import; EU responsible person on label (GPSR)", "CE (EMC, RoHS), WEEE registration, PPWR packaging marks, Triman for France"),
    "UK": ("Guangdong, CN", "Ocean FCL to Felixstowe", "3PL kitting centre, UK Midlands", 6, 4.80, "UK tariff 3926.40, 6%; VAT at import", "UKCA (EMC, RoHS), UK responsible person"),
    "APAC": ("Guangdong, CN", "Truck to Hong Kong hub, then ocean to Tokyo, Busan, Sydney", "3PL kitting centre, Hong Kong; local 3PLs in JP, KR, AU", 3, 3.10, "Japan and Australia duty-free or low for these goods; Korea 6.5%", "RCM (AU), KC (KR); Japan PSE not needed for USB-powered lamp"),
    "LATAM": ("Guangdong, CN", "Ocean to Miami for LATAM ex-Brazil; Brazil via local importer to Santos", "3PL Miami; importer of record in Brazil", 6, 6.50, "Brazil import taxes near 60% landed, so Brazil allocation priced locally; ClassInd rating label", "Anatel not needed for no-radio lamp; INMETRO checked for the lamp"),
}
lrows = []
for reg in ["NA", "EU", "UK", "APAC", "LATAM"]:
    o, mode, dc, wk, fr, duty, marks = LANES[reg]
    lrows.append((f"LIC_LOG_{reg}", reg, units.get(reg, 0), o, mode, dc, wk, f"{fr:.2f}", duty, marks))
write("logistics_lanes.csv", ["lane_id", "region", "ce_units", "origin", "mode", "destination_dc", "transit_weeks", "freight_usd_per_unit", "duty_and_tax", "compliance_marks"], lrows)
CE_UNITS = sum(r[2] for r in lrows)
AVG_FREIGHT = sum(r[2] * float(r[7]) for r in lrows) / CE_UNITS

# ---------------------------------------------------------------- compliance and QC
QC = [
    ("Ostra Shard lamp", "US", "FCC Part 15 Subpart B (unintentional radiator), SDoC", "Accredited lab", 47),
    ("Ostra Shard lamp", "EU", "EMC Directive 2014/30/EU, RoHS 2011/65/EU, CE mark, GPSR 2023/988 file", "Accredited lab", 47),
    ("Ostra Shard lamp", "UK", "EMC Regulations 2016, RoHS, UKCA mark", "Accredited lab", 47),
    ("Ostra Shard lamp", "CA, AU, KR", "ICES-003, RCM, KC EMC", "Accredited lab", 47),
    ("Ostra Shard lamp", "All", "LED photobiological safety IEC 62471 (exempt group target)", "Accredited lab", 47),
    ("Statue", "EU, UK", "REACH SVHC and Annex XVII (phthalates, lead in paint); labelled 15+ collectible, not a toy", "Accredited lab", 47),
    ("Statue", "US", "Lead in surface coatings and Prop 65 screening; general conformity certificate (adult product)", "Accredited lab", 47),
    ("Pins, jewelry", "EU, UK", "Nickel release EN 1811; cadmium and lead limits", "Accredited lab", 47),
    ("Plush and construction sets (licensee)", "EU, UK, US", "EN 71-1/2/3, ASTM F963, CPSIA tracking labels; tested as toys although sold 14+", "Licensee lab, we review", 56),
    ("Drinkware (licensee)", "EU, US", "Food-contact: EU 1935/2004, FDA, Prop 65 for lead in glaze", "Licensee lab, we review", 52),
    ("Packaging", "All", "ISTA 3A drop and vibration on packed CE units", "Inspection agency", 50),
    ("Packaging", "EU", "PPWR 2025/40 marks; FSC paper; no plastic inserts", "Supply chain", 46),
    ("Factories", "All", "Social-compliance audit (amfori BSCI or SA8000) before order", "Audit firm", 41),
    ("All CE units", "All", "AQL inspection 2.5 major, 4.0 minor; 100% lamp power-on at pack-out", "Inspection agency", 50),
]
write("compliance_qc.csv", ["check_id", "item", "market", "standard_or_test", "who", "due_month", "due_calendar"],
      [(f"LIC_QC_{i:02d}",) + q + (cal(q[4]),) for i, q in enumerate(QC, 1)])

# ---------------------------------------------------------------- team
TEAM = [
    ("Head of Consumer Products", 1, 30, "Owns the program, partner deals, revenue"),
    ("Licensing manager", 1, 36, "Contracts, royalty reports, audits"),
    ("Transmedia producer", 1, 36, "Books, comics, animation; canon approvals with the narrative lead"),
    ("Product development and approvals coordinator", 2, 40, "Runs the three-gate approval flow; 10 business days per submission"),
    ("Supply chain manager", 1, 40, "Collector's Edition and first-party stock"),
    ("Brand artist", 1, 32, "Style guide, approvals art, product renders"),
    ("Regional licensing agents", 0, 40, "Contracted, not staff (LIC_PTR_15)"),
]
write("team.csv", ["team_id", "role", "headcount", "start_month", "start_calendar", "duty"],
      [(f"LIC_TEAM_{i:02d}", r, n, m, cal(m), d) for i, (r, n, m, d) in enumerate(TEAM, 1)])

# ---------------------------------------------------------------- Collector's Edition unit economics
ws = 249.99 * 0.75  # retailers keep 25% on high-price collector's items (design choice)
game_roy = 52.50 * 0.30  # platform royalty on the game's wholesale share
ce = [
    ("Retail price", 249.99), ("Retailer margin 25%", -(249.99 - ws)), ("Wholesale to us", ws),
    ("Platform royalty on game share (30% of 52.50)", -game_roy), ("Bill of materials", -BOM_TOTAL),
    ("Freight (weighted by region)", -AVG_FREIGHT), ("Duty average", -3.50), ("Kitting and 3PL", -3.00),
    ("Returns and damage 2% of wholesale", -ws * 0.02), ("Tooling and certification spread over 60,000", -sum(b[4] for b in BOM) / 60000),
]
contrib = ws - game_roy - BOM_TOTAL - AVG_FREIGHT - 3.50 - 3.00 - ws * 0.02 - sum(b[4] for b in BOM) / 60000
ce.append(("Contribution per unit", contrib))
ce.append((f"Contribution for {CE_UNITS:,} units", contrib * CE_UNITS))
write("ce_unit_economics.csv", ["line", "usd"], [(a, f"{b:.2f}") for a, b in ce])

# ---------------------------------------------------------------- revenue summary
rev = [
    ("Launch-window products (products.csv, year 1)", PRODUCT_INCOME, "Royalties on licensed lines plus first-party margin"),
    ("Minimum guarantees committed (partner_types.csv)", sum(p[5] for p in PTRS), "Floor if sales disappoint"),
    ("Collector's Edition contribution", round(contrib * CE_UNITS), "ce_unit_economics.csv"),
    ("Publishing advances (novels and artbooks)", 150000 + 60000 * 2 + 40000, "Recouped against royalties"),
]
write("revenue_summary.csv", ["line", "usd", "source"], [(a, int(b), c) for a, b, c in rev])

# ---------------------------------------------------------------- data requests: none needed
write("data-requests.csv", ["dr_id", "owner_table", "current_value", "requested_value", "reason"], [])
print(f"BOM {BOM_TOTAL}, CE units {CE_UNITS}, contribution/unit {contrib:.2f}, product income {PRODUCT_INCOME}")
