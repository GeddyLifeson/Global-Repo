// Drinking: each drink gives a small gift of its kind, and strength builds a drunkenness that wears off with time.
// One unit is half an ABV point per serving; five units wear off every 25 seconds.
const DRK_GIFT = {
  beer: [['minecraft:resistance', 400, 0]], wine: [['minecraft:regeneration', 200, 0]], fort: [['minecraft:resistance', 600, 0]],
  grain: [['minecraft:speed', 600, 0]], fruit: [['minecraft:speed', 600, 0], ['minecraft:regeneration', 100, 0]],
  clear: [['minecraft:strength', 400, 0], ['minecraft:fire_resistance', 600, 0]], brown: [['minecraft:strength', 600, 0], ['minecraft:resistance', 400, 0]],
  liq: [['minecraft:absorption', 600, 0], ['minecraft:speed', 400, 0]],
}
const drkIntox = {}

function drkDrunkLevel(v) {
  return v >= 90 ? 4 : v >= 60 ? 3 : v >= 40 ? 2 : v >= 25 ? 1 : 0
}

ItemEvents.foodEaten(event => {
  let id = String(event.item.id)
  if (id.indexOf('diaithir_drinks:') !== 0) return
  if (id === 'diaithir_drinks:off_brew') {  // a batch left far too long: sour and foul
    let q = event.entity
    if (q && q.isPlayer()) { q.potionEffects.add('minecraft:nausea', 300, 0); q.potionEffects.add('minecraft:hunger', 200, 0) }
    return
  }
  let d = DRK[id.substring(16)]
  let p = event.entity
  if (!d || !p || !p.isPlayer()) return
  let now = p.level.getGameTime()
  let e = drkIntox[String(p.uuid)] || { v: 0, t: now }
  let m = String(event.item.customData).match(/abv:([0-9.]+)d/)
  let abv = m ? Number(m[1]) : d.abv
  e.v = Math.max(0, e.v - (now - e.t) / 100) + abv * 0.5
  e.t = now
  drkIntox[String(p.uuid)] = e
  let boost = 1 + Math.floor(d.richness / 3)
  ;(DRK_GIFT[d.cat] || []).forEach(g => p.potionEffects.add(g[0], g[1] * boost, g[2]))
  let lvl = drkDrunkLevel(e.v)
  let dur = Math.floor(200 + e.v * 8)
  if (lvl >= 1) p.potionEffects.add('minecraft:slowness', dur, lvl >= 3 ? 2 : lvl - 1)
  if (lvl >= 2) p.potionEffects.add('minecraft:nausea', Math.min(dur, 400), 0)
  if (lvl >= 3) p.potionEffects.add('minecraft:weakness', dur, 0)
  if (lvl >= 4) p.potionEffects.add('minecraft:blindness', 200, 0)
  if (lvl >= 1) p.setStatusMessage(Text.gold(['Merry', 'Tipsy', 'Drunk', 'Senseless', 'Senseless'][lvl] + '. Slow down.'))
})

