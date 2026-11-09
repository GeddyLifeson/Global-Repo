# Handoff: bugs D1-D4 (11-09)

Nothing below is proven in game. PC client lane tests only these, in the real world at spawn.

Ports branch `claude/project-thread-c62igd` (diaithir-ports) holds both code changes.

- D1 Superman #287: patch already on DiaithirRPG main (grant_on_spawn.js). Test: spawn zombie `{NeoForgeData:{library_id:"TEST.superman"}}` near a joined client; `/data get entity <it> attributes` (damage, speed, armor up), slow_falling active, energy_beam / freeze_breath hits a player without Resistance. Evidence: LOG + SHOT.
- D2 gate rite: no change. Needs C4 and a client; run the gate rite, log each chain step. LOG + SHOT.
- D3 tank Space-fire: `FireKey` (diaithir-units): while riding (`player.isPassenger()`) and the jump key is held, the client sends `/diaithirvehicle shoot` every 3 ticks; the new ungated command holds the trigger 4 ticks and sends no chat. No new keybind, no jump change. `gradle compileJava` passes (JDK 25). Test: sit in a loaded tank seat, hold Space, loadedBullet count drops, muzzle and impact visible. Open risk: IV seats may not count as `isPassenger()`; if no fire, check that. UNTESTED in game.
- D4 Tool Belt: enumextensions.json is in source and referenced by neoforge.mods.toml. No built jar or release exists in the repo, so inclusion in the pack jar is UNCONFIRMED: `unzip -l` the pack's diaithir-gear jar for META-INF/enumextensions.json. Keys changed: open R to N, slot V to Y. Test: client reaches title screen, belt screens open, key audit shows no conflicts for N and Y.
- J15 name shot: open the Codex or an item tooltip in a joined client with a start culture other than Diaithir; the page must show the English name and, beneath it, the grey italic native name (spelled per the culture's rules; 11-09 names were mechanically repaired, so check it is not an obvious gibberish run). Then switch to Diaithir start and confirm Diaithiris shows. SHOT of both. Audit already passes (`python3 -I cloud/names/linguistics/audit_names.py` exits 0); only the in-game shot is missing. UNTESTED.
