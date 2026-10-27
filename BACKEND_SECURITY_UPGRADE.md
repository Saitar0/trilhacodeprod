# Atualização de segurança do backend

Data da validação: 16/10/2026. Runtime de validação: Python 3.11.9.

## 1. Matriz de versões

| Pacote | Anterior | Nova | Resultado |
| --- | ---: | ---: | --- |
| FastAPI | 0.110.1 | 0.133.0 | Primeiro release com suporte declarado a Starlette 1.0+. |
| Starlette | 0.37.2 | 1.3.1 | Mínima corrigida indicada na auditoria recebida. |
| Motor | 3.3.1 | 3.7.1 | Mantido; aceita PyMongo >=4.9,<5. |
| PyMongo | 4.6.3 | 4.18.2 | Corrige as quatro ocorrências encontradas na versão anterior. |
| Pydantic | 2.13.5 | 2.13.5 | Mantido; satisfaz FastAPI 0.133.0 (>=2.7.0). |

O FastAPI 0.133.0 declara `starlette>=0.40.0` e `pydantic>=2.7.0`, e as notas do projeto declaram suporte a Starlette 1.0+. Motor 3.7.1 requer PyMongo >=4.9,<5. Todos aceitam Python 3.11. A combinação foi instalada em ambiente virtual isolado e passou pela suíte existente.

Fontes: [notas de versão do FastAPI](https://fastapi.tiangolo.com/release-notes/), [metadados do FastAPI 0.133.0](https://raw.githubusercontent.com/fastapi/fastapi/0.133.0/pyproject.toml), [metadados do Motor 3.7.1](https://pypi.org/project/motor/3.7.1/), [Starlette 1.3.1 no PyPI](https://pypi.org/project/starlette/1.3.1/), [PyMongo 4.18.2 no PyPI](https://pypi.org/project/pymongo/4.18.2/).

## 2. Compatibilidade verificada

- A auditoria isolada das versões anteriores reproduziu 18 ocorrências: 4 para PyMongo e 14 para Starlette. Há IDs repetidos no resultado do `pip-audit` por aliases dos advisories.
- PyMongo 4.18.2 é compatível com Motor 3.7.1 segundo o intervalo declarado pelo Motor. Portanto, a correção destes advisories não exige migrar para PyMongo Async.
- FastAPI 0.110.1 limita Starlette a uma faixa anterior à versão 1.x. FastAPI 0.133.0 declara suporte à família Starlette 1.x. Pydantic não precisou ser atualizado.
- Os manifests de desenvolvimento e produção especificam o mesmo FastAPI, Starlette, Motor, PyMongo e Pydantic. O manifest de desenvolvimento inclui o Sentry já usado pelo de produção.

## 3. Advisories corrigidos e restantes

As 18 ocorrências da combinação anterior correspondiam aos IDs abaixo. A versão final passou no `pip-audit` do ambiente e dos manifests de desenvolvimento e produção, sem advisories conhecidos.

- PyMongo: `PYSEC-2026-4294`, `PYSEC-2026-4295`, `PYSEC-2026-4296`, `PYSEC-2026-4297`.
- Starlette: `PYSEC-2026-161`, `PYSEC-2026-248`, `PYSEC-2026-249`, `PYSEC-2026-1941`, `PYSEC-2026-1943`, `PYSEC-2026-2280`, `PYSEC-2026-2281`.

Durante a auditoria também apareceram dependências não usadas pelo código do Trilha Code:

- `python-jose==3.5.0` (`PYSEC-2026-4298`) e `ecdsa==0.19.2` (`PYSEC-2026-1325`) foram removidos do manifest de desenvolvimento. O código usa PyJWT e não importa esses pacotes; o advisory de ECDSA não tem versão corrigida planejada pelo projeto upstream.
- O wheel privado `litellm==1.80.0`, sem importações no repositório e ausente do manifest de produção, foi removido do manifest de desenvolvimento após o `pip-audit` apontar 32 advisories para essa versão.

Esses pacotes foram removidos por não serem dependências usadas pela aplicação; nenhum advisory foi ignorado ou suprimido.

## 4. Modificações realizadas

- Atualizadas as versões de FastAPI, Starlette, Motor e PyMongo em `backend/requirements.txt` e `backend/requirements.prod.txt`.
- Mantido Pydantic 2.13.5 e alinhados os componentes compartilhados pelos manifests de desenvolvimento e produção.
- Removidos os pacotes sem uso `python-jose`, `ecdsa` e o wheel privado `litellm` do manifest de desenvolvimento.
- Alterados `.dockerignore` e `backend/Dockerfile.prod.dockerignore` para excluir nomes de ambientes como `.venv311`; o build mostrou que o padrão anterior só excluía a pasta chamada exatamente `.venv`.
- Nenhuma rota, código de autenticação, permissão, contrato da API ou código de acesso ao banco foi alterado.
- A suíte foi executada com `MONGO_URL_TEST=mongodb://localhost:27017`. O fixture gerou e removeu seu banco `test_<uuid>`; `test_database` não foi usado.

## 5. Validação

| Verificação | Resultado |
| --- | --- |
| `pip check` no ambiente separado | Aprovado: sem dependências quebradas. |
| `pip-audit` no ambiente instalado | Aprovado: nenhum advisory conhecido. |
| `pip-audit -r requirements.txt --no-deps` | Aprovado: nenhum advisory conhecido. |
| `pip-audit -r requirements.prod.txt --no-deps` | Aprovado: nenhum advisory conhecido. |
| Resolução do manifest completo de desenvolvimento (`pip install --dry-run`) | Aprovada: sem conflito de dependências. |
| `ruff check` | Aprovado. |
| Compilação de arquivos Python | Aprovada: 44 arquivos compilados em memória. |
| Testes backend | Aprovados: 47 passaram; 4 avisos de depreciação de `@app.on_event` já usado pelo servidor. |
| Build de `backend/Dockerfile.prod` | Aprovado em build local; instalação concluída sobre `python:3.11-slim`. Nenhum push ou deploy realizado. |

O ambiente usado para validar foi `backend/security-validation/.venv`; o ambiente previamente aprovado `backend/.venv311` permaneceu intacto.

## 6. Mudanças incompatíveis

Não foi identificada alteração no contrato da API pelos testes. Houve uma mudança de versão major em Starlette e uma atualização de FastAPI necessária para aceitar Starlette 1.x; por isso, a cobertura dos 47 testes é a verificação de compatibilidade disponível. Os testes reportam avisos existentes sobre `@app.on_event`; essa modernização não foi incluída nesta atualização de segurança.

## 7. Riscos e rollback

O principal risco é a mudança de Starlette 0.x para 1.x, além do salto de FastAPI 0.110.1 para 0.133.0. A combinação passou na suíte, no lint, na compilação, no auditor e no build de produção, mas deve ser observada em staging antes de qualquer release.

O rollback de dependências é restaurar nos dois manifests compartilhados as versões registradas na matriz: FastAPI 0.110.1, Starlette 0.37.2, Motor 3.3.1, PyMongo 4.6.3 e Pydantic 2.13.5. O ambiente anterior `backend/.venv311` continua disponível para retomar a validação aprovada. Esse rollback reintroduz os advisories conhecidos de PyMongo e Starlette; deve ser usado apenas como contingência enquanto se corrige a incompatibilidade.

## 8. Recomendação Motor → PyMongo Async

Manter Motor nesta alteração reduz o escopo e é compatível com PyMongo 4.18.2. Contudo, Motor está descontinuado desde 14/05/2026 e recebe apenas correções críticas até 14/05/2027. Recomendo uma migração separada e próxima para PyMongo Async, sem combinar essa mudança com atualizações do FastAPI.

O impacto previsto é concentrado no cliente criado em `backend/core.py`: trocar `AsyncIOMotorClient` por `pymongo.AsyncMongoClient`, rever o fechamento assíncrono do cliente e validar as chamadas de cursor e operações usadas pelos serviços. A documentação do MongoDB alerta que `AsyncMongoClient` deve ficar restrito a um único event loop e lista pequenas diferenças de métodos. A migração deve ter seu próprio conjunto de testes para operações de leitura/escrita, cursores, inicialização e encerramento, seguido da mesma suíte de 47 testes com banco temporário. Nenhuma alteração de dados é necessária.

Fontes: [aviso de descontinuação do Motor](https://github.com/mongodb/motor), [guia oficial de migração para PyMongo Async](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/).
