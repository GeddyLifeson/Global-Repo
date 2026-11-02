import csv, os, math
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def write(name, header, rows):
    p = os.path.join(OUT, name)
    if 'Startup frames' in header and 'Attack type' not in header:
        # Visual Bible / art notes: openers and standalone attacks wind up >= 12 frames; combo follow-ups >= 8.
        # Each combo is one row timed from its opener, so no row is a follow-up yet; a row named '... (follow-up)' would be.
        n = 2; header = header[:n + 1] + ['Attack type'] + header[n + 1:]
        kind = lambda nm: 'Follow-up' if 'follow-up' in str(nm).lower() else 'Opener' if 'combo' in str(nm).lower() else 'Standalone'
        rows = [r[:n + 1] + [kind(r[n])] + r[n + 1:] for r in rows]
        i = header.index('Startup frames')
        rows = [r[:i] + [max(8 if r[n + 1] == 'Follow-up' else 12, r[i]) if isinstance(r[i], (int, float)) else r[i]] + r[i + 1:] for r in rows]
    with open(p, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    print(f'{name}: {len(rows)} rows')
ELEMENTS = ['Ember', 'Storm', 'Hollow', 'Frost', 'Bloom', 'Iron']
OPPOSITE = {'Ember': 'Frost', 'Frost': 'Ember', 'Storm': 'Iron', 'Iron': 'Storm', 'Hollow': 'Bloom', 'Bloom': 'Hollow'}
PHYS = ['Slash', 'Pierce', 'Blunt', 'Bullet']
REGIONS = [  # id, name, band lo, band hi, element tint
    ('R1', 'Cinderreach', 1, 12, 'Ember'), ('R2', 'Saltmere', 10, 22, 'Storm'),
    ('R3', 'Thornwood', 20, 34, 'Bloom'), ('R4', 'Glasswaste', 32, 46, 'Iron'),
    ('R5', 'Rimefall', 44, 58, 'Frost'), ('R6', 'Hollowdeep', 55, 70, 'Hollow'),
    ('RQ', 'The Quiet', 68, 80, 'Hollow'), ('RU', 'The Undervault', 30, 70, 'Iron'),
    ('RH', 'Lantern Hold', 1, 80, 'None')]
REG = {r[0]: r for r in REGIONS}
# Shared stat formulas (also listed in derived_formulas.csv)
def player_level_cost(L):          # FRM_EMBER_LEVELCOST
    return int(0.02 * L**3 + 3 * L**2 + 100 * L + 500)
def enemy_hp(L, mult):             # FRM_ENEMY_HP
    return round(mult * (60 + 18 * L))
def enemy_dmg(L, mult):            # FRM_ENEMY_DMG
    return round(mult * (8 + 1.6 * L))
def ember_drop(L, mult):           # FRM_EMBER_DROP
    return round(0.16 * mult * (10 + 1.5 * L**1.5))   # DR-001 x0.2, then B08 SIM-01 x0.16
def boss_hp(L, mult):              # FRM_BOSS_HP
    return int(round(mult * (400 + 140 * L), -1))
def boss_dmg(L, mult):             # FRM_BOSS_DMG
    return round(mult * (20 + 4 * L))
def defense_at(L, mult):           # FRM_ENEMY_DEF
    return round(mult * (10 + 2 * L))

# DR-SYS-010 rev 2: absolute HP / Ward / damage per level for the 24 base and leader enemies (copied from design/systems/enemy_curve_target.csv).
# Levels outside a row's band follow the formula, scaled to meet the nearest target level, so HP still rises every level.
import csv as _csv
TARGET = {}
for _r in _csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'enemy_curve_target.csv'))):
    TARGET[(_r['ACT_ID'], int(_r['Level']))] = (int(_r['HP_target']), int(_r['Ward_target']), int(_r['Damage_per_1x_target']))
def target(aid, L, hm):
    if (aid, L) in TARGET: return TARGET[(aid, L)]
    lv = sorted(l for a, l in TARGET if a == aid); e = lv[0] if L < lv[0] else lv[-1]
    th, tw, td = TARGET[(aid, e)]
    k = enemy_hp(L, hm) / enemy_hp(e, hm); kd = enemy_dmg(L, 1) / enemy_dmg(e, 1)
    return round(th * k), round(tw * k), round(td * kd)
