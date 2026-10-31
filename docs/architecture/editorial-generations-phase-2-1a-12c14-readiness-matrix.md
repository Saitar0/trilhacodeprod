# Fase 2.1A.12C.14 — Matriz de prontidão

Esta matriz é estruturada em [`editorial-generations-phase-2-1a-12c14-readiness.json`](editorial-generations-phase-2-1a-12c14-readiness.json), validada por teste offline. Ela não mede implantação, atividade de runtime, cobertura de ferramentas externas ou segurança de produção.

## Estados

* `SATISFIED_IN_ISOLATION`: teste/contrato concluído no escopo isolado; não significa operacional.
* `OPERATIONALLY_VERIFIED`: permitido somente com evidência operacional obtida por autorização. Não usado na C14.
* `PENDING_DECISION`: falta decisão de owner, produto, privacidade ou IAM.
* `PENDING_TEST`: contrato ainda requer teste explicitamente identificado.
* `BLOCKED`: há dependência/evidência impeditiva, inclusive ADR-008 ou bypass não contido.
* `NOT_APPLICABLE_WITH_RATIONALE`: exceção explicada e verificável.

## Resumo dos requisitos

| ID | Domínio | Estado | Responsável | Bloqueio principal | Próxima ação |
|---|---|---|---|---|---|
| R-01 | Fonte primária de grants | PENDING_DECISION | Owner + autoridade IAM | Nenhuma fonte/esquema operacional aprovado | Deliberar fonte única e ciclo de vida |
| R-02 | Concessão, delegação e revogação | PENDING_DECISION | Owner + IAM | Aprovadores e separação de deveres não nomeados | Aprovar matriz de responsabilidades |
| R-03 | Escopo global administrativo | PENDING_DECISION | Owner + IAM | Processo explícito de provisionamento/recuperação ausente | Aprovar scope explícito ou rejeitá-lo |
| R-04 | Ordenação de revogação | PENDING_DECISION | Owner + IAM | Matriz global de permissões é código estático | Aprovar policy epoch ou drenagem por release |
| R-05 | Transação com estado IAM real | BLOCKED | Owner + ops | Dados e topology reais não verificados; ADR-008 bloqueado | Obter baseline pelo processo autorizado |
| R-06 | Separação de IAM, capability e fence | SATISFIED_IN_ISOLATION | Segurança | Integração real ausente | Preservar contrato; requer nova autorização |
| R-07 | CAS, fence, audit e idempotência | SATISFIED_IN_ISOLATION | Arquitetura/owner | Nenhum writer ativo usa contrato C8/C10 | Revalidar no baseline aprovado |
| R-08 | Inventário estático dos 17 writers | SATISFIED_IN_ISOLATION | Arquitetura | Runtime e operadores permanecem NOT_VERIFIED | Reconciliar após baseline |
| R-09 | Contenção de writers no mesmo scope | BLOCKED | Arquitetura + ops | Import, restore, publish, delete, seed e outros podem disputar conteúdo | Provar conformidade ou bloqueio de cada path |
| R-10 | Contrato HTTP/clients antigos | PENDING_DECISION | Produto/API | Revisão/idempotência/receipt divergem da rota ativa | Aprovar versão e compatibilidade |
| R-11 | ACL, retenção, HMAC e privacy | PENDING_DECISION | Produto/segurança/privacidade | Retenção, readers e rotação não decididos | Aprovar matriz de dados e chaves |
| R-12 | Snapshot unit safety | SATISFIED_IN_ISOLATION | Arquitetura | Não cobre source-revision, publicação, reader pinning ou aluno | Planejar testes de concorrência em nova fase |
| R-13 | Progress/attempts/generation do aluno | PENDING_DECISION | Produto de aprendizagem | Delete/restore/withdrawal sem decisão final | Aprovar semântica e cobertura |
| R-14 | Seleção de primeira onda | BLOCKED | Owner + arquitetura | Nenhum candidato seguro sem completar dependências | Não iniciar cutover |
| R-15 | Rollback ensaiado | BLOCKED | Ops + owner | Não há alvo autorizado para rehearsal | Planejar e ensaiar após R-05/R-09 |
| R-16 | Baseline ADR-008 | BLOCKED | Operações + owner | SHA/digest e readiness implantados não verificados | Usar solicitação administrativa aprovada |
| R-17 | Autorização específica | PENDING_DECISION | Owner | C14 exclui implementação operacional | Pedir nova autorização após fechamento dos gates |

## Critérios de entrada da onda operacional

Os 18 requisitos da solicitação são agrupados sem esconder suas dependências:

1. Fonte grants aprovada: R-01 `PENDING_DECISION`.
2. Governança aprovada: R-02 `PENDING_DECISION`.
3. Scope de administrador aprovado: R-03 `PENDING_DECISION`.
4. Revogação definida e ordenável para todos estados: R-04 `PENDING_DECISION`, R-05 `BLOCKED`.
5. Sessão/role global revalidável no commit: R-05 `BLOCKED`; política de permissão estática também R-04.
6. Capability confiável: R-06 `SATISFIED_IN_ISOLATION`, sem integração operacional.
7. Revisão/fencing definidos: R-07 `SATISFIED_IN_ISOLATION`.
8. Auditoria obrigatória: R-07 `SATISFIED_IN_ISOLATION`.
9. Idempotência: R-07 `SATISFIED_IN_ISOLATION`.
10. Compatibilidade HTTP: R-10 `PENDING_DECISION`.
11. Escritores concorrentes: R-08 `SATISFIED_IN_ISOLATION` estático; runtime `NOT_VERIFIED`.
12. Bypasses contidos: R-09 `BLOCKED`.
13. ACL/retention: R-11 `PENDING_DECISION`.
14. Testes: R-12 snapshot isolado aprovado; persistência/concor­rência operacional pendentes de baseline.
15. Rollback: R-15 `BLOCKED`.
16. Progresso e tentativas: R-13 `PENDING_DECISION`.
17. ADR-008: R-16 `BLOCKED`.
18. Autorização da implementação: R-17 `PENDING_DECISION`.

Os estados desta matriz são consumidos automaticamente pelo teste de contrato. Nenhuma linha está `OPERATIONALLY_VERIFIED`; a matriz de gates permanece intocada.
