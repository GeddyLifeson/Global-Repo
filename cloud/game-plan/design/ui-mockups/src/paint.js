// Shardfall procedural painter: layered landscapes, region features, figures, particles, grade.
const SF = (() => {
function rng(seed){return()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function noise1(r){const p=[];for(let i=0;i<1024;i++)p.push(r());return x=>{const i=Math.floor(x),f=x-i,a=p[i&1023],b=p[(i+1)&1023],u=f*f*(3-2*f);return a+(b-a)*u}}
function fbm(n,x,o=6,ridge=false){let v=0,a=.5,f=1;for(let i=0;i<o;i++){let s=n(x*f);if(ridge)s=1-Math.abs(s*2-1);v+=a*s;a*=.5;f*=2.07}return v}
const lerp=(a,b,t)=>a+(b-a)*t;
function hex(h){h=h.replace('#','');return[parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]}
function mix(a,b,t){const A=hex(a),B=hex(b);return`rgb(${A.map((v,i)=>Math.round(lerp(v,B[i],t))).join(',')})`}
function rgba(h,a){const c=hex(h);return`rgba(${c[0]},${c[1]},${c[2]},${a})`}

const P = {
 cinderreach:{seed:11,sky:['#1b1416','#5a2e22','#d27a3e','#f0b070'],sun:{x:.68,y:.55,r:90,c:'#ffcf8a'},haze:'#c9773b',
   layers:[{y:.62,amp:.22,f:1.4,c:'#6a3c2c'},{y:.70,amp:.10,f:2.2,c:'#3e2620'},{y:.80,amp:.07,f:3,c:'#241714'},{y:.93,amp:.05,f:5,c:'#120c0b'}],
   feat:'cinder',part:{t:'ember',n:260,c:'#ffb060'},rays:1,grade:'#ff8a3a'},
 saltmere:{seed:23,sky:['#0f1c22','#2f5560','#9cc6c2','#e6e2d4'],sun:{x:.3,y:.5,r:70,c:'#f4f0e0'},haze:'#a9cfc6',
   layers:[{y:.57,amp:.12,f:1.2,c:'#3e6a6c',soft:1},{y:.60,amp:.04,f:2,c:'#244448'}],water:.62,
   feat:'salt',part:{t:'rain',n:420,c:'#cfe6e6'},rays:0,grade:'#6fb0b0'},
 thornwood:{seed:37,sky:['#140d0c','#3e1c16','#a8562e','#e3b56a'],sun:{x:.5,y:.42,r:60,c:'#ffd890'},haze:'#b8663a',
   layers:[{y:.6,amp:.16,f:1.6,c:'#5a2a20',soft:1},{y:.68,amp:.08,f:2.5,c:'#3a1a16'},{y:.82,amp:.06,f:4,c:'#1e0f0d'}],
   feat:'thorn',part:{t:'pollen',n:220,c:'#7fe0c0'},rays:1,grade:'#d07040'},
 glasswaste:{seed:41,sky:['#0e0b1c','#3a2c64','#b796d6','#f4e2c4'],sun:{x:.75,y:.48,r:80,c:'#fff0d8'},haze:'#c7a8e0',
   layers:[{y:.64,amp:.05,f:.9,c:'#7a64a8'},{y:.72,amp:.06,f:1.4,c:'#4e3e78'},{y:.86,amp:.05,f:2.2,c:'#241c3c'}],
   feat:'glass',part:{t:'glint',n:160,c:'#ffffff'},rays:1,grade:'#a080e0'},
 rimefall:{seed:53,sky:['#0c1420','#2a4460','#8eaecb','#e8f0f6'],sun:{x:.22,y:.4,r:55,c:'#ffffff'},haze:'#c8dcea',
   layers:[{y:.58,amp:.42,f:1.1,c:'#7d98b4',snow:1},{y:.70,amp:.24,f:1.8,c:'#4a6582',snow:1},{y:.82,amp:.1,f:3,c:'#26384c'},{y:.94,amp:.04,f:5,c:'#121c28'}],
   feat:'rime',part:{t:'snow',n:500,c:'#ffffff'},rays:0,grade:'#a8c8ff'},
 hollowdeep:{seed:67,sky:['#0b0b0e','#26232c','#6e6a78','#b8b2c0'],sun:{x:.5,y:.3,r:120,c:'#d8d0e8'},haze:'#8a8496',
   layers:[{y:.68,amp:.2,f:1.3,c:'#4a4654'},{y:.76,amp:.07,f:2.4,c:'#2e2b36'},{y:.9,amp:.05,f:4,c:'#141318'}],
   feat:'hollow',part:{t:'updebris',n:240,c:'#c9c4cf'},rays:0,grade:'#7a6a9a',desat:.55},
 lantern:{seed:71,sky:['#0c0a10','#2a2030','#7a4a3a','#d89050'],sun:{x:.5,y:.62,r:40,c:'#ffd090'},haze:'#c8803a',
   layers:[{y:.80,amp:.04,f:3,c:'#1a1418'}],feat:'lantern',part:{t:'ember',n:120,c:'#ffd070'},rays:0,grade:'#e0a050'},
 undervault:{seed:83,sky:['#020606','#061414','#0e3030','#1a5a58'],sun:null,haze:'#2a8a88',
   layers:[{y:.78,amp:.08,f:2,c:'#0a1a1a'},{y:.9,amp:.06,f:4,c:'#040c0c'}],feat:'vault',part:{t:'mote',n:200,c:'#8fe3ee'},rays:0,grade:'#40c0c0'},
 quiet:{seed:97,sky:['#000000','#020306','#06080c','#0c1014'],sun:null,haze:'#30343c',
   layers:[],feat:'quiet',part:{t:'stars',n:0,c:'#fff'},rays:0,grade:'#c8281e'}
};

function sky(ctx,W,H,p){
  const g=ctx.createLinearGradient(0,0,0,H*.75);
  p.sky.forEach((c,i)=>g.addColorStop(i/(p.sky.length-1),c));
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  if(p.sun){const s=p.sun,x=s.x*W,y=s.y*H;
    let r=ctx.createRadialGradient(x,y,0,x,y,s.r*7);r.addColorStop(0,rgba(s.c,.55));r.addColorStop(.25,rgba(s.c,.18));r.addColorStop(1,rgba(s.c,0));
    ctx.fillStyle=r;ctx.fillRect(0,0,W,H);
    r=ctx.createRadialGradient(x,y,0,x,y,s.r);r.addColorStop(0,'#fff');r.addColorStop(.5,rgba(s.c,.9));r.addColorStop(1,rgba(s.c,0));
    ctx.fillStyle=r;ctx.beginPath();ctx.arc(x,y,s.r,0,7);ctx.fill();}
}
function clouds(ctx,W,H,p,R){
  const n=noise1(R);ctx.save();ctx.globalCompositeOperation='screen';
  for(let b=0;b<7;b++){const y=H*(.08+b*.07),th=H*(.03+R()*.04);
    for(let x=0;x<W;x+=6){const v=fbm(n,x/260+b*13,5);if(v<.5)continue;
      ctx.fillStyle=rgba(p.haze,(v-.5)*.22);ctx.fillRect(x,y+Math.sin(x/300+b)*th,6,th*(v*1.4));}}
  ctx.restore();
}
function ridge(ctx,W,H,L,R,i,p){
  const n=noise1(R),off=R()*100,pts=[];
  for(let x=0;x<=W;x+=4){let v=fbm(n,x/W*L.f*3+off,6,i===0&&!L.soft);v=Math.max(0,Math.min(1,(v-.22)/.56));const y=H*L.y-H*L.amp*v;pts.push([x,y])}
  ctx.beginPath();ctx.moveTo(0,H);pts.forEach(q=>ctx.lineTo(q[0],q[1]));ctx.lineTo(W,H);ctx.closePath();
  const g=ctx.createLinearGradient(0,H*(L.y-L.amp),0,H);g.addColorStop(0,L.c);g.addColorStop(1,mix(L.c,'#000000',.55));
  ctx.fillStyle=g;ctx.fill();
  // rim light from sun side
  ctx.save();ctx.clip();ctx.globalCompositeOperation='screen';
  const sx=p.sun?p.sun.x*W:W/2;
  ctx.lineWidth=3;ctx.strokeStyle=rgba(p.sun?p.sun.c:p.haze,.25);ctx.beginPath();pts.forEach((q,k)=>k?ctx.lineTo(q[0],q[1]+2):ctx.moveTo(q[0],q[1]+2));ctx.stroke();
  if(L.snow){ctx.globalCompositeOperation='source-over';const th=H*L.y-H*L.amp*.35;
    const sg=ctx.createLinearGradient(0,H*(L.y-L.amp),0,H*L.y);sg.addColorStop(0,'rgba(245,250,255,.95)');sg.addColorStop(1,'rgba(200,220,240,.5)');ctx.fillStyle=sg;
    ctx.beginPath();pts.forEach((q,k)=>k?ctx.lineTo(q[0],q[1]):ctx.moveTo(q[0],q[1]));
    for(let k=pts.length-1;k>=0;k--){const q=pts[k];const d=Math.max(0,th-q[1])*(.7+.5*fbm(n,q[0]/18,4));ctx.lineTo(q[0],q[1]+d)}ctx.fill();
    }
  // light falloff toward sun
  const lg=ctx.createRadialGradient(sx,H*L.y,0,sx,H*L.y,W*.6);lg.addColorStop(0,rgba(p.haze,.18));lg.addColorStop(1,rgba(p.haze,0));
  ctx.globalCompositeOperation='screen';ctx.fillStyle=lg;ctx.fillRect(0,0,W,H);ctx.restore();
  // fog band in front of layer
  const f=ctx.createLinearGradient(0,H*(L.y-.02),0,H*(L.y+.12));f.addColorStop(0,rgba(p.haze,0));f.addColorStop(.5,rgba(p.haze,.16*(1-i*.2)));f.addColorStop(1,rgba(p.haze,0));
  ctx.fillStyle=f;ctx.fillRect(0,H*(L.y-.02),W,H*.14);
  return pts;
}
function glow(ctx,x,y,r,c,a=1){const g=ctx.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,rgba(c,a));g.addColorStop(1,rgba(c,0));ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,7);ctx.fill()}
function shardCrack(ctx,R,x,y,len,ang,c='#8fe3ee'){
  ctx.save();ctx.globalCompositeOperation='screen';ctx.strokeStyle=c;ctx.shadowColor=c;ctx.shadowBlur=14;ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(x,y);let px=x,py=y;for(let i=0;i<8;i++){ang+=(R()-.5)*.9;px+=Math.cos(ang)*len/8;py+=Math.sin(ang)*len/8;ctx.lineTo(px,py)}ctx.stroke();ctx.restore();
}
// --- features
function wreck(ctx,W,H,R,x,y,s,col){
  ctx.save();ctx.translate(x,y);ctx.rotate(-.18);ctx.fillStyle=col;
  ctx.beginPath();ctx.moveTo(-s*1.6,0);ctx.lineTo(-s*1.2,-s*.32);ctx.lineTo(s*.6,-s*.42);ctx.lineTo(s*1.1,-s*.18);ctx.lineTo(s*1.3,0);ctx.closePath();ctx.fill();
  ctx.strokeStyle=col;ctx.lineWidth=s*.035;
  for(let i=0;i<9;i++){const rx=-s*1.1+i*s*.22,h=.7+R()*.45,bx=rx+s*.22*(R()<.3?.4:1);ctx.beginPath();ctx.moveTo(rx-s*.04,-s*.3);ctx.quadraticCurveTo(rx,-s*h*1.1,bx,-s*h);ctx.lineTo(bx+s*.02,-s*h+s*.03);ctx.quadraticCurveTo(rx+s*.05,-s*h*.95,rx+s*.04,-s*.3);ctx.fill()}
  ctx.lineWidth=s*.02;ctx.beginPath();ctx.moveTo(s*.6,-s*.42);ctx.lineTo(s*.95,-s*1.3);ctx.lineTo(s*1.02,-s*1.28);ctx.lineTo(s*.72,-s*.4);ctx.fill();ctx.stroke();
  for(let i=0;i<26;i++)glow(ctx,-s*1.3+R()*s*2.4,-s*(.05+R()*.33),3+R()*4,R()<.7?'#8fe3ee':'#ffb060',.9);
  for(let i=0;i<4;i++)shardCrack(ctx,R,-s+R()*s*1.8,-s*.2,s*.4,-Math.PI/2+R()-.5);
  ctx.restore();
}
function castle(ctx,R,x,y,s,col,lit='#ffb060'){
  ctx.fillStyle=col;const n=5+Math.floor(R()*4);
  for(let i=0;i<n;i++){const w=s*(.12+R()*.1),h=s*(.4+R()*.9),tx=x+(i-n/2)*s*.18;
    ctx.fillRect(tx-w/2,y-h,w,h);ctx.beginPath();ctx.moveTo(tx-w*.65,y-h);ctx.lineTo(tx,y-h-s*(.2+R()*.3));ctx.lineTo(tx+w*.65,y-h);ctx.fill();
    for(let k=0;k<3;k++)if(R()<.7)glow(ctx,tx+(R()-.5)*w*.5,y-h*(.2+R()*.7),3+R()*3,lit,.95);}
  ctx.fillRect(x-s*n*.1,y-s*.25,s*n*.2,s*.25);
}
function conifers(ctx,R,pts,col,h,dens){
  ctx.fillStyle=col;for(let k=0;k<pts.length;k+=dens){const[x,y]=pts[k];const th=h*(.6+R()*.8);
    ctx.beginPath();ctx.moveTo(x-th*.22,y+4);ctx.lineTo(x,y-th);ctx.lineTo(x+th*.22,y+4);ctx.fill();}
}
function canopy(ctx,R,pts,col,hi,h,dens){
  for(let k=0;k<pts.length;k+=dens){const[x,y]=pts[k];const r=h*(.4+R()*.6);
    ctx.fillStyle=col;ctx.fillRect(x-2,y-r*.6,4,r);
    for(let j=0;j<5;j++){ctx.beginPath();ctx.arc(x+(R()-.5)*r,y-r*.9-R()*r*.5,r*(.35+R()*.3),0,7);ctx.fill()}
    ctx.fillStyle=hi;for(let j=0;j<4;j++){ctx.beginPath();ctx.arc(x-r*.25+(R()-.5)*r*.5,y-r*1.15-R()*r*.3,r*(.12+R()*.12),0,7);ctx.fill()}}
}
function spire(ctx,R,x,y,h,w){
  const g=ctx.createLinearGradient(x-w,0,x+w,0);g.addColorStop(0,'#3a2c64');g.addColorStop(.45,'#d8c4f4');g.addColorStop(.55,'#8a6ac0');g.addColorStop(1,'#241c3c');
  ctx.fillStyle=g;ctx.beginPath();ctx.moveTo(x-w,y);ctx.lineTo(x-w*.3,y-h*.7);ctx.lineTo(x,y-h);ctx.lineTo(x+w*.4,y-h*.65);ctx.lineTo(x+w,y);ctx.fill();
  glow(ctx,x,y-h,w*3,'#f0e0ff',.35);
}
function floater(ctx,R,x,y,s,col){
  ctx.fillStyle=col;ctx.beginPath();ctx.moveTo(x-s,y);
  for(let i=0;i<=6;i++)ctx.lineTo(x-s+i*s/3,y-(R()*s*.15));
  ctx.lineTo(x+s*.2,y+s*(.9+R()*.6));ctx.closePath();ctx.fill();
  ctx.fillStyle='rgba(220,214,230,.25)';ctx.fillRect(x-s,y-s*.08,s*2,s*.06);
}
function figure(ctx,kind,x,y,h,rim,opt={}){
  // silhouettes built from primitives, rim-lit
  ctx.save();ctx.translate(x,y);const s=h/100;ctx.scale(s,s);
  const body=()=>{ctx.beginPath();
    if(kind==='knight'){ // back view player
      ctx.moveTo(-14,0);ctx.lineTo(-12,-40);ctx.lineTo(-22,-46);ctx.lineTo(-24,-70);ctx.quadraticCurveTo(-20,-82,-8,-84);ctx.lineTo(-7,-92);ctx.quadraticCurveTo(0,-102,7,-92);ctx.lineTo(8,-84);ctx.quadraticCurveTo(20,-82,24,-70);ctx.lineTo(22,-46);ctx.lineTo(12,-40);ctx.lineTo(14,0);ctx.lineTo(4,0);ctx.lineTo(0,-34);ctx.lineTo(-4,0);ctx.closePath();
      ctx.moveTo(-22,-68);ctx.lineTo(-30,-20);ctx.lineTo(-24,-18);ctx.lineTo(-18,-60); // cape edge
    } else if(kind==='riot'){
      ctx.moveTo(-20,0);ctx.lineTo(-18,-36);ctx.lineTo(-30,-40);ctx.lineTo(-32,-72);ctx.lineTo(-12,-80);ctx.lineTo(-10,-90);ctx.lineTo(10,-90);ctx.lineTo(12,-80);ctx.lineTo(32,-72);ctx.lineTo(30,-40);ctx.lineTo(18,-36);ctx.lineTo(20,0);ctx.lineTo(6,0);ctx.lineTo(0,-30);ctx.lineTo(-6,0);ctx.closePath();
    } else if(kind==='boss'){
      ctx.moveTo(-22,0);ctx.lineTo(-20,-38);ctx.lineTo(-40,-44);ctx.lineTo(-44,-74);ctx.lineTo(-26,-84);ctx.lineTo(-14,-86);ctx.lineTo(-12,-94);ctx.lineTo(-6,-106);ctx.lineTo(0,-98);ctx.lineTo(6,-106);ctx.lineTo(12,-94);ctx.lineTo(14,-86);ctx.lineTo(26,-84);ctx.lineTo(44,-74);ctx.lineTo(40,-44);ctx.lineTo(20,-38);ctx.lineTo(22,0);ctx.lineTo(8,0);ctx.lineTo(0,-30);ctx.lineTo(-8,0);ctx.closePath();
      ctx.moveTo(-40,-70);ctx.lineTo(-62,-4);ctx.lineTo(-30,-10);ctx.closePath();ctx.moveTo(40,-70);ctx.lineTo(60,-6);ctx.lineTo(30,-10);ctx.closePath();
    } else if(kind==='shambler'){
      ctx.moveTo(-10,0);ctx.lineTo(-8,-30);ctx.lineTo(-18,-58);ctx.lineTo(-4,-66);ctx.lineTo(4,-74);ctx.lineTo(14,-64);ctx.lineTo(16,-40);ctx.lineTo(10,-30);ctx.lineTo(12,0);ctx.lineTo(3,0);ctx.lineTo(0,-24);ctx.lineTo(-3,0);ctx.closePath();
    }};
  body();ctx.fillStyle=opt.fill||'#0b0a0c';ctx.fill();
  ctx.save();ctx.clip();ctx.lineWidth=5/s*.6;ctx.strokeStyle=rim;ctx.shadowColor=rim;ctx.shadowBlur=10;ctx.translate(opt.rimDx||2,0);body();ctx.stroke();ctx.restore();
  if(kind==='knight'){ // sword held low right, glowing
    ctx.save();ctx.translate(22,-44);ctx.rotate(.5);const g=ctx.createLinearGradient(0,0,0,58);g.addColorStop(0,'#fff2d0');g.addColorStop(1,opt.blade||'#ff8a3a');
    ctx.shadowColor=opt.blade||'#ff8a3a';ctx.shadowBlur=24;ctx.fillStyle=g;ctx.fillRect(-1.6,0,3.2,58);ctx.fillStyle='#222';ctx.fillRect(-6,-2,12,3);ctx.restore();}
  if(kind==='riot'){ctx.save();ctx.globalCompositeOperation='screen';const g=ctx.createLinearGradient(-50,0,-30,0);g.addColorStop(0,rgba(opt.shield||'#b48cff',.0));g.addColorStop(1,rgba(opt.shield||'#b48cff',.55));
    ctx.fillStyle=g;ctx.fillRect(-52,-86,22,74);ctx.strokeStyle=opt.shield||'#b48cff';ctx.shadowColor=opt.shield||'#b48cff';ctx.shadowBlur=18;ctx.lineWidth=1.4;ctx.strokeRect(-52,-86,22,74);
    glow(ctx,0,-84,8,'#8fe3ee',1);ctx.restore();}
  if(kind==='boss'){ctx.save();ctx.globalCompositeOperation='screen';glow(ctx,0,-100,26,'#ffb060',1);glow(ctx,0,-100,9,'#fff4d8',1);
    ctx.strokeStyle='#ff8a3a';ctx.shadowColor='#ff6a20';ctx.shadowBlur=20;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(48,-60);ctx.lineTo(70,-150);ctx.stroke();ctx.restore();}
  if(kind==='shambler'){ctx.save();ctx.globalCompositeOperation='screen';for(let i=0;i<5;i++)glow(ctx,-6+i*4,-50-i*4,5,'#8fe3ee',.9);ctx.restore();}
  ctx.restore();
}
function particles(ctx,W,H,p,R){
  const q=p.part;if(!q)return;ctx.save();ctx.globalCompositeOperation='screen';
  for(let i=0;i<q.n;i++){const x=R()*W,y=R()*H,z=R();
    if(q.t==='ember'){glow(ctx,x,y,2+z*6,q.c,.5+z*.5);}
    else if(q.t==='rain'){ctx.strokeStyle=rgba(q.c,.15+z*.25);ctx.lineWidth=1+z;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x-8-z*10,y+30+z*40);ctx.stroke();}
    else if(q.t==='snow'){ctx.fillStyle=rgba(q.c,.3+z*.6);ctx.beginPath();ctx.arc(x,y,.8+z*3.2,0,7);ctx.fill();}
    else if(q.t==='pollen'){glow(ctx,x,y,2+z*5,q.c,.35+z*.4);}
    else if(q.t==='glint'){if(y<H*.5)continue;ctx.strokeStyle=rgba(q.c,.4+z*.6);ctx.lineWidth=1;const r=2+z*7;ctx.beginPath();ctx.moveTo(x-r,y);ctx.lineTo(x+r,y);ctx.moveTo(x,y-r);ctx.lineTo(x,y+r);ctx.stroke();}
    else if(q.t==='updebris'){ctx.fillStyle=rgba(q.c,.2+z*.5);const r=1+z*4;ctx.fillRect(x,y,r,r*1.6);ctx.fillStyle=rgba(q.c,.06);ctx.fillRect(x,y+r*1.6,r*.5,10+z*30);}
    else if(q.t==='mote'){glow(ctx,x,y,1.5+z*4,q.c,.4+z*.5);}
  }ctx.restore();
}
function rays(ctx,W,H,p){if(!p.rays||!p.sun)return;ctx.save();ctx.globalCompositeOperation='screen';const x=p.sun.x*W,y=p.sun.y*H;
  for(let i=0;i<9;i++){const a=Math.PI*.15+i*.09+Math.sin(i*7)*.03,l=W;ctx.fillStyle=rgba(p.sun.c,.035);ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+Math.cos(a)*l,y+Math.sin(a)*l);ctx.lineTo(x+Math.cos(a+.04)*l,y+Math.sin(a+.04)*l);ctx.fill();
   ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x-Math.cos(a)*l,y+Math.sin(a)*l);ctx.lineTo(x-Math.cos(a+.04)*l,y+Math.sin(a+.04)*l);ctx.fill();}ctx.restore();}
let grainPat=null;
function post(ctx,W,H,p,R){
  ctx.save();ctx.globalCompositeOperation='soft-light';ctx.fillStyle=rgba(p.grade,.35);ctx.fillRect(0,0,W,H);ctx.restore();
  if(p.desat){ctx.save();ctx.globalCompositeOperation='saturation';ctx.fillStyle=`rgba(128,128,128,${p.desat})`;ctx.fillRect(0,0,W,H);ctx.restore();}
  const v=ctx.createRadialGradient(W/2,H*.55,H*.35,W/2,H*.55,W*.75);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(1,'rgba(0,0,0,.72)');ctx.fillStyle=v;ctx.fillRect(0,0,W,H);
  if(!grainPat){const c=document.createElement('canvas');c.width=c.height=160;const g=c.getContext('2d'),d=g.createImageData(160,160);for(let i=0;i<d.data.length;i+=4){const n=Math.random()*255;d.data[i]=d.data[i+1]=d.data[i+2]=n;d.data[i+3]=16}g.putImageData(d,0,0);grainPat=c}
  ctx.fillStyle=ctx.createPattern(grainPat,'repeat');ctx.fillRect(0,0,W,H);
}
function features(ctx,W,H,p,R,ridges){
  const f=p.feat;
  if(f==='cinder'){wreck(ctx,W,H,R,W*.42,H*.66,W*.2,'#2a1a16');castle(ctx,R,W*.84,H*.71,70,'#24171a');}
  if(f==='salt'){const y0=H*p.water;
    const g=ctx.createLinearGradient(0,y0,0,H);g.addColorStop(0,'#8fb8b4');g.addColorStop(.3,'#3f6a6a');g.addColorStop(1,'#0e1e20');ctx.fillStyle=g;ctx.fillRect(0,y0,W,H-y0);
    ctx.save();ctx.globalCompositeOperation='screen';for(let i=0;i<260;i++){const y=y0+Math.pow(R(),1.6)*(H-y0),w=20+R()*160;ctx.fillStyle=`rgba(240,240,225,${.05+R()*.12})`;ctx.fillRect(p.sun.x*W-w/2+(R()-.5)*W*.5*(y-y0)/(H-y0),y,w,1.5);}ctx.restore();
    // half-sunk cargo decks
    [[.62,.6,.16,-.12],[.18,.7,.1,.2],[.86,.66,.08,.08]].forEach(([x,y,s,a])=>{ctx.save();ctx.translate(W*x,H*y);ctx.rotate(a);ctx.fillStyle='#14262a';ctx.fillRect(-W*s,-H*s*.5,W*s*2,H*s*.55);
      for(let i=0;i<8;i++){ctx.fillStyle='#1c3236';ctx.fillRect(-W*s+i*W*s/4,-H*s*.62,W*s*.18,H*s*.14)}for(let i=0;i<6;i++)glow(ctx,-W*s+R()*W*s*2,-H*s*.4,3,'#8fe3ee',.8);ctx.restore();
      ctx.fillStyle='rgba(20,38,42,.35)';ctx.fillRect(W*(x-s),H*y+H*.04,W*s*2,H*s*.3);});
    // stilt town
    for(let i=0;i<14;i++){const x=W*(.02+i*.03),y=H*.64;ctx.fillStyle='#10201f';ctx.fillRect(x,y-30-R()*20,26,26);ctx.fillRect(x+4,y-8,2,20);ctx.fillRect(x+20,y-8,2,20);glow(ctx,x+12,y-24,5,'#ffcf8a',.9)}}
  if(f==='thorn'){canopy(ctx,R,ridges[0],'#5a2a20','#6e3424',34,8);canopy(ctx,R,ridges[1],'#3e1612','#5a2418',62,12);canopy(ctx,R,ridges[2],'#1c0b09','#33140f',120,18);
    shardCrack(ctx,R,W*.5,H*.62,180,-Math.PI/2);glow(ctx,W*.5,H*.6,160,'#8fe3ee',.25);}
  if(f==='glass'){for(let i=0;i<7;i++)spire(ctx,R,W*(.1+i*.13+R()*.04),H*(.7+R()*.08),H*(.18+R()*.3),18+R()*20);
    ctx.save();ctx.globalCompositeOperation='screen';const g=ctx.createLinearGradient(0,H*.72,0,H);g.addColorStop(0,'rgba(240,220,255,.0)');g.addColorStop(.3,'rgba(240,220,255,.18)');g.addColorStop(1,'rgba(240,220,255,0)');ctx.fillStyle=g;ctx.fillRect(0,H*.72,W,H*.28);ctx.restore();}
  if(f==='rime'){castle(ctx,R,W*.62,H*.47,70,'#1c2a3a','#ffd890');conifers(ctx,R,ridges[2],'#0e1824',60,10);conifers(ctx,R,ridges[3],'#070c12',110,16);}
  if(f==='hollow'){for(let i=0;i<14;i++)floater(ctx,R,W*R(),H*(.15+R()*.5),20+R()*90,i%3?'#2a2830':'#3c3844');
    const g=ctx.createLinearGradient(0,0,0,H*.5);g.addColorStop(0,'rgba(200,190,220,.12)');g.addColorStop(1,'rgba(200,190,220,0)');ctx.fillStyle=g;ctx.fillRect(W*.45,0,W*.1,H*.5);}
  if(f==='lantern'){ // bridge section rising from city
    ctx.fillStyle='#120e12';ctx.beginPath();ctx.moveTo(W*.28,H);ctx.lineTo(W*.36,H*.3);ctx.quadraticCurveTo(W*.5,H*.16,W*.64,H*.3);ctx.lineTo(W*.72,H);ctx.fill();
    for(let i=0;i<340;i++){const x=W*(.3+R()*.4),y=H*(.28+R()*.7);if(Math.abs(x-W/2)>W*(.08+(y/H)*.14))continue;ctx.fillStyle=R()<.15?'#8fe3ee':`rgba(255,${170+R()*60|0},90,${.5+R()*.5})`;ctx.fillRect(x,y,3+R()*5,2+R()*4)}
    for(let i=0;i<70;i++){const x=R()*W,y=H;ctx.fillStyle=i%2?'#0c0a0c':'#151014';const w=30+R()*70,h=H*(.08+R()*.22);ctx.beginPath();ctx.moveTo(x-6,y-h);ctx.lineTo(x+w/2,y-h-24-R()*30);ctx.lineTo(x+w+6,y-h);ctx.fill();ctx.fillRect(x,y-h,w,h);for(let k=0;k<4;k++)glow(ctx,x+R()*w,y-R()*h,4,'#ffc070',.9)}
    glow(ctx,W/2,H*.2,90,'#8fe3ee',.4);}
  if(f==='vault'){const n=noise1(R);ctx.fillStyle='#020707';ctx.beginPath();ctx.moveTo(0,0);for(let x=0;x<=W;x+=6)ctx.lineTo(x,H*.08+H*.22*fbm(n,x/220,5,true)*(.6+.4*Math.sin(x/300)));ctx.lineTo(W,0);ctx.fill();
    for(let i=0;i<40;i++){const x=R()*W;ctx.beginPath();ctx.moveTo(x-12,0);ctx.lineTo(x,H*(.2+R()*.25));ctx.lineTo(x+12,0);ctx.fill()}
    for(let i=0;i<14;i++)shardCrack(ctx,R,R()*W,H*(.3+R()*.6),120+R()*200,R()*6);glow(ctx,W*.55,H*.6,300,'#3fb0b0',.25);}
  if(f==='quiet'){for(let i=0;i<900;i++){ctx.fillStyle=`rgba(255,255,255,${R()*.8})`;ctx.fillRect(R()*W,R()*H*.8,R()*2,R()*2)}
    // planet below
    const cx=W*.5,cy=H*2.15,r=H*1.5;let g=ctx.createRadialGradient(cx,cy,0,cx,cy,r*1.06);g.addColorStop(0,'#1a120e');g.addColorStop(.8,'#3a2a22');g.addColorStop(.93,'#a0623a');g.addColorStop(.955,'#cfe4f4');g.addColorStop(1,'rgba(156,198,232,0)');
    ctx.fillStyle=g;ctx.beginPath();ctx.arc(cx,cy,r*1.06,0,7);ctx.fill();
    // ring structure, seamless
    ctx.save();ctx.translate(W*.5,H*.42);ctx.rotate(-.22);ctx.strokeStyle='#e8e6e0';ctx.lineWidth=26;ctx.beginPath();ctx.ellipse(0,0,W*.42,H*.12,0,Math.PI*1.05,Math.PI*1.95);ctx.stroke();
    ctx.strokeStyle='#8a8880';ctx.lineWidth=10;ctx.beginPath();ctx.ellipse(0,18,W*.42,H*.12,0,Math.PI*1.05,Math.PI*1.95);ctx.stroke();
    ctx.lineWidth=40;ctx.strokeStyle='#22252a';ctx.beginPath();ctx.ellipse(0,0,W*.42,H*.12,0,Math.PI*.05,Math.PI*.95);ctx.stroke();
    for(let i=0;i<9;i++){const a=Math.PI*(1.1+i*.1);glow(ctx,Math.cos(a)*W*.42,Math.sin(a)*H*.12,9,'#c8281e',1)}ctx.restore();
    glow(ctx,W*.5,H*.42,40,'#ffffff',.6);
    ctx.save();ctx.globalCompositeOperation='screen';for(let i=0;i<5;i++)shardCrack(ctx,R,W*(.3+i*.1),H*.66,140,-Math.PI/2,'#8fe3ee');ctx.restore();}
}
function paint(cv,key,draw){
  const p=P[key],W=cv.width,H=cv.height,ctx=cv.getContext('2d'),R=rng(p.seed);
  sky(ctx,W,H,p);if(key!=='quiet'&&key!=='undervault')clouds(ctx,W,H,p,R);
  const ridges=p.layers.map((L,i)=>ridge(ctx,W,H,L,R,i,p));
  features(ctx,W,H,p,R,ridges);rays(ctx,W,H,p);
  if(draw)draw(ctx,W,H,R);
  particles(ctx,W,H,p,R);post(ctx,W,H,p,R);
}
return {paint,figure,glow,shardCrack,rng,P};
})();
