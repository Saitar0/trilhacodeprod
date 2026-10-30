# Relatório — Etapa 14F

## Resultado

Foi implementado um repositório Mongo isolado para versões editoriais de atividades tipadas. Ele separa snapshots sem gabarito, snapshots privados, eventos de criação e um ponteiro de revisão por atividade. A camada não foi conectada a rotas, `quiz_versions`, publicação, importação curricular, progresso ou inicialização da aplicação.

**Conclusão parcial.** Os contratos e testes unitários passaram. A homologação de persistência Mongo real não foi executada porque não havia `TRILHACODE_TYPED_ACTIVITY_MONGO_TEST_URI`, `MONGO_URL_TEST`, Docker daemon nem `mongod` instalado. Nenhuma instância local desconhecida foi consultada. O teste de integração opcional foi ignorado antes de abrir conexão.

## Arquivos desta etapa

- `backend/curriculum_contract/activity_persistence.py`
- `backend/unit_tests/test_typed_activity_persistence.py`
- `backend/unit_tests/test_typed_activity_persistence_mongodb.py`
- `docs/migracao/RELATORIO_ETAPA_14F.md`
- `docs/migracao/CONTRATO_PERSISTENCIA_ATIVIDADES.md`
- `docs/migracao/MATRIZ_SEGURANCA_ATIVIDADES.md`
- `docs/migracao/PLANO_INTEGRACAO_IMPORTADOR_ATIVIDADES.md`

## Modelo implementado

O pacote `trilhacode.typed_activities/1.0` é persistido por `TypedActivityDraftStore` em quatro coleções novas e isoladas:

1. `typed_activity_public_versions`: identidade curricular, tipo, versão da fonte, conteúdo público allowlisted, Markdown da questão, proveniência, hashes públicos, status inicial e autor.
2. `typed_activity_private_versions`: gabarito/critério privado, proveniência da chave e hash integral privado. Há um registro complementar mesmo quando a atividade não tem chave, com `private_payload: null`.
3. `typed_activity_version_events`: evento append-only de criação, sem enunciado, gabarito, explicação ou hash derivado de conteúdo privado.
4. `typed_activity_heads`: ponteiro único para a revisão atual e contador monotônico, usado para detectar revisões concorrentes com compare-and-swap dentro da transação.

O armazenamento é somente editorial. Os quizzes operacionais continuam tendo `quiz_versions` como fonte de verdade. Nenhuma rota nem serviço de aluno lê as novas coleções. A relação entre IDs de atividade e quizzes operacionais continua pendente de reconciliação com um snapshot autorizado.

## Versões e idempotência

- `activity_ref` preserva o ID curricular.
- Cada gravação nova recebe um ObjectId operacional que permanece estável após a criação.
- Um SHA-256 canônico de conteúdo, guardado somente na coleção privada, identifica reexecuções sem revelar um hash derivado do gabarito em projeções públicas.
- Reenvio do mesmo conteúdo retorna `unchanged`; conteúdo diferente cria outra versão e não altera as anteriores.
- Para criar uma revisão após a primeira versão, o chamador informa `expected_version_id`. A versão-base é comparada atomicamente ao head; dois editores que partem da mesma versão não conseguem gravar revisões divergentes como se ambas fossem atuais. Uma gravação sem a versão-base atual falha em conflito.
- Tentativa de mudar o estado editorial de uma versão já salva retorna conflito. Transições de estado e eventos de revisão ainda não foram implementados.
- `publishable` pode ser armazenado somente como rótulo editorial. O repositório rejeita `published`; nenhum status cria publicação operacional.
- No replay, o par público/privado é revalidado, incluindo tipo, versão de fonte, payload, hashes e correspondência de IDs. Histórico sem ponteiro atual falha fechado.

Uma revisão técnica independente identificou dois riscos durante esta execução: ausência de conflito explícito para revisões divergentes simultâneas e checagem incompleta de identidade no replay idempotente. Foram tratados com head compare-and-swap, versão-base obrigatória para revisões subsequentes e validação do par completo antes de retornar `unchanged`. Testes fake cobrem esses caminhos; sua atomicidade concorrente real ainda depende do teste em replica set.

## Atomicidade e índices

A gravação do par público/privado, evento e head ocorre em uma transação MongoDB. Não existe fallback para gravação parcial. O repositório exige replica set ou mongos; em standalone, a operação deve falhar sem deixar qualquer um dos quatro documentos persistido.

`ensure_indexes()` cria índices únicos para (atividade, versão), (atividade, hash integral), evento de criação e head de atividade, além do índice de histórico. A função só é invocada pelo repositório explícito; não foi conectada ao inicializador global nem a uma migration de produção.

**Não comprovado em Mongo real nesta execução:** transações, rollback, índices, concorrência entre processos e comportamento de failover. Testes em memória simulam os caminhos do repositório, mas não são evidência de atomicidade Mongo.

## Autorização e projeções

- Escrita editorial: permissão existente `content.write`.
- Leitura do snapshot sem chave: `content.read`.
- Leitura privada: `submissions.grade`.
- As autorizações usam `permissions.has_permission`; não há endpoint administrativo ou público novo.
- A consulta pública lê apenas a coleção pública e usa projeção allowlist. A consulta privada lê a coleção privada separadamente e verifica a existência/tipo do companheiro público.
- Serializadores e eventos públicos não incluem chave, explicação privada ou hash integral.
- Acesso por RBAC do MongoDB às coleções e criptografia em repouso precisam ser homologados na topologia real. Esta etapa não alterou usuários/roles do banco.

## Compatibilidade curricular e funcional

Os seis tipos são representáveis sem adicionar respostas ou critérios. As atividades de associação/ordenação incompletas permanecem sem decomposição inventada; respostas curtas e discursivas não ganham correção automática; R1–R5 continuam sem chave e sem pontuação. Os 143 candidatos permanecem apenas `structurally_validated` no pacote 14E — não são publicados por esta persistência.

A atividade tipada não substitui snapshots publicados existentes. Uma integração futura deverá mapear questões objetivas aprovadas para o serviço atual e preservar `quiz_versions`, histórico, limite de três tentativas, nota de 70% e revelação após a terceira tentativa.

## Testes e verificações

Testes unitários focados executados:

```text
py -3.13 -m pytest unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py -q
17 passed, 1 skipped

py -3.13 -m pytest unit_tests/test_typed_activities.py unit_tests/test_experimental_quiz_converter.py unit_tests/test_quiz_grading.py unit_tests/test_quiz_api_contracts.py unit_tests/test_curriculum_bulk_import.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py -q
96 passed, 1 skipped

py -3.13 -m ruff check curriculum_contract/activity_persistence.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py
All checks passed

py -3.13 -m ruff format --check curriculum_contract/activity_persistence.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py
3 files already formatted

py -3.13 -m mypy --explicit-package-bases --follow-imports=silent curriculum_contract/activity_persistence.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py
Success: no issues found in 3 source files

py -3.13 -m py_compile curriculum_contract/activity_persistence.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py
passed

git diff --check
passed (Git reported only the existing JSON LF/CRLF working-copy warning)
```

O teste ignorado requer explicitamente `TRILHACODE_TYPED_ACTIVITY_MONGO_TEST_URI`, nome do replica set e confirmação `TRILHACODE_TYPED_ACTIVITY_MONGO_TEST_DISPOSABLE=YES`. Sem URI, não tenta localhost nem qualquer host. O conjunto de regressão executado incluiu contratos de atividades, conversor experimental, corretor de quizzes, contratos da API e adaptador curricular unitário. Testes do serviço/API que carregam `backend/tests/conftest.py` não foram executados porque o fixture legado tem fallback para `mongodb://localhost:27017`; sem configuração explícita de banco descartável, executá-los violaria o pré-voo. Nenhum teste de Mongo foi apresentado como aprovado.

O teste de fake repository demonstra apenas a lógica da camada e sua resposta a falhas simuladas. Ele não comprova transações, rollback, índices ou concorrência real do MongoDB.

## Integridade dos artefatos

Hashes verificados nesta etapa:

- JSON curricular: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- CSV 14C: `bd8487357aab3e6aa6b4831362ee52b88fa230d1f78c1bc136ae95be60fab89b`.
- CSV 14D: `ed6e48e675965bb6936a4451372641da212e2589f9696d1bba26acbe18cc10b2`.
- Inventário 14E: `dbdfed7e162116d45aa1b6a95cbb4c08c16c00325e4ef761dee11304857498d4`.

Nenhum desses arquivos foi editado; nenhuma importação, publicação ou migração foi executada.

## Pendências para homologação

1. Executar o teste opt-in em replica set descartável, com URI explícita, porta dedicada e nome de instância confirmado.
2. Validar índices, transações, rollback e concorrência no MongoDB descartável; depois homologar requisitos da topologia de produção sem acessá-la nesta etapa.
3. Aprovar RBAC Mongo para impedir que credenciais públicas leiam a coleção privada.
4. Reconciliar IDs das atividades com quizzes operacionais sem criar fonte de verdade concorrente.
5. Aprovar transições editoriais/auditoria de revisão separadas da versão imutável.
6. Manter as 358 atividades não avaliáveis objetivamente bloqueadas e as cinco revisões R1–R5 sem pontuação.

Não criar commit nesta execução.
