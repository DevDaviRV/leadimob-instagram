"""Alinhamento palavra a palavra pela energia da voz (núcleos silábicos).
Para cada frase (vo_b/pNN.wav), detecta picos de energia na banda da voz (~núcleos vocálicos),
estima sílabas por palavra e mapeia o início de cada palavra para o pico correspondente.
Grava 'words' em timeline.json: [{w, t}]."""
import json, re, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, find_peaks
tl = json.load(open('timeline.json'))
V = re.compile(r'[aeiouáéíóúâêôãõàü]+', re.I)
def syl(w):
    n = len(V.findall(w))
    return max(1, n)
for c in tl:
    sr, x = wavfile.read(f"vo_b/p{c['i']:02d}.wav"); x = x.astype(np.float64)
    if x.ndim > 1: x = x.mean(1)
    x = sosfilt(butter(4, [250, 3000], 'band', fs=sr, output='sos'), x)
    hop = int(sr*0.005); win = int(sr*0.025)
    env = np.array([np.sqrt(np.mean(x[i:i+win]**2)) for i in range(0, len(x)-win, hop)])
    env = np.convolve(env, np.ones(5)/5, 'same'); env /= env.max()+1e-9
    pk, pr = find_peaks(env, distance=int(0.085/0.005), prominence=0.06, height=0.12)
    pt = pk*0.005 + c['start']        # file starts at c['start'] (sync_voice pads -0.03)
    ws = c['text'].split(' '); sy = [syl(w) for w in ws]; S = sum(sy)
    out = []; k = 0
    for w, s in zip(ws, sy):
        if len(pt) >= 2:
            j = int(round(k * (len(pt)-1) / max(1, S-1))) if S > 1 else 0
            t = pt[min(j, len(pt)-1)] - 0.07
        else:
            t = c['start'] + (k/S)*(c['end']-c['start'])
        out.append({'w': w, 't': round(max(c['start'], t), 3)}); k += s
    # monotonic
    for i in range(1, len(out)): out[i]['t'] = max(out[i]['t'], out[i-1]['t']+0.06)
    c['words'] = out
json.dump(tl, open('timeline.json', 'w'), ensure_ascii=False)
for c in tl[:4]: print(c['i'], [(o['w'], o['t']) for o in c['words']])
