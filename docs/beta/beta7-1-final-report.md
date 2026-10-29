# Trilha Code — Beta 7.1: relatório final

## A. Resultado executivo

A prévia isolada consumiu as dez unidades revisadas com frontend React, API FastAPI, Chromium e MongoDB 7 descartável. O usuário sintético percorreu os três módulos, abriu cada unidade, respondeu quizzes representativos, enviou exercício e entrega do projeto 3.5, recebeu solicitação de revisão e consultou feedback/progresso após novo login e recarga. O leitor editorial real continuou negando a trilha original privada/em rascunho. Não houve publicação, promoção ou dado real.

**Resultado global: BETA 7.1 PARCIALMENTE VALIDADA — INTEGRAÇÃO PEDAGÓGICA OU SEGURANÇA PENDENTES.** A avaliação e conclusão pedagógica do projeto 3.5 ainda requer decisão; integração com IAM operacional e segurança editorial C8–C16 também permanecem fora da prova.

## B. Git e isolamento

Base exata `e671375effee9b957b281559a7310481ef82534b`; branch `codex/beta7-1-real-curriculum-preview`; worktree `C:\Users\Joao\.codex\worktrees\trilhacode-beta7-1-curriculum-preview\trilhacodeprod`. A execução integrada final usou o run `8dad34026a7d4e7ea210301c5754fd08`. O commit local final será registrado após sua criação. O ambiente descartável foi limpo; os filtros da fase não mostraram containers ou redes residuais. Checkout original e worktree curricular permaneceram intocados.

## C. Fonte e currículo

Fonte lida somente da worktree Beta 4 em `migration@147dc68:tracked-clean-first-phase-files`, marcada `rascunho` e `APPROVED_FOR_ISOLATED_EXPERIMENT`. Manifesto Beta 4 SHA-256 `6e820ce44d6d23141d6cdc57e323e9a42e23c36e14b9741f030952d3772ffb42`; manifesto de staging Beta 5 SHA-256 `4e1145798574bce58a72afdbe3150977d3025225b04f962aa46be811eb7077db`. Payload curricular Beta 5 `dce89cbc9beb1040a5cb993494026ac07a5c0d8d80e19479349e088f225eb6e4`. Hashes individuais foram revalidados durante a conversão; veja matriz de cobertura.

Inventário: 3 módulos, 10 unidades, 30 tópicos, 42 segmentos, 44 questões, 26 exercícios, 39 referências, 30 relações, 11 artefatos de projeto e 161 blocos. Nenhum conteúdo-fonte foi alterado. As dez unidades foram acessadas no browser; quiz por HTTP/browser exercitado em 1.1 e 2.1; exercício HTTP/browser em 1.1; outros elementos foram validados estruturalmente. Isso não é execução funcional de todos os itens.

## D. Entrega A — prévia isolada

**PRÉVIA CURRICULAR ISOLADA VALIDADA.** API e interface de teste são compostas explicitamente pelo harness; a aplicação não importa `server:app`, não registra rotas de prévia no startup operacional e só o modo Vite dedicado registra a tela. A prévia usa namespace separado e grants sintéticos de lote/usuário. Requisições sem grant recebem 404; aluno autenticado com escopo recebe 403 para materiais restritos. A mesma execução provou 404 no leitor operacional da trilha privada em rascunho, sem inserir registros de publicação. O staging não foi promovido.

## E–O. Navegação, atividades e progresso

**PRIMEIRA FASE REVISADA VALIDADA COMO JORNADA DE ALUNO EM AMBIENTE ISOLADO.** Playwright percorreu todas as dez unidades pela interface, na ordem, com conteúdo vindo da API. Teoria, resumo, referências e atividades são fornecidos a partir da conversão real. IDs, hashes, ordem e associações foram validados. 44 perguntas e 26 exercícios foram preservados estruturalmente; tentativas HTTP/browser foram amostrais, não totais. Respostas e explicações restritas não aparecem na projeção pública nem no recibo do quiz.

Progresso é por atividade/unidade/módulo/fase e distingue respondido, enviado, aguardando correção, revisão e critério pendente. Projeto 3.5 permanece obrigatório; fase `BLOCKED_BY_UNRESOLVED_PEDAGOGICAL_CRITERIA`, domínio `NOT_ASSESSED`. Nenhuma leitura ou envio foi convertido em domínio. Após nova sessão e reload, a tentativa, entrega, feedback e estado persistiram.

As 30 relações foram classificadas: 21 internas à Fase 1 foram persistidas; nove apontam para outras fases não carregadas e foram preservadas como referências externas pendentes, sem se tornarem inválidas nem novos pré-requisitos. Matriz completa em `beta7-1-curricular-relations.md`.

## P–S. Projeto 3.5

**PROJETO 3.5 PARCIALMENTE VALIDADO — AVALIAÇÃO OU CRITÉRIOS PENDENTES.** Os 11 materiais (brief, quatro marcos, rubrica e cinco checklists) foram reconhecidos. O aluno só recebe o brief; marcos sem política de desbloqueio, checklists não classificados e rubrica ficam ocultos. Avaliador autorizado consulta os materiais restritos e a entrega dentro do lote. Entrega textual, estado `AWAITING_REVIEW`, correção `NEEDS_REVISION`, feedback e histórico foram persistidos e consultados em nova sessão. Aprovação não está disponível porque os critérios pedagógicos não dão base suficiente para decisão objetiva; não foi inventada.

## T.–U. Autorização concorrente

**SEGURANÇA DA PRÉVIA E E2E REAL VALIDADOS EM AMBIENTE ISOLADO**, com escopo estritamente experimental. A janela revogação/correção foi exercitada no replica set com barreira controlada. A transação grava o mesmo grant usado pela revogação, cria uma ordem de commit verificável e inclui CAS da submissão e auditoria. Revogação antes do commit causa conflito sem escrita parcial; correção commitada antes da revogação permanece auditada. Essa garantia não se estende ao IAM operacional.

## V–Z. Testes e qualidade

Resultados da execução Beta 7.1:

* Contratos offline: 7 testes aprovados no runner descartável. O Python do host não tinha `pytest`; não foi alterado nem suplementado.
* API HTTP integrada, autenticação real de usuários sintéticos, autorização, leitura privada, quiz, exercício, projeto, feedback e progresso: aprovado (`HTTP_VERIFIED`).
* Playwright/Chromium com dez unidades reais: 1 cenário aprovado (`BROWSER_VERIFIED`).
* Revogação versus CAS em MongoDB replica set: aprovado (`PERSISTENCE_VERIFIED`).
* Vitest: 29 testes aprovados em 9 arquivos.
* TypeScript typecheck, ESLint e build Vite: aprovados.
* Build emite aviso de bundle principal de aproximadamente 506 kB (acima do limiar atual de 500 kB); não bloqueou a execução.

Suites históricas completas Beta 2–7 não foram reexecutadas nesta validação. O relatório não as declara aprovadas. Execução e ambiente são isolados pelo harness Beta 7.1; Mongo 7.0.43, WiredTiger, replica set, rede interna, sem porta publicada, sem volume persistente, sem credenciais operacionais. Cleanup só remove recursos que carregam os IDs e ownership marker do run.

## AA–AC. Segurança editorial, gates e restrições

Nenhum writer editorial, IAM global, rota de publicação ou matriz histórica foi alterado. C8–C16 continuam dependendo de autoridade operacional única, grants reais, fencing, contenção de escritores diretos, auditoria e preservação de progresso/tentativas. Gates preservados: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 PARTIAL; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. ADR-008 permanece bloqueado. Sem acesso a produção, staging, Coolify ou GHCR; sem push, merge ou deploy.

## AD–AF. Arquivos, limitações e próximo incremento

Implementação: composição ASGI e roteador de prévia no test support; contratos e serviço de prévia isolados; gate/harness, seed, HTTP e race runner; rota/tela Beta 7.1 condicionada ao modo Vite; fluxo Playwright e diagnóstico seguro de falha. Arquivos adicionados: `backend/schemas/beta7_1_preview.py`, `backend/services/beta7_1_preview.py`, `backend/test_support/beta7_1_docker_harness.py`, `backend/test_support/beta7_1_http_validation.py`, `backend/test_support/beta7_1_internal_target.py`, `backend/test_support/beta7_1_preview_router.py`, `backend/test_support/beta7_1_preview_server.py`, `backend/test_support/beta7_1_revocation_race.py`, `backend/test_support/beta7_1_seed_preview.py`, `backend/test_support/run_beta7_1_preview.py`, `backend/unit_tests/test_beta7_1_preview_contract.py`, `frontend/e2e/beta7-1-real-first-phase.spec.ts`, `frontend/src/pages/beta/Beta71CurriculumPreview.tsx` e os cinco documentos de evidência Beta 7.1 nesta pasta. Arquivos ajustados: `backend/test_support/beta6_1_docker_harness.py` (opção segura de comando/ambiente do Mongo e verificação de comando padrão `mongod`), `frontend/e2e/fixtures.ts` (diagnósticos limitados) e `frontend/src/App.tsx` (rota condicionada ao modo exclusivo). Detalhes nos documentos focados listados acima.

Limitações: rascunho sem aprovação para publicação; grants sintéticos; sem integração com IAM operacional; sem decisão pedagógica final sobre critério/rubrica e marcos do projeto; não houve tentativa em todas as questões/exercícios; nove relações apontam a conteúdo fora do lote; regressões históricas completas não foram executadas; homologação visual de acessibilidade não foi reivindicada; escritores operacionais ainda são dependência editorial C8–C16.

Próximo incremento mínimo: decidir e versionar os critérios de conclusão e avaliação do projeto 3.5; resolver as relações externas contra fontes aprovadas; então integrar a prévia ao IAM e à autoridade editorial através de grant por recurso e fence transacional, com testes de contrato/HTTP antes de qualquer homologação de lançamento. Manter publicação operacional bloqueada até ADR-008 e contenção dos writers.

## AG. Vereditos independentes

| Entrega | Veredito |
|---|---|
| A — Prévia isolada | **PRÉVIA CURRICULAR ISOLADA VALIDADA** |
| B — Currículo e jornada | **PRIMEIRA FASE REVISADA VALIDADA COMO JORNADA DE ALUNO EM AMBIENTE ISOLADO**; conclusão pedagógica da fase permanece bloqueada |
| C — Projeto 3.5 | **PROJETO 3.5 PARCIALMENTE VALIDADO — AVALIAÇÃO OU CRITÉRIOS PENDENTES** |
| D — Segurança e E2E | **SEGURANÇA DA PRÉVIA E E2E REAL VALIDADOS EM AMBIENTE ISOLADO**; IAM editorial operacional não demonstrado |

## AH. Veredito global

**BETA 7.1 PARCIALMENTE VALIDADA — INTEGRAÇÃO PEDAGÓGICA OU SEGURANÇA PENDENTES.** A prévia e a jornada das dez unidades foram provadas isoladamente; a prova não aprova publicação, homologação ou lançamento.
