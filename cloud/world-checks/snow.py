"""Snowline check: snow cover fraction by elevation band vs the Age I line (EraMath.age1SnowlineMeters)."""
import json, sys
import numpy as np
from PIL import Image
from sites import lat_of_z, S as WS
ICE = np.array(Image.open("jar/data/tellus/diaithir/ice_thickness.png"))

def ice_m(x, z):
    lat, lon = np.degrees(np.arctan(np.sinh(-z * WS / (111319.49166666667 * 180 / np.pi)))), x * WS / 111319.49166666667
    return ICE[((90 - lat) / 0.05).astype(int).clip(0, 3599), ((lon + 180) / 0.05).astype(int).clip(0, 7199)]
SEA, VS = 200, 5
LAT = [0, 10, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90]
N = [4700, 4800, 5200, 5300, 5100, 4500, 3800, 3000, 2600, 2000, 1500, 1000, 600, 300, 100, 0]
S = [4700, 5000, 5600, 5800, 5200, 4200, 2000, 1500, 1200, 900, 500, 200, 0, 0, 0, 0]

def line(lat):
    return max(0.0, float(np.interp(abs(lat), LAT, N if lat >= 0 else S)) - 800)

def report(name, files):
    cols = [c for f in files for c in json.load(open(f))["cols"]]
    SNOWY = {"minecraft:" + b for b in ("snowy_plains", "snowy_taiga", "snowy_slopes", "grove", "ice_spikes", "frozen_peaks", "snowy_beach")}
    snowy_biome = sum(1 for c in cols if c[2] > SEA and c[7] in SNOWY)
    a = np.array([(c[0], c[1], c[2], c[4]) for c in cols if c[2] > SEA and c[7] not in SNOWY], dtype=float)
    iced = ice_m(a[:, 0], a[:, 1]) > 0
    ice_cols = int(iced.sum()); a = a[~iced]
    if not len(a):
        return {"site": name, "land_cols": 0, "ice_sheet_cols": ice_cols, "snowy_biome_cols": snowy_biome, "pass": None, "note": "all columns under the 15 ka ice sheet"}
    x, z, g, snow = a.T
    m = (g - SEA) * VS; L = line(lat_of_z(float(np.median(z))))
    rel = m - L
    bands = {}
    for lo in range(-3000, 5000, 250):
        sel = (rel >= lo) & (rel < lo + 250)
        if sel.sum() >= 50:
            bands[f"{lo:+d}..{lo+250:+d} m"] = [int(sel.sum()), round(float(snow[sel].mean()), 3)]
    above, below = snow[rel >= 200].mean() if (rel >= 200).any() else None, snow[rel <= -300].mean() if (rel <= -300).any() else None
    ok = above is not None and below is not None and above >= 0.5 and below <= 0.05
    return {"site": name, "lat": round(lat_of_z(float(np.median(z))), 2), "line_m": round(L), "land_cols": len(a), "ice_sheet_cols": ice_cols,
            "elev_m": [int(m.min()), int(m.max())], "snow_above_line+200": None if above is None else round(float(above), 3),
            "snow_below_line-300": None if below is None else round(float(below), 3), "pass": bool(ok), "bands": bands}

if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(json.dumps(report(s, [f"out_{s}.json", f"out_t_{s}.json"])))
