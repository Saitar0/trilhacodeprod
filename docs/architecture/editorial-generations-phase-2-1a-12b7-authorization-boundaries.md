# Fase 2.1A.12B.7 — Limites de autorização

Esta matriz descreve apenas a autorização da fase atual e a separação que deve ser mantida em fases futuras. Uma direção arquitetural aprovada em princípio não amplia permissões operacionais.

## 1. Autorização desta fase

| Atividade | Estado nesta fase | Delimitação |
|---|---|---|
| Análise documental | AUTORIZADA | Ler artefatos técnicos já disponíveis localmente. |
| Registro das deliberações humanas fornecidas | AUTORIZADO | Registrar fielmente escopo, limites e pendências; sem assinatura/autenticação não ocorrida. |
| Criar Markdown em `docs/architecture/` | AUTORIZADO | Somente documentos novos; não sobrescrever artefatos anteriores. |
| Commit local documental | AUTORIZADO | Somente Markdown novo da Fase 12B.7. |
| Alterar ADRs originais ou matriz original | NÃO AUTORIZADO NESTA FASE | Permanecem `Proposed` e `PENDING_APPROVAL`; registro novo é separado. |
| Alterar código funcional ou testes executáveis | NÃO AUTORIZADO | Nenhuma implementação. |
| Alterar schemas/DTOs/APIs/frontend | NÃO AUTORIZADO | Nenhuma alteração de runtime ou contrato implementado. |
| Migração/backfill/GC/dados reais | NÃO AUTORIZADO | Nenhuma alteração ou leitura de banco real. |
| Criar/ativar feature flags | NÃO AUTORIZADO | Todos os conceitos permanecem planejamento. |
| Acessar Coolify/GHCR/staging/produção | NÃO AUTORIZADO NESTA FASE | ADR-008 permanece bloqueado; usar apenas handoff sanitizado do administrador em fase futura. |
| Alterar infraestrutura, deployment, secrets ou Coolify | NÃO AUTORIZADO | Nenhuma mudança operacional. |
| Executar workflows, Docker ou MongoDB | NÃO AUTORIZADO | Nenhuma execução. |
| Push, PR, merge, rebase ou alteração remota | NÃO AUTORIZADO | Commit local apenas. |
| Cutover/rollback operacional | NÃO AUTORIZADO | Requer baseline, gates e autorização de operação específica. |

## 2. Níveis de aprovação para trabalhos futuros

| Nível | O que decide | O que não concede |
|---|---|---|
| Aprovação de princípios | Direção arquitetural geral de um ADR | Não aprova schema/API/contrato executável nem código |
| Aprovação de contrato técnico | Campos, invariantes, erros, versionamento, testes e compatibilidade | Não permite executar migração ou deploy |
| Autorização de implementação isolada | Um escopo de código, branch/base, arquivos e verificações locais definidos | Não permite dados reais, staging/produção ou publicação sem autorização separada |
| Autorização de migração/backfill | Plano, dados/coleção, idempotência, observabilidade e parada definidos | Não permite cutover público por implicação |
| Autorização operacional de staging | Ambiente, artefato, janela, rollback e owner definidos | Não permite produção |
| Autorização de deployment/cutover | Evidência dos gates, destino e aprovação do owner | Não reabre qualquer escopo não declarado |
| Autorização de GC/exclusão | Política, referências, privacidade/legal, escopo e recuperação aprovados | Não se infere dos princípios de ADR-004 |

## 3. Restrições preservadas

- O checkout original e outras worktrees não são alterados.
- `docs/courses/trilhacode/` e `docs/migracao/` não são materializados ou modificados.
- Não integrar `migracao-estrutura`.
- Não alterar o executor MongoDB independente.
- Não interpretar homologação da PoC como autorização ou prova de integração real.

Registro consolidado: [deliberações humanas](./editorial-generations-phase-2-1a-12b7-human-decision-register.md). Estados dos gates: [matriz técnica/operacional](./editorial-generations-phase-2-1a-12b7-implementation-gates.md).
