# Fase 2.1A.12C.10 — Fronteira editorial de API/IAM e execução assíncrona

## Escopo e resultado

Este documento registra a análise do contrato C8 contra a API editorial versionada e duas composições experimentais executadas apenas em testes: uma ponte PyMongo síncrona por `asyncio.to_thread` e um adaptador que usa `AsyncMongoClient` nativamente. Os módulos novos não são importados por rotas, serviços, startup ou workers ativos. Não houve acesso a dados ou infraestrutura operacional.

Classificação geral: **fronteira parcialmente validada no escopo isolado**. A transação async nativa, CAS, fencing, auditoria obrigatória, recibo e replay foram exercitados em MongoDB 7 descartável. IAM real completo, política real de escopo por trilha, compatibilidade de resposta, grants implantados, retenção e cancelamentos durante commit continuam sem prova.

Estados usados neste documento:

* **OBSERVED** — verificado no código versionado.
* **EXPERIMENTAL** — exercitado em harness C10, com identidades e dados sintéticos.
* **PROPOSED** — contrato futuro recomendado, ainda sujeito a aprovação.
* **OPEN** — política ou evidência ainda pendente.

## Fronteira HTTP atual

**OBSERVED.** O `APIRouter` declara prefixo `/api`; a rota é `PUT /api/blocks/{block_id}`, usa `BlockUpdate`, `BlockOut`, depende de `require("content.write")`, encaminha `model_dump(exclude_unset=True)` ao serviço e devolve o bloco serializado. O router é incluído sem outro prefixo em `server.py`. Referências: [rota e prefixo](../../backend/routes_content.py#L59), [PUT do bloco](../../backend/routes_content.py#L166-L168) e [inclusão do router](../../backend/server.py#L184).

`BlockUpdate` define `title`, `data` e `status` como opcionais, sem configuração local `extra="forbid"`: [schema](../../backend/schemas/content.py#L88-L92). A rota retorna o documento (`BlockOut`) em HTTP 200 e não declara ETag ou chave de idempotência. `update_block` lê o documento, valida status, aplica `$set` por `_id`, chama auditoria e lê o documento de novo: [serviço](../../backend/services/blocks.py#L38-L44). `audit` grava `entity`, `entity_id`, `action`, `track_id`, `summary`, `user_id`, `user_name` e `at` em `edit_history`, sem receber uma sessão: [auditoria](../../backend/audit.py#L1-L11).

### Semântica de presença e `null`

**OBSERVED.** `exclude_unset=True` preserva a distinção entre campo ausente e campo presente. Ausência não entra no `$set`; `null` explícito é encaminhado como valor. `check_status(None)` permite `null`; os três campos do schema aceitam `None`. Assim, o writer pode persistir `title: null`, `data: null` ou `status: null`. String vazia, objeto vazio e lista vazia dentro de `data` são valores presentes. `update_block` também atualiza `updated_at` e grava auditoria para um patch vazio.

**EXPERIMENTAL.** `ExperimentalBlockPatch` usa `extra="forbid"`, mantém ausente diferente de `null`, permite string vazia, objeto vazio e `null` explícito, e retorna 400 para status fora de `draft`, `published` e `archived`. Um patch vazio é rejeitado em 422 pelo contrato de intenção. Isso é uma alteração deliberada em relação ao writer atual, não uma equivalência silenciosa.

## Autenticação, autorização e escopo

**OBSERVED.** `current_user` aceita cookie `access_token` ou Bearer, valida JWT, sessão ativa, usuário, estado da conta, versão do token e e-mail verificado; então devolve o usuário e permissões por papel: [autenticação](../../backend/security.py#L87-L110). `require` aplica a tabela estática de papéis `PERMISSIONS`: [verificação](../../backend/permissions.py#L9-L18) e [permissões](../../backend/constants.py#L1-L16). `admin` e `editor` possuem `content.write`; `student` não. O writer obtém `track_id` do bloco lido para preencher auditoria. O código examinado não demonstra uma regra de autorização de escrita por trilha.

`database.py` instancia `AsyncMongoClient` no import: [cliente](../../backend/database.py#L1-L8). Por isso o harness não importa `security.py`, `database.py` nem `server.py`. Ele carrega o `permissions.py` real com apenas sua dependência `current_user` substituída por uma identidade sintética. A tabela real de permissões por papel é exercitada; JWT, sessão, usuário real e autorização por trilha não são.

**EXPERIMENTAL.** `TestCapabilityAuthority` emite uma capability não serializável a partir do ator retornado pelo dependency real, de uma lista sintética de escopos permitidos e de credencial/fence inseridos do lado do servidor de teste. A capability é vinculada a ator, trilha, tipo de operação e operation ID. O cliente não fornece capability, `WriterCredential` ou fence. IAM e fencing permanecem controles distintos.

**OPEN.** Não há política versionada de escopo `content.write` por trilha comprovada. Antes de uma integração, é necessário decidir e testar a autorização da trilha, incluindo conteúdo órfão, trilha arquivada, transferência de pertencimento e replay depois de mudança de permissões. A capability de teste não substitui autenticação nem IAM.

## Contrato HTTP futuro proposto

O harness implementa somente uma rota de teste candidata: `PUT /api/v2/tracks/{track_id}/blocks/{block_id}`. Ela não é registrada no FastAPI ativo.

| Entrada/resultado | Proposta experimental | Observação |
|---|---|---|
| Revisão esperada | `If-Match: "editorial-rev-N"` obrigatório | GET futuro deve fornecer ETag; ausente 428, malformado 400, obsoleto 412. |
| Idempotência | `Idempotency-Key` 16–128 caracteres ASCII permitidos | HMAC deriva operation ID de ator + trilha + operação + chave; chave original não é persistida. |
| Reutilização | Mesma chave e mesma intenção retorna o recibo original; intenção/base divergente retorna 409 | C8 verifica fingerprint, revisão esperada, writer e conteúdo preparado. |
| Sucesso e replay | 200 com `{revision, parent_revision}`, ETag e `Idempotency-Replayed` | Nenhum conteúdo, usuário, chave ou detalhe interno na resposta. |
| Fence obsoleto | 409 genérico | Cliente não recebe o token esperado/atual. |
| Documento ausente ou pertencimento divergente | 404 | Query transacional vincula `_id` e `track_id`. |
| Corpo inválido/status inválido | 422 para schema; 400 para status fora do conjunto, conforme writer observado | Não expor mensagens internas. |
| Commit indeterminado | 503 com instrução para repetir a mesma chave | Nunca afirmar falha definitiva sem reconciliação. |
| Falha inesperada/auditoria | 500 sanitizado | Retry só com a mesma chave; sem retry automático. |
| Autenticação/autorização | 401/403 do dependency | O harness exercita 403 por papel; não executa JWT/session real. |

`If-Match` torna explícita a precondição CAS e favorece semântica HTTP condicional. `Idempotency-Key` identifica uma intenção; o escopo proposto impede colisão cruzada entre atores/trilhas/operações. Chave, prazo de retenção, resposta estável e envelope de erros precisam de deliberação de produto/API. A retenção do recibo não foi definida.

O endpoint atual retorna um documento completo, enquanto a proposta retorna um recibo mínimo. A migração exigiria uma nova versão, leitura que exponha o ETag, implantação dos clientes compatíveis e uma regra explícita para chamadas antigas. Não se deve aceitar silenciosamente uma escrita antiga sem revisão durante o modo protegido.

### Replay depois da remoção do bloco

**EXPERIMENTAL.** A rota de teste recebe a trilha na URL, calcula a mesma intenção e chama `prepare`/`commit`; se a operação já estiver `COMMITTED`, o C8 retorna o recibo antes de executar o participante que atualiza o bloco. Repetir depois de excluir o documento retornou o mesmo recibo e não recriou bloco nem auditoria.

O harness também reavaliou o dependency real de `content.write` antes do replay: trocar o principal sintético de `editor` para `student` entre a confirmação e a repetição produziu 403, sem liberar o recibo.

**PROPOSED.** Replay autorizado representa o resultado histórico da operação, não o estado atual do bloco. Requer autenticação e autorização atuais; devolve apenas recibo mínimo e nunca reconstrói conteúdo privado. Sem a rota com trilha explícita ou um índice de idempotência separado, o endpoint legado só com `block_id` não consegue localizar com segurança o escopo de uma operação depois que o bloco desaparece. A API versionada com trilha explícita é preferível.

## Privacidade e persistência histórica

O adaptador genérico C8 persiste `payload_json`, seu SHA-256 e fingerprint em operação e histórico; por isso, uma chamada que inclua valores privados no payload os conserva. O harness C10 passa somente operação, versão do payload, referência do bloco, nomes de campos alterados e HMAC do conteúdo canônico. A intenção privada real continua apenas no patch em memória e na alteração transacional do bloco; a auditoria mantém ator, referência, campos e timestamp necessários ao formato legado/testado. Os testes verificam que valor sintético privado não aparece em payload JSON do protocolo, resposta ou recibo.

O HMAC depende de segredo fornecido pela autoridade confiável. A chave C10 é sintética e fixa apenas em testes; armazenamento, rotação e recuperação da chave em runtime não foram resolvidos. O HMAC não é uma política de ACL ou retenção. `edit_history` continua contendo `user_id` e `user_name` no modelo legado; acesso, retenção e privacidade dessa auditoria dependem de política futura. Não há logs de payload adicionados pelos módulos C10.

O adaptador async ainda aceita um `Mapping` genérico, como o C8. A minimização é garantida pelo builder restrito da fronteira HTTP testada, não pelo protocolo genérico. Um futuro chamador que ignore esse builder ainda poderia persistir dados sensíveis no C8; essa lacuna não deve ser confundida com proteção universal.

## Execução assíncrona e comparação

### Ponte via thread

PyMongo síncrono roda em `asyncio.to_thread`, com cliente e sessão próprios. O teste C10 confirmou commit, recibo e auditoria no mesmo contrato C8 e manteve um heartbeat assíncrono ativo. A ponte evita bloquear o event loop no cenário exercitado, mas cancelar a coroutine não interrompe thread nem operação MongoDB. O C9 reporta a mesma limitação e reconciliação por identidade: [resultado C9](editorial-generations-phase-2-1a-12c9-final-report.md#L24-L28).

### Adaptador nativamente assíncrono

`AsyncEditorialRevisionAdapter` exige instância explícita de `AsyncMongoClient`, replica set MongoDB 7 e banco `editorial_revision_test_c10_*`. Usa a mesma coleção de tracks/revisions, operação, histórico, writers e authorities em formato C8. A transação usa snapshot read concern, primary read preference e majority+journal write concern. CAS de revisão, fence, confirmação da credencial, callback de bloco/auditoria, histórico e recibo ficam na mesma transação e sessão.

Este código é uma implementação paralela experimental, não uma fachada do adaptador C8. Compartilha normalização JSON, fingerprint, IDs compostos e modelos C8; sua semântica foi verificada nos casos desta suíte, mas não se afirma equivalência total a todos os estados, retries ou erros do C8.

| Dimensão exercitada | Thread/PyMongo | AsyncMongoClient |
|---|---|---|
| Commit + auditoria | Passou em uma operação persistente C8 com cliente independente no worker | Passou com sessão async explícita |
| CAS | Uma das operações persistentes venceu; a outra recebeu conflito | Duas instâncias/clientes independentes disputaram uma revisão; um commit e um conflito |
| Auditoria falha | Cobertura histórica C7/C8, fora da suíte C10 de thread | Falha injetada no participante abortou atualização, revisão, auditoria e histórico; retry da mesma preparação confirmou uma vez |
| Replay | C8 foi mantido como referência no cenário de thread | Mesmo recibo em retry e após remover bloco, sem repetição de efeito |
| Cancelamento | C9 descreveu que thread pode continuar após cancelamento | Cancelamento durante callback pré-commit foi propagado; o teste observou ausência de commit naquele ponto específico |
| Latência/throughput | Sem benchmark comparável | Sem benchmark comparável |

Não foi executado benchmark. A amostra de testes é inadequada para conclusão de latência/capacidade. Para o escopo validado, async nativo elimina a thread adaptadora e usa o driver que o backend já utiliza; a implementação paralela e a revisão de seu lifecycle são custos de manutenção. Não há decisão de produção sobre qual estratégia adotar.

### Cancelamento e confirmação incerta

**EXPERIMENTAL.** Cancelar a coroutine enquanto o participante aguardava, antes do retorno ao `with_transaction`, propagou `CancelledError` e o teste observou bloco e revisão inalterados. Repetir uma requisição HTTP depois de um commit confirmado recuperou o recibo.

**NÃO TESTADO.** Cancelamento durante envio/confirmação de commit, queda real de rede, perda de ACK MongoDB, resultado `UnknownTransactionCommitResult`, encerramento de processo e shutdown do cliente. O código reconcilia erro rotulado desconhecido consultando operação; se a consulta também falhar, produz `CommitOutcomeUnknown`. Não se promete rollback quando o commit já pode ter sido aceito. Não há retry automático fora do mecanismo controlado de transação do driver; o replay do chamador mantém a mesma identidade.

## Capability, fence e limites

O fluxo conceitual é: autenticação do usuário → `content.write` → política de escopo da trilha → capability criada pelo servidor → credencial de writer e fence persistidos → intenção com revisão esperada → CAS transacional. O cliente não escolhe fence nem credencial. O fence demonstra que o writer não está obsoleto; não demonstra identidade humana ou permissão.

No teste, o permission checker real aplica `PERMISSIONS`, mas a dependência de usuário e escopo são sintéticos. Nenhuma IAM real foi validada. Não houve consulta de grants MongoDB implantados.

## Decisões ainda abertas

1. Política de autorização de escrita por trilha e tratamento de trilha/entidade órfã.
2. Versão e formato de resposta: recibo mínimo vs documento atual; rollout dos clientes.
3. Obrigatoriedade e formato final de `If-Match` e política para clientes legados.
4. Escopo, caracteres, validade e retenção de `Idempotency-Key`/recibo.
5. HTTP code/envelope definitivo para falhas de auditoria, fencing e commit indeterminado.
6. Política de replay após remoção, revogação ou alteração de permissões.
7. Semântica de patch vazio, nulls e rejeição de campos extras.
8. Gestão de HMAC/segredos e acesso a histórico, recibos e `edit_history`.
9. Escolha entre thread bridge e driver async, incluindo cancelamento e encerramento.
10. Compatibilidade com schemas, índices, grants e dados efetivamente implantados.

## Evidências e gates

Testes C10: **11 passed** (5 unitários e 6 de integração persistente), sem skips. As seis integrações abrangem API, role permission, capability sintética, privacidade, null, retry/replay após remoção, transação, rollback, CAS com dois AsyncMongoClient independentes, fencing e cancelamento pré-commit. A integração também comparou um commit C8 síncrono executado em `asyncio.to_thread` com o commit nativo assíncrono.

Regressões offline: **118 passed, 38 subtests passed** (C1, contrato offline C2, C5, harness C6 e PoC offline). Somadas aos 11 testes C10, o total observado nesta fase foi **129 passed, 38 subtests passed**. Suites persistentes C7/C8/C9 não foram reexecutadas: seus fixtures requerem portas/contêineres próprios e não foram reutilizados. A prova C10 não valida MongoDB operacional, failover multinó, grants reais, sistema ativo, API real ou todos os cenários do C8.

Estados históricos G1–G10 preservados: `PARTIAL`, `NOT_VERIFIED`, `NOT_VERIFIED`, `PARTIAL`, `NOT_VERIFIED`, `PARTIAL`, `PARTIAL`, `NOT_VERIFIED`, `BLOCKED`, `BLOCKED`. ADR-008 continua bloqueado. Nenhum gate é promovido por esta prova isolada.
