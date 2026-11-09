# Boss client tests (G01, G02, G08, G17-G20, G60-G68)

Run through the already-running w28 client (joined to C:\MCTestServer\w28, survival, at world spawn, name Uber_Byte). Do not launch a second client. RCON port 25576, password from server.properties (never post it). Never touch C:\DiaithirServer. Test in the overworld at spawn, only the thing asked.

Evidence = server log line (C:\MCTestServer\w28\logs\latest.log) AND a screenshot of the fight. Otherwise UNTESTED. Save shots next to the report and tick the item in plans/V1_CHECKLIST.md (branch claude/project-thread-wx17x3) with the log line and shot path. Push after each tick.

## Prep (once)
1. `gamemode survival Uber_Byte` (no resistance effects, the player must be hurt). Give iron armor + sword: `give Uber_Byte minecraft:iron_sword`, set health full: `effect give Uber_Byte minecraft:instant_health 1 5`.
2. `kill @e[type=!player,distance=..64]` to clear the area; `time set day`; `gamerule doMobSpawning false`.
3. Mark the log position (note the last line number) before each boss.

## Per boss: G01 antlered_hollow, G02 ash_seraph, G08 driegunsalund, G17 natuirkriegach, G18 natuirmoir, G19 natuirrig, G20 natuirsaegul
Id is `diaithirbosses:<name>`. Summon 6 blocks in front of the player:
`execute as Uber_Byte at @s run summon diaithirbosses:<name> ^ ^ ^6` (or `/boss spawn <name>` if present; try it for G17/G19 too).

Steps and pass checks, in order:
1. Spawn: command accepted, entity exists: `execute if entity @e[type=diaithirbosses:<name>]` returns success. Log line of the summon.
2. Alive at 60 s: still exists 60 s later (no despawn). If it vanishes, read the log for the despawn/discard reason and note it (G17/G19 failed this: "gone in under 3 s"; RCON-only summon without a player held 60 s, so test with the player standing near).
3. Hurts the player: stand within 8 blocks and let it attack; the player's health must drop from boss damage. Evidence: death-message-free health drop in screenshot, or log line `Uber_Byte was ...by <boss>` if killed. Screenshot showing the damage and the boss.
4. Dies to player damage only: fight it with the sword (add `/effect give @e[type=...] minecraft:weakness` only if too long; no `kill` command). Pass if it dies from player hits, and `kill`/`/damage` was not used. Log line of the death.
5. Loot: drops its loot table. List drops after death: `data get`/screenshot of items on the ground; log line of the loot table roll if logged.
6. Static checks (no client needed): its entry exists in the Codex `bosses.json`, it has an Age and an arena. Cite file path and line.
Pass = all six. Fail = say which step and the log reason; fix in diaithir-ports diaithir-bosses on its own branch with a draft PR.

## G60 Ascendant altar and tier gating
1. Place/raise the altar through the quest "Raise the altar" (do not `setblock` it). Screenshot of the altar.
2. Try Ascendant tier II before beating tier I: must be refused (log line of the refusal).
3. Beat tier I once, retry tier II: accepted (log line). Tier I only at Age VII, II and III at Rodos.
Pass = refusal log, acceptance log, altar screenshot.

## G61 Boss rush (data/diaithirbosses/rush.json)
Start the rush after 3 required kills. 6 base bosses then 9 Ascendant, no healing (confirm healing is blocked). Reward lines in the log at 6, 9, 12, 15 kills (4 lines), scoreboard best time updates. Pass = 4 reward log lines plus a screenshot. Heavy: schedule when the player is stable; client must not disconnect.

## G62 Difficulty modes (difficulty.json: standard, relentless, merciless, ordeal)
For each mode: complete its quest in the Codex Quests tab (screenshot), then fight one boss and log the multipliers (HP, damage, tempo, Champion elite chance, loot, XP). Try to lower the mode: must be refused. Pass = per-mode log lines and one quest screenshot. Needs G61.

## G63 quests/ascendant.json
Raise the altar, Ascendant I, II, III, The Gauntlet, and one per mode (4+3 quests shown in the Codex Quests tab). Each completes once (log line on completion; second attempt gives no repeat reward). Screenshot of the Quests tab.

## G64 Global Events hooks (diaithir_events.json)
Fire each event once on the server (event command per diaithir_events.json): blood moon halves the respawn cooldown, eclipse buffs Dusk Wyrm, storm buffs the listed boss, and so on. Pass = one log line per event showing the boss effect (cooldown value or effect applied). #113 wins over #111, #134 follows.

## G65 Shardfall Gate win ceremony
Gate stays closed before `shard_resonance` (log refusal), opens after (Rodos), ceremony plays, win flag set once (log: gate open and win flag, and a second trigger does not set it again). Screenshot.

## G66 Ascendant biomes and rite sites
In a fresh chunk set: `/locate structure <site>` only (never `/locate biome`). Travel to each site, confirm it generated and its rite plays. Log line plus screenshot per site.

## G67 Boss items have a role
CMD: run the strict-orphan list script against the 81 boss items (see plans/ITEM_ROLES.csv and the orphan script in global-repo); pass when boss items in the list = 0. Paste the command and its output count.

## G68 Planet altars (gen_planet_altars.py)
Generator output for 216 planets is in the jar (jar listing). Pick 10 planets, spawn at each altar, boss spawns (log line x10). Pass = 10 log lines.

## Memory rule
Do not run boss rush or worldgen tests (G61, G66) at the same time as other loads; the PC has little free RAM.
