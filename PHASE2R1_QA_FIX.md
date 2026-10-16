# Trilha Code — Fase 2R.1: correção do bloqueio de QA

**Data:** 16/10/2026  
**Estado do checkout:** alterações locais pré-existentes preservadas; sem push, deploy, migração ou acesso a banco existente.

## 1. Causa raiz

`backend/indexes.py` foi alterado localmente para declarar os índices em `INDEXES` e implementar o preflight somente leitura por `preflight_indexes()`. A verificação de chaves duplicadas passou a ser feita por `_duplicates(collection, fields, partial_filter)`, que retorna amostras para compor os achados do preflight.

O arquivo local não rastreado `backend/tests/test_integrity_concurrency.py` ainda importava `_assert_unique_values`, uma função privada de uma interface anterior. O histórico Git não contém esse arquivo de teste; portanto, o import incompatível pertence ao conjunto de mudanças locais, e não a uma regressão entre dois arquivos rastreados no commit atual.

## 2. Diferença entre implementação e teste

- `_assert_unique_values` não existe na implementação atual e não é a interface usada por `preflight-indexes`.
- `_duplicates` recebe os campos como tupla e um filtro parcial opcional; devolve valores agrupados, contagem e um ID de amostra. `preflight_indexes()` apresenta os resultados como achados `DUPLICATAS`.
- `backend/manage.py` imprime os achados e encerra com erro se o preflight encontrar `CONFLITO` ou `DUPLICATAS`. `ensure-indexes` é um comando separado que chama `create_index` sequencialmente.

## 3. Arquivos modificados

- `backend/tests/test_integrity_concurrency.py`: removido o import do helper inexistente e substituído o teste antigo por uma verificação do contrato público de `preflight_indexes()`.
- `PHASE2R1_QA_FIX.md`: este relatório.

Não alterei `backend/indexes.py`, as definições de índices, dados, regras de negócio ou outros testes.

## 4. Correção e verificações de regressão

O teste atualizado usa um banco simulado somente de leitura. Ele valida que o preflight:

- apresenta duplicatas legadas com a amostra de ID;
- agrega todas as entradas de `INDEXES` que declaram chaves únicas;
- preserva os pipelines com `$group`, `$match` de contagem e limite de 20 resultados;
- aplica `partialFilterExpression` a `reviews` (`status: pending`) e `restore_jobs` (`status: running`);
- não tenta criar índices nem escrever dados (o objeto simulado não oferece operações de escrita);
- confirma que `manage.run("preflight-indexes")` encerra com erro ao receber achados de duplicatas.

A revisão do código confirmou que o preflight diferencia `AUSENTE` de `CONFLITO` e não faz operações de escrita. Também confirmou que `collection.aggregate(pipeline)` é aguardado antes de consumir o cursor com `to_list(20)`, compatível com PyMongo Async. O teste de integração `test_pymongo_async.py` já exercita esse padrão com o driver; ele não pôde ser executado nesta sessão por falta de MongoDB acessível.

`ensure-indexes` mantém a criação idempotente por `create_index` e não remove índices. A sequência operacional documentada exige executar o preflight antes do comando de escrita. Se alguém executar `ensure-indexes` sem esse gate e houver duplicatas, o próprio MongoDB rejeita a criação do índice único; como a rotina cria os índices em sequência, índices anteriores podem já ter sido criados. A separação entre os comandos e esse limite não foram alterados nesta correção.

## 5. Validações executadas

| Etapa | Resultado |
|---|---|
| `ruff check .` no backend | **Aprovado** — `All checks passed!` |
| Compilação Python | **Aprovada** — 57 fontes Python do backend compilados em memória, excluindo ambientes virtuais e caches locais |
| `pytest --collect-only -q` | **Aprovado** — 63 testes coletados, igual ao total anterior documentado |
| Testes específicos de integridade/preflight | **Bloqueados por infraestrutura** — tentativa de execução aguardou conexão MongoDB; o daemon Docker negou acesso e `localhost:27017` está fechado |
| Suíte completa em MongoDB 7 descartável | **Não executada** — Docker não está acessível neste agente; nenhum banco preexistente foi consultado |

Nenhum teste foi removido, desabilitado ou reduzido para obter a coleta. A substituição preserva o teste no mesmo lugar, mantém a asserção de bloqueio por duplicatas via comando público e cobre os pipelines dos índices únicos, incluindo os parciais.

## 6. Riscos restantes

- Os testes de integração, concorrência, criação idempotente e compatibilidade real com MongoDB 7 ainda precisam ser executados quando o daemon estiver acessível.
- O preflight é somente leitura e não reserva o estado do banco. Escritas concorrentes entre preflight e criação podem introduzir duplicatas; mantenha congeladas as escritas relevantes durante esse intervalo, conforme `DEPLOY.md`.
- `ensure-indexes` não chama o preflight internamente. Execute o gate operacional documentado antes dele; uma falha durante a criação sequencial pode deixar índices anteriores já criados.

## 7. Comandos PowerShell para validação externa

Em uma janela PowerShell com Docker Desktop acessível, inicie um MongoDB 7 descartável, sem volume persistente:

```powershell
docker run --rm --name trilhacode-qa-mongo-7 -p 27018:27017 mongo:7
```

Em outra janela PowerShell, execute a suíte específica e depois a completa. A fixture cria um banco `test_<uuid>` por execução e o remove ao terminar:

```powershell
Set-Location 'C:\Users\Joao\Documents\CURSO\trilhacodeprod\backend'
$env:MONGO_URL_TEST = 'mongodb://127.0.0.1:27018/?serverSelectionTimeoutMS=5000'
try {
    .\.venv311\Scripts\python.exe -m pytest -q tests/test_integrity_concurrency.py tests/test_pymongo_async.py
    if ($LASTEXITCODE -ne 0) { throw 'Testes específicos falharam.' }
    .\.venv311\Scripts\python.exe -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Suíte completa falhou.' }
} finally {
    Remove-Item Env:MONGO_URL_TEST -ErrorAction SilentlyContinue
}
```

Interrompa o primeiro comando com `Ctrl+C` ao terminar; `--rm` remove o container descartável.

# Trilha Code — Fase 2R.2: correção do mock do preflight

**Data:** 16/10/2026  
**Estado do checkout:** somente o mock do teste e este registro foram alterados; sem push, deploy, migração ou acesso a bancos preexistentes.

## Causa raiz confirmada

`preflight_indexes()` consome dois cursores com limites distintos: `_duplicates()` chama `aggregate(...).to_list(20)`, enquanto a inspeção dos índices chama `list_indexes().to_list(1000)`. O teste usava uma classe `Cursor` compartilhada cuja `to_list()` exigia sempre `20`; por isso, a chamada válida de `list_indexes()` falhava com `AssertionError: assert 1000 == 20`. A implementação de `backend/indexes.py` está correta e não foi alterada.

## Correção

Em `backend/tests/test_integrity_concurrency.py`, o mock agora tem `AggregationCursor`, que mantém a assertion de limite `20`, e `IndexCursor`, que valida separadamente o limite `1000`. As verificações existentes de duplicatas e ID de amostra, pipelines e limites, filtros parciais de `reviews` e `restore_jobs`, e rejeição do comando público `preflight-indexes` foram mantidas.

## Validações

| Verificação | Resultado |
|---|---|
| `ruff check .` | **Aprovado** |
| Compilação das fontes Python do backend | **Aprovada** — 57 fontes compiladas |
| `pytest --collect-only -q` | **Aprovado** — 63 testes coletados |
| Teste específico via pytest | **Não concluído** — a fixture autouse prepara um banco MongoDB descartável; o Docker daemon negou acesso e a execução sem Mongo não progrediu. A tentativa foi interrompida, sem usar banco preexistente. |
| Suíte completa contra MongoDB 7 descartável | **Não executada** — Docker Engine indisponível nesta sessão. |

## Execução PowerShell quando Docker estiver acessível

Em uma janela PowerShell, inicie MongoDB 7 sem volume persistente:

```powershell
docker run --rm --name trilhacode-qa-mongo-7 -p 27018:27017 mongo:7
```

Em outra janela, rode primeiro o teste afetado e depois a suíte completa. O `conftest.py` usa um nome `test_<uuid>` e remove esse banco ao terminar:

```powershell
Set-Location 'C:\Users\Joao\Documents\CURSO\trilhacodeprod\backend'
$env:MONGO_URL_TEST = 'mongodb://127.0.0.1:27018/?serverSelectionTimeoutMS=5000'
try {
    .\.venv311\Scripts\python.exe -m pytest -q tests/test_integrity_concurrency.py::test_unique_index_preflight_reports_duplicates_and_respects_partial_indexes
    if ($LASTEXITCODE -ne 0) { throw 'Teste de preflight falhou.' }
    .\.venv311\Scripts\python.exe -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Suíte completa falhou.' }
} finally {
    Remove-Item Env:MONGO_URL_TEST -ErrorAction SilentlyContinue
}
```

Interrompa o container com `Ctrl+C` ao terminar; `--rm` remove o container descartável.
