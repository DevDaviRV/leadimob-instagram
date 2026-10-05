"""Reel 2 (08/10) "Corretor, pare de abandonar quem já quer comprar." — trilha 96 BPM em Ré maior (abre no relativo Si menor).
Arranjo próprio (não é o do modelo de 03/10): piano elétrico em acordes, sub-baixo longo, bateria em meio-tempo (bumbo no 1, aro no 3),
shaker em colcheias. Arco: gancho contido (Bm) -> cartões pousando em notas que descem (G) -> envelhecimento: o relógio marca cada dia,
o filtro fecha e a música "esfria" (Em -> A sus) -> puxão -> groove completo em Ré quando a conversa é retomada -> sino no envio ->
fecho no CTA (G, A, D). SFX nos mesmos tempos do index.html."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; B=0.625; END=35*B; N=int((END+0.4)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(808)
b=lambda n:n*B
T=dict(truck=b(5.3),k=[b(6),b(7.5),b(9)],h2=b(10.5),tick=[b(11)+i*B/2 for i in range(6)],pull=b(15),hero=b(16),rew=b(16.25),q=b(19),typ=b(19.1),send=b(21),h3=b(23),step=b(24),morph=b(27),word=b(27)+0.3,sub=b(29.5),logo=b(31))
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
def bp(x,a,c): return sosfilt(butter(2,[a,c],'band',fs=SR,output='sos'),x)
def add(buf,x,at,g=1.0):
    i=int(round(at*SR))
    if i<0: x=x[-i:];i=0
    j=min(len(buf),i+len(x))
    if j>i: buf[i:j]+=g*x[:j-i]
midi=lambda n:440*2**((n-69)/12)
def tri(f,n,ph=0.0): p=np.cumsum(np.full(n,f)/SR)+ph; return 2*np.abs(2*(p%1)-1)-1
# ---------- harmonia (em tempos) ----------
CH={'Bm':(35,[59,62,66,69]),'G':(31,[59,62,67,71]),'Em':(28,[59,64,67,71]),'Asus':(33,[57,62,64,69]),'D':(38,[57,62,66,69]),'A':(33,[57,61,64,69]),'D9':(38,[57,64,66,69])}
PROG=[(0,6,'Bm'),(6,10.5,'G'),(10.5,13,'Em'),(13,16,'Asus'),(16,18,'D'),(18,20,'A'),(20,22,'Bm'),(22,24,'G'),(24,26,'D'),(26,28,'A'),(28,30,'G'),(30,31,'A'),(31,35.6,'D9')]
def chord_at(bt):
    for a,c,n in PROG:
        if a<=bt<c: return CH[n]
    return CH['D']
def sec(bt):
    if bt<6: return 'hook'
    if bt<10.5: return 'pile'
    if bt<16: return 'cold'
    if bt<27: return 'warm'
    if bt<31: return 'cta'
    return 'out'
L=np.zeros(N);R=np.zeros(N);KK=[]
# cama: triângulos filtrados (quente, sem serrote), um por acorde
for a,c,nm in PROG:
    root,notes=CH[nm]; d=min(b(c),END+0.3)-b(a); n=int((d+0.9)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.4)*np.clip((d+0.9-tt)/0.9,0,1)
    op={'hook':0.3,'pile':0.42,'cold':0.3,'warm':1.0,'cta':0.8,'out':0.9}[sec(a+0.01)]
    for k,m in enumerate(notes):
        f=midi(m)
        sL=lp((tri(f*1.003,n,k*.13)+.5*tri(f*2.002,n,k*.4))*env*0.011,400+2200*op)
        sR=lp((tri(f*0.997,n,k*.57)+.5*tri(f*1.998,n,k*.7))*env*0.011,400+2200*op)
        add(L,sL,b(a));add(R,sR,b(a))
    s=np.sin(2*np.pi*midi(root)*tt)*env*0.05*(0.7 if sec(a+0.01) in('hook','cold') else 1)
    add(L,s,b(a));add(R,s,b(a))
def kick(t,g=.36):
    n=int(0.45*SR);tt=np.arange(n)/SR;f=44+110*np.exp(-tt*30);k=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*7)*g
    k[:200]+=hp(rng.standard_normal(200),2000)*np.linspace(1,0,200)*g*.2
    add(L,k,t);add(R,k,t);KK.append(t)
def rim(t,g=.06):
    n=int(0.12*SR);tt=np.arange(n)/SR;c=(np.sin(2*np.pi*1750*tt)*.6+bp(rng.standard_normal(n),900,4200))*np.exp(-tt*55)*g
    add(L,c,t);add(R,c*.9,t+0.0005)
def shaker(t,g=.012):
    n=int(0.09*SR);tt=np.arange(n)/SR;h=hp(rng.standard_normal(n),6500)*np.minimum(1,tt/0.012)*np.exp(-tt*42)*g;add(L,h,t);add(R,h*.7,t)
def bass(t,note,g=.12,d=0.5):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note);x=(np.sin(2*np.pi*f*tt)+.3*lp(tri(f*2,n),500))*np.exp(-tt*2.6)*np.minimum(1,tt/0.006)*np.clip((d-tt)/0.05,0,1)*g;add(L,x,t);add(R,x,t)
def ep(t,notes,g=.035,dec=3.2,pan=0.0,cut=3200):
    """piano elétrico: senóide + parcial de sino curta, tremolo leve"""
    n=int(1.6*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes:
        f=midi(m);x+=(np.sin(2*np.pi*f*tt)+.5*np.sin(2*np.pi*f*2*tt)*np.exp(-tt*7)+.25*np.sin(2*np.pi*f*7.02*tt)*np.exp(-tt*22))*np.exp(-tt*dec)
    x=lp(x,cut)*np.minimum(1,tt/0.004)*g*(1+.12*np.sin(2*np.pi*4.6*tt))
    add(L,x*(1-pan),t);add(R,x*(1+pan),t)
# grade em colcheias
E8=B/2
for k in range(int(35/0.5)):
    bt=k*0.5; t=bt*B; s=sec(bt); pos=k%8; root,notes=chord_at(bt)     # pos 0..7 dentro do compasso
    if s=='hook':
        if k==0: kick(t,.32); ep(t,notes,.04,2.4)
        if k in (3,6): ep(t,[notes[1],notes[3]],.026,3.5,.2)
        if k in (0,5,8): bass(t,root,.1,.7)
        if k==8: kick(t,.26)
    elif s=='pile':
        if pos%2==0: shaker(t,.008)
    elif s=='cold':
        pass                                           # só o relógio (SFX) e a cama fechada
    elif s=='warm':
        if pos==0: kick(t,.36)
        if pos==3 and bt>=18: kick(t,.22)
        if pos==4: rim(t,.075)
        shaker(t,.013*(1.0 if pos%2==0 else .6))
        if pos in (0,3): bass(t,root,.13,.62)
        if pos==6: bass(t,root+12 if root<34 else root,.07,.3)
        if pos==0: ep(t,notes,.034,2.6)
        if pos==3: ep(t,notes[1:],.026,3.4,.25)
        if pos==6 and bt>=20: ep(t,[notes[3]+12],.02,4,-.3)
    elif s=='cta':
        if pos==0: kick(t,.33)
        if pos==4: rim(t,.06)
        if pos%2==0: shaker(t,.011)
        if pos in (0,3): bass(t,root,.12,.62)
        if pos==0: ep(t,notes,.034,2.6)
        if pos==3: ep(t,notes[1:],.024,3.4,-.25)
    else:
        if bt==31: kick(t,.3); bass(t,root,.13,1.6); ep(t,notes,.042,1.5)
        if bt in (33,): ep(t,[notes[2]+12,notes[3]+12],.022,2.2,.25)
sc=np.ones(N)
for kt in KK:
    i=int(kt*SR);n=int(0.32*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.42*np.exp(-tt/0.1)[:j-i])
L*=sc;R*=sc
# "esfriar": o filtro fecha ao longo do envelhecimento e reabre no puxão
def coldfilter(x):
    y=x.copy();a=int(T['h2']*SR);c=int((T['hero'])*SR);seg=x[a:c];nb=24;out=np.zeros(len(seg))
    for q in range(nb):
        i0=int(q*len(seg)/nb);i1=int((q+1)*len(seg)/nb);k=(q+.5)/nb
        fc=6000*(0.07**min(1,k/0.72)) if k<0.86 else 420*(14**((k-0.86)/0.14))
        w=np.zeros(len(seg));w[i0:i1]=1;w=np.convolve(w,np.hanning(801)/np.hanning(801).sum(),'same')
        out+=lp(seg,max(260,min(fc,9000)))*w
    y[a:c]=out;return y
L=coldfilter(L);R=coldfilter(R)
ir=rng.standard_normal(int(2.2*SR))*np.exp(-np.arange(int(2.2*SR))/SR*2.6);ir/=np.sqrt((ir**2).sum())
L=L+0.22*fftconvolve(hp(L,350),ir)[:N];R=R+0.22*fftconvolve(hp(R,350),np.roll(ir,131))[:N]
# ---------- SFX ----------
FL=np.zeros(N);FR=np.zeros(N)
def fx(x,at,g=1.0,pan=0.0): add(FL,x,at,g*(1-pan));add(FR,x,at,g*(1+pan))
def impact(at,g=.35,f0=38):
    n=int(1.3*SR);tt=np.arange(n)/SR;f=f0+90*np.exp(-tt*12);fx(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*3.2)*g+lp(rng.standard_normal(n),1400)*np.exp(-tt*16)*g*.3,at)
def thud(at,g=.16,f0=70):
    n=int(0.3*SR);tt=np.arange(n)/SR;f=f0+70*np.exp(-tt*40);fx(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*14)*g+bp(rng.standard_normal(n),300,2400)*np.exp(-tt*50)*g*.35,at)
def tick(at,g=.05,f=2200,pan=0.0): n=int(.04*SR);tt=np.arange(n)/SR;fx(np.sin(2*np.pi*f*tt)*np.exp(-tt*150)*g,at,1,pan)
def wood(at,g=.07,f=820,pan=0.0):
    n=int(.12*SR);tt=np.arange(n)/SR;fx((np.sin(2*np.pi*f*tt)+.5*np.sin(2*np.pi*f*2.7*tt)*np.exp(-tt*60))*np.exp(-tt*46)*np.minimum(1,tt/0.001)*g,at,1,pan)
def key(at,g=.05):
    n=int(.05*SR);tt=np.arange(n)/SR;fx(bp(rng.standard_normal(n),1800,5200)*np.exp(-tt*120)*g+np.sin(2*np.pi*(300+rng.uniform(-40,40))*tt)*np.exp(-tt*90)*g*.6,at,1,rng.uniform(-.2,.2))
def pop(at,g=.09,f=700,pan=0.0): n=int(.16*SR);tt=np.arange(n)/SR;fr=f*(1+.7*np.exp(-tt*55));fx(np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*34)*g,at,1,pan)
def whoosh(at,d=.5,g=.08,f0=500,f1=5200,peak=.6,pan=0.0):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;env=np.where(k<peak,(k/peak)**2.2,((1-k)/(1-peak))**1.6);x=rng.standard_normal(n);out=np.zeros(n);nb=12
    for q in range(nb):
        a=int(q*n/nb);e=int((q+1)*n/nb);fc=f0*(f1/f0)**((q+.5)/nb);out[a:e]=bp(x[a:e],fc*.6,min(fc*1.6,20000))[:e-a]
    fx(lp(out,9000)*env*g,at,1,pan)
def swell(at,d,notes,g=.03):
    """acorde invertido (cresce até o corte): puxa o cartão para a frente"""
    n=int(d*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes: x+=np.sin(2*np.pi*midi(m)*tt)+.4*np.sin(2*np.pi*midi(m)*2*tt)
    fx(x*(tt/d)**2.4*np.clip((d-tt)/0.02,0,1)*g,at)
def bell(at,notes,g=.05,dec=4.0,pan=0.0):
    n=int(1.8*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes:
        f=midi(m);x+=(np.sin(2*np.pi*f*tt)+.4*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt*8)+.2*np.sin(2*np.pi*f*3.02*tt)*np.exp(-tt*14))*np.exp(-tt*dec)
    fx(x*g*np.minimum(1,tt/0.002),at,1,pan)
def shimmer(at,d=.6,g=.03):
    n=int(d*SR);tt=np.arange(n)/SR;fx(hp(rng.standard_normal(n),7000)*np.sin(np.pi*tt/d)**2*g*(0.6+0.4*np.sin(2*np.pi*14*tt)),at)
# A · gancho: cada linha assenta com um toque seco
impact(0.0,.26,40);thud(0.0,.12,84)
thud(0.28,.14,74);tick(0.3,.03,1900)
for dt,f in [(0.68,96),(0.78,104),(0.92,112)]: thud(dt,.07,f)
# "ABANDONAR" esfria: nota que cai
n=int(0.9*SR);tt=np.arange(n)/SR;fq=midi(78)*(2**(-5/12*np.clip(tt/0.8,0,1)));fx(np.sin(2*np.pi*np.cumsum(fq)/SR)*np.sin(np.pi*np.clip(tt/0.9,0,1))**1.5*.022,1.9)
# deslocamento lateral
whoosh(T['truck']-0.05,0.72,.11,420,5200,.5,0.0)
# B · cartões pousando (notas descendo: Ré, Si, Sol)
for i,(tk,nt) in enumerate(zip(T['k'],[74,71,67])):
    whoosh(tk-0.26,.3,.035,900,3200,.85,(.25,-.25,.25)[i]);thud(tk-0.02,.2,78-8*i);ep(tk,[nt],.05,3.0,(.15,-.15,.15)[i]);tick(tk+0.04,.02,1700)
# título "sem retorno" e o relógio dos dias (desce e perde brilho)
thud(T['h2'],.12,70);thud(T['h2']+0.34,.14,62)
for i,tk in enumerate(T['tick']):
    wood(tk,.085-.006*i,880*(0.94**i),(-.2,.2)[i%2]);tick(tk,.02,1500-120*i)
bell(T['tick'][5]+0.02,[47],.05,2.2)                 # fundo do poço: Si grave
# puxão
swell(T['pull']-0.3,0.92,[57,64,69],.03);whoosh(T['pull'],0.64,.1,300,6200,.72)
# C · herói: pouso + contagem voltando a "2 dias"
impact(T['hero'],.34,40);thud(T['hero'],.16,72)
for i in range(5): wood(T['rew']+i*0.1,.05,560*(1.09**i),.25)
bell(T['rew']+0.52,[74],.04,5,.25)
# pergunta: campo abre, digitação, envio
pop(T['q']+0.03,.06,560,-.2)
for i in range(22): key(T['typ']+0.03+i*((T['send']-T['typ']-0.3)/22),.045)
whoosh(T['send']-0.2,.24,.05,700,5200,.85);pop(T['send'],.11,920,.2);bell(T['send']+0.02,[74,78,81],.07,2.4);bell(T['send']+0.16,[86],.04,4,.25);shimmer(T['send']+0.1,.8,.035);impact(T['send']+0.02,.22,44)
# próximo passo
for dt,f in [(0.0,96),(0.1,104),(0.24,112),(0.36,118)]: thud(T['h3']+dt+0.08,.06,f)
thud(T['step'],.13,84);bell(T['step']+0.08,[69,76],.05,4,-.2);tick(T['step']+0.48,.035,2600);tick(T['step']+0.56,.04,3100)
# cartão vira o campo do CTA
whoosh(T['morph']-0.1,.56,.09,3800,480,.4);thud(T['morph']+0.38,.2,62);pop(T['word']+0.1,.07,640)
bell(T['word']+0.12,[66,74],.045,3.5)
for dt,f in [(-0.2,100),(0.1,108),(0.26,116)]: thud(T['sub']+dt+0.08,.06,f)
whoosh(T['logo']-0.3,.34,.035,600,3000,.8);bell(T['logo']+0.04,[62,69,74,78],.06,2.0);impact(T['logo']+0.04,.16,44);shimmer(T['logo']+0.9,.6,.02);bell(b(33.5),[81,86],.03,3)
FL=FL+0.16*fftconvolve(hp(FL,400),ir)[:N];FR=FR+0.16*fftconvolve(hp(FR,400),np.roll(ir,211))[:N]
# ---------- mix ----------
mus=np.sqrt(np.mean(((L+R)/2)**2));fxr=np.sqrt(np.mean(((FL+FR)/2)**2))
g=mus*10**(-2.5/20)/fxr
fade=np.clip(TT/0.02,0,1)*np.clip((END-TT)/0.35,0,1)
st=np.stack([(L+FL*g)*fade,(R+FR*g)*fade],1);st=np.tanh(st/np.max(np.abs(st))*1.6)/np.tanh(1.6)*0.86
wavfile.write('mix.wav',SR,(st[:int(END*SR)]*32767).astype(np.int16));print('ok',st.shape)
