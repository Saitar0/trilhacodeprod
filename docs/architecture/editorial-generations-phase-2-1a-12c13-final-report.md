# Fase 2.1A.12C.13 — Relatório final

**Veredito: GOVERNANÇA EDITORIAL PARCIALMENTE ESPECIFICADA — COBERTURA OU DECISÕES PENDENTES.** O IAM versionado foi rastreado, 17 caminhos/helpers foram catalogados, a proposta de governança e as ondas de integração foram documentadas, e os contratos offline C13 passaram. O runtime e writers externos continuam não verificados; integração operacional não autorizada.

## A. Resultado executivo

O backend tem identidade autenticada por JWT, validação de sessão persistida e permissões globais derivadas de uma matriz estática de papel. Não foi encontrado grant de escrita por trilha. Portanto, `content.write` não oferece o escopo necessário para proteger edição por recurso.

Recomendo explicitamente não atribuir escopo global implícito ao papel `admin`. O modelo a deliberar é uma autoridade primária de grants por trilha, com delegação limitada, epochs monotônicos, auditoria obrigatória e ordenação no limite de confirmação. C11/C12 mostraram ordering somente com registros sintéticos participantes da mesma transação; a fonte real, a governança e o runtime não foram comprovados.

O inventário estático identificou 17 linhas: **6 A** (adaptar), **8 B** (bloquear/restringir), **1 C** (fora do protocolo somente em namespace PoC isolado) e **2 D** (decisões/investigação). O maior bloqueio é coexistência de writers que compartilham coleções e ainda não usam revisão, fence e auditoria comuns, em particular publicação, import, restore e operações de exclusão.

## B. Git e isolamento

* Base exata: `ff9cf18d0751d06d3362716372b4ea88d143a0b6`, parent `a9b9c69eccf50f3d5713e4b55533b39210785635`.
* Branch: `codex/fase2-1a-12c13-editorial-governance-writers`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c13-editorial-governance-writers\trilhacodeprod`.
* Checkout original e outras worktrees não foram alterados; somente commits locais serão criados. Sem push, PR, merge, rebase ou deploy.
* Sparse checkout foi configurado antes de materializar `backend`, `docs/architecture` e `scripts`. `docs/courses/trilhacode/` e `docs/migracao/` permaneceram ausentes.
* Hash(es) do commit local: registrados no histórico final da branch após o commit; sem alterações pendentes ao encerrar.

## C. IAM, grants e papéis

`security.current_user` valida JWT, sessão, conta e versão do token e lê usuário/papel atual ([`security.py`](../../backend/security.py#L75-L110)); a sessão persistida tem TTL de sete dias e `revoked_at` ([`sessions.py`](../../backend/services/sessions.py#L13-L83)); a matriz de papel é estática ([`constants.py`](../../backend/constants.py#L5-L16)). Mudança de role requer `users.manage` e atualiza `users.role` ([`routes_auth.py`](../../backend/routes_auth.py#L281-L283), [`auth.py`](../../backend/services/auth.py#L221-L228)).

O código não demonstrou grant por trilha nem escopo global administrativo explícito. `can_view_track` é regra de leitura/visibilidade, não autorização de escrita por trilha ([`permissions.py`](../../backend/permissions.py#L21-L31)). C13 propõe permissão global necessária **e** grant da trilha/operação resolvida pelo servidor. Capability deve ser emitida somente após autorização confiável e não deve ser fornecida pelo cliente; fencing/idempotência não são IAM.

Governança proposta: autoridade IAM designada emite o grant inicial e nomeia responsáveis; responsável delega somente subconjunto do próprio escopo; autoconcessão e delegação superior são proibidas; revogador emergencial, se aprovado, é deny-only. `admin` não recebe wildcard pelo nome. Escopo global requer provisionamento explícito, auditoria e recuperação por autoridade independente. Esses são papéis conceituais, não papéis ativos.

Matriz de operação/permissão atual, grant futuro e auditoria consta em [governança de grants](editorial-generations-phase-2-1a-12c13-grant-governance.md). Retenção, dupla aprovação, expiração, break-glass, policy epoch e donos humanos permanecem decisões pendentes.

## D. Fonte de autoridade e revogação

C12 recomenda uma autoridade primária por ator/escopo e demonstrou que grant, papel/sessão sintéticos e edição podem ordenar quando participam da mesma transação Mongo. Uma verificação IAM externa ou projeção eventual não dá essa garantia: pode ocorrer revogação entre check e commit. Epoch ajuda somente se sua leitura é atual e sua alteração participa do mesmo limite de ordenação. C13 não escolheu coleção operacional nem alterou IAM.

Política preservada: revogação confirmada antes do commit impede a edição; commit anterior à revogação permanece historicamente válido. Para estender isso a grant, papel/política, sessão, usuário desativado e escopo global, cada estado revogável precisa participar do commit ou de coordenador com prova de ordem equivalente. Garantia de corrida sintética não confirma URI, topologia, schema, índices, roles ou runtime.

## E. Escritores e invariantes

| Classe | Quantidade | Exemplos | Disposição indicada |
|---|---:|---|---|
| A — adaptar | 6 | Track CRUD/reorder, node CRUD, block CRUD, relations, snapshot helpers, `audit()` | Usar revisão/CAS/fence onde aplicável, grant exato, idempotência e audit no limite de commit. |
| B — bloquear/restringir | 8 | Track/node delete, duplicaçōes, publish, import, restore, seed, migrations/CLI | Não habilitar no escopo até recovery, impacto sobre alunos, exclusão mútua e bypass serem resolvidos. |
| C — fora do protocolo justificado | 1 | PoC `editorial_generations_poc.py` | Isolado em namespace `poc_`, sem rota/ponteiro público encontrado; runtime externo ainda NOT_VERIFIED. |
| D — investigação/decisão | 2 | Taxonomia/tag global, preparação de publicação privada | Definir autoridade global/catálogo ou call graph/ACL antes de decidir adaptação. |

O [inventário C13](editorial-generations-phase-2-1a-12c13-writer-coverage-matrix.md) documenta símbolo, entrada, coleções, permissão atual, escopo, auditoria, CAS/fence/idempotência/transação, risco, evidência de teste, dependências e critérios de aceitação. O JSON estruturado permite checagem offline de ids, símbolos e referências.

Pontos críticos: `publish_track` escreve quiz, snapshot e status antes do CAS final em `tracks`; `restore` substitui em lotes sob job/lease, não fence aplicado a cada escrita; `run_import` usa lock/job próprios, mas toca várias coleções sem o fence compartilhado; `delete_tag` atualiza nodes/tracks globalmente em etapas; delete track/node alcança progresso, tentativas e outros registros de aluno; `audit()` insere em `edit_history` sem sessão explícita. C7 demonstrou alteração parcial de bloco quando falha auditoria. Estes são fatos de código/testes anteriores, não prova de execução atual.

## F. Threat model e segurança

A proposta documenta 16 ameaças: `content.write` cross-track; capability revogada/forjada; JWT com sessão invalidada; alteração de papel/grant em voo; `track_id` adulterado; fence usado como IAM; replay por outro ator ou após exclusão; writer legado bypass; audit ausente; commit indeterminado; recibo/histórico com conteúdo privado; projeção/cache stale e confusão entre identidade/permissão/grant/fence. Impactos são qualitativos, com precondição, mitigação e evidência, sem score numérico inventado.

Nenhum token, grant, conteúdo ou dado real foi consultado. O código e os contratos C13 não foram importados em routes/startup; nenhum writer foi executado nesta fase.

## G. Dependências, aluno e publicação

O grafo da matriz registra que publish depende de snapshot/versão e quiz; import também chama snapshot e escreve estrutura; restore usa apply_snapshot, save_version, reconciliação e audit; tag delete cruza tracks/nodes; deleções podem apagar progresso/attempts. Assim, um piloto de `update_block` só seria seguro quando qualquer writer que altere os mesmos blocks (delete/reorder/import/restore/clone/seed/CLI) for coordenado ou bloqueado para aquele escopo.

Preservar sessões do aluno vinculadas à geração original enquanto válida, histórico de tentativas e correções auditáveis; retirada emergencial deve ser explícita. Revisão editorial, generation imutável e public head são conceitos diferentes. A publicação precisa de generation completa e head atômico com leitores pinados (ADR-006); transação C8 de revisão sozinha não resolve leitura/publicação misturada.

## H. Ondas e rollback

A sequência [ondas C13](editorial-generations-phase-2-1a-12c13-integration-waves.md) é: (0) decisões de governança; (1) baseline ADR-008; (2) fonte e ciclo de vida de grants; (3) capability e contrato HTTP; (4) cobertura/contenção de todos writers por coleção; (5) write de conteúdo sob autoridade única; (6) estrutura e relações; (7) catálogo/import; (8) snapshots/restore/publicação/leitores; (9) expansão/cutover. Cada onda possui entrada, testes/saída, bloqueios e recovery.

Rollback futuro pausa a escrita e preserva grants revogados, receipts, audit e revisões confirmadas. Corrige-se com nova revisão, não apagando confirmação nem reabrindo writer sem CAS/fence. Feature flag não serializa writers antigos. Qualquer caminho externo desconhecido ou incapacidade de pausar/bloquear writers é bloqueio do primeiro cutover.

## I. Testes e qualidade

* C13: `pytest backend/integration_tests/test_editorial_grant_governance.py backend/integration_tests/test_editorial_writer_inventory.py -q` — **11 aprovados**.
* Regressões offline selecionadas (C1 protocol, C2 adapter unit, C5 observability, C10 API contract, C11 authorization unit, PoC/immutable publication): **117 aprovados, 26 subtests aprovados, 1 teste deliberadamente desmarcado** (`test_operation_index_is_unique_and_recovery_index_is_declared` importa `indexes` e requer `pydantic_settings` ausente no venv herdado C12). A execução completa também reportou esse teste falhando na coleta por dependência ausente, não defeito funcional.
* `backend/unit_tests/test_snapshot_safety.py` não pôde ser coletado pelo mesmo `ModuleNotFoundError: pydantic_settings`; não executado. Nenhuma instalação global foi modificada e o venv de C12 não foi alterado.
* Writer/testes persistentes C7–C12: não executados — fora do escopo de provar cobertura e sem necessidade de infraestrutura para esta fase.
* Ruff: aprovado nos dois testes novos. Mypy: aprovado nos dois arquivos novos. Verificação sintática por AST, links Markdown de três documentos técnicos e `git diff --check`: aprovados.
* Todos os arquivos de referência de teste indicados na matriz são testes encontrados no checkout, não testes executados por C13.

## J. Gates e ADR-008

Preservados, sem promoção: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 continua bloqueado. Nenhuma matriz histórica foi alterada.

## K. Arquivos e verificações de escopo

Criados exclusivamente:

* `backend/curriculum_contract/editorial_grant_governance_c13.json`
* `backend/integration_tests/editorial_writer_inventory_c13.json`
* `backend/integration_tests/test_editorial_grant_governance.py`
* `backend/integration_tests/test_editorial_writer_inventory.py`
* `docs/architecture/editorial-generations-phase-2-1a-12c13-grant-governance.md`
* `docs/architecture/editorial-generations-phase-2-1a-12c13-writer-coverage-matrix.md`
* `docs/architecture/editorial-generations-phase-2-1a-12c13-integration-waves.md`
* `docs/architecture/editorial-generations-phase-2-1a-12c13-final-report.md`

Não foram modificados routes, serviços, writers, IAM, schemas operacionais, configuração, workers, gates, ADRs ou conteúdo. Não houve acesso a banco, Docker, staging, produção, Coolify/GHCR ou rede operacional. Sem recursos descartáveis para limpar nesta fase.

## L. Limitações

1. Código versionado não revela writers externos, runtime, tráfego, imagem/digest ativos, agendadores, permissões de banco ou ferramenta de operador não versionada.
2. A matriz estática e seu teste de símbolo não equivalem à análise dinâmica de todos os call-sites nem à cobertura de produção.
3. Não há decisão humana sobre autoridade de grants, ownership, escopo global, delegação, expiração, recuperação, ACL, retention ou audit de negação.
4. C11/C12 demonstraram ordem somente com authorities sintéticas na mesma transação; não há prova com IAM/schema/topologia reais.
5. `pydantic_settings` ausente bloqueou duas verificações históricas de snapshot/index; 117 regressões offline selecionadas passaram.
6. Estados de gates históricos não podem ser atualizados por inventário documental.

## M. Próximo incremento recomendado

Realizar uma deliberação documentada com a autoridade IAM e o responsável editorial para decidir a fonte primária de grants, quem concede/revoga, se há escopo global e como papel/sessão/grant terão ordem com commit. Essa decisão é pré-requisito para definir schema e baseline; não pede integração operacional.

## N. Veredito

**GOVERNANÇA EDITORIAL PARCIALMENTE ESPECIFICADA — COBERTURA OU DECISÕES PENDENTES.** O repositório versionado foi mapeado e os contratos offline passaram; a cobertura do runtime, a fonte operacional de grants e as decisões de governança permanecem pendentes. Os writers não estão declarados protegidos e a integração continua não autorizada.
