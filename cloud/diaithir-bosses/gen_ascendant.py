"""Additive generator for the Ascendant tier of diaithir-bosses: nine post-endgame bosses (Age VII and Rodos), the boss rush
sequence, difficulty modes, quests, event hooks, Codex chapter and gates. Touches only the files it adds or merges into
(boss_index, lang, age_gates, names_map, codex); gen.py (which wipes and rebuilds the base set) is not needed.
Run: python3 -I tools/gen_ascendant.py <dir with the vanilla entity skins, <kind>/<kind>.png>
Names come from tools/archaic.py (Diaithiris) via modern Goidelic source words; nothing is copied from any other game or mod.
"""
import ast, importlib.util, json, os, random, sys
import numpy as np
from PIL import Image

VAN = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = "diaithirbosses"
RES = os.path.join(ROOT, "src/main/resources")
AS, DA = os.path.join(RES, "assets", NS), os.path.join(RES, "data", NS)
ROM = ["", "I", "II", "III", "IV", "V", "VI", "VII", "Rodos"]

# reuse gen.py's attack/phase/loot builders instead of copying them
_src = open(os.path.join(ROOT, "tools/gen.py"), encoding="utf8").read()
_want = {"A", "slam", "charge", "leap", "bolt", "summon", "lightning", "cloud", "wave", "heal", "roar", "phases", "L", "arms_set"}
G = {"ROM": ROM, "DMG": {7: 24, 8: 34}, "HP": {7: 950, 8: 1500}}
for n in ast.parse(_src).body:
    if isinstance(n, ast.FunctionDef) and n.name in _want:
        exec(compile(ast.Module([n], []), "gen.py", "exec"), G)
slam, charge, leap, bolt, summon, lightning, cloud, wave, heal, roar, phases, L = (G[k] for k in
    ("slam", "charge", "leap", "bolt", "summon", "lightning", "cloud", "wave", "heal", "roar", "phases", "L"))

_sp = importlib.util.spec_from_file_location("archaic", "/mnt/project-files/diaithiris-archaic/tools/archaic.py")
ARCH = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(ARCH)
_h = "/mnt/project-files/diaithiris-archaic/"
ARCH.MEMO.update(json.load(open(_h + "archaic_map.json")))
ARCH.OVERRIDES.update(json.load(open(_h + "tools/overrides.json")))

def nm(*words): return " ".join(ARCH.text(w).capitalize() for w in words)

def W(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf8"), indent=1, ensure_ascii=False)

def R(path):
    return json.load(open(path, encoding="utf8"))

# kind -> vanilla skin folder, ramp (dark, mid, light)
RAMP = {
    "antler": ("hoglin", (0.06, 0.05, 0.04), (0.38, 0.30, 0.20), (0.86, 0.80, 0.62)),
    "cauldron": ("iron_golem", (0.04, 0.07, 0.06), (0.22, 0.42, 0.36), (0.70, 0.92, 0.74)),
    "tide": ("guardian", (0.02, 0.07, 0.12), (0.12, 0.38, 0.52), (0.62, 0.92, 0.98)),
    "foundry": ("iron_golem", (0.08, 0.05, 0.03), (0.48, 0.30, 0.16), (0.98, 0.72, 0.28)),
    "mist": ("spider", (0.07, 0.07, 0.10), (0.46, 0.48, 0.58), (0.92, 0.94, 0.98)),
    "ash": ("blaze", (0.06, 0.05, 0.05), (0.40, 0.36, 0.34), (0.92, 0.88, 0.82)),
    "dusk": ("phantom", (0.03, 0.02, 0.07), (0.22, 0.14, 0.40), (0.72, 0.56, 0.96)),
    "root": ("ravager", (0.04, 0.06, 0.03), (0.24, 0.34, 0.14), (0.74, 0.86, 0.44)),
    "wheel": ("illager", (0.07, 0.06, 0.02), (0.60, 0.50, 0.14), (1.00, 0.94, 0.56)),
}

# id, source words (modern Goidelic, run through the archaic tool), English name, kind, ramp, scale, age, tier, bar
SPEC = [
    ("antlered_hollow", ("damh", "falamh"), "Antlered Hollow", "hoglin", "antler", 1.9, 7, 1, "green"),
    ("cauldron_heart", ("coire", "cridhe"), "Cauldron-Heart", "golem", "cauldron", 2.5, 7, 1, "green"),
    ("tide_reaver", ("tonn", "creachadair"), "Tide Reaver", "guardian", "tide", 2.2, 7, 1, "blue"),
    ("foundry_sovereign", ("ceardach", "rìgh"), "Foundry Sovereign", "golem", "foundry", 3.0, 8, 2, "yellow"),
    ("mist_weaver", ("ceò", "figheadair"), "Mist Weaver", "spider", "mist", 2.4, 8, 2, "white"),
    ("ash_seraph", ("luaithre", "ainglean"), "Ash Seraph", "blaze", "ash", 2.2, 8, 2, "red"),
    ("dusk_wyrm", ("dorchadas", "nathair"), "Dusk Wyrm", "phantom", "dusk", 3.2, 8, 3, "purple"),
    ("rootbreaker", ("fréamh", "bristeoir"), "Rootbreaker", "ravager", "root", 2.4, 8, 3, "green"),
    ("last_wheel", ("roth", "deireadh"), "The Last Wheel", "illager", "wheel", 2.0, 8, 3, "pink"),
]
TIER_M = {1: (1.0, 1.0), 2: (1.0, 1.15), 3: (1.35, 1.3)}   # hp mult, damage mult
KIT = {
    "antlered_hollow": dict(atk=lambda a: {"gore": charge(a, 1.1, 22, 90), "root_snare": cloud(a, "minecraft:slowness", 7, 24, 150, 100, 2),
                                           "herd_call": summon(a, "minecraft:hoglin", 2, 4, 44, 260), "antler_sweep": slam(a, 6, 1.0, 28, 85)},
                            ph=(["gore", "antler_sweep"], ["gore", "antler_sweep", "root_snare"], ["gore", "antler_sweep", "root_snare", "herd_call"])),
    "cauldron_heart": dict(atk=lambda a: {"boil_over": cloud(a, "minecraft:poison", 8, 28, 150, 120, 2), "ladle": slam(a, 7, 1.1, 36, 95),
                                          "brew_bolt": bolt(a, 4, 0.8, 30, 100, effect="minecraft:wither", rng=34), "mend": heal(a, 0.03, 50, 420)},
                           ph=(["ladle", "brew_bolt"], ["ladle", "brew_bolt", "boil_over"], ["ladle", "brew_bolt", "boil_over", "mend"])),
    "tide_reaver": dict(atk=lambda a: {"undertow": wave(a, 12, 0.9, 30, 120), "spear_rain": bolt(a, 5, 0.75, 28, 90, rng=36),
                                       "drown_cloud": cloud(a, "minecraft:mining_fatigue", 7, 26, 160, 100, 1), "surge": lightning(a, 4, 0.9, 36, 150)},
                        ph=(["undertow", "spear_rain"], ["undertow", "spear_rain", "drown_cloud"], ["undertow", "spear_rain", "drown_cloud", "surge"])),
    "foundry_sovereign": dict(atk=lambda a: {"press": slam(a, 8, 1.1, 38, 90), "slag_volley": bolt(a, 5, 0.8, 30, 95, fire=True, rng=36),
                                             "assemble": summon(a, "minecraft:iron_golem", 2, 4, 50, 300), "overclock": roar(a, 16, "minecraft:weakness", 140, 1, 34, 200),
                                             "pylon_arc": lightning(a, 5, 0.9, 38, 140)},
                              ph=(["press", "slag_volley"], ["press", "slag_volley", "assemble", "pylon_arc"], ["press", "slag_volley", "assemble", "pylon_arc", "overclock"])),
    "mist_weaver": dict(atk=lambda a: {"web_snare": cloud(a, "minecraft:slowness", 8, 22, 140, 120, 3), "pounce": leap(a, 6, 1.1, 26, 100),
                                       "thread_bolt": bolt(a, 3, 0.8, 24, 85, effect="minecraft:poison", rng=34), "brood": summon(a, "minecraft:cave_spider", 4, 8, 40, 220)},
                        ph=(["pounce", "thread_bolt"], ["pounce", "thread_bolt", "web_snare"], ["pounce", "thread_bolt", "web_snare", "brood"])),
    "ash_seraph": dict(atk=lambda a: {"cinder_fan": bolt(a, 6, 0.7, 26, 80, fire=True, rng=36), "scorch_ring": wave(a, 12, 0.9, 32, 120),
                                      "smoulder": cloud(a, "minecraft:blindness", 8, 26, 160, 80, 0), "pyre_strike": lightning(a, 4, 1.0, 36, 130)},
                       ph=(["cinder_fan", "scorch_ring"], ["cinder_fan", "scorch_ring", "smoulder"], ["cinder_fan", "scorch_ring", "smoulder", "pyre_strike"]),
                       fire_immune=True),
    "dusk_wyrm": dict(atk=lambda a: {"dive": charge(a, 1.2, 20, 90, 16), "gloom_breath": cloud(a, "minecraft:darkness", 9, 28, 150, 140, 0),
                                     "wing_gale": wave(a, 14, 0.9, 30, 110), "night_bolt": bolt(a, 5, 0.85, 26, 85, effect="minecraft:wither", rng=40), "eclipse": roar(a, 18, "minecraft:blindness", 140, 0, 36, 220)},
                      ph=(["dive", "night_bolt"], ["dive", "night_bolt", "wing_gale", "gloom_breath"], ["dive", "night_bolt", "wing_gale", "gloom_breath", "eclipse"])),
    "rootbreaker": dict(atk=lambda a: {"maul": slam(a, 7, 1.2, 30, 85), "stampede": charge(a, 1.3, 20, 90, 18), "thorn_burst": bolt(a, 6, 0.7, 26, 85, effect="minecraft:poison", rng=32),
                                       "quake": wave(a, 13, 1.0, 36, 130), "sprout": summon(a, "minecraft:vindicator", 3, 6, 44, 240)},
                        ph=(["maul", "stampede"], ["maul", "stampede", "thorn_burst", "quake"], ["maul", "stampede", "thorn_burst", "quake", "sprout"])),
    "last_wheel": dict(atk=lambda a: {"spoke_cut": slam(a, 8, 1.2, 26, 75), "turn": charge(a, 1.3, 18, 80, 18), "age_bolt": bolt(a, 7, 0.8, 24, 80, rng=40),
                                      "season": cloud(a, "minecraft:wither", 9, 24, 140, 120, 1), "recall": summon(a, "minecraft:vindicator", 3, 6, 40, 220),
                                      "stop_time": roar(a, 20, "minecraft:slowness", 160, 2, 40, 240), "year_end": lightning(a, 6, 1.1, 36, 120)},
                       ph=(["spoke_cut", "turn", "age_bolt"], ["spoke_cut", "turn", "age_bolt", "season", "recall"],
                           ["spoke_cut", "turn", "age_bolt", "season", "recall", "stop_time", "year_end"])),
}
LOOT_DROP = {   # signature drop per boss: existing items only; new materials arrive with the worldgen module (see docs/ASCENDANT.md)
    "antlered_hollow": "minecraft:netherite_scrap", "cauldron_heart": "minecraft:echo_shard", "tide_reaver": "minecraft:heart_of_the_sea",
    "foundry_sovereign": "minecraft:netherite_ingot", "mist_weaver": "minecraft:breeze_rod", "ash_seraph": "minecraft:blaze_rod",
    "dusk_wyrm": "minecraft:nether_star", "rootbreaker": "minecraft:resin_brick", "last_wheel": "minecraft:enchanted_golden_apple"}

def texture(kind, rampkey, rnd):
    folder, lo, mid, hi = RAMP[rampkey]
    f = os.path.join(VAN, folder, folder + ".png")
    img = Image.open(f if os.path.exists(f) else os.path.join(VAN, f"_ao_{folder}.png")).convert("RGBA")
    a = np.asarray(img).astype(np.float32) / 255.0
    l = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    t = ((l - l.min()) / max(1e-4, l.max() - l.min()))[..., None]
    lo, mid, hi = (np.array(c, np.float32) for c in (lo, mid, hi))
    c = np.where(t < .5, lo + (mid - lo) * t * 2, mid + (hi - mid) * (t - .5) * 2)
    h, w = l.shape
    c = np.clip(c + (np.array([[rnd.random() for _ in range(w)] for _ in range(h)], np.float32) - .5)[..., None] * .10, 0, 1)
    return Image.fromarray((np.dstack([c, a[..., 3]]) * 255).astype(np.uint8), "RGBA"), mid

def icon(path, body, rim, trophy):
    from PIL import ImageDraw
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if not trophy:
        d.ellipse((3, 1, 12, 14), fill=rim); d.ellipse((4, 2, 11, 13), fill=body)
    else:
        d.ellipse((2, 2, 13, 13), fill=rim); d.ellipse((3, 3, 12, 12), fill=body)
        d.rectangle((5, 6, 6, 7), fill=rim); d.rectangle((9, 6, 10, 7), fill=rim); d.rectangle((6, 10, 9, 11), fill=rim)
    os.makedirs(os.path.dirname(path), exist_ok=True); im.save(path)

hexc = lambda c: tuple(int(v * 255) for v in c)
index = R(os.path.join(DA, "boss_index.json"))
lang = R(os.path.join(AS, "lang/en_us.json"))
gates = R(os.path.join(ROOT, "age_gates.json"))
names = R(os.path.join(ROOT, "names_map.json"))
codex = R(os.path.join(ROOT, "codex/bosses_handbook.json"))
new_ids, items = [], []

for (bid, words, en, kind, rk, scale, age, tier, bar) in SPEC:
    G["DMG"][age] = G["DMG"][age]; hm, dm = TIER_M[tier]
    a = age
    name = nm(*words)
    atk = KIT[bid]["atk"](a)
    ph = KIT[bid]["ph"]
    n_ph = len(ph)
    ats = (1.0, 0.65, 0.3) if n_ph == 3 else (1.0, 0.7, 0.4, 0.15)
    prof = {
        "id": bid, "name": name, "name_en": en, "age": age, "tier": f"ascendant_{tier}",
        "own": {"kind": kind, "scale": scale, "hp": int(G["HP"][age] * hm), "damage": round(G["DMG"][age] * dm), "armor": 16 + 2 * tier,
                "speed": 0.30, "knockback_resistance": 1.0, "follow_range": 56, "fire_immune": bool(KIT[bid].get("fire_immune", False))},
        "bar": {"color": bar, "overlay": "notched_12"},
        "scaling": {"hp_per_age": 0.22, "damage_per_age": 0.1, "hp_per_extra_player": 0.5, "max_age_steps": 4},
        "arena": {"radius": 32, "lock": True, "leash": True, "burn": round(G["DMG"][age] * dm * 0.5, 1)},
        "max_hit_fraction": 0.06,
        "respawn": {"mode": "cooldown", "ticks": 96000},
        "hostile": True, "xp": 1500 * tier + 1000, "equipment": {}, "attacks": atk,
        "phases": phases((ats[0], 1.0, 1.0, 1.0, ph[0]),
                         (ats[1], 1.12, 1.15, 0.85, ph[1], {"invuln": 40}),
                         (ats[2], 1.25, 1.3, 0.7, ph[2], {"invuln": 40})),
        "loot": [L(LOOT_DROP[bid], 1, 2 + tier, age, 0.5 + 0.1 * tier, 0), L("minecraft:diamond", 4, 10, 6, 1.0, 2),
                 L("minecraft:netherite_scrap", 2 * tier, 5 * tier, 7, 1.0, 1), L("minecraft:experience_bottle", 6, 14, 7, 1.0, 2)],
        "structure": None, "mythic": False, "entity": f"{NS}:{bid}", "creature_id": None,
        "summon": {"rite": "ascendant_altar", "requires_kills": [s[0] for s in SPEC if s[7] == tier - 1] if tier > 1 else []},
    }
    W(os.path.join(DA, "boss", bid + ".json"), prof)
    tex, mid = texture(kind, rk, random.Random(bid))
    os.makedirs(os.path.join(AS, "textures/entity"), exist_ok=True)
    tex.save(os.path.join(AS, "textures/entity", bid + ".png"))
    body, rim = hexc(mid), hexc(RAMP[rk][1])
    icon(os.path.join(AS, "textures/item", bid + "_spawn_egg.png"), body, rim, False)
    icon(os.path.join(AS, "textures/item", bid + "_trophy.png"), hexc(RAMP[rk][3]), rim, True)
    for it in ("spawn_egg", "trophy"):
        W(os.path.join(AS, "items", f"{bid}_{it}.json"), {"model": {"type": "minecraft:model", "model": f"{NS}:item/{bid}_{it}"}})
        W(os.path.join(AS, "models/item", f"{bid}_{it}.json"), {"parent": "minecraft:item/generated", "textures": {"layer0": f"{NS}:item/{bid}_{it}"}})
    lang.update({f"entity.{NS}.{bid}": name, f"boss.{NS}.{bid}": name, f"item.{NS}.{bid}_spawn_egg": name, f"item.{NS}.{bid}_trophy": "Kuochbuoda " + name})
    names[name] = en
    if bid not in index: index.append(bid)
    gates["entities"][f"{NS}:{bid}"] = ROM[age]
    gates["items"][f"{NS}:{bid}_trophy"] = gates["items"][f"{NS}:{bid}_spawn_egg"] = ROM[age]
    items.append({"id": f"{NS}:{bid}_trophy", "name": name, "age": ROM[age], "text": ""})
    new_ids.append((bid, tier, age, name))

W(os.path.join(DA, "boss_index.json"), index)
W(os.path.join(AS, "lang/en_us.json"), lang)
W(os.path.join(ROOT, "age_gates.json"), gates)
W(os.path.join(ROOT, "names_map.json"), names)
codex["chapters"] = [c for c in codex["chapters"] if not c["tier"].startswith("ascendant")]
for t, label in ((1, "Age VII"), (2, "Rodos I"), (3, "Rodos II")):
    codex["chapters"].append({"tier": f"ascendant_{t}", "name": "Ascendant " + "I" * t, "age": "VII" if t == 1 else "Rodos",
        "text": f"Post-endgame bosses, {label}. Each is summoned at an Ascendant altar and needs the previous tier beaten.",
        "items": [i for i, (b, tt, _, _) in zip(items, new_ids) if tt == t]})
W(os.path.join(ROOT, "codex/bosses_handbook.json"), codex)

# ---- boss rush: ordered gauntlet over every boss, no healing between, shared arena at the player's start, rewards by tier
rush_order = [b for b, _, _, _ in new_ids]
W(os.path.join(DA, "rush.json"), {
    "_doc": "Boss rush: bosses fight one after another in one arena; fallen players spectate until the wave ends. Read by the rush controller; "
            "every id is a boss profile. Gated by Age (VII) and by having beaten every Ascendant I boss once.",
    "id": f"{NS}:ascendant_rush", "min_age": 7, "requires_kills": [b for b, t, _, _ in new_ids if t == 1],
    "arena": {"radius": 40, "lock": True, "leash": True, "between_ticks": 200, "heal_between": False, "disable_potions": False},
    "order": ["tribal_chief", "stone_colossus", "bronze_warking", "iron_walker", "steel_marshal", "ceramic_warlord"] + rush_order,
    "scale": {"hp": 0.75, "damage": 0.9, "note": "base bosses scale to the Ascendant gauntlet; Ascendant bosses at their own stats"},
    "rewards": [{"after": 6, "item": "diaithirbosses:champion_token", "count": 8},
                {"after": 9, "item": "minecraft:netherite_ingot", "count": 4}, {"after": 12, "item": "minecraft:nether_star", "count": 1},
                {"after": 15, "item": "diaithirbosses:rush_laurel", "count": 1}],
    "leaderboard": "scoreboard:rush_best_seconds"})

# ---- difficulty modes: world-level multipliers on every boss (per world, chosen at the altar with a Mode Stone, can only go up)
W(os.path.join(DA, "difficulty.json"), {
    "_doc": "Boss difficulty modes. Multipliers apply to hp, damage and attack tempo of every boss profile and to Champion elite chance. "
            "Raised, never lowered, once chosen; drops and XP scale with the mode. Optional systems arrive as quests, so a mode is a quest reward, not a switch.",
    "modes": [
        {"id": "standard", "hp": 1.0, "damage": 1.0, "cooldown": 1.0, "elite_chance": 1.0, "loot": 1.0, "xp": 1.0, "quest": None},
        {"id": "relentless", "hp": 1.4, "damage": 1.25, "cooldown": 0.9, "elite_chance": 1.5, "loot": 1.25, "xp": 1.5, "quest": "ascendant/mode_relentless"},
        {"id": "merciless", "hp": 2.0, "damage": 1.6, "cooldown": 0.8, "elite_chance": 2.0, "loot": 1.6, "xp": 2.0, "no_regen_in_arena": True, "quest": "ascendant/mode_merciless"},
        {"id": "ordeal", "hp": 2.8, "damage": 2.2, "cooldown": 0.7, "elite_chance": 3.0, "loot": 2.2, "xp": 3.0, "no_regen_in_arena": True,
         "one_life_per_attempt": True, "quest": "ascendant/mode_ordeal"}]})

# ---- global events: bosses listen to and fire Global Events (#111); format per plans/INTEGRATION.md section 5
W(os.path.join(DA, "diaithir_events.json"), {
    "_doc": "Ascendant bosses and Global Events. 'listens' modify spawn/altar rules while the event runs; 'fires' announce results on the bus.",
    "listens": {"blood_moon": {"effect": "respawn_ticks_x", "value": 0.5}, "eclipse": {"effect": "boss_hp_x", "value": 1.1, "bosses": ["dusk_wyrm"]},
                "storm": {"effect": "boss_damage_x", "value": 1.1, "bosses": ["tide_reaver", "ash_seraph"]},
                "calendar_year_changed": {"effect": "reset_respawn_cooldown"}},
    "fires": {"ascendant_boss_defeated": {"carries": ["boss", "tier", "players", "year"]}, "boss_rush_cleared": {"carries": ["players", "seconds", "mode", "year"]},
              "ascendant_mode_raised": {"carries": ["mode", "year"]}}})

# ---- quests (Codex Quests tab): optional systems reach players as quests
def Q(qid, title, desc, after, kind, **kw): return dict(id=f"ascendant/{qid}", title=title, text=desc, after=after, kind=kind, **kw)
W(os.path.join(DA, "quests/ascendant.json"), {"tab": "Bosses", "quests": [
    Q("rite", "Raise the Ascendant altar", "Build an Ascendant altar from refined metal and carved stone in a cleared arena of radius 32.", ["boss_altar"], "build", age="VII"),
    Q("tier1", "Ascendant I", "Defeat Antlered Hollow, Cauldron-Heart and Tide Reaver (any order).", ["ascendant/rite"], "kill_all", bosses=[b for b, t, _, _ in new_ids if t == 1]),
    Q("tier2", "Ascendant II", "Defeat Foundry Sovereign, Mist Weaver and Ash Seraph.", ["ascendant/tier1"], "kill_all", bosses=[b for b, t, _, _ in new_ids if t == 2]),
    Q("tier3", "Ascendant III", "Defeat Dusk Wyrm, Rootbreaker and The Last Wheel.", ["ascendant/tier2"], "kill_all", bosses=[b for b, t, _, _ in new_ids if t == 3]),
    Q("rush", "The Gauntlet", "Clear the boss rush once.", ["ascendant/tier1"], "event", event="boss_rush_cleared"),
    Q("mode_relentless", "Relentless", "Win any Ascendant I fight, then take the first Mode Stone.", ["ascendant/tier1"], "reward", mode="relentless"),
    Q("mode_merciless", "Merciless", "Clear the Gauntlet on Relentless.", ["ascendant/rush"], "reward", mode="merciless"),
    Q("mode_ordeal", "Ordeal", "Beat The Last Wheel on Merciless.", ["ascendant/tier3"], "reward", mode="ordeal")]})
print("ok", len(new_ids), "bosses;", ", ".join(n for _, _, _, n in new_ids))
