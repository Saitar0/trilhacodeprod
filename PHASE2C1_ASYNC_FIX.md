# Fase 2C.1 — Correções de compatibilidade PyMongo Async

## Alterações

- `_assert_unique_values()` mantém a mesma pipeline (`$group`, `$match`, `$limit: 20`), agora aguarda `collection.aggregate(pipeline)` e então aguarda `cursor.to_list(20)`. Limite, exemplos de duplicatas e mensagem de erro foram preservados.
- Corrigidas as outras seis chamadas de agregação em serviços para aguardar `aggregate()` antes do consumo: `learning.py`, `services/nodes.py`, `services/progress.py`, `services/stats.py`, `services/submissions.py` e `services/tracks.py`.
- O teste de integração do driver agora também aguarda a criação do cursor de agregação antes de chamar `to_list()`.
- O mock do teste de preflight de índices passou a implementar `aggregate()` como coroutine e verifica a pipeline integral e o limite de 20 itens. O teste continua cobrindo a interrupção da criação do índice diante de duplicatas e os detalhes da mensagem.

## Auditoria das APIs assíncronas

- Todas as oito ocorrências de `aggregate()` em código e testes foram verificadas. Agora aguardam o método antes de consumir o cursor. A documentação do driver mostra esse padrão para agregação assíncrona: [Aggregation — PyMongo Driver](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/aggregation/).
- `find()` retorna cursor sem `await`; o consumo por `to_list()` e `async for` já estava assíncrono.
- Não foram encontrados `.each()`, `to_list(0)`, `io_loop`, GridFS ou `stream_to_handler()`.
- Operações de escrita/leitura de resultado (`find_one`, CRUD, índices, `count_documents`, `find_one_and_update`) continuam aguardadas. O singleton `AsyncMongoClient` e os fechamentos assíncronos foram preservados.
- Não foram alterados rotas, schemas, regras de negócio, índices, dados ou permissões.

## Arquivos alterados

- `backend/indexes.py`
- `backend/learning.py`
- `backend/services/nodes.py`
- `backend/services/progress.py`
- `backend/services/stats.py`
- `backend/services/submissions.py`
- `backend/services/tracks.py`
- `backend/tests/test_integrity_concurrency.py`
- `backend/tests/test_pymongo_async.py`
- `PHASE2C1_ASYNC_FIX.md`

## Validações executadas

Ambiente: Python 3.11.9, PyMongo 4.18.2.

- `ruff check .`: aprovado.
- Compilação sintática dos 57 arquivos Python do backend (excluindo ambientes virtuais e caches): aprovada.
- `python -m pip check`: aprovado, sem dependências quebradas.
- `python -m pytest --collect-only -q`: 63 testes coletados.
- A suíte não foi executada contra banco. O Docker daemon recusou conexão (`permission denied`); por segurança, nenhum teste foi direcionado a `localhost:27017`, que poderia apontar para uma instância preexistente.
- Uma tentativa isolada de executar o teste de regressão com `--noconftest` não terminou em 30 segundos neste ambiente Windows; foi interrompida sem resultado de assertions. A regressão permanece coberta pela suíte normal, que deve ser executada com o fixture de loop e MongoDB 7 descartável.

## Pendente: execução com MongoDB 7 descartável

Quando o Docker Desktop estiver acessível, execute no PowerShell a partir da raiz do repositório. O container não monta volumes e usa a porta 27018 para não tocar em uma instância MongoDB preexistente na porta padrão.

```powershell
docker run --detach --rm --name trilha-code-mongo7-phase2c1 `
  -p 127.0.0.1:27018:27017 mongo:7

$mongoReady = $false
for ($i = 0; $i -lt 30 -and -not $mongoReady; $i++) {
  docker exec trilha-code-mongo7-phase2c1 `
    mongosh --quiet --eval "db.adminCommand({ ping: 1 })" *> $null
  $mongoReady = $LASTEXITCODE -eq 0
  if (-not $mongoReady) { Start-Sleep -Seconds 1 }
}
if (-not $mongoReady) { docker stop trilha-code-mongo7-phase2c1; throw "MongoDB 7 não ficou pronto" }

$env:MONGO_URL_TEST = "mongodb://127.0.0.1:27018"
Push-Location .\backend
.\.venv311\Scripts\python.exe -m pytest
Pop-Location

docker stop trilha-code-mongo7-phase2c1
Remove-Item Env:MONGO_URL_TEST
```

O resultado da suíte de integração permanece pendente até essa execução. Não foi acessado nem alterado banco de dados nesta etapa.
