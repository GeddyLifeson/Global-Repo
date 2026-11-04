# Handoff: Port Botania to 26.1

Status 2026-11-04: partly done, post-V1 per driver. Thread resolved.

## State
- Licence: Botania License (copyleft, credit Vazkii, non-monetary). Port allowed (MOD_SURVEY, Global-Repo #28).
- diaithir-ports PR #280 MERGED (base diaithircompat). Code in `diaithir-druidry/botania/`.
- Compiles on NeoForge 26.1.2, JDK 25: 88 files (API shell, helpers) + slice `vazkii/botania/slice` (mana pool block and block entity, mana powder, namespace `botania`).
- Mana stored as joules, 100 J per mana (same as MagicFuel in diaithir-units, ports #266), exposed via NeoForge `EnergyHandler` capability (SimpleEnergyHandler). Age V gate: `"botania": "V"` in `diaithir-druidry/age_gates.json`.
- Boot-tested headless with `./gradlew runServer -PbootTest` (drops Spell Engine dep). setblock mana_pool OK, BE reports energy.
- Not tested: powder insert, client render, save/reload, full pack.

## Not done
- ~1090 files in `botania/pending/java` (registries, spreader, bursts, lenses, generating and functional flowers, apothecary, runic altar, mixins). Data for them in `botania/pending-data/` (worldgen, structures, jukebox songs, Patchouli).
- MagicFuel is not imported by druidry; constant duplicated.

## Next steps
1. New branch from latest diaithircompat. Port registries first, then spreader/burst, then generating flowers.
2. Use `/tmp/iter.sh` idea: compile, move erroring files to pending, repeat, then fix in batches.
3. 26.1 API: Identifier replaces ResourceLocation; EnergyHandler transfer API; ValueInput/ValueOutput for BE saving; useItemOn/useWithoutItem on Block.
4. Dev server: stdin is not forwarded, use RCON (enable-rcon, port 25599); forceload a chunk before setblock; do not set level-type=flat.
