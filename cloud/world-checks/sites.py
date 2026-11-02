import math
R = 111319.49166666667 * 180 / math.pi
S = 5
SITES = {"alps_montblanc": (45.832, 6.865), "himalaya_everest": (27.988, 86.925), "andes_aconcagua": (-32.653, -70.011),
         "scotland_bennevis": (56.797, -5.004), "kilimanjaro": (-3.067, 37.355), "rwenzori": (0.386, 29.872),
         "paris_lowland": (48.85, 2.35)}
HALF = 10  # chunks each side
def center(la, lo):
    return round(lo * 111319.49166666667 / S), round(-R * math.log(math.tan(math.pi / 4 + math.radians(la) / 2)) / S)
def lat_of_z(z):
    return math.degrees(math.atan(math.sinh(-z * S / R)))
def box(name):
    x, z = center(*SITES[name]); cx, cz = x >> 4, z >> 4
    return cx - HALF, cz - HALF, cx + HALF - 1, cz + HALF - 1

# peak -> low town, for snowline transects
TRANSECTS = {"alps_montblanc": ((45.832, 6.865), (45.923, 6.869)), "himalaya_everest": ((27.988, 86.925), (27.687, 86.731)),
             "andes_aconcagua": ((-32.653, -70.011), (-32.826, -69.92)), "scotland_bennevis": ((56.797, -5.004), (56.82, -5.105)),
             "kilimanjaro": ((-3.067, 37.355), (-3.35, 37.34)), "rwenzori": ((0.386, 29.872), (0.18, 30.08))}
def transect_chunks(name, width=2):
    (a, b) = TRANSECTS[name]
    (xa, za), (xb, zb) = center(*a), center(*b)
    n = max(abs(xb - xa), abs(zb - za)) // 8 + 1
    out = set()
    for i in range(n + 1):
        cx, cz = int(xa + (xb - xa) * i / n) >> 4, int(za + (zb - za) * i / n) >> 4
        out |= {(cx + dx, cz + dz) for dx in range(width) for dz in range(width)}
    return sorted(out)
