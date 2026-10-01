"""Reel 1 (02/10) — "O cliente não quer receber mais imóveis".
Trilha original: 104 BPM, Ré menor -> Fá maior. Arco: gancho seco (pulso + sub) -> sobrecarga (pops acelerando, filtro abrindo)
-> queda no "adia" (quase silêncio) -> método (groove limpo, cada pergunta = uma nota da escala subindo)
-> produto (acorde aberto) -> CTA (resolução em Fá).
Uso: python3 trilha.py -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[11]['end']+1.5; N=int((END+0.4)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(25)
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
BPM=104; beat=60/BPM; bar=4*beat
# marcos visuais
PHONE=C[3]['start']-0.35; VINTE=WF(3,'vinte'); ADIA=WF(5,'adia'); METH=C[6]['start']-0.4
PICK=C[8]['start']-0.2; PROD=C[9]['start']-0.3; CTA=C[11]['start']-0.3
T0=METH-np.ceil(METH/bar)*bar            # tempo forte cai na virada para o método
def sec(t):
    if t<PHONE: return 'hook'
    if t<ADIA: return 'load'
    if t<METH: return 'stall'
    if t<PROD: return 'meth'
    if t<CTA: return 'prod'
    return 'cta'
PA=[[38,62,65,69,72],[34,62,65,70,74],[41,60,65,69,72],[36,60,64,67,72]]   # Dm7 Bbmaj7 F C
L=np.zeros(N);R=np.zeros(N)
nb=int((END-T0)/bar)+2
PL=np.zeros(N);PR=np.zeros(N)
for b in range(nb):
    st=T0+b*bar
    if st>END: break
    ch=PA[b%4]; n=int((bar+1.6)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.7)*np.clip((bar+1.6-tt)/1.6,0,1)
    for m in ch[1:]:
        for d,pan in((-0.005,.25),(0.005,.75)):
            s=saw(midi(m),n,d)*env*0.010; add(PL,s*(1-pan),st); add(PR,s*pan,st)
cv={'hook':.12,'load':.45,'stall':.05,'meth':.7,'prod':.9,'cta':1.0}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.repeat(ctrl,480)[:N]
# sobrecarga: o filtro abre junto com o contador
k0,k1=int(VINTE*SR),int(ADIA*SR); ctrl[k0:k1]=np.linspace(.25,.8,k1-k0)
ctrl=np.convolve(ctrl,np.ones(9600)/9600,'same')
PLd,PRd,PLo,PRo=lp(PL,420),lp(PR,420),lp(PL,3400),lp(PR,3400)
vol=np.where((T>ADIA)&(T<METH),0.35,1.0); vol=np.convolve(vol,np.ones(4800)/4800,'same')
L+=(PLd*(1-ctrl)+PLo*ctrl)*vol; R+=(PRd*(1-ctrl)+PRo*ctrl)*vol
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
pat=[0,2,1,3,2,3,1,2]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.3: continue
    s_=sec(t); pos=k%16; b=int((t-T0)//bar); ch=PA[b%4]
    groove=s_ in('meth','prod','cta'); full=s_ in('prod','cta')
    if (groove and pos in(0,8)) or (full and pos==10) or (s_=='hook' and pos in(0,8)) or (s_=='load' and pos%4==0):
        n=int(0.45*SR);tt=np.arange(n)/SR;fk=42+105*np.exp(-tt*28); g=.2 if s_=='hook' else(.26 if s_=='load' else .32)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*7)*g+hp(rng.standard_normal(n),3000)*np.exp(-tt*240)*0.025
        add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if groove and pos in(4,12):
        n=int(0.24*SR);tt=np.arange(n)/SR;cp=bp(rng.standard_normal(n),1300,6000)*(np.exp(-tt*26)+0.4*np.exp(-np.abs(tt-0.012)*300))*0.055
        add(L,cp,t);add(R,cp*0.9,t)
    if (groove and pos%2==0) or (full and pos%2==1) or (s_=='load' and pos%2==0 and t>VINTE):
        n=int(0.04*SR);tt=np.arange(n)/SR;vel=[.8,.25,.55,.3][pos%4]
        h=hp(rng.standard_normal(n),9000)*np.exp(-tt*130)*0.022*vel;pan=0.25+0.5*((k*5)%7)/6;add(L,h*(1-pan),t);add(R,h*pan,t)
    if pos%2==0 and s_ not in('hook','stall'):
        n=int(beat/2*SR*0.9);tt=np.arange(n)/SR;f=midi(ch[0]-12 if full else ch[0])
        g={'load':0.06,'meth':0.085,'prod':0.1,'cta':0.1}[s_]
        if s_=='load' and pos%4!=0: g=0
        add(BL,(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt))*np.exp(-tt*3.5)*g,t)
    if (groove and pos%2==0):
        m=ch[1:][pat[(k//2)%8]]+12;n=int(0.3*SR);tt=np.arange(n)/SR
        x=lp(saw(midi(m),n)*np.exp(-tt*11),2800)*(0.013 if s_=='meth' else 0.018); add(AL,x,t);add(AR,x*0.75,t)
d=int(beat*0.75*SR)
for rep in range(1,4):
    g=0.33**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.3*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.5*np.exp(-tt/0.09)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
# drone do gancho + da pausa
def drone(a,b,m,g):
    n=int((b-a)*SR);tt=np.arange(n)/SR
    x=(np.sin(2*np.pi*midi(m)*tt)+0.4*np.sin(2*np.pi*midi(m+12)*tt*1.002))*g*np.clip(tt/0.6,0,1)*np.clip((b-a-tt)/0.5,0,1);add(L,x,a);add(R,x,a)
drone(0,PHONE+0.3,26,0.06);drone(ADIA-0.1,METH+0.2,26,0.05)
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
# GANCHO: cards caem (cartas), palavras batem
for i in range(20): click(max(0.02,-0.4+i*0.05+0.18),0.03+0.01*(i%3),0.15+0.7*((i*7)%10)/9)
impact(0.02,0.26)
for w,g in(('não',.10),('receber',.10),('imóveis',.2)): thud(WF(1,w)-0.05,g)
sweep(C[2]['start']-0.55,0.55,4500,700,0.07)
# "quer que alguém entenda": digitação
ty=WF(2,'entenda')
for k in range(26): click(ty+k*1.4/26,0.022+0.008*(k%2),0.4+0.2*(k%3)/2)
ding(WF(2,'procura')+0.1,0.03,81,0.5)
# CELULAR: 20 pops acelerando com o contador
sweep(PHONE-0.3,0.6,500,5000,0.08)
VINTE=WF(3,'manda'); span=WF(4,'trabalho')-VINTE
for k in range(20):
    x=(k+0.5)/20; u=np.sqrt(x/2) if x<.5 else 1-np.sqrt((1-x)/2)     # inversa do easeInOutQuad
    pop(VINTE+u*span,0.035+0.02*x,700+k*22,0.3+0.4*(k%2)); tick(VINTE+u*span+0.02,0.02,1500+k*45,0.5)
sweep(VINTE,span*0.9,400,6000,0.045,'rise')
pop(C[5]['start']-0.2,0.06,520,0.35)                                   # "vou ver com calma"
# ADIA: tudo para
EL=WF(5,'ele');pop(EL,0.07,420,0.5);thud(ADIA,0.24);sweep(ADIA,0.9,2600,250,0.06);ding(ADIA+0.05,0.03,62,0.5,3)
# MÉTODO
sweep(METH-0.9,0.9,300,8000,0.09,'rise');impact(METH,0.3);chime(METH+0.05,[62,69,74],0.02,1.6)
q0=WF(6,'qualquer')-0.1;qs=(WF(6,'quatro')-0.25-q0)/3
for i in range(4): click(q0+i*qs,0.07,0.3+0.13*i); tick(q0+i*qs+0.04,0.035,1300+i*140); tick(WF(6,'quatro')+i*0.09,0.03,2000+i*100)
for i,(w,m) in enumerate((('compra',74),('região',77),('quanto',81),('para',86))): ding(WF(7,w)+0.02,0.05,m,0.3+0.13*i,5);tick(WF(7,w),0.04,2200)
# 3 OPÇÕES
sweep(PICK-0.35,0.5,600,5000,0.07)
for i in range(3): pop(C[8]['start']+0.5+i*0.18,0.07,760+i*120,0.4+0.1*i)
for i in range(3): ding(WF(8,'porquê')+i*0.15,0.035,81+i*2,0.4+0.1*i,7)
# PRODUTO
sweep(PROD-0.7,0.7,300,8000,0.08,'rise');impact(PROD+0.02,0.26)
pop(C[9]['start']+0.1,0.06,700,0.4);pop(WF(9,'whatsapp'),0.07,1000,0.6);pop(WF(9,'qualquer')+0.2,0.06,700,0.4)
pf=WF(10,'perfil');sweep(pf-0.35,0.45,900,4500,0.06);chime(pf-0.05,[65,69,72,77],0.035,1.5)
for i in range(4): tick(pf+0.1+i*0.12,0.04,2000+i*150,0.35+0.1*i)
# CTA
sweep(CTA-1.0,1.0,250,9000,0.085,'rise');impact(CTA+0.02,0.32);chime(CTA+0.05,[53,60,65,69],0.028,1.2)
dg=WF(11,'diagn')
for k in range(11): click(dg-0.25+k*0.7/11,0.05,0.5)
pop(dg+0.6,0.09,1200,0.6);chime(dg+0.62,[77,81,84],0.03,1.4)
chime(WF(11,'checklist')+0.25,[65,72,77,81],0.03,1.0)
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
