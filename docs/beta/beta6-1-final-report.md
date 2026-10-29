# Trilha Code — Beta 6.1: relatório final

## A. Resultado executivo

A jornada Beta 6 foi validada com HTTP, persistência MongoDB e Chromium em infraestrutura descartável. A causa do bloqueio anterior foi incompatibilidade entre rede Docker interna e porta publicada; foi removida a necessidade de binding host, sem relaxar o gate. Encontrou-se e corrigiu-se uma incompatibilidade real na leitura da fila do avaliador. Autenticação, aula, quiz, submissão, correção autorizada, feedback e progresso passaram na prova integrada.

**Veredito: JORNADA DE APRENDIZAGEM VALIDADA PONTA A PONTA EM AMBIENTE ISOLADO — LANÇAMENTO NÃO AUTORIZADO.** Esta evidência não autoriza merge, publicação, acesso de alunos reais ou deploy.

## B. Git e isolamento

Base exata `e31486ad6ba22909afb50a8faea6c05e7b144fb5`, na sequência confirmada da Beta 6 (`6fae4dfd`, `f962f05f`, `d0a68adb`, `e31486ad`). A branch sugerida `codex/beta6-1-http-e2e-validation` já existia na base Beta 6 e foi preservada sem alteração; esta execução usa a branch isolada `codex/beta6-1-http-e2e-validation-isolated`. Worktree: `C:\Users\Joao\.codex\worktrees\trilhacode-beta6-1-http-e2e\trilhacodeprod`. O checkout original e as demais worktrees não foram modificados. O commit local de implementação é `c1aed5b1c38897bdefb309f1e1838f892799324b`; a documentação final também foi commitada localmente.

## C. Diagnóstico Docker

O harness Beta 6 exigia rede `--internal` e binding loopback publicado. No Docker Desktop, `HostConfig.PortBindings` podia existir sem um `NetworkSettings.Ports` efetivo. O gate detectava corretamente que o caminho host não estava comprovado e abortava antes do cliente Mongo. Não era seguro aceitar o binding solicitado como efetivo. A Beta 6.1 usa rede interna sem portas publicadas e executa runner/API/Vite/Chromium no runner; Mongo só é acessado pelo DNS interno do contêiner exclusivo. Detalhes em [diagnóstico de binding](beta6-1-docker-binding-diagnosis.md).

## D. Correção do harness e E. gate

O teste persistente requer opt-in específico. IDs completos, labels e token da execução, rede interna e membership exato, imagem, banco, credenciais, tmpfs, ausência de portas/mounts e marcador são verificados antes de importar aplicação, conectar, migrar ou semear. URI só é entregue ao runner após o gate do host; o helper interno verifica servidor MongoDB 7, WiredTiger e owner marker. Falha ou divergência fecha a execução sem fallback a localhost.

## F. Ambiente descartável

MongoDB `7.0.43`, contexto Docker `desktop-linux`, bridge interna específica, IDs gerados por execução, credenciais sintéticas aleatórias, banco exclusivo, tmpfs e nenhum volume persistente ou binding. A auditoria final encontrou zero recursos Beta 6.1 por label. Não acessamos o Mongo da Beta 4, qualquer banco operacional, staging ou produção.

## G. HTTP e H. autenticação

`tests/test_beta6_learning_journey.py`: **1 passed** usando o app/rotas reais e persistência descartável. Login de aluno, login de instrutor e sessão foram exercitados pela stack de autenticação existente. Requisição anônima recebeu `401`; o cliente não escolheu identidade/proprietário. A leitura da fila foi corrigida para dispensar Origin de mutação em GET, mantendo `submissions.grade` e escopo por trilha.

## I. autorização

O editor sem escopo recebeu `403` na fila e `404` em detalhe/claim. O avaliador com `submissions.grade` e escopo explícito sintético na trilha consultou, reivindicou e avaliou. Outro aluno não acessou submissão alheia (`404`). Isso valida somente a autorização experimental nesse banco; não integra nem substitui o IAM/grants operacionais C11–C15.

## J. quiz e K. submissão

O leitor HTTP e o browser não receberam gabarito. O servidor registrou a tentativa com versão publicada e calculou feedback. Submissão manual idempotente repetida com a mesma chave retornou a mesma identidade; permaneceu vinculada ao aluno e aguardando avaliação. O envio não foi aceito como conclusão/aprovação.

## L. correção e M. progresso

O avaliador autorizado registrou feedback e aprovação. Aluno recuperou o feedback após nova autenticação e consulta. O estado da submissão, quiz concluído e exercício concluído ficaram persistidos; recarga do browser confirmou a consulta posterior. O teste não prova atomicidade global de todas as projeções, nem resolução de escrita com resposta indeterminada.

## N. frontend e O. browser E2E

Playwright Chromium: **1 passed** com API Uvicorn, Vite, navegador e MongoDB na rede isolada. A jornada percorreu login, leitura, quiz, envio de exercício, rejeição de avaliador sem escopo, correção, feedback e progresso após reload. Typecheck, lint, 29 testes Vitest e build passaram. O bundle principal tem 505,92 kB e excede o limite de aviso de 500 kB. A validação foi desktop Chromium, não homologação visual/mobile completa.

## P. testes negativos

Foram verificados: anonimato, gabarito/rubrica/resposta privada, alteração direta de progresso pelo cliente, fila/detalhe/claim sem escopo e leitura de submissão por outro aluno. O feedback aprovado foi visível ao proprietário. Não foram exercitados nesta fase: expiração e desativação de sessão, versão manipulada no browser, concorrência de duas correções ou todas as falhas entre gravação de correção e projeção de progresso.

## Q. regressões

68 testes offline de isolamento e contratos passaram. Ruff, MyPy direcionado, compilação e `git diff --check` passaram. A suíte unitária completa e as suites persistentes históricas não foram repetidas: a inspeção encontrou um teste Docker histórico que cria redes/contêineres fora do ownership da Beta 6.1; ele foi evitado para não tocar recursos sem essa proteção. O relatório Beta 6 reportou historicamente 334 passed/43 skipped/26 subtests, mas não é resultado novo. Ver [regressões](beta6-1-regression-results.md).

## R. segurança editorial

Sem importação, promoção, publicação curricular operacional, alteração de geração ou escrita de coleções editoriais ativas. A prova de aprendizagem não elimina o bypass de writer direto demonstrado na C16. A integração editorial continua bloqueada pelos controles C8–C16.

## S. isolamento e T. gates

Todos os componentes HTTP/browser/Mongo foram locais ao runner isolado; HTTPS externo foi bloqueado no browser. A imagem de teste foi construída com dependências declaradas e pacotes-base obtidos de seus repositórios; nenhuma API de produto externa foi usada durante a jornada. Recursos foram removidos após confirmação de ownership. Gates preservados: G1 PARTIAL; G2 NOT_VERIFIED; G3 NOT_VERIFIED; G4 PARTIAL; G5 NOT_VERIFIED; G6 PARTIAL; G7 PARTIAL; G8 NOT_VERIFIED; G9 BLOCKED; G10 BLOCKED. ADR-008 continua BLOCKED.

## U. arquivos alterados/criados

* Modificado: `backend/routes_submissions.py`.
* Modificado: `backend/tests/conftest.py`.
* Criados: `backend/test_support/Dockerfile.beta6_1_e2e`, `Dockerfile.beta6_1_e2e.dockerignore`, `beta6_1_docker_harness.py`, `beta6_1_internal_target.py`, `beta6_1_seed_fixture.py`, `run_beta6_1_http.py`, `run_beta6_1_journey.py`.
* Criados: `backend/unit_tests/test_beta6_1_internal_target.py`, `frontend/e2e/beta6-1-learning-journey.spec.ts`.
* Criados: os cinco relatórios `docs/beta/beta6-1-*.md` desta fase.

## V. limitações

A autorização de avaliador é fixture experimental, não lifecycle real de grants. A prova não abrange concorrência de revisão, falhas distribuídas de confirmação, expiração de sessão, acessibilidade e dispositivos móveis. O progresso reconcilia por operações existentes, sem atomicidade única demonstrada. O bundle permanece acima do aviso. Não foi validada implantação ou exposição de serviço.

## W. próximo incremento

Antes de qualquer piloto com pessoas: especificar e implementar a ligação da jornada ao IAM/grants real com revogação ordenada, testar concorrência/indeterminação da correção e progresso, cobrir expiração de sessão e concluir homologação responsiva/acessível. Qualquer ativação exige autorização separada e continua subordinada a ADR-008 e aos gates.

## X. veredito

**JORNADA DE APRENDIZAGEM VALIDADA PONTA A PONTA EM AMBIENTE ISOLADO — LANÇAMENTO NÃO AUTORIZADO.**
