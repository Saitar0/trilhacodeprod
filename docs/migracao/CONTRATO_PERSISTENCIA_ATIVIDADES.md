# Contrato de persistência de atividades — 14F

**Estado:** implementação isolada de rascunhos; não conectada à aplicação nem validada em MongoDB real. Os documentos aqui definidos não são endpoints de aluno.

## Relação com a persistência existente

O sistema atual mantém quizzes publicados em `quiz_versions`, com catálogo ativo e tentativas em `quiz_progress`. O repositório 14F é um arquivo editorial separado para as seis atividades do contrato 14E, incluindo atividades ainda não avaliáveis. Ele não serve conteúdo ao aluno, não publica snapshots e não substitui a fonte operacional `quiz_versions`.

Não foi consultado MongoDB para determinar se algum `activity_ref` já corresponde a um quiz operacional. Sem snapshot autorizado, essa correspondência permanece pendente. Uma futura publicação deve adaptar apenas conteúdo aprovado para o fluxo existente e manter o histórico de tentativas vinculado à versão operacional exata.

## Modelo lógico

```text
activity_ref (ID curricular estável)
└── version_id (ObjectId operacional, imutável)
    ├── public version (sem gabarito)
    ├── private version (gabarito/critério, ou null)
    └── version_created event (metadados, sem conteúdo)
activity_ref
└── current head (version_id + revisão monotônica)
```

`source_version_ref` conserva a referência hash do enunciado da 14E. `version_id` é criado uma vez na primeira gravação. O hash canônico do registro — incluindo público e privado — fica exclusivamente no documento privado e no índice de idempotência. Alterar somente gabarito ainda cria nova versão, mesmo que `source_version_ref` do enunciado permaneça igual.

## Esquema físico implementado

### `typed_activity_public_versions`

Campos: `storage_schema_version`, `version_id`, `activity_ref`, `source_version_ref`, `activity_type`, `phase`, `source_id`, `source_markdown`, `public`, `validation_state`, `publication_state`, `evaluator_compatibility`, `evaluation_policy`, `provenance`, `integrity` pública, diagnósticos, `created_at` e `created_by`.

Não contém `private_payload`, resposta correta, explicação privada, hash integral, hash da fonte do gabarito ou índice correto. A projeção de consulta lista os campos permitidos. `public` e `source_markdown` são conteúdo sem gabarito; o modelo é um snapshot interno answer-key-free, não o schema HTTP de aluno.

### `typed_activity_private_versions`

Campos: `storage_schema_version`, `version_id`, `activity_ref`, `activity_type`, `private_payload`, `private_content_sha256`, hashes privados, `created_at` e `created_by`.

Esta coleção contém um documento para toda versão, inclusive `private_payload: null` quando não há material privado, mantendo o pareamento atômico. Modelos e campos privados usam `repr=False`; a leitura exige autorização `submissions.grade`. A projeção privada também é explícita.

### `typed_activity_version_events`

Registra `version_created`, ator, atividade, versão, tipo, status inicial e hora. Não registra conteúdo, respostas, explicações ou hashes derivados do gabarito. Não há mutação de evento nem implementação de transição editorial nesta etapa.

### `typed_activity_heads`

Mantém uma linha por `activity_ref` com `current_version_id`, contador `revision`, data e ator da última gravação. O `_id` também é o `activity_ref`; o índice único `one_typed_activity_current_head` reforça a unicidade.

## Estados editoriais

A camada armazena `draft`, `pending_review`, `structurally_validated` e `publishable`. O rótulo `publishable` não autoriza nem executa publicação; nenhuma rota consome essa coleção. `published` é recusado porque snapshots operacionais pertencem ao catálogo existente `quiz_versions`.

Não há método para promover estados ou modificar uma versão. Uma tentativa de salvar o mesmo conteúdo com estado diferente resulta em conflito. Uma futura mudança de estado exige contrato separado de eventos/auditoria e autorização explícita.

## Integridade e idempotência

O hash interno é SHA-256 de JSON UTF-8 canônico sobre contrato, identidade, tipo, texto original, projeções pública/privada, versão de fonte, validação, política, proveniência e integridade. Ele exclui somente status editorial e diagnósticos derivados. O status é comparado na reexecução e diferença de status gera conflito em vez de overwrite.

- Mesmo `activity_ref` e mesmo hash: retorno `unchanged`, com o `version_id` já existente.
- Mesmo `activity_ref` e conteúdo diferente: novo `version_id` somente se o chamador fornecer `expected_version_id` igual ao head corrente; a versão antiga permanece e o head avança por compare-and-swap na mesma transação.
- Uma revisão concorrente baseada em head obsoleto falha com conflito; ela não cria um ramo silencioso. Para a primeira versão, `expected_version_id` deve ser omitido. Histórico sem head falha por integridade.
- Replay idempotente valida novamente o par público/privado, identidade, versão de fonte, tipo e hashes. Um par inconsistente não retorna `unchanged`.
- Conteúdo privado nunca é usado como chave em consulta pública.
- Colisão ou pareamento incompleto: erro de conflito/integridade; nenhum fallback de atualização.
- Não há método de excluir ou atualizar documentos.

## Índices

`ensure_indexes()` define, sem ser chamado pelo startup global:

- público: único `(activity_ref, version_id)`;
- privado: único `(activity_ref, version_id)`;
- privado: único `(activity_ref, private_content_sha256)` para idempotência;
- eventos: único `(activity_ref, version_id, event_type)`;
- público: `(activity_ref, created_at desc)` para histórico;
- heads: único `(activity_ref)`.

Os nomes são `one_typed_activity_public_version`, `one_typed_activity_private_version`, `one_typed_activity_content_revision`, `one_typed_activity_creation_event`, `typed_activity_public_version_history` e `one_typed_activity_current_head`. Nenhum índice foi criado em banco nesta execução.

## Atomicidade e requisito de topologia

As gravações pública, privada e do evento ocorrem em `AsyncClientSession.with_transaction`. O repositório não tenta gravar sem transação; `InvalidOperation`/`OperationFailure` tornam-se `ActivityTransactionsRequiredError`. O MongoDB precisa ser replica set ou mongos. A exigência não foi validada em banco real nesta execução.

O teste opt-in usa somente `TRILHACODE_TYPED_ACTIVITY_MONGO_TEST_URI` explícita, exige host loopback e porta declarada, exige `replicaSet`, confere `hello` antes de qualquer operação de banco e requer a confirmação de instância descartável `TRILHACODE_TYPED_ACTIVITY_MONGO_TEST_DISPOSABLE=YES`. A URI nunca deve ser impressa. O teste seleciona um DB aleatório `test_typed_activity_<uuid>` e apaga somente esse DB após executar. O teste não roda sem a URI.

## Permissões e limites

O código reaproveita as permissões reais existentes: `content.write` para gravação de rascunho, `content.read` para leitura answer-key-free e `submissions.grade` para acesso privado. Não há endpoints novos, não há controle de acesso por objeto além da identidade curricular/versionamento e não há RBAC de coleção configurado pelo código.

Antes de uso operacional, o administrador do Mongo deve assegurar que credenciais usadas por consultas públicas não possam ler `typed_activity_private_versions`, e que backups/telemetria/logs respeitem a mesma separação. Esta regra não foi testada em produção e não foi alterada no banco.

## Compatibilidade dos tipos

Os tipos `multiple_choice`, `short_answer`, `discursive`, `matching`, `ordering` e `review` são armazenados pelo mesmo envelope discriminado, sem converter tipo. Respostas e critérios aparecem apenas no documento privado. Associação/ordenação vazias/incompletas ficam como tais; R1–R5 podem ser armazenadas como revisão sem pontuação. Nenhum tipo novo foi adicionado ao avaliador.
