"""Top-down PNG per site: snow white, water blue, land shaded by elevation, ice-sheet columns tinted; 1 px = 4x4 blocks."""
import json, sys
import numpy as np
from PIL import Image
from snow import ice_m
K = 4

def render(name, files, out):
    SNOWY = {"minecraft:" + b for b in ("snowy_plains", "snowy_taiga", "snowy_slopes", "grove", "ice_spikes", "frozen_peaks", "snowy_beach")}
    cols = np.array([(c[0], c[1], c[2], c[4], c[6] == "minecraft:water", c[7] in SNOWY) for f in files for c in json.load(open(f))["cols"]], dtype=float)
    x, z, g, snow, water, sb = cols.T
    x0, z0 = x.min(), z.min()
    W, H = int((x.max() - x0) // K) + 1, int((z.max() - z0) // K) + 1
    img = np.zeros((H, W, 4), np.uint8)
    t = np.clip((g - g.min()) / max(1, np.ptp(g)), 0, 1)
    rgb = np.stack([70 + 110 * t, 80 + 70 * t, 50 + 50 * t], 1)
    iced = ice_m(x, z) > 0
    rgb[snow > 0] = (250, 250, 250)  # snowline snow
    rgb[(snow > 0) & (sb > 0)] = (150, 200, 255)  # snow from a snowy biome
    rgb[(snow > 0) & iced] = (90, 220, 220)  # 15 ka ice sheet
    rgb[water > 0] = (50, 100, 200)
    px, pz = ((x - x0) // K).astype(int), ((z - z0) // K).astype(int)
    img[pz, px, :3] = rgb.astype(np.uint8); img[pz, px, 3] = 255
    im = Image.fromarray(img, "RGBA")
    if max(im.size) > 900:
        im.thumbnail((900, 900), Image.NEAREST)
    im.save(out)
    return {"elev_m": [int((g.min() - 200) * 5), int((g.max() - 200) * 5)]}

if __name__ == "__main__":
    for s in sys.argv[1:]:
        fs = [f for f in (f"out_{s}.json", f"out_t_{s}.json") if __import__("os").path.exists(f)]
        print(s, render(s, fs, f"map_{s}.png"))
