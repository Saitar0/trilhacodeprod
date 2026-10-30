# Relatório — Etapa 14H.1

**Data:** 2026-10-28
**Escopo:** contrato offline e projeções de leitura para conteúdo compartilhado.
**Estado:** implementação isolada; sem publicação, persistência operacional ou importação.

## Resultado

[IMPLEMENTADO] O novo módulo backend/curriculum_contract/shared_content.py usa IntermediateContract, SharedPlacement, os blocos tipados e validate_contract já existentes. Não criou uma segunda entidade curricular nem alterou a versão trilhacode.intermediate/1.2.

[IMPLEMENTADO] O índice offline resolve colocações para blocos canônicos por referência. Cada projeção interna de assunto mantém as colocações separadas de um mapa canônico deduplicado; o payload do bloco não é copiado para cada colocação. A ordenação contextual é (order, ref).

[IMPLEMENTADO] A projeção interna é uma fotografia imutável de valores JSON e preserva o manifesto, o assunto, os blocos canônicos completos e as colocações completas, incluindo IDs, owner_ref, ordem de autoria, status existente, proveniência e progress_scope.

[IMPLEMENTADO] A projeção de apresentação usa uma allowlist por tipo. Quiz expõe somente título, enunciado, formato e alternativas públicas; prática expõe enunciado, linguagem e código inicial; flashcard expõe somente a frente. Rubrica, feedback, checklist e critérios de aceite ficam sem payload público até existir política de audiência/revelação aprovada. Tipos sem política são rejeitados.

[TESTADO] Não houve escrita em MongoDB, execução do importador, criação de estado publicado, registro de progresso ou ligação a rotas, renderizadores, quizzes ou frontend.

## Contagens verificadas

| Elemento | Quantidade |
| --- | ---: |
| Blocos compartilhados canônicos | 406 |
| Colocações | 1.001 |
| Assuntos consumidores distintos | 284 |
| Colocações com progress_scope: undecided | 1.001 |
| Escopos diferentes de undecided | 0 |

Tipos compartilhados: 180 practice, 90 rubric, 90 feedback, 26 checklist, 17 quiz, 1 acceptance_criteria e 2 flashcard. Todos os 406 blocos possuem ao menos uma colocação; blocos compartilhados mantêm owner_ref nulo conforme a validação existente, e a origem permanece em provenance.

## Pré-voo e preservação

- Worktree: C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod.
- Branch: migracao-estrutura.
- HEAD: 147dc68b81169f66b0ba3802fa2f26e5130923a3.
- O índice não contém entradas staged.
- Antes da Etapa 14H.1 havia 25 arquivos rastreados modificados, 138 arquivos não rastreados, nenhuma exclusão rastreada. Os 25 modificados foram comparados ao blob do índice e são alterações preexistentes.
- git status e git diff falham com fatal: this operation must be run in a work tree. O worktree, o arquivo .git, o vínculo gitdir, o commondir, HEAD e a lista registrada pelo Git foram conferidos sem reparar metadados. O inventário foi obtido por git ls-files --stage, git diff --cached --name-only, git ls-files -m, git hash-object --path, git ls-files --others, git ls-files -d e git ls-files -k. Nenhum dos 25 arquivos rastreados foi alterado por esta etapa. O comando git diff --check foi repetido ao final e falhou com a mesma mensagem de worktree; a checagem manual equivalente de whitespace e LF final passou nos cinco arquivos novos.
- Os cinco caminhos novos estavam ausentes no início. Nenhum arquivo preexistente foi sobrescrito.

SHA-256 do bundle antes da alteração: 43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2. A verificação final foi repetida após a implementação.

## Testes e verificações

- [TESTADO] 92 passed na suíte selecionada: projeção compartilhada nova, contratos, leitor do bundle e planejador offline.
- [TESTADO] Ruff lint: aprovado nos dois arquivos Python novos.
- [TESTADO] Ruff format check: os dois arquivos Python novos já formatados.
- [TESTADO] Mypy focado: módulo e teste verificados separadamente; ambos sem erros.
- [TESTADO] Compilação sintática via ast.parse, sem gerar bytecode no repositório.
- [TESTADO] Verificação manual de whitespace e newline dos arquivos novos.
- A primeira execução dos testes de compatibilidade teve três erros de setup porque tmp_path padrão não podia criar diretórios no ambiente restrito. A repetição com --basetemp em pasta TEMP exclusiva passou integralmente. Nenhum teste de banco foi executado.

## Arquivos desta etapa

- backend/curriculum_contract/shared_content.py
- backend/unit_tests/test_shared_content_projection.py
- docs/migracao/RELATORIO_ETAPA_14H_1.md
- docs/migracao/CONTRATO_IDENTIDADE_COMPARTILHADA_14H_1.md
- docs/migracao/MATRIZ_PROGRESSO_COMPARTILHADO_14H_1.md

## Decisões e limitações

[PENDENTE] As 1.001 colocações continuam com progress_scope: undecided. A recomendação anterior de progresso independente por colocação continua sendo apenas [PROPOSTA]; nenhum valor ou comportamento foi escolhido nesta etapa.

[PENDENTE] Não há versão de conteúdo própria nos modelos atuais. O snapshot conserva versão do contrato, revisão do pacote, hashes e proveniência já existentes; não inventa números de versão de conteúdo.

[PENDENTE] Feedbacks, rubricas, checklists e critérios de aceite não possuem regra aprovada de audiência na projeção pública. Por segurança, seus payloads são omitidos. A projeção é offline e não determina publicação.

[ESPECIFICADO] A matriz compara progresso global, por colocação e híbrido, incluindo o índice atual do progresso e o escopo atual de tentativas de quiz. A decisão humana continua necessária.

## Estado do Git

Nenhum comando de staging ou commit foi executado. Nenhum banco foi acessado. O estado final e o SHA do bundle foram conferidos ao encerrar. O erro de Git porcelain permaneceu, sem alteração de metadados.
