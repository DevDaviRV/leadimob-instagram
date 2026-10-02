# Leadimob Motion — ACERTOS (regras permanentes aprendidas)

## Manter
- Davi aprova o roteiro; em seguida recebe a narração em bloco pronto para ElevenLabs e gera o áudio ele mesmo.
- Produção 100% em código (three.js, DOM, canvas, ffmpeg, numpy). Sem geradores de terceiros.
- LID sempre secundário (fecho, discreto).
- Logo oficial sobre cartão claro no fundo dark.

- Fluxo aprovado pelo Davi (30/09/2026): questionário → roteiro com tabela → narração em bloco → ele gera na ElevenLabs e envia o mp3 → sync_voice + word_align.
- Voz Bianca lê ~15 caracteres/s; com gaps de 0,7s o roteiro de 15 frases deu ~51s. Para 40–45s, cortar 2–3 frases.

## Padrão mínimo de carrossel (aprovado pelo Davi em 01/10: "ficou animal, daí para cima")
Referência: `instagram/2026-10-02/carrossel/` (fontes em `src/c1-index.html`). Todo carrossel novo parte deste nível e sobe:
- Faixa contínua de 10 × 1080 px renderizada de uma vez: elementos atravessam os slides (linha da jornada com glow e pontos por slide), o swipe tem continuidade.
- Um artefato visual de produto por slide (bolha de WhatsApp, chips de pergunta, 20 → 3 cards, agenda, ficha de CRM, régua de follow-up, KPIs), nunca só texto.
- Número fantasma em contorno ao fundo, selo numerado ciano + kicker em caixa alta, título 76–128px com destaque ciano, apoio ≥ 38px.
- Conteúdo centralizado verticalmente acima da linha; rodapé com @leadimob.ai e n/10; capa com "salve este post" e CTA final com campo de comentário DIAGNÓSTICO + logo em cartão claro.
- Âmbar só nos pontos de dor; verde para a solução.

## Padrão mínimo de reel (Davi, 01/10: "o primeiro reel ficou ótimo e ele é a qualidade mínima")
Referência: `motion-pro/v1-plataforma/` (vídeo de apresentação). O Reel 1 de 02/10, feito só com cenas DOM planas trocadas por fade, foi sentido como inferior ("satisfatório, mas buscamos a maior qualidade"). Todo reel narrado parte do nível do v1 e sobe:
- Mundo 3D contínuo em three.js com câmera viajando (dolly, crane, órbita), profundidade real, fog, luz e reflexo; nunca uma sequência de telas planas com fade.
- Elemento proprietário atravessando o vídeo (linha de luz da jornada do lead, estações, símbolo do logo como wipe ou máscara).
- UI de produto em DOM nítido ancorado por projeção 3D (parallax real), com 1 elemento herói por plano.
- Transições desenhadas (match cut, wipe do símbolo, zoom-through), nunca só opacidade.
- Acabamento de estúdio: partículas, glow, sombras de contato, motion blur, grão, vinheta, trilha com arco e SFX por ação.
- O Reel 2 tipográfico também precisa de profundidade e câmera (tipografia cinética em 3D ou camadas com parallax), não só texto trocando.

## Nunca repetir
- Frame 0 com uma palavra só: abrir com pelo menos 2 palavras e movimento.
- Quadros vazios entre estações (card só entrando depois da câmera chegar).
- Texto de interface < 28px em mockup (ilegível no celular).
- Elementos a menos de 72px da borda direita (botões do Reels).
