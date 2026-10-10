"""Reel 2 (11/10) "Visitou e não fechou? O que perguntar depois." · trilha 84 BPM em Mi bemol maior.
Arranjo próprio (diferente de 03/10 100 BPM Láb, 06/10 96 Ré, 07/10 108 Mim, 09/10 104 Ré, 10/10 116 Dó#m):
piano de feltro (síntese aditiva com martelo), dedilhado em Karplus-Strong, baixo acústico, vassourinha (ruído filtrado) e chimbal fechado suave.
Arco: gancho em Mib/Sol m com o sino verde da visita realizada -> o card encolhe (sopro grave) -> "E depois?": a música para,
fica uma nota de piano sustentada e um tique por dia que passa, o âmbar ganha duas notas graves abafadas -> a célula de hoje se
expande e vira a conversa de hoje (inspiração) -> perguntas enviadas: entra a vassourinha, cada mensagem é uma nota que sobe (Mib, Sol, Sib), acorde quando as três estão na tela ->
match cut: a 3ª pergunta vira a resposta (sopro + pouso grave) -> resposta e próximo passo (groove cheio, Mib-Sib/Ré-Dóm-Sib) -> CTA resolve em Mib.
SFX presos aos mesmos tempos do index.html."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=48000; END=19.6; N=int((END+0.5)*SR); TT=np.arange(N)/SR
rng=np.random.default_rng(1110)
B=60/84; E8=B/2; E16=B/4
T=dict(a1=-0.45,ag=-0.35,chk=0.85,t1=2.95,b1=3.07,cur=[3.9,4.4,4.9,5.4],b2=4.25,b3=5.05,bp=5.9,t2=6.9,c1=6.82,q=[7.3,8.35,9.35],cOut=11.4,d=[11.5,11.62,11.74],rb=11.95,kw=12.6,cat=12.95,np=13.7,dOut=15.1,ag2=15.36,f1=15.48,f2=15.74,typ=15.74,send=16.42,sub=16.72,logo=17.2,sheen=18.0)
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
def piano(note,d=2.5,vel=1.0):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note);x=np.zeros(n)
    for h,(a,dec) in enumerate([(1,1.6),(.5,2.4),(.28,3.4),(.14,4.6),(.08,6),(.04,7.5)],1):
        fh=f*h*(1+0.0004*h*h);x+=a*np.sin(2*np.pi*fh*tt+rng.random())*np.exp(-tt*dec*(0.6+0.4*f/300))
    ham=lp(rng.standard_normal(n)*np.exp(-tt*120),2500)*0.15
    x=(x*np.minimum(1,tt/0.004)+ham)*vel
    return lp(x,1800+1400*vel)*np.clip((d-tt)/0.3,0,1)
def pluck(note,d=1.4,g=1.0,bright=0.5):
    f=midi(note);P=int(SR/f);n=int(d*SR);buf=lp(rng.standard_normal(P),3000+3000*bright);out=np.zeros(n)
    y=np.concatenate([buf,np.zeros(n)])
    for i in range(P,n+P): y[i]=0.996*0.5*(y[i-P]+y[i-P+1]) if i-P+1<len(y) else 0
    out=y[P:P+n];return out*g*np.clip((d-np.arange(n)/SR)/0.2,0,1)
def bass(note,d=0.6,g=1.0):
    n=int(d*SR);tt=np.arange(n)/SR;f=midi(note)
    x=(np.sin(2*np.pi*f*tt)+.3*np.sin(2*np.pi*2*f*tt)+.1*np.sin(2*np.pi*3*f*tt))*np.exp(-tt*3.2)*np.minimum(1,tt/0.008)
    return lp(x,900)*g*np.clip((d-tt)/0.08,0,1)
def brush(g=1.0,d=0.28):
    n=int(d*SR);tt=np.arange(n)/SR;return bp(rng.standard_normal(n),1800,7000)*(np.minimum(1,tt/0.02))*np.exp(-tt*11)*g
def hat(g=1.0):
    n=int(0.06*SR);tt=np.arange(n)/SR;return hp(rng.standard_normal(n),7000)*np.exp(-tt*70)*g
def kick(g=1.0):
    n=int(0.4*SR);tt=np.arange(n)/SR;f=46+70*np.exp(-tt*26);return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*7)*g
def bell(notes,g=1.0,dec=3.0):
    n=int(2.4*SR);tt=np.arange(n)/SR;x=np.zeros(n)
    for m in notes:
        f=midi(m);x+=(np.sin(2*np.pi*f*tt)+.35*np.sin(2*np.pi*f*2.76*tt)*np.exp(-tt*6)+.2*np.sin(2*np.pi*f*5.4*tt)*np.exp(-tt*12))*np.exp(-tt*dec)
    return x*np.minimum(1,tt/0.002)*g/len(notes)
def whoosh(d,lo,hi,g=1.0,up=True):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;env=np.sin(np.pi*k)**1.6
    x=rng.standard_normal(n);a=bp(x,lo*0.6,min(lo*1.8,SR/2.1));b=bp(x,hi*0.5,min(hi*1.5,SR/2.1))
    m=k if up else 1-k
    return (a*(1-m)+b*m)*env*g
def thud(g=1.0,f0=70):
    n=int(0.45*SR);tt=np.arange(n)/SR;f=f0+60*np.exp(-tt*30);return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*8)*g
def tick(g=1.0,f=2400):
    n=int(0.05*SR);tt=np.arange(n)/SR;return (np.sin(2*np.pi*f*tt)*.6+bp(rng.standard_normal(n),f*0.8,f*1.6))*np.exp(-tt*90)*g
def pop(g=1.0,f=900):
    n=int(0.12*SR);tt=np.arange(n)/SR;ff=f*(1+0.6*np.exp(-tt*60));return np.sin(2*np.pi*np.cumsum(ff)/SR)*np.exp(-tt*38)*g
def key(g=1.0):
    n=int(0.04*SR);tt=np.arange(n)/SR;return bp(rng.standard_normal(n),1500,6000)*np.exp(-tt*120)*g
def riser(d,g=1.0):
    n=int(d*SR);tt=np.arange(n)/SR;k=tt/d;return (bp(rng.standard_normal(n),900,5000)*k**2+np.sin(2*np.pi*np.cumsum(200+700*k**2)/SR)*0.25*k**2)*g
# ---------- harmonia (Mib maior) ----------
CH={'Eb':(39,[55,58,63,67]),'Gm':(43,[55,58,62,67]),'Ab':(44,[56,60,63,67]),'Bb':(46,[53,58,62,65]),'Cm':(48,[55,60,63,67]),'Bb/D':(38,[53,58,62,65]),'Ebadd9':(39,[55,58,63,65,70]),'Fm7':(41,[56,60,63,65])}
# pedaço, inicio, fim, acorde
PROG=[(0,1.45,'Eb'),(1.45,2.95,'Gm'),(2.95,6.9,'Ab'),
      (6.9,8.0,'Ab'),(8.0,9.4,'Bb'),(9.4,10.4,'Cm'),(10.4,11.4,'Bb'),
      (11.4,12.6,'Eb'),(12.6,13.7,'Bb/D'),(13.7,14.5,'Cm'),(14.5,15.1,'Bb'),(15.1,20.1,'Ebadd9')]
def chord_at(t):
    for a,b,c in PROG:
        if a<=t<b: return CH[c]
    return CH['Ebadd9']
def sec(t):
    if t<2.95: return 'hook'
    if t<6.9: return 'sil'
    if t<11.4: return 'perg'
    if t<15.1: return 'resp'
    return 'cta'
# piano: acordes no início de cada pedaço (exceto o silêncio, que fica com uma nota só)
for a,b,c in PROG:
    root,notes=CH[c];s=sec(a+0.01)
    if s=='sil':
        st(piano(63,4.4,.55),a+0.05,.05,-.1);st(piano(51,4.4,.4),a+0.05,.04,.1);continue
    v={'hook':.55,'perg':.7,'viag':.5,'resp':.85,'cta':.8}[s]
    for k,m in enumerate(notes): st(piano(m,b-a+1.2,v),max(0,a)+k*0.012,.028,(k-1.5)*.12)
    if s in ('perg','resp','cta') or a>0.5: st(piano(root+12,b-a+1.0,v),a,.03)
# dedilhado (Karplus-Strong) em colcheias: gancho leve, perguntas e resposta mais cheio
PAT=[0,2,1,3,2,1,3,2]
for k in range(int(END/E8)+1):
    t=k*E8;s=sec(t);root,notes=chord_at(t)
    if s=='sil' or s=='viag': continue
    g={'hook':.07,'perg':.06,'resp':.075,'cta':.06}[s]
    if s=='hook' and t<0.2: continue
    st(pluck(notes[PAT[k%8]%len(notes)]+12,1.0,1,.4+.2*(s=='resp')),t,g,.3*(1 if k%2 else -1))
# ritmo
for k in range(int(END/E16)+1):
    t=k*E16;s=sec(t);pos=k%16;root,notes=chord_at(t)
    if s=='hook':
        if pos==0 and t>1.4: st(kick(),t,.16)
        if pos in (4,12) and t>1.4: st(brush(),t,.035)
    elif s=='perg':
        r=(t-6.9)/4.5
        if pos in (0,10): st(kick(),t,.2+.06*r)
        if pos in (4,12): st(brush(),t,.05+.02*r)
        if pos%2==0: st(hat(),t,.012+.01*r,.25)
        if pos in (0,6,8,14): st(bass(root,0.5),t,.22)
    elif s=='resp':
        if pos in (0,7,10): st(kick(),t,.26)
        if pos in (4,12): st(brush(1,.35),t,.075)
        if pos%2==0: st(hat(),t,.022,.25)
        if pos%2==1: st(hat(),t,.01,-.25)
        if pos in (0,3,6,8,11,14): st(bass(root+(7 if pos in (6,14) else 0),0.4),t,.25)
    elif s=='cta':
        if t>15.8 and pos in (0,10): st(kick(),t,.22)
        if t>15.8 and pos in (4,12): st(brush(),t,.06)
        if t>15.8 and pos%2==0: st(hat(),t,.016,.25)
        if t>15.8 and pos in (0,8): st(bass(root,0.7),t,.24)
# ---------- SFX ----------
st(piano(70,2.5,.8),0.0,.04,.2)                                    # nota de abertura com o título
st(thud(1,64),0.02,.14)
st(whoosh(0.5,600,4000),T['ag']+0.2,.05,-.2,True)
st(pop(1,1100),T['chk'],.07,.2,True);st(bell([79,82],1,4),T['chk']+0.02,.06,.2,True)          # visita realizada (verde)
# virada 1: o card encolhe
st(whoosh(0.6,3000,400),T['t1']-0.05,.08,0,True);st(thud(1,58),T['t1']+0.6,.12,0,True)
# silêncio: um tique por dia que passa
for i,tc in enumerate(T['cur']): st(tick(1,2600-120*i),tc+0.05,.05,(-.3+.2*i),True)
st(piano(51,2.6,.5),T['bp'],.05);st(piano(50,2.6,.5),T['bp']+0.36,.045)                        # âmbar: duas notas graves
st(pop(1,520),T['bp'],.05,0,True)
# virada 2: a célula de hoje se expande
st(riser(0.62,1),T['t2']-0.05,.05,0,True);st(whoosh(0.5,500,5000),T['t2']+0.1,.06,0,True);st(thud(1,72),T['t2']+0.62,.12,0,True)
# perguntas: cada uma é uma nota que sobe
for i,(tq,m) in enumerate(zip(T['q'],[75,79,82])):
    st(piano(m,2.6,.9),tq+0.05,.07,(-.2,0,.2)[i]);st(pop(1,700+150*i),tq+0.08,.05,(-.2,0,.2)[i],True)
    if i>0: st(whoosh(0.35,800,4500),tq-0.12,.04,0,True)
st(bell([63,70,75,79],1,2.2),T['q'][2]+0.45,.05,0,True)
# match cut: a 3ª pergunta desce e vira a resposta
st(whoosh(0.4,600,3500),T['cOut']-0.02,.06,-.1,True);st(tick(1,1800),T['rb']-0.15,.05,0,True);st(thud(1,58),T['rb'],.13,0,True)
st(pop(1,480),T['rb']+0.02,.08,-.2,True)                                                         # mensagem recebida: nota grave
for i,td in enumerate(T['d']): st(thud(1,70+8*i),td+0.03,.07,0,True)
st(bell([82,87],1,5),T['kw']+0.05,.04,-.1,True)
st(whoosh(0.45,700,4500),T['cat']-0.15,.06,.25,True);st(pop(1,820),T['cat']+0.08,.05,.25,True)
st(pop(1,1050),T['np'],.08,.1,True);st(bell([75,79,82],1,3),T['np']+0.03,.07,.1,True);st(thud(1,46),T['np'],.14,0,True)
# CTA: o card da 2ª visita chega
st(whoosh(0.5,500,4000),T['dOut']+0.0,.06,0,True);st(whoosh(0.5,700,3800),T['dOut'],.05,0,True);st(pop(1,760),T['ag2']+0.05,.05,0,True);st(thud(1,80),T['f1'],.1,0,True)
for i in range(6): st(key(1),T['typ']+0.03+i*0.075,.05,0,True)
st(pop(1,900),T['send'],.09,.3,True);st(bell([82,87],1,4),T['send']+0.03,.06,.3,True);st(thud(1,44),T['send'],.12,0,True)
for i,dt in enumerate([-0.3,-0.14,0.06,0.22]): st(thud(1,110+8*i),T['sub']+dt+0.1,.04,0,True)
st(bell([63,67,70,75],1,2.4),T['logo']+0.05,.06,0,True);st(bell([79,82,87],1,2.6),T['sheen'],.035,0,True)
# reverb curto (ambiência) nos efeitos e no piano
ir_n=int(1.6*SR);irt=np.arange(ir_n)/SR;ir=rng.standard_normal(ir_n)*np.exp(-irt*3.4);ir=lp(ir,5000);ir/=np.sqrt(np.sum(ir**2))
FL=FL+0.18*fftconvolve(hp(FL,300),ir)[:N];FR=FR+0.18*fftconvolve(hp(FR,300),np.roll(ir,233))[:N]
L=L+0.12*fftconvolve(hp(L,250),ir)[:N];R=R+0.12*fftconvolve(hp(R,250),np.roll(ir,177))[:N]
# ---------- mix ----------
mus=np.sqrt(np.mean(((L+R)/2)**2));fxr=np.sqrt(np.mean(((FL+FR)/2)**2))
g=mus*10**(-3/20)/fxr
fade=np.clip(TT/0.01,0,1)*np.clip((END-TT)/0.4,0,1)
stx=np.stack([(L+FL*g)*fade,(R+FR*g)*fade],1);stx=np.tanh(stx/np.max(np.abs(stx))*1.5)/np.tanh(1.5)*0.86
wavfile.write('mix.wav',SR,(stx[:int(END*SR)]*32767).astype(np.int16));print('ok',stx.shape)
