// One-shot: players who joined before the spawn fix (old Tellus default) are moved to Creag Ruadh on their next login.
PlayerEvents.loggedIn(event => {
  let p = event.player
  if (p.persistentData.getBooleanOr('creag_ruadh_v1', false)) return
  p.persistentData.putBoolean('creag_ruadh_v1', true)
  let name = p.username
  event.server.scheduleInTicks(40, () => {
    event.server.runCommandSilent(`execute in minecraft:overworld run tp ${name} -251201 207 -1541408`)
    event.server.runCommandSilent(`execute in minecraft:overworld run spawnpoint ${name} -251201 207 -1541408`)
  })
})
