# Relatório — Etapa 14F.2

## Veredito

**Homologação da persistência concluída no escopo descartável testado; integração operacional continua não autorizada.** Foram executados testes em um MongoDB real, recém-iniciado nesta etapa, com autenticação e replica set de um membro. Cinco testes de integração passaram, incluindo transações, rollback, concorrência, replay e RBAC por coleção.

Isso comprova o comportamento no MongoDB 9.0.2 e na topologia usada. Não comprova failover, eleição de primário, compatibilidade com a topologia de produção ou prontidão para conectar o repositório a rotas/importador.

Não houve importação, publicação, migração de schema em banco real, conexão com rotas operacionais, acesso ao MongoDB preexistente, alteração curricular ou acesso a banco de produção.

## Pré-voo e preservação

- Worktree: `C:\Users\Joao\.codex\worktrees\fase1-migracao\trilhacodeprod`.
- Branch: `migracao-estrutura`.
- HEAD: `147dc68b81169f66b0ba3802fa2f26e5130923a3`.
- Índice no pré-voo: vazio. Nenhum commit foi criado.
- Foram preservados os arquivos rastreados modificados e não rastreados já presentes no worktree; nenhum foi limpo, sobrescrito ou incluído no índice.
- SHA-256 do pacote curricular ao final: `43e3619dc9caaa92c2e9dd8bf3bea45f2a2934e73458c297fe9206e27b1281c2`.
- A árvore curricular, o contrato intermediário e o JSON não foram modificados por esta etapa.

## Ambiente descartável

- Provisionamento por processo Windows separado usando `mongod.exe` 9.0.2 em `C:\Program Files\MongoDB\Server\9.0\bin\mongod.exe`.
- Replica set de um membro, autenticação por keyfile, bind somente em `127.0.0.1` e porta exclusiva `54159`.
- Nome do replica set: `rs14f2_f85d35f7538647afb729c99588333084`.
- PID do processo: `14088`; o executável, argumentos, PID e proprietário do listener foram conferidos antes da primeira consulta Mongo.
- Diretório de dados exclusivo: `%TEMP%\TrilhaCode14F2_f85d35f7538647afb729c99588333084\db`.
- A URI foi explícita, autenticada, restrita a loopback e ao replica set desta execução; nenhuma URI padrão ou fallback foi usada. A URI e credenciais foram mantidas fora dos relatórios e da saída de teste.
- A instância foi iniciada nesta etapa. Nenhum acesso foi feito ao serviço Windows `MongoDB` preexistente, que permaneceu em execução sem alteração, nem a `localhost:27017`.
- Docker Engine não estava acessível; foi usado o binário Mongo já instalado como processo independente, sem instalar software nem alterar configuração global.

## Correções diretamente relacionadas

Os primeiros testes reais revelaram incompatibilidades entre os fakes e a API assíncrona real do PyMongo 4.17.0, além de comprimentos de nomes de bancos acima do limite MongoDB. Também revelaram uma corrida: dois criadores com conteúdo idêntico poderiam obter conflito ao observar o mesmo head vazio.

Correções focadas:

1. `activity_persistence.py` agora usa `AsyncMongoClient.start_session()` sem `await`, conforme a API instalada. Os fakes foram ajustados para espelhar a chamada síncrona que retorna uma sessão assíncrona.
2. O repositório, ao receber um conflito de CAS, só reconcilia como replay quando encontra a mesma atividade e o mesmo hash de conteúdo privado já persistido. Se não houver hash idêntico, preserva o conflito. Não substitui conteúdo divergente.
3. Os bancos temporários dos testes usam nomes únicos curtos, dentro do limite de 63 caracteres.
4. A leitura de índices foi ajustada à API assíncrona e os testes passaram a conferir chaves e flags `unique` retornadas pelo próprio servidor.
5. Foi acrescentado um teste de incerteza de confirmação que deixa a transação Mongo real concluir e injeta a perda da confirmação no limite do cliente; o replay idêntico deve resolver para `unchanged`, sem duplicar documentos. A injeção não simula queda de rede real.

## Testes MongoDB reais

Comando, executado no backend com URI temporária explícita:

```text
py -3.13 -m pytest unit_tests/test_typed_activity_persistence_mongodb.py -vv --tb=short
5 passed
```

Casos aprovados:

1. Seis tipos de atividade, documentos públicos/privados, criação de revisões, replay, conflito de versão obsoleta, índices do servidor e credenciais RBAC distintas.
2. Rollback após a primeira escrita staged: as quatro coleções permanecem sem documentos.
3. Rollback antes da atualização do head: versão anterior, evento e ponteiro permanecem íntegros.
4. Confirmação de commit perdida após commit real: o serviço reporta resultado desconhecido e o replay do mesmo conteúdo retorna `unchanged`, preservando uma única versão/evento/head.
5. Concorrência real: gravações idênticas simultâneas convergem para `created`/`unchanged`; duas revisões divergentes baseadas na mesma versão produzem um vencedor e um conflito, sem revisão duplicada.

O teste principal consultou os índices no MongoDB. Foram encontrados:

| Índice | Chaves | Único |
| --- | --- | --- |
| `one_typed_activity_public_version` | `activity_ref`, `version_id` | Sim |
| `one_typed_activity_private_version` | `activity_ref`, `version_id` | Sim |
| `one_typed_activity_content_revision` | `activity_ref`, `private_content_sha256` | Sim |
| `one_typed_activity_creation_event` | `activity_ref`, `version_id`, `event_type` | Sim |
| `one_typed_activity_current_head` | `activity_ref` | Sim |
| `typed_activity_public_version_history` | `activity_ref`, `created_at` descendente | Não |

Também foi tentada uma duplicação de `activity_ref` no índice único do head e o servidor rejeitou com `DuplicateKeyError`.

## RBAC

O teste criou usuários e papéis temporários diferentes, restritos ao banco exclusivo do caso:

- **Público:** `find` somente em `typed_activity_public_versions`; leitura do conteúdo público permitida; leitura direta de `typed_activity_private_versions` e escrita pública negadas pelo servidor (código 13).
- **Editorial:** `find`, `insert`, `update` e `createIndex` limitados às quatro coleções editoriais do banco de teste. Leitura da coleção privada é necessária ao repositório para validar/reconciliar revisões. A gravação de uma atividade de teste foi autorizada.
- **Interno:** `find` somente nas coleções pública e privada; a leitura de versão privada foi autorizada.

As verificações usaram credenciais próprias para cada papel. A credencial administrativa temporária foi usada apenas para provisionamento e limpeza, não como prova de acesso público. Usuários e papéis foram removidos pelo teardown do teste; o banco de teste foi descartado. Detalhes sem credenciais estão em [MATRIZ_RBAC_MONGODB_14F2.md](MATRIZ_RBAC_MONGODB_14F2.md).

## Regressões e qualidade

- Testes focados sem URI Mongo: `20 passed, 5 skipped`. Os cinco são opt-in e foram executados separadamente contra o replica set descartável.
- Regressões de atividades tipadas, conversor, correção/API de quizzes, adaptador curricular, contratos e pré-requisitos: `262 passed`.
- Ruff: aprovado.
- Ruff format: três arquivos já formatados.
- Mypy focado: sem erros nos três arquivos analisados; em funções de teste sem anotação completa, mypy informa que seus corpos não são verificados por padrão.
- `py_compile`: aprovado.
- `git diff --check`: aprovado; Git emitiu apenas o aviso de conversão LF/CRLF no JSON que já estava modificado antes desta etapa.

Não houve teste ignorado na execução com URI explícita: os cinco testes opt-in passaram. O replica set de um membro confirma transações locais, mas não failover ou comportamento distribuído.

## Limpeza

Após cada execução, foi confirmado que o PID próprio havia terminado e que a porta não estava mais escutando. Foram removidos somente os diretórios temporários exclusivos criados por esta etapa, contendo banco, keyfile, logs, metadados e runner. Ao final não restou processo/porta da execução nem diretório `TrilhaCode14F2_*` temporário. O serviço MongoDB preexistente permaneceu intacto.

## Arquivos desta execução e estado

Alterações relacionadas ao código/testes:

- `backend/curriculum_contract/activity_persistence.py`
- `backend/unit_tests/test_typed_activity_persistence.py`
- `backend/unit_tests/test_typed_activity_persistence_mongodb.py`

Documentação criada:

- `docs/migracao/RELATORIO_ETAPA_14F2.md`
- `docs/migracao/EVIDENCIAS_MONGODB_14F2.md`
- `docs/migracao/MATRIZ_RBAC_MONGODB_14F2.md`

O worktree contém várias alterações preexistentes, mantidas intactas. Nada foi staged ou commitado.
