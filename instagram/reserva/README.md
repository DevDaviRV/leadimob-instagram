# Reserva de peças aprovadas

Peças atemporais, já com 8 ou mais em tudo na crítica do corte final, para cobrir horário que ficou vago (peça retida ou produção que falhou).

- Uma pasta por peça: `reel-<nome>/` (MP4, `legenda.json` com {"tipo":"reel","arquivo","capa_s","legenda"}, `src/`) ou `carrossel-<nome>/` (`slide-NN.png`, `jpg/slide-NN.jpg`, `legenda.json` com {"tipo":"carrossel","legenda"}, `src/`).
- Quem usa: a rotina diária (passo de aprovação) e o chat. Ao usar, mova a pasta para o dia, inclua no `posts.json` e apague da reserva. Peça de reserva nunca é publicada duas vezes.
- Reposição: quando a reserva tiver menos de 2 reels e 1 carrossel, a rotina diária produz uma peça de reserva no lugar de um dia a mais de fila.
