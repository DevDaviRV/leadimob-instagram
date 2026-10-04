"""Leadimob R1 06/10 (modo incorporador) — trilha original: 96 BPM, Ré maior (Dmaj9 Bm7 Gmaj7 A6/9), pad aberto + kalimba, groove leve a partir da cena C.
Uso: python3 trilha.py -> mix_novo.wav e mix_vo.wav"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[11]['end']+1.5; N=int((END+0.5)*SR); T=np.arange(N)/SR
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
        if w['w'].lower().startswith(s.lower()): return float(w['t'])
    return float(C[i]['start'])
def saw(f,n,det=0.0):
    ph=np.cumsum(np.full(n,f*(1+det))/SR); return 2*(ph%1)-1
BPM=96; beat=60/BPM; bar=4*beat
T0=4.2-np.ceil(4.2/bar)*bar     # um tempo forte cai na entrada da cena B
def sec(t):
    if t<3.9: return 'hook'
    if t<10.2: return 'wave'
    if t<30.2: return 'prod'
    if t<34.0: return 'view'
    return 'cta'
prog=[[50,62,66,69,73,76],[47,62,66,69,73,78],[43,62,66,71,74,78],[45,61,64,69,73,76]]
L=np.zeros(N);R=np.zeros(N)
nb=int((END-T0)/bar)+2
PL=np.zeros(N);PR=np.zeros(N)
for b in range(0,nb):
    st=T0+b*bar
    if st>END: break
    ch=prog[b%4]; n=int((bar+1.6)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.7)*np.clip((bar+1.6-tt)/1.6,0,1)
    for m in ch[1:]:
        for d,pan in((-0.005,.25),(0.005,.75)):
            s=saw(midi(m),n,d)*env*0.011; add(PL,s*(1-pan),st); add(PR,s*pan,st)
cv={'hook':.2,'wave':.4,'prod':.8,'view':.6,'cta':1.0}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(24000)/24000,'same')
L+=lp(PL,500)*(1-ctrl)+lp(PL,3400)*ctrl; R+=lp(PR,500)*(1-ctrl)+lp(PR,3400)*ctrl
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
arp=[0,2,4,2,3,5,4,2]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.3: continue
    s_=sec(t); pos=k%16; b=int((t-T0)//bar); ch=prog[b%4]
    groove=s_ in('prod','cta') ; light=s_ in('wave','view')
    if groove and pos in(0,10) or (s_=='cta' and pos in(0,6,8,12)):
        n=int(0.4*SR);tt=np.arange(n)/SR;fk=46+95*np.exp(-tt*32)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*8)*0.26;add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if groove and pos in(4,12):
        n=int(0.2*SR);tt=np.arange(n)/SR;cp=bp(rng.standard_normal(n),1500,5500)*np.exp(-tt*30)*0.035;add(L,cp,t);add(R,cp*.9,t)
    if (groove and pos%2==0) or (s_=='wave' and pos%4==0 and t>6.0) or (light and pos%8==0):
        n=int(0.04*SR);tt=np.arange(n)/SR;h=hp(rng.standard_normal(n),9000)*np.exp(-tt*140)*0.016*[.8,.3,.6,.3][pos%4];pan=0.3+0.4*((k*3)%5)/4;add(L,h*(1-pan),t);add(R,h*pan,t)
    if pos in(0,8) and s_!='hook':
        n=int(beat*2*SR*0.95);tt=np.arange(n)/SR;f=midi(ch[0]-12);x=(np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt))*np.exp(-tt*1.6)*(0.085 if groove else 0.05);add(BL,x,t)
    if (groove or s_=='view') and pos%2==0 or (s_=='wave' and pos%4==0):
        m=ch[1:][arp[(k//2)%8]%5]+12;n=int(0.5*SR);tt=np.arange(n)/SR
        x=(np.sin(2*np.pi*midi(m)*tt)+0.2*np.sin(2*np.pi*midi(m)*4*tt)*np.exp(-tt*20))*np.exp(-tt*7)*(0.02 if s_!='view' else 0.016)
        add(AL,x,t);add(AR,x*0.7,t)
d=int(beat*0.5*SR)
for rep in range(1,4):
    g=0.3**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.28*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.4*np.exp(-tt/0.09)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
n=int(4.4*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(38)*tt)+0.35*np.sin(2*np.pi*midi(50)*tt*1.002))*0.04*np.clip(tt/1.2,0,1)*np.clip((4.4-tt)/0.5,0,1)
add(L,dr,0);add(R,dr,0)
ir_n=int(2.2*SR);tt=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-tt*2.6);irR=rng.standard_normal(ir_n)*np.exp(-tt*2.6);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.25*fftconvolve(hp(L,300),irL)[:N];R=R+0.25*fftconvolve(hp(R,300),irR)[:N]
# ---- SFX
FL=np.zeros(N);FR=np.zeros(N)
def st2(x,at,pan=.5,g=1): add(FL,x*(1-pan)*1.4*g,at);add(FR,x*pan*1.4*g,at)
def sweep(at,dur,f0,f1,g,env='bell'):
    n=int(dur*SR);tt=np.arange(n)/SR;x=rng.standard_normal(n);out=np.zeros(n);seg=960
    for i in range(0,n,seg):
        k=i/n;f=f0+(f1-f0)*(k**2 if env=='rise' else np.sin(np.pi*k));out[i:i+seg]=bp(x[max(0,i-3000):i+seg],max(60,f*0.7),min(f*1.45,20000))[-len(out[i:i+seg]):]
    e=(tt/dur)**2 if env=='rise' else np.sin(np.pi*tt/dur)**2
    pan=np.linspace(.25,.75,n);s=out*e*g;add(FL,s*(1-pan),at);add(FR,s*pan,at)
def impact(at,g=0.28):
    n=int(1.6*SR);tt=np.arange(n)/SR;f=36+70*np.exp(-tt*9)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.8)*g;add(FL,s,at);add(FR,s,at)
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
def buzz(at,dur=0.5,g=0.06):
    n=int(dur*SR);tt=np.arange(n)/SR;x=np.sin(2*np.pi*170*tt)*(0.5+0.5*np.sign(np.sin(2*np.pi*9*tt)))*np.sin(np.pi*tt/dur)*g;add(FL,x,at);add(FR,x,at)
# hook: unidades acendem
for j in range(14): tick(0.8+j*0.2+rng.random()*0.05,0.02,1800+j*90,0.2+0.6*rng.random())
chime(WF(2,'leadimob')-0.05,[62,69,74],0.03,1.6); sweep(3.45,0.7,500,5500,0.08,'rise'); impact(3.98,0.2)
# wave: mensagens
BT=[4.5,5.08,5.58,6.02,6.42,6.78,7.1,7.38,7.64,7.88,8.1,8.3,8.5,8.7,8.9,9.08,9.28]
for i,bt in enumerate(BT): ding(bt,0.022+0.008*(i/16),int([86,88,90,83,93][i%5]),0.2+0.6*((i*3)%7)/6)
buzz(WF(4,'consegue'),0.45,0.06); pop(9.28,0.06,700)
sweep(9.5,0.8,300,3500,0.06,'rise')
# C
for k in range(3): tick(11.95+k*0.12,0.035,1300+k*100,0.6)
pop(12.42,0.08,1000,0.65); chime(WF(5,'empreendimento')-0.05,[69,74,81],0.03,1.6); sweep(14.1,0.6,800,4000,0.05)
# push C->D
sweep(16.3,0.7,300,6000,0.09,'rise'); impact(16.95,0.18)
for k in range(10): click(17.0+k*0.07,0.02,0.2+0.06*k)
tick(WF(6,'disponíveis'),0.05,2200); sweep(WF(6,'disponíveis'),0.6,700,4000,0.04)
pop(WF(6,'tabela')-0.2,0.06,800); chime(WF(6,'vigente')+0.05,[69,73,76],0.03,1.6)
# E
for i,w in enumerate(['perfil']): pass
for a in (22.45,22.9,23.2): tick(a,0.05,2000+int(a*10)%300)
ding(WF(7,'direciona'),0.03,81,0.5); sweep(WF(7,'direciona'),0.5,900,3600,0.05)
chime(WF(7,'certo')-0.1,[66,73,78],0.03,1.6); sweep(25.2,0.8,300,5000,0.08,'rise'); impact(25.95,0.14)
# F
pop(WF(8,'lead')-0.1,0.06,760,0.4); sweep(WF(8,'consultor')-0.2,0.5,1000,3500,0.05)
for k in range(3): tick(WF(8,'agenda')+0.1+k*0.14,0.045,1900+k*180,0.3+0.2*k)
tick(WF(8,'visita')-0.2,0.05,1500); chime(WF(8,'visita')+0.05,[64,69,73,76],0.035,1.5)
# zoom through
sweep(29.8,0.7,250,5500,0.09,'rise'); impact(30.3,0.2)
# G
for i in range(4): tick(31.1+i*0.12,0.04,2100+i*140)
sweep(WF(9,'campanha')-0.3,0.4,900,3000,0.05); click(WF(9,'campanha')-0.1,0.07,0.6)
for i in range(4): tick(WF(9,'campanha')+i*0.08,0.035,2300)
# CTA
sweep(33.2,0.9,250,8500,0.09,'rise'); impact(33.9,0.3); chime(34.0,[57,66,69,73],0.03,1.2)
chime(WF(10,'demonstr')-0.2,[69,76,81,85],0.035,1.1)
pop(WF(11,'link')-0.05,0.07,900,0.5); chime(WF(11,'bio'),[74,78,85],0.03,1.4)
# ---- voz
V=np.zeros(N)
for c in TL:
    sr,x=wavfile.read(f"vo_b/p{c['i']:02d}.wav");x=x.astype(np.float64)/32768.0
    if x.ndim>1: x=x.mean(1)
    if sr!=SR: x=resample_poly(x,SR,sr)
    add(V,x,c['start'])
env=lp(np.abs(V),6);env=np.clip(env/0.05,0,1);duck=1-0.55*env
fade=np.clip(T/0.05,0,1)*np.clip((END-T)/1.3,0,1)
L*=duck*fade;R*=duck*fade
vr=np.sqrt(np.mean(V[lp(np.abs(V),6)>0.01]**2));mr=np.sqrt(np.mean(((L+R)/2)**2))
gm=vr*10**(-11/20)/mr;L*=gm;R*=gm;FL*=gm*fade;FR*=gm*fade
sfr=np.sqrt(np.mean(((FL+FR)/2)**2)); FL*=vr*10**(-15/20)/sfr; FR*=vr*10**(-15/20)/sfr
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_novo.wav',L+FL,R+FR);save('mix_vo.wav',(L+FL)+V,(R+FR)+V)
print('END',round(END,2),'gain',round(gm,3))
