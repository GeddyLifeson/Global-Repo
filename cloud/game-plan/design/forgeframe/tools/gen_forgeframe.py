#!/usr/bin/env python3
"""Generates the Forgeframe (shipped player editor) design tables.
Plan 3.12, 4.8, 9.3; runtime in design/tech (read-only). All values are design choices of 3 Oct 2026.
Run: python3 design/forgeframe/tools/gen_forgeframe.py
"""
import csv, os, glob
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..')
DATA = os.path.join(HERE, '..', '..', '..', 'data')

def w(name, cols, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        x = csv.writer(f); x.writerow(cols); x.writerows(rows)
    return len(rows)

def split(block):  # pipe-separated lines -> rows
    return [[c.strip() for c in l.split('|')] for l in block.strip().splitlines() if l.strip()]

# ------------------------------------------------------------------ modes
MODES = split('''
FF_MODE_RECORD|Record Editor|Edit or add data records (items, enemies, quests, strings) as an override file over base data|PC|Mod package|Opens the same records designers use (plan 3.12); load-order override via SfRecords
FF_MODE_SANDBOX|Sandbox Map Builder|Build PvP maps from the prefab palette on a blank or stock terrain plate|PC, PS5, Xbox Series X and S|Map|3v3 arena rules from design/loops; cross-platform if within the Series S budget
FF_MODE_CHALLENGE|Challenge Room|Build PvE rooms: enemy waves, traps, timers, scoring, win and fail rules|PC, PS5, Xbox Series X and S|Challenge room|1 to 3 players; uses stock enemies at a chosen level band
FF_MODE_RULES|Mode Rules|Make custom game modes: score, teams, respawn, loadouts, power weapon timers|PC, PS5, Xbox Series X and S|Mode|Attach to any shared map
FF_MODE_SCRIPT|Forgescript|Text scripting (sandboxed Luau) for maps, rooms, modes and mods|PC|Script|Same API as Loom graphs; compiles to the same bytecode
FF_MODE_LOOM|Loom graphs|Visual node scripting for maps, rooms and modes|PC, PS5, Xbox Series X and S|Script|Every Forgescript API call has a node
FF_MODE_TEST|Test Play|Play the work in place with bots, a budget overlay and a script debugger|All|-|Bots fill empty slots; one button returns to the editor at the same camera
FF_MODE_PUBLISH|Publish|Validate, describe, rate and upload to the Forge Hub|All|-|Runs the automated checks in curation_rules.csv before upload
''')
w('modes.csv', ['mode_id', 'name', 'purpose', 'platforms', 'output', 'notes'], MODES)

# ------------------------------------------------------------------ UX screens
SCREENS = split('''
FF_SCR_LAUNCH|Launcher|All|Start page: New, Open, Recent, Tutorials, Forge Hub, Settings|Tiles 3x2; last project on the left|A opens; Y opens Hub
FF_SCR_BROWSER|Project browser|All|List of local projects with thumbnail, mode, size, budget state, last edit|Sort by date, name, mode; filter by mode|X new; Y duplicate; Menu delete with confirm
FF_SCR_REC_GRID|Record grid|PC|Spreadsheet view of one record table, base values greyed, overridden cells bold|Left: table tree (data/ folders); centre: grid; right: inspector|Ctrl+F search; Ctrl+D duplicate row as new ID
FF_SCR_REC_INSPECT|Record inspector|PC|One record as a form with field types, ranges, references and tooltip from the base table header|Reference fields have a picker and a jump link|F12 jump to referenced record
FF_SCR_REC_INHERIT|Inheritance view|PC|Parent chain for a record and which fields each layer sets|Tree left to right: base, DLC, each mod in load order|Hover shows the winning value
FF_SCR_REC_CONFLICT|Conflict viewer|PC|Every record two or more loaded mods change, with the winning value and a merge option|Same as the dev Record override viewer (tech 05)|Merge writes a patch file
FF_SCR_REC_VALIDATE|Validation report|PC|Runs the same rules as data/tools/validate.py on the mod: missing references, bad patterns, out-of-range values, missing strings|Errors block publish; warnings do not|Click an error to jump to the cell
FF_SCR_VIEWPORT|Sandbox viewport|All|3D editor view with gizmo, grid snap, surface snap, free camera and play camera|Top bar: mode, undo, redo, test; bottom: budget meter|See controls.csv
FF_SCR_PALETTE|Prefab palette|All|Categories of placeable prefabs with search and favourites|Left panel PC; radial plus list on controller|Thumbnails rendered in engine
FF_SCR_OUTLINER|Outliner|All|Every placed object in folders and layers, with lock and hide toggles|Right panel PC; tab page on controller|Group with Ctrl+G
FF_SCR_PROPS|Properties|All|Selected object: transform, team, visibility, physics, script tags, variant, colour from the map palette|Right panel under the outliner|Multi-edit shows mixed values as dashes
FF_SCR_LAYERS|Layers|All|Named layers per mode variant (for example Slayer layer and Control layer)|Toggle in test play|Max 16 layers
FF_SCR_BUDGET|Budget meter|All|Live bars for each budget in budgets.csv for the target platform|Amber at 80%, red at 100%|Red blocks publish
FF_SCR_LOOM|Loom graph editor|All|Node graph per object or per map; events on the left, actions right|Search palette by verb; comment boxes; wire colours by type|Controller: snap-to-port cursor
FF_SCR_SCRIPT|Forgescript editor|PC|Code editor with autocomplete from script_api.csv, type hints and inline errors|Breakpoints and watch in Test Play|Ctrl+Space autocomplete
FF_SCR_DEBUG|Script debugger|All|Event log, variable watch, instruction-budget graph per tick|Overlay in Test Play|Pauses on error
FF_SCR_RULES|Mode rules|All|Form for score limit, time limit, teams, respawn time, loadouts, power weapon timers, friendly fire|Presets from the official arena playlist|Saves as a Mode file
FF_SCR_CHALLENGE|Challenge setup|All|Waves table, enemy picker (stock ACT_ only), level band, modifiers, timers, scoring, medals|Wave timeline at the bottom|Medals: Bronze, Silver, Gold times or scores
FF_SCR_TEST|Test play|All|Play with bots; toggle budget, nav mesh, spawn and sightline overlays|One button back to the editor|Bots use stock AI profiles
FF_SCR_PUB_META|Publish: details|All|Title, description, tags, mode, player count, thumbnail capture (in-engine only), credits|Text runs through the chat filter|Title 40 chars, description 500
FF_SCR_PUB_RATING|Publish: content questionnaire|All|Creator declares violence level, horror, language, and whether it uses other creators' work|Answers set the Hub age gate|Lying is a strike
FF_SCR_PUB_CHECK|Publish: checks|All|Automated checks run with progress and results|Must pass all blocking checks|Shows the review queue estimate
FF_SCR_HUB_HOME|Forge Hub home|All|Featured (monthly, plan 9.3), Trending, New, Top rated, Studio picks, categories|Rows of tiles|Filter by platform-compatible only (default on)
FF_SCR_HUB_DETAIL|Hub item page|All|Screenshots, description, creator, version, size, rating, compatible platforms, mods it needs, report button|Download, Play now, Add to playlist|Up and down vote plus 1 to 5 star
FF_SCR_HUB_MODS|Mod manager|PC|Installed mods, load order drag list, enable toggles, conflicts badge, mod-set hash|Sort by load order|Auto-sort by dependencies
FF_SCR_MY|My creations|All|Published items with status (in review, live, rejected, removed), plays, rating, reports|Version history|Update, unpublish
FF_SCR_PROFILE|Creator profile|All|Creator name, bio, published items, followers, strikes standing|Visible to all|Bio uses chat filter
FF_SCR_MOD_STATUS|Moderation status|All|Reason codes for any rejection or removal, with the rule link and Appeal button|One appeal per decision|Appeal answered within 7 days
FF_SCR_TUTORIAL|Tutorials|All|Ten guided lessons: move camera, place, snap, layers, Loom basics, spawns, power weapons, waves, test, publish|Each lesson unlocks a starter template|Rewards a creator emblem on completion
FF_SCR_SETTINGS|Editor settings|All|Grid size, snap angles, camera speed, autosave interval, invert axes, colourblind wire palette|Per user|Autosave every 5 min, 10 versions
''')
w('ux_screens.csv', ['screen_id', 'name', 'platforms', 'purpose', 'layout', 'interaction'], SCREENS)

# ------------------------------------------------------------------ controls
CTRL = split('''
Move camera|WASD + right mouse|Left stick
Look|Mouse with right button held|Right stick
Up and down|E and Q|RB and LB
Camera speed|Mouse wheel while flying|D-pad up and down
Select|Left click|A
Multi-select|Shift + click, or drag box|Hold A and sweep
Grab and move|W gizmo, or drag|A on selection then left stick
Rotate|E gizmo, 15 deg snap|RT + right stick
Scale|R gizmo|LT + right stick
Toggle grid snap|G|D-pad left
Toggle surface snap|Shift+G|D-pad right
Duplicate|Ctrl+D|X
Delete|Delete|Y twice
Undo|Ctrl+Z|View button + LB
Redo|Ctrl+Y|View button + RB
Palette|Tab|Hold Y for radial
Outliner|O|Menu, then Outliner tab
Properties|P|Menu, then Properties tab
Focus on selection|F|Click right stick
Group|Ctrl+G|Menu, then Group
Lock|L|Menu, then Lock
Test play|F5|View button hold 1 s
Back to editor from test|F5|View button hold 1 s
Save|Ctrl+S|Autosave; Menu then Save
''')
w('controls.csv', ['action', 'keyboard_mouse', 'controller'], CTRL)

# ------------------------------------------------------------------ budgets
BUD = split('''
Placed objects (static)|6000|4000|4000|2500|Count; Series S sets the cross-platform cap
Dynamic objects (physics)|300|200|200|120|Count
Dynamic lights|32|24|24|12|Count; shadows on 8 of them (4 on Series S)
AI actors alive|40|32|32|20|Count, challenge rooms only
Spawn points|64|64|64|64|Count
Loom nodes per map|5000|5000|5000|5000|Count
Script instructions per tick|60000|40000|40000|25000|Luau VM budget; overruns throttle then error
Script memory|64|32|32|24|MB
Map footprint|768|512|512|512|Metres per side
Memory for placed content|1024|640|640|400|MB of streamed prefab memory
Frame time in Test Play bot run|16.6|16.6|16.6|16.6|ms at the 95th percentile, Performance mode
Players|6|6|6|6|3v3 PvP (6 players); challenge rooms 3
Mod package size|4096|-|-|-|MB, PC only
Custom textures per mod|2000|-|-|-|Count, PC only, max 4096 px
''')
w('budgets.csv', ['budget', 'pc', 'ps5', 'xbox_series_x', 'xbox_series_s', 'unit_notes'], BUD)

# ------------------------------------------------------------------ palette
PAL = split('''
FF_PAL_STRUCT|Structures|Walls, floors, ramps, stairs, pillars, arches, bridges in each region kit|600|All regions' modular kits from design/art naming
FF_PAL_TERRAIN|Terrain plates|Base plates: flat, hills, canyon, island, ring section; sculpt brush on PC|24|Sculpt is PC only; consoles pick plates
FF_PAL_NATURE|Nature|Trees, rocks, foliage, glass shards, ice, ash, per region|400|Foliage counts as instanced, 1/10 cost
FF_PAL_PROPS|Props|Crates, barricades, lamps, wreckage, banners|500|
FF_PAL_LIGHT|Lights|Point, spot, area, sky preset, fog volume, post volume|20|Post volumes limited to presets from design/art post_process_volumes
FF_PAL_GAME|Gameplay|Spawn points, team zones, capture zones, flags, power weapon pads, ammo crates, kill volumes, soft kill, teleporters, jump pads|60|
FF_PAL_WEAPON|Weapon pads|Every arena power weapon and standard weapon on a timer|40|From items/arena_power_weapons.csv
FF_PAL_ENEMY|Enemy spawners|Stock enemies and creatures by region and role, level band set per room|300|Challenge rooms only; no bosses except Field bosses
FF_PAL_TRAP|Traps and hazards|Fire jets, falling blocks, Hollow pools, frost vents, pendulums|30|
FF_PAL_LOGIC|Logic objects|Triggers, timers, counters, buttons, doors, movers, rotators, HUD message, scoreboard, waypoint|40|Each has Loom events
FF_PAL_AUDIO|Audio|Ambience zones and music states from the region beds|50|No custom audio on consoles
FF_PAL_FX|Effects|Stock VFX emitters|80|Flash-safe set only
''')
w('palette.csv', ['category_id', 'name', 'contents', 'approx_prefabs', 'notes'], PAL)

# ------------------------------------------------------------------ scripting API
# namespace | function | params | returns | where it runs | cost | available in | description
API = split('''
Game|GetTime|-|number|Server|1|All|Seconds since round start
Game|GetMode|-|ModeId|Server|1|All|Current mode
Game|GetRound|-|int|Server|1|Map, Mode|Round number
Game|EndRound|winner: Team?|-|Server|10|Map, Mode|End the round with an optional winner
Game|EndMatch|winner: Team?|-|Server|10|Map, Mode, Room|End the match
Game|SetScoreLimit|n: int|-|Server|2|Mode|Score to win
Game|SetTimeLimit|seconds: number|-|Server|2|Mode, Room|Time limit
Game|GetDifficulty|-|string|Server|1|Room|Room level band and modifiers
Players|All|-|list<Player>|Server|5|All|Every player in the session
Players|OnTeam|team: Team|list<Player>|Server|5|Map, Mode|Players on a team
Player|GetName|p: Player|string|Both|1|All|Display name (filtered)
Player|GetTeam|p: Player|Team|Both|1|All|Team
Player|SetTeam|p: Player, team: Team|-|Server|5|Mode|Move a player to a team
Player|GetHealth|p: Player|number|Both|1|All|Current health
Player|Damage|p: Player, amount: number, type: DamageType|-|Server|5|All|Deal damage of a stock type (ITM_DMG_)
Player|Heal|p: Player, amount: number|-|Server|5|All|Restore health
Player|Kill|p: Player|-|Server|5|All|Kill instantly
Player|Respawn|p: Player, at: SpawnPoint?|-|Server|10|Map, Mode, Room|Respawn now
Player|SetRespawnTime|p: Player, seconds: number|-|Server|2|Mode|Respawn delay
Player|Teleport|p: Player, to: Vector or Object|-|Server|10|All|Move a player
Player|GiveWeapon|p: Player, weapon: ItemId|-|Server|10|Map, Mode, Room|Give a stock weapon (no Shardborn in PvP)
Player|ClearInventory|p: Player|-|Server|10|Mode, Room|Strip the loadout for this session only
Player|SetLoadout|p: Player, loadout: LoadoutId|-|Server|10|Mode|Apply a mode loadout
Player|SetSpeedMultiplier|p: Player, m: number|-|Server|2|All|0.5 to 1.5
Player|SetGravityMultiplier|p: Player, m: number|-|Server|2|All|0.25 to 2.0
Player|AddScore|p: Player, n: int|-|Server|2|All|Add score
Player|GetScore|p: Player|int|Both|1|All|Score
Player|ApplyStatus|p: Player, status: StatusId, seconds: number|-|Server|5|All|Stock status effects (STS_)
Player|IsAlive|p: Player|bool|Both|1|All|Alive check
Player|GetPosition|p: Player|Vector|Both|1|All|World position
Player|GetLookDirection|p: Player|Vector|Both|1|All|Aim direction
Player|SetWaypoint|p: Player, target: Object or Vector, label: string|-|Server|5|All|Personal waypoint
Object|Find|tag: string|list<Object>|Server|5|All|Objects with a script tag
Object|Spawn|prefab: PrefabId, at: Vector, rot: Rotator|Object|Server|20|All|Spawn a palette prefab (counts toward budgets)
Object|Destroy|o: Object|-|Server|10|All|Remove an object
Object|SetVisible|o: Object, on: bool|-|Server|2|All|Show or hide
Object|SetCollision|o: Object, on: bool|-|Server|2|All|Collision on or off
Object|MoveTo|o: Object, to: Vector, seconds: number, ease: Ease|-|Server|5|All|Animated move
Object|RotateTo|o: Object, rot: Rotator, seconds: number, ease: Ease|-|Server|5|All|Animated rotate
Object|GetPosition|o: Object|Vector|Both|1|All|Position
Object|SetColor|o: Object, slot: int, colour: PaletteColor|-|Server|2|All|Colour from the map palette
Object|SetTeam|o: Object, team: Team|-|Server|2|Map, Mode|Team ownership
Object|AddTag|o: Object, tag: string|-|Server|1|All|Script tag
Zone|IsInside|z: Zone, p: Player|bool|Server|2|All|Point test
Zone|PlayersInside|z: Zone|list<Player>|Server|5|All|Occupants
Zone|SetCaptureTeam|z: Zone, team: Team|-|Server|2|Map, Mode|Capture owner
Enemy|Spawn|actor: ActorId, at: SpawnPoint, level: int|Enemy|Server|25|Room|Spawn a stock enemy (ACT_), level clamped to the room band
Enemy|SpawnWave|wave: WaveId|list<Enemy>|Server|50|Room|Spawn a wave from the Challenge setup
Enemy|SetTarget|e: Enemy, p: Player|-|Server|5|Room|Force aggro
Enemy|SetAIProfile|e: Enemy, profile: AIProfileId|-|Server|5|Room|Stock AI profile (AIP_)
Enemy|Count|-|int|Server|1|Room|Enemies alive
Enemy|KillAll|-|-|Server|20|Room|Clear the room
Weapon|SetPadTimer|pad: WeaponPad, seconds: number|-|Server|2|Map, Mode|Power weapon respawn timer
Weapon|SetPadWeapon|pad: WeaponPad, weapon: ItemId|-|Server|2|Map, Mode|Weapon on a pad
Timer|Start|t: Timer, seconds: number|-|Server|2|All|Start a timer object
Timer|Stop|t: Timer|-|Server|2|All|Stop
Timer|After|seconds: number, fn: function|Handle|Server|5|All|Run once later
Timer|Every|seconds: number, fn: function|Handle|Server|5|All|Repeat (min 0.1 s)
Timer|Cancel|h: Handle|-|Server|1|All|Cancel a scheduled call
Var|SetGlobal|name: string, value: any|-|Server|2|All|Session variable (max 256)
Var|GetGlobal|name: string|any|Server|1|All|Read session variable
Var|SetPlayer|p: Player, name: string, value: any|-|Server|2|All|Per-player variable
Var|GetPlayer|p: Player, name: string|any|Server|1|All|Read per-player variable
UI|Message|p: Player or All, text: LocString, seconds: number|-|Server|5|All|Centre-screen message (filtered text or STR_ id)
UI|Banner|p: Player or All, title: LocString, sub: LocString|-|Server|5|All|Uses the stock banner popup style
UI|SetObjective|p: Player or All, text: LocString|-|Server|5|All|Objective line under the compass
UI|ShowScoreboard|on: bool|-|Server|2|All|Scoreboard
UI|SetTimerDisplay|seconds: number|-|Server|2|All|Top-centre timer
UI|SetMedal|p: Player, medal: Medal|-|Server|5|Room|Bronze, Silver or Gold result
Audio|PlayStinger|s: StingerId, p: Player or All|-|Server|2|All|Stock music stinger
Audio|PlaySound|s: SoundId, at: Vector|-|Server|2|All|Stock SFX_ hook
Audio|SetMusicState|state: MusicStateId|-|Server|2|All|Stock region music state
FX|Play|fx: VfxId, at: Vector|-|Server|2|All|Stock VFX_ (flash-safe list)
Math|Random|min: number, max: number|number|Both|1|All|Seeded per session for replays
Math|Distance|a: Vector, b: Vector|number|Both|1|All|Distance
Math|Lerp|a, b, t|number|Both|1|All|Interpolate
Debug|Log|text: string|-|Both|1|All|Test Play log only; stripped on publish
Record|Get|id: RecordId|Record|Both|2|Mod|Read any record (mods only)
Record|GetField|id: RecordId, field: string|any|Both|1|Mod|Read one field
Record|Override|id: RecordId, field: string, value: any|-|Load time|5|Mod|Override a field at load time (record_access.csv rules apply)
Record|Create|parent: RecordId, newId: RecordId|Record|Load time|10|Mod|New record inheriting from a parent
Quest|Start|q: QuestId|-|Server|10|Mod|Start a quest (mod quests use QST_MOD_ prefix)
Quest|SetStage|q: QuestId, stage: int|-|Server|5|Mod|Advance a quest
Quest|GetStage|q: QuestId|int|Both|1|Mod|Read stage
Quest|SetFlag|flag: FlagId, value: bool|-|Server|2|Mod|Set a mod flag (FLG_MOD_ only; base story flags are read-only)
Quest|GetFlag|flag: FlagId|bool|Both|1|Mod|Read any flag
Actor|SpawnNPC|actor: ActorId, at: Vector|Actor|Server|25|Mod|Spawn a stock or mod NPC
Actor|StartDialogue|a: Actor, d: DialogueId|-|Server|10|Mod|Mod dialogue trees (text plus optional PC voice files)
Inventory|AddItem|p: Player, item: ItemId, n: int|-|Server|10|Mod|Give items in a Forged (modded) character only
Inventory|RemoveItem|p: Player, item: ItemId, n: int|-|Server|10|Mod|Take items
''')
api_rows = [[f'FFAPI_{a[0].upper()}_{a[1].upper()}'] + a for a in API]
w('script_api.csv', ['api_id', 'namespace', 'function', 'params', 'returns', 'runs_on', 'cost_units', 'available_in', 'description'], api_rows)

EVENTS = split('''
OnRoundStart|-|All|Round begins
OnRoundEnd|winner|All|Round ends
OnMatchEnd|winner|All|Match ends
OnPlayerJoin|player|All|Player joins
OnPlayerLeave|player|All|Player leaves
OnPlayerSpawn|player|All|Player spawns
OnPlayerKilled|victim, killer, weapon|All|Player dies
OnPlayerDamaged|victim, source, amount, type|All|Player takes damage
OnZoneEnter|zone, player|All|Player enters a zone
OnZoneExit|zone, player|All|Player leaves a zone
OnZoneCaptured|zone, team|Map, Mode|Zone captured
OnInteract|object, player|All|Player uses an object
OnTimerDone|timer|All|Timer object finishes
OnWeaponPickup|pad, player|Map, Mode|Weapon taken from a pad
OnEnemyKilled|enemy, player|Room|Enemy dies
OnWaveCleared|wave|Room|Wave cleared
OnObjectDestroyed|object, source|All|Destructible destroyed
OnVariableChanged|name, value|All|A watched variable changes
OnTick|dt|All|Every 0.1 s (not every frame) to protect the budget
OnLoad|-|Mod|Mod load, where record overrides are applied
OnQuestStage|quest, stage|Mod|Quest stage reached
OnDialogueChoice|actor, choice|Mod|Player picks a dialogue choice
''')
w('script_events.csv', ['event', 'args', 'available_in', 'fires_when'], EVENTS)

LANGR = split('''
LANG|Forgescript is sandboxed Luau (open source, MIT licence, gradual types). Loom graphs compile to the same bytecode, so any graph can be shown as text on PC
SANDBOX|No file, network, OS, debug, or reflection libraries. No loadstring. No access to engine objects except through the API handles
AUTH|Gameplay scripts run on the server (dedicated) or host (listen). Clients run only UI and cosmetic calls marked Both
BUDGET|Instruction budget per tick from budgets.csv. 2 overruns in 10 s throttle the script to half rate; 5 errors stop it and show the debugger
DETERMINISM|Math.Random is seeded per session so Theater replays match
VERSION|Each publish pins an API version. Old versions keep working for 2 major game updates; the editor offers an upgrade tool
STRINGS|Player-visible text is either an STR_ id or creator text run through the chat filter at publish and at runtime
NO_ECONOMY|No API can grant Ember, Seals, XP or items to a normal character. Inventory calls work only on Forged (modded) characters
''')
w('script_rules.csv', ['rule_id', 'rule'], LANGR)

# ------------------------------------------------------------------ record access (mod override rules per data table)
LOCK = {'cosmetics': 'Locked: paid cosmetics (real-money prices)', 'currencies': 'Locked: online economy', 'economy_currencies': 'Locked: online economy',
        'economy_formulas': 'Override in Forged characters only', 'asset_hooks': 'Read only: generated by link.py', 'strings_data': 'Override allowed (translation and rename mods)',
        'strings': 'Override allowed (translation and rename mods)', 'popups': 'Override text only; layout locked', 'arena_power_weapons': 'Locked for ranked; custom games may override',
        'matchmaking': 'Locked', 'coop_scaling': 'Override in Forged characters only'}
recs = []
for p in sorted(glob.glob(os.path.join(DATA, '*', '*.csv'))):
    folder = os.path.basename(os.path.dirname(p)); t = os.path.splitext(os.path.basename(p))[0]
    try: cols = next(csv.reader(open(p)))
    except StopIteration: continue
    rule = LOCK.get(t, 'Override and add rows in Forged characters only')
    recs.append([f'{folder}/{t}.csv', cols[0], len(cols), rule,
                 'No' if rule.startswith('Locked') or rule.startswith('Read only') else 'Yes',
                 'Yes' if t in ('strings', 'strings_data', 'popups') else 'No',
                 'Key column and parent cannot change; new rows need the MOD_<author>_ id prefix'])
w('record_access.csv', ['table', 'key', 'columns', 'mod_rule', 'mods_can_change', 'allowed_on_unmodded_characters', 'id_rule'], recs)

# ------------------------------------------------------------------ curation
CUR = split('''
CUR_A01|Automated|Validation|Record and script validation (same rules as data/tools/validate.py, plus API version)|Blocking|All
CUR_A02|Automated|Budget|Every budget in budgets.csv within the lowest target platform|Blocking|Maps, rooms, modes
CUR_A03|Automated|Performance|Bot run: 8 bots (or room max) play 5 min on min-spec PC and Series S; 95th percentile frame time under 16.6 ms in Performance mode|Blocking|Maps, rooms
CUR_A04|Automated|Reachability|Nav check: every spawn reaches every objective; no spawn inside geometry; no unescapable pits without a kill volume|Blocking|Maps, rooms
CUR_A05|Automated|Text filter|Title, description, tags, in-map text through the chat filter in all 12 languages|Blocking|All
CUR_A06|Automated|Image moderation|Thumbnails and custom textures through image moderation (nudity, gore, hate symbols, real people)|Blocking|All
CUR_A07|Automated|Package scan|PC mods: file types allowed list, no executables, DLLs, shaders, or scripts outside Luau; malware scan|Blocking|Mods
CUR_A08|Automated|IP match|Hash and perceptual match against known commercial asset libraries and other Hub items (reuploads)|Blocking|All
CUR_A09|Automated|Exploit|Challenge rooms: detect AFK or loop farming patterns; rooms grant no loot or XP anyway|Warning|Rooms
CUR_A10|Automated|Flash safety|Photosensitivity analysis of a 60 s capture (Harding-style test)|Blocking|All
CUR_H01|Human|Content rating|Reviewer checks the creator's questionnaire against the content|Blocking|Mods; maps flagged by A06 or reports
CUR_H02|Human|Quality bar for featuring|Two reviewers score fun, readability, performance, originality 1 to 5; 16+ is eligible for Featured|Featuring only|All
CUR_H03|Human|Report review|Any item with 5 reports per 1,000 plays, or one report of illegal content, goes to the queue|Blocking (item hidden while reviewed)|All
CUR_H04|Human|Appeal|A different reviewer re-checks; one appeal per decision|-|All
CUR_P01|Policy|Queue targets|Automated checks under 30 min. Human review for mods within 72 h at launch, 24 h by month 6. Featured picks monthly (plan 9.3)|-|All
CUR_P02|Policy|Strikes|Strike 1: warning. Strike 2: 30-day publish ban. Strike 3: permanent publish ban. Strikes expire after 12 months. Illegal content is an instant ban and report to authorities|-|All
CUR_P03|Policy|Takedowns|DMCA and equivalent takedowns honoured within 48 h; counter-notice flow in the Hub|-|All
CUR_P04|Policy|No paid mods|Hub items are free. No paid mods at launch; a creator programme can be considered in year 2 after legal review|-|All
CUR_P05|Policy|Studio content rule|Creators may not use real people, real brands, or other games' IP. Shardfall IP use is allowed under the Forge licence in the EULA|-|All
CUR_P06|Policy|Age|Publishing needs a platform account age 13+ (16+ in the EU where local law sets it) and accepted Forge terms|-|All
''')
w('curation_rules.csv', ['rule_id', 'stage', 'check', 'detail', 'result', 'applies_to'], CUR)

REJ = split('''
REJ_VALID|Fails validation|Fix the listed errors and publish again
REJ_BUDGET|Over budget on a target platform|Reduce content or untick that platform
REJ_PERF|Fails the performance run|Lower dynamic lights, physics objects or AI
REJ_TEXT|Text breaks the content rules|Edit the text
REJ_IMAGE|Image breaks the content rules|Recapture the thumbnail or remove the texture
REJ_FILES|Package has files that are not allowed|Remove them
REJ_IP|Matches someone else's work|Prove ownership by appeal or remove it
REJ_RATING|Content does not match the questionnaire|Update the answers
REJ_FLASH|Fails the photosensitivity check|Reduce flashing effects
REJ_ILLEGAL|Illegal content|No appeal; account action
''')
w('rejection_reasons.csv', ['reason_id', 'player_text_summary', 'creator_fix'], REJ)

CON = split('''
Imported meshes|Allowed (cooked by Forgeframe, max 200k tris per mesh, 4 LODs auto)|Not allowed|Consoles only use the prefab palette
Imported textures|Allowed (PNG, TGA, DDS up to 4096 px)|Not allowed|-
Materials|Instances of the shipped master materials only (design/art/master_materials.csv)|Prefab palette colour slots only|No custom shaders anywhere
Audio|WAV and OGG, 48 kHz, max 10 min per file, loudness -23 LUFS checked|Stock SFX and music states only|-
Voice|Allowed for mod dialogue, filtered by the audio content check|Not allowed|-
Scripts|Forgescript (text) and Loom graphs|Loom graphs only|Same bytecode; consoles cannot edit text, but can run published text scripts in maps
Record overrides|Allowed in Forged characters|Not allowed|Consoles get maps, rooms and modes only (plan 3.12: mods on PC, shared maps on all)
Thumbnails|In-engine capture or upload (moderated)|In-engine capture only|-
Download size|Up to 4 GB per mod|Up to 50 MB per map, room or mode|Map data is placements and graphs, not assets
Cross-play|PC maps marked cross-platform must pass the Series S budget and use no PC-only assets|Same|Badge on the Hub tile
''')
w('console_asset_rules.csv', ['asset_type', 'pc', 'consoles', 'notes'], CON)

HUB = split('''
Categories|PvP maps, Challenge rooms, Modes, Mods (PC), Prefab sets (PC), Translations (PC)
Sorting|Featured, Trending (plays in 7 days, weighted by rating), New, Top rated (Wilson score on votes), Most played
Featured|Studio picks monthly (plan 9.3): 3 maps, 3 rooms, 2 modes, 2 PC mods. Featured maps can enter an official rotating arena playlist for 2 weeks
Ratings|Up and down vote after 5 minutes of play; star rating 1 to 5 shown as average with count
Rewards|Players: no loot, XP or Seals from Hub content on normal characters. Room medals give Hub emblems only. Creators: creator emblems and a profile badge at 1k, 10k and 100k plays
Mod sets|A mod set is a load order hash. Co-op with mods only when every player has the same hash; loot stays on Forged characters
Forged characters|Any character that loads record-changing mods becomes Forged. It cannot enter matchmade strikes, raids, arena or invasions, and cannot be converted back. Cosmetic and translation mods do not set Forged
Anti-cheat|Easy Anti-Cheat stays on for online modes; mods run only on Forged characters, solo or same-hash co-op (tech 02)
Updates|Creator can update a published item; each update goes through checks again; players get the new version on next launch; old versions kept 30 days
Report reasons|Offensive content, Sexual content, Hate, Real person, Stolen work, Broken or exploit, Malicious file, Spam, Other
Release|PC 3 months after launch, consoles 6 months after (plan 9.3)
''')
w('hub_rules.csv', ['topic', 'rule'], HUB)

# ------------------------------------------------------------------ strings and popups
strs = []
def S(i, screen, text, notes=''): strs.append([i, screen, text, max(4, int(len(text) * 1.4 + .999)), '', notes])
for m in MODES: S(f'STR_{m[0]}', 'Forgeframe', m[1]); S(f'STR_{m[0]}_DESC', 'Forgeframe', m[2])
for s in SCREENS: S(f'STR_{s[0]}', 'Forgeframe', s[1])
for p in PAL: S(f'STR_{p[0]}', 'Forgeframe', p[1])
for c in CTRL: S('STR_FF_ACT_' + c[0].upper().replace(' ', '_').replace('-', '_').replace(',', ''), 'Forgeframe', c[0])
for r in REJ: S(f'STR_FF_{r[0]}', 'Forgeframe', r[1]); S(f'STR_FF_{r[0]}_FIX', 'Forgeframe', r[2])
for b in BUD: S('STR_FF_BUD_' + ''.join(ch if ch.isalnum() else '_' for ch in b[0].upper()).strip('_').replace('__', '_'), 'Forgeframe', b[0])
POP = split('''
CNF_FF_PUBLISH|confirm|Publish to the Forge Hub?|Your work will be checked and reviewed. You can unpublish it at any time.|Publish;Cancel
CNF_FF_DELETE|confirm|Delete this project?|This can't be undone. Published copies stay on the Hub until you unpublish them.|Delete;Cancel
CNF_FF_FORGED|confirm|Make this character Forged?|Mods that change game data will mark this character as Forged. Forged characters can't join matchmade strikes, raids, arena or invasions. This can't be undone.|Make Forged;Cancel
CNF_FF_UNSAVED|confirm|Leave without saving?|You have unsaved changes.|Save;Leave;Cancel
ERR_FF_BUDGET|error|Over budget|{VAR_n} budgets are over the limit for {VAR_platform}. Open the budget meter to see which.|Open meter;OK
ERR_FF_VALIDATE|error|Can't publish yet|{VAR_n} errors need fixing first.|Show errors;OK
ERR_FF_SCRIPT|error|Script stopped|A script hit too many errors and was stopped. Open the debugger to see why.|Open debugger;OK
ERR_FF_MODSET|error|Mods don't match|Everyone in a modded co-op session needs the same mods in the same order.|Show differences;OK
ERR_FF_OFFLINE|error|Forge Hub unavailable|Can't reach the Forge Hub. Local projects still work.|OK
NTF_FF_LIVE|toast|Your creation is live|{VAR_name} passed review and is on the Forge Hub.|
NTF_FF_REJECTED|toast|Changes needed|{VAR_name} wasn't approved. See Moderation status for why.|
NTF_FF_FEATURED|toast|You've been featured|{VAR_name} is a Studio pick this month.|
NTF_FF_AUTOSAVE|toast|Autosaved||
NTF_FF_MILESTONE|toast|{VAR_n} plays|{VAR_name} reached {VAR_n} plays.|
''')
pops = []
for i, kind, title, body, buttons in POP:
    S(f'STR_{i}_T', 'Forgeframe', title, 'Popup title'); body and S(f'STR_{i}_B', 'Forgeframe', body, 'Popup body')
    pops.append([i, kind, 'Forgeframe', 'Modal centre' if kind != 'toast' else 'Toast top right', '', f'STR_{i}_T', f'STR_{i}_B' if body else '',
                 buttons, '' if kind != 'toast' else '4.0', 'Button' if kind != 'toast' else 'Auto', 2 if kind == 'error' else 3, 'One modal at a time', 'SFX_UI_CONFIRM' if kind == 'confirm' else 'SFX_UI_ERROR' if kind == 'error' else 'SFX_UI_TOAST'])
w('strings_forgeframe.csv', ['str_id', 'screen', 'text_en', 'max_chars', 'tokens', 'notes'], strs)
w('popups_forgeframe.csv', ['popup_id', 'kind', 'screen', 'layer', 'trigger', 'title_str', 'body_str', 'buttons', 'duration_s', 'dismiss', 'priority', 'queue_rule', 'sfx_hook'], pops)

req = [['STR_FF_*', 'new strings', 'ui/strings.csv', f'Merge strings_forgeframe.csv ({len(strs)} rows)'],
       ['CNF_FF_* ERR_FF_* NTF_FF_*', 'new popups', 'ui/popups.csv', f'Merge popups_forgeframe.csv ({len(pops)} rows); runtime tokens {{VAR_n}} {{VAR_name}} {{VAR_platform}}'],
       ['UI_FF_*', 'new assets', 'assets/asset_hooks.csv', f'One UI hook per screen in ux_screens.csv ({len(SCREENS)}) and per palette category ({len(PAL)})'],
       ['ICON_FF_EMBLEM_*', 'new cosmetics', 'items/cosmetics.csv', 'Creator emblems (tutorial, 1k, 10k, 100k plays) and room medal emblems, price_usd 0, source Forge Hub'],
       ['FLG_MOD_*, QST_MOD_*, MOD_<author>_*', 'new id prefixes', 'data/README.md', 'Reserve prefixes for mod content so validate.py can tell mod rows from base rows'],
       ['Forged character flag', 'save field', 'design/tech (save system)', 'Per-character Forged bool and mod-set hash in the save header; tech thread owns the save format'],
       ['Chat filter and image moderation', 'service', 'design/tech/02-online.md', 'Forge Hub needs the same text filter plus an image moderation service and a review queue tool']]
w('data-requests.csv', ['id', 'request', 'target_table', 'notes'], req)
print(f'{len(MODES)} modes, {len(SCREENS)} screens, {len(api_rows)} API calls, {len(EVENTS)} events, {len(recs)} tables mapped, {len(CUR)} curation rules, {len(strs)} strings, {len(pops)} popups')
