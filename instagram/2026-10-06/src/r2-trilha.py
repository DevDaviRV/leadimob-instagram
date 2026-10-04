'''Reel 2 (06/10) trilha 116 BPM em Mi menor -> Sol maior (arpejo em colcheias, kick em 4, baixo sincopado).'''
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=24.74; N=int((END+0.4)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(31)
B=0.6
bt=lambda n:round(n*60/116,3)
s0=bt(21)
T=dict(cs=0.25,gray=bt(6),pill=bt(7),curt=4.5,curtOut=5.03,roll=bt(15),bOut=10.2,s=[s0,s0+1.81,s0+3.62,s0+5.43],irisC=s0+7.18,irisO=s0+7.18,push=s0+9.78,typ=s0+10.58,send=s0+11.48,sub=s0+11.98,logo=s0+12.48)
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
CH={'Em':(40,[52,55,59,64]),'C':(36,[52,55,60,64]),'Am':(33,[52,57,60,64]),'D':(38,[54,57,62,66]),'G':(43,[55,59,62,67]),'Bm':(35,[54,59,62,66])}
PROG=[(0,2.07,'Em'),(2.07,4.14,'C'),(4.14,6.21,'Am'),(6.21,8.28,'D'),(8.28,10.34,'Em'),(10.34,12.41,'C'),(12.41,14.48,'Am'),(14.48,16.55,'D'),(16.55,18.62,'G'),(18.62,20.69,'C'),(20.69,22.76,'G'),(22.76,25.0,'G')]
def chord_at(t):
    for a,b,c in PROG:
        if a<=t<b: return CH[c]
    return CH['G']
def sec(t):
    if t<4.45: return 'hook'
    if t<5.03: return 'void'
    if t<10.8: return 'build'
    if t<18.0: return 'full'
    if t<18.1: return 'void'
    if t<20.63: return 'pay'
    if t<23.3: return 'cta'
    return 'out'
L=np.zeros(N);R=np.zeros(N);KK=[]
# pad (abre o filtro ao longo do arco)
for a,b,c in PROG:
    root,notes=CH[c]; d=min(b,END+0.3)-a; n=int((d+0.7)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.25)*np.clip((d+0.7-tt)/0.7,0,1)
    op={'hook':0.3,'void':0.1,'build':0.5,'full':1.0,'pay':1.0,'cta':0.7,'out':0.8}[sec(a+0.01)]
    if a>=23.2: env=env*1.8
    for k,m in enumerate(notes):
        sL=lp((saw(midi(m),n,0.004,k*.13)+saw(midi(m),n,-0.005,k*.31))*env*0.006,500+3200*op)
        sR=lp((saw(midi(m),n,-0.004,k*.57)+saw(midi(m),n,0.006,k*.77))*env*0.006,500+3200*op)
        add(L,sL,a);add(R,sR,a)
    add(L,np.sin(2*np.pi*midi(root-12 if root>36 else root)*tt)*env*0.03,a);add(R,np.sin(2*np.pi*midi(root-12 if root>36 else root)*tt)*env*0.03,a)
# bateria, baixo e arpejo no grid de semicolcheias
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
ARP=[0,2,1,3,2,1,3,0]
for k in range(int(END/S16)):
    t=k*S16; s_=sec(t); pos=k%16; bt_=pos%4==0; root,notes=chord_at(t)
    if s_=='hook':
        if pos in (0,6,10) : kick(t,.3)
        if pos%4==2: hat(t,.016)
        if pos%2==0: bass(t,root,.07)
        if t>=2.07 and pos in (4,12): clap(t,.04)
    elif s_=='void':
        pass
    elif s_=='build':
        r=(t-5.03)/5.8
        if bt_ : kick(t,.26+.08*r)
        if pos in (4,12): clap(t,.04+.03*r)
        if pos%2==0 and not pos%4==0: bass(t,root,.08)
        hat(t,.01+.012*r)
        if t>=7.5 and pos%2==0: pluck(t,notes[ARP[k%8]]+12,.02+.01*r,0.3)
    elif s_=='full':
        if bt_: kick(t,.36)
        if pos in (4,12): clap(t,.08)
        hat(t,.02*[1,.45,.75,.45][pos%4],90 if pos%4==2 else 160)
        if pos in (0,3,6,10,14): bass(t,root+(12 if pos==14 else 0),.12,.22)
        pluck(t,notes[ARP[k%8]]+12,.032,0.35)
    elif s_=='pay':
        if bt_: kick(t,.34)
        if pos in (4,12): clap(t,.08)
        hat(t,.02*[1,.5,.8,.5][pos%4])
        if pos in (0,3,6,10,14): bass(t,root,.12,.22)
        if pos%2==0: pluck(t,notes[ARP[(k//2)%8]]+12,.036,0.3)
    elif s_=='cta':
        if pos in (0,8): kick(t,.32)
        if pos in (4,12): clap(t,.06)
        if pos%2==0: bass(t,root,.1); hat(t,.016)
        if pos%2==0: pluck(t,notes[ARP[(k//2)%8]]+12,.03,0.3)
    else:
        if t<23.4 and pos in (0,8): kick(t,.26)
        if pos%2==0 and t<23.3: bass(t,root,.09)
        if t<23.5 and pos%2==0: pluck(t,notes[ARP[(k//2)%8]]+12,.034,0.3)
sc=np.ones(N)
for kt in KK:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.5*np.exp(-tt/0.09)[:j-i])
kickbus=np.zeros(N)
L*=sc;R*=sc
# dinâmica do arco: silêncio no "E só.", respiro antes do drop
dyn=np.ones(N)
def duck(a,b,g,ra=0.05,rb=0.15):
    m=np.clip((TT-a)/ra,0,1)*np.clip((b-TT)/rb,0,1); dyn[:]=dyn*(1-(1-g)*m)
duck(4.8,5.03,0.35,0.05,0.05); duck(17.95,18.1,0.3,0.03,0.04)
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
impact(0.0,.3);tick(0.0,.04,1800)
for i in range(5):
    a_=T['cs']+i*0.34; whoosh(a_-0.2,0.3,.04,500,3000,.8,(-.3,.3)[i%2]); thud(a_+0.12,.1+.01*i,80+8*i); tick(a_+0.2,.03,2000+120*i,(-.3,.3)[i%2])
for i in range(5): thud(T['gray']+(4-i)*0.09,.05,70)
bell(T['pill']+0.04,[64],.04,6,-.2);bell(T['pill']+0.2,[59],.04,6,-.2);thud(T['pill'],.2,55)
# cortina
for i in range(6): tick(T['curt']+i*0.045+0.2,.03,900+120*i,(-.5+i*.2))
riser(T['curt']-0.1,0.5,.06);whoosh(T['curt'],0.5,.12,300,6500,.5);impact(T['curtOut']-0.02,.34,36)
whoosh(T['curtOut'],0.5,.08,6000,500,.4)
# B
for tt_ in (5.6,5.85,6.15): thud(tt_+0.06,.1,90);tick(tt_+0.14,.03,2400)
whoosh(T['roll']-0.1,.3,.08,600,5000,.6);impact(T['roll']+0.04,.32,40);bell(T['roll']+0.05,[52,59,64],.05,3.2);tick(T['roll']+0.4,.03,1500)
# travelling lateral
whoosh(T['bOut']-0.05,.75,.13,300,6500,.5,.3);riser(T['bOut']-0.1,0.7,.05)
for i,s_ in enumerate(T['s']):
    if i>0: whoosh(s_-0.55,.55,.1,300,6000,.5,.3)
    thud(s_,.14,70+6*i);bell(s_+0.05,[64+3*i],.05,5,(-.2,.2)[i%2]);tick(s_+0.1,.03,2200)
pop(T['s'][0]-0.05,.08,620,-.3);pop(T['s'][0]+0.2,.09,880,.3)
for k in range(3): pop(T['s'][1]+0.15+k*0.14,.08,700+90*k,0)
for k in range(3): key(T['s'][2]-0.2+k*0.16,.05)
for i in range(6): key(T['s'][2]+0.55+i*0.06,.04)
for k in range(3): pop(T['s'][3]+0.15+k*0.2,.08,700+120*k,0)
bell(T['s'][3]+0.6,[67,71,74],.05,3,.2)
# iris
whoosh(T['irisC']-0.35,.38,.12,5200,300,.5);impact(T['irisO']+0.0,.4,34);whoosh(T['irisO'],.5,.1,400,6000,.5);bell(T['irisO']+0.05,[55,62,67,71],.055,2.6)
# D
impact(T['irisO']+0.05,.3,38);bell(T['irisO']+0.1,[67,71,74,79],.05,2.6)
for i in range(4): thud(T['irisO']+0.1+i*0.15,.08,95+8*i);bell(T['irisO']+0.25+i*0.15,[67+2*i],.04,6,(-.2,.2)[i%2])
thud(T['irisO']+0.5,.12,60);shimmer(T['irisO']+0.5,.8,.035)
# crane
riser(T['push']-0.3,0.3,.05);whoosh(T['push'],0.7,.13,300,6500,.5);impact(T['push']+0.9,.3,38)
for i in range(11): key(T['typ']+0.04+i*(0.8/11),.05)
pop(T['send'],.1,900,.3);bell(T['send']+0.03,[74,79],.05,5,.3);bell(T['send']+0.15,[83],.04,5,.3)
for i,dt in enumerate([-0.3,-0.14,0.06,0.24]): thud(T['sub']+dt+0.1,.06,110+8*i)
whoosh(T['logo']-0.3,.34,.035,600,3000,.8);bell(T['logo']+0.06,[55,62,67,71],.06,2.2);impact(T['logo']+0.06,.16,44);bell(23.0,[67,71,74,79],.045,2.6);shimmer(22.9,.5,.02)
FL=FL+0.16*fftconvolve(hp(FL,400),ir)[:N];FR=FR+0.16*fftconvolve(hp(FR,400),np.roll(ir,211))[:N]
# ---------- mix ----------
mus=np.sqrt(np.mean(((L+R)/2)**2));fxr=np.sqrt(np.mean(((FL+FR)/2)**2))
g=mus*10**(-2.5/20)/fxr
fade=np.clip(TT/0.02,0,1)*np.clip((END-TT)/0.3,0,1)
st=np.stack([(L+FL*g)*fade,(R+FR*g)*fade],1);st=np.tanh(st/np.max(np.abs(st))*1.6)/np.tanh(1.6)*0.86
wavfile.write('mix.wav',SR,(st[:int(END*SR)]*32767).astype(np.int16));print('ok',st.shape)
