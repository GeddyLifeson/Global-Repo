// Server rules (/rules, shown once on first join) and the first-boot claim that keeps the land round spawn
// out of players' hands. Story NPCs are already invulnerable and refuse every interaction (deepworlds/npcs.js).

const SAFETY_TEAM = 'Diaithir'
const SAFETY_SPAWN_RADIUS = -1 // chunks each way from spawn; -1 keeps nothing. Age I spawn has no old places to guard yet, and a claim blocked mining.

const SAFETY_RULES = [
  'Claim your land on the map (M), and it is yours and your House\'s.',
  'Do not break, take or burn what another player has built.',
  'Leave the old places be. The land round spawn and the story\'s halls and folk are kept and cannot be broken.',
  'No x-ray, no duplication, no cheat clients.',
  'Keep chat civil. No slurs, no spam, no hounding anyone.',
  'Fighting is open in the wild. Inside a claim, the House that holds it decides.',
  'Every block placed or broken is written down. If someone wrongs you, tell a Warden.'
]

function safetyTellRules(player) {
  player.tell(Text.gold('Rules of the server'))
  SAFETY_RULES.forEach((r, i) => player.tell(Text.white(`${i + 1}. ${r}`)))
}

PlayerEvents.loggedIn(event => {
  let p = event.player
  if (p.persistentData.getBooleanOr('safety_rules_seen', false)) return
  p.persistentData.putBoolean('safety_rules_seen', true)
  safetyTellRules(p)
  p.tell(Text.gray('Read these again any time with /rules.'))
})

ServerEvents.commandRegistry(event => {
  event.register(event.commands.literal('rules').executes(ctx => {
    safetyTellRules(ctx.source.playerOrException)
    return 1
  }))
})

function safetySpawnPos(level) {
  return level.levelData.respawnData.pos()
}

ServerEvents.loaded(event => safetyKeepSpawn(event.server))

// The ftbteams/ftbchunks commands can't name a server team from the console (TeamArgument throws), so use their APIs.
function safetyKeepSpawn(s) {
  if (SAFETY_SPAWN_RADIUS < 0) return safetyReleaseSpawn(s)
  if (s.persistentData.getBooleanOr('safety_spawn_kept', false)) return
  let teams = Java.loadClass('dev.ftb.mods.ftbteams.api.FTBTeamsAPI').api().manager
  let chunks = Java.loadClass('dev.ftb.mods.ftbchunks.api.FTBChunksAPI').api().manager
  let ChunkDimPos = Java.loadClass('dev.ftb.mods.ftblibrary.math.ChunkDimPos')
  let source = s.createCommandSourceStack()
  // getTeamByName wants FTB's "Name#id" short name, so match the display name instead
  let team = teams.teams.stream().filter(t => t.serverTeam && String(t.name.string) === SAFETY_TEAM).findFirst().orElse(null) ||
    teams.createServerTeam(source, SAFETY_TEAM, 'The old places', Java.loadClass('dev.ftb.mods.ftblibrary.icon.Color4I').WHITE)
  let props = Java.loadClass('dev.ftb.mods.ftbchunks.api.FTBChunksProperties')
  let PUBLIC = Java.loadClass('dev.ftb.mods.ftbteams.api.property.PrivacyMode').PUBLIC
  team.setProperty(props.BLOCK_INTERACT_MODE, PUBLIC) // doors, buttons and chests at spawn still work
  team.setProperty(props.ENTITY_INTERACT_MODE, PUBLIC)
  let data = chunks.getOrCreateData(team)
  let spawn = safetySpawnPos(s.overworld())
  let cx = spawn.x >> 4, cz = spawn.z >> 4, failed = 0
  for (let x = cx - SAFETY_SPAWN_RADIUS; x <= cx + SAFETY_SPAWN_RADIUS; x++) {
    for (let z = cz - SAFETY_SPAWN_RADIUS; z <= cz + SAFETY_SPAWN_RADIUS; z++) {
      let pos = new ChunkDimPos(s.overworld().dimension, x, z)
      let held = chunks.getChunk(pos)
      if (held && held.teamData.team.id.equals(team.id)) continue
      let r = data.claim(source, pos, false)
      if (!r.isSuccess()) { failed++; console.error(`[safety] claim ${x},${z}: ${r}`) }
    }
  }
  if (failed) return console.error(`[safety] ${failed} spawn chunks could not be claimed for ${SAFETY_TEAM}; will retry next start`)
  s.persistentData.putBoolean('safety_spawn_kept', true)
  console.info(`[safety] kept ${SAFETY_SPAWN_RADIUS * 2 + 1}x${SAFETY_SPAWN_RADIUS * 2 + 1} chunks round spawn ${spawn.x} ${spawn.z} for ${SAFETY_TEAM}`)
}

// Gives back every chunk the old spawn claim holds, once, so new players can mine and build round spawn.
function safetyReleaseSpawn(s) {
  if (s.persistentData.getBooleanOr('safety_spawn_released', false)) return
  let teams = Java.loadClass('dev.ftb.mods.ftbteams.api.FTBTeamsAPI').api().manager
  let chunks = Java.loadClass('dev.ftb.mods.ftbchunks.api.FTBChunksAPI').api().manager
  let team = teams.teams.stream().filter(t => t.serverTeam && String(t.name.string) === SAFETY_TEAM).findFirst().orElse(null)
  if (!team) return s.persistentData.putBoolean('safety_spawn_released', true)
  let source = s.createCommandSourceStack()
  let data = chunks.getOrCreateData(team)
  let held = Array.from(data.claimedChunks), freed = 0, failed = 0
  held.forEach(c => {
    let r = data.unclaim(source, c.pos, false)
    if (r.isSuccess()) freed++; else { failed++; console.error(`[safety] unclaim ${c.pos}: ${r}`) }
  })
  if (failed) return console.error(`[safety] ${failed} of ${held.length} spawn chunks could not be released; will retry next start`)
  s.persistentData.putBoolean('safety_spawn_released', true)
  console.info(`[safety] released ${freed} spawn chunks held by ${SAFETY_TEAM}`)
}
