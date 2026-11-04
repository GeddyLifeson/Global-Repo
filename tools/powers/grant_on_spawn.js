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
    try { var nd = entity.nbt.get('NeoForgeData'); var lid = nd ? '' + nd.getString('library_id').orElse('') : ''; if (lid && grants[lid]) key = lid } catch (e) {}
    if (!key && grants['' + entity.type]) key = '' + entity.type
    if (!key) return null
    var g = grants[key]
    if (g.powers == null) return g
    var n = g.count == null ? g.powers.length : g.count
    return g.powers.slice(0, n)
  }

  // NeoOrigins only runs persistent_effect and mob_behavior powers on mobs; every other passive type is applied here from its JSON.
  var NATIVE = {  // neoorigins powers in the pool, written as the same config shape as the JSON files
    'neoorigins:draconic_flight': { type: 'fly' }, 'neoorigins:elytrian_flight': { type: 'fly' }, 'neoorigins:phantom_flight': { type: 'fly' },
    'neoorigins:qi_core_pressure': { type: 'neoorigins:modify_damage', direction: 'out', multiplier: 1.3 },
    'neoorigins:golden_bell_diamond_body': { type: 'neoorigins:attribute_modifier', attribute: 'minecraft:armor_toughness', amount: 6, operation: 'add_value' },
    'neoorigins:golden_bell_iron_shirt': { type: 'neoorigins:attribute_modifier', attribute: 'minecraft:armor', amount: 8, operation: 'add_value' },
    'neoorigins:jianxian_immortal_body': { type: 'nofall' },
    'neoorigins:class_rogue_stealth': { type: 'invisible' },
    'neoorigins:class_titan_size': { type: 'neoorigins:attribute_modifier', attribute: 'minecraft:scale', amount: 0.25, operation: 'add_multiplied_base' }
  }
  var OPS = { add_value: 'addition', add_multiplied_base: 'multiply_base', add_multiplied_total: 'multiply_total' }
  var cache = {}
  var dmgIn = {}, dmgOut = {}, noFall = {}  // uuid -> multiplier / flag, rebuilt on load

  function configOf(id) {
    if (NATIVE[id]) return NATIVE[id]
    if (id.indexOf('diaithirpowers:') != 0) return null
    if (!(id in cache)) {
      try { cache[id] = JsonIO.read('kubejs/data/diaithirpowers/origins/powers/' + id.substring(15) + '.json') } catch (e) { cache[id] = null }
    }
    return cache[id]
  }

  function cmd(e, c) { e.server.runCommandSilent('execute as ' + e.uuid + ' run ' + c) }

  function applyConfig(entity, id, c) {
    var u = '' + entity.uuid
    if (c.type == 'neoorigins:attribute_modifier') cmd(entity, 'attribute @s ' + c.attribute + ' modifier add diaithir:' + id.replace(':', '_') + ' ' + c.amount + ' ' + (c.operation || 'add_value'))
    else if (c.type == 'neoorigins:modify_damage') { var t = c.direction == 'in' ? dmgIn : dmgOut; t[u] = (t[u] == null ? 1 : t[u]) * c.multiplier }
    else if (c.type == 'fly') cmd(entity, 'effect give @s minecraft:slow_falling infinite 0 true')
    else if (c.type == 'nofall') noFall[u] = true
    else if (c.type == 'invisible') cmd(entity, 'effect give @s minecraft:invisibility infinite 0 true')
    else return false
    return true
  }

  function applyPassive(entity, ids) {
    for (var i = 0; i < ids.length; i++) {
      try {
        var c = configOf(ids[i])
        if (c && applyConfig(entity, ids[i], c)) continue
        var h = PDM.INSTANCE.getPower(Ident.parse(ids[i]))
        if (h != null && h.appliesToMobs()) h.applyToMob(entity)
      } catch (e) { console.error('[powers] ' + ids[i] + ': ' + e) }
    }
  }

  EntityEvents.beforeHurt(function (event) {
    var u = '' + event.entity.uuid
    if (noFall[u] && '' + event.source.type == 'minecraft:fall') { event.cancel(); return }
    if (dmgIn[u] != null) event.damage = event.damage * dmgIn[u]
    var a = event.source.actual
    if (a != null && dmgOut['' + a.uuid] != null) event.damage = event.damage * dmgOut['' + a.uuid]
  })

  EntityEvents.spawned(function (event) {
    var entity = event.entity
    if (entity.maxHealth == null || entity.isPlayer()) return
    var list = grantList(entity)
    if (list == null) return
    var u = '' + entity.uuid
    delete dmgIn[u]; delete dmgOut[u]; delete noFall[u]
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
    return entity.server.players.filter(function (x) { return x.level == entity.level && entity.distanceToEntity(x) <= r })
  }

  function fire(m, a, now, t) {
    var e = m.entity, p = a.p, f = a.m / 5  // magnitude 5 = table values
    if (p.k == 'self') { if (e.target) cmd(e, 'effect give @s minecraft:' + p.e + ' ' + Math.ceil(p.t * f / 20) + ' ' + p.a + ' true') }
    else if (p.k == 'aoe') {
      var ps = near(e, p.r)
      if (!ps.length) return false
      ps.forEach(function (x) {
        cmd(x, 'effect give @s minecraft:' + p.e + ' ' + Math.ceil(p.t * f / 20) + ' ' + p.a)
        if (p.push) x.addMotion((x.x - e.x) * 0.2 * p.push, 0.4, (x.z - e.z) * 0.2 * p.push)
      })
    } else {
      if (!t || e.distanceToEntity(t) > p.range * f) return false
      if (p.k == 'ray') { t.attack(p.dmg * f); if (p.fire) t.igniteForSeconds(p.fire) }
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
