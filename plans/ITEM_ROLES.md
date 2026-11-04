# Item roles (Marlon rule 11-03: every item has a real role)
Registry list: 32171 priced item ids in DiaithirRPG `claude/pack-v1-3` (`economy/kubejs/data/diaithir/prices.json`; no server dump exists in the repo, so this is the closest full list). Pack-layer use scan: `tools/item_roles/scan_uses.py`.
- Strong pack-layer use (recipe, quest, Codex, loot or cuisine file mentions it): 1167
- Needed a role: 31004; roles assigned so far: 29886; still unassigned: 1118
- Zero mentions anywhere in the pack layer (true orphans): 5550
- Caveat: mod-internal recipes live in the jars and are not scanned, so 'no use' means no hookup in OUR layer (Age station, vendor, quest, Codex).
## Rules applied
Role may be an Age use, a material with real properties (density, strength) for vehicles/ships/rails/structures, or anything useful Minecraft never gave it. Genuinely decorative items stay `decor`. Every role lists 2-5 cross-system links.
## Role classes
|class|items|
|---|---|
|structure|6330|
|material|6017|
|machine_part|3100|
|storage_container|2598|
|automation|2537|
|decor|2427|
|tool_weapon|2126|
|rite_ingredient|1558|
|food_drink|992|
|other|812|
|energy_fuel|514|
|station_input|224|
|currency_trade|185|
|vehicle_part|180|
|ammo|138|
|medicine_rite|69|
|rail_part|42|
|ship_part|37|

## Cross-system link counts (low = under-integrated system)
|system|items linked|share|
|---|---|---|
|building|15255|51.0%|
|machines|9527|31.9%|
|economy|7059|23.6%|
|progression|6438|21.5%|
|storage|6130|20.5%|
|food|3844|12.9%|
|energy|3616|12.1%|
|circuit|3241|10.8%|
|rites|2864|9.6%|
|codex|2797|9.4%|
|vehicles|2436|8.2%|
|ships|2343|7.8%|
|munitions|1815|6.1%|
|quests|1247|4.2%|
|spoilage|1215|4.1%|
|autonomy|981|3.3%|
|rail|953|3.2%|
|npc_wages|847|2.8%|

## Isolated or thin systems (under 2% of items linked): none
These need a pass: either real parts are missing (vehicle/ship/rail part items, munitions, circuit) or roles should route items into them.

## Decor-only: 2137 items (7.2%), kept decorative. Highest-decor namespaces:
|namespace|items|decor|
|---|---|---|
|bibliocraft|2302|707|
|productivetrees|3528|170|
|minecraft|1207|156|
|mekanismtools|318|154|
|lightmanscurrency|359|145|
|forestry|2008|122|
|aether_ii|1048|61|
|enderio|954|57|
|mcwtrpdoors|214|53|
|cabletiers|648|51|
|securitycraft|640|38|
|farmersdelight|53|34|
|pneumaticcraft|230|30|
|comforts|34|28|
|tconstruct|896|28|
|occultism|693|26|
|mcwfurnitures|716|25|
|biomesoplenty|425|24|
|mysticalagriculture|687|21|
|theurgy|452|19|
|actuallyadditions|249|17|
|mcwroofs|621|17|
|mcwdoors|270|15|
|utilitarian|56|13|
|jousting|19|12|

## Files
`plans/ITEM_ROLES.csv` (id, role_class, role, where, props, links, decor_only), `plans/ITEM_ROLES_ORPHANS.txt` (zero-mention ids).

## Ages (Age balance thread ruling 11-04)
`age` column in the CSV = tech_ages.json (item/decided entry, else namespace), which wins. `draft_age` = Haiku's station Age, a suggestion used only where tech_ages has no row; items with neither have an empty age and need one. Drafts that differ from tech_ages were not applied, so the thin Ages stay as tech_ages sets them.
