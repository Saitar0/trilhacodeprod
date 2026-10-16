# Fase 2C — Migração para PyMongo Async

## 1. Auditoria da API Motor existente

O cliente era criado como singleton em `backend/database.py` com `AsyncIOMotorClient(settings.mongo_url, tz_aware=True)`. `db` era selecionado uma vez a partir de `settings.db_name` e compartilhado pelo backend e pela fachada `backend/core.py`.

Foram localizados os seguintes usos:

- CRUD assíncrono em routers, serviços, migrations, seed e scripts de manutenção. Operações de rede já são aguardadas com `await`.
- Cursores de `find()` e `aggregate()` consumidos por `to_list(n)` ou `async for`, com paginação por `sort`, `skip` e `limit`.
- `ReturnDocument` e erros importados de `pymongo`, já compatíveis com o novo driver.
- Fechamento síncrono `client.close()` no lifespan do FastAPI, CLI de gerenciamento e fixture de testes.
- Fixture de integração com um `event_loop` de sessão usado pelos clientes e pelas operações de banco. O cleanup do banco continua síncrono e usa um `MongoClient` separado depois do fechamento assíncrono.

A busca também cobriu `backend/database.py`, `server.py`, `core.py`, serviços, migrations, `seed.py`, testes e scripts. Não foram encontrados usos de `io_loop`, `AsyncCursor.each()`, `to_list(0)`, `MotorGridOut`, `stream_to_handler()`, change streams, sessões ou transações Motor-específicas.

## 2. Alterações realizadas

- Substituído `AsyncIOMotorClient` por `pymongo.AsyncMongoClient`, mantendo URL, `tz_aware=True`, seleção do banco e singleton compartilhado.
- O lifespan do FastAPI, o CLI e o teardown da fixture agora aguardam `client.close()`.
- Removido Motor dos manifests de desenvolvimento e produção. O pin de PyMongo 4.18.2 já existente foi mantido e passa a fornecer a API assíncrona nativa.
- Mantida `core.py` como fachada, exportando as mesmas referências compartilhadas `client` e `db`.
- Nenhuma rota, schema, regra de negócio, índice ou migração de dados foi alterada.

## 3. Arquivos modificados nesta fase

- `backend/database.py`
- `backend/server.py`
- `backend/manage.py`
- `backend/requirements.txt`
- `backend/requirements.prod.txt`
- `backend/tests/conftest.py`
- `backend/tests/test_integrity_concurrency.py`
- `backend/tests/test_pymongo_async.py` (novo)
- `PHASE2C_PYMONGO_ASYNC.md` (este relatório)

O workspace já continha alterações de fases anteriores; elas foram preservadas e não fazem parte desta lista.

## 4. Compatibilidade e diferenças

A documentação oficial descreve a migração em geral como uma troca de `AsyncIOMotorClient` por `AsyncMongoClient`, com alterações nos métodos listados abaixo: [guia oficial Motor → PyMongo Async](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/).

- `AsyncMongoClient` não aceita `io_loop` e não pode ser compartilhado entre event loops ou threads. Nenhum parâmetro `io_loop` existia. A aplicação utiliza um cliente por processo e o fixture existente mantém um loop de sessão para as operações assíncronas.
- `close()` é assíncrono no cliente novo; os três pontos de encerramento foram adaptados para `await`.
- `find()` e `aggregate()` retornam cursores sem `await`, e o consumo segue assíncrono por `to_list()`/`async for`, como já ocorria.
- A documentação assinala que `to_list(0)` não é válido no PyMongo Async; a auditoria não encontrou tal chamada.
- ObjectId, `ReturnDocument`, `DuplicateKeyError`, CRUD, projeções, pipelines e operações de índice continuam usando as APIs PyMongo.

## 5. Testes adicionados

`backend/tests/test_pymongo_async.py` cobre:

- tipo do cliente nativo e compartilhamento das referências da fachada `core`;
- CRUD assíncrono, `to_list`, iteração `async for`, ordenação e agregação;
- preservação de `ObjectId` na escrita e leitura;
- uso das operações dentro do event loop de sessão da suíte.

O teste existente de lifespan foi adaptado para validar fechamento assíncrono. As operações de banco desse novo teste exigem uma instância MongoDB 7 disponível.

## 6. Resultado das verificações

Executado com Python 3.11.9 e PyMongo 4.18.2:

- Ruff: aprovado (`All checks passed`).
- Compilação: 57 arquivos Python compilados sem erro.
- `pip check`: aprovado (`No broken requirements found`).
- Verificação local sem banco: tipo do cliente e referências compartilhadas entre `core`, `database` e `db` aprovados.
- `pip-audit -r backend/requirements.txt`: aprovado, nenhum advisory conhecido nas versões resolvidas do manifest.
- `pip-audit --local`: reportou 57 ocorrências em cinco pacotes já instalados no ambiente virtual (ecdsa, litellm, python-jose, setuptools e Starlette). O ambiente instalado diverge dos manifests do backend; esses pacotes não foram alterados nesta fase.
- Coleta da suíte: 63 testes encontrados (61 anteriores mais os testes novos). A execução integral foi tentada, mas não completou: não há MongoDB acessível em `localhost:27017` e o Docker Desktop não aceitou conexão ao daemon, inclusive na tentativa com acesso elevado. Assim, a suíte de integração e os casos CRUD/cursores/agregação não podem ser declarados aprovados nesta sessão.
- O ambiente virtual continha PyMongo 4.6.3 apesar do pin 4.18.2 nos manifests. O pin foi instalado no `.venv311` local para validar a presença de `AsyncMongoClient`; nenhum manifest precisou de atualização de versão.

## 7. Riscos de regressão

- O risco principal é o cliente ser acessado a partir de mais de um event loop. A arquitetura atual e os fixtures apontam para um loop por processo/sessão, mas a validação de integração precisa ser repetida com MongoDB disponível.
- Diferenças futuras de cursor ou desempenho podem aparecer sob carga; a migração mantém a semântica das chamadas observadas, mas não inclui benchmark.
- A instalação do ambiente local estava desatualizada e contaminou a auditoria de dependências instaladas; CI deve criar o ambiente a partir dos manifests fixados.

## 8. Estratégia de rollback

Reverter apenas as alterações desta fase nos arquivos listados na seção 3: restaurar `motor==3.7.1`, recolocar `AsyncIOMotorClient`, e restaurar o fechamento síncrono nos pontos de lifecycle. A fachada e os dados do MongoDB não exigem alteração. Não foi realizada migração ou escrita de dados como parte desta alteração. O rollback reintroduz a dependência Motor, que está descontinuada segundo o guia oficial.

## 9. Pendências futuras

- Reexecutar os 63 testes em Python 3.11 contra MongoDB 7 descartável.
- Confirmar a imagem/CI de produção a partir de um ambiente limpo com `requirements.prod.txt`.
- Avaliar os advisories do ambiente local (`pip-audit --local`) na fase apropriada, alinhando o ambiente à matriz oficial antes de modificar dependências não relacionadas.
- Medir desempenho do driver em carga representativa, caso latência/throughput seja critério de aceite.
