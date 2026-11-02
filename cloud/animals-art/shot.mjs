import { chromium } from 'playwright';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 1200, height: 1300 } });
p.on('console', m => console.log('console:', m.text())); p.on('pageerror', e => console.log('err:', e.message));
await p.goto('file:///tmp/claude-0/-home-user-shardfall-game/c7c6e01c-f645-52a1-a902-bee2fbf5787f/scratchpad/trial.html');
await p.waitForTimeout(5000);
await p.screenshot({ path: 'shot.png', fullPage: true });
const cards = await p.$$('.cards button');
for (const i of [0,1,2,3,4,6]) { await cards[i].click(); await p.waitForTimeout(400); await (await p.$('.viewer')).screenshot({ path: `v${i}.png` }); }
await b.close();
