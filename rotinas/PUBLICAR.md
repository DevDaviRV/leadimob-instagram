# Publicação no Instagram (instruções da rotina)

Este arquivo é a fonte das instruções. A rotina em claude.ai/code/routines (ambiente Default) só manda ler e seguir este arquivo.

Você publica no Instagram @leadimob.ai o post do horário atual, usando o script do repositório. Não escreva legendas novas, não edite mídias e não publique nada além do que o manifesto do dia manda. Nunca imprima nem grave tokens.

1. Dois repositórios estão clonados na sessão: `leadimob-instagram` (privado, com as peças e o script) e `leadimob-instagram-midia` (público, só criativos finais). Trabalhe na branch main dos dois (não crie branches claude/).
2. TESTE: se existir o arquivo `rotinas/TESTE-AGORA.json` no `leadimob-instagram` (formato {"data":"AAAA-MM-DD","slot":"HH:MM"}), esta execução é um teste pedido pelo Davi: garanta as dependências do passo 4, rode `python3 publicar/publish.py --data <data> --slot <slot> --midia <caminho do leadimob-instagram-midia> --teste`, depois apague `rotinas/TESTE-AGORA.json`, faça commit ("Teste de publicação executado") e push na main, informe o resultado (linha TESTE_PUBLICADO com o link, ou o erro completo) e encerre sem seguir os passos abaixo. Se der ERRO, apague o arquivo do mesmo jeito e relate o erro completo.
3. Descubra a data e a hora atuais em America/Sao_Paulo. Leia `instagram/AAAA-MM-DD/posts.json` de hoje (se não existir, não publique e diga isso) e `instagram/AAAA-MM-DD/PUBLICADO.json` (se existir). Candidatos = horários que estão no posts.json de hoje, que ainda não estão no PUBLICADO.json e cuja hora é no máximo 40 minutos depois da hora atual (ou seja, o horário da vez e também os atrasados de hoje que não saíram). Publique UM por execução: o mais antigo dos candidatos. Se não houver candidato, não publique nada e diga isso. Nunca publique posts de outro dia.
4. Garanta as dependências: `python3 -c "import PIL"` (se faltar: `pip install --break-system-packages pillow`).
5. Rode, a partir da raiz do `leadimob-instagram`: `python3 publicar/publish.py --data AAAA-MM-DD --slot HH:MM --midia <caminho do clone do leadimob-instagram-midia>`.
   - `PUBLICADO ...`: sucesso. Faça commit de `instagram/AAAA-MM-DD/PUBLICADO.json` no `leadimob-instagram` (mensagem "Publicado AAAA-MM-DD HH:MM", terminando com "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>") e push na main.
   - `JA_PUBLICADO ...`: não faça nada.
   - `AGUARDANDO_APROVACAO ...`: não publique; informe que o dia não foi aprovado.
   - `ERRO ...`: não tente contornar nem publicar por outro caminho. Tente rodar o mesmo comando mais uma vez depois de 2 minutos; se falhar de novo, pare.
   - Se faltar `instagram/AAAA-MM-DD/posts.json` (o dia não foi produzido), não publique.
6. Termine com um resumo de 2 linhas em português: o que foi publicado (com o link) ou por que não foi.
