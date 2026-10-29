# Beta 3 — relatório final

## A. Resultado executivo

A conversão experimental agora conserva os cinco tópicos e os oito segmentos H3 sem reescrever a teoria, cinco questões completas, três exercícios manuais, o critério textual, conexões, referências e proveniência. Um contrato Pydantic estrito gera IDs e payload determinísticos, explicita destinos não suportados e separa projeções de aluno e restritas.

O serviço real versionado `run_import` persistiu o piloto em MongoDB 7 descartável e os serviços reais de leitura consultaram os drafts. Seis falhas controladas mostraram retomada por identidade da importação sem duplicar blocos ou auditoria nos casos exercitados. O importador continua multi-etapas, sem transação global; isso não é contenção editorial C8–C16 nem integração operacional.

**Veredito: FIDELIDADE CURRICULAR E RECUPERAÇÃO EXPERIMENTAL VALIDADAS — INTEGRAÇÃO NÃO AUTORIZADA.** A validação cobre conversão, persistência privada/draft, leitor de serviço e retomada sintética; não valida publicação, rota, frontend ou jornada do aluno.

## B. Git e isolamento

- Base: `497e2a320f25d2bb3223b8fc257eaf9197bc49c5`, contendo Beta 2.
- Branch: `codex/beta3-curriculum-fidelity-recovery`.
- Worktree exclusiva: `C:\Users\Joao\.codex\worktrees\trilhacode-beta3-fidelity-recovery\trilhacodeprod`.
- Sparse checkout: backend, documentos Beta/arquitetura e, para regressões estáticas, apenas `.github/workflows` e `ops/g2`. `docs/courses` e `docs/migracao` não foram materializados.
- Nenhuma referência foi atualizada; sem merge, push, PR, deploy, acesso a ambientes operacionais ou alteração de outra worktree.
- Commit local criado após as verificações finais; o identificador completo está no resumo de entrega da fase.

## C. Fonte e unidade piloto

A fonte é a cópia Beta 2 da unidade `1.1 — Computação e software`, com revisão registrada `migracao@147dc68:tracked-clean-file`, ainda `rascunho`. SHA-256 bruto da origem e fixture: `db6e3ae5bcbdfa786caae171897f5140fc167249f591cb5ed9fcf9d1dd3aeec4`; SHA normalizado LF: `21736a209b840406169d88862f793e848952a402a01a37ae22d974d7bd59e513`. Revalidei o arquivo no checkout da migração em modo de leitura; estava limpo e tinha o mesmo hash. A fonte continua `APPROVED_FOR_ISOLATED_EXPERIMENT`, não aprovada para publicação ou importação operacional.

## D–L. Fidelidade, contrato, privacidade e conversão

- Cinco grupos curriculares ordenados contêm oito trechos H3 integrais; a concatenação dos trechos recompõe a teoria original. No destino, são oito blocos `theory_text` ordenados no mesmo nó. Os refs preservam grupo, mas o schema não tem entidade de agrupamento de tópico.
- Objetivo, resumo, tags, estimativa de minutos e campos taxonômicos do frontmatter são preservados nos destinos C16 aceitos.
- Cinco quizzes preservam enunciado, alternativas, gabarito, explicação e IDs determinísticos na representação restrita. `normalize_quiz` aceitou schema v1. `public_activity` e `_student_block` excluem gabarito/feedback; a leitura de estudante do track draft/private foi negada pelo serviço real. Não foi publicada a aula.
- Três exercícios preservam enunciado, ordem e dados de corretor no modelo intermediário restrito. Respostas/rubricas não foram enviadas ao importador, pois o schema/leitor genérico não demonstra ACL própria.
- O critério de conclusão é preservado como texto e não vira regra automática. Três conexões ficam não resolvidas e não se transformam em pré-requisitos. Duas referências preservam título, URL e descrição no contrato; o bloco atual só aceita título/citação e URL, então a descrição exige adaptador.
- O manifesto registra hashes, versões, contagens, refs, payload hash, seções sem destino e estados. Não contém o corpo privado dos exercícios nem a conclusão textual. IDs e payload são reproduzíveis para a mesma origem/versão.
- A projeção persistida tem um nó draft e 19 blocos draft: 8 teoria, 1 resumo, 5 quiz, 3 exercícios e 2 referências. A identidade de hash/revisão da fonte fica no manifesto; C16 não a grava nos documentos.

## M–P. Importação, falhas e recuperação

Leitura do código confirmou reserva job/lock, criação/atualização de trilha, escrita de nós/blocos/refs, relações, snapshot se publicado, auditoria por upsert, finalização e conclusão do job. Não há transação global. A retomada usa a mesma identidade de operação, refs estáveis e comparação das escritas persistidas.

Os seis cenários persistentes passaram: importação/replay; interrupção depois de quatro blocos; interrupção depois dos cinco quizzes; interrupção depois dos três exercícios; falha de auditoria antes da persistência; auditoria persistida seguida de confirmação simuladamente perdida. As retomadas completaram o payload sem duplicar blocos e mantiveram uma única auditoria. Estas falhas são wrappers sintéticos, não uma falha natural de rede/driver.

Recomendação futura: preparar importação em staging privada, validar manifesto/ref/contagens e promover por operação pequena da autoridade editorial aprovada, com job recuperável por etapas. Transação global permanece uma alternativa a validar para importações pequenas, não comportamento atual.

## Q–R. Persistência e leitura

MongoDB 7.0.43, WiredTiger standalone, tmpfs, rede exclusiva sem NAT de saída, publicação somente `127.0.0.1:27150`, sem volumes ou credenciais reais. Um teste leu a árvore e nó usando `nodes.get_track_tree` e `get_node`; verificou IDs, ordem e contagens. A leitura de estudante foi negada porque a trilha permanece private/draft. Nenhuma rota, endpoint HTTP, frontend, publicação ou jornada E2E foi exercitada.

## S–T. Ambiente e testes

Venv Beta 3 isolado com Python 3.11.9; `httpx==0.28.1` está declarado em `requirements-dev.txt`. Nenhuma dependência operacional/global foi alterada.

- Coleta padrão: 131 testes encontrados.
- Suíte padrão `backend/tests` no Mongo local descartável: 130 passaram, 1 falhou. A falha estática espera 38 índices e encontra 40 em `tests/test_integrity_concurrency.py`; preservada sem alteração.
- `backend/unit_tests`: 277 passaram, 36 skipped e 26 subtests aprovados.
- Segurança de snapshots: 6 passaram.
- Fidelidade Beta 3: 8 passaram.
- Recuperação persistente Beta 3: 6 passaram.
- Ruff nos quatro arquivos Python novos: aprovado. Mypy no módulo de fidelidade: aprovado. `py_compile`: aprovado.
- Validação do manifesto JSON: aprovada. `git diff --check`, verificação de links, arquivos protegidos, imports ativos e segredos registrados no encerramento.

Testes persistentes de outras fases não foram reexecutados nem reutilizados. Os skips permanecem skips; o resultado não representa cobertura completa de todos os cenários C8–C16.

## U–W. Segurança, gates e limitações

Nenhum writer, rota, IAM, schema operacional, modelo, configuração, serviço, migration, conteúdo curricular ou dado de aluno foi alterado. O conversor e harness são experimentais e não foram importados em startup/rotas. Nenhum banco real, staging, produção, Coolify ou GHCR foi acessado. Não houve publicação ou deploy.

Gates preservados: G1 `PARTIAL`; G2 `NOT_VERIFIED`; G3 `NOT_VERIFIED`; G4 `PARTIAL`; G5 `NOT_VERIFIED`; G6 `PARTIAL`; G7 `PARTIAL`; G8 `NOT_VERIFIED`; G9 `BLOCKED`; G10 `BLOCKED`. ADR-008 permanece bloqueado.

Não demonstrado: rota e frontend; resposta do aluno em uma publicação; ACL operacional de gabaritos/rubricas; destino de critério de conclusão/conexões/descrições; importação completa da Fase 1; transação global; falhas naturais de rede; integração com autoridade editorial e contenção de writers C16; progresso/tentativas/gerações em ciclo de aluno.

## X. Limpeza

Cada banco aleatório foi removido pelo harness após validar marcador da fase. O container e a rede exclusivos foram removidos após verificar IDs, labels e ausência de mounts/bancos. Nenhum recurso anterior ou de terceiros foi removido. A worktree terminou limpa após o commit local.

## Y. Arquivos entregues

- `backend/curriculum_contract/experimental_beta_curriculum_fidelity.py`
- `backend/integration_tests/beta_import_recovery_harness.py`
- `backend/integration_tests/test_beta_import_recovery.py`
- `backend/unit_tests/test_beta_curriculum_fidelity.py`
- `docs/beta/beta3-curriculum-fidelity-contract.md`
- `docs/beta/beta3-typed-content-mapping.md`
- `docs/beta/beta3-quiz-and-exercise-privacy.md`
- `docs/beta/beta3-completion-and-curricular-relations.md`
- `docs/beta/beta3-import-failure-recovery.md`
- `docs/beta/beta3-persistent-validation.md`
- `docs/beta/beta3-test-environment-recovery.md`
- `docs/beta/beta3-first-phase-readiness.md`
- `docs/beta/beta3-pilot-unit-manifest.json`
- `docs/beta/beta3-final-report.md`

## Z–AB. Próximo incremento e veredito

Antes de converter a Fase 1: ratificar uma revisão congelada da fonte segmentada; especificar destino/ACL para dados restritos; resolver tópicos, critérios, conexões e placements; aprovar recuperação/staging/promote e política editorial; então executar comparação persistente de toda a fase e validar leitores/publicação em ambiente isolado. Isso requer decisão humana e autorização específica futura.

**FIDELIDADE CURRICULAR E RECUPERAÇÃO EXPERIMENTAL VALIDADAS — INTEGRAÇÃO NÃO AUTORIZADA.**
