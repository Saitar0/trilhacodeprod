# Trilha Code — Beta 7: relatório final

## A. Resultado executivo

A Beta 7 validou duas coisas em escopos distintos: (1) segurança e consistência da jornada de aprendizagem em API e MongoDB descartáveis, incluindo sessões, fila com escopo, correções concorrentes e replay idempotente; (2) conversão/persistência/leitura administrativa das dez unidades do rascunho curricular. Um browser real percorreu duas unidades sintéticas, e esse teste encontrou e levou à correção de uma corrida no formulário de correção que podia apagar feedback digitado após uma atualização assíncrona.

As dez unidades não foram navegadas como aluno no browser e permanecem rascunho/privadas; o projeto 3.5 não tem avaliação operacional. Portanto, não há base para dizer que a primeira fase está pronta para alunos. Nenhum gate operacional foi promovido.

**Frente A:** SEGURANÇA E CONSISTÊNCIA DA APRENDIZAGEM VALIDADAS EM AMBIENTE ISOLADO, dentro dos cenários comprovados e com os limites de revogação/CAS descritos abaixo.

**Frente B:** PRIMEIRA FASE CURRICULAR PARCIALMENTE VALIDADA — RECURSOS PENDENTES.

**Global:** BETA 7 PARCIALMENTE VALIDADA — INTEGRAÇÃO OU SEGURANÇA PENDENTES.

## B. Git e isolamento

* Base exata: `c486fa7f5715d93ec7481534a07791830c130fc4`.
* Ancestralidade Beta 6.1: `c1aed5b1c38897bdefb309f1e1838f892799324b` é ancestral da base. A sequência e os relatórios Beta 6.1 estão presentes.
* Branch: `codex/beta7-first-phase-learning-hardening`.
* Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-beta7-learning-hardening\trilhacodeprod`.
* Fonte de migração consultada em leitura: commit `147dc68b81169f66b0ba3802fa2f26e5130923a3`, limpa nos caminhos selecionados.
* Checkout original e demais worktrees não foram usados para edição. Sem push, merge, deploy, staging ou produção.
* Commits Beta 7 locais serão listados após o fechamento deste relatório; worktree deve terminar limpa.

## C. Frente A — sessões

Reutilizou autenticação/sessões existentes. Nove testes de sessão e um de atualização de papel passaram por HTTP: expiração, desconhecido/ausente, usuário desativado, logout/revogação, revogação por troca de senha e corrida refresh/logout. Papel atualizado tem efeito na sessão existente. Revogação global de IAM/grants não é inferida desses testes.

## D–E. Autorização da fila e recursos

GET da fila exige permissão e escopo de trilha no backend; filtros e paginação do cliente não ampliam o escopo. Admin/editor sem grant sintético recebeu `403`; aluno não acessa a fila; usuário sem escopo no browser recebeu negativa. Submissão de terceiro ficou indistinguível de inexistente (`404`). O banco usa grants de fixture, não IAM operacional.

## F–G. Concorrência e idempotência

Duas requisições HTTP verdadeiramente concorrentes no Mongo foram sincronizadas antes da leitura. CAS por revisão e status permitiu uma única correção e retornou `409` para a perdedora, sem sobrescrever histórico. Mesmo `Idempotency-Key` e fingerprint reproduz decisão; chave reutilizada com payload divergente dá `409`. A UI conserva chave durante retry da mesma operação. O grant é revalidado imediatamente antes do CAS; teste HTTP/Mongo removeu o grant após a primeira checagem e comprovou que a correção foi negada sem mutação. A checagem final e a escrita ainda não são atômicas entre coleções.

## H–I. Progresso e histórico

Os 33 testes persistentes incluíram sessões, atualização de papel, jornada Beta 6, concorrência/revogação Beta 7, importação/readers da primeira fase, confiabilidade de progresso e tentativas. Reconciliar evento pendente em retry não duplicou evento; tentativas permanecem distintas. A gravação de correção e todas as projeções não formam uma transação global; falha exatamente nessa fronteira não foi injetada nesta fase.

## J. Teste Docker histórico

O teste G2 está opt-in e ownership-bound, com rede interna, tmpfs e sem mounts/ports. Guard offline: 5 passed; execução opt-in: 6 passed. Sem opt-in, é skip. A suíte unitária completa foi repetida em runner isolado e terminou em 386 passed, 39 skipped. O skip do Compose decorre da ausência de CLI/daemon dentro do runner.

## K. Veredito independente da Frente A

**SEGURANÇA E CONSISTÊNCIA DA APRENDIZAGEM VALIDADAS EM AMBIENTE ISOLADO.** Limites: grants sintéticos, janela residual entre checagem final do grant e CAS, e ausência de transação global correção/progresso; essas garantias não autorizam integração.

## L–M. Frente B — fonte e inventário

Fonte permanece `rascunho`, autorizada somente para experimento. Os 221 artefatos do manifesto Beta 4 foram copiados após validação SHA-256; o piloto 1.1 também foi conferido contra `db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4`. Ver [matriz por unidade](beta7-curricular-unit-coverage.md).

## N–S. Dez unidades, teoria, quizzes, exercícios e critérios

Conversor Beta 4 e `run_import` real processaram lote integral em MongoDB descartável: 3 módulos, 10 unidades, 30 tópicos, 42 segmentos, 44 questões/blocos de quiz, 26 exercícios, 39 referências, 30 relações extraídas e 11 materiais do projeto 3.5. A leitura administrativa por API cobriu todos os nós e blocos. Persistiram 21 relações segundo o schema/importador; não se simulou disponibilidade ao aluno. O lote ficou draft/private, sem publicação/registro de publicação.

Não há equivalência entre esta prova de ingestão/leitura e renderização estudantil. Critérios sem regra executável não foram transformados em aprovação automática. A avaliação do projeto 3.5 continua ausente; a fase não deve ser considerada concluída quando o projeto for requisito.

## T. Progresso agregado

Estados de quiz e submissão foram validados por HTTP para a fixture sintética; não foi implementada/validada nesta fase uma visão agregada de progresso por módulo e fase para o lote curricular real. Percentual de atividade não é tratado como domínio pedagógico.

## U–V. Projeto 3.5 e frontend

Os 11 materiais foram inventariados no manifesto: brief, quatro marcos, cinco checklists e rubrica. Visibilidade do aluno mantém deny-by-default para materiais não revisados; avaliação do projeto não foi implementada.

Playwright Chromium usou API e frontend reais e banco isolado, com duas unidades sintéticas: login, navegação pela árvore, aula, dois quizzes, exercício, negativa ao avaliador sem escopo, correção, feedback e progresso após reload. Após primeira falha por perda de feedback em refetch, a interface foi corrigida e o E2E confirmou tanto o corpo HTTP quanto a tela do aluno. Não é E2E das dez aulas revisadas.

Qualidade frontend: typecheck, ESLint, 9 arquivos/29 testes Vitest e build passaram. O bundle principal continua em 505,92 kB, acima do aviso de 500 kB; não foi feita refatoração ampla.

## W. HTTP e X. Playwright

HTTP/persistência: **33 passed**. Browser E2E: **1 passed** na fixture sintética multiunidade. Primeira fase real: prova administrativa de importação e leitura; aluno corretamente recebeu `404` para conteúdo privado.

## Z. Regressões e ferramentas

* Suíte offline completa no runner Python 3.11 isolado: **386 passed, 39 skipped**.
* Testes persistentes selecionados Beta 6/Beta 7: **33 passed**.
* Browser Playwright: **1 passed**.
* Frontend: typecheck, lint, 29 Vitest e build aprovados.
* Guard Docker offline: **5 passed**; opt-in G2: **6 passed**.
* Ruff direcionado: passou.
* MyPy direcionado: passou, 9 arquivos.
* Compilação Python direcionada e `git diff --check`: passaram.
* Uma execução inicial da suíte total falhou em 17 testes porque o contexto esparso não copiava arquivos estáticos usados por contratos; runner e dockerignore foram corrigidos, repetição passou. A primeira repetição do browser encontrou a corrida no feedback; teste reforçado e repetição passou.

## AA–AB. Segurança editorial, infraestrutura e gates

Não houve uso de staging, produção, Coolify ou GHCR; nenhum escritor/IAM editorial operacional foi alterado. C8–C16 continuam com bypass direto já documentado, sem contenção global. MongoDB 7, API, frontend e Chromium operaram em rede Docker interna exclusiva, sem portas publicadas, mounts persistentes ou volumes. Cleanup revalidou ownership e inspeção posterior por label encontrou zero recursos Beta 7.

Estados preservados: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 PARTIAL; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. ADR-008 permanece BLOCKED.

## AC. Arquivos Beta 7

**Alterados:** `backend/routes_submissions.py`; `backend/services/submissions.py`; `backend/test_support/Dockerfile.beta6_1_e2e`; `backend/test_support/Dockerfile.beta6_1_e2e.dockerignore`; `backend/test_support/beta5_mongo_target.py`; `backend/tests/conftest.py`; `backend/tests/test_progress_reliability.py`; `backend/unit_tests/test_g2_docker_api_contract.py`; `frontend/src/components/admin/GradingPanel.tsx`.

**Criados:** `backend/test_support/beta7_docker_harness.py`; `backend/test_support/beta7_internal_target.py`; `backend/test_support/beta7_seed_multiunit_fixture.py`; `backend/test_support/run_beta7_journey.py`; `backend/tests/test_beta7_first_phase_http.py`; `backend/tests/test_beta7_review_concurrency.py`; `backend/unit_tests/test_beta7_docker_contract_guard.py`; `backend/unit_tests/test_beta7_internal_target.py`; `frontend/e2e/beta7-multiunit-learning.spec.ts`; `docs/beta/beta7-security-hardening.md`; `docs/beta/beta7-curricular-unit-coverage.md`; `docs/beta/beta7-docker-test-isolation.md`; `docs/beta/beta7-final-report.md`.

## AD–AF. Limitações e próxima fase

Falta renderização de aluno das dez unidades; contrato/avaliação progressiva do projeto 3.5; tratamento de campos pedagógicos sem destino; visão de progresso agregado por fase; autorização operacional com grants/revogação; eliminação da janela não atômica entre checagem final de escopo e CAS; injeção de falha na fronteira correção/progresso; execução E2E de conteúdo real em modo de aluno sem publicação; homologação mobile/acessibilidade; contenção de writers C8–C16; ADR-008 e gates operacionais.

Próximo incremento recomendado: homologação isolada da leitura de conteúdo estudantil a partir de uma geração/fixture explicitamente liberada apenas no harness, seguida de renderização browser de amostra representativa (incluindo 3.5) e testes de reconciliação em falha entre decisão e projeção. Manter o curriculum draft e os writers operacionais desconectados até resolver IAM/grants e autoridade editorial.

## AG. Veredito global

**BETA 7 PARCIALMENTE VALIDADA — INTEGRAÇÃO OU SEGURANÇA PENDENTES.** A segurança da jornada foi validada nos cenários isolados exercitados; a primeira fase real tem conversão e leitura administrativa completas, mas sua experiência de aluno nas dez unidades e a avaliação do projeto 3.5 não foram demonstradas. Nenhum resultado autoriza publicação, merge, lançamento ou deploy.
