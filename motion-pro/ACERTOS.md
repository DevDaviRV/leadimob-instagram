# Leadimob Motion — ACERTOS (regras permanentes aprendidas)

## Manter
- Davi aprova o roteiro; em seguida recebe a narração em bloco pronto para ElevenLabs e gera o áudio ele mesmo.
- Produção 100% em código (three.js, DOM, canvas, ffmpeg, numpy). Sem geradores de terceiros.
- LID sempre secundário (fecho, discreto).
- Logo oficial sobre cartão claro no fundo dark.

- Fluxo aprovado pelo Davi (30/09/2026): questionário → roteiro com tabela → narração em bloco → ele gera na ElevenLabs e envia o mp3 → sync_voice + word_align.
- Voz Bianca lê ~15 caracteres/s; com gaps de 0,7s o roteiro de 15 frases deu ~51s. Para 40–45s, cortar 2–3 frases.

## Padrão mínimo de carrossel (aprovado pelo Davi em 01/10: "ficou animal, daí para cima")
Referência: `instagram/2026-10-04/carrossel/` (produzido para 02/10; fontes em `instagram/2026-10-02/src/c1-index.html`; modelo `carrossel` em `motion-pro/MODELOS.md`). Todo carrossel novo parte deste nível e sobe:
- Faixa contínua de 10 × 1080 px renderizada de uma vez: elementos atravessam os slides (linha da jornada com glow e pontos por slide), o swipe tem continuidade.
- Um artefato visual de produto por slide (bolha de WhatsApp, chips de pergunta, 20 → 3 cards, agenda, ficha de CRM, régua de follow-up, KPIs), nunca só texto.
- Número fantasma em contorno ao fundo, selo numerado ciano + kicker em caixa alta, título 76–128px com destaque ciano, apoio ≥ 38px.
- Conteúdo centralizado verticalmente acima da linha; rodapé com @leadimob.ai e n/10; capa com "salve este post" e CTA final com campo de comentário DIAGNÓSTICO + logo em cartão claro.
- Âmbar só nos pontos de dor; verde para a solução.

## Direção de arte dos reels: premium, sóbrio, corporativo (Davi, 02/10)
Palavras dele: o `r2-lead-curioso` (03/10) "tem o design muito bom, padrão da marca, sem exageros de cores ou efeitos"; o `r1-nao-precisa-de-mais-trafego` (03/10) "ficou exagerado nos efeitos. Gosto de efeitos bonitos e profissionais, mas sem exagero visual". Pediu visual "mais adequado, corporativo e bonito" e mandou seguir esse padrão nos próximos.
- **Referência a seguir:** `instagram/2026-10-03/r2-lead-curioso.mp4` (fontes em `src/r2-*`) e o vídeo de apresentação `motion-pro/v1-plataforma/`. **Contraexemplo:** `instagram/2026-10-03/r1-nao-precisa-de-mais-trafego.mp4` (nuvem de orbes brilhantes, portal, halos, muita coisa acesa ao mesmo tempo).
- Fundo escuro limpo com muito respiro; tipografia grande e bem composta como protagonista; UI de produto nítida (bolhas, cards, etiquetas) como apoio; UMA cor de destaque por cena (ciano ou verde), âmbar no máximo em um detalhe.
- Profundidade e câmera continuam (o DOM plano com fade de 02/10 foi sentido como inferior), mas com contenção: movimentos suaves e poucos, uma transição desenhada por virada (zoom-through, wipe do símbolo, match cut), sem chicotes em sequência.
- Um elemento herói por plano. Nada de enxames de partículas, campos de orbes, vários glows simultâneos, anéis pulsando, feixes ou cenário competindo com o texto. Linha da jornada fina e discreta, chão de pontos sutil, poeira quase imperceptível.
- Teste antes de renderizar: se tirar um efeito e a mensagem continuar igual, o efeito sai. A cena tem de parecer peça institucional de SaaS B2B, não demo de 3D.
- Acabamento de estúdio vem de composição, ritmo, tipografia, sombras de contato, motion blur limpo e som preciso, não de quantidade de efeitos.

## Âmbar e elementos de dor (Davi, 01/10: "achei exagerado esses funis amarelos, devem sempre seguir a marca")
- Âmbar é detalhe: anel fino, palavra-chave, uma pílula, os próprios leads caindo. Nunca volumes grandes (cones, feixes, halos chapados, vários elementos âmbar na mesma cena).
- A cena precisa continuar lendo como Leadimob: base escura, azul/ciano dominando, verde para resultado.

## Nunca repetir
- Frame 0 com uma palavra só: abrir com pelo menos 2 palavras e movimento.
- Quadros vazios entre estações (card só entrando depois da câmera chegar).
- Texto de interface < 28px em mockup (ilegível no celular).
- Elementos a menos de 72px da borda direita (botões do Reels).

## Ganchos: chamada direta ao ICP (Davi, 02/10)
- Sempre um dos reels do dia fala diretamente com o público da Leadimob, pelo nome, na primeira palavra: "Corretor, você ainda não faz isso?", "Imobiliária que não faz isso, perde.", "Incorporador, o que falta?".
- Rodízio entre corretor, imobiliária e incorporador; o gancho precisa ser pago logo em seguida com uma prática concreta. Regras e moldes em `instagram/PLANO-INSTAGRAM.md` ("Linha de ganchos").

## Padrão de qualidade (Davi, 03/10)
- "Use todo o poder do Opus 5.5 para entregar qualidade e material premium, qualidade de estúdio profissional, harmonia entre os efeitos dinâmicos; os efeitos devem fazer sentido com o design da Leadimob, a UI e as funcionalidades."
- Efeito só entra se vier do produto ou do sistema visual da marca, e todos os efeitos de uma peça falam a mesma linguagem de movimento. Vale junto com a direção sóbria: não é licença para mais efeitos.

## Rotina de 03/10 (aprendizados de processo)
- Não use `pkill -f` com trecho do comando que também aparece no shell da ferramenta: derruba a própria sessão. Mate por PID.
- Narrações da semana seguinte saem aos sábados; dias com áudio reaproveitado (sem vocativo) levam a chamada ao ICP no Reel 2.


## Rotina diária: lições de 03/10 (primeira produção feita pela rotina)
- Partir do modelo não é copiar o modelo: o Reel 2 de 05/10 saiu como o de 03/10 com o texto trocado. Sistema visual e motor ficam; cenas, composição e transições mudam.
- A nota que vale é a do corte final. Entregar com nota abaixo de 8 só com o aviso "ABAIXO DA META" no LEGENDAS.md e no resumo.
- A publicação não instala pacotes e roda um comando só; os JPEG do carrossel saem da produção (`publicar/prepara_jpg.py`).

## Carrosséis mais leves (Davi, 05/10)
Palavras dele sobre os carrosséis de 07/10 e 08/10: gostou do conteúdo e da produção, mas achou as artes "bem carregadas", com "excesso de conteúdo". Esses dois ficam como estão; vale para os próximos:
- Uma ideia por slide: título, uma frase de apoio e UM artefato visual. Nada de dois blocos de conteúdo no mesmo slide (como "sem processo" e "com processo" empilhados).
- Menos texto dentro dos artefatos e mais área vazia; se precisar de mais conteúdo, vai para a legenda ou vira outro slide.
- O elemento contínuo entre slides fica discreto, sem fichas, rótulos e pílulas acumulando na faixa de baixo.
- Na crítica, incluir o critério "leveza" (o slide se lê em 2 segundos).

## Palavra de comentário por post (Davi, 06/10)
- "Comente DIAGNÓSTICO" deixou de ser regra: ele achou que não tinha a ver. Cada post pede uma palavra própria, ligada ao tema, na arte, na narração e na legenda.
- Peças já prontas ou narrações já gravadas com DIAGNÓSTICO ficam como estão; vale para o que for produzido a partir de agora (roteiros novos inclusive).
