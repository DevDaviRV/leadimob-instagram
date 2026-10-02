# Status das credenciais do ambiente de nuvem

Teste somente leitura, sem cabeçalho de autorização (a credencial deveria ser anexada pelo proxy do ambiente). Nenhum token ou chave foi impresso ou gravado.

**Data e hora:** 02/10/2026 14:29 (America/Sao_Paulo)

| Teste | Endpoint | Código HTTP | Resultado |
|---|---|---|---|
| Instagram Graph API | `GET graph.instagram.com/v24.0/me` | — (403 no CONNECT do proxy) | bloqueado pela rede |
| ElevenLabs | `GET api.elevenlabs.io/v1/user/subscription` | 401 | `Neither authorization header nor xi-api-key received` |

## Campos anotados
- Instagram: nenhum (`user_id`, `username`, `account_type`, `media_count` não obtidos — a conexão não chegou ao servidor).
- ElevenLabs: nenhum (`tier`, `character_count`, `character_limit` não obtidos — resposta 401).

## Conclusão
- **Instagram: NÃO funciona neste ambiente.** O domínio `graph.instagram.com` não está liberado na rede do ambiente (403 no CONNECT), então nem dá para saber se a credencial está configurada.
- **ElevenLabs: NÃO funciona neste ambiente.** O domínio está liberado, mas o proxy não anexou a chave `xi-api-key` (401) e não há chave na requisição.
