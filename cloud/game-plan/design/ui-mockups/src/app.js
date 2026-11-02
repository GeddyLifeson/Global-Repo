// Screens: each entry paints a region backdrop, optional canvas extras, then an HTML overlay at 1920x1080.
const RC={Common:'#8A857A',Forged:'#A87A4A',Rare:'#4F8FE6',Relic:'#9B7BD6',Shardborn:'#8FE3EE'};
DATA.rarities.forEach(r=>RC[r.name]=r.frame_color_hex);
const NOTCH={Common:0,Forged:1,Rare:2,Relic:3,Shardborn:4};
const ICO={'Straight Sword':'sword','Curved Sword':'curved','Greatsword':'great','Dagger':'dagger','Pistol':'pistol','Auto Rifle':'rifle','Scout Rifle':'rifle','Submachine Gun':'rifle','Shotgun':'rifle','Sniper Rifle':'rifle',Head:'helm',Chest:'chest',Hands:'hands',Legs:'legs'};
const fmt=n=>Number(n).toLocaleString('en-US');
const S=(k,v={})=>(DATA.s[k]||k).replace(/\{(\w+)\}/g,(m,x)=>v[x]??m);
const use=(id,st='')=>`<svg viewBox="0 0 64 64" style="${st}"><use href="#i-${id}"/></svg>`;
const el=(e,px=22)=>e?`<svg class="glyph" style="width:${px}px;height:${px}px" viewBox="0 0 24 24"><use href="#e-${e}"/></svg>`:'';
const tile=(it,o={})=>`<div class="tile ${o.sel?'sel':''} ${o.eq?'eq':''}" style="--rc:${RC[it.rarity]||'#3a352d'};${o.st||''}">${use(o.icon||ICO[it.weapon_class||it.slot]||'sword')}<div class="n">${'<i></i>'.repeat(NOTCH[it.rarity]||0)}</div>${o.lv?`<span class="lv">+${o.lv}</span>`:''}${o.q?`<span class="q">${o.q}</span>`:''}</div>`;
const prompts=(arr,st='right:80px;bottom:44px')=>`<div class="abs prompts" style="${st}">${arr.map(([b,t])=>`<span><span class="btn">${b}</span>${t}</span>`).join('')}</div>`;
const boss=n=>DATA.bosses.find(b=>b.Boss.startsWith(n));
const band=r=>DATA.bands.find(b=>b.Region===r);
const SHB=DATA.shardborn[0];

// ---------- HUD pieces
function vitals(o){const bar=(lab,c,c2,v,max,w,h,ghost)=>`<div style="display:flex;align-items:center;gap:14px;margin-top:8px">
  <span class="mono" style="width:70px;font-size:15px;letter-spacing:.12em;color:${c}">${lab}</span>
  <div class="bar" style="width:${w}px;height:${h}px;transform:skewX(-24deg)"><i style="width:${(ghost||0)*100}%;background:rgba(255,240,220,.55)"></i><i style="width:${v/max*100}%;background:linear-gradient(180deg,${c2},${c});box-shadow:0 0 14px ${c}"></i></div>
  <span class="mono shadowT" style="font-size:17px">${fmt(v)}<span style="color:#8a877e"> / ${fmt(max)}</span></span></div>`;
 return `<div class="abs" style="left:76px;bottom:70px">
  ${bar('WARD','#4f8fe6','#a8ccff',o.ward,o.wardMax,o.w*o.wardMax/o.hpMax,13)}
  ${bar('HEALTH','#d4483f','#ff9a8a',o.hp,o.hpMax,o.w,15,o.ghost)}
  ${bar('BREATH','#7cc46a','#c6f0b0',o.br,o.brMax,o.w*o.brMax/o.hpMax*1.6,8)}
  <div style="display:flex;align-items:center;gap:7px;margin:16px 0 0 84px">${Array.from({length:o.tmax},(_,i)=>`<div style="width:17px;height:30px;border-radius:5px 5px 8px 8px;border:2px solid #d4483f;background:${i<o.t?'linear-gradient(#ff8a7a,#8a1a14)':'transparent'};box-shadow:${i<o.t?'0 0 10px rgba(212,72,63,.6)':'none'}"></div>`).join('')}
  <span class="mono shadowT" style="margin-left:10px;font-size:16px;color:#cfc8b8">${S('STR_HUD_TONIC').toUpperCase()} ${o.t}/${o.tmax}</span></div></div>`}
function compass(marks,line){const W=820;let t='';['W','NW','N','NE','E'].forEach((d,i)=>t+=`<span class="abs mono" style="left:${i*W/4-12}px;top:6px;font-size:${d.length>1?15:20}px;color:${d==='N'?'#fff':'#9fd8de'}">${S('STR_HUD_COMPASS_'+d)}</span>`);
 for(let i=0;i<=40;i++)t+=`<i class="abs" style="left:${i*W/40}px;top:36px;width:2px;height:${i%5?6:12}px;background:rgba(143,227,238,${i%5?.35:.7})"></i>`;
 marks.forEach(m=>t+=`<div class="abs" style="left:${m.x*W-14}px;top:50px;text-align:center;width:28px">${m.svg}<div class="mono" style="font-size:12px;color:#cfc8b8;margin-top:2px">${m.d||''}</div></div>`);
 return `<div class="abs" style="left:${960-W/2}px;top:34px;width:${W}px;height:100px;filter:drop-shadow(0 0 6px rgba(0,0,0,.8))">${t}<div class="abs" style="left:0;right:0;top:38px;height:1px;background:linear-gradient(90deg,transparent,rgba(143,227,238,.6),transparent)"></div></div>
 ${line?`<div class="abs shadowT" style="left:0;right:0;top:132px;text-align:center;font:500 25px var(--body)"><span class="lensT mono" style="font-size:17px;letter-spacing:.2em;margin-right:14px">OSTRA</span>${line}</div>`:''}`}
const mk={anchor:`<svg width="26" height="26" viewBox="0 0 64 64"><use href="#i-anchor"/></svg>`,quest:`<svg width="22" height="26" viewBox="0 0 22 26"><path d="M2 0v26M2 2h16l-4 6 4 6H2" fill="#e8873a" stroke="#e8873a" stroke-width="3"/></svg>`,
 ghost:`<svg width="24" height="24" viewBox="0 0 64 64"><use href="#i-ember"/></svg>`,ally:`<svg width="20" height="20"><circle cx="10" cy="10" r="7" fill="#7cc46a"/></svg>`};
function abilities(o){const ring=(x,y,r,c,p,lab,ready)=>`<div class="abs" style="left:${x-r}px;top:${y-r}px;width:${r*2}px;height:${r*2}px;border-radius:50%;background:conic-gradient(${c} 0 ${p}%,rgba(255,255,255,.1) ${p}% 100%);-webkit-mask:radial-gradient(circle,transparent ${r-7}px,#000 ${r-6}px);mask:radial-gradient(circle,transparent ${r-7}px,#000 ${r-6}px);${ready?`box-shadow:0 0 18px ${c}`:''}"></div>
 <div class="abs" style="left:${x-r+8}px;top:${y-r+8}px;width:${r*2-16}px;height:${r*2-16}px;border-radius:50%;background:radial-gradient(circle at 40% 35%,rgba(255,255,255,.12),rgba(0,0,0,.55));display:grid;place-items:center">${el(o.el,r*.8)}</div>
 <div class="abs mono shadowT" style="left:${x-40}px;top:${y+r+4}px;width:80px;text-align:center;font-size:13px;letter-spacing:.12em;color:${ready?'#efe8d8':'#8a877e'}">${lab}</div>`;
 return ring(1110,950,34,o.c,100,'CAST',1)+ring(1196,950,34,o.c,o.strike,'STRIKE',0)+ring(1282,950,34,o.c,100,'STEP',1)+
 `<div class="abs" style="left:1336px;top:870px;width:150px;height:150px;border-radius:50%;background:conic-gradient(#8fe3ee 0 ${o.surge}%,rgba(143,227,238,.12) ${o.surge}% 100%);-webkit-mask:radial-gradient(circle,transparent 62px,#000 63px);mask:radial-gradient(circle,transparent 62px,#000 63px);filter:drop-shadow(0 0 10px #8fe3ee)"></div>
 <div class="abs" style="left:1361px;top:895px;width:100px;height:100px;border-radius:50%;background:radial-gradient(circle,rgba(143,227,238,.25),rgba(0,0,0,.6));display:grid;place-items:center;text-align:center"><div><div class="mono lensT" style="font-size:30px;font-weight:600">${o.surge}%</div><div class="mono" style="font-size:12px;letter-spacing:.2em;color:#9fd8de">${S('STR_HUD_SURGE').toUpperCase()}</div></div></div>
 <div class="abs" style="left:1080px;top:1022px;display:flex;align-items:center;gap:10px"><div style="width:34px;height:34px;transform:rotate(45deg);border:2px solid #e8e6e0;background:rgba(0,0,0,.5);display:grid;place-items:center"><span style="transform:rotate(-45deg);font:600 13px var(--mono)">${o.res}</span></div><span class="mono shadowT" style="font-size:14px;color:#cfc8b8">${o.resName}</span></div>`}
function weapon(o){return `<div class="abs shadowT" style="right:80px;bottom:62px;text-align:right">
 <div style="font:500 22px var(--display);letter-spacing:.04em">${el(o.el,20)} ${o.name}</div>
 <div class="mono" style="font-size:78px;line-height:1;font-weight:500;margin-top:4px">${o.mag}<span style="font-size:30px;color:#8a877e"> / ${o.res}</span></div>
 <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:8px">${['Common','Charged','Heavy'].map((a,i)=>`<span class="pill" style="color:${i==o.ammo?'#efe8d8':'#8a877e'};border-color:${i==o.ammo?'#efe8d8':'#3a3730'}">${S('STR_HUD_AMMO_'+a.toUpperCase()).toUpperCase()}</span>`).join('')}</div>
 <div class="mono" style="font-size:15px;color:#8a877e;margin-top:10px">${o.alt}</div></div>`}
function feed(lines,top=170){return `<div class="abs" style="right:80px;top:${top}px;text-align:right;display:grid;gap:8px">${lines.map(l=>`<div class="shadowT" style="font:500 19px var(--body);color:${l.c||'#e7e2d6'};opacity:${l.o||1}">${l.t}</div>`).join('')}</div>`}
function emberCounter(n,risk){return `<div class="abs shadowT" style="right:80px;top:56px;display:flex;align-items:center;gap:10px;font:500 32px var(--mono);color:#ffcf9a"><svg width="28" height="28" viewBox="0 0 64 64"><use href="#i-ember"/></svg>${fmt(n)}</div>${risk?`<div class="abs mono" style="right:80px;top:104px;font-size:14px;color:#e8873a;letter-spacing:.1em">${fmt(risk)} AT YOUR GHOST</div>`:''}`}
function plate(x,y,name,hp,ward,wc,badge,status){return `<div class="abs shadowT" style="left:${x-120}px;top:${y}px;width:240px;text-align:center">
 <div style="font:500 18px var(--body)">${badge?`<span class="mono" style="color:#e8873a;font-size:13px;margin-right:6px">${badge}</span>`:''}${name}</div>
 <div class="bar" style="height:9px;margin-top:6px;border-color:${wc}"><i style="width:${ward*100}%;background:${wc};box-shadow:0 0 12px ${wc}"></i></div>
 <div class="bar" style="height:6px;margin-top:3px"><i style="width:${hp*100}%;background:#d4483f"></i></div>
 ${status?`<div style="display:flex;gap:6px;justify-content:center;margin-top:6px">${status}</div>`:''}</div>`}
const statusChip=(e,lab,p)=>`<div style="display:flex;align-items:center;gap:5px;background:rgba(0,0,0,.6);padding:2px 8px 2px 4px;border:1px solid rgba(255,255,255,.15)">${el(e,18)}<div class="bar" style="width:60px;height:6px;border:0"><i style="width:${p}%;background:#b9a27a"></i></div><span class="mono" style="font-size:12px">${lab}</span></div>`;

// ---------- canvas extras
function rifleFP(ctx,W,H){ctx.save();ctx.translate(W*.66,H*1.02);ctx.rotate(-.2);
 const g=ctx.createLinearGradient(0,-260,0,0);g.addColorStop(0,'#4a4c52');g.addColorStop(.4,'#26272b');g.addColorStop(1,'#0e0e10');ctx.fillStyle=g;
 ctx.beginPath();ctx.moveTo(60,-150);ctx.lineTo(560,-260);ctx.lineTo(620,-230);ctx.lineTo(600,-190);ctx.lineTo(380,-130);ctx.lineTo(360,-40);ctx.lineTo(260,0);ctx.lineTo(200,-80);ctx.lineTo(40,-40);ctx.closePath();ctx.fill();
 ctx.fillStyle='#17181b';ctx.fillRect(150,-210,260,40);ctx.fillStyle='#8fe3ee';ctx.shadowColor='#8fe3ee';ctx.shadowBlur=20;ctx.fillRect(300,-180,110,8);ctx.fillRect(470,-232,40,6);ctx.shadowBlur=0;
 ctx.strokeStyle='rgba(255,255,255,.18)';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(60,-150);ctx.lineTo(560,-260);ctx.stroke();
 ctx.fillStyle='#3a2a20';ctx.beginPath();ctx.ellipse(280,-60,90,60,-.3,0,7);ctx.fill();ctx.fillStyle='#5a4030';ctx.beginPath();ctx.ellipse(270,-80,60,30,-.3,0,7);ctx.fill();ctx.restore();}
function flames(ctx,W,H,R,n,y0){ctx.save();ctx.globalCompositeOperation='screen';for(let i=0;i<n;i++){const x=R()*W,y=y0+R()*(H-y0),h=20+R()*90;const g=ctx.createLinearGradient(0,y,0,y-h);g.addColorStop(0,'rgba(255,140,40,.7)');g.addColorStop(1,'rgba(255,60,10,0)');ctx.fillStyle=g;ctx.beginPath();ctx.moveTo(x-8,y);ctx.quadraticCurveTo(x-4,y-h*.6,x,y-h);ctx.quadraticCurveTo(x+4,y-h*.6,x+8,y);ctx.fill();}ctx.restore();}
function bust(ctx,x,y,s){ctx.save();ctx.translate(x,y);ctx.scale(s,s);
 const g=ctx.createLinearGradient(-200,0,200,0);g.addColorStop(0,'#2a3438');g.addColorStop(.5,'#1a1c20');g.addColorStop(1,'#3a2a20');
 ctx.fillStyle=g;ctx.beginPath();ctx.moveTo(-260,300);ctx.quadraticCurveTo(-250,90,-150,60);ctx.lineTo(-60,30);ctx.lineTo(60,30);ctx.lineTo(150,60);ctx.quadraticCurveTo(250,90,260,300);ctx.fill();
 // pauldrons of hull plate
 ctx.fillStyle='#4a4e54';ctx.beginPath();ctx.ellipse(-170,90,110,60,-.35,0,7);ctx.fill();ctx.beginPath();ctx.ellipse(170,90,110,60,.35,0,7);ctx.fill();
 ctx.fillStyle='#e8e6e0';ctx.font='600 22px IBM Plex Mono';ctx.save();ctx.rotate(-.35);ctx.fillText('MRD-07',-250,20);ctx.restore();
 ctx.strokeStyle='rgba(143,227,238,.8)';ctx.lineWidth=4;ctx.shadowColor='#8fe3ee';ctx.shadowBlur=18;ctx.beginPath();ctx.ellipse(-170,90,110,60,-.35,Math.PI*1.05,Math.PI*1.6);ctx.stroke();ctx.shadowBlur=0;
 ctx.fillStyle='#6a2a20';ctx.fillRect(-40,40,80,260);ctx.fillStyle='#e8873a';ctx.fillRect(-6,60,12,60);
 // neck/head
 const sk=ctx.createLinearGradient(-60,0,60,0);sk.addColorStop(0,'#6a8890');sk.addColorStop(.35,'#b08a70');sk.addColorStop(1,'#d8a070');
 ctx.fillStyle=sk;ctx.fillRect(-30,-20,60,60);ctx.beginPath();ctx.ellipse(0,-90,62,82,0,0,7);ctx.fill();
 ctx.fillStyle='#1a1210';ctx.beginPath();ctx.moveTo(-66,-80);ctx.quadraticCurveTo(-70,-190,0,-180);ctx.quadraticCurveTo(70,-190,66,-80);ctx.quadraticCurveTo(60,-140,10,-150);ctx.quadraticCurveTo(-40,-140,-50,-60);ctx.lineTo(-70,10);ctx.closePath();ctx.fill();
 ctx.fillStyle='#2a1a14';ctx.beginPath();ctx.ellipse(-22,-92,10,5,0,0,7);ctx.ellipse(22,-92,10,5,0,0,7);ctx.fill();
 ctx.strokeStyle='rgba(120,60,50,.8)';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(-14,-46);ctx.quadraticCurveTo(0,-40,14,-46);ctx.stroke();
 ctx.strokeStyle='rgba(255,255,255,.35)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(30,-120);ctx.lineTo(44,-70);ctx.stroke(); // scar
 // form shading: cool shadow side, warm key, rim
 ctx.save();ctx.beginPath();ctx.ellipse(0,-90,62,82,0,0,7);ctx.clip();let sh=ctx.createLinearGradient(-62,0,62,0);sh.addColorStop(0,'rgba(20,40,60,.55)');sh.addColorStop(.45,'rgba(20,30,40,0)');sh.addColorStop(1,'rgba(255,170,90,.18)');ctx.fillStyle=sh;ctx.fillRect(-70,-180,140,180);
 sh=ctx.createLinearGradient(0,-30,0,-10);sh.addColorStop(0,'rgba(0,0,0,0)');sh.addColorStop(1,'rgba(0,0,0,.35)');ctx.fillStyle=sh;ctx.fillRect(-70,-40,140,40);ctx.restore();
 ctx.strokeStyle='rgba(143,227,238,.7)';ctx.lineWidth=3;ctx.shadowColor='#8fe3ee';ctx.shadowBlur=12;ctx.beginPath();ctx.ellipse(0,-90,62,82,0,Math.PI*.7,Math.PI*1.25);ctx.stroke();ctx.shadowBlur=0;
 for(let k=0;k<3;k++){[-1,1].forEach(sg=>{const pg=ctx.createLinearGradient(0,40+k*40,0,90+k*40);pg.addColorStop(0,'#6a7078');pg.addColorStop(1,'#24272c');ctx.fillStyle=pg;ctx.beginPath();ctx.ellipse(sg*(150+k*14),70+k*36,96-k*8,34,sg*.35,0,7);ctx.fill();ctx.strokeStyle='rgba(255,220,170,.25)';ctx.lineWidth=2;ctx.stroke()})}
 ctx.restore();}
function anchorCrystal(ctx,x,y,s){ctx.save();ctx.globalCompositeOperation='screen';SF.glow(ctx,x,y-s*.6,s*2.4,'#8fe3ee',.35);
 const g=ctx.createLinearGradient(0,y-s*1.4,0,y);g.addColorStop(0,'rgba(143,227,238,.0)');g.addColorStop(1,'rgba(143,227,238,.25)');ctx.fillStyle=g;ctx.fillRect(x-14,0,28,y);ctx.restore();
 const c=ctx.createLinearGradient(x-s*.3,0,x+s*.3,0);c.addColorStop(0,'#2a8a98');c.addColorStop(.5,'#e8fdff');c.addColorStop(1,'#1a5a68');
 ctx.fillStyle=c;ctx.shadowColor='#8fe3ee';ctx.shadowBlur=60;ctx.beginPath();ctx.moveTo(x,y-s*1.3);ctx.lineTo(x+s*.28,y-s*.5);ctx.lineTo(x+s*.12,y);ctx.lineTo(x-s*.12,y);ctx.lineTo(x-s*.28,y-s*.5);ctx.fill();ctx.shadowBlur=0;
 ctx.fillStyle='#1a1d20';ctx.fillRect(x-s*.5,y,s,s*.12);ctx.fillStyle='#2a2e32';ctx.fillRect(x-s*.62,y+s*.12,s*1.24,s*.1);}
function mapPaint(ctx,W,H){const w=800,h=450,c=document.createElement('canvas');c.width=w;c.height=h;const g=c.getContext('2d'),d=g.createImageData(w,h);
 const R=SF.rng(5),perm=[];for(let i=0;i<4096;i++)perm.push(R());const n2=(x,y)=>{const xi=Math.floor(x),yi=Math.floor(y),xf=x-xi,yf=y-yi,u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf),
  h=(a,b)=>perm[((a*73856093)^(b*19349663))&4095];return (h(xi,yi)*(1-u)+h(xi+1,yi)*u)*(1-v)+(h(xi,yi+1)*(1-u)+h(xi+1,yi+1)*u)*v};
 const fb=(x,y)=>{let s=0,a=.5,f=1;for(let i=0;i<6;i++){s+=a*n2(x*f,y*f);a*=.5;f*=2}return s};
 const seeds=[[.26,.66,'#5a3a2a','#b88a5a',1],[.22,.32,'#2f4f50','#9cbcb6',1],[.5,.5,'#4a2a20','#8a5a3a',1],[.78,.6,'#6a5a9a','#c7a8e0',0],[.52,.18,'#5a7898','#e8f0f6',0],[.8,.24,'#3a3644','#8a8496',0]];
 const H2=[];for(let y=0;y<h;y++)for(let x=0;x<w;x++){const nx=x/w,ny=y/h;let e=fb(nx*6,ny*6);const dx=(nx-.5)*1.15,dy=(ny-.46)*1.6;e=e-Math.max(0,Math.hypot(dx,dy)-.42)*1.6;H2.push(e)}
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x,e=H2[i],nx=x/w,ny=y/h;let best=9,b2=9,k=0;seeds.forEach((s,j)=>{const dd=Math.hypot(nx-s[0]+(fb(nx*9,ny*9)-.5)*.08,(ny-s[1])*.62);if(dd<best){b2=best;best=dd;k=j}else if(dd<b2)b2=dd});
  const sh=Math.max(-.5,Math.min(.6,(e-(H2[i-w-1]??e))*28));let col;
  if(e<.42){const t=Math.max(0,(e-.2)/.22);col=[12+t*20,24+t*36,30+t*40]}
  else{const s=seeds[k],A=SF.P?hex2(s[2]):0,B=hex2(s[3]),t=Math.min(1,(e-.42)/.35);col=A.map((v,j)=>v+(B[j]-v)*t);col=col.map(v=>v*(1+sh));if(!s[4]){const gr=(col[0]+col[1]+col[2])/3*.35;col=[gr*.9+10,gr*.85+8,gr*.8+6]}
   if(b2-best<.004)col=col.map(v=>v*.6+90)}
  d.data.set([col[0],col[1],col[2],255],i*4)}
 g.putImageData(d,0,0);ctx.imageSmoothingQuality='high';ctx.drawImage(c,0,0,W,H);
 ctx.save();ctx.globalAlpha=.08;ctx.strokeStyle='#e7e2d6';for(let x=0;x<W;x+=120){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}for(let y=0;y<H;y+=120){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}ctx.restore();
 // fog over unrevealed
 ctx.save();[[.78,.6],[.52,.18],[.8,.24]].forEach(([x,y])=>{const r=ctx.createRadialGradient(x*W,y*H,0,x*W,y*H,W*.2);r.addColorStop(0,'rgba(10,10,12,.82)');r.addColorStop(1,'rgba(10,10,12,0)');ctx.fillStyle=r;ctx.fillRect(0,0,W,H)});ctx.restore();
 const v=ctx.createRadialGradient(W/2,H/2,H*.4,W/2,H/2,W*.7);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(1,'rgba(0,0,0,.7)');ctx.fillStyle=v;ctx.fillRect(0,0,W,H);}
function hex2(h){h=h.slice(1);return[0,2,4].map(i=>parseInt(h.slice(i,i+2),16))}

// ---------- screens
const SHOTS=[];const add=(o)=>SHOTS.push(o);
const ember=12480;

add({sec:'Screens',id:'title',name:'Title and main menu',src:'ui/strings.csv (STR_TITLE_*)',region:'cinderreach',
 draw:(c,W,H)=>{SF.figure(c,'knight',W*.6,H*1.02,H*.46,'#ffb060');const v=c.createLinearGradient(0,0,W*.55,0);v.addColorStop(0,'rgba(0,0,0,.85)');v.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=v;c.fillRect(0,0,W,H)},
 html:()=>`<div class="abs" style="left:120px;top:150px">
  <div style="font:600 128px/1 var(--display);letter-spacing:.06em;background:linear-gradient(180deg,#fff8ea 10%,#d8c8a8 55%,#7a6a52);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 6px 30px rgba(0,0,0,.8))">SHARD<span style="display:inline-block;width:46px;height:110px;vertical-align:-6px;margin:0 4px;background:linear-gradient(180deg,#e8fdff,#3fb0c0);clip-path:polygon(50% 0,100% 30%,72% 100%,28% 100%,0 30%);filter:drop-shadow(0 0 30px #8fe3ee)"></span>FALL</div>
  <div class="mono" style="letter-spacing:.5em;color:#cfc8b8;font-size:17px;margin:14px 0 0 8px">THE FALL OF THE MERIDIAN</div></div>
 <div class="abs" style="left:120px;top:440px;display:grid;gap:10px;font:500 30px var(--display);letter-spacing:.06em">
  <div style="display:flex;align-items:center;gap:18px;color:#fff"><i style="width:14px;height:14px;transform:rotate(45deg);background:#8fe3ee;box-shadow:0 0 14px #8fe3ee"></i>${S('STR_TITLE_CONTINUE')}<span style="height:2px;width:220px;background:linear-gradient(90deg,#8fe3ee,transparent)"></span></div>
  <div class="mono" style="font-size:17px;color:#9fd8de;margin:-4px 0 8px 32px;letter-spacing:.04em">Aren Vos · Level 27 · Spinegate Bridge, Spine Keep · 41:12:06</div>
  ${['STR_TITLE_NEW','STR_TITLE_LOAD','STR_TITLE_COOP','STR_TITLE_OPTIONS','STR_TITLE_CREDITS','STR_TITLE_QUIT'].map(k=>`<div style="color:#bdb7aa;margin-left:32px">${S(k)}</div>`).join('')}</div>
 <div class="abs mono" style="right:80px;bottom:44px;text-align:right;color:#8a877e;font-size:15px;line-height:1.8"><span style="color:#7cc46a">● ${S('STR_TITLE_ONLINE')}</span><br>${S('STR_TITLE_VERSION',{VAR_build:'0.9.412 slice'})}<br>${S('STR_TITLE_COPYRIGHT',{VAR_year:'2026'})}</div>
 ${prompts([['A','Select'],['B','Back']],'left:120px;bottom:44px')}`});

add({sec:'Screens',id:'hud',name:'Combat HUD',src:'actors/player_base_stats.csv, items/weapons_firearm.csv, actors/element_matrix.csv, ui/strings.csv (STR_HUD_*)',region:'saltmere',
 draw:(c,W,H,R)=>{SF.figure(c,'shambler',W*.36,H*.78,H*.2,'#8fe3ee');SF.figure(c,'shambler',W*.31,H*.8,H*.17,'#8fe3ee');SF.figure(c,'shambler',W*.74,H*.77,H*.19,'#8fe3ee');
  SF.figure(c,'riot',W*.555,H*.78,H*.34,'#b48cff');
  c.save();c.globalCompositeOperation='screen';c.strokeStyle='rgba(255,220,160,.8)';c.lineWidth=3;c.shadowColor='#ffb060';c.shadowBlur=12;[[0,0],[14,-8],[-10,6]].forEach(([a,b])=>{c.beginPath();c.moveTo(W*.7,H*.84);c.lineTo(W*.51+a,H*.6+b);c.stroke()});
  for(let i=0;i<30;i++){c.strokeStyle='rgba(200,170,255,.9)';c.beginPath();const x=W*.505,y=H*.6;const a=R()*6.3,l=10+R()*40;c.moveTo(x,y);c.lineTo(x+Math.cos(a)*l,y+Math.sin(a)*l);c.stroke()}SF.glow(c,W*.505,H*.6,50,'#b48cff',.8);c.restore();rifleFP(c,W,H)},
 html:()=>`${compass([{x:.18,svg:mk.anchor,d:'210m'},{x:.62,svg:mk.quest,d:'480m'},{x:.83,svg:mk.ghost,d:'95m'}],'Its Ward is Storm. Hit it with Iron.')}
 ${emberCounter(ember)}${feed([{t:'Firearms 34 → 35',c:'#8fe3ee'},{t:S('STR_HUD_LOOT_LINE',{ITM_name:'Hull Scrap',VAR_n:3})},{t:S('STR_HUD_LOOT_EMBER',{VAR_n:58}),c:'#ffcf9a',o:.8},{t:'Shard Dust x1',o:.6}])}
 ${plate(1066,422,'Remnant Riot Frame',.92,.36,'#b48cff','LEADER',statusChip('Iron','SHATTER',64))}${plate(690,690,'Shardsick Shambler',.55,0,'#4f8fe6')}
 <div class="abs mono" style="left:930px;top:560px;font-size:34px;font-weight:600;color:#d8c4ff;text-shadow:0 0 12px #b48cff,0 2px 4px #000">212</div><div class="abs mono" style="left:1010px;top:520px;font-size:26px;color:#d8c4ff;opacity:.7;text-shadow:0 2px 4px #000">198</div>
 <div class="abs" style="left:939px;top:519px;width:42px;height:42px;border:2px solid rgba(143,227,238,.9);border-radius:50%"></div><svg class="abs" style="left:930px;top:510px" width="60" height="60"><path d="M30 0v14M30 46v14M0 30h14M46 30h14" stroke="#8fe3ee" stroke-width="2"/><path d="M14 14l8 8M46 14l-8 8M14 46l8-8M46 46l-8-8" stroke="#fff" stroke-width="3"/></svg>
 <svg class="abs" style="left:0;top:0" width="1920" height="1080"><path d="M300 260 A700 700 0 0 0 220 560" fill="none" stroke="rgba(212,72,63,.7)" stroke-width="12" filter="drop-shadow(0 0 10px #d4483f)"/></svg>
 ${vitals({ward:212,wardMax:342,hp:614,hpMax:688,br:142,brMax:196,w:430,t:5,tmax:8,ghost:.95})}
 ${abilities({el:'Iron',c:'#b9a27a',strike:62,surge:74,res:'II',resName:'Point-Defense Lance · 38s'})}
 ${weapon({el:'',name:'Remnant Repeater',mag:27,res:288,ammo:0,alt:'2nd  Hullplate Longsword<br>side  Hull Knight Service Pistol'})}`});

const vael=boss('Vael');
add({sec:'Screens',id:'boss',name:'Boss fight and boss bar',src:'actors/bosses.csv (ACT_BOSS_VAEL), items/shardborn.csv',region:'cinderreach',
 draw:(c,W,H,R)=>{c.fillStyle='rgba(20,10,8,.35)';c.fillRect(0,0,W,H);SF.figure(c,'boss',W*.56,H*.74,H*.5,'#ffb060');flames(c,W,H,R,160,H*.78);SF.figure(c,'knight',W*.38,H*1.04,H*.42,'#ffb060',{blade:'#ff8a3a'});
  c.save();c.globalCompositeOperation='screen';SF.glow(c,W*.705,H*.06,60,'#ffffff',.9);c.strokeStyle='#fff';c.lineWidth=3;c.beginPath();c.moveTo(W*.705-50,H*.06);c.lineTo(W*.705+50,H*.06);c.moveTo(W*.705,H*.06-50);c.lineTo(W*.705,H*.06+50);c.stroke();c.restore()},
 html:()=>{const hp=+vael['HP (solo)'],cur=Math.round(hp*.52),th=vael['Phase HP thresholds %'].split(';').map(Number);return `
 <div class="abs" style="left:360px;top:60px;width:1200px">
  <div style="display:flex;align-items:baseline;gap:18px" class="shadowT"><span style="font:500 38px var(--display);letter-spacing:.06em">${vael.Boss}</span><span class="mono" style="font-size:16px;color:#cfc8b8;letter-spacing:.14em">SHARD-BEARER OF ${vael['Region name'].toUpperCase()}</span><span class="mono" style="margin-left:auto;font-size:16px;color:#ffb060">${S('STR_HUD_BOSS_PHASE',{VAR_n:2}).toUpperCase()} / ${vael.Phases}</span></div>
  <div class="bar" style="height:20px;margin-top:10px;border-color:rgba(255,180,96,.5);background:rgba(0,0,0,.7)"><i style="width:58%;background:rgba(255,230,200,.5)"></i><i style="width:52%;background:linear-gradient(180deg,#ff8a7a,#a8241c 60%,#6a1410);box-shadow:0 0 18px #d4483f"></i>
   ${th.map(t=>`<i style="left:${t}%;width:3px;background:#fff;box-shadow:0 0 8px #fff"></i>`).join('')}</div>
  <div style="display:flex;justify-content:space-between;margin-top:6px" class="mono shadowT"><span style="font-size:15px;color:#cfc8b8">${fmt(cur)} / ${fmt(hp)} · no Ward</span><span style="font-size:15px;color:#ffb060">STANCE</span></div>
  <div class="bar" style="height:6px;margin-left:auto;width:300px;margin-top:4px"><i style="width:78%;background:linear-gradient(90deg,#e8873a,#ffd090)"></i></div></div>
 <div class="abs" style="left:1050px;top:236px;width:76px;height:76px"><svg width="76" height="76"><circle cx="38" cy="38" r="20" fill="none" stroke="#fff" stroke-width="2"/><path d="M38 4v14M38 58v14M4 38h14M58 38h14" stroke="#fff" stroke-width="3"/></svg></div>
 <div class="abs mono shadowT" style="left:1140px;top:252px;font-size:15px;color:#ffd090">CROWN SHARD<br><span style="color:#cfc8b8">${vael['Weak points / parts'].replace('Crown Shard ','')}</span></div>
 <div class="abs shadowT" style="left:1255px;top:150px;font:600 15px var(--mono);color:#fff;letter-spacing:.14em">UNBLOCKABLE</div>
 ${vitals({ward:0,wardMax:342,hp:401,hpMax:688,br:88,brMax:196,w:430,t:3,tmax:8,ghost:.66})}
 <div class="abs mono pulse" style="left:150px;bottom:236px;font-size:15px;letter-spacing:.14em;color:#ff6a5a;text-shadow:0 0 10px #d4483f">${S('STR_HUD_WARD_BROKEN')}</div>
 ${abilities({el:'Ember',c:'#f06a2a',strike:100,surge:100,res:'I',resName:'Ember Rain · ready'})}
 <div class="abs shadowT" style="right:80px;bottom:62px;text-align:right"><div style="font:500 24px var(--display)">${el('Ember',20)} ${SHB.name}</div><div class="mono" style="font-size:15px;color:#8fe3ee;margin-top:6px">MEMORY OF FIRE · 2 / 3 HITS</div><div class="mono" style="font-size:15px;color:#8a877e;margin-top:6px">side  Rivet Pistol 14/96</div></div>
 <div class="abs" style="left:1336px;top:870px;width:150px;height:150px" ><div class="abs mono lensT pulse" style="left:-30px;top:-30px;width:210px;text-align:center;font-size:15px;letter-spacing:.2em">${S('STR_HUD_SURGE_READY')}</div></div>`}});

const loot=[['Common',DATA.melee.find(m=>m.rarity==='Common')],['Forged',DATA.melee.find(m=>m.rarity==='Forged')],['Rare',DATA.melee.find(m=>m.name==='Choir-Glass Edge')],['Relic',DATA.melee.find(m=>m.name==='Starmetal Spatha')]];
add({sec:'Screens',id:'loot',name:'Loot popups by rarity',src:'items/rarities.csv, items/weapons_melee.csv, items/shardborn.csv (ITM_SHB_W01)',region:'thornwood',
 draw:(c,W,H)=>{c.fillStyle='rgba(0,0,0,.45)';c.fillRect(0,0,W,H);c.save();c.globalCompositeOperation='screen';const g=c.createLinearGradient(W/2-160,0,W/2+160,0);g.addColorStop(0,'rgba(143,227,238,0)');g.addColorStop(.5,'rgba(143,227,238,.35)');g.addColorStop(1,'rgba(143,227,238,0)');c.fillStyle=g;c.fillRect(W/2-160,0,320,H*.62);SF.glow(c,W/2,H*.4,380,'#8fe3ee',.35);
  for(let i=0;i<18;i++){const a=i/18*6.28;c.strokeStyle='rgba(143,227,238,.18)';c.lineWidth=3;c.beginPath();c.moveTo(W/2,H*.4);c.lineTo(W/2+Math.cos(a)*700,H*.4+Math.sin(a)*700);c.stroke()}c.restore()},
 html:()=>`<div class="abs" style="left:0;right:0;top:120px;text-align:center">
  <div class="mono lensT" style="font-size:20px;letter-spacing:.5em">SHARDBORN</div>
  <div style="display:inline-block;margin-top:26px">${tile({rarity:'Shardborn',weapon_class:'Straight Sword'},{st:'width:240px;height:240px;box-shadow:0 0 80px rgba(143,227,238,.6),inset 0 0 30px rgba(0,0,0,.5)'}).replace('inset:14px;width:80px;height:80px','')}</div>
  <div style="font:500 64px var(--display);letter-spacing:.04em;margin-top:24px;text-shadow:0 0 30px rgba(143,227,238,.5)">${SHB.name}</div>
  <div class="mono" style="font-size:17px;color:#cfc8b8;letter-spacing:.2em;margin-top:6px">${SHB.slot_or_class.toUpperCase()} · ${el(SHB.element,18)} ${SHB.element.toUpperCase()}</div>
  <div style="width:760px;margin:22px auto 0;padding:18px 26px;border-top:1px solid rgba(143,227,238,.4);border-bottom:1px solid rgba(143,227,238,.4);background:rgba(8,20,22,.6)">
   <div style="font:500 24px var(--display);color:#8fe3ee">${SHB.perk_name}</div><div style="font:400 20px/1.5 var(--body);color:#e7e2d6;margin-top:6px">${SHB.perk_effect}</div></div>
  <div class="mono" style="font-size:14px;color:#8a877e;margin-top:14px;letter-spacing:.1em">ONLY ONE SHARDBORN WEAPON MAY BE EQUIPPED · FIRST KILL OF ${vael.Boss.toUpperCase()}</div></div>
 <div class="abs" style="right:70px;top:600px;display:grid;gap:10px;width:470px">${loot.map(([r,it])=>`<div style="display:flex;align-items:center;gap:14px;padding:8px 14px 8px 8px;background:linear-gradient(90deg,color-mix(in srgb,${RC[r]} 30%,transparent),rgba(0,0,0,.6));border-left:4px solid ${RC[r]}">
  ${tile(it,{st:'width:64px;height:64px'}).replace('inset:14px;width:80px;height:80px','inset:8px;width:44px;height:44px')}<div style="min-width:0"><div style="font:500 21px var(--display);color:#f2ecdf">${it.name}</div><div class="mono" style="font-size:13px;letter-spacing:.12em;color:${RC[r]}">${r.toUpperCase()} · ${it.weapon_class.toUpperCase()}</div></div>
  <div class="mono" style="margin-left:auto;font-size:18px">${+it.phys_ar+ +(it.element_ar||0)}<span style="font-size:12px;color:#8a877e"> AR</span></div></div>`).join('')}</div>
 <div class="abs" style="left:70px;top:610px;display:grid;gap:12px">${DATA.rarities.map(r=>`<div style="display:flex;align-items:center;gap:14px">${tile({rarity:r.name,weapon_class:'Straight Sword'},{st:'width:54px;height:54px;border-width:2px'}).replace('inset:14px;width:80px;height:80px','inset:7px;width:36px;height:36px')}<span style="font:500 20px var(--display);width:120px">${r.name}</span><span class="mono" style="font-size:14px;color:#8a877e">${r.frame_color_hex} · ${NOTCH[r.name]} notch</span></div>`).join('')}</div>
 ${prompts([['A','Equip now'],['Y','Inspect'],['B','Dismiss']])}`});

const inv=[...DATA.melee.filter(m=>['Relic','Rare'].includes(m.rarity)).slice(0,10),...DATA.melee.filter(m=>m.rarity==='Forged').slice(0,8),...DATA.melee.filter(m=>m.rarity==='Common').slice(0,9)];
const cmp=DATA.melee.find(m=>m.name==="Meridian Officer's Sword");
add({sec:'Screens',id:'inv',name:'Inventory and gear',src:'items/weapons_melee.csv, items/shardborn.csv, actors/player_base_stats.csv',region:'lantern',
 draw:(c,W,H)=>{c.fillStyle='rgba(6,6,8,.82)';c.fillRect(0,0,W,H)},
 html:()=>{const cells=[tile({rarity:'Shardborn',weapon_class:'Straight Sword'},{sel:1,lv:7}),...inv.map((m,i)=>tile(m,{lv:[3,5,0,2,8,1,0,4,6,0][i%10]||'',eq:m===cmp}))].slice(0,30);
 const ar=Math.round(118*1.12),elar=64,row=(k,v,d)=>`<div class="stat"><span>${k}</span><span>${v}</span><span class="${d>0?'up':d<0?'dn':'eq0'}">${d>0?'+'+d:d<0?d:'±0'}</span></div>`;
 return `<div class="ledgerBg"></div><div class="ledgerHead"><h2>Ledger</h2><div class="tabs"><span class="bump">LB</span><span class="on">INVENTORY</span><span>EQUIPMENT</span><span>SKILLS</span><span>MAP</span><span>JOURNAL</span><span>CODEX</span><span class="bump">RB</span></div>
  <div class="cur"><span style="color:#ffcf9a">${use('ember','width:22px;height:22px;vertical-align:-3px')} ${fmt(ember)}</span><span style="color:#cfc8b8">CARRY 118.4 / 210</span></div></div>
 <div class="abs" style="left:80px;top:170px;width:270px;display:grid;gap:4px;font:500 22px var(--body)">${[['All',412],['Melee',48],['Firearms',22],['Foci',9],['Armor',96],['Tonics & Brews',31],['Materials',187],['Lore',19]].map(([n,c],i)=>`<div style="display:flex;justify-content:space-between;padding:10px 16px;${i==1?'background:linear-gradient(90deg,rgba(143,227,238,.18),transparent);border-left:3px solid #8fe3ee;color:#fff':'color:#9a968c'}"><span>${n}</span><span class="mono" style="font-size:17px">${c}</span></div>`).join('')}
  <div class="rule"></div><div class="lbl">Sort</div><div style="color:#cfc8b8;margin-top:6px">Rarity, then AR</div><div class="rule"></div>
  <div class="lbl">Equip load</div><div class="bar" style="margin-top:10px;height:12px"><i style="width:61%;background:linear-gradient(90deg,#7cc46a,#c6f0b0)"></i><i style="left:30%;width:2px;background:#fff"></i><i style="left:70%;width:2px;background:#fff"></i></div>
  <div class="mono" style="font-size:16px;margin-top:8px;color:#cfc8b8">61.0% · MEDIUM ROLL</div></div>
 <div class="abs" style="left:390px;top:170px;display:grid;grid-template-columns:repeat(6,112px);gap:12px">${cells.join('')}</div>
 <div class="panel" style="left:1180px;top:160px;width:660px;height:800px;padding:34px 38px;box-sizing:border-box">
  <div class="mono lensT" style="font-size:15px;letter-spacing:.2em">SHARDBORN · STRAIGHT SWORD · +7</div>
  <div style="font:500 50px/1.1 var(--display);margin-top:8px">${SHB.name}</div>
  <div style="display:flex;gap:10px;margin-top:12px">${el('Ember',26)}<span style="font:500 18px var(--body);color:#f0a070">Ember · Burn</span><span class="mono" style="margin-left:auto;color:#8a877e">WT 4.0</span></div>
  <div class="rule"></div>
  <div class="lbl" style="display:flex;justify-content:space-between"><span>Attack rating</span><span>vs ${cmp.name}</span></div>
  ${row('Physical (Slash)',ar,ar-cmp.phys_ar)}${row('Ember',elar,elar)}${row('Total AR',ar+elar,ar+elar-cmp.phys_ar)}${row('Breath / light',14,-(+cmp.breath_light-14))}${row('Poise dmg / light',12,12-cmp.poise_light)}
  <div class="lbl" style="margin-top:22px">Scaling</div><div style="margin-top:10px;display:flex;align-items:center;gap:6px;font:500 16px var(--mono);color:#9a968c"><span class="grade">D</span>MIG <span class="grade" style="color:#8fe3ee;border-color:#8fe3ee">B</span>FIN <span class="grade">C</span>LOR <span class="grade">E</span>GRT</div>
  <div class="rule"></div>
  <div style="font:500 22px var(--display);color:#8fe3ee">${SHB.perk_name}</div><div style="font:400 18px/1.5 var(--body);color:#d8d2c4;margin-top:4px">${SHB.perk_effect}</div>
  <div class="lbl" style="margin-top:20px">Perk columns</div><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:10px">${[['Edge','Honed Hull-Steel'],['Grip','Cable Wrap'],['Trait 1','Kindling'],['Trait 2','Afterburn']].map(([a,b])=>`<div style="border:1px solid #3a372f;background:#1a1916;padding:10px"><div class="mono" style="font-size:12px;color:#8a877e;letter-spacing:.1em">${a.toUpperCase()}</div><div style="font-size:16px;margin-top:4px">${b}</div></div>`).join('')}</div>
  <div style="font:italic 19px/1.5 var(--serif);color:#9a968c;margin-top:22px">"Cut from the cryo bay door. Ostra says she remembers it opening."</div></div>
 ${prompts([['A','Equip'],['Y','Upgrade'],['X','Compare'],['B','Back']])}`}});

const skl=DATA.skills,perks=DATA.perks,myRank=52;
add({sec:'Screens',id:'skills',name:'Skills and perk tree',src:'actors/skills.csv, actors/perks.csv (SKL_BLADES)',region:'rimefall',
 draw:(c,W,H)=>{c.fillStyle='rgba(6,8,12,.84)';c.fillRect(0,0,W,H)},
 html:()=>{const X=r=>560+(+r)/100*1180;const lanes={};let pos={};perks.forEach((p,i)=>{const k=p.rank;lanes[k]=(lanes[k]||0)+1;pos[p.id]={x:X(p.rank),y:0,n:lanes[k]}});
  Object.values(pos).forEach(p=>{const tot=perks.filter(q=>X(q.rank)===p.x).length;p.y=560+(p.n-(tot+1)/2)*170});
  const state=p=>+p.rank<=25?'own':+p.rank<=myRank?'ready':'lock',col={own:'#8fe3ee',ready:'#e8873a',lock:'#4a4740'};
  let lines='';perks.forEach(p=>p.req.split(';').map(s=>s.trim()).filter(Boolean).forEach(r=>{if(pos[r])lines+=`<path d="M${pos[r].x} ${pos[r].y} C${(pos[r].x+pos[p.id].x)/2} ${pos[r].y},${(pos[r].x+pos[p.id].x)/2} ${pos[p.id].y},${pos[p.id].x} ${pos[p.id].y}" stroke="${state(p)==='lock'?'#3a372f':state(p)==='own'?'#8fe3ee':'#a8703a'}" stroke-width="3" fill="none" ${state(p)==='own'?'filter="drop-shadow(0 0 6px #8fe3ee)"':''}/>`}));
  const sel=perks.find(p=>p.name==='Counterflow')||perks[7];
  return `<div class="ledgerBg"></div><div class="ledgerHead"><h2>Skills</h2><div class="tabs"><span class="bump">LB</span><span>INVENTORY</span><span>EQUIPMENT</span><span class="on">SKILLS</span><span>MAP</span><span>JOURNAL</span><span class="bump">RB</span></div><div class="cur"><span>LEVEL 27</span><span class="lensT">2 PERK POINTS</span></div></div>
  <div class="abs" style="left:80px;top:160px;width:360px">${['Steel','Weave','Salvage'].map(g=>`<div class="lbl" style="margin:14px 0 6px">${g}</div>`+skl.filter(s=>s.Group===g).map(s=>{const lv=s.Skill==='Blades'?myRank:({Firearms:35,Guard:31,'Heavy Arms':22,'Ember Rite':18,Warding:26,Speech:40,Engineering:12}[s.Skill]||5+(s.Skill.length*3)%14);const on=s.Skill==='Blades';
   return `<div style="display:grid;grid-template-columns:1fr 50px;align-items:center;padding:6px 14px;${on?'background:linear-gradient(90deg,rgba(143,227,238,.18),transparent);border-left:3px solid #8fe3ee':''}"><span style="font:500 20px var(--body);color:${on?'#fff':'#bdb7aa'}">${s.Skill}</span><span class="mono" style="text-align:right;font-size:18px;color:${on?'#8fe3ee':'#9a968c'}">${lv}</span><div class="bar" style="grid-column:1/3;height:4px;border:0;margin-top:5px;background:rgba(255,255,255,.07)"><i style="width:${lv}%;background:${on?'#8fe3ee':'#6a675f'}"></i></div></div>`}).join('')).join('')}</div>
  <div class="abs" style="left:520px;top:160px"><div style="font:500 44px var(--display)">Blades</div><div class="mono" style="color:#9a968c;font-size:16px;margin-top:2px">RANK ${myRank} / 100 · FINESSE · ${perks.length} PERKS · RISES WHEN YOU LAND BLADE HITS</div></div>
  <svg class="abs" style="left:0;top:0" width="1920" height="1080">${[0,25,50,75,100].map(r=>`<line x1="${X(r)}" y1="270" x2="${X(r)}" y2="880" stroke="rgba(154,150,140,.18)" stroke-dasharray="4 8"/><text x="${X(r)}" y="905" fill="#8a877e" font-family="IBM Plex Mono" font-size="16" text-anchor="middle">${r}</text>`).join('')}
   <line x1="${X(0)}" y1="890" x2="${X(100)}" y2="890" stroke="#2a2f37" stroke-width="6"/><line x1="${X(0)}" y1="890" x2="${X(myRank)}" y2="890" stroke="#8fe3ee" stroke-width="6" filter="drop-shadow(0 0 6px #8fe3ee)"/>${lines}</svg>
  ${perks.map(p=>{const P=pos[p.id],s=state(p),cap=p.desc.startsWith('CAPSTONE'),isSel=p===sel;return `<div class="abs" style="left:${P.x-40}px;top:${P.y-40}px;width:80px;height:80px;${cap?'transform:rotate(45deg);':'border-radius:50%;'}border:3px solid ${col[s]};background:radial-gradient(circle at 40% 35%,${s==='own'?'rgba(143,227,238,.45)':s==='ready'?'rgba(232,135,58,.25)':'rgba(255,255,255,.04)'},rgba(0,0,0,.85));box-shadow:${s!=='lock'?`0 0 24px ${col[s]}`:'none'};${isSel?'outline:3px solid #fff;outline-offset:6px':''}"></div>
   <svg class="abs" style="left:${P.x-22}px;top:${P.y-22}px;width:44px;height:44px;color:${s==='lock'?'#4a4740':s==='own'?'#e8fdff':'#ffd2a0'};${cap?'':''}" viewBox="0 0 512 512"><use href="#p-${p.name}"/></svg>
   <div class="abs" style="left:${P.x-58}px;top:${P.y+48}px;width:116px;text-align:center;line-height:1.25;font:500 15px var(--body);color:${s==='lock'?'#8a877e':'#e7e2d6'}">${p.name}<br><span class="mono" style="color:#8a877e;font-size:13px">${s==='own'?p.max+'/'+p.max:'0/'+p.max}</span></div>`}).join('')}
  <div class="panel" style="left:520px;top:930px;width:1320px;height:100px;padding:20px 30px;box-sizing:border-box;display:flex;align-items:center;gap:30px"><div style="font:500 30px var(--display);color:#e8873a;white-space:nowrap">${sel.name}</div><div style="font:400 20px var(--body);color:#d8d2c4">${sel.desc}. Needs Blades ${sel.rank}.</div><div style="margin-left:auto;white-space:nowrap" class="prompts"><span><span class="btn">A</span>Spend point</span></div></div>`}});

const MK=[[.21,.62,'anchor'],[.29,.7,'anchor'],[.33,.58,'anchor'],[.19,.34,'anchor'],[.27,.28,'anchor'],[.44,.48,'anchor'],[.52,.55,'anchor']];
add({sec:'Screens',id:'map',name:'World map',src:'actors/region_bands.csv, actors/bosses.csv, world/regions.csv',region:'quiet',
 draw:(c,W,H)=>mapPaint(c,W,H),
 html:()=>{const reg=[['Cinderreach',.26,.69,1],['Saltmere',.2,.4,1],['Thornwood',.5,.5,1],['Glasswaste',.79,.62,0],['Rimefall',.52,.2,0],['Hollowdeep',.81,.27,0]];
 return `${reg.map(([n,x,y,on])=>{const b=band(n);return `<div class="abs" style="left:${x*1920-200}px;top:${y*1080-30}px;width:400px;text-align:center;text-shadow:0 2px 10px #000"><div style="font:500 ${on?40:34}px var(--display);letter-spacing:.12em;color:${on?'#f2ecdf':'#8a877e'}">${on?n.toUpperCase():'UNCHARTED'}</div><div class="mono" style="font-size:15px;color:${on?'#cfc8b8':'#5a574f'}">${on?`LV ${b['Min level']}–${b['Max level']}`:'CLIMB THE RELAY TOWER TO REVEAL'}</div></div>`}).join('')}
 ${MK.map(([x,y])=>`<div class="abs" style="left:${x*1920-15}px;top:${y*1080-15}px;filter:drop-shadow(0 0 8px #8fe3ee)">${mk.anchor}</div>`).join('')}
 <div class="abs" style="left:${.36*1920-13}px;top:${.74*1080-24}px;filter:drop-shadow(0 0 10px #e8873a)">${mk.ghost}</div>
 <div class="abs" style="left:${.255*1920-18}px;top:${.6*1080-18}px;width:36px;height:36px;transform:rotate(45deg);border:3px solid #f2ecdf;box-shadow:0 0 14px #fff"></div><div class="abs mono shadowT" style="left:${.255*1920+30}px;top:${.6*1080-12}px;font-size:15px">SPINE KEEP</div>
 <div class="abs" style="left:${.47*1920}px;top:${.64*1080}px;width:0;height:0;border-left:16px solid transparent;border-right:16px solid transparent;border-bottom:34px solid #fff;transform:rotate(-30deg);filter:drop-shadow(0 0 10px #fff)"></div>
 <div class="abs" style="left:${.56*1920-10}px;top:${.43*1080-26}px">${mk.quest}</div>
 <div class="panel" style="left:70px;top:60px;width:420px;padding:24px 28px;box-sizing:border-box"><div class="lbl">Region</div><div style="font:500 38px var(--display);margin-top:4px">Cinderreach</div><div class="mono" style="color:#cfc8b8;font-size:16px">LV 1–12 · ${el('Ember',18)} EMBER TINT</div><div class="rule"></div>
  ${[['Anchors lit','7 / 14'],['Sites cleared','11 / 18'],['Shard-bearer',`${vael.Boss}`],['Relay Tower','Climbed']].map(([a,b])=>`<div class="stat" style="grid-template-columns:1fr auto"><span>${a}</span><span>${b}</span></div>`).join('')}</div>
 <div class="panel" style="right:70px;top:60px;width:330px;padding:22px 26px;box-sizing:border-box;display:grid;gap:10px;font-size:18px"><div class="lbl">Layer</div><div style="display:flex;gap:10px"><span class="pill" style="color:#8fe3ee">SURFACE</span><span class="pill" style="color:#8a877e">UNDERVAULT</span></div><div class="rule" style="margin:4px 0"></div>
  <div style="display:flex;gap:12px;align-items:center">${mk.anchor}Lit Anchor</div><div style="display:flex;gap:12px;align-items:center">${mk.ghost}Shard-ghost · 3,120</div><div style="display:flex;gap:12px;align-items:center">${mk.quest}The Silent Keep</div><div style="display:flex;gap:12px;align-items:center"><i style="width:16px;height:16px;transform:rotate(45deg);border:2px solid #fff;margin:0 5px"></i>Citadel</div></div>
 ${prompts([['A','Travel'],['X','Place marker'],['LB','Layer'],['B','Back']])}`}});

const ven=DATA.vendor.slice(0,12),vs=ven[3];
add({sec:'Screens',id:'vendor',name:'Vendor',src:'items/vendors.csv (ITM_VEN_QUARTERMASTER), items/weapons_melee.csv',region:'lantern',
 draw:(c,W,H)=>{c.fillStyle='rgba(6,5,6,.55)';c.fillRect(0,0,W,H);bust(c,W*.83,H*.62,1.05);const v=c.createLinearGradient(0,0,W*.75,0);v.addColorStop(0,'rgba(6,6,8,.96)');v.addColorStop(.7,'rgba(6,6,8,.85)');v.addColorStop(1,'rgba(6,6,8,0)');c.fillStyle=v;c.fillRect(0,0,W,H)},
 html:()=>`<div class="ledgerHead" style="background:none"><h2>Quartermaster</h2><div class="tabs"><span class="bump">LB</span><span class="on">BUY</span><span>SELL</span><span>BUYBACK</span><span class="bump">RB</span></div><div class="cur" style="margin-left:180px"><span style="color:#ffcf9a">${use('ember','width:22px;height:22px;vertical-align:-3px')} ${fmt(ember)}</span></div></div>
 <div class="abs mono" style="left:80px;top:134px;font-size:15px;color:#8a877e;letter-spacing:.1em">LANTERN HOLD · RESTOCKS EVERY 72 H GAME TIME · NEXT IN 41 H · MATERIALS ARE NOT SOLD</div>
 <div class="abs" style="left:80px;top:180px;width:820px"><div style="display:grid;grid-template-columns:76px 1fr 150px 120px;gap:14px;padding:0 16px 8px" class="lbl"><span></span><span>Item</span><span>Class</span><span style="text-align:right">Price</span></div>
  ${ven.map((v,i)=>`<div style="display:grid;grid-template-columns:76px 1fr 150px 120px;gap:14px;align-items:center;padding:6px 16px;${v===vs?'background:linear-gradient(90deg,rgba(143,227,238,.2),rgba(143,227,238,.03));outline:1px solid rgba(143,227,238,.5)':i%2?'background:rgba(255,255,255,.02)':''}">
   ${tile(v,{st:'width:56px;height:56px'}).replace('inset:14px;width:80px;height:80px','inset:6px;width:40px;height:40px')}<div><div style="font:500 20px var(--display);color:#f2ecdf">${v.name}</div><div class="mono" style="font-size:12px;color:${RC[v.rarity]};letter-spacing:.12em">${v.rarity.toUpperCase()}</div></div><span style="color:#bdb7aa;font-size:17px">${v.cls}</span><span class="mono" style="text-align:right;font-size:19px;color:${+v.price>ember?'#d4483f':'#ffcf9a'}">${fmt(v.price)}</span></div>`).join('')}</div>
 <div class="panel" style="left:960px;top:180px;width:520px;padding:28px 32px;box-sizing:border-box"><div class="mono" style="font-size:14px;letter-spacing:.2em;color:${RC[vs.rarity]}">${vs.rarity.toUpperCase()} · ${vs.cls.toUpperCase()}</div><div style="font:500 40px var(--display);margin-top:6px">${vs.name}</div><div class="rule"></div>
  ${[['Physical AR',vs.ar],['Weight',vs.w],['Scaling',`MIG ${vs.g[0]} · FIN ${vs.g[1]} · LOR ${vs.g[2]} · GRT ${vs.g[3]}`],['Stock','1']].map(([a,b])=>`<div class="stat" style="grid-template-columns:1fr auto"><span>${a}</span><span>${b}</span></div>`).join('')}
  <div style="display:flex;align-items:center;justify-content:space-between;margin-top:24px;padding:16px 18px;background:rgba(232,135,58,.1);border:1px solid rgba(232,135,58,.4)"><span style="font:500 20px var(--body)">Buy for</span><span class="mono" style="font-size:30px;color:#ffcf9a">${use('ember','width:24px;height:24px;vertical-align:-3px')} ${fmt(vs.price)}</span></div>
  <div class="mono" style="font-size:15px;color:#8a877e;margin-top:10px">After purchase ${fmt(ember-vs.price)} Ember</div></div>
 <div class="abs shadowT" style="left:1500px;top:900px;font:italic 22px var(--serif);color:#e7e2d6;width:360px">"Hull steel, honest edge. Ostra's voice in your chest won't sharpen it for you."</div>
 ${prompts([['A','Buy'],['X','Buy x5'],['Y','Compare'],['B','Leave']])}`});

const shop=(()=>{const a=DATA.shop.filter(s=>+s.price_usd>0||+s.price_seals>0),k=[...new Set(a.map(x=>x.kind))],o=[];for(let i=0;o.length<9&&i<40;i++)k.forEach(K=>{const x=a.filter(y=>y.kind===K)[i];if(x&&o.length<9)o.push(x)});return o})();
add({sec:'Screens',id:'store',name:'Wardrobe store',src:'items/cosmetics.csv',region:'lantern',
 draw:(c,W,H)=>{c.fillStyle='rgba(8,7,9,.86)';c.fillRect(0,0,W,H)},
 html:()=>{const f=DATA.shop.find(s=>s.kind&&/Strider/i.test(s.kind)&&!shop.includes(s))||shop[0];const price=s=>+s.price_usd>0?`$${(+s.price_usd).toFixed(2)}`:+s.price_seals>0?`${s.price_seals} Seals`:`${fmt(s.price_ember)} Ember`;
 const ic=s=>/Strider/i.test(s.kind)?'strider':/Emote/i.test(s.kind)?'emote':'dye';
 return `<div class="ledgerBg"></div><div class="ledgerHead"><h2>Wardrobe</h2><div class="tabs"><span class="bump">LB</span><span class="on">FEATURED</span><span>DYES</span><span>STRIDER SKINS</span><span>EMOTES</span><span class="bump">RB</span></div><div class="cur"><span style="color:#cfc8b8">COSMETIC ONLY · NO POWER FOR SALE</span></div></div>
 <div class="panel" style="left:80px;top:170px;width:820px;height:780px;overflow:hidden"><div class="abs" style="inset:0;background:radial-gradient(circle at 60% 40%,${f.color_hex||'#8fe3ee'}55,transparent 60%),linear-gradient(160deg,#1c1a20,#0c0b0e)"></div>
  <svg class="abs" style="left:140px;top:90px;width:560px;height:560px;color:${f.color_hex||'#cfc8b8'};filter:drop-shadow(0 30px 40px rgba(0,0,0,.7)) drop-shadow(0 0 30px ${f.color_hex||'#8fe3ee'}66)" viewBox="0 0 64 64"><use href="#i-${ic(f)}"/></svg>
  <div class="abs" style="left:40px;bottom:36px;right:40px"><div class="mono lensT" style="font-size:15px;letter-spacing:.2em">FEATURED · ${f.kind.toUpperCase()}</div><div style="font:500 52px var(--display)">${f.name}</div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px"><span style="color:#9a968c;font-size:18px">${f.acquisition}</span><span class="mono" style="font-size:30px;color:#f2ecdf">${price(f)}</span></div></div></div>
 <div class="abs" style="left:940px;top:170px;display:grid;grid-template-columns:repeat(3,290px);gap:16px">${shop.map(s=>`<div style="position:relative;height:250px;border:1px solid rgba(154,150,140,.25);background:radial-gradient(circle at 50% 40%,${s.color_hex||'#6a675f'}44,transparent 65%),linear-gradient(160deg,#1c1a20,#0f0e11)">
  <svg style="position:absolute;left:85px;top:24px;width:120px;height:120px;color:${s.color_hex||'#cfc8b8'};filter:drop-shadow(0 10px 14px rgba(0,0,0,.7))" viewBox="0 0 64 64"><use href="#i-${ic(s)}"/></svg>
  <div style="position:absolute;left:16px;right:16px;bottom:14px"><div class="mono" style="font-size:12px;color:#8a877e;letter-spacing:.12em">${s.kind.toUpperCase()}</div><div style="font:500 20px var(--display);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${s.name}</div><div class="mono" style="font-size:18px;color:#f2ecdf;margin-top:4px">${price(s)}</div></div></div>`).join('')}</div>
 ${prompts([['A','Preview on character'],['Y','Purchase'],['B','Back']])}`}});

add({sec:'Screens',id:'dialogue',name:'Dialogue',src:'world/npcs.csv (ACT_NPC_HULLKNIGHT_COMMANDER), ui/strings.csv (STR_DLG_*)',region:'lantern',
 draw:(c,W,H)=>{c.fillStyle='rgba(8,6,6,.35)';c.fillRect(0,0,W,H);bust(c,W*.62,H*.66,1.35);const g=c.createLinearGradient(0,H*.5,0,H);g.addColorStop(0,'rgba(0,0,0,0)');g.addColorStop(1,'rgba(0,0,0,.92)');c.fillStyle=g;c.fillRect(0,0,W,H)},
 html:()=>`<div class="letterbox abs" style="inset:0"></div>
 <div class="abs" style="left:1330px;top:300px;z-index:6" class="shadowT"><div class="mono" style="font-size:15px;color:#e8873a;letter-spacing:.2em">HULL KNIGHTS · FACTION LEADER</div><div style="font:500 44px var(--display);text-shadow:0 2px 14px #000">Knight-Commander<br>Iselde Marr</div><div class="mono" style="font-size:15px;color:#cfc8b8;margin-top:6px">LANTERN HOLD · KNIGHTS' GATE</div></div>
 <div class="abs" style="left:0;right:0;top:770px;text-align:center;font:500 30px/1.45 var(--body);text-shadow:0 2px 10px #000;z-index:6">The Spine Keep went dark three nights ago. Vael's banner still flies over it.<br>I need it struck, and I can't spare a single knight to do it.</div>
 <div class="abs" style="left:120px;top:150px;display:grid;gap:10px;z-index:6;width:820px">${[
  ['1',"I'll take the Spine Keep.",'#fff',1],['2',`<span style="color:#7cc46a">${S('STR_DLG_CHECK_SPEECH',{VAR_req:40})}</span> Your knights abandoned that keep. Why should I bleed for it?`,'#e7e2d6'],
  ['3',`<span style="color:#8a877e">${S('STR_DLG_CHECK_FAC',{FAC_name:'Hull Knights'})}</span> I wear your colors. Give me a company.`,'#8a877e'],['4',S('STR_DLG_TRADE'),'#e7e2d6'],['5',S('STR_DLG_LEAVE'),'#bdb7aa']].map(([n,t,c,on])=>`<div style="display:flex;gap:18px;align-items:center;padding:12px 22px;font:500 24px var(--body);color:${c};background:${on?'linear-gradient(90deg,rgba(143,227,238,.22),rgba(143,227,238,0))':'linear-gradient(90deg,rgba(0,0,0,.55),transparent)'};border-left:3px solid ${on?'#8fe3ee':'transparent'}"><span class="mono" style="color:#8a877e;font-size:18px">${n}</span><span>${t}</span></div>`).join('')}</div>
 <div class="abs prompts" style="left:120px;bottom:40px;z-index:6"><span><span class="btn">A</span>Choose</span><span><span class="btn">Y</span>${S('STR_DLG_LOG')}</span></div>`});

add({sec:'Screens',id:'death',name:'Death screen',src:'ui/strings.csv (STR_DEATH_*)',region:'cinderreach',
 draw:(c,W,H)=>{c.save();c.globalCompositeOperation='saturation';c.fillStyle='rgba(128,128,128,.85)';c.fillRect(0,0,W,H);c.restore();c.fillStyle='rgba(6,22,26,.62)';c.fillRect(0,0,W,H);
  c.save();c.globalCompositeOperation='screen';SF.glow(c,W/2,H*.4,700,'#8fe3ee',.22);c.restore();
  c.save();c.translate(W*.8,H*.97);c.rotate(1.35);SF.figure(c,'knight',0,0,H*.3,'#8fe3ee',{blade:'#8fe3ee'});c.restore()},
 html:()=>`<div class="abs" style="left:0;right:0;top:250px;text-align:center"><div style="font:500 150px/1 var(--display);letter-spacing:.24em;color:#e8fdff;text-shadow:0 0 40px rgba(143,227,238,.7),0 0 120px rgba(143,227,238,.4)">${S('STR_DEATH_TITLE')}</div>
  <div class="shadowT" style="font:italic 28px var(--serif);color:#cfeff2;margin-top:24px"><span class="mono lensT" style="font-style:normal;font-size:17px;letter-spacing:.2em;margin-right:14px">OSTRA</span>Get up. I can still hear you.</div></div>
 <div class="panel" style="left:610px;top:560px;width:700px;padding:28px 34px;box-sizing:border-box;display:grid;grid-template-columns:90px 1fr;gap:20px;align-items:center">
  <div style="width:80px;height:80px;display:grid;place-items:center;border:2px solid #e8873a;border-radius:50%;box-shadow:0 0 30px rgba(232,135,58,.6)">${use('ember','width:44px;height:44px')}</div>
  <div><div style="font:500 24px var(--body)">${S('STR_DEATH_GHOST',{VAR_location:'Spinegate Bridge'})}</div><div class="mono" style="font-size:22px;color:#ffcf9a;margin-top:4px">${S('STR_DEATH_EMBER',{VAR_ember:'3,120'})}</div></div>
  <div style="grid-column:1/3;font:400 19px/1.5 var(--body);color:#bdb7aa;border-top:1px solid rgba(255,255,255,.1);padding-top:14px">${S('STR_DEATH_RULE')}</div></div>
 <div class="abs" style="left:0;right:0;top:860px;display:flex;justify-content:center"><div style="padding:16px 40px;border:1px solid rgba(143,227,238,.7);background:rgba(143,227,238,.12);font:500 26px var(--display);letter-spacing:.08em;box-shadow:0 0 30px rgba(143,227,238,.3)"><span class="btn">A</span>${S('STR_DEATH_RESPAWN',{VAR_anchor_name:'the Rib Anchor'})}</div></div>`});

add({sec:'Screens',id:'anchor',name:'Anchor rest',src:'actors/player_base_stats.csv (STAT_TONICS), plan 3.4 and 3.7',region:'undervault',
 draw:(c,W,H)=>{anchorCrystal(c,W/2,H*.62,260);SF.figure(c,'knight',W*.15,H*.98,H*.4,'#8fe3ee',{blade:'#8fe3ee'})},
 html:()=>{const opts=[['Rest','Refill Tonics. Normal enemies return.',-90,1],['Level Up','2 perk points · 1 Vigor · 1 attribute',-18],['Travel','7 Anchors lit in Cinderreach',54],['Summon Echo','Spend an Echo Bell to call a helper',126],['Smithing','Smith nearby: Brother Cane',198]];
 return `${opts.map(([n,d,a,on])=>{const r=330,x=960+Math.cos(a*Math.PI/180)*r,y=560+Math.sin(a*Math.PI/180)*r;return `<div class="abs" style="left:${x-150}px;top:${y-44}px;width:300px;text-align:center;padding:12px;background:${on?'rgba(143,227,238,.16)':'rgba(0,0,0,.55)'};border:1px solid ${on?'#8fe3ee':'rgba(154,150,140,.3)'};${on?'box-shadow:0 0 30px rgba(143,227,238,.35)':''}"><div style="font:500 28px var(--display);color:${on?'#fff':'#d8d2c4'}">${n}</div><div style="font-size:15px;color:#9a968c;margin-top:2px">${d}</div></div>`}).join('')}
 <div class="abs" style="left:0;right:0;top:40px;text-align:center"><div class="mono lensT" style="font-size:16px;letter-spacing:.3em">ANCHOR LIT</div><div style="font:500 48px var(--display);text-shadow:0 2px 20px #000">The Rib Anchor</div><div class="mono" style="color:#cfc8b8;font-size:15px">UNDERVAULT · BENEATH SALTMERE</div></div>
 <div class="panel" style="right:70px;top:660px;width:400px;padding:24px 28px;box-sizing:border-box"><div class="lbl">On rest</div>${[['Tonics','5 → 8'],['Health','401 → 688'],['Ward','Full'],['Elites, bosses','Stay down'],['Normal enemies','Return']].map(([a,b])=>`<div class="stat" style="grid-template-columns:1fr auto"><span>${a}</span><span>${b}</span></div>`).join('')}</div>
 ${prompts([['A','Rest'],['RS','Choose'],['B','Leave']])}`}});

// key art
const KA=[['cinderreach','Region 1','Cinderreach','The crash scar. The Meridian\'s spine still smokes on the horizon.','Spine Keep','Vael'],['saltmere','Region 2','Saltmere','Flooded salt flats and the decks of a ship that never stopped sinking.','The Drowned Hold','Corsa'],
 ['thornwood','Region 3','Thornwood','Red bark grown around a reactor shard. The Clans call it mother.','The Briar Engine','Sorrel'],['glasswaste','Region 4','Glasswaste','Sand fused to glass by a falling Shard. The dunes sing at dusk.','The Choir Spire','Brannoch'],
 ['rimefall','Region 5','Rimefall','Frozen highlands around the drive section. The monks keep its lamps lit.','Saint Drive Abbey','Mother Rime'],['hollowdeep','Region 6','Hollowdeep','Land the Quiet has already taken. The ground falls upward.','The Lifted City','The Hollow Twins'],
 ['lantern','Hub','Lantern Hold','A city built inside the Meridian\'s bridge.','Vendors · factions · raid gate','' ],['undervault','Underground','The Undervault','Cargo tunnels and Weave caves, lit only by Shard veins.','Beneath Regions 2, 3 and 5',''],['quiet','Act 3 · orbit','The Quiet','An older ship, seamless and too clean, waking in orbit.','Ring section, about 2 km²','']];
KA.forEach(([k,r,n,t,cit,b])=>{const bb=band(n)||{},bo=b?boss(b):null;add({sec:'Key art',id:'ka-'+k,name:n,src:'actors/region_bands.csv'+(bo?', actors/bosses.csv':''),region:k,small:1,
 draw:(c,W,H)=>{if(k==='cinderreach')SF.figure(c,'knight',W*.72,H*1.02,H*.4,'#ffb060');if(k==='hollowdeep')SF.figure(c,'knight',W*.5,H*.98,H*.2,'#c9c4cf',{blade:'#8fe3ee'});if(k==='glasswaste')SF.figure(c,'knight',W*.3,H*.95,H*.18,'#f0e0ff',{blade:'#b48cff'});
  const g=c.createLinearGradient(0,H*.55,0,H);g.addColorStop(0,'rgba(0,0,0,0)');g.addColorStop(1,'rgba(0,0,0,.75)');c.fillStyle=g;c.fillRect(0,0,W,H)},
 html:()=>`<div class="keyTitle"><div class="r">${r.toUpperCase()}${bb['Min level']?` · LV ${bb['Min level']}–${bb['Max level']}`:''}</div><h3>${n}</h3><p>${t}</p></div>
  <div class="keyMeta">${cit}${bo?`<br>Shard-bearer: ${bo.Boss}`:''}${bb['Element tint']&&bb['Element tint']!=='None'?`<br>${el(bb['Element tint'],18)} ${bb['Element tint']}`:''}</div>`})});

// ---------- mount
const gal=document.getElementById('gallery'),nav=document.getElementById('nav');let lastSec='';const queue=[];
SHOTS.forEach(s=>{if(s.sec!==lastSec){lastSec=s.sec;const h=document.createElement('h2');h.className='sect';h.id='sec-'+s.sec.replace(/\W/g,'');h.textContent=s.sec;gal.appendChild(h);nav.insertAdjacentHTML('beforeend',`<a href="#${h.id}">${s.sec}</a>`);
  if(s.small){const gr=document.createElement('div');gr.className='grid2';gr.id='kagrid';gal.appendChild(gr)}}
 const f=document.createElement('figure');f.className='shot';f.id=s.id;
 f.innerHTML=`<div class="frame"><div class="stage"><canvas class="bg" width="1920" height="1080"></canvas>${s.html()}</div></div><figcaption><b>${s.name}</b><code>${s.src}</code></figcaption>`;
 (s.small?document.getElementById('kagrid'):gal).appendChild(f);queue.push([f.querySelector('canvas'),s]);if(!s.small)nav.insertAdjacentHTML('beforeend',`<a href="#${s.id}">${s.name}</a>`)});
const ro=new ResizeObserver(es=>es.forEach(e=>{e.target.firstElementChild.style.transform=`scale(${e.contentRect.width/1920})`}));
document.querySelectorAll('.frame').forEach(f=>ro.observe(f));
(function next(){const q=queue.shift();if(!q)return;try{SF.paint(q[0],q[1].region,q[1].draw)}catch(e){console.error(q[1].id,e)}setTimeout(next,0)})();

gal.insertAdjacentHTML('beforeend','<p class="lede" style="margin-top:40px;font-size:.85rem">Icons made by Lorc, Delapouite, Sbed, Carl Olsen and Felbrigg from game-icons.net, CC BY 3.0, recolored. Landscapes, figures and the map are original procedural art. Full list in design/ui-mockups/CREDITS.csv.</p>');
