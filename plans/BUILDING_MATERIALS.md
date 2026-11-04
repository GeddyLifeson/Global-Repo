# BUILDING MATERIALS: a lean set, each earning its place (draft 2, 2026-11-03)

Draft 1 had nine lines including cold-formed steel framing, rebar, precast and drywall as their own chains. Marlon cut that: no standalone cold-formed steel, no Roll-Former. Rule now: **one entry per real material class, and a class only exists if it has a distinct property or use no other class covers.** Light-gauge steel framing is just a late stage of the steel set. Rebar and precast are stages of concrete. Drywall is a stage of wall lining.

Each class is an evolution chain through the Ages, fed by existing Foundry tags (`c:ingots/steel` etc.), gated by `gate.<Age>`, SI units (UNITS.md), upgradeable (UPGRADES.md), no new jar (stations and items go in the Foundry module, blocks in blocks-decor). Age names: I Ancient, II Ailean, III Holy, IV Sundering, V Strangers, VI Kingdom, VII Dubhan, VIII Future, RODOS. Placement is a proposal; tech-by-age.md wins.

## 1. The set (9 classes)
| Class | Distinct job | Stages by Age |
|---|---|---|
| Timber | cheap, light, burns | I post and beam, II sawn and pegged, III glulam-style engineered timber (VII) |
| Masonry (mud, fired brick, stone) | fireproof, heavy, good in compression | I mud and fired brick, II cut stone, IV block |
| Lime, cement, concrete | moulded, heavy, blast resistant | II pozzolan concrete, IV kiln cement, V Portland, VI reinforced (steel bars inside), VII precast and prestressed, VIII self-healing |
| Iron and steel sections | span and tension, takes heavy loads | III wrought bar, IV cast and rolled iron, V steel angle and plate, VI I-beams, VII light-gauge studs and joists (the old CFS idea), RODOS alloy lattice |
| Glass | light and view, brittle | I blown, III sheet, V plate, VI float, VII laminated and tempered |
| Wall lining (plaster, board) | cheap interior fire rating and finish | II lime plaster, IV gypsum plaster, V board, VI fire-rated board |
| Roofing and cladding | keeps weather out | I thatch, II slate and shingle, III tile, V metal sheet, VII insulated panel |
| Road and ground surface | movement speed, vehicle load | I flagstone, II cobble, IV macadam, V asphalt, VI concrete road |
| Insulation | indoor warmth under diaithir-climate | I turf and thatch, IV rock wool, V glass wool, VII foam, VIII aerogel |

Shard and alloy composites are the RODOS stage inside steel and concrete, not a tenth class.

## 2. Property table (the real role of each class; all blocks and items read the same numbers)
Per block or per metre, SI, approximate real-world orders of magnitude, tuned in game later:
| Property | Where it bites in game |
|---|---|
| density kg/m3 | build weight: ships (Keelwright), vehicles, crane lift_kg, ground load |
| strength / span | max unsupported span and height before a structure needs more support; assembly yards and cranes check it |
| fire rating | spreading fire and lava damage; timber burns, masonry and concrete do not |
| blast and mining resistance | sieges, bosses, raids; concrete and steel last |
| thermal conductance W/(m2 K) | indoor temperature in the climate module; insulation and glass matter in cold or hot biomes |
| light transmission | glass only |
| cost per unit | the sink that pushes players up the tree: later stages cost more Foundry output but do more per unit |

## 3. How it ties into the game
- **Shared tags** per INTEGRATION.md (`c:planks`, `c:bricks`, `c:concrete`, `c:beams/steel`, `c:glass_blocks`, `c:wallboard`, `c:roofing`, `c:road_surface`, `c:insulation`) so other mods' items work as inputs and outputs.
- **Consumers:** settlements (a building tier needs a material tier, so a town can't pass an Age on timber), assembly yards and cranes (structure kits need beams, slabs, glass), Keelwright hull stock, roads and rail, the trucks thread's concrete trucks and road rollers (they consume cement, aggregate, asphalt), economy (tradable goods), Codex entry and quest per class.
- **Evolution rule:** older stages stay craftable at lower speed and quality; refits and upgrade modules raise throughput. Old builds stay valid through id migration.
- **Panscriptum:** names and descriptions come from real page text only; names go through the 130-culture pipeline.

### Tags other threads consume (requested by the megastructure threads, Global-Repo #33 and diaithir-ports #265)
| Tag | Age | Class and stage | Note |
|---|---|---|---|
| `c:stone/cut` | III | masonry, cut stone (table stage is Age II; the tag opens at III once cut stone is craftable at a station) | stand-in values today: stone bricks |
| `c:timber/beam` | III | timber, sawn structural beam used for centering and framing | stand-in values today: oak planks |
| `c:tether/ultrahigh` | VIII | steel class, ultra-high-strength tether fibre (composite stage ahead of the RODOS lattice) | no real item yet |
Replace the stand-ins in diaithir-ships when the real items exist. Depot rule from the requesting thread: 1 t per pallet item, 20 t if the item also carries `c:container/bulk`. Table rows `timber_beam` and `steel_tether_fibre` get added when the stages are built.

## 4. Build order (when Marlon says go)
1. Property table as one data file read by blocks, structures, climate and fire.
2. Concrete line first (touches trucks, rollers, roads, cranes), then steel sections, glass, roads, lining, roofing, insulation.
3. Each stage: station recipe (Foundry stations framework already supports parts, assemblies, processes, steam power and kept tool items), block, Codex entry, quest, Age gate, selftest.
Mod sources: check latest 26.1 builds of Create-style addons and Modern Industrialization first; default is clean-room in the Foundry and blocks-decor modules.
