# Relatório — Etapa 14F.1

## Veredito

**HOMOLOGAÇÃO PARCIAL — bloqueada para persistência transacional real e isolamento por RBAC MongoDB.** O ambiente não permitiu iniciar o Docker Engine e não havia URI explícita para replica set descartável. O serviço MongoDB que já estava em execução não foi consultado, pois sua identidade e finalidade não estavam comprovadas.

Não foram realizadas importação, publicação, migração de banco, conexão com rotas operacionais ou alterações de dados curriculares.

## Pré-voo e preservação

- Diretório: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch: `migracao-estrutura`.
- HEAD: `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Índice: vazio.
- Estado no início: 25 arquivos rastreados modificados e 123 não rastreados, incluindo trabalho local de etapas anteriores. Foram preservados; não houve staging ou commit.
- SHA-256 do pacote curricular: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- Hashes 14C, 14D e 14E conferidos novamente e iguais aos valores homologados na 14F.

## Ambiente MongoDB

- Windows PowerShell; Python 3.13.15, PyMongo 4.17.0 e Pydantic 2.13.5.
- Docker CLI 29.8.2 e Docker Compose v5.6.0 estavam instalados.
- O contexto Docker apontava ao pipe local `dockerDesktopLinuxEngine`, mas o Engine estava indisponível.
- O serviço `com.docker.service` estava parado. A tentativa de iniciar o serviço falhou com “Cannot open 'com.docker.service' service on computer”; não foi alterada configuração nem instalado serviço.
- `mongod`, `mongosh` e `mongo` não estavam no PATH. Havia um serviço Windows chamado `MongoDB` em execução automática, de identidade desconhecida; não foi consultado nem utilizado.
- Não havia variáveis de ambiente de URI de teste.
- Nenhuma conexão, `hello`, leitura ou escrita Mongo foi realizada.

## Auditoria e correções da camada

O repositório está isolado em `backend/curriculum_contract/activity_persistence.py` e não é criado no startup nem ligado a rotas. A leitura idempotente anterior à transação é somente leitura; as leituras que decidem criação/revisão e as gravações usam a mesma sessão passada a `with_transaction`.

Durante a revisão, foi fechada a integridade do ponteiro: antes de avançar um head existente, o repositório valida o modelo do head, a presença do par público/privado, tipo/identidade, hashes e evento de criação. Se o head estiver quebrado ou houver histórico sem head, a operação falha fechado. Uma regressão fake confirma que a tentativa não cria revisão nem move o head.

O tratamento de erro também foi separado: ausência comprovada de suporte transacional gera `ActivityTransactionsRequiredError`; rótulo `UnknownTransactionCommitResult` e interrupções de conexão geram `ActivityTransactionOutcomeUnknownError`, orientando replay do mesmo conteúdo; outras falhas PyMongo geram `ActivityTransactionFailedError`. O replay após resultado simulado desconhecido retorna `unchanged` no fake. Esses testes verificam lógica, não semântica do servidor Mongo.

Uma revisão independente confirmou que as leituras decisórias, gravações, evento e CAS do head compartilham a mesma sessão. Não encontrou outro achado concreto após a validação adicional do head. A revisão também confirmou que RBAC Mongo não está configurado no código.

## Testes e qualidade

```text
py -3.13 -m pytest unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py -q
20 passed, 4 skipped

py -3.13 -m pytest unit_tests/test_typed_activities.py unit_tests/test_experimental_quiz_converter.py unit_tests/test_quiz_grading.py unit_tests/test_quiz_api_contracts.py unit_tests/test_curriculum_bulk_import.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py -q
99 passed, 4 skipped

py -3.13 -m ruff check curriculum_contract/activity_persistence.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py
All checks passed

py -3.13 -m ruff format --check curriculum_contract/activity_persistence.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py
3 files already formatted

py -3.13 -m mypy --explicit-package-bases --follow-imports=silent curriculum_contract/activity_persistence.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py
Success: no issues found in 3 source files

py -3.13 -m py_compile curriculum_contract/activity_persistence.py unit_tests/test_typed_activity_persistence.py unit_tests/test_typed_activity_persistence_mongodb.py
passed
```

Os quatro testes ignorados são opt-in e requerem URI explícita, replica set identificado e confirmação de instância descartável. Eles cobrem, quando executados, persistência real dos seis tipos, índices, replay, revisão obsoleta, rollback após escrita staged e concorrência. **Nenhum deles foi executado contra MongoDB nesta etapa.** Os 20/99 testes aprovados usam validação Pydantic e repositório fake; não comprovam atomicidade, rollback, unicidade de índice, concorrência entre processos ou failover.

`git diff --check` passou; Git apenas reportou o aviso conhecido de conversão LF/CRLF do JSON já modificado no working tree.

## Cobertura dos requisitos

| Requisito | Resultado |
|---|---|
| Auditoria de sessões e transação no código | Confirmada estaticamente; todas as gravações do par, evento e head usam uma sessão |
| Validação do ponteiro corrente | Implementada; regressão unitária fake aprovada |
| Transações, rollback e estado persistido | Não homologados em Mongo real |
| Concorrência Mongo e CAS sob corrida | Declarados no teste opt-in, não executados |
| Índices Mongo | Definições inspecionadas no código; índices reais não consultados/criados |
| RBAC por coleção e credenciais distintas | Não testado nem configurado; bloqueador para alegar isolamento no banco |
| Regressão dos quizzes existentes | Testes unitários relevantes aprovados; nenhum endpoint foi conectado ao repositório editorial |
| Integridade curricular | Hash esperado do JSON preservado; sem acesso ao pacote para importação |

## Pendências de homologação

1. Disponibilizar um replica set descartável iniciado para a execução, com URI local explícita e banco exclusivo; confirmar a instância antes de qualquer operação.
2. Executar os quatro testes opt-in e registrar versão/topologia, índices, rollback, concorrência e resultados persistidos.
3. Criar usuários Mongo distintos no ambiente descartável e demonstrar que o principal público não consegue ler `typed_activity_private_versions`; validar usuário editorial e acesso privado sem usar credencial administrativa como evidência.
4. Repetir validação de RBAC e compatibilidade de topologia antes de integração futura. Um replica set de um membro não demonstra eleição/failover de produção.

**Recomendação:** não integrar a persistência ao frontend, às rotas ou ao importador até concluir os itens 1–3. Não declarar prontidão operacional.
