// Brewing: six stations turn farm goods into drinks over game time. Data comes from data.js (tools/drinks/gen_data.py).
// Right-click a station with an empty hand to cycle what you can brew from your pack, sneak and right-click to start,
// right-click again when it is ready. Hold an ingredient to narrow the list to what uses it.
const DRK_DAY = 24000
const DRK_STATE_FILE = 'kubejs/data/drinks_state.json'
const DRK_ITEM = 'diaithir_drinks:'
const DRK_ROLE_BLOCK = {}
Object.keys(DRINK_STATIONS).forEach(id => { DRK_ROLE_BLOCK[DRK_ITEM + id] = DRINK_STATIONS[id][0] })

const DRK_GROUPS = {}
Object.keys(DRINK_ING).forEach(g => { DRK_GROUPS[g] = DRINK_ING[g] })
DRK_GROUPS.grain = ['croptopia:barley', 'biomesoplenty:barley', 'minecraft:wheat', 'croptopia:rye', 'croptopia:oat', 'croptopia:corn']
DRK_GROUPS.young_wine = [DRK_ITEM + 'young_wine']
DRK_GROUPS.neutral = [DRK_ITEM + 'neutral_spirit']
;['grain', 'corn', 'cane', 'grape', 'fruit', 'agave'].forEach(k => { DRK_GROUPS['nm_' + k] = [DRK_ITEM + 'new_make_' + k] })

const DRK = {}
DRINK_ROWS.forEach(r => {
  let o = {}
  DRINK_KEYS.forEach((k, i) => { o[k] = r[i] })
  DRK[o.id] = o
})

let drkState = {}
const drkSel = {}
let drkRecipes = null

function drkIds(g) {
  if (g.indexOf(':') >= 0) return Item.exists(g) ? [g] : []  // an exact item id
  return (DRK_GROUPS[g] || []).filter(id => Item.exists(id))
}

function drkLocked(item) {
  return typeof techLocked === 'function' && techLocked(item)
}

const DRK_SEASONING = /cinnamon|clove|nutmeg|star_anise|vanilla|ginger|coriander|caraway|allspice|cardamon|cumin|fenugreek|dill|pepper|saffron|salt|wormwood|gentian|angelica|cassia|cinchona|licorice|koji|bay_leaf|thyme|sage|rosemary|mint|lemongrass|chamomile|balm|marjoram|iris|calluna/

function drkRecipeFor(d) {
  let a = d.abv
  let base = d.bases[0]
  let n = Math.max(2, Math.min(6, Math.round(2 + a / 4)))
  let r = { id: d.id, out: DRK_ITEM + d.id, name: d.name, abv: d.abv, age: d.age, station: d.station, count: 3, inputs: [], ticks: DRK_DAY }
  let grainy = ['rice', 'millet', 'rye', 'corn', 'oat', 'wheat'].indexOf(base) >= 0
  switch (d.route) {
    case 'ferment':
      if (d.cat === 'beer') {
        if (base === 'barley' || base === 'malt') r.inputs.push(['malt', n])
        else { r.inputs.push([base, n]); r.inputs.push(['malt', 1]) }
        if (d.hopped) r.inputs.push(['hops', 1])
        r.inputs.push(['yeast', 1])
      } else if (base === 'honey') {
        r.inputs.push(['honey', n])
        if (/metheglin/.test(d.id)) r.inputs.push(['herb', 1])
        if (/melomel|cyser|pyment/.test(d.id)) r.inputs.push([/cyser/.test(d.id) ? 'apple' : /pyment/.test(d.id) ? 'grape' : 'berry', 2])
      } else if (grainy || base === 'barley') {
        r.inputs.push([base, n]); r.inputs.push(['yeast', 1])
      } else {
        r.inputs.push([base, n + 1])
        if (a > 9) r.inputs.push(['sugar', 1])
      }
      r.ticks = DRK_DAY * Math.min(4, 1 + Math.floor(a / 4))
      break
    case 'sparkle':
      r.inputs.push(['grape', 5], ['sugar', 1]); r.ticks = DRK_DAY * 3
      break
    case 'lager':
      r.inputs.push(['malt', 3], ['hops', 1], ['yeast', 1]); r.ticks = DRK_DAY * 6
      break
    case 'distill':
      if (d.station === 'cask') {
        r.inputs.push(['nm_' + d.new_make, 3]); r.ticks = DRK_DAY * Math.max(1, d.cask_days)
      } else {
        r.inputs.push([base, Math.min(6, 3 + Math.floor(a / 30))])
        if (grainy || base === 'barley') r.inputs.push(['yeast', 1])
        r.ticks = 6000
      }
      break
    case 'fortify':
      r.inputs.push(['young_wine', 3], ['neutral', 1]); r.ticks = DRK_DAY * Math.max(1, d.cask_days)
      break
    case 'steep':
      r.inputs.push(['neutral', 1], [base, 3], ['sugar', 2]); r.ticks = DRK_DAY * 2
      break
  }
  // audited against the drink's real recipe (content/drinks/ingredients.json): inputs it would not use go, ingredients it would use come in
  let freed = 0
  ;(d.drop || []).forEach(g => {
    r.inputs.filter(i => i[0] === g).forEach(i => { freed += i[1] })
    r.inputs = r.inputs.filter(i => i[0] !== g)
  })
  let fresh = []
  ;(d.add || []).forEach(id => {
    if (!r.inputs.some(i => i[0] === id || (DRK_GROUPS[i[0]] || []).indexOf(id) >= 0)) {
      let inp = [id, 1]
      r.inputs.push(inp)
      if (!DRK_SEASONING.test(id)) fresh.push(inp)
    }
  })
  // what a dropped group used to supply is now supplied by the ids that replace it
  if (freed > fresh.length && fresh.length) {
    let each = Math.floor(freed / fresh.length)
    fresh.forEach((inp, k) => { inp[1] = Math.max(1, each + (k === 0 ? freed - each * fresh.length : 0)) })
  }
  return r
}

function drkExtraRecipes() {
  let mk = (id, station, inputs, ticks) => ({ id: id, out: DRK_ITEM + id, name: (DRINK_EXTRAS.filter(x => x[0] === id)[0] || [0, id])[1], abv: 0, age: (DRINK_EXTRAS.filter(x => x[0] === id)[0] || [0, 0, 'I'])[2], station: station, count: 3, inputs: inputs, ticks: ticks })
  return [
    mk('young_wine', 'vat', [['grape', 4]], DRK_DAY * 2),
    mk('neutral_spirit', 'still', [['grain', 4], ['yeast', 1]], 6000),
    mk('new_make_grain', 'still', [['grain', 4], ['yeast', 1]], 6000),
    mk('new_make_corn', 'still', [['corn', 4], ['yeast', 1]], 6000),
    mk('new_make_cane', 'still', [['cane', 6]], 6000),
    mk('new_make_grape', 'still', [['young_wine', 3]], 6000),
    mk('new_make_fruit', 'still', [['apple', 5]], 6000),
    mk('new_make_agave', 'still', [['agave', 6]], 6000),
  ]
}

// Styles that differ mainly in strength must differ in what goes in the vessel: where two drinks of one station share every input,
// the stronger one is bumped step by step (more hops, more of the main fermentable, a sugar or honey adjunct) until each set is its own.
const DRK_STEPS = {
  beer: [['hops', 3], ['malt', 7], ['sugar', 3], ['honey', 2]],
  mead: [['honey', 8], ['sugar', 3]],
  other: [['grape', 8], ['sugar', 3], ['honey', 2], ['yeast', 2]]
}

function drkFingerprint(r) {
  return r.station + '|' + r.inputs.map(i => i[0] + '*' + i[1]).sort().join('|')
}

function drkBump(r, d, level) {
  let steps = DRK_STEPS[d.cat === 'beer' ? 'beer' : d.bases[0] === 'honey' ? 'mead' : 'other']
  let list = steps.slice()
  let main = r.inputs.filter(i => i[0] !== 'yeast' && i[0] !== 'hops' && i[0] !== 'sugar' && i[0] !== 'honey' && i[0].indexOf(':') < 0)[0]
  if (main && !list.some(s => s[0] === main[0])) list.unshift([main[0], 8])
  for (let k = 0; k < level; k++) {
    let done = false
    for (let j = 0; j < list.length && !done; j++) {
      let st = list[j]
      let inp = r.inputs.filter(i => i[0] === st[0])[0]
      if (inp) { if (inp[1] < st[1]) { inp[1]++; done = true } }
      else if (st[0] !== 'hops' || d.hopped) { r.inputs.push([st[0], 1]); done = true }
    }
    if (!done) break
  }
}

function drkFerm(r) {
  return r.inputs.filter(i => i[0] !== 'yeast' && i[0] !== 'hops' && !DRK_SEASONING.test(i[0])).reduce((a, i) => a + i[1], 0)
}

// within one family (category, base, hopped) a stronger style never takes less fermentable than a weaker one
function drkMonotone(rs) {
  let fam = {}
  rs.forEach(r => { let d = DRK[r.id]; if (d && d.route === 'ferment') (fam[d.cat + '|' + d.bases[0] + '|' + d.hopped] = fam[d.cat + '|' + d.bases[0] + '|' + d.hopped] || []).push(r) })
  Object.keys(fam).forEach(k => {
    let g = fam[k].sort((a, b) => a.abv - b.abv)
    for (let i = 1; i < g.length; i++) {
      for (let t = 0; t < 6 && g[i].abv - g[i - 1].abv >= 3 && drkFerm(g[i]) < drkFerm(g[i - 1]); t++) drkBump(g[i], DRK[g[i].id], 1)
    }
  })
}

function drkDistinguish(rs) {
  drkMonotone(rs)
  for (let pass = 0; pass < 12; pass++) {
    let groups = {}
    rs.forEach(r => { if (DRK[r.id]) (groups[drkFingerprint(r)] = groups[drkFingerprint(r)] || []).push(r) })
    let clash = Object.keys(groups).filter(k => groups[k].length > 1)
    if (!clash.length) return
    clash.forEach(k => {
      let g = groups[k].sort((a, b) => a.abv - b.abv || (a.id < b.id ? -1 : 1))
      for (let i = 1; i < g.length; i++) drkBump(g[i], DRK[g[i].id], 1)
    })
  }
}

function drkAllRecipes() {
  if (!drkRecipes) {
    drkRecipes = []
    DRINK_ROWS.forEach(row => { drkRecipes.push(drkRecipeFor(DRK[row[0]])) })
    drkDistinguish(drkRecipes)
    drkExtraRecipes().forEach(r => drkRecipes.push(r))
  }
  return drkRecipes
}

function drkCount(p, ids) {
  let n = 0
  let inv = p.inventory
  for (let i = 0; i < inv.containerSize; i++) {
    let s = inv.getItem(i)
    if (!s.isEmpty() && ids.indexOf(String(s.id)) >= 0) n += s.count
  }
  return n
}

function drkTake(p, ids, n) {
  let inv = p.inventory
  for (let i = 0; i < inv.containerSize && n > 0; i++) {
    let s = inv.getItem(i)
    if (!s.isEmpty() && ids.indexOf(String(s.id)) >= 0) {
      let t = Math.min(n, s.count)
      s.shrink(t)
      n -= t
    }
  }
}

function drkCan(p, rc) {
  return rc.inputs.every(inp => {
    let ids = drkIds(inp[0])
    return ids.length > 0 && drkCount(p, ids) >= inp[1]
  })
}

function drkUses(rc, heldId) {
  return rc.inputs.some(inp => drkIds(inp[0]).indexOf(heldId) >= 0)
}

function drkNeeds(rc) {
  return rc.inputs.map(inp => {
    let ids = drkIds(inp[0])
    let nm = ids.length ? Item.of(ids[0]).hoverName.string : inp[0]
    return inp[1] + ' ' + nm
  }).join(', ')
}


// Strength by time. A fermenting batch gains ABV with its ferment time up to the style's yeast cap (set by the fermentable put in),
// bottled early it is weaker and sweeter, left far past the cap it turns sour. The vessel never shows the number; a hydrometer reads it.
const DRK_MIN_T = 0.1   // fraction of the full ferment before anything can be bottled
const DRK_OFF_T = 2.5   // fraction of the full ferment after which the batch has turned
const DRK_ROUTES_TIMED = ['ferment', 'sparkle', 'lager']

function drkTimed(rc) {
  return !!DRK[rc.id] && DRK_ROUTES_TIMED.indexOf(DRK[rc.id].route) >= 0
}

function drkFrac(s, now) {
  return (now - s.start) / Math.max(1, s.end - s.start)
}

function drkAbvAt(s, t) {
  return t >= 1 ? s.cap : s.cap * (1 - (1 - t) * (1 - t))
}

function drkStageWord(t) {
  return t < 0.15 ? 'barely stirring' : t < 0.4 ? 'bubbling hard' : t < 0.7 ? 'bubbling steadily' : t < 1 ? 'slowing down' : t < 1.8 ? 'quiet and settled' : 'smelling sharp'
}

function drkSweetWord(t) {
  return t < 0.5 ? 'very sweet' : t < 0.8 ? 'sweet' : t < 1 ? 'off-dry' : 'dry'
}

const DRK_ROLE_TEMP = { vat: 20, cellar: 8, cask: 12, tank: 4, still: 78, pot: 78 }

function drkTemp(role, now) {
  return (DRK_ROLE_TEMP[role] || 15) + Math.round(2 * Math.sin(now / 24000 * Math.PI * 2))
}

function drkCollect(p, s, now) {
  let name = Item.of(s.out).hoverName.string
  if (s.abvOut !== undefined) {
    let st = Item.of(s.out + '[custom_data={abv:' + s.abvOut + ',aged:' + (s.aged || 0) + '}]', s.count)
    try { st.setLore([Text.gray(s.aged ? 'Aged ' + s.aged + ' days in oak' : 'Run through the still again')]) } catch (e) {}
    p.give(st)
    p.setStatusMessage(Text.gold('Ready. You take ' + s.count + ' ' + name + '.'))
    return
  }
  if (!s.timed) {
    p.give(Item.of(s.out, s.count))
    p.setStatusMessage(Text.gold('Ready. You take ' + s.count + ' ' + name + '.'))
    return
  }
  let t = drkFrac(s, now)
  if (t > DRK_OFF_T) {
    p.give(Item.of(DRK_ITEM + 'off_brew', s.count))
    p.setStatusMessage(Text.red('It has turned sour. You take ' + s.count + ' off brew.'))
    return
  }
  let abv = Math.round(drkAbvAt(s, t) * 10) / 10
  let st = Item.of(s.out + '[custom_data={abv:' + abv + '}]', s.count)
  try { st.setLore([Text.gray(drkSweetWord(t) + (t < 1 ? ', bottled young' : ''))]) } catch (e) {}
  p.give(st)
  p.setStatusMessage(Text.gold((t < 1 ? 'Bottled young: ' : 'Ready: ') + s.count + ' ' + name + ', ' + drkSweetWord(t) + '.'))
}

// Distilling and ageing work on the bottle's own strength. Hold a finished bottle and sneak-right-click an idle still to run it again
// (3 bottles become 2, stronger each pass, pot stills stop near 86%, column stills near 96%); at an oak cask the same gesture ages it
// (a little strength lost to the angel's share, the drink worth more). The strength rides on the bottle as custom data.
const DRK_STILL_CAP = { still: 86, column: 96 }  // by station role
const DRK_ANGEL = 0.012   // share of strength lost per day in the cask
const DRK_ANGEL_MAX = 0.15

function drkBottleAbv(stack) {
  let m = String(stack.customData).match(/abv:([0-9.]+)d/)
  if (m) return Number(m[1])
  let d = DRK[String(stack.id).substring(16)]
  return d ? d.abv : 0
}

function drkBottleAged(stack) {
  let m = String(stack.customData).match(/aged:([0-9.]+)d/)
  return m ? Number(m[1]) : 0
}

function drkRound(x) {
  return Math.round(x * 10) / 10
}

// returns false when the held bottle does not fit this vessel
function drkRework(p, block, role, now, k) {
  let held = p.mainHandItem
  let hid = String(held.id)
  let d = hid.indexOf(DRK_ITEM) === 0 ? DRK[hid.substring(16)] : null
  if (!d || held.count < 1) return false
  let abv = drkBottleAbv(held)
  let aged = drkBottleAged(held)
  if (role === 'still' || role === 'column') {
    if (['clear', 'brown', 'liq', 'grain', 'fort', 'wine', 'fruit', 'beer'].indexOf(d.cat) < 0 || held.count < 3) return false
    let cap = DRK_STILL_CAP[role]
    if (abv >= cap - 0.5) { p.setStatusMessage(Text.gray('This still cannot take it any stronger.')); return true }
    let n = Math.min(12, Math.floor(held.count / 3) * 3)
    held.shrink(n)
    let out = drkRound(abv + (cap - abv) * 0.4)
    drkState[k] = { out: hid, count: n * 2 / 3, end: now + 6000, start: now, cap: out, timed: false, abvOut: out, aged: aged }
    drkSave()
    p.setStatusMessage(Text.gold('Running ' + n + ' bottles through again: ' + (n * 2 / 3) + ' will come out stronger. Back in about 5 minutes.'))
    return true
  }
  if (role === 'cask') {
    if (['clear', 'brown', 'liq', 'fort', 'wine', 'grain'].indexOf(d.cat) < 0) return false
    let n = Math.min(12, held.count)
    held.shrink(n)
    let days = Math.max(2, Math.min(12, d.cask_days || 4))
    let loss = Math.min(DRK_ANGEL_MAX, DRK_ANGEL * days)
    let out = drkRound(abv * (1 - loss))
    drkState[k] = { out: hid, count: n, end: now + days * DRK_DAY, start: now, cap: out, timed: false, abvOut: out, aged: aged + days }
    drkSave()
    p.setStatusMessage(Text.gold(n + ' bottles into the cask for ' + days + ' days.'))
    return true
  }
  return false
}

// styles folded into another keep working: an old drink id becomes its kept id (content/drinks/id_migration.json)
function drkMigrated(id) {
  let short = id.indexOf(DRK_ITEM) === 0 ? id.substring(DRK_ITEM.length) : null
  return short && DRINK_MIGRATE[short] ? DRK_ITEM + DRINK_MIGRATE[short] : id
}

PlayerEvents.loggedIn(event => {
  try {
    let inv = event.player.inventory
    for (let i = 0; i < inv.containerSize; i++) {
      let st = inv.getItem(i)
      if (st.isEmpty()) continue
      let id = String(st.id)
      let to = drkMigrated(id)
      if (to !== id) inv.setItem(i, Item.of(to, st.count))
    }
  } catch (e) { console.warn('[drinks] id migration failed: ' + e) }
})

function drkKey(block) {
  return block.dimension + '|' + block.x + ',' + block.y + ',' + block.z
}

function drkSave() {
  JsonIO.write(DRK_STATE_FILE, drkState)
}


ServerEvents.loaded(event => {
  let raw = null
  try { raw = JsonIO.read(DRK_STATE_FILE) } catch (e) { raw = null }
  drkState = {}
  if (raw) {
    try { Object.keys(raw).forEach(k => { drkState[k] = { out: drkMigrated(String(raw[k].out)), count: Number(raw[k].count), end: Number(raw[k].end), start: Number(raw[k].start || 0), cap: Number(raw[k].cap || 0), timed: !!raw[k].timed, abvOut: raw[k].abvOut === undefined ? undefined : Number(raw[k].abvOut), aged: Number(raw[k].aged || 0) } }) } catch (e) { drkState = {} }
  }
  let noSeed = DRINK_CROPS.filter(c => !Item.exists(DRK_ITEM + c[0] + '_seeds'))
  if (noSeed.length) console.warn('[drinks] crops without a seed item: ' + noSeed.map(c => c[0]).join(','))
  let recipes = drkAllRecipes()
  let bad = recipes.filter(r => !Item.exists(r.out))
  let missing = {}
  recipes.forEach(r => r.inputs.forEach(inp => { if (drkIds(inp[0]).length === 0) missing[inp[0]] = true }))
  console.info('[drinks] ' + recipes.length + ' recipes, ' + bad.length + ' without an output item, groups with no item in this pack: ' + Object.keys(missing).join(','))
})

BlockEvents.rightClicked(event => {
  let role = DRK_ROLE_BLOCK[String(event.block.id)]
  if (!role) return
  if (String(event.hand).toLowerCase().indexOf('main') < 0) return
  let p = event.player
  let level = event.level
  let now = level.getGameTime()
  let k = drkKey(event.block)
  let s = drkState[k]
  if (s) {
    let heldTool = String(p.mainHandItem.id)
    let t = s.timed ? drkFrac(s, now) : 1
    if (s.timed && heldTool === DRK_ITEM + 'hydrometer') {
      p.setStatusMessage(Text.aqua('Hydrometer: ' + (Math.round(drkAbvAt(s, Math.min(t, 1)) * 10) / 10) + '% so far, ' + drkSweetWord(t) + (t > 1.8 ? ', going off' : '')))
    } else if (heldTool === DRK_ITEM + 'thermometer') {
      p.setStatusMessage(Text.aqua('Thermometer: ' + drkTemp(role, now) + ' degrees'))
    } else if (now >= s.end) {
      drkCollect(p, s, now)
      delete drkState[k]
      drkSave()
    } else if (s.timed && p.crouching) {
      if (t < DRK_MIN_T) {
        p.setStatusMessage(Text.gray('Barely begun. Nothing to bottle yet.'))
      } else {
        drkCollect(p, s, now)
        delete drkState[k]
        drkSave()
      }
    } else if (s.timed) {
      p.setStatusMessage(Text.gray('It is ' + drkStageWord(t) + '. Sneak and right-click to bottle it now.'))
    } else {
      p.setStatusMessage(Text.gray('Still working: about ' + Math.ceil((s.end - now) / 1200) + ' minutes left.'))
    }
    event.cancel()
    return
  }
  if (p.crouching && drkRework(p, event.block, role, now, k)) {
    event.cancel()
    return
  }
  let held = String(p.mainHandItem.id)
  let opts = drkAllRecipes().filter(r => r.station === role && !drkLocked(r.out) && drkCan(p, r))
  if (held !== 'minecraft:air') {
    let narrowed = opts.filter(r => drkUses(r, held))
    if (narrowed.length) opts = narrowed
  }
  if (!opts.length) {
    let first = drkAllRecipes().filter(r => r.station === role && !drkLocked(r.out)).slice(0, 3)
    p.setStatusMessage(Text.red('Nothing to brew here with what you carry.'))
    first.forEach(r => p.tell(Text.gray(r.name + ': ' + drkNeeds(r))))
    event.cancel()
    return
  }
  let sk = String(p.uuid) + k
  let idx = ((drkSel[sk] === undefined ? -1 : drkSel[sk]) + (p.crouching ? 0 : 1)) % opts.length
  if (idx < 0) idx = 0
  drkSel[sk] = idx
  let rc = opts[idx]
  if (p.crouching) {
    rc.inputs.forEach(inp => drkTake(p, drkIds(inp[0]), inp[1]))
    drkState[k] = { out: rc.out, count: rc.count, end: now + rc.ticks, start: now, cap: rc.abv, timed: drkTimed(rc) }
    drkSave()
    p.setStatusMessage(Text.gold('Started ' + rc.name + ' (' + rc.abv + '%). Back in about ' + Math.ceil(rc.ticks / 1200) + ' minutes.'))
  } else {
    p.setStatusMessage(Text.yellow((idx + 1) + '/' + opts.length + ' ' + rc.name + (rc.abv ? ' (' + rc.abv + '%)' : '') + ' | ' + drkNeeds(rc) + ' | sneak to start'))
  }
  event.cancel()
})

BlockEvents.broken(event => {
  let role = DRK_ROLE_BLOCK[String(event.block.id)]
  if (!role) return
  let k = drkKey(event.block)
  let s = drkState[k]
  if (s && event.level.getGameTime() >= s.end) event.block.popItem(s.timed ? Item.of(s.out + '[custom_data={abv:' + s.cap + '}]', s.count) : Item.of(s.out, s.count))
  if (s) { delete drkState[k]; drkSave() }
})

ServerEvents.recipes(event => {
  let station = (id, pattern, keys) => { try { event.shaped(DRK_ITEM + id, pattern, keys) } catch (e) { console.warn('[drinks] station recipe ' + id + ' failed: ' + e) } }
  station('fermenting_vat', ['PPP', 'S S', 'PPP'], { P: '#minecraft:planks', S: 'minecraft:string' })
  station('pot_still', ['CCC', 'CBC', 'CCC'], { C: 'minecraft:copper_ingot', B: 'minecraft:bucket' })
  station('oak_cask', ['PCP', 'P P', 'PCP'], { P: '#minecraft:planks', C: 'minecraft:copper_ingot' })
  station('pressure_tank', ['III', 'IGI', 'III'], { I: 'minecraft:iron_ingot', G: 'minecraft:glass_pane' })
  station('column_still', ['ICI', 'CBC', 'ICI'], { I: 'minecraft:iron_ingot', C: 'minecraft:copper_ingot', B: 'minecraft:cauldron' })
  station('cold_cellar', ['BBB', 'BIB', 'BBB'], { B: 'minecraft:stone_bricks', I: 'minecraft:blue_ice' })
  event.shapeless(DRK_ITEM + 'hydrometer', ['minecraft:glass_bottle', 'minecraft:iron_nugget', 'minecraft:copper_ingot'])
  event.shapeless(DRK_ITEM + 'thermometer', ['minecraft:glass_bottle', 'minecraft:redstone', 'minecraft:iron_nugget'])
  // koji: a mould culture on steamed rice
  event.shapeless('2x ' + DRK_ITEM + 'koji', ['croptopia:rice', 'croptopia:rice', 'minecraft:brown_mushroom', DRK_ITEM + 'barm'])
  // each harvest crafts back into seeds
  DRINK_CROPS.forEach(c => event.shapeless('2x ' + DRK_ITEM + c[0] + '_seeds', [DRK_ITEM + c[2]]))
  event.shapeless('2x ' + DRK_ITEM + 'barm', ['minecraft:wheat', 'minecraft:honey_bottle'])
  // pressing: Create's mechanical press when present, a plain crafting grid otherwise
  ;[['croptopia:grape', 'grape_must'], ['minecraft:apple', 'apple_must']].forEach(([fruit, must]) => {
    event.shapeless('2x ' + DRK_ITEM + must, [fruit, fruit, fruit])
    try { if (Item.exists('create:mechanical_press')) event.recipes.create.pressing(DRK_ITEM + must, fruit) } catch (e) { console.warn('[drinks] Create pressing for ' + must + ' skipped: ' + e) }
  })
  ;['croptopia:barley', 'biomesoplenty:barley', 'minecraft:wheat'].filter(id => Item.exists(id)).forEach(id => {
    event.smoking(DRK_ITEM + 'malted_barley', id)
  })
})

// small-batch brews for the hand-fed keg and fermenting barrel (diaithir-ports diaithirbrewing): early ferments only
ServerEvents.generateData('before_mods', event => {
  let n = 0
  let used = {}
  let keyOf = ing => Object.keys(ing).sort().map(k => k + '*' + ing[k]).join('|')
  drkAllRecipes().filter(r => r.station === 'vat' && (r.age === 'I' || r.age === 'II')).forEach(r => {
    let ing = {}
    let total = 0
    let ok = true
    r.inputs.forEach(([g, c]) => {
      let ids = drkIds(g)
      if (!ids.length) { ok = false; return }
      ing[ids[0]] = (ing[ids[0]] || 0) + c
      total += c
    })
    if (!ok || total > 12) return
    // every brew needs its own ingredient set: add the drink's signature ingredients, then raise the main one
    let sig = DRK[r.id].sig.filter(id => Item.exists(id) && !ing[id])
    let added = 0
    while (used[keyOf(ing)] && total < 12) {
      if (sig.length && added < 3) { ing[sig.shift()] = 1; added++ } else { let k = Object.keys(ing)[0]; ing[k]++ }
      total++
    }
    if (used[keyOf(ing)]) { console.warn('[drinks] no unique keg ingredient set for ' + r.id); return }
    used[keyOf(ing)] = r.id
    event.json(DRK_ITEM.replace(':', ':diaithirbrewing/') + r.id, {
      station: total <= 6 ? 'keg' : 'fermenting_barrel', base: 'minecraft:water_bucket', base_returns: 'minecraft:bucket',
      ingredients: ing, ticks: r.ticks, drink: r.out, servings: r.count, abv: r.abv, container: 'minecraft:glass_bottle'
    })
    n++
  })
  console.info('[drinks] ' + n + ' keg and barrel brews')
})

// Seeds turn up in the grass of the biomes the plant really grows in
BlockEvents.broken('minecraft:short_grass', event => {
  try {
    if (Math.random() > 0.04) return
    let biome = String(event.block.biomeId)
    let hits = DRINK_CROPS.filter(c => c[4].some(w => biome.indexOf(w) >= 0))
    if (hits.length) event.block.popItem(DRK_ITEM + hits[Math.floor(Math.random() * hits.length)][0] + '_seeds')
  } catch (e) {}
})
