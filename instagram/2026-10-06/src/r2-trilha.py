"""Reel 2 (06/10) "Quanto mais leads, maior pode ser o prejuízo" — trilha 112 BPM em Ré maior (entra pelo relativo Si menor).
Arranjo próprio (diferente das trilhas de 03/10 e 05/10, que usavam Lá bemol/Si bemol a 100 BPM com palmas e arpejo reto):
marimba em padrão 3-3-2 que ganha densidade a cada lead que cai, tique-taque de relógio como percussão da cena do relógio,
estalo de madeira (rim) no lugar das palmas, vazio na íris, drop na metade do pan, resolução em Ré maior no CTA.
SFX sincronizados aos mesmos tempos do index.html."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=23.3; N=int((END+0.5)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(66)
BPM=112; B=60/BPM; BAR=4*B
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
CH={'Bm':(35,[54,57,62,66]),'G':(31,[55,59,62,67]),'D':(38,[54,57,62,66]),'A':(33,[52,57,61,64]),'Em':(40,[55,59,62,64])}
PROG=[(0,1,'Bm'),(1,2,'G'),(2,3,'D'),(3,4,'A'),(4,5,'Bm'),(5,6,'Em'),(6,7,'G'),(7,8,'D'),(8,9,'A'),(9,10,'D'),(10,12,'D')]
PROG=[(a*BAR,b*BAR,c) for a,b,c in PROG]
# (G no compasso 10 também pode ser G->D; aqui resolvemos direto em D)
def chord_at(t):
    for a,b,c in PROG:
        if a<=t<b: return CH[c]
    return CH['D']
def sec(t):
    if t<4.3: return 'hook'
    if t<8.4: return 'scale'
    if t<12.857: return 'clock'
    if t<19.1: return 'full'
    if t<20.9: return 'cta'
    return 'out'
L=np.zeros(N);R=np.zeros(N);KK=[]
# pad (abre o filtro ao longo do arco; fecha no relógio)
for a,b,c in PROG:
    root,notes=CH[c]; d=min(b,END+0.3)-a; n=int((d+0.7)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.3)*np.clip((d+0.7-tt)/0.7,0,1)
    op={'hook':0.3,'scale':0.5,'clock':0.18,'full':0.95,'cta':0.8,'out':0.9}[sec(a+0.01)]
    for k,m in enumerate(notes):
        sL=lp((saw(midi(m),n,0.004,k*.13)+saw(midi(m),n,-0.005,k*.31))*env*0.006,450+2800*op)
        sR=lp((saw(midi(m),n,-0.004,k*.57)+saw(midi(m),n,0.006,k*.77))*env*0.006,450+2800*op)
        add(L,sL,a);add(R,sR,a)
    sub=np.sin(2*np.pi*midi(root+12)*tt)*env*0.035
    add(L,sub,a);add(R,sub,a)
# bateria, baixo e marimba no grid de semicolcheias
S16=B/4
def kick(t,g=.34):
    n=int(0.4*SR);tt=np.arange(n)/SR;f=48+110*np.exp(-tt*32);k=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)*g
    k[:160]+=hp(rng.standard_normal(160),2200)*np.linspace(1,0,160)*g*.2
    add(L,k,t);add(R,k,t);KK.append(t)
def rim(t,g=.06):
    n=int(0.12*SR);tt=np.arange(n)/SR
    x=(np.sin(2*np.pi*1750*tt)*np.exp(-tt*85)*.7+bp(rng.standard_normal(n),1800,7000)*np.exp(-tt*70)*.5)*g
    add(L,x*.9,t);add(R,x,t+0.0005)
def hat(t,g=.02,dec=170):
    n=int(0.06*SR);tt=np.arange(n)/SR;h=hp(rng.standard_normal(n),9000)*np.exp(-tt*dec)*g;add(L,h*.7,t);add(R,h,t)
def shaker(t,g=.012):
    n=int(0.05*SR);tt=np.arange(n)/SR;h=bp(rng.standard_normal(n),5000,11000)*np.sin(np.pi*tt/0.05)*g;add(L,h,t);add(R,h*.8,t+0.001)
def bass(t,note,g=.1,d=0.3):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note);x=(np.sin(2*np.pi*f*tt)+.25*lp(saw(f,n),380))*np.exp(-tt*4.5)*np.minimum(1,tt/0.005)*g;add(L,x,t);add(R,x,t)
def marimba(t,note,g=.035,pan=0.0):
    n=int(0.55*SR);tt=np.arange(n)/SR;f=midi(note)
    x=(np.sin(2*np.pi*f*tt)*np.exp(-tt*7)+.45*np.sin(2*np.pi*f*4.0*tt)*np.exp(-tt*38)+.15*np.sin(2*np.pi*f*10*tt)*np.exp(-tt*90))*np.minimum(1,tt/0.002)*g
    for k,(dl,gg) in enumerate([(0,1),(0.375,.34),(0.75,.14)]): add(L,x*(1-pan*(1 if k%2==0 else -1))*gg,t+dl);add(R,x*(1+pan*(1 if k%2==0 else -1))*gg,t+dl)
ARPS=[0,3,6,8,11,14]            # 3-3-2 (tresillo) em semicolcheias
NOTE_I=[0,2,1,3,2,1]
for k in range(int(END/S16)):
    t=k*S16; s=sec(t); pos=k%16; root,notes=chord_at(t)
    a_i=ARPS.index(pos) if pos in ARPS else -1
    if s=='hook':
        if pos==0: kick(t,.26)
        if pos%4==2 and t>1.0: hat(t,.012)
        if t>2.1 and pos in (0,10): kick(t,.24)
        if pos in (0,6,8) and t>1.0: bass(t,root,.07)
    elif s=='scale':
        pro=(t-4.3)/4.2
        if pos in (0,10) or (pos==8 and pro>.4): kick(t,.28)
        if pos in (4,12) and pro>.2: rim(t,.035+.03*pro)
        if pos in (0,6,8,14): bass(t,root,.08+.03*pro)
        if pos%2==1 or pro>.5: hat(t,.006+.014*pro)
        if a_i>=0 and t>=4.7: marimba(t,notes[NOTE_I[a_i]]+12+(12 if (k//16)%2 and a_i==5 else 0),.016+.022*pro,.3)
    elif s=='clock':
        if t>=11.2 and pos in (0,8): kick(t,.14+.14*(t-11.2)/1.6)
        if t>=11.6 and pos%4==2: hat(t,.012)
    elif s=='full':
        if pos in (0,6,10) or (pos==8 and False): kick(t,.38)
        if pos in (4,12): rim(t,.08)
        hat(t,.02*[1,.4,.8,.4][pos%4],95 if pos%4==2 else 170)
        shaker(t+S16/2,.01)
        if pos in (0,3,6,8,11,14): bass(t,root+(12 if pos==14 else 0),.12)
        if a_i>=0: marimba(t,notes[NOTE_I[a_i]]+12,.03 if t<17.2 else .036,.35)
    elif s=='cta':
        if pos in (0,6,10): kick(t,.32)
        if pos in (4,12): rim(t,.06)
        if pos%2==0: hat(t,.014)
        if pos in (0,6,8,14): bass(t,root,.1)
        if a_i>=0: marimba(t,notes[NOTE_I[a_i]]+12,.03,.3)
    else:
        if t<22.2 and pos in (0,10): kick(t,.26)
        if t<22.5 and pos in (0,8): bass(t,root,.09)
        if t<22.7 and a_i in (0,2,4): marimba(t,notes[NOTE_I[a_i]]+12,.03,.3)
sc=np.ones(N)
for kt in KK:
    i=int(kt*SR);n=int(0.28*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.45*np.exp(-tt/0.09)[:j-i])
L*=sc;R*=sc
# dinâmica do arco: íris (esvazia), relógio (cama fina), respiro antes do drop
dyn=np.ones(N)
def duck(a,b,g,ra=0.05,rb=0.15):
    m=np.clip((TT-a)/ra,0,1)*np.clip((b-TT)/rb,0,1); dyn[:]=dyn*(1-(1-g)*m)
duck(8.4,9.0,0.12,0.45,0.1); duck(9.0,12.4,0.45,0.05,0.2); duck(12.45,12.84,0.25,0.05,0.02)
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
def whoosh(at,d=.5,g=.08,f0=500,f1=5200,peak=.6,pan0=0.0,pan1=None):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;env=np.where(k<peak,(k/peak)**2.2,((1-k)/(1-peak))**1.6);x=rng.standard_normal(n);out=np.zeros(n);nb=12
    for b in range(nb):
        a=int(b*n/nb);e=int((b+1)*n/nb);fc=f0*(f1/f0)**((b+.5)/nb);out[a:e]=bp(x[a:e],fc*.6,min(fc*1.6,20000))[:e-a]
    y=lp(out,9000)*env*g
    if pan1 is None: fx(y,at,1,pan0)
    else:
        pn=np.linspace(pan0,pan1,n);add(FL,y*(1-pn),at);add(FR,y*(1+pn),at)
def riser(at,d,g=.06):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;f=200*(8**k);fx((np.sin(2*np.pi*np.cumsum(f)/SR)*.35+hp(rng.standard_normal(n),1500)*k)*k**2*g,at)
def bell(at,notes,g=.05,dec=4.0,pan=0.0):
    n=int(1.6*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes:
        f=midi(m);x+=(np.sin(2*np.pi*f*tt)+.4*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt*8)+.2*np.sin(2*np.pi*f*3.02*tt)*np.exp(-tt*14))*np.exp(-tt*dec)
    fx(x*g*np.minimum(1,tt/0.002),at,1,pan)
def shimmer(at,d=.6,g=.03):
    n=int(d*SR);tt=np.arange(n)/SR;fx(hp(rng.standard_normal(n),7000)*np.sin(np.pi*tt/d)**2*g*(0.6+0.4*np.sin(2*np.pi*14*tt)),at)
def tock(at,g=.05,hi=True):
    n=int(.06*SR);tt=np.arange(n)/SR;f=2300 if hi else 1650
    fx((np.sin(2*np.pi*f*tt)+.5*np.sin(2*np.pi*f*2.7*tt))*np.exp(-tt*120)*g+bp(rng.standard_normal(n),2500,6000)*np.exp(-tt*200)*g*.5,at,1,0.1 if hi else -0.1)
PEN=[74,78,81,85,86,90]   # Ré maior pentatônica subindo (pílulas que entram no funil)
# A · funil: cada lead que cai vira uma nota (cada vez mais rápido)
impact(0.0,.28,40);tick(0.02,.04,1800)
whoosh(-0.0+0.02,0.4,.05,500,3500,.7)
for i,ta in enumerate([0.45,0.82,1.1,1.33,1.52,1.68]): pop(ta,.07,520+40*i,(-.25,.25)[i%2]);bell(ta+0.02,[PEN[i]-12],.032,7,(-.3,.3)[i%2])
for ta in [1.85,2.05,2.25]: thud(ta,.07,120);tick(ta+0.02,.03,1200)
whoosh(1.62,.3,.05,500,3500,.8);whoosh(2.1,.36,.06,800,4500,.8)
for tx,dr in [(2.1,-1),(2.3,1),(2.5,-1)]: whoosh(tx,0.4,.03,1200,300,.4,0.4*dr)
impact(2.1,.34,38);bell(2.1,[62,66,69],.045,3)
# gota pelo bico + queda (crane)
for i,tt_ in enumerate([3.2,3.3,3.4]): pop(tt_,.05,900-120*i)
riser(3.55,0.85,.06);whoosh(3.85,0.55,.12,300,7000,.6,0,0);impact(4.4,.26,44);bell(4.42,[74,78,81],.05,4)
# B · balança
whoosh(4.5,.3,.05,600,3500,.8);tick(4.57,.03,2000)
for i,tb in enumerate([5.62,5.92,6.17,6.37,6.53]): thud(tb,.1,150-8*i);pop(tb+0.04,.05,500+30*i,-.35);tick(tb+0.1,.02,1400)
bell(5.27,[86],.05,6,.35);pop(5.25,.06,900,.4)
whoosh(6.45,.3,.05,600,3500,.8)
thud(7.1,.18,60);bell(7.12,[59,63],.04,5,-.1);tick(7.3,.03,1100)
# íris: fecha (sucção) e abre
riser(8.4,0.5,.07);whoosh(8.35,0.6,.1,5500,300,.5)
thud(8.9,.18,50);bell(8.92,[69,73,76],.05,3);whoosh(8.9,0.4,.08,400,6000,.5)
# C · relógio: tique-taque
ti=9.1;j=0
while ti<12.5:
    tock(ti,.045 if j%2==0 else .036,j%2==0);ti+=B/2;j+=1
whoosh(8.95,.3,.04,700,3500,.8);bell(9.55,[74,79],.05,6,.2);bell(9.69,[79,83],.04,6,.2);pop(9.55,.06,800,.3)
thud(10.9,.1,70);thud(11.1,.12,60);bell(11.12,[59],.03,5)
riser(11.8,1.05,.08);whoosh(12.2,.66,.07,400,6000,.5)
# pan (esquerda -> direita) + drop no meio
whoosh(12.5,0.45,.13,300,7000,.5,-.6,.6);impact(12.857,.4,38)
for ts,nt in zip([12.75,13.03,13.37,13.67],[62,66,69,74]): whoosh(ts-0.05,.22,.04,800,3500,.8,.25);thud(ts+0.08,.12,100+8*(nt-62)/4);bell(ts+0.1,[nt+12],.04,6,.2)
impact(13.75,.28,36)
# S4 -> S5 (lift)
whoosh(15.7,.4,.07,3000,300,.4);thud(16.0,.08,70)
for ts in [15.9,15.95,16.0,16.05,16.1,16.15,16.2]: tick(ts+0.04,.025,1500+100*(len(str(ts))%3))
whoosh(16.0,.3,.05,700,3500,.8);thud(16.3,.12,80);thud(16.42,.12,90);thud(16.54,.12,100)
for tm in [16.9,17.55,18.05,17.0,17.08]: whoosh(tm-0.04,.34,.04,900,4000,.7,0.1);tick(tm+0.3,.03,1800)
bell(18.22,[74,78,81,86],.06,2.6);shimmer(18.24,.8,.04);thud(18.22,.12,100);pop(18.25,.06,1000,.2)
# rise -> CTA
riser(19.1,.45,.07);whoosh(19.1,.45,.12,350,6000,.55);thud(19.55,.14,70)
impact(19.2,.32,40)
pop(19.4,.06,520)
for i in range(11): key(19.75+i*(0.8/11),.05)
pop(20.7,.1,900,.3);bell(20.73,[74,81],.05,5,.3);bell(20.85,[86],.04,5,.3)
for i,dt in enumerate([-0.05,0.07,0.28,0.42]): thud(21.0+dt+0.1,.05,110+8*i)
whoosh(20.95,.3,.04,700,3500,.8);whoosh(21.2,.3,.04,700,3500,.8)
whoosh(21.4,.34,.035,600,3000,.8);bell(21.65,[50,57,62,66],.06,2.2);impact(21.65,.16,44);bell(22.2,[74,78,81,86],.045,2.6);shimmer(22.1,.5,.02)
FL=FL+0.16*fftconvolve(hp(FL,400),ir)[:N];FR=FR+0.16*fftconvolve(hp(FR,400),np.roll(ir,211))[:N]
# ---------- mix ----------
mus=np.sqrt(np.mean(((L+R)/2)**2));fxr=np.sqrt(np.mean(((FL+FR)/2)**2))
g=mus*10**(-2.5/20)/fxr
fade=np.clip(TT/0.02,0,1)*np.clip((END-TT)/0.3,0,1)
st=np.stack([(L+FL*g)*fade,(R+FR*g)*fade],1);st=np.tanh(st/np.max(np.abs(st))*1.6)/np.tanh(1.6)*0.86
wavfile.write('mix.wav',SR,(st[:int(END*SR)]*32767).astype(np.int16));print('ok',st.shape)
