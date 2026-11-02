// Age gate for the far worlds of na Speuran (datapack diaithir_worlds). Stellaris has no per-planet rocket
// tier, so on every datapack sync (each login, and every /reload, which the Age Turn runs) a world the
// current diaithir_ages Age has not reached is taken out of Stellaris's planet list before Stellaris sends
// it: the rocket menu does not show it and the server refuses travel there. Without diaithir_ages all open.
const SPEURAN_AGES = ['TELLING', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'RODOS']
const SPEURAN_OPENS = {
  'diaithir_worlds:gealach_an_fhuamhaire': 'VI',
  'diaithir_worlds:talamh_reota': 'VI',
  'diaithir_worlds:muir_gun_chrioch': 'VI',
  'diaithir_worlds:fasach_an_luis': 'VII',
  'diaithir_worlds:an_sgeap_dhubh': 'VII',
  'diaithir_worlds:saoghal_nan_inneal': 'VII',
  'diaithir_worlds:an_fhainne_mhor': 'RODOS',
  'diaithir_worlds:ard_bhaile': 'RODOS'
}
const SpeuranPlanets = Java.loadClass('org.exodusstudio.stellaris.common.data.PlanetsData')
let speuranHeld = []

function speuranAge(server) {
  try {
    return SPEURAN_AGES.indexOf(String(Java.loadClass('net.diaithir.ages.mc.AgesSavedData').get(server).world.age).toUpperCase())
  } catch (e) {
    return SPEURAN_AGES.length
  }
}

NativeEvents.onEvent('highest', Java.loadClass('net.neoforged.neoforge.event.OnDatapackSyncEvent'), event => {
  let age = speuranAge(event.getPlayerList().getServer())
  let all = {}
  speuranHeld.concat(Array.from(SpeuranPlanets.PLANETS)).forEach(p => { all[String(p.dimension())] = p })
  let open = [], held = []
  Object.keys(all).forEach(dim => {
    let opens = SPEURAN_OPENS[dim]
    if (opens && SPEURAN_AGES.indexOf(opens) > age) held.push(all[dim])
    else open.push(all[dim])
  })
  speuranHeld = held
  SpeuranPlanets.setPlanets(open)
  console.info(`[speuran] Age ${SPEURAN_AGES[age] || 'unlinked'}: ${open.length} planets open, ${held.length} held`)
})
