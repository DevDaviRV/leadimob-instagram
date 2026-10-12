"""Leadimob R1 13/10 — trilha original: 88 BPM, Ré menor -> Fá maior.
Arranjo novo: piano de feltro aditivo (sem pluck), pad de seno, baixo sub, aro e vassourinha.
Gancho (pulso contido, relógio do plantão) -> "fecha" (porta desce: baque e chocalho metálico, trilha cai) ->
a noite (só pad grave e piano esparso; notificações) -> Leadimob (abre em Fá maior, groove) -> ficha (um acorde por linha) ->
painel por empreendimento -> CTA (resolve em Fá).
Uso: /usr/bin/python3 trilha.py -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[7]['end']+2.3; N=int((END+0.5)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(1310)
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def add(buf,x,at,g=1.0):
    i=int(at*SR)
    if i<0: x=x[-i:]; i=0
    j=min(len(buf),i+len(x))
    if i<len(buf) and j>i: buf[i:j]+=g*x[:j-i]
def midi(n): return 440*2**((n-69)/12)
def norm(s): return s.lower().replace('"','').replace('“','').replace('”','')
def WF(i,s):
    for w in C[i]['words']:
        if norm(w['w']).startswith(s.lower()): return float(w['t'])
    return float(C[i]['start'])
def pluck(f,dur,g=1.0,bright=0.5):
    n=int(dur*SR);L=max(2,int(SR/f));buf=rng.uniform(-1,1,L);buf=lp(buf,2000+6000*bright) if L>30 else buf
    out=np.zeros(n);d=0.996
    for i in range(n):
        v=buf[i%L];out[i]=v;buf[i%L]=d*0.5*(v+buf[(i+1)%L])
    return out*g
PL={}
def pl(m,dur=0.9,b=0.5):
    k=(m,dur,b)
    if k not in PL: PL[k]=pluck(midi(m),dur,1.0,b)
    return PL[k]

def piano(m,dur=1.6,g=1.0):
    f=midi(m);n=int(dur*SR);tt=np.arange(n)/SR
    x=sum(a*np.sin(2*np.pi*f*h*tt*(1+0.0004*h*h))*np.exp(-tt*(2.2+1.4*h)) for h,a in ((1,1),(2,.42),(3,.16),(4,.07)))
    x+=lp(rng.standard_normal(n),900)*np.exp(-tt*60)*0.05
    return x*np.minimum(1,tt/0.004)*g
PN={}
def pn(m,dur=1.6):
    if (m,dur) not in PN: PN[(m,dur)]=piano(m,dur)
    return PN[(m,dur)]
BPM=88; beat=60/BPM; bar=4*beat
FE=WF(1,'fecha'); TB=C[2]['start']-0.5; TC=C[3]['start']-0.15; TD=C[4]['start']-0.8
TD2=C[5]['start']-0.3; TE=C[6]['start']-0.45; TF=C[7]['start']-0.4
T0=TD-np.ceil(TD/bar)*bar       # tempo forte quando a Leadimob atende
def sec(t):
    if t<FE: return 'hook'
    if t<TD: return 'noite'
    if t<TD2: return 'prod'
    if t<TE: return 'ficha'
    if t<TF: return 'painel'
    return 'cta'
MIN=[[38,62,65,69,72],[34,62,65,69,74],[41,60,65,69,72],[33,61,64,69,73]]     # Dm9 Bbmaj7 F A
MAJ=[[41,60,64,69,72,76],[34,62,65,69,74,77],[38,60,65,69,72,76],[36,60,64,67,70,74]]  # F Bb Dm7 C
def chord(t):
    b=int(np.floor((t-T0)/bar)); s=sec(t)
    if s in('hook','noite'): return MIN[b%4] if s=='hook' else MIN[(b%2)*1]
    if s=='cta': return MAJ[0]
    return MAJ[b%4]
L=np.zeros(N);R=np.zeros(N)
PLp=np.zeros(N);PRp=np.zeros(N)
nb=int((END-T0)/bar)+2
for b in range(-1,nb):
    st=T0+b*bar
    if st>END or st+bar<0: continue
    ch=chord(max(st+0.01,0)); n=int((bar+1.2)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.6)*np.clip((bar+1.2-tt)/1.2,0,1)
    for j,m in enumerate(ch[1:]):
        f=midi(m); x=(np.sin(2*np.pi*f*tt)+0.2*np.sin(2*np.pi*2*f*tt+0.3))*env*0.011
        pan=0.3+0.4*(j%2); add(PLp,x*(1-pan),st); add(PRp,x*pan,st)
cv={'hook':.45,'noite':.32,'prod':1.0,'ficha':1.0,'painel':.95,'cta':.85}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(9600)/9600,'same')
L+=lp(PLp,2200)*ctrl; R+=lp(PRp,2200)*ctrl
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
arp=[0,2,1,3,2,4,3,1]
for k in range(-64,int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.0: continue
    s=sec(t); pos=k%16; ch=chord(t)
    full=s in('prod','ficha','painel')
    if (full and pos in(0,7,10)) or (s=='cta' and pos==0) or (s=='hook' and pos==0):
        n=int(0.4*SR);tt=np.arange(n)/SR;fk=44+100*np.exp(-tt*30)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*7)*(0.16 if s=='hook' else 0.26)
        add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if full and pos in(4,12):
        n=int(0.1*SR);tt=np.arange(n)/SR;rm=(bp(rng.standard_normal(n),1800,5000)*np.exp(-tt*50)+np.sin(2*np.pi*700*tt)*np.exp(-tt*70)*0.4)*0.04
        add(L,rm,t);add(R,rm*0.8,t)
    if full and pos%2==0:
        n=int(0.12*SR);tt=np.arange(n)/SR;vel=[.8,.35,.6,.4][(pos//2)%4]
        h=bp(rng.standard_normal(n),3500,10000)*np.minimum(1,tt/0.02)*np.exp(-tt*30)*0.016*vel;pan=0.35+0.3*((k*3)%5)/4;add(L,h*(1-pan),t);add(R,h*pan,t)
    if s=='hook' and pos%4==0:
        n=int(0.03*SR);tt=np.arange(n)/SR;tk=np.sin(2*np.pi*(2000 if pos%8==0 else 1700)*tt)*np.exp(-tt*200)*0.018;add(L,tk*0.6,t);add(R,tk,t)
    if pos==0 or (full and pos==8):
        n=int(beat*2*SR*0.9);tt=np.arange(n)/SR;f=midi(ch[0])
        g={'hook':0.06,'noite':0.05,'prod':0.1,'ficha':0.1,'painel':0.1,'cta':0.09}[s]
        x=(np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt))*np.minimum(1,tt/0.01)*np.exp(-tt*1.4)*g; add(BL,x,t)
    if (s=='hook' and pos%8==0) or (s=='noite' and pos==0) or (s=='cta' and pos%4==0) or (full and pos%2==0):
        m=ch[1:][arp[(k//2)%8]%len(ch[1:])]+12
        x=pn(m,1.6)*(0.035 if full else 0.03)
        pan=0.3+0.4*((k//2)%2); add(AL,x*(1-pan),t); add(AR,x*pan,t)
d=int(beat*0.75*SR)
for rep in range(1,3):
    g=0.28**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.28*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.35*np.exp(-tt/0.08)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
# a noite: grave de Ré sustentado
n=int((TD-FE)*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(38)*tt)+0.3*np.sin(2*np.pi*midi(50)*tt*1.003))*0.03*np.clip(tt/0.8,0,1)*np.clip((TD-FE-tt)/0.4,0,1)
add(L,dr,FE);add(R,dr,FE)
ir_n=int(2.2*SR);tt=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-tt*2.8);irR=rng.standard_normal(ir_n)*np.exp(-tt*2.8);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.26*fftconvolve(hp(L,300),irL)[:N];R=R+0.26*fftconvolve(hp(R,300),irR)[:N]
# ---------------- SFX ----------------
FL=np.zeros(N);FR=np.zeros(N)

FL=np.zeros(N);FR=np.zeros(N)
def st2(x,at,pan=.5,g=1): add(FL,x*(1-pan)*1.4*g,at);add(FR,x*pan*1.4*g,at)
def sweep(at,dur,f0,f1,g,env='bell'):
    n=int(dur*SR);tt=np.arange(n)/SR;x=rng.standard_normal(n);out=np.zeros(n);seg=960
    for i in range(0,n,seg):
        k=i/n;f=f0+(f1-f0)*(k**2 if env=='rise' else np.sin(np.pi*k));out[i:i+seg]=bp(x[max(0,i-3000):i+seg],max(60,f*0.7),min(f*1.45,20000))[-len(out[i:i+seg]):]
    e=(tt/dur)**2 if env=='rise' else np.sin(np.pi*tt/dur)**2
    pan=np.linspace(.3,.7,n);s=out*e*g;add(FL,s*(1-pan),at);add(FR,s*pan,at)
def whoosh_side(at,dur,g,l2r=True):
    n=int(dur*SR);tt=np.arange(n)/SR;x=bp(rng.standard_normal(n),600,5000)*np.sin(np.pi*tt/dur)**2*g
    pan=np.linspace(.15,.85,n) if l2r else np.linspace(.85,.15,n);add(FL,x*(1-pan),at);add(FR,x*pan,at)
def impact(at,g=0.28):
    n=int(1.6*SR);tt=np.arange(n)/SR;f=36+70*np.exp(-tt*9)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.8)*g+lp(rng.standard_normal(n),1400)*np.exp(-tt*12)*g*0.2;add(FL,s,at);add(FR,s,at)
def pop(at,g=0.07,f=900,pan=.5):
    n=int(0.14*SR);tt=np.arange(n)/SR;fr=f*(1+0.6*np.exp(-tt*60));st2(np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*38)*g,at,pan)
def chime(at,notes,g=0.03,dec=1.4):
    n=int(2.6*SR);tt=np.arange(n)/SR;s=np.zeros(n)
    for i,m in enumerate(notes):
        dd=int(i*0.07*SR);f=midi(m);s[dd:]+=(np.sin(2*np.pi*f*tt[:n-dd])+0.22*np.sin(2*np.pi*2.01*f*tt[:n-dd]))*np.exp(-tt[:n-dd]*dec)
    add(FL,s*g,at);add(FR,s*g,at)
def key(at,g=0.035,pan=.5):
    n=int(0.035*SR);tt=np.arange(n)/SR;st2(bp(rng.standard_normal(n),1800,7000)*np.exp(-tt*180)*g,at,pan)
def click(at,g=0.05,pan=.5):
    n=int(0.02*SR);tt=np.arange(n)/SR;st2(hp(rng.standard_normal(n),2500)*np.exp(-tt*400)*g,at,pan)
def swoosh_send(at,g=0.05):
    n=int(0.22*SR);tt=np.arange(n)/SR;f=700+1800*tt/0.22;st2(np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt/0.22)*g,at,0.7)
def thud(at,g=0.15):
    n=int(0.8*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*(48+30*np.exp(-tt*20))*tt)*np.exp(-tt*6)*g;add(FL,s,at);add(FR,s,at)

def rattle(at,dur,g=0.04):
    n=int(dur*SR);tt=np.arange(n)/SR;x=bp(rng.standard_normal(n),900,4000)*(0.5+0.5*np.sign(np.sin(2*np.pi*38*tt)))*np.sin(np.pi*tt/dur)*g;add(FL,x,at);add(FR,x*0.9,at)
# gancho: régua do plantão; "fecha": porta desce e baque
rattle(FE-0.02,0.55,0.035);thud(FE+0.5,0.16);pop(FE+0.08,0.04,500,0.6)
# plantão vira chip; anúncio entra
sweep(TB-0.1,0.6,600,2800,0.04);pop(TB+0.45,0.05,820,0.5)
pop(WF(2,'rodando')-0.05,0.04,1200,0.6)
# o anúncio recua; perguntas chegam
sweep(TC-0.1,0.6,2600,700,0.04)
for x in(WF(3,'pergunta')-0.15,WF(3,'sem')+0.05,WF(3,'é')-0.05): pop(x+0.02,0.055,950,0.65)
pop(WF(3,'resposta')+0.2,0.045,520,0.5)
o=WF(3,'outro')+0.12
for k in range(3): whoosh_side(o+k*0.12,0.4,0.035,True)
# a noite clareia: Leadimob
sweep(TD-0.35,0.7,400,4200,0.06,'rise');impact(TD+0.15,0.2);chime(WF(4,'leadimob')-0.05,[65,69,72,77],0.028,1.5)
pop(TD+0.27,0.05,900,0.35)
r1=WF(4,'cada')+0.05;swoosh_send(r1-0.05,0.04);pop(r1,0.05,950,0.7)
cx=WF(4,'qual')-0.05;chime(cx,[72,77,81],0.02,1.6)
pop(WF(4,'ele')-0.1,0.05,780,0.35)
# ficha
sweep(TD2-0.1,0.5,900,3200,0.035)
for k,x in enumerate([TD2+0.4,WF(5,'perfil')-0.05,WF(5,'perfil')+0.25]): pop(x+0.25,0.045,1000+k*140,0.4+0.1*k)
ag=WF(5,'agendada')-0.08;pop(ag,0.07,1100,0.55);chime(ag+0.02,[69,72,77,81],0.026,1.4)
# painel
whoosh_side(TE-0.3,0.6,0.045,True);pop(TE+0.3,0.06,1000,0.65)
whoosh_side(WF(6,'empreendimento')-0.1,0.45,0.045,False)
# CTA
sweep(TF-0.35,0.6,500,4200,0.045,'rise');impact(TF+0.05,0.18);chime(TF+0.5,[65,72,77,81],0.028,1.5);pop(TF+1.45,0.045,700,0.6)
# ---------------- voz ----------------
V=np.zeros(N)
for c in TL:
    sr,x=wavfile.read(f"vo_b/p{c['i']:02d}.wav");x=x.astype(np.float64)/32768.0
    if x.ndim>1: x=x.mean(1)
    if sr!=SR: x=resample_poly(x,SR,sr)
    add(V,x,c['start'])
env=lp(np.abs(V),6);env=np.clip(env/0.05,0,1);duck=1-0.55*env
fade=np.clip(T/0.05,0,1)*np.clip((END-T)/1.2,0,1)
L*=duck*fade;R*=duck*fade
vr=np.sqrt(np.mean(V[lp(np.abs(V),6)>0.01]**2));mr=np.sqrt(np.mean(((L+R)/2)**2))
gm=vr*10**(-11/20)/mr;L*=gm;R*=gm;FL*=gm*fade;FR*=gm*fade
sfr=np.sqrt(np.mean(((FL+FR)/2)**2)); FL*=vr*10**(-15/20)/sfr; FR*=vr*10**(-15/20)/sfr
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_novo.wav',L+FL,R+FR);save('mix_vo.wav',(L+FL)+V,(R+FR)+V)
print('END',round(END,2),'gain',round(gm,3))
