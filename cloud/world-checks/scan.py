"""Scan Tellus region files: per-column ground Y, snow cover, bedrock floor, and every *_ore block position."""
import io, json, struct, sys, zlib
from pathlib import Path
import nbtlib, numpy as np

MIN_Y = -2032
SKIP = {"minecraft:air", "minecraft:cave_air", "minecraft:void_air"}
SNOW = {"minecraft:snow", "minecraft:snow_block", "minecraft:powder_snow"}
COVER = ("leaves", "_log", "mushroom", "flower", "sapling", "bush", "vine", "fern", "kelp", "seagrass", "_wood", "dandelion", "poppy", "tulip", "orchid", "allium", "bluet", "daisy", "cornflower", "lily", "berry", "dead_bush")
NOT_GROUND = SKIP | SNOW | {"minecraft:water", "minecraft:short_grass", "minecraft:tall_grass", "minecraft:fern", "minecraft:large_fern"}

def chunks(region_dir, box):
    x0, z0, x1, z1 = box
    for rx in range(x0 >> 5, (x1 >> 5) + 1):
        for rz in range(z0 >> 5, (z1 >> 5) + 1):
            p = Path(region_dir) / f"r.{rx}.{rz}.mca"
            if not p.exists() or p.stat().st_size == 0:
                continue
            b = p.read_bytes()
            for i in range(1024):
                cx, cz = rx * 32 + i % 32, rz * 32 + i // 32
                off = int.from_bytes(b[i * 4:i * 4 + 3], "big") * 4096
                if not off or not (x0 <= cx <= x1 and z0 <= cz <= z1):
                    continue
                n, c = struct.unpack(">iB", b[off:off + 5])
                raw = b[off + 5:off + 4 + n]
                yield cx, cz, nbtlib.File.parse(io.BytesIO(zlib.decompress(raw) if c == 2 else raw))

def section_blocks(sec):
    bs = sec.get("block_states")
    if bs is None:
        return None, None
    pal = [str(p["Name"]) for p in bs["palette"]]
    if "data" not in bs:
        return pal, np.zeros(4096, np.int64)
    bits = max(4, (len(pal) - 1).bit_length())
    per = 64 // bits
    longs = np.array(bs["data"], dtype=np.int64).view(np.uint64)
    shifts = np.arange(per, dtype=np.uint64) * np.uint64(bits)
    idx = ((longs[:, None] >> shifts) & np.uint64((1 << bits) - 1)).reshape(-1)[:4096]
    return pal, idx.astype(np.int64)  # index = y*256 + z*16 + x

def surface_biomes(nbt, ground):
    out = np.empty(256, object)
    secs = {int(s["Y"]): s for s in nbt["sections"]}
    for k in range(256):
        y = int(ground[k]); sec = secs.get(y >> 4)
        b = sec.get("biomes") if sec is not None else None
        if b is None:
            continue
        pal = [str(p) for p in b["palette"]]
        if "data" not in b:
            out[k] = pal[0]; continue
        bits = (len(pal) - 1).bit_length(); per = 64 // bits
        i = (((y & 15) >> 2) * 4 + ((k // 16) >> 2)) * 4 + ((k % 16) >> 2)
        v = int(b["data"][i // per]) & 0xFFFFFFFFFFFFFFFF
        out[k] = pal[(v >> (i % per * bits)) & ((1 << bits) - 1)]
    return out

def scan(region_dir, box):
    cols, ores = [], []
    for cx, cz, nbt in chunks(region_dir, box):
        if str(nbt.get("Status", "")) not in ("minecraft:full", "full"):
            continue
        top = np.full(256, MIN_Y - 1); ground = np.full(256, MIN_Y - 1); snow = np.zeros(256, bool); tname = np.empty(256, object); floor = np.full(256, MIN_Y)
        secs = sorted(nbt["sections"], key=lambda s: -int(s["Y"]))
        for sec in secs:
            pal, idx = section_blocks(sec)
            if pal is None or all(p in SKIP for p in pal):
                continue
            sy = int(sec["Y"]) * 16
            pal_a = np.array(pal, dtype=object)
            is_solid = np.array([p not in SKIP for p in pal])
            is_snow = np.array([p in SNOW for p in pal])
            is_ground = np.array([p not in NOT_GROUND and not any(w in p for w in COVER) for p in pal])
            grid = idx.reshape(16, 256)
            for ly in range(15, -1, -1):
                row, y = grid[ly], sy + ly
                new_top = is_solid[row] & (top < MIN_Y)
                top[new_top] = y
                tname[new_top] = pal_a[row[new_top]]
                g = is_ground[row] & (ground < MIN_Y)
                ground[g] = y
                snow |= (is_snow[row] & (ground < MIN_Y))
                bed = (pal_a[row] == "minecraft:bedrock") & (floor == MIN_Y)
                floor[bed] = y
            for j, p in enumerate(pal):
                if p.endswith("_ore"):
                    for k in np.nonzero(idx == j)[0]:
                        ores.append((p, int(cx * 16 + k % 16), int(sy + k // 256), int(cz * 16 + (k // 16) % 16)))
        bio = surface_biomes(nbt, ground)
        for k in range(256):
            cols.append((cx * 16 + k % 16, cz * 16 + k // 16, int(ground[k]), int(top[k]), bool(snow[k]), int(floor[k]), str(tname[k]), str(bio[k])))
    return cols, ores

if __name__ == "__main__":
    from sites import box, transect_chunks
    region, name = sys.argv[1], sys.argv[2]
    if name.startswith("t_"):
        ch = transect_chunks(name[2:]); xs, zs = [c[0] for c in ch], [c[1] for c in ch]
        cols, ores = scan(region, (min(xs), min(zs), max(xs), max(zs)))
    else:
        cols, ores = scan(region, box(name))
    json.dump({"cols": cols, "ores": ores}, open(f"out_{name}.json", "w"))
    print(name, len(cols) // 256, "chunks", len(ores), "ore blocks")
