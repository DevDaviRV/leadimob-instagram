"""Leadimob R1 08/10 — trilha original: 92 BPM, Lá menor -> Fá maior. Hook tenso e esparso -> inbox (ruído que se repete) -> triagem (groove abre) -> Leadimob (maior, brilhante) -> CTA.
Uso: python3 trilha.py -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[9]['end']+2.3; N=int((END+0.5)*SR); T=np.arange(N)/SR
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
BPM=92; beat=60/BPM; bar=4*beat
T1=C[3]['start']-0.4; T2=C[6]['start']-0.5; T3=C[7]['start']-0.4; WIPE=C[9]['start']-0.3
T0=T2-np.ceil(T2/bar)*bar            # um tempo forte cai no zoom-through
def sec(t):
    if t<T1: return 'hook'
    if t<T2: return 'inbox'
    if t<T3: return 'tri'
    if t<WIPE: return 'prod'
    return 'cta'
prog=[[45,57,60,64,67,71],[41,60,64,67,72,76],[48,60,64,67,71,76],[43,59,62,67,71,74]]  # Am9 Fmaj9 Cmaj9 G6/9
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
n=int((T1+0.3)*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(33)*tt)+0.4*np.sin(2*np.pi*midi(45)*tt*1.002))*0.05*np.clip(tt/1.5,0,1)*np.clip((T1+0.3-tt)/0.5,0,1)
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
# HOOK: mensagens caindo, risco em "mais leads", virada para "menos conversas"
for j in range(10):
    ding(0.1+j*0.33+rng.random()*0.1,0.014+0.01*rng.random(),int(rng.choice([81,83,86,88,91])),rng.random())
sweep(WF(1,'mais'),0.5,4500,900,0.05);thud(WF(1,'leads')+0.1,0.14)
sweep(WF(2,'menos')-0.15,0.7,500,3500,0.06,'rise');click(WF(2,'menos'),0.06,0.5)
sweep(T1-0.7,0.7,400,4200,0.08,'rise')
# INBOX: linhas entrando, perguntas repetidas, noite
for i in range(6): pop(C[3]['start']-0.15+i*0.13,0.05,700+i*60,0.2+0.12*i)
for k,x in enumerate([0,.25,.12,.37]): tick(WF(4,'repetidas')+x,0.05,2000+k*160,0.3+k*0.15)
ding(WF(4,'repetidas')+0.05,0.025,76,0.5)
thud(WF(5,'onze'),0.13);ding(WF(5,'noite'),0.03,64,0.5)
for k in range(4): ding(WF(5,'noite')+0.12+k*0.12,0.012,62-k,0.4)
# TRIAGEM: zoom-through, gate, passagem, linhas preenchidas
sweep(T2-0.2,0.7,300,6500,0.1,'rise');impact(T2+0.15,0.3);chime(T2+0.2,[57,64,69],0.02,1.6)
sweep(WF(6,'triagem')-0.2,0.5,900,3500,0.05)
for k in range(10): click(C[6]['start']+0.1+k*0.28,0.02,0.2+0.6*(k%2))
tc=WF(6,'corretor');sweep(tc-0.5,0.5,500,2600,0.07,'rise');thud(tc-0.08,0.15);pop(tc+0.2,0.07,820,0.5)
pop(WF(6,'entra'),0.05,1000,0.7)
for w,f in [('perfil',2200),('orçamento',2350),('visita',2500)]: tick(WF(6,w),0.05,f);pop(WF(6,w)+0.02,0.04,900,0.5)
chime(WF(6,'visita')+0.35,[69,73,76,81],0.03,1.6)
# T3 match cut
sweep(T3-0.1,0.8,2400,500,0.06);tick(T3+0.65,0.07,1800)
# LEADIMOB
pop(C[7]['start']+0.1,0.06,800,0.5);chime(WF(7,'leadimob'),[64,69,73,76],0.03,1.6)
pop(WF(7,'leadimob')+0.2,0.06,640,0.4)
ai=WF(8,'atende')-0.1
for k in range(3): tick(ai+0.05+k*0.15,0.03,1200,0.6)
pop(ai+0.55,0.08,1000,0.6);chime(ai+0.7,[73,78,85],0.025,1.8)
sw0=WF(8,'qualifica')-0.12
sweep(sw0,0.35,900,3500,0.05);chime(WF(8,'qualifica')+0.1,[69,76,81],0.03,1.6)
for i in range(3): tick(sw0+0.35+i*0.2,0.045,2200+i*100);pop(sw0+0.36+i*0.2,0.03,900,0.5)
tick(sw0+0.9,0.06,2600)
sw1=WF(8,'passa')-0.12
sweep(sw1,0.35,900,3500,0.05);buzz(WF(8,'passa')+0.1,0.5,0.07);ding(WF(8,'passa')+0.15,0.04,81,0.6)
pop(WF(8,'quem'),0.05,760,0.5)
tk=WF(8,'passo')+0.05;click(tk,0.1,0.55);chime(tk+0.1,[66,69,73,76],0.03,1.5)
# WIPE + CTA
sweep(WIPE-0.9,0.9,300,9000,0.09,'rise');impact(WIPE,0.34);chime(WIPE+0.05,[57,64,69,73],0.025,1.5)
w0=WF(9,'diagn')
for k in range(11): click(w0-0.05+k*0.055,0.045,0.35+0.3*(k%2))
sd=WF(9,'e')+0.35;click(sd,0.1,0.6);pop(sd+0.05,0.06,800,0.4)
chime(WF(9,'checklist')-0.1,[64,69,73,76],0.03,1.4)
sweep(WF(9,'checklist')-0.25,0.8,400,5000,0.04)
chime(WF(9,'completo')+0.3,[69,76,81,85],0.035,1.1);ding(WF(9,'completo')+0.5,0.03,88,0.5)
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
