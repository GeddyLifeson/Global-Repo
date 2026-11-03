# BUILDING MATERIALS: manufacturing lines as evolution chains (draft 1, 2026-11-03)

Answer to "should we add CFS manufacturing and the like": yes. Each line below is one chain that changes form through the Ages, not one machine. Every stage is a node in PROGRESSION (`needs`, `makes`, `age`, `module`, `q.<id>`), gated by `gate.<Age>`, in SI units (UNITS.md), with upgrade slots (UPGRADES.md). No new jar: all stages fold into existing consolidated modules (Foundry/tech for machines, blocks-decor for the blocks, Keelwright for hull stock, transport for vehicles).

Age names: I Ancient, II Ailean, III Holy, IV Sundering, V Strangers, VI Kingdom, VII Dubhan, VIII Future, RODOS. Age placement below is a first proposal; tech-by-age.md (DiaithirRPG) wins on conflict.

## 1. Chains (one row per stage; output is a shared `c:` tag so the next stage and other mods accept it)
| Line | I | II | III | IV | V | VI | VII | VIII / RODOS |
|---|---|---|---|---|---|---|---|---|
| Framing (studs, tracks, joists) | hewn timber post and beam | pegged and sawn timber | wrought iron strap and bar framing | cast and rolled iron sections | Bessemer steel angles and channel | hot-rolled steel I-section frames | cold-formed steel (CFS) roll-forming line: coil to C-stud, track, joist | robotic CFS plus alloy sections / shard-lattice frame |
| Reinforcement (rebar, mesh) | withies in daub | iron rods in masonry | wrought iron bars | cast iron ties | mild steel round bar | ribbed rebar and wire mesh | pre-tensioned and post-tensioned strand | composite and shard-fibre rebar |
| Structural beams (I-beam, plate) | log beams | iron-shod beams | iron plate girders | riveted rolled shapes | steel I-beams | welded plate girders | high-strength low-alloy beams | alloy and lattice beams |
| Cement and concrete | lime mortar | Roman-style pozzolan concrete | hydraulic lime | rotary-kiln cement | Portland cement | reinforced concrete mixing | precast and prestressed plant, concrete trucks | self-healing and printed concrete |
| Precast and block | mud brick, fired brick | cut and fired masonry | moulded tile | hollow block | concrete block | precast panels and slabs | prestressed planks, tilt-up panels | printed modular units |
| Wall boards (drywall) | wattle and daub | lime plaster on lath | gypsum plaster | plaster of Paris boards | plasterboard | gypsum drywall line | fire-rated and moisture boards | smart panels |
| Glass | blown glass | crown glass | cylinder sheet | plate glass | rolled and wired | float glass line | laminated and tempered | switchable glass |
| Road surface | beaten earth, flagstone | cobble and gravel roads | pitch and macadam | tar macadam | asphalt mix plant | paving machines, road rollers | reinforced concrete highway | self-repairing surface |
| Insulation and cladding | thatch, turf | slate, shingle | lead sheet, tile | rock wool | glass wool | foam board, metal cladding | CFS-backed cladding panels | aerogel panels |

## 2. How it ties into the rest of the game
- **Resources (shared tags):** each output is a `c:` tag per INTEGRATION.md (`c:framing/cfs`, `c:rebar`, `c:beams/steel`, `c:concrete/precast`, `c:wallboard`, `c:glass_blocks`, `c:asphalt`). Inputs reuse Foundry steel, plate and coil tags, Create-style rolling and pressing, coal, lime, gypsum, sand, aggregate from worldgen.
- **Consumers:** cranes and assembly yards (structure kits need beams, framing and slabs), settlements (buildings upgrade by material tier, so a town can't pass an Age on timber alone), Keelwright hull stock (plate, beams), roads and rail (asphalt, concrete, ballast), concrete trucks and road rollers (trucks thread: they consume cement, aggregate and asphalt, and are gated by the same Age), economy (each product is a tradable good with a company recipe), Codex entry and quest per stage.
- **Evolution rule:** a later stage never deletes an earlier one. Older stages stay craftable at lower speed and quality; each upgrade is a Factorio-style module or line refit that raises throughput and lowers W per kg. Worlds keep old buildings valid via id migration.
- **Panscriptum:** stage names, descriptions and any assay come from real page text only; nothing invented. Names go through the 130-culture pipeline.

## 3. Mod sources (mod-first rule; status unverified, to check before building)
| Need | Plan |
|---|---|
| Rolling mills, presses, casting | existing Foundry and Create port nodes first; fold stages in |
| Concrete, asphalt, rebar blocks | check latest 26.1 NeoForge builds of Modern Industrialization, Mekanism and Create addons; otherwise clean-room blocks in blocks-decor |
| CFS roll-forming, precast plant, drywall line | no known 26.1 mod; clean-room machines in the Foundry module |
| Glass line | extend existing glass node (`tech.glass`) with stages |
| Concrete trucks, rollers | trucks thread owns vehicles; this plan supplies the material items and Age gates |
Next step is a licence and 26.1 build check per row (Modrinth API dump works from the cloud), logged in a CSV, then node entries added to `graph.json` and run through `check_progression.py`.

## 4. Open items for the coordinator
- Which consolidated module owns the new machines (suggest Foundry/tech) and which owns blocks (blocks-decor rewrite).
- Truck and crane threads should read section 1 for material names so ids match.
