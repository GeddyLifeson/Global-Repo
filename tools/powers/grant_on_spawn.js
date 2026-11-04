// S6961 Grant pool powers to mobs and NPCs when they load. One generic mechanism, nothing per character.
// data/diaithir/powers/pool.json: pool id -> NeoOrigins power ids (+ "mob" emulation for active powers).
// data/diaithir/powers/grants.json: library id or entity type id -> pool ids, 'id' or 'id:magnitude' (array) or {count, powers}.
(function () {
  var PDM = Java.loadClass('com.cyberday1.neoorigins.data.PowerDataManager')
  var Ident = Java.loadClass('net.minecraft.resources.Identifier')
  var pool = {}, grants = {}
  try { pool = JsonIO.read('kubejs/data/diaithir/powers/pool.json') || {} } catch (e) { console.error('[powers] pool: ' + e) }
  try { grants = JsonIO.read('kubejs/data/diaithir/powers/grants.json') || {} } catch (e) { console.error('[powers] grants: ' + e) }
  var active = {}  // uuid -> {entity, acts:[{p, next}]}

  function grantList(entity) {
    var key = null
    try { var lid = entity.persistentData.getString('library_id'); if (lid && grants[lid]) key = lid } catch (e) {}
    if (!key && grants['' + entity.type]) key = '' + entity.type
    if (!key) return null
    var g = grants[key]
    if (Array.isArray(g)) return g
    var n = g.count == null ? g.powers.length : g.count
    return g.powers.slice(0, n)
  }

  function applyPassive(entity, ids) {
    for (var i = 0; i < ids.length; i++) {
      try {
        var h = PDM.INSTANCE.getPower(Ident.parse(ids[i]))
        if (h != null && h.appliesToMobs()) h.applyToMob(entity)
      } catch (e) { console.error('[powers] ' + ids[i] + ': ' + e) }
    }
  }

  EntityEvents.spawned(function (event) {
    var entity = event.entity
    if (!entity.isLiving() || entity.isPlayer()) return
    var list = grantList(entity)
    if (list == null) return
    var acts = []
    for (var i = 0; i < list.length; i++) {
      var parts = ('' + list[i]).split(':'), p = pool[parts[0]]
      if (!p) { console.warn('[powers] unknown pool id ' + list[i]); continue }
      if (p.kind == 'A') acts.push({ p: p.mob, m: +(parts[1] || 5), next: 0 })
      else applyPassive(entity, p.sources.map(function (s) { return s.replace('{m}', parts[1] || '1') }))
    }
    if (acts.length) active['' + entity.uuid] = { entity: entity, acts: acts }
  })

  function near(entity, r) {
    return entity.level.getEntitiesWithin(entity.boundingBox.inflate(r)).filter(function (e) { return e.isPlayer() })
  }

  function fire(m, a, now, t) {
    var e = m.entity, p = a.p, f = a.m / 5  // magnitude 5 = table values
    if (p.k == 'self') { if (e.target) e.potionEffects.add('minecraft:' + p.e, Math.ceil(p.t * f), p.a, false, false) }
    else if (p.k == 'aoe') {
      var ps = near(e, p.r)
      if (!ps.length) return false
      ps.forEach(function (x) {
        x.potionEffects.add('minecraft:' + p.e, Math.ceil(p.t * f), p.a)
        if (p.push) x.addMotion((x.x - e.x) * 0.2 * p.push, 0.4, (x.z - e.z) * 0.2 * p.push)
      })
    } else {
      if (!t || e.distanceToEntity(t) > p.range * f) return false
      if (p.k == 'ray') { t.attack(p.dmg * f); if (p.fire) t.setSecondsOnFire(p.fire) }
      else if (p.k == 'blink') e.setPosition(t.x, t.y, t.z)
    }
    if (p.p) e.server.runCommandSilent('execute as ' + e.uuid + ' at @s run particle ' + p.p + ' ~ ~1 ~ 0.4 0.4 0.4 0.05 12')
    return true
  }

  ServerEvents.tick(function (event) {
    var now = event.server.tickCount
    if (now % 20 != 0) return
    for (var id in active) {
      var m = active[id]
      if (!m.entity.isAlive()) { delete active[id]; continue }
      var t = m.entity.target
      if (!t) continue
      for (var i = 0; i < m.acts.length; i++) {
        var a = m.acts[i]
        if (now < a.next) continue
        try { if (fire(m, a, now, t)) a.next = now + a.p.cd } catch (e) { console.error('[powers] fire: ' + e); a.next = now + 1200 }
      }
    }
  })
  console.info('[powers] grant_on_spawn ready: ' + Object.keys(pool).length + ' pool powers, ' + Object.keys(grants).length + ' grant keys')
})()
