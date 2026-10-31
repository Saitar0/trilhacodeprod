# Fase 2.1A.12C.9 — Matriz de compatibilidade editorial

## Escopo e conclusão

Esta análise compara o contrato transacional experimental da C8 com o writer assíncrono `update_block`, o formato versionado pelo código para `content_blocks` e `edit_history`, e os contratos de request/identidade do backend. A prova usa somente dados sintéticos em MongoDB 7 descartável. O banco implantado, seus validadores, índices, grants e documentos legados reais não foram consultados.

**Resultado:** compatibilidade parcial, mediante adaptação isolada demonstrada para os formatos e operações cobertos. Não há compatibilidade operacional demonstrada. A ponte C9 não é importada pela aplicação e não altera `update_block`, `audit.py`, rotas ou schemas.

Classificações usadas: `Compatível`; `Compatível mediante adaptação isolada demonstrada`; `Incompatível`; `Indeterminado por falta de evidência`.

## Código e sequência observados

O escopo é o writer W-05 identificado no [inventário C4](editorial-generations-phase-2-1a-12c4-writer-inventory.md), seguindo a evidência de escrita parcial da [C7](editorial-generations-phase-2-1a-12c7-block-audit-atomicity.md) e o contrato transacional da [C8](editorial-generations-phase-2-1a-12c8-transaction-protocol.md). Esses relatórios são contexto versionado; os comportamentos citados abaixo foram novamente inspecionados ou exercitados nesta worktree C9.

O serviço [blocks.py](../../backend/services/blocks.py#L38-L44) implementa `async def update_block(block_id: str, data: dict, user: dict)`. Ele carrega o bloco por `_id`, valida o status fornecido, acrescenta `updated_at`, aplica `$set` em `content_blocks`, chama `audit(...)` e lê o documento atualizado para retornar. A query de escrita usa somente `_id`: não há CAS, revisão esperada, fencing, chave idempotente ou sessão nessa função. O retorno é o documento completo encontrado, não um recibo de revisão.

O [audit.py](../../backend/audit.py#L7-L11) grava diretamente em `edit_history` os campos `entity`, `entity_id`, `action`, `track_id`, `summary`, `user_id`, `user_name` e `at`. A assinatura não aceita sessão e a função obtém `db` do módulo de banco. O writer e a auditoria, portanto, não compartilham transação no código observado. O comportamento parcial e uma falha após a escrita do bloco também foram reproduzidos em MongoDB descartável na C7 e na C9.

O endpoint de atualização valida `BlockUpdate`, exige `content.write`, encaminha `model_dump(exclude_unset=True)` ao serviço e serializa o retorno; ver [routes_content.py](../../backend/routes_content.py#L167-L168), [content.py](../../backend/schemas/content.py#L88-L92), [permissions.py](../../backend/permissions.py#L13-L18) e [serialization.py](../../backend/serialization.py#L17-L31). O modelo versionado declara `title`, `data` e `status` como opcionais. Com a configuração atual do Pydantic, campos extras foram ignorados no teste C9; isso não substitui uma allowlist explícita na fronteira experimental.

## Formatos versionados pelo código

| Entidade | Formato observado no código | Evidência / limite |
|---|---|---|
| `content_blocks` | `_id` é `ObjectId`; `node_id` e `track_id` são usados como strings; criação define `type`, `title`, `data`, `status`, `order`, `schema_version: 1`, `created_by`, `created_at`, `updated_at`. Atualização permite os campos fornecidos ao `$set` e acrescenta `updated_at`. | [blocks.py](../../backend/services/blocks.py#L12-L28), [blocks.py](../../backend/services/blocks.py#L38-L44). O teste C9 usou documento sintético com essa forma; não é amostra do banco implantado. |
| Request `BlockUpdate` | `title: Optional[str]`, `data: Optional[dict]`, `status: Optional[str]`; o endpoint exclui campos não enviados. | [content.py](../../backend/schemas/content.py#L88-L92), rota acima. O modelo não declara rejeição de campos extras. |
| `edit_history` | `entity`, `entity_id` string, `action`, `track_id`, `summary`, `user_id`, `user_name`, `at`. | [audit.py](../../backend/audit.py#L7-L11). C9 comprovou coexistência com duas linhas sintéticas sem campos novos. |
| Índices versionados | `content_blocks(node_id, order)` não único; `content_blocks(track_id, meta.import_ref)` único parcial; `edit_history(track_id, at)`; `edit_history(import_operation_id)` único parcial. | [indexes.py](../../backend/indexes.py#L25-L28), [indexes.py](../../backend/indexes.py#L71-L75). Definições versionadas no repositório; estado implantado não verificado. |

Não foi encontrado no escopo consultado um validador MongoDB declarativo de schema para essas duas coleções. A ausência no código inspecionado não prova ausência no ambiente implantado. Os formatos legados existentes foram representados por fixtures sintéticas derivadas do writer e de `audit.py`, não por exportação de dados.

## IDs e referências

| Identidade | Backend versionado | Composição C9 | Resultado |
|---|---|---|---|
| Bloco | String de 24 hex na API; convertido por `oid()` a `ObjectId` na persistência. | Parser estrito converte apenas a representação de 24 hex para `ObjectId`; round-trip e valores inválidos foram testados. | `Compatível mediante adaptação isolada demonstrada`. |
| Unidade/nó | `node_id` é string no schema/criação. | Não é usado para escolher a autoridade de revisão; o experimento exige `track_id` no próprio documento do bloco. | `Compatível` para o formato sintético coberto; integridade da referência armazenada não verificada. |
| Trilha | `track_id` do nó é copiado para o bloco na criação; `update_block` usa `block["track_id"]` para auditoria. | Uma autoridade C8 por `track_id`; a transação lê/escreve o bloco com seletor `{_id, track_id}` e rejeita ausência ou divergência. | `Compatível mediante adaptação isolada demonstrada`; órfãos/valores legados sem `track_id` são rejeitados ou bloqueados. |
| Auditoria | `entity_id` string; `user_id` vem de `user["id"]`. O tipo concreto do usuário autenticado não foi exercitado end-to-end. | `entity_id` usa string canônica do ObjectId; ator deve fornecer identidade string explícita. | `Compatível mediante adaptação isolada demonstrada` apenas para ator sintético string. |
| Operação, revisão e fence | O writer atual não os recebe. | Identidade de operação string por trilha; revisão e fence numéricos sob contrato C8. | `Indeterminado` quanto à origem/IAM operacional desses valores; contrato isolado foi exercitado. |

O caminho atual identifica a trilha diretamente em `content_blocks.track_id`; não há caminhada bloco → nó → módulo → trilha no `update_block`. A composição C9 não cria uma segunda autoridade e não infere uma trilha quando o campo está ausente. Pertencimento, arquivamento, duplicidade e consistência de hierarquia no banco implantado permanecem não verificados.

## Auditoria, transação e adaptação C9

A C9 reutiliza o protocolo e o adaptador persistente C8. Seu participante privado de transação faz, na mesma sessão, leitura do bloco, validação do `type` necessário ao `summary` legado, `$set` dos campos permitidos, leitura posterior e inserção em `edit_history`. A auditoria mantém os oito campos legados e acrescenta `operation_id`, `revision`, `parent_revision`, `writer_id`, `fencing_token` e `changed_fields`; ver [experimental_editorial_compatibility.py](../../backend/curriculum_contract/experimental_editorial_compatibility.py#L229-L318). A chave única parcial experimental `(track_id, operation_id)` permite registros históricos sem `operation_id` coexistirem; ela foi criada apenas no banco C9.

O documento do bloco mantém seu `schema_version: 1`. O `schema_version` dentro do payload de intenção C8 identifica a versão daquele payload de protocolo e não substitui nem altera o schema do bloco. Os campos adicionais de auditoria não foram verificados contra validators ou grants implantados; introduzi-los no ambiente exigiria compatibilidade de schema/permissões e autorização próprias.

| Dimensão | Contrato atual | Contrato C8/C9 | Evidência | Status |
|---|---|---|---|---|
| Estrutura do bloco | `ObjectId`, strings de referência, campos editoriais versionados. | Atualiza somente `title`, `data`, `status`; adiciona `updated_at`; exige `type` para auditoria. | Writer real carregado do arquivo e atualizado em MongoDB C9; formato sintético. | `Compatível mediante adaptação isolada demonstrada` para o subconjunto testado. |
| Auditoria | Documento legado sem revisão, fence ou identidade de operação. | Preserva campos legados e acrescenta metadados C8 na mesma transação. | Teste de sucesso, falha de insert/rollback, e índice parcial; nenhum validador implantado. | `Compatível mediante adaptação isolada demonstrada`; compatibilidade implantada `Indeterminada`. |
| CAS/revisão | Ausentes no writer. | Revisão monotônica por trilha e CAS do adaptador C8. | Dois clientes PyMongo separados disputaram revisão 0: um confirmou revisão 1, o outro recebeu `RevisionConflict`; uma revisão, uma auditoria C9. | `Compatível mediante adaptação isolada demonstrada`; não cobre escritores legados restantes. |
| Fencing | Ausente no writer. | O participante C9 comita dentro do mesmo protocolo transacional e respeita o fence C8. | Caminho transacional e credencial/fence sintéticos; não substitui autorização real. | `Compatível mediante adaptação isolada demonstrada` no contrato isolado; integração IAM `Indeterminada`. |
| Idempotência | Ausente; retry do writer atual pode inserir auditoria repetida. | Recibo C8 por `(track_id, operation_id)` e fingerprint; auditoria única parcial. | Replay recuperou o recibo sem revisão/auditoria duplicada; payload diferente conflitou. | `Compatível mediante adaptação isolada demonstrada`. |
| Async/lifecycle | `update_block` e `audit` são coroutines sobre `AsyncMongoClient` da aplicação. | C9 executa PyMongo síncrono em `asyncio.to_thread`; usa cliente/sessão própria e explicitamente injetada, sem compartilhar sessão com `AsyncMongoClient`. | Teste de heartbeat confirmou event loop responsivo; cancelamento da coroutine não interrompe a thread e resultado foi reconciliado por replay. | `Compatível mediante adaptação isolada demonstrada` para execução sem bloquear o loop; ponte não é cliente async nativo e não prova lifecycle operacional. |
| Validação | `check_status`; request opcional title/data/status; Pydantic ignora extra na configuração testada. | Allowlist estrita dos campos e estados permitidos, com rejeição fail-closed. | Testes de campo extra, status inválido, ObjectId e formato do request. | `Incompatível` sem adaptação de fronteira; C9 mostra a adaptação, mas mudar a rota exigiria contrato/API autorizado. |
| Autorização | Endpoint exige `content.write`; auditoria registra ator da requisição. | Credencial de writer e autoridade de fence C8 sintéticas. | Código da rota/permissão lido; nenhuma rota ou identidade real invocada. | `Incompatível` como substituição de IAM; a integração de authz permanece `Indeterminada`. |
| Erros e resposta | Erros FastAPI/driver existentes; retorno é documento do bloco. | Exceções de domínio C8/C9; retorno `CompatibleBlockCommit(receipt, block)`. | Exercício de conflito, erro de referência, falha de auditoria e replay. | `Incompatível` sem mapper explícito de API. O formato/semântica HTTP deve ser decisão explícita. |
| Legado implantado | Apenas formatos versionados por código e fixtures. | Fixture C9 com auditorias antigas sem `operation_id`. | Coexistência testada somente no banco descartável. | `Indeterminado por falta de evidência`. |

## Comportamento, erros e segurança de integração

1. **Campos editáveis:** C9 limita a atualização a `title`, `data` e `status`, alinhados ao `BlockUpdate`; não copia campos arbitrários do request.
2. **`None` e ausência:** o endpoint atual usa `exclude_unset=True`; a composição C9 preserva as chaves explicitamente presentes, inclusive `None`. O efeito de limpar campos opcionais precisa de decisão/contrato de API e testes antes de integração.
3. **Status:** o writer chama `check_status(data.get("status"))`; C9 valida contra os estados declarados no componente. A equivalência completa de mensagens/códigos HTTP não foi implementada.
4. **Bloco inexistente ou referência divergente:** o backend comum converte ID inválido/ausente em erro HTTP; C9 usa erro de domínio e restringe por `track_id`. Um mapper de compatibilidade não existe.
5. **Auditoria obrigatória:** a deliberação arquitetural estabelece confirmação conjunta. O código atual propaga erro de `audit` após a atualização já confirmada. O C9 demonstra rollback transacional em falha do insert, dentro do replica set local.
6. **Autorização:** CAS/fence não autenticam um editor. `WriterCredential` C8 e `actor` C9 de teste não substituem `require("content.write")`, escopo administrativo nem validação do ator.
7. **Replay:** C8 armazena recibo, não snapshot de resposta HTTP. O C9 tenta ler o bloco atual em replay; se o bloco tiver sido removido depois, pode não produzir o retorno original. Isso é incompatibilidade potencial de resposta e requer decisão de API/idempotência.
8. **Payload privado:** o C8 mantém payload da intenção no histórico do protocolo. `data` pode conter conteúdo privado; ACL, retenção e fronteira ADR-005 ainda precisam ser verificadas. A compatibilidade não autoriza expor o histórico C8 a leitores públicos.
9. **Cancelamento:** `asyncio.to_thread` mantém a operação síncrona em execução após cancelamento do awaiter. A transação pode confirmar; reconciliar por `(track_id, operation_id)` é necessário antes de decidir retry. Não há retry automático.
10. **Retry transacional:** o callback C8 é executável por `with_transaction`; seus efeitos devem permanecer MongoDB e determinísticos. Não incluir nele logging externo, notificações ou outras ações não transacionais.

## Ambiente, testes e evidência

Ambiente C9: MongoDB `7.0.43`, imagem local `mongo:7.0.43` (image ID reportado na C8: `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b`), replica set descartável de nó único `rs12c9`, WiredTiger, sessões lógicas habilitadas, PyMongo `4.18.2`, Python `3.11.9`, Pydantic `2.13.5`. Banco aleatório `editorial_revision_test_c9_*`, marcado antes de fixtures. Cliente AsyncMongoClient do writer real e cliente PyMongo síncrono do adaptador eram independentes. A porta foi publicada somente no loopback; não houve mount persistente, URI operacional ou conexão a outro ambiente. Essa topologia não prova failover multinó, perda de host ou durabilidade equivalente à produção.

Os 12 testes da [suite C9](../../backend/integration_tests/test_editorial_compatibility.py#L215-L623) exercitaram: formato e writer async real; documento transacional C8/C9; coexistência de auditorias históricas sintéticas; estado parcial do writer real quando auditoria falha; rollback do participante transacional; replay e conflito de fingerprint; ObjectId/schema do request; isolamento por trilha; event loop responsivo; cancelamento e reconciliação; concorrência entre dois clientes PyMongo independentes. Resultado final: **12 passed, 5 subtests passed**. Regressões offline: **118 passed, 38 subtests passed** para protocolo em memória, contrato offline do adaptador, observabilidade, harness C6 e PoC offline de gerações. Nenhum teste foi contado como skip/aprovado sem execução.

O writer real foi executado por harness que carrega seu código fonte com dependências controladas, sem importar o módulo `database.py` operacional; a transação C9 foi chamada separadamente com clientes próprios. Ver [harness C9](../../backend/integration_tests/editorial_compatibility_harness.py#L1-L145) e [teste do writer real](../../backend/integration_tests/test_editorial_compatibility.py#L215-L245). Não foram exercitados rota HTTP, autenticação real, fluxo FastAPI de startup, validadores/grants implantados, shutdown do cliente de aplicação ou respostas perdidas de rede do servidor. Os testes dedicados C7/C8, vinculados às próprias identidades de seus containers, não foram reexecutados nem reutilizados.

## Compatibilidade integrada

| Dimensão | Código atual | C8 | Adaptação C9 | Evidência | Status |
|---|---|---|---|---|---|
| IDs | ObjectId de bloco, strings para referências e auditoria. | IDs editoriais do protocolo são string/JSON. | Conversão estrita de block ID; `track_id` preservado; `entity_id` canônico string. | Testes ObjectId, documento e auditoria. | Compatível mediante adaptação isolada demonstrada. |
| Bloco | Schema versão 1; update parcial. | Payload de intenção versionado e revisionado. | Allowlist de 3 campos; atualização condicional por `_id` + `track_id`. | Teste em coleção sintética. | Compatível no subconjunto testado; validators implantados desconhecidos. |
| Auditoria | Campos legados sem operation/revision/fence. | Recibo/histórico protocolar próprio. | Campos legados preservados e campos C8 aditivos; índice único parcial de teste. | Coexistência e rollback persistente. | Compatível mediante adaptação isolada demonstrada. |
| Revisão/fence | Não usados. | Por trilha, CAS e fencing. | Mesmo protocolo C8; não cria autoridade concorrente. | Concorrência C9 e suites offline C8. | Adaptado isoladamente; cobertura global bloqueada. |
| Async | AsyncMongoClient e coroutines. | PyMongo síncrono. | Thread worker, sem sessão compartilhada. | Teste de loop/cancelamento. | Ponte experimental, não integração nativa. |
| Validação | Pydantic permissivo a extras no caso testado e `check_status`. | Validador de intenção C8. | Allowlist explícita e estados fechados. | Casos inválidos no C9. | Requer mudança de contrato explícita na futura API. |
| Autorização | `content.write` no endpoint; ator de request. | Writer credential/capability de protocolo. | Não tenta converter um no outro. | Inspeção de código; sem auth end-to-end. | Incompatível como substituição; bloqueado até contrato IAM. |
| Erros/resposta | HTTPException/driver; documento simples. | Exceções C8 e recibo. | Resultado composto e erros de domínio. | Testes isolados. | Requer mapper HTTP e decisão de replay. |
| Dados legados | Versão implantada não consultada. | Estado protocolar separado. | Índice parcial e fixtures sem operação. | Somente fixture sintética C9. | Indeterminado no banco implantado. |

## Bloqueios e recomendações

- Não integrar enquanto todos os writers relevantes não estiverem cobertos ou isolados; o `update_block` atual permanece um bypass e outros escritores podem alterar a trilha sem a revisão C8.
- Definir a API para `expected_revision`, operação idempotente, conflitos e formato da resposta/erros, incluindo replay após alteração ou remoção posterior do bloco.
- Projetar um adaptador MongoDB assíncrono nativo ou aprovar formalmente o uso de thread workers, com lifecycle, cancelamento e encerramento especificados. A ponte de teste não se liga ao `AsyncMongoClient` da aplicação.
- Verificar em ambiente autorizado os validadores, índices, grants e tipos legados; nenhum deles foi consultado nesta fase.
- Ligar a identidade autenticada e autorização editorial à autoridade de fence sem tratar a capability C8 como IAM.
- Rever o armazenamento/acesso do payload C8 para não expor `data` potencialmente privado; estabelecer retenção e ACL conforme ADR-005/ADR-004.
- Manter baseline operacional ADR-008 bloqueado. A prova C9 não identifica runtime, deployment, serviço, rota ou ambiente implantado.

Gates históricos permanecem: G1 `PARTIAL`, G2 `NOT_VERIFIED`, G3 `NOT_VERIFIED`, G4 `PARTIAL`, G5 `NOT_VERIFIED`, G6 `PARTIAL`, G7 `PARTIAL`, G8 `NOT_VERIFIED`, G9 `BLOCKED`, G10 `BLOCKED`. A evidência C9 é nova e isolada; não altera a matriz histórica nem satisfaz cobertura global.
