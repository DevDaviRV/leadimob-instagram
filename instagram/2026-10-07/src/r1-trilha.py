"""Leadimob Reel 1 de 07/10 — "Sabe aquele cliente que sumiu?" — trilha original.
96 BPM, Si menor -> Ré maior. Arranjo: piano elétrico esparso (gancho) -> pulso contido (conversa) -> relógio e quase silêncio
(os dias passam, "conversa parada") -> pad abre (tese) -> groove leve (prática) -> arranjo cheio com sino (produto) -> resolução (CTA).
Uso: python3 trilha.py  -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[16]['end']+1.5; N=int((END+0.3)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(71)
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
# ---- tempos das cenas (iguais aos do index.html)
tB=C[3]['start']-0.42; tDays=C[5]['start']-0.05; tC=C[7]['start']-0.42; tD=C[8]['start']-0.52
tD2=C[9]['start']-0.2; tE=C[10]['start']-0.3; tF=C[13]['start']-0.5; tScr=C[15]['start']-0.05; WIPE=C[16]['start']-0.22
BPM=96; beat=60/BPM; bar=4*beat
T0=tD+0.3-np.ceil((tD+0.3)/bar)*bar     # um tempo forte cai na chegada do calendário
def sec(t):
    if t<tB: return 'hook'
    if t<tDays: return 'chat'
    if t<tC: return 'days'
    if t<tD: return 'tese'
    if t<tF: return 'prat'
    if t<WIPE: return 'prod'
    return 'cta'
prog=[[47,62,66,69,73],[43,62,66,67,71],[50,62,64,66,69],[49,61,64,69,73]]   # Bm9  Gmaj7  D6/9  A/C#
L=np.zeros(N);R=np.zeros(N)
nb=int((END-T0)/bar)+2
# ---- pad (serra filtrada; abre e fecha por seção)
PL=np.zeros(N);PR=np.zeros(N)
for b in range(nb):
    st=T0+b*bar
    if st>END: break
    ch=prog[b%4]; n=int((bar+1.6)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.8)*np.clip((bar+1.6-tt)/1.6,0,1)
    for m in ch[1:]:
        for d,pan in((-0.005,.25),(0.005,.75)):
            s=saw(midi(m),n,d)*env*0.010; add(PL,s*(1-pan),st); add(PR,s*pan,st)
cv={'hook':.12,'chat':.2,'days':.04,'tese':.55,'prat':.6,'prod':.9,'cta':1.0}
lv={'hook':.8,'chat':.8,'days':.35,'tese':1,'prat':.9,'prod':1,'cta':1}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(14400)/14400,'same')
lvl=np.array([lv[sec(x)] for x in T[::480]]); lvl=np.convolve(np.repeat(lvl,480)[:N],np.ones(14400)/14400,'same')
PLd,PRd,PLo,PRo=lp(PL,450),lp(PR,450),lp(PL,3200),lp(PR,3200)
L+=(PLd*(1-ctrl)+PLo*ctrl)*lvl; R+=(PRd*(1-ctrl)+PRo*ctrl)*lvl
# ---- piano elétrico (seno + harmônicos com ataque de sino)
def ep(m,dur=1.6,g=0.03):
    n=int(dur*SR);tt=np.arange(n)/SR;f=midi(m)
    x=(np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*5)+0.18*np.sin(2*np.pi*7.01*f*tt)*np.exp(-tt*28))*np.exp(-tt*2.6)*(1+0.12*np.sin(2*np.pi*4.6*tt))
    return x*g*np.minimum(1,tt/0.004)
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
pat=[0,2,1,3,2,0,3,1]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0.05 or t>END-1.0: continue
    s_=sec(t); pos=k%16; b=int((t-T0)//bar); ch=prog[b%4]
    full=s_ in('prod','cta'); groove=s_ in('prat','prod','cta')
    # gancho: um acorde por compasso, arpejado devagar
    if s_=='hook' and pos in(0,6,12):
        m=ch[1:][{0:0,6:2,12:3}[pos]]; x=ep(m,2.2,0.04); add(AL,x*0.6,t); add(AR,x,t)
    # conversa: pulso contido em colcheias
    if s_=='chat' and pos%4==0:
        m=ch[1:][(k//4)%4]; x=ep(m,1.0,0.03); add(AL,x,t); add(AR,x*0.6,t)
    # os dias passam: só uma nota grave por compasso
    if s_=='days' and pos==0:
        x=ep(ch[0]+12,2.4,0.035); add(AL,x,t); add(AR,x,t)
    if s_=='tese' and pos%2==0:
        m=ch[1:][pat[(k//2)%8]]+(12 if (k//2)%8>4 else 0); x=ep(m,1.2,0.022+0.002*((k//2)%8)); add(AL,x*0.7,t); add(AR,x,t)
    if groove and (pos in(0,8) or (full and pos==10)):
        n=int(0.4*SR);tt=np.arange(n)/SR;fk=44+90*np.exp(-tt*32)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*8)*0.27+hp(rng.standard_normal(n),3000)*np.exp(-tt*260)*0.02
        add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if groove and pos in(4,12):       # aro
        n=int(0.12*SR);tt=np.arange(n)/SR;cp=(bp(rng.standard_normal(n),1500,5000)*np.exp(-tt*60)*0.5+np.sin(2*np.pi*1750*tt)*np.exp(-tt*90))*0.035
        add(L,cp,t);add(R,cp*0.85,t)
    if (full and True) or (s_=='prat' and pos%2==0):   # shaker
        n=int(0.035*SR);tt=np.arange(n)/SR;vel=[.8,.22,.5,.28][pos%4]
        h=hp(rng.standard_normal(n),8500)*np.exp(-tt*150)*0.018*vel;pan=0.3+0.4*((k*3)%5)/4;add(L,h*(1-pan),t);add(R,h*pan,t)
    if groove and pos in(0,3,8,11):   # baixo sincopado
        n=int(beat*0.8*SR);tt=np.arange(n)/SR;f=midi(ch[0]-12)
        x=(np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt))*np.exp(-tt*4)*np.minimum(1,tt/0.006)*(0.085 if pos in(0,8) else 0.055); add(BL,x,t)
    if groove and pos%2==0:
        m=ch[1:][pat[(k//2)%8]]+12; x=ep(m,0.7,0.02 if s_=='prat' else 0.025); add(AL,x,t);add(AR,x*0.7,t)
    if full and pos in(2,7,13):       # sino agudo no produto
        m=ch[1:][(k*5)%4]+24;n=int(0.5*SR);tt=np.arange(n)/SR;x=np.sin(2*np.pi*midi(m)*tt)*np.exp(-tt*9)*0.013;add(AL,x*0.6,t);add(AR,x,t)
d=int(beat*0.75*SR)
for rep in range(1,4):
    g=0.3**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.45*np.exp(-tt/0.09)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
# grave contínuo do gancho até a tese
n=int((tC+0.4)*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(35)*tt)+0.35*np.sin(2*np.pi*midi(47)*tt*1.002))*0.04*np.clip(tt/1.2,0,1)*np.clip((tC+0.4-tt)/0.5,0,1)
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
    pan=np.linspace(.3,.7,n);s=out*e*g;add(FL,s*(1-pan),at);add(FR,s*pan,at)
def impact(at,g=0.3):
    n=int(1.6*SR);tt=np.arange(n)/SR;f=36+70*np.exp(-tt*9)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.8)*g+lp(rng.standard_normal(n),1400)*np.exp(-tt*12)*g*0.22;add(FL,s,at);add(FR,s,at)
def tick(at,g=0.05,f=2400,pan=.5):
    n=int(0.05*SR);tt=np.arange(n)/SR;st2(np.sin(2*np.pi*f*tt)*np.exp(-tt*140)*g,at,pan)
def pop(at,g=0.07,f=900,pan=.5):
    n=int(0.14*SR);tt=np.arange(n)/SR;fr=f*(1+0.6*np.exp(-tt*60));st2(np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*38)*g,at,pan)
def ding(at,g=0.04,m=88,pan=.5):
    n=int(0.9*SR);tt=np.arange(n)/SR;f=midi(m);x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2.76*f*tt)*np.exp(-tt*9))*np.exp(-tt*6)*g;st2(x,at,pan)
def chime(at,notes,g=0.035,dec=1.4,gap=0.07):
    n=int(3*SR);tt=np.arange(n)/SR;s=np.zeros(n)
    for i,m in enumerate(notes):
        dd=int(i*gap*SR);f=midi(m);s[dd:]+=(np.sin(2*np.pi*f*tt[:n-dd])+0.22*np.sin(2*np.pi*2.01*f*tt[:n-dd]))*np.exp(-tt[:n-dd]*dec)
    add(FL,s*g,at);add(FR,s*g,at)
def click(at,g=0.05,pan=.5):
    n=int(0.02*SR);tt=np.arange(n)/SR;st2(hp(rng.standard_normal(n),2500)*np.exp(-tt*400)*g,at,pan)
def thud(at,g=0.2):
    n=int(0.8*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*(48+30*np.exp(-tt*20))*tt)*np.exp(-tt*6)*g;add(FL,s,at);add(FR,s,at)
# GANCHO: a linha da conversa chega; "sumiu" = a nota cai
pop(0.14,0.05,760,0.45)
sweep(WF(1,'sumiu')+0.35,0.7,2600,400,0.045)
tick(WF(2,'nunca')-0.08,0.04,1500,0.6)
# LINHA -> CONVERSA
sweep(tB-0.1,0.6,500,3200,0.06)
pop(WF(3,'perguntou')-0.2,0.07,720,0.35); pop(WF(4,'recebeu')+0.1,0.07,1000,0.65)
for k in range(3): click(WF(4,'recebeu')+0.18+k*0.08,0.035,0.55+k*0.1)
pop(WF(4,'disse')+0.1,0.07,720,0.35)
# OS DIAS PASSAM: relógio, cada dia uma nota mais grave, depois o aviso
for k in range(int((tC-tDays)/0.5)): tick(tDays+0.05+k*0.5,0.03,1300 if k%2 else 1600,0.38+0.24*(k%2))
for i in range(3): ding(tDays+0.12+i*0.36,0.03,78-i*3,0.5)
thud(WF(6,'ninguém')+0.12,0.16); ding(WF(6,'ninguém')+0.16,0.03,66,0.5)
# TESE
sweep(tC-0.05,0.7,400,2600,0.05); chime(WF(7,'próximo')-0.1,[66,69,73,78],0.03,1.5,0.09)
# VIAGEM -> CALENDÁRIO
sweep(tD-0.25,0.85,300,6000,0.09); thud(tD+0.5,0.12)
tick(WF(8,'dois')-0.34,0.06,1760,0.45); tick(WF(8,'dois')-0.02,0.07,2093,0.6); ding(WF(8,'dois')+0.02,0.03,86,0.6)
pop(WF(8,'uma')-0.02,0.08,1000,0.65)
pop(C[9]['start']-0.08,0.05,620,0.7); sweep(WF(9,'não')+0.08,0.36,3000,700,0.06)
# RÉGUA
sweep(tE-0.05,0.6,500,3000,0.05)
tick(tE+0.1,0.05,1568,0.3); tick(tE+0.6,0.05,1760,0.3)
thud(WF(10,'responder'),0.08)
sweep(WF(11,'tente')-0.05,0.6,700,3600,0.05,'rise'); tick(WF(11,'tente')+0.5,0.06,2093,0.3)
pop(WF(12,'algo')-0.1,0.08,1000,0.6); click(WF(12,'novo')-0.1,0.05,0.5)
# PRODUTO
sweep(tF,0.7,400,4000,0.05); click(WF(13,'faz')-0.05,0.09,0.75); ding(WF(13,'faz')+0.02,0.03,81,0.7)
for i,(ci,w,off) in enumerate([(13,'follow',-0.05),(13,'whatsapp',-0.05),(14,'certo',-0.12)]): chime(WF(ci,w)+off,[[74],[78],[81,86]][i],0.04,2.2)
sweep(tScr,0.5,900,2800,0.04); pop(tScr+0.72,0.08,720,0.35); chime(WF(15,'memória')-0.25,[74,78,81,86],0.035,1.3,0.08)
# WIPE -> CTA
sweep(WIPE-0.8,0.8,300,9000,0.085,'rise'); impact(WIPE,0.3); chime(WIPE+0.06,[62,69,74,78],0.028,1.1)
ta=WF(16,'diagn')-0.08
for k in range(11): click(ta+k*0.62/11,0.05,0.35+0.03*k)
ts=WF(16,'e')-0.12; sweep(ts,0.3,1500,5000,0.05,'rise'); chime(ts+0.08,[78,86],0.04,1.6)
chime(WF(16,'completo')+0.15,[74,78,81],0.025,1.2)
# ---------------- voz ----------------
V=np.zeros(N)
for c in TL:
    sr,x=wavfile.read(f"vo_b/p{c['i']:02d}.wav");x=x.astype(np.float64)/32768.0
    if x.ndim>1: x=x.mean(1)
    if sr!=SR: x=resample_poly(x,SR,sr)
    add(V,x,c['start'])
env=lp(np.abs(V),6);env=np.clip(env/0.05,0,1);duck=1-0.55*env       # ducking sob a voz
fade=np.clip(T/0.05,0,1)*np.clip((END-T)/1.0,0,1)
L*=duck*fade;R*=duck*fade
vr=np.sqrt(np.mean(V[lp(np.abs(V),6)>0.01]**2));mr=np.sqrt(np.mean(((L+R)/2)**2))
gm=vr*10**(-12/20)/mr;L*=gm;R*=gm;FL*=fade;FR*=fade
sfr=np.sqrt(np.mean(((FL+FR)/2)**2)); FL*=vr*10**(-16/20)/sfr; FR*=vr*10**(-16/20)/sfr
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_novo.wav',L+FL,R+FR);save('mix_vo.wav',(L+FL)+V,(R+FR)+V)
print('END',round(END,2),'gain',round(gm,3),'T0',round(T0,3))
