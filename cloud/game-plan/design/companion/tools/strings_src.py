# Screen strings and popups for the companion app. exec'd by gen_companion.py.
# Format per line: SUFFIX | English text | optional note. IDs become STR_APP_<SUFFIX>.

sblock("Companion shared", """
NAME|Shardfall Companion|App name; follows the game's working title
TAB_HOME|Home
TAB_GEAR|Gear
TAB_SOCIAL|Social
TAB_WORLD|World
TAB_CODEX|Codex
TAB_MORE|More
BTN_BACK|Back
BTN_CLOSE|Close
BTN_CANCEL|Cancel
BTN_CONFIRM|Confirm
BTN_DONE|Done
BTN_RETRY|Try Again
BTN_SAVE|Save
BTN_SEE_ALL|See All
BTN_FILTER|Filter
BTN_SORT|Sort
BTN_CLEAR|Clear
BTN_SEARCH|Search
BTN_REFRESH|Refresh
BTN_SHARE|Share
BTN_REPORT|Report
BTN_BLOCK|Block
BTN_MUTE|Mute
BTN_UNMUTE|Unmute
BTN_UNBLOCK|Unblock
BTN_HELP|Help
AS_OF|As of {VAR_time}|Snapshot age label
AS_OF_LIVE|Live|Shown while the game streams deltas
STALE|This may be out of date. Your game syncs every 2 minutes.
OFFLINE_BANNER|You're offline. Showing what was saved on this device.
LOADING|Loading…
EMPTY_GENERIC|Nothing here yet.
PLATFORM_PS|PlayStation
PLATFORM_XBOX|Xbox
PLATFORM_STEAM|Steam
PLATFORM_EPIC|Epic Games
GAME_ONLINE|Playing now on {VAR_platform}
GAME_OFFLINE|Not playing
TIME_LOCAL|{VAR_time} your time
COUNTDOWN_DHM|{VAR_d}d {VAR_h}h {VAR_m}m
COUNTDOWN_HM|{VAR_h}h {VAR_m}m
""")

sblock("Companion splash and sign-in", """
SPLASH_CHECK|Checking for new game data…
SPLASH_DOWNLOAD|Downloading game data ({VAR_mb} MB)…
SPLASH_WIFI|Game data will download on Wi-Fi. Data Saver is on.
SIGNIN_TITLE|Sign in with your game account
SIGNIN_BODY|Use the account you play Shardfall with. If you linked platforms for cross-save, any of them works.
SIGNIN_PS|Continue with PlayStation
SIGNIN_XBOX|Continue with Xbox
SIGNIN_STEAM|Continue with Steam
SIGNIN_EPIC|Continue with Epic Games
SIGNIN_TERMS|By signing in you agree to the Terms of Service and Privacy Policy.
SIGNIN_TERMS_LINK|Terms of Service
SIGNIN_PRIVACY_LINK|Privacy Policy
SIGNIN_WAIT|Finishing sign-in…
SIGNIN_BANNED_T|This account is suspended
SIGNIN_BANNED_B|Suspended until {VAR_date}. You can appeal on the help site.
SIGNIN_BANNED_PERM|This account is permanently suspended. You can appeal on the help site.
SIGNIN_APPEAL|Appeal
NOCHAR_TITLE|No characters yet
NOCHAR_BODY|Your characters show up here after you play Shardfall online once on {VAR_platform}.
NOCHAR_LINK|Link Another Platform
NOCHAR_SWITCH|Use a Different Account
""")

sblock("Companion characters", """
CHARS_TITLE|Characters
CHARS_COUNT|{VAR_n} of 10
CHAR_LEVEL|Level {VAR_n}
CHAR_PLAYTIME|{VAR_h} h played
CHAR_LASTPLAYED|Last played {VAR_date}
CHAR_MODDED|Modded, read only
CHAR_MODDED_D|This save loaded PC mods, so it never uploads to the cloud and can't be changed from the app.
CHAR_NOTSYNCED|Not synced
CHAR_NOTSYNCED_D|This character stays on {VAR_platform} until a cross-save slot frees up.
CHAR_FLAGGED|Read only
CHAR_FLAGGED_D|This save needs to resync from the cloud in game before the app can change it.
CHAR_SWITCH|Switch Character
CHAR_TITLE|Character
CHAR_XP|{VAR_xp} / {VAR_next} XP
CHAR_VIGOR|Vigor
CHAR_ATTRS|Attributes
CHAR_POINTS|{VAR_n} unspent points. Spend them at an Anchor in game.
CHAR_ORIGIN|Origin
CHAR_REP|Reputation
CHAR_RESONANCES|Resonances
CHAR_RES_FOUND|{VAR_n} of {VAR_total} found
SKILLS_TITLE|Skills and Perks
SKILLS_STEEL|Steel
SKILLS_WEAVE|Weave
SKILLS_SALVAGE|Salvage
SKILLS_RANK|Rank {VAR_n} of 100
SKILLS_PERKS|Perks
SKILLS_GATE|Unlocks at rank {VAR_n}
SKILLS_TREE_VIEW|Tree
SKILLS_LIST_VIEW|List
""")

sblock("Companion home", """
HOME_SEALS|Seals this week: {VAR_n} / 100
HOME_SEALS_HELD|{VAR_n} Seals held
HOME_SEASON_RANK|Season rank {VAR_n}
HOME_RESET|Weekly reset in {VAR_time}
HOME_FEATURED|This week
HOME_STRIKE|Featured Strike
HOME_CITADEL|Hollowed Citadel
HOME_RAID|Raid challenge
HOME_EVENTS_NOW|Happening now
HOME_EVENTS_NEXT|Coming up
HOME_MOTD|From your Company
HOME_ORDERS_CHIP|{VAR_n} orders waiting
HOME_INBOX_CHIP|{VAR_n} new
HOME_STATUS_DEGRADED|Some online services are having problems. See status.
HOME_STATUS_LINK|Service Status
""")

sblock("Companion gear", """
GEAR_TITLE|Gear
GEAR_PACK|Pack
GEAR_STORAGE|Storage
GEAR_VAULT|Account Vault
GEAR_LOADOUTS|Loadouts
GEAR_ORDERS|Pending Orders
GEAR_EMPTY_SLOT|Empty
GEAR_EQUIPLOAD|Equip Load {VAR_pct}%
GEAR_ROLL_LIGHT|Light roll
GEAR_ROLL_MEDIUM|Medium roll
GEAR_ROLL_HEAVY|Heavy roll
GEAR_CAPACITY|{VAR_n} / {VAR_max}
GEAR_VAULT_D|Shared by every character on your account. Quest, key and lore items stay with their character.
GEAR_VAULT_ONLINE|The Account Vault needs a connection.
CAT_WEAPONS|Weapons
CAT_ARMOR|Armor
CAT_CHARMS|Charms
CAT_CONSUMABLES|Consumables
CAT_MATERIALS|Materials
CAT_LORE|Lore
SORT_RARITY|Rarity
SORT_LEVEL|Level
SORT_NAME|Name
SORT_NEWEST|Newest
FILTER_ELEMENT|Element
FILTER_CLASS|Class
FILTER_RARITY|Rarity
FILTER_LOCKED|Locked
FILTER_FAVORITE|Favorites
FILTER_JUNK|Junk
VIEW_GRID|Grid
VIEW_LIST|List
ITEM_EQUIP|Equip
ITEM_UNEQUIP|Unequip
ITEM_MOVE|Move
ITEM_MOVE_TO|Move to {VAR_place}
ITEM_LOCK|Lock
ITEM_UNLOCK|Unlock
ITEM_FAVORITE|Favorite
ITEM_UNFAVORITE|Remove Favorite
ITEM_JUNK|Mark as Junk
ITEM_UNJUNK|Not Junk
ITEM_COMPARE|Compare
ITEM_EQUIPPED|Equipped
ITEM_LOCKED|Locked
ITEM_WHERE|On {VAR_char}, {VAR_place}
ITEM_LEVEL|Level {VAR_n}
ITEM_UPGRADE|+{VAR_n}
ITEM_SCALING|Scaling
ITEM_PERKS|Perks
ITEM_INFUSION|Infusion
ITEM_ART|Weapon Art
ITEM_REQS|Requires
ITEM_BOUND|Stays with this character
ITEM_FORGE_NOTE|Upgrade, infuse, sell or dismantle at the forge in game.
ITEM_PENDING|Order waiting
COMPARE_TITLE|Compare
COMPARE_BETTER|+{VAR_n} better
COMPARE_WORSE|{VAR_n} worse
COMPARE_SAME|Same
SEARCH_HINT|Search all your gear
SEARCH_EMPTY|No gear matches "{VAR_query}".
SEARCH_RECENT|Recent searches
SEARCH_MORE|Showing the first 200. Add a filter to narrow it down.
LOADOUTS_TITLE|Loadouts
LOADOUT_APPLY|Apply
LOADOUT_SAVE_CURRENT|Save Current Gear Here
LOADOUT_RENAME|Rename
LOADOUT_CLEAR|Clear Loadout
LOADOUT_READY|Ready
LOADOUT_MISSING|{VAR_n} items missing
LOADOUT_MOVES|{VAR_n} items will move first
LOADOUT_EMPTY|Empty loadout
LOADOUT_NAME_HINT|Loadout name
LOADOUT_MORE_S3|4 more loadout slots arrive in Season 3.
LOADOUT_OTHER_CHAR|In {VAR_char}'s storage. It will move through the vault.
ORDERS_TITLE|Pending Orders
ORDERS_EMPTY|No orders waiting.
ORDERS_WAITING|Waiting for your game
ORDERS_WAITING_D|Applies next time {VAR_char} loads online.
ORDERS_SENDING|Sending to your game
ORDERS_SAFE|Waiting until you're out of combat
ORDERS_APPLIED|Applied
ORDERS_FAILED|Couldn't apply
ORDERS_EXPIRED|Expired
ORDERS_NOTSENT|Not sent yet. Sends when you're back online.
ORDERS_CANCEL|Cancel Order
ORDERS_CLEAR|Clear Finished
""")

sblock("Companion social", """
SOCIAL_TITLE|Social
SOCIAL_FRIENDS|Friends
SOCIAL_COMPANY|Company
SOCIAL_WHISPERS|Whispers
SOCIAL_SIGNALS|Signal Board
SOCIAL_ONLINE|Online ({VAR_n})
SOCIAL_OFFLINE|Offline ({VAR_n})
SOCIAL_JOINABLE|Joinable in game
SOCIAL_NOFRIENDS|No friends yet. Add players from their player card.
SOCIAL_REQUESTS|Requests ({VAR_n})
SOCIAL_ACCEPT|Accept
SOCIAL_DECLINE|Decline
CARD_ADD|Add Friend
CARD_WHISPER|Whisper
CARD_INVITE_CO|Invite to Company
CARD_MET|Met in {VAR_activity}
WHISPERS_EMPTY|No whispers yet.
WHISPERS_PRIVACY|Only friends and Company members can whisper you. Change this in Privacy.
""")

sblock("Companion company", """
CO_TITLE|Company
CO_LEVEL|Level {VAR_n}
CO_MEMBERS|{VAR_n} / 100 members
CO_MOTD|Message of the Day
CO_MOTD_EDIT|Edit Message
CO_MOTD_HINT|Up to 280 characters
CO_GOALS|Weekly Goals
CO_GOAL_PROGRESS|{VAR_n} / {VAR_target}
CO_XP|Company XP
CO_CHAT|Chat
CO_ROSTER|Roster
CO_REQUESTS|Join Requests
CO_LEAVE|Leave Company
CO_NONE_TITLE|You're not in a Company
CO_NONE_BODY|Companies are groups of up to 100 players who play together and earn cosmetic rewards. Find one here, or found your own at the Company hall in Lantern Hold.
CO_FIND|Find a Company
CO_REQUEST_JOIN|Request to Join
CO_REQUEST_SENT|Request sent
CO_FILTER_LANG|Language
CO_FILTER_PLATFORM|Platform
CO_FILTER_TZ|Time zone
CO_FILTER_STYLE|Play style
CO_FILTER_SIZE|Size
CO_FILTER_JOIN|Join mode
CO_FILTER_LEVEL|Minimum level
CO_FINDER_EMPTY|No Companies match these filters.
CO_RANK_PROMOTE|Promote
CO_RANK_DEMOTE|Demote
CO_REMOVE|Remove from Company
CO_LAST_ONLINE|Last online {VAR_date}
CO_WEEK_XP|{VAR_n} XP this week
CO_REQ_EMPTY|No join requests.
CO_REQ_EXPIRES|Expires in {VAR_d} days
CHAT_HINT|Message your Company
CHAT_SEND|Send
CHAT_COUNT|{VAR_n} / 200
CHAT_NEW|New messages
CHAT_JUMP|Jump to newest
CHAT_COPY|Copy
CHAT_READ_ALOUD|Read Aloud
CHAT_HISTORY_NOTE|Company chat keeps 7 days of messages.
CHAT_RESTRICTED|You can read chat but can't send messages until {VAR_date}.
CHAT_CHILD|Chat is turned off by your platform's family settings.
CHAT_SLOWDOWN|Slow down. You can send again in {VAR_s} s.
CHAT_REPEAT|You just sent that.
CHAT_LINK_STRIPPED|Links aren't allowed, so it was removed.
CHAT_ITEM_LINK|Link an Item
CHAT_MENTION|@{VAR_player}
""")

sblock("Companion signal board", """
SIG_TITLE|Signal Board
SIG_RAISE|Raise a Signal
SIG_YOURS|Your Signal
SIG_NEEDS|Needs {VAR_n}
SIG_MIC_REQ|Mic required
SIG_MIC_PREF|Mic preferred
SIG_MIC_NONE|No mic needed
SIG_LANG|Language
SIG_MINLEVEL|Level {VAR_n}+
SIG_CROSSPLAY|Cross-play
SIG_TAGS|Tags (up to 5)
SIG_APPLY|Apply
SIG_APPLIED|Applied
SIG_WITHDRAW|Withdraw
SIG_APPLICANTS|Applicants ({VAR_n})
SIG_ACCEPT|Accept
SIG_DECLINE|Decline
SIG_CLOSE|Close Signal
SIG_REFRESH|Keep Open 30 More Minutes
SIG_EXPIRES|Closes in {VAR_m} min
SIG_EMPTY|No Signals for this activity right now. Try matchmaking in game.
SIG_GAME_NEEDED|Start Shardfall to raise a Signal. Players you accept join your game.
SIG_ACCEPTED_T|You're in
SIG_ACCEPTED_B|Join from your game within {VAR_m} minutes. {VAR_player} has sent you an invite.
SIG_EXTEND|I Need More Time
SIG_APPLY_LIMIT|You have 5 open applications. Withdraw one to apply here.
SIG_CHANNEL|Signal chat
SIG_MM_ALT|Or use matchmaking in game
""")

sblock("Companion world and season", """
WORLD_TITLE|World
WEEK_TITLE|This Week
WEEK_RESET|Resets {VAR_day} at {VAR_time} your time
EVENT_LIVE|Live now
EVENT_UPCOMING|Starts {VAR_date}
EVENT_ENDS|Ends {VAR_date}
EVENT_RULES|How it works
EVENT_REWARDS|Rewards
EVENT_OWNED|Owned
EVENT_CALENDAR|Add to Calendar
EVENT_REMIND|Remind Me
EVENT_REMIND_ON|Reminder on
EVENT_RETURNS|This event comes back every season.
IRONCROWN_LIVE|Iron Crown is live
IRONCROWN_WATCH|Watch
SEASON_TITLE|Season
SEASON_DATES|{VAR_start} to {VAR_end}
SEASON_RANK|Rank {VAR_n} of 50
SEASON_XP|{VAR_xp} / {VAR_next} to next rank
SEASON_EARNED|Earned
SEASON_LOGS|Ostra Logs
SEASON_LOG_LOCKED|Reach rank {VAR_n} in game to hear this log.
SEASON_FREE_NOTE|The season track is free and its rewards are never sold.
""")

sblock("Companion codex", """
CODEX_ATLAS|Atlas
CODEX_ACH|Achievements
CODEX_LISTEN|Listen
CODEX_STOP|Stop
CODEX_FOUND_AT|Found at {VAR_place}
CODEX_SPOILER|Some entries stay hidden until you reach them in the story.
ATLAS_TITLE|Atlas
ATLAS_LIST|List View
ATLAS_MAP|Map View
ATLAS_DARK|Climb this region's Relay Tower in game to reveal it.
ATLAS_ANCHORS|Anchors lit: {VAR_n} / {VAR_total}
ATLAS_SITES|Sites found: {VAR_n} / {VAR_total}
ATLAS_LORE|Lore found: {VAR_n} / {VAR_total}
ATLAS_NOTE|The Atlas shows what you've found. Travel happens in game.
ACH_TITLE|Achievements
ACH_PROGRESS|{VAR_n} / {VAR_total}
ACH_HIDDEN|Hidden achievement
ACH_EARNED|Earned {VAR_date}
ACH_PLATFORM_NOTE|Achievements unlock on your platform when you next play.
""")

sblock("Companion store", """
STORE_TITLE|Wardrobe Shop
STORE_FEATURED|Featured This Week
STORE_DYES|Dyes
STORE_ORNAMENTS|Armor Ornaments
STORE_EMOTES|Emotes
STORE_SKINS|Strider Skins
STORE_BUNDLES|Bundles
STORE_EARN|Earn in Play
STORE_OWNED|Owned
STORE_PRICE|{VAR_price}
STORE_LIST_PRICE|List price {VAR_price}
STORE_PRICE_NOTE|Your platform store sets the final price and tax.
STORE_BUY_IN_GAME|Buy in game from the Wardrobe Shop in Lantern Hold.
STORE_OPEN_PLATFORM|View on {VAR_platform} Store
STORE_WISH_ADD|Add to Wishlist
STORE_WISH_REMOVE|Remove from Wishlist
STORE_PREVIEW_ME|Preview on My Armor
STORE_PREVIEW_NEUTRAL|Plain Backdrop
STORE_PREVIEW_WORLD|World Backdrop
STORE_EARN_HOW|How to earn: {VAR_source}
STORE_BUNDLE_NOTE|Bundle price drops for items you already own.
STORE_NO_RANDOM|Every item is shown before you buy. Nothing is random.
STORE_OFFLINE|Prices need a connection.
WISH_TITLE|Wishlist
WISH_EMPTY|Your wishlist is empty.
WISH_TOTAL|Total {VAR_price}
WISH_LIMIT|Your wishlist holds 100 items.
""")

sblock("Companion inbox and more", """
INBOX_TITLE|Inbox
INBOX_EMPTY|No messages.
INBOX_MARK_READ|Mark All Read
MORE_TITLE|More
MORE_STATUS|Service Status
MORE_LEGAL|Legal
MORE_VERSION|Version {VAR_version}
""")

sblock("Companion settings", """
SET_TITLE|Settings
SET_LANGUAGE|Language
SET_THEME|Theme
SET_THEME_DARK|Dark
SET_THEME_LIGHT|Light
SET_THEME_HC|High Contrast
SET_THEME_SYSTEM|Match Device
SET_CB|Color-Blind Filter
SET_CB_OFF|Off
SET_CB_PROTAN|Protanopia
SET_CB_DEUTAN|Deuteranopia
SET_CB_TRITAN|Tritanopia
SET_CB_SYNC|Synced with your game setting
SET_TEXT|Text Size
SET_TEXT_D|Follows your device text size.
SET_MOTION|Reduce Motion
SET_MOTION_D|Follows your device setting unless you change it here.
SET_HAPTICS|Haptics
SET_READ_ALOUD|Read Chat Aloud
SET_BIOLOCK|Lock with Face ID, Fingerprint or Passcode
SET_DATASAVER|Data Saver
SET_DATASAVER_D|Download game data and images on Wi-Fi only.
SET_PUSH|Notifications
SET_PUSH_OFF_OS|Notifications are off for this app in your device settings.
SET_PUSH_OPEN_OS|Open Device Settings
SET_QUIET|Quiet Hours
SET_QUIET_FROM|From
SET_QUIET_TO|To
SET_MUTE_PLAYING|Mute While I'm Playing
SET_MUTE_PLAYING_D|Social and gear alerts wait in your inbox while you're in game.
SET_DAILY_CAP|You'll get at most 4 alerts a day. The rest wait in your inbox.
PUSHCAT_GEAR|Gear
PUSHCAT_COMPANY|Company
PUSHCAT_FRIENDS|Friends
PUSHCAT_SIGNAL|Signal Board
PUSHCAT_WORLD|World and Events
PUSHCAT_SHOP|Wardrobe Shop
PUSHCAT_SERVICE|Service
PUSHCAT_ACCOUNT|Account
PUSHCAT_SECURITY|Security (always on)
SET_PRIVACY|Privacy
SET_PRESENCE|Show When I'm Online
SET_WHISPER_PRIV|Who Can Whisper Me
SET_WHISPER_FRIENDS|Friends and Company
SET_WHISPER_ANYONE|Anyone
SET_WHISPER_NONE|No One
SET_FINDER|List My Company in the Finder
SET_ANALYTICS|Share Usage Data
SET_ANALYTICS_D|Helps us fix problems. The stricter of your game and app choices applies.
SET_EXPORT|Request My Data
SET_EXPORT_SENT|We'll email a download link within 30 days.
SET_DELETE|Delete My Account
SET_DELETE_D|Opens the account portal. This deletes your game account too.
ACC_TITLE|Accounts and Devices
ACC_LINKED|Linked Platforms
ACC_LINKED_D|Link platforms for cross-save in game under Options > Account.
ACC_LINK_STATE_ON|Linked
ACC_LINK_STATE_OFF|Not linked
ACC_HOLDER|Playing here now
ACC_DEVICES|Signed-In Devices
ACC_THIS_DEVICE|This device
ACC_SIGNOUT|Sign Out
ACC_SIGNOUT_ALL|Sign Out Everywhere
""")

sblock("Companion help and report", """
HELP_TITLE|Help
HELP_ARTICLES|Help Articles
HELP_CONTACT|Contact Support
HELP_BUG|Report an App Bug
HELP_COPY_DIAG|Copy Diagnostics
HELP_COPIED|Copied
REPORT_TITLE|Report {VAR_player}
REPORT_REASON|What happened?
REPORT_EVIDENCE|The last 50 lines of chat you both saw are attached.
REPORT_SEND|Send Report
REPORT_THANKS|Thanks. Our team will review it.
REPORT_BLOCK_TOO|Also block this player
MAINT_TITLE|Down for maintenance
MAINT_BODY|Online services are down from {VAR_start} to about {VAR_end} your time. The Codex still works.
UPDATE_TITLE|Update needed
UPDATE_BODY|This version of the app can't talk to the game servers any more. Update to keep using it.
UPDATE_BTN|Update
LOCK_TITLE|Shardfall Companion is locked
LOCK_BTN|Unlock
""")

sblock("Companion errors", """
ERR_OFFLINE_SIGNIN|You need a connection to sign in.
ERR_SIGNIN_FAILED|Sign-in didn't finish. Try again.
ERR_SIGNIN_CANCEL|Sign-in was cancelled.
ERR_PROVIDER_DOWN|{VAR_platform} sign-in is down right now. Try another linked platform or try later.
ERR_SESSION|You were signed out. Sign in again to continue.
ERR_SERVER|Something went wrong on our side. Try again in a moment.
ERR_RATE|Too many requests. Wait a moment.
ERR_NOT_FOUND|That isn't available any more.
ERR_PERMISSION|Your Company rank can't do that.
ERR_CONTENT_OLD|Your game data is out of date. Updating…
ERR_NAME_FILTER|That text isn't allowed. Try something else.
""")

# In-game strings the companion feature needs (shown by the game, not the app)
sblock("Companion (in game)", """
INGAME_NAME|Companion App|Options > Account row
INGAME_DESC|Manage gear, chat with your Company and check the week from your phone or browser.
INGAME_QR|Scan to get the app
INGAME_ORDERS_FAIL|{VAR_n} couldn't be applied. See the app for details.
INGAME_SIG_APP|Raised from the Companion app
""")

# popups: id, kind, screen, trigger, title, body, buttons, duration_s, dismiss, priority
POPUPS = [
    ("NTF_APP_ORDER_QUEUED", "toast", "Companion gear", "Order created while the game is offline", "Order saved", "It applies next time this character loads online.", "View Orders", "4.0", "Auto or swipe", "2"),
    ("NTF_APP_ORDER_SENT", "toast", "Companion gear", "Order sent to a running game", "Sent to your game", "It applies once you're out of combat.", "", "3.0", "Auto or swipe", "2"),
    ("NTF_APP_ORDER_DONE", "toast", "Companion gear", "Order applied while the app is open", "Applied", "", "", "3.0", "Auto or swipe", "2"),
    ("NTF_APP_ORDER_FAIL", "toast", "Companion gear", "Order failed while the app is open", "Couldn't apply", "{VAR_reason}", "Details", "Until dismissed", "Swipe or button", "3"),
    ("NTF_APP_ORDERS_APPLIED", "toast", "HUD", "Game applies queued app orders during load", "Companion orders applied", "{VAR_n} gear changes from the app were applied.", "", "4.0", "Auto", "2"),
    ("NTF_APP_COPIED", "toast", "Companion shared", "Copy action", "Copied", "", "", "2.0", "Auto", "1"),
    ("NTF_APP_WISH_ADDED", "toast", "Companion store", "Wishlist add", "Added to wishlist", "", "Undo", "4.0", "Auto or swipe", "1"),
    ("NTF_APP_SIG_APPLIED", "toast", "Companion signal board", "Application sent", "Application sent", "You'll get an alert if they accept.", "", "3.0", "Auto", "2"),
    ("BAN_APP_OFFLINE", "banner", "Companion shared", "Network lost", "You're offline", "Showing what was saved on this device.", "", "Until online", "Auto", "4"),
    ("BAN_APP_STALE", "banner", "Companion gear", "Snapshot older than 2 min and game not streaming", "This may be out of date", "Your game syncs every 2 minutes.", "Refresh", "Until refreshed", "Button", "2"),
    ("BAN_APP_DEGRADED", "banner", "Companion home", "Live config marks a service degraded", "Some services have problems", "Gear changes may take longer to apply.", "Status", "Until resolved", "Auto", "3"),
    ("BAN_APP_GAME_LIVE", "banner", "Companion gear", "Game online and streaming for this character", "Live with your game", "Changes apply in game within seconds.", "", "While live", "Auto", "1"),
    ("CNF_APP_SIGNOUT_ALL", "modal", "Companion settings", "Sign Out Everywhere pressed", "Sign out everywhere?", "Every phone, tablet and browser using the app will be signed out. Your game is not affected.", "Sign Out Everywhere / Cancel", "Until input", "Button press", "5"),
    ("CNF_APP_LEAVE_CO", "modal", "Companion company", "Leave Company pressed", "Leave {VAR_company}?", "You can't join another Company for 24 hours.", "Leave / Stay", "Until input", "Button press", "5"),
    ("CNF_APP_REMOVE_MEMBER", "modal", "Companion company", "Remove from Company pressed", "Remove {VAR_player}?", "They can join another Company right away.", "Remove / Cancel", "Until input", "Button press", "5"),
    ("CNF_APP_CLEAR_LOADOUT", "modal", "Companion gear", "Clear Loadout pressed", "Clear this loadout?", "The items stay where they are. Only the saved set is cleared.", "Clear / Cancel", "Until input", "Button press", "4"),
    ("CNF_APP_LOADOUT_MOVES", "modal", "Companion gear", "Apply loadout that needs items moved", "Move items first?", "{VAR_n} items will move from storage or the vault before equipping.", "Apply / Cancel", "Until input", "Button press", "4"),
    ("CNF_APP_CLOSE_SIGNAL", "modal", "Companion signal board", "Close Signal pressed", "Close your Signal?", "Applicants will be told it closed.", "Close / Keep Open", "Until input", "Button press", "4"),
    ("CNF_APP_LINKOUT", "modal", "Companion store", "View on platform store pressed", "Open {VAR_platform} Store?", "You'll leave the app. Purchases happen on the platform store, not here.", "Open / Cancel", "Until input", "Button press", "3"),
    ("CNF_APP_DELETE", "modal", "Companion settings", "Delete My Account pressed", "Delete your Shardfall account?", "This opens the account portal. Deleting removes your characters, cosmetics and Company membership after 30 days.", "Continue / Cancel", "Until input", "Button press", "5"),
    ("ERR_APP_ORDER_LIMIT", "modal", "Companion gear", "51st waiting order for a character", "Too many orders waiting", "This character already has 50 orders waiting. Play online once or cancel some.", "View Orders / OK", "Until input", "Button press", "4"),
    ("ERR_APP_VAULT_FULL", "inline", "Companion gear", "Move to vault with 300 items", "The Account Vault is full", "", "", "Until changed", "Auto", "3"),
    ("ERR_APP_READ_ONLY", "inline", "Companion gear", "Action on modded or flagged save", "This character is read only", "", "", "Until changed", "Auto", "3"),
    ("ERR_APP_CHAT_RATE", "inline", "Companion company", "6th message in 10 s", "Slow down", "You can send again in {VAR_s} s.", "", "Until timer ends", "Auto", "3"),
    ("ERR_APP_GAME_NEEDED", "inline", "Companion signal board", "Raise a Signal with no game online", "Start Shardfall first", "Players you accept join your game.", "", "Until changed", "Auto", "3"),
    ("ERR_APP_DEVICE_LIMIT", "modal", "Companion splash and sign-in", "11th device signs in", "Signed out your oldest device", "{VAR_device} was signed out because you can use the app on 10 devices.", "OK", "Until input", "Button press", "3"),
    ("PRM_APP_PUSH_ASK", "modal", "Companion settings", "First time the player turns on a push category, never at first launch", "Turn on alerts?", "Get alerts for Company mentions, Signal Board replies and gear orders. You choose which in Settings.", "Turn On / Not Now", "Until input", "Button press", "3"),
    ("PRM_APP_SIG_JOIN", "modal", "Companion signal board", "App opened from PSH_SIG_ACCEPTED", "You're in", "Join from your game within {VAR_m} minutes.", "I Need More Time / OK", "Until input", "Button press", "5"),
    ("INL_APP_PENDING", "inline", "Companion gear", "Item has a waiting order", "Order waiting", "", "", "While waiting", "Auto", "1"),
]
