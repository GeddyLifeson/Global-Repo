# NPC power pool
One shared list, no per-character powers. `POWER_POOL.tsv`: id, name, slot, tier (1-3), kind (P passive, works on mobs; A active, needs a trigger), source_power (NeoOrigins ids, comma list), keywords (regex, lowercase).
Extraction matches card text to keywords; the grant step gives each NPC the N powers it needs on spawn (priority order, highest tier first within slot). `ARCHETYPE_GRANTS.tsv` holds ordered examples for Superman, Kenshiro, Goku, Jotaro and Flash analogs.
Existing powers come from NeoOrigins 2.2.30. Gaps (super strength, invulnerability, super speed, barrage, ki blast, energy beam, time stop, telepathy, rapid regeneration) are composed from NeoOrigins action types in `powers/` (namespace diaithirpowers). Time stop is an approximation (slowness 254 plus weakness and fatigue in 32 blocks for 5 s). Rebuild: `python3 -I tools/powers/gen_power_pool.py data/powers` (S6960).
Copy of the list: /mnt/project-files/plans/powers/.
