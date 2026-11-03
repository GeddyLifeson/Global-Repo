"""S6873 Adds the Shardfall Gate to diaithir-bosses: lang lines, the Codex quests (quests/gate.json), the handbook chapter, the block texture
and the worldgen structure (a gate court, one rare structure set). Re-runnable; touches only those files. Run from the module root: python3 -I tools/gen_gate.py"""
import gzip, json, math, os, random, struct
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AS, DA = os.path.join(ROOT, "src/main/resources/assets/diaithirbosses"), os.path.join(ROOT, "src/main/resources/data/diaithirbosses")
gate = json.load(open(os.path.join(DA, "gate.json"), encoding="utf8"))
n, secs = len(gate["keystones"]), gate["defend"]["seconds"]

TEXT = {
    "block.diaithirbosses.shardfall_gate": "Shardfall Gate",
    "gate.diaithirbosses.age": "The Gate does not answer yet. Its Age has not come.",
    "gate.diaithirbosses.locked": "The Gate is shut. Beat The Last Wheel and clear the rush first.",
    "gate.diaithirbosses.missing": "%s of %s keystones are in. Still missing: %s.",
    "gate.diaithirbosses.keystone": "A keystone is taken. %s of %s are in.",
    "gate.diaithirbosses.wrong_hour": "The Gate does not answer at this hour. Use it at midnight.",
    "gate.diaithirbosses.hour_done": "The Gate answers. Use it again and hold it for %s seconds.",
    "gate.diaithirbosses.defend_start": "The waves come. Hold the Gate for %s seconds.",
    "gate.diaithirbosses.defend_failed": "The Gate was left alone. Use it again to restart the hold.",
    "gate.diaithirbosses.progress": "%s of %s seconds.",
    "gate.diaithirbosses.opened": "The Shardfall Gate is open.",
    "gate.diaithirbosses.open": "The Shardfall Gate is open.",
}
QUESTS = [
    ("gate/price", "The Gate's price", "Beat The Last Wheel and clear the boss rush. The Gate stays shut until both are done.", ["ascendant/tier3", "ascendant/rush"], "event", "boss_rush_cleared"),
    ("gate/keystones", "The keystones", f"The Gate takes {n} keystones, one for each system of the world. Sneak-use the Gate with an item to give it; some are known to it already. Use the Gate bare-handed to see what is missing.", ["gate/price"], "event", "gate_keystones_complete"),
    ("gate/hour", "The hour", "Use the Gate at midnight.", ["gate/keystones"], "event", "gate_hour_done"),
    ("gate/hold", "The hold", f"Hold the Gate for {secs} seconds against the waves. Do not leave it.", ["gate/hour"], "event", "gate_hold_done"),
    ("gate/open", "The Shardfall Gate", "The Gate is open.", ["gate/hold"], "event", "shardfall_gate_open"),
]

def rw(path, fn):
    d = json.load(open(path, encoding="utf8")) if os.path.exists(path) else None
    d = fn(d)
    json.dump(d, open(path, "w", encoding="utf8"), indent=1, ensure_ascii=False)

rw(os.path.join(AS, "lang/en_us.json"), lambda d: {**d, **TEXT})
rw(os.path.join(DA, "quests/gate.json"), lambda d: {"tab": "Bosses", "quests": [
    {"id": i, "title": t, "text": x, "after": a, "kind": k, "event": e, "age": "RODOS"} for i, t, x, a, k, e in QUESTS]})
def codex(d):
    d["chapters"] = [c for c in d["chapters"] if c.get("tier") != "gate"]
    d["chapters"].append({"tier": "gate", "name": "The Shardfall Gate", "age": "RODOS", "text": " ".join(q[2] for q in QUESTS[:4]), "items": [
        {"id": "diaithirbosses:shardfall_gate", "name": "Shardfall Gate", "age": "RODOS", "text": ""}]})
    return d
rw(os.path.join(ROOT, "codex/bosses_handbook.json"), codex)


# ---- block texture: dark stone with a lit shard-shaped opening (own pixels, nothing copied)
def texture(path):
    rnd = random.Random("shardfall_gate")
    im = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            v = 38 + rnd.randint(-6, 6)
            edge = min(x, y, 15 - x, 15 - y)
            c = (v + 14, v + 14, v + 22) if edge == 0 else (v, v, v + 8)
            dx, dy = abs(x - 7.5), abs(y - 7.5)
            if dx + dy * 0.55 < 3.2:           # the opening
                t = 1 - (dx + dy * 0.55) / 3.2
                c = (int(90 + 150 * t), int(180 + 70 * t), 255)
            elif dx + dy * 0.55 < 4.4:         # its rim
                c = (70, 90, 130)
            im.putpixel((x, y), c + (255,))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)


# ---- structure: a round court of dark brick with eight pillars, the Gate in the middle
def _s(v):
    b = v.encode("utf8")
    return struct.pack(">H", len(b)) + b

TAG = {"int": 3, "str": 8, "list": 9, "compound": 10}

def nbt(t, v):
    if t == "int": return struct.pack(">i", v)
    if t == "str": return _s(v)
    if t == "list":
        et, items = v
        return bytes([TAG[et]]) + struct.pack(">i", len(items)) + b"".join(nbt(et, i) for i in items)
    out = b""
    for k, (tt, vv) in v.items(): out += bytes([TAG[tt]]) + _s(k) + nbt(tt, vv)
    return out + b"\x00"

def court(path, radius=10):
    pal, blocks = {}, []
    def st(name, props=None):
        k = (name, tuple(sorted((props or {}).items())))
        pal.setdefault(k, len(pal))
        return pal[k]
    size, height, c = radius * 2 + 1, 10, radius
    rnd = random.Random("shardfall_gate_court")
    for x in range(size):
        for z in range(size):
            d = math.hypot(x - c, z - c)
            if d > radius + 0.3: continue
            for y in (0, 1): blocks.append(((x, y, z), st("minecraft:polished_blackstone_bricks"), None))
            top = "minecraft:chiseled_polished_blackstone" if abs(d - radius * 0.5) < 0.6 else (
                "minecraft:cracked_polished_blackstone_bricks" if rnd.random() < 0.15 else "minecraft:polished_blackstone_bricks")
            blocks.append(((x, 2, z), st(top), None))
            for y in range(3, height):
                if (x, y, z) != (c, 3, c): blocks.append(((x, y, z), st("minecraft:air"), None))  # air is placed after solid blocks and would erase the Gate
    for k in range(8):
        a = k * math.tau / 8
        px, pz = round(c + math.cos(a) * (radius - 1)), round(c + math.sin(a) * (radius - 1))
        for y in range(3, 8): blocks.append(((px, y, pz), st("minecraft:polished_blackstone_brick_wall"), None))
        blocks.append(((px, 8, pz), st("minecraft:soul_lantern", {"hanging": "false"}), None))
    blocks.append(((c, 3, c), st(f"{NS}:shardfall_gate"), None))
    palette = [None] * len(pal)
    for (name, props), i in pal.items():
        e = {"Name": ("str", name)}
        if props: e["Properties"] = ("compound", {k: ("str", v) for k, v in props})
        palette[i] = e
    root = {"DataVersion": ("int", 4790), "size": ("list", ("int", [size, height, size])),
            "palette": ("list", ("compound", palette)), "entities": ("list", ("compound", [])),
            "blocks": ("list", ("compound", [{"pos": ("list", ("int", list(p))), "state": ("int", s)} for p, s, _ in blocks]))}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wb") as f: f.write(bytes([10]) + _s("") + nbt("compound", root))

NS = "diaithirbosses"
texture(os.path.join(AS, "textures/block/shardfall_gate.png"))
court(os.path.join(DA, "structure/shardfall_gate.nbt"))
def w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf8"), indent=1)
w(os.path.join(DA, "worldgen/template_pool/shardfall_gate/start.json"), {"fallback": "minecraft:empty", "elements": [{"weight": 1, "element": {
    "element_type": "minecraft:single_pool_element", "location": f"{NS}:shardfall_gate", "processors": "minecraft:empty", "projection": "rigid"}}]})
w(os.path.join(DA, "worldgen/structure/shardfall_gate.json"), {"type": "minecraft:jigsaw", "biomes": f"#{NS}:has_shardfall_gate", "step": "surface_structures",
    "spawn_overrides": {}, "terrain_adaptation": "beard_thin", "start_pool": f"{NS}:shardfall_gate/start", "size": 1, "start_height": {"absolute": 0},
    "project_start_to_heightmap": "WORLD_SURFACE_WG", "max_distance_from_center": 80, "use_expansion_hack": False})
w(os.path.join(DA, "worldgen/structure_set/shardfall_gate.json"), {"structures": [{"structure": f"{NS}:shardfall_gate", "weight": 1}],
    "placement": {"type": "minecraft:random_spread", "spacing": 96, "separation": 40, "salt": 6873}})
w(os.path.join(DA, "tags/worldgen/biome/has_shardfall_gate.json"), {"values": [{"id": "#minecraft:is_overworld", "required": False}]})
