"""Generate every live ops and launch table in design/liveops/.
Run: python3 design/liveops/tools/gen_liveops.py  (from game-plan/)
All values not set by the master plan are Shardfall design choices, 3 Oct 2026."""
import csv, datetime as dt, os, colorsys, hashlib, re, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GP = os.path.dirname(os.path.dirname(ROOT))
def w(name, rows, cols=None):
    cols = cols or list(rows[0].keys())
    with open(os.path.join(ROOT, name), 'w', newline='') as f:
        c = csv.DictWriter(f, cols); c.writeheader(); c.writerows(rows)
    print(f'{name}: {len(rows)} rows')

LAUNCH = dt.date(2031, 4, 15)          # Tuesday, plan month 54 (Apr 2031); weekly reset Tue 17:00 UTC
def wk(n): return LAUNCH + dt.timedelta(weeks=n)   # n = weeks after launch

# ---------- expansions (plan 9.2: region, raid, enemy faction, faction questline; DR-018 power track)
EXP = [
 dict(exp_id='EXP_1', name='The Sunken Fore', plan_month=66, date=str(wk(52)), price_usd=29.99, region_id='REG_X1',
      region='The Sunken Fore: the Meridian\'s drowned bow section off the Saltmere coast, about 3.5 km2, tidal (map floods and drains every 20 min)',
      level_band='80-90 (own power track)', raid='Fathom Vault (6 players, 4 encounters)', enemy_faction='The Drowned Crew: bridge crew fused with Shard-coral; roles fodder, shield-bearer, skirmisher, artillery, heavy',
      faction_questline='The Tidewardens (12 quests): keepers who want the bow sealed forever', power_track='Tide Marks: 20 levels from 50 Fathom Pearls; up to +60% damage dealt and 40% damage reduction inside REG_X1 only',
      new_bosses='1 Shard-bearer, 1 Citadel boss, 2 field bosses, 4 raid bosses', reveal_month=60, preorder_month=63),
 dict(exp_id='EXP_2', name='The Burning Crown', plan_month=78, date=str(wk(104)), price_usd=29.99, region_id='REG_X2',
      region='Crownfire Peaks: mountains around the Meridian\'s fallen engine block, still burning after 900 years, about 3.5 km2, vertical with updraft vents',
      level_band='80-90 (own power track)', raid='The Engine Choir (6 players, 4 encounters)', enemy_faction='The Cinder Synod: engine-room automatons that worship the reactor fire',
      faction_questline='The Keelwrights (12 quests): shipwrights who want to make the Meridian fly again', power_track='Crown Sparks: 20 levels from 50 Ember Cores; same caps as Tide Marks, inside REG_X2 only',
      new_bosses='1 Shard-bearer, 1 Citadel boss, 2 field bosses, 4 raid bosses', reveal_month=72, preorder_month=75),
]

# ---------- seasons (plan 9.1: every 3 months a strike, a Hollowed Citadel variant, Shardborn items, a PvP map; free)
S = [  # n, name, element, region, theme words, strike, citadel modifier, shb weapon, shb armor, map, event, event modifier, feature, story
 (1,'Season of the Kiln','Ember','REG_01',['Kiln','Slag','Bellows','Forgefire','Clinker','Ashwright'],
  'The Sunken Index','Overheat: every third hit taken applies Burn','Kilnheart|Hammer','Furnace Mantle|Chest','Undervault Sluice',
  'Ember Tide','Region enemies apply Burn on every hit; Ember Tide bounties in every region','Forgeframe on PC (plan 9.3)',
  'Ostra recovers the reactor-room log: the crash was a deliberate burn, ordered from the bridge.'),
 (2,'Season of Drowned Bells','Storm','REG_02',['Tidebell','Brine','Squall','Undertow','Gull','Wrackline'],
  'Wreck of the Lowanchor','Stormsurge: lightning strikes a random 6 m circle every 20 s','Tidecaller|Scout Rifle','Drowned Captain\'s Helm|Head','Breakwater',
  'Night of Drowned Bells','Bells ring each 10 min; Drowned spawn at every coastal Anchor for 2 min','Forgeframe on consoles (plan 9.3); Iron Crown open cups begin',
  'A distress signal from the Meridian\'s bow, under the sea, answers Ostra by name.'),
 (3,'Season of the Root','Bloom','REG_03',['Briar','Rootsong','Mossheart','Thornveil','Sap','Canopy'],
  'The Rootvault','Overgrowth: thorns spread from fallen enemies and Root players who dodge into them','Briarlash|Twinblade','Thornmother\'s Grips|Hands','Canopy',
  'Thornmoot','Thorn Clans call a truce; clan champions roam regions as roaming elites','Armor loadouts: 4 more saved loadout slots',
  'The Thorn Clans hold a Shard that remembers the colonists\' first winter on Veyl.'),
 (4,'Season of the Fathom','Iron','REG_04',['Fathom','Pressure','Diver\'s','Keel','Ballast','Barnacle'],
  'Pressure Hull','Refraction: Ward hits reflect 15% of damage as Iron shards','Fathom Hook|Polearm','Diving Bell Helm|Head','Dry Dock',
  'Pressure Run','Timed salvage dives in the Glasswaste wreck fields; leaderboards per fireteam','Launches with Expansion 1, The Sunken Fore',
  'The bow is open. The Drowned Crew still keeps watch at their stations.'),
 (5,'Season of the Rime','Frost','REG_05',['Rime','Hoarfrost','Glacier','Snowveil','Icebound','Whiteout'],
  'Glacier Engine','Whiteout: fog cuts sight to 25 m; Frost Ward enemies take 25% less from non-Ember','Hoarfrost Repeater|Auto Rifle','Whiteout Cloak|Legs','Frostgate',
  'Rimewatch','Blizzard fronts cross Rimefall; shelter at Anchors or stack Slow','Photo mode filters and poses',
  'In the ice, Ostra finds the frozen colonists who never left their pods, and one is awake.'),
 (6,'Season of the Hollow Choir','Hollow','REG_06',['Hollow','Hushed','Pale','Echoing','Voidlit','Murmur'],
  'The Silent Nave','Hush: abilities cost 30% more charge; Drain stacks twice as fast','Hushblade|Curved Sword','Choirless Hood|Head','Nave of Echoes',
  'Choir of Silence','Choirborn invaders (NPC) hunt players in the open world; kill them for Silence Notes','Shard-note word list +80 words; note voting rework',
  'The Choir hears the Quiet answering in a voice that sounds like Ostra.'),
 (7,'Season of the Undertow','Storm','REG_X1',['Rip','Tideglass','Saltcrown','Riptide','Coral','Mariner'],
  'The Flooded Bridge','Rip Current: floors flood every 90 s and push players 4 m','Riptide Lance|Shard Lance','Coral Crown|Head','Tidal Lock',
  'Low Tide','The Sunken Fore drains fully for 3 weeks; sealed decks open','Expansion 1 raid challenge mode; Forgeframe raid-style rooms',
  'Below the bridge, the Tidewardens guard the captain\'s chair. It is not empty.'),
 (8,'Season of the Crown','Ember','REG_X2',['Crownfire','Cinder','Updraft','Engine','Smelt','Halo-Fire'],
  'Engine Heart','Ignition: the arena heats every 60 s; standing still applies Burn','Crownbreaker|Greatsword','Synod Furnace Plate|Chest','Updraft',
  'Kindling Rite','Engine vents erupt across all regions; Strider glide gets +50% lift','Launches with Expansion 2, The Burning Crown',
  'The engine block still holds enough fire to lift the Meridian. The Keelwrights want to try.'),
]
SEASON_MONTH = {n: 54 + 3*n for n in range(0, 9)}
def s_start(n): return wk(13*n)

seasons = [dict(season_id='SSN_00', n=0, name='Launch (Kindling)', plan_month=54, start=str(LAUNCH), end=str(s_start(1)-dt.timedelta(days=1)),
    element='-', focus_region='-', new_strike='6 launch Strikes STK_01..06', citadel_variant='6 Hollowed Citadels', shardborn='30 at launch (plan 4.3)',
    pvp_map='6 launch maps (pvp_maps.csv)', event='-', event_weeks='-', feature='Launch; patch 1.0.1 in week 2, 1.1.0 in week 6 (plan 8.3)',
    expansion='-', story_beat='Base campaign.', track_ranks=50, store_new_items='launch catalog (store_catalog.csv)', version='1.0.0')]
for (n,name,el,reg,words,strike,mod,shbw,shba,mp,ev,evmod,feat,story) in S:
    st = s_start(n)
    exp = next((e['name'] for e in EXP if e['date']==str(st)), '-')
    seasons.append(dict(season_id=f'SSN_{n:02d}', n=n, name=name, plan_month=SEASON_MONTH[n], start=str(st), end=str(st+dt.timedelta(weeks=13, days=-1)),
        element=el, focus_region=reg, new_strike=f'STK_S{n}: {strike}', citadel_variant=f'Hollowed Citadel {reg} variant: {mod}',
        shardborn=f'ITM_SHB_S{n}W {shbw.split("|")[0]} ({shbw.split("|")[1]}); ITM_SHB_S{n}A {shba.split("|")[0]} ({shba.split("|")[1]})',
        pvp_map=f'PVP_MAP_S{n}: {mp}', event=f'EVT_S{n}: {ev}', event_weeks=f'{st+dt.timedelta(weeks=4)} to {st+dt.timedelta(weeks=7,days=-1)}',
        feature=feat, expansion=exp, story_beat=story, track_ranks=50, store_new_items=11, version=f'1.{n+1}.0'))
w('season_roadmap.csv', seasons)
w('expansions.csv', EXP)

# ---------- future content IDs this plan names (defined here so they are not dangling; data rows requested in DR-LO-05 / DR-LO-10)
fut = []
for (n, name, el, reg, words, strike, mod, shbw, shba, *_r) in S:
    sid, st = f'SSN_{n:02d}', str(s_start(n))
    fut.append(dict(content_id=f'STK_S{n}', kind='Seasonal Strike (3 players)', name=strike, season_or_expansion=sid, first_available=st,
                    owner='design/levels/multiplayer (layout); data/world/strikes.csv row', status='In data (world/strikes.csv)' if n == 1 else 'Future content; data row requested (DR-LO-05)'))
    for suf, (nm, cls) in (('W', shbw.split('|')), ('A', shba.split('|'))):
        fut.append(dict(content_id=f'ITM_SHB_S{n}{suf}', kind=f'Seasonal Shardborn {"weapon" if suf == "W" else "armor"} ({cls})', name=nm, season_or_expansion=sid,
                        first_available=st, owner='data/items (Shardborn table)', status='Future content; seasonal Shardborn come after the 30 at launch; data row requested (DR-LO-05)'))
for e in EXP:
    fut.append(dict(content_id=e['region_id'], kind='Expansion region (level 80-90, own power track)', name=e['region'].split(':')[0], season_or_expansion=e['exp_id'],
                    first_available=e['date'], owner='design/world + data/world when the expansion enters production', status='Future content; requested (DR-LO-10)'))
for fid, nm, ex in (('FAC_DROWNED', 'The Drowned Crew', EXP[0]), ('FAC_CINDERSYNOD', 'The Cinder Synod', EXP[1])):
    fut.append(dict(content_id=fid, kind='Expansion enemy faction', name=nm, season_or_expansion=ex['exp_id'], first_available=ex['date'],
                    owner='data/actors when the expansion enters production', status='Future content; requested (DR-LO-10)'))
w('future_content_ids.csv', fut)

# ---------- PvP maps
# launch maps come from the owner, design/levels/multiplayer (mp_maps.csv ARENA_MP_01..06, arena_points.csv pads)
_mp = [r for r in csv.DictReader(open(os.path.join(GP, 'design/levels/multiplayer/mp_maps.csv'))) if re.fullmatch(r'ARENA_MP_0\d', r['map_id'])]
_pads = collections.Counter(r['map_id'] for r in csv.DictReader(open(os.path.join(GP, 'design/levels/multiplayer/arena_points.csv'))) if r['kind'].startswith('Power weapon pad'))
maps = [dict(map_id=f'PVP_MAP_{i+1:02d}', name=r['name'], region_theme=r['region'], season='SSN_00', modes='Clash, Control, Last Light', ranked='yes', competitive_pool='yes' if i<5 else 'Last Light only',
    power_pads=_pads[r['map_id']], layout_note=f"{r['size']}; owner design/levels/multiplayer {r['map_id']} (layouts/{r['map_id']}.txt)", asset_hook=f'MESH_PVP_MAP_{i+1:02d}') for i, r in enumerate(_mp)]
for s in S:
    s1 = s[0] == 1  # DR-LO-13 decided 2026-10-03: Season 1 uses multiplayer's LOC_MP_STK_S1 and ARENA_MP_S1 (REG_U)
    maps.append(dict(map_id=f'PVP_MAP_S{s[0]}', name=s[9], region_theme=('REG_U' if s1 else s[3]), season=f'SSN_{s[0]:02d}', modes='Clash, Control, Last Light', ranked='from season week 3',
        competitive_pool='next season', power_pads=2, layout_note=('52 x 40 m; owner design/levels/multiplayer ARENA_MP_S1 (Undervault, Ember season); built in Forgeframe so the community can remix it' if s1 else f'{s[2]} theme; built in Forgeframe so the community can remix it'), asset_hook=f'MESH_PVP_MAP_S{s[0]}'))
w('pvp_maps.csv', maps)

# ---------- events (definitions)
events = [
 dict(event_id='EVT_IRONTRIAL', name='Iron Trial', kind='Weekend PvP', when='Season weeks 3 and 10, Fri 17:00 to Tue 17:00 UTC', players='3v3, fireteam required',
      rules='7 wins on one card for a flawless reward; 3 losses end the card', rewards='Iron Trial armor ornaments (Seals) and ITM_LT_ENDGAME_ARENA_WIN rolls; no paid entry', ui='NTF_EVENT, event screen UV-066'),
 dict(event_id='EVT_DOUBLESEALS', name='Double Seals', kind='Weekend bonus', when='Season week 12, Fri to Tue', players='All',
      rules='Seal drops x2; weekly cap stays 100 (loops rule)', rewards='Faster cap, no extra cap', ui='NTF_EVENT'),
 dict(event_id='EVT_STRIDERRACE', name='Strider Derby', kind='Weekend race', when='Season week 8, Fri to Tue (from Season 1)', players='Solo time trial; ghosts of friends',
      rules='3 tracks per season, 1 built by the community in Forgeframe; medal times bronze/silver/gold', rewards='Derby dye per gold medal set; season-track XP x1.5', ui='NTF_EVENT, leaderboard'),
 dict(event_id='EVT_CRASHDAY', name='Crashday', kind='Annual anniversary', when='Season 4 and Season 8 week 4 (first week of May), 1 week', players='All',
      rules='Lantern Hold decorated; free anniversary emote; Meridian crash memorial quest (1 h)', rewards='Free emote + dye each year; Ostra anniversary log', ui='NTF_EVENT, banner'),
 dict(event_id='EVT_LONGNIGHT', name='The Long Night', kind='Annual winter', when='3 weeks from the Tuesday nearest 16 Dec', players='All',
      rules='Snow in Lantern Hold; lantern-lighting co-op activity; gift Shard-notes', rewards='Free Strider skin + emote + 2 dyes per year, all earnable', ui='NTF_EVENT, banner'),
]
for s in S:
    events.append(dict(event_id=f'EVT_S{s[0]}', name=s[10], kind='Seasonal event (3 weeks)', when='Season weeks 5 to 7', players='All, open world',
        rules=s[11] + '; season-track XP x1.5 (loops rule)', rewards='Event emote, Strider skin and 2 dyes, earn-only, stay earnable later (plan 9.1)', ui='NTF_EVENT, event screen UV-066'))
w('events.csv', events)

# ---------- weekly calendar (launch to end of Season 8)
STRIKES_BASE = [f'STK_0{i}' for i in range(1, 7)]
RAIDS = ['QUIETCORE', 'ARCHIVIST', 'MERIDIANGHOST', 'UNMADECHOIR']
CIT = ['REG_01','REG_02','REG_03','REG_04','REG_05','REG_06']
cal = []
for i in range(13*9):
    d = wk(i); sn, sw = divmod(i, 13); sw += 1
    strikes = STRIKES_BASE + [f'STK_S{k}' for k in range(1, sn+1)]
    cits = CIT + (['REG_X1'] if d >= dt.date.fromisoformat(EXP[0]['date']) else []) + (['REG_X2'] if d >= dt.date.fromisoformat(EXP[1]['date']) else [])
    raid = RAIDS[i % 4] + (' + Fathom Vault' if sn >= 4 and i % 2 else '') + (' + Engine Choir' if sn >= 8 and not i % 2 else '')
    weekend = {3:'EVT_IRONTRIAL',10:'EVT_IRONTRIAL',12:'EVT_DOUBLESEALS'}.get(sw, 'EVT_STRIDERRACE' if (sw == 8 and sn >= 1) else '')
    seasonal = f'EVT_S{sn}' if sn >= 1 and 5 <= sw <= 7 else ''
    annual = ''
    if sn in (4, 8) and sw == 4: annual = 'EVT_CRASHDAY'
    if d.month == 12 and 13 <= d.day <= 19 or (d.month == 12 and d.day > 19) or (d.month == 1 and d.day <= 9):
        # 3 weeks starting the Tuesday nearest 16 Dec
        y = d.year if d.month == 12 else d.year - 1
        t = dt.date(y, 12, 16); t = t + dt.timedelta(days=(1 - t.weekday() + 3) % 7 - 3)
        if t <= d < t + dt.timedelta(weeks=3): annual = 'EVT_LONGNIGHT'
    patch = ''
    if sw == 1: patch = seasons[sn]['version'] + (' (launch)' if sn == 0 else ' season update')
    elif sn == 0 and sw == 2: patch = '1.0.1 (top launch issues, plan 8.3)'
    elif sn == 0 and sw == 6: patch = '1.1.0 (telemetry balance, plan 8.3)'
    elif sw == 7 and sn: patch = f'1.{sn+1}.1 mid-season balance'
    comms = ['Lantern Hold Dispatch (weekly blog, Thursday)']
    if d.day <= 7: comms.append('Monthly developer update (plan 9.4)')
    if sw == 11: comms.append('Next-season reveal stream (2 weeks ahead)')
    if sw in (12, 13): comms.append('Next-season patch notes preview' if sw == 13 else 'Next-season trailer')
    if sn >= 1 and d.day <= 7: comms.append('Forgeframe Spotlight (plan 9.3)')
    store = 'Season drop: 11 new items + bundle' if sw == 1 and sn >= 1 else ('Launch catalog live' if i == 0 else 'Featured rotation (6 slots)')
    esp = ''
    ym = d.strftime('%Y-%m'); big = {'2032-02':'Iron Crown Major I (online)','2032-05':'Iron Crown Major II (LAN)','2032-08':'Iron Crown Championship Y1 (LAN)',
        '2032-12':'Iron Crown Major Y2-I (LAN)','2033-03':'Iron Crown Major Y2-II (LAN)','2033-06':'Iron Crown Major Y2-III (LAN)'}
    if 22 <= d.day <= 28:
        if ym in big: esp = big[ym]
        elif '2031-10' <= ym <= '2032-06': esp = 'Iron Crown Open Cup weekend (4 regions)'
        elif '2032-10' <= ym <= '2033-06': esp = 'Iron Crown Regional League week'
    cal.append(dict(week=i+1, reset_date=str(d), season_id=f'SSN_{sn:02d}', season_week=sw, featured_strike=(f'STK_S{sn}' if sw == 1 and sn else strikes[i % len(strikes)]),
        featured_citadel=cits[i % len(cits)] + ' + 2 CHL_HOLLOWCIT modifiers', raid_challenge=raid, weekend_event=weekend, seasonal_event=seasonal, annual_event=annual,
        patch=patch, store=store, comms='; '.join(comms), esports=esp, telemetry_review='yes' if i % 2 == 0 else ''))
w('events_calendar.csv', cal)

# ---------- store: price tiers (local price points, direct real money, no premium currency)
TIERS = [('PT_1',1.99,1.99,1.79,300,2.49,2.95,9.90),('PT_2',2.99,2.99,2.49,450,3.99,4.45,14.90),('PT_3',4.99,4.99,4.29,750,6.49,7.45,24.90),
 ('PT_4',7.99,7.99,6.99,1200,10.49,11.95,39.90),('PT_5',9.99,9.99,8.49,1500,12.99,14.95,49.90),('PT_6',14.99,14.99,12.99,2200,19.99,22.45,74.90),
 ('PT_7',19.99,19.99,16.99,3000,25.99,29.95,99.90),('PT_EXP',29.99,29.99,24.99,4400,39.99,44.95,149.90),('PT_PASS',49.99,49.99,42.99,7400,64.99,74.95,249.90),
 ('PT_STD',69.99,79.99,69.99,9680,89.99,109.95,349.90),('PT_COMPLETE',79.99,89.99,74.99,11000,104.99,124.95,399.90),('PT_DLX',99.99,109.99,94.99,13860,129.99,154.95,499.90),
 ('PT_CE',249.99,269.99,229.99,39800,329.99,399.95,1499.90)]
w('price_tiers.csv', [dict(tier=t, usd=u, eur=e, gbp=g, jpy=j, cad=c, aud=a, brl=b, use={'PT_1':'Dyes','PT_2':'Premium dyes, emotes','PT_3':'Strider skins, ornaments, emotes',
   'PT_4':'Animated Strider skins','PT_5':'Ornament sets','PT_6':'Smaller bundles (bundles only; single items stop at PT_5)','PT_7':'Season bundle (hard cap for any cosmetic purchase; must cost less than the items bought separately)','PT_EXP':'One expansion','PT_PASS':'Expansion Pass (both)',
   'PT_STD':'Standard Edition','PT_COMPLETE':'Complete Edition (year 2)','PT_DLX':'Deluxe Edition','PT_CE':"Collector's Edition"}[t]) for (t,u,e,g,j,c,a,b) in TIERS])

def hexcol(seed, el):
    base = {'Ember':0.03,'Storm':0.58,'Bloom':0.30,'Iron':0.10,'Frost':0.53,'Hollow':0.78,'-':0.0}[el]
    h = int(hashlib.md5(seed.encode()).hexdigest()[:4], 16) / 65535
    r, g, b = colorsys.hls_to_rgb((base + (h - 0.5) * 0.12) % 1, 0.30 + h * 0.4, 0.35 + h * 0.4)
    return '#%02X%02X%02X' % (int(r*255), int(g*255), int(b*255))

EMOTES = {1:['Stoke the Fire','Hammer Rest','Spark Toss','Bellows Breath','Ash Wipe','Ember Juggle','Forge Bow','Hot Iron Shake','Cinder Snap','Kiln Salute','Slag Kick','Quench'],
 2:['Ring the Bell','Wring Out','Spyglass','Bail Water','Gull Call','Sea Legs','Storm Shout','Knot Tying','Drowned Toll','Wave Watch','Brine Spit','Anchor Drop'],
 3:['Root Down','Leaf Catch','Thorn Pluck','Clan Drum','Moss Nap','Bark Knock','Seed Scatter','Briar Bow','Vine Swing','Canopy Gaze','Bloom Breath','Antler Call'],
 4:['Depth Check','Pressure Pop','Diver Wave','Ballast Lift','Hull Tap','Bubble Rise','Keel Sight','Lamp Signal','Coral Pick','Hatch Turn','Sonar Ping','Dive Salute'],
 5:['Breath Fog','Snow Angel','Ice Skate','Shiver','Frost Blow','Snowball','Hand Warm','Icicle Snap','Rime Stare','Glacier Lean','Pod Wake','Whiteout Wave'],
 6:['Hush','Faint Clap','Pale Bow','Void Stare','Choir Silence','Murmur','Fade Step','Empty Hum','Hollow Knock','Still Kneel','Mask Tilt','Unsing'],
 7:['Rip Pull','Coral Crown','Tidewarden Oath','Mariner Bow','Salt Toss','Drain Plug','Deck Swab','Captain Nod','Wave Ride','Bridge Salute','Undertow Sway','Low Tide Dig'],
 8:['Keel Raise','Engine Fist','Updraft Leap','Cinder Prayer','Synod Kneel','Crown Lift','Smelt Pour','Ignition','Spark Bow','Wing Flare','Shipwright Measure','Lift Off']}
KINDS_STORE = [('Strider skin','{w} Barding Strider Skin','PT_3'),('Strider skin','{w} Animated Hide Strider Skin','PT_4'),
 ('Emote','{e}','PT_2'),('Emote','{e}','PT_2'),('Emote','{e}','PT_3'),('Dye','{w} Dye','PT_1'),('Dye','{w} Dye','PT_1'),('Dye','{w} Gleam Dye','PT_2'),
 ('Armor ornament','{w} Ornament (any light set)','PT_3'),('Armor ornament','{w} Ornament Set (head, chest, hands, legs)','PT_5')]
PRICE = {t[0]: t[1] for t in TIERS}
catalog, track, ids = [], [], 0
# launch catalog straight from data/items/cosmetics.csv (owner: items generator)
for r in csv.DictReader(open(os.path.join(GP, 'data/items/cosmetics.csv'))):
    catalog.append(dict(item_id=r['item_id'], name=r['name'], kind=r['kind'], season_id='SSN_00', source=r['acquisition'], price_usd=r['price_usd'],
        price_tier={'1.99':'PT_1','2.99':'PT_2','4.99':'PT_3','7.99':'PT_4','9.99':'PT_5'}.get(r['price_usd'], ''), color_hex=r['color_hex'],
        first_available=str(LAUNCH), asset_hooks=r['icon'] + ((' ' + r['anim']) if r.get('anim') else ''), in_data='yes (items/cosmetics.csv)'))
def add(iid, name, kind, sn, source, tier, el, avail, extra=''):
    hooks = f'UI_ICON_{iid[4:]}' + {'Strider skin': f' MESH_{iid[4:]}', 'Emote': f' ANIM_{iid[4:]} SFX_{iid[4:]}', 'Armor ornament': f' MESH_{iid[4:]}', 'Dye': ''}.get(kind, '')
    catalog.append(dict(item_id=iid, name=name, kind=kind, season_id=f'SSN_{sn:02d}', source=source, price_usd=PRICE.get(tier, ''), price_tier=tier,
        color_hex=hexcol(iid, el) if kind == 'Dye' else '', first_available=avail, asset_hooks=hooks, in_data='requested (DR-LO-01)'))
for (n,name,el,reg,words,*_rest) in S:
    st = str(s_start(n)); em = EMOTES[n]; ei = 0
    for k, (kind, pat, tier) in enumerate(KINDS_STORE):
        e = em[ei] if kind == 'Emote' else ''; ei += kind == 'Emote'
        add(f'ITM_COS_S{n}_SHOP_{k+1:02d}', pat.format(w=words[k % 6], e=e), kind, n, 'Wardrobe Shop (real money)', tier, el, st)
    bundle = sum(PRICE[t] for _,_,t in KINDS_STORE)
    catalog.append(dict(item_id=f'ITM_COS_S{n}_BUNDLE', name=f'{name} Bundle (all 10 shop items)', kind='Bundle', season_id=f'SSN_{n:02d}', source='Wardrobe Shop (real money)',
        price_usd=19.99, price_tier='PT_7', color_hex='', first_available=st, asset_hooks=f'UI_ICON_COS_S{n}_BUNDLE',
        in_data=f'requested (DR-LO-01); items bought separately = {bundle:.2f} USD, bundle price discounts owned items'))
    # season track (earn-only) items
    TR = [(1,'Dye',f'{words[0]} Track Dye'),(10,'Emote',em[3]),(15,'Dye',f'{words[1]} Track Dye'),(25,'Strider skin',f'{words[2]} Track Strider Skin'),
          (30,'Dye',f'{words[3]} Track Dye'),(35,'Emote',em[4]),(40,'Armor ornament',f'{words[4]} Track Ornament (any medium set)'),(45,'Dye',f'{words[5]} Track Dye'),
          (50,'Strider skin',f'{words[0]} Ascendant Strider Skin (animated)')]
    trk = {r: (k, nm) for r, k, nm in TR}
    for rank in range(1, 51):
        rw = []
        if rank in trk:
            k, nm = trk[rank]; iid = f'ITM_COS_S{n}_TRK_{rank:02d}'
            add(iid, nm, k, n, f'Season track rank {rank} (earn-only, free)', '', el, st); rw.append(iid)
        if rank % 10 == 0: rw.append('ITM_MAT_STAR_01 x1')
        if rank % 5 == 0 and rank % 10: rw.append(f'Ostra Log S{n}-{rank//5}')
        track.append(dict(season_id=f'SSN_{n:02d}', rank=rank, xp_to_rank=1000, cumulative_xp=1000*rank, rewards=' + '.join(rw) or '-'))
    # event items (earn-only)
    for k, (kind, nm) in enumerate([('Emote', em[5]), ('Strider skin', f'{words[1]} Event Strider Skin'), ('Dye', f'{words[2]} Event Dye'), ('Dye', f'{words[4]} Event Dye')]):
        add(f'ITM_COS_S{n}_EVT_{k+1:02d}', nm, kind, n, f'EVT_S{n} event reward (earn-only; stays earnable later)', '', el, str(s_start(n) + dt.timedelta(weeks=4)))
# annual events and pre-order / edition items
for y, d_ln, d_cd in [(1, '2031-12-16', '2032-05-04'), (2, '2032-12-14', '2033-05-03')]:
    for k, (kind, nm, src, d) in enumerate([('Strider skin', f'Long Night Lantern Strider Skin {y}', 'EVT_LONGNIGHT', d_ln), ('Emote', ['Lantern Lighting', 'Snowfall Hush'][y-1], 'EVT_LONGNIGHT', d_ln),
            ('Dye', ['Long Night Blue Dye', 'Hearthglow Dye'][y-1], 'EVT_LONGNIGHT', d_ln), ('Dye', ['Frostlamp Dye', 'Midwinter Gold Dye'][y-1], 'EVT_LONGNIGHT', d_ln),
            ('Emote', ['Crashday Toast', 'Memorial Lantern'][y-1], 'EVT_CRASHDAY', d_cd), ('Dye', ['Meridian Hull Dye', 'First Landing Dye'][y-1], 'EVT_CRASHDAY', d_cd)]):
        add(f'ITM_COS_Y{y}_{src[4:]}_{k+1:02d}', nm, kind, 0, f'{src} year {y} (earn-only, free)', '', 'Frost' if 'LONG' in src else 'Ember', d)
for k, (kind, nm) in enumerate([('Strider skin', 'First Light Strider Skin'), ('Emote', 'Kindled Greeting')]):
    add(f'ITM_COS_PRE_{k+1:02d}', nm, kind, 0, 'Pre-order bonus; earnable in game from 6 months after launch (no permanent exclusives)', '', 'Ember', str(LAUNCH))
for k, (kind, nm) in enumerate([('Armor ornament', 'Meridian Officer Ornament Set'), ('Strider skin', 'Meridian Officer Barding'), ('Emote', 'Officer\'s Salute'),
        ('Emote', 'Bridge Command'), ('Dye', 'Officer Navy Dye'), ('Dye', 'Brass Trim Dye'), ('Dye', 'Command Red Dye')]):
    add(f'ITM_COS_DLX_{k+1:02d}', nm, kind, 0, "Deluxe and Collector's Edition; sold separately in the shop from launch + 12 months", 'PT_3' if kind != 'Dye' else 'PT_1', 'Iron', str(LAUNCH))
for e in EXP:
    for k, (kind, nm) in enumerate([('Strider skin', f'{e["name"]} Strider Skin'), ('Emote', f'{e["name"]} Victory'), ('Emote', f'{e["name"].split()[-1]} Salute')]):
        add(f'ITM_COS_{e["exp_id"].replace("_","")}_{k+1:02d}', nm, kind, 0, f'{e["exp_id"]} content reward (earn-only, expansion owners)', '', 'Storm' if e['exp_id'] == 'EXP_1' else 'Ember', e['date'])
# items the data merge already took in appear twice (launch read + generated row): keep the generated row
# (it carries the season and date) and mark it merged; note any price that differs from data
_data = {r['item_id']: r for r in csv.DictReader(open(os.path.join(GP, 'data/items/cosmetics.csv')))}
_gen_ids = {c['item_id'] for c in catalog if c['in_data'].startswith('requested')}
catalog = [c for c in catalog if not (c['in_data'].startswith('yes') and c['item_id'] in _gen_ids)]
for c in catalog:
    d = _data.get(c['item_id'])
    if d and c['in_data'].startswith('requested'):
        note = 'requested (DR-LO-01; in items/cosmetics.csv)'   # stays "requested": the data merge re-adds these rows on every rebuild
        if d['price_usd'] and c['price_usd'] != '' and abs(float(d['price_usd']) - float(c['price_usd'])) > 0.001:
            note += f"; data price {d['price_usd']} differs (DR-LO-11)"
        c['in_data'] = note
w('store_catalog.csv', catalog)
w('season_track.csv', track)

# ---------- retail editions and SKUs
eds = [
 dict(edition_id='ED_STD', name='Standard Edition', tier='PT_STD', price_usd=69.99, formats='Digital (PC, PS5, Xbox Series); disc (PS5, Xbox Series)',
      contents='Base game', physical_extras='Disc box: reversible cover, folded A3 map of Veyl', available='Launch'),
 dict(edition_id='ED_DLX', name='Deluxe Edition', tier='PT_DLX', price_usd=99.99, formats='Digital only (all platforms)',
      contents='Base game; Expansion Pass (EXP_1 + EXP_2, worth 59.98 USD); Meridian Officer cosmetic set (ITM_COS_DLX_01..07); digital artbook (120 pages); digital soundtrack (40 tracks)',
      physical_extras='-', available='Launch; no early access in any edition (design choice)'),
 dict(edition_id='ED_CE', name="Collector's Edition", tier='PT_CE', price_usd=249.99, formats='PS5 disc, Xbox Series disc, PC (code in box)',
      contents='Everything in Deluxe', physical_extras="38 cm resin statue of a Kindled riding a Strider; 20 cm light-up Ostra Shard (USB-C, 3 modes); SteelBook case; 200-page hardcover artbook; 60 x 45 cm cloth map of Veyl; 5 enamel faction pins; Kindled's field journal (96 pages); certificate (numbered)",
      available='Launch; one run of 60,000 units worldwide; bill of materials target 95 USD a unit'),
 dict(edition_id='ED_PASS', name='Expansion Pass', tier='PT_PASS', price_usd=49.99, formats='Digital', contents='EXP_1 and EXP_2 on release', physical_extras='-', available='Launch to EXP_2 release'),
 dict(edition_id='ED_EXP1', name='Expansion: The Sunken Fore', tier='PT_EXP', price_usd=29.99, formats='Digital', contents='EXP_1', physical_extras='-', available=EXP[0]['date']),
 dict(edition_id='ED_EXP2', name='Expansion: The Burning Crown', tier='PT_EXP', price_usd=29.99, formats='Digital', contents='EXP_2', physical_extras='-', available=EXP[1]['date']),
 dict(edition_id='ED_COMPLETE', name='Complete Edition', tier='PT_COMPLETE', price_usd=79.99, formats='Digital; disc (PS5, Xbox Series) with expansion codes',
      contents='Base game + EXP_1 + EXP_2 + Meridian Officer set', physical_extras='Same as Standard', available=EXP[1]['date'] + ' (year 2 relaunch)'),
]
w('retail_editions.csv', eds)
skus = []
for plat in ['PS5', 'Xbox Series', 'PC']:
    for reg in ['NA', 'EU', 'UK', 'APAC', 'LATAM']:
        for ed, init in [('ED_STD', {'PS5': 0.55, 'Xbox Series': 0.30}), ('ED_CE', {'PS5': 0.45, 'Xbox Series': 0.30, 'PC': 0.25})]:
            if plat not in init: continue
            share = {'NA': 0.38, 'EU': 0.30, 'UK': 0.10, 'APAC': 0.14, 'LATAM': 0.08}[reg]
            units = round(700000 * init[plat] * share, -3) if ed == 'ED_STD' else round(60000 * init[plat] * share, -2)
            skus.append(dict(sku=f'SKU_{ed[3:]}_{plat.replace(" ","").upper()}_{reg}', edition_id=ed, platform=plat, region=reg, first_run_units=int(units),
                rating_label={'NA':'ESRB M','EU':'PEGI 18','UK':'PEGI 18','APAC':'CERO D / GRAC 18 / ACB MA15+','LATAM':'ESRB M / ClassInd 18'}[reg],
                languages='Text 12, voice 5 (localization.csv)', on_disc='Full 1.0 game; day-one patch downloads',
                gold_master='Month 52 (Gate 7)', replication='6 weeks', ship_to_retail='2 weeks before launch'))
w('retail_skus.csv', skus)

# ---------- marketing beats (plan 8.1 anchors; months from project start, Oct 2026 = month 0)
def cal_m(m): y, mo = divmod(9 + int(m), 12); return f'{2026 + y}-{mo+1:02d}'
MK = [
 (30,'Pre-reveal','Trademarks cleared on title and faction names; domains and social handles reserved','Legal, owned channels','-','Internal',1),
 (34,'Pre-reveal','Platform partner pitch for showcase slot; press list built','Platform holders','-','Showcase slot booked',0),
 (36,'Reveal','Reveal trailer at a major showcase; Steam, PlayStation and Xbox wishlist pages; website; Discord opens to the public','Showcase, stores, YouTube, socials','Reveal trailer (xlsx A105), key art UV-112, logo UV-113','1M wishlists in 30 days',12),
 (37,'Reveal follow-up','Developer interviews; Visual Bible art drop; first dev diary (Combat: sword and rifle are equals)','Press, YouTube','Dev diary 1','Discord 150k members',2),
 (39,'Dev diaries','Monthly dev diaries begin (world, Weave, Striders, factions), one every month to launch','YouTube, blog','Dev diary 2..12','Wishlists +100k a month',4),
 (42,'World showcase','Region showcase: Cinderreach and Lantern Hold in-engine','Stream','World trailer','2M wishlists',3),
 (45,'Gameplay deep-dive','30-minute gameplay deep-dive: combat, co-op, a Citadel, a Shard-bearer (plan 8.1, 9 months out)','Showcase stream, press','Gameplay trailer','2.5M wishlists',8),
 (46,'Co-op showcase','4-player co-op and Strikes; release date announced (April 2031)','Stream, press','Co-op trailer','Release date trend top 10',3),
 (47,'PvP and Forgeframe','3v3 arena reveal and Forgeframe teaser; beta sign-ups open','Stream','PvP trailer','1M beta sign-ups',3),
 (48,'Pre-orders','Editions and Collector\'s Edition revealed; pre-orders open at all retailers; pre-order bonus announced (earnable later)','Stores, retail','Edition art, CE photo shoot, 60 store images (A106)','600k pre-orders by launch',6),
 (49,'Closed beta','Closed online beta, 50,000 players, co-op and PvP stress test (plan 7.2)','Game client, Discord','Beta trailer','Server targets met; beta survey 80% would buy',5),
 (50,'Story trailer','Story trailer: Ostra, the Quiet, the factions','Showcase, YouTube','Story trailer','3M wishlists',6),
 (51,'Preview events','Hands-on preview events for press and creators, first 5 hours (plan 8.1)','Press, creators','Preview build','Preview coverage 85+ sentiment',6),
 (52,'Gold','Gold master announcement; launch-date ad buys begin (TV, digital, outdoor in 6 cities)','Paid media','15 s and 30 s spots','-',20),
 (53.5,'Creator early access','Creator early access 2 weeks before launch (plan 8.1); review embargo lifts 2 days before launch','Creators, press','Review guide, creator kit','Review score 85+ (Gate 8)',4),
 (54,'Launch','Launch trailer; launch livestream; live ops room 14 days (plan 8.2)','All','Launch trailer','4M units year one (monetization.md forecast)',10),
 (54.5,'Post-launch','Accolades trailer; patch 1.0.1 notes; thank-you post with community stats','YouTube, socials','Accolades trailer','D7 retention 45%',1),
 (55,'Year-one roadmap','Year-one roadmap stream: Seasons 1 to 3, Forgeframe, Expansion 1 teaser','Stream','Roadmap graphic','-',1),
 (57,'Season 1','Season 1 trailer; Forgeframe PC launch','All','Season trailer','Returning players 30% of lapsed',2),
 (60,'Expansion 1 reveal','The Sunken Fore reveal at showcase; Season 2; Forgeframe consoles; Iron Crown esports announced','Showcase','Expansion reveal trailer','-',3),
 (63,'Expansion 1 pre-order','Gameplay deep-dive and pre-orders; Season 3','Stream, stores','Expansion gameplay trailer','35% attach goal (monetization.md)',3),
 (66,'Expansion 1 launch','The Sunken Fore launch; Season 4; Crashday (first anniversary)','All','Launch trailer','35% attach year one',5),
 (72,'Expansion 2 reveal','The Burning Crown reveal; Season 6; Iron Crown Year 1 Championship recap','Showcase','Expansion reveal trailer','-',3),
 (75,'Expansion 2 pre-order','Gameplay deep-dive and pre-orders; Season 7','Stream, stores','Expansion gameplay trailer','-',3),
 (78,'Expansion 2 launch','The Burning Crown launch; Season 8; Complete Edition relaunch at retail; Crashday (second anniversary)','All, retail','Complete Edition trailer and box','Complete Edition 1M units first year',5),
]
w('marketing_beats.csv', [dict(plan_month=m, calendar=cal_m(m), stage=st, beat=b, channels=ch, assets=a, kpi_target=k, share_of_marketing_budget_pct=round(p*100/sum(x[-1] for x in MK),1)) for (m,st,b,ch,a,k,p) in MK])

# ---------- creator program
w('creator_program.csv', [
 dict(tier='CRT_SPARK', name='Spark', entry='Any creator with 1,000+ followers on one platform; open sign-up from reveal', perks='Press kit, B-roll, Discord creator channel, monthly creator newsletter, code for every season launch',
      support_a_creator='Yes: players enter the creator code in the Wardrobe Shop; creator receives 5% of the net price (design choice)', obligations='Follow embargoes and disclosure rules; no paid power or account selling content'),
 dict(tier='CRT_LANTERN', name='Lantern', entry='10,000+ followers or a Forgeframe map with 25,000 plays', perks='All Spark perks; preview events; creator early access 2 weeks before launch; 2 dev Q&A sessions a year',
      support_a_creator='Yes, 5%', obligations='As Spark'),
 dict(tier='CRT_BEACON', name='Beacon', entry='Invite only, about 150 creators worldwide', perks='All Lantern perks; studio visits; reveal-stream co-streaming rights; Forgeframe early builds; creator-designed dye each year (sold, 50% of net to the creator, design choice)',
      support_a_creator='Yes, 5%', obligations='As Spark; quarterly feedback session'),
 dict(tier='CRT_FORGE', name='Forgeframe Builder', entry='Any player who publishes a map or challenge room', perks='Monthly Forgeframe Spotlight (plan 9.3); best map each season enters the arena rotation or Strider Derby; builder credit in game',
      support_a_creator='No money for mods (no paid mods, design choice); featured builders get a free cosmetic bundle', obligations='Mod hub review rules (plan 4.8)'),
])

# ---------- esports (3v3 arena: Marlon's decision 3 Oct 2026 overrides plan 3.11's larger teams)
ESP = [
 ('ESP_Y1_OPEN','Year 1','Iron Crown Open Cups','2031-10 to 2032-06, monthly','Online, NA / EU / APAC / LATAM','Open sign-up, 3-player teams plus 1 substitute, Ranked skill rating floor Gold','Double elimination, Bo3 (Bo5 final)',10000,'Circuit points'),
 ('ESP_Y1_MAJ1','Year 1','Iron Crown Major I','2032-02','Online regional finals','Top 8 per region from Open Cups points','Groups then single elimination, Bo5',100000,'Circuit points'),
 ('ESP_Y1_MAJ2','Year 1','Iron Crown Major II','2032-05','LAN, one city','Top 16 worldwide by points','Double elimination, Bo5, Bo7 grand final',250000,'Circuit points'),
 ('ESP_Y1_CHAMP','Year 1','Iron Crown Championship','2032-08','LAN, arena venue','Top 16 by points + 4 last-chance qualifiers','Groups then double elimination, Bo7 final',500000,'Title, champions dye (earn-only to viewers via Drops)'),
 ('ESP_Y2_LEAGUE','Year 2','Iron Crown Regional Leagues','2032-10 to 2033-06, 2 splits','Online, 4 regions, 10 teams each','Promotion from Open Cups; relegation each split','Round robin Bo3, playoffs Bo5',300000,'Points'),
 ('ESP_Y2_MAJ','Year 2','Iron Crown Majors I-III','2032-12, 2033-03, 2033-06','LAN, rotating regions','Top 4 per region per split','Double elimination Bo5',600000,'Points'),
 ('ESP_Y2_CHAMP','Year 2','Iron Crown Championship','2033-08','LAN, arena venue','Top 16 by points','Double elimination, Bo7 final',1500000,'Title'),
]
w('esports_circuit.csv', [dict(event_id=a, year=b, name=c, dates=d, format_place=e, entry=f, bracket=g, prize_pool_usd=h, awards=i) for (a,b,c,d,e,f,g,h,i) in ESP])
w('esports_ruleset.csv', [
 dict(rule_id='ESR_01', rule='Modes and order', value='Bo5 series: Control, Clash, Last Light, Control, Clash (Last Light is Bo7 rounds)'),
 dict(rule_id='ESR_02', rule='Map pool', value='5 maps: PVP_MAP_01..05 plus the previous season map from season 2; one pool refresh a season'),
 dict(rule_id='ESR_03', rule='Map pick', value='Higher seed bans 1, lower seed bans 1, alternating picks; deciders by remaining map'),
 dict(rule_id='ESR_04', rule='Loadouts', value='Normalized level 80, upgrades +15 (Ranked rule); Shardborn weapons and armor disabled; Resonances disabled'),
 dict(rule_id='ESR_05', rule='Power weapons', value='ITM_PWR_01..06 on fixed pads; first spawn 1:00, respawn 120 s (loops rule); spawn shown to both teams'),
 dict(rule_id='ESR_06', rule='Tonics', value='3 per life (loops rule)'),
 dict(rule_id='ESR_07', rule='Client', value='Tournament client build with spectator mode, 30 s delay broadcast, observer free camera, replay from server inputs'),
 dict(rule_id='ESR_08', rule='Pause', value='Technical pauses only, 10 min per team per series'),
 dict(rule_id='ESR_09', rule='Patch lock', value='Competitive play uses the patch live 14 days before the event'),
 dict(rule_id='ESR_10', rule='Integrity', value='Kernel anti-cheat on LAN PCs; console finals on supplied hardware; no account sharing; age 16+'),
 dict(rule_id='ESR_11', rule='Viewer rewards', value='Platform Drops: watch 60 min of a Major for an earn-only Iron Crown dye; Championship gives a Strider skin; all also earnable in game'),
])

# ---------- KPIs
w('liveops_kpis.csv', [dict(kpi_id=k, metric=m, target=t, review=r) for (k,m,t,r) in [
 ('KPI_01','Crash rate','under 0.5% of sessions (Gate 8)','Daily in launch room, then weekly'),
 ('KPI_02','Review score','85 or higher (Gate 8)','Launch'),
 ('KPI_03','Retention D1 / D7 / D30','60% / 45% / 30%','Every 2 weeks (plan 9.4)'),
 ('KPI_04','Season track completion','50% of active players reach rank 50 by week 13 (6 h a week player at about week 11)','Per season'),
 ('KPI_05','Returning players at season launch','30% of players lapsed 4+ weeks return in week 1','Per season'),
 ('KPI_06','Matchmaking time','Strike under 90 s, Arena Quickplay under 60 s at 90th percentile','Daily'),
 ('KPI_07','Store conversion','12% of monthly active players buy at least once a year; average 25 USD (monetization.md)','Monthly'),
 ('KPI_08','Store refund rate','under 2% of purchases','Monthly'),
 ('KPI_09','Expansion attach','35% of owners (monetization.md)','Per expansion'),
 ('KPI_10','Forgeframe','10,000 published maps or rooms in the first 6 months on PC','Monthly'),
 ('KPI_11','Player support','First reply under 24 h; 90% of tickets closed in 72 h','Weekly'),
 ('KPI_12','Sentiment','Steam recent reviews Mostly Positive or better every season','Weekly'),
]])


# ---------- strings for ui/strings.csv and ui/strings_data.csv (merge via DR-LO-03)
import math
def S_(sid, screen, text, notes=''):
    return dict(str_id=sid, screen=screen, text_en=text, max_chars=math.ceil(len(text)*1.4), tokens=' '.join(t.strip('{}') for t in text.split() if t.startswith('{')), notes=notes)
st = []
for s in seasons[1:]: st += [S_(f"STR_{s['season_id']}_NAME", 'Season pass and events', s['name']), S_(f"STR_{s['season_id']}_DESC", 'Season pass and events', s['story_beat'])]
for e in events: st += [S_(f"STR_{e['event_id']}_NAME", 'Season pass and events', e['name'])]
for e in EXP: st += [S_(f"STR_{e['exp_id']}_NAME", 'Store and title menu', e['name'])]
for e in eds: st += [S_(f"STR_{e['edition_id']}_NAME", 'Store and title menu', e['name'])]
for m in maps: st += [S_(f"STR_{m['map_id']}_NAME", 'Arena', m['name'])]
for c in catalog:
    if c['in_data'].startswith('requested'): st.append(S_(f"STR_{c['item_id']}_NAME", 'Cosmetics shop', c['name'], 'strings_data.csv'))
for sid, scr, t in [
 ('STR_SHOP_ORNAMENTS','Cosmetics shop','Ornaments'),('STR_SHOP_FEATURED','Cosmetics shop','Featured'),('STR_SHOP_SEASON','Cosmetics shop','This Season'),
 ('STR_SHOP_BUNDLE_OWNED','Cosmetics shop','Price lowered for items you own.'),('STR_SHOP_CREATOR','Cosmetics shop','Support a Creator'),
 ('STR_SHOP_CREATOR_HINT','Cosmetics shop','Enter a creator code. They get 5% of what you spend.'),('STR_SHOP_EARN_ONLY','Cosmetics shop','Earned in play. Not for sale.'),
 ('STR_SHOP_RETURNS','Cosmetics shop','Every item stays for sale. Nothing leaves the shop.'),('STR_SHOP_LOCAL','Cosmetics shop','Prices in {VAR_currency}, set by your platform store.'),
 ('STR_SEASON_TRACK_FREE','Season pass and events','Season Track: free for everyone'),('STR_SEASON_XP_RANK','Season pass and events','{VAR_xp} / 1,000 XP'),
 ('STR_SEASON_OSTRA_LOG','Season pass and events','Ostra Log {VAR_n} unlocked'),('STR_SEASON_STARMETAL','Season pass and events','Starmetal x1'),
 ('STR_EVENT_XP_BONUS','Season pass and events','Event live: Season XP x1.5'),('STR_EVENT_RETURNS','Season pass and events','Missed it? Event rewards return in later seasons.'),
 ('STR_DERBY_GOLD','Season pass and events','Gold time: {VAR_time}'),('STR_PREORDER_NOTE','Store and title menu','Pre-order items become earnable in play six months after launch.')]:
    st.append(S_(sid, scr, t))
w('strings_liveops.csv', st)
