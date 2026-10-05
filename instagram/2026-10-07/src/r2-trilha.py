"""Reel 2 (07/10) "Imobiliária, você não perde a venda quando o lead chega. Perde depois." — trilha 96 BPM, Mi menor -> Sol maior.
Arco: gancho contido (Em, sem bateria) -> descida pela linha do tempo (Em, D, C, Bm: uma nota de sino mais grave e mais
abafada a cada etapa que apaga, baixo rareando) -> quase silêncio quando o lead esfria -> recuo para a linha inteira (Am, sem bateria)
-> virada (D): quatro sinos subindo, um por etapa que acende -> groove em meio-tempo (G, Em, C) -> fecho em Sol no logo.
Mesma mixagem do modelo (reverb curto, sidechain, SFX 2,5 dB abaixo da música); andamento, tonalidade, timbres e arranjo novos.
SFX nos mesmos tempos do index.html."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=694/30; N=int((END+0.4)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(710)
B=0.625
TN=[4.0625,5.9375,7.8125,9.6875]; HOP=0.46
T=dict(n0=0.95,h2=1.875,dead=10.2,pb=11.3,over=11.9,turn=14.375,L=[15.0,15.3125,15.625,15.9375],cta=18.125,typ=18.825,send=19.825,sub=20.075,logo=20.625)
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
def tri(f,n,ph=0.0): p=np.cumsum(np.full(n,f)/SR)+ph; return 2*np.abs(2*(p%1)-1)-1
# ---------- harmonia (raiz do baixo, notas do pad) ----------
CH={'Em':(40,[52,59,64,67]),'D':(38,[54,57,62,66]),'C':(36,[52,55,60,64]),'Bm':(35,[54,59,62,66]),'Am':(33,[52,57,60,64]),'G':(43,[55,59,62,67]),'Dh':(38,[57,62,66,69])}
PROG=[(0,TN[0]-HOP,'Em'),(TN[0]-HOP,TN[1]-HOP,'Em'),(TN[1]-HOP,TN[2]-HOP,'D'),(TN[2]-HOP,TN[3]-HOP,'C'),(TN[3]-HOP,T['pb'],'Bm'),
      (T['pb'],T['turn'],'Am'),(T['turn'],15.625,'Dh'),(15.625,16.875,'G'),(16.875,18.125,'Em'),(18.125,19.375,'C'),(19.375,20.625,'G'),(20.625,21.875,'D'),(21.875,23.625,'G')]
def chord_at(t):
    for a,b,c in PROG:
        if a<=t<b: return CH[c]
    return CH['G']
def sec(t):
    if t<TN[0]-HOP: return 'hook'
    if t<T['dead']: return 'fall'
    if t<T['pb']: return 'void'
    if t<T['turn']: return 'whole'
    if t<T['cta']: return 'rise'
    if t<21.875: return 'cta'
    return 'out'
L=np.zeros(N);R=np.zeros(N);KK=[]
# pad: triângulo + serra bem filtrada (mais macio que o do modelo); o filtro fecha na descida e abre na virada
OPEN={'hook':0.2,'fall':0.26,'void':0.07,'whole':0.22,'rise':0.9,'cta':0.75,'out':0.8}
for i,(a,b,c) in enumerate(PROG):
    root,notes=CH[c]; d=min(b,END+0.3)-a; n=int((d+0.8)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.3)*np.clip((d+0.8-tt)/0.8,0,1)
    op=OPEN[sec(a+0.01)]*(1-0.16*max(0,i-1) if sec(a+0.01)=='fall' else 1)
    for k,m in enumerate(notes):
        f=midi(m)
        sL=lp((tri(f,n,k*.13)*1.4+saw(f,n,0.004,k*.31)*.6)*env*0.0075,420+3000*op)
        sR=lp((tri(f*1.003,n,k*.57)*1.4+saw(f,n,-0.005,k*.77)*.6)*env*0.0075,420+3000*op)
        add(L,sL,a);add(R,sR,a)
    sub=np.sin(2*np.pi*midi(root)*tt)*env*0.032;add(L,sub,a);add(R,sub,a)
S16=B/4
def kick(t,g=.36):
    n=int(0.42*SR);tt=np.arange(n)/SR;f=44+110*np.exp(-tt*30);k=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*7.5)*g
    k[:200]+=hp(rng.standard_normal(200),2000)*np.linspace(1,0,200)*g*.22
    add(L,k,t);add(R,k,t);KK.append(t)
def rim(t,g=.06):
    n=int(0.12*SR);tt=np.arange(n)/SR;c=(bp(rng.standard_normal(n),1400,4800)*np.exp(-tt*46)+.5*np.sin(2*np.pi*820*tt)*np.exp(-tt*60))*g
    add(L,c,t);add(R,c*.9,t+0.0005)
def hat(t,g=.02,dec=150):
    n=int(0.06*SR);tt=np.arange(n)/SR;h=hp(rng.standard_normal(n),8800)*np.exp(-tt*dec)*g;add(L,h,t);add(R,h*.7,t)
def bass(t,note,g=.11,d=0.3):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note);x=(np.sin(2*np.pi*f*tt)+.3*lp(tri(f*2,n),500))*np.exp(-tt*4.6)*np.minimum(1,tt/0.005)*g;add(L,x,t);add(R,x,t)
def mallet(t,note,g=.035,pan=0.0,bright=1.0):
    n=int(0.6*SR);tt=np.arange(n)/SR;f=midi(note)
    x=(np.sin(2*np.pi*f*tt)*np.exp(-tt*7)+.5*bright*np.sin(2*np.pi*f*4*tt)*np.exp(-tt*22)+.15*bright*np.sin(2*np.pi*f*9.2*tt)*np.exp(-tt*40))*np.minimum(1,tt/0.002)*g
    for k,(dl,gg) in enumerate([(0,1),(B*.75,.34),(B*1.5,.14)]): add(L,x*(1-pan*(1 if k%2==0 else -1))*gg,t+dl);add(R,x*(1+pan*(1 if k%2==0 else -1))*gg,t+dl)
# gancho: sem bateria; pedal de baixo em colcheias espaçadas
for k in range(int((TN[0]-HOP)/B)+1):
    t=k*B
    if t<TN[0]-HOP-0.1: bass(t,40,.06 if k%2 else .085,.5)
    if t>=T['h2'] and t<3.4: hat(t+B/2,.01)
# descida: o baixo rareia e o chimbal some a cada etapa
BASS_N=[40,38,36,35]; DENS=[(0,2,3,4,6),(0,2,4,6),(0,3,6),(0,4)]
for st in range(4):
    a=TN[st]; b=(TN[st+1]-HOP) if st<3 else T['dead']
    kick(a,.3-.035*st)
    for j in range(8):
        t=a+j*B/2
        if t>=b-0.05: break
        if j in DENS[st]: bass(t,BASS_N[st],.1-.014*st,.34)
        if st<3 and j%2==1: hat(t,.016-.004*st)
        if st==0 and j in (2,6): rim(t,.04)
        if st==1 and j==4: rim(t,.032)
# virada e groove em meio-tempo (bumbo nos tempos pares a partir de 14,375, aro nos ímpares)
ARP=[0,2,3,1,2,3,1,2]
k0=int(round(T['turn']/S16))
for k in range(k0,int(END/S16)):
    t=k*S16; s=sec(t); rel=k-k0; pos=rel%16; root,notes=chord_at(t)
    if s=='rise':
        lit=t>=T['L'][3]
        if pos in (0,8): kick(t,.3 if not lit else .37)
        if lit and pos in (4,12): rim(t,.075)
        if pos%2==0: bass(t,root+(12 if pos%8==6 else 0),.085 if not lit else .115,.28)
        hat(t,(.008 if not lit else .02)*[1,.4,.7,.4][pos%4],100 if pos%4==2 else 160)
        if lit and pos%2==0: mallet(t,notes[ARP[(rel//2)%8]]+12,.03,0.3)
    elif s=='cta':
        if pos in (0,8): kick(t,.34)
        if pos in (4,12): rim(t,.065)
        if pos%2==0: bass(t,root,.1,.28)
        hat(t,.017*[1,.4,.7,.4][pos%4],100 if pos%4==2 else 160)
        if pos%2==0 and t>T['cta']+0.3: mallet(t,notes[ARP[(rel//2)%8]]+12,.028,0.3)
    elif s=='out':
        if pos==0 and t<22.025: kick(t,.3)
        if t<22.525 and pos%4==0: mallet(t,notes[ARP[(rel//4)%8]]+12,.028,0.3)
sc=np.ones(N)
for kt in KK:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.45*np.exp(-tt/0.09)[:j-i])
L*=sc;R*=sc
# dinâmica do arco: quase silêncio quando o lead esfria, respiro antes de a linha inteira aparecer e antes do giro para o CTA
dyn=np.ones(N)
def duck(a,b,g,ra=0.05,rb=0.15):
    m=np.clip((TT-a)/ra,0,1)*np.clip((b-TT)/rb,0,1); dyn[:]=dyn*(1-(1-g)*m)
duck(T['dead'],T['pb']+0.3,0.28,0.25,0.3); duck(T['turn']-0.14,T['turn'],0.4,0.08,0.02); duck(T['cta']-0.2,T['cta'],0.5,0.1,0.02)
L*=dyn;R*=dyn
ir=rng.standard_normal(int(2.0*SR))*np.exp(-np.arange(int(2.0*SR))/SR*2.6);ir/=np.sqrt((ir**2).sum())
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
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;f=200*(8**k);fx((np.sin(2*np.pi*np.cumsum(f)/SR)*.35+hp(rng.standard_normal(n),1500)*k)*k**2*g,at)
def bell(at,notes,g=.05,dec=4.0,pan=0.0,bright=1.0):
    n=int(1.6*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes:
        f=midi(m);x+=(np.sin(2*np.pi*f*tt)+.4*bright*np.sin(2*np.pi*f*2.01*tt)*np.exp(-tt*8)+.2*bright*np.sin(2*np.pi*f*3.02*tt)*np.exp(-tt*14))*np.exp(-tt*dec)
    fx(x*g*np.minimum(1,tt/0.002),at,1,pan)
def shimmer(at,d=.6,g=.03):
    n=int(d*SR);tt=np.arange(n)/SR;fx(hp(rng.standard_normal(n),7000)*np.sin(np.pi*tt/d)**2*g*(0.6+0.4*np.sin(2*np.pi*14*tt)),at)
def powerdown(at,g=.07,f0=420,f1=150,d=.34):
    n=int(d*SR);tt=np.arange(n)/SR;f=f0*(f1/f0)**(tt/d);fx(lp(tri(1,n)*0+np.sin(2*np.pi*np.cumsum(f)/SR),1800)*np.sin(np.pi*np.minimum(1,tt/d))**0.6*np.exp(-tt*3)*g,at)
# A · gancho
impact(0.0,.26);tick(0.0,.04,1800);thud(0.1,.09,96);thud(0.5,.09,104)
pop(T['n0']-0.04,.08,780,-.3);bell(T['n0'],[79,83],.05,4,-.25);tick(T['n0']+0.1,.025,2600,-.3)
whoosh(T['n0']+0.1,0.7,.03,1800,500,.3,-.3)
whoosh(T['h2']-0.42,0.4,.06,500,3600,.82);thud(T['h2']-0.1,.16,62);impact(T['h2']+0.1,.4,40);thud(T['h2']+0.1,.2,58)
# B · descida pela linha: a cada etapa, um sino mais grave e mais abafado, e a etapa "desliga"
FALL=[71,69,67,64]
for st in range(4):
    a=TN[st]
    whoosh(a-HOP,HOP+0.12,.1-.012*st,2600-300*st,320,.62)
    thud(a-0.02,.2-.02*st,64-4*st);tick(a,.03,1500-150*st,-.3)
    bell(a+0.02,[FALL[st]],.06-.008*st,5+st,-.25,1-0.26*st)
    powerdown(a+0.26,.06-.008*st,400-50*st,150-14*st)
# o lead esfria
bell(TN[3]+0.64,[52],.04,5,-.2,.3);thud(TN[3]+0.64,.1,50);tick(TN[3]+0.66,.02,900,-.2)
# C · recuo: a linha inteira
riser(T['pb']-0.1,0.6,.035);whoosh(T['pb'],0.66,.13,5600,260,.5);impact(T['over'],.36,34);thud(T['over'],.18,52)
bell(T['over']+0.06,[57,64],.03,3)
whoosh(T['turn']-0.36,.3,.04,2400,600,.5)
# a vista geral dura 4 tempos: pedal de baixo em Lá e um sino no meio, para a pausa não ficar vazia
bass(12.5,33,.07,.55);bass(13.75,33,.06,.55);bell(13.125,[64],.022,3.5,-.2,.5)
# virada: "Com processo, o depois acontece." e as quatro etapas acendem (sinos subindo)
riser(T['turn'],T['L'][0]-T['turn'],.045);thud(T['turn'],.12,84);thud(T['turn']+0.16,.12,92)
RISE=[74,79,83,86]
for i,tl in enumerate(T['L']):
    pop(tl-0.02,.07,620+90*i,-.3);bell(tl,[RISE[i]],.06,5,-.2);tick(tl+0.06,.03,2400+220*i,-.3);thud(tl+0.04,.09,96+8*i)
impact(T['L'][3]+0.02,.3,43);bell(T['L'][3]+0.04,[67,71,74],.04,2.6);shimmer(T['L'][3]+0.1,.9,.03)
# D · a linha gira e vira o cabeçalho do CTA
whoosh(T['cta']-0.3,0.66,.11,380,5200,.55);thud(T['cta']+0.16,.16,66);tick(T['cta']+0.16,.03,2000)
thud(T['cta']+0.2,.1,100);pop(T['cta']+0.42,.05,520)
for i in range(11): key(T['typ']+0.04+i*(0.8/11),.05)
pop(T['send'],.1,900,.3);bell(T['send']+0.03,[79,83],.05,5,.3);whoosh(T['send']+0.05,.72,.035,900,4200,.7)
bell(T['send']+0.74,[86],.035,5,.3)
thud(T['sub'],.06,110);thud(T['sub']+0.18,.06,118)
whoosh(T['logo']-0.3,.34,.035,600,3000,.8);bell(T['logo']+0.06,[55,62,67,71],.06,2.2);impact(T['logo']+0.06,.16,44)
bell(21.875,[67,71,74,79],.045,2.4);shimmer(21.825,.5,.02);bell(22.5,[79,83],.028,3)
FL=FL+0.16*fftconvolve(hp(FL,400),ir)[:N];FR=FR+0.16*fftconvolve(hp(FR,400),np.roll(ir,211))[:N]
# ---------- mix ----------
mus=np.sqrt(np.mean(((L+R)/2)**2));fxr=np.sqrt(np.mean(((FL+FR)/2)**2))
g=mus*10**(-2.5/20)/fxr
fade=np.clip(TT/0.02,0,1)*np.clip((END-TT)/0.3,0,1)
st=np.stack([(L+FL*g)*fade,(R+FR*g)*fade],1);st=np.tanh(st/np.max(np.abs(st))*1.6)/np.tanh(1.6)*0.86
wavfile.write('mix.wav',SR,(st[:int(END*SR)]*32767).astype(np.int16));print('ok',st.shape)
