#!/usr/bin/env python3
"""Writes every table in design/social/. Run from anywhere: python3 gen_social.py
All values are Shardfall design choices (3 Oct 2026) unless a note cites the plan or another folder."""
import csv, math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def w(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        c = csv.writer(f)
        c.writerow(header)
        c.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def mc(t):
    return max(8, math.ceil(len(t) * 1.4))


def toks(t):
    import re
    return " ".join(sorted(set(re.findall(r"\{([A-Z]+_[a-z_0-9]+)\}", t))))


# ---------------------------------------------------------------- limits
LIMITS = [
    # id, system, limit, value, unit, note
    ("LIM_NAME_LEN", "Identity", "Shardfall ID display name length", "3-16", "chars", "Letters, digits, one space or underscore; filtered at entry and server-side"),
    ("LIM_NAME_SUFFIX", "Identity", "Discriminator after name", "4", "digits", "Name#1234, shown in friend search and Company roster only"),
    ("LIM_NAME_CHANGE", "Identity", "Name change cooldown", "30", "days", "First change free; forced renames from moderation do not reset the cooldown"),
    ("LIM_FRIENDS", "Friends", "Shardfall cross-play friends", "250", "friends", "Platform friends are separate and uncapped by Shardfall"),
    ("LIM_FRIEND_REQ_OUT", "Friends", "Pending outgoing requests", "50", "requests", ""),
    ("LIM_FRIEND_REQ_IN", "Friends", "Pending incoming requests kept", "100", "requests", "Oldest dropped silently past 100"),
    ("LIM_FRIEND_REQ_EXPIRE", "Friends", "Request expiry", "30", "days", ""),
    ("LIM_FRIEND_REQ_RATE", "Friends", "Requests sent per hour", "20", "per hour", "Anti-spam"),
    ("LIM_BLOCKS", "Safety", "Blocked players", "1000", "players", "Platform block lists are also honored"),
    ("LIM_RECENT", "Friends", "Recent players list", "100", "players", "Kept 14 days"),
    ("LIM_FAVORITES", "Friends", "Favorite friends pinned to top", "20", "friends", ""),
    ("LIM_FT_SIZE", "Fireteam", "Fireteam size", "6", "players", "Activity caps: co-op 4, strike 3, raid 6, arena 3 (PvP is 3v3, Marlon 3 Oct 2026)"),
    ("LIM_FT_INVITE_EXPIRE", "Fireteam", "Invite expiry", "30", "seconds", "Matches MM_COOP_INVITE"),
    ("LIM_FT_INVITE_RATE", "Fireteam", "Invites sent per minute", "10", "per minute", ""),
    ("LIM_FT_IDLE_KICK", "Fireteam", "AFK removal in matchmade activities", "180", "seconds", "No input and no movement; warning at 120 s"),
    ("LIM_FT_VOTE_KICK", "Fireteam", "Vote-kick in matchmade activities", "2 of 3 (strike), 4 of 6 (raid), 2 of 3 (arena team)", "votes", "Once per player per activity; not during boss fights"),
    ("LIM_CO_SIZE", "Company", "Company members", "100", "members", ""),
    ("LIM_CO_PER_ACCOUNT", "Company", "Companies per account", "1", "company", ""),
    ("LIM_CO_NAME", "Company", "Company name length", "3-24", "chars", "Unique per language region; filtered"),
    ("LIM_CO_TAG", "Company", "Company tag length", "2-4", "chars", "Letters and digits; shown as [TAG] after player name"),
    ("LIM_CO_MOTD", "Company", "Message of the day", "280", "chars", "Filtered; edit by Captain and Lieutenants"),
    ("LIM_CO_BIO", "Company", "Finder description", "500", "chars", "Filtered"),
    ("LIM_CO_LIEUTENANTS", "Company", "Lieutenants", "10", "members", ""),
    ("LIM_CO_REQ_PENDING", "Company", "Pending join requests", "50", "requests", "Expire after 7 days"),
    ("LIM_CO_REJOIN", "Company", "Cooldown after leaving before joining another", "24", "hours", "None if removed by the Company"),
    ("LIM_CO_RECRUIT_DAYS", "Company", "Recruit rank duration", "7", "days", "Auto-promotes to Member"),
    ("LIM_CO_CAPTAIN_IDLE", "Company", "Captain inactivity before auto-transfer", "60", "days", "Goes to the most active Lieutenant, else the longest-serving Veteran"),
    ("LIM_CO_CREATE_LEVEL", "Company", "Character level to found a Company", "10", "level", "Free; stops throwaway accounts spamming names"),
    ("LIM_CO_LEVEL_MAX", "Company", "Company level cap", "10", "levels", "Cosmetic rewards only"),
    ("LIM_CO_XP_WEEKLY_PER_MEMBER", "Company", "Company XP one member can add per week", "1000", "XP", "Stops one player carrying the Company"),
    ("LIM_LFG_POSTS", "LFG", "Active posts per player", "1", "post", ""),
    ("LIM_LFG_POST_TTL", "LFG", "Post lifetime", "30", "minutes", "Refresh once to 60; closes when full or when the poster starts the activity"),
    ("LIM_LFG_APPLICANTS", "LFG", "Applicants shown per post", "20", "players", ""),
    ("LIM_LFG_TAGS", "LFG", "Tags per post", "5", "tags", "From the fixed tag list only; no free text"),
    ("LIM_LFG_APPLY_ACTIVE", "LFG", "Open applications per player", "5", "applications", ""),
    ("LIM_CHAT_MSG", "Chat", "Message length", "200", "chars", ""),
    ("LIM_CHAT_RATE", "Chat", "Rate limit", "5 per 10 s", "messages", "6th message starts a 30 s cooldown"),
    ("LIM_CHAT_REPEAT", "Chat", "Identical message repeat block", "30", "seconds", ""),
    ("LIM_CHAT_HISTORY", "Chat", "History kept on screen per channel", "200", "messages", "Server keeps 30 days for reports, then deletes"),
    ("LIM_CHAT_WHISPER_TABS", "Chat", "Open whisper tabs", "8", "tabs", "Oldest closes"),
    ("LIM_CHAT_NEW_ACCOUNT", "Chat", "Hub and arena all-chat locked for new accounts", "2", "hours played", "Fireteam, Company and friend whispers open from the start"),
    ("LIM_CHAT_LINKS", "Chat", "URLs in chat", "0", "", "Links are stripped; item links use the item token"),
    ("LIM_CHAT_ITEM_LINKS", "Chat", "Item links per message", "3", "links", ""),
    ("LIM_PING_RATE", "Chat", "Pings", "3 per 4 s", "pings", "Then 4 s lockout"),
    ("LIM_QUICKCHAT_RATE", "Chat", "Quick-chat lines", "3 per 6 s", "lines", "Then 6 s lockout"),
    ("LIM_EMOTE_SLOTS", "Emotes", "Emote wheel slots", "8 x 2 pages", "slots", ""),
    ("LIM_EMOTE_CD", "Emotes", "Emote cooldown", "2", "seconds", ""),
    ("LIM_EMOTE_COMBAT", "Emotes", "Emotes blocked after damage dealt or taken", "5", "seconds", ""),
    ("LIM_EMOTE_LOOP", "Emotes", "Looping emote max duration", "60", "seconds", "Then returns to idle"),
    ("LIM_VOICE_THRESHOLD", "Voice", "Open-mic gate default", "-40", "dBFS", "Adjustable -60 to -20"),
    ("LIM_REPORTS_DAY", "Safety", "Reports a player can file per day", "20", "reports", "Same target once per 24 h per reason"),
    ("LIM_REPORT_EVIDENCE", "Safety", "Chat log attached to a report", "5 minutes or 50 lines", "", "Whichever is longer, from all channels both players share"),
    ("LIM_TICKETS_OPEN", "Support", "Open tickets per account", "3", "tickets", "Extra tickets merge into the newest open one"),
    ("LIM_ATTACH", "Support", "Ticket attachments", "5 files, 25 MB each", "", "png, jpg, mp4, txt, log, dmp"),
    ("LIM_APPEALS", "Support", "Appeals per penalty", "1", "appeal", "Filed within 30 days of the penalty"),
    ("LIM_SAVE_SNAPSHOTS", "Support", "Cloud save snapshots kept for restore", "10 per character, 30 days", "", "Taken at every Anchor rest, max one per 15 min"),
]
w("limits.csv", ["limit_id", "system", "limit", "value", "unit", "note"], LIMITS)

# ---------------------------------------------------------------- strings
S = []  # (id, screen, text, notes)


def s(i, screen, text, note=""):
    S.append((i, screen, text, note))


SC = "Social menu"
for i, t in [("TITLE", "Social"), ("TAB_FRIENDS", "Friends"), ("TAB_FIRETEAM", "Fireteam"), ("TAB_COMPANY", "Company"),
             ("TAB_RECENT", "Recent"), ("TAB_BLOCKED", "Blocked"), ("TAB_REQUESTS", "Requests ({VAR_n})"),
             ("SEARCH", "Search by Shardfall ID"), ("SEARCH_HINT", "Name#1234"), ("ADD", "Add Friend"),
             ("ONLINE_COUNT", "{VAR_n} Online"), ("PLATFORM_FRIENDS", "Platform Friends"), ("SF_FRIENDS", "Shardfall Friends"),
             ("FAVORITE", "Favorite"), ("UNFAVORITE", "Remove Favorite"), ("REMOVE", "Remove Friend"),
             ("ACCEPT", "Accept"), ("DECLINE", "Decline"), ("CANCEL_REQ", "Cancel Request"), ("SENT", "Request sent."),
             ("PROFILE", "View Profile"), ("INVITE_FT", "Invite to Fireteam"), ("JOIN_GAME", "Join Game"),
             ("WHISPER", "Send Message"), ("INVITE_CO", "Invite to Company"), ("UNBLOCK", "Unblock"),
             ("EMPTY_FRIENDS", "No friends yet. Add someone by their Shardfall ID or invite a player you met."),
             ("EMPTY_RECENT", "Players you meet in co-op, strikes, raids and the Arena appear here for 14 days."),
             ("EMPTY_BLOCKED", "You haven't blocked anyone."), ("EMPTY_REQUESTS", "No pending requests."),
             ("MET_IN", "Met in {VAR_activity}, {VAR_time} ago"), ("CROSSPLAY_ICON_PC", "PC"),
             ("CROSSPLAY_ICON_PS", "PlayStation"), ("CROSSPLAY_ICON_XB", "Xbox"), ("YOUR_ID", "Your Shardfall ID: {VAR_name}"),
             ("COPY_ID", "Copy ID"), ("COPIED", "Copied."), ("SORT", "Sort"), ("SORT_STATUS", "Status"), ("SORT_NAME", "Name"),
             ("SORT_RECENT", "Last Played")]:
    s(f"STR_SOC_{i}", SC, t)
for i, t in [("ONLINE", "Online"), ("IN_ACTIVITY", "In Activity"), ("AWAY", "Away"), ("BUSY", "Do Not Disturb"),
             ("INVISIBLE", "Appear Offline"), ("OFFLINE", "Offline"), ("LAST_SEEN", "Last seen {VAR_time} ago")]:
    s(f"STR_PRES_{i}", "Presence", t, "Away after 10 min idle")
for i, t in [("MENU", "In the menus"), ("REGION", "Exploring {REGION_name}"), ("COOP", "In co-op, {REGION_name} ({VAR_n}/4)"),
             ("CITADEL", "In a Citadel: {VAR_place}"), ("STRIKE", "Strike: {VAR_activity} ({VAR_n}/3)"), ("RAID", "Raid: {VAR_activity}, encounter {VAR_n}"),
             ("ARENA", "Arena: {VAR_mode}, {VAR_score}"), ("HUB", "In Lantern Hold"), ("FORGE", "Building in Forgeframe"),
             ("QUIET", "Aboard the Quiet"), ("JOINABLE", "Joinable"), ("NOT_JOINABLE", "Not joinable")]:
    s(f"STR_RP_{i}", "Rich presence", t, "Shown in friends list and platform overlay")

FT = "Fireteam panel"
for i, t in [("TITLE", "Fireteam"), ("LEADER", "Leader"), ("MAKE_LEADER", "Make Leader"), ("LEAVE", "Leave Fireteam"),
             ("DISBAND", "Disband"), ("PRIVACY", "Fireteam Privacy"), ("PRIV_OPEN", "Open"), ("PRIV_FRIENDS", "Friends Only"),
             ("PRIV_COMPANY", "Friends and Company"), ("PRIV_INVITE", "Invite Only"), ("PRIV_CLOSED", "Closed"),
             ("SLOT_EMPTY", "Empty slot"), ("TOO_BIG", "Your fireteam has {VAR_n}. {VAR_activity} allows {VAR_max}."),
             ("LEVEL_LOW", "{VAR_player} is below the level for {VAR_activity} ({VAR_level})."),
             ("VOTE_KICK", "Vote to Remove"), ("VOTE_KICK_Q", "Remove {VAR_player} from the fireteam?"),
             ("VOTE_YES", "Yes"), ("VOTE_NO", "No"), ("VOTE_PASSED", "{VAR_player} was removed by vote."),
             ("VOTE_FAILED", "The vote did not pass."), ("AFK_WARN", "Move or you'll be removed in {VAR_time}."),
             ("JOIN_REQ", "{VAR_player} wants to join your fireteam."), ("READY_CHECK", "Ready Check"),
             ("READY_Q", "{VAR_player} started a ready check."), ("ALL_READY", "Everyone is ready.")]:
    s(f"STR_FT_{i}", FT, t)

CO = "Company screens"
for i, t in [
    ("TITLE", "Company"), ("FINDER", "Find a Company"), ("CREATE", "Found a Company"), ("NAME", "Company Name"),
    ("TAG", "Tag"), ("BANNER", "Banner"), ("MOTD", "Message of the Day"), ("BIO", "About"), ("ROSTER", "Roster"),
    ("GOALS", "Weekly Goals"), ("REWARDS", "Rewards"), ("SETTINGS", "Settings"), ("LOG", "Activity Log"),
    ("LEVEL", "Company Level {VAR_level}"), ("XP", "{VAR_n} / {VAR_max} XP"), ("MEMBERS", "{VAR_n}/100 Members"),
    ("RANK_CAPTAIN", "Captain"), ("RANK_LIEUTENANT", "Lieutenant"), ("RANK_VETERAN", "Veteran"), ("RANK_MEMBER", "Member"), ("RANK_RECRUIT", "Recruit"),
    ("PROMOTE", "Promote"), ("DEMOTE", "Demote"), ("REMOVE", "Remove from Company"), ("TRANSFER", "Make Captain"),
    ("LEAVE", "Leave Company"), ("DISBAND", "Disband Company"), ("JOIN", "Join"), ("REQUEST", "Request to Join"),
    ("REQUESTED", "Request sent"), ("JOIN_OPEN", "Anyone can join"), ("JOIN_REQUEST", "Players request, officers approve"),
    ("JOIN_INVITE", "Invite only"), ("FILTER_LANG", "Language"), ("FILTER_PLATFORM", "Platform"), ("FILTER_TZ", "Time Zone"),
    ("FILTER_STYLE", "Play Style"), ("FILTER_SIZE", "Size"), ("STYLE_CASUAL", "Casual"), ("STYLE_STORY", "Story and Exploring"),
    ("STYLE_ENDGAME", "Raids and Strikes"), ("STYLE_PVP", "Arena"), ("STYLE_BUILD", "Forgeframe Builders"), ("STYLE_SOCIAL", "Social"),
    ("CROSSPLAY_ONLY", "Cross-play members allowed"), ("MIN_LEVEL", "Minimum Level {VAR_level}"),
    ("NAME_TAKEN", "That name is taken."), ("NAME_BAD", "That name isn't allowed. Try another."),
    ("TAG_BAD", "Tags use 2 to 4 letters or numbers."), ("CREATE_LEVEL", "Reach level 10 to found a Company."),
    ("WELCOME", "Welcome to {VAR_company}."), ("GOAL_PROGRESS", "{VAR_goal}: {VAR_n}/{VAR_max}"),
    ("GOAL_DONE", "Goal complete: {VAR_goal}"), ("REWARD_COSMETIC", "Company rewards are cosmetic. They never change stats."),
    ("CONTRIB", "Your contribution this week: {VAR_n}/1000 XP"), ("LOG_JOINED", "{VAR_player} joined."), ("LOG_LEFT", "{VAR_player} left."),
    ("LOG_REMOVED", "{VAR_player} was removed by {VAR_player2}."), ("LOG_PROMOTED", "{VAR_player} is now {VAR_rank}."),
    ("LOG_GOAL", "Goal complete: {VAR_goal}."), ("LOG_LEVEL", "The Company reached level {VAR_level}."),
    ("LOG_MOTD", "{VAR_player} changed the message of the day."), ("EMPTY_FINDER", "No Companies match. Clear a filter or found your own."),
    ("PERM_INVITE", "Can invite"), ("PERM_APPROVE", "Can approve requests"), ("PERM_REMOVE", "Can remove lower ranks"),
    ("PERM_PROMOTE", "Can promote up to Veteran"), ("PERM_MOTD", "Can edit message of the day"), ("PERM_BANNER", "Can edit banner and settings"),
    ("BANNER_SHAPE", "Shape"), ("BANNER_EMBLEM", "Emblem"), ("BANNER_FIELD", "Field Color"), ("BANNER_TRIM", "Trim Color"), ("BANNER_EMBLEM_COLOR", "Emblem Color"),
    ("REPORT", "Report Company"), ("INACTIVE_TRANSFER", "{VAR_player} is now Captain. The last Captain was away for 60 days.")]:
    s(f"STR_CO_{i}", CO, t)

LF = "Signal Board (LFG)"
for i, t in [
    ("TITLE", "Signal Board"), ("SUB", "Find a fireteam"), ("POST", "Post a Signal"), ("MY_POST", "Your Signal"),
    ("ACTIVITY", "Activity"), ("SLOTS", "Looking for {VAR_n}"), ("MIC", "Mic"), ("MIC_REQ", "Mic required"), ("MIC_PREF", "Mic preferred"),
    ("MIC_NONE", "No mic needed"), ("LANG", "Language"), ("MIN_LEVEL", "Level {VAR_level}+"), ("TAGS", "Tags"),
    ("APPLY", "Signal Back"), ("APPLIED", "Signalled"), ("WITHDRAW", "Withdraw"), ("APPLICANTS", "Applicants ({VAR_n})"),
    ("ACCEPT", "Accept"), ("DECLINE", "Decline"), ("REFRESH", "Refresh Signal"), ("CLOSE", "Close Signal"),
    ("EXPIRES", "Closes in {VAR_time}"), ("FILTERS", "Filters"), ("EMPTY", "No Signals for this activity right now. Post one or try matchmaking."),
    ("FULL", "That fireteam is full."), ("CLOSED", "That Signal has closed."), ("ACCEPTED", "{VAR_player} accepted you. Joining fireteam."),
    ("DECLINED", "Your Signal to {VAR_player} was declined."), ("TRY_MM", "Use Matchmaking Instead"),
    ("CROSSPLAY", "Cross-play"), ("SAME_PLATFORM", "My platform only")]:
    s(f"STR_LFG_{i}", LF, t)
LFG_TAGS = ["First Time", "Teaching", "Experienced", "Fast Run", "Relaxed", "Completion", "Farming", "Challenge", "Triumph Hunting",
            "Melee Build", "Gun Build", "Weave Build", "Need Healer Build", "Lore and Exploring", "Speedrun", "Late Night",
            "Patient", "Checkpoint Run", "Ranked Push", "Practice"]
for n, t in enumerate(LFG_TAGS, 1):
    s(f"STR_LFG_TAG_{n:02d}", LF, t, "Fixed LFG tag")

CH = "Chat"
for i, t in [
    ("TITLE", "Chat"), ("CH_FIRETEAM", "Fireteam"), ("CH_SESSION", "World"), ("CH_TEAM", "Team"), ("CH_ALL", "All"),
    ("CH_COMPANY", "Company"), ("CH_WHISPER", "Whisper"), ("CH_HUB", "Lantern Hold"), ("CH_LFG", "Signal"), ("CH_SYSTEM", "System"),
    ("PROMPT", "Press {BTN_chat} to chat"), ("INPUT_HINT", "Message {VAR_channel}"), ("SEND", "Send"),
    ("TOO_FAST", "Slow down. You can send again in {VAR_time}."), ("REPEAT", "You just sent that."),
    ("FILTERED", "Some words were hidden by your chat filter."), ("MUTED_SELF", "You are muted until {VAR_date}."),
    ("LOCKED_NEW", "This channel opens after 2 hours of play."), ("OFFLINE", "{VAR_player} is offline."),
    ("WHISPER_BLOCKED", "{VAR_player} isn't accepting messages."), ("JOINED", "{VAR_player} joined {VAR_channel}."),
    ("LEFT", "{VAR_player} left {VAR_channel}."), ("LINK_STRIPPED", "Links can't be shared in chat."),
    ("HIDDEN_MSG", "Message hidden. Select to show."), ("HISTORY_CLEARED", "Chat history cleared."),
    ("SPEECH_TO_TEXT", "[voice] {VAR_player}: {VAR_text}"), ("READ_ALOUD", "Read Aloud"),
    ("OPT_SHOW", "Show Chat"), ("OPT_FADE", "Fade After"), ("OPT_SIZE", "Chat Text Size"), ("OPT_OPACITY", "Background Opacity"),
    ("OPT_PROFANITY", "Chat Filter"), ("OPT_FILTER_OFF", "Off (slurs always hidden)"), ("OPT_FILTER_STD", "Standard"),
    ("OPT_FILTER_STRICT", "Strict"), ("OPT_TTS", "Read Chat Aloud"), ("OPT_STT", "Show Voice as Text"),
    ("OPT_TIMESTAMPS", "Timestamps"), ("OPT_ALLCHAT", "Arena All-Chat"), ("OPT_HUBCHAT", "Lantern Hold Chat"),
    ("OPT_WHISPERS", "Whispers From"), ("OPT_WHISPER_ALL", "Anyone"), ("OPT_WHISPER_FRIENDS", "Friends and Company"),
    ("OPT_WHISPER_NONE", "No One"), ("CTX_WHISPER", "Whisper"), ("CTX_PROFILE", "View Profile"), ("CTX_INVITE", "Invite to Fireteam"),
    ("CTX_ADD", "Add Friend"), ("CTX_MUTE", "Mute"), ("CTX_BLOCK", "Block"), ("CTX_REPORT", "Report"), ("CTX_COPY", "Copy Text")]:
    s(f"STR_CHAT_{i}", CH, t)

QC = [("HELLO", "Hello!"), ("THANKS", "Thanks!"), ("GG", "Good game."), ("SORRY", "Sorry!"), ("YES", "Yes."), ("NO", "No."),
      ("WAIT", "Wait for me."), ("GO", "Let's go."), ("FOLLOW", "Follow me."), ("REGROUP", "Regroup on me."),
      ("HELP", "I need help!"), ("REVIVE", "Revive me!"), ("WARD_DOWN", "My Ward is down."), ("NO_TONIC", "I'm out of Tonics."),
      ("SURGE_READY", "My Surge is ready."), ("SURGE_NOW", "Use Surge now!"), ("FOCUS", "Focus this target."),
      ("BREAK_STANCE", "Break its stance!"), ("ADDS", "Clear the adds."), ("BOSS", "Boss incoming."),
      ("ANCHOR", "Rest at the Anchor?"), ("LOOT", "Loot here."), ("SHORTCUT", "Shortcut here."), ("CAREFUL", "Careful. Trap."),
      ("HOLD", "Hold this position."), ("PUSH", "Push now."), ("FALL_BACK", "Fall back."), ("POWER_WEAPON", "Power weapon is up."),
      ("FLAG", "Defend the objective."), ("NICE", "Nice!"), ("AFK", "Be right back."), ("BACK", "I'm back.")]
for i, t in QC:
    s(f"STR_QC_{i}", "Quick chat wheel", t, "Auto-localized to each reader's language")
PG = [("HERE", "Here"), ("ENEMY", "Enemy"), ("ENEMY_ELITE", "Elite"), ("ITEM", "{ITM_name}"), ("AMMO", "Ammo here"),
      ("DANGER", "Danger"), ("GO_HERE", "Go here"), ("WATCH", "Watching here"), ("ANCHOR", "Anchor"), ("NOTE", "Shard-note"),
      ("CANCEL", "Cancelled ping")]
for i, t in PG:
    s(f"STR_PING_{i}", "Pings", t, "World marker label, lasts 8 s (enemy 5 s, follows target)")

EM = "Emote wheel"
for i, t in [("TITLE", "Emotes"), ("EQUIP", "Equip to Wheel"), ("UNEQUIP", "Remove"), ("PAGE", "Page {VAR_n}/2"),
             ("LOCKED", "Locked"), ("UNLOCK_QUEST", "Unlock: {VAR_source}"), ("UNLOCK_SHOP", "Wardrobe Shop"),
             ("IN_COMBAT", "Can't emote in combat."), ("COOLDOWN", "Wait a moment."), ("PREVIEW", "Preview"),
             ("FAV", "Favorites"), ("ALL", "All Emotes"), ("NEW", "New"), ("SYNC_INVITE", "{VAR_player} wants to {VAR_emote} with you."),
             ("SYNC_ACCEPT", "Join In"), ("HIDE_OTHERS", "Hide Other Players' Emotes")]:
    s(f"STR_EMW_{i}", EM, t)

PV = "Privacy and online options"
for i, t in [("TITLE", "Online and Privacy"), ("CROSSPLAY", "Cross-play"), ("CROSSPLAY_D", "Play with people on other platforms. Turning this off may make matchmaking slower."),
             ("CROSSPLAY_INPUT", "Arena: Controller Lobbies Only"), ("CROSSPLAY_INPUT_D", "Console only. Keeps mouse-and-keyboard players out of your Arena matches."),
             ("JOIN_FROM", "Who Can Join Your Game"), ("INVITE_FROM", "Who Can Invite You"), ("FRIEND_REQ_FROM", "Who Can Send Friend Requests"),
             ("OPT_ANYONE", "Anyone"), ("OPT_FRIENDS", "Friends"), ("OPT_FRIENDS_CO", "Friends and Company"), ("OPT_NOONE", "No One"),
             ("SHOW_PLATFORM", "Show My Platform"), ("SHOW_ONLINE", "Show When I'm Online"), ("STREAMER", "Streamer Mode"),
             ("STREAMER_D", "Hides other players' names, your Shardfall ID and Company tags on screen. Licensed music only."),
             ("ANON", "Kindred {VAR_n}"), ("VOICE_DEFAULT", "Voice Chat Default"), ("VOICE_PTT", "Push to Talk"), ("VOICE_OPEN", "Open Mic"),
             ("VOICE_OFF", "Off"), ("VOICE_GATE", "Open Mic Threshold"), ("VOICE_IN", "Incoming Voice"), ("VOICE_IN_ALL", "Everyone"),
             ("VOICE_IN_FRIENDS", "Friends and Fireteam"), ("VOICE_IN_NONE", "No One"), ("VOICE_VOL", "Voice Volume"),
             ("SPEAKING", "{VAR_player} is speaking"), ("MIC_MUTED", "Your mic is muted."), ("SHARD_NOTES", "Show Shard-notes"),
             ("DEATH_ECHOES", "Show Death Echoes"), ("GHOSTS", "Show Ghost Glimpses"), ("PARENTAL", "Some options are set by platform parental controls.")]:
    s(f"STR_PRIV_{i}", PV, t)

SF = "Report and safety"
for i, t in [("TITLE", "Report {VAR_player}"), ("WHY", "What happened?"), ("DETAILS", "Add details (optional)"),
             ("EVIDENCE", "Recent chat with this player is attached automatically."), ("BLOCK_TOO", "Also block this player"),
             ("SUBMIT", "Send Report"), ("THANKS", "Thanks. We'll review it. You'll hear back if we act."),
             ("ACTED", "A player you reported has been penalized. Thank you."), ("DUPLICATE", "You already reported this player for this today."),
             ("LIMIT", "You've reached today's report limit."), ("MUTE_T", "Mute {VAR_player}"), ("MUTE_VOICE", "Mute Voice"), ("MUTE_TEXT", "Mute Text"),
             ("MUTE_EMOTES", "Hide Emotes"), ("BLOCK_D", "Blocked players can't invite you, message you, join your game or match into your fireteam where possible."),
             ("BLOCK_MATCH_NOTE", "Blocked players can still be matched into Arena on the other team."),
             ("PENALTY_WARN", "Warning: a report about your {VAR_reason} was upheld. Next time your account will be restricted."),
             ("PENALTY_MUTE", "Chat restricted until {VAR_date}: {VAR_reason}."), ("PENALTY_COMM", "Chat and voice restricted until {VAR_date}: {VAR_reason}."),
             ("PENALTY_SUSPEND", "Online play suspended until {VAR_date}: {VAR_reason}."), ("PENALTY_PERM", "Online play permanently disabled: {VAR_reason}."),
             ("PENALTY_RENAME", "Your {VAR_field} broke the Code of Conduct and was reset. Choose a new one."),
             ("PENALTY_MATCH", "Matchmaking cooldown: {VAR_time}. You left {VAR_n} matches early."),
             ("APPEAL", "Appeal This"), ("CODE_OF_CONDUCT", "Code of Conduct"), ("CRISIS", "If you or someone else is in danger, contact local emergency services now. Support resources: {VAR_url}")]:
    s(f"STR_SAFE_{i}", SF, t)
REPORT_REASONS = [
    ("RR_HATE", "Hate speech or slurs", "Chat, voice, name, Company, LFG", 1),
    ("RR_HARASS", "Harassment or bullying", "Chat, voice, emotes, whispers", 2),
    ("RR_THREAT", "Threats of violence", "Chat, voice", 1),
    ("RR_SELFHARM", "Self-harm or suicide risk", "Chat, voice", 1),
    ("RR_SEXUAL", "Sexual content", "Chat, voice, name, Forgeframe", 1),
    ("RR_MINOR", "Child safety", "Any", 1),
    ("RR_CHEAT", "Cheating or exploits", "Gameplay", 2),
    ("RR_GRIEF", "Griefing or throwing", "Strikes, raids, Arena", 3),
    ("RR_AFK", "AFK or leeching", "Strikes, raids, Arena", 4),
    ("RR_SPAM", "Spam or advertising", "Chat, LFG, whispers", 3),
    ("RR_SCAM", "Scam, phishing or account selling", "Chat, whispers", 2),
    ("RR_NAME", "Offensive name", "Shardfall ID, Company name or tag", 3),
    ("RR_IMPERSONATE", "Pretending to be staff", "Chat, name", 2),
    ("RR_PERSONAL", "Sharing someone's personal info", "Chat, voice", 1),
    ("RR_OTHER", "Something else", "Any", 4),
]
for rid, t, *_ in REPORT_REASONS:
    s(f"STR_SAFE_{rid}", SF, t, "Report reason")

SU = "Help and support"
for i, t in [("TITLE", "Help and Support"), ("KB", "Help Articles"), ("CONTACT", "Contact Support"), ("MY_TICKETS", "My Tickets"),
             ("REPORT_PROBLEM", "Report a Problem"), ("SERVER_STATUS", "Server Status"), ("STATUS_OK", "All services running."),
             ("STATUS_DEGRADED", "{VAR_service} is having problems. We're on it."), ("STATUS_DOWN", "{VAR_service} is down. Started {VAR_time} ago."),
             ("CATEGORY", "What do you need help with?"), ("SUBCATEGORY", "Tell us more"), ("DESCRIBE", "Describe what happened"),
             ("ATTACH", "Attach Screenshot or Clip"), ("SYSINFO", "Include build, platform and session ID (recommended)"),
             ("SUBMIT", "Submit Ticket"), ("SUBMITTED", "Ticket {VAR_id} sent. We usually reply within {VAR_time}."),
             ("STATE_NEW", "Received"), ("STATE_OPEN", "Being worked on"), ("STATE_PENDING", "Waiting for you"), ("STATE_SOLVED", "Solved"),
             ("STATE_CLOSED", "Closed"), ("REPLY", "Reply"), ("REOPEN", "Reopen"), ("RATE", "How did we do?"),
             ("RATE_GOOD", "Good"), ("RATE_BAD", "Not good"), ("NEW_REPLY", "Support replied to ticket {VAR_id}."),
             ("APPEAL_TITLE", "Appeal a Penalty"), ("APPEAL_PENALTY", "Penalty: {VAR_reason}, {VAR_date}"),
             ("APPEAL_WHY", "Why should we review this?"), ("APPEAL_SENT", "Appeal sent. We reply within 7 days."),
             ("APPEAL_UPHELD", "We reviewed your appeal. The penalty stands."), ("APPEAL_REDUCED", "We reviewed your appeal and shortened the penalty to {VAR_date}."),
             ("APPEAL_OVERTURNED", "We reviewed your appeal and removed the penalty. Anything it took has been restored."),
             ("APPEAL_USED", "You've already appealed this penalty."), ("APPEAL_LATE", "Appeals must be sent within 30 days."),
             ("REFUND_PLATFORM", "Purchases are refunded by {VAR_platform}. Open their refund page?"),
             ("PURCHASE_MISSING", "Missing a purchase? Restore Purchases first."), ("RESTORE", "Restore Purchases"),
             ("RESTORED", "{VAR_n} purchases restored."), ("RESTORED_NONE", "Everything you bought is already here."),
             ("SAVE_RESTORE", "Restore a Cloud Save"), ("SAVE_LIST", "{VAR_character}, {VAR_place}, {VAR_date}"),
             ("SAVE_RESTORE_Q", "Replace your current save with this one? Your current save is kept as a backup for 30 days."),
             ("DATA_REQUEST", "Download or Delete My Data"), ("DATA_EXPORT", "Request My Data"), ("DATA_DELETE", "Delete My Account"),
             ("DATA_DELETE_Q", "This deletes your Shardfall account data on every platform after 30 days. Your platform purchases stay with your platform account."),
             ("LINKED", "Linked Accounts"), ("LINK", "Link Account"), ("UNLINK", "Unlink"), ("UNLINK_COOLDOWN", "You can link a different account in {VAR_time}."),
             ("OFFLINE", "Can't reach support right now. Visit {VAR_url} or try again later."), ("CRASH_LINK", "We found a crash report from your last session. Attach it?")]:
    s(f"STR_SUP_{i}", SU, t)

# ---------------------------------------------------------------- popups
P = []  # popup_id,kind,screen,layer,trigger,title_str,body_str,buttons,duration_s,dismiss,priority,queue_rule,sfx_hook
TOAST = ("toast", "HUD", "HUD notification feed, top right", "3.0", "Auto", "Queue max 4 visible; newer push older up; same ID within 2 s merges count")
MODAL = ("modal", "Various", "Modal dialog over current screen", "Until input", "Button press", "Blocks input; does not pause online play")
ERR = ("error", "Various", "Modal dialog, red rule", "Until input", "Button press", "Blocks input; replaces any modal of lower priority")
INL = ("inline", "Various", "Inline under the field", "4.0", "Auto or next input", "Replaces previous inline")
PRM = ("prompt", "HUD", "HUD prompt, lower centre", "10.0", "Button press or timeout", "One at a time; newer waits")


def pop(pid, base, trig, title, body, buttons, prio, sfx, dur=None):
    kind, screen, layer, d, dis, q = base
    P.append((pid, kind, screen, layer, trig, title, body, buttons, dur or d, dis, prio, q, sfx))


def ps(pid, base, trig, title_text, body_text, buttons, prio, sfx, dur=None):
    t = f"STR_{pid}_T" if title_text else ""
    b = f"STR_{pid}_B" if body_text else ""
    if title_text:
        s(t, "Popups", title_text, f"{base[0]} title")
    if body_text:
        s(b, "Popups", body_text, f"{base[0]} body")
    pop(pid, base, trig, t, b, buttons, prio, sfx, dur)


ps("NTF_FRIEND_REQ", TOAST, "Friend request received (not while DND)", "{VAR_player} sent a friend request.", "", "", 2, "SFX_UI_SOC_REQUEST")
ps("NTF_FRIEND_ACCEPT", TOAST, "Your request accepted", "{VAR_player} is now your friend.", "", "", 2, "SFX_UI_SOC_ACCEPT")
ps("NTF_FRIEND_ONLINE", TOAST, "Favorite friend comes online (option, default on for favorites)", "{VAR_player} is online.", "", "", 1, "SFX_UI_SOC_ONLINE")
ps("NTF_FT_JOIN", TOAST, "Player joins fireteam", "{VAR_player} joined the fireteam.", "", "", 2, "SFX_UI_SOC_JOIN")
ps("NTF_FT_LEAVE", TOAST, "Player leaves fireteam", "{VAR_player} left the fireteam.", "", "", 2, "SFX_UI_SOC_LEAVE")
ps("NTF_FT_LEADER", TOAST, "Leader changes", "{VAR_player} now leads the fireteam.", "", "", 2, "SFX_UI_TOAST")
ps("NTF_CO_JOIN", TOAST, "Member joins your Company", "{VAR_player} joined {VAR_company}.", "", "", 1, "SFX_UI_SOC_JOIN")
ps("NTF_CO_GOAL", TOAST, "Weekly Company goal completed", "Company goal complete: {VAR_goal}", "", "", 3, "SFX_UI_SOC_GOAL", "5.0")
ps("NTF_CO_LEVEL", TOAST, "Company levels up", "{VAR_company} reached level {VAR_level}.", "Collect your reward at the Company screen.", "", 3, "SFX_UI_SOC_LEVEL", "5.0")
ps("NTF_CO_REQ", TOAST, "Join request arrives (officers only)", "{VAR_player} asked to join your Company.", "", "", 2, "SFX_UI_SOC_REQUEST")
ps("NTF_CO_PROMOTED", TOAST, "You are promoted or demoted", "You are now {VAR_rank} in {VAR_company}.", "", "", 2, "SFX_UI_TOAST")
ps("NTF_LFG_APPLICANT", TOAST, "Someone answers your Signal", "{VAR_player} signalled back.", "", "", 2, "SFX_UI_SOC_REQUEST")
ps("NTF_LFG_EXPIRING", TOAST, "Your Signal has 2 min left", "Your Signal closes in 2 minutes.", "", "", 1, "SFX_UI_TOAST")
ps("NTF_WHISPER", TOAST, "Whisper received while chat hidden", "Message from {VAR_player}", "", "", 2, "SFX_UI_CHAT_WHISPER")
ps("NTF_REPORT_ACTED", TOAST, "A player you reported was penalized (next login)", "Thanks for your report.", "We took action on a player you reported.", "", 2, "SFX_UI_TOAST", "5.0")
ps("NTF_TICKET_REPLY", TOAST, "Support reply (next login or live)", "Support replied to your ticket.", "", "", 3, "SFX_UI_TOAST", "5.0")
ps("PRM_FT_INVITE", PRM, "Fireteam invite received", "{VAR_player} invited you to their fireteam.", "{VAR_activity}", "Join / Decline", 4, "SFX_UI_SOC_INVITE", "30.0")
ps("PRM_FT_JOIN_REQ", PRM, "Someone asks to join your fireteam", "{VAR_player} wants to join.", "", "Accept / Decline", 4, "SFX_UI_SOC_REQUEST", "30.0")
ps("PRM_CO_INVITE", PRM, "Company invite received", "{VAR_player} invited you to {VAR_company}.", "", "View / Decline", 3, "SFX_UI_SOC_INVITE", "30.0")
ps("PRM_READY_CHECK", PRM, "Ready check started", "Ready check", "{VAR_player} asked if everyone is ready.", "Ready / Not Ready", 4, "SFX_UI_SOC_READY", "20.0")
ps("PRM_VOTE_KICK", PRM, "Vote-kick started", "Vote to remove {VAR_player}?", "", "Yes / No", 4, "SFX_UI_SOC_VOTE", "20.0")
ps("PRM_EMOTE_SYNC", PRM, "Paired emote offered within 3 m", "{VAR_player} wants to {VAR_emote}.", "", "Join In", 2, "SFX_UI_TOAST", "8.0")
ps("PRM_AFK", PRM, "No input for 120 s in a matchmade activity", "Are you there?", "You'll be removed in {VAR_time}.", "I'm Here", 5, "SFX_UI_WARN", "60.0")
ps("CNF_REMOVE_FRIEND", MODAL, "Remove friend", "Remove Friend", "Remove {VAR_player} from your friends?", "Remove / Cancel", 5, "SFX_UI_CONFIRM")
ps("CNF_BLOCK", MODAL, "Block player", "Block {VAR_player}?", "They won't be able to invite, message or join you. They aren't told.", "Block / Cancel", 5, "SFX_UI_CONFIRM")
ps("CNF_LEAVE_FT", MODAL, "Leave fireteam during an activity", "Leave Fireteam", "You'll also leave {VAR_activity}.", "Leave / Stay", 5, "SFX_UI_CONFIRM")
ps("CNF_CO_LEAVE", MODAL, "Leave Company", "Leave {VAR_company}?", "You can't join another Company for 24 hours.", "Leave / Cancel", 5, "SFX_UI_CONFIRM")
ps("CNF_CO_DISBAND", MODAL, "Captain disbands Company", "Disband {VAR_company}?", "Every member is removed and the name is freed after 30 days. This can't be undone. Type the Company tag to confirm.", "Disband / Cancel", 6, "SFX_UI_WARN")
ps("CNF_CO_TRANSFER", MODAL, "Captain transfers captaincy", "Make {VAR_player} Captain?", "You'll become a Lieutenant.", "Confirm / Cancel", 5, "SFX_UI_CONFIRM")
ps("CNF_CO_REMOVE", MODAL, "Officer removes member", "Remove {VAR_player}?", "They can join another Company right away.", "Remove / Cancel", 5, "SFX_UI_CONFIRM")
ps("CNF_CROSSPLAY_OFF", MODAL, "Turn cross-play off", "Turn Off Cross-play?", "You'll only match with players on your platform, and cross-play friends will appear offline.", "Turn Off / Cancel", 5, "SFX_UI_CONFIRM")
ps("CNF_REPORT", MODAL, "Send report", "Send Report?", "False reports can lead to penalties on your account.", "Send / Cancel", 5, "SFX_UI_CONFIRM")
ps("CNF_SAVE_RESTORE", MODAL, "Restore cloud save", "Restore This Save?", "Your current save is kept as a backup for 30 days.", "Restore / Cancel", 6, "SFX_UI_WARN")
ps("CNF_DELETE_ACCOUNT", MODAL, "Request account deletion", "Delete Your Account?", "Deletion finishes after 30 days. Sign in before then to cancel.", "Delete / Cancel", 6, "SFX_UI_WARN")
ps("CNF_UNLINK", MODAL, "Unlink a platform account", "Unlink {VAR_platform}?", "Progress stays with your Shardfall account. You can't link a different {VAR_platform} account for 30 days.", "Unlink / Cancel", 6, "SFX_UI_WARN")
ps("CNF_EXTERNAL_LINK", MODAL, "Open a support web page", "Leave the Game?", "This opens {VAR_url} in your browser or platform overlay.", "Open / Cancel", 4, "SFX_UI_CONFIRM")
for code, title, body, trig in [
    ("FRIEND_LIMIT", "Friends List Full", "You have 250 Shardfall friends. Remove one to add more.", "Add friend at cap"),
    ("FRIEND_NOT_FOUND", "Player Not Found", "No player has the ID {VAR_name}. Check the 4 digits after the #.", "Search miss"),
    ("FRIEND_PRIVACY", "Can't Send Request", "This player isn't accepting friend requests.", "Target privacy"),
    ("CROSSPLAY_OFF", "Cross-play Is Off", "{VAR_player} plays on another platform. Turn on cross-play to play together.", "Invite or join across platforms with cross-play off"),
    ("FT_FULL", "Fireteam Full", "That fireteam is full.", "Join full fireteam"),
    ("FT_TOO_BIG", "Fireteam Too Large", "{VAR_activity} allows {VAR_max} players. Your fireteam has {VAR_n}.", "Launch activity over size"),
    ("FT_PRIVACY", "Can't Join", "That fireteam is closed.", "Join closed fireteam"),
    ("FT_BLOCKED", "Can't Join", "You can't join this player.", "Join player who blocked you (reason not shown)"),
    ("CO_FULL", "Company Full", "{VAR_company} has 100 members.", "Join full Company"),
    ("CO_COOLDOWN", "Can't Join Yet", "You left a Company recently. You can join another in {VAR_time}.", "Join within 24 h of leaving"),
    ("CO_ALREADY", "Already in a Company", "Leave {VAR_company} before joining another.", "Join while member"),
    ("CHAT_RESTRICTED", "Chat Restricted", "Your chat is restricted until {VAR_date}.", "Send while muted by moderation"),
    ("UGC_PARENTAL", "Blocked by Parental Controls", "Your platform settings don't allow chat or player content.", "Platform parental control"),
    ("PLATFORM_PRIVILEGE", "Online Not Available", "Your platform account doesn't have online play. {VAR_platform} membership may be needed.", "Missing PS Plus or Game Pass Core for online"),
    ("SUPPORT_OFFLINE", "Support Unavailable", "We can't reach support right now. Try again later or visit {VAR_url}.", "Support service down"),
    ("TICKET_LIMIT", "Too Many Open Tickets", "You have 3 open tickets. Reply to one of them instead.", "4th ticket"),
    ("SUSPENDED", "Online Play Suspended", "Online play is suspended until {VAR_date}. Reason: {VAR_reason}. You can still play solo offline.", "Login with active suspension"),
    ("PERM_BAN", "Online Play Disabled", "Online play is permanently disabled on this account. Reason: {VAR_reason}. You can still play solo offline.", "Login with permanent ban"),
    ("MM_COOLDOWN", "Matchmaking Cooldown", "You left too many matches early. You can queue again in {VAR_time}.", "Queue with leaver penalty"),
]:
    ps(f"ERR_{code}", ERR, trig, title, body, "OK", 6, "SFX_UI_ERROR")
for code, text, trig in [
    ("NAME_TAKEN", "That name is taken.", "Company or ID name in use"),
    ("NAME_FILTER", "That name isn't allowed.", "Name fails filter"),
    ("NAME_COOLDOWN", "You can change your name again in {VAR_time}.", "Rename during cooldown"),
    ("CHAT_SLOW", "Slow down. Try again in {VAR_time}.", "Chat rate limit"),
    ("CHAT_LOCKED", "This channel opens after 2 hours of play.", "New account in hub or all-chat"),
    ("REPORT_DUP", "You already reported this player for this today.", "Duplicate report"),
    ("EMOTE_COMBAT", "Can't emote in combat.", "Emote within 5 s of damage"),
    ("LFG_ONE_POST", "Close your current Signal to post a new one.", "Second LFG post"),
]:
    ps(f"INL_{code}", INL, trig, text, "", "", 3, "SFX_UI_DENY")

# ---------------------------------------------------------------- write strings + popups
w("strings_social.csv", ["str_id", "screen", "text_en", "max_chars", "tokens", "notes"],
  [(i, sc, t, mc(t), toks(t), n) for i, sc, t, n in S])
w("popups_social.csv", ["popup_id", "kind", "screen", "layer", "trigger", "title_str", "body_str", "buttons", "duration_s",
                        "dismiss", "priority", "queue_rule", "sfx_hook"], P)

# ---------------------------------------------------------------- screens
SCREENS = [
    # screen_id, name, opened_from, layout, elements, input_notes, ui_hook
    ("SCR_SOC_HOME", "Social menu", "Pause menu > Social; {BTN_social} (View/Touchpad hold) anywhere", "Full-screen panel, left tabs, right detail card",
     "Tabs Friends / Fireteam / Company / Recent / Blocked / Requests; search bar; your ID with Copy; online count; list rows (avatar, name, [TAG], platform icon, presence, rich presence line); detail card with actions",
     "LB/RB switch tabs; A open card; X invite; Y whisper; hold B close", "UI_SCR_SOC_HOME"),
    ("SCR_SOC_PROFILE", "Player card", "Any player name (list, chat, roster, HUD nameplate)", "Side card 520 px wide",
     "Name#1234, Company tag and banner, character level, Origin crest, title, 3 showcased Triumphs, met-in line, platform icon; actions Add / Invite / Join / Whisper / Mute / Block / Report",
     "Report and Block always last two buttons", "UI_CARD_PLAYER"),
    ("SCR_SOC_RECENT", "Recent players", "Social > Recent", "List",
     "Last 100 players, 14 days; activity and time met; actions Add, Invite, Report, Block", "", "UI_SCR_SOC_RECENT"),
    ("SCR_SOC_BLOCKED", "Blocked list", "Social > Blocked", "List", "Name, date blocked, Unblock", "Platform-blocked players listed greyed with 'Blocked on {VAR_platform}'", "UI_SCR_SOC_BLOCKED"),
    ("SCR_FT_PANEL", "Fireteam panel", "Social > Fireteam; d-pad left hold in hub", "Card stack, 6 slots",
     "Slot per member (name, level, Origin, mic state, ready state, leader crown); privacy dropdown; Ready Check; Leave; leader actions Make Leader, Remove",
     "Remove only for leader outside matchmade activities; vote-kick inside them", "UI_PANEL_FIRETEAM"),
    ("SCR_FT_HUD", "Fireteam HUD strip", "Always in a fireteam", "Top-left strip under Ward bar",
     "Per member: name, Health/Ward bars, Surge ready pip, downed icon, speaking icon, distance in m when off screen", "Hidden in Photo Mode and Streamer Mode names", "UI_HUD_FIRETEAM"),
    ("SCR_CO_HOME", "Company home", "Social > Company; Company Steward NPC in Lantern Hold", "Full-screen; banner left, tabs right",
     "Tabs Overview (MOTD, level bar, weekly goals, your contribution) / Roster / Rewards / Log / Settings", "", "UI_SCR_CO_HOME"),
    ("SCR_CO_ROSTER", "Company roster", "Company > Roster", "Sortable table",
     "Name, rank, level, last online, weekly XP, join date; filters Online / Rank; officer actions per row", "", "UI_SCR_CO_ROSTER"),
    ("SCR_CO_FINDER", "Company finder", "Company tab when not in a Company", "Grid of cards with filter rail",
     "Filters language, platform, time zone, play style, size, join mode, min level; card shows banner, name, tag, members, level, style, join button", "", "UI_SCR_CO_FINDER"),
    ("SCR_CO_CREATE", "Found a Company", "Finder > Found a Company", "3-step wizard",
     "1 Name and tag (live availability and filter check), 2 Banner builder (shape, emblem, field, trim, emblem colors), 3 Join mode, style, language, about; Confirm", "", "UI_SCR_CO_CREATE"),
    ("SCR_CO_BANNER", "Banner builder", "Create step 2; Settings > Banner", "Live 3D banner preview left, pickers right",
     "12 shapes, 60 emblems (40 at start, 20 from Company levels), 24 colors from the dye palette", "Banner shows on the Company hall pennant, cape slot and player card", "UI_SCR_CO_BANNER"),
    ("SCR_CO_SETTINGS", "Company settings", "Company > Settings (officers)", "Form",
     "Join mode, min level, language, style tags, cross-play members, MOTD, about, rank permissions grid, disband", "", "UI_SCR_CO_SETTINGS"),
    ("SCR_LFG_BOARD", "Signal Board", "Lantern Hold Signal Board object; Director > any activity > Find Fireteam", "Left activity tree, centre post list, right post detail",
     "Activity filter tree (campaign co-op, Citadel, strike, Hollowed Citadel, raid by encounter, Arena), filters (mic, language, platform, min level, tags), post rows (poster, activity, slots, tags, mic, language, time left), Signal Back",
     "Free text not allowed: tags and fixed fields only", "UI_SCR_LFG_BOARD"),
    ("SCR_LFG_POST", "Post a Signal", "Signal Board > Post", "Modal form",
     "Activity, slots wanted (auto from activity size minus fireteam), mic, language, min level, up to 5 tags, cross-play toggle", "", "UI_SCR_LFG_POST"),
    ("SCR_CHAT_HUD", "Chat window", "{BTN_chat} (Enter on PC, d-pad up hold or on-screen keyboard on console)", "Bottom-left, 480 x 220 px at 100% scale, fades after 10 s",
     "Channel tabs, message list with timestamps (option), input line with channel prefix, item link chips", "Commands: /f fireteam, /w name whisper, /c Company, /t team, /a all, /h hub, /r reply", "UI_HUD_CHAT"),
    ("SCR_QUICKCHAT", "Quick chat wheel", "Hold {BTN_quickchat} (d-pad right hold; T on PC)", "Radial, 8 slots x 4 pages",
     "32 preset lines (STR_QC_*), customizable slots", "Lines arrive translated into each reader's language", "UI_WHEEL_QUICKCHAT"),
    ("SCR_PING", "Ping", "Tap {BTN_ping} (d-pad up tap; middle mouse)", "World marker plus HUD edge arrow",
     "Contextual: enemy, item, Anchor, location; double tap = danger; hold = ping wheel", "", "UI_HUD_PING"),
    ("SCR_EMOTE_WHEEL", "Emote wheel", "Hold {BTN_emote} (d-pad down hold; B on PC)", "Radial, 8 slots x 2 pages",
     "Equipped emotes with icons; centre shows name; locked slots greyed", "Edit in Wardrobe > Emotes", "UI_WHEEL_EMOTE"),
    ("SCR_EMOTE_COLLECTION", "Emote collection", "Wardrobe > Emotes", "Grid with preview",
     "All emotes, owned and locked with source line, preview on character, equip to slot", "", "UI_SCR_EMOTES"),
    ("SCR_VOICE_HUD", "Voice indicators", "Voice chat active", "Speaker icons in Fireteam HUD strip; your mic icon bottom-left",
     "Speaking, muted by you, mic off, push-to-talk held", "Speech-to-text lines go to chat with a [voice] prefix", "UI_HUD_VOICE"),
    ("SCR_PRIVACY", "Online and Privacy options", "Options > Online and Privacy", "Options list",
     "Cross-play, controller-only Arena (console), who can join / invite / friend-request / whisper, show platform, show online, Streamer Mode, voice default and gate, incoming voice, chat filter, Shard-notes and echoes toggles",
     "Platform parental controls override and grey out options", "UI_SCR_PRIVACY"),
    ("SCR_REPORT", "Report a player", "Player card > Report; chat context menu; post-activity screen", "Modal, 2 steps",
     "1 Reason list (15 reasons), 2 optional details (300 chars, filtered) and Also block; evidence note", "", "UI_SCR_REPORT"),
    ("SCR_PENALTY", "Penalty notice", "Login or live when a penalty starts", "Modal, red rule",
     "Penalty type, reason, end date or permanent, what still works (solo offline always), Appeal and Code of Conduct buttons", "", "UI_SCR_PENALTY"),
    ("SCR_SUP_HOME", "Help and Support", "Pause > Help; title screen > Help", "Full-screen list",
     "Server Status banner, Help Articles (searchable, offline cache of top 40), Contact Support, My Tickets, Restore Purchases, Restore Cloud Save, Appeal a Penalty, Linked Accounts, Download or Delete My Data", "", "UI_SCR_SUP_HOME"),
    ("SCR_SUP_TICKET", "New ticket", "Help > Contact Support; Report a Problem", "3-step form",
     "1 Category, 2 Subcategory with suggested articles (deflection), 3 Description (2,000 chars), attachments, system info toggle; Submit", "", "UI_SCR_SUP_TICKET"),
    ("SCR_SUP_MYTICKETS", "My tickets", "Help > My Tickets", "List and thread view",
     "Ticket ID, category, state, last update; thread with replies; Reply, Reopen within 14 days of solved, rating", "", "UI_SCR_SUP_MYTICKETS"),
    ("SCR_SUP_SAVE", "Restore cloud save", "Help > Restore Cloud Save", "List", "Up to 10 snapshots per character: character, place, date, play time; Restore", "Self-serve; tier 2 can restore older backups", "UI_SCR_SUP_SAVE"),
    ("SCR_SUP_APPEAL", "Appeal a penalty", "Penalty notice > Appeal; Help > Appeal", "Form", "Penalty picker, reason (1,000 chars), Submit; status line", "", "UI_SCR_SUP_APPEAL"),
    ("SCR_SUP_ACCOUNTS", "Linked accounts", "Help > Linked Accounts", "List", "Steam, PlayStation, Xbox, Epic link state; Link / Unlink with 30-day relink cooldown", "", "UI_SCR_SUP_ACCOUNTS"),
    ("SCR_SUP_STATUS", "Server status", "Help home banner; title screen banner when degraded", "Banner plus detail list",
     "Per service: Sign-in, Co-op relay, Matchmaking, Raids, Arena, Shop, Shard-notes, Support; state and start time", "Fed by live config (tech/02-online.md)", "UI_SCR_SUP_STATUS"),
]
w("screens.csv", ["screen_id", "name", "opened_from", "layout", "elements", "input_notes", "ui_hook"], SCREENS)

# ---------------------------------------------------------------- chat channels
CHANNELS = [
    # id, name_str, who, default_on, voice, persistence, filter_floor, notes
    ("CHN_FIRETEAM", "STR_CHAT_CH_FIRETEAM", "Fireteam members (1-6)", "On", "Yes, default push-to-talk on PC, open mic on console", "Session only", "Player setting", "Survives activity changes"),
    ("CHN_SESSION", "STR_CHAT_CH_SESSION", "The host's co-op world (1-4), host team only", "On", "Shares fireteam voice when same fireteam", "Session only", "Player setting", "Invaders get no chat, only emotes and pings (Shardfall choice, limits harassment)"),
    ("CHN_TEAM", "STR_CHAT_CH_TEAM", "Your side in a strike (3), raid (6) or Arena team (3)", "On", "Yes", "Activity only", "Player setting", "Matchmade strangers default to voice muted; text on"),
    ("CHN_ALL", "STR_CHAT_CH_ALL", "Both Arena teams (6)", "Off", "No", "Match only", "Standard minimum", "Pre-match and post-match only; locked during rounds"),
    ("CHN_COMPANY", "STR_CHAT_CH_COMPANY", "Company members online (up to 100)", "On", "Optional Company voice room (16 max)", "Server keeps 7 days so offline members can catch up", "Player setting", ""),
    ("CHN_WHISPER", "STR_CHAT_CH_WHISPER", "One other player", "Friends and Company by default", "No", "30 days", "Player setting", "Strangers need the 'Anyone' privacy option"),
    ("CHN_HUB", "STR_CHAT_CH_HUB", "Players in the same Lantern Hold instance (max 40)", "On", "No", "Instance only", "Standard minimum", "Locked 2 h for new accounts"),
    ("CHN_LFG", "STR_CHAT_CH_LFG", "Poster and applicants of one Signal", "On", "No", "Until post closes", "Standard minimum", "Lets applicants ask a question before joining"),
    ("CHN_SYSTEM", "STR_CHAT_CH_SYSTEM", "You", "On", "No", "Session", "n/a", "Joins, leaves, loot, penalties, server notices"),
]
w("chat_channels.csv", ["channel_id", "name_str", "audience", "default", "voice", "history", "filter_floor", "notes"], CHANNELS)

# ---------------------------------------------------------------- company ranks and perms
RANKS = ["Captain", "Lieutenant", "Veteran", "Member", "Recruit"]
PERMS = [  # perm, captain, lt, vet, member, recruit
    ("Invite players", 1, 1, 1, 0, 0), ("Approve join requests", 1, 1, 0, 0, 0), ("Remove lower ranks", 1, 1, 0, 0, 0),
    ("Promote up to Veteran", 1, 1, 0, 0, 0), ("Promote to Lieutenant", 1, 0, 0, 0, 0), ("Edit MOTD", 1, 1, 0, 0, 0),
    ("Edit banner and settings", 1, 0, 0, 0, 0), ("Pick weekly goals", 1, 1, 0, 0, 0), ("Open Company voice room", 1, 1, 1, 1, 0),
    ("Company chat", 1, 1, 1, 1, 1), ("Earn Company XP", 1, 1, 1, 1, 1), ("Claim level rewards", 1, 1, 1, 1, 0),
    ("Transfer captaincy", 1, 0, 0, 0, 0), ("Disband", 1, 0, 0, 0, 0),
]
w("company_permissions.csv", ["permission"] + RANKS, PERMS)

CO_XP = [  # source, xp, cap note
    ("Complete a strike with a Company member", 40, ""), ("Complete a raid encounter with 2+ members", 80, ""),
    ("Win an Arena match with a Company member", 25, ""), ("Lose an Arena match with a Company member", 10, ""),
    ("Clear a Citadel in co-op with a member", 60, ""), ("Defeat a field boss with a member", 20, ""),
    ("Complete a weekly Company goal (each participant)", 100, ""), ("Help a Recruit finish a strike", 50, "Once per Recruit"),
    ("Any activity solo", 0, "Company XP comes only from playing together"),
]
w("company_xp.csv", ["source", "company_xp", "note"], CO_XP)
CO_LEVELS = [(1, 0, "Banner emblems set 1 (40)"), (2, 2500, "Company emote: Company Salute"), (3, 6000, "Banner emblems set 2 (5)"),
             (4, 11000, "Cape trim in Company colors"), (5, 18000, "Company emote: Raise the Banner"), (6, 27000, "Banner emblems set 3 (5)"),
             (7, 38000, "Strider barding in Company colors"), (8, 52000, "Banner emblems set 4 (5)"), (9, 70000, "Company emote: Shield Wall (group, 2-6)"),
             (10, 92000, "Banner emblems set 5 (5) and animated banner")]
w("company_levels.csv", ["level", "total_xp", "reward (cosmetic only)"], CO_LEVELS)
GOALS = [("CG_STRIKES", "Complete 30 strikes as a Company", 30), ("CG_RAID", "Clear 4 raid encounters as a Company", 4),
         ("CG_ARENA", "Win 40 Arena matches with Company members", 40), ("CG_CITADEL", "Clear 6 Hollowed Citadels", 6),
         ("CG_BOSSES", "Defeat 25 field bosses together", 25), ("CG_RECRUITS", "Help Recruits finish 10 strikes", 10),
         ("CG_SEASON", "Complete 20 seasonal event runs", 20), ("CG_FORGE", "Play 15 Company members' Forgeframe maps", 15)]
w("company_goals.csv", ["goal_id", "text", "target"], [(g, t, n) for g, t, n in GOALS])

# ---------------------------------------------------------------- LFG activities
LFG = [("Campaign co-op (any region)", 4, 1, "MM_COOP_SIGN"), ("Citadel run", 4, 1, "MM_COOP_SIGN"), ("Field boss", 4, 1, "MM_COOP_SIGN"),
       ("Strike (playlist)", 3, 75, "MM_STRIKE"), ("Strike (pick one)", 3, 75, "none"), ("Hollowed Citadel", 4, 78, "MM_CITADEL"),
       ("Raid (full clear)", 6, 80, "MM_RAIDFINDER"), ("Raid (single encounter, checkpoint)", 6, 80, "MM_RAIDFINDER"),
       ("Arena Quickplay", 3, 1, "MM_ARENA_QUICK"), ("Arena Ranked", 3, 1, "MM_ARENA_RANKED"), ("Seasonal event", 4, 1, "season playlist"),
       ("Forgeframe challenge room", 4, 1, "none")]
w("lfg_activities.csv", ["activity", "max_players", "min_level", "matchmaking_alternative"], LFG)

# ---------------------------------------------------------------- emotes
EMO = []
for n in range(1, 21):
    EMO.append((f"ITM_COS_EMT_{n:02d}", "Solo", "No" if n not in (7,) else "Yes (loop)", "Hub, open world, between Arena rounds, post-activity",
                "Damage taken or dealt, sprint, roll, block", "Quest or play unlock" if n <= 10 else "Wardrobe Shop"))
for nid, name, kind in [("ITM_COS_EMT_CO1", "Company Salute", "Solo"), ("ITM_COS_EMT_CO2", "Raise the Banner", "Solo"),
                        ("ITM_COS_EMT_CO3", "Shield Wall", "Group 2-6, starts on leader, others join within 3 m")]:
    EMO.append((nid, kind, "No", "Same as above", "Same as above", f"Company level reward: {name}"))
w("emote_rules.csv", ["emote_id", "type", "loops", "allowed_in", "interrupted_by", "source"], EMO)

# ---------------------------------------------------------------- safety
w("report_reasons.csv", ["reason_id", "str", "where", "review_priority (1 high)"],
  [(r, f"STR_SAFE_{r}", wh, p) for r, t, wh, p in REPORT_REASONS])
LADDER = [  # offense class, 1st, 2nd, 3rd, 4th, 5th
    ("Chat toxicity (insults, spam, mild harassment)", "Warning", "24 h chat mute", "72 h chat mute", "7 d chat and voice ban", "30 d online suspension"),
    ("Hate speech, slurs, sexual harassment", "72 h chat and voice ban", "7 d online suspension", "30 d online suspension", "Permanent", ""),
    ("Threats of violence, doxxing", "30 d online suspension and review", "Permanent", "", "", ""),
    ("Child safety", "Permanent and legal referral", "", "", "", ""),
    ("Offensive name or Company name", "Forced rename", "Forced rename and 7 d rename lock", "7 d online suspension", "Permanent", ""),
    ("Griefing or throwing", "Warning", "24 h matchmaking ban", "7 d matchmaking ban", "30 d online suspension", "Permanent"),
    ("Cheating (EAC detection or server proof)", "Permanent online ban; Seals and leaderboard entries removed", "", "", "", ""),
    ("Exploits (reported, not confirmed malicious)", "Warning and rollback of gains", "7 d online suspension and rollback", "Permanent", "", ""),
    ("Scams, account selling, real-money trading", "30 d online suspension", "Permanent", "", "", ""),
    ("Chargeback fraud", "Disputed items revoked; shop locked until resolved", "Shop locked permanently", "", "", ""),
    ("False reporting (deliberate, 10+ in 7 days rejected)", "Reports ignored for 7 d", "Reports ignored for 30 d", "", "", ""),
]
w("penalty_ladder.csv", ["offense", "1st", "2nd", "3rd", "4th", "5th"], LADDER)
LEAVER = [("Arena Ranked", "Leave or 3 min AFK", "5 min", "15 min", "60 min", "24 h", "Counts decay 1 per 24 h; loss counted"),
          ("Arena Quickplay", "Leave", "None", "5 min", "15 min", "60 min", "3 leaves in 24 h before first step"),
          ("Strike (matchmade)", "Leave before final boss", "None", "5 min", "15 min", "30 min", "3 leaves in 24 h before first step"),
          ("Raid Finder", "Leave mid-encounter", "None", "15 min", "30 min", "60 min", "Leaving between encounters is free")]
w("leaver_penalties.csv", ["activity", "counts_as_leave", "step1", "step2", "step3", "step4", "notes"], LEAVER)
FILTER = [("Slurs and hate terms", "Hidden", "Hidden", "Hidden", "Always on; also blocked in names, Company names, tags"),
          ("Profanity", "Shown", "Hidden as ****", "Hidden", "Default Standard"),
          ("Sexual terms", "Shown", "Hidden", "Hidden", ""),
          ("Personal info (phone, email, address patterns)", "Hidden", "Hidden", "Hidden", "Always on"),
          ("URLs and invite links", "Removed", "Removed", "Removed", "Always on"),
          ("Leetspeak and spacing evasions", "Normalized before match", "Normalized", "Normalized", "e.g. character swaps and spaced letters"),
          ("Unknown words (Strict only)", "Shown", "Shown", "Hidden unless on allow list", "Strict default for platform child or teen accounts")]
w("chat_filter.csv", ["category", "off", "standard", "strict", "notes"], FILTER)

# ---------------------------------------------------------------- support
TICKETS = [
    # cat, sub, priority, tier, self_serve, target_resolution
    ("Account", "Can't sign in", "P2", 1, "KB: sign-in errors; platform status", "24 h"),
    ("Account", "Account compromised or stolen", "P1", 2, "Platform password reset first", "48 h"),
    ("Account", "Link or unlink platforms", "P3", 1, "Linked Accounts screen", "48 h"),
    ("Account", "Name change or forced rename", "P4", 1, "Rename screen", "72 h"),
    ("Account", "Data access, export or delete (GDPR, CCPA)", "P2", 2, "Download or Delete My Data", "Legal deadline (30 days GDPR, 45 days CCPA)"),
    ("Purchases", "Purchase missing", "P2", 1, "Restore Purchases", "24 h"),
    ("Purchases", "Refund request", "P3", 1, "Platform refund page", "Same day redirect"),
    ("Purchases", "Expansion not unlocked", "P2", 1, "Restore Purchases", "24 h"),
    ("Purchases", "Charged twice", "P2", 1, "Platform purchase history", "Redirect plus grant check 24 h"),
    ("Progress", "Lost progress or save corrupted", "P2", 2, "Restore Cloud Save", "48 h"),
    ("Progress", "Missing items, Seals or rewards", "P3", 2, "KB: reward timing", "5 days"),
    ("Progress", "Quest blocked or broken", "P3", 1, "KB: known issues", "5 days or next patch"),
    ("Technical", "Crashes", "P3", 1, "KB: crash fixes; crash report link", "5 days"),
    ("Technical", "Performance or graphics", "P4", 1, "KB: settings guide", "5 days"),
    ("Technical", "Connection, co-op or matchmaking errors", "P3", 1, "KB: error codes (ERR_*)", "5 days"),
    ("Safety", "Report a player (outside the game)", "P3", 2, "In-game report", "72 h"),
    ("Safety", "Threat of harm or self-harm", "P0", 2, "Crisis line shown at once", "Escalate within 1 h, 24/7"),
    ("Safety", "Child safety", "P0", 2, "None", "Escalate within 1 h; legal referral"),
    ("Penalties", "Ban or suspension appeal", "P3", 2, "Appeal form", "7 days"),
    ("Penalties", "Chat restriction appeal", "P4", 2, "Appeal form", "7 days"),
    ("Feedback", "Bug report", "P4", 1, "Report a Problem", "Acknowledge only; routed to QA"),
    ("Feedback", "Suggestion", "P4", 1, "Community forum link", "Acknowledge only"),
    ("Forgeframe", "Mod or map takedown and DMCA", "P2", 2, "Takedown form", "72 h"),
    ("Accessibility", "Accessibility help", "P3", 1, "KB: accessibility options", "48 h"),
]
w("ticket_types.csv", ["category", "subcategory", "priority", "first_tier", "self_serve_first", "target_resolution"], TICKETS)
SLA = [("P0", "Safety emergency", "15 min", "1 h escalation to Trust and Safety lead; law enforcement contact per policy", "24/7 on-call"),
       ("P1", "Account takeover, payment fraud", "1 h", "48 h", "24/7"),
       ("P2", "Can't play or paid content missing", "4 h (launch window 2 h)", "24-48 h", "24/7 English; business hours other languages"),
       ("P3", "Progress, technical, appeals", "24 h (launch window 4 h)", "5 days; appeals 7 days", "Business hours tier 2"),
       ("P4", "Feedback, cosmetic issues", "72 h", "Acknowledge only", "Business hours")]
w("sla.csv", ["priority", "covers", "first_response", "resolution", "coverage"], SLA)
MACROS = [
    ("MAC_REFUND_STEAM", "Refunds: Steam", "Steam handles refunds for Shardfall and its cosmetics. Open Steam Support > Purchases > Shardfall to request one. Their standard window is 14 days and under 2 hours played for the game."),
    ("MAC_REFUND_PS", "Refunds: PlayStation", "PlayStation Store handles refunds. Contact PlayStation Support from your account's transaction history."),
    ("MAC_REFUND_XB", "Refunds: Xbox", "Microsoft handles refunds. Request one at the Microsoft Store refund page from your order history."),
    ("MAC_RESTORE", "Missing purchase", "Please open Help > Restore Purchases in game. If the item still isn't there after 24 hours, reply with your platform order number and we'll grant it."),
    ("MAC_SAVE", "Save restore", "Open Help > Restore Cloud Save and pick a snapshot from before the problem. If none work, reply and we'll check older backups."),
    ("MAC_HACKED", "Compromised account", "First reset your platform password and turn on two-step sign-in. Then reply with your Shardfall ID and the last date you played normally. We'll lock the account, check the activity and restore anything taken."),
    ("MAC_APPEAL_RECEIVED", "Appeal received", "We got your appeal. A different agent from the one who applied the penalty will review it and reply within 7 days."),
    ("MAC_APPEAL_UPHELD", "Appeal upheld", "We reviewed the evidence and the penalty stands. This decision is final for this penalty."),
    ("MAC_APPEAL_OVERTURNED", "Appeal overturned", "We reviewed your appeal and removed the penalty. Anything it removed, such as Seals or rankings, has been restored."),
    ("MAC_KNOWN_ISSUE", "Known issue", "This is a known issue and a fix is planned for {patch}. Thanks for your patience; we'll update this ticket when it ships."),
    ("MAC_CRISIS", "Crisis", "We're concerned for your safety. Please contact local emergency services or a crisis line now. Resources by country: {url}."),
    ("MAC_DATA", "Data request", "We've started your data request. You'll get a download link (or deletion confirmation) at your account email within 30 days."),
]
w("support_macros.csv", ["macro_id", "name", "text_en"], MACROS)
KB = ["Sign-in and platform account errors", "Every error code and what to do (ERR_*)", "Cross-play: how it works and how to turn it off",
      "Linking Steam, PlayStation, Xbox and Epic accounts", "Restore Purchases", "Refunds by platform", "Restore a cloud save",
      "Save corruption: what we back up and when", "Co-op: hosting, joining, level sync", "Strikes, raids and Arena matchmaking",
      "NAT and port settings for PC", "Crashes on PC: drivers, shader cache, verify files", "Performance settings guide",
      "Console performance and quality modes", "Shard-notes, death echoes and ghost glimpses", "Invasions: turning them on and off",
      "Friends, fireteams and privacy", "Companies: founding, ranks and goals", "Using the Signal Board", "Chat, voice and the chat filter",
      "Muting, blocking and reporting", "Code of Conduct", "Penalties and how to appeal", "Leaver penalties", "Streamer Mode",
      "Accessibility options", "Text-to-speech and speech-to-text chat", "Wardrobe Shop and prices", "Expansions and how to install them",
      "Seasons and event rewards", "Seals: caps and weekly reset", "Forgeframe: getting started", "Mod hub rules and takedowns",
      "Parental controls by platform", "Privacy: download or delete your data", "Account security and two-step sign-in",
      "Server status and maintenance windows", "Known issues (live)", "Patch notes", "Contacting support"]
w("kb_articles.csv", ["kb_id", "title", "launch_phase"], [(f"KB_{n:03d}", t, "Beta (month 49)") for n, t in enumerate(KB, 1)])
RECOVERY = [
    (1, "Player opens support web (no sign-in needed) and picks 'Account compromised'", "Web form", "Ticket P1"),
    (2, "Agent asks player to secure the platform account first (Steam Guard, PSN or Microsoft two-step)", "Macro MAC_HACKED", "Platform owns credentials"),
    (3, "Player proves ownership: platform sign-in to the support portal, or 3 of: Shardfall ID, character names, first purchase date, Company, last play date", "Portal", "Shardfall choice"),
    (4, "Agent locks the Shardfall account (no online, no shop) while reviewing", "Admin tool", "Within 1 h of proof"),
    (5, "Agent reviews ledger and audit log: items dismantled or sold, Seals spent, Company changes, link changes", "Economy ledger (tech/02-online.md)", ""),
    (6, "Restore from the last good cloud snapshot or re-grant items from the ledger", "Save backups, ledger", "Seals restored up to carry cap 500"),
    (7, "Revert unauthorized links, names and Company captaincy", "Admin tool", ""),
    (8, "Unlock and close; KB link on two-step sign-in", "Macro", "Target 48 h end to end"),
]
w("account_recovery_flow.csv", ["step", "action", "tool", "note"], RECOVERY)
REFUND = [("Base game and expansions", "Platform only (Steam, PlayStation Store, Microsoft Store, Epic)", "Platform policy", "Support redirects with MAC_REFUND_*"),
          ("Cosmetics (real money)", "Platform only", "Platform policy", "On refund notice the item is revoked; if equipped, slot resets to default"),
          ("Purchase not delivered", "Shardfall grants after receipt check", "Store service receipt (tech/02-online.md)", "Never a cash refund from Shardfall"),
          ("Chargeback", "Platform decides", "Platform notice", "Disputed items revoked, shop locked until resolved; online play not affected"),
          ("Goodwill after an outage", "Free cosmetic or extended season event, never Seals or power", "Live ops decision", "No real-money compensation"),
          ("Ember, Seals, materials", "Never refundable or sold", "", "Real money never buys power (production/monetization.md)")]
w("refund_rules.csv", ["case", "who_refunds", "evidence", "handling"], REFUND)
APPEAL = [("Who can appeal", "Any penalty except automatic rate-limit cooldowns and leaver timers under 60 min"),
          ("Window", "30 days from the penalty"), ("How many", "1 per penalty"), ("Reviewer", "Tier 2 agent other than the one who applied it; cheating bans add an anti-cheat analyst"),
          ("Reply time", "7 days (production/customer_support.md)"), ("Outcomes", "Upheld, reduced, overturned"),
          ("Overturned", "Penalty removed from history; Seals, leaderboard and items restored; penalty does not count toward the ladder"),
          ("Penalty runs during appeal", "Yes, except permanent bans from automated detection with under 95% confidence, which pause to a 30-day suspension"),
          ("Evidence kept", "Chat logs 30 days (180 days if tied to a penalty); anti-cheat evidence 2 years for permanent bans"),
          ("Audit", "5% of upheld appeals re-reviewed monthly by the Trust and Safety lead")]
w("appeal_rules.csv", ["rule", "value"], APPEAL)
STAFF = [("Closed beta (month 49)", "50,000", "1.5%", 750, 4, 0, "Vendor pilot team plus 2 in-house"),
         ("Launch month (month 54)", "4,000,000 units year one; 1.6M month one", "3%", 48000, 40, 4, "Production plan: 40 vendor agents, 4 in-house"),
         ("Months 2-3", "1.2M active", "1%", 12000, 12, 4, ""), ("Steady state", "600k active", "0.6%", 3600, 5, 2, "Production plan: 2 in-house after launch"),
         ("Expansion launch week", "+40% active", "2%", 16000, 15, 3, "Temporary vendor surge")]
w("staffing.csv", ["period", "players", "contact_rate", "tickets_per_month", "tier1_agents", "tier2_agents", "note"], STAFF)

# ---------------------------------------------------------------- audio and asset hooks, telemetry
HOOKS = [("SFX_UI_SOC_REQUEST", "SFX", "Soft two-note chime, rising"), ("SFX_UI_SOC_ACCEPT", "SFX", "Warm three-note chime"),
         ("SFX_UI_SOC_ONLINE", "SFX", "Single lantern tick, quiet"), ("SFX_UI_SOC_JOIN", "SFX", "Anchor-light whoosh, short"),
         ("SFX_UI_SOC_LEAVE", "SFX", "Anchor-light whoosh reversed"), ("SFX_UI_SOC_INVITE", "SFX", "Shard ping with Ostra shimmer"),
         ("SFX_UI_SOC_READY", "SFX", "Hull bell, single"), ("SFX_UI_SOC_VOTE", "SFX", "Low drum tap"),
         ("SFX_UI_SOC_GOAL", "SFX", "Company horn, short"), ("SFX_UI_SOC_LEVEL", "SFX", "Company horn with choir swell"),
         ("SFX_UI_CHAT_WHISPER", "SFX", "Quiet glass tick"), ("SFX_UI_CHAT_SEND", "SFX", "Paper slide, very soft"),
         ("SFX_PING_LOCATION", "SFX", "3D marker tone, mid"), ("SFX_PING_ENEMY", "SFX", "3D marker tone, sharp"), ("SFX_PING_DANGER", "SFX", "3D double tone"),
         ("VFX_PING_MARKER", "VFX", "Cyan Shard diamond, pulses 2x, 8 s life"), ("VFX_PING_ENEMY", "VFX", "Red chevron over target, 5 s"),
         ("VFX_EMOTE_SYNC_RING", "VFX", "Faint ring on ground 3 m, shows join area for group emotes"), ("VFX_BANNER_ANIMATED", "VFX", "Cloth sim plus emblem glow for level 10 banner"),
         ("MESH_CO_BANNER_POLE", "MESH", "Company banner on Lantern Hold Company hall wall"), ("MESH_SIGNAL_BOARD", "MESH", "Signal Board object in Lantern Hold, salvaged comms panel"),
         ("ACT_NPC_CO_STEWARD", "ACT", "Company Steward NPC in Lantern Hold who opens the Company screen"),
         ("ANIM_EMOTE_CO1", "ANIM", "Company Salute"), ("ANIM_EMOTE_CO2", "ANIM", "Raise the Banner"), ("ANIM_EMOTE_CO3", "ANIM", "Shield Wall group emote, 6 positions")]
w("asset_hooks_social.csv", ["hook", "kind", "description"], HOOKS)
TEL = ["friend_request_sent", "friend_request_accepted", "fireteam_formed", "fireteam_size_at_launch", "company_created", "company_joined",
       "company_left", "company_goal_completed", "lfg_post_created", "lfg_post_filled_s", "lfg_post_expired", "chat_message_sent (count only, no text)",
       "quickchat_used", "ping_used", "emote_used", "report_filed", "report_actioned", "penalty_applied", "appeal_filed", "appeal_outcome",
       "mute_used", "block_used", "crossplay_toggled", "support_ticket_opened", "kb_article_viewed", "kb_deflected (article viewed and no ticket in 24 h)"]
w("telemetry_social.csv", ["event"], [(t,) for t in TEL])
