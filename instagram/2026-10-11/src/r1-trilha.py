"""Leadimob R1 11/10 — trilha original: 112 BPM, Dó menor -> Mi bemol maior.
Arranjo novo: pluck de cordas (Karplus-Strong) em vez de serras, pad de seno/triângulo, baixo sub, rimshot e shaker.
Gancho (pulso contido, Dó menor) -> a cobrança (relógio) -> O SILÊNCIO (a trilha corta, só um grave) ->
"volte com algo" (abre em Mi bemol maior) -> três motivos (cheio, um acorde por motivo) -> tese (só pad, kick no 1) ->
Leadimob (groove completo) -> CTA (resolve em Mi bemol).
Uso: /usr/bin/python3 trilha.py -> mix_novo.wav (sem voz) e mix_vo.wav (com voz)"""
import numpy as np, json
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[10]['end']+2.1; N=int((END+0.5)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(1110)
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
def pluck(f,dur,g=1.0,bright=0.5):
    n=int(dur*SR);L=max(2,int(SR/f));buf=rng.uniform(-1,1,L);buf=lp(buf,2000+6000*bright) if L>30 else buf
    out=np.zeros(n);d=0.996
    for i in range(n):
        v=buf[i%L];out[i]=v;buf[i%L]=d*0.5*(v+buf[(i+1)%L])
    return out*g
PL={}
def pl(m,dur=0.9,b=0.5):
    k=(m,dur,b)
    if k not in PL: PL[k]=pluck(midi(m),dur,1.0,b)
    return PL[k]
BPM=112; beat=60/BPM; bar=4*beat
TA=C[2]['start']-0.4; SIL=WF(2,'silêncio'); TC=C[4]['start']-0.62; TK=C[5]['start']-0.42
P1=C[6]['start']-0.38; P2=C[7]['start']-0.34; TD=C[8]['start']-0.3; TE=C[9]['start']-0.48; TF=C[10]['start']-0.5
T0=(TC+0.36)-np.ceil((TC+0.36)/bar)*bar      # tempo forte no meio da grua
def sec(t):
    if t<TA: return 'hook'
    if t<SIL-0.05: return 'cob'
    if t<TC+0.36: return 'sil'
    if t<TK: return 'volte'
    if t<TD: return 'mot'
    if t<TE: return 'tese'
    if t<TF: return 'prod'
    return 'cta'
MIN=[[36,60,63,67,70],[32,60,63,67,72],[39,58,63,67,70],[31,59,62,67,71]]      # Cm9 Abmaj7 Eb G
MAJ=[[39,58,63,67,70,74],[44,60,63,67,72,75],[36,58,63,67,70,74],[34,58,62,65,70,74]]  # Eb Ab Cm7 Bb
def chord(t):
    b=int(np.floor((t-T0)/bar)); s=sec(t)
    if s in('hook','cob','sil'): return MIN[(b//1)%4]
    if s=='mot':
        k=0 if t<P1 else 1 if t<P2 else 2; return [MAJ[1],MAJ[2],MAJ[3]][k]
    if s=='tese': return MAJ[1]
    if s=='cta': return MAJ[0]
    return MAJ[b%4]
L=np.zeros(N);R=np.zeros(N)
# pad: seno + triângulo suave, um acorde por compasso, filtrado pela seção
PLp=np.zeros(N);PRp=np.zeros(N)
nb=int((END-T0)/bar)+2
for b in range(nb):
    st=T0+b*bar
    if st>END or st+bar<0: continue
    ch=chord(max(st+0.01,0)); n=int((bar+1.2)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/0.6)*np.clip((bar+1.2-tt)/1.2,0,1)
    for j,m in enumerate(ch[1:]):
        f=midi(m); x=(np.sin(2*np.pi*f*tt)+0.25*np.sin(2*np.pi*2*f*tt+0.3)+0.08*np.sin(2*np.pi*3*f*tt))*env*0.011
        pan=0.3+0.4*(j%2); add(PLp,x*(1-pan),st); add(PRp,x*pan,st)
cv={'hook':.35,'cob':.4,'sil':0.0,'volte':.7,'mot':1.0,'tese':.6,'prod':1.0,'cta':.85}
ctrl=np.array([cv[sec(x)] for x in T[::480]]); ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(9600)/9600,'same')
L+=lp(PLp,2600)*ctrl; R+=lp(PRp,2600)*ctrl
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
arp=[0,2,1,3,2,1,3,2]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.0: continue
    s=sec(t); pos=k%16; ch=chord(t)
    if s=='sil': continue
    full=s in('mot','prod')
    # kick
    if (s in('volte','mot','prod') and pos in(0,6,8)) or (s in('tese','cta','cob') and pos==0):
        n=int(0.4*SR);tt=np.arange(n)/SR;fk=46+110*np.exp(-tt*34)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*8)*(0.18 if s=='cob' else 0.28)
        add(L,kk,t);add(R,kk,t);KICKS.append(t)
    # rimshot no 2 e 4
    if full and pos in(4,12):
        n=int(0.12*SR);tt=np.arange(n)/SR;rm=(bp(rng.standard_normal(n),1500,4500)*np.exp(-tt*45)+np.sin(2*np.pi*820*tt)*np.exp(-tt*60)*0.5)*0.045
        add(L,rm*0.8,t);add(R,rm,t)
    # shaker em semicolcheias
    if full or (s in('volte','cta') and pos%2==0):
        n=int(0.06*SR);tt=np.arange(n)/SR;vel=[.9,.3,.6,.35][pos%4]
        h=bp(rng.standard_normal(n),5000,12000)*np.minimum(1,tt/0.008)*np.exp(-tt*70)*0.02*vel;pan=0.35+0.3*((k*3)%5)/4;add(L,h*(1-pan),t);add(R,h*pan,t)
    # relógio na cobrança e no gancho (tique contido)
    if s in('hook','cob') and pos%4==0:
        n=int(0.03*SR);tt=np.arange(n)/SR;tk=np.sin(2*np.pi*(2200 if pos%8==0 else 1800)*tt)*np.exp(-tt*200)*0.02;add(L,tk*0.6,t);add(R,tk,t)
    # baixo sub
    if pos in(0,8) and s not in('hook',) or (s=='hook' and pos==0):
        n=int(beat*2*SR*0.9);tt=np.arange(n)/SR;f=midi(ch[0])
        g={'hook':0.06,'cob':0.06,'volte':0.09,'mot':0.11,'tese':0.07,'prod':0.11,'cta':0.1}[s]
        x=(np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt))*np.minimum(1,tt/0.01)*np.exp(-tt*1.6)*g; add(BL,x,t)
    # pluck: arpejo em colcheias (gancho esparso, motivos/produto cheio)
    if (s=='hook' and pos%8==0) or (s=='cob' and pos%8==4) or (s in('volte','tese','cta') and pos%4==0) or (full and pos%2==0):
        m=ch[1:][arp[(k//2)%8]%len(ch[1:])]+12
        x=pl(m,0.9,0.45 if s in('hook','cob') else 0.7)*(0.05 if full else 0.04)
        pan=0.3+0.4*((k//2)%2); add(AL,x*(1-pan),t); add(AR,x*pan,t)
d=int(beat*0.75*SR)
for rep in range(1,3):
    g=0.3**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.28*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.4*np.exp(-tt/0.08)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
# o silêncio: só um grave de Dó, bem baixo
n=int((TC+0.4-SIL)*SR);tt=np.arange(n)/SR
dr=(np.sin(2*np.pi*midi(36)*tt)+0.3*np.sin(2*np.pi*midi(48)*tt*1.003))*0.035*np.clip(tt/0.6,0,1)*np.clip((TC+0.4-SIL-tt)/0.3,0,1)
add(L,dr,SIL);add(R,dr,SIL)
ir_n=int(2.0*SR);tt=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-tt*3.0);irR=rng.standard_normal(ir_n)*np.exp(-tt*3.0);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.24*fftconvolve(hp(L,300),irL)[:N];R=R+0.24*fftconvolve(hp(R,300),irR)[:N]
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
# GANCHO: digitando e enviando
a=WF(1,'ainda')-0.18
for k in range(20):
    tk=-0.3+(a-0.35+0.3)*(k+0.5)/20
    if tk>0: key(tk,0.03,0.4+0.2*(k%2))
click(a-0.04,0.08,0.7);swoosh_send(a-0.02,0.05);pop(a+0.05,0.06,1000,0.7)
# conversa
sweep(TA-0.15,0.6,3000,800,0.05);pop(TA+0.4,0.05,780,0.6)
tk=WF(2,'resposta');pop(tk,0.04,1500,0.7)
for k in range(3): click(WF(2,'fácil')-0.25+k*0.18,0.02,0.3)
thud(SIL-0.05,0.14);pop(SIL+0.05,0.05,420,0.5)
a2=WF(3,'cliente')-0.15;a3=WF(3,'porque')-0.1
for x in(a2,a3): swoosh_send(x-0.05,0.04);pop(x+0.02,0.055,950,0.7)
thud(WF(3,'motivo')+0.05,0.1)
# grua
sweep(TC-0.4,0.75,400,5200,0.08,'rise');impact(TC+0.36,0.26);chime(WF(4,'usar')+0.05,[63,70,75],0.022,1.6)
# título -> cabeçalho, trilho entra
sweep(TK-0.2,0.7,900,3600,0.045);whoosh_side(TK-0.15,0.6,0.05,False)
for i in range(3): pop(WF(5,'bate')-0.05+i*0.16,0.05,900+i*120,0.4+0.1*i)
chime(WF(5,'pediu'),[70,75,79],0.02,1.5)
whoosh_side(P1,0.6,0.06,False);pop(WF(6,'bairro')-0.2,0.06,700,0.5);chime(WF(6,'bairro'),[68,72,75],0.02,1.5)
whoosh_side(P2,0.6,0.06,False);pop(WF(7,'livre')-0.08,0.07,1100,0.55);chime(WF(7,'livre'),[70,74,77,82],0.025,1.4);pop(WF(7,'visitar')-0.05,0.05,1300,0.7)
whoosh_side(TD-0.05,0.4,0.07,False)
sweep(WF(8,'cobrar')-0.1,0.35,3000,600,0.04);thud(WF(8,'cobrar')+0.3,0.1)
# grua: a tese sobe, a conversa volta
sweep(TE-0.35,0.65,400,5000,0.07,'rise');impact(TE+0.3,0.22)
chime(WF(9,'leadimob')-0.1,[63,67,70,75],0.03,1.6)
m0=WF(9,'conversa')-0.25;swoosh_send(m0,0.04);pop(m0+0.05,0.05,900,0.7)
cx=WF(9,'contexto')-0.1
for k in range(3): pop(cx+k*0.12,0.045,1100+k*150,0.3+0.2*k)
r0=WF(9,'whatsapp')-0.35;pop(r0,0.07,720,0.3);chime(r0+0.25,[70,75,79,82],0.028,1.4)
# CTA
sweep(TF-0.3,0.6,500,4500,0.05,'rise');impact(TF+0.1,0.2);chime(TF+0.55,[63,70,75,79],0.028,1.5);pop(TF+0.7,0.05,700,0.4)
w0=WF(10,'diagn')
for k in range(11): key(w0-0.05+k*0.055,0.04,0.35+0.3*(k%2))
sd=WF(10,'e')+0.1;click(sd,0.09,0.6);pop(sd+0.05,0.06,800,0.4)
chime(WF(10,'receba')+0.5,[70,75,79,82],0.03,1.1)
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
