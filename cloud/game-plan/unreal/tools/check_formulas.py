"""B06: checks the formula library's math against the data CSVs, then writes the C++ test cases.

Each function mirrors one USfFormulaLibrary function (same name). Expected values in the
generated cases come from the CSV columns where data exists, so the C++ is tested against data.
Run: python3 tools/check_formulas.py  (exits 1 on any mismatch).
"""
import ast, csv, functools, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / 'data'
OUT = ROOT / 'Source/SfTests/Private/SfFormulaCases.inl'

@functools.cache
def rows(rel):
    with open(DATA / rel, newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
def generator_table(rel, name):  # a dict literal from an actors generator, read without running it
    tree = ast.parse((DATA / 'actors/tools' / rel).read_text())
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == name)
rnd = round  # half to even, as the data generators round; C++ uses FMath::RoundHalfToEven
def lerp(a, b, t): return a + (b - a) * t

# --- the formulas (mirror SfFormulaLibrary.cpp) ---
def PiecewiseLinear(pts, x):
    if x <= pts[0][0]: return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1: return lerp(y0, y1, (x - x0) / (x1 - x0))
    return pts[-1][1]
def UpgradeMult(u, armor=False): return 1 + (0.06 if armor else 0.075) * u
def ScalingCoef(grade_coef, u): return grade_coef * (1 + 0.025 * u)
def AttackRating(base, u, rar_mult, coefs, factors, req_met=True):
    if not req_met: return base * UpgradeMult(u) * rar_mult * 0.6
    return base * UpgradeMult(u) * rar_mult + sum(base * ScalingCoef(c, u) * f for c, f in zip(coefs, factors))
def HitDamage(ar, motion, defense, resist, elem, crit=1.0, coop=1.0):
    raw = ar * motion
    return max(raw * 100 / (100 + defense) * (1 - resist) * elem * crit * coop, 0.1 * raw)
def WardHit(dmg, ward, ward_mult, flesh_mult):  # returns (ward damage, health damage)
    wd = dmg * ward_mult
    if wd <= ward: return wd, 0.0
    return ward, (dmg - ward / ward_mult) * flesh_mult
def PrecisionMult(weapon_mult, ward): return weapon_mult if ward <= 0 else 1.25
def RangeFalloff(d, start, end, floor):
    if d <= start: return 1.0
    if d >= end: return floor
    return lerp(1.0, floor, (d - start) / (end - start))
def CritDamage(ar, weapon_crit_mult, crit_pct): return ar * 3.0 * weapon_crit_mult * crit_pct / 100
def BlockResult(raw, absorb, stability): return raw * (1 - absorb), raw * (1 - stability / 100)
def BreathRegen(finesse_bonus_pct, blocking): return 20.0 if blocking else 40 * (1 + finesse_bonus_pct / 100)
def WeaponStatusBuildup(value, u, motion): return value * UpgradeMult(u) * motion
def AbilityStatusBuildup(value, rite_rank): return value * (1 + rite_rank / 200)
def StatusThreshold(base, boss, recent_proc): return base * (2.0 if boss else 1.0) * (1.25 if recent_proc else 1.0)
def RollType(load, max_load):  # 0 Light, 1 Medium, 2 Heavy, 3 Overloaded
    r = load / max_load
    return 0 if r < 0.30 else 1 if r < 0.70 else 2 if r <= 1.0 else 3
def KindleCost(L): return math.floor(0.02 * L**3 + 3 * L**2 + 100 * L + 500)
def EnemyHealth(L, mult): return rnd(mult * (60 + 18 * L))
def EnemyDamage(L, mult): return rnd(mult * (8 + 1.6 * L))
def EnemyDefense(L, mult): return rnd(mult * (10 + 2 * L))
def EnemyEmber(L, mult, player_level):
    return rnd(0.16 * mult * (10 + 1.5 * L**1.5) * (0.25 if player_level - L >= 10 else 1.0))
def BossHealth(L, class_mult): return rnd(class_mult * (400 + 140 * L) / 10) * 10
def BossDamage(L, move_mult): return rnd(move_mult * (20 + 4 * L))
def BossEmber(L, class_ember): return rnd(class_ember * KindleCost(L))
def EmberIncomePerHour(mid_level): return rnd(1.9 * KindleCost(mid_level))
def TonicHeal(max_health, distillations, grit):
    return max_health * (0.40 + 0.025 * min(distillations, 8)) * (1 + 0.005 * max(0, grit - 30))
def ReputationGain(base, speech, rival): return base * (1 + speech / 200) * (0.5 if rival else 1.0)
def BuyPrice(base, price_mult, u, speech, faction_discount):
    return rnd(base * price_mult * (1 + 0.05 * u) * (1 - min(0.20, speech / 500)) * faction_discount / 10) * 10
def SellPrice(base, price_mult, u, speech):
    return math.floor(BuyPrice(base, price_mult, u, 0, 1.0) * 0.12 * (1 + speech / 1000))
def UpgradeEmber(to_level, armor, rarity_mult):
    step = 120 * 1.3 ** (to_level - 1) if armor else 150 * 1.18 ** (to_level - 1)
    return rnd(step * rarity_mult / 10) * 10
def ArmorAbsorption(absorbs, upgrades):
    p = 1.0
    for a, u in zip(absorbs, upgrades): p *= 1 - a * UpgradeMult(u, True)
    return 1 - p
def CraftedBonusCap(bonus, perk): return min(bonus, 0.18 if perk else 0.15)
def RiteEmberCost(mag, dur, area, effect_base, shaping):
    return mag**1.3 * dur**0.6 * area**0.4 * effect_base * (1 - shaping / 250)
def RiteCooldown(base_cd, mag, dur, area):
    return min(90.0, max(6.0, base_cd * (mag / 10)**1.1 * (1 + dur / 20) * (1 + area / 8)))
def GhostEmber(carried, old_ghost): return carried + old_ghost // 2
def BountyClear(bounty, bribe_perk): return rnd(bounty * (0.6 if bribe_perk else 1.0))
def EnemyHitChance(d, a10, a30, a60, sprinting, partial_cover):
    p = PiecewiseLinear([(10, a10), (30, a30), (60, a60)], d)
    return p * (0.6 if sprinting else 1.0) * (0.75 if partial_cover else 1.0)
def CoverScore(w_dist, dist, w_cover, cover, w_allies, allies, w_ward, ward_frac, w_exp, los):
    return w_dist * (1 - dist / 30) + w_cover * cover + w_allies * min(allies, 4) / 4 + w_ward * ward_frac - w_exp * los
def SyncedLevel(level, band_min, band_max): return max(band_min, min(level, band_max + 5))
def GameSpeed(assist, players): return 1.0 if players > 1 else assist

# --- cross-check against data ---
cases, errors = [], []
def check(name, call, actual, expected, tol=0.001, emit=True):
    if abs(actual - expected) > tol: errors.append(f'{name}: formula {actual} vs data {expected}')
    elif emit: cases.append((name, call, expected, tol))

for r in rows('actors/level_curve.csv'):
    L = int(r['Level'])
    if r['Ember to kindle next'] != '0': check(f'KindleCost L{L}', f'KindleCost({L})', KindleCost(L), int(r['Ember to kindle next']))
for L, v in [(10, 1820), (35, 8532), (70, 29060)]: check(f'ECOF_LEVEL L{L}', f'KindleCost({L})', KindleCost(L), v)
check('ECOF_INFLOW Thornwood', 'EmberIncomePerHour(27)', EmberIncomePerHour(27), 10982)

for r in rows('items/upgrade_costs.csv'):
    u, armor = int(r['to_level']), r['item_kind'] == 'armor'
    a = 'true' if armor else 'false'
    check(f'UpgradeMult {r["item_kind"]} +{u}', f'UpgradeMult({u}, {a})', UpgradeMult(u, armor), float(r['ar_mult_after']))
    check(f'UpgradeEmber {r["item_kind"]} +{u}', f'UpgradeEmber({u}, {a}, 1.0)', UpgradeEmber(u, armor, 1.0), int(r['ember']))

DEF_MULT = {role: v[1] for role, v in generator_table('gen_enemies.py', 'ROLE').items()}
ember_mult = {r['ACT_ID']: (DEF_MULT.get(r['Role']), float(r['Ember mult'])) for r in rows('actors/enemies.csv')}
for r in rows('actors/enemy_stats_by_level.csv'):
    aid, L = r['ACT_ID'], int(r['Level'])
    dm, em = ember_mult[aid]
    emit = L in (1, 35, 70) or L % 20 == 0
    check(f'EnemyDefense {aid} L{L}', f'EnemyDefense({L}, {dm})', EnemyDefense(L, dm), int(r['Defense']), emit=emit)
    check(f'EnemyEmber {aid} L{L}', f'EnemyEmber({L}, {em}, {L})', EnemyEmber(L, em, L), int(r['Ember']), emit=emit)
for r in rows('actors/creatures.csv'):
    L, hm, em = int(r['Reference level']), float(r['HP mult']), float(r['Ember mult'])
    check(f'EnemyHealth {r["ACT_ID"]}', f'EnemyHealth({L}, {hm})', EnemyHealth(L, hm), int(r['HP @ref']))
    check(f'EnemyEmber {r["ACT_ID"]}', f'EnemyEmber({L}, {em}, {L})', EnemyEmber(L, em, L), int(r['Ember @ref']))
check('EnemyEmber 10 levels below', 'EnemyEmber(35, 0.5, 45)', EnemyEmber(35, 0.5, 45), 6)

CLS = {c: (v[0], v[2]) for c, v in generator_table('gen_bosses.py', 'CLS').items()}  # class: (HP mult, Ember mult)
boss_level = {}
for r in rows('actors/bosses.csv'):
    aid, L = r['ACT_ID'], int(r['Level']); hm, em = CLS[r['Class']]; boss_level[aid] = L
    check(f'BossHealth {aid}', f'BossHealth({L}, {hm})', BossHealth(L, hm), int(r['HP (solo)']))
    check(f'BossEmber {aid}', f'BossEmber({L}, {em})', BossEmber(L, em), int(r['Ember reward']))
for r in rows('actors/boss_moves.csv'):
    if not r['Damage (solo)'] or float(r['Damage mult']) == 0: continue
    L, m = boss_level[r['ACT_ID']], float(r['Damage mult'])
    check(f'BossDamage {r["MOV_ID"]}', f'BossDamage({L}, {m})', BossDamage(L, m), int(r['Damage (solo)']), emit=r['MOV_ID'].endswith('_01'))

rar = {r['name']: (int(r['price_mult']), float(r['ar_and_armor_mult'])) for r in rows('items/rarities.csv')}
for f in ('items/weapons_melee.csv', 'items/weapons_firearm.csv'):
    for r in rows(f):
        if not r.get('base_value'): continue
        pm, base = rar[r['rarity']][0], int(r['base_value'])
        emit = r['item_id'].endswith('_01')
        check(f'BuyPrice {r["item_id"]}', f'BuyPrice({base}, {pm}, 0, 0, 1.0)', BuyPrice(base, pm, 0, 0, 1.0), int(r['buy_price']), emit=emit)
        check(f'SellPrice {r["item_id"]}', f'SellPrice({base}, {pm}, 0, 0)', SellPrice(base, pm, 0, 0), int(r['sell_price']), emit=emit)

curve = [(0, 0.0)] + [(int(r['Points']), float(r['Curve value (0-1)'])) for r in rows('actors/attribute_scaling_curve.csv')]
for p, _ in curve:
    check(f'AttributeFactor {p}', f'AttributeFactor({p})', PiecewiseLinear(curve, p), dict(curve)[p])
grade = {r['grade']: float(r['coef_at_plus0']) for r in rows('items/scaling_grades.csv')}

# Formulas with no data column: literal inputs, value from the Python mirror (C++ parity).
def lit(name, call, value, tol=0.001): cases.append((name, call, value, tol))
sts = rows('items/weapons_melee.csv')[0]  # Salvager's Shortsword: Slash 114, C/C/E/E
coefs = [grade[sts[f'grade_{a}']] for a in ('might', 'finesse', 'lore', 'grit')]
facs = [PiecewiseLinear(curve, v) for v in (20, 30, 10, 10)]
lit('AttackRating Shortsword +5 Rare', f'AttackRating(114, 5, 1.08, {{{", ".join(map(str, coefs))}}}, {{{", ".join(map(str, facs))}}}, true)',
    AttackRating(114, 5, 1.08, coefs, facs))
lit('AttackRating unmet requirement', 'AttackRating(114, 5, 1.08, {0.6, 0.6, 0.15, 0.15}, {0.5, 0.7, 0.25, 0.25}, false)',
    AttackRating(114, 5, 1.08, [0.6, 0.6, 0.15, 0.15], [0.5, 0.7, 0.25, 0.25], False))
lit('EnemyDamage creature', 'EnemyDamage(20, 1.2)', EnemyDamage(20, 1.2))
lit('HitDamage', 'HitDamage(200, 1.2, 51, 0.1, 1.0, 1.0, 1.0)', HitDamage(200, 1.2, 51, 0.1, 1.0))
lit('HitDamage floor 10%', 'HitDamage(100, 1.0, 300, 0.9, 0.5, 1.0, 1.0)', HitDamage(100, 1.0, 300, 0.9, 0.5))
lit('WardHit absorbed', 'WardHit(100, 200, 1.5, 0.8).X', WardHit(100, 200, 1.5, 0.8)[0])
lit('WardHit overflow', 'WardHit(100, 30, 0.5, 1.25).Y', WardHit(100, 30, 0.5, 1.25)[1])
lit('WardHit tint 3x', 'WardHit(100, 1000, 4.5, 0.8).X', WardHit(100, 1000, 4.5, 0.8)[0])
lit('PrecisionMult Ward up', 'PrecisionMult(2.0, 10)', PrecisionMult(2.0, 10))
lit('PrecisionMult Ward down', 'PrecisionMult(2.0, 0)', PrecisionMult(2.0, 0))
lit('RangeFalloff mid', 'RangeFalloff(26, 18, 34, 0.55)', RangeFalloff(26, 18, 34, 0.55))
lit('RangeFalloff past end', 'RangeFalloff(50, 18, 34, 0.55)', RangeFalloff(50, 18, 34, 0.55))
lit('CritDamage', 'CritDamage(200, 1.0, 130)', CritDamage(200, 1.0, 130))
lit('BlockResult chip', 'BlockResult(100, 0.45, 28).X', BlockResult(100, 0.45, 28)[0])
lit('BlockResult Breath', 'BlockResult(100, 0.45, 28).Y', BlockResult(100, 0.45, 28)[1])
lit('BreathRegen', 'BreathRegen(10, false)', BreathRegen(10, False))
lit('BreathRegen blocking', 'BreathRegen(10, true)', BreathRegen(10, True))
lit('WeaponStatusBuildup', 'WeaponStatusBuildup(40, 10, 1.2)', WeaponStatusBuildup(40, 10, 1.2))
lit('AbilityStatusBuildup', 'AbilityStatusBuildup(50, 60)', AbilityStatusBuildup(50, 60))
lit('StatusThreshold boss recent', 'StatusThreshold(100, true, true)', StatusThreshold(100, True, True))
for load, exp in ((10, 0), (20, 1), (35, 2), (40, 2), (41, 3)):
    lit(f'RollType {load}/40', f'RollType({load}, 40)', exp)
lit('TonicHeal', 'TonicHeal(1000, 4, 40)', TonicHeal(1000, 4, 40))
lit('TonicHeal cap', 'TonicHeal(1000, 12, 0)', TonicHeal(1000, 12, 0))
lit('ReputationGain rival', 'ReputationGain(100, 50, true)', ReputationGain(100, 50, True))
lit('BuyPrice Speech 100 Rare +5', 'BuyPrice(300, 4, 5, 100, 0.9)', BuyPrice(300, 4, 5, 100, 0.9))
lit('SellPrice Speech 50', 'SellPrice(300, 4, 5, 50)', SellPrice(300, 4, 5, 50))
lit('UpgradeEmber Rare +5', 'UpgradeEmber(5, false, 1.7)', UpgradeEmber(5, False, 1.7))
lit('ArmorAbsorption', 'ArmorAbsorption({0.1, 0.2}, {0, 10})', ArmorAbsorption([0.1, 0.2], [0, 10]))
lit('CraftedBonusCap', 'CraftedBonusCap(0.3, false)', CraftedBonusCap(0.3, False))
lit('CraftedBonusCap perk', 'CraftedBonusCap(0.3, true)', CraftedBonusCap(0.3, True))
lit('RiteEmberCost', 'RiteEmberCost(20, 10, 2, 1.5, 50)', RiteEmberCost(20, 10, 2, 1.5, 50))
lit('RiteCooldown', 'RiteCooldown(8, 20, 10, 4)', RiteCooldown(8, 20, 10, 4))
lit('RiteCooldown clamp', 'RiteCooldown(8, 100, 60, 20)', RiteCooldown(8, 100, 60, 20))
lit('GhostEmber second death', 'GhostEmber(300, 1001)', GhostEmber(300, 1001))
lit('BountyClear bribe', 'BountyClear(1000, true)', BountyClear(1000, True))
lit('EnemyHitChance 20 m', 'EnemyHitChance(20, 0.8, 0.5, 0.2, false, false)', EnemyHitChance(20, 0.8, 0.5, 0.2, False, False))
lit('EnemyHitChance 70 m sprint cover', 'EnemyHitChance(70, 0.8, 0.5, 0.2, true, true)', EnemyHitChance(70, 0.8, 0.5, 0.2, True, True))
lit('CoverScore', 'CoverScore(1, 15, 2, 0.5, 1, 6, 0.5, 0.5, 1.5, 1)', CoverScore(1, 15, 2, 0.5, 1, 6, 0.5, 0.5, 1.5, 1))
for lv, exp in ((90, 27), (5, 10), (15, 15)): lit(f'SyncedLevel {lv} in 10-22', f'SyncedLevel({lv}, 10, 22)', exp)
lit('GameSpeed co-op', 'GameSpeed(0.8, 2)', GameSpeed(0.8, 2))
lit('GameSpeed solo', 'GameSpeed(0.8, 1)', GameSpeed(0.8, 1))

if errors:
    print(f'{len(errors)} mismatches:', *errors[:30], sep='\n'); sys.exit(1)
OUT.write_text('// Generated by tools/check_formulas.py from the data CSVs. Do not edit.\n'
               + ''.join(f'SF_CASE(TEXT("{n}"), {c}, {e!r}, {t});\n' for n, c, e, t in cases))
print(f'all data checks passed; {len(cases)} cases written to {OUT.relative_to(ROOT)}')
