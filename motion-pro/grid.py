import sys,glob,re
from PIL import Image, ImageDraw
fs=sorted(glob.glob('chk/s_*.png'),key=lambda f:float(re.findall(r's_([\d.]+)\.png',f)[0]))
cols=int(sys.argv[2]) if len(sys.argv)>2 else 5; w,h=360,640
ims=[Image.open(f).convert('RGB').resize((w,h)) for f in fs]
rows=(len(ims)+cols-1)//cols; c=Image.new('RGB',(w*cols,h*rows),(40,40,40)); d=ImageDraw.Draw(c)
for i,(f,im) in enumerate(zip(fs,ims)):
    x,y=(i%cols)*w,(i//cols)*h; c.paste(im,(x,y)); d.text((x+8,y+8),re.findall(r's_([\d.]+)',f)[0],fill=(255,0,255))
c.save(sys.argv[1],quality=85)
