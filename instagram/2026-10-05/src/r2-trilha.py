"""Reel 2 (05/10) "Imobiliária, lead pago" (tom +2: Si bemol) — trilha 100 BPM em Lá bemol maior (entra pelo relativo Fá menor).
Arco: tensão (Fm) -> conversa (Db) -> silêncio do "E só." -> build (Eb) -> drop no wipe (Ab) -> resolução na virada "quente" -> fecho.
SFX sincronizados a cada entrada de elemento (mesmos tempos do index.html)."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=23.4; N=int((END+0.4)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(53)
B=0.6
T=dict(tag=0.6,a2=1.5,venda=1.8,dive=2.52,hole=2.96,b=3.0,bb1=3.3,b2=4.2,dots=4.5,b3=5.4,pill=5.6,drop=6.86,c=7.2,c2=9.6,ckey=9.9,wipe=12.0,k=[13.2,13.5,13.8,14.1],sheen=14.7,e=16.2,flip=17.4,f=19.2,typ=19.5,send=20.4,sub=20.7,logo=21.3)
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
def add(buf,x,at,g=1.0):
    i=int(round(at*SR))
    if i<0: x=x[-i:];i=0
    j=min(len(buf),i+len(x))
    if j>i: buf[i:j]+=g*x[:j-i]
midi=lambda n:440*2**((n+2-69)/12)
def saw(f,n,d=0.0,ph=0.0): p=np.cumsum(np.full(n,f*(1+d))/SR)+ph; return 2*(p%1)-1
def tri(f,n): p=np.cumsum(np.full(n,f)/SR); return 2*np.abs(2*(p%1)-1)-1
# ---------- harmonia ----------
CH={'Fm':(41,[53,56,60,63]),'Db':(37,[53,56,61,65]),'Bbm':(34,[53,58,61,65]),'Eb':(39,[55,58,63,67]),'Ab':(44,[56,60,63,68])}
PROG=[(0,2.4,'Fm'),(2.4,4.8,'Db'),(4.8,7.2,'Bbm'),(7.2,9.6,'Db'),(9.6,12.0,'Eb'),(12.0,13.2,'Ab'),(13.2,14.4,'Fm'),(14.4,15.6,'Db'),(15.6,17.4,'Eb'),(17.4,19.2,'Ab'),(19.2,20.4,'Db'),(20.4,21.3,'Eb'),(21.3,24.0,'Ab')]
def chord_at(t):
    for a,b,c in PROG:
        if a<=t<b: return CH[c]
    return CH['Ab']
def sec(t):
    if t<3.0: return 'hook'
    if t<5.4: return 'chat'
    if t<7.2: return 'void'
    if t<12.0: return 'build'
    if t<19.2: return 'full'
    if t<21.3: return 'cta'
    return 'out'
L=np.zeros(N);R=np.zeros(N);KK=[]
# pad (abre o filtro ao longo do arco)
for a,b,c in PROG:
    root,notes=CH[c]; d=min(b,END+0.3)-a; n=int((d+0.7)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.25)*np.clip((d+0.7-tt)/0.7,0,1)
    op={'hook':0.22,'chat':0.3,'void':0.1,'build':0.45,'full':1.0,'cta':0.7,'out':0.8}[sec(a+0.01)]
    if a>=21.3: env=env*1.8
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
ARP=[0,1,3,2,1,3,2,0]
for k in range(int(END/S16)):
    t=k*S16; s=sec(t); pos=k%16; bt=pos%4==0; root,notes=chord_at(t)
    if s=='hook':
        if k in (0,4,12): kick(t,.3)
        if pos%2==0: bass(t,root,.07)
        if pos%4==2: hat(t,.014)
    elif s=='chat':
        if pos in (0,8) or k==20: kick(t,.3)
        if pos in (4,12): clap(t,.04)
        if pos%2==0: bass(t,root,.085); hat(t,.016*[1,.5][pos%4//2])
    elif s=='void':
        pass
    elif s=='build':
        r=(t-7.2)/4.8
        if t>=8.4 and bt: kick(t,.24+.1*r)
        elif t<8.4 and pos in (0,8): kick(t,.22)
        if pos%2==0: bass(t,root,.075+.04*r)
        hat(t,.007+.016*r)
        if t>=9.6 and pos in (4,12): clap(t,.03+.04*r)
        if t>=9.6 and pos%4==2: pluck(t,notes[ARP[(k//4)%8]]+12,.02+.012*r,0.3)
        if t>=11.4: clap(t,.02+.06*(t-11.4)/0.6)
        if t>=11.7: clap(t+S16/2,.03+.05*(t-11.7)/0.3)
    elif s=='full':
        suck=15.9<=t<16.2
        if bt and not suck: kick(t,.38)
        if pos in (4,12) and not suck: clap(t,.085)
        hat(t,.022*[1,.45,.75,.45][pos%4],90 if pos%4==2 else 160)
        if pos%2==0: bass(t,root+(12 if pos%8==6 else 0),.12)
        if not suck: pluck(t,notes[ARP[k%8]]+12,.03 if t<17.4 else .038,0.35)
    elif s=='cta':
        if pos in (0,8): kick(t,.33)
        if pos in (4,12): clap(t,.06)
        if pos%2==0: bass(t,root,.1); hat(t,.016)
        if pos%2==0: pluck(t,notes[ARP[(k//2)%8]]+12,.03,0.3)
    else:
        if t<22.9 and pos in (0,8): kick(t,.28)
        if pos%2==0 and t<22.8: bass(t,root,.09)
        if t<23.0 and pos%2==0: pluck(t,notes[ARP[(k//2)%8]]+12,.034,0.3)
sc=np.ones(N)
for kt in KK:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.5*np.exp(-tt/0.09)[:j-i])
kickbus=np.zeros(N)
L*=sc;R*=sc
# dinâmica do arco: silêncio no "E só.", respiro antes do drop
dyn=np.ones(N)
def duck(a,b,g,ra=0.05,rb=0.15):
    m=np.clip((TT-a)/ra,0,1)*np.clip((b-TT)/rb,0,1); dyn[:]=dyn*(1-(1-g)*m)
duck(5.4,7.1,0.3,0.03,0.3); duck(11.9,12.0,0.3,0.05,0.02); duck(15.95,16.2,0.45,0.1,0.02)
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
impact(0.0,.3);tick(0.0,.04,1800)
whoosh(T['tag']-0.32,0.36,.07,400,3000,.85);impact(T['tag'],.36,42);thud(T['tag'],.2);tick(T['tag']+0.16,.03,2600)
whoosh(T['a2']-0.44,0.4,.05,600,4000,.8);thud(T['a2']-0.24,.1);thud(T['a2']-0.12,.1);thud(T['a2']+0.06,.12);impact(T['venda']+0.04,.2,44);bell(T['venda']+0.04,[68,72,75],.055)
# mergulho pelo furo da etiqueta
riser(T['dive'],T['hole']-T['dive'],.05);whoosh(T['dive'],0.8,.13,300,7000,.56);impact(T['hole']+0.04,.3,34)
# B · conversa
pop(T['bb1']-0.06,.09,620,-.3);tick(T['b']+0.12,.025,1500)
whoosh(T['b2']-0.18,.2,.03,900,3000,.8);pop(T['b2']+0.04,.09,880,.3);tick(T['b2']+0.42,.03,3200,.3);tick(T['b2']+0.5,.03,3600,.3)
for i in range(5): tick(3.6+i*0.11,.014,1500+60*(i%3),.3)
for i in range(7): tick(T['dots']+0.02+i*0.12,.016,1100+60*(i%3),-.3)
for i in range(16): tick(5.75+1.1*(i/16)**0.7,.012+.0006*i,900,0.0)
thud(T['b3']-0.04,.26,55);impact(T['b3'],.22,30)
bell(T['pill']+0.04,[63],.03,7,-.2);bell(T['pill']+0.2,[58],.035,6,-.2)
# queda para C
whoosh(T['drop'],0.68,.1,5200,350,.45)
for i in range(3): thud(T['c']-0.02+i*0.1,.09+.02*i,80+12*i)
whoosh(T['c2']-0.44,.3,.04,2400,500,.5)
thud(T['c2']-0.02,.11,84);thud(T['c2']+0.2,.12,92)
impact(T['ckey']+0.04,.3,40);bell(T['ckey']+0.04,[72,75,80],.05);whoosh(T['ckey']+0.1,.42,.04,1500,6000,.7)
# wipe do símbolo
riser(T['wipe']-0.62,0.6,.07);whoosh(T['wipe']-0.32,0.62,.14,250,6500,.5);impact(T['wipe'],.42,36);bell(T['wipe'],[56,63,68],.04,3)
thud(T['wipe']+0.2,.08,90);thud(T['wipe']+0.6,.2,66);tick(T['wipe']+0.6,.03,2000)
# D · perguntas (cada chip = nota subindo)
for i,(tk,nt) in enumerate(zip(T['k'],[68,72,75,80])):
    whoosh(tk-0.2,.3,.045,700,4200,.8,(-.35,.35)[i%2]);thud(tk+0.1,.13,95+10*i);bell(tk+0.12,[nt],.055,6,(-.2,.2)[i%2]);tick(tk+0.24,.03,2400+200*i)
shimmer(T['sheen']-0.06,.7,.03)
# match cut -> etiqueta
whoosh(T['e']-0.34,.36,.09,4500,400,.75);thud(T['e'],.24,60);tick(T['e']+0.02,.04,1400)
thud(T['e']+0.2,.07,110);thud(T['e']+0.32,.07,118);thud(T['e']+0.64,.08,124)
# virada "quente"
whoosh(T['flip']-0.16,.34,.09,500,6000,.5);impact(T['flip']+0.1,.42,40);bell(T['flip']+0.12,[68,72,75,80],.06,2.6);shimmer(T['flip']+0.14,.9,.04)
thud(T['flip']+0.14,.12,100);thud(T['flip']+0.26,.12,108)
# viagem ao CTA
whoosh(T['f']-0.46,0.78,.12,350,6000,.55);thud(T['f'],.14,70)
pop(T['f']+0.34,.05,520)
for i in range(11): key(T['typ']+0.04+i*(0.8/11),.05)
pop(T['send'],.1,900,.3);bell(T['send']+0.03,[75,80],.05,5,.3);bell(T['send']+0.15,[84],.04,5,.3)
for i,dt in enumerate([-0.3,-0.14,0.06,0.24]): thud(T['sub']+dt+0.1,.06,110+8*i)
whoosh(T['logo']-0.3,.34,.035,600,3000,.8);bell(T['logo']+0.06,[56,63,68,72],.06,2.2);impact(T['logo']+0.06,.16,44);bell(22.2,[68,72,75,80],.045,2.6);shimmer(22.1,.5,.02);bell(22.8,[80,84],.03,3)
FL=FL+0.16*fftconvolve(hp(FL,400),ir)[:N];FR=FR+0.16*fftconvolve(hp(FR,400),np.roll(ir,211))[:N]
# ---------- mix ----------
mus=np.sqrt(np.mean(((L+R)/2)**2));fxr=np.sqrt(np.mean(((FL+FR)/2)**2))
g=mus*10**(-2.5/20)/fxr
fade=np.clip(TT/0.02,0,1)*np.clip((END-TT)/0.3,0,1)
st=np.stack([(L+FL*g)*fade,(R+FR*g)*fade],1);st=np.tanh(st/np.max(np.abs(st))*1.6)/np.tanh(1.6)*0.86
wavfile.write('mix.wav',SR,(st[:int(END*SR)]*32767).astype(np.int16));print('ok',st.shape)
