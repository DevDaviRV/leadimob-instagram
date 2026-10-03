# Rotinas (claude.ai/code/routines, ambiente Default)

As rotinas rodam no ambiente **Default** da nuvem, que tem as credenciais da ElevenLabs e do Instagram. Cada rotina tem uma instrução de uma linha que aponta para um arquivo desta pasta, então as regras são atualizadas pelo repositório, sem editar a rotina.

| Rotina | Instrução a colar | Agenda |
|---|---|---|
| Teste de credenciais | `Leia rotinas/TESTE-CREDENCIAIS.md no repositório e siga exatamente as instruções.` | manual (Run now) |
| Leadimob Instagram diário | `Leia rotinas/ROTINA-DIARIA.md no repositório e siga exatamente as instruções.` | diária, 06:21 (America/Sao_Paulo) |

| Leadimob publicar | `Leia rotinas/PUBLICAR.md no repositório leadimob-instagram e siga exatamente as instruções.` | diária às 08:55, 11:55 e 17:55 (três gatilhos) |

Repositórios: `DevDaviRV/leadimob-instagram` em todas; a rotina de publicação também precisa de `DevDaviRV/leadimob-instagram-midia` (público, só criativos finais). Conectores: nenhum.

Publicação: a rotina não instala pacotes e roda um comando só (`python3 publicar/publish.py ...`). Os JPEG do carrossel vêm prontos da produção (`publicar/prepara_jpg.py`). Em 03/10 o post das 12:00 não saiu porque a instalação do Pillow foi encadeada com o script e o classificador de permissões negou o comando inteiro; por isso a instalação saiu do caminho da publicação.

Aprovação: `rotinas/config.json` → `"aprovacao": "manual"` exige o arquivo `instagram/AAAA-MM-DD/APROVADO` para publicar o dia; `"auto"` publica direto.
