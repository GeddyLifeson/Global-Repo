# V1 audit against the plans (2026-11-04 14:10Z)

Question (Marlon): are we close, and is everything cross-compatible, integrated, textured and complete? Honest answer: **not close to proven.** Most things are built, but almost none are proven together. No full-pack client join has ever passed.

Audited: ports `claude/pack-v1-3-wave15` @ da34c034 (37 jars + 52 downloads = 89 files; jars are the 37 only, downloads could not be opened), the bot reports of 11-03 and 11-04, MERGE_ORDER, V1_PUNCHLIST, FINISH_PLAN, DRIVER, Bible. Detail: `V1_AUDIT_FEATURES.md` (61 rows), `V1_AUDIT_INTEGRATION.md`. Scripts and raw output: /mnt/project-files/audit/v1-2026-11-04/. All checks are static unless stated; I did not boot the pack.

## Verdict
| Measure | Value |
|---|---|
| Feature rows audited | 61 |
| Seen working in a real client (light per-module cloud packs only) | 14 (23%) |
| Headless/server-only proof | 9 (15%) |
| Code exists, never run (in pack or only in an open PR) | 29 (48%) |
| Design only | 5 (8%) |
| Missing | 4 (6%) |
| Proven in the full pack | 0 |

Rough "done" figure: about 60% built in some form, about 25% shown working anywhere, 0% proven together. The plan itself says the first full join will need 2 to 4 crash-fix cycles.

## Note on "the master plan"
The Shardfall master plan artifact (57d08605...) is the Unreal Engine production plan (6-game teardown, 54-month phases). It never mentions Ages, Panscriptum or the pack, so it cannot be checked against this work. The real V1 plan lives in plans/ (FINISH_PLAN, V1_PUNCHLIST, DRIVER) and the Bible. Someone should decide which document is the master for the Minecraft pack; I used the plans/ files.

## Top gaps (ranked)
1. **No full-pack client join.** The 11-03 join crashed 13 s in (ships jar). Pack is still 89 files against a 20-40 target, and the "no PC client until 20-40" rule blocks the join that finds the rest.
2. **Fixes sit in unmerged PRs.** Vehicles (#225 #345 #221 mount/drive fixes), animation, planets picker, Age Wardens, magic V/VI, canning, munitions items, megastructures, wages, stations. The pack's own vehicle jars may still have the 11-03 defects.
3. **Missing textures from absent mods (new finding).** diaithirwoodvariants has 5,060 block models; 3,542 reference `productivetrees:` textures and productivetrees is not in the pack (also forbidden_arcanus 122, buildinggadgets 24, rusticdelight 12, buzzier_bees 6). Those are about 2,070 items that will render as missing texture unless productivetrees is added. Also 310 more model texture refs inside our own namespaces do not resolve (megacells 97, appflux 39, diaithirwoodvariants 37, integrateddynamics 18, extendedae 13; some may be supplied by the ae2 download at runtime), plus 321 broken parent models (pneumaticcraft 64, extendedae 41, betternether 32, mcwdoors 28, industrialforegoing 19). Not boot errors but magenta blocks in game.
4. **Placeholder and low-quality art.** 92k textures in the jars. 3,400 files are byte-identical copies in groups of 8 or more (chisel pillars 34x, silentgear 68x). About 5,000 textures use only one or two colours (chisel 2,063, tconstruct 644, antique_atlas 252, mts 229, spell_engine 145). 16 px share is 80%+ in equivox, silentgear, croptopia, storagedrawers, diaithirtrees, diaithir_classes and others. Blank textures: silentgear 169, chisel 46. Known weak: firearms and furnishings templates, planet blocks and items (art-quality note 11-03). 681 items have a lang key but no model, untamedwilds 57, tconstruct 101.
5. **Age gating holes.** 5,989 of 47,200 items (12.7%) have no Age: diaithirtrees 1,141, diaithir_planets 840, regions_unexplored 713, biomesoplenty 336, lightmanscurrency 333. The two Age tables disagree on 324 ids and 273 table ids name items that do not exist.
6. **Every-item-role.** 17,850 of 43,183 items (41%) appear in no recipe and no loot or trade; 2,164 are strict orphans (aerialhell 207, aether_ii 192, all 81 boss items). Java-side drops are invisible to this check, so it is an upper bound, but the rule (no dead content) is not met by any measure.
7. **Codex coverage 26%** of items (12,385 of 47,200). Zero for chisel, woodvariants, trees, eternal_starlight, planets, create. 2,165 codex ids name nothing in the pack. The Library lore records link to no game object, so Panscriptum==modpack parity is design only. **Civilopedia: no code or PR anywhere.**
8. **Language.** 2,729 items (6.3%) and 801 blocks have no English name key (enderio 612, silentgems 378, mysticalagriculture 351, create 264); about 5 of 7 are variants, but some show raw ids.
9. **Integration traps.** `create` content ships as modId diaithir_create, so every `mod_loaded:create` guard and optional dep stays off (also jei, emi, buildinggadgets, productivetrees). Adventure suite declares casinodeco and casinosound incompatible while shipping them. 3 `diaithir:foundry_*` recipe ids exist nowhere (probably wrong namespace diaithirfoundry). 71 tag entries point at undefined stellaris and creatureutils ids. 1 duplicate registry id (nutritionalbalance:lunchbox_3d).
10. **Boot data errors.** Wave14's 168 could not be reproduced here (no boot log found, no full-pack boot in the cloud container). The static scan finds the likely sources above (about 23 dangling recipe ids, 71 tag ids, unresolved tags such as diaithir_integration:lorgchraoibhe/*, theurgy:alchemical_sulfurs/*). Needs the server-boot log from the pack thread to attribute each of the 168.

## Planned, but nothing found anywhere
Civilopedia; autonomy (stub that counts any rider as crew, no wages); narrow-gauge payload and steam-crew enforcement (found unenforced); Keelwright power layer, HP and mass tables; Panscriptum "Library to pack" forms and any parity checker; Future/Rodos era rows (need PC canon/eras.csv); keybinds.txt (#218, #322 unmerged, Tool Belt R collides); Off Grid compat test.

## Real-client bugs known and not yet confirmed fixed
Space-key tank fire; narrow-car payload; trade screens (guard renderer NPE, PackVersionCheck kicks unversioned clients, empty ItemStack disconnect); `/diaithircargo` regression in n345; fauna with capitals in species ids crash the client; Better Animations (#317) has no renderer; culture picker, Codex screens, upgrade menu, wiretech, Foundry never opened in any client.

## Finish date
Plan figures: best 11-09, realistic 11-12 to 11-16, bad 11-28+. Evidence above says the plan's realistic case assumed the join takes 2 to 3 cycles and the art/integration gaps are small. They are not small (woodvariants art alone is a 2,000-item decision), and the join has no history. My estimate: **realistic 11-20 to 12-01, best 11-16, bad after the 11-26 API key expiry.** Dates stay soft until one full-pack client join runs.

## Fix routing (coordinator)
1. Decide productivetrees: add it (check licence/26.1 build), or remove/redirect the 3,542 woodvariants models.
2. Merge the vehicle, animation, picker and Age Warden PRs; rebuild; swap ships jar to .16.
3. Run one early full-pack join (needs the 18:55 rule lifted) to start the crash-fix cycles now.
4. Job for compute lane: Age + lang + codex gap fill for the namespaces listed (data, not features).
5. Texture pass: dedupe/replace the blank, one-colour and magenta files; firearms and furnishings archetypes first.
6. Fix the `create` modId guard, casino incompatible flags, foundry ids, stellaris tags.
7. Pull the wave15 boot log and attribute the 168 errors.
