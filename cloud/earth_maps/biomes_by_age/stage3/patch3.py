t = open('/tmp/claude-0/bm2/template2.html').read()
def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (a[:70], t.count(a))
    t = t.replace(a, b)

# forebulge overlay
rep('<label class="tog" id="trb">', '<label class="tog" id="tfb"><input type="checkbox" id="ofb"> Land raised by the forebulge</label>\n<label class="tog" id="trb">')
rep("m.rb?gray(m.rb,0):null]);", "m.rb?gray(m.rb,0):null,m.fb?gray(m.fb,0):null]);")
rep("const [c,lu,cr,ur,rb]=", "const [c,lu,cr,ur,rb,fb]=")
rep("return cache[k]={c,lu,cr,ur,rb,cnt,land,m};", "return cache[k]={c,lu,cr,ur,rb,fb,cnt,land,m};")
rep("showRb=$('orb').checked&&s.rb;", "showRb=$('orb').checked&&s.rb,showFb=$('ofb').checked&&s.fb;")
rep("if(showUr&&s.ur[p])", "if(showFb&&s.fb[p]){r+=(235-r)*.8;g+=(150-g)*.8;b+=(40-b)*.8}\n   if(showUr&&s.ur[p])")
rep("$('trb').toggleAttribute('data-off',!s.rb);$('orb').disabled=!s.rb;", "$('trb').toggleAttribute('data-off',!s.rb);$('orb').disabled=!s.rb;$('tfb').toggleAttribute('data-off',!s.fb);$('ofb').disabled=!s.fb;")
rep("$('our').onchange=$('orb').onchange=draw;", "$('our').onchange=$('orb').onchange=$('ofb').onchange=draw;")
rep("${m.changed_pct?", "${m.fb_m>0?`<div><b>${m.fb_m} m</b><small>highest land raised by the forebulge</small></div>`:''}${m.changed_pct?")
# layer switch in the controls row
rep('<div class="slwrap">', '<div class="tabs" id="layer" role="group" aria-label="Layer"><button type="button" data-l="cls" aria-pressed="true">Vegetation class</button><button type="button" data-l="pk" aria-pressed="false">Game biomes</button></div>\n<div class="slwrap">')
rep('.row{display:flex;flex-wrap:wrap;gap:12px 28px;align-items:center}', '.row{display:flex;flex-wrap:wrap;gap:12px 28px;align-items:center}\n#layer button{padding:5px 12px;min-width:0;font-size:13px}\n.mod{color:var(--mute);font:11px var(--mono);margin-left:6px}')

# state + slice loading
rep("let depth=null;const cache={};let age=0,idx=0,sel=-1,filt='';", "let depth=null;const cache={};let age=0,idx=0,sel=-1,filt='',layer='cls';const pkc={};")
rep("return cache[k]={c,lu,cr,ur,rb,fb,cnt,land,m};",
    """const pkm=m.pk?m:(m.pkref?DATA.imgs[m.pkref]:null);let pk=null,pcnt=null;
 if(pkm){const key=m.pk?k:m.pkref;if(!pkc[key]){const i=await loadImg(pkm.pk);const cc=document.createElement('canvas');cc.width=W;cc.height=H;const x=cc.getContext('2d',{willReadFrequently:true});x.drawImage(i,0,0);const d=x.getImageData(0,0,W,H).data;const o=new Uint16Array(W*H);for(let p=0;p<W*H;p++)o[p]=d[p*4];pkc[key]=o}pk=pkc[key];
  pcnt=new Float64Array(DATA.vocab.length+1);for(let p=0;p<W*H;p++){if(pk[p]&&c[p]&&c[p]!==28&&c[p]!==30)pcnt[pk[p]]++}}
 return cache[k]={c,lu,cr,ur,rb,fb,cnt,land,m,pk,pcnt};""")

# colours
rep("function loadImg(src)", """const fr=x=>x-Math.floor(x);
function tint(c,n){const q=RGB[c]||[200,200,200];const f=.66+.7*fr(n*.61803),a=1+(fr(n*.371)-.5)*.5,b=1+(fr(n*.773)-.5)*.5;return [Math.min(255,q[0]*f*a),Math.min(255,q[1]*f),Math.min(255,q[2]*f*b)]}
const MODS={minecraft:'Vanilla',biomesoplenty:"Biomes O' Plenty",regions_unexplored:'Regions Unexplored',terralith:'Terralith',tellus:'Tellus',diaithir:'Diaithir'};
function pretty(id){const [ns,nm]=id.includes(':')?id.split(':'):['',id];const t=nm.replace(/_/g,' ');return [t.charAt(0).toUpperCase()+t.slice(1),MODS[ns]||ns]}
function loadImg(src)""")

# draw: pack layer colouring
rep("const dim=sel>=0;const bg=hex(rgbHex(css('--bg')));", "const usePk=layer==='pk'&&s.pk;const dim=sel>=0;const bg=hex(rgbHex(css('--bg')));")
rep("else{const q=RGB[c];r=q[0];g=q[1];b=q[2];", "else{let q=RGB[c];if(usePk&&c!==28&&c!==30&&s.pk[p])q=tint(DATA.dom[s.pk[p]-1],s.pk[p]);r=q[0];g=q[1];b=q[2];")
rep("if(dim&&c!==sel)", "if(dim&&(usePk?(s.pk[p]!==sel||c===28||c===30):c!==sel))")

# legend: by layer
i0 = t.index('function legend(s){'); i1 = t.index('function tabs(){')
t = t[:i0] + """function legend(s){
 const L=$('legend');L.innerHTML='';
 const tot=s.land-0||1;
 if(layer==='pk'&&s.pk){
  let ids=[];for(let i=1;i<s.pcnt.length;i++)if(s.pcnt[i]>0){const [nm,mod]=pretty(DATA.vocab[i-1]);if((nm+' '+mod).toLowerCase().includes(filt))ids.push(i)}
  ids.sort((a,b)=>s.pcnt[b]-s.pcnt[a]);
  let pt=0;for(let i=1;i<s.pcnt.length;i++)pt+=s.pcnt[i];pt=pt||1;
  for(const i of ids){const li=document.createElement('li'),b=document.createElement('button');const [nm,mod]=pretty(DATA.vocab[i-1]);const q=tint(DATA.dom[i-1],i);
   b.setAttribute('aria-pressed',String(i===sel));b.type='button';
   b.innerHTML=`<span class="sw" style="background:rgb(${q[0]|0},${q[1]|0},${q[2]|0})"></span><span class="nm">${nm}<span class="mod">${mod}</span></span><span class="pc">${(s.pcnt[i]/pt*100).toFixed(1)}%</span>`;
   b.onclick=()=>{sel=sel===i?-1:i;draw()};li.appendChild(b);L.appendChild(li)}
  return;
 }
 const ids=Object.keys(PAL).map(Number).filter(i=>i>0&&PAL[i][0].toLowerCase().includes(filt));
 ids.sort((a,b)=>s.cnt[b]-s.cnt[a]);
 const rows=[...ids.filter(i=>s.cnt[i]>0||i===sel)];
 if('ocean'.includes(filt))rows.push(0);
 for(const i of rows){
  const li=document.createElement('li'),b=document.createElement('button');
  b.setAttribute('aria-pressed',String(i===sel));b.type='button';
  const col=i===0?css('--sea'):PAL[i][1];
  b.innerHTML=`<span class="sw" style="background:${col}"></span><span class="nm">${PAL[i][0]}</span><span class="pc">${i===0?'':(s.cnt[i]/tot*100).toFixed(1)+'%'}</span>`;
  b.onclick=()=>{sel=sel===i?-1:i;draw()};
  li.appendChild(b);L.appendChild(li);
 }
}
""" + t[i1:]

# layer buttons: enable per slice, handler
rep("$('olu').onchange=", """document.querySelectorAll('#layer button').forEach(b=>b.onclick=()=>{if(b.disabled)return;layer=b.dataset.l;sel=-1;draw()});
$('olu').onchange=""")
rep("$('tcr').toggleAttribute('data-off',!s.cr);", "const hasPk=!!s.pk;if(!hasPk&&layer==='pk'){layer='cls';sel=-1}document.querySelectorAll('#layer button').forEach(b=>{b.disabled=b.dataset.l==='pk'&&!hasPk;b.setAttribute('aria-pressed',String(b.dataset.l===layer))});\n $('tcr').toggleAttribute('data-off',!s.cr);")

# hover
rep("let t=(c===0?'Ocean':PAL[c][0])", "let gb='';if(c&&c!==28&&c!==30&&s.pk&&s.pk[p]){const [pn,pm]=pretty(DATA.vocab[s.pk[p]-1]);gb='Game biome: '+pn+' ('+pm+')<br>'}\n let t=gb+(c===0?'Ocean':PAL[c][0])")
rep("$('mapnote').textContent='Hover the map for the biome under the pointer. Pick a biome in the list to highlight it. Half-degree data drawn at quarter-degree coasts.';",
    "$('mapnote').textContent=layer==='pk'?'Game biomes: the pack biome the Age palette picks for each place (vanilla, Biomes O’ Plenty, Regions Unexplored), one sample per quarter degree, tinted by name inside its vegetation class. Hover for the name.':'Hover the map for the biome under the pointer. Pick a biome in the list to highlight it. Half-degree data drawn at quarter-degree coasts.';")

# methods: replace the sentence about the finer layer
rep("The game places Minecraft and mod biomes inside each class; the finer layer is not drawn here yet.", "The game places Minecraft and mod biomes inside each class; switch to Game biomes to see that finer layer.")
rep("<p><b>Rodos.</b>", "<p><b>Game biomes.</b> The pack-biome palette (the Python mirror of EraPalette, rules in world/earth/biome/palette) is run once per dated slice from 15 thousand years ago to today, using that slice's BIOME4 class, climate rasters and sea level, today's relief for mountain belts, and one sample per eighth of a degree reduced to quarter degrees. The AD slices from 1700 on use today’s layer. The Future runs on the climate-analog values described above. Relief is today's, so crust rebound and ice do not move the mountain belts; ice and lake cells show the ice or lake instead.</p>\n<p><b>Rodos.</b>")
open('/tmp/claude-0/bm3/template3.html', 'w').write(t)
print(len(t))
