"""Merge module m_systems: design/loops, design/systems, design/simulation and design/controls data requests.
Patches the loaded tables in T only; idempotent (every append checks its key, every edit sets an absolute value)."""
import re, math

FILES = ['loops/data-requests.csv', 'systems/data-requests.csv', 'simulation/data-requests.csv', 'controls/data-requests.csv']
L, SY, SI, C = FILES

TOK = re.compile(r'(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![a-z0-9])')
RUNTIME = re.compile(r'\{([A-Z]+)_[a-z_]+\}')
RUNTIME_OK = {'ITM', 'ACT', 'PRK', 'VAR', 'BTN', 'SKL', 'ATTR', 'ELEM', 'STATUS', 'FAC', 'CMP', 'REGION'}
HOOK = ('MESH', 'VFX', 'SFX', 'ANIM', 'UI', 'ARENA')          # link.py registers every token with these prefixes as an asset hook
STALE = ['Ashfall Reach', 'Region 2', 'Region 3', 'Region 4', 'Region 5', 'Region 6', 'Seals Quartermaster', 'TXT_', 'Lanterns', 'Hardcore']  # bible: ok
# 'Lanterns' means the removed currency; these two place names (design/world/locations.csv) are allowed
NOT_STALE = ('Stilt Lanterns', 'Abbot Lanterns')
def unstale(c):
    for n in NOT_STALE: c = c.replace(n, '')
    return c



# ------------------------------------------------------------------ helpers
def _row(ctx, k, key):
    for r in ctx.rows(k):
        if r[ctx.T[k][0][0]] == key: return r
    return None

def _append_multi(ctx, k, dicts, match):
    """Append rows to a several-rows-per-key table; skip a row when a row with the same match columns exists."""
    h, rr = ctx.T[k]; n = 0
    for d in dicts:
        for c in d:
            if c not in h: h.append(c); [r.append('') for r in rr]
        if any(all(r[h.index(m)] == str(d.get(m, '')) for m in match) for r in rr): continue
        rr.append([str(d.get(c, '')) for c in h]); n += 1
    return n

def _str(ctx, sid, text, screen='Design merge', note='', tokens=''):
    """Add a string with its tokens column. Returns 'added', 'same' or 'clash'."""
    have = {}
    for f in ('ui/strings.csv', 'ui/strings_data.csv'):
        for r in ctx.T[f][1]: have.setdefault(r[0], r[2])
    if sid in have: return 'same' if have[sid] == text else 'clash'
    ctx.append('ui/strings_data.csv', {'str_id': sid, 'screen': screen, 'text_en': text, 'max_chars': math.ceil(len(text) * 1.4), 'tokens': tokens, 'notes': note})
    return 'added'

def _count(res):
    return {s: res.count(s) for s in ('added', 'same', 'clash')}

def _defined(T, extra):
    d = set()
    for h, rr in list(T.values()) + list(extra):
        d.update(TOK.findall(','.join(h)))
        for r in rr:
            if r: d.add(r[0])
    pre = set()
    for x in d:
        for n in range(1, x.count('_') + 1): pre.add('_'.join(x.split('_')[:n]))
    return d, pre

def _bad_cell(c, d, pre):
    if any(s in unstale(c) for s in STALE): return True
    if any(m.group(1) not in RUNTIME_OK for m in RUNTIME.finditer(c)): return True
    for m in TOK.finditer(c):
        t, after = m.group(0), c[m.end():m.end() + 2]
        if t.split('_')[0] in HOOK: continue
        if after.startswith(('_*', '_<', '*')) or re.match(r'_[a-z]', after):
            if t not in d and t not in pre: return True
        elif t not in d: return True
    return False

def _new_tables(ctx, specs):
    """specs: list of (data key, design rel path or (header, rows)). Builds all tables together so they can reference each other,
    keeps only the columns whose every cell resolves. Returns {key: [dropped columns]}."""
    raw = {}
    for k, src in specs:
        if isinstance(src, str):
            rows = ctx.design_rows(src); h = list(rows[0].keys())
            raw[k] = [h, [[r[c] or '' for c in h] for r in rows]]
        else:
            raw[k] = [list(src[0]), [list(r) for r in src[1]]]
    for k in raw: ctx.T.pop(k, None)
    d, pre = _defined(ctx.T, raw.values())
    dropped = {}
    for k, (h, rr) in raw.items():
        keep = [0] + [j for j in range(1, len(h)) if not any(_bad_cell(r[j], d, pre) for r in rr)]
        dropped[k] = [h[j] for j in range(len(h)) if j not in keep]
        ctx.T[k] = [[h[j] for j in keep], [[r[j] for j in keep] for r in rr]]
    return dropped

def _drop_note(dropped):
    parts = [f"{k.split('/')[-1]} without {', '.join(v)}" for k, v in dropped.items() if v]
    return ('; unresolved columns dropped: ' + '; '.join(parts)) if parts else ''


# ------------------------------------------------------------------ simulation
GUARD_ROLES = [  # guard_profiles id suffix, display, Thorn Clans base role used for the enemy_stats_by_level curve, level offset
    ('WATCH', 'Watch', 'SHIELDBEARER', 0), ('ARCHER', 'Watch Rifle', 'ARTILLERY', 0), ('CAPTAIN', 'Captain', 'LEADER', 3),
    ('WARDEN', 'Weave Warden', 'ARTILLERY', 0), ('HUNTER', 'Bounty Hunter', 'SKIRMISHER', 0)]

def simulation(T, ctx):
    rep = {}
    gp = {r['guard_id'][4:]: r for r in ctx.design_rows('simulation/guard_profiles.csv')}
    jur = [r for r in ctx.design_rows('simulation/crime_jurisdictions.csv') if r['jur_id'] != 'JUR_NONE']

    # DR-SIM-03 FAC_TOWN
    new = ctx.append('actors/factions.csv', {'FAC_ID': 'FAC_TOWN', 'Faction': 'Town', 'Type': 'Neutral', 'Hub hall': '-', 'Questline length': '-',
        'Rival (joining closes)': '-', 'Theme': 'Civilians and town guards',
        'Join requirement': 'Not joinable; hostile only to players with bounty tier Wanted for arrest or higher in that jurisdiction', 'Leader (actor)': ''})
    _str(ctx, 'STR_FAC_TOWN', 'Town', 'Data name', 'Faction (DR-SIM-03)')
    rep['DR-SIM-03'] = ('applied' if new else 'skipped', 'actors/factions.csv FAC_TOWN',
        'FAC_TOWN added as a Neutral faction for civilians and guards, hostile only to players at bounty tier Wanted for arrest or higher.' if new else 'already applied: FAC_TOWN exists.')

    # DR-SIM-02 AIP_GUARD_*
    aip = 'actors/ai_profiles.csv'; n = 0
    for code, disp, base, _ in GUARD_ROLES:
        src = dict(_row(ctx, aip, f'AIP_THORN_{base}')); g = gp[code]
        src.update({'AIP_ID': f'AIP_GUARD_{code}', 'Faction': 'Town', 'Role': g['role'], 'Reaction ms': g['reaction_ms'], 'Sight m': g['sight_m'],
                    'Sight FOV deg': g['fov_deg'], 'Hearing m': g['hearing_m'], 'Morale base': 100, 'Panic threshold': 0,
                    'Behaviour notes': f'Town guard ({g["weapon_kit"]}); never flees; sight, hearing and reaction from guard_profiles.csv; other weights copied from AIP_THORN_{base}'})
        n += ctx.append(aip, src)
    rep['DR-SIM-02'] = ('applied' if n else 'skipped', aip,
        f'{n} AIP_GUARD_* profiles added with sight, FOV, hearing and reaction from guard_profiles.csv, morale 100 and panic 0; combat weights copied from the matching Thorn Clans role.' if n else 'already applied: AIP_GUARD_* exist.')

    # DR-SIM-01 guard actors
    en, sbl = 'actors/enemies.csv', 'actors/enemy_stats_by_level.csv'
    stats = {(r['ACT_ID'], int(r['Level'])): r for r in ctx.rows(sbl)}
    n = 0
    for j in jur:
        suf = j['jur_id'][4:]; force = j['guard_force']
        force = force[force.find('(') + 1:-1] if '(' in force else force
        for code, disp, base, off in GUARD_ROLES:
            aid = f'ACT_GUARD_{code}_{suf}'; lvl = int(j['guard_level']) + off; b = _row(ctx, en, f'ACT_THORN_{base}'); s = stats[(f'ACT_THORN_{base}', lvl)]
            d = dict(b)
            d.update({'ACT_ID': aid, 'Name': f'{force} {disp}', 'FAC_ID': 'FAC_TOWN', 'Tier': 'Guard', 'Base ACT_ID': f'ACT_THORN_{base}', 'Regions': j['reg_id'],
                      'Level band': f'{lvl}-{lvl}', 'Reference level': lvl, 'HP @ref': s['HP'], 'Ward @ref': s['Ward'], 'Defense @ref': s['Defense'],
                      'AIP_ID': f'AIP_GUARD_{code}', 'Ember @ref': s['Ember'], 'Drops (item refs, chance)': '', 'Asset ref': '',
                      'Notes': f'Guard of {j["guard_force"]}, {j["region"]} (DR-SIM-01): {gp[code]["weapon_kit"]}; {gp[code]["count_per_town"]} per town; never flees; stats = ACT_THORN_{base} at level {lvl} (enemy_stats_by_level)'})
            if ctx.append(en, d):
                n += 1
                ctx.append(sbl, {'ACT_ID': aid, 'Level': lvl, 'HP': s['HP'], 'Ward': s['Ward'], 'Defense': s['Defense'], 'Damage per 1.0 mult': s['Damage per 1.0 mult'], 'Ember': s['Ember']})
            _str(ctx, f'STR_{aid}_NAME', d['Name'], 'Data name')
    rep['DR-SIM-01'] = ('applied' if n else 'skipped', en,
        f'{n} guard actors added (5 roles x JUR_01..06 and JUR_HUB) on FAC_TOWN at guard_level (Captain +3), stats from the Thorn Clans role curve in enemy_stats_by_level (Watch=Shield-bearer, Rifle and Warden=Artillery, Captain=Leader, Hunter=Skirmisher, a merge choice since no curve is named).' if n else 'already applied: guard actors exist.')

    # DR-SIM-04 reputation actions
    a = ctx.append('actors/reputation_actions.csv', {'RPA_ID': 'RPA_ARREST_HK', 'Action': 'Jailed in Lantern Hold', 'Base rep': -100, 'Applies to': 'Hull Knights', 'Notes': 'DR-SIM-04'})
    b = ctx.append('actors/reputation_actions.csv', {'RPA_ID': 'RPA_GUARD_KILL', 'Action': 'Kill a guard in Lantern Hold (REG_HUB)', 'Base rep': -400, 'Applies to': 'Hull Knights', 'Notes': 'Per guard killed (DR-SIM-04)'})
    rep['DR-SIM-04'] = ('applied' if a or b else 'skipped', 'actors/reputation_actions.csv',
        'RPA_ARREST_HK (-100) and RPA_GUARD_KILL (-400) added for the Hull Knights.' if a or b else 'already applied: both actions exist.')

    # DR-SIM-05 fences
    towns = sorted(r['loc_id'] for r in ctx.rows('world/locations.csv') if r['loc_id'].startswith('LOC_TOWN_REG_'))
    rows = []
    for t in towns:
        rn = int(t.split('_')[3])
        rows.append({'vendor_id': f'ITM_VEN_FENCE_{t[9:]}', 'vendor_name': 'Fence', 'location': t, 'item_id': 'Stolen items (buys only)',
                     'price': '0.35 x value, +0.05 per Salvagers tier above Neutral (max 0.55)', 'currency': 'ITM_CUR_EMBER', 'stock': f'{4000 * rn} Ember cash per restock', 'restock_game_h': '', 'unlock': "Salvagers' Guild Neutral"})
    for i in (1, 2):
        rows.append({'vendor_id': f'ITM_VEN_FENCE_HUB_{i:02d}', 'vendor_name': 'Fence', 'location': 'LOC_LANTERN_HOLD', 'item_id': 'Stolen items (buys only)',
                     'price': '0.35 x value, +0.05 per Salvagers tier above Neutral (max 0.55)', 'currency': 'ITM_CUR_EMBER', 'stock': '25000 Ember cash per restock', 'restock_game_h': '', 'unlock': "Salvagers' Guild Neutral"})
    n = _append_multi(ctx, 'items/vendors.csv', rows, ['vendor_id'])
    rep['DR-SIM-05'] = ('applied' if n else 'skipped', 'items/vendors.csv',
        f'{n} fence vendors added ({len(towns)} towns plus 2 in Lantern Hold) with buy price and cash cap from stolen_goods.csv; SCH_FENCE is not referenced because no schedule table is in data/.' if n else 'already applied: fence vendors exist.')

    # DR-SIM-06 civilian archetypes
    sch = {}
    for r in ctx.design_rows('simulation/schedule_blocks.csv'): sch.setdefault(r['schedule_id'], r['archetype'])
    homes = towns + ['LOC_LANTERN_HOLD']; n = 0
    for sid, arch in sch.items():
        code = sid[4:]; _str(ctx, f'STR_ACT_CIV_{code}_NAME', arch, 'Data name', 'Generic town NPC (schedule_blocks.csv)')
        for h in homes:
            n += ctx.append('world/npcs.csv', {'act_id': f'ACT_CIV_{code}_{h[9:] if h != "LOC_LANTERN_HOLD" else "HUB"}', 'name': arch, 'role': 'Town NPC (generic)',
                                               'fac_id': 'FAC_TOWN', 'location': h, 'vendor_id': '', 'str_id': f'STR_ACT_CIV_{code}_NAME'})
    rep['DR-SIM-06'] = ('applied' if n else 'skipped', 'world/npcs.csv',
        f'{n} ACT_CIV_* rows added ({len(sch)} schedule archetypes x {len(homes)} towns incl. Lantern Hold, home in location); schedule_id dropped because SCH_* IDs have no data table, and town_tiers population stays in design.' if n else 'already applied: ACT_CIV_* rows exist.')

    # DR-SIM-07 breakable loot tables
    rows = []
    for rg in ['REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06', 'REG_Q']:
        t = f'ITM_LT_BREAKABLE_{rg}'; own = 'breakable crates and barrels'
        rows += [{'table_id': t, 'owner': own, 'entry': 'nothing', 'qty_min': 0, 'qty_max': 0, 'chance_pct': 60, 'condition': 'one roll per break'},
                 {'table_id': t, 'owner': own, 'entry': f'ITM_LT_TIERMAT_{rg}', 'qty_min': 1, 'qty_max': 2, 'chance_pct': 15, 'condition': 'common materials at region band item level'},
                 {'table_id': t, 'owner': own, 'entry': 'ITM_AMO_COM', 'qty_min': 'class pickup', 'qty_max': 'class pickup', 'chance_pct': 15, 'condition': 'ammo'},
                 {'table_id': t, 'owner': own, 'entry': 'ITM_LT_CONSUMABLE', 'qty_min': 1, 'qty_max': 1, 'chance_pct': 10, 'condition': 'one consumable'}]
    n = _append_multi(ctx, 'items/loot_tables.csv', rows, ['table_id', 'entry'])
    rep['DR-SIM-07'] = ('applied' if n else 'skipped', 'items/loot_tables.csv',
        f'ITM_LT_BREAKABLE_REG_01..06 and _Q added ({n} rows): 60% nothing, 30% split 15/15 between region tier materials and common ammo, 10% one consumable.' if n else 'already applied: breakable loot tables exist.')

    # DR-SIM-08 strings + popups
    res = []
    for r in ctx.design_rows('simulation/strings_simulation.csv'):
        res.append(_str(ctx, r['str_id'], r['text_en'], r['screen'], r['notes'], r['tokens']))
    modal = {'kind': 'modal', 'screen': 'Various', 'layer': 'Modal dialog over current screen', 'duration_s': 'Until input', 'dismiss': 'Button press', 'priority': 5,
             'queue_rule': 'Blocks input; pauses game in single player', 'sfx_hook': 'SFX_UI_MODAL'}
    pn = 0
    for pid, trig, title, buttons in [
            ('POP_SIM_SENTENCE', 'Player goes to jail', 'STR_SIM_SENTENCE', ''),
            ('POP_SIM_GUARD_DIALOGUE', 'Guard stops a player with a bounty', 'STR_SIM_GUARD_STOP', 'STR_SIM_OPT_PAY / STR_SIM_OPT_JAIL / STR_SIM_OPT_PERSUADE / STR_SIM_OPT_BRIBE / STR_SIM_OPT_FACTION / STR_SIM_OPT_RESIST'),
            ('POP_SIM_WAIT', 'Wait at an Anchor or bed', 'STR_SIM_WAIT', '')]:
        pn += ctx.append('ui/popups.csv', dict(modal, popup_id=pid, trigger=trig, title_str=title, body_str='', buttons=buttons))
    pn = sum(1 for r in T['ui/popups.csv'][1] if r[0].startswith('POP_SIM_'))
    c = _count(res)
    st = 'conflict' if c['clash'] else 'applied'
    rep['DR-SIM-08'] = (st, 'ui/strings_data.csv + ui/popups.csv',
        f"{c['added']} strings added, {c['same']} already present, {c['clash']} clashed (existing text kept); popups POP_SIM_SENTENCE, POP_SIM_GUARD_DIALOGUE and POP_SIM_WAIT in place ({pn} of 3) using these strings.")

    # requests outside data/ or not applicable
    rep['DR-SIM-09'] = ('skipped', 'assets/asset_hooks.csv', 'outside data/: owned by link.py and the asset thread; hooks are built from data cells and no request puts destructibles.csv or physics_materials.csv into data/, so their MESH/VFX/SFX columns have no data row to register from.')
    rep['DR-SIM-10'] = ('skipped', 'design/audio/vo_bark_categories.csv', 'outside data/: owned by design/audio (audio thread).')
    rep['DR-SIM-11'] = ('skipped', 'design/systems/stealth_actions.csv', 'outside data/: owned by design/systems (systems thread); data already has the lockpick as ITM_CON_UTL_PICK.')
    rep['DR-SIM-12'] = ('skipped', 'tech runtime config', 'outside data/: owned by design/tech (tech thread).')
    for r in ctx.design_rows('simulation/data-requests.csv'):
        st, tg, why = rep[r['id']]; ctx.log(SI, r['id'], st, tg, why)


# ------------------------------------------------------------------ systems
def _item(ctx, iid, name, cat_file, desc):
    ctx.append('items/items_index.csv', {'item_id': iid, 'name': name, 'category': 'Consumable', 'rarity': '', 'file': cat_file})
    _str(ctx, f'STR_{iid}_NAME', name, 'Item name', 'Consumable')
    _str(ctx, f'STR_{iid}_DESC', desc, 'Item description')

def systems(T, ctx):
    rep = {}
    con = 'items/consumables.csv'
    # DR-SYS-001 Repair Kit
    new = ctx.append(con, {'item_id': 'ITM_CON_UTL_REPAIR', 'name': 'Repair Kit', 'category': 'Utility', 'effect': 'Repairs 1 vehicle part (field repair, hold interact at the part)',
                           'magnitude': 1, 'duration_s': 0, 'max_stack': 10, 'buy_price': 300, 'sell_price': 75, 'weight': 0.5, 'use_time_s': '',
                           'craft_recipe': 'ITM_RCP_TNK_UTL_REPAIR', 'icon': 'UI_ICON_CON_UTL_REPAIR', 'vfx': 'VFX_CON_UTL_REPAIR', 'sfx': 'SFX_CON_UTL_REPAIR'})
    ctx.append('items/crafting_recipes.csv', {'recipe_id': 'ITM_RCP_TNK_UTL_REPAIR', 'station': 'Tinkering', 'output': 'ITM_CON_UTL_REPAIR', 'output_qty': 1,
                                              'inputs': '3x ITM_MAT_HULL_01', 'ember_cost': 0, 'skill': 'Engineering', 'skill_rank_req': 1, 'craft_time_s': 2.0, 'learned_from': 'default'})
    _item(ctx, 'ITM_CON_UTL_REPAIR', 'Repair Kit', 'consumables.csv', 'Repairs 1 vehicle part.')
    _append_multi(ctx, 'items/vendors.csv', [{'vendor_id': 'ITM_VEN_TINKER', 'vendor_name': 'Tinker', 'location': 'LOC_LANTERN_HOLD', 'item_id': 'ITM_CON_UTL_REPAIR',
                                              'price': 300, 'currency': 'ITM_CUR_EMBER', 'stock': 10, 'restock_game_h': 72, 'unlock': ''}], ['vendor_id', 'item_id'])
    rep['DR-SYS-001'] = ('applied' if new else 'skipped', 'items/consumables.csv ITM_CON_UTL_REPAIR',
        'Repair Kit added (Tinker 300 Ember, stack 10, weight 0.5, sell 75 by ITM_F_PRICE_SELL) with recipe ITM_RCP_TNK_UTL_REPAIR (3 Hull Scrap).' if new else 'already applied: ITM_CON_UTL_REPAIR exists.')
    # DR-SYS-002 lockpick
    rep['DR-SYS-002'] = ('skipped', 'items/consumables.csv', 'already applied: the lockpick exists as ITM_CON_UTL_PICK (Salvager Picks, stack 50; data keeps its 20 Ember price and 0.05 weight), as DR-SIM-11 also notes.')
    # DR-SYS-003 suppressor
    new = ctx.append('items/weapon_perks.csv', {'perk_id': 'ITM_PRK_BRL_SUPPRESSED', 'column': 1, 'applies_to': 'firearm: ITM_CLS_PST ITM_CLS_SMG ITM_CLS_ARF ITM_CLS_SCT',
        'name': 'Suppressed Barrel', 'effect': 'Noise radius x0.35; -15% range', 'max_crafted_value': '', 'attachment_mesh': 'MESH_ATT_BRL_SUPPRESSED', 'icon': 'UI_ICON_ITM_PRK_BRL_SUPPRESSED'})
    rep['DR-SYS-003'] = ('applied' if new else 'skipped', 'items/weapon_perks.csv', 'ITM_PRK_BRL_SUPPRESSED added in the barrel column for Pistol, SMG, Auto Rifle and Scout Rifle (noise x0.35, range -15%).' if new else 'already applied.')
    # DR-SYS-004 legendary skills
    k = 'actors/skills.csv'
    for r in ctx.rows(k): ctx.edit(k, r['SKL_ID'], 'Legendary rule', 'At rank 100 the skill can reset to 15, refunding its perk points; resets shown as stars; no cap')
    rep['DR-SYS-004'] = ('applied', k, 'Legendary rule column added to every skill: reset at rank 100 to 15 with perk refund, stars counter, no cap.')
    # DR-SYS-005 vehicles (new world tables)
    parts = ctx.design_rows('systems/vehicle_parts.csv')
    ph = ['part_id'] + list(parts[0].keys())
    prow = [[f"{p['veh_id']}_{p['part'].replace('..', '_TO_')}"] + [p[c] for c in parts[0]] for p in parts]
    dropped = _new_tables(ctx, [('world/vehicles.csv', 'systems/vehicles.csv'), ('world/vehicle_parts.csv', (ph, prow)), ('world/vehicle_weapons.csv', 'systems/vehicle_weapons.csv')])
    rep['DR-SYS-005'] = ('applied', 'world/vehicles.csv, vehicle_parts.csv, vehicle_weapons.csv',
        'Vehicle tables added with VEH_ and VWP_ IDs (vehicle_parts keyed VEH_<vehicle>_<part>)' + _drop_note(dropped) + '; MESH/VFX/SFX_VEH hooks need link.py (not in this module).')
    # DR-SYS-006 character creator strings
    res = []
    cc = ctx.design_rows('systems/character_creator.csv')
    for r in cc:
        sid = r['label_str']
        if re.match(r'STR_CC_(FACE_SHAPE|BROW|EYES|NOSE|CHEEKS|MOUTH|JAW|EARS)_\d\d$', sid):
            res.append(_str(ctx, sid, re.sub(r' \(.*\)$', '', r['notes']).replace('colour', 'color'), 'Character creation', 'Face slider (DR-SYS-006)'))
    for sid in ['STR_CC_PRONOUN', 'STR_CC_PROSTHETIC', 'STR_CC_EYE_SHARD', 'STR_CC_MAKEUP', 'STR_CC_TATTOO', 'STR_CC_SAVE_PRESET', 'STR_CC_MIRROR']:
        res.append(_str(ctx, sid, sid[7:].replace('_', ' ').title(), 'Character creation', 'Option label (DR-SYS-006)'))
    for r in ctx.design_rows('systems/cc_presets.csv'):
        res.append(_str(ctx, r['name_str'], r['look'], 'Character creation', f"Face preset {r['frame']}"))
    c = _count(res)
    rep['DR-SYS-006'] = ('conflict' if c['clash'] else 'applied', 'ui/strings_data.csv',
        f"{c['added']} character creator strings added (slider labels and preset names from character_creator.csv / cc_presets.csv, option labels from their IDs), {c['same']} already present, {c['clash']} clashed; {{VAR_pronoun}} is an allowed runtime token.")
    # DR-SYS-007 stealth strings + popups
    res = [_str(ctx, r['data_ids'], re.sub(r' \(.*\)$', '', r['state']), 'HUD', 'Stealth state (DR-SYS-007)') for r in ctx.design_rows('systems/stealth_states.csv') if r['data_ids'].startswith('STR_STL_')]
    prm = {'kind': 'prompt', 'screen': 'HUD', 'layer': 'HUD bottom centre', 'body_str': '', 'buttons': '', 'duration_s': 'Until out of range', 'dismiss': 'Condition met',
           'priority': 4, 'queue_rule': 'One at a time; highest priority wins', 'sfx_hook': 'SFX_UI_PROMPT'}
    modal = {'kind': 'modal', 'screen': 'Various', 'layer': 'Modal dialog over current screen', 'body_str': '', 'duration_s': 'Until input', 'dismiss': 'Button press',
             'priority': 5, 'queue_rule': 'Blocks input; pauses game in single player', 'sfx_hook': 'SFX_UI_MODAL'}
    pn = 0
    pn += ctx.append('ui/popups.csv', dict(prm, popup_id='PRM_CARRY_BODY', trigger='Body of a takedown or sneak kill within reach', title_str='STR_PROMPT_CARRY'))
    pn += ctx.append('ui/popups.csv', dict(prm, popup_id='PRM_HIJACK', trigger='Vehicle hijack window open (vehicle_hijack rules)', title_str='STR_PROMPT_HIJACK'))
    pn += ctx.append('ui/popups.csv', dict(prm, popup_id='PRM_DOOR_ONEWAY', trigger='Shortcut door seen from its opening side', title_str='STR_PROMPT_SHORTCUT'))
    pn += ctx.append('ui/popups.csv', dict(modal, popup_id='CNF_FIRSTBOOT', trigger='First boot: language, subtitle size, brightness, colorblind and Assist on one screen', title_str='', buttons='Confirm'))
    pn += ctx.append('ui/popups.csv', dict(modal, popup_id='CNF_CHOICE', trigger='Story choice with consequence', title_str='', buttons=''))
    pn = sum(1 for r in T['ui/popups.csv'][1] if r[0] in ('PRM_CARRY_BODY', 'PRM_HIJACK', 'PRM_DOOR_ONEWAY', 'CNF_FIRSTBOOT', 'CNF_CHOICE'))
    c = _count(res)
    rep['DR-SYS-007'] = ('conflict' if c['clash'] else 'applied', 'ui/strings_data.csv + ui/popups.csv',
        f"{c['added']} STR_STL_* added from stealth_states.csv ({c['same']} present, {c['clash']} clashed); {pn} of 5 popups in place (none existed before), prompts reuse STR_PROMPT_CARRY/HIJACK/SHORTCUT and CNF_FIRSTBOOT/CNF_CHOICE have no title text yet (writing pass).")
    rep['DR-SYS-008'] = ('skipped', 'assets/asset_hooks.csv -> shardfall-assets.xlsx', 'outside data/: owned by the asset thread (shardfall-assets.xlsx); asset_hooks.csv is generated by link.py from data cells.')
    # DR-SYS-009 AI detection columns (after DR-SIM-02 so guards get FAC_TOWN values)
    sfr = {r['fac_id']: r for r in ctx.design_rows('systems/stealth_faction_rules.csv')}
    fmap = {'Hollowed': 'FAC_HOLLOWED', 'Remnant': 'FAC_REMNANT', 'Thorn Clans': 'FAC_THORN', 'Choirborn': 'FAC_CHOIRBORN', 'Creature': 'CREATURE', 'Town': 'FAC_TOWN'}
    k = 'actors/ai_profiles.csv'; n = 0
    for r in ctx.rows(k):
        f = sfr.get(fmap.get(r['Faction'], ''))
        for col, src in (('sight_gain_mult', 'sight_gain_mult'), ('hearing_mult', 'hearing_radius_mult'), ('shout_radius_m', 'shout_alert_radius_m')):
            ctx.edit(k, r['AIP_ID'], col, f[src] if f else '')
        n += bool(f)
    rep['DR-SYS-009'] = ('applied', k, f'sight_gain_mult, hearing_mult and shout_radius_m added from stealth_faction_rules.csv for {n} profiles by faction; AIP_BOSS has no faction row and stays blank.')
    # DR-SYS-010 / 011 verified in data
    tgt = {(r['ACT_ID'], r['Level']): r for r in ctx.design_rows('systems/enemy_curve_target.csv')}
    ok = sum(1 for r in ctx.rows('actors/enemy_stats_by_level.csv') if (r['ACT_ID'], r['Level']) in tgt and r['HP'] == tgt[(r['ACT_ID'], r['Level'])]['HP_target'])
    rep['DR-SYS-010'] = ('skipped', 'actors/enemy_stats_by_level.csv', f'already applied: rev 2 targets in the actors generator; {ok} of {len(tgt)} enemy_curve_target rows match data HP, and validate checks HP rises every level.')
    imp = {r['class_id']: r['impact'] for r in ctx.rows('items/firearm_classes.csv')}
    rep['DR-SYS-011'] = ('skipped', 'items/firearm_classes.csv', f"already applied in the items generator: impact PST {imp['ITM_CLS_PST']}, ARF {imp['ITM_CLS_ARF']}, SMG {imp['ITM_CLS_SMG']} (x1.30, x1.35, x1.30; README design choice 27).")
    rep['DR-SYS-012'] = ('skipped', 'ui/popups.csv', 'info only: no new TUT_ popups requested; order and timing live in design/systems/onboarding_first2h.csv.')
    for r in ctx.design_rows('systems/data-requests.csv'):
        st, tg, why = rep[r['dr_id']]; ctx.log(SY, r['dr_id'], st, tg, why)


# ------------------------------------------------------------------ loops
def loops(T, ctx):
    rep = {}
    df, ef = _row(ctx, 'actors/derived_formulas.csv', 'FRM_EMBER_DROP'), _row(ctx, 'actors/economy_formulas.csv', 'ECOF_DROP')
    ok1 = df['Formula'].startswith('Ember = 0.2 x') and ef['Expression'].startswith('0.2 x')
    rep['DR-001'] = ('skipped', 'FRM_EMBER_DROP + ECOF_DROP', 'already applied: both formulas carry the 0.2 multiplier.' if ok1 else 'already applied in the actors generator (README 20).')
    rep['DR-002'] = ('skipped', 'ECOF_BOSS', 'already applied: ECOF_BOSS has Site 0.15 and Field 0.8.' if 'Site 0.15' in _row(ctx, 'actors/economy_formulas.csv', 'ECOF_BOSS')['Expression'] else 'already applied (README 20).')
    # DR-003
    k = 'actors/economy_currencies.csv'; r = _row(ctx, k, 'ECO_CUR_SEAL')
    add = 'over-cap Seals convert to Ember at 500 each (DR-003)'
    if add not in r['Rules']: ctx.edit(k, 'ECO_CUR_SEAL', 'Rules', r['Rules'] + '; ' + add)
    rep['DR-003'] = ('applied', 'actors/economy_currencies.csv ECO_CUR_SEAL', 'Seal rules now say Seals earned over the weekly cap convert to Ember at 500 each.')
    # DR-004
    ctx.edit('actors/economy_formulas.csv', 'ECOF_SEALS', 'Example', 'Weekly cap 100')
    ctx.edit('actors/challenge_scaling.csv', 'CHL_HOLLOWCIT', 'Rewards', 'Featured Citadel 15 Seals (ITM_LT_ENDGAME_HOLLOWED_CITADEL)')
    rep['DR-004'] = ('applied', 'ECOF_SEALS + CHL_HOLLOWCIT', 'Seals x3 removed from CHL_HOLLOWCIT (featured Citadel 15 Seals, matching the loot table) and ECOF_SEALS example set to weekly cap 100.')
    rep['DR-005'] = ('conflict', 'world/locations.csv', 'design/world/locations.csv wins (frozen LOC_ IDs): Anchors are LOC_ANC_REG_* (251 placed) and there is one Relay Tower per region (LOC_RELAY_REG_01..06), so LOC_ANCHOR_*/LOC_TOWER_* are not added.')
    # DR-006
    k = 'items/firearm_classes.csv'
    for r in ctx.rows(k):
        ctx.edit(k, r['class_id'], 'swap_from_melee_ms', 400 + int(r['ads_ms'])); ctx.edit(k, r['class_id'], 'swap_from_firearm_ms', 350)
    rep['DR-006'] = ('applied', k, 'swap_from_melee_ms (400 + ads_ms) and swap_from_firearm_ms (350) columns added to every firearm class.')
    # DR-007
    k = 'actors/creatures.csv'
    for col, v in (('Mount walk m/s', 2.5), ('Mount trot m/s', 7), ('Mount gallop m/s', 14), ('Mount double jump m', 4), ('Mount glide drop m per 10 m', 1.5)):
        ctx.edit(k, 'ACT_CRT_STRIDER', col, v)
    rep['DR-007'] = ('applied', 'actors/creatures.csv ACT_CRT_STRIDER', 'Strider mount speeds added: walk 2.5, trot 7, gallop 14 m/s, double jump 4 m, glide 1.5 m drop per 10 m.')
    # DR-008 Unkindling
    new = ctx.append('items/consumables.csv', {'item_id': 'ITM_CON_UTL_UNKINDLE', 'name': 'Unkindling', 'category': 'Utility', 'effect': 'Resets attributes and perks',
                     'magnitude': '', 'duration_s': 0, 'max_stack': '', 'buy_price': 25000, 'sell_price': 6250, 'weight': '', 'use_time_s': '', 'craft_recipe': '',
                     'icon': 'UI_ICON_CON_UTL_UNKINDLE', 'vfx': 'VFX_CON_UTL_UNKINDLE', 'sfx': 'SFX_CON_UTL_UNKINDLE'})
    _item(ctx, 'ITM_CON_UTL_UNKINDLE', 'Unkindling', 'consumables.csv', 'Resets attributes and perks.')
    _append_multi(ctx, 'items/vendors.csv', [{'vendor_id': 'ITM_VEN_LANTERNCHURCH', 'vendor_name': 'Lantern Church', 'location': 'LOC_LANTERN_HOLD', 'item_id': 'ITM_CON_UTL_UNKINDLE',
                                              'price': 25000, 'currency': 'ITM_CUR_EMBER', 'stock': '', 'restock_game_h': '', 'unlock': ''}], ['vendor_id', 'item_id'])
    k = 'actors/bosses.csv'; col = 'Drops (item refs)'
    for r in ctx.rows(k):
        if r['Class'] == 'Shard-bearer' and 'ITM_CON_UTL_UNKINDLE' not in r[col]:
            ctx.edit(k, r['ACT_ID'], col, r[col] + '; ITM_CON_UTL_UNKINDLE x1 (first kill)')
    rep['DR-008'] = ('applied' if new else 'skipped', 'items/consumables.csv ITM_CON_UTL_UNKINDLE',
        'Unkindling respec item added: 1 per Shard-bearer first kill (bosses.csv drops), sold by a new Lantern Church vendor row for 25,000 Ember.' if new else 'already applied.')
    # DR-009 strikes
    wl = {r['loc_id']: r['name'] for r in ctx.design_rows('world/locations.csv') if r['kind'] == 'Strike'}
    field = {}
    for r in ctx.rows('actors/bosses.csv'):
        if r['Class'] == 'Field': field.setdefault(r['Region'], []).append(r['ACT_ID'])
    hdr = ['stk_id', 'name', 'region', 'level', 'players', 'coop_id', 'bosses', 'loot_table', 'seals', 'notes']
    rows = []
    for i in range(1, 7):
        rg = f'REG_0{i}'; nm = wl.get(f'LOC_END_STRIKE_0{i}', f'Strike {i}')
        rows.append([f'STK_0{i}', nm, rg, 80, 3, 'COOP_STRIKE_3', ' '.join(field.get(rg, [])), 'ITM_LT_ENDGAME_STRIKE', 10, 'Name from the Strike location in design/world/locations.csv'])
    rows.append(['STK_S1', 'The Sunken Index', 'REG_U', 80, 3, 'COOP_STRIKE_3', '', 'ITM_LT_ENDGAME_STRIKE', 10, 'Season 1 Strike (DR-LO-13, decided 2026-10-03): layout in design/levels/multiplayer mp_maps.csv (The Sunken Index); featured week 1 (loops season_calendar.csv); bosses set with the season'])
    T['world/strikes.csv'] = [hdr, [[str(x) for x in r] for r in rows]]
    for r in rows: _str(ctx, f'STR_{r[0]}_NAME', r[1], 'Data name', 'Strike')
    rep['DR-009'] = ('applied', 'world/strikes.csv', 'world/strikes.csv added: STK_01..06 (level 80, 3 players, the region\'s two Field bosses, ITM_LT_ENDGAME_STRIKE, names from design/world) and STK_S1.')
    rep['DR-010'] = ('conflict', 'actors/coop_scaling.csv', 'Plan wins: Strikes are exactly 3 players (COOP_STRIKE_3 already in data, README 19) and COOP_OW_4 is already open world only, so COOP_STRIKE_1..2 are not added.')
    rep['DR-011'] = ('conflict', 'items/shardborn.csv', 'Plan wins: Shardborn stay at the plan\'s 30 (README 21); seasonal ITM_SHB_S* IDs are not reserved in shardborn.csv until a season adds them.')
    res = _str(ctx, 'STR_COOP_REJOIN', 'Reconnect within {VAR_s} s to keep your slot.', 'HUD', '90 s rejoin window for dedicated activities (loops 07)', 'VAR_s')
    rep['DR-012'] = ('applied' if res == 'added' else 'skipped', 'ui/strings_data.csv',
        'Added STR_COOP_REJOIN for the 90 s rejoin window; the 30 s bleed-out already exists (PRM_DOWNED 30 s, STR_PRM_DOWNED_T) and NTF_SEASON_RANK exists.' if res == 'added' else 'already applied: STR_COOP_REJOIN, PRM_DOWNED and NTF_SEASON_RANK exist.')
    k = 'actors/level_curve.csv'
    for lv in range(71, 81): ctx.edit(k, str(lv), 'Matching region band', 'The Quiet')
    rep['DR-013'] = ('applied', k, 'Levels 71-80 now labelled The Quiet; 81-100 stay Endgame.')
    rep['DR-014'] = ('skipped', 'FRM_MORALE', 'already applied: FRM_MORALE has Fodder flee 6 s at 60% chance on Leader death.' if '60% chance' in _row(ctx, 'actors/derived_formulas.csv', 'FRM_MORALE')['Formula'] else 'already applied (README 20).')
    nt = sum(1 for r in ctx.rows('world/locations.csv') if r['loc_id'].startswith('LOC_TOWN_REG_'))
    rep['DR-015'] = ('skipped', 'world/locations.csv', f'already applied: {nt} towns, 2 to 3 per region (README 15).')
    nshb = len(T['items/shardborn.csv'][1]); nmel = len(T['items/melee_classes.csv'][1]); r1 = _row(ctx, 'world/regions.csv', 'REG_01')['name']
    rep['DR-016'] = ('skipped', 'items/, world/, data/README', f'already applied: {nshb} Shardborn and {nmel} melee classes; the Region 1 rename is rejected because the Visual Bible name {r1} stays (README 1).')
    rep['DR-017'] = ('skipped', 'world/ (defeat_scenarios.csv)', 'nothing to apply: no design file defines Defeat Mode scenarios, so no rows can be built without inventing them.')
    rep['DR-018'] = ('skipped', 'actors/ (expansion power track)', 'nothing to apply: no expansion power track rows are defined in design/loops; note only.')
    for r in ctx.design_rows('loops/data-requests.csv'):
        st, tg, why = rep[r['dr_id']]; ctx.log(L, r['dr_id'], st, tg, why)


# ------------------------------------------------------------------ controls
def controls(T, ctx):
    rep = {}
    # CTL-009 option names (no description text in settings.csv)
    res, clash = [], []
    for r in ctx.design_rows('controls/settings.csv'):
        if r['string_id'].startswith('NEW: '):
            sid = r['string_id'][5:]
            res.append(_str(ctx, sid, sid[8:].replace('_', ' ').title().replace('Fov 1P', 'FOV 1P'), 'Options', f"{r['tab']}: {r['range']}, default {r['default']}"))
            if res[-1] == 'clash': clash.append(sid)
    c = _count(res)
    rep['CTL-009'] = ('conflict' if c['clash'] else 'applied', 'ui/strings_data.csv',
        f"{c['added']} option names added from their IDs ({c['same']} present, {c['clash']} clashed: {', '.join(clash) or 'none'}, existing text kept{'; STR_OPT_PRESET is the Graphics Preset string, so the input preset option needs its own ID' if 'STR_OPT_PRESET' in clash else ''}); the _D descriptions are not added because settings.csv has no description text.")
    # CTL-010 preset and action names
    res = [_str(ctx, 'STR_PRESET_' + r['preset_id'][4:], r['name'], 'Remap', 'Input preset') for r in ctx.design_rows('controls/input_presets.csv')]
    for r in ctx.design_rows('controls/input_actions.csv'):
        res.append(_str(ctx, 'STR_ACTION_' + r['action_id'][3:], r['action'].replace('_', ' ').capitalize(), 'Remap', f"Action in {r['ctx_id']}"))
    c = _count(res)
    rep['CTL-010'] = ('conflict' if c['clash'] else 'applied', 'ui/strings_data.csv',
        f"{c['added']} remap strings added (STR_PRESET_<preset suffix> from input_presets names, STR_ACTION_<action suffix> from the action column), {c['same']} present, {c['clash']} clashed.")
    # CTL-004 feel_id
    afm = {r['source_id']: r['feel'] for r in ctx.design_rows('controls/attack_feel_map.csv')}
    k = 'items/melee_frame_data.csv'; n = 0
    for r in ctx.rows(k):
        ctx.edit(k, r['attack_id'], 'feel_id', afm.get(r['attack_id'], '')); n += r['attack_id'] in afm
    # CTL-006 timing stats (parry frames, assist and riposte already live in STAT_PARRY)
    tim = {r['id']: r for r in ctx.design_rows('controls/input_timing.csv')}
    a = ctx.append('actors/player_base_stats.csv', {'STAT_ID': 'STAT_GUARD_COUNTER_WINDOW', 'Stat': 'Guard counter window', 'Base': 20, 'Per Vigor point': 0, 'Per attribute point': 0,
        'Attribute': '-', 'Cap': 20, 'Regen / rule': tim['TIM_GUARD_COUNTER']['notes'], 'Notes': '60 fps frames (CTL-006)'})
    b = ctx.append('actors/player_base_stats.csv', {'STAT_ID': 'STAT_COMMIT_FRAME', 'Stat': 'Animation commit frame', 'Base': 6, 'Per Vigor point': 0, 'Per attribute point': 0,
        'Attribute': '-', 'Cap': 6, 'Regen / rule': tim['TIM_COMMIT']['notes'], 'Notes': '60 fps frames (CTL-006)'})
    rep['CTL-006'] = ('applied' if a or b else 'skipped', 'actors/player_base_stats.csv',
        'STAT_GUARD_COUNTER_WINDOW (20) and STAT_COMMIT_FRAME (6) added; parry frames 6, Assist +4 and riposte 60 already live in STAT_PARRY, so no duplicate stats were added.')
    # CTL-008 lock points
    k = 'actors/bosses.csv'
    for r in ctx.rows(k):
        wp = r['Weak points / parts']
        pts = ['Head', 'Core']
        for p in ([] if wp.startswith('None') else re.split(r'[;,]', wp)):
            p = re.sub(r'\s+x\d.*$|\s*\(.*$|\s+\d+(\s+each)?$', '', p.strip()).strip()
            if re.search(r'whichever|shared health', p, re.I): continue   # rules, not body parts
            if p and p.lower() not in [x.lower() for x in pts]: pts.append(p[0].upper() + p[1:])
        ctx.edit(k, r['ACT_ID'], 'lock_points', '; '.join(pts))
    rep['CTL-008'] = ('applied', k, 'lock_points column added to every boss: Head and Core plus the named Weak points / parts (camera_rules LOCK_POINTS).')
    # CTL-001..003 new tables
    specs = [(f'input/{f}', f'controls/{f}') for f in ['input_actions.csv', 'input_contexts.csv', 'input_timing.csv', 'input_presets.csv', 'input_preset_bindings.csv', 'aim_assist.csv']]
    specs += [(f'feel/{f}', f'controls/{f}') for f in ['feel_hit_types.csv', 'feel_weapon_class.csv', 'feel_matrix.csv', 'shake_presets.csv', 'rumble_presets.csv', 'trigger_effects.csv', 'attack_feel_map.csv']]
    specs += [(f'camera/{f}', f'controls/{f}') for f in ['camera_modes.csv', 'camera_weapon_offsets.csv', 'camera_rules.csv']]
    dropped = _new_tables(ctx, specs)
    sub = lambda p: {k: v for k, v in dropped.items() if k.startswith(p)}
    rep['CTL-001'] = ('applied', 'data/input/', 'input/ tables added: input_actions, input_contexts, input_timing, input_presets, input_preset_bindings, aim_assist' + _drop_note(sub('input/')) + '.')
    rep['CTL-002'] = ('applied', 'data/feel/', 'feel/ tables added: feel_hit_types, feel_weapon_class, feel_matrix, shake_presets, rumble_presets, trigger_effects, attack_feel_map' + _drop_note(sub('feel/')) + '.')
    rep['CTL-003'] = ('applied', 'data/camera/', 'camera/ tables added: camera_modes, camera_weapon_offsets, camera_rules' + _drop_note(sub('camera/')) + '.')
    rep['CTL-004'] = ('applied', 'items/melee_frame_data.csv', f'feel_id column added from attack_feel_map.csv; {n} of {len(T["items/melee_frame_data.csv"][1])} attacks mapped, each resolving to feel/feel_matrix.csv.')
    rep['CTL-005'] = ('skipped', 'items/melee_classes.csv', f'already applied: melee_classes has {len(T["items/melee_classes.csv"][1])} classes including ITM_CLS_GAX and ITM_CLS_GHM.')
    rep['CTL-007'] = ('skipped', 'world/vehicles.csv', 'already applied by DR-SYS-005 in this module: world/vehicles.csv has VEH_SKIMMER, VEH_HAULER and VEH_FLYER with seats, speeds, boost, part health and turret overheat.')
    rep['CTL-011'] = ('skipped', 'ui/README.md', 'outside data tables: ui/README.md is documentation owned by the ui thread; BTN is already an allowed runtime token prefix in validate.py.')
    rep['CTL-012'] = ('skipped', 'shardfall-assets.xlsx', 'outside data/: owned by the asset thread (shardfall-assets.xlsx glyphs).')
    vfx = sorted({t for r in T['feel/feel_hit_types.csv'][1] for c in r for t in TOK.findall(c) if t.startswith('VFX_')}) if 'feel/feel_hit_types.csv' in T else []
    rep['CTL-013'] = ('applied', 'assets/asset_hooks.csv', f'{len(vfx)} VFX hooks come from feel/feel_hit_types.csv vfx_hook and are registered by the link.py hook pass; templated names ({{DMG}}, {{Element}}, {{Status}}) register only their fixed stem.')
    rep['CTL-014'] = ('skipped', 'assets/asset_hooks.csv (HPT_)', 'outside this module: a new HPT_ hook prefix needs link.py (main thread) and the audio thread; until then the HPT_ columns are left out of the feel tables.')
    rep['CTL-015'] = ('skipped', 'design/audio/event_map.csv', 'outside data/: owned by design/audio (audio thread).')
    rep['CTL-016'] = ('skipped', 'design/tech/01-code-architecture.md', 'outside data/: owned by design/tech (tech thread).')
    rep['CTL-017'] = ('skipped', 'design/production/accessibility_checklist.csv', 'outside data/: owned by design/production (production thread).')
    rep['CTL-018'] = ('skipped', 'design/production/accessibility_checklist.csv', 'outside data/: owned by design/production (production thread).')
    rep['CTL-019'] = ('skipped', 'world design', 'note only: swimming is surface only (CTX_SWIM in input/input_contexts.csv); the world thread may override.')
    for r in ctx.design_rows('controls/data-requests.csv'):
        st, tg, why = rep[r['id']]; ctx.log(C, r['id'], st, tg, why)


def apply(T, ctx):
    simulation(T, ctx)
    systems(T, ctx)
    loops(T, ctx)
    controls(T, ctx)
