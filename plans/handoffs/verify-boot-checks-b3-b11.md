# Verify lane: boot checks after the ARR strip (11-09)
Pack branch: diaithir-ports claude/project-thread-htoezl (PR #364 into claude/pack-v1-3-wave17), commit 90812bc5. Nothing below was booted; all UNTESTED.

Changed: Oritech (platform suite), Regions Unexplored, Relics & Artifacts, Apotheosis (extras suite) and ScalableLux (worldgen suite) were cut out of the hosted suite jars by `tools/integrity/strip_module.py` and now download as the original Modrinth files (`mods/oritech.pw.toml`, `regions-unexplored`, `relics-artifacts`, `apotheosis`, `immersive-vehicles` both-side, `scalablelux` client-only). The hosted Immersive Vehicles diaithir.2 jar is gone (original 24.0.0 replaces it; diaithir.2 differed by 2 client classes, `mcinterface261/InterfaceClient` and `MultiPackResourceManagerMixin`, so check the client for whatever that fixed).

Boot checks to run (C:\MCTestServer, real world at spawn):
1. Server boot reaches Done with 0 new errors; log count of "Failed to analyze class" = 0 (B11, was 2,325).
2. No duplicate-mod error; no missing-mod error for oritech, regions_unexplored, relics_artifacts, apotheosis, mts, scalablelux.
3. Client boot with ScalableLux present, then client join (Immersive Vehicles client fix).
4. Known suspect: `easy_npc` is still folded in diaithir-tech-ext-suite (519 entries) while `easy_npc_bundle-neoforge-26.1.2-7.16.0.pw.toml` is also linked; expect a duplicate-mod error, drop one.
5. Run `python3 -I tools/integrity/check_licenses.py . <MOD_REMOVALS.json>` and `check_models.py .` (counts in V1_CHECKLIST B6, B10).

## Second pass (04a775c3)
Also stripped and now linked: The Aether II 26.1.2-alpha.4.2, The Undergarden 0.9.8, The Backwoods 1.8.0 (worldgen suite). Boot check: these three load with their own dependencies (look for missing-dependency errors), our `diaithir_overworld_biomes` realm classes still find them. Item 4 above is withdrawn: `easy_npc_bundle` is a MIT meta mod, no duplicate.
