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
