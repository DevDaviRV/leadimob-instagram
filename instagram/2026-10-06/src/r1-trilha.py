"""Leadimob R1 06/10 "Modo incorporador" — trilha original: 92 BPM, Sol maior (relativo Mi menor no gancho).
Arco: tensão em Em (gancho/onda/fila) -> virada no morph do chat (impact) -> groove com arpejo de pluck (Cmaj7 G D/F# Em) que cresce por cena -> resolução em Sol no CTA.
Uso: python3 trilha.py -> mix_vo.wav (com voz)"""
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
    i=int(round(at*SR))
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
BPM=92; beat=60/BPM; bar=4*beat
MORPH=10.2; tD=17.25; tScan=22.0; tF=26.3; tG=31.05; tH=34.95
QTA=[4.95,5.35,5.7,6.0,6.25,6.5,6.72,6.92,7.1,7.28]
T0=MORPH-np.ceil(MORPH/bar)*bar
def sec(t):
    if t<4.2: return 'hook'
    if t<MORPH-0.1: return 'wave'
    if t<tD: return 'chat'
    if t<tF: return 'prod'
    if t<tH: return 'prod2'
    return 'cta'
prog=[[40,59,62,66,69,71],[36,60,64,67,71,76],[43,59,62,67,71,74],[38,57,62,66,69,74]]  # Em9 Cmaj7 G/B? D/F#-ish
L=np.zeros(N);R=np.zeros(N)
nb=int((END-T0)/bar)+2
PL=np.zeros(N);PR=np.zeros(N)
for b in range(0,nb,2):
    st=T0+b*bar
    if st>END: break
    ch=prog[(b//2)%4]; n=int((2*bar+1.6)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/1.0)*np.clip((2*bar+1.6-tt)/1.6,0,1)
    for m in ch[1:]:
        for d,pan in((-0.005,.25),(0.005,.75)):
            s=saw(midi(m),n,d)*env*0.010; add(PL,s*(1-pan),st); add(PR,s*pan,st)
cv={'hook':.12,'wave':.25,'chat':.6,'prod':.8,'prod2':.9,'cta':1.0}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(19200)/19200,'same')
L+=lp(PL,500)*(1-ctrl)+lp(PL,3200)*ctrl; R+=lp(PR,500)*(1-ctrl)+lp(PR,3200)*ctrl
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
pat=[0,2,4,2,1,3,5,3]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.2: continue
    s_=sec(t); pos=k%16; b=int((t-T0)//bar); ch=prog[(b//2)%4]
    groove=s_ in('chat','prod','prod2','cta'); full=s_ in('prod','prod2','cta')
    if s_=='wave' and pos%4==0 and t>5.0:   # heartbeat of the queue
        n=int(0.3*SR);tt=np.arange(n)/SR;kk=np.sin(2*np.pi*np.cumsum(50+60*np.exp(-tt*35))/SR)*np.exp(-tt*10)*0.18;add(L,kk,t);add(R,kk,t)
    if groove and (pos in(0,8) or (full and pos==10)):
        n=int(0.4*SR);tt=np.arange(n)/SR;fk=44+100*np.exp(-tt*28)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*8)*0.3;add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if full and pos in(4,12):
        n=int(0.2*SR);tt=np.arange(n)/SR;sn=bp(rng.standard_normal(n),1500,7000)*np.exp(-tt*28)*0.045;add(L,sn,t);add(R,sn*0.9,t)
    if groove and pos%2==1:
        n=int(0.05*SR);tt=np.arange(n)/SR;h=hp(rng.standard_normal(n),8000)*np.exp(-tt*120)*0.02*(0.6 if pos%4==1 else 1);pan=0.3+0.4*((k*3)%5)/4;add(L,h*(1-pan),t);add(R,h*pan,t)
    if pos%8==0 and s_!='hook':
        n=int(beat*2*SR*0.9);tt=np.arange(n)/SR;f=midi(ch[0]);g={'wave':0.05,'chat':0.09,'prod':0.1,'prod2':0.1,'cta':0.1}[s_]
        add(BL,(np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt))*np.exp(-tt*1.6)*g,t)
    if (groove and pos%2==0) or (s_=='wave' and pos%4==2 and t>6.0):
        m=ch[1:][pat[(k//2)%8]%5]+12;n=int(0.4*SR);tt=np.arange(n)/SR
        lvl={'wave':0.007,'chat':0.012,'prod':0.016,'prod2':0.019,'cta':0.02}[s_]
        x=lp(saw(midi(m),n)*np.exp(-tt*9)+0.5*np.sin(2*np.pi*midi(m+12)*tt)*np.exp(-tt*14),3500)*lvl;add(AL,x,t);add(AR,x*0.8,t)
d=int(beat*0.75*SR)
for rep in range(1,3):
    g=0.3**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.45*np.exp(-tt/0.09)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
n=int((MORPH+0.4)*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(28)*tt)+0.35*np.sin(2*np.pi*midi(40)*tt*1.003))*0.05*np.clip(tt/1.5,0,1)*np.clip((MORPH+0.4-tt)/0.5,0,1)
add(L,dr,0);add(R,dr,0)
irn=int(2.2*SR);tt=np.arange(irn)/SR
irL=rng.standard_normal(irn)*np.exp(-tt*2.6);irR=rng.standard_normal(irn)*np.exp(-tt*2.6);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.25*fftconvolve(hp(L,300),irL)[:N];R=R+0.25*fftconvolve(hp(R,300),irR)[:N]
FL=np.zeros(N);FR=np.zeros(N)
def st2(x,at,pan=.5,g=1): add(FL,x*(1-pan)*1.4*g,at);add(FR,x*pan*1.4*g,at)
def sweep(at,dur,f0,f1,g,env='bell'):
    n=int(dur*SR);tt=np.arange(n)/SR;x=rng.standard_normal(n);out=np.zeros(n);seg=960
    for i in range(0,n,seg):
        k=i/n;f=f0+(f1-f0)*(k**2 if env=='rise' else np.sin(np.pi*k));out[i:i+seg]=bp(x[max(0,i-3000):i+seg],max(60,f*0.7),min(f*1.45,20000))[-len(out[i:i+seg]):]
    e=(tt/dur)**2 if env=='rise' else np.sin(np.pi*tt/dur)**2
    pan=np.linspace(.25,.75,n);s=out*e*g;add(FL,s*(1-pan),at);add(FR,s*pan,at)
def impact(at,g=0.3):
    n=int(1.6*SR);tt=np.arange(n)/SR;f=34+70*np.exp(-tt*9)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.8)*g+lp(rng.standard_normal(n),1400)*np.exp(-tt*12)*g*0.2;add(FL,s,at);add(FR,s,at)
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
def thud(at,g=0.2):
    n=int(0.8*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*(48+30*np.exp(-tt*20))*tt)*np.exp(-tt*6)*g;add(FL,s,at);add(FR,s,at)
# hook: tower windows, label
for k in range(6): tick(0.55+k*0.12,0.03,900+k*160,0.2+0.12*k)
sweep(0.1,0.5,300,3000,0.05,'rise');pop(WF(1,'incorporador')+0.0,0.07,600,0.5)
pop(WF(2,"agora"),0.04,900,0.4);ding(1.7+1.2,0.03,91,0.6)
sweep(3.7,0.6,400,5000,0.07,'rise')
# wave + queue
sweep(4.4,2.2,300,2400,0.04)
for k,a in enumerate(QTA): pop(a,0.05,700+30*k,0.3+0.04*k);ding(a+0.03,0.012,80+(k%4)*2,0.7)
thud(WF(4,'consegue'),0.14);ding(WF(4,'responder'),0.03,66,0.4)
sweep(MORPH-0.7,0.8,300,6000,0.09,'rise');impact(MORPH+0.25,0.34);chime(MORPH+0.3,[67,71,74],0.02,1.6)
# chat
pop(C[5]['start']+0.1,0.06,800,0.4);chime(WF(5,'incorporador')+0.05,[71,76,79],0.02,1.8)
pop(WF(5,'atende'),0.08,1000,0.6);sweep(WF(5,'sabendo')-0.1,0.5,800,3000,0.04);chime(WF(5,'empreendimento')+0.1,[74,79,83],0.03,1.5)
# units/table
sweep(tD-0.2,0.7,500,5000,0.08,'rise')
for ri in range(6):
    for ci in range(6):
        if rng.random()<.5: tick(WF(6,'disponíveis')+ri*0.05+ci*0.04,0.02,1800+ci*140,0.2+ci*0.12)
pop(WF(6,'disponíveis')+0.75,0.06,900,0.5);sweep(19.95,0.5,600,3500,0.06)
for i in range(4): click(20.3+i*0.1,0.04,0.3+0.1*i)
for i in range(4): tick(WF(6,'preços')+0.05+i*0.12,0.04,1500+i*220,0.7)
chime(WF(6,'vigente'),[74,79,83,86],0.035,1.5)
# profile/route
sweep(tScan-0.1,0.7,500,7000,0.1,'rise');impact(tScan+0.25,0.2)
for i,k in enumerate([WF(7,'qualifica')+0.2,WF(7,'perfil')-0.2,WF(7,'perfil')+0.25,WF(7,'direciona')-0.55]): tick(k,0.05,2000+i*180)
sweep(WF(7,'direciona')-0.1,0.9,900,3500,0.05)
for i in range(3): tick(WF(7,'direciona')+0.3+i*0.1,0.035,1800+i*200)
chime(WF(7,'certo')-0.1,[71,76,79],0.035,1.6)
# distribute/schedule
sweep(tF-0.2,0.6,500,6000,0.09,'rise')
for i in range(3): click(tF+0.05+i*0.12,0.04,0.3+0.2*i)
pop(WF(8,'distribui'),0.07,900,0.4);sweep(WF(8,'consultor')-0.05,0.5,900,3500,0.05);chime(WF(8,'consultor')+0.4,[67,71,74],0.025,1.6)
for i in range(5): tick(WF(8,'agenda')+i*0.07,0.04,1900+i*150,0.2+i*0.15)
chime(WF(8,'visita')+0.1,[67,71,74,79],0.035,1.5);pop(WF(8,'visita')+0.15,0.06,1000,0.6)
# dashboard
sweep(tG-0.3,0.7,400,6500,0.09,'rise');impact(tG+0.1,0.18)
for i in range(4): tick(WF(9,'acompanha')+0.05+i*0.13,0.04,1700+i*200)
click(WF(9,'campanha')-0.12,0.08,0.5);pop(WF(9,'campanha')-0.1,0.05,800,0.5)
for i in range(4): tick(WF(9,'campanha')+0.05+i*0.12,0.04,2100+i*150,0.6)
# CTA
sweep(tH-1.2,1.2,250,9000,0.09,'rise');impact(tH+0.05,0.32);chime(tH+0.08,[55,62,67,71],0.03,1.2)
chime(WF(11,'link')-0.1,[67,74,79,83],0.035,1.1)
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
sfr=np.sqrt(np.mean(((FL+FR)/2)**2));FL*=vr*10**(-15/20)/sfr;FR*=vr*10**(-15/20)/sfr
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_vo.wav',(L+FL)+V,(R+FR)+V)
print('END',round(END,2),'gain',round(gm,3))
