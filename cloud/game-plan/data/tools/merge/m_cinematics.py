"""Merge module for design/cinematics/data-requests.csv (cinematics thread).
Asset hooks: link.py rebuilds assets/asset_hooks.csv after the merge layer by scanning every cell of every table in T, and
T['assets/asset_hooks.csv'] is itself scanned, so hooks appended to it here are kept in the rebuilt registry.
"SFX_CIN_<scene>_*" expands to the sfx_hook values of that scene in design/cinematics/shots.csv.
Music cues (design/audio), dialogue lines (design/writing), the save field (design/tech) and the Theater screen are outside data/."""
import re

FILES = ['cinematics/data-requests.csv']
F = 'cinematics/data-requests.csv'
TOK = re.compile(r'(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+(?![a-z0-9])')
AP = ('MESH', 'VFX', 'SFX', 'ANIM', 'UI', 'ARENA')
HK = 'assets/asset_hooks.csv'


def apply(T, ctx):
    log = lambda rid, st, tgt, why: ctx.log(F, rid, st, tgt, why)
    req = ctx.design_rows(F)
    shots = ctx.design_rows('cinematics/shots.csv')
    # every asset hook the data already uses (what link's registry will find)
    have = {m for k, (h, rr) in T.items() if k != HK for r in rr for c in r for m in TOK.findall(c) if m.split('_')[0] in AP}
    have |= ctx.ids(HK)

    def hook(hid, note):
        if hid in have: return False
        ctx.append(HK, dict(hook=hid, kind=hid.split('_')[0], first_used_in='design/cinematics', first_row=note, uses=0))
        have.add(hid); return True

    for r in req:
        rid, kind, tgt, notes = r['id'], r['request'], r['target_table'], r['notes']
        if kind in ('new asset', 'new asset (if missing)'):
            if rid.endswith('_*'):
                cin = 'CIN_' + rid[len('SFX_CIN_'):-2]
                hooks = sorted({s['sfx_hook'] for s in shots if s['cin_id'] == cin and s['sfx_hook']})
                if not hooks: log(rid, 'skipped', HK, f'nothing to apply: shots.csv has no sfx_hook for {cin}.'); continue
                new = [h for h in hooks if hook(h, '')]
                if new: log(rid, 'applied', HK, f'added {len(new)} per-beat SFX hooks for {cin} from shots.csv ({new[0]}..{new[-1]})' + (f'; {len(hooks) - len(new)} already present.' if len(new) < len(hooks) else '.'))
                else: log(rid, 'skipped', HK, f'already applied: all {len(hooks)} SFX hooks for {cin} are in data.')
            else:
                if hook(rid, ''): log(rid, 'applied', HK, f'added asset hook {rid} ({notes.split(",")[0]}).')
                else: log(rid, 'skipped', HK, f'already applied: {rid} is already an asset hook in data.')
        elif kind == 'new string':
            m = re.search(r'"(.+?)"', notes)
            if m: text = m.group(1)
            elif notes.startswith('Setting: '): text = re.sub(r'\s*\(.*\)$', '', notes[len('Setting: '):]).strip()
            else: log(rid, 'skipped', 'ui/strings_data.csv', 'nothing to apply: the request gives no text.'); continue
            screen = 'Extras: Theater' if rid.startswith('STR_CIN_') else 'Options: Cinematics'
            if ctx.string(rid, text, screen, notes.split(':')[0]): log(rid, 'applied', 'ui/strings_data.csv', f'added "{text}".')
            else: log(rid, 'skipped', 'ui/strings_data.csv', f'already applied: {rid} exists.')
        elif kind == 'new cue':
            log(rid, 'skipped', tgt, 'outside data/: owned by design/audio (music_cues.csv).')
        elif kind == 'new popup':
            # prompt text from the request; runtime tokens written in the data convention ({BTN_confirm}, {VAR_n})
            text = re.search(r'"(.+?)"', notes).group(1).replace('{BTN_CONFIRM}', '{BTN_confirm}').replace('{n}', '{VAR_n}').replace('{m}', '{VAR_m}')
            trig = 'Skippable cutscene playing for 1 s' if 'HOLD' in rid else 'Skippable cutscene in co-op, after any player holds skip'
            layer = 'HUD bottom right' if 'bottom right' in notes else 'HUD bottom centre'
            sid = f'STR_{rid}_T'
            ctx.string(sid, text, 'Cinematics', 'prompt title')
            ok = ctx.append('ui/popups.csv', dict(popup_id=rid, kind='prompt', screen='Cinematics', layer=layer, trigger=trig, title_str=sid, body_str='',
                                                  buttons='', duration_s='Until scene ends', dismiss='Condition met', priority=4,
                                                  queue_rule='One at a time; highest priority wins', sfx_hook='SFX_UI_PROMPT'))
            if ok: log(rid, 'applied', 'ui/popups.csv', f'added prompt {rid} with {sid} "{text}".')
            else: log(rid, 'skipped', 'ui/popups.csv', f'already applied: popup {rid} exists.')
        elif kind == 'new lines':
            log(rid, 'skipped', tgt, 'outside data/: owned by design/writing (dialogue text and VO IDs).')
        elif kind == 'new screen':
            log(rid, 'skipped', tgt, 'outside data/: screen layouts are owned by the frontend and ui-mockups threads (data/ui holds strings and popups; the Theater titles are added as STR_CIN_*_TITLE).')
        elif kind == 'save field':
            log(rid, 'skipped', tgt, 'outside data/: owned by design/tech (save system).')
        else:
            log(rid, 'skipped', tgt, f'not recognised by m_cinematics: request kind "{kind}".')
