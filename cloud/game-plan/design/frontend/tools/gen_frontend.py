"""Shardfall front end: boot flow, main menu, saves, photo mode, credits.
Writes every CSV in design/frontend/. Run: python3 tools/gen_frontend.py (from design/frontend/).
Values marked DC are Shardfall design choices where the plan is silent."""
import csv, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(OUT, "..", ".."))
UI_STR = os.path.join(ROOT, "data", "ui", "strings.csv")
UI_POP = os.path.join(ROOT, "data", "ui", "popups.csv")

def w(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)
    return len(rows)

existing = {r["str_id"]: r for r in csv.DictReader(open(UI_STR, encoding="utf-8"))}
existing_pop = {r["popup_id"] for r in csv.DictReader(open(UI_POP, encoding="utf-8"))}

# ---------------------------------------------------------------- new strings
S = []  # (id, screen, text, notes)
def s(i, scr, t, n=""): S.append((i, scr, t, n))

# Boot
B = "Boot"
s("STR_FE_EPI_T", B, "Photosensitivity Warning")
s("STR_FE_EPI_B", B, "A small number of people may have seizures when exposed to flashing lights or patterns, even with no history of epilepsy. If you feel dizzy, have altered vision, twitching, or loss of awareness while playing, stop at once and see a doctor. You can reduce flashing effects in Options > Accessibility.", "Legal; text reviewed by counsel")
s("STR_FE_EPI_CONTINUE", B, "Hold {BTN_confirm} to Continue", "Hold 1.0 s; enabled after 2.0 s")
s("STR_FE_SHADER_T", B, "Preparing Shaders")
s("STR_FE_SHADER_B", B, "This happens once after install or a driver update. You can start playing while it finishes, but you may see stutter.")
s("STR_FE_SHADER_PCT", B, "{VAR_pct}%")
s("STR_FE_SHADER_SKIP", B, "Play Now")
s("STR_FE_LANG_T", B, "Language")
s("STR_FE_LANG_TEXT", B, "Text Language")
s("STR_FE_LANG_VOICE", B, "Voice Language")
s("STR_FE_LANG_VOICE_NOTE", B, "Voice is recorded in English, French, German, Spanish and Japanese.")
s("STR_FE_LANG_CHANGE_NOTE", B, "You can change both later in Options > Interface.")
for code, name in [("EN","English"),("FR","Français"),("DE","Deutsch"),("ES","Español"),("JA","日本語"),("PTBR","Português (Brasil)"),("IT","Italiano"),("PL","Polski"),("RU","Русский"),("KO","한국어"),("ZHS","简体中文"),("ZHT","繁體中文")]:
    s(f"STR_FE_LANG_{code}", B, name, "Endonym; never translated")
s("STR_FE_EULA_T", B, "End User License Agreement")
s("STR_FE_EULA_SCROLL", B, "Scroll to the end to continue.")
s("STR_FE_EULA_ACCEPT", B, "Accept")
s("STR_FE_EULA_DECLINE", B, "Decline")
s("STR_FE_EULA_DECLINE_B", B, "You must accept the license agreement to play Shardfall.")
s("STR_FE_EULA_VERSION", B, "Version {VAR_n}, updated {VAR_date}")
s("STR_FE_PRIV_T", B, "Privacy")
s("STR_FE_PRIV_B", B, "Shardfall collects some data to run online play and to fix problems. Choose what you share. You can change this at any time in Options > Account.")
s("STR_FE_PRIV_CRASH", B, "Send Crash Reports")
s("STR_FE_PRIV_CRASH_D", B, "Sends a report when the game crashes. No personal files are included.")
s("STR_FE_PRIV_TELEM", B, "Share Gameplay Data")
s("STR_FE_PRIV_TELEM_D", B, "Sends anonymous data about how the game is played, such as where players fall, so we can tune it.")
s("STR_FE_PRIV_READ", B, "Read Privacy Policy")
s("STR_FE_PRIV_CONTINUE", B, "Continue")
s("STR_FE_A11Y_T", B, "Before You Begin")
s("STR_FE_A11Y_B", B, "Set up the options you need now. Everything here is also in Options > Accessibility.")
s("STR_FE_A11Y_OPEN", B, "Open Accessibility Options")
s("STR_FE_A11Y_NARR", B, "Menu Narration")
s("STR_FE_A11Y_SUBS", B, "Subtitles")
s("STR_FE_A11Y_SUBSIZE", B, "Subtitle Size")
s("STR_FE_A11Y_CB", B, "Colorblind Mode")
s("STR_FE_A11Y_CONTINUE", B, "Continue")
s("STR_FE_BRI_T", B, "Brightness")
s("STR_FE_BRI_SDR_B", B, "Adjust until the left symbol is barely visible, the middle symbol is faint and the right symbol is clear.")
s("STR_FE_BRI_GAMMA", B, "Brightness")
s("STR_FE_BRI_HDR_T", B, "HDR Calibration")
s("STR_FE_BRI_HDR_MAX", B, "Peak Brightness")
s("STR_FE_BRI_HDR_MAX_B", B, "Lower until the symbol disappears into the white.")
s("STR_FE_BRI_HDR_PAPER", B, "Menu Brightness")
s("STR_FE_BRI_HDR_PAPER_B", B, "Set how bright menus and text look.")
s("STR_FE_BRI_HDR_BLACK", B, "Black Level")
s("STR_FE_BRI_HDR_BLACK_B", B, "Raise until the symbol is just visible.")
s("STR_FE_BRI_SYSTEM", B, "Use System Calibration")
s("STR_FE_BRI_RESET", B, "Reset to Default")
s("STR_FE_BRI_CONFIRM", B, "Confirm")
s("STR_FE_AUDIO_T", B, "Audio Output")
s("STR_FE_AUDIO_TV", B, "TV Speakers")
s("STR_FE_AUDIO_HOME", B, "Home Theater")
s("STR_FE_AUDIO_HEAD", B, "Headphones")
s("STR_FE_AUDIO_NIGHT", B, "Night Mode")
s("STR_FE_AUDIO_NIGHT_D", B, "Reduces loud peaks so you can play quietly.")
s("STR_FE_ONLINE_CONNECT", B, "Connecting to Shardfall services...")
s("STR_FE_ONLINE_FAIL_T", B, "Can't Connect")
s("STR_FE_ONLINE_FAIL_B", B, "Shardfall services are unavailable. You can play solo and local co-op offline. Seals, raids, Arena and the Wardrobe Shop need a connection.")
s("STR_FE_ONLINE_RETRY", B, "Retry")
s("STR_FE_ONLINE_OFFLINE", B, "Play Offline")
s("STR_FE_ONLINE_MAINT", B, "Shardfall services are down for maintenance until {VAR_time}.")
s("STR_FE_LINK_T", B, "Cross-Progression")
s("STR_FE_LINK_B", B, "Link this {VAR_platform} account to carry your characters, Seals and cosmetics across PC, PlayStation 5 and Xbox Series.")
s("STR_FE_LINK_YES", B, "Link Account")
s("STR_FE_LINK_LATER", B, "Not Now")
s("STR_FE_LINK_CODE", B, "Go to {VAR_url} and enter code {VAR_code}.")
s("STR_FE_LINK_DONE", B, "Account linked.")
s("STR_FE_UPDATE_T", B, "Update Required")
s("STR_FE_UPDATE_B", B, "A newer version of Shardfall is available. Update to play online.")

# Title and main menu
T = "Title and main menu"
s("STR_FE_TITLE_PRESS_PC", T, "Press Any Key", "PC keyboard-mouse only; controller uses STR_TITLE_PRESS")
s("STR_FE_TITLE_PROFILE", T, "Signed in as {VAR_player}", "Console")
s("STR_FE_TITLE_SWITCH_USER", T, "Change Profile", "Xbox requirement")
s("STR_FE_MAIN_EXTRAS", T, "Extras")
s("STR_FE_MAIN_NEWS", T, "What's New")
s("STR_FE_MAIN_NG_PLUS", T, "Begin New Game+")
s("STR_FE_MAIN_CHAR", T, "Characters")
s("STR_FE_MAIN_CONTINUE_NONE", T, "No saves yet")
s("STR_FE_MAIN_HINT_SELECT", T, "{BTN_confirm} Select")
s("STR_FE_MAIN_HINT_BACK", T, "{BTN_back} Back")
s("STR_FE_NEWS_T", T, "What's New")
s("STR_FE_NEWS_DISMISS", T, "{BTN_back} Close")
s("STR_FE_NEWS_HIDE_TODAY", T, "Don't show again today")
s("STR_FE_NEWS_OFFLINE", T, "News is unavailable offline.")
s("STR_FE_EXTRAS_T", T, "Extras")
s("STR_FE_EXTRAS_PHOTOS", T, "Photos")
s("STR_FE_EXTRAS_ENDINGS", T, "Endings")
s("STR_FE_EXTRAS_ENDING_LOCKED", T, "Not yet seen")
s("STR_FE_EXTRAS_CINEMA", T, "Cinematics")
s("STR_FE_EXTRAS_CINEMA_D", T, "Rewatch cinematics you have seen on any character.")
s("STR_FE_EXTRAS_PATCH", T, "Patch Notes")
s("STR_FE_EXTRAS_LEGAL", T, "Legal")
s("STR_FE_LEGAL_EULA", T, "License Agreement")
s("STR_FE_LEGAL_PRIVACY", T, "Privacy Policy")
s("STR_FE_LEGAL_TOS", T, "Terms of Service")
s("STR_FE_LEGAL_THIRD", T, "Third-Party Licenses")
s("STR_FE_PHOTOS_EMPTY", T, "No photos yet. Open Photo Mode from the Ledger.")
s("STR_FE_PHOTOS_CONSOLE", T, "Your photos are in the {VAR_platform} capture gallery.")
s("STR_FE_PHOTOS_DELETE", T, "Delete Photo")
s("STR_FE_PHOTOS_FOLDER", T, "Open Folder")
s("STR_FE_PHOTOS_COUNT", T, "{VAR_n} photos")

# Characters and saves
C = "Characters and saves"
s("STR_FE_CHAR_T", C, "Characters")
s("STR_FE_CHAR_COUNT", C, "{VAR_n} / 10")
s("STR_FE_CHAR_NEW", C, "New Character")
s("STR_FE_CHAR_FULL", C, "All 10 character slots are in use. Delete a character to make a new one.")
s("STR_FE_CHAR_CARD", C, "{VAR_char_name}  ·  Level {VAR_level}  ·  {VAR_origin}")
s("STR_FE_CHAR_CARD_SUB", C, "{VAR_location}  ·  {VAR_playtime}  ·  {VAR_date}")
s("STR_FE_CHAR_CYCLE", C, "NG+{VAR_n}")
s("STR_FE_CHAR_ACT", C, "Act {VAR_n}")
s("STR_FE_CHAR_ENDINGS", C, "Endings seen: {VAR_n} / 3")
s("STR_FE_CHAR_PLAY", C, "Play")
s("STR_FE_CHAR_LOAD", C, "Load a Save")
s("STR_FE_CHAR_DELETE", C, "Delete Character")
s("STR_FE_CHAR_DELETE_HOLD", C, "Hold {BTN_confirm} to Delete")
s("STR_FE_SAVE_T", C, "Saves: {VAR_char_name}")
s("STR_FE_SAVE_SAVE_T", C, "Save Game")
s("STR_FE_SAVE_NEW", C, "New Save")
s("STR_FE_SAVE_CARD", C, "{VAR_location}  ·  Level {VAR_level}  ·  {VAR_playtime}")
s("STR_FE_SAVE_STAMP", C, "{VAR_date} {VAR_time}")
s("STR_FE_SAVE_BACKUP", C, "Backup {VAR_n}")
s("STR_FE_SAVE_BEFORE_END", C, "Before the End")
s("STR_FE_SAVE_BEFORE_END_D", C, "Kept so you can return and choose another ending.")
s("STR_FE_SAVE_CYCLE", C, "Start of NG+{VAR_n}")
s("STR_FE_SAVE_EMBER", C, "Ember {VAR_ember}")
s("STR_FE_SAVE_GHOST", C, "Shard-ghost holds {VAR_ember} Ember")
s("STR_FE_SAVE_MODS", C, "Modded")
s("STR_FE_SAVE_CLOUD_OK", C, "Synced")
s("STR_FE_SAVE_CLOUD_LOCAL", C, "On this device only")
s("STR_FE_SAVE_CLOUD_UP", C, "Uploading...")
s("STR_FE_SAVE_CLOUD_CONFLICT", C, "Cloud conflict")
s("STR_FE_SAVE_FULL", C, "Manual saves are full (10). Overwrite one to save.")
s("STR_FE_SAVE_DELETE", C, "Delete Save")
s("STR_FE_SAVE_LOCKED", C, "Protected saves can't be deleted on their own.")
s("STR_FE_SAVE_RECOVERED", C, "Loaded {VAR_save} from {VAR_time}. The newer save was damaged.")
s("STR_FE_QS_DONE", C, "Quicksaved", "PC toast")
s("STR_FE_QL_LOADING", C, "Quickloading...")
s("STR_FE_CANT_SAVE_BOSS", C, "You can't save during a boss fight.")
s("STR_FE_CANT_SAVE_GUEST", C, "Only the host can save. Your progress saves when you leave.")
s("STR_FE_CANT_SAVE_ONLINE", C, "Progress in this activity saves when it ends.")
s("STR_FE_CANT_SAVE_CINE", C, "You can't save during a cinematic.")
s("STR_FE_CLOUD_T", C, "Choose a Save")
s("STR_FE_CLOUD_B", C, "This character changed on this device and in the cloud. Which one do you want to keep? The other is kept as a backup.")
s("STR_FE_CLOUD_LOCAL", C, "This Device: {VAR_playtime}, {VAR_date}")
s("STR_FE_CLOUD_REMOTE", C, "Cloud: {VAR_playtime}, {VAR_date}")
s("STR_FE_NG_T", C, "Begin New Game+")
s("STR_FE_NG_B", C, "Start the story again at NG+{VAR_n}. You keep your level, skills, perks, gear and Ember. Quests, companions and the world reset. Enemies are much stronger.")
s("STR_FE_NG_KEEP", C, "Your current save is kept as Start of NG+{VAR_n}.")
s("STR_FE_NG_CONFIRM", C, "Begin")
s("STR_FE_NG_LATER", C, "Not Now")
s("STR_FE_POST_T", C, "The Story Is Told")
s("STR_FE_POST_B", C, "Return to Veyl to finish what you started, or begin the next cycle.")
s("STR_FE_POST_RETURN", C, "Return to Veyl")
s("STR_FE_POST_NG", C, "Begin NG+{VAR_n}")
s("STR_FE_POST_TITLE", C, "Return to Title")

# Photo mode (adds to existing STR_PHOTO_*)
P = "Photo mode"
for k, t in [("TAB_CAMERA","Camera"),("TAB_LENS","Lens"),("TAB_FILTER","Filter"),("TAB_FRAME","Frame"),("TAB_SUBJECT","Subject"),("TAB_LIGHT","Lights"),("TAB_STAMP","Stamp"),
             ("MOVE_SPEED","Camera Speed"),("COLLISION","Camera Collision"),("AUTOFOCUS","Auto Focus"),("FOCUS_TARGET","Focus on Character"),("VIGNETTE","Vignette"),("GRAIN","Film Grain"),
             ("CHROMA","Chromatic Aberration"),("BLOOM","Bloom"),("SHARPEN","Sharpen"),("SATURATION","Saturation"),("CONTRAST","Contrast"),("TINT","Tint"),("SUN","Sun Angle"),("LOOK_CAM","Look at Camera"),
             ("HIDE_COMPANION","Hide Companion"),("HIDE_ENEMIES","Hide Enemies"),("HIDE_WEAPON","Hide Weapon"),("HIDE_HELM","Hide Helmet"),("FREEZE_FX","Freeze Effects"),
             ("LIGHT_N","Light {VAR_n}"),("LIGHT_ON","Light On"),("LIGHT_COLOR","Color Temperature"),("LIGHT_INT","Intensity"),("LIGHT_RAD","Radius"),("LIGHT_PLACE","Place at Camera"),
             ("STAMP_ON","Show Logo"),("STAMP_POS","Logo Position"),("GRID","Grid"),("HIDE_UI","Hide Menu"),("RESET","Reset All"),("RESET_TAB","Reset Tab"),("EXIT","Exit Photo Mode"),
             ("CANT_COMBAT","Photo Mode is unavailable in combat."),("CANT_HERE","Photo Mode is unavailable here."),("ONLINE_NOTE","The world keeps moving in co-op."),
             ("SAVED_PATH","Saved to {VAR_path}"),("SAVED_CONSOLE","Saved to captures."),("RES","Resolution"),("RES_1X","Screen"),("RES_2X","2x (PC)"),("FMT","Format")]:
    s(f"STR_PHOTO_{k}", P, t)
FILTERS = ["None","Ledger Sepia","Hull Steel","Choir Glass","Ashlight","Saltlight","Briar","Rime","Hollowed","Lens","Candle","Noir","Signal"]
for i, n in enumerate(FILTERS): s(f"STR_PHOTO_FILTER_{i:02d}", P, n, "Filter name")
FRAMES = ["None","Ledger Margin","Wax Seal","Ship Console","Cinema 2.39:1","Classic 4:3","Square 1:1","Portrait 9:16","Ostra's Lens","Lantern Church Icon"]
for i, n in enumerate(FRAMES): s(f"STR_PHOTO_FRAME_{i:02d}", P, n, "Frame name")
POSES = ["Idle","Battle Ready","Guard Up","Aim","Salute (Hull Knight)","Kneel","Prayer (Lantern Church)","Sit","Lean","Arms Crossed","Point Ahead","Look Back","Victory","Laugh","Bow","Wave","Hand to Shard","Sheathe","Rest on Weapon","Scout","Wounded","Cold","Weave Gather","Weave Release","Reload","Shoulder Rifle","Strider Pet","Over the Edge","Hero Stand","Lying Down"]
for i, n in enumerate(POSES, 1): s(f"STR_PHOTO_POSE_{i:02d}", P, n, "Pose name")
EXPR = ["Neutral","Smile","Grin","Frown","Angry","Shout","Sad","Afraid","Surprised","Determined","Eyes Closed","Wince"]
for i, n in enumerate(EXPR, 1): s(f"STR_PHOTO_EXPR_{i:02d}", P, n, "Expression name")

# Credits
K = "Credits"
s("STR_FE_CRED_SKIP", K, "Hold {BTN_back} to Skip")
s("STR_FE_CRED_FAST", K, "Hold {BTN_confirm} to Speed Up")
s("STR_FE_CRED_THANKS", K, "Thank you for playing.")
s("STR_FE_CRED_MEMORY", K, "In Memory Of")
s("STR_FE_CRED_PLAYTESTERS", K, "And the {VAR_n} playtesters who fell so others wouldn't have to.")
s("STR_FE_CRED_LEGAL", K, "Shardfall © {VAR_year} Shardfall Team. All rights reserved. All trademarks are the property of their respective owners.")
s("STR_FE_CRED_UE", K, "Unreal® Engine, Copyright 1998 – {VAR_year}, Epic Games, Inc. All rights reserved.")
s("STR_FE_CRED_WWISE", K, "Wwise © {VAR_year} Audiokinetic Inc. All rights reserved.")
s("STR_FE_CRED_EOS", K, "Uses Epic Online Services and Easy Anti-Cheat.")
s("STR_FE_CRED_FONTS", K, "Fonts used under license. See Extras > Legal > Third-Party Licenses.")
s("STR_FE_CRED_AI", K, "Some development tools used machine learning. Every line of writing, voice and art that ships was made or approved by the people credited here.")
CRED_SECTIONS = [
 ("01","Directors"),("02","Design"),("03","Region Teams"),("04","Engineering"),("05","Online and Backend"),("06","Art"),("07","Animation"),
 ("08","Bosses"),("09","Cinematics"),("10","Audio and Music"),("11","Writing and Narrative"),("12","User Experience and Accessibility"),
 ("13","Production"),("14","Quality Assurance"),("15","Localization"),("16","Voice Cast"),("17","Performance Capture"),("18","Outsourcing Partners"),
 ("19","Live Operations and Analytics"),("20","Marketing and Community"),("26","Consumer Products and Licensing"),("21","Studio Services"),("22","Playtesters"),("23","Special Thanks"),("24","Third-Party Software"),("25","Legal")]
for code, name in CRED_SECTIONS: s(f"STR_FE_CRED_SEC_{code}", K, name, "Credits section heading")
s("STR_FE_CRED_POST_A", K, "Ostra: The ship remembers your name now. So do I.", "Post-credit line, Restore ending (MQ_END_R)")
s("STR_FE_CRED_POST_B", K, "Ostra: The Weave is quiet. I can hear it breathing.", "Post-credit line, Bind ending (MQ_END_B)")
s("STR_FE_CRED_POST_C", K, "Ostra: Captain. Orders?", "Post-credit line, Take ending (MQ_END_T)")

# validate ids unique and not clashing with existing
ids = [x[0] for x in S]
dup = {i for i in ids if ids.count(i) > 1}
clash = [i for i in ids if i in existing]
assert not dup, dup
assert not clash, clash
new_ids = set(ids)
def has(sid): return sid in new_ids or sid in existing

def maxc(t): return math.ceil(len(t) * 1.4)
TOK = re.compile(r"\{([A-Z]+_[A-Za-z_]+)\}")
w("strings_frontend.csv", ["str_id","screen","text_en","max_chars","tokens","notes"],
  [(i, scr, t, maxc(t), " ".join(TOK.findall(t)), n) for i, scr, t, n in S])

# ---------------------------------------------------------------- screens
SCREENS = [
# id, name, group, layer, background, music, input_context, pauses_game, notes
("FE_BOOT_EPI","Photosensitivity warning","Boot","Full screen","Black, Ledger frame","None","Boot","n/a","Every boot. Required in several regions (DC: shown everywhere)."),
("FE_BOOT_LOGOS","Logo cards","Boot","Full screen","Black; logos drawn in-engine (no video, plan 5.7 rule)","Stinger SFX only","Boot","n/a","Publisher, studio, Unreal Engine + Wwise card. All skippable after first boot."),
("FE_BOOT_SHADER","Shader preparation","Boot","Full screen","Slow orbit of the Meridian wreck at low detail","MUS_MENU_LOADING","Boot","n/a","PC and Steam Deck. First launch, new driver or patch that changes shaders."),
("FE_BOOT_LANG","Language","Boot (first run)","Full screen","Ledger page","MUS_MENU_LOADING","Boot","n/a","First run only. Preselects system language; voice defaults to text language when recorded, else English."),
("FE_BOOT_EULA","License agreement","Boot (first run)","Full screen","Ledger page, scroll box","MUS_MENU_LOADING","Boot","n/a","First run and whenever the EULA version rises. Accept enabled once scrolled to end."),
("FE_BOOT_PRIV","Privacy and data","Boot (first run)","Full screen","Ledger page","MUS_MENU_LOADING","Boot","n/a","Two toggles, both default Off (DC, GDPR opt-in). Reshown when the policy version rises."),
("FE_BOOT_A11Y","Quick accessibility","Boot (first run)","Full screen","Ledger page","MUS_MENU_LOADING","Boot","n/a","Four quick toggles; full settings owned by design/accessibility/. Narration auto-on if the platform screen reader is on."),
("FE_BOOT_BRI","Brightness (SDR)","Boot (first run)","Full screen","Three Shard glyphs on a dark Hollowdeep plate","MUS_MENU_LOADING","Boot","n/a","Shown when output is SDR."),
("FE_BOOT_HDR","HDR calibration","Boot (first run)","Full screen","Three-step calibration plates","MUS_MENU_LOADING","Boot","n/a","Shown when output is HDR. Console offers system values first."),
("FE_BOOT_AUDIO","Audio output","Boot (first run)","Full screen","Ledger page with speaker diagram","MUS_MENU_LOADING","Boot","n/a","Sets mix preset (design/audio/mix_standards.csv)."),
("FE_TITLE","Title (press start)","Title","Full screen","Live Meridian wreck at dusk; changes to the last ending seen","MUS_MENU_TITLE","Menu","n/a","Logo fades in over 2.0 s. Idle 90 s starts attract mode."),
("FE_ATTRACT","Attract mode","Title","Full screen","In-engine flythrough of the six regions, 120 s loop","MUS_THEME_MAIN","Menu","n/a","Any input returns to FE_TITLE. No gameplay footage of unreleased content."),
("FE_CONNECT","Online connect","Title","Overlay","Title backdrop dimmed 40%","MUS_MENU_TITLE","Menu","n/a","Timeout 15 s then FE_ONLINE_FAIL. Skipped when Offline mode was chosen this session."),
("FE_ONLINE_FAIL","Can't connect","Title","Modal","Title backdrop dimmed","MUS_MENU_TITLE","Menu","n/a","Retry or Play Offline."),
("FE_LINK","Cross-progression link","Title","Modal","Title backdrop dimmed","MUS_MENU_TITLE","Menu","n/a","Once per platform account until linked or declined 3 times."),
("FE_NEWS","What's New","Title","Modal panel, right side","Main menu stays visible","MUS_MENU_TITLE","Menu","n/a","Max once per day, max 3 cards. Never shows store prices (DC)."),
("FE_MAIN","Main menu","Title","Full screen, left column","Title backdrop, camera eases 8 deg right","MUS_MENU_TITLE","Menu","n/a","Ledger style. Vertical list, focus starts on Continue (or New Game with no saves)."),
("FE_CHARS","Characters","Saves","Full screen","Title backdrop dimmed 60%","MUS_MENU_TITLE","Menu","n/a","10 slots, newest first. Portrait is a capture taken at the last save."),
("FE_SAVES","Save list (load)","Saves","Full screen","Title backdrop dimmed 60%, or game paused","MUS_MENU_TITLE","Menu","Yes in single player","Grouped: Autosave, Backups, Quicksave, Manual, Protected."),
("FE_SAVE_GAME","Save list (save)","Saves","Full screen over Ledger","Game paused","Current cue low-passed (MUS_MENU_PAUSE)","Menu","Yes in single player","From Ledger > Save Game. New Save at top."),
("FE_CLOUD","Cloud conflict","Saves","Modal","Behind: FE_CHARS","Current","Menu","n/a","Side-by-side cards; loser kept as Backup 3."),
("FE_NG","Begin New Game+","Saves","Modal","Behind: FE_CHARS or FE_POST","Current","Menu","n/a","Available on characters with at least one ending seen."),
("FE_POST","After the ending","Saves","Full screen","Ending's final shot, held","Credits tail","Menu","n/a","Shown once per ending per character, right after credits."),
("FE_EXTRAS","Extras","Extras","Full screen","Title backdrop dimmed 60%","MUS_MENU_TITLE","Menu","n/a",""),
("FE_PHOTOS","Photos","Extras","Full screen grid","Dark Ledger","MUS_MENU_TITLE","Menu","n/a","PC: in-game gallery of the photo folder. Console: message pointing to system captures."),
("FE_ENDINGS","Endings","Extras","Full screen","Three tall cards","MUS_MENU_TITLE","Menu","n/a","Account-wide. Seen endings show the ending art and replay its cinematic."),
("FE_CINEMA","Cinematics","Extras","Full screen list","Dark Ledger","MUS_MENU_TITLE","Menu","n/a","Replays seen in-engine cinematics with a stand-in character in the default Origin armor (DC)."),
("FE_PATCH","Patch notes","Extras","Full screen scroll","Dark Ledger","MUS_MENU_TITLE","Menu","n/a","Bundled notes for this build plus online notes when connected."),
("FE_LEGAL","Legal","Extras","Full screen list","Dark Ledger","MUS_MENU_TITLE","Menu","n/a","EULA, privacy, terms, third-party licenses (read-only scroll views)."),
("FE_CREDITS","Credits roll","Extras / ending","Full screen","Left 60% scroll, right 40% photo strip","MUS_MENU_CREDITS","Credits","n/a","See credits_structure.csv."),
("FE_PHOTO","Photo mode","In game","Full screen overlay, panel left 30%","Frozen world (solo)","Current cue continues, ducked -6 dB","PhotoMode","Yes in solo; no in co-op","See photo_mode.csv."),
("FE_QUIT","Quit confirm","Title","Modal","Main menu","MUS_MENU_TITLE","Menu","n/a","PC and Steam Deck only."),
]
w("screens.csv", ["screen_id","name","group","layer","background","music","input_context","pauses_game","notes"], SCREENS)
screen_ids = {r[0] for r in SCREENS}

# ---------------------------------------------------------------- boot sequence
BOOT = [
# step, screen, shown_when, min_s, max_s, skippable, platform, notes
(1,"Platform splash","Every boot","0","platform","No","All","OS/launcher owns this; not built by us"),
(2,"FE_BOOT_EPI","Every boot","2.0","until input","Hold 1.0 s after 2.0 s","All","DC: every boot, so a new player on a shared console always sees it"),
(3,"FE_BOOT_LOGOS publisher","Every boot","1.0","3.0","After first boot: any input","All","Fade 0.5 in / 2.0 hold / 0.5 out"),
(4,"FE_BOOT_LOGOS studio","Every boot","1.0","3.0","After first boot: any input","All","Same timing"),
(5,"FE_BOOT_LOGOS tech card","Every boot","1.0","2.5","After first boot: any input","All","Unreal Engine and Wwise marks on one card"),
(6,"FE_BOOT_SHADER","First launch, driver change, shader-changing patch","0","until done","Play Now after 10 s","PC, Steam Deck","Runs async; Play Now continues while compiling at lower priority"),
(7,"FE_BOOT_LANG","First run","0","until input","No","All","Logos above load in the background during first-run screens"),
(8,"FE_BOOT_EULA","First run or new EULA version","0","until input","No","All","Decline: PC quits; console returns to platform home"),
(9,"FE_BOOT_PRIV","First run or new policy version","0","until input","No","All",""),
(10,"FE_BOOT_A11Y","First run","0","until input","Continue","All","Narration starts reading from here if on"),
(11,"FE_BOOT_BRI or FE_BOOT_HDR","First run, or display mode changed SDR<>HDR","0","until input","Use System Calibration (console HDR)","All",""),
(12,"FE_BOOT_AUDIO","First run","0","until input","Continue","All","Default preset from platform audio output"),
(13,"FE_TITLE","Every boot","0","until input","n/a","All","Target: cold boot to title in 20 s or less on base PS5 without first-run screens (DC)"),
(14,"FE_CONNECT","After first input, unless offline chosen","0","15.0","Play Offline after 5 s","All","Also checks build version (FE_UPDATE)"),
(15,"FE_LINK","First successful connect per platform account","0","until input","Not Now","All","Max 3 asks, then only from Options > Account"),
(16,"FE_NEWS","Connected and new news since last view, once per day","0","until input","Close","All",""),
(17,"FE_MAIN","Every boot","0","until input","n/a","All",""),
]
w("boot_sequence.csv", ["step","screen","shown_when","min_s","max_s","skip_rule","platform","notes"], BOOT)

# ---------------------------------------------------------------- widgets (every button and control)
WID = []
def b(screen, wid, kind, str_id, action, target="", enabled="Always", platform="All", focus="", notes=""):
    WID.append((wid, screen, kind, str_id, action, target, enabled, platform, focus, notes))
b("FE_BOOT_EPI","EPI_CONTINUE","hold button","STR_FE_EPI_CONTINUE","Advance","FE_BOOT_LOGOS","After 2.0 s",focus="Yes")
b("FE_BOOT_SHADER","SHADER_BAR","progress bar","STR_FE_SHADER_PCT","Display","")
b("FE_BOOT_SHADER","SHADER_PLAY","button","STR_FE_SHADER_SKIP","Continue boot, compile in background","FE_BOOT_LANG","After 10 s","PC, Steam Deck","Yes")
b("FE_BOOT_LANG","LANG_TEXT","list (12)","STR_FE_LANG_TEXT","Set text language live","", focus="Yes", notes="Entries STR_FE_LANG_EN..ZHT")
b("FE_BOOT_LANG","LANG_VOICE","list (5)","STR_FE_LANG_VOICE","Set voice language","", notes="EN FR DE ES JA")
b("FE_BOOT_LANG","LANG_OK","button","STR_FE_A11Y_CONTINUE","Advance","FE_BOOT_EULA")
b("FE_BOOT_EULA","EULA_TEXT","scroll box","STR_FE_EULA_T","Scroll","", notes="Text from legal, versioned; STR_FE_EULA_VERSION under title")
b("FE_BOOT_EULA","EULA_ACCEPT","button","STR_FE_EULA_ACCEPT","Store accepted version","FE_BOOT_PRIV","Scrolled to end",focus="Yes")
b("FE_BOOT_EULA","EULA_DECLINE","button","STR_FE_EULA_DECLINE","Show STR_FE_EULA_DECLINE_B then quit or return home","")
b("FE_BOOT_PRIV","PRIV_CRASH","toggle (default Off)","STR_FE_PRIV_CRASH","Set consent","", focus="Yes")
b("FE_BOOT_PRIV","PRIV_TELEM","toggle (default Off)","STR_FE_PRIV_TELEM","Set consent","")
b("FE_BOOT_PRIV","PRIV_READ","button","STR_FE_PRIV_READ","Open policy scroll view","FE_LEGAL")
b("FE_BOOT_PRIV","PRIV_OK","button","STR_FE_PRIV_CONTINUE","Advance","FE_BOOT_A11Y")
b("FE_BOOT_A11Y","A11Y_NARR","toggle","STR_FE_A11Y_NARR","Menu narration on/off","", focus="Yes", notes="Default = platform screen reader state")
b("FE_BOOT_A11Y","A11Y_SUBS","toggle (default On)","STR_FE_A11Y_SUBS","Subtitles","")
b("FE_BOOT_A11Y","A11Y_SUBSIZE","3-step selector","STR_FE_A11Y_SUBSIZE","Small / Medium / Large","", notes="Values from accessibility thread")
b("FE_BOOT_A11Y","A11Y_CB","selector","STR_FE_A11Y_CB","Off / Protan / Deutan / Tritan","")
b("FE_BOOT_A11Y","A11Y_MORE","button","STR_FE_A11Y_OPEN","Open full accessibility settings","design/accessibility/ settings menu")
b("FE_BOOT_A11Y","A11Y_OK","button","STR_FE_A11Y_CONTINUE","Advance","FE_BOOT_BRI")
b("FE_BOOT_BRI","BRI_GAMMA","slider 1.60-2.80 step 0.05, default 2.20","STR_FE_BRI_GAMMA","Live preview","", focus="Yes")
b("FE_BOOT_BRI","BRI_RESET","button","STR_FE_BRI_RESET","Gamma 2.20","")
b("FE_BOOT_BRI","BRI_OK","button","STR_FE_BRI_CONFIRM","Advance","FE_BOOT_AUDIO")
b("FE_BOOT_HDR","HDR_SYSTEM","button","STR_FE_BRI_SYSTEM","Use console system HDR values","FE_BOOT_AUDIO", platform="PS5, Xbox", focus="Yes")
b("FE_BOOT_HDR","HDR_MAX","slider 300-10000 nits step 50, default = display report or 1000","STR_FE_BRI_HDR_MAX","Step 1","")
b("FE_BOOT_HDR","HDR_PAPER","slider 80-500 nits step 10, default 200","STR_FE_BRI_HDR_PAPER","Step 2","")
b("FE_BOOT_HDR","HDR_BLACK","slider 0.000-0.050 nits step 0.001, default 0.005","STR_FE_BRI_HDR_BLACK","Step 3","")
b("FE_BOOT_HDR","HDR_RESET","button","STR_FE_BRI_RESET","Restore defaults","")
b("FE_BOOT_HDR","HDR_OK","button","STR_FE_BRI_CONFIRM","Advance","FE_BOOT_AUDIO")
b("FE_BOOT_AUDIO","AUD_TV","radio","STR_FE_AUDIO_TV","Mix preset TV","", focus="Yes")
b("FE_BOOT_AUDIO","AUD_HOME","radio","STR_FE_AUDIO_HOME","Mix preset Home Theater (wide range)","")
b("FE_BOOT_AUDIO","AUD_HEAD","radio","STR_FE_AUDIO_HEAD","Mix preset Headphones (binaural on)","")
b("FE_BOOT_AUDIO","AUD_NIGHT","toggle (default Off)","STR_FE_AUDIO_NIGHT","Night mode compression","")
b("FE_BOOT_AUDIO","AUD_OK","button","STR_FE_A11Y_CONTINUE","Advance","FE_TITLE")
b("FE_TITLE","TITLE_PRESS","prompt","STR_TITLE_PRESS","Engage: bind controller/user, go online","FE_CONNECT", notes="PC keyboard shows STR_FE_TITLE_PRESS_PC")
b("FE_TITLE","TITLE_PROFILE","label","STR_FE_TITLE_PROFILE","Display","", platform="PS5, Xbox")
b("FE_TITLE","TITLE_VERSION","label","STR_TITLE_VERSION","Display bottom right","")
b("FE_TITLE","TITLE_COPY","label","STR_TITLE_COPYRIGHT","Display bottom left","")
b("FE_ONLINE_FAIL","ONF_RETRY","button","STR_FE_ONLINE_RETRY","Retry connect","FE_CONNECT", focus="Yes")
b("FE_ONLINE_FAIL","ONF_OFFLINE","button","STR_FE_ONLINE_OFFLINE","Set offline for session","FE_MAIN")
b("FE_LINK","LINK_YES","button","STR_FE_LINK_YES","Show code STR_FE_LINK_CODE, poll 5 s","FE_MAIN", focus="Yes")
b("FE_LINK","LINK_LATER","button","STR_FE_LINK_LATER","Count decline","FE_MAIN")
b("FE_NEWS","NEWS_CARDS","card list (max 3)","STR_FE_NEWS_T","Open link card in Patch notes or season page","FE_PATCH")
b("FE_NEWS","NEWS_HIDE","toggle","STR_FE_NEWS_HIDE_TODAY","Suppress for 24 h","")
b("FE_NEWS","NEWS_CLOSE","button","STR_FE_NEWS_DISMISS","Close","FE_MAIN", focus="Yes")
b("FE_MAIN","MAIN_CONTINUE","button + subtitle","STR_TITLE_CONTINUE","Load newest save of last played character","Loading", "Any save exists", focus="Yes", notes="Subtitle STR_TITLE_CONTINUE_SUB; disabled shows STR_FE_MAIN_CONTINUE_NONE")
b("FE_MAIN","MAIN_NEW","button","STR_TITLE_NEW","Pick slot then Character creation","Character creation", notes="CNF_NEW_GAME if saves exist; STR_FE_CHAR_FULL if 10 used")
b("FE_MAIN","MAIN_CHARS","button","STR_FE_MAIN_CHAR","Open characters","FE_CHARS","Any save exists")
b("FE_MAIN","MAIN_COOP","button","STR_TITLE_COOP","Open co-op lobby with last character","Co-op and multiplayer lobby","Online and any save exists")
b("FE_MAIN","MAIN_OPTIONS","button","STR_TITLE_OPTIONS","Open settings","design/accessibility/ settings menu")
b("FE_MAIN","MAIN_EXTRAS","button","STR_FE_MAIN_EXTRAS","Open extras","FE_EXTRAS")
b("FE_MAIN","MAIN_NEWS","button","STR_FE_MAIN_NEWS","Open news","FE_NEWS","Online")
b("FE_MAIN","MAIN_QUIT","button","STR_TITLE_QUIT","Quit confirm","FE_QUIT", platform="PC, Steam Deck", notes="Consoles have no quit item (platform norm)")
b("FE_MAIN","MAIN_ONLINE","status label","STR_TITLE_ONLINE","Shows Online or STR_TITLE_OFFLINE; select to retry connect","FE_CONNECT")
b("FE_MAIN","MAIN_SWITCH","button","STR_FE_TITLE_SWITCH_USER","Platform account picker","FE_TITLE", platform="Xbox")
b("FE_QUIT","QUIT_YES","button","STR_PAUSE_QUIT_DESK","Exit app","")
b("FE_QUIT","QUIT_NO","button","STR_FE_MAIN_HINT_BACK","Close","FE_MAIN", focus="Yes")
b("FE_CHARS","CHARS_NEW","card","STR_FE_CHAR_NEW","New game in empty slot","Character creation","Fewer than 10 characters")
b("FE_CHARS","CHARS_CARD","card x10","STR_FE_CHAR_CARD","Focus shows sub line, cycle, act, endings","", focus="Newest", notes="Sub STR_FE_CHAR_CARD_SUB; badges STR_FE_CHAR_CYCLE, STR_FE_CHAR_ACT, STR_FE_CHAR_ENDINGS, cloud state")
b("FE_CHARS","CHARS_PLAY","button","STR_FE_CHAR_PLAY","Load newest save","Loading")
b("FE_CHARS","CHARS_LOAD","button","STR_FE_CHAR_LOAD","Open save list","FE_SAVES")
b("FE_CHARS","CHARS_NG","button","STR_FE_MAIN_NG_PLUS","NG+ confirm","FE_NG","Character has seen an ending")
b("FE_CHARS","CHARS_DELETE","hold button 1.5 s","STR_FE_CHAR_DELETE_HOLD","Delete character and all its saves (local + cloud)","CNF_DELETE_SAVE", notes="Hold, then modal; two steps by design")
b("FE_SAVES","SAVES_ROW","row","STR_FE_SAVE_CARD","Select to load","CNF_LOAD (in game) or Loading", focus="Newest", notes="Stamp STR_FE_SAVE_STAMP; extra STR_FE_SAVE_EMBER, STR_FE_SAVE_GHOST, STR_FE_SAVE_MODS, cloud label")
b("FE_SAVES","SAVES_DELETE","button","STR_FE_SAVE_DELETE","Delete one save","CNF_DELETE_SAVE","Manual or quick save only", notes="Protected and autosave rows show STR_FE_SAVE_LOCKED")
b("FE_SAVES","SAVES_BACK","button","STR_FE_MAIN_HINT_BACK","Back","FE_CHARS")
b("FE_SAVE_GAME","SAVEG_NEW","row","STR_FE_SAVE_NEW","Write a new manual save","", "Fewer than 10 manual saves and save allowed", focus="Yes", notes="If full show STR_FE_SAVE_FULL")
b("FE_SAVE_GAME","SAVEG_ROW","row x10","STR_FE_SAVE_CARD","Overwrite","CNF_OVERWRITE")
b("FE_SAVE_GAME","SAVEG_DELETE","button","STR_FE_SAVE_DELETE","Delete","CNF_DELETE_SAVE")
b("FE_CLOUD","CLOUD_LOCAL","card","STR_FE_CLOUD_LOCAL","Keep local","FE_CHARS", focus="Card with more play time")
b("FE_CLOUD","CLOUD_REMOTE","card","STR_FE_CLOUD_REMOTE","Keep cloud","FE_CHARS")
b("FE_NG","NG_BEGIN","button","STR_FE_NG_CONFIRM","Snapshot save, apply CHL_NG cycle, start Act 1","Loading")
b("FE_NG","NG_LATER","button","STR_FE_NG_LATER","Close","", focus="Yes", notes="Default focus on the safe choice")
b("FE_POST","POST_RETURN","button","STR_FE_POST_RETURN","Load post-ending world state at Lantern Hold","Loading", focus="Yes")
b("FE_POST","POST_NG","button","STR_FE_POST_NG","NG+ confirm","FE_NG")
b("FE_POST","POST_TITLE","button","STR_FE_POST_TITLE","Autosave then title","FE_TITLE")
b("FE_EXTRAS","EX_CREDITS","button","STR_TITLE_CREDITS","Play credits","FE_CREDITS", focus="Yes")
b("FE_EXTRAS","EX_PHOTOS","button","STR_FE_EXTRAS_PHOTOS","Open photos","FE_PHOTOS")
b("FE_EXTRAS","EX_ENDINGS","button","STR_FE_EXTRAS_ENDINGS","Open endings","FE_ENDINGS")
b("FE_EXTRAS","EX_CINEMA","button","STR_FE_EXTRAS_CINEMA","Open cinematics","FE_CINEMA","At least one seen")
b("FE_EXTRAS","EX_PATCH","button","STR_FE_EXTRAS_PATCH","Open notes","FE_PATCH")
b("FE_EXTRAS","EX_LEGAL","button","STR_FE_EXTRAS_LEGAL","Open legal","FE_LEGAL")
b("FE_PHOTOS","PH_GRID","grid 4x3 per page","STR_FE_PHOTOS_COUNT","View full screen","", platform="PC, Steam Deck", notes="Empty: STR_FE_PHOTOS_EMPTY; console: STR_FE_PHOTOS_CONSOLE")
b("FE_PHOTOS","PH_DELETE","button","STR_FE_PHOTOS_DELETE","Delete file after confirm","", platform="PC, Steam Deck")
b("FE_PHOTOS","PH_FOLDER","button","STR_FE_PHOTOS_FOLDER","Open OS folder","", platform="PC")
b("FE_ENDINGS","END_CARD","card x3","STR_FE_EXTRAS_ENDING_LOCKED","Replay ending cinematic if seen","FE_CINEMA", notes="Seen cards use ending name from design/campaign/endings.csv")
b("FE_LEGAL","LEG_EULA","button","STR_FE_LEGAL_EULA","Scroll view","")
b("FE_LEGAL","LEG_PRIV","button","STR_FE_LEGAL_PRIVACY","Scroll view","")
b("FE_LEGAL","LEG_TOS","button","STR_FE_LEGAL_TOS","Scroll view","")
b("FE_LEGAL","LEG_THIRD","button","STR_FE_LEGAL_THIRD","Scroll view of credits_attribution.csv license texts","")
b("FE_CREDITS","CRED_SKIP","hold button 1.5 s","STR_FE_CRED_SKIP","End credits","FE_POST or FE_EXTRAS")
b("FE_CREDITS","CRED_FAST","hold","STR_FE_CRED_FAST","Scroll x4 while held","")
b("FE_PHOTO","PHOTO_TAKE","button","STR_PHOTO_TAKE","Capture","", focus="n/a", notes="Hides panel 0.2 s, shutter SFX, toast STR_PHOTO_SAVED")
b("FE_PHOTO","PHOTO_HIDE","button","STR_PHOTO_HIDE_UI","Toggle panel","")
b("FE_PHOTO","PHOTO_RESET","button","STR_PHOTO_RESET","Reset all controls","")
b("FE_PHOTO","PHOTO_EXIT","button","STR_PHOTO_EXIT","Return to game","Game")
missing = [x[3] for x in WID if not has(x[3])]
assert not missing, missing
w("widgets.csv", ["widget_id","screen_id","kind","str_id","action","target","enabled_when","platform","default_focus","notes"], WID)

# ---------------------------------------------------------------- transitions
TR = [
# from, trigger, to, anim, ms, sfx, music
("FE_BOOT_EPI","Hold confirm","FE_BOOT_LOGOS","Fade to black","500","","None"),
("FE_BOOT_LOGOS","Timer or skip","FE_TITLE / first-run screens","Fade to black","500","","Start MUS_MENU_LOADING (first run) or MUS_MENU_TITLE"),
("First-run screens","Continue","Next first-run screen","Ledger page turn (slide 200 ms)","200","Play_SFX_Ui_Interface_Confirm","Keep"),
("FE_BOOT_AUDIO","Continue","FE_TITLE","Page burns to cyan line, then logo","1200","Play_SFX_Ui_Interface_TitleReveal (new)","Crossfade to MUS_MENU_TITLE 2.0 s"),
("FE_TITLE","Press start","FE_CONNECT / FE_MAIN","Prompt flares, camera eases right","600","Play_SFX_Ui_Interface_Confirm","Keep"),
("FE_TITLE","Idle 90 s","FE_ATTRACT","Fade","1000","","Crossfade to MUS_THEME_MAIN"),
("FE_ATTRACT","Any input","FE_TITLE","Fade","500","","Crossfade to MUS_MENU_TITLE"),
("FE_MAIN","Select item","Sub screen","Ledger page turn","200","Play_SFX_Ui_Interface_MenuOpen","Keep"),
("Sub screen","Back","Previous screen","Page turn reversed","200","Play_SFX_Ui_Interface_BackCancel","Keep"),
("Any list","Move focus","Same","Cyan underline sweep 120 ms","120","Play_SFX_Ui_Interface_CursorMove","Keep"),
("FE_MAIN / FE_CHARS","Continue, Play or Load","Loading screen","Fade to black, loading screen per data/ui Loading screens","800","Play_SFX_Ui_Interface_Confirm","Fade out over 1.5 s; MUS_MENU_LOADING"),
("Loading","Load done","Game","Fade from black","800","","Region music system takes over"),
("Ledger (pause)","Quit to Title confirmed","FE_TITLE","Autosave first if allowed, fade","800","Play_SFX_Ui_Interface_SaveGame","Crossfade to MUS_MENU_TITLE"),
("Game","Ending cinematic ends","FE_CREDITS","Cut to black 1.0 s, credits fade in","1000","","MUS_MENU_CREDITS from 0:00"),
("FE_CREDITS","Roll ends or skip","FE_POST (after ending) / FE_EXTRAS","Fade to black, post-credit Ostra line 4 s","1500","","Credits tail"),
("Game","Photo mode key","FE_PHOTO","World freezes (solo), HUD fades 120 ms, panel slides in","200","Play_SFX_Ui_Interface_PhotoEnter (new)","Duck -6 dB"),
("FE_PHOTO","Exit","Game","Panel slides out, HUD returns, camera snaps back to player","200","Play_SFX_Ui_Interface_MenuClose","Unduck"),
("Any","Error or confirm popup","Modal","Dim 60%, modal scales 96%->100%","150","SFX_UI_MODAL / SFX_UI_ERROR","Keep"),
("Any","Reduced motion on","Same targets","All slides and scales become 150 ms fades","150","Same","Same"),
]
w("transitions.csv", ["from","trigger","to","animation","duration_ms","sfx","music"], TR)

# ---------------------------------------------------------------- save rules
SR = [
("SAV_01","Characters per platform account","10","tech/03","Each character is its own folder of saves"),
("SAV_02","Autosave per character","1 slot, plus 3 rotating backups","tech/03","Backup 1 is the previous autosave, and so on"),
("SAV_03","Autosave triggers","Anchor rest, region change, boss kill, quest step, Rare+ pickup, every 5 min out of combat (interval option 5/10/15 min)","tech/03 + DC interval","Never in combat"),
("SAV_04","Quicksave","1 slot per character; F5 on PC keyboard, F9 to quickload (with CNF_LOAD unless Options > Gameplay > Confirm Quickload is Off)","DC","Controllers have no quicksave button; use Ledger > Save Game"),
("SAV_05","Manual saves","10 per character (DC); overwrite needed when full","DC","Ledger > Save Game"),
("SAV_06","Protected: Before the End","1 per character, written automatically when MQ_A3_06 The Choice starts (design/campaign/03-main-story.md); never overwritten by other saves, rewritten only if the player reaches that point again","DC","Lets players see all 3 endings without replaying (supports achievements 08 to 10)"),
("SAV_07","Protected: Start of NG+n","1 per character, newest cycle only, written when NG+ begins","DC","Lets the player go back to the finished world"),
("SAV_08","Saving blocked","In combat, boss arena, cinematic, dialogue, airborne or falling, mounted glide, during an invasion, as a co-op guest, inside strikes, raids, Arena","tech/03 + DC","Shows INL_CANT_SAVE with the matching reason string"),
("SAV_09","Co-op","Host saves the world for everyone; guests autosave their character on join, leave and every host autosave","plan 3.11, tech/03",""),
("SAV_10","Online activities","Strikes, raids, Arena save on completion or exit; Seals and cosmetics are account-side and never roll back with a save load","tech/02",""),
("SAV_11","Ember and death on load","Loading any save restores that save's Ember and Shard-ghost exactly. No penalty for loading.","DC","Plan's death rule is not undone by design: autosave runs on death, so Continue always keeps the loss"),
("SAV_12","Death autosave","Death writes the autosave the moment the Shard-ghost drops","DC","Stops quit-to-avoid-loss. Manual saves remain the player's choice."),
("SAV_13","Write method","Async, atomic temp-then-rename, signed (HMAC)","tech/03, tech/02",""),
("SAV_14","Save icon","Lens-cyan Shard glyph bottom right, min 1.0 s visible, STR_PLAT_SAVING on console during writes over 1 s","tech/03 platform rule","Do not power off message per platform"),
("SAV_15","Cloud","Steam Cloud, PS5 and Xbox saves, and Profile service copy for cross-progression","tech/03",""),
("SAV_16","Cloud conflict","Newest by play time wins silently if only one side changed; if both changed show FE_CLOUD; loser kept as Backup 3","tech/03 + DC",""),
("SAV_17","Corruption recovery","Checksum fail: newest good backup, then cloud copy; tell the player which loaded (STR_FE_SAVE_RECOVERED)","plan 4.7, tech/03",""),
("SAV_18","Version","Saves from newer builds refuse to load (ERR_VERSION); older saves upgrade on load and keep a pre-upgrade backup","tech/03",""),
("SAV_19","Mods (PC)","Saves made with mods carry a Modded badge; loading one with mods off warns; achievements off for modded saves","data/ui CNF_MODS",""),
("SAV_20","Slot card data","Portrait capture, name, level, Origin, location, act, NG+ cycle, endings seen, play time, date and time, Ember, Shard-ghost Ember, cloud state, mod badge","DC","Header fields per tech/03"),
("SAV_21","Size budget","Target 2 MB per save, 400 MB per account max (10 chars x 16 saves x 2 MB plus headroom)","DC","Console storage quota request at cert"),
("SAV_22","Delete","Manual and quick saves deletable one at a time; whole character delete removes local and cloud and needs hold plus confirm","DC","Autosave and protected saves only go with the character"),
("SAV_23","Continue","Newest save across the last played character, any type","DC",""),
("SAV_24","Suspend and resume (console)","On resume after over 10 min or network loss, re-check online; world never rolls back","tech/04 cert",""),
("SAV_25","Profile switch","Signed-in user change returns to FE_TITLE after autosave if allowed (STR_PLAT_USER_CHANGE)","cert",""),
]
w("save_rules.csv", ["rule_id","rule","value","source","notes"], SR)

# ---------------------------------------------------------------- photo mode
PM = [
# id, tab, str_id, type, min, max, default, step, notes
("PM_RULE_ENTRY","Rules","STR_PAUSE_PHOTO","rule","","","","","Entry: Ledger > Photo Mode, or press both sticks (L3+R3), or F12 on PC (DC). Not in cinematics, dialogue, loading, Arena, during an invasion, or in combat while online."),
("PM_RULE_PAUSE","Rules","STR_PHOTO_ONLINE_NOTE","rule","","","","","Solo: world freezes. Co-op, strikes, raids: world keeps running, player is not invulnerable, so it is blocked in combat (STR_PHOTO_CANT_COMBAT)."),
("PM_RULE_RADIUS","Rules","STR_PHOTO_CAMERA","rule","","","","","Free camera within 15 m of the player solo, 8 m online; may not pass through walls or below terrain; ceiling 10 m above the player."),
("PM_CAM_FOV","Camera","STR_PHOTO_FOV","slider","20","120","Gameplay FOV","1","Degrees"),
("PM_CAM_ROLL","Camera","STR_PHOTO_ROLL","slider","-90","90","0","1","Degrees"),
("PM_CAM_SPEED","Camera","STR_PHOTO_MOVE_SPEED","slider","0.25","4.0","1.0","0.25","m/s x multiplier"),
("PM_CAM_COLL","Camera","STR_PHOTO_COLLISION","toggle","","","On","","Off allows clipping through foliage only; walls always block"),
("PM_LENS_AF","Lens","STR_PHOTO_AUTOFOCUS","toggle","","","On","",""),
("PM_LENS_TGT","Lens","STR_PHOTO_FOCUS_TARGET","toggle","","","On","","Locks focus to the player head"),
("PM_LENS_FOCUS","Lens","STR_PHOTO_FOCUS","slider","0.1","100","3.0","0.1","Metres; disabled while Auto Focus is On"),
("PM_LENS_AP","Lens","STR_PHOTO_APERTURE","slider","1.2","22","8","stops (1.2 1.4 2 2.8 4 5.6 8 11 16 22)","f-number"),
("PM_LENS_EXP","Lens","STR_PHOTO_EXPOSURE","slider","-3","3","0","0.1","EV"),
("PM_LENS_VIG","Lens","STR_PHOTO_VIGNETTE","slider","0","100","0","1",""),
("PM_LENS_GRAIN","Lens","STR_PHOTO_GRAIN","slider","0","100","0","1",""),
("PM_LENS_CA","Lens","STR_PHOTO_CHROMA","slider","0","100","0","1",""),
("PM_LENS_BLOOM","Lens","STR_PHOTO_BLOOM","slider","0","200","100","5","% of gameplay bloom"),
("PM_LENS_SHARP","Lens","STR_PHOTO_SHARPEN","slider","0","100","0","1",""),
("PM_FIL_PICK","Filter","STR_PHOTO_FILTERS","list","","",FILTERS[0],"",f"{len(FILTERS)} filters: " + "; ".join(FILTERS)),
("PM_FIL_STR","Filter","STR_PHOTO_STRENGTH","slider","0","100","100","1",""),
("PM_FIL_SAT","Filter","STR_PHOTO_SATURATION","slider","-100","100","0","1",""),
("PM_FIL_CON","Filter","STR_PHOTO_CONTRAST","slider","-100","100","0","1",""),
("PM_FIL_TINT","Filter","STR_PHOTO_TINT","slider","-100","100","0","1","Cool to warm"),
("PM_FRM_PICK","Frame","STR_PHOTO_FRAMES","list","","",FRAMES[0],"",f"{len(FRAMES)} frames: " + "; ".join(FRAMES)),
("PM_FRM_GRID","Frame","STR_PHOTO_GRID","selector","","","Off","","Off / Thirds / Golden / Center; never saved into the photo"),
("PM_SUB_POSE","Subject","STR_PHOTO_POSE","list","","","Idle","",f"{len(POSES)} poses (anim set ANIM_PHOTO_POSE_01..{len(POSES):02d})"),
("PM_SUB_EXPR","Subject","STR_PHOTO_EXPRESSION","list","","","Neutral","",f"{len(EXPR)} expressions"),
("PM_SUB_LOOK","Subject","STR_PHOTO_LOOK_CAM","toggle","","","Off","","Head and eyes track camera within 70 deg"),
("PM_SUB_HPLAYER","Subject","STR_PHOTO_HIDE_PLAYER","toggle","","","Off","",""),
("PM_SUB_HALLY","Subject","STR_PHOTO_HIDE_ALLIES","toggle","","","Off","","Co-op players and Echoes; solo only hides Echoes"),
("PM_SUB_HCOMP","Subject","STR_PHOTO_HIDE_COMPANION","toggle","","","Off","",""),
("PM_SUB_HENEMY","Subject","STR_PHOTO_HIDE_ENEMIES","toggle","","","Off","","Solo only"),
("PM_SUB_HWPN","Subject","STR_PHOTO_HIDE_WEAPON","toggle","","","Off","",""),
("PM_SUB_HHELM","Subject","STR_PHOTO_HIDE_HELM","toggle","","","Off","",""),
("PM_SUB_FREEZEFX","Subject","STR_PHOTO_FREEZE_FX","toggle","","","On","","Off lets particles and cloth keep animating while time is frozen (solo)"),
("PM_LGT_SUN","Lights","STR_PHOTO_SUN","slider","-30","30","0","1","Degrees of sun rotation; time of day itself never changes (DC)"),
("PM_LGT_SLOT","Lights","STR_PHOTO_LIGHT_N","3 slots","","","Off","","Each: On, color temperature, intensity, radius, place at camera"),
("PM_LGT_ON","Lights","STR_PHOTO_LIGHT_ON","toggle","","","Off","",""),
("PM_LGT_K","Lights","STR_PHOTO_LIGHT_COLOR","slider","1800","10000","4500","100","Kelvin"),
("PM_LGT_INT","Lights","STR_PHOTO_LIGHT_INT","slider","0","100","50","1","Maps to 0-5000 lm"),
("PM_LGT_RAD","Lights","STR_PHOTO_LIGHT_RAD","slider","1","15","5","0.5","Metres"),
("PM_LGT_PLACE","Lights","STR_PHOTO_LIGHT_PLACE","button","","","","","Light spawns at camera position"),
("PM_STAMP_ON","Stamp","STR_PHOTO_STAMP_ON","toggle","","","Off","","Shardfall wordmark, 6% of width"),
("PM_STAMP_POS","Stamp","STR_PHOTO_STAMP_POS","selector","","","Bottom right","","4 corners"),
("PM_OUT_RES","Output","STR_PHOTO_RES","selector","","","Screen","","Screen / 2x (PC, Steam Deck excluded)"),
("PM_OUT_FMT","Output","STR_PHOTO_FMT","selector","","","PNG","","PC: PNG or JPG 95; console: platform capture. Path Documents/My Games/Shardfall/Photos/Shardfall_YYYYMMDD_HHMMSS.png"),
("PM_OUT_HUD","Output","STR_PHOTO_HIDE_UI","rule","","","","","HUD, subtitles, nameplates and damage numbers never appear in photos"),
("PM_BTN_TAKE","Buttons","STR_PHOTO_TAKE","button","","","","","Controller: A / Cross. PC: Space or Enter"),
("PM_BTN_HIDE","Buttons","STR_PHOTO_HIDE_UI","button","","","","","Controller: Y / Triangle. PC: H"),
("PM_BTN_RESETTAB","Buttons","STR_PHOTO_RESET_TAB","button","","","","","Controller: X / Square (hold 1 s for Reset All). PC: R"),
("PM_BTN_EXIT","Buttons","STR_PHOTO_EXIT","button","","","","","Controller: B / Circle. PC: Esc"),
("PM_BTN_TABS","Buttons","STR_PHOTO_TAB_CAMERA","tabs","","","Camera","","LB/RB or Q/E switch tabs: Camera, Lens, Filter, Frame, Subject, Lights, Stamp"),
("PM_BTN_MOVE","Buttons","STR_PHOTO_CAMERA","input","","","","","Left stick or WASD move, right stick or mouse look, LT/RT or Ctrl/Space down/up"),
]
assert not [p for p in PM if not has(p[2])]
w("photo_mode.csv", ["control_id","tab","str_id","type","min","max","default","step","notes"], PM)

# ---------------------------------------------------------------- credits
# headcount: plan 5.1 peak 280 + crediting all who worked 30+ days across phases (DC estimate)
orgrows = list(csv.DictReader(open(os.path.join(ROOT, "design", "production", "team_by_phase.csv"), encoding="utf-8")))
cast = list(csv.DictReader(open(os.path.join(ROOT, "design", "audio", "vo_cast.csv"), encoding="utf-8")))
peak = {r["department"]: int(r["P4+P5"]) for r in orgrows if r["department"] and not r["department"].startswith("TOTAL")}
def peakof(d): return peak.get(d, 0)
_lic = lambda f: list(csv.DictReader(open(os.path.join(ROOT, "design", "licensing", f), encoding="utf-8")))
LIC_NAMES = (sum(int(r["headcount"] or 0) for r in _lic("team.csv")) + len(_lic("partner_types.csv")) +
             len({r["supplier_type"] for r in _lic("ce_bill_of_materials.csv")}) + len(_lic("logistics_lanes.csv")) + 2 * len(_lic("transmedia.csv")))
CS = [
# order, section_str, source, est_names, sort rule, notes
(1,"Logo card","",0,"","Shardfall wordmark 6 s, then 'A Shardfall Team game' 4 s"),
(2,"STR_FE_CRED_SEC_01","team_by_phase Leadership",peakof("Leadership"),"Fixed order: game, creative, art, tech, audio directors, executive producer","Big type: 2 names per screen"),
(3,"STR_FE_CRED_SEC_02","team_by_phase Design",peakof("Design"),"Role then surname",""),
(4,"STR_FE_CRED_SEC_03","org_chart Region teams",150,"One block per region, Cinderreach to Hollowdeep, lead first","Names may repeat with Design/Art; list each person once, under their home team"),
(5,"STR_FE_CRED_SEC_04","team_by_phase Engineering",peakof("Engineering"),"Role then surname",""),
(6,"STR_FE_CRED_SEC_05","team_by_phase Online/Backend",peakof("Online/Backend"),"Surname",""),
(7,"STR_FE_CRED_SEC_06","team_by_phase Art",peakof("Art"),"Role then surname",""),
(8,"STR_FE_CRED_SEC_07","team_by_phase Animation",peakof("Animation"),"Surname",""),
(9,"STR_FE_CRED_SEC_08","org_chart Boss team",15,"Surname",""),
(10,"STR_FE_CRED_SEC_09","org_chart Cinematics",12,"Surname",""),
(11,"STR_FE_CRED_SEC_10","team_by_phase Audio",peakof("Audio"),"Composer first, then surname",""),
(12,"STR_FE_CRED_SEC_11","team_by_phase Narrative",peakof("Narrative"),"Lead writer first, then surname",""),
(13,"STR_FE_CRED_SEC_12","team_by_phase UX/UI",peakof("UX/UI"),"Surname","Includes accessibility consultants"),
(14,"STR_FE_CRED_SEC_13","team_by_phase Production",peakof("Production"),"Role then surname",""),
(15,"STR_FE_CRED_SEC_14","team_by_phase QA (P6 peak)",60,"Lead first, then surname; external QA vendor names",""),
(16,"STR_FE_CRED_SEC_15","design/production/localization.csv",11*6,"One block per language in localization.csv order: vendor, translators, LQA, VO director for the 4 dubbed languages","Estimate 6 names per language"),
(17,"STR_FE_CRED_SEC_16","design/audio/vo_cast.csv",len(cast),"Script order: Ostra first, then by lines_en descending","Format: Character .... Actor. Dubbed casts listed per language after English"),
(18,"STR_FE_CRED_SEC_17","design/art/mocap_shotlist.csv",30,"Surname","Estimate 30 performers"),
(19,"STR_FE_CRED_SEC_18","design/art/outsource_packages.csv",120,"Company, then names they supply","Estimate"),
(20,"STR_FE_CRED_SEC_19","team_by_phase Live ops/Analytics",8,"Surname",""),
(21,"STR_FE_CRED_SEC_20","team_by_phase Marketing/Community",10,"Surname",""),
(21.5,"STR_FE_CRED_SEC_26","design/licensing/team.csv, partner_types.csv, ce_bill_of_materials.csv, logistics_lanes.csv, transmedia.csv",LIC_NAMES,"Four blocks: Consumer Products team (Head of Consumer Products first, then role order of team.csv); licensing and merchandise partners (company per partner_types.csv order, then named contacts); Collector's Edition manufacturing and logistics partners (supplier per ce_bill_of_materials.csv, then logistics_lanes.csv); transmedia partners (transmedia.csv order: company, then credited writers and artists)","Estimate: licensing team plus 1 company line per partner, CE supplier and lane, plus 2 credited creators per transmedia project. Fill names when contracts sign"),
(22,"STR_FE_CRED_SEC_21","team_by_phase IT/HR/Finance",4,"Surname",""),
(23,"STR_FE_CRED_SEC_22","Playtest roster",0,"One line: STR_FE_CRED_PLAYTESTERS with count","Names not listed (privacy)"),
(24,"STR_FE_CRED_SEC_23","Production",40,"Free order","Families, partners, platform holders' account teams"),
(25,"STR_FE_CRED_MEMORY","Production",0,"","Only if needed; centered, 8 s hold"),
(26,"STR_FE_CRED_SEC_24","credits_attribution.csv",0,"Fixed order of credits_attribution.csv","Logos where a license requires one"),
(27,"STR_FE_CRED_SEC_25","STR_FE_CRED_LEGAL",0,"","Legal lines, ratings logos not shown here"),
(28,"STR_FE_CRED_THANKS","",0,"","8 s hold, then post-credit Ostra line by ending (STR_FE_CRED_POST_A/B/C)"),
]
CS = [(k + 1,) + tuple(c[1:]) for k, c in enumerate(sorted(CS, key=lambda c: c[0]))]  # renumber after inserts
assert all(has(c[1]) for c in CS if c[1].startswith("STR_"))
total_names = sum(c[3] for c in CS)
heads = len([c for c in CS if c[1].startswith("STR_FE_CRED_SEC")])
LINE = 64  # px at 4K per name line (36 px type, 1.78 leading)
height = total_names * LINE + heads * 400 + 12 * 2160  # section gaps 400 px, 12 full-screen holds
DUR = 600 - 30  # music 600 s minus 30 s tail for thanks and post line
speed = round(height / DUR, 1)
w("credits_structure.csv", ["order","section_str","source","est_names","sort_rule","notes"], CS)
CR = [
("CRD_RULE_WHO","Who is credited","Everyone who worked 30 days or more on the game, including people who left before launch, contractors and outsourcers (DC, follows IGDA crediting guidance)"),
("CRD_RULE_NAME","Names","As the person asks, in their chosen script; Latin transliteration beside non-Latin names only if they ask"),
("CRD_RULE_TITLE","Titles","The highest title held for at least 3 months"),
("CRD_ROLL_TIME","Roll length","600 s, matched to MUS_MENU_CREDITS; 570 s of scroll then 30 s for thanks and post-credit line"),
("CRD_ROLL_SPEED",f"Scroll speed","%s px/s at 4K (%s est. name lines, %s headings). Recompute from final list so the roll ends with the music." % (speed, total_names, heads)),
("CRD_TYPE","Type","Headings Spectral SC 48 px, roles Plex Mono 28 px lens cyan, names Plex Sans 36 px, at 4K; min contrast 7:1"),
("CRD_LAYOUT","Layout","Scroll column in the left 60%; right 40% shows up to 12 of the player's photo-mode shots, 8 s each with 1 s crossfade, else 12 concept paintings"),
("CRD_SKIP","Skip","Hold Back 1.5 s at any time, first view included (DC); hold Confirm to scroll x4"),
("CRD_WHEN","When it plays","After each ending cinematic, and from Extras > Credits. Achievement and save happen before it starts."),
("CRD_A11Y","Accessibility","Menu narration reads section headings only; reduced motion swaps scroll for paged cards, 6 s each"),
("CRD_LOC","Localization","Headings and legal lines translated; names never translated; RTL not needed (no RTL language in the 12)"),
("CRD_DATA","Data","Names live in a credits table filled by production at Gate 7 (plan 7); not in strings.csv, as names are not translated"),
]
w("credits_rules.csv", ["rule_id","rule","value"], CR)
ATT = [
("ATT_UE","Unreal Engine 5","Epic Games","EULA notice in credits and legal screen","STR_FE_CRED_UE","Logo on boot tech card allowed under brand guidelines"),
("ATT_WWISE","Wwise","Audiokinetic","Credit and logo required by license","STR_FE_CRED_WWISE","Logo on tech card and in credits"),
("ATT_EOS","Epic Online Services, Easy Anti-Cheat","Epic Games","Disclosure in EULA and privacy (tech/02)","STR_FE_CRED_EOS",""),
("ATT_CRASH","Crash reporting (Sentry or BugSplat, tech/06)","Vendor TBD","Per vendor terms","STR_FE_CRED_SEC_24","Fill when chosen"),
("ATT_BACKEND","Cloud hosting (AWS, tech/02)","Amazon Web Services","Trademark line if logo used","STR_FE_CRED_SEC_24",""),
("ATT_FONT_HEAD","Ledger heading face (Spectral SC stand-in)","Production Type","SIL Open Font License text in Third-Party Licenses","STR_FE_CRED_FONTS","Visual Bible: license to confirm"),
("ATT_FONT_BODY","Interface face (IBM Plex Sans stand-in)","IBM","SIL Open Font License text","STR_FE_CRED_FONTS",""),
("ATT_FONT_MONO","Numerals face (IBM Plex Mono stand-in)","IBM","SIL Open Font License text","STR_FE_CRED_FONTS",""),
("ATT_FONT_CJK","CJK and Hangul fallback faces","Vendor TBD","Per license; needed for JA, KO, ZH-S, ZH-T","STR_FE_CRED_FONTS","Gap: pick at Phase 2 font licensing"),
("ATT_PLATFORM","PlayStation, Xbox, Steam marks","Platform holders","Per platform guidelines, legal line only","STR_FE_CRED_LEGAL",""),
("ATT_AI","AI tool disclosure","Shardfall Team","Plan 5.5 and legal_eula_privacy.md","STR_FE_CRED_AI","Store disclosure handled by production"),
]
w("credits_attribution.csv", ["att_id","software_or_asset","owner","requirement","str_id","notes"], ATT)

# ---------------------------------------------------------------- new popups
POP = [
("CNF_CLOUD_CONFLICT","modal","Characters and saves","Modal dialog over current screen","Both local and cloud copies changed since last sync","STR_FE_CLOUD_T","STR_FE_CLOUD_B","This Device / Cloud","Until input","Button press","5","Blocks input","SFX_UI_MODAL"),
("CNF_NG_PLUS","modal","Characters and saves","Modal dialog over current screen","Begin New Game+ chosen","STR_FE_NG_T","STR_FE_NG_B","Begin / Not Now","Until input","Button press","5","Blocks input","SFX_UI_MODAL"),
("CNF_EULA_DECLINE","modal","Boot","Modal dialog over current screen","EULA declined","STR_FE_EULA_T","STR_FE_EULA_DECLINE_B","Back / Quit","Until input","Button press","5","Blocks input","SFX_UI_MODAL"),
("ERR_ONLINE_FAIL","error","Title and main menu","Modal dialog, red rule","Connect timeout 15 s or backend down","STR_FE_ONLINE_FAIL_T","STR_FE_ONLINE_FAIL_B","Retry / Play Offline","Until input","Button press","6","Blocks input","SFX_UI_ERROR"),
("ERR_UPDATE","error","Title and main menu","Modal dialog, red rule","Build older than backend minimum","STR_FE_UPDATE_T","STR_FE_UPDATE_B","OK","Until input","Button press","6","Blocks input; continues offline","SFX_UI_ERROR"),
("NTF_SAVE_RECOVERED","toast","HUD","HUD notification feed, top right","Backup loaded after a damaged save","STR_FE_SAVE_RECOVERED","","","6.0","Auto","4","Queue","SFX_UI_TOAST"),
("NTF_QUICKSAVE","toast","HUD","HUD notification feed, top right","Quicksave written","STR_FE_QS_DONE","","","1.5","Auto","2","Same ID within 2 s merges","SFX_UI_TOAST"),
("NTF_PHOTO_SAVED","toast","Photo mode","Photo mode, bottom centre","Photo written","STR_PHOTO_SAVED","STR_PHOTO_SAVED_PATH","","2.0","Auto","2","Replaces previous","SFX_UI_TOAST"),
("INL_CANT_SAVE_BOSS","inline","Various","Inline on current screen","Save attempted in boss arena","STR_FE_CANT_SAVE_BOSS","","","3.0","Auto","1","Replaces previous inline message","SFX_UI_INLINE"),
("INL_CANT_SAVE_GUEST","inline","Various","Inline on current screen","Save attempted as co-op guest","STR_FE_CANT_SAVE_GUEST","","","3.0","Auto","1","Replaces previous inline message","SFX_UI_INLINE"),
("INL_CANT_SAVE_ONLINE","inline","Various","Inline on current screen","Save attempted in strike, raid or Arena","STR_FE_CANT_SAVE_ONLINE","","","3.0","Auto","1","Replaces previous inline message","SFX_UI_INLINE"),
("INL_CANT_SAVE_CINE","inline","Various","Inline on current screen","Save attempted in cinematic or dialogue","STR_FE_CANT_SAVE_CINE","","","3.0","Auto","1","Replaces previous inline message","SFX_UI_INLINE"),
("INL_PHOTO_COMBAT","inline","HUD","Inline on current screen","Photo mode key in combat while online","STR_PHOTO_CANT_COMBAT","","","3.0","Auto","1","Replaces previous inline message","SFX_UI_INLINE"),
("INL_PHOTO_HERE","inline","HUD","Inline on current screen","Photo mode key in a blocked context","STR_PHOTO_CANT_HERE","","","3.0","Auto","1","Replaces previous inline message","SFX_UI_INLINE"),
("INL_SAVES_FULL","inline","Characters and saves","Inline on current screen","New Save with 10 manual saves","STR_FE_SAVE_FULL","","","3.0","Auto","1","Replaces previous inline message","SFX_UI_INLINE"),
("INL_CHARS_FULL","inline","Characters and saves","Inline on current screen","New Character with 10 characters","STR_FE_CHAR_FULL","","","4.0","Auto","1","Replaces previous inline message","SFX_UI_INLINE"),
]
POP_MERGED = [p[0] for p in POP if p[0] in existing_pop]  # rows the data merge already took in (FE-DR-002)
assert all(has(p[5]) and (not p[6] or has(p[6])) for p in POP)
w("popups_frontend.csv", ["popup_id","kind","screen","layer","trigger","title_str","body_str","buttons","duration_s","dismiss","priority","queue_rule","sfx_hook"], POP)

# ---------------------------------------------------------------- data requests
DR = [
("FE-DR-001","data/ui/strings.csv (gen ui_c.py)","none",f"Add the {len(S)} rows in design/frontend/strings_frontend.csv","Front-end screens need them; IDs checked free of clashes"),
("FE-DR-002","data/ui/popups.csv (gen ui_c.py)",(f"Done: all {len(POP)} rows are in data/ui/popups.csv" if len(POP_MERGED) == len(POP) else f"{len(POP_MERGED)} of {len(POP)} merged"),f"Add the {len(POP)} rows in design/frontend/popups_frontend.csv","Cloud conflict, NG+, online fail, save-blocked reasons, photo toasts"),
("FE-DR-003","data/ui/strings.csv STR_TITLE_COPYRIGHT","Done: data now uses the © sign","© {VAR_year} Shardfall Team. All rights reserved.","Use the real © sign; fonts cover it"),
("FE-DR-004","data/ui/strings.csv STR_TIP_REG_R2..R5","Done: tips now match region bands (was Saltmere 10-24, Thornwood 22-36, Rimefall 42-58)","Use actors/region_bands.csv (Saltmere 10-22, Thornwood 20-34, Glasswaste 32-46, Rimefall 44-58)","Tips disagree with the link pass bands in data/README.md item 1"),
("FE-DR-005","design/audio/event_map.csv","none","Add Play_SFX_Ui_Interface_TitleReveal, _LogoStinger, _PhotoEnter, _PhotoShutter, _SlotSelect, _CharacterDelete, _CreditsSkip","Front-end transitions and widgets reference them"),
("FE-DR-006","data/assets/asset_hooks.csv (via link.py)","none",f"Add ANIM_PHOTO_POSE_01..{len(POSES):02d}, ANIM_PHOTO_EXPR_01..{len(EXPR):02d}, UI_PHOTO_FRAME_01..{len(FRAMES)-1:02d}, UI_PHOTO_FILTER_LUT_01..{len(FILTERS)-1:02d}, UI_FE_LOGO_CARD, UI_FE_BRI_PLATE, UI_FE_HDR_PLATES, UI_FE_SAVE_ICON","Photo mode and boot assets"),
("FE-DR-007","design/tech/03-save-ai-world.md Slots line","Done: Slots line lists quicksave, manual and protected saves","Also 1 quicksave, 10 manual and 2 protected saves per character (design/frontend/save_rules.csv)","Strings and Ledger already offer Quicksave and Manual Save"),
]
w("data-requests.csv", ["dr_id","owner_table","current_value","requested_value","reason"], DR)

print(f"strings {len(S)}, screens {len(SCREENS)}, widgets {len(WID)}, transitions {len(TR)}, save rules {len(SR)}, photo {len(PM)}, credits sections {len(CS)}, popups {len(POP)}, est credit names {total_names}, scroll {speed} px/s")
