# Handoff: bugs D1-D4 (11-09)

Nothing below is proven in game. PC client lane tests only these, in the real world at spawn.

Ports branch `claude/project-thread-c62igd` (diaithir-ports) holds both code changes.

- D1 Superman #287: patch already on DiaithirRPG main (grant_on_spawn.js). Test: spawn zombie `{NeoForgeData:{library_id:"TEST.superman"}}` near a joined client; `/data get entity <it> attributes` (damage, speed, armor up), slow_falling active, energy_beam / freeze_breath hits a player without Resistance. Evidence: LOG + SHOT.
- D2 gate rite: no change. Needs C4 and a client; run the gate rite, log each chain step. LOG + SHOT.
- D3 tank Space-fire: new `FireKey` (Space) in diaithir-units runs new ungated `/diaithirvehicle shoot` (4 ticks, reuses `fire`). Test: stand beside a loaded tank, press Space, loadedBullet count drops, muzzle and impact visible. Known cost: Space also jumps (vanilla conflict, D11 to resolve; consider rebinding), and pressing Space with no vehicle within 8 blocks sends a failure chat line each press. UNTESTED, never compiled here.
- D4 Tool Belt: enumextensions.json is in source and referenced by neoforge.mods.toml. No built jar or release exists in the repo, so inclusion in the pack jar is UNCONFIRMED: `unzip -l` the pack's diaithir-gear jar for META-INF/enumextensions.json. Keys changed: open R to N, slot V to Y. Test: client reaches title screen, belt screens open, key audit shows no conflicts for N and Y.
