# Survey part 4: ports status and blocked entries (2026-11-03)
Done as draft PRs in diaithir-ports (see MERGE_ORDER rows): #259 Nutritional Balance, #262 graves (Epitaphs), #267 PermissionGate, #272 Ore Detector, #279 quest engine (Not Quests), #282 capitals (MCA Capitals), #283 parties (Open Parties and Claims), #285 taxes (Tale of Kingdoms, stacked on #282), #289 law (Cuffed, Bountycraft), #290 Simple Backups, #291 grief log (GriefLogger), #292 structure protection (Structural Safety).
Owned by other threads: More Professions, Better Caravans, Chapters, Server Waypoint, Guard Villagers, Global Events and Oh My Meteors (#111/#113), MineColonies, Researcher.
Blocked or not attempted, one line each:
- Biology Dictionary (LGPL-3.0): 37k lines, 100 mixin imports and access wideners, JEI/Cloth hooks; needs its own jar and thread.
- Homeostatic Seasons (MIT): requires the WhiteNoise and ClimateSettings libraries (not in tree) and 10 mixins; port those libraries first.
- Chat Heads (MPL-2.0): client chat-renderer mixins; clean-room rewrite needs the chat-client spec first.
- No Chat Reports (WTFPL): mixin-based; the same effect is `enforce-secure-profile=false` in the pack's server.properties override.
- Blood Moon: Modrinth licence is All Rights Reserved (survey said MIT); not portable.
- Lightman's Currency treasury/tax fold: our fork's source is not in diaithircompat; do it in the economy thread.
- Your Reputation, Wandering Trader Plus, Villager Trading Plus, Trading Post: diaithir-villager-trade module does not exist in the tree and villager gossip already covers reputation pricing; needs the trade module first.
- Minepedia, Guide-API VP, Modonomicon renderer: Codex is a separate module; no codex jar in the tree yet.
- Origins picker UI, Language Reload, Ending Library idea, Convenient Achievements: Fabric-only or idea-only; belong to the culture-start and achievements threads.
- Skill trees (Default Skill Trees, Stronger Skill Tree): data for the ARR Puffish engine, which is not in the tree.
- Ore Scanner: vanilla-only ticking datapack; superseded by the Ore Detector fold.
- Bannerbound Antiquity Age, Ancient Warfare 2 research: source access unconfirmed (jar only / 1.12); concepts feed the clean-room research tree.
- Tale of Kingdoms wars/diplomacy, MCA villagers as subjects, Cuffed/Bountycraft art parity: later stages of #282, #285, #289.
