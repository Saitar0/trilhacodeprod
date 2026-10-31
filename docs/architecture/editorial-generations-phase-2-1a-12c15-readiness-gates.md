# Fase 2.1A.12C.15 — Matriz de prontidão para enforcement

Esta matriz separa políticas ratificadas de contratos propostos, provas isoladas e bloqueios operacionais. Não mede runtime nem promove os gates. A versão estruturada é [`editorial-generations-phase-2-1a-12c15-enforcement-contract.json`](editorial-generations-phase-2-1a-12c15-enforcement-contract.json), validada offline por teste C15.

## Estados

* `ARCHITECTURAL_POLICY_APPROVED`: diretriz explicitamente autorizada; não é implementação.
* `TECHNICAL_DESIGN_PROPOSED`: contrato recomendado, ainda sem aprovação operacional/técnica final.
* `VERIFIED_IN_ISOLATION`: evidência de teste isolado anterior; não representa runtime.
* `PENDING_PRODUCT_DECISION`, `PENDING_SECURITY_DECISION`: depende do decisor indicado.
* `PENDING_OPERATIONAL_EVIDENCE`: depende de baseline/ambiente autorizado.
* `BLOCKED`: impede habilitar mutação até resolução.

Nenhum requisito está `OPERATIONALLY_VERIFIED`.

## Requisitos e estado

| ID | Requisito | Estado C15 | Responsável restante | Evidência/critério de fechamento |
|---|---|---|---|---|
| R-01 | P1–P8 formalizadas | `ARCHITECTURAL_POLICY_APPROVED` | Owner do projeto | Diretrizes registradas e aprovadas para desenho; nova decisão necessária para execução. |
| R-02 | Fonte primária/schema de grants | `PENDING_PRODUCT_DECISION` | Owner + autoridade IAM | Escolher autoridade única, lifecycle, referências, índices, owner e concorrência; sem coleção operacional nesta fase. |
| R-03 | Responsabilidade/grant/delegação/recuperação | `PENDING_PRODUCT_DECISION` | Owner + IAM | RACI nominal, anti-escalonamento e separação de funções aprovados. |
| R-04 | Admin scope global explícito | `PENDING_SECURITY_DECISION` | Security + IAM + owner | Provisionador/revogador independente, audit e recovery aprovados; admin sem wildcard por papel. |
| R-05 | Revogação ordenada com grant/role/session/user | `VERIFIED_IN_ISOLATION` | Arquitetura + IAM + ops | C11/C12 sintético demonstrou mesma transação; falta prova no baseline real. |
| R-06 | Matriz estática versionada/drain | `TECHNICAL_DESIGN_PROPOSED` | IAM + arquitetura + ops | Aprovar transição híbrida e provar que todos writers consultam epoch ou foram drenados. |
| R-07 | Capability server-issued separada de fence/revision | `VERIFIED_IN_ISOLATION` | Segurança | C11/C12 negativo sintético; integrar somente após autorização e revalidar epoch na confirmação. |
| R-08 | CAS/fencing/auditoria/idempotência | `VERIFIED_IN_ISOLATION` | Arquitetura + owner | C8–C12 isoladas; nenhum writer operacional consome o contrato. |
| R-09 | Compatibilidade HTTP/clientes | `PENDING_PRODUCT_DECISION` | Product/API | Contrato versionado, If-Match, idempotência, null/absent, erros/replay e período de transição. |
| R-10 | Privacidade/ACL/retenção/HMAC | `PENDING_SECURITY_DECISION` | Privacy + security + owner | Matriz por classe, readers, retenção, exclusão, rotação/perda de chave aprovadas. |
| R-11 | Inventário de 17 writers | `VERIFIED_IN_ISOLATION` | Arquitetura + ops | Código/símbolos C13 revalidados C14; runtime e operadores `NOT_VERIFIED`. |
| R-12 | Contenção same-scope de bypasses | `BLOCKED` | Arquitetura + ops | Todos os caminhos adaptados ou tecnicamente incapazes, com evidência no target. |
| R-13 | Publicação/snapshot/readers | `BLOCKED` | Arquitetura + produto | Snapshot de revisão única, geração/head atômicos, reader pinning e atividade testados. |
| R-14 | Tentativas/progresso/gerações | `PENDING_PRODUCT_DECISION` | Learning/product + arquitetura | Política de delete/restore/withdrawal e testes sem perda de estado do aluno. |
| R-15 | Auditoria de autoridade/editorial atomicamente definida | `TECHNICAL_DESIGN_PROPOSED` | Security + produto | Schema mínimo, fail semantics, ACL/retention e teste persistente no target. |
| R-16 | Baseline ADR-008 | `BLOCKED` | Ops + owner | SHA/digest, schema, topology, drivers, roles, indexes e readiness por processo autorizado. |
| R-17 | Rollback ensaiado | `BLOCKED` | Ops + owner | Pausa, bloqueio de writers velhos, reconciliação e preservação de revogações provados. |
| R-18 | Primeira onda segura selecionada | `BLOCKED` | Owner + arquitetura | C14 não selecionou onda; revisar só depois de fechar R-02–R-17 e reconciliar callers externos. |
| R-19 | Regressões e critérios de aceite de integração | `PENDING_TEST` | Arquitetura + QA + security | Unit/persistência/concorrência/leitores no baseline futuro; testes históricos C14 não substituem. |
| R-20 | Autorização específica de implementação/implantação | `PENDING_PRODUCT_DECISION` | Owner | Autorizações separadas definem scope, branch, environment, testes, rollback e proibidos. |

## Bloqueadores automáticos

Manter mutações editoriais operacionais bloqueadas se qualquer um de R-02, R-03, R-04, R-06, R-09, R-10, R-12, R-13, R-14, R-16, R-17 ou R-20 não estiver fechado com evidência apropriada. O validador offline apenas detecta lacunas na especificação; não aprova pessoas, IAM ou ambiente.

## Critérios de entrada/saída

Entrada: fonte e governança aprovadas; admin/delegação/revogação definidos; papel/sessão/usuário/policy version ordenados; capability confiável; HTTP e privacidade aprovados; writers concorrentes enumerados e contidos; auditoria/CAS/fence/idempotência; comportamento de snapshots/aluno; rollback; regressões; baseline ADR-008; autorização exata.

Saída futura: negar escrita sem grant, após revogação, sem permissão, com sessão inválida, capability forjada, revision/fence stale; replay não duplicar; auditoria falhar aborta; commit indeterminado reconciliado; nenhum payload privado vazar; nenhum writer antigo confirmar; nenhum snapshot/publication parcial; progresso/tentativas preservados; API contratada; rollback ensaiado e suites por camada aprovadas.

## Gates históricos preservados

| Gate | Estado |
|---|---|
| G1 | PARTIAL |
| G2 | NOT_VERIFIED |
| G3 | NOT_VERIFIED |
| G4 | PARTIAL |
| G5 | NOT_VERIFIED |
| G6 | PARTIAL |
| G7 | PARTIAL |
| G8 | NOT_VERIFIED |
| G9 | BLOCKED |
| G10 | BLOCKED |
| ADR-008 | BLOCKED |
