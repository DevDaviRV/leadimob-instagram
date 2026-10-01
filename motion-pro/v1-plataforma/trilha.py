"""Leadimob v1 — trilha original: 118 BPM, Fá# menor/Lá maior, tensão (hook/noite) -> groove (produto) -> breakdown (controle) -> resolução (CTA).
Uso: python3 trilha.py  -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[15]['end']+2.6; N=int((END+0.5)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(7)
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
        if w['w'].lower().startswith(s.lower()): return w['t']
    return C[i]['start']
def saw(f,n,det=0.0):
    ph=np.cumsum(np.full(n,f*(1+det))/SR); return 2*(ph%1)-1
BPM=118; beat=60/BPM; bar=4*beat
WIPE=C[5]['start']-0.28
T0=WIPE-np.ceil(WIPE/bar)*bar          # grid anchored so a downbeat lands on the wipe
HUM=C[13]['start']-0.6; ED=C[14]['start']-0.2; CTA=C[15]['start']-0.42
ST=[C[i]['start']-0.75 for i in range(7,13)]
def sec(t):
    if t<C[3]['start']-0.4: return 'hook'
    if t<WIPE: return 'night'
    if t<C[7]['start']-0.75: return 'turn'
    if t<HUM: return 'prod'
    if t<ED: return 'hum'
    if t<CTA: return 'ed'
    return 'cta'
prog=[[42,61,64,66,69,73],[38,62,66,69,73,76],[45,61,64,69,71,76],[40,59,64,68,71,76]]  # F#m9 Dmaj9 A6/9 E/G#
L=np.zeros(N);R=np.zeros(N)
nb=int((END-T0)/bar)+2
# ---- pad (filtered saw, opens with sections)
PL=np.zeros(N);PR=np.zeros(N)
for b in range(0,nb,2):
    st=T0+b*bar
    if st>END: break
    ch=prog[(b//2)%4]; n=int((2*bar+1.8)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.9)*np.clip((2*bar+1.8-tt)/1.8,0,1)
    for m in ch[1:]:
        for d,pan in((-0.006,.2),(0.006,.8)):
            s=saw(midi(m),n,d)*env*0.010; add(PL,s*(1-pan),st); add(PR,s*pan,st)
cv={'hook':.15,'night':.1,'turn':.6,'prod':.85,'hum':.35,'ed':.7,'cta':1.0}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(19200)/19200,'same')
PLd,PRd,PLo,PRo=lp(PL,500),lp(PR,500),lp(PL,3600),lp(PR,3600)
L+=PLd*(1-ctrl)+PLo*ctrl; R+=PRd*(1-ctrl)+PRo*ctrl
# ---- rhythm section
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
pat=[0,3,1,4,2,4,1,3]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.2: continue
    s_=sec(t); pos=k%16; b=int((t-T0)//bar); ch=prog[(b//2)%4]
    full=s_ in('prod','cta'); grooveK=s_ in('turn','prod','cta','ed')
    # progressive density across product stations
    lvl=sum(t>=x for x in ST) if s_=='prod' else 0
    if grooveK and (pos in(0,8) or (full and pos in(6,)) or (s_=='ed' and pos in(0,4,8,12) and t>ED+1.5)):
        n=int(0.45*SR);tt=np.arange(n)/SR;fk=42+110*np.exp(-tt*30)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*7)*0.32+hp(rng.standard_normal(n),3000)*np.exp(-tt*240)*0.03
        add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if (full or s_=='turn') and pos in(4,12):
        n=int(0.25*SR);tt=np.arange(n)/SR;cp=bp(rng.standard_normal(n),1200,6000)*(np.exp(-tt*24)+0.4*np.exp(-np.abs(tt-0.012)*300))*0.06
        add(L,cp,t);add(R,cp*0.9,t)
    if (full and (pos%2==0 or lvl>=2)) or (s_=='turn' and pos%4==2) or (s_=='night' and pos%4==0):
        n=int(0.04*SR);tt=np.arange(n)/SR;vel=[.8,.25,.55,.3][pos%4]*(0.5 if s_=='night' else 1)
        h=hp(rng.standard_normal(n),9000)*np.exp(-tt*130)*0.024*vel;pan=0.25+0.5*((k*5)%7)/6;add(L,h*(1-pan),t);add(R,h*pan,t)
    if pos%2==0 and s_ not in('hook',):
        n=int(beat/2*SR*0.9);tt=np.arange(n)/SR;f=midi(ch[0]-12 if full else ch[0])
        g={'night':0.035,'turn':0.08,'prod':0.1,'hum':0.03,'ed':0.07,'cta':0.1}[s_]
        if s_ in('night','hum') and pos%8!=0: g=0
        x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt))*np.exp(-tt*3.5)*g; add(BL,x,t)
    if (full and pos%2==0) or (s_=='turn' and pos%4==0) or (s_=='ed' and pos%2==0):
        m=ch[1:][pat[(k//2)%8]]+12;n=int(0.3*SR);tt=np.arange(n)/SR
        x=lp(saw(midi(m),n)*np.exp(-tt*11),3000)*(0.016+0.003*min(lvl,3)); add(AL,x,t);add(AR,x*0.75,t)
    if full and lvl>=3 and pos in(3,10,14):
        m=ch[3]+24;n=int(0.25*SR);tt=np.arange(n)/SR;x=np.sin(2*np.pi*midi(m)*tt)*np.exp(-tt*13)*0.018;add(AL,x*0.6,t);add(AR,x,t)
d=int(beat*0.75*SR)
for rep in range(1,4):
    g=0.33**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.5*np.exp(-tt/0.09)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
# hook/night drone
n=int((WIPE+0.3)*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(30)*tt)+0.4*np.sin(2*np.pi*midi(42)*tt*1.002))*0.05*np.clip(tt/1.5,0,1)*np.clip((WIPE+0.3-tt)/0.4,0,1)
add(L,dr,0);add(R,dr,0)
ir_n=int(2.4*SR);tt=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-tt*2.4);irR=rng.standard_normal(ir_n)*np.exp(-tt*2.4);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.28*fftconvolve(hp(L,300),irL)[:N];R=R+0.28*fftconvolve(hp(R,300),irR)[:N]
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
def pop(at,g=0.07,f=900,pan=.5):   # message bubble
    n=int(0.14*SR);tt=np.arange(n)/SR;fr=f*(1+0.6*np.exp(-tt*60));st2(np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*38)*g,at,pan)
def ding(at,g=0.04,m=88,pan=.5):   # notification
    n=int(0.9*SR);tt=np.arange(n)/SR;f=midi(m);x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2.76*f*tt)*np.exp(-tt*9))*np.exp(-tt*6)*g;st2(x,at,pan)
def chime(at,notes,g=0.035,dec=1.4):
    n=int(3*SR);tt=np.arange(n)/SR;s=np.zeros(n)
    for i,m in enumerate(notes):
        dd=int(i*0.07*SR);f=midi(m);s[dd:]+=(np.sin(2*np.pi*f*tt[:n-dd])+0.22*np.sin(2*np.pi*2.01*f*tt[:n-dd]))*np.exp(-tt[:n-dd]*dec)
    add(FL,s*g,at);add(FR,s*g,at)
def click(at,g=0.05,pan=.5):
    n=int(0.02*SR);tt=np.arange(n)/SR;st2(hp(rng.standard_normal(n),2500)*np.exp(-tt*400)*g,at,pan)
def buzz(at,dur=0.55,g=0.08):
    n=int(dur*SR);tt=np.arange(n)/SR;x=np.sin(2*np.pi*170*tt)*(0.5+0.5*np.sign(np.sin(2*np.pi*9*tt)))*np.sin(np.pi*tt/dur)*g;add(FL,x,at);add(FR,x,at)
def thud(at,g=0.2):
    n=int(0.8*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*(48+30*np.exp(-tt*20))*tt)*np.exp(-tt*6)*g;add(FL,s,at);add(FR,s,at)
# HOOK: notifications raining, strike, loss
for j in range(16):
    t=0.05+j*0.26+rng.random()*0.12; ding(t,0.018+0.012*rng.random(),int(rng.choice([83,85,88,90,92])),rng.random())
sweep(WF(1,'leads')-0.2,0.45,5000,900,0.06);thud(WF(1,'leads')+0.2,0.16)
tw=WF(2,'perder');sweep(tw,1.1,2400,300,0.05)
for k in range(5): ding(tw+0.1+k*0.16,0.012*(1-k/6),int(80-k*2),0.2+k*0.15)
sweep(C[3]['start']-0.7,0.7,400,4000,0.08)
# NIGHT: clock ticks, alert, time-lapse, loss
for k in range(int((C[4]['start']-C[3]['start'])/0.5)): tick(C[3]['start']+0.25+k*0.5,0.03,1300 if k%2 else 1600,0.35+0.3*(k%2))
pop(C[3]['start']+0.1,0.05,700,0.4)
thud(WF(3,'ninguém'),0.12);ding(WF(3,'ninguém')+0.05,0.03,66,0.5)
tm=WF(4,'manhã')-0.35
for k in range(22): tick(tm+ (k/22)**0.8*1.0,0.028,1800+k*40,0.2+0.6*(k%2))
sweep(tm,1.1,300,5000,0.07,'rise');pop(WF(4,'lead'),0.05,600,0.45)
thud(WF(4,'outro'),0.18)
# WIPE into product
sweep(WIPE-0.9,0.9,300,9000,0.09,'rise');impact(WIPE,0.36);chime(WIPE+0.05,[61,66,73],0.02,1.6)
m2t=WF(5,'atende')+0.05
for k in range(6): click(C[5]['start']+0.05+k*0.14,0.025,0.6)
pop(m2t,0.08,1000,0.6);chime(WF(5,'hora'),[73,78,85],0.03,1.8)
sweep(WF(6,'catálogo')-0.3,1.0,500,5000,0.06);ding(WF(6,'vinte'),0.035,85,0.7)
# STATIONS
for i,a in enumerate(ST): sweep(a-0.05,0.75,500,6500,0.11); tick(a+0.7,0.05,1600+i*150)
for w in ['entende','cliente','procura']: tick(WF(7,w),0.045,2200)
tick(WF(7,'procura')+0.35,0.045,2300);chime(WF(7,'qualifica')+0.1,[69,76,81],0.03,1.6)
for k in range(12): click(C[8]['start']+k*0.075,0.03,0.4)
pop(WF(8,'certo'),0.06,700);sweep(WF(8,'certo'),0.5,1200,4000,0.04)
for k in range(3): click(WF(8,'fotos')-0.2+k*0.05,0.06,0.3+k*0.2)
pop(WF(8,'envia'),0.07,1000,0.6)
for k in range(3): tick(WF(9,'horários')+k*0.12,0.045,2000+k*200,0.3+k*0.2)
pop(WF(9,'deixa'),0.06,1000,0.6);chime(WF(9,'agendada')+0.05,[64,69,73,76],0.035,1.5)
sweep(WF(10,'funil')-0.1,0.4,900,3500,0.05);sweep(WF(10,'sozinha')-0.1,0.4,900,3500,0.05)
tick(WF(10,'funil')+0.25,0.05,1500);tick(WF(10,'sozinha')+0.25,0.05,1700)
for k in range(3): tick(WF(10,'resumo')+0.1+k*0.22,0.04,2400)
pop(WF(11,'follow'),0.07,1000,0.6);pop(WF(11,'esfriou')+0.25,0.07,760,0.4);chime(WF(11,'esfriou')+0.4,[69,73,76],0.025,1.6)
cb=WF(12,'nasce')-0.15;click(cb,0.09,0.6);pop(cb+0.12,0.07,800,0.4);ding(WF(12,'leads'),0.03,88,0.5)
# HUMAN
pop(WF(13,'hora'),0.06,760,0.4);buzz(WF(13,'ela'),0.5,0.07);ding(WF(13,'ela')+0.05,0.035,81,0.6)
click(WF(13,'você'),0.09,0.55);chime(WF(13,'você')+0.15,[66,69,73],0.02,1.5)
# EDITORIAL -> CTA
sweep(C[14]['start'],0.9,400,3000,0.04);sweep(CTA-1.3,1.3,250,9000,0.09,'rise')
impact(CTA+0.02,0.34);chime(CTA+0.05,[57,64,69,73],0.03,1.2)
chime(WF(15,'demonstr')-0.1,[69,76,81,85],0.035,1.1)
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
# SFX loudness relative to voice: keep audible but under the voice
sfr=np.sqrt(np.mean(((FL+FR)/2)**2)); FL*=vr*10**(-15/20)/sfr; FR*=vr*10**(-15/20)/sfr
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_novo.wav',L+FL,R+FR);save('mix_vo.wav',(L+FL)+V,(R+FR)+V)
print('END',round(END,2),'gain',round(gm,3))
