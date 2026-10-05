import sys,subprocess,glob,os
from PIL import Image,ImageDraw
ts=[float(x) for x in sys.argv[2:]];name=sys.argv[1]
for f in glob.glob('chk/s_*.png'): os.remove(f)
subprocess.run(['node','../../motion-pro/engine/shot2.js','http://localhost:8126/work/r1-incorporador/build.html']+[str(t) for t in ts],check=True)
w,h=360,640;cols=min(len(ts),5);rows=(len(ts)+cols-1)//cols
m=Image.new('RGB',(w*cols,h*rows));d=ImageDraw.Draw(m)
for i,t in enumerate(ts):
    im=Image.open(f'chk/s_{t:g}.png').convert('RGB').resize((w,h));x,y=(i%cols)*w,(i//cols)*h;m.paste(im,(x,y));d.text((x+6,y+6),f'{t}s',fill=(255,0,255))
m.save(f'chk/{name}.jpg',quality=85)
