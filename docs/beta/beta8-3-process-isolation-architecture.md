# Beta 8.3 — Isolamento entre processos

## Escopo

Esta composição é exclusivamente experimental. O commit-base é `167166e311024678a9619b18678bc145c3482d12`. API, autoridade e MongoDB 7 são serviços separados em uma rede Docker interna identificada por um UUID desta execução. Nenhuma porta é publicada e o banco usa `tmpfs`.

## Antes e depois

Na Beta 8.2, a composição instalava o limite editorial no processo da API. A API tinha uma identidade MongoDB comum e o mesmo processo construía o boundary privilegiado. Isso demonstrava isolamento por coleção no MongoDB, mas não separação da credencial da autoridade.

Na Beta 8.3:

| Processo | Identidade MongoDB | Responsabilidade | Segredos ausentes |
| --- | --- | --- | --- |
| API FastAPI | `beta8-3-api` | Autenticação existente, leitura comum e RPC de comandos fechados | URI/senha da autoridade, URI/senha de staging, chave do stager e credencial root |
| Autoridade editorial | `beta8-3-authority` | Revalidar sessão/grant; C8/C12, CAS, fencing e auditoria | credencial da API, root e escritor de staging |
| Preparador Beta 5 | `beta8-3-stager` | Preparar e checkpointar somente o lote sintético | Mongo privilegiado da autoridade |
| Leitor de staging | `beta8-3-stage-reader` | Relê e valida lote já preparado | escrita de staging e publicação |
| Provisionador/verificador | root sintético | Provisionamento e assertions do harness | Não é distribuído aos serviços long-lived |

O harness inspeciona PIDs de contêineres distintos, identidade de imagem/labels, variáveis de ambiente, mounts, portas, rede e usuários MongoDB antes de executar a prova. A API comum não tem privilégios Mongo para `nodes`, `content_blocks`, C8/C12, gerações, auditoria ou publicação. A autoridade não tem `delete` editorial nem acesso à coleção operacional de publicações.

## Limites

Os privilégios Mongo são por coleção. O driver não limita predicates dentro de uma coleção; por isso a autoridade continua sendo um processo confiável. O harness não prova como segredos serão distribuídos operacionalmente. O provisionador root é uma identidade temporária de teste, não uma identidade de serviço da aplicação.

O canal HTTP usa rede interna e HMAC autenticado, sem TLS nem criptografia de payload. Esta é evidência de isolamento e integridade no harness, não um desenho operacional de transporte. A chave API↔autoridade está presente em ambos os processos de teste, e a API é tratada como gateway confiável; comprometimento total da API permanece uma fronteira de confiança.

## Startup

Os módulos de composição fazem preflight antes de importar `server`/`database`, exigem os dois marcadores de harness e recusam URI/usuários que não pertençam ao banco descartável. O startup comum não importa os módulos Beta 8.3 nem recebe o client privilegiado. Sem capacidade remota, W-07 PUT/POST e W-05 PUT continuam negando com `503`; nenhum fallback local é instalado.

Essa negativa protege a fronteira, mas significa que essas operações editoriais não estão disponíveis no startup comum desta composição. Isso é indisponibilidade intencional/fail-closed da capacidade experimental; a compatibilidade operacional das rotas depende de uma autoridade aprovada e integrada posteriormente.
