"""B24: turns the Cinderreach level design CSVs into Content/Python/sf_blockout_spec.json for sf_blockout.py.

Only the vertical slice levels (design/levels/cinderreach/01-region-flow.md) are kept. The CSVs give each node a
size, an elevation and links but no floor-plan position, so this lays every level out as a tree from its first node:
the critical path runs forward, side rooms branch left and right, and a level reached by a link from an earlier one
continues from that link. Levels nobody links to start at their world position (data/world/locations.csv).
Map metres: x east, y north. Output is Unreal centimetres, X east and Y south (Y = -north).
"""
import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT.parent
LVL = PLAN / "design/levels/cinderreach"
WORLD = PLAN / "data/world"
OUT = ROOT / "Content/Python/sf_blockout_spec.json"

MAP = "/GF_Cinderreach/Maps/L_Cinderreach_Slice"
SLICE = ["LVL_R1_PRO_BAY9", "LVL_R1_PRO_SPINE", "LVL_R1_RELAY", "LVL_R1_TWN_01", "LVL_R1_POI_30", "LVL_R1_DGN_15",
         "LVL_R1_FB_ASHCOLOSSUS", "LVL_R1_CIT_Z1", "LVL_R1_CIT_Z2", "LVL_R1_CIT_Z3"]
VERTICAL = {"ladder", "lift", "rope", "climb", "mantle", "drop", "down"}
WIDTH = {"squeeze": 2.4, "door": 3.2, "locked": 1.6, "secret": 1.6, "gate": 5.0}
SLAB = 0.5      # thinnest node floor (m)
RAMP = 0.3      # ramp thickness (m)
SLOPE = 1.75    # horizontal metres per metre of rise on a walked link (about 30 degrees)
MARGIN = 20.0   # ground beyond the outermost node (m)
DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def element(token):
    """'shortcut-lift28' -> ('lift', True); 'ladder 6 m' -> ('ladder', False)."""
    t = token.lower().replace("shortcut:", "shortcut-").strip()
    shortcut = t.startswith("shortcut-")
    return re.sub(r"\s*[\d.]+(\s*m)?$", "", t.removeprefix("shortcut-").strip()) or "walk", shortcut


LEVELS = {r["lvl_id"]: r for r in rows(LVL / "levels.csv")}
LOCS = {r["loc_id"]: r for r in rows(WORLD / "locations.csv")}
LOC_LEVEL = {LEVELS[l]["loc_id"]: l for l in SLICE}

NODES = {r["node_id"]: r for r in rows(LVL / "nodes.csv") if r["lvl_id"] in SLICE}
designed = {n["lvl_id"] for n in NODES.values()}
for r in rows(WORLD / "level_nodes.csv"):  # world rows only fill levels the Cinderreach sheets leave empty
    lvl = LOC_LEVEL.get(r["loc_id"])
    if lvl and lvl not in designed:
        NODES[r["node_id"]] = dict(node_id=r["node_id"], lvl_id=lvl, order=r["seq"], name=r["name"],
                                   type=r["role"].upper(), critical=r["critical"], size_m="20 x 20 x 0",
                                   elev_rel_m="0", links="; ".join(f"{e}(walk)" for e in r["exits"].split()),
                                   anchor="")
for n in NODES.values():
    n["w"], n["l"], _ = (float(v) for v in n["size_m"].split(" x "))
    n["elev"] = float(n["elev_rel_m"] or 0)

# Edges: node links, then traversal rows (which label them and add any the links miss).
EDGES = {}
dropped = 0
for n in sorted(NODES.values(), key=lambda n: (SLICE.index(n["lvl_id"]), int(n["order"]))):
    for link in filter(None, (s.strip() for s in n["links"].split(";"))):
        to, kind = re.match(r"(\S+)\((.*)\)", link).groups()
        if to not in NODES:
            dropped += 1
            continue
        if (to, n["node_id"]) not in EDGES:  # a link listed from both ends is one edge
            EDGES.setdefault((n["node_id"], to), dict(kind=kind, label=kind, trv=""))
for t in rows(LVL / "traversal.csv"):
    if t["from_node"] in NODES and t["to_node"] in NODES:
        ab = (t["from_node"], t["to_node"])
        e = EDGES.get(ab[::-1]) or EDGES.setdefault(ab, dict(kind=t["element"]))
        e.update(kind=t["element"], label=f"{t['trv_id']} {t['element']}", trv=t["trv_id"])
for e in EDGES.values():
    e["element"], e["shortcut"] = element(e["kind"])
    e["vertical"] = e["element"] in VERTICAL


# Layout ----------------------------------------------------------------------------------------------------------
pos, base, placed = {}, {}, []  # node -> (cx, cy, dir); level -> base z; rects already used


def rect(n, cx, cy, d):
    hx, hy = (n["l"] / 2, n["w"] / 2) if d[0] else (n["w"] / 2, n["l"] / 2)
    return cx - hx, cy - hy, cx + hx, cy + hy


def free(r):
    return all(r[2] + 2 <= o[0] or o[2] + 2 <= r[0] or r[3] + 2 <= o[1] or o[3] + 2 <= r[1] for o in placed)


def put(nid, cx, cy, d):
    pos[nid] = (cx, cy, d)
    placed.append(rect(NODES[nid], cx, cy, d))


def z(nid):
    n = NODES[nid]
    return base[n["lvl_id"]] + n["elev"]


def level_base(lvl, via=None):
    parent = LEVELS[lvl]["parent"]
    if parent:  # Spine Keep zones share the Citadel's elevation datum
        return float(LOCS[LEVELS[parent]["loc_id"]]["z_m"])
    if via:
        return z(via[0]) - NODES[via[1]]["elev"]
    return float(LOCS[LEVELS[lvl]["loc_id"]]["z_m"])


def gap(e, a, b):
    if e["vertical"]:
        return 1.0
    return max(4.0, abs(z(b) - z(a)) * SLOPE) if e["element"] not in ("door", "locked", "fog") else 2.0


def place_child(parent, child, e, forward):
    if NODES[child]["lvl_id"] not in base:
        base[NODES[child]["lvl_id"]] = level_base(NODES[child]["lvl_id"], (parent, child))
    px, py, pd = pos[parent]
    left, right, back = (-pd[1], pd[0]), (pd[1], -pd[0]), (-pd[0], -pd[1])
    tries = [pd, left, right, back] if forward else [left, right, pd, back]
    pr = rect(NODES[parent], px, py, pd)
    for push in range(0, 400, 10):
        for d in tries:
            reach = (pr[2] - px if d[0] else pr[3] - py) + gap(e, parent, child) + push
            half = NODES[child]["l"] / 2
            cx, cy = px + d[0] * (reach + half), py + d[1] * (reach + half)
            if free(rect(NODES[child], cx, cy, d)):
                put(child, cx, cy, d)
                return
    raise SystemExit(f"no room for {child}")


origin = LOCS[LEVELS[SLICE[0]]["loc_id"]]
first_node = {}
for n in sorted(NODES.values(), key=lambda n: -int(n["order"])):
    first_node[n["lvl_id"]] = n["node_id"]
tree = set()
for lvl in SLICE:
    first = first_node[lvl]
    if first in pos:
        continue
    loc = LOCS[LEVELS[lvl]["loc_id"]]
    base[lvl] = level_base(lvl)
    cx, cy = float(loc["x_m"]) - float(origin["x_m"]), float(loc["y_m"]) - float(origin["y_m"])
    while not free(rect(NODES[first], cx, cy, DIRS[0])):
        cx += 10
    put(first, cx, cy, DIRS[0])
    queue = [first]
    while queue:
        nid = queue.pop(0)
        out = [(b, e) for (a, b), e in EDGES.items() if a == nid and not e["shortcut"]]
        inc = [(a, e) for (a, b), e in EDGES.items() if b == nid and not e["shortcut"]]
        forward = True
        for other, e in out + inc:
            if other in pos:
                continue
            crit = NODES[other]["critical"] == "Y" and forward
            place_child(nid, other, e, crit)
            forward = forward and not crit
            tree.add((nid, other) if (nid, other) in EDGES else (other, nid))
            queue.append(other)
missing = [n for n in NODES if n not in pos]
if missing:
    raise SystemExit(f"unreached nodes: {missing}")


# Actors ----------------------------------------------------------------------------------------------------------
actors = []


def cm(*v):
    return [round(x * 100, 1) for x in v]


def ue(x, y, zz):
    return cm(x, -y, zz - float(origin["z_m"]))


def actor(key, cls, label, folder, loc, rot=(0, 0, 0), scale=(1, 1, 1), **extra):
    actors.append(dict(key=key, cls=cls, label=label, folder=f"Blockout/{folder}", loc=loc,
                       rot=[round(r, 2) for r in rot], scale=[round(s, 3) for s in scale], **extra))


def yaw(d):
    return math.degrees(math.atan2(-d[1], d[0]))


def spread(nid, count, frac):
    """count points on a grid inside the node's floor, frac of its extent."""
    x0, y0, x1, y1 = rect(NODES[nid], *pos[nid])
    cols = math.ceil(math.sqrt(count))
    rws = math.ceil(count / cols)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return [(cx + (x1 - x0) * frac * ((i % cols + 0.5) / cols - 0.5),
             cy + (y1 - y0) * frac * ((i // cols + 0.5) / rws - 0.5)) for i in range(count)]


groups = {}
for nid, n in NODES.items():
    groups.setdefault(n["lvl_id"], []).append(nid)
# One ground slab per connected run of levels (a root level and everything chained from it).
runs, seen = [], set()
for lvl in SLICE:
    if lvl in seen:
        continue
    run = {lvl}
    while True:
        more = {NODES[b]["lvl_id"] for (a, b) in tree if NODES[a]["lvl_id"] in run} - run
        if not more:
            break
        run |= more
    seen |= run
    runs.append(sorted(run, key=SLICE.index))
floor_z = {}
for run in runs:
    ids = [nid for l in run for nid in groups[l]]
    rs = [rect(NODES[i], *pos[i]) for i in ids]
    x0, y0 = min(r[0] for r in rs) - MARGIN, min(r[1] for r in rs) - MARGIN
    x1, y1 = max(r[2] for r in rs) + MARGIN, max(r[3] for r in rs) + MARGIN
    top = min(z(i) for i in ids) - SLAB
    for l in run:
        floor_z[l] = top
    actor(f"GROUND_{run[0]}", "StaticMeshActor", f"Ground {run[0]}", run[0], ue((x0 + x1) / 2, (y0 + y1) / 2, top - 0.5),
          scale=(x1 - x0, y1 - y0, 1), mesh="cube")

for nid, n in NODES.items():
    cx, cy, d = pos[nid]
    lvl = n["lvl_id"]
    top = z(nid)
    bottom = min(floor_z[lvl], top - SLAB)
    across, along = n["w"], n["l"]
    sx, sy = (along, across) if d[0] else (across, along)
    actor(nid, "StaticMeshActor", f"{nid} {n['name']} ({n['type']})", f"{lvl}/Nodes",
          ue(cx, cy, (top + bottom) / 2), scale=(sx, sy, top - bottom), mesh="cube",
          tags=["SfNode", nid, n["type"]])
    actor(f"{nid}_TXT", "TextRenderActor", f"{nid} label", f"{lvl}/Labels", ue(cx, cy, top + 3),
          rot=(0, yaw(d) + 180, 0), text=f"{n['name']} ({n['type']})")
    if n["type"] == "ANCHOR" or n["anchor"]:
        actor(f"{nid}_ANCHOR", "StaticMeshActor", f"Anchor {n['anchor'] or nid}", f"{lvl}/Anchors",
              ue(cx, cy, top + 1.5), scale=(1.5, 1.5, 3), mesh="cylinder", collision=False,
              tags=["SfAnchor", n["anchor"] or nid])

links = 0
for (a, b), e in EDGES.items():
    ax, ay, ad = pos[a]
    bx, by, bd = pos[b]
    za, zb = z(a), z(b)
    lvl = NODES[a]["lvl_id"]
    key = f"LINK_{a}__{b}"
    label = f"{a} > {b} {e['label']}"
    tags = ["SfLink", e["element"]] + ([e["trv"]] if e["trv"] else [])
    links += 1
    if (a, b) not in tree:  # shortcuts and loops: a guide beam centre to centre, no collision
        dx, dy, dz = bx - ax, by - ay, zb - za
        h = math.hypot(dx, dy)
        actor(key, "StaticMeshActor", label, f"{lvl}/Shortcuts", ue((ax + bx) / 2, (ay + by) / 2, (za + zb) / 2 + 1),
              rot=(math.degrees(math.atan2(dz, h)), yaw((dx, dy)), 0), scale=(math.hypot(h, dz), 0.4, 0.4),
              mesh="cube", collision=False, tags=tags + ["shortcut"])
        continue
    ra, rb = rect(NODES[a], ax, ay, ad), rect(NODES[b], bx, by, bd)
    d = (int(math.copysign(1, bx - ax)), 0) if abs(bx - ax) > abs(by - ay) else (0, int(math.copysign(1, by - ay)))
    edge_a = (ra[2] if d[0] > 0 else ra[0], ay) if d[0] else (ax, ra[3] if d[1] > 0 else ra[1])
    edge_b = (rb[0] if d[0] > 0 else rb[2], by) if d[0] else (bx, rb[1] if d[1] > 0 else rb[3])
    mx, my = (edge_a[0] + edge_b[0]) / 2, (edge_a[1] + edge_b[1]) / 2
    if e["vertical"]:
        lo, hi = min(za, zb), max(za, zb)
        actor(key, "StaticMeshActor", label, f"{lvl}/Links", ue(mx, my, (lo + hi) / 2),
              scale=(0.6, 0.6, max(hi - lo, 1)), mesh="cylinder", tags=tags)
        continue
    width = min(WIDTH.get(e["element"], 4.0), NODES[a]["w"], NODES[b]["w"])
    run_m = math.dist(edge_a, edge_b)
    actor(key, "StaticMeshActor", label, f"{lvl}/Links", ue(mx, my, (za + zb) / 2 - RAMP / 2),
          rot=(math.degrees(math.atan2(zb - za, run_m)), yaw(d), 0),
          scale=(math.hypot(run_m, zb - za) + 0.5, width, RAMP), mesh="cube", tags=tags)

spawns = 0
for enc in rows(LVL / "encounters.csv"):
    if enc["node_id"] not in NODES:
        continue
    units = []
    for part in filter(None, (p.strip() for p in enc["actors"].split(";"))):
        act, _, count = part.partition(" x")
        units += [act] * int(count or 1)
    nid = enc["node_id"]
    for i, (act, (x, y)) in enumerate(zip(units, spread(nid, len(units), 0.5)), 1):
        actor(f"{enc['enc_id']}.{i:02d}", "TargetPoint", f"{enc['enc_id']} {act} {i}",
              f"{NODES[nid]['lvl_id']}/Encounters", ue(x, y, z(nid) + 1), rot=(0, yaw(pos[nid][2]) + 180, 0),
              tags=["SfSpawn", enc["enc_id"], act])
    spawns += len(units)

loot = [dict(id=r["loot_id"], node=r["node_id"], ref=r["contents"], qty=r["qty"], how=r["container"], kind="Loot")
        for r in rows(LVL / "loot.csv") if r["node_id"] in NODES]
world_rows = 0
for r in rows(WORLD / "level_placements.csv"):
    node = r["node_id"] if r["node_id"] in NODES else first_node.get(LOC_LEVEL.get(r["loc_id"]))
    if node:
        loot.append(dict(id=r["place_id"], node=node, ref=r["ref"], qty=r["qty"], how=r["container_or_trigger"],
                         kind=r["kind"]))
        world_rows += 1
by_node = {}
for p in loot:
    by_node.setdefault(p["node"], []).append(p)
for nid, items in by_node.items():
    for p, (x, y) in zip(items, spread(nid, len(items), 0.85)):
        tag = "SfLoot" if p["kind"] == "Loot" else "SfSpawn"
        actor(p["id"], "TargetPoint", f"{p['id']} {p['how']} {p['ref']} x{p['qty']}",
              f"{NODES[nid]['lvl_id']}/{'Loot' if p['kind'] == 'Loot' else 'Encounters'}", ue(x, y, z(nid) + 0.5),
              tags=[tag, p["id"], p["ref"]])

start = next((n for n in NODES if NODES[n]["type"] == "START"), None) or next(iter(pos))
sx, sy, sd = pos[start]
actor("PLAYER_START", "PlayerStart", "PlayerStart", "Gameplay", ue(sx, sy, z(start) + 1), rot=(0, yaw(sd), 0))
actor("ENV_SUN", "DirectionalLight", "Sun", "Environment", ue(sx, sy, z(start) + 50), rot=(-40, 135, 0))
actor("ENV_SKYLIGHT", "SkyLight", "SkyLight", "Environment", ue(sx, sy, z(start) + 50))
actor("ENV_ATMOSPHERE", "SkyAtmosphere", "SkyAtmosphere", "Environment", ue(sx, sy, z(start)))

keys = [a["key"] for a in actors]
assert len(keys) == len(set(keys)), "duplicate actor keys"
spec = dict(map=MAP, levels=SLICE, actors=actors)
OUT.write_text(json.dumps(spec, indent=1) + "\n", encoding="utf-8")
print(f"{OUT.relative_to(ROOT)}: {len(SLICE)} levels in {len(runs)} runs, {len(NODES)} nodes, {links} links "
      f"({len(tree)} ramps or climbs, {links - len(tree)} shortcut beams), {dropped} links leave the slice, "
      f"{spawns} enemy spawns, {len(loot)} placements ({world_rows} from data/world), {len(actors)} actors, "
      f"player start at {start}")
