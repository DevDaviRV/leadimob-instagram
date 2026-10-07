"""Leadimob R1 10/10 — trilha original: 86 BPM, Ré maior (abre em Si menor).
Arranjo novo: piano elétrico (FM) em vez de pads de serra, arpejo de marimba, pulso de relógio na espera,
kick macio no 1 e no 3, shaker em colcheias. Gancho contido -> formulário (fica parado, filtro fecha) ->
Leadimob (groove abre em Ré maior) -> qualifica/imóvel/visita (cheio) -> corretor -> CTA (resolve).
Uso: /usr/bin/python3 trilha.py -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[12]['end']+2.1; N=int((END+0.5)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(1010)
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
BPM=86; beat=60/BPM; bar=4*beat
T1=C[2]['start']-0.3; T2=C[3]['start']-0.42; T3=C[6]['start']-0.45; T4=C[9]['start']-0.4; TE=C[10]['start']-0.28; T5=C[11]['start']-0.5
SEND1=WF(3,'meta')+0.28; SEND2=WF(6,'envia')+0.05; M0=WF(6,'formul')-0.3; M1=M0+0.8
T0=(T3+0.45)-np.ceil((T3+0.45)/bar)*bar    # tempo forte no zoom-through
def sec(t):
    if t<T2: return 'hook'
    if t<T3: return 'form'
    if t<T4: return 'lead'
    if t<TE: return 'ia'
    if t<T5: return 'cor'
    return 'cta'
PRE=[[47,59,62,66,69,73],[43,59,62,66,69,71]]                       # Bm9 · Gmaj9
POS=[[50,62,66,69,71,76],[49,61,64,69,73,76],[47,62,66,69,74,78],[43,62,66,67,71,74]]  # D6/9 · A/C# · Bm(add11) · Gmaj7
def chord(t):
    b=int((t-T0)//bar)
    return PRE[b%2] if t<T3 else POS[b%4]
def epiano(f,n,g):
    tt=np.arange(n)/SR; I=2.2*np.exp(-tt*3.5)
    return np.sin(2*np.pi*f*tt+I*np.sin(2*np.pi*f*tt))*np.exp(-tt*1.3)*(1-np.exp(-tt*200))*g
L=np.zeros(N);Rr=np.zeros(N)
# piano elétrico: acorde no tempo 1 e um eco suave no "e" do 3
EPL=np.zeros(N);EPR=np.zeros(N)
nb=int((END-T0)/bar)+2
for b in range(nb):
    for off,gg in ((0,1.0),(2.5*beat,0.5)):
        st=T0+b*bar+off
        if st<-0.1 or st>END-0.6: continue
        s_=sec(max(st,0)); ch=chord(max(st,0))
        if s_=='hook' and off>0: continue
        g={'hook':0.020,'form':0.016,'lead':0.024,'ia':0.026,'cor':0.026,'cta':0.028}[s_]*gg
        for j,m in enumerate(ch[1:]):
            x=epiano(midi(m),int(2.6*SR),g); pan=0.3+0.1*j; add(EPL,x*(1-pan),st+j*0.012); add(EPR,x*pan,st+j*0.012)
cv={'hook':.35,'form':.12,'lead':.7,'ia':1,'cor':.85,'cta':1}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.repeat(ctrl,480)[:N]; ctrl=np.pad(ctrl,(0,max(0,N-len(ctrl))),'edge'); cs=np.concatenate([[0],np.cumsum(np.pad(ctrl,(9600,9599),'edge'))]); ctrl=(cs[19200:]-cs[:-19200])/19200  # média móvel de 0,4s (cumsum, rápido)
L+=lp(EPL,700)*(1-ctrl)+lp(EPL,6000)*ctrl; Rr+=lp(EPR,700)*(1-ctrl)+lp(EPR,6000)*ctrl
# pad de cordas suave (seno + 2ª) só no produto
PD=np.zeros(N)
for b in range(nb):
    st=T0+b*bar
    if st<T3-0.2 or st>END: continue
    ch=chord(st);n=int((bar+1.2)*SR);tt=np.arange(n)/SR;env=np.minimum(1,tt/0.7)*np.clip((bar+1.2-tt)/1.2,0,1)
    for m in ch[1:4]: add(PD,(np.sin(2*np.pi*midi(m)*tt)+0.25*np.sin(4*np.pi*midi(m)*tt*1.003))*env*0.006,st)
L+=PD;Rr+=PD
KICKS=[];BL=np.zeros(N);ML=np.zeros(N);MR=np.zeros(N)
arp=[0,2,4,1,3,4,2,1]
for k in range(int((END-T0)/(beat/2))+1):
    t=T0+k*beat/2
    if t<0 or t>END-1.0: continue
    s_=sec(t); pos=k%8; ch=chord(t)
    groove=s_ in('lead','ia','cor','cta')
    if (groove and pos in(0,4)) or (s_=='hook' and pos==0 and t>1.0):
        n=int(0.5*SR);tt=np.arange(n)/SR;fk=46+80*np.exp(-tt*26)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*6.5)*(0.16 if s_=='hook' else 0.26)
        add(L,kk,t);add(Rr,kk,t);KICKS.append(t)
    if groove and pos in(2,6):   # rim/snap macio
        n=int(0.18*SR);tt=np.arange(n)/SR;cp=bp(rng.standard_normal(n),1500,5000)*np.exp(-tt*30)*0.035
        add(L,cp*0.8,t);add(Rr,cp,t)
    if groove or s_=='hook':     # shaker
        n=int(0.06*SR);tt=np.arange(n)/SR;vel=[.9,.35,.6,.35][pos%4]*(0.4 if s_=='hook' else 1)
        h=hp(rng.standard_normal(n),7000)*np.sin(np.pi*np.clip(tt/0.06,0,1))**2*0.018*vel;pan=0.35+0.3*(pos%2);add(L,h*(1-pan),t);add(Rr,h*pan,t)
    if s_!='hook' and pos in(0,3,4) and not(s_=='form' and pos!=0):
        n=int(beat*SR*1.4);tt=np.arange(n)/SR;f=midi(ch[0])
        g={'form':0.05,'lead':0.08,'ia':0.1,'cor':0.09,'cta':0.1}[s_]*(1 if pos==0 else 0.6)
        add(BL,(np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt))*np.exp(-tt*2.2)*(1-np.exp(-tt*300))*g,t)
    if s_ in('ia','cor','cta') or (s_=='lead' and t>M1):   # marimba
        m=ch[1:][arp[k%8]]+12;n=int(0.5*SR);tt=np.arange(n)/SR;f=midi(m)
        x=(np.sin(2*np.pi*f*tt)+0.12*np.sin(2*np.pi*3.93*f*tt)*np.exp(-tt*30))*np.exp(-tt*9)*(0.016 if s_=='lead' else 0.02)
        pan=0.3+0.4*((k*3)%5)/4;add(ML,x*(1-pan),t);add(MR,x*pan,t)
d=int(beat*0.75*SR)
for rep in range(1,3):
    g=0.3**rep;src=(ML if rep%2 else MR).copy();tgt=MR if rep%2 else ML;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.4*np.exp(-tt/0.1)[:j-i])
L=L*sc+BL*sc+ML;Rr=Rr*sc+BL*sc+MR
# drone grave na espera (Si)
a=T2+0.3;n=int((T3-a+0.4)*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(35)*tt)+0.35*np.sin(2*np.pi*midi(47)*tt*1.002))*0.045*np.clip(tt/1.2,0,1)*np.clip((T3+0.4-a-tt)/0.4,0,1)
add(L,dr,a);add(Rr,dr,a)
ir_n=int(2.0*SR);tt=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-tt*2.8);irR=rng.standard_normal(ir_n)*np.exp(-tt*2.8);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.24*fftconvolve(hp(L,300),irL)[:N];Rr=Rr+0.24*fftconvolve(hp(Rr,300),irR)[:N]
# ---------------- SFX (foley de interface) ----------------
FL=np.zeros(N);FR=np.zeros(N)
def st2(x,at,pan=.5,g=1): add(FL,x*(1-pan)*1.4*g,at);add(FR,x*pan*1.4*g,at)
def sweep(at,dur,f0,f1,g,env='bell'):
    n=int(dur*SR);tt=np.arange(n)/SR;x=rng.standard_normal(n);out=np.zeros(n);seg=960
    for i in range(0,n,seg):
        k=i/n;f=f0+(f1-f0)*(k**2 if env=='rise' else np.sin(np.pi*k));out[i:i+seg]=bp(x[max(0,i-3000):i+seg],max(60,f*0.7),min(f*1.45,20000))[-len(out[i:i+seg]):]
    e=(tt/dur)**2 if env=='rise' else np.sin(np.pi*tt/dur)**2
    pan=np.linspace(.3,.7,n);s=out*e*g;add(FL,s*(1-pan),at);add(FR,s*pan,at)
def impact(at,g=0.3):
    n=int(1.6*SR);tt=np.arange(n)/SR;f=36+66*np.exp(-tt*9)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.8)*g+lp(rng.standard_normal(n),1200)*np.exp(-tt*14)*g*0.2;add(FL,s,at);add(FR,s,at)
def tick(at,g=0.05,f=2400,pan=.5):
    n=int(0.05*SR);tt=np.arange(n)/SR;st2(np.sin(2*np.pi*f*tt)*np.exp(-tt*140)*g,at,pan)
def pop(at,g=0.07,f=900,pan=.5):
    n=int(0.14*SR);tt=np.arange(n)/SR;fr=f*(1+0.6*np.exp(-tt*60));st2(np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*38)*g,at,pan)
def ding(at,g=0.04,m=88,pan=.5):
    n=int(0.9*SR);tt=np.arange(n)/SR;f=midi(m);x=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2.76*f*tt)*np.exp(-tt*9))*np.exp(-tt*6)*g;st2(x,at,pan)
def chime(at,notes,g=0.03,dec=1.4):
    n=int(3*SR);tt=np.arange(n)/SR;s=np.zeros(n)
    for i,m in enumerate(notes):
        dd=int(i*0.07*SR);f=midi(m);s[dd:]+=(np.sin(2*np.pi*f*tt[:n-dd])+0.22*np.sin(2*np.pi*2.01*f*tt[:n-dd]))*np.exp(-tt[:n-dd]*dec)
    add(FL,s*g,at);add(FR,s*g,at)
def click(at,g=0.05,pan=.5):
    n=int(0.02*SR);tt=np.arange(n)/SR;st2(hp(rng.standard_normal(n),2500)*np.exp(-tt*400)*g,at,pan)
def thud(at,g=0.18):
    n=int(0.8*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*(48+30*np.exp(-tt*20))*tt)*np.exp(-tt*6)*g;add(FL,s,at);add(FR,s,at)
def typing(a,dur,pan=.45):
    k=0
    while k*0.06<dur: click(a+k*0.06+0.012*np.sin(k*7),0.03+0.012*(k%3==0),pan+0.1*(k%2));k+=1
# GANCHO
sweep(0,0.9,2400,600,0.03);pop(0.05,0.04,700,0.5)
pop(WF(1,'funcion')-0.05,0.06,1100,0.35);ding(WF(1,'funcion'),0.02,86,0.35)
sweep(T1-0.4,0.45,500,3000,0.035,'rise');click(T1+0.1,0.04)
a0=WF(2,'leads')-0.2
for i in range(3): pop(a0+i*0.32,0.05,820-i*80,0.4+0.1*i)
sweep(WF(2,'desperd')+0.15,0.9,2600,300,0.05);thud(WF(2,'desperd')+0.5,0.12)
# FORMULÁRIO
sweep(T2-0.25,0.55,600,4200,0.06,'rise');pop(T2+0.3,0.06,760,0.5)
a=WF(3,'cliente')+0.05;typing(a,0.5);typing(a+0.55,0.45,0.55);typing(WF(3,'formul')-0.05,0.4,0.5)
click(SEND1,0.1,0.5);pop(SEND1+0.04,0.06,640,0.5);chime(SEND1+0.4,[71,78],0.016,2)
pop(WF(4,'esperando')-0.05,0.05,420,0.5)
w0=WF(4,'esperando');h0=WF(5,'por')-0.1;t=w0;
while t<T3-0.1:
    rate=0.5 if t<h0 else max(0.09,0.5-0.4*(t-h0)/1.0)
    tick(t,0.028,1700 if int(t/rate)%2 else 1350,0.5);t+=rate
# LEADIMOB
sweep(T3-0.45,0.5,300,6000,0.08,'rise');impact(T3+0.45,0.26);chime(WF(6,'leadimob')-0.1,[62,66,69,74],0.028,1.6)
pop(T3+0.35,0.05,700,0.5)
click(SEND2,0.11,0.5);sweep(M0,0.8,800,2600,0.04);pop(M1-0.05,0.08,980,0.6);ding(M1,0.03,81,0.6)
ding(WF(7,'whatsapp')+0.05,0.025,88,0.65)
pop(WF(8,'sabendo'),0.06,820,0.45);tick(WF(8,'imóvel'),0.05,2600,0.55);chime(WF(8,'imóvel')+0.1,[74,81],0.02,1.8)
pop(WF(8,'viu')-0.1,0.07,700,0.3);ding(WF(8,'viu'),0.025,76,0.3)
# IA: qualifica, imóvel, visita
sweep(T4-0.15,0.6,2600,500,0.05);click(T4+0.25,0.05)
pop(WF(9,'qualifica')-0.2,0.06,760,0.5)
for i in range(2): pop(WF(9,'qualifica')+0.05+i*0.16,0.05,980+i*120,0.4+0.2*i)
pop(WF(9,'qualifica')+0.45,0.05,1250,0.7)
pop(WF(9,'apresenta')-0.1,0.07,820,0.5);sweep(WF(9,'apresenta')-0.3,0.4,900,3000,0.03)
pop(WF(9,'agenda')-0.15,0.07,880,0.5);chime(WF(9,'visita'),[69,74,78],0.026,1.5)
# CORRETOR
sweep(TE-0.2,0.5,3200,700,0.04);ding(TE+0.15,0.04,83,0.5);ding(TE+0.3,0.035,88,0.5)
pop(WF(10,'entra'),0.06,900,0.4);click(WF(10,'pede')+0.03,0.09,0.45);chime(WF(10,'pede')+0.1,[74,78,81],0.028,1.4)
# CTA
sweep(T5-0.55,0.6,300,7000,0.07,'rise');impact(T5+0.05,0.24);chime(T5+0.6,[62,69,74,78],0.03,1.3)
pop(T5+1.1,0.05,700,0.65)
for w in ['solicite','uma','demonstr']: click(WF(11,w)-0.1,0.03)
chime(WF(12,'link'),[74,81,86],0.028,1.2)
# ---------------- voz ----------------
V=np.zeros(N)
for c in TL:
    sr,x=wavfile.read(f"vo_b/p{c['i']:02d}.wav");x=x.astype(np.float64)/32768.0
    if x.ndim>1: x=x.mean(1)
    if sr!=SR: x=resample_poly(x,SR,sr)
    add(V,x,c['start'])
env=lp(np.abs(V),6);env=np.clip(env/0.05,0,1);duck=1-0.55*env
fade=np.clip(T/0.04,0,1)*np.clip((END-T)/1.4,0,1)
L*=duck*fade;Rr*=duck*fade
vr=np.sqrt(np.mean(V[lp(np.abs(V),6)>0.01]**2));mr=np.sqrt(np.mean(((L+Rr)/2)**2))
gm=vr*10**(-11/20)/mr;L*=gm;Rr*=gm;FL*=fade;FR*=fade
sfr=np.sqrt(np.mean(((FL+FR)/2)**2)); FL*=vr*10**(-15/20)/sfr; FR*=vr*10**(-15/20)/sfr
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_novo.wav',L+FL,Rr+FR);save('mix_vo.wav',(L+FL)+V,(Rr+FR)+V)
print('END',round(END,2),'gain',round(gm,3))
