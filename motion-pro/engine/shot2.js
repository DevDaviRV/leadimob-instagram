const {chromium}=require('playwright');
(async()=>{const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await br.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto(process.argv[2]);await p.waitForFunction(()=>window.ready);await p.evaluate(()=>window.ready);
for(const t of process.argv.slice(3).map(Number)){await p.evaluate(t=>render(t),t);await p.screenshot({path:`chk/s_${t}.png`});}
await br.close()})();
