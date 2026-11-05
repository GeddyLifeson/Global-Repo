# Handoff: Build a script that tests everything in game
## State (11-05 16:50Z)
Harness = Global-Repo draft PR #116, branch claude/project-thread-ah6kth, dir cloud/headless_bot/everything/ (S6986 manifest.py static census + recipe checks, S6987 run_all.py RCON runner; README there). Raw proof rows in everything/proof/.
Proven on a real cloud Lane (JDK25 + NeoForge installer at /tmp/claude-0/lane, ephemeral; reinstall with cloud/tools/get_jdk25.sh and the neoforge-26.1.2.116 installer --install-server srv-base):
- diaithir-arms jar: 20/20 blocks PASS, 20/20 items PASS, 12/20 recipes PASS (8 UNTESTED: c: tag ingredients unresolvable), entity thrown_weapon UNTESTED (removes itself), negative control FAILs correctly.
- diaithir-bosses jar (diaithir-ports branch claude/pack-v1-3-wave17, mods/): 35 bosses: 28 PASS, 5 UNTESTED (antlered_hollow, ash_seraph, driegunsalund, natuirmoir, natuirsaegul: die+drop but never seen hurting player), 2 FAIL (natuirrig, natuirkriegach: summon accepted, entity gone <3 s, cause unknown; try /boss spawn).
Bosses cap damage per hit; script grinds 1000/hit by Tester until dead. Run with --client, BOSS_RES=4 env for safe player.
## Not done
- Full pack run (cloud lane only fits light packs; do it on PC C:\MCTestServer via --rcon HOST:PORT:PASS, needs enable-rcon=true, Marlon/PC RC thread).
- dimensions, commands, machines (spec file), smelting/non-crafting recipes, KubeJS recipes, tag resolution for c: tags (add map or read tag json from pack), abilities per boss, screenshots per process.
- Hand report.tsv to verify thread cmsg_01EpyoqYuwV3X4z3b4zk5pEKAV9C6jeiVQ2j3ZaMzpJqwx.
- Project storage full: could not attach files; proof is in the PR.
