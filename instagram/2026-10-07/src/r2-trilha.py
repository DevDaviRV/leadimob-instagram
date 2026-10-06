"""Reel 2 (07/10) "Imobiliária, recebeu o lead?" · trilha 108 BPM em Mi menor (resolve em Sol maior no CTA).
Arco: gancho (Em/C) -> funil e lead parado (Am sombrio, silêncio no "parado") -> UMA ETAPA/UM DONO/UM PRÓXIMO PASSO (Sol, groove sobe) -> funil que vira visita (groove completo) -> CTA (Sol).
SFX presos aos mesmos tempos do index.html."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=23.1; N=int((END+0.4)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(71)
B=60/108
T=dict(ld=0.7,hb=1.55,dep=2.05,bar=2.5,pr=2.95,sh1=[4.45,4.95],B=4.95,b1=5.15,b2=5.3,kb=5.55,h0=6.1,mv=7.1,g=[8.0,8.55],stall=9.0,bOut=10.2,cOut=14.55,c=[10.6,10.9,11.55,12.2,12.65],nx=13.5,sh2=[14.55,14.9],D=14.9,d1=15.15,kdp=15.45,h=[15.8,16.4,16.95],dOut=18.35,F=18.9,logo=18.75,f1=19.05,f2=19.3,typ=19.6,send=20.6,sub=20.9,sheen=21.5)
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
def add(buf,x,at,g=1.0):
    i=int(round(at*SR))
    if i<0: x=x[-i:];i=0
    j=min(len(buf),i+len(x))
    if j>i: buf[i:j]+=g*x[:j-i]
midi=lambda n:440*2**((n-69)/12)
def saw(f,n,d=0.0,ph=0.0): p=np.cumsum(np.full(n,f*(1+d))/SR)+ph; return 2*(p%1)-1
def tri(f,n): p=np.cumsum(np.full(n,f)/SR); return 2*np.abs(2*(p%1)-1)-1
# ---------- harmonia ----------
CH={'Em':(40,[52,55,59,64]),'C':(36,[52,55,60,64]),'Am':(45,[52,57,60,64]),'G':(43,[55,59,62,67]),'D':(38,[54,57,62,66])}
PROG=[(0,2.5,'Em'),(2.5,4.95,'C'),(4.95,7.5,'Am'),(7.5,10.2,'Am'),(10.2,12.6,'G'),(12.6,14.9,'Em'),(14.9,17.4,'C'),(17.4,18.9,'D'),(18.9,21.4,'G'),(21.4,24.0,'G')]
def chord_at(t):
    for a,b,c in PROG:
        if a<=t<b: return CH[c]
    return CH['G']
def sec(t):
    if t<4.95: return 'hook'
    if t<9.0: return 'cool'
    if t<10.2: return 'void'
    if t<14.9: return 'build'
    if t<18.9: return 'full'
    return 'cta'
L=np.zeros(N);R=np.zeros(N);KK=[]
for a,b,c in PROG:
    root,notes=CH[c]; d=min(b,END+0.3)-a; n=int((d+0.7)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.25)*np.clip((d+0.7-tt)/0.7,0,1)
    op={'hook':0.25,'cool':0.2,'void':0.08,'build':0.5,'full':1.0,'cta':0.8}[sec(a+0.01)]
    for k,m in enumerate(notes):
        sL=lp((saw(midi(m),n,0.004,k*.13)+saw(midi(m),n,-0.005,k*.31))*env*0.006,500+3200*op)
        sR=lp((saw(midi(m),n,-0.004,k*.57)+saw(midi(m),n,0.006,k*.77))*env*0.006,500+3200*op)
        add(L,sL,a);add(R,sR,a)
    sub=np.sin(2*np.pi*midi(root)*tt)*env*0.03;add(L,sub,a);add(R,sub,a)
S16=B/4
def kick(t,g=.36):
    n=int(0.4*SR);tt=np.arange(n)/SR;f=46+120*np.exp(-tt*34);k=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*8)*g
    k[:200]+=hp(rng.standard_normal(200),2000)*np.linspace(1,0,200)*g*.25
    add(L,k,t);add(R,k,t);KK.append(t)
def clap(t,g=.075):
    n=int(0.2*SR);tt=np.arange(n)/SR;c=bp(rng.standard_normal(n),1100,5200)*(np.exp(-tt*30)+.6*np.exp(-np.maximum(0,tt-.012)*42)*(tt>.012))*g
    add(L,c,t);add(R,c*.92,t+0.0006)
def hat(t,g=.02,dec=150):
    n=int(0.06*SR);tt=np.arange(n)/SR;h=hp(rng.standard_normal(n),8500)*np.exp(-tt*dec)*g;add(L,h*.65,t);add(R,h,t)
def bass(t,note,g=.11,d=0.26):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note);x=(np.sin(2*np.pi*f*tt)+.35*lp(saw(f,n),420))*np.exp(-tt*5.5)*np.minimum(1,tt/0.004)*g;add(L,x,t);add(R,x,t)
def pluck(t,note,g=.035,pan=0.0):
    n=int(0.5*SR);tt=np.arange(n)/SR;f=midi(note);x=lp(tri(f,n)+.4*saw(f*2,n),3800)*np.exp(-tt*9)*np.minimum(1,tt/0.003)*g
    for k,(dl,gg) in enumerate([(0,1),(0.45,.42),(0.9,.2)]): add(L,x*(1-pan*(1 if k%2==0 else -1))*gg,t+dl);add(R,x*(1+pan*(1 if k%2==0 else -1))*gg,t+dl)
ARP=[0,1,3,2,1,3,2,0]
for k in range(int(END/S16)):
    t=k*S16; s=sec(t); pos=k%16; bt=pos%4==0; root,notes=chord_at(t)
    if s=='hook':
        if pos in (0,8) and t>=1.9: kick(t,.3)
        if pos%4==0 and t>=1.9: bass(t,root,.07)
        if pos%4==2 and t>0.6: hat(t,.012)
    elif s=='cool':
        # esfria: grave sustentado, kick some aos poucos
        if t<7.0 and pos in (0,8): kick(t,.24*(1-(t-4.95)/2.0))
        if t<8.0 and pos%4==0: bass(t,root,.07*(1-(t-4.95)/3.6))
        if t<7.0 and pos%4==2: hat(t,.01)
    elif s=='void':
        pass
    elif s=='build':
        r=(t-10.2)/4.7
        if bt: kick(t,.26+.1*r)
        if pos in (4,12) and t>=11.0: clap(t,.03+.04*r)
        if pos%2==0: bass(t,root,.07+.05*r)
        hat(t,.008+.014*r)
        if t>=11.0 and pos%4==2: pluck(t,notes[ARP[(k//4)%8]]+12,.02+.012*r,0.3)
        if t>=13.9:
            clap(t,.02+.06*(t-13.9)/0.65)
            clap(t+S16/2,.02+.05*(t-13.9)/0.65)
    elif s=='full':
        if bt: kick(t,.38)
        if pos in (4,12): clap(t,.085)
        hat(t,.022*[1,.45,.75,.45][pos%4],90 if pos%4==2 else 160)
        if pos%2==0: bass(t,root+(12 if pos%8==6 else 0),.12)
        pluck(t,notes[ARP[k%8]]+12,.032 if t<17.2 else .038,0.35)
    else:
        if t<22.1 and pos in (0,8): kick(t,.3)
        if t<22.1 and pos in (4,12): clap(t,.05)
        if pos%2==0 and t<22.5: bass(t,root,.095); hat(t,.014)
        if t<22.6 and pos%2==0: pluck(t,notes[ARP[(k//2)%8]]+12,.032,0.3)
sc=np.ones(N)
for kt in KK:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.5*np.exp(-tt/0.09)[:j-i])
L*=sc;R*=sc
dyn=np.ones(N)
def duck(a,b,g,ra=0.05,rb=0.15):
    m=np.clip((TT-a)/ra,0,1)*np.clip((b-TT)/rb,0,1); dyn[:]=dyn*(1-(1-g)*m)
duck(9.0,10.1,0.28,0.05,0.4); duck(14.55,14.9,0.45,0.1,0.02)
L*=dyn;R*=dyn
ir=rng.standard_normal(int(2.0*SR))*np.exp(-np.arange(int(2.0*SR))/SR*2.8);ir/=np.sqrt((ir**2).sum())
L=L+0.2*fftconvolve(hp(L,350),ir)[:N];R=R+0.2*fftconvolve(hp(R,350),np.roll(ir,97))[:N]
# ---------- SFX ----------
FL=np.zeros(N);FR=np.zeros(N)
def fx(x,at,g=1.0,pan=0.0): add(FL,x,at,g*(1-pan));add(FR,x,at,g*(1+pan))
def impact(at,g=.35,f0=38):
    n=int(1.3*SR);tt=np.arange(n)/SR;f=f0+90*np.exp(-tt*12);fx(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*3.2)*g+lp(rng.standard_normal(n),1400)*np.exp(-tt*16)*g*.3,at)
def thud(at,g=.16,f0=70):
    n=int(0.3*SR);tt=np.arange(n)/SR;f=f0+70*np.exp(-tt*40);fx(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*14)*g+bp(rng.standard_normal(n),300,2400)*np.exp(-tt*50)*g*.35,at)
def tick(at,g=.05,f=2200,pan=0.0): n=int(.04*SR);tt=np.arange(n)/SR;fx(np.sin(2*np.pi*f*tt)*np.exp(-tt*150)*g,at,1,pan)
def key(at,g=.05):
    n=int(.05*SR);tt=np.arange(n)/SR;fx(bp(rng.standard_normal(n),1800,5200)*np.exp(-tt*120)*g+np.sin(2*np.pi*(300+rng.uniform(-40,40))*tt)*np.exp(-tt*90)*g*.6,at,1,rng.uniform(-.2,.2))
def pop(at,g=.09,f=700,pan=0.0): n=int(.16*SR);tt=np.arange(n)/SR;fr=f*(1+.7*np.exp(-tt*55));fx(np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*34)*g,at,1,pan)
def whoosh(at,d=.5,g=.08,f0=500,f1=5200,peak=.6,pan=0.0):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;env=np.where(k<peak,(k/peak)**2.2,((1-k)/(1-peak))**1.6);x=rng.standard_normal(n);out=np.zeros(n);nb=12
    for b in range(nb):
        a=int(b*n/nb);e=int((b+1)*n/nb);fc=f0*(f1/f0)**((b+.5)/nb);out[a:e]=bp(x[a:e+0],fc*.6,min(fc*1.6,20000))[:e-a]
    fx(lp(out,9000)*env*g,at,1,pan)
def riser(at,d,g=.06):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;f=200*(8**k);fx((np.sin(2*np.pi*np.cumsum(f)/SR)*.35+hp(rng.standard_normal(n),1500+5000*0)*k)*k**2*g,at)
def bell(at,notes,g=.05,dec=4.0,pan=0.0):
    n=int(1.6*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes:
        f=midi(m);x+=(np.sin(2*np.pi*f*tt)+.4*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt*8)+.2*np.sin(2*np.pi*f*3.02*tt)*np.exp(-tt*14))*np.exp(-tt*dec)
    fx(x*g*np.minimum(1,tt/0.002),at,1,pan)
def shimmer(at,d=.6,g=.03):
    n=int(d*SR);tt=np.arange(n)/SR;fx(hp(rng.standard_normal(n),7000)*np.sin(np.pi*tt/d)**2*g*(0.6+0.4*np.sin(2*np.pi*14*tt)),at)
# A · gancho
impact(0.0,.22,40);tick(0.0,.04,1800)
whoosh(T['ld']-0.28,0.3,.04,500,3500,.8,.3);pop(T['ld']+0.02,.08,780,.3);bell(T['ld']+0.04,[71],.03,7,.3)
whoosh(T['hb']-0.3,0.34,.06,400,3500,.8);thud(T['hb'],.1)
thud(T['dep']-0.1,.12);whoosh(T['dep']-0.3,.34,.06,400,3500,.8);thud(T['dep'],.16,60);impact(T['dep'],.3,40);bell(T['dep']+0.02,[64,67,71],.05)
for i in range(10): tick(T['bar']+i*0.02,.02,1500+200*i)
whoosh(T['pr']-0.2,.3,.05,600,3500,.7);thud(T['pr'],.08,80)
# persianas A->B
for i in range(8): tick(T['sh1'][0]+i*0.025+0.1,.03,1200+150*i)
whoosh(T['sh1'][0]-0.05,.5,.1,300,6000,.5);riser(T['sh1'][0],.45,.04)
impact(T['sh1'][1],.2,36);whoosh(T['sh1'][1],.5,.08,5200,350,.4)
# B · funil
thud(T['b1']-0.1,.1,70);thud(T['b2']-0.05,.1,70);pop(T['kb'],.06,520)
whoosh(T['h0']-0.2,.28,.04,700,3500,.8);pop(T['h0'],.08,860,-.1);bell(T['h0']+0.02,[71],.04,6,-.1)
whoosh(T['mv']-0.05,.55,.05,600,3800,.55,-.1);tick(T['mv']+0.55,.04,2000);bell(T['mv']+0.55,[67],.04,6)
for i,gg in enumerate([T['g'][0],T['g'][1]]): pop(gg+0.1,.05,1000+120*i,.3);bell(gg+0.1,[74+2*i],.03,7,.3)
thud(T['stall']-0.02,.18,55);bell(T['stall']+0.04,[63],.035,7,-.2);bell(T['stall']+0.2,[58],.04,6,-.2);impact(T['stall'],.24,32)
# giro B->C
whoosh(T['bOut']-0.05,.5,.1,5200,350,.45);whoosh(T['bOut']+0.3,.4,.07,350,5200,.5)
# C
for i,tc in enumerate(T['c']): whoosh(tc-0.18,.28,.04,600,3500,.8,(-.2,.2)[i%2]);thud(tc+0.02,.1+.01*i,80+8*i)
bell(T['c'][1]+0.05,[67],.04,5);bell(T['c'][2]+0.05,[71],.04,5);bell(T['c'][3]+0.05,[74],.04,5)
impact(T['c'][4]+0.1,.3,40);bell(T['c'][4]+0.12,[67,71,74],.06,3);shimmer(T['c'][4]+0.14,.7,.03)
whoosh(T['nx']-0.2,.3,.05,600,3500,.8);pop(T['nx']+0.1,.06,700);pop(T['nx']+0.5,.08,950,.2);bell(T['nx']+0.5,[79,86],.05,5,.2);tick(T['nx']+0.6,.03,2600)
# cortina C->D
riser(T['sh2'][0]-0.02,0.36,.06);whoosh(T['sh2'][0],.34,.1,6000,300,.5);impact(T['D'],.34,36);whoosh(T['D']+0.02,.4,.07,300,5200,.55)
# D
whoosh(T['d1']-0.1,.25,.04,600,3500,.8);thud(T['d1'],.1,70);thud(T['d1']+0.14,.1,76);pop(T['kdp'],.06,540)
for i,h_ in enumerate(T['h']): whoosh(h_-0.12,.3,.05,700,4200,.8,(-.2,.2)[i%2]);pop(h_+0.02,.07,880+80*i,.1)
for i,h_ in enumerate(T['h'][1:]): tick(h_+0.45,.04,2200+200*i);bell(h_+0.45,[(71,74)[i]],.05,5,.1)
arr=T['h'][2]+0.5
impact(arr,.3,40);pop(arr+0.02,.1,1000,.3);bell(arr+0.04,[74,78,81],.06,3,.2);shimmer(arr+0.05,.8,.035)
pop(arr+0.12,.07,1200,-.2);bell(arr+0.18,[86],.04,5,-.2)
# dolly D->E
whoosh(T['dOut']-0.05,.8,.12,350,6000,.55);riser(T['dOut'],.7,.04);thud(T['F'],.14,70)
# E · CTA
whoosh(T['logo']-0.2,.34,.04,600,3000,.8);bell(T['logo']+0.06,[50,57,62,66],.06,2.2);impact(T['logo']+0.06,.16,44)
thud(T['f1'],.12,80);pop(T['f2']+0.04,.05,520)
for i in range(11): key(T['typ']+0.04+i*(0.8/11),.05)
pop(T['send'],.1,900,.3);bell(T['send']+0.03,[74,78],.05,5,.3);bell(T['send']+0.15,[81],.04,5,.3);impact(T['send'],.2,44)
for i,dt in enumerate([-0.3,-0.14,0.06,0.24]): thud(T['sub']+dt+0.1,.06,110+8*i)
bell(T['sheen']-0.1,[62,66,69,74],.05,2.6);shimmer(T['sheen'],.6,.02);bell(22.1,[74,78,81],.03,3)
FL=FL+0.16*fftconvolve(hp(FL,400),ir)[:N];FR=FR+0.16*fftconvolve(hp(FR,400),np.roll(ir,211))[:N]
# ---------- mix ----------
mus=np.sqrt(np.mean(((L+R)/2)**2));fxr=np.sqrt(np.mean(((FL+FR)/2)**2))
g=mus*10**(-2.5/20)/fxr
fade=np.clip(TT/0.02,0,1)*np.clip((END-TT)/0.3,0,1)
st=np.stack([(L+FL*g)*fade,(R+FR*g)*fade],1);st=np.tanh(st/np.max(np.abs(st))*1.6)/np.tanh(1.6)*0.86
wavfile.write('mix.wav',SR,(st[:int(END*SR)]*32767).astype(np.int16));print('ok',st.shape)
