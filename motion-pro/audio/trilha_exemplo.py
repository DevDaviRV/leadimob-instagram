"""Trilha v3 (institucional) — 108 BPM, Mi menor, arranjo que cresce com o método.
Uso: python3 audio3.py [pasta_voz=vo_b]"""
import numpy as np, json, sys, re
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from scipy.io import wavfile
SR=48000; VODIR=sys.argv[1] if len(sys.argv)>1 else 'vo_b'
TL=json.load(open('timeline.json')); C={c['i']:c for c in TL}
END=C[26]['end']+2.3; N=int((END+1)*SR); T=np.arange(N)/SR
rng=np.random.default_rng(23)
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
BPM=108; beat=60/BPM; bar=4*beat
DROP=C[7]['start']-0.1
T0=DROP-np.ceil(DROP/bar)*bar
S={'hook':0,'cen':C[3]['start']-0.4,'who':DROP,'met':C[11]['start']-0.3,'sol':C[17]['start']-0.2,'val':C[19]['start']-0.3,
   'pri':C[22]['start']-0.15,'cta':C[24]['start']-0.1,'sig':C[26]['start']-0.2,'end':END}
steps=[C[12+i]['start'] for i in range(5)]
def sec(t):
    k='hook'
    for n in ['cen','who','met','sol','val','pri','cta','sig']:
        if t>=S[n]: k=n
    return k
def layer(t):  # 0..5 arrangement density
    s=sec(t)
    if s in('hook','cen'): return 0
    if s=='who': return 1
    if s=='met': return 1+sum(t>=x for x in steps)   # grows per step
    if s in('sol','val'): return 5
    if s=='pri': return -1
    if s=='cta': return 3
    return -2
prog=[[40,64,67,71,74,78],[36,64,67,71,74,76],[43,62,67,71,74,76],[42,62,66,69,74,78]]  # Em9 Cmaj7 G6 D/F#
def saw(f,n,det=0.0):
    ph=np.cumsum(np.full(n,f*(1+det))/SR); return 2*(ph%1)-1
L=np.zeros(N);R=np.zeros(N)
nb=int((END-T0)/bar)+2
# pad
PL=np.zeros(N);PR=np.zeros(N)
for b in range(0,nb,2):
    st=T0+b*bar
    if st>END: break
    ch=prog[(b//2)%4]; n=int((2*bar+1.6)*SR); tt=np.arange(n)/SR
    env=np.minimum(1,tt/1.0)*np.clip((2*bar+1.6-tt)/1.6,0,1)
    for m in ch[1:]:
        for d,pan in((-0.005,.15),(0.005,.85)):
            s=saw(midi(m),n,d)*env*0.011; add(PL,s*(1-pan),st); add(PR,s*pan,st)
ctrl=np.array([{'hook':.2,'cen':.35,'who':.8,'met':.9,'sol':.6,'val':1,'pri':.25,'cta':.8,'sig':.7}[sec(x)] for x in T[::480]])
ctrl=np.convolve(np.repeat(ctrl,480)[:N],np.ones(24000)/24000,'same')
PLd,PRd,PLo,PRo=lp(PL,600),lp(PR,600),lp(PL,3200),lp(PR,3200)
L+=PLd*(1-ctrl)+PLo*ctrl; R+=PRd*(1-ctrl)+PRo*ctrl
# drums / bass / arp by 16ths
KICKS=[];BL=np.zeros(N);AL=np.zeros(N);AR=np.zeros(N)
pat=[0,2,4,1,3,5,2,4]
for k in range(int((END-T0)/(beat/4))+1):
    t=T0+k*beat/4
    if t<0 or t>END-1.5: continue
    lay=layer(t); pos=k%16
    b=int((t-T0)//bar); ch=prog[(b//2)%4]
    # kick
    if lay>=1 and pos in (0,6,8) :
        n=int(0.42*SR);tt=np.arange(n)/SR;fk=44+100*np.exp(-tt*32)
        kk=np.sin(2*np.pi*np.cumsum(fk)/SR)*np.exp(-tt*8)*0.3+hp(rng.standard_normal(n),3500)*np.exp(-tt*220)*0.03
        add(L,kk,t);add(R,kk,t);KICKS.append(t)
    if lay>=1 and pos in (4,12):
        n=int(0.26*SR);tt=np.arange(n)/SR;cp=bp(rng.standard_normal(n),1000,5500)*(np.exp(-tt*26)+0.4*np.exp(-np.abs(tt-0.011)*300))*0.065
        add(L,cp*0.9,t);add(R,cp,t)
    # hats: cenário ticking (tension), groove 16ths from step 2
    if (lay==0 and sec(t)=='cen' and pos%2==0) or (lay>=2 and True) or (lay==1 and pos%2==0) or (lay==3 and sec(t)=='cta'):
        n=int(0.04*SR);tt=np.arange(n)/SR;vel=[.8,.25,.5,.3][pos%4]*(0.6 if lay==0 else 1)
        h=hp(rng.standard_normal(n),8500)*np.exp(-tt*120)*0.026*vel;pan=0.3+0.4*((k*3)%5)/4;add(L,h*(1-pan),t);add(R,h*pan,t)
    # bass 8ths (cenário: drone pulses on beats)
    if pos%2==0 and lay!=-2:
        n=int(beat/2*SR*0.92);tt=np.arange(n)/SR;f=midi(ch[0]-12 if lay>=3 else ch[0])
        g=0.06 if lay<=0 else 0.1
        if lay==-1: g=0.04
        s=(np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt))*np.exp(-tt*4)*g
        if lay>=0 or pos%8==0: add(BL,s,t)
    # arp (from step 1) with delay
    if lay>=2 or (lay==1 and sec(t)=='met'):
        if pos%2==0:
            m=ch[1:][pat[(k//2)%8]%5]+12;n=int(0.3*SR);tt=np.arange(n)/SR
            s=lp(saw(midi(m),n)*np.exp(-tt*10),2800)*(0.018 if lay<5 else 0.022)
            add(AL,s,t);add(AR,s*0.8,t)
    # counter pluck (step 4+)
    if lay>=4 and pos in (3,11,14):
        m=ch[2]+24;n=int(0.25*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*midi(m)*tt)*np.exp(-tt*14)*0.02
        add(AL,s*0.6,t);add(AR,s,t)
# hook chaos: random detuned plucks, dense and irregular
tc=WF(2,'cresc')
for j in range(46):
    t=0.1+rng.random()*(tc-0.2);m=int(rng.choice([64,66,67,69,71,72,74,76,79]))+int(rng.choice([0,12]))
    n=int(0.22*SR);tt=np.arange(n)/SR;s=lp(saw(midi(m)*(1+rng.normal(0,0.01)),n)*np.exp(-tt*16),3000)*0.012
    pan=rng.random();add(AL,s*(1-pan),t);add(AR,s*pan,t)
d=int(beat*0.75*SR)
for rep in range(1,4):
    g=0.35**rep;src=(AL if rep%2 else AR).copy();tgt=AR if rep%2 else AL;tgt[d*rep:]+=src[:-d*rep]*g
sc=np.ones(N)
for kt in KICKS:
    i=int(kt*SR);n=int(0.32*SR);tt=np.arange(n)/SR;j=min(N,i+n);sc[i:j]=np.minimum(sc[i:j],1-0.55*np.exp(-tt/0.09)[:j-i])
L=L*sc+BL*sc+AL;R=R*sc+BL*sc+AR
ir_n=int(2.6*SR);tt=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-tt*2.2);irR=rng.standard_normal(ir_n)*np.exp(-tt*2.2);irL/=np.sqrt((irL**2).sum());irR/=np.sqrt((irR**2).sum())
L=L+0.3*fftconvolve(hp(L,300),irL)[:N];R=R+0.3*fftconvolve(hp(R,300),irR)[:N]
# ---------------- SFX ----------------
FL=np.zeros(N);FR=np.zeros(N)
def sweep(at,dur,f0,f1,g,env='bell'):
    n=int(dur*SR);tt=np.arange(n)/SR;x=rng.standard_normal(n);out=np.zeros(n);seg=960
    for i in range(0,n,seg):
        k=i/n;f=f0+(f1-f0)*(k**2 if env=='rise' else np.sin(np.pi*k));out[i:i+seg]=bp(x[max(0,i-3000):i+seg],max(60,f*0.7),min(f*1.45,20000))[-len(out[i:i+seg]):]
    e=(tt/dur)**2 if env=='rise' else np.sin(np.pi*tt/dur)**2
    pan=np.linspace(.2,.8,n);s=out*e*g;add(FL,s*(1-pan),at);add(FR,s*pan,at)
def impact(at,g=0.34):
    n=int(1.8*SR);tt=np.arange(n)/SR;f=36+70*np.exp(-tt*9)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*2.6)*g+lp(rng.standard_normal(n),1400)*np.exp(-tt*12)*g*0.25;add(FL,s,at);add(FR,s,at)
def tick(at,g=0.05,f=2400,pan=.5):
    n=int(0.05*SR);tt=np.arange(n)/SR;s=np.sin(2*np.pi*f*tt)*np.exp(-tt*140)*g;add(FL,s*(1-pan)*1.4,at);add(FR,s*pan*1.4,at)
def snap(at,g=0.12):
    n=int(0.3*SR);tt=np.arange(n)/SR;s=bp(rng.standard_normal(n),1500,6000)*np.exp(-tt*40)*g+np.sin(2*np.pi*170*tt)*np.exp(-tt*30)*g*0.5;add(FL,s,at);add(FR,s,at)
def chime(at,notes,g=0.035,dec=1.3):
    n=int(3*SR);tt=np.arange(n)/SR;s=np.zeros(n)
    for i,m in enumerate(notes):
        dd=int(i*0.07*SR);f=midi(m);s[dd:]+=(np.sin(2*np.pi*f*tt[:n-dd])+0.25*np.sin(2*np.pi*2.01*f*tt[:n-dd]))*np.exp(-tt[:n-dd]*dec)
    add(FL,s*g,at);add(FR,s*g,at)
# hook: riser to "crescimento" + impact
sweep(tc-1.6,1.6,300,7000,0.08,'rise');impact(tc,0.36);chime(tc+0.05,[64,71,76],0.02,1.8)
sweep(C[3]['start']-0.8,0.8,500,4000,0.1)
# cenário: breaks/ticks per phrase
snap(WF(3,'demora'),0.12);tick(WF(4,'perdem'),0.05,1200);tick(WF(5,'diferen'),0.05,1500,.3);tick(WF(5,'diferen')+0.08,0.05,1500,.7)
for k in range(3): tick(C[6]['start']+0.4+k*0.18,0.04,1800+k*250,0.3+k*0.2)
# who: Y-band whoosh + drop
sweep(C[7]['start']-2.0,1.8,300,8000,0.09,'rise');sweep(C[7]['start']-0.35,0.8,600,6000,0.16);impact(DROP,0.38)
lw=C[9]['words'];
for j in [1,2,3,len(lw)-1]: tick(lw[j]['t'],0.055,1400+j*120)
chime(WF(10,'única'),[71,76,83],0.022,1.6)
# method: riser + tick into each step, overview whoosh
sweep(C[11]['start']-0.5,0.8,500,5000,0.12)
for i,st in enumerate(steps): sweep(st-0.9,0.9,400,6000,0.05,'rise');tick(st-0.02,0.07,1600+i*200);sweep(st+0.05,0.5,800,4000,0.05)
chime(steps[4]+0.1,[76,83,88],0.02,1.6)
sw=C[17]['words'];
for tt_ in [sw[0]['t'],WF(17,'estrutura'),WF(17,'growth')]: tick(tt_,0.06,2000)
chime(WF(18,'única'),[71,78,83],0.02,1.6)
# value: long whoosh following dolly + node ticks
sweep(C[19]['start']+0.2,C[20]['end']-C[19]['start'],400,3000,0.07)
for w in ['clareza','velocidade','decisões']: tick(WF(21,w),0.06,1900)
# principle: hard stop hits
impact(C[22]['start']-0.1,0.3);impact(C[23]['start']-0.05,0.25)
# CTA
sweep(C[24]['start']-0.9,0.9,300,6000,0.07,'rise');impact(WF(24,'diagn'),0.3)
# slogan: Y band + chimes per word
sweep(C[26]['start']-0.4,0.8,600,6000,0.14)
for j,w in enumerate(C[26]['words']): chime(w['t'],[[64,71],[67,74],[71,76,83]][j],0.03,1.1)
# ---------------- voice ----------------
V=np.zeros(N)
for c in TL:
    sr,x=wavfile.read(f"{VODIR}/p{c['i']:02d}.wav");x=x.astype(np.float64)/32768.0
    if x.ndim>1: x=x.mean(1)
    if sr!=SR: x=resample_poly(x,SR,sr)
    add(V,x,c['start'])
env=lp(np.abs(V),6);env=np.clip(env/0.05,0,1);duck=1-0.5*env
fade=np.clip(T/0.2,0,1)*np.clip((END-T)/1.6,0,1)
L*=duck*fade;R*=duck*fade
vr=np.sqrt(np.mean(V[lp(np.abs(V),6)>0.01]**2));mr=np.sqrt(np.mean(((L+R)/2)**2))
gm=vr*10**(-12/20)/mr;L*=gm;R*=gm;FL*=gm*1.2*fade;FR*=gm*1.2*fade
def save(name,l,r):
    st=np.stack([l,r],1);st=st/max(np.max(np.abs(st)),1e-9)*0.89;wavfile.write(name,SR,(st*32767).astype(np.int16))
save('mix_novo.wav',L+FL,R+FR);save('mix_vo.wav',(L+FL)*0.9+V,(R+FR)*0.9+V)
print('END',END,'gain',round(gm,3))
