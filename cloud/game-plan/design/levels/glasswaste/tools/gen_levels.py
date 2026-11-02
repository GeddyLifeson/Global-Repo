"""Glasswaste (REG_04) level design generator.

Reads the world thread's placement tables (design/world/), data/ and the asset
sheet, and writes room-by-room level design for every Glasswaste level into
design/levels/glasswaste/. Never hand-edit the CSVs it writes; change this file.

Every value not taken from the master plan or another table is a Shardfall
design choice made 3 Oct 2026 (marked in README.md). Set REGION to reuse it.
"""
import csv, math, os, re, random
from collections import defaultdict, Counter

REGION = "REG_04"
RNAME = "Glasswaste"
RCODE = "GLS"          # audio code used by design/audio
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))  # game-plan/
W = os.path.join(ROOT, "design", "world")
D = os.path.join(ROOT, "data")
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
random.seed(404)


def rd(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def wr(name, rows, cols=None):
    if not rows:
        return
    cols = cols or list(rows[0].keys())
    p = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


# ---------------------------------------------------------------- inputs
locs = [r for r in rd(os.path.join(W, "locations.csv")) if r["region"] == REGION]
L = {r["loc_id"]: r for r in locs}
sites = {r["loc_id"]: r for r in rd(os.path.join(W, "sites.csv")) if r["region"] == REGION}
zones = [r for r in rd(os.path.join(W, "citadel_zones.csv")) if r["loc_id"].startswith(f"LOC_CIT_{REGION}")]
encs = [r for r in rd(os.path.join(W, "encounters.csv")) if r["region"] == REGION]
ENC_BY_LOC = defaultdict(list)
for e in encs:
    ENC_BY_LOC[e["loc_id"]].append(e)
secrets = [r for r in rd(os.path.join(W, "secrets.csv")) if r["region"] == REGION]
SEC_BY_HOST = defaultdict(list)
for s in secrets:
    SEC_BY_HOST[s["host_loc"]].append(s)
anchors = [r for r in rd(os.path.join(W, "anchors.csv")) if r["region"] == REGION]
ANC_BY_PARENT = defaultdict(list)
for a in anchors:
    ANC_BY_PARENT[a["parent_loc"]].append(a["loc_id"])
arenas = {r["loc_id"]: r for r in rd(os.path.join(W, "boss_arenas.csv")) if r["region"] == REGION}
landmarks = {r["loc_id"]: r for r in rd(os.path.join(W, "landmarks.csv")) if r["region"] == REGION}
layout = next(r for r in rd(os.path.join(W, "regions_layout.csv")) if r["reg_id"] == REGION)
npcs = rd(os.path.join(W, "npc_placement.csv"))
lore = [r for r in rd(os.path.join(D, "items", "lore_items.csv")) if r["region"] == REGION]
LORE_BY_SITE = defaultdict(list)
for r in lore:
    LORE_BY_SITE[r["location"]].append(r)
templates = {r["template"]: r for r in rd(os.path.join(W, "encounter_templates.csv"))}

# asset sheet ids (VFX V####, SFX S####), looked up by text so ids stay in sync
VFX, SFX = {}, {}
try:
    import openpyxl
    wb = openpyxl.load_workbook(os.path.join(ROOT, "shardfall-assets.xlsx"), read_only=True)
    for sheet, store in (("VFX", VFX), ("SFX", SFX)):
        for r in list(wb[sheet].iter_rows(values_only=True))[1:]:
            if r[0]:
                store[f"{r[2]}|{r[3]}"] = r[0]
except Exception as ex:  # sheet missing or openpyxl absent: cues fall back to names
    print("asset sheet not read:", ex)


def vfx(key, default=""):
    for k, v in VFX.items():
        if key.lower() in k.lower():
            return v
    return default


def sfx(key, default=""):
    for k, v in SFX.items():
        if key.lower() in k.lower():
            return v
    return default


C = {  # shared cue ids
    "anchor_v": vfx("Kindled|Anchor first light"), "anchor_s": sfx("Kindled|Anchor light"),
    "short_v": vfx("Environment|Shortcut unlock"), "short_s": sfx("Environment|Shortcut unlock"),
    "chest_v": vfx("Environment|Chest open"), "chest_s": sfx("Environment|Chest open"),
    "lift_v": vfx("Environment|Elevator"), "lift_s": sfx("Environment|Lift"),
    "lever_v": vfx("Environment|Lever"), "lever_s": sfx("Environment|Lever"),
    "wall_v": vfx("Environment|Breakable wall"), "wall_s": sfx("Environment|Illusory wall"),
    "brk_s": sfx("Environment|Breakable wall"),
    "lore_v": vfx("Environment|Lore item shimmer"), "lore_s": sfx("Environment|Lore item pickup"),
    "door_v": vfx("Environment|Door open"), "hatch_s": sfx("Environment|Ship hatch"),
    "doorm_s": sfx("Environment|Door open/close metal"),
    "relay_v": vfx("Environment|Relay Tower activation"), "relay_s": sfx("Environment|Relay Tower"),
    "map_v": vfx("Environment|Map reveal"), "shard_v": vfx("Environment|Shard crystal glow"),
    "hum_s": sfx("Environment|Shard hum"), "spark_v": vfx("Environment|Sparking wreckage"),
    "spark_s": sfx("Environment|Sparks"), "holo_v": vfx("Environment|Hologram terminals"),
    "beep_s": sfx("Environment|Terminal beep"), "dust_v": vfx("Environment|Dust motes"),
    "trap_v": vfx("Environment|Trap"), "trap_s": sfx("Environment|Traps"),
    "torch_v": vfx("Environment|Torches"), "fire_s": sfx("Environment|Fire loop"),
    "steam_v": vfx("Environment|Steam vents"), "steam_s": sfx("Environment|Steam vent"),
    "region_v": vfx("R4 Glasswaste|Region signature"), "sand_v": vfx("Sky|Sandstorm"),
    "sand_s": sfx("Sky|Sandstorm"), "loot_relic_v": vfx("Environment|Loot glow Relic"),
    "loot_rare_v": vfx("Environment|Loot glow Rare"), "pickup_s": sfx("Environment|Item pickup"),
    "discover_s": sfx("Interface|Area discovered"), "weave_v": vfx("Environment|Weave threads"),
    "ghost_v": vfx("Kindled|Shard-ghost (dropped"),
}

# ---------------------------------------------------------------- helpers
def ecount(actors):
    return sum(int(m) for m in re.findall(r"x(\d+)", actors))


def dist(a, b):
    return math.hypot(float(a["x_m"]) - float(b["x_m"]), float(a["y_m"]) - float(b["y_m"]))


STORY = {  # campaign names (design/campaign/01-lore-bible.md) for world LOC ids
    "LOC_CIT_REG_04": "The Grafted Foundry", "LOC_DGN_REG_04_03": "Mirror Hall",
    "LOC_DGN_REG_04_10": "The Last Hangar",
}

KIT_LIGHT = {  # interior light preset per kit (design choice, requested from art)
    "KIT_TOWER": "LGT_LVL_04_TOWER", "KIT_WRECK": "LGT_LVL_04_WRECK", "KIT_LAB": "LGT_LVL_04_LAB",
    "KIT_FORT": "LGT_LVL_04_FORT", "KIT_CAVE": "LGT_LVL_04_CAVE", "KIT_CATACOMB": "LGT_LVL_04_CATACOMB",
    "KIT_CHOIR_VAULT": "LGT_LVL_04_VAULT", "KIT_CITADEL": "LGT_LVL_04_CITADEL", "KIT_TOWN": "LGT_REG_04_*",
}
KIT_MOOD = {
    "KIT_TOWER": "Sun-split prisms throw moving rainbow bars across the stairs; wind whistles through cracked panes",
    "KIT_WRECK": "Half-buried Meridian hull, sand pouring through breaches in slow falls; red emergency strips flicker",
    "KIT_LAB": "Sterile white panels fused by heat; humming cold-light terminals; Remnant drones still doing rounds",
    "KIT_FORT": "Thorn palisade of fused-glass spikes and salvaged plate; cookfire smoke and drums",
    "KIT_CAVE": "Glass-walled caverns where the dunes melted; the walls hum when wind passes the mouth",
    "KIT_CATACOMB": "Sun-priest ossuary cut into glass bedrock; bone shrines lit by mirror shafts from the surface",
    "KIT_CHOIR_VAULT": "Tuned glass pillars ring as you pass; violet Weave light; no ambient sound except the tones",
    "KIT_CITADEL": "Iron Choir fortress-foundry around a buried Meridian engine; heat haze, forge glow, hymn-machinery",
}
LEX = {  # room name lexicon per kit
    "KIT_TOWER": ["Sand-choked Foyer", "Spiral Stair", "Prism Landing", "Cable Gallery", "Lens Room", "Broken Belfry",
                  "Signal Deck", "Crown Platform", "Mirror Loft", "Upper Ring"],
    "KIT_WRECK": ["Breach Ramp", "Cargo Spine", "Sand-flooded Deck", "Crew Bunks", "Reactor Crawlway", "Bridge Stub",
                  "Hangar Gallery", "Pressure Lock", "Galley", "Coolant Trench", "Bulkhead Hall", "Drone Nest"],
    "KIT_LAB": ["Decon Lobby", "Specimen Hall", "Server Crypt", "Lens Bench Room", "Sealed Ward", "Observation Ring",
                "Cold Store", "Director's Office", "Clean Corridor"],
    "KIT_FORT": ["Spike Gate", "Muster Yard", "Long Barracks", "Archer Walk", "Warchief's Hall", "Store Pit",
                 "Postern Lane", "Drum Tower"],
    "KIT_CAVE": ["Singing Mouth", "Melt Tunnel", "Glass Gallery", "Echo Chamber", "Crawler Den", "Underground Pool",
                 "Lamp Grotto", "Fused Ravine", "Deep Hollow"],
    "KIT_CATACOMB": ["Mirror Stair", "Bone Nave", "Niche Corridor", "Priest Crypt", "Sun Well", "Statue Hall",
                     "Collapsed Aisle", "Reliquary", "Lower Ossuary", "Lever Gauntlet", "Ash Pit"],
    "KIT_CHOIR_VAULT": ["Glass Door", "Tone Hall", "Pillar Court", "Resonant Stair", "Choir Cell", "Heart Chamber"],
}
ROLE_DIM = {  # w x l x h metres (design choice, within design/world/level_metrics.csv)
    "entry": (14, 14, 6), "approach": (6, 26, 5), "combat": (22, 26, 8), "gun": (14, 70, 10),
    "vertical": (12, 12, 22), "side": (8, 12, 4), "lore": (8, 10, 4), "puzzle": (16, 16, 8),
    "rest": (10, 10, 5), "keeper": (24, 24, 10), "boss": (36, 36, 14), "reward": (8, 8, 4),
    "shortcut": (4, 18, 4), "secret": (6, 6, 3), "antechamber": (12, 18, 8),
}

rooms, edges, placements, loot, secrets_out, collect, cues, levels = [], [], [], [], [], [], [], []
_lvl_rooms = defaultdict(list)


def room(lvl, role, name, floor, crit, beat, mood, light, music, amb, trav="", anchor="", notes="", dims=None):
    n = len(_lvl_rooms[lvl]) + 1
    rid = f"RM_{lvl[4:]}_{n:02d}"
    w, l, h = dims or ROLE_DIM.get(role, (12, 12, 5))
    r = dict(room_id=rid, level=lvl, order=n, name=name, role=role, floor=floor, size_m=f"{w}x{l}x{h}",
             critical_path="Y" if crit else "N", beat=beat, encounters="", enemies=0, anchor=anchor,
             traversal=trav, lighting=light, music_state=music, ambience=amb, mood=mood, notes=notes)
    rooms.append(r)
    _lvl_rooms[lvl].append(r)
    return r


def link(a, b, kind, trav="walk", state="open", note=""):
    edges.append(dict(edge_id=f"EDG_{len(edges)+1:05d}", level=a["level"], from_room=a["room_id"],
                      to_room=b["room_id"], kind=kind, traversal=trav, initial_state=state, note=note))


def cue(r, trigger, kind, cid, note=""):
    if cid:
        cues.append(dict(cue_id=f"CUE_{len(cues)+1:05d}", room_id=r["room_id"], level=r["level"],
                         trigger=trigger, kind=kind, asset_id=cid, note=note))


def boss_music(r, boss, hooks):
    b = boss.replace("ACT_BOSS_", ""); n = max(1, len(hooks.split()))
    cue(r, "Fog gate crossed / aggro", "MUSIC", f"MUS_BOSS_{b}_INTRO")
    cue(r, "Fight starts", "MUSIC", f"MUS_BOSS_{b}_P1")
    for i in range(2, n + 1):
        cue(r, f"Phase {i} threshold", "MUSIC", f"MUS_BOSS_{b}_T{i}")
        cue(r, f"Phase {i} loop", "MUSIC", f"MUS_BOSS_{b}_P{i}")
    cue(r, "Boss dies", "MUSIC", f"MUS_BOSS_{b}_WIN")


def place_enc(r, e, trigger, wave=1):
    t = templates.get(e["template"], {})
    n = ecount(e["actors"])
    r["encounters"] = (r["encounters"] + " " + e["enc_id"]).strip()
    r["enemies"] = int(r["enemies"]) + n
    if r["beat"] in ("explore", "rest"):
        r["beat"] = "combat"
    placements.append(dict(enc_id=e["enc_id"], room_id=r["room_id"], level=r["level"], template=e["template"],
                           faction=e["faction"], enemy_level=e["level"], actors=e["actors"], enemy_count=n,
                           trigger=trigger, wave=wave, spawn_points=max(2, math.ceil(n / 2)),
                           cover_points=e["cover_points"], fallback_points=e["fallback_points"],
                           respawn=e["respawn"], alert_link=t.get("use", "")[:60]))
    combat_cues(r)


def combat_cues(r):
    if not any(c["room_id"] == r["room_id"] and c["kind"] == "MUSIC" for c in cues):
        cue(r, "Enemy aware", "MUSIC", f"MUS_{RCODE}_TENSION")
        cue(r, "First hit", "MUSIC", f"MUS_{RCODE}_COMBAT_L1", "Threat drives L2/L3")
        cue(r, "Last enemy dies", "MUSIC", f"MUS_{RCODE}_COMBAT_END")


def add_loot(r, kind, item, qty=1, vis="open", note=""):
    loot.append(dict(loot_id=f"LP_04_{len(loot)+1:04d}", room_id=r["room_id"], level=r["level"], container=kind,
                     item=item, qty=qty, visibility=vis, note=note))
    if kind in ("Chest", "Shard crate", "Pedestal", "Reward chest"):
        cue(r, f"Open {kind.lower()}", "VFX", C["chest_v"]); cue(r, f"Open {kind.lower()}", "SFX", C["chest_s"])


def add_anchor(r, aid):
    r["anchor"] = aid
    r["beat"] = "rest" if r["beat"] == "explore" else r["beat"]
    cue(r, "Anchor first lit", "VFX", C["anchor_v"]); cue(r, "Anchor first lit", "SFX", C["anchor_s"])


def add_secret(lvl, host, s, mech, reward_item):
    sr = room(lvl, "secret", f"Hidden: {s['secret_type']}", host["floor"], False, "secret",
              "Small, lit by a single Shard glint so the reward reads from the doorway", host["lighting"],
              host["music_state"], host["ambience"])
    link(host, sr, "secret", mech, "hidden", s["hint"])
    trig = "Hit or roll into wall" if "Illusory" in s["secret_type"] else "Discover"
    if "Illusory" in s["secret_type"]:
        cue(sr, trig, "VFX", C["wall_v"]); cue(sr, trig, "SFX", C["wall_s"])
    elif "Breakable" in s["secret_type"]:
        cue(sr, "Floor breaks", "SFX", C["brk_s"])
    cue(sr, "Discover", "SFX", C["discover_s"])
    secrets_out.append(dict(secret_id=s["loc_id"], level=lvl, host_room=host["room_id"], secret_room=sr["room_id"],
                            type=s["secret_type"], hint=s["hint"], mechanism=mech,
                            requirement=s["requirement"], reward=s["reward"]))
    add_loot(sr, "Secret cache", reward_item or s["reward"], 1, "secret")
    return sr


SECRET_MECH = {
    "Illusory wall": "Wall section with cracked mortar 1.6 m wide; one hit or roll dissolves it",
    "Hidden ledge path": "0.8 m ledge along the outside, visible only from the far side; drop 4 m to reach",
    "Breakable floor": "Fused-glass floor patch, heavy attack or explosive breaks it; 5 m drop into cellar",
    "Resonance gate": "Glass gate that opens to a Resonance (see requirement)",
    "Night-only event": "Event runs 22:00-04:00 game time only; a ghost procession leads to the cache",
    "Hidden merchant": "Vendor behind a sand-curtain alcove; appears after the site is cleared",
    "Shard-note cache": "Pre-placed Shard-note reads 'Look down, then look back'; cache under the overlook lip",
    "Sunken chest": "Chest buried under drifting sand; interact prompt after 3 s of digging (hold)",
    "Rooftop route": "Climbable cable from a balcony leads over the roof to a skylight drop",
    "Vehicle jump": "Ramp of fused glass; clear the 22 m gap at 26 m/s on a Skimmer, or double jump on a Strider",
    "Echo duel": "Kneel at the grave marker to summon an Echo duelist (level +2); win for the reward",
}


def reward_item(s):
    m = re.match(r"(ITM_[A-Z0-9_]+)", s["reward"])
    if m:
        return m.group(1)
    if "Unique site reward" in s["reward"]:
        return f"ITM_LT_VAULT_{REGION}"
    if "Region loot table" in s["reward"]:
        return f"ITM_LT_SMALLCHEST_{REGION}"
    if "ITM_LT_ARTS" in s["reward"]:
        return "ITM_LT_ARTS"
    if "Lore item" in s["reward"]:
        return "ITM_MAT_DUST_01 x5 + lore item"
    return s["reward"]


def level_row(lvl, kind, name, level, layout_kind, path_min, full_min, notes="", **kw):
    rs = _lvl_rooms[lvl]
    r = dict(level_id=lvl, kind=kind, name=name, story_name=STORY.get(lvl, ""), level=level,
             layout=layout_kind, rooms=len([x for x in rs if x["role"] != "secret"]),
             secret_rooms=len([x for x in rs if x["role"] == "secret"]),
             encounters=sum(len(x["encounters"].split()) for x in rs),
             enemies=sum(int(x["enemies"]) for x in rs),
             anchors=" ".join(x["anchor"] for x in rs if x["anchor"]),
             loot_points=len([x for x in loot if x["level"] == lvl]),
             critical_min=path_min, completion_min=full_min, notes=notes)
    r.update(kw)
    levels.append(r)


# ---------------------------------------------------------------- sites and Choir vaults
SITE_SEQ = {  # role order on the critical path (design choice, per kit)
    "KIT_TOWER": ["entry", "approach", "combat", "vertical", "combat", "puzzle", "vertical", "combat", "keeper"],
    "KIT_WRECK": ["entry", "approach", "combat", "gun", "puzzle", "vertical", "combat", "rest", "combat", "keeper"],
    "KIT_LAB": ["entry", "approach", "combat", "puzzle", "combat", "vertical", "combat", "keeper"],
    "KIT_FORT": ["entry", "gun", "combat", "combat", "approach", "keeper"],
    "KIT_CAVE": ["entry", "approach", "combat", "puzzle", "vertical", "combat", "keeper"],
    "KIT_CATACOMB": ["entry", "vertical", "combat", "approach", "puzzle", "combat", "vertical", "combat", "keeper"],
    "KIT_CHOIR_VAULT": ["entry", "puzzle", "combat", "keeper"],
}
UP_KITS = {"KIT_TOWER"}
DOWN_KITS = {"KIT_CAVE", "KIT_CATACOMB", "KIT_CHOIR_VAULT"}
VERT_TRAV = {"KIT_TOWER": "Ladder 2 m/s or cable climb", "KIT_WRECK": "Collapsed deck ramp / ladder",
             "KIT_LAB": "Maintenance ladder", "KIT_CAVE": "Glass slide (one-way drop 4 m)",
             "KIT_CATACOMB": "Spiral stair", "KIT_FORT": "Ramp", "KIT_CHOIR_VAULT": "Resonant stair"}

for sid, s in sorted(sites.items()):
    kit = s["template"]; loc = L[sid]; nrooms = int(s["rooms"]); floors = int(s["floors"])
    lex = LEX[kit][:]; light = KIT_LIGHT[kit]; mood = KIT_MOOD[kit]
    music, amb = f"MUS_{RCODE}_SITE", f"AMB_{RCODE}_INTERIOR"
    seq = SITE_SEQ[kit][:]
    if not s["puzzle"] and "puzzle" in seq:
        seq[seq.index("puzzle")] = "combat"
    boss = s["end"].replace("Site boss ", "") if s["end"].startswith("Site boss") else ""
    if boss:
        seq[-1] = "boss"; seq.insert(-1, "antechamber")
    # side rooms fill up to the site's room count
    sides = max(0, nrooms - len(seq) - 1)  # -1 for the reward room
    crit = []
    fl = 0
    for i, role in enumerate(seq):
        if role == "vertical":
            fl = fl + 1 if kit in UP_KITS or (kit not in DOWN_KITS and i % 2) else fl - 1
            fl = max(-floors + 1, min(floors - 1, fl))
        nm = {"entry": lex[0], "keeper": "Keeper's Hall", "boss": "Boss Arena", "antechamber": "Fog Gate Antechamber",
              "rest": "Quiet Alcove", "puzzle": "Puzzle: " + (s["puzzle"] or "Mechanism")[:28]}.get(role) or lex[(i % (len(lex) - 1)) + 1]
        beat = {"entry": "rest", "keeper": "keeper fight", "boss": "boss fight", "puzzle": "puzzle",
                "vertical": "traversal", "approach": "explore", "rest": "rest", "antechamber": "rest"}.get(role, "combat")
        trav = VERT_TRAV[kit] if role == "vertical" else ""
        dims = None
        if role == "boss":
            a = arenas.get(sid)
            d = int(a["diameter_m"]) if a else 34
            dims = (d, d, 14)
        r = room(sid, role, nm, fl, True, beat, mood, light, music, amb, trav, dims=dims,
                 notes=s["puzzle"] if role == "puzzle" else "")
        if crit:
            link(crit[-1], r, "path", trav or ("fog gate (4 m)" if role == "boss" else "walk"),
                 "one-way while fighting" if role == "boss" else "open")
        crit.append(r)
    # anchors
    add_anchor(crit[0], s["entrance_anchor"])
    if s["interior_anchor"]:
        mid = next((x for x in crit if x["role"] in ("rest", "antechamber")), crit[len(crit) // 2])
        add_anchor(mid, s["interior_anchor"])
    if boss:
        ante = next(x for x in crit if x["role"] == "antechamber")
        if not ante["anchor"]:
            ante["notes"] = "Nearest Anchor run per design/world/boss_arenas.csv"
    cue(crit[0], "Enter site", "MUSIC", music); cue(crit[0], "Enter site", "AMB", amb)
    cue(crit[0], "Enter site", "SFX", C["discover_s"]); cue(crit[0], "Always", "VFX", C["dust_v"])
    # encounters: keeper template to the end room, the rest in order over combat rooms
    es = ENC_BY_LOC.get(sid, [])
    keeper = [e for e in es if e["template"] == "ENT_KEEPER"]
    rest = [e for e in es if e["template"] != "ENT_KEEPER"]
    slots = [x for x in crit if x["role"] in ("combat", "gun", "approach", "vertical")] or crit[1:-1]
    for i, e in enumerate(rest):
        r = slots[i % len(slots)]
        trig = "Ambush volume 12 m" if e["template"] == "ENT_AMBUSH" else (
            "Sight 40 m" if e["template"] in ("ENT_GUNLINE", "ENT_FORT") else "Room entry")
        place_enc(r, e, trig, wave=1 + sum(1 for p in placements if p["room_id"] == r["room_id"]))
    end = crit[-1]
    for e in keeper:
        place_enc(end, e, "Room entry; doors lock until keeper dies")
    if boss:
        a = arenas.get(sid, {})
        cue(end, "Fog gate crossed", "VFX", vfx(f"{a.get('boss_name','')}|Arena barrier"))
        cue(end, "Boss intro", "SFX", sfx(f"{a.get('boss_name','')}|Intro sting"))
        cue(end, "Boss alive", "SFX", sfx(f"{a.get('boss_name','')}|Arena ambience"))
        boss_music(end, boss, a.get("arena_hooks", ""))
        end["encounters"] = boss; end["enemies"] = 1
        end["notes"] = f"{a.get('shape','')} {a.get('diameter_m','')} m; phases {a.get('arena_hooks','')}; {a.get('notes','')}"
    # reward and shortcut
    rw = room(sid, "reward", "Reward Alcove", end["floor"], True, "reward", "A single shaft of light on the pedestal",
              light, music, amb)
    link(end, rw, "path", "walk", "locked until fight ends")
    add_loot(rw, "Reward chest", s["unique_reward"], 1, "open", "Unique site reward (plan 3.7)")
    cue(rw, "Pick up", "VFX", C["loot_relic_v"])
    sc = room(sid, "shortcut", "Shortcut", end["floor"], True, "shortcut", "Daylight at the end; the entrance is below",
              light, music, amb, trav=s["shortcut"])
    link(rw, sc, "path"); link(sc, crit[0], "shortcut", s["shortcut"], "one-way until opened")
    cue(sc, "Open shortcut", "VFX", C["short_v"]); cue(sc, "Open shortcut", "SFX", C["short_s"])
    if "Lift" in s["shortcut"]:
        cue(sc, "Ride", "SFX", C["lift_s"]); cue(sc, "Ride", "VFX", C["lift_v"])
    # side rooms hang off critical rooms
    side_hosts = [x for x in crit[1:-1] if x["role"] not in ("antechamber",)]
    side_rooms = []
    for i in range(sides):
        h = side_hosts[(i * 2 + 1) % len(side_hosts)]
        sr = room(sid, "side", lex[(i + 3) % len(lex)] + " (side)", h["floor"], False, "explore", mood, light, music, amb)
        link(h, sr, "branch", "walk")
        side_rooms.append(sr)
    # lore room (plan: at least one lore item per site)
    lsite = s["lore_site"]
    lore_host = side_rooms[0] if side_rooms else crit[len(crit) // 2]
    lr = room(sid, "lore", "Lore Nook", lore_host["floor"], False, "lore", "Personal belongings, a corpse and a log terminal",
              light, music, amb)
    link(lore_host, lr, "branch")
    for it in LORE_BY_SITE.get(lsite, []):
        add_loot(lr, "Lore pickup" if it["lore_type"] != "Key" else "Key on corpse", it["item_id"], 1, "open",
                 it["name"])
        collect.append(dict(item=it["item_id"], kind=it["lore_type"], name=it["name"], level=sid, room_id=lr["room_id"],
                            lore_site=lsite))
    cue(lr, "In range 6 m", "VFX", C["lore_v"]); cue(lr, "Pick up", "SFX", C["lore_s"])
    # chests and crates already placed by world
    for child in [x for x in locs if x["parent_loc"] == sid]:
        if child["kind"] == "Small chest":
            h = side_rooms[-1] if side_rooms else crit[2]
            add_loot(h, "Chest", f"ITM_LT_SMALLCHEST_{REGION}", 1, "open", child["loc_id"])
        elif child["kind"] == "Shard crate":
            h = next((x for x in crit if x["role"] == "gun"), crit[-3])
            add_loot(h, "Shard crate", f"ITM_LT_SHARDCRATE_{REGION}", 1, "open", child["loc_id"] + "; charged ammo")
    # corpses with consumables and tier materials (design choice: 2 per site)
    add_loot(crit[1], "Corpse", "ITM_LT_CONSUMABLE", 1, "open")
    add_loot(crit[-3], "Corpse", f"ITM_LT_TIERMAT_{REGION}", 1, "open")
    # puzzle cues
    for x in crit:
        if x["role"] == "puzzle":
            cue(x, "Solve", "SFX", C["lever_s"]); cue(x, "Solve", "VFX", C["holo_v"] if kit == "KIT_LAB" else C["shard_v"])
    if kit == "KIT_WRECK":
        for x in crit[1:4]:
            cue(x, "Always", "VFX", C["spark_v"]); cue(x, "Always", "SFX", C["spark_s"])
    # secrets hosted here
    for sec in SEC_BY_HOST.get(sid, []):
        host = side_rooms[0] if side_rooms else crit[2]
        add_secret(sid, host, sec, SECRET_MECH.get(sec["secret_type"], sec["hint"]), reward_item(sec))
    pm = int(s["path_min"])
    full = round(pm * 1.4 + 2 * len(SEC_BY_HOST.get(sid, [])))
    level_row(sid, "Choir vault" if kit == "KIT_CHOIR_VAULT" else "Site", s["name"], s["level"],
              f"Node graph, {floors} floor(s), {kit}", pm, full,
              f"Ends: {s['end']}. Shortcut: {s['shortcut']}. Puzzle: {s['puzzle'] or 'none'}",
              boss=boss, unique_reward=s["unique_reward"], entry_requirement=loc["gate"],
              mood=mood, lighting=light, music=music, ambience=amb)

# ---------------------------------------------------------------- Citadel
CIT = f"LOC_CIT_{REGION}"
ZONE_ROOMS = {  # per zone style: role list (design choice)
    "Mixed": ["approach", "combat", "gun", "combat", "side"],
    "Melee close quarters": ["approach", "combat", "combat", "vertical", "combat", "side"],
    "Vertical climb": ["vertical", "combat", "vertical", "combat", "side"],
    "Gun gallery (40-80 m sightlines)": ["approach", "gun", "combat", "gun", "side"],
    "Boss arena": ["approach", "antechamber", "boss", "reward"],
}
ZNAMES = {
    "Dune Gate": ["Sand Ramp", "Outer Barbican", "Gatehouse Murder-walk", "Drone Yard", "Toll Cells"],
    "Glassblower Terraces": ["Kiln Steps", "Blowpipe Workshops", "Annealing Ovens", "Terrace Ladders", "Cullet Heap",
                             "Glassblower's Store"],
    "Lens Courts": ["Lens Shaft", "Polishing Court", "Focusing Tower", "Mirror Court", "Lens Vault"],
    "Sun Gallery": ["Gallery Steps", "Long Sun Gallery", "Reflector Battery", "Sniper Nest Row", "Heliograph Room"],
    "Engine Foundry": ["Slag Bridge", "Foundry Antechamber", "Engine Floor", "Grafted Cradle"],
    "Spire Cisterns": ["Cistern Stair", "Coolant Reservoir", "Pump Hall", "Overflow Channel", "Valve Gallery"],
    "Choir Ascent": ["Hymn Stair", "Bell Cages", "Iron Choir Barracks", "Anvil Mast Ladder", "Choir Practice Hall",
                     "Reliquary of Plates"],
    "The Iron Choir Loft": ["Loft Gangway", "Seat Antechamber", "Brannoch's Anvil", "The Iron Seat"],
}
ZMOOD = {
    "Dune Gate": "Wind-blasted gate in a dune wall; drone searchlights sweep the ramp; first view of the Spire above",
    "Glassblower Terraces": "Stepped workshops, glowing kilns and cooling racks of half-blown Shard glass; tight lanes",
    "Lens Courts": "Huge cracked lenses focus sun into white-hot spots that move with time of day",
    "Sun Gallery": "A 70 m mirrored hall; enemy gun lines at the far end; low cover of fallen lens frames",
    "Engine Foundry": "The buried Meridian engine, grafted with Iron Choir plate; molten channels; deafening rhythm",
    "Spire Cisterns": "Cool, dark, dripping coolant tanks below the Spire; blue Shard light under the water",
    "Choir Ascent": "Iron bells and hymn-machines; the Choir's soldiers drilling; climb toward the mast",
    "The Iron Choir Loft": "Open sky at the Spire top; Brannoch's forge-throne; the Quiet visible in orbit",
}
cit_rooms = {}
prev = None
first = None
for z in zones:
    zid = z["loc_id"]; style = z["style"]
    roles = ZONE_ROOMS[style][:]
    names = ZNAMES.get(z["name"], [z["name"]] * 8)
    zr = []
    fl = int(int(z["elevation_rel_m"]) / 14)
    for i, role in enumerate(roles):
        crit = role != "side"
        nm = names[i % len(names)]
        beat = {"boss": "boss fight", "antechamber": "rest", "reward": "reward", "vertical": "traversal",
                "approach": "explore", "side": "explore"}.get(role, "combat")
        dims = None
        if role == "boss":
            a = arenas.get(zid, {})
            d = int(a.get("diameter_m") or 54); dims = (d, d, 20)
        if role == "gun":
            dims = (16, 75, 12)
        r = room(CIT, role, f"{z['name']}: {nm}", fl + (1 if role == "vertical" else 0), crit, beat, ZMOOD.get(z["name"], ""),
                 "LGT_LVL_04_CITADEL", f"MUS_{RCODE}_CITADEL", f"AMB_{RCODE}_CITADEL",
                 "Ladder or lift" if role == "vertical" else "", dims=dims, notes=f"Zone {z['order']} {zid}")
        r["zone"] = zid
        if zr and crit:
            last_crit = [x for x in zr if x["critical_path"] == "Y"][-1]
            link(last_crit, r, "path", "fog gate (4 m)" if role == "boss" else "walk",
                 "one-way while fighting" if role == "boss" else "open")
        elif zr:
            link(zr[-2] if len(zr) > 1 else zr[-1], r, "branch")
        elif prev:
            link(prev, r, "path", "walk", "open", f"Zone {int(z['order'])-1} to {z['order']}")
        zr.append(r)
    if not first:
        first = zr[0]
    crits = [x for x in zr if x["critical_path"] == "Y"]
    if z["anchor"]:
        add_anchor(crits[0] if style != "Boss arena" else crits[1], z["anchor"])
    es = ENC_BY_LOC.get(zid, [])
    slots = [x for x in zr if x["beat"] in ("combat", "explore", "traversal") and x["role"] != "side"]
    for i, e in enumerate(es):
        place_enc(slots[i % len(slots)], e, "Sight 40 m" if e["template"] in ("ENT_GUNLINE", "ENT_FORT") else "Room entry")
    if z["boss"]:
        b = next(x for x in zr if x["role"] == "boss")
        a = arenas.get(zid, {})
        b["encounters"] = z["boss"]; b["enemies"] = 1
        b["notes"] += f"; {a.get('shape','')} {a.get('diameter_m','')} m, cover {a.get('cover_pieces','')}; phases {a.get('arena_hooks','')}; hazards {a.get('hazards','')}"
        cue(b, "Fog gate crossed", "VFX", vfx(f"{a.get('boss_name','')}|Arena barrier"))
        cue(b, "Boss intro", "SFX", sfx(f"{a.get('boss_name','')}|Intro sting"))
        cue(b, "Boss alive", "SFX", sfx(f"{a.get('boss_name','')}|Arena ambience"))
        boss_music(b, z["boss"], a.get("arena_hooks", ""))
        rw = next(x for x in zr if x["role"] == "reward")
        add_loot(rw, "Boss drop", "ITM_LT_BOSS_* (see data/items/loot_tables.csv owner " + z["boss"] + ")", 1, "open")
    # shortcut and locked door
    if z["shortcut"] and "none" not in z["shortcut"]:
        tail = crits[-1]
        cue(tail, "Open shortcut", "VFX", C["short_v"]); cue(tail, "Open shortcut", "SFX", C["short_s"])
        tail["traversal"] = (tail["traversal"] + "; " if tail["traversal"] else "") + "Shortcut: " + z["shortcut"]
    if z["locked_door"]:
        door = L[z["locked_door"]]
        key = door["gate"].replace("Key ", "")
        side = next((x for x in zr if x["role"] == "side"), crits[-1])
        tr = room(CIT, "side", f"{z['name']}: Locked Store", side["floor"], False, "reward",
                  "Iron Choir strongroom; racks of grafted plate", "LGT_LVL_04_CITADEL", f"MUS_{RCODE}_CITADEL",
                  f"AMB_{RCODE}_CITADEL", notes=f"Locked door {z['locked_door']} opens with {key} (optional, off path)")
        tr["zone"] = zid
        link(side, tr, "locked door", "door", f"locked: {key}")
        add_loot(tr, "Chest", f"ITM_LT_GEAR_{REGION}", 1, "open", "Behind locked door")
        add_loot(tr, "Chest", f"ITM_LT_TIERMAT_{REGION}", 1, "open")
        cue(tr, "Unlock", "SFX", C["doorm_s"]); cue(tr, "Unlock", "VFX", C["door_v"])
    sd = next((x for x in zr if x["role"] == "side"), None)
    if sd:
        add_loot(sd, "Corpse", "ITM_LT_CONSUMABLE", 1, "open")
    cit_rooms[zid] = zr
    prev = crits[-1]
# Citadel shortcuts as edges (from design/world/citadel_zones.csv)
def zcrit(zid, which=0):
    return [x for x in cit_rooms[zid] if x["critical_path"] == "Y"][which]
zmap = {z["loc_id"]: z for z in zones}
for z in zones:  # parse targets like "to Z1", "to the Z3 Anchor" from the world shortcut text
    if not z["shortcut"] or "none" in z["shortcut"]:
        continue
    for part in z["shortcut"].split(";"):
        m = re.search(r"\bZ(\d)\b", part.split(" to ")[-1]) if " to " in part else None
        tz = f"{CIT}_Z{m.group(1)}" if m else None
        if tz in cit_rooms and tz != z["loc_id"]:
            tgt = next((x for x in cit_rooms[tz] if x["anchor"]), zcrit(tz, 0)) if "Anchor" in part else zcrit(tz, 0)
            src = zcrit(z["loc_id"], 1 if zmap[z["loc_id"]]["style"] == "Boss arena" else -1)
            link(src, tgt, "shortcut", part.strip(), "one-way until opened")
        elif "field" in part:
            link(zcrit(z["loc_id"], -1), zcrit(z["loc_id"], -1), "exit", part.strip(), "one-way until opened")
cue(first, "Enter Citadel", "MUSIC", f"MUS_{RCODE}_CITADEL"); cue(first, "Enter Citadel", "AMB", f"AMB_{RCODE}_CITADEL")
cue(first, "Enter Citadel", "SFX", C["discover_s"])
for sec in SEC_BY_HOST.get(CIT, []):
    add_secret(CIT, first, sec, SECRET_MECH.get(sec["secret_type"], ""), reward_item(sec))
cpm = sum(int(z["path_min"]) for z in zones)
level_row(CIT, "Citadel", L[CIT]["name"], f"{zones[0]['level']}-{zones[-1]['level']}",
          f"Side-view flow, {len(zones)} zones, rises {zones[-1]['elevation_rel_m']} m", cpm, round(cpm * 1.35),
          "Plan 5.2: 2-3 h first play; every shortcut found by 60% of testers", boss="ACT_BOSS_GRAFTED ACT_BOSS_BRANNOCH",
          entry_requirement="MQ_A2_03 (story); open at any time", mood=KIT_MOOD["KIT_CITADEL"],
          lighting="LGT_LVL_04_CITADEL", music=f"MUS_{RCODE}_CITADEL", ambience=f"AMB_{RCODE}_CITADEL")

# ---------------------------------------------------------------- towns
TOWN_DISTRICTS = [  # role, name, notes
    ("entry", "Caravan Gate", "Guard post; wagons unload; first sight of the market canopy"),
    ("hub", "Shade Market", "Canopies of salvaged sail; vendors; crowd walla"),
    ("smith", "Glass Forge", "Smithing station; smith NPC"),
    ("inn", "Cistern Inn", "Rest, rumours, radiant job board"),
    ("faction", "Faction House", "Faction contact and quest givers"),
    ("homes", "Dune Homes", "Residents' schedules; locked homes (crime rules)"),
    ("shrine", "Anchor Shrine", "Town Anchor; fast travel"),
    ("overlook", "Wall Walk", "View to the Citadel and the Relay Tower; orientation beat"),
]
for tid in sorted(x["loc_id"] for x in locs if x["kind"] == "Settlement"):
    t = L[tid]; main = "Main town" in t["notes"]
    dist_list = TOWN_DISTRICTS if main else [d for d in TOWN_DISTRICTS if d[0] in ("entry", "hub", "inn", "homes", "shrine")]
    tr = []
    for role, nm, note in dist_list:
        r = room(tid, role, nm, 0, role in ("entry", "hub", "shrine"), "town", note, "LGT_REG_04_*",
                 f"MUS_{RCODE}_TOWN", f"AMB_{RCODE}_BED_DAY", dims=(30, 30, 10) if role == "hub" else (18, 18, 8))
        if tr:
            link(tr[1] if len(tr) > 1 and role != "hub" else tr[-1], r, "street")
        tr.append(r)
    sh = next(x for x in tr if x["role"] == "shrine")
    for a in ANC_BY_PARENT.get(tid, []):
        add_anchor(sh, a)
    cue(tr[0], "Enter town", "MUSIC", f"MUS_{RCODE}_TOWN"); cue(tr[0], "Enter town", "SFX", sfx("R4Glasswaste|Town") or C["discover_s"])
    who = [n for n in npcs if n["home_loc"] == tid]
    hub = tr[1]
    hub["notes"] = (hub["notes"] + "; NPCs: " + ", ".join(f"{n['act_id']} ({n['name']})" for n in who)).strip("; ")
    if tid == "LOC_TOWN_REG_04_01":
        hub["notes"] += "; ACT_NPC_MIRAGE_SABA (caravan matriarch, MQ_A2_03 giver)"
    add_loot(tr[-1], "Chest (owned: theft)", f"ITM_LT_SMALLCHEST_{REGION}", 1, "open", "Taking it is theft")
    level_row(tid, "Town", t["name"], t["level"], f"Street graph, {len(tr)} districts", 6 if main else 3, 20 if main else 10,
              t["notes"], entry_requirement="", mood="Safe; walla, shade, wind chimes of glass", lighting="LGT_REG_04_*",
              music=f"MUS_{RCODE}_TOWN", ambience=f"AMB_{RCODE}_BED_DAY")

# ---------------------------------------------------------------- POIs and small levels
POI_T = {  # tag: nodes (role, name), time min, mood
    "faction camp": ([("approach", "Picket Line"), ("combat", "Camp Ring"), ("side", "Leader's Tent")], 5,
                     "Smoke column visible at 600 m; drums; tents of hull-cloth"),
    "ruin": ([("approach", "Fallen Arch"), ("combat", "Inner Court"), ("side", "Cellar")], 4,
             "Pre-crash sun temple half-fused into glass"),
    "wreck fragment": ([("approach", "Debris Field"), ("combat", "Hull Shell")], 4,
                       "A torn Meridian section, sparks and creaking metal in wind"),
    "wayshrine": ([("rest", "Wayshrine")], 2, "Small Lantern Church shrine; prayer strips; safe"),
    "watchtower": ([("approach", "Tower Base"), ("vertical", "Tower Top")], 4,
                   "Lookout over the dunes; climbing it reveals nearby POIs on the compass"),
    "overturned cart": ([("combat", "Wreckage")], 3, "Ambushed caravan; tracks lead to the attackers"),
    "overlook": ([("rest", "Overlook Lip")], 2, "Vista; landmark framing shot; Strider glide start"),
    "hermit hut": ([("rest", "Hut"), ("side", "Hermit's Store")], 3, "One NPC hermit; trade or quest hook"),
    "grave field": ([("combat", "Grave Rows")], 3, "Glass headstones that sing at dusk; Hollowed rise at night"),
    "shard crater": ([("combat", "Crater Floor")], 4, "Glowing Shard in a crater; Shard-sick Hollowed drawn to it"),
    "hunting ground": ([("combat", "Grazing Flats")], 3, "Creature herd and predator; harvesting materials"),
    "lair": ([("approach", "Lair Mouth"), ("combat", "Lair")], 4, "Bones and nests; a large creature lives here"),
    "trader stop": ([("rest", "Trader Stop")], 2, "Wandering trader stops here on route; safe"),
    "vehicle depot": ([("approach", "Depot Yard"), ("combat", "Vehicle Bay")], 4,
                      "Remnant motor pool; clear it to unlock vehicles at this depot"),
}
for pid in sorted(x["loc_id"] for x in locs if x["kind"] == "POI"):
    p = L[pid]; tag = p["tags"]
    nodes, tmin, mood = POI_T.get(tag, ([("combat", p["name"])], 3, ""))
    pr = []
    for role, nm in nodes:
        r = room(pid, role, nm, 1 if role == "vertical" else 0, role != "side", {"rest": "rest", "side": "explore",
                 "approach": "explore", "vertical": "traversal"}.get(role, "combat"), mood, "LGT_REG_04_*",
                 f"MUS_{RCODE}_EXPLORE_DAY", f"AMB_{RCODE}_BED_DAY", "Ladder" if role == "vertical" else "",
                 dims=(40, 40, 0) if role == "combat" else (16, 16, 0))
        if pr:
            link(pr[-1] if role != "side" else pr[-1], r, "path" if role != "side" else "branch")
        pr.append(r)
    for e in ENC_BY_LOC.get(pid, []):
        tgt = next((x for x in pr if x["beat"] == "combat"), pr[0])
        place_enc(tgt, e, "Ambush volume 12 m" if e["template"] == "ENT_AMBUSH" else "Sight 40 m")
    for child in [x for x in locs if x["parent_loc"] == pid and x["kind"] == "Small chest"]:
        add_loot(pr[-1], "Chest", f"ITM_LT_SMALLCHEST_{REGION}", 1, "open", child["loc_id"])
    for sec in SEC_BY_HOST.get(pid, []):
        add_secret(pid, pr[0], sec, SECRET_MECH.get(sec["secret_type"], ""), reward_item(sec))
    if tag == "vehicle depot":
        pr[-1]["notes"] = "Vehicles: " + layout["vehicles"]
    if tag == "watchtower":
        cue(pr[-1], "Reach top", "SFX", C["discover_s"])
    if tag == "overlook":
        cue(pr[0], "First visit", "MUSIC", f"MUS_{RCODE}_DISCOVERY")
    cue(pr[0], "Always", "VFX", C["region_v"])
    level_row(pid, "POI", p["name"], p["level"], f"{len(pr)} node(s), open field", tmin,
              tmin + 2 * len(SEC_BY_HOST.get(pid, [])), p["notes"], mood=mood, lighting="LGT_REG_04_*",
              music=f"MUS_{RCODE}_EXPLORE_DAY", ambience=f"AMB_{RCODE}_BED_DAY")

# Relay Tower
rid = f"LOC_RELAY_{REGION}"
rl = L[rid]
rr = [room(rid, "entry", "Tower Foot", 0, True, "rest", "Remnant relay mast wrapped in glass; base half-buried",
           "LGT_REG_04_*", f"MUS_{RCODE}_EXPLORE_DAY", f"AMB_{RCODE}_WIND"),
      room(rid, "vertical", "Stage 1: Ledges", 1, True, "traversal", "Mantle ledges (2.0 m max) spiral up the outside",
           "LGT_REG_04_*", f"MUS_{RCODE}_EXPLORE_DAY", f"AMB_{RCODE}_WIND", "Mantle ledges"),
      room(rid, "combat", "Stage 2: Lift Platform", 2, True, "combat", "Drone nest guards the lift motor",
           "LGT_REG_04_*", f"MUS_{RCODE}_TENSION", f"AMB_{RCODE}_WIND", "Lift 4 m/s, 30 m"),
      room(rid, "vertical", "Stage 3: Ladder", 3, True, "traversal", "Exposed ladder; wind gusts", "LGT_REG_04_*",
           f"MUS_{RCODE}_EXPLORE_DAY", f"AMB_{RCODE}_WIND", "Ladder 2 m/s, 25 m"),
      room(rid, "reward", "Relay Crown", 4, True, "reward", "Ostra fills in the region map; 360-degree vista",
           "LGT_REG_04_*", f"MUS_{RCODE}_DISCOVERY", f"AMB_{RCODE}_WIND", "Glide off to any direction (Strider)")]
for a, b in zip(rr, rr[1:]):
    link(a, b, "path", b["traversal"] or "walk")
for a in ANC_BY_PARENT.get(rid, []):
    add_anchor(rr[0], a)
cue(rr[-1], "Activate", "VFX", C["relay_v"]); cue(rr[-1], "Activate", "SFX", C["relay_s"])
cue(rr[-1], "Activate", "VFX", C["map_v"]); cue(rr[-1], "Activate", "MUSIC", f"MUS_{RCODE}_DISCOVERY")
placements.append(dict(enc_id="LENC_04_001", room_id=rr[2]["room_id"], level=rid, template="ENT_AMBUSH",
                       faction="FAC_REMNANT", enemy_level=rl["level"], actors="ACT_VAR_R4_05 x3; ACT_REMNANT_ARTILLERY x1",
                       enemy_count=4, trigger="Step onto lift platform", wave=1, spawn_points=2, cover_points=3,
                       fallback_points=1, respawn="On Anchor rest", alert_link="New: requested in data-requests.csv"))
rr[2]["encounters"] = "LENC_04_001"; rr[2]["enemies"] = 4
level_row(rid, "Relay Tower", rl["name"], rl["level"], "Vertical climb, 3 stages, 80 m", 6, 8, rl["notes"],
          mood="Wind and height; the region opens up", lighting="LGT_REG_04_*", music=f"MUS_{RCODE}_EXPLORE_DAY",
          ambience=f"AMB_{RCODE}_WIND")

# Choir site
cid = f"LOC_CHOIR_{REGION}"
cl = L[cid]
cr = [room(cid, "entry", "Hidden Dune Door", -1, True, "rest", KIT_MOOD["KIT_CHOIR_VAULT"], "LGT_LVL_04_VAULT",
           f"MUS_{RCODE}_SITE", f"AMB_{RCODE}_INTERIOR", notes=cl["gate"]),
      room(cid, "puzzle", "Chorus Hall", -1, True, "puzzle", "Six singing pillars; match the tone Ostra hums",
           "LGT_LVL_04_VAULT", f"MUS_{RCODE}_SITE", f"AMB_{RCODE}_INTERIOR", notes="Match the tone pillars"),
      room(cid, "combat", "Warden Court", -2, True, "combat", "Choir wardens test the Kindled", "LGT_LVL_04_VAULT",
           f"MUS_{RCODE}_SITE", f"AMB_{RCODE}_INTERIOR"),
      room(cid, "reward", "Resonance Heart", -2, True, "reward", "A single huge Shard sings; the Resonance is granted",
           "LGT_LVL_04_VAULT", f"MUS_{RCODE}_DISCOVERY", f"AMB_{RCODE}_WEAVE_HUM")]
for a, b in zip(cr, cr[1:]):
    link(a, b, "path")
for a in ANC_BY_PARENT.get(cid, []):
    add_anchor(cr[0], a)
for e in ENC_BY_LOC.get(cid, []):
    place_enc(cr[2], e, "Room entry")
res = re.search(r"(RES_[A-Z0-9_]+)", cl["notes"])
add_loot(cr[3], "Resonance", res.group(1) if res else "RES_*", 1, "open", "Plan 3.4: Resonances come from Choir sites")
cue(cr[3], "Grant", "VFX", C["weave_v"]); cue(cr[3], "Always", "SFX", C["hum_s"])
level_row(cid, "Choir site", cl["name"], cl["level"], "4 rooms, below the dunes", 10, 14, cl["notes"],
          entry_requirement=cl["gate"], mood=KIT_MOOD["KIT_CHOIR_VAULT"], lighting="LGT_LVL_04_VAULT",
          music=f"MUS_{RCODE}_SITE", ambience=f"AMB_{RCODE}_INTERIOR")

# Field bosses
for fid in sorted(x["loc_id"] for x in locs if x["kind"] == "Field boss"):
    a = arenas[fid]; fl_ = L[fid]
    fr = [room(fid, "approach", "Approach", 0, True, "explore", "Spoor, wreckage and warning signs on the way in",
               "LGT_REG_04_*", f"MUS_{RCODE}_TENSION", f"AMB_{RCODE}_BED_DAY"),
          room(fid, "boss", "Boss Ground", 0, True, "boss fight", a["notes"], "LGT_REG_04_*", "", f"AMB_{RCODE}_WIND",
               "Strider allowed", dims=(int(a["diameter_m"]), int(a["diameter_m"]), 0),
               notes=f"{a['shape']}; cover {a['cover_pieces']}; {a['entry']}; phases {a['arena_hooks']}")]
    link(fr[0], fr[1], "path")
    fr[1]["encounters"] = a["boss"]; fr[1]["enemies"] = 1
    for anc in ANC_BY_PARENT.get(fid, []):
        add_anchor(fr[0], anc)
    cue(fr[1], "Boss aggro", "VFX", vfx(f"{a['boss_name']}|Intro") or vfx(f"{a['boss_name']}|Arena barrier"))
    cue(fr[1], "Boss aggro", "SFX", sfx(f"{a['boss_name']}|Intro sting"))
    boss_music(fr[1], a["boss"], a["arena_hooks"])
    add_loot(fr[1], "Boss drop", f"ITM_LT_BOSS_* (owner {a['boss']})", 1, "open", "Trophy: Ascendant Shard (data README 21)")
    level_row(fid, "Field boss", fl_["name"], fl_["level"], f"Open ground {a['diameter_m']} m", 6, 10, fl_["notes"],
              boss=a["boss"], mood=a["notes"], lighting="LGT_REG_04_*", music="Boss cue", ambience=f"AMB_{RCODE}_WIND")

# Landmarks, lore sites in the open, connection, patrols, gather nodes
for lid in sorted(x["loc_id"] for x in locs if x["kind"] == "Landmark"):
    lm = landmarks.get(lid, {}); ll = L[lid]
    r = room(lid, "landmark", ll["name"], 0, True, "explore",
             f"Height {lm.get('height_m','?')} m, visible {lm.get('visible_km','?')} km; silhouette readable against sky",
             "LGT_REG_04_*", f"MUS_{RCODE}_EXPLORE_DAY", f"AMB_{RCODE}_EMITTERS")
    cue(r, "First seen (on screen 2 s)", "MUSIC", f"MUS_{RCODE}_DISCOVERY")
    level_row(lid, "Landmark", ll["name"], ll["level"], "Single set piece", 1, 2, lm.get("role", ""), mood=r["mood"])
for sid2 in sorted(x["loc_id"] for x in locs if x["kind"] == "Lore site" and not x["parent_loc"]):
    sl = L[sid2]
    r = room(sid2, "lore", "Lore Site", 0, True, "lore", "Glass War battlefield remains: a fused soldier, a banner",
             "LGT_REG_04_*", f"MUS_{RCODE}_EXPLORE_DAY", f"AMB_{RCODE}_BED_DAY")
    for it in LORE_BY_SITE.get(sid2, []):
        add_loot(r, "Lore pickup", it["item_id"], 1, "open", it["name"])
        collect.append(dict(item=it["item_id"], kind=it["lore_type"], name=it["name"], level=sid2, room_id=r["room_id"],
                            lore_site=sid2))
    cue(r, "In range 6 m", "VFX", C["lore_v"]); cue(r, "Pick up", "SFX", C["lore_s"])
    level_row(sid2, "Lore site", sl["name"], sl["level"], "Single node", 2, 2, "", mood=r["mood"])
for con in sorted(x["loc_id"] for x in locs if x["kind"] == "Connection"):
    cn = L[con]
    a_ = room(con, "approach", "Glassfall Rim", 0, True, "explore", "A sinkhole in the glass; wind roars up from below",
              "LGT_REG_04_*", f"MUS_{RCODE}_TENSION", f"AMB_{RCODE}_WIND")
    b_ = room(con, "vertical", "Drop Shaft", -1, True, "traversal", "One-way drop toward Hollowdeep; lift returns once lit",
              "LGT_LVL_04_CAVE", f"MUS_{RCODE}_TENSION", f"AMB_{RCODE}_INTERIOR", cn["gate"])
    link(a_, b_, "connection", "Drop (no damage: slide)", "one-way", cn["gate"])
    level_row(con, "Connection", cn["name"], cn["level"], "Region exit to REG_06", 2, 2, cn["gate"])
for pat in sorted(x["loc_id"] for x in locs if x["kind"] == "Patrol route"):
    pt = L[pat]
    r = room(pat, "route", "Patrol loop", 0, True, "combat", "Patrol walks a 150-300 m loop between Anchors",
             "LGT_REG_04_*", f"MUS_{RCODE}_EXPLORE_DAY", f"AMB_{RCODE}_BED_DAY",
             notes="Waypoints: " + "; ".join(f"{int(float(pt['x_m'])+dx)},{int(float(pt['y_m'])+dy)}"
                                            for dx, dy in ((0, 0), (90, 30), (60, 110), (-40, 70))))
    for e in ENC_BY_LOC.get(pat, []):
        place_enc(r, e, "Sight 40 m (patrol)")
    level_row(pat, "Patrol route", pt["name"], pt["level"], "4-waypoint loop", 1, 1, "")

# outside locked doors: attach to nearest level
lv_pos = {l["level_id"]: L.get(l["level_id"]) for l in levels}
for d in sorted(x["loc_id"] for x in locs if x["kind"] == "Locked door" and not x["parent_loc"]):
    dl = L[d]
    near = min((k for k, v in lv_pos.items() if v and v["kind"] in ("POI", "Site", "Choir vault")), key=lambda k: dist(dl, lv_pos[k]))
    host = _lvl_rooms[near][0]
    key = dl["gate"].replace("Key ", "")
    tr = room(near, "side", "Locked Cellar", host["floor"], False, "reward", "Sealed store under the sand",
              host["lighting"], host["music_state"], host["ambience"], notes=f"Door {d} needs {key}")
    link(host, tr, "locked door", "door", f"locked: {key}")
    add_loot(tr, "Chest", f"ITM_LT_GEAR_{REGION}", 1, "open", f"Behind {d}")
    lr_ = next(l for l in levels if l["level_id"] == near)
    lr_["rooms"] += 1; lr_["loot_points"] += 1

# gather nodes: nearest level within 150 m, else open field
gather = []
for g in sorted((x for x in locs if x["kind"] == "Gather node"), key=lambda x: x["loc_id"]):
    near = min(lv_pos, key=lambda k: dist(g, lv_pos[k]) if lv_pos[k] else 1e9)
    dd = dist(g, lv_pos[near]) if lv_pos[near] else 1e9
    gather.append(dict(node=g["loc_id"], type=g["tags"], loot_table=f"ITM_LT_NODE_{g['tags'].upper()}",
                       level=near if dd <= 150 else "Open field", distance_m=round(dd), x_m=g["x_m"], y_m=g["y_m"]))

# Tonic Seed and Distillation and keys as collectibles (from secrets)
for s in secrets:
    if "TNC" in s["reward"]:
        collect.append(dict(item=reward_item(s), kind="Key upgrade", name=s["reward"], level=s["host_loc"],
                            room_id=next((x["secret_room"] for x in secrets_out if x["secret_id"] == s["loc_id"]), ""),
                            lore_site=""))

# ---------------------------------------------------------------- region critical path
ZB = {z["boss"]: z["loc_id"] for z in zones if z["boss"]}
zg, zb = int(ZB["ACT_BOSS_GRAFTED"][-1]), int(ZB["ACT_BOSS_BRANNOCH"][-1])
m1 = sum(int(z["path_min"]) for z in zones if int(z["order"]) <= zg)
crit_path = [
    ("01", "Arrive by CON_05 mountain pass (Saltmere) or CON_11 road (Thornwood)", "LOC_CON_05 / LOC_CON_11", "32", "MQ_A2_01", 5),
    ("02", "Reach Glassmouth Caravanserai; meet Saba; MQ_A2_03 starts", "LOC_TOWN_REG_04_01", "36", "MQ_A2_03", 15),
    ("03", "Climb the Relay Tower; map fills in", f"LOC_RELAY_{REGION}", "38", "MQ_RT_04", 8),
    ("04", "The Last Hangar: Last Pilot; recruit Unit 9 (ACT_CMP_C8)", "LOC_DGN_REG_04_10", "37", "MQ_A2_03", 30),
    ("05", "Choirtower Hamlet: recruit Hal Merrow (optional)", "LOC_TOWN_REG_04_02", "40", "", 10),
    ("06", "Glass Basilisk (optional field boss)", "LOC_FB_BASILISK", "40", "", 10),
    ("07", f"Citadel zones 1-{zg} to the Grafted Engine", f"{CIT}_Z1-Z{zg}", "43-45", "MQ_A2_03C", m1),
    ("08", f"Citadel zones {zg+1}-{zb} to Brannoch Iron-Choir; Heart Shard choice", f"{CIT}_Z{zg+1}-Z{zb}", "45-46", "MQ_A2_03", cpm - m1),
]
cp = [dict(step=a, beat=b, where=c, player_level=d, quest=e, minutes=f) for a, b, c, d, e, f in crit_path]

# ---------------------------------------------------------------- quest location aliases (proposal)
aliases = [
    ("LOC_CQ_REG_04_GRAFTED_FOUNDRY", ZB["ACT_BOSS_GRAFTED"], "Zone with the Grafted Engine arena"),
    ("LOC_CQ_REG_04_BRANNOCHS_ANVIL", ZB["ACT_BOSS_BRANNOCH"], "Brannoch's seat"),
    ("LOC_CQ_REG_04_ANVIL_MAST", next(z["loc_id"] for z in zones if z["name"] == "Choir Ascent"), "Choir Ascent: Anvil Mast Ladder room"),
    ("LOC_CQ_REG_04_MIRROR_HALL", "LOC_DGN_REG_04_03", "Hall of Panes (Mirror Knight site)"),
    ("LOC_CQ_REG_04_LAST_HANGAR", "LOC_DGN_REG_04_10", "Shuttle Bay Wreck (Last Pilot site)"),
    ("LOC_CQ_REG_04_RELAY_TOWER_9", f"LOC_RELAY_{REGION}", "Glasswaste Relay Tower"),
    ("LOC_CQ_REG_04_IRON_CHOIR_CAMP", "LOC_POI_REG_04_29", "Lens Faction camp; Remnant camp ENC_0533 becomes the drone pickets"),
    ("LOC_CQ_REG_04_GLASS_ROAD_CAMP", "LOC_POI_REG_04_07", "Sun Overlook; quiet camp spot on the Glass Road"),
]
al = [dict(quest_loc=a, world_loc=b, note=c) for a, b, c in aliases]

HAZ = {  # design choice: a hazard keeps a fight-shaped room busy when no encounter is placed
    "KIT_TOWER": "Lens hot spot: focused sun spot 3 m wide moves across the floor, 40 Ember-fire dmg/s",
    "KIT_WRECK": "Sparking conduit: Storm arc every 4 s along a 6 m strip (Shock)",
    "KIT_LAB": "Laser grid: Remnant tripwire calls 2 Hornet Drones (ACT_VAR_R4_05)",
    "KIT_FORT": "Spike-trap pit: hidden glass spikes, 180 dmg, visible on second look",
    "KIT_CAVE": "Singing glass: loud tone every 6 s staggers (stance 30) within 5 m of the wall",
    "KIT_CATACOMB": "Mirror dart trap: pressure plate fires darts from the wall, 120 dmg",
    "KIT_CHOIR_VAULT": "Resonant pillar: hum builds 3 s then knocks back 4 m",
    "CIT": "Molten cullet channel: 2 m wide, Burn on contact; jump or bridge",
    "OPEN": "Creature ambush: Rust Beetles (ACT_CRT_RUSTBEETLE x3) burst from the sand",
}
for r in rooms:
    if r["beat"] == "combat" and not r["encounters"]:
        kit = sites.get(r["level"], {}).get("template") or ("CIT" if r["level"] == CIT else "OPEN")
        r["beat"] = "hazard"
        r["notes"] = (r["notes"] + "; " if r["notes"] else "") + "Hazard: " + HAZ.get(kit, HAZ["OPEN"])
        cue(r, "Hazard active", "VFX", C["trap_v"]); cue(r, "Hazard trigger", "SFX", C["trap_s"])

# ---------------------------------------------------------------- write
wr("levels.csv", levels, ["level_id", "kind", "name", "story_name", "level", "layout", "rooms", "secret_rooms",
                          "encounters", "enemies", "anchors", "loot_points", "critical_min", "completion_min", "boss",
                          "unique_reward", "entry_requirement", "mood", "lighting", "music", "ambience", "notes"])
wr("rooms.csv", rooms, ["room_id", "level", "order", "name", "role", "floor", "size_m", "critical_path", "beat",
                        "encounters", "enemies", "anchor", "traversal", "lighting", "music_state", "ambience", "mood", "notes"])
wr("edges.csv", edges)
wr("encounter_placement.csv", placements)
wr("loot_placement.csv", loot)
wr("secrets.csv", secrets_out)
wr("collectibles.csv", collect)
wr("gather_nodes.csv", gather)
wr("cues.csv", cues)
wr("critical_path.csv", cp)
wr("quest_location_aliases.csv", al)

# ---------------------------------------------------------------- SVG node graphs (major levels)
def svg(lvl):
    rs = [r for r in _lvl_rooms[lvl]]
    if len(rs) < 3:
        return
    col = {"Y": "#C7A8E0", "N": "#8A857A"}
    pos = {}
    rowkey = (lambda r: r.get("zone") or r["floor"]) if lvl == CIT else (lambda r: int(r["floor"]))
    floors_ = sorted({rowkey(r) for r in rs}, reverse=True)
    perfl = defaultdict(int)
    for r in rs:
        f = rowkey(r); perfl[f] += 1
        pos[r["room_id"]] = (60 + perfl[f] * 190, 40 + floors_.index(f) * 110)
    wid = max(p[0] for p in pos.values()) + 160; hei = max(p[1] for p in pos.values()) + 90
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{wid}" height="{hei}" font-family="sans-serif" font-size="11">',
           f'<rect width="100%" height="100%" fill="#16141C"/>']
    for e in edges:
        if e["level"] != lvl or e["from_room"] not in pos or e["to_room"] not in pos:
            continue
        (x1, y1), (x2, y2) = pos[e["from_room"]], pos[e["to_room"]]
        c = {"shortcut": "#8FE3EE", "secret": "#9B7BD6", "locked door": "#A87A4A"}.get(e["kind"], "#777")
        dash = ' stroke-dasharray="6 4"' if e["kind"] in ("shortcut", "secret", "locked door") else ""
        out.append(f'<line x1="{x1+85}" y1="{y1+20}" x2="{x2+85}" y2="{y2+20}" stroke="{c}" stroke-width="2"{dash}/>')
    for r in rs:
        x, y = pos[r["room_id"]]
        fill = "#3A2F4A" if r["critical_path"] == "Y" else "#2A2A2A"
        if r["role"] in ("boss", "keeper"):
            fill = "#6A2A2A"
        out.append(f'<rect x="{x}" y="{y}" width="170" height="40" rx="6" fill="{fill}" stroke="{col[r["critical_path"]]}"/>')
        out.append(f'<text x="{x+6}" y="{y+16}" fill="#EEE">{r["order"]}. {r["name"].split(": ")[-1][:24]}</text>')
        tag = ("A " if r["anchor"] else "") + (f'{r["enemies"]}e' if int(r["enemies"]) else "")
        out.append(f'<text x="{x+6}" y="{y+32}" fill="#BBB">{r["role"]} {tag}</text>')
    for f in floors_:
        lab = zmap[f]["name"] if lvl == CIT and f in zmap else f"Floor {f}"
        out.append(f'<text x="10" y="{40 + floors_.index(f) * 110 + 25}" fill="#C7A8E0">{lab[:24]}</text>')
    out.append(f'<text x="10" y="{hei-10}" fill="#AAA">{lvl}: rows are floors; violet border = critical path; cyan dashed = shortcut; purple dashed = secret; brown dashed = locked door; A = Anchor; e = enemies</text></svg>')
    p = os.path.join(OUT, "maps", f"{lvl}.svg")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write("\n".join(out))


major = [l["level_id"] for l in levels if l["kind"] in ("Citadel", "Site", "Choir vault", "Town", "Relay Tower", "Choir site")]
for m in major:
    svg(m)

# ---------------------------------------------------------------- one-page sheets for major levels
os.makedirs(os.path.join(OUT, "sheets"), exist_ok=True)
for l in levels:
    if l["level_id"] not in major and l["kind"] != "Field boss":
        continue
    lid = l["level_id"]
    rs = _lvl_rooms[lid]
    lines = [f"# {l['name']}" + (f" ({l['story_name']})" if l["story_name"] else ""), "",
             f"{l['kind']}, level {l['level']}. {l['layout']}. Critical path {l['critical_min']} min, full clear "
             f"{l['completion_min']} min. {l['encounters']} encounters, {l['enemies']} enemies, {l['loot_points']} loot points, "
             f"{l['secret_rooms']} secret(s). Anchors: {l['anchors'] or 'none'}.", "",
             f"Mood: {l['mood']}", "", f"Lighting {l['lighting']}, music {l['music']}, ambience {l['ambience']}.", ""]
    if l.get("boss"):
        lines += [f"Boss: {l['boss']}.", ""]
    if l["notes"]:
        lines += [l["notes"], ""]
    if os.path.exists(os.path.join(OUT, "maps", f"{lid}.svg")):
        lines += [f"Map: [maps/{lid}.svg](../maps/{lid}.svg)", ""]
    lines += ["| # | Room | Role | Floor | Size (m) | Path | Encounters | Anchor | Traversal | Notes |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rs:
        lines.append(f"| {r['order']} | {r['name']} | {r['role']} | {r['floor']} | {r['size_m']} | {r['critical_path']} | "
                     f"{r['encounters']} | {r['anchor']} | {r['traversal']} | {r['notes'][:120]} |")
    lp = [x for x in loot if x["level"] == lid]
    if lp:
        lines += ["", "Loot: " + "; ".join(f"{x['room_id'][-2:]} {x['container']}: {x['item']}" for x in lp)]
    ed = [x for x in edges if x["level"] == lid and x["kind"] in ("shortcut", "secret", "locked door", "connection")]
    if ed:
        lines += ["", "Shortcuts, secrets and doors: " + "; ".join(
            f"{x['from_room'][-2:]} to {x['to_room'][-2:]} {x['kind']} ({x['traversal']}, {x['initial_state']})" for x in ed)]
    open(os.path.join(OUT, "sheets", f"{lid}.md"), "w").write("\n".join(lines) + "\n")

print(f"levels {len(levels)}, rooms {len(rooms)}, edges {len(edges)}, encounters placed {len(placements)}, "
      f"loot {len(loot)}, secrets {len(secrets_out)}, collectibles {len(collect)}, cues {len(cues)}, gather {len(gather)}, "
      f"maps {len(major)}")
tot = sum(int(l['critical_min']) for l in levels if l['kind'] not in ('Patrol route',))
full = sum(int(l['completion_min']) for l in levels if l['kind'] not in ('Patrol route',))
print("region critical-path content minutes", tot, "completion", full)
