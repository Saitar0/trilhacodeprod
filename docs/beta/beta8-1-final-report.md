# Trilha Code — Beta 8.1 — Relatório final

## A. Resultado executivo

Foi integrada uma fatia representativa: a rota HTTP existente de edição de bloco usa a autenticação ativa FastAPI, exige permissão nominal existente e grant C12 por trilha, chama o serviço de bloco existente, passa pela autoridade C8/C10 com CAS/fencing e grava histórico/auditoria em MongoDB descartável. O role comum não escreve diretamente em conteúdo editorial; o preparador não promove. O serviço real Beta 5 de staging foi conectado a uma transição de geração sintética.

A prova integrada passou no harness local descartável. A cobertura não contém globalmente os writers: W-07 está coberto só para PUT no harness e os demais caminhos permanecem não verificados. O processo/role da autoridade ainda possui escrita por coleção necessária ao participante e pode contornar o protocolo se seu segredo for usado diretamente. IAM operacional, credenciais reais, publicação e configuração de produção não foram examinados.

**Veredito global:** BETA 8.1 PARCIALMENTE VALIDADA — IAM, WRITERS OU STAGING AINDA NÃO INTEGRADOS GLOBALMENTE.

## B. Git e isolamento

* Commit-base exato: `6a4beafee56917569a649f8d75baae5a5ce0fa90`.
* Branch: `codex/beta8-1-runtime-editorial-integration`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-beta8-1-runtime-security\trilhacodeprod`.
* A origem Beta 8 contém a sequência e os relatórios requeridos; alterações ficaram nesta worktree.
* Commit(s) local(is): registrados no histórico da branch e listados na resposta final.
* Sem push, PR, merge, cherry-pick, rebase, deploy ou alteração do checkout original/worktrees externas.

## C. Arquitetura de autenticação

O harness importou, depois do gate, as rotas e dependências ativas: login/logout em `routes_auth.py`, `current_user` em `security.py`, `require("content.write")` em `permissions.py`, usuário em `users` e sessão em `auth_sessions`. O ator vem do JWT verificado e da sessão armazenada; corpo/papel enviado pelo cliente não escolhe identidade.

## D–F. Adaptador, grants e revogação

`Beta8_1RuntimeIAMBridge` vincula actor/role/token version/session do `current_user` ao principal e à sessão C12. Divergência, inatividade, expiração ou falta de permissão nega. A fronteira editorial resolve a trilha do bloco no servidor e exige grant `block.update`; grant de outra trilha e papel admin sem grant específico foram negados.

No commit, a transação C8/C10 toca condicionalmente usuário/sessão ativos, principal/sessão/grant C12, revisão do bloco, histórico e auditoria. O ponto de confirmação experimental é o commit da transação; grant revogado que serializa antes da mutação resulta em rejeição/conflito e conteúdo/revisão inalterados. O teste utilizou barreira entre autorização e commit no replica set descartável.

## G–I. HTTP, auditoria e Entrega A

O teste exerceu a rota PUT real e login real sobre ASGI HTTP, não somente função de serviço. Foram observados login, update autorizado, ETag/revisão, replay da mesma chave e persistência. Negativas: anônimo, JWT expirado, sessão após logout, usuário desativado, ausência de capability, grant ausente, grant de outra trilha e admin sem escopo. Erros de grant são 403 sanitizados; a ausência de capability retorna 503.

Auditoria/histórico foram persistidos na transação e inspecionados com o provisionador, porque a identidade de autoridade é write-only nas coleções de auditoria. Não há tokens, credenciais ou conteúdo completo em respostas/eventos da fatia.

**Entrega A:** IAM INTEGRADO AOS GRANTS EDITORIAIS NO RUNTIME DE TESTE — ATIVAÇÃO OPERACIONAL PENDENTE.

## J–M. Inventário, risco e identidade MongoDB

Os 17 writers da matriz C13/C16 permanecem no código. Todos foram localizados estaticamente; inventário de código não comprova processos implantados nem identidade efetiva. O PUT de W-07 foi integrado na composição experimental. O runtime comum do harness não tem `insert/update/delete` em `content_blocks` nem escrita em publicações; chamada MongoDB direta e chamada legada de `services.blocks.update_block` foram negadas pelo banco. O preparador Beta 5 grava somente nas coleções de staging e não grava o head experimental.

A autoridade recebe `find/update` em conteúdo, coleções C8/C12 e sessões/usuários necessários; recebe insert em history/auditoria e coleções sintéticas. Não possui leitura de auditoria. Como MongoDB controla por coleção, esse role pode efetuar update direto em `content_blocks`: é uma fronteira de confiança experimental, não uma capability impossível de contornar. A prova não isola a autoridade em processo/RPC separado e não identifica credenciais de deployment.

Veja a matriz individual dos 17 caminhos em [beta8-1-writer-reconciliation.md](beta8-1-writer-reconciliation.md).

## N–R. Escritores, CAS, idempotência e histórico

Na operação selecionada, CAS rejeita revisão obsoleta; fencing pertence à credencial C8/C10; replay idêntico devolve o recibo existente e não duplica auditoria/histórico. Corrida controlada de revogação não altera o bloco. A role comum não consegue efetuar escrita direta. A operação não toca tentativas, progresso, submissões ou gerações educacionais reais; a prova de preservação é limitada às fixtures sintéticas e aos namespaces que foram consultados.

Somente a operação PUT de W-07 foi exercitada. Criar, reordenar e excluir blocos, assim como os outros 16 writers, permanecem fora da contenção comprovada. Os caminhos de exclusão, restore, importação e publicação seguem bloqueados para cutover.

**Entrega B:** WRITERS SELECIONADOS INTEGRADOS E CONTIDOS — COBERTURA GLOBAL PENDENTE.

## S–X. Staging, autoridade, promoção sintética e gerações

O código real `CurriculumStagingService` Beta 5 preparou e inspecionou um pacote sintético em banco separado; o usuário `beta8-1-preparer` tinha privilégios apenas nas coleções de staging. Um bridge validou hash, batch, revisão/proveniência e registros sintéticos antes de passar para o `Beta8ExperimentalPromoter`, em namespace de geração experimental. A autoridade C12/C8 realizou uma transição; preparação sem privilégio de promoção foi negada.

Não foram usados `run_import` operacional, coleções de publicação, trilha real ou rubrica real. `SYNTHETIC_FIXTURE_APPROVED` é somente estado de teste. O fluxo da ponte não exercitou repetição de staging com payload divergente, recuperação de falha após commit ou promoções concorrentes por meio do bridge; a prova histórica Beta 8 testa propriedades do promotor isolado, não substitui esses cenários integrados. Gerações e histórico operacional não foram tocados.

**Entrega C:** STAGING PARCIALMENTE INTEGRADO — ENFORCEMENT PENDENTE.

## Y–AB. Ambiente e testes

O script `ops/beta8-1-security/run-local.ps1` validou o contexto Docker local, imagem MongoDB 7.0.43 por digest, ownership por IDs e labels, rede interna exclusiva, nenhum port mapping, tmpfs para dados e ausência de volumes persistentes. O runner foi corrigido para PowerShell 5.1 e cardinalidade de `docker inspect`. URI e credenciais foram geradas pelo harness; o teste não usou fallback `localhost:27017`.

Na última execução: **4 testes offline Beta 8.1 passaram**; regressão persistente Beta 8 passou nos gates/roles, authority, promoção e concorrência; a prova persistente/HTTP Beta 8.1 passou na autenticação, autorização, update, CAS, idempotência, revogação, negativas MongoDB e staging experimental. Contêiner, rede e imagem temporária foram removidos após revalidação de ownership.

Ruff 0.17.3 passou nos arquivos Python alterados, instalado temporariamente fora do repositório e sem instalação global. Mypy 2.4.1 passou nos cinco módulos Python direcionados (`--ignore-missing-imports --follow-imports=silent --python-version 3.11`). `compileall`, validação JSON do inventário e `git diff --check` passaram. Suites completas Beta 5–7.2, regressões de aprendizagem/Playwright/frontend não foram executados. O projeto não mudou frontend.

**Entrega D:** VALIDAÇÃO INTEGRADA PARCIAL — REGRESSÕES OU GARANTIAS PENDENTES.

## AC. Regressões de aprendizagem

Não houve mudança nos fluxos de aluno, quizzes, submissões, correção ou progresso. A prova Beta 8 base foi executada como regressão persistente. Suites completas de aprendizagem e Playwright não foram executados nesta fase; não declarar regressão E2E aprovada. A rubrica real do projeto 3.5 continua `PROPOSED` e a conclusão pedagógica permanece bloqueada.

## AD–AI. Segurança editorial, gates e ADR-008

Não houve publicação, promoção curricular real, alteração de IAM operacional, uso de credenciais reais, alteração curricular original, acesso a produção/staging/Coolify/GHCR ou deploy. C8–C16 não estão operacionalmente integrados; distribuição de segredos, autoridade em processo separado, identidades efetivas, privilégio real, backup/restore, observabilidade e revogação operacional precisam de confirmação autorizada.

Gates históricos preservados conforme estado Beta 8.1: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 NOT_VERIFIED; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. ADR-008 continua **BLOCKED**. Pendências detalhadas em [beta8-1-adr008-dependencies.md](beta8-1-adr008-dependencies.md).

Arquivos alterados:

* Modificados: `backend/routes_content.py`, `backend/services/blocks.py`, `backend/services/beta8_editorial_enforcement.py`.
* Novos: `backend/services/beta8_1_runtime_iam.py`, `backend/services/beta8_1_staging_authority.py`, `backend/integration_tests/beta8_1_runtime_security.py`, `backend/unit_tests/test_beta8_1_runtime_security.py`.
* Harness exclusivo: `ops/beta8-1-security/Dockerfile.dockerignore`, `Dockerfile`, `compose.yaml`, `requirements.lock`, `run-local.ps1`.
* Relatórios novos em `docs/beta/`: `beta8-1-adr008-dependencies.md`, `beta8-1-final-report.md`, `beta8-1-runtime-iam-integration.md`, `beta8-1-staging-authority-integration.md`, `beta8-1-validation-results.md`, `beta8-1-writer-reconciliation.md`.

Nenhuma alteração em `docs/courses/trilhacode/`, `docs/migracao/`, credenciais, configuração operacional, migrations, deploy ou gates históricos.

## AJ. Rubrica 3.5

Nenhuma alteração pedagógica. Rubrica real continua proposta; a fixture sintética da Beta 8 não concede aprovação ao projeto real.

## AL–AM. Limitações e próxima ação

Não foram verificados todos os writers, credenciais/roles reais, endpoint em startup operacional, promoção real, integração IAM oficial, leitor público de todas as rotas, transação em topologia produtiva, recovery natural de interrupção, suites completas ou frontend. A autoridade experimental ainda pode fazer escrita direta por privilégio da coleção.

Próximo incremento mínimo: numa etapa operacional somente leitura formalmente autorizada, mapear identidades e privilégios efetivos dos 17 writers; em seguida isolar a autoridade num processo/credencial próprio, retirar escrita editorial de runtimes comuns, migrar o importador/staging como segundo writer real e executar probes de bypass contra cada identidade, antes de propor cutover/ADR-008. Não publicar currículo como parte dessa etapa.

## AN. Veredito global

**BETA 8.1 PARCIALMENTE VALIDADA — IAM, WRITERS OU STAGING AINDA NÃO INTEGRADOS GLOBALMENTE.** A evidência integrada em ambiente descartável é positiva para a fatia selecionada; contenção global e homologação operacional continuam pendentes. Nenhum resultado autoriza publicação, merge ou deploy.
