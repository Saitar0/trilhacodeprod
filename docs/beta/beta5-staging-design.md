# Beta 5 — staging curricular recuperável

## Isolamento e contrato

`CurriculumStagingService` recebe o banco explicitamente; não importa `database`, rotas, startup, workers, IAM ou writers ativos. O construtor exige banco chamado `beta5_<run UUID>` e token de ownership. Antes de criar índices ou escrever, confere o marcador `_beta5_test_owner` correspondente. A prova persistente complementa essa checagem com o harness Docker e MongoDB 7.

O serviço escreve somente em `_beta5_staging_batches`, `_beta5_staging_records`, `_beta5_staging_checkpoints` e `_beta5_staging_events`. O pacote inteiro é validado em memória antes de qualquer gravação. Não toca tracks, nodes, content_blocks, publications, progresso ou tentativas. Não existe estado `PUBLISHED`, promoção, leitor de staging ou integração com runtime.

## Identidade e retomada

O hash SHA-256 canônico inclui conteúdo tipado, separação de classificação, projeto, critérios, relações, referências e avisos. `batch_id` deriva dos primeiros 32 hexadecimais do hash; manifesto também guarda o SHA-256 completo e hash da fonte. IDs de registros são determinísticos. Índices únicos por lote/registro, lote/checkpoint e lote/evento evitam duplicação. Payload divergente com a mesma identidade é rejeitado pelo contrato ou pelo serviço.

Por registro, o serviço persiste documento, confirma hash, grava checkpoint e evento idempotente. Após erro, o lote fica `RECOVERABLE` se já houver registro; caso contrário, `FAILED`. A retomada confere conteúdo/checkpoints, completa o que falta e somente então marca `PREPARED`. Estados `CREATED`, `VALIDATING`, `VALIDATED`, `PREPARING`, `FAILED`, `RECOVERABLE` e `QUARANTINED` são internos ao contrato. Não há promoção.

## Atomicidade

Staging é recuperável por etapa, não uma transação global. Documento parcial é possível durante a preparação; permanece fora dos leitores e a conclusão só ocorre após reconciliação. Checkpoint atrasado depois de documento confirmado é reparado pela repetição. Conflito de conteúdo ou estado em quarentena bloqueia em vez de apagar dados. O serviço não apaga outros lotes nem revisões editoriais.
