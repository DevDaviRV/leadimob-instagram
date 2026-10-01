"""Reel 2 (02/10) — trilha 120 BPM Mi menor, cortes no grid; SFX sincronizados às cenas."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=19.5; N=int((END+0.3)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(11)
B=0.5; T_={'s1':0,'s2':2.5,'s3':5.0,'s4':7.5,'s5':10.0,'s6':12.5,'s7':15.5}
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
def add(buf,x,at,g=1.0):
    i=int(at*SR)
    if i<0: x=x[-i:];i=0
    j=min(len(buf),i+len(x))
    if j>i: buf[i:j]+=g*x[:j-i]
midi=lambda n:440*2**((n-69)/12)
def saw(f,n,d=0): ph=np.cumsum(np.full(n,f*(1+d))/SR); return 2*(ph%1)-1
prog=[[40,59,64,67,71],[36,60,64,67,71],[43,59,62,67,74],[38,57,62,66,69]]  # Em C G D
L=np.zeros(N);R=np.zeros(N);KK=[]
for b in range(0,int(END/(4*B))+1):
    st=b*4*B; ch=prog[b%4]; n=int((4*B+0.8)*SR); tt=np.arange(n)/SR; env=np.minimum(1,tt/0.4)*np.clip((4*B+0.8-tt)/0.8,0,1)
    open_=0.25 if st<T_['s6'] else 1.0
    for m in ch[1:]:
        s=lp(saw(midi(m),n,0.004)*env*0.009,700+2600*open_); add(L,s,st); add(R,s*0.9,st)
for k in range(int(END/(B/4))):
    t=k*B/4; pos=k%16; sec=max([s for s,v in T_.items() if t>=v],key=lambda s:T_[s])
    if t>END-1.0: continue
    build = sec in ('s6','s7')
    if pos in (0,8) or (build and pos in (4,12)) or (sec in('s5',) and pos in(4,12)):
        n=int(0.42*SR);tt=np.arange(n)/SR;f=44+110*np.exp(-tt*30);kk=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*7)*0.34
        add(L,kk,t);add(R,kk,t);KK.append(t)
    if pos in (4,12) and sec not in ('s1',):
        n=int(0.22*SR);tt=np.arange(n)/SR;c=bp(rng.standard_normal(n),1500,6500)*np.exp(-tt*28)*0.06;add(L,c,t);add(R,c,t)
    if pos%2==0 and sec!='s1' or (sec=='s1' and pos%4==2):
        n=int(0.035*SR);tt=np.arange(n)/SR;h=hp(rng.standard_normal(n),9000)*np.exp(-tt*140)*0.022*[1,.4,.7,.4][pos%4];add(L,h*.6,t);add(R,h,t)
    if pos%2==0:
        b=int(t//(4*B));ch=prog[b%4];n=int(B/2*SR*0.9);tt=np.arange(n)/SR;f=midi(ch[0]-12)
        add(L,np.sin(2*np.pi*f*tt)*np.exp(-tt*4)*0.1,t);add(R,np.sin(2*np.pi*f*tt)*np.exp(-tt*4)*0.1,t)
sc=np.ones(N)
for kt in KK:
    i=int(kt*SR);n=int(0.28*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.5*np.exp(-tt/0.08)[:j-i])
L*=sc;R*=sc
ir=rng.standard_normal(int(1.8*SR))*np.exp(-np.arange(int(1.8*SR))/SR*3);ir/=np.sqrt((ir**2).sum())
L=L+0.22*fftconvolve(hp(L,300),ir)[:N];R=R+0.22*fftconvolve(hp(R,300),ir)[:N]
F=np.zeros(N)
def impact(at,g=.35):
    n=int(1.4*SR);tt=np.arange(n)/SR;f=36+80*np.exp(-tt*10);add(F,np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*3)*g+lp(rng.standard_normal(n),1500)*np.exp(-tt*14)*g*.3,at)
def tick(at,g=.05,f=2200): n=int(.04*SR);tt=np.arange(n)/SR;add(F,np.sin(2*np.pi*f*tt)*np.exp(-tt*150)*g,at)
def pop(at,g=.08,f=900): n=int(.14*SR);tt=np.arange(n)/SR;fr=f*(1+.6*np.exp(-tt*60));add(F,np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*38)*g,at)
def whoosh(at,d=.5,g=.08):
    n=int(d*SR);tt=np.arange(n)/SR;x=bp(rng.standard_normal(n),600,5000)*np.sin(np.pi*tt/d)**2*g;add(F,x,at)
def stampfx(at): impact(at,.22); n=int(.12*SR);tt=np.arange(n)/SR;add(F,bp(rng.standard_normal(n),200,2500)*np.exp(-tt*30)*.15,at)
impact(0.0,.3);impact(0.5,.38)
for c in [2.5,5.0,7.5,10.0,12.5,15.5]: whoosh(c-0.35,0.45,0.07)
pop(2.75,.08,800)
for k in range(28): tick(5.2+(k/28)**0.85*1.7,.03,1700+k*30)
impact(6.0,.2)
pop(7.7,.07,1000)
for i in range(3): stampfx(10.15+i*1.0)
impact(12.5,.25)
for i,a in enumerate([13.5,14.0,14.5]): impact(a,.3 if i<2 else .4)
for k in range(11): tick(16.4+k*0.082,.04,2600)
pop(17.5,.09,1200);whoosh(17.5,.4,.06)
fade=np.clip(T/0.03,0,1)*np.clip((END-T)/0.6,0,1)
mus=(L+R)/2; mr=np.sqrt(np.mean(mus**2)); fr_=np.sqrt(np.mean(F**2))
F*=mr*10**(-4/20)/fr_
outL=(L+F)*fade; outR=(R+F)*fade
st=np.stack([outL,outR],1); st=st/np.max(np.abs(st))*0.85
wavfile.write('mix.wav',SR,(st*32767).astype(np.int16)); print('ok')
