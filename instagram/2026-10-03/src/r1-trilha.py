"""Reel 1 (03/10) — "Você não precisa de mais tráfego".
Trilha original: 124 BPM, Lá menor -> Dó maior. Arco: gancho com fluxo (pulso grave + arpejo filtrado) -> revelação dos vazamentos (queda + gotas descendentes)
-> estações em tensão (meio-tempo, cada vazamento = tríade descendente) -> orçamento (riser) -> teste (groove four-on-the-floor, perseguição)
-> CTA (resolução em Dó, sete notas subindo nos sete pontos).
Uso: python3 trilha.py -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[12]['end']+1.5; N=int((END+0.4)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(310)
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,a,b,o=2): return sosfilt(butter(o,[a,b],'band',fs=SR,output='sos'),x)
def add(buf,x,at,g=1.0):
    i=int(at*SR)
    if i<0: x=x[-i:]; i=0
    j=min(len(buf),i+len(x))
    if i<len(buf) and j>i: buf[i:j]+=g*x[:j-i]
midi=lambda n:440*2**((n-69)/12)
def WF(i,s):
    for w in C[i]['words']:
        if w['w'].lower().startswith(s.lower()): return w['t']
    return C[i]['start']
def saw(f,n,det=0.0):
    ph=np.cumsum(np.full(n,f*(1+det))/SR); return 2*(ph%1)-1
BPM=124; beat=60/BPM; bar=4*beat
HK2=C[2]['start']; AD=C[3]['start']; CHt=C[4]['start']; PB=C[5]['start']; LK=[C[6]['start'],C[7]['start'],C[8]['start']]
WIDE=C[9]['start']; PH=C[10]['start']; SEND=WF(10,'imobili'); GO=SEND+0.25; NT=[WF(11,'anote')-0.1,WF(11,'tudo')+0.05,WF(11,'acontece')]; CTA=C[12]['start']-0.1
T0=GO-np.ceil(GO/bar)*bar            # tempo forte cai na largada do teste
def sec(t):
    if t<HK2: return 'hook'
    if t<AD-0.3: return 'reveal'
    if t<LK[0]-0.3: return 'build'
    if t<WIDE: return 'leak'
    if t<PH-0.3: return 'wide'
    if t<GO: return 'phone'
    if t<CTA: return 'chase'
    return 'cta'
PA=[[45,60,64,69,72],[41,60,65,69,72],[36,60,64,67,72],[43,59,62,67,74]]   # Am F C G
L=np.zeros(N);R=np.zeros(N)
nb=int((END-T0)/bar)+2
PL=np.zeros(N);PR=np.zeros(N)
for b in range(nb):
    st=T0+b*bar
    if st>END: break
    ch=PA[b%4]; n=int((bar+1.5)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.6)*np.clip((bar+1.5-tt)/1.5,0,1)
    for m in ch[1:]:
        for d,pan in((-0.005,.25),(0.005,.75)):
            s=saw(midi(m),n,d)*env*0.010; add(PL,s*(1-pan),st); add(PR,s*pan,st)
cv={'hook':.35,'reveal':.15,'build':.4,'leak':.22,'wide':.6,'phone':.3,'chase':.9,'cta':1.0}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.repeat(ctrl,480)[:N]
k0,k1=int(WIDE*SR),int((PH-0.3)*SR); ctrl[k0:k1]=np.linspace(.25,.95,k1-k0)
ctrl=np.convolve(ctrl,np.ones(9600)/9600,'same')
PLd,PRd,PLo,PRo=lp(PL,420),lp(PR,420),lp(PL,3600),lp(PR,3600)
L+=PLd*(1-ctrl)+PLo*ctrl; R+=PRd*(1-ctrl)+PRo*ctrl
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
pat=[0,2,1,3,2,1,3,2]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.2: continue
    s_=sec(t); pos=k%16; b=int((t-T0)//bar); ch=PA[b%4]
    four=s_ in('chase','cta'); half=s_ in('leak','build','phone'); hk=s_=='hook'
    if (four and pos%4==0) or (half and pos==0) or (hk and pos in(0,6,10)) or (s_=='wide' and pos%4==0):
        n=int(0.45*SR);tt=np.arange(n)/SR;fk=42+108*np.exp(-tt*28); g=.33 if four else .27
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*7)*g+hp(rng.standard_normal(n),3000)*np.exp(-tt*240)*0.025
        add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if (four and pos in(4,12)) or (half and pos==8):
        n=int(0.24*SR);tt=np.arange(n)/SR;cp=bp(rng.standard_normal(n),1300,6000)*(np.exp(-tt*26)+0.4*np.exp(-np.abs(tt-0.012)*300))*(0.06 if four else 0.045)
        add(L,cp,t);add(R,cp*0.9,t)
    if (four) or (s_ in('hook','wide') and pos%2==0) or (half and pos%4==2):
        n=int(0.04*SR);tt=np.arange(n)/SR;vel=[.8,.25,.55,.3][pos%4]
        h=hp(rng.standard_normal(n),9000)*np.exp(-tt*130)*0.022*vel;pan=0.25+0.5*((k*5)%7)/6;add(L,h*(1-pan),t);add(R,h*pan,t)
    if pos%2==0 and s_!='reveal':
        n=int(beat/2*SR*0.9);tt=np.arange(n)/SR;f=midi(ch[0]-12 if four else ch[0])
        g={'hook':0.07,'build':0.06,'leak':0.05,'wide':0.08,'phone':0.05,'chase':0.1,'cta':0.1}[s_]
        if half and pos%8!=0: g=0
        add(BL,(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt))*np.exp(-tt*3.5)*g,t)
    if (four and pos%2==0) or (s_ in('hook','wide') and pos%2==0) or (s_=='build' and pos%4==0):
        m=ch[1:][pat[(k//2)%8]]+12;n=int(0.3*SR);tt=np.arange(n)/SR
        x=lp(saw(midi(m),n)*np.exp(-tt*11),3000 if four else 1800)*(0.018 if four else 0.012); add(AL,x,t);add(AR,x*0.75,t)
d=int(beat*0.75*SR)
for rep in range(1,4):
    g=0.33**rep;src_=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src_[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.5*np.exp(-tt/0.09)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
def drone(a,b,m,g):
    n=int((b-a)*SR);tt=np.arange(n)/SR
    x=(np.sin(2*np.pi*midi(m)*tt)+0.4*np.sin(2*np.pi*midi(m+12)*tt*1.002))*g*np.clip(tt/0.6,0,1)*np.clip((b-a-tt)/0.5,0,1);add(L,x,a);add(R,x,a)
drone(HK2-0.2,AD,33,0.07);drone(LK[0]-0.3,WIDE+0.2,33,0.045)
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
def ding(at,g=0.04,m=88,pan=.5,dec=6):
    n=int(1.1*SR);tt=np.arange(n)/SR;f=midi(m);x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2.76*f*tt)*np.exp(-tt*9))*np.exp(-tt*dec)*g;st2(x,at,pan)
def chime(at,notes,g=0.035,dec=1.4):
    n=int(3*SR);tt=np.arange(n)/SR;s=np.zeros(n)
    for i,m in enumerate(notes):
        dd=int(i*0.07*SR);f=midi(m);s[dd:]+=(np.sin(2*np.pi*f*tt[:n-dd])+0.22*np.sin(2*np.pi*2.01*f*tt[:n-dd]))*np.exp(-tt[:n-dd]*dec)
    add(FL,s*g,at);add(FR,s*g,at)
def click(at,g=0.05,pan=.5):
    n=int(0.02*SR);tt=np.arange(n)/SR;st2(hp(rng.standard_normal(n),2500)*np.exp(-tt*400)*g,at,pan)
def thud(at,g=0.2):
    n=int(0.8*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*(48+30*np.exp(-tt*20))*tt)*np.exp(-tt*6)*g;add(FL,s,at);add(FR,s,at)
def drain(at,g=0.04,pan=.5):          # tres notas descendo: lead caindo no vazamento
    for i,m in enumerate((81,76,69)): ding(at+i*0.11,g*(1-i*0.2),m,pan,7)
# GANCHO: fluxo de leads
sweep(0.0,2.6,900,3200,0.035);impact(0.02,0.24)
for w,g in(('não',.12),('mais',.10),('tráfego',.2)): thud(WF(1,w)-0.06,g)
sweep(WF(1,'tráfego')+0.3,0.35,3000,600,0.07)                      # risco no "tráfego"
# REVELAÇÃO
sweep(HK2-0.5,1.3,300,6000,0.08,'rise');impact(HK2+0.9,0.3)
for i in range(9): ding(HK2+1.1+i*0.22,0.022,84-i*2,0.2+0.07*i,6)   # gotas descendo
thud(WF(2,'morrendo')-0.05,0.22)
# ANÚNCIO / LEAD
sweep(AD-0.5,0.5,5000,700,0.07);chime(WF(3,'funciona'),[72,76,79],0.03,1.6);click(CHt-0.62,0.09,0.6)
sweep(CHt-0.4,0.4,600,4500,0.06);pop(CHt+0.05,0.08,900,0.4);ding(WF(4,'chama'),0.04,88,0.5)
sweep(PB+0.05,0.6,700,5000,0.06);thud(WF(5,'problema'),0.24);ding(WF(5,'problema')+0.03,0.03,57,0.5,3)
# VAZAMENTOS
for i,a in enumerate(LK): sweep(a-0.45,0.45,500,5000,0.07);thud(a,0.16);drain(a+0.25,0.035,0.3+0.2*i)
tk=WF(6,'responde')
for k in range(14): tick(tk+(k/14)**0.8*1.0,0.03,1500+k*50,0.3+0.4*(k%2))
pop(WF(7,'resposta'),0.07,1000,0.6);thud(WF(7,'genérica'),0.14)
for i in range(3): click(WF(8,'follow')+0.12+i*0.2,0.06,0.35+0.15*i)
n=int(0.09*SR);x=bp(rng.standard_normal(n),900,5000)*np.exp(-np.arange(n)/SR*40)*0.12;st2(x,WF(8,'memória')-0.1,0.65)   # post-it
# ORÇAMENTO
sweep(WIDE-0.3,0.75,400,7000,0.09,'rise');impact(WIDE+0.42,0.28)
for k in range(10): tick(WF(9,'aumentar')+k*0.09,0.035,1200+k*110,0.4)
for i in range(3): pop(WIDE+0.35+i*0.12,0.05,700+i*90,0.3+0.2*i)
sweep(WF(9,'aumentar'),1.2,500,6000,0.05,'rise');chime(WF(9,'teste'),[69,76,81],0.03,1.4)
# TESTE: celular, envio, perseguição
sweep(PH-0.5,0.5,5000,700,0.07)
for k in range(22): click(PH+0.05+k*(SEND-PH-0.25)/22,0.03+0.008*(k%2),0.45+0.1*(k%3)/2)
pop(SEND,0.09,1100,0.6);sweep(GO-0.1,0.9,500,7000,0.1,'rise');impact(GO+0.02,0.22)
for i,a in enumerate(NT): sweep(a-0.35,0.4,2500,900,0.06);thud(a,0.15);ding(a+0.02,0.045,[76,74,72][i],0.5,6);n=int(0.12*SR);st2(bp(rng.standard_normal(n),1800,6000)*np.exp(-np.arange(n)/SR*25)*0.08,a+0.03,0.4)
# CTA
sweep(CTA-0.9,0.9,250,9000,0.085,'rise');impact(CTA+0.05,0.32);chime(CTA+0.1,[60,67,72,76],0.028,1.2)
dg=WF(12,'diagn')
for k in range(11): click(dg-0.2+k*0.65/11,0.05,0.5)
pop(dg+0.6,0.09,1200,0.6);chime(dg+0.62,[76,79,84],0.03,1.4)
mk=WF(12,'checklist')+0.3
for i,m in enumerate((72,74,76,77,79,81,84)): ding(mk+i*0.14,0.04,m,0.2+0.09*i,7)
chime(WF(12,'checklist')+0.2,[72,79,84],0.02,1.2)
# ---------------- voz ----------------
V=np.zeros(N)
for c in TL:
    sr,x=wavfile.read(f"vo_b/p{c['i']:02d}.wav");x=x.astype(np.float64)/32768.0
    if x.ndim>1: x=x.mean(1)
    if sr!=SR: x=resample_poly(x,SR,sr)
    add(V,x,c['start'])
env=lp(np.abs(V),6);env=np.clip(env/0.05,0,1);duck=1-0.55*env
fade=np.clip(T/0.04,0,1)*np.clip((END-T)/1.1,0,1)
L*=duck*fade;R*=duck*fade
vr=np.sqrt(np.mean(V[lp(np.abs(V),6)>0.01]**2));mr=np.sqrt(np.mean(((L+R)/2)**2))
gm=vr*10**(-11/20)/mr;L*=gm;R*=gm;FL*=fade;FR*=fade
sfr=np.sqrt(np.mean(((FL+FR)/2)**2)); FL*=vr*10**(-15/20)/sfr; FR*=vr*10**(-15/20)/sfr
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_novo.wav',L+FL,R+FR);save('mix_vo.wav',(L+FL)+V,(R+FR)+V)
print('END',round(END,2),'gain',round(gm,3))
