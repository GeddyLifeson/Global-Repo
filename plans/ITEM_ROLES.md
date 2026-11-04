# Item roles (Marlon rule 11-03: every item has a real role)
Registry list: 32171 priced item ids in DiaithirRPG `claude/pack-v1-3` (`economy/kubejs/data/diaithir/prices.json`; no server dump exists in the repo, so this is the closest full list). Pack-layer use scan: `tools/item_roles/scan_uses.py`.
- Strong pack-layer use (recipe, quest, Codex, loot or cuisine file mentions it): 1167
- Needed a role: 31004; roles assigned so far: 23824; still unassigned: 7180
- Zero mentions anywhere in the pack layer (true orphans): 5550
- Caveat: mod-internal recipes live in the jars and are not scanned, so 'no use' means no hookup in OUR layer (Age station, vendor, quest, Codex).
## Rules applied
Role may be an Age use, a material with real properties (density, strength) for vehicles/ships/rails/structures, or anything useful Minecraft never gave it. Genuinely decorative items stay `decor`. Every role lists 2-5 cross-system links.
## Role classes
|class|items|
|---|---|
|structure|5076|
|material|4697|
|machine_part|2466|
|automation|2092|
|storage_container|2079|
|decor|1899|
|tool_weapon|1706|
|rite_ingredient|1273|
|food_drink|820|
|other|629|
|energy_fuel|412|
|station_input|200|
|vehicle_part|136|
|currency_trade|126|
|ammo|97|
|medicine_rite|47|
|rail_part|37|
|ship_part|32|

## Cross-system link counts (low = under-integrated system)
|system|items linked|share|
|---|---|---|
|building|12116|50.9%|
|machines|7659|32.1%|
|economy|5741|24.1%|
|progression|5199|21.8%|
|storage|4836|20.3%|
|food|3104|13.0%|
|energy|2967|12.5%|
|circuit|2528|10.6%|
|rites|2296|9.6%|
|codex|2248|9.4%|
|vehicles|1892|7.9%|
|ships|1803|7.6%|
|munitions|1445|6.1%|
|spoilage|1030|4.3%|
|quests|977|4.1%|
|autonomy|818|3.4%|
|rail|778|3.3%|
|npc_wages|697|2.9%|

## Isolated or thin systems (under 2% of items linked): none
These need a pass: either real parts are missing (vehicle/ship/rail part items, munitions, circuit) or roles should route items into them.

## Decor-only: 1645 items (6.9%), kept decorative. Highest-decor namespaces:
|namespace|items|decor|
|---|---|---|
|bibliocraft|1919|561|
|mekanismtools|288|137|
|productivetrees|2743|131|
|minecraft|897|123|
|forestry|1481|96|
|lightmanscurrency|239|61|
|enderio|745|53|
|mcwtrpdoors|214|53|
|aether_ii|894|50|
|farmersdelight|53|34|
|pneumaticcraft|178|29|
|comforts|34|28|
|occultism|600|25|
|biomesoplenty|365|24|
|cabletiers|528|24|
|mcwfurnitures|540|21|
|theurgy|276|19|
|actuallyadditions|195|16|
|mcwroofs|501|16|
|tconstruct|723|16|
|mcwdoors|240|15|
|securitycraft|443|13|
|utilitarian|56|13|
|mysticalagriculture|543|12|
|silentgear|191|9|

## Files
`plans/ITEM_ROLES.csv` (id, role_class, role, where, props, links, decor_only), `plans/ITEM_ROLES_ORPHANS.txt` (zero-mention ids).
