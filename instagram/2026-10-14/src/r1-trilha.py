"""Leadimob R1 14/10 — trilha original: 100 BPM, Sol menor -> Si bemol maior.
Arranjo novo: marimba FM (madeira) em vez de pluck/serra, pad de seno, baixo sub, aro e vassourinha.
Gancho (marimba esparsa, Sol menor, o campo pisca) -> a mensagem genérica (teclas, envio) ->
O TRABALHO VOLTA PARA O CLIENTE (a música para no giro, só um grave) -> os dois ingredientes (abre em Si bemol) ->
o exemplo (groove) -> tese (pad, bumbo no 1) -> Leadimob (groove cheio) -> CTA (resolve em Si bemol).
Uso: /usr/bin/python3 trilha.py -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[8]['end']+1.9; N=int((END+0.5)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(1410)
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
MC={}
def mar(m,dur=0.7):
    if m in MC: return MC[m]
    n=int(dur*SR);tt=np.arange(n)/SR;f=midi(m)
    mod=np.sin(2*np.pi*f*4.0*tt)*2.2*np.exp(-tt*30)
    x=np.sin(2*np.pi*f*tt+mod)*np.exp(-tt*7)+0.25*np.sin(2*np.pi*f*3.93*tt)*np.exp(-tt*22)
    x*=np.minimum(1,tt/0.002); MC[m]=x; return x
BPM=100; beat=60/BPM; bar=4*beat
TA=C[2]['start']-0.3; TB=C[3]['start']-0.4; TC=C[4]['start']-0.42
TD=C[5]['start']-0.36; RE=WF(5,'investir')+0.05; TE=C[6]['start']-0.1; TL7=WF(7,'leadimob')-0.3; TF=WF(7,'abre')-0.15; TG=C[8]['start']-0.42
T0=(TC+0.2)-np.ceil((TC+0.2)/bar)*bar      # tempo forte quando os ingredientes entram
def sec(t):
    if t<TA: return 'hook'
    if t<TB: return 'gen'
    if t<TC+0.2: return 'trab'
    if t<TD: return 'ing'
    if t<TE: return 'ex'
    if t<TF: return 'tese'
    if t<TG: return 'prod'
    return 'cta'
MIN=[[31,58,62,65,69],[27,58,63,67,70],[34,58,62,65,70],[26,57,62,66,69]]      # Gm9 Ebmaj7 Bb D
MAJ=[[34,58,62,65,69,72],[27,58,63,67,70,74],[31,58,62,65,70,74],[29,57,60,65,69,72]]  # Bbmaj7 Ebmaj9 Gm7 F
def chord(t):
    b=int(np.floor((t-T0)/bar)); s=sec(t)
    if s in('hook','gen','trab'): return MIN[b%4]
    if s=='tese': return MAJ[1]
    if s=='cta': return MAJ[0]
    return MAJ[b%4]
L=np.zeros(N);R=np.zeros(N)
PLp=np.zeros(N);PRp=np.zeros(N)
nb=int((END-T0)/bar)+2
for b in range(nb):
    st=T0+b*bar
    if st>END or st+bar<0: continue
    ch=chord(max(st+0.01,0)); n=int((bar+1.2)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.7)*np.clip((bar+1.2-tt)/1.2,0,1)
    for j,m in enumerate(ch[1:]):
        f=midi(m); x=(np.sin(2*np.pi*f*tt)+0.2*np.sin(2*np.pi*2*f*tt+0.3))*env*0.011
        pan=0.3+0.4*(j%2); add(PLp,x*(1-pan),st); add(PRp,x*pan,st)
cv={'hook':.4,'gen':.45,'trab':0.0,'ing':.8,'ex':1.0,'tese':.65,'prod':1.0,'cta':.85}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(9600)/9600,'same')
L+=lp(PLp,2400)*ctrl; R+=lp(PRp,2400)*ctrl
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
arp=[0,2,4,1,3,2,4,3]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.0: continue
    s=sec(t); pos=k%16; ch=chord(t)
    if s=='trab': continue
    full=s in('ex','prod')
    if (s in('ing','ex','prod') and pos in(0,7,10)) or (s in('tese','cta','gen') and pos==0):
        n=int(0.4*SR);tt=np.arange(n)/SR;fk=44+100*np.exp(-tt*30)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*8)*(0.2 if s=='gen' else 0.28)
        add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if full and pos in(4,12):   # aro
        n=int(0.1*SR);tt=np.arange(n)/SR;rm=(bp(rng.standard_normal(n),1800,5000)*np.exp(-tt*55)+np.sin(2*np.pi*900*tt)*np.exp(-tt*70)*0.4)*0.04
        add(L,rm,t);add(R,rm*0.8,t)
    if full or (s in('ing','cta') and pos%4==2):   # vassourinha
        n=int(0.09*SR);tt=np.arange(n)/SR;vel=[.8,.25,.5,.3][pos%4]
        h=bp(rng.standard_normal(n),3000,9000)*np.minimum(1,tt/0.015)*np.exp(-tt*40)*0.016*vel;pan=0.4+0.2*((k*3)%5)/4;add(L,h*(1-pan),t);add(R,h*pan,t)
    if pos in(0,8) and s!='hook' or (s=='hook' and pos==0):
        n=int(beat*2*SR*0.9);tt=np.arange(n)/SR;f=midi(ch[0])
        g={'hook':0.06,'gen':0.06,'ing':0.1,'ex':0.11,'tese':0.07,'prod':0.11,'cta':0.1}[s]
        x=(np.sin(2*np.pi*f*tt)+0.2*np.sin(4*np.pi*f*tt))*np.minimum(1,tt/0.01)*np.exp(-tt*1.5)*g; add(BL,x,t)
    if (s=='hook' and pos%8==0) or (s=='gen' and pos%8==4) or (s in('ing','tese','cta') and pos%4==0) or (full and pos%2==0):
        m=ch[1:][arp[(k//2)%8]%len(ch[1:])]+12
        x=mar(m)*(0.05 if full else 0.045)
        pan=0.3+0.4*((k//2)%2); add(AL,x*(1-pan),t); add(AR,x*pan,t)
d=int(beat*0.75*SR)
for rep in range(1,3):
    g=0.28**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.28*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.4*np.exp(-tt/0.08)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
# o trabalho volta para o cliente: só um grave de Sol
n=int((TC+0.3-TB)*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(31)*tt)+0.3*np.sin(2*np.pi*midi(43)*tt*1.003))*0.035*np.clip(tt/0.5,0,1)*np.clip((TC+0.3-TB-tt)/0.3,0,1)
add(L,dr,TB);add(R,dr,TB)
ir_n=int(2.0*SR);tt=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-tt*3.0);irR=rng.standard_normal(ir_n)*np.exp(-tt*3.0);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.22*fftconvolve(hp(L,300),irL)[:N];R=R+0.22*fftconvolve(hp(R,300),irR)[:N]
# ---------------- SFX ----------------
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
# gancho: o campo
chime(0.05,[67,70,74],0.018,1.8)
# mensagem genérica digitada e enviada
pop(0.08,0.045,1000,0.7)
sweep(TA-0.1,0.9,700,2600,0.035);pop(TA+0.6,0.035,1500,0.7)
for i in range(2): pop(WF(2,'dificilmente')+0.05+i*0.5,0.045,520-i*60,0.4+0.2*i)
# giro
whoosh_side(TB,1.0,0.06,True);thud(TB+0.55,0.12)
for i in range(4): click(WF(3,'devolve')+i*0.16,0.025,0.3+0.1*i)
pop(WF(3,'cliente')+0.05,0.05,420,0.5)
# para dentro: os ingredientes
sweep(TC-0.35,0.7,400,5200,0.07,'rise');impact(TC+0.2,0.22)
pop(WF(4,'cita')-0.12,0.05,800,0.4);chime(WF(4,'imóvel')+0.1,[70,74,77],0.022,1.6)
pop(WF(4,'faz')-0.12,0.05,900,0.6);chime(WF(4,'fácil')+0.05,[74,77,82],0.022,1.6)
# exemplo
sweep(TD-0.15,0.8,2600,900,0.04);swoosh_send(TD,0.04);pop(TD+0.7,0.05,950,0.7)
pop(RE-0.7,0.03,1500,0.3);pop(RE,0.07,720,0.3);chime(RE+0.2,[70,74,77,82],0.026,1.4)
# zoom para a tese
sweep(TE-0.3,0.55,400,4800,0.06,'rise');impact(TE+0.2,0.2)
whoosh_side(WF(6,'por')-0.1,0.5,0.045,False);thud(WF(6,'por')+0.35,0.09)
# produto
chime(TL7-0.05,[58,62,65,70],0.03,1.6);pop(TF+0.1,0.05,800,0.5)
for j,w in enumerate(['abre','toda','conversa']): pop(WF(7,w)-0.15,0.045,900+j*130,0.3+0.2*j)
im=WF(7,'imóvel')-0.08
for k in range(3): pop(im+k*0.12,0.04,1200+k*150,0.3+0.2*k)
chime(WF(7,'mãos')-0.1,[70,74,77,82],0.024,1.4)
# CTA
sweep(TG-0.3,0.6,500,4500,0.05,'rise');impact(TG+0.1,0.2);chime(TG+0.55,[58,65,70,74],0.028,1.5)
w0=WF(8,'diagn')
for k in range(11): key(w0-0.05+k*0.055,0.04,0.35+0.3*(k%2))
sd=WF(8,'e')+0.1;click(sd,0.09,0.6);pop(sd+0.05,0.06,800,0.4)
chime(WF(8,'receba')+0.5,[70,74,77,82],0.03,1.1)
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
