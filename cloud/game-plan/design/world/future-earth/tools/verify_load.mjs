// Check the .map loads in FMG: open the page, upload the file, print a few names back
// Usage: FMG_DIR=<fmg checkout> node verify_load.mjs future-earth.map
import { readFileSync } from "node:fs";
const { chromium } = await import(`${process.env.FMG_DIR}/node_modules/playwright/index.mjs`);
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH ?? "/opt/pw-browsers/chromium" });
const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
page.on("pageerror", e => console.log("page error:", e.message));
const base = "http://localhost:5173/Fantasy-Map-Generator/";
await page.goto(base);
await page.evaluate(() => { localStorage.clear(); localStorage.setItem("version", "99.0.0"); });
await page.goto(base + "?seed=1&width=1600&height=900");
await page.waitForFunction(() => (window.mapHistory?.length ?? 0) > 0, null, { timeout: 300000 });
const before = await page.evaluate(() => mapHistory.length);
const text = readFileSync(process.argv[2], "utf8");
await page.evaluate(t => Services.Load.uploadMap(new File([t], "future-earth.map")), text);
await page.waitForFunction(n => mapHistory.length > n, before, { timeout: 300000 });
await page.waitForTimeout(2000);
console.log(await page.evaluate(() => ({
  name: options.map.lore?.name ?? null,
  states: pack.states.filter(s => s.i && !s.removed).length,
  dia: pack.states.find(s => s.name === "Diaithìr")?.fullName,
  markers: pack.markers.map(m => m.name).filter(n => /Last Port|Diaithir|Glass/.test(n)),
  lastPortNote: pack.markers.find(m => m.name === "Last Port")?.note?.slice(0, 60)
})));
await browser.close();
