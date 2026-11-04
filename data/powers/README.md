# NPC power pool
One shared list, no per-character powers. `POWER_POOL.tsv`: id, name, slot, magnitude ('1-10' scalable, '-' fixed), kind (P passive, works on mobs; A active, needs a trigger), source_power (comma list of power ids; `{m}` is replaced by the magnitude), keywords (regex, lowercase).
EVERY power takes a magnitude 1-10 (effectiveness); one pool id each. The grant step resolves `{m}` in source_power to the matching power files, so two beings with different time-stop magnitudes play differently. Values scale linearly from magnitude (strength +2 attack damage per step, blast 2 and beam 2.5 damage per step, speed +25% per step, invulnerability damage taken 0.9 at 1 down to 0.02 at 10).
Magnitude from card scale words: 1 peak human, 2 city block, 3 building/tank, 4 city, 5 mountain, 6 island, 7 ocean/continent, 8 moon, 9 planet, 10 splits worlds / star / universe.
Extraction output per being: `power_id` or `power_id:magnitude`. Grant: give the first N powers needed in priority order (`ARCHETYPE_GRANTS.tsv` shows ordered examples for Superman, Kenshiro, Goku, Jotaro, Flash analogs).
Existing powers come from NeoOrigins 2.2.30; gaps are composed from NeoOrigins action types in `powers/` (namespace diaithirpowers). Time stop is an approximation (slowness 254 plus weakness and fatigue in 32 blocks for 5 s). Rebuild: `python3 -I tools/powers/gen_power_pool.py data/powers` (S6960). Copy of the lists: /mnt/project-files/plans/powers/.

Matching: `keywords_strong` hit = grant (magnitude from scale words); `keywords_weak` hit alone = low confidence (magnitude 1-2, grant only if the being's `realms` matches or it needs more powers); `realms` (regex on the Library realm) strengthens a weak hit. Ki Reserve: realm Ki is the main signal (the text "Ki realm" is not a ki mention).

## What magnitude m (1-10) changes
- time_stop: radius 8+4m blocks, duration 1+m s, cooldown 65-5m s. telepathy: radius 16+6m, glow 5+3m s.
- flight: base flight plus flying speed +10% per step. blink: range 8+6m blocks, cooldown shrinks. phase: depth 2+2m blocks. dash: power 0.8+0.3m. levitation: 2+m s, higher amplifier from 4.
- fireball 2+1.5m dmg; ki_blast 2m; energy_beam 2.5m; whirlwind 1+m; flying_sword 2+2m; vibrating_palm 2m; repulse 1+0.7m; freeze breath slowness 1+m/2 plus 0.5m dmg. Radius and cooldown improve with m.
- super_strength +2 attack dmg/step; super_speed +25% move speed/step; invulnerability damage taken 0.9 to 0.02; regeneration level up to 4; barrage attack speed +0.4/step; pressure_strike +6% damage/step; qi_heal regen and duration.
- Base-power ones (glide, spectral_flight, hard_body, iron_shirt, immortal_body, invisibility, giant_size, dragon_form, ki_resource): the NeoOrigins power plus a boost by slot (mobility +4% move speed/step; defense +1.5 armor and +2 max health/step; utility +4 follow range/step).
