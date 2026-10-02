# Leadimob Motion — Registro de evolução

Regra: **cada vídeo supera o anterior.** Ler antes de criar; atualizar ao entregar. Nunca repetir a mesma estrutura de cenas, transições ou trilha do vídeo anterior. Cada vídeo estreia ≥ 3 técnicas novas.

## Nível de partida (herdado do motor)
O motor já entregou, em outra marca: plano contínuo 3D com câmera viajando por estações; painéis 3D com texturas canvas; callouts DOM ancorados no 3D; tipografia cinética com springs; legenda palavra a palavra sincronizada pela energia da voz; partículas que se reorganizam (caos → estrutura); objeto SVG próprio por ideia com animações declarativas; transição com forma proprietária da marca; janela recortada com foto em Ken Burns; campo de comentário digitando o CTA; motion blur por subquadros; trilha sintetizada com arranjo que cresce por seção, sidechain, risers e impactos no drop. **Esse é o piso, não o teto.**

## Backlog de técnicas
- Câmera: dolly/crane contínuo, parallax, órbita, match cuts (forma final de uma cena = primeira da próxima).
- Tipografia: palavra a palavra na voz, palavra-chave em destaque, recortes tipográficos, texto gigante cruzando a tela.
- Transições variadas: forma da marca, máscara tipográfica, zoom-through, split screen, morph de linha, corte seco no beat.
- 3D: extrusões, instâncias (InstancedMesh), shaders simples, luz/sombra fake, profundidade com fog.
- Imagem real: fotos/vídeos do cliente com parallax 2.5D, recorte de sujeito, grade de cor da marca.
- Acabamento: 60 fps em trechos rápidos, motion blur, grão fino, vinheta, respiração de elementos ociosos.
- Som: cortes no grid da trilha, risers antes das viradas, sub-drops nas revelações, foley de interface, trilha licenciada do cliente quando houver.
- Retenção: texto + movimento no quadro 0, promessa do vídeo escrita na tela, troca de plano a cada 2–4s, nada parado > 1,5s, CTA junto com a palavra falada.

## Aprendizados
### v1 — "Você não precisa de mais leads" (30/09/2026)
- Funcionou: gancho contraintuitivo com tachado âmbar em "MAIS LEADS"; chuva de pills "Novo lead" que ficam cinzas/"sem resposta" em "perder"; relógio 23:48 → 07:31 com badge de tempo sem resposta; wipe com o símbolo do logo (barra + triângulos) na virada para o produto; mundo 3D contínuo com a linha da jornada do lead e estações com anel no chão; cards DOM ancorados por projeção 3D (texto nítido + parallax real); crane final mostrando a jornada inteira com rótulos.
- Crítica rodada 1 → 2: hook 6→7, dinamismo 6→7, clareza 7→8, acabamento 6→7, legibilidade 5→6, marca 8→8.
- Correções que viraram regra: cards de estação entram junto com a câmera (sem quadros vazios); título da estação troca antes do card; faixa escura atrás das legendas; nada encostado na borda direita (clamp de rótulos, órbita menor); máscaras de palavra com translateY 145% (125% deixava traço); âmbar só para alerta; card do site recua quando a mensagem aparece (sem sobreposição).
- QA do render final pegou bolha de fotos vazia por ~0,5s (fotos entravam só na palavra "fotos"); corrigido re-renderizando só o trecho (quadros 685–745) e emendando — técnica de re-render parcial vale para ajustes pontuais.
- Ainda abaixo do ideal: legibilidade do texto dentro dos mockups (Kanban ~30px, rótulos do nav 20px); produto aparece só aos ~11,7s (preso ao roteiro); ritmo das 6 estações ainda regular (~3,3s cada).

### Reel 02/10 R1 — "O cliente não quer receber mais imóveis" (01/10/2026)
- Funcionou: gancho com parede de 20 cards caindo e título palavra a palavra na voz; celular com contador "N imóveis enviados" subindo junto com pops acelerando na trilha; queda da trilha em "adia" com a pill âmbar "Conversa parada"; 4 cards de pergunta que chegam um a um, revelam o texto em "quatro" e acendem na palavra falada (cada pergunta = uma nota subindo); perfil pronto para o corretor como fecho do produto.
- Crítica independente no primeiro corte: gancho 7,5 · ritmo 6,5 · clareza 8 · acabamento 6 · legibilidade 7 · marca 9. Re-renderizado com as correções abaixo.
- Correções que viraram regra: (1) transição entre cenas DOM = a cena antiga termina de sair antes de a nova começar a entrar (nada de crossfade com dois textos legíveis); (2) painéis escuros (chat) entram em fade junto com o título, nunca opacos de uma vez; (3) nenhum bloco fica parado esperando a fala: os elementos chegam escalonados durante a frase e o conteúdo só é revelado na palavra; (4) fim do vídeo = fim da fala + 1,5s, com push-in lento e reveals presos às palavras; (5) legenda de 2 linhas termina em y ≤ 1520 (topo em 1398 com fonte 50px); (6) título do gancho sobre fundo limpo: cards atrás do texto a 28% e sombra radial forte; (7) todo texto que carrega a mensagem (chips, subtítulos de card, rótulos) ≥ 36px, só horário/status de interface pode ser menor; (8) pill de desfecho precisa de ≥ 0,8s legível antes do corte.
- Áudio: `alimiter` precisa de `level=0` (o padrão renormaliza e leva o pico a 0 dB); cadeia final `loudnorm=I=-14:TP=-2:LRA=9,alimiter=limit=0.8:level=0`.
- Render: cenas DOM com gradientes radiais grandes e 20 cards em 3D custaram ~5s por quadro com sub=3 em 2 processos (~50 min para 41s). Planejar o tempo, ou trocar os glows por imagem pré-renderizada.
- O ambiente de nuvem pode reiniciar no meio de um render longo e o mp4 parcial fica inutilizável: renderizar sempre em blocos de 80 quadros que retomam de onde pararam (`motion-pro/engine/render_blocos.sh`, 2 processos) e juntar com `concat`.
- Corte final conferido quadro a quadro nas 6 transições: sem texto sobreposto. Áudio final -14,3 LUFS, pico -2,0 dB.
- Narração: gerada pela API da ElevenLabs (conta paga), 7 mp3 da semana em `instagram/narracoes/`.
- Ainda abaixo do ideal: motion blur com sub=3 aparece como cópias empilhadas em movimentos muito rápidos (feed do celular); contador ainda está em 3 quando a voz diz "vinte"; quadro 0 mostra só "O CLIENTE" (escolher a capa em ~2,6s).

### Posts de 03/10 — primeiro lote depois do pedido "nível de estúdio" (01–02/10/2026)
Davi (01/10): o Reel 1 de 02/10 (DOM plano) ficou "um pouco inferior"; o vídeo de apresentação (v1) é a qualidade mínima. Durante a produção ele viu a prévia e achou exagerados os funis âmbar dos vazamentos: "devem sempre seguir a marca". Viraram regra no ACERTOS.

**Reel 1 "Você não precisa de mais tráfego" (35s, 3D)**
- Técnicas novas: metáfora única em mundo 3D (pista de luz com ~1.100 orbes em shader de pontos, portal com a foto do anúncio, três vazamentos onde os leads caem); cada orbe tem "destino" determinístico; orçamento que dobra o fluxo e os vazamentos junto; orbe-herói "Você · cliente" com câmera de perseguição presa a ele e bloco de anotações preenchido a cada vazamento; CTA com sete marcadores projetados na pista; títulos no topo como legenda (sem legenda no rodapé); câmera por spline cúbica monotônica (não para em cada keyframe); cards DOM ancorados com trava nas margens.
- Crítica do rascunho: 6 / 6,5 / 6,5 / 5 / 7 / 7,5 (gancho, ritmo, clareza, acabamento, legibilidade, marca). Crítica do primeiro corte final: 7 / 8,5 / 8 / 6,5 / 7,5 / 8. Corrigido depois disso e re-renderizado; o corte entregue não passou por nova rodada de notas.
- Correções que viraram regra: vazamento/dor = buraco escuro + anel fino + só os leads em âmbar (nada de cones, feixes ou halos chapados); fios de luz de 1px parecem defeito de render; título nunca sobre o card (no gancho, título em cima e portal embaixo); contador precisa assentar e segurar o valor final ≥ 0,4s; etiquetas no plano aberto ancoradas no próprio anel, à esquerda, ≥ 36px; cards não chegam vazios; a câmera de perseguição é função direta do objeto seguido; marcadores do CTA todos acima de y=1520; pílulas de estado neutras quando já há âmbar demais na cena.
- Motion blur: 3 subquadros em obturador de 360° deixavam orbes e etiquetas como 3–4 cópias. `render2.js` agora usa obturador de 180° (SHUTTER=0.5) e o padrão passou a 4 subquadros.

**Reel 2 "Esse lead 'curioso' pode ser uma venda" (23s, tipográfico em 3D)**
- Técnicas novas: tipografia DOM projetada pela câmera do three (matrix3d) com profundidade real; zoom-through pelo furo da etiqueta; wipe com o símbolo do logo; match cut dos chips para a etiqueta; flip da etiqueta CURIOSO → QUENTE (verde); tipografia fantasma e chão em perspectiva preenchendo a metade de baixo; trilha 100 BPM em Lá bemol com silêncio no "E só.".
- Crítica do corte: 8 / 6 / 6 / 6,5 / 8 / 8. Corrigido (tempo de leitura ≥ 1,5s das frases-tese, pill limpo, lista completa ≥ 1,2s, fecho ≥ 1,5s sem fade, etiqueta verde, 180° de obturador) e re-renderizado; não re-pontuado.
- Regras: toda frase fica completa e parada pelo menos ~0,3s por palavra (mínimo 1,5s para a tese); composição centrada (bloco entre ~y 380 e 1380), nunca só na metade de cima; "quente"/resultado é verde, não azul; vídeo termina em quadro cheio (bom para loop).

**Carrossel "Mande 3 imóveis. Não 20."**
- Elemento contínuo novo: fluxo de cards de imóvel que afunila ao longo do swipe (pilha caótica → enxurrada âmbar → quatro portões das perguntas → funil → 3 escolhidas num trilho). Miniaturas procedurais em SVG, perspectiva individual por card, mensagem pronta para copiar no slide 8.
- Só autoavaliado por quem produziu (sem crítica independente). Ponto fraco: slides 5–10 repetem a mesma faixa inferior.

- Ainda abaixo do ideal no lote: restam fantasmas leves no mergulho do Reel 2; microtextos de interface entre 28 e 34px; nenhum dos três teve nota final depois das últimas correções; a trilha é medida (-14 LUFS) mas nunca ouvida por quem produz.

## Backlog para o v2
- Abrir com o produto já no quadro 0 (gancho em cima do celular), roteiro com problema em ≤ 6s.
- Zoom de câmera no elemento principal de cada estação (1 elemento herói ≥ 85% da largura, texto ≥ 36px).
- Durações variadas por estação e ao menos uma transição de match cut (forma final de uma cena = primeira da próxima).
- Trilha: experimentar tonalidade maior/brilhante e drop mais forte no wipe; foley de teclado real.
- Testar formato 4:5 para feed.

## Histórico
| Versão | Vídeo | Novidades | Nota da crítica | A superar no próximo |
|---|---|---|---|---|
| v1 | Plataforma: "Você não precisa de mais leads" (9:16, 51s) | mundo 3D contínuo + linha da jornada, cards DOM ancorados em 3D, wipe do símbolo, relógio time-lapse, crane final, trilha 118 BPM F#m com SFX por ação | 7/7/8/7/6/8 | legibilidade de mockups, produto antes de 6s, ritmo das estações |
| R1 02/10 | "O cliente não quer receber mais imóveis" (9:16, 41s) | parede de cards 3D no gancho, contador + pops acelerando, cards de pergunta acesos pela voz, trilha 104 BPM Ré menor com queda no "adia" | 7,5/6,5/8/6/7/9 no primeiro corte (corrigido e re-renderizado) | motion blur em movimento rápido, capa no quadro 0, custo de render |

| R1 03/10 | "Você não precisa de mais tráfego" (9:16, 35s, 3D) | pista de orbes com vazamentos, orbe-herói com câmera de perseguição, spline de câmera, obturador 180° | 7/8,5/8/6,5/7,5/8 no 1º corte (corrigido, não re-pontuado) | blur perfeito em objetos rápidos, microtextos ≥ 36px |
| R2 03/10 | "Esse lead curioso pode ser uma venda" (9:16, 23s, tipográfico 3D) | tipografia projetada por matrix3d, zoom-through, wipe do símbolo, match cut | 8/6/6/6,5/8/8 no 1º corte (corrigido, não re-pontuado) | fantasmas no mergulho, quadros de viagem vazios |
