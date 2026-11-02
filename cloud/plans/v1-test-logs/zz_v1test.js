// TEST ONLY (v1 cloud test, not for the repo): probes for the Age Turn reload and the cities year listener.
const V1_PROBES = ['framedblocks:framed_cube', 'cookingforblockheads:cooking_table', 'mcwfences:oak_picket_fence', 'farmingforblockheads:market', 'chisel:chisel_iron', 'minecraft:iron_ingot']
ServerEvents.recipes(event => {
  let out = {}
  for (let id of V1_PROBES) { try { out[id] = Math.round(event.countRecipes({ output: id })) } catch (e) { out[id] = 'err ' + e } }
  console.info('[v1probe] age ' + AGES.age + ' recipes ' + JSON.stringify(out))
})
ServerEvents.commandRegistry(event => {
  event.register(event.commands.literal('v1year').executes(ctx => {
    let SE = Java.loadClass('net.diaithir.ages.mc.StoryEvent')
    let bus = Java.loadClass('net.neoforged.neoforge.common.NeoForge').EVENT_BUS
    bus.post(new SE('year', 'lc', '4321'))
    let s = Java.loadClass('net.neoforged.neoforge.server.ServerLifecycleHooks').getCurrentServer()
    console.info('[v1probe] cities_lc after year event = ' + s.persistentData.getInt('cities_lc'))
    return 1
  }))
})
