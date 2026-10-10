// Renderiza a faixa contínua (10800×1350) de uma vez e recorta os 10 slides de 1080×1350.
// uso: node shoot.js http://localhost:8126/d3/c1/index.html png
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await br.newPage({viewport:{width:10800,height:1350}});
p.on('pageerror',e=>console.log('ERR',e.message));p.on('response',r=>{if(r.status()>=400)console.log('HTTP',r.status(),r.url())});
await p.goto(process.argv[2]||'http://localhost:8126/d3/c1/index.html');await p.waitForFunction(()=>window.ready);await p.evaluate(()=>window.ready);
const out=process.argv[3]||'png';fs.mkdirSync(out,{recursive:true});
// auditoria: tamanho mínimo de fonte e vazamento de conteúdo para fora da margem/slide
const audit=await p.evaluate(()=>{const r=[];document.querySelectorAll('.sl').forEach((s,i)=>{const sb=s.getBoundingClientRect();let minF=999,minT='';
 const w=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(!n.textContent.trim())continue;const el=n.parentElement;const f=parseFloat(getComputedStyle(el).fontSize);if(f<minF){minF=f;minT=n.textContent.trim().slice(0,24)}
  const rg=document.createRange();rg.selectNodeContents(n);const b=rg.getBoundingClientRect();if(b.left<sb.left+70||b.right>sb.right-70)r.push(`slide ${i+1}: texto fora da margem: "${n.textContent.trim().slice(0,30)}" [${Math.round(b.left-sb.left)}..${Math.round(b.right-sb.left)}]`)}
 let top=1e9,bot=0;[...s.children].forEach(c=>{if(c.classList.contains('foot')||c.classList.contains('ghost'))return;const b=c.getBoundingClientRect();top=Math.min(top,b.top);bot=Math.max(bot,b.bottom)});
 r.push(`slide ${i+1}: fonte mín ${minF}px ("${minT}") · conteúdo y ${Math.round(top)}..${Math.round(bot)}`)});return r});
console.log(audit.join('\n'));
for(let i=0;i<10;i++)await p.screenshot({path:`${out}/slide-${String(i+1).padStart(2,'0')}.png`,clip:{x:i*1080,y:0,width:1080,height:1350}});
await p.screenshot({path:`${out}/_strip.jpg`,type:'jpeg',quality:72});
await br.close();console.log('ok')})();
