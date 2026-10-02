# Teste de credenciais (instruções da rotina)

Este arquivo é a fonte das instruções. A rotina em claude.ai/code/routines (ambiente Default) só manda ler e seguir este arquivo; para mudar o comportamento, edite aqui.

Teste SOMENTE LEITURA de duas credenciais do ambiente de nuvem. Não publique nada no Instagram, não imprima nem grave nenhum token ou chave.

1. Rode: curl -sS -m 30 -o /tmp/ig.json -w "%{http_code}" "https://graph.instagram.com/v24.0/me?fields=user_id,username,account_type,media_count" SEM enviar cabeçalho de autorização (a credencial do ambiente é anexada pelo proxy). Anote o código HTTP e, se for 200, os campos user_id, username, account_type e media_count. Se a conexão for recusada (403 no CONNECT), anote "bloqueado pela rede". Se vier erro 190, anote a mensagem.
2. Rode: curl -sS -m 30 -o /tmp/el.json -w "%{http_code}" "https://api.elevenlabs.io/v1/user/subscription" SEM cabeçalho de chave. Anote o código HTTP e, se for 200, os campos tier, character_count e character_limit.
3. No repositório leadimob-instagram (já clonado no diretório de trabalho), substitua o conteúdo de instagram/STATUS-CREDENCIAIS.md pelo resultado: data e hora em America/Sao_Paulo, o nome do ambiente se souber, código HTTP de cada teste, os campos anotados e uma linha dizendo se cada credencial funciona. Faça commit direto na branch main (não crie branch claude/) com a mensagem "Teste de credenciais (ambiente Default)" e dê push na main.
4. Responda com o mesmo resumo em português, em 3 linhas.
