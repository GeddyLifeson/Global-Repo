#!/usr/bin/env python3
"""Builds every table in design/companion/. Run from game-plan/:
    python3 design/companion/tools/gen_companion.py
Never hand-edit the CSVs. Every value not cited to the plan or another
design folder is a Shardfall design choice made on 3 Oct 2026."""
import csv, math, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GP = os.path.dirname(os.path.dirname(ROOT))  # game-plan/
DC = "design choice"

def write(name, header, rows):
    with open(os.path.join(ROOT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return len(rows)

def block(text):
    """'A|B|C' lines -> list of tuples."""
    return [tuple(c.strip() for c in l.split("|")) for l in text.strip().splitlines() if l.strip() and not l.startswith("#")]

# ---------------------------------------------------------------- strings
STR = []  # (id, screen, text, notes)
def S(sid, screen, text, notes=""):
    STR.append((sid, screen, text, notes))

def sblock(screen, text, prefix="STR_APP_"):
    for t in block(text):
        S(prefix + t[0], screen, t[1], t[2] if len(t) > 2 else "")

# ---------------------------------------------------------------- screens
# screen_id, name, platforms, opened_from, layout, elements, needs, offline, ui_hook
SCREENS = block("""
SCR_APP_SPLASH|Splash|All|App launch|Full-bleed key art, wordmark, Ostra Shard glow pulse (static if Reduce Motion)|Wordmark; version line; status line while the content bundle checks|None|Shows cached content if bundle check fails|UI_APP_SPLASH
SCR_APP_SIGNIN|Sign in|All|First launch; after sign-out; expired refresh token|Centered column, max 440 px wide|Four platform buttons (PlayStation, Xbox, Steam, Epic Games) in that order, each with its logo and 'Continue with' label; privacy and terms links; Help link|Online|Shows STR_APP_ERR_OFFLINE_SIGNIN|UI_APP_SIGNIN
SCR_APP_NO_CHARS|No characters yet|All|Signed in but the Profile service has no character for this account|Illustration, text, two buttons|Explains that characters appear after first online play; shows which platform is signed in; 'Link another platform' opens Accounts; 'Sign in with a different account'|Online|Cached last answer|UI_APP_EMPTY
SCR_APP_CHAR_SELECT|Characters|All|After sign-in when 2+ characters; avatar button on Home|List of up to 10 character cards (plan cap via SAV_01)|Card: Origin crest, name, level, region band, play time, last played, platform icon, 'Modded, read only' tag where XS_15 applies, 'Not synced' tag where XL_06 applies|Online first, cache after|Cached list with snapshot age|UI_APP_CHAR_CARD
SCR_APP_HOME|Home|All|Tab 1|Phone: scrolling cards. Tablet and web: 2-column grid|Character header (name, level, Seals x/100 this week, season rank); weekly reset countdown; this week's featured Strike, Hollowed Citadel and raid challenge (events_calendar.csv); live and next events; Company MOTD card; pending orders chip; inbox chip; service status banner when degraded|Online for live cards|Cached cards with 'As of' time|UI_APP_HOME
SCR_APP_CHARACTER|Character|All|Home > character header|Header plus 4 sections|Level and XP bar; Vigor split (Health, Ward, Breath); attributes Might, Finesse, Lore, Grit with points to spend shown as a read-only notice; Origin; reputation with the five factions (7 tiers); Resonances found; play time|Snapshot|Cached|UI_APP_CHARACTER
SCR_APP_SKILLS|Skills and perks|All|Character > Skills|14 skills in 3 groups (Steel, Weave, Salvage); tap a skill for its perk tree|Rank 1 to 100 with bar; perk tree nodes as a vertical list (screen readers) or tree (sighted default); gates at 25, 50, 75, 100; capstone text|Snapshot|Cached|UI_APP_SKILLS
SCR_APP_GEAR|Gear|All|Tab 2|Phone: paper-doll list. Tablet/web: doll left, item list right|Slots reuse in-game labels STR_EQ_* (Primary, Secondary, Sidearm, Off Hand, Head, Chest, Arms, Legs, Charm 1, Charm 2, Tonic Slots, Throwable); Shardborn rule line; Equip Load bar and roll type; buttons Inventory, Storage, Vault, Loadouts|Snapshot; writes are orders|Read-only offline; orders queue locally|UI_APP_GEAR
SCR_APP_INVENTORY|Pack|All|Gear > Pack|Filter bar, sort, grid (icon tiles) or list toggle|Category tabs Weapons / Armor / Charms / Consumables / Materials / Lore; sort by rarity, level, name, newest; filters element, class, rarity, locked, favorite, junk; tile shows icon, rarity notch count (F02) and level|Snapshot|Cached|UI_APP_GRID
SCR_APP_STORAGE|Storage|All|Gear > Storage|Same as Pack|The character's Lantern Hold and Anchor storage; capacity x/y|Snapshot|Cached|UI_APP_GRID
SCR_APP_VAULT|Account Vault|All|Gear > Vault|Same as Pack plus character switcher to move items|Shared across all characters on the account (proposed, DR-APP-04); capacity x/300; bound items cannot enter|Online (server-held)|Cached read-only|UI_APP_GRID
SCR_APP_ITEM|Item detail|All|Any item tile|Sheet on phone (full height), side panel on tablet/web|Name, rarity, class, level, damage or armor stats, scaling grades S to E, perks per column, infusion, Weapon Art, upgrade level, lore line; actions Equip, Move, Lock, Favorite, Mark as Junk, Compare|Snapshot; actions are orders|Actions queue offline|UI_APP_ITEM
SCR_APP_COMPARE|Compare|All|Item > Compare|Two columns side by side; stacked on phones under 400 px|Stat deltas with + and - text and arrow icons, never color alone|Snapshot|Cached|UI_APP_COMPARE
SCR_APP_SEARCH|Search gear|All|Gear > search icon|Search field with live results across pack, storage, vault and every character|Results grouped by where the item is; filter chips; recent searches (local only)|Snapshot|Cached index|UI_APP_SEARCH
SCR_APP_LOADOUTS|Loadouts|All|Gear > Loadouts|List of loadout cards|6 slots at launch, 10 from Season 3 (season_roadmap SSN_03); each shows name, weapons, armor, readiness (all items present or what is missing); actions Apply, Save current gear here, Rename, Clear|Snapshot; writes are orders|Queue offline|UI_APP_LOADOUT
SCR_APP_LOADOUT_EDIT|Edit loadout|All|Loadouts > card|Slot list like Gear|Pick an item per slot from anywhere the character can reach; warns when an item sits in another character's storage or the vault (it will move first)|Snapshot; writes are orders|Queue offline|UI_APP_LOADOUT
SCR_APP_ORDERS|Pending orders|All|Gear > orders chip; Home chip|List grouped by character|Each order: what, created time, state (Waiting for your game, Sending, Applied, Failed with reason, Expired); Cancel on waiting orders; Clear finished|Online|Shows local unsent orders|UI_APP_ORDERS
SCR_APP_SOCIAL|Social|All|Tab 3|Tabs Friends / Company / Whispers / Signal Board|Friends list from the social service with presence and rich presence line (rich_presence.csv), platform icon, Joinable tag (join happens in game)|Online|Cached list without presence|UI_APP_SOCIAL
SCR_APP_PLAYER_CARD|Player card|All|Any player name|Sheet|Same fields as SCR_SOC_PROFILE; actions Add, Whisper, Invite to Company, Mute, Block, Report (Report and Block last)|Online|Unavailable|UI_CARD_PLAYER
SCR_APP_COMPANY|Company|All|Social > Company|Header with banner, name, [TAG], level 1 to 10; sections below|MOTD; weekly goals with progress (company_goals.csv); Company XP; member count x/100; buttons Chat, Roster, Requests (Lieutenant and up), Leave|Online|Cached read-only|UI_APP_COMPANY
SCR_APP_COMPANY_CHAT|Company chat|All|Company > Chat; push|Chat thread; composer at bottom; jumps to newest unread|CHN_COMPANY history (server keeps 7 days); @mentions; item links (max 3, item token); long-press a message for Copy, Report, Mute, Block; read-aloud button (CVAA)|Online|Last 200 messages read-only|UI_APP_CHAT
SCR_APP_COMPANY_ROSTER|Roster|All|Company > Roster|Searchable list|Name#1234, rank (5 ranks), online state, last online, weekly XP added; rank actions per company_permissions.csv|Online|Cached|UI_APP_ROSTER
SCR_APP_COMPANY_REQUESTS|Join requests|All|Company > Requests|List, max 50 pending (LIM_CO_REQ_PENDING)|Applicant card with level, play style tags, language; Accept and Decline|Online|Unavailable|UI_APP_ROSTER
SCR_APP_COMPANY_FINDER|Find a Company|All|Company tab when not in one|Filter bar then results list|Filters from 01-social.md (language, platform, time zone, play style, size, join mode, minimum level); Request to Join; one Company per account|Online|Unavailable|UI_APP_FINDER
SCR_APP_WHISPERS|Whispers|All|Social > Whispers|Conversation list then thread|CHN_WHISPER, 30-day history; Friends and Company by default; privacy follows the game setting|Online|Cached read-only|UI_APP_CHAT
SCR_APP_SIGNALS|Signal Board|All|Social > Signal Board|Activity chips then post list|Posts from lfg_activities.csv activities; fixed fields only (needed players, mic, language, minimum level, 5 of 20 tags, cross-play); Apply; your post at top|Online|Unavailable (live only)|UI_APP_SIGNAL
SCR_APP_SIGNAL_NEW|Raise a Signal|All|Signal Board > Raise|Form with pickers only, no text fields|Activity, players needed, mic, language, minimum level, tags, cross-play; only enabled while your game is online (rule FEA_LFG_02)|Online and game online|Unavailable|UI_APP_SIGNAL
SCR_APP_SIGNAL_DETAIL|Signal detail|All|Any post|Header then applicant list or apply button|Poster sees up to 20 applicants with Accept and Decline and the CHN_LFG channel; applicant sees state and the channel|Online|Unavailable|UI_APP_SIGNAL
SCR_APP_EVENTS|This week|All|Tab 4 'World' > This week|Reset countdown then cards|Weekly reset Tuesday 17:00 UTC shown in local time; featured Strike, Hollowed Citadel, raid challenge; active and upcoming events (events.csv, events_calendar.csv); Iron Crown broadcasts when live|Online|Cached with 'As of' time|UI_APP_EVENTS
SCR_APP_EVENT_DETAIL|Event|All|This week > card; push|Hero art, dates in local time, rules, rewards with Owned ticks|Rules and rewards text from events.csv; Add to calendar (device calendar); remind me toggle|Online|Cached|UI_APP_EVENTS
SCR_APP_SEASON|Season|All|World > Season|Track of 50 ranks|Current season name and dates; rank and XP to next; each rank's reward with Earned tick; Ostra Logs earned so far (text only, liveops README)|Online|Cached|UI_APP_SEASON
SCR_APP_CODEX|Codex|All|Tab 5 'Codex'|Tabs reuse STR_CDX_* (Items, Places, Ship Logs, Bestiary, People)|Only entries the character has found; '{found} of {total} found'; undiscovered shows a silhouette and STR_CDX_LOCKED; Act 3 entries hidden until unlocked|Snapshot plus content bundle|Fully offline once downloaded|UI_APP_CODEX
SCR_APP_CODEX_ENTRY|Codex entry|All|Codex list|Reading view, max 680 px line length|Title, art, text (STR_LOREITEM_*), where found; bestiary: weak to, resists, drops, defeated count; Listen button uses OS text-to-speech|Content bundle|Offline|UI_APP_CODEX
SCR_APP_ATLAS|Atlas|All|Codex > Atlas|Pan and zoom map; list view alternative|Only revealed regions (Relay Tower climbed); lit Anchors; found sites; collected lore pins; no fast travel or waypoints from the app|Snapshot plus content bundle|Offline|UI_APP_ATLAS
SCR_APP_TRIUMPHS|Achievements|All|Codex > Achievements|List with progress bars|The 60 achievements (STR_ACH_01..60) with progress; hidden ones stay hidden until earned; platform unlock happens in game|Snapshot|Cached|UI_APP_TRIUMPHS
SCR_APP_STORE|Wardrobe Shop|All|More > Wardrobe Shop|Featured row (6 weekly slots) then kind tabs|Dyes, Armor ornaments, Emotes, Strider skins, Bundles; Owned tick; price in local currency from the platform store when it answers, else the tier price; 'Earn in play' items listed separately and never priced|Online|Cached 24 h, prices hidden offline|UI_APP_STORE
SCR_APP_STORE_ITEM|Shop item|All|Shop tile|Preview area then details|Renders on a neutral and a world backdrop, turntable loop (static if Reduce Motion), dye swatch preview on your character's current armor, price, Owned, Add to wishlist, 'Buy in game' text and, where live config allows, a link to the platform store page|Online|Cached|UI_APP_STORE
SCR_APP_WISHLIST|Wishlist|All|Shop > Wishlist|List|Up to 100 items; total; per-item price; nothing is bought in the app|Online|Cached|UI_APP_STORE
SCR_APP_INBOX|Inbox|All|Bell icon on Home|List, newest first, 90 days|Every push also lands here, plus order results, Company notices, report outcomes, support replies|Online|Cached|UI_APP_INBOX
SCR_APP_MORE|More|All|Tab 5 overflow on phone|List|Wardrobe Shop, Inbox, Settings, Accounts and devices, Help, Service status, Legal|None|Offline|UI_APP_LIST
SCR_APP_SETTINGS|Settings|All|More > Settings|Grouped list|Language (12 text languages, plan 7.4), theme (Dark, Light, High contrast, System), color-blind filter, text size follows OS, Reduce Motion follows OS with override, haptics, read chat aloud, biometric lock, data saver|None|Offline|UI_APP_LIST
SCR_APP_SETTINGS_PUSH|Notifications|All|Settings > Notifications|Toggles per category then per type|Categories from push_notifications.csv; quiet hours (default 22:00 to 08:00 local); 'Mute while I am playing' (default on); daily cap shown|Online to save|Edits queue|UI_APP_LIST
SCR_APP_SETTINGS_PRIVACY|Privacy|All|Settings > Privacy|List|Presence visibility, whisper privacy, Company finder listing, analytics consent (most restrictive wins, XS_17); request data export; delete account (opens account portal)|Online|Unavailable|UI_APP_LIST
SCR_APP_ACCOUNTS|Accounts and devices|All|Settings > Accounts|Two sections|Linked platforms with link state from cross-save (XL rules; linking itself happens in game or the browser flow); signed-in app devices (max 10) with Sign out; Sign out everywhere|Online|Unavailable|UI_APP_LIST
SCR_APP_HELP|Help|All|More > Help|List|Help site articles (kb_articles.csv), contact support (opens a ticket form on web), service status, report a bug in the app, app version and copy-diagnostics button|Online for tickets|KB cached|UI_APP_LIST
SCR_APP_REPORT|Report|All|Player card; message long-press|Form with reason list|Reasons from report_reasons.csv; evidence attaches the last 50 lines of the shared channel (LIM_REPORT_EVIDENCE); confirmation|Online|Unavailable|UI_APP_REPORT
SCR_APP_MAINT|Maintenance|All|Live config says maintenance|Full screen over the app; Codex still reachable|Start and end time in local time; link to status page|None|Shown from cache|UI_APP_EMPTY
SCR_APP_UPDATE|Update required|iOS, Android|App version below live config minimum|Full screen|Why, and a button to the app store page|None|Shown|UI_APP_EMPTY
SCR_APP_LOCKED|App locked|iOS, Android|Biometric lock on and app resumed after 5 min|Full screen blur|Unlock with Face ID, Touch ID, fingerprint or device passcode|None|Shown|UI_APP_EMPTY
""")

# ---------------------------------------------------------------- features
FEATURES = block("""
FEA_GEN_01|General|The app is free, has no ads and sells nothing. It never shows a price as a call to buy now and never counts down to an item leaving, because nothing leaves the shop (liveops store rules).|liveops README
FEA_GEN_02|General|One codebase in TypeScript with React Native for iOS and Android and react-native-web for the browser. Shared API client, state store and design tokens.|DC
FEA_GEN_03|General|The app never holds game rules. Every write is an order that the game or the backend checks with the same code the in-game menus use.|DC; tech/02 server authority
FEA_GEN_04|General|Static content (item definitions, strings, icons, codex text, map tiles) ships as a content bundle versioned per game patch, fetched from the CDN and cached on the device.|DC
FEA_GEN_05|General|App name is 'Shardfall Companion' and follows the game's working title if production renames it.|DC; production naming question
FEA_GEAR_01|Gear|Read the character's equipped gear, pack, storage and the Account Vault, with stats and perks exactly as the game shows them.|brief
FEA_GEAR_02|Gear|Equip, unequip, move between pack, storage and vault, lock, favorite and mark as junk. Each action is an order (live_link.csv).|DC
FEA_GEAR_03|Gear|No sell, dismantle, upgrade, infuse or craft from the app. Those spend Ember or materials and cannot be undone, so they stay at the forge in game.|DC
FEA_GEAR_04|Gear|Moves between characters go through the Account Vault (300 slots, proposed in DR-APP-04). Quest items, key items, lore items and Ember never move.|DC
FEA_GEAR_05|Gear|Shardborn rule holds in the app: one Shardborn weapon and one Shardborn armor piece equipped (plan 3.6).|plan 3.6
FEA_GEAR_06|Gear|Search finds any item across all characters, storage and the vault, with where it is.|DC
FEA_GEAR_07|Gear|Modded PC saves (XS_15) and saves flagged for tampering (tech/02) are read only in the app.|platform XS_15; tech/02
FEA_LOAD_01|Loadouts|Loadouts mirror the in-game loadouts: 6 slots at launch and 10 from Season 3 (SSN_03 adds 4).|liveops season_roadmap; DC for 6
FEA_LOAD_02|Loadouts|Applying a loadout first moves missing items from storage or the vault, then equips. If any step fails the rest still run and the order reports what was skipped.|DC
FEA_LOAD_03|Loadouts|Saving 'current gear' to a loadout reads the latest snapshot, so it warns if the snapshot is older than 2 minutes.|DC; XS_01 upload throttle
FEA_SOC_01|Social|Friends list with presence and the rich presence line from rich_presence.csv. Joining a session happens in game; the app shows Joinable but cannot launch the game on another device.|platform rich_presence
FEA_SOC_02|Social|Whispers to friends and Company members, 30-day history, same privacy setting as in game.|social chat_channels
FEA_SOC_03|Social|Mute, block and report work the same as in game and sync both ways.|social 02-safety
FEA_CO_01|Company|Company chat (CHN_COMPANY) with the 7 days of history the server already keeps, @mentions and item links.|social chat_channels
FEA_CO_02|Company|Roster, ranks, MOTD editing, weekly goals and join requests, with the same rank permissions as in game.|social company_permissions
FEA_CO_03|Company|Find and request to join a Company. Founding a Company stays in game (needs character level 10, LIM_CO_CREATE_LEVEL, and a name check at the Company hall).|DC
FEA_CO_04|Company|Chat limits are the game's: 200 characters, 5 messages per 10 s, no links, filter on the server.|social limits
FEA_LFG_01|Signal Board|Browse, filter and apply to Signals for every activity in lfg_activities.csv. Posts have no free text, same as in game.|social 01-social
FEA_LFG_02|Signal Board|Raising a Signal from the app needs your game online on some platform, because accepted players join your session. The post closes when your game goes offline.|DC
FEA_LFG_03|Signal Board|When the poster accepts you, the app pushes 'You're in' and sends a game invite; you have 5 minutes to join from your game, with one extension to 10 minutes.|DC; accessibility timing
FEA_LFG_04|Signal Board|The CHN_LFG channel is open in the app so applicants can ask a question before joining.|social chat_channels
FEA_EVT_01|Events|This week view: reset countdown, featured Strike, Hollowed Citadel and raid challenge, and events, all from live config fed by events_calendar.csv.|liveops events_calendar
FEA_EVT_02|Events|Season view with the 50-rank track, rewards, and the Ostra Logs the player has earned. Logs stay text the player unlocked in game; the app never adds lore of its own.|liveops README
FEA_EVT_03|Events|Add an event to the device calendar with times in local time.|DC
FEA_LORE_01|Codex|Codex mirrors the in-game Codex tabs and shows only what this character found; Act 3 and ending lore stay hidden until unlocked so the app never spoils the story.|plan 3.8; DC
FEA_LORE_02|Codex|Atlas shows only revealed regions, lit Anchors and found sites. No waypoints, no fast travel, no hidden-item pins.|plan 3.7; DC
FEA_LORE_03|Codex|Achievements list with progress. Unlocks stay a platform event in game.|platform XS_11
FEA_STORE_01|Store|Browse the Wardrobe Shop catalog (store_catalog.csv), see what you own, preview dyes on your current armor, and keep a wishlist.|liveops store_catalog
FEA_STORE_02|Store|No purchases in the app. Paid items are bought in game through the platform store. The app shows 'Buy in game' and, only where live config allows it per country and app store, a link to the platform store page.|DC; platform entitlements
FEA_STORE_03|Store|Prices show in local currency when the platform store price API answers; otherwise the price tier from price_tiers.csv, labeled as the list price.|liveops price_tiers
FEA_STORE_04|Store|Earn-only items (season track, events, Seals, play unlocks) show how to earn them and never a price.|liveops store rules
FEA_PUSH_01|Alerts|Push notifications by category with per-type toggles, quiet hours and a daily cap (push_notifications.csv, limits.csv).|DC
FEA_PUSH_02|Alerts|Marketing pushes (shop, wishlist) are off by default and never sent to accounts under the platform's adult age.|DC; tech/02 privacy
FEA_PUSH_03|Alerts|'Mute while I am playing' holds social pushes while the account's game is online; the game already shows them.|DC
FEA_ACC_01|Account|Sign in with PlayStation Network, Xbox network, Steam or Epic Games (auth.csv). The Epic link from cross-save shows characters from every linked platform.|platform cross_save_rules
FEA_ACC_02|Account|Accounts and devices screen: linked platforms, app devices, sign out one or all.|DC
FEA_ACC_03|Account|Data export and account deletion use the same GDPR and CCPA endpoints as the game.|tech/02 privacy
FEA_SAFE_01|Safety|Chat restrictions and bans from the penalty ladder apply in the app too; a chat-restricted player reads chat but cannot send.|social penalty_ladder
FEA_SAFE_02|Safety|Platform child accounts with communication restricted get no chat, whispers or Signal posts in the app, and no marketing pushes.|DC; platform policy
FEA_OFF_01|Offline|Everything read-only works offline from the cache with an 'As of' time; writes queue as orders on the device and send on reconnect (offline_rules.csv).|DC
FEA_HELP_01|Support|Help articles, service status and ticket entry match the game's support desk (social 03-support.md).|social 03-support
""")

# ---------------------------------------------------------------- API
API = block("""
API_AUTH_START|POST|/v1/auth/{provider}/start|Identity|none|10/min per device|none|No|Starts OAuth 2.1 code flow with PKCE in the system browser; provider is psn, xbl, steam (OpenID 2.0 bridged), epic
API_AUTH_CALLBACK|GET|/v1/auth/{provider}/callback|Identity|none|10/min per device|none|No|Exchanges the code; returns app session (mobile) or sets a secure cookie (web)
API_AUTH_REFRESH|POST|/v1/auth/token|Identity|refresh|30/hour per device|none|No|Rotating refresh tokens with reuse detection
API_AUTH_SIGNOUT|POST|/v1/auth/signout|Identity|session|10/min|none|Queued|Revokes this device; scope=all revokes every app device
API_ME|GET|/v1/me|Profile|read|60/min|60 s|Cache|Account id, display name#1234, linked platforms, age flags, privacy, chat restriction state
API_DEVICES|GET|/v1/me/devices|Identity|read|60/min|none|No|Signed-in app devices
API_DEVICE_REVOKE|DELETE|/v1/me/devices/{device_id}|Identity|session|10/min|none|No|
API_CHARS|GET|/v1/me/characters|Profile|read|60/min|60 s|Cache|Up to 10 character cards with snapshot time and flags (modded, not synced, read only)
API_CHAR|GET|/v1/characters/{cid}|Profile|read|60/min|ETag|Cache|Level, Vigor, attributes, Origin, reputation, Resonances
API_INV|GET|/v1/characters/{cid}/inventory|Profile|read|60/min|ETag|Cache|bucket=equipped,pack,storage; instance ids, item ids, rolls, perks, upgrade, lock and tag flags
API_VAULT|GET|/v1/vault|Profile|read|60/min|ETag|Cache|Account Vault contents (server-held)
API_LOADOUTS|GET|/v1/characters/{cid}/loadouts|Profile|read|60/min|ETag|Cache|
API_PROGRESS|GET|/v1/characters/{cid}/progress|Profile|read|60/min|ETag|Cache|Skills, perks, achievements progress, codex found ids, atlas reveal state
API_ORDERS_POST|POST|/v1/characters/{cid}/orders|Orders (Profile)|inventory.write|20/min|none|Queued|Body: order_id (client UUID, idempotent), type, args; returns state
API_ORDERS_GET|GET|/v1/characters/{cid}/orders|Orders (Profile)|read|60/min|none|Cache|Waiting, sending, applied, failed, expired with reason codes
API_ORDER_CANCEL|DELETE|/v1/orders/{order_id}|Orders (Profile)|inventory.write|20/min|none|Queued|Only while Waiting
API_SEALS|GET|/v1/me/seals|Economy|read|60/min|60 s|Cache|Balance, weekly earned of 100, carry cap 500 (data README item 4)
API_SEASON|GET|/v1/season/current|Live config|none|60/min|10 min|Cache|Season id, dates, track definition
API_SEASON_ME|GET|/v1/me/season|Profile|read|60/min|60 s|Cache|Rank, XP, earned rewards, Ostra Logs unlocked
API_ROTATION|GET|/v1/live/rotation|Live config|none|60/min|10 min|Cache|This week's featured Strike, Citadel variant, raid challenge, reset time
API_EVENTS|GET|/v1/live/events|Live config|none|60/min|10 min|Cache|Active and next 8 weeks of events
API_STATUS|GET|/v1/live/status|Live config|none|120/min|30 s|Cache|Service health per platform, maintenance windows
API_CONFIG|GET|/v1/live/config|Live config|none|30/min|5 min|Cache|Feature flags, min app version, store link-out countries, push copy kill switch
API_CONTENT|GET|/v1/content/manifest|CDN|none|CDN|immutable per version|Cache|Content bundle manifest for the game patch; files are hashed and immutable
API_CATALOG|GET|/v1/store/catalog|Store|none|60/min|24 h|Cache|locale and platform params; featured slots; earn-only items flagged
API_PRICES|GET|/v1/store/prices|Store|read|30/min|1 h|No|Local prices from the signed-in platform store where its API allows; else tier prices
API_OWNED|GET|/v1/me/entitlements/cosmetics|Profile|read|60/min|5 min|Cache|Owned cosmetics, filtered by platform policy (XS_06)
API_WISH_GET|GET|/v1/me/wishlist|Profile|read|60/min|60 s|Cache|
API_WISH_PUT|PUT|/v1/me/wishlist/{item_id}|Profile|social.write|30/min|none|Queued|
API_WISH_DEL|DELETE|/v1/me/wishlist/{item_id}|Profile|social.write|30/min|none|Queued|
API_FRIENDS|GET|/v1/friends|Social|read|60/min|30 s|Cache|Merged platform friends and Shardfall friends with presence
API_PLAYER|GET|/v1/players/{pid}|Social|read|60/min|5 min|Cache|Player card
API_BLOCK|POST|/v1/players/{pid}/block|Social|social.write|20/min|none|Queued|Also mute and unblock via action param
API_REPORT|POST|/v1/reports|Social (safety)|social.write|10/hour|none|No|Reason, target, channel evidence window per LIM_REPORT_EVIDENCE
API_CO|GET|/v1/company|Social|read|60/min|60 s|Cache|Company header, MOTD, level, goals
API_CO_MEMBERS|GET|/v1/company/members|Social|read|30/min|60 s|Cache|
API_CO_MEMBER_ACT|POST|/v1/company/members/{pid}:{action}|Social|social.write|20/min|none|No|promote, demote, remove; checked against company_permissions
API_CO_MOTD|PATCH|/v1/company/motd|Social|social.write|10/hour|none|No|280 characters, filtered
API_CO_REQS|GET|/v1/company/requests|Social|read|30/min|none|No|
API_CO_REQ_ACT|POST|/v1/company/requests/{rid}:{action}|Social|social.write|30/min|none|No|accept or decline
API_CO_FINDER|GET|/v1/company/finder|Social|read|30/min|5 min|No|
API_CO_JOIN|POST|/v1/company/{coid}/join-requests|Social|social.write|10/hour|none|No|
API_CO_LEAVE|POST|/v1/company:leave|Social|social.write|5/hour|none|No|Starts the 24 h rejoin cooldown
API_CHAT_GET|GET|/v1/chat/{channel}/messages|Messages|read|60/min|none|Cache|channel = company, whisper:{pid}, lfg:{sid}; before cursor
API_CHAT_POST|POST|/v1/chat/{channel}/messages|Messages|social.write|5 per 10 s|none|No|Server filter, rate limit and repeat block from social limits
API_WHISPERS|GET|/v1/whispers|Messages|read|30/min|none|Cache|Conversation list
API_SIG_LIST|GET|/v1/signals|Matchmaking (Signal Board)|read|60/min|none|No|Filters: activity, language, platform, mic, level, tags
API_SIG_POST|POST|/v1/signals|Matchmaking (Signal Board)|lfg.write|5/hour|none|No|Rejected unless the account's game is online (FEA_LFG_02)
API_SIG_REFRESH|POST|/v1/signals/{sid}:refresh|Matchmaking (Signal Board)|lfg.write|1 per post|none|No|30 to 60 minutes, once
API_SIG_CLOSE|DELETE|/v1/signals/{sid}|Matchmaking (Signal Board)|lfg.write|10/hour|none|No|
API_SIG_APPLY|POST|/v1/signals/{sid}/applications|Matchmaking (Signal Board)|lfg.write|20/hour|none|No|Max 5 open per player
API_SIG_APP_ACT|POST|/v1/signals/{sid}/applications/{aid}:{action}|Matchmaking (Signal Board)|lfg.write|60/hour|none|No|accept, decline, withdraw; accept sends the game invite
API_PUSH_REG|POST|/v1/push/devices|Push|session|10/day|none|Queued|APNs, FCM or Web Push token, app language, time zone
API_PUSH_UNREG|DELETE|/v1/push/devices/{token_id}|Push|session|10/day|none|Queued|
API_PUSH_PREFS_GET|GET|/v1/push/preferences|Push|read|30/min|none|Cache|
API_PUSH_PREFS_PUT|PUT|/v1/push/preferences|Push|session|30/min|none|Queued|
API_INBOX|GET|/v1/inbox|Push|read|60/min|none|Cache|90 days
API_INBOX_READ|POST|/v1/inbox:read|Push|session|60/min|none|Queued|
API_PRIVACY_EXPORT|POST|/v1/me/data-export|Identity|session|1/day|none|No|Same pipeline as the game (tech/02)
API_PRIVACY_DELETE|POST|/v1/me/delete|Identity|session|1/day|none|No|Opens the account portal; 30-day grace
API_STREAM|WSS|/v1/stream|Companion gateway|read|1 socket per device|none|No|Topics: chat, order status, presence, signals, inbox, inventory deltas while the game is online. Heartbeat 25 s; reconnect with backoff 1, 2, 4, 8, 16, 30 s
""")

# ---------------------------------------------------------------- auth
AUTH = block("""
AUTH_01|Providers|PlayStation Network, Xbox network (Microsoft account), Steam (OpenID 2.0, bridged by the Identity service into the app's OAuth flow) and Epic Games Account. Each needs that holder's partner approval for third-party sign-in; production tracks it as a Phase 7 task.|DC; platform XL_05
AUTH_02|Flow|OAuth 2.1 authorization code with PKCE in the system browser (ASWebAuthenticationSession on iOS, Custom Tabs on Android). No embedded web views for login.|DC
AUTH_03|Account model|The Identity service maps the platform login to the EOS product user id (tech/02). If the account has the cross-save Epic link, the app sees characters from every linked platform; if not, only the signed-in platform's characters.|tech/02; platform cross_save_rules
AUTH_04|Tokens (mobile)|Access token: signed JWT, 15 minutes. Refresh token: 30 days sliding, rotated on every use, reuse of an old one revokes the whole session. Stored in iOS Keychain and Android Keystore-backed storage.|DC
AUTH_05|Tokens (web)|The browser never holds tokens. A backend-for-frontend keeps them and gives the browser an HttpOnly, Secure, SameSite=Strict session cookie; CSRF token on writes; 7-day idle limit.|DC
AUTH_06|Scopes|read (default), inventory.write, social.write, lfg.write. All four are granted at sign-in; a chat-restricted or child account gets read and inventory.write only.|DC
AUTH_07|Devices|Up to 10 signed-in app devices per account (LIM_APP_DEVICES). The 11th sign-in signs out the oldest. New-device sign-in sends PSH_SEC_SIGNIN to the others.|DC
AUTH_08|Revocation|Platform password change, unlink or ban revokes app sessions through the holder's token webhook where one exists; otherwise the Identity service re-checks the platform token every 24 h.|DC
AUTH_09|Biometric lock|Optional. Locks the app after 5 minutes in the background; Face ID, Touch ID, Android BiometricPrompt or device passcode unlocks.|DC
AUTH_10|Age and parental controls|Age comes from the platform account. Child accounts follow the platform's communication setting: when restricted, no chat, whispers or Signal posting, and no marketing push. Under-13 accounts in the US and accounts under the local digital age of consent in the EU get no analytics.|DC; tech/02 privacy
AUTH_11|Bans|A game ban shows SCR_APP_SIGNIN with the ban notice and the appeal link (appeal_rules.csv). A chat restriction leaves the app usable with chat read-only.|social penalty_ladder
AUTH_12|Server checks|Every write checks the token scope, the account's restriction state and the target character's ownership. The client is never trusted for item ids or counts.|tech/02 security
AUTH_13|Transport|TLS 1.3 only, certificate pinning to the gateway's intermediate CA on mobile with a live-config kill switch.|DC
AUTH_14|Secrets|No API keys or secrets ship in the app binary. Push credentials and platform client secrets live in the backend secret manager.|tech/02
""")

# ---------------------------------------------------------------- live link / orders
ORDER_TYPES = block("""
ORD_EQUIP|Equip item|instance_id, slot|Same checks as the in-game equip: level and attribute requirements, Shardborn one-each, slot type, Equip Load allowed over cap (roll type changes)
ORD_UNEQUIP|Unequip item|slot|Item goes to the pack; fails if the pack is full
ORD_MOVE|Move item|instance_id, from, to (pack, storage, vault)|Bound items (quest, key, lore) cannot enter the vault; vault moves need the backend online
ORD_LOCK|Lock or unlock|instance_id, locked|Locked items cannot be sold or dismantled in game
ORD_TAG|Favorite or junk tag|instance_id, tag|Junk tags make the vendor 'Sell junk' button include it in game; the app never sells
ORD_LOADOUT_APPLY|Apply loadout|loadout_index|Moves then equips (FEA_LOAD_02)
ORD_LOADOUT_SAVE|Save current gear to loadout|loadout_index|Uses the game's current gear at apply time, not the app snapshot
ORD_LOADOUT_RENAME|Rename loadout|loadout_index, name|Max 24 characters; filtered on the server
ORD_LOADOUT_CLEAR|Clear loadout|loadout_index|
""")
LIVE = block("""
LL_01|Snapshot|The app reads the character's cloud copy (XS_01). While the game is online and an app session is open for that account, the game also streams inventory deltas every 5 s at most, so the app is live. The game streams only when the backend tells it an app is watching.|DC; platform XS_01
LL_02|Orders, game online|If the target character is loaded on the platform holding the cross-save lease, the order goes to that game client over its existing backend connection and applies at the next safe moment.|DC
LL_03|Safe moment|The same moments the in-game equipment menu allows: no damage dealt or taken for 5 s, not in a cinematic, dialogue, load, Arena match, invasion, or a raid encounter (between encounters is fine).|DC; plan 3.11
LL_04|Wait limit|An online order waits up to 10 minutes for a safe moment, then fails with ORDER_TIMEOUT.|DC
LL_05|Orders, game offline|Orders queue on the server and apply during the load screen the next time that character loads online, before the player gets control. The game shows NTF_APP_ORDERS_APPLIED with the count.|DC
LL_06|Queue|Up to 50 waiting orders per character, applied first in first out, each idempotent by its client order_id. Waiting orders expire after 7 days.|DC
LL_07|Game is the authority|Each order runs through the game's own inventory code. If an item is gone or a rule blocks it, that order fails with a reason code and the next one still runs.|tech/02 server authority
LL_08|Lease|Orders never take the cross-save lease (XL_01). They go to whichever platform holds it, or wait.|platform XL_01
LL_09|Offline play|A character played offline applies its queued orders only on its next online load, after the cloud sync and any conflict prompt (XL_02).|platform XL_02
LL_10|Account Vault|The vault lives on the server like Seals. Vault to character moves reserve the item at once; character to vault moves finish when that character's game applies the order.|DC; tech/02 Economy pattern
LL_11|Read-only saves|Modded (XS_15) or tamper-flagged saves accept no orders.|platform XS_15; tech/02
LL_12|Co-op|As a guest in someone's world, orders apply to your own character at a safe moment like solo. The host's world is never touched.|plan 3.11
""")
REASONS = block("""
ORDER_TIMEOUT|No safe moment in 10 minutes. Try again when you're out of combat.
ORDER_ITEM_GONE|That item isn't on this character any more.
ORDER_REQ_LEVEL|Your level is too low for that item.
ORDER_REQ_ATTR|You don't meet that item's attribute requirements.
ORDER_SHARDBORN|You can equip one Shardborn weapon and one Shardborn armor piece.
ORDER_PACK_FULL|Your pack is full.
ORDER_STORAGE_FULL|Storage is full.
ORDER_VAULT_FULL|The Account Vault is full.
ORDER_BOUND|Quest, key and lore items stay with their character.
ORDER_READ_ONLY|This character's save is read-only in the app.
ORDER_EXPIRED|This order waited 7 days and expired.
ORDER_DLC_LOCKED|That item needs an expansion this platform doesn't have.
ORDER_CANCELLED|You cancelled this order.
ORDER_FILTER|That name isn't allowed. Try another.
""")

# ---------------------------------------------------------------- offline cache
OFFLINE = block("""
OFF_01|Character snapshot and inventory|7 days|Shown with 'As of {time}'; stale after 2 minutes while online
OFF_02|Content bundle (items, strings, icons, codex, atlas tiles)|Until the next game patch|Downloaded on first sign-in over any network, or Wi-Fi only with Data Saver
OFF_03|Store catalog and renders|24 hours|Prices hidden offline because they come from the platform store
OFF_04|This week and events|1 hour after the next reset time|After that the cards show 'Connect to see this week'
OFF_05|Company chat, whispers|Last 200 messages per channel, 7 days|Read only offline; no outbox for chat, so nobody gets stale messages
OFF_06|Signal Board|Not cached|Live only; shows 'Signal Board needs a connection'
OFF_07|Friends and roster|24 hours|Presence hidden offline
OFF_08|Inbox|90 days|
OFF_09|Orders made offline|Up to 20 on the device|Marked 'Not sent' and sent in order on reconnect; the server then treats them like any order
OFF_10|Storage on device|150 MB cap for images and bundle (LRU), encrypted at rest with the OS file protection|Cleared on sign-out
""")

# ---------------------------------------------------------------- push
# push_id, category, default, trigger, title, body, deep_link, collapse, ttl_h, bypass_quiet
PUSH = block("""
PSH_ORDER_DONE|Gear|On|Queued orders applied while the app was in the background|Orders applied|{VAR_n} gear orders were applied to {VAR_char}.|app/orders|orders|24|No
PSH_ORDER_FAILED|Gear|On|An order failed|An order couldn't be applied|{VAR_order}: {VAR_reason}|app/orders|orders|24|No
PSH_CO_MENTION|Company|On|Someone @mentions you in Company chat|{VAR_player} mentioned you|{VAR_msg}|app/company/chat|co_mention|24|No
PSH_CO_MSG|Company|Off|New Company chat messages, digest at most every 30 minutes|Company chat|{VAR_n} new messages in {VAR_company}.|app/company/chat|co_msg|12|No
PSH_CO_REQUEST|Company|On|New join request (Lieutenant and up)|New join request|{VAR_player} wants to join {VAR_company}.|app/company/requests|co_req|72|No
PSH_CO_ACCEPTED|Company|On|Your join request was accepted|Welcome to {VAR_company}|You're now a Recruit. Say hello in Company chat.|app/company|co_join|72|No
PSH_CO_RANK|Company|On|Your rank changed|New rank|You're now {VAR_rank} in {VAR_company}.|app/company|co_rank|72|No
PSH_CO_GOAL|Company|On|A weekly Company goal is complete|Company goal complete|{VAR_goal} is done. Rewards are waiting in game.|app/company|co_goal|48|No
PSH_WHISPER|Friends|On|Whisper from a friend or Company member|{VAR_player}|{VAR_msg}|app/whispers/{pid}|whisper_{pid}|24|No
PSH_FRIEND_REQ|Friends|On|Friend request received|Friend request|{VAR_player} sent you a friend request.|app/social/requests|friend_req|72|No
PSH_FRIEND_ONLINE|Friends|Off|A favorited friend comes online, at most 3 a day|{VAR_player} is online|They're playing {VAR_activity}.|app/social|friend_on|1|No
PSH_SIG_APPLICANT|Signal Board|On|Someone applied to your Signal|New applicant|{VAR_player} applied to your {VAR_activity} Signal.|app/signals/{sid}|sig_{sid}|1|Yes
PSH_SIG_ACCEPTED|Signal Board|On|Your application was accepted|You're in|Join {VAR_player}'s {VAR_activity} from your game within 5 minutes.|app/signals/{sid}|sig_{sid}|1|Yes
PSH_SIG_EXPIRING|Signal Board|On|Your Signal has 5 minutes left|Signal ending soon|Refresh your {VAR_activity} Signal to keep it open.|app/signals/{sid}|sig_{sid}|1|No
PSH_RESET|World|Off|Weekly reset, Tuesday 17:00 UTC|New week|This week's Strike is {VAR_strike}.|app/week|reset|24|No
PSH_EVENT_START|World|On|An event starts (events.csv)|{VAR_event} has started|Runs until {VAR_end}.|app/events/{eid}|event_{eid}|24|No
PSH_EVENT_REMIND|World|On (per event)|A 'remind me' event starts in 1 hour|{VAR_event} starts soon|Starts at {VAR_start}.|app/events/{eid}|event_{eid}|2|No
PSH_SEASON_START|World|On|A new season starts|{VAR_season} is live|New Strike, Citadel variant and PvP map.|app/season|season|48|No
PSH_IRONCROWN|World|Off|An Iron Crown broadcast goes live|Iron Crown is live|{VAR_match} is on now.|app/events/ironcrown|esports|3|No
PSH_SHOP_WEEK|Shop|Off|Weekly featured slots change|Wardrobe Shop updated|See this week's featured items.|app/shop|shop|24|No
PSH_WISHLIST|Shop|Off|A wishlisted item joins a bundle or the featured row|From your wishlist|{VAR_item} is in this week's featured row.|app/shop/{item}|wish|24|No
PSH_MAINT|Service|On|Scheduled maintenance in 1 hour|Maintenance soon|Servers go down at {VAR_start} for about {VAR_minutes} minutes.|app/status|maint|2|No
PSH_SERVICE_BACK|Service|On|Maintenance or an outage ends|Servers are back|Online play is available again.|app/status|maint|6|No
PSH_REPORT_DONE|Account|On|A player you reported was actioned|Thanks for your report|We took action on a player you reported.|app/inbox|report|168|No
PSH_TICKET|Account|On|Support replied to a ticket|Support replied|There's a new reply on ticket {VAR_ticket}.|app/help|ticket|168|No
PSH_SEC_SIGNIN|Security|Always|New app device signed in|New sign-in|{VAR_device} signed in to your account. Not you? Sign out everywhere.|app/settings/accounts|sec|168|Yes
PSH_SEC_LINK|Security|Always|A platform was linked or unlinked|Account change|{VAR_platform} was {VAR_change} on your account.|app/settings/accounts|sec|168|Yes
""")

PUSH_RULES = block("""
PR_01|Quiet hours|Default 22:00 to 08:00 device local time. Pushes in quiet hours wait until it ends, except Security and Signal Board timing pushes.
PR_02|Daily cap|At most 4 non-security pushes per device per day. Over the cap they land in the inbox only.
PR_03|Mute while playing|On by default. While the account's game is online, Company, Friends and Gear pushes go to the inbox only; Signal Board and Security still push.
PR_04|Marketing|Shop category is off by default, opt-in only, never for child accounts, and never more than once a week.
PR_05|Wording|No urgency or scarcity wording ('last chance', 'leaving soon'), because nothing leaves the shop and events return. Live config has a copy kill switch per push type.
PR_06|Language|Rendered server-side in the app language; falls back to English.
PR_07|Collapse|Same collapse key replaces the older notification on the device.
PR_08|Delivery|APNs on iOS, FCM on Android, Web Push (VAPID) on web for Chrome, Edge, Firefox and installed Safari web apps.
PR_09|Privacy|Message previews in pushes are off when the device lock screen hides previews; Company and whisper text never shows for child accounts.
PR_10|Inbox|Every push also lands in the inbox for 90 days.
""")

# ---------------------------------------------------------------- limits
LIMITS = block("""
LIM_APP_DEVICES|Account|Signed-in app devices|10|devices|Oldest signs out
LIM_APP_ORDERS_QUEUE|Orders|Waiting orders per character|50|orders|
LIM_APP_ORDER_TTL|Orders|Waiting order lifetime|7|days|
LIM_APP_ORDER_WAIT|Orders|Online wait for a safe moment|10|minutes|
LIM_APP_ORDERS_LOCAL|Orders|Orders held on the device while offline|20|orders|
LIM_APP_SNAPSHOT_STALE|Gear|Snapshot age before the stale label|2|minutes|Matches the XS_01 upload throttle
LIM_APP_DELTA_RATE|Gear|Live inventory delta batch|5|seconds|
LIM_APP_VAULT|Gear|Account Vault slots|300|slots|Proposed (DR-APP-04)
LIM_APP_LOADOUTS|Gear|Loadout slots|6 (10 from Season 3)|slots|
LIM_APP_LOADOUT_NAME|Gear|Loadout name length|1-24|chars|Filtered
LIM_APP_SEARCH|Gear|Search results shown|200|items|
LIM_APP_WISHLIST|Store|Wishlist items|100|items|
LIM_APP_READ_RATE|API|Read requests per account|60|per minute|Burst 20
LIM_APP_WRITE_RATE|API|Write requests per account|20|per minute|Chat has its own limit
LIM_APP_PUSH_DAY|Push|Non-security pushes per device per day|4|pushes|
LIM_APP_CO_DIGEST|Push|Company chat digest interval|30|minutes|
LIM_APP_FRIEND_ONLINE|Push|Friend online pushes per day|3|pushes|
LIM_APP_INBOX|Push|Inbox history|90|days|
LIM_APP_CACHE|Device|Image and bundle cache|150|MB|
LIM_APP_DOWNLOAD|Device|Store download size|80|MB|Bundle downloads after install
LIM_APP_SIG_JOIN|Signal Board|Time to join after acceptance|5 (one extension to 10)|minutes|
LIM_APP_BIOLOCK|Account|Background time before biometric lock|5|minutes|
LIM_APP_WEB_IDLE|Account|Web session idle limit|7|days|
LIM_APP_SUPPORT|Platforms|App versions supported after release|90|days|
""")

# ---------------------------------------------------------------- platforms
PLATFORMS = block("""
PLT_IOS|iOS and iPadOS|iOS 17 or later, iPhone and iPad, portrait and landscape; iPad uses the tablet layout|App Store; age rating 12+ (user chat, infrequent fantasy violence in art); Sign in with Apple not required because only platform game accounts sign in|DC
PLT_ANDROID|Android|Android 10 (API 29) or later, phones, tablets and foldables; Material 3 navigation|Google Play; IARC Teen / PEGI 12 with 'Users interact'; Play data safety form from telemetry_companion.csv|DC
PLT_WEB|Web|Last 2 major versions of Chrome, Edge, Firefox and Safari; installable as a web app; works from 320 px wide|Hosted on the game's domain; same content rating notice as the game site|DC
PLT_NONE|Not supported|No watch apps, no TV apps, no desktop native app (the web app covers PC), no in-game overlay|n/a|DC
PLT_LAYOUT|Breakpoints|Phone under 600 px (bottom tabs), tablet 600 to 1199 px (side rail, two panes), desktop 1200 px and up (side rail, three panes, max content 1440 px)|n/a|DC
PLT_STACK|Stack|TypeScript, React Native with the New Architecture, react-native-web, one shared design-token package with the game UI colors from the Visual Bible|n/a|DC
PLT_FONTS|Fonts|The game's faces (art/fonts.csv): Spectral SC headings, IBM Plex Sans text, IBM Plex Mono numbers, Source Han and Plex CJK fallbacks; all SIL OFL so app use is covered|n/a|art/fonts.csv
PLT_LANG|Languages|The game's 12 text languages (plan 7.4); store listings localized in all 12|n/a|plan 7.4
PLT_RELEASE|Release cadence|Store release every 2 weeks during live service, hotfix as needed; content and live config change without a store release|n/a|DC
PLT_FORCE|Forced update|Only when an API change breaks old versions; live config sets the minimum version and SCR_APP_UPDATE shows|n/a|DC
PLT_LAUNCH|Launch|Same day as the game, Tue 15 Apr 2031 (liveops). Closed test with the plan's network beta (Phase 7.2), 5,000 testers through TestFlight and Play closed testing|n/a|plan 7.2; liveops README
PLT_PRICE|Price|Free, no ads, no in-app purchases, no tracking SDKs from ad networks|n/a|DC
""")

# ---------------------------------------------------------------- accessibility
A11Y = block("""
A11Y_01|Standard|WCAG 2.2 level AA on all three platforms, plus Apple and Android accessibility guidance. Checked at every release.|DC
A11Y_02|Screen readers|Full VoiceOver, TalkBack and web screen reader support: every control labeled, item tiles read name, rarity, level and state ('Rare Auto Rifle, level 42, equipped, locked').|WCAG 1.1.1, 4.1.2
A11Y_03|Text size|Follows iOS Dynamic Type and Android font scale up to 200%; layouts reflow and item names wrap, never cut. Web reflows at 400% zoom with no sideways scroll.|WCAG 1.4.4, 1.4.10
A11Y_04|Contrast|Body text 4.5:1, large text and UI parts 3:1 in Dark, Light and High contrast themes.|WCAG 1.4.3, 1.4.11
A11Y_05|Color|Rarity shows as corner notches 0 to 4 and a text label, elements as glyphs and names, stat changes as +/- and arrows; never color alone (game rule F02). Color-blind filters Protan, Deutan and Tritan match the game and sync from the game setting (XS_08).|WCAG 1.4.1; accessibility F02
A11Y_06|Touch targets|At least 48 by 48 dp on Android, 44 by 44 pt on iOS, 24 by 24 px with spacing on web (larger on touch screens).|WCAG 2.5.8
A11Y_07|No drag needed|Every drag (move item, reorder loadout) has a button alternative.|WCAG 2.5.7
A11Y_08|Keyboard|Web and tablets with keyboards: full keyboard use, visible focus ring 3 px, logical order, skip link, no keyboard traps.|WCAG 2.1.1, 2.4.7, 2.4.11
A11Y_09|Motion|Honors Reduce Motion: turntables become still images, the splash glow stops, transitions become fades. No flashing over 3 times a second.|WCAG 2.3.1, 2.3.3
A11Y_10|Timing|No session timeouts mid-edit. The Signal Board join window can be extended once to 10 minutes. Toasts with actions stay until dismissed.|WCAG 2.2.1
A11Y_11|Chat|Read chat aloud (OS text-to-speech) and voice-free use throughout, as CVAA asks (production A11, A23).|CVAA; social 01-social
A11Y_12|Codex|Listen button reads entries with OS text-to-speech; reading view keeps lines under 80 characters and line height 1.5.|WCAG 1.4.8 (AAA, adopted)
A11Y_13|Language|Each screen sets its language so screen readers pronounce it right; player names are marked as names.|WCAG 3.1.1, 3.1.2
A11Y_14|Errors|Errors say what happened and what to do, in text, next to the field or as a banner read by screen readers.|WCAG 3.3.1, 3.3.3
A11Y_15|Orientation|Works in portrait and landscape everywhere.|WCAG 1.3.4
A11Y_16|Haptics|Optional, off by default for repeating events; never the only signal.|DC
A11Y_17|Captions|Store preview loops are silent; trailers linked from events have captions in all 12 languages.|WCAG 1.2.2
A11Y_18|Consistent help|Help sits in the same place (More > Help) on every screen.|WCAG 3.2.6
A11Y_19|Testing|Each release: automated checks (axe for web, Accessibility Scanner and XCUI audits), a manual screen-reader pass of the 10 main flows, and a yearly audit by disabled players through the accessibility council seat (liveops community council).|DC
""")

# ---------------------------------------------------------------- deep links
DEEP = block("""
app/home|SCR_APP_HOME
app/characters/{cid}|SCR_APP_CHARACTER
app/gear|SCR_APP_GEAR
app/items/{instance_id}|SCR_APP_ITEM
app/loadouts|SCR_APP_LOADOUTS
app/orders|SCR_APP_ORDERS
app/company|SCR_APP_COMPANY
app/company/chat|SCR_APP_COMPANY_CHAT
app/company/requests|SCR_APP_COMPANY_REQUESTS
app/whispers/{pid}|SCR_APP_WHISPERS
app/social/requests|SCR_APP_SOCIAL
app/signals/{sid}|SCR_APP_SIGNAL_DETAIL
app/week|SCR_APP_EVENTS
app/events/{eid}|SCR_APP_EVENT_DETAIL
app/season|SCR_APP_SEASON
app/codex/{entry_id}|SCR_APP_CODEX_ENTRY
app/shop|SCR_APP_STORE
app/shop/{item}|SCR_APP_STORE_ITEM
app/inbox|SCR_APP_INBOX
app/help|SCR_APP_HELP
app/status|SCR_APP_MAINT
app/settings/accounts|SCR_APP_ACCOUNTS
""")

# ---------------------------------------------------------------- telemetry
TELEMETRY = block("""
app_open|platform, app_version, cold_or_warm, ms_to_interactive
app_signin|provider, result, ms
app_signout|scope (device, all)
app_screen_view|screen_id
app_order_created|type, online_target (yes or no)
app_order_result|type, state, reason, ms_to_apply
app_loadout_apply|loadout_index, steps, failed_steps
app_search|result_count (no query text)
app_chat_send|channel_kind (company, whisper, lfg)
app_signal_post|activity
app_signal_apply|activity
app_signal_join|activity, seconds_to_join, extended
app_store_view|item_id
app_wishlist_add|item_id
app_store_linkout|item_id, platform
app_push_sent|push_id, delivered, suppressed_reason
app_push_open|push_id
app_codex_open|tab
app_offline|seconds_offline, orders_queued
app_crash|platform, app_version, stack_hash
app_a11y_settings|screen_reader, text_scale, reduce_motion, theme (anonymous, opt-in)
""")

# ---------------------------------------------------------------- production
PROD = block("""
CP_01|Team at peak (months 40 to 54)|1 product designer, 1 UX and UI designer, 3 client engineers (React Native and web), 2 backend engineers (Companion gateway, Orders, Push), 1 QA engineer plus an outsourced device lab, 0.5 producer: 8.5 people|DC
CP_02|Team in live service|1 designer, 2 client engineers, 1 backend engineer, 0.5 QA: 4.5 people, part of the plan's live team of 120 (plan 5.1)|DC; plan 5.1
CP_03|Month 36|API design with the Profile, Social and Messages owners; Orders contract signed off|DC
CP_04|Month 40|Build starts: auth, character read, gear read, content bundle|DC
CP_05|Month 44|Orders, loadouts, Company chat, Signal Board, push|DC
CP_06|Month 46|Feature complete with the game's alpha (Gate 6)|plan 5.6
CP_07|Month 49|Closed test with the network beta, 5,000 testers|plan 7.2; liveops marketing_beats
CP_08|Month 51|App Store and Play review, partner sign-in approvals done|DC
CP_09|Month 54|Launch with the game, 15 Apr 2031|plan 5.6; liveops
CP_10|Build cost|About $3.4M: 8.5 people for about 16 months at $300k a year fully loaded, inside the Staff share (plan 5.2)|DC
CP_11|Running cost|About $1.4M a year: the 4.5-person team plus about $8,000 a month for gateway, push, websocket and CDN, inside the Servers and backend share (plan 5.2)|DC
CP_12|Cut order|If money runs short, cut in this order: web push, Atlas, store wishlist and link-out, Signal posting from the app. Never cut gear orders, Company chat or accessibility.|DC
""")

ASSETS = block("""
UI_APP_ICON|UI|App icon: Ostra Shard on Meridian hull plate, iOS 1024 px and Android adaptive layers, dark and tinted variants
UI_APP_PUSH_ICON|UI|Monochrome push icon (Android 96 px)
UI_APP_SPLASH|UI|Splash key art, phone and tablet crops, static fallback
UI_APP_EMPTY|UI|Ostra line illustration for empty and error states (5 poses)
UI_APP_RENDER_COSMETIC_*|UI|Two renders and a 4 s turntable loop for each store_catalog item (379), made by the store render pipeline
UI_APP_ATLAS_TILES|UI|Map tiles for 6 regions, the Undervault and The Quiet at 3 zoom levels, cut from the in-game world map art
UI_APP_STORE_SHOTS|UI|Store screenshots, 5 per device class, in 12 languages
UI_APP_FEATURE_GRAPHIC|UI|Google Play feature graphic 1024 x 500
""")

# ---------------------------------------------------------------- write tables
n = {}
n["screens"] = write("screens.csv", ["screen_id","name","platforms","opened_from","layout","elements","needs","offline","ui_hook"], SCREENS)
n["features"] = write("features.csv", ["feature_id","area","rule","source"], FEATURES)
n["api"] = write("api_endpoints.csv", ["endpoint_id","method","path","service","scope","rate_limit","cache","offline","notes"], API)
n["auth"] = write("auth.csv", ["rule_id","topic","rule","source"], AUTH)
n["orders"] = write("order_types.csv", ["order_type","name","args","rule"], ORDER_TYPES)
n["live"] = write("live_link.csv", ["rule_id","topic","rule","source"], LIVE)
n["offline"] = write("offline_rules.csv", ["rule_id","data","kept","notes"], OFFLINE)
n["push_rules"] = write("push_rules.csv", ["rule_id","topic","rule"], PUSH_RULES)
n["limits"] = write("limits.csv", ["limit_id","system","limit","value","unit","note"], LIMITS)
n["platforms"] = write("platforms.csv", ["platform_id","topic","detail","store_and_rating","source"], PLATFORMS)
n["a11y"] = write("accessibility.csv", ["rule_id","topic","rule","standard"], A11Y)
n["deep"] = write("deep_links.csv", ["path","screen_id"], [(f"shardfall-companion://{p}", s) for p, s in DEEP])
n["telemetry"] = write("telemetry_companion.csv", ["event","fields"], TELEMETRY)
n["prod"] = write("production.csv", ["row_id","topic","value","source"], PROD)
n["assets"] = write("asset_hooks_companion.csv", ["hook","type","description"], ASSETS)

# ---------------------------------------------------------------- strings
# push strings and push table
push_rows = []
for p in PUSH:
    pid, cat, dflt, trig, title, body, link, col, ttl, byp = p
    base = "STR_APP_" + pid
    S(base + "_T", "Companion push", title)
    S(base + "_B", "Companion push", body)
    push_rows.append((pid, cat, dflt, trig, base + "_T", base + "_B", "shardfall-companion://" + link, col, ttl, byp))
n["push"] = write("push_notifications.csv", ["push_id","category","default","trigger","title_str","body_str","deep_link","collapse_key","ttl_hours","bypass_quiet_hours"], push_rows)

for code, text in REASONS:
    S("STR_APP_" + code, "Companion orders", text, "order failure reason")
for t in ORDER_TYPES:
    S("STR_APP_" + t[0], "Companion orders", t[1], "order type name")
for p in PUSH:
    pass

exec(open(os.path.join(ROOT, "tools", "strings_src.py"), encoding="utf-8").read())

# popups: popup_id,kind,screen,layer,trigger,title_str,body_str,buttons,duration_s,dismiss,priority,queue_rule,sfx_hook
POP = []
LAYER = {"toast": "App toast, bottom above tabs", "banner": "App banner, top of screen", "modal": "Modal dialog over current screen", "inline": "Inline under the control"}
for pid, kind, screen, trig, title, body, buttons, dur, dismiss, prio in POPUPS:
    S("STR_APP_" + pid + "_T", screen, title, "popup title")
    if body:
        S("STR_APP_" + pid + "_B", screen, body, "popup body")
    POP.append((pid, kind, screen, LAYER[kind], trig, "STR_APP_" + pid + "_T", "STR_APP_" + pid + "_B" if body else "", buttons, dur, dismiss, prio,
                "Max 1 modal; toasts queue 3, newer replaces older" if kind != "modal" else "Blocks input", "none (app is silent; haptic only if on)" if kind != "modal" else "none"))
n["popups"] = write("popups_companion.csv", ["popup_id","kind","screen","layer","trigger","title_str","body_str","buttons","duration_s","dismiss","priority","queue_rule","sfx_hook"], POP)

# string rows: tokens and max_chars
seen, rows = set(), []
for sid, screen, text, notes in STR:
    assert sid not in seen, "duplicate " + sid
    seen.add(sid)
    toks = sorted(set(re.findall(r"\{([A-Z]+_[A-Za-z_]+)\}", text)))
    rows.append((sid, screen, text, math.ceil(len(text) * 1.4), " ".join(toks), notes))
n["strings"] = write("strings_companion.csv", ["str_id","screen","text_en","max_chars","tokens","notes"], rows)

# clash check against every other strings file
others = {}
for f in [os.path.join(GP, "data/ui/strings.csv"), os.path.join(GP, "data/ui/strings_data.csv")] + glob.glob(os.path.join(GP, "design/*/*strings*.csv")):
    if "/companion/" in f:
        continue
    try:
        with open(f, encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if len(r) > 2: others[r[0]] = r[2]
    except OSError:
        pass
mine = {r[0]: r[2] for r in rows}
clash = sorted(k for k in seen & others.keys() if others[k] != mine[k])
assert not clash, "string id clash: %s" % clash[:10]
ALLOWED = ("ITM", "ACT", "PRK", "VAR", "BTN", "SKL", "ATTR", "ELEM", "STATUS", "FAC", "CMP", "REGION")
bad = [r[0] for r in rows for t in r[4].split() if t.split("_")[0] not in ALLOWED]
assert not bad, "bad token prefix in %s" % bad[:5]

exec(open(os.path.join(ROOT, "tools", "requests_src.py"), encoding="utf-8").read())
print("companion tables:", n)
