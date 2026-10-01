// render2: URL-based, supports subframe motion blur. node render2.js url fps sub start end out.mp4
const {chromium}=require('playwright');const {spawn}=require('child_process');
const [url,fps,sub,a,b,out]=process.argv.slice(2);const FPS=+fps,SUB=+sub;
(async()=>{const br=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium',args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await br.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>console.log('LOG',m.text()));
await p.goto(url);await p.waitForFunction(()=>window.ready);await p.evaluate(()=>window.ready);
const vf=SUB>1?['-vf',`tmix=frames=${SUB}:weights=${Array(SUB).fill(1).join(' ')},select='not(mod(n\\,${SUB}))',setpts=N/(${FPS}*TB)`]:[];
const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',''+(FPS*SUB),'-i','-',...vf,'-r',''+FPS,'-c:v','libx264','-preset','medium','-crf','14','-pix_fmt','yuv420p',out],{stdio:['pipe','inherit','inherit']});
const t0=Date.now();
for(let f=+a;f<+b;f++){for(let s=0;s<SUB;s++){const t=(f+s/SUB-0.5+0.5/SUB)/FPS;await p.evaluate(t=>render(Math.max(0,t)),t);
  const buf=await p.screenshot({type:'png'});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
 if(f%30==0)console.log(out,f,((Date.now()-t0)/1000).toFixed(1)+'s');}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await br.close();})();
