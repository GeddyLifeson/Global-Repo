"""Builds design/accessibility/*.csv from opts.txt, features.txt and gag.txt. Run from anywhere."""
import csv, math, os, re, collections
T = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(T)
UI = os.path.join(OUT, '..', '..', 'data', 'ui', 'strings.csv')
S = {r['str_id']: r for r in csv.DictReader(open(UI, encoding='utf-8'))}
TEXT2ID = {}
for k, r in S.items():
    if r['screen'] in ('Options', 'Accessibility suite'): TEXT2ID.setdefault(r['text_en'], k)
mc = lambda t: max(4, math.ceil(len(t) * 1.4))
slug = lambda t: re.sub(r'[^A-Z0-9]+', '_', t.upper()).strip('_')[:28]
def w(name, hdr, rows):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        c = csv.writer(f); c.writerow(hdr); c.writerows(rows)
    print(name, len(rows))
def lines(fn):
    return [l.rstrip('\n').split('|') for l in open(os.path.join(T, fn), encoding='utf-8') if l.strip() and not l.startswith('#')]

strreq = collections.OrderedDict()   # str_id -> [screen, text, action, current, note]
def need(sid, screen, text, note=''):
    if sid in strreq: return sid
    cur = S.get(sid)
    strreq[sid] = [screen, text, 'new', '', note] if cur is None else [screen, text, 'change', cur['text_en'], note]
    return sid
def valstr(v, screen):
    v = {'Minimal': 'Minimal (fades out of combat)'}.get(v, v)
    if v in TEXT2ID: return TEXT2ID[v]
    sid = 'STR_OPT_VAL_' + slug(v); TEXT2ID[v] = sid
    return need(sid, screen, v, 'option value')

rows, order = [], collections.Counter()
for p in [l for l in open(os.path.join(T, 'opts.txt'), encoding='utf-8')]:
    if not p.strip() or p.startswith('#'): continue
    sid, tab, sec, label, typ, dflt, vals, tip, apply, plat, mp, refs, src = p.rstrip('\n').split('|')
    screen = 'Accessibility suite' if tab == 'Accessibility' else 'Options'
    order[tab] += 1
    need(sid, screen, label)
    tsid = ''
    if tip != '-':
        tsid = need({'STR_ACC_COLORBLIND': 'STR_ACC_CB_D'}.get(sid, sid + '_D'), screen, tip, 'tooltip')
    need('STR_OPT_SEC_' + slug(sec), screen, sec, 'section header')
    mn = mx = st = un = ''; vids = ''
    if typ == 'slider':
        m = re.match(r'(-?[\d.]+)\.\.(-?[\d.]+)/([\d.]+)\s*(.*)', vals); mn, mx, st, un = m.groups()
    elif typ in ('dropdown', 'toggle', 'multi'):
        vids = ';'.join(valstr(v.strip(), screen) for v in vals.split(';'))
    scope = 'Device' if tab in ('Display', 'Graphics') or sid in ('STR_OPT_AUDIO_OUT', 'STR_OPT_CHAT_DEVICE', 'STR_OPT_MUTE_BG') else 'Profile (cloud)'
    ap = {'I': 'Instant', 'P': 'Preview, keep within 15 s or revert', 'R': 'After restart', '-': '-'}[apply]
    oid = 'OPT_' + sid.split('_', 2)[2]
    if any(r[0] == oid for r in rows): oid = 'OPT_ACC_' + sid.split('_', 2)[2]
    rows.append([oid, tab, sec, order[tab], sid, label, typ, dflt, vals, mn, mx, st, un, vids, tsid, tip, ap, scope, plat, mp, refs, src])
H = ['option_id','tab','section','order','label_str','label_en','type','default','values','min','max','step','unit','value_strs','tooltip_str','tooltip_en','apply','saved_to','platforms','multiplayer_rule','standards','source']
w('settings_menu.csv', H, rows)
ids = {r[0] for r in rows}

F = lines('features.txt')
w('accessibility_features.csv', ['feature_id','area','rule','standards','phase','source'], F)

G = lines('gag.txt')
w('gag_coverage.csv', ['level','category','guideline','status','how_shardfall_meets_it'], G)
st = collections.Counter(g[3].split(' ')[0] for g in G)

XAG = [('101','Text display'),('102','Contrast'),('103','Additional channels for visual and audio cues'),('104','Subtitles and captions'),('105','Audio accessibility'),('106','Screen narration'),('107','Input'),('108','Game difficulty options'),('109','Object clarity'),('110','Haptic feedback'),('111','Audio description'),('112','UI navigation'),('113','UI focus handling'),('114','UI context'),('115','Error messages and destructive actions'),('116','Time limits'),('117','Visual distractions and motion settings'),('118','Photosensitivity'),('119','Speech-to-text/text-to-speech chat'),('120','Communication experiences'),('121','Accessible feature documentation'),('122','Accessible customer support'),('123','Mental health best practices')]
NOTE = {'108': 'Partial by design: plan 3.4 has no difficulty menu. Assist Mode, Echoes, co-op and leveling cover it.'}
xr = []
for n, t in XAG:
    o = [r[0] for r in rows if 'XAG ' + n in r[20]]
    f = [x[0] for x in F if 'XAG ' + n in x[3]]
    xr.append([n, t, NOTE.get(n, 'Met' if (o or f) else 'GAP'), ' '.join(o), ' '.join(f)])
w('xag_coverage.csv', ['xag','title','status','option_ids','feature_ids'], xr)

PRE = {'Vision': 'Menu Narration=On; Menu Text Size=150%; UI Scale=125; High Contrast HUD=On; Enemy Outlines=Enemies and items; Interactable Glint=Strong; Navigation Ping=On; Audio Description=On; Subtitle Size=Large; Crosshair Size=150',
       'Hearing': 'Subtitles=On; Subtitle Size=Large; Speaker Direction=On; Sound Captions=On; Visual Sound Cues=On; Sound Cue Types=All; Damage Direction=On; Speech to Text=On',
       'Motor': 'Replace Holds with Taps=On; Auto-complete Button Mashing=On; Timed Prompts=Long (2x); Auto-Sprint=On; Strider Follows Roads=On; Vehicle Steering Assist=On; Assist Mode=On (all sub-options except Game Speed and Keep Ember on Death)',
       'Cognitive': 'Objective Reminders=After 5 min; Story Recap on Load=On; Control Hints=Always; Notification Time=2x; Highlight Key Terms=On; Ostra Chatter=Story only; Background Motion=Reduced; Tutorials=On'}
pr = []
for k, v in PRE.items():
    labels = {r[5]: r for r in rows}
    for kv in v.split('; '):
        a, b = kv.split('=', 1); r = labels[a]
        pr.append(['PRE_' + k.upper(), k, r[0], a, b])
    need('STR_ACC_PRESET_' + k.upper() + '_D', 'Accessibility suite', 'Turns on: ' + ', '.join(x.split('=')[0] for x in v.split('; ')) + '.', 'preset tooltip')
w('presets.csv', ['preset_id','preset','option_id','label_en','set_to'], pr)

FB = [
 ('FB1','Health and photosensitivity warning','STR_FB_WARN_T','Health Warning','STR_FB_WARN_B','A very small number of people may have a seizure when exposed to flashing lights or patterns. Stop playing and see a doctor if you feel dizzy, have blurred vision or twitching. Reduce Flashing is in Options > Accessibility.','Continue','Every boot until the player ticks Do not show again; always shown on first boot','XAG 118'),
 ('FB2','Language and narration','STR_FB_LANG_T','Language','STR_FB_LANG_B','Choose your text and voice language. Press {BTN_narration} at any time to turn menu narration on or off.','Text Language; Voice Language; Menu Narration','Narration auto-starts if the system screen reader is on','XAG 106; XAG 114'),
 ('FB3','Subtitles','STR_FB_SUBS_T','Subtitles','STR_FB_SUBS_B','Subtitles are on. Pick a size and background you can read comfortably.','Subtitles; Subtitle Size; Subtitle Background; Show Speaker Names','Live preview line from Ostra, text only, no audio yet','XAG 104; GAG Intermediate Hearing'),
 ('FB4','Text and interface size','STR_FB_SIZE_T','Text Size','STR_FB_SIZE_B','Make menus and the HUD bigger or smaller.','UI Scale; Menu Text Size','Preview of the HUD and an inventory card','XAG 101'),
 ('FB5','Brightness','STR_FB_BRIGHT_T','Brightness','STR_FB_BRIGHT_B','Adjust until the left symbol is barely visible.','Brightness; HDR Peak Brightness; HDR Paper White','HDR steps only when HDR is on','XAG 102'),
 ('FB6','Accessibility presets','STR_FB_ACC_T','Accessibility','STR_FB_ACC_B','Choose a preset to turn on a group of settings, or open every accessibility option.','Accessibility Presets; Assist Mode; Colorblind Mode; Reduce Motion','More Options opens the full Accessibility tab','XAG 114; XAG 121'),
 ('FB7','Controls','STR_FB_CTRL_T','Controls','STR_FB_CTRL_B','Pick a layout and how hold buttons work. You can remap every button later.','Controller Layout; Replace Holds with Taps; Invert Y (Camera)','Layout list comes from design/controls/','XAG 107'),
 ('FB8','Done','STR_FB_DONE_T','You are set','STR_FB_DONE_B','You can change all of this any time in Options. Accessibility settings also open from the pause menu.','Begin','Leads into the opening cinematic','XAG 121'),
]
for f in FB:
    need(f[2], 'First boot', f[3]); need(f[4], 'First boot', f[5])
w('first_boot.csv', ['step','purpose','title_str','title_en','body_str','body_en','options_shown','notes','standards'], [list(f) for f in FB])

POP = [
 ('CNF_ACC_RESET','modal','Options','Modal dialog over current screen','Select Reset Accessibility Settings','STR_CNF_ACC_RESET_T','Reset accessibility settings?','STR_CNF_ACC_RESET_B','Every option on the Accessibility tab goes back to default.','Cancel (focus); Reset','','Button','5','Replaces current modal','SFX_UI_CONFIRM'),
 ('CNF_ACC_PRESET','modal','Options','Modal dialog over current screen','Pick a preset when it would change options you already set','STR_CNF_ACC_PRESET_T','Apply {VAR_preset} preset?','STR_CNF_ACC_PRESET_B','This changes {VAR_count} settings you set yourself.','Cancel (focus); Apply','','Button','5','Replaces current modal','SFX_UI_CONFIRM'),
 ('CNF_OPT_SHADER','modal','Options','Modal dialog over current screen','Select Rebuild Shader Cache','STR_CNF_OPT_SHADER_T','Rebuild shaders?','STR_CNF_OPT_SHADER_B','Shaders rebuild next time you start the game. This can take a few minutes.','Cancel (focus); Rebuild','','Button','4','Replaces current modal','SFX_UI_CONFIRM'),
 ('NTF_ACC_SPEED_LOCK','toast','HUD','HUD notification feed, top right','A player joins while Game Speed is under 100%','STR_NTF_ACC_SPEED_LOCK_T','Game Speed set to 100% while others are in your world.','','','','4.0','Auto','4','Queue max 4 visible','SFX_UI_TOAST'),
 ('NTF_ACC_PVP_ASSIST','toast','HUD','HUD notification feed, top right','Enter PvP Arena or an invasion with Assist Mode on','STR_NTF_ACC_PVP_ASSIST_T','Aim help and longer windows are off in PvP. Visual aids stay on.','','','','5.0','Auto','4','Queue max 4 visible','SFX_UI_TOAST'),
 ('NTF_ACC_NARR','toast','Various','Notification feed','Menu narration toggled with its shortcut','STR_NTF_ACC_NARR_ON_T','Menu narration on.','STR_NTF_ACC_NARR_OFF_T','Menu narration off.','','2.0','Auto','6','Shows immediately; narrated','SFX_UI_TOAST'),
 ('NTF_OPT_SAVED','toast','HUD','HUD notification feed, top right','Save Now completes','STR_NTF_OPT_SAVED_T','Game saved.','','','','2.0','Auto','2','Queue max 4 visible','SFX_UI_TOAST'),
 ('INL_OPT_LOCKED_MP','inline','Options','Inline on current screen','Open a solo-only option while others are in your world','STR_INL_OPT_LOCKED_MP_T','Only available when you play alone.','','','','3.0','Auto','3','Replaces previous inline','SFX_UI_ERROR'),
]
pops = []
for p in POP:
    need(p[5], p[2], p[6], 'popup')
    if p[7]: need(p[7], p[2], p[8], 'popup')
    pops.append([p[0], p[1], p[2], p[3], p[4], p[5], p[7], p[9], p[10], p[11], p[12], p[13], p[14]])
w('popups_requests.csv', ['popup_id','kind','screen','layer','trigger','title_str','body_str','buttons','duration_s','dismiss','priority','queue_rule','sfx_hook'], pops)

need('STR_OPT_DYN_MID', 'Options', 'Standard', 'audio mix_standards names the middle mode Standard')
w('strings_requests.csv', ['str_id','screen','text_en','max_chars','action','current_text','notes'],
  [[k, v[0], v[1], mc(v[1]), v[2], v[3], v[4]] for k, v in strreq.items()])
unused = [k for k, r in S.items() if r['screen'] in ('Options', 'Accessibility suite') and k not in strreq and k not in {x for r in rows for x in [r[4], r[14]] + r[13].split(';')} and not k.startswith('STR_OPT_TAB_') and k != 'STR_OPT_TITLE']
print('existing Options strings not used:', unused)
print('strings new', sum(v[2] == 'new' for v in strreq.values()), 'changed', sum(v[2] == 'change' for v in strreq.values()), 'GAG', dict(st), 'XAG gaps', [x[0] for x in xr if x[2] == 'GAP'])
