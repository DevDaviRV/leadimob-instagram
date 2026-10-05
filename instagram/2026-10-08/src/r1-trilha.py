"""Reel 1 (08/10) "Seu corretor não precisa de mais leads. Precisa de menos conversas."
Trilha original: 112 BPM, Dó menor -> Mi bemol maior. A ideia da peça está no arranjo, que SUBTRAI:
gancho cheio (plucks em semicolcheias + notificações empilhando) -> "menos" esvazia (colcheias, depois semínimas, filtro fecha)
-> lista quase vazia (sub + uma nota grave de piano elétrico por item, relógio às onze) -> triagem (pulso volta, filtro abre,
três sinos subindo em perfil/orçamento/visita) -> produto em Mi bemol maior (bumbo suave em 1 e 3, baixo, piano elétrico, arpejo com eco)
-> CTA (teclas no DIAGNÓSTICO, três marcações do checklist, acorde final).
Uso: python3 trilha.py -> mix_novo.wav (sem voz) e mix_vo.wav (com voz). Os tempos vêm do timeline.json (os mesmos do index.html)."""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[10]['end']+1.5; N=int(round(END*SR)); T=np.arange(N)/SR
rng=np.random.default_rng(808)
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
        if w['w'].lower().replace('“','').replace('"','').startswith(s.lower()): return w['t']
    return C[i]['start']
def saw(f,n,det=0.0):
    ph=np.cumsum(np.full(n,f*(1+det))/SR); return 2*(ph%1)-1
# ---- eventos da cena (iguais aos do index.html)
MAIS=WF(1,'mais'); LEADS=WF(1,'leads'); H2=C[2]['start']-0.22; MENOS=WF(2,'menos'); CONV=WF(2,'conversas')
S2=C[3]['start']+0.12; A=WF(3,'conversas'); A2=WF(3,'não'); B=WF(4,'perguntas'); Cq=WF(5,'ainda'); C2=WF(5,'onze')
S2OUT=C[6]['start']-0.22; LINE=WF(6,'triagem')+0.08; CRANE=WF(7,'só')+0.05; STOP=CRANE+1.35-0.08
PF=WF(7,'perfil'); OR=WF(7,'orçamento'); VI=WF(7,'visita'); S4=C[8]['start']-0.3; LD=WF(8,'leadimob'); WA=WF(8,'whatsapp')
AT=WF(9,'atende'); QU=WF(9,'qualifica'); PA=WF(9,'passa'); CO=WF(9,'corretor'); VA=WF(9,'vale')
CTA=C[9]['end']-0.02; CM=WF(10,'comente'); DG=WF(10,'diagn'); RC=WF(10,'receba'); CK=WF(10,'checklist')
BPM=112; beat=60/BPM; bar=4*beat
T0=S4-np.ceil(S4/bar)*bar               # grade ancorada: um tempo forte cai na virada para o produto
def sec(t):
    if t<MENOS-0.05: return 'hook'
    if t<S2: return 'menos'
    if t<S2OUT: return 'lista'
    if t<S4: return 'triagem'
    if t<CTA: return 'prod'
    return 'cta'
PM=[[36,58,62,63,67],[44,60,63,67,70],[41,60,63,65,68],[43,58,62,65,67]]      # Cm9  Abmaj9  Fm7  Gm7
PJ=[[39,58,65,67,70],[44,60,63,67,72],[36,58,63,67,70],[46,58,63,65,70]]      # Ebadd9  Abmaj7  Cm7  Bbsus4
def chord(t):
    b=int((t-T0)//bar)
    return (PJ if t>=S4 else PM)[(b//2)%4]
L=np.zeros(N);R=np.zeros(N)
nb=int((END-T0)/bar)+2
# ---- pad (serra filtrada; abre e fecha com as seções)
PL=np.zeros(N);PR=np.zeros(N)
for b in range(0,nb,2):
    st=T0+b*bar
    if st>END: break
    ch=chord(st+0.01); n=int((2*bar+1.6)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.8)*np.clip((2*bar+1.6-tt)/1.6,0,1)
    for m in ch[1:]:
        for d,pan in((-0.005,.22),(0.005,.78)):
            s=saw(midi(m),n,d)*env*0.010; add(PL,s*(1-pan),st); add(PR,s*pan,st)
cv={'hook':.55,'menos':.25,'lista':.06,'triagem':.45,'prod':.9,'cta':1.0}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(24000)/24000,'same')
PLd,PRd,PLo,PRo=lp(PL,420),lp(PR,420),lp(PL,3200),lp(PR,3200)
L+=PLd*(1-ctrl)+PLo*ctrl; R+=PRd*(1-ctrl)+PRo*ctrl
# ---- instrumentos
def pluck(m,g,dec=16):      # madeira curta (marimba abafada)
    n=int(0.35*SR);tt=np.arange(n)/SR;f=midi(m)
    return (np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*4*f*tt)*np.exp(-tt*40))*np.exp(-tt*dec)*g
def epiano(m,g,dur=2.2):    # piano elétrico (FM de índice decrescente)
    n=int(dur*SR);tt=np.arange(n)/SR;f=midi(m)
    return np.sin(2*np.pi*f*tt+1.6*np.exp(-tt*5)*np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*14*f*tt)*np.exp(-tt*30))*np.exp(-tt*2.2)*np.minimum(1,tt/0.004)*g
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N);EL=np.zeros(N);ER=np.zeros(N)
seq=[1,3,2,4,1,2,4,3,2,4,1,3,4,2,3,1]; arp=[0,2,1,3,2,3,1,2]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.0: continue
    s_=sec(t); pos=k%16; ch=chord(t)
    # plucks: 16 por compasso no gancho, 8 em "menos", 2 na lista, 4 na triagem
    hit={'hook':True,'menos':pos%2==0 if t<CONV else pos%4==0,'lista':pos in(0,10),'triagem':pos%4==0 or (t>CRANE and pos%2==0),'prod':False,'cta':False}[s_]
    if hit:
        g={'hook':0.05+0.012*((k*3)%4),'menos':0.05,'lista':0.03,'triagem':0.04}[s_]
        x=pluck(ch[seq[pos]]+12,g);pan=0.2+0.6*((k*5)%8)/7;add(AL,x*(1-pan),t);add(AR,x*pan,t)
    # bumbo suave: só no produto e no começo do CTA
    if s_ in('prod','cta') and pos in(0,8) and t<CK+0.4:
        n=int(0.4*SR);tt=np.arange(n)/SR;fk=44+90*np.exp(-tt*32)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*8)*0.19;add(L,kk,t);add(R,kk,t);KICKS.append(t)
    # chimbal discreto
    if (s_=='prod' and pos%2==0) or (s_=='triagem' and pos%4==2 and t>LINE) or (s_=='hook' and pos%4==2):
        n=int(0.035*SR);tt=np.arange(n)/SR;vel=[.7,.3,.5,.3][(pos//2)%4]
        h=hp(rng.standard_normal(n),9500)*np.exp(-tt*150)*0.016*vel;pan=0.3+0.4*((k*3)%5)/4;add(L,h*(1-pan),t);add(R,h*pan,t)
    # baixo
    gb={'hook':0.06 if pos%4==0 else 0,'menos':0.05 if pos%8==0 else 0,'lista':0.045 if pos==0 else 0,'triagem':0.06 if pos%4==0 else 0,
        'prod':0.062 if pos in(0,3,8,10) else 0,'cta':0.058 if pos in(0,8) and t<CK+0.4 else 0}[s_]
    if gb:
        dur=beat*(2.6 if s_=='lista' else 0.9);n=int(dur*SR);tt=np.arange(n)/SR;f=midi(ch[0]-(12 if ch[0]>=41 else 0))
        add(BL,(np.sin(2*np.pi*f*tt)+0.28*np.sin(4*np.pi*f*tt))*np.exp(-tt*(1.2 if s_=='lista' else 3.2))*np.minimum(1,tt/0.006)*gb,t)
    # produto: acordes de piano elétrico no tempo 1 e arpejo em colcheias
    if s_ in('prod','cta') and pos==0 and t<END-1.6:
        for i,m in enumerate(ch[1:]): x=epiano(m,0.022);pan=0.3+0.13*i;add(EL,x*(1-pan),t+i*0.012);add(ER,x*pan,t+i*0.012)
    if s_=='prod' and pos%2==0 and t>AT-0.3:
        m=ch[1:][arp[(k//2)%8]]+12;x=pluck(m,0.028,12);add(AL,x*0.8,t);add(AR,x*0.55,t)
d=int(beat*0.75*SR)
for rep in range(1,4):
    g=0.30**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.28*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.4*np.exp(-tt/0.08)[:j-i])
L=L*sc+BL*sc+AL+EL;R=R*sc+BL*sc+AR+ER
ir_n=int(2.2*SR);tt=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-tt*2.8);irR=rng.standard_normal(ir_n)*np.exp(-tt*2.8);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.26*fftconvolve(hp(L,300),irL)[:N];R=R+0.26*fftconvolve(hp(R,300),irR)[:N]
# ---------------- efeitos presos aos eventos ----------------
FL=np.zeros(N);FR=np.zeros(N)
def st2(x,at,pan=.5,g=1): add(FL,x*(1-pan)*1.4*g,at);add(FR,x*pan*1.4*g,at)
def sweep(at,dur,f0,f1,g,env='bell'):
    n=int(dur*SR);tt=np.arange(n)/SR;x=rng.standard_normal(n);out=np.zeros(n);seg=960
    for i in range(0,n,seg):
        k=i/n;f=f0+(f1-f0)*(k**2 if env=='rise' else np.sin(np.pi*k));out[i:i+seg]=bp(x[max(0,i-3000):i+seg],max(60,f*0.7),min(f*1.45,20000))[-len(out[i:i+seg]):]
    e=(tt/dur)**2 if env=='rise' else np.sin(np.pi*tt/dur)**2
    pan=np.linspace(.3,.7,n);s=out*e*g;add(FL,s*(1-pan),at);add(FR,s*pan,at)
def thud(at,g=0.2):
    n=int(0.9*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*(46+34*np.exp(-tt*18))*tt)*np.exp(-tt*5)*g;add(FL,s,at);add(FR,s,at)
def tick(at,g=0.05,f=2400,pan=.5):
    n=int(0.05*SR);tt=np.arange(n)/SR;st2(np.sin(2*np.pi*f*tt)*np.exp(-tt*140)*g,at,pan)
def pop(at,g=0.07,f=900,pan=.5):
    n=int(0.14*SR);tt=np.arange(n)/SR;fr=f*(1+0.6*np.exp(-tt*60));st2(np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*38)*g,at,pan)
def ding(at,g=0.04,m=88,pan=.5,dec=6):
    n=int(0.9*SR);tt=np.arange(n)/SR;f=midi(m);st2((np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2.76*f*tt)*np.exp(-tt*9))*np.exp(-tt*dec)*g,at,pan)
def bell(at,m,g=0.04,dec=2.0,pan=.5):
    n=int(2.4*SR);tt=np.arange(n)/SR;f=midi(m);st2((np.sin(2*np.pi*f*tt)+0.2*np.sin(2*np.pi*2.01*f*tt)+0.08*np.sin(2*np.pi*3.0*f*tt)*np.exp(-tt*6))*np.exp(-tt*dec)*np.minimum(1,tt/0.003)*g,at,pan)
def click(at,g=0.05,pan=.5):
    n=int(0.02*SR);tt=np.arange(n)/SR;st2(hp(rng.standard_normal(n),2500)*np.exp(-tt*400)*g,at,pan)
# GANCHO: notificações empilhando; aceleram em "mais", rareiam em "menos"
t=0.08
while t<MENOS+0.5:
    dens=0.34 if t<MAIS-0.1 else (0.15 if t<H2+0.25 else 0.5)
    ding(t,0.014+0.010*rng.random(),int(rng.choice([79,82,84,87,91])),0.15+0.7*rng.random(),9); t+=dens*(0.75+0.5*rng.random())
thud(LEADS+0.42,0.10)                                   # "mais leads" perde a cor
sweep(MENOS-0.45,0.6,3800,500,0.05); thud(MENOS-0.1,0.2)   # o fluxo freia em MENOS
tick(CONV-0.14,0.04,1500)
sweep(S2-0.1,0.6,700,2600,0.035)                        # MENOS vira cabeçalho
# LISTA: uma nota grave de piano elétrico por item (descendo), efeitos pequenos por mudança na caixa de entrada
for at,m in((A-0.1,55),(B-0.1,53),(Cq-0.1,51)): x=epiano(m,0.05,2.6);add(FL,x,at);add(FR,x,at)
sweep(A2,0.7,1800,400,0.03)                             # conversas perdem a cor
for k in range(8): tick(B+0.06+0.075*k,0.03*(1-k/11),1900-k*90,0.25+0.07*k)   # prévias viram a mesma pergunta
for k in range(4): tick(C2-0.45+k*0.5,0.035,1250 if k%2 else 1500,0.4+0.2*(k%2))   # relógio
ding(C2+0.08,0.03,70,0.6,5)                             # 23:00 (o detalhe âmbar)
# TRIAGEM
sweep(S2OUT-0.05,0.55,2400,500,0.04)
sweep(LINE-0.05,0.6,900,5200,0.06); bell(LINE+0.3,79,0.02,3)            # linha traçada + etiqueta
for k in range(7): tick(LINE+0.5+k*0.19,0.022,1100-k*40,0.3+0.06*k)   # conversas barradas (descendo)
bell(LINE+1.0,75,0.022,2.5,0.4); bell(STOP-0.35,79,0.03,2.2,0.55)       # as que passam
sweep(CRANE-0.1,1.3,300,4200,0.06,'rise'); thud(STOP-0.02,0.16)        # câmera sobe e fica de frente
for at,m,p in((PF,67,0.3),(OR,70,0.5),(VI,75,0.7)): bell(at+0.05,m,0.045,1.8,p); tick(at+0.24,0.035,2600,p)
# PRODUTO
sweep(S4-0.5,0.55,400,5000,0.06,'rise'); thud(S4+0.05,0.22); bell(S4+0.08,63,0.02,1.4)
pop(S4+0.55,0.06,700,0.35)                              # mensagem do lead
bell(LD+0.1,82,0.025,3,0.5)                             # selo Leadimob
for k in range(5): click(WA-0.05+k*0.2,0.022,0.65)      # digitando
pop(AT+0.05,0.08,1000,0.65); bell(AT+0.02,75,0.03,2.2,0.3)
pop(QU-0.38,0.06,720,0.35)
for i in range(3): tick(QU+0.1+i*0.2,0.045,2000+i*260,0.3+0.2*i)
bell(QU+0.55,79,0.03,2.2,0.5)
sweep(PA-0.15,0.5,1500,500,0.035); bell(PA+0.02,82,0.03,2.2,0.7)        # conversa fecha, passo 3
sweep(CO-0.1,0.5,800,4200,0.05); pop(CO+0.32,0.07,1100,0.72)            # ponto corre até o corretor
for i,m in enumerate((75,79,82,87)): bell(VA-0.02+i*0.06,m,0.03,1.6,0.5)  # vale o próximo passo
# CTA
sweep(CTA,0.72,500,6500,0.07); thud(CTA+0.7,0.18)
for i in range(11): click(DG-0.05+i*0.72/11,0.04+0.01*(i%3),0.42+0.02*i)
pop(DG+0.86,0.08,1200,0.62)                             # enviar
for i in range(3): tick(CK+0.05+i*0.2,0.045,2100+i*200,0.35+0.1*i)
for i,m in enumerate((63,70,75,79,82)): bell(CK+0.7+i*0.07,m,0.03,1.3,0.3+0.1*i)
# ---------------- voz, ducking e mixagem ----------------
V=np.zeros(N)
for c in TL:
    sr,x=wavfile.read(f"vo_b/p{c['i']:02d}.wav");x=x.astype(np.float64)/32768.0
    if x.ndim>1: x=x.mean(1)
    if sr!=SR: x=resample_poly(x,SR,sr)
    add(V,x,c['start'])
env=lp(np.abs(V),6);env=np.clip(env/0.05,0,1);duck=1-0.55*env
fade=np.clip(T/0.04,0,1)*np.clip((END-T)/1.2,0,1)
L*=duck*fade;R*=duck*fade
vr=np.sqrt(np.mean(V[lp(np.abs(V),6)>0.01]**2));mr=np.sqrt(np.mean(((L+R)/2)**2))
gm=vr*10**(-12/20)/mr;L*=gm;R*=gm;FL*=fade;FR*=fade
sfr=np.sqrt(np.mean(((FL+FR)/2)**2)); FL*=vr*10**(-17/20)/sfr; FR*=vr*10**(-17/20)/sfr
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_novo.wav',L+FL,R+FR);save('mix_vo.wav',(L+FL)+V,(R+FR)+V)
def db(x): return round(20*np.log10(np.sqrt(np.mean(x**2))+1e-12),1)
print('END',round(END,3),'voz',db(V[np.abs(V)>1e-4]),'musica',db((L+R)/2),'efeitos',db((FL+FR)/2))
for a,b,nm in((0,MENOS,'gancho'),(S2,S2OUT,'lista'),(S2OUT,S4,'triagem'),(S4,CTA,'produto'),(CTA,END,'cta')):
    i,j=int(a*SR),int(b*SR);print(nm,'musica',db((L[i:j]+R[i:j])/2),'efeitos',db((FL[i:j]+FR[i:j])/2),'voz',db(V[i:j]))
