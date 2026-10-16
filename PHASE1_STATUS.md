# Auditoria final — Fase 1 de qualidade

Data da auditoria: 16/10/2026

Escopo: inspeção do workflow local, manifests e configuração; execução das verificações disponíveis. Esta auditoria não alterou código/configuração. O único arquivo criado para esta solicitação é este relatório.

## Resumo

| Área | Estado | Evidência |
|---|---|---|
| Testes do backend | Concluído localmente | `python -m pytest -q --tb=short` em `backend/`: **47 passaram**, 4 avisos. |
| TypeScript strict | Concluído localmente | `frontend/tsconfig.json` define `strict: true`; `npm run typecheck` passou sem erros. |
| ESLint frontend | Concluído localmente; ausente do CI | `npm run lint` passou. O workflow não executa esse script. |
| Build frontend | Concluído localmente; presente indiretamente no CI | `npm run build` passou; `frontend/Dockerfile.prod` chama o mesmo script. Vite avisou que o bundle JS principal excede 500 kB. |
| Ruff | Pendente | Sem `pyproject.toml`, `ruff.toml` ou `.ruff.toml`; Ruff não está nos requirements e não está instalado (`python -m ruff --version`: módulo ausente). |
| Auditorias de dependências | Bloqueadas/incompletas | `pip-audit` não está instalado nem no CI. `npm audit` falhou por DNS para `registry.npmjs.org`, portanto não há resultado de vulnerabilidades. |

## CI do GitHub Actions

Existe `.github/workflows/ci-deploy.yml`, acionado em push e pull request para `main` e `staging`.

- **Backend:** job inicia MongoDB 7, instala `backend/requirements.txt` e executa `python -m pytest` (`.github/workflows/ci-deploy.yml`, seção `backend`).
- **TypeScript e build:** o job `frontend` constrói a imagem de produção. `frontend/Dockerfile.prod` executa `npm ci` e `npm run build`; o script build é `tsc --noEmit && vite build`. Assim, typecheck e build entram no CI por esse Docker build.
- **Lint:** `npm run lint` existe em `frontend/package.json`, mas não é chamado no workflow. O CI não verifica ESLint.
- **Frontend tests:** `npm test` existe, mas também não é chamado pelo workflow.
- **Backend lint/Ruff:** nenhum passo de lint backend está configurado.
- A inspeção foi do arquivo versionado localmente; não consultei o estado de uma execução remota do GitHub Actions.

## Ruff e tipagem

- Não há configuração de Ruff no repositório. A pasta `.ruff_cache` existente é apenas cache e não demonstra configuração ou execução funcional.
- `ruff` não aparece em `backend/requirements.txt` nem em `backend/requirements.prod.txt`; não há executável em `backend/.venv/Scripts/ruff.exe` e `python -m ruff --version` retorna que o módulo não está instalado.
- `frontend/tsconfig.json` contém `"strict": true`. `npm run typecheck` terminou com código zero e sem diagnósticos.
- `npm run lint` terminou com código zero e sem diagnósticos.

## Requirements, dependências e lockfiles

- `backend/requirements.prod.txt` é a lista pequena de runtime para a imagem de produção. `backend/requirements.txt` é muito maior e mistura dependências de execução, testes e ferramentas de desenvolvimento. Não existe `requirements-dev.txt` nem `requirements.txt` na raiz.
- `backend/requirements.txt` inclui ferramentas como Flake8, Black, isort e mypy, mas o workflow não executa essas ferramentas. Ruff não está declarado.
- Uma leitura estática dos imports do backend não encontrou uso direto aparente de vários pacotes do requirements amplo, incluindo `aiohttp`, `numpy`, `pandas`, `google-genai`, `google-generativeai`, `huggingface-hub`, `openai`, `litellm` e `stripe`. Isso é uma lista de candidatos à remoção, não prova de que sejam inúteis: dependências opcionais, scripts e imports dinâmicos exigem confirmação pelos responsáveis antes de removê-las.
- O frontend contém `frontend/package-lock.json` (usado por `npm ci`) e `frontend/yarn.lock` (não usado pelos comandos/CI atuais). Há ainda um `yarn.lock` na raiz, de apenas 86 bytes, sem `package.json` correspondente. Há lockfiles redundantes; o lockfile canônico demonstrado pelo build é `frontend/package-lock.json`.
- Não há lockfile Python dedicado; `requirements.txt` e `requirements.prod.txt` pinam versões, com exceção das faixas de `pydantic-settings` e `sentry-sdk`.

## Segurança de dependências e conectividade

- Não encontrei `pip-audit` ou `npm audit` em `.github/workflows/ci-deploy.yml` ou scripts de CI. `pip-audit` também não está instalado localmente.
- Executei `npm audit --json` em `frontend/`; a consulta falhou com `ENOTFOUND registry.npmjs.org`. Não foi possível obter dados de advisories, então o estado de vulnerabilidades npm permanece **não verificado**, e não deve ser interpretado como “sem vulnerabilidades”.
- Sem `pip-audit` instalado e sem verificação de advisories na pipeline, as dependências Python também não têm auditoria de vulnerabilidades comprovada.
- Não imprimi nem incluí valores de arquivos de ambiente ou credenciais neste relatório.

## Validações executadas

| Comando | Resultado |
|---|---|
| `python -m pytest -q --tb=short` (diretório `backend/`) | **47 passed**, 4 warnings, em 14,06 s. Avisos remanescentes são deprecation warnings do uso de `FastAPI.on_event`. |
| `npm run typecheck` (diretório `frontend/`) | Passou, sem erros. |
| `npm run lint` (diretório `frontend/`) | Passou, sem erros. |
| `npm run build` (diretório `frontend/`) | Passou; Vite transformou 2.422 módulos. Aviso informativo: bundle JS principal de aproximadamente 1,64 MB antes de gzip, acima do limite padrão de 500 kB. |
| `npm audit --json` (diretório `frontend/`) | Bloqueado por DNS (`ENOTFOUND registry.npmjs.org`); nenhum relatório de vulnerabilidade foi produzido. |
| `python -m ruff --version` | Ruff ausente; a verificação Ruff não pôde ser executada. |
| `python -m pip_audit --version` | pip-audit ausente; a verificação Python não pôde ser executada. |
| `git diff --check` nos arquivos dos testes backend | Sem erros de whitespace. |

Os testes usam `test_<uuid>` descartável. Após a execução, consultei `list_database_names`: nenhum banco UUID da suíte ficou para trás. O banco preexistente `test_database` permaneceu intocado; não executei operações nele nem em outros bancos existentes.

## Itens da Fase 1

### Concluídos

- Testes backend executam localmente com MongoDB e passaram (47/47).
- TypeScript strict está habilitado e o typecheck passou.
- ESLint frontend e build de produção passaram localmente.
- CI configura serviço MongoDB e executa os testes backend; o build do Docker frontend também executa o typecheck e o build Vite.
- Testes confirmados sem alterações em bancos preexistentes; o banco UUID foi removido no teardown.

### Pendentes

- Adicionar lint explícito ao workflow e decidir se os testes frontend também devem fazer parte do CI.
- Configurar Ruff, incluir a dependência e definir os diretórios/regras que ele deve validar; depois fazê-lo passar no CI.
- Separar dependências de desenvolvimento/teste de `requirements.txt` e avaliar os candidatos sem uso aparente antes de removê-los.
- Remover lockfiles Yarn redundantes ou declarar oficialmente qual gerenciador é suportado; manter o lockfile coerente com o CI.
- Adicionar auditoria de dependências à pipeline (por exemplo, `pip-audit` e `npm audit`) e definir como tratar advisories.
- Avaliar divisão do bundle principal Vite para reduzir o aviso de chunk grande.

### Bloqueados nesta auditoria

- Resultado de `npm audit`: bloqueado pela resolução DNS para o registry npm.
- Resultado de `pip-audit`: ferramenta ausente; não houve consulta ao banco de advisories.
- Execução remota do GitHub Actions: não verificada; a auditoria avaliou somente a configuração local do workflow.
