// Make Create mixing recipes (heated basin) from the drinks KubeJS scripts, running their real code.
//
// usage: node gen_create_bridge_kubejs.mjs <script dir with a_data.js + brewing.js> <out data dir> [--have items.txt]
//
// brewing.js already builds one hand-fed keg/barrel brew per age I/II vat drink, each with its own ingredient
// set (event.json of 'before_mods' generateData). This runs that script with KubeJS stubbed out and turns each
// of those brews into a heated-basin create:mixing recipe: one bucket of water plus the same items, 3 servings.
// --have lists the item ids the pack has (one per line); without it every item is taken to exist.
// A brew with more than 9 items (Create's limit) is skipped and reported.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const [dir, out] = process.argv.slice(2, 4);
const haveFile = process.argv.includes('--have') ? process.argv[process.argv.indexOf('--have') + 1] : null;
const have = haveFile ? new Set(fs.readFileSync(haveFile, 'utf8').split(/\s+/).filter(Boolean)) : null;
const BUCKET = 81000; // fluid units in the port: 20250 per 250 mb
const MAX_ITEMS = 9;
const extra = {};

const noop = () => {};
// any KubeJS global the scripts touch at load time (PlayerEvents, Text, ...) becomes a do-nothing stub
const stub = () => new Proxy(noop, { get: (_t, k) => (k === Symbol.toPrimitive ? () => '' : stub()), apply: () => stub() });
const src = ['a_data.js', 'brewing.js'].map(f => fs.readFileSync(path.join(dir, f), 'utf8')).join('\n');
let generate = null;
let sandbox;
for (let attempt = 0; attempt < 50; attempt++) {
  generate = null;
  sandbox = sandbox0();
  vm.createContext(sandbox);
  try {
    vm.runInContext(src, sandbox);
    break;
  } catch (e) {
    const m = /^(\w+) is not defined/.exec(e.message);
    if (!m) throw e;
    extra[m[1]] = stub();
  }
}
if (!generate) throw new Error('brewing.js registered no generateData handler');
function sandbox0() {
  return {
    ...extra,
    console: { info: noop, warn: noop, log: noop },
    Item: { exists: id => !have || have.has(id) },
    ServerEvents: { generateData: (_stage, cb) => { generate = cb; }, loaded: noop, recipes: noop },
    BlockEvents: { rightClicked: noop, broken: noop },
  };
}

// strength of each drink (a_data.js DRINK_ROWS), stamped on the basin's output as custom_data abv:X.Xd
const keys = vm.runInContext('DRINK_KEYS', sandbox);
const abvOf = {};
for (const row of vm.runInContext('DRINK_ROWS', sandbox)) abvOf['diaithir_drinks:' + row[0]] = row[keys.indexOf('abv')];

const brews = [];
generate({ json: (id, body) => brews.push([id, body]) });

const abvResult = b => {
  const abv = b.abv ?? abvOf[b.drink];
  const r = { id: b.drink, count: b.servings };
  if (abv > 0) r.components = { 'minecraft:custom_data': `{abv:${Number(abv).toFixed(1)}d}` };
  return r;
};

// A basin hands out the recipe it matches first, and a bigger set also contains every smaller recipe inside it,
// so the bigger drink could never be made. Make the sets an antichain: wherever recipe A's items sit inside
// recipe B's, give A one extra item B does not use (its own signature items first, then cheap vanilla adjuncts).
const sigOf = {};
for (const row of vm.runInContext('DRINK_ROWS', sandbox)) sigOf['diaithir_drinks:' + row[0]] = row[keys.indexOf('sig')] ?? [];
const POOL = ['minecraft:sugar_cane', 'minecraft:potato', 'minecraft:carrot', 'minecraft:beetroot', 'minecraft:melon_slice', 'minecraft:cactus',
  'minecraft:sweet_berries', 'minecraft:apple', 'minecraft:wheat', 'minecraft:sugar', 'minecraft:honey_bottle', 'minecraft:kelp', 'minecraft:pumpkin_seeds'];
const size = ing => Object.values(ing).reduce((a, n) => a + n, 0);
const inside = (a, b) => Object.entries(a).every(([k, n]) => (b[k] ?? 0) >= n);
const sets = brews.map(([, b]) => b.ingredients);
const stuck = new Set();
for (let pass = 0; pass < 200; pass++) {
  let changed = false;
  for (let i = 0; i < sets.length; i++) {
    for (let j = 0; j < sets.length; j++) {
      if (i === j || !inside(sets[i], sets[j])) continue;
      const cands = [...(sigOf[brews[i][1].drink] ?? []), ...POOL].filter(c => (!have || have.has(c)) && !(c in sets[i]) && !(c in sets[j]));
      if (size(sets[i]) >= MAX_ITEMS || !cands.length) { stuck.add(brews[i][0]); continue; }
      sets[i][cands[0]] = 1;
      changed = true;
    }
  }
  if (!changed) break;
}
for (const id of stuck) console.log(`note ${id.split('/').pop()}: still sits inside another brew's set (no room for a distinguishing item)`);

const dest = path.join(out, 'create', 'recipe', 'mixing');
fs.mkdirSync(dest, { recursive: true });
let made = 0;
for (const [id, b] of brews) {
  const name = id.split('/').pop();
  const items = Object.entries(b.ingredients).flatMap(([item, n]) => Array(n).fill(item));
  if (items.length > MAX_ITEMS) { console.log(`skip ${name}: ${items.length} items, Create allows ${MAX_ITEMS}`); continue; }
  const rec = {
    'neoforge:conditions': [{ type: 'neoforge:mod_loaded', modid: 'diaithir_create' }],
    type: 'create:mixing',
    heat_requirement: 'heated',
    processing_time: Math.min(2400, Math.max(20, Math.floor(b.ticks / 20))),
    ingredients: items,
    fluid_ingredients: [{ type: 'fluid_stack', amount: BUCKET, fluid: 'minecraft:water' }],
    results: [abvResult(b)],
  };
  fs.writeFileSync(path.join(dest, `brew_${name}.json`), JSON.stringify(rec, null, 1) + '\n');
  made++;
}
console.log(`${made} written, ${brews.length - made} skipped`);
