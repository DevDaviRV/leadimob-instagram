"""Sincroniza uma locução real (ElevenLabs etc.) com o roteiro.
Uso: python3 sync_voice.py voz.mp3 [gap_entre_secoes=1.0]
Opcional: gaps.json = {"1":1.3,"2":0.95,...} pausa antes de cada seção (índice da seção, 0 = primeira).
A primeira seção começa no alvo do script; as demais começam logo após a anterior + gap (ritmo real da voz).
Entrada: timeline_guide.json (voz-guia: i,start,end,text,sec)
Saída: timeline.json re-sincronizado + vo_b/pNN.wav (uma frase por arquivo)
Método: detecta pausas (silencedetect) e escolhe, por programação dinâmica,
as fronteiras de frase que melhor batem com as durações relativas da voz-guia.
Pausas entre frases da mesma seção são preservadas; seções são ancoradas nos
tempos-alvo (targets) com gap mínimo para as transições."""
import json, math, subprocess, sys, re, os
voice = sys.argv[1]; GAP = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
GAPS = json.load(open('gaps.json')) if os.path.exists('gaps.json') else {}
tl = json.load(open('timeline_guide.json'))
exp = [c['end']-c['start'] for c in tl]
log = subprocess.run(['ffmpeg','-v','info','-i',voice,'-af','silencedetect=noise=-38dB:d=0.09','-f','null','-'],capture_output=True,text=True).stderr
starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',voice]))
if len(ends) < len(starts): ends.append(dur)
sil = [(s, e, e-s) for s, e in zip(starts, ends)]
speech_start = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
tail = [s for s, e, d in sil if e >= dur-0.05]
total = tail[0] if tail else dur
cands = [(s, e, d) for s, e, d in sil if s > 0.05 and e < total-0.05]
m, n = len(cands), len(exp)
scale = sum(exp)/((total-speech_start)-sum(d for s, e, d in cands if d > 0.22))
def seglen(a, b):
    st = speech_start if a < 0 else cands[a][1]; en = total if b >= m else cands[b][0]; return en-st
INF = 1e9
def cost(k, a, b):
    L = seglen(a, b)
    if L <= 0.2: return INF
    c = (math.log(L*scale/exp[k]))**2*4
    if b < m: c -= min(cands[b][2], 0.6)*3
    for j in range(a+1, b): c += max(0, cands[j][2]-0.2)*6
    return c
dp = [[INF]*(m+1) for _ in range(n)]; bk = [[None]*(m+1) for _ in range(n)]
for b in range(m): dp[0][b] = cost(0, -1, b)
for k in range(1, n):
    for b in range(m+1):
        if (k == n-1) != (b == m): continue
        for a in range(b):
            if dp[k-1][a] < INF:
                v = dp[k-1][a]+cost(k, a, b)
                if v < dp[k][b]: dp[k][b] = v; bk[k][b] = a
b = m; bounds = []
for k in range(n-1, 0, -1):
    a = bk[k][b]; bounds.append(a); b = a
bounds = bounds[::-1]; segs = []; prev = -1
for bi in bounds+[m]:
    st = speech_start if prev < 0 else cands[prev][1]; en = total if bi >= m else cands[bi][0]
    segs.append((st, en)); prev = bi
# ancoragem por seção
secs = []; cur = None
for k, c in enumerate(tl):
    if c['sec'] != cur: secs.append([]); cur = c['sec']
    secs[-1].append(k)
targets = [tl[ks[0]]['sec'] for ks in secs]
os.makedirs('vo_b', exist_ok=True); new = []; prev_end = 0
for si, ks in enumerate(secs):
    b0 = segs[ks[0]][0]; start = targets[0] if si == 0 else prev_end + float(GAPS.get(str(si), GAP)); off = start-b0
    for k in ks:
        s, e = segs[k]
        new.append(dict(i=k+1, start=round(s+off-0.03, 3), end=round(e+off, 3), text=tl[k]['text'], sec=tl[k]['sec'], src=[s, e]))
    prev_end = new[-1]['end']
for c in new:
    s, e = c['src']
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(max(0, s-0.03)),'-to',str(e+0.12),'-i',voice,'-af',
      'afade=t=in:d=0.02,areverse,afade=t=in:d=0.06,areverse,highpass=f=70,acompressor=threshold=-22dB:ratio=2.2:attack=8:release=120:makeup=1.5',
      '-ar','48000','-ac','1',f"vo_b/p{c['i']:02d}.wav"], check=True)
json.dump(new, open('timeline.json','w'), ensure_ascii=False)
for c in new: print(f"{c['i']:2} {c['start']:6.2f} {c['end']:6.2f} {c['text']}")
print('END', round(new[-1]['end']+2.3, 2))
