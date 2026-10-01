"""Timeline estimada SEM gerar voz (substitui tts.py).
Calibrado na voz Bianca (ElevenLabs, Multilingual v2, speed 1.0): ~14,5 caracteres/s, pausa média entre frases ~0,32s.
Uso: python3 estimate_timeline.py   (lê script.py: SECTIONS = [(alvo_s, [(legenda, texto_tts|None), ...]), ...])
Saída: timeline.json e timeline_guide.json (mesmo formato do sync_voice.py: i, start, end, text, sec).
Quando o áudio real chegar: python3 sync_voice.py voz.mp3 <gap> substitui os tempos pelos reais."""
import json
from script import SECTIONS
CPS = 14.5      # caracteres por segundo da voz (14,5 = voz "Bianca" ElevenLabs; recalibre com o primeiro áudio da nova marca)
GAP = 0.32      # pausa entre frases da mesma seção
SEC_GAP = 1.0   # pausa mínima entre seções (transições de câmera)
tl = []; i = 0; t = 0
for si, (target, cues) in enumerate(SECTIONS):
    t = target if si == 0 else max(target, t - GAP + SEC_GAP)
    for cap, tts in cues:
        i += 1; d = len(tts or cap) / CPS + 0.15
        tl.append(dict(i=i, start=round(t, 2), end=round(t + d, 2), text=cap, sec=target))
        t += d + GAP
json.dump(tl, open('timeline.json', 'w'), ensure_ascii=False)
json.dump(tl, open('timeline_guide.json', 'w'), ensure_ascii=False)
for c in tl: print(c['i'], c['start'], c['end'], c['text'])
print('END ~', round(tl[-1]['end'] + 3.3, 1))
