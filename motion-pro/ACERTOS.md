# Leadimob Motion — ACERTOS (regras permanentes aprendidas)

## Manter
- Davi aprova o roteiro; em seguida recebe a narração em bloco pronto para ElevenLabs e gera o áudio ele mesmo.
- Produção 100% em código (three.js, DOM, canvas, ffmpeg, numpy). Sem geradores de terceiros.
- LID sempre secundário (fecho, discreto).
- Logo oficial sobre cartão claro no fundo dark.

- Fluxo aprovado pelo Davi (30/09/2026): questionário → roteiro com tabela → narração em bloco → ele gera na ElevenLabs e envia o mp3 → sync_voice + word_align.
- Voz Bianca lê ~15 caracteres/s; com gaps de 0,7s o roteiro de 15 frases deu ~51s. Para 40–45s, cortar 2–3 frases.

## Nunca repetir
- Frame 0 com uma palavra só: abrir com pelo menos 2 palavras e movimento.
- Quadros vazios entre estações (card só entrando depois da câmera chegar).
- Texto de interface < 28px em mockup (ilegível no celular).
- Elementos a menos de 72px da borda direita (botões do Reels).
