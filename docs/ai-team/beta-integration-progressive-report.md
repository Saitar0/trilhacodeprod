# Integração progressiva Beta 1–9

## Fundação

- PR #38 permanece aberto: `codex/foundation-ci-e2e-recovery` em `86cf85e6`.
- Estado: `MERGEABLE`, sem aprovação registrada, checks obrigatórios verdes, deploys pulados.
- A fundação não foi mesclada na `main`; esta onda usa a branch de fundação como base.
- Alertas Dependabot estão desabilitados no repositório; nenhum alerta foi inventado a partir dessa ausência.

## Matriz consolidada

| Incremento | Branch / referência | Estado verificado | Classificação |
| --- | --- | --- | --- |
| Beta 1 | `codex/beta1-platform-course-readiness-audit` / `e801cee8` | Auditoria e inventário; curso ainda draft, sem jornada ponta a ponta | PRECISA DE CORREÇÃO |
| Beta 2 | `codex/beta2-curriculum-import-proof` / `497e2a32` | Importação piloto e proveniência isoladas | EXPERIMENTAL |
| Beta 3 | `codex/beta3-curriculum-fidelity-recovery` / `68cd396f` | Fidelidade e recuperação em cenários controlados | EXPERIMENTAL |
| Beta 4 | `codex/beta4-first-phase-curriculum-validation` / `3e7c1a87` | Conversão da Fase 1; índices e destinos operacionais ainda pendentes | PRECISA DE CORREÇÃO |
| Beta 5 | `codex/beta5-safe-curriculum-foundation` / `828e8bbb` | Contratos protegidos e staging isolado; sem publicação | PRONTO PARA INTEGRAR EM LOTES |
| Beta 6 | `codex/beta6-first-learning-journey` / `e31486ad` | Jornada original bloqueada antes da prova HTTP | BLOQUEADO |
| Beta 6.1 | `codex/beta6-1-http-e2e-validation-isolated` / `c486fa7f` | Jornada HTTP/Chromium isolada validada | PRONTO PARA INTEGRAR APÓS CI |
| Beta 7 | `codex/beta7-first-phase-learning-hardening` / `e671375e` | Hardening parcial; cobertura e conteúdo real incompletos | PRECISA DE CORREÇÃO |
| Beta 7.1 | `codex/beta7-1-real-curriculum-preview` / `2202905a` | Preview das dez unidades em ambiente isolado | PRONTO PARA INTEGRAR COMO PREVIEW |
| Beta 7.2 | `codex/beta7-2-versioned-project-assessment` / `47a48c71` | Rubrica real ainda proposta; aprovação operacional ausente | BLOQUEADO |
| Beta 8 | `codex/beta8-iam-editorial-enforcement` / `6a4beafe` | Contratos IAM/CAS testados, enforcement operacional incompleto | PRECISA DE CORREÇÃO |
| Beta 8.1 | `codex/beta8-1-runtime-editorial-integration` / `23e985d9` | Endpoints HTTP selecionados com grants e replay | PRONTO PARA INTEGRAR LIMITADO |
| Beta 8.2 | `codex/beta8-2-editorial-writer-containment` / `167166e3` | Apenas parte dos writers contida | PRECISA DE CORREÇÃO |
| Beta 8.3/8.4 | `aa84b209` / `e3c44637` | Laboratório de autoridade isolada e recuperação | EXPERIMENTAL |
| Beta 9 | `codex/beta9-integrated-validation-and-writers` / `e294c68d` | Branch-only, sem relatório final ou CI publicável | BLOQUEADO |

## Grafo e ordem recomendada

```text
Beta 1 -> Beta 2 -> Beta 3 -> Beta 4 -> Beta 5 -> Beta 6.1
                                                -> Beta 7.1
Beta 7.1 -> Beta 7.2 (rubrica aprovada)
Beta 8 -> 8.1 -> 8.2 -> 8.3 -> 8.4
Beta 7.1 + 7.2 + 8.3/8.4 -> Beta 9
```

As dependências são cumulativas, mas não autorizam cherry-pick indiscriminado. Os commits de isolamento/staging Beta 5 dependem de índices, conversores e fixtures das Betas 2–4; por isso não foram portados nesta primeira onda.

## Primeira onda executada

- PR: #39
- Base: `codex/foundation-ci-e2e-recovery`
- Branch: `codex/beta5-contracts-integration-wave1`
- Commit original portado: `b868c728`
- Escopo: contratos de conteúdo protegido, metadados curriculares, critérios e artefatos do projeto 3.5.
- Fora do escopo: staging, Mongo harness, writers, IAM, publicação e C14–C16.
- Testes locais: 8 testes direcionados passaram em venv isolado.
- CI: workflow `41082490518` passou Backend/MongoDB, Frontend, Docker/G2, Playwright E2E e resumo.

## Gates preservados

O baseline curricular, a migração operacional, os 17 writers, grants/IAM operacionais, ADR-008, staging e produção permanecem bloqueados. A primeira onda não transforma contratos sintéticos em conteúdo publicado nem autoriza merge automático.

## Próxima onda

Revisar e, se autorizado, preparar Beta 6.1 como lote separado após repetir sua validação HTTP/Chromium sobre a base de fundação. A migração/staging Beta 5 somente deve avançar em lote próprio, com adaptação explícita para os índices e conversores das Betas 2–4.
