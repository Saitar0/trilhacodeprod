# Beta 8.2 — fronteira da autoridade editorial

## Resultado medido

O harness MongoDB provisiona credenciais sintéticas separadas para `beta8-1-runtime`, `beta8-1-authority` e `beta8-1-preparer`. O client comum não possui escrita em `nodes`, `content_blocks` ou coleções de publicação. Tentativas autenticadas diretamente no MongoDB para inserir, atualizar e excluir nós/blocos foram rejeitadas pelo servidor MongoDB; o preparador também não escreveu no namespace de heads experimentais. A autoridade realizou as mutações aprovadas pelo caminho C8/C12 e gravou histórico/auditoria.

## Limite identificado

Isso prova **DATABASE_PRIVILEGE_VERIFIED** para as roles sintéticas usadas. Não prova **PROCESS_ISOLATION_VERIFIED**. O teste executa FastAPI via `httpx.ASGITransport` no processo Python do harness; esse mesmo processo abre `authority_client`, `runtime_client` e `stage_client`, e injeta `authority_db` em `Beta8EditorialMutationBoundary`. Assim, a credencial privilegiada e o client da autoridade são alcançáveis pelo mesmo processo que executa a rota. A diferença de variável/objeto não é isolamento forte.

| Garantia | Estado | Evidência/limite |
|---|---|---|
| Privilégio MongoDB do cliente comum | `DATABASE_PRIVILEGE_VERIFIED` | MongoDB 7 replica set descartável rejeitou mutações diretas das coleções testadas. |
| Negativa de autorização por usuário/recurso | `APPLICATION_AUTHORIZATION_VERIFIED` | Requisição HTTP usa login/sessão real do backend e grant sintético C12 por trilha. |
| Protocolo editorial C8/C12 no caminho | `PROTOCOL_ENFORCEMENT_VERIFIED` para 3 operações | W-07 PUT, W-07 POST e W-05 PUT no harness; CAS, fence, revogação, auditoria e idempotência exercitados conforme cada fluxo. |
| Separação de processos API/autoridade | `NOT_VERIFIED` | Mesma instância Python contém os clients e o boundary. |
| Distribuição de credenciais operacionais | `OPERATIONAL_CREDENTIAL_DISTRIBUTION_NOT_VERIFIED` | Não houve acesso a runtime, secret store, produção ou staging. |

## Comportamento de startup

As operações selecionadas (`POST /api/blocks`, `PUT /api/nodes/{id}`) falham com 503 sem a capacidade injetada explicitamente; `PUT /api/blocks/{id}` já falhava da mesma forma. O teste monta uma aplicação pequena e injeta a capacidade apenas depois do gate de propriedade. O startup comum não constrói essa composição Beta 8.1. Isso não prova que os demais writers antigos sejam desabilitados nem que suas credenciais operacionais sejam restritas.

## Próximo passo necessário

Para afirmar isolamento da autoridade, separar a autoridade em processo/serviço com acesso exclusivo à credencial editorial, comunicação autenticada em rede privada, comandos fechados e validação independente de sessão/grant/revisão. A API comum não pode importar nem receber o client/URI privilegiado. Depois, provar que a falha da RPC não aciona fallback de escrita no processo comum. A distribuição real de credenciais e a topologia precisam de verificação operacional aprovada pelo ADR-008; esta fase não fez essa verificação.
