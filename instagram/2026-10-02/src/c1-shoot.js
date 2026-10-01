const {chromium}=require('playwright');
(async()=>{const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await br.newPage({viewport:{width:10800,height:1350}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(process.argv[2]);await p.waitForFunction(()=>window.ready);await p.evaluate(()=>window.ready);
const out=process.argv[3]||'png';require('fs').mkdirSync(out,{recursive:true});
for(let i=0;i<10;i++)await p.screenshot({path:`${out}/slide-${String(i+1).padStart(2,'0')}.png`,clip:{x:i*1080,y:0,width:1080,height:1350}});
await p.screenshot({path:`${out}/_strip.jpg`,type:'jpeg',quality:70});
await br.close();console.log('ok')})();
