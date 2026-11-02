#!/usr/bin/env python3
"""Generate Shardfall platform integration tables into design/platform/.
Every value not set by the master plan or another owning folder is a Shardfall design choice (3 Oct 2026).
Run: python3 design/platform/tools/gen_platform.py (from game-plan/)."""
import csv, os, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GP = os.path.dirname(os.path.dirname(ROOT))
CH = "Shardfall choice"
STRINGS = []  # new UI strings for data/ui/strings.csv (merge pass)

def w(name, header, rows):
    with open(os.path.join(ROOT, name), "w", newline="") as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)
    print(f"{name}: {len(rows)} rows")

def s(sid, screen, text, notes="", tokens=""):
    if not tokens:
        tokens = " ".join(t.strip("{}") for t in text.split() if t.startswith("{") or "{" in t).replace(".", "").replace(",", "")
        tokens = " ".join(x[x.index("{")+1:x.index("}")] for x in text.split() if "{" in x and "}" in x)
    STRINGS.append([sid, screen, text, math.ceil(len(text) * 1.4), tokens, notes])
    return sid

REG = [("REG_01", "Cinderreach"), ("REG_02", "Saltmere"), ("REG_03", "Thornwood"), ("REG_04", "Glasswaste"),
       ("REG_05", "Rimefall"), ("REG_06", "Hollowdeep")]

# ---------------------------------------------------------------- platform feature matrix
feat = [
 # id, area, feature, PC Steam, PS5, Xbox Series, rule, owner module, source
 ("PF_01","Account","Platform sign-in","Steam account; EOS Connect with Steam ticket","PSN account; EOS Connect with PSN token","Xbox account (XUser); EOS Connect with XSTS token","Sign-in is silent at boot. No Shardfall account is ever required to play solo.","SfOnline","tech/02-online.md; "+CH),
 ("PF_02","Account","Cross-progression link","Epic Account link (EOS Account Linking)","Same","Same","Optional. Offered once at first online boot and any time from Options > Account. Never forced. See cross_save.csv.","SfOnline",CH),
 ("PF_03","Account","User switching","n/a","Return to title on profile change","Return to title on XUser change; support multiple signed-in users at title","Profile change mid-game saves if safe, then returns to title (STR_PLAT_USER_CHANGE).","SfPlatform","tech/04; CERT"),
 ("PF_04","Save","Platform save storage","Steam Cloud (see pc_storefront.csv)","PS5 save data, one slot per character + settings","Connected Storage, one container per character + settings","Character save under 2 MB (tech/03). Platform save is always written; cross-save copy is extra.","SfSave","tech/03"),
 ("PF_05","Save","Cross-save","Yes","Yes","Yes","Profile service copy, single active platform lock. See cross_save.csv.","SfSave","AUD-71; "+CH),
 ("PF_06","Presence","Rich presence","Steam Rich Presence tokens + steam_player_group","Activity-driven presence (UDS) plus joinable session","Xbox rich presence strings (Partner Center) + MPSD joinable session","See rich_presence.csv.","SfPlatform","AUD-72; "+CH),
 ("PF_07","Presence","Join from friends list","Steam 'Join Game' via connect string","Join via PSN session invite / Game Base","Join via Xbox Guide / activity","Only when the host's session is open to friends and the joiner is in band (coop_scaling).","SfOnline",CH),
 ("PF_08","Activities","PS5 Activity Cards","n/a","Yes, every activity in ps5_activities.csv","n/a","Each card deep-links to the nearest lit Anchor for the activity.","SfPlatform","AUD-72; "+CH),
 ("PF_09","Activities","PS5 Game Help","n/a","Yes, hints on main quests, Citadels and bosses","n/a","Hints are written by design; spoiler-tagged hints for bosses. Video hints captured from QA runs in Phase 7.","SfPlatform",CH),
 ("PF_10","Suspend","Suspend and resume","Steam Deck sleep","Rest mode","Constrained / suspend","See suspend_resume.csv.","SfPlatform","CERT; AUD-72"),
 ("PF_11","Suspend","Xbox Quick Resume","n/a","n/a","Yes for solo; online modes resume to safe state","See suspend_resume.csv.","SfPlatform","AUD-72"),
 ("PF_12","Achievements","Achievements / trophies","60 Steam achievements, progress via Steam Stats","59 trophies + Platinum","60 achievements, 1,000 Gamerscore","See achievements_platform.csv. Mods turn achievements off for that save (existing STR_FFE_ACH_OFF).","SfPlatform","UI strings STR_ACH_*; "+CH),
 ("PF_13","Achievements","Retroactive unlock","Yes","Yes","Yes","On load, any achievement the save already qualifies for unlocks (covers cross-save onto a new platform).","SfPlatform",CH),
 ("PF_14","Store","DLC and edition entitlements","Steam DLC app IDs","PS Store entitlement labels","Xbox Store durable add-ons","See entitlements.csv. Verified server-side by the Store service before grants (tech/02).","SfOnline","AUD-73; tech/02"),
 ("PF_15","Store","Cosmetics shop purchase","Steam microtransaction API (overlay)","PS Store consumable-free durable products via in-game commerce dialog","Xbox Store durable add-ons via in-game purchase UI","Direct real-money prices, local currency, no premium currency (Marlon's decision).","SfOnline","production/monetization.md"),
 ("PF_16","Install","Play while installing","No (Steam installs fully)","Yes, chunk 1 playable (install_chunks.csv)","Yes, Intelligent Delivery chunk 1 playable","Areas still downloading show STR_PLAT_INSTALL_WAIT at their boundary.","SfPlatform","AUD-74; "+CH),
 ("PF_17","Install","Optional language packs","Steam language DLC-style depots chosen by Steam language","Language chunks by system language; others optional","Intelligent Delivery language features","English VO always installed; 4 other VO languages optional.","SfPlatform","plan 7.4; "+CH),
 ("PF_18","Install","Smart Delivery / cross-gen","n/a","n/a","One purchase covers Series X and S packages; no Xbox One build","Series S package ships half-resolution textures (tech/04).","SfPlatform","tech/04"),
 ("PF_19","Input","Device glyphs","Xbox, PlayStation, Steam Deck, keyboard and mouse; Steam Input API glyphs when Steam Input is on","DualSense","Xbox controller","Glyph set follows the last device used. See input_glyphs.csv.","SfUI","AUD-75; tech/04"),
 ("PF_20","Input","Haptics and adaptive triggers","DualSense on PC over USB only","DualSense haptics + adaptive triggers","Impulse triggers","See dualsense_feedback.csv. Intensity slider 0-100% and off switch.","SfPlatform",CH),
 ("PF_21","Online","Online subscription","None","PlayStation Plus for co-op, invasions, strikes, raid, arena","Game Pass Core / Ultimate for the same","Solo, Shard-notes reading and cosmetics shop work without subscription; Shard-notes writing needs online only.","SfOnline","STR_PLAT_PSPLUS, STR_PLAT_XBL"),
 ("PF_22","Online","Cross-play","On by default, opt-out in Options","Same; follows PS5 cross-play setting where the platform requires","Same; obeys Xbox privacy setting for cross-network play","Owned by tech/02-online.md; listed here for cert.","SfOnline","tech/02"),
 ("PF_23","Online","Voice and text chat","EOS voice; Steam overlay chat","Platform party chat preferred; EOS voice in-game","Platform party chat preferred; EOS voice in-game","Obey platform communication and UGC privileges for child accounts.","SfOnline","tech/02; CERT"),
 ("PF_24","Online","Block and mute lists","Steam block list honored","PSN block list honored","Xbox block list honored","Blocked players never matched into the same co-op, strike or raid by matchmaking; arena may match but hides chat and names.","SfOnline",CH),
 ("PF_25","Online","UGC privilege","n/a","Shared maps hidden when UGC is restricted","Same","Forgeframe maps and Shard-notes text count as UGC.","SfOnline","CERT"),
 ("PF_26","Social","Screenshots and video capture","Steam screenshots; Steam Timeline markers","Share button capture; spoiler block on ending cinematics","Xbox capture","Ending cinematics and Act 3 reveal are capture-blocked on PS5 until 14 days after launch.","SfPlatform",CH),
 ("PF_27","Social","Photo mode","Yes","Yes","Yes","Photo mode saves go to platform capture gallery on console, Screenshots folder on PC.","SfUI","UI strings STR_PHOTO_*"),
 ("PF_28","Mods","Forgeframe mods","Curated hub + Steam Workshop mirror","Hub maps and challenge rooms only","Hub maps and challenge rooms only","Plan 3.12 and 9.3: PC launch +3 months, consoles +6 months.","SfMods","plan 3.12, 9.3"),
 ("PF_29","Accessibility","Platform accessibility settings","n/a","Read PS5 system settings: subtitles, text size, reduce motion where exposed","Read Xbox system settings: closed captions, high contrast hint","System settings seed the in-game defaults at first boot only.","SfUI","tech/04; XAG"),
 ("PF_30","Accessibility","Text to speech","Windows narrator API","PS5 screen reader API","Xbox narrator API","Menus only, as tech/04 says.","SfUI","tech/04"),
 ("PF_31","Parental","Parental controls and age","n/a (Steam Family View)","Honor PSN age and spending limits","Honor Xbox family settings","Shop hidden when spending is blocked; online features hidden when blocked.","SfOnline","CERT"),
 ("PF_32","Network","Network loss","Message + offline fallback","Same","Same","Existing STR_PLAT_NET_* strings. Solo continues offline (tech/02).","SfOnline","tech/02"),
 ("PF_33","Storage","Storage full","Message","Same","Same","Existing STR_PLAT_STORAGE_FULL / STR_ERR_STORAGE_B.","SfSave","UI strings"),
 ("PF_34","Video","Graphics modes","Full settings menu","Performance (default) and Quality","Performance (default) and Quality on X; single 30 fps mode on S","Owned by tech/perf_budgets.csv.","SfRender","tech/perf_budgets.csv"),
 ("PF_35","Video","HDR and VRR","HDR10, VRR via G-Sync/FreeSync","HDR10 calibrated with system HDR settings; VRR unlocked framerate option in Performance","HDR10 + Auto HDR off; VRR supported","120 Hz output in Performance mode when VRR is on (cap 60, unlocked up to 80 is a Shardfall choice).","SfRender",CH),
 ("PF_36","Launch","Launcher","None. Game boots straight to EAC bootstrap then splash","n/a","n/a","See pc_storefront.csv.","SfPlatform",CH),
 ("PF_37","Launch","Storefronts at launch","Steam only","PlayStation Store","Microsoft Store (console)","Epic Games Store and Microsoft Store on PC are reviewed again for the Expansion 1 window.","Production",CH),
]
w("platform_features.csv", ["feat_id","area","feature","pc_steam","ps5","xbox_series","rule","owner_module","source"], feat)

# ---------------------------------------------------------------- cross-save
cs = [
 # id, data, where it lives, crosses platforms, conflict rule, notes
 ("XS_01","Character saves (10 slots)","Platform save + Profile service copy","Yes","Newest by play time; prompt if both changed since last sync (tech/03)","Upload on every autosave when online, throttled to once per 2 min plus forced on quit/suspend."),
 ("XS_02","Backups (3 rotating per character)","Local only","No","n/a","Corruption recovery falls back to backup then cloud copy (tech/03)."),
 ("XS_03","Ember, items, quest state, reputation, world delta","Inside character save","Yes","Follows XS_01","Campaign Ember stays in the save (tech/02)."),
 ("XS_04","Seals and weekly caps","Economy service ledger","Yes","Server is the only source","Weekly reset Tuesday 17:00 UTC (Shardfall choice) is per account, not per platform."),
 ("XS_05","Cosmetics earned in play (Ember, Seals, season track)","Profile service","Yes","Union of both sides","Earned cosmetics follow the account everywhere."),
 ("XS_06","Cosmetics bought with real money","Platform entitlement + Profile mirror","Only where the platform allows","Union, filtered by platform policy","If a platform does not allow cross-platform use of purchases made elsewhere, the item shows as 'Owned on another platform' and stays hidden from loadouts there."),
 ("XS_07","Expansions and editions","Platform entitlement","No","n/a","A save that uses expansion content on a platform without it loads; expansion regions and items lock (STR_ERR_DLC_MISSING_*). Nothing is deleted."),
 ("XS_08","Gameplay and accessibility settings (subtitles, Assist, colorblind, camera, HUD)","Profile service","Yes","Newest write wins","Seeded from platform system settings only on the first boot of a new account."),
 ("XS_09","Graphics, audio device and display settings","Local only","No","n/a","Hardware differs per platform."),
 ("XS_10","Input bindings","Profile service, one set per device family","Per device family","Newest write wins","Gamepad layout syncs between PS5, Xbox and PC gamepad; keyboard layout PC only."),
 ("XS_11","Achievements and trophies","Platform","No","n/a","Retroactive unlock on load (PF_13)."),
 ("XS_12","Arena rating and season rank","Matchmaking service","Yes","Server only","One rating per account; input-pool split (tech/02) uses the same rating."),
 ("XS_13","Shard-notes, ratings and death echoes","Messages service","Yes","Server only","Visible across platforms when cross-play is on."),
 ("XS_14","Forgeframe maps and challenge rooms","Mod hub","Yes (console-safe ones)","Server only","Bookmarks and play counts sync."),
 ("XS_15","PC mods (non-console-safe)","Local","No","n/a","A save that loaded non-console-safe mods is marked modded and is never uploaded to the cross-save copy; a 'Make unmodded copy' option is not offered (records may be broken)."),
 ("XS_16","Photo mode captures","Local / platform gallery","No","n/a",""),
 ("XS_17","Telemetry consent and privacy choices","Profile service","Yes","Most restrictive wins","GDPR/CCPA rules from tech/02."),
]
w("cross_save.csv", ["xs_id","data","stored_in","cross_platform","conflict_rule","notes"], cs)

lock = [
 ("XL_01","Active platform lock","One platform at a time may hold the account's cross-save lock. Lease 5 minutes, renewed every 60 s while playing."),
 ("XL_02","Lock taken elsewhere","Boot shows STR_XS_LOCKED. Choices: Play here (takes the lock after the other side's next sync or lease end) or Play offline with the local save only (that local save will conflict later and prompts on the next sync)."),
 ("XL_03","Unlink","Unlinking keeps the newest copy on each platform. Relink allowed once per 30 days per platform (abuse limit)."),
 ("XL_04","Link prompt timing","First online boot after the tutorial ends (MQ_A1_01 start) and from Options > Account. Shown at most once unprompted."),
 ("XL_05","Link method","Epic Account via EOS Account Linking. Console shows a QR code and a 6-character code for the browser flow; PC opens the Steam overlay browser."),
 ("XL_06","Merge on first link","If both platforms already hold characters, slots merge up to 10. Overflow characters stay platform-local and are listed as 'Not synced' until a slot frees."),
 ("XL_07","Version gate","A cloud save written by a newer build than this platform's build shows STR_ERR_VERSION_* and is not overwritten."),
 ("XL_08","Bans","An account banned for save tampering (tech/02 signed saves) loses cross-save upload but keeps local play."),
]
w("cross_save_rules.csv", ["rule_id","rule","detail"], lock)
s("STR_XS_LINK_T","Account","Carry Your Progress")
s("STR_XS_LINK_B","Account","Link an Epic Games account to play the same characters on PC, PlayStation 5 and Xbox Series X|S.")
s("STR_XS_LINK_CODE","Account","Go to {VAR_url} and enter code {VAR_code}.")
s("STR_XS_LINK_DONE","Account","Linked. Your characters now sync across systems.")
s("STR_XS_LINK_LATER","Account","Not Now")
s("STR_XS_UNLINK_B","Account","Unlink this account? Each system keeps its newest copy. You can relink once every 30 days.")
s("STR_XS_LOCKED","Account","You are playing Shardfall on another system. Continue here?")
s("STR_XS_PLAY_HERE","Account","Play Here")
s("STR_XS_PLAY_OFFLINE","Account","Play Offline")
s("STR_XS_CONFLICT_T","Account","Two Saves Found")
s("STR_XS_CONFLICT_B","Account","{VAR_char_name} has newer progress in two places. Keep this system's save ({VAR_time_local}) or the cloud save ({VAR_time_cloud})?")
s("STR_XS_KEEP_LOCAL","Account","Keep This System")
s("STR_XS_KEEP_CLOUD","Account","Keep Cloud")
s("STR_XS_SYNCING","Account","Syncing characters...")
s("STR_XS_NOT_SYNCED","Account","Not synced")
s("STR_XS_MODDED","Account","Modded saves do not sync to other systems.")
s("STR_XS_OWNED_ELSEWHERE","Account","Owned on another platform")
s("STR_XS_SLOTS_FULL","Account","All 10 character slots are full. {VAR_count} characters stay on this system only.")

# ---------------------------------------------------------------- rich presence
rp = [
 # id, trigger, en text, steam_group, joinable, ps5 activity
 ("RP_TITLE","Title or main menu","In the main menu","", "No",""),
 ("RP_CREATE","Character creation","Waking from cryo","", "No","ACTV_MQ_P_01"),
 ("RP_EXPLORE","Open world, no quest focus","Exploring {REGION_name}","party","Yes",""),
 ("RP_QUEST","Main quest step active","{VAR_quest}, {REGION_name}","party","Yes","ACTV_<main quest>"),
 ("RP_CITADEL","Inside a Citadel","Storming {LOC_name} in {REGION_name}","party","Yes","ACTV_CIT_<region>"),
 ("RP_BOSS","Boss health bar visible","Fighting {ACT_name}","party","No","ACTV_<owning activity>"),
 ("RP_HUB","In Lantern Hold","In Lantern Hold","party","Yes",""),
 ("RP_UNDERVAULT","In the Undervault","Below the world","party","Yes","ACTV_MQ_A2_06"),
 ("RP_QUIET","In the Quiet (Act 3)","Aboard the Quiet","party","Yes","ACTV_<A3 quest>"),
 ("RP_COOP_HOST","Hosting co-op","Leading a party of {VAR_n}/4 in {REGION_name}","party","Yes",""),
 ("RP_COOP_GUEST","Guest in co-op","Helping a friend in {REGION_name}","party","No",""),
 ("RP_INVADE","Invading","Invading another world","","No",""),
 ("RP_STRIKE","In a Strike","Strike: {VAR_strike}","fireteam","No","ACTV_STK_<n>"),
 ("RP_CITADEL_H","Hollowed Citadel","Hollowed Citadel: {LOC_name}","fireteam","No","ACTV_HCIT_<region>"),
 ("RP_RAID","In the raid","Raid: The Quiet, encounter {VAR_n}/4","fireteam","No","ACTV_RAID_<n>"),
 ("RP_ARENA","In an arena match","Arena {MODE}: {SCORE_A} to {SCORE_B}","fireteam","No","ACTV_ARENA"),
 ("RP_ARENA_Q","Matchmaking queue","Waiting for a match","fireteam","No",""),
 ("RP_FORGE","Forgeframe editor","Building in Forgeframe","","No",""),
 ("RP_FORGE_PLAY","Playing a shared map","Playing {VAR_map}","party","Yes",""),
 ("RP_PHOTO","Photo mode","Taking photos in {REGION_name}","","No",""),
 ("RP_ENDING","Credits","Watching the credits","","No",""),
 ("RP_NGPLUS","NG+ cycle 1-7 exploring","Exploring {REGION_name} (NG+{VAR_n})","party","Yes",""),
]
rows = []
for rid, trig, en, grp, join, act in rp:
    sid = s(f"STR_{rid}", "Rich presence", en, "rich presence; tokens filled by platform layer")
    steam = "#" + "".join(p.capitalize() for p in rid[3:].split("_"))
    rows.append([rid, trig, en, sid, steam, grp, f"XRP_{rid[3:]}", act or "none (presence follows last activity)", join, "Updated on state change, at most once per 10 s"])
w("rich_presence.csv", ["rp_id","trigger","text_en","str_id","steam_token","steam_player_group","xbox_presence_id","ps5_activity","joinable","update_rule"], rows)

# ---------------------------------------------------------------- PS5 activities
mq = [("A1",8,"Act 1"),("A2",9,"Act 2"),("A3",6,"Act 3")]
acts = []
acts.append(["ACTV_MQ_P_01","Progress","The Cryo Wreck (prologue)","MQ_P_01","REG_01",25,"No",3,"Tutorial complete","Prologue start"])
for a, n, lab in mq:
    for i in range(1, n+1):
        q = f"MQ_{a}_{i:02d}"
        mins = 60 if a != "A3" else 75
        acts.append([f"ACTV_{q}","Progress",f"{lab} main quest {i} (name from campaign/03-main-story.md)",q,
                     "REG_Q" if a == "A3" else ("REG_U" if q == "MQ_A2_06" else "varies"),mins,"No",4,"Quest complete",f"Nearest lit Anchor to step 1 of {q}"])
for rid, rn in REG:
    acts.append([f"ACTV_CIT_{rid}","Progress",f"{rn} Citadel","Citadel path",rid,150,"No",6,"Citadel boss defeated","Citadel entrance Anchor"])
    acts.append([f"ACTV_RELAY_{rid}","Task list",f"{rn} Relay Towers","Relay Towers",rid,40,"No",2,"All towers in region climbed","Nearest unclimbed tower"])
    acts.append([f"ACTV_FIELD_{rid}","Task list",f"{rn} field bosses","2 field bosses",rid,30,"No",2,"Both field bosses defeated","Nearest Anchor to the next living field boss"])
for f, fn in [("HK","Hull Knights"),("LC","Lantern Church"),("SG","Salvagers' Guild"),("QH","Quiet Hand"),("CH","The Choir")]:
    acts.append([f"ACTV_FAC_{f}","Task list",f"{fn} questline",f"QST_{f}_*","REG_HUB",600,"No",2,"Faction finale complete","Faction hall in Lantern Hold"])
for i in range(1, 9):
    acts.append([f"ACTV_CMP_C{i}","Task list",f"Companion {i} questline",f"ACT_CMP_C{i} line","varies",300,"No",2,"Companion questline complete","Companion's current location"])
for i in range(1, 7):
    acts.append([f"ACTV_STK_{i:02d}","Open-ended",f"Strike {i} (STK_{i:02d})",f"STK_{i:02d}",REG[i-1][0],25,"Yes",1,"Strike complete (repeatable)","Strike launch in Lantern Hold"])
    acts.append([f"ACTV_HCIT_{REG[i-1][0]}","Open-ended",f"Hollowed Citadel: {REG[i-1][1]}","EG_CITADEL",REG[i-1][0],45,"Yes",1,"Run complete (repeatable)","Citadel entrance Anchor"])
for i in range(1, 5):
    acts.append([f"ACTV_RAID_{i}","Progress",f"Raid: The Quiet, encounter {i}","EG_RAID","REG_Q",50,"Yes",2 if i < 4 else 3,"Encounter cleared","Raid gate in Lantern Hold"])
acts.append(["ACTV_ARENA","Open-ended","Arena 3v3","EG_ARENA","REG_HUB",10,"Yes",0,"Match ended","Arena queue"])
acts.append(["ACTV_UNDERVAULT","Task list","The Undervault: every Choir vault","REG_U sites","REG_U",180,"No",2,"All Undervault sites cleared","Undervault entrance Anchor"])
for r in acts:
    r.append("Hidden until unlocked" if r[0].startswith(("ACTV_MQ_A3","ACTV_MQ_A2_06","ACTV_MQ_A2_07","ACTV_MQ_A2_08","ACTV_MQ_A2_09")) else "Visible")
w("ps5_activities.csv", ["activity_id","type","name","links_to","region","est_minutes","online_required","game_help_hints","complete_event","launch_destination","visibility"], acts)
print("  activities:", len(acts))

# ---------------------------------------------------------------- suspend, resume, Quick Resume
sr = [
 ("SR_01","Solo campaign, out of combat","Write suspend snapshot of current state (not a new autosave slot); pause audio and timers","Continue exactly where left","Quick Resume restores memory image; backend reconnects silently","Game-time clocks (vendor restock, respawn) do not advance while suspended"),
 ("SR_02","Solo campaign, in combat or boss","Pause; no save written","Continue exactly where left (paused menu shown)","Same, opens on the pause menu","Never save mid-combat (tech/03)"),
 ("SR_03","Save write in progress","Finish write before suspend acknowledges (budget 1.5 s); atomic rename (tech/03)","n/a","n/a","Save icon rule (CERT)"),
 ("SR_04","Co-op host","Session ends for guests after 30 s of no heartbeat; guests return to own world at last Anchor with loot kept","If back within 30 s: party continues. Later: solo, party gone, STR_SR_PARTY_ENDED","Resume solo","Host progress already saved at last checkpoint"),
 ("SR_05","Co-op guest","Guest leaves session after 30 s","Back within 30 s: rejoin. Later: own world at last Anchor, loot and XP kept","Same","Plan: guests keep loot and XP"),
 ("SR_06","Strike","Player counted as disconnected","Rejoin window 3 min, same checkpoint","After window: own world in Lantern Hold, no Seals lost","Matches the plan's 3-player strike rule (no penalty)"),
 ("SR_07","Raid (dedicated server)","Player disconnected; fireteam continues","Rejoin window 5 min to the same instance","Lantern Hold; checkpoint kept on the account","Dedicated servers mean host loss cannot end a run (tech/02)"),
 ("SR_08","Arena match","Player disconnected; bot does not replace","Rejoin within 60 s","Match counted as left. First leave per day has no rating penalty; later ones follow matchmaking rules","Shardfall choice"),
 ("SR_09","Invasion (as invader)","Invasion ends; no penalty to either side","Own world at last Anchor","Same",""),
 ("SR_10","Cutscene playing","Pause cutscene","Resume from pause","Cutscene restarts from its last shot boundary",""),
 ("SR_11","Shop or store overlay open","Cancel pending purchase UI; backend transaction stays idempotent","Store reopens to item page; no double charge","Same","tech/02 idempotent transaction IDs"),
 ("SR_12","Resume after more than 24 hours","n/a","Re-validate entitlements and sign-in; refresh live config and weekly rotation","Same","Weekly reset may have passed"),
 ("SR_13","Signed-in user changed while suspended","n/a","Return to title (STR_PLAT_USER_CHANGE)","Same","CERT user switching"),
 ("SR_14","Network lost while suspended","n/a","Online modes end as above; solo continues offline (STR_PLAT_NET_OFFLINE)","Same","tech/02 offline rule"),
 ("SR_15","Quick Resume across a patch","n/a","n/a","Xbox discards the memory image after updates; normal boot","Platform behaviour"),
]
w("suspend_resume.csv", ["sr_id","state_on_suspend","on_suspend","on_resume","xbox_quick_resume","notes"], sr)
s("STR_SR_PARTY_ENDED","Platform overlays","Your party ended while the game was suspended.")
s("STR_SR_REJOIN","Platform overlays","Rejoining your fireteam...")
s("STR_SR_REJOIN_FAIL","Platform overlays","The activity ended. You are back in Lantern Hold. Nothing was lost.")

# ---------------------------------------------------------------- achievements
strs = {r["str_id"]: r["text_en"] for r in csv.DictReader(open(os.path.join(GP, "data/ui/strings.csv")))}
# 59 trophies + Platinum sized to 1,230 points (Bronze 15, Silver 30, Gold 90, Platinum 180): 1 Gold, 6 Silver, 52 Bronze.
# Check the points table and allowed range against current TRC in Phase 7.
gold = {12}
silver = {8,9,10,24,35,51}
hidden = {8,9,10,13,14,58}
online = {46,47,48,49,50,51,52,53,54,57}
gp = {"Bronze":15,"Silver":30,"Gold":90}
xw = {"Bronze":15,"Silver":20,"Gold":50,"Platinum":50}  # Xbox has no platinum; ACH_60 is a normal 50 G achievement. Sums to 1,000.
ach = [(i, "Platinum" if i == 60 else "Gold" if i in gold else "Silver" if i in silver else "Bronze") for i in range(1, 61)]
rows = [[i, g, xw[g]] for i, g in ach]
out = []
for i, g, gs in rows:
    k = f"STR_ACH_{i:02d}"
    out.append([f"ACH_{i:02d}", k, strs.get(k, ""), strs.get(k + "_DESC", ""), g, 180 if g == "Platinum" else gp[g], gs,
                f"ACH_{i:02d}", "Yes" if i in hidden else "No", "Yes" if i in online else "No",
                "Steam stat progress" if strs.get(k + "_DESC", "")[:1].isalpha() and any(ch.isdigit() for ch in strs.get(k + "_DESC", "")) else "",
                "Base game"])
w("achievements_platform.csv", ["ach_id","str_id","name_en","desc_en","ps5_grade","ps5_points","xbox_gamerscore","steam_api_name","hidden","online_required","progress","list"], out)
ps = sum(r[5] for r in out)
print(f"  PS5 points incl. platinum: {ps}; Xbox Gamerscore: {sum(r[6] for r in out)}")
exp = [["ACH_X1_01..10","Expansion 1","10 achievements, 250 Gamerscore on Xbox; PS5 add-on trophy group (no platinum); Steam adds to the same list","Set when the expansion is designed (Phase 9)"],
       ["ACH_X2_01..10","Expansion 2","Same budget","Same"],
       ["Seasons","Free seasons","No new achievements; season content uses in-game titles","Keeps the list completable forever (no content removal, plan 9.1)"]]
w("achievements_future.csv", ["ids","list","budget","notes"], exp)

# ---------------------------------------------------------------- entitlements and editions
# Editions, prices and contents are owned by design/liveops/ (retail_editions.csv, store_catalog.csv). This table only maps them to platform entitlements.
ent = [
 # id, liveops edition, name, type, price, grants, store products, offline, coop, notes
 ("ENT_BASE","ED_STD","Standard Edition","Base game",69.99,"Full game, all free seasons, Forgeframe","Steam app; PS5 product; Xbox product (Smart Delivery X|S); disc SKUs carry the same license","Platform license check only","n/a","Disc installs the 1.0 game; day-one patch downloads (liveops retail_skus.csv)"),
 ("ENT_ED_DLX","ED_DLX","Deluxe Edition","Edition bundle",99.99,"ENT_BASE + ENT_EXP_PASS + ENT_PACK_DLX + ENT_DIG_ARTBOOK + ENT_DIG_OST","Bundle of the listed products on every store (digital only)","Cached grant works offline","n/a","No early access in any edition (liveops)"),
 ("ENT_ED_CE","ED_CE","Collector's Edition","Edition bundle",249.99,"Same digital grants as ENT_ED_DLX","Disc + in-box code for the Deluxe digital bundle; PC is a code in the box","Cached grant works offline","n/a","Physical extras are liveops' list; the code redeems ENT_ED_DLX contents on the box's platform"),
 ("ENT_EXP_PASS","ED_PASS","Expansion Pass","Add-on bundle",49.99,"ENT_EXP_01 + ENT_EXP_02 when each releases","Season-pass style bundle per store","Expansion content unlocks on release day from the platform entitlement","Guest rule as ENT_EXP_01","On sale from launch to EXP_2 release (liveops)"),
 ("ENT_EXP_01","ED_EXP1","Expansion: The Sunken Fore","Expansion",29.99,"EXP_1: new region, raid, enemy faction, faction questline (plan 9.2)","DLC app / add-on per store","Playable offline except its raid","Guests without it may join a host in the expansion region; their drops roll from REG_END tables instead of expansion tables and they cannot start expansion quests","Release 2032-04-13 (liveops expansions.csv)"),
 ("ENT_EXP_02","ED_EXP2","Expansion: The Burning Crown","Expansion",29.99,"EXP_2, same structure","Same","Same","Same","Release 2033-04-12"),
 ("ENT_ED_COMPLETE","ED_COMPLETE","Complete Edition","Edition bundle",79.99,"ENT_BASE + ENT_EXP_01 + ENT_EXP_02 + ENT_PACK_DLX","New store product; disc version carries expansion codes","Cached grant works offline","n/a","Year 2 relaunch 2033-04-12. Existing owners are not double-charged: stores show the upgrade price where they support it"),
 ("ENT_PACK_DLX","-","Meridian Officer set","Cosmetic pack",None,"ITM_COS_DLX_01..07","Durable add-on inside the Deluxe, Collector's and Complete bundles","Works offline","Visible to all players","Each item sold separately in the shop from launch + 12 months (liveops store_catalog.csv)"),
 ("ENT_DIG_ARTBOOK","-","Digital Artbook","Digital extra",None,"Extras menu artbook viewer (120 pages)","Steam: separate DLC with PDF; consoles: in-game viewer","Works offline","n/a","Deluxe and Collector's"),
 ("ENT_DIG_OST","-","Digital Soundtrack","Digital extra",None,"Extras menu jukebox (40 tracks); Steam soundtrack DLC (FLAC + MP3)","Steam soundtrack app; consoles in-game jukebox","Works offline","n/a","Deluxe and Collector's"),
 ("ENT_PREORDER","-","Pre-order bonus","Bonus",0,"ITM_COS_PRE_01 First Light Strider Skin, ITM_COS_PRE_02 Kindled Greeting","Pre-order entitlement per store","Works offline","Visible to all","Earnable in game from 6 months after launch (liveops), so nothing is exclusive forever"),
 ("ENT_COS_SHOP","-","Cosmetics shop items","Durable add-ons","1.99-9.99 per item; bundles up to 19.99","One entitlement per shop item in liveops store_catalog.csv / data/items/cosmetics.csv","Steam microtransaction item; PS Store and Xbox Store durables","Owned items work offline; buying needs online","Visible to all","No consumables, no currency, no random items. Price rule: single items $1.99 to $9.99; season bundles up to $19.99 (hard cap) and always cheaper than the items bought separately (liveops price_tiers.csv)"),
 ("ENT_FORGE","-","Forgeframe","Free tool",0,"Editor and sandbox","Included in base","Editor works offline; publishing needs online","n/a","Plan 9.3"),
 ("ENT_PLAT_SUB","-","Platform online subscription","Platform rule",None,"PS Plus / Game Pass Core for online multiplayer on console","Platform","n/a","Required for co-op, strikes, raid, arena, invasions on console","Not sold by Shardfall"),
]
w("entitlements.csv", ["ent_id","liveops_edition","name","type","price_usd","grants","store_products","offline_rule","coop_rule","notes"], ent)
er = [
 ("ER_01","Check order","Boot reads platform entitlements, then the Store service verifies receipts server-side (tech/02) and writes grants to the Profile service."),
 ("ER_02","Offline cache","Last verified entitlement list is cached signed in the settings save for 30 days; after that, paid cosmetics still show but expansion regions need one online check."),
 ("ER_03","Missing content in a save","Load anyway; lock content and show STR_ERR_DLC_MISSING_*. Equipped locked items swap to the last unlocked loadout."),
 ("ER_04","Refund or revoke","Platform revoke removes the grant at next check. Earned progress inside an expansion region stays in the save but locks."),
 ("ER_05","Purchase grant timing","Grant appears without restart within 10 s of the platform purchase callback; STR_ENT_GRANTED toast."),
 ("ER_06","Expansion release","Content ships in a free patch before release day (so co-op guests have the data) and unlocks by entitlement at 15:00 UTC on release day."),
 ("ER_07","Family and sharing","Steam Families, PS5 primary console and Xbox home console sharing follow platform rules; no extra block."),
 ("ER_08","Gifting","Platform gifting only. No in-game gifting at launch (tech/02 has no trading)."),
 ("ER_09","Price display","Prices come from each store's localized price tiers; the game never shows a hard-coded price."),
 ("ER_10","Store page honesty","Every edition and pack page lists contents with images. No 'mystery' or randomized bundles."),
]
w("entitlement_rules.csv", ["rule_id","rule","detail"], er)
s("STR_ENT_GRANTED","Store","{VAR_item} is ready to use.")
s("STR_ENT_OWNED","Store","Owned")
s("STR_ENT_PENDING","Store","Purchase pending. It will appear when your store confirms it.")
s("STR_ENT_CHECK_ONLINE","Store","Connect online once to unlock {VAR_dlc}.")
s("STR_ENT_GUEST_REGION","Store","You are a guest in {VAR_dlc}. Rewards here come from endgame tables until you own it.")
s("STR_ENT_BUY","Store","Buy {VAR_item} ({VAR_price})")
s("STR_ENT_PURCHASE_FAIL","Store","The purchase did not finish. You were not charged.")
s("STR_EXTRAS_ARTBOOK","Extras","Artbook")
s("STR_EXTRAS_OST","Extras","Soundtrack")

# ---------------------------------------------------------------- install and patch budgets
inst = [
 # platform, total_gb, required_free_gb, base_content, vo_en, vo_optional_each, text_all, shader_cache, notes
 ("PC (Steam)",140,150,"128 (pak, Oodle compressed)",3.5,3.5,0.3,"6 GB at first launch (PSO cache build)","Matches tech/04 150 GB SSD requirement"),
 ("PS5",115,"Platform managed","104",3.5,3.5,0.3,"Precompiled","Kraken hardware decompression"),
 ("Xbox Series X",120,"Platform managed","109",3.5,3.5,0.3,"Precompiled","BCPack textures"),
 ("Xbox Series S",92,"Platform managed","81 (half-res textures, tech/04)",3.5,3.5,0.3,"Precompiled","Separate Smart Delivery package"),
 ("Steam Deck (stretch)",140,150,"Same as PC",3.5,3.5,0.3,"Shader pre-caching via Steam","Same depot as PC"),
]
w("install_budgets.csv", ["platform","install_gb_launch","required_free_gb","base_content_gb","vo_english_gb","vo_optional_language_gb","text_all_languages_gb","shader_cache","notes"], inst)
chunks = [
 ("CHK_00","Boot, engine, UI, shared core (characters, weapons, enemies, audio banks)",22,"Yes","1"),
 ("CHK_01","Prologue (cryo wreck) + Cinderreach (REG_01) + Lantern Hold (REG_HUB) + English VO for these",16,"Yes (first playable with CHK_00)","1"),
 ("CHK_02","Saltmere (REG_02)",11,"No","2"),
 ("CHK_03","Thornwood (REG_03)",11,"No","3"),
 ("CHK_04","Glasswaste (REG_04)",11,"No","3"),
 ("CHK_05","Rimefall (REG_05)",11,"No","3"),
 ("CHK_06","Hollowdeep (REG_06)",11,"No","3"),
 ("CHK_07","The Undervault (REG_U)",6,"No","4"),
 ("CHK_08","The Quiet (REG_Q), endings",8,"No","4"),
 ("CHK_09","Endgame: strikes, raid, arena maps",6,"No","4"),
 ("CHK_10","Cinematics (in-engine, data only) + remaining English VO",3,"No","4"),
 ("CHK_L_FR/DE/ES/JA","Optional VO language, one chunk each",3.5,"No","Optional"),
]
w("install_chunks.csv", ["chunk_id","contents","size_gb_ps5","initial_playable","download_order"], chunks)
pb = [
 # release, max download PS5/Xbox, max PC, rules
 ("Day-one patch",15,15,"Ready at certification (plan 8.2). Touches only changed paks."),
 ("Hotfix",1,1,"Code and small data only. Most tuning goes through live config with no patch (tech/02)."),
 ("Patch 1.01 (2 weeks)",5,5,"Plan 8.3"),
 ("Patch 1.1 (6 weeks)",8,8,"Plan 8.3"),
 ("Free season update (every 3 months)",12,12,"New strike, Hollowed Citadel variant, Shardborn items, PvP map (plan 9.1)"),
 ("Expansion data patch",30,30,"Shipped to everyone before release day so co-op guests can join (ER_06)"),
 ("Forgeframe console release (+6 months)",4,0,"Plan 9.3"),
]
w("patch_budgets.csv", ["release","max_download_gb_console","max_download_gb_pc","notes"], pb)
pr = [
 ("PR_01","Pak layout","One pak set per region, per mode (strike, raid, arena) and per language, so a change in one region does not re-download others."),
 ("PR_02","Delta ratio","Download size must stay under 1.5x the size of changed content. Build CI fails a patch above that (release engineer reviews)."),
 ("PR_03","Install growth","Total install may grow at most 25 GB a year from seasons; each expansion may add 30 GB. No content removal (plan 9.1), so budget comes from compression and deduplication."),
 ("PR_04","Free space during patch","PC patch staging needs at most 1.2x the patch size free. Steam depot chunking at 1 MB; files aligned to avoid shifts."),
 ("PR_05","Optional content","HD texture pack is not offered; Series S and PC Low use the base textures with mip streaming."),
 ("PR_06","Uninstall parts","Consoles allow removing optional VO languages and, after the campaign, the prologue chunk is kept (needed for NG+)."),
 ("PR_07","Version compatibility","Co-op, strikes and raids require matching build; the matchmaker gates by build hash. Live config can block old builds after a 72 h grace."),
]
w("patch_rules.csv", ["rule_id","rule","detail"], pr)
s("STR_PLAT_INSTALL_WAIT","Platform overlays","This area is still installing ({VAR_pct}%). Explore elsewhere and come back soon.")
s("STR_PLAT_INSTALL_DONE","Platform overlays","Shardfall has finished installing.")
s("STR_PLAT_UPDATE_REQ","Platform overlays","An update is required to play online.")

# ---------------------------------------------------------------- PC storefront
pc = [
 ("PC_01","Steam Cloud","On. Synced: character autosaves and manual saves, settings save. Not synced: local backups, shader cache, logs. Quota 64 MB, 200 files.","Cross-save copy in the Profile service still applies (cross_save.csv)."),
 ("PC_02","Steam Workshop","Mirror only. The curated Forgeframe hub (plan 3.12) is the source of truth and review queue; approved PC mods are published to Workshop by the hub so Steam users can subscribe. Subscribing in Steam installs through the hub's loader.","One review queue for all platforms; console-safe items also show on PS5 and Xbox through the hub."),
 ("PC_03","Steam Input","Full action manifest with action sets: OnFoot, Aiming, Mounted, Vehicle, Menu, PhotoMode, Forgeframe. BTN_ tokens map to actions. Glyphs from Steam Input API when Steam Input is on.","Lets players remap any controller in Steam."),
 ("PC_04","Steam Deck","Stretch target Verified (tech/04). Deck preset: 1280x800 native, 30 fps cap, TSR, Low plus medium textures. Minimum text 14 px at 1280x800 (Shardfall choice). Deck glyphs, on-screen keyboard for text fields, no launcher, suspend-safe.","Steam Deck row in tech/perf_budgets.csv."),
 ("PC_05","Steam Achievements and Stats","60 achievements; Stats drive progress bars for counted ones (achievements_platform.csv).",""),
 ("PC_06","Steam Rich Presence","Tokens and steam_player_group per rich_presence.csv; 'Join Game' passes connect string to co-op beacon.",""),
 ("PC_07","Steam Timeline","Markers: boss defeated, death, Shardborn found, achievement, ending reached, raid encounter cleared. Game phase per activity.","Free clip markers for players."),
 ("PC_08","Steam overlay purchases","Cosmetics bought through ISteamMicroTxn with overlay checkout; Store service verifies (tech/02).",""),
 ("PC_09","Trading Cards","Yes, once Steam makes the game eligible. Card art from concept paintings.",""),
 ("PC_10","Remote Play Together","Off. Shardfall has no local split-screen.",""),
 ("PC_11","Steam Families","Allowed (platform default).",""),
 ("PC_12","DRM","Steamworks ownership check only; no third-party DRM. Easy Anti-Cheat for online modes (tech/02).","Shardfall choice"),
 ("PC_13","Launcher policy","No launcher. Exe starts the EAC bootstrapper, then splash, then the first-launch shader cache pass with a progress bar (tech/04), then title. No forced account creation.",""),
 ("PC_14","Storefronts","Steam at launch. Epic Games Store and Microsoft Store PC reviewed for the Expansion 1 window.","Shardfall choice"),
 ("PC_15","Store page","Live at reveal, month 36 (production/marketing_launch.md). Lists AI use disclosure as Steam requires (production/legal_eula_privacy.md).",""),
 ("PC_16","Controller support tag","Full Controller Support. PlayStation and Xbox controllers natively, others through Steam Input.",""),
 ("PC_17","Ultrawide and high refresh","21:9 and 32:9 gameplay, UI safe area at 16:9; cutscenes letterbox to 21:9; frame cap options 30/60/90/120/144/unlocked.",""),
 ("PC_18","Mod and achievement rule","Existing rule: mods turn achievements off for that save (STR_FFE_ACH_OFF). Console-safe Forgeframe maps keep achievements on.",""),
]
w("pc_storefront.csv", ["pc_id","feature","decision","notes"], pc)

# ---------------------------------------------------------------- input glyphs
gl = [
 # physical, xbox, ps, deck, kbm default
 ("FACE_DOWN","A","Cross","A"),("FACE_RIGHT","B","Circle","B"),("FACE_LEFT","X","Square","X"),("FACE_UP","Y","Triangle","Y"),
 ("SHOULDER_L","LB","L1","L1"),("SHOULDER_R","RB","R1","R1"),("TRIGGER_L","LT","L2","L2"),("TRIGGER_R","RT","R2","R2"),
 ("STICK_L","Left stick","Left stick","Left stick"),("STICK_R","Right stick","Right stick","Right stick"),
 ("STICK_L_CLICK","LS","L3","L3"),("STICK_R_CLICK","RS","R3","R3"),
 ("DPAD_UP","D-pad up","D-pad up","D-pad up"),("DPAD_DOWN","D-pad down","D-pad down","D-pad down"),
 ("DPAD_LEFT","D-pad left","D-pad left","D-pad left"),("DPAD_RIGHT","D-pad right","D-pad right","D-pad right"),
 ("MENU","Menu","Options","Menu (≡)"),("VIEW","View","Touchpad press","View (⧉)"),
 ("BACK_L4","n/a","n/a (Edge: back left)","L4"),("BACK_R4","n/a","n/a (Edge: back right)","R4"),
 ("BACK_L5","n/a","n/a","L5"),("BACK_R5","n/a","n/a","R5"),("TRACKPAD_R","n/a","Touchpad swipe","Right trackpad"),
]
rows = []
for p, x, ps, d in gl:
    rows.append([p, x, f"UI_GLYPH_XB_{p}", ps, f"UI_GLYPH_PS_{p}", d, f"UI_GLYPH_DECK_{p}"])
w("input_glyphs.csv", ["physical_input","xbox_label","xbox_asset","ps_label","ps_asset","deck_label","deck_asset"], rows)
grules = [
 ("GR_01","Switching","Glyph set follows the last device with input above the dead zone; switch waits 0.25 s to stop flicker when both are touched."),
 ("GR_02","Steam Input","If Steam Input is on, glyphs come from the Steam Input API per action, not from this table."),
 ("GR_03","Deck detection","On Steam Deck, Deck glyphs are default even with keyboard input until a mouse moves."),
 ("GR_04","Keyboard","KBM glyphs show the bound key cap (UI_GLYPH_KEY_<key>), drawn from one key-cap template plus text."),
 ("GR_05","Remap","Glyphs always show the player's current binding, including in tutorials and popups (BTN_ tokens)."),
 ("GR_06","Style","Glyph art: monochrome on dark plate, 64 px source, 3 states (normal, held, disabled). Platform glyph shapes follow each holder's guidelines; PS face buttons keep their shapes."),
 ("GR_07","Bindings","Default action bindings belong to the controls folder; this table only maps physical inputs to glyph art."),
]
w("input_glyph_rules.csv", ["rule_id","rule","detail"], grules)

# ---------------------------------------------------------------- DualSense and impulse triggers
fc = [("ITM_CLS_PST","Pistol","Weapon",3,7,4,"Short click per shot"),("ITM_CLS_ARF","Auto Rifle","Vibration",3,9,3,"Fast buzz at fire rate"),
      ("ITM_CLS_SCT","Scout Rifle","Weapon",4,8,5,"Firm break per shot"),("ITM_CLS_SMG","Submachine Gun","Vibration",2,9,2,"Light fast buzz"),
      ("ITM_CLS_SHG","Shotgun","Weapon",5,8,8,"Heavy break plus pump click on reload"),("ITM_CLS_SNP","Sniper Rifle","Weapon",6,9,7,"Two-stage: half pull steadies, full pull fires"),
      ("ITM_CLS_LCH","Launcher","Feedback",3,9,6,"Constant resistance, release thump"),("ITM_CLS_LNC","Shard Lance","Feedback",2,9,1,"Resistance rises with charge (1 to 8)")]
rows = []
for cid, n, mode, a, b, st, note in fc:
    rows.append([f"HAP_{cid[8:]}", n, cid, "R2", mode, a, b, st, note, "RT impulse at 40% on fire", "Shardfall choice"])
ev = [("HAP_AIM","Aim down sights","L2","Feedback",1,9,2,"Light resistance while aiming","None"),
      ("HAP_BLOCK","Shield block held","L1/L2 block","Feedback",0,9,3,"Resistance rises to 6 when Breath under 25%","LT impulse on block hit"),
      ("HAP_BREATH_OUT","Breath empty","Both","Off","","","","Triggers go slack (feedback off) for 1 s","None"),
      ("HAP_WARD_BREAK","Ward broken","Haptics","n/a","","","","Sharp glass-crack haptic clip, 0.3 s","Both motors 0.3 s"),
      ("HAP_LOW_HP","Health under 25%","Haptics","n/a","","","","Heartbeat pulse every 0.9 s","Low motor pulse"),
      ("HAP_PARRY","Successful parry","Haptics","n/a","","","","Short high-frequency ping","Short high motor"),
      ("HAP_STRIDER","Strider gallop","Haptics","n/a","","","","Footfall pulses at gait rate; glide is a soft wind texture","Low motor per footfall"),
      ("HAP_HEAVY_HIT","Heavy melee hit lands","Haptics","n/a","","","","Weighted thud scaled by weapon weight","Both motors scaled"),
      ("HAP_CHARGE","Charged heavy attack","R2","Feedback",2,9,4,"Resistance builds while charging","None"),
      ("HAP_SURGE","Surge (super) cast","Haptics","n/a","","","","Rising swell 0.8 s by element","Both motors swell")]
for hid, n, t, mode, a, b, st, note, xb in ev:
    rows.append([hid, n, "", t, mode, a, b, st, note, xb, "Shardfall choice"])
w("dualsense_feedback.csv", ["hap_id","event","item_class","trigger","trigger_mode","start_pos_0_9","end_pos_0_9","strength_0_8","haptic_note","xbox_impulse","source"], rows)
s("STR_OPT_HAPTICS","Options","Haptic Intensity")
s("STR_OPT_TRIGGERS","Options","Trigger Effects")
s("STR_OPT_TRIGGERS_D","Options","Resistance in the triggers for weapons, blocking and aiming.")
s("STR_OPT_ACCOUNT","Options","Account and Cross-Save")
s("STR_OPT_CROSSSAVE","Options","Cross-Save")

# ---------------------------------------------------------------- strings + data requests
w("platform_strings.csv", ["str_id","screen","text_en","max_chars","tokens","notes"], STRINGS)
dr = [
 ("DR-PLT-001","Append platform_strings.csv rows","ui/strings.csv",f"{len(STRINGS)} new STR_ rows (screens Account, Store, Rich presence, Platform overlays, Options, Extras). Same columns as strings.csv."),
 ("DR-PLT-002","New popups for cross-save conflict, cross-save lock, link prompt, entitlement granted, install wait","ui/popups.csv","CNF_XS_CONFLICT (STR_XS_CONFLICT_T/B, buttons KEEP_LOCAL/KEEP_CLOUD), CNF_XS_LOCKED, PRM_XS_LINK, NTF_ENT_GRANTED (toast, 5 s), INL_INSTALL_WAIT (inline at streaming boundary)."),
 ("DR-PLT-003","Asset hooks for glyphs","assets/asset_hooks.csv","UI_GLYPH_XB_*, UI_GLYPH_PS_*, UI_GLYPH_DECK_* (23 physical inputs each, see input_glyphs.csv) and UI_GLYPH_KEY_TEMPLATE."),
 ("DR-PLT-004","Haptic asset hooks","assets/asset_hooks.csv","HAP_* clips from dualsense_feedback.csv as SFX-adjacent assets (UI_HAPTIC_<id>); audio thread authors haptic waveforms with the matching SFX."),
 ("DR-PLT-006","Achievement platform values","ui (new table achievements.csv) or keep here","achievements_platform.csv holds trophy grades, Gamerscore, hidden and online flags for STR_ACH_01..60. Link pass may import it as data/ui/achievements.csv with prefix ACH_."),
 ("DR-PLT-007","Entitlement IDs","new data table or keep here","ENT_ IDs in entitlements.csv; cosmetics.csv may gain an ent_id column = ENT_COS_<item suffix>."),
]
w("data-requests.csv", ["id","request","target_table","notes"], dr)
