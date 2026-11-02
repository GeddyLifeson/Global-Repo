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
  return (DRK_GROUPS[g] || []).filter(id => Item.exists(id))
}

function drkLocked(item) {
  return typeof techLocked === 'function' && techLocked(item)
}

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

function drkAllRecipes() {
  if (!drkRecipes) {
    drkRecipes = []
    DRINK_ROWS.forEach(row => { drkRecipes.push(drkRecipeFor(DRK[row[0]])) })
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
    try { Object.keys(raw).forEach(k => { drkState[k] = { out: String(raw[k].out), count: Number(raw[k].count), end: Number(raw[k].end) } }) } catch (e) { drkState = {} }
  }
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
    if (now >= s.end) {
      p.give(Item.of(s.out, s.count))
      p.setStatusMessage(Text.gold('Ready. You take ' + s.count + ' ' + Item.of(s.out).hoverName.string + '.'))
      delete drkState[k]
      drkSave()
    } else {
      p.setStatusMessage(Text.gray('Still working: about ' + Math.ceil((s.end - now) / 1200) + ' minutes left.'))
    }
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
    drkState[k] = { out: rc.out, count: rc.count, end: now + rc.ticks }
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
  if (s && event.level.getGameTime() >= s.end) event.block.popItem(Item.of(s.out, s.count))
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
      ingredients: ing, ticks: r.ticks, drink: r.out, servings: r.count, container: 'minecraft:glass_bottle'
    })
    n++
  })
  console.info('[drinks] ' + n + ' keg and barrel brews')
})
