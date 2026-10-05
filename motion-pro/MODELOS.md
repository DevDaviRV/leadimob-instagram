# Modelos aprovados pelo Davi (ponto de partida obrigatório)

Toda peça nova **parte do código de um modelo aprovado**, não de uma página em branco. Abra a pasta de trabalho com
`motion-pro/novo_trabalho.sh <modelo> <nome>` (cria `work/<nome>/` com fontes, three, motion, logo e ativos já ligados), sirva a raiz por HTTP
(`python3 -m http.server 8126`) e abra `http://localhost:8126/work/<nome>/index.html`. Conferido em 03/10: os quatro modelos abrem e renderizam a partir deste repositório, e o carrossel modelo sai idêntico, pixel a pixel, ao aprovado.

| Peça | Modelo (`novo_trabalho.sh`) | Peça aprovada | Fontes | O que o Davi disse |
|---|---|---|---|---|
| Reel 2 tipográfico | `reel-tipografico` | `instagram/2026-10-03/r2-lead-curioso.mp4` | `instagram/2026-10-03/src/r2-index.html`, `r2-trilha.py` | "design muito bom, padrão da marca, sem exageros de cores ou efeitos" |
| Reel 1 narrado | `reel-narrado` | `instagram/2026-10-06/r1-voce-nao-precisa-de-mais-leads.mp4` (v1) | `motion-pro/v1-plataforma/` (index.html com `__TIMELINE__`, script.py, gaps.json, timeline.json, trilha.py) | "o primeiro reels de todos ficou ótimo e ele é a qualidade mínima" |
| Carrossel | `carrossel` | `instagram/2026-10-04/carrossel/` ("7 lugares onde seus leads morrem") | `instagram/2026-10-02/src/c1-index.html` | "ficou animal, daí para cima" |
| Carrossel (variação) | `carrossel-b` | `instagram/2026-10-03/carrossel/` ("Mande 3 imóveis. Não 20.") | `instagram/2026-10-03/src/c1-index.html`, `c1-shoot.js`, `c1-slides.json` | aprovado em 02/10 |

Contraexemplo (não usar como base): `instagram/2026-10-03/r1-nao-precisa-de-mais-trafego.mp4` — exagerado em efeitos.

## Como usar o modelo sem copiar a peça
- **Mantém do modelo:** sistema visual (fundo, grade/poeira discreta, tipografia Inter 800 em caixa alta com tracking negativo, cartões e bolhas de UI, logo em cartão claro, linha da jornada), o motor (`window.render(t)` determinístico, springs, câmera contida), a estrutura do arquivo, o nível de acabamento e a mixagem da trilha.
- **Muda a cada peça:** texto, roteiro, artefatos de produto de cada cena/slide, ordem e tipo das transições, andamento/tonalidade/arranjo da trilha, composição dos planos. Não entregue a mesma peça com texto trocado.
- **Reel narrado:** escreva `script.py`, gere/pegue o mp3, rode `sync_voice.py` + `word_align.py` na pasta de trabalho, depois `python3 ../../motion-pro/engine/build.py` (gera `build.html`) e revise com `sheet.js`/`shot2.js`. O v1 tem 51s; os reels diários ficam em 30–40s.
- **Reel tipográfico:** os tempos ficam no próprio `index.html`; a trilha é `trilha.py`.
- **Carrossel:** uma faixa contínua de 10 × 1080 px. `node shoot.js http://localhost:8126/work/<nome>/index.html png` recorta os 10 PNG e audita fonte mínima e margens. O primeiro carrossel tem textos de apoio de 24px: é o modelo de visual, mas nas peças novas vale a regra de **≥ 30px** (o `carrossel-b` já cumpre).
- **Editor do carrossel:** `python3 motion-pro/carrossel/make_editor.py slides.json <pasta>/carrossel/carrossel-editor.html` (não depende da skill carrossel-pro estar instalada; formato do `slides.json` em `instagram/2026-10-03/src/c1-slides.json`).
- **Ao terminar:** copie as fontes da pasta de trabalho para `instagram/AAAA-MM-DD/src/` com os prefixos `r1-`, `r2-`, `c1-`. `work/` não vai para o git.

## Estrutura própria (correção de 03/10)
O modelo é o ponto de partida do código, não o roteiro visual. O Reel 2 de 05/10 repetiu o de 03/10 cena por cena, só com o texto trocado, e isso não serve: mude a sequência de cenas, o elemento central de cada cena, a composição e ao menos duas transições. O que se mantém é o sistema visual, o motor e o nível de acabamento.

## Teste de fidelidade (antes do render final)
Monte uma folha de contato da peça nova ao lado de quadros da peça aprovada do mesmo tipo e peça ao subagente crítico a nota de "fidelidade ao modelo aprovado" (mesma família visual, mesmo nível de acabamento, sem efeitos a mais). Meta ≥ 8, junto com os demais critérios e com "estrutura própria" (ao lado do modelo, a peça nova não pode parecer a mesma com outro texto).
