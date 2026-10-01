import glob,sys
from PIL import Image, ImageDraw
fs=sorted(glob.glob('chk/f_*.jpg'));w,h=216,384;cols=10
for part in range(0,len(fs),40):
    sub=fs[part:part+40];rows=(len(sub)+cols-1)//cols
    c=Image.new('RGB',(w*cols,h*rows),(30,30,30));d=ImageDraw.Draw(c)
    for i,f in enumerate(sub):
        im=Image.open(f).resize((w,h));x,y=(i%cols)*w,(i//cols)*h;c.paste(im,(x,y));d.text((x+5,y+5),f"{(part+i)*0.5:.1f}s",fill=(255,0,255))
    c.save(f'chk/sheet_{part//40}.jpg',quality=82)
print('ok')
