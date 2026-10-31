# Beta 6 — relatório final

## A. Resultado executivo

A worktree contém uma fatia vertical isolada: rotas atuais de quiz/submissão, projeções fechadas, escopo explícito de avaliador por trilha, idempotência e reconciliação de progresso, além de ajustes pequenos nos componentes existentes. A suíte unitária offline, as verificações direcionadas e a suíte frontend passaram. O MongoDB descartável não atingiu a condição de identidade de rede/porta exigida, e o harness encerrou antes de criar um cliente. Portanto, a jornada HTTP e ponta a ponta não foi demonstrada.

**Veredito: JORNADA DE APRENDIZAGEM PARCIALMENTE VALIDADA — INTEGRAÇÕES OU SEGURANÇA PENDENTES.**

## B. Git e isolamento

Base `828e8bbb5314df61d1b8dea39659b52654f111a3` com Beta 5; branch `codex/beta6-first-learning-journey`; worktree `C:\Users\Joao\.codex\worktrees\trilhacode-beta6-learning-journey\trilhacodeprod`. Nenhum outro checkout foi alterado. O venv local é temporário e será removido. Commits locais e status final serão listados no fechamento desta execução. Não houve push, PR, merge, publicação ou deploy.

## C. Arquitetura

A jornada reaproveita `current_user`, `require`, leitores de conteúdo, serviços versionados de atividades, submissões, progresso e componentes já presentes. O código novo permanece na branch e não foi conectado a staging/publicação editorial.

## D. Autenticação

Rotas usam a dependência autenticada existente; nenhuma identidade ou papel é aceito como autoridade a partir do cliente. O contrato integrado de autenticação não foi executado porque não houve banco persistente isolado validado.

## E. Autorização

Submissão fica vinculada ao usuário resolvido pelo servidor. Fila e correção exigem permissão estática `submissions.grade` e registro ativo experimental por usuário, trilha e operação. Falta de escopo nega. Isso não cria administração de grants nem substitui IAM real. Testes unitários cobrem projeções; negativos HTTP permanecem não executados.

## F. Leitura da aula

A leitura segue `get_node` e `can_view_node`. Fixture do teste tenta disponibilizar somente dados sintéticos no banco da execução; a fonte curricular original não foi modificada. Leitura HTTP da fixture não foi exercitada.

## G. Quiz

Reutiliza a atividade versionada e sua correção no servidor. O teste HTTP implementado verifica ausência de gabarito e retenção da versão, mas ficou bloqueado antes de ser executado. Não se declara quiz integrado validado nesta fase.

## H. Privacidade

Blocos de avaliação e submissões de aluno são serializados por allowlists fechadas. A projeção do aluno remove rubricas, respostas de referência, contexto de correção, metadados técnicos e campos desconhecidos. A resposta de instrutor tem allowlist própria. A verificação HTTP real ainda é necessária.

## I. Submissões

Modelos estritos limitam campos e tamanho. A identidade do aluno vem da sessão. `Idempotency-Key` é amarrada ao fingerprint e ao usuário. Resposta enviada é versionada com a atividade e histórico.

## J. Correção manual

Claim e correção são condicionais à revisão corrente e ao estado da submissão. Correção exige escopo do avaliador; submissão própria ou fora da trilha é ocultada/negada. Resultado de aprovação não deriva do envio. O endpoint não foi executado nesta fase.

## K. Progresso

Eventos de quiz e submissão projetam estados de progresso. Exercício manual não pode ser concluído por atualização direta do cliente sem resultado aprovado. IDs determinísticos permitem retry/reconciliação. A implementação usa várias gravações e não garante atomicidade global.

## L. Conclusão

Não foi introduzido limiar universal de nota nem inferência de domínio. Quiz conserva a política/versionamento existente. Exercício manual só chega a `completed` após aprovação persistida de avaliador. Teste persistente de resultado segue pendente.

## M. Projeto 3.5

O manifesto Beta 5 identifica 11 artefatos: brief, quatro marcos, rubrica e cinco checklists. Diretrizes de visibilidade permanecem deny-by-default; rubrica e materiais ainda não aprovados não são públicos. Beta 6 não implementa avaliação completa do projeto nem libera os artefatos.

## N. Frontend do aluno

Componentes existentes de leitura, quiz e exercício foram reutilizados. O formulário de exercício renderiza instruções e reaproveita a mesma chave de idempotência quando tenta novamente a mesma intenção. Vitest passou com 29 testes em 9 arquivos; typecheck e ESLint passaram. Não houve inspeção de browser.

## O. Frontend do instrutor

O painel existente consome fila/detalhe/claim/grade e mostra critérios retornados pelo servidor. A visibilidade do botão não é a ACL; autorização está no backend. O painel não foi conectado a API nesta fase.

## P. API HTTP

Usa rotas existentes de `/api/activities/.../attempts`, `/api/submissions/mine`, `draft`, `submit`, fila, detalhe, `claim` e `grade`; nenhuma rota editorial nova foi adicionada. A validação HTTP depende da regressão persistente bloqueada.

## Q. Testes persistentes

**NOT RUN.** Duas tentativas do harness MongoDB Beta 6 encontraram `HostConfig.PortBindings` configurado, mas ausência de `NetworkSettings.Ports` publicado. O verificador falhou antes de abrir conexão. Não se usou `localhost:27017`. Recursos identificados como pertencentes às tentativas foram removidos; a checagem de labels ao final não encontrou contêiner Beta 6 remanescente.

## R. Testes frontend

TypeScript typecheck passou; Vitest: 9 arquivos e 29 testes passaram; ESLint passou; build Vite passou com aviso de chunk de entrada >500 kB. Não são testes E2E.

## S. Testes E2E

Teste HTTP integrado de 1 fluxo foi criado em `backend/tests/test_beta6_learning_journey.py`, mas não coletado/executado sem alvo explicitamente provisionado. Coleta sem opt-in foi bloqueada antes de importar a aplicação, conforme política. Navegador não foi iniciado. Resultado: **E2E não demonstrado**.

## T. Regressões

Suíte `backend/unit_tests`: **334 passed, 43 skipped, 26 subtests passed**. Os skips são condicionados a recursos/plataformas não disponíveis no Windows. Regressões de API persistente não executadas por bloqueio de ambiente.

## U. Segurança

Ruff passou nos arquivos Python alterados. MyPy direcionado passou em `services/submissions.py`, `services/learning_scopes.py` e `schemas/submissions.py`. `compileall` passou. Isolamento de banco falhou fechado antes da conexão. Permanecem dependentes de teste HTTP as garantias de sessão, ACL, serialização e progresso.

## V. Isolamento

Não houve acesso a banco operacional, staging, produção, Coolify ou GHCR. Nenhum dado real, segredo operacional, conteúdo original ou usuário real foi usado. O antigo localhost da Beta 4 não foi consultado nem limpo retroativamente. Venv e recursos desta execução são removidos somente se o caminho/ownership forem confirmados.

## W. Gates

Preservados: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 PARTIAL; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. ADR-008 permanece bloqueado.

## X. Arquivos

Backend: rotas de atividades/submissões, schemas, serviços de nodes/progress/submissions e novo `learning_scopes.py`; helper/harness de teste Mongo, runner Beta 6, fixture persistente, testes unitários offline. Frontend: painel de correção, renderização/instruções do exercício, formulário de envio, tipos e teste do componente. Documentação nova em `docs/beta/beta6-*.md`. A lista exata é o `git show --stat` dos commits locais.

## Y. Limitações

Não demonstrados: serviço Mongo/HTTP, autenticação ponta a ponta, fila e correção sob ACL, progresso persistido, concorrência/recovery no banco, resposta serializada via endpoint, navegador, visual/mobile/acessibilidade e integração entre UI e API. `learning_review_scopes` não tem lifecycle IAM real. Reconciliação de progresso não é transação única. C16 continua demonstrando bypass editorial por writer com escrita direta.

## Z. Próximo incremento

Reexecutar o mesmo harness em executor que suporte rede `--internal` e binding loopback verificável; não relaxar a política. Validar teste HTTP completo, corrigir eventuais falhas e então automatizar browser contra API e MongoDB descartáveis. Aprovar previamente grants por trilha e revogação no IAM antes de qualquer ambiente com aluno.

## AA. Veredito

**JORNADA DE APRENDIZAGEM PARCIALMENTE VALIDADA — INTEGRAÇÕES OU SEGURANÇA PENDENTES.** Implementação isolada e verificações offline estão presentes; prova HTTP/E2E e ativação para Pioneiros não estão autorizadas ou demonstradas.
