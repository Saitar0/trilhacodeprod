# Fase 2.1A.12C.15 — Plano de enforcement dos escritores

## Escopo e fonte

Esta matriz C15 complementa, sem alterar, [`editorial_writer_inventory_c13.json`](../../backend/integration_tests/editorial_writer_inventory_c13.json) e a [matriz descritiva C13](editorial-generations-phase-2-1a-12c13-writer-coverage-matrix.md). A C14 revalidou os 17 símbolos no código versionado. Isso é cobertura estática, não runtime; todas as entradas seguem `NOT_VERIFIED`. As classificações A/B/C/D históricas são preservadas.

**Regra de cutover:** writer que toca estado protegido precisa (1) participar do contrato e da autoridade apropriados, ou (2) estar bloqueado/restrito e tecnicamente incapaz de escrever o escopo. Se nenhum dos dois for demonstrado, não habilitar a mutação. O contrato comum está em [enforcement](editorial-generations-phase-2-1a-12c15-enforcement-contract.md).

## Matriz dos 17 caminhos conhecidos

| ID / classe C13 | Caminho versionado / acionador | Estado e risco relevante | Enforcement futuro e dependências | Critério de aceitação mínimo |
|---|---|---|---|---|
| W-01 / A | `tracks.py`: create/update/reorder; rotas `/tracks*`. | `tracks`, `edit_history`; writes sequenciais, reorder perde ator; `HIGH`. | Resolver trilha/ator; revisão CAS/fence única, auditoria transacional, reorder como intenção idempotente. | Duas edições/reorders concorrentes não deixam ordem parcial; stale revision conflita; audit e revisão confirmam juntos. |
| W-02 / B | `delete_track`; `DELETE /tracks/{id}`. | Cascata inclui conteúdo, versões, publicações, progresso e tentativas; `CRITICAL`. | Bloqueado até política de retirada/exclusão e retenção do aluno; operação composta/reversível conforme decisão. | Falha injetada em cada etapa não perde tentativas nem deixa cascade inconsistente; recuperação/auditoria aprovada. |
| W-03 / B | `duplicate_track`; rota POST duplicate. | Cria estrutura relacionada em várias coleções; origem/destino e retry; `HIGH`. | Autorizar leitura da origem e criação no destino; intenção idempotente e staging invisível até ativação. | Retry não duplica; destino nunca é visível parcialmente; auditoria e grants de ambos escopos verificados. |
| W-04 / B | `publish_track`; rota publish. | Versões/chunks, atividades, status de nós/blocos e track antes do CAS final; `CRITICAL`. | Bloqueado até snapshot da revisão exata, geração imutável, validação e swap de head atômico; depende W-12 e leitores. | Candidate parcial não público; conflito não ativa; todos leitores permanecem em uma geração e tentativas históricas preservadas. |
| W-05 / A | `nodes.py`: create/update/reorder; rotas nodes. | `nodes`, audit posterior; hierarquia e reorder; `HIGH`. | Resolver ancestralidade/trilha no servidor; CAS/fence por trilha; ator confiável; validação relacional na transação. | Corridas não criam órfão/ciclo nem ordem parcial; audit atômica. |
| W-06 / B | `delete_node`, `duplicate_node`, `clone_nodes`. | Apaga subárvore, blocos, relações e progresso; clone multi-documento; `CRITICAL`. | Bloqueado para delete até política de aluno; duplicação autorizada em origem/destino e staging transacional/idempotente. | Tentativas/progresso preservados conforme decisão; nenhuma cópia parcial; retry seguro. |
| W-07 / A | `blocks.py`: CRUD/order/quiz; `/blocks*`. | `content_blocks`, `edit_history`; update+audit não atômicos (C7); DELETE usa `content.write`; `CRITICAL`. | CAS/fence da trilha, audit obrigatória, idempotência, semântica HTTP aprovada; depende conter W-02/03/04/06/10/11/13/12 no mesmo escopo. | Nenhuma atualização parcial; stale revision/fence conflitam; retorno/replay não expõem payload; bypasses contidos. |
| W-08 / A | `relations.py`: create/update/delete. | `relations`/`nodes`; validação prévia sujeita a corrida; `HIGH`. | Transação/revisão comum com validação de ciclo, alvo e trilha; depende W-05. | Corridas concorrentes não criam ciclo, duplicata ou referência inconsistente. |
| W-09 / D | `taxonomy.py`: taxonomies/tags/block types; routes_taxonomy. | Catálogo global; remover tag `$pull` em nodes/tracks; sem escopo de uma trilha; `HIGH`. | Investigar autoridade global/epoch e impacto em snapshots; não forçar grant por trilha. | Contrato de catálogo, versão e efeito sobre geração/leitores aprovado; falha não deixa referências parciais. |
| W-10 / B | `imports.py`: `run_import`, `_execute`, lock/job; POST import. | tracks/tags/nodes/blocks/relations/versions/audit; lock local não cobre outros writers; `CRITICAL`. | Bloqueado até coordenar todas entidades com a autoridade global do escopo; staging, plano validado, job idempotente, audit e recuperação. | Crash/retry concorrente deixa estado antigo ou nova geração completa, nunca parcial; conflicts com CRUD/restore/publication. |
| W-11 / B | `versions.py`: restore/apply/resume; rota e CLI `resume-restores`. | Apaga e reinsere lotes; lease não é fence por escrita; também progress; `CRITICAL`. | Bloqueado até state machine, fencing por unidade, preservação de aluno e exclusão mútua com W-04/10/01/05/07. | Crash em cada checkpoint recupera deterministicamente; sem apagar tentativa; novo revision/generation auditado. |
| W-12 / A | `integrity.py`: snapshot/save version/migrate/reconcile. | Fonte editorial, versões/chunks, progress/submissions reconciliation; `HIGH`. | Vincular a revisão de origem e verificar manifesto/conteúdo; serializar contra writers; chamadas de publish/import/restore cobertas. | Snapshot prova revisão única e não mistura source revisions; orphan repair idempotente e auditável. |
| W-13 / B | `seed.py` via `manage seed`/Compose condicional. | Cria users/tracks/nodes/blocks/taxonomy; target operacional incerto; `HIGH`. | Restringir a ambiente descartável por allowlist e identidade separada; remover seed demo de qualquer escopo integrado. | Negative test impede target não permitido; logs/proveniência; nenhum writer seed alcança scope cutover. |
| W-14 / B | `manage.py`, migrations ledger/commands, indexes. | Schema, catálogo, índices; comandos migrate/seed/resume-restores; execução não verificada; `HIGH`. | Inventariar cada migration; preflight, compatibilidade expand/contract, janela autorizada; não usar como bypass editorial. | Migração idempotente/reversível ou compensável, sem writer fora de protocolo; pré-condições/rollback testadas. |
| W-15 / D | `prepare_track_publication` em `immutable_publications.py`. | Coleções privadas e artifacts candidatos; caller de app não encontrado, mas execução externa desconhecida; `MEDIUM`. | Manter desativado; resolver call graph/runtime, ACL e source consistency antes de reutilizar; depende W-04/12/leitores. | Proveniência de todos callers e policy ACL; preparation não pode ativar public head. |
| W-16 / A | `audit.py::audit`. | `edit_history`, chamada sem sessão; falha pode separar mutation/audit; `CRITICAL`. | Adaptar contrato futuro para session/transação comum e schema minimizado sem alterar esta função agora; necessário aos writers A/B. | Injeção de falha aborta mutation/revision/receipt; ator e sumário não contêm payload privado indevido. |
| W-17 / C | `EditorialGenerationsPoC`; namespace `poc_editorial_generation_*`. | Isolamento em código/teste, mas runtime externo não verificado; `LOW` só dentro do namespace comprovado. | Fora do cutover enquanto isolado; qualquer reuso reabre revisão e exige novo consentimento. | Import scan continua sem consumidor operacional; namespace distinto e teste offline passam. |

`A` adaptar: W-01/05/07/08/12/16. `B` bloquear/restringir: W-02/03/04/06/10/11/13/14. `C` isolado: W-17. `D` investigar: W-09/15. Não se reclassifica nenhuma entrada. A documentação C13 contém coleções, permissões, evidências por linha e testes localizados; C14 confirma revalidação estática, não execução de todas as suites.

## Metadados verificados no inventário C13

Esta tabela explicita os campos de controle e as coleções que não cabiam na tabela de estratégia. Os nomes de símbolos, acionadores, coleções, permissão, classificação, evidência e runtime podem ser conferidos no registro C13 linkado acima. “Não demonstrado” significa precisamente que o inventário não comprovou aquele mecanismo para o caminho.

| ID | Coleções versionadas | Permissão/ator observado | CAS, fence, auditoria, idempotência e transação observados |
|---|---|---|---|
| W-01 | tracks, edit_history | `content.write`; reorder descarta principal | Sem CAS/fence/idempotência/transaction comuns; audit posterior em algumas chamadas. |
| W-02 | tracks, nodes, content_blocks, relations, progress, learning_events, activity_publications, activity_attempts, user_track_state, version_chunks, track_versions, edit_history | `content.delete` | Cascata sequencial sem transaction/CAS/fence abrangente; audit não prova preservação de tentativa. |
| W-03 | tracks, nodes, content_blocks, relations, edit_history | `content.write` | Sem transaction multi-coleção ou chave idempotente única demonstrada; origem/destino sem grants próprios. |
| W-04 | tracks, nodes, content_blocks, activity_publications, track_versions, version_chunks, edit_history | `content.publish` | CAS final em track, operações anteriores fora de transação comum; fence compartilhado não demonstrado. |
| W-05 | nodes, edit_history | `content.write`; reorder descarta ator | Sem revisão/CAS/fence comuns; auditoria em chamadas com usuário ocorre após mutação. |
| W-06 | nodes, content_blocks, relations, progress, edit_history | `content.delete` para delete; `content.write` para duplicar | Delete multi-coleção sem transação; clone multi-documento sem idempotência uniforme. |
| W-07 | content_blocks, edit_history | `content.write`, inclusive delete | C7 reproduziu atualização separada de audit; protocolo CAS/fence/transaction não integrado. |
| W-08 | relations, nodes, edit_history | `content.write` | Checagens antes da escrita podem concorrer; audit separado; transaction/CAS/fence comuns não demonstrados. |
| W-09 | taxonomies, tags, block_types, nodes, tracks | `taxonomy.manage` para parte do catálogo; tags `content.write`; ator descartado em rotas | Catálogo transversal; remoção de tag altera referências em operações distintas; audit/transaction por ator não demonstrados. |
| W-10 | import_locks, import_jobs, tracks, tags, nodes, content_blocks, relations, track_versions, version_chunks, edit_history | `content.write` na rota; lock/job próprio | operation/job IDs, lock e heartbeat cobrem parte do import, mas não fence comum com todos os escritores; writes em etapas. |
| W-11 | restore_jobs, tracks, nodes, content_blocks, relations, track_versions, version_chunks, progress, edit_history | `content.publish` na rota; também CLI/job | Lease/heartbeat, porém `apply_snapshot` apaga/insere lotes sem fence comum por escrita nem transaction abrangente. |
| W-12 | version_chunks, track_versions, tracks, nodes, content_blocks, relations, submissions, progress | Helper/caller; sem permissão própria demonstrada | Snapshot não amarrado por evidência a uma revisão única; fence próprio e transaction abrangente não demonstrados. |
| W-13 | users, tracks, nodes, content_blocks, relations, taxonomies, block_types, tags | Seed/CLI sem principal HTTP/grant | Seed de conteúdo/conta demo; autorização, revisão, fence e idempotência editorial comuns não demonstrados. |
| W-14 | migrations, block_types, indexes/unique constraints | CLI administrativa; autorização operacional não verificada | Lock de migration não é fence editorial; classificação e rollback dependem de cada migration. |
| W-15 | track_publications, activity_publications, version_chunks | Nenhum caller ativo encontrado na busca estática; runtime externo desconhecido | Lease/idempotência próprios; source consistency não verificada; `activation_eligible=false`; sem head público. |
| W-16 | edit_history | Recebe `user`, entity, action e summary; sem session explícita | Insert de audit é separado quando chamado depois da mutation; falha parcial demonstrada por C7. |
| W-17 | `poc_editorial_generation_*` | PoC/testes, nenhum caller operacional encontrado estaticamente | Isolamento de namespace demonstrado em código/testes; não classificar como writer seguro fora dessa fronteira. |

Campos resumidos acima não promovem a cobertura dinâmica: todos os 17 caminhos e acionadores externos continuam `NOT_VERIFIED` em runtime.

## Cobertura cruzada e contenção de bypass

Para `content_blocks`, W-07 não é piloto independente: W-04 publica/atualiza bloco e quiz; W-10 importa; W-11 restaura; W-02/W-06 excluem; W-03 duplica; W-13 seed; W-12 snapshot/reconciliação é dependência; e executores externos não estão inventariados. Transição gradual que deixa um desses caminhos livre é bypass explícito, não compatibilidade temporária.

Defesa futura exige duas camadas: serviço/autoridade comum e bloqueio comprovável de rotas, jobs, CLI, seeds, imports, restores e identidades antigas. Permissões de banco separadas por identidade podem reduzir blast radius, mas sua granularidade e topologia não foram verificadas; não presumir enforcement por documento. Telemetria passiva pode detectar alguns usos, mas ausência de evento não prova ausência de writer. Import central ou feature flag de rota não fecha caminhos externos.

## Invariantes por família

* CRUD e relações: revisão monotônica por trilha, CAS, fence, auditoria obrigatória e idempotência de retries; reordenação como intenção consistente.
* Import/duplicate/restore: operação composta, fronteiras de ativação, estado recuperável e nenhum artefato parcial visível.
* Publish/snapshot: snapshot amarrado à revisão; generation imutável; head público atômico; readers pinados.
* Delete: preservar histórico e estado do aluno conforme política; eventual retirada emergencial explícita/auditada, sem apagar tentativas incidentalmente.
* Taxonomy: autoridade global distinta, versão e impacto transversal definidos.
* Seed/migration/admin: target e identidade de execução controlados, operação registrada e não concorrente com cutover.

## Experiência dos alunos e aceitação

Qualquer onda precisa manter sessão do aluno presa à geração original enquanto válida, tentativas e progresso preservados segundo contrato, correções auditáveis, retirada emergencial explícita e nenhuma revogação negativa automática de credenciais. Os seis testes C14 de `test_snapshot_safety.py` cobrem validações estruturais com doubles; não provam consistência de source revision, publicação, leitores, restore, tentativas ou runtime.

Os critérios por família devem incluir testes unitários de schema/semântica, persistentes de commit+audit+receipt, concorrência com barriers, falha em cada etapa, cobertura de todos writers do mesmo scope, testes de leitores/generation/aluno e validação operacional autorizada. O [plano de dependências](editorial-generations-phase-2-1a-12c15-implementation-dependencies.md) define ordem e bloqueios.
