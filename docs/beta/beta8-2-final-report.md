# Trilha Code — relatório final Beta 8.2

## A. Resultado executivo

Foram integradas duas operações de rascunho adicionais e ampliada a prova persistente do bridge de staging. A suíte isolada demonstrou autorização, CAS/fencing, idempotência, auditoria, negativas MongoDB e recuperação nos cenários injetados. A contenção permanece parcial: somente três operações editoriais HTTP selecionadas passaram pela autoridade e a autoridade e API ainda compartilham processo no harness.

## B. Git e isolamento

* Base exata: `23e985d9ab4df34baecc1590a8e514b43210c0d7`, pertencente à linha Beta 8.1 e descendente de `af76e636ac257d4aa5f13c42fcc63fb4c87f67e2`.
* Branch: `codex/beta8-2-editorial-writer-containment`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-beta8-2-writer-containment\trilhacodeprod`.
* O checkout original e demais worktrees foram preservados. Commits somente locais; sem push, merge ou deploy.

## C–H. IAM, integração e auditoria

O caminho HTTP usa o mecanismo ativo do backend para autenticar e resolver usuário/sessão. O adaptador experimental valida a projeção da identidade e a permissão global existente; C12 exige grant explícito para `block.create`, `block.update` ou `node.update` na trilha resolvida. Escopo ausente ou divergente nega a operação. A identidade e os campos de autorização não são escolhidos no body pelo cliente.

As rotas selecionadas passam ao boundary C8/C12. O commit condicional vincula autorização, sessão, usuário, revisão, fence, mutação e evento de auditoria na transação do replica set descartável. Retry com mesmo operation ID/payload retorna replay; operação com revisão/fence obsoletos ou grant revogado é rejeitada. Auditoria registra ator, ação, recurso, revisão e operation ID, sem token ou senha.

**Entrega A — veredito:** `CONTENÇÃO DOS WRITERS PARCIALMENTE AMPLIADA — CAMINHOS PENDENTES`.

## I–N. Inventário, seleção e W-07

O inventário C16 contém 17 famílias; os símbolos versionados permanecem no código. W-07 PUT de atualização de bloco da Beta 8.1 foi reexecutado; Beta 8.2 adicionou W-07 POST de criação de bloco e W-05 PUT de atualização restrita de nó em draft. A matriz operação por operação está em [beta8-2-writer-coverage-matrix.md](beta8-2-writer-coverage-matrix.md); priorização em [beta8-2-writer-risk-prioritization.md](beta8-2-writer-risk-prioritization.md).

Novas operações: grant obrigatório, CAS/fence, auditoria e retry idempotente. O teste também rejeitou `insert/update/delete` direto em `content_blocks` e `nodes`, e `insert` em `track_publications`, usando o usuário Mongo comum. POST de criação e PUT de nó retornam 503 sem a composição experimental explícita.

W-05 criação/reordenação; W-07 reordenação/exclusão; e as outras 15 famílias não foram migradas nesta fase. Exclusões e publicação permanecem adiadas por risco/decisão. Nenhum writer foi declarado globalmente contido. O usuário Mongo de autoridade ainda pode escrever diretamente nas coleções permitidas.

## O–X. Autoridade e credenciais

As negativas de privilégio MongoDB foram persistentes e exercitaram identidades sintéticas. O preparador conseguiu persistir staging Beta 5 e foi negado no namespace de promoção; a identidade comum não conseguiu mutar conteúdo/publicação.

**Process isolation não foi demonstrado:** FastAPI roda por ASGI no mesmo processo do harness, que abre simultaneamente clients runtime, authority e staging e injeta o client authority no boundary. Portanto, isto comprova `DATABASE_PRIVILEGE_VERIFIED`, `APPLICATION_AUTHORIZATION_VERIFIED` e `PROTOCOL_ENFORCEMENT_VERIFIED` no harness; não comprova isolamento forte de processo/segredos. Distribuição operacional de credenciais é `NOT_VERIFIED`.

**Entrega B — veredito:** `ISOLAMENTO DA AUTORIDADE PARCIALMENTE VALIDADO — FRONTEIRAS PENDENTES`.

## Y–AE. Staging, recuperação, gerações e aprendizagem

O bridge reutiliza `CurriculumStagingService` Beta 5 e `Beta8_1StagingAuthorityBridge`. No banco descartável, a prova cobriu lote completo; retry idempotente; falha injetada entre documento e checkpoint com estado recuperável; retry após confirmação com resposta artificialmente perdida; duas transições simultâneas (um vencedor, um conflito); revogação antes do commit; e preservação da geração anterior. O preparador foi negado ao tentar escrever no head experimental. Não houve chamada a rota/coleção operacional de publicação.

As falhas foram injetadas; encerramento abrupto natural de processo, falha espontânea de rede e recuperação operacional não foram provados. Staging e transição C8 não formam uma transação distribuída única; há janela recuperável entre a preparação e o commit.

Rubrica real do projeto 3.5 continua `PROPOSED`; conclusão pedagógica permanece bloqueada. Nenhum currículo real foi importado/promovido nesta fase. Não houve mudança no frontend nem em serviços de aprendizagem; a prova Beta 8 base e a prova Beta 8.1 de auth/aprendizagem foram repetidas como regressões persistentes.

**Entrega C — veredito:** `RECUPERAÇÃO E CONCORRÊNCIA DO STAGING VALIDADAS NO ESCOPO EXPERIMENTAL`, restrito aos pontos exercitados.

## AF–AG. Verificações executadas

* Docker Desktop Linux Engine 29.8.2; MongoDB 7.0.43 fixado; replica set `rsB8` descartável.
* Rede interna exclusiva, sem portas publicadas; `/data/db`, `/data/configdb` e `/run/mongo` em tmpfs; sem volume persistente. Gate validou IDs, labels e ownership antes de conectar/migrar/semear/escrever.
* Pytest no contêiner: **7 testes offline aprovados** (regressões Beta 8.1 mais contratos Beta 8.2) e **prova persistente integrada aprovada** nos cenários listados. Falhas intermediárias de desenvolvimento foram corrigidas antes da execução final; resultados finais descritos acima.
* `compileall` passou nos módulos/testes alterados; `git diff --check` passou.
* Ruff e MyPy não foram executados (não fazem parte da imagem mínima); frontend/typecheck/lint/build e Playwright não foram executados, pois não houve mudança frontend e o escopo desta prova foi backend/staging.
* Não foi executada a suíte completa histórica do backend; seus testes persistentes não foram inspecionados/executados em massa nesta fase.
* As execuções Docker encerraram com revalidação de ownership; contêiner, rede e imagem temporária foram removidos. Nenhum banco preexistente foi acessado.

**Entrega D — veredito:** `REGRESSÕES E SEGURANÇA PARCIALMENTE VALIDADAS — EVIDÊNCIAS PENDENTES`.

## AH–AJ. Segurança editorial, gates e arquivos

Não houve acesso a produção, staging operacional, Coolify, GHCR, credenciais reais ou curso original. Nenhuma publicação/promoção operacional ocorreu. Nenhum documento em `docs/courses/trilhacode/` ou `docs/migracao/` foi alterado.

Os estados históricos Beta 8.1 permanecem: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 NOT_VERIFIED; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. ADR-008 permanece **BLOCKED**. A rubrica 3.5 continua **PROPOSED**.

Arquivos de implementação/teste: `backend/curriculum_contract/experimental_editorial_grants.py`, `backend/curriculum_contract/experimental_editorial_iam_authority.py`, `backend/services/beta8_editorial_enforcement.py`, `backend/services/blocks.py`, `backend/services/nodes.py`, `backend/routes_content.py`, `backend/services/beta8_1_staging_authority.py`, `backend/services/beta8_curriculum_promotion.py`, `backend/integration_tests/beta8_1_runtime_security.py`, `backend/integration_tests/beta8_2_security.py`, `backend/unit_tests/test_beta8_2_writer_containment.py`, `ops/beta8-2-security/`.

Documentação: este relatório, [beta8-2-writer-coverage-matrix.md](beta8-2-writer-coverage-matrix.md), [beta8-2-writer-risk-prioritization.md](beta8-2-writer-risk-prioritization.md), [beta8-2-editorial-authority-process-isolation.md](beta8-2-editorial-authority-process-isolation.md) e [beta8-2-staging-recovery-design.md](beta8-2-staging-recovery-design.md).

## AK–AM. Limitações e próximo incremento

1. Isolar autoridade em processo próprio e remover URI/client privilegiado do processo comum; proteger o RPC com identidade verificável e comandos fechados.
2. Fazer inventário autorizado de distribuição operacional de credenciais e privilégios, sem inferi-los dos testes sintéticos.
3. Migrar writers restantes por risco, cobrindo criação, atualização, exclusão quando a política de retenção estiver aprovada, importação real e geração/publicação somente após cutover e ADR-008.
4. Executar suíte histórica segura, Playwright/regressão de aprendizagem se a composição de runtime for alterada e provas operacionais somente após autorização separada.
5. Completar evidências ADR-008: identidades/configuração efetivas, secrets, topologia, privilégios, backup/restore, incidente/revogação, observabilidade, auditoria e rollback.

## Vereditos por entrega

* A: `CONTENÇÃO DOS WRITERS PARCIALMENTE AMPLIADA — CAMINHOS PENDENTES`.
* B: `ISOLAMENTO DA AUTORIDADE PARCIALMENTE VALIDADO — FRONTEIRAS PENDENTES`.
* C: `RECUPERAÇÃO E CONCORRÊNCIA DO STAGING VALIDADAS NO ESCOPO EXPERIMENTAL`.
* D: `REGRESSÕES E SEGURANÇA PARCIALMENTE VALIDADAS — EVIDÊNCIAS PENDENTES`.

**Veredito global:** `BETA 8.2 PARCIALMENTE VALIDADA — WRITERS, AUTORIDADE OU RECUPERAÇÃO PENDENTES`.

Este resultado não autoriza homologação operacional, publicação, merge, push ou deploy.
