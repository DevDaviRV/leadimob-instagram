"""Reel 2 (14/10) "Pergunta fácil vence mensagem longa." · trilha 120 BPM em Lá maior (paragrafo em Fá# menor).
Arranjo próprio (diferente de 03/10 100 Láb, 06/10 96 Ré, 07/10 108 Mim, 09/10 104 Ré, 11/10 84 Mib, 13/10 90 Fá):
piano elétrico em FM (timbre de "tine" com tremolo), baixo redondo, estalo de dedo no lugar da caixa, chimbal fechado.
Arco = a ideia do vídeo: gancho limpo e seguro -> recuo com desfoque (varredura de filtro para baixo) -> MENSAGEM LONGA:
a bolha é enviada inteira (pop) e a textura entope (arpejo de fusas em Fá# menor, cluster que cresce), cinco notas sobem nas 5 perguntas,
duas notas graves abafadas no ponto âmbar -> o parágrafo se apaga: um tique por palavra, cada vez mais esparso, o cluster
vai perdendo notas -> o voo do sobrevivente: um sopro que sobe até o pouso (acorde limpo de Lá maior) -> pergunta: só o piano;
"?" = duas notas subindo; "Três." = sino verde + o groove começa (a conversa começou) -> varredura da linha de luz: sopro que
atravessa da esquerda para a direita (uma passada) -> tese com o groove inteiro (Lá-Mi-Fá#m-Ré) -> CTA: teclas, envio, logo.
SFX presos aos tempos do index.html."""
import numpy as np, re
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=20.0; N=int((END+0.5)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(1410)
B=0.5; E16=B/4
T=dict(a3=0.04,a4=0.16,peek=0.3,aOut=2.98,b=2.94,bIn=3.64,bLines=3.38,qq=4.95,pill=5.35,bOut=7.0,er=7.12,erE=8.15,fly=7.98,land=8.78,cK=8.74,c1=8.82,cq=8.96,cK2=9.78,ans=9.93,wA=11.9,wD=0.56,dOut=15.2,f=15.4,typ=15.9,send=16.7,sub=16.96,logo=17.6)
def lp(x,f): return sosfilt(butter(2,f,'low',fs=SR,output='sos'),x)
def hp(x,f): return sosfilt(butter(2,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b): return sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
L=np.zeros(N);R=np.zeros(N);FL=np.zeros(N);FR=np.zeros(N)
def add(buf,x,at,g=1.0):
    i=int(round(at*SR))
    if i<0: x=x[-i:];i=0
    j=min(len(buf),i+len(x))
    if j>i: buf[i:j]+=g*x[:j-i]
def st(x,at,g=1.0,pan=0.0,fx=False):
    a,b=(FL,FR) if fx else (L,R); add(a,x,at,g*(1-pan)); add(b,x,at,g*(1+pan))
midi=lambda n:440*2**((n-69)/12)
# ---------- instrumentos ----------
def ep(note,d=1.2,vel=1.0):     # piano elétrico: FM 1:1 + tine 14:1, tremolo leve
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note)
    idx=(1.6*vel)*np.exp(-tt*6)
    x=np.sin(2*np.pi*f*tt+idx*np.sin(2*np.pi*f*tt))*np.exp(-tt*(2.2+f/900))
    x+=0.22*vel*np.sin(2*np.pi*f*14*tt)*np.exp(-tt*60)
    x*=1+0.12*np.sin(2*np.pi*5.2*tt)
    return x*np.minimum(1,tt/0.003)*np.clip((d-tt)/0.08,0,1)*vel
def pad(notes,d,g=1.0,cut=1300):
    n=int(d*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes:
        f=midi(m)
        for dt in (-0.0035,0.004):
            p=np.cumsum(np.full(n,f*(1+dt))/SR)+rng.random();x+=2*(p%1)-1
    env=np.minimum(1,tt/0.35)*np.clip((d-tt)/0.5,0,1)
    return lp(x*env,cut)*g/len(notes)
def bass(note,d=0.4,g=1.0):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note);p=np.cumsum(np.full(n,f)/SR)
    x=np.sin(2*np.pi*p)+0.25*lp(2*(p%1)-1,500)
    return x*np.exp(-tt*4)*np.minimum(1,tt/0.005)*np.clip((d-tt)/0.04,0,1)*g
def kick(g=1.0):
    n=int(0.4*SR);tt=np.arange(n)/SR;f=48+110*np.exp(-tt*32);return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*7.8)*g
def snap(g=1.0):
    n=int(0.12*SR);tt=np.arange(n)/SR;x=bp(rng.standard_normal(n),1400,6000)
    return (x*np.exp(-tt*55)+0.6*x*np.exp(-np.maximum(0,tt-0.009)*70)*(tt>0.009))*g
def hat(g=1.0,dec=160):
    n=int(0.07*SR);tt=np.arange(n)/SR;return hp(rng.standard_normal(n),8000)*np.exp(-tt*dec)*g
def tick(g=1.0,f=2400):
    n=int(0.035*SR);tt=np.arange(n)/SR;return (np.sin(2*np.pi*f*tt)*np.exp(-tt*170)+0.4*bp(rng.standard_normal(n),f*0.8,min(f*2,20000))*np.exp(-tt*220))*g
def typekey(g=1.0):
    n=int(.05*SR);tt=np.arange(n)/SR;return bp(rng.standard_normal(n),1800,5200)*np.exp(-tt*120)*g+np.sin(2*np.pi*(300+rng.uniform(-40,40))*tt)*np.exp(-tt*90)*g*.6
def bell(notes,g=1.0,dec=2.6):
    n=int(2.4*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes:
        f=midi(m);x+=(np.sin(2*np.pi*f*tt)+.35*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt*6)+.18*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*12))*np.exp(-tt*dec)
    return x*np.minimum(1,tt/0.002)*g/len(notes)
def whoosh(d,lo,hi,g=1.0,up=True):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;env=np.sin(np.pi*k)**1.6
    x=rng.standard_normal(n);a=bp(x,lo*0.6,min(lo*1.8,SR/2.1));b=bp(x,hi*0.5,min(hi*1.5,SR/2.1))
    m=k if up else 1-k
    return (a*(1-m)+b*m)*env*g
def thud(g=1.0,f0=60):
    n=int(0.5*SR);tt=np.arange(n)/SR;f=f0+60*np.exp(-tt*30);return (np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)+lp(rng.standard_normal(n),900)*np.exp(-tt*40)*0.3)*g
def pop(g=1.0,f=760):
    n=int(.16*SR);tt=np.arange(n)/SR;fr=f*(1+.7*np.exp(-tt*55));return np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*34)*g
def riser(d,g=1.0):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;f=300*(6**k)
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*0.3+hp(rng.standard_normal(n),2500)*k)*k**2.2*g
CH={'A':(45,[61,64,69,73]),'E':(40,[59,64,68,71]),'F#m':(42,[61,66,69,73]),'D':(38,[62,66,69,74]),'Bm':(47,[62,66,71,74]),'C#m':(49,[61,64,68,73])}

# ---------- A · gancho (0–3.0): limpo e seguro ----------
st(kick(),0.0,.34);st(bass(33,1.2,1),0.0,.2);st(ep(69,1.6,1),0.0,.07);st(ep(73,1.6,0.9),0.0,.05,.2)
st(bell([81,85,88],1,2.4),0.0,.06,.25)                     # "FÁCIL" (ciano)
st(pad(CH['A'][1],1.6,1,1500),0,.05);st(pad(CH['E'][1],1.6,1,1500),1.5,.05)
for k in range(int(2.9/E16)):
    t=k*E16;pos=k%16
    if pos in (0,10) and t>0.1: st(kick(),t,.27)
    if pos in (4,12): st(snap(),t,.05,-.1)
    if pos%2==0: st(hat(1,190),t,.011*(1 if pos%4 else .5),.25)
    if pos%4==0: st(bass((45 if t<1.5 else 40)-12,0.45),t,.17)
    if pos%4==2: st(ep([76,73,69,73][(k//4)%4],0.5,0.5),t,.03,(.25,-.25)[(k//4)%2])
st(thud(1,64),T['a3'],.1);st(ep(57,0.8,0.6),T['a3'],.05)
st(lp(ep(45,1.2,0.6),500),T['a4'],.12,-.1)                # "MENSAGEM LONGA." abafado
st(lp(whoosh(0.35,300,1400,1),1800),T['peek']-0.05,.03,.2);st(thud(1,56),T['peek']+0.12,.05)   # borda da bolha aparece por baixo
# ---------- recuo com desfoque ----------
w=whoosh(0.5,3500,300,1,False);st(w,T['aOut']-0.1,.09);st(thud(1,48),T['bIn']-0.1,.18)
# ---------- B · a mensagem longa: textura que entope ----------
d=T['bOut']-T['b']+0.3
st(pad(CH['F#m'][1],d,1,700),T['b'],.06);st(pad([30,42],d,1,300),T['b'],.12)
cl_notes=[61,64,66,68,69,71,73,76]
k=0;t=T['bLines']
while t<T['bOut']:                                           # arpejo de fusas, cada vez mais cheio e mais alto
    r=(t-T['bLines'])/(T['bOut']-T['bLines'])
    nt=cl_notes[(k*3+(k//5))%len(cl_notes)]+(12 if k%7==3 else 0)
    st(lp(ep(nt,0.3,0.4),1500+2500*r),t,.012+.02*r,np.sin(k*1.3)*.4)
    t+=B/8;k+=1
st(pop(1,620),T['bIn']-0.08,.1,.3);st(whoosh(T['bIn']-T['b'],800,3600,1),T['b'],.06,.3);st(thud(1,70),T['bIn']-0.06,.08)   # a bolha sobe e chega inteira
for i in range(3): st(tick(1,2600+300*i),T['bLines']+0.1+i*0.07,.02,.35)
for i in range(5): st(ep(64+[0,2,4,5,7][i]+12,0.6,0.7),T['qq']+i*0.1,.05,(-.3+.15*i))   # as 5 perguntas acendem
st(ep(42,1.2,0.8),T['pill']+0.02,.09,-.2);st(ep(41,1.2,0.8),T['pill']+0.3,.08,-.2)        # ponto âmbar
cl=pad([61,62,64,66,68,69],T['erE']-T['pill']+0.4,1,2400);nn=len(cl);cl*=np.linspace(0.2,1,nn)**2
st(cl,T['pill'],.05)
st(riser(T['bOut']-T['pill']-0.05,1),T['pill'],.035)
# ---------- o parágrafo se apaga palavra a palavra ----------
PAR='Olá! Aqui é o Rafael, corretor. Vi que você se interessou pelo residencial e separei as informações: temos plantas de , lazer completo, varanda gourmet e vaga coberta. Qual é a sua renda? Vai usar FGTS? Pretende financiar? Qual bairro prefere? Para quando seria a mudança? Fico à disposição!'
nw=len(PAR.split())
ers=[T['er']+(T['erE']-T['er']-0.16)*(i/(nw-1))**0.85 for i in range(nw)]
for i,te in enumerate(ers):
    if i%2==0 or i>nw*0.6: st(tick(1,3200-1600*i/nw),te+0.02,.022*(1-0.5*i/nw),np.sin(i*2.1)*.5)
st(whoosh(T['erE']-T['er'],5000,900,1,False),T['er'],.035)
# ---------- voo e pouso ----------
st(whoosh(T['land']-T['fly']+0.1,500,5200,1),T['fly'],.07);st(riser(T['land']-T['fly'],1),T['fly'],.03)
st(thud(1,58),T['land'],.15);st(ep(57,2.0,0.9),T['land'],.08)
for j,m in enumerate([61,64,69]): st(ep(m+12,2.2,0.7),T['land']+0.02+j*0.03,.045,(-.2,0,.2)[j])
st(pad(CH['A'][1],T['ans']-T['land']+0.3,1,900),T['land'],.05)
# ---------- C · pergunta e resposta ----------
st(pop(1,700),T['cq'],.06,.25);st(pop(1,1050),T['cq']+0.08,.05,.25)
for k in range(int(np.ceil(T['land']/B)),int(T['ans']/B)):   # só o piano, um toque por tempo
    st(ep([69,73,71,73][k%4],0.6,0.45),k*B,.03,.2)
st(ep(56,0.8,0.6),T['cK2'],.04)
st(bell([81,85,88,93],1,2.2),T['ans']+0.02,.08,.15);st(thud(1,62),T['ans'],.14);st(kick(),T['ans'],.3)
PROGC=[(T['ans'],'A'),(T['ans']+2*B,'E'),(T['ans']+4*B,'F#m')]
def chord(t,prog):
    c=prog[0][1]
    for a,cc in prog:
        if t>=a: c=cc
    return c
for j,(a,c) in enumerate(PROGC):
    e=PROGC[j+1][0] if j+1<len(PROGC) else T['wA']+0.2
    st(pad(CH[c][1],e-a+0.4,1,1300),a,.05)
for k in range(int(np.ceil((T['ans']+0.01)/E16)),int(T['wA']/E16)):
    t=k*E16;pos=k%16;root,notes=CH[chord(t,PROGC)]
    if pos in (0,8): st(kick(),t,.24)
    if pos%2==0: st(hat(1,200),t,.008,.25)
    if pos%4==0: st(bass(root-12,0.4),t,.13)
    if pos%4==2: st(ep(notes[(k//4)%4]+12,0.5,0.5),t,.028,(.25,-.25)[(k//4)%2])
# ---------- varredura da linha de luz (esquerda -> direita, duas vezes) ----------
T['wB']=T['wA']+0.28   # meio da passada: a tese já ocupa a metade esquerda
o=whoosh(T['wD']+0.15,400,6000,1);n=len(o);pan=np.linspace(-0.8,0.8,n)
add(FL,o*(1-pan),T['wA']-0.08,.14);add(FR,o*(1+pan),T['wA']-0.08,.14)
st(thud(1,52),T['wB'],.2)
# ---------- D · tese: groove inteiro (Lá-Mi-Fá#m-Ré) ----------
PROGD=[(T['wB'],'A'),(T['wB']+4*B*0.5+0.0,'E'),(T['wB']+4*B,'F#m'),(T['wB']+6*B,'D')]
for j,(a,c) in enumerate(PROGD):
    e=PROGD[j+1][0] if j+1<len(PROGD) else T['dOut']+0.3
    st(pad(CH[c][1],e-a+0.4,1,1800),a,.06)
for k in range(int(np.ceil(T['wB']/E16)),int(T['dOut']/E16)):
    t=k*E16;pos=k%16;root,notes=CH[chord(t,PROGD)]
    if pos in (0,8) or pos==11: st(kick(),t,.34)
    if pos in (4,12): st(snap(),t,.075,-.1)
    st(hat(1,150 if pos%4==2 else 220),t,.016*[1,.45,.8,.45][pos%4],.25)
    if pos%2==0: st(bass(root-12+(12 if pos%8==6 else 0),0.3),t,.15)
    st(ep(notes[[0,2,1,3,2,1,3,2][k%8]]+12,0.35,0.5),t,.022,(.3,-.3)[k%2])
st(bell([81,85,88],1,2.6),T['wB']+0.6,.05,-.2)
# ---------- E · CTA ----------
st(whoosh(0.4,3500,300,1,False),T['dOut'],.08);st(thud(1,54),T['f'],.16)
st(pad(CH['A'][1]+[76],END-T['f']+0.3,1,1700),T['f'],.08)
PROGE=[(T['f'],'A'),(T['f']+4*B,'D'),(T['f']+8*B,'A'),(T['f']+12*B,'E')]
for k in range(int(np.ceil(T['f']/E16)),int((END-0.5)/E16)):
    t=k*E16;pos=k%16;root,notes=CH[chord(t,PROGE)]
    if pos in (0,8) and t<END-0.9: st(kick(),t,.3)
    if pos in (4,12) and t<END-0.9: st(snap(),t,.055,-.1)
    if pos%2==0: st(hat(1,210),t,.01,.25)
    if pos%4==0 and t<END-0.7: st(bass(root-12,0.45),t,.14)
    if pos%4==2: st(ep(notes[(k//4)%4]+12,0.6,0.5),t,.03,(.25,-.25)[(k//4)%2])
for i in range(5): st(typekey(1),T['typ']+0.03+i*(0.55/5),.055,rng.uniform(-.2,.2))
st(pop(1,900),T['send'],.1,.3);st(bell([85,88],1,4),T['send']+0.03,.05,.3)
for i,dt in enumerate([0,0.12,0.26,0.4]): st(thud(1,110+8*i),T['sub']+dt+0.06,.05)
st(bell([69,73,76,81],1,2.2),T['logo']+0.05,.07);st(thud(1,50),T['logo']+0.05,.1);st(bell([85,88],1,3),T['logo']+0.95,.035)
st(ep(57,2.4,0.8),END-1.7,.07);st(ep(64,2.4,0.7),END-1.7,.05,.2);st(ep(73,2.4,0.7),END-1.7,.05,-.2)
# ---------- mix ----------
ir=rng.standard_normal(int(1.8*SR))*np.exp(-np.arange(int(1.8*SR))/SR*3.0);ir/=np.sqrt((ir**2).sum())
L=L+0.18*fftconvolve(hp(L,300),ir)[:N];R=R+0.18*fftconvolve(hp(R,300),np.roll(ir,97))[:N]
FL=FL+0.14*fftconvolve(hp(FL,400),ir)[:N];FR=FR+0.14*fftconvolve(hp(FR,400),np.roll(ir,211))[:N]
fade=np.clip(TT/0.01,0,1)*np.clip((END-TT)/0.35,0,1)
s=np.stack([(L+FL)*fade,(R+FR)*fade],1);s=np.tanh(s/np.max(np.abs(s))*1.5)/np.tanh(1.5)*0.86
wavfile.write('mix.wav',SR,(s[:int(END*SR)]*32767).astype(np.int16));print('ok',s.shape)
