# Munitions containers: intended ids and tags (contract for animation threads, 11-03, NOT BUILT YET)
Namespace `diaithircrafting`. Treat every id below as optional until the container PR merges.

## 1. Item ids (class = pistol, smg, rifle, sniper, lmg, shotgun, musket, launcher, energy)
- magazine: `magazine_pistol`, `magazine_smg`, `magazine_rifle`, `magazine_sniper`, `magazine_lmg_box`
- drum: `drum_smg`, `drum_lmg`
- clip (stripper): `clip_rifle`
- speedloader: `speedloader_pistol` (revolvers)
- belt: `belt_lmg`; link: `link_lmg` (belt segment part, a real item used in crafting)
- shotgun: loose shells, round id `shell_shotgun`; musket: `cartridge_musket` (paper cartridge); launcher: rounds go in directly (no container); energy: `cell_energy`
- ammo box (bulk, not fed to a gun): `ammo_box_small`, `ammo_box_large`
- casings: NOT items. Spawn as client-only particles. A recycled `casing_scrap` item may come later.

## 2. Gun class to container
pistol: magazine_pistol or speedloader_pistol; smg: magazine_smg or drum_smg; rifle: magazine_rifle or clip_rifle; sniper: magazine_sniper; lmg: belt_lmg, magazine_lmg_box or drum_lmg; shotgun: shell_shotgun (tube, no container); musket: cartridge_musket; launcher: direct round; energy: cell_energy.

## 3. How to read it
- Item tags: `c:ammo_container/magazine|drum|clip|speedloader|belt|box|cell` on containers; gun items carry `diaithircrafting:uses_container/<kind>` for each kind they accept, plus `diaithircrafting:ammo_class/<class>`.
- Data component on container stacks: `diaithircrafting:ammo_container` = {class, capacity, count, round (item id)}; empty form is count 0. Animation can show a full, partial or empty container from count/capacity.
