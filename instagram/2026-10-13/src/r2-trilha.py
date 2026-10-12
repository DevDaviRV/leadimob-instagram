"""Reel 2 (13/10) "Lançamento: o lead pergunta da unidade e espera." · trilha 90 BPM em Fá maior.
Arranjo próprio (diferente de 100 Láb, Sib, 96 Ré M, 108 Mi m, 84 Mib M dos R2 anteriores): marimba em FM (síntese de 2 operadores),
pad suave, sub-baixo, shaker, rimshot e um relógio de verdade (tique-taque) que vira o metrônomo da espera.
Arco: o espelho se monta (uma nota de marimba subindo por andar) -> a 1204 acende (sino) e a pergunta chega (pop) -> órbita (sopro que
atravessa da esquerda para a direita) -> "A noite toda.": a banda sai, fica o pad em Ré menor e o tique-taque; no time-lapse os tiques aceleram
e somem, "toda." cai às 09:00 -> âmbar: duas notas graves abafadas -> "Quem espera, compara.": dois golpes graves -> troca de foco (swell invertido)
-> prática: entra o groove (Fá-Dó-Rém-Sib), cada passo do card é um acorde que sobe; a visita (verde) resolve em Fá com sino
-> o card vira a resposta enviada na conversa da 1204 (dois pops) -> CTA: teclas, envio, logo. SFX presos aos tempos do index.html."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=21.3; N=int((END+0.5)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(1310)
B=60/90; E16=B/4
T=dict(rows=-1.0,lit=0.3,aq=0.45,o1=2.1,o2=2.95,b1=2.74,ck=2.94,tl=3.55,tlE=5.15,b2=5.13,bp=3.85,bOut=6.35,b4=6.47,b5=6.78,b6=7.15,rf=9.55,c1=9.67,pln=10.1,dsp=11.0,st2=12.65,st3=14.7,cOut=16.75,f1=17.3,f2=17.45,typ=17.75,send=18.4,sub=18.7,logo=19.35,sheen=20.15)   # espelho do index.html (rodada 3)
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
def marimba(note,d=1.0,vel=1.0):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note)
    idx=2.2*np.exp(-tt*28)*vel
    x=np.sin(2*np.pi*f*tt+idx*np.sin(2*np.pi*f*4*tt))*np.exp(-tt*(5+f/400))
    x+=0.25*np.sin(2*np.pi*f*3.93*tt)*np.exp(-tt*30)
    return x*np.minimum(1,tt/0.002)*vel
def pad(notes,d,g=1.0,cut=1400):
    n=int(d*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for k,m in enumerate(notes):
        f=midi(m)
        for dt in (-0.004,0.0035):
            p=np.cumsum(np.full(n,f*(1+dt))/SR)+rng.random();x+=2*(p%1)-1
    env=np.minimum(1,tt/0.4)*np.clip((d-tt)/0.6,0,1)
    return lp(x*env,cut)*g/len(notes)
def sub(note,d,g=1.0):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note)
    return np.sin(2*np.pi*f*tt)*np.exp(-tt*2.4)*np.minimum(1,tt/0.01)*np.clip((d-tt)/0.05,0,1)*g
def kick(g=1.0):
    n=int(0.4*SR);tt=np.arange(n)/SR;f=44+95*np.exp(-tt*30);return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*7.5)*g
def rim(g=1.0):
    n=int(0.08*SR);tt=np.arange(n)/SR;return (bp(rng.standard_normal(n),1500,4500)*np.exp(-tt*80)+0.5*np.sin(2*np.pi*820*tt)*np.exp(-tt*60))*g
def shaker(g=1.0):
    n=int(0.09*SR);tt=np.arange(n)/SR;return hp(rng.standard_normal(n),6000)*np.sin(np.pi*np.clip(tt/0.09,0,1))**2*g
def clock(g=1.0,f=2600):
    n=int(0.05*SR);tt=np.arange(n)/SR;return (bp(rng.standard_normal(n),f*0.7,f*1.4)*np.exp(-tt*160)+0.4*np.sin(2*np.pi*f*0.5*tt)*np.exp(-tt*120))*g
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
def key(g=1.0):
    n=int(.05*SR);tt=np.arange(n)/SR;return bp(rng.standard_normal(n),1800,5200)*np.exp(-tt*120)*g+np.sin(2*np.pi*(300+rng.uniform(-40,40))*tt)*np.exp(-tt*90)*g*.6
def swell(d,g=1.0):   # "reverso": ruído + acorde que crescem até o corte
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d
    x=(lp(rng.standard_normal(n),900)*(1-k)+lp(rng.standard_normal(n),5200)*k)*k**3+0.6*sum(np.sin(2*np.pi*midi(m)*tt) for m in (65,69,72))/3*k**2.5
    return x*g
# ---------- harmonia ----------
CH={'F':(41,[60,65,69,72]),'Am':(45,[60,64,69,72]),'Bb':(46,[62,65,70,74]),'C':(48,[60,64,67,72]),'Dm':(50,[62,65,69,74]),'Gm':(43,[62,67,70,74])}
# ---------- A · gancho: o espelho se monta ----------
H1,H2=T['o1']/3,2*T['o1']/3   # o gancho agora dura até a órbita em 2,1 s
for a,b,c in [(0,H1,'F'),(H1,H2,'Am'),(H2,T['o2']+0.05,'Bb')]: st(pad(CH[c][1],b-a+0.6,1,1100),a,.05)
for i,m in enumerate([60,62,65,67,69,72,74]):   # um andar = uma nota (o espelho já está montado no quadro 0: arpejo rápido de abertura)
    st(marimba(m,0.9,0.8),i*0.04,.11,(-.3+.1*i))
for k in range(int(T['o1']/E16)):
    t=k*E16;pos=k%16
    if pos in (0,10): st(kick(),t,.28)
    if pos%2==0: st(shaker(),t,.012*(1 if pos%4 else .6),.25)
    if pos in (4,12): st(rim(),t,.05,-.15)
    if pos%4==0: st(sub(CH['F' if t<H1 else 'Am' if t<H2 else 'Bb'][0]-12+12,0.5),t,.16)
    if t>T['aq'] and pos%4==2: st(marimba([72,76,77,81][(k//4)%4],0.6,0.6),t,.05,.3)
st(bell([84,88],1,3),T['lit']+0.02,.06,.3);st(thud(1,80),T['lit'],.08)
st(pop(1,700),T['aq'],.09,.35);st(pop(1,940),T['aq']+0.07,.05,.35)
# ---------- órbita ----------
o=whoosh(T['o2']-T['o1']+0.2,300,4200,1);n=len(o);pan=np.linspace(-0.7,0.7,n)
add(FL,o*(1-pan),T['o1']-0.1,.13);add(FR,o*(1+pan),T['o1']-0.1,.13)
st(thud(1,52),T['o2']-0.05,.2);st(bell([62],1,5),T['o2'],.04)
# ---------- B · espera: pad em Ré menor, tique-taque, time-lapse ----------
st(pad(CH['Dm'][1],T['bOut']-T['o2']+0.8,1,800),T['o2']-0.1,.06)
st(sub(38,3.5,1),T['o2'],.08)
tt0=T['ck']+0.1;t=tt0;i=0
while t<T['tl']: st(clock(1,2600 if i%2==0 else 2100),t,.05,(-.2,.2)[i%2]);t+=0.5;i+=1
# time-lapse: tiques acelerando e desacelerando (segue a curva do ponteiro)
def eio3(x): x=min(max(x,0),1); return 4*x**3 if x<.5 else 1-(-2*x+2)**3/2
ts=[];prev=0
for j in range(1,600):
    tt=T['tl']+(T['tlE']-T['tl'])*j/600;m=int(eio3((tt-T['tl'])/(T['tlE']-T['tl']))*68)   # um tique a cada 10 min
    if m>prev: ts.append(tt);prev=m
for j,tq in enumerate(ts): st(clock(1,2600+200*(j%2)),tq,.035,(-.2,.2)[j%2])
st(thud(1,48),T['tlE']+0.02,.12);st(marimba(50,1.6,0.9),T['b2'],.08,-.1)   # "TODA." cai quando o relógio chega às 09:00
t=T['tlE']+0.5;i=0
while t<T['bOut']: st(clock(1,2600 if i%2==0 else 2100),t,.045,(-.2,.2)[i%2]);t+=0.5;i+=1
st(marimba(45,1.4,0.7),T['bp']+0.02,.12,-.2);st(marimba(44,1.4,0.7),T['bp']+0.36,.1,-.2)
st(whoosh(0.4,2500,400,1,False),T['bOut']-0.05,.06)
# ---------- tese ----------
st(thud(1,46),T['b4'],.24);st(pad([50,57,62],2.6,1,600),T['b4'],.07);st(sub(38,2.4,1),T['b4'],.12)
st(thud(1,42),T['b5'],.26);st(marimba(50,1.6,1),T['b5'],.09);st(marimba(57,1.6,0.8),T['b6'],.05,.2)
# ---------- troca de foco ----------
sw=swell(T['c1']-T['rf']+0.05,1);st(sw,T['rf'],.09)
# ---------- C · prática: groove ----------
PROG=[(T['c1'],'F'),(T['c1']+4*B*0.5,'C'),(T['st2'],'Dm'),(T['st2']+1*B*1.5,'Bb'),(T['st3'],'F'),(T['st3']+B*1.5,'C')]
def chord(t):
    c='F'
    for a,cc in PROG:
        if t>=a: c=cc
    return c
for a,b in [(T['c1'],T['st2']),(T['st2'],T['st3']),(T['st3'],T['cOut']+0.3)]:
    seg=[(x,c) for x,c in PROG if a<=x<b]
    for j,(x,c) in enumerate(seg):
        e=seg[j+1][0] if j+1<len(seg) else b
        st(pad(CH[c][1],e-x+0.5,1,1200+600*(a>=T['st3'])),x,.06)
ARP=[0,2,1,3,2,1,3,2]
k0=int(np.ceil(T['c1']/E16))
for k in range(k0,int(T['cOut']/E16)):
    t=k*E16;pos=k%16;c=chord(t);root,notes=CH[c];lvl=0 if t<T['st2'] else 1 if t<T['st3'] else 2
    if pos in (0,8) or (lvl>=1 and pos==10): st(kick(),t,.3+.03*lvl)
    if pos in (4,12): st(rim(),t,.06,-.15)
    if pos%2==0: st(shaker(),t,.014*(1 if pos%4 else .6),.25)
    if pos%4==0: st(sub(root-12+12,0.55),t,.18)
    if pos%2==0: st(marimba(notes[ARP[(k//2)%8]]+12,0.5,0.55+0.1*lvl),t,.04+.006*lvl,(.3,-.3)[(k//2)%2])
st(thud(1,58),T['c1'],.16);st(bell([77,81],1,3),T['c1']+0.04,.04)
for i in range(4): st(clock(1,3000),T['pln']+i*0.18,.02,.1*i-.15)
st(pop(1,820),T['dsp'],.08,.2);st(bell([84],1,4),T['dsp']+0.03,.04,.2)
# passos: cada acorde sobe
st(whoosh(0.3,600,3200,1),T['st2']-0.25,.05);st(thud(1,64),T['st2'],.12);st(bell([74,77,81],1,3),T['st2']+0.32,.05,-.2)
st(whoosh(0.3,600,3200,1),T['st3']-0.25,.05);st(thud(1,68),T['st3'],.12)
st(bell([77,81,84,89],1,2.4),T['st3']+0.38,.07,.2);st(pop(1,900),T['st3']+0.36,.07,.2)
# ---------- D · CTA ----------
st(whoosh(0.45,3500,300,1,False),T['cOut'],.08);st(pop(1,700),T['cOut']+0.22,.07,-.3);st(pop(1,940),T['cOut']+0.4,.08,.3);st(pop(1,1180),T['cOut']+0.47,.04,.3)   # pergunta e resposta na conversa
st(thud(1,56),T['f1'],.14)
st(pad(CH['F'][1]+[77],END-T['f1']+0.2,1,1700),T['f1'],.09);st(sub(41,2.5,1),T['f1'],.14)
for k in range(int(np.ceil(T['f1']/E16)),int((END-0.6)/E16)):
    t=k*E16;pos=k%16
    if pos in (0,8) and t<END-1.0: st(kick(),t,.33)
    if pos in (4,12) and t<END-1.0: st(rim(),t,.05,-.15)
    if pos%4==0 and t<END-0.8: st(sub(41 if (k//16)%2==0 else 46,0.55),t,.15)
    if pos%2==0: st(shaker(),t,.01,.25)
    if pos%4==2: st(marimba([72,77,81,84][(k//4)%4],0.6,0.6),t,.06,.25)
for i in range(7): st(key(1),T['typ']+0.03+i*(0.5/7),.05,rng.uniform(-.2,.2))
st(pop(1,900),T['send'],.1,.3);st(bell([81,84],1,4),T['send']+0.03,.05,.3)
st(bell([65,69,72,77],1,2.2),T['logo']+0.05,.07);st(thud(1,50),T['logo']+0.05,.1);st(bell([84,89],1,3),T['sheen'],.035)
# ---------- mix ----------
ir=rng.standard_normal(int(1.8*SR))*np.exp(-np.arange(int(1.8*SR))/SR*3.0);ir/=np.sqrt((ir**2).sum())
L=L+0.18*fftconvolve(hp(L,300),ir)[:N];R=R+0.18*fftconvolve(hp(R,300),np.roll(ir,97))[:N]
FL=FL+0.14*fftconvolve(hp(FL,400),ir)[:N];FR=FR+0.14*fftconvolve(hp(FR,400),np.roll(ir,211))[:N]
fade=np.clip(TT/0.02,0,1)*np.clip((END-TT)/0.35,0,1)
s=np.stack([(L+FL)*fade,(R+FR)*fade],1);s=np.tanh(s/np.max(np.abs(s))*1.5)/np.tanh(1.5)*0.86
wavfile.write('mix.wav',SR,(s[:int(END*SR)]*32767).astype(np.int16));print('ok',s.shape)
