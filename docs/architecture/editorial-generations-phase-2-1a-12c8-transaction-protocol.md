# Fase 2.1A.12C.8 — Contrato transacional editorial

**Observação:** 2026-10-29 UTC. Implementação e evidências restritas a MongoDB 7 descartável.

## Escopo e decisão aplicada

Esta fase implementa um contrato experimental para que uma alteração sintética de bloco, sua auditoria editorial obrigatória, a revisão por trilha, o histórico do protocolo e o recibo idempotente sejam confirmados juntos. O serviço ativo `update_block`, rotas, schemas operacionais e dados reais permaneceram inalterados.

A política de auditoria obrigatória foi autorizada para este contrato experimental. Ela não foi ampliada para telemetria, auditoria de autenticação ou eventos externos. A observabilidade das fases 12C.5/12C.6 continua separada e não participa da transação.

## Contratos anteriores reutilizados

O experimento reutiliza `WriterCredential`, `PreparedRevision`, `RevisionReceipt`, CAS por revisão da trilha, fencing persistente, fingerprints, estados de operação e histórico do protocolo da 12C.1/12C.2. O adaptador MongoDB mantém a trilha como autoridade única de revisão e fencing. Não foi criado contador por bloco nem segundo head editorial.

A 12C.7 demonstrou, no writer real e em ambiente descartável, que a atualização de `content_blocks` e o insert em `edit_history` eram operações separadas: uma falha entre elas podia deixar alteração sem auditoria. A 12C.7 também identificou diferença entre o schema operacional e o modelo experimental. Consulte a [evidência C7](editorial-generations-phase-2-1a-12c7-block-audit-atomicity.md) e seu [relatório](editorial-generations-phase-2-1a-12c7-final-report.md).

## Implementação e fronteira transacional

O módulo [experimental_editorial_block_commit.py](../../backend/curriculum_contract/experimental_editorial_block_commit.py#L1) só aceita banco `editorial_revision_test_*`, namespace `c8_*`, o mesmo cliente/banco do adaptador e topologia previamente verificada. Não cria cliente nem lê configuração implícita.

1. `prepare_editorial_block_update` valida uma intenção limitada a título e registra a operação como `PREPARED`. Esse estado não confirma alteração editorial.
2. `commit_prepared_editorial_block_update` verifica que a preparação persistida corresponde à credencial e à intenção.
3. O adaptador inicia uma transação com `readConcern: snapshot`, `readPreference: primary` e `writeConcern: majority` com journal.
4. Dentro da transação, valida credencial, fence e revisão-base; aplica update condicional do documento da trilha em `(track_id, revision, fencing_epoch, control_sequence)` e atribui a próxima revisão no servidor.
5. Um participante privado opcional, passado somente por esta composição experimental, atualiza o bloco sintético e insere a auditoria na mesma sessão.
6. O adaptador grava histórico imutável e recibo `COMMITTED`; a confirmação do commit MongoDB torna o conjunto visível atomicamente.

O ponto de serialização lógica é a transação confirmada. O update condicional do documento da trilha é a guarda CAS e a escrita de coordenação: avanço de fencing altera o mesmo documento e sequência de controle. Uma disputa de escrita impede que a operação obsoleta confirme sob um estado antigo. A transação não protege escritores que ignorem esta autoridade.

O hook `_transaction_participant` foi a extensão mínima necessária no adaptador: ele é dono da sessão e da transação que já abrangem CAS, histórico e recibo. Sem esse ponto de composição, seria necessário copiar o protocolo ou criar outra autoridade de revisão. O parâmetro é privado e opcional; chamadores existentes que o omitem preservam o caminho anterior. Como `with_transaction` pode repetir o callback, o participante deve limitar-se a operações MongoDB determinísticas na sessão recebida e não pode causar efeitos externos.

## Dados e vínculos do experimento

| Parte | Persistência de teste | Vínculo |
|---|---|---|
| Estado da revisão/fence | coleção namespaced `c8_editorial_tracks` | `_id = track_id`; revisão, fence e sequência de controle |
| Preparação e recibo | `c8_editorial_operations` | `(track_id, operation_id)`; fingerprint e estado |
| Histórico imutável | `c8_editorial_history` | `(track_id, revision)` único |
| Bloco | `content_blocks` | bloco sintético identificado por `track_id` e `_id` |
| Auditoria editorial | `edit_history` | `(track_id, operation_id)` único |

A auditoria experimental guarda apenas referências sintéticas, revisão resultante, escritor/fence, ator sintético, ação e nome do campo alterado. Não copia o título nem outros valores de conteúdo para a auditoria. O nome e os campos da coleção operacional `edit_history` não foram validados como compatíveis com esse modelo; `actor_id` sintético não define política de identidade real.

Os índices de operação, histórico, escritores, autoridades e auditoria são criados apenas no banco de teste. A unicidade impede recibos, revisões e auditorias duplicados para as respectivas chaves no escopo ensaiado.

## CAS, fencing e idempotência

* **CAS editorial:** uma revisão-base antiga conflita explicitamente. Apenas uma intenção pode avançar a mesma revisão da trilha; a revisão seguinte é server-assigned.
* **Fencing:** o fence corrente é conferido dentro da transação. `advance_fence` incrementa a autoridade e a sequência de controle do mesmo documento da trilha, sem incrementar a revisão editorial. A operação com fence antigo falha mesmo se o conteúdo não mudou.
* **Idempotência:** identidade `(track_id, operation_id)` e fingerprint vinculam escritor, revisão-base e intenção canônica. Repetição idêntica recupera o recibo e não repete update, revisão, auditoria ou histórico. Reuso da chave com intenção diferente conflita.
* **Recuperação:** diante de `UnknownTransactionCommitResult`, o adaptador tenta reconciliar pelo recibo persistido. Se não consegue determinar o resultado, expõe `CommitOutcomeUnknown`; o chamador deve reconciliar a mesma intenção, sem inventar uma nova chave nem assumir falha.

Isso significa um efeito lógico confirmado por intenção nas condições testadas; não promete exatamente uma execução física em toda falha distribuída. Retry do callback transacional, retry da operação de negócio e reconciliação de commit desconhecido são casos distintos.

As capabilities `WriterCredential` e `FenceAuthorityCredential` são credenciais sintéticas do protocolo de teste, não autenticação, autorização ou IAM de produção.

## Falhas e semântica observada

Os proxies de falha em [editorial_block_commit_harness.py](../../backend/integration_tests/editorial_block_commit_harness.py#L1) são exclusivos de teste. Falhas injetadas antes/depois dos writes de bloco, auditoria, histórico, recibo e antes do commit causaram rollback de todos os efeitos confirmáveis. O erro de duplicidade de identidade de auditoria também abortou a transação. Uma falha de leitura posterior à confirmação preservou o recibo e permitiu replay.

O teste de encerramento abrupto terminou um processo filho, via `os._exit`, depois do insert não confirmado da auditoria e antes do commit. O estado observável foi: revisão zero, bloco inalterado, sem auditoria/histórico/recibo confirmado e operação ainda `PREPARED`. Isso prova o cenário de perda do processo cliente no meio da transação deste replica set. Não é uma falha do processo `mongod`, de rede ou de failover.

## Evidências de teste

O arquivo [test_editorial_block_commit_protocol.py](../../backend/integration_tests/test_editorial_block_commit_protocol.py#L321) contém 44 casos persistentes. Cobrem o caminho normal, falhas e rollback, CAS, fencing e corrida fence/commit, replay idempotente, cliente/adaptador recriados, perda simulada de resposta, credencial revogada, bloco ausente, identidade de auditoria duplicada e entrada inválida. O caso T19 usa dois processos Python e conexões independentes; T44 coordena duas tarefas assíncronas por `asyncio.to_thread`, cada qual com cliente Mongo independente. T19, T27 e T34 foram repetidos três vezes além da suíte completa; as nove execuções passaram.

Resultado completo e contagens de regressão estão em [relatório final C8](editorial-generations-phase-2-1a-12c8-final-report.md).

## Ambiente e limitações

MongoDB `7.0.43`, `mongo:7.0.43`, image ID local `sha256:1f995ad6fdb93244a1addab1b58f934a0bc2f5643c38e02f5e9d7f0c7d227a7b`, WiredTiger, replica set `rs12c8` com um membro primário, sessões lógicas disponíveis; Docker client/server `29.8.2`, Python `3.11.9`, PyMongo `4.18.2`. O servidor usou tmpfs sem mounts persistentes, rede específica da fase sem masquerade de saída e porta publicada somente em `127.0.0.1:27138`. Os bancos eram novos, aleatórios, sintéticos e marcados com a fase antes de qualquer fixture; todos foram descartados após verificar o marcador.

Em replica set de um nó, `majority` é o único membro. A evidência não demonstra redundância, failover multinó, disponibilidade, tolerância a perda de host ou durabilidade operacional equivalente à produção. A falha pós-commit foi simulada no cliente/test harness; não houve queda real de rede nem commit de resultado desconhecido provocado pelo servidor.

O contrato não foi integrado nem comparado por execução ao schema operacional. O writer atual usa outras características, incluindo fluxo assíncrono e identificadores MongoDB distintos dos IDs string sintéticos; a auditoria operacional também tem contrato próprio. Não foram provados grants reais, compatibilidade do runtime, cobertura global de writers, política de retenção ou segurança de cutover.

## Decisão de integração

Este experimento demonstra composição técnica de revisão por trilha, fence, update, auditoria, histórico e recibo em uma unidade MongoDB. Não satisfaz G1 ou G2 integralmente, não promove qualquer gate da 12B.7 e não libera integração. ADR-008 continua bloqueado por baseline operacional. Qualquer adaptação do `update_block`, validação dos grants, cobertura de todos os writers, plano de release e cutover exige autorização futura específica.
