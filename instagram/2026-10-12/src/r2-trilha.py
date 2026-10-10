# Trilha do Reel 2 de 09/10: 104 BPM, Ré maior, pad + baixo + pulso suave + arpejo; marcações nos eventos da conversa.
import numpy as np, wave
SR=44100; BT=60/104; DUR=35*BT; N=int(SR*DUR); t=np.arange(N)/SR
rng=np.random.default_rng(909)
def env(n,a,d): e=np.ones(n); na=int(a*SR); nd=int(d*SR); e[:na]=np.linspace(0,1,na); e[-nd:]=np.linspace(1,0,nd); return e
def put(buf,sig,at,g=1.0):
    i=int(at*SR); j=min(N,i+len(sig)); 
    if i<N: buf[i:j]+=sig[:j-i]*g
L=np.zeros(N); R=np.zeros(N)
f=lambda m:440*2**((m-69)/12)
CH=[[50,57,62,66],[47,54,59,62],[43,50,55,59],[45,52,57,61]]   # D, Bm, G, A
bar=4*BT
for k in range(int(DUR/bar)+1):
    ch=CH[k%4]; n=int(bar*SR)+int(0.4*SR); tt=np.arange(n)/SR
    lvl=0.5 if k<2 else (0.8 if k<6 else 1.0)
    pad=sum(np.sin(2*np.pi*f(m)*tt+rng.random()*6)+0.4*np.sin(2*np.pi*f(m)*2.003*tt) for m in ch)/len(ch)
    pad*=env(n,0.5,0.5)*0.11*lvl
    put(L,pad,k*bar); put(R,np.roll(pad,180),k*bar)
    if k>=1:
        nb=int(bar*SR); tb=np.arange(nb)/SR; bass=np.sin(2*np.pi*f(ch[0]-12)*tb)*env(nb,0.02,0.3)*0.16
        put(L,bass,k*bar); put(R,bass,k*bar)
    for q in range(8):                      # arpejo em colcheias, entra no compasso 2
        if k<2: break
        m=ch[[0,2,1,3,2,3,1,2][q]]+12; n2=int(0.42*SR); ta=np.arange(n2)/SR
        a=np.sin(2*np.pi*f(m)*ta)*np.exp(-ta*7)*0.055
        at=k*bar+q*BT/2; pan=0.35+0.3*(q%2)
        put(L,a,at,1-pan); put(R,a,at,pan); put(L,a,at+BT*0.75,0.25*pan); put(R,a,at+BT*0.75,0.25*(1-pan))
    for q in range(4):                      # pulso suave
        if k<1: break
        n3=int(0.22*SR); tk=np.arange(n3)/SR; kick=np.sin(2*np.pi*(52+70*np.exp(-tk*38))*tk)*np.exp(-tk*16)*0.2
        put(L,kick,k*bar+q*BT); put(R,kick,k*bar+q*BT)
def tick(at,fr=1700,g=0.12,d=0.09):
    n=int(d*SR); tt=np.arange(n)/SR; s=np.sin(2*np.pi*fr*tt)*np.exp(-tt*60)*g; put(L,s,at); put(R,s,at)
def pop(at,up=True,g=0.16):
    n=int(0.16*SR); tt=np.arange(n)/SR; fr=(520+420*tt/0.16) if up else (760-260*tt/0.16); s=np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*22)*g; put(L,s,at); put(R,s,at)
def whoosh(at,d=0.8,g=0.10):
    n=int(d*SR); x=rng.standard_normal(n); k=np.cumsum(x); k=k-np.linspace(k[0],k[-1],n); k/=np.abs(k).max()+1e-9
    hp=x-np.convolve(x,np.ones(40)/40,'same'); s=(0.5*k+0.5*hp)*np.sin(np.pi*np.arange(n)/n)**2*g
    put(L,s,at); put(R,s[::-1],at)
b=lambda n:n*BT
whoosh(b(5.5)-0.1); pop(b(7),False); pop(b(8),True)
for i in range(18): tick(b(16.2)+i*(b(18.6)-b(16.2)-0.25)/18, 1500+rng.random()*500, 0.05, 0.05)
pop(b(18.6),True,0.2); pop(b(20),False,0.18)
n=int(1.2*SR); tt=np.arange(n)/SR; chime=(np.sin(2*np.pi*f(81)*tt)+0.6*np.sin(2*np.pi*f(86)*tt))*np.exp(-tt*3.2)*0.07; put(L,chime,b(21)); put(R,chime,b(21))
whoosh(b(25.5)-0.1)
for i in range(8): tick(b(27.4)+i*0.9/8, 1600, 0.05, 0.05)
put(L,chime,b(31.4),0.9); put(R,chime,b(31.4),0.9)
# queda na frase "E a conversa acabou." (compassos ficam mais vazios entre os tempos 12 e 15,5)
duck=np.ones(N); i0,i1=int(b(12)*SR),int(b(15.5)*SR); duck[i0:i1]=0.55; duck=np.convolve(duck,np.ones(4000)/4000,'same')
L*=duck; R*=duck
fade=np.ones(N); nf=int(1.4*SR); fade[-nf:]=np.linspace(1,0.0,nf)**1.5; fade[:int(0.02*SR)]=np.linspace(0,1,int(0.02*SR))
S=np.stack([L*fade,R*fade],1); S=np.tanh(S*1.6)/1.6; S/=np.abs(S).max()/0.7
w=wave.open('mix.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((S*32767).astype(np.int16).tobytes()); w.close(); print('ok',round(DUR,3))
