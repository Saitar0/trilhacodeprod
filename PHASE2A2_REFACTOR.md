# Trilha Code — Fase 2A.2: Refatoração de `routes_content.py`

## 1. Distribuição das responsabilidades antes da refatoração

Registro feito antes de alterar a implementação.

| Área/endpoints | Responsabilidade HTTP que fica na rota | Persistência/regra já delegada |
| --- | --- | --- |
| Trilhas: `GET/POST /api/tracks`, `PUT /api/tracks/reorder`, `GET/PUT/DELETE /api/tracks/{track_id}`, `POST /api/tracks/{track_id}/duplicate`, `POST /api/tracks/{track_id}/publish` | Rotas, schemas, dependências de autenticação/permissão e serialização | `services.tracks` |
| Versões: `GET /api/tracks/{track_id}/versions`, `GET /api/versions/{version_id}` | Rotas, `VersionOut` e `content.read` | **Exceção encontrada:** a rota listava `track_versions` diretamente e a consulta combinava `services.common.get_document` com `integrity.load_snapshot` |
| Árvore da trilha: `GET /api/tracks/{track_id}/tree` | Parâmetros e resposta `TrackTreeOut` | `services.nodes.get_track_tree` |
| Nós: `POST /api/nodes`, `POST /api/nodes/reorder`, `GET /api/nodes/{node_id}`, `PUT/DELETE /api/nodes/{node_id}`, `POST /api/nodes/{node_id}/duplicate` | Rotas, schemas, permissões e serialização | `services.nodes` |
| Blocos: `POST /api/blocks`, `POST /api/blocks/reorder`, `PUT/DELETE /api/blocks/{block_id}` | Rotas, schemas e permissões | `services.blocks` |
| Relações: `POST /api/relations`, `PUT/DELETE /api/relations/{rel_id}` | Rotas, schemas e permissões | `services.relations` |
| Busca: `GET /api/search` | Parâmetros e `SearchResultOut` | `services.search.search_nodes` |
| Histórico: `GET /api/history` | Parâmetros e `HistoryOut` | `services.history.list_history` |
| Estatísticas: `GET /api/admin/stats` | Rota, permissão e `StatsOut` | `services.stats.get_stats` |

Operações de leitura, escrita, agregação e regras de domínio dos demais grupos
já estão em serviços. A rota de versões era a única exceção de acesso direto a
MongoDB; ambas as consultas usam leitura assíncrona. A listagem filtra registros
com `chunks`, omite `snapshot`, ordena por `created_at` decrescente e limita a
500 resultados. A leitura individual carrega o snapshot através da função
existente em `integrity.py`.

As rotas mantêm validação de entrada via Pydantic, dependências
`current_user`/`require(...)`, parâmetros HTTP e montagem/serialização de
respostas. O escopo não altera essas regras nem a lógica de snapshots e
restaurações.

## 2. Resultado da refatoração

As operações de versões foram movidas para `services.versions`:

- `list_track_versions(track_id)` mantém exatamente o filtro por `chunks`, a
  projeção que omite `snapshot`, a ordenação decrescente por `created_at` e o
  limite de 500.
- `get_version(version_id)` busca o documento com `get_document` e usa a mesma
  função `integrity.load_snapshot` que a rota usava. A representação HTTP
  serializada permanece a mesma.

`routes_content.py` continua definindo os mesmos endpoints, schemas,
dependências e respostas. A rota não importa nem acessa `db`, `load_snapshot`
ou `get_document` diretamente. Nenhuma lógica de criação, publicação,
comparação, snapshot ou restauração foi alterada. As permissões
`content.read` permaneceram nas duas rotas de versões.

## 3. Arquivos alterados

Alterados nesta fase:

- `backend/routes_content.py` — encaminha as duas leituras de versão ao serviço.
- `backend/services/versions.py` — recebe as consultas de versões.
- `backend/tests/backend_test.py` — fortalece a regressão HTTP para ordenação,
  omissão de snapshot na listagem e inclusão na consulta individual.
- `backend/ruff.toml` — move `extend-exclude` para o nível raiz do TOML. A
  configuração anterior colocava essa chave dentro de `lint.per-file-ignores`,
  fazendo o Ruff interpretar `.venv` como seletor inválido e impedindo a
  verificação solicitada.
- `PHASE2A2_REFACTOR.md` — este registro.

O checkout já continha outras mudanças locais da Fase 2A.1; elas foram
preservadas e não fazem parte das alterações desta fase.

## 4. Testes e verificações

No Python **3.11** (`backend/.venv311`):

- `ruff check .`: **passou**.
- Compilação de **52 arquivos Python**: **passou**.
- `pytest --noconftest -q tests/test_core_modules.py`: **5 passaram**. Essa
  execução cobre testes que não precisam de MongoDB.
- A suíte completa coletou **52 testes**, mas não pôde ser concluída. A tentativa
  com `MONGO_URL_TEST=mongodb://127.0.0.1:27017` ficou aguardando a conexão e foi
  interrompida: não há daemon Docker acessível, `mongod` instalado nem MongoDB
  escutando na porta local. O teste de integração que foi reforçado ainda
  precisa rodar com MongoDB descartável.
- `git diff --check`: **passou**.

Para concluir a verificação integrada no PowerShell, a partir da raiz:

```powershell
Set-Location .\backend
$mongoContainer = 'trilhacode-phase2a2-mongo'
docker run --rm -d --name $mongoContainer -p 27019:27017 mongo:7
try {
    $env:MONGO_URL_TEST = 'mongodb://127.0.0.1:27019'
    .\.venv311\Scripts\python.exe -m ruff check .
    .\.venv311\Scripts\python.exe -c "from pathlib import Path; import py_compile; files=[p for p in Path('.').rglob('*.py') if not any(part in {'.venv','.venv311','.pytest_cache','.ruff_cache','__pycache__'} for part in p.parts)]; [py_compile.compile(str(p), doraise=True) for p in files]; print(f'Compiled {len(files)} Python files')"
    .\.venv311\Scripts\python.exe -m pytest -q
} finally {
    docker stop $mongoContainer | Out-Null
    Remove-Item Env:MONGO_URL_TEST -ErrorAction SilentlyContinue
}
```

O container usa uma porta separada e não monta `mongo-data`. A fixture cria um
banco aleatório com prefixo `test_` e remove apenas esse banco.

## 5. Riscos e possíveis regressões

O risco de regressão se concentra em manter as convenções da consulta de versões
(filtro, projeção, ordenação e limite) e o carregamento de snapshots
comprimidos. Esses detalhes foram preservados literalmente na movimentação; a
verificação de integração completa ainda está pendente por falta do MongoDB
descartável no ambiente atual. Não foram alteradas autorizações, formatos de
coleção, snapshots ou restaurações.

## 6. Pendências para a Fase 2A.3

Executar a suíte completa com o container Mongo descartável acima e registrar o
resultado final. Como próxima análise arquitetural, mapear acessos diretos ao
MongoDB nas demais rotas (`routes_import.py`, `routes_progress.py`,
`routes_submissions.py`, `routes_taxonomy.py` e `routes_versions.py`) e priorizar
os que ainda não estejam delegados, sem ampliar o escopo de snapshots e
restaurações sem solicitação específica.
