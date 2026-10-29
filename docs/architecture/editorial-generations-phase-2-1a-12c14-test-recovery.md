# Fase 2.1A.12C.14 — Recuperação do ambiente e testes

## Recuperação de `pydantic_settings`

C13 registrou bloqueio de coleta de `backend/unit_tests/test_snapshot_safety.py` porque o venv herdado não tinha `pydantic_settings`. No checkout C14, `backend/requirements.txt` declara `pydantic-settings>=2.7,<3`; `backend/requirements.prod.txt` também declara o intervalo. A dependência não estava ausente do manifesto: o ambiente de teste anterior estava incompleto.

Foi criado um venv novo e exclusivo em `C:\Users\Joao\.codex\tmp\trilhacode-12c14-venv`, sem modificar Python global ou o ambiente da C7/C12. Python 3.11 foi usado. Dependências vieram do índice público PyPI e dos manifests versionados do projeto; nenhuma fonte privada, secret ou arquivo `.env` foi usada. Versões instaladas: `pydantic-settings 2.16.2`, `pydantic 2.13.5`, `pymongo 4.18.2`, `fastapi 0.141.1`, `pytest 9.1.1`, `ruff 0.17.3`, `mypy 2.4.0`. O intervalo de `pydantic-settings` é aberto dentro de `<3`; o venv não foi criado como lockfile/hash reprodutível. O venv C14 permanece no diretório temporário exclusivo, fora do repositório e sem alterar outros ambientes.

## Suíte de snapshots

Comando executado do diretório `backend`:

```powershell
& 'C:\Users\Joao\.codex\tmp\trilhacode-12c14-venv\Scripts\python.exe' -m pytest unit_tests/test_snapshot_safety.py -q
```

Resultado: **6 passed**, sem skips/erros de coleta. Os testes cobrem snapshot vazio completo, coleção ausente, contagem inconsistente, documento de outra trilha, prefixo contíguo conhecido do ledger de migrações e captura acima dos limites antigos de tamanho. Os casos monkeypatcham collections e funções de banco; não validam storage persistente.

**Limite da cobertura:** a suíte não demonstra snapshot da mesma revisão de origem, concorrência snapshot-versus-write, atomicidade com publicação, swap de head, readers pinados, restauração sob falha, failover, retenção de progress/attempts, ou topologia implantada. Não declarar “segurança de snapshots” globalmente validada pelo fato de 6 testes passarem.

## Regressões offline executadas

Comando combinado (também do diretório `backend`):

```powershell
& 'C:\Users\Joao\.codex\tmp\trilhacode-12c14-venv\Scripts\python.exe' -m pytest unit_tests/test_snapshot_safety.py unit_tests/test_editorial_revision_protocol.py unit_tests/test_editorial_observability.py unit_tests/test_editorial_iam_authority.py unit_tests/test_editorial_generations_poc.py unit_tests/test_experimental_editorial_api_contract.py unit_tests/test_experimental_editorial_privacy_policy.py unit_tests/test_immutable_publications.py unit_tests/test_mongodb_editorial_revision_adapter.py unit_tests/test_editorial_readiness_contract.py integration_tests/test_editorial_writer_inventory.py integration_tests/test_editorial_grant_governance.py integration_tests/test_editorial_observability_harness.py -q
```

Resultado combinado incluindo o novo contrato de prontidão e harness C6: **183 passed, 38 subtests passed**, sem falhas, skips ou deselections. O conjunto selecionado inclui C1 protocolo/PoC, C2 adaptador offline, C5 observabilidade, C6 harness, C8 contrato de revisão, C10 contrato API e C11/C12/C13 IAM/governança/inventário; inclui testes unitários de publicações imutáveis, snapshot e o contrato JSON C14.

O teste de snapshot também foi executado separadamente: **6 passed**. O novo `unit_tests/test_editorial_readiness_contract.py` passou com **5 testes** (incluído no total combinado). Não rodamos suites persistentes C3 e C7–C12, nem a compatibilidade persistente C9; não criamos Mongo/Docker. Os testes completos de serviços legados localizados pelo inventário C13 também não foram reexecutados. A suíte completa `backend/unit_tests` não foi executada; esta foi uma seleção de regressões editoriais e de segurança definida acima.

| Fase | Resultado na C14 |
|---|---|
| C13 | Testes offline de inventário e governança executados e aprovados (incluídos no total). |
| C12 | Testes unitários IAM/autorização aprovados; corrida persistente C12 não executada. |
| C11 | Testes unitários de autorização, privacidade e replay aprovados; persistência C11 não executada. |
| C10 | Contrato API unitário aprovado; AsyncMongoClient persistente não executado. |
| C9 | Compatibilidade do writer depende de Mongo descartável; não executada nesta consolidação. |
| C8 | Protocolo/revisão unitária aprovada; commit persistente não executado. |
| C7 | Regressão persistente de update/audit não reexecutada. |
| C6 | Harness do writer real com dependências sintéticas executado e aprovado offline. |
| C5 | Testes unitários de observabilidade aprovados. |
| C3 | Validação persistente Mongo não reexecutada. |
| C2 | Teste offline do adaptador aprovado; validação persistente Mongo não reexecutada. |
| C1 | Protocolo em memória e PoC offline aprovados. |

Esta seleção não equivale à suíte completa do backend nem a uma nova validação persistente das fases anteriores.

## Ambiente e segurança

`test_snapshot_safety.py` importa módulos que constroem dependências de aplicação em import; seus casos substituem as coleções chamadas com doubles e não executam rota, migração, writer ou query. No ambiente C14 não havia `.env` no root ou em `backend`; não havia variável de ambiente `MONGO*`, `PYTHON*` ou `PIP*` disponibilizada na inspeção, além das variáveis internas do app. Nenhum MongoDB, Docker, rede operacional ou serviço externo foi iniciado/consultado pelo teste.

Dependências instaladas são isoladas no venv C14 e fora do repositório. A evidência não comprova configuração/runtime de implantação. Não remover ambiente de outras fases.
