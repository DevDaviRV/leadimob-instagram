"""Reel 2 (10/10) "Imobiliária, quem responde o formulário da Meta?" · trilha 116 BPM em Dó sustenido menor (resolve em Mi maior no CTA).
Arranjo próprio: marimba de FM em arpejo, pad de triângulos filtrado, baixo em contratempo (house leve), shaker em semicolcheias.
Arco: gancho contido (C#m/A) com relógio tiquetaqueando no "Sem resposta" -> foco desfocado (sucção grave) ->
conversa no WhatsApp (E/B/C#m, groove sobe a cada mensagem; enviada = nota aguda, recebida = nota grave) -> painel diagonal ->
dono no funil (A/E, groove cheio, checks em sino) -> linha da jornada -> tese em meio-tempo (B suspenso) -> recolhe no ponto, respiro -> CTA (E).
SFX presos aos mesmos tempos do index.html."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=22.6; N=int((END+0.4)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(1010)
B=60/116; S16=B/4
T=dict(fm=-0.4,a3=0.2,a4=0.4,pill=1.15,pr=1.8,pr2=2.15,rf=[4.15,4.45,4.8],B=4.45,b1=4.55,ch=4.6,m=[4.95,7.05,7.85,8.6,9.35],b3=6.85,dw=[10.45,10.8,11.15],C=10.8,c1=10.9,kc=11.05,stp=11.7,cp=[12.0,12.25,12.5],own=13.0,cpl=13.75,cOut=15.15,D=15.6,d=[15.62,15.82,16.05],dOut=18.15,dot=18.45,F=18.45,f2=18.55,f1=18.7,logo=18.9,typ=19.0,send=19.85,sub=20.15,sheen=20.9)
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
def add(buf,x,at,g=1.0):
    i=int(round(at*SR))
    if i<0: x=x[-i:];i=0
    j=min(len(buf),i+len(x))
    if j>i: buf[i:j]+=g*x[:j-i]
midi=lambda n:440*2**((n-69)/12)
def tri(f,n,ph=0.0): p=np.cumsum(np.full(n,f)/SR)+ph; return 2*np.abs(2*(p%1)-1)-1
# ---------- harmonia ----------
CH={'C#m':(37,[56,61,64,68]),'A':(33,[57,61,64,69]),'E':(40,[56,59,64,68]),'B':(35,[54,59,63,66]),'Bsus':(35,[54,59,64,66]),'F#m':(42,[57,61,66,69])}
PROG=[(0,2.2,'C#m'),(2.2,4.45,'A'),(4.45,6.85,'E'),(6.85,8.6,'B'),(8.6,10.8,'C#m'),(10.8,13.0,'A'),(13.0,15.6,'E'),(15.6,17.0,'Bsus'),(17.0,18.45,'B'),(18.45,23.0,'E')]
def chord_at(t):
    for a,b,c in PROG:
        if a<=t<b: return CH[c]
    return CH['E']
def sec(t):
    if t<4.45: return 'hook'
    if t<10.8: return 'chat'
    if t<15.6: return 'full'
    if t<18.45: return 'tese'
    return 'cta'
L=np.zeros(N);R=np.zeros(N);KK=[]
for a,b,c in PROG:
    root,notes=CH[c]; d=min(b,END+0.3)-a; n=int((d+0.8)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.35)*np.clip((d+0.8-tt)/0.8,0,1)
    op={'hook':0.25,'chat':0.45,'full':0.8,'tese':0.6,'cta':0.7}[sec(a+0.01)]
    for k,m in enumerate(notes):
        vib=1+0.003*np.sin(2*np.pi*(4.5+k*.3)*tt)
        sL=lp(tri(midi(m),n,k*.13)*vib*env*0.012,400+2600*op); sR=lp(tri(midi(m)*1.003,n,k*.41)*env*0.012,400+2600*op)
        add(L,sL,a);add(R,sR,a)
    sub=np.sin(2*np.pi*midi(root)*tt)*env*0.028;add(L,sub,a);add(R,sub,a)
def kick(t,g=.34):
    n=int(0.35*SR);tt=np.arange(n)/SR;f=50+110*np.exp(-tt*30);k=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)*g
    add(L,k,t);add(R,k,t);KK.append(t)
def clap(t,g=.07):
    n=int(0.2*SR);tt=np.arange(n)/SR;c=bp(rng.standard_normal(n),1300,6000)*(np.exp(-tt*28)+.5*np.exp(-np.maximum(0,tt-.01)*40)*(tt>.01))*g
    add(L,c*.9,t);add(R,c,t+0.0005)
def shaker(t,g=.012):
    n=int(0.07*SR);tt=np.arange(n)/SR;h=bp(rng.standard_normal(n),5000,12000)*np.sin(np.pi*np.minimum(1,tt/0.07))**2*g;add(L,h,t);add(R,h*.7,t)
def bass(t,note,g=.1,d=0.2):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note);x=(np.sin(2*np.pi*f*tt)+.25*np.sin(2*np.pi*2*f*tt))*np.exp(-tt*7)*np.minimum(1,tt/0.006)*g;add(L,x,t);add(R,x,t)
def marimba(t,note,g=.04,pan=0.0):
    n=int(0.7*SR);tt=np.arange(n)/SR;f=midi(note);mod=np.sin(2*np.pi*f*4*tt)*2.2*np.exp(-tt*30)
    x=np.sin(2*np.pi*f*tt+mod)*np.exp(-tt*7.5)*np.minimum(1,tt/0.002)*g
    for k,(dl,gg) in enumerate([(0,1),(B*0.75,.35),(B*1.5,.15)]):
        s=pan*(1 if k%2==0 else -1);add(L,x*(1-s)*gg,t+dl);add(R,x*(1+s)*gg,t+dl)
ARP=[0,2,1,3,2,1,3,0]
for k in range(int(END/S16)+1):
    t=k*S16; s=sec(t); pos=k%16; root,notes=chord_at(t)
    if s=='hook':
        if t>=1.8 and pos==0: kick(t,.26)
        if t>=2.2 and pos in (6,14): bass(t,root+12,.06)
        if t>=0.3 and t<4.1 and pos%4==2: shaker(t,.006)
        if t<4.1 and pos%4==0 and t>0.1: marimba(t,notes[ARP[(k//4)%8]]+12,.022,.25)
    elif s=='chat':
        r=(t-4.45)/6.35
        if pos%4==0: kick(t,.24+.08*r)
        if pos%4==2: bass(t,root+12,.07+.03*r)
        if pos%2==1 or r>.5: shaker(t,.007+.008*r)
        if pos%2==0: marimba(t,notes[ARP[(k//2)%8]]+12,.02+.01*r,.3)
    elif s=='full':
        if pos%4==0: kick(t,.36)
        if pos in (4,12): clap(t,.075)
        if pos%4==2: bass(t,root+12,.11)
        if pos%4==3: bass(t,root+12,.05,.12)
        shaker(t,.016*[1,.5,.8,.5][pos%4])
        marimba(t,notes[ARP[k%8]]+12+(12 if pos in (6,14) else 0),.028,.35)
    elif s=='tese':
        if t<18.1 and pos==0: kick(t,.3)
        if t<18.1 and pos in (8,): clap(t,.05)
        if pos%8==0 and t<18.1: bass(t,root,.11,.5)
        if pos%4==0 and t<18.0: marimba(t,notes[ARP[(k//4)%8]]+24,.024,.3)
    else:
        if t>=18.45 and t<21.6 and pos%4==0: kick(t,.3)
        if t<21.6 and pos in (4,12): clap(t,.05)
        if t<21.8 and pos%4==2: bass(t,root+12,.09)
        if t<21.8: shaker(t,.011*[1,.5,.8,.5][pos%4])
        if t<22.0 and pos%2==0: marimba(t,notes[ARP[(k//2)%8]]+12,.026,.3)
sc=np.ones(N)
for kt in KK:
    i=int(kt*SR);n=int(0.28*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.45*np.exp(-tt/0.08)[:j-i])
L*=sc;R*=sc
dyn=np.ones(N)
def duck(a,b,g,ra=0.05,rb=0.15):
    m=np.clip((TT-a)/ra,0,1)*np.clip((b-TT)/rb,0,1); dyn[:]=dyn*(1-(1-g)*m)
duck(T['rf'][0],T['rf'][1]+0.05,0.35,0.15,0.1); duck(T['dOut']+0.05,T['F'],0.15,0.1,0.02)
L*=dyn;R*=dyn
ir=rng.standard_normal(int(2.2*SR))*np.exp(-np.arange(int(2.2*SR))/SR*2.6);ir/=np.sqrt((ir**2).sum())
L=L+0.22*fftconvolve(hp(L,350),ir)[:N];R=R+0.22*fftconvolve(hp(R,350),np.roll(ir,131))[:N]
# ---------- SFX ----------
FL=np.zeros(N);FR=np.zeros(N)
def fx(x,at,g=1.0,pan=0.0): add(FL,x,at,g*(1-pan));add(FR,x,at,g*(1+pan))
def impact(at,g=.3,f0=38):
    n=int(1.2*SR);tt=np.arange(n)/SR;f=f0+90*np.exp(-tt*12);fx(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*3.4)*g+lp(rng.standard_normal(n),1400)*np.exp(-tt*16)*g*.25,at)
def thud(at,g=.14,f0=70):
    n=int(0.3*SR);tt=np.arange(n)/SR;f=f0+70*np.exp(-tt*40);fx(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*14)*g+bp(rng.standard_normal(n),300,2400)*np.exp(-tt*50)*g*.3,at)
def tick(at,g=.04,f=2200,pan=0.0): n=int(.035*SR);tt=np.arange(n)/SR;fx(np.sin(2*np.pi*f*tt)*np.exp(-tt*170)*g+bp(rng.standard_normal(n),3000,8000)*np.exp(-tt*300)*g*.4,at,1,pan)
def key(at,g=.045):
    n=int(.05*SR);tt=np.arange(n)/SR;fx(bp(rng.standard_normal(n),1800,5200)*np.exp(-tt*120)*g+np.sin(2*np.pi*(300+rng.uniform(-40,40))*tt)*np.exp(-tt*90)*g*.6,at,1,rng.uniform(-.2,.2))
def pop(at,g=.08,f=700,pan=0.0): n=int(.16*SR);tt=np.arange(n)/SR;fr=f*(1+.7*np.exp(-tt*55));fx(np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*34)*g,at,1,pan)
def whoosh(at,d=.5,g=.08,f0=500,f1=5200,peak=.6,pan=0.0):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;env=np.where(k<peak,(k/peak)**2.2,((1-k)/(1-peak))**1.6);x=rng.standard_normal(n);out=np.zeros(n);nb=12
    for b in range(nb):
        a=int(b*n/nb);e=int((b+1)*n/nb);fc=f0*(f1/f0)**((b+.5)/nb);out[a:e]=bp(x[a:e],fc*.6,min(fc*1.6,20000))[:e-a]
    fx(lp(out,9000)*env*g,at,1,pan)
def riser(at,d,g=.05):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;f=220*(6**k);fx((np.sin(2*np.pi*np.cumsum(f)/SR)*.35+hp(rng.standard_normal(n),2000)*k)*k**2*g,at)
def bell(at,notes,g=.045,dec=4.0,pan=0.0):
    n=int(1.6*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes:
        f=midi(m);x+=(np.sin(2*np.pi*f*tt)+.4*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt*8)+.2*np.sin(2*np.pi*f*3.02*tt)*np.exp(-tt*14))*np.exp(-tt*dec)
    fx(x*g*np.minimum(1,tt/0.002),at,1,pan)
def shimmer(at,d=.6,g=.025):
    n=int(d*SR);tt=np.arange(n)/SR;fx(hp(rng.standard_normal(n),7000)*np.sin(np.pi*tt/d)**2*g*(0.6+0.4*np.sin(2*np.pi*14*tt)),at)
def suck(at,d=.32,g=.1):  # sucção reversa (ruído que cresce e corta seco)
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;x=rng.standard_normal(n);y=lp(x,900)*(1-k)+hp(x,1500)*k*.6;fx(y*k**3*g,at)
# A · gancho
impact(0.0,.2,40);whoosh(0.0,0.2,.05,500,4200,.7,.3);thud(0.02,.1)
pop(T['fm']+0.45,.06,680,.3);whoosh(T['a3']-0.25,.3,.05,400,3500,.8);thud(T['a3'],.1,72);thud(T['a4'],.12,64)
thud(T['pill']-0.02,.14,58);bell(T['pill']+0.03,[61],.035,6,-.2)
for i in range(int((T['rf'][0]-T['pill']-0.2)/B)+1): tick(T['pill']+0.25+i*B,.03,(1600,1250)[i%2],-.2)
whoosh(T['pr']-0.2,.3,.05,600,3500,.7);thud(T['pr'],.08,82);thud(T['pr2']+0.16,.1,76)
# foco A->B
whoosh(T['rf'][0]-0.05,.45,.09,4000,300,.5);impact(T['rf'][1],.22,36);shimmer(T['rf'][1]+0.05,.5,.02)
# B · conversa
thud(T['b1'],.1,70);thud(T['b1']+0.22,.1,74);whoosh(T['ch']-0.1,.35,.04,600,3000,.8)
for i,tm in enumerate(T['m']):
    if i in (2,4): pop(tm,.07,520,-.25);bell(tm+0.02,[56 if i==2 else 59],.03,7,-.25)
    else: pop(tm,.08,980,.25);bell(tm+0.02,[[73],[76],[80]][[0,1,3].index(i)],.035,6,.25);whoosh(tm-0.12,.16,.03,1500,7000,.8,.25)
whoosh(T['b3']-0.35,.3,.05,600,3500,.7);thud(T['b3'],.1,70);thud(T['b3']+0.12,.12,64)
# painel diagonal B->C
whoosh(T['dw'][0]-0.1,.75,.12,300,6500,.45,-.3);impact(T['dw'][1],.24,38);thud(T['c1'],.1,70);thud(T['c1']+0.24,.1,74)
# C · dono
pop(T['kc']+0.1,.06,560);whoosh(T['stp'],.5,.035,700,3200,.7);pop(T['stp']+0.5,.09,1050,.2);bell(T['stp']+0.52,[76,80],.045,5,.2)
for i,tc in enumerate(T['cp']): pop(tc,.06,800+110*i,(-.2,0,.2)[i])
pop(T['own'],.09,620,-.2);bell(T['own']+0.02,[64],.035,6,-.2)
for i in range(12): key(T['own']+0.17+i*(0.45/12),.03)
impact(T['cpl'],.24,42);pop(T['cpl']+0.02,.09,1100,.2);bell(T['cpl']+0.04,[68,71,76],.055,3.2,.1);shimmer(T['cpl']+0.05,.7,.03)
# linha C->D
riser(T['cOut']-0.25,0.5,.05);whoosh(T['cOut']-0.1,.5,.11,300,6000,.6);impact(T['D'],.26,38)
# D · tese
for i,td in enumerate(T['d']): thud(td+0.02,.11+.01*i,70+6*i)
bell(T['d'][2]+0.15,[59,64,66,71],.05,2.5);shimmer(T['d'][2]+0.2,.8,.025)
# recolhe no ponto -> CTA
suck(T['dOut']-0.12,.32,.12);tick(T['dOut']+0.22,.05,3000);impact(T['F'],.28,40)
whoosh(T['f2']-0.05,.3,.05,800,5000,.7);thud(T['f1'],.12,80);bell(T['logo']+0.05,[52,59,64,68],.055,2.2)
for i in range(10): key(T['typ']+0.03+i*(0.6/10),.045)
pop(T['send'],.1,900,.3);bell(T['send']+0.03,[76,80],.05,5,.3);bell(T['send']+0.15,[83],.035,5,.3);impact(T['send'],.18,44)
for i,dt in enumerate([-0.3,-0.14,0.06,0.24]): thud(T['sub']+dt+0.1,.055,110+8*i)
bell(T['sheen']-0.1,[64,68,71,76],.045,2.6);shimmer(T['sheen'],.6,.02);bell(21.9,[76,80,83],.03,2.5)
FL=FL+0.15*fftconvolve(hp(FL,400),ir)[:N];FR=FR+0.15*fftconvolve(hp(FR,400),np.roll(ir,211))[:N]
# ---------- mix ----------
mus=np.sqrt(np.mean(((L+R)/2)**2));fxr=np.sqrt(np.mean(((FL+FR)/2)**2))
g=mus*10**(-2.5/20)/fxr
fade=np.clip(TT/0.02,0,1)*np.clip((END-TT)/0.35,0,1)
st=np.stack([(L+FL*g)*fade,(R+FR*g)*fade],1);st=np.tanh(st/np.max(np.abs(st))*1.6)/np.tanh(1.6)*0.86
wavfile.write('mix.wav',SR,(st[:int(END*SR)]*32767).astype(np.int16));print('ok',st.shape)
