# Relatório — Etapa 13C.1: backend seguro de quizzes

## Resultado

**PARCIALMENTE CONCLUÍDA — implementação funcional pronta para revisão técnica, sem ativação no frontend ou homologação de produção.**

O backend publica versões imutáveis, corrige tentativas no servidor, persiste histórico por usuário e versão, aplica o limite de três tentativas e libera a revisão após a terceira tentativa válida. A aprovação usa 70% sem arredondamento prévio. Nenhum dado foi escrito no MongoDB de produção; os testes de integração usaram somente o banco local descartável criado pelo harness.

O resultado é parcial porque permanecem limites que esta etapa não podia resolver silenciosamente: os bloqueios curriculares existentes ainda consultam o progresso legado informado pelo cliente; a divulgação imediata da pontuação pode permitir inferência em quizzes de uma questão; e os testes não simularam reinício do processo nem falha de rede após a gravação confirmada. Esses pontos estão detalhados abaixo.

## Pré-voo e integridade

- Worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch e HEAD de base: `migracao-estrutura`, `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- O índice Git permaneceu vazio; nenhum commit foi criado.
- As 2.890 unidades/arquivos da árvore migrada continuam presentes e sem alterações nesta execução.
- Os 13 arquivos do contrato intermediário permanecem presentes: 12 artefatos listados no manifesto e o próprio `integrity_manifest.json`. Os 12 hashes listados foram verificados, sem divergências.
- SHA-256 do JSON legado `docs/courses/trilhacode/trilha-code-bulk-import.json`: `43125c5902168def6359e514ad80602a1f7579157e1a0bb16f1f2212ee4c18e7`.
- Os artefatos locais preexistentes e não rastreados foram preservados. Não houve reset, limpeza, stash, merge, rebase ou push.

## Implementação

### Arquitetura e arquivos

| Arquivo | Alteração |
|---|---|
| `backend/schemas/quizzes.py` | Schemas estritos para quiz público, envio, resultado, histórico, revisão e publicação; campos extras no request são recusados. |
| `backend/services/quizzes.py` | Publicação de snapshots, validação da fonte, avaliação determinística, idempotência, atualização concorrente, histórico e revisão autorizada. |
| `backend/routes_quizzes.py` | Rotas autenticadas para leitura, tentativa, histórico e revisão; publicação restrita à permissão existente `content.publish`. |
| `backend/migrations/0003_quiz_attempts.py` | Criação dos índices para versões e agregados de tentativa. |
| `backend/migrations/__init__.py` | Registra a migração 0003 e passa a exigir sua versão no readiness. |
| `backend/indexes.py` | Declara índices únicos e inclui verificações de duplicidade no preflight operacional. |
| `backend/server.py` | Registra o roteador, exige schema v3 em `/ready` e permite `Idempotency-Key` no CORS. |
| `backend/tests/test_quizzes.py` | Testes HTTP integrados com autenticação e MongoDB local descartável. |
| `backend/unit_tests/test_quiz_grading.py` | Testes do avaliador, de referências tipadas e da allowlist do resultado. |
| `backend/tests/test_integrity_concurrency.py` | Atualiza a contagem esperada dos índices. |
| `ops/g2/preflight-manifest-v1.json` | Inclui verificações dos dois índices únicos novos e de duplicatas existentes. |
| `docs/migracao/ESPECIFICACAO_QUIZZES.md` | Registra política aprovada, comportamento implementado e limites. |
| `docs/migracao/CONTRATOS_API_QUIZZES.md` | Atualiza os contratos HTTP implementados e exemplos sem chave exposta. |
| `docs/migracao/IMPLEMENTACAO_BACKEND_QUIZZES.md` | Documenta arquitetura, persistência, segurança, compatibilidade e operação. |
| `docs/migracao/RELATORIO_ETAPA_13C1.md` | Este relatório. |

### Persistência e concorrência

- `quiz_versions` guarda snapshot privado e imutável do quiz, incluindo chave de correção, explicação, hash e proveniência.
- `quiz_catalog` aponta para a versão ativa.
- `quiz_progress` guarda um agregado por usuário/quiz/versão e até três tentativas imutáveis. A pontuação exata é armazenada como Decimal128; a apresentação é arredondada a duas casas.
- Índices únicos: `(quiz_id, content_hash)` em `quiz_versions` e `(user_id, quiz_id, version_id)` em `quiz_progress`.
- Uma operação condicional `find_one_and_update` incrementa contador e adiciona a tentativa no mesmo documento MongoDB. Não há reserva separada nem transação entre coleções.
- `Idempotency-Key` é armazenada como SHA-256. A mesma chave e payload retorna o resultado persistido; a chave com payload diferente retorna 409. A chave bruta não é persistida.
- Se a gravação for confirmada mas a resposta se perder, um retry com a mesma chave recupera o resultado. Não foi injetada uma falha real de rede pós-gravação; essa recuperação é coberta pela lógica de reenvio e pelos testes de repetição, não por simulação de transporte.
- A consulta de histórico usa paginação por agregação no MongoDB e não aplica teto fixo ao número de versões consultadas.

### Política aplicada

- Três tentativas válidas por usuário, quiz e versão.
- Múltipla escolha com uma resposta correta; cada questão tem peso uniforme.
- Aprovação se `correct_answers * 100 >= 70 * total_questions`, antes do arredondamento.
- Questões omitidas contam como incorretas. IDs de questão/alternativa desconhecidos, respostas duplicadas, quiz vazio, pesos explícitos e formatos não avaliados são rejeitados sem consumir tentativa.
- Aprovação antecipada não encerra tentativas nem libera a revisão.
- Melhor pontuação preservada; todas as tentativas válidas permanecem no histórico.
- Quiz alterado gera outro snapshot e limite por versão. Repetir publicação de conteúdo idêntico reutiliza o snapshot correspondente.

## Endpoints

- `GET /api/quizzes/{quiz_id}` — sessão autenticada; visão pública com enunciados, alternativas e estado resumido do usuário.
- `POST /api/quizzes/{quiz_id}/attempts` — sessão e `Idempotency-Key`; recebe apenas versão e respostas.
- `GET /api/quizzes/{quiz_id}/attempts` — histórico do usuário autenticado, paginado.
- `GET /api/quizzes/{quiz_id}/versions/{version_id}/review` — chave e explicações somente após três tentativas válidas daquela versão.
- `POST /api/admin/quizzes/{quiz_id}/versions` — publicação restrita a `content.publish`, sem retornar a chave.

Schemas de saída são allowlists. Quiz público, resultado e histórico não incluem `correct_index`, `correct_option_id`, explicações, respostas submetidas, hash de conteúdo nem contagem de respostas corretas. A revisão inclui a alternativa correta e a explicação somente depois da checagem de elegibilidade no servidor.

**Risco residual da regra aprovada:** o resultado precisa retornar a pontuação imediatamente. Em um quiz com uma questão, a pontuação permite inferir se a resposta foi correta. A chave não é enviada diretamente e a revisão continua bloqueada, mas eliminar essa inferência exigiria mudar a regra de divulgação imediata da nota.

## Compatibilidade com o contrato intermediário

A publicação aceita o formato legado de bloco (`question`, `options`, `correct_index`) e uma projeção tipada de `QuizBlock`/`AnswerKeyBlock` (`prompt`, opções com referências e gabarito associado). Valida a identidade recíproca quiz–gabarito, a alternativa correta, explicação e proveniência. Um gabarito tipado sem alternativa correta avaliável é recusado mesmo se também houver `correct_index` legado.

Um teste com modelos reais do pacote `curriculum_contract` comprova preservação de IDs, ordem das opções, referências, explicação e proveniência. Isso valida a fronteira de publicação por fixture; não importa nem converte os 3.431 blocos do contrato intermediário.

## Progresso curricular e autorização

O serviço não lê nem escreve `POST /api/progress` para calcular pontuação, aprovação, tentativas ou elegibilidade de revisão. O endpoint legado, em `backend/schemas/progress.py` e `backend/services/progress.py`, aceita `status`, `block_id` e um `data` arbitrário; o timestamp de atualização é atribuído pelo servidor. Não foi encontrado campo de data controlado pelo cliente nesse request.

As rotas novas reutilizam `assert_visible` e `assert_unlocked`. Este último consulta o grafo de pré-requisitos e registros `progress` com status `completed`. Portanto, a nota e a aprovação do quiz são autoritativas, mas a autorização por pré-requisito ainda pode depender de progresso não-quiz informado pelo cliente. O comportamento legado não foi alterado por estar fora da autorização desta etapa. É necessária uma decisão/etapa específica para usar evidência confiável nos bloqueios curriculares.

## Verificações executadas

Ambiente: Python 3.13; testes integrados contra MongoDB local em URL direta e banco aleatório `test_<uuid>`, protegido por `backend/test_support/mongo_target.py`. A fixture verifica o prefixo seguro e apaga somente esse banco descartável no teardown. Nenhum acesso ao MongoDB de produção ocorreu.

| Verificação | Comando | Resultado |
|---|---|---|
| Testes unitários | `py -3.13 -m pytest unit_tests -q --tb=short` | 206 passed, 37 skipped. |
| Testes de API/integração | `py -3.13 -m pytest -q --tb=short` | 105 passed. |
| Lint | `py -3.13 -m ruff check backend` | Passou. |
| Formatação dos módulos e testes novos | `py -3.13 -m ruff format --check` nos seis arquivos novos | Passou. |
| Verificação de formatação em todos os arquivos alterados | `ruff format --check` nos dez arquivos Python alterados | Aponta quatro arquivos legados que o formatter reformataria amplamente: `backend/indexes.py`, `backend/migrations/__init__.py`, `backend/server.py` e `backend/tests/test_integrity_concurrency.py`. Não foi aplicado reformatamento amplo fora do escopo; os arquivos novos estão formatados e as linhas novas de roteamento foram ajustadas. |
| Tipagem | `py -3.13 -m mypy --explicit-package-bases --follow-imports=silent --disable-error-code=import-not-found ...` em dez arquivos | Passou. O código opcional de Sentry não está instalado localmente; foi suprimido somente o diagnóstico `import-not-found`. |
| Compilação | `py -3.13 -m compileall -q ...` nos módulos/testes alterados | Passou. |
| Diff | `git diff --check` | Passou. |

Os 37 testes ignorados são os skips existentes na suíte unitária. O teste de persistência usa clientes autenticados independentes, mas não reinicia um processo do servidor. A concorrência e os índices foram verificados contra MongoDB standalone local; a configuração de implantação com replica set/failover não foi testada.

## Limitações e próximas decisões

1. O renderer existente permanece incompatível com a nova API e não foi modificado. Até a Etapa 13C.2, o novo fluxo não está integrado ao navegador.
2. Não há rate limit específico de quiz. Não foi escolhido um limite novo nesta etapa.
3. O avaliador implementado aceita apenas múltipla escolha com uma resposta correta; outros formatos são rejeitados explicitamente.
4. Não há integração da aprovação com conclusão curricular.
5. Bloqueios de pré-requisito ainda usam o sistema legado de progresso, como descrito acima.
6. Publicar a migração de schema 0003 será pré-requisito operacional para readiness. Ela foi executada somente pelo harness de teste descartável, nunca em banco real.
7. Não há teste de processo reiniciado nem falha de transporte após gravação; ambos devem ser cobertos antes da homologação operacional.
8. O conflito conhecido entre `google-api-core==2.33.0` e `grpcio-status==1.71.2` não foi alterado. Nenhuma dependência ou lockfile foi modificado.

## Arquivos curriculares e JSON

Nenhum arquivo sob `Conteudos_migrado/` foi alterado. O total continua em 2.890. Os 13 artefatos de `docs/migracao/contrato_intermediario/` não foram alterados. O JSON legado conserva o SHA-256 registrado no pré-voo. Nenhum importador, frontend ou banco de produção foi executado ou acessado.
