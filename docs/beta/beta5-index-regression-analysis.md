# Beta 5 — divergência histórica de índices 38/40

## Evidência versionada

`backend/indexes.py` declara dois índices chamados:

| Nome | Coleção | Chaves | Opção | Finalidade observada |
|---|---|---|---|---|
| `one_track_publication_operation` | `track_publications` | `(track_id, operation_id)` | único | Impedir duplicação de uma operação de publicação por trilha |
| `track_publication_recovery_lookup` | `track_publications` | `(state, lease_until)` | não único | Encontrar publicações por estado e expiração de lease |

O `git show 2574bf1b98482b58746c5e7a42b4df0fe07bec93 -- backend/indexes.py` confirma que ambos foram acrescentados juntos no commit `feat(learning): prepare immutable publication read models`, que também introduziu o modelo/serviço de publicações imutáveis e testes correspondentes. A hipótese de que 38 é a expectativa histórica anterior e 40 é a lista atual intencional é sustentada pelo diff versionado.

## Correção mínima

Em `backend/tests/test_integrity_concurrency.py::test_preflight_compound_and_text_index_key_matching`, a asserção global `len(INDEXES) == 38` foi substituída por verificações explícitas dos dois nomes, coleção, ordem das chaves, unicidade e campos de preflight. As verificações pré-existentes de índices compostos/texto continuam no teste. `backend/indexes.py` não foi alterado.

## Verificação

O teste de contrato e `test_live_index_preflight_accepts_existing_indexes` passaram dentro do MongoDB 7 descartável Beta 5, depois de `ensure_indexes` e migrações do fixture terem rodado somente no banco cuja propriedade foi comprovada. Isso valida a definição e o preflight desse cenário isolado; não valida os índices de qualquer banco operacional.
