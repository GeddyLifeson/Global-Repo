t = open('/tmp/claude-0/bm2/template.html').read()
def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (a[:60], t.count(a))
    t = t.replace(a, b)

# --- controls: more overlays
rep('<label class="tog" id="tcr"><input type="checkbox" id="ocr"> Cropland</label>',
    '<label class="tog" id="tcr"><input type="checkbox" id="ocr"> Cropland</label>\n<label class="tog" id="tur"><input type="checkbox" id="our"> Towns and cities</label>\n<label class="tog" id="trb"><input type="checkbox" id="orb"> Sea over still-sunken crust</label>')
# --- rodos panel + hide switch
rep('<section>\n<div class="mapbox">', '<section id="rodos" hidden></section>\n<section id="globe">\n<div class="mapbox">')
rep('<section id="sea">', '<section id="sea" class="globe">')
rep('.meth p{max-width', '[hidden]{display:none!important}\n#rodos svg{width:100%;height:auto;display:block;background:var(--panel);border:1px solid var(--line);border-radius:6px}\n#rodos .grid2{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:16px;align-items:start}\n@media(max-width:860px){#rodos .grid2{grid-template-columns:minmax(0,1fr)}}\n#rodos text{fill:var(--fg);font:12px var(--font)}#rodos .m{fill:var(--mute)}\n.meth p{max-width')

# --- ages
i0 = t.index('const AGES=['); i1 = t.index('];', i0) + 2
t = t[:i0] + """const AGES=[
 {id:'i',name:'Age I',note:'Ice-age end, hunter-gatherers',bp:'14,872 to 9,549 years ago',sl:[15,14,13,12,11,10]},
 {id:'ii',name:'Age II',note:'Farming spreads',bp:'9,549 to 4,947 years ago',sl:[9,8,7,6,5]},
 {id:'iii',name:'Age III',note:'Bronze and iron',bp:'4,947 to 1,988 years ago',sl:[5,4,3,2]},
 {id:'iv',name:'Age IV',note:'Roman to steam',bp:'1,988 to 170 years ago',sl:[2,1,'y1700']},
 {id:'v',name:'Age V',note:'Industrial',bp:'170 to 20 years ago (AD 1780 to 1930)',sl:['y1800','y1850','y1900'],people:1},
 {id:'vi',name:'Age VI',note:'Twentieth century',bp:'20 years ago to AD 2000 (AD 1930 to 2000)',sl:['y1930','y1960','y2000'],people:1},
 {id:'vii',name:'Age VII',note:'Turn of the millennium',bp:'AD 2000 to 2026',sl:['y2017'],people:1},
 {id:'future',name:'Future',note:'Modelled climate, end of this century',bp:'after 2026, no date in the game',sl:['f245','f585']},
 {id:'rodos',name:'Rodos',note:'Two made worlds, design',bp:'opens at Age Rodos, AD 2026 onward',sl:[0],rodos:1}
];""" + t[i1:]

# --- labels
rep("function label(k){return k==='future'?'Sketch: warmer world':k===0?'Today':(k*1000).toLocaleString('en-US')+' years ago'}",
    "function label(k){if(k==='f245')return '2071 to 2099, middle path';if(k==='f585')return '2071 to 2099, high emissions';if(typeof k==='string'&&k[0]==='y')return 'AD '+k.slice(1);return k===0?'Today':(k*1000).toLocaleString('en-US')+' years ago'}")

# --- slice loading with ur, rb
rep("const [c,lu,cr]=await Promise.all([gray(m.c,0),m.lu?gray(m.lu,0):null,m.cr?gray(m.cr,0):null]);",
    "const [c,lu,cr,ur,rb]=await Promise.all([gray(m.c,0),m.lu?gray(m.lu,0):null,m.cr?gray(m.cr,0):null,m.ur?gray(m.ur,0):null,m.rb?gray(m.rb,0):null]);")
rep("return cache[k]={c,lu,cr,cnt,land,m};", "return cache[k]={c,lu,cr,ur,rb,cnt,land,m};")

# --- draw
rep("const showLu=$('olu').checked&&s.lu,showCr=$('ocr').checked&&s.cr;", "const showLu=$('olu').checked&&s.lu,showCr=$('ocr').checked&&s.cr,showUr=$('our').checked&&s.ur,showRb=$('orb').checked&&s.rb;")
rep("if(c===0){const t=depth[p]/255;r=deep[0]+(sea[0]-deep[0])*t;g=deep[1]+(sea[1]-deep[1])*t;b=deep[2]+(sea[2]-deep[2])*t}",
    "if(c===0){const t=depth[p]/255;r=deep[0]+(sea[0]-deep[0])*t;g=deep[1]+(sea[1]-deep[1])*t;b=deep[2]+(sea[2]-deep[2])*t;if(showRb&&s.rb[p]){const a=.8;r+=(214-r)*a;g+=(96-g)*a;b+=(77-b)*a}}")
rep("if(dim&&c!==sel)", "if(showUr&&s.ur[p]){const a=Math.min(1,s.ur[p]/255*1.2);r+=(200-r)*a;g+=(40-g)*a;b+=(60-b)*a}\n   if(dim&&c!==sel)")

# --- facts
rep("<div><b>${(s.cnt[28]/(W*H)*100).toFixed(1)}%</b><small>of the globe is ice</small></div>`;",
    "<div><b>${(s.cnt[28]/(W*H)*100).toFixed(1)}%</b><small>of the globe is ice</small></div>${m.lake_pct>0?`<div><b>${m.lake_pct.toFixed(2)}%</b><small>of the globe is a modelled lake</small></div>`:''}${m.rb_m>0?`<div><b>${m.rb_m} m</b><small>deepest sinking of the crust under flooded land</small></div>`:''}${m.changed_pct?`<div><b>${m.changed_pct.toFixed(1)}%</b><small>of land changes climate class</small></div>`:''}`;")
rep("$('tcr').toggleAttribute('data-off',!s.cr);$('ocr').disabled=!s.cr;", "$('tcr').toggleAttribute('data-off',!s.cr);$('ocr').disabled=!s.cr;$('tur').toggleAttribute('data-off',!s.ur);$('our').disabled=!s.ur;$('trb').toggleAttribute('data-off',!s.rb);$('orb').disabled=!s.rb;")
# flag block
i0 = t.index("if(k==='future'){f.style.display='block'"); i1 = t.index("else f.style.display='none';", i0)
t = t[:i0] + """if(k==='f245'||k==='f585'){f.style.display='block';f.textContent='Modelled, one scenario each. Where the Koppen-Geiger climate class of a place changes by 2071 to 2099, the cell takes the vegetation of the nearest place on Earth that has that class today. The game’s Future has no date; this is a stand-in.'}
 else if(a.people&&k!=='y1700'){f.style.display='block';f.textContent='Vegetation here is the natural cover for today’s climate. People are drawn on top from HYDE: cleared woodland, cropland and towns.'}
 """ + t[i1:]

# --- setAge: defaults + rodos
rep("function setAge(i,keepIdx){age=i;idx=keepIdx?Math.min(idx,AGES[i].sl.length-1):0;",
    "function setAge(i,keepIdx){age=i;idx=keepIdx?Math.min(idx,AGES[i].sl.length-1):0;\n const ro=!!AGES[i].rodos;$('rodos').hidden=!ro;$('globe').hidden=ro;$('sea').hidden=ro;document.querySelector('.row').hidden=ro;$('facts').hidden=ro;\n if(AGES[i].people){$('olu').checked=$('ocr').checked=$('our').checked=true}\n if(ro){rodos();}")
rep("$('olu').onchange=$('ocr').onchange=draw;", "$('olu').onchange=$('ocr').onchange=$('our').onchange=$('orb').onchange=draw;")
rep("async function draw(){\n const k=sliceKey()", "async function draw(){\n if(AGES[age].rodos)return;\n const k=sliceKey()")

# --- marker + tooltips
rep("function marker(k){const mk=document.getElementById('mk');if(!mk)return;const ka=k==='future'?0:k;const m=DATA.imgs[k==='future'?0:k].sea;mk.setAttribute('transform',`translate(${window._sx(ka)},${window._sy(m)})`)}",
    "function marker(k){const mk=document.getElementById('mk');if(!mk)return;const ka=typeof k==='string'?(k[0]==='y'?Math.max(0,(1950-(+k.slice(1)))/1000):0):k;const m=DATA.imgs[k].sea;mk.setAttribute('transform',`translate(${window._sx(ka)},${window._sy(m)})`)}")
rep("if(c&&s.cr&&s.cr[p])t+='<br>cropland '+Math.round(s.cr[p]/255*100)+'%';", "if(c&&s.cr&&s.cr[p])t+='<br>cropland '+Math.round(s.cr[p]/255*100)+'%';\n if(c&&s.ur&&s.ur[p])t+='<br>towns and cities '+(s.ur[p]>200?'dense':'scattered');\n if(!c&&s.rb&&s.rb[p])t='Sea over sunken crust<br>'+Math.abs(lat).toFixed(1)+(lat<0?'°S ':'°N ')+Math.abs(lon).toFixed(1)+(lon<0?'°W':'°E');")

# --- rodos panel
rodos_js = r"""
function rodos(){
 const R=$('rodos');if(R.dataset.done){return}R.dataset.done=1;
 const rg=[['North-west Corner',-1,-1],['North End',0,-1],['North-east Corner',1,-1],['West End',-1,0],['Middle of the Ring',0,0],['East End',1,0],['South-west Corner',-1,1],['South End',0,1],['South-east Corner',1,1]];
 const S=400,o=40,u=S/3;let g='';
 rg.forEach(r=>{g+=`<rect x="${o+(r[1]+1)*u}" y="${o+(r[2]+1)*u}" width="${u}" height="${u}" fill="${(r[1]+r[2])%2?'color-mix(in srgb,var(--accent) 7%,transparent)':'color-mix(in srgb,var(--accent) 14%,transparent)'}" stroke="var(--line)"/><text class="m" x="${o+(r[1]+1)*u+8}" y="${o+(r[2]+1)*u+(r[2]===-1?32:18)}" style="font-size:11px">${r[0]==='Middle of the Ring'?'Middle of':r[0]}</text>${r[0]==='Middle of the Ring'?`<text class="m" x="${o+(r[1]+1)*u+8}" y="${o+(r[2]+1)*u+32}" style="font-size:11px">the Ring</text>`:''}`});
 const cx=o+S/2,cy=o+S/2;
 const gates=[[cx,o],[cx,o+S],[o,cy],[o+S,cy]];
 let rd='';gates.forEach(p=>{rd+=`<line x1="${p[0]}" y1="${p[1]}" x2="${cx}" y2="${cy}" stroke="var(--warn)" stroke-width="2" stroke-dasharray="6 4"/>`});
 gates.forEach(p=>{rd+=`<rect x="${p[0]-6}" y="${p[1]-6}" width="12" height="12" fill="var(--warn)"/>`});
 const rim=`<rect x="${o}" y="${o}" width="${S}" height="14" fill="#8a7a62" opacity=".5"/><rect x="${o}" y="${o+S-14}" width="${S}" height="14" fill="#8a7a62" opacity=".5"/><text class="m" x="${o+8}" y="${o+11}" style="font-size:10px">The Rim (hills)</text><text class="m" x="${o+8}" y="${o+S-3}" style="font-size:10px">The Rim (hills)</text>`;
 const ring=`<svg viewBox="0 0 ${S+2*o} ${S+2*o+34}" role="img" aria-label="The Great Ring, schematic plan">${g}${rim}${rd}<circle cx="${cx}" cy="${cy}" r="6" fill="var(--accent)"/><text x="${cx+10}" y="${cy+22}" style="font-size:11px">Waymark of Origin</text><text class="m" x="${o}" y="${o-14}" style="font-size:11px">north (−Z)</text><text class="m" x="${o+S}" y="${o-14}" text-anchor="end" style="font-size:11px">east (+X, spinward)</text><text class="m" x="${o}" y="${o+S+28}" style="font-size:11px">Square, 40,000 blocks = 200 km a side. Plan, not terrain.</text></svg>`;
 const hs=200,ht=`<svg viewBox="0 0 260 300" role="img" aria-label="The High Town, schematic plan"><rect x="30" y="20" width="${hs}" height="${hs}" fill="color-mix(in srgb,var(--fg) 12%,transparent)" stroke="var(--line)"/><circle cx="130" cy="120" r="9" fill="var(--accent)"/><text x="130" y="105" text-anchor="middle">Aperture Plaza</text><rect x="124" y="136" width="12" height="6" fill="var(--warn)"/><text class="m" x="144" y="142" style="font-size:11px">Seat Steps</text><text class="m" x="130" y="238" text-anchor="middle" style="font-size:11px">Square, 12,000 blocks = 60 km a side.</text><text class="m" x="130" y="254" text-anchor="middle" style="font-size:11px">Flat, paved, top block Y63. Plan, not terrain.</text></svg>`;
 R.innerHTML=`<div class="grid2"><div><h2>The Great Ring</h2>${ring}</div><div><h2>The High Town</h2>${ht}<p class="note">Streets and towers are a later build job; the plan only places the two named structures.</p></div></div>
 <p class="note" style="max-width:80ch;margin-top:12px"><b>What this is.</b> Rodos has no Azgaar source and no globe map: both worlds are made, not grown, so this is the design spec drawn as a plan. Scale 1:5, sea level Y63. The Great Ring is a square world of wide meadows, long rivers and meres under mild steady weather; the four Ring Gates stand 19,900 blocks out from the Waymark, joined to it by the Gate Roads (planned, laid by the routes system). Biomes are scattered by noise inside every reach: Great Meadow, Flower Lea, Ring Wood, Long Fen, Long River, Ring Mere, Mere Strand, and the Rim hills on the north and south edges. The High Town is a separate flat world, the seat of a far empire whose name is not in any file, where travellers from other shelves trade. Both open at Age Rodos (AD 2026 onward). Source: maps/rodos/rodos.json and README.md in the shared project files.</p>`;
}
"""
rep("// sea level strip", rodos_js + "// sea level strip")

# --- methods
i0 = t.index('<section class="meth">'); i1 = t.index('</section>', i0) + len('</section>')
t = t[:i0] + """<section class="meth">
<h2>How it is drawn</h2>
<p><b>Vegetation.</b> BIOME4 classes at half a degree for each dated slice from 15,000 years ago to today (Beyer, Krapp and Manica 2020, CC BY 4.0, with Neotoma pollen overrides), drawn at quarter-degree coasts. The game places Minecraft and mod biomes inside each class; the finer layer is not drawn here yet.</p>
<p><b>Coast and crust.</b> Land is wherever today's relief (ETOPO 2022) stands above that slice's sea level (the timeline's sea curve). Under the ice sheets the crust sank, and a ring around them bulged up. The model: each cell sinks 0.2 times the ice thickness (ICE-NADI-1 and DATED-1 extra ice) through a plate response, a smoothing of about 170 km minus a wider one of about 330 km that leaves a peripheral forebulge of about 9% of the depression, and the displacement relaxes toward that with a time constant of 7 thousand years. Ground that is still lower than today's by more than the sea allows is flooded (Hudson Bay, the Baltic, the St Lawrence), and ground raised by the bulge above the sea of the day is dry land (the shelf off the US east coast, up to 27 m of uplift at 15 thousand years ago). The two fitted numbers were tuned to four approximate published values: the Scandinavian marine limit of about 290 m at 9.5 thousand years ago, the Hudson Bay marine limit of about 270 m at 8 thousand years ago, and the uplift still to come today of about 150 m in Hudson Bay and 100 m around the Gulf of Bothnia. The model gives 279, 310, 148 and 97 m. ICE-6G_C was not used because no licence for it was found. The bulge amplitude is a chosen ratio, not fitted to observations. The model ignores ice before 15 thousand years ago (the crust is assumed settled under the 15 thousand year ice) and the shape of the ice margin below the 30 m cut-off.</p>
<p><b>Lakes.</b> The 11 lakes the game builds from its elevation model (Baltic Ice Lake to 11.7 thousand years ago, the Black Sea lake while the sea stands below its level, Lake Chicago, the Patagonian palaeolakes) and two stages of Lake Agassiz, Herman at 335 m from 11.5 to 10.9 and Campbell at 299 m from 10.9 to 8.4 thousand years ago. Lake Chicago and the Patagonian lakes have no drainage dates in any source we found, so they are drawn through Age I only; the game itself has no end date for them. Lake Ojibway and the later Black Sea refilling are left out for the same reason.</p>
<p><b>Ice.</b> Extra ice over today's surface from NADI-1 and DATED-1, 15 to 6 thousand years ago, plus the Greenland and Antarctic sheets at every date. There is no Eurasian ice mask after 10 thousand years ago, so Fennoscandia is ice-free from then on.</p>
<p><b>People.</b> Cleared woodland, cropland and towns come from HYDE 3.2.1 anthromes (CC0): every thousand years from 8000 BC to AD 1, then AD 1700, 1800, 1850, 1900, 1930, 1960, 2000 and 2017. The vegetation underneath for Ages V to VII is today's natural cover; only the people overlay changes.</p>
<p><b>Ages.</b> Spans come from the timeline presets. Age V is AD 1780 to 1930, VI is 1930 to 2000, VII is 2000 to 2026.</p>
<p><b>Future.</b> Beck et al. 2023 (CC BY 4.0) Koppen-Geiger maps for 1991 to 2020 and 2071 to 2099 under the middle path (SSP2-4.5) and high emissions (SSP5-8.5). Where a cell changes climate class, it takes the vegetation and the climate values (temperature, coldest and warmest month, precipitation, dryness) of the nearest place on Earth (by great-circle distance, half-degree cells) that already has the new class; unchanged cells keep today's. The Game biomes layer runs the pack palette on those values. Sea +0.6 m is below the map's resolution, and the ice sheets stay. This is a climate-analog model, not a vegetation simulation, and the game gives the Future no date.</p>
<p><b>Rodos.</b> A plan of the two made worlds from the design spec, not a globe map.</p>
</section>""" + t[i1:]
open('/tmp/claude-0/bm2/template2.html', 'w').write(t)
print(len(t))
