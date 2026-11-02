// Generate the future Earth map in Azgaar's FMG (vite dev server on :5173) and export .map, SVG and PNG.
// Usage: FMG_DIR=<fmg checkout> node build_map.mjs future_earth.json future-earth-heightmap.png outDir
import { readFileSync, writeFileSync } from "node:fs";

const { chromium } = await import(`${process.env.FMG_DIR}/node_modules/playwright/index.mjs`);

const [cfgPath, heightmapPath, outDir] = process.argv.slice(2);
const cfg = JSON.parse(readFileSync(cfgPath, "utf8"));
const BASE = "http://localhost:5173/Fantasy-Map-Generator/";
// map box: 72N to 56S, 170W to 180E (make_heightmap.py); FMG derives it from size and shifts
const geo = { mapSize: (128 / 180) * 100, latitude: (18 / 52) * 100, longitude: 0 };

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH ?? "/opt/pw-browsers/chromium" });
const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
page.on("pageerror", e => console.log("page error:", e.message));
await page.route("**/heightmaps/world.png", route =>
  route.fulfill({ contentType: "image/png", body: readFileSync(heightmapPath) })
);

await page.goto(BASE);
const pins = {
  ...cfg.pins, ...geo, mapWidth: cfg.width, mapHeight: cfg.height,
  mapName: cfg.mapName, year: cfg.year, era: cfg.era, eraShort: cfg.eraShort
};
await page.evaluate(p => {
  localStorage.clear();
  localStorage.setItem("version", "99.0.0");
  localStorage.setItem("fmg-locks", JSON.stringify(p));
}, pins);
await page.goto(`${BASE}?seed=${cfg.seed}&width=${cfg.width}&height=${cfg.height}`);
await page.waitForFunction(() => (window.mapHistory?.length ?? 0) > 0, null, { timeout: 600000 });

const report = await page.evaluate(cfg => {
  const { cells, burgs, states, cultures, religions, provinces } = pack;
  const c = options.map.geography.coordinates;
  const { width: W, height: H } = options.map.graph;
  const toLatLon = ([x, y]) => [c.latN - (y / H) * c.latT, c.lonW + (x / W) * c.lonT];
  const toXY = (lat, lon) => [((lon - c.lonW) / c.lonT) * W, ((c.latN - lat) / c.latT) * H];
  const degrees = ([la1, lo1], [la2, lo2]) =>
    Math.hypot(la1 - la2, (lo1 - lo2) * Math.cos((((la1 + la2) / 2) * Math.PI) / 180));
  const nearestCell = (x, y, land) => {
    let best = 0, bd = Infinity;
    for (const i of cells.i) {
      if (land && cells.h[i] < 20) continue;
      const d = (cells.p[i][0] - x) ** 2 + (cells.p[i][1] - y) ** 2;
      if (d < bd) [bd, best] = [d, i];
    }
    return best;
  };
  const live = list => list.filter(e => e.i && !e.removed);
  // closest pairs first, each name used once; anything left unmatched keeps a generated name
  const match = (entities, where, names) => {
    const pairs = [];
    for (const e of entities)
      for (const n of names) {
        const d = degrees(where(e), n.slice(-2));
        if (d <= cfg.maxMatchDegrees) pairs.push([d, e, n]);
      }
    pairs.sort((p, q) => p[0] - q[0]);
    const result = new Map(), taken = new Set();
    for (const [, e, n] of pairs) {
      if (result.has(e) || taken.has(n)) continue;
      result.set(e, n);
      taken.add(n);
    }
    return result;
  };

  // far overseas holdings (naval states hug every coast at this scale) go to the nearest state on their landmass
  const capCell = s => burgs[s.capital].cell;
  const far = i => {
    const s = states[cells.state[i]];
    return s.i && cells.f[i] !== cells.f[capCell(s)] && degrees(toLatLon(cells.p[i]), toLatLon(cells.p[capCell(s)])) > 10;
  };
  let orphans = Array.from(cells.i).filter(i => cells.h[i] >= 20 && far(i));
  for (const i of orphans) cells.state[i] = 0;
  for (let pass = 0; pass < 60 && orphans.length; pass++) {
    orphans = orphans.filter(i => {
      const n = cells.c[i].find(n => cells.state[n] && cells.f[n] === cells.f[i]);
      if (n) cells.state[i] = cells.state[n];
      return !n;
    });
  }
  // regions the generator left without a state get one, carved around the listed anchor
  const forced = new Map();
  for (const def of cfg.forceStates) {
    const center = nearestCell(...toXY(def[2], def[3]), true);
    if (cells.burg[center] && burgs[cells.burg[center]].capital) continue;
    if (!cells.burg[center]) Burgs.add(...cells.p[center]);
    const id = States.add(...cells.p[center]);
    // grow across land from the anchor at a cost that rises with height and a fixed per-cell jitter, so the
    // border is ragged and follows ridges; it takes neutral land and land far nearer it than its own capital
    const anchor = def.slice(2, 4);
    const takes = i => {
      if (cells.h[i] < 20 || (cells.burg[i] && burgs[cells.burg[i]].capital)) return false;
      if (!cells.state[i]) return true;
      const own = states[cells.state[i]];
      return degrees(toLatLon(cells.p[i]), anchor) < 0.6 * degrees(toLatLon(cells.p[i]), toLatLon(cells.p[capCell(own)]));
    };
    const jitter = i => { const x = Math.sin(i * 12.9898) * 43758.5453; return x - Math.floor(x); };
    const budget = def[4] / 0.6;
    const cost = new Map([[center, 0]]), carved = [];
    const queue = [center];
    while (queue.length) {
      queue.sort((p, q) => cost.get(q) - cost.get(p));
      const i = queue.pop();
      carved.push(i);
      for (const n of cells.c[i]) {
        if (cost.has(n) || !takes(n)) continue;
        const c2 = cost.get(i) + 0.6 + Math.max(0, cells.h[n] - 30) / 15 + jitter(n) * 1.2;
        if (c2 > budget) continue;
        cost.set(n, c2);
        queue.push(n);
      }
    }
    States.setCells(id, carved);
    forced.set(id, def);
  }
  // neutral land joins the nearest state across land
  let neutral = Array.from(cells.i).filter(i => cells.h[i] >= 20 && !cells.state[i]);
  for (let pass = 0; pass < 40 && neutral.length; pass++) {
    const claims = neutral.map(i => [i, cells.c[i].find(n => cells.state[n] && cells.f[n] === cells.f[i])]);
    for (const [i, n] of claims) if (n) cells.state[i] = cells.state[n];
    neutral = claims.filter(([, n]) => !n).map(([i]) => i);
  }
  for (const b of live(burgs)) b.state = cells.state[b.cell];
  States.getPoles();
  States.findNeighbors();
  States.collectStatistics();
  Provinces.generate();
  Provinces.getPoles();

  // Diaithir: its island gets its own culture, faith and state
  const dia = cfg.markers.find(m => m.type === "diaithir");
  const diaCell = nearestCell(...toXY(dia.lat, dia.lon), true);
  const diaCells = Array.from(cells.i).filter(i => cells.f[i] === cells.f[diaCell]);
  const diaCulture = cultures[Cultures.add(...cells.p[diaCell])];
  for (const i of diaCells) cells.culture[i] = diaCulture.i;
  const diaRel = religions[Religions.add(...cells.p[diaCell])];
  for (const i of diaCells) cells.religion[i] = diaRel.i;
  if (!cells.burg[diaCell]) Burgs.add(...cells.p[diaCell]);
  const diaState = States.add(...cells.p[diaCell]);
  States.setCells(diaState, diaCells);

  const cultureNames = match(live(cultures).filter(cu => cu !== diaCulture), cu => toLatLon(cells.p[cu.center]), cfg.cultures);
  for (const cu of live(cultures)) {
    const def = cu === diaCulture ? cfg.diaithir.culture : cultureNames.get(cu);
    if (def) [cu.name, cu.base] = def;
  }

  for (const b of live(burgs)) b.name = Names.getCulture(b.culture);
  const diaBurgs = live(burgs).filter(b => diaCells.includes(b.cell));
  diaBurgs.forEach((b, j) => (b.name = cfg.diaithirBurgs[j % cfg.diaithirBurgs.length]));

  const capitalAt = s => toLatLon([burgs[s.capital].x, burgs[s.capital].y]);
  const forcedNames = new Set([...forced.values()].map(d => d[0]));
  const stateNames = match(live(states).filter(s => s.i !== diaState && !forced.has(s.i)), capitalAt,
    cfg.states.filter(d => !forcedNames.has(d[0])));
  for (const s of live(states)) {
    const def = s.i === diaState ? cfg.diaithir.state : (forced.get(s.i) ?? stateNames.get(s));
    if (def) [s.name, s.formName] = def;
    s.fullName = `${s.name} ${s.formName}`;
  }
  for (const p of live(provinces)) {
    if (p.burg) p.name = burgs[p.burg].name;
    p.fullName = `${p.name} ${p.formName}`;
  }

  // organised faiths take the nearest listed name; folk faiths and any left over are named after their culture
  const suffix = { Folk: "Folk Rite", Organized: "Church", Cult: "Mystery", Heresy: "Dissent" };
  const faithNames = match(live(religions).filter(r => r.type !== "Folk" && r !== diaRel), r => toLatLon(cells.p[r.center]), cfg.religions);
  const named = new Set();
  for (const rel of live(religions)) {
    rel.name = faithNames.get(rel)?.[0] ?? `${cultures[rel.culture].name} ${suffix[rel.type] ?? "Faith"}`;
    if (named.has(rel.name)) rel.name = `${rel.name} of ${burgs[cells.burg[rel.center]]?.name || provinces[cells.province[rel.center]]?.name || rel.i}`;
    named.add(rel.name);
    if (cfg.religionDefs[rel.name]) rel.note = cfg.religionDefs[rel.name];
  }
  [diaRel.name, diaRel.note] = [cfg.diaithir.religion, cfg.religionDefs[cfg.diaithir.religion]];

  // generated markers are fantasy dressing; keep only the natural ones, then add ours
  pack.markers = pack.markers.filter(m => cfg.keepMarkerTypes.includes(m.type));
  for (const m of cfg.markers) {
    const [x, y] = toXY(m.lat, m.lon);
    const cell = nearestCell(x, y, m.type !== "drowned" && m.type !== "warscar");
    Markers.place(...cells.p[cell], m.type, { name: m.name, note: m.note, icon: m.icon });
  }

  const at = ll => `@${ll.map(Math.round)}`;
  return {
    coords: c,
    diaithir: { at: at(toLatLon(cells.p[diaCell])), cells: diaCells.length, burgs: diaBurgs.map(b => b.name), culture: diaCulture.name, state: states[diaState].fullName, religion: diaRel.name },
    states: live(states).map(s => `${s.fullName} ${s.cells} ${at(capitalAt(s))}`),
    cultures: live(cultures).map(cu => `${cu.name} ${at(toLatLon(cells.p[cu.center]))}`),
    religions: live(religions).map(r => `${r.name} (${r.type}) ${at(toLatLon(cells.p[r.center]))}`),
    burgs: live(burgs).length
  };
}, cfg);
writeFileSync(`${outDir}/build-report.json`, JSON.stringify(report, null, 1));

await page.evaluate(() => {
  Layers.show("markers", "coordinates");
  Layers.drawAll();
});
await page.waitForTimeout(3000);

const mapData = await page.evaluate(() => Services.Save.prepareMapData());
writeFileSync(`${outDir}/future-earth.map`, mapData);

const svg = await page.evaluate(async () => {
  const url = await Services.ExportMap.getMapURL("svg", { fullMap: true });
  return (await fetch(url)).text();
});
writeFileSync(`${outDir}/future-earth.svg`, svg);

const png = await page.evaluate(async scale => {
  const url = await Services.ExportMap.getMapURL("png", { fullMap: true });
  const { width, height } = options.map.graph;
  const canvas = Object.assign(document.createElement("canvas"), { width: width * scale, height: height * scale });
  const img = new Image();
  await new Promise((res, rej) => { img.onload = res; img.onerror = rej; img.src = url; });
  canvas.getContext("2d").drawImage(img, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/png").split(",")[1];
}, 2);
writeFileSync(`${outDir}/future-earth.png`, Buffer.from(png, "base64"));
await browser.close();
