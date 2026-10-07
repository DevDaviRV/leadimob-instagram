"""Leadimob R1 09/10 — trilha original: 98 BPM, Sol menor. Gancho esparso -> lista (pulso contido) -> plano (groove abre) -> Leadimob (brilhante) -> CTA.
Uso: python3 trilha.py -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[10]['end']+2.1; N=int((END+0.5)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(11)
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def add(buf,x,at,g=1.0):
    i=int(at*SR)
    if i<0: x=x[-i:]; i=0
    j=min(len(buf),i+len(x))
    if i<len(buf) and j>i: buf[i:j]+=g*x[:j-i]
def midi(n): return 440*2**((n-69)/12)
def WF(i,s):
    for w in C[i]['words']:
        if w['w'].lower().replace('"','').startswith(s.lower()): return float(w['t'])
    return float(C[i]['start'])
def saw(f,n,det=0.0):
    ph=np.cumsum(np.full(n,f*(1+det))/SR); return 2*(ph%1)-1
BPM=98; beat=60/BPM; bar=4*beat
T1=C[2]['start']-0.3; T2=C[3]['start']-0.35; T3=C[4]['start']-0.55; T4=C[9]['start']-0.35; WIPE=C[10]['start']-0.3
T0=(T3+0.42)-np.ceil((T3+0.42)/bar)*bar            # um tempo forte cai no zoom-through
def sec(t):
    if t<T2: return 'hook'
    if t<T3: return 'inbox'
    if t<T4: return 'tri'
    if t<WIPE: return 'prod'
    return 'cta'
prog=[[x-2 for x in c] for c in [[45,57,60,64,67,71],[48,60,64,67,71,76],[41,60,64,67,72,76],[43,59,62,67,71,74]]]  # Am9 Fmaj9 Cmaj9 G6/9
L=np.zeros(N);R=np.zeros(N)
nb=int((END-T0)/bar)+2
PL=np.zeros(N);PR=np.zeros(N)
for b in range(0,nb,2):
    st=T0+b*bar
    if st>END: break
    ch=prog[(b//2)%4]; n=int((2*bar+1.8)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.9)*np.clip((2*bar+1.8-tt)/1.8,0,1)
    for m in ch[1:]:
        for d,pan in((-0.006,.2),(0.006,.8)):
            s=saw(midi(m),n,d)*env*0.010; add(PL,s*(1-pan),st); add(PR,s*pan,st)
cv={'hook':.12,'inbox':.3,'tri':.65,'prod':.95,'cta':1.0}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(24000)/24000,'same')
PLd,PRd,PLo,PRo=lp(PL,450),lp(PR,450),lp(PL,3400),lp(PR,3400)
L+=PLd*(1-ctrl)+PLo*ctrl; R+=PRd*(1-ctrl)+PRo*ctrl
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
pat=[0,2,1,3,2,4,1,3]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.2: continue
    s_=sec(t); pos=k%16; b=int((t-T0)//bar); ch=prog[(b//2)%4]
    groove=s_ in('inbox','tri','prod','cta'); full=s_ in('prod','cta')
    if groove and (pos in(0,8) or (s_ in('tri','prod','cta') and pos==10)):
        if s_=='inbox' and pos==10: continue
        n=int(0.45*SR);tt=np.arange(n)/SR;fk=44+100*np.exp(-tt*30)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*7)*(0.2 if s_=='inbox' else 0.3)
        add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if s_ in('tri','prod','cta') and pos in(4,12):
        n=int(0.25*SR);tt=np.arange(n)/SR;cp=bp(rng.standard_normal(n),1200,6000)*(np.exp(-tt*24)+0.4*np.exp(-np.abs(tt-0.012)*300))*0.05
        add(L,cp,t);add(R,cp*0.9,t)
    if (s_ in('inbox') and pos%4==2) or (s_ in('tri','prod','cta') and pos%2==0):
        n=int(0.04*SR);tt=np.arange(n)/SR;vel=[.8,.25,.55,.3][pos%4]*(0.6 if s_=='inbox' else 1)
        h=hp(rng.standard_normal(n),9000)*np.exp(-tt*130)*0.022*vel;pan=0.25+0.5*((k*5)%7)/6;add(L,h*(1-pan),t);add(R,h*pan,t)
    if pos%4==0 and s_!='hook':
        n=int(beat*SR*0.95);tt=np.arange(n)/SR;f=midi(ch[0])
        g={'inbox':0.05,'tri':0.08,'prod':0.1,'cta':0.1}[s_]
        x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt))*np.exp(-tt*2.8)*g; add(BL,x,t)
    if (s_=='tri' and pos%4==0) or (full and pos%2==0):
        m=ch[1:][pat[(k//2)%8]]+12;n=int(0.34*SR);tt=np.arange(n)/SR
        x=lp(saw(midi(m),n)*np.exp(-tt*10),3200)*(0.016 if s_=='tri' else 0.02); add(AL,x,t);add(AR,x*0.75,t)
d=int(beat*0.75*SR)
for rep in range(1,4):
    g=0.33**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.45*np.exp(-tt/0.09)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
n=int((T2+0.3)*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(31)*tt)+0.4*np.sin(2*np.pi*midi(43)*tt*1.002))*0.05*np.clip(tt/1.5,0,1)*np.clip((T2+0.3-tt)/0.5,0,1)
add(L,dr,0);add(R,dr,0)
ir_n=int(2.2*SR);tt=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-tt*2.6);irR=rng.standard_normal(ir_n)*np.exp(-tt*2.6);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.26*fftconvolve(hp(L,300),irL)[:N];R=R+0.26*fftconvolve(hp(R,300),irR)[:N]
# ---------------- SFX ----------------
FL=np.zeros(N);FR=np.zeros(N)
def st2(x,at,pan=.5,g=1): add(FL,x*(1-pan)*1.4*g,at);add(FR,x*pan*1.4*g,at)
def sweep(at,dur,f0,f1,g,env='bell'):
    n=int(dur*SR);tt=np.arange(n)/SR;x=rng.standard_normal(n);out=np.zeros(n);seg=960
    for i in range(0,n,seg):
        k=i/n;f=f0+(f1-f0)*(k**2 if env=='rise' else np.sin(np.pi*k));out[i:i+seg]=bp(x[max(0,i-3000):i+seg],max(60,f*0.7),min(f*1.45,20000))[-len(out[i:i+seg]):]
    e=(tt/dur)**2 if env=='rise' else np.sin(np.pi*tt/dur)**2
    pan=np.linspace(.25,.75,n);s=out*e*g;add(FL,s*(1-pan),at);add(FR,s*pan,at)
def impact(at,g=0.32):
    n=int(1.8*SR);tt=np.arange(n)/SR;f=34+72*np.exp(-tt*9)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.6)*g+lp(rng.standard_normal(n),1400)*np.exp(-tt*12)*g*0.25;add(FL,s,at);add(FR,s,at)
def tick(at,g=0.05,f=2400,pan=.5):
    n=int(0.05*SR);tt=np.arange(n)/SR;st2(np.sin(2*np.pi*f*tt)*np.exp(-tt*140)*g,at,pan)
def pop(at,g=0.07,f=900,pan=.5):
    n=int(0.14*SR);tt=np.arange(n)/SR;fr=f*(1+0.6*np.exp(-tt*60));st2(np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*38)*g,at,pan)
def ding(at,g=0.04,m=88,pan=.5):
    n=int(0.9*SR);tt=np.arange(n)/SR;f=midi(m);x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2.76*f*tt)*np.exp(-tt*9))*np.exp(-tt*6)*g;st2(x,at,pan)
def chime(at,notes,g=0.035,dec=1.4):
    n=int(3*SR);tt=np.arange(n)/SR;s=np.zeros(n)
    for i,m in enumerate(notes):
        dd=int(i*0.07*SR);f=midi(m);s[dd:]+=(np.sin(2*np.pi*f*tt[:n-dd])+0.22*np.sin(2*np.pi*2.01*f*tt[:n-dd]))*np.exp(-tt[:n-dd]*dec)
    add(FL,s*g,at);add(FR,s*g,at)
def click(at,g=0.05,pan=.5):
    n=int(0.02*SR);tt=np.arange(n)/SR;st2(hp(rng.standard_normal(n),2500)*np.exp(-tt*400)*g,at,pan)
def buzz(at,dur=0.5,g=0.07):
    n=int(dur*SR);tt=np.arange(n)/SR;x=np.sin(2*np.pi*170*tt)*(0.5+0.5*np.sign(np.sin(2*np.pi*9*tt)))*np.sin(np.pi*tt/dur)*g;add(FL,x,at);add(FR,x,at)
def thud(at,g=0.2):
    n=int(0.8*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*(48+30*np.exp(-tt*20))*tt)*np.exp(-tt*6)*g;add(FL,s,at);add(FR,s,at)
# GANCHO: lembretes surgem e somem; virada para "sem perceber"
for j in range(6): ding(0.05+j*0.1,0.016,int([79,82,84,86,89,91][j])-2,0.2+0.12*j)
for j in range(6): sweep(1.5+j*0.3,0.6,2600,700,0.012)
thud(WF(1,'memória')+0.05,0.13)
sweep(T1-0.5,0.5,500,3200,0.05,'rise');click(T1+0.1,0.05,0.5)
thud(WF(2,'perdeu'),0.1);ding(WF(2,'sem'),0.03,62,0.5)
sweep(T2-0.7,0.7,400,4200,0.08,'rise')
# LISTA: linhas entram, a conversa desce
for i in range(6): pop(C[3]['start']-0.15+i*0.11,0.045,700+i*60,0.2+0.12*i)
tick(WF(3,'disse'),0.05,2000,0.4)
A0=WF(3,'e')+0.1
for j in range(5): pop(A0+j*0.52,0.06,980-j*70,0.3+0.1*j);ding(A0+j*0.52+0.04,0.02,84-j*2,0.6)
thud(A0+4*0.52+0.35,0.12);ding(A0+4*0.52+0.4,0.03,62,0.5)
# FAÇA DIFERENTE: zoom na linha e virada
sweep(T3-0.15,0.6,300,6500,0.1,'rise');impact(T3+0.42,0.3);chime(WF(4,'diferente'),[55,62,67],0.022,1.6)
# PLANO
TP=C[5]['start']-0.2
sweep(TP-0.1,0.5,2400,700,0.05);pop(TP+0.15,0.06,760,0.5)
a=WF(5,'próximo')-0.05
for k in range(16): click(a+k*0.047,0.035,0.4+0.2*(k%2))
pop(WF(5,'encerrar'),0.07,1000,0.7);chime(WF(5,'encerrar')+0.05,[67,74,79],0.025,1.4)
for w,c,m in [((6,'em'),(6,'volte'),[67,70,74]),((7,'depois'),(7,'com'),[70,74,77])]:
    n=WF(*w)-0.1;sweep(n-0.3,0.4,900,3200,0.04);tick(n+0.02,0.06,2200);pop(WF(*c)-0.1,0.07,880,0.6);chime(WF(*c),m,0.022,1.4)
tick(WF(8,'nunca')-0.1,0.04,1400);pop(WF(8,'um')+0.2,0.05,520,0.4)
sweep(WF(8,'viu')-0.05,0.35,3000,600,0.05);thud(WF(8,'viu')+0.3,0.1)
# LEADIMOB
sweep(T4-0.2,0.7,500,4500,0.07,'rise');pop(T4+0.25,0.06,800,0.5)
chime(WF(9,'leadimob')-0.1,[62,67,70,74],0.03,1.6);pop(T4+0.55,0.05,640,0.3)
f0=WF(9,'esse')-0.1;snd=WF(9,'certo')-0.05
pop(f0,0.06,900,0.5)
k=0
while f0+0.3+k*0.26<snd-0.1: tick(f0+0.3+k*0.26,0.03,1500 if k%2 else 1250,0.5);k+=1
click(snd,0.09,0.55);pop(snd+0.12,0.08,1000,0.65);chime(snd+0.15,[74,79,86],0.025,1.6)
t3=WF(9,'memória')-0.15
for k in range(3): tick(WF(9,'depender')+k*0.16,0.025,1100,0.3)
pop(t3,0.07,720,0.3);ding(t3+0.05,0.03,79,0.35)
chime(WF(9,'ninguém')+0.05,[67,74,79,82],0.03,1.5)
# CTA
sweep(WIPE-0.7,0.7,300,7000,0.07,'rise');impact(WIPE+0.02,0.26);chime(WIPE+0.08,[55,62,67,70],0.025,1.5)
w0=WF(10,'diagn')
for k in range(11): click(w0-0.05+k*0.055,0.045,0.35+0.3*(k%2))
sd=WF(10,'e')+0.1;click(sd,0.1,0.6);pop(sd+0.05,0.06,800,0.4)
sweep(WIPE+0.45,0.8,400,5000,0.04);chime(WIPE+0.7,[62,67,70,74],0.03,1.4)
chime(WF(10,'receba')+0.5,[67,74,79,82],0.035,1.1);ding(WF(10,'completo')+0.3,0.03,86,0.5)
# ---------------- voice ----------------
V=np.zeros(N)
for c in TL:
    sr,x=wavfile.read(f"vo_b/p{c['i']:02d}.wav");x=x.astype(np.float64)/32768.0
    if x.ndim>1: x=x.mean(1)
    if sr!=SR: x=resample_poly(x,SR,sr)
    add(V,x,c['start'])
env=lp(np.abs(V),6);env=np.clip(env/0.05,0,1);duck=1-0.55*env
fade=np.clip(T/0.05,0,1)*np.clip((END-T)/1.4,0,1)
L*=duck*fade;R*=duck*fade
vr=np.sqrt(np.mean(V[lp(np.abs(V),6)>0.01]**2));mr=np.sqrt(np.mean(((L+R)/2)**2))
gm=vr*10**(-11/20)/mr;L*=gm;R*=gm;FL*=gm*fade;FR*=gm*fade
sfr=np.sqrt(np.mean(((FL+FR)/2)**2)); FL*=vr*10**(-15/20)/sfr; FR*=vr*10**(-15/20)/sfr
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_novo.wav',L+FL,R+FR);save('mix_vo.wav',(L+FL)+V,(R+FR)+V)
print('END',round(END,2),'gain',round(gm,3))
