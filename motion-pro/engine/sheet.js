const {chromium}=require('playwright');
(async()=>{const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await br.newPage({viewport:{width:1080,height:1920}});
await p.goto(process.argv[2]);await p.waitForFunction(()=>window.ready);const dur=await p.evaluate(()=>window.ready);
const step=+process.argv[3]||0.5;let n=0;
for(let t=0;t<dur;t+=step){await p.evaluate(t=>render(t),t);await p.screenshot({path:`chk/f_${String(n).padStart(3,'0')}.jpg`,type:'jpeg',quality:70});n++}
console.log(n);await br.close()})();
