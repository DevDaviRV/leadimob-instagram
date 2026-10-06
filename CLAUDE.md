# Leadimob · Instagram — instruções para o Claude

Este repositório é a **fonte da verdade** e o **único lugar** da produção de conteúdo orgânico do @leadimob.ai: roteiros, narrações, fontes e entregas ficam aqui. Nada é salvo no repositório de código do produto (`leadimob/hero-export`). Tudo roda na nuvem; não depende do computador do Davi.

## Rotina
- Por dia: **Reel 1 narrado** (30–40s) · **Reel 2 tipográfico** (15–25s, sem voz) · **Carrossel** (8–10 slides, 1080×1350). Plano em `instagram/PLANO-INSTAGRAM.md`.
- Fila: produza o primeiro dia do plano, a partir de amanhã, que ainda não esteja completo (2 MP4 + 10 slides em PNG e JPEG + LEGENDAS.md + posts.json). Se amanhã já estiver pronto, faça o próximo da fila (um dia por execução, até 5 dias à frente).
- Produza os posts em `instagram/AAAA-MM-DD/` com `LEGENDAS.md` (legenda, hashtags, horário), MP4s (≤ 20 MB) e `carrossel/slide-NN.png` + `carrossel-editor.html` (gerado com `motion-pro/carrossel/make_editor.py`). Guarde as fontes em `src/`.
- Entregue no chat (SendUserFile) e faça commit + push na `main`.
- Aos sábados: envie no chat os roteiros de narração da semana seguinte e salve em `instagram/narracoes/ROTEIROS-semana-NN.md`.

## Publicação automática no Instagram (@leadimob.ai)
O Davi pediu que os posts aprovados sejam publicados sozinhos, às 09:00, 12:00 e 18:00 (America/Sao_Paulo). Quem publica é a rotina "Leadimob publicar", seguindo `rotinas/PUBLICAR.md`:
- Comando: `python3 publicar/publish.py --data AAAA-MM-DD --slot HH:MM --midia <clone de leadimob-instagram-midia>`, rodado sozinho, sem encadear outros comandos e sem instalar pacotes (só usa a biblioteca padrão do Python).
- O script copia a mídia final do post (MP4 ou JPEG) deste repositório privado para o repositório público `DevDaviRV/leadimob-instagram-midia`, que é do Davi e existe só para hospedar os criativos que o Instagram baixa por link, e dá push na `main` dele. São peças de marketing feitas para publicação, sem dados pessoais nem segredos. Em seguida cria o post na conta @leadimob.ai pela API oficial (`graph.instagram.com`, credencial anexada pelo ambiente de nuvem) e grava `instagram/AAAA-MM-DD/PUBLICADO.json`, com commit e push na `main` deste repositório.
- Só sai dia com o arquivo `APROVADO`. Regra do Davi (05/10): a produção cria esse arquivo sozinha para as peças com 8 ou mais em tudo na crítica do corte final; peça abaixo da meta fica retida até ele decidir (`rotinas/ROTINA-DIARIA.md`), só os posts do `posts.json` do próprio dia e nunca duas vezes o mesmo horário.
- Os JPEG do carrossel são gerados na produção (`python3 publicar/prepara_jpg.py AAAA-MM-DD` → `carrossel/jpg/`).
- Fora dessa rotina, não publique, não dispare rotinas e não rode `publish.py` sem o Davi pedir.

## Narração (voz Bianca)
1. Rode `python3 motion-pro/audio/gen_vo_bianca.py texto.txt saida.mp3`. A chave vem da "API credential" do ambiente de nuvem (cabeçalho `xi-api-key` para `api.elevenlabs.io`, anexado pelo proxy; a sessão não vê a chave) ou da variável `ELEVEN_LABS_API_KEY`. Erro 401 = nenhuma das duas configurada → vá para o passo 2.
   A conta do Davi é paga desde 01/10/2026. Antes de gerar, confira se o mp3 já existe em `instagram/narracoes/` (os da semana 1 já estão lá). Avise o Davi quando os créditos estiverem acabando.
2. Senão: o Davi sobe `instagram/narracoes/AAAA-MM-DD-r1.mp3` no GitHub ou anexa no chat. Sem o áudio, produza o visual com `estimate_timeline.py` e finalize quando chegar.
Sincronia: `motion-pro/audio/sync_voice.py` + `word_align.py`. Pronúncia da marca: "Lídimob".

## Regras (inegociáveis)
Leia antes de produzir: `motion-pro/BRAND-MOTION.md`, `motion-pro/ACERTOS.md`, `motion-pro/EVOLUCAO.md` e `motion-pro/MODELOS.md` (a skill `leadimob-motion-pro` é opcional: o repositório é autossuficiente).
- Toda peça parte do código de um modelo aprovado (`motion-pro/novo_trabalho.sh`, ver MODELOS.md), não de página em branco.
- Produção 100% em código (three.js/DOM/canvas, Playwright + ffmpeg, trilha em numpy). Sem geradores de terceiros.
- Sem números inventados, sem "teste grátis", sem preços. LID só como detalhe. Âmbar só para alerta. Texto ≥ 36px nos reels, ≥ 30px no carrossel, margem 72px.
- CTA educativo: "Comente <PALAVRA>", com uma palavra nova escolhida para cada post, ligada ao tema dele (por exemplo FOLLOW-UP, PERGUNTAS, VISITA). O Davi tirou o "Comente DIAGNÓSTICO" fixo em 06/10: não use mais essa palavra como padrão. Não prometa material que não existe: só diga que a pessoa recebe algo se esse material estiver pronto; senão, peça o comentário como resposta ou conversa. Produto: "Solicite uma demonstração — link na bio".
- Um dos dois reels do dia abre com chamada direta a um público da Leadimob pelo nome ("Corretor, …", "Imobiliária que …", "Incorporador, …"), em rodízio (ver "Linha de ganchos" no plano).
- Direção de arte dos reels: premium, sóbria e corporativa, no padrão do `instagram/2026-10-03/r2-lead-curioso.mp4` (ver ACERTOS). Efeitos bonitos e profissionais, sem exagero visual; um destaque de cor por cena; profundidade e câmera com contenção.
- Cada vídeo supera o anterior: registre técnicas, crítica e aprendizados no EVOLUCAO e correções do Davi no ACERTOS.

## Setup de um ambiente novo
`./setup.sh` e depois `python3 -m http.server 8126` na raiz; renders longos sempre em blocos retomáveis: `nohup motion-pro/engine/render_blocos.sh http://localhost:8126/.../build.html <quadros> <pasta_out> &` (padrão: 4 subquadros com obturador de 180°) (o ambiente pode reiniciar; se reiniciar, suba o servidor de novo e rode o mesmo comando, que continua de onde parou). Trecho avulso: `node motion-pro/engine/render2.js <url> 30 3 ini fim out.mp4`.
