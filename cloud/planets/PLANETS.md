# PLANETS: every Panscriptum universe is a planet in the game (Marlon 11-03)

Source: library-content/content.sqlite (217 universes, 699,649 entries) and universe_placement.json. Real data only; nothing invented. Generator: gen_planets.py (data only, no jars). Outputs: planets.tsv, planets.json, datapack/.

## The rule
- **One universe = one planet = one dimension** `diaithir_planets:<planet_id>`. `planet_id` is the lowercase universe name (a-z, 0-9, _), unique across all 217. Diaithir is Terra (the existing Overworld, `minecraft:overworld`); the other 216 are new dimensions.
- **Every entry lives on its planet.** An entry's planet is its `universe` column (id form `REALM.universe.E<era>.collection.number`). NPCs, mobs, bosses, rites, gear, structures, quests and books place by that key, never anywhere else. Tier (Age) gates what appears; a planet opens at the first Age with at least 50 entries (`opens_age`).
- **Planets group into seven soils** (the charter metaverses): Bloom 68, Hollow 42, Storm 35, Frost 26, Iron 25, Ember 16, Quiet 5. The spine code (II.T.1 style) gives the orbit number within its soil.
- **Host terrain per soil** (vanilla dimension types and noise settings, so no new jars): Bloom overworld, Frost amplified, Storm floating islands, Hollow caves, Iron large biomes, Ember nether, Quiet end. Biome palettes, structures and flora come next from each planet's BIOME, DIMENSION, SETTLEMENT and STRUCTURE entries via the biomes-dimensions module.
- **Travel** is by Keelwright space hulls (SHIPBUILDING.md step 9): each soil is a drift region in space, each planet an orbit slot by spine number. Age gate = `opens_age`. Library entries stay readable from the Library dimension.

## For the sibling lanes
Read `planets.tsv` (one row per planet: id, dimension, soil, opens_age, entries and counts per form). Place each entry by its `universe`. Per-planet counts per form are included so you can size your work.

## Status
Done: table, ids, dimension JSON, English names. Untested: dimension JSON has not been booted (no server jar in the cloud); the PC lane or a headless boot must load datapack/ before it ships. Not done: per-planet biome palettes, sky/skybox, Keelwright route data, name pipeline for the 130 cultures (universe names are coined; they keep their own names).
