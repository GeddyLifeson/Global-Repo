#!/usr/bin/env python3
"""Integration pass for Shardfall data. Run after the three folder generators (tools/build.py does it).
Resolves cross-folder placeholders, reconciles names, writes data/world/*, data/ui/strings_data.csv and
data/assets/asset_hooks.csv. Every mapping and naming decision lives in this file; see data/README.md."""
import csv, os, re, math, random, glob
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOK = re.compile(r'(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![a-z0-9])')
GENERATED = ('world/', 'assets/', 'ui/strings_data.csv')
T = {}  # relative path -> [header, rows]

def load():
    for p in sorted(glob.glob(os.path.join(D, '*', '*.csv'))):
        with open(p, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        T[os.path.relpath(p, D)] = [rows[0], rows[1:]]
    for k in [k for k in T if k.startswith(GENERATED)]: del T[k]   # rebuilt below from the source tables

def save():
    for k, (h, rows) in T.items():
        os.makedirs(os.path.dirname(os.path.join(D, k)), exist_ok=True)
        with open(os.path.join(D, k), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f); w.writerow(h); w.writerows(rows)

def dicts(k):
    h, rows = T[k]; return [dict(zip(h, r)) for r in rows]

def col(k, name):
    return T[k][0].index(name)

def setrows(k, header, dict_rows):
    T[k] = [header, [[str(r.get(c, '')) for c in header] for r in dict_rows]]

def edit(k, key, colname, value):
    h, rows = T[k]; i = h.index(colname)
    for r in rows:
        if r[0] == key: r[i] = value

def append(k, dict_rows):
    h, rows = T[k]; have = {r[0] for r in rows}
    for d in dict_rows:
        if d[h[0]] not in have: rows.append([str(d.get(c, '')) for c in h])

def remap(mapping, files=None, fn=None):
    for k, (h, rows) in T.items():
        if files and not any(k.startswith(f) for f in files): continue
        for r in rows:
            for i, c in enumerate(r):
                if fn: c = fn(c)
                r[i] = TOK.sub(lambda m: mapping.get(m.group(0), m.group(0)), c) if mapping else c

load()
# ------------------------------------------------------------------ regions (actors region_bands is canonical)
REGNEW = {'R1': 'REG_01', 'R2': 'REG_02', 'R3': 'REG_03', 'R4': 'REG_04', 'R5': 'REG_05', 'R6': 'REG_06',
          'RQ': 'REG_Q', 'RU': 'REG_U', 'RH': 'REG_HUB'}
remap(None, ['actors/'], lambda c: re.sub(r'\bR([1-6QUH])\b', lambda m: REGNEW['R' + m.group(1)], c))
REG = {}
for r in dicts('actors/region_bands.csv'):
    REG[r['Region ID']] = r
STRREG = {'REG_01': '01', 'REG_02': '02', 'REG_03': '03', 'REG_04': '04', 'REG_05': '05', 'REG_06': '06',
          'REG_Q': 'Q', 'REG_U': 'U', 'REG_HUB': 'HUB', 'REG_END': 'END'}
regrows = [dict(reg_id=k, name=r['Region'], str_id='STR_REGION_' + STRREG[k], level_min=r['Min level'], level_max=r['Max level'],
                element_tint=r['Element tint'], kind='Hub' if k == 'REG_HUB' else 'Region', notes=r['Notes']) for k, r in REG.items()]
regrows.append(dict(reg_id='REG_END', name='Endgame', str_id='STR_REGION_END', level_min=75, level_max=80, element_tint='None',
                    kind='Drop band', notes='Not a place: loot band for Strikes, Citadels, raids and arena'))
setrows('world/regions.csv', ['reg_id', 'name', 'str_id', 'level_min', 'level_max', 'element_tint', 'kind', 'notes'], regrows)
REGNAME = {r['reg_id']: r['name'] for r in regrows}
k = 'items/drop_rarity_by_region.csv'
for r in T[k][1]:
    if r[0] in REG:
        r[1], r[2], r[3] = REG[r[0]]['Region'], REG[r[0]]['Min level'], REG[r[0]]['Max level']
    elif r[0] == 'REG_Q': r[1] = 'The Quiet'

# ------------------------------------------------------------------ bosses: items numbered ACT_BOSS_01..40 in gen_items BCAT order
B = dicts('actors/bosses.csv')
bycls = lambda c: [b for b in B if b['Class'] == c]
def pairs(c):
    out = []
    for j in range(12):
        reg = 'REG_0%d' % (j % 6 + 1)
        out.append([b for b in bycls(c) if b['Region'] == reg][j // 6])
    return out
ORDER = bycls('Shard-bearer') + bycls('Citadel') + pairs('Field') + pairs('Site') + bycls('Raid')
M = {}
BOSSREG = {}
for i, b in enumerate(ORDER):
    n = '%02d' % (i + 1); a = b['ACT_ID']; s = a.replace('ACT_BOSS_', '')
    shb = {1: 'W01', 2: 'W02', 3: 'W03', 4: 'W04', 5: 'W05', 6: 'W06', 7: 'A01', 8: 'A02', 9: 'A03', 10: 'A04', 11: 'A05', 12: 'A06', 37: 'W07', 38: 'W08', 39: 'W09', 40: 'W10'}.get(i + 1)
    shb = 'ITM_SHB_' + shb if shb else 'ITM_MAT_SPC_ASCENDANT'   # bosses without a Shardborn keep the Ascendant Shard as their trophy
    M['ACT_BOSS_' + n] = a
    M['ITM_LOOT_TABLE_BOSS_' + s] = 'ITM_LT_BOSS_' + n
    M['ITM_BOSS_%s_SOUL' % s] = shb          # boss "soul" = its guaranteed first-kill Shardborn
    BOSSREG[a] = b['Region']
# ------------------------------------------------------------------ enemy faction x role loot tables
ROLE = {'SHIELD': 'SHIELDBEARER'}
for fac in ['HOLLOWED', 'REMNANT', 'THORNCLAN', 'CHOIRBORN']:
    f2 = 'THORN' if fac == 'THORNCLAN' else fac
    for role in ['FODDER', 'SHIELD', 'SKIRMISHER', 'ARTILLERY', 'HEAVY', 'LEADER']:
        r2 = ROLE.get(role, role)
        M['ITM_LT_%s_%s' % (fac, role)] = 'ITM_LT_%s_%s' % (f2, r2)
        M['ACT_%s_%s' % (fac, role)] = 'ACT_%s_%s' % (f2, r2)
        M['ITM_LOOT_TABLE_%s_%s' % (f2, role)] = 'ITM_LT_%s_%s' % (f2, r2)
M['ITM_LT_ENEMYSET_THORNCLAN'] = 'ITM_LT_ENEMYSET_THORN'
# ------------------------------------------------------------------ actors item placeholders -> real items
def first(k, **kw):
    return next(r['item_id'] for r in dicts(k) if all(r[c] == v for c, v in kw.items()))
M.update({
    'ITM_AMMO_COMMON': 'ITM_AMO_COM', 'ITM_AMMO_CHARGED': 'ITM_AMO_CHG', 'ITM_AMMO_HEAVY': 'ITM_AMO_HVY',
    'ITM_ARM_CRASHKNIGHT_SET': 'ITM_SET_01', 'ITM_ARM_HULLWITCH_SET': 'ITM_SET_02', 'ITM_ARM_SCAVENGER_SET': 'ITM_SET_03',
    'ITM_ARM_LANTERNPRIEST_SET': 'ITM_SET_04', 'ITM_ARM_RANGER_SET': 'ITM_SET_05', 'ITM_ARM_COLONIST_RAGS': 'ITM_SET_06',
    'ITM_CAT_HULLWITCH_FOCUS': 'ITM_CAT_02', 'ITM_CAT_LANTERN_TOME': 'ITM_CAT_03',
    'ITM_WPN_GREATSWORD_HULLCLEAVER': first('items/weapons_melee.csv', weapon_class='Greatsword', rarity='Common'),
    'ITM_WPN_DAGGER_RIVET': first('items/weapons_melee.csv', weapon_class='Dagger', rarity='Common'),
    'ITM_WPN_HAMMER_CENSER': first('items/weapons_melee.csv', weapon_class='Hammer', rarity='Common'),
    'ITM_WPN_POLEARM_THORNSPEAR': first('items/weapons_melee.csv', weapon_class='Polearm', rarity='Common'),
    'ITM_SHD_HULLPLATE_KITE': first('items/weapons_melee.csv', weapon_class='Shield', rarity='Common'),
    'ITM_WPN_SCOUTRIFLE_SALVAGE': first('items/weapons_firearm.csv', weapon_class='Scout Rifle', rarity='Common'),
    'ITM_WPN_PISTOL_RIVETGUN': first('items/weapons_firearm.csv', weapon_class='Pistol', rarity='Common'),
    'ITM_WPN_SNIPER_LONGBARREL': first('items/weapons_firearm.csv', weapon_class='Sniper Rifle', rarity='Common'),
    'ITM_CON_TONIC': 'ITM_CON_TNC_CRIMSON', 'ITM_CON_TONICSHARD': 'ITM_MAT_HRB_01', 'ITM_CON_THORNSALVE': 'ITM_CON_BRW_WRD',
    'ITM_CON_ECHOSIGIL': 'ITM_CON_UTL_ECHO', 'ITM_CON_MEAT': 'ITM_MAT_HRB_11', 'ITM_MAT_TONICBLOOM': 'ITM_CON_TNC_DISTIL',
    'ITM_KEY_STRIDERHARNESS': 'ITM_CON_UTL_HARNESS', 'ITM_CUR_SEAL': 'ITM_CUR_SEALS',
    'ITM_MAT_HULLSCRAP': 'ITM_MAT_HULL_01', 'ITM_MAT_SHARDDUST': 'ITM_MAT_DUST_01', 'ITM_MAT_CHOIRGLASS': 'ITM_MAT_GLASS_01',
    'ITM_MAT_STARMETAL': 'ITM_MAT_STAR_01',
    'ACT_PLAYER_MAX_LOAD': 'STAT_EQUIPLOAD', 'ACT_SPELL': 'ABL', 'ACT_ECHO': 'ACT_NPC_ECHO',
    'F_TONIC': 'ITM_F_TONIC', 'ACT_EMBER_BOSS': 'ECOF_BOSS', 'ACT_EMBER_KILL': 'ECOF_DROP', 'COOP_BOSS': 'COOP_BOSS_1',
})
for e, c in [('EMBER', 'EMB'), ('STORM', 'STM'), ('HOLLOW', 'HOL'), ('FROST', 'FRS'), ('BLOOM', 'BLM'), ('IRON', 'IRN')]:
    M['ITM_MAT_%sESSENCE' % e] = 'ITM_MAT_ESS_' + c
CRT = [('BLOOMPOD', 'Bloom Pod'), ('BONE', 'Beast Bone'), ('CHITIN', 'Chitin Plate'), ('DRAKESCALE', 'Drake Scale'),
       ('FEATHER', 'Glide Feather'), ('GLASSDUST', 'Glass Dust'), ('HIDE', 'Thick Hide'), ('LANTERNTAIL', 'Lanterntail Gland'),
       ('LEECHOIL', 'Leech Oil'), ('SERPENTSKIN', 'Serpent Skin'), ('STONEHEART', 'Stoneheart'), ('WYRMSCALE', 'Wyrm Scale')]
for c, _ in CRT: M['ITM_MAT_' + c] = 'ITM_MAT_CRT_' + c
# items text ids -> STR_ (STR_LORE_01..08 are loading-screen lines, so item lore uses STR_LOREITEM_)
for i in range(1, 401): M['TXT_LORE_%03d' % i] = 'STR_LOREITEM_%03d' % i
# quests that items filed under LOC_Q_
for t in {m for k2, (h, rows) in T.items() for r in rows for c in r for m in re.findall(r'LOC_Q_[A-Z0-9_]+', c)}:
    M[t] = 'QST_' + t[6:]
# ui string keys renamed to match the canonical ID suffixes
UIKEY = {'STR_SKILL_EMBER_RITE': 'STR_SKILL_EMBERRITE', 'STR_SKILL_STORM_RITE': 'STR_SKILL_STORMRITE', 'STR_SKILL_HOLLOW_RITE': 'STR_SKILL_HOLLOWRITE',
         'STR_FAC_KNIGHTS': 'STR_FAC_HULLKNIGHTS', 'STR_FAC_CHURCH': 'STR_FAC_LANTERNCHURCH', 'STR_FAC_GUILD': 'STR_FAC_SALVAGERS', 'STR_FAC_HAND': 'STR_FAC_QUIETHAND',
         'STR_EFAC_HOLLOWED': 'STR_FAC_HOLLOWED', 'STR_EFAC_REMNANT': 'STR_FAC_REMNANT', 'STR_EFAC_THORN': 'STR_FAC_THORN', 'STR_EFAC_CHOIRBORN': 'STR_FAC_CHOIRBORN',
         'STR_ORIGIN_CRASH': 'STR_ORIGIN_CRASHKNIGHT', 'STR_ORIGIN_SCAV': 'STR_ORIGIN_SCAVENGER', 'STR_ORIGIN_PRIEST': 'STR_ORIGIN_LANTERNPRIEST',
         'STR_REGION_UNDER': 'STR_REGION_U', 'STR_REGION_QUIET': 'STR_REGION_Q'}
for n in range(1, 7): UIKEY['STR_REGION_R%d' % n] = 'STR_REGION_0%d' % n
for sid in [r[0] for r in T['ui/strings.csv'][1]]:
    for old, new in UIKEY.items():
        if sid == old or sid.startswith(old + '_'): M[sid] = new + sid[len(old):]
remap(M)
remap(None, ['actors/'], lambda c: c.replace('per COOP_BOSS_1 (Echo = 0.5 player)', 'per COOP_BOSS_1..4 rows (Echo counts as 0.5 player)')
      .replace('Region 3 midpoint', 'Thornwood midpoint')
      .replace('TonicHeal (0.45 + 0.05 per upgrade)', 'TonicHeal (0.40 + 0.025 per Tonic Distillation, ITM_F_TONIC)'))

# ------------------------------------------------------------------ items: new rows, element opposites, currency, vendors
OPP = {'Ember': 'Frost', 'Frost': 'Ember', 'Storm': 'Iron', 'Iron': 'Storm', 'Hollow': 'Bloom', 'Bloom': 'Hollow'}  # actors element_matrix + ui
for r in dicts('items/damage_types.csv'):
    if r['family'] == 'Weave':
        o = OPP[r['name']]
        edit('items/damage_types.csv', r['dmg_id'], 'ward_tint_breaks_3x', o + '-tinted Ward')
        edit('items/damage_types.csv', r['dmg_id'], 'notes', f'Opposite of {o} (actors/element_matrix.csv); status thresholds in actors/status_effects.csv')
edit('items/damage_types.csv', 'ITM_DMG_STR', 'notes', '+30% stance damage vs enemies tagged armored')
T.pop('items/element_combos.csv', None)
p = os.path.join(D, 'items/element_combos.csv')
if os.path.exists(p): os.remove(p)   # duplicate of actors/element_combos.csv (canonical)
for r in dicts('items/shardborn.csv'):
    a = re.search(r'ACT_BOSS_[A-Z]+', r['source'])
    if a: edit('items/shardborn.csv', r['item_id'], 'first_region', BOSSREG[a.group(0)].replace('REG_Q', 'REG_Q'))
edit('items/currencies.csv', 'ITM_CUR_EMBER', 'source', 'kills (ECOF_DROP), bosses (ECOF_BOSS), Ember Pouches, selling')
h, rows = T['items/cosmetics.csv']; a = h.index('acquisition')
for r in rows: r[a] = r[a].replace('Cosmetics shop', 'Wardrobe Shop (real money)')
h, rows = T['items/vendors.csv']
VN = {'ITM_VEN_APOTHECARY': 'Apothecary', 'ITM_VEN_TINKER': 'Tinker', 'ITM_VEN_SEALS': 'Seal Warden'}
for r in rows:
    r[1] = VN.get(r[0], r[1].replace('Seals Quartermaster', 'Seal Warden'))
mt = dicts('items/materials.csv')
append('items/materials.csv', [dict(item_id='ITM_MAT_CRT_' + c, name=n, category='Creature part', rarity='Common' if j < 8 else 'Rare',
        base_value=12 if j < 8 else 40, sell_price=3 if j < 8 else 10, buyable='no', max_stack=999, weight=0,
        uses='Brewing, Tinkering and Strider gear; see crafting_recipes.csv', icon='UI_ICON_MAT_CRT_' + c, pickup_mesh='MESH_PICKUP_MAT_CRT_' + c)
        for j, (c, n) in enumerate(CRT)])
append('items/consumables.csv', [dict(item_id='ITM_CON_UTL_HARNESS', name='Strider Harness', category='Utility',
        effect='Tame a calmed Strider (ACT_CRT_STRIDER) as a mount', magnitude='', duration_s='', max_stack=1, buy_price=2500,
        sell_price=250, weight=1, use_time_s=3, icon='UI_ICON_CON_UTL_HARNESS', vfx='VFX_CON_UTL_HARNESS', sfx='SFX_CON_UTL_HARNESS')])
append('items/vendors.csv', [dict(vendor_id='ITM_VEN_TINKER', vendor_name='Tinker', location='LOC_LANTERN_HOLD', item_id='ITM_CON_UTL_HARNESS',
        price=2500, currency='ITM_CUR_EMBER', stock=1, restock_game_h=72, unlock='Meet a Strider in Cinderreach')])
idx = dicts('items/items_index.csv'); have = {r['item_id'] for r in idx}
for c, n in CRT:
    if 'ITM_MAT_CRT_' + c not in have: T['items/items_index.csv'][1].append(['ITM_MAT_CRT_' + c, n, 'Material', '', 'materials.csv'])
for iid, n, cat, f in [('ITM_CON_UTL_HARNESS', 'Strider Harness', 'Consumable', 'consumables.csv')]:
    if iid not in have: T['items/items_index.csv'][1].append([iid, n, cat, '', f])

# ------------------------------------------------------------------ actors: economy and stat text agree with items
edit('actors/economy_currencies.csv', 'ECO_CUR_SEAL', 'Sources', 'Strike 10, Hollowed Citadel 15, raid boss 20/27/33/40 by wing (actors/bosses.csv drops), arena win 5 / loss 2 (items/loot_tables.csv)')
edit('actors/economy_currencies.csv', 'ECO_CUR_SEAL', 'Sinks', 'Seal Warden in Lantern Hold (items/vendors.csv ITM_VEN_SEALS)')
edit('actors/economy_currencies.csv', 'ECO_CUR_SEAL', 'Rules', 'Weekly cap 100; carry cap 500; kept on death')
edit('actors/player_base_stats.csv', 'STAT_TONICHEAL', 'Base', '0.4')
edit('actors/player_base_stats.csv', 'STAT_TONICHEAL', 'Regen / rule', '+0.025 per Tonic Distillation (8 in world, ITM_CON_TNC_DISTIL)')
edit('actors/player_base_stats.csv', 'STAT_TONICS', 'Regen / rule', '+1 per Tonic Seed (8 in world, ITM_CON_TNC_SEED); heal per STAT_TONICHEAL over 0.8 s')
h = T['actors/ai_profiles.csv'][0]
append('actors/ai_profiles.csv', [dict({c: 'see boss_ai_rules.csv' for c in h}, **{h[0]: 'AIP_BOSS', 'Faction': 'Boss', 'Role': 'Boss'})])

# ------------------------------------------------------------------ world: npcs, quests, locations
FAC = {r['FAC_ID']: r for r in dicts('actors/factions.csv')}
LEAD = {'ACT_NPC_HULLKNIGHT_COMMANDER': ('Knight-Commander Iselde Marr', 'FAC_HULLKNIGHTS'),
        'ACT_NPC_LANTERN_ARCHIVIST': ('Archivist Oswin Hale', 'FAC_LANTERNCHURCH'),
        'ACT_NPC_SALVAGER_BOSS': ('Guildmistress Petra Quell', 'FAC_SALVAGERS'),
        'ACT_NPC_QUIETHAND_SPEAKER': ('The Speaker', 'FAC_QUIETHAND'),
        'ACT_NPC_CHOIR_PRECENTOR': ('Precentor Amaury Lisk', 'FAC_CHOIR')}
npcs = [dict(act_id=a, name=n, role='Faction leader', fac_id=f, location=FAC[f]['Hub hall'], vendor_id='', str_id=f'STR_{a}_NAME') for a, (n, f) in LEAD.items()]
cmpfac = {'C1': 'FAC_HULLKNIGHTS', 'C2': 'FAC_LANTERNCHURCH', 'C3': 'FAC_SALVAGERS', 'C4': 'FAC_QUIETHAND', 'C5': 'FAC_CHOIR', 'C6': '', 'C7': 'FAC_THORN', 'C8': 'FAC_REMNANT'}
S = {r[0]: r for r in T['ui/strings.csv'][1]}
for c, f in cmpfac.items():
    npcs.append(dict(act_id='ACT_CMP_' + c, name=S['STR_CMP_' + c][2], role='Companion: ' + S['STR_CMP_%s_TAG' % c][2], fac_id=f,
                     location='LOC_LANTERN_HOLD', vendor_id='', str_id='STR_CMP_' + c))
for vid, vn in sorted({(r['vendor_id'], r['vendor_name']) for r in dicts('items/vendors.csv')}):
    loc = next(r['location'] for r in dicts('items/vendors.csv') if r['vendor_id'] == vid)
    npcs.append(dict(act_id='ACT_NPC_VEN_' + vid[8:], name=vn, role='Vendor', fac_id='FAC_CHOIR' if 'ARCHIVIST' in vid else '',
                     location=loc, vendor_id=vid, str_id=f'STR_ACT_NPC_VEN_{vid[8:]}_NAME'))
npcs.append(dict(act_id='ACT_NPC_ECHO', name='Echo', role='Summoned ally (FRM_ECHO, COOP_BOSS_*)', fac_id='', location='', vendor_id='', str_id='STR_ACT_NPC_ECHO_NAME'))
setrows('world/npcs.csv', ['act_id', 'name', 'role', 'fac_id', 'location', 'vendor_id', 'str_id'], npcs)
allcells = lambda: (c for k2, (h, rows) in T.items() for r in rows for c in r)
QN = {'HK': 'FAC_HULLKNIGHTS', 'LC': 'FAC_LANTERNCHURCH', 'SG': 'FAC_SALVAGERS', 'QH': 'FAC_QUIETHAND', 'CH': 'FAC_CHOIR'}
quests = []
for q in sorted({m for c in allcells() for m in re.findall(r'QST_[A-Z0-9_]+', c)}):
    p = q.split('_')
    if p[1] in QN: quests.append(dict(qst_id=q, name=FAC[QN[p[1]]]['Faction'] + ' questline, opening', kind='Faction questline', fac_id=QN[p[1]], region='REG_HUB', reward=''))
    elif p[1] == 'SHB':
        sb = 'ITM_SHB_' + p[2]; reg = next(r['first_region'] for r in dicts('items/shardborn.csv') if r['item_id'] == sb)
        quests.append(dict(qst_id=q, name='Shardborn quest ' + p[2], kind='Exotic quest', fac_id='', region=reg, reward=sb))
    elif p[1] == 'CHOIR': quests.append(dict(qst_id=q, name='Choir questline, part ' + p[2], kind='Faction questline', fac_id='FAC_CHOIR', region='REG_HUB', reward='Choir Archivist stock'))
    else: quests.append(dict(qst_id=q, name=q, kind='Quest', fac_id='', region='', reward=''))
setrows('world/quests.csv', ['qst_id', 'name', 'kind', 'fac_id', 'region', 'reward'], quests)
KIND = {'SMALLCHEST': ('Small chest', 30), 'SHARDCRATE': ('Shard crate', 10), 'VAULT': ('Choir vault', 3), 'NODE': ('Gather node', 10)}
locs = {}
def addloc(lid, kind, reg, note=''):
    locs.setdefault(lid, dict(loc_id=lid, kind=kind, region=reg, name=f'{kind}, {REGNAME.get(reg, reg)}', notes=note))
for c in list(allcells()):
    for m in re.finditer(r'LOC_[A-Z0-9_]+?(_\*)?(?=[^A-Z0-9_*]|$)', c):
        lid = m.group(0)
        rm = re.search(r'REG_(0[1-6]|Q|U|HUB|END)', lid); reg = rm.group(0) if rm else ''
        kd = lid.split('_')[1]
        if lid.endswith('_*'):
            base = lid[:-2]; name, n = KIND.get(kd, (kd.title(), 5))
            regs = [reg] if reg else ['REG_0%d' % i for i in range(1, 7)]
            for rg in regs:
                for j in range(1, n + 1):
                    addloc(f'{base}_{j:02d}' if reg else f'{base}_{rg}_{j:02d}', name, rg, 'Placed by level design; count is a Shardfall choice')
        elif lid == 'LOC_LANTERN_HOLD': addloc(lid, 'Hub', 'REG_HUB')
        else: addloc(lid, {'SITE': 'Lore site', 'DOOR': 'Locked door', 'TOWN': 'Settlement'}.get(kd, kd.title()), reg)
for i, n in enumerate([3, 3, 2, 2, 3, 2]):   # DR-015: 2-3 towns per region (plan 3.7), 15 total
    for j in range(1, n + 1): addloc('LOC_TOWN_REG_0%d_%02d' % (i + 1, j), 'Settlement', 'REG_0%d' % (i + 1), 'Town; count from plan 3.7')
setrows('world/locations.csv', ['loc_id', 'kind', 'region', 'name', 'notes'], sorted(locs.values(), key=lambda r: r['loc_id']))

# ------------------------------------------------------------------ ui: names, numbers and keys from the owning tables
U = T['ui/strings.csv']; S = {r[0]: r for r in U[1]}
def stxt(sid, text, note=None):
    if sid in S:
        S[sid][2] = text; S[sid][3] = str(math.ceil(len(text) * 1.4))
        if note is not None: S[sid][5] = note
for rid, r in REG.items():
    stxt(f'STR_REGION_{STRREG[rid]}', r['Region'], f"Level band {r['Min level']} to {r['Max level']}" if rid != 'REG_HUB' else 'Hub')
    stxt(f'STR_REGION_{STRREG[rid]}_ENTER', r['Region'].upper())
for f, r in FAC.items(): stxt('STR_' + f, r['Faction'])
STS = {'BURN': 'Takes 2% max Health plus 5 per second for 6 seconds. Healing received is cut by 20%.',
       'SHOCK': 'Ward recharge stops for 4 seconds. The next hit chains 30% damage to 2 targets within 6 m.',
       'DRAIN': 'Loses 3% max Ward and 3% max Breath per second for 5 seconds. The attacker heals 1% of their max Health per second.',
       'SLOW': 'Moves and attacks 30% slower for 5 seconds. Three stacks within 10 seconds freeze the target for 2.5 seconds.',
       'ROOT': 'Cannot move or dodge for 3 seconds. Can still attack and block.',
       'SHATTER': 'Armor and Defense drop 25% and poise damage taken rises 20% for 8 seconds.'}
for k2, t in STS.items(): stxt(f'STR_STATUS_{k2}_DESC', t, 'Numbers from actors/status_effects.csv')
REP = dicts('actors/reputation_tiers.csv')
for i, r in enumerate(REP): stxt(f'STR_STANDING_{i}', r['Tier'], f"Standing {r['REP_ID']}, {r['Min']} to {r['Max']} (actors/reputation_tiers.csv)")
ORG = {r['ORG_ID']: r for r in dicts('actors/origins.csv')}
NAME = {r['item_id']: r['name'] for r in dicts('items/items_index.csv')}
NAME.update({r['set_id']: r['name'] for r in dicts('items/armor_sets.csv')})
okey = lambda o: o.replace('ORG_', '')
for o, r in ORG.items():
    kitcol = [c for c in r if c.startswith('Starting kit')][0]
    kit = [x.split(' x')[0].strip() for x in re.split(r'[|;]', r[kitcol]) if x.strip()]
    stxt(f'STR_ORIGIN_{okey(o)}_KIT', 'Starting gear: ' + ', '.join(NAME.get(x, x) + (' armor' if x.startswith('ITM_SET') else '') for x in kit))
    SKN = {x['SKL_ID']: x['Skill'] for x in dicts('actors/skills.csv')}
    sk = re.sub(r'(SKL_[A-Z]+)\+(\d+)', lambda m: f'{SKN[m.group(1)]} +{m.group(2)}', r['Skill bonuses (added to base 5)']).replace(';', ',')
    stxt(f'STR_ORIGIN_{okey(o)}_SKILLS', 'Starting skills: ' + sk)
stxt('STR_ORIGIN_UNBOUND_DESC', 'No past. No starting skill bonuses. Six free attribute points instead.')
stxt('STR_END_SEAL_CAP', 'Weekly Seals {VAR_n} / 100', 'Weekly cap from items/currencies.csv')
U[1] = [r for r in U[1] if not r[0].startswith('STR_WFAM_')]
for cls in dicts('items/melee_classes.csv') + dicts('items/firearm_classes.csv'):
    t = cls['name']; U[1].append(['STR_WFAM_' + cls['class_id'][8:], 'Shared', t, str(math.ceil(len(t) * 1.4)), '', 'Weapon family (items class ' + cls['class_id'] + ')'])
for sid, t in [('STR_REGION_END', 'Endgame'), ('STR_CUR_EMBER', 'Ember'), ('STR_CUR_SEALS', 'Seals')]:
    if sid not in S: U[1].append([sid, 'Shared', t, str(math.ceil(len(t) * 1.4)), '', 'Currency name'])

# ------------------------------------------------------------------ ui/strings_data.csv: names and descriptions of every data entity, lore text
SD = []
def sd(sid, screen, text, note=''):
    if text: SD.append([sid, screen, text, str(math.ceil(len(text) * 1.4)), '', note])
for r in dicts('items/items_index.csv'):
    if r['category'] != 'Lore item': sd(f"STR_{r['item_id']}_NAME", 'Item name', r['name'], r['category'])
for f, idc, dc in [('items/weapon_arts.csv', 'item_id', 'description'), ('items/consumables.csv', 'item_id', 'effect'), ('items/shardborn.csv', 'item_id', 'perk_effect'),
                   ('items/weapon_perks.csv', 'perk_id', 'effect'), ('items/infusions.csv', 'infusion_id', 'rule')]:
    for r in dicts(f):
        if f.endswith(('weapon_perks.csv', 'infusions.csv')): sd(f'STR_{r[idc]}_NAME', 'Item name', r['name'])
        sd(f'STR_{r[idc]}_DESC', 'Item description', r[dc])
for r in dicts('items/armor_sets.csv'):
    sd(f"STR_{r['set_id']}_NAME", 'Item name', r['name'], 'Armor set')
    sd(f"STR_{r['set_id']}_BONUS2", 'Item description', r['bonus_2pc']); sd(f"STR_{r['set_id']}_BONUS4", 'Item description', r['bonus_4pc'])
for f, idc, nc, dc in [('actors/bosses.csv', 'ACT_ID', 'Boss', None), ('actors/enemies.csv', 'ACT_ID', 'Name', None), ('actors/creatures.csv', 'ACT_ID', 'Name', None),
                       ('actors/perks.csv', 'PRK_ID', 'Perk', 'Effect (per rank)'), ('actors/weave_abilities.csv', 'ABL_ID', 'Name', 'Notes'),
                       ('actors/resonances.csv', 'RES_ID', 'Resonance', 'Effect (tier 1)'), ('world/quests.csv', 'qst_id', 'name', None)]:
    for r in dicts(f):
        sd(f'STR_{r[idc]}_NAME', 'Data name', re.sub(r' \(.*\)$', '', r[nc]))
        if dc: sd(f'STR_{r[idc]}_DESC', 'Data description', r[dc])
for r in npcs:
    if not r['str_id'].startswith('STR_CMP_'): sd(r['str_id'], 'Data name', r['name'])
# lore text: first-pass copy, one per lore item, seeded so it is stable between builds
L = random.Random(20261003)
DECK = {'Bridge': 'the bridge', 'Engineering': 'engineering', 'Observation Deck': 'the observation deck', 'Hydroponics': 'hydroponics', 'Cryo Bay': 'the cryo bay'}
LOGA = ['Hull integrity holding at {p}%.', 'Crew rotation suspended.', 'The Shard is louder tonight.', 'Third night without stars on the scopes.',
        'Captain Ostra ordered the lanterns lit on every deck.', 'Lost contact with the aft ring.', 'Navigation insists we are not falling. We are falling.',
        'Rationing begins tomorrow.', 'Someone has been writing hymns in the margins of these logs.', 'The glass in the viewports has started to sing.']
LOGB = ['If anyone reads this, keep the lanterns burning.', 'End of entry.', 'I have stopped counting the days.', 'We will make landfall or we will make a grave.',
        'Choir says the Shard is dreaming. I say it is awake.', 'Note to self: do not listen at the core door.']
LET = ['I am well, mostly. The food is ash and the walls hum.', 'They gave me a sword before they gave me boots.', 'Do not believe what the Church says about the logs.',
       'The Guild pays in Ember and promises. Only one of those spends.', 'I heard the Choir singing below the town again.', 'Burn this after reading.',
       'The Hollowed came within sight of the wall last night.', 'I have found work in {r}. Do not come looking for me.']
REL = ['Warm to the touch, though it should not be.', 'Etched with a ship registry number from the Meridian.', 'Hums a single note when held near a Shard.',
       'The Choir pays well for these, and asks no questions.', 'Found in {r}, in the hands of someone long dead.']
KEY = ['Opens a sealed door in {r}.', 'The teeth are cut from Starmetal.', 'Stamped with the Lantern Church sigil.', 'Someone wanted this door to stay closed.']
for r in dicts('items/lore_items.csv'):
    sid = r['text_id']; rn = REGNAME.get(r['region'], r['region']); t = r['lore_type']; p = L.randint(12, 97)
    if t == 'Key': txt = L.choice(KEY).format(r=rn)
    elif t == 'Relic': txt = ' '.join(L.sample(REL, 2)).format(r=rn)
    elif t == 'Letter': txt = ' '.join(L.sample(LET, 3)).format(r=rn)
    else:
        deck = next((v for k2, v in DECK.items() if k2 in r['name']), 'the ship')
        txt = f'Log from {deck}. ' + ' '.join(L.sample(LOGA, 2)).format(p=p) + ' ' + L.choice(LOGB)
    sd(sid, 'Lore reader', txt, f"Text for {r['item_id']} ({t}); first pass, writer polish later")
setrows('ui/strings_data.csv', U[0], [dict(zip(U[0], r)) for r in SD])

# ------------------------------------------------------------------ design data requests (tools/merge/m_*.py); writes design/merge-report.csv
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merge
_rep = merge.run(T, D)
print('merge: ' + ', '.join(f"{n} {s}" for s, n in sorted(__import__('collections').Counter(r['status'] for r in _rep).items())))

# ------------------------------------------------------------------ asset hooks registry for the asset list
AP = ('MESH', 'VFX', 'SFX', 'ANIM', 'UI', 'ARENA')
hooks = {}
for k2, (h, rows) in sorted(T.items()):
    for r in rows:
        for c in r:
            for m in TOK.findall(c):
                if m.split('_')[0] in AP:
                    hooks.setdefault(m, dict(hook=m, kind=m.split('_')[0], first_used_in=k2, first_row=r[0], uses=0))['uses'] += 1
setrows('assets/asset_hooks.csv', ['hook', 'kind', 'first_used_in', 'first_row', 'uses'], sorted(hooks.values(), key=lambda r: r['hook']))
save()
print('link: %d id remaps, %d npcs, %d quests, %d locations, %d data strings, %d asset hooks' % (len(M), len(npcs), len(quests), len(locs), len(SD), len(hooks)))
