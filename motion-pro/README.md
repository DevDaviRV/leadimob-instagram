# Motion Kit Pro — motor de vídeo motion premium (render programático)

Motor usado para produzir Reels/vídeos institucionais premium com Claude: animação 100% em código (HTML/SVG/Canvas/three.js), render quadro a quadro determinístico, motion blur, sincronia com locução real palavra a palavra, trilha e SFX sintetizados e mixagem final. Tudo roda dentro do ambiente do Claude (Linux em nuvem, sem GPU).

> Os arquivos em `exemplos/` são de outra marca (Domyni). Use **só como referência de técnica e de código** — nunca copie cores, textos, logo ou estrutura de cenas para a nova empresa.

## Estrutura
| Pasta/arquivo | Função |
|---|---|
| `engine/render2.js` | `node render2.js <url> <fps> <sub> <quadro_ini> <quadro_fim> saida.mp4` — Chromium headless (WebGL via SwiftShader), chama `window.render(t)` por quadro, envia PNG ao ffmpeg. `sub>1` = motion blur por subquadros (média com `tmix`). |
| `engine/shot2.js` | `node shot2.js <url> t1 t2 …` — stills em tempos específicos → `chk/s_<t>.png`. |
| `engine/sheet.js` | `node sheet.js <url> 0.5` — um still a cada 0,5s (JPEG) → folha de contato para revisão/crítica **sem** renderizar vídeo (~2 min). |
| `engine/build.py` | Injeta `timeline.json` no `index.html` (placeholder `__TIMELINE__`) → `build.html`. |
| `audio/estimate_timeline.py` | Sem voz ainda: estima tempos das frases pelo ritmo da voz (parâmetro `CPS` = caracteres/segundo; recalibre para a voz da nova marca). Lê `script.py`. |
| `audio/sync_voice.py` | Voz real chegou: detecta pausas, alinha frase a frase por programação dinâmica, ancora seções (`gaps.json` = pausa antes de cada seção), corta `vo_b/pNN.wav` e grava `timeline.json`. |
| `audio/word_align.py` | Depois do sync: tempo de cada palavra pela energia da voz (picos silábicos) → `words` no `timeline.json` (legendas/tipografia palavra a palavra). |
| `audio/trilha_exemplo.py` | Exemplo de trilha sintetizada (numpy/scipy): pad, baixo, kick com sidechain, hats, arpejo com delay, risers, impactos, ticks, chimes, ducking sob a voz, `mix_vo.wav` e `mix_novo.wav`. **Adapte** (índices de cues são do exemplo). |
| `exemplos/*.html` | Três motores completos de referência: teaser 3D, Reels 3D com câmera viajando por "estações", institucional com partículas, escada 3D e objetos SVG por etapa. |

## Setup (ambiente novo, efêmero)
```bash
npm i playwright three motion @fontsource/<fonte-da-marca> ...   # Google Fonts NÃO é acessível; use @fontsource via npm
pip install --break-system-packages numpy scipy pillow
# Chromium já vem em /opt/pw-browsers/chromium (não rodar "playwright install")
mkdir -p chk out; python3 -m http.server 8125 &   # módulos ES/importmap não carregam via file:// — servir por HTTP (o servidor pode morrer entre turnos: reinicie)
```
Importmap do three: `{"imports":{"three":"./node_modules/three/build/three.module.js"}}`. Motion: `<script src="node_modules/motion/dist/motion.js">` → `window.Motion.spring`.

## Contrato do motor (obrigatório)
- A página expõe `window.render(t)` **determinística** (mesmo `t` → mesmo quadro) e `window.ready` (Promise). Nada de requestAnimationFrame, CSS transitions ou `Math.random()` sem seed.
- Todos os tempos derivam da timeline de voz: `C[i].start/end` por frase e `C[i].words[j].t` por palavra. Nada de números soltos.
- Springs: `const s=Motion.spring({keyframes:[0,1],stiffness:190,damping:17}); v=s.next(ms).value` (amostrado por tempo).
- Fontes: `await document.fonts.load('700 20px NomeFonte')` antes de desenhar texto em canvas/texturas.
- DOM ancorado em objeto 3D: `cam.updateMatrixWorld(); v=obj.position.clone().project(cam)` → pixels.

## Fluxo de render e entrega
1. Rascunho: `sheet.js` (stills) → revisar → crítica independente → corrigir.
2. Final: 2 processos em paralelo (2 CPUs): `render2.js url 30 3 0 N/2 a.mp4` e `N/2 N b.mp4`; `concat` (`-c copy`).
   Custo ~0,3–0,6 s por subquadro. 40s com sub=3 ≈ 35 min; 90s ≈ 70 min. Rode em background (`nohup … &`) e acompanhe o log.
   Se precisar parar: `pkill -f "node render2.js"` finaliza o mp4 corretamente; conte quadros com `ffprobe -count_frames` e retome do quadro seguinte.
3. Áudio: trilha → `loudnorm=I=-14:TP=-1.5:LRA=9` → mux.
4. Grão SEMPRE no ffmpeg (`noise=alls=2..4:allf=t`), nunca na página.
5. Limite de envio ao usuário ≈ 30 MB: até ~45s use `-crf 20 -preset slow -maxrate 16M -bufsize 32M`; acima disso, 2-pass com bitrate alvo (ex.: 91s → `-b:v 2350k`, áudio 192k) e grão leve.

## Armadilhas já descobertas (não repetir)
- `filter: blur()` CSS sobre o canvas WebGL deixa o quadro 3–6× mais lento no SwiftShader → use overlay escuro ou desfoque no ffmpeg.
- Ruído/grão desenhado na página deixa o PNG pesado e o render 3× mais lento.
- Máscara de texto (palavra sobe de dentro de `overflow:hidden`): esconder com `translateY ≥ 130%`; com ~108% a ponta de ascendentes vaza e vira um ponto na tela.
- Vertical 9:16 com fov 38°: largura visível = 0,387 × distância; altura = 0,689 × distância. O conteúdo 3D precisa caber em ~45% da altura (entre título e legenda).
- Texto importante sempre em DOM (≥ 36px). Texto dentro de textura 3D fica ilegível no celular.
- Área segura Reels: texto essencial entre y≈200 e y≈1520 (de 1920), margens laterais ≥ 72px, fora da faixa direita dos botões.
- A API da ElevenLabs (e a maioria dos sites) é bloqueada pelo proxy deste ambiente: o usuário gera a voz e envia o arquivo.
