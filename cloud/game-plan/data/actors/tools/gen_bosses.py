from common import *
CLS={'Shard-bearer':(3.0,120,1.0,'A031'),'Citadel':(2.4,100,0.6,'A032'),'Field':(1.6,90,0.4,'A033'),'Site':(1.3,80,0.1,'A034'),'Raid':(30.0,150,0.5,'A035'),'Final':(3.5,130,1.0,'A031'),'Undervault':(1.6,100,0.4,'A034')}  # Ember mults halved by B08 SIM-01
# archetype move templates: name, type, mult, poise, startup, active, recovery, range, aoe, tracking, counter, phase
ARC={
'KNIGHT':[('Diagonal Slash','Slash',1.2,30,24,6,30,3.0,0,'High','Roll through / parry',1),('Lunging Thrust','Pierce',1.4,35,30,6,36,6.0,0,'Medium','Roll sideways / parry',1),
 ('Delayed Overhead','Slash',1.8,50,52,6,48,3.5,0,'High until frame 40','Roll late',1),('Three-Hit Chain','Slash',1.0,25,20,5,26,3.0,0,'High','Block or roll each',1),
 ('Leaping Strike','Blunt',2.0,60,40,8,60,8.0,2.0,'Locks at jump apex','Roll toward',1),('Shoulder Charge','Blunt',1.2,50,26,20,40,10,0,'Low','Roll sideways',1),
 ('Grab','Grab',2.6,0,34,8,70,2.5,0,'Medium','Roll; unblockable',2),('Infused Chain','Slash',1.3,30,22,6,30,3.5,1.5,'High','Roll; element trail lingers 2 s',2)],
'CASTER':[('Bolt Volley','Weave',0.8,10,30,0,30,30,0,'Homing light','Sprint sideways',1),('Ground Sigil','Weave',1.6,40,60,10,40,20,4.0,'Placed under player','Leave circle',1),
 ('Blink Away','None',0,0,8,10,10,10,0,'-','Close distance',1),('Staff Sweep','Blunt',1.1,30,22,6,30,3.0,0,'High','Block / parry',1),
 ('Orbiting Shards','Weave',0.6,6,40,300,30,4.0,4.0,'Follows caster','Strike between orbits',1),('Beam','Weave',2.2,40,70,60,50,40,0,'Slow turn 45 deg/s','Get behind cover / roll through edge',2),
 ('Summon Adds','Summon',0,0,60,0,40,0,0,'-','Kill adds or stance caster',2),('Nova','Weave',2.4,70,90,8,70,0,7.0,'-','Run out 7 m',2)],
'BEAST':[('Bite','Pierce',1.3,30,22,6,30,3.0,0,'High','Roll toward flank',1),('Claw Swipe x2','Slash',1.1,30,20,6,28,3.5,0,'High','Roll each',1),
 ('Pounce','Blunt',1.8,60,36,10,50,12,2.0,'Locks at leap','Roll toward',1),('Tail Sweep','Blunt',1.4,50,30,10,40,5.0,0,'360 deg','Roll away or jump',1),
 ('Roar','None',0,0,30,60,30,0,10,'-','Stay out of 10 m (stagger + 3 s fear)',1),('Charge','Blunt',1.6,60,40,40,60,25,0,'Low after 1 s','Roll sideways',1),
 ('Frenzy Combo x4','Slash',1.0,25,18,5,24,3.5,0,'High','Block or retreat',2),('Elemental Breath','Weave',2.0,40,50,90,50,15,0,'Sweeps 60 deg','Get under / behind',2)],
'GIANT':[('Stomp','Blunt',1.6,70,40,8,50,0,4.0,'-','Roll out',1),('Fist Slam','Blunt',2.0,80,50,8,60,6.0,3.0,'Medium','Roll sideways',1),
 ('Sweep','Blunt',1.6,60,44,14,50,8.0,0,'Wide arc','Roll toward the arm',1),('Grab and Crush','Grab',3.0,0,40,10,80,4.0,0,'Medium','Roll; unblockable',1),
 ('Boulder Throw','Blunt',1.8,60,60,0,50,40,3.0,'Aimed at release','Sprint sideways',1),('Body Slam','Blunt',2.6,100,70,10,90,0,6.0,'-','Get out of shadow',2),
 ('Earthquake','Blunt',1.2,40,80,60,60,0,15,'-','Jump each pulse (3 pulses)',2),('Elemental Fist','Blunt',2.2,80,46,10,60,6.0,4.0,'Medium','Roll late',2)],
'MACHINE':[('Piston Punch','Blunt',1.6,60,30,6,40,5.0,0,'Medium','Roll sideways',1),('Gatling Sweep','Bullet',0.25,2,40,120,40,40,0,'40 deg/s','Cover',1),
 ('Missile Pod','Blunt',1.2,40,60,0,50,60,3.0,'Homing weak','Dodge on impact marker',1),('Saw Sweep','Slash',1.4,40,36,30,40,5.0,0,'Wide','Jump or roll back',1),
 ('Overheat Vent','Weave',1.8,40,60,40,120,0,5.0,'-','Back off then punish vents (x2 damage)',1),('Rail Shot','Bullet',2.8,80,90,6,60,100,0,'Locks 0.4 s before fire','Break line of sight',2),
 ('Drone Release','Summon',0,0,60,0,40,0,0,'-','Kill drones (they repair 2%/s)',2),('Core Overload','Weave',3.0,100,120,10,120,0,12,'-','Hide behind pylons',2)],
'FLYER':[('Dive Bomb','Blunt',2.0,70,50,10,60,30,3.0,'Locks at 1 s','Roll toward',1),('Wing Buffet','None',0.6,40,30,30,30,0,8.0,'-','Brace / block',1),
 ('Strafing Breath','Weave',1.6,30,40,90,40,30,0,'Line along path','Run perpendicular',1),('Tail Spike','Pierce',1.4,30,26,6,34,6.0,0,'High','Roll',1),
 ('Grounded Bite','Pierce',1.4,30,22,6,30,3.5,0,'High','Roll',1),('Hover Barrage','Weave',0.8,10,40,120,40,40,2.0,'Rain on player','Keep moving',2),
 ('Crash Landing','Blunt',2.6,100,80,10,100,0,8.0,'-','Leave the shadow',2),('Sky Spiral','Weave',2.2,50,90,60,80,0,12,'-','Hide behind rock',2)],
'MULTI':[('Head Bite (per head)','Pierce',1.2,30,24,6,30,6.0,0,'High','Roll; heads attack 0.4 s apart',1),('Coil Sweep','Blunt',1.4,50,36,14,40,8.0,0,'Wide','Jump',1),
 ('Spit Volley','Weave',0.8,10,40,0,30,25,2.0,'Each head aims','Sprint',1),('Brood Call','Summon',0,0,60,0,40,0,0,'-','Kill adds',1),
 ('Grapple Pin','Grab',2.4,0,40,10,70,5.0,0,'Medium','Roll; unblockable',2),('Regrow','Heal',0,0,80,0,40,0,0,'-','Burn neck stumps within 6 s to stop',2),
 ('Toxic Pool','Weave',0.5,0,50,600,30,0,5.0,'-','Leave pool',2),('All-Heads Crash','Blunt',2.8,100,70,10,90,8.0,4.0,'Medium','Roll late sideways',2)],
'DUO':[('Twin Cross','Slash',1.3,30,26,6,30,3.5,0,'High','Roll between them',1),('Swap Places','None',0,0,10,10,20,20,0,'-','Track the one behind you',1),
 ('Pincer Rush','Pierce',1.6,40,40,20,50,12,0,'Low','Roll toward one',1),('Linked Beam','Weave',1.8,30,60,90,40,20,0,'Between them','Never stand between',1),
 ('Mirror Combo x3','Slash',1.0,25,20,5,26,3.0,0,'High','Block each',1),('Revive Partner','Heal',0,0,180,0,30,0,0,'-','Interrupt (3 s channel) or kill both within 20 s',2),
 ('Synced Slam','Blunt',2.4,80,60,10,80,0,5.0,'-','Roll away from both',2),('Shadow Clone','Summon',0,0,40,0,40,0,0,'-','Clones have 1 HP',2)],
}
# boss: id, name, class, region, archetype, element, phases, height m, weak points, signature moves [(name,type,mult,phase,startup,telegraph)], extra notes
B=[
('VAEL','Vael the Ember Regent','Shard-bearer','R1','KNIGHT','Ember',3,3.2,'Crown Shard x1.5 when stance broken',[('Regent\'s Pyre','Weave',2.4,2,70,'Raises sword skyward, ring of fire 6 m forms'),('Ash Coronation','Weave',3.0,3,110,'Kneels, crown flares 1.8 s, then 12 m blast'),('Cinder Waltz x5','Slash',1.0,3,18,'Spins sword, embers trail')],'Phase 3 arena edges burn (5 dmg/s)'),
('CORSA','Corsa, Storm Admiral','Shard-bearer','R2','CASTER','Storm',3,2.4,'Signal mast backpack x1.4',[('Broadside','Bullet',2.0,1,80,'Whistles; 4 cannon lines painted on deck'),('Lightning Rod','Weave',2.4,2,60,'Plants harpoon; strikes it after 1.5 s, 5 m'),('Maelstrom','Weave',1.0,3,90,'Arena rotates; wind pulls 2 m/s toward center')],'Fight on a beached ark deck; rain on'),
('SORREL','Sorrel of the Bloom','Shard-bearer','R3','CASTER','Bloom',2,2.2,'Heart-flower x2.0 (opens after Root combo)',[('Bramble Cage','None',0,1,40,'Vines rise in 8 m ring, Root 120 buildup'),('Spring\'s Wrath','Weave',2.6,2,80,'Blossoms open across arena, 1.3 s'),('Seedling Host','Summon',0,1,60,'Scatters seeds; 4 Thornling adds')],'Arena grows cover over time'),
('BRANNOCH','Brannoch Iron-Choir','Shard-bearer','R4','GIANT','Iron',3,6.0,'Choir pipes on back x1.5; legs (stance x1.3)',[('Iron Hymn','Weave',2.2,2,70,'Pipes sing low; shockwave rings 3 x 5 m'),('Anvil Fall','Blunt',3.2,3,100,'Leaps 20 m up, shadow tracks player'),('Shattering Choir','None',0,3,60,'High note; Shatter 150 buildup to all within 10 m')],'Phase 2 armor plates fall (Defense -30%)'),
('RIME','Mother Rime','Shard-bearer','R5','CASTER','Frost',3,4.0,'Ice veil x1.5 after Ember Ward break',[('Whiteout','None',0,2,60,'Blizzard; visibility 10 m for 15 s'),('Glacier Lance','Pierce',2.6,1,50,'Ice spear forms over head 0.8 s'),('Frozen Choir','Summon',0,3,80,'Three ice statues revive as Rime Wardens')],'Frozen ground: rolls slide +1 m'),
('HOLLOWTWINS','The Hollow Twins','Shard-bearer','R6','DUO','Hollow',3,2.3,'Shared health; whichever is Drained takes x1.2',[('Eclipse Pact','Weave',2.8,3,100,'Twins merge into one; arena dims'),('Grief Mirror','None',0,2,40,'Copies the player\'s last Weave ability'),('Twin Unmaking','Weave',3.2,3,120,'Both rise; dark sphere grows 1.8 s')],'Two bodies, one HP pool; at phase 3 merge'),
('SPINEGATE','Warden of Spinegate','Citadel','R1','KNIGHT','Iron',2,3.0,'Gate-key on belt x1.3',[('Portcullis Drop','Blunt',2.4,1,70,'Points up; gates fall in 2 lanes'),('Spine Halberd Sweep','Slash',1.8,1,36,'Halberd pulled wide left'),('Rally the Garrison','Summon',0,2,60,'Horn; 3 Thorn Shieldmen')],'Arena: gatehouse with lanes'),
('CANTOR','The Drowned Cantor','Citadel','R2','CASTER','Storm',2,2.6,'Throat lantern x1.5',[('Tidal Psalm','Weave',2.0,1,70,'Water rises knee-high 10 s, Slow 30/s'),('Drowning Note','Weave',2.6,2,90,'Long held note; 3 bubble mines'),('Bell Toll','None',0,1,40,'Bell rings; stagger within 6 m')],'Partly flooded nave'),
('HALDEN','Ser Halden Unburied','Citadel','R3','KNIGHT','Hollow',3,2.4,'Open chest wound x1.4',[('Gravebind','Grab',2.8,2,40,'Reaches with off-hand, grey glow'),('Last Oath','Slash',3.0,3,90,'Plants sword, recites oath 1.5 s, 3-hit 360 combo'),('Buried Rise','Blunt',2.2,2,60,'Sinks into ground, erupts under player')],'Honorable: bows at start; free hit allowed'),
('GRAFTED','Grafted Engine','Citadel','R4','MACHINE','Iron',3,7.0,'Exposed reactor (after both arms broken) x2.0',[('Arm Graft Swap','None',0,2,40,'Swaps left arm: drill / cannon / claw'),('Reactor Breach','Weave',3.0,3,120,'Reactor glows red 2 s, 12 m'),('Conveyor Pull','None',0,1,30,'Floor belts pull 3 m/s to saws')],'Breakable arms 1,200 HP each at L46 scale'),
('YSSE','Choir Mother Ysse','Citadel','R5','CASTER','Hollow',3,3.0,'Mask x1.5',[('Lullaby','None',0,1,60,'Soft hymn; player Breath regen -50% for 10 s'),('Choir of Knives','Pierce',1.6,2,50,'Ring of 8 floating blades'),('Hymn of Unmaking','Weave',3.0,3,130,'Arena-wide; only Choir Barrier pillars protect')],'Counter-casts any Weave ability during phase 3'),
('LAMPLIGHTER','The Lamplighter','Citadel','R6','KNIGHT','Ember',3,2.8,'Lantern x2.0 (breaking it ends phase 2 early)',[('Wick Lash','Slash',1.6,1,26,'Lantern chain swings back'),('Lights Out','None',0,2,40,'Extinguishes lamps; dark 10 s, he is only visible by lantern'),('Final Flame','Weave',3.0,3,110,'Holds lantern high, 2 s, 15 m burst')],'Light/dark mechanic'),
('ASHCOLOSSUS','Ash Colossus','Field','R1','GIANT','Ember',2,12.0,'Knees (stance x1.5), head x1.5',[('Ashfall','Weave',1.2,2,80,'Shakes body; ash clouds rain 6 s'),('Magma Fist','Blunt',2.6,1,56,'Fist glows red 0.9 s'),('Collapse','Blunt',3.0,2,70,'Staggers forward when knees broken')],'Roams Cinderreach road at night'),
('NIGHTDRAKE','Night Drake','Field','R1','FLYER','Hollow',2,5.0,'Wings (ground it at 600 dmg each)',[('Moonless Dive','Blunt',2.4,1,60,'Vanishes in sky, screech 1 s'),('Shadow Breath','Weave',1.8,2,50,'Inhales, purple glow'),('Night Terror','None',0,2,40,'Fear 3 s if facing it')],'Spawns 20:00-04:00 only'),
('LEVIATHAN','Reef Leviathan','Field','R2','BEAST','Storm',2,9.0,'Gill plates x1.6',[('Breach','Blunt',3.0,1,90,'Water bulges under player 1.5 s'),('Tidal Wave','Blunt',1.6,2,80,'Rises, wave 30 m wide'),('Static Surge','Weave',2.0,2,60,'Body crackles, water electrified 3 s')],'Fight from skimmer or shore'),
('SKIMMERACE','Skimmer Ace','Field','R2','MACHINE','Storm',2,2.0,'Engine (disables boost) x1.5',[('Ram Run','Blunt',2.2,1,40,'Engine whine, headlights flash'),('Harpoon Drag','Grab',1.8,1,40,'Harpoon gun aimed, red dot'),('Mine Trail','Blunt',1.4,2,20,'Drops mines behind (3)')],'Vehicle duel; skimmer part HP 600/150/120'),
('THORNHOUND','Thorn King\'s Hound','Field','R3','BEAST','Bloom',2,3.5,'Collar x1.3',[('Bramble Howl','None',0,2,30,'Howls; summons 4 Thornboar'),('Thorn Volley','Pierce',1.2,1,40,'Shakes body, thorns fly 15 m'),('Hunt Lunge x3','Pierce',1.6,2,30,'Low crouch')],'Tracks player across Thornwood once seen'),
('BOGMATRIARCH','Bog Matriarch','Field','R3','MULTI','Hollow',2,6.0,'Egg sac x2.0',[('Leech Spawn','Summon',0,1,60,'Sac pulses; 6 Bog Leeches'),('Bog Swallow','Grab',3.0,2,50,'Sinks; mud bubbles under player'),('Rot Spray','Weave',1.4,1,40,'Mouth tendrils open')],'Swamp; deep water slows 40%'),
('BASILISK','Glass Basilisk','Field','R4','BEAST','Iron',2,4.0,'Eyes (blind 6 s) x1.8',[('Petrifying Gaze','None',0,1,60,'Eyes glow white 1 s; Shatter 100 buildup if facing'),('Glass Spines','Pierce',1.4,1,36,'Spines flare'),('Shard Burrow','Blunt',2.2,2,50,'Dives into sand, ripple tracks')],'Look away during gaze'),
('HAULER','Wandering Hauler','Field','R4','MACHINE','Iron',2,6.0,'Engine 450, turret 400, wheels 300 each',[('Turret Burst','Bullet',0.4,1,30,'Turret swivels'),('Run Down','Blunt',2.8,1,40,'Horn blares'),('Deploy Crew','Summon',0,2,60,'Rear hatch: 4 Remnant Scrap Drones')],'Hijack after engine broken'),
('FROSTTITAN','Frost Titan','Field','R5','GIANT','Frost',2,14.0,'Frozen heart (back) x2.0',[('Glacier Stomp','Blunt',2.0,1,50,'Leg lifts, frost cloud'),('Avalanche','Blunt',2.4,2,90,'Strikes cliff; snow wave 20 m'),('Ice Prison','None',0,2,50,'Exhales; Slow 3 stacks if hit')],'Climbable: grab fur on back'),
('ARKKNIGHT','Fallen Ark-Knight','Field','R5','KNIGHT','Storm',2,2.6,'Helmet visor x1.4',[('Thruster Lunge','Pierce',2.0,1,24,'Jet pack flares'),('Hardlight Shield Bash','Blunt',1.6,1,26,'Blue shield up'),('Orbital Call','Weave',2.6,2,120,'Points skyward, red marker 2 s')],'Uses guns at range and sword close'),
('BONEHARVESTER','Bone Harvester','Field','R6','GIANT','Hollow',2,8.0,'Bone cage chest x1.5',[('Harvest Scythe','Slash',2.2,1,44,'Scythe drawn back, screech'),('Bone Rain','Pierce',1.2,2,60,'Shakes cage, bones fall 6 s'),('Raise Bones','Summon',0,2,60,'5 Hollowed Shamblers rise')],'Collects corpses: stronger if fight starts near battlefield'),
('SENTINELS','Twin Sentinels','Field','R6','DUO','Iron',2,4.0,'Core on whichever is not shielding x1.5',[('Shield Swap','None',0,1,20,'One raises shield, other attacks'),('Crossfire','Bullet',1.0,1,40,'Both aim, red lines'),('Fusion','Weave',2.8,2,100,'Join at center, white light 1.5 s')],'Guard the Hollowdeep lift'),
('FURNACEMAW','Furnace Maw','Site','R1','BEAST','Ember',2,4.0,'Belly furnace x2.0 when open',[('Swallow Fire','Weave',1.8,1,50,'Mouth glows, inhale'),('Coal Spit','Weave',1.2,1,40,'Coughs 3 coal balls'),('Belly Flop','Blunt',2.4,2,60,'Rears up, belly open')],'Mine furnace site'),
('MINEGOLEM','Mine Golem','Site','R1','GIANT','Iron',2,5.0,'Ore core (back) x1.8',[('Pickaxe Arm','Pierce',2.0,1,40,'Arm drawn back'),('Cave-In','Blunt',1.6,2,70,'Punches ceiling, rocks fall 5 s'),('Ore Shield','None',0,2,30,'Coats in ore; Defense +50% until Blunt break')],'Shortcut lift unlocks on kill'),
('SMUGGLERQUEEN','Smuggler Queen','Site','R2','KNIGHT','Storm',2,2.0,'None; parry-focused',[('Pistol Feint','Bullet',1.0,1,20,'Draws pistol, tips hat'),('Smoke Bomb','None',0,1,20,'Throws smoke, reappears behind'),('Call Crew','Summon',0,2,40,'Whistle; 3 Clan Raiders')],'Can be persuaded at Speech 60 (no fight, rewards differ)'),
('WRECKFOREMAN','Wreck Foreman','Site','R2','MACHINE','Iron',2,3.5,'Fuel tank x1.6',[('Crane Swing','Blunt',2.2,1,50,'Crane hook overhead'),('Rivet Storm','Bullet',0.3,1,30,'Rivet gun spins'),('Weld Burst','Weave',1.8,2,40,'Torch flares bright')],'In a wreck section with moving hull plates'),
('ROTHYDRA','Rot Hydra','Site','R3','MULTI','Bloom',2,6.0,'Necks (3 x 900 HP at L27, sever)',[('Rot Breath','Weave',1.6,1,50,'Middle head inhales'),('Triple Bite','Pierce',1.4,1,30,'Heads rise in sequence'),('Regrowth','Heal',0,2,80,'Stumps bubble; Ember stops it')],'Severing all heads skips phase 2'),
('BROODQUEEN','Cave Brood Queen','Site','R3','MULTI','Hollow',2,4.5,'Abdomen x1.8',[('Egg Barrage','Summon',0,1,50,'Abdomen pulses; 4 crawler eggs'),('Web Ceiling','None',0,2,40,'Climbs ceiling, drops web pools'),('Venom Fang','Pierce',2.0,1,30,'Rears up, fangs out')],'Cave; webbed walls block rolls'),
('MIRRORKNIGHT','Mirror Knight','Site','R4','KNIGHT','Iron',2,2.2,'Mirror shield (break at 800) x1.5',[('Reflect','None',0,1,8,'Shield flashes; reflects projectiles'),('Mirror Image','Summon',0,2,40,'Splits into 3; 2 shatter at 1 hit'),('Glass Cascade','Slash',2.2,2,50,'Shards orbit sword 1 s')],'Copies the player\'s weapon class in phase 2'),
('LASTPILOT','Last Pilot','Site','R4','FLYER','Storm',2,2.0,'Cockpit x1.5',[('Gun Run','Bullet',0.5,1,40,'Engines roar, approach line'),('Bail Out','None',0,2,30,'Ejects; fights on foot (KNIGHT moves) at 40%'),('Crash Dive','Blunt',3.0,2,80,'Burning flyer aims at player')],'Flyer hijackable after kill'),
('TOWERWITCH','Tower Witch','Site','R5','CASTER','Frost',2,2.0,'Familiar crow x2.0 (kill to stop teleports)',[('Hex Circle','Weave',1.8,1,60,'Draws sigil, 4 m'),('Teleport','None',0,1,10,'Crow caws first'),('Frozen Hex','Weave',2.4,2,70,'Hands freeze blue 1.2 s')],'Tower climb; falls from floors kill'),
('CRYPTABBOT','Crypt Abbot','Site','R5','CASTER','Hollow',2,2.2,'Censer x1.5',[('Censer Smoke','Weave',0.6,1,40,'Swings censer, smoke 6 m'),('Raise Monks','Summon',0,2,60,'Rings bell; 4 Husk Wardens'),('Last Rites','Weave',2.6,2,90,'Kneels to pray, 2 s')],'Crypt; coffins are cover'),
('CLOCKPRIOR','Clockwork Prior','Site','R6','MACHINE','Iron',2,3.0,'Mainspring (back) x2.0',[('Tick Strike','Blunt',1.4,1,30,'Clicks 3 times before'),('Time Skip','None',0,2,20,'Gears stop; prior moves 2x for 3 s'),('Chime of Ending','Weave',2.8,2,100,'Clock face spins, 12 chimes')],'Attacks land on a 1 s rhythm'),
('VAULTKEEPER','Vault Keeper','Site','R6','GIANT','Iron',2,5.0,'Keyhole chest x2.0',[('Vault Door Slam','Blunt',2.6,1,60,'Lifts door-shield'),('Lockdown','None',0,2,30,'Exits seal; lasers 20 s'),('Treasure Hoard','Summon',0,2,50,'Mimic chests (2) awaken')],'Undervault vault'),
('HUSH','Hush','Final','RQ','CASTER','Hollow',3,6.0,'Lens pylons (4, phase 1) x1.5; HP -4% per Heart Shard the player took',[('Lens Sweep','Weave',3.0,1,72,'White line traces the floor for 1.2 s, then the beam follows it'),('Choir of Copies','Summon',0,2,60,'Hush hums in many voices; two Choirborn copies of fallen foes rise'),('Seed Collapse','Weave',4.0,3,150,'Platforms dim one by one over 2.5 s; only lit platforms are safe')],'Campaign final boss (Act 3, LOC_Q_CORE); outside the 44 bosses; gravity 1.0 g / 0.4 g / 0 g by phase (world/gravity_zones.csv GRV_CORE); no Seals'),
('UV_STEVEDORE','The Stevedore','Undervault','RU','MACHINE','Iron',2,6.0,'Cage (break at 60%) x1.5',[('Container Throw','Blunt',2.2,1,50,'Lifts a container overhead 1.0 s'),('Shoulder Charge','Blunt',1.8,1,40,'Lowers shoulder, sparks at the feet'),('Magnet Crush','Blunt',2.6,2,70,'Hums and pulls everyone within 12 m')],'Undervault boss, Cargo Vaults (LOC_UV_REG_02_S06); outside the plan\'s 40'),
('UV_ROOTWRIGHT','The Rootwright','Undervault','RU','KNIGHT','Bloom',2,3.5,'Root pillars (6) heal it; cut them x1.5',[('Hook-axe Chain','Slash',1.6,1,30,'Hooks the axe back over the shoulder'),('Root Snare Line','None',0,1,45,'Stamps; a 15 m line of roots ripples toward the target'),('Root Eruption','Weave',2.4,2,60,'Three glowing knots appear on the floor')],'Undervault boss, Root Galleries (LOC_UV_REG_03_S06); outside the plan\'s 40'),
('UV_SUMPMOTHER','The Sump Mother','Undervault','RU','BEAST','Frost',2,8.0,'Egg sac x2.0',[('Ice Burst','Pierce',2.4,1,60,'Ice cracks in a ring under the player'),('Tail Sweep','Blunt',1.8,1,35,'Coils left, 270 degree sweep'),('Frost Breath','Weave',2.6,2,70,'Rears up, throat glows white')],'Undervault boss, Rime Sump (LOC_UV_REG_05_S06); outside the plan\'s 40'),
('UV_GOVERNOR','The Governor','Undervault','RU','MACHINE','Iron',3,7.0,'Core housing vents x2.0',[('Arm Sweep','Blunt',2.0,1,40,'Arms fold back, servos whine'),('Welding Beam','Weave',2.8,2,60,'Red aiming laser tracks for 1.5 s'),('Core Flare','Weave',4.0,3,90,'Core housing glows; stand behind a pillar')],'Undervault engine-block boss (LOC_UV_CORE); outside the plan\'s 40; Ostra is locked out from phase 2'),
('QUIETCORE','The Quiet Core','Raid','RQ','MACHINE','Hollow',3,20.0,'Three containment nodes (raid mechanic) x3.0',[('Orbital Purge','Weave',5.0,1,180,'Countdown 10 s; only shielded zones survive'),('Gravity Inversion','None',0,2,60,'Arena flips; fall damage off'),('Silent Pulse','Weave',3.0,3,90,'Silence 6 s; Resonance needed to cleanse')],'Launch raid; 6 players; no co-op scaling'),
('ARCHIVIST','Archivist Prime','Raid','RQ','CASTER','Storm',3,6.0,'Data cores (4) x2.5',[('Purge Record','Weave',4.0,1,150,'Selects 2 players, marked 6 s'),('Index Maze','None',0,2,60,'Arena split into 6 rooms'),('Recompile','Heal',0,3,120,'Heals 10% unless cores broken')],'Expansion 1 raid'),
('MERIDIANGHOST','Meridian\'s Ghost','Raid','RQ','KNIGHT','Ember',3,4.0,'Captain\'s badge x2.0',[('Abandon Ship','Weave',4.5,2,160,'Alarms; hull sections vent'),('Captain\'s Order','Summon',0,1,60,'Calls 4 Echo crew'),('Final Log','Weave',3.5,3,120,'Reads log aloud, 2 s, cone 30 m')],'Expansion 2 raid'),
('UNMADECHOIR','The Unmade Choir','Raid','RQ','DUO','Hollow',3,5.0,'Conductor (centre) x2.0',[('Dissonance','Weave',3.0,1,90,'Six singers off-key; split party into pairs'),('Crescendo','Weave',5.0,3,180,'Rising chord 10 s; Resonance cleanse'),('Harmony Link','None',0,2,40,'Links 2 players; split damage')],'Expansion 3 raid'),
]
RES_UNLOCK={'VAEL':'RES_EMBERRAIN','CORSA':'RES_LANCE','SORREL':'RES_BLOOMGATE','BRANNOCH':'RES_IRONSKIN','RIME':'RES_STILLPOINT','HOLLOWTWINS':'RES_ECHOLEGION'}
UVLT={'UV_STEVEDORE':'ITM_LT_BOSS_UV_02','UV_ROOTWRIGHT':'ITM_LT_BOSS_UV_03','UV_SUMPMOTHER':'ITM_LT_BOSS_UV_05','UV_GOVERNOR':'ITM_LT_BOSS_UV_CORE'}
UVLV={'UV_STEVEDORE':42,'UV_ROOTWRIGHT':56,'UV_SUMPMOTHER':70,'UV_GOVERNOR':46}
RAIDLV={'QUIETCORE':80,'ARCHIVIST':84,'MERIDIANGHOST':88,'UNMADECHOIR':92,'HUSH':80}
bosses=[];phases=[];moves=[]
for bid,name,cls,rid,arc,el,ph,ht,weak,sig,note in B:
    hm,stance,em,asset=CLS[cls]; _,rn,lo,hi,_t=REG[rid]
    L={'Shard-bearer':hi,'Citadel':hi-1,'Field':lo+round((hi-lo)*0.6),'Site':lo+round((hi-lo)*0.4),'Raid':RAIDLV.get(bid,80),'Final':80,'Undervault':UVLV.get(bid,46)}[cls]
    if rid=='RQ': L=RAIDLV[bid]
    aid='ACT_BOSS_'+bid; hp=boss_hp(L,hm)
    res={e:0.0 for e in ELEMENTS}; res[el]=0.5; res[OPPOSITE[el]]=-0.3
    bosses.append([aid,name,cls,rid,rn,L,hp,round(hp*0.0) if arc not in('MACHINE','CASTER') else round(hp*0.15),el if arc in('MACHINE','CASTER') else 'None',defense_at(L,1.5),stance,round(stance/13,1),
        0.1,0.1,0.1,0.1,0.2]+[res[e] for e in ELEMENTS]+[ph,'62' if ph==2 else '65; 30',arc,ht,weak,'x2.0 status thresholds',
        round(em*player_level_cost(L)),('None (the ending sequence follows)' if cls=='Final' else f'ITM_MAT_SPC_ASCENDANT 100%; '+UVLT[bid]+' 100%' if cls=='Undervault' else f'ITM_BOSS_{bid}_SOUL 100%; ITM_LOOT_TABLE_BOSS_{bid} 100%')+('; 5 ITM_CUR_SEAL' if cls=='Raid' else '')+('; ITM_MAT_STARMETAL x2' if cls in('Shard-bearer','Raid') else ''),
        RES_UNLOCK.get(bid,''),'AIP_BOSS',asset,note])
    # phases
    th=[100,62] if ph==2 else [100,65,30]
    for p in range(ph):
        pid=f'BPH_{bid}_{p+1}'
        changes={0:'Base moveset',1:f'Adds phase 2 moves; +10% speed; {el} infused on all attacks (30% conversion)',2:'Adds phase 3 moves; +15% damage; attack recovery -20%; signature finisher enabled'}[p]
        phases.append([pid,aid,p+1,th[p],th[p+1] if p+1<len(th) else 0,changes,'3.0 s readable transition, invulnerable, roar/cinematic' if p else 'Intro 4.0 s (skippable on retry)',
            f'ARENA_{bid}_P{p+1}','Music layer '+str(p+1)])
    # moves
    n=0
    for t in ARC[arc]:
        nm,ty,m,po,s,a,r,rg,aoe,trk,cnt,pf=t; n+=1
        if pf>ph: pf=ph
        elem=el if (ty=='Weave' or 'Infused' in nm or 'Elemental' in nm) else 'None'
        nm2=nm.replace('Elemental',el).replace('Infused',el+'-infused')
        moves.append([f'MOV_{bid}_{n:02d}',aid,nm2,pf,ty,elem,m,boss_dmg(L,m) if m else 0,po,s,a,r,max(0,r-12),rg,aoe,trk,cnt,round(s/60,2),
            'Weapon/body glow '+str(round(s/60,2))+' s; SFX tell at frame '+str(max(1,s-20)),round(1.0/(n**0.3),2),{1:6,2:10,3:14}.get(pf,6) if m>=2 else 0])
    for sn,ty,m,pf,s,tel in sig:
        n+=1; elem=el if ty in('Weave','Pierce','Slash','Blunt') else 'None'
        a=8 if ty!='Summon' else 0; r=max(30,round(s*0.9))
        moves.append([f'MOV_{bid}_{n:02d}',aid,sn,pf,ty,elem,m,boss_dmg(L,m) if m else 0,round(m*35),s,a,r,max(0,r-12),'per telegraph','per telegraph','Signature','Read the telegraph',round(s/60,2),tel,0.6,20 if m>=3 else 12])
write('bosses.csv',['ACT_ID','Boss','Class','Region','Region name','Level','HP (solo)','Ward','Ward element','Defense','Stance','Stance regen delay s','Res Slash','Res Pierce','Res Blunt','Res Bullet','Res Weave']+['Res '+e for e in ELEMENTS]+
 ['Phases','Phase HP thresholds %','Archetype','Height m','Weak points / parts','Status rule','Ember reward','Drops (item refs)','Resonance unlocked','AIP_ID','Asset ref','Notes'],bosses)
write('boss_phases.csv',['BPH_ID','ACT_ID','Phase','Starts at HP %','Ends at HP %','Changes','Transition','Arena state','Audio'],phases)
write('boss_moves.csv',['MOV_ID','ACT_ID','Move','From phase','Damage type','Element','Damage mult','Damage (solo)','Poise damage','Startup frames','Active frames','Recovery frames','Punish window frames','Range m','AoE radius m','Tracking','Counter','Telegraph lead s','Telegraph cue','AI weight','Cooldown s'],moves)
write('boss_ai_rules.csv',['RULE_ID','Rule','Value'],[
 ['BAI_INPUT','Boss AI may read player button input','Never; reacts only to position, distance and visible animation state'],
 ['BAI_REACT','Reaction delay after player animation starts','12 frames minimum (Raid 10)'],
 ['BAI_REPEAT','Same move back-to-back','Not allowed except combos; weight x0.3 for 2nd use within 10 s'],
 ['BAI_RANGE','Move selection','Filter by range band (close <4 m, mid 4-12 m, far >12 m), then weighted random by AI weight'],
 ['BAI_HEAL','Punish healing','Allowed only with moves of startup <= 30 frames when Tonic animation seen within 6 m'],
 ['BAI_STANCE','Stance break','Crit window 150 frames; stance resets to 0; regen delay = stance/13 s'],
 ['BAI_RETRY','Retry fairness','Intro skippable; nearest Anchor within 60 s run of fog gate'],
 ['BAI_COOP','Target choice in co-op','Aggro = damage dealt x 1.0 + proximity bonus (10 at <5 m) + 30 for last hitter; re-evaluate every 4 s'],
 ['BAI_TELEGRAPH','Telegraph minimum','Every damaging move shows a visual + audio tell at least 0.3 s before active frames'],
])
