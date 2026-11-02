"""Front-end and string requests: accessibility, companion, forgeframe, frontend, platform, social, research, liveops, art, licensing.
Merges the design strings files into ui/strings_data.csv, popups into ui/popups.csv, cosmetics into items/cosmetics.csv (+ items_index),
and adds ui/achievements.csv (ACH_) and world/pvp_maps.csv (PVP_MAP_). Re-runs cleanly: every append is keyed."""
import colorsys, math, re

FILES = ['accessibility/data-requests.csv', 'companion/data-requests.csv', 'forgeframe/data-requests.csv', 'frontend/data-requests.csv',
         'platform/data-requests.csv', 'social/data-requests.csv', 'research/data-requests.csv', 'liveops/data-requests.csv',
         'art/data-requests.csv', 'licensing/data-requests.csv']

TOK = re.compile(r'(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![a-z0-9])')
AP = ('MESH', 'VFX', 'SFX', 'ANIM', 'UI', 'ARENA')
PRICE_CAP = 9.99            # highest real-money price for a single cosmetic item ($1.99-$9.99)
BUNDLE_CAP = 19.99          # season bundles: hard cap $19.99 and below the summed item prices (continuity pass 2026-10-03)

# ---------------------------------------------------------------- dye color rules (data/README decisions 28 and 29, same math as items/gen_items.py)
HUE = {'Red': (340, 20), 'Crimson': (340, 15), 'Wine': (330, 10), 'Rust': (5, 30), 'Orange': (15, 40), 'Copper': (15, 35), 'Amber': (30, 50), 'Saffron': (35, 50),
       'Gold': (35, 55), 'Brass': (35, 55), 'Bronze': (20, 45), 'Yellow': (40, 60), 'Olive': (50, 75), 'Moss': (70, 110), 'Pine': (120, 160), 'Jade': (130, 165),
       'Verdigris': (145, 180), 'Teal': (165, 190), 'Cyan': (180, 200), 'Sky': (195, 220), 'Cerulean': (195, 215), 'Blue': (200, 230), 'Cobalt': (210, 230),
       'Navy': (210, 235), 'Lavender': (250, 280), 'Violet': (260, 290), 'Plum': (290, 330), 'Pink': (320, 350), 'Clay': (10, 30)}
RESERVED = {'Health red': '#D4483F', 'Ward blue': '#4F8FE6', 'Breath green': '#7CC46A', 'Lens cyan': '#8FE3EE', 'Ember amber': '#E8873A', 'Signal red': '#FF3B30'}
def _lab(hx):
    c = [int(hx[k:k+2], 16) / 255 for k in (1, 3, 5)]; c = [((v+0.055)/1.055)**2.4 if v > 0.04045 else v/12.92 for v in c]
    x = (0.4124*c[0]+0.3576*c[1]+0.1805*c[2])/0.95047; y = 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]; z = (0.0193*c[0]+0.1192*c[1]+0.9505*c[2])/1.08883
    f = lambda t: t**(1/3) if t > 0.008856 else 7.787*t+16/116
    return 116*f(y)-16, 500*(f(x)-f(y)), 200*(f(y)-f(z))
def _de(a, b): return sum((p-q)**2 for p, q in zip(_lab(a), _lab(b)))**0.5
def _hls(hx): return colorsys.rgb_to_hls(*(int(hx[k:k+2], 16) / 255 for k in (1, 3, 5)))
def _hex(h, l, s): return '#%02X%02X%02X' % tuple(round(v*255) for v in colorsys.hls_to_rgb(h, l, s))
def clear_reserved(hx):
    h, l, s = _hls(hx)
    for step in range(40):
        for dl in (-0.03*step, 0.03*step):
            for ds in (0, -0.04*step):
                cand = _hex(h, min(0.95, max(0.05, l+dl)), max(0.15, min(1, s+ds)))
                if min(_de(cand, c) for c in RESERVED.values()) >= 20: return cand
    return hx
def fix_dye(name, hx):
    """Returns (hex, what changed). Hue moves into the range its name word sets (README 28); then lightness/saturation step clear of reserved colors (README 29)."""
    h, l, s = _hls(hx); why = []
    for w in name.replace(' Dye', '').split():
        if w in HUE:
            lo, hi = HUE[w]; hd = h*360
            ok = lo <= hd <= hi if lo < hi else (hd >= lo or hd <= hi)
            if not ok or s <= 0.12:
                mid = ((lo + hi) / 2) if lo < hi else ((lo + hi + 360) / 2) % 360
                h = mid / 360; s = max(s, 0.35); why.append(f'hue to {w}')
    new = _hex(h, l, s) if why else hx
    if min(_de(new, c) for c in RESERVED.values()) < 20: new = clear_reserved(new); why.append('cleared reserved color')
    return new, why


def apply(T, ctx):
    S = {}            # str_id -> (table, text)
    for k in ('ui/strings.csv', 'ui/strings_data.csv'):
        for r in ctx.rows(k): S[r['str_id']] = (k, r['text_en'])
    defined = ctx.all_ids()
    for h, _ in T.values(): defined.update(TOK.findall(','.join(h)))

    def add_string(r):
        """'added' | 'same' | 'clash'."""
        sid = r['str_id']
        if sid in S: return 'same' if S[sid][1] == r['text_en'] else 'clash'
        mc = r.get('max_chars') or math.ceil(len(r['text_en']) * 1.4)
        note = r.get('notes', '')
        for t in TOK.findall(note):          # design-side IDs in a free-text note (e.g. campaign ending IDs) that data does not define
            if t not in defined and t.split('_')[0] not in AP: note = note.replace(f' ({t})', '').replace(t, '').strip()
        ctx.append('ui/strings_data.csv', {'str_id': sid, 'screen': r.get('screen', ''), 'text_en': r['text_en'], 'max_chars': mc,
                                           'tokens': r.get('tokens', ''), 'notes': note})
        S[sid] = ('ui/strings_data.csv', r['text_en']); defined.add(sid); return 'added'

    def change_string(sid, text):
        k = S[sid][0]
        if S[sid][1] == text: return False
        ctx.edit(k, sid, 'text_en', text); ctx.edit(k, sid, 'max_chars', math.ceil(len(text) * 1.4)); S[sid] = (k, text); return True

    def merge_strings(rel, skip=(), changes_ok=False):
        rows = ctx.design_rows(rel); n = {'added': 0, 'same': 0, 'clash': 0, 'changed': 0, 'skip': 0}; clash = []
        for r in rows:
            if r['str_id'] in skip: n['skip'] += 1; clash.append(r['str_id']); continue
            if changes_ok and r.get('action') == 'change' and r['str_id'] in S:
                n['changed' if change_string(r['str_id'], r['text_en']) else 'same'] += 1; continue
            res = add_string(r); n[res] += 1
            if res == 'clash': clash.append(r['str_id'])
        return len(rows), n, clash

    def log_strings(src, rid, rel, total, n, clash, why=''):
        parts = [f"{n['added']} strings added"]
        if n['changed']: parts.append(f"{n['changed']} text changes")
        if n['same']: parts.append(f"{n['same']} already present")
        if clash:
            ctx.log(src, rid, 'conflict', 'ui/strings_data.csv', f"{', '.join(parts)} from {rel} ({total} rows); {len(clash)} IDs clashed and kept the existing text ({' '.join(clash)}){why}.")
        else:
            ctx.log(src, rid, 'applied', 'ui/strings_data.csv', f"applied: {', '.join(parts)} from {rel} ({total} rows).")

    # popups ------------------------------------------------------
    PH = T['ui/popups.csv'][0]
    tmpl = {}
    for r in ctx.rows('ui/popups.csv'): tmpl.setdefault(r['kind'], r)
    KINDS = set(tmpl)
    KIND_MAP = {'confirm': 'modal'}
    TRIGGER_FIX = {'LAB_BUILDFLAG': None, 'OPT_TELEMETRY': 'STR_OPT_TELEMETRY', 'PSH_SIG_ACCEPTED': 'STR_APP_PSH_SIG_ACCEPTED_T'}

    def fix_cell(c):
        for t, rep in TRIGGER_FIX.items():
            if t in c: c = c.replace(f' ({t})', '') if rep is None else c.replace(t, rep)
        return c

    def add_popup(d):
        """'added' | 'same' | 'clash'."""
        d = dict(d); d['kind'] = KIND_MAP.get(d['kind'], d['kind'])
        assert d['kind'] in KINDS, d
        base = tmpl[d['kind']]
        row = {c: fix_cell(d[c]) if c in d else (base[c] if c in ('layer', 'duration_s', 'dismiss', 'priority', 'queue_rule', 'sfx_hook') else '') for c in PH}
        if d['kind'] == 'prompt' and row['buttons'] and 'duration_s' not in d:      # answered prompts wait for input, like the modal rows
            row['duration_s'], row['dismiss'] = 'Until input', 'Button press'
        for c in ('title_str', 'body_str'):
            assert not row[c] or row[c] in S, (row['popup_id'], row[c])
        if row['popup_id'] in ctx.ids('ui/popups.csv'):
            old = next(r for r in ctx.rows('ui/popups.csv') if r['popup_id'] == row['popup_id'])
            return 'same' if all(old[c] == row[c] for c in PH) else 'clash'
        ctx.append('ui/popups.csv', row); defined.add(row['popup_id']); return 'added'

    def merge_popups(src, rid, rel, rows=None, note=''):
        rows = rows if rows is not None else ctx.design_rows(rel.replace('design/', '', 1))
        res = [(r['popup_id'], add_popup(r)) for r in rows]
        a = sum(1 for _, x in res if x == 'added'); s = sum(1 for _, x in res if x == 'same'); cl = [p for p, x in res if x == 'clash']
        txt = f"{a} popups added" + (f", {s} already present" if s else '') + f" from {rel}{note}"
        if cl: ctx.log(src, rid, 'conflict', 'ui/popups.csv', f"{txt}; {len(cl)} IDs clashed with existing rows and kept them ({' '.join(cl)}).")
        else: ctx.log(src, rid, 'applied', 'ui/popups.csv', f"applied: {txt}.")

    # cosmetics ---------------------------------------------------
    def add_cosmetic(d):
        new = ctx.append('items/cosmetics.csv', d)
        ctx.append('items/items_index.csv', {'item_id': d['item_id'], 'name': d['name'], 'category': 'Cosmetic', 'rarity': '', 'file': 'cosmetics.csv'})
        add_string({'str_id': f"STR_{d['item_id']}_NAME", 'screen': 'Item name', 'text_en': d['name'], 'notes': 'Cosmetic'})
        defined.add(d['item_id']); return new

    def outside(src, rid, owner, extra=''):
        ctx.log(src, rid, 'skipped', owner, f"outside data/: owned by {owner}{extra}.")

    def hooks_note(text):
        hs = sorted({t for t in TOK.findall(text) if t.split('_')[0] in AP})
        refs = set()
        for k, (h, rr) in T.items():
            if k == 'assets/asset_hooks.csv': continue
            for r in rr:
                for c in r[1:]: refs.update(TOK.findall(c))
        got = [x for x in hs if x in refs]
        return hs, got

    # ================================================================ accessibility
    A = 'accessibility/data-requests.csv'
    tot, n, cl = merge_strings('accessibility/strings_requests.csv', changes_ok=True)
    log_strings(A, 'ACC-DR-001', 'design/accessibility/strings_requests.csv', tot, n, cl)
    merge_popups(A, 'ACC-DR-002', 'design/accessibility/popups_requests.csv')
    ctx.log(A, 'ACC-DR-003', 'skipped', 'actors/difficulty_modifiers.csv',
            'target table no longer exists: the plan has no campaign difficulty menu and data/README decision 17 removed difficulty_modifiers.csv, so Assist is specified only in design/accessibility/settings_menu.csv.')
    if ctx.append('actors/derived_formulas.csv', {'FRM_ID': 'FRM_GAME_SPEED', 'Name': 'Game Speed',
                  'Formula': 'Global time dilation = Assist Game Speed (1.0, 0.9, 0.8, 0.75); forced to 1.0 when player count > 1',
                  'Notes / source table': 'Assist Mode sub-option, solo only (design/accessibility/settings_menu.csv)'}):
        ctx.log(A, 'ACC-DR-004', 'applied', 'actors/derived_formulas.csv', 'applied: FRM_GAME_SPEED added with the requested formula.')
    else:
        ctx.log(A, 'ACC-DR-004', 'skipped', 'actors/derived_formulas.csv', 'already applied: FRM_GAME_SPEED exists.')
    acc_hook_text = ctx.design_rows(A)[4]['requested_value']

    ctx.log(A, 'ACC-DR-006', 'skipped', 'design/audio', 'outside data/: owned by the audio thread (design/audio): Audio Description VO and ping-wheel recording.')
    outside(A, 'ACC-DR-007', 'the production thread (design/production/accessibility_checklist.csv)')

    # ================================================================ platform strings before social (rich presence owner), after accessibility (Options owner)
    P = 'platform/data-requests.csv'
    tot, n, cl = merge_strings('platform/platform_strings.csv', skip=('STR_RP_ARENA',))
    log_strings(P, 'DR-PLT-001', 'design/platform/platform_strings.csv', tot, n, cl,
                why='; STR_OPT_TRIGGERS keeps the existing "Adaptive Triggers", STR_OPT_TRIGGERS_D keeps the accessibility text (settings_menu.csv owns Options), '
                    'and STR_RP_ARENA was not added because {SCORE_A}/{SCORE_B} are not valid runtime tokens, so social\'s STR_RP_ARENA is used')

    # ================================================================ companion
    C = 'companion/data-requests.csv'
    tot, n, cl = merge_strings('companion/strings_companion.csv')
    log_strings(C, 'DR-APP-01', 'design/companion/strings_companion.csv', tot, n, cl)
    merge_popups(C, 'DR-APP-02', 'design/companion/popups_companion.csv', note=' (PSH_SIG_ACCEPTED in a trigger points at its push string STR_APP_PSH_SIG_ACCEPTED_T)')
    outside(C, 'DR-APP-03', 'the tech thread (design/tech/02-online.md)')
    outside(C, 'DR-APP-04', 'the systems and frontend threads (design/systems, design/frontend inventory)')
    outside(C, 'DR-APP-05', 'the frontend thread (design/frontend Options > Account); its strings and NTF_APP_ORDERS_APPLIED came in with DR-APP-01 and DR-APP-02')
    outside(C, 'DR-APP-06', 'the platform thread (design/platform/platform_features.csv)')
    outside(C, 'DR-APP-07', 'the production thread (design/production)')
    outside(C, 'DR-APP-08', 'the audit thread (design/audit/genre_checklist.csv)')
    outside(C, 'DR-APP-09', 'the liveops thread (design/liveops store_catalog.csv, events_calendar.csv)')
    outside(C, 'DR-APP-10', 'the social thread (design/social limits.csv, 01-social.md)')
    outside(C, 'DR-APP-11', 'the tech thread (design/tech/06-telemetry-crash-liveops.md)')
    outside(C, 'DR-APP-12', 'the asset thread (shardfall-assets.xlsx)')
    outside(C, 'DR-APP-13', 'the accessibility thread (design/accessibility/README.md)')
    outside(C, 'DR-APP-14', 'the coordinator (master plan)')

    # ================================================================ forgeframe
    F = 'forgeframe/data-requests.csv'
    tot, n, cl = merge_strings('forgeframe/strings_forgeframe.csv')
    log_strings(F, 'STR_FF_*', 'design/forgeframe/strings_forgeframe.csv', tot, n, cl)
    merge_popups(F, 'CNF_FF_* ERR_FF_* NTF_FF_*', 'design/forgeframe/popups_forgeframe.csv',
                 note=' (kind confirm mapped to the existing modal kind; {n} {name} {platform} are lowercase placeholders the validator does not treat as runtime tokens, so the allowed list needs no change)')
    ctx.log(F, 'UI_FF_*', 'skipped', 'assets/asset_hooks.csv',
            'outside data/: owned by the asset thread (shardfall-assets.xlsx); asset_hooks.csv is generated by link.py from hooks that data rows reference, and no data row references the Forgeframe screen or palette UI hooks.')
    ctx.log(F, 'ICON_FF_EMBLEM_*', 'skipped', 'items/cosmetics.csv',
            'nothing concrete to apply: design/forgeframe gives no item IDs or names for the creator emblems and no count for room medal emblems, so adding rows would invent content.')
    ctx.log(F, 'FLG_MOD_*, QST_MOD_*, MOD_<author>_*', 'skipped', 'data/README.md',
            'outside merge modules: data/README.md is edited by the coordinator; prefix reservation passed on in the module report.')
    outside(F, 'Forged character flag', 'the tech thread (design/tech save system)')
    outside(F, 'Chat filter and image moderation', 'the tech thread (design/tech/02-online.md)')

    # ================================================================ frontend
    FE = 'frontend/data-requests.csv'
    tot, n, cl = merge_strings('frontend/strings_frontend.csv')
    log_strings(FE, 'FE-DR-001', 'design/frontend/strings_frontend.csv', tot, n, cl)
    merge_popups(FE, 'FE-DR-002', 'design/frontend/popups_frontend.csv')
    cr = '© {VAR_year} Shardfall Team. All rights reserved.'
    if change_string('STR_TITLE_COPYRIGHT', cr):
        ctx.log(FE, 'FE-DR-003', 'applied', 'ui/strings.csv STR_TITLE_COPYRIGHT', 'applied: (c) replaced with the © sign.')
    else:
        ctx.log(FE, 'FE-DR-003', 'skipped', 'ui/strings.csv STR_TITLE_COPYRIGHT', 'already applied: text already uses the © sign.')
    ch = 0
    for r in ctx.rows('world/regions.csv'):
        if r['reg_id'] in ('REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06'):
            sid = 'STR_TIP_REG_R' + r['reg_id'][-1]
            if sid in S: ch += change_string(sid, f"{r['name']} is meant for level {r['level_min']} to {r['level_max']}.")
    if ch: ctx.log(FE, 'FE-DR-004', 'applied', 'ui/strings.csv STR_TIP_REG_R1..R6', f'applied: {ch} region tips now use the world/regions.csv bands (from actors/region_bands.csv).')
    else: ctx.log(FE, 'FE-DR-004', 'skipped', 'ui/strings.csv STR_TIP_REG_R1..R6', 'already applied: region tips match world/regions.csv.')
    ctx.log(FE, 'FE-DR-005', 'skipped', 'design/audio/event_map.csv', 'outside data/: owned by the audio thread (design/audio/event_map.csv).')
    fe_hook_text = ctx.design_rows(FE)[5]['requested_value']
    outside(FE, 'FE-DR-007', 'the tech thread (design/tech/03-save-ai-world.md)')

    # ================================================================ platform (rest)
    xs = [dict(popup_id='CNF_XS_CONFLICT', kind='modal', screen='Account', trigger='Cross-save conflict: newer progress on this system and in the cloud',
               title_str='STR_XS_CONFLICT_T', body_str='STR_XS_CONFLICT_B', buttons='Keep This System / Keep Cloud'),
          dict(popup_id='CNF_XS_LOCKED', kind='modal', screen='Account', trigger='Cross-save lock held by another system at boot',
               title_str='', body_str='STR_XS_LOCKED', buttons='Play Here / Play Offline'),
          dict(popup_id='PRM_XS_LINK', kind='prompt', screen='Account', trigger='Link prompt: first online boot after the tutorial, and from Options > Account; at most once unprompted',
               title_str='STR_XS_LINK_T', body_str='STR_XS_LINK_B', buttons='Not Now'),
          dict(popup_id='NTF_ENT_GRANTED', kind='toast', screen='Store', trigger='Entitlement granted', title_str='STR_ENT_GRANTED', body_str='', duration_s='5.0'),
          dict(popup_id='INL_INSTALL_WAIT', kind='inline', screen='Various', trigger='Player reaches a streaming boundary whose chunk is still installing',
               title_str='STR_PLAT_INSTALL_WAIT', body_str='')]
    merge_popups(P, 'DR-PLT-002', 'the DR-PLT-002 notes', rows=xs, note=' (strings from platform_strings.csv; layer, dismiss, priority and sound follow the existing rows of each kind)')
    plt3 = ctx.design_rows(P)[2]['notes'] + ' ' + ctx.design_rows(P)[2]['request']
    plt4 = ctx.design_rows(P)[3]['notes']
    # achievements table
    ach = ctx.design_rows('platform/achievements_platform.csv')
    h = list(ach[0].keys()); T['ui/achievements.csv'] = [h, [[r[c] for c in h] for r in ach]]   # derived wholly from design: rebuilt every run
    defined.update(r['ach_id'] for r in ach)
    bad = [r['ach_id'] for r in ach if S.get(r['str_id'], (0, None))[1] != r['name_en']]
    ctx.log(P, 'DR-PLT-006', 'conflict' if bad else 'applied', 'ui/achievements.csv',
            f'applied: new table ui/achievements.csv (prefix ACH_) with the {len(ach)} rows of design/platform/achievements_platform.csv' + (f'; names differ from strings for {bad}' if bad else '; names match STR_ACH_*') + '.')
    ctx.log(P, 'DR-PLT-007', 'skipped', 'design/platform/entitlements.csv',
            'kept in design/platform as the request allows: its liveops_edition, grants and notes columns point at ED_ and EXP_ IDs that data does not define, and there are no per-item ENT_COS_<item> rows for a cosmetics ent_id column to reference (ENT_COS_SHOP is one umbrella row).')

    # ================================================================ social
    SO = 'social/data-requests.csv'
    tot, n, cl = merge_strings('social/strings_social.csv')
    log_strings(SO, 'DR-SOC-01', 'design/social/strings_social.csv', tot, n, cl, why='; platform owns rich presence (rich_presence.csv), so its STR_RP_ text wins')
    merge_popups(SO, 'DR-SOC-02', 'design/social/popups_social.csv')
    emotes = [('CO1', 'Company Salute', 2), ('CO2', 'Raise the Banner', 5), ('CO3', 'Shield Wall', 9)]
    a = 0
    for code, name, lvl in emotes:
        a += add_cosmetic({'item_id': f'ITM_COS_EMT_{code}', 'name': name, 'kind': 'Emote', 'color_hex': '', 'applies_to': 'player' if code != 'CO3' else 'player (group emote, 2-6 players)',
                           'acquisition': f'Company level {lvl} reward', 'price_ember': '', 'price_seals': '', 'price_usd': '', 'tradeable': 0, 'power': 0,
                           'icon': f'UI_ICON_COS_EMT_{code}', 'anim': f'ANIM_EMOTE_{code}'})
    ctx.log(SO, 'DR-SOC-03', 'applied' if a else 'skipped', 'items/cosmetics.csv',
            f'applied: {a} Company emotes added (ITM_COS_EMT_CO1..CO3, Company level 2/5/9, no price, ANIM_EMOTE_CO1..3).' if a else 'already applied: ITM_COS_EMT_CO1..CO3 exist.')
    co = [('ITM_COS_CO_BAN_1', 'Banner Emblems Set 1', 'Banner emblems', 'Company banner (40 emblems)', 1),
          ('ITM_COS_CO_BAN_2', 'Banner Emblems Set 2', 'Banner emblems', 'Company banner (5 emblems)', 3),
          ('ITM_COS_CO_CAPE', 'Cape Trim in Company Colors', 'Cape trim', 'player cape', 4),
          ('ITM_COS_CO_BAN_3', 'Banner Emblems Set 3', 'Banner emblems', 'Company banner (5 emblems)', 6),
          ('ITM_COS_CO_STR', 'Strider Barding in Company Colors', 'Strider skin', 'ACT_CRT_STRIDER (tamed mount)', 7),
          ('ITM_COS_CO_BAN_4', 'Banner Emblems Set 4', 'Banner emblems', 'Company banner (5 emblems)', 8),
          ('ITM_COS_CO_BAN_5', 'Banner Emblems Set 5', 'Banner emblems', 'Company banner (5 emblems and animated banner)', 10)]
    a = 0
    for iid, name, kind, app, lvl in co:
        a += add_cosmetic({'item_id': iid, 'name': name, 'kind': kind, 'color_hex': '', 'applies_to': app, 'acquisition': f'Company level {lvl} reward',
                           'price_ember': '', 'price_seals': '', 'price_usd': '', 'tradeable': 0, 'power': 0, 'icon': f'UI_ICON_{iid[4:]}', 'anim': ''})
    ctx.log(SO, 'DR-SOC-04', 'applied' if a else 'skipped', 'items/cosmetics.csv',
            f'applied: {a} Company-level rewards from design/social/company_levels.csv added (5 banner emblem sets, cape trim, Strider barding; IDs ITM_COS_CO_*, cosmetic only, no price).' if a else 'already applied: ITM_COS_CO_* exist.')
    soc_hook_text = ' '.join(r['hook'] if 'hook' in r else list(r.values())[0] for r in ctx.design_rows('social/asset_hooks_social.csv'))
    # NPC (world/npcs.csv is link-generated but not frozen); LOC rows are frozen by design/world/locations.csv
    steward = ctx.append('world/npcs.csv', {'act_id': 'ACT_NPC_CO_STEWARD', 'name': 'Company Steward', 'role': 'Company Steward (opens the Company screen)', 'fac_id': '',
                                            'location': 'Lantern Hold', 'vendor_id': '', 'str_id': 'STR_ACT_NPC_CO_STEWARD_NAME'})
    add_string({'str_id': 'STR_ACT_NPC_CO_STEWARD_NAME', 'screen': 'NPC name', 'text_en': 'Company Steward', 'notes': 'NPC'})
    ctx.log(SO, 'DR-SOC-06', 'conflict', 'world/npcs.csv; world/locations.csv',
            ('ACT_NPC_CO_STEWARD added to world/npcs.csv in Lantern Hold; ' if steward else 'ACT_NPC_CO_STEWARD already present; ') +
            'no LOC rows added for the Signal Board or Company hall because design/world/locations.csv (frozen, wins on LOC_ IDs) has none in REG_HUB.')
    outside(SO, 'DR-SOC-07', 'the loops thread (design/loops/matchmaking.csv)')
    outside(SO, 'DR-SOC-08', 'the tech thread (design/tech/02-online.md)')
    t9 = '6 players. Bring a fireteam, use the Signal Board or the Raid Finder.'
    if change_string('STR_END_RAID_D', t9): ctx.log(SO, 'DR-SOC-09', 'applied', 'ui/strings.csv STR_END_RAID_D', 'applied: raid text now names the Signal Board and Raid Finder.')
    else: ctx.log(SO, 'DR-SOC-09', 'skipped', 'ui/strings.csv STR_END_RAID_D', 'already applied: text already matches.')
    outside(SO, 'DR-SOC-10', 'the production thread (production/customer_support.md)')

    # ================================================================ research
    R = 'research/data-requests.csv'
    tot, n, cl = merge_strings('research/strings_requests.csv')     # strings before popups
    rs = []
    for r in ctx.design_rows('research/popups_requests.csv'):
        rs.append({c: r[c] for c in ('popup_id', 'kind', 'screen', 'trigger', 'title_str', 'body_str', 'buttons')})
    merge_popups(R, 'RES-DR-001', 'design/research/popups_requests.csv',
                 rows=rs, note=' (IDs kept with their POP_ prefix; layer, timing and sound follow existing rows of each kind; LAB_BUILDFLAG dropped from a trigger that already says playtest builds only, OPT_TELEMETRY written as its label STR_OPT_TELEMETRY)')
    log_strings(R, 'RES-DR-002', 'design/research/strings_requests.csv', tot, n, cl)
    ctx.log(R, 'RES-DR-003', 'skipped', 'items, actors and world tables', 'note only: no change requested; telemetry keys on existing IDs.')

    # ================================================================ liveops
    L = 'liveops/data-requests.csv'
    tot, n, cl = merge_strings('liveops/strings_liveops.csv')
    log_strings(L, 'DR-LO-03', 'design/liveops/strings_liveops.csv', tot, n, cl)
    # DR-LO-02
    gone = 0
    h, rr = T['ui/strings.csv']
    keep = [r for r in rr if r[0] not in ('STR_SEASON_PREMIUM', 'STR_SHOP_FRAMES')]
    gone = len(rr) - len(keep); T['ui/strings.csv'] = [h, keep]
    for sid in ('STR_SEASON_PREMIUM', 'STR_SHOP_FRAMES'): S.pop(sid, None)
    xp = change_string('STR_SEASON_XP', '{VAR_xp} / 1,000 XP') if 'STR_SEASON_XP' in S else False
    if gone or xp:
        ctx.log(L, 'DR-LO-02', 'applied', 'ui/strings.csv', f'applied: {gone} strings removed (STR_SEASON_PREMIUM, STR_SHOP_FRAMES; nothing references them) and STR_SEASON_XP set to 1,000 XP per rank.')
    else:
        ctx.log(L, 'DR-LO-02', 'skipped', 'ui/strings.csv', 'already applied: premium track and photo frame strings are gone and STR_SEASON_XP reads 1,000 XP.')
    # DR-LO-01 cosmetics
    APPLIES = {'Dye': 'any armor dye channel', 'Strider skin': 'ACT_CRT_STRIDER (tamed mount)', 'Emote': 'player'}
    def resolve_text(c):
        for t in TOK.findall(c):
            if t not in defined:
                sid = f'STR_{t}_NAME'
                if sid in S: c = c.replace(t, S[sid][1])
        return c
    cat = [r for r in ctx.design_rows('liveops/store_catalog.csv') if r['in_data'].startswith('requested')]
    added = present = 0; capped = []; recolored = []
    for r in cat:
        hooks = r['asset_hooks'].split()
        pick = lambda p: next((x for x in hooks if x.startswith(p)), '')
        kind = r['kind']; app = APPLIES.get(kind, '')
        if kind == 'Armor ornament': app = r['name'][r['name'].find('(') + 1:-1] if '(' in r['name'] else ''
        if kind == 'Bundle': app = f"{r['item_id'].replace('_BUNDLE', '_SHOP')}_* (all 10 shop items of the season)"
        hx = r['color_hex']
        if kind == 'Dye' and hx.startswith('#'):
            nh, why = fix_dye(r['name'], hx)
            if why: recolored.append(r['item_id']); hx = nh
        price = r['price_usd']
        cap = BUNDLE_CAP if kind == 'Bundle' else PRICE_CAP
        if price and float(price) > cap: capped.append(r['item_id']); price = f'{cap:.2f}'
        d = {'item_id': r['item_id'], 'name': r['name'], 'kind': kind, 'color_hex': hx, 'applies_to': app, 'acquisition': resolve_text(r['source']),
             'price_ember': '', 'price_seals': '', 'price_usd': price, 'tradeable': 0, 'power': 0, 'icon': pick('UI_'), 'anim': pick('ANIM_'),
             'mesh': pick('MESH_'), 'sfx': pick('SFX_')}
        if add_cosmetic(d): added += 1
        else: present += 1
    msg = (f'{added} cosmetics added to items/cosmetics.csv and items_index.csv from design/liveops/store_catalog.csv (in_data requested)' + (f', {present} already present' if present else '') +
           f'; tradeable 0, power 0; icon/anim/mesh/sfx hooks in their own columns; {len(recolored)} dye colors moved to fit their names or clear reserved gameplay colors (README 28-29)')
    if capped:
        ctx.log(L, 'DR-LO-01', 'conflict', 'items/cosmetics.csv', msg + f'; {len(capped)} items asked more than their cap (single items $9.99, bundles $19.99) and were capped: {" ".join(capped)}.')
    else:
        ctx.log(L, 'DR-LO-01', 'applied', 'items/cosmetics.csv', 'applied: ' + msg + '.')
    # DR-LO-05: PVP maps table
    pm = ctx.design_rows('liveops/pvp_maps.csv')
    if True:   # derived wholly from design: rebuilt every run
        hdr = ['map_id', 'name', 'str_id', 'live', 'modes', 'ranked', 'competitive_pool', 'power_pads', 'layout_note', 'asset_hook']
        rows = []
        for r in pm:
            sid = f"STR_{r['map_id']}_NAME"
            rows.append([r['map_id'], r['name'], sid if sid in S else '', '0' if r['season'] == 'SSN_00' else '1', r['modes'], r['ranked'], r['competitive_pool'],
                         r['power_pads'], r['layout_note'], r['asset_hook']])
        T['world/pvp_maps.csv'] = [hdr, rows]; defined.update(r[0] for r in rows)
    ctx.log(L, 'DR-LO-05', 'conflict', 'world/pvp_maps.csv',
            f'{len(pm)} arena maps added as new table world/pvp_maps.csv (PVP_MAP_01..06 live=0, S1..S8 live=1; region and season columns left out because REG_X1/X2 and SSN_ IDs are not defined in data); '
            'STK_S1..S8 and ITM_SHB_S1W..S8A not added: loops DR-009/DR-011 own the strikes table and seasonal Shardborn and name them ITM_SHB_S<season>_W/_A, and no design file gives their stats.')
    lo4 = ctx.design_rows(L)[3]['requested_value']
    hs = [t for r in cat for t in r['asset_hooks'].split()] + [r['asset_hook'] for r in pm]
    ctx.log(L, 'DR-LO-04', 'applied', 'assets/asset_hooks.csv',
            f'applied: the {len(hs)} catalog and arena map hooks are referenced from items/cosmetics.csv (icon, anim, mesh, sfx) and world/pvp_maps.csv, so link.py registers them in asset_hooks.csv.')
    cur = {r['item_id'] for r in ctx.rows('items/currencies.csv')}
    lant = [k for k, (h, rr) in T.items() if any('price_lanterns' in c or 'ITM_CUR_LANTERNS' in c for c in h) or any('ITM_CUR_LANTERNS' in r[0] for r in rr)]  # bible: ok
    if 'ITM_CUR_LANTERNS' not in cur and not lant:  # bible: ok
        ctx.log(L, 'DR-LO-06', 'skipped', 'items/currencies.csv', 'already applied: no ITM_CUR_LANTERNS, price_lanterns or Lanterns text in data (validate.py flags "Lanterns"), and data/README decision 4 already says there is no premium currency.')  # bible: ok
    else:
        ctx.log(L, 'DR-LO-06', 'conflict', 'items/currencies.csv', f'Lantern leftovers still present in {lant}.')
    outside(L, 'DR-LO-07', 'the loops thread (design/loops/08-live-seasons.md)')
    outside(L, 'DR-LO-08', 'the production thread (design/production/liveops_calendar.csv, marketing_launch.md)')
    outside(L, 'DR-LO-09', 'the production thread (design/production/ratings_legal.md)')
    ctx.log(L, 'DR-LO-10', 'skipped', 'actors/', 'future note: applies when the expansions enter production; nothing to add now.')

    # ================================================================ asset hook requests (registry is generated from references after merge)
    def hook_log(src, rid, text, owner='the asset thread (shardfall-assets.xlsx)'):
        hs, got = hooks_note(text)
        ctx.log(src, rid, 'skipped', 'assets/asset_hooks.csv',
                f'outside data/: owned by {owner}; asset_hooks.csv is generated by link.py from hooks data rows reference, '
                f'and {len(got)} of the {len(hs)} explicitly named hooks are referenced and register automatically.')
    hook_log(A, 'ACC-DR-005', acc_hook_text)
    hook_log(FE, 'FE-DR-006', fe_hook_text)
    hook_log(P, 'DR-PLT-003', plt3)
    hook_log(P, 'DR-PLT-004', plt4, owner='the asset and audio threads (haptic clips, shardfall-assets.xlsx)')
    hook_log(SO, 'DR-SOC-05', soc_hook_text)

    # ================================================================ art (targets are the asset sheet and ui-visual-assets.csv)
    for r in ctx.design_rows('art/data-requests.csv'):
        owner = 'the asset thread (shardfall-assets.xlsx)' if 'xlsx' in r['owner_table'] else 'the art/UI asset thread (ui-visual-assets.csv)'
        outside('art/data-requests.csv', r['dr_id'], owner)
    for r in ctx.design_rows('licensing/data-requests.csv'):      # 0 rows today
        ctx.log('licensing/data-requests.csv', r['dr_id'], 'skipped', r['owner_table'], 'outside data/: owned by the licensing thread.')
