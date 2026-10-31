# Beta 6.1 — regressões e qualidade

## Executados nesta fase

| Verificação | Resultado |
|---|---:|
| Gate offline Beta 6.1 + políticas Beta 5/Beta 6 | 61 passed |
| Contratos de segurança Beta 6 + gate + políticas de banco | 68 passed |
| HTTP integrado `test_beta6_learning_journey.py` | 1 passed em MongoDB descartável |
| Browser Playwright Chromium | 1 passed contra API, frontend e MongoDB descartável |
| Frontend Vitest | 9 arquivos, 29 passed |
| TypeScript typecheck | passou |
| ESLint | passou |
| Build Vite | passou; chunk principal 505,92 kB |
| Ruff nos arquivos Python alterados/novos | passou |
| MyPy direcionado ao harness, alvo Mongo e fixture | 3 arquivos, sem problemas |
| `compileall` Python | passou |
| `git diff --check` | passou |
| Inspeção final de recursos da execução | nenhum contêiner, rede ou imagem Beta 6.1 restante |

O venv temporário foi criado fora do repositório e recebeu as dependências oficiais de `backend/requirements-dev.txt`; Python global e arquivos de dependências não foram alterados.

## Não executados

* A suíte inteira `backend/unit_tests`: **NOT RUN** nesta fase. A inspeção encontrou `test_g2_docker_api_contract.py`, que cria contêineres e duas redes Docker sem o gate de ownership exclusivo Beta 6.1. Não foi executada para evitar efeitos de infraestrutura fora da prova isolada. A Beta 6 reportou historicamente 334 passed, 43 skipped e 26 subtests, mas isso não é uma nova execução da Beta 6.1.
* Regressões persistentes históricas Beta 2–6 fora do teste HTTP nomeado: NOT RUN; fixtures e efeitos variam e não foram autorizados pelo gate desta execução.
* Mypy global do backend: NOT RUN; executado somente nos três módulos experimentais relacionados.
* E2E mobile e navegador além de Chromium desktop: NOT RUN.

## Falhas corrigidas durante a validação

* A fila HTTP do avaliador exigia `Origin` de escrita em um GET; corrigido com dependência de leitura que mantém permissão e escopo.
* O probe de prontidão foi corrigido para ser sintaxe Python válida.
* A origem frontend/API foi alinhada para manter cookies e sessão no browser.
* O spec foi ajustado para aguardar claim e usar as APIs Playwright corretamente, além de confirmar feedback da resposta e persistência.
* Ruff detectou imports novos não ordenados/unused; corrigidos sem alterar contratos.

As falhas iniciais foram reproduzidas e corrigidas; a execução final HTTP e browser passou.
