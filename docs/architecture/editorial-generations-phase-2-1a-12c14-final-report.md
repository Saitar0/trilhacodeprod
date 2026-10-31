# Fase 2.1A.12C.14 — Relatório final

**Veredito: PRONTIDÃO EDITORIAL PARCIAL — PRIMEIRA ONDA CONDICIONADA A DECISÕES E EVIDÊNCIAS.** A recuperação de testes e a consolidação foram concluídas no escopo isolado. Não há base para selecionar ou iniciar uma primeira integração operacional.

## A. Resultado executivo

O snapshot unitário anteriormente bloqueado coletou e passou depois de criar um venv exclusivo com a dependência já declarada pelo projeto. A matriz estática dos 17 writers C13 passou suas checagens de símbolos, arquivos e referências. As provas anteriores de CAS, fencing, audit, idempotência e ordenação de autorização permanecem evidências isoladas; não são cobertura de runtime.

Não é seguro integrar `update_block` por si só: publicação, import, restore, exclusões, duplicação, seed e helpers compartilham conteúdo ou snapshots. Gestão isolada de grants também não protege writers que não os consultam; contrato passivo não é enforcement. Assim, a primeira onda operacional não foi selecionada.

## B. Git e isolamento

* Base obrigatória e parent do commit C14: `cf3326594f572cc4d17a03e998c2b8efaa0a1f94`; esse commit C13 tem parent `1138c1cf821923e739d5bbe419d0fe6120fde902`.
* Branch: `codex/fase2-1a-12c14-editorial-readiness`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-fase2-1a-12c14-editorial-readiness\trilhacodeprod`.
* O commit local C14 é documental e seu SHA é registrado na resposta de entrega (o próprio documento não inclui seu hash).
* Checkout original e outras worktrees não foram modificados. O sparse-checkout materializou somente `backend` e `docs/architecture`; `docs/courses/trilhacode/` e `docs/migracao/` permaneceram ausentes.
* Sem push, PR, merge, rebase, deploy, acesso a banco, Coolify, GHCR, staging ou produção.

## C. Decisões consolidadas

Princípios experimentais previamente aprovados: uma autoridade editorial única por trilha com revisão/CAS/fencing; auditoria funcional obrigatória na mesma transação; idempotência e reconciliação sem repetir mutação às cegas; publicação/head separado de revisão de trabalho. As provas C8–C12 demonstram esses contratos somente nos cenários sintéticos relatados.

Dependem de decisão humana: fonte primária dos grants, grantors/revokers/delegadores, scope administrativo, policy epoch para permissões globais estáticas, semântica de revogação externa, ACL/retention e gestão de HMAC, política de delete/progresso, contrato HTTP/clients antigos e a linha de integração/baseline. A síntese está em [decisões arquiteturais](editorial-generations-phase-2-1a-12c14-architecture-decisions.md).

## D. Fonte de grants e governança

Recomendação para deliberação: uma autoridade primária de grant por trilha, com scope explícito e lifecycle auditado, coordenada com a confirmação editorial ou com mecanismo de ordenação equivalente demonstrado. C12 provou que uma transação comum ordena registros sintéticos; contraexemplos de IAM externo/projeção stale demonstram limites. Não há coleção nem schema operacional escolhido.

Papéis atuais `admin`, `editor`, `student` têm matriz estática; admin/editor têm permissões globais de conteúdo, sem grant por trilha demonstrado. Não inferir que admin é wildcard ou que `users.manage` implica gerir grants. A proposta de governança exige delegação subconjunta, sem autoconcessão, e recuperação independente; owners humanos estão pendentes.

## E. IAM e revogação

O código versionado valida JWT, sessão persistida, status da conta, versão de token e papel a cada request; `PERMISSIONS` é calculado de matriz Python estática. Testes anteriores exercitaram verificadores com identidades sintéticas. Nenhuma identidade/sessão/grant implantada foi consultada.

Regra preservada: revogação confirmada antes do commit deve negar a edição; commit anterior permanece historicamente válido. Grant, usuário, sessão e scope administrativo persistidos precisam participar do limite transacional para garantia forte. A matriz de permissões em código requer epoch persistente ou drenagem coordenada de writers na troca de release; um grant epoch isolado não ordena mudança de papel ou de código.

## F. Privacidade

Receipt deve ser mínimo; history/audit/receipt/fingerprint têm finalidades e ACLs diferentes. HMAC é integridade e não cifra conteúdo. ACL, retenção, exclusão, rotação/perda/revogação de chaves e exposição de históricos permanecem decisões humanas; nenhum prazo legal foi presumido.

## G–H. Inventário e classificação dos escritores

Os 17 caminhos C13 foram revalidados offline no commit C14: todos os IDs e símbolos continuam presentes, arquivos e evidências estão válidos e runtime continua `NOT_VERIFIED`. Classificação preservada: **A=6, B=8, C=1, D=2**. C é somente PoC isolada com namespace separado; não significa prova de ausência em deployment. Detalhamento individual e caminhos está em [cobertura dos writers C13](editorial-generations-phase-2-1a-12c13-writer-coverage-matrix.md) e o resultado do teste C14 fica na [matriz de prontidão](editorial-generations-phase-2-1a-12c14-readiness-matrix.md).

Uma busca de operações C14 encontrou módulos adjacentes que escrevem estado do aluno (`progress.py`, `activities.py`, `submissions.py`, `learning.py`). Eles não são writers editoriais novos por definição, mas exclusões/publicação/restauração não podem corromper progresso, tentativas e sessões pinadas. A busca estática não prova cobertura completa de scripts/containers/operadores externos.

## I–J. Primeira onda e dependências

**Nenhuma onda selecionável com as evidências atuais.** W-07 bloco depende de contenção/coordenacão de W-02/03/04/06/10/11/13, snapshot W-12 e paths de operador não verificados. Publicação (W-04) e restore (W-11) exigem mais que revisão de bloco; publicação depende de snapshot/quiz/head/readers. Grants isolados não protegem os atuais writers. A alternativa C — contrato/verificador offline — é preparação de baixo risco, não integração. A comparação completa está no [documento de seleção](editorial-generations-phase-2-1a-12c14-first-wave-selection.md).

## K–L. Entrada, saída e rollback

Entradas bloqueadas incluem decisões humanas de grants/admin/revogação/privacy/API, baseline ADR-008, contenção de todos writers no scope, cobertura de progresso/attempts, testes persistentes/concorrentes aplicáveis e autorização específica. A saída de uma futura onda exige evidências unitárias, persistentes, concorrentes, snapshot/leitores e validação operacional autorizada.

Rollback é pausar novas entradas e bloquear os writers antigos, reconciliar commits/receipts, preservar auditoria/revisões/revogações e corrigir com nova revisão. Flag de rota não contém CLI, seed, jobs, import ou restore. Não repetir operações indeterminadas nem reabrir bypass. O ensaio operacional segue bloqueado até baseline ADR-008.

## M–N. Recuperação e snapshots

`pydantic-settings` consta em `backend/requirements.txt` e `requirements.prod.txt`; o venv anterior estava incompleto. Um venv Python 3.11 C14 com dependências do manifest e PyPI público recuperou `test_snapshot_safety.py`: **6 passed**. Cobertura: integridade estrutural, contagens, trilha, ledger de migração e volumes acima do limite antigo. Não cobre publicação atômica, concorrência com mutação, revisão da fonte, reader pinning nem progresso/aluno.

## O. Testes e regressões

* Snapshot isolado: **6 passed**, sem skips/coleta falha.
* Conjunto offline C14/C13 e protocolos: **183 passed, 38 subtests passed**, sem falhas/skips/deseleções. Inclui 5 testes C14 de prontidão, inventário e governança C13, IAM C12, C11 privacidade/autorização, C10 API, C2 adaptador offline, harness C6, C8 revisão, C5 observabilidade e C1 PoC/protocolo.
* Testes persistentes C3 e C7–C12 e compatibilidade persistente C9 não executados; nenhuma infraestrutura Mongo foi iniciada. Testes completos de serviços legados e publicação de ponta a ponta não foram executados nesta fase.
* Ruff 0.17.3: passou no teste Python novo. Mypy 2.4.0: sem issues no teste novo.
* JSON da matriz, compilação sintática, links relativos nos cinco Markdown C14, `git diff --check`, busca de padrões de credenciais e ausência de imports/referências em rotas/serviços operacionais: aprovados. O diff contém apenas sete arquivos novos dentro dos caminhos autorizados; diretórios protegidos ausentes.

Por fase: C13 inventário/governança offline aprovados; C12 IAM unitário aprovado; C11 autorização/privacidade unitária aprovada; C10 contrato HTTP unitário aprovado; C9 compatibilidade persistente não executada; C8 protocolo unitário aprovado; C7 persistente não executado; C6 harness offline aprovado; C5 observabilidade unitária aprovada; C3 persistente não executado; C2 adaptador offline aprovado; C1 protocolo e PoC offline aprovados. A seleção não substitui as suites completas.

## P. Segurança

Somente documentação e teste offline de contrato da matriz são novos. Nenhum endpoint, IAM, writer, configuração, migrador, dado ou conteúdo foi alterado. Nenhuma credencial, `.env` operacional, dado real, Mongo, Docker, staging, produção ou runtime foi acessado. A única conexão de rede foi a instalação autorizada de dependências do PyPI público; os testes não acessaram rede nem banco. A instrumentação/experimentos anteriores não foram importados por rotas/startup.

## Q. Gates

Preservados: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 segue `BLOCKED`. Matriz histórica não foi modificada.

## R–V. Arquivos e limpeza

Documentos criados: decisões, seleção da onda, matriz de prontidão, recuperação de testes e relatório final; foi criado JSON estruturado e um teste offline para validar IDs, estados, dependências, fontes, cobertura C13 e gates. Nenhum documento C8–C13 foi alterado. Venv é externo ao repositório; nenhum recurso persistente precisa de limpeza.

## W. Limitações e próximo incremento

Faltam decisões de produto/IAM/privacidade, baseline/runtime autorizado, grants reais, roles/índices/topology, cobertura de operadores externos, contenção de bypasses, testes integrados do scope, ACL/retention e rollback operacional. Próximo passo recomendado: o responsável e a autoridade IAM deliberarem fonte primária dos grants, autoridades de concessão/revogação, scope admin, revogação de matriz estática e privacy/API; depois solicitar baseline pelo processo ADR-008. Não começar integração até atualizar a matriz.

## X. Veredito

**PRONTIDÃO EDITORIAL PARCIAL — PRIMEIRA ONDA CONDICIONADA A DECISÕES E EVIDÊNCIAS.** Testes bloqueados por dependência foram recuperados e a cobertura versionada dos 17 writers foi revalidada. A primeira onda operacional não é selecionável; integração e implantação continuam não autorizadas.
