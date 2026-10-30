# Beta 8.4 — relatório final

## A–B. Resultado e Git

Foram estabilizadas no laboratório a ordem transacional entre grant e mutação, a reconciliação após reinício real da autoridade e as regressões selecionadas. O veredito global é **BETA 8.4 PARCIALMENTE VALIDADA — CONCORRÊNCIA, RECUPERAÇÃO OU REGRESSÕES PENDENTES** porque Playwright curricular e suíte histórica completa não foram executados. Nada nesta fase autoriza publicação, homologação operacional ou lançamento.

* Base exata: `aa84b209ac6fbbe6bc3863b94e75d65170f7ddd2`.
* Branch: `codex/beta8-4-authority-consistency-recovery`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-beta8-4-authority-recovery\trilhacodeprod`.
* Commits locais: mantidos somente nesta branch/worktree. Sem push, PR, merge ou deploy.

## C–H. Arquitetura e revogação

API e autoridade continuaram em contêineres/PIDs separados com MongoDB descartável e credenciais distintas; a API não recebeu URI/client privilegiados e o MongoDB negou sua escrita direta editorial. A autoridade consultou usuário, sessão e grant por recurso, e a participação condicional C12 ocorreu dentro da transação editorial.

O ponto de linearização da mutação é o commit MongoDB contendo CAS/fencing, participação do principal/sessão/grant, mutação, histórico e auditoria. Revogação pré-commit foi persistida antes da liberação e bloqueou W-07 PUT/POST e W-05 PUT. Uma operação W-07 PUT pausada depois de escrever condicionalmente o grant na transação concorreu com revogação por segundo cliente; o commit transacional veio primeiro, seguido da revogação, com estado/auditoria compatíveis. A barreira de teste só existe na composição isolada.

**Entrega A — REVOGAÇÃO CONCORRENTE VALIDADA ENTRE PROCESSOS COM ORDEM DE COMMIT COMPROVADA** no conjunto testado.

## I–P. Canal interno e modelo de ameaças

O RPC usa HMAC-SHA256 versão `beta8-4-rpc-v2` sobre serviço emissor, audiência explícita da autoridade, método, caminho, timestamp, nonce e hash dos bytes do corpo; a resposta assina a audiência do serviço chamador, nonce, status e hash do corpo. Os testes HTTP rejeitaram assinatura ausente/adulterada, mensagem expirada, serviço/audiência errados e campo de coleção arbitrária. Retry legítimo com nova mensagem de transporte reconciliou operação idempotente; nonce repetido continua rejeitado. A autoridade revalidou sessão/grant; autorização autodeclarada não é aceita.

A chave HMAC permanece compartilhada por API e autoridade no harness. Comprometimento total da API não está protegido por desenho: o processo detém a chave de serviço e é gateway confiável. Transporte TLS, rotação e distribuição operacional não foram verificados.

**Entrega B — AUTENTICAÇÃO E INTEGRIDADE DO CANAL INTERNO VALIDADAS NO MODELO DE AMEAÇAS DEFINIDO.**

## Q–X. Reinício, bridge e aprendizagem

O controlador enviou SIGKILL somente à autoridade própria e confirmou novo PID depois do restart em três pontos: antes do commit, depois do commit antes da resposta e depois da transição do staging. O verifier encontrou o estado no MongoDB e fez retries/reconciliação sem duplicar mutação ou geração. O bridge reutilizou staging Beta 5; geração anterior e sentinelas sintéticas de tentativas, submissão e progresso permaneceram intactas. A prova também editou um rascunho via HTTP entre duas transições sintéticas e verificou a revisão editorial separada da sequência CAS do ponteiro, além da proveniência editorial da segunda geração.

**Entrega C — REINÍCIO REAL E RECUPERAÇÃO DA AUTORIDADE VALIDADOS NO ESCOPO EXPERIMENTAL.** Falhas naturais de rede/host, backup/restore e eleição de replica set não foram exercitadas.

## Y–AI. Testes, frontend e E2E

O runner B8.4 terminou com código 0 na execução final. Offline: 4 testes de runtime isolados e 94 testes direcionados, com 4 skips (98 passed, 4 skipped total). Persistente: baseline de processo B8.3, três operações HTTP, negativas pelo MongoDB, RPC adversarial, revogação, auditoria, CAS, staging, retries e três reinícios reais. Ruff e MyPy direcionados, compilação Python, parser do PowerShell, configuração/guard Docker e `git diff --check` passaram.

Frontend: TypeScript, ESLint, Vitest (9 arquivos/29 testes) e build passaram; o aviso de bundle 506,05 kB permanece. Playwright curricular: **NOT_RUN**, pois a composição B8.4 não contém frontend nem prévia/lote real Beta 7.x. A suíte completa histórica do backend também não foi executada. Os detalhes e escopo constam em [backend](beta8-4-backend-regression-results.md) e [frontend/browser](beta8-4-frontend-and-browser-results.md).

**Entrega D — REGRESSÕES PARCIALMENTE VALIDADAS — COBERTURA PENDENTE.**

## AJ–AP. Editorial, gates e conclusão

W-07 PUT, W-07 POST e W-05 PUT foram revalidados; demais writers não foram ampliados nem considerados contidos. As dez unidades permaneceram draft/private; não houve acesso a fonte curricular ou sistemas operacionais. A rubrica real do projeto 3.5 continua **PROPOSED**.

ADR-008 permanece **BLOCKED**. Nenhum gate foi promovido. A documentação de base contém divergência histórica sobre G7 (alguns relatórios registram `PARTIAL`, o relatório Beta 8.2 citado em Beta 8.3 registra `NOT_VERIFIED`); ela foi preservada, não alterada. Os demais estados históricos continuam conforme seus relatórios.

Limites concretos: E2E Playwright curricular ausente; cobertura global de writers e ACL/distribuição real de segredos pendentes; HMAC não protege contra comprometimento total da API; configurações operacionais, backup/restore, rollout e rollback não verificados. O próximo incremento mínimo é rodar Playwright com a prévia real em uma composição igualmente isolada e, por processo autorizado separado, reunir evidências operacionais para ADR-008.

## Vereditos por entrega

* A — **REVOGAÇÃO CONCORRENTE VALIDADA ENTRE PROCESSOS COM ORDEM DE COMMIT COMPROVADA**.
* B — **AUTENTICAÇÃO E INTEGRIDADE DO CANAL INTERNO VALIDADAS NO MODELO DE AMEAÇAS DEFINIDO**.
* C — **REINÍCIO REAL E RECUPERAÇÃO DA AUTORIDADE VALIDADOS NO ESCOPO EXPERIMENTAL**.
* D — **REGRESSÕES PARCIALMENTE VALIDADAS — COBERTURA PENDENTE**.
* Global — **BETA 8.4 PARCIALMENTE VALIDADA — CONCORRÊNCIA, RECUPERAÇÃO OU REGRESSÕES PENDENTES**.

## Arquivos modificados

* `backend/integration_tests/beta8_1_runtime_security.py`
* `backend/integration_tests/beta8_3_process_security.py`
* `backend/integration_tests/beta8_4_authority_consistency.py`
* `backend/services/beta8_3_editorial_rpc.py`
* `backend/services/beta8_3_internal_protocol.py`
* `backend/services/beta8_curriculum_promotion.py`
* `backend/services/beta8_editorial_enforcement.py`
* `backend/test_support/beta8_3_authority_server.py`
* `backend/unit_tests/test_beta8_3_internal_protocol.py`
* `backend/unit_tests/test_beta8_4_authority_consistency.py`
* `ops/beta8-4-security/Dockerfile`
* `ops/beta8-4-security/Dockerfile.dockerignore`
* `ops/beta8-4-security/compose.yaml`
* `ops/beta8-4-security/requirements.lock`
* `ops/beta8-4-security/run-local.ps1`
* `docs/beta/beta8-4-authority-real-restart.md`
* `docs/beta/beta8-4-backend-regression-results.md`
* `docs/beta/beta8-4-final-report.md`
* `docs/beta/beta8-4-frontend-and-browser-results.md`
* `docs/beta/beta8-4-internal-channel-threat-model.md`
* `docs/beta/beta8-4-revocation-linearization.md`
* `docs/beta/beta8-4-test-isolation-and-remaining-blockers.md`
